# AI-Assisted: Claude Code (model: claude-haiku-4-5) - Tests for `read_export_payloads` row
# routing. The module verifies: (1) two non-option row shapes are dropped from the options table
# (matching the retired HTML arm's behaviour); (2) default-equipment rows are derived from the
# Datasheets export's loadout column; (3) sentence boundaries are anchored on the export's
# markup—one bold subject per default-loadout sentence; (4) line-break tags are rendered as
# spaces; (5) segments ambiguous after tag-stripping are refused and reported as
# EQP-BOUNDARY-AMBIGUOUS; (6) loadout-derived line numbers start one past the highest
# composition-derived line for that datasheet_id. All fixture text is invented.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 3 task 1: a refused sentence now
# keeps its ordinal as an empty-description row instead of being dropped, so the datasheet
# publishes `partial` (never `extracted` or `none`). Amended the three tests that asserted the
# refused sentence vanished from `split_equipment_sentences`'s output and from the equipment
# table entirely; added coverage for a refused sentence between two resolved ones, and for the
# equipment grammar counting an empty description as unparsed.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 4 task 1: added coverage for the
# export's own footnote marker (`button` `*`) being routed out of the options table alongside the
# two shapes above, and for the one `OPT-FOOTNOTE-ROW` finding per affected datasheet.
"""``read_export_payloads`` reaches parity with the html arm's row routing (010 R1)."""

from __future__ import annotations

from pipeline.acquire.detail_source import read_export_payloads
from pipeline.acquire.export_rows import split_equipment_sentences
from pipeline.acquire.fixtures import FixturePayload
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE

OPTIONS = "Datasheets_options.csv"

_OPTIONS_TEXT = (
    "datasheet_id|line|button|description|\n"
    "CM03|1||None|\n"
    "CM03|2||None.|\n"
    "CM03|3||The Marshguard Leader is equipped with: tide axe.|\n"
    "CM03|4||This model can be equipped with 1 glow lantern.|\n"
    "CM04|1||Any number of models can each have their fen pike replaced with 1 tide axe.|\n"
)


def _options_rows(text: str = _OPTIONS_TEXT) -> dict[str, list[str]]:
    detail = read_export_payloads([FixturePayload(name=OPTIONS, text=text)])
    grouped = detail[OPTIONS].grouped_by("datasheet_id")
    return {ds: [row.fields["line"] for row in rows] for ds, rows in grouped.items()}


def test_the_none_placeholder_row_is_dropped_with_or_without_its_full_stop() -> None:
    assert "1" not in _options_rows()["CM03"]
    assert "2" not in _options_rows()["CM03"]


def test_a_default_equipment_sentence_offering_no_choice_is_dropped() -> None:
    assert "3" not in _options_rows()["CM03"]


def test_a_genuine_option_row_that_mentions_equipment_and_offers_a_choice_survives() -> None:
    assert "4" in _options_rows()["CM03"]


def test_rows_on_an_unaffected_datasheet_are_untouched() -> None:
    assert _options_rows()["CM04"] == ["1"]


def test_the_other_tables_are_not_touched_by_the_options_routing() -> None:
    detail = read_export_payloads(
        [
            FixturePayload(name=OPTIONS, text=_OPTIONS_TEXT),
            FixturePayload(
                name="Datasheets_keywords.csv",
                text="datasheet_id|keyword|is_faction_keyword|model|\nCM03|None|false||\n",
            ),
        ]
    )
    assert len(detail["Datasheets_keywords.csv"].rows) == 1


_FOOTNOTE_TEXT = (
    "datasheet_id|line|button|description|\n"
    "CM03|1|•|This model can be equipped with 1 glow lantern.|\n"
    "CM03|2|*|Invented footnote text about the lantern.|\n"
    "CM04|1|•|Any number of models can each have their fen pike replaced with 1 tide axe.|\n"
)


def test_a_footnote_row_is_routed_out_of_the_options_table() -> None:
    assert _options_rows(_FOOTNOTE_TEXT)["CM03"] == ["1"]


def test_a_bullet_row_survives_footnote_routing() -> None:
    assert _options_rows(_FOOTNOTE_TEXT)["CM04"] == ["1"]


def test_footnote_routing_raises_one_finding_per_datasheet_with_the_row_count() -> None:
    detail = read_export_payloads([FixturePayload(name=OPTIONS, text=_FOOTNOTE_TEXT)])
    findings = detail[OPTIONS].findings  # type: ignore[attr-defined]
    assert [f.finding_code for f in findings] == ["OPT-FOOTNOTE-ROW"]
    assert findings[0].entity_refs == ("CM03",)
    assert findings[0].detail["rows"] == 1


