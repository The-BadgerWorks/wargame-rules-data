# AI-Assisted: Claude Code (model: claude-opus-5) - Fixtures for the 004 enrichment tests (004
# tasks T019-T026): the two synthetic detail-source exports, read through the ordinary CSV
# reader so the tests exercise the same path a run does.
"""Shared access to ``fixtures/enrichment/``.

Every row these fixtures carry is invented — invented faction, invented units, invented model
and weapon names, invented option wording — and hand-authored from the *structure descriptions*
in `004`'s research D2 and D3. Nothing here is a slice of any acquired source, and redacting a
capture into a fixture would not make it one either (FR-006).

The tests read the exports through :func:`pipeline.parse.wahapedia_csv.read_file` rather than
splitting the text themselves, so a change to the reader's record repair shows up here as a test
failure rather than as a divergence between what the suite parses and what a run parses.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pytest

from pipeline.models.curated import CuratedModelLine, CuratedWeaponLine
from pipeline.parse.wahapedia_csv import CsvReadResult, read_file

ENRICHMENT = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "wahapedia"


def _read(file_name: str) -> CsvReadResult:
    path = ENRICHMENT / file_name
    if not path.is_file():
        pytest.skip(f"{path} has not landed yet")
    return read_file(path)


@pytest.fixture(scope="session")
def composition_rows() -> Mapping[str, list[tuple[int, str]]]:
    """``detail datasheet id -> [(line, description)]`` from the composition export."""
    grouped: dict[str, list[tuple[int, str]]] = {}
    for row in _read("Datasheets_unit_composition.csv").rows:
        grouped.setdefault(row.fields["datasheet_id"], []).append(
            (int(row.fields["line"]), row.fields["description"])
        )
    return grouped


@pytest.fixture(scope="session")
def option_rows() -> Mapping[str, list[tuple[int, str]]]:
    """``detail datasheet id -> [(line, description)]`` from the options export."""
    grouped: dict[str, list[tuple[int, str]]] = {}
    for row in _read("Datasheets_options.csv").rows:
        grouped.setdefault(row.fields["datasheet_id"], []).append(
            (int(row.fields["line"]), row.fields["description"])
        )
    return grouped


#: The model rows the composition fixture's datasheets carry, as a run would read them from
#: ``Datasheets_models.csv``. Kept beside the fixture rather than in it because the linking
#: cases — exactly one match, none, and two — are a property of the *pair* of files, and stating
#: the pair in one place is what makes each case legible.
MODEL_LINES: Mapping[str, Mapping[int, str]] = {
    "GF01": {1: "Glimmerfen Warden"},
    "GF02": {1: "Fenmire Skirmisher", 2: "Fenmire Marshbearer"},
    # No model row is named "Bracklight Outrider": the composition line names the unit's models
    # and the profile is filed under a different name, which is the zero-match case.
    "GF03": {1: "Bracklight Rider"},
    "GF04": {1: "Sedgeward Adept", 2: "Sedgeward Acolyte"},
    "GF05": {1: "Mirefen Tangler"},
    # "Thornlight Chorister" is a prefix of "Thornlight Chorister Prime", so the Prime line
    # matches both rows and is correctly refused rather than attached to the shorter one.
    "GF06": {1: "Thornlight Chorister Prime", 2: "Thornlight Chorister"},
}


def model_lines(datasheet_id: str) -> Mapping[int, str]:
    return MODEL_LINES[datasheet_id]


def curated_models(datasheet_id: str) -> list[CuratedModelLine]:
    """The same model rows as curated records, for tests that need the real type."""
    return [
        CuratedModelLine(
            line=line,
            name=name,
            movement='6"',
            toughness=4,
            save="4+",
            wounds=2,
            leadership="7+",
            objective_control=1,
        )
        for line, name in sorted(MODEL_LINES[datasheet_id].items())
    ]


def weapon(line: int, name: str) -> CuratedWeaponLine:
    """One melee weapon profile — everything but ``line`` and ``name`` is scaffolding here."""
    return CuratedWeaponLine(
        line=line,
        name=name,
        is_melee=True,
        attacks="2",
        skill="3+",
        strength="4",
        armour_penetration="-1",
        damage="1",
    )
