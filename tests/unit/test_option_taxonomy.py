# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the option-row taxonomy classifier
# (006 task T001): every research D1b class is reachable and disjoint, the cross-cutting features
# are the overlapping set they are meant to be, the report carries counts and no source text, and
# the acquired pages are discarded with work/ (006 risk R-A).
"""What a classifier that sizes a build order has to be trusted about is two things.

That each row lands in **exactly one** class — otherwise the per-class counts do not sum to the
residual and no production can be sized off one of them — and that **no source text reaches the
report**, because a taxonomy report is a committed artifact and the corpus it classifies is
publisher prose.

Every skeleton below is invented: invented model names, invented item names, invented counts.
They carry the grammar's own vocabulary because that is what a classifier matches on, and nothing
else.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from pipeline.config import load_config
from pipeline.exit_codes import ExitCode
from pipeline.models.curated import CuratedOptionGroup, OptionScope, WargearOptionState
from tests.factories import datasheet, snapshot
from tools.option_taxonomy import (
    BUILD_ORDER,
    classify,
    conditional_blocking_census,
    excluded_populations,
    features_of,
    iter_class_keys,
    load_published_snapshot_evidence,
    main,
    measure,
    override_candidate_worklist,
    render,
    render_override_candidate_worklist,
    zero_group_breakdown,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "fixtures" / "minimal"

HTML_ENV = {
    "WGC_DETAIL_ACQUISITION_MODE": "html",
    "WGC_DETAIL_EDITION": "wh40k-11e",
}

#: One invented skeleton per research D1b class. The tuple is the taxonomy's own coverage claim:
#: if a class here stops being reachable, a production has been sized against a class nothing
#: lands in.
SKELETONS: tuple[tuple[str, str], ...] = (
    (
        "1a",
        "Any number of models can each have their glimmer rifle replaced with 1 ember lance.",
    ),
    (
        "1b",
        "Any number of Fen Wardens can each have their glimmer rifle replaced with 1 ember lance.",
    ),
    (
        "1c",
        "Up to 4 Fen Wardens can each have their glimmer rifle replaced with one of the following:",
    ),
    (
        "1d",
        "For every 5 models in this unit, up to 2 Fen Wardens can each have their glimmer rifle "
        "replaced with 1 ember lance.",
    ),
    (
        "1e",
        "All models in this unit can each have their glimmer rifle replaced with 1 ember lance.",
    ),
    (
        "1f",
        "The Warden Prime can each have their glimmer rifle replaced with 1 ember lance.",
    ),
    ("2", "One Fen Warden's glimmer rifle can be replaced with 1 ember lance."),
    ("3", "Any number of Fen Wardens can each be equipped with 1 ember lance."),
    ("4", "This unit can replace its glimmer rifle with 1 ember lance."),
    ("5", "2 Fen Wardens can have its glimmer rifle replaced with 1 ember lance."),
    ("6", "Every Fen Warden is equipped with: glimmer rifle; ember lance."),
    ("7", "Fen Wardens can each replace their glimmer rifle with 1 ember lance."),
    (
        "8",
        "Any number of Fen Wardens' glimmer rifles can each be replaced with one of the following:",
    ),
    ("9", "If this unit has 5 or more models:"),
    ("10", "For every 5 models in this unit, it can have 1 ember lance."),
    ("11", "Warden Prime ."),
    ("12", "The Warden Prime's glimmer rifle replaced ember lance."),
    ("13", "Glimmer, ember, and the third thing nobody wrote a verb for, at some length."),
)


# -- classification -----------------------------------------------------------------------------


@pytest.mark.parametrize(("expected", "skeleton"), SKELETONS)
def test_each_class_owns_its_own_shape(expected: str, skeleton: str) -> None:
    assert classify(skeleton) == expected


def test_every_declared_class_is_reachable() -> None:
    """A class nothing can land in is a production sized against nothing."""
    assert {expected for expected, _ in SKELETONS} == set(iter_class_keys())


def test_classification_is_disjoint() -> None:
    """Each skeleton resolves to one class and the same one every time — ordering is fixed."""
    for expected, skeleton in SKELETONS:
        assert [classify(skeleton) for _ in range(3)] == [expected] * 3


def test_the_distributive_family_is_split_by_head_not_by_verb() -> None:
    """T016 builds the verb; T017 builds the heads. The report has to separate the two."""
    verb_only = {key for _task, key in BUILD_ORDER}
    assert verb_only == {"1a", "1b", "1c", "1d", "1e", "1f"}


def test_a_conditional_predicate_is_not_filed_as_an_extractor_bug() -> None:
    """Class 9 carries no clause vocabulary, exactly as a footnote fragment does not.

    Ordering is the only thing that tells them apart, and getting it wrong hides the one class
    research D1c.5 says to plan no production for behind a class that is a DOM fix.
    """
    assert classify("If this unit has 5 or more models:") == "9"
    assert classify("Warden Prime .") == "11"


# -- the cross-cutting features -----------------------------------------------------------------


def test_the_features_overlap_on_one_sentence() -> None:
    """They are properties of a row, not a partition of the corpus."""
    stem = (
        "Up to 4 Fen Wardens can each have their glimmer rifle and ember lance replaced with "
        "one of the following:"
    )
    found = features_of(stem, ("1 tide hammer and 1 shard cloak",))

    assert found >= {"sublist", "following", "distributive", "scoped_max", "multi_replaced"}
    assert "multi_granted" in found


def test_a_single_granted_item_is_not_a_bundle() -> None:
    stem = "Any number of models can each have their glimmer rifle replaced with 1 ember lance."
    assert "multi_granted" not in features_of(stem, ())
    assert "multi_replaced" not in features_of(stem, ())


def test_an_item_whose_own_name_contains_and_is_not_a_bundle() -> None:
    """The leading count is what distinguishes a bundle from a two-word name."""
    stem = "Any number of models can each have their glimmer rifle replaced with 1 bell and book."
    assert "multi_granted" not in features_of(stem, ())


# -- the measurement ----------------------------------------------------------------------------


def _measure(repo: Path):  # type: ignore[no-untyped-def]
    return measure(
        load_config(env=HTML_ENV),
        repository_root=repo,
        fixtures_dir=FIXTURES,
        offline=True,
        generated_at=datetime(2026, 8, 10, tzinfo=UTC),
    )


def test_the_class_counts_sum_to_the_residual(tmp_path: Path) -> None:
    """The property the whole report rests on: nothing is counted twice and nothing is lost."""
    report = _measure(tmp_path)
    assert sum(report.classes.values()) == report.unparsed
    assert report.unparsed <= report.rows


def test_the_run_records_the_mode_and_edition_it_measured(tmp_path: Path) -> None:
    report = _measure(tmp_path)
    assert (report.mode, report.edition) == ("html", "wh40k-11e")


def test_the_acquired_text_is_discarded(tmp_path: Path) -> None:
    _measure(tmp_path)
    work = tmp_path / "work"
    assert not work.exists() or next(work.iterdir(), None) is None


def test_no_source_text_reaches_the_report(tmp_path: Path) -> None:
    """The report is committed. The corpus it classifies is the publisher's wording."""
    rendered = render(_measure(tmp_path))

    for vocabulary in ("can be replaced with", "can be equipped with", "is equipped with:"):
        assert vocabulary not in rendered
    assert "Option-row taxonomy" in rendered
    assert "counts" in rendered


