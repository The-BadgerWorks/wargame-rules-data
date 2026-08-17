# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the html-mode detail sweep (004 task
# T072): sitemap-driven faction enumeration, one polite request per faction page, the sweep count
# and interval measured against the existing points sweep's politeness budget, the FR-004
# deny-list refusing before a socket is opened, and --offline raising rather than requesting.
"""The html-mode sweep, measured against the politeness budget the repository already spends.

The claim `004` research D1c makes — "~26 pages, the same order of magnitude as the existing
points sweep, so the politeness budget is unchanged in character" — is the reason this feature
did not need a new conversation about rate limits. It is asserted here rather than believed:
:func:`test_the_sweep_is_one_request_per_faction_page_plus_the_sitemap` counts the requests, and
:func:`test_the_sweep_spends_the_same_interval_the_points_sweep_does` counts the seconds.

Every test here runs against a mocked transport or a synthetic fixture set. Nothing opens a
socket, and :func:`test_offline_raises_rather_than_opening_a_socket` makes that a property of the
code rather than of this file's discipline.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from pipeline.acquire.http import OfflineViolation, PoliteClient, SourceUnreachable
from pipeline.acquire.mfm import acquire_mfm
from pipeline.acquire.robots import DisallowedPath
from pipeline.acquire.wahapedia_html import (
    FACTION_PAGE,
    SITEMAP_PATH,
    WORKSPACE_DIR,
    acquire_wahapedia_html,
    enumerate_faction_slugs,
)
from pipeline.config import PipelineConfig, load_config
from pipeline.models.source import AcquisitionOutcome, SourceKey

pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)

HOST = "https://detail.example"
BASE = f"{HOST}/wh40k11ed"
ROBOTS = f"{HOST}/robots.txt"
SITEMAP = f"{BASE}/{SITEMAP_PATH}"

ALLOW_ALL = "User-agent: *\nAllow: /\n"

#: Three invented slugs. The sitemap lists one URL **per datasheet**, not per faction page — the
#: live shape, verified on 2026-08-05 — so the slug set is the distinct path segment, and a
#: faction contributing several entries must still be requested exactly once.
SITEMAP_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url><loc>{BASE}/factions/alpha-covenant/Alpha-Warden</loc></url>
  <url><loc>{BASE}/factions/alpha-covenant/Alpha-Skirmishers</loc></url>
  <url><loc>{BASE}/factions/beta-conclave/Beta-Adept</loc></url>
  <url><loc>{BASE}/factions/gamma-host/Gamma-Rider</loc></url>
  <url><loc>{BASE}/the-rules/core-rules/</loc></url>
</urlset>
"""

SLUGS = ("alpha-covenant", "beta-conclave", "gamma-host")

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment"


def _config(**overrides: str) -> PipelineConfig:
    return load_config(
        env={
            "WGC_DETAIL_ACQUISITION_MODE": "html",
            "WGC_DETAIL_SOURCE_URL": BASE,
            "WGC_DETAIL_EDITION": "wh40k-11e",
            "WGC_REQUEST_INTERVAL_MS": "2000",
            **overrides,
        }
    )


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


def _serve(httpx_mock: HTTPXMock, *, page: str = "<html></html>") -> None:
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL, is_reusable=True)
    httpx_mock.add_response(url=SITEMAP, text=SITEMAP_XML)
    for slug in SLUGS:
        httpx_mock.add_response(url=f"{BASE}/{FACTION_PAGE.format(slug=slug)}", text=page)


# -- the sweep -------------------------------------------------------------------------------


def test_the_faction_list_is_read_from_the_publishers_own_sitemap(httpx_mock: HTTPXMock) -> None:
    _serve(httpx_mock)
    with _client(_config(), Recorder()) as client:
        assert enumerate_faction_slugs(client, BASE) == list(SLUGS)


def test_a_sitemap_that_lists_no_faction_stops_the_run(httpx_mock: HTTPXMock) -> None:
    """Not "we found nothing this time": the base URL is wrong or the layout moved (FR-004)."""
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL, is_reusable=True)
    httpx_mock.add_response(url=SITEMAP, text="<urlset></urlset>")
    with (
        _client(_config(), Recorder()) as client,
        pytest.raises(SourceUnreachable, match="no faction page"),
    ):
        enumerate_faction_slugs(client, BASE)


def test_the_sweep_is_one_request_per_faction_page_plus_the_sitemap(httpx_mock: HTTPXMock) -> None:
    _serve(httpx_mock)
    recorder = Recorder()
    with _client(_config(), recorder) as client:
        acquisition, payloads = acquire_wahapedia_html(_config(), client=client)

    # robots.txt, the sitemap, then one page per faction — and nothing else. A datacard page
    # carries every card for its faction, which is why this is tens of requests rather than the
    # thousands a per-datasheet sweep would cost.
    assert acquisition.request_count == len(SLUGS) + 2
    assert [payload.name for payload in payloads] == list(SLUGS)
    assert acquisition.coverage == {"faction_pages": len(SLUGS)}
    assert acquisition.outcome is AcquisitionOutcome.OK


