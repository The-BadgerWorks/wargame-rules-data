# AI-Assisted: Claude Opus 5 - 010 R6 task 4 (model half). Failing-first receipt for the one
# model-row rejection class round 6 measured live: 65 model rows are rejected by the
# `characteristics` arm of `_detail_datasheet_fields`, all 65 on `OC`, all 65 on the value class
# `has -`. `line`, `T` and `W` fail `to_int` on zero rows, and the value classes `has +` and
# `has "` measure zero occurrences -- so nothing here asks for them, and the second test pins
# that a genuinely malformed characteristic is still `DQ-MALFORMED-ROW`.
#
# AI-Assisted: Claude Opus 5 - 010 R6b task 2. Failing-first receipt for the wargear-row class
# round 6 measured live: 1990 `Datasheets_wargear.csv` rows carry an empty `line` column and a
# numeric `line_in_wargear`, and were all rejected. The Owner ruled these rows are read, with
# `line` minted from position exactly as an ordinary row's is.
"""``OC`` stated as ``-`` is no objective control, which is mechanically zero -- not a defect.

Two directions, as the project's receipt rule demands:

* the false positive is gone -- a row whose ``OC`` is ``-`` yields a ``CuratedModelLine`` with
  ``objective_control == 0`` and no finding;
* the true positive still fires -- a row whose ``T`` (or ``W``, or ``line``) is non-numeric is
  still ``DQ-MALFORMED-ROW`` on ``field="characteristics"``, and contributes no model line.

A second class covers the wargear loop: a row whose `line` column is empty but whose
`line_in_wargear` parses is read, with `line` minted from position -- and a row whose `line` is
non-empty but malformed is still `DQ-MALFORMED-ROW`, proving the true positive still fires there
too.

All identifiers, names and prose here are invented; only the header shape and the stat value
shapes (``'3+'``, ``'-'``) come from the export.
"""

from __future__ import annotations

from pipeline.curate.assemble import _detail_datasheet_fields
from pipeline.models.curated import CuratedModelLine, CuratedWeaponLine
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text

_DATASHEETS_CSV = (
    "id|name|faction_id|source_id|legend|role|loadout|transport|virtual|leader_head|"
    "leader_footer|damaged_w|damaged_description|link|\n"
    "ds1|Test Unit|TF|1||Battleline|||0|||||https://example.invalid/ds/ds1|\n"
)

_MODELS_HEADER = (
    "datasheet_id|line|name|M|T|Sv|inv_sv|inv_sv_descr|W|Ld|OC|base_size|base_size_descr|\n"
)
_EMPTY_WARGEAR_CSV = (
    "datasheet_id|line|line_in_wargear|dice|name|description|range|type|A|BS_WS|S|AP|D|\n"
)
_EMPTY_KEYWORDS_CSV = "datasheet_id|keyword|model|is_faction_keyword|\n"
_EMPTY_ABILITIES_CSV = "datasheet_id|line|ability_id|model|name|description|type|parameter|\n"


def _detail(models_csv: str, wargear_csv: str = _EMPTY_WARGEAR_CSV) -> dict[str, CsvReadResult]:
    return {
        "Datasheets.csv": read_text("Datasheets.csv", _DATASHEETS_CSV),
        "Datasheets_models.csv": read_text("Datasheets_models.csv", models_csv),
        "Datasheets_wargear.csv": read_text("Datasheets_wargear.csv", wargear_csv),
        "Datasheets_keywords.csv": read_text("Datasheets_keywords.csv", _EMPTY_KEYWORDS_CSV),
        "Datasheets_abilities.csv": read_text("Datasheets_abilities.csv", _EMPTY_ABILITIES_CSV),
    }


_ONE_MODEL_CSV = _MODELS_HEADER + 'ds1|1|Test Trooper|6"|4|3+|||2|6|2|32mm||\n'


def test_a_model_stating_no_objective_control_is_read_as_zero() -> None:
    """`OC` of `-` is the export's way of writing "this model has none" -- mechanically 0.

    Reverted, this is red on the first assertion: `to_int` raises `NumericParseError` on `-`,
    the row is swallowed by the `characteristics` arm, `models` is `[]`, and one
    `DQ-MALFORMED-ROW` finding is emitted instead of a model line.
    """
    models_csv = _MODELS_HEADER + 'ds1|1|Test Walker|10"|9|2+|||12|6|-|100mm||\n'

    fields, findings = _detail_datasheet_fields(
        "ds1", _detail(models_csv), frozenset(), ability_names={}
    )

    models: list[CuratedModelLine] = fields["models"]  # type: ignore[assignment]
    assert len(models) == 1, (
        "a model row stating `-` objective control was rejected rather than read as zero: "
        f"{len(models)} model lines, findings {[f.finding_code for f in findings]}"
    )
    assert models[0].objective_control == 0
    assert models[0].toughness == 9
    assert models[0].wounds == 12
    assert not [f for f in findings if f.finding_code == "DQ-MALFORMED-ROW"]


