# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the tier-projection tests (task T049):
# datasheet_cost is exactly the copy_index_min = 1 projection of datasheet_cost_tier in both
# directions, and an unresolvable tier set raises the blocking PRC-TIER-INCOMPLETE.
"""Tests for consumer-contract guarantee 7 (`reference-db-schema.md` v1.2.0 §3.1, C1/R2).

The redundancy between `datasheet_cost` and `datasheet_cost_tier` is deliberate: it is what
lets a v1.1.0 app keep reading `datasheet_cost` unchanged while a v1.2.0 app prices escalating
units exactly. Redundancy only helps while it is *exact*, so the projection is asserted in both
directions rather than one.

`PRC-TIER-INCOMPLETE` is blocking because the alternative is worse than refusing to publish: a
tier set with a hole prices some copy of some unit by falling off the end of a lookup, and the
player finds out at a tournament.
"""

from __future__ import annotations

from pipeline.build.bundle_emit import emit_bundle
from pipeline.models.findings import Severity
from pipeline.report.catalogue import severity_of
from pipeline.validate.contract_checks import check_snapshot
from tests import factories


def _codes(snapshot):  # type: ignore[no-untyped-def]
    return [f.finding_code for f in check_snapshot(snapshot, factories.meta())]


ESCALATING = ((1, 5, 90), (1, 10, 175), (3, 5, 100), (3, 10, 195))


def test_costs_are_the_first_copy_projection_of_the_tiers() -> None:
    snapshot = factories.snapshot(
        datasheets=[factories.datasheet(cost_rows=factories.costs(ESCALATING))]
    )
    bundle = emit_bundle(snapshot, factories.meta())

    assert [(r["modelCount"], r["points"]) for r in bundle["datasheetCosts"]] == [
        (5, 90),
        (10, 175),
    ]
    assert [
        (r["modelCount"], r["copyIndexMin"], r["points"]) for r in bundle["datasheetCostTiers"]
    ] == [(5, 1, 90), (5, 3, 100), (10, 1, 175), (10, 3, 195)]


def test_the_projection_holds_in_the_other_direction_too() -> None:
    """Every emitted cost row has a matching first-copy tier row with identical points and label."""
    snapshot = factories.snapshot(
        datasheets=[factories.datasheet(cost_rows=factories.costs(ESCALATING))]
    )
    bundle = emit_bundle(snapshot, factories.meta())

    tiers = {
        (r["datasheetId"], r["modelCount"]): r
        for r in bundle["datasheetCostTiers"]
        if r["copyIndexMin"] == 1
    }
    assert len(tiers) == len(bundle["datasheetCosts"])
    for cost in bundle["datasheetCosts"]:
        tier = tiers[(cost["datasheetId"], cost["modelCount"])]
        assert (tier["points"], tier["label"]) == (cost["points"], cost["label"])
        assert tier["pricingConfidence"] == cost["pricingConfidence"]


def test_a_datasheet_with_no_escalating_price_still_has_one_tier_row_per_cost_row() -> None:
    bundle = emit_bundle(factories.snapshot(), factories.meta())
    assert len(bundle["datasheetCostTiers"]) == len(bundle["datasheetCosts"])
    assert {r["copyIndexMin"] for r in bundle["datasheetCostTiers"]} == {1}


def test_a_tier_for_one_model_count_but_not_another_is_blocking() -> None:
    """`{5: [1, 3], 10: [1]}` — the 10-model third copy would fall off the end of the lookup."""
    lopsided = ((1, 5, 90), (1, 10, 175), (3, 5, 100))
    snapshot = factories.snapshot(
        datasheets=[factories.datasheet(cost_rows=factories.costs(lopsided))]
    )
    assert "PRC-TIER-INCOMPLETE" in _codes(snapshot)
    assert severity_of("PRC-TIER-INCOMPLETE") is Severity.BLOCKING


def test_a_missing_first_copy_row_is_blocking() -> None:
    """Without a `copy_index_min = 1` row the lookup for copy 1 has no answer at all."""
    headless = ((3, 5, 100),)
    snapshot = factories.snapshot(
        datasheets=[factories.datasheet(cost_rows=factories.costs(headless))]
    )
    assert "PRC-TIER-INCOMPLETE" in _codes(snapshot)


def test_the_finding_names_the_datasheet_and_the_counts_and_nothing_else() -> None:
    lopsided = ((1, 5, 90), (1, 10, 175), (3, 5, 100))
    snapshot = factories.snapshot(
        datasheets=[factories.datasheet(cost_rows=factories.costs(lopsided))]
    )
    finding = next(
        f
        for f in check_snapshot(snapshot, factories.meta())
        if f.finding_code == "PRC-TIER-INCOMPLETE"
    )
    assert finding.detail["datasheet_id"] == "ds-ember-sentinel"
    assert finding.detail["model_count"] == 10


def test_a_consistent_escalating_set_raises_nothing() -> None:
    snapshot = factories.snapshot(
        datasheets=[factories.datasheet(cost_rows=factories.costs(ESCALATING))]
    )
    assert "PRC-TIER-INCOMPLETE" not in _codes(snapshot)
