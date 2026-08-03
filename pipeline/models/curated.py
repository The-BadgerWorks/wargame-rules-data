# AI-Assisted: Claude Code (model: claude-opus-5) - Defined the curated records of
# data-model.md §3 (task T022) against reference-db-schema.md v1.2.0: copy-indexed pricing with
# copy_index_min, per-row pricing_confidence, and the curated-only fields the bundle drops.
"""Curated records — the canonical reviewable state, machine-written into ``data/``.

Every record here maps to a row in the consumer schema; the field-level mapping is
``curated-snapshot-format.md`` §4. Fields marked **curated-only** stay in the tree and are
deliberately not emitted, because no consumer reads them — ``force_disposition`` and
``is_unique`` (C4/R7), ``mfm_slug`` and ``detail_source_faction_id`` (C3/R6),
``source_acquisition_id``, and the full :class:`~pipeline.models.provenance.EntityProvenance`.

Two contract points worth stating where the types live:

* An optional value that has not been curated is ``None`` here and **omitted** on the way out —
  never a guess, never a default, never a sentinel (FR-019, §5). ``max_copies_per_army`` is
  absent rather than ``1``; ``invuln_save`` is absent rather than ``"-"``.
* ``costs[]`` is copy-indexed. ``copy_index_min`` is the 1-based ordinal of a copy of the
  datasheet within one army, counted across all squad sizes; a row applies to that copy and
  every later one. ``model_count`` values are band **lower bounds** — a unit of *n* models pays
  the smallest listed count ≥ *n* (§3.1, §3.2; C1/R2, C2/R5).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from pipeline.build.canonical_json import JsonValue
from pipeline.models.authored import AbilitySummary
from pipeline.models.provenance import EntityProvenance, PricingConfidence, PricingConfidenceState

#: ``restriction_type`` is a closed set at ``restriction_vocabulary_version`` 1
#: (``reference-db-schema.md`` §4). An out-of-vocabulary value is the blocking
#: ``CON-RESTRICTION-VOCAB``; it is never passed through.
RESTRICTION_VOCABULARY: Final[frozenset[str]] = frozenset(
    {
        "max_copies_per_datasheet",
        "max_units_with_keyword",
        "min_units_with_keyword",
        "requires_keyword_in_army",
        "forbids_keyword_in_army",
        "forbids_datasheet",
        "legends_allowed",
        "max_enhancements",
        "unique_epic_heroes",
    }
)

#: ``enhancement_eligibility.rule_type`` is likewise closed (``reference-db-schema.md`` §3).
ELIGIBILITY_RULE_TYPES: Final[frozenset[str]] = frozenset(
    {"requires_keyword", "forbids_keyword", "datasheet_allowlist"}
)


class _Curated(BaseModel):
    """Base for curated records: frozen, unknown fields rejected."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class CuratedEditionRule(_Curated):
    """One non-tabular construction rule. ``value`` is serialised into ``value_json``."""

    rule_key: str
    value: JsonValue


class CuratedEdition(_Curated):
    """``edition.json``'s edition row."""

    id: str
    code: str
    name: str
    display_order: int


class CuratedGameSizeRule(_Curated):
    """One point band. Bands must be contiguous, non-overlapping, and cover
    ``reference-db-schema.md`` §3.4's declared ``500``..``5000`` range end to end (V3, C7/R9)."""

    id: str
    edition_id: str
    label: str
    min_points: int
    max_points: int
    detachment_points_budget: int
    max_detachments: int
    max_enhancements: int


class CuratedFaction(_Curated):
    """One faction. ``parent_faction_id`` carries the points source's chapter split (C3/R6)."""

    faction_id: str
    edition_id: str
    code: str
    name: str
    parent_faction_id: str | None = None
    mfm_slug: str = Field(description="CURATED-ONLY provenance key, from curation/faction-map.json")
    detail_source_faction_id: str = Field(description="CURATED-ONLY provenance key")
    provenance: EntityProvenance


class CuratedDetachmentRestriction(_Curated):
    """A machine-evaluable constraint. ``detachment_id`` absent = an edition-wide rule."""

    id: str
    edition_id: str
    detachment_id: str | None = None
    restriction_type: str = Field(description="closed vocabulary — RESTRICTION_VOCABULARY")
    params: Mapping[str, JsonValue] = Field(default_factory=dict)
    message_template: str = Field(
        description="AUTHORED by the producer, short and mechanical; never publisher wording"
    )


class CuratedDetachment(_Curated):
    """One detachment and its restrictions."""

    detachment_id: str
    edition_id: str
    faction_id: str
    name: str
    detachment_points_cost: int
    is_legends: bool = False
    force_disposition: str | None = Field(default=None, description="CURATED-ONLY (C4/R7)")
    is_unique: bool | None = Field(default=None, description="CURATED-ONLY (C4/R7)")
    restrictions: Sequence[CuratedDetachmentRestriction] = ()
    provenance: EntityProvenance


class CuratedEnhancementEligibility(_Curated):
    """One eligibility rule. No rows for an enhancement = offered to any Character."""

    rule_type: str = Field(description="requires_keyword | forbids_keyword | datasheet_allowlist")
    value: str


class CuratedEnhancement(_Curated):
    """One enhancement. ``detachment_id`` is **required** — an orphan is blocking (FR-030)."""

    enhancement_id: str
    edition_id: str
    detachment_id: str
    name: str
    points: int
    max_per_army: int = 1
    eligibility: Sequence[CuratedEnhancementEligibility] = ()
    provenance: EntityProvenance


