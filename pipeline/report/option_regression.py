# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the FR-009 zero-regression
# harness, layer 2 (006 task T011): the per-choice, per-field comparison between what a version
# actually published and what the extended pipeline rebuilds from the same source, rendered
# through change_summary.py's existing OptionGroupChange/OptionChoiceChange vocabulary into
# Identical / Newly resolved / Corrected (006 research D5 layer 2).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 007 US2 (T026): every choice whose
# `grants_`/`replaces_weapon_line` moved is now also classified into research D3.3's three
# transition classes and raises `OPT-LEGACY-CORRECTED`, so `render()`'s Corrected section groups
# FR-007's ≈2 030-choice correction into three patterns an approver can read, rather than a flat
# per-field table (plan Open Decision O1).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 008 task T061 (FR-014, FR-021): added the
# default-equipment twin of this comparison. A new equipment group or item is bucketed by what the
# DATASHEET's own prior `default_equipment_state` was -- `none`/omitted is a previously ABSENT
# value, `partial` is a previously UNPARSED row resolving beside one that already had -- and a
# field changing on a group or item the published side already carried is the third class, the one
# an approver must read (FR-013/SC-004's zero-regression claim, on the equipment side).
"""Hold the source fixed, vary the parser, and report what moved.

`004`'s :mod:`pipeline.report.change_summary` holds the **parser** fixed and varies the
**source**: it is how an approver reads "what did the publisher change this release". This module
is the other comparison — one source, two parsers — and it reuses that module's record types
rather than inventing a second diff vocabulary for the same entities, because an approver who can
already read one should not have to learn another (Principle 14).

**The three sections, and why the third one starting empty is the point.**

*Identical*
    The candidate parser produced exactly what the version published. This is the overwhelming
    majority and it is what FR-009 promises.

*Newly resolved*
    A row the baseline reported as ``OPT-UNPARSED`` now resolves, or a choice that carried no
    items now carries them. This is the feature working, and every row here is a row that was
    absent from the published bundle.

*Corrected*
    A group or choice the baseline **did** resolve now resolves *differently*. Research D5's
    layer 0 makes this structurally impossible for the shapes the baseline handled — every `004`
    production is tried first and wins, so a row the baseline resolved never reaches new code —
    and D5a's decompose-without-renaming rule makes it impossible for the legacy conflated
    bundles too. **The expected size of this section is zero.** It stays in the report because it
    is the instrument that *proves* it is zero, and because a future production may not be so
    tidy.

**Nothing here is a test and nothing here blocks.** It is an approval artifact, produced per
candidate and read by a human, exactly as ``consumer-compat.md`` and ``spot-check.md`` are. The
gate that blocks on a coverage regression is ``COV-OPTION-REGRESSION``, which is a different
instrument measuring a different thing: coverage counts *resolved* rows, so a row that resolves
**differently** is still resolved and is exactly what coverage cannot see.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from pipeline.models.curated import (
    CuratedDatasheet,
    CuratedSnapshot,
    DefaultEquipmentState,
    OptionItemRole,
)
from pipeline.models.findings import Finding
from pipeline.report.catalogue import build_finding
from pipeline.report.change_summary import OptionChoiceChange, OptionGroupChange

#: Research D3.3's three transition classes, in the order the report presents them — the order
#: an approver reads the pattern, not alphabetical and not discovery order.
TRANSITION_RESOLVED_AND_RELINKED: Final = "resolved_and_relinked"
TRANSITION_STATED_BUT_UNLINKED: Final = "stated_but_unlinked"
TRANSITION_NO_GIVEN_UP_ITEM_STATED: Final = "no_given_up_item_stated"

TRANSITION_CLASSES: Final[tuple[str, ...]] = (
    TRANSITION_RESOLVED_AND_RELINKED,
    TRANSITION_STATED_BUT_UNLINKED,
    TRANSITION_NO_GIVEN_UP_ITEM_STATED,
)

_TRANSITION_LABELS: Final[Mapping[str, str]] = {
    TRANSITION_RESOLVED_AND_RELINKED: "Resolved and relinked — the given-up item resolves "
    "and links",
    TRANSITION_STATED_BUT_UNLINKED: "Stated but unlinked — the given-up item is stated but "
    "does not link uniquely",
    TRANSITION_NO_GIVEN_UP_ITEM_STATED: "No given-up item stated — an equip-only shape",
}

#: The two fields FR-007's correction touches. `OPT-LEGACY-CORRECTED` is scoped to these two —
#: never to `name`/`count`/other fields, which are a *different* kind of correction and, per
#: FR-009, are expected to stay at zero (data-model.md §4).
LEGACY_LINK_FIELDS: Final[frozenset[str]] = frozenset(
    {"grants_weapon_line", "replaces_weapon_line"}
)

#: The choice fields compared one by one. `name` and `count` are in the list deliberately: the
#: O1 Ruling says a legacy conflated label is never rewritten, and this is where a rewrite would
#: show up. `points_delta` is compared as a string so an unpriced choice reads `unpriced` and
#: never `0` — a published zero and an absent price are different facts (`004` guarantee 10).
CHOICE_FIELDS: Final[tuple[str, ...]] = (
    "name",
    "count",
    "grants_weapon_line",
    "replaces_weapon_line",
    "is_no_change",
    "points_delta",
    "priced_option_id",
)

#: The group fields compared one by one. The three `006` eligibility columns are absent from
#: every group the baseline published, so a value appearing on one is *newly resolved* detail
#: rather than a correction — which is why they are not in this list.
GROUP_FIELDS: Final[tuple[str, ...]] = ("scope", "scope_n", "min_choices", "max_choices")

#: How an absent value prints. Never `0`, never the empty string: a field the source did not
#: state and a field it stated as zero must stay distinguishable in a report a human reads to
#: decide whether anything moved.
ABSENT: Final = "absent"

#: FR-021's two allowed-addition classes for a new default-equipment group or item, bucketed by
#: what the DATASHEET's own `default_equipment_state` was *before* this run — never by anything
#: about the added row itself, since the row is new and has no "before" of its own to read.
EQUIPMENT_ADDED_TO_ABSENT: Final = "added_to_previously_absent"
EQUIPMENT_ADDED_TO_UNPARSED: Final = "added_to_previously_unparsed"

#: The group and item fields compared one by one on the equipment side — `006` data-model.md
#: §1.2/§1.3's own field lists, minus `id`/`item_index`/`line`, which are identity rather than
#: content and would report as "corrected" on every ordinal renumbering.
EQUIPMENT_GROUP_FIELDS: Final[tuple[str, ...]] = ("applies_to", "model_name", "composition_line")
EQUIPMENT_ITEM_FIELDS: Final[tuple[str, ...]] = ("item_name", "count", "weapon_line")


def _show(value: object) -> str:
    return ABSENT if value is None else str(value)


@dataclass(frozen=True, slots=True)
class FieldDifference:
    """One field of one entity that the two parsers disagree about."""

    datasheet_id: str
    entity_id: str
    field: str
    was: str
    now: str


@dataclass(frozen=True, slots=True)
class EquipmentAddition:
    """A default-equipment group or item absent from the published side, present in the
    candidate's — FR-021's addition, bucketed by what the DATASHEET's own
    ``default_equipment_state`` was before this run (:data:`EQUIPMENT_ADDED_TO_ABSENT` /
    :data:`EQUIPMENT_ADDED_TO_UNPARSED`).
    """

    datasheet_id: str
    datasheet_name: str
    entity_id: str
    classification: str


@dataclass(frozen=True, slots=True)
class OptionRegression:
    """The whole comparison: what stayed, what appeared, and what moved.

    ``corrected`` is the one an approver reads first, and the one that should be empty.

    The ``equipment_*`` fields are the default-equipment twin of the option-side ones above
    (008 T061, FR-021): ``equipment_added`` is the addition side, already classified;
    ``equipment_corrected``/``equipment_removed`` reuse :class:`FieldDifference` directly rather
    than inventing a second diff shape for the same kind of fact (Principle 14).
    """

    published_version_id: str
    identical_groups: int
    identical_choices: int
    newly_resolved_groups: tuple[OptionGroupChange, ...] = ()
    newly_resolved_choices: tuple[OptionChoiceChange, ...] = ()
    removed_groups: tuple[OptionGroupChange, ...] = ()
    removed_choices: tuple[OptionChoiceChange, ...] = ()
    corrected: tuple[FieldDifference, ...] = ()
    #: One `OPT-LEGACY-CORRECTED` finding per choice whose `grants_`/`replaces_weapon_line`
    #: moved (007 T026) — a SUBSET of `corrected` (that tuple still carries every field, for
    #: `is_clean` and the two `corrected_*` helpers below), each carrying its research D3.3
    #: transition class in `detail["transition_class"]` and its name in `detail["choice_name"]`
    #: (FR-007, data-model.md §4).
    legacy_corrections: tuple[Finding, ...] = ()
    equipment_added: tuple[EquipmentAddition, ...] = ()
    equipment_corrected: tuple[FieldDifference, ...] = ()
    equipment_removed: tuple[FieldDifference, ...] = ()

    def corrected_groups(self) -> set[str]:
        """The ids of option groups carrying at least one corrected field."""
        return {d.entity_id for d in self.corrected if d.entity_id.startswith("og-")}

    def corrected_choices(self) -> set[str]:
        """The ids of option choices carrying at least one corrected field."""
        return {d.entity_id for d in self.corrected if d.entity_id.startswith("oc-")}

    @property
    def is_clean(self) -> bool:
        """True when nothing the baseline resolved moved — FR-009's claim, as a boolean.

        A **removed** group or choice counts as a correction: a row the baseline published and
        the candidate does not is a regression by any reading, and folding it in here rather
        than reporting it apart is what stops the headline claim being narrower than it sounds.
        The equipment side's own removals and corrections count on the identical terms — one
        "did anything the baseline resolved move" claim, not two.
        """
        return not (
            self.corrected
            or self.removed_groups
            or self.removed_choices
            or self.equipment_corrected
            or self.equipment_removed
        )


def _groups(snapshot: CuratedSnapshot) -> dict[tuple[str, str], object]:
    return {
        (datasheet.datasheet_id, group.id): group
        for datasheet in snapshot.datasheets
        for group in datasheet.option_groups
    }


def _choices(snapshot: CuratedSnapshot) -> dict[tuple[str, str], object]:
    return {
        (datasheet.datasheet_id, choice.id): choice
        for datasheet in snapshot.datasheets
        for choice in datasheet.option_choices
    }


def _price(choice: object) -> str:
    delta = getattr(choice, "points_delta", None)
    return "unpriced" if delta is None else str(delta)


def _equipment_groups(snapshot: CuratedSnapshot) -> dict[tuple[str, str], object]:
    return {
        (datasheet.datasheet_id, group.id): group
        for datasheet in snapshot.datasheets
        for group in datasheet.equipment_groups
    }


def _equipment_items(snapshot: CuratedSnapshot) -> dict[tuple[str, str, int], object]:
    return {
        (datasheet.datasheet_id, group.id, item.item_index): item
        for datasheet in snapshot.datasheets
        for group in datasheet.equipment_groups
        for item in group.items
    }


def _equipment_classification(state: DefaultEquipmentState | None) -> str:
    """Which of FR-021's two allowed-addition classes a new group or item falls in, read off the
    DATASHEET's own prior state — never off the added row itself, which has no "before".

    ``partial`` is the only state that means "something on this card already resolved, something
    else had not" — a previously unparsed row resolving beside one that already had.
    ``none``/omitted (the datasheet never published an equipment fact) and ``extracted`` (which
    should never see an addition, since a fully-resolved datasheet has no sentence left to close)
    both fall to "previously absent" — the more conservative reading, and the one that puts an
    `extracted`-datasheet surprise in front of an approver via the same bucket a genuinely first
    fact would use, rather than inventing a fourth class for a state this should not reach.
    """
    if state is DefaultEquipmentState.PARTIAL:
        return EQUIPMENT_ADDED_TO_UNPARSED
    return EQUIPMENT_ADDED_TO_ABSENT


def compare(
    published: CuratedSnapshot,
    candidate: CuratedSnapshot,
    *,
    published_version_id: str,
) -> OptionRegression:
    """Compare one source read by two parsers, per entity and per field.

    ``published`` is the git-tracked ``data/`` tree — what a version actually shipped, and the
    only side of this comparison that can be committed. ``candidate`` is the same source rebuilt
    by the extended pipeline from ephemeral inputs.
    """
    before_groups, after_groups = _groups(published), _groups(candidate)
    before_choices, after_choices = _choices(published), _choices(candidate)

    new_groups = tuple(
        (datasheet_id, group_id, "added")
        for datasheet_id, group_id in sorted(set(after_groups) - set(before_groups))
    )
    gone_groups = tuple(
        (datasheet_id, group_id, "removed")
        for datasheet_id, group_id in sorted(set(before_groups) - set(after_groups))
    )
    new_choices = tuple(
        (datasheet_id, choice_id, "added", ABSENT, _price(after_choices[(datasheet_id, choice_id)]))
        for datasheet_id, choice_id in sorted(set(after_choices) - set(before_choices))
    )
    gone_choices = tuple(
        (
            datasheet_id,
            choice_id,
            "removed",
            _price(before_choices[(datasheet_id, choice_id)]),
            ABSENT,
        )
        for datasheet_id, choice_id in sorted(set(before_choices) - set(after_choices))
    )

    corrected: list[FieldDifference] = []
    identical_groups = 0
    for key in sorted(set(before_groups) & set(after_groups)):
        differences = _field_differences(before_groups[key], after_groups[key], GROUP_FIELDS, key)
        corrected.extend(differences)
        identical_groups += not differences

    identical_choices = 0
    legacy_corrections: list[Finding] = []
    for key in sorted(set(before_choices) & set(after_choices)):
        differences = _field_differences(
            before_choices[key], after_choices[key], CHOICE_FIELDS, key
        )
        corrected.extend(differences)
        identical_choices += not differences
        if any(d.field in LEGACY_LINK_FIELDS for d in differences):
            datasheet_id, choice_id = key
            legacy_corrections.append(
                build_finding(
                    "OPT-LEGACY-CORRECTED",
                    entity_refs=[datasheet_id, choice_id],
                    detail={
                        "datasheet_id": datasheet_id,
                        "choice_id": choice_id,
                        "choice_name": _show(getattr(after_choices[key], "name", None)),
                        "transition_class": _transition_class(after_choices[key]),
                    },
                )
            )

    equipment_added, equipment_corrected, equipment_removed = _compare_equipment(
        published, candidate
    )

    return OptionRegression(
        published_version_id=published_version_id,
        identical_groups=identical_groups,
        identical_choices=identical_choices,
        newly_resolved_groups=new_groups,
        newly_resolved_choices=new_choices,
        removed_groups=gone_groups,
        removed_choices=gone_choices,
        corrected=tuple(corrected),
        legacy_corrections=tuple(legacy_corrections),
        equipment_added=equipment_added,
        equipment_corrected=equipment_corrected,
        equipment_removed=equipment_removed,
    )


def _compare_equipment(
    published: CuratedSnapshot, candidate: CuratedSnapshot
) -> tuple[tuple[EquipmentAddition, ...], tuple[FieldDifference, ...], tuple[FieldDifference, ...]]:
    """FR-021's equipment twin of :func:`compare`'s group/choice comparison above.

    Datasheet-scoped classification rather than group/item-scoped: the question FR-021 asks about
    an addition is about the DATASHEET's own prior state, not about the added row (which has no
    "before" to read a class from).
    """
    published_states = {d.datasheet_id: d.default_equipment_state for d in published.datasheets}
    published_names = {d.datasheet_id: d.name for d in published.datasheets}

    before_groups, after_groups = _equipment_groups(published), _equipment_groups(candidate)
    before_items, after_items = _equipment_items(published), _equipment_items(candidate)
    new_group_keys = set(after_groups) - set(before_groups)
    gone_group_keys = set(before_groups) - set(after_groups)

    added = [
        EquipmentAddition(
            datasheet_id=datasheet_id,
            datasheet_name=published_names.get(datasheet_id, ABSENT),
            entity_id=group_id,
            classification=_equipment_classification(published_states.get(datasheet_id)),
        )
        for datasheet_id, group_id in sorted(new_group_keys)
    ]
    removed = [
        FieldDifference(datasheet_id, group_id, "(whole group)", "present", ABSENT)
        for datasheet_id, group_id in sorted(gone_group_keys)
    ]
    corrected: list[FieldDifference] = []
    for key in sorted(set(before_groups) & set(after_groups)):
        corrected.extend(
            _field_differences(before_groups[key], after_groups[key], EQUIPMENT_GROUP_FIELDS, key)
        )

    # An item belonging to a group that is itself new (or itself removed) is not counted a
    # SECOND time here — its presence is a consequence of the group's own addition/removal above,
    # not an independent fact about that item. Only an item added to or dropped from a group that
    # existed on BOTH sides is its own addition/removal.
    added += [
        EquipmentAddition(
            datasheet_id=datasheet_id,
            datasheet_name=published_names.get(datasheet_id, ABSENT),
            entity_id=f"{group_id}/{item_index}",
            classification=_equipment_classification(published_states.get(datasheet_id)),
        )
        for datasheet_id, group_id, item_index in sorted(set(after_items) - set(before_items))
        if (datasheet_id, group_id) not in new_group_keys
    ]
    removed += [
        FieldDifference(datasheet_id, f"{group_id}/{item_index}", "(whole item)", "present", ABSENT)
        for datasheet_id, group_id, item_index in sorted(set(before_items) - set(after_items))
        if (datasheet_id, group_id) not in gone_group_keys
    ]
    for datasheet_id, group_id, item_index in sorted(set(before_items) & set(after_items)):
        item_key = (datasheet_id, group_id, item_index)
        corrected.extend(
            _field_differences(
                before_items[item_key],
                after_items[item_key],
                EQUIPMENT_ITEM_FIELDS,
                (datasheet_id, f"{group_id}/{item_index}"),
            )
        )

    return tuple(added), tuple(corrected), tuple(removed)


def _transition_class(choice: object) -> str:
    """Which of research D3.3's three cases the CANDIDATE side's items now show.

    Classified from the corrected choice's own ``REPLACED``-role items — the structured fact the
    correction produces — never from source text: zero items is "no given-up item stated", one
    linked item is "resolved and relinked", and one unlinked item (or more than one, an
    unmeasured shape) is "stated but unlinked".
    """
    replaced = [
        item
        for item in getattr(choice, "items", ())
        if getattr(item, "role", None) is OptionItemRole.REPLACED
    ]
    if not replaced:
        return TRANSITION_NO_GIVEN_UP_ITEM_STATED
    if len(replaced) == 1 and replaced[0].weapon_line is not None:
        return TRANSITION_RESOLVED_AND_RELINKED
    return TRANSITION_STATED_BUT_UNLINKED


def _field_differences(
    before: object, after: object, fields: Sequence[str], key: tuple[str, str]
) -> list[FieldDifference]:
    datasheet_id, entity_id = key
    found: list[FieldDifference] = []
    for field in fields:
        was, now = getattr(before, field, None), getattr(after, field, None)
        if was == now:
            continue
        found.append(
            FieldDifference(
                datasheet_id=datasheet_id,
                entity_id=entity_id,
                field=field,
                # `_show` rather than the raw repr: an enum's repr carries its class name, and a
                # report a human reads to decide whether to approve a release should not make
                # them parse Python.
                was=_show(getattr(was, "value", was)),
                now=_show(getattr(now, "value", now)),
            )
        )
    return found


def newly_resolved_datasheets(
    published: CuratedSnapshot, candidate: CuratedSnapshot
) -> tuple[str, ...]:
    """Datasheets whose ``wargear_option_state`` improved — the feature's headline set."""
    before: Mapping[str, CuratedDatasheet] = {d.datasheet_id: d for d in published.datasheets}
    improved: list[str] = []
    for datasheet in candidate.datasheets:
        was = before.get(datasheet.datasheet_id)
        if was is None:
            continue
        if was.wargear_option_state != datasheet.wargear_option_state:
            improved.append(datasheet.datasheet_id)
    return tuple(sorted(improved))


