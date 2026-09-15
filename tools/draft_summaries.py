#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the summary drafting tool (010 R7
# task 2): drives the Task-1 `SummaryClient` over a build report's outstanding summary findings
# and writes CANDIDATE records to a scratch directory for the Owner to read. It never writes
# `curation/` — a human does that, later, in a separate PR — and it refuses an `--out` that
# resolves inside the repository's curation tree (amended standing rule 3, 2026-09-14; rule 4).
"""Draft candidate summaries for the entries a build reported as outstanding.

Standing rule 3 was amended on 2026-09-14: a summary may be **machine-drafted** from the
export's rules text, reviewed by a second model pass, and **approved by the Owner before
merge**. This tool is the drafting half of that, and nothing else. Read the three sentences it
is built around:

* **It produces candidates, never curation.** Every record lands under ``--out``, which must
  resolve outside the repository's ``curation/`` tree or the run refuses before it starts. The
  Owner reads the candidates and copies what they approve into ``curation/`` by hand, in a
  separate pull request, which is where ``tools/check_summary_approvals.py`` meets them
  (standing rules 4 and 5, FR-017).
* **The export's rules text never leaves the workspace.** The acquisition, the join, and every
  API call happen inside one ``with workspace(...)`` block — the shape
  ``tools/churn_dry_run.py`` already uses — and what comes back out is a digest, a
  model-authored summary, and counts. Stdout carries **keys, counts and verdict codes only**:
  no mechanic text, no digest, no configured secret.
* **It spends money, so it asks first.** Before the first call it prints how many calls the
  work list implies and an order-of-magnitude token estimate, and waits for ``--yes`` or an
  interactive ``y``. A non-interactive run without ``--yes`` refuses rather than proceeding.

::

    python tools/draft_summaries.py --report reports/candidate/report.json \\
        --out ../scratch/summary-candidates --version wh40k-11e-2026-09-1
    python tools/draft_summaries.py ... --classes abilities,detachment_rules --limit 25 --yes

**The re-baseline path.** A ``*-NEEDS-REREVIEW`` finding means an approved summary's mechanic
digest moved. The reviewing model is shown the *current* text beside the *approved* summary; a
``keep`` verdict produces a candidate that carries the existing summary and approval across the
move with the **new** digest and the attribution pair
``digest_refreshed_at_version`` / ``digest_refreshed_under_authorization``
(FR-028/FR-029) that ``tools/check_summary_approvals.py`` requires. A ``redraft`` verdict is
treated exactly as a missing summary: the approval is not carried, and no attribution pair is
written, because there is nothing to attribute — the summary is new.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Literal, Protocol

from pipeline.acquire.detail_source import acquire_detail, read_detail
from pipeline.acquire.http import AcquisitionError
from pipeline.config import ConfigError, PipelineConfig, load_config, repo_root
from pipeline.curate.summaries import binding_texts, compute_digests, detachment_rule_key
from pipeline.exit_codes import ExitCode
from pipeline.models.authored import AbilitySummary, DetachmentRuleSummary, SummaryClass
from pipeline.normalize.ip_strip import strip_field
from pipeline.normalize.mechanic_digest import DigestKeyMissingError, resolve_digest_key
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.reconcile.identity import slugify
from pipeline.summaries import Draft, Verdict
from pipeline.workspace import workspace

PROG: Final = "draft_summaries.py"

#: The Owner's blanket authorization for this round's re-baseline candidates (Owner ruling 6,
#: 2026-09-15, superseding ruling 3). It is a **citation, not a permission**: writing it here
#: does not approve anything, it records which decision a reviewer is being asked to check the
#: candidate against. Every candidate this tool writes still has to be read and merged by hand.
REBASELINE_AUTHORIZATION: Final = "owner-2026-09-15-digest-key-rotation"

#: ``--classes`` default. The two classes this round has outstanding findings for.
DEFAULT_CLASSES: Final = ("abilities", "detachment_rules")

#: The directory each class's candidates land in, under ``--out``. Named after the ``curation/``
#: directory the Owner will eventually merge them into, so the correspondence is obvious while
#: the path very plainly is not that directory.
_CLASS_DIRECTORY: Final[Mapping[SummaryClass, str]] = {
    SummaryClass.ABILITIES: "abilities",
    SummaryClass.DETACHMENT_RULES: "detachment-rules",
}

#: The client's ``ability_class`` argument per summary class.
_CLASS_ABILITY_CLASS: Final[Mapping[SummaryClass, Literal["ability", "detachment_rule"]]] = {
    SummaryClass.ABILITIES: "ability",
    SummaryClass.DETACHMENT_RULES: "detachment_rule",
}

#: Field order per class, matching the committed `curation/` files byte-for-byte in the fields
#: they already carry, so a candidate can be pasted into one without reformatting the file.
_FIELD_ORDER: Final[Mapping[SummaryClass, tuple[str, ...]]] = {
    SummaryClass.ABILITIES: (
        "ability_key",
        "authored_against_acquisition",
        "digest_refreshed_at_version",
        "digest_refreshed_under_authorization",
        "mechanic_digest",
        "name",
        "review_state",
        "reviewed_at",
        "reviewed_by",
        "summary",
    ),
    SummaryClass.DETACHMENT_RULES: (
        "summary_key",
        "detachment_id",
        "name",
        "summary",
        "review_state",
        "mechanic_digest",
        "reviewed_by",
        "reviewed_at",
        "digest_refreshed_at_version",
        "digest_refreshed_under_authorization",
    ),
}

_MODEL: Final[Mapping[SummaryClass, type[AbilitySummary] | type[DetachmentRuleSummary]]] = {
    SummaryClass.ABILITIES: AbilitySummary,
    SummaryClass.DETACHMENT_RULES: DetachmentRuleSummary,
}

#: A crude characters-per-token divisor, and the fixed per-call overhead of the system prompt and
#: the reply. This is an **order-of-magnitude estimate shown to a human before they say yes**, not
#: an accounting figure; it is deliberately not derived from a tokenizer, because a tokenizer
#: would have to be handed the mechanic text and the point of the estimate is that nobody has
#: committed to sending it yet.
_CHARS_PER_TOKEN: Final = 4
_PER_CALL_OVERHEAD_TOKENS: Final = 700

#: The export table the detachment-rule join reads.
DETACHMENT_ABILITIES_FILE: Final = "Detachment_abilities.csv"
DETACHMENTS_FILE: Final = "Detachments.csv"

__all__ = [
    "DEFAULT_CLASSES",
    "REBASELINE_AUTHORIZATION",
    "Candidate",
    "ClassOutcome",
    "ConfirmationRefused",
    "DraftRun",
    "detachment_rule_texts",
    "draft_candidates",
    "main",
]


class ConfirmationRefused(RuntimeError):
    """The run was not confirmed, so not one API call was made.

    Raised rather than returned so that there is no path on which a caller can ignore it and
    carry on spending: the work list is computed, the estimate is printed, and the run stops.
    """


class OutsideCurationError(ValueError):
    """``--out`` resolves inside the repository's ``curation/`` tree."""


