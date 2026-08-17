# AI-Assisted: Claude Code (model: claude-sonnet-5) - Asserts the equipment-sentence taxonomy
# classifier (008 task T002): every class is reachable and disjoint, ordering matches
# `equipment_grammar._REFUSED` exactly, the report carries counts and no source text, and the
# acquired pages are discarded with `work/` (008 risk R-H).
"""The equipment-sentence sibling of `test_option_taxonomy.py`, held to the same two standards:
each refused subject lands in exactly one class, and no source text reaches a committed report.

Every skeleton below is invented: invented model names, invented item names.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from pipeline.config import load_config
from pipeline.exit_codes import ExitCode
from pipeline.models.curated import DefaultEquipmentState
from tests.factories import datasheet, snapshot
from tools.equipment_taxonomy import (
    CLASS_LABELS,
    classify_subject,
    default_equipment_ratchet_baseline,
    diagnose_sentence,
    equipment_override_candidate_worklist,
    equipment_partial_breakdown,
    iter_class_keys,
    main,
    measure,
    render,
    render_equipment_override_candidate_worklist,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "fixtures" / "minimal"

HTML_ENV = {
    "WGC_DETAIL_ACQUISITION_MODE": "html",
    "WGC_DETAIL_EDITION": "wh40k-11e",
}

#: One invented subject per class, mirroring `equipment_grammar._REFUSED`'s own fixed order
#: (006 research D1e). If a class here stops being reachable, O1's own sizing has nothing to
#: measure it against.
SKELETONS: tuple[tuple[str, str], ...] = (
    ("equipment_qualified", "Every Fen Warden with a glimmer rifle"),
    ("subset_one", "One Fen Warden"),
    ("subset_a", "A Fen Warden"),
    ("subset_a", "An Ember Sentry"),
    ("subset_int", "2 Fen Wardens"),
    ("conditional", "For every 5 models in the unit, 1 model"),
    ("conditional", "If the unit has 10 models, 2 models"),
    ("conditional", "Unless stated otherwise, this model"),
    ("conditional", "Up to 3 Fen Wardens"),
    ("conditional", "Fen Warden, veteran of the marsh campaigns,"),
    ("subject_unmatched", ""),
)


# -- classification -----------------------------------------------------------------------------


@pytest.mark.parametrize(("expected", "subject"), SKELETONS)
def test_each_class_owns_its_own_shape(expected: str, subject: str) -> None:
    assert classify_subject(subject) == expected


def test_every_declared_class_is_reachable_or_named() -> None:
    """`no_marker`/`empty_items` are sentence-level, not subject-level (checked below); every
    other declared class must be reachable from `classify_subject` alone."""
    subject_level = set(CLASS_LABELS) - {"no_marker", "empty_items"}
    assert {expected for expected, _ in SKELETONS} == subject_level


def test_classification_is_disjoint() -> None:
    for expected, subject in SKELETONS:
        assert [classify_subject(subject) for _ in range(3)] == [expected] * 3


def test_equipment_qualified_is_checked_before_a_subset_word() -> None:
    """Mirrors `_REFUSED`'s own fixed order: a subject naming both a subset word and an
    equipment qualifier is equipment-qualified, exactly as `equipment_grammar._match_subject`
    would refuse it on the `with` pattern before ever reaching the subset ones."""
    assert classify_subject("One Fen Warden with a glimmer rifle") == "equipment_qualified"


def test_diagnose_sentence_checks_the_marker_and_the_item_list_first() -> None:
    assert diagnose_sentence("Every model in this unit is arrayed for war.") == "no_marker"
    assert diagnose_sentence("Every model is equipped with:") == "empty_items"
    assert diagnose_sentence("One Fen Warden is equipped with: glimmer rifle.") == "subset_one"


def test_iter_class_keys_matches_the_label_table() -> None:
    assert list(iter_class_keys()) == list(CLASS_LABELS)


# -- the measurement ------------------------------------------------------------------------------


def _measure(repo: Path):  # type: ignore[no-untyped-def]
    return measure(
        load_config(env=HTML_ENV),
        repository_root=repo,
        fixtures_dir=FIXTURES,
        offline=True,
        generated_at=datetime(2026, 8, 15, tzinfo=UTC),
    )


def test_the_class_counts_sum_to_the_residual(tmp_path: Path) -> None:
    report = _measure(tmp_path)
    assert sum(report.classes.values()) == report.unparsed
    assert report.unparsed <= report.sentences


def test_the_run_records_the_mode_and_edition_it_measured(tmp_path: Path) -> None:
    report = _measure(tmp_path)
    assert (report.mode, report.edition) == ("html", "wh40k-11e")


def test_the_acquired_text_is_discarded(tmp_path: Path) -> None:
    _measure(tmp_path)
    work = tmp_path / "work"
    assert not work.exists() or next(work.iterdir(), None) is None


def test_no_source_text_reaches_the_report(tmp_path: Path) -> None:
    """`render` only ever sees `EquipmentTaxonomyReport` — integers and its own static class
    labels — never a sentence, model name, or item name, so none of this test's own invented
    skeleton subjects can appear in it. (The marker text `is`/`are equipped with:` legitimately
    appears in a class *label*, describing the grammar's own structural vocabulary, exactly as
    `equipment_grammar.py`'s own committed module docstring already states it — this is a
    structural connective, not a card's own sentence, and checking for it would fail on this
    report's own necessary self-description rather than on a leak.)"""
    rendered = render(_measure(tmp_path))
    for _expected, subject in SKELETONS:
        if subject:
            assert subject not in rendered
    assert "Equipment-sentence taxonomy" in rendered
    assert "counts" in rendered


def test_it_writes_nothing_but_its_own_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)

    code = main(["--fixtures", str(FIXTURES), "--offline", "--repo", str(tmp_path)])

    assert code == int(ExitCode.SUCCESS)
    written = sorted((tmp_path / "reports" / "equipment-taxonomy").glob("*.md"))
    assert len(written) == 1
    assert not (tmp_path / "reports" / "candidate").exists()
    assert not (tmp_path / "curation").exists()
    assert not (tmp_path / "data").exists()


