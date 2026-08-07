# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the primary-key uniqueness tests for
# the emitted bundle, after the first real-bundle consumer-compat run found five classes of
# duplicate consumer primary key in the published release and in the 004 candidate
# (docs/follow-ups.md item 8). Two layers, deliberately separated: the emitter collapses rows
# that are byte-identical, and validation refuses rows that collide on the key and disagree.
"""One row per consumer primary key, or a blocking finding saying why not.

`reference-db-schema.md` §3 declares a `PRIMARY KEY` on every table, and the producer's
obligation is to "emit a bundle from which exactly this schema can be built with no additional
input". Two rows sharing a key make that false: an ingestor either fails, or — where a key
component is NULL and SQLite's own uniqueness therefore does not bite — silently stores both and
shows a player the same thing twice.

The split between the two layers is the whole design, and it is not symmetric on purpose:

* **byte-identical duplicates collapse, silently.** Two identical rows and one identical row
  ingest to the same table content, so dropping the second loses nothing at all. This is the
  common case: one source page printing the same keyword block twice.
* **rows that collide and disagree are never resolved by the emitter.** Choosing between 55 and
  65 points for one band is a content decision, and picking one silently is exactly how a wrong
  price reaches a player with nothing in the report to say so. Both rows still ship, and
  `CON-DUPLICATE-KEY` blocks publication until a human decides.

The fixtures here are synthetic in the usual way — invented names, invented values.
"""

from __future__ import annotations

from typing import Any

from pipeline.build.bundle_emit import emit_bundle
from pipeline.models.curated import CuratedDatasheetCost, CuratedKeyword, PricingConfidenceState
from pipeline.models.findings import Severity
from pipeline.report.catalogue import severity_of
from pipeline.validate.contract_checks import (
    CONSUMER_PRIMARY_KEYS,
    check_bundle_primary_keys,
)
from tests import factories


def _cost(model_count: int, points: int, label: str) -> CuratedDatasheetCost:
    return CuratedDatasheetCost(
        model_count=model_count,
        copy_index_min=1,
        points=points,
        label=label,
        pricing_confidence=PricingConfidenceState.VERIFIED,
    )


def _bundle(**datasheet_fields: Any) -> dict[str, Any]:
    """One synthetic datasheet with the given fields replaced, emitted whole."""
    datasheet = factories.datasheet().model_copy(update=datasheet_fields)
    return emit_bundle(factories.snapshot(datasheets=[datasheet]), factories.meta())


# --- the emitter collapses what is genuinely the same row ----------------------------------------


def test_byte_identical_keyword_rows_collapse_to_one() -> None:
    keyword = CuratedKeyword(keyword="Emberbound", is_faction_keyword=False)
    bundle = _bundle(keywords=[keyword, keyword])

    assert len(bundle["datasheetKeywords"]) == 1


def test_a_null_key_component_does_not_let_a_duplicate_through() -> None:
    """`model_scope` is part of the key and is usually absent.

    SQLite treats NULLs in a unique index as distinct, so a consumer building the declared
    schema would accept both rows and show the keyword twice. The emitter must not rely on the
    ingestor catching this, because the ingestor cannot.
    """
    keyword = CuratedKeyword(keyword="Emberbound", is_faction_keyword=False)
    rows = _bundle(keywords=[keyword, keyword])["datasheetKeywords"]

    assert all("modelScope" not in row for row in rows)
    assert len(rows) == 1


def test_byte_identical_cost_rows_collapse_in_both_the_cost_and_the_tier_array() -> None:
    row = _cost(5, 90, "5 models")
    bundle = _bundle(costs=[row, row])

    assert len(bundle["datasheetCosts"]) == 1
    assert len(bundle["datasheetCostTiers"]) == 1


def test_rows_that_disagree_are_both_kept() -> None:
    """The emitter never picks. Dropping one here would publish a price nobody chose."""
    bundle = _bundle(costs=[_cost(1, 55, "1 model"), _cost(1, 65, "1 model")])

    assert sorted(row["points"] for row in bundle["datasheetCosts"]) == [55, 65]


# --- and validation refuses exactly those ---------------------------------------------------------


def test_a_disagreeing_collision_blocks_in_both_projections_of_the_price() -> None:
    """`datasheetCosts` is the first-copy slice of `datasheetCostTiers`, so one conflict is two.

    Reporting both is right rather than noisy: guarantee 7 makes the two arrays one fact told
    twice, and a curator who fixed only the array named in a single finding would leave the
    other carrying the collision.
    """
    bundle = _bundle(costs=[_cost(1, 55, "1 model"), _cost(1, 65, "1 model")])

    findings = check_bundle_primary_keys(bundle)

    assert [f.detail["array"] for f in findings] == ["datasheetCostTiers", "datasheetCosts"]
    assert all(f.severity.value == "blocking" for f in findings)
    assert all(f.detail["row_count"] == 2 for f in findings)


