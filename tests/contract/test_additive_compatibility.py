# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the additive-compatibility proof (004
# task T065): the enriched bundle schema compared field by field against the frozen
# pre-enrichment baseline, failing on any rename, reshape, reorder, or optionality change to an
# existing class, with bundleFormatVersion and snapshotMeta.schemaContractVersion unchanged
# (004 FR-031, FR-032, contracts/bundle-schema-delta.md §1).
"""Nothing existing moved. Proven by comparison, not by assertion.

`contracts/bundle-schema-delta.md` §1 makes a claim about a document nobody in this repository
consumes: **every change is additive, so the currently released app build and the currently
released site build read an enriched snapshot with no release of their own.** The failure mode is
brutal and remote — a renamed field or a newly-required column does not fail anything here, it
fails in an app that cannot ingest a published version, after publication.

So the claim is checked the only way it can be checked from this side: against
`fixtures/contract/bundle.schema.pre-enrichment.json`, a frozen copy of the schema as the
released consumers were built against it. Every existing array, every existing property, its
type, its enumerated values, its required-ness, and the **order** of both are compared. The seven
new arrays and three new columns are permitted; nothing else is.

**When this fails, the schema is wrong, not the baseline.** Editing the baseline to match would
delete the only evidence that anything moved.

`bundleFormatVersion` and `snapshotMeta.schemaContractVersion` get their own assertions because
`003`'s fetch-time checks assert on both, and a bump of either is a release of every consumer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pipeline.build.bundle_emit import BUNDLE_FORMAT_VERSION, emit_bundle
from pipeline.schema_validation import validate_bundle
from pipeline.validate.contract_checks import SCHEMA_CONTRACT_VERSION
from tests import factories

ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = ROOT / "fixtures" / "contract" / "bundle.schema.pre-enrichment.json"
SCHEMA_PATH = ROOT / "schemas" / "bundle.schema.json"

#: The seven arrays `004-rules-data-enrichment` adds (contract §2). Everything outside this set
#: must be byte-for-byte what the released consumers were built against.
NEW_ARRAYS: frozenset[str] = frozenset(
    {
        "datasheetCompositions",
        "datasheetOptionGroups",
        "datasheetOptionChoices",
        "chapterKeywords",
        "factionRules",
        "detachmentRules",
        "keywordGlossary",
    }
)

#: The three additive columns (contract §3), as ``array -> column``. Each is **optional** and
#: omitted when absent, so every existing row that acquires no value is byte-identical.
NEW_COLUMNS: dict[str, str] = {
    "datasheets": "wargearOptionState",
    "datasheetKeywords": "keywordClass",
    "factions": "armyRuleState",
}


def _schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


@pytest.fixture(scope="module")
def baseline() -> dict[str, Any]:
    return _schema(BASELINE_PATH)


@pytest.fixture(scope="module")
def enriched() -> dict[str, Any]:
    return _schema(SCHEMA_PATH)


def _arrays(schema: dict[str, Any]) -> dict[str, Any]:
    return {
        name: node
        for name, node in schema["properties"].items()
        if isinstance(node, dict) and node.get("type") == "array"
    }


#: Keys excluded from the compared shape. ``description`` is prose for humans and changes freely.
#: ``maxLength`` is excluded because **widening** it cannot invalidate a document that was already
#: valid, so it is additive in exactly the sense contract §1 means — but narrowing it very much
#: can, which is why it is not merely dropped: :func:`_max_lengths` asserts the direction
#: separately. See ``test_no_existing_field_had_its_length_ceiling_narrowed``.
_UNCOMPARED_KEYS: frozenset[str] = frozenset({"description", "maxLength"})


def _shape(
    items: dict[str, Any], *, ignore: str | None = None, strict: bool = False
) -> dict[str, Any]:
    """One element type's comparable shape: ordered properties, ordered required, strictness.

    Descriptions and length ceilings are excluded — see :data:`_UNCOMPARED_KEYS` for why each is,
    and what checks it instead. Everything else a consumer's ingestor can observe is included, and
    **order is included**, because `curated-snapshot-format.md` §3 makes the column order part of
    the layout an array-to-table load depends on.

    ``strict=True`` compares length ceilings too, for the objects where no widening is expected.
    """
    dropped = frozenset({"description"}) if strict else _UNCOMPARED_KEYS
    properties = {
        name: {key: value for key, value in node.items() if key not in dropped}
        for name, node in items.get("properties", {}).items()
        if name != ignore
    }
    return {
        "properties": properties,
        "property_order": [name for name in properties],
        "required": list(items.get("required", [])),
        "additionalProperties": items.get("additionalProperties"),
    }


def _max_lengths(items: dict[str, Any]) -> dict[str, int]:
    """Each property's declared length ceiling, for the properties that declare one."""
    return {
        name: node["maxLength"]
        for name, node in items.get("properties", {}).items()
        if isinstance(node, dict) and "maxLength" in node
    }


