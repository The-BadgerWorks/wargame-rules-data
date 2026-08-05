# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the datacard DOM extraction (004 task
# T073): label-anchored block identity, the homoglyph-folded column read, the separately-labelled
# keyword split, and — the point of the whole design — that the extracted composition and option
# lists feed pipeline.parse.composition_grammar and pipeline.parse.options_grammar UNMODIFIED
# (risk R-A, research D1c-D1d, docs/verification/html-markup-spike.md).
"""The mode-blindness proof, stated as tests rather than as a design note.

`004`'s architecture rests on one claim: the composition and option grammars, measured once
against the bulk export's shape, are reused **unchanged** against the current edition's markup.
The tests that matter here are therefore not "the parser extracts something" but
:func:`test_every_composition_line_resolves_through_the_unmodified_grammar` and
:func:`test_every_option_row_reaches_the_unmodified_grammar_with_its_sub_list_intact` — they run
the *same functions* the csv path runs, over the html fixture, and compare the results with what
the csv fixture produces for the same invented units.

The fixture is synthetic and reproduces the structure recorded in
``docs/verification/html-markup-spike.md``, **including** the Cyrillic homoglyph in the column
class names, because a defence proven only against markup nobody publishes is not a defence.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pytest
from selectolax.lexbor import LexborHTMLParser, LexborNode

from pipeline.acquire.fixtures import FixturePayload
from pipeline.parse.composition_grammar import link_model_line, parse_entry
from pipeline.parse.options_grammar import choice_names, parse_row, split_sublist
from pipeline.parse.wahapedia_html_dom import (
    CHARACTERISTIC_NAMES,
    HtmlStructureError,
    blocks_of,
    emit_records,
    parse_faction_page,
    read_datacard_payloads,
)

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "enrichment"
    / "wahapedia-html"
    / "glimmerfen-covenant.html"
)
SLUG = "glimmerfen-covenant"

#: The html fixture's datacard anchors, against the csv fixture's ids for the same invented
#: units. Stated here rather than derived, because the whole point of the cross-mode assertions
#: below is that the two shapes are compared by *unit*, not by whatever id each one happens to
#: mint.
CSV_ID_TO_ANCHOR: Mapping[str, str] = {
    "GF01": "Glimmerfen-Warden",
    "GF02": "Fenmire-Skirmishers",
    "GF03": "Bracklight-Outriders",
    "GF04": "Sedgeward-Conclave",
    "GF05": "Mirefen-Tanglers",
    "GF06": "Thornlight-Chorus",
}


@pytest.fixture(scope="module")
def page():  # type: ignore[no-untyped-def] - the return type is the module's own dataclass
    return parse_faction_page(SLUG, FIXTURE.read_text(encoding="utf-8"))


def _card(page, anchor: str):  # type: ignore[no-untyped-def]
    return next(card for card in page.cards if card.detail_id.endswith(f":{anchor}"))


# -- card and block discovery ----------------------------------------------------------------


def test_every_datacard_on_the_page_is_found_exactly_once(page) -> None:  # type: ignore[no-untyped-def]
    assert len(page.cards) == len(CSV_ID_TO_ANCHOR)
    assert len({card.detail_id for card in page.cards}) == len(page.cards)


def test_a_datasheet_is_identified_by_the_sources_own_anchor(page) -> None:  # type: ignore[no-untyped-def]
    # Not by its display name: an anchor is what the publisher's own sitemap and its own
    # cross-card links use, so a renamed datasheet keeps its identity rather than becoming a
    # removal plus an addition.
    assert {card.detail_id for card in page.cards} == {
        f"{SLUG}:{anchor}" for anchor in CSV_ID_TO_ANCHOR.values()
    }


def _first_frame() -> LexborNode:
    """The first datacard as a DOM node, for the two tests that assert about segmentation."""
    frame = LexborHTMLParser(FIXTURE.read_text(encoding="utf-8")).css_first(
        "div.dsOuterFrame.datasheet"
    )
    assert frame is not None
    return frame


def test_block_identity_comes_from_the_label_and_not_from_a_class() -> None:
    """``div.dsAbility`` is shared by unrelated blocks; only the heading tells them apart."""
    found = blocks_of(_first_frame())
    labels = [block.label for block in found]
    assert "UNIT COMPOSITION" in labels
    assert "ABILITIES" in labels

    # Both blocks are made of elements carrying the same class, so a class-keyed reader would
    # merge them into one and there would be no way downstream to tell which was which.
    composition = next(block for block in found if block.label == "UNIT COMPOSITION")
    abilities = next(block for block in found if block.label == "ABILITIES")
    assert {node.attributes.get("class") for node in composition.nodes} & {
        node.attributes.get("class") for node in abilities.nodes
    }


def test_the_weapon_tables_column_heads_are_not_read_as_block_labels() -> None:
    """They share the ``dsHeader`` class; the walk excludes them by never entering a table."""
    labels = {block.label for block in blocks_of(_first_frame())}
    assert not labels & {"RANGE", "A", "S", "AP", "D", "BS", "WS"}


def test_an_unrecognised_block_is_passed_over_and_recorded(page) -> None:  # type: ignore[no-untyped-def]
    """A datasheet may head its own block with anything, so an unknown label is not an error —
    but it is not invisible either, or a vocabulary shift would be indistinguishable from a
    quiet stop in extraction."""
    assert "STRATAGEMS" in page.unconsumed_labels


def test_a_page_with_no_datacard_fails_the_run_loudly() -> None:
    with pytest.raises(HtmlStructureError, match="no div.dsOuterFrame"):
        parse_faction_page(SLUG, "<html><body><div class='other'></div></body></html>")


def test_a_card_missing_a_required_block_fails_the_run_loudly() -> None:
    """The structural assertion `004` T073 asks for: a move fails loudly, not silently."""
    mangled = FIXTURE.read_text(encoding="utf-8").replace("UNIT COMPOSITION", "UNIT MAKE-UP")
    with pytest.raises(HtmlStructureError, match="UNIT COMPOSITION"):
        parse_faction_page(SLUG, mangled)


def test_a_moved_characteristic_row_fails_the_run_loudly() -> None:
    """Profiles after the first are read by position, which is safe only while the order holds."""
    mangled = FIXTURE.read_text(encoding="utf-8").replace(
        '<div class="dsCharName">SV</div>', '<div class="dsCharName">SAVE</div>'
    )
    with pytest.raises(HtmlStructureError, match="characteristic row"):
        parse_faction_page(SLUG, mangled)


# -- the homoglyph trap ----------------------------------------------------------------------


def test_the_fixture_really_carries_the_cyrillic_homoglyph() -> None:
    """If this ever fails, the test below has stopped proving anything (spike §5, trap 1)."""
    text = FIXTURE.read_text(encoding="utf-8")
    assert "dsLeftСol" in text, "the fixture must spell the column class as the source does"
    assert "dsLeftCol" not in text, "an ASCII spelling would make the defence untested"


def test_the_columns_are_read_despite_the_homoglyph(page) -> None:  # type: ignore[no-untyped-def]
    # The ASCII selector `.dsLeftCol` matches nothing on the real page, silently. Every card
    # here yields its two-column body and its keyword split regardless of the spelling.
    assert all(card.keywords for card in page.cards)
    assert all(card.abilities for card in page.cards)


# -- the keyword split (FR-017) ---------------------------------------------------------------


def test_the_faction_split_comes_from_the_pages_own_two_labelled_columns(page) -> None:  # type: ignore[no-untyped-def]
    warden = _card(page, "Glimmerfen-Warden")
    # (keyword, model scope, is_faction_keyword) — the scope is empty where the page names no
    # model, which is the ordinary case and the export's own empty `model` column.
    assert warden.keywords == (
        ("INFANTRY", "", False),
        ("GLIMMERFEN COVENANT", "", True),
        ("THORNLIGHT CHORUS", "", True),
    )


def test_a_multi_word_keyword_is_one_keyword_and_not_several(page) -> None:  # type: ignore[no-untyped-def]
    """The page spells one keyword as several adjacent spans; they are line breaks, not tokens."""
    outriders = _card(page, "Bracklight-Outriders")
    faction_keywords = [keyword for keyword, _scope, is_faction in outriders.keywords if is_faction]
    assert faction_keywords == ["GLIMMERFEN COVENANT", "THORNLIGHT CHORUS", "BRACKLIGHT HOST"]


# -- the mode-blindness proof -----------------------------------------------------------------


def test_every_composition_line_resolves_through_the_unmodified_grammar(page) -> None:  # type: ignore[no-untyped-def]
    """The same function the csv path calls, over the html shape, with no adapter in between."""
    resolved = {
        card.detail_id: [parse_entry(line) for line in card.composition] for card in page.cards
    }
    warden = resolved[f"{SLUG}:Glimmerfen-Warden"]
    assert [(entry.model_name, entry.min_count, entry.max_count) for entry in warden] == [
        ("Glimmerfen Warden", 1, 1)
    ]
    skirmishers = resolved[f"{SLUG}:Fenmire-Skirmishers"]
    assert [(entry.model_name, entry.min_count, entry.max_count) for entry in skirmishers] == [
        ("Fenmire Skirmisher", 5, 10),
        ("Fenmire Marshbearer", 1, 1),
    ]


def test_the_non_breaking_hyphen_survives_the_html_shape_too(page) -> None:  # type: ignore[no-untyped-def]
    """The quirk the csv fixture carries at GF03, carried here in the markup instead."""
    outriders = _card(page, "Bracklight-Outriders")
    parsed = parse_entry(outriders.composition[0])
    assert parsed is not None
    assert (parsed.model_name, parsed.min_count, parsed.max_count) == ("Bracklight Outrider", 3, 6)


def test_the_status_keywords_printed_beside_a_composition_line_are_not_part_of_the_name(
    page,  # type: ignore[no-untyped-def]
) -> None:
    """``1 <model> – EPIC HERO`` names one model, not one called ``<model> – EPIC``."""
    warden = _card(page, "Glimmerfen-Warden")
    assert warden.composition == ("1 Glimmerfen Warden",)


def test_a_composition_line_the_grammar_refuses_is_still_carried(page) -> None:  # type: ignore[no-untyped-def]
    """The residual is the caller's business (``CMP-UNRESOLVED``), not the extractor's."""
    tanglers = _card(page, "Mirefen-Tanglers")
    assert tanglers.composition
    assert parse_entry(tanglers.composition[0]) is None


def test_the_model_link_is_made_on_the_html_shape_exactly_as_on_the_csv_shape(page) -> None:  # type: ignore[no-untyped-def]
    chorus = _card(page, "Thornlight-Chorus")
    model_lines = {model.line: model.name for model in chorus.models}
    parsed = [parse_entry(line) for line in chorus.composition]
    # "Thornlight Chorister" is a prefix of "Thornlight Chorister Prime", so the Prime line
    # matches two model rows and is correctly refused — the same case the csv fixture pins.
    assert link_model_line(parsed[0].model_name, model_lines) is None
    assert link_model_line(parsed[1].model_name, model_lines) == 2


def test_every_option_row_reaches_the_unmodified_grammar_with_its_sub_list_intact(page) -> None:  # type: ignore[no-untyped-def]
    conclave = _card(page, "Sedgeward-Conclave")
    stem, items = split_sublist(conclave.options[0])
    assert len(items) == 3, "the nested <li> alternatives must survive extraction as markup"

    parsed = parse_row(conclave.options[0])
    assert parsed is not None
    # The grammar's own reading, unchanged: the leading integer becomes `count`, not part of the
    # name, and the explicit "no change" alternative keeps its fixed label.
    assert choice_names(parsed) == ["sedge halberd", "mire censer", "No change"]
    assert [choice.count for choice in parsed.choices] == [1, 1, None]
    assert stem


@pytest.mark.parametrize(
    ("anchor", "expected_scope"),
    [
        ("Glimmerfen-Warden", "model"),
        ("Fenmire-Skirmishers", "unit"),
        ("Bracklight-Outriders", "per_n_models"),
    ],
)
def test_each_option_scope_resolves_from_the_html_shape(page, anchor, expected_scope) -> None:  # type: ignore[no-untyped-def]
    parsed = parse_row(_card(page, anchor).options[0])
    assert parsed is not None
    assert parsed.scope.value == expected_scope


def test_an_option_row_the_grammar_refuses_is_still_carried(page) -> None:  # type: ignore[no-untyped-def]
    tanglers = _card(page, "Mirefen-Tanglers")
    assert tanglers.options
    assert parse_row(tanglers.options[0]) is None


# -- the rest of the card ----------------------------------------------------------------------


def test_a_multi_profile_card_yields_one_model_line_per_profile(page) -> None:  # type: ignore[no-untyped-def]
    skirmishers = _card(page, "Fenmire-Skirmishers")
    assert [(model.line, model.name) for model in skirmishers.models] == [
        (1, "Fenmire Skirmisher"),
        (2, "Fenmire Marshbearer"),
    ]
    assert len(skirmishers.models[0].characteristics) == len(CHARACTERISTIC_NAMES)


def test_a_single_profile_card_takes_its_model_name_from_the_datasheet(page) -> None:  # type: ignore[no-untyped-def]
    warden = _card(page, "Glimmerfen-Warden")
    assert [model.name for model in warden.models] == ["Glimmerfen Warden"]
    assert warden.models[0].invuln_save == "4+"
    assert warden.models[0].base_size == "(⌀32mm)"


def test_weapon_profiles_take_their_section_from_the_header_that_introduces_them(page) -> None:  # type: ignore[no-untyped-def]
    skirmishers = _card(page, "Fenmire-Skirmishers")
    assert [(weapon.name, weapon.is_melee) for weapon in skirmishers.weapons] == [
        ("Marsh carbine", False),
        ("Fen blade", True),
    ]


def test_a_weapons_own_ability_keywords_are_not_part_of_its_name(page) -> None:  # type: ignore[no-untyped-def]
    warden = _card(page, "Glimmerfen-Warden")
    assert [weapon.name for weapon in warden.weapons] == ["Glimmer lantern"]


def test_only_the_first_cost_tier_is_read(page) -> None:  # type: ignore[no-untyped-def]
    """Both tiers are keyed by model count, so reading the second would overwrite the base."""
    skirmishers = _card(page, "Fenmire-Skirmishers")
    assert skirmishers.costs == (("6 models", "65"), ("11 models", "130"))


def test_the_legends_marker_is_read_from_the_cards_own_class(page) -> None:  # type: ignore[no-untyped-def]
    assert [card.detail_id for card in page.cards if card.is_legends] == [
        f"{SLUG}:Mirefen-Tanglers"
    ]


def test_the_damaged_bracket_is_read_from_the_label_that_embeds_it(page) -> None:  # type: ignore[no-untyped-def]
    assert _card(page, "Mirefen-Tanglers").damaged_wounds == "1-3"


def test_abilities_carry_their_type_and_their_shared_ability_id(page) -> None:  # type: ignore[no-untyped-def]
    warden = _card(page, "Glimmerfen-Warden")
    assert [(a.name, a.ability_type, bool(a.ability_id)) for a in warden.abilities] == [
        ("Deep Strike", "Core", True),
        ("Ember Shield", "Datasheet", False),
    ]
    conclave = _card(page, "Sedgeward-Conclave")
    assert ("Mire Censer", "Wargear") in [(a.name, a.ability_type) for a in conclave.abilities]


def test_two_abilities_printed_in_one_element_are_two_abilities(page) -> None:  # type: ignore[no-untyped-def]
    outriders = _card(page, "Bracklight-Outriders")
    assert [a.name for a in outriders.abilities] == ["Tanglecharge", "Fenrunner"]
    assert all(a.description for a in outriders.abilities)


def test_a_shared_abilitys_mechanic_is_read_without_its_flavour(page) -> None:  # type: ignore[no-untyped-def]
    name, mechanic = page.ability_texts["00001"]
    assert name == "Deep Strike"
    assert "flavour" not in mechanic, "the abLegend paragraph is not a mechanic and is dropped"
    assert "24.01" not in mechanic


def test_leader_pairings_are_read_from_the_pages_own_links(page) -> None:  # type: ignore[no-untyped-def]
    warden = _card(page, "Glimmerfen-Warden")
    skirmishers = _card(page, "Fenmire-Skirmishers")
    assert warden.leads == (skirmishers.detail_id,)
    assert skirmishers.led_by == (warden.detail_id,)


# -- detachment rules: the source data US4's denominator was missing --------------------------


def test_the_detachment_roster_is_read_from_the_pages_own_filter(page) -> None:  # type: ignore[no-untyped-def]
    assert [(d.code, d.name) for d in page.detachments] == [
        ("TC", "Thornlight Chorus"),
        ("BH", "Bracklight Host"),
    ]


def test_each_detachment_rule_is_attached_to_the_detachment_that_owns_it(page) -> None:  # type: ignore[no-untyped-def]
    """The faction-wide class tokens on the same element must not attach a rule to a detachment
    that does not exist — only tokens resolving against the roster are read."""
    warden = _card(page, "Glimmerfen-Warden")
    assert warden.detachment_rules == (
        ("TC", "Chorus Resonance"),
        ("BH", "Bracklight Advance"),
    )


def test_the_emitted_detachment_tables_are_what_the_curate_stage_joins_on(page) -> None:  # type: ignore[no-untyped-def]
    tables = emit_records([page], edition_code="wh40k-11e")
    detachments = {row.fields["id"]: row.fields["name"] for row in tables["Detachments.csv"].rows}
    rules = [
        (row.fields["detachment_id"], row.fields["name"])
        for row in tables["Detachment_abilities.csv"].rows
    ]
    assert detachments == {"TC": "Thornlight Chorus", "BH": "Bracklight Host"}
    # De-duplicated across the cards that each print the same rule.
    assert sorted(rules) == [("BH", "Bracklight Advance"), ("TC", "Chorus Resonance")]


# -- the emitted tables ------------------------------------------------------------------------


def test_the_reader_returns_the_export_shaped_mapping() -> None:
    records = read_datacard_payloads(
        [FixturePayload(name=SLUG, text=FIXTURE.read_text(encoding="utf-8"))],
        edition_code="wh40k-11e",
    )
    composition = records["Datasheets_unit_composition.csv"]
    assert composition.field_names == ("datasheet_id", "line", "description")
    assert {row.fields["datasheet_id"] for row in composition.rows} == {
        f"{SLUG}:{anchor}" for anchor in CSV_ID_TO_ANCHOR.values()
    }
    # The reader raises no data-quality findings of its own: there is no record repair to do in
    # a DOM, which is the one shape difference between the two modes that is visible below them.
    assert all(not result.findings for result in records.values())


def test_a_legends_datasheet_is_carried_by_the_source_id_join(page) -> None:  # type: ignore[no-untyped-def]
    tables = emit_records([page], edition_code="wh40k-11e")
    legends_ids = {
        row.fields["id"]
        for row in tables["Source.csv"].rows
        if "legends" in f"{row.fields['name']} {row.fields['type']}".casefold()
    }
    marked = {
        row.fields["id"]
        for row in tables["Datasheets.csv"].rows
        if row.fields["source_id"] in legends_ids
    }
    assert marked == {f"{SLUG}:Mirefen-Tanglers"}
