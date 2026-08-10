# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the FR-009 zero-regression
# harness, layer 2 (006 task T011): the per-choice, per-field comparison between what a version
# actually published and what the extended pipeline rebuilds from the same source, rendered
# through change_summary.py's existing OptionGroupChange/OptionChoiceChange vocabulary into
# Identical / Newly resolved / Corrected (006 research D5 layer 2).
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

from pipeline.models.curated import CuratedDatasheet, CuratedSnapshot
from pipeline.report.change_summary import OptionChoiceChange, OptionGroupChange

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
class OptionRegression:
    """The whole comparison: what stayed, what appeared, and what moved.

    ``corrected`` is the one an approver reads first, and the one that should be empty.
    """

    published_version_id: str
    identical_groups: int
    identical_choices: int
    newly_resolved_groups: tuple[OptionGroupChange, ...] = ()
    newly_resolved_choices: tuple[OptionChoiceChange, ...] = ()
    removed_groups: tuple[OptionGroupChange, ...] = ()
    removed_choices: tuple[OptionChoiceChange, ...] = ()
    corrected: tuple[FieldDifference, ...] = ()

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
        """
        return not (self.corrected or self.removed_groups or self.removed_choices)


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
    for key in sorted(set(before_choices) & set(after_choices)):
        differences = _field_differences(
            before_choices[key], after_choices[key], CHOICE_FIELDS, key
        )
        corrected.extend(differences)
        identical_choices += not differences

    return OptionRegression(
        published_version_id=published_version_id,
        identical_groups=identical_groups,
        identical_choices=identical_choices,
        newly_resolved_groups=new_groups,
        newly_resolved_choices=new_choices,
        removed_groups=gone_groups,
        removed_choices=gone_choices,
        corrected=tuple(corrected),
    )


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


def render(regression: OptionRegression) -> str:
    """The comparison as Markdown, in the order an approver reads it.

    **Corrected first**, because it is the one that decides whether the candidate may proceed,
    and burying an empty section under two long ones would make its emptiness easy to assume
    rather than easy to check.
    """
    lines = [
        "<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Generated by "
        "pipeline/report/option_regression.py (006 T011/T044). -->",
        "# Option-regression evidence",
        "",
        f"- Compared against published version: `{regression.published_version_id}`",
        "- One source, two parsers. The published side is the git-tracked curated tree; the "
        "candidate side was rebuilt by the extended pipeline from ephemeral inputs that were "
        "discarded when the run ended.",
        "- No source sentence appears on this page. Entities are named by id.",
        "",
        "## Corrected",
        "",
        "**This section is expected to be empty.** A row the baseline resolved that now "
        "resolves differently is what FR-009 forbids, and research D5's production ordering "
        "makes it structurally impossible for every shape the baseline handled. A non-empty "
        "section here is a finding, not a diff to skim.",
        "",
    ]
    if regression.is_clean:
        lines += ["Nothing the baseline resolved moved.", ""]
    else:
        lines += [
            "| Datasheet | Entity | Field | Published | Candidate |",
            "|---|---|---|---|---|",
        ]
        lines += [
            f"| `{d.datasheet_id}` | `{d.entity_id}` | `{d.field}` | {d.was} | {d.now} |"
            for d in regression.corrected
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
    return "\n".join(lines)