class Drafter(Protocol):
    """The half of :class:`pipeline.summaries.SummaryClient` the drafting pass uses."""

    def draft(
        self,
        name: str,
        mechanic_text: str,
        *,
        ability_class: Literal["ability", "detachment_rule"],
    ) -> Draft: ...


class Reviewer(Protocol):
    """The half of :class:`pipeline.summaries.SummaryClient` the reviewing pass uses."""

    def review(self, name: str, mechanic_text: str, summary: str) -> Verdict: ...


@dataclass(frozen=True, slots=True)
class Candidate:
    """One record this run proposes, and the class it belongs to."""

    summary_class: SummaryClass
    key: str
    record: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ClassOutcome:
    """What happened to one class's work list. Keys and counts — never a summary, never text."""

    summary_class: SummaryClass
    kept: tuple[str, ...] = ()
    """Keys that produced a candidate, re-baselines included."""

    rebaselined: tuple[str, ...] = ()
    """The subset of :attr:`kept` whose approval was carried across a digest move."""

    redrafted: tuple[str, ...] = ()
    """Keys the reviewer sent back at least once before keeping."""

    dropped_lore: tuple[str, ...] = ()
    """Keys the reviewer called lore twice. Reported, never guessed at — standing rule 10."""

    dropped_unresolved: tuple[str, ...] = ()
    """Keys whose second attempt still did not pass review for a non-lore reason."""

    verbatim: tuple[str, ...] = ()
    """Keys whose kept draft restated the mechanic as written (rule 3's narrow permission)."""

    unresolved: tuple[str, ...] = ()
    """Keys the report names that this run's source does not publish. Reported, not invented."""

    skipped_over_limit: tuple[str, ...] = ()
    """Keys ``--limit`` left for a later run."""

    candidates: tuple[Candidate, ...] = ()

    @property
    def drafted(self) -> int:
        """How many drafting calls this class's outcome represents."""
        return (
            len(self.kept)
            - len(self.rebaselined)
            + len(self.dropped_lore)
            + len(self.dropped_unresolved)
        )


