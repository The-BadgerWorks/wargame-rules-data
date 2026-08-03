# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the FR-030 guarantee set as
# V1-V6 and V19 of data-model.md §8 (task T066), each emitting its catalogued CON-*/PRC-* code,
# with reference-db-schema.md §3.4's range read from the contract rather than from configuration.
"""V1-V6 and V19 — the guarantees the producer owes the consumer (FR-030, FR-049).

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
from typing import TYPE_CHECKING, Final

from pipeline.models.curated import RESTRICTION_VOCABULARY, CuratedSnapshot
from pipeline.models.findings import Finding
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
    """
    findings: list[Finding] = []

    for datasheet in snapshot.datasheets:
        if not datasheet.costs:
            continue
        by_model_count: dict[int, set[int]] = {}
        for cost in datasheet.costs:
            by_model_count.setdefault(cost.model_count, set()).add(cost.copy_index_min)

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
                            "missing_copy_index_min": sorted(missing | ({1} - tiers)),
                        },
                    )
                )

    return findings


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
        *check_version_stamp(meta),
        *check_tier_projection(snapshot),
    ]
