# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the manifest field tests (task T052):
# a generated entry carries every field rules-data-manifest.md v1.1.1 §2 requires, fileUrl
# resolves to the JSON bundle, sizeBytes and sha256 match the artifact, manifestVersion is 1.
"""Tests for manifest generation (FR-042, R10, `rules-data-manifest.md` v1.1.1 §2).

The manifest is the only network resource the app requires, and every field in it is load
bearing: `sizeBytes` and `sha256` gate ingestion, `publishedAt` orders "newer available",
`schemaContractVersion` decides whether the app may read the snapshot at all, and
`rulesVersionId` is what an imported army fetches by months later (§3.1).

Two structural rules are asserted alongside the fields. Generation is **ordering-stable**, so an
unchanged manifest produces an empty diff and a real change is visible in review; and a
withdrawn entry stays listed, because deleting it would leave an importing player with an
unexplained failure instead of a reason.
"""

from __future__ import annotations

import json

import pytest

from pipeline.build.checksum import checksum
from pipeline.build.manifest import (
    MANIFEST_VERSION,
    ManifestError,
    manifest_entry,
    regenerate_manifest,
    render_manifest,
)
from pipeline.config import Channel
from tests import factories

REQUIRED_FIELDS = {
    "rulesVersionId",
    "displayName",
    "publishedAt",
    "editionCodes",
    "schemaContractVersion",
    "restrictionVocabularyVersion",
    "fileUrl",
    "sizeBytes",
    "sha256",
    "withdrawn",
}

PAYLOAD = b'{"bundleFormatVersion":1}\n'
BASE_URL = "https://the-badgerworks.github.io/wargame-rules-data"


def _entry(**overrides):  # type: ignore[no-untyped-def]
    kwargs = {
        "meta": factories.meta(),
        "display_name": "Invented Fixture 2026.06",
        "edition_codes": ["wh40k-11e"],
        "file_url": f"{BASE_URL}/releases/rules-mfm-2026-06.json",
        "checksum": checksum(PAYLOAD),
    }
    kwargs.update(overrides)
    return manifest_entry(**kwargs)  # type: ignore[arg-type]


def test_an_entry_carries_every_required_field() -> None:
    assert REQUIRED_FIELDS <= set(_entry())


def test_the_entry_carries_nothing_the_contract_does_not_define() -> None:
    assert set(_entry()) <= REQUIRED_FIELDS | {"withdrawnReason"}


def test_size_and_checksum_match_the_artifact() -> None:
    entry = _entry()
    assert entry["sizeBytes"] == len(PAYLOAD)
    assert entry["sha256"] == checksum(PAYLOAD).sha256


def test_file_url_resolves_to_the_json_bundle_not_a_sqlite_file() -> None:
    """v1.1.1 corrected this explicitly: the wire format is JSON (`reference-db-schema.md`)."""
    entry = _entry()
    assert entry["fileUrl"].startswith("https://")
    assert entry["fileUrl"].endswith(".json")
    assert entry["rulesVersionId"] in entry["fileUrl"]


def test_a_non_https_file_url_is_refused() -> None:
    with pytest.raises(ManifestError):
        _entry(file_url="http://example.invalid/rules-mfm-2026-06.json")


def test_a_new_entry_is_not_withdrawn_and_states_no_reason() -> None:
    entry = _entry()
    assert entry["withdrawn"] is False
    assert "withdrawnReason" not in entry


def test_the_document_declares_manifest_version_one() -> None:
    document = render_manifest([_entry()], generated_at="2026-06-13T12:02:41Z")
    assert document["manifestVersion"] == MANIFEST_VERSION == 1
    assert document["generatedAt"] == "2026-06-13T12:02:41Z"
    assert len(document["versions"]) == 1


def test_generation_is_ordering_stable() -> None:
    a, b = _entry(), _entry(meta=factories.meta("mfm-2026-05"))
    forwards = render_manifest([a, b], generated_at="2026-06-13T12:02:41Z")
    backwards = render_manifest([b, a], generated_at="2026-06-13T12:02:41Z")
    assert forwards == backwards


def test_regeneration_appends_without_disturbing_existing_entries(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {"manifestVersion": 1, "generatedAt": "2026-05-01T00:00:00Z", "versions": [_entry(meta=factories.meta("mfm-2026-05"))]}
        ),
        encoding="utf-8",
    )

    regenerate_manifest(path, _entry(), generated_at="2026-06-13T12:02:41Z")
    document = json.loads(path.read_text(encoding="utf-8"))

    assert [v["rulesVersionId"] for v in document["versions"]] == ["mfm-2026-05", "mfm-2026-06"]


def test_republishing_an_existing_id_is_refused(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Immutability is guarantee 1: a correction ships as a new id, never as an edit."""
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps({"manifestVersion": 1, "generatedAt": "2026-05-01T00:00:00Z", "versions": [_entry()]}),
        encoding="utf-8",
    )
    with pytest.raises(ManifestError, match="mfm-2026-06"):
        regenerate_manifest(path, _entry(), generated_at="2026-06-13T12:02:41Z")


def test_a_withdrawn_entry_stays_listed_when_the_manifest_is_regenerated(tmp_path) -> None:  # type: ignore[no-untyped-def]
    withdrawn = dict(_entry(meta=factories.meta("mfm-2026-05")))
    withdrawn["withdrawn"] = True
    withdrawn["withdrawnReason"] = "Superseded by a corrected build."
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps({"manifestVersion": 1, "generatedAt": "2026-05-01T00:00:00Z", "versions": [withdrawn]}),
        encoding="utf-8",
    )

    regenerate_manifest(path, _entry(), generated_at="2026-06-13T12:02:41Z")
    document = json.loads(path.read_text(encoding="utf-8"))
    kept = next(v for v in document["versions"] if v["rulesVersionId"] == "mfm-2026-05")

    assert kept["withdrawn"] is True
    assert kept["withdrawnReason"] == "Superseded by a corrected build."


def test_the_channel_selects_the_path_and_nothing_else() -> None:
    from pipeline.build.manifest import manifest_relative_path

    assert manifest_relative_path(Channel.PUBLISHED) == "manifest.json"
    assert manifest_relative_path(Channel.PRERELEASE) == "prerelease/manifest.json"


def test_the_manifest_file_is_written_with_the_canonical_serialiser(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps({"manifestVersion": 1, "generatedAt": "2026-05-01T00:00:00Z", "versions": []}),
        encoding="utf-8",
    )
    regenerate_manifest(path, _entry(), generated_at="2026-06-13T12:02:41Z")
    raw = path.read_bytes()
    assert raw.endswith(b"\n")
    assert b"\r\n" not in raw
