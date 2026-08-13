# AI-Assisted: Claude Code (model: claude-opus-5) - Defined the curated records of
# data-model.md §3 (task T022) against reference-db-schema.md v1.2.0: copy-indexed pricing with
# copy_index_min, per-row pricing_confidence, and the curated-only fields the bundle drops.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added 004-rules-data-enrichment's structured
# entities (004 task T009): CuratedCompositionEntry, CuratedOptionGroup, CuratedOptionChoice,
# CuratedChapterKeyword, and the three additive fields datasheet.wargear_option_state,
# keyword.keyword_class, and faction.army_rule_state (004 data-model.md §1).
# AI-Assisted: Claude Code (model: claude-opus-5) - Exposed each detachment's rule identities
# (004 task T053): CuratedDetachmentRule carries a rule's stable key and its name — never its
# text — so the detachment-rule summary class has a denominator that comes from the source
# rather than from the curator's own file (004 data-model.md §2.2, FR-022).
# AI-Assisted: Claude Code (model: claude-opus-5) - Carried the authored keyword glossary on
# the snapshot (004 task T061), keyed by the normalised keyword key of §2.4.
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
from enum import StrEnum
from typing import Final, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from pipeline.build.canonical_json import JsonValue
from pipeline.models.authored import (
    AbilitySummary,
    DetachmentRuleSummary,
    FactionRuleFile,
    GlossaryEntry,
)
from pipeline.models.mechanical import assert_mechanical_fields
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


class OptionScope(StrEnum):
    """Whom an option group applies to (`004` research D3's clause heads)."""

    UNIT = "unit"
    MODEL = "model"
    PER_N_MODELS = "per_n_models"


class WargearOptionState(StrEnum):
    """Whether a datasheet's option set extracted, and how completely (FR-016).

    This exists to keep one honest distinction visible: a datasheet with genuinely **no**
    options and a datasheet whose options **failed to extract** are not the same thing, and a
    consumer that cannot tell them apart shows an empty list for both.
    """

    NONE = "none"
    """The source states no options for this datasheet."""

    EXTRACTED = "extracted"
    """Every option row resolved."""

    PARTIAL = "partial"
    """At least one row did not resolve; what did resolve still ships (`OPT-UNPARSED`)."""


class DefaultEquipmentState(StrEnum):
    """Whether a datasheet's default equipment extracted, and how completely (`006` FR-015).

    :class:`WargearOptionState`'s pattern reused **without variation**, so no consumer learns a
    new idea: three codes, and the fourth fact — "the source was not consulted, *or* this
    datasheet's composition did not resolve" — expressed by the value's absence (`006` FR-016).

    A separate enum rather than a reuse of :class:`WargearOptionState`, because the two are
    different facts about one datasheet and routinely disagree: a datacard states no options and
    a full equipment sentence, or the reverse, on the same card.
    """

    NONE = "none"
    """The datacard states no default-equipment sentence."""

    EXTRACTED = "extracted"
    """Every sentence resolved."""

    PARTIAL = "partial"
    """At least one sentence did not resolve; what did resolve still ships (``EQP-UNPARSED``)."""


class OptionItemRole(StrEnum):
    """Which side of a swap an option-choice item sits on (`006` FR-005, FR-006).

    **One code, not two arrays.** ``granted`` and ``replaced`` carry identical fields, are
    produced by one clause grammar, are linked by one join, and fail in one way; two arrays would
    duplicate every constraint and every consumer join to encode a distinction one enumerated
    code already carries (`006` contract §2.1).
    """

    GRANTED = "granted"
    REPLACED = "replaced"


class EquipmentAppliesTo(StrEnum):
    """Whom a default-equipment sentence covers (`006` FR-012, FR-013).

    An **explicit code** rather than the presence of ``composition_line``, and that is the whole
    reason it exists: a nullable foreign key alone cannot tell *"this sentence covers the whole
    unit"* from *"this sentence names a group I could not identify"*, and FR-015 requires those
    two to be distinguishable.
    """

    UNIT = "unit"
    MODEL_GROUP = "model_group"


class KeywordClass(StrEnum):
    """A keyword's role. **Omitted** when unclassified — never guessed (FR-020)."""

    FACTION = "faction"
    CHAPTER = "chapter"
    UNIT = "unit"


