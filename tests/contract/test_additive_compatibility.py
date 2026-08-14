# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the additive-compatibility proof (004
# task T065): the enriched bundle schema compared field by field against the frozen
# pre-enrichment baseline, failing on any rename, reshape, reorder, or optionality change to an
# existing class, with bundleFormatVersion and snapshotMeta.schemaContractVersion unchanged
# (004 FR-031, FR-032, contracts/bundle-schema-delta.md §1).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the SECOND comparison, against the
# frozen pre-loadout baseline (006 task T033): 004's fully shipped shape is what the currently
# released consumers hold, and three of 006's four new columns land on an array 004 added, so the
# pre-enrichment baseline cannot govern them at all (006 FR-017, FR-018,
# contracts/loadout-schema-delta.md §1). Also replaced the single-name parse of jsonschema's
# additionalProperties message with _strict_validator_objections, which reads every name it
# lists -- `datasheets` now carries two added columns and the old parse saw one of them.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added 007-loadout-display-fidelity's
# `datasheetItemConstraints` to NEW_ARRAYS and LOADOUT_ARRAYS (007 task T011), and the two new
# OPTIONAL snapshotMeta fields to a permitted-exception set the same way NEW_COLUMNS/
# LOADOUT_COLUMNS already except additive columns on ordinary arrays.
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

**Two baselines, two comparisons, and neither replaces the other** (006 task T033).
`bundle.schema.pre-enrichment.json` freezes the shape before `004`; `bundle.schema.pre-loadout.json`
freezes the shape after it, which is what the *currently* released consumers were built against.
The second is not a refinement of the first: three of `006`'s four new columns land on
`datasheetOptionGroups`, an array `004` added, so the pre-enrichment baseline does not describe
that class at all and could never have caught a reshape of it. Keeping both is also what stops an
existing class being walked across two features one small "additive" step at a time.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from pipeline.build.bundle_emit import BUNDLE_FORMAT_VERSION, emit_bundle
from pipeline.schema_validation import validate_bundle
from pipeline.validate.contract_checks import SCHEMA_CONTRACT_VERSION
from tests import factories

ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = ROOT / "fixtures" / "contract" / "bundle.schema.pre-enrichment.json"

#: `004`'s fully shipped shape — the schema the *currently* released consumers were built
#: against, and therefore the baseline `006`'s own additive promise is measured from (006 task
#: T033, contracts/loadout-schema-delta.md §1).
#:
#: Both baselines are kept and both comparisons run. Retiring the older one on the grounds that
#: the newer subsumes it is the tempting simplification and it is wrong twice over: `004`'s
#: promise was made to consumers still in the field, and a comparison that only ever looks one
#: feature back would let an existing class be walked across two features one small "additive"
#: step at a time, with every individual step passing.
PRE_LOADOUT_PATH = ROOT / "fixtures" / "contract" / "bundle.schema.pre-loadout.json"
SCHEMA_PATH = ROOT / "schemas" / "bundle.schema.json"

#: The arrays `004-rules-data-enrichment` adds (contract §2, plus `datasheetCostContexts` at
#: v1.4.0). Everything outside this set must be byte-for-byte what the released consumers were
#: built against.
#:
#: `datasheetCostContexts` is a separate array rather than a `pricingContext` column on
#: `datasheetCosts` precisely so this file's assertions can hold. A column would have carried
#: extra *rows* under a primary key an old consumer already declares, and an extra row under a
#: declared key is not something a consumer can ignore — it is a constraint error that refuses
#: the whole snapshot.
NEW_ARRAYS: frozenset[str] = frozenset(
    {
        "datasheetCompositions",
        "datasheetOptionGroups",
        "datasheetOptionChoices",
        "chapterKeywords",
        "factionRules",
        "detachmentRules",
        "keywordGlossary",
        "datasheetCostContexts",
        # 006-unit-loadout-fidelity (006 task T006, contracts/loadout-schema-delta.md §2). Three
        # sibling arrays, for the same reason `datasheetCostContexts` is one: extra rows under a
        # primary key an old consumer already declares is not something it can ignore, and a
        # multi-item swap published as extra `datasheetOptionChoices` rows would be rendered as
        # four alternatives -- a WRONG reading rather than a lossy one.
        "datasheetOptionChoiceItems",
        "datasheetEquipmentGroups",
        "datasheetEquipmentItems",
        # 007-loadout-display-fidelity (007 task T011, display-fidelity-schema-delta.md §2.1).
        # Measured against the PRE-ENRICHMENT baseline below, so it joins this set too: a
        # consumer released before `004` has never heard of any array added since, including
        # this one.
        "datasheetItemConstraints",
    }
)