def test_it_writes_nothing_but_its_own_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)

    code = main(["--fixtures", str(FIXTURES), "--offline", "--repo", str(tmp_path)])

    assert code == int(ExitCode.SUCCESS)
    written = sorted((tmp_path / "reports" / "option-taxonomy").glob("*.md"))
    assert len(written) == 1
    assert not (tmp_path / "reports" / "candidate").exists()
    assert not (tmp_path / "curation").exists()
    assert not (tmp_path / "data").exists()


def test_a_live_run_without_a_source_url_is_a_configuration_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The live path — the one T002 takes — stops before a request is constructed."""
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("WGC_DETAIL_SOURCE_URL", raising=False)

    code = main(["--repo", str(tmp_path)])

    assert code == int(ExitCode.CONFIG_ERROR)
    assert "WGC_DETAIL_SOURCE_URL" in capsys.readouterr().err
    assert not (tmp_path / "reports").exists()


# -- 008 T001(b)/(c)/T003/T004: the published-snapshot section ----------------------------------


def _group(datasheet_id: str, line: int) -> CuratedOptionGroup:
    return CuratedOptionGroup(id=f"og-{datasheet_id}-{line}", line=line, scope=OptionScope.MODEL)


def test_zero_group_breakdown_splits_partial_by_whether_a_group_published() -> None:
    zero_a = datasheet("ds-zero-a", faction_id="f-a")
    zero_b = datasheet("ds-zero-b", faction_id="f-b")  # same name -> same shape as zero_a
    some = datasheet("ds-some", faction_id="f-c")
    extracted = datasheet("ds-extracted", faction_id="f-d")
    zero_a = zero_a.model_copy(update={"wargear_option_state": WargearOptionState.PARTIAL})
    zero_b = zero_b.model_copy(update={"wargear_option_state": WargearOptionState.PARTIAL})
    some = some.model_copy(
        update={
            "wargear_option_state": WargearOptionState.PARTIAL,
            "option_groups": [_group("ds-some", 1)],
        }
    )
    extracted = extracted.model_copy(update={"wargear_option_state": WargearOptionState.EXTRACTED})

    result = zero_group_breakdown(snapshot(datasheets=[zero_a, zero_b, some, extracted]))

    assert result.zero_group_datasheets == 2
    assert result.zero_group_shapes == 1  # zero_a and zero_b share `datasheet()`'s default name
    assert result.some_group_datasheets == 1
    assert result.some_group_shapes == 1
    assert set(result.zero_group_ids) == {"ds-zero-a", "ds-zero-b"}
    assert result.some_group_ids == ("ds-some",)


def test_excluded_populations_finds_the_cst_only_and_no_state_sets() -> None:
    vocab_gap = datasheet("ds-vocab-gap").model_copy(
        update={"wargear_option_state": WargearOptionState.PARTIAL}
    )
    genuinely_unparsed = datasheet("ds-genuinely-unparsed").model_copy(
        update={"wargear_option_state": WargearOptionState.PARTIAL}
    )
    no_state = datasheet("ds-no-state").model_copy(update={"wargear_option_state": None})
    findings = [
        {"finding_code": "OPT-UNPARSED", "detail": {"datasheet_id": "ds-genuinely-unparsed"}},
        {"finding_code": "CST-UNPARSED", "detail": {"datasheet_id": "ds-vocab-gap"}},
        {"finding_code": "OTHER-CODE", "detail": {"datasheet_id": "ds-vocab-gap"}},
    ]

    result = excluded_populations(
        snapshot(datasheets=[vocab_gap, genuinely_unparsed, no_state]), findings
    )

    assert result.item_constraint_vocabulary_gap == ("ds-vocab-gap",)
    assert result.no_option_state_at_all == ("ds-no-state",)


def test_conditional_blocking_census_builds_the_histogram_and_bounds_the_estimate() -> None:
    findings = [
        {"finding_code": "OPT-UNPARSED", "detail": {"datasheet_id": "ds-a"}},
        {"finding_code": "OPT-UNPARSED", "detail": {"datasheet_id": "ds-b"}},
        {"finding_code": "OPT-UNPARSED", "detail": {"datasheet_id": "ds-b"}},
        {"finding_code": "OTHER-CODE", "detail": {"datasheet_id": "ds-c"}},
    ]

    census = conditional_blocking_census(
        findings,
        measured_conditional_rows=1,
        measured_total_unparsed_rows=2,
        sc002_headroom=5,
    )

    assert census.unparsed_row_datasheets == 2
    assert census.unparsed_rows_total == 3
    assert census.single_row_datasheets == 1
    assert census.row_count_histogram == {1: 1, 2: 1}
    # share = 1/2 = 0.5; single_row=1 -> low = round(0.5) = 0; high = min(1, 1) = 1
    assert (census.estimate_low, census.estimate_high) == (0, 1)


def test_conditional_blocking_census_handles_zero_unparsed_rows() -> None:
    """A findings list with no `OPT-UNPARSED` at all must not divide by zero."""
    census = conditional_blocking_census(
        [], measured_conditional_rows=0, measured_total_unparsed_rows=0, sc002_headroom=21
    )
    assert (census.unparsed_row_datasheets, census.estimate_low, census.estimate_high) == (0, 0, 0)


def test_override_candidate_worklist_groups_lines_by_datasheet_in_order() -> None:
    """008 T071/T072 preparation: a worklist of `(datasheet_id, line)` pairs, never item content
    -- `detail` here carries only what `report.json`'s own text-free finding detail ever carries."""
    findings = [
        {"finding_code": "OPT-UNPARSED", "detail": {"datasheet_id": "ds-b", "line": 2}},
        {"finding_code": "OPT-UNPARSED", "detail": {"datasheet_id": "ds-a", "line": 3}},
        {"finding_code": "OPT-UNPARSED", "detail": {"datasheet_id": "ds-a", "line": 1}},
        {"finding_code": "OTHER-CODE", "detail": {"datasheet_id": "ds-a", "line": 9}},
        {"finding_code": "OPT-UNPARSED", "detail": {"not_a_datasheet_id": True}},
    ]

    worklist = override_candidate_worklist(findings)

    assert worklist.rows_by_datasheet == {"ds-a": (1, 3), "ds-b": (2,)}
    assert (worklist.total_rows, worklist.total_datasheets) == (3, 2)