@dataclass(frozen=True, slots=True)
class DraftRun:
    """The whole run: per class, plus what was written where."""

    version: str
    acquisition_id: str
    out_dir: Path
    by_class: Mapping[str, ClassOutcome]
    written: tuple[Path, ...] = ()


# --------------------------------------------------------------------------------------
# Reading the report
# --------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _WorkList:
    """One class's outstanding keys, split by what the finding says about them."""

    fresh: tuple[str, ...] = ()
    """No usable summary exists: `-MISSING`, `-UNAPPROVED`, or the gated-off `-OUTSTANDING`."""

    rereview: tuple[str, ...] = ()
    """`-NEEDS-REREVIEW`: an approved summary whose mechanic digest moved."""

    @property
    def calls(self) -> int:
        """The minimum number of API calls, before any redraft: draft+review, or review."""
        return 2 * len(self.fresh) + len(self.rereview)


#: Finding suffixes that mean "this entry has no summary a run can use".
_FRESH_SUFFIXES: Final = ("-MISSING", "-UNAPPROVED", "-OUTSTANDING")
_REREVIEW_SUFFIX: Final = "-NEEDS-REREVIEW"


def work_lists(
    findings: Sequence[Mapping[str, Any]], classes: Sequence[SummaryClass]
) -> dict[SummaryClass, _WorkList]:
    """Split a report's findings into each class's outstanding keys.

    The key is read from the finding's ``detail`` under the class's own key field — the field
    ``pipeline.validate.gates`` put it there under — and falls back to the first entity ref,
    because a resolved or suppressed finding may carry a trimmed detail.
    """
    lists: dict[SummaryClass, _WorkList] = {}
    for summary_class in classes:
        prefix = summary_class.finding_prefix
        key_field = summary_class.key_field
        fresh: list[str] = []
        rereview: list[str] = []
        for finding in findings:
            code = str(finding.get("finding_code", ""))
            if not code.startswith(f"{prefix}-"):
                continue
            detail = finding.get("detail") or {}
            refs = finding.get("entity_refs") or []
            key = str(detail.get(key_field) or (refs[0] if refs else ""))
            if not key:
                continue
            if code.endswith(_REREVIEW_SUFFIX):
                rereview.append(key)
            elif code.endswith(_FRESH_SUFFIXES):
                fresh.append(key)
        lists[summary_class] = _WorkList(
            fresh=tuple(sorted(set(fresh))), rereview=tuple(sorted(set(rereview)))
        )
    return lists


# --------------------------------------------------------------------------------------
# The joins: key -> (name, mechanic text)
# --------------------------------------------------------------------------------------


