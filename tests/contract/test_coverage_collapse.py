# AI-Assisted: Claude Code (model: claude-opus-5) - Coverage-collapse tests (task T086): a
# partial or error response that parses cleanly but drops faction, datasheet, or priced-datasheet
# counts below the configured ratios raises the blocking COV-COLLAPSE and exits 42 without
# publishing (FR-009, V10).
"""V10 — coverage against the previous published version.

The failure this catches is the quiet one. A partial response, or an error page that happens to
be well-formed, produces a snapshot in which *every value is correct* — it simply contains a
fraction of the release. Nothing downstream can tell: the parser is happy, the guarantees hold,
the bundle builds and its checksum is perfectly reproducible. Only the comparison against what
was published last time reveals it, which is why this check lands in US2 rather than US1: US1 has
no previous published version by definition.
"""

from __future__ import annotations

from pathlib import Path

from pipeline.cli import run_build
from pipeline.config import load_config
from pipeline.curate.prior import load_prior, prior_from_snapshot
from pipeline.exit_codes import ExitCode
from pipeline.validate.coverage import check_coverage
from tests import factories

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def snapshot_of(*, factions: int, datasheets: int, priced: int):
    faction_rows = [factories.faction(f"f-{index}") for index in range(factions)]
    datasheet_rows = [
        factories.datasheet(
            f"ds-{index}",
            faction_id="f-0",
            cost_rows=factories.costs(((1, 1, 60),)) if index < priced else [],
        )
        for index in range(datasheets)
    ]
    return factories.snapshot(factions=faction_rows, datasheets=datasheet_rows)


def test_unchanged_coverage_reports_nothing_and_still_states_the_figures() -> None:
    config = load_config(env={})
    baseline = snapshot_of(factions=3, datasheets=12, priced=12)
    prior = prior_from_snapshot(baseline, rules_version_id="mfm-2026-05")

    outcome = check_coverage(snapshot_of(factions=3, datasheets=12, priced=12), prior, config)

    assert outcome.findings == []
    assert not outcome.collapsed
    assert outcome.figures["factions"].ratio == 1.0
    assert outcome.figures["datasheets"].previous == 12
    assert set(outcome.figures) == {"factions", "datasheets", "priced_datasheets"}


def test_a_small_drop_inside_the_configured_ratios_is_not_a_collapse() -> None:
    config = load_config(env={})
    prior = prior_from_snapshot(
        snapshot_of(factions=3, datasheets=12, priced=12), rules_version_id="mfm-2026-05"
    )

    outcome = check_coverage(snapshot_of(factions=3, datasheets=11, priced=11), prior, config)

    assert outcome.findings == []
    assert round(outcome.figures["datasheets"].ratio, 4) == 0.9167


def test_a_faction_collapse_is_blocking_and_exits_42() -> None:
    config = load_config(env={})
    prior = prior_from_snapshot(
        snapshot_of(factions=3, datasheets=12, priced=12), rules_version_id="mfm-2026-05"
    )

    outcome = check_coverage(snapshot_of(factions=1, datasheets=12, priced=12), prior, config)

    assert [f.finding_code for f in outcome.findings] == ["COV-COLLAPSE"]
    assert outcome.findings[0].severity.value == "blocking"
    assert outcome.findings[0].detail["category"] == "factions"
    assert outcome.collapsed
    assert outcome.exit_code is ExitCode.COVERAGE_COLLAPSE


def test_a_datasheet_collapse_is_reported_per_category() -> None:
    config = load_config(env={})
    prior = prior_from_snapshot(
        snapshot_of(factions=3, datasheets=12, priced=12), rules_version_id="mfm-2026-05"
    )

    outcome = check_coverage(snapshot_of(factions=3, datasheets=2, priced=2), prior, config)

    categories = sorted(str(f.detail["category"]) for f in outcome.findings)
    assert categories == ["datasheets", "priced_datasheets"]


def test_no_previous_published_version_cannot_collapse() -> None:
    config = load_config(env={})

    outcome = check_coverage(snapshot_of(factions=1, datasheets=1, priced=1), None, config)

    assert outcome.findings == []
    assert outcome.figures == {}, "there is nothing to compare a first release against"


def test_the_baseline_is_read_from_a_checkout_without_acquiring_anything() -> None:
    prior = load_prior(FIXTURES / "disagreements" / "previous", edition_code="wh40k-11e")

    assert prior is not None
    assert prior.rules_version_id == "mfm-2026-05"
    assert prior.faction_count == 3
    assert prior.datasheet_count == prior.priced_datasheet_count == 11


def test_the_partial_page_fixture_exits_42_without_publishing(tmp_path: Path) -> None:
    """The end-to-end case: a page that parses cleanly and still loses most of the release."""
    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-collapsed",
        fixtures_dir=FIXTURES / "disagreements" / "collapsed",
        prior_dir=FIXTURES / "disagreements" / "previous",
        offline=True,
        output_root=tmp_path / "out",
        reports_root=tmp_path,
        published_at="2026-08-02T00:00:00Z",
    )

    assert result.exit_code is ExitCode.COVERAGE_COLLAPSE
    assert result.coverage.collapsed
    assert {
        str(f.detail["category"]) for f in result.findings if f.finding_code == "COV-COLLAPSE"
    } == {
        "factions",
        "datasheets",
        "priced_datasheets",
    }
    assert not list((tmp_path / "out").rglob("manifest.json")), "exit 42 never publishes"
    assert (result.report_path / "report.json").is_file(), "the report is written regardless"
