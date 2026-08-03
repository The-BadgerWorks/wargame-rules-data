# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the bundle conformance tests (task
# T050): the emitted bundle validates against schemas/bundle.schema.json, carries one array per
# consumer table in lowerCamelCase sorted by primary key, omits absent optionals rather than
# emitting null, drops every curated-only field, and fails the build on an unmapped field.
"""Tests for the published bundle's shape (`curated-snapshot-format.md` §3-§4).

The bundle exists so the app's ingestor is a mechanical array-to-table load with no reshaping.
That only holds while the arrays really are one-per-table with the columns the consumer contract
declares, so the schema is the assertion and this module is the proof the emitter satisfies it.

The two rules that are easy to break quietly, and are therefore tested hardest:

* **absence is meaningful** — an uncurated optional is *omitted*, never `null` and never a
  guessed default, because the app reports an unevaluated rule rather than enforcing a
  fabricated one (§5, FR-019); and
* **curated-only fields stop at this boundary** — `source_acquisition_id`, `force_disposition`,
  `is_unique`, `mfm_slug`, `detail_source_faction_id` and full provenance are producer-side, and
  an unmapped field is a build failure rather than a silent omission (§3).
"""

from __future__ import annotations

import pytest

from pipeline.build import bundle_emit
from pipeline.build.bundle_emit import (
    FIELD_MAPPING,
    UnmappedFieldError,
    check_mapping_totality,
    emit_bundle,
)
from pipeline.schema_validation import validate_bundle
from tests import factories

CONSUMER_ARRAYS = (
    "editions",
    "editionRules",
    "gameSizeRules",
    "factions",
    "detachments",
    "detachmentRestrictions",
    "enhancements",
    "enhancementEligibility",
    "datasheets",
    "datasheetKeywords",
    "datasheetModels",
    "datasheetWeapons",
    "datasheetAbilities",
    "datasheetCosts",
    "datasheetCostTiers",
    "datasheetWargearOptions",
    "datasheetLeaderPairs",
    "datasheetDetachmentEligibility",
)


@pytest.fixture
def bundle():  # type: ignore[no-untyped-def]
    return emit_bundle(factories.snapshot(), factories.meta())


def test_the_bundle_validates_against_its_schema(bundle) -> None:  # type: ignore[no-untyped-def]
    validate_bundle(bundle, source="emitted bundle")


def test_exactly_one_array_per_consumer_table_and_nothing_else(bundle) -> None:  # type: ignore[no-untyped-def]
    assert set(bundle) == {"bundleFormatVersion", "snapshotMeta", *CONSUMER_ARRAYS}


def test_every_array_is_present_even_when_empty(bundle) -> None:  # type: ignore[no-untyped-def]
    for name in CONSUMER_ARRAYS:
        assert isinstance(bundle[name], list), name


def test_datasheet_detachment_eligibility_is_always_present_and_always_empty(bundle) -> None:  # type: ignore[no-untyped-def]
    """No upstream join exists, so the contract's default applies: absence = legal anywhere."""
    assert bundle["datasheetDetachmentEligibility"] == []


def test_columns_are_lower_camel_case(bundle) -> None:  # type: ignore[no-untyped-def]
    for name in CONSUMER_ARRAYS:
        for row in bundle[name]:
            for column in row:
                assert "_" not in column, f"{name}.{column}"
                assert column[0].islower(), f"{name}.{column}"


def test_snapshot_meta_carries_the_five_columns_the_consumer_reads(bundle) -> None:  # type: ignore[no-untyped-def]
    assert set(bundle["snapshotMeta"]) == {
        "schemaContractVersion",
        "restrictionVocabularyVersion",
        "rulesVersionId",
        "publishedAt",
        "sourceNote",
    }


