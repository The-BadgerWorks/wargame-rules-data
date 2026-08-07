# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the pricing-context tests: the points
# source prices some units twice, and until this landed the second price arrived as an anonymous
# duplicate row and blocked the release as CON-DUPLICATE-KEY (docs/follow-ups.md item 8).
"""A price the points source states a **condition** for, and where it goes.

Two conditions exist in the source, and they reach `pricing_context` by two different routes:

* **the unit section heading.** One faction page carries every one of its units twice, the
  second copy under `EVERY MODEL HAS THE <KEYWORD> KEYWORD`, at different prices. Other pages
  use the same structure to *group* units by chapter, where no unit appears twice — so the
  heading's form, not its presence, is what decides.
* **the band label.** A unit whose bands hold the same number of models in different
  compositions cannot be told apart by a model count at all. What tells them apart is the model
  types some bands name and others do not.

Everything here is synthetic: invented factions, invented units, invented prices.
"""

from __future__ import annotations

from pipeline.build.bundle_emit import emit_bundle
from pipeline.curate.assemble import _army_context, _costs
from pipeline.models.source import MfmCostRow, MfmUnitCostBlock
from pipeline.normalize.numerics import model_count
from pipeline.validate.contract_checks import check_bundle_primary_keys, check_tier_projection
from tests import factories

ACQUISITION = "mfm-20260613T000000Z-deadbeef"


def _block(*, section: str = "", table: str = "YOUR UNIT COSTS", rows: list[tuple[str, int]]):  # type: ignore[no-untyped-def]
    return MfmUnitCostBlock(
        faction_slug="emberwrights",
        unit_display_name="ASH ENVOY",
        cost_table_label=table,
        cost_section_label=section,
        rows=[MfmCostRow(model_count_label=label, points=points) for label, points in rows],
    )


# --- the section heading: a condition, or just a group -------------------------------------------


def test_a_conditional_section_heading_becomes_a_pricing_context() -> None:
    assert _army_context("EVERY MODEL HAS THE ASHBOUND KEYWORD") == "every-model-has-ashbound"


def test_a_grouping_section_heading_is_not_a_condition_and_yields_none() -> None:
    """`EMBERWRIGHT CHAPTER` heads a section of units only that chapter fields — a partition."""
    assert _army_context("EMBERWRIGHT CHAPTER") is None
    assert _army_context("") is None


def test_the_same_unit_priced_by_two_sections_yields_two_distinguishable_rows() -> None:
    rows, _options, findings = _costs(
        [
            _block(rows=[("1 model", 55)]),
            _block(section="EVERY MODEL HAS THE ASHBOUND KEYWORD", rows=[("1 model", 65)]),
        ],
        ACQUISITION,
        "ds-ash-envoy",
    )

    assert findings == []
    assert [(row.model_count, row.points, row.pricing_context) for row in rows] == [
        (1, 55, None),
        (1, 65, "every-model-has-ashbound"),
    ]


def test_the_unconditional_price_keeps_its_meaning_by_carrying_no_context_at_all() -> None:
    """Absence is the whole compatibility argument: an untouched row says what it always said."""
    rows, _options, _findings = _costs([_block(rows=[("5 models", 90)])], ACQUISITION, "ds-x")
    assert [row.pricing_context for row in rows] == [None]


# --- the band label: a composite size, and two compositions of one size --------------------------


def test_a_composite_band_label_states_the_total_it_names_not_its_first_number() -> None:
    label = "1 Ash Marshal, 4 Emberkin, 5 Cinderguard"
    assert model_count(label, field="cost.model_count") == 10


def test_a_plain_band_label_is_unaffected_by_the_composite_rule() -> None:
    assert model_count("5 models", field="cost.model_count") == 5
    assert model_count("1 model", field="cost.model_count") == 1


