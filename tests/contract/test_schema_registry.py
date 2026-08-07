# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts every authored JSON Schema is itself
# valid, loads through the cached registry, and enforces additionalProperties: false, so an
# unmapped field is a hard failure rather than a silent pass-through (tasks T032-T035).
"""The schemas are the "nowhere to land it" half of the IP boundary.

Control 1 of research D8 is that a violation has no field to occupy. That only holds if every
object in every schema really does refuse unknown properties — so this test walks the schema
documents themselves rather than trusting the review that wrote them.
"""

from __future__ import annotations

from typing import Any

import pytest
from jsonschema import Draft202012Validator

from pipeline.schema_validation import (
    BUNDLE_SCHEMA,
    CURATED_SCHEMAS,
    CURATION_SCHEMAS,
    SchemaValidationError,
    load_schema,
    schemas_dir,
    validate_authored,
    validate_bundle,
    validate_curated,
    validator_for,
)

ALL_SCHEMAS = [BUNDLE_SCHEMA, *CURATED_SCHEMAS.values(), *CURATION_SCHEMAS.values()]

PROVENANCE = {
    "points_source": "mfm",
    "points_edition_code": "wh40k-11e",
    "detail_source": "wahapedia",
    "detail_edition_code": "wh40k-10e",
}

DATASHEET = {
    "datasheet_id": "ds-storm-riders",
    "faction_id": "f-iron-wardens",
    "name": "Storm Riders",
    "costs": [
        {
            "model_count": 5,
            "copy_index_min": 1,
            "points": 90,
            "label": "5 models",
            "pricing_confidence": "verified",
        }
    ],
    "provenance": PROVENANCE,
}

EMPTY_BUNDLE: dict[str, Any] = {
    "bundleFormatVersion": 1,
    "snapshotMeta": {
        "schemaContractVersion": 1,
        "restrictionVocabularyVersion": 1,
        "rulesVersionId": "fixture-minimal",
        "publishedAt": "2026-06-13T00:00:00Z",
        "sourceNote": "synthetic fixture",
    },
    "editions": [],
    "editionRules": [],
    "gameSizeRules": [],
    "factions": [],
    "detachments": [],
    "detachmentRestrictions": [],
    "enhancements": [],
    "enhancementEligibility": [],
    "datasheets": [],
    "datasheetKeywords": [],
    "datasheetModels": [],
    "datasheetWeapons": [],
    "datasheetAbilities": [],
    "datasheetCosts": [],
    "datasheetCostTiers": [],
    "datasheetCostContexts": [],
    "datasheetWargearOptions": [],
    "datasheetLeaderPairs": [],
    "datasheetDetachmentEligibility": [],
    "datasheetCompositions": [],
    "datasheetOptionGroups": [],
    "datasheetOptionChoices": [],
    # 004 task T040. `chapterKeywords` is always present and empty until a curator classifies
    # something, exactly like every other array here.
    "chapterKeywords": [],
    # 004 task T048.
    "factionRules": [],
    # 004 task T055.
    "detachmentRules": [],
    # 004 task T062.
    "keywordGlossary": [],
}


