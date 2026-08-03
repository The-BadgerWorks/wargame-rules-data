# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the politeness contract (task T028):
# the configured interval is observed, a 429/403 produces exit 40 with a named diagnostic and no
# further requests, a robots.txt disallow stops the sweep, and --offline makes any request a
# hard failure (FR-007).
"""FR-007 is a behaviour contract, so these are behaviour tests.

The one that matters most is :func:`test_a_refusal_is_never_retried`. Retrying a refusal is the
definition of evading one, and the difference between "polite client" and "the thing that got
the project blocked" is exactly that branch.
"""

from __future__ import annotations

import dataclasses

import pytest
from pytest_httpx import HTTPXMock

from pipeline.acquire.http import (
    DEFAULT_HEADERS,
    USER_AGENT,
    OfflineViolation,
    PoliteClient,
    RobotsDisallowed,
    SourceRefused,
    SourceUnreachable,
)
from pipeline.config import PipelineConfig, load_config
from pipeline.exit_codes import ExitCode

pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)

HOST = "https://points.example"
PAGE = f"{HOST}/en/faction/alpha"
ROBOTS = f"{HOST}/robots.txt"

ALLOW_ALL = "User-agent: *\nAllow: /\n"
DISALLOW_ALL = "User-agent: *\nDisallow: /\n"


def _config(**overrides: str) -> PipelineConfig:
    return load_config(env={"WGC_REQUEST_INTERVAL_MS": "2000", "WGC_MAX_RETRIES": "2", **overrides})


class Recorder:
    """A stand-in clock and sleeper, so the polite interval is asserted, not spent."""

    def __init__(self) -> None:
        self.sleeps: list[float] = []

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)

    def monotonic(self) -> float:
        return 0.0


def _client(config: PipelineConfig, recorder: Recorder, **kwargs: object) -> PoliteClient:
    return PoliteClient(
        config,
        sleep=recorder.sleep,
        monotonic=recorder.monotonic,
        jitter=lambda: 0.0,
        **kwargs,  # type: ignore[arg-type]
    )


def test_the_configured_interval_is_observed_between_requests(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL)
    httpx_mock.add_response(url=PAGE, text="<html></html>", is_reusable=True)

    recorder = Recorder()
    with _client(_config(), recorder) as client:
        client.get(PAGE)
        client.get(PAGE)

    # robots.txt is the first request of the run and waits for nothing; every request after it
    # waits out the configured interval.
    assert recorder.sleeps == [2.0, 2.0]


def test_jitter_only_ever_adds_delay(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL)
    httpx_mock.add_response(url=PAGE, text="<html></html>", is_reusable=True)

    recorder = Recorder()
    client = PoliteClient(
        _config(), sleep=recorder.sleep, monotonic=recorder.monotonic, jitter=lambda: 0.4
    )
    with client:
        client.get(PAGE)
        client.get(PAGE)

    assert recorder.sleeps == [pytest.approx(2.4), pytest.approx(2.4)]


def test_a_browser_user_agent_and_english_are_sent(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL)
    httpx_mock.add_response(url=PAGE, text="<html></html>")

    recorder = Recorder()
    with _client(_config(), recorder) as client:
        client.get(PAGE)

    request = httpx_mock.get_requests()[-1]
    assert request.headers["User-Agent"] == USER_AGENT
    assert request.headers["Accept-Language"] == "en"
    assert DEFAULT_HEADERS["User-Agent"].startswith("Mozilla/5.0")


@pytest.mark.parametrize("status", [403, 429])
def test_a_refusal_is_never_retried_and_stops_the_run(httpx_mock: HTTPXMock, status: int) -> None:
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL)
    httpx_mock.add_response(url=PAGE, status_code=status, is_reusable=True)

    recorder = Recorder()
    with _client(_config(), recorder) as client:
        with pytest.raises(SourceRefused) as raised:
            client.get(PAGE)

        assert raised.value.exit_code is ExitCode.SOURCE_UNAVAILABLE
        assert raised.value.finding_code == "SRC-REFUSED"
        assert str(status) in str(raised.value), "the diagnostic must name what happened"

        # One robots fetch and exactly one page fetch: the refusal was not retried.
        assert client.request_count == 2

        # And no further request is made against that host for the rest of the run.
        with pytest.raises(SourceRefused):
            client.get(f"{HOST}/en/faction/beta")
        assert client.request_count == 2


def test_transient_failures_are_retried_up_to_the_ceiling_and_no_further(
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL)
    httpx_mock.add_response(url=PAGE, status_code=503, is_reusable=True)

    recorder = Recorder()
    with _client(_config(), recorder) as client:
        with pytest.raises(SourceUnreachable):
            client.get(PAGE)
        # WGC_MAX_RETRIES = 2 means three attempts in total, plus the one robots fetch.
        assert client.request_count == 4
    # Every retry waited out the full polite interval; nothing accelerated.
    assert recorder.sleeps == [2.0, 2.0, 2.0]


def test_a_robots_disallow_stops_the_sweep(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=ROBOTS, text=DISALLOW_ALL)

    recorder = Recorder()
    with _client(_config(), recorder) as client, pytest.raises(RobotsDisallowed) as raised:
        client.get(PAGE)

    assert raised.value.exit_code is ExitCode.SOURCE_UNAVAILABLE
    assert "robots.txt" in str(raised.value)
    # Only robots.txt itself was fetched; the disallowed page never was.
    assert client.request_count == 1


def test_a_missing_robots_file_is_read_as_no_rules_stated(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=ROBOTS, status_code=404)
    httpx_mock.add_response(url=PAGE, text="<html></html>")

    recorder = Recorder()
    with _client(_config(), recorder) as client:
        assert client.get(PAGE).status_code == 200


def test_offline_makes_any_request_a_hard_failure() -> None:
    recorder = Recorder()
    with (
        _client(_config(), recorder, offline=True) as client,
        pytest.raises(OfflineViolation) as raised,
    ):
        client.get(PAGE)

    assert raised.value.exit_code is ExitCode.CONFIG_ERROR
    assert "--fixtures" in str(raised.value), "the diagnostic should name the way out"
    assert client.request_count == 0, "offline mode must not open a socket at all"


def test_the_interval_comes_from_configuration_not_a_constant(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL)
    httpx_mock.add_response(url=PAGE, text="<html></html>", is_reusable=True)

    slow = dataclasses.replace(_config(), request_interval_ms=5000)
    recorder = Recorder()
    with _client(slow, recorder) as client:
        client.get(PAGE)
        client.get(PAGE)

    assert recorder.sleeps == [5.0, 5.0]
