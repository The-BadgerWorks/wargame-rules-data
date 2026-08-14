# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the FR-030 guarantee set as
# V1-V6 and V19 of data-model.md §8 (task T066), each emitting its catalogued CON-*/PRC-* code,
# with reference-db-schema.md §3.4's range read from the contract rather than from configuration.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added V20, the per-key uniqueness of the
# emitted bundle (contract v1.3.2 guarantee 12), after the first ingestion of a real bundle found
# duplicate primary keys in two releases — including a class SQLite itself cannot see.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added the item-constraint closed-vocabulary
# check and its version-stamp check (007 task T016, display-fidelity-schema-delta.md §3.2), and
# `datasheetItemConstraints` to CONSUMER_PRIMARY_KEYS so V20 covers it too.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added check_marker_residue (007 task T036,
# guarantee 21): the blocking CST-MARKER-RESIDUE check that proves the T038 extraction-time strip
# actually ran, scanned independently of pipeline/validate/ip_scan.py's generic markup scan.
"""V1-V6, V19 and V20 — the guarantees the producer owes the consumer (FR-030, FR-049).

These are the checks that decide whether a candidate may ship at all. Each one exists because
the alternative failure lands on a player rather than on a curator: a datasheet with no cost is
a unit that prices as nothing, an orphan enhancement is an ingestion failure on a phone, a gap
in the point bands is an army size the app cannot validate, and a tier set with a hole prices
some copy of some unit by falling off the end of a lookup.

**The point-limit range is read from the consumer contract, not from configuration** (C7/R9).
`reference-db-schema.md` §3.4 declares it normative and shared with the app precisely so the two
sides cannot drift apart silently — making it a pipeline variable would reintroduce exactly the
divergence the resolution closed. Changing it is a contract revision on both sides, which is why
it appears below as a constant with the contract cited, and not in `pipeline/config.py`.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Final

from pipeline.models.curated import RESTRICTION_VOCABULARY, CuratedSnapshot, ItemConstraintType
from pipeline.models.findings import Finding
from pipeline.parse.composition_grammar import FOOTNOTE_MARK
from pipeline.report.catalogue import build_finding
from pipeline.validate.refs import check_intra_snapshot_references

if TYPE_CHECKING:  # pragma: no cover - import cycle only matters to the type checker
    from pipeline.build.bundle_emit import BundleMeta

# --- values fixed by the consumer contract, not by this repository's configuration -----------

#: `reference-db-schema.md` §3.4, normative. The app's `WGC_POINT_LIMIT_MIN` / `_MAX` are set
#: from the same two numbers.
MIN_CUSTOM_POINT_LIMIT: Final = 500
MAX_CUSTOM_POINT_LIMIT: Final = 5000

#: The MAJOR of `reference-db-schema.md` (currently v1.2.0) and its restriction vocabulary
#: version. Stamped into `snapshotMeta` and checked here, so a snapshot cannot claim to satisfy
#: a contract version this build of the pipeline does not actually emit (FR-049).
SCHEMA_CONTRACT_VERSION: Final = 1
RESTRICTION_VOCABULARY_VERSION: Final = 1

#: 007-loadout-display-fidelity (display-fidelity-schema-delta.md §3.2). `constraint_type` is
#: `ItemConstraintType`-typed on `CuratedItemConstraint` (unlike `restriction_type`, which is a
#: bare `str`), so Pydantic already refuses an out-of-vocabulary value at the model boundary and
#: this check is unreachable in normal operation. It is kept anyway, modelled exactly on
#: `RESTRICTION_VOCABULARY`/`check_restriction_vocabulary`, as defence-in-depth against a future
#: widening of the field's type — the same reasoning that keeps `check_intra_snapshot_references`
#: checking a `weapon_line` the reconcile-stage join already guarantees resolves (guarantee 22).
ITEM_CONSTRAINT_VOCABULARY_VERSION: Final = 1
ITEM_CONSTRAINT_VOCABULARY: Final[frozenset[str]] = frozenset(
    member.value for member in ItemConstraintType
)

#: A rules version id is a stable, non-empty identifier. The *publication* path additionally
#: pins the `mfm-YYYY-MM` shape (research D9, V12); at build time a fixture id such as
#: `fixture-minimal` is legitimate, so the check here is that there is an id at all.
_RULES_VERSION_ID: Final = re.compile(r"^[a-z0-9][a-z0-9.-]{2,63}$")


def check_costs(snapshot: CuratedSnapshot) -> list[Finding]:
    """V1 — every datasheet carries at least one cost row (guarantee 3)."""
    return [
        build_finding(
            "CON-NO-COST",
            entity_refs=[datasheet.datasheet_id],
            detail={"datasheet_id": datasheet.datasheet_id, "faction_id": datasheet.faction_id},
        )
        for datasheet in snapshot.datasheets
        if not datasheet.costs
    ]


def check_enhancement_parents(snapshot: CuratedSnapshot) -> list[Finding]:
    """V2 — every enhancement belongs to a detachment that exists (guarantee 3)."""
    detachment_ids = {d.detachment_id for d in snapshot.detachments}
    return [
        build_finding(
            "CON-ORPHAN-ENHANCEMENT",
            entity_refs=[enhancement.enhancement_id],
            detail={
                "enhancement_id": enhancement.enhancement_id,
                "detachment_id": enhancement.detachment_id,
            },
        )
        for enhancement in snapshot.enhancements
        if enhancement.detachment_id not in detachment_ids
    ]


def check_game_size_bands(snapshot: CuratedSnapshot) -> list[Finding]:
    """V3 — bands are contiguous, non-overlapping, and cover §3.4's range end to end.

    A gap is reported once per hole rather than once per band, because the approver's question
    is "which point limits does this snapshot not cover", and the answer is a list of ranges.
    """
    findings: list[Finding] = []
    bands = sorted(snapshot.game_sizes, key=lambda band: (band.min_points, band.max_points))

    if not bands:
        return [
            build_finding(
                "CON-BAND-GAP",
                detail={"from_points": MIN_CUSTOM_POINT_LIMIT, "to_points": MAX_CUSTOM_POINT_LIMIT},
            )
        ]

    cursor = MIN_CUSTOM_POINT_LIMIT
    for band in bands:
        if band.min_points > cursor:
            findings.append(
                build_finding(
                    "CON-BAND-GAP",
                    entity_refs=[band.id],
                    detail={"from_points": cursor, "to_points": band.min_points - 1},
                )
            )
        elif band.min_points < cursor:
            findings.append(
                build_finding(
                    "CON-BAND-OVERLAP",
                    entity_refs=[band.id],
                    detail={"from_points": band.min_points, "to_points": cursor - 1},
                )
            )
        if band.max_points < band.min_points:
            findings.append(
                build_finding(
                    "CON-BAND-GAP",
                    entity_refs=[band.id],
                    detail={"from_points": band.max_points, "to_points": band.min_points},
                )
            )
        cursor = max(cursor, band.max_points + 1)

    if cursor <= MAX_CUSTOM_POINT_LIMIT:
        findings.append(
            build_finding(
                "CON-BAND-GAP",
                detail={"from_points": cursor, "to_points": MAX_CUSTOM_POINT_LIMIT},
            )
        )

    return findings


def check_restriction_vocabulary(snapshot: CuratedSnapshot) -> list[Finding]:
    """V5 — every `restriction_type` is in the contract's closed vocabulary."""
    return [
        build_finding(
            "CON-RESTRICTION-VOCAB",
            entity_refs=[restriction.id],
            detail={
                "restriction_id": restriction.id,
                "restriction_type": restriction.restriction_type,
                "vocabulary_version": RESTRICTION_VOCABULARY_VERSION,
            },
        )
        for restriction in snapshot.all_restrictions
        if restriction.restriction_type not in RESTRICTION_VOCABULARY
    ]


