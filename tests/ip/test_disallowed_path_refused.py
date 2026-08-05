# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the FR-004 pre-request deny-list
# (004 task T004): a request for a disallowed path fails the run with a named diagnostic and a
# mocked transport proves ZERO HTTP calls were issued, while the permitted current-edition tree
# is unaffected.
"""FR-004 is a compliance control, so the assertion that matters is *zero requests*.

`004/research.md` D1a re-read the source's published crawling rules and found the
previous-edition tree — the exact path the previous edition's export sits under — explicitly
disallowed, correcting `002/plan.md`'s recorded "verified ``Allow: /``". Honouring the file
after fetching it is not enough on its own: a permissive edit, a truncated response, or an
unreachable ``robots.txt`` (which :mod:`pipeline.acquire.http` reads, correctly, as "no rules
stated") would all reopen the path. The deny-list closes it *before a request is constructed*,
which is what the spec's verification plan asks for in as many words.

These tests therefore assert behaviour at two levels: the predicate refuses the right paths,
and the client issues no socket traffic at all for one.
"""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from pipeline.acquire.http import PoliteClient
from pipeline.acquire.robots import (
    DISALLOWED_PATH_PREFIXES,
    DisallowedPath,
    assert_path_permitted,
    disallowed_prefix,
)
from pipeline.config import PipelineConfig, load_config
from pipeline.exit_codes import ExitCode

pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)

HOST = "https://wahapedia.ru"
PREVIOUS_EDITION = f"{HOST}/wh40k10ed/Datasheets.csv"
STAGING_TREE = f"{HOST}/wh40k11ed_/factions/alpha/datasheets.html"
PERMITTED = f"{HOST}/wh40k11ed/factions/alpha/datasheets.html"
ROBOTS = f"{HOST}/robots.txt"

ALLOW_ALL = "User-agent: *\nAllow: /\n"


def _config(**overrides: str) -> PipelineConfig:
    return load_config(env={"WGC_REQUEST_INTERVAL_MS": "0", "WGC_MAX_RETRIES": "0", **overrides})


def _client(**kwargs: object) -> PoliteClient:
    return PoliteClient(
        _config(),
        sleep=lambda _seconds: None,
        monotonic=lambda: 0.0,
        jitter=lambda: 0.0,
        **kwargs,  # type: ignore[arg-type]
    )


# -- the deny-list itself ----------------------------------------------------------------


def test_the_deny_list_is_exactly_the_two_paths_the_source_disallows() -> None:
    # research D1a, re-confirmed by the T002 spike against the live robots.txt.
    assert set(DISALLOWED_PATH_PREFIXES) == {"/wh40k10ed/", "/wh40k11ed_/"}


@pytest.mark.parametrize(
    "url",
    [
        PREVIOUS_EDITION,
        STAGING_TREE,
        "https://wahapedia.ru/wh40k10ed/",
        "http://wahapedia.ru/WH40K10ED/Factions.csv",
        "/wh40k10ed/Datasheets_options.csv",
        "https://wahapedia.ru//wh40k10ed//Datasheets.csv",
        "https://wahapedia.ru/wh40k10ed%2FDatasheets.csv",
        "https://wahapedia.ru/wh40k11ed_/factions/alpha/datasheets.html",
    ],
)
def test_a_disallowed_path_is_recognised_however_it_is_spelled(url: str) -> None:
    assert disallowed_prefix(url) is not None, f"{url} must be refused"


@pytest.mark.parametrize(
    "url",
    [
        PERMITTED,
        "https://wahapedia.ru/wh40k11ed/Datasheets.csv",
        "https://wahapedia.ru/robots.txt",
        "https://mfm.warhammer-community.com/en/faction/alpha",
        # The permitted tree is a prefix of nothing disallowed, and the underscore tree must not
        # drag it down with it.
        "https://wahapedia.ru/wh40k11ed/the-rules/data-export/",
    ],
)
def test_a_permitted_path_is_untouched(url: str) -> None:
    assert disallowed_prefix(url) is None, f"{url} must be permitted"


def test_the_diagnostic_names_the_path_class_and_the_requirement() -> None:
    with pytest.raises(DisallowedPath) as raised:
        assert_path_permitted(PREVIOUS_EDITION)

    message = str(raised.value)
    assert "/wh40k10ed/" in message, "the diagnostic must name which rule was hit"
    assert "FR-004" in message, "and the requirement that forbids it"
    assert raised.value.finding_code == "SRC-REFUSED"
    assert raised.value.exit_code is ExitCode.CONFIG_ERROR


def test_assert_path_permitted_returns_a_permitted_url_unchanged() -> None:
    assert assert_path_permitted(PERMITTED) == PERMITTED


# -- and the behaviour that actually matters: no request is issued -----------------------


@pytest.mark.parametrize("url", [PREVIOUS_EDITION, STAGING_TREE])
def test_a_disallowed_path_issues_zero_requests(httpx_mock: HTTPXMock, url: str) -> None:
    # Every response the client could conceivably want is registered, so a request that *is*
    # issued succeeds and the test fails loudly rather than erroring for an unrelated reason.
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL, is_reusable=True)
    httpx_mock.add_response(url=url, text="", is_reusable=True)

    with _client() as client, pytest.raises(DisallowedPath):
        client.get(url)

    assert client.request_count == 0, "the guard runs before a request is constructed"
    assert httpx_mock.get_requests() == [], "not one socket was opened, robots.txt included"


def test_the_guard_runs_ahead_of_the_robots_txt_check(httpx_mock: HTTPXMock) -> None:
    """A permissive or unreachable ``robots.txt`` may not reopen a disallowed path.

    :mod:`pipeline.acquire.http` reads a missing ``robots.txt`` as "no rules stated", which is
    the standard reading and the right one — but it means the fetch-and-honour check alone
    cannot be the control for a path we already know is forbidden.
    """
    httpx_mock.add_response(url=ROBOTS, status_code=404, is_reusable=True)
    httpx_mock.add_response(url=PREVIOUS_EDITION, text="", is_reusable=True)

    with _client() as client, pytest.raises(DisallowedPath):
        client.get(PREVIOUS_EDITION)

    assert httpx_mock.get_requests() == []


def test_the_permitted_current_edition_tree_is_unaffected(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL)
    httpx_mock.add_response(url=PERMITTED, text="<html></html>")

    with _client() as client:
        assert client.get(PERMITTED).status_code == 200
    assert client.request_count == 2, "robots.txt, then the page — unchanged behaviour"


def test_offline_mode_still_refuses_a_disallowed_path() -> None:
    # Neither guard may shadow the other into silence: offline refuses network access, the
    # deny-list refuses this path, and a disallowed path in an offline run is still disallowed.
    with _client(offline=True) as client, pytest.raises(DisallowedPath):
        client.get(PREVIOUS_EDITION)
    assert client.request_count == 0
