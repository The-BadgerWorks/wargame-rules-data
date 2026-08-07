# AI-Assisted: Claude Code (model: claude-opus-5) - The one enriched snapshot Phase 8's four
# proofs share (004 tasks T065-T067, T071): every one of the seven new arrays non-empty, all
# three additive columns set, and an army that prices against it, so "additive" is proven against
# a bundle that actually carries the additions rather than against an empty one.
"""A snapshot carrying **every** addition `004-rules-data-enrichment` makes.

Phase 8's whole point is that the additions are invisible to a consumer that does not read them.
That claim is worth nothing against a bundle whose new arrays are empty — an ingestor ignores an
empty array by accident as readily as by design — so the additive proof, the conformance proof,
the determinism proof and the FR-034 consumer dry-run all build from this one snapshot, and it is
deliberately dense: seven non-empty arrays, three set columns, nested option groups, an unpriced
choice, an unapproved summary, and a keyword nothing defines.

Everything here is invented, like every fixture in this repository.

The pricing is chosen so the FR-034 dry-run exercises the awkward cases rather than the easy one:
an escalating copy tier, a squad size that is not a listed band, a cost-bearing wargear option,
two detachments, and an enhancement in each.
"""

from __future__ import annotations

from pipeline.models.authored import (
    DetachmentRuleSummary,
    FactionRuleFile,
    FactionRuleSummary,
    GlossaryEntry,
    ReviewState,
)
from pipeline.models.curated import (
    ArmyRuleState,
    CuratedChapterKeyword,
    CuratedCompositionEntry,
    CuratedDatasheet,
    CuratedDetachment,
    CuratedDetachmentRule,
    CuratedEnhancement,
    CuratedKeyword,
    CuratedModelLine,
    CuratedOptionChoice,
    CuratedOptionGroup,
    CuratedSnapshot,
    CuratedWargearOption,
    CuratedWeaponLine,
    KeywordClass,
    OptionScope,
    WargearOptionState,
)
from tests import factories

PARENT_FACTION = "f-glimmerfen-covenant"
CHAPTER_FACTION = "f-glimmerfen-thornlight"
"""Sorts **after** its parent, deliberately.

`factions` is sorted by id and the consumer schema's `parent_faction_id` is a real foreign
key, so a chapter whose id sorted before its parent's would fail to ingest on the forward
reference. That hazard predates this feature and is not what the dry-run is about, so the
fixture stays out of its way rather than dressing it up as an enrichment failure.
"""

SUMMARY = "Invented mechanics-only summary authored for this data set from the mechanic."


def _model(line: int, name: str) -> CuratedModelLine:
    return CuratedModelLine(
        line=line,
        name=name,
        movement='6"',
        toughness=4,
        save="3+",
        wounds=2,
        leadership="6+",
        objective_control=2,
        base_size="32mm",
    )


def _weapon(line: int, name: str, *, abilities: tuple[str, ...] = ()) -> CuratedWeaponLine:
    return CuratedWeaponLine(
        line=line,
        name=name,
        is_melee=False,
        range='24"',
        attacks="2",
        skill="3+",
        strength="5",
        armour_penetration="-1",
        damage="1",
        ability_keywords=list(abilities),
    )


def _warden() -> CuratedDatasheet:
    """The dense one: composition, a nested option group, an unpriced choice, a priced link."""
    return factories.datasheet(
        "ds-fen-warden", faction_id=PARENT_FACTION, ability_keys=("core:tidewalk",)
    ).model_copy(
        update={
            "name": "FEN WARDEN",
            "models": [_model(1, "Fen Warden"), _model(2, "Fen Warden Prime")],
            "weapons": [
                _weapon(1, "Fen glaive", abilities=("SUSTAINED HITS 1",)),
                _weapon(2, "Marsh lance", abilities=("LETHAL HITS",)),
            ],
            "keywords": [
                CuratedKeyword(keyword="INFANTRY", keyword_class=KeywordClass.UNIT),
                CuratedKeyword(
                    keyword="GLIMMERFEN COVENANT",
                    is_faction_keyword=True,
                    keyword_class=KeywordClass.FACTION,
                ),
                CuratedKeyword(keyword="THORNLIGHT CHORUS", keyword_class=KeywordClass.CHAPTER),
                # Deliberately unclassified: it still ships, still counts, and blocks nothing.
                CuratedKeyword(keyword="TIDEWALK"),
            ],
            "composition": [
                CuratedCompositionEntry(
                    line=1, model_name="Fen Warden Prime", min_count=1, max_count=1, model_line=2
                ),
                CuratedCompositionEntry(
                    line=2, model_name="Fen Warden", min_count=4, max_count=9, model_line=1
                ),
            ],
            "option_groups": [
                CuratedOptionGroup(
                    id="og-fen-warden-1",
                    line=1,
                    scope=OptionScope.UNIT,
                    default_choice_id="oc-fen-warden-1-1",
                    min_choices=0,
                    max_choices=1,
                ),
                CuratedOptionGroup(
                    id="og-fen-warden-2",
                    line=2,
                    scope=OptionScope.PER_N_MODELS,
                    scope_n=5,
                    parent_group_id="og-fen-warden-1",
                ),
            ],
            "option_choices": [
                CuratedOptionChoice(
                    id="oc-fen-warden-1-1",
                    group_id="og-fen-warden-1",
                    name="No change",
                    is_default=True,
                    is_no_change=True,
                ),
                CuratedOptionChoice(
                    id="oc-fen-warden-1-2",
                    group_id="og-fen-warden-1",
                    name="Warden banner",
                    count=1,
                    points_delta=15,
                    priced_option_id="wo-fen-warden-banner",
                ),
                # No `points_delta` at all: the points source does not price it, and emitting `0`
                # would be a fabricated cost (FR-013, guarantee 10).
                CuratedOptionChoice(
                    id="oc-fen-warden-2-1",
                    group_id="og-fen-warden-2",
                    name="Marsh lance",
                    count=1,
                    grants_weapon_line=2,
                ),
            ],
            "wargear_options": [
                CuratedWargearOption(
                    id="wo-fen-warden-banner",
                    group_key="banner",
                    name="Warden banner",
                    points_delta=15,
                    max_per_unit=1,
                )
            ],
            "wargear_option_state": WargearOptionState.EXTRACTED,
            "costs": factories.costs(((1, 5, 90), (1, 10, 175), (3, 5, 100))),
        }
    )


