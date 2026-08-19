# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the CLI skeleton (task T029):
# the eight commands, the global options, the per-command options, and the exit-code mapping of
# contracts/pipeline-run-interface.md §1-§2, each command dispatching to its stage module.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wired `rules-pipeline publish` (task T116)
# to pipeline.publish.gate: locate the rebuilt bundle, re-validate, and hand off to the release
# and Pages steps, with the environment deployment's approval record read from the Actions run
# context (task T117, FR-038, FR-039).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wired `rules-pipeline withdraw` (task T141)
# to pipeline.publish.withdraw, and `rules-pipeline verify` (task T143) to pipeline.publish.
# verify with its own ledger entry, completing the eight-command contract surface (FR-044,
# SC-007, SC-009).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wired `pipeline.report.trends.
# render_trends` (task T149) into both `write_reports` call sites (`run_build` and
# `run_validate`), reading `state/run-ledger.jsonl` from the real repository root each time so
# the trend is always a property of the actual run history, never of a fixture's synthetic one.
# AI-Assisted: Claude Code (model: claude-opus-5) - Wired 006's loadout coverage into both report
# paths (006 tasks T038, T039): the two `loadout.*` rows and the COV-OPTION-REGRESSION ratchet,
# deliberately OUTSIDE CoverageOutcome.findings -- that set's non-emptiness exits 42 for a source
# collapse, and a resolved-option regression is a defect in this pipeline rather than evidence
# that the source went strange.
# AI-Assisted: Claude Code (model: claude-opus-5) - Read the coverage collapse off the RESOLVED
# findings in `_verdict` (006 T049 follow-on). A dated resolution suppressed the finding in the
# report and satisfied `pipeline.publish.gate.blocking_finding_codes`, but `CoverageOutcome`'s own
# `collapsed` is computed before any resolution exists, so exit 42 alone ignored it -- three
# answers to one question, and the only blocking finding FR-034 could not actually resolve.
# AI-Assisted: Claude Code (model: claude-opus-5) - Wired `published_at` to the `build` command
# (`--published-at`, `--published-at-from-report`). It had been documented as a build input by
# `run_build`'s own docstring and by curated-snapshot-format.md §6 since 002, and was reachable
# from no invocation at all, so every build stamped its own UTC day and `publish.yml`'s rebuild
# of an approved candidate failed FR-039 with exit 51 the moment approval crossed 00:00Z.
"""``rules-pipeline`` — the operator-facing surface.

The same CLI runs locally against fixtures and in CI against the real sources: **there is no
CI-only code path**, so a curator can reproduce any run and any failure on a laptop
(``contracts/pipeline-run-interface.md`` §1).

::

    rules-pipeline <command> [options]

      detect      Acquire the points source, digest mechanical values, compare with the last.
      acquire     Acquire both sources into work/. Never commits anything.
      build       Full run: acquire -> parse -> normalize -> reconcile -> curate -> validate
                  -> build.
      validate    Re-validate the existing curated tree without acquiring anything.
      report      Regenerate reports from the curated tree and the previous published version.
      publish     Publish an approved candidate. Refuses outside the approved CI context.
      withdraw    Mark one published version withdrawn. Manifest-only.
      verify      Re-verify every published version's checksum against its recorded value.

Global options work on either side of the command, because an operator under pressure should
not have to remember which. Exit codes are :mod:`pipeline.exit_codes` and nothing else — CI
branches on them and alerting maps them to severities.

**Commands whose stages land in a later phase return 60 with a diagnostic naming the task that
implements them.** That is an invocation error in the honest sense — the command exists in the
contract, the stage does not exist in this build yet — and it keeps the returned-code set
exactly the contract's own.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from pipeline.acquire.detail_source import (
    acquire_detail,
    apply_detail_source_authority,
    read_detail,
)
from pipeline.acquire.http import AcquisitionError, PoliteClient
from pipeline.acquire.mfm import acquire_mfm
from pipeline.build.bundle_emit import BundleMeta, emit_bundle
from pipeline.build.canonical_json import encode_bundle, write_bundle
from pipeline.build.checksum import BundleChecksum, checksum
from pipeline.build.manifest import ManifestError
from pipeline.config import (
    Channel,
    ConfigError,
    DetailAcquisitionMode,
    PipelineConfig,
    load_config,
    repo_root,
)
from pipeline.curate.assemble import assemble
from pipeline.curate.authored import AuthoredContent, load_authored
from pipeline.curate.carry_forward import apply_carried_forward
from pipeline.curate.prior import PriorSnapshot, load_prior, read_curated_tree
from pipeline.curate.summaries import (
    compute_current_digests,
    digestless_keyword_keys,
    glossary_current_digests,
)
from pipeline.curate.writer import write_tree
from pipeline.detect.digest import DIGEST_STATE_RELATIVE_PATH
from pipeline.detect.digest import compare as compare_digests
from pipeline.detect.digest import load_state as load_detection_state
from pipeline.detect.digest import save_state as save_detection_state
from pipeline.detect.staleness import is_stale
from pipeline.exit_codes import ExitCode
from pipeline.models.authored import SummaryClass
from pipeline.models.curated import CuratedSnapshot
from pipeline.models.findings import CoverageFigure, Finding, Severity, ValidationReport
from pipeline.normalize.mechanic_digest import DigestKeyMissingError, resolve_digest_key
from pipeline.observability.ledger import (
    LEDGER_RELATIVE_PATH,
    RunLedgerEntry,
    Trigger,
    append_entry,
    read_entries,
)
from pipeline.parse.mfm_dom import MfmPage, parse_faction_page
from pipeline.parse.mfm_swap_replay import StructureChanged, replay
from pipeline.publish.gate import (
    AlreadyPublishedError,
    GateOutcome,
    OutsideApprovedContextError,
    RebuildOutcome,
    run_publish,
)
from pipeline.publish.github_api import GitHubReleaseApi
from pipeline.publish.pages import ApprovalRecord
from pipeline.publish.release import ReleaseApi
from pipeline.publish.verify import AssetDownloader, VerifyOutcome, mismatched, unreachable
from pipeline.publish.verify import run_verify as _verify_all_published
from pipeline.publish.withdraw import WithdrawalError, WithdrawOutcome
from pipeline.publish.withdraw import run_withdraw as _withdraw_one
from pipeline.reconcile.conflicts import detect_faction_changes, detect_renames
from pipeline.reconcile.findings import apply_resolutions
from pipeline.reconcile.pricing_confidence import apply_pricing_confidence
from pipeline.report.change_summary import (
    compute_change_summary,
    compute_enrichment_changes,
    render_change_summary,
    tier_findings,
)
from pipeline.report.coverage import render_summary_coverage
from pipeline.report.delta_crosscheck import crosscheck_deltas
from pipeline.report.edition_mismatch import (
    render_edition_mismatch,
    render_unverified_pricing,
)
from pipeline.report.option_regression import OptionRegression, compare, render
from pipeline.report.trends import render_trends
from pipeline.report.validation import (
    build_report,
    report_dir,
    write_reports,
)
from pipeline.schema_validation import validate_bundle
from pipeline.validate.contract_checks import (
    RESTRICTION_VOCABULARY_VERSION,
    SCHEMA_CONTRACT_VERSION,
    check_bundle_primary_keys,
    check_snapshot,
)
from pipeline.validate.coverage import (
    LOADOUT_RATCHETED_KEYS,
    CoverageOutcome,
    check_coverage,
    check_weapon_ability_keywords,
    loadout_coverages,
)
from pipeline.validate.equivalence import EquivalenceSummary, check_equivalence
from pipeline.validate.gates import (
    ClassCheck,
    ClassCoverage,
    check_glossary_orphans,
    check_option_ratchet,
    check_summary_gates,
    check_summary_ratchet,
    class_coverage,
    detachment_rule_keys,
    detachment_rule_summaries,
    faction_rule_keys,
    faction_rule_summaries,
    gate_for,
    glossary_keys,
    glossary_summaries,
    loadout_coverage_figures,
    loadout_ratchet_tolerance_for,
    max_chars_for,
    summary_coverage_figures,
    tolerance_for,
    used_ability_keys,
    used_keyword_keys,
)
from pipeline.validate.ip_scan import scan_bundle
from pipeline.validate.refs import check_authored_references
from pipeline.workspace import workspace

LOGGER: Final = logging.getLogger("pipeline")

PROG: Final = "rules-pipeline"

#: The eight commands, in the contract's order (§1).
COMMANDS: Final[tuple[str, ...]] = (
    "detect",
    "acquire",
    "build",
    "validate",
    "report",
    "publish",
    "withdraw",
    "verify",
)

#: Evidence commands: additive to the contract's §1 surface, and **never on the approval-gate
#: path**. They gather material a human reads before approving a candidate; none of them writes
#: a Release, a manifest, `data/`, or `curation/`, and none returns a verdict any workflow acts
#: on.
#:
#: Held apart from :data:`COMMANDS` rather than appended to it, because
#: `contracts/pipeline-run-interface.md` is **frozen at 1.0.2** and a ninth operational command
#: is a MINOR bump of a cross-repository contract, not something a feature branch may do as a
#: side effect. This mirrors `pipeline/report/catalogue.py`'s own precedent for a code
#: implemented ahead of its contract row; the owed §1 addition is `docs/follow-ups.md` item 11.
EVIDENCE_COMMANDS: Final[tuple[str, ...]] = ("option-regression",)

#: The global options (§1). Accepted before or after the command.
GLOBAL_OPTIONS: Final[frozenset[str]] = frozenset(
    {"--channel", "--config", "--offline", "--fixtures", "--json", "--dry-run"}
)

#: The two `build` options that supply :data:`snapshotMeta.publishedAt`, held apart from the
#: contract's own set for the same reason :data:`EVIDENCE_COMMANDS` is held apart from
#: :data:`COMMANDS`: `pipeline-run-interface.md` is frozen at 1.0.2, and adding an option to a
#: declared command is a MINOR bump of a cross-repository contract. The owed §1 amendment is
#: `docs/follow-ups.md` item 12.
#:
#: What makes implementing ahead defensible here: these options do not *extend* the contract,
#: they make an existing clause reachable. `curated-snapshot-format.md` §6 already requires that
#: `publishedAt` be "an explicit build input rather than 'now'", and `run_build` already took it
#: as one — the operator surface simply never offered a way to pass it, so the documented
#: guarantee was unreachable and FR-033/FR-039 held only within a single UTC day.
PUBLISHED_AT_OPTIONS: Final[frozenset[str]] = frozenset(
    {"--published-at", "--published-at-from-report"}
)

#: The per-command options (§1). A command absent from this map takes globals only.
COMMAND_OPTIONS: Final[Mapping[str, frozenset[str]]] = {
    "detect": frozenset(),
    "acquire": frozenset(),
    "build": frozenset({"--rules-version-id", "--since"}) | PUBLISHED_AT_OPTIONS,
    "validate": frozenset(),
    "report": frozenset(),
    "publish": frozenset({"--commit-sha", "--expect-sha256"}),
    "withdraw": frozenset({"--rules-version-id", "--reason"}),
    "verify": frozenset(),
    "option-regression": frozenset({"--rules-version-id", "--since"}),
}

#: One-line help per command, so ``--help`` states the contract rather than paraphrasing it.
_HELP: Final[Mapping[str, str]] = {
    "detect": "acquire the points source, digest mechanical values, compare with the last digest",
    "acquire": "acquire both sources into work/; never commits anything",
    "build": "full run: acquire, parse, normalize, reconcile, curate, validate, build",
    "validate": "re-validate the existing curated tree without acquiring anything",
    "report": "regenerate reports from the curated tree and the previous published version",
    "publish": "publish an approved candidate; refuses outside the approved CI context",
    "withdraw": "mark one published version withdrawn; manifest only, no rebuild",
    "verify": "re-verify every published version's checksum against its recorded value",
    "option-regression": (
        "EVIDENCE: rebuild the published option tree with this pipeline and diff it, per "
        "choice and per field; writes a report and nothing else"
    ),
}

#: Commands whose stage modules arrive in a later phase, with the task that lands each.
_PENDING_STAGES: Final[Mapping[str, str]] = {
    "acquire": "T108 (the acquire-only entry point)",
}

#: Where a fixture-sourced run writes. A fixture build must never overwrite the real curated
#: tree — `data/` is the machine-written record of a real release, and a synthetic set sitting
#: in it would be indistinguishable from one. The generated bundle is committed under the
#: fixture set so the consuming app's CI can use it (FR-048).
FIXTURE_BUILD_DIR: Final = "build"

#: The edition the pipeline curates, and its display name. Not configuration: an edition change
#: is a curation exercise across `curation/`, not a variable flip.
EDITION_CODE: Final = "wh40k-11e"
EDITION_NAME: Final = "Warhammer 40,000 11th Edition"


class InvocationError(ValueError):
    """A malformed invocation. Mapped to exit 60 rather than argparse's own exit 2."""