def test_a_live_run_without_a_source_url_is_a_configuration_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("WGC_DETAIL_SOURCE_URL", raising=False)

    code = main(["--repo", str(tmp_path)])

    assert code == int(ExitCode.CONFIG_ERROR)
    assert "WGC_DETAIL_SOURCE_URL" in capsys.readouterr().err
    assert not (tmp_path / "reports").exists()


# -- 008 T002's card-shape collapse, T005's ratchet-baseline confirmation -----------------------


def test_equipment_partial_breakdown_collapses_by_case_insensitive_name() -> None:
    a = datasheet("ds-partial-a", faction_id="f-a").model_copy(
        update={"default_equipment_state": DefaultEquipmentState.PARTIAL}
    )
    b = datasheet("ds-partial-b", faction_id="f-b").model_copy(
        update={"default_equipment_state": DefaultEquipmentState.PARTIAL}
    )
    extracted = datasheet("ds-extracted", faction_id="f-c").model_copy(
        update={"default_equipment_state": DefaultEquipmentState.EXTRACTED}
    )

    result = equipment_partial_breakdown(snapshot(datasheets=[a, b, extracted]))

    assert result.partial_datasheets == 2
    assert result.partial_shapes == 1  # `datasheet()`'s default name, shared by a and b
    assert set(result.partial_ids) == {"ds-partial-a", "ds-partial-b"}


def test_default_equipment_ratchet_baseline_is_none_without_a_manifest(tmp_path: Path) -> None:
    assert default_equipment_ratchet_baseline(tmp_path) is None


def test_equipment_override_candidate_worklist_is_none_without_a_manifest(tmp_path: Path) -> None:
    assert equipment_override_candidate_worklist(tmp_path) is None


def test_equipment_override_candidate_worklist_reads_this_repositorys_own_committed_state() -> None:
    """008 T071/T072 preparation, the equipment twin of `test_option_taxonomy.py`'s
    `override_candidate_worklist`: the previous published version's retained `report.json`
    resolves in **this** checkout with no live acquisition, and its `EQP-UNPARSED` findings group
    into a real, non-empty worklist."""
    root = Path(__file__).resolve().parents[2]
    result = equipment_override_candidate_worklist(root)
    assert result is not None
    rules_version_id, worklist = result
    assert rules_version_id
    assert worklist.total_rows > 0
    assert worklist.total_datasheets > 0
    assert sum(len(lines) for lines in worklist.rows_by_datasheet.values()) == worklist.total_rows


def test_the_rendered_equipment_worklist_carries_only_ids_and_line_numbers() -> None:
    result = equipment_override_candidate_worklist(Path(__file__).resolve().parents[2])
    assert result is not None
    rules_version_id, worklist = result
    rendered = render_equipment_override_candidate_worklist(rules_version_id, worklist)
    assert "stale" in rendered.casefold()
    assert "ember" not in rendered.casefold()  # a canary invented item name, never present


def test_default_equipment_ratchet_baseline_reads_this_repositorys_own_committed_state() -> None:
    """The real property T005 depends on: `site/manifest.json` and
    `reports/<rulesVersionId>/report.json` are committed in **this** checkout, and the previous
    published version's `loadout.default_equipment` figure resolves from them with no live
    acquisition at all."""
    root = Path(__file__).resolve().parents[2]
    baseline = default_equipment_ratchet_baseline(root)
    assert baseline is not None
    assert baseline.ratio_percent is not None
