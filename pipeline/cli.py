# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the CLI skeleton (task T029):
# the eight commands, the global options, the per-command options, and the exit-code mapping of
# contracts/pipeline-run-interface.md §1-§2, each command dispatching to its stage module.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wired `rules-pipeline publish` (task T116)
# to pipeline.publish.gate: locate the rebuilt bundle, re-validate, and hand off to the release
# and Pages steps, with the environment deployment's approval record read from the Actions run
# context (task T117, FR-038, FR-039).
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
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from pipeline.acquire.http import AcquisitionError, PoliteClient
from pipeline.acquire.mfm import acquire_mfm
from pipeline.acquire.wahapedia import acquire_wahapedia
from pipeline.build.bundle_emit import BundleMeta, emit_bundle
from pipeline.build.canonical_json import encode_bundle, write_bundle
from pipeline.build.checksum import BundleChecksum, checksum
from pipeline.config import Channel, ConfigError, PipelineConfig, load_config, repo_root
from pipeline.curate.assemble import assemble
from pipeline.curate.authored import AuthoredContent, load_authored
from pipeline.curate.prior import PriorSnapshot, load_prior, read_curated_tree
from pipeline.curate.summaries import compute_current_digests
from pipeline.curate.writer import write_tree
from pipeline.detect.digest import DIGEST_STATE_RELATIVE_PATH
from pipeline.detect.digest import compare as compare_digests
from pipeline.detect.digest import load_state as load_detection_state
from pipeline.detect.digest import save_state as save_detection_state
from pipeline.detect.staleness import is_stale
from pipeline.exit_codes import ExitCode
from pipeline.models.curated import CuratedSnapshot
from pipeline.models.findings import Finding, Severity, ValidationReport
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
from pipeline.parse.wahapedia_csv import read_text as read_csv_text
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
from pipeline.reconcile.conflicts import detect_faction_changes, detect_renames
from pipeline.reconcile.findings import apply_resolutions
from pipeline.reconcile.pricing_confidence import apply_pricing_confidence
from pipeline.report.change_summary import (
    compute_change_summary,
    render_change_summary,
    tier_findings,
)
from pipeline.report.coverage import render_summary_coverage
from pipeline.report.delta_crosscheck import crosscheck_deltas
from pipeline.report.edition_mismatch import (
    render_edition_mismatch,
    render_unverified_pricing,
)
from pipeline.report.validation import (
    build_report,
    report_dir,
    write_reports,
)
from pipeline.schema_validation import validate_bundle
from pipeline.validate.contract_checks import (
    RESTRICTION_VOCABULARY_VERSION,
    SCHEMA_CONTRACT_VERSION,
    check_snapshot,
)
from pipeline.validate.coverage import CoverageOutcome, check_coverage
from pipeline.validate.ip_scan import scan_bundle
from pipeline.validate.refs import check_authored_references
from pipeline.validate.summaries import check_summaries
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

#: The global options (§1). Accepted before or after the command.
GLOBAL_OPTIONS: Final[frozenset[str]] = frozenset(
    {"--channel", "--config", "--offline", "--fixtures", "--json", "--dry-run"}
)

#: The per-command options (§1). A command absent from this map takes globals only.
COMMAND_OPTIONS: Final[Mapping[str, frozenset[str]]] = {
    "detect": frozenset(),
    "acquire": frozenset(),
    "build": frozenset({"--rules-version-id", "--since"}),
    "validate": frozenset(),
    "report": frozenset(),
    "publish": frozenset({"--commit-sha", "--expect-sha256"}),
    "withdraw": frozenset({"--rules-version-id", "--reason"}),
    "verify": frozenset(),
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
}