# --- the versions that would each be a release of every consumer ---------------------------------


def test_the_bundle_layout_version_is_unchanged(
    baseline: dict[str, Any], enriched: dict[str, Any]
) -> None:
    """The layout *rules* are unchanged; only new arrays appear (contract §1)."""
    assert enriched["properties"]["bundleFormatVersion"]["const"] == 1
    assert (
        enriched["properties"]["bundleFormatVersion"]["const"]
        == baseline["properties"]["bundleFormatVersion"]["const"]
    )
    assert BUNDLE_FORMAT_VERSION == 1


def test_the_consumer_contract_major_is_unchanged() -> None:
    """`schemaContractVersion` carries the consumer contract's MAJOR; these additions are MINOR."""
    assert SCHEMA_CONTRACT_VERSION == 1
    bundle = emit_bundle(factories.snapshot(), factories.meta())
    assert bundle["snapshotMeta"]["schemaContractVersion"] == 1


def test_snapshot_meta_is_untouched(baseline: dict[str, Any], enriched: dict[str, Any]) -> None:
    """`003` asserts on this object at fetch time; a change here is a site release."""
    assert _shape(enriched["properties"]["snapshotMeta"], strict=True) == _shape(
        baseline["properties"]["snapshotMeta"], strict=True
    )


# --- nothing existing renamed, reshaped, reordered, or changed optionality -----------------------


def test_every_pre_enrichment_array_still_exists_under_its_own_name(
    baseline: dict[str, Any], enriched: dict[str, Any]
) -> None:
    assert set(_arrays(baseline)) <= set(_arrays(enriched))


def test_the_root_required_list_only_grows_and_keeps_its_order(
    baseline: dict[str, Any], enriched: dict[str, Any]
) -> None:
    """A consumer reading positionally, or asserting on the list, sees its own prefix intact."""
    before = baseline["required"]
    after = enriched["required"]

    assert after[: len(before)] == before
    assert set(after) - set(before) == NEW_ARRAYS


@pytest.mark.parametrize(
    "array",
    sorted(_schema(BASELINE_PATH)["properties"]),
)
def test_an_existing_class_is_identical_but_for_its_permitted_new_column(
    array: str, baseline: dict[str, Any], enriched: dict[str, Any]
) -> None:
    """The field-by-field comparison FR-031 asks for, one existing class at a time."""
    before_node = baseline["properties"][array]
    after_node = enriched["properties"][array]
    if before_node.get("type") != "array":
        pytest.skip(f"{array} is not an array")

    added = NEW_COLUMNS.get(array)
    assert _shape(after_node["items"], ignore=added) == _shape(before_node["items"])


