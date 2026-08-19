# AI-Assisted: Claude Code (model: claude-sonnet-5) - Failing-first tests for the csv-mode
# equipment derivation (009 tasks T052/T053, FR-017): `Datasheets_unit_composition.csv` rows
# carrying the `... is equipped with:` marker are split out of composition and into a derived
# `Datasheets_unit_equipment.csv`, in the reader adapter, on the same shape
# `wahapedia_html_dom.py::_equipment` already extracts under `html` mode -- and the split routes
# the row out of `CMP-UNRESOLVED`'s refusal path rather than merely relabelling it (plan.md
# finding 9, the "poisoning fix").
"""``read_export_payloads`` derives a csv-mode equipment table from composition rows.

The real bulk export publishes no ``Datasheets_unit_equipment.csv`` at all (FR-018's whole
premise) -- this reader-level derivation is the csv arm's equivalent of what
``wahapedia_html_dom.py::_equipment`` does against a DOM: read the *same* marker sentence,
already filed by the export into the composition table (`plan.md` finding 9's `GF05|1`/`CM03|2`
shape), and emit it into the equipment table's own ``datasheet_id|line|description`` shape.

Fixture rows here mirror ``fixtures/enrichment/wahapedia``'s ``CM03`` shape exactly (invented
content, `tests/enrichment/conftest.py`'s own docstring already records `CM03|2` as "the mechanism
FR-017's csv-mode derivation route actually uses") so a reader confirmed against this synthetic
pair is confirmed against the same shape the fixture-backed grammar tests already exercise.
"""

from __future__ import annotations

from pipeline.acquire.detail_source import read_export_payloads
from pipeline.acquire.fixtures import FixturePayload
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE

_COMPOSITION = (
    "datasheet_id|line|description|\n"
    "CM03|1|4 Marshguard Trooper|\n"
    "CM03|2|Every model in this unit is equipped with: glow lantern; tide axe.|\n"
    "CM04|1|3 Fenmarsh Warden|\n"
)


def _read(composition: str = _COMPOSITION) -> dict[str, object]:
    return read_export_payloads(
        [FixturePayload(name="Datasheets_unit_composition.csv", text=composition)]
    )


def test_a_marker_row_is_removed_from_the_composition_result() -> None:
    detail = _read()

    rows = detail["Datasheets_unit_composition.csv"].grouped_by("datasheet_id")  # type: ignore[attr-defined]
    assert [row.fields["line"] for row in rows["CM03"]] == ["1"]


def test_a_genuine_composition_row_on_the_same_datasheet_is_left_alone() -> None:
    detail = _read()

    rows = detail["Datasheets_unit_composition.csv"].grouped_by("datasheet_id")  # type: ignore[attr-defined]
    (row,) = rows["CM03"]
    assert row.fields["description"] == "4 Marshguard Trooper"


def test_a_datasheet_with_no_marker_row_is_unaffected() -> None:
    detail = _read()

    rows = detail["Datasheets_unit_composition.csv"].grouped_by("datasheet_id")  # type: ignore[attr-defined]
    assert [row.fields["description"] for row in rows["CM04"]] == ["3 Fenmarsh Warden"]


def test_the_marker_row_is_derived_into_the_equipment_table_unchanged_shape() -> None:
    detail = _read()

    assert EQUIPMENT_TABLE in detail
    equipment_rows = detail[EQUIPMENT_TABLE].grouped_by("datasheet_id")  # type: ignore[attr-defined]
    (row,) = equipment_rows["CM03"]
    assert row.fields["line"] == "2"
    assert (
        row.fields["description"]
        == "Every model in this unit is equipped with: glow lantern; tide axe."
    )


def test_no_composition_table_at_all_is_a_no_op() -> None:
    detail = read_export_payloads(
        [FixturePayload(name="Datasheets.csv", text="id|name|\nCM03|Marshguard Squad|\n")]
    )
    assert EQUIPMENT_TABLE not in detail


def test_no_marker_rows_leaves_the_equipment_table_absent() -> None:
    detail = read_export_payloads(
        [
            FixturePayload(
                name="Datasheets_unit_composition.csv",
                text="datasheet_id|line|description|\nCM04|1|3 Fenmarsh Warden|\n",
            )
        ]
    )
    assert EQUIPMENT_TABLE not in detail


def test_an_already_present_equipment_table_is_appended_to_not_replaced() -> None:
    """`read_export_payloads` also receives an already-acquired `Datasheets_unit_equipment.csv`
    payload in principle (the reader is generic over whatever payloads are handed to it); the
    derivation must not clobber it."""
    detail = read_export_payloads(
        [
            FixturePayload(name="Datasheets_unit_composition.csv", text=_COMPOSITION),
            FixturePayload(
                name="Datasheets_unit_equipment.csv",
                text="datasheet_id|line|description|\nGF24|1|Existing row.|\n",
            ),
        ]
    )
    ids = {row.fields["datasheet_id"] for row in detail[EQUIPMENT_TABLE].rows}  # type: ignore[attr-defined]
    assert ids == {"GF24", "CM03"}
