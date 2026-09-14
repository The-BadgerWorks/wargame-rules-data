# AI-Assisted: Claude Code (model: Claude Opus 5) - Receipts for the 010 R6 parity tool: the
# candidate CSV build publishes different field content from the published tree and no tool in
# this repository compared them field by field. These tests pin the three behaviours that make
# such a comparison trustworthy - that a printed-suffix-only difference is classified as format
# and not as content, that two identical trees produce an all-zero report (anti-vacuity, so a
# green reading cannot come from a comparison that never ran), and that the rendered markdown
# carries no name or keyword out of the trees it read.
"""Unit tests for :mod:`tools.compare_published_tree`.

Every string in the synthetic trees below is invented. `ds-fen-warden`, `tide axe` and
`FEN WARDENS` name nothing the publisher publishes, which is the only form a fixture in this
repository is permitted to take.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.compare_published_tree import compare_trees

FACTION = "f-fen"
DATASHEET = "ds-fen-warden-1"


def _datasheet(*, skill: str, weapon_range: str, keyword: str, ability_keys: list[str]) -> Any:
    return {
        "datasheet_id": DATASHEET,
        "faction_id": FACTION,
        "name": "Fen Warden",
        "ability_keys": ability_keys,
        "keywords": [{"keyword": keyword, "is_faction_keyword": False}],
        "models": [
            {
                "name": "Fen Warden",
                "line": 1,
                "movement": '6"',
                "toughness": "4",
                "save": "3+",
                "invuln_save": None,
                "wounds": "2",
                "leadership": "6+",
                "objective_control": "1",
                "base_size": "32mm",
            }
        ],
        "weapons": [
            {
                "name": "tide axe",
                "is_melee": True,
                "line": 1,
                "range": weapon_range,
                "attacks": "3",
                "skill": skill,
                "strength": "5",
                "armour_penetration": "1",
                "damage": "2",
                "ability_keywords": [],
            }
        ],
        "costs": [{"label": "1 model", "points": 20, "source_acquisition_id": "acq-a"}],
        "pricing_confidence": "exact",
        "provenance": {"run_id": "run-a"},
    }


def _write_tree(root: Path, payload: Any) -> Path:
    directory = root / "wh40k-11e" / "factions" / FACTION / "datasheets"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{DATASHEET}.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8", newline="\n"
    )
    return root


def _tree_a(root: Path) -> Path:
    return _write_tree(
        root,
        _datasheet(
            skill="3+",
            weapon_range='12"',
            keyword="FEN WARDENS",
            ability_keys=["core:deep-strike", "datasheet:tidal-surge"],
        ),
    )


def _tree_b(root: Path) -> Path:
    return _write_tree(
        root,
        _datasheet(
            skill="3",
            weapon_range="12",
            keyword="Fen Wardens",
            ability_keys=["datasheet:tidal-surge"],
        ),
    )


def test_printed_suffix_and_case_differences_are_classified_not_counted_as_content(
    tmp_path: Path,
) -> None:
    """A `3+` vs `3` skill is a printed-suffix difference, not a different characteristic.

    Fails if the tool stops distinguishing format from content: `weapon_format_only` drops to
    zero and the same pair reappears under `weapon_field_diffs`, which would read as the
    candidate having changed a stat it did not change.
    """
    report = compare_trees(_tree_a(tmp_path / "a"), _tree_b(tmp_path / "b"))

    assert report.shared == 1
    assert report.identical == 0
    assert report.weapon_format_only == {"skill": 1, "range": 1}
    assert report.weapons_paired == 1
    assert report.weapon_field_diffs.get("skill", 0) == 0
    assert report.weapon_field_diffs.get("range", 0) == 0
    assert report.keywords_case_only == 1
    assert report.keywords_set_differs == 0
    assert report.ability_keys_only_published == {"core": 1}
    assert report.ability_keys_only_candidate == {}


def test_two_identical_trees_report_every_counter_zero(tmp_path: Path) -> None:
    """Anti-vacuity: a comparison that never ran would also report no differences.

    Fails if the tool reports a difference between a tree and its own copy - which is how a
    broken pairing rule, a mis-stripped exclusion or a path-keying mistake shows up.
    """
    report = compare_trees(_tree_a(tmp_path / "a"), _tree_a(tmp_path / "b"))

    assert report.shared == 1
    assert report.identical == 1
    assert report.only_published == 0
    assert report.only_candidate == 0
    assert report.top_level == {}
    assert report.keywords_case_only == 0
    assert report.keywords_set_differs == 0
    assert report.keywords_missing == 0
    assert report.keywords_extra == 0
    assert report.ability_keys_only_published == {}
    assert report.ability_keys_only_candidate == {}
    assert report.weapons_paired == 1
    assert report.weapons_only_published == {}
    assert report.weapons_only_candidate == {}
    assert report.weapon_field_diffs == {}
    assert report.weapon_format_only == {}
    assert report.models_count_differs == 0
    assert report.model_field_diffs == {}
    assert report.names_case_only == 0
    assert report.names_differ == 0


def test_markdown_carries_no_name_or_keyword_out_of_either_tree(tmp_path: Path) -> None:
    """The report is counts and stat shapes. Fails the moment a cell leaks into it."""
    report = compare_trees(_tree_a(tmp_path / "a"), _tree_b(tmp_path / "b"))
    markdown = report.to_markdown()

    assert "tide axe" not in markdown
    assert "Fen Wardens" not in markdown
    assert "FEN WARDENS" not in markdown
    assert "Fen Warden" not in markdown
