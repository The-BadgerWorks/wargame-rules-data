# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the IP-scan tests (task T047): the
# scanner over data/, curation/, reports/, state/ and the built bundle finds zero occurrences,
# and a deliberately poisoned tree fails with CON-IP-BOUNDARY.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added coverage for the report renderer's
# `<details>`/`<summary>` exemption (CI run 30939452542 on PR #1, candidate/mfm-2026-08's first
# committed report.md): pipeline/report/validation.py's collapsible sections are pipeline-
# authored formatting, not upstream data, and must not trip the "markup" violation class -- while
# any other tag in the same file still must.
"""Tests for validation V8, the scan that turns the IP boundary into a monitored control.

The schema design is what *makes* the boundary hold — there is no prose-typed field anywhere
downstream of normalize. This scan is the independent second mechanism (research D8), and the
poisoned-tree case is the part that matters: a scanner nobody has ever seen fail is a scanner
nobody knows works.
"""

from __future__ import annotations

import json
from pathlib import Path

from pipeline.validate.ip_scan import (
    IP_SCAN_MAX_CHARS,
    SCANNED_DIRECTORIES,
    scan_bundle,
    scan_repository,
)


def _write(root: Path, relative: str, payload: object) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_text(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_the_scanner_covers_every_directory_the_requirement_names() -> None:
    assert set(SCANNED_DIRECTORIES) == {"data", "curation", "reports", "state"}


def test_a_clean_tree_yields_no_findings(temp_repo) -> None:  # type: ignore[no-untyped-def]
    root = temp_repo()
    _write(root, "data/wh40k-11e/factions.json", [{"faction_id": "f-a", "name": "Emberwrights"}])
    _write(root, "curation/game-sizes.json", [{"id": "gs-1", "label": "Incursion"}])
    _write(root, "state/detection-digest.json", {"per_faction": {}, "release_digest": None})

    assert scan_repository(root) == []


def test_the_real_repository_is_clean() -> None:
    """The scan CI runs on every PR (SC-003). If this fails, something landed that must not."""
    repo_root = Path(__file__).resolve().parents[2]
    assert scan_repository(repo_root) == []


def test_markup_in_a_curated_file_is_a_blocking_boundary_finding(temp_repo) -> None:  # type: ignore[no-untyped-def]
    root = temp_repo()
    _write(root, "data/wh40k-11e/factions.json", [{"name": "<span class='kwb'>x</span>"}])

    (finding,) = scan_repository(root)
    assert finding.finding_code == "CON-IP-BOUNDARY"
    assert finding.severity == "blocking"
    assert finding.detail["violation"] == "markup"
    assert finding.detail["path"] == "data/wh40k-11e/factions.json"


def test_the_finding_names_the_violation_class_and_never_the_offending_text(temp_repo) -> None:  # type: ignore[no-untyped-def]
    root = temp_repo()
    _write(root, "reports/x/report.json", {"note": "<b>quote-me-if-you-dare</b>"})

    (finding,) = scan_repository(root)
    rendered = json.dumps(dict(finding.detail), ensure_ascii=False)
    assert "quote-me-if-you-dare" not in rendered


def test_each_violation_class_is_detected(temp_repo) -> None:  # type: ignore[no-untyped-def]
    cases = {
        "markup": "<i>x</i>",
        "html_entity": "a &amp; b",
        "placeholder_token": "adds $BONUS$ to it",
        "cyrillic": "Special (правая колонка)",
        # Pinned to the constant, not to a literal: the ceiling moved 400 -> 1 000 with the
        # Product Owner's 2026-08-06 summary-length decision, and a hard-coded 401 silently
        # stopped exercising this branch rather than failing.
        "over_length": "x" * (IP_SCAN_MAX_CHARS + 1),
    }
    for violation, payload in cases.items():
        root = temp_repo()
        _write(root, "curation/abilities/f-a.json", [{"summary": payload}])
        findings = scan_repository(root)
        assert [f.detail["violation"] for f in findings] == [violation], violation


def test_a_file_under_work_is_itself_a_violation(temp_repo) -> None:  # type: ignore[no-untyped-def]
    root = temp_repo()
    (root / "work").mkdir(parents=True, exist_ok=True)
    (root / "work" / "leftover.html").write_text("anything", encoding="utf-8")

    findings = scan_repository(root)
    assert [f.detail["violation"] for f in findings] == ["work_not_empty"]


def test_the_built_bundle_is_scanned_too() -> None:
    clean = {"datasheets": [{"id": "ds-a", "name": "Ember Sentinel"}]}
    assert scan_bundle(clean) == []

    poisoned = {"datasheetAbilities": [{"summary": "See <b>page 42</b>."}]}
    (finding,) = scan_bundle(poisoned)
    assert finding.finding_code == "CON-IP-BOUNDARY"


def test_keys_are_scanned_as_well_as_values() -> None:
    (finding,) = scan_bundle({"<script>": 1})
    assert finding.detail["violation"] == "markup"


def test_a_bare_ampersand_or_dollar_sign_is_not_a_false_positive() -> None:
    assert scan_bundle({"name": "Fire & Fury costs $"}) == []


def test_the_report_renderers_own_collapsible_sections_are_not_a_false_positive(
    temp_repo,  # type: ignore[no-untyped-def]
) -> None:
    """`pipeline/report/validation.py`'s `render_report_markdown` wraps each findings class in
    `<details><summary>...</summary>` / `</details>` so a report with thousands of rows stays
    readable. That is pipeline-authored formatting, not upstream data, and must not be what
    "markup" flags -- every real build with any findings emits exactly this."""
    root = temp_repo()
    _write_text(
        root,
        "reports/fixture-minimal/report.md",
        "## All findings\n\n"
        "<details><summary>contract (3)</summary>\n\n"
        "| code | severity |\n|---|---|\n"
        "| `CON-WARGEAR-COST-MISSING` | advisory |\n\n"
        "</details>\n",
    )

    assert scan_repository(root) == []


def test_a_genuine_tag_in_a_report_markdown_file_is_still_caught(
    temp_repo,  # type: ignore[no-untyped-def]
) -> None:
    """The `<details>`/`<summary>` exemption is narrow: anything else still trips "markup", even
    inside `reports/`."""
    root = temp_repo()
    _write_text(root, "reports/fixture-minimal/report.md", "See <span class='kwb'>this</span>.")

    (finding,) = scan_repository(root)
    assert finding.detail["violation"] == "markup"
    assert finding.detail["path"] == "reports/fixture-minimal/report.md"