def check_item_constraint_vocabulary(snapshot: CuratedSnapshot) -> list[Finding]:
    """007 — every item constraint's `constraint_type` is in the closed vocabulary.

    Reuses `CON-RESTRICTION-VOCAB` rather than minting a second code: the fact this check reports
    — "a value lies outside a closed vocabulary the contract declares" — is the same fact
    `check_restriction_vocabulary` reports, over a second field. `007`'s own finding catalogue
    (data-model.md §4) deliberately adds no tenth code for it, on `OPT-UNPARSED`'s precedent
    (006 catalogue.py: "a second code for one fact is a second thing to keep in step").
    """
    return [
        build_finding(
            "CON-RESTRICTION-VOCAB",
            entity_refs=[datasheet.datasheet_id],
            detail={
                "datasheet_id": datasheet.datasheet_id,
                "constraint_index": constraint.constraint_index,
                "constraint_type": constraint.constraint_type.value,
                "vocabulary_version": ITEM_CONSTRAINT_VOCABULARY_VERSION,
            },
        )
        for datasheet in snapshot.datasheets
        for constraint in datasheet.item_constraints
        if constraint.constraint_type.value not in ITEM_CONSTRAINT_VOCABULARY
    ]


def check_marker_residue(snapshot: CuratedSnapshot) -> list[Finding]:
    """007 US3 — guarantee 21: no name field carries a footnote-marker artifact (SC-002).

    Blocking, unlike every other check in this module's item-constraint half: a marker surviving
    into a published name is the **exact defect** this feature exists to remove, and it is cheap
    to detect — the same "a contradiction blocks, a gap is advisory" split `CMP-HEADER-ROW`
    (guarantee 20) already draws.

    Reuses :data:`~pipeline.parse.composition_grammar.FOOTNOTE_MARK`, the one expression every
    extraction-time strip (`007` T038) already applies — this is the **independent second
    mechanism** that proves the strip actually ran, on `validate/ip_scan.py`'s own precedent of
    pairing a schema-level control with a scanned one (research D9 control 1/2). Every name-shaped
    field guarantee 21 names: ``itemName``, ``modelName``, ``eligibleModelName``, and
    ``datasheetWeapons.name`` — plus the choice's own ``name``, the one D4.1 measured 119 rows of
    (the item rows a bundle item and its choice's name seed both descend from it).
    """
    findings: list[Finding] = []
    for datasheet in snapshot.datasheets:
        candidates: list[tuple[str, str]] = [
            *((f"weapon[{w.line}].name", w.name) for w in datasheet.weapons),
            *((f"composition[{c.line}].model_name", c.model_name) for c in datasheet.composition),
            *(
                (f"option_groups[{g.id}].eligible_model_name", g.eligible_model_name)
                for g in datasheet.option_groups
                if g.eligible_model_name is not None
            ),
            *((f"option_choices[{ch.id}].name", ch.name) for ch in datasheet.option_choices),
            *(
                (f"option_choices[{ch.id}].items[{it.item_index}].item_name", it.item_name)
                for ch in datasheet.option_choices
                for it in ch.items
            ),
            *(
                (f"equipment_groups[{eg.id}].model_name", eg.model_name)
                for eg in datasheet.equipment_groups
                if eg.model_name is not None
            ),
            *(
                (f"equipment_groups[{eg.id}].items[{ei.item_index}].item_name", ei.item_name)
                for eg in datasheet.equipment_groups
                for ei in eg.items
            ),
            *(
                (f"item_constraints[{ic.constraint_index}].item_name", ic.item_name)
                for ic in datasheet.item_constraints
            ),
            *(
                (f"item_constraints[{ic.constraint_index}].model_name", ic.model_name)
                for ic in datasheet.item_constraints
                if ic.model_name is not None
            ),
        ]
        for field_path, value in candidates:
            if FOOTNOTE_MARK.search(value):
                findings.append(
                    build_finding(
                        "CST-MARKER-RESIDUE",
                        entity_refs=[datasheet.datasheet_id],
                        detail={"datasheet_id": datasheet.datasheet_id, "field": field_path},
                    )
                )
    return findings