def _objects(node: Any) -> list[dict[str, Any]]:
    """Every sub-schema that describes a JSON object with declared properties."""
    found: list[dict[str, Any]] = []
    if isinstance(node, dict):
        if node.get("type") == "object" and "properties" in node:
            found.append(node)
        for value in node.values():
            found.extend(_objects(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_objects(item))
    return found


@pytest.mark.parametrize("relative", sorted(ALL_SCHEMAS))
def test_each_schema_is_a_valid_draft_2020_12_schema(relative: str) -> None:
    Draft202012Validator.check_schema(dict(load_schema(relative)))


@pytest.mark.parametrize("relative", sorted(ALL_SCHEMAS))
def test_each_schema_carries_an_ai_assisted_comment_and_an_id(relative: str) -> None:
    schema = load_schema(relative)
    assert "AI-Assisted" in str(schema.get("_comment", "")), "Principle 16 header (JSON: _comment)"
    assert str(schema.get("$id", "")).endswith(relative)


@pytest.mark.parametrize("relative", sorted(ALL_SCHEMAS))
def test_every_object_refuses_unknown_properties(relative: str) -> None:
    for node in _objects(dict(load_schema(relative))):
        assert node.get("additionalProperties") is False, (
            f"{relative}: an object schema permits unmapped fields, which is exactly the "
            "silent pass-through the schemas exist to prevent"
        )


@pytest.mark.parametrize("relative", sorted(ALL_SCHEMAS))
def test_each_schema_loads_through_the_cached_registry(relative: str) -> None:
    assert isinstance(validator_for(relative), Draft202012Validator)


def test_the_schema_files_on_disk_are_exactly_the_ones_declared() -> None:
    on_disk = {
        p.relative_to(schemas_dir()).as_posix() for p in schemas_dir().rglob("*.schema.json")
    }
    assert on_disk == set(ALL_SCHEMAS)


def test_a_curated_datasheet_validates() -> None:
    validate_curated("datasheet", DATASHEET)


def test_an_unmapped_field_fails_the_curated_datasheet() -> None:
    with pytest.raises(SchemaValidationError, match="Additional properties"):
        validate_curated("datasheet", {**DATASHEET, "lore": "not a column"})


def test_a_datasheet_with_no_cost_row_fails_the_schema() -> None:
    with pytest.raises(SchemaValidationError):
        validate_curated("datasheet", {**DATASHEET, "costs": []})


def test_a_null_optional_fails_because_absence_is_expressed_by_omission() -> None:
    with pytest.raises(SchemaValidationError):
        validate_curated("datasheet", {**DATASHEET, "max_copies_per_army": None})


def test_the_empty_bundle_skeleton_validates() -> None:
    validate_bundle(EMPTY_BUNDLE)


def test_the_bundle_requires_every_consumer_table_array() -> None:
    missing = {k: v for k, v in EMPTY_BUNDLE.items() if k != "datasheetCostTiers"}
    with pytest.raises(SchemaValidationError, match="datasheetCostTiers"):
        validate_bundle(missing)


def test_datasheet_detachment_eligibility_is_always_empty() -> None:
    populated = {
        **EMPTY_BUNDLE,
        "datasheetDetachmentEligibility": [
            {"datasheetId": "ds-a", "detachmentId": "d-b", "isAllowed": True}
        ],
    }
    with pytest.raises(SchemaValidationError):
        validate_bundle(populated)


def test_an_out_of_vocabulary_restriction_type_fails_the_bundle() -> None:
    populated = {
        **EMPTY_BUNDLE,
        "detachmentRestrictions": [
            {
                "id": "r-1",
                "editionId": "ed-wh40k-11e",
                "restrictionType": "no_such_rule",
                "paramsJson": "{}",
                "messageTemplate": "{unit} is not allowed",
            }
        ],
    }
    with pytest.raises(SchemaValidationError):
        validate_bundle(populated)


def test_authored_files_validate_and_reject_typos() -> None:
    validate_authored(
        "faction-map",
        [
            {
                "mfm_slug": "iron-wardens",
                "faction_id": "f-iron-wardens",
                "detail_source_faction_id": "IW",
            }
        ],
    )
    with pytest.raises(SchemaValidationError, match="Additional properties"):
        validate_authored(
            "faction-map",
            [
                {
                    "mfm_slug": "iron-wardens",
                    "faction_id": "f-iron-wardens",
                    "detail_source_faction_id": "IW",
                    "detial_source_faction_id": "typo",
                }
            ],
        )


def test_an_unapproved_review_state_outside_the_vocabulary_is_refused() -> None:
    with pytest.raises(SchemaValidationError):
        validate_authored(
            "abilities",
            [
                {
                    "ability_key": "core:deep-strike",
                    "name": "Deep Strike",
                    "summary": 'Set up in reserve; arrive more than 9" from enemies.',
                    "review_state": "rubber-stamped",
                    "mechanic_digest": "hmac:deadbeef",
                }
            ],
        )


def test_an_unknown_schema_name_is_a_hard_failure() -> None:
    with pytest.raises(SchemaValidationError, match="no curated schema named"):
        validate_curated("not-a-thing", {})
