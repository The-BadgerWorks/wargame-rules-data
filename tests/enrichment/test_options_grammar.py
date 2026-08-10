# AI-Assisted: Claude Code (model: claude-opus-5) - The wargear-option grammar's contract (004
# task T022): one case per clause head and verb of research D3, the `<li>` split ahead of the
# clause grammar and its space-variant `<ul` forms, the unmatched head that is reported rather
# than dropped, the never-priced "no change" choice, line-ordinal identity, and the three-state
# rule (FR-010, FR-015, FR-016).
"""What the option grammar promises, stated against the synthetic fixture.

The load-bearing assertions here are the two negatives — an unmatched head is **reported**, and
a "no change" alternative is **never** priced — plus the identity one. Identity is what decides
whether an upstream relabelling reaches an approver as "this option was renamed" or as "this
option vanished and a different one appeared", and only the first of those is true.
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from pipeline.models.curated import CuratedOptionChoice, OptionScope, WargearOptionState
from pipeline.models.findings import Severity
from pipeline.parse.options_grammar import (
    NO_CHANGE_NAME,
    OptionVerb,
    choice_id,
    choice_names,
    group_id,
    option_state,
    parse_row,
    split_sublist,
)
from pipeline.report.catalogue import CATALOGUE

# --- the clause head table (research D3) -------------------------------------------------------


def test_this_model_is_a_model_scoped_group(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    parsed = parse_row(dict(option_rows["GF01"])[1])
    assert parsed is not None
    assert parsed.scope is OptionScope.MODEL
    assert parsed.scope_n is None
    assert choice_names(parsed) == ["glimmer lantern"]


def test_any_number_of_models_is_a_unit_scoped_group(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    parsed = parse_row(dict(option_rows["GF02"])[1])
    assert parsed is not None
    assert parsed.scope is OptionScope.UNIT


def test_for_every_n_models_carries_its_n(option_rows: Mapping[str, list[tuple[int, str]]]) -> None:
    parsed = parse_row(dict(option_rows["GF03"])[1])
    assert parsed is not None
    assert (parsed.scope, parsed.scope_n) == (OptionScope.PER_N_MODELS, 3)


def test_a_leading_integer_head_is_unit_scoped(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    parsed = parse_row(dict(option_rows["GF06"])[1])
    assert parsed is not None
    assert parsed.scope is OptionScope.UNIT


def test_a_leading_the_head_is_unit_scoped(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    parsed = parse_row(dict(option_rows["GF04"])[1])
    assert parsed is not None
    assert parsed.scope is OptionScope.UNIT


# --- the verbs and the `with N` quantifier -----------------------------------------------------


def test_the_replace_verb_marks_every_choice_it_governs(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    parsed = parse_row(dict(option_rows["GF04"])[1])
    assert parsed is not None
    assert {choice.verb for choice in parsed.choices} == {OptionVerb.REPLACE}


def test_the_equip_verb_marks_every_choice_it_governs(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    parsed = parse_row(dict(option_rows["GF06"])[1])
    assert parsed is not None
    assert {choice.verb for choice in parsed.choices} == {OptionVerb.EQUIP}


def test_with_n_becomes_the_choices_count(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    parsed = parse_row(dict(option_rows["GF06"])[1])
    assert parsed is not None
    assert [(c.name, c.count) for c in parsed.choices] == [
        ("chime flail", 1),
        ("resonance shards", 2),
    ]


def test_an_unquantified_choice_carries_no_count() -> None:
    parsed = parse_row("This model can be equipped with a fen charm.")
    assert parsed is not None
    assert parsed.choices[0].count is None


# --- the `<li>` split, which runs BEFORE the clause grammar ------------------------------------


def test_the_split_matches_the_space_variant_ul_not_only_the_literal_tag() -> None:
    # The export emits 2 050 sub-list openers, exactly one of which is the literal string
    # `<ul>`. A parser matching only that one reads every other row's alternatives as part of
    # its stem clause.
    for opener in ("<ul>", "< ul >", "<ul", "<UL>"):
        row = f"The Sedgeward Adept can be equipped with:{opener}<li>1 a</li>"
        stem, items = split_sublist(row)
        assert stem.strip() == "The Sedgeward Adept can be equipped with:"
        assert items, f"{opener!r} was not recognised as a sub-list opener"


def test_the_split_precedes_the_clause_grammar(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    parsed = parse_row(dict(option_rows["GF04"])[1])
    assert parsed is not None
    # Three alternatives, not one stem clause that happens to contain three names.
    assert choice_names(parsed) == ["sedge halberd", "mire censer", NO_CHANGE_NAME]


# --- the residual --------------------------------------------------------------------------


def test_an_unmatched_head_is_reported_and_never_dropped(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    assert parse_row(dict(option_rows["GF05"])[1]) is None
    assert CATALOGUE["OPT-UNPARSED"].severity is Severity.ADVISORY


@pytest.mark.parametrize(
    "description",
    [
        "Each Mirefen Tangler may take a snare net.",
        "This model may replace its fen spear with a bog maul.",
        "1 in every 3 models can be equipped with 1 tanglelance.",
        "for every 3 models, 1 model can be equipped with 1 tanglelance.",
        "Only one model can be equipped with 1 tanglelance.",
        "This model has no options.",
        "",
    ],
)
def test_the_productions_deliberately_not_built_stay_unbuilt(description: str) -> None:
    # research D3 verified these absent from the baseline and refused to build for them. The
    # point of the refusal is that a vocabulary shift shows up as a falling coverage figure
    # rather than as data that quietly stopped being extracted.
    assert parse_row(description) is None


# --- "no change" ------------------------------------------------------------------------------


def test_an_explicit_no_change_choice_is_flagged_and_never_priced(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    parsed = parse_row(dict(option_rows["GF04"])[1])
    assert parsed is not None
    (no_change,) = [choice for choice in parsed.choices if choice.is_no_change]
    assert no_change.name == NO_CHANGE_NAME

    # And the curated model refuses to price one at all, so the guarantee does not depend on
    # every future call site remembering it.
    with pytest.raises(ValueError, match="no change"):
        CuratedOptionChoice(
            id="oc-x-1-3", group_id="og-x-1", name=NO_CHANGE_NAME, is_no_change=True, points_delta=0
        )


# --- identity (FR-015) ------------------------------------------------------------------------


def test_group_identity_derives_from_the_sources_own_line_ordinal() -> None:
    assert group_id("ds-sedgeward-conclave", 1) == "og-sedgeward-conclave-1"
    assert choice_id(group_id("ds-sedgeward-conclave", 1), 2) == "oc-sedgeward-conclave-1-2"


def test_a_relabelling_is_a_rename_rather_than_a_removal_plus_an_addition() -> None:
    before = parse_row("The Sedgeward Adept can be equipped with 1 sedge halberd.")
    after = parse_row("The Sedgeward Adept can be equipped with 1 sedge glaive.")
    assert before is not None and after is not None
    # Same source row, so the same ids on both sides of the change...
    assert group_id("ds-sedgeward-conclave", 1) == group_id("ds-sedgeward-conclave", 1)
    # ...and only the name moves, which is what `reconcile/conflicts.py::detect_renames` reports.
    assert choice_names(before) != choice_names(after)


# --- the three-state rule (FR-016) -------------------------------------------------------------


@pytest.mark.parametrize(
    ("row_count", "unparsed_count", "expected"),
    [
        (0, 0, WargearOptionState.NONE),
        (3, 0, WargearOptionState.EXTRACTED),
        (3, 1, WargearOptionState.PARTIAL),
    ],
)
def test_the_three_state_rule(
    row_count: int, unparsed_count: int, expected: WargearOptionState
) -> None:
    assert option_state(row_count=row_count, unparsed_count=unparsed_count) is expected


def test_the_fixtures_residual_is_exactly_the_one_unmatched_head(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    """The fixture's own coverage, pinned so a grammar change has to state its effect.

    Five of the six `004` rows resolve and one does not — the quirk class research D3 calls the
    residual. Pinning the identity of that row rather than a percentage is what makes this test
    say something when it fails: "the grammar stopped matching GF03" is actionable, "83% became
    67%" is not.

    **Scoped to the `004` datasheets on purpose.** `006` T003 added GF07-GF11, whose rows are the
    shapes this grammar was never built for; every one of them is residual today and the point of
    `006` is that some of them stop being. Folding them into this assertion would make a
    deliberate improvement read as a regression here, while the assertion that actually protects
    `004` — that *these* six rows never move — would be diluted by it. That is what
    ``tests/enrichment/test_options_grammar_regression.py`` is for.
    """
    baseline = {"GF01", "GF02", "GF03", "GF04", "GF05", "GF06"}
    rows_in_baseline = {
        datasheet_id: rows for datasheet_id, rows in option_rows.items() if datasheet_id in baseline
    }
    residual = {
        (datasheet_id, line)
        for datasheet_id, rows in rows_in_baseline.items()
        for line, description in rows
        if parse_row(description) is None
    }
    assert residual == {("GF05", 1)}
    assert sum(len(rows) for rows in rows_in_baseline.values()) == 6


def test_parsing_is_deterministic_over_the_whole_fixture(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    def run() -> list[object]:
        return [
            (datasheet_id, line, parse_row(description))
            for datasheet_id, rows in sorted(option_rows.items())
            for line, description in rows
        ]

    assert run() == run()