def check_version_stamp(meta: BundleMeta) -> list[Finding]:
    """V6 — the stamps are present and match what this build actually emits (FR-049)."""
    findings: list[Finding] = []

    if meta.schema_contract_version != SCHEMA_CONTRACT_VERSION:
        findings.append(
            build_finding(
                "CON-VERSION-STAMP",
                detail={
                    "field": "schemaContractVersion",
                    "stamped": meta.schema_contract_version,
                    "expected": SCHEMA_CONTRACT_VERSION,
                },
            )
        )
    if meta.restriction_vocabulary_version != RESTRICTION_VOCABULARY_VERSION:
        findings.append(
            build_finding(
                "CON-VERSION-STAMP",
                detail={
                    "field": "restrictionVocabularyVersion",
                    "stamped": meta.restriction_vocabulary_version,
                    "expected": RESTRICTION_VOCABULARY_VERSION,
                },
            )
        )
    # 007-loadout-display-fidelity: OPTIONAL, unlike the two required stamps above (contract
    # §3.1) — a producer that has not stamped it yet has said nothing wrong, so the check only
    # fires on a stamp that is PRESENT and disagrees.
    if (
        meta.item_constraint_vocabulary_version is not None
        and meta.item_constraint_vocabulary_version != ITEM_CONSTRAINT_VOCABULARY_VERSION
    ):
        findings.append(
            build_finding(
                "CON-VERSION-STAMP",
                detail={
                    "field": "itemConstraintVocabularyVersion",
                    "stamped": meta.item_constraint_vocabulary_version,
                    "expected": ITEM_CONSTRAINT_VOCABULARY_VERSION,
                },
            )
        )
    if not _RULES_VERSION_ID.match(meta.rules_version_id):
        findings.append(
            build_finding(
                "CON-VERSION-STAMP",
                detail={"field": "rulesVersionId", "length": len(meta.rules_version_id)},
            )
        )
    if not meta.published_at:
        findings.append(
            build_finding("CON-VERSION-STAMP", detail={"field": "publishedAt", "length": 0})
        )

    return findings


