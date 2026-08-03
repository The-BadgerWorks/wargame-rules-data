# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the detection outcome tests (task
# T102): a mechanical change exits 10, a presentation-only change exits 0 and raises no
# candidate, an unreachable source exits 40, a restructured source exits 41 with the prior
# digest untouched, and every check appends a ledger entry (FR-051..FR-054).
"""`rules-pipeline detect`'s whole exit-code contract, one outcome per test.

The two failure cases (`40`, `41`) share the property that matters most: **the previously
recorded digest is untouched.** A detector that overwrote its own baseline on a failed sweep
could talk itself into believing a broken run was the new normal, which is precisely the "the
previously published version stays current" guarantee FR-007/FR-008 make.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from pipeline.acquire.http import PoliteClient
from pipeline.cli import DetectResult, run_detect
from pipeline.config import PipelineConfig, load_config
from pipeline.exit_codes import ExitCode
from pipeline.observability.ledger import LEDGER_RELATIVE_PATH, read_entries

DETECTION = Path(__file__).resolve().parents[2] / "fixtures" / "detection"

DIGEST_STATE_PATH = "state/detection-digest.json"


def _config(**overrides: str) -> PipelineConfig:
    return load_config(env=dict(overrides))


def _sweep(fixture_set: str, repo: Path) -> DetectResult:
    return run_detect(
        config=_config(),
        fixtures_dir=DETECTION / fixture_set,
        offline=True,
        repository_root=repo,
    )


def test_a_mechanical_change_exits_10(temp_repo) -> None:  # type: ignore[no-untyped-def]
    repo = temp_repo()
    _sweep("baseline", repo)

    result = _sweep("mechanical-change", repo)

    assert result.exit_code is ExitCode.CHANGE_DETECTED
    assert result.changed_factions == ("verdant-marchers",)


def test_a_presentation_only_change_exits_0_and_raises_no_candidate(temp_repo) -> None:  # type: ignore[no-untyped-def]
    repo = temp_repo()
    _sweep("baseline", repo)

    result = _sweep("presentation-only", repo)

    assert result.exit_code is ExitCode.SUCCESS
    assert result.changed_factions == ()


def test_a_restructured_source_exits_41_and_the_prior_digest_is_untouched(temp_repo) -> None:  # type: ignore[no-untyped-def]
    repo = temp_repo()
    _sweep("baseline", repo)
    state_before = (repo / DIGEST_STATE_PATH).read_text(encoding="utf-8")

    result = _sweep("restructured", repo)

    assert result.exit_code is ExitCode.SOURCE_STRUCTURE_CHANGED
    assert result.diagnostic is not None
    assert "SRC-STRUCTURE-CHANGED" in result.diagnostic
    assert (repo / DIGEST_STATE_PATH).read_text(encoding="utf-8") == state_before


@pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
def test_an_unreachable_source_exits_40_and_the_prior_digest_is_untouched(  # type: ignore[no-untyped-def]
    temp_repo, httpx_mock: HTTPXMock
) -> None:
    """A filesystem fixture cannot represent network unreachability (``fixtures/detection/
    README.md``), so this is the one detection outcome exercised against a real
    :class:`PoliteClient` and a mocked transport, the same way ``test_http_politeness.py`` does.
    """
    host = "https://points.example"
    sitemap = (
        '<?xml version="1.0"?><urlset>'
        "<url><loc>https://points.example/en/verdant-marchers</loc></url>"
        "</urlset>"
    )
    httpx_mock.add_response(url=f"{host}/sitemap.xml", text=sitemap)
    httpx_mock.add_response(url=f"{host}/robots.txt", text="User-agent: *\nAllow: /\n")
    httpx_mock.add_response(url=f"{host}/en/verdant-marchers", status_code=503, is_reusable=True)

    repo = temp_repo()
    config = _config(WGC_MFM_BASE_URL=f"{host}/en", WGC_MAX_RETRIES="0")
    client = PoliteClient(config, sleep=lambda _seconds: None)
    try:
        result = run_detect(config=config, client=client, repository_root=repo)
    finally:
        client.close()

    assert result.exit_code is ExitCode.SOURCE_UNAVAILABLE
    assert result.diagnostic is not None
    assert not (repo / DIGEST_STATE_PATH).exists()


def test_every_check_appends_a_ledger_entry_so_a_quiet_period_is_distinguishable(  # type: ignore[no-untyped-def]
    temp_repo,
) -> None:
    """A completed no-change check (exit `0`) is recorded exactly like a changed one — the
    ledger is what makes a quiet period distinguishable from a detector that has stopped running
    at all (FR-054)."""
    repo = temp_repo()
    _sweep("baseline", repo)
    _sweep("presentation-only", repo)

    entries = read_entries(repo / LEDGER_RELATIVE_PATH)
    assert [entry["command"] for entry in entries] == ["detect", "detect"]
    assert [entry["exit_code"] for entry in entries] == [10, 0]
