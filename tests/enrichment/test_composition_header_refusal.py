# AI-Assisted: Claude Code (model: claude-sonnet-5) - User Story 4's test for the five-signal
# composition-header refusal (007 task T028): both measured header shapes (GF13's two-row-summing,
# GF14's single-row) are refused with `CMP-HEADER-ROW` while GF15's near-miss genuine first row
# survives untouched, and a before/after comparison shows the second-order `REC-BAND-MISMATCH`
# advisories the phantom rows caused disappearing with them (research D1, FR-010, SC-003).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Rewritten for the Product Owner's 2026-08-14
# decision (T061 review of the live corpus's T031 re-derivation): the automatic five-signal
# conjunction is demoted from a blocking auto-drop to an advisory flag, because the live corpus
# proved its own documented false-positive risk (R-1/R-A) real -- three of the rows it would have
# auto-dropped were genuine duo-sheet first models, not phantom headers. This file now proves (1)
# a flagged row SURVIVES in the published composition rather than being dropped, (2) the near-miss
# still goes unflagged, and (3) a curator's explicit `remove` override -- and ONLY that -- still
# removes a confirmed phantom, including clearing its second-order REC-BAND-MISMATCH damage.
"""User Story 4 (as revised 2026-08-14): flag a candidate unit-size header row for a curator, but
never drop one automatically.

research D1's five-signal conjunction is applied over the datasheet's WHOLE composition row set
inside ``pipeline/curate/assemble.py::_flag_header_row_candidate`` (renamed from
``_refuse_header_row``) — never in ``pipeline/parse/composition_grammar.py``, which stays
mode-blind and unchanged, because the discriminating evidence (a first row whose count equals the
aggregate of the rows after it) does not exist inside a single line.

GF13/GF14/GF15 (Setup task T007) are the three fixtures this test proves against: two header
shapes measured on the eight originally-affected Kill Team datasheets, and the near-miss the
conjunction is designed NOT to flag. The live corpus's own T031 re-derivation
(``reports/composition-header-refusal/2026-08-14.md``) found that the eight all fail signal 4 in
practice (their variant rows overlap the base row, so the count does not sum) while the rows the
conjunction DID flag were three real duo-sheet first models — the false-positive risk research D8
named as R-1/R-A, materialised. Product Owner decision, 2026-08-14 (T061 review): the conjunction
never drops a row by itself any more.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from pipeline.curate.assemble import _composition_entries
from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import CompositionOverrideEntry
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


def _entries(
    detail_id: str, datasheet_id: str, authored: AuthoredContent | None = None
) -> tuple[list[CuratedCompositionEntry], list[str]]:
    entries, findings = _composition_entries(
        detail_id, datasheet_id, _detail(), authored or AuthoredContent(), curated_models(detail_id)
    )
    return entries, [finding.finding_code for finding in findings]


# --- both measured header shapes are FLAGGED, never dropped ---------------------------------


def test_two_row_header_candidate_survives_with_an_advisory_flag() -> None:
    # GF13: "9 Fenward Cohort" (header candidate) then "3 Fenward Sergeant" + "6 Fenward Trooper"
    # (3+6=9). The candidate is flagged, but it is NOT removed from the published composition —
    # only a curator's explicit override removes a row now (2026-08-14 PO decision).
    entries, finding_codes = _entries("GF13", "ds-fenward-cohort-alpha")
    assert [entry.model_name for entry in entries] == [
        "Fenward Cohort",
        "Fenward Sergeant",
        "Fenward Trooper",
    ]
    assert "CMP-HEADER-ROW" in finding_codes
    assert CATALOGUE["CMP-HEADER-ROW"].severity.value == "advisory"


def test_single_row_header_candidate_survives_with_an_advisory_flag() -> None:
    # GF14: "5 Fenward Vanguard Squad" (header candidate) then "5 Fenward Outrider" (5 == 5).
    entries, finding_codes = _entries("GF14", "ds-fenward-cohort-beta")
    assert [entry.model_name for entry in entries] == [
        "Fenward Vanguard Squad",
        "Fenward Outrider",
    ]
    assert "CMP-HEADER-ROW" in finding_codes


# --- the near-miss the conjunction is designed not to flag -----------------------------------


def test_near_miss_row_survives_and_is_never_flagged() -> None:
    # GF15: row 1 ("Fenward Relict Warden", 1) is a genuine model and IS the datasheet's own
    # first row -- it resolves, and its count does not sum its successors (1 != 8 + 7), so it is
    # never a candidate. Row 2 ("Fenward Relict Line", 8) is fixed-size, unlinkable, and
    # numerically equal to the sum of rows 1 and 3 (1 + 7 = 8) -- every signal the rule tests for
    # except the position gate, because the rule only ever examines the FIRST row. Nothing is
    # flagged; every genuine row resolves and survives, exactly as before this revision.
    entries, finding_codes = _entries("GF15", "ds-fenward-relict-watch")
    assert [entry.model_name for entry in entries] == [
        "Fenward Relict Warden",
        "Fenward Relict Line",
        "Fenward Relict Skirmisher",
    ]
    assert "CMP-HEADER-ROW" not in finding_codes


# --- a curator's `remove` override is the ONLY thing that still removes a row -----------------


def _remove_override(datasheet_id: str, line: int) -> AuthoredContent:
    return AuthoredContent(
        composition_overrides=(
            CompositionOverrideEntry.model_validate(
                {"datasheet_id": datasheet_id, "line": line, "remove": True}
            ),
        )
    )


def test_a_curator_remove_override_removes_a_confirmed_phantom_and_only_that_row() -> None:
    # GF13's flagged header row (line 1) is removed once a curator has confirmed it and written
    # the override; nothing else about the datasheet's composition moves.
    entries, finding_codes = _entries(
        "GF13", "ds-fenward-cohort-alpha", _remove_override("ds-fenward-cohort-alpha", 1)
    )
    assert [entry.model_name for entry in entries] == ["Fenward Sergeant", "Fenward Trooper"]
    # The row is gone before the flag function ever sees it -- no advisory for a row that no
    # longer exists, no CMP-UNRESOLVED either (it isn't unresolved, it's removed).
    assert "CMP-HEADER-ROW" not in finding_codes
    assert "CMP-UNRESOLVED" not in finding_codes


def test_remove_is_the_only_way_a_row_disappears_a_bare_flag_never_does_it() -> None:
    # Without an override the same fixture keeps its flagged row (proven above); WITH one it is
    # gone. The two tests together are the whole claim: flagging is advisory, removal is opt-in.
    with_flag_only, _ = _entries("GF13", "ds-fenward-cohort-alpha")
    with_override, _ = _entries(
        "GF13", "ds-fenward-cohort-alpha", _remove_override("ds-fenward-cohort-alpha", 1)
    )
    assert len(with_flag_only) == 3
    assert len(with_override) == 2


# --- the second-order damage a confirmed removal (not a bare flag) clears --------------------


def test_second_order_band_mismatch_advisory_persists_until_a_curator_removes_the_row() -> None:
    # research D1: "the phantom is summed by the composition-band reconciliation, inflating a
    # datasheet's model range and raising an advisory band-mismatch finding." Since the phantom
    # row is no longer auto-dropped, this damage now persists by default -- and clears only once
    # a curator's `remove` override actually takes it out of the composition.
    flagged_only, _ = _entries("GF13", "ds-fenward-cohort-alpha")
    removed, _ = _entries(
        "GF13", "ds-fenward-cohort-alpha", _remove_override("ds-fenward-cohort-alpha", 1)
    )

    flagged_findings = reconcile_composition_bands(
        datasheet_id="ds-fenward-cohort-alpha", entries=flagged_only, model_counts=[9]
    )
    removed_findings = reconcile_composition_bands(
        datasheet_id="ds-fenward-cohort-alpha", entries=removed, model_counts=[9]
    )

    assert len(flagged_findings) == 1
    assert flagged_findings[0].finding_code == "REC-BAND-MISMATCH"
    assert removed_findings == []
