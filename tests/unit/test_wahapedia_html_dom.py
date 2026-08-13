# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the datacard DOM extraction (004 task
# T073): label-anchored block identity, the homoglyph-folded column read, the separately-labelled
# keyword split, and — the point of the whole design — that the extracted composition and option
# lists feed pipeline.parse.composition_grammar and pipeline.parse.options_grammar UNMODIFIED
# (risk R-A, research D1c-D1d, docs/verification/html-markup-spike.md).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the repeated-cost-header case, the other
# half of the tier rule, against the trap now reproduced on the Thornlight-Chorus fixture card.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the weapon-ability-keyword cases (issue
# #4): the keywords the name extractor removes are now read rather than discarded, including the
# adjacent-element split and the parameterised forms, and they leave html mode in the export's
# own `description` column.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the colliding-`data-det-code` cases
# (issue #5): two invented factions publishing the same two-letter code must emit two
# detachments and keep each one's rules on its own page.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the colliding-tooltip-id cases
# (issue #6): the same shape one layer over, on the ids the ability digest join resolves.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the army-rule tooltip template cases
# (issue #7): the div.tooltip_header family an ordinary ability's div.abName reader emitted
# nothing for, including the owner line, the embedded ability card and the digest-join guard.
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
from pipeline.normalize.weapon_abilities import parse_weapon_ability_keywords
from pipeline.parse.composition_grammar import link_model_line, parse_entry
from pipeline.parse.options_grammar import choice_names, parse_row, split_sublist
from pipeline.parse.wahapedia_html_dom import (
    CHARACTERISTIC_NAMES,
    AbilityReference,
    Datacard,
    DatacardPage,
    Detachment,
    HtmlStructureError,
    blocks_of,
    detail_id,
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
    # 006 T003/T004's quirk-class carriers. GF07 holds one invented row per research D1b class
    # plus the Purgation-Squad shape; GF08-GF11 hold the four default-equipment shapes research
    # D1e measured — differentiated model groups, one sentence over two composition rows, no
    # sentence at all, and a datasheet whose composition itself does not resolve.
    "GF07": "Purgeflight-Wardens",
    "GF08": "Mirebound-Choir",
    "GF09": "Fenwatch-Sentinel",
    "GF10": "Gloamtide-Host",
    "GF11": "Snarebound-Wretches",
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


def test_a_comma_appended_conditional_keyword_is_its_own_keyword(page) -> None:  # type: ignore[no-untyped-def]
    """The `;` is not the only separator a keyword column prints (006 T049).

    A detachment-conditional faction keyword is appended after a `, ` carried in its own
    ``span.clFl``, so a column that lists two of them yields two keywords. Reading the cell whole
    yields one keyword nobody can filter on: a consumer asking for either exact name finds
    nothing, which is what 356 rows of the 2026-08-2 candidate did.
    """
    host = _card(page, "Gloamtide-Host")
    assert [keyword for keyword, _scope, is_faction in host.keywords if is_faction] == [
        "GLIMMERFEN COVENANT",
        "THORNLIGHT CHORUS",
    ]


def test_a_keyword_whose_own_name_contains_a_comma_is_not_split_on_it(page) -> None:  # type: ignore[no-untyped-def]
    """The other half of the case above, and the reason the fix is not a string split.

    The separator is the text printed *between* two ``span.kwb`` runs, so punctuation inside one
    of them is part of the name. Splitting the flattened cell on `,` would turn this one keyword
    into two that the page never printed.
    """
    wretches = _card(page, "Snarebound-Wretches")
    assert [keyword for keyword, _scope, is_faction in wretches.keywords if not is_faction] == [
        "INFANTRY",
        "SNAREBOUND, UNBOWED",
    ]


def test_a_conditional_group_introduced_by_a_printed_colon_is_split_too(page) -> None:  # type: ignore[no-untyped-def]
    """The third separator: a `:` printed after a model-scoped list, introducing a conditional.

    The scope survives it — the whole group is still the one the ``dsVertLine`` opened — so the
    conditional keyword is attributed to the same models the list before it names.
    """
    sentinel = _card(page, "Fenwatch-Sentinel")
    assert sentinel.keywords == (
        ("VEHICLE", "ALL MODELS", False),
        ("CHARACTER", "SENTINEL PILOT ONLY", False),
        ("GRENADES", "SENTINEL PILOT ONLY", False),
        ("GLIMMERFEN COVENANT", "", True),
    )


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


# -- the two shapes that are not option rows at all (006 T022) ---------------------------------
#
# Research D1c.4 diagnosed both as defects in this extractor rather than gaps in the grammar: 30
# measured rows, 5.3% of the unparsed residual, fixed where the mistake is made. A grammar taught
# to recognise and discard them would instead be a grammar that tolerates being handed anything.


def test_a_default_equipment_sentence_is_not_an_option_row(page) -> None:  # type: ignore[no-untyped-def]
    # 22 measured rows: a named model's fixed loadout, printed inside the options list. It
    # offers no choice, so reporting it as an unresolved option sizes a production against a
    # layout quirk.
    wardens = _card(page, "Purgeflight-Wardens")
    assert not [row for row in wardens.options if "is equipped with:" in row]
    # ...and the rows around it are untouched, which is the half that makes the drop safe.
    assert any("can be equipped with" in row for row in wardens.options)


def test_the_none_placeholder_is_dropped_with_its_full_stop_too(page) -> None:  # type: ignore[no-untyped-def]
    # 8 measured rows. The extractor already dropped `None`; the variant carrying the
    # publisher's full stop fell through an exact-string comparison and shipped as an option row
    # that says nothing.
    choir = _card(page, "Mirebound-Choir")
    assert choir.options
    assert not [row for row in choir.options if row.strip().rstrip(".").casefold() == "none"]


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


def test_a_weapons_ability_keywords_are_read_rather_than_discarded(page) -> None:  # type: ignore[no-untyped-def]
    """Issue #4: the keywords removed from the name have to *go* somewhere.

    Three shapes in one cell, because the card prints all three: a keyword in a single element,
    a keyword whose words are split across adjacent elements (they are line-break opportunities,
    not tokens — concatenating them would yield ``marshbind2``), and a target-parameterised one.
    """
    warden = _card(page, "Glimmerfen-Warden")

    assert warden.weapons[0].ability_keywords == ("blast", "marshbind 2", "fenlock 4+")


def test_each_sibling_keyword_element_is_its_own_keyword(page) -> None:  # type: ignore[no-untyped-def]
    """Nothing is printed between two keywords, so the element boundary is the separator."""
    warden = _card(page, "Glimmerfen-Warden")

    assert len(warden.weapons[0].ability_keywords) == 3


def test_a_section_whose_header_shares_a_tbody_with_its_rows_still_yields_them(page) -> None:  # type: ignore[no-untyped-def]
    """The shape that silently dropped 19% of live weapon rows, almost all of them melee.

    The page groups a section's header and its rows into one ``tbody`` on some cards and into
    separate ones on others — both shapes appear on the same page. Treating "this group has a
    header" as "this group has no rows" discarded every weapon printed beneath such a header.
    """
    conclave = _card(page, "Sedgeward-Conclave")

    assert [(w.name, w.is_melee) for w in conclave.weapons] == [
        ("Sedge halberd", True),
        ("Mire censer", True),
    ]
    assert conclave.weapons[0].ability_keywords == ("bracklight bound",)


def test_a_weapon_the_card_prints_no_keyword_for_carries_none(page) -> None:  # type: ignore[no-untyped-def]
    skirmishers = _card(page, "Fenmire-Skirmishers")

    assert [weapon.ability_keywords for weapon in skirmishers.weapons] == [(), ()]


def test_the_emitted_wargear_table_carries_the_keywords_in_the_exports_own_field(page) -> None:  # type: ignore[no-untyped-def]
    """Mode-blindness: the keywords leave html mode in the column the csv export puts them in.

    Asserted through :func:`pipeline.normalize.weapon_abilities.parse_weapon_ability_keywords`
    — the reader ``pipeline.curate.assemble`` uses — rather than against a literal string, so
    the test states the property the two modes share instead of one mode's formatting.
    """
    tables = emit_records([page])
    rows = {
        (row.fields["datasheet_id"], row.fields["line"]): row
        for row in tables["Datasheets_wargear.csv"].rows
    }
    warden = rows[(f"{SLUG}:Glimmerfen-Warden", "1")]
    carbine = rows[(f"{SLUG}:Fenmire-Skirmishers", "1")]

    assert "description" in tables["Datasheets_wargear.csv"].field_names
    assert parse_weapon_ability_keywords(warden.fields["description"]) == (
        "blast",
        "marshbind 2",
        "fenlock 4+",
    )
    assert parse_weapon_ability_keywords(carbine.fields["description"]) == ()


def test_only_the_first_cost_tier_is_read(page) -> None:  # type: ignore[no-untyped-def]
    """Both tiers are keyed by model count, so reading the second would overwrite the base."""
    skirmishers = _card(page, "Fenmire-Skirmishers")
    assert skirmishers.costs == (("6 models", "65"), ("11 models", "130"))


def test_a_repeated_cost_header_before_any_price_is_the_same_heading(page) -> None:  # type: ignore[no-untyped-def]
    """The other half of the tier rule, and the half that cost 160 live datasheets their price.

    A tier boundary is a header row that follows a *cost* row. A header row that follows another
    header row, with nothing priced in between, is the same heading printed twice — and ending
    the read there yields no cost at all, which is the blocking ``REC-NEVER-PRICED`` rather than
    a merely wrong number.
    """
    chorus = _card(page, "Thornlight-Chorus")
    assert chorus.costs == (("4 models", "55"),)


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
    assert detachments == {
        f"{SLUG}:TC": "Thornlight Chorus",
        f"{SLUG}:BH": "Bracklight Host",
    }
    # De-duplicated across the cards that each print the same rule.
    assert sorted(rules) == [
        (f"{SLUG}:BH", "Bracklight Advance"),
        (f"{SLUG}:TC", "Chorus Resonance"),
    ]


# -- issue #5: `data-det-code` is unique on its page and nowhere else -------------------------


def _synthetic_page(slug: str, code: str, detachment: str, rule: str) -> DatacardPage:
    """One invented faction publishing one invented detachment and one invented rule.

    Built from the module's own dataclasses rather than from markup: what is under test is the
    identity the emission mints, and a second html fixture would say nothing more about it.
    """
    return DatacardPage(
        faction_slug=slug,
        faction_name=slug,
        detachments=(Detachment(code=code, name=detachment),),
        cards=(
            Datacard(
                detail_id=detail_id(slug, "Invented-Card"),
                name="Invented Card",
                faction_id=slug,
                detachment_rules=((code, rule),),
            ),
        ),
    )


def test_two_factions_publishing_the_same_det_code_get_two_detachments() -> None:
    """71 of the 208 codes on the 2026-08-05 live sweep were published by more than one faction.

    A bare code therefore names a *page position*, not a detachment, and emitting it as the id
    made the curate stage's ``id -> name`` map one entry per code across every page read.
    """
    tables = emit_records(
        [
            _synthetic_page("ashenreach", "SC", "Sable Cohort", "Sable Advance"),
            _synthetic_page("thornmoor", "SC", "Sedge Column", "Sedge Volley"),
        ],
        edition_code="wh40k-11e",
    )

    detachments = {row.fields["id"]: row.fields["name"] for row in tables["Detachments.csv"].rows}
    assert detachments == {
        "ashenreach:SC": "Sable Cohort",
        "thornmoor:SC": "Sedge Column",
    }


def test_a_rule_is_emitted_against_the_detachment_on_its_own_page() -> None:
    """The failure this replaces: the last page read took every colliding code's rules."""
    tables = emit_records(
        [
            _synthetic_page("ashenreach", "SC", "Sable Cohort", "Sable Advance"),
            _synthetic_page("thornmoor", "SC", "Sedge Column", "Sedge Volley"),
        ],
        edition_code="wh40k-11e",
    )

    rules = tables["Detachment_abilities.csv"].rows
    assert {(row.fields["detachment_id"], row.fields["name"]) for row in rules} == {
        ("ashenreach:SC", "Sable Advance"),
        ("thornmoor:SC", "Sedge Volley"),
    }
    # And the rule rows' own ids stay distinct, so neither overwrites the other downstream.
    assert len({row.fields["id"] for row in rules}) == 2


# -- issue #6: nor is a tooltip id ------------------------------------------------------------


def _ability_page(slug: str, tooltip: str, name: str, mechanic: str) -> DatacardPage:
    """One invented faction whose one card refers to one invented shared ability."""
    return DatacardPage(
        faction_slug=slug,
        faction_name=slug,
        cards=(
            Datacard(
                detail_id=detail_id(slug, "Invented-Card"),
                name="Invented Card",
                faction_id=slug,
                abilities=(
                    AbilityReference(name=name, ability_type="Faction", ability_id=tooltip),
                ),
            ),
        ),
        ability_texts={tooltip: (name, mechanic)},
    )


def test_two_factions_sharing_a_tooltip_id_get_two_abilities() -> None:
    """569 of the 1 169 tooltip ids on the 2026-08-05 sweep were on more than one page, and 350
    of those named a different thing on each — the ids are assigned per page, from 1."""
    tables = emit_records(
        [
            _ability_page("ashenreach", "00003", "Sable Resolve", "Invented mechanic one."),
            _ability_page("thornmoor", "00003", "Sedge Cunning", "Invented mechanic two."),
        ],
        edition_code="wh40k-11e",
    )

    assert {row.fields["id"]: row.fields["name"] for row in tables["Abilities.csv"].rows} == {
        "ashenreach:00003": "Sable Resolve",
        "thornmoor:00003": "Sedge Cunning",
    }


def test_a_binding_names_the_ability_tooltip_on_its_own_page() -> None:
    """The digest join resolves ``ability_id`` against ``Abilities.csv``; a bare id let the first
    page read answer for every other page's ability of the same number."""
    tables = emit_records(
        [
            _ability_page("ashenreach", "00003", "Sable Resolve", "Invented mechanic one."),
            _ability_page("thornmoor", "00003", "Sedge Cunning", "Invented mechanic two."),
        ],
        edition_code="wh40k-11e",
    )
    texts = {row.fields["id"]: row.fields["description"] for row in tables["Abilities.csv"].rows}

    for row in tables["Datasheets_abilities.csv"].rows:
        slug = row.fields["datasheet_id"].split(":")[0]
        assert row.fields["ability_id"] == f"{slug}:00003"
        assert texts[row.fields["ability_id"]].endswith("one." if slug == "ashenreach" else "two.")


def test_a_card_that_prints_its_own_ability_names_no_tooltip() -> None:
    """An empty id must stay empty rather than become a bare faction slug that resolves to
    whatever ``Abilities.csv`` row happens to carry an empty-suffixed id."""
    page = DatacardPage(
        faction_slug="ashenreach",
        faction_name="ashenreach",
        cards=(
            Datacard(
                detail_id=detail_id("ashenreach", "Invented-Card"),
                name="Invented Card",
                faction_id="ashenreach",
                abilities=(
                    AbilityReference(
                        name="Printed In Full",
                        ability_type="Other",
                        description="Invented mechanic printed on the card itself.",
                    ),
                ),
            ),
        ),
    )

    tables = emit_records([page], edition_code="wh40k-11e")

    assert [row.fields["ability_id"] for row in tables["Datasheets_abilities.csv"].rows] == [""]


# -- issue #7: an army rule's tooltip is not shaped like an ability's -------------------------


def test_a_faction_army_rules_tooltip_is_read_from_its_own_heading(page) -> None:  # type: ignore[no-untyped-def]
    """The whole of issue #7: a faction army rule is published in the *other* tooltip template.

    ``_ability_texts`` emitted a row only for a tooltip carrying ``div.abName``, so a rule headed
    by ``div.tooltip_header`` produced no ``Abilities.csv`` row at all, the digest join fell
    through to the empty string, and every faction's army rule was exempt from FR-024 change
    detection — 38 keys on the 2026-08-05 live sweep, essentially one per faction.
    """
    name, mechanic = page.ability_texts["00002"]

    assert name == "Mirelight Vigil"
    assert mechanic, "the rule's mechanic is what the digest is taken over"
    assert "flavour" not in mechanic, "the ShowFluff paragraph is not a mechanic and is dropped"
    assert name not in mechanic, "the heading is the name, not part of the mechanic"


def test_the_rule_tooltips_owner_line_is_not_part_of_its_mechanic(page) -> None:  # type: ignore[no-untyped-def]
    """``div.detachName`` states which detachment publishes the rule — an attribution, not a
    mechanic, and a rule reattached upstream must not read as a rule that changed."""
    name, mechanic = page.ability_texts["00003"]

    assert name == "Fenwatch Litany"
    assert "Thornlight Chorus" not in mechanic
    assert "flavour" not in mechanic
    assert "ignore one point of Damage" in mechanic


def test_a_rule_tooltip_that_embeds_an_ability_card_is_named_by_the_rule(page) -> None:  # type: ignore[no-untyped-def]
    """Both headings occur in one tooltip on four of the live sweep's referenced ids.

    The outer ``div.tooltip_header`` is the tooltip's own title and the inner ``div.abName`` is a
    card printed *inside* the rule, so the heading nearest the tooltip wins — reading the inner
    one named the rule after the ability it grants.
    """
    name, mechanic = page.ability_texts["00004"]

    assert name == "Gloamtide Surge"
    assert "Gloamtide Bearer" in mechanic, "the embedded card is body text of the rule"
    assert "flavour" not in mechanic, "including the embedded card's own flavour paragraph"


def test_the_rule_body_is_read_despite_the_upstream_mis_nesting(page) -> None:  # type: ignore[no-untyped-def]
    """The templates put a ``<p>`` directly inside a ``<span>``, which is why an earlier DOM
    attempt read nothing. The fixture reproduces it rather than tidying it away."""
    markup = FIXTURE.read_text(encoding="utf-8")
    opened = markup.index('<span id="tooltip_content00002">')
    assert markup[opened:].index("<p class=") < markup[opened:].index("</span>")

    assert "re-roll Battle-shock tests" in page.ability_texts["00002"][1]


def test_every_referenced_ability_reaches_the_digest_join_with_text(page) -> None:  # type: ignore[no-untyped-def]
    """The regression guard in the join's own terms (`compute_current_digests`).

    A binding that names a tooltip and resolves to no ``Abilities.csv`` row digests over ``""``,
    and every key that does shares one digest value — so ``effective_status`` can never move any
    of them to ``needs_rereview``. The failure is silent in every other assertion here.
    """
    tables = emit_records([page], edition_code="wh40k-11e")
    texts = {row.fields["id"]: row.fields["description"] for row in tables["Abilities.csv"].rows}

    named = [
        row.fields["ability_id"]
        for row in tables["Datasheets_abilities.csv"].rows
        if row.fields["ability_id"]
    ]
    assert named, "the fixture's cards refer to shared abilities"
    assert all(texts.get(identifier, "").strip() for identifier in named)


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
