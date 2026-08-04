# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented deterministic, ordering-stable
# manifest generation (task T070) into site/manifest.json or site/prerelease/manifest.json per
# WGC_DATA_CHANNEL, with every rules-data-manifest.md v1.1.1 field populated (FR-042, FR-045,
# FR-047).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added `withdraw_entry` (task T139): the
# only other way a manifest may ever be rewritten -- flipping `withdrawn`/`withdrawnReason` on
# exactly one existing entry, never adding, removing, or otherwise editing one (FR-042, FR-043,
# FR-044, data-model.md §7.4).
"""Generate the manifest — the only network resource the consuming app requires.

Every field in it is load bearing. `sizeBytes` and `sha256` gate ingestion; `publishedAt` orders
"newer available"; `schemaContractVersion` decides whether the app may read the snapshot at all;
and `rulesVersionId` is what an imported army fetches by months after the fact (§3.1). So the
entry is built from the artifact rather than described alongside it: the checksum and the size
come from the bytes that were actually produced.

**Generation is ordering-stable.** Entries are sorted by `rulesVersionId`, so an unchanged
manifest produces an empty diff and a real change is visible in review rather than buried in a
reshuffle.

**Existing entries are never rewritten.** A published version is immutable (guarantee 1): a
correction ships as a new id, and a withdrawn entry stays listed with its withdrawal fields
intact — deleting it would leave an importing player with an unexplained failure instead of a
reason (§3.1).

**The channel selects a path and nothing else** (FR-047). There is no behavioural branch on
channel anywhere below the CLI entry point; pre-release and published differ in where the file
lands and in who may approve the job that writes it.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Final

from pipeline.build.bundle_emit import BundleMeta
from pipeline.build.canonical_json import JsonValue, omit_absent, write_bundle
from pipeline.build.checksum import BundleChecksum
from pipeline.config import Channel

#: `rules-data-manifest.md` v1.1.1 §2. The app refuses a higher value.
MANIFEST_VERSION: Final = 1

#: Channel -> the path under `site/` the manifest is written to (contract §5).
MANIFEST_PATHS: Final[Mapping[Channel, str]] = {
    Channel.PUBLISHED: "manifest.json",
    Channel.PRERELEASE: "prerelease/manifest.json",
}


class ManifestError(ValueError):
    """A manifest operation that would break an invariant the consuming app relies on."""


def manifest_relative_path(channel: Channel) -> str:
    """The manifest's path under `site/` for one channel."""
    return MANIFEST_PATHS[channel]


def manifest_entry(
    *,
    meta: BundleMeta,
    display_name: str,
    edition_codes: Sequence[str],
    file_url: str,
    checksum: BundleChecksum,
    withdrawn: bool = False,
    withdrawn_reason: str | None = None,
) -> dict[str, JsonValue]:
    """Build one `versions[]` entry from the artifact that was actually produced."""
    if not file_url.startswith("https://"):
        raise ManifestError(
            f"fileUrl must be HTTPS; got a {len(file_url)}-character value that is not. "
            "The app fetches this without credentials and verifies the checksum after "
            "download, but the transport is still the first control."
        )
    if not file_url.endswith(".json"):
        raise ManifestError(
            "fileUrl must resolve to the JSON snapshot bundle, not a .sqlite file — the wire "
            "format is JSON and the database is built by the app at ingestion time "
            "(rules-data-manifest.md v1.1.1 §2)"
        )
    if not display_name.strip():
        raise ManifestError("displayName is player-visible and may not be empty")

    return omit_absent(
        {
            "rulesVersionId": meta.rules_version_id,
            "displayName": display_name,
            "publishedAt": meta.published_at,
            "editionCodes": list(edition_codes),
            "schemaContractVersion": meta.schema_contract_version,
            "restrictionVocabularyVersion": meta.restriction_vocabulary_version,
            "fileUrl": file_url,
            "sizeBytes": checksum.size_bytes,
            "sha256": checksum.sha256,
            "withdrawn": withdrawn,
            "withdrawnReason": withdrawn_reason,
        }
    )