def detachment_rule_texts(detail: Mapping[str, CsvReadResult]) -> Iterator[tuple[str, str, str]]:
    """``(summary_key, rule name, mechanic text)`` for every detachment rule the source binds.

    The abilities class has :func:`pipeline.curate.summaries.binding_texts`, which the digest
    join itself consumes, so the two can never disagree. **The detachment-rule class has no such
    join in the pipeline yet** — ``pipeline/cli.py`` passes ``current_digests=None`` for it — so
    this is the first one, and it is stated here rather than in ``pipeline/`` because nothing
    under ``pipeline/`` reads it: a join with one caller belongs with its caller until it has
    two. When the pipeline grows its own detachment digest join, this moves and both consume it.

    The detachment id is derived the way :class:`pipeline.reconcile.identity.IdRegistry` mints
    it — ``d-`` plus the slug of the detachment's own name — because that is the id the curated
    ``summary_key`` carries and this tool has no registry. The one case that derivation misses
    is a name collision the registry disambiguated with a numeric suffix; such a key simply
    finds no text and is reported as **unresolved** rather than being paired with the wrong
    rule. A summary approved against a rule it does not describe is not a milder failure than a
    missing summary.
    """
    detachments = detail.get(DETACHMENTS_FILE)
    abilities = detail.get(DETACHMENT_ABILITIES_FILE)
    if detachments is None or abilities is None:
        return

    ids: dict[str, str] = {}
    for row in detachments.rows:
        identifier = row.fields.get("id", "").strip()
        name = strip_field(row.fields.get("name", ""), field="detachment.name").text
        if not identifier or not name:
            continue
        ids[identifier] = f"d-{slugify(name)}"

    seen: set[str] = set()
    for row in abilities.rows:
        detachment_id = ids.get(row.fields.get("detachment_id", "").strip())
        name = strip_field(row.fields.get("name", ""), field="detachment_rule.name").text
        if not detachment_id or not name:
            continue
        key = detachment_rule_key(detachment_id, name)
        if key in seen:
            continue
        seen.add(key)
        yield key, name, row.fields.get("description", "").strip()


def _texts_for(
    summary_class: SummaryClass, detail: Mapping[str, CsvReadResult]
) -> dict[str, tuple[str, str]]:
    """``key -> (name, mechanic text)`` for one class, from this run's acquired source."""
    join = (
        binding_texts(detail)
        if summary_class is SummaryClass.ABILITIES
        else detachment_rule_texts(detail)
    )
    return {key: (name, text) for key, name, text in join}


# --------------------------------------------------------------------------------------
# Reading what the curator already approved
# --------------------------------------------------------------------------------------


def _authored_records(curation_dir: Path, summary_class: SummaryClass) -> dict[str, dict[str, Any]]:
    """``key -> the committed record``, read straight from the class's ``curation/`` files.

    Read, never written. The re-baseline path needs the approved ``summary`` to show the
    reviewing pass and to carry across the digest move; nothing here writes back.
    """
    directory = curation_dir / _CLASS_DIRECTORY[summary_class]
    if not directory.is_dir():
        return {}
    key_field = summary_class.key_field
    records: dict[str, dict[str, Any]] = {}
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else payload.get("rules", [])
        for record in rows:
            key = record.get(key_field)
            if isinstance(key, str) and key not in records:
                records[key] = dict(record)
    return records


# --------------------------------------------------------------------------------------
# The confirmation gate
# --------------------------------------------------------------------------------------


def _estimate(
    work: Mapping[SummaryClass, _WorkList], texts: Mapping[SummaryClass, Any]
) -> tuple[int, int]:
    """``(calls, tokens)`` the confirmed work list implies, before any redraft.

    A **lower bound**, and said to be one where it is printed: a reviewer that sends a draft
    back costs one more draft and one more review, and there is no way to know in advance how
    many will.
    """
    calls = sum(item.calls for item in work.values())
    characters = 0
    for summary_class, item in work.items():
        per_class = texts.get(summary_class, {})
        for key in (*item.fresh, *item.rereview):
            entry = per_class.get(key)
            if entry is not None:
                characters += len(entry[1])
    return calls, calls * _PER_CALL_OVERHEAD_TOKENS + characters // _CHARS_PER_TOKEN