def test_an_ordinary_numeric_objective_control_is_unchanged() -> None:
    models_csv = _MODELS_HEADER + 'ds1|1|Test Trooper|6"|4|3+|||2|6|2|32mm||\n'

    fields, findings = _detail_datasheet_fields(
        "ds1", _detail(models_csv), frozenset(), ability_names={}
    )

    models: list[CuratedModelLine] = fields["models"]  # type: ignore[assignment]
    assert [m.objective_control for m in models] == [2]
    assert not [f for f in findings if f.finding_code == "DQ-MALFORMED-ROW"]


def test_a_non_numeric_toughness_is_still_a_malformed_row() -> None:
    """The true positive still fires. `T`, `W` and `line` measured zero non-integer rows live,
    so the `-` mapping is confined to `OC`: a malformed one of these is still a defect.

    Reverted, this test is green -- it pins that the fix did not widen into a blanket
    tolerance. It goes red if the `-` mapping is ever extended past `OC`.
    """
    for column, row in (
        ("T", 'ds1|1|Test Trooper|6"|-|3+|||2|6|2|32mm||\n'),
        ("W", 'ds1|1|Test Trooper|6"|4|3+|||-|6|2|32mm||\n'),
        ("line", 'ds1|-|Test Trooper|6"|4|3+|||2|6|2|32mm||\n'),
    ):
        fields, findings = _detail_datasheet_fields(
            "ds1", _detail(_MODELS_HEADER + row), frozenset(), ability_names={}
        )

        assert fields["models"] == [], f"a malformed `{column}` produced a model line"
        malformed = [f for f in findings if f.finding_code == "DQ-MALFORMED-ROW"]
        assert len(malformed) == 1, f"a malformed `{column}` produced {len(malformed)} findings"
        assert malformed[0].detail == {
            "file_name": "Datasheets_models.csv",
            "field": "characteristics",
        }


def test_a_wargear_row_with_empty_line_and_numeric_line_in_wargear_is_read() -> None:
    """The change: a wargear row whose `line` column is empty but whose `line_in_wargear`
    parses is a legitimate weapon profile, not a defect (010 R6b, 1990 live rows).

    Reverted, this test is red: `to_int(weapon.fields["line"], ...)` raises `NumericParseError`
    on the empty string, the row is swallowed by the `except` arm, `weapons` is `[]` and one
    `DQ-MALFORMED-ROW` finding is emitted instead of a weapon line.
    """
    wargear_csv = _EMPTY_WARGEAR_CSV + "ds1||1||Test Blade||Melee|Melee|3|3+|5|-1|2|\n"

    fields, findings = _detail_datasheet_fields(
        "ds1", _detail(_ONE_MODEL_CSV, wargear_csv), frozenset(), ability_names={}
    )

    weapons: list[CuratedWeaponLine] = fields["weapons"]  # type: ignore[assignment]
    assert len(weapons) == 1, (
        "a wargear row with an empty `line` column and a numeric `line_in_wargear` was "
        f"rejected rather than read: weapons={weapons}, "
        f"findings={[f.finding_code for f in findings]}"
    )
    assert weapons[0].line == 1, "the minted `line` was not the row's position"
    assert weapons[0].name == "Test Blade"
    assert not [f for f in findings if f.finding_code == "DQ-MALFORMED-ROW"]


def test_two_empty_line_wargear_rows_get_distinct_positional_lines() -> None:
    """A second empty-`line` row is also read, and the two profiles get distinct positional
    `line` values -- proving `line` is minted from position, not copied from `line_in_wargear`.
    """
    wargear_csv = (
        _EMPTY_WARGEAR_CSV
        + "ds1||1||Test Blade One||Melee|Melee|3|3+|5|-1|2|\n"
        + "ds1||2||Test Blade Two||Melee|Melee|3|3+|5|-1|2|\n"
    )

    fields, findings = _detail_datasheet_fields(
        "ds1", _detail(_ONE_MODEL_CSV, wargear_csv), frozenset(), ability_names={}
    )

    weapons: list[CuratedWeaponLine] = fields["weapons"]  # type: ignore[assignment]
    assert [w.name for w in weapons] == ["Test Blade One", "Test Blade Two"], weapons
    assert [w.line for w in weapons] == [1, 2], (
        f"the two profiles did not get distinct positional `line` values: {weapons}"
    )
    assert not [f for f in findings if f.finding_code == "DQ-MALFORMED-ROW"]


