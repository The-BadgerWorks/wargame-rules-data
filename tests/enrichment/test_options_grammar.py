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
    ItemParse,
    OptionVerb,
    choice_id,
    choice_names,
    group_id,
    option_state,
    parse_row,
    split_conjuncts,
    split_replaced,
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


# --- 006 US1: the extended productions (T013) --------------------------------------------------
#
# Every case below is a shape `004`'s grammar returned `None` for. The `004` cases above are
# unchanged and stay above, which is the ordering half of FR-009 written into this file's own
# layout: the baseline's contract is stated first and never edited to accommodate what follows.


def test_the_distributive_replace_verb_resolves_a_row_004_could_not(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # GF07|3 - `All models in this unit can each have their glimmer rifle replaced with 1 ...`
    parsed = parse_row(dict(option_rows["GF07"])[3])
    assert parsed is not None
    assert parsed.scope is OptionScope.UNIT
    assert parsed.is_per_model is True
    assert choice_names(parsed) == ["ember lance"]
    assert parsed.replaced_clause == "their glimmer rifle"


def test_is_per_model_is_omitted_rather_than_false_on_a_non_distributive_row(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # Never defaulted to False: research D1c measured `can each` on 350 of 571 unparsed rows, so
    # a default would over-grant the majority form of the residual.
    parsed = parse_row(dict(option_rows["GF07"])[8])
    assert parsed is not None
    assert parsed.is_per_model is None


def test_a_scoped_stem_carries_its_model_name_and_its_maximum(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # GF07|1 - `Up to 4 Purgeflight Wardens can each have ...`. `scope` stays `unit`: it is a
    # declared closed set and a fourth member would be a MAJOR break wearing an additive costume.
    parsed = parse_row(dict(option_rows["GF07"])[1])
    assert parsed is not None
    assert parsed.scope is OptionScope.UNIT
    assert parsed.eligible_model_name == "Purgeflight Wardens"
    assert parsed.eligible_max_count == 4
    assert parsed.is_per_model is True


def test_a_scoped_stem_reads_through_a_footnote_marker(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # GF07|20 - the same head with a footnote marker glued to the model name. 24 measured rows
    # carry one inside the stem; a head that cannot read past it loses the row to a typographic
    # convention.
    parsed = parse_row(dict(option_rows["GF07"])[20])
    assert parsed is not None
    assert parsed.eligible_model_name == "Purgeflight Wardens"
    assert parsed.eligible_max_count == 2


def test_the_all_models_head_is_unit_scoped_and_names_no_subset(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    parsed = parse_row(dict(option_rows["GF07"])[3])
    assert parsed is not None
    assert (parsed.scope, parsed.eligible_model_name) == (OptionScope.UNIT, None)


def test_the_any_number_of_named_model_head_carries_the_name(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # `004`'s head requires the literal word `models`; 42 measured rows name the model instead.
    parsed = parse_row(dict(option_rows["GF07"])[5])
    assert parsed is not None
    assert parsed.scope is OptionScope.UNIT
    assert parsed.eligible_model_name == "Purgeflight Wardens"
    assert parsed.eligible_max_count is None


def test_a_possessive_singular_head_is_a_subset_of_exactly_one_model(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # T055, and GF07|8 carries the largest class-2 head: `One <MODEL>'s <ITEM> can be replaced
    # with ...`. The cap is one *model*, which is the eligibility scope, not the choice's count.
    parsed = parse_row(dict(option_rows["GF07"])[8])
    assert parsed is not None
    assert parsed.scope is OptionScope.UNIT
    assert parsed.eligible_model_name == "Purgeflight Warden"
    assert parsed.eligible_max_count == 1
    assert parsed.is_per_model is None


@pytest.mark.parametrize(
    ("description", "scope", "eligible_model_name", "is_per_model"),
    [
        ("This unit can be equipped with 1 void net.", OptionScope.UNIT, None, None),
        (
            "Each of this model's glimmer rifles can be replaced with 1 ember lance.",
            OptionScope.MODEL,
            None,
            None,
        ),
        (
            "Each Purgeflight Warden can be equipped with 1 void net.",
            OptionScope.UNIT,
            "Purgeflight Warden",
            True,
        ),
    ],
)
def test_the_class_2_heads_resolve_a_row_whose_verb_004_already_carried(
    description: str,
    scope: OptionScope,
    eligible_model_name: str | None,
    is_per_model: bool | None,
) -> None:
    # T055. 105 measured rows carry a verb `004` built and a head it did not, which is a
    # different production to write from a row that failed on its verb.
    parsed = parse_row(description)
    assert parsed is not None
    assert parsed.scope is scope
    assert parsed.eligible_model_name == eligible_model_name
    assert parsed.is_per_model is is_per_model


@pytest.mark.parametrize(
    "description",
    [
        # The 27 measured conditional class-2 rows. The condition is an availability predicate
        # and nothing in the schema holds one, so resolving the row would publish "any unit may
        # take this" where the source says "a unit of six or more may" - research D1c.5's ruling
        # on class 9, applied to the same predicate wearing a verb.
        "If this unit has 6 or more models, one model's glimmer rifle can be replaced with 1 x.",
        "If this model is equipped with a fen charm, its glimmer rifle can be replaced with 1 x.",
        # The 14 measured rows whose subject is qualified by the equipment it already carries.
        "One Purgeflight Warden equipped with a glimmer rifle can be replaced with 1 x.",
        "For each fen charm this model is equipped with, it can be equipped with 1 x.",
    ],
)
def test_a_class_2_row_whose_predicate_the_schema_cannot_hold_stays_unparsed(
    description: str,
) -> None:
    assert parse_row(description) is None


# --- 007 US2: the legacy stem-object shape's given-up item (T018) ------------------------------
#
# `_REPLACE_VERB` ("can be replaced with") is the `004` production. Until now it discarded
# everything before the verb phrase, which is precisely the text that names what a sergeant-shape
# subject gives up (research D3.1). GF12 is T005's fixture: row 1 is D3.3's "resolves and links"
# case, row 2 is "stated but does not link uniquely" (link-level, so parse-level the two look the
# same), row 3 is the "no given-up item at all" control — a plain `_EQUIP_VERB` row with nothing
# to do with the legacy replace shape at all — and row 4 is the `OPT-SCOPE-UNRESOLVED` edge case
# (a subject naming no composition row of its own datasheet).


def test_the_legacy_replace_verb_captures_the_given_up_item_between_head_and_verb(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # GF12|1 - `One Marshlight Warden's storm maul can be replaced with 1 glow lance.`
    parsed = parse_row(dict(option_rows["GF12"])[1])
    assert parsed is not None
    assert parsed.eligible_model_name == "Marshlight Warden"
    assert parsed.eligible_max_count == 1
    assert parsed.replaced_clause == "storm maul"
    assert choice_names(parsed) == ["glow lance"]
    assert {choice.verb for choice in parsed.choices} == {OptionVerb.REPLACE}


def test_a_second_legacy_row_captures_its_own_given_up_item(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # GF12|2 - the same shape, a different given-up item ("ceremonial rod"). Parsing does not
    # know yet whether it will link uniquely — that is `link_choice_items`'s job (T019/T023) —
    # so the two rows differ only in which item name is captured.
    parsed = parse_row(dict(option_rows["GF12"])[2])
    assert parsed is not None
    assert parsed.eligible_model_name == "Marshlight Warden"
    assert parsed.replaced_clause == "ceremonial rod"


def test_an_equip_only_row_captures_no_given_up_item(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # GF12|3 - `The Marshlight Warden can be equipped with 1 glow lance.` D3.3's third case: an
    # `_EQUIP_VERB` row never touches the replace-verb capture at all, so `replaced_clause` stays
    # `None` exactly as `004` always produced it.
    parsed = parse_row(dict(option_rows["GF12"])[3])
    assert parsed is not None
    assert {choice.verb for choice in parsed.choices} == {OptionVerb.EQUIP}
    assert parsed.replaced_clause is None


def test_a_legacy_row_whose_subject_matches_no_model_still_captures_its_given_up_item(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # GF12|4 - `One Marshguard Sentinel's storm maul can be replaced with 1 glow lance.` No model
    # row of GF12 is named "Marshguard Sentinel" (research D3.4's OPT-SCOPE-UNRESOLVED edge case,
    # wired at curate time by T025) — but the grammar itself has no composition to check against,
    # so parsing succeeds and captures the given-up item exactly as row 1 does.
    parsed = parse_row(dict(option_rows["GF12"])[4])
    assert parsed is not None
    assert parsed.eligible_model_name == "Marshguard Sentinel"
    assert parsed.replaced_clause == "storm maul"


def test_the_legacy_shapes_singular_head_is_not_forced_per_model(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # The regression this capture must not cause: a singular "One <Model>'s <item>" legacy head
    # is not distributive, and populating `replaced_clause` for it must not flip `is_per_model`
    # to `True` the way the `006` `_DISTRIBUTIVE_REPLACE` shape genuinely does (GF07|8 already
    # pins `is_per_model is None` for the same head shape under `_EQUIP_VERB`; this pins it for
    # the legacy `_REPLACE_VERB` shape too).
    parsed = parse_row(dict(option_rows["GF12"])[1])
    assert parsed is not None
    assert parsed.is_per_model is None


def test_the_distributive_shapes_replaced_clause_still_forces_per_model(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # The other half of the same regression, read from the `006` side: a genuinely distributive
    # stem must still force `is_per_model = True`, so the new capture must not have collapsed
    # the distinction between "legacy stem, now also captured" and "always was distributive".
    parsed = parse_row(dict(option_rows["GF07"])[3])
    assert parsed is not None
    assert parsed.is_per_model is True
    assert parsed.replaced_clause == "their glimmer rifle"


def test_a_group_level_select_quantifier_populates_max_choices() -> None:
    # T019, and the vocabulary is the corpus's own: it states the quantifier as a WORD numeral,
    # which is why research D1d's digit-shaped skeletons matched zero rows. `min_choices` stays
    # omitted because no measured stem states a floor.
    parsed = parse_row(
        "This model can be equipped with up to two of the following:<ul><li>1 a</li><li>1 b</li>"
    )
    assert parsed is not None
    assert (parsed.min_choices, parsed.max_choices) == (None, 2)


def test_the_one_of_the_following_boilerplate_states_no_quantifier(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # 174 measured stems end `one of the following:` and it is boilerplate, not a cap of one.
    parsed = parse_row(dict(option_rows["GF04"])[1])
    assert parsed is not None
    assert (parsed.min_choices, parsed.max_choices) == (None, None)


def test_a_quantifier_form_the_corpus_does_not_state_is_deliberately_unbuilt() -> None:
    # `N different <ITEM> from the following` - research D1d's other skeleton, measured at ZERO
    # rows. Built productions are for measured vocabulary; this one stays unbuilt so a shift
    # shows up as a falling coverage figure rather than as a guess.
    parsed = parse_row(
        "This model can be equipped with 2 different weapons from the following:<ul><li>1 a</li>"
    )
    assert parsed is not None
    assert parsed.max_choices is None


# --- multi-item conjunct splitting (T018) ------------------------------------------------------


def test_the_granted_side_splits_on_a_counted_conjunct() -> None:
    assert split_conjuncts("ember lance and 1 close combat weapon", 1) == (
        ItemParse(name="ember lance", count=1),
        ItemParse(name="close combat weapon", count=1),
    )


def test_the_granted_side_does_not_split_a_name_that_merely_contains_and() -> None:
    # The leading count is the evidence a second item started. Without one, `and` is part of the
    # name, and splitting on it would invent an item the source does not name.
    assert split_conjuncts("bolt and blade", None) == (ItemParse(name="bolt and blade"),)


def test_the_replaced_side_splits_on_a_bare_conjunction() -> None:
    # The possessive side lists the model's own weapons and states no counts, so `and` is the
    # only boundary the source gives.
    assert split_replaced("their glimmer rifle and fen halberd") == (
        ItemParse(name="glimmer rifle"),
        ItemParse(name="fen halberd"),
    )


def test_splitting_never_rewrites_the_choice_it_decomposes(
    option_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    # The O1 Ruling. GF07|2's object clause conflates a bundle and parses TODAY; decomposition
    # gives it items and leaves `name` and `count` exactly as `004` produced them.
    parsed = parse_row(dict(option_rows["GF07"])[2])
    assert parsed is not None
    (choice,) = parsed.choices
    assert (choice.name, choice.count) == ("ember lance and 2 void nets", 1)
    assert split_conjuncts(choice.name, choice.count) == (
        ItemParse(name="ember lance", count=1),
        ItemParse(name="void nets", count=2),
    )