def _render_legacy_corrections(findings: Sequence[Finding]) -> list[str]:
    """FR-007's ≈2 030-choice correction, grouped by research D3.3's three transition classes.

    Plan Open Decision O1: an approver reads three patterns with counts and a per-choice name
    enumeration within each, never a row-by-row listing of every changed value.
    """
    by_class: dict[str, list[Finding]] = {cls: [] for cls in TRANSITION_CLASSES}
    for finding in findings:
        by_class.setdefault(str(finding.detail.get("transition_class")), []).append(finding)

    lines = [
        "### FR-007: legacy option link correction, by transition class",
        "",
        f"**{len(findings)}** choice(s) total.",
        "",
    ]
    for transition_class in TRANSITION_CLASSES:
        entries = sorted(
            by_class.get(transition_class, []),
            key=lambda f: (f.detail["datasheet_id"], f.detail["choice_id"]),
        )
        lines.append(f"**{_TRANSITION_LABELS[transition_class]}**: {len(entries)}")
        lines.append("")
        lines += [
            f"- `{f.detail['choice_name']}` (`{f.detail['datasheet_id']}` / "
            f"`{f.detail['choice_id']}`)"
            for f in entries
        ]
        lines.append("")
    return lines


def render(regression: OptionRegression) -> str:
    """The comparison as Markdown, in the order an approver reads it.

    **Corrected first**, because it is the one that decides whether the candidate may proceed,
    and burying an empty section under two long ones would make its emptiness easy to assume
    rather than easy to check.
    """
    lines = [
        "<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Generated by "
        "pipeline/report/option_regression.py (006 T011/T044). -->",
        "<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Corrected section now groups "
        "FR-007's legacy-link corrections by research D3.3's transition class (007 T026). -->",
        "# Option-regression evidence",
        "",
        f"- Compared against published version: `{regression.published_version_id}`",
        "- One source, two parsers. The published side is the git-tracked curated tree; the "
        "candidate side was rebuilt by the extended pipeline from ephemeral inputs that were "
        "discarded when the run ended.",
        "- No source sentence appears on this page. Entities are named by id, or — for a "
        "legacy-link correction — by the item's own curated name (never a source sentence).",
        "",
        "## Corrected",
        "",
        "**This section is expected to be empty, except for FR-007's legacy-link correction "
        "below.** A row the baseline resolved that now resolves differently in any OTHER field "
        "is what FR-009 forbids, and research D5's production ordering makes it structurally "
        "impossible for every shape the baseline handled. A non-empty residual table below is a "
        "finding, not a diff to skim.",
        "",
    ]
    residual = [d for d in regression.corrected if d.field not in LEGACY_LINK_FIELDS]
    if regression.legacy_corrections:
        lines += _render_legacy_corrections(regression.legacy_corrections)
    if not (residual or regression.removed_groups or regression.removed_choices):
        if not regression.legacy_corrections:
            lines += ["Nothing the baseline resolved moved.", ""]
    else:
        lines += [
            "### Other corrected fields",
            "",
            "| Datasheet | Entity | Field | Published | Candidate |",
            "|---|---|---|---|---|",
        ]
        lines += [
            f"| `{d.datasheet_id}` | `{d.entity_id}` | `{d.field}` | {d.was} | {d.now} |"
            for d in residual
        ]
        lines += [
            f"| `{datasheet_id}` | `{entity_id}` | *(whole group)* | present | {ABSENT} |"
            for datasheet_id, entity_id, _kind in regression.removed_groups
        ]
        lines += [
            f"| `{datasheet_id}` | `{entity_id}` | *(whole choice)* | {was} | {ABSENT} |"
            for datasheet_id, entity_id, _kind, was, _now in regression.removed_choices
        ]
        lines.append("")

    lines += [
        "## Identical",
        "",
        "| Entity | Compared | Identical |",
        "|---|---:|---:|",
        f"| option groups | {regression.identical_groups + len(regression.corrected_groups())} | "
        f"{regression.identical_groups} |",
        f"| option choices | "
        f"{regression.identical_choices + len(regression.corrected_choices())} | "
        f"{regression.identical_choices} |",
        "",
        "## Newly resolved",
        "",
        "Rows absent from the published bundle that the extended grammar now resolves. Every one "
        "of these is the feature working; none of them is a change to a value any consumer has "
        "read.",
        "",
        f"- Option groups: **{len(regression.newly_resolved_groups)}**",
        f"- Option choices: **{len(regression.newly_resolved_choices)}**",
        "",
    ]
    if regression.newly_resolved_groups:
        lines += ["| Datasheet | Group |", "|---|---|"]
        lines += [
            f"| `{datasheet_id}` | `{group_id}` |"
            for datasheet_id, group_id, _kind in regression.newly_resolved_groups
        ]
        lines.append("")

    lines += [
        "## Equipment",
        "",
        "FR-021's default-equipment twin of the classification above. Every group or item "
        "absent from the published side is bucketed by what the DATASHEET's own "
        "`default_equipment_state` was **before** this run: `none`/omitted means this is the "
        "first equipment fact the card has ever published; `partial` means one more sentence "
        "resolved beside what already had. The third bucket — a field changing on a group or "
        "item the published side already carried — is the one an approver must read.",
        "",
    ]
    added_to_absent = [
        a for a in regression.equipment_added if a.classification == EQUIPMENT_ADDED_TO_ABSENT
    ]
    added_to_unparsed = [
        a for a in regression.equipment_added if a.classification == EQUIPMENT_ADDED_TO_UNPARSED
    ]
    lines += [
        f"- Added to a previously absent datasheet: **{len(added_to_absent)}**",
        f"- Added to a previously partial datasheet: **{len(added_to_unparsed)}**",
        "",
    ]
    if regression.equipment_corrected or regression.equipment_removed:
        lines += [
            "### Corrected or removed",
            "",
            "| Datasheet | Entity | Field | Published | Candidate |",
            "|---|---|---|---|---|",
        ]
        lines += [
            f"| `{d.datasheet_id}` | `{d.entity_id}` | `{d.field}` | {d.was} | {d.now} |"
            for d in regression.equipment_corrected
        ]
        lines += [
            f"| `{d.datasheet_id}` | `{d.entity_id}` | *({d.field})* | {d.was} | {d.now} |"
            for d in regression.equipment_removed
        ]
        lines.append("")
    else:
        lines += ["No equipment group or item the baseline resolved moved.", ""]
    return "\n".join(lines)