#: The arrays `004` alone added. Kept apart from :data:`NEW_ARRAYS` because a `004`-era fixture
#: bundle populates exactly these, and a proof that says "the fixture really is enriched" can
#: only assert about arrays the fixture carries. `006`'s three join it once T021 and T030 emit
#: them, and T042 re-runs that proof against a loadout-extended bundle.
ENRICHMENT_ARRAYS: frozenset[str] = frozenset(
    {
        "datasheetCompositions",
        "datasheetOptionGroups",
        "datasheetOptionChoices",
        "chapterKeywords",
        "factionRules",
        "detachmentRules",
        "keywordGlossary",
        "datasheetCostContexts",
    }
)

#: The additive columns on **pre-enrichment** arrays, as ``array -> columns``. Each is
#: **optional** and omitted when absent, so every existing row that acquires no value is
#: byte-identical.
#:
#: `006`'s three eligibility columns are not here because they land on `datasheetOptionGroups`,
#: which is itself an array `004` added — so it is outside this baseline entirely, and the
#: comparison that governs it is the pre-loadout one (006 task T033).
NEW_COLUMNS: dict[str, frozenset[str]] = {
    "datasheets": frozenset({"wargearOptionState", "defaultEquipmentState"}),
    "datasheetKeywords": frozenset({"keywordClass"}),
    "factions": frozenset({"armyRuleState"}),
}

#: Flattened ``(array, column)`` pairs, for the assertions that parametrise or compare per pair.
NEW_COLUMN_PAIRS: frozenset[tuple[str, str]] = frozenset(
    (array, column) for array, columns in NEW_COLUMNS.items() for column in columns
)

#: The arrays added since :data:`PRE_LOADOUT_PATH` was frozen (006 task T033) -- i.e. everything
#: the CURRENTLY released consumers do not know about. `006`'s own three, plus `007`'s
#: `datasheetItemConstraints` (007 task T011): `PRE_LOADOUT_PATH` freezes the shape as it stood
#: BEFORE `006` shipped, so from that vantage point `007`'s addition is just as new as `006`'s
#: three were. A THIRD baseline, frozen at `007`'s own release, is `007`'s own concern when it
#: ships -- not a reason to keep this set artificially at three in the meantime.
LOADOUT_ARRAYS: frozenset[str] = frozenset(
    {
        "datasheetOptionChoiceItems",
        "datasheetEquipmentGroups",
        "datasheetEquipmentItems",
        "datasheetItemConstraints",
    }
)

#: The two OPTIONAL `snapshotMeta` fields `007` alone adds (display-fidelity-schema-delta.md
#: §3). Both are omitted by a producer with nothing to say, so an old consumer reading neither is
#: unaffected — `test_snapshot_meta_is_untouched(_since_the_last_release)` would otherwise treat
#: this addition as a shape change, which is exactly the kind of "additive" schema change the two
#: `NEW_COLUMNS`/`LOADOUT_COLUMNS` dicts above already carve an exception for on ordinary arrays.
SNAPSHOT_META_NEW_FIELDS: frozenset[str] = frozenset(
    {"itemConstraintVocabularyVersion", "renderingContractVersion"}
)

#: The four columns `006` alone adds, as ``array -> columns``.
#:
#: Three of them land on `datasheetOptionGroups`, which is an array `004` added — so they are
#: invisible to the pre-enrichment comparison above and this is the only place they are governed.
#: That is exactly why a second baseline exists rather than a wider permission on the first.
LOADOUT_COLUMNS: dict[str, frozenset[str]] = {
    "datasheets": frozenset({"defaultEquipmentState"}),
    "datasheetOptionGroups": frozenset({"eligibleModelName", "eligibleMaxCount", "isPerModel"}),
}

LOADOUT_COLUMN_PAIRS: frozenset[tuple[str, str]] = frozenset(
    (array, column) for array, columns in LOADOUT_COLUMNS.items() for column in columns
)

#: The `004` columns specifically. Kept apart from the union above because they are the ones a
#: `004`-era fixture bundle actually *carries*, and the old-strict-validator assertion below can
#: only observe a column a bundle populates.
ENRICHMENT_COLUMN_PAIRS: frozenset[tuple[str, str]] = frozenset(
    {
        ("datasheets", "wargearOptionState"),
        ("datasheetKeywords", "keywordClass"),
        ("factions", "armyRuleState"),
    }
)


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
    items: dict[str, Any], *, ignore: frozenset[str] = frozenset(), strict: bool = False
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
        if name not in ignore
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
    """`003` asserts on this object at fetch time; a change here is a site release.

    `007`'s two OPTIONAL fields are the one permitted exception (`SNAPSHOT_META_NEW_FIELDS`),
    on the same footing as `NEW_COLUMNS`'s additive columns on ordinary arrays.
    """
    assert _shape(
        enriched["properties"]["snapshotMeta"], ignore=SNAPSHOT_META_NEW_FIELDS, strict=True
    ) == _shape(baseline["properties"]["snapshotMeta"], strict=True)


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

    added = NEW_COLUMNS.get(array, frozenset())
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


