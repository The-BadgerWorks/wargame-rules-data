# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 R7c task 1: failing-first tests for the
# CLI transport of the drafting client, so the Owner's subscription pays for a drafting run
# instead of the billed messages API. Every mechanic string in this file is INVENTED -- no
# publisher wording reaches a fixture, a transcript or a log, and the caplog test below is the
# receipt for the last of those.
"""The CLI summary drafting client: argv shape, parsing, batching, retry, and log silence.

Every test here supplies a fake ``runner`` callable recording its arguments and returning a
``subprocess.CompletedProcess``. Not one test invokes the real ``claude`` CLI.
"""

from __future__ import annotations

import json
import logging
import subprocess

import pytest

from pipeline.config import load_config
from pipeline.summaries import CliSummaryClient, Draft, DraftingError, Verdict, prompts

#: Invented stand-ins for an export's rules text. Nothing here came from a publisher.
INVENTED_NAME = "Chitin Bloom"
INVENTED_MECHANIC = (
    "While this model is within 6 inches of a Vault Cadence marker, add 1 to the Strength "
    "characteristic of its melee weapons."
)
INVENTED_SUMMARY = "Melee weapons gain +1 Strength while within 6 inches of a Vault Cadence marker."


def _completed(
    stdout_obj: dict[str, object], *, returncode: int = 0, stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["claude"], returncode=returncode, stdout=json.dumps(stdout_obj), stderr=stderr
    )


def _envelope(payload: dict[str, object]) -> dict[str, object]:
    """One CLI print-mode envelope carrying ``payload`` as both fields the parser tries."""
    return {
        "is_error": False,
        "result": json.dumps(payload),
        "structured_output": payload,
    }