class _Parser(argparse.ArgumentParser):
    """An ``ArgumentParser`` that raises instead of calling ``sys.exit(2)``.

    The contract assigns invocation errors exit ``60``; argparse's default of ``2`` is outside
    the stable set, and a code CI does not recognise is worse than a wrong one.
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        raise InvocationError(message)


def _add_global_options(parser: argparse.ArgumentParser, *, suppress: bool) -> None:
    """Add the global options to ``parser``.

    ``suppress`` sets ``default=SUPPRESS`` on the sub-parser copies, so a global given before
    the command is not silently overwritten by the sub-parser's default.
    """
    default = argparse.SUPPRESS if suppress else None
    store_default = argparse.SUPPRESS if suppress else False
    parser.add_argument(
        "--channel",
        choices=[c.value for c in Channel],
        default=argparse.SUPPRESS if suppress else None,
        help="delivery channel (default: prerelease, or WGC_DATA_CHANNEL)",
    )
    parser.add_argument("--config", default=default, help="path to a JSON config file")
    parser.add_argument(
        "--offline",
        action="store_true",
        default=store_default,
        help="fail rather than make any network request",
    )
    parser.add_argument(
        "--fixtures", default=default, help="source both upstreams from a synthetic fixture tree"
    )
    parser.add_argument(
        "--json", action="store_true", default=store_default, help="machine-readable output"
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=store_default, help="make no lasting change"
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser — the machine-readable form of contract §1."""
    parser = _Parser(prog=PROG, description=__doc__, add_help=True)
    _add_global_options(parser, suppress=False)

    globals_parent = _Parser(add_help=False)
    _add_global_options(globals_parent, suppress=True)

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    for name in (*COMMANDS, *EVIDENCE_COMMANDS):
        sub = subparsers.add_parser(name, help=_HELP[name], parents=[globals_parent], add_help=True)
        if name == "build":
            sub.add_argument("--rules-version-id", help="the id this candidate will carry")
            sub.add_argument("--since", help="the previous rulesVersionId to compare against")
            sub.add_argument(
                "--published-at",
                help=(
                    "the publication date to stamp, YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ "
                    "(default: today, which is correct only for a first build)"
                ),
            )
            sub.add_argument(
                "--published-at-from-report",
                action="store_true",
                default=False,
                help=(
                    "take the publication date from this checkout's own "
                    "reports/<id>/report.json; what a rebuild of an approved candidate uses"
                ),
            )
        elif name == "publish":
            sub.add_argument("--commit-sha", help="the approved candidate commit")
            sub.add_argument("--expect-sha256", help="the approved bundle checksum")
        elif name == "withdraw":
            sub.add_argument("--rules-version-id", help="the version to withdraw")
            sub.add_argument("--reason", help="short factual reason")
        elif name == "option-regression":
            sub.add_argument("--rules-version-id", help="the id this evidence run reports under")
            sub.add_argument("--since", help="the published rulesVersionId being compared against")
    return parser


def _pending(command: str) -> int:
    """Report a command whose stage module has not landed yet."""
    task = _PENDING_STAGES[command]
    print(
        f"{PROG}: '{command}' is defined by contracts/pipeline-run-interface.md §1 but its "
        f"stage module is not implemented in this build yet — see {task}.",
        file=sys.stderr,
    )
    return int(ExitCode.CONFIG_ERROR)


@dataclass(frozen=True, slots=True)
class BuildResult:
    """Everything one ``build`` produced, so a caller can assert on it without re-running it."""

    exit_code: ExitCode
    snapshot: CuratedSnapshot
    bundle: dict[str, object]
    payload: bytes
    checksum: BundleChecksum
    findings: tuple[Finding, ...]
    output_root: Path
    bundle_path: Path
    report: ValidationReport
    report_path: Path
    coverage: CoverageOutcome


def _verdict(findings: Sequence[Finding], coverage: CoverageOutcome | None = None) -> ExitCode:
    """``42`` on coverage collapse, ``30`` if anything else blocking stands, ``20``, or ``0``.

    Coverage collapse comes first and gets its own code, because "the source went strange" and
    "a curator has work to do" want different alerts even though neither may publish (§2).

    There is no override flag anywhere in this function or reachable from it. The only ways past
    a blocking finding are to fix the data or to record a dated resolution (FR-029, SC-005).

    Which is why the collapse is read off ``findings`` — the **resolved** set — and not off
    ``CoverageOutcome.collapsed``. That property is computed in
    :func:`pipeline.validate.coverage.check_coverage`, before any resolution exists, so reading
    it here made a dated resolution the one kind of blocking finding a curator could record and
    watch do nothing: the report said `ADVISORY ONLY` with no blocking finding, the publish
    gate's :func:`~pipeline.publish.gate.blocking_finding_codes` agreed, and only this line still
    refused. Suppression is still no override — the digest binds it to one occurrence and it
    lapses the moment either figure moves.
    """
    collapse_codes = {finding.finding_code for finding in coverage.findings} if coverage else set()
    if any(
        finding.finding_code in collapse_codes and not finding.is_suppressed for finding in findings
    ):
        return ExitCode.COVERAGE_COLLAPSE
    if any(
        finding.severity is Severity.BLOCKING and not finding.is_suppressed for finding in findings
    ):
        return ExitCode.BLOCKING
    return ExitCode.ADVISORY_ONLY if findings else ExitCode.SUCCESS


