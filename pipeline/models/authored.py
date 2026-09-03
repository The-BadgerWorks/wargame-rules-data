# AI-Assisted: Claude Code (model: claude-opus-5) - Defined the authored records of
# data-model.md §4 (task T023), including the AbilitySummary review-state machine of §4.1 and
# the digest-bound FindingResolution of validation-report.md §5.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added FactionMapEntry.
# detail_source_publication_id, an optional stage-2 disambiguation signal for the
# REC-AMBIGUOUS-MATCH ladder (see pipeline/reconcile/match.py): it lets a chapter-scoped mapping
# prefer its own supplement's datasheet over a same-named core-codex twin.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added 004-rules-data-enrichment's authored
# records (004 task T010): FactionRuleSummary's object wrapper, DetachmentRuleSummary,
# GlossaryEntry, and the three curator resolution records KeywordClassEntry,
# CompositionOverrideEntry, and OptionOverrideEntry (004 data-model.md §2 and §4).
# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote down what detail_source_faction_id is
# (004 T076 follow-up), after it was re-pointed wholesale at mfm_slug: it is the source's own
# slug, three factions spell it differently, and two curated factions legitimately share one.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added CompositionOverrideEntry.remove (007,
# Product Owner decision 2026-08-14 T061 review): the curator-suppression shape research D1
# called "impossible today" and "a reasonable later addition", added once CMP-HEADER-ROW's
# automatic refusal was demoted to advisory-only.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added FactionMapEntry.
# detail_source_faction_code and UnitMapEntry.faction_id (009 tasks T021/T024, data-model.md
# §1-§2): the bulk export's own faction-code vocabulary alongside the existing (now html-slug)
# detail_source_faction_id, and the unit-map crosswalk's optional faction scope, which is what
# stops a chapter-shared entry from adopting one datasheet_id into all six Space Marine chapters
# (risk R-C, the C1 ruling).
"""Authored records — human-written, under ``curation/``.

**Invariant:** the pipeline reads these and never writes them; humans write these and never
hand-edit ``data/``. CI enforces both directions. That is what makes FR-017's and FR-024's
carry-forward guarantees *structural* rather than procedural — a rebuild physically cannot
clobber authored work.

Any authored record referencing an entity absent from curated data is the blocking
``AUT-DANGLING-REF`` (FR-018) — which is what catches a copy limit or a restriction still
pointing at a retired datasheet.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Final, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from pipeline.build.canonical_json import JsonValue

#: The hard ceiling on an authored summary, in characters, and the ONE place it is written down
#: on the Python side. Every ``schemas/curation/*.schema.json`` and ``schemas/bundle.schema.json``
#: must agree with it, which ``tests/enrichment/test_summary_length_ceiling.py`` asserts rather
#: than trusts -- this constant was 400 in one file and 1 000 in six others for exactly as long
#: as it took a live build to reach the curation loader and die there.
#:
#: Distinct from ``WGC_SUMMARY_MAX_CHARS`` and its three siblings, which are the *editorial*
#: targets whose breach is the advisory ``<CLS>-OVERLENGTH``. This one refuses the record.
SUMMARY_MAX_LENGTH: Final = 1000


class ReviewState(StrEnum):
    """The ability-summary review state (data-model.md §4.1, FR-020/FR-023/FR-024).

    ::

                (new ability_key seen)
                         |
                         v
                      draft --author--> in_review --non-author approval--> approved
                         ^                                                    |
                         |                                    mechanic_digest changed
                         |                                                    v
                         +----------- re-author <---------------------- needs_rereview

    ``draft``, ``in_review``, and ``needs_rereview`` all **block publication**. ``approved``
    carries forward untouched while ``mechanic_digest`` is unchanged — no re-authoring, no
    re-review, which is exactly what SC-011 measures.
    """

    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    NEEDS_REREVIEW = "needs_rereview"

    @property
    def blocks_publication(self) -> bool:
        """Everything but :attr:`APPROVED` blocks (FR-020, FR-023, FR-024)."""
        return self is not ReviewState.APPROVED


#: The review states that block publication, stated as data for the validate stage.
BLOCKING_REVIEW_STATES: frozenset[ReviewState] = frozenset(
    state for state in ReviewState if state.blocks_publication
)


class _Authored(BaseModel):
    """Base for authored records: frozen, and an unknown field is a hard failure.

    ``extra="forbid"`` is what makes a hand-edited ``curation/`` file fail fast with a named
    key rather than have a typo silently ignored.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)


