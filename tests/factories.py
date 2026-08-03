# AI-Assisted: Claude Code (model: claude-opus-5) - Test-support builders for curated snapshots
# (tasks T048-T052), so a contract test states the ONE thing it is about rather than restating
# thirty fields of scaffolding around it.
"""Builders for synthetic curated snapshots.

Every contract test needs a snapshot that is valid in every respect except the one it is
testing. Building that inline makes the interesting field impossible to see, so it is built
here once and mutated per test.

Everything produced here is invented, like every fixture in this repository.
"""

from __future__ import annotations

from collections.abc import Sequence

from pipeline.build.bundle_emit import BundleMeta
from pipeline.models.authored import AbilitySummary, ReviewState
from pipeline.models.curated import (
    CuratedDatasheet,
    CuratedDatasheetCost,
    CuratedDetachment,
    CuratedEdition,
    CuratedEditionRule,
    CuratedEnhancement,
    CuratedFaction,
    CuratedGameSizeRule,
    CuratedKeyword,
    CuratedModelLine,
    CuratedSnapshot,
    CuratedWeaponLine,
)
from pipeline.models.provenance import (
    DetailSource,
    EntityProvenance,
    PointsSource,
    PricingConfidence,
    PricingConfidenceState,
)

EDITION_ID = "ed-wh40k-11e"
EDITION_CODE = "wh40k-11e"


def provenance(*, detail_edition_code: str = EDITION_CODE) -> EntityProvenance:
    return EntityProvenance(
        points_source=PointsSource.MFM,
        points_acquisition_id="mfm-20260613T000000Z-deadbeef",
        points_edition_code=EDITION_CODE,
        detail_source=DetailSource.WAHAPEDIA,
        detail_acquisition_id="wahapedia-20260613T000000Z-cafebabe",
        detail_edition_code=detail_edition_code,
    )


def edition() -> CuratedEdition:
    return CuratedEdition(
        id=EDITION_ID, code=EDITION_CODE, name="Invented Edition", display_order=1
    )


def bands() -> list[CuratedGameSizeRule]:
    """Two contiguous bands covering 500..5000 end to end (reference-db-schema.md §3.4)."""
    return [
        CuratedGameSizeRule(
            id="gs-incursion",
            edition_id=EDITION_ID,
            label="Incursion",
            min_points=500,
            max_points=1999,
            detachment_points_budget=6,
            max_detachments=2,
            max_enhancements=2,
        ),
        CuratedGameSizeRule(
            id="gs-strike-force",
            edition_id=EDITION_ID,
            label="Strike Force",
            min_points=2000,
            max_points=5000,
            detachment_points_budget=12,
            max_detachments=4,
            max_enhancements=3,
        ),
    ]


def faction(faction_id: str = "f-emberwrights", *, parent: str | None = None) -> CuratedFaction:
    return CuratedFaction(
        faction_id=faction_id,
        edition_id=EDITION_ID,
        code=faction_id.removeprefix("f-"),
        name=faction_id.removeprefix("f-").replace("-", " ").title(),
        parent_faction_id=parent,
        mfm_slug=faction_id.removeprefix("f-"),
        detail_source_faction_id="EW",
        provenance=provenance(),
    )


def detachment(
    detachment_id: str = "d-anvil-vigil", *, faction_id: str = "f-emberwrights"
) -> CuratedDetachment:
    return CuratedDetachment(
        detachment_id=detachment_id,
        edition_id=EDITION_ID,
        faction_id=faction_id,
        name="Anvil Vigil",
        detachment_points_cost=2,
        force_disposition="HOLD THE LINE",
        is_unique=False,
        provenance=provenance(),
    )


def enhancement(
    enhancement_id: str = "e-emberbound-oath", *, detachment_id: str = "d-anvil-vigil"
) -> CuratedEnhancement:
    return CuratedEnhancement(
        enhancement_id=enhancement_id,
        edition_id=EDITION_ID,
        detachment_id=detachment_id,
        name="Emberbound Oath",
        points=25,
        max_per_army=1,
        provenance=provenance(),
    )


def costs(
    pairs: Sequence[tuple[int, int, int]] = ((1, 3, 60), (1, 6, 115)),
    *,
    confidence: PricingConfidenceState = PricingConfidenceState.VERIFIED,
) -> list[CuratedDatasheetCost]:
    """``pairs`` are ``(copy_index_min, model_count, points)`` triples."""
    return [
        CuratedDatasheetCost(
            model_count=model_count,
            copy_index_min=copy_index_min,
            points=points,
            label=f"{model_count} models",
            pricing_confidence=confidence,
            source_acquisition_id="mfm-20260613T000000Z-deadbeef",
        )
        for copy_index_min, model_count, points in pairs
    ]


def datasheet(
    datasheet_id: str = "ds-ember-sentinel",
    *,
    faction_id: str = "f-emberwrights",
    cost_rows: Sequence[CuratedDatasheetCost] | None = None,
    ability_keys: Sequence[str] = ("core:deep-strike",),
    detail_edition_code: str = EDITION_CODE,
) -> CuratedDatasheet:
    return CuratedDatasheet(
        datasheet_id=datasheet_id,
        edition_id=EDITION_ID,
        faction_id=faction_id,
        name="Ember Sentinel",
        role="Battleline",
        is_battleline=True,
        models=[
            CuratedModelLine(
                line=1,
                name="Ember Sentinel",
                movement='6"',
                toughness=5,
                save="3+",
                wounds=3,
                leadership="6+",
                objective_control=2,
                base_size="32mm",
            )
        ],
        weapons=[
            CuratedWeaponLine(
                line=1,
                name="Ember lance",
                is_melee=False,
                range='24"',
                attacks="2",
                skill="3+",
                strength="5",
                armour_penetration="-1",
                damage="2",
            )
        ],
        keywords=[CuratedKeyword(keyword="INFANTRY")],
        ability_keys=list(ability_keys),
        costs=list(cost_rows if cost_rows is not None else costs()),
        pricing_confidence=PricingConfidence(state=PricingConfidenceState.VERIFIED),
        provenance=provenance(detail_edition_code=detail_edition_code),
    )


def summaries(keys: Sequence[str] = ("core:deep-strike",)) -> dict[str, AbilitySummary]:
    return {
        key: AbilitySummary(
            ability_key=key,
            name=key.split(":")[-1].replace("-", " ").title(),
            summary="Invented mechanics-only summary authored for this data set.",
            review_state=ReviewState.APPROVED,
            mechanic_digest="0" * 32,
            reviewed_by="curator",
            reviewed_at="2026-06-13T00:00:00Z",
        )
        for key in keys
    }


def snapshot(**overrides: object) -> CuratedSnapshot:
    """A snapshot that satisfies every FR-030 guarantee, ready to be broken one field at a time."""
    base: dict[str, object] = {
        "edition": edition(),
        "edition_rules": [CuratedEditionRule(rule_key="warlord_required", value=True)],
        "game_sizes": bands(),
        "factions": [faction()],
        "detachments": [detachment()],
        "enhancements": [enhancement()],
        "datasheets": [datasheet()],
        "restrictions": [],
        "ability_summaries": summaries(),
    }
    base.update(overrides)
    return CuratedSnapshot(**base)  # type: ignore[arg-type]


def meta(rules_version_id: str = "mfm-2026-06") -> BundleMeta:
    return BundleMeta(
        rules_version_id=rules_version_id,
        published_at="2026-06-13T00:00:00Z",
        source_note="Invented Fixture 2026.06",
        schema_contract_version=1,
        restriction_vocabulary_version=1,
    )
