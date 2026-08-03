# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the CLI skeleton (task T029):
# the eight commands, the global options, the per-command options, and the exit-code mapping of
# contracts/pipeline-run-interface.md §1-§2, each command dispatching to its stage module.
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
import logging
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from pipeline.acquire.http import AcquisitionError
from pipeline.acquire.mfm import acquire_mfm
from pipeline.acquire.wahapedia import acquire_wahapedia
from pipeline.build.bundle_emit import BundleMeta, emit_bundle
from pipeline.build.canonical_json import encode_bundle, write_bundle
from pipeline.build.checksum import BundleChecksum, checksum
from pipeline.config import Channel, ConfigError, PipelineConfig, load_config, repo_root
from pipeline.curate.assemble import assemble
from pipeline.curate.authored import load_authored
from pipeline.curate.writer import write_tree
from pipeline.exit_codes import ExitCode
from pipeline.models.curated import CuratedSnapshot
from pipeline.models.findings import Finding, Severity
from pipeline.parse.mfm_dom import parse_faction_page
from pipeline.parse.mfm_swap_replay import replay
from pipeline.parse.wahapedia_csv import read_text as read_csv_text
from pipeline.schema_validation import validate_bundle
from pipeline.validate.contract_checks import (
    RESTRICTION_VOCABULARY_VERSION,
    SCHEMA_CONTRACT_VERSION,
    check_snapshot,
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
    "detect": "T106 (pipeline.detect)",
    "acquire": "T108 (the acquire-only entry point)",
    "validate": "T099 (pipeline.validate re-run without acquiring)",
    "report": "T099 (pipeline.report.validation)",
    "publish": "T117 (the publish job's CLI entry point)",
    "withdraw": "T118 (pipeline.publish.withdraw)",
    "verify": "T124 (pipeline.publish.integrity)",
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


def _verdict(findings: Sequence[Finding]) -> ExitCode:
    """``30`` if anything blocking stands, ``20`` if only advisories remain, ``0`` if none.

    There is no override flag anywhere in this function or reachable from it. The only ways past
    a blocking finding are to fix the data or to record a dated resolution (FR-029, SC-005).
    """
    if any(
        finding.severity is Severity.BLOCKING and not finding.is_suppressed for finding in findings
    ):
        return ExitCode.BLOCKING
    return ExitCode.ADVISORY_ONLY if findings else ExitCode.SUCCESS


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

    return BuildResult(
        exit_code=_verdict(findings),
        snapshot=snapshot,
        bundle=bundle,
        payload=payload,
        checksum=checksum(payload),
        findings=tuple(findings),
        output_root=destination,
        bundle_path=bundle_path,
    )


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

    blocking = [
        f for f in result.findings if f.severity is Severity.BLOCKING and not f.is_suppressed
    ]
    for finding in blocking:
        print(
            f"{PROG}: BLOCKING {finding.finding_code} {sorted(finding.entity_refs)}",
            file=sys.stderr,
        )
    print(f"{PROG}: bundle {result.bundle_path} sha256 {result.checksum.sha256}")
    return int(result.exit_code)


def dispatch(command: str, config: PipelineConfig, args: argparse.Namespace) -> int:
    """Run one command and return its contract exit code.

    Split out from :func:`main` so the exit-code mapping is testable without process control.
    """
    if command == "build":
        return _run_build_command(config, args)
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