def test_override_candidate_worklist_handles_no_findings() -> None:
    worklist = override_candidate_worklist([])
    assert worklist.rows_by_datasheet == {}
    assert (worklist.total_rows, worklist.total_datasheets) == (0, 0)


def test_render_override_candidate_worklist_never_carries_more_than_ids_and_line_numbers() -> None:
    worklist = override_candidate_worklist(
        [{"finding_code": "OPT-UNPARSED", "detail": {"datasheet_id": "ds-a", "line": 1}}]
    )
    rendered = render_override_candidate_worklist(worklist, rules_version_id="wh40k-11e-2026-08-3")
    assert "ds-a" in rendered
    assert "line" in rendered.casefold() and "1" in rendered
    assert "stale" in rendered.casefold()
    # No prose ever appears in the worklist: it names ids and integers only.
    assert "ember" not in rendered.casefold()  # a canary invented item name, never present


def test_load_published_snapshot_evidence_is_none_without_a_manifest(tmp_path: Path) -> None:
    """A fresh checkout, or a `--fixtures` rehearsal, has no `site/manifest.json` — additive,
    never a crash."""
    assert load_published_snapshot_evidence(tmp_path, edition_code="wh40k-11e") is None


def test_load_published_snapshot_evidence_reads_this_repositorys_own_committed_state() -> None:
    """The real property this feature depends on: `data/wh40k-11e/`, `site/manifest.json`, and
    `reports/<rulesVersionId>/report.json` are all committed in **this** checkout, so this run
    against the real repository root resolves real evidence rather than needing a fixture."""
    root = Path(__file__).resolve().parents[2]
    evidence = load_published_snapshot_evidence(root, edition_code="wh40k-11e")
    assert evidence is not None
    assert evidence.snapshot.datasheets
    assert evidence.findings