def test_a_wargear_row_with_both_line_columns_empty_is_still_malformed() -> None:
    """A row with `line` empty **and** `line_in_wargear` empty has nothing to mint a position
    guard from and is still `DQ-MALFORMED-ROW`."""
    wargear_csv = _EMPTY_WARGEAR_CSV + "ds1||||Test Blade||Melee|Melee|3|3+|5|-1|2|\n"

    fields, findings = _detail_datasheet_fields(
        "ds1", _detail(_ONE_MODEL_CSV, wargear_csv), frozenset(), ability_names={}
    )

    assert fields["weapons"] == [], "an all-empty `line` pair produced a weapon line"
    malformed = [f for f in findings if f.finding_code == "DQ-MALFORMED-ROW"]
    assert len(malformed) == 1, f"an all-empty `line` pair produced {len(malformed)} findings"
    assert malformed[0].detail == {
        "file_name": "Datasheets_wargear.csv",
        "field": "profile",
    }


def test_a_wargear_row_with_empty_line_and_non_numeric_line_in_wargear_is_still_malformed() -> None:
    """A row with `line` empty and `line_in_wargear` non-numeric is still `DQ-MALFORMED-ROW`."""
    wargear_csv = _EMPTY_WARGEAR_CSV + "ds1||not-a-number||Test Blade||Melee|Melee|3|3+|5|-1|2|\n"

    fields, findings = _detail_datasheet_fields(
        "ds1", _detail(_ONE_MODEL_CSV, wargear_csv), frozenset(), ability_names={}
    )

    assert fields["weapons"] == [], "a non-numeric `line_in_wargear` produced a weapon line"
    malformed = [f for f in findings if f.finding_code == "DQ-MALFORMED-ROW"]
    assert len(malformed) == 1, (
        f"a non-numeric `line_in_wargear` produced {len(malformed)} findings"
    )
    assert malformed[0].detail == {
        "file_name": "Datasheets_wargear.csv",
        "field": "profile",
    }


def test_a_wargear_row_with_non_empty_malformed_line_is_still_malformed() -> None:
    """The true positive still fires: a row whose `line` column is non-empty but malformed is
    still `DQ-MALFORMED-ROW`, exactly as before this change."""
    wargear_csv = _EMPTY_WARGEAR_CSV + "ds1|not-a-number|1||Test Blade||Melee|Melee|3|3+|5|-1|2|\n"

    fields, findings = _detail_datasheet_fields(
        "ds1", _detail(_ONE_MODEL_CSV, wargear_csv), frozenset(), ability_names={}
    )

    assert fields["weapons"] == [], "a malformed non-empty `line` produced a weapon line"
    malformed = [f for f in findings if f.finding_code == "DQ-MALFORMED-ROW"]
    assert len(malformed) == 1, f"a malformed non-empty `line` produced {len(malformed)} findings"
    assert malformed[0].detail == {
        "file_name": "Datasheets_wargear.csv",
        "field": "profile",
    }


def test_a_non_numeric_objective_control_that_is_not_a_dash_is_still_malformed() -> None:
    """The `OC` field's own boundary: only exactly `-` maps to zero, nothing else.

    Without this fence, every other test here stays green if `_objective_control` were widened
    to swallow any `NumericParseError` on `OC` and return `0` -- and `0` is a legal value in
    `schemas/curated/datasheet.schema.json`, so nothing downstream would catch the fabricated
    characteristic. Two shapes, so the fence is not a single point: a value that contains a dash
    without being one, and a non-numeric value with no dash at all. Both invented.
    """
    for shape, row in (
        ("contains a dash", 'ds1|1|Test Trooper|6"|4|3+|||2|6|1-2|32mm||\n'),
        ("no dash at all", 'ds1|1|Test Trooper|6"|4|3+|||2|6|N/A|32mm||\n'),
    ):
        fields, findings = _detail_datasheet_fields(
            "ds1", _detail(_MODELS_HEADER + row), frozenset(), ability_names={}
        )

        assert fields["models"] == [], (
            f"an `OC` value that {shape} was mapped to a model line rather than rejected: "
            "only exactly `-` means no objective control"
        )
        malformed = [f for f in findings if f.finding_code == "DQ-MALFORMED-ROW"]
        assert len(malformed) == 1, f"an `OC` value that {shape} produced {len(malformed)} findings"
        assert malformed[0].detail == {
            "file_name": "Datasheets_models.csv",
            "field": "characteristics",
        }