def _confirm(calls: int, tokens: int, *, assume_yes: bool) -> None:
    """Print the estimate and refuse unless a human, or ``--yes``, says go.

    Prints a **count**, never a sample: the estimate is derived from the length of the text, not
    from the text, so that the thing a human is being asked to authorise sending is still not on
    their screen when they authorise it.
    """
    print(f"{PROG}: about to make at least {calls} API calls, ~{tokens} tokens, before redrafts")
    if assume_yes:
        print(f"{PROG}: --yes given; proceeding")
        return
    if not sys.stdin.isatty():
        raise ConfirmationRefused(
            f"{calls} API calls were not confirmed: this run is not interactive and --yes was "
            "not given. Re-run with --yes when the estimate above is acceptable."
        )
    answer = input(f"{PROG}: proceed? [y/N] ").strip().lower()
    if answer not in {"y", "yes"}:
        raise ConfirmationRefused(f"{calls} API calls were declined at the prompt")


# --------------------------------------------------------------------------------------
# The drafting loop
# --------------------------------------------------------------------------------------


@dataclass
class _ClassTally:
    """Mutable accumulator; frozen into a :class:`ClassOutcome` when the class is done."""

    kept: list[str] = field(default_factory=list)
    rebaselined: list[str] = field(default_factory=list)
    redrafted: list[str] = field(default_factory=list)
    dropped_lore: list[str] = field(default_factory=list)
    dropped_unresolved: list[str] = field(default_factory=list)
    verbatim: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    candidates: list[Candidate] = field(default_factory=list)

    def freeze(self, summary_class: SummaryClass) -> ClassOutcome:
        return ClassOutcome(
            summary_class=summary_class,
            kept=tuple(self.kept),
            rebaselined=tuple(self.rebaselined),
            redrafted=tuple(self.redrafted),
            dropped_lore=tuple(self.dropped_lore),
            dropped_unresolved=tuple(self.dropped_unresolved),
            verbatim=tuple(self.verbatim),
            unresolved=tuple(self.unresolved),
            skipped_over_limit=tuple(self.skipped),
            candidates=tuple(self.candidates),
        )


def _draft_one(
    name: str,
    text: str,
    *,
    summary_class: SummaryClass,
    drafter: Drafter,
    reviewer: Reviewer,
) -> tuple[Draft | None, Verdict, bool]:
    """Draft, review, and — where the reviewer says so — draft once more.

    Returns ``(accepted draft or None, the last verdict, whether a redraft happened)``.

    **The reason code is not fed back to the client.** Task 1 fixed ``draft``'s signature with no
    channel for it, and widening a frozen interface to carry a hint is a larger change than the
    hint is worth: the second attempt is a second sample, and a mechanic the model cannot
    restate twice is one the Owner should see as dropped rather than as coaxed. The code is
    still reported in the tally so a run that redrafts a lot says why.
    """
    ability_class = _CLASS_ABILITY_CLASS[summary_class]
    draft = drafter.draft(name, text, ability_class=ability_class)
    verdict = reviewer.review(name, text, draft.summary)
    if verdict.decision == "keep":
        return draft, verdict, False

    second = drafter.draft(name, text, ability_class=ability_class)
    verdict = reviewer.review(name, text, second.summary)
    if verdict.decision == "keep":
        return second, verdict, True
    return None, verdict, True


def _record(
    summary_class: SummaryClass,
    key: str,
    *,
    name: str,
    summary: str,
    digest: str,
    reviewed_by: str,
    reviewed_at: str,
    acquisition_id: str,
    version: str | None = None,
) -> dict[str, Any]:
    """One candidate record, in the class's own field order, absent fields omitted."""
    values: dict[str, Any] = {
        summary_class.key_field: key,
        "name": name,
        "summary": summary,
        "review_state": "approved",
        "mechanic_digest": digest,
        "reviewed_by": reviewed_by,
        "reviewed_at": reviewed_at,
    }
    if summary_class is SummaryClass.ABILITIES:
        values["authored_against_acquisition"] = acquisition_id
    else:
        # `detachment:<detachment-id>:<slug>` — the id the key already carries, rather than a
        # second derivation of it. DetachmentRuleSummary requires the field.
        values["detachment_id"] = key.split(":")[1] if key.count(":") >= 2 else ""
    if version is not None:
        values["digest_refreshed_at_version"] = version
        values["digest_refreshed_under_authorization"] = REBASELINE_AUTHORIZATION

    order = _FIELD_ORDER[summary_class]
    return {name_: values[name_] for name_ in order if name_ in values}