def _rider() -> CuratedDatasheet:
    """The chapter's own unit, and the one whose option set failed to extract."""
    return factories.datasheet(
        "ds-thornlight-rider", faction_id=CHAPTER_FACTION, ability_keys=("core:tidewalk",)
    ).model_copy(
        update={
            "name": "THORNLIGHT RIDER",
            "keywords": [
                CuratedKeyword(keyword="MOUNTED", keyword_class=KeywordClass.UNIT),
                CuratedKeyword(keyword="THORNLIGHT CHORUS", keyword_class=KeywordClass.CHAPTER),
                # Nothing defines this one, which is the "undefined keyword ships unchanged" case.
                CuratedKeyword(keyword="Duskrail", keyword_class=KeywordClass.UNIT),
            ],
            "weapons": [_weapon(1, "Thornlight lance", abilities=("TWIN-LINKED",))],
            "composition": [
                CuratedCompositionEntry(
                    line=1, model_name="Thornlight Rider", min_count=3, max_count=3
                )
            ],
            # `partial`, not `none`: the difference between "this unit has no options" and
            # "this unit's options did not extract" is exactly what the column is for (FR-016).
            "wargear_option_state": WargearOptionState.PARTIAL,
            # Priced twice over: its own price, and the price a stated condition puts on it.
            # The second set is what `datasheetCostContexts` carries, and keeping it off
            # `datasheetCosts` is what lets the v1.2.0 consumer below ingest this bundle at all.
            "costs": factories.costs(((1, 3, 110),))
            + factories.costs(((1, 3, 130),), pricing_context="every-model-has-emberbound"),
        }
    )


def _detachments() -> list[CuratedDetachment]:
    vigil = factories.detachment("d-fenlight-vigil", faction_id=PARENT_FACTION).model_copy(
        update={
            "name": "Fenlight Vigil",
            "detachment_points_cost": 1,
            "rules": [
                CuratedDetachmentRule(
                    summary_key="detachment:d-fenlight-vigil:veiled-advance",
                    name="Veiled Advance",
                ),
                # No authored record: it still ships, named, and blocks nothing.
                CuratedDetachmentRule(
                    summary_key="detachment:d-fenlight-vigil:fenlight-muster",
                    name="Fenlight Muster",
                ),
            ],
        }
    )
    charge = factories.detachment("d-thornlight-charge", faction_id=CHAPTER_FACTION).model_copy(
        update={
            "name": "Thornlight Charge",
            "detachment_points_cost": 2,
            "rules": [
                CuratedDetachmentRule(
                    summary_key="detachment:d-thornlight-charge:sundering-tide",
                    name="Sundering Tide",
                )
            ],
        }
    )
    return [vigil, charge]


def _detachment_rules() -> dict[str, DetachmentRuleSummary]:
    return {
        "detachment:d-fenlight-vigil:veiled-advance": DetachmentRuleSummary(
            summary_key="detachment:d-fenlight-vigil:veiled-advance",
            detachment_id="d-fenlight-vigil",
            name="Veiled Advance",
            summary=SUMMARY,
            review_state=ReviewState.APPROVED,
            mechanic_digest="c" * 32,
            reviewed_by="second-curator",
        ),
        # Authored but not signed off, so the bundle carries its name and not its wording.
        "detachment:d-thornlight-charge:sundering-tide": DetachmentRuleSummary(
            summary_key="detachment:d-thornlight-charge:sundering-tide",
            detachment_id="d-thornlight-charge",
            name="Sundering Tide",
            summary=SUMMARY,
            review_state=ReviewState.DRAFT,
            mechanic_digest="a" * 32,
        ),
    }