class ArmyRuleState(StrEnum):
    """Whether a faction has an army rule at all (FR-021).

    The third state is expressed by **absence**: an omitted value means *not yet curated*, which
    is a different fact from :attr:`NONE` — "this faction genuinely has no army rule" — and
    conflating unfinished work with a curated negative is exactly what FR-021 forbids.
    """

    PRESENT = "present"
    NONE = "none"


class _Curated(BaseModel):
    """Base for curated records: frozen, unknown fields rejected."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class _CuratedMechanical(_Curated):
    """A curated record that asserts every string it holds is a mechanical value.

    Applied to the records `004-rules-data-enrichment` adds. The scan in
    :mod:`pipeline.validate.ip_scan` still runs and still asserts the absence; this asserts it
    at the *model boundary*, before the value can reach the tree, a report, or a log
    (research D9 control 1). The two controls are deliberately independent: one proves the
    absence, the other makes the presence impossible.
    """

    @model_validator(mode="after")
    def _fields_are_mechanical(self) -> Self:
        assert_mechanical_fields(self)
        return self


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
    army_rule_state: ArmyRuleState | None = Field(
        default=None,
        description="present | none; OMITTED = not yet curated, which is a different fact from "
        "'none' (FR-021). Set from curation/faction-rules/<faction-id>.json.",
    )
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


class CuratedDetachmentRule(_CuratedMechanical):
    """One detachment rule's **identity**: its stable key and its name. Never its text.

    The name comes from the source and is **always carried** into the bundle; only the summary is
    authored and gated (FR-022). This record exists so the detachment-rule summary class has a
    denominator — "every published detachment rule" (contract §4.1) — that comes from the source
    rather than from the curator's own file, which would make coverage measure itself.

    ``summary_key`` is ``detachment:<detachment-id>:<slug of the rule name>``, minted by
    :func:`pipeline.curate.summaries.detachment_rule_key`. Keying on the detachment **id** rather
    than its display name is what makes an upstream rename of the detachment leave the rule's key
    — and therefore its approval — untouched.
    """

    summary_key: str = Field(min_length=1, description="detachment:<detachment-id>:<slug>")
    name: str = Field(min_length=1, max_length=120, description="a short mechanical label")


class CuratedDetachment(_Curated):
    """One detachment, its restrictions, and the identities of the rules it owns."""

    detachment_id: str
    edition_id: str
    faction_id: str
    name: str
    detachment_points_cost: int
    is_legends: bool = False
    force_disposition: str | None = Field(default=None, description="CURATED-ONLY (C4/R7)")
    is_unique: bool | None = Field(default=None, description="CURATED-ONLY (C4/R7)")
    restrictions: Sequence[CuratedDetachmentRestriction] = ()
    rules: Sequence[CuratedDetachmentRule] = Field(
        default=(),
        description="the rules this detachment publishes, name always carried (004 FR-022). "
        "One-to-many: the measured baseline carries 284 detachment abilities over 261 "
        "detachments, which is why the rule rather than the detachment is the key.",
    )
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
    """One keyword binding, sorted by ``(keyword, model_scope)``.

    ``keyword_class`` is **omitted when unclassified**, so an unclassified keyword's row is
    byte-identical to what it was before this classification existed (FR-020). Two faction
    keywords on one datasheet is the normal shape of a chapter unit — 38.5% of the measured
    baseline — and is never an error (FR-017).
    """

    keyword: str
    is_faction_keyword: bool = False
    model_scope: str | None = None
    keyword_class: KeywordClass | None = Field(
        default=None, description="OMITTED when unclassified; KWD-UNCLASSIFIED, advisory"
    )


class CuratedCompositionEntry(_CuratedMechanical):
    """One model line of one datasheet, sorted by ``line`` (004 data-model.md §1.1).

    **A fixed count is not missing data.** ``min_count == max_count`` is the majority shape
    (1 669 of 2 168 rows in the measured baseline) and must never be read as an unresolved
    range — the spec names this edge case explicitly.

    A source row that resolves to neither production yields **no entry at all**, raises the
    advisory ``CMP-UNRESOLVED``, and suppresses the whole datasheet's composition: FR-008 asks
    for a datasheet "published without composition rather than with a guessed count", because a
    partial composition is worse than none. A curator override in
    ``curation/composition-overrides.json`` supplies the resolution and the finding disappears.
    """

    line: int = Field(ge=1, description="source row ordinal; also display order")
    model_name: str = Field(min_length=1, description="a name, never prose")
    min_count: int = Field(ge=0)
    max_count: int = Field(ge=0, description="equals min_count for a fixed-size unit")
    model_line: int | None = Field(
        default=None,
        ge=1,
        description="OMITTED on zero or >= 2 name matches — never guessed",
    )

    @model_validator(mode="after")
    def _range_is_ordered(self) -> Self:
        if self.max_count < self.min_count:
            raise ValueError(
                f"composition line {self.line}: max_count {self.max_count} is below min_count "
                f"{self.min_count}; a range that runs backwards is a parse defect, not data"
            )
        return self


class CuratedOptionGroup(_CuratedMechanical):
    """One wargear option group (004 data-model.md §1.2).

    **Identity is the load-bearing property** (FR-015). ``id`` derives from the source's own
    ``line`` ordinal, unique per ``(datasheet_id, line)``, so it is stable across snapshots for
    the same real-world option and an upstream relabelling surfaces as a **rename** — same
    ``id``, changed choice names — rather than a removal plus an addition, which is what
    ``reconcile/conflicts.py::detect_renames`` already knows how to report.

    The limitation, stated rather than papered over: if the source *reorders* its option rows,
    the ordinals shift and identity moves with them, which
    ``reconcile/conflicts.py`` reports as a bulk rename across one datasheet. A content-derived
    key would instead break identity on every relabelling — the opposite failure, and the worse
    one.
    """

    id: str = Field(min_length=1, description="og-<datasheet-stem>-<line>[-<sub>]")
    line: int = Field(ge=1, description="source row ordinal; also display order")
    scope: OptionScope
    scope_n: int | None = Field(default=None, ge=1, description="only when scope=per_n_models")
    parent_group_id: str | None = Field(default=None, description="OMITTED for a top-level group")
    default_choice_id: str | None = Field(
        default=None, description="OMITTED when the source states no default"
    )
    min_choices: int | None = Field(default=None, ge=0)
    max_choices: int | None = Field(default=None, ge=0)
    # -- 006-unit-loadout-fidelity, data-model.md §2.1 -----------------------------------------
    # Three mutually independent optional fields. None is defaulted from another and none is
    # inferred from the unit's composition.
    #
    # **`scope` does not gain a fourth member for this, and that is not a detail.** It is a
    # declared closed set, and the bundle schema validates it, which is evidence a consumer does
    # too. Adding a member would be a MAJOR break wearing an additive costume — FR-018 and
    # SC-006 forfeited in one line of JSON. A scoped stem therefore publishes `scope = unit`,
    # which is the truthful coarse reading, and carries its restriction here.
    eligible_model_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="the model name a scoped stem restricts the option to; OMITTED when the "
        "stem names no subset — which is every group `004` already publishes",
    )
    eligible_max_count: int | None = Field(
        default=None,
        ge=1,
        description="the maximum of that model the stem makes eligible; OMITTED when the stem "
        "states no maximum. Carried as the source states it and NOT reconciled against the "
        "named model's own composition band (spec Clarifications, 2026-08-09)",
    )
    is_per_model: bool | None = Field(
        default=None,
        description="True when the stem distributes the option per eligible model; OMITTED "
        "when the source does not distinguish. Never defaulted to False: research D1c measured "
        "a distributive `can each` on 350 of 571 unparsed rows, so defaulting would over-grant "
        "the majority form of the residual",
    )

    @model_validator(mode="after")
    def _scope_n_belongs_to_its_scope(self) -> Self:
        if (self.scope is OptionScope.PER_N_MODELS) != (self.scope_n is not None):
            raise ValueError(
                f"option group {self.id}: scope_n is present exactly when scope is "
                f"{OptionScope.PER_N_MODELS.value}; got scope={self.scope.value}, "
                f"scope_n={self.scope_n}"
            )
        return self


class CuratedOptionChoice(_CuratedMechanical):
    """One selectable choice within a group (004 data-model.md §1.3).

    **A choice is a name plus mechanical values.** There is no description field and none may be
    added: the option's source text is parsed into these fields or the row is reported as
    ``OPT-UNPARSED``. That is what stops this class becoming a prose channel — there is nowhere
    for prose to land.

    ``points_delta`` absence is **semantic**: a consumer sees "uncosted", never "free" (FR-013).
    ``is_no_change`` carries the same idea at a different layer — an explicit "no change"
    alternative must not read as a zero-cost item a player thinks they can take.
    """

    id: str = Field(min_length=1, description="oc-<group-stem>-<index>")
    group_id: str = Field(min_length=1)
    name: str = Field(min_length=1, description="a name, never prose")
    count: int | None = Field(default=None, ge=1, description="the `with N` quantifier")
    grants_weapon_line: int | None = Field(
        default=None, ge=1, description="OMITTED unless exactly one weapon name matched"
    )
    replaces_weapon_line: int | None = Field(default=None, ge=1, description="as above")
    is_default: bool = False
    is_no_change: bool = False
    points_delta: int | None = Field(
        default=None,
        description="OMITTED, never 0, when the points source does not price it (FR-013). A "
        "published cost of 0 is a different fact from an unpriced choice and is not rejected "
        "here; what is forbidden is emitting 0 *because* no price was found.",
    )
    priced_option_id: str | None = Field(default=None, description="-> CuratedWargearOption.id")
    items: Sequence[CuratedOptionChoiceItem] = Field(
        default=(),
        description="`006` §1.1: the replaced set and the granted bundle, sorted by "
        "(role, item_index). Produced by a second pass over the same object clause that NEVER "
        "rewrites this choice's `name` or `count` — which is what makes FR-009 hold literally "
        "over the 144 currently-parsing rows whose names conflate a bundle (research D5a).",
    )

    @model_validator(mode="after")
    def _a_no_change_choice_is_never_priced(self) -> Self:
        if self.is_no_change and (self.points_delta is not None or self.priced_option_id):
            raise ValueError(
                f"option choice {self.id}: an explicit 'no change' alternative carries no price "
                "— pricing one would publish 'take nothing' as a purchasable item"
            )
        return self


class CuratedOptionChoiceItem(_CuratedMechanical):
    """One item on one side of one wargear choice (`006` data-model.md §1.1).

    Sorted by ``(role, item_index)`` within its choice.

    **Every choice has items — including the single-item ones `004` already publishes.** A
    choice that resolves to one granted item emits one ``granted`` row whose ``weapon_line``
    equals the choice's own ``grants_weapon_line``. That redundancy is deliberate and
    load-bearing: it makes the consumer's read uniform ("iterate the items"), it turns the
    spec's *one-element-bundle-must-not-diverge* edge case into contract guarantee 12 — an
    invariant a test checks on every build — and it costs nothing, because the singular fields
    keep exactly the values they have today.

    **A multi-item choice carries no singular field.** ``grants_weapon_line`` and
    ``replaces_weapon_line`` are omitted whenever the choice's item count on that side is
    anything other than one. Filling them from the first item is precisely the truncation this
    feature exists to remove, and a consumer showing an unlinked choice is a smaller harm than
    one showing half a swap as the whole swap.
    """

    role: OptionItemRole = Field(description="the clause verb that produced the item")
    item_index: int = Field(ge=1, description="1-based, the SOURCE's own order; zero inference")
    item_name: str = Field(min_length=1, max_length=120, description="a name, never prose")
    count: int | None = Field(
        default=None,
        ge=1,
        description="the leading INT of the conjunct; OMITTED when the source states none, and "
        "never defaulted to 1 — absence means the source said nothing",
    )
    weapon_line: int | None = Field(
        default=None,
        ge=1,
        description="exactly-one-match linking, per item; OMITTED on zero or >= 2 matches, "
        "where the item ships unlinked with OPT-BUNDLE-UNLINKED and its siblings ship too",
    )


class CuratedEquipmentItem(_CuratedMechanical):
    """One item a default-equipment sentence names (`006` data-model.md §1.3).

    An item that fails to link ships **unlinked** with ``EQP-ITEM-UNLINKED`` and neither its
    siblings nor its group is discarded — `004`'s ``OPT-LINK-AMBIGUOUS`` discipline applied to a
    second class.
    """

    item_index: int = Field(ge=1, description="1-based, the source's own order")
    item_name: str = Field(min_length=1, max_length=120, description="a name, never prose")
    count: int | None = Field(default=None, ge=1, description="OMITTED when unstated")
    weapon_line: int | None = Field(
        default=None, ge=1, description="OMITTED on zero or >= 2 matches (FR-014)"
    )


class CuratedEquipmentGroup(_CuratedMechanical):
    """One default-equipment sentence from the datacard, and who it applies to (§1.2).

    ``id`` is ``eq-<datasheet-stem>-<line>``, derived from the sentence's own ordinal — stable
    across snapshots, zero inference, the same identity discipline as ``og-`` (`004` FR-015).

    **``composition_line`` is resolved by NAME and never by ordinal.** Research D1e measured the
    pairings: 1 331 cards carry one composition line and one sentence, but **195 carry two lines
    and one sentence**, where any positional pairing would attach a squad's loadout to its
    leader. Zero or two-or-more name matches omit the link and raise
    ``EQP-GROUP-UNRESOLVED``.
    """

    id: str = Field(min_length=1, description="eq-<datasheet-stem>-<line>")
    line: int = Field(ge=1, description="source ordinal within the composition block")
    applies_to: EquipmentAppliesTo
    model_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="present exactly when applies_to = model_group",
    )
    composition_line: int | None = Field(
        default=None,
        ge=1,
        description="exactly-one-match against the datasheet's own composition rows; OMITTED on "
        "zero or >= 2 — never guessed, and never resolved positionally",
    )
    items: Sequence[CuratedEquipmentItem] = Field(default=(), description="sorted by item_index")

    @model_validator(mode="after")
    def _model_name_belongs_to_its_subject(self) -> Self:
        if (self.applies_to is EquipmentAppliesTo.MODEL_GROUP) != (self.model_name is not None):
            raise ValueError(
                f"equipment group {self.id}: model_name is present exactly when applies_to is "
                f"{EquipmentAppliesTo.MODEL_GROUP.value}; got applies_to="
                f"{self.applies_to.value}, model_name={self.model_name!r}"
            )
        return self


class CuratedChapterKeyword(_CuratedMechanical):
    """One chapter (sub-faction) keyword and its parent, sorted by ``keyword`` (§1.5).

    **Keyed by ``keyword`` alone**, deliberately: FR-019 guarantees one parent per chapter
    keyword, so "resolve a chapter -> its datasheets" stays a plain join against
    ``datasheet_keyword.keyword`` with no composite lookup — which is the navigational
    capability US2 exists to unlock.

    **Uniform enumeration** (FR-018): a chapter the points source already models as a faction of
    its own still appears here, flagged, so consumers have one mechanism for every chapter
    grouping. The flag plus the parent-agreement check (``KWD-CHAPTER-PARENT-CONFLICT``,
    blocking) are what prevent double counting.
    """

    keyword: str = Field(min_length=1, description="primary key")
    parent_faction_id: str = Field(min_length=1, description="must resolve in factions.json")
    chapter_faction_id: str | None = Field(
        default=None, description="set when the points source models this chapter as a faction"
    )
    is_modelled_as_faction: bool = False

    @model_validator(mode="after")
    def _the_flag_and_the_id_agree(self) -> Self:
        if self.is_modelled_as_faction != (self.chapter_faction_id is not None):
            raise ValueError(
                f"chapter keyword {self.keyword!r}: is_modelled_as_faction and "
                "chapter_faction_id state the same fact and must agree — a flag without an id "
                "tells a consumer nothing it can act on"
            )
        return self


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
    """One cost row, keyed ``(pricing_context, model_count, copy_index_min)`` in its datasheet.

    A ``copy_index_min = 1`` row must exist for every ``model_count`` **within each context** —
    the tier table would otherwise be unresolvable at lookup time, which is the blocking
    ``PRC-TIER-INCOMPLETE`` (contract v1.2.0 guarantee 7).
    """

    model_count: int
    copy_index_min: int = Field(default=1, ge=1, description="1-based copy ordinal; 1 = base tier")
    points: int
    label: str = Field(description="'5 models' — the band's LOWER bound (C2/R5)")
    pricing_context: str | None = Field(
        default=None,
        description="ABSENT for the price the unit costs in its own army, which is what every "
        "cost row has always meant. Present only where the points source states a condition "
        "this price applies under and the model count cannot express it: "
        "'every-model-has-imperium' (the second Imperial Agents cost table) or "
        "'with-hunting-wolves' (two bands of one unit that hold the same number of models).",
    )
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
    composition: Sequence[CuratedCompositionEntry] = Field(
        default=(),
        description="sorted by line; EMPTY for a datasheet whose composition did not fully "
        "resolve — FR-008 publishes it without composition rather than with a guessed count",
    )
    option_groups: Sequence[CuratedOptionGroup] = Field(default=(), description="sorted by id")
    option_choices: Sequence[CuratedOptionChoice] = Field(default=(), description="sorted by id")
    wargear_option_state: WargearOptionState | None = Field(
        default=None,
        description="none | extracted | partial; OMITTED = the source was not consulted "
        "(FR-016). This is what distinguishes 'no options' from 'options that failed'.",
    )
    equipment_groups: Sequence[CuratedEquipmentGroup] = Field(
        default=(),
        description="`006` §1.2: sorted by id. EMPTY for a datasheet whose composition did not "
        "resolve — FR-016 refuses to attach equipment to a composition structure that does not "
        "exist. Note the asymmetry with composition, and that it is intentional: an unresolved "
        "composition line suppresses the WHOLE datasheet's composition, while an unresolved "
        "equipment sentence suppresses only itself.",
    )
    default_equipment_state: DefaultEquipmentState | None = Field(
        default=None,
        description="`006` §3: none | extracted | partial; OMITTED = the source was not "
        "consulted, OR this datasheet's composition did not resolve.",
    )
    wargear_options: Sequence[CuratedWargearOption] = Field(
        default=(),
        description="the PRICED projection, UNCHANGED by 004: same fields, same producer "
        "(_costs()), same id scheme. Preserving it by not touching it is what makes SC-004's "
        "byte-identical row set a structural guarantee rather than a test that happens to pass.",
    )
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
    chapter_keywords: Sequence[CuratedChapterKeyword] = Field(
        default=(),
        description="data/<edition>/chapter-keywords.json, sorted by keyword — the enumerable "
        "chapter vocabulary (FR-018). Snapshot-level rather than per-faction because a chapter "
        "keyword is resolved by keyword, not by the faction it happens to hang off.",
    )
    ability_summaries: Mapping[str, AbilitySummary] = Field(
        default_factory=dict, description="ability_key -> approved summary (FR-020)"
    )
    faction_rules: Mapping[str, FactionRuleFile] = Field(
        default_factory=dict,
        description="faction_id -> curation/faction-rules/<faction-id>.json (004 FR-021). "
        "Authored content travelling with the snapshot exactly as ability_summaries does, and "
        "for the same reason: the builder expands it into bundle rows at emission time, so it "
        "is never written into the machine-written tree. A faction ABSENT from this mapping is "
        "uncurated, which is a different fact from army_rule_state = none.",
    )
    detachment_rules: Mapping[str, DetachmentRuleSummary] = Field(
        default_factory=dict,
        description="summary_key -> curation/detachment-rules/<faction-id>.json's record (004 "
        "FR-022). Authored content travelling with the snapshot exactly as ability_summaries "
        "and faction_rules do. The rules THEMSELVES live on CuratedDetachment.rules and come "
        "from the source; this mapping carries only each rule's authored summary, which is why "
        "a rule with no record here still ships with its name.",
    )
    keyword_glossary: Mapping[str, GlossaryEntry] = Field(
        default_factory=dict,
        description="keyword_key -> curation/glossary.json's entry (004 FR-023). Keyed by the "
        "NORMALISED key of contracts/bundle-schema-delta.md §4, so casing, spacing, punctuation "
        "and numeric-parameter variants of one keyword resolve to ONE entry. An unauthored "
        "keyword simply has no entry: it still appears on its datasheets and weapons unchanged, "
        "publication is not blocked while the gate is off, and it is named in the coverage "
        "report.",
    )

    @property
    def all_restrictions(self) -> list[CuratedDetachmentRestriction]:
        """Edition-wide and per-detachment restrictions in one list, sorted by id."""
        collected = list(self.restrictions)
        for detachment in self.detachments:
            collected.extend(detachment.restrictions)
        return sorted(collected, key=lambda restriction: restriction.id)
