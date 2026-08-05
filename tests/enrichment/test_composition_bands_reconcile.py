# AI-Assisted: Claude Code (model: claude-opus-5) - FR-009's contract (004 task T025): a
# composition disagreeing with the points source's model-count bands is reported with BOTH
# values, the points bands stay authoritative for pricing, and neither side is adjusted.
"""What happens when the two sources describe different units.

The failure this prevents is quiet and expensive: a band that prices a squad size the unit cannot
legally be produces an army list that validates cleanly and is illegal on the table. The failure
it must *not* introduce is quieter still — clamping one side into the other would leave a
snapshot in which every value is internally consistent and one of them is invented.
"""

from __future__ import annotations

from pipeline.models.curated import CuratedCompositionEntry
from pipeline.models.findings import Severity
from pipeline.reconcile.composition_bands import (
    reconcile_composition_bands,
    representable_range,
)
from pipeline.report.catalogue import CATALOGUE

DATASHEET = "ds-sedgeward-conclave"


def entries(*pairs: tuple[int, int]) -> list[CuratedCompositionEntry]:
    return [
        CuratedCompositionEntry(
            line=index, model_name=f"Sedgeward Model {index}", min_count=low, max_count=high
        )
        for index, (low, high) in enumerate(pairs, start=1)
    ]


def test_the_representable_range_sums_the_unit_s_parts() -> None:
    # A composition names the unit's *parts*: a one-model leader plus a four-to-nine-model body
    # is fieldable at five to ten models, and it is that total the points source prices.
    assert representable_range(entries((1, 1), (4, 9))) == (5, 10)


def test_a_band_inside_the_range_reports_nothing() -> None:
    assert (
        reconcile_composition_bands(
            datasheet_id=DATASHEET, entries=entries((1, 1), (4, 9)), model_counts=[5, 10]
        )
        == []
    )


def test_a_band_outside_the_range_is_reported_with_both_values() -> None:
    findings = reconcile_composition_bands(
        datasheet_id=DATASHEET, entries=entries((1, 1), (4, 4)), model_counts=[5, 12]
    )
    (finding,) = findings
    assert finding.detail["model_count"] == 12
    assert (finding.detail["composition_min"], finding.detail["composition_max"]) == (5, 5)
    assert DATASHEET in finding.entity_refs


def test_the_mismatch_is_advisory_so_the_points_bands_stay_authoritative() -> None:
    # FR-009: the points bands remain authoritative for pricing. A blocking finding here would
    # make a detail-source disagreement able to withhold a price the publisher published.
    assert CATALOGUE["REC-BAND-MISMATCH"].severity is Severity.ADVISORY
    findings = reconcile_composition_bands(
        datasheet_id=DATASHEET, entries=entries((1, 1)), model_counts=[3]
    )
    assert all(finding.severity is Severity.ADVISORY for finding in findings)


def test_neither_side_is_adjusted_to_agree_with_the_other() -> None:
    composition = entries((1, 1), (4, 4))
    counts = [5, 12]
    reconcile_composition_bands(datasheet_id=DATASHEET, entries=composition, model_counts=counts)
    assert [(e.min_count, e.max_count) for e in composition] == [(1, 1), (4, 4)]
    assert counts == [5, 12]


def test_a_datasheet_with_no_resolved_composition_reports_no_band_mismatch() -> None:
    # A band cannot be mismatched against a range that was never established, and saying so
    # anyway would double-count one defect into two categories. The free-text reconciliation in
    # `reconcile/bands.py` is what still speaks for that datasheet.
    assert reconcile_composition_bands(datasheet_id=DATASHEET, entries=[], model_counts=[5]) == []


def test_one_finding_per_band_not_per_composition_line() -> None:
    findings = reconcile_composition_bands(
        datasheet_id=DATASHEET, entries=entries((1, 1), (1, 1), (1, 1)), model_counts=[10, 20, 20]
    )
    assert len(findings) == 2  # deduplicated by band, in sorted order
    assert [f.detail["model_count"] for f in findings] == [10, 20]


def test_reconciliation_is_deterministic() -> None:
    args = {
        "datasheet_id": DATASHEET,
        "entries": entries((1, 1), (4, 9)),
        "model_counts": [20, 3, 20],
    }
    assert reconcile_composition_bands(**args) == reconcile_composition_bands(**args)  # type: ignore[arg-type]