class CuratedModelLine(_Curated):
    """One model profile, sorted by ``line``."""

    line: int
    name: str
    movement: str
    toughness: int
    save: str
    invuln_save: str | None = None
    wounds: int
    leadership: str
    objective_control: int
    base_size: str | None = None


class CuratedWeaponLine(_Curated):
    """One weapon profile, sorted by ``line``."""

    line: int
    name: str
    is_melee: bool
    range: str | None = None
    attacks: str
    skill: str
    strength: str
    armour_penetration: str
    damage: str
    ability_keywords: Sequence[str] = ()


class CuratedKeyword(_Curated):
    """One keyword binding, sorted by ``(keyword, model_scope)``."""

    keyword: str
    is_faction_keyword: bool = False
    model_scope: str | None = None


class CuratedWargearOption(_Curated):
    """One **cost-bearing** option. Options with no point effect are intentionally absent.

    ``points_delta`` comes from the points source while the structure comes from the detail
    source (C8/R3). An option whose structure is known but whose cost the points source does not
    publish is the advisory ``CON-WARGEAR-COST-MISSING`` — a finding, never a zero.
    """

    id: str
    group_key: str
    name: str
    points_delta: int
    max_per_unit: int | None = None
    models_per_instance: int | None = None


class CuratedDatasheetCost(_Curated):
    """One cost row, keyed ``(model_count, copy_index_min)`` within its datasheet.

    A ``copy_index_min = 1`` row must exist for every ``model_count`` — the tier table would
    otherwise be unresolvable at lookup time, which is the blocking ``PRC-TIER-INCOMPLETE``
    (contract v1.2.0 guarantee 7).
    """

    model_count: int
    copy_index_min: int = Field(default=1, ge=1, description="1-based copy ordinal; 1 = base tier")
    points: int
    label: str = Field(description="'5 models' — the band's LOWER bound (C2/R5)")
    pricing_confidence: PricingConfidenceState = PricingConfidenceState.VERIFIED
    source_acquisition_id: str | None = Field(default=None, description="CURATED-ONLY")


class CuratedDatasheet(_Curated):
    """One datasheet and all of its child rows — one file, one diffable unit (FR-016)."""

    datasheet_id: str
    edition_id: str
    faction_id: str
    name: str = Field(description="current display name; a change here IS a rename (FR-015)")
    role: str | None = None
    is_legends: bool = False
    is_character: bool = False
    is_epic_hero: bool = False
    is_battleline: bool = False
    is_dedicated_transport: bool = False
    max_copies_per_army: int | None = Field(
        default=None, description="ABSENT unless authored — never guessed (FR-019)"
    )
    damaged_threshold: int | None = None
    models: Sequence[CuratedModelLine] = ()
    weapons: Sequence[CuratedWeaponLine] = ()
    keywords: Sequence[CuratedKeyword] = ()
    ability_keys: Sequence[str] = Field(
        default=(),
        description="KEYS, not text. Summaries live in curation/abilities/<faction-id>.json and "
        "are resolved at build time — which is what keeps authored content out of the "
        "machine-written tree entirely.",
    )
    leader_pairs: Sequence[str] = ()
    wargear_options: Sequence[CuratedWargearOption] = ()
    costs: Sequence[CuratedDatasheetCost] = Field(
        default=(), description="≥ 1 required; none is the blocking CON-NO-COST (FR-030)"
    )
    pricing_confidence: PricingConfidence
    provenance: EntityProvenance


class CuratedSnapshot(_Curated):
    """One complete curated data set: everything ``validate`` checks and ``build`` emits.

    A container rather than a stage-local tuple because three stages need the *same* view of it
    — ``curate`` writes it to the tree, ``validate`` checks it whole (referential integrity is
    not checkable a file at a time), and ``build`` transforms it into the bundle. Passing the
    pieces around separately is how one of the three ends up checking a set the other two did
    not build.

    ``ability_summaries`` is authored content, keyed per ability rather than per
    ``(datasheet, ability)`` binding (data-model.md §4). It travels with the snapshot because
    the builder expands the keys into per-datasheet rows at emission time — the consumer
    contract requires a summary on every binding, while the editorial cost is paid once per
    distinct ability.
    """

    edition: CuratedEdition
    edition_rules: Sequence[CuratedEditionRule] = ()
    game_sizes: Sequence[CuratedGameSizeRule] = ()
    factions: Sequence[CuratedFaction] = ()
    detachments: Sequence[CuratedDetachment] = ()
    enhancements: Sequence[CuratedEnhancement] = ()
    datasheets: Sequence[CuratedDatasheet] = ()
    restrictions: Sequence[CuratedDetachmentRestriction] = Field(
        default=(),
        description="edition-wide restrictions; a detachment's own live on the detachment",
    )
    ability_summaries: Mapping[str, AbilitySummary] = Field(
        default_factory=dict, description="ability_key -> approved summary (FR-020)"
    )

    @property
    def all_restrictions(self) -> list[CuratedDetachmentRestriction]:
        """Edition-wide and per-detachment restrictions in one list, sorted by id."""
        collected = list(self.restrictions)
        for detachment in self.detachments:
            collected.extend(detachment.restrictions)
        return sorted(collected, key=lambda restriction: restriction.id)
