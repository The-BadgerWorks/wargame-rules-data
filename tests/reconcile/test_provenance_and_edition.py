# AI-Assisted: Claude Code (model: claude-opus-5) - Provenance and hybrid-edition reporting tests
# (task T083): every published datasheet carries source and edition provenance, the mismatch
# report leads with count AND proportion, and aligning the two declared editions empties it with
# no other behaviour change (FR-058..FR-061, SC-013).
"""Provenance, and the hybrid-edition report.

At launch a hybrid entity is the **normal** case, not an edge case: the points source is 11th
Edition and the detail export is 10th (research §0.1). That is exactly why the report has to
state a *proportion* and not a list — "1 487 hybrid entities" is unreadable, "100% of the
release" is a decision an approver can actually make.

The last test here is the one that matters when the export catches up: aligning the two declared
editions must empty the report and change nothing else. If anything else moves, the edition
codes have quietly become a behavioural switch rather than a declaration (FR-061).
"""

from __future__ import annotations

from pipeline.report.edition_mismatch import (
    hybrid_datasheets,
    render_edition_mismatch,
    render_unverified_pricing,
)
from tests import factories


def snapshot_with(detail_edition: str, *, hybrid_count: int = 1, total: int = 4):
    datasheets = [
        factories.datasheet(
            f"ds-unit-{index}",
            detail_edition_code=detail_edition if index < hybrid_count else factories.EDITION_CODE,
        )
        for index in range(total)
    ]
    return factories.snapshot(datasheets=datasheets)


def test_every_published_datasheet_carries_source_and_edition_provenance() -> None:
    snapshot = snapshot_with("wh40k-10e", hybrid_count=4, total=4)

    for datasheet in snapshot.datasheets:
        assert datasheet.provenance.points_source.value
        assert datasheet.provenance.points_edition_code
        assert datasheet.provenance.detail_source.value
        assert datasheet.provenance.detail_edition_code


def test_hybrid_entities_are_named_exactly_once_each() -> None:
    snapshot = snapshot_with("wh40k-10e", hybrid_count=2, total=5)

    hybrids = hybrid_datasheets(snapshot)

    assert [d.datasheet_id for d in hybrids] == ["ds-unit-0", "ds-unit-1"]


def test_the_edition_mismatch_report_states_count_and_proportion_before_any_enumeration() -> None:
    snapshot = snapshot_with("wh40k-10e", hybrid_count=2, total=5)

    rendered = render_edition_mismatch(snapshot)

    count_position = rendered.index("2")
    proportion_position = rendered.index("40.0%")
    first_entity_position = rendered.index("ds-unit-0")
    assert count_position < first_entity_position
    assert proportion_position < first_entity_position
    assert "wh40k-10e" in rendered


def test_aligning_the_declared_editions_empties_the_report() -> None:
    aligned = snapshot_with(factories.EDITION_CODE, hybrid_count=0, total=5)

    assert hybrid_datasheets(aligned) == []
    rendered = render_edition_mismatch(aligned)
    assert "0" in rendered
    assert "ds-unit-0" not in rendered, "an aligned release names no hybrid entity"


def test_aligning_the_editions_changes_nothing_but_the_report() -> None:
    hybrid = snapshot_with("wh40k-10e", hybrid_count=5, total=5)
    aligned = snapshot_with(factories.EDITION_CODE, hybrid_count=0, total=5)

    def mechanical(snapshot) -> list[tuple[str, str, tuple[int, ...]]]:
        return [
            (d.datasheet_id, d.name, tuple(sorted(c.points for c in d.costs)))
            for d in snapshot.datasheets
        ]

    assert mechanical(hybrid) == mechanical(aligned), (
        "the declared edition is a statement about provenance, never a behavioural switch"
    )


def test_the_unverified_pricing_report_leads_with_count_and_proportion() -> None:
    from pipeline.models.provenance import PricingConfidence, PricingConfidenceState

    unverified = factories.datasheet("ds-slate-lantern").model_copy(
        update={
            "pricing_confidence": PricingConfidence(
                state=PricingConfidenceState.UNVERIFIED,
                unverified_since_version="mfm-2026-05",
                consecutive_unverified_releases=2,
                last_verified_version="mfm-2026-04",
            )
        }
    )
    snapshot = factories.snapshot(datasheets=[unverified, factories.datasheet("ds-slate-sentinel")])

    rendered = render_unverified_pricing(snapshot)

    assert rendered.index("50.0%") < rendered.index("ds-slate-lantern")
    assert "mfm-2026-05" in rendered
    assert "2" in rendered