def test_an_empty_or_bullet_button_never_routes_a_row() -> None:
    """The existing fixture has an empty button column on every row; nothing may change."""
    assert _options_rows()["CM04"] == ["1"]


DATASHEETS = "Datasheets.csv"
_DS_HEADER = (
    "id|name|faction_id|source_id|legend|role|loadout|transport|virtual|is_support|"
    "leader_head|leader_footer|damaged_w|damaged_description|link|\n"
)


def _datasheets(loadouts: dict[str, str]) -> str:
    body = "".join(
        f"{ds}|Unit {ds}|FX|1||Battleline|{loadout}||false|false||||||\n"
        for ds, loadout in loadouts.items()
    )
    return _DS_HEADER + body


def _equipment_rows(loadouts: dict[str, str]) -> dict[str, list[tuple[str, str]]]:
    detail = read_export_payloads([FixturePayload(name=DATASHEETS, text=_datasheets(loadouts))])
    if EQUIPMENT_TABLE not in detail:
        return {}
    grouped = detail[EQUIPMENT_TABLE].grouped_by("datasheet_id")
    return {
        ds: [(row.fields["line"], row.fields["description"]) for row in rows]
        for ds, rows in grouped.items()
    }


def test_a_single_loadout_sentence_becomes_one_equipment_row_on_line_1() -> None:
    rows = _equipment_rows({"CM03": "Every model is equipped with: glow lantern; tide axe."})
    assert rows["CM03"] == [("1", "Every model is equipped with: glow lantern; tide axe.")]


def test_two_sentences_in_one_cell_become_two_rows_in_text_order() -> None:
    cell = (
        "<b>Every model</b> is equipped with: glow lantern; tide axe. "
        "<b>The Marshguard Leader</b> is equipped with: fen pike."
    )
    rows = _equipment_rows({"CM03": cell})
    assert [line for line, _ in rows["CM03"]] == ["1", "2"]
    assert rows["CM03"][1][1] == "<b>The Marshguard Leader</b> is equipped with: fen pike."


def test_an_empty_loadout_yields_no_row_and_no_table_when_nothing_else_does() -> None:
    assert _equipment_rows({"CM03": ""}) == {}


def test_a_loadout_without_the_marker_yields_no_row() -> None:
    assert _equipment_rows({"CM03": "Prose that mentions no loadout at all."}) == {}


def test_blanking_every_loadout_removes_every_derived_row() -> None:
    """The receipt: identical counts would mean the reader is not wired into the csv path."""
    populated = _equipment_rows({"CM03": "Every model is equipped with: glow lantern."})
    blanked = _equipment_rows({"CM03": ""})
    assert sum(len(v) for v in populated.values()) > sum(len(v) for v in blanked.values()), (
        "blanking the loadout column changed nothing: derive_equipment_from_loadout is not wired"
    )


def test_loadout_rows_append_to_composition_derived_rows_rather_than_replacing_them() -> None:
    detail = read_export_payloads(
        [
            FixturePayload(
                name=DATASHEETS,
                text=_datasheets({"CM05": "This model is equipped with: tide axe."}),
            ),
            FixturePayload(
                name="Datasheets_unit_composition.csv",
                text=(
                    "datasheet_id|line|description|\n"
                    "CM03|2|Every model in this unit is equipped with: glow lantern.|\n"
                ),
            ),
        ]
    )
    ids = {row.fields["datasheet_id"] for row in detail[EQUIPMENT_TABLE].rows}
    assert ids == {"CM03", "CM05"}


def test_a_composition_and_loadout_derived_row_on_the_same_datasheet_get_distinct_lines() -> None:
    """Fix-round F2 receipt: equal line values on the same datasheet_id would collide the
    equipment group id curate/assemble.py mints from (datasheet_id, line)."""
    detail = read_export_payloads(
        [
            FixturePayload(
                name=DATASHEETS,
                text=_datasheets({"CM03": "This model is equipped with: tide axe."}),
            ),
            FixturePayload(
                name="Datasheets_unit_composition.csv",
                text=(
                    "datasheet_id|line|description|\n"
                    "CM03|1|Every model in this unit is equipped with: glow lantern.|\n"
                ),
            ),
        ]
    )
    lines = [
        row.fields["line"]
        for row in detail[EQUIPMENT_TABLE].rows
        if row.fields["datasheet_id"] == "CM03"
    ]
    assert len(lines) == 2
    assert len(set(lines)) == 2, "equal line values collide the equipment group id"


