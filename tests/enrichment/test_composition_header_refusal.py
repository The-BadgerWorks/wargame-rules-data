# AI-Assisted: Claude Code (model: claude-sonnet-5) - User Story 4's test for the five-signal
# composition-header refusal (007 task T028): both measured header shapes (GF13's two-row-summing,
# GF14's single-row) are refused with `CMP-HEADER-ROW` while GF15's near-miss genuine first row
# survives untouched, and a before/after comparison shows the second-order `REC-BAND-MISMATCH`
# advisories the phantom rows caused disappearing with them (research D1, FR-010, SC-003).
"""User Story 4: no Kill Team datasheet carries a fabricated header composition row.

research D1's five-signal conjunction is applied over the datasheet's WHOLE composition row set
inside ``pipeline/curate/assemble.py::_composition_entries`` — never in
``pipeline/parse/composition_grammar.py``, which stays mode-blind and unchanged, because the
discriminating evidence (a first row whose count equals the aggregate of the rows after it) does
not exist inside a single line.

GF13/GF14/GF15 (Setup task T007) are the three fixtures this test proves against: two header
shapes measured on the eight affected Kill Team datasheets, and the near-miss the conjunction is
designed NOT to refuse.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from pipeline.curate.assemble import _composition_entries
from pipeline.curate.authored import AuthoredContent
from pipeline.models.curated import CuratedCompositionEntry
from pipeline.parse.wahapedia_csv import CsvReadResult, read_file
from pipeline.reconcile.composition_bands import reconcile_composition_bands
from pipeline.report.catalogue import CATALOGUE
from tests.enrichment.conftest import curated_models

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "wahapedia"


def _detail() -> Mapping[str, CsvReadResult]:
    return {
        "Datasheets_unit_composition.csv": read_file(FIXTURES / "Datasheets_unit_composition.csv"),
    }


def _entries(detail_id: str, datasheet_id: str) -> tuple[list[CuratedCompositionEntry], list[str]]:
    entries, findings = _composition_entries(
        detail_id, datasheet_id, _detail(), AuthoredContent(), curated_models(detail_id)
    )
    return entries, [finding.finding_code for finding in findings]


# --- both measured header shapes are refused ------------------------------------------------


def test_two_row_header_is_refused_and_the_genuine_rows_survive() -> None:
    # GF13: "9 Fenward Cohort" (header) then "3 Fenward Sergeant" + "6 Fenward Trooper" (3+6=9).
    entries, finding_codes = _entries("GF13", "ds-fenward-cohort-alpha")
    assert [entry.model_name for entry in entries] == ["Fenward Sergeant", "Fenward Trooper"]
    assert "CMP-HEADER-ROW" in finding_codes
    assert CATALOGUE["CMP-HEADER-ROW"].severity.value == "blocking"


def test_single_row_header_is_refused_and_the_genuine_row_survives() -> None:
    # GF14: "5 Fenward Vanguard Squad" (header) then "5 Fenward Outrider" (5 == 5).
    entries, finding_codes = _entries("GF14", "ds-fenward-cohort-beta")
    assert [entry.model_name for entry in entries] == ["Fenward Outrider"]
    assert "CMP-HEADER-ROW" in finding_codes


# --- the near-miss the conjunction is designed not to refuse --------------------------------


def test_near_miss_row_survives_because_it_is_not_the_first_row() -> None:
    # GF15: row 1 ("Fenward Relict Warden", 1) is a genuine model and IS the datasheet's own
    # first row -- it resolves, and its count does not sum its successors (1 != 8 + 7), so it is
    # never a candidate. Row 2 ("Fenward Relict Line", 8) is fixed-size, unlinkable, and
    # numerically equal to the sum of rows 1 and 3 (1 + 7 = 8) -- every signal the rule tests for
    # except the position gate, because the rule only ever examines the FIRST row. Nothing is
    # refused; every genuine row still resolves.
    entries, finding_codes = _entries("GF15", "ds-fenward-relict-watch")
    assert [entry.model_name for entry in entries] == [
        "Fenward Relict Warden",
        "Fenward Relict Line",
        "Fenward Relict Skirmisher",
    ]
    assert "CMP-HEADER-ROW" not in finding_codes


# --- the second-order damage the fix also removes (research D1) -----------------------------


def test_second_order_band_mismatch_advisory_disappears_with_the_phantom_row() -> None:
    # research D1: "the phantom is summed by the composition-band reconciliation, inflating a
    # datasheet's model range and raising an advisory band-mismatch finding." Before the fix
    # (simulated here, since `_composition_entries` no longer produces the header row at all),
    # the header's own count (9) is summed on top of the genuine rows' (3 + 6 = 9), producing a
    # represented range of 9..18 that the unit's true model count (9) falls outside of. After the
    # fix, only the genuine rows remain (3 + 6 = 9) and the same model count reconciles cleanly.
    before = [
        CuratedCompositionEntry(line=1, model_name="Fenward Cohort", min_count=9, max_count=9),
        CuratedCompositionEntry(line=2, model_name="Fenward Sergeant", min_count=3, max_count=3),
        CuratedCompositionEntry(line=3, model_name="Fenward Trooper", min_count=6, max_count=6),
    ]
    after, _finding_codes = _entries("GF13", "ds-fenward-cohort-alpha")

    before_findings = reconcile_composition_bands(
        datasheet_id="ds-fenward-cohort-alpha", entries=before, model_counts=[9]
    )
    after_findings = reconcile_composition_bands(
        datasheet_id="ds-fenward-cohort-alpha", entries=after, model_counts=[9]
    )

    assert len(before_findings) == 1
    assert before_findings[0].finding_code == "REC-BAND-MISMATCH"
    assert after_findings == []