def check_tier_projection(snapshot: CuratedSnapshot) -> list[Finding]:
    """V19 — the tier table is resolvable at every `(model_count, copy_index)` lookup.

    Two ways it can fail, and both leave some copy of some unit with no price:

    * a `model_count` with no `copy_index_min = 1` row, so the *first* copy has no answer; and
    * a `copy_index_min` present for one `model_count` but not another, so a later copy at the
      second size falls back to a tier the publisher did not price it at.

    Resolvability is **per pricing context**. A context is a self-contained price list — a unit
    priced under a stated condition must be resolvable under that condition without borrowing a
    tier from the price it costs without it — so the two are checked apart rather than merged.
    """
    findings: list[Finding] = []

    for datasheet in snapshot.datasheets:
        if not datasheet.costs:
            continue
        by_context: dict[str, dict[int, set[int]]] = {}
        for cost in datasheet.costs:
            by_model_count = by_context.setdefault(cost.pricing_context or "", {})
            by_model_count.setdefault(cost.model_count, set()).add(cost.copy_index_min)

        for context, by_model_count in sorted(by_context.items()):
            expected_tiers = {tier for tiers in by_model_count.values() for tier in tiers}
            for model_count, tiers in sorted(by_model_count.items()):
                missing = expected_tiers - tiers
                if 1 not in tiers or missing:
                    findings.append(
                        build_finding(
                            "PRC-TIER-INCOMPLETE",
                            entity_refs=[datasheet.datasheet_id],
                            detail={
                                "datasheet_id": datasheet.datasheet_id,
                                "model_count": model_count,
                                "pricing_context": context or "(absent)",
                                "missing_copy_index_min": sorted(missing | ({1} - tiers)),
                            },
                        )
                    )

    return findings


