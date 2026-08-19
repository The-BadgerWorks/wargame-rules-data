# AI-Assisted: Claude Code (model: claude-sonnet-5) - Failing-first test for 009's Finding A
# (CON-DUPLICATE-KEY, datasheetWeapons, 39 live instances): the real bulk export numbers a
# WEAPON, not a weapon PROFILE ROW -- a multi-profile weapon (plasma standard/supercharge,
# missile frag/krak, and 314 other live datasheets measured this session) states two rows under
# the same `line`, distinguished only by `line_in_wargear`, a column `_detail_datasheet_fields`
# never reads. Reading the export's own `line` column verbatim collided every such pair onto one
# `(datasheetId, line)` key. Invented weapon names and stats throughout; the shape (two rows,
# same `line`, different `line_in_wargear`) is transcribed from the live export's own header and
# row shape, never the publisher's content.
"""``CuratedWeaponLine.line`` must be unique per row, not copied off the export's own column.

The export's `line` numbers a wargear *choice* (the same physical weapon may print more than one
firing-mode row under it); the html arm has never had this problem because
`wahapedia_html_dom.py::_weapon_profiles` mints a fresh sequential number per scraped row rather
than reading one off the page. `_detail_datasheet_fields`'s weapon loop is the one place both
arms' `Datasheets_wargear.csv`-shaped tables converge, so the fix belongs there: mint `line` from
the row's own position in the datasheet's weapon list, the same guarantee the html arm already
gives for free, while still validating the raw `line` column parses (a genuinely malformed row is
still `DQ-MALFORMED-ROW`).
"""

from __future__ import annotations

from pipeline.curate.assemble import _detail_datasheet_fields
from pipeline.models.curated import CuratedWeaponLine
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text

_DATASHEETS_CSV = (
    "id|name|faction_id|source_id|legend|role|loadout|transport|virtual|leader_head|"
    "leader_footer|damaged_w|damaged_description|link|\n"
    "ds1|Test Unit|TF|1||Battleline|||0|||||https://example.invalid/ds/ds1|\n"
)

#: The live export's own shape (research this session, 009 Finding A): two profile rows share one
#: `line`, disambiguated by `line_in_wargear` alone. A third, single-profile weapon is included to
#: prove the fix does not disturb the ordinary (non-colliding) case.
_WARGEAR_CSV = (
    "datasheet_id|line|line_in_wargear|dice|name|description|range|type|A|BS_WS|S|AP|D|\n"
    'ds1|1|1||Test plasma gun — standard|[]|24"|Ranged|1|3+|7|-2|1|\n'
    'ds1|1|2||Test plasma gun — supercharge|[]|24"|Ranged|1|3+|8|-3|2|\n'
    "ds1|2|1||Test combat blade||Melee|Melee|3|3+|4|0|1|\n"
)

_EMPTY_MODELS_CSV = (
    "datasheet_id|line|name|M|T|Sv|inv_sv|inv_sv_descr|W|Ld|OC|base_size|base_size_descr|\n"
)
_EMPTY_KEYWORDS_CSV = "datasheet_id|keyword|model|is_faction_keyword|\n"
_EMPTY_ABILITIES_CSV = "datasheet_id|line|ability_id|model|name|description|type|parameter|\n"


def _detail() -> dict[str, CsvReadResult]:
    return {
        "Datasheets.csv": read_text("Datasheets.csv", _DATASHEETS_CSV),
        "Datasheets_wargear.csv": read_text("Datasheets_wargear.csv", _WARGEAR_CSV),
        "Datasheets_models.csv": read_text("Datasheets_models.csv", _EMPTY_MODELS_CSV),
        "Datasheets_keywords.csv": read_text("Datasheets_keywords.csv", _EMPTY_KEYWORDS_CSV),
        "Datasheets_abilities.csv": read_text("Datasheets_abilities.csv", _EMPTY_ABILITIES_CSV),
    }


def test_two_profile_rows_sharing_the_exports_line_get_distinct_curated_lines() -> None:
    fields, findings = _detail_datasheet_fields("ds1", _detail(), frozenset())

    weapons: list[CuratedWeaponLine] = fields["weapons"]  # type: ignore[assignment]

    assert [w.name for w in weapons] == [
        "Test plasma gun — standard",
        "Test plasma gun — supercharge",
        "Test combat blade",
    ]
    lines = [w.line for w in weapons]
    assert len({w.line for w in weapons}) == len(weapons), (
        f"CON-DUPLICATE-KEY precursor: two weapon rows share one `line`: {lines}"
    )
    assert not [f for f in findings if f.finding_code == "DQ-MALFORMED-ROW"]


def test_the_row_order_is_preserved_in_the_minted_line_numbers() -> None:
    """The mint is positional, not a re-sort — the export's own row order is what a consumer
    displaying a datasheet's weapons in source order depends on."""
    fields, _ = _detail_datasheet_fields("ds1", _detail(), frozenset())
    weapons: list[CuratedWeaponLine] = fields["weapons"]  # type: ignore[assignment]

    lines = [w.line for w in weapons]
    assert lines == sorted(lines)


def test_a_single_profile_datasheet_is_unaffected() -> None:
    """The ordinary (non-colliding) case: one row per weapon, exactly as before the fix."""
    detail = _detail()
    only_blade = CsvReadResult(
        file_name="Datasheets_wargear.csv",
        field_names=detail["Datasheets_wargear.csv"].field_names,
        rows=tuple(
            row
            for row in detail["Datasheets_wargear.csv"].rows
            if row.fields["name"] == "Test combat blade"
        ),
        repairs=0,
        findings=(),
    )
    detail["Datasheets_wargear.csv"] = only_blade

    fields, _ = _detail_datasheet_fields("ds1", detail, frozenset())
    weapons: list[CuratedWeaponLine] = fields["weapons"]  # type: ignore[assignment]

    assert [(w.name, w.line) for w in weapons] == [("Test combat blade", 1)]