def _faction_rules() -> dict[str, FactionRuleFile]:
    return {
        PARENT_FACTION: FactionRuleFile(
            faction_id=PARENT_FACTION,
            army_rule_state=ArmyRuleState.PRESENT.value,
            rules=[
                FactionRuleSummary(
                    summary_key=f"faction:{PARENT_FACTION}:tidewalk",
                    name="Tidewalk",
                    display_order=1,
                    summary=SUMMARY,
                    review_state=ReviewState.APPROVED,
                    mechanic_digest="b" * 32,
                    reviewed_by="second-curator",
                )
            ],
        ),
        CHAPTER_FACTION: FactionRuleFile(
            faction_id=CHAPTER_FACTION, army_rule_state=ArmyRuleState.NONE.value
        ),
    }


def _glossary() -> dict[str, GlossaryEntry]:
    def entry(key: str, display: str, *, numeric: bool = False) -> GlossaryEntry:
        return GlossaryEntry(
            summary_key=f"glossary:{key}",
            keyword_key=key,
            display_keyword=display,
            has_numeric_parameter=numeric,
            name=display.title(),
            summary=SUMMARY,
            review_state=ReviewState.APPROVED,
            mechanic_digest="d" * 32,
            reviewed_by="second-curator",
        )

    return {
        "sustained hits": entry("sustained hits", "SUSTAINED HITS", numeric=True),
        "lethal hits": entry("lethal hits", "LETHAL HITS"),
        "twin linked": entry("twin linked", "TWIN-LINKED"),
        "tidewalk": entry("tidewalk", "TIDEWALK"),
    }


def enriched_snapshot() -> CuratedSnapshot:
    """One snapshot carrying every addition of `004-rules-data-enrichment`."""
    return factories.snapshot(
        factions=[
            factories.faction(PARENT_FACTION).model_copy(
                update={"army_rule_state": ArmyRuleState.PRESENT}
            ),
            factories.faction(CHAPTER_FACTION, parent=PARENT_FACTION).model_copy(
                update={"army_rule_state": ArmyRuleState.NONE}
            ),
        ],
        detachments=_detachments(),
        enhancements=[
            factories.enhancement("e-fenlight-oath", detachment_id="d-fenlight-vigil"),
            CuratedEnhancement(
                enhancement_id="e-thornbound-ward",
                edition_id=factories.EDITION_ID,
                detachment_id="d-thornlight-charge",
                name="Thornbound Ward",
                points=20,
                provenance=factories.provenance(),
            ),
        ],
        datasheets=[_warden(), _rider()],
        chapter_keywords=[
            CuratedChapterKeyword(
                keyword="THORNLIGHT CHORUS",
                parent_faction_id=PARENT_FACTION,
                chapter_faction_id=CHAPTER_FACTION,
                is_modelled_as_faction=True,
            ),
            # A chapter the points source does NOT model as a faction of its own: enumerated by
            # the same mechanism, flagged differently (FR-018).
            CuratedChapterKeyword(keyword="BRACKLIGHT HOST", parent_faction_id=PARENT_FACTION),
        ],
        ability_summaries=factories.summaries(("core:tidewalk",)),
        faction_rules=_faction_rules(),
        detachment_rules=_detachment_rules(),
        keyword_glossary=_glossary(),
    )


#: The FR-034 dry-run army: two detachments, a unit taken past its escalating tier, a squad size
#: that is not a listed band, the cost-bearing wargear option, and an enhancement from each.
#:
#: 90 + 90 + 100 (the third copy crosses the `copy_index_min = 3` tier) + 25 + 175 (six models
#: round up to the 10-model band) + 15 (wargear) + 110 + 20.
EXERCISE_ARMY: tuple[dict[str, object], ...] = (
    {"kind": "detachment", "id": "d-fenlight-vigil"},
    {"kind": "datasheet", "id": "ds-fen-warden", "models": 5},
    {"kind": "datasheet", "id": "ds-fen-warden", "models": 5},
    {"kind": "datasheet", "id": "ds-fen-warden", "models": 5},
    {"kind": "enhancement", "id": "e-fenlight-oath"},
    {"kind": "detachment", "id": "d-thornlight-charge"},
    {"kind": "datasheet", "id": "ds-fen-warden", "models": 6},
    {"kind": "wargear", "id": "wo-fen-warden-banner"},
    {"kind": "datasheet", "id": "ds-thornlight-rider", "models": 3},
    {"kind": "enhancement", "id": "e-thornbound-ward"},
)

EXERCISE_ARMY_TOTAL = 90 + 90 + 100 + 25 + 175 + 15 + 110 + 20
