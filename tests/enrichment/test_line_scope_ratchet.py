# AI-Assisted: Claude Code (model: claude-sonnet-5) - 2026-10-09 pipeline P3 task 5: failing-first
# tests for `loadout.options_line_scoped`, the ratcheted coverage figure over
# `CuratedOptionGroup.eligible_composition_lines` (spec §4.3). The denominator is option groups
# with at least one REPLACED choice item; the numerator is those whose eligible_composition_lines
# derivation resolved (!= ()). Confirmed failing before `pipeline/validate/coverage.py` declared
# `OPTIONS_LINE_SCOPED_KEY` and before `pipeline/validate/gates.py` knew
# `COV-LINE-SCOPE-REGRESSION`.
"""`loadout.options_line_scoped` — did this release publish fewer line-scoped option groups,
as a proportion of the groups that could ever have one, than the previous published release?

Trap 1 (`CLAUDE.md`): `LoadoutCoverage.ratio_percent` returns 100 when `total` is 0, so every
assertion here states `resolved` and `total` alongside any percentage — never the percentage
alone — and one test below states the empty-denominator trap out loud rather than leaving it
implicit.
"""

from __future__ import annotations

from pipeline.models.curated import (
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
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


def test_the_figure_counts_scoped_groups_over_groups_with_a_replaced_item() -> None:
    """Three groups on one datasheet: scoped-with-replaced, unscoped-with-replaced, and
    granted-only. The granted-only group names no REPLACED item, so it is outside the candidate
    set entirely — "has a replaced item" is the denominator's whole test, not "has any choice"."""
    scoped = _option_group("og-fx-1", eligible_composition_lines=(2, 3))
    unscoped = _option_group("og-fx-2")
    granted_only = _option_group("og-fx-3")

    ds = datasheet(datasheet_id="ds-fx-scope")
    ds = ds.model_copy(
        update={
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
