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
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from pipeline.build.canonical_json import JsonValue


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
    """

    mfm_slug: str
    faction_id: str
    parent_faction_id: str | None = None
    detail_source_faction_id: str
    detail_source_publication_id: str | None = None


class UnitMapEntry(_Authored):
    """``curation/unit-map.json``, keyed by curated ``datasheet_id``.

    Consulted **before any name matching** (D5 stage 1). A confirmed pairing is never
    re-derived, so an upstream rename lands as a changed display name on an unchanged curated
    id — reported as a rename, never as a removal plus an addition (FR-015).
    """

    datasheet_id: str
    mfm_display_name: str
    wahapedia_datasheet_id: str
    confirmed_at: str
    confirmed_by: str


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
    summary: str = Field(min_length=1, max_length=400, description="authored, mechanics-only")
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
    """

    datasheet_id: str = Field(min_length=1)
    line: int = Field(ge=1)
    model_name: str = Field(min_length=1)
    min_count: int = Field(ge=0)
    max_count: int = Field(ge=0)
    model_line: int | None = Field(default=None, ge=1)
    note: str | None = None


class OptionOverrideChoice(_Authored):
    """One curator-authored choice inside an :class:`OptionOverrideEntry`."""

    name: str = Field(min_length=1)
    count: int | None = Field(default=None, ge=1)
    grants_weapon_line: int | None = Field(default=None, ge=1)
    replaces_weapon_line: int | None = Field(default=None, ge=1)
    is_default: bool = False
    is_no_change: bool = False


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
    min_choices: int | None = Field(default=None, ge=0)
    max_choices: int | None = Field(default=None, ge=0)
    choices: Sequence[OptionOverrideChoice] = ()
    note: str | None = None


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
