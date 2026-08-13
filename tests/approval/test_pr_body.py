# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote coverage for the candidate reviewer
# view (task T119): the PR body opens with the verdict and scale, orders every sub-report in the
# approver's reading order, and points at the changed-file list (FR-037).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the loadout coverage table and the
# option-regression pointer (006 task T039): both figures get a row, the table says which of them
# a gate is actually watching, and the FR-009 evidence link is stated whether or not the file
# exists -- its absence is what an approver is meant to notice.
"""Tests for `pipeline.report.pr_body` — the PR body a candidate opens with (FR-037)."""

from __future__ import annotations

from pipeline.report.pr_body import READING_ORDER, render_pr_body
from pipeline.report.validation import SUB_REPORT_FILES, report_json
from tests import factories


def _report_json(**overrides):  # type: ignore[no-untyped-def]
    from pipeline.report.validation import build_report

    report = build_report(
        run_id="local-candidate-2026-01",
        rules_version_id="candidate-2026-01",
        channel="prerelease",
        generated_at="2026-06-13T12:00:00Z",
        acquisitions=[],
        coverage={},
        snapshot=factories.snapshot(),
        findings=[],
    )
    document = report_json(report)
    document.update(overrides)
    return document


def test_the_body_opens_with_the_candidate_id_and_the_verdict_line() -> None:
    body = render_pr_body(_report_json())
    assert "candidate-2026-01" in body.splitlines()[0]
    assert "CLEAN" in body


def test_the_body_names_no_blocking_findings_for_a_clean_report() -> None:
    body = render_pr_body(_report_json())
    assert "## Blocking findings" in body
    assert "None." in body


def test_the_body_lists_every_sub_report_in_the_approvers_reading_order() -> None:
    body = render_pr_body(_report_json())
    positions = [body.index(SUB_REPORT_FILES[key]) for key in READING_ORDER]
    assert positions == sorted(positions), "sub-reports must appear in the declared reading order"


def test_the_body_points_at_the_changed_file_list() -> None:
    body = render_pr_body(_report_json())
    assert "Files changed" in body
    assert "datasheets" in body


def test_the_reports_directory_defaults_to_the_rules_version_id() -> None:
    body = render_pr_body(_report_json())
    assert "reports/candidate-2026-01/change-summary.md" in body


def test_a_custom_reports_directory_is_honoured() -> None:
    body = render_pr_body(_report_json(), reports_relative_dir="fixtures/minimal/build/reports")
    assert "fixtures/minimal/build/reports/change-summary.md" in body


# --- 004 T084: the four classes' coverage, and the churn dry-run reference ----------------------


def _coverage_json():  # type: ignore[no-untyped-def]
    return _report_json(
        coverage={
            "datasheets": {"current": 10, "previous": 10, "ratio_percent": 100},
            "summaries.abilities": {"current": 1934, "previous": 1900, "ratio_percent": 100},
            "summaries.detachment_rules": {"current": 324, "previous": 0, "ratio_percent": 100},
            "summaries.faction_rules": {"current": 28, "previous": 0, "ratio_percent": 100},
            "summaries.glossary": {"current": 70, "previous": 0, "ratio_percent": 5},
        }
    )


def test_all_four_summary_classes_get_their_own_row() -> None:
    body = render_pr_body(_coverage_json())

    assert "## Authored summary coverage" in body
    for name in ("abilities", "detachment_rules", "faction_rules", "glossary"):
        assert f"`{name}`" in body


def test_a_short_class_shows_its_figure_rather_than_being_rounded_away() -> None:
    """The glossary at 5% is the whole reason this table exists — it must be legible as 5%."""
    body = render_pr_body(_coverage_json())

    assert "| `glossary` | 70 | 0 | 5% |" in body


def test_a_non_summary_coverage_figure_stays_out_of_this_table() -> None:
    """`datasheets` belongs to Scale's question, not this one."""
    body = render_pr_body(_coverage_json())
    table = body.split("## Authored summary coverage", 1)[1].split("##", 1)[0]

    assert "datasheets" not in table


def test_the_body_points_at_the_churn_dry_run() -> None:
    body = render_pr_body(_coverage_json())
    assert "reports/churn-dry-run" in body


def test_a_report_carrying_no_summary_coverage_omits_the_table_entirely() -> None:
    """An empty table reads as "no summaries", a different claim from "not measured"."""
    body = render_pr_body(_report_json(coverage={}))
    assert "## Authored summary coverage" not in body


# --- 006 T039: the two loadout figures, and the option-regression pointer ------------------------


def _loadout_json():  # type: ignore[no-untyped-def]
    return _report_json(
        coverage={
            "datasheets": {"current": 10, "previous": 10, "ratio_percent": 100},
            "summaries.abilities": {"current": 1934, "previous": 1900, "ratio_percent": 100},
            "loadout.options_resolved": {
                "current": 402,
                "previous": 380,
                "ratio_percent": 19,
                "threshold": 0.18,
            },
            "loadout.default_equipment": {
                "current": 1664,
                "previous": 0,
                "ratio_percent": 99,
                "threshold": 0.0,
            },
        }
    )


def test_both_loadout_figures_get_their_own_row() -> None:
    body = render_pr_body(_loadout_json())

    assert "## Loadout coverage" in body
    assert "| `options_resolved` | 402 | 380 | 19% | blocks below 18% |" in body
    assert "| `default_equipment` | 1664 | 0 | 99% | reported only |" in body


def test_the_table_says_which_figure_can_refuse_a_release() -> None:
    """A falling unratcheted number must not read as one a gate has already considered.

    `default_equipment` at 99% and `options_resolved` at 19% is the shape of the first extended
    release, and an approver who cannot tell which of the two a gate is watching is being asked
    to approve on the wrong information.
    """
    table = render_pr_body(_loadout_json()).split("## Loadout coverage", 1)[1].split("##", 1)[0]

    assert "reported only" in table
    assert "blocks below" in table


def test_the_loadout_table_is_separate_from_the_authored_summary_one() -> None:
    """Different questions: editorial backlog a curator works through, versus what parsed."""
    body = render_pr_body(_loadout_json())
    summary_table = body.split("## Authored summary coverage", 1)[1].split("##", 1)[0]
    loadout_table = body.split("## Loadout coverage", 1)[1].split("##", 1)[0]

    assert "options_resolved" not in summary_table
    assert "abilities" not in loadout_table
    assert "datasheets" not in loadout_table


def test_a_report_carrying_no_loadout_coverage_omits_the_table_entirely() -> None:
    """An empty table reads as "nothing resolved", a different claim from "not measured"."""
    assert "## Loadout coverage" not in render_pr_body(_report_json(coverage={}))


def test_the_body_points_at_the_option_regression_evidence() -> None:
    """FR-022: the zero-regression evidence is named, not left to whoever remembers it exists."""
    body = render_pr_body(_loadout_json())

    assert "reports/candidate-2026-01/option-regression.md" in body
    assert "Corrected" in body


def test_the_option_regression_link_is_stated_even_for_a_clean_report() -> None:
    """Its absence on disk is itself something an approver is meant to notice.

    `rules-pipeline option-regression` is evidence tooling and deliberately not on the
    approval-gate path, so nothing in a build guarantees the file exists. A link that appeared
    only when the file did would quietly turn "nobody ran it" into "there was nothing to say".
    """
    assert "option-regression.md" in render_pr_body(_report_json(coverage={}))
