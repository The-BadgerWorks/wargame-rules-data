# AI-Assisted: Claude Code (model: claude-opus-5) - Failing-first test for 010 R6: the CSV
# export states a Core or Faction binding with an EMPTY `name` and a populated `ability_id`
# (2015 Core and 1437 of 1442 Faction rows live, all 3452 resolving to an `Abilities.csv` id),
# so `_detail_datasheet_fields`'s binding loop `continue`d on the empty name and bound zero
# `core:` keys against the published tree's 2422. Invented ids, names and prose throughout.
"""``ability_keys`` must resolve a nameless binding through ``Abilities.csv``.

The binding row is a *join row*: for Core and Faction abilities the export states the name once,
in `Abilities.csv`, and the binding carries only the `ability_id`. Reading the binding's own
`name` column alone therefore drops every Core and Faction key.

And a binding that resolves to nothing is now **reported** rather than skipped in silence:
`DQ-MALFORMED-ROW` against `Datasheets_abilities.csv`/`name`. Silence is what hid the missing
2422 keys for five rounds.
"""

from __future__ import annotations

from pipeline.curate.assemble import _detail_datasheet_fields
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text

_DATASHEETS_CSV = (
    "id|name|faction_id|source_id|legend|role|loadout|transport|virtual|leader_head|"
    "leader_footer|damaged_w|damaged_description|link|\n"
    "ds1|Test Unit|TF|1||Battleline|||0|||||https://example.invalid/ds/ds1|\n"
)

_EMPTY_MODELS_CSV = (
    "datasheet_id|line|name|M|T|Sv|inv_sv|inv_sv_descr|W|Ld|OC|base_size|base_size_descr|\n"
)
_EMPTY_KEYWORDS_CSV = "datasheet_id|keyword|model|is_faction_keyword|\n"
_EMPTY_WARGEAR_CSV = (
    "datasheet_id|line|line_in_wargear|dice|name|description|range|type|A|BS_WS|S|AP|D|\n"
)

_ABILITIES_HEADER = "id|name|legend|faction_id|description|\n"
_BINDINGS_HEADER = "datasheet_id|line|ability_id|model|name|description|type|parameter|\n"

#: Invented placeholder prose (research D10) — never the publisher's wording.
_INVENTED_DESCRIPTION = "Invented placeholder prose describing one mechanic, for this test only."


def _detail(*, bindings: str, abilities: str = "") -> dict[str, CsvReadResult]:
    return {
        "Datasheets.csv": read_text("Datasheets.csv", _DATASHEETS_CSV),
        "Datasheets_wargear.csv": read_text("Datasheets_wargear.csv", _EMPTY_WARGEAR_CSV),
        "Datasheets_models.csv": read_text("Datasheets_models.csv", _EMPTY_MODELS_CSV),
        "Datasheets_keywords.csv": read_text("Datasheets_keywords.csv", _EMPTY_KEYWORDS_CSV),
        "Datasheets_abilities.csv": read_text(
            "Datasheets_abilities.csv", _BINDINGS_HEADER + bindings
        ),
        "Abilities.csv": read_text("Abilities.csv", _ABILITIES_HEADER + abilities),
    }


def test_a_nameless_core_binding_resolves_its_name_through_abilities_csv() -> None:
    fields, findings = _detail_datasheet_fields(
        "ds1",
        _detail(
            bindings=f"ds1|1|A1|||{_INVENTED_DESCRIPTION}|Core||\n",
            abilities=f"A1|Tidal Step||TF|{_INVENTED_DESCRIPTION}|\n",
        ),
        frozenset(),
    )

    assert fields["ability_keys"] == ["core:tidal-step"]
    assert [finding.finding_code for finding in findings] == []


def test_a_nameless_faction_binding_resolves_its_name_through_abilities_csv() -> None:
    fields, findings = _detail_datasheet_fields(
        "ds1",
        _detail(
            bindings=f"ds1|1|A2|||{_INVENTED_DESCRIPTION}|Faction||\n",
            abilities=f"A2|Ember Vigil||TF|{_INVENTED_DESCRIPTION}|\n",
        ),
        frozenset(),
    )

    assert fields["ability_keys"] == ["faction:ember-vigil"]
    assert [finding.finding_code for finding in findings] == []


def test_a_bindings_own_name_still_wins_over_the_joined_one() -> None:
    """The datasheet-local override case: `datasheet` bindings state their own name."""
    fields, _findings = _detail_datasheet_fields(
        "ds1",
        _detail(
            bindings=f"ds1|1|A1||Harbour Watch|{_INVENTED_DESCRIPTION}|Datasheet||\n",
            abilities=f"A1|Tidal Step||TF|{_INVENTED_DESCRIPTION}|\n",
        ),
        frozenset(),
    )

    assert _fields_keys(fields) == ["datasheet:harbour-watch"]


def test_an_unresolvable_nameless_binding_is_reported_not_skipped_in_silence() -> None:
    fields, findings = _detail_datasheet_fields(
        "ds1",
        _detail(
            bindings=f"ds1|1|A9|||{_INVENTED_DESCRIPTION}|Core||\n",
            abilities=f"A1|Tidal Step||TF|{_INVENTED_DESCRIPTION}|\n",
        ),
        frozenset(),
    )

    assert _fields_keys(fields) == []
    assert [finding.finding_code for finding in findings] == ["DQ-MALFORMED-ROW"]
    assert findings[0].detail == {
        "file_name": "Datasheets_abilities.csv",
        "field": "name",
    }
    assert list(findings[0].entity_refs) == ["wahapedia:ds1"]


def test_a_detail_source_without_the_abilities_table_reports_rather_than_raising() -> None:
    """The fixture sets that predate the join publish no `Abilities.csv` at all."""
    detail = _detail(bindings=f"ds1|1|A1|||{_INVENTED_DESCRIPTION}|Core||\n")
    del detail["Abilities.csv"]

    fields, findings = _detail_datasheet_fields("ds1", detail, frozenset())

    assert _fields_keys(fields) == []
    assert [finding.finding_code for finding in findings] == ["DQ-MALFORMED-ROW"]


def _fields_keys(fields: dict[str, object]) -> list[str]:
    keys: list[str] = fields["ability_keys"]  # type: ignore[assignment]
    return keys