#: Every authored summary class is now wired into a run. A class with no curation tree yet simply
#: contributes an empty numerator against its own denominator and an advisory backlog, which is
#: the correct state for a campaign that has not started rather than a special case in the code.
WIRED_SUMMARY_CLASSES: Final[tuple[SummaryClass, ...]] = tuple(SummaryClass)


def _summary_class_checks(
    snapshot: CuratedSnapshot,
    *,
    config: PipelineConfig,
    authored: AuthoredContent,
    ability_current_digests: Mapping[str, str] | None,
    digest_key: bytes | None = None,
) -> list[ClassCheck]:
    """One :class:`ClassCheck` per wired class, each carrying only its own class's state.

    `authored` rather than the snapshot supplies the records for every class, deliberately: a
    snapshot reconstructed from `data/` alone — a bare `validate` re-run — never carries authored
    content, because authored content is never written to the curated tree (FR-017). Reading it
    from one place is what stops `build` and `validate` disagreeing about a faction's coverage.

    Faction and detachment rules pass `current_digests=None` for now: the digest join for those
    classes arrives with its own source in Phase 9, and passing `None` means an approved summary
    is trusted as-is rather than flipped without evidence — exactly what a run with no source
    text already does for abilities. The glossary is the exception, and not because it has a
    source: it has none at all, so **every** entry is stem-digested under contract §5.1 and
    `digest_key` is all it needs.
    """
    return [
        ClassCheck(
            summary_class=SummaryClass.ABILITIES,
            keys=sorted(used_ability_keys(snapshot)),
            authored=authored.ability_summaries,
            current_digests=ability_current_digests,
            gate=gate_for(SummaryClass.ABILITIES, config),
            max_chars=max_chars_for(SummaryClass.ABILITIES, config),
        ),
        ClassCheck(
            summary_class=SummaryClass.FACTION_RULES,
            keys=faction_rule_keys(snapshot, authored.faction_rule_files),
            authored=faction_rule_summaries(snapshot, authored.faction_rule_files),
            current_digests=None,
            gate=gate_for(SummaryClass.FACTION_RULES, config),
            max_chars=max_chars_for(SummaryClass.FACTION_RULES, config),
        ),
        ClassCheck(
            summary_class=SummaryClass.DETACHMENT_RULES,
            # The denominator comes off the snapshot's detachments — the SOURCE — while the
            # records come from `authored`. Reading both from the authored file would let a
            # campaign nobody had started report 100% coverage.
            keys=detachment_rule_keys(snapshot),
            authored=detachment_rule_summaries(snapshot, authored.detachment_rule_summaries),
            current_digests=None,
            gate=gate_for(SummaryClass.DETACHMENT_RULES, config),
            max_chars=max_chars_for(SummaryClass.DETACHMENT_RULES, config),
        ),
        ClassCheck(
            summary_class=SummaryClass.GLOSSARY,
            keys=glossary_keys(snapshot),
            authored=glossary_summaries(snapshot, authored.glossary_entries),
            # Every keyword in use is stem-digested this run, because no keyword glossary source
            # exists to describe any of them yet (contract §5.1). That is stable by construction,
            # so an approved entry whose curator stored the same stem digest carries forward
            # forever and NEVER auto-flags — the limitation is real, is recorded, and its
            # compensating controls are `GLS-ORPHANED` and the manual sweep of the digest-less
            # subset that `summary-coverage.md` enumerates.
            current_digests=(
                glossary_current_digests(used_keyword_keys(snapshot), key=digest_key)
                if digest_key is not None
                else None
            ),
            gate=gate_for(SummaryClass.GLOSSARY, config),
            max_chars=max_chars_for(SummaryClass.GLOSSARY, config),
        ),
    ]


def _summary_findings_and_coverage(
    checks: Sequence[ClassCheck], *, prior: PriorSnapshot | None, config: PipelineConfig
) -> tuple[list[Finding], list[ClassCoverage], dict[str, CoverageFigure]]:
    """Every class's gate findings, its coverage, and the ratchet against the last release.

    The ratchet runs **whether or not a class's gate is on** (contract §4). That is what makes
    the gates-off first release safe: a campaign that has reached 40% cannot quietly fall back to
    30% just because nothing is blocking on it yet.
    """
    coverages = [class_coverage(check) for check in checks]
    previous_approved = {
        summary_class: count
        for summary_class in SummaryClass
        if (count := (prior.summary_approved_count.get(summary_class.value) if prior else None))
        is not None
    }
    previous_percent = {
        summary_class: percent
        for summary_class in SummaryClass
        if (percent := (prior.summary_ratio_percent.get(summary_class.value) if prior else None))
        is not None
    }
    tolerances = {
        summary_class: tolerance_for(summary_class, config) for summary_class in SummaryClass
    }

    findings = check_summary_gates(checks)
    findings.extend(
        check_summary_ratchet(coverages, previous_percent=previous_percent, tolerances=tolerances)
    )
    figures = summary_coverage_figures(
        coverages,
        previous_approved=previous_approved,
        previous_percent=previous_percent,
        tolerances=tolerances,
    )
    return findings, coverages, figures


def _loadout_findings_and_coverage(
    snapshot: CuratedSnapshot,
    *,
    prior: PriorSnapshot | None,
    config: PipelineConfig,
    equivalence: EquivalenceSummary | None = None,
) -> tuple[list[Finding], dict[str, CoverageFigure]]:
    """`006`'s two report rows plus `007`'s two new ones, and the ratchet over both guarded
    figures (`006` FR-022, `008` FR-021).

    Beside :func:`_summary_findings_and_coverage` and not inside it, because the two answer
    different questions. That one measures an editorial backlog a curator works through; this
    one measures how much of the source the *pipeline* resolved, which no amount of curation
    moves. Folding them together would produce one figure that means two things.

    ``equivalence`` is `None` on every call site that has no source text in scope (`run_validate`,
    or a `run_build` with the check disabled) — read by `loadout_coverages` as "not measured this
    run," which omits the figure rather than reporting a false 100% (007 T001, T053).

    Iterates :data:`~pipeline.validate.coverage.LOADOUT_RATCHETED_KEYS` rather than naming
    ``OPTIONS_RESOLVED_KEY`` (008 T060): `default_equipment` joined the ratcheted set on the
    2026-08-15 two-step ruling, and each figure carries its own tolerance
    (:func:`~pipeline.validate.gates.loadout_ratchet_tolerance_for`) so a campaign can configure
    the two ratchets independently.
    """
    coverages = loadout_coverages(snapshot, equivalence=equivalence)
    previous_percent = prior.loadout_ratio_percent if prior else {}
    previous_count = prior.loadout_resolved_count if prior else {}
    tolerances = {key: loadout_ratchet_tolerance_for(key, config) for key in LOADOUT_RATCHETED_KEYS}

    findings: list[Finding] = []
    for key in LOADOUT_RATCHETED_KEYS:
        findings.extend(
            check_option_ratchet(
                coverages[key],
                previous_percent=previous_percent.get(key),
                tolerance=tolerances[key],
            )
        )
    figures = loadout_coverage_figures(
        coverages,
        previous_count=previous_count,
        previous_percent=previous_percent,
        tolerances=tolerances,
    )
    return findings, figures


