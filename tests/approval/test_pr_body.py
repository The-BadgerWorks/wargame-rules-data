# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote coverage for the candidate reviewer
# view (task T119): the PR body opens with the verdict and scale, orders every sub-report in the
# approver's reading order, and points at the changed-file list (FR-037).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the loadout coverage table and the
# option-regression pointer (006 task T039): both figures get a row, the table says which of them
# a gate is actually watching, and the FR-009 evidence link is stated whether or not the file
# exists -- its absence is what an approver is meant to notice.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 008 task T062: `default_equipment` now
# reports a real, non-zero threshold (the two-step ratchet, FR-021) rather than the first-extended-
# release `reported only` state -- the fixture and its assertions moved to reflect that, and an
# unratcheted `item_constraints` row was added so the "which figure can refuse" distinction still
# has an unratcheted example to point at.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R06a-fix item 3: added receipts for the
# bulk-arm-vs-per-faction `unused` rendering split. Confirmed red against the pre-fix
# `_carried_forward_section`, which rendered "may be retired" for every `unused` finding
# regardless of `detail` (see each test's own docstring).
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
                "current": 1680,
                "previous": 1664,
                "ratio_percent": 99,
                "threshold": 0.97,
            },
            "loadout.item_constraints": {
                "current": 120,
                "previous": 110,
                "ratio_percent": 80,
                "threshold": 0.0,
            },
        }
    )


def test_both_loadout_figures_get_their_own_row() -> None:
    body = render_pr_body(_loadout_json())

    assert "## Loadout coverage" in body
    assert "| `options_resolved` | 402 | 380 | 19% | blocks below 18% |" in body
    assert "| `default_equipment` | 1680 | 1664 | 99% | blocks below 97% |" in body