def _run_class(  # noqa: PLR0913 - one argument per input; the alternative is a context blob
    summary_class: SummaryClass,
    work: _WorkList,
    *,
    texts: Mapping[str, tuple[str, str]],
    digests: Mapping[str, str],
    authored: Mapping[str, dict[str, Any]],
    drafter: Drafter,
    reviewer: Reviewer,
    reviewed_by: str,
    reviewed_at: str,
    acquisition_id: str,
    version: str,
    limit: int | None,
) -> ClassOutcome:
    tally = _ClassTally()

    # Re-review first: it is the cheaper call (one review, no draft) and the one whose outcome
    # can turn into drafting work, so a --limit that runs out should run out on drafting.
    ordered: list[tuple[str, bool]] = [(key, True) for key in work.rereview]
    ordered += [(key, False) for key in work.fresh if key not in set(work.rereview)]

    worked = 0
    for key, is_rereview in ordered:
        entry = texts.get(key)
        if entry is None:
            # Standing rule 10: a key measured at zero gets no code, and a key the source does
            # not publish gets no guess. It is reported and left for a human.
            tally.unresolved.append(key)
            continue
        if limit is not None and worked >= limit:
            tally.skipped.append(key)
            continue
        worked += 1
        name, text = entry
        digest = digests[key]

        if is_rereview:
            prior = authored.get(key)
            if prior is not None and isinstance(prior.get("summary"), str):
                verdict = reviewer.review(name, text, prior["summary"])
                if verdict.decision == "keep":
                    tally.kept.append(key)
                    tally.rebaselined.append(key)
                    tally.candidates.append(
                        Candidate(
                            summary_class,
                            key,
                            _record(
                                summary_class,
                                key,
                                name=prior.get("name") or name,
                                summary=prior["summary"],
                                digest=digest,
                                reviewed_by=reviewed_by,
                                reviewed_at=reviewed_at,
                                acquisition_id=acquisition_id,
                                version=version,
                            ),
                        )
                    )
                    continue
                if verdict.decision == "lore":
                    tally.dropped_lore.append(key)
                    continue
                # `redraft`: the approved summary no longer describes the mechanic, so this is
                # a missing summary and falls through to the drafting path below. No attribution
                # pair is written — there is no approval being carried across anything.

        draft, verdict, redrafted = _draft_one(
            name, text, summary_class=summary_class, drafter=drafter, reviewer=reviewer
        )
        if redrafted:
            tally.redrafted.append(key)
        if draft is None:
            if verdict.decision == "lore":
                tally.dropped_lore.append(key)
            else:
                tally.dropped_unresolved.append(key)
            continue
        if draft.used_verbatim:
            tally.verbatim.append(key)
        tally.kept.append(key)
        tally.candidates.append(
            Candidate(
                summary_class,
                key,
                _record(
                    summary_class,
                    key,
                    name=name,
                    summary=draft.summary,
                    digest=digest,
                    reviewed_by=reviewed_by,
                    reviewed_at=reviewed_at,
                    acquisition_id=acquisition_id,
                ),
            )
        )

    return tally.freeze(summary_class)


# --------------------------------------------------------------------------------------
# --out safety
# --------------------------------------------------------------------------------------


