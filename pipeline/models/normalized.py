# AI-Assisted: Claude Code (model: claude-opus-5) - Defined the eleven normalized record types
# of data-model.md §2 (task T021), the first records that may cross into committed storage and
# therefore the first with no field typed to hold prose (research D8, control 1).
"""Normalized records — the first records that may cross into committed storage.

Produced by ``normalize``, the only stage permitted to read the prose fields of
:mod:`pipeline.models.source`. **Nothing here is typed to hold prose**: every field is an id, a
name, a number, an enumerated code, or a digest. That is control 1 of research D8 — the policy
holds because there is nowhere to put a violation, not because a reviewer noticed.

``normalized_*_name`` values are produced by the D5 ladder: NFKC, strip combining marks,
casefold, typographic punctuation to ASCII, drop a leading ``the ``, collapse runs of
non-alphanumerics to a single space, trim. **No stemming, no singularisation, no synonym
expansion** — those introduce the silent wrong matches the ladder exists to avoid.
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AbilityType(StrEnum):
    """The consumer contract's closed ``ability_type`` vocabulary.

    Any source value outside the explicit mapping table raises ``DQ-ABILITY-TYPE`` and is never
    passed through — this is where the observed Cyrillic classification artefacts stop
    (research §0.1, FR-006).
    """

    CORE = "core"
    FACTION = "faction"
    DATASHEET = "datasheet"


class ParseConfidence(StrEnum):
    """How well a free-text unit composition yielded a model count (FR-027).

    ``unparsed`` feeds a standing advisory class, not a run failure: at a few thousand
    datasheets a residual unparseable tail is a budgeted cost, not a bug.
    """

    EXACT = "exact"
    RANGE = "range"
    UNPARSED = "unparsed"


class _Normalized(BaseModel):
    """Base for normalized records: frozen, unknown fields rejected."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class NormalizedUnitCost(_Normalized):
    """Key ``(source_faction_ref, normalized_unit_name, tier_index, model_count)``."""

    source_faction_ref: str
    normalized_unit_name: str
    tier_index: int = Field(description="1-based; > 1 only for an escalating price table (C1)")
    model_count: int
    points: int
    raw_display_name: str = Field(description="the source's own casing, a name only")
    tier_label: str = Field(description="the cost-table label literal tier detection keyed on")


class NormalizedDetachment(_Normalized):
    """Key ``(source_faction_ref, normalized_detachment_name)``."""

    source_faction_ref: str
    normalized_detachment_name: str
    display_name: str
    dp_cost: int
    force_disposition: str | None = Field(default=None, description="curated-only (C4/R7)")
    is_unique: bool | None = Field(default=None, description="curated-only (C4/R7)")


class NormalizedEnhancement(_Normalized):
    """Key ``(detachment_ref, normalized_enhancement_name)``."""

    detachment_ref: str
    normalized_enhancement_name: str
    display_name: str
    points: int


class NormalizedDatasheet(_Normalized):
    """Key ``(wahapedia_datasheet_id)`` — the detail source's own identity."""

    wahapedia_datasheet_id: str
    display_name: str
    faction_id: str = Field(description="the DETAIL source's faction id, not a curated id")
    role: str | None = None
    is_legends: bool = False
    is_virtual: bool = False
    damaged_threshold: int | None = None


class NormalizedModelLine(_Normalized):
    """Key ``(wahapedia_datasheet_id, line)`` — one model profile."""

    wahapedia_datasheet_id: str
    line: int
    name: str
    movement: str = Field(description="printed form, e.g. '6\"'")
    toughness: int
    save: str
    invuln_save: str | None = None
    wounds: int
    leadership: str
    objective_control: int
    base_size: str | None = None


class NormalizedWeaponLine(_Normalized):
    """Key ``(wahapedia_datasheet_id, line)`` — one weapon profile."""

    wahapedia_datasheet_id: str
    line: int
    name: str
    is_melee: bool
    range: str | None = None
    attacks: str
    skill: str
    strength: str
    armour_penetration: str
    damage: str
    ability_keywords: Sequence[str] = Field(
        default=(), description="keywords only — 'lethal hits', 'rapid fire 1'; never rules text"
    )


class NormalizedAbilityBinding(_Normalized):
    """Key ``(wahapedia_datasheet_id, ability_key)`` — a datasheet's binding to an ability.

    ``mechanic_digest`` is a **keyed, truncated** digest (HMAC-SHA256 under a repository-held
    key, 128 bits) over the hard-normalised mechanic text, computed while that text exists only
    in ephemeral storage and then discarded. An unkeyed hash of a short, publicly known string
    is a verification oracle for it; a keyed one is neither invertible nor confirmable, which is
    what makes FR-024's change detection compatible with FR-013 (C6/R8, research D6).
    """

    wahapedia_datasheet_id: str
    ability_key: str = Field(description="e.g. 'core:deep-strike' — a key, never text")
    display_name: str
    ability_type: AbilityType
    mechanic_digest: str


class NormalizedKeyword(_Normalized):
    """Key ``(wahapedia_datasheet_id, keyword, model_scope)``."""

    wahapedia_datasheet_id: str
    keyword: str
    model_scope: str | None = Field(default=None, description="None = the whole unit")
    is_faction_keyword: bool = False


class NormalizedComposition(_Normalized):
    """Key ``(wahapedia_datasheet_id, line)`` — model counts recovered from free text."""

    wahapedia_datasheet_id: str
    line: int
    min_models: int | None = None
    max_models: int | None = None
    parse_confidence: ParseConfidence = ParseConfidence.UNPARSED


class NormalizedWargearOption(_Normalized):
    """Key ``(wahapedia_datasheet_id, line)`` — structure only.

    **No points.** The detail source publishes no cost column for options; the points source
    does, and it is authoritative for anything a player pays (C8/R3, FR-001/FR-002 as amended).
    """

    wahapedia_datasheet_id: str
    line: int
    group_key: str
    name: str
    max_per_unit: int | None = None
    models_per_instance: int | None = None


class NormalizedLeaderPair(_Normalized):
    """Key ``(leader_id, attached_id)``."""

    leader_id: str
    attached_id: str
