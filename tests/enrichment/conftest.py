# AI-Assisted: Claude Code (model: claude-opus-5) - Fixtures for the 004 enrichment tests (004
# tasks T019-T026): the two synthetic detail-source exports, read through the ordinary CSV
# reader so the tests exercise the same path a run does.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the keyword-classification fixture
# access for US2 (004 task T034): the keyword export, the curated faction tree the fixture
# implies, and the curator's keyword-class records, all in one place because the classification
# cases are a property of the THREE together and stating them apart makes each one illegible.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added MODEL_LINES entries for GF12-GF15
# (007 task T005/T007 fixture scaffolding): the legacy stem-object/footnote-restriction/
# over-length-item fixture (GF12) and the three unit-size-header fixtures (GF13-GF15), the last
# of which is the near-miss the five-signal header rule is designed not to refuse.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Reconciled the three csv fixture sets this
# repository carries (009 task T013, retiring risk R-G's fixture half): recorded which one models
# the real bulk export and which one models the html arm's own manufactured table, so a future
# reader of `Datasheets_unit_equipment.csv` cannot mistake this set for evidence about the export.
"""Shared access to ``fixtures/enrichment/``.

Every row these fixtures carry is invented — invented faction, invented units, invented model
and weapon names, invented option wording — and hand-authored from the *structure descriptions*
in `004`'s research D2 and D3. Nothing here is a slice of any acquired source, and redacting a
capture into a fixture would not make it one either (FR-006).

The tests read the exports through :func:`pipeline.parse.wahapedia_csv.read_file` rather than
splitting the text themselves, so a change to the reader's record repair shows up here as a test
failure rather than as a divergence between what the suite parses and what a run parses.

**Which of the three committed csv fixture sets models what (009 T013).** This repository carries
three: this one (``fixtures/enrichment/``), ``fixtures/minimal/``, and ``fixtures/disagreements/``.
They diverge on exactly one point that matters to the CSV acquisition migration, and it is worth
stating plainly rather than leaving a future reader to infer it from a diff:

* ``fixtures/minimal/wahapedia/`` and ``fixtures/disagreements/wahapedia/`` **omit**
  ``Datasheets_unit_equipment.csv`` entirely — correctly, because the real bulk export publishes
  no such file (FR-017's whole premise: the html arm *manufactures* it from the datacard's
  composition block, and phase 0's 20-file inventory confirmed the export carries no counterpart).
  Both sets are built to stand in for a real acquisition — one arm or the other, faithfully — and
  this is the one file whose *absence* is the faithful choice.
* **This set (``fixtures/enrichment/wahapedia/``) invents
  ``Datasheets_unit_equipment.csv``.** It exists so `pipeline.parse.equipment_grammar` can be
  exercised directly against a table of its own, independent of which acquisition arm would have
  produced it — `test_equipment_grammar_regression.py`'s own docstring records that no such file
  backed the grammar at all before `008` task T009 created this one. **It is not evidence about
  what the export publishes**, and FR-018's rule follows directly: table-presence and
  table-population claims for the migration are asserted against an **acquired** set (009 T054,
  T065), never against this file or any fixture — the one category of assertion in this feature
  that may not be fixture-backed.

`Datasheets_unit_composition.csv` here (this set) carries the equipment-marker shape (`GF05|1`,
`CM03|2`, 009 T011) that a real export-sourced derivation reads *instead of* a manufactured
equipment table — the mechanism FR-017's csv-mode derivation route actually uses, and the reason
this set's own invented equipment file and its composition file can coexist without contradicting
each other: one models the html arm's manufactured table, the other models the raw material a csv
derivation reads.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pytest

from pipeline.models.authored import KeywordClassEntry
from pipeline.models.curated import (
    CuratedFaction,
    CuratedKeyword,
    CuratedModelLine,
    CuratedWeaponLine,
)
from pipeline.parse.wahapedia_csv import CsvReadResult, read_file
from tests.factories import faction

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
    # -- 007-loadout-display-fidelity: T005/T007 additions -------------------------------------
    # GF12 is T005's legacy stem-object fixture (research D3.3's three outcomes plus
    # OPT-SCOPE-UNRESOLVED) and T006/T008's footnote-restriction and over-length-item fixtures.
    # "Marshlight Warden" is the eligibility subject three option rows name; it must link so the
    # sergeant-shape subject is a genuine model, never itself the unresolved case.
    "GF12": {1: "Marshlight Warden", 2: "Marshlight Sentry"},
    # GF13/GF14/GF15 are T007's unit-size-header fixtures (research D1's five-signal rule). No
    # model row is named "Fenward Cohort" or "Fenward Vanguard Squad": the header names are the
    # zero-match case signal 5 tests for, on the same terms GF03's "Bracklight Outrider" already
    # establishes.
    "GF13": {1: "Fenward Sergeant", 2: "Fenward Trooper"},
    "GF14": {1: "Fenward Outrider"},
    # GF15 is the near-miss: its row 2 ("Fenward Relict Line") is fixed-size, unlinkable (no
    # profile below is named for it, on the same zero-match terms), and numerically equal to the
    # sum of the OTHER two rows (1 + 7 = 8) — every property research D1's five-signal rule tests
    # for except the first (it is not the datasheet's FIRST composition row, so the rule — which
    # only ever examines row 1 — never considers it a candidate at all). This is "the one case
    # the five-signal conjunction is designed not to refuse": not because four of five signals
    # fail, but because the position gate that starts the conjunction does.
    "GF15": {1: "Fenward Relict Warden", 3: "Fenward Relict Skirmisher"},
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


#: The curated faction tree ``fixtures/enrichment/wahapedia/Factions.csv`` implies once
#: ``curation/faction-map.json`` has mapped it. Two parentless factions and one chapter the
#: points source models as a faction of its own — which is the FR-018 case, and the only reason
#: `f-sedgeward-conclave` is here is so the parent-agreement check has a *wrong* parent available
#: to be asserted against (T037).
CHAPTER_FACTIONS: tuple[CuratedFaction, ...] = (
    faction("f-glimmerfen-covenant"),
    faction("f-sedgeward-conclave"),
    faction("f-bracklight-host", parent="f-glimmerfen-covenant"),
)

#: What the curator writes in ``curation/keyword-classes.json`` for this fixture: **only the
#: exceptions**. `GLIMMERFEN COVENANT` needs no record — it resolves to a parentless faction and
#: defaults to `faction` — and `MIREFEN ENCLAVE` deliberately has none, which is the
#: unclassified case (`KWD-UNCLASSIFIED`, advisory).
KEYWORD_CLASS_RECORDS: tuple[KeywordClassEntry, ...] = (
    KeywordClassEntry(
        keyword="THORNLIGHT CHORUS",
        keyword_class="chapter",
        parent_faction_id="f-glimmerfen-covenant",
        note="A chapter the points source does not model as a faction of its own.",
    ),
    KeywordClassEntry(
        keyword="BRACKLIGHT HOST",
        keyword_class="chapter",
        parent_faction_id="f-glimmerfen-covenant",
        chapter_faction_id="f-bracklight-host",
        note="Modelled as a faction as well; enumerated uniformly and flagged (FR-018).",
    ),
)


@pytest.fixture(scope="session")
def keyword_rows() -> Mapping[str, list[tuple[str, bool, str | None]]]:
    """``detail datasheet id -> [(keyword, is_faction_keyword, model_scope)]``."""
    grouped: dict[str, list[tuple[str, bool, str | None]]] = {}
    for row in _read("Datasheets_keywords.csv").rows:
        grouped.setdefault(row.fields["datasheet_id"], []).append(
            (
                row.fields["keyword"],
                row.fields.get("is_faction_keyword", "").strip().casefold() == "true",
                row.fields.get("model") or None,
            )
        )
    return grouped


def curated_keywords(
    rows: Mapping[str, list[tuple[str, bool, str | None]]], datasheet_id: str
) -> list[CuratedKeyword]:
    """The fixture's keyword rows for one datasheet, as the curated records assemble builds."""
    return [
        CuratedKeyword(keyword=keyword, is_faction_keyword=is_faction, model_scope=scope)
        for keyword, is_faction, scope in rows[datasheet_id]
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