def _reconcile_against_prior(
    snapshot: CuratedSnapshot,
    *,
    prior: PriorSnapshot | None,
    pages: Sequence[MfmPage],
    datasheet_ids: Mapping[tuple[str, str], str],
    rules_version_id: str,
    config: PipelineConfig,
    authored: AuthoredContent,
    ability_current_digests: Mapping[str, str] | None,
    digest_key: bytes | None,
    previous_tree: CuratedSnapshot | None = None,
    equivalence: EquivalenceSummary | None = None,
) -> tuple[CuratedSnapshot, list[Finding], CoverageOutcome, dict[str, str]]:
    """Everything US2 adds that needs a baseline, in one place.

    Ordered so each step sees the finished state of the last: pricing confidence is resolved
    before the change summary, because a confidence transition *is* one of the changes the
    summary has to account for.
    """
    resolved, findings = apply_pricing_confidence(
        snapshot.datasheets,
        prior_confidence={
            datasheet_id: entry.pricing_confidence
            for datasheet_id, entry in (prior.datasheets.items() if prior else {}.items())
        },
        rules_version_id=rules_version_id,
        escalate_after=config.unverified_escalate_releases,
    )
    snapshot = snapshot.model_copy(update={"datasheets": resolved})

    findings.extend(detect_renames(prior, snapshot))
    findings.extend(detect_faction_changes(prior, snapshot))

    summary = compute_change_summary(prior, snapshot)
    # The five enrichment categories need the previous **tree**, not `prior`'s cost projection:
    # composition entries, option groups and their prices, and per-binding keyword classes are
    # all things that projection deliberately does not carry (FR-037).
    enrichment_changes = compute_enrichment_changes(previous_tree, snapshot)
    findings.extend(tier_findings(summary))
    findings.extend(crosscheck_deltas(pages, summary, datasheet_ids=datasheet_ids))

    coverage = check_coverage(snapshot, prior, config)
    findings.extend(coverage.findings)
    # Advisory, and outside `coverage.findings` on purpose: anything in there refuses
    # publication with exit 42, and this reading is a plausibility judgement rather than a
    # violated guarantee (issue #4, pipeline/validate/coverage.py).
    findings.extend(check_weapon_ability_keywords(snapshot))

    checks = _summary_class_checks(
        snapshot,
        config=config,
        authored=authored,
        ability_current_digests=ability_current_digests,
        digest_key=digest_key,
    )
    summary_findings, coverages, summary_figures = _summary_findings_and_coverage(
        checks, prior=prior, config=config
    )
    findings.extend(summary_findings)
    # Advisory, and it belongs beside the gate findings rather than inside them: an orphan is
    # a definition nobody looks up, which is editorial debt rather than a defect in this
    # candidate. It is also one of the two compensating controls for the glossary's digest
    # limitation, since a stem-digested entry can never flag for re-review on its own
    # (contract §3.1, §5.1).
    findings.extend(check_glossary_orphans(snapshot, authored.glossary_entries))
    coverage.figures.update(summary_figures)

    # 006 FR-022. Kept OUT of `coverage.findings`, whose non-emptiness is what exits 42 for a
    # source collapse: a resolved-option regression is a defect in this pipeline, not evidence
    # that the source went strange, and conflating the two would make CI alert on the wrong
    # thing. It is a blocking finding like any other, refused through the normal verdict.
    loadout_findings, loadout_figures = _loadout_findings_and_coverage(
        snapshot, prior=prior, config=config, equivalence=equivalence
    )
    findings.extend(loadout_findings)
    coverage.figures.update(loadout_figures)

    sub_reports = {
        "change_summary": render_change_summary(summary, enrichment_changes),
        "edition_mismatch": render_edition_mismatch(snapshot),
        "unverified_pricing": render_unverified_pricing(snapshot),
        "summary_coverage": render_summary_coverage(
            snapshot,
            authored_summaries=authored.ability_summaries,
            current_digests=ability_current_digests,
            class_coverages=coverages,
            # Every keyword in use, because no keyword glossary source exists at all yet: the
            # whole vocabulary is stem-digested and the whole vocabulary therefore needs the
            # manual sweep (contract §5.1, §7 item 4).
            digestless_keywords=digestless_keyword_keys(used_keyword_keys(snapshot)),
        ),
    }
    return snapshot, findings, coverage, sub_reports


def run_build(  # noqa: PLR0913 - the stage boundary is the argument list
    *,
    config: PipelineConfig,
    rules_version_id: str,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    output_root: Path | None = None,
    repository_root: Path | None = None,
    curation_dir: Path | None = None,
    published_at: str | None = None,
    source_note: str | None = None,
    prior_dir: Path | None = None,
    reports_root: Path | None = None,
    run_id: str | None = None,
) -> BuildResult:
    """The full run: acquire, parse, normalize, reconcile, curate, validate, build.

    Ordered exactly as ``contracts/pipeline-run-interface.md`` §1 states, and the ordering is
    load bearing rather than tidy: ``normalize`` is the last stage that may read the publisher's
    prose fields, so everything after it is structurally incapable of leaking any (research D8).

    ``published_at`` is an **input**, never ``now``. That single decision is what makes the
    bundle byte-reproducible and therefore what makes the manifest checksum and the approval
    assertion mean anything (FR-033, FR-039).

    The operator surface for it is ``build --published-at`` and ``build
    --published-at-from-report`` (see :func:`_resolve_published_at`). The fallback below — the
    build's own UTC day — is correct for exactly one caller, ``candidate.yml``: for a *fresh*
    candidate the build day is the publication date. It is wrong for every rebuild, and until
    those two options existed it was the only reachable behaviour, so an approval that crossed
    00:00Z could not be published at all (exit 51 on an otherwise identical bundle).
    """
    root = repository_root or repo_root()
    # The baseline is read from a checkout, never re-acquired: the previous curated tree is
    # committed and the previously published version id is in the channel manifest beside it
    # (FR-032, FR-035, spec Support implications). A fixture set carries its own `previous/`.
    baseline_root = prior_dir or (
        fixtures_dir / "previous"
        if fixtures_dir is not None and (fixtures_dir / "previous").is_dir()
        else root
    )
    # A fixture set brings its own authored tree. It has to: the repository's `curation/` maps
    # the publisher's real faction slugs, and a synthetic set's invented slugs would every one
    # of them be the blocking `REC-FACTION-UNMAPPED`. The set is self-contained, which is also
    # what lets it be reviewed as one thing.
    authored_dir = curation_dir or (
        fixtures_dir / "curation"
        if fixtures_dir is not None and (fixtures_dir / "curation").is_dir()
        else root / "curation"
    )

    # Loaded before acquisition, not after (008 FR-024): the html detail arm needs the declared
    # carry-forward slug set *before* it decides which faction pages to attempt, so a curator's
    # declaration in curation/carried-forward-factions.json has to be in hand first. Neither
    # `load_authored` nor a curation-dir read touches the network, so moving it earlier costs
    # nothing and changes no other stage's inputs.
    authored = load_authored(authored_dir)

    with workspace(root) as work:
        points_acq, points_payloads = acquire_mfm(
            config, fixtures_dir=fixtures_dir, offline=offline
        )
        # The mode selector, and the only place in a run that it is consulted: below this line
        # nothing can tell whether the detail source was the bulk export or the current-edition
        # datacard pages, because what it receives is the same shape either way (research D1d).
        detail_acq, detail_payloads = acquire_detail(
            config,
            fixtures_dir=fixtures_dir,
            offline=offline,
            workspace=work,
            carried_forward_slugs=authored.carried_forward_slugs,
        )

        pages = [
            parse_faction_page(payload.name, replay(payload.text).html)
            for payload in points_payloads
        ]
        detail = read_detail(config, detail_payloads)
        # 009 T048, FR-010 (Product Owner decision T047, 2026-08-18: hybrid now, full later): a
        # no-op unless `curation/detail-source-authority.json` carries records — see the
        # function's own docstring for why that is what keeps a full migration and a hybrid the
        # same code path here.
        detail = apply_detail_source_authority(
            detail,
            authority=authored.detail_source_authority,
            config=config,
            fixtures_dir=fixtures_dir,
            offline=offline,
            workspace=work,
            carried_forward_slugs=authored.carried_forward_slugs,
        )

        findings: list[Finding] = []
        for result in detail.values():
            findings.extend(result.findings)

        assembly = assemble(
            pages=pages,
            detail=detail,
            authored=authored,
            points_acquisition=points_acq,
            detail_acquisition=detail_acq,
            edition_code=EDITION_CODE,
            edition_name=EDITION_NAME,
        )
        findings.extend(assembly.findings)
        snapshot = assembly.snapshot

        # 007 US5 (FR-019..FR-021). Same reasoning as the mechanic digest just below: the source
        # card's block text is only reachable here, inside this `with workspace()` block, so the
        # equivalence check must be called from here too rather than from either of `validate`'s
        # own call sites (neither has `detail` in scope — `reports/equivalence-availability/
        # 2026-08-13.md`, T001). Advisory and gated: a run with the check disabled leaves
        # `equivalence_summary` `None`, which `loadout_coverages` reads as "not measured this
        # run," never as "everything matched."
        equivalence_summary: EquivalenceSummary | None = None
        if config.equivalence_check_enabled:
            equivalence_findings, equivalence_summary = check_equivalence(
                snapshot, detail, wahapedia_datasheet_ids=assembly.wahapedia_datasheet_ids
            )
            findings.extend(equivalence_findings)

        # The mechanic digest may only be computed while the detail source's text is in hand
        # (research D6: "the digest may only be computed where the text exists"), which is here
        # and only here — `detail` goes out of scope with `work/` at the end of this block. A
        # run with no configured key computes no digests at all rather than failing the build:
        # every summary still gets its non-staleness checks (SUM-MISSING, SUM-UNAPPROVED), and
        # an `approved` summary is trusted as-is for this run, exactly as a bare `validate`
        # re-run (which never has source text either) already must (FR-020, FR-024, C6/R8).
        try:
            resolved_digest_key: bytes | None = resolve_digest_key(config)
        except DigestKeyMissingError:
            resolved_digest_key = None
            ability_current_digests: Mapping[str, str] | None = None
        else:
            assert resolved_digest_key is not None
            ability_current_digests = compute_current_digests(detail, key=resolved_digest_key)

    # Always the **published** manifest, whichever channel this run targets: FR-009 measures a
    # candidate against the last version players actually have, and measuring a pre-release
    # against the previous pre-release would let coverage erode one candidate at a time without
    # any single run crossing a threshold.
    prior = load_prior(baseline_root, edition_code=EDITION_CODE)
    # The same checkout `prior` is projected from, read whole: the five enrichment categories
    # compare structures the cost projection does not carry (FR-037). `None` on a first release.
    previous_tree = read_curated_tree(baseline_root / "data" / EDITION_CODE)

    # 008 FR-024/FR-025 (Product Owner decision 2026-08-17): splice in every declared faction the
    # acquisition layer could not fetch this run, from `previous_tree` — BEFORE reconciliation, so
    # a carried faction's datasheets read as "present, unchanged" to every coverage figure below,
    # structurally rather than via a coverage.py special case. No-op when nothing was declared.
    # Which declared slug landed which way is derived here, from the payloads actually returned —
    # `SourceAcquisition.coverage` carries only counts (it is `Mapping[str, int]`, feeding FR-009's
    # figures), never slugs, so this is the one place that needs the two sets and the one place
    # cheap enough to compute them in. **html mode only**: a csv-mode payload's `name` is a file
    # name (`Datasheets.csv`), never a faction slug, so a declaration would falsely read as
    # "carried" for every entry under any other mode — carry-forward has no meaning where there is
    # no per-faction page to fail in the first place.
    if config.detail_acquisition_mode is DetailAcquisitionMode.HTML:
        fetched_slugs = frozenset(payload.name for payload in detail_payloads)
        carried_slugs = authored.carried_forward_slugs - fetched_slugs
        unused_slugs = authored.carried_forward_slugs & fetched_slugs
    else:
        carried_slugs = frozenset()
        unused_slugs = frozenset()
    snapshot, carry_forward_findings = apply_carried_forward(
        snapshot,
        previous_tree=previous_tree,
        carried_slugs=carried_slugs,
        unused_declaration_slugs=unused_slugs,
        previous_version_id=(prior.rules_version_id if prior else None) or "(none)",
    )
    findings.extend(carry_forward_findings)

    snapshot, prior_findings, coverage, sub_reports = _reconcile_against_prior(
        snapshot,
        prior=prior,
        pages=pages,
        datasheet_ids=assembly.datasheet_ids,
        rules_version_id=rules_version_id,
        config=config,
        authored=authored,
        ability_current_digests=ability_current_digests,
        digest_key=resolved_digest_key,
        previous_tree=previous_tree,
        equivalence=equivalence_summary,
    )
    findings.extend(prior_findings)

    destination = output_root or (
        fixtures_dir / FIXTURE_BUILD_DIR if fixtures_dir is not None else root
    )
    data_dir = destination / "data" / EDITION_CODE
    write_tree(snapshot, data_dir=data_dir, curation_dir=authored_dir)

    meta = BundleMeta(
        rules_version_id=rules_version_id,
        published_at=published_at or f"{datetime.now(UTC).date().isoformat()}T00:00:00Z",
        source_note=source_note or f"Rules data {rules_version_id}",
        schema_contract_version=SCHEMA_CONTRACT_VERSION,
        restriction_vocabulary_version=RESTRICTION_VOCABULARY_VERSION,
    )

    findings.extend(check_snapshot(snapshot, meta))
    findings.extend(check_authored_references(snapshot, authored))

    bundle = emit_bundle(snapshot, meta)
    validate_bundle(bundle, source=f"rules-{rules_version_id}.json")
    findings.extend(scan_bundle(bundle))
    findings.extend(check_bundle_primary_keys(bundle))

    payload = encode_bundle(bundle)
    bundle_path = destination / f"rules-{rules_version_id}.json"
    write_bundle(bundle_path, bundle)

    # Resolutions are applied last, over the whole finding set, so a curator's dated explanation
    # covers a finding whichever stage raised it (FR-034).
    resolved_findings = apply_resolutions(findings, authored.resolutions)

    report = build_report(
        run_id=run_id or f"local-{rules_version_id}",
        rules_version_id=rules_version_id,
        channel=config.data_channel.value,
        generated_at=meta.published_at,
        acquisitions=[points_acq, detail_acq],
        coverage=coverage.figures,
        snapshot=snapshot,
        findings=resolved_findings,
    )
    # `trends` (task T149) reads the ledger this same repository root already carries — never a
    # fixture's own root, since the trend is a property of the real run history, not of one
    # synthetic set.
    sub_reports = {
        **sub_reports,
        "trends": render_trends(read_entries(root / LEDGER_RELATIVE_PATH)),
    }
    # A fixture run's reports land beside its build output, never in the repository's own
    # `reports/`, which holds the retained report of a real published version (§1).
    report_path = write_reports(
        report,
        directory=report_dir(reports_root or destination, rules_version_id),
        sub_reports=sub_reports,
    )

    return BuildResult(
        exit_code=_verdict(resolved_findings, coverage),
        snapshot=snapshot,
        bundle=bundle,
        payload=payload,
        checksum=checksum(payload),
        findings=tuple(resolved_findings),
        output_root=destination,
        bundle_path=bundle_path,
        report=report,
        report_path=report_path,
        coverage=coverage,
    )