class FactionMapEntry(_Authored):
    """``curation/faction-map.json``, keyed by ``mfm_slug``.

    Faction mapping is **authored, not derived**: the taxonomies genuinely disagree — 30 points
    slugs against 26 detail ids, chapters split one way and Titan Legions the other (C3/R6). An
    unmapped slug is the blocking ``REC-FACTION-UNMAPPED``.

    ``detail_source_faction_id`` is **the detail source's own identifier, verbatim** — under
    ``html`` mode, the faction page's slug. It is *not* derivable from ``mfm_slug``, and the two
    disagree in both of the ways a curator will assume they cannot:

    * the same faction, spelled differently by each source (``tau-empire`` against
      ``t-au-empire``, ``emperors-children`` against ``emperor-s-children``); and
    * **two** curated factions the detail source publishes on **one** page — the Titan Legions,
      loyalist and traitor, both read from ``adeptus-titanicus``. Sharing an id is supported and
      correct: the scope resolution keeps each faction's datasheets apart by what the *points*
      source prices on each faction's own page (see
      :func:`pipeline.reconcile.match.resolve_factions` and ``_owning_factions``), exactly as
      five Space Marine chapters already share their parent's id through the parent fallback.

    Copying ``mfm_slug`` into this field therefore ships those factions with **no datasheets at
    all** — quietly enough to read as an upstream coverage collapse. It is reported, in two
    halves that have to be joined by hand: ``REC-DETAIL-FACTION-ORPHAN`` names the source page
    nobody claimed, and one ``REC-UNMATCHED-POINTS-ONLY`` names each of that faction's units.

    ``detail_source_publication_id`` is an optional, narrowly-scoped disambiguation signal for
    D5 stage 2 (:func:`pipeline.reconcile.match.match_units`). When a chapter-scoped mapping's
    detail-source faction id collides with its parent's (five Space Marine chapters all share
    ``SM``), two detail-source datasheets can normalise to the same name with neither Legends —
    an ambiguity stage 2 cannot otherwise resolve. If set, it names the detail source's own
    publication id (Wahapedia's ``source_id``) for this chapter's supplement, letting stage 2
    prefer the datasheet published there over a same-named core-codex twin — but **only** when
    that preference narrows the candidates to exactly one; it never manufactures a match where
    none of the candidates carry that publication id.

    ``detail_source_faction_code`` is an optional second vocabulary for the SAME detail faction
    (009 data-model.md §2, plan.md finding 1): ``detail_source_faction_id`` carries one value for
    two arms with two genuinely different vocabularies — commit ``200a6e23`` rewrote all 30
    records from the bulk export's own codes (``SM``) to html-mode's page slugs
    (``space-marines``), overwriting the only record of the csv vocabulary rather than storing it
    alongside. When set, this field names the detail source's identifier for this faction **in
    the bulk export's vocabulary specifically**; ``detail_source_faction_id`` keeps its current
    slug value unchanged. Absent means the arm-appropriate value IS ``detail_source_faction_id``,
    which is every existing record's case today. Resolution
    (:func:`pipeline.reconcile.match.resolve_factions`) reads BOTH values into scope when this is
    set, never chooses between them by a mode check (FR-012) — whichever arm actually acquired
    the data, only its own vocabulary's value will ever appear in a real row.
    """

    mfm_slug: str
    faction_id: str
    parent_faction_id: str | None = None
    detail_source_faction_id: str
    detail_source_publication_id: str | None = None
    detail_source_faction_code: str | None = None


