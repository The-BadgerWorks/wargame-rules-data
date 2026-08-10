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
from tools.option_taxonomy import (
    BUILD_ORDER,
    classify,
    features_of,
    iter_class_keys,
    main,
    measure,
    render,
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