def resolve_out_dir(out: Path, repository_root: Path) -> Path:
    """The absolute ``--out``, refused if it resolves inside the repository's ``curation/``.

    Resolved with :meth:`Path.resolve` on both sides before comparing, so ``work/../curation``,
    a symlink, and a relative path all reach the same answer. The check is on the resolved path
    and not on the spelling, because the spelling is exactly what an accident gets wrong.
    """
    resolved = Path(out).resolve()
    curation = (Path(repository_root).resolve() / "curation").resolve()
    if resolved == curation or curation in resolved.parents:
        raise OutsideCurationError(
            f"--out {resolved} is inside {curation}; this tool writes candidates only, and "
            "curation/ is written by a human in a separate pull request (standing rule 4)"
        )
    return resolved


# --------------------------------------------------------------------------------------
# The run
# --------------------------------------------------------------------------------------


def draft_candidates(  # noqa: PLR0913 - one argument per input, as tools/churn_dry_run.py's style
    config: PipelineConfig,
    *,
    repository_root: Path,
    report_path: Path,
    out_dir: Path,
    version: str,
    drafter: Drafter,
    reviewer: Reviewer,
    classes: Sequence[str] = DEFAULT_CLASSES,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    curation_dir: Path | None = None,
    limit: int | None = None,
    assume_yes: bool = False,
    now: datetime | None = None,
) -> DraftRun:
    """Acquire, join, draft, review, write candidates — and discard the acquired text.

    Everything that touches the export's rules text happens inside the ``with workspace(...)``
    block, the API calls included: that is the only place the text exists, and what leaves the
    block is a set of candidate records and a tally of keys.
    """
    resolved_out = resolve_out_dir(out_dir, repository_root)
    selected = [SummaryClass(name) for name in classes]
    key = resolve_digest_key(config)
    findings = json.loads(Path(report_path).read_text(encoding="utf-8")).get("findings", [])
    work = work_lists(findings, selected)
    curation = curation_dir or (Path(repository_root) / "curation")
    authored = {
        summary_class: _authored_records(curation, summary_class) for summary_class in selected
    }
    reviewed_by = f"{config.review_model}-reviewer"
    reviewed_at = (now or datetime.now(UTC)).astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    outcomes: dict[str, ClassOutcome] = {}
    with workspace(repository_root) as work_path:
        acquisition, payloads = acquire_detail(
            config, fixtures_dir=fixtures_dir, offline=offline, workspace=work_path
        )
        detail = read_detail(payloads)
        texts = {summary_class: _texts_for(summary_class, detail) for summary_class in selected}
        digests = {
            summary_class: compute_digests({k: v[1] for k, v in per_class.items()}, key=key)
            for summary_class, per_class in texts.items()
        }

        calls, tokens = _estimate(work, texts)
        _confirm(calls, tokens, assume_yes=assume_yes)

        for summary_class in selected:
            outcomes[summary_class.value] = _run_class(
                summary_class,
                work[summary_class],
                texts=texts[summary_class],
                digests=digests[summary_class],
                authored=authored[summary_class],
                drafter=drafter,
                reviewer=reviewer,
                reviewed_by=reviewed_by,
                reviewed_at=reviewed_at,
                acquisition_id=acquisition.acquisition_id,
                version=version,
                limit=limit,
            )

    written = _write(resolved_out, outcomes)
    run = DraftRun(
        version=version,
        acquisition_id=acquisition.acquisition_id,
        out_dir=resolved_out,
        by_class=outcomes,
        written=written,
    )
    _report(run)
    return run


def _write(out_dir: Path, outcomes: Mapping[str, ClassOutcome]) -> tuple[Path, ...]:
    """Write each class's candidates, validating every record as its class's authored model.

    Validating before writing rather than trusting the shape: a candidate that cannot load as
    the model the Owner will merge it as is a defect in this tool, and it should stop here
    rather than in a pull request. A class with no candidates writes **no file** — an empty
    array on disk reads as "this class is done", which is exactly the false green
    ``CLAUDE.md``'s first trap is about.
    """
    written: list[Path] = []
    for outcome in outcomes.values():
        if not outcome.candidates:
            continue
        model = _MODEL[outcome.summary_class]
        records = [dict(candidate.record) for candidate in outcome.candidates]
        for record in records:
            model.model_validate(record)
        path = out_dir / _CLASS_DIRECTORY[outcome.summary_class] / "candidates.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8", newline="\n")
        written.append(path)
    return tuple(written)