class UnitMapEntry(_Authored):
    """``curation/unit-map.json``, keyed by curated ``datasheet_id``.

    Consulted **before any name matching** (D5 stage 1). A confirmed pairing is never
    re-derived, so an upstream rename lands as a changed display name on an unchanged curated
    id — reported as a rename, never as a removal plus an addition (FR-015).

    ``faction_id`` is optional (009 data-model.md §1) — additive, so every entry stays valid
    without it — but **mandatory in the authoring rule** (rule 8) the moment an entry is written
    for a name shared across sibling factions. Stage 1's matcher loop runs once PER faction
    scope; an entry naming no faction is adopted into every scope that reaches it, which is
    correct for a name unique to one faction and a C1-breaching collapse for one that is not (six
    Space Marine chapters would all resolve the same `datasheet_id` for a shared unit name).
    Omitted keeps today's global behaviour exactly.
    """

    datasheet_id: str
    mfm_display_name: str
    wahapedia_datasheet_id: str
    confirmed_at: str
    confirmed_by: str
    faction_id: str | None = None


class UnitAlias(_Authored):
    """``curation/unit-aliases.json``, keyed ``(faction_id, alias)`` — D5 stage 3."""

    faction_id: str
    alias: str
    datasheet_id: str
    note: str | None = None


class AbilitySummary(_Authored):
    """``curation/abilities/<faction-id>.json``, keyed by **ability key, not by binding**.

    The export carries thousands of bindings over a much smaller distinct ability set; keying
    per binding would multiply release 1's dominant editorial cost by roughly an order of
    magnitude for no editorial benefit (research D6). The builder expands keys to per-datasheet
    rows at snapshot time, satisfying the consumer contract's ``NOT NULL`` per-datasheet
    summary.

    ``summary`` is **authored from the mechanic**, in the data set's own words. Machine
    paraphrase of the publisher's text does not satisfy the contract and is prohibited
    (``reference-db-schema.md`` §6.1(2), research D6).
    """

    ability_key: str
    name: str
    summary: str
    review_state: ReviewState = ReviewState.DRAFT
    mechanic_digest: str = Field(description="keyed, truncated digest — see research D6, C6/R8")
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    authored_against_acquisition: str | None = None


class GameSizeBand(_Authored):
    """``curation/game-sizes.json``, keyed by ``id``."""

    id: str
    label: str
    min_points: int
    max_points: int
    detachment_points_budget: int
    max_detachments: int
    max_enhancements: int


class EditionRuleValue(_Authored):
    """``curation/edition-rules.json``, keyed by ``rule_key``."""

    rule_key: str
    value: JsonValue


class CopyLimit(_Authored):
    """``curation/copy-limits.json``, keyed by ``datasheet_id``.

    Uncurated at first release by design: absent means the rule is *unevaluated* in the app,
    which is the honest state. A guessed ``1`` would be a fabricated rule (FR-019).
    """

    datasheet_id: str
    max_copies_per_army: int
    note: str | None = None


class RestrictionAuthoring(_Authored):
    """``curation/detachment-restrictions.json``, keyed by ``id``."""

    id: str
    detachment_id: str | None = None
    restriction_type: str
    params: Mapping[str, JsonValue] = Field(default_factory=dict)
    message_template: str


class SummaryClass(StrEnum):
    """The four authored summary classes (`contracts/authored-summary-gates.md` §1).

    All four share, **without variation**: :class:`ReviewState`, the record shape, the
    ``mechanic_digest`` algorithm, the carry-forward rule, and the self-approval refusal.
    Nothing about the authoring regime is relaxed for the three new ones, and the volume of
    authoring is explicitly not a justification for automating it.
    """

    ABILITIES = "abilities"
    """2 031 records, 100% approved. **No gate switch** — always on; FR-001 forbids weakening
    a guarantee this feature inherits."""

    FACTION_RULES = "faction_rules"
    DETACHMENT_RULES = "detachment_rules"
    GLOSSARY = "glossary"

    @property
    def finding_prefix(self) -> str:
        """The ``<CLS>`` of the class's finding codes (contract §3)."""
        return _SUMMARY_CLASS_PREFIXES[self]

    @property
    def has_gate_switch(self) -> bool:
        """False for :attr:`ABILITIES` alone, whose gate predates this feature."""
        return self is not SummaryClass.ABILITIES

    @property
    def key_field(self) -> str:
        """The record field carrying the key (contract §6's glob-to-key-field table).

        The **only** field-name difference between the four classes: ``ability_key`` on the
        existing class, ``summary_key`` on the three new ones. Renaming the existing 2 031
        records to match would be a change-class collision with this feature's pipeline work
        under ``tools/check_change_classes.py``, so the difference is carried as data here — one
        table, read by the self-approval guard and by the finding detail alike — rather than
        being paid for once in a migration and forever in a divergence.
        """
        return "ability_key" if self is SummaryClass.ABILITIES else "summary_key"