@pytest.mark.parametrize(
    "array",
    sorted(_schema(BASELINE_PATH)["properties"]),
)
def test_no_existing_field_had_its_length_ceiling_narrowed(
    array: str, baseline: dict[str, Any], enriched: dict[str, Any]
) -> None:
    """The one relaxation §1 permits, and the direction it is only ever permitted in.

    A **widened** ``maxLength`` is additive by construction: every document the released
    consumers could already ingest still validates, so nothing has to be released to read it.
    A **narrowed** one is a breaking change wearing the same clothes — it invalidates documents
    that were legal a version ago — and dropping ``maxLength`` from :func:`_shape` outright would
    have let that through silently. Hence a comparison by direction rather than by equality.

    Live instance: the Product Owner raised the authored-summary ceiling from 400 to 1 000 on
    2026-08-06 (``WGC_SUMMARY_MAX_CHARS`` 240 → 1 000) so a multi-clause mechanic can be stated
    completely. ``datasheetAbilities.summary`` is the existing field that moved.
    """
    before_node = baseline["properties"][array]
    after_node = enriched["properties"][array]
    if before_node.get("type") != "array":
        pytest.skip(f"{array} is not an array")

    before = _max_lengths(before_node["items"])
    after = _max_lengths(after_node["items"])

    for name, ceiling in before.items():
        assert name in after, f"{array}.{name} lost its length ceiling entirely"
        assert after[name] >= ceiling, (
            f"{array}.{name} narrowed its length ceiling {ceiling} -> {after[name]}, "
            "which invalidates documents the released consumers can already ingest"
        )


@pytest.mark.parametrize(("array", "column"), sorted(NEW_COLUMNS.items()))
def test_each_added_column_is_optional_and_therefore_invisible_to_an_old_consumer(
    array: str, column: str, enriched: dict[str, Any]
) -> None:
    items = enriched["properties"][array]["items"]

    assert column in items["properties"]
    assert column not in items["required"]


def test_the_only_new_arrays_are_the_seven_the_contract_declares(
    baseline: dict[str, Any], enriched: dict[str, Any]
) -> None:
    assert set(_arrays(enriched)) - set(_arrays(baseline)) == NEW_ARRAYS


# --- and an enriched bundle still validates against the schema the consumers hold ---------------


def _enriched_bundle() -> dict[str, Any]:
    from tests.contract.enrichment_bundle import enriched_snapshot

    bundle = emit_bundle(enriched_snapshot(), factories.meta())
    validate_bundle(bundle)
    return bundle


def test_the_seven_new_arrays_are_invisible_to_the_pre_enrichment_schema() -> None:
    """A released consumer's own schema does not object to a single new array.

    The baseline's **root** is not `additionalProperties: false`, so the seven arrays a released
    consumer knows nothing about are simply not its business — which is the mechanism by which
    contract §1's "no release of their own" actually works.
    """
    from jsonschema import Draft202012Validator

    baseline = {key: value for key, value in _schema(BASELINE_PATH).items() if key != "$id"}
    offending = {
        str(error.absolute_path[0])
        for error in Draft202012Validator(baseline).iter_errors(_enriched_bundle())
        if error.absolute_path
    }

    assert offending & NEW_ARRAYS == set()


def test_the_three_added_columns_are_the_only_thing_an_old_strict_validator_sees() -> None:
    """The honest edge, named rather than glossed.

    Each existing element type carries `additionalProperties: false` in the released consumers'
    own copy of the schema, so a consumer that *re-validates* a bundle against that copy —
    rather than ingesting it, which is what `001` and `003` actually do — would object to the
    three additive columns and to **nothing else**. Contract §3 permits the columns under
    `curated-snapshot-format.md` §3's layout rules and `reference-db-schema.md` §2's MINOR rule;
    this test pins the blast radius of that permission to exactly those three fields, so a fourth
    one cannot be slipped in behind the same argument.
    """
    from jsonschema import Draft202012Validator

    baseline = {key: value for key, value in _schema(BASELINE_PATH).items() if key != "$id"}
    observed = {
        (str(error.absolute_path[0]), error.message.split("'")[1])
        for error in Draft202012Validator(baseline).iter_errors(_enriched_bundle())
        if error.absolute_path and error.validator == "additionalProperties"
    }

    assert observed == set(NEW_COLUMNS.items())
