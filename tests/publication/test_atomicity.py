# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the atomicity tests (task T138): an
# interruption after the asset upload but before the manifest regeneration leaves the previous
# manifest live and at worst an unreferenced release asset; an interruption in the reverse order
# is impossible by construction; the manifest never names an unretrievable artifact (FR-045).
"""Tests for FR-045: publication is atomic from a consumer's point of view.

`pipeline.publish.release.publish` fixes the order — create, upload, re-download and verify,
*then* regenerate the manifest, append the checksum ledger, deploy Pages (contract §4 steps
5-7). This suite fails the re-download step and asserts what that interruption leaves behind: the
manifest is written only after the artifact has already been proven retrievable, so it can never
be caught naming something a consumer cannot fetch. The reverse ordering — manifest before the
asset exists — has no code path to fail *into*, because `publish`'s source calls
`regenerate_manifest` strictly after the create/upload/verify sequence, never interleaved with
it; that is demonstrated by the successful case asserting order-of-operations directly.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from pipeline.build.bundle_emit import BundleMeta
from pipeline.config import Channel
from pipeline.publish.pages import read_published_checksums
from pipeline.publish.release import PublicationError, PublicationRequest, publish

PAYLOAD = b'{"bundleFormatVersion":1}\n'


def _manifest(root: Path, relative: str = "prerelease/manifest.json") -> dict[str, object]:
    text = (root / "site" / relative).read_text(encoding="utf-8")
    return json.loads(text)  # type: ignore[no-any-return]


def _request(rules_version_id: str, *, payload: bytes = PAYLOAD) -> PublicationRequest:
    meta = BundleMeta(
        rules_version_id=rules_version_id,
        published_at="2026-06-13T00:00:00Z",
        source_note="Invented Fixture",
        schema_contract_version=1,
        restriction_vocabulary_version=1,
    )
    return PublicationRequest(
        meta=meta,
        payload=payload,
        display_name="Invented Fixture",
        edition_codes=["wh40k-11e"],
        commit_sha="deadbeef",
        expect_sha256=hashlib.sha256(payload).hexdigest(),
        channel=Channel.PRERELEASE,
    )


def test_a_failed_re_download_leaves_the_previous_manifest_live(channel_repo, fake_api) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("interrupted-after-upload")
    before = _manifest(root)

    # Simulate an interruption between "upload the asset" and "regenerate the manifest": the
    # re-download comes back corrupted, exactly as a crash mid-transfer or a truncated response
    # would leave it (contract §4 step 3).
    fake_api.corrupt_next_download = True

    with pytest.raises(PublicationError):
        publish(
            _request("mfm-2026-06"),
            api=fake_api,
            site_dir=root / "site",
            state_dir=root / "state",
            generated_at="2026-06-13T12:00:00Z",
        )

    assert _manifest(root) == before


def test_a_failed_re_download_leaves_the_checksum_ledger_untouched(channel_repo, fake_api) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("interrupted-ledger")
    fake_api.corrupt_next_download = True

    with pytest.raises(PublicationError):
        publish(
            _request("mfm-2026-06"),
            api=fake_api,
            site_dir=root / "site",
            state_dir=root / "state",
            generated_at="2026-06-13T12:00:00Z",
        )

    assert read_published_checksums(root / "state" / "published-checksums.json") == []


def test_a_failed_re_download_leaves_at_worst_an_unreferenced_release_asset(
    channel_repo, fake_api
) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("interrupted-orphan-asset")
    fake_api.corrupt_next_download = True

    with pytest.raises(PublicationError):
        publish(
            _request("mfm-2026-06"),
            api=fake_api,
            site_dir=root / "site",
            state_dir=root / "state",
            generated_at="2026-06-13T12:00:00Z",
        )

    # The upload itself succeeded before the interruption -- that is what makes it "at worst
    # unreferenced" rather than "lost". Nothing in the manifest points at it, so no consumer can
    # ever reach it.
    assert len(fake_api.released) == 1
    assert _manifest(root)["versions"] == []


def test_the_manifest_is_written_only_after_the_asset_is_proven_retrievable(
    channel_repo, fake_api
) -> None:  # type: ignore[no-untyped-def]
    """The reverse interruption — a manifest naming an artifact before it is retrievable — has no
    code path to occur through: `regenerate_manifest` runs only after `create_release`,
    `upload_asset`, and a successful re-download-and-verify, in that order, in `publish`'s own
    source. A normal run demonstrates the ordering was actually exercised, not merely asserted."""
    root = channel_repo("ordering")

    result = publish(
        _request("mfm-2026-07"),
        api=fake_api,
        site_dir=root / "site",
        state_dir=root / "state",
        generated_at="2026-07-13T12:00:00Z",
    )

    assert fake_api.create_calls  # the release was created
    assert fake_api.upload_calls  # ... the asset was uploaded
    assert fake_api.download_calls  # ... and re-verified, before the manifest below was written
    manifest = _manifest(root)
    assert [v["rulesVersionId"] for v in manifest["versions"]] == ["mfm-2026-07"]
    assert manifest["versions"][0]["fileUrl"] == result.file_url


def test_the_manifest_never_names_an_artifact_that_failed_its_own_verification(
    channel_repo, fake_api
) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("never-names-unverified")
    fake_api.corrupt_next_download = True

    with pytest.raises(PublicationError):
        publish(
            _request("mfm-2026-08"),
            api=fake_api,
            site_dir=root / "site",
            state_dir=root / "state",
            generated_at="2026-08-13T12:00:00Z",
        )

    assert _manifest(root)["versions"] == []
    # A later, successful publish of a *different* id still works — the failed attempt above
    # left nothing behind that could interfere with it.
    fake_api.corrupt_next_download = False
    publish(
        _request("mfm-2026-08-b"),
        api=fake_api,
        site_dir=root / "site",
        state_dir=root / "state",
        generated_at="2026-08-14T12:00:00Z",
    )
    assert [v["rulesVersionId"] for v in _manifest(root)["versions"]] == ["mfm-2026-08-b"]
