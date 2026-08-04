# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the ability-summary authoring
# workflow's computed half (task T128): the current mechanic digest per ability key, joined from
# the detail source, and the effective review status each key carries once that digest is
# compared against what a curator most recently approved (FR-020, FR-023, FR-024, research D6).
"""Compare an ability's *current* mechanic against what a curator approved.

Two things this module deliberately does **not** do:

* it never writes `curation/` — the authored file's stored `review_state` is read, never
  overwritten, so the state-machine diagram in `pipeline.models.authored.ReviewState`'s
  docstring is conceptual rather than a set of writes this module performs (the data/<->
  curation/ invariant, FR-017); and
* it never emits `DQ-ABILITY-TYPE` — :mod:`pipeline.curate.assemble` already classifies every
  binding once while building `CuratedDatasheet.ability_keys`, and a second classification pass
  here raising the same finding a second time would double-count one defect in the report's
  scale figures.

Instead this module computes the **effective status** a key carries for *this* run: what the
catalogued `SUM-*` checks (:mod:`pipeline.validate.summaries`) and the coverage report
(:mod:`pipeline.report.coverage`) both need, and both call this rather than re-deriving it.

**Why a key can move from `approved` to needs-rereview without anyone editing a file.** The
stored `review_state` in `curation/abilities/<faction-id>.json` says what a curator most
recently approved *against*. Whether that approval is still current is a question only this
run's freshly acquired detail source can answer — comparing the stored `mechanic_digest`
against one computed from the *current* source text. When they disagree, this run treats the
key as effectively `needs_rereview` for validation and coverage purposes, exactly as if a human
had flipped it, even though the committed file still reads `approved` until a curator re-authors
it and updates the digest they approved against. A run with no fresh source text at all (a bare
`rules-pipeline validate`, which acquires nothing) has no evidence of drift and so trusts the
stored state as-is — it can still catch a key with no summary at all, or one a curator left in
`draft` or `in_review`, from the authored file alone.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from enum import StrEnum

from pipeline.models.authored import AbilitySummary, ReviewState
from pipeline.normalize.ability_types import classify
from pipeline.normalize.ip_strip import strip_field
from pipeline.normalize.mechanic_digest import mechanic_digest
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.reconcile.identity import slugify


class SummaryStatus(StrEnum):
    """The effective per-ability-key status this run observes.

    Mirrors :class:`~pipeline.models.authored.ReviewState` plus :attr:`MISSING`, which is not a
    review state at all — it means no authored record exists for a key the snapshot uses.
    """

    MISSING = "missing"
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    NEEDS_REREVIEW = "needs_rereview"
    APPROVED = "approved"

    @property
    def blocks_publication(self) -> bool:
        """Every status but :attr:`APPROVED` blocks (FR-020, FR-023, FR-024)."""
        return self is not SummaryStatus.APPROVED


_REVIEW_STATE_TO_STATUS: Mapping[ReviewState, SummaryStatus] = {
    ReviewState.DRAFT: SummaryStatus.DRAFT,
    ReviewState.IN_REVIEW: SummaryStatus.IN_REVIEW,
    ReviewState.NEEDS_REREVIEW: SummaryStatus.NEEDS_REREVIEW,
    ReviewState.APPROVED: SummaryStatus.APPROVED,
}


def compute_current_digests(detail: Mapping[str, CsvReadResult], *, key: bytes) -> dict[str, str]:
    """The current mechanic digest per ability key, joined from the detail source.

    An ability's mechanic text is its own `description` where the binding carries one (a
    datasheet-local override), else the text of the `Abilities.csv` row its `ability_id` names.
    Neither is retained past this function: only the keyed digest is returned (FR-013, C6/R8).

    A key used by more than one binding (the overwhelmingly common case — thousands of bindings
    resolve to a much smaller distinct set, research D6) is digested once, from the first
    binding carrying non-empty text, in source file order. Two bindings sharing a key are
    expected to share a mechanic; if the source ever disagrees, the first is authoritative for
    this run rather than the digest being taken twice and silently picking one.
    """
    bindings = detail.get("Datasheets_abilities.csv")
    if bindings is None:
        return {}

    by_ability_id: dict[str, str] = {}
    abilities = detail.get("Abilities.csv")
    if abilities is not None:
        for row in abilities.rows:
            ability_id = row.fields.get("id", "").strip()
            if ability_id and ability_id not in by_ability_id:
                by_ability_id[ability_id] = row.fields.get("description", "")

    digests: dict[str, str] = {}
    for row in bindings.rows:
        name = strip_field(row.fields.get("name", ""), field="ability.name").text
        if not name:
            continue
        ability_type, _finding = classify(row.fields.get("type", ""))
        if ability_type is None:
            continue  # DQ-ABILITY-TYPE already raised once by the assemble-stage pass.

        ability_key = f"{ability_type.value}:{slugify(name)}"
        if ability_key in digests:
            continue

        text = row.fields.get("description", "").strip()
        if not text:
            ability_id = row.fields.get("ability_id", "").strip()
            text = by_ability_id.get(ability_id, "")

        digests[ability_key] = mechanic_digest(text, key=key)

    return digests


def effective_status(
    ability_key: str,
    *,
    authored: Mapping[str, AbilitySummary],
    current_digest: str | None,
) -> SummaryStatus:
    """The status one ability key carries for this run (see module docstring).

    Args:
        current_digest: the digest computed from this run's freshly acquired source, or
            ``None`` when this run has no source text to compare against (a bare `validate`).
            ``None`` never flips an approved summary to needing re-review — there is no
            evidence of drift, only an absence of a fresh check.
    """
    summary = authored.get(ability_key)
    if summary is None:
        return SummaryStatus.MISSING
    if summary.review_state is not ReviewState.APPROVED:
        return _REVIEW_STATE_TO_STATUS[summary.review_state]
    if current_digest is not None and current_digest != summary.mechanic_digest:
        return SummaryStatus.NEEDS_REREVIEW
    return SummaryStatus.APPROVED


def summary_statuses(
    ability_keys: Iterable[str],
    *,
    authored: Mapping[str, AbilitySummary],
    current_digests: Mapping[str, str] | None = None,
) -> dict[str, SummaryStatus]:
    """:func:`effective_status` over every key the snapshot actually uses, once each.

    ``current_digests`` is ``None`` (rather than an empty mapping) both when this run has no
    source text at all and when it is simply empty; either way every key's lookup misses and no
    approved summary is flipped without evidence (see :func:`effective_status`).
    """
    digests = current_digests or {}
    return {
        key: effective_status(key, authored=authored, current_digest=digests.get(key))
        for key in sorted(set(ability_keys))
    }
