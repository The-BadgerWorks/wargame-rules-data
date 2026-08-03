# AI-Assisted: Claude Code (model: claude-opus-5) - Defined the authored records of
# data-model.md §4 (task T023), including the AbilitySummary review-state machine of §4.1 and
# the digest-bound FindingResolution of validation-report.md §5.
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

from collections.abc import Mapping
from enum import StrEnum

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
    """

    mfm_slug: str
    faction_id: str
    parent_faction_id: str | None = None
    detail_source_faction_id: str


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
