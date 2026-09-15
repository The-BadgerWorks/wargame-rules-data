# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R7 task 1: failing-first tests for the
# summary drafting client that executes the Owner's amended standing rule 3 (summaries may be
# machine-drafted from the export's rules text, reviewed by a second model, approved by the
# Owner). Every mechanic string in this file is INVENTED -- no publisher wording reaches a
# fixture, a transcript or a log, and the caplog test below is the receipt for the last of those.
"""The summary drafting client: transport, validation, retry, and log silence.

All API traffic is mocked with ``pytest-httpx``; not one test opens a socket. The strings
standing in for rules text are inventions of this file (``Chitin Bloom``, ``Vault Cadence``),
chosen so that an accidental leak into a log or a request dump is unmistakable.
"""

from __future__ import annotations

import json
import logging

import httpx
import pytest
from pytest_httpx import HTTPXMock

from pipeline.config import load_config
from pipeline.summaries import (
    MESSAGES_URL,
    Draft,
    DraftingError,
    SummaryClient,
    Verdict,
    prompts,
)

#: Invented stand-ins for an export's rules text. Nothing here came from a publisher.
INVENTED_NAME = "Chitin Bloom"
INVENTED_MECHANIC = (
    "While this model is within 6 inches of a Vault Cadence marker, add 1 to the Strength "
    "characteristic of its melee weapons."
)
INVENTED_SUMMARY = "Melee weapons gain +1 Strength while within 6 inches of a Vault Cadence marker."


def _reply(payload: dict[str, object]) -> dict[str, object]:
    """One messages-API envelope carrying ``payload`` as its JSON text block."""
    return {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "model": "claude-opus-5",
        "content": [{"type": "text", "text": json.dumps(payload)}],
        "stop_reason": "end_turn",
    }


def _client(http: object | None = None) -> SummaryClient:
    return SummaryClient("unit-test-key-not-a-secret", model="claude-opus-5", http=http)  # type: ignore[arg-type]


# -- (a) draft ---------------------------------------------------------------------------------


def test_draft_sends_the_system_prompt_and_the_text_and_returns_a_parsed_draft(
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(
        url=MESSAGES_URL,
        json=_reply({"summary": INVENTED_SUMMARY, "used_verbatim": False}),
    )

    drafted = _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    assert drafted == Draft(summary=INVENTED_SUMMARY, used_verbatim=False)
    request = httpx_mock.get_requests()[0]
    assert request.headers["anthropic-version"] == "2023-06-01"
    body = json.loads(request.content)
    assert body["system"] == prompts.DRAFT_SYSTEM
    assert body["max_tokens"] == 800
    assert body["model"] == "claude-opus-5"
    sent = json.dumps(body["messages"])
    assert INVENTED_MECHANIC in sent, "the mechanic text is what the model is asked to restate"
    assert INVENTED_NAME in sent


def test_draft_carries_the_verbatim_flag_back(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url=MESSAGES_URL,
        json=_reply({"summary": INVENTED_MECHANIC, "used_verbatim": True}),
    )

    drafted = _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="detachment_rule")

    assert drafted.used_verbatim is True


# -- (b) review --------------------------------------------------------------------------------


def test_review_returns_the_verdict_the_model_gave(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url=MESSAGES_URL,
        json=_reply({"decision": "redraft", "reason_code": "meaning-changed"}),
    )

    verdict = _client().review(INVENTED_NAME, INVENTED_MECHANIC, INVENTED_SUMMARY)

    assert verdict == Verdict(decision="redraft", reason_code="meaning-changed")
    body = json.loads(httpx_mock.get_requests()[0].content)
    assert body["system"] == prompts.REVIEW_SYSTEM


def test_a_reason_code_outside_the_closed_set_is_refused(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url=MESSAGES_URL,
        json=_reply({"decision": "redraft", "reason_code": "the summary reads oddly to me"}),
    )

    with pytest.raises(DraftingError) as caught:
        _client().review(INVENTED_NAME, INVENTED_MECHANIC, INVENTED_SUMMARY)

    assert caught.value.status_code is None


# -- (c) malformed reply -----------------------------------------------------------------------


def test_a_reply_that_is_not_the_expected_json_shape_is_refused(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=MESSAGES_URL, json=_reply({"summary": INVENTED_SUMMARY}))

    with pytest.raises(DraftingError) as caught:
        _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    assert caught.value.status_code is None, "a shape failure is not an HTTP failure"