def _report_blocking(findings: Sequence[Finding], report_path: Path) -> None:
    """Name every unresolved blocking finding on stdout, then the report path (§1-§2).

    Both are printed on every verdict, not only on a refusal: an approver reading an advisory
    run still needs the path, and a curator reading a blocked one needs the codes without having
    to open a file to find out why the run stopped.
    """
    for finding in findings:
        if finding.severity is Severity.BLOCKING and not finding.is_suppressed:
            print(f"{PROG}: BLOCKING {finding.finding_code} {sorted(finding.entity_refs)}")
    print(f"{PROG}: report {report_path}")


def normalise_published_at(value: str) -> str:
    """``YYYY-MM-DD`` or ``YYYY-MM-DDTHH:MM:SSZ`` -> the stamp the bundle carries.

    Deliberately strict about the zone: `curated-snapshot-format.md` §6 makes `publishedAt` the
    one timestamp in the bundle, and a local-offset instant would make the same moment two
    different strings and therefore two different checksums. Raises :class:`InvocationError`,
    which the CLI maps to exit 60 — the contract's invocation error, not a build failure.
    """
    text = value.strip()
    try:
        if len(text) == len("YYYY-MM-DD"):
            return f"{datetime.strptime(text, '%Y-%m-%d').date().isoformat()}T00:00:00Z"
        parsed = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as error:
        raise InvocationError(
            f"--published-at must be YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ, got {value!r}"
        ) from error
    return f"{parsed.date().isoformat()}T{parsed.time().isoformat()}Z"


