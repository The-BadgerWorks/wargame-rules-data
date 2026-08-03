# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the command set, the option set, and
# the exit-code mapping match contracts/pipeline-run-interface.md §1-§2 exactly (task T030), so
# the operator contract cannot drift silently.
"""The CLI is the operator contract, and an operator contract that drifts is a broken promise.

Every expectation below is transcribed from ``contracts/pipeline-run-interface.md`` §1-§2
rather than read out of the implementation, which is what makes this a contract test instead of
a change detector.
"""

from __future__ import annotations

import argparse

import pytest

from pipeline.cli import COMMAND_OPTIONS, COMMANDS, GLOBAL_OPTIONS, build_parser, main
from pipeline.exit_codes import STABLE_EXIT_CODES, ExitCode

CONTRACT_COMMANDS = {
    "detect",
    "acquire",
    "build",
    "validate",
    "report",
    "publish",
    "withdraw",
    "verify",
}

CONTRACT_GLOBAL_OPTIONS = {
    "--channel",
    "--config",
    "--offline",
    "--fixtures",
    "--json",
    "--dry-run",
}

CONTRACT_COMMAND_OPTIONS = {
    "build": {"--rules-version-id", "--since"},
    "publish": {"--commit-sha", "--expect-sha256"},
    "withdraw": {"--rules-version-id", "--reason"},
}


def _subparsers(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    for action in parser._actions:  # noqa: SLF001 - argparse exposes no public accessor
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            return dict(action.choices)
    raise AssertionError("the parser defines no subcommands")


def _option_strings(parser: argparse.ArgumentParser) -> set[str]:
    options: set[str] = set()
    for action in parser._actions:  # noqa: SLF001
        options.update(s for s in action.option_strings if s.startswith("--"))
    return options - {"--help"}


def test_the_command_set_is_exactly_the_contracts() -> None:
    assert set(COMMANDS) == CONTRACT_COMMANDS
    assert set(_subparsers(build_parser())) == CONTRACT_COMMANDS


def test_the_commands_are_declared_in_the_contracts_order() -> None:
    assert COMMANDS == (
        "detect",
        "acquire",
        "build",
        "validate",
        "report",
        "publish",
        "withdraw",
        "verify",
    )


def test_the_global_option_set_is_exactly_the_contracts() -> None:
    assert set(GLOBAL_OPTIONS) == CONTRACT_GLOBAL_OPTIONS
    assert _option_strings(build_parser()) == CONTRACT_GLOBAL_OPTIONS


@pytest.mark.parametrize("command", sorted(CONTRACT_COMMANDS))
def test_each_command_exposes_the_globals_plus_its_own_options(command: str) -> None:
    sub = _subparsers(build_parser())[command]
    expected = CONTRACT_GLOBAL_OPTIONS | CONTRACT_COMMAND_OPTIONS.get(command, set())
    assert _option_strings(sub) == expected
    assert set(COMMAND_OPTIONS[command]) == CONTRACT_COMMAND_OPTIONS.get(command, set())


def test_globals_are_accepted_on_either_side_of_the_command() -> None:
    parser = build_parser()
    before = parser.parse_args(["--offline", "--channel", "published", "build"])
    after = parser.parse_args(["build", "--offline", "--channel", "published"])
    assert (before.command, before.offline, before.channel) == ("build", True, "published")
    assert (after.command, after.offline, after.channel) == ("build", True, "published")


def test_a_global_given_before_the_command_is_not_clobbered_by_a_subparser_default() -> None:
    parser = build_parser()
    parsed = parser.parse_args(["--fixtures", "fixtures/minimal", "build"])
    assert parsed.fixtures == "fixtures/minimal"


def test_channel_only_accepts_the_two_contract_channels() -> None:
    parser = build_parser()
    assert parser.parse_args(["--channel", "prerelease", "verify"]).channel == "prerelease"
    assert parser.parse_args(["--channel", "published", "verify"]).channel == "published"
    with pytest.raises(ValueError, match="invalid choice"):
        parser.parse_args(["--channel", "staging", "verify"])


def test_build_options_parse() -> None:
    parsed = build_parser().parse_args(
        ["build", "--rules-version-id", "mfm-2026-06", "--since", "mfm-2026-03"]
    )
    assert parsed.rules_version_id == "mfm-2026-06"
    assert parsed.since == "mfm-2026-03"


def test_publish_and_withdraw_options_parse() -> None:
    published = build_parser().parse_args(
        ["publish", "--commit-sha", "abc123", "--expect-sha256", "0" * 64]
    )
    assert (published.commit_sha, published.expect_sha256) == ("abc123", "0" * 64)

    withdrawn = build_parser().parse_args(
        ["withdraw", "--rules-version-id", "mfm-2026-06", "--reason", "mispriced band"]
    )
    assert withdrawn.rules_version_id == "mfm-2026-06"


def test_an_invocation_error_exits_60_not_argparses_own_2() -> None:
    assert main(["build", "--not-an-option"]) == ExitCode.CONFIG_ERROR
    assert main(["not-a-command"]) == ExitCode.CONFIG_ERROR
    assert main([]) == ExitCode.CONFIG_ERROR


def test_a_configuration_error_exits_60(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WGC_REQUEST_INTERVAL_MS", "not-a-number")
    assert main(["verify"]) == ExitCode.CONFIG_ERROR


def test_help_exits_zero() -> None:
    with pytest.raises(SystemExit) as raised:
        main(["--help"])
    assert raised.value.code == 0


@pytest.mark.parametrize("command", sorted(CONTRACT_COMMANDS))
def test_every_command_returns_a_code_from_the_stable_set(command: str) -> None:
    assert main([command]) in STABLE_EXIT_CODES
