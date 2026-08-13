# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the bundle conformance tests (task
# T050): the emitted bundle validates against schemas/bundle.schema.json, carries one array per
# consumer table in lowerCamelCase sorted by primary key, omits absent optionals rather than
# emitting null, drops every curated-only field, and fails the build on an unmapped field.
# AI-Assisted: Claude Code (model: claude-opus-5) - Extended to 004-rules-data-enrichment's
# seven new arrays (004 task T066): each non-empty, sorted by its stated key, omitting absent
# optionals, and each of FR-033's three lockstep layers proven to fail on its own.
# AI-Assisted: Claude Code (model: claude-opus-5) - Extended again to 006-unit-loadout-fidelity's
# three new arrays (006 task T034): each non-empty and sorted by its COMPOSITE key, absent
# optionals proven absent somewhere rather than asserted over rows that all carry them, the two
# guarantee-12/13 invariants read off the bundle, and both lockstep layers re-proven over an
# element type and a curated model this feature added.
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

from collections.abc import Mapping
from typing import Final

import pytest

from pipeline.build import bundle_emit
from pipeline.build.bundle_emit import (
    FIELD_MAPPING,
    UnmappedFieldError,
    check_mapping_totality,
    emit_bundle,
)
from pipeline.schema_validation import SchemaValidationError, validate_bundle
from tests import factories
from tests.contract.enrichment_bundle import enriched_snapshot
from tests.contract.loadout_bundle import loadout_snapshot

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
    "datasheetCostContexts",
    "datasheetWargearOptions",
    "datasheetLeaderPairs",
    "datasheetDetachmentEligibility",
    # 004-rules-data-enrichment (004 task T032). Additive: bundleFormatVersion stays 1
    # because the layout rules are unchanged — one array per consumer table, sorted by
    # primary key, absent optionals omitted.
    "datasheetCompositions",
    "datasheetOptionGroups",
    "datasheetOptionChoices",
    # 004 task T040, contract §2.4. Snapshot-level rather than a datasheet child, because a
    # chapter keyword is resolved by keyword and not by the faction it hangs off.
    "chapterKeywords",
    # 004 task T048, contract §2.5. A faction may own more than one army rule.
    "factionRules",
    # 004 task T055, contract §2.6. A detachment may own more than one rule, so the RULE is
    # the key; the name is always carried and the summary appears only once approved.
    "detachmentRules",
    # 004 task T062, contract §2.7. An entry exists ONLY when authored and approved: an
    # unauthored keyword has no row and still appears on its datasheets unchanged.
    "keywordGlossary",
    # 006-unit-loadout-fidelity (006 task T006), contract §2. Three sibling arrays rather than
    # extra rows under an existing primary key: a v1.x consumer reading extra
    # datasheetOptionChoices rows would render one swap as four alternatives, which is a WRONG
    # reading rather than a lossy one.
    "datasheetOptionChoiceItems",
    "datasheetEquipmentGroups",
    "datasheetEquipmentItems",
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


# --- 004-rules-data-enrichment's seven new arrays (004 task T066, contract §2) --------------------

#: array -> the key tuple contract §2 states it is sorted by. Stated as data because the point is
#: that **every** new array declares one and is checked against it, not that a few of them are.
NEW_ARRAY_SORT_KEYS: Final[Mapping[str, tuple[str, ...]]] = {
    "datasheetCompositions": ("datasheetId", "line"),
    "datasheetOptionGroups": ("id",),
    "datasheetOptionChoices": ("id",),
    "chapterKeywords": ("keyword",),
    "factionRules": ("id",),
    "detachmentRules": ("id",),
    "keywordGlossary": ("keywordKey",),
}


@pytest.fixture(scope="module")
def enriched():  # type: ignore[no-untyped-def]
    """A bundle in which every one of the seven new arrays is **non-empty**.

    An ingestor ignores an empty array by accident as readily as by design, so the additions are
    checked against a bundle that actually carries them.
    """
    return emit_bundle(enriched_snapshot(), factories.meta())


def test_the_enriched_bundle_validates_against_the_schema(enriched) -> None:  # type: ignore[no-untyped-def]
    validate_bundle(enriched, source="enriched bundle")


@pytest.mark.parametrize("array", sorted(NEW_ARRAY_SORT_KEYS))
def test_every_new_array_carries_rows(array: str, enriched) -> None:  # type: ignore[no-untyped-def]
    assert enriched[array], f"{array} is empty, so nothing below it is really being tested"