def test_the_sweep_spends_the_same_interval_the_points_sweep_does(httpx_mock: HTTPXMock) -> None:
    """The politeness budget is a property of the client, and both sweeps share it (research D1c).

    Asserted by running the *points* sweep over the same number of pages against the same
    configured interval and comparing the wall clock each would spend — if the detail sweep ever
    grew its own pacing, this is where the two stop agreeing.
    """
    _serve(httpx_mock)
    detail_recorder = Recorder()
    with _client(_config(), detail_recorder) as client:
        acquire_wahapedia_html(_config(), client=client)

    points_config = load_config(
        env={"WGC_MFM_BASE_URL": f"{HOST}/en", "WGC_REQUEST_INTERVAL_MS": "2000"}
    )
    points_sitemap = "<urlset>{}</urlset>".format(
        "".join(f"<url><loc>{HOST}/{slug}</loc></url>" for slug in SLUGS)
    )
    httpx_mock.add_response(url=f"{HOST}/sitemap.xml", text=points_sitemap)
    for slug in SLUGS:
        httpx_mock.add_response(url=f"{HOST}/en/{slug}", text="<html></html>")
    points_recorder = Recorder()
    with _client(points_config, points_recorder) as client:
        acquire_mfm(points_config, client=client)

    interval = points_config.request_interval_ms / 1000.0
    assert set(detail_recorder.sleeps) <= {interval}
    assert set(points_recorder.sleeps) <= {interval}
    # And the budget is the same order of magnitude, which is the claim research D1c makes.
    assert sum(detail_recorder.sleeps) <= sum(points_recorder.sleeps) * 2


def test_a_page_that_does_not_answer_is_a_failed_sweep(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL, is_reusable=True)
    httpx_mock.add_response(url=SITEMAP, text=SITEMAP_XML)
    httpx_mock.add_response(url=f"{BASE}/{FACTION_PAGE.format(slug=SLUGS[0])}", status_code=404)

    with _client(_config(), Recorder()) as client, pytest.raises(SourceUnreachable):
        acquire_wahapedia_html(_config(), client=client)


# -- carry-forward (008 FR-024/FR-025, Product Owner decision 2026-08-17) ------------------------
#
# A declared faction's page failing no longer fails the whole sweep; an UNDECLARED one still does,
# on the identical terms `test_a_page_that_does_not_answer_is_a_failed_sweep` above already proves
# for the no-declarations-at-all case. Written against a stashed-out `carried_forward_slugs`
# parameter first — confirmed failing (`TypeError: unexpected keyword argument`) — then restored.


def test_a_declared_faction_absent_from_the_sitemap_is_still_attempted(
    httpx_mock: HTTPXMock,
) -> None:
    """The exact gap 008's T074 dry-run found: a slug the sitemap does not list, but whose page
    is still live. A declared slug is attempted even though `enumerate_faction_slugs` never
    named it."""
    _serve(httpx_mock)
    extra = "delta-remnant"
    httpx_mock.add_response(url=f"{BASE}/{FACTION_PAGE.format(slug=extra)}", text="<html></html>")

    with _client(_config(), Recorder()) as client:
        acquisition, payloads = acquire_wahapedia_html(
            _config(), client=client, carried_forward_slugs=frozenset({extra})
        )

    assert {p.name for p in payloads} == {*SLUGS, extra}
    assert acquisition.coverage["faction_pages"] == len(SLUGS) + 1


def test_a_declared_unreachable_faction_is_skipped_not_refused(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL, is_reusable=True)
    httpx_mock.add_response(url=SITEMAP, text=SITEMAP_XML)
    for slug in SLUGS:
        if slug == SLUGS[0]:
            httpx_mock.add_response(url=f"{BASE}/{FACTION_PAGE.format(slug=slug)}", status_code=404)
        else:
            httpx_mock.add_response(
                url=f"{BASE}/{FACTION_PAGE.format(slug=slug)}", text="<html></html>"
            )

    with _client(_config(), Recorder()) as client:
        acquisition, payloads = acquire_wahapedia_html(
            _config(), client=client, carried_forward_slugs=frozenset({SLUGS[0]})
        )

    # No payload for the carried faction — its data comes from the previous tree instead
    # (pipeline.curate.carry_forward), never from a partial or fabricated live fetch.
    assert {p.name for p in payloads} == set(SLUGS[1:])
    assert acquisition.outcome.value == "ok"
    assert acquisition.coverage["carried_forward_faction_count"] == 1


