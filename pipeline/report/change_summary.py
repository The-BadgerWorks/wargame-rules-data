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

#: ``(datasheet_id, copy_index_min, model_count, pricing_context, was, now)``. The context is
#: `""` for the ordinary price and is part of the identity of the row that changed: two prices
#: of one unit at one size, under different stated conditions, move independently.
DatasheetCostChange = tuple[str, int, int, str, int, int]

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


def _datasheet_costs(
    snapshot: CuratedSnapshot,
) -> Mapping[str, Mapping[tuple[int, int, str], int]]:
    return {
        datasheet.datasheet_id: {
            (cost.copy_index_min, cost.model_count, cost.pricing_context or ""): cost.points
            for cost in datasheet.costs
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
                        key[2],
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
    accounted_datasheet = {
        (row[0], row[1], row[2], row[3]) for row in summary.datasheet_cost_changes
    }
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
                    key[2],
                )
                not in accounted_datasheet
            ):
                missing.append(
                    f"{datasheet_id}: cost at copy_index_min={key[0]} model_count={key[1]} "
                    f"pricing_context={key[2] or '(absent)'} changed but is not listed"
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


#: ``(datasheet_id, line, was, now)`` where each side is ``"<model name> <min>-<max>"`` or
#: ``"absent"``. Rendered as a string pair rather than as counts because a composition change is
#: read by a human deciding whether the squad they can build has changed.
CompositionChange = tuple[str, int, str, str]

#: ``(datasheet_id, group_id, "added" | "removed")``.
OptionGroupChange = tuple[str, str, str]

#: ``(datasheet_id, choice_id, "added" | "removed" | "repriced", was, now)`` — the price sides are
#: ``"unpriced"`` where no ``points_delta`` was published, never ``0`` (FR-013).
OptionChoiceChange = tuple[str, str, str, str, str]

#: ``(keyword, was, now)`` where each side is a class name or ``"unclassified"``.
KeywordClassChange = tuple[str, str, str]

#: ``(summary class, summary_key, "added" | "changed" | "flagged")``.
SummaryChange = tuple[str, str, str]

#: The five categories `004-rules-data-enrichment` adds to the accounting. Named as data because
#: :func:`unaccounted_enrichment_differences` iterates them, so a sixth category cannot be added
#: to :class:`EnrichmentChanges` without the omission check learning about it.
ENRICHMENT_CATEGORIES: Sequence[str] = (
    "composition_changes",
    "option_group_changes",
    "option_choice_changes",
    "keyword_class_changes",
    "summary_changes",
)


@dataclass(frozen=True, slots=True)
class EnrichmentChanges:
    """What moved in the five things `004-rules-data-enrichment` added (FR-037).

    Separate from :class:`ChangeSummary` rather than folded into it, because the two answer to
    different sources: that one is derived from :class:`PriorSnapshot`, the narrow projection
    used for cost comparison, while these need the previous **curated tree** — composition
    entries, option groups and their prices, and per-binding keyword classes are all things the
    cost projection deliberately does not carry.
    """

    composition_changes: tuple[CompositionChange, ...] = ()
    option_group_changes: tuple[OptionGroupChange, ...] = ()
    option_choice_changes: tuple[OptionChoiceChange, ...] = ()
    keyword_class_changes: tuple[KeywordClassChange, ...] = ()
    summary_changes: tuple[SummaryChange, ...] = ()

    def entries(self, category: str) -> tuple[tuple[object, ...], ...]:
        """One category's rows, by name — what the omission check iterates."""
        return getattr(self, category)  # type: ignore[no-any-return]


def _composition(snapshot: CuratedSnapshot) -> dict[tuple[str, int], str]:
    return {
        (datasheet.datasheet_id, entry.line): (
            f"{entry.model_name} {entry.min_count}-{entry.max_count}"
        )
        for datasheet in snapshot.datasheets
        for entry in datasheet.composition
    }


def _option_groups(snapshot: CuratedSnapshot) -> dict[tuple[str, str], str]:
    return {
        (datasheet.datasheet_id, group.id): group.scope.value
        for datasheet in snapshot.datasheets
        for group in datasheet.option_groups
    }


def _option_choices(snapshot: CuratedSnapshot) -> dict[tuple[str, str], str]:
    """``(datasheet_id, choice_id) -> price``, where an unpriced choice reads ``"unpriced"``.

    Never ``0``: a choice the points source does not price and a choice priced at zero are
    different facts, and collapsing them here would report a repricing that never happened
    (FR-013, guarantee 10).
    """
    return {
        (datasheet.datasheet_id, choice.id): (
            "unpriced" if choice.points_delta is None else str(choice.points_delta)
        )
        for datasheet in snapshot.datasheets
        for choice in datasheet.option_choices
    }


def _keyword_classes(snapshot: CuratedSnapshot) -> dict[str, str]:
    """``keyword -> class``, over the whole snapshot rather than per datasheet.

    A keyword's class is a property of the keyword, not of the binding — FR-019 guarantees one
    parent per chapter keyword — so reporting it per datasheet would print the same
    classification decision once per unit that carries it.
    """
    classes: dict[str, str] = {}
    for datasheet in snapshot.datasheets:
        for keyword in datasheet.keywords:
            if keyword.keyword_class is not None:
                classes.setdefault(keyword.keyword, keyword.keyword_class.value)
    return classes


def _authored_summaries(snapshot: CuratedSnapshot) -> dict[tuple[str, str], tuple[str, str]]:
    """``(class, summary_key) -> (digest, review_state)`` across all four summary classes."""
    collected: dict[tuple[str, str], tuple[str, str]] = {}
    for key, ability in snapshot.ability_summaries.items():
        collected[("abilities", key)] = (ability.mechanic_digest, ability.review_state.value)
    for file in snapshot.faction_rules.values():
        for rule in file.rules:
            collected[("faction_rules", rule.summary_key)] = (
                rule.mechanic_digest,
                rule.review_state.value,
            )
    for key, detachment_rule in snapshot.detachment_rules.items():
        collected[("detachment_rules", key)] = (
            detachment_rule.mechanic_digest,
            detachment_rule.review_state.value,
        )
    for entry in snapshot.keyword_glossary.values():
        collected[("glossary", entry.summary_key)] = (
            entry.mechanic_digest,
            entry.review_state.value,
        )
    return collected


def compute_enrichment_changes(
    previous: CuratedSnapshot | None, snapshot: CuratedSnapshot
) -> EnrichmentChanges:
    """Diff the five enrichment categories between two curated versions (FR-037).

    Args:
        previous: the previously published **curated tree**, as
            :func:`pipeline.curate.prior.read_curated_tree` reconstructs it. ``None`` — a first
            release — yields no rows at all rather than reporting the whole snapshot as added,
            because "everything is new" is not a change summary anyone reads.

    **One honest degradation, stated rather than hidden.** Authored summaries live in
    ``curation/`` and are *never* written to ``data/`` (FR-017), so a previous snapshot
    reconstructed from the tree carries none of them. When that is so — every real run today —
    the summary category reports **nothing** instead of reporting every summary in the data set
    as newly added. A summary's own history is in the ``curation/`` diff, which is the review
    surface it belongs on; inventing a bulk "added" list here would bury the four categories
    that *are* derivable from the tree under thousands of lines that say nothing.
    """
    if previous is None:
        return EnrichmentChanges()

    composition_before, composition_after = _composition(previous), _composition(snapshot)
    composition = tuple(
        (
            datasheet_id,
            line,
            composition_before.get(key, "absent"),
            composition_after.get(key, "absent"),
        )
        for key in sorted(set(composition_before) | set(composition_after))
        for datasheet_id, line in (key,)
        if composition_before.get(key) != composition_after.get(key)
    )

    groups_before, groups_after = _option_groups(previous), _option_groups(snapshot)
    group_changes = tuple(
        (datasheet_id, group_id, "added" if key in groups_after else "removed")
        for key in sorted(set(groups_before) ^ set(groups_after))
        for datasheet_id, group_id in (key,)
    )

    choices_before, choices_after = _option_choices(previous), _option_choices(snapshot)
    choice_changes: list[OptionChoiceChange] = []
    for key in sorted(set(choices_before) | set(choices_after)):
        datasheet_id, choice_id = key
        was, now = choices_before.get(key), choices_after.get(key)
        if was == now:
            continue
        if was is None:
            choice_changes.append((datasheet_id, choice_id, "added", "absent", now or "absent"))
        elif now is None:
            choice_changes.append((datasheet_id, choice_id, "removed", was, "absent"))
        else:
            choice_changes.append((datasheet_id, choice_id, "repriced", was, now))

    classes_before, classes_after = _keyword_classes(previous), _keyword_classes(snapshot)
    class_changes = tuple(
        (
            keyword,
            classes_before.get(keyword, "unclassified"),
            classes_after.get(keyword, "unclassified"),
        )
        for keyword in sorted(set(classes_before) | set(classes_after))
        if classes_before.get(keyword) != classes_after.get(keyword)
    )

    summaries_before = _authored_summaries(previous)
    summaries_after = _authored_summaries(snapshot)
    summary_changes: list[SummaryChange] = []
    if summaries_before:
        for key in sorted(summaries_after):
            summary_class, summary_key = key
            before = summaries_before.get(key)
            after = summaries_after[key]
            if before is None:
                summary_changes.append((summary_class, summary_key, "added"))
            elif before[0] != after[0]:
                summary_changes.append((summary_class, summary_key, "changed"))
            elif after[1] == "needs_rereview" and before[1] != "needs_rereview":
                summary_changes.append((summary_class, summary_key, "flagged"))

    return EnrichmentChanges(
        composition_changes=composition,
        option_group_changes=group_changes,
        option_choice_changes=tuple(choice_changes),
        keyword_class_changes=class_changes,
        summary_changes=tuple(summary_changes),
    )


def unaccounted_enrichment_differences(
    changes: EnrichmentChanges, previous: CuratedSnapshot | None, snapshot: CuratedSnapshot
) -> list[str]:
    """Re-derive all five categories independently and report whatever ``changes`` omitted.

    The same discipline :func:`unaccounted_differences` applies to costs, and for the same
    reason: an accounting check that shares its arithmetic with the thing it checks proves
    nothing. This one re-computes the difference sets from the two snapshots and asks, of each
    difference, whether ``changes`` mentions its **key** — never its rendered value, so a
    formatting change here cannot make the check pass or fail on its own.
    """
    if previous is None:
        return []

    accounted: dict[str, set[object]] = {
        "composition_changes": {(row[0], row[1]) for row in changes.composition_changes},
        "option_group_changes": {(row[0], row[1]) for row in changes.option_group_changes},
        "option_choice_changes": {(row[0], row[1]) for row in changes.option_choice_changes},
        "keyword_class_changes": {row[0] for row in changes.keyword_class_changes},
        "summary_changes": {(row[0], row[1]) for row in changes.summary_changes},
    }

    missing: list[str] = []

    def _sweep[K](category: str, before: Mapping[K, str], after: Mapping[K, str]) -> None:
        for key in sorted(set(before) | set(after), key=str):
            if before.get(key) != after.get(key) and key not in accounted[category]:
                missing.append(f"{category}: {key} changed but is not listed")

    _sweep("composition_changes", _composition(previous), _composition(snapshot))
    _sweep("option_group_changes", _option_groups(previous), _option_groups(snapshot))
    _sweep("option_choice_changes", _option_choices(previous), _option_choices(snapshot))
    _sweep("keyword_class_changes", _keyword_classes(previous), _keyword_classes(snapshot))

    summaries_before = _authored_summaries(previous)
    if summaries_before:
        summaries_after = _authored_summaries(snapshot)
        for key in sorted(summaries_after):
            before_summary = summaries_before.get(key)
            after_summary = summaries_after[key]
            moved = (
                before_summary is None
                or before_summary[0] != after_summary[0]
                or (after_summary[1] == "needs_rereview" and before_summary[1] != "needs_rereview")
            )
            if moved and key not in accounted["summary_changes"]:
                missing.append(f"summary_changes: {key} changed but is not listed")

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


def render_change_summary(
    summary: ChangeSummary, enrichment: EnrichmentChanges | None = None
) -> str:
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
            f"`{ds}` copy {copy_index}+, {models} models"
            f"{f' ({context})' if context else ''}: "
            f"{'absent' if was < 0 else was} → {'absent' if now < 0 else now}"
            for ds, copy_index, models, context, was, now in summary.datasheet_cost_changes
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

    changes = enrichment or EnrichmentChanges()
    out += _rows(
        "Unit composition",
        [
            f"`{ds}` line {line}: {was} → {now}"
            for ds, line, was, now in changes.composition_changes
        ],
    )
    out += _rows(
        "Wargear option groups",
        [f"`{ds}` `{group}`: {verb}" for ds, group, verb in changes.option_group_changes],
    )
    out += _rows(
        "Wargear option choices",
        [
            f"`{ds}` `{choice}`: {verb} ({was} → {now})"
            for ds, choice, verb, was, now in changes.option_choice_changes
        ],
    )
    out += _rows(
        "Keyword classification",
        [f"`{keyword}`: {was} → {now}" for keyword, was, now in changes.keyword_class_changes],
    )
    out += _rows(
        "Authored summaries",
        [f"`{cls}` `{key}`: {verb}" for cls, key, verb in changes.summary_changes],
    )
    return "\n".join(out).rstrip() + "\n"
