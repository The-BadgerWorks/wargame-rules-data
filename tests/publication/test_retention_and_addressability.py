# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the retention and addressability
# tests (task T135): with three published versions, each rulesVersionId resolves to its own
# artifact and no other; publishing a fourth leaves every earlier entry listed, unchanged, and
# retrievable; and no code path deletes a manifest entry (FR-041, FR-043, SC-007).
"""Tests for FR-041, FR-043, SC-007: every published version stays listed and addressable.

Three versions are published into one repository root, then a fourth. The property under test is
retention, not the pipeline's other behaviour, so publication itself uses `publish_version` — the
same call path `publish.yml` uses (`pipeline.cli.run_publish_command` -> `pipeline.publish.gate.
run_publish` -> `pipeline.publish.release.publish`) — leaving each earlier entry exactly as
`regenerate_manifest` (T070/T139) already promises to.
"""

from __future__ import annotations

import json
from pathlib import Path

IDS = ("mfm-2026-01", "mfm-2026-02", "mfm-2026-03")


def _manifest(root: Path) -> dict[str, object]:
    text = (root / "site" / "prerelease" / "manifest.json").read_text(encoding="utf-8")
    return json.loads(text)  # type: ignore[no-any-return]


def test_each_version_resolves_to_its_own_artifact_and_no_other(
    channel_repo, publish_version, fake_api
) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("three-versions")
    payloads: dict[str, bytes] = {}
    for index, rules_version_id in enumerate(IDS, start=1):
        result, _outcome = publish_version(root, rules_version_id, f"2026-0{index}-01T00:00:00Z")
        payloads[rules_version_id] = result.payload

    entries = {e["rulesVersionId"]: e for e in _manifest(root)["versions"]}
    assert set(entries) == set(IDS)

    # Every version has its own, distinct retrieval location -- "addressable by id" (contract
    # §3.1), not merely "the newest one is downloadable".
    urls = {entry["fileUrl"] for entry in entries.values()}
    assert len(urls) == len(IDS)

    for rules_version_id in IDS:
        entry = entries[rules_version_id]
        fetched = fake_api.download_asset(url=entry["fileUrl"])
        assert fetched == payloads[rules_version_id]


def test_the_checksum_recorded_for_each_id_matches_only_that_ids_artifact(
    channel_repo, publish_version, fake_api
) -> None:  # type: ignore[no-untyped-def]
    from pipeline.build.checksum import checksum

    root = channel_repo("checksum-per-id")
    for index, rules_version_id in enumerate(IDS, start=1):
        publish_version(root, rules_version_id, f"2026-0{index}-01T00:00:00Z")

    entries = {e["rulesVersionId"]: e for e in _manifest(root)["versions"]}
    for entry in entries.values():
        fetched = fake_api.download_asset(url=entry["fileUrl"])
        assert checksum(fetched).sha256 == entry["sha256"]


def test_publishing_a_fourth_version_leaves_every_earlier_entry_unchanged(
    channel_repo, publish_version
) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("fourth-version")
    for index, rules_version_id in enumerate(IDS, start=1):
        publish_version(root, rules_version_id, f"2026-0{index}-01T00:00:00Z")

    before = {e["rulesVersionId"]: e for e in _manifest(root)["versions"]}

    publish_version(root, "mfm-2026-04", "2026-04-01T00:00:00Z")

    after = {e["rulesVersionId"]: e for e in _manifest(root)["versions"]}
    assert set(after) == {*IDS, "mfm-2026-04"}
    for rules_version_id in IDS:
        assert after[rules_version_id] == before[rules_version_id]


def test_no_code_path_shrinks_the_manifest(channel_repo, publish_version) -> None:  # type: ignore[no-untyped-def]
    """Every publication only ever adds an entry (T139); the version count is monotonic."""
    root = channel_repo("monotonic")
    counts = []
    for index, rules_version_id in enumerate(IDS, start=1):
        publish_version(root, rules_version_id, f"2026-0{index}-01T00:00:00Z")
        counts.append(len(_manifest(root)["versions"]))
    assert counts == [1, 2, 3]
