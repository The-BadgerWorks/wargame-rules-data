# AI-Assisted: Claude Code (model: claude-sonnet-5) - Failing-first tests for 010 round 1: the csv
# reader drops the two non-option row shapes the html extractor already dropped, and derives
# default equipment rows from the Datasheets export's loadout column. All fixture text is invented.
"""``read_export_payloads`` reaches parity with the html arm's row routing (010 R1)."""

from __future__ import annotations

from pipeline.acquire.detail_source import read_export_payloads
from pipeline.acquire.fixtures import FixturePayload
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE, parse_sentence

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
        "Every model is equipped with: glow lantern; tide axe. "
        "The Marshguard Leader is equipped with: fen pike."
    )
    rows = _equipment_rows({"CM03": cell})
    assert [line for line, _ in rows["CM03"]] == ["1", "2"]
    assert rows["CM03"][1][1] == "The Marshguard Leader is equipped with: fen pike."


def test_sentences_separated_by_a_line_break_tag_are_split_too() -> None:
    cell = "Every model is equipped with: glow lantern.<br>The Leader is equipped with: fen pike."
    rows = _equipment_rows({"CM03": cell})
    assert len(rows["CM03"]) == 2


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


def test_an_internal_period_inside_one_sentence_does_not_truncate_it() -> None:
    """Fix-round F1: a mid-sentence 'X. Y' period must not be read as a sentence end."""
    rows = _equipment_rows({"CM03": "Every model is equipped with: Mk. II blade."})
    assert len(rows["CM03"]) == 1
    assert "II blade." in rows["CM03"][0][1]
    assert rows["CM03"][0][1] == "Every model is equipped with: Mk. II blade."


def test_a_marker_less_leading_clause_never_merges_forward_onto_the_following_sentence() -> None:
    """General merge-direction guard, independent of any Finding-1 fix: a leading marker-less
    clause must be dropped, never merged FORWARD onto the marker sentence after it. Renamed (was
    ``..._is_discarded_leaving_one_row``) and strengthened per fix-round-2 review: the old name
    read as evidence the Finding-1 fix worked, but pre-fix code already produced this exact
    one-row outcome here, so it proves nothing about that fix — only about merge direction, which
    this assertion now pins directly rather than leaving implicit in the row count."""
    rows = _equipment_rows({"CM03": "Some intro text. Every model is equipped with: fen pike."})
    assert len(rows["CM03"]) == 1
    description = rows["CM03"][0][1]
    assert description == "Every model is equipped with: fen pike."
    assert "intro" not in description.casefold(), "the leading clause merged forward"


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


def test_a_line_break_immediately_after_a_period_opens_the_next_row_intact() -> None:
    """A ``<br>`` sitting directly against a full stop, with the next segment opening on an
    abbreviation-style full stop, must split on the ``<br>`` and start row 2 at the segment's own
    first character — the line-break tag may never be read as part of the word ending row 1's
    sentence, and no tag text may reach either row. (Replaces the fix-round-2 assertions, which
    pinned the removed fold's output.)"""
    cell = (
        "Every model is equipped with: glow lantern.<br>Mk. II Leader is equipped with: fen pike."
    )
    rows = _equipment_rows({"CM03": cell})
    assert [line for line, _ in rows["CM03"]] == ["1", "2"]
    row_1, row_2 = (description for _, description in rows["CM03"])
    assert row_1 == "Every model is equipped with: glow lantern."
    assert row_2 == "Mk. II Leader is equipped with: fen pike."
    assert "<br" not in row_1 and "<br" not in row_2


def _parsed_item_names(cell: str) -> list[list[str]]:
    """The item names a user would see: every derived row driven through the real grammar entry
    point, ``equipment_grammar.parse_sentence`` — the reader whose output reaches a published
    ``item_name``. Asserting on the split output alone would have missed T1-1 entirely."""
    names: list[list[str]] = []
    for _, description in _equipment_rows({"CM03": cell})["CM03"]:
        parse = parse_sentence(description)
        assert parse is not None, "the derived row no longer parses at all"
        names.append([item.item_name for item in parse.items])
    return names


def test_a_trailing_non_equipment_sentence_never_enters_a_parsed_item_name() -> None:
    """T1-1 receipt. A cell whose loadout sentence is followed by a non-equipment sentence must
    yield ONE row, and the trailing prose must not be absorbed into the last item's name — the
    field that is published. Remove the boundary rule and the trailing clause reappears inside
    ``items[-1].item_name``."""
    cell = "Every model is equipped with: glow lantern. Some trailing note about it in play."
    rows = _equipment_rows({"CM03": cell})
    assert len(rows["CM03"]) == 1
    assert _parsed_item_names(cell) == [["glow lantern"]]


def test_a_pre_marker_lead_in_is_not_deleted() -> None:
    """T1-2 receipt. The subject clause before the marker is what the equipment linker reads to
    decide which model carries the equipment, so a false boundary inside it must never delete
    it."""
    rows = _equipment_rows({"CM03": "A Mk. II Leader is equipped with: fen pike."})
    assert rows["CM03"] == [("1", "A Mk. II Leader is equipped with: fen pike.")]
    two = _equipment_rows(
        {
            "CM03": (
                "The Mk. II Sergeant is equipped with: blade. "
                "Every model is equipped with: lantern."
            )
        }
    )
    assert [description for _, description in two["CM03"]] == [
        "The Mk. II Sergeant is equipped with: blade.",
        "Every model is equipped with: lantern.",
    ]


def test_the_guard_splits_two_sentences_joined_by_a_short_final_item_name() -> None:
    """The boundary rule's own guard. A genuine sentence whose final word is three characters or
    shorter suppresses its boundary, so the two sentences arrive as one segment carrying two
    markers — which is the signal that the suppression was wrong. The segment is split at the
    suppressed boundary after all, so the rule cannot silently merge two real sentences."""
    cell = "Every model is equipped with: axe. Mk. II Leader is equipped with: fen pike."
    rows = _equipment_rows({"CM03": cell})
    assert [description for _, description in rows["CM03"]] == [
        "Every model is equipped with: axe.",
        "Mk. II Leader is equipped with: fen pike.",
    ]
    assert _parsed_item_names(cell) == [["axe"], ["fen pike"]]
