# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the IP-scan tests (task T047): the
# scanner over data/, curation/, reports/, state/ and the built bundle finds zero occurrences,
# and a deliberately poisoned tree fails with CON-IP-BOUNDARY.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added coverage for the report renderer's
# `<details>`/`<summary>` exemption (CI run 30939452542 on PR #1, candidate/mfm-2026-08's first
# committed report.md): pipeline/report/validation.py's collapsible sections are pipeline-
# authored formatting, not upstream data, and must not trip the "markup" violation class -- while
# any other tag in the same file still must.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the 006 loadout field families (006 task
# T036): itemName, modelName and eligibleModelName are poisoned one at a time, in the tree and in
# the built bundle, proving the pointer walk reaches fields nested three deep inside a datasheet
# and that no allowlist had to be updated for them to be covered.
"""Tests for validation V8, the scan that turns the IP boundary into a monitored control.

The schema design is what *makes* the boundary hold — there is no prose-typed field anywhere
downstream of normalize. This scan is the independent second mechanism (research D8), and the
poisoned-tree case is the part that matters: a scanner nobody has ever seen fail is a scanner
nobody knows works.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

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


# --- 004 T083: the enrichment's own fields, deliberately poisoned -------------------------------

#: One poisoned value per field family `004-rules-data-enrichment` adds, each carrying a different
#: violation class, so a scanner that silently stopped walking one of the new shapes is caught by
#: the field it stopped at rather than by an aggregate count.
POISONED_ENRICHMENT: dict[str, tuple[str, object]] = {
    "composition": (
        "data/wh40k-11e/factions/f-a/datasheets/ds-a.json",
        {"composition": [{"model_name": "Warden <sup>1</sup>", "count_min": 1, "count_max": 1}]},
    ),
    "option_choices": (
        "data/wh40k-11e/factions/f-a/datasheets/ds-b.json",
        {"option_groups": [{"choices": [{"label": "bolt pistol &amp; chainsword"}]}]},
    ),
    "chapter_keywords": (
        "data/wh40k-11e/chapter-keywords.json",
        [{"keyword": "Emberwrights", "chapter_id": "c-a", "note": "adds $CHAPTER$ to it"}],
    ),
    "faction_rules": (
        "curation/faction-rules/f-a.json",
        {
            "faction_id": "f-a",
            "army_rule_state": "present",
            "rules": [{"summary_key": "faction:f-a:x", "summary": "Special (правая колонка)"}],
        },
    ),
    "detachment_rules": (
        "curation/detachment-rules/f-a.json",
        [{"summary_key": "detachment:d-a:x", "summary": "See <i>the codex</i>."}],
    ),
    "glossary": (
        "curation/glossary.json",
        [{"summary_key": "glossary:x", "summary": "x" * (IP_SCAN_MAX_CHARS + 1)}],
    ),
}


@pytest.mark.parametrize("field", sorted(POISONED_ENRICHMENT))
def test_every_enrichment_field_family_is_scanned(field: str, temp_repo) -> None:  # type: ignore[no-untyped-def]
    """FR-039/SC-007 over the fields `004` added, one family at a time.

    The scan walks JSON structurally rather than by field name, so this is a proof that the new
    shapes are *reached* — a nested composition row, a choice two levels inside an option group,
    an object-wrapped rules array — not that each field was individually enumerated somewhere.
    Structure is what would break silently; a named list would only break loudly.
    """
    relative, payload = POISONED_ENRICHMENT[field]
    root = temp_repo()
    _write(root, relative, payload)

    findings = scan_repository(root)

    assert [f.finding_code for f in findings] == ["CON-IP-BOUNDARY"], field
    assert findings[0].detail["path"] == relative


@pytest.mark.parametrize("field", sorted(POISONED_ENRICHMENT))
def test_no_enrichment_finding_quotes_the_text_that_provoked_it(field: str, temp_repo) -> None:  # type: ignore[no-untyped-def]
    """The scanner names the violation class; it never becomes the thing it is guarding against."""
    relative, payload = POISONED_ENRICHMENT[field]
    root = temp_repo()
    _write(root, relative, payload)

    rendered = json.dumps(dict(scan_repository(root)[0].detail), ensure_ascii=False)

    for forbidden in ("codex", "правая", "CHAPTER", "chainsword", "<sup>"):
        assert forbidden not in rendered, f"{field} leaked {forbidden!r}"


# --- 006 T036: the loadout fields, deliberately poisoned ---------------------------------------

#: One poisoned value per field family `006-unit-loadout-fidelity` adds. The three the task names
#: — `item_name`, `model_name`, `eligible_model_name` — plus the equipment item, because it is a
#: *different* nesting (datasheet -> equipment_groups -> items) reached by a different branch of
#: the same walk.
#:
#: **Nesting depth is the point.** An option choice item sits four levels inside a datasheet file:
#: `option_groups[] -> choices[] -> items[] -> item_name`. A scanner that enumerated fields would
#: need a new entry for each of these; the pointer walk needed none, and this is the evidence for
#: that claim rather than a restatement of it.
POISONED_LOADOUT: dict[str, tuple[str, object]] = {
    "option_choice_items": (
        "data/wh40k-11e/factions/f-a/datasheets/ds-c.json",
        {
            "option_groups": [
                {"choices": [{"items": [{"item_name": "bolt pistol &amp; chainsword"}]}]}
            ]
        },
    ),
    "option_group_eligibility": (
        "data/wh40k-11e/factions/f-a/datasheets/ds-d.json",
        {"option_groups": [{"eligible_model_name": "Warden <sup>1</sup>"}]},
    ),
    "equipment_group_model_name": (
        "data/wh40k-11e/factions/f-a/datasheets/ds-e.json",
        {"equipment_groups": [{"model_name": "Sergeant (правая колонка)"}]},
    ),
    "equipment_items": (
        "data/wh40k-11e/factions/f-a/datasheets/ds-f.json",
        {"equipment_groups": [{"items": [{"item_name": "x" * (IP_SCAN_MAX_CHARS + 1)}]}]},
    ),
}


@pytest.mark.parametrize("field", sorted(POISONED_LOADOUT))
def test_every_loadout_field_family_is_scanned(field: str, temp_repo) -> None:  # type: ignore[no-untyped-def]
    """FR-023 over the fields `006` adds, one family at a time, with no allowlist update."""
    relative, payload = POISONED_LOADOUT[field]
    root = temp_repo()
    _write(root, relative, payload)

    findings = scan_repository(root)

    assert [f.finding_code for f in findings] == ["CON-IP-BOUNDARY"], field
    assert findings[0].detail["path"] == relative


@pytest.mark.parametrize("field", sorted(POISONED_LOADOUT))
def test_no_loadout_finding_quotes_the_text_that_provoked_it(field: str, temp_repo) -> None:  # type: ignore[no-untyped-def]
    relative, payload = POISONED_LOADOUT[field]
    root = temp_repo()
    _write(root, relative, payload)

    rendered = json.dumps(dict(scan_repository(root)[0].detail), ensure_ascii=False)

    for forbidden in ("chainsword", "<sup>", "правая", "xxxx"):
        assert forbidden not in rendered, f"{field} leaked {forbidden!r}"


def test_the_loadout_bundle_is_scanned_clean_before_it_is_ever_written() -> None:
    """The in-memory bundle path covers the three new arrays too, and finds nothing in them."""
    from pipeline.build.bundle_emit import emit_bundle
    from tests import factories
    from tests.contract.loadout_bundle import loadout_snapshot

    bundle = emit_bundle(loadout_snapshot(), factories.meta())

    assert bundle["datasheetOptionChoiceItems"], "an empty array proves nothing"
    assert bundle["datasheetEquipmentItems"], "an empty array proves nothing"
    assert scan_bundle(bundle) == []


@pytest.mark.parametrize(
    ("array", "column"),
    [
        ("datasheetOptionChoiceItems", "itemName"),
        ("datasheetEquipmentItems", "itemName"),
        ("datasheetEquipmentGroups", "modelName"),
        ("datasheetOptionGroups", "eligibleModelName"),
    ],
)
def test_a_poisoned_new_column_is_caught_the_moment_it_is_emitted(array: str, column: str) -> None:
    """The bundle scan reaches each new column by pointer, so emission is when it is covered.

    Not "when someone remembers to add it to a list": the same test written against an enumerated
    allowlist would pass while the allowlist was stale, which is the failure mode this scan exists
    to be immune to.
    """
    from pipeline.build.bundle_emit import emit_bundle
    from tests import factories
    from tests.contract.loadout_bundle import loadout_snapshot

    bundle = emit_bundle(loadout_snapshot(), factories.meta())
    poisoned = {**bundle, array: [{**bundle[array][0], column: "<b>x</b>"}, *bundle[array][1:]]}

    (finding,) = scan_bundle(poisoned)

    assert finding.finding_code == "CON-IP-BOUNDARY"
    assert finding.detail["violation"] == "markup"
    assert column in str(finding.detail["pointer"])