class _FakeRunner:
    """Records every call and returns queued replies in order."""

    def __init__(self, *replies: subprocess.CompletedProcess[str]) -> None:
        self._replies = list(replies)
        self.calls: list[dict[str, object]] = []

    def __call__(self, argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        self.calls.append({"argv": argv, **kwargs})
        return self._replies.pop(0)


def _client(runner: _FakeRunner) -> CliSummaryClient:
    return CliSummaryClient(model="claude-opus-5", runner=runner)


# -- (a) draft builds exactly the documented argv, prompt on stdin -----------------------------


def test_draft_builds_the_exact_argv_and_puts_the_prompt_on_stdin() -> None:
    runner = _FakeRunner(
        _completed(_envelope({"summary": INVENTED_SUMMARY, "used_verbatim": False}))
    )

    drafted = _client(runner).draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    assert drafted == Draft(summary=INVENTED_SUMMARY, used_verbatim=False)
    assert len(runner.calls) == 1
    call = runner.calls[0]
    assert call["argv"] == [
        "claude",
        "-p",
        "--no-session-persistence",
        "--tools",
        "",
        "--model",
        "claude-opus-5",
        "--system-prompt",
        prompts.DRAFT_SYSTEM,
        "--output-format",
        "json",
        "--json-schema",
        json.dumps(prompts.DRAFT_SCHEMA),
    ]
    assert "--bare" not in call["argv"]
    assert INVENTED_MECHANIC in str(call["input"])
    assert call["text"] is True
    assert call["encoding"] == "utf-8"
    assert call["timeout"] == 180
    assert call["capture_output"] is True


# -- (b) review parses a structured_output reply ------------------------------------------------


def test_review_parses_a_structured_output_reply() -> None:
    runner = _FakeRunner(
        _completed(_envelope({"decision": "redraft", "reason_code": "meaning-changed"}))
    )

    verdict = _client(runner).review(INVENTED_NAME, INVENTED_MECHANIC, INVENTED_SUMMARY)

    assert verdict == Verdict(decision="redraft", reason_code="meaning-changed")


# -- (c) review_many: order, shape mismatch, and the 10-item cap -------------------------------


def test_review_many_returns_verdicts_in_order() -> None:
    payload = {
        "verdicts": [
            {"decision": "keep", "reason_code": "ok"},
            {"decision": "redraft", "reason_code": "too-long"},
            {"decision": "lore", "reason_code": "lore-present"},
        ]
    }
    runner = _FakeRunner(_completed(_envelope(payload)))

    verdicts = _client(runner).review_many(
        [
            ("Item One", INVENTED_MECHANIC, INVENTED_SUMMARY),
            ("Item Two", INVENTED_MECHANIC, INVENTED_SUMMARY),
            ("Item Three", INVENTED_MECHANIC, INVENTED_SUMMARY),
        ]
    )

    assert verdicts == [
        Verdict(decision="keep", reason_code="ok"),
        Verdict(decision="redraft", reason_code="too-long"),
        Verdict(decision="lore", reason_code="lore-present"),
    ]


def test_review_many_with_too_few_verdicts_raises_batch_shape_error() -> None:
    payload = {
        "verdicts": [
            {"decision": "keep", "reason_code": "ok"},
            {"decision": "redraft", "reason_code": "too-long"},
        ]
    }
    runner = _FakeRunner(_completed(_envelope(payload)))

    with pytest.raises(DraftingError) as caught:
        _client(runner).review_many(
            [
                ("Item One", INVENTED_MECHANIC, INVENTED_SUMMARY),
                ("Item Two", INVENTED_MECHANIC, INVENTED_SUMMARY),
                ("Item Three", INVENTED_MECHANIC, INVENTED_SUMMARY),
            ]
        )

    assert str(caught.value) == "cli-batch-shape"


def test_review_many_with_more_than_ten_items_raises_batch_shape_error_immediately() -> None:
    runner = _FakeRunner()

    items = [(f"Item {i}", INVENTED_MECHANIC, INVENTED_SUMMARY) for i in range(11)]
    with pytest.raises(DraftingError) as caught:
        _client(runner).review_many(items)

    assert str(caught.value) == "cli-batch-shape"
    assert runner.calls == []


def test_review_many_with_no_items_raises_batch_shape_error() -> None:
    runner = _FakeRunner()

    with pytest.raises(DraftingError) as caught:
        _client(runner).review_many([])

    assert str(caught.value) == "cli-batch-shape"
    assert runner.calls == []


# -- (d) a non-zero returncode raises DraftingError ----------------------------------------------


def test_a_nonzero_returncode_raises_drafting_error() -> None:
    runner = _FakeRunner(_completed({"is_error": True, "result": "not logged in"}, returncode=1))

    with pytest.raises(DraftingError) as caught:
        _client(runner).draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    assert caught.value.status_code == 1


# -- (e) the model id and system prompt are on argv, never on stdin; the mechanic text is the
#        reverse ---------------------------------------------------------------------------------


def test_the_model_and_system_prompt_are_on_argv_never_on_stdin() -> None:
    runner = _FakeRunner(
        _completed(_envelope({"summary": INVENTED_SUMMARY, "used_verbatim": False}))
    )

    _client(runner).draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    call = runner.calls[0]
    argv = call["argv"]
    assert isinstance(argv, list)
    stdin_text = str(call["input"])

    assert INVENTED_MECHANIC in stdin_text
    assert not any(INVENTED_MECHANIC in arg for arg in argv)
    assert prompts.DRAFT_SYSTEM in argv
    assert prompts.DRAFT_SYSTEM not in stdin_text
    assert "claude-opus-5" in argv
    assert "claude-opus-5" not in stdin_text


# -- (f) config: draft_transport defaults to "cli", rejects unknown values -----------------------


def test_load_config_exposes_draft_transport_defaulting_to_cli() -> None:
    config = load_config(env={})
    assert config.draft_transport == "cli"
    assert config.claude_cli == "claude"


def test_load_config_rejects_an_unknown_draft_transport() -> None:
    with pytest.raises(Exception) as caught:
        load_config(env={"WGC_DRAFT_TRANSPORT": "foo"})

    from pipeline.config import ConfigError

    assert isinstance(caught.value, ConfigError)


# -- (g) structured_output-absent reply falls back to json.loads(result) ------------------------


def test_a_reply_without_structured_output_falls_back_to_parsing_result() -> None:
    payload = {"summary": INVENTED_SUMMARY, "used_verbatim": False}
    runner = _FakeRunner(_completed({"is_error": False, "result": json.dumps(payload)}))

    drafted = _client(runner).draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    assert drafted == Draft(summary=INVENTED_SUMMARY, used_verbatim=False)


# -- (h) a rate-limit-shaped failure retries once and then succeeds ------------------------------


def test_a_rate_limit_shaped_failure_retries_once_and_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    slept: list[float] = []
    monkeypatch.setattr("pipeline.summaries.cli_client.time.sleep", slept.append)
    runner = _FakeRunner(
        _completed(
            {"is_error": True, "result": "Rate limit exceeded, try again later"}, returncode=1
        ),
        _completed(_envelope({"summary": INVENTED_SUMMARY, "used_verbatim": False})),
    )

    drafted = _client(runner).draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    assert drafted.summary == INVENTED_SUMMARY
    assert len(runner.calls) == 2, "exactly one retry, not a loop"
    assert slept == [60.0]


def test_a_non_rate_limited_failure_is_not_retried() -> None:
    runner = _FakeRunner(
        _completed({"is_error": True, "result": "something else broke"}, returncode=1)
    )

    with pytest.raises(DraftingError):
        _client(runner).draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    assert len(runner.calls) == 1


# -- (i) no exception message or log record ever carries the mechanic text or reply body --------


def test_no_exception_or_log_record_carries_the_mechanic_text_or_reply_body(
    caplog: pytest.LogCaptureFixture,
) -> None:
    runner = _FakeRunner(
        _completed({"is_error": True, "result": f"leaked body: {INVENTED_MECHANIC}"}, returncode=1)
    )

    with caplog.at_level(logging.DEBUG), pytest.raises(DraftingError) as caught:
        _client(runner).draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    assert INVENTED_MECHANIC not in str(caught.value)
    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert INVENTED_MECHANIC not in logged
    assert INVENTED_NAME not in logged
    assert INVENTED_SUMMARY not in logged