def test_arrays_are_sorted_by_their_primary_key() -> None:
    snapshot = factories.snapshot(
        factions=[factories.faction("f-zzz"), factories.faction("f-aaa")],
        datasheets=[
            factories.datasheet("ds-zzz", faction_id="f-aaa"),
            factories.datasheet("ds-aaa", faction_id="f-aaa"),
        ],
        detachments=[factories.detachment("d-anvil-vigil", faction_id="f-aaa")],
        enhancements=[factories.enhancement()],
    )
    bundle = emit_bundle(snapshot, factories.meta())

    assert [row["id"] for row in bundle["factions"]] == ["f-aaa", "f-zzz"]
    assert [row["id"] for row in bundle["datasheets"]] == ["ds-aaa", "ds-zzz"]
    assert [(row["datasheetId"], row["modelCount"]) for row in bundle["datasheetCosts"]] == sorted(
        (row["datasheetId"], row["modelCount"]) for row in bundle["datasheetCosts"]
    )


def test_absent_optionals_are_omitted_rather_than_null(bundle) -> None:  # type: ignore[no-untyped-def]
    (datasheet,) = bundle["datasheets"]
    assert "maxCopiesPerArmy" not in datasheet
    assert "damagedThreshold" not in datasheet
    assert "detailEditionCode" not in datasheet, "same-edition detail repeats nothing (§5)"

    def _no_nulls(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                assert value is not None, key
                _no_nulls(value)
        elif isinstance(node, list):
            for item in node:
                _no_nulls(item)

    _no_nulls(bundle)


def test_a_hybrid_edition_datasheet_states_its_detail_edition() -> None:
    snapshot = factories.snapshot(datasheets=[factories.datasheet(detail_edition_code="wh40k-10e")])
    (datasheet,) = emit_bundle(snapshot, factories.meta())["datasheets"]
    assert datasheet["detailEditionCode"] == "wh40k-10e"


def test_curated_only_fields_stop_at_this_boundary(bundle) -> None:  # type: ignore[no-untyped-def]
    (faction,) = bundle["factions"]
    assert "mfmSlug" not in faction
    assert "detailSourceFactionId" not in faction
    assert "provenance" not in faction

    (detachment,) = bundle["detachments"]
    assert "forceDisposition" not in detachment
    assert "isUnique" not in detachment

    for row in bundle["datasheetCosts"] + bundle["datasheetCostTiers"]:
        assert "sourceAcquisitionId" not in row


def test_edition_rule_values_are_canonical_json_strings(bundle) -> None:  # type: ignore[no-untyped-def]
    (rule,) = bundle["editionRules"]
    assert rule["valueJson"] == "true"


def test_ability_keys_are_expanded_into_per_datasheet_rows_with_summaries(bundle) -> None:  # type: ignore[no-untyped-def]
    (ability,) = bundle["datasheetAbilities"]
    assert ability["datasheetId"] == "ds-ember-sentinel"
    assert ability["abilityType"] == "core"
    assert ability["summary"]


def test_the_mapping_is_total_for_every_curated_model() -> None:
    """Every field of every curated model is either mapped to a column or explicitly dropped.

    This is what makes "an unmapped field is a build failure" true by construction: a field
    added to a curated model with no decision recorded about it fails here, not in review.
    """
    check_mapping_totality()


def test_an_unmapped_field_fails_the_build_rather_than_being_dropped_silently(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from pipeline.models.curated import CuratedDatasheet

    mapping = {
        model: (set(mapped), set(dropped)) for model, (mapped, dropped) in FIELD_MAPPING.items()
    }
    mapping[CuratedDatasheet][0].discard("role")
    monkeypatch.setattr(bundle_emit, "FIELD_MAPPING", mapping)

    with pytest.raises(UnmappedFieldError, match="role"):
        bundle_emit.check_mapping_totality()

    with pytest.raises(UnmappedFieldError, match="role"):
        emit_bundle(factories.snapshot(), factories.meta())


def test_bundle_format_version_is_distinct_from_the_consumer_contract_version(bundle) -> None:  # type: ignore[no-untyped-def]
    assert bundle["bundleFormatVersion"] == 1
    assert bundle["snapshotMeta"]["schemaContractVersion"] == 1