def test_one_bold_subject_per_sentence_splits_on_the_bold_tag() -> None:
    cell = (
        "<b>Every model</b> is equipped with: glow lantern. "
        "<b>The Leader</b> is equipped with: fen pike."
    )
    assert split_equipment_sentences(cell) == (
        "<b>Every model</b> is equipped with: glow lantern.",
        "<b>The Leader</b> is equipped with: fen pike.",
    )


def test_a_line_break_inside_one_sentence_keeps_the_text_after_it() -> None:
    cell = "<b>Every model</b> is equipped with: glow lantern,<br>fen pike."
    (sentence,) = split_equipment_sentences(cell)
    assert "fen pike" in sentence
    assert "<br>" not in sentence


def test_a_line_break_between_two_sentences_is_not_needed_to_split_them() -> None:
    cell = (
        "<b>Every model</b> is equipped with: glow lantern."
        "<br><b>The Leader</b> is equipped with: fen pike."
    )
    assert len(split_equipment_sentences(cell)) == 2


def test_an_abbreviation_style_full_stop_inside_an_item_name_is_refused_never_truncated() -> None:
    """After tag stripping, an abbreviation and a trailing sentence are the same shape. The rule
    refuses both (visible, curator-resolvable) rather than cutting the item name (silent, wrong)."""
    cell = "<b>Every model</b> is equipped with: Mk. II glow lantern; tide axe."
    assert split_equipment_sentences(cell) == ("",)


def test_a_lead_in_before_the_first_bold_subject_is_dropped_not_folded() -> None:
    cell = "Some invented lead-in prose. <b>Every model</b> is equipped with: glow lantern."
    assert split_equipment_sentences(cell) == (
        "<b>Every model</b> is equipped with: glow lantern.",
    )


def test_a_trailing_sentence_with_its_own_bold_subject_is_dropped_not_folded() -> None:
    cell = (
        "<b>Every model</b> is equipped with: glow lantern. "
        "<b>Note</b> some invented trailing prose."
    )
    assert split_equipment_sentences(cell) == (
        "<b>Every model</b> is equipped with: glow lantern.",
    )


def test_a_mid_sentence_bold_on_an_item_is_rejoined_to_its_sentence() -> None:
    cell = "<b>Every model</b> is equipped with: glow lantern; <b>tide axe</b>; fen pike."
    (sentence,) = split_equipment_sentences(cell)
    assert sentence.endswith("<b>tide axe</b>; fen pike.")


def test_a_sentence_with_untagged_trailing_prose_is_refused_not_guessed() -> None:
    """Three or more words after an internal full stop: could be prose (must not enter an item
    name) or an abbreviation (must not be cut). Neither is guessed; the row is refused."""
    cell = "<b>Every model</b> is equipped with: glow lantern. Some invented trailing prose here."
    assert split_equipment_sentences(cell) == ("",)


def test_a_refused_sentence_raises_the_boundary_finding_on_the_equipment_table() -> None:
    cell = "<b>Every model</b> is equipped with: glow lantern. Some invented trailing prose here."
    detail = read_export_payloads(
        [FixturePayload(name=DATASHEETS, text=_datasheets({"CM03": cell}))]
    )
    findings = detail[EQUIPMENT_TABLE].findings  # type: ignore[attr-defined]
    assert [f.finding_code for f in findings] == ["EQP-BOUNDARY-AMBIGUOUS"]
    assert findings[0].entity_refs == ("CM03",)
    rows = [r for r in detail[EQUIPMENT_TABLE].rows if r.fields["datasheet_id"] == "CM03"]  # type: ignore[attr-defined]
    assert len(rows) == 1
    fields = rows[0].fields
    assert fields["line"] == "1"
    assert fields["description"] == ""


def test_a_refused_second_sentence_keeps_the_third_sentence_on_line_3() -> None:
    cell = (
        "<b>Every model</b> is equipped with: glow lantern. "
        "<b>The Leader</b> is equipped with: fen pike. Some invented trailing prose here. "
        "<b>The Herald</b> is equipped with: tide axe."
    )
    rows = _equipment_rows({"CM03": cell})["CM03"]
    assert [line for line, _ in rows] == ["1", "2", "3"]
    assert rows[1][1] == ""
    assert rows[2][1].endswith("tide axe.")


def test_a_refused_row_is_counted_by_the_equipment_grammar_as_unparsed() -> None:
    from pipeline.parse.equipment_grammar import parse_sentence

    assert parse_sentence("") is None
