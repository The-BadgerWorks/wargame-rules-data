# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the end-to-end wiring receipts for
# 009 rung R05-fix item 6 (gate on PR #30, Product Owner ruling 2026-09-03): `detect` opts into
# the export-timestamp short-circuit and reports its outcome distinctly (skipped/ok/failed); a
# real, successful detail-source acquisition followed by a downstream points-source failure
# leaves the detail source's own state file unadvanced (item 2, proven again at the wiring level
# rather than only at `acquire_wahapedia`'s own unit tests).
"""`detect`'s new detail-source probe, exercised end to end against a real `PoliteClient` and a
mocked `httpx` transport for BOTH upstreams -- the short-circuit only ever fires on the live
acquisition path (`--fixtures` bypasses it entirely, per `acquire_wahapedia`'s own docstring), so
this is the one place in the suite that can actually watch the second `detect` run skip.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from pipeline.acquire.detail_source import acquire_detail
from pipeline.acquire.http import PoliteClient
from pipeline.acquire.wahapedia import (
    EXPORT_DIGEST_STATE_RELATIVE_PATH,
    EXPORT_FILES,
    LAST_UPDATE_FILE,
)
from pipeline.cli import run_detect
from pipeline.config import PipelineConfig, load_config
from pipeline.exit_codes import ExitCode
from pipeline.models.source import AcquisitionOutcome
from pipeline.observability.ledger import StageOutcome

REPO_ROOT = Path(__file__).resolve().parents[2]
DETECTION_FIXTURES = REPO_ROOT / "fixtures" / "detection"

MFM_HOST = "https://points.example"
WAHAPEDIA_HOST = "https://wahapedia.example"
ALLOW_ALL = "User-agent: *\nAllow: /\n"

#: A placeholder body good enough for every wahapedia export file no test here inspects the
#: content of.
_WAHAPEDIA_PLACEHOLDER = "id|name|\n"


def _config(**overrides: str) -> PipelineConfig:
    return load_config(
        env={
            "WGC_MFM_BASE_URL": f"{MFM_HOST}/en",
            "WGC_DETAIL_SOURCE_URL": WAHAPEDIA_HOST,
            **overrides,
        }
    )


def _mock_mfm_page(httpx_mock: HTTPXMock, *, slug: str, fixture_set: str) -> None:
    """One faction page, served from an existing `fixtures/detection/<set>/mfm/<slug>.html` so
    the DOM shape is real and already proven to parse (or, for `restructured`, already proven to
    raise `StructureChanged`) -- no new synthetic MFM markup is authored here."""
    sitemap = f'<?xml version="1.0"?><urlset><url><loc>{MFM_HOST}/en/{slug}</loc></url></urlset>'
    httpx_mock.add_response(url=f"{MFM_HOST}/sitemap.xml", text=sitemap, is_reusable=True)
    httpx_mock.add_response(url=f"{MFM_HOST}/robots.txt", text=ALLOW_ALL, is_reusable=True)
    page = (DETECTION_FIXTURES / fixture_set / "mfm" / f"{slug}.html").read_text(encoding="utf-8")
    httpx_mock.add_response(url=f"{MFM_HOST}/en/{slug}", text=page, is_reusable=True)


def _mock_wahapedia(httpx_mock: HTTPXMock, *, last_update: str) -> None:
    httpx_mock.add_response(url=f"{WAHAPEDIA_HOST}/robots.txt", text=ALLOW_ALL, is_reusable=True)
    for name in EXPORT_FILES:
        text = last_update if name == LAST_UPDATE_FILE else _WAHAPEDIA_PLACEHOLDER
        httpx_mock.add_response(url=f"{WAHAPEDIA_HOST}/{name}", text=text, is_reusable=True)


@pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
def test_a_second_detect_run_against_an_unmoved_timestamp_skips_the_fetch_and_reports_it(
    temp_repo,
    httpx_mock: HTTPXMock,  # type: ignore[no-untyped-def]
) -> None:
    """The item 6 receipt: a second `detect` run against an unmoved `Last_update.csv` skips the
    detail-source fetch and reports `SRC-EXPORT-UNCHANGED`, with the run record distinguishing
    the first run's `ok` (a normal full fetch) from the second's `skipped`."""
    _mock_mfm_page(httpx_mock, slug="verdant-marchers", fixture_set="baseline")
    _mock_wahapedia(httpx_mock, last_update="2026-08-01T00:00:00Z")

    repo = temp_repo()
    config = _config()
    client = PoliteClient(config, sleep=lambda _seconds: None)
    try:
        first = run_detect(config=config, client=client, repository_root=repo)
        second = run_detect(config=config, client=client, repository_root=repo)
    finally:
        client.close()

    assert first.wahapedia_stage is StageOutcome.OK
    assert first.wahapedia_findings == ()
    assert first.exit_code is ExitCode.CHANGE_DETECTED  # no prior points-source digest either

    assert second.wahapedia_stage is StageOutcome.SKIPPED
    assert second.wahapedia_findings == ("SRC-EXPORT-UNCHANGED",)
    assert second.exit_code is ExitCode.SUCCESS  # the points source itself did not move

    assert (repo / EXPORT_DIGEST_STATE_RELATIVE_PATH).exists()


@pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
def test_a_run_that_fails_downstream_leaves_the_export_digest_state_unadvanced(
    temp_repo,
    httpx_mock: HTTPXMock,  # type: ignore[no-untyped-def]
) -> None:
    """The item 2 receipt, proven again at the wiring level: the detail source acquires a
    genuinely fetchable export successfully, but the points-source sweep fails downstream of it
    (a structural break) -- `state/wahapedia-export-digest.json` must stay exactly as it was
    (absent), and the following acquisition against that same path must fetch in full rather
    than trust a digest the sweep never actually confirmed a complete run over."""
    _mock_mfm_page(httpx_mock, slug="verdant-marchers", fixture_set="restructured")
    _mock_wahapedia(httpx_mock, last_update="2026-08-01T00:00:00Z")

    repo = temp_repo()
    config = _config()
    client = PoliteClient(config, sleep=lambda _seconds: None)
    export_state_path = repo / EXPORT_DIGEST_STATE_RELATIVE_PATH
    try:
        failed = run_detect(config=config, client=client, repository_root=repo)

        assert failed.exit_code is ExitCode.SOURCE_STRUCTURE_CHANGED
        assert failed.wahapedia_stage is StageOutcome.OK, (
            "the detail source itself acquired fine this run -- it is the points source that "
            "broke, downstream of it"
        )
        assert not export_state_path.exists(), (
            "a run that dies partway through is unfinished work, not a completed sweep -- the "
            "detail source's own state must not advance on its account"
        )

        # The following run must re-fetch in full rather than skip -- there is nothing on
        # record for it to have skipped against.
        next_detail_acq, next_payloads = acquire_detail(
            config, client=client, state_path=export_state_path
        )
    finally:
        client.close()

    assert next_detail_acq.outcome is AcquisitionOutcome.OK
    assert len(next_payloads) == len(EXPORT_FILES)


def test_a_build_run_never_reads_or_writes_the_export_digest_state(tmp_path: Path) -> None:
    """The other half of the item 6 receipt: `build` (unwired, by Product Owner ruling) is
    demonstrably unaffected by any of this -- same fingerprint, same acquisition behaviour, no
    state read or written, whatever a caller happens to pass as `state_path`. `run_build` itself
    never passes one (`pipeline/cli.py`'s own comment on `detail_acq.findings` says so), but the
    guarantee belongs to `acquire_wahapedia`/`acquire_detail`, not to `run_build`'s call site
    alone -- a fixtures-driven acquisition returns via `acquire_from_fixtures` before `state_path`
    is even inspected, so this is provable directly.
    """
    from pipeline.acquire.wahapedia import acquire_wahapedia

    fixtures_dir = REPO_ROOT / "fixtures" / "minimal"
    config = load_config(env={})
    # A state_path whose parent does not even exist -- if this were read or written, the
    # acquisition would fail outright rather than silently succeed.
    poison_state_path = tmp_path / "does" / "not" / "exist" / "wahapedia-export-digest.json"

    acquisition, payloads = acquire_wahapedia(
        config, fixtures_dir=fixtures_dir, offline=True, state_path=poison_state_path
    )

    assert acquisition.outcome is AcquisitionOutcome.OK
    assert len(payloads) > 0
    assert not poison_state_path.exists()
    assert not poison_state_path.parent.exists()