_SUMMARY_CLASS_PREFIXES: Final[Mapping[SummaryClass, str]] = {
    SummaryClass.ABILITIES: "SUM",
    SummaryClass.FACTION_RULES: "FRL",
    SummaryClass.DETACHMENT_RULES: "DRL",
    SummaryClass.GLOSSARY: "GLS",
}


class _SummaryRecord(_Authored):
    """The shape every authored summary shares (004 data-model.md §2).

    Identical to :class:`AbilitySummary` in every field but one: ``ability_key`` generalises to
    ``summary_key``. Nothing new is invented, so the existing digest, state, carry-forward, and
    self-approval machinery **generalises rather than duplicates** — which is the whole reason
    the three new classes cost a fraction of what the first one did.

    ``summary`` is authored **by a human from the mechanic, in the data set's own words**.
    Machine paraphrase, synonym substitution, and reordering of the publisher's text do not
    satisfy this and are policy violations, not quality issues (FR-024, Principle 4).
    """

    summary_key: str = Field(min_length=1, description="class-prefixed, stable, curator-visible")
    name: str = Field(min_length=1, max_length=120, description="a short mechanical label")
    summary: str = Field(
        min_length=1, max_length=SUMMARY_MAX_LENGTH, description="authored, mechanics-only"
    )
    review_state: ReviewState = ReviewState.DRAFT
    mechanic_digest: str = Field(description="keyed, truncated digest — research D6, C6/R8")
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    authored_against_acquisition: str | None = None


class FactionRuleSummary(_SummaryRecord):
    """One army rule of one faction, in ``curation/faction-rules/<faction-id>.json``'s ``rules``.

    Keyed ``faction:<faction-id>:<slug>``. ``display_order`` exists because a faction may have
    more than one army rule.
    """

    display_order: int = Field(default=1, ge=1)


class FactionRuleFile(_Authored):
    """``curation/faction-rules/<faction-id>.json`` — an **object wrapper**, not a bare array.

    The wrapper earns its awkwardness by making one distinction expressible that a bare array
    cannot (FR-021):

    ==========================  ================================================
    State                       Meaning
    ==========================  ================================================
    file absent                 not yet curated — unfinished work
    ``army_rule_state: none``   the faction genuinely has no army rule
    ``army_rule_state: present``  >= 1 rule, each with a name; summaries gated
    ==========================  ================================================

    A faction with no army rule and a faction nobody has looked at yet are different facts, and
    a consumer that cannot tell them apart shows the same empty section for both.
    """

    faction_id: str = Field(min_length=1)
    army_rule_state: str = Field(description="present | none — see CuratedFaction.army_rule_state")
    rules: Sequence[FactionRuleSummary] = ()


class DetachmentRuleSummary(_SummaryRecord):
    """One detachment rule, in ``curation/detachment-rules/<faction-id>.json`` (a bare array).

    Keyed ``detachment:<detachment-id>:<slug>`` — by the **rule**, not by the detachment,
    because a detachment may own more than one (the measured baseline carries 284 detachment
    abilities over 261 detachments).

    Three edge cases the key handles, each of which a name-based key gets wrong:

    * two detachments in different factions sharing a rule name are **distinct keys**;
    * a detachment renamed upstream while its rule is unchanged keeps its key and its digest, so
      **nothing re-reviews**;
    * a rule changed while its name is unchanged **moves its digest and re-reviews** — which is
      the whole point of digesting the mechanic rather than the name.

    The rule's **name is always carried** into the bundle and comes from the source; only the
    *summary* is authored and gated (FR-022).
    """

    detachment_id: str = Field(min_length=1)


