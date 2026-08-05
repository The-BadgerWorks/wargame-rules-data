# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the churn dry run (004 task T075):
# it measures the re-review wave per faction and in total, writes nothing under curation/,
# discards the acquired text with work/, and puts neither a digest nor the key in its report
# (research D8, risk R-B, quickstart section 3).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the live-path assertions (004 T075
# follow-up): the tool's un-fixtured invocation, which is the one that met the real source and
# the one no test exercised.
"""What a measurement tool has to be trusted about is what it does *not* do.

The number this tool produces sizes a blocking campaign, so the counts are asserted. But the
tests that earn it the right to run against the live source are the other four:
:func:`test_it_writes_nothing_under_curation`, :func:`test_the_acquired_text_is_discarded`,
:func:`test_no_digest_reaches_the_report`, and :func:`test_the_report_never_carries_the_key`.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from pipeline.acquire.detail_source import acquire_detail, read_detail
from pipeline.config import load_config
from pipeline.curate.summaries import compute_current_digests
from pipeline.exit_codes import ExitCode
from tools.churn_dry_run import main, measure, render

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "fixtures" / "minimal"
KEY = "churn-dry-run-test-key"

HTML_ENV = {
    "WGC_DETAIL_ACQUISITION_MODE": "html",
    "WGC_DETAIL_EDITION": "wh40k-11e",
    "WGC_MECHANIC_DIGEST_KEY": KEY,
}


def _current_digests() -> dict[str, str]:
    """The digests the fixture source produces, computed exactly as the tool computes them."""
    config = load_config(env=HTML_ENV)
    _acquisition, payloads = acquire_detail(config, fixtures_dir=FIXTURES, offline=True)
    return compute_current_digests(read_detail(config, payloads), key=KEY.encode("utf-8"))


def _authored(curation: Path, faction_id: str, records: list[dict[str, object]]) -> Path:
    directory = curation / "abilities"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{faction_id}.json"
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return path


@pytest.fixture
def curation(tmp_path: Path) -> Path:
    """Two faction files: one whose summaries are current, one whose mechanic has moved."""
    digests = _current_digests()
    current_key = "core:deep-strike"
    moved_key = "datasheet:ember-shield"

    _authored(
        tmp_path / "curation",
        "f-current",
        [
            {
                "ability_key": current_key,
                "name": "Current",
                "summary": "An invented summary that is still accurate.",
                "review_state": "approved",
                "mechanic_digest": digests[current_key],
            }
        ],
    )
    _authored(
        tmp_path / "curation",
        "f-moved",
        [
            {
                "ability_key": moved_key,
                "name": "Moved",
                "summary": "An invented summary whose mechanic has since changed.",
                "review_state": "approved",
                "mechanic_digest": "0" * 32,
            },
            {
                "ability_key": "datasheet:retired",
                "name": "Retired",
                "summary": "An invented summary for an ability this edition no longer publishes.",
                "review_state": "approved",
                "mechanic_digest": "1" * 32,
            },
            {
                "ability_key": "datasheet:slag-wake",
                "name": "Still drafting",
                "summary": "An invented summary nobody has approved yet.",
                "review_state": "draft",
                "mechanic_digest": digests["datasheet:slag-wake"],
            },
        ],
    )
    return tmp_path / "curation"


def _measure(repo: Path, curation: Path):  # type: ignore[no-untyped-def]
    return measure(
        load_config(env=HTML_ENV),
        repository_root=repo,
        curation_dir=curation,
        fixtures_dir=FIXTURES,
        offline=True,
        generated_at=datetime(2026, 8, 5, tzinfo=UTC),
    )


# -- the measurement ---------------------------------------------------------------------------


def test_it_counts_the_wave_per_faction_and_in_total(tmp_path: Path, curation: Path) -> None:
    report = _measure(tmp_path, curation)

    per_faction = {faction.faction_id: faction for faction in report.factions}
    assert per_faction["f-current"].needs_rereview == 0
    assert per_faction["f-moved"].needs_rereview == 1
    assert report.needs_rereview == 1
    assert report.total == 4
    assert report.approved == 3
    assert report.ratio == pytest.approx(1 / 3)


def test_an_ability_the_edition_no_longer_publishes_is_counted_apart(
    tmp_path: Path, curation: Path
) -> None:
    """It cannot flip — there is no fresh digest to differ from — and it is not re-reviewed."""
    report = _measure(tmp_path, curation)
    moved = next(f for f in report.factions if f.faction_id == "f-moved")

    assert moved.absent_from_source == 1
    assert report.absent_from_source == 1


def test_a_record_nobody_approved_is_not_counted_as_churn(tmp_path: Path, curation: Path) -> None:
    """A draft is already blocking for its own reason; counting it here would double-count it."""
    report = _measure(tmp_path, curation)
    moved = next(f for f in report.factions if f.faction_id == "f-moved")

    assert moved.unapproved == 1
    assert moved.needs_rereview == 1


def test_the_run_records_the_mode_and_edition_it_measured(tmp_path: Path, curation: Path) -> None:
    report = _measure(tmp_path, curation)
    assert (report.mode, report.edition) == ("html", "wh40k-11e")


# -- what it must not do -------------------------------------------------------------------------


def test_it_writes_nothing_under_curation(tmp_path: Path, curation: Path) -> None:
    """The wave is a measurement. Flipping records from a script is what must never happen."""
    before = {path: path.read_bytes() for path in sorted((curation / "abilities").glob("*.json"))}
    _measure(tmp_path, curation)
    after = {path: path.read_bytes() for path in sorted((curation / "abilities").glob("*.json"))}

    assert before == after


def test_the_acquired_text_is_discarded(tmp_path: Path, curation: Path) -> None:
    _measure(tmp_path, curation)
    work = tmp_path / "work"
    assert not work.exists() or next(work.iterdir(), None) is None


def test_no_digest_reaches_the_report(tmp_path: Path, curation: Path) -> None:
    """A digest in a committed report is a fingerprint of the publisher's wording (FR-027)."""
    digests = _current_digests()
    rendered = render(_measure(tmp_path, curation))

    for digest in digests.values():
        assert digest not in rendered
    assert "0" * 32 not in rendered


