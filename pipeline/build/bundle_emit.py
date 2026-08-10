# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the tree-to-bundle transformation
# (task T069) per curated-snapshot-format.md §4: the datasheet_cost first-copy projection, the
# full datasheet_cost_tier emission, pricing_confidence, detail_edition_code, an always-empty
# datasheetDetachmentEligibility, and a build failure on any unmapped field.
# AI-Assisted: Claude Code (model: claude-opus-5) - Emitted 004-rules-data-enrichment's first
# three additive arrays and the wargearOptionState column (004 task T032), per
# contracts/bundle-schema-delta.md §2.1-§2.3 and §3.
# AI-Assisted: Claude Code (model: claude-opus-5) - Emitted `chapterKeywords` and the
# `datasheetKeywords.keywordClass` column (004 task T040, contract §2.4 and §3).
# AI-Assisted: Claude Code (model: claude-opus-5) - Emitted `factionRules` and the
# `factions.armyRuleState` column (004 task T048, contract §2.5 and §3).
# AI-Assisted: Claude Code (model: claude-opus-5) - Emitted `detachmentRules` (004 task T055,
# contract §2.6): the name always carried from the source, the summary only once approved.
# AI-Assisted: Claude Code (model: claude-opus-5) - Emitted `keywordGlossary` (004 task T062,
# contract §2.7): an entry exists only when authored and approved, and carries none of the
# authoring state a consumer has no business reading.
# AI-Assisted: Claude Code (model: claude-opus-5) - Gave `datasheetAbilities` a scope precedence:
# where a datasheet-scoped and a core-scoped authored record collide on the consumer key, the
# datasheet-scoped one wins for that datasheet and the core one keeps serving every other.
# AI-Assisted: Claude Code (model: claude-opus-5) - Emitted `datasheetCostContexts`: the prices
# the points source states a condition for, kept out of `datasheetCosts` / `datasheetCostTiers`
# so those two arrays are unchanged for a consumer that does not read the new one.
# AI-Assisted: Claude Code (model: claude-opus-5) - Made `_rows` collapse byte-identical duplicate
# rows, with absence compared as a value, so the emitted bundle satisfies the per-key uniqueness
# the consumer contract declares (v1.3.2 guarantee 12). Rows that collide and DISAGREE are left
# alone on purpose — those are `CON-DUPLICATE-KEY`, not a dedupe.
"""Turn the curated tree into the published bundle. A pure function, and nothing else.

No network, no source re-acquisition, no input the tree does not already contain, and no clock:
the only timestamp anywhere is `snapshotMeta.publishedAt`, and that is a build **input**. Those
constraints together are what make the bundle byte-reproducible, which is what makes the
manifest checksum mean anything and what lets the publish job assert that an approved artifact
and a rebuilt artifact are the same artifact (FR-033, FR-039, SC-006).

Three mapping decisions are worth reading before changing anything here.

**The cost projection is deliberate redundancy.** `datasheetCosts` is exactly the
`copy_index_min = 1` slice of `datasheetCostTiers`. That is what lets a v1.1.0 app keep reading
`datasheet_cost` unchanged — correct for the common case, under-priced only for escalating units
past their threshold — while a v1.2.0 app reads the tiers and is exact (guarantee 7, §3.1).

**A context-qualified price never enters `datasheetCosts` or `datasheetCostTiers`.** Those two
arrays carry the price a unit costs in its own army — which is what every row in them has always
meant — and nothing else, so their key, shape and row set are untouched by `pricing_context`
arriving. A price the points source states a *condition* for goes to `datasheetCostContexts`
instead, keyed with the condition. That is what keeps this additive in effect and not only on
paper: a consumer built against v1.3.2 declares `PRIMARY KEY (datasheet_id, model_count)`, and
an extra row under that key is not a column it can ignore — it is a constraint error that
refuses the whole snapshot (reference-db-schema.md §2, guarantee 12).

**`datasheetDetachmentEligibility` is always present and always empty.** No upstream
datasheet-to-detachment join exists (research §0.1), so the consumer contract's default applies:
absence of rows means legal in any detachment of its faction. Emitting a guess would be
fabricating a rule; omitting the array would make the ingestor branch.

**An unmapped field is a build failure.** Every field of every curated model is either mapped to
a bundle column or explicitly listed as dropped, and :func:`check_mapping_totality` asserts the
partition covers the model. Add a field to a curated model without deciding what happens to it
and the build stops — which is the point, because the alternative is a value that exists in the
tree, looks published, and silently is not.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Any, Final

from pipeline.build.canonical_json import JsonValue, dumps_bundle, omit_absent
from pipeline.models.authored import ReviewState
from pipeline.models.curated import (
    CuratedChapterKeyword,
    CuratedCompositionEntry,
    CuratedDatasheet,
    CuratedDatasheetCost,
    CuratedDetachment,
    CuratedDetachmentRestriction,
    CuratedDetachmentRule,
    CuratedEdition,
    CuratedEditionRule,
    CuratedEnhancement,
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    CuratedFaction,
    CuratedGameSizeRule,
    CuratedKeyword,
    CuratedModelLine,
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
    CuratedSnapshot,
    CuratedWargearOption,
    CuratedWeaponLine,
)

BUNDLE_FORMAT_VERSION: Final = 1


class UnmappedFieldError(RuntimeError):
    """A curated field that is neither emitted nor explicitly dropped.

    Raised at build time rather than caught in review. A field nobody decided about is a field
    that silently does not reach the app, and the failure shows up as "the rule is not being
    enforced" months later rather than as a red build now.
    """


@dataclass(frozen=True, slots=True)
class BundleMeta:
    """The build inputs that are not in the tree. All five reach `snapshotMeta` verbatim."""

    rules_version_id: str
    published_at: str
    source_note: str
    schema_contract_version: int
    restriction_vocabulary_version: int

    def replace(self, **changes: object) -> BundleMeta:
        """A copy with fields changed — the readable form for tests and for a re-stamp."""
        return replace(self, **changes)  # type: ignore[arg-type]


#: curated model -> (fields emitted to the bundle, fields deliberately dropped at this boundary).
#:
#: The two sets must together cover the model exactly. Anything mapped is a consumer column;
#: anything dropped is producer-side by an explicit contract decision — `source_acquisition_id`,
#: full provenance, `force_disposition` and `is_unique` (C4/R7), `mfm_slug` and
#: `detail_source_faction_id` (C3/R6).
FIELD_MAPPING: Final[Mapping[type, tuple[set[str], set[str]]]] = {
    CuratedEdition: ({"id", "code", "name", "display_order"}, set()),
    CuratedEditionRule: ({"rule_key", "value"}, set()),
    CuratedGameSizeRule: (
        {
            "id",
            "edition_id",
            "label",
            "min_points",
            "max_points",
            "detachment_points_budget",
            "max_detachments",
            "max_enhancements",
        },
        set(),
    ),
    # 004-rules-data-enrichment moved four datasheet fields (T032), `keyword_class` (T040) and
    # `army_rule_state` (T048) from the dropped set into the mapped one, each beside its emitter.
    # Listing a field as dropped until its emitter exists is the honest state and is what this
    # partition is for: a field nobody has decided about stops the build rather than silently
    # failing to reach the app.
    CuratedFaction: (
        {"faction_id", "edition_id", "code", "name", "parent_faction_id", "army_rule_state"},
        {"mfm_slug", "detail_source_faction_id", "provenance"},
    ),
    CuratedDetachment: (
        {
            "detachment_id",
            "edition_id",
            "faction_id",
            "name",
            "detachment_points_cost",
            "is_legends",
            "restrictions",
            "rules",
        },
        {"force_disposition", "is_unique", "provenance"},
    ),
    CuratedDetachmentRule: ({"summary_key", "name"}, set()),
    CuratedDetachmentRestriction: (
        {"id", "edition_id", "detachment_id", "restriction_type", "params", "message_template"},
        set(),
    ),
    CuratedEnhancement: (
        {
            "enhancement_id",
            "edition_id",
            "detachment_id",
            "name",
            "points",
            "max_per_army",
            "eligibility",
        },
        {"provenance"},
    ),
    CuratedDatasheet: (
        {
            "datasheet_id",
            "edition_id",
            "faction_id",
            "name",
            "role",
            "is_legends",
            "is_character",
            "is_epic_hero",
            "is_battleline",
            "is_dedicated_transport",
            "max_copies_per_army",
            "damaged_threshold",
            "models",
            "weapons",
            "keywords",
            "ability_keys",
            "leader_pairs",
            "wargear_options",
            "costs",
            "composition",
            "option_groups",
            "option_choices",
            "wargear_option_state",
            # 006-unit-loadout-fidelity.
            "equipment_groups",
            "default_equipment_state",
        },
        {"pricing_confidence", "provenance"},
    ),
    CuratedCompositionEntry: (
        {"line", "model_name", "min_count", "max_count", "model_line"},
        set(),
    ),
    CuratedOptionGroup: (
        {
            "id",
            "line",
            "scope",
            "scope_n",
            "parent_group_id",
            "default_choice_id",
            "min_choices",
            "max_choices",
            # 006-unit-loadout-fidelity: the eligibility scope, as optional columns on an
            # existing array rather than a fourth member of the `scope` enum (contract §1.2).
            "eligible_model_name",
            "eligible_max_count",
            "is_per_model",
        },
        set(),
    ),
    CuratedOptionChoice: (
        {
            "id",
            "group_id",
            "name",
            "count",
            "grants_weapon_line",
            "replaces_weapon_line",
            "is_default",
            "is_no_change",
            "points_delta",
            "priced_option_id",
            # 006: emitted into its OWN array, `datasheetOptionChoiceItems`, and not as a
            # nested property -- one array per consumer table is the layout rule that keeps
            # bundleFormatVersion at 1.
            "items",
        },
        set(),
    ),
    CuratedOptionChoiceItem: (
        {"role", "item_index", "item_name", "count", "weapon_line"},
        set(),
    ),
    CuratedEquipmentGroup: (
        {"id", "line", "applies_to", "model_name", "composition_line", "items"},
        set(),
    ),
    CuratedEquipmentItem: (
        {"item_index", "item_name", "count", "weapon_line"},
        set(),
    ),
    CuratedDatasheetCost: (
        {
            "model_count",
            "copy_index_min",
            "points",
            "label",
            "pricing_context",
            "pricing_confidence",
        },
        {"source_acquisition_id"},
    ),
    CuratedModelLine: (
        {
            "line",
            "name",
            "movement",
            "toughness",
            "save",
            "invuln_save",
            "wounds",
            "leadership",
            "objective_control",
            "base_size",
        },
        set(),
    ),
    CuratedWeaponLine: (
        {
            "line",
            "name",
            "is_melee",
            "range",
            "attacks",
            "skill",
            "strength",
            "armour_penetration",
            "damage",
            "ability_keywords",
        },
        set(),
    ),
    CuratedKeyword: ({"keyword", "is_faction_keyword", "model_scope", "keyword_class"}, set()),
    CuratedChapterKeyword: (
        {"keyword", "parent_faction_id", "chapter_faction_id", "is_modelled_as_faction"},
        set(),
    ),
    CuratedWargearOption: (
        {"id", "group_key", "name", "points_delta", "max_per_unit", "models_per_instance"},
        set(),
    ),
}


def check_mapping_totality() -> None:
    """Assert every curated field is either mapped or explicitly dropped, or raise."""
    for model, (mapped, dropped) in FIELD_MAPPING.items():
        declared = set(model.model_fields)  # type: ignore[attr-defined]
        undecided = declared - mapped - dropped
        if undecided:
            raise UnmappedFieldError(
                f"{model.__name__}: {sorted(undecided)} is neither emitted to the bundle nor "
                "listed as dropped. Decide, in FIELD_MAPPING — an undecided field silently "
                "does not reach the app."
            )
        phantom = (mapped | dropped) - declared
        if phantom:
            raise UnmappedFieldError(
                f"{model.__name__}: FIELD_MAPPING names {sorted(phantom)}, which the model does "
                "not declare"
            )


def _rows(items: Sequence[Mapping[str, JsonValue]], *keys: str) -> list[dict[str, JsonValue]]:
    """Sort emitted rows by their table's primary key, and collapse identical duplicates.

    The sort is what makes the bundle byte-stable. The collapse is what makes it *ingestible*:
    ``reference-db-schema.md`` §3 declares a `PRIMARY KEY` on every table, so two rows sharing a
    key are a bundle the declared schema cannot be built from.

    **Only byte-identical rows collapse.** Two identical rows and one identical row ingest to the
    same table content, so the second is not information — it is one source page printing the
    same block twice. Rows that share a key and *disagree* are left exactly as they are, because
    choosing between them is a content decision and a silent choice is how a price nobody picked
    reaches a player. `check_bundle_primary_keys` raises the blocking `CON-DUPLICATE-KEY` for
    those, which is the layer where a human can see it.
    """
    unique: dict[tuple[tuple[str, str], ...], dict[str, JsonValue]] = {}
    for item in items:
        row = dict(item)
        unique.setdefault(row_identity(row), row)

    return sorted(
        unique.values(),
        key=lambda row: tuple(_sort_key(row.get(key)) for key in keys),
    )


def row_identity(row: Mapping[str, JsonValue]) -> tuple[tuple[str, str], ...]:
    """A row's whole content as a comparable value, with **absence as a value**.

    Absence has to compare equal to absence rather than to nothing at all, because SQLite treats
    NULLs in a unique index as distinct from each other: a consumer building the declared schema
    cannot catch a duplicate whose `model_scope` — or any other nullable key column — is absent,
    so the producer has to. The type name is carried alongside the value so `1` and `"1"` do not
    collapse into one another.
    """
    return tuple(
        sorted(
            (name, "\x00" if value is None else f"{type(value).__name__}:{value}")
            for name, value in row.items()
        )
    )


def _sort_key(value: JsonValue | None) -> tuple[int, str, int]:
    """Order rows deterministically across mixed and absent key values."""
    if value is None:
        return (0, "", 0)
    if isinstance(value, bool):
        return (1, "", int(value))
    if isinstance(value, int):
        return (1, "", value)
    return (2, str(value), 0)


def _emit_editions(snapshot: CuratedSnapshot) -> list[dict[str, JsonValue]]:
    edition = snapshot.edition
    return [
        {
            "id": edition.id,
            "code": edition.code,
            "name": edition.name,
            "displayOrder": edition.display_order,
        }
    ]


def _emit_edition_rules(snapshot: CuratedSnapshot) -> list[dict[str, JsonValue]]:
    return _rows(
        [
            {
                "editionId": snapshot.edition.id,
                "ruleKey": rule.rule_key,
                # The value becomes a canonical JSON *string*, so `value_json` is byte-stable
                # whatever the value's shape.
                "valueJson": dumps_bundle(rule.value),
            }
            for rule in snapshot.edition_rules
        ],
        "editionId",
        "ruleKey",
    )


def _emit_game_sizes(snapshot: CuratedSnapshot) -> list[dict[str, JsonValue]]:
    return _rows(
        [
            {
                "id": band.id,
                "editionId": band.edition_id,
                "label": band.label,
                "minPoints": band.min_points,
                "maxPoints": band.max_points,
                "detachmentPointsBudget": band.detachment_points_budget,
                "maxDetachments": band.max_detachments,
                "maxEnhancements": band.max_enhancements,
            }
            for band in snapshot.game_sizes
        ],
        "id",
    )


def _emit_factions(snapshot: CuratedSnapshot) -> list[dict[str, JsonValue]]:
    return _rows(
        [
            omit_absent(
                {
                    "id": faction.faction_id,
                    "editionId": faction.edition_id,
                    "code": faction.code,
                    "name": faction.name,
                    "parentFactionId": faction.parent_faction_id,
                    # Omitted = not yet curated, which is a third fact distinct from a curated
                    # `none` (contract §3). This three-state-via-absence is the whole of what
                    # FR-021 asks for, and a consumer that cannot tell the two apart shows the
                    # same empty section for a mercenary faction and an unfinished one.
                    "armyRuleState": (
                        faction.army_rule_state.value
                        if faction.army_rule_state is not None
                        else None
                    ),
                }
            )
            for faction in snapshot.factions
        ],
        "id",
    )


def _emit_detachments(snapshot: CuratedSnapshot) -> list[dict[str, JsonValue]]:
    return _rows(
        [
            {
                "id": detachment.detachment_id,
                "editionId": detachment.edition_id,
                "factionId": detachment.faction_id,
                "name": detachment.name,
                "detachmentPointsCost": detachment.detachment_points_cost,
                "isLegends": detachment.is_legends,
            }
            for detachment in snapshot.detachments
        ],
        "id",
    )


def _emit_restrictions(snapshot: CuratedSnapshot) -> list[dict[str, JsonValue]]:
    return _rows(
        [
            omit_absent(
                {
                    "id": restriction.id,
                    "editionId": restriction.edition_id,
                    "detachmentId": restriction.detachment_id,
                    "restrictionType": restriction.restriction_type,
                    "paramsJson": dumps_bundle(dict(restriction.params)),
                    "messageTemplate": restriction.message_template,
                }
            )
            for restriction in snapshot.all_restrictions
        ],
        "id",
    )


def _emit_enhancements(
    snapshot: CuratedSnapshot,
) -> tuple[list[dict[str, JsonValue]], list[dict[str, JsonValue]]]:
    enhancements = _rows(
        [
            {
                "id": enhancement.enhancement_id,
                "editionId": enhancement.edition_id,
                "detachmentId": enhancement.detachment_id,
                "name": enhancement.name,
                "points": enhancement.points,
                "maxPerArmy": enhancement.max_per_army,
            }
            for enhancement in snapshot.enhancements
        ],
        "id",
    )
    eligibility = _rows(
        [
            {
                "enhancementId": enhancement.enhancement_id,
                "ruleType": rule.rule_type,
                "value": rule.value,
            }
            for enhancement in snapshot.enhancements
            for rule in enhancement.eligibility
        ],
        "enhancementId",
        "ruleType",
        "value",
    )
    return enhancements, eligibility


def _emit_datasheets(snapshot: CuratedSnapshot) -> dict[str, list[dict[str, JsonValue]]]:
    datasheets: list[dict[str, JsonValue]] = []
    keywords: list[dict[str, JsonValue]] = []
    models: list[dict[str, JsonValue]] = []
    weapons: list[dict[str, JsonValue]] = []
    costs: list[dict[str, JsonValue]] = []
    tiers: list[dict[str, JsonValue]] = []
    contexts: list[dict[str, JsonValue]] = []
    wargear: list[dict[str, JsonValue]] = []
    leader_pairs: list[dict[str, JsonValue]] = []
    compositions: list[dict[str, JsonValue]] = []
    option_groups: list[dict[str, JsonValue]] = []
    option_choices: list[dict[str, JsonValue]] = []
    choice_items: list[dict[str, JsonValue]] = []
    equipment_groups: list[dict[str, JsonValue]] = []
    equipment_items: list[dict[str, JsonValue]] = []

    snapshot_edition = snapshot.edition.code

    for datasheet in snapshot.datasheets:
        detail_edition = datasheet.provenance.detail_edition_code
        datasheets.append(
            omit_absent(
                {
                    "id": datasheet.datasheet_id,
                    "editionId": datasheet.edition_id,
                    "factionId": datasheet.faction_id,
                    "name": datasheet.name,
                    "role": datasheet.role,
                    "isLegends": datasheet.is_legends,
                    "isCharacter": datasheet.is_character,
                    "isEpicHero": datasheet.is_epic_hero,
                    "isBattleline": datasheet.is_battleline,
                    "isDedicatedTransport": datasheet.is_dedicated_transport,
                    "maxCopiesPerArmy": datasheet.max_copies_per_army,
                    "damagedThreshold": datasheet.damaged_threshold,
                    # Omitted when the detail came from the snapshot's own edition (§5): a
                    # same-edition datasheet repeats nothing, a hybrid one says so.
                    "detailEditionCode": (
                        detail_edition if detail_edition != snapshot_edition else None
                    ),
                    # Omitted = the detail source was not consulted, which is a third fact
                    # distinct from `none` and from `partial` (004 FR-016, contract §3).
                    "wargearOptionState": (
                        datasheet.wargear_option_state.value
                        if datasheet.wargear_option_state is not None
                        else None
                    ),
                    # 006: the same three-state pattern for a second, independent fact. Omitted
                    # also means "this datasheet's composition did not resolve", in which case
                    # no equipment attaches at all (FR-016).
                    "defaultEquipmentState": (
                        datasheet.default_equipment_state.value
                        if datasheet.default_equipment_state is not None
                        else None
                    ),
                }
            )
        )

        compositions.extend(
            omit_absent(
                {
                    "datasheetId": datasheet.datasheet_id,
                    "line": entry.line,
                    "modelName": entry.model_name,
                    "minCount": entry.min_count,
                    "maxCount": entry.max_count,
                    "modelLine": entry.model_line,
                }
            )
            for entry in datasheet.composition
        )
        option_groups.extend(
            omit_absent(
                {
                    "id": group.id,
                    "datasheetId": datasheet.datasheet_id,
                    "line": group.line,
                    "scope": group.scope.value,
                    "scopeN": group.scope_n,
                    "parentGroupId": group.parent_group_id,
                    "defaultChoiceId": group.default_choice_id,
                    "minChoices": group.min_choices,
                    "maxChoices": group.max_choices,
                    # 006: the eligibility scope. Every one of these is omitted on every group
                    # `004` already publishes, so those rows stay byte-identical.
                    "eligibleModelName": group.eligible_model_name,
                    "eligibleMaxCount": group.eligible_max_count,
                    "isPerModel": group.is_per_model,
                }
            )
            for group in datasheet.option_groups
        )
        option_choices.extend(
            omit_absent(
                {
                    "id": choice.id,
                    "groupId": choice.group_id,
                    "name": choice.name,
                    "count": choice.count,
                    "grantsWeaponLine": choice.grants_weapon_line,
                    "replacesWeaponLine": choice.replaces_weapon_line,
                    # Required booleans, so they survive `omit_absent`'s None-only rule and a
                    # consumer never has to distinguish "false" from "not stated".
                    "isDefault": choice.is_default,
                    "isNoChange": choice.is_no_change,
                    # `pointsDelta` is OMITTED, never 0, when the points source does not price
                    # the choice (guarantee 10). A published 0 would read as "free".
                    "pointsDelta": choice.points_delta,
                    "pricedOptionId": choice.priced_option_id,
                }
            )
            for choice in datasheet.option_choices
        )
        # 006: one row per item, in its own sibling array keyed on the choice. Never extra
        # `datasheetOptionChoices` rows under `id` -- a v1.x consumer would render one swap as
        # four alternatives, which is a *wrong* reading rather than a lossy one (contract §1.1).
        choice_items.extend(
            omit_absent(
                {
                    "choiceId": choice.id,
                    "role": item.role.value,
                    "itemIndex": item.item_index,
                    "itemName": item.item_name,
                    "count": item.count,
                    "weaponLine": item.weapon_line,
                }
            )
            for choice in datasheet.option_choices
            for item in choice.items
        )
        equipment_groups.extend(
            omit_absent(
                {
                    "id": group.id,
                    "datasheetId": datasheet.datasheet_id,
                    "line": group.line,
                    "appliesTo": group.applies_to.value,
                    "modelName": group.model_name,
                    "compositionLine": group.composition_line,
                }
            )
            for group in datasheet.equipment_groups
        )
        equipment_items.extend(
            omit_absent(
                {
                    "groupId": group.id,
                    "itemIndex": item.item_index,
                    "itemName": item.item_name,
                    "count": item.count,
                    "weaponLine": item.weapon_line,
                }
            )
            for group in datasheet.equipment_groups
            for item in group.items
        )

        keywords.extend(
            omit_absent(
                {
                    "datasheetId": datasheet.datasheet_id,
                    "keyword": keyword.keyword,
                    "isFactionKeyword": keyword.is_faction_keyword,
                    "modelScope": keyword.model_scope,
                    # Omitted = unclassified (contract §3). An unclassified keyword's row is
                    # therefore byte-identical to what it was before classification existed,
                    # which is the whole of FR-020's guarantee.
                    "keywordClass": (
                        keyword.keyword_class.value if keyword.keyword_class is not None else None
                    ),
                }
            )
            for keyword in datasheet.keywords
        )
        models.extend(
            omit_absent(
                {
                    "datasheetId": datasheet.datasheet_id,
                    "line": model.line,
                    "name": model.name,
                    "movement": model.movement,
                    "toughness": model.toughness,
                    "save": model.save,
                    "invulnSave": model.invuln_save,
                    "wounds": model.wounds,
                    "leadership": model.leadership,
                    "objectiveControl": model.objective_control,
                    "baseSize": model.base_size,
                }
            )
            for model in datasheet.models
        )
        weapons.extend(
            omit_absent(
                {
                    "datasheetId": datasheet.datasheet_id,
                    "line": weapon.line,
                    "name": weapon.name,
                    "isMelee": weapon.is_melee,
                    "range": weapon.range,
                    "attacks": weapon.attacks,
                    "skill": weapon.skill,
                    "strength": weapon.strength,
                    "armourPenetration": weapon.armour_penetration,
                    "damage": weapon.damage,
                    # A comma-separated run of keywords, never rules text (§6).
                    "abilityKeywords": ",".join(weapon.ability_keywords) or None,
                }
            )
            for weapon in datasheet.weapons
        )
        wargear.extend(
            omit_absent(
                {
                    "id": option.id,
                    "datasheetId": datasheet.datasheet_id,
                    "groupKey": option.group_key,
                    "name": option.name,
                    "pointsDelta": option.points_delta,
                    "maxPerUnit": option.max_per_unit,
                    "modelsPerInstance": option.models_per_instance,
                }
            )
            for option in datasheet.wargear_options
        )
        leader_pairs.extend(
            {
                "leaderDatasheetId": datasheet.datasheet_id,
                "bodyguardDatasheetId": bodyguard,
            }
            for bodyguard in datasheet.leader_pairs
        )

        for cost in datasheet.costs:
            row: dict[str, JsonValue] = {
                "datasheetId": datasheet.datasheet_id,
                "modelCount": cost.model_count,
                "points": cost.points,
                "label": cost.label,
                "pricingConfidence": cost.pricing_confidence.value,
            }
            if cost.pricing_context is not None:
                contexts.append(
                    {
                        **row,
                        "pricingContext": cost.pricing_context,
                        "copyIndexMin": cost.copy_index_min,
                    }
                )
                continue
            tiers.append({**row, "copyIndexMin": cost.copy_index_min})
            if cost.copy_index_min == 1:
                costs.append(row)

    return {
        "datasheets": _rows(datasheets, "id"),
        "datasheetKeywords": _rows(keywords, "datasheetId", "keyword", "modelScope"),
        "datasheetModels": _rows(models, "datasheetId", "line"),
        "datasheetWeapons": _rows(weapons, "datasheetId", "line"),
        "datasheetCosts": _rows(costs, "datasheetId", "modelCount"),
        "datasheetCostTiers": _rows(tiers, "datasheetId", "modelCount", "copyIndexMin"),
        "datasheetCostContexts": _rows(
            contexts, "datasheetId", "pricingContext", "modelCount", "copyIndexMin"
        ),
        "datasheetWargearOptions": _rows(wargear, "id"),
        "datasheetLeaderPairs": _rows(leader_pairs, "leaderDatasheetId", "bodyguardDatasheetId"),
        "datasheetCompositions": _rows(compositions, "datasheetId", "line"),
        "datasheetOptionGroups": _rows(option_groups, "id"),
        "datasheetOptionChoices": _rows(option_choices, "id"),
        "datasheetOptionChoiceItems": _rows(choice_items, "choiceId", "role", "itemIndex"),
        "datasheetEquipmentGroups": _rows(equipment_groups, "id"),
        "datasheetEquipmentItems": _rows(equipment_items, "groupId", "itemIndex"),
    }


def _emit_faction_rules(snapshot: CuratedSnapshot) -> list[dict[str, JsonValue]]:
    """`factionRules`, sorted by `id` (contract §2.5).

    **The name is always carried; the summary is not.** A rule whose summary is not `approved`
    ships with its name alone, which is what "the entry ships with its name only" means in
    contract §3's gates-off row — and it holds in the gated-on state too, where the run is
    already refused for that entry by a blocking finding. Emitting an unapproved draft would
    publish, to every player, wording that by definition nobody has signed off.

    `id` is the record's own `summary_key`: stable, curator-visible, and already unique per rule
    across factions, so nothing has to be minted here and a rule keeps its identity across a
    rebuild without a registry.
    """
    rows: list[dict[str, JsonValue]] = []
    for faction_id in sorted(snapshot.faction_rules):
        for rule in snapshot.faction_rules[faction_id].rules:
            approved = rule.review_state is ReviewState.APPROVED and bool(rule.summary.strip())
            rows.append(
                omit_absent(
                    {
                        "id": rule.summary_key,
                        "factionId": faction_id,
                        "name": rule.name,
                        "displayOrder": rule.display_order,
                        "summary": rule.summary if approved else None,
                    }
                )
            )
    return _rows(rows, "id")


def _emit_detachment_rules(snapshot: CuratedSnapshot) -> list[dict[str, JsonValue]]:
    """`detachmentRules`, sorted by `id` (contract §2.6).

    **The name comes from the source and is always carried; the summary is authored and is not**
    (FR-022). That asymmetry is the whole shape of this array: the rows exist because a
    detachment publishes rules, not because a curator has written about them, so a detachment
    whose campaign has not started still ships every rule it owns — named, unexplained, and
    counted in the coverage report.

    `id` is the rule's own `summary_key`, minted from the detachment id and the rule name by
    :func:`pipeline.curate.summaries.detachment_rule_key`. Two detachments in different factions
    sharing a rule name therefore emit two rows with different ids, which is what a name-keyed
    array would get wrong.
    """
    rows: list[dict[str, JsonValue]] = []
    for detachment in snapshot.detachments:
        for rule in detachment.rules:
            authored = snapshot.detachment_rules.get(rule.summary_key)
            approved = (
                authored is not None
                and authored.review_state is ReviewState.APPROVED
                and bool(authored.summary.strip())
            )
            rows.append(
                omit_absent(
                    {
                        "id": rule.summary_key,
                        "detachmentId": detachment.detachment_id,
                        "name": rule.name,
                        "summary": authored.summary if approved and authored else None,
                    }
                )
            )
    return _rows(rows, "id")


def _emit_keyword_glossary(snapshot: CuratedSnapshot) -> list[dict[str, JsonValue]]:
    """`keywordGlossary`, sorted by `keywordKey` (contract §2.7).

    **An entry exists here only when authored and approved.** That is the opposite asymmetry from
    the two rule arrays, and it is right for the same reason theirs is: a rule has a *name* the
    source publishes, so it can ship half-stated, while a keyword has nothing to ship but the
    definition itself. An unauthored keyword therefore simply has **no row** — it still appears
    on its datasheets and weapons exactly as it does today, blocks nothing while the gate is off,
    and is named in the coverage report (FR-023).

    Every field of the authoring regime — the review state, the digest, the reviewer — stops at
    this boundary. A consumer has no business reading whether a definition is still in review.
    """
    return _rows(
        [
            {
                "keywordKey": entry.keyword_key,
                "displayKeyword": entry.display_keyword,
                # Required, so it survives `omit_absent`: a consumer must never read "absent"
                # as "false".
                "hasNumericParameter": entry.has_numeric_parameter,
                "summary": entry.summary,
            }
            for entry in snapshot.keyword_glossary.values()
            if entry.review_state is ReviewState.APPROVED and entry.summary.strip()
        ],
        "keywordKey",
    )


def _emit_chapter_keywords(snapshot: CuratedSnapshot) -> list[dict[str, JsonValue]]:
    """`chapterKeywords`, sorted by `keyword` (contract §2.4).

    Keyed by `keyword` alone: FR-019 guarantees one parent per chapter keyword, so resolving a
    chapter to its datasheets stays a plain join against `datasheetKeywords.keyword` with no
    composite lookup — the navigational capability US2 exists to unlock.

    A chapter the points source already models as a faction of its own **still appears here**,
    flagged (FR-018). One mechanism for every chapter grouping; the flag plus the blocking
    parent-agreement check are what stop the two representations double counting.
    """
    return _rows(
        [
            omit_absent(
                {
                    "keyword": chapter.keyword,
                    "parentFactionId": chapter.parent_faction_id,
                    "chapterFactionId": chapter.chapter_faction_id,
                    # Required, so it survives `omit_absent`'s None-only rule: a consumer must
                    # never have to read "absent" as "false".
                    "isModelledAsFaction": chapter.is_modelled_as_faction,
                }
            )
            for chapter in snapshot.chapter_keywords
        ],
        "keyword",
    )


def _emit_abilities(snapshot: CuratedSnapshot) -> list[dict[str, JsonValue]]:
    """Expand each datasheet's `ability_keys` against the authored summaries.

    The authored records are keyed per **ability**; the consumer contract wants one row per
    `(datasheet, ability)` with a `NOT NULL` summary. This is where the one becomes the other,
    which is what keeps the editorial cost proportional to the number of distinct abilities
    rather than to the number of bindings (data-model.md §4).

    A key with no summary is not emitted as an empty string: `SUM-MISSING` is a blocking finding
    of its own (V7, US5), and a blank summary would satisfy the schema while telling a player
    nothing.

    **The narrower record wins a name it shares.** The consumer's key is `(datasheet_id, name)`
    and excludes `ability_type` on purpose (`reference-db-schema.md` §3.8), so a datasheet that
    binds both `core:super-heavy-walker` and `datasheet:super-heavy-walker` — four Chaos
    datasheets do — offers two rows for one key with two different authored summaries. Where one
    of them is scoped more narrowly than the others, that one is what the datasheet carries: an
    author who wrote a record *for this datasheet* was answering the question this row asks, and
    the core record was answering a more general one. The core record is untouched and keeps
    serving every other datasheet bound to it.

    Deliberately not a tie-break of last resort. Precedence resolves a collision only when the
    narrowest scope holds exactly **one** record; two datasheet-scoped records of one name, or
    two core-scoped ones, are a question about the data and both still ship, so
    `check_bundle_primary_keys` blocks the release rather than the emitter choosing (V20).
    """
    rows: list[dict[str, JsonValue]] = []
    for datasheet in snapshot.datasheets:
        for key in datasheet.ability_keys:
            summary = snapshot.ability_summaries.get(key)
            if summary is None or not summary.summary.strip():
                continue
            rows.append(
                {
                    "datasheetId": datasheet.datasheet_id,
                    "name": summary.name,
                    "abilityType": key.split(":", 1)[0],
                    "summary": summary.summary,
                }
            )
    return _rows(_narrowest_scope_wins(rows), "datasheetId", "name")


#: How narrowly an `ability_type` is scoped. Higher is narrower, and the narrowest record that
#: is *alone* at its scope wins the consumer key it shares (§3.8).
_ABILITY_SCOPE: Final[Mapping[str, int]] = {"core": 0, "faction": 1, "datasheet": 2}


def _narrowest_scope_wins(rows: Sequence[dict[str, JsonValue]]) -> list[dict[str, JsonValue]]:
    """Resolve `(datasheetId, name)` collisions by scope, or leave them for V20 to block."""
    grouped: dict[tuple[JsonValue, JsonValue], list[dict[str, JsonValue]]] = {}
    for row in rows:
        grouped.setdefault((row["datasheetId"], row["name"]), []).append(row)

    resolved: list[dict[str, JsonValue]] = []
    for group in grouped.values():
        if len(group) == 1:
            resolved.extend(group)
            continue
        narrowest = max(_ABILITY_SCOPE.get(str(row["abilityType"]), -1) for row in group)
        winners = [
            row for row in group if _ABILITY_SCOPE.get(str(row["abilityType"]), -1) == narrowest
        ]
        resolved.extend(winners if len(winners) == 1 else group)
    return resolved


def emit_bundle(snapshot: CuratedSnapshot, meta: BundleMeta) -> dict[str, Any]:
    """Transform the curated tree into the published bundle."""
    check_mapping_totality()

    enhancements, eligibility = _emit_enhancements(snapshot)
    datasheet_arrays = _emit_datasheets(snapshot)

    return {
        "bundleFormatVersion": BUNDLE_FORMAT_VERSION,
        "snapshotMeta": {
            "schemaContractVersion": meta.schema_contract_version,
            "restrictionVocabularyVersion": meta.restriction_vocabulary_version,
            "rulesVersionId": meta.rules_version_id,
            "publishedAt": meta.published_at,
            "sourceNote": meta.source_note,
        },
        "editions": _emit_editions(snapshot),
        "editionRules": _emit_edition_rules(snapshot),
        "gameSizeRules": _emit_game_sizes(snapshot),
        "factions": _emit_factions(snapshot),
        "detachments": _emit_detachments(snapshot),
        "detachmentRestrictions": _emit_restrictions(snapshot),
        "enhancements": enhancements,
        "enhancementEligibility": eligibility,
        "datasheetAbilities": _emit_abilities(snapshot),
        "chapterKeywords": _emit_chapter_keywords(snapshot),
        "factionRules": _emit_faction_rules(snapshot),
        "detachmentRules": _emit_detachment_rules(snapshot),
        "keywordGlossary": _emit_keyword_glossary(snapshot),
        **datasheet_arrays,
        # Always present, always empty: no upstream join exists, so the contract's default
        # applies (absence = legal in any detachment of its faction). Fabricating rows would be
        # inventing a rule; omitting the array would make the ingestor branch.
        "datasheetDetachmentEligibility": [],
    }