@pytest.mark.parametrize(("array", "column"), sorted(NEW_COLUMN_PAIRS))
def test_each_added_column_is_optional_and_therefore_invisible_to_an_old_consumer(
    array: str, column: str, enriched: dict[str, Any]
) -> None:
    items = enriched["properties"][array]["items"]

    assert column in items["properties"]
    assert column not in items["required"]


def test_the_only_new_arrays_are_the_ones_the_contract_declares(
    baseline: dict[str, Any], enriched: dict[str, Any]
) -> None:
    assert set(_arrays(enriched)) - set(_arrays(baseline)) == NEW_ARRAYS


# --- and an enriched bundle still validates against the schema the consumers hold ---------------


def _enriched_bundle() -> dict[str, Any]:
    from tests.contract.enrichment_bundle import enriched_snapshot

    bundle = emit_bundle(enriched_snapshot(), factories.meta())
    validate_bundle(bundle)
    return bundle


def _strict_validator_objections(
    baseline_path: Path, bundle: dict[str, Any]
) -> set[tuple[str, str]]:
    """``(array, column)`` for every field a strict validator of ``baseline_path`` objects to.

    **Every** field, not the first one named. `jsonschema` reports one `additionalProperties`
    error per object and lists all of that object's unexpected properties inside a single
    message, so reading one name out of it silently under-reports exactly the case this file
    exists to bound: a row that acquired *two* new columns. `datasheets` is that row now — it
    carries `wargearOptionState` from `004` and `defaultEquipmentState` from `006`.
    """
    from jsonschema import Draft202012Validator

    baseline = {key: value for key, value in _schema(baseline_path).items() if key != "$id"}
    return {
        (str(error.absolute_path[0]), name)
        for error in Draft202012Validator(baseline).iter_errors(bundle)
        if error.absolute_path and error.validator == "additionalProperties"
        for name in re.findall(r"'([^']+)'", error.message)
    }


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
    observed = _strict_validator_objections(BASELINE_PATH, _enriched_bundle())

    # `<=` rather than `==`, and the second assertion is what stops that being a weakening: a
    # strict old validator can only object to a column the bundle actually CARRIES, and 006's
    # `defaultEquipmentState` is omitted on every row of a 004-era fixture. The claim this test
    # makes is about the blast radius -- nothing outside the permitted set is ever seen -- and
    # the 004 three prove it cannot pass vacuously.
    #
    # `test_the_pre_enrichment_blast_radius_is_exactly_the_permitted_columns` below closes the
    # gap the `<=` opens, over a bundle that carries all four (006 task T042).
    assert observed <= NEW_COLUMN_PAIRS
    assert observed >= ENRICHMENT_COLUMN_PAIRS


# --- and the same comparison again, against the baseline the CURRENT consumers hold -------------
#
# Everything above proves `004`'s promise to a consumer released before `004`. Nothing above says
# anything about `006`'s promise to a consumer released *after* it: `datasheetOptionGroups` is an
# array `004` added, so the pre-enrichment baseline does not describe it at all, and three of this
# feature's four new columns live there. This section is where they are governed.


@pytest.fixture(scope="module")
def pre_loadout() -> dict[str, Any]:
    return _schema(PRE_LOADOUT_PATH)


def _loadout_bundle() -> dict[str, Any]:
    from tests.contract.loadout_bundle import loadout_snapshot

    bundle = emit_bundle(loadout_snapshot(), factories.meta())
    validate_bundle(bundle)
    return bundle


def test_the_bundle_layout_version_is_unchanged_since_the_last_release(
    pre_loadout: dict[str, Any], enriched: dict[str, Any]
) -> None:
    """`006` adds arrays and columns; it does not change what an array *is* (contract §1)."""
    assert (
        enriched["properties"]["bundleFormatVersion"]["const"]
        == pre_loadout["properties"]["bundleFormatVersion"]["const"]
        == 1
    )


def test_snapshot_meta_is_untouched_since_the_last_release(
    pre_loadout: dict[str, Any], enriched: dict[str, Any]
) -> None:
    """`007`'s two OPTIONAL fields are the one permitted exception, same as above."""
    assert _shape(
        enriched["properties"]["snapshotMeta"], ignore=SNAPSHOT_META_NEW_FIELDS, strict=True
    ) == _shape(pre_loadout["properties"]["snapshotMeta"], strict=True)