class GlossaryEntry(_SummaryRecord):
    """One keyword definition, in ``curation/glossary.json`` (a bare array).

    Keyed ``glossary:<keyword_key>`` where ``keyword_key`` is the normalised key of
    ``contracts/bundle-schema-delta.md`` §4 — so casing, spacing, punctuation, and numeric
    parameter variants of one keyword collapse to **one entry** (FR-023).

    An unauthored keyword simply has **no row**. It still appears on its datasheets and weapons
    exactly as today, publication is not blocked while the gate is off, and it is named in the
    coverage report. An entry whose keyword no published datasheet or weapon uses raises the
    advisory ``GLS-ORPHANED``, so the glossary cannot silently accumulate dead definitions.

    **The digest limitation, stated plainly** (contract §5.1): no keyword glossary source
    exists. Where the current edition publishes a description for the keyword, the digest is
    over that text and the entry behaves exactly like an ability summary. Where it does not, the
    digest is over the normalised keyword stem, which is stable by construction, so such an entry
    **never auto-flags for re-review**. The subset is enumerated in ``summary-coverage.md`` and
    swept manually before the glossary gate is switched on.
    """

    keyword_key: str = Field(min_length=1, description="the normalised key — primary key")
    display_keyword: str = Field(min_length=1, description="the keyword as readers see it")
    has_numeric_parameter: bool = Field(
        default=False, description="a trailing integer parameter was stripped from the key"
    )


class KeywordClassEntry(_Authored):
    """``curation/keyword-classes.json``, keyed by ``keyword`` (004 data-model.md §4, research D7).

    The curator writes only the **exceptions** to a deterministic default: a non-faction keyword
    is ``unit``; a faction keyword resolving to a faction with no parent is ``faction``; anything
    else is unclassified and awaits a record here. Of 1 423 distinct keywords in the measured
    baseline only 46 are faction keywords, so the authoring surface is at most 46 records and
    realistically about 20 — the cheapest of this feature's five content gaps by a wide margin.

    ``chapter_faction_id`` is checked against the faction tree: that faction's own
    ``parent_faction_id`` MUST equal this record's, or ``KWD-CHAPTER-PARENT-CONFLICT`` blocks
    (FR-019). One side declares, the other is asserted against it — the same shape as `002`'s
    R9 fix for the point range, and for the same reason: two structures describing the same
    hierarchy drift apart unless one of them is made to answer to the other.
    """

    keyword: str = Field(min_length=1)
    keyword_class: str = Field(description="faction | chapter | unit")
    parent_faction_id: str | None = Field(default=None, description="required when class=chapter")
    chapter_faction_id: str | None = None
    note: str | None = None


class CompositionOverrideEntry(_Authored):
    """``curation/composition-overrides.json``, keyed ``(datasheet_id, line)`` (§4).

    The curator's resolution for a composition line the grammar could not resolve. Mirrors
    ``curation/resolutions.json``'s existing pattern: curator-written, carried forward, validated
    on load, never written by any pipeline stage.

    ``remove`` (007, Product Owner decision 2026-08-14 T061 review) is the second shape an entry
    may take, added when the automatic five-signal ``CMP-HEADER-ROW`` refusal was demoted from a
    blocking auto-drop to an advisory flag (research D1, risk R-1/R-A materialising on the live
    corpus: 3 of the rows the automatic conjunction would have refused were real duo-sheet first
    models, not phantom headers). A ``remove`` entry carries **no** replacement fields — it names
    the line and states only that it is gone, the same "resolves once, carried forward" shape
    ``option-overrides.json``'s escape hatch already has, but subtractive rather than corrective.
    A non-``remove`` entry is unchanged from `004`: it *replaces* the row's fields, and still
    requires all three.
    """

    datasheet_id: str = Field(min_length=1)
    line: int = Field(ge=1)
    remove: bool = False
    model_name: str | None = Field(default=None, min_length=1)
    min_count: int | None = Field(default=None, ge=0)
    max_count: int | None = Field(default=None, ge=0)
    model_line: int | None = Field(default=None, ge=1)
    note: str | None = None

    @model_validator(mode="after")
    def _remove_xor_replace(self) -> Self:
        replacement_fields_present = (
            self.model_name is not None or self.min_count is not None or self.max_count is not None
        )
        if self.remove:
            if replacement_fields_present or self.model_line is not None:
                raise ValueError(
                    f"composition override {self.datasheet_id}:{self.line}: remove=true carries "
                    "no model_name/min_count/max_count/model_line — a removal states only that "
                    "the row is gone, never a replacement for it"
                )
        elif self.model_name is None or self.min_count is None or self.max_count is None:
            raise ValueError(
                f"composition override {self.datasheet_id}:{self.line}: model_name, min_count, "
                "and max_count are all required unless remove=true"
            )
        return self