#: Bundle array -> the consumer primary key `reference-db-schema.md` §3 declares for its table.
#:
#: Transcribed from the contract rather than derived from the emitter, for the same reason the
#: point-limit range above is: the check has to be able to disagree with this repository's own
#: code, or it is only asserting that the emitter agrees with itself.
CONSUMER_PRIMARY_KEYS: Final[dict[str, tuple[str, ...]]] = {
    "editions": ("id",),
    "editionRules": ("editionId", "ruleKey"),
    "gameSizeRules": ("id",),
    "factions": ("id",),
    "detachments": ("id",),
    "detachmentRestrictions": ("id",),
    "enhancements": ("id",),
    "enhancementEligibility": ("enhancementId", "ruleType", "value"),
    "datasheets": ("id",),
    "datasheetKeywords": ("datasheetId", "keyword", "modelScope"),
    "datasheetModels": ("datasheetId", "line"),
    "datasheetWeapons": ("datasheetId", "line"),
    "datasheetAbilities": ("datasheetId", "name"),
    "datasheetCosts": ("datasheetId", "modelCount"),
    "datasheetCostTiers": ("datasheetId", "modelCount", "copyIndexMin"),
    "datasheetCostContexts": ("datasheetId", "pricingContext", "modelCount", "copyIndexMin"),
    "datasheetWargearOptions": ("id",),
    "datasheetLeaderPairs": ("leaderDatasheetId", "bodyguardDatasheetId"),
    "datasheetDetachmentEligibility": ("datasheetId", "detachmentId"),
    # 004-rules-data-enrichment's additive tables (contract v1.3.0 §3).
    "datasheetCompositions": ("datasheetId", "line"),
    "datasheetOptionGroups": ("id",),
    "datasheetOptionChoices": ("id",),
    "chapterKeywords": ("keyword",),
    "factionRules": ("id",),
    "detachmentRules": ("id",),
    "keywordGlossary": ("keywordKey",),
    # 006-unit-loadout-fidelity's additive tables (contracts/loadout-schema-delta.md §2).
    # Each key is a composite the SOURCE supplies -- the choice or group it hangs off, plus the
    # source's own conjunct or sentence ordinal -- so no identity is minted here and a rebuild
    # from an unchanged tree reproduces the same rows in the same order.
    "datasheetOptionChoiceItems": ("choiceId", "role", "itemIndex"),
    "datasheetEquipmentGroups": ("id",),
    "datasheetEquipmentItems": ("groupId", "itemIndex"),
    # 007-loadout-display-fidelity's one additive table (display-fidelity-schema-delta.md §2.1).
    "datasheetItemConstraints": ("datasheetId", "constraintIndex"),
}


def check_bundle_primary_keys(bundle: Mapping[str, object]) -> list[Finding]:
    """V20 — one row per consumer primary key, over the **bundle** rather than the snapshot.

    Over the bundle because that is where the collision becomes real: `datasheetAbilities` is an
    expansion of each datasheet's ability keys against the authored summaries, so two keys that
    resolve to the same ability *name* are one row in the tree and two rows in the wire format.
    A snapshot-level check cannot see it.

    The emitter has already collapsed rows that were byte-identical (`bundle_emit._rows`), which
    is lossless. Anything still colliding here therefore **disagrees about something**, and the
    producer may not pick: `reference-db-schema.md` §3 gives the app one row per key, and which
    one it should be is a content decision. So this blocks, and it names the key and the number
    of rows rather than the values, because a finding is a report row and not a data channel.

    NULL participates in the key. SQLite treats NULLs in a unique index as distinct, so an
    ingestor building the declared schema silently accepts duplicates whose `model_scope` is
    absent — the producer is the only side that can catch those.
    """
    findings: list[Finding] = []

    for array, keys in sorted(CONSUMER_PRIMARY_KEYS.items()):
        rows = bundle.get(array)
        if not isinstance(rows, Sequence) or isinstance(rows, str | bytes):
            continue

        grouped: dict[tuple[str, ...], list[Mapping[str, object]]] = {}
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            grouped.setdefault(tuple(_key_part(row.get(key)) for key in keys), []).append(row)

        for key, group in sorted(grouped.items()):
            if len(group) > 1:
                findings.append(
                    build_finding(
                        "CON-DUPLICATE-KEY",
                        entity_refs=[str(group[0].get(keys[0], ""))],
                        detail={
                            "array": array,
                            "key": " / ".join(
                                f"{name}={part}" for name, part in zip(keys, key, strict=True)
                            ),
                            "row_count": len(group),
                        },
                    )
                )

    return findings


def _key_part(value: object) -> str:
    """One key component as text, with absence written as a value rather than left out."""
    return "(absent)" if value is None else str(value)


def check_snapshot(snapshot: CuratedSnapshot, meta: BundleMeta) -> list[Finding]:
    """Run the whole FR-030 guarantee set over one snapshot.

    Returns every finding rather than stopping at the first: a curator fixing a candidate wants
    the list, not the first item of it.
    """
    return [
        *check_costs(snapshot),
        *check_enhancement_parents(snapshot),
        *check_game_size_bands(snapshot),
        *check_intra_snapshot_references(snapshot),
        *check_restriction_vocabulary(snapshot),
        *check_item_constraint_vocabulary(snapshot),
        *check_marker_residue(snapshot),
        *check_version_stamp(meta),
        *check_tier_projection(snapshot),
    ]
