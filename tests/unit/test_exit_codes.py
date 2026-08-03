# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the exit-code values never drift
# (task T017), because CI branches on them and alerting maps them to severities
# (contracts/pipeline-run-interface.md §2).
"""The exit codes are an interface. This test is the thing that stops them moving."""

from __future__ import annotations

from pipeline.exit_codes import STABLE_EXIT_CODES, ExitCode

#: Transcribed from contracts/pipeline-run-interface.md §2. If a change to `pipeline.exit_codes`
#: makes this fail, the contract is what has to change first.
CONTRACT_CODES = {
    "SUCCESS": 0,
    "CHANGE_DETECTED": 10,
    "ADVISORY_ONLY": 20,
    "BLOCKING": 30,
    "SOURCE_UNAVAILABLE": 40,
    "SOURCE_STRUCTURE_CHANGED": 41,
    "COVERAGE_COLLAPSE": 42,
    "NONDETERMINISTIC": 50,
    "APPROVAL_MISMATCH": 51,
    "CONFIG_ERROR": 60,
}


def test_every_contract_code_has_its_exact_value() -> None:
    for name, value in CONTRACT_CODES.items():
        assert ExitCode[name].value == value, f"{name} drifted from the contract"


def test_no_code_exists_outside_the_contract() -> None:
    assert {code.name for code in ExitCode} == set(CONTRACT_CODES)
    assert frozenset(CONTRACT_CODES.values()) == STABLE_EXIT_CODES


def test_codes_are_ints_so_they_can_be_returned_from_main() -> None:
    for code in ExitCode:
        assert isinstance(code.value, int)
        assert int(code) == code.value


def test_the_five_codes_that_never_touch_a_published_artifact_are_distinct() -> None:
    # Contract §2: "Exit 40, 41, 42, 50, and 51 never touch a published artifact."
    never_publishes = {
        ExitCode.SOURCE_UNAVAILABLE,
        ExitCode.SOURCE_STRUCTURE_CHANGED,
        ExitCode.COVERAGE_COLLAPSE,
        ExitCode.NONDETERMINISTIC,
        ExitCode.APPROVAL_MISMATCH,
    }
    assert len({code.value for code in never_publishes}) == 5
    assert ExitCode.SUCCESS not in never_publishes