def _collision_bundle(keys: tuple[str, ...], *, datasheet_ids: tuple[str, ...] = ("ds-a",)) -> Any:
    """Every named datasheet binds every named ability key, and all of them share one name."""
    summaries = factories.summaries(keys)
    for key, summary in summaries.items():
        summaries[key] = summary.model_copy(
            update={"name": "Ember Stride", "summary": f"Invented summary for {key}."}
        )
    return emit_bundle(
        factories.snapshot(
            datasheets=[
                factories.datasheet(datasheet_id=ds, ability_keys=keys) for ds in datasheet_ids
            ],
            ability_summaries=summaries,
        ),
        factories.meta(),
    )


def test_one_ability_classified_twice_resolves_to_the_narrower_record() -> None:
    """The candidate's own case, in miniature (`docs/follow-ups.md` item 8, class 2c).

    `datasheet_ability`'s key is `(datasheet_id, name)` and carries no `ability_type`, so a card
    that prints one ability under two classifications offers two rows the app cannot hold. It is
    a collision the tree cannot show, because the tree keys abilities per *ability* and the
    expansion into per-binding rows happens at emission.

    The Product Owner's 2026-08-06 ruling is that the narrower record wins: an author who wrote
    a record for *this datasheet* was answering the question this row asks.
    """
    bundle = _collision_bundle(("core:ember-stride", "datasheet:ember-stride"))

    rows = bundle["datasheetAbilities"]
    assert [(row["abilityType"], row["summary"]) for row in rows] == [
        ("datasheet", "Invented summary for datasheet:ember-stride.")
    ]
    assert check_bundle_primary_keys(bundle) == []


def test_the_core_record_still_serves_every_datasheet_that_did_not_override_it() -> None:
    """Precedence is per datasheet. The core record is not edited, dropped, or narrowed."""
    bundle = emit_bundle(
        factories.snapshot(
            datasheets=[
                factories.datasheet(
                    datasheet_id="ds-a",
                    ability_keys=("core:ember-stride", "datasheet:ember-stride"),
                ),
                factories.datasheet(datasheet_id="ds-b", ability_keys=("core:ember-stride",)),
            ],
            ability_summaries={
                key: summary.model_copy(update={"name": "Ember Stride", "summary": f"For {key}."})
                for key, summary in factories.summaries(
                    ("core:ember-stride", "datasheet:ember-stride")
                ).items()
            },
        ),
        factories.meta(),
    )

    assert {(row["datasheetId"], row["abilityType"]) for row in bundle["datasheetAbilities"]} == {
        ("ds-a", "datasheet"),
        ("ds-b", "core"),
    }


def test_a_collision_with_no_single_narrowest_record_still_blocks() -> None:
    """Precedence resolves a disagreement *between* scopes, never one inside a single scope."""
    bundle = _collision_bundle(("datasheet:ember-stride", "datasheet:ash-stride"))

    assert len(bundle["datasheetAbilities"]) == 2
    (finding,) = check_bundle_primary_keys(bundle)
    assert finding.detail["array"] == "datasheetAbilities"
    assert severity_of(finding.finding_code) is Severity.BLOCKING


def test_a_clean_bundle_raises_nothing() -> None:
    assert check_bundle_primary_keys(_bundle()) == []


def test_the_finding_names_the_key_but_never_the_disagreeing_values() -> None:
    """A finding is a report row, not a data channel: it says *which* row, not what is in it."""
    bundle = _bundle(costs=[_cost(1, 55, "1 model"), _cost(1, 65, "1 model")])
    findings = check_bundle_primary_keys(bundle)

    assert all(f.detail["key"] for f in findings)
    assert all("55" not in str(f.detail) and "65" not in str(f.detail) for f in findings)


def test_every_emitted_array_has_a_declared_key() -> None:
    """A new array with no key would be silently exempt from the whole guarantee."""
    bundle = _bundle()
    arrays = {name for name, value in bundle.items() if isinstance(value, list)}

    assert arrays <= set(CONSUMER_PRIMARY_KEYS)


def test_the_code_is_blocking_in_the_catalogue() -> None:
    assert severity_of("CON-DUPLICATE-KEY").value == "blocking"
