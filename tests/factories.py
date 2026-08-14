# AI-Assisted: Claude Code (model: claude-opus-5) - Test-support builders for curated snapshots
# (tasks T048-T052), so a contract test states the ONE thing it is about rather than restating
# thirty fields of scaffolding around it.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added loadout_datasheet() (007 task T009):
# one synthetic datasheet exercising all five classes 006 added that pipeline/curate/writer.py
# and prior.py currently lose on a round trip (research D2, issue #14) — equipment groups with
# items, default_equipment_state, option_choices[].items, and the three option-group eligibility
# columns — ready for T029's write-read-compare test to import directly.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Extended loadout_datasheet() with
# item_constraints (007 US3, T037/T040, and the carried-over writer.py/prior.py round-trip gap
# US4's T032 deliberately left for US3 to close): one linked, one scoped-and-unlinked row, so the
# same fixture proves both the vocabulary's linking rule and the round trip in one place.
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
    CuratedCompositionEntry,
    CuratedDatasheet,
    CuratedDatasheetCost,
    CuratedDetachment,
    CuratedEdition,
    CuratedEditionRule,
    CuratedEnhancement,
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    CuratedFaction,
    CuratedGameSizeRule,
    CuratedItemConstraint,
    CuratedKeyword,
    CuratedModelLine,
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
    CuratedSnapshot,
    CuratedWeaponLine,
    DefaultEquipmentState,
    EquipmentAppliesTo,
    ItemConstraintType,
    OptionItemRole,
    OptionScope,
    WargearOptionState,
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
    pricing_context: str | None = None,
) -> list[CuratedDatasheetCost]:
    """``pairs`` are ``(copy_index_min, model_count, points)`` triples."""
    return [
        CuratedDatasheetCost(
            model_count=model_count,
            copy_index_min=copy_index_min,
            points=points,
            label=f"{model_count} models",
            pricing_context=pricing_context,
            pricing_confidence=confidence,
            source_acquisition_id="mfm-20260613T000000Z-deadbeef",
        )
        for copy_index_min, model_count, points in pairs
    ]


def contextual_costs() -> list[CuratedDatasheetCost]:
    """The §7 fixture requirement for `pricing_context`: one unit priced twice over.

    The same two size bands at the unit's own price and at the price a stated condition puts on
    it, so a consumer test meets both the unconditional rows and the conditional ones.
    """
    return costs() + costs(((1, 3, 70), (1, 6, 135)), pricing_context="every-model-has-emberbound")


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