def test_every_pre_loadout_array_still_exists_under_its_own_name(
    pre_loadout: dict[str, Any], enriched: dict[str, Any]
) -> None:
    assert set(_arrays(pre_loadout)) <= set(_arrays(enriched))


def test_the_root_required_list_only_grew_by_the_arrays_added_since_the_last_release(
    pre_loadout: dict[str, Any], enriched: dict[str, Any]
) -> None:
    """Appended, never inserted: a consumer reading the list positionally keeps its own prefix."""
    before = pre_loadout["required"]
    after = enriched["required"]

    assert after[: len(before)] == before
    assert set(after) - set(before) == LOADOUT_ARRAYS


@pytest.mark.parametrize("array", sorted(_schema(PRE_LOADOUT_PATH)["properties"]))
def test_a_released_class_is_identical_but_for_its_permitted_loadout_column(
    array: str, pre_loadout: dict[str, Any], enriched: dict[str, Any]
) -> None:
    """The field-by-field comparison FR-017 asks for, one released class at a time.

    This is the assertion that would fail if `scope` had gained a fourth member for eligibility
    scoping, or if `grantsWeaponLine` had been reshaped to carry a list — the two shapes the
    design considered and rejected. Both would have read as "additive" in a diff.
    """
    before_node = pre_loadout["properties"][array]
    after_node = enriched["properties"][array]
    if before_node.get("type") != "array":
        pytest.skip(f"{array} is not an array")

    added = LOADOUT_COLUMNS.get(array, frozenset())
    assert _shape(after_node["items"], ignore=added) == _shape(before_node["items"])


@pytest.mark.parametrize("array", sorted(_schema(PRE_LOADOUT_PATH)["properties"]))
def test_no_released_field_had_its_length_ceiling_narrowed(
    array: str, pre_loadout: dict[str, Any], enriched: dict[str, Any]
) -> None:
    before_node = pre_loadout["properties"][array]
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


@pytest.mark.parametrize(("array", "column"), sorted(LOADOUT_COLUMN_PAIRS))
def test_each_loadout_column_is_optional_and_therefore_invisible_to_a_released_consumer(
    array: str, column: str, enriched: dict[str, Any]
) -> None:
    items = enriched["properties"][array]["items"]

    assert column in items["properties"]
    assert column not in items["required"]


def test_the_only_arrays_added_since_the_last_release_are_the_ones_the_contracts_declare(
    pre_loadout: dict[str, Any], enriched: dict[str, Any]
) -> None:
    assert set(_arrays(enriched)) - set(_arrays(pre_loadout)) == LOADOUT_ARRAYS


def test_the_arrays_added_since_the_last_release_are_invisible_to_the_released_schema() -> None:
    """A consumer released against `004`'s schema does not object to a single new array."""
    from jsonschema import Draft202012Validator

    baseline = {key: value for key, value in _schema(PRE_LOADOUT_PATH).items() if key != "$id"}
    offending = {
        str(error.absolute_path[0])
        for error in Draft202012Validator(baseline).iter_errors(_loadout_bundle())
        if error.absolute_path
    }

    assert offending & LOADOUT_ARRAYS == set()


def test_the_four_added_columns_are_the_only_thing_a_released_strict_validator_sees() -> None:
    """The honest edge again, and this time with **no** `<=`.

    A strict old validator can only object to a column the bundle actually carries, so the
    equality below is only meaningful because `tests/contract/loadout_bundle.py` sets all four:
    `defaultEquipmentState` on both datasheets, and all three eligibility columns on the scoped
    group. Nothing outside the permitted set is seen, and the permitted set is not padding.
    """
    observed = _strict_validator_objections(PRE_LOADOUT_PATH, _loadout_bundle())

    assert observed == LOADOUT_COLUMN_PAIRS


def test_the_pre_enrichment_blast_radius_is_exactly_the_permitted_columns() -> None:
    """The `<=` above, closed — the 006 re-run of the assertion a 004-era fixture can only bound.

    `test_the_three_added_columns_are_the_only_thing_an_old_strict_validator_sees` has to state
    its claim as an inclusion, because the bundle it runs against omits `defaultEquipmentState`
    on every row and a validator cannot object to a column that is not there. Run over a bundle
    that carries it, the same claim becomes an equality — and an equality is what "the blast
    radius is exactly these four fields" actually means (006 task T042).
    """
    observed = _strict_validator_objections(BASELINE_PATH, _loadout_bundle())

    assert observed == NEW_COLUMN_PAIRS