class OptionOverrideItem(_Authored):
    """One item on one side of a curator-authored choice (`006` FR-005..FR-007, T005).

    The curator's own decomposition of a multi-item swap. A stated ``weapon_line`` is **used and
    never re-derived**: the point of an override is that the pipeline could not resolve the row,
    so re-deriving the link here would overrule the human who did.
    """

    role: str = Field(description="granted | replaced")
    item_name: str = Field(min_length=1, max_length=120)
    count: int | None = Field(default=None, ge=1)
    weapon_line: int | None = Field(default=None, ge=1)


class OptionOverrideChoice(_Authored):
    """One curator-authored choice inside an :class:`OptionOverrideEntry`."""

    name: str = Field(min_length=1)
    count: int | None = Field(default=None, ge=1)
    grants_weapon_line: int | None = Field(default=None, ge=1)
    replaces_weapon_line: int | None = Field(default=None, ge=1)
    is_default: bool = False
    is_no_change: bool = False
    items: Sequence[OptionOverrideItem] = ()
    """Empty for a `004`-shaped override, and that is not a migration but a schema property:
    every new member here is optional, so an override written before `006` validates and
    resolves unchanged (FR-011)."""


class OptionOverrideEntry(_Authored):
    """``curation/option-overrides.json``, keyed ``(datasheet_id, line)`` (§4).

    A full group-plus-choices structure for an option row the grammar left unparsed. **No
    price**: cost comes from the points source and only from there, so a curator can supply the
    structure that was missed but never a number the publisher did not publish (FR-013).

    These two override files are **the escape hatch that makes "never guess" affordable**.
    Without them a 1.3% composition tail and a ~20% option-link tail would be permanent defects;
    with them they are a bounded, one-time, carry-forward cost — exactly how `002` made ability
    summaries tractable.
    """

    datasheet_id: str = Field(min_length=1)
    line: int = Field(ge=1)
    scope: str = Field(description="unit | model | per_n_models")
    scope_n: int | None = Field(default=None, ge=1)
    # `006` FR-004's eligibility scope. Three mutually independent optional members, and
    # deliberately NOT a fourth member of `scope`: that column is a declared closed set, and a
    # consumer that validates it would reject a snapshot carrying a value it has never seen.
    eligible_model_name: str | None = Field(default=None, min_length=1, max_length=120)
    eligible_max_count: int | None = Field(default=None, ge=1)
    is_per_model: bool | None = None
    min_choices: int | None = Field(default=None, ge=0)
    max_choices: int | None = Field(default=None, ge=0)
    choices: Sequence[OptionOverrideChoice] = ()
    note: str | None = None


class EquipmentOverrideItem(_Authored):
    """One item of a curator-authored default-equipment sentence (`006` FR-012..FR-014, T005).

    A stated ``weapon_line`` is **used and never re-derived**, for the same reason
    :class:`OptionOverrideItem`'s is: the point of an override is that the pipeline could not
    resolve the sentence, so re-joining it here would overrule the human who did.
    """

    item_name: str = Field(min_length=1, max_length=120)
    count: int | None = Field(default=None, ge=1)
    weapon_line: int | None = Field(default=None, ge=1)


