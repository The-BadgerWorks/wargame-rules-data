# AI-Assisted: Claude Code (model: claude-sonnet-5) - User Story 3's independent test (007 task
# T041): GF12 rows 5-10 through `_option_structure`, end to end, proving the story — a reader of
# GF12's own card sees a footnote-style restriction as a structured fact never left as a marker
# on the item's own name, and never silently dropped — rather than the pieces
# `test_item_constraints.py` and `test_contract_guarantees.py` prove separately.
"""User Story 3, end to end: see a footnote restriction instead of a stray marker.

The tests beside this one prove the pieces: the vocabulary and the marker strip
(``test_item_constraints.py``), and the blocking marker-residue guarantee
(``test_contract_guarantees.py``). This one proves the **story** — GF12's own card, read
through ``_option_structure`` exactly as ``_datasheet_for`` builds it, produces every
``CuratedItemConstraint`` the card states, with every item name published clean and the one
unlinkable restriction shipping unlinked rather than guessed or dropped (FR-009, SC-002).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from pipeline.curate.assemble import _composition_entries, _option_structure
from pipeline.curate.authored import AuthoredContent
from pipeline.models.curated import CuratedWeaponLine, ItemConstraintType
from pipeline.parse.wahapedia_csv import CsvReadResult, read_file
from pipeline.report.catalogue import CATALOGUE
from tests.enrichment.conftest import curated_models, weapon

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "wahapedia"
DETAIL_ID = "GF12"
DATASHEET = "ds-marshlight-vigil"

WEAPONS: Sequence[CuratedWeaponLine] = (
    weapon(1, "Storm maul"),
    weapon(2, "Glow lance"),
    weapon(3, "Marsh axe"),
)


def _detail() -> Mapping[str, CsvReadResult]:
    return {
        "Datasheets_options.csv": read_file(FIXTURES / "Datasheets_options.csv"),
        "Datasheets_unit_composition.csv": read_file(FIXTURES / "Datasheets_unit_composition.csv"),
    }


def test_gf12s_footnote_restrictions_all_become_structured_facts_never_markers_never_dropped() -> (
    None
):
    detail = _detail()
    composition, _composition_findings = _composition_entries(
        DETAIL_ID, DATASHEET, detail, AuthoredContent(), curated_models("GF12")
    )
    outcome = _option_structure(
        DETAIL_ID, DATASHEET, detail, AuthoredContent(), WEAPONS, (), composition
    )
    constraints = {c.constraint_index: c for c in outcome.item_constraints}
    finding_codes = [f.finding_code for f in outcome.findings]

    # Every name field GF12 exercises publishes clean — no `*` survives anywhere, on either an
    # ordinary choice's own name (row 5) or a constraint's item name (rows 6-9).
    for choice in outcome.choices:
        assert "*" not in choice.name, choice.id
    for constraint in constraints.values():
        assert "*" not in constraint.item_name, constraint.constraint_index

    # Four restrictions resolve as structured facts — two unscoped, one scoped to a named model
    # group, one deliberately unlinked — never guessed and never silently dropped.
    assert constraints[6].constraint_type is ItemConstraintType.NOT_REPLACEABLE
    assert constraints[6].weapon_line == 3
    assert constraints[7].constraint_type is ItemConstraintType.NOT_REPLACEABLE
    assert constraints[7].model_name == "Marshlight Warden"
    assert constraints[8].constraint_type is ItemConstraintType.ONE_PER_UNIT
    assert constraints[8].weapon_line == 2
    assert constraints[9].weapon_line is None, "ceremonial standard names no weapon of GF12"
    assert "CST-UNLINKED" in finding_codes
    assert CATALOGUE["CST-UNLINKED"].severity.value == "advisory"

    # The one row (10) that looks like a restriction but matches no vocabulary member produces no
    # row and the advisory that says so — never a nearest-member guess.
    assert 10 not in constraints
    assert "CST-UNPARSED" in finding_codes
    assert CATALOGUE["CST-UNPARSED"].severity.value == "advisory"

    # And the row (5) that is NOT a restriction at all — an ordinary equip choice whose granted
    # item's own name happened to carry the marker — produces no constraint row either.
    assert 5 not in constraints
