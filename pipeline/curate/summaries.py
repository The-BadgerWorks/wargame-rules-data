# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the ability-summary authoring
# workflow's computed half (task T128): the current mechanic digest per ability key, joined from
# the detail source, and the effective review status each key carries once that digest is
# compared against what a curator most recently approved (FR-020, FR-023, FR-024, research D6).
# AI-Assisted: Claude Code (model: claude-opus-5) - Generalised the state and digest machinery
# over all four summary classes (004 task T045): `effective_status` and `summary_statuses` now
# read the structural :class:`AuthoredSummary`, and `compute_digests` states the digest step
# apart from the ability-specific join `compute_current_digests` still performs. The abilities
# code path is behaviourally identical — it is the same function with a wider parameter type.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the two remaining classes' key minting
# (004 task T053): `detachment_rule_key` and `glossary_key`, so a class's denominator is derived
# from the source rather than read back out of the curator's own file.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added `glossary_current_digests` (004 task
# T061): the §5.1 stem-digest fallback for a keyword the edition publishes no description for,
# and the honest consequence — such an entry never auto-flags for re-review.
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
from typing import Protocol

from pipeline.models.authored import ReviewState
from pipeline.normalize.ability_types import classify
from pipeline.normalize.ip_strip import strip_field
from pipeline.normalize.mechanic_digest import mechanic_digest
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.reconcile.identity import slugify


class AuthoredSummary(Protocol):
    """What this module needs of an authored record, in **any** of the four classes.

    Structural rather than nominal on purpose. `contracts/authored-summary-gates.md` §1 says the
    four classes share the review state, the record shape, the digest algorithm, the
    carry-forward rule and the self-approval refusal *without variation* — so the machinery is
    written against the shape they share rather than against a common base class the existing
    :class:`~pipeline.models.authored.AbilitySummary` would have had to be retrofitted into. The
    one field they genuinely differ on, the key, is never read here: every function below takes
    the key as its argument or as a mapping key, which is exactly why one code path serves four
    classes (research D6).
    """

    @property
    def name(self) -> str: ...

    @property
    def summary(self) -> str: ...

    @property
    def review_state(self) -> ReviewState: ...

    @property
    def mechanic_digest(self) -> str: ...


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


def detachment_rule_key(detachment_id: str, name: str) -> str:
    """``detachment:<detachment-id>:<slug>`` — one detachment rule's stable key (§2.2).

    Keyed on the detachment's **id** and the rule's own name, which is what makes the three edge
    cases fall out rather than needing special cases:

    * two detachments in **different factions** sharing a rule name get **different** keys,
      because their detachment ids differ;
    * a detachment **renamed upstream** keeps its curated id, so its rules keep their keys and
      their digests, and nothing re-reviews;
    * a **rule** renamed upstream is a different rule as far as authoring is concerned, and gets
      a new key — the old one falls out of the denominator and its record is orphaned rather than
      silently reattached to wording nobody approved.

    What the key deliberately does *not* encode is the rule's text: a rule changed while its name
    is unchanged keeps this key and moves its **digest**, which is the whole point of digesting
    the mechanic rather than the name.
    """
    return f"detachment:{detachment_id}:{slugify(name)}"


def glossary_key(keyword_key: str) -> str:
    """``glossary:<keyword_key>`` — one keyword definition's key (§2.3).

    The keyword key is already normalised by
    :func:`pipeline.normalize.keyword_key.normalize_keyword`, so casing, spacing, punctuation and
    numeric-parameter variants of one keyword have collapsed to one value before they reach here
    and therefore cannot produce two entries (FR-023).
    """
    return f"glossary:{keyword_key}"


def compute_digests(mechanic_texts: Mapping[str, str], *, key: bytes) -> dict[str, str]:
    """``summary_key -> keyed digest``, for **any** class (contract §1, §5).

    The digest step stated apart from the join that finds the text, because the join is the only
    part that differs per class: an ability's mechanic comes from the detail source's ability
    binding, a faction or detachment rule's from its own source row, and a keyword's — where the
    edition publishes no description at all — from the normalised keyword stem itself (§5.1).
    Whichever it is, the text reaches this function while it exists only in ephemeral ``work/``
    and **nothing but the digest comes back** (FR-027, C6/R8).
    """
    return {
        summary_key: mechanic_digest(text, key=key)
        for summary_key, text in sorted(mechanic_texts.items())
    }


def glossary_current_digests(
    keyword_keys: Iterable[str], *, mechanic_texts: Mapping[str, str] | None = None, key: bytes
) -> dict[str, str]:
    """``summary_key -> digest`` for every keyword in use, per contract §5.1.

    **The limitation this function embodies, stated plainly rather than engineered around.** No
    keyword glossary source exists. So:

    * where the edition publishes a core-rule or ability description for the keyword,
      ``mechanic_texts`` carries it and the digest is over that text — the entry then behaves
      exactly like an ability summary, flagging for re-review the moment the mechanic moves;
    * where it does not, the digest is over the **normalised keyword stem itself**. That stem is
      a pure function of the key, identical on every run forever, so such an entry **never
      auto-flags for re-review**.

    The compensating controls are elsewhere and are deliberate: ``GLS-ORPHANED`` catches
    definitions that have fallen out of use, and the digest-less subset is enumerated in
    ``summary-coverage.md`` (see :func:`digestless_keyword_keys`) so a reviewer can sweep it by
    hand before the glossary gate is switched on for the first time. Digesting the *usage set*
    instead would churn on every unrelated datasheet edit; digesting nothing would hide the gap.
    """
    texts = mechanic_texts or {}
    return compute_digests(
        {
            glossary_key(keyword_key): texts.get(keyword_key, keyword_key)
            for keyword_key in keyword_keys
        },
        key=key,
    )


def digestless_keyword_keys(
    keyword_keys: Iterable[str], *, mechanic_texts: Mapping[str, str] | None = None
) -> tuple[str, ...]:
    """The keywords whose digest is over the stem rather than over published text (§5.1).

    Enumerable **without the digest key**, because it is a question about which keywords the
    source describes and not about any digest value — which is what lets the coverage report name
    the subset for the manual sweep contract §7 item 4 requires.
    """
    texts = mechanic_texts or {}
    return tuple(sorted(key for key in set(keyword_keys) if key not in texts))


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
    summary_key: str,
    *,
    authored: Mapping[str, AuthoredSummary],
    current_digest: str | None,
) -> SummaryStatus:
    """The status one key carries for this run, in any class (see module docstring).

    Args:
        summary_key: the key in that class's own vocabulary — an ``ability_key`` for the
            existing class, a ``summary_key`` for the three new ones. This function never reads
            it off the record, only looks it up, which is what makes one path serve four classes.
        current_digest: the digest computed from this run's freshly acquired source, or
            ``None`` when this run has no source text to compare against (a bare `validate`).
            ``None`` never flips an approved summary to needing re-review — there is no
            evidence of drift, only an absence of a fresh check.
    """
    summary = authored.get(summary_key)
    if summary is None:
        return SummaryStatus.MISSING
    if summary.review_state is not ReviewState.APPROVED:
        return _REVIEW_STATE_TO_STATUS[summary.review_state]
    if current_digest is not None and current_digest != summary.mechanic_digest:
        return SummaryStatus.NEEDS_REREVIEW
    return SummaryStatus.APPROVED


def summary_statuses(
    summary_keys: Iterable[str],
    *,
    authored: Mapping[str, AuthoredSummary],
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
        for key in sorted(set(summary_keys))
    }
