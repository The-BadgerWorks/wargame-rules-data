# AI-Assisted: Claude Code (model: claude-sonnet-5) - Failing-first receipts for the line-scoped
# wargear-option measurement tool (pipeline PR P3 task 1): the seven-figure split (A-G) over
# inline synthetic tables, the D/F split over a mutated curated tree, and the counts-only CLI
# contract (one JSON file, `work/` discarded, no raw text anywhere). Figure G's synthetic data
# and both-direction assertions follow the controller's 2026-10-09 ruling made after this test's
# own first run showed `measure_tables` could not reach (2, 1, 1, 1) on the brief's literal
# fixture without it (`pipeline.normalize.names.normalize_name` does no singularisation by
# design).
"""Counts only, in and out: no sentence, subject, model name, or item name may appear anywhere
a failure message here could print it (every skeleton below is synthetic already, but the
discipline is the same one `test_equipment_taxonomy.py` holds itself to)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline.exit_codes import ExitCode
from pipeline.models.curated import CuratedOptionChoiceItem, OptionItemRole
from pipeline.parse.wahapedia_csv import read_text
from tests.factories import loadout_datasheet, snapshot
from tools.line_scope_taxonomy import (
    LineScopeFigures,
    main,
    measure_tables,
    measure_tree,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "fixtures" / "minimal"

HTML_ENV = {"WGC_DETAIL_EDITION": "wh40k-11e"}


# -- measure_tables: A, B, C, E, G -----------------------------------------------------------


def _synthetic_tables() -> dict[str, object]:
    """Datasheet FX01, per the controller's 2026-10-09 ruling.

    Composition: `1 Test Sergeant`, `4 Test Troopers`, `2 Test Troopers with test shield`,
    `1 Test Champion with test shield`. Four equipment sentences and two option rows, invented
    throughout: invented ids (`FX01`), invented model and item names (`Test Sergeant`, `Test
    Trooper`, `Test Champion`, `test shield`, `test blade`, `test lantern`).
    """
    equipment = read_text(
        "Datasheets_unit_equipment.csv",
        "datasheet_id|line|description|\n"
        "FX01|1|The Test Champion with test shield is equipped with: test shield; test blade.|\n"
        "FX01|2|Every Test Trooper with test shield is equipped with: test shield; test blade.|\n"
        "FX01|3|Every Test Trooper with test lantern is equipped with: test lantern.|\n"
        "FX01|4|Every Test Sergeant is equipped with: test blade.|\n",
    )
    composition = read_text(
        "Datasheets_unit_composition.csv",
        "datasheet_id|line|description|\n"
        "FX01|1|1 Test Sergeant|\n"
        "FX01|2|4 Test Troopers|\n"
        "FX01|3|2 Test Troopers with test shield|\n"
        "FX01|4|1 Test Champion with test shield|\n",
    )
    options = read_text(
        "Datasheets_options.csv",
        "datasheet_id|line|button|description|\n"
        "FX01|1||2 models can be equipped with 1 test lantern.|\n"
        "FX01|2||This model can be equipped with 1 test lantern.|\n",
    )
    return {
        "Datasheets_unit_equipment.csv": equipment,
        "Datasheets_unit_composition.csv": composition,
        "Datasheets_options.csv": options,
    }


def test_measure_tables_counts_a_through_g_on_the_ruled_fixture() -> None:
    """Controller ruling, 2026-10-09: expected (3, 1, 2, 1, 1).

    A=3 — all three "with"-bearing refused subjects (the `Every Test Sergeant` sentence parses
    cleanly and is counted nowhere). B=1 — only the exact singular/singular pair (`Test Champion`
    against the `1 Test Champion with test shield` line). C=2 — the two that do not equal a line
    exactly (one of which is the plural/singular gap G separately sizes, one of which names no
    line at all). E=1 — only the UNIT-scoped, unnamed, uncapped row matches
    `^(\\d+) models? can\\b`; the `This model ...` row is MODEL-scoped and does not count.
    """
    assert measure_tables(_synthetic_tables()) == (3, 1, 2, 1, 1)


def test_g_counts_only_the_plural_singular_pair_not_already_an_exact_match() -> None:
    """Both directions of figure G, named explicitly so a future change to either comparison is
    caught by name rather than folded into the one aggregate assertion above.

    - The exact match (`Test Champion`/`Test Champion`) must land in B, not contribute to G's
      denominator at all (G is "of C" only).
    - Of the two members of C, only the one whose line differs by a trailing "s" (`Test Trooper`
      vs. `Test Troopers`) counts toward G; the other (`test lantern`, no matching line under any
      comparison) must not.
    """
    with_subjects, exact_line, no_line, _n_models_can, plural_line = measure_tables(
        _synthetic_tables()
    )
    assert with_subjects == 3
    assert exact_line == 1
    assert no_line == 2
    assert plural_line == 1  # true positive: the plural/singular pair is caught
    assert plural_line < no_line  # true negative: the no-matching-line member is NOT caught


def test_an_exact_match_to_two_or_more_lines_counts_in_neither_b_nor_c() -> None:
    """Rule 4 (controller ruling): an ambiguous exact match is not evidence either way.

    Two composition lines share one name (`Test Duplicate`) on a second datasheet, FX02, and one
    equipment sentence's subject, after the marker and leading-article strip, equals both of them
    exactly. It must not be counted in B, in C, or toward G.
    """
    tables = dict(_synthetic_tables())
    equipment = tables["Datasheets_unit_equipment.csv"]
    composition = tables["Datasheets_unit_composition.csv"]
    tables["Datasheets_unit_equipment.csv"] = read_text(
        "Datasheets_unit_equipment.csv",
        "datasheet_id|line|description|\n"
        + "".join(
            f"{row.fields['datasheet_id']}|{row.fields['line']}|{row.fields['description']}|\n"
            for row in equipment.rows
        )
        + "FX02|1|Every Test Duplicate with test shield is equipped with: test shield.|\n",
    )
    tables["Datasheets_unit_composition.csv"] = read_text(
        "Datasheets_unit_composition.csv",
        "datasheet_id|line|description|\n"
        + "".join(
            f"{row.fields['datasheet_id']}|{row.fields['line']}|{row.fields['description']}|\n"
            for row in composition.rows
        )
        + "FX02|1|1 Test Duplicate with test shield|\n"
        + "FX02|2|1 Test Duplicate with test shield|\n",
    )
    with_subjects, exact_line, no_line, _n_models_can, plural_line = measure_tables(tables)
    assert with_subjects == 4  # the three FX01 subjects plus the new ambiguous FX02 one
    assert exact_line == 1  # unchanged: the FX01 Test Champion match, still the only clean one
    assert no_line == 2  # unchanged: the ambiguous subject is excluded from C too
    assert plural_line == 1  # unchanged: the ambiguous subject never reaches the relaxed check


def test_measure_tables_is_empty_on_tables_missing_every_source_file() -> None:
    assert measure_tables({}) == (0, 0, 0, 0, 0)


# -- measure_tree: D, F -----------------------------------------------------------------------


def test_measure_tree_counts_d_and_f() -> None:
    """007's `loadout_datasheet()` fixture, mutated per the brief's Step 1:

    D — a SECOND equipment group added alongside the original, sharing its `model_name`
    ("Sootveil Warden", which equals the datasheet's own composition line 1 exactly) but with
    `composition_line=None` — the "shadowed" case D measures. The original group is kept, with
    its `composition_line` intact, so the datasheet still has >= 1 line-resolved equipment group
    for F's own precondition to hold.

    F — one `REPLACED` item added to an existing option choice under the datasheet's only option
    group, which the datasheet's (still) line-resolved equipment group makes a line-scope
    candidate.
    """
    base = loadout_datasheet()
    original_group = base.equipment_groups[0]
    shadowed_group = original_group.model_copy(
        update={"id": f"{original_group.id}-shadow", "composition_line": None}
    )

    first_choice = base.option_choices[0]
    mutated_first_choice = first_choice.model_copy(
        update={
            "items": [
                *first_choice.items,
                CuratedOptionChoiceItem(
                    role=OptionItemRole.REPLACED,
                    item_index=len(first_choice.items) + 1,
                    item_name="Test glow lance",
                ),
            ]
        }
    )

    mutated = base.model_copy(
        update={
            "equipment_groups": [original_group, shadowed_group],
            "option_choices": [mutated_first_choice, *base.option_choices[1:]],
        }
    )

    assert measure_tree(snapshot(datasheets=[mutated])) == (1, 1)


def test_measure_tree_f_requires_a_line_resolved_equipment_group_on_the_same_datasheet() -> None:
    """F's precondition, isolated: a REPLACED item on a datasheet with NO line-resolved equipment
    group (every group's `composition_line` is `None`) must not be counted."""
    base = loadout_datasheet()
    unresolved_group = base.equipment_groups[0].model_copy(update={"composition_line": None})

    first_choice = base.option_choices[0]
    mutated_first_choice = first_choice.model_copy(
        update={
            "items": [
                *first_choice.items,
                CuratedOptionChoiceItem(
                    role=OptionItemRole.REPLACED, item_index=99, item_name="Test glow lance"
                ),
            ]
        }
    )

    mutated = base.model_copy(
        update={
            "equipment_groups": [unresolved_group],
            "option_choices": [mutated_first_choice, *base.option_choices[1:]],
        }
    )

    _shadowed, candidates = measure_tree(snapshot(datasheets=[mutated]))
    assert candidates == 0


def test_measure_tree_is_empty_on_a_snapshot_with_no_datasheets() -> None:
    assert measure_tree(snapshot(datasheets=[])) == (0, 0)


# -- LineScopeFigures -----------------------------------------------------------------------


def test_as_dict_carries_exactly_the_seven_named_figures() -> None:
    figures = LineScopeFigures(
        with_subjects=1,
        with_subject_exact_line=2,
        with_subject_no_line=3,
        exact_name_shadowed=4,
        n_models_can_stems=5,
        line_scope_candidates=6,
        with_subject_plural_line=7,
    )
    assert figures.as_dict() == {
        "with_subjects": 1,
        "with_subject_exact_line": 2,
        "with_subject_no_line": 3,
        "exact_name_shadowed": 4,
        "n_models_can_stems": 5,
        "line_scope_candidates": 6,
        "with_subject_plural_line": 7,
    }


# -- the CLI: counts-only output, work/ discarded, config error path -------------------------


def test_it_writes_only_its_own_json_and_discards_work(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)

    code = main(
        [
            "--fixtures",
            str(FIXTURES),
            "--offline",
            "--out",
            str(tmp_path / "out"),
            "--repo",
            str(tmp_path),
            "--edition-dir",
            str(tmp_path / "data" / "none"),
        ]
    )

    assert code == int(ExitCode.SUCCESS)
    written = sorted((tmp_path / "out").glob("*.json"))
    assert len(written) == 1

    document = json.loads(written[0].read_text(encoding="utf-8"))
    assert set(document) == {"figures", "rules_version_id", "acquired_at", "tool_commit"}
    assert set(document["figures"]) == {
        "with_subjects",
        "with_subject_exact_line",
        "with_subject_no_line",
        "exact_name_shadowed",
        "n_models_can_stems",
        "line_scope_candidates",
        "with_subject_plural_line",
    }
    assert all(isinstance(value, int) for value in document["figures"].values())

    work = tmp_path / "work"
    assert not work.exists() or next(work.iterdir(), None) is None
    assert not (tmp_path / "curation").exists()
    assert not (tmp_path / "reports" / "candidate").exists()


def test_a_live_run_without_a_source_url_is_a_configuration_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("WGC_DETAIL_SOURCE_URL", raising=False)

    code = main(["--repo", str(tmp_path), "--out", str(tmp_path / "out")])

    assert code == int(ExitCode.CONFIG_ERROR)
    assert "WGC_DETAIL_SOURCE_URL" in capsys.readouterr().err
    assert not (tmp_path / "out").exists()