def render_manifest(
    entries: Sequence[Mapping[str, JsonValue]], *, generated_at: str
) -> dict[str, JsonValue]:
    """Render the whole document, sorted so an unchanged manifest diffs to nothing."""
    ordered: list[dict[str, JsonValue]] = sorted(
        (dict(entry) for entry in entries),
        key=lambda entry: str(entry["rulesVersionId"]),
    )
    return {
        "manifestVersion": MANIFEST_VERSION,
        "generatedAt": generated_at,
        "versions": ordered,
    }


def read_manifest(path: Path) -> dict[str, Any]:
    """Read an existing manifest, or the empty document a fresh channel starts from."""
    if not path.is_file():
        return {"manifestVersion": MANIFEST_VERSION, "generatedAt": "", "versions": []}
    document: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if document.get("manifestVersion") != MANIFEST_VERSION:
        raise ManifestError(
            f"{path}: manifestVersion is {document.get('manifestVersion')}, this producer "
            f"writes {MANIFEST_VERSION}"
        )
    return document


def regenerate_manifest(
    path: Path, entry: Mapping[str, JsonValue], *, generated_at: str
) -> dict[str, JsonValue]:
    """Add one entry to a channel's manifest and rewrite it, or refuse.

    Refuses when the id is already listed. That is guarantee 1 enforced at the last possible
    moment: a published `rulesVersionId` is never re-published with different content, and the
    check being here means the refusal happens before Pages is touched rather than after.
    """
    document = read_manifest(path)
    existing = list(document.get("versions", []))

    new_id = str(entry["rulesVersionId"])
    if any(str(item.get("rulesVersionId")) == new_id for item in existing):
        raise ManifestError(
            f"{new_id} is already listed in {path.name}. A published version is immutable: "
            "ship the correction as a new rulesVersionId (guarantee 1)."
        )

    rendered = render_manifest([*existing, entry], generated_at=generated_at)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_bundle(path, rendered)
    return rendered


def withdraw_entry(
    path: Path, *, rules_version_id: str, reason: str, generated_at: str
) -> dict[str, JsonValue]:
    """Mark one existing entry withdrawn, and touch nothing else in the manifest (FR-044).

    The only two fields that ever change are ``withdrawn`` and ``withdrawnReason``, on exactly
    the one entry named. Every other entry, and every other field of this one, is carried
    forward byte-for-byte through :func:`render_manifest`'s own re-sort — which is a no-op here
    since the id set is unchanged, but keeps this function going through the same ordering-
    stable path every other manifest write does, rather than a bespoke in-place edit that could
    drift from it.

    Refuses when the id is not listed at all: withdrawing a version that was never published is
    not "no-op safe", it is evidence the caller named the wrong id (§3.1 of the manifest
    contract — a withdrawn entry's *presence* is what lets the app explain itself to a player,
    so silently doing nothing here would be the wrong failure mode).
    """
    if not reason.strip():
        raise ManifestError(
            "withdrawnReason must be a short factual reason a player pinned to this version "
            "can be shown, not an empty or whitespace-only string (FR-044)"
        )

    document = read_manifest(path)
    existing = list(document.get("versions", []))
    if not any(str(item.get("rulesVersionId")) == rules_version_id for item in existing):
        raise ManifestError(
            f"{rules_version_id} is not listed in {path.name}; nothing to withdraw. Withdrawal "
            "only ever edits an existing entry, it never creates one."
        )

    updated: list[dict[str, JsonValue]] = []
    for item in existing:
        if str(item.get("rulesVersionId")) != rules_version_id:
            updated.append(dict(item))
            continue
        edited = dict(item)
        edited["withdrawn"] = True
        edited["withdrawnReason"] = reason
        updated.append(edited)

    rendered = render_manifest(updated, generated_at=generated_at)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_bundle(path, rendered)
    return rendered
