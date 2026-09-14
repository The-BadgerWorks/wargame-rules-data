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

from tools.compare_published_tree import USAGE_EXIT, compare_trees, main

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
    assert report.weapon_samples == {}


def test_markdown_carries_no_name_or_keyword_out_of_either_tree(tmp_path: Path) -> None:
    """The report is counts and stat shapes. Fails the moment a cell leaks into it."""
    report = compare_trees(_tree_a(tmp_path / "a"), _tree_b(tmp_path / "b"))
    markdown = report.to_markdown()

    assert "tide axe" not in markdown
    assert "Fen Wardens" not in markdown
    assert "FEN WARDENS" not in markdown
    assert "Fen Warden" not in markdown


def test_a_root_one_directory_too_high_is_a_usage_error_not_an_all_zero_report(
    tmp_path: Path, capsys: Any
) -> None:
    """A mis-aimed root must not read as a comparison that found nothing.

    This is CLAUDE.md trap 1 on the output side: `factions/` absent loads zero datasheets, and
    without this branch the tool prints a full report of zeros and exits 0 - indistinguishable
    from a genuine comparison of two empty trees. Fails if the diagnostic or the non-zero exit
    is removed: the exit drops to 0 and a markdown report appears on stdout.
    """
    _tree_a(tmp_path / "a")
    _tree_a(tmp_path / "b")

    # One directory too high: `tmp_path` holds `a/` and `b/`, neither of which is `factions/`.
    exit_code = main(["--published", str(tmp_path), "--candidate", str(tmp_path / "b")])

    captured = capsys.readouterr()
    assert exit_code == USAGE_EXIT
    assert exit_code != 0
    assert "Published-vs-candidate field parity" not in captured.out
    assert "| 0 | 0 | 0 | 0 |" not in captured.out
    assert str(tmp_path) in captured.err


def test_two_version_directories_under_one_root_is_a_usage_error(
    tmp_path: Path, capsys: Any
) -> None:
    """Ambiguity is named, never resolved by picking one.

    Fails if `_data_dir` goes back to falling back to the root: the run would then load zero
    datasheets from a tree that has two, and report it as a comparison.
    """
    root = tmp_path / "a"
    _tree_a(root)
    (root / "wh40k-12e" / "factions").mkdir(parents=True)

    exit_code = main(["--published", str(root), "--candidate", str(_tree_a(tmp_path / "b"))])

    captured = capsys.readouterr()
    assert exit_code == USAGE_EXIT
    assert "Published-vs-candidate field parity" not in captured.out
    assert str(root) in captured.err


def _variant(root: Path, **overrides: Any) -> Path:
    """Tree A with named fields replaced. Every value invented, as everywhere in this file."""
    payload = _datasheet(
        skill="3+",
        weapon_range='12"',
        keyword="FEN WARDENS",
        ability_keys=["core:deep-strike", "datasheet:tidal-surge"],
    )
    payload.update(overrides)
    return _write_tree(root, payload)


def test_equal_ability_key_counts_with_different_slugs_are_counted_as_changed(
    tmp_path: Path,
) -> None:
    """The count of `core:` keys is not the set of them.

    Fails against a comparator that subtracts per-prefix counts: both sides hold exactly one
    `core:` key, so a count difference is zero while the binding has in fact been replaced. An
    equal count with a different slug is a changed key, not a match, and a tool that reports it
    as a match asserts a parity it never checked.
    """
    published = _variant(tmp_path / "a")
    candidate = _variant(
        tmp_path / "b", ability_keys=["core:rapid-insertion", "datasheet:tidal-surge"]
    )

    report = compare_trees(published, candidate)

    assert report.ability_keys_only_published == {"core": 1}, (
        "an equal count of core: keys with different slugs is a changed key, not a match"
    )
    assert report.ability_keys_only_candidate == {"core": 1}


def test_duplicate_keyword_multiplicity_is_not_reported_as_a_case_difference(
    tmp_path: Path,
) -> None:
    """Case-only means the same keywords printed differently - nothing else.

    Fails against a comparator that tests casefolded *set* equality: a side carrying the same
    keyword twice has an equal set and would be filed as a case difference, which is a claim
    about capitalisation that was never checked.
    """
    published = _variant(
        tmp_path / "a",
        keywords=[
            {"keyword": "FEN WARDENS", "is_faction_keyword": False},
            {"keyword": "FEN WARDENS", "is_faction_keyword": False},
        ],
    )
    candidate = _variant(
        tmp_path / "b", keywords=[{"keyword": "FEN WARDENS", "is_faction_keyword": False}]
    )

    report = compare_trees(published, candidate)

    assert report.keywords_case_only == 0, (
        "a differing number of identical keywords is not a capitalisation difference"
    )
    assert report.keywords_set_differs == 1


def test_a_changed_model_name_is_reported(tmp_path: Path) -> None:
    """Fails if `name` drops out of the model fields: a renamed profile would read as parity."""
    published = _variant(tmp_path / "a")
    candidate_payload = _datasheet(
        skill="3+",
        weapon_range='12"',
        keyword="FEN WARDENS",
        ability_keys=["core:deep-strike", "datasheet:tidal-surge"],
    )
    candidate_payload["models"][0]["name"] = "Fen Reaver"
    candidate = _write_tree(tmp_path / "b", candidate_payload)

    report = compare_trees(published, candidate)

    assert report.model_field_diffs.get("name", 0) == 1


def test_a_weapon_name_differing_only_in_case_is_reported(tmp_path: Path) -> None:
    """Weapons pair case-insensitively, so the case difference itself must still be counted.

    Fails if `name` is absent from the weapon fields: the pair matches, every stat matches, and
    a printed-name difference disappears from the field table entirely.
    """
    published = _variant(tmp_path / "a")
    candidate_payload = _datasheet(
        skill="3+",
        weapon_range='12"',
        keyword="FEN WARDENS",
        ability_keys=["core:deep-strike", "datasheet:tidal-surge"],
    )
    candidate_payload["weapons"][0]["name"] = "Tide Axe"
    candidate = _write_tree(tmp_path / "b", candidate_payload)

    report = compare_trees(published, candidate)

    assert report.weapons_paired == 1
    assert report.weapon_field_diffs.get("name", 0) == 1


def test_a_key_present_as_null_against_an_absent_key_is_a_difference(tmp_path: Path) -> None:
    """`.get()` on both sides cannot tell null from absent.

    Fails against a comparator that compares `payload.get(key)` alone: the datasheet counts as
    non-identical yet appears in no top-level row, so the report shows a difference it cannot
    name.
    """
    published = _variant(tmp_path / "a", damaged_threshold=None)
    candidate = _variant(tmp_path / "b")

    report = compare_trees(published, candidate)

    assert report.identical == 0
    assert report.top_level.get("damaged_threshold", 0) == 1