def test_the_report_never_carries_the_key(tmp_path: Path, curation: Path) -> None:
    assert KEY not in render(_measure(tmp_path, curation))


def test_the_report_carries_every_faction_file_it_measured(tmp_path: Path, curation: Path) -> None:
    rendered = render(_measure(tmp_path, curation))
    assert "`f-current`" in rendered
    assert "`f-moved`" in rendered
    assert "Digest-churn dry run" in rendered


# -- the entry point ----------------------------------------------------------------------------


def test_a_missing_digest_key_is_a_configuration_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """And the diagnostic names the variable without ever naming what it would have held."""
    monkeypatch.delenv("WGC_MECHANIC_DIGEST_KEY", raising=False)
    for name, value in HTML_ENV.items():
        if name != "WGC_MECHANIC_DIGEST_KEY":
            monkeypatch.setenv(name, value)

    code = main(["--fixtures", str(FIXTURES), "--offline", "--repo", str(tmp_path)])

    assert code == int(ExitCode.CONFIG_ERROR)
    assert "WGC_MECHANIC_DIGEST_KEY" in capsys.readouterr().err


def test_a_live_run_without_a_source_url_is_a_configuration_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The live path, which every other test here reaches past by passing ``--fixtures``.

    This is the exact invocation that failed the first time the tool was pointed at the real
    source: no ``--fixtures``, so the configured location is read — and it had never been set.
    The run must stop as a configuration error naming the variable, not as an FR-008 partial
    export naming an export file, and it must stop *before* a request is constructed.
    """
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("WGC_DETAIL_SOURCE_URL", raising=False)

    code = main(["--repo", str(tmp_path)])

    assert code == int(ExitCode.CONFIG_ERROR)
    error = capsys.readouterr().err
    assert "WGC_DETAIL_SOURCE_URL" in error
    # The regression, stated as the thing that must not come back: the operator was told the
    # publisher had served a partial export when the publisher had not been contacted.
    assert "Abilities.csv" not in error
    assert "FR-008" not in error
    assert not (tmp_path / "reports").exists()


def test_a_live_run_in_csv_mode_fails_the_same_way(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`csv` is the default mode, so this is what an operator who set only the key actually got."""
    monkeypatch.setenv("WGC_MECHANIC_DIGEST_KEY", KEY)
    monkeypatch.delenv("WGC_DETAIL_ACQUISITION_MODE", raising=False)
    monkeypatch.delenv("WGC_DETAIL_SOURCE_URL", raising=False)

    code = main(["--repo", str(tmp_path)])

    assert code == int(ExitCode.CONFIG_ERROR)
    assert "WGC_DETAIL_SOURCE_URL" in capsys.readouterr().err


def test_the_report_lands_under_its_own_directory_and_not_beside_a_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`reports/candidate/` is the approver's view of a real run and is never written here."""
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)

    code = main(["--fixtures", str(FIXTURES), "--offline", "--repo", str(tmp_path)])

    assert code == int(ExitCode.SUCCESS)
    written = sorted((tmp_path / "reports" / "churn-dry-run").glob("*.md"))
    assert len(written) == 1
    assert not (tmp_path / "reports" / "candidate").exists()
