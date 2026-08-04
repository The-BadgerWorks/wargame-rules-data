# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote coverage for the candidate reviewer
# view (task T119): the PR body opens with the verdict and scale, orders every sub-report in the
# approver's reading order, and points at the changed-file list (FR-037).
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