def test_a_reply_whose_text_block_is_not_json_at_all_is_refused(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url=MESSAGES_URL,
        json={
            "id": "msg_test",
            "type": "message",
            "role": "assistant",
            "model": "claude-opus-5",
            "content": [{"type": "text", "text": "not json"}],
        },
    )

    with pytest.raises(DraftingError):
        _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")


def test_the_refusal_never_quotes_the_reply_body(httpx_mock: HTTPXMock) -> None:
    # A malformed reply may still contain the model's restatement of the rules text. The error
    # says what went wrong and nothing about what it saw (standing rule 2).
    httpx_mock.add_response(url=MESSAGES_URL, json=_reply({"summary": INVENTED_SUMMARY}))

    with pytest.raises(DraftingError) as caught:
        _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    assert INVENTED_SUMMARY not in str(caught.value)


# -- (d) retry ---------------------------------------------------------------------------------


def test_a_429_then_a_200_succeeds_after_one_retry(
    httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    slept: list[float] = []
    monkeypatch.setattr("pipeline.summaries.client.time.sleep", slept.append)
    httpx_mock.add_response(url=MESSAGES_URL, status_code=429)
    httpx_mock.add_response(
        url=MESSAGES_URL,
        json=_reply({"summary": INVENTED_SUMMARY, "used_verbatim": False}),
    )

    drafted = _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    assert drafted.summary == INVENTED_SUMMARY
    assert len(httpx_mock.get_requests()) == 2, "exactly one retry, not a loop"
    assert slept, "the retry backs off rather than hammering the endpoint"


def test_a_second_529_gives_up_and_reports_the_status(
    httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("pipeline.summaries.client.time.sleep", lambda _seconds: None)
    httpx_mock.add_response(url=MESSAGES_URL, status_code=529, is_reusable=True)

    with pytest.raises(DraftingError) as caught:
        _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    assert caught.value.status_code == 529
    assert len(httpx_mock.get_requests()) == 2


def test_a_400_is_not_retried(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=MESSAGES_URL, status_code=400)

    with pytest.raises(DraftingError) as caught:
        _client().review(INVENTED_NAME, INVENTED_MECHANIC, INVENTED_SUMMARY)

    assert caught.value.status_code == 400
    assert len(httpx_mock.get_requests()) == 1


# -- (e) the request body never reaches a logger -----------------------------------------------


def test_the_request_body_is_never_written_to_any_logger(
    httpx_mock: HTTPXMock, caplog: pytest.LogCaptureFixture
) -> None:
    httpx_mock.add_response(
        url=MESSAGES_URL,
        json=_reply({"summary": INVENTED_SUMMARY, "used_verbatim": False}),
    )

    with caplog.at_level(logging.DEBUG):
        _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert INVENTED_MECHANIC not in logged
    assert INVENTED_SUMMARY not in logged
    assert INVENTED_NAME not in logged
    assert "unit-test-key-not-a-secret" not in logged


def test_a_failure_logs_neither_the_body_nor_the_key(
    httpx_mock: HTTPXMock, caplog: pytest.LogCaptureFixture
) -> None:
    httpx_mock.add_response(url=MESSAGES_URL, status_code=400)

    with caplog.at_level(logging.DEBUG), pytest.raises(DraftingError):
        _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert INVENTED_MECHANIC not in logged
    assert "unit-test-key-not-a-secret" not in logged


# -- (f) configuration -------------------------------------------------------------------------


def test_load_config_exposes_the_api_key_stripped_of_its_dotenv_quotes() -> None:
    # The same incident `unquote_env_value` was written for: a `.env.local` secret written
    # `WGC_ANTHROPIC_API_KEY="…"` must not carry its quoting into the request header.
    quoted = load_config(env={"WGC_ANTHROPIC_API_KEY": '"sk-not-a-real-key"'})
    bare = load_config(env={"WGC_ANTHROPIC_API_KEY": "sk-not-a-real-key"})

    assert quoted.anthropic_api_key == bare.anthropic_api_key
    assert not quoted.anthropic_api_key.startswith('"')


def test_the_api_key_is_declared_sensitive_and_never_rendered() -> None:
    from pipeline.config import CONFIG_VARS, REDACTED

    var = next(v for v in CONFIG_VARS if v.env_name == "WGC_ANTHROPIC_API_KEY")
    assert var.sensitive
    secret = "sk-not-a-real-key-0123456789"
    rendered = load_config(env={"WGC_ANTHROPIC_API_KEY": secret}).redacted()
    assert secret not in json.dumps(rendered)
    assert rendered["WGC_ANTHROPIC_API_KEY"] == f"{REDACTED} (set)"


def test_the_two_model_variables_carry_their_documented_defaults() -> None:
    config = load_config(env={})
    assert config.draft_model == "claude-opus-5"
    assert config.review_model == "claude-sonnet-5"


# -- (g) the redraft hint (010 R7 task 2 fix round 1) --------------------------------------------


def test_a_draft_without_a_hint_sends_no_hint_line(httpx_mock: HTTPXMock) -> None:
    """The additive parameter must not change what an existing caller sends."""
    httpx_mock.add_response(
        url=MESSAGES_URL, json=_reply({"summary": INVENTED_SUMMARY, "used_verbatim": False})
    )

    _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    sent = json.dumps(json.loads(httpx_mock.get_requests()[0].content)["messages"])
    assert "reason code" not in sent
    assert "previous attempt" not in sent


def test_the_redraft_hint_reaches_the_request_body(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url=MESSAGES_URL, json=_reply({"summary": INVENTED_SUMMARY, "used_verbatim": False})
    )

    _client().draft(
        INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability", hint="meaning-changed"
    )

    body = json.loads(httpx_mock.get_requests()[0].content)
    # The standing instructions are untouched; only the user message grew.
    assert body["system"] == prompts.DRAFT_SYSTEM
    sent = json.dumps(body["messages"])
    assert "meaning-changed" in sent
    assert "changed, dropped or added meaning" in sent
    assert INVENTED_MECHANIC in sent


def test_an_unrecognised_hint_is_passed_through_rather_than_dropped(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url=MESSAGES_URL, json=_reply({"summary": INVENTED_SUMMARY, "used_verbatim": False})
    )

    _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability", hint="invented-code")

    sent = json.dumps(json.loads(httpx_mock.get_requests()[0].content)["messages"])
    assert "invented-code" in sent


# -- (h) transport faults (010 R7 task 2 fix round 2, B) ----------------------------------------


@pytest.mark.parametrize(
    "fault",
    [
        httpx.ConnectError("an invented connection failure"),
        httpx.ReadTimeout("an invented read timeout"),
        httpx.RemoteProtocolError("an invented protocol fault"),
        httpx.PoolTimeout("an invented pool timeout"),
    ],
    ids=["connect", "read-timeout", "protocol", "pool-timeout"],
)
def test_a_transport_fault_is_reported_as_a_drafting_error(
    httpx_mock: HTTPXMock, fault: httpx.HTTPError
) -> None:
    """A caller that handles `DraftingError` must not be surprised by a socket.

    The whole partial-write path in `tools/draft_summaries.py` keys off this type. Letting these
    propagate as themselves meant one connection reset in a multi-hour billed run bypassed it.
    """
    httpx_mock.add_exception(fault)

    with pytest.raises(DraftingError) as caught:
        _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    assert caught.value.status_code is None
    assert str(caught.value) == "the request did not complete"


def test_a_transport_fault_message_names_neither_the_entry_nor_the_url(
    httpx_mock: HTTPXMock,
) -> None:
    """`httpx` renders a URL, and sometimes a payload hint, in its own `str`. Neither travels."""
    httpx_mock.add_exception(httpx.ConnectError("an invented connection failure"))

    with pytest.raises(DraftingError) as caught:
        _client().draft(INVENTED_NAME, INVENTED_MECHANIC, ability_class="ability")

    rendered = str(caught.value)
    assert INVENTED_MECHANIC not in rendered
    assert INVENTED_NAME not in rendered
    assert "api.anthropic.com" not in rendered
    assert "an invented connection failure" not in rendered
    # Kept for a debugger, never rendered.
    assert isinstance(caught.value.__cause__, httpx.ConnectError)


def test_a_transport_fault_during_review_is_reported_the_same_way(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_exception(httpx.ReadTimeout("an invented read timeout"))

    with pytest.raises(DraftingError) as caught:
        _client().review(INVENTED_NAME, INVENTED_MECHANIC, INVENTED_SUMMARY)

    assert caught.value.status_code is None
