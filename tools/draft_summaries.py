#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the summary drafting tool (010 R7
# task 2): drives the Task-1 `SummaryClient` over a build report's outstanding summary findings
# and writes CANDIDATE records to a scratch directory for the Owner to read. It never writes
# `curation/` — a human does that, later, in a separate PR — and it refuses an `--out` that
# resolves inside the curation tree (amended standing rule 3, 2026-09-14; rule 4).
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R7 task 2 fix round 1: the attribution
# pair is written for every candidate whose key is already approved in `curation/` (not only the
# carried-approval path, which left a redrafted re-review candidate failing
# `check_summary_approvals.py`); the detachment id is resolved from the BUILD rather than
# re-slugged from the CSV name; the run is resumable, writes per class, survives a `DraftingError`
# with its partial results on disk, and files an invalid record rather than losing the batch;
# candidates are laid out per faction; `-UNAPPROVED` is left to the human who owns that draft.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R7 task 2 fix round 2: the detachment-rule
# join is driven from the report key (a name shared across factions reaches every curated id,
# not one), the ambiguous-source-id guard is adopted from the pipeline, the drafted count is
# recorded where the drafting happens rather than inferred, and a per-class
# keys/resolved/unresolved line is printed BEFORE the confirmation prompt.
# AI-Assisted: Claude Code (model: claude-opus-5[1m]) - 010 R7c task 2: a `--transport cli|api`
# switch (defaulting to the configured `cli`) that drives the run through `CliSummaryClient` and
# therefore needs no API key, and re-reviews issued in batches of at most ten through
# `review_many`, so the round-7 backlog of ~2000 re-reviews costs ~200 calls rather than 2000.
# The class pass is three phases now — gate, batched re-review, per-entry drafting — with every
# bucket, gate order and partial-write guarantee of the single loop it replaces.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 R8 task 3: `data_dir` is now derived
# from the report's own run root (`<run root>/out/data`, found by walking up from the report
# until it exists) instead of defaulting to `repository_root/data` — the committed tree, which
# round 7d found was silently swallowing every detachment rule new since round 6. No `--data`
# and no discoverable `out/data` is a `ConfigError` naming `--data`, never a silent fallback. The
# resolution table now prints the `data_dir` it used. `--rebaseline-authorization` replaces the
# hard-coded citation as a CLI parameter, defaulting to the prior constant, for task 5's
# per-round authorization string.
"""Draft candidate summaries for the entries a build reported as outstanding.

Standing rule 3 was amended on 2026-09-14: a summary may be **machine-drafted** from the
export's rules text, reviewed by a second model pass, and **approved by the Owner before
merge**. This tool is the drafting half of that, and nothing else. Read the four sentences it
is built around:

* **It produces candidates, never curation.** Every record lands under ``--out``, which must
  resolve outside the curation tree of both ``--repo`` and this checkout, or the run refuses
  before it starts. The Owner reads the candidates and copies what they approve into
  ``curation/`` by hand, in a separate pull request, which is where
  ``tools/check_summary_approvals.py`` meets them (standing rules 4 and 5, FR-017).
* **The export's rules text never leaves the workspace.** The acquisition, the join, and every
  API call happen inside one ``with workspace(...)`` block — the shape
  ``tools/churn_dry_run.py`` already uses — and what comes back out is a digest, a
  model-authored summary, and counts. Stdout carries **keys, counts and outcome labels only**:
  no mechanic text, no summary, no digest, no configured secret.
* **It spends money, so it asks first — and never spends it twice.** Before the first call it
  prints how many calls the work list implies and an order-of-magnitude token estimate, and
  waits for ``--yes`` or an interactive ``y``. Keys already drafted into ``--out`` by an earlier
  invocation are skipped, each class is written as it finishes, and a ``DraftingError`` keeps
  every candidate produced so far and exits non-zero. The live run has one budget; nothing here
  may discard work that has already been billed.
* **It never guesses.** A key the source does not publish, a detachment whose curated id this
  run cannot resolve, a record that fails its own model — each is reported by key and left for a
  human (standing rule 10).

::

    python tools/draft_summaries.py --report reports/candidate/report.json \\
        --out ../scratch/summary-candidates --version wh40k-11e-2026-09-1
    python tools/draft_summaries.py ... --classes abilities,detachment_rules --limit 25 --yes

**The re-baseline path.** A ``*-NEEDS-REREVIEW`` finding means an approved summary's mechanic
digest moved. The reviewing model is shown the *current* text beside the *approved* summary; a
``keep`` verdict produces a candidate that carries the existing summary and approval across the
move. A ``redraft`` verdict is treated as a missing summary and the entry is drafted fresh —
but the attribution pair is written either way, because see :func:`_record`.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Literal, Protocol, runtime_checkable

from pydantic import ValidationError

from pipeline.acquire.detail_source import acquire_detail, read_detail
from pipeline.acquire.http import AcquisitionError
from pipeline.config import ConfigError, PipelineConfig, load_config, repo_root
from pipeline.curate.summaries import binding_texts, compute_digests
from pipeline.exit_codes import ExitCode
from pipeline.models.authored import AbilitySummary, DetachmentRuleSummary, SummaryClass
from pipeline.normalize.ip_strip import strip_field
from pipeline.normalize.mechanic_digest import DigestKeyMissingError, resolve_digest_key
from pipeline.normalize.names import normalize_name
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.reconcile.identity import slugify
from pipeline.summaries import Draft, DraftingError, Verdict
from pipeline.summaries.cli_client import MAX_BATCH_ITEMS
from pipeline.workspace import workspace

PROG: Final = "draft_summaries.py"

#: The Owner's blanket authorization for this round's re-baseline candidates (Owner ruling 6,
#: 2026-09-15, superseding ruling 3). It is a **citation, not a permission**: writing it here
#: does not approve anything, it records which decision a reviewer is being asked to check the
#: candidate against. Every candidate this tool writes still has to be read and merged by hand.
REBASELINE_AUTHORIZATION: Final = "owner-2026-09-15-digest-key-rotation"

#: ``--classes`` default. The two classes this round has outstanding findings for.
DEFAULT_CLASSES: Final = ("abilities", "detachment_rules")

#: The file a key with no resolvable faction lands in. Placement is **editorial, not
#: correctness**: `pipeline.curate.authored` flattens every file of a class into one mapping, so
#: a record in the wrong file is still the same record. Naming the ambiguity is what matters.
UNASSIGNED: Final = "unassigned"

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

#: The export tables the detachment-rule join reads.
DETACHMENT_ABILITIES_FILE: Final = "Detachment_abilities.csv"
DETACHMENTS_FILE: Final = "Detachments.csv"

__all__ = [
    "DEFAULT_CLASSES",
    "REBASELINE_AUTHORIZATION",
    "UNASSIGNED",
    "Candidate",
    "ClassOutcome",
    "ConfirmationRefused",
    "DraftRun",
    "curated_detachments",
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
    """``--out`` resolves inside a ``curation/`` tree."""


class Drafter(Protocol):
    """The half of :class:`pipeline.summaries.SummaryClient` the drafting pass uses."""

    def draft(
        self,
        name: str,
        mechanic_text: str,
        *,
        ability_class: Literal["ability", "detachment_rule"],
        hint: str | None = None,
    ) -> Draft: ...


class Reviewer(Protocol):
    """The half of :class:`pipeline.summaries.SummaryClient` the reviewing pass uses."""

    def review(self, name: str, mechanic_text: str, summary: str) -> Verdict: ...


@runtime_checkable
class BatchReviewer(Protocol):
    """A reviewer that can take several entries in one call.

    Only :class:`pipeline.summaries.CliSummaryClient` implements it. Declared here rather than
    added to ``SummaryClient`` because the messages API transport has no batching to offer and a
    method that loops internally would be a second, slower implementation wearing the same name.
    Runtime-checkable so :func:`_review_batch` can ask the object rather than the caller.
    """

    def review_many(self, items: Sequence[tuple[str, str, str]]) -> list[Verdict]: ...


def _review_batch(reviewer: Reviewer, items: Sequence[tuple[str, str, str]]) -> list[Verdict]:
    """Review ``items`` — ``(name, mechanic_text, summary)`` triples — in as few calls as the
    reviewer allows, returning one verdict per item **in the order given**.

    One call when the reviewer batches, one call per item when it does not. This is the whole
    of the difference between the two transports inside the drafting loop: the loop above does
    not branch on the transport, and the api path keeps exactly today's call shape.
    """
    if isinstance(reviewer, BatchReviewer):
        return reviewer.review_many(items)
    return [reviewer.review(*item) for item in items]


@dataclass(frozen=True, slots=True)
class Candidate:
    """One record this run proposes, the class it belongs to, and the file it lands in."""

    summary_class: SummaryClass
    key: str
    faction: str
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

    dropped_invalid: tuple[str, ...] = ()
    """Keys whose candidate failed its own class model — an overlength summary, most likely."""

    verbatim: tuple[str, ...] = ()
    """Keys whose kept draft restated the mechanic as written (rule 3's narrow permission)."""

    unresolved: tuple[str, ...] = ()
    """Keys the report names that this run cannot pair with source text. Reported, not invented."""

    skipped_unapproved: tuple[str, ...] = ()
    """`-UNAPPROVED` keys: a human has a draft in flight, and this tool does not write over it."""

    already_drafted: tuple[str, ...] = ()
    """Keys an earlier invocation already wrote into ``--out``. Never paid for twice."""

    skipped_over_limit: tuple[str, ...] = ()
    """Keys ``--limit`` left for a later run."""

    not_attempted: tuple[str, ...] = ()
    """Keys the run never reached because a :class:`DraftingError` stopped it."""

    drafted: tuple[str, ...] = ()
    """Keys this class actually put through the drafting pass — **recorded, not inferred**.

    Fix round 2, D. Deriving the figure from the other buckets got two edges wrong, in opposite
    directions: a key dropped by :func:`_write` for failing its model was removed from ``kept``
    and so went uncounted although it had been drafted and billed; and a re-review key whose
    *review* verdict was ``lore`` was counted although it never reached the drafting pass at all.
    A figure that is recorded where the event happens cannot drift from the event.
    """

    candidates: tuple[Candidate, ...] = ()

    failure: str | None = None
    """Why this class stopped early, if it did. Never carries a reply body."""

    @property
    def entries_drafted(self) -> int:
        """How many **entries** this class put through the drafting pass.

        Entries, not API calls: a redrafted entry costs two draft calls and two review calls and
        counts once here. The printed label says ``entries-drafted`` for that reason — a
        diagnostic that reads as a call count while counting entries is the shipped-doc defect
        class, not a wording preference.
        """
        return len(self.drafted)


@dataclass(frozen=True, slots=True)
class DraftRun:
    """The whole run: per class, plus what was written where."""

    version: str
    acquisition_id: str
    out_dir: Path
    by_class: Mapping[str, ClassOutcome]
    written: tuple[Path, ...] = ()
    failure: str | None = None
    """Set when a :class:`DraftingError` stopped the run. Candidates written so far are on disk."""


# --------------------------------------------------------------------------------------
# Reading the report
# --------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _WorkList:
    """One class's outstanding keys, split by what the finding says about them."""

    fresh: tuple[str, ...] = ()
    """No summary exists at all: `-MISSING`, or the gated-off `-OUTSTANDING`."""

    rereview: tuple[str, ...] = ()
    """`-NEEDS-REREVIEW`: an approved summary whose mechanic digest moved."""

    unapproved: tuple[str, ...] = ()
    """`-UNAPPROVED`: a human's `draft`/`in_review` record. Reported, never written over."""

    # There was a `calls` property here, and it had no caller. Removed in 010 R7c task 2 rather
    # than taught about batching: two call counts that can disagree is exactly the shipped-
    # diagnostic defect class, and :func:`_estimate` is the one the human is shown.


#: Finding suffixes that mean "this entry has no summary at all".
#:
#: ``-UNAPPROVED`` is deliberately **not** here (010 R7 fix round 1, ruling on minor 8). It means
#: a human has a `draft` or `in_review` record in flight (`pipeline/validate/gates.py`), and
#: producing a machine candidate for a key a curator is mid-authoring crosses the human/machine
#: boundary standing rule 4 draws. Those keys are reported and left alone.
_FRESH_SUFFIXES: Final = ("-MISSING", "-OUTSTANDING")
_REREVIEW_SUFFIX: Final = "-NEEDS-REREVIEW"
_UNAPPROVED_SUFFIX: Final = "-UNAPPROVED"


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
        unapproved: list[str] = []
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
            elif code.endswith(_UNAPPROVED_SUFFIX):
                unapproved.append(key)
            elif code.endswith(_FRESH_SUFFIXES):
                fresh.append(key)
        lists[summary_class] = _WorkList(
            fresh=tuple(sorted(set(fresh))),
            rereview=tuple(sorted(set(rereview))),
            unapproved=tuple(sorted(set(unapproved))),
        )
    return lists


# --------------------------------------------------------------------------------------
# The joins: key -> (name, mechanic text)
# --------------------------------------------------------------------------------------


def _default_data_dir(report_path: Path) -> Path | None:
    """``<report's run root>/out/data``, or ``None`` when no ancestor of ``report_path`` has one.

    010 R8 task 3 (round 7d fix): the tool used to default to ``repository_root/data`` — the
    committed tree — regardless of which build the report came from, so every detachment rule
    new since round 6 was silently unresolved (``curated.get(detachment_id)`` returning
    ``None``). ``live_build.py`` writes its build under ``<run root>/out`` and its reports under
    ``<run root>/reports/<rules_version_id>/report.json``, which may or may not sit directly
    under ``<run root>`` (a caller is free to nest its own ``reports_root`` further, as
    ``live_build.py`` itself does). Walking upward from the report until an ``out/data``
    directory turns up finds the run root either way, without guessing a fixed number of
    parent hops that only one calling convention would satisfy.
    """
    for ancestor in Path(report_path).resolve().parents:
        candidate = ancestor / "out" / "data"
        if candidate.is_dir():
            return candidate
    return None


def curated_detachments(data_dir: Path) -> dict[str, tuple[str, str]]:
    """``detachment_id -> (curated name, faction_id)``, read from the built snapshot tree.

    **Why the build and not the CSV.** The curated detachment id is minted from the *points
    source's* card name (``pipeline/curate/assemble.py``'s
    ``registry.mint(EntityKind.DETACHMENT, key, card.detachment_name)``), and the detail source
    is joined to it by :func:`pipeline.normalize.names.normalize_name`, which folds NFKC and
    typographic characters and strips a leading article — none of which
    :func:`pipeline.reconcile.identity.slugify` does. Deriving the id from the CSV name instead
    produces a different id whenever the two spellings differ by an article or by punctuation,
    and the key it produces is one no curated record ever uses. The pipeline says this about
    itself two lines away: *"a second derivation is a second chance to disagree"*.

    So the ids are **read from the build the report came from** rather than re-derived. A tree
    that is absent, or that does not carry a detachment, yields nothing for that key and the key
    is reported ``unresolved`` — which is a stated gap a human can act on, where a wrong id is a
    summary approved against a rule it does not describe.
    """
    resolved: dict[str, tuple[str, str]] = {}
    if not data_dir.is_dir():
        return resolved
    for path in sorted(data_dir.glob("*/factions/*/detachments.json")):
        faction_id = path.parent.name
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("detachments", []) if isinstance(payload, dict) else payload
        for row in rows:
            identifier = row.get("detachment_id")
            name = row.get("name")
            if isinstance(identifier, str) and isinstance(name, str) and identifier not in resolved:
                resolved[identifier] = (name, faction_id)
    return resolved


def _source_detachment_rules(
    detail: Mapping[str, CsvReadResult],
) -> tuple[dict[str, list[tuple[str, str]]], set[str]]:
    """``normalised detachment name -> [(rule name, mechanic text)]``, plus the ambiguous ids.

    The pipeline's own guard, adopted rather than paraphrased
    (``pipeline/curate/assemble.py::_source_detachment_rules``, "issue #5"): a source detachment
    **id** that publishes two differently-named detachments names neither of them and is
    **deleted**, not resolved to whichever row was read last. Last-write-wins here would attach a
    rule to the wrong detachment, and in this project a wrong record the Owner then approves is
    worse than a missing one — a missing one is an outstanding entry a curator sees.

    Grouped by the **normalised name** rather than by the source id, because the curated id is
    minted from the points card and the two taxonomies share no id; the normalised name is the
    only thing they have in common, and it is the join the pipeline already performs.
    """
    detachments = detail.get(DETACHMENTS_FILE)
    abilities = detail.get(DETACHMENT_ABILITIES_FILE)
    if detachments is None or abilities is None:
        return {}, set()

    names_by_id: dict[str, str] = {}
    ambiguous: set[str] = set()
    for row in detachments.rows:
        identifier = row.fields.get("id", "").strip()
        if not identifier:
            continue
        name = normalize_name(strip_field(row.fields.get("name", ""), field="detachment.name").text)
        if not name:
            continue
        if identifier in names_by_id and names_by_id[identifier] != name:
            ambiguous.add(identifier)
        names_by_id[identifier] = name
    for identifier in ambiguous:
        del names_by_id[identifier]

    grouped: dict[str, list[tuple[str, str]]] = {}
    for row in abilities.rows:
        normalised = names_by_id.get(row.fields.get("detachment_id", "").strip())
        name = strip_field(row.fields.get("name", ""), field="detachment_rule.name").text
        if not normalised or not name:
            continue
        rules = grouped.setdefault(normalised, [])
        if all(existing != name for existing, _text in rules):
            rules.append((name, row.fields.get("description", "").strip()))
    return grouped, ambiguous


def detachment_rule_texts(
    detail: Mapping[str, CsvReadResult],
    *,
    curated: Mapping[str, tuple[str, str]],
    keys: Iterable[str],
) -> Iterator[tuple[str, str, str]]:
    """``(summary_key, rule name, mechanic text)`` for each outstanding detachment-rule key.

    The abilities class has :func:`pipeline.curate.summaries.binding_texts`, which the digest
    join itself consumes, so the two can never disagree. **The detachment-rule class has no such
    join in the pipeline yet** — ``pipeline/cli.py`` passes ``current_digests=None`` for it — so
    this is the first one, and it is stated here rather than in ``pipeline/`` because nothing
    under ``pipeline/`` reads it: a join with one caller belongs with its caller until it has two.

    **Driven from the report's keys, not from the source rows** (010 R7 fix round 2, A). A
    source-driven join has to answer "which curated id does this detachment name belong to", and
    that question has no single answer: 16 normalised detachment names in the live tree are shared
    across roughly six factions each — the Space Marine chapter duplicates
    (``d-anvil-siege-force`` and its ``-2`` … ``-6``), which are exactly the per-chapter
    identifiers the C1 ruling exists to hold apart. Any one-to-one map, ``setdefault`` or
    last-write-wins alike, silently makes 78 of 346 detachment ids unreachable and drops the 68
    rules they carry.

    The key already carries the answer. ``detachment:<id>:<slug>`` names the curated id, so this
    reads the curated **name** for that id and matches it one-to-many against the source's
    detachments, then picks the rule whose name slugifies back to ``<slug>``. Every chapter's id
    resolves to the same shared source rows and each gets its own key, which is the behaviour the
    ruling requires.

    A key whose id the build does not carry, or whose slug no rule matches, yields nothing and is
    reported ``unresolved`` — a stated gap a human can act on, where a wrong pairing would be a
    summary approved against a rule it does not describe.
    """
    grouped, _ambiguous = _source_detachment_rules(detail)
    if not grouped:
        return

    seen: set[str] = set()
    for key in keys:
        if key in seen or key.count(":") < 2:
            continue
        _prefix, detachment_id, slug = key.split(":", 2)
        entry = curated.get(detachment_id)
        if entry is None:
            continue
        for name, text in grouped.get(normalize_name(entry[0]), ()):
            if slugify(name) == slug:
                seen.add(key)
                yield key, name, text
                break


def _texts_for(
    summary_class: SummaryClass,
    detail: Mapping[str, CsvReadResult],
    *,
    curated: Mapping[str, tuple[str, str]],
    keys: Iterable[str],
) -> dict[str, tuple[str, str]]:
    """``key -> (name, mechanic text)`` for one class, from this run's acquired source.

    The abilities join enumerates the source; the detachment-rule join is driven from ``keys``.
    That asymmetry is the source's, not a design preference: an ability key is derivable from the
    binding row alone, and a detachment-rule key is not (see :func:`detachment_rule_texts`).
    """
    join = (
        binding_texts(detail)
        if summary_class is SummaryClass.ABILITIES
        else detachment_rule_texts(detail, curated=curated, keys=keys)
    )
    return {key: (name, text) for key, name, text in join}


# --------------------------------------------------------------------------------------
# Reading what the curator already approved, and what an earlier invocation already drafted
# --------------------------------------------------------------------------------------


def _authored_records(
    curation_dir: Path, summary_class: SummaryClass
) -> dict[str, tuple[dict[str, Any], str]]:
    """``key -> (the committed record, the file stem it came from)``.

    Read, never written. Two things need it: the re-baseline path needs the approved ``summary``,
    and :func:`_record` needs to know whether the key is already approved in ``curation/``. The
    **file stem** is carried because it is the faction the record belongs to — the one piece of
    faction attribution a re-baseline candidate can state with certainty, and it was being
    discarded before fix round 1.
    """
    directory = curation_dir / _CLASS_DIRECTORY[summary_class]
    if not directory.is_dir():
        return {}
    key_field = summary_class.key_field
    records: dict[str, tuple[dict[str, Any], str]] = {}
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else payload.get("rules", [])
        for record in rows:
            key = record.get(key_field)
            if isinstance(key, str) and key not in records:
                records[key] = (dict(record), path.stem)
    return records


def existing_candidates(out_dir: Path, summary_class: SummaryClass) -> dict[str, set[str]]:
    """``file stem -> the keys an earlier invocation already wrote there``.

    The resume mechanism, and it is a **key-presence** check rather than an offset or a cursor
    on purpose: an offset is a second piece of state that can be wrong, and it goes wrong exactly
    when the work list changes between invocations — which it does, because a rebuilt report is
    what produces the work list. "Is this key already drafted into the output I am about to
    extend" is answerable from the output alone and cannot drift from it.
    """
    directory = out_dir / _CLASS_DIRECTORY[summary_class]
    if not directory.is_dir():
        return {}
    key_field = summary_class.key_field
    present: dict[str, set[str]] = {}
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        keys = {
            record[key_field]
            for record in payload
            if isinstance(record, dict) and isinstance(record.get(key_field), str)
        }
        present[path.stem] = keys
    return present


# --------------------------------------------------------------------------------------
# The confirmation gate
# --------------------------------------------------------------------------------------


def _estimate(
    work: Mapping[SummaryClass, _WorkList],
    texts: Mapping[SummaryClass, Mapping[str, tuple[str, str]]],
    drafted: Mapping[SummaryClass, set[str]],
    *,
    batch_size: int | None,
) -> tuple[int, int]:
    """``(calls, tokens)`` the confirmed work list implies, before any redraft.

    A **lower bound**, and said to be one where it is printed: a reviewer that sends a draft
    back costs one more draft and one more review, and there is no way to know in advance how
    many will. Keys an earlier invocation already drafted, and keys the source does not publish,
    are excluded — the estimate is what this invocation will actually spend.

    ``batch_size`` is the reviewer's own batch limit, or ``None`` when it does not batch. It is
    derived from the reviewer object rather than from the transport name, because it has to be
    the same fact :func:`_review_batch` acts on: an estimate that counts calls the run will not
    make is a diagnostic that contradicts behaviour, however plausible the number looks.
    """
    calls = 0
    characters = 0
    for summary_class, item in work.items():
        per_class = texts.get(summary_class, {})
        done = drafted.get(summary_class, set())
        for key in item.fresh:
            entry = per_class.get(key)
            if entry is None or key in done:
                continue
            calls += 2
            characters += len(entry[1])
        reviews = 0
        for key in item.rereview:
            entry = per_class.get(key)
            if entry is None or key in done:
                continue
            reviews += 1
            characters += len(entry[1])
        # Ceiling division: a last partial batch is still one call.
        calls += reviews if batch_size is None else -(-reviews // batch_size)
    return calls, calls * _PER_CALL_OVERHEAD_TOKENS + characters // _CHARS_PER_TOKEN


def _report_resolution(
    selected: Sequence[SummaryClass],
    work: Mapping[SummaryClass, _WorkList],
    texts: Mapping[SummaryClass, Mapping[str, tuple[str, str]]],
    drafted: Mapping[SummaryClass, set[str]],
    *,
    data_dir: Path,
) -> None:
    """Per class, before the prompt: how many outstanding keys this run can actually pair with text.

    Printed **before** the confirmation gate and not only in the closing report (fix round 2, E).
    The session has one billed run; an unresolved count that only appears afterwards is a number
    nobody can act on. A large ``unresolved`` here means the source or the ``--data`` tree is not
    the one the report came from, and the answer is to say no at the prompt and check, not to
    spend the budget and read about it later.

    ``data_dir`` is printed **once, before the per-class lines** (010 R8 task 3): the detachment
    join reads it, and a human deciding whether ``unresolved`` looks wrong needs to see which
    tree was actually read, not infer it from ``--data`` or a default they may not remember.
    """
    print(f"{PROG}: data_dir={data_dir}")
    for summary_class in selected:
        item = work[summary_class]
        keys = (*item.rereview, *item.fresh)
        resolved = sum(1 for key in keys if key in texts.get(summary_class, {}))
        already = sum(
            1
            for key in keys
            if key in texts.get(summary_class, {}) and key in drafted.get(summary_class, set())
        )
        print(
            f"{PROG}: {summary_class.value}: keys={len(keys)} resolved={resolved} "
            f"unresolved={len(keys) - resolved} already-drafted={already} "
            f"skipped-unapproved={len(item.unapproved)}"
        )


def _confirm(calls: int, tokens: int, *, assume_yes: bool, transport: str) -> None:
    """Print the estimate and refuse unless a human, or ``--yes``, says go.

    Prints a **count**, never a sample: the estimate is derived from the length of the text, not
    from the text, so that the thing a human is being asked to authorise sending is still not on
    their screen when they authorise it.

    The ``cli`` transport is a subscription seat, so its line states calls and **no token
    figure**: a token count there is a number with no meaning attached to it, shown to the one
    person whose job at that moment is to decide whether the number is acceptable. The ``api``
    transport is billed by token and its line is unchanged.
    """
    noun = "CLI calls" if transport == "cli" else "API calls"
    if transport == "cli":
        print(
            f"{PROG}: about to make at least {calls} {noun} on the cli transport "
            "(subscription seat), before redrafts"
        )
    else:
        print(f"{PROG}: about to make at least {calls} {noun}, ~{tokens} tokens, before redrafts")
    if assume_yes:
        print(f"{PROG}: --yes given; proceeding")
        return
    if not sys.stdin.isatty():
        raise ConfirmationRefused(
            f"{calls} {noun} were not confirmed: this run is not interactive and --yes was "
            "not given. Re-run with --yes when the estimate above is acceptable."
        )
    answer = input(f"{PROG}: proceed? [y/N] ").strip().lower()
    if answer not in {"y", "yes"}:
        raise ConfirmationRefused(f"{calls} {noun} were declined at the prompt")


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
    drafted: list[str] = field(default_factory=list)
    verbatim: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    unapproved: list[str] = field(default_factory=list)
    already: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    not_attempted: list[str] = field(default_factory=list)
    candidates: list[Candidate] = field(default_factory=list)
    failure: str | None = None

    def freeze(self, summary_class: SummaryClass) -> ClassOutcome:
        return ClassOutcome(
            summary_class=summary_class,
            kept=tuple(self.kept),
            rebaselined=tuple(self.rebaselined),
            redrafted=tuple(self.redrafted),
            dropped_lore=tuple(self.dropped_lore),
            dropped_unresolved=tuple(self.dropped_unresolved),
            drafted=tuple(self.drafted),
            verbatim=tuple(self.verbatim),
            unresolved=tuple(self.unresolved),
            skipped_unapproved=tuple(self.unapproved),
            already_drafted=tuple(self.already),
            skipped_over_limit=tuple(self.skipped),
            not_attempted=tuple(self.not_attempted),
            candidates=tuple(self.candidates),
            failure=self.failure,
        )


def _draft_one(
    name: str,
    text: str,
    *,
    summary_class: SummaryClass,
    drafter: Drafter,
    reviewer: Reviewer,
) -> tuple[Draft | None, Verdict, bool]:
    """Draft, review, and — where the reviewer says so — draft once more, **with the reason**.

    Returns ``(accepted draft or None, the last verdict, whether a redraft happened)``.

    The second attempt carries the first verdict's ``reason_code`` through
    :meth:`SummaryClient.draft`'s ``hint`` (added in fix round 1), so a redraft is directed
    rather than an undirected second sample. The reason code is one of our own four; no
    publisher material travels in it.
    """
    ability_class = _CLASS_ABILITY_CLASS[summary_class]
    draft = drafter.draft(name, text, ability_class=ability_class)
    verdict = reviewer.review(name, text, draft.summary)
    if verdict.decision == "keep":
        return draft, verdict, False

    second = drafter.draft(name, text, ability_class=ability_class, hint=verdict.reason_code)
    verdict = reviewer.review(name, text, second.summary)
    if verdict.decision == "keep":
        return second, verdict, True
    return None, verdict, True


def _record(  # noqa: PLR0913 - one argument per field the record carries
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
    rebaseline_authorization: str = REBASELINE_AUTHORIZATION,
) -> dict[str, Any]:
    """One candidate record, in the class's own field order, absent fields omitted.

    **When ``version`` is passed** the re-baseline attribution pair is written. Fix round 1
    widened the condition that decides that, and the reason is worth stating because the first
    reading of it was wrong. ``tools/check_summary_approvals.py``'s ``digest_refreshes``
    classifies ``carries_approval`` from the base and head ``review_state`` **alone**: a key that
    is ``approved`` in ``curation/`` at base and ``approved`` in the merged candidate at head,
    with a moved ``mechanic_digest``, carries an approval as far as that guard is concerned — no
    matter that this tool re-drafted the summary from scratch and considers it new authorship.
    Omitting the pair for a redrafted re-review candidate therefore failed CI on merge with
    "refreshes mechanic_digest on a record that is approved at both ends … without freshly naming
    the version". So the caller passes ``version`` for **any** key already approved in
    ``curation/``, and the tool's notion of "carried approval" is aligned with the guard's rather
    than argued with.
    """
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
        values["digest_refreshed_under_authorization"] = rebaseline_authorization

    order = _FIELD_ORDER[summary_class]
    return {field_name: values[field_name] for field_name in order if field_name in values}


@dataclass(frozen=True, slots=True)
class _ClassInputs:
    """Everything one class's pass reads. A record rather than fifteen parameters."""

    texts: Mapping[str, tuple[str, str]]
    digests: Mapping[str, str]
    authored: Mapping[str, tuple[dict[str, Any], str]]
    curated: Mapping[str, tuple[str, str]]
    already: set[str]
    reviewed_by: str
    reviewed_at: str
    acquisition_id: str
    version: str
    limit: int | None
    rebaseline_authorization: str


def _faction_of(
    summary_class: SummaryClass,
    key: str,
    *,
    authored: Mapping[str, tuple[dict[str, Any], str]],
    curated: Mapping[str, tuple[str, str]],
) -> str:
    """The file stem a candidate belongs in, or :data:`UNASSIGNED`.

    Three sources, in order of certainty: the ``curation/`` file the key already lives in (a
    re-baseline, or any key a curator has touched); the built snapshot's own faction directory
    (every detachment rule, since a detachment belongs to exactly one faction); and otherwise
    nothing — a fresh ``core:`` or multi-faction ability key genuinely has no single faction, and
    :data:`UNASSIGNED` says so rather than picking one.
    """
    known = authored.get(key)
    if known is not None:
        return known[1]
    if summary_class is SummaryClass.DETACHMENT_RULES and key.count(":") >= 2:
        entry = curated.get(key.split(":")[1])
        if entry is not None:
            return entry[1]
    return UNASSIGNED


@dataclass(frozen=True, slots=True)
class _WorkItem:
    """One key that passed the gates, with everything the two call phases need, read once.

    Built by :func:`_work_items` so that the batching phase can look at a whole chunk of keys
    without re-deriving per-key facts, and so that the candidate a key produces is assembled
    from exactly the same five values whichever phase produces it.
    """

    key: str
    is_rereview: bool
    name: str
    """The display name the source publishes for this key."""

    text: str
    digest: str
    faction: str
    version: str | None
    """The version a re-baseline is attributed to, or ``None`` when no approval is carried."""

    prior_summary: str | None
    """The approved summary to re-review, or ``None`` when this key goes straight to drafting."""

    prior_name: str
    """The display name a carried-across candidate keeps: the curated one, else the source's."""


def _work_items(
    ordered: Sequence[tuple[str, bool]],
    summary_class: SummaryClass,
    inputs: _ClassInputs,
    *,
    tally: _ClassTally,
) -> list[_WorkItem]:
    """Phase 0: the three gates, in today's order, without making one call.

    Hoisted out of the drafting loop so that phase 1 can see a whole class's re-reviews at once
    and batch them. Behaviour-preserving because no gate reads a result: ``unresolved`` before
    ``already`` before ``--limit``, and ``worked`` counts exactly the keys that reach a call.
    ``ordered`` still puts re-reviews first, so a ``--limit`` still runs out on drafting.
    """
    items: list[_WorkItem] = []
    worked = 0
    for key, is_rereview in ordered:
        entry = inputs.texts.get(key)
        if entry is None:
            # Standing rule 10: a key measured at zero gets no code, and a key this run cannot
            # pair with source text gets no guess. It is reported and left for a human.
            tally.unresolved.append(key)
            continue
        if key in inputs.already:
            tally.already.append(key)
            continue
        if inputs.limit is not None and worked >= inputs.limit:
            tally.skipped.append(key)
            continue
        worked += 1
        items.append(
            _work_item(
                key, entry, is_rereview=is_rereview, summary_class=summary_class, inputs=inputs
            )
        )
    return items


def _work_item(
    key: str,
    entry: tuple[str, str],
    *,
    is_rereview: bool,
    summary_class: SummaryClass,
    inputs: _ClassInputs,
) -> _WorkItem:
    """Everything one key's candidate is built from — the prologue of the old ``_work_one``."""
    name, text = entry
    prior_entry = inputs.authored.get(key)
    prior = prior_entry[0] if prior_entry is not None else None
    # The guard's own test, not ours: a key already approved in curation/ whose digest moves is a
    # re-baseline as far as check_summary_approvals.py is concerned, however the summary got
    # here. See `_record`.
    approved_in_curation = prior is not None and prior.get("review_state") == "approved"
    summary = prior.get("summary") if prior is not None else None
    prior_name = prior.get("name") if prior is not None else None
    return _WorkItem(
        key=key,
        is_rereview=is_rereview,
        name=name,
        text=text,
        digest=inputs.digests[key],
        faction=_faction_of(summary_class, key, authored=inputs.authored, curated=inputs.curated),
        version=inputs.version if approved_in_curation else None,
        prior_summary=summary if is_rereview and isinstance(summary, str) else None,
        prior_name=prior_name if isinstance(prior_name, str) and prior_name else name,
    )


def _add(
    item: _WorkItem,
    summary: str,
    display_name: str,
    *,
    tally: _ClassTally,
    summary_class: SummaryClass,
    inputs: _ClassInputs,
) -> None:
    """Record one candidate. The single construction site, whichever phase produced it."""
    tally.kept.append(item.key)
    tally.candidates.append(
        Candidate(
            summary_class,
            item.key,
            item.faction,
            _record(
                summary_class,
                item.key,
                name=display_name,
                summary=summary,
                digest=item.digest,
                reviewed_by=inputs.reviewed_by,
                reviewed_at=inputs.reviewed_at,
                acquisition_id=inputs.acquisition_id,
                version=item.version,
                rebaseline_authorization=inputs.rebaseline_authorization,
            ),
        )
    )


def _run_class(
    summary_class: SummaryClass,
    work: _WorkList,
    inputs: _ClassInputs,
    *,
    drafter: Drafter,
    reviewer: Reviewer,
) -> ClassOutcome:
    """One class's whole pass, in three phases. Stops on a :class:`DraftingError`, keeping what
    it has.

    Phase 0 gates without calling anything; phase 1 re-reviews the keys that have an approved
    summary, up to :data:`MAX_BATCH_ITEMS` per call; phase 2 drafts, one entry at a time, the
    fresh keys and the ones phase 1 sent back. Splitting the old single loop is what turns this
    round's ~2000 re-reviews into ~200 calls; every bucket a key can land in, the order the
    gates apply in, and the partial-write guarantee are the loop's own and are unchanged.
    """
    tally = _ClassTally()
    tally.unapproved.extend(work.unapproved)

    # Re-review first: it is the cheaper call (one review, no draft) and the one whose outcome
    # can turn into drafting work, so a --limit that runs out should run out on drafting.
    rereview = set(work.rereview)
    ordered: list[tuple[str, bool]] = [(key, True) for key in work.rereview]
    ordered += [(key, False) for key in work.fresh if key not in rereview]

    pending = _work_items(ordered, summary_class, inputs, tally=tally)

    # A re-review key with no usable prior summary is a missing summary, and goes straight to
    # drafting exactly as it did before there were phases.
    reviewable: list[tuple[_WorkItem, str]] = []
    queue: list[_WorkItem] = []
    for item in pending:
        prior = item.prior_summary
        if prior is None:
            queue.append(item)
        else:
            reviewable.append((item, prior))

    redrafts: list[_WorkItem] = []
    for start in range(0, len(reviewable), MAX_BATCH_ITEMS):
        chunk = reviewable[start : start + MAX_BATCH_ITEMS]
        try:
            verdicts = _review_batch(reviewer, [(i.name, i.text, s) for i, s in chunk])
            if len(verdicts) != len(chunk):
                # Defence in depth behind `CliSummaryClient`'s own length check, and raised as a
                # `DraftingError` rather than left to `zip(strict=True)`'s `ValueError` (fix
                # round 1, Important 2). Nothing in this module, `draft_candidates` or `main`
                # catches `ValueError`, so a mismatch used to discard the whole class's
                # already-paid-for candidates and print a traceback — exactly the failure mode
                # the write-inside-the-loop exists to prevent. Same detail string the client
                # uses, so one shape has one name wherever it is noticed.
                raise DraftingError(None, "cli-batch-shape")
        except DraftingError as exc:
            # The bill for everything before this point is already paid. Stop the class, keep the
            # candidates, name the batch this stopped on, and let the caller write and report.
            # `redrafts` joins not-attempted: those keys were reviewed but never drafted, and a
            # key in no bucket at all would vanish from the report the operator resumes from.
            tally.failure = f"stopped at {chunk[0][0].key}: {exc}"
            tally.not_attempted.extend(
                entry.key for entry in (*redrafts, *(i for i, _ in reviewable[start:]), *queue)
            )
            return tally.freeze(summary_class)
        # `strict=True` cannot fire: the guard above has already stopped an unequal reply.
        for (item, _prior), verdict in zip(chunk, verdicts, strict=True):
            if verdict.decision == "keep":
                tally.rebaselined.append(item.key)
                _add(
                    item,
                    _prior,
                    item.prior_name,
                    tally=tally,
                    summary_class=summary_class,
                    inputs=inputs,
                )
            elif verdict.decision == "lore":
                tally.dropped_lore.append(item.key)
            else:
                # `redraft`: the approved summary no longer describes the mechanic, so this is a
                # missing summary and joins the drafting queue below.
                redrafts.append(item)

    drafting = [*redrafts, *queue]
    for index, item in enumerate(drafting):
        try:
            _draft_item(
                item,
                tally=tally,
                summary_class=summary_class,
                inputs=inputs,
                drafter=drafter,
                reviewer=reviewer,
            )
        except DraftingError as exc:
            tally.failure = f"stopped at {item.key}: {exc}"
            tally.not_attempted.extend(rest.key for rest in drafting[index + 1 :])
            break

    return tally.freeze(summary_class)


def _draft_item(
    item: _WorkItem,
    *,
    tally: _ClassTally,
    summary_class: SummaryClass,
    inputs: _ClassInputs,
    drafter: Drafter,
    reviewer: Reviewer,
) -> None:
    """Draft one entry and file the outcome — the drafting half of the old ``_work_one``."""
    # Recorded HERE, at the one call site of the drafting pass, so the figure is an
    # observation rather than an inference from buckets that later change (fix round 2, D).
    tally.drafted.append(item.key)
    draft, verdict, redrafted = _draft_one(
        item.name, item.text, summary_class=summary_class, drafter=drafter, reviewer=reviewer
    )
    if redrafted:
        tally.redrafted.append(item.key)
    if draft is None:
        if verdict.decision == "lore":
            tally.dropped_lore.append(item.key)
        else:
            tally.dropped_unresolved.append(item.key)
        return
    if draft.used_verbatim:
        tally.verbatim.append(item.key)
    _add(item, draft.summary, item.name, tally=tally, summary_class=summary_class, inputs=inputs)


# --------------------------------------------------------------------------------------
# --out safety
# --------------------------------------------------------------------------------------


def resolve_out_dir(out: Path, repository_root: Path) -> Path:
    """The absolute ``--out``, refused if it resolves inside **any** ``curation/`` in play.

    Both ``--repo``'s curation tree and this checkout's own are compared, because ``--repo`` is
    an argument and an argument can be wrong: ``--repo /tmp/anything --out <real repo>/curation``
    passed the single-root check while writing straight into the tree the whole tool exists to
    keep out of (fix round 1, minor 6).

    Resolved with :meth:`Path.resolve` on both sides before comparing, so ``work/../curation``, a
    symlink, and a relative path all reach the same answer. The check is on the resolved path and
    not on the spelling, because the spelling is exactly what an accident gets wrong.
    """
    resolved = Path(out).resolve()
    roots = {Path(repository_root).resolve(), repo_root().resolve()}
    for root in sorted(roots):
        curation = (root / "curation").resolve()
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
    data_dir: Path | None = None,
    limit: int | None = None,
    assume_yes: bool = False,
    now: datetime | None = None,
    transport: str = "api",
    rebaseline_authorization: str = REBASELINE_AUTHORIZATION,
) -> DraftRun:
    """Acquire, join, draft, review, write candidates — and discard the acquired text.

    Everything that touches the export's rules text happens inside the ``with workspace(...)``
    block, the API calls included: that is the only place the text exists, and what leaves the
    block is a set of candidate records and a tally of keys.

    **Each class is written as it completes**, not at the end. The live run has exactly one
    budget; a failure in the second class must not discard the first class's paid-for work.

    ``transport`` names how ``drafter``/``reviewer`` reach a model, and is used for **one**
    thing: whether the cost line quotes a token figure. Whether re-reviews are batched is asked
    of the reviewer object instead, so the printed call count cannot disagree with the calls the
    run then makes.
    """
    resolved_out = resolve_out_dir(out_dir, repository_root)
    selected = [SummaryClass(name) for name in classes]
    key = resolve_digest_key(config)
    findings = json.loads(Path(report_path).read_text(encoding="utf-8")).get("findings", [])
    work = work_lists(findings, selected)
    curation = curation_dir or (Path(repository_root) / "curation")
    if data_dir is not None:
        data = Path(data_dir)
    else:
        derived = _default_data_dir(report_path)
        if derived is None:
            raise ConfigError(
                f"cannot derive data_dir from {report_path}: no <run root>/out/data directory "
                "found above it. This tool never falls back to the committed data/ tree — pass "
                "--data <path to the build's snapshot tree> explicitly"
            )
        data = derived
    curated = curated_detachments(Path(data))
    authored = {
        summary_class: _authored_records(curation, summary_class) for summary_class in selected
    }
    already = {
        summary_class: set().union(*existing_candidates(resolved_out, summary_class).values())
        if existing_candidates(resolved_out, summary_class)
        else set()
        for summary_class in selected
    }
    reviewed_by = f"{config.review_model}-reviewer"
    reviewed_at = (now or datetime.now(UTC)).astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    outcomes: dict[str, ClassOutcome] = {}
    written: list[Path] = []
    failure: str | None = None
    with workspace(repository_root) as work_path:
        acquisition, payloads = acquire_detail(
            config, fixtures_dir=fixtures_dir, offline=offline, workspace=work_path
        )
        detail = read_detail(payloads)
        texts = {
            summary_class: _texts_for(
                summary_class,
                detail,
                curated=curated,
                keys=(*work[summary_class].rereview, *work[summary_class].fresh),
            )
            for summary_class in selected
        }
        digests = {
            summary_class: compute_digests({k: v[1] for k, v in per_class.items()}, key=key)
            for summary_class, per_class in texts.items()
        }

        _report_resolution(selected, work, texts, already, data_dir=data)
        batch_size = MAX_BATCH_ITEMS if isinstance(reviewer, BatchReviewer) else None
        calls, tokens = _estimate(work, texts, already, batch_size=batch_size)
        _confirm(calls, tokens, assume_yes=assume_yes, transport=transport)

        for summary_class in selected:
            if failure is not None:
                outcomes[summary_class.value] = ClassOutcome(
                    summary_class=summary_class,
                    not_attempted=tuple(
                        sorted({*work[summary_class].fresh, *work[summary_class].rereview})
                    ),
                    failure="an earlier class stopped the run",
                )
                continue
            outcome = _run_class(
                summary_class,
                work[summary_class],
                _ClassInputs(
                    texts=texts[summary_class],
                    digests=digests[summary_class],
                    authored=authored[summary_class],
                    curated=curated,
                    already=already[summary_class],
                    reviewed_by=reviewed_by,
                    reviewed_at=reviewed_at,
                    acquisition_id=acquisition.acquisition_id,
                    version=version,
                    limit=limit,
                    rebaseline_authorization=rebaseline_authorization,
                ),
                drafter=drafter,
                reviewer=reviewer,
            )
            # Written HERE, inside the loop and before the next class starts: a DraftingError in
            # the next class must not cost this one's paid-for candidates.
            outcome, paths = _write(resolved_out, outcome)
            outcomes[summary_class.value] = outcome
            written.extend(paths)
            if outcome.failure is not None:
                failure = outcome.failure

    run = DraftRun(
        version=version,
        acquisition_id=acquisition.acquisition_id,
        out_dir=resolved_out,
        by_class=outcomes,
        written=tuple(written),
        failure=failure,
    )
    _report(run)
    return run


def _write(out_dir: Path, outcome: ClassOutcome) -> tuple[ClassOutcome, tuple[Path, ...]]:
    """Write one class's candidates, per faction file, and return the outcome plus the paths.

    Three properties, each of which cost a finding to learn:

    * **Validation is per record, not per batch.** ``DetachmentRuleSummary.summary`` caps at
      1 000 characters, so an overlong draft raises ``ValidationError`` — which, uncaught, lost
      the whole class's candidates *and* rendered pydantic's truncated ``input_value`` repr, i.e.
      summary text, onto the terminal. The record is dropped into ``dropped-invalid`` **by key
      only**: the exception is never rendered, printed, or carried.
    * **A class with no candidates writes no file.** An empty array on disk reads as "this class
      is done", which is exactly the false green ``CLAUDE.md``'s first trap is about.
    * **An existing file is extended, not replaced.** Records already in it are kept, so a
      resumed run adds to what the previous one paid for. Sorted by key on write so the file is
      reviewable and a re-run is a no-op.
    """
    per_faction: dict[str, list[dict[str, Any]]] = {}
    invalid: list[str] = []
    model_for = _MODEL[outcome.summary_class]
    for candidate in outcome.candidates:
        record = dict(candidate.record)
        try:
            model_for.model_validate(record)
        except ValidationError:
            # By key only. `ValidationError.__str__` renders the input it rejected, and the input
            # here is a summary — see the docstring.
            invalid.append(candidate.key)
            continue
        per_faction.setdefault(candidate.faction, []).append(record)

    key_field = outcome.summary_class.key_field
    written: list[Path] = []
    for faction, records in sorted(per_faction.items()):
        path = out_dir / _CLASS_DIRECTORY[outcome.summary_class] / f"{faction}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        merged: dict[str, dict[str, Any]] = {}
        if path.exists():
            for record in json.loads(path.read_text(encoding="utf-8")):
                if isinstance(record, dict) and isinstance(record.get(key_field), str):
                    merged[record[key_field]] = record
        for record in records:
            merged[str(record[key_field])] = record
        ordered = [merged[k] for k in sorted(merged)]
        path.write_text(json.dumps(ordered, indent=2) + "\n", encoding="utf-8", newline="\n")
        written.append(path)

    if not invalid:
        return outcome, tuple(written)
    kept = tuple(k for k in outcome.kept if k not in set(invalid))
    return (
        ClassOutcome(
            summary_class=outcome.summary_class,
            kept=kept,
            rebaselined=tuple(k for k in outcome.rebaselined if k not in set(invalid)),
            redrafted=outcome.redrafted,
            dropped_lore=outcome.dropped_lore,
            dropped_unresolved=outcome.dropped_unresolved,
            dropped_invalid=tuple(sorted(invalid)),
            # NOT filtered by `invalid`: the entry was drafted and billed, and the count says
            # what this run spent, not what survived validation.
            drafted=outcome.drafted,
            verbatim=outcome.verbatim,
            unresolved=outcome.unresolved,
            skipped_unapproved=outcome.skipped_unapproved,
            already_drafted=outcome.already_drafted,
            skipped_over_limit=outcome.skipped_over_limit,
            not_attempted=outcome.not_attempted,
            candidates=outcome.candidates,
            failure=outcome.failure,
        ),
        tuple(written),
    )


def _report(run: DraftRun) -> None:
    """Stdout: keys, counts and outcome labels. Never text, never a digest, never a secret."""
    print(f"{PROG}: candidates for {run.version} under {run.out_dir}")
    for name, outcome in run.by_class.items():
        print(
            f"{PROG}: {name}: entries-drafted={outcome.entries_drafted} "
            f"kept={len(outcome.kept)} rebaselined={len(outcome.rebaselined)} "
            f"redrafted={len(outcome.redrafted)} dropped-lore={len(outcome.dropped_lore)} "
            f"dropped-invalid={len(outcome.dropped_invalid)} verbatim={len(outcome.verbatim)} "
            f"unresolved={len(outcome.unresolved)} "
            f"skipped-unapproved={len(outcome.skipped_unapproved)} "
            f"already-drafted={len(outcome.already_drafted)} "
            f"over-limit={len(outcome.skipped_over_limit)} "
            f"not-attempted={len(outcome.not_attempted)}"
        )
        for label, keys in (
            ("kept", outcome.kept),
            ("rebaselined", outcome.rebaselined),
            ("redrafted", outcome.redrafted),
            ("dropped-lore", outcome.dropped_lore),
            ("dropped-unresolved", outcome.dropped_unresolved),
            ("dropped-invalid", outcome.dropped_invalid),
            ("verbatim", outcome.verbatim),
            ("unresolved", outcome.unresolved),
            ("skipped-unapproved", outcome.skipped_unapproved),
            ("already-drafted", outcome.already_drafted),
            ("over-limit", outcome.skipped_over_limit),
            ("not-attempted", outcome.not_attempted),
        ):
            for key in keys:
                print(f"{PROG}:   {name} {label} {key}")
    for path in run.written:
        print(f"{PROG}: wrote {path}")
    if run.failure is not None:
        print(f"{PROG}: RUN INCOMPLETE — {run.failure}")
        print(
            f"{PROG}: every candidate produced before that point is on disk; re-run with the "
            "same --out to resume from where this stopped."
        )
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
    parser.add_argument("--limit", type=int, help="work at most N new entries per class")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    parser.add_argument("--repo", type=Path, help="repository root (default: this checkout)")
    parser.add_argument("--curation", type=Path, help="curation tree to READ (never written)")
    parser.add_argument(
        "--data", type=Path, help="built snapshot tree the report came from (READ; never written)"
    )
    parser.add_argument(
        "--transport",
        choices=("cli", "api"),
        default=None,
        help=(
            "how to reach the model: cli (a Claude Code subscription seat) or api (the billed "
            "messages API). Default: WGC_DRAFT_TRANSPORT."
        ),
    )
    parser.add_argument("--fixtures", type=Path, help="source from a synthetic fixture set")
    parser.add_argument(
        "--offline", action="store_true", help="refuse network access; requires --fixtures"
    )
    parser.add_argument(
        "--rebaseline-authorization",
        default=REBASELINE_AUTHORIZATION,
        help=(
            "the Owner ruling a re-baseline candidate's digest_refreshed_under_authorization "
            f"cites (default: {REBASELINE_AUTHORIZATION!r})"
        ),
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(
    argv: Sequence[str] | None = None,
    *,
    env: Mapping[str, str] | None = None,
    clients: tuple[Drafter, Reviewer] | None = None,
) -> int:
    """The CLI entry point.

    ``clients`` substitutes the two :class:`SummaryClient` instances. It exists so the exit-code
    contract — which is what CI and the operator branch on — can be exercised without a socket,
    and so a future dry-run harness can drive the whole path. ``None`` (every real invocation)
    builds the real clients from the configured key.
    """
    args = _parse_args(argv)
    root = args.repo or repo_root()

    try:
        resolve_out_dir(args.out, root)
        config = load_config(env=env) if env is not None else load_config()
        # An explicit --transport overrides the configured default.
        transport = str(args.transport or config.draft_transport)
        # Only the api path spends a key, and only the api path may refuse for the want of one:
        # the whole point of the cli transport is a drafting run that needs no API credential.
        if transport == "api" and not config.anthropic_api_key:
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

    from contextlib import AbstractContextManager, nullcontext

    from pipeline.summaries import CliSummaryClient, SummaryClient

    drafting: Drafter
    reviewing: Reviewer
    # `CliSummaryClient` holds no connection to close, so it enters through `nullcontext` for the
    # same reason injected clients do rather than growing an `__enter__` it has no work for.
    contexts: tuple[AbstractContextManager[Any], AbstractContextManager[Any]]
    if clients is not None:
        drafting, reviewing = clients
        contexts = (nullcontext(drafting), nullcontext(reviewing))
    elif transport == "cli":
        cli_drafting = CliSummaryClient(model=config.draft_model, executable=config.claude_cli)
        cli_reviewing = CliSummaryClient(model=config.review_model, executable=config.claude_cli)
        drafting, reviewing = cli_drafting, cli_reviewing
        contexts = (nullcontext(cli_drafting), nullcontext(cli_reviewing))
    else:
        api_drafting = SummaryClient(config.anthropic_api_key, model=config.draft_model)
        api_reviewing = SummaryClient(config.anthropic_api_key, model=config.review_model)
        drafting, reviewing = api_drafting, api_reviewing
        contexts = (api_drafting, api_reviewing)

    try:
        with contexts[0], contexts[1]:
            run = draft_candidates(
                config,
                repository_root=root,
                report_path=args.report,
                out_dir=args.out,
                version=args.version,
                drafter=drafting,
                reviewer=reviewing,
                classes=classes,
                fixtures_dir=args.fixtures,
                offline=args.offline,
                curation_dir=args.curation,
                data_dir=args.data,
                limit=args.limit,
                assume_yes=args.yes,
                transport=transport,
                rebaseline_authorization=args.rebaseline_authorization,
            )
    except (ConfigError, DigestKeyMissingError, ConfirmationRefused) as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)
    except DraftingError as exc:
        # Belt and braces: `draft_candidates` catches this per key and writes what it has, so
        # reaching here means it escaped the per-key handler (a failure outside the drafting
        # loop). Reported as the same class of outcome rather than as a traceback.
        print(f"{PROG}: drafting stopped: {exc}", file=sys.stderr)
        return int(ExitCode.SOURCE_UNAVAILABLE)
    except AcquisitionError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(exc.exit_code)

    if run.failure is not None:
        # Non-zero, and NOT zero-with-a-warning: an incomplete run that exits 0 is a green check
        # over work that did not happen. The candidates are on disk either way.
        print(f"{PROG}: {run.failure}", file=sys.stderr)
        return int(ExitCode.SOURCE_UNAVAILABLE)
    return int(ExitCode.SUCCESS)


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
