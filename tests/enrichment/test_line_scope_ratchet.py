# AI-Assisted: Claude Code (model: claude-sonnet-5) - 2026-10-09 pipeline P3 task 5: failing-first
# tests for `loadout.options_line_scoped`, the ratcheted coverage figure over
# `CuratedOptionGroup.eligible_composition_lines` (spec §4.2 P4b). The denominator is option groups
# with at least one REPLACED choice item; the numerator is those whose eligible_composition_lines
# derivation resolved (!= ()). Confirmed failing before `pipeline/validate/coverage.py` declared
# `OPTIONS_LINE_SCOPED_KEY` and before `pipeline/validate/gates.py` knew
# `COV-LINE-SCOPE-REGRESSION`.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - final review I1: the denominator is
# corrected to figure F -- option groups with a REPLACED item ON DATASHEETS THAT HAVE >= 1
# equipment group with `composition_line` set. The existing figure test's datasheet gained a
# line-resolved equipment group (it had none, which under the corrected reading would drop it out
# of the denominator entirely). A new test pins the datasheet-level filter directly: a candidate
# group on a datasheet with no line-resolved equipment group is excluded from both resolved and
# total. A second new test states the integer-percent coarseness out loud (trap 1): counts
# (3, 213) and (2, 213) share one percent, so the gate must re-derive counts, never trust the
# percent alone.
"""`loadout.options_line_scoped` — did this release publish fewer line-scoped option groups,
as a proportion of the groups that could ever have one, than the previous published release?

Trap 1 (`CLAUDE.md`): `LoadoutCoverage.ratio_percent` returns 100 when `total` is 0, so every
assertion here states `resolved` and `total` alongside any percentage — never the percentage
alone — and one test below states the empty-denominator trap out loud rather than leaving it
implicit.
"""

from __future__ import annotations

from pipeline.models.curated import (
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
    EquipmentAppliesTo,
    OptionItemRole,
    OptionScope,
)
from pipeline.report.pr_body import (
    _RATCHETED_LOADOUT_FIGURES,  # noqa: PLC2701 (test of the constant itself)
)
from pipeline.validate.coverage import (
    OPTIONS_LINE_SCOPED_KEY,
    LoadoutCoverage,
    line_scope_candidate_groups,
    line_scoped_groups,
    loadout_coverages,
)
from pipeline.validate.gates import check_option_ratchet
from tests.factories import datasheet, snapshot


def _option_group(
    group_id: str, *, eligible_composition_lines: tuple[int, ...] = ()
) -> CuratedOptionGroup:
    return CuratedOptionGroup(
        id=group_id,
        line=1,
        scope=OptionScope.UNIT,
        eligible_composition_lines=eligible_composition_lines,
    )


def _choice(group_id: str, *, items: tuple[CuratedOptionChoiceItem, ...]) -> CuratedOptionChoice:
    return CuratedOptionChoice(id=f"oc-{group_id}-1", group_id=group_id, name="choice", items=items)


def _replaced(name: str, index: int = 1) -> CuratedOptionChoiceItem:
    return CuratedOptionChoiceItem(role=OptionItemRole.REPLACED, item_index=index, item_name=name)


def _granted(name: str, index: int = 1) -> CuratedOptionChoiceItem:
    return CuratedOptionChoiceItem(role=OptionItemRole.GRANTED, item_index=index, item_name=name)


def _line_resolved_equipment_group(line: int, *, composition_line: int) -> CuratedEquipmentGroup:
    """One line-resolved default-equipment group -- figure F's own precondition (final review
    I1): a datasheet only enters the denominator when it has >= 1 of these."""
    return CuratedEquipmentGroup(
        id=f"eq-fx-{line}",
        line=line,
        applies_to=EquipmentAppliesTo.MODEL_GROUP,
        model_name="Test Sergeant",
        composition_line=composition_line,
        items=(CuratedEquipmentItem(item_index=1, item_name="test blade"),),
    )


def test_the_figure_counts_scoped_groups_over_groups_with_a_replaced_item() -> None:
    """Three groups on one datasheet: scoped-with-replaced, unscoped-with-replaced, and
    granted-only. The granted-only group names no REPLACED item, so it is outside the candidate
    set entirely — "has a replaced item" is the denominator's whole test, not "has any choice".
    The datasheet carries a line-resolved equipment group (final review I1's own precondition),
    so all three groups are in scope for the datasheet-level filter; "has a replaced item" is
    then the only thing separating the candidates from the granted-only group."""
    scoped = _option_group("og-fx-1", eligible_composition_lines=(2, 3))
    unscoped = _option_group("og-fx-2")
    granted_only = _option_group("og-fx-3")

    ds = datasheet(datasheet_id="ds-fx-scope")
    ds = ds.model_copy(
        update={
            "equipment_groups": [_line_resolved_equipment_group(1, composition_line=1)],
            "option_groups": [scoped, unscoped, granted_only],
            "option_choices": [
                _choice("og-fx-1", items=(_replaced("test blade"), _granted("test maul"))),
                _choice("og-fx-2", items=(_replaced("test shield"), _granted("test lantern"))),
                _choice("og-fx-3", items=(_granted("test maul"),)),
            ],
        }
    )
    snap = snapshot(datasheets=[ds])

    assert line_scope_candidate_groups(snap) == 2
    assert line_scoped_groups(snap) == 1

    figure = loadout_coverages(snap)[OPTIONS_LINE_SCOPED_KEY]
    assert (figure.resolved, figure.total, figure.ratio_percent) == (1, 2, 50.0)


