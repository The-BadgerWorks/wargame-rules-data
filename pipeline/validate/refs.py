# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented V4 intra-snapshot referential
# integrity and V9 authored-reference integrity (task T068), so a copy limit or restriction
# pointing at a retired datasheet is the blocking AUT-DANGLING-REF (FR-018).
# AI-Assisted: Claude Code (model: claude-opus-5) - Extended V9 to 004's two override files (004
# task T026, 004 data-model.md §4): an override naming a line, model row, or weapon row that no
# longer exists is the same defect, reported the same way rather than by a check of its own.
"""V4 and V9 — every reference resolves, in both directions.

**V4** is the consumer contract's guarantee 4, checked here rather than discovered at ingestion:
the app builds a SQLite file with real foreign keys, so a dangling reference in the bundle is an
ingestion failure on a player's phone. Checking it in the producer turns that into a blocked
candidate.

**V9** is the direction people forget. Authored records outlive the data they point at: a copy
limit written for a datasheet the publisher later retires stays in `curation/copy-limits.json`
forever, silently doing nothing, and nobody notices until someone wonders why the limit is not
being enforced. Making it blocking (FR-018) means the retirement and the authored record are
reconciled in the same release rather than never.
"""

from __future__ import annotations

from pipeline.curate.authored import AuthoredContent, authored_entity_refs
from pipeline.models.curated import CuratedSnapshot
from pipeline.models.findings import Finding
from pipeline.report.catalogue import build_finding


def _known_ids(snapshot: CuratedSnapshot) -> dict[str, set[str]]:
    return {
        "faction_id": {faction.faction_id for faction in snapshot.factions},
        "parent_faction_id": {faction.faction_id for faction in snapshot.factions},
        "detachment_id": {d.detachment_id for d in snapshot.detachments},
        "datasheet_id": {d.datasheet_id for d in snapshot.datasheets},
        "enhancement_id": {e.enhancement_id for e in snapshot.enhancements},
    }


def check_intra_snapshot_references(snapshot: CuratedSnapshot) -> list[Finding]:
    """V4 — every reference inside the snapshot resolves inside the snapshot."""
    known = _known_ids(snapshot)
    findings: list[Finding] = []

    def _require(holder: str, field: str, value: str | None, pool: str) -> None:
        if value is None or value in known[pool]:
            return
        findings.append(
            build_finding(
                "CON-DANGLING-REF",
                entity_refs=[holder],
                detail={"holder": holder, "field": field, "missing_id": value},
            )
        )

    for faction in snapshot.factions:
        _require(faction.faction_id, "parent_faction_id", faction.parent_faction_id, "faction_id")

    for detachment in snapshot.detachments:
        _require(detachment.detachment_id, "faction_id", detachment.faction_id, "faction_id")
        for restriction in detachment.restrictions:
            for key, value in restriction.params.items():
                if key == "datasheet_id" and isinstance(value, str):
                    _require(restriction.id, "params.datasheet_id", value, "datasheet_id")

    for restriction in snapshot.restrictions:
        _require(restriction.id, "detachment_id", restriction.detachment_id, "detachment_id")
        for key, value in restriction.params.items():
            if key == "datasheet_id" and isinstance(value, str):
                _require(restriction.id, "params.datasheet_id", value, "datasheet_id")

    # An enhancement whose detachment does not resolve is deliberately **not** checked here.
    # It has its own catalogued code, `CON-ORPHAN-ENHANCEMENT`, and raising both for one defect
    # would double-count it in the report's scale figures — which the approver reads as "how
    # much of this release is broken".

    for datasheet in snapshot.datasheets:
        _require(datasheet.datasheet_id, "faction_id", datasheet.faction_id, "faction_id")
        for bodyguard in datasheet.leader_pairs:
            _require(datasheet.datasheet_id, "leader_pairs", bodyguard, "datasheet_id")

    return findings


def check_authored_references(
    snapshot: CuratedSnapshot, authored: AuthoredContent
) -> list[Finding]:
    """V9 — no authored record references an entity the snapshot does not contain."""
    known = _known_ids(snapshot)
    findings: list[Finding] = []

    for file_name, field, value in authored_entity_refs(authored):
        pool = known.get(field)
        if pool is None or value in pool:
            continue
        findings.append(
            build_finding(
                "AUT-DANGLING-REF",
                entity_refs=[f"{file_name}:{value}"],
                detail={"file_name": file_name, "field": field, "missing_id": value},
            )
        )

    findings.extend(check_override_references(snapshot, authored))
    return findings


def check_override_references(
    snapshot: CuratedSnapshot, authored: AuthoredContent
) -> list[Finding]:
    """V9 for `004`'s two override files, whose references are *rows*, not ids.

    ``authored_entity_refs`` already catches an override naming a datasheet that no longer
    exists. These are the two references it cannot express: the **line** the override resolves,
    and the **model or weapon row** it points the resolution at. Both go stale the same way and
    for the same reason — the publisher restructures a datasheet, the override keeps silently
    doing nothing, and nobody notices until someone wonders why the composition is still missing.

    **One deliberate carve-out.** A composition override's line is not checked when the
    datasheet publishes no composition at all, because FR-008 suppresses the *whole* datasheet's
    composition as soon as any one of its lines is unresolved — so a still-valid override on a
    datasheet with a second unresolved line would otherwise be reported as dangling, and the
    curator would be sent to fix the record that is already correct.
    """
    findings: list[Finding] = []
    datasheets = {datasheet.datasheet_id: datasheet for datasheet in snapshot.datasheets}

    def _dangle(file_name: str, field: str, ref: str, missing: str | int) -> None:
        findings.append(
            build_finding(
                "AUT-DANGLING-REF",
                entity_refs=[f"{file_name}:{ref}"],
                detail={"file_name": file_name, "field": field, "missing_id": str(missing)},
            )
        )

    for override in authored.composition_overrides:
        datasheet = datasheets.get(override.datasheet_id)
        if datasheet is None:
            continue  # already reported by `authored_entity_refs`
        reference = f"{override.datasheet_id}:{override.line}"
        if datasheet.composition and override.line not in {
            entry.line for entry in datasheet.composition
        }:
            _dangle("composition-overrides.json", "line", reference, override.line)
        if override.model_line is not None and override.model_line not in {
            model.line for model in datasheet.models
        }:
            _dangle("composition-overrides.json", "model_line", reference, override.model_line)

    for option_override in authored.option_overrides:
        datasheet = datasheets.get(option_override.datasheet_id)
        if datasheet is None:
            continue
        reference = f"{option_override.datasheet_id}:{option_override.line}"
        if option_override.line not in {group.line for group in datasheet.option_groups}:
            _dangle("option-overrides.json", "line", reference, option_override.line)
        weapon_lines = {weapon.line for weapon in datasheet.weapons}
        for choice in option_override.choices:
            for field, line in (
                ("grants_weapon_line", choice.grants_weapon_line),
                ("replaces_weapon_line", choice.replaces_weapon_line),
            ):
                if line is not None and line not in weapon_lines:
                    _dangle("option-overrides.json", field, reference, line)

    return findings
