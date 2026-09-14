# AI-Assisted: Claude Code (model: claude-sonnet-5) - Failing-first tests for 010 round 1: the csv
# reader drops the two non-option row shapes the html extractor already dropped, and derives
# default equipment rows from the Datasheets export's loadout column. All fixture text is invented.
"""``read_export_payloads`` reaches parity with the html arm's row routing (010 R1)."""

from __future__ import annotations

from pipeline.acquire.detail_source import read_export_payloads
from pipeline.acquire.fixtures import FixturePayload

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