#: Commands whose stage modules arrive in a later phase, with the task that lands each.
_PENDING_STAGES: Final[Mapping[str, str]] = {
    "acquire": "T108 (the acquire-only entry point)",
    "withdraw": "T141 (pipeline.publish.withdraw)",
    "verify": "T143 (pipeline.publish.verify)",
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
    for name in COMMANDS:
        sub = subparsers.add_parser(name, help=_HELP[name], parents=[globals_parent], add_help=True)
        if name == "build":
            sub.add_argument("--rules-version-id", help="the id this candidate will carry")
            sub.add_argument("--since", help="the previous rulesVersionId to compare against")
        elif name == "publish":
            sub.add_argument("--commit-sha", help="the approved candidate commit")
            sub.add_argument("--expect-sha256", help="the approved bundle checksum")
        elif name == "withdraw":
            sub.add_argument("--rules-version-id", help="the version to withdraw")
            sub.add_argument("--reason", help="short factual reason")
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
    """
    if coverage is not None and coverage.collapsed:
        return ExitCode.COVERAGE_COLLAPSE
    if any(
        finding.severity is Severity.BLOCKING and not finding.is_suppressed for finding in findings
    ):
        return ExitCode.BLOCKING
    return ExitCode.ADVISORY_ONLY if findings else ExitCode.SUCCESS


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
    findings.extend(tier_findings(summary))
    findings.extend(crosscheck_deltas(pages, summary, datasheet_ids=datasheet_ids))

    coverage = check_coverage(snapshot, prior, config)
    findings.extend(coverage.findings)

    findings.extend(
        check_summaries(
            snapshot,
            authored_summaries=authored.ability_summaries,
            current_digests=ability_current_digests,
            summary_max_chars=config.summary_max_chars,
        )
    )

    sub_reports = {
        "change_summary": render_change_summary(summary),
        "edition_mismatch": render_edition_mismatch(snapshot),
        "unverified_pricing": render_unverified_pricing(snapshot),
        "summary_coverage": render_summary_coverage(
            snapshot,
            authored_summaries=authored.ability_summaries,
            current_digests=ability_current_digests,
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

    with workspace(root) as work:
        points_acq, points_payloads = acquire_mfm(
            config, fixtures_dir=fixtures_dir, offline=offline
        )
        detail_acq, detail_payloads = acquire_wahapedia(
            config, fixtures_dir=fixtures_dir, offline=offline, workspace=work
        )

        pages = [
            parse_faction_page(payload.name, replay(payload.text).html)
            for payload in points_payloads
        ]
        detail = {
            f"{payload.name}.csv"
            if not payload.name.endswith(".csv")
            else payload.name: read_csv_text(
                payload.name if payload.name.endswith(".csv") else f"{payload.name}.csv",
                payload.text,
            )
            for payload in detail_payloads
        }

        findings: list[Finding] = []
        for result in detail.values():
            findings.extend(result.findings)

        authored = load_authored(authored_dir)

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

        # The mechanic digest may only be computed while the detail source's text is in hand
        # (research D6: "the digest may only be computed where the text exists"), which is here
        # and only here — `detail` goes out of scope with `work/` at the end of this block. A
        # run with no configured key computes no digests at all rather than failing the build:
        # every summary still gets its non-staleness checks (SUM-MISSING, SUM-UNAPPROVED), and
        # an `approved` summary is trusted as-is for this run, exactly as a bare `validate`
        # re-run (which never has source text either) already must (FR-020, FR-024, C6/R8).
        try:
            digest_key = resolve_digest_key(config)
        except DigestKeyMissingError:
            ability_current_digests: Mapping[str, str] | None = None
        else:
            ability_current_digests = compute_current_digests(detail, key=digest_key)

    # Always the **published** manifest, whichever channel this run targets: FR-009 measures a
    # candidate against the last version players actually have, and measuring a pre-release
    # against the previous pre-release would let coverage erode one candidate at a time without
    # any single run crossing a threshold.
    prior = load_prior(baseline_root, edition_code=EDITION_CODE)
    snapshot, prior_findings, coverage, sub_reports = _reconcile_against_prior(
        snapshot,
        prior=prior,
        pages=pages,
        datasheet_ids=assembly.datasheet_ids,
        rules_version_id=rules_version_id,
        config=config,
        authored=authored,
        ability_current_digests=ability_current_digests,
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


def _run_build_command(config: PipelineConfig, args: argparse.Namespace) -> int:
    rules_version_id = getattr(args, "rules_version_id", None)
    if not rules_version_id:
        print(f"{PROG}: build requires --rules-version-id", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)

    fixtures = getattr(args, "fixtures", None)
    result = run_build(
        config=config,
        rules_version_id=rules_version_id,
        fixtures_dir=Path(fixtures) if fixtures else None,
        offline=bool(getattr(args, "offline", False)),
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

    findings: list[Finding] = [
        *check_snapshot(snapshot, meta),
        *check_authored_references(snapshot, authored),
        *scan_bundle(emit_bundle(snapshot, meta)),
        # No source text is ever re-acquired here (contract §1), so this run has no evidence of
        # digest drift — `current_digests=None` — and trusts each stored `review_state` as-is.
        # It still catches a key with no summary at all, or one left in `draft`/`in_review`.
        *check_summaries(
            snapshot,
            authored_summaries=authored.ability_summaries,
            current_digests=None,
            summary_max_chars=config.summary_max_chars,
        ),
    ]

    prior = load_prior(root, edition_code=EDITION_CODE)
    coverage = check_coverage(snapshot, prior, config)
    findings.extend(coverage.findings)

    summary = compute_change_summary(prior, snapshot)
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
                "change_summary": render_change_summary(summary),
                "edition_mismatch": render_edition_mismatch(snapshot),
                "unverified_pricing": render_unverified_pricing(snapshot),
                "summary_coverage": render_summary_coverage(
                    snapshot, authored_summaries=authored.ability_summaries, current_digests=None
                ),
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
    except AcquisitionError as exc:
        print(f"{PROG}: {exc.finding_code}: {exc}", file=sys.stderr)
        return int(exc.exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
