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
from typing import Final

from pipeline.acquire.http import AcquisitionError
from pipeline.config import Channel, ConfigError, PipelineConfig, load_config
from pipeline.exit_codes import ExitCode

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
    "acquire": "T055/T056 (pipeline.acquire.mfm, pipeline.acquire.wahapedia)",
    "build": "T073 (the wired build pipeline)",
    "validate": "T099 (pipeline.validate)",
    "report": "T099 (pipeline.report.validation)",
    "publish": "T071 (pipeline.publish.release)",
    "withdraw": "T118 (pipeline.publish.withdraw)",
    "verify": "T124 (pipeline.publish.integrity)",
}


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


def dispatch(command: str, config: PipelineConfig, args: argparse.Namespace) -> int:
    """Run one command and return its contract exit code.

    Split out from :func:`main` so the exit-code mapping is testable without process control.
    """
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
