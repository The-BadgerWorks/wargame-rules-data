# AI-Assisted: Claude Code (model: claude-sonnet-5) - Asserts the R-2 non-summing-header
# population probe (007 task T004): the pure per-datasheet classification is disjoint and correct
# on invented composition shapes, the measurement discards its acquired text, and the report
# carries counts and datasheet ids only — never a composition description (research D1, risk R-2).
"""Every skeleton below is invented: invented counts, invented model-row shapes.

The classifier only ever sees already-parsed :class:`CompositionParse` rows, never a raw
description, which is what lets it be tested without acquiring anything.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from pipeline.config import load_config
from pipeline.exit_codes import ExitCode
from pipeline.parse.composition_grammar import CompositionParse
from tools.header_refusal_population import classify_datasheet, main, measure, render

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "fixtures" / "minimal"

HTML_ENV = {
    "WGC_DETAIL_ACQUISITION_MODE": "html",
    "WGC_DETAIL_EDITION": "wh40k-11e",
}


def _entry(*, count: int, min_count: int | None = None) -> CompositionParse:
    return CompositionParse(
        model_name="invented model",
        min_count=count if min_count is None else min_count,
        max_count=count,
    )


# -- classify_datasheet -------------------------------------------------------------------------


def test_a_single_row_datasheet_is_not_a_candidate() -> None:
    assert classify_datasheet([_entry(count=5)]) == "not_a_candidate"


def test_a_ranged_first_row_is_not_a_candidate() -> None:
    """`min_count != max_count` — a range states itself, not a total."""
    ranged = CompositionParse(model_name="invented model", min_count=3, max_count=6)
    assert classify_datasheet([ranged, _entry(count=6)]) == "not_a_candidate"


def test_an_unresolved_first_row_is_not_a_candidate() -> None:
    assert classify_datasheet([None, _entry(count=5)]) == "not_a_candidate"


def test_a_two_row_header_that_sums_is_sums() -> None:
    """The two-row shape research D1 measured: a header over one model row equal to it."""
    assert classify_datasheet([_entry(count=5), _entry(count=5)]) == "sums"


def test_a_three_row_header_that_sums_across_successors_is_sums() -> None:
    assert classify_datasheet([_entry(count=8), _entry(count=3), _entry(count=5)]) == "sums"


def test_a_header_shaped_row_whose_successors_do_not_sum_is_non_sums() -> None:
    """The R-2 population this tool exists to measure."""
    assert classify_datasheet([_entry(count=9), _entry(count=3), _entry(count=5)]) == "non_sums"


def test_an_unresolved_successor_makes_the_sum_undefined() -> None:
    assert classify_datasheet([_entry(count=5), None]) == "successor_unresolved"
    assert classify_datasheet([_entry(count=5), _entry(count=2), None]) == "successor_unresolved"


def test_classification_is_deterministic() -> None:
    rows = [_entry(count=5), _entry(count=5)]
    assert [classify_datasheet(rows) for _ in range(3)] == ["sums"] * 3


# -- the measurement ----------------------------------------------------------------------------


def _measure(repo: Path):  # type: ignore[no-untyped-def]
    return measure(
        load_config(env=HTML_ENV),
        repository_root=repo,
        fixtures_dir=FIXTURES,
        offline=True,
        generated_at=datetime(2026, 8, 13, tzinfo=UTC),
    )


def test_the_run_records_the_mode_and_edition_it_measured(tmp_path: Path) -> None:
    report = _measure(tmp_path)
    assert (report.mode, report.edition) == ("html", "wh40k-11e")


def test_the_acquired_text_is_discarded(tmp_path: Path) -> None:
    _measure(tmp_path)
    work = tmp_path / "work"
    assert not work.exists() or next(work.iterdir(), None) is None


def test_non_summing_never_exceeds_the_candidate_count(tmp_path: Path) -> None:
    report = _measure(tmp_path)
    assert report.summing + report.non_summing == report.header_candidates
    assert report.header_candidates <= report.datasheets_with_composition


def test_no_source_text_reaches_the_report(tmp_path: Path) -> None:
    rendered = render(_measure(tmp_path))
    assert "Unit-size-header non-summing population" in rendered
    assert "no composition description reaches this page" in rendered


def test_it_writes_nothing_but_its_own_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)

    code = main(["--fixtures", str(FIXTURES), "--offline", "--repo", str(tmp_path)])

    assert code == int(ExitCode.SUCCESS)
    written = sorted((tmp_path / "reports" / "header-refusal-population").glob("*.md"))
    assert len(written) == 1
    assert not (tmp_path / "data").exists()
    assert not (tmp_path / "curation").exists()


def test_a_live_run_without_a_source_url_is_a_configuration_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("WGC_DETAIL_SOURCE_URL", raising=False)

    code = main(["--repo", str(tmp_path)])

    assert code == int(ExitCode.CONFIG_ERROR)
    assert "WGC_DETAIL_SOURCE_URL" in capsys.readouterr().err
    assert not (tmp_path / "reports").exists()
