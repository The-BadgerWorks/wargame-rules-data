# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the immutability tests (task T136):
# two fetches of the same version return identical content and checksum; a version id already
# present in the manifest is refused; and an altered release asset is caught by the checksum
# ledger (FR-041, SC-007, SC-009).
"""Tests for FR-041, SC-007, SC-009: a published version's content never moves.

Duplicate-id refusal (guarantee 1) is already covered at the manifest layer by
`tests/publication/test_manifest_fields.py`; this suite asserts the same guarantee end to end
through the publish gate, plus the two integrity properties `rules-pipeline verify` (T143) exists
to police: a stable double-fetch, and a caught tamper.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline.build.checksum import checksum
from pipeline.cli import run_build, run_publish_command
from pipeline.publish.gate import AlreadyPublishedError
from pipeline.publish.pages import read_published_checksums
from pipeline.publish.verify import verify_all

FIXTURES_ROOT = Path(__file__).resolve().parents[2] / "fixtures"


def _manifest(root: Path) -> dict[str, object]:
    text = (root / "site" / "prerelease" / "manifest.json").read_text(encoding="utf-8")
    return json.loads(text)  # type: ignore[no-any-return]


def test_two_fetches_of_the_same_version_return_identical_content_and_checksum(
    channel_repo, publish_version, fake_api
) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("stable-fetch")
    result, _outcome = publish_version(root, "mfm-2026-06", "2026-06-01T00:00:00Z")

    (entry,) = _manifest(root)["versions"]

    first = fake_api.download_asset(url=entry["fileUrl"])
    second = fake_api.download_asset(url=entry["fileUrl"])

    assert first == second == result.payload
    assert (
        checksum(first).sha256
        == checksum(second).sha256
        == entry["sha256"]
        == result.checksum.sha256
    )


def test_a_rules_version_id_already_in_the_manifest_is_refused(
    channel_repo, publish_version, config, fake_api
) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("duplicate")
    result, _outcome = publish_version(root, "mfm-2026-06", "2026-06-01T00:00:00Z")

    # `publish_version` clears the rebuilt bundle after publishing it (so a second, different id
    # can be published into the same root without `_discover_rebuilt_bundle` finding two
    # candidates) -- so a re-run needs its own rebuild first, exactly as a curator dispatching
    # `publish.yml` a second time against the same commit would produce one. Refused whether or
    # not the content would come out the same -- a re-run and an attempted "fix in place" both
    # hit the same refusal (FR-041).
    run_build(
        config=config,
        rules_version_id="mfm-2026-06",
        fixtures_dir=FIXTURES_ROOT / "minimal",
        output_root=root,
        repository_root=root,
        published_at="2026-06-01T00:00:00Z",
    )
    with pytest.raises(AlreadyPublishedError):
        run_publish_command(
            config=config,
            commit_sha="sha-mfm-2026-06-again",
            expect_sha256=result.checksum.sha256,
            api=fake_api,
            repository_root=root,
            generated_at="2026-06-02T00:00:00Z",
            require_ci_context=False,
        )


def test_an_altered_release_asset_is_caught_by_the_checksum_ledger(
    channel_repo, publish_version, fake_api
) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("tampered")
    publish_version(root, "mfm-2026-06", "2026-06-01T00:00:00Z")

    entries = read_published_checksums(root / "state" / "published-checksums.json")
    (url,) = fake_api.released
    fake_api.released[url] = fake_api.released[url] + b"\x00"  # simulate a replaced asset

    (result,) = verify_all(entries, api=fake_api)
    assert result.matched is False
    assert result.actual_sha256 != result.expected_sha256


def test_an_unreachable_asset_is_reported_distinctly_from_a_tampered_one(
    channel_repo, publish_version, fake_api
) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("unreachable")
    publish_version(root, "mfm-2026-06", "2026-06-01T00:00:00Z")

    entries = read_published_checksums(root / "state" / "published-checksums.json")
    (url,) = fake_api.released
    del fake_api.released[url]  # the asset is simply gone

    (result,) = verify_all(entries, api=fake_api)
    assert result.matched is False
    assert result.actual_sha256 is None
    assert result.error is not None