def recorded_published_at(output_root: Path, rules_version_id: str) -> str:
    """The publication date this checkout already recorded for ``rules_version_id``.

    `run_build` writes `generated_at` into `reports/<id>/report.json` **from**
    `snapshotMeta.publishedAt`, and `candidate.yml` commits `reports/` alongside `data/`. So the
    approved commit carries its own published date, and a rebuild of that commit can recover it
    without anybody re-typing it at dispatch time. That is the point: `publish.yml` checks out
    the approved commit and asserts the rebuild reproduces the approved bytes (FR-039), so the
    date must be a property of the approval, not an input to the run that verifies it.

    Refuses loudly when the record is absent or unusable. A fallback to the clock here would
    reinstate the exact defect — a wrong date nobody notices until exit 51.
    """
    path = report_dir(output_root, rules_version_id) / "report.json"
    if not path.is_file():
        raise InvocationError(
            f"--published-at-from-report found no recorded report at {path}; a rebuild can only "
            "recover the approved publication date from the commit that recorded it"
        )
    try:
        recorded = json.loads(path.read_bytes().decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        raise InvocationError(f"{path} is not readable JSON: {error}") from error
    value = recorded.get("generated_at") if isinstance(recorded, dict) else None
    if not isinstance(value, str) or not value:
        raise InvocationError(f"{path} records no 'generated_at' to publish under")
    return normalise_published_at(value)


def _resolve_published_at(args: argparse.Namespace, rules_version_id: str) -> str | None:
    """Which date this build stamps, or ``None`` for "today" (a first build's own day).

    Resolved here rather than inside :func:`run_build` so a bad invocation is refused **before**
    an acquisition sweep: on the real sources that sweep is the expensive part of the run, and an
    invocation error found at the end of it is an invocation error found too late.
    """
    explicit = getattr(args, "published_at", None)
    from_report = bool(getattr(args, "published_at_from_report", False))
    if explicit and from_report:
        raise InvocationError(
            "--published-at and --published-at-from-report both name the publication date; give one"
        )
    if explicit is not None:
        return normalise_published_at(explicit)
    if not from_report:
        return None
    fixtures = getattr(args, "fixtures", None)
    # The same destination `run_build` will write to, so the record read is the record written.
    output_root = Path(fixtures) / FIXTURE_BUILD_DIR if fixtures else repo_root()
    return recorded_published_at(output_root, rules_version_id)


def _run_build_command(config: PipelineConfig, args: argparse.Namespace) -> int:
    rules_version_id = getattr(args, "rules_version_id", None)
    if not rules_version_id:
        print(f"{PROG}: build requires --rules-version-id", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    published_at = _resolve_published_at(args, rules_version_id)
    if published_at is not None:
        print(f"{PROG}: publishedAt {published_at}")

    fixtures = getattr(args, "fixtures", None)
    result = run_build(
        config=config,
        rules_version_id=rules_version_id,
        fixtures_dir=Path(fixtures) if fixtures else None,
        offline=bool(getattr(args, "offline", False)),
        published_at=published_at,
    )

    _report_blocking(result.findings, result.report_path)
    print(f"{PROG}: bundle {result.bundle_path} sha256 {result.checksum.sha256}")
    return int(result.exit_code)


def run_validate(
    *,
    config: PipelineConfig,
    rules_version_id: str,
    repository_root: Path | None = None,
    reports_root: Path | None = None,
    write: bool = True,
    run_id: str | None = None,
) -> tuple[ExitCode, ValidationReport, Path | None]:
    """Re-check the existing curated tree, acquiring nothing (contract §1).

    The tree is the canonical state, so everything that can be checked at all can be checked
    from it — which is what lets a curator reproduce a verdict, and lets a support enquiry be
    answered months later, without touching either upstream source.
    """
    root = repository_root or repo_root()
    snapshot = read_curated_tree(root / "data" / EDITION_CODE)
    if snapshot is None:
        print(
            f"{PROG}: no curated tree at {root / 'data' / EDITION_CODE}; run 'build' first",
            file=sys.stderr,
        )
        raise FileNotFoundError(root / "data" / EDITION_CODE)

    authored = load_authored(root / "curation")
    meta = BundleMeta(
        rules_version_id=rules_version_id,
        published_at="1970-01-01T00:00:00Z",
        source_note=f"Rules data {rules_version_id}",
        schema_contract_version=SCHEMA_CONTRACT_VERSION,
        restriction_vocabulary_version=RESTRICTION_VOCABULARY_VERSION,
    )

    bundle = emit_bundle(snapshot, meta)
    findings: list[Finding] = [
        *check_snapshot(snapshot, meta),
        *check_authored_references(snapshot, authored),
        *scan_bundle(bundle),
        *check_bundle_primary_keys(bundle),
    ]

    prior = load_prior(root, edition_code=EDITION_CODE)
    coverage = check_coverage(snapshot, prior, config)
    findings.extend(coverage.findings)
    # Advisory, and outside `coverage.findings` on purpose: anything in there refuses
    # publication with exit 42, and this reading is a plausibility judgement rather than a
    # violated guarantee (issue #4, pipeline/validate/coverage.py).
    findings.extend(check_weapon_ability_keywords(snapshot))

    # No source text is ever re-acquired here (contract §1), so this run has no evidence of
    # digest drift — every class passes `current_digests=None` — and trusts each stored
    # `review_state` as-is. It still catches an entry with no summary at all, or one left in
    # `draft`/`in_review`, and the ratchet still compares against the previous release.
    checks = _summary_class_checks(
        snapshot, config=config, authored=authored, ability_current_digests=None
    )
    summary_findings, coverages, summary_figures = _summary_findings_and_coverage(
        checks, prior=prior, config=config
    )
    findings.extend(summary_findings)
    # Advisory, and it belongs beside the gate findings rather than inside them: an orphan is
    # a definition nobody looks up, which is editorial debt rather than a defect in this
    # candidate. It is also one of the two compensating controls for the glossary's digest
    # limitation, since a stem-digested entry can never flag for re-review on its own
    # (contract §3.1, §5.1).
    findings.extend(check_glossary_orphans(snapshot, authored.glossary_entries))
    coverage.figures.update(summary_figures)

    # 006 FR-022. Kept OUT of `coverage.findings`, whose non-emptiness is what exits 42 for a
    # source collapse: a resolved-option regression is a defect in this pipeline, not evidence
    # that the source went strange, and conflating the two would make CI alert on the wrong
    # thing. It is a blocking finding like any other, refused through the normal verdict.
    loadout_findings, loadout_figures = _loadout_findings_and_coverage(
        snapshot, prior=prior, config=config
    )
    findings.extend(loadout_findings)
    coverage.figures.update(loadout_figures)

    summary = compute_change_summary(prior, snapshot)
    # `validate` re-reads the *current* tree, so there is no distinct previous tree here to diff
    # against — the enrichment categories are a build-time comparison and stay empty.
    enrichment_changes = compute_enrichment_changes(None, snapshot)
    resolved = apply_resolutions(findings, authored.resolutions)

    report = build_report(
        run_id=run_id or f"local-{rules_version_id}",
        rules_version_id=rules_version_id,
        channel=config.data_channel.value,
        generated_at=meta.published_at,
        acquisitions=[],
        coverage=coverage.figures,
        snapshot=snapshot,
        findings=resolved,
    )

    directory: Path | None = None
    if write:
        directory = write_reports(
            report,
            directory=report_dir(reports_root or root, rules_version_id),
            sub_reports={
                "change_summary": render_change_summary(summary, enrichment_changes),
                "edition_mismatch": render_edition_mismatch(snapshot),
                "unverified_pricing": render_unverified_pricing(snapshot),
                "summary_coverage": render_summary_coverage(
                    snapshot,
                    authored_summaries=authored.ability_summaries,
                    current_digests=None,
                    class_coverages=coverages,
                ),
                "trends": render_trends(read_entries(root / LEDGER_RELATIVE_PATH)),
            },
        )
    return _verdict(resolved, coverage), report, directory


def _run_validate_command(config: PipelineConfig, args: argparse.Namespace, *, write: bool) -> int:
    rules_version_id = getattr(args, "rules_version_id", None) or "candidate"
    try:
        exit_code, report, directory = run_validate(
            config=config, rules_version_id=rules_version_id, write=write
        )
    except FileNotFoundError:
        return int(ExitCode.CONFIG_ERROR)

    _report_blocking(report.findings, directory or report_dir(repo_root(), rules_version_id))
    return int(exit_code)


class PublishInvocationError(RuntimeError):
    """A `publish` invocation is missing required input, or the working tree is not in the
    state contract §4 requires (no rebuilt bundle, or more than one)."""


def _discover_rebuilt_bundle(root: Path) -> tuple[str, bytes]:
    """Locate the single ``rules-<id>.json`` the preceding ``build`` step just wrote.

    Contract §1 gives ``publish`` only ``--commit-sha`` and ``--expect-sha256`` — the rebuilt
    artifact is *found*, not requested by id, because ``publish.yml``'s "Rebuild the snapshot
    from the approved commit" step has already run ``rules-pipeline build`` against the checked-
    out commit before this command runs (contract §4 steps 1-2). Exactly one such file should
    exist after a clean checkout; more or fewer means the working tree is not in the state this
    command requires, which is a configuration error rather than a checksum mismatch.
    """
    candidates = sorted(root.glob("rules-*.json"))
    if len(candidates) == 0:
        raise PublishInvocationError(
            f"no rebuilt bundle at {root}; run 'rules-pipeline build --rules-version-id <id>' "
            "against the approved commit before 'publish' (contract §4 step 2)"
        )
    if len(candidates) > 1:
        names = ", ".join(p.name for p in candidates)
        raise PublishInvocationError(
            f"more than one rebuilt bundle at {root} ({names}); publish cannot tell which one "
            "was approved — clean the working tree and rebuild exactly one"
        )
    path = candidates[0]
    return path.stem.removeprefix("rules-"), path.read_bytes()


def run_publish_command(  # noqa: PLR0913 - the stage boundary is the argument list
    *,
    config: PipelineConfig,
    commit_sha: str,
    expect_sha256: str,
    api: ReleaseApi | None = None,
    repository_root: Path | None = None,
    generated_at: str | None = None,
    approval: ApprovalRecord | None = None,
    require_ci_context: bool = True,
    deploy: bool = True,
) -> GateOutcome:
    """Wire the discovered rebuild, the curated tree, and a ``ReleaseApi`` into the gate.

    Split from :func:`_run_publish_command` so a test can drive the whole sequence with a fake
    ``api`` and a throwaway repository root, without going through argv parsing (task T116).
    """
    root = repository_root or repo_root()
    rules_version_id, payload = _discover_rebuilt_bundle(root)

    def _rebuild() -> RebuildOutcome:
        snapshot = read_curated_tree(root / "data" / EDITION_CODE)
        if snapshot is None:
            raise PublishInvocationError(f"no curated tree at {root / 'data' / EDITION_CODE}")
        # The bundle's own `snapshotMeta.publishedAt` is the authoritative build input (FR-033)
        # — never `now()`, and never `run_validate`'s placeholder timestamp for a bare re-check.
        published_at = json.loads(payload)["snapshotMeta"]["publishedAt"]
        _exit_code, report, _directory = run_validate(
            config=config, rules_version_id=rules_version_id, repository_root=root, write=False
        )
        return RebuildOutcome(
            payload=payload,
            findings=report.findings,
            display_name=f"{snapshot.edition.name} {rules_version_id}",
            edition_codes=[snapshot.edition.code],
            published_at=published_at,
        )

    release_api = api or GitHubReleaseApi(
        repository=os.environ.get("GITHUB_REPOSITORY", ""),
        token=os.environ.get("GITHUB_TOKEN", ""),
    )

    return run_publish(
        config=config,
        commit_sha=commit_sha,
        expect_sha256=expect_sha256,
        rules_version_id=rules_version_id,
        rebuild=_rebuild,
        api=release_api,
        site_dir=root / "site",
        state_dir=root / "state",
        generated_at=generated_at or datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        approval=approval,
        require_ci_context=require_ci_context,
        deploy=deploy,
    )


def _approval_from_environment() -> ApprovalRecord | None:
    """The environment deployment's approval record, read from the Actions run context (T117).

    GitHub's own environment-protection review is the real control (contract §4) — a named
    reviewer approved before this job could even start. This function only carries that fact
    forward into the checksum ledger. **Documented limitation, not glossed over**: attributing
    the record to the *specific approver* rather than the run's actor would need a Deployments-
    API call this command does not make; while `docs/repo-settings.md` records a single reviewer
    (`adhoxx`) with `prevent_self_review: false`, the dispatching actor and the approver are the
    same person in practice, so this is accurate today and a limitation to revisit the day a
    second reviewer exists — exactly the posture that file already documents for the environment
    itself.
    """
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return None
    run_id = os.environ.get("GITHUB_RUN_ID")
    actor = os.environ.get("GITHUB_ACTOR")
    if not run_id or not actor:
        return None
    return ApprovalRecord(
        deployment_id=run_id,
        approver=actor,
        approved_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    )


def _run_publish_command(config: PipelineConfig, args: argparse.Namespace) -> int:
    commit_sha = getattr(args, "commit_sha", None)
    expect_sha256 = getattr(args, "expect_sha256", None)
    if not commit_sha or not expect_sha256:
        print(f"{PROG}: publish requires --commit-sha and --expect-sha256", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    # `--dry-run` is the contract's own "make no lasting change" global (§1): it lets a curator
    # reproduce the gate's verdict — the checksum assertion and the re-validation — without the
    # CI-context refusal or an actual Release/Pages write, which is what "no CI-only code path"
    # (§1) has to mean for a job whose only real trigger is the environment-gated workflow.
    dry_run = bool(getattr(args, "dry_run", False))

    try:
        outcome = run_publish_command(
            config=config,
            commit_sha=commit_sha,
            expect_sha256=expect_sha256,
            approval=_approval_from_environment(),
            require_ci_context=not dry_run,
            deploy=not dry_run,
        )
    except (PublishInvocationError, AlreadyPublishedError, OutsideApprovedContextError) as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    if outcome.diagnostic:
        print(f"{PROG}: {outcome.diagnostic}", file=sys.stderr)
    if outcome.result:
        print(
            f"{PROG}: published {outcome.result.file_url} sha256 {outcome.result.checksum.sha256}"
        )
    return int(outcome.exit_code)


def run_withdraw_command(
    *,
    config: PipelineConfig,
    rules_version_id: str,
    reason: str,
    repository_root: Path | None = None,
    generated_at: str | None = None,
    require_ci_context: bool = True,
    deploy: bool = True,
) -> WithdrawOutcome:
    """Wire the CLI's ``--rules-version-id``/``--reason`` into the withdrawal gate.

    Split from :func:`_run_withdraw_command` the same way :func:`run_publish_command` is split
    from its own CLI wrapper (task T116) — so a test drives the whole sequence without argv
    parsing (task T141).
    """
    root = repository_root or repo_root()
    return _withdraw_one(
        config=config,
        rules_version_id=rules_version_id,
        reason=reason,
        site_dir=root / "site",
        generated_at=generated_at or datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        require_ci_context=require_ci_context,
        deploy=deploy,
    )


def _run_withdraw_command(config: PipelineConfig, args: argparse.Namespace) -> int:
    rules_version_id = getattr(args, "rules_version_id", None)
    reason = getattr(args, "reason", None)
    if not rules_version_id or not reason:
        print(f"{PROG}: withdraw requires --rules-version-id and --reason", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    # Mirrors `publish`'s own `--dry-run` (§1): a curator reproduces the gate's verdict without
    # the CI-context refusal or an actual Pages write.
    dry_run = bool(getattr(args, "dry_run", False))

    try:
        outcome = run_withdraw_command(
            config=config,
            rules_version_id=rules_version_id,
            reason=reason,
            require_ci_context=not dry_run,
            deploy=not dry_run,
        )
    except (WithdrawalError, ManifestError, OutsideApprovedContextError) as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    print(f"{PROG}: withdrew {outcome.rules_version_id} ({outcome.manifest_path})")
    return int(outcome.exit_code)


def run_verify_command(
    *,
    api: AssetDownloader | None = None,
    repository_root: Path | None = None,
    ledger_path: Path | None = None,
    run_id: str | None = None,
    trigger: Trigger = Trigger.MANUAL,
    channel: str = "published",
    now: datetime | None = None,
) -> VerifyOutcome:
    """Re-verify every published checksum and append the one ledger entry `verify` contributes.

    Mirrors :func:`run_detect`'s own "append exactly one line, whatever the outcome" shape
    (contract §6) — a quiet integrity sweep and a broken one both have to be distinguishable from
    a sweep that never ran (task T143, task T144).
    """
    root = repository_root or repo_root()
    release_api = api or GitHubReleaseApi(
        repository=os.environ.get("GITHUB_REPOSITORY", ""),
        token=os.environ.get("GITHUB_TOKEN", ""),
    )
    outcome = _verify_all_published(state_dir=root / "state", api=release_api)

    moment = now or datetime.now(UTC)
    entry = RunLedgerEntry(
        run_id=run_id or f"local-verify-{moment.strftime('%Y%m%dT%H%M%SZ')}",
        command="verify",
        trigger=trigger,
        channel=channel,
        started_at=moment.isoformat().replace("+00:00", "Z"),
        coverage={
            "versions_checked": len(outcome.results),
            "mismatched": len(mismatched(outcome.results)),
            "unreachable": len(unreachable(outcome.results)),
        },
        exit_code=int(outcome.exit_code),
    )
    append_entry(ledger_path or (root / LEDGER_RELATIVE_PATH), entry)
    return outcome


def _run_verify_command(config: PipelineConfig, args: argparse.Namespace) -> int:
    del args  # `verify` takes global options only — nothing per-command to read
    outcome = run_verify_command(
        trigger=_trigger_from_environment(), channel=config.data_channel.value
    )
    for result in outcome.results:
        if not result.matched:
            print(
                f"{PROG}: MISMATCH {result.rules_version_id} {result.file_url} "
                f"expected {result.expected_sha256} got {result.actual_sha256 or result.error}",
                file=sys.stderr,
            )
    print(f"{PROG}: verified {len(outcome.results)} version(s)")
    return int(outcome.exit_code)


@dataclass(frozen=True, slots=True)
class DetectResult:
    """Everything one ``detect`` sweep produced (contract §1-§2, research D4b)."""

    exit_code: ExitCode
    changed_factions: tuple[str, ...] = ()
    diagnostic: str | None = None
    stale: bool = False
    ledger_line: str = ""


def _trigger_from_environment() -> Trigger:
    """What started this run, read from the GitHub Actions event context.

    Falls back to :attr:`Trigger.MANUAL` outside CI — a curator's laptop run and an explicit
    ``workflow_dispatch`` are the same kind of trigger from the ledger's point of view.
    """
    if os.environ.get("GITHUB_EVENT_NAME") == "schedule":
        return Trigger.SCHEDULED
    return Trigger.MANUAL


def run_detect(  # noqa: PLR0913 - the stage boundary is the argument list
    *,
    config: PipelineConfig,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    client: PoliteClient | None = None,
    repository_root: Path | None = None,
    retrieved_at: datetime | None = None,
    now: datetime | None = None,
    run_id: str | None = None,
    trigger: Trigger = Trigger.MANUAL,
) -> DetectResult:
    """Sweep the points source, digest its mechanical values, and compare with the last digest.

    ``detect`` never touches the detail source and never writes ``data/`` or a report — its only
    writes are the digest state and one ledger line (contract §1, §3). A structural or
    reachability failure leaves the previously recorded digest untouched, so the previously
    published version stays current (FR-007, FR-008, exit codes 40/41 §2).
    """
    root = repository_root or repo_root()
    state_path = root / DIGEST_STATE_RELATIVE_PATH
    ledger_path = root / LEDGER_RELATIVE_PATH
    prior_state = load_detection_state(state_path)
    moment = now or datetime.now(UTC)
    started_at = moment.isoformat().replace("+00:00", "Z")

    def _finish(
        exit_code: ExitCode,
        *,
        changed: tuple[str, ...] = (),
        diagnostic: str | None = None,
        coverage: Mapping[str, int] | None = None,
    ) -> DetectResult:
        entry = RunLedgerEntry(
            run_id=run_id or f"local-detect-{moment.strftime('%Y%m%dT%H%M%SZ')}",
            command="detect",
            trigger=trigger,
            channel=config.data_channel.value,
            started_at=started_at,
            coverage=coverage or {},
            exit_code=int(exit_code),
        )
        line = append_entry(ledger_path, entry)
        stale = is_stale(
            read_entries(ledger_path), now=moment, staleness_hours=config.detect_staleness_hours
        )
        return DetectResult(
            exit_code=exit_code,
            changed_factions=changed,
            diagnostic=diagnostic,
            stale=stale,
            ledger_line=line,
        )

    try:
        _acquisition, payloads = acquire_mfm(
            config,
            fixtures_dir=fixtures_dir,
            offline=offline,
            client=client,
            retrieved_at=retrieved_at,
        )
    except AcquisitionError as exc:
        diagnostic = f"{exc.finding_code}: {exc}"
        if exc.exit_code is ExitCode.CONFIG_ERROR:
            # An invocation error (e.g. `--offline` with no `--fixtures`), not a detection
            # attempt: the source was never contacted, so there is nothing for the ledger to
            # record -- the same reasoning `run_build`'s missing `--rules-version-id` check
            # already applies before it writes anything.
            return DetectResult(exit_code=exc.exit_code, diagnostic=diagnostic)
        return _finish(exc.exit_code, diagnostic=diagnostic)

    pages: list[MfmPage] = []
    try:
        for payload in payloads:
            replayed = replay(payload.text)
            pages.append(parse_faction_page(payload.name, replayed.html))
    except StructureChanged as exc:
        return _finish(exc.exit_code, diagnostic=f"{exc.finding_code}: {exc}")

    comparison = compare_digests(pages, prior_state)
    save_detection_state(state_path, comparison.new_state)

    exit_code = ExitCode.CHANGE_DETECTED if comparison.changed else ExitCode.SUCCESS
    return _finish(
        exit_code,
        changed=comparison.changed_factions,
        coverage={"faction_pages": len(payloads)},
    )


def _report_detect(result: DetectResult) -> None:
    """Print the detect verdict, the same way :func:`_report_blocking` prints a build one."""
    if result.diagnostic is not None:
        print(f"{PROG}: {result.diagnostic}", file=sys.stderr)
    if result.changed_factions:
        print(f"{PROG}: CHANGE DETECTED {' '.join(result.changed_factions)}")
    elif result.diagnostic is None:
        print(f"{PROG}: no change")
    if result.stale:
        print(
            f"{PROG}: STALE detection - no successful check completed within the configured "
            "staleness window",
            file=sys.stderr,
        )


def _run_detect_command(config: PipelineConfig, args: argparse.Namespace) -> int:
    fixtures = getattr(args, "fixtures", None)
    result = run_detect(
        config=config,
        fixtures_dir=Path(fixtures) if fixtures else None,
        offline=bool(getattr(args, "offline", False)),
        trigger=_trigger_from_environment(),
    )
    _report_detect(result)
    return int(result.exit_code)


def run_option_regression(
    *,
    config: PipelineConfig,
    rules_version_id: str,
    published_version_id: str,
    repository_root: Path | None = None,
    reports_root: Path | None = None,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    write: bool = True,
) -> tuple[OptionRegression, Path | None]:
    """The FR-009 harness, layer 2: one source, two parsers (006 research D5, task T011).

    The published side is the git-tracked ``data/`` tree — the *expected* half of this
    comparison is committed, which is the whole reason a real-corpus proof is possible at all
    when the *input* half never can be. The candidate side is a full run of this pipeline over
    the same source, into a throwaway destination that is deleted before this function returns.

    **This is evidence, not a gate.** It returns a report and no exit code, it writes nothing
    under ``data/``, ``curation/``, or ``state/``, and no workflow branches on it. The blocking
    instrument is ``COV-OPTION-REGRESSION``, which measures a different thing: coverage counts
    resolved rows, so a row that resolves *differently* is still resolved and is precisely what
    coverage cannot see.
    """
    root = repository_root or repo_root()
    published = read_curated_tree(root / "data" / EDITION_CODE)
    if published is None:
        raise FileNotFoundError(root / "data" / EDITION_CODE)

    with tempfile.TemporaryDirectory(prefix="wgc-option-regression-") as scratch:
        # A throwaway destination, and the reason is FR-010's rather than tidiness: a rebuild
        # writing into `data/` would overwrite the machine-written record of a real release with
        # a comparison artifact, and the two would then be indistinguishable.
        candidate = run_build(
            config=config,
            rules_version_id=f"{rules_version_id}-option-regression",
            fixtures_dir=fixtures_dir,
            offline=offline,
            output_root=Path(scratch),
            repository_root=root,
            published_at="1970-01-01T00:00:00Z",
        ).snapshot

    regression = compare(published, candidate, published_version_id=published_version_id)

    destination: Path | None = None
    if write:
        destination = report_dir(reports_root or root, rules_version_id) / "option-regression.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render(regression), encoding="utf-8", newline="\n")
    return regression, destination


def _run_option_regression_command(config: PipelineConfig, args: argparse.Namespace) -> int:
    rules_version_id = getattr(args, "rules_version_id", None)
    if not rules_version_id:
        print(f"{PROG}: option-regression requires --rules-version-id", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    fixtures = getattr(args, "fixtures", None)
    try:
        regression, path = run_option_regression(
            config=config,
            rules_version_id=rules_version_id,
            published_version_id=getattr(args, "since", None) or "the committed curated tree",
            fixtures_dir=Path(fixtures) if fixtures else None,
            offline=bool(getattr(args, "offline", False)),
        )
    except FileNotFoundError as exc:
        print(f"{PROG}: no curated tree at {exc}; run 'build' first", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    print(f"{PROG}: option-regression {path}")
    print(
        f"{PROG}: {regression.identical_choices} choices identical, "
        f"{len(regression.newly_resolved_choices)} newly resolved, "
        f"{len(regression.corrected)} corrected fields"
    )
    if not regression.is_clean:
        # stderr, and deliberately not an exit code: this command gathers evidence and does not
        # hold a verdict. A non-empty Corrected section is for the approver (T048) to act on,
        # and giving it an exit code here would put an evidence tool on the gate path.
        print(
            f"{PROG}: the Corrected section is NOT empty. FR-009 says a row the baseline "
            "resolved must resolve identically, and research D5's production ordering is "
            "supposed to make that structural. Read the report before approving anything.",
            file=sys.stderr,
        )
    return int(ExitCode.SUCCESS)


def dispatch(command: str, config: PipelineConfig, args: argparse.Namespace) -> int:
    """Run one command and return its contract exit code.

    Split out from :func:`main` so the exit-code mapping is testable without process control.
    """
    if command == "build":
        return _run_build_command(config, args)
    if command in {"validate", "report"}:
        return _run_validate_command(config, args, write=True)
    if command == "detect":
        return _run_detect_command(config, args)
    if command == "publish":
        return _run_publish_command(config, args)
    if command == "withdraw":
        return _run_withdraw_command(config, args)
    if command == "verify":
        return _run_verify_command(config, args)
    if command == "option-regression":
        return _run_option_regression_command(config, args)
    del config, args  # consumed by the stage modules as they land
    return _pending(command)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``rules-pipeline`` console script."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    parser = build_parser()

    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
    except InvocationError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    command: str | None = getattr(args, "command", None)
    if command is None:
        parser.print_help(sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    try:
        config = load_config(
            config_path=getattr(args, "config", None),
            channel_override=args.channel,
        )
    except ConfigError as exc:
        print(f"{PROG}: configuration error: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    config.log_resolved(LOGGER)

    try:
        return dispatch(command, config, args)
    except InvocationError as exc:
        # Raised by a command's own argument checking, not by argparse — a malformed
        # `--published-at`, or a `--published-at-from-report` with nothing to read. Same exit
        # code as a parse error, because to an operator it is the same mistake.
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)
    except AcquisitionError as exc:
        print(f"{PROG}: {exc.finding_code}: {exc}", file=sys.stderr)
        return int(exc.exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