class EquipmentOverrideEntry(_Authored):
    """``curation/equipment-overrides.json``, keyed ``(datasheet_id, line)`` (`006` §4).

    The curator's resolution for a default-equipment sentence the grammar refused — research
    D1e's compound-and-conditional tail. **No price field anywhere**, on the same terms as
    :class:`OptionOverrideEntry`: default equipment is what a model already carries and costs
    nothing by definition, so there is nowhere here for a number to go. **No description field**
    either: a sentence is a subject plus item names, which is what stops this class becoming a
    prose channel.

    ``model_name`` is present **exactly when** ``applies_to`` is ``model_group`` — the same
    biconditional :class:`pipeline.models.curated.CuratedEquipmentGroup` enforces, checked here
    as well so a curator learns of the mistake at load time rather than at write time.
    """

    datasheet_id: str = Field(min_length=1)
    line: int = Field(ge=1)
    applies_to: str = Field(description="unit | model_group")
    model_name: str | None = Field(default=None, min_length=1, max_length=120)
    composition_line: int | None = Field(default=None, ge=1)
    items: Sequence[EquipmentOverrideItem] = ()
    note: str | None = None

    @model_validator(mode="after")
    def _model_name_belongs_to_its_subject(self) -> Self:
        if (self.applies_to == "model_group") != (self.model_name is not None):
            raise ValueError(
                f"equipment override {self.datasheet_id}:{self.line}: model_name is present "
                f"exactly when applies_to is model_group; got applies_to={self.applies_to!r}, "
                f"model_name={self.model_name!r}"
            )
        return self


class FindingResolution(_Authored):
    """``curation/resolutions.json``, keyed ``(finding_code, entity_ref)`` (FR-034).

    ``data_digest`` binds the resolution to the data that produced the finding. The finding is
    suppressed **only while the digest matches**; when the underlying data changes the
    resolution lapses automatically and the finding is raised again at its catalogue severity —
    a curator cannot silence a class of finding permanently.

    ``explanation`` is a human sentence about *mechanics or process* and must not quote source
    text (``validation-report.md`` §5).
    """

    finding_code: str
    entity_ref: str
    data_digest: str
    resolved_at: str
    resolved_by: str
    explanation: str


class CarriedForwardFactionEntry(_Authored):
    """``curation/carried-forward-factions.json``, keyed ``faction_slug`` (008 FR-024/FR-025,
    Product Owner decision 2026-08-17).

    A curator's explicit declaration that a named faction's detail-source page may be sourced
    from the previous published version if a run cannot fetch it live — never inferred, never
    silent. ``faction_slug`` is the detail source's own page slug
    (:data:`pipeline.acquire.wahapedia_html.FACTION_PAGE`), which is not always the same string
    as a curated ``faction_id`` — this file is read before curation resolves one to the other, so
    it has to name the vocabulary the acquisition layer actually sees.
    """

    faction_slug: str = Field(min_length=1)
    declared_at: str
    reason: str = Field(min_length=1, max_length=240)
    note: str | None = Field(default=None, min_length=1, max_length=240)


class DetailSourceAuthorityEntry(_Authored):
    """``curation/detail-source-authority.json``, keyed ``data_class`` (009 T048, FR-010,
    data-model.md §3, Product Owner decision T047 2026-08-18: hybrid now, full later).

    Authored only because a hybrid was chosen: FR-009's four criteria measured two classes —
    ``options`` and ``default_equipment`` — below their own floor
    (``reports/009-diagnosis/shape-decision-2026-08-18.md``), so those two stay on the ``html``
    arm while every class not named here takes the build's own
    :attr:`~pipeline.config.PipelineConfig.detail_acquisition_mode`. A full migration would leave
    this file empty (or absent); every class then takes the configured default, exactly as it did
    before this feature.

    ``data_class`` is deliberately a closed set (``options``, ``default_equipment``) rather than
    a free string: it names the ONLY two classes this feature's own measurements evaluated, and it
    is what :data:`pipeline.acquire.detail_source._CLASS_TABLES` keys on to know which acquired
    table(s) the declared arm supplies. Reversal (FR-011) is editing this file — removing a record
    (or moving its ``arm``) changes which arm a class is read from, no code change.
    """

    data_class: Literal["options", "default_equipment"]
    arm: Literal["csv", "html"]
    reason: str = Field(min_length=1, max_length=240)
    declared_at: str