@pytest.mark.parametrize(("array", "keys"), sorted(NEW_ARRAY_SORT_KEYS.items()))
def test_every_new_array_is_sorted_by_its_stated_key(  # type: ignore[no-untyped-def]
    array: str, keys: tuple[str, ...], enriched
) -> None:
    observed = [tuple(row[key] for key in keys) for row in enriched[array]]
    assert observed == sorted(observed)
    assert len(set(observed)) == len(observed), f"{array} has a duplicate primary key"


@pytest.mark.parametrize("array", sorted(NEW_ARRAY_SORT_KEYS))
def test_a_new_arrays_absent_optionals_are_omitted_never_null(array: str, enriched) -> None:  # type: ignore[no-untyped-def]
    for row in enriched[array]:
        assert all(value is not None for value in row.values()), array


def test_an_unpriced_option_choice_carries_no_points_delta_at_all(enriched) -> None:  # type: ignore[no-untyped-def]
    """Guarantee 10: emitting `0` for an unpriced choice is a contract violation, not a default."""
    unpriced = next(row for row in enriched["datasheetOptionChoices"] if row["id"].endswith("-2-1"))

    assert "pointsDelta" not in unpriced
    assert "pricedOptionId" not in unpriced


def test_an_unapproved_rule_ships_its_name_and_not_its_summary(enriched) -> None:  # type: ignore[no-untyped-def]
    draft = next(row for row in enriched["detachmentRules"] if row["name"] == "Sundering Tide")
    unwritten = next(row for row in enriched["detachmentRules"] if row["name"] == "Fenlight Muster")

    assert "summary" not in draft
    assert "summary" not in unwritten


def test_a_field_the_schema_does_not_describe_fails_the_build(enriched) -> None:  # type: ignore[no-untyped-def]
    """`additionalProperties: false` on every element type is the third of FR-033's three layers.

    The other two — `FIELD_MAPPING`'s totality and every model's `extra="forbid"` — are checked
    above. All three must move in lockstep or the build fails, which is the property that stops
    a new field reaching the app undescribed.
    """
    polluted = {**enriched, "detachmentRules": [{**enriched["detachmentRules"][0], "note": "x"}]}

    with pytest.raises(SchemaValidationError, match="note"):
        validate_bundle(polluted, source="polluted bundle")


def test_an_undescribed_array_fails_the_build(enriched) -> None:  # type: ignore[no-untyped-def]
    """`additionalProperties: false` at the root, too: a new array must be declared to ship."""
    with pytest.raises(SchemaValidationError, match="datasheetInventions"):
        validate_bundle({**enriched, "datasheetInventions": []}, source="polluted bundle")


# --- 006-unit-loadout-fidelity's three new arrays (006 task T034, contract §2) -------------------

#: array -> the key tuple `contracts/loadout-schema-delta.md` §2 states it is sorted by.
#:
#: Every one of the three is **composite**, which is the difference from `004`'s seven and the
#: reason they are restated here rather than folded into the map above: a single-column sort key
#: is checked by the same code but proves much less, because it cannot get the *tie-break* wrong.
#: `datasheetOptionChoiceItems` sorts by `(choiceId, role, itemIndex)` and its `role` component is
#: an enum sorted as a string — `granted` before `replaced` — so the replaced set of one choice
#: never interleaves with the granted bundle of another.
LOADOUT_ARRAY_SORT_KEYS: Final[Mapping[str, tuple[str, ...]]] = {
    "datasheetOptionChoiceItems": ("choiceId", "role", "itemIndex"),
    "datasheetEquipmentGroups": ("id",),
    "datasheetEquipmentItems": ("groupId", "itemIndex"),
}


@pytest.fixture(scope="module")
def loadout():  # type: ignore[no-untyped-def]
    """A bundle in which all three of `006`'s arrays are **non-empty** and all four columns set."""
    return emit_bundle(loadout_snapshot(), factories.meta())


def test_the_loadout_bundle_validates_against_the_extended_schema(loadout) -> None:  # type: ignore[no-untyped-def]
    validate_bundle(loadout, source="loadout bundle")


@pytest.mark.parametrize("array", sorted(LOADOUT_ARRAY_SORT_KEYS))
def test_every_loadout_array_carries_rows(array: str, loadout) -> None:  # type: ignore[no-untyped-def]
    assert loadout[array], f"{array} is empty, so nothing below it is really being tested"


@pytest.mark.parametrize(("array", "keys"), sorted(LOADOUT_ARRAY_SORT_KEYS.items()))
def test_every_loadout_array_is_sorted_by_its_stated_composite_key(  # type: ignore[no-untyped-def]
    array: str, keys: tuple[str, ...], loadout
) -> None:
    observed = [tuple(row[key] for key in keys) for row in loadout[array]]
    assert observed == sorted(observed)
    assert len(set(observed)) == len(observed), f"{array} has a duplicate primary key"