def loadout_datasheet(
    datasheet_id: str = "ds-sootveil-cohort",
    *,
    faction_id: str = "f-emberwrights",
) -> CuratedDatasheet:
    """007 T009: one datasheet exercising all five classes ``006`` added and the curated tree
    currently loses on a write-read round trip through ``writer.py``/``prior.py`` (research D2,
    issue #14): equipment groups (with items), ``default_equipment_state``, ``option_choices[].
    items``, and the three ``option_groups`` eligibility columns (``eligible_model_name``,
    ``eligible_max_count``, ``is_per_model``).

    A self-contained build rather than an override of :func:`datasheet` — every named field
    below (models, weapons, composition, equipment, options) is one consistent invented unit, so
    a round-trip failure on one class is legible without cross-referencing a second function's
    defaults.

    Shape: **The Sootveil Warden** (a named leader, default-equipped with a ranged and a melee
    weapon — the ``model_group`` equipment-applies-to case) leads a squad of **Sootveil
    Troopers**, up to four of whom may each individually replace their glow lance with one of two
    alternatives — a multi-item granted bundle, or no change — which is simultaneously
    ``eligible_model_name``-scoped, ``eligible_max_count``-capped, and ``is_per_model``
    distributive.

    007 US3 (T037/T040) extends this fixture with a **sixth** class the curated tree also needs
    to round-trip: ``item_constraints`` — one row linked to a weapon line and unscoped (``Storm
    maul``, ``not_replaceable``), one row scoped to a named model group and deliberately
    unlinked (``Marsh axe``, ``one_per_unit``, ``model_name`` present, ``weapon_line`` absent) —
    so a round-trip failure on either optional field is legible without a second fixture.
    """
    return CuratedDatasheet(
        datasheet_id=datasheet_id,
        edition_id=EDITION_ID,
        faction_id=faction_id,
        name="Sootveil Cohort",
        role="Battleline",
        is_battleline=True,
        models=[
            CuratedModelLine(
                line=1,
                name="Sootveil Warden",
                movement='6"',
                toughness=4,
                save="4+",
                wounds=3,
                leadership="6+",
                objective_control=1,
                base_size="32mm",
            ),
            CuratedModelLine(
                line=2,
                name="Sootveil Trooper",
                movement='6"',
                toughness=3,
                save="4+",
                wounds=1,
                leadership="7+",
                objective_control=1,
                base_size="25mm",
            ),
        ],
        weapons=[
            CuratedWeaponLine(
                line=1,
                name="Glow lance",
                is_melee=False,
                range='18"',
                attacks="2",
                skill="4+",
                strength="4",
                armour_penetration="0",
                damage="1",
            ),
            CuratedWeaponLine(
                line=2,
                name="Storm maul",
                is_melee=True,
                attacks="2",
                skill="4+",
                strength="4",
                armour_penetration="-1",
                damage="1",
            ),
            CuratedWeaponLine(
                line=3,
                name="Marsh axe",
                is_melee=True,
                attacks="2",
                skill="4+",
                strength="4",
                armour_penetration="-1",
                damage="1",
            ),
        ],
        keywords=[CuratedKeyword(keyword="INFANTRY")],
        composition=[
            CuratedCompositionEntry(
                line=1, model_name="Sootveil Warden", min_count=1, max_count=1, model_line=1
            ),
            CuratedCompositionEntry(
                line=2, model_name="Sootveil Trooper", min_count=4, max_count=8, model_line=2
            ),
        ],
        # -- 006 class 1: equipment groups (with items) ------------------------------------------
        equipment_groups=[
            CuratedEquipmentGroup(
                id=f"eq-{datasheet_id.removeprefix('ds-')}-1",
                line=1,
                applies_to=EquipmentAppliesTo.MODEL_GROUP,
                model_name="Sootveil Warden",
                composition_line=1,
                items=[
                    CuratedEquipmentItem(item_index=1, item_name="Glow lance", weapon_line=1),
                    CuratedEquipmentItem(item_index=2, item_name="Storm maul", weapon_line=2),
                ],
            ),
        ],
        # -- 006 class 2: default_equipment_state ------------------------------------------------
        default_equipment_state=DefaultEquipmentState.EXTRACTED,
        # -- 006 class 4: the three option-group eligibility columns -----------------------------
        option_groups=[
            CuratedOptionGroup(
                id=f"og-{datasheet_id.removeprefix('ds-')}-1",
                line=1,
                scope=OptionScope.UNIT,
                eligible_model_name="Sootveil Trooper",
                eligible_max_count=4,
                is_per_model=True,
            ),
        ],
        # -- 006 class 3: option_choices[].items --------------------------------------------------
        option_choices=[
            CuratedOptionChoice(
                id=f"oc-{datasheet_id.removeprefix('ds-')}-1-1",
                group_id=f"og-{datasheet_id.removeprefix('ds-')}-1",
                name="marsh axe and storm maul",
                items=[
                    CuratedOptionChoiceItem(
                        role=OptionItemRole.GRANTED,
                        item_index=1,
                        item_name="Marsh axe",
                        weapon_line=3,
                    ),
                    CuratedOptionChoiceItem(
                        role=OptionItemRole.GRANTED,
                        item_index=2,
                        item_name="Storm maul",
                        weapon_line=2,
                    ),
                ],
            ),
            CuratedOptionChoice(
                id=f"oc-{datasheet_id.removeprefix('ds-')}-1-2",
                group_id=f"og-{datasheet_id.removeprefix('ds-')}-1",
                name="No change",
                is_no_change=True,
            ),
        ],
        wargear_option_state=WargearOptionState.EXTRACTED,
        # -- 007 T037/T040: item constraints -- one linked, unscoped; one scoped, unlinked -------
        item_constraints=[
            CuratedItemConstraint(
                constraint_index=1,
                constraint_type=ItemConstraintType.NOT_REPLACEABLE,
                item_name="Storm maul",
                weapon_line=2,
            ),
            CuratedItemConstraint(
                constraint_index=2,
                constraint_type=ItemConstraintType.ONE_PER_UNIT,
                item_name="Marsh axe",
                model_name="Sootveil Warden",
            ),
        ],
        costs=costs(),
        pricing_confidence=PricingConfidence(state=PricingConfidenceState.VERIFIED),
        provenance=provenance(),
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
        "datasheets": [datasheet(cost_rows=contextual_costs())],
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