def _report(run: DraftRun) -> None:
    """Stdout: keys, counts and verdict outcomes. Never text, never a digest, never a secret."""
    print(f"{PROG}: candidates for {run.version} under {run.out_dir}")
    for name, outcome in run.by_class.items():
        print(
            f"{PROG}: {name}: drafted={outcome.drafted} kept={len(outcome.kept)} "
            f"rebaselined={len(outcome.rebaselined)} redrafted={len(outcome.redrafted)} "
            f"dropped-lore={len(outcome.dropped_lore)} verbatim={len(outcome.verbatim)} "
            f"unresolved={len(outcome.unresolved)} over-limit={len(outcome.skipped_over_limit)}"
        )
        for label, keys in (
            ("kept", outcome.kept),
            ("rebaselined", outcome.rebaselined),
            ("redrafted", outcome.redrafted),
            ("dropped-lore", outcome.dropped_lore),
            ("dropped-unresolved", outcome.dropped_unresolved),
            ("verbatim", outcome.verbatim),
            ("unresolved", outcome.unresolved),
            ("over-limit", outcome.skipped_over_limit),
        ):
            for key in keys:
                print(f"{PROG}:   {name} {label} {key}")
    for path in run.written:
        print(f"{PROG}: wrote {path}")
    print(
        f"{PROG}: nothing under curation/ was written. Read the candidates, approve what is "
        "correct, and merge them by hand in a separate pull request."
    )


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=PROG, description="Draft candidate summaries for a report's outstanding entries."
    )
    parser.add_argument("--report", type=Path, required=True, help="a build's report.json")
    parser.add_argument(
        "--out", type=Path, required=True, help="scratch directory for the candidates"
    )
    parser.add_argument(
        "--version", required=True, help="the version id a re-baseline is attributed to"
    )
    parser.add_argument(
        "--classes",
        default=",".join(DEFAULT_CLASSES),
        help=f"comma-separated summary classes (default: {','.join(DEFAULT_CLASSES)})",
    )
    parser.add_argument("--limit", type=int, help="work at most N entries per class")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    parser.add_argument("--repo", type=Path, help="repository root (default: this checkout)")
    parser.add_argument("--curation", type=Path, help="curation tree to READ (never written)")
    parser.add_argument("--fixtures", type=Path, help="source from a synthetic fixture set")
    parser.add_argument(
        "--offline", action="store_true", help="refuse network access; requires --fixtures"
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None, *, env: Mapping[str, str] | None = None) -> int:
    args = _parse_args(argv)
    root = args.repo or repo_root()

    try:
        resolve_out_dir(args.out, root)
        config = load_config(env=env) if env is not None else load_config()
        if not config.anthropic_api_key:
            raise ConfigError("WGC_ANTHROPIC_API_KEY is not set; this tool cannot draft without it")
        classes = tuple(name.strip() for name in str(args.classes).split(",") if name.strip())
        for name in classes:
            SummaryClass(name)
    except OutsideCurationError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)
    except (ConfigError, ValueError) as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    from pipeline.summaries import SummaryClient

    try:
        with (
            SummaryClient(config.anthropic_api_key, model=config.draft_model) as drafter,
            SummaryClient(config.anthropic_api_key, model=config.review_model) as reviewer,
        ):
            draft_candidates(
                config,
                repository_root=root,
                report_path=args.report,
                out_dir=args.out,
                version=args.version,
                drafter=drafter,
                reviewer=reviewer,
                classes=classes,
                fixtures_dir=args.fixtures,
                offline=args.offline,
                curation_dir=args.curation,
                limit=args.limit,
                assume_yes=args.yes,
            )
    except (ConfigError, DigestKeyMissingError, ConfirmationRefused) as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)
    except AcquisitionError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(exc.exit_code)

    return int(ExitCode.SUCCESS)


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