def test_two_compositions_holding_the_same_model_count_are_told_apart_by_what_they_add() -> None:
    """`3 Envoys, 3 Wardogs` and `6 Envoys` are both six models, at two different prices."""
    rows, _options, _findings = _costs(
        [
            _block(
                rows=[
                    ("3 Ash Envoys", 85),
                    ("3 Ash Envoys, 3 Cinder Hounds", 115),
                    ("6 Ash Envoys", 170),
                    ("6 Ash Envoys, 6 Cinder Hounds", 230),
                ]
            )
        ],
        ACQUISITION,
        "ds-ash-envoy",
    )

    assert [(row.model_count, row.points, row.pricing_context) for row in rows] == [
        (3, 85, None),
        (6, 115, "with-cinder-hounds"),
        (6, 170, None),
        (12, 230, "with-cinder-hounds"),
    ]


def test_bands_a_model_count_already_separates_are_left_alone() -> None:
    """The context disambiguates; it does not reclassify. No collision, no context."""
    rows, _options, _findings = _costs(
        [
            _block(
                rows=[
                    ("1 Ash Marshal, 10 Emberkin", 45),
                    ("1 Ash Marshal, 20 Emberkin", 85),
                    ("10 Emberkin", 40),
                ]
            )
        ],
        ACQUISITION,
        "ds-emberkin",
    )

    assert [(row.model_count, row.pricing_context) for row in rows] == [
        (11, None),
        (21, None),
        (10, None),
    ]


def test_colliding_bands_with_nothing_to_tell_them_apart_are_left_to_block() -> None:
    """Guessing here would publish a price nobody chose (reference-db-schema.md §3.8)."""
    rows, _options, _findings = _costs(
        [_block(rows=[("5 models", 90)]), _block(rows=[("5 models", 100)])],
        ACQUISITION,
        "ds-ash-envoy",
    )
    assert [row.pricing_context for row in rows] == [None, None]

    bundle = emit_bundle(
        factories.snapshot(datasheets=[factories.datasheet(cost_rows=rows)]), factories.meta()
    )
    codes = {finding.finding_code for finding in check_bundle_primary_keys(bundle)}
    assert codes == {"CON-DUPLICATE-KEY"}


# --- where a context-qualified price goes in the bundle ------------------------------------------


def _bundle_with_context():  # type: ignore[no-untyped-def]
    costs = factories.costs(((1, 3, 60), (2, 3, 70))) + factories.costs(
        ((1, 3, 80), (2, 3, 95)), pricing_context="every-model-has-ashbound"
    )
    return emit_bundle(
        factories.snapshot(datasheets=[factories.datasheet(cost_rows=costs)]), factories.meta()
    )


def test_a_context_qualified_price_never_enters_the_two_arrays_an_old_consumer_reads() -> None:
    """Those arrays' primary keys are unchanged, so a v1.2.0 consumer still ingests the bundle."""
    bundle = _bundle_with_context()

    assert [row["points"] for row in bundle["datasheetCosts"]] == [60]
    assert sorted(row["points"] for row in bundle["datasheetCostTiers"]) == [60, 70]
    assert all("pricingContext" not in row for row in bundle["datasheetCostTiers"])


def test_the_context_array_carries_every_copy_index_with_the_condition_in_its_key() -> None:
    bundle = _bundle_with_context()

    assert [
        (row["pricingContext"], row["copyIndexMin"], row["points"])
        for row in bundle["datasheetCostContexts"]
    ] == [("every-model-has-ashbound", 1, 80), ("every-model-has-ashbound", 2, 95)]
    assert check_bundle_primary_keys(bundle) == []


def test_each_context_must_be_resolvable_on_its_own_rather_than_borrowing_a_tier() -> None:
    """A context is a self-contained price list: its own `copy_index_min = 1` row or nothing."""
    costs = factories.costs(((1, 3, 60),)) + factories.costs(
        ((2, 3, 95),), pricing_context="every-model-has-ashbound"
    )
    findings = check_tier_projection(
        factories.snapshot(datasheets=[factories.datasheet(cost_rows=costs)])
    )

    assert [finding.finding_code for finding in findings] == ["PRC-TIER-INCOMPLETE"]
    assert findings[0].detail["pricing_context"] == "every-model-has-ashbound"