@pytest.mark.parametrize("array", sorted(LOADOUT_ARRAY_SORT_KEYS))
def test_a_loadout_arrays_absent_optionals_are_omitted_never_null(array: str, loadout) -> None:  # type: ignore[no-untyped-def]
    for row in loadout[array]:
        assert all(value is not None for value in row.values()), array


def test_the_absent_optionals_really_are_absent_somewhere(loadout) -> None:  # type: ignore[no-untyped-def]
    """The assertion above passes vacuously on a fixture where every optional is set.

    So each optional is named, and at least one row must be missing it. These are the three
    absences the feature's whole design rests on: an item whose name matched no weapon line ships
    with no `weaponLine` rather than a guessed one, a unit-wide equipment sentence carries no
    `modelName`, and a sentence that resolved to no single composition row carries no
    `compositionLine` (006 FR-007, FR-014, FR-015).
    """
    assert any("weaponLine" not in row for row in loadout["datasheetOptionChoiceItems"])
    assert any("weaponLine" not in row for row in loadout["datasheetEquipmentItems"])
    assert any("modelName" not in row for row in loadout["datasheetEquipmentGroups"])
    assert any("compositionLine" not in row for row in loadout["datasheetEquipmentGroups"])


def test_a_multi_item_side_carries_no_singular_column_at_all(loadout) -> None:  # type: ignore[no-untyped-def]
    """Guarantee 13, read off the bundle rather than off the model.

    Two granted items and two replaced items, and therefore neither `grantsWeaponLine` nor
    `replacesWeaponLine` — filling either from the first item is the exact truncation this
    feature exists to remove, and it would be invisible in a bundle that carried it.
    """
    swap = next(
        row for row in loadout["datasheetOptionChoices"] if row["id"] == "oc-fen-warden-3-1"
    )
    items = [row for row in loadout["datasheetOptionChoiceItems"] if row["choiceId"] == swap["id"]]

    assert "grantsWeaponLine" not in swap
    assert "replacesWeaponLine" not in swap
    assert sorted((row["role"], row["itemIndex"]) for row in items) == [
        ("granted", 1),
        ("granted", 2),
        ("replaced", 1),
        ("replaced", 2),
    ]


def test_a_sole_item_agrees_with_the_singular_column_it_mirrors(loadout) -> None:  # type: ignore[no-untyped-def]
    """Guarantee 12: the redundancy is an invariant, not a fixture accident.

    A `004`-era consumer reads `grantsWeaponLine`; a `006` consumer iterates the items. They must
    never disagree, which is what makes "iterate the items" a safe uniform read.
    """
    for choice in loadout["datasheetOptionChoices"]:
        for role, column in (("granted", "grantsWeaponLine"), ("replaced", "replacesWeaponLine")):
            side = [
                row
                for row in loadout["datasheetOptionChoiceItems"]
                if row["choiceId"] == choice["id"] and row["role"] == role
            ]
            if len(side) != 1:
                assert column not in choice, f"{choice['id']}.{column} with {len(side)} items"
                continue
            assert choice.get(column) == side[0].get("weaponLine")


def test_a_loadout_field_the_schema_does_not_describe_fails_the_build(loadout) -> None:  # type: ignore[no-untyped-def]
    """FR-033's third layer, on a `006` element type: `additionalProperties: false` holds here too.

    `test_the_mapping_is_total_for_every_curated_model` above is the first layer for the same
    three models — `FIELD_MAPPING` was extended for them in T012 — and every model's
    `extra="forbid"` is the second.
    """
    polluted = {
        **loadout,
        "datasheetEquipmentItems": [{**loadout["datasheetEquipmentItems"][0], "note": "x"}],
    }

    with pytest.raises(SchemaValidationError, match="note"):
        validate_bundle(polluted, source="polluted bundle")


def test_an_unmapped_loadout_field_fails_the_build_rather_than_being_dropped(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """The other side of the same lockstep: a curated field nobody decided about stops the build.

    Deliberately over `CuratedEquipmentItem` rather than over the datasheet again — the point is
    that the totality check reaches the models this feature *added*, not that it still reaches
    the ones it did not touch.
    """
    from pipeline.models.curated import CuratedEquipmentItem

    mapping = {
        model: (set(mapped), set(dropped)) for model, (mapped, dropped) in FIELD_MAPPING.items()
    }
    mapping[CuratedEquipmentItem][0].discard("item_name")
    monkeypatch.setattr(bundle_emit, "FIELD_MAPPING", mapping)

    with pytest.raises(UnmappedFieldError, match="item_name"):
        bundle_emit.check_mapping_totality()

    with pytest.raises(UnmappedFieldError, match="item_name"):
        emit_bundle(loadout_snapshot(), factories.meta())