def test_an_undeclared_unreachable_faction_still_refuses_even_with_other_declarations(
    httpx_mock: HTTPXMock,
) -> None:
    """Selectivity: declaring faction A does not relax the FR-008 refusal for faction B."""
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL, is_reusable=True)
    httpx_mock.add_response(url=SITEMAP, text=SITEMAP_XML)
    httpx_mock.add_response(
        url=f"{BASE}/{FACTION_PAGE.format(slug=SLUGS[0])}", text="<html></html>"
    )
    httpx_mock.add_response(
        url=f"{BASE}/{FACTION_PAGE.format(slug=SLUGS[1])}", status_code=404, is_reusable=True
    )

    with (
        _client(_config(), Recorder()) as client,
        pytest.raises(SourceUnreachable, match="carried-forward-factions"),
    ):
        acquire_wahapedia_html(
            _config(), client=client, carried_forward_slugs=frozenset({SLUGS[0]})
        )


def test_a_declared_faction_that_is_reachable_uses_live_data(httpx_mock: HTTPXMock) -> None:
    """The source recovered: live data wins, exactly as O2's "prefer real data" instruction."""
    _serve(httpx_mock, page="<html><body>live and current</body></html>")

    with _client(_config(), Recorder()) as client:
        acquisition, payloads = acquire_wahapedia_html(
            _config(), client=client, carried_forward_slugs=frozenset({SLUGS[0]})
        )

    (recovered,) = [p for p in payloads if p.name == SLUGS[0]]
    assert recovered.text == "<html><body>live and current</body></html>"
    assert acquisition.coverage["carry_forward_unused_declaration_count"] == 1
    assert acquisition.coverage.get("carried_forward_faction_count", 0) == 0


def test_no_declarations_leaves_coverage_exactly_as_before(httpx_mock: HTTPXMock) -> None:
    """A declaration-free run's `coverage` keeps the plain `{"faction_pages": N}` shape every
    existing test and report reads — no new key appears unless something was actually declared."""
    _serve(httpx_mock)
    with _client(_config(), Recorder()) as client:
        acquisition, _ = acquire_wahapedia_html(_config(), client=client)

    assert acquisition.coverage == {"faction_pages": len(SLUGS)}


def test_the_pages_land_in_the_workspace_and_nowhere_else(
    httpx_mock: HTTPXMock, tmp_path: Path
) -> None:
    _serve(httpx_mock, page="<html><body>invented</body></html>")
    with _client(_config(), Recorder()) as client:
        acquire_wahapedia_html(_config(), client=client, workspace=tmp_path)

    written = sorted(path.name for path in (tmp_path / WORKSPACE_DIR).iterdir())
    assert written == [f"{slug}.html" for slug in SLUGS]
    assert sorted(entry.name for entry in tmp_path.iterdir()) == [WORKSPACE_DIR]


# -- the guards ------------------------------------------------------------------------------


def test_offline_raises_rather_than_opening_a_socket() -> None:
    """No mocked transport here on purpose: a request would be a real one, and would fail."""
    with pytest.raises(OfflineViolation, match="--offline"):
        acquire_wahapedia_html(_config(), offline=True)


def test_a_deny_listed_base_url_issues_no_request_at_all() -> None:
    """FR-004: the previous-edition tree is refused before a request is constructed.

    Pointed at the disallowed tree, the sweep never reaches its sitemap read — which is what
    "issues no request" means, and why this test needs no transport either.
    """
    config = _config(WGC_DETAIL_SOURCE_URL=f"{HOST}/wh40k10ed")
    with pytest.raises(DisallowedPath, match="wh40k10ed"):
        acquire_wahapedia_html(config)


def test_the_permitted_current_edition_tree_is_not_refused(httpx_mock: HTTPXMock) -> None:
    """The mirror image of the test above, and the one that would catch an over-broad rule."""
    _serve(httpx_mock)
    with _client(_config(), Recorder()) as client:
        acquisition, _ = acquire_wahapedia_html(_config(), client=client)
    assert acquisition.outcome is AcquisitionOutcome.OK


# -- fixtures --------------------------------------------------------------------------------


def test_a_fixture_set_sources_the_same_record_with_no_network() -> None:
    acquisition, payloads = acquire_wahapedia_html(_config(), fixtures_dir=FIXTURES, offline=True)

    assert acquisition.source_key is SourceKey.WAHAPEDIA
    assert acquisition.declared_edition_code == "wh40k-11e"
    assert acquisition.request_count == 0
    assert [payload.name for payload in payloads] == ["glimmerfen-covenant"]
