# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented conflict resolution and rename
# detection (task T093): the FR-002 authority applied so the points source wins every value a
# player pays, both values recorded and the loser carried nowhere; and a display-name change on a
# stable id emitted as REC-RENAME (FR-015, FR-028).
"""When the two sources disagree, and when a name moves.

**A disagreement is not a negotiation.** FR-002 makes the points source authoritative for every
value a player pays, so a conflict has a decided outcome before it is discovered: the points
value is carried, the detail value is recorded *in the report* so the disagreement is visible to
a human, and the losing value goes nowhere — not into the tree, not into the bundle, not as a
fallback if the winner later looks wrong. A fallback is how the losing value ends up in a
player's list six months later with nobody able to say why.

**A rename is one event, not two.** If a display-name change were reported as a removal plus an
addition, the curated id would move with the name and every saved army naming the old id would
stop resolving — on a phone, months later, with no explanation. Stage 1 of the matching ladder is
what makes the id hold; this module is what makes the change *visible* once it has (FR-015).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pipeline.curate.prior import PriorSnapshot
from pipeline.models.curated import CuratedSnapshot
from pipeline.models.findings import Finding
from pipeline.report.catalogue import build_finding


@dataclass(slots=True)
class ConflictOutcome:
    """The value that is carried, and anything the disagreement caused to be reported."""

    value: int
    findings: list[Finding] = field(default_factory=list)


def resolve_cost_conflict(
    *, datasheet_id: str, model_count: int, points_value: int, detail_value: int | None
) -> ConflictOutcome:
    """Apply the FR-002 authority to one cost both sources publish.

    Returns the points source's value always. ``detail_value`` appears in the finding and
    nowhere else.
    """
    if detail_value is None or detail_value == points_value:
        return ConflictOutcome(value=points_value)

    return ConflictOutcome(
        value=points_value,
        findings=[
            build_finding(
                "REC-VALUE-CONFLICT",
                entity_refs=[datasheet_id],
                detail={
                    "datasheet_id": datasheet_id,
                    "field": "cost.points",
                    "model_count": model_count,
                    "points_source_value": points_value,
                    "detail_source_value": detail_value,
                    "authority": "mfm",
                },
            )
        ],
    )


def detect_renames(prior: PriorSnapshot | None, snapshot: CuratedSnapshot) -> list[Finding]:
    """A display-name change on a curated id that existed last release (FR-015)."""
    if prior is None:
        return []
    return [
        build_finding(
            "REC-RENAME",
            entity_refs=[datasheet.datasheet_id],
            detail={
                "datasheet_id": datasheet.datasheet_id,
                "faction_id": datasheet.faction_id,
                "previous_name": prior.datasheets[datasheet.datasheet_id].name,
                "name": datasheet.name,
            },
        )
        for datasheet in sorted(snapshot.datasheets, key=lambda d: d.datasheet_id)
        if datasheet.datasheet_id in prior.datasheets
        and prior.datasheets[datasheet.datasheet_id].name != datasheet.name
    ]


def detect_faction_changes(prior: PriorSnapshot | None, snapshot: CuratedSnapshot) -> list[Finding]:
    """The publisher's faction list gaining or losing a faction between runs (FR-004)."""
    if prior is None:
        return []

    current = {faction.faction_id for faction in snapshot.factions}
    previous = set(prior.factions)

    findings = [
        build_finding(
            "REC-FACTION-ADDED",
            entity_refs=[faction_id],
            detail={"faction_id": faction_id},
        )
        for faction_id in sorted(current - previous)
    ]
    findings.extend(
        build_finding(
            "REC-FACTION-REMOVED",
            entity_refs=[faction_id],
            detail={"faction_id": faction_id},
        )
        for faction_id in sorted(previous - current)
    )
    return findings
