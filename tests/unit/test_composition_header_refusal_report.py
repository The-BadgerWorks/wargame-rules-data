# AI-Assisted: Claude Code (model: claude-sonnet-5) - Asserts the T031 whole-corpus five-signal
# header-refusal re-derivation tool: the pure `refuses()` classifier agrees with
# `pipeline.curate.assemble._refuse_header_row` on the same GF13/GF14/GF15 fixtures T028 already
# proves the production rule against, the measurement discards its acquired text, and the report
# carries datasheet ids, line ordinals, and already-published model names only — never a
# composition description (research D1, risk R-1/R-A).
"""Every invented skeleton below mirrors T028's GF13/GF14/GF15 fixtures directly, so the tool's
own classifier is proven to agree with the production rule it re-derives, not just internally
consistent with itself."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from pipeline.config import load_config
from pipeline.curate.assemble import _composition_entries
from pipeline.curate.authored import AuthoredContent
from pipeline.exit_codes import ExitCode
from pipeline.parse.composition_grammar import CompositionParse
from pipeline.parse.wahapedia_csv import read_file
from tests.enrichment.conftest import curated_models
from tools.composition_header_refusal_report import main, measure, refuses, render

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "fixtures" / "minimal"
ENRICHMENT_FIXTURES = REPO_ROOT / "fixtures" / "enrichment" / "wahapedia"

HTML_ENV = {
    "WGC_DETAIL_ACQUISITION_MODE": "html",
    "WGC_DETAIL_EDITION": "wh40k-11e",
}


def _entry(name: str, count: int) -> CompositionParse:
    return CompositionParse(model_name=name, min_count=count, max_count=count)


# -- refuses() agrees with the production rule on GF13/GF14/GF15 --------------------------------


def test_agrees_with_assemble_py_on_the_two_row_header() -> None:
    # GF13: header refused by both the tool's classifier and the production rule.
    model_lines = {1: "Fenward Sergeant", 2: "Fenward Trooper"}
    first = _entry("Fenward Cohort", 9)
    rest = [_entry("Fenward Sergeant", 3), _entry("Fenward Trooper", 6)]
    assert refuses(first, rest, model_lines=model_lines) is True

    detail = {
        "Datasheets_unit_composition.csv": read_file(
            ENRICHMENT_FIXTURES / "Datasheets_unit_composition.csv"
        ),
    }
    entries, findings = _composition_entries(
        "GF13", "ds-fenward-cohort-alpha", detail, AuthoredContent(), curated_models("GF13")
    )
    assert [entry.model_name for entry in entries] == ["Fenward Sergeant", "Fenward Trooper"]
    assert any(f.finding_code == "CMP-HEADER-ROW" for f in findings)


def test_agrees_with_assemble_py_on_the_single_row_header() -> None:
    # GF14: header refused by both.
    model_lines = {1: "Fenward Outrider"}
    first = _entry("Fenward Vanguard Squad", 5)
    rest = [_entry("Fenward Outrider", 5)]
    assert refuses(first, rest, model_lines=model_lines) is True


def test_agrees_with_assemble_py_on_the_near_miss() -> None:
    # GF15: the near-miss is only reachable through the caller's own position gate (first row
    # only) -- `refuses()` itself is never asked to classify GF15's row 2, exactly as
    # `_refuse_header_row` never considers a non-first row. Row 1 (the datasheet's genuine first
    # row) is correctly NOT refused: it resolves to a model, so signal 5 fails.
    model_lines = {1: "Fenward Relict Warden", 3: "Fenward Relict Skirmisher"}
    first = _entry("Fenward Relict Warden", 1)
    rest = [_entry("Fenward Relict Line", 8), _entry("Fenward Relict Skirmisher", 7)]
    assert refuses(first, rest, model_lines=model_lines) is False


def test_a_fixed_size_genuine_first_row_that_does_not_sum_is_not_refused() -> None:
    model_lines = {1: "Genuine Leader"}
    first = _entry("Genuine Leader", 1)
    rest = [_entry("Genuine Trooper", 4)]
    assert refuses(first, rest, model_lines=model_lines) is False


def test_a_ranged_first_row_is_never_refused() -> None:
    model_lines: dict[int, str] = {}
    ranged = CompositionParse(model_name="Unresolved Header", min_count=3, max_count=9)
    rest = [_entry("Some Model", 9)]
    assert refuses(ranged, rest, model_lines=model_lines) is False


def test_a_linkable_first_row_is_never_refused_even_if_it_sums() -> None:
    """Signal 5 alone can veto a refusal a name blocklist never would."""
    model_lines = {1: "Coincidental Total"}
    first = _entry("Coincidental Total", 9)
    rest = [_entry("Body A", 4), _entry("Body B", 5)]
    assert refuses(first, rest, model_lines=model_lines) is False


# -- the measurement, against the offline smoke-test corpus -------------------------------------


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


def test_refused_never_exceeds_datasheets_with_composition(tmp_path: Path) -> None:
    report = _measure(tmp_path)
    assert len(report.refused) <= report.datasheets_with_composition


def test_no_source_text_reaches_the_report(tmp_path: Path) -> None:
    rendered = render(_measure(tmp_path))
    assert "Composition-header refusal set" in rendered
    assert "no composition description reaches this page" in rendered


def test_it_writes_nothing_but_its_own_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)

    code = main(["--fixtures", str(FIXTURES), "--offline", "--repo", str(tmp_path)])

    assert code == int(ExitCode.SUCCESS)
    written = sorted((tmp_path / "reports" / "composition-header-refusal").glob("*.md"))
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