def test_a_replaced_item_group_on_a_datasheet_with_no_line_resolved_group_is_not_a_candidate() -> (
    None
):
    """Final review I1's own receipt: two datasheets, each with one group carrying a REPLACED
    item. The first has a line-resolved default-equipment group (figure F's own precondition);
    the second has none at all. The total counts only the first -- a REPLACED-item group on a
    datasheet `derive_line_scopes` could never have scoped (no candidate line exists for it to
    resolve to) is outside the question this figure asks, the same "outside the question"
    reasoning the denominator already applies to a GRANTED-only group."""
    with_line = _option_group("og-fx-with-line", eligible_composition_lines=(1,))
    ds_with_line = datasheet(datasheet_id="ds-fx-with-line")
    ds_with_line = ds_with_line.model_copy(
        update={
            "equipment_groups": [_line_resolved_equipment_group(1, composition_line=1)],
            "option_groups": [with_line],
            "option_choices": [
                _choice("og-fx-with-line", items=(_replaced("test blade"), _granted("test maul")))
            ],
        }
    )

    without_line = _option_group("og-fx-without-line")
    ds_without_line = datasheet(datasheet_id="ds-fx-without-line", faction_id="f-emberwrights")
    ds_without_line = ds_without_line.model_copy(
        update={
            "equipment_groups": [],
            "option_groups": [without_line],
            "option_choices": [
                _choice(
                    "og-fx-without-line",
                    items=(_replaced("test shield"), _granted("test lantern")),
                )
            ],
        }
    )

    snap = snapshot(datasheets=[ds_with_line, ds_without_line])

    assert line_scope_candidate_groups(snap) == 1
    assert line_scoped_groups(snap) == 1

    figure = loadout_coverages(snap)[OPTIONS_LINE_SCOPED_KEY]
    assert (figure.resolved, figure.total) == (1, 1)


def test_the_percent_hides_what_the_counts_show() -> None:
    """Trap 1 (`CLAUDE.md`), stated out loud rather than left implicit: `ratio_percent` is an
    **integer**, so two different counts can round to the identical percent. (3, 213) and
    (2, 213) round to the same 1% here -- a manager re-deriving this figure at the gate must read
    `resolved`/`total` from the report, never trust the rendered percent alone, because the
    percent cannot tell these two releases apart even though one published one fewer scoped
    group than the other."""
    higher = LoadoutCoverage(OPTIONS_LINE_SCOPED_KEY, resolved=3, total=213)
    lower = LoadoutCoverage(OPTIONS_LINE_SCOPED_KEY, resolved=2, total=213)

    assert higher.resolved != lower.resolved
    assert higher.ratio_percent == lower.ratio_percent


def test_a_regression_past_tolerance_blocks_and_within_tolerance_does_not() -> None:
    current = LoadoutCoverage(OPTIONS_LINE_SCOPED_KEY, resolved=40, total=100)

    findings = check_option_ratchet(current, previous_percent=60, tolerance=0.0)
    assert [f.finding_code for f in findings] == ["COV-LINE-SCOPE-REGRESSION"]

    assert check_option_ratchet(current, previous_percent=41, tolerance=0.01) == []


def test_no_previous_figure_means_no_finding_and_the_pr_body_says_so() -> None:
    """Trap 1 / standing rule 8: the floor is read from the previous published report, and a
    first release (or one predating this feature) has no such row — `None`, never 0, never an
    authored default. The PR body still has to render the figure, so it must be in the ratcheted
    set the body checks against."""
    current = LoadoutCoverage(OPTIONS_LINE_SCOPED_KEY, resolved=1, total=2)
    assert check_option_ratchet(current, previous_percent=None, tolerance=0.0) == []
    assert OPTIONS_LINE_SCOPED_KEY in _RATCHETED_LOADOUT_FIGURES


def test_an_empty_denominator_reads_100_so_the_gate_must_re_derive_counts() -> None:
    """Trap 1 stated as a test, not hidden: total 0 -> 100. A manager re-deriving this figure at
    the gate must read `resolved`/`total`, never trust the percent alone."""
    assert LoadoutCoverage(OPTIONS_LINE_SCOPED_KEY, resolved=0, total=0).ratio_percent == 100
