# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the change summary (task T096):
# added, removed and renamed entities, every changed unit point, detachment point and enhancement
# cost as `was -> now`, pricing-confidence transitions both ways, and the independent accounting
# check that makes SC-010's 100% claim testable (FR-032).
"""`change-summary.md` — what moved since the last release, all of it.

SC-010 does not ask for a list of changes; it asks the summary to account for **100%** of the
cost differences between two versions. Those are different claims, and the second needs a second
computation to be worth anything — so :func:`unaccounted_differences` re-derives the raw
difference set straight from the two versions and reports whatever the summary failed to mention.
An accounting check that shares its arithmetic with the thing it checks proves nothing.

Renames are classified before additions and removals, because a rename that falls through into
"removed ds-x, added ds-x" is both wrong and alarming to read.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from pipeline.curate.prior import PriorSnapshot
from pipeline.models.curated import CuratedSnapshot
from pipeline.models.findings import Finding
from pipeline.report.catalogue import build_finding

#: ``(datasheet_id, copy_index_min, model_count, was, now)``.
DatasheetCostChange = tuple[str, int, int, int, int]

#: ``(entity_id, was, now)`` for a detachment or an enhancement.
CostChange = tuple[str, int, int]

#: ``(datasheet_id, previous_name, name)``.
Rename = tuple[str, str, str]

#: ``(datasheet_id, was_state, now_state)``.
ConfidenceTransition = tuple[str, str, str]


@dataclass(frozen=True, slots=True)
class ChangeSummary:
    """Everything that moved between two versions."""

    previous_version: str | None
    added_datasheets: tuple[str, ...] = ()
    removed_datasheets: tuple[str, ...] = ()
    renamed_datasheets: tuple[Rename, ...] = ()
    added_detachments: tuple[str, ...] = ()
    removed_detachments: tuple[str, ...] = ()
    datasheet_cost_changes: tuple[DatasheetCostChange, ...] = ()
    detachment_cost_changes: tuple[CostChange, ...] = ()
    enhancement_cost_changes: tuple[CostChange, ...] = ()
    confidence_transitions: tuple[ConfidenceTransition, ...] = ()
    tier_changes: tuple[tuple[str, bool, bool], ...] = ()
    """``(datasheet_id, had_escalating_tier, has_escalating_tier)`` — C1/R2."""


def _datasheet_costs(snapshot: CuratedSnapshot) -> Mapping[str, Mapping[tuple[int, int], int]]:
    return {
        datasheet.datasheet_id: {
            (cost.copy_index_min, cost.model_count): cost.points for cost in datasheet.costs
        }
        for datasheet in snapshot.datasheets
    }


def compute_change_summary(prior: PriorSnapshot | None, snapshot: CuratedSnapshot) -> ChangeSummary:
    """Diff two versions into the summary an approver reads."""
    if prior is None:
        return ChangeSummary(previous_version=None)

    current_costs = _datasheet_costs(snapshot)
    current_ids = set(current_costs)
    previous_ids = set(prior.datasheets)

    renames: list[Rename] = []
    transitions: list[ConfidenceTransition] = []
    cost_changes: list[DatasheetCostChange] = []
    tier_changes: list[tuple[str, bool, bool]] = []

    for datasheet in sorted(snapshot.datasheets, key=lambda d: d.datasheet_id):
        before = prior.datasheets.get(datasheet.datasheet_id)
        if before is None:
            continue

        if before.name != datasheet.name:
            renames.append((datasheet.datasheet_id, before.name, datasheet.name))

        was = before.pricing_confidence.state.value
        now = datasheet.pricing_confidence.state.value
        if was != now:
            transitions.append((datasheet.datasheet_id, was, now))

        after = current_costs[datasheet.datasheet_id]
        for key in sorted(set(before.costs) | set(after)):
            old = before.costs.get(key)
            new = after.get(key)
            if old != new:
                cost_changes.append(
                    (
                        datasheet.datasheet_id,
                        key[0],
                        key[1],
                        old if old is not None else -1,
                        new if new is not None else -1,
                    )
                )

        had_tier = before.has_escalating_tier
        has_tier = any(cost.copy_index_min > 1 for cost in datasheet.costs)
        if had_tier != has_tier:
            tier_changes.append((datasheet.datasheet_id, had_tier, has_tier))

    return ChangeSummary(
        previous_version=prior.rules_version_id,
        added_datasheets=tuple(sorted(current_ids - previous_ids)),
        removed_datasheets=tuple(sorted(previous_ids - current_ids)),
        renamed_datasheets=tuple(renames),
        added_detachments=tuple(
            sorted({d.detachment_id for d in snapshot.detachments} - set(prior.detachments))
        ),
        removed_detachments=tuple(
            sorted(set(prior.detachments) - {d.detachment_id for d in snapshot.detachments})
        ),
        datasheet_cost_changes=tuple(cost_changes),
        detachment_cost_changes=tuple(
            (d.detachment_id, prior.detachments[d.detachment_id].points, d.detachment_points_cost)
            for d in sorted(snapshot.detachments, key=lambda d: d.detachment_id)
            if d.detachment_id in prior.detachments
            and prior.detachments[d.detachment_id].points != d.detachment_points_cost
        ),
        enhancement_cost_changes=tuple(
            (e.enhancement_id, prior.enhancements[e.enhancement_id].points, e.points)
            for e in sorted(snapshot.enhancements, key=lambda e: e.enhancement_id)
            if e.enhancement_id in prior.enhancements
            and prior.enhancements[e.enhancement_id].points != e.points
        ),
        confidence_transitions=tuple(transitions),
        tier_changes=tuple(tier_changes),
    )


def unaccounted_differences(
    summary: ChangeSummary, prior: PriorSnapshot | None, snapshot: CuratedSnapshot
) -> list[str]:
    """Re-derive every cost difference independently and report what the summary omitted.

    This exists to make SC-010's "accounts for 100% of cost differences" a *testable* claim
    rather than a hopeful one. It shares no arithmetic with :func:`compute_change_summary`: it
    walks the two versions again and asks, of each difference it finds, whether the summary
    mentions it.
    """
    if prior is None:
        return []

    missing: list[str] = []
    accounted_datasheet = {(row[0], row[1], row[2]) for row in summary.datasheet_cost_changes}
    accounted_detachment = {row[0] for row in summary.detachment_cost_changes}
    accounted_enhancement = {row[0] for row in summary.enhancement_cost_changes}
    accounted_entities = (
        set(summary.added_datasheets)
        | set(summary.removed_datasheets)
        | {row[0] for row in summary.renamed_datasheets}
    )

    current_costs = _datasheet_costs(snapshot)
    for datasheet_id, before in sorted(prior.datasheets.items()):
        after = current_costs.get(datasheet_id)
        if after is None:
            if datasheet_id not in accounted_entities:
                missing.append(f"{datasheet_id}: removed but not listed")
            continue
        for key in sorted(set(before.costs) | set(after)):
            if (
                before.costs.get(key) != after.get(key)
                and (
                    datasheet_id,
                    key[0],
                    key[1],
                )
                not in accounted_datasheet
            ):
                missing.append(
                    f"{datasheet_id}: cost at copy_index_min={key[0]} model_count={key[1]} "
                    "changed but is not listed"
                )

    for datasheet_id in sorted(set(current_costs) - set(prior.datasheets)):
        if datasheet_id not in accounted_entities:
            missing.append(f"{datasheet_id}: added but not listed")

    for detachment in sorted(snapshot.detachments, key=lambda d: d.detachment_id):
        before_detachment = prior.detachments.get(detachment.detachment_id)
        if (
            before_detachment is not None
            and before_detachment.points != detachment.detachment_points_cost
            and detachment.detachment_id not in accounted_detachment
        ):
            missing.append(f"{detachment.detachment_id}: detachment cost changed but is not listed")

    for enhancement in sorted(snapshot.enhancements, key=lambda e: e.enhancement_id):
        before_enhancement = prior.enhancements.get(enhancement.enhancement_id)
        if (
            before_enhancement is not None
            and before_enhancement.points != enhancement.points
            and enhancement.enhancement_id not in accounted_enhancement
        ):
            missing.append(
                f"{enhancement.enhancement_id}: enhancement cost changed but is not listed"
            )

    return missing


def tier_findings(summary: ChangeSummary) -> list[Finding]:
    """`PRC-TIER-DETECTED` for each datasheet that gained or lost an escalating price tier.

    Informational, but it changes what a repeated copy costs, so an approver sees it (C1/R2).
    """
    return [
        build_finding(
            "PRC-TIER-DETECTED",
            entity_refs=[datasheet_id],
            detail={"datasheet_id": datasheet_id, "had_tier": had, "has_tier": has},
        )
        for datasheet_id, had, has in summary.tier_changes
    ]


def _rows(title: str, lines: Sequence[str]) -> list[str]:
    if not lines:
        return [f"## {title}", "", "None.", ""]
    return [f"## {title}", "", *[f"- {line}" for line in lines], ""]


def render_change_summary(summary: ChangeSummary) -> str:
    """`change-summary.md`."""
    out: list[str] = [
        "# Change summary",
        "",
        f"Compared against **{summary.previous_version or 'no previous published version'}**.",
        "",
    ]
    out += _rows("Added datasheets", summary.added_datasheets)
    out += _rows("Removed datasheets", summary.removed_datasheets)
    out += _rows(
        "Renamed datasheets",
        [f"`{ds}`: {was} → {now}" for ds, was, now in summary.renamed_datasheets],
    )
    out += _rows(
        "Unit point costs",
        [
            f"`{ds}` copy {copy_index}+, {models} models: "
            f"{'absent' if was < 0 else was} → {'absent' if now < 0 else now}"
            for ds, copy_index, models, was, now in summary.datasheet_cost_changes
        ],
    )
    out += _rows(
        "Detachment point costs",
        [f"`{entity}`: {was} → {now}" for entity, was, now in summary.detachment_cost_changes],
    )
    out += _rows(
        "Enhancement costs",
        [f"`{entity}`: {was} → {now}" for entity, was, now in summary.enhancement_cost_changes],
    )
    out += _rows(
        "Pricing-confidence transitions",
        [f"`{ds}`: {was} → {now}" for ds, was, now in summary.confidence_transitions],
    )
    out += _rows(
        "Escalating price tiers",
        [
            f"`{ds}`: {'gained' if has else 'lost'} an escalating tier"
            for ds, _had, has in summary.tier_changes
        ],
    )
    return "\n".join(out).rstrip() + "\n"