def test_the_table_says_which_figure_can_refuse_a_release() -> None:
    """A falling unratcheted number must not read as one a gate has already considered.

    `item_constraints` (unratcheted — `007` FR-022, PO decision 2026-08-13) beside
    `options_resolved`/`default_equipment` (both ratcheted, `008` FR-021's two-step ruling) is
    what lets an approver tell the two apart in the table itself, without knowing the tolerance
    configuration.
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


# -- carried-forward factions (008 FR-025, Product Owner decision 2026-08-17) --------------------


def _carried_forward_finding(**overrides):  # type: ignore[no-untyped-def]
    base = {
        "finding_code": "SRC-FACTION-CARRIED-FORWARD",
        "finding_class": "reconciliation",
        "severity": "advisory",
        "entity_refs": ["faction:f-tau-empire"],
        "detail": {
            "faction_id": "f-tau-empire",
            "faction_slug": "tau-empire",
            "frozen_at_version": "wh40k-11e-2026-08-3",
            "datasheets_carried": 42,
        },
    }
    base.update(overrides)
    return base


def test_a_carried_faction_gets_its_own_prominent_section() -> None:
    body = render_pr_body(_report_json(findings=[_carried_forward_finding()]))
    section = body.split("## Carried-forward factions", 1)[1].split("##", 1)[0]
    assert "f-tau-empire" in section
    assert "wh40k-11e-2026-08-3" in section
    assert "42" in section


def test_an_unused_declaration_is_named_separately_from_a_carried_one() -> None:
    unused = _carried_forward_finding(
        finding_code="SRC-FACTION-CARRY-FORWARD-UNUSED",
        detail={"faction_id": "f-tau-empire", "faction_slug": "tau-empire"},
    )
    body = render_pr_body(_report_json(findings=[unused]))
    section = body.split("## Carried-forward factions", 1)[1].split("##", 1)[0]
    assert "not needed this run" in section
    assert "tau-empire" in section


# -- R06a-fix item 3: a bulk-arm `unused` finding must not advise retirement ---------------------


def test_an_html_arm_unused_declaration_still_advises_retirement() -> None:
    """`answers_per_faction: True` (or absent, for an older report) is a genuine per-faction
    fetch answering live -- the existing "may be retired" advice is correct and must stay."""
    unused = _carried_forward_finding(
        finding_code="SRC-FACTION-CARRY-FORWARD-UNUSED",
        detail={
            "faction_id": "f-tau-empire",
            "faction_slug": "tau-empire",
            "answers_per_faction": True,
        },
    )
    body = render_pr_body(_report_json(findings=[unused]))
    section = body.split("## Carried-forward factions", 1)[1].split("##", 1)[0]
    assert "may be retired" in section
    assert "tau-empire" in section


def test_a_bulk_arm_unused_declaration_never_advises_retirement() -> None:
    """R06a-fix item 3: "this arm cannot answer per-faction at all" and "this faction answered
    live, so retire the declaration" are opposite facts. Under a bulk arm (`answers_per_faction:
    False`), `unused` is not evidence any one faction's own page is reachable -- acting on
    retirement advice here would delete the declaration that stops the per-faction sweep
    hard-failing once the arm returns to it. Confirmed red against `render_pr_body` before this
    fix: the ONLY branch was the "may be retired" text, rendered for every `unused` finding
    regardless of `detail`."""
    unused = _carried_forward_finding(
        finding_code="SRC-FACTION-CARRY-FORWARD-UNUSED",
        detail={
            "faction_id": "f-tau-empire",
            "faction_slug": "tau-empire",
            "answers_per_faction": False,
        },
    )
    body = render_pr_body(_report_json(findings=[unused]))
    section = body.split("## Carried-forward factions", 1)[1].split("##", 1)[0]
    assert "may be retired" not in section
    assert "do not retire" in section.lower()
    assert "tau-empire" in section


def test_html_and_bulk_unused_declarations_are_rendered_separately_in_one_report() -> None:
    """A run could plausibly report both in principle (though not today, since one run has one
    configured arm) -- if it ever does, each slug's own advice must follow its own evidence."""
    per_faction = _carried_forward_finding(
        finding_code="SRC-FACTION-CARRY-FORWARD-UNUSED",
        detail={
            "faction_id": "f-tau-empire",
            "faction_slug": "tau-empire",
            "answers_per_faction": True,
        },
    )
    bulk = _carried_forward_finding(
        finding_code="SRC-FACTION-CARRY-FORWARD-UNUSED",
        detail={
            "faction_id": "f-drukhari",
            "faction_slug": "drukhari",
            "answers_per_faction": False,
        },
    )
    body = render_pr_body(_report_json(findings=[per_faction, bulk]))
    section = body.split("## Carried-forward factions", 1)[1].split("##", 1)[0]
    retire_line = next(line for line in section.splitlines() if "tau-empire" in line)
    keep_line = next(line for line in section.splitlines() if "drukhari" in line)
    assert retire_line != keep_line


# AI-Assisted: Claude Code (model: claude-sonnet-5) - R06a-fix item 4: added receipts for the
# per-class-vs-whole-faction `SRC-FACTION-CARRIED-FORWARD` rendering split. Confirmed red: before
# `_carried_line` read `data_class`, a four-field freeze rendered indistinguishably from a
# whole-faction freeze of N datasheets.
# -- R06a-fix item 4: a per-class freeze must not read as a whole-faction freeze -----------------


def test_a_whole_faction_freeze_reads_as_the_whole_datasheet() -> None:
    body = render_pr_body(_report_json(findings=[_carried_forward_finding()]))
    section = body.split("## Carried-forward factions", 1)[1].split("##", 1)[0]
    assert "class only" not in section


def test_a_per_class_freeze_names_which_class_not_the_whole_datasheet() -> None:
    """R06a-fix item 4: the per-class `SRC-FACTION-CARRIED-FORWARD` reuses the whole-faction
    detail shape (`faction_id`, `frozen_at_version`, `datasheets_carried`) plus `data_class` --
    the predecessor's own addition. Before this fix the rendering never read `data_class`, so a
    four-field freeze of one datasheet rendered indistinguishably from a whole-faction freeze of
    N datasheets. Confirmed red: `"options"` and `"class"` were absent from the rendered section
    for this exact finding before `_carried_line` was taught to read `data_class`."""
    finding = _carried_forward_finding(
        detail={
            "faction_id": "f-tau-empire",
            "faction_slug": "tau-empire",
            "frozen_at_version": "wh40k-11e-2026-08-3",
            "datasheets_carried": 1,
            "data_class": "options",
        }
    )
    body = render_pr_body(_report_json(findings=[finding]))
    section = body.split("## Carried-forward factions", 1)[1].split("##", 1)[0]
    assert "options" in section
    assert "class only" in section
    assert "f-tau-empire" in section


def test_no_carried_forward_section_when_nothing_was_substituted() -> None:
    """Absence is itself the signal — a clean report with no declarations active gets no section
    at all, the same discipline the option-regression link's own test file documents."""
    assert "Carried-forward factions" not in render_pr_body(_report_json())
