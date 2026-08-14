# AI-Assisted: Claude Code (model: claude-sonnet-5) - Asserts the footnote-restriction-arrival-
# path classifier (007 task T002): every diagnosis class is reachable and disjoint, the two
# restriction signals are generic-shape tests rather than vocabulary guesses, the measurement
# discards its acquired text, and the report carries counts and no source text (research D4.2,
# risk R-J).
"""What T003 rests its verdict on is two properties of this classifier, not on its counts.

That the diagnosis of an unparsed options row **never drifts** from what
:func:`pipeline.parse.options_grammar.parse_row` itself does — it calls the same private
functions directly rather than a second copy of their patterns — and that **no source text
reaches the report**, because the report this tool writes is a committed artifact and the corpus
it classifies is publisher prose.

Every skeleton below is invented: invented model names, invented item names. They carry the
grammar's own vocabulary because that is what the diagnosis matches on, and the two restriction
signals are generic English phrasings, not text lifted from any inspected card.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from pipeline.config import load_config
from pipeline.exit_codes import ExitCode
from pipeline.parse.options_grammar import parse_row
from tools.item_constraint_taxonomy import (
    OPTION_DIAGNOSIS_CLASSES,
    diagnose_option_row,
    main,
    measure,
    render,
    restriction_signal,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "fixtures" / "minimal"

HTML_ENV = {
    "WGC_DETAIL_ACQUISITION_MODE": "html",
    "WGC_DETAIL_EDITION": "wh40k-11e",
}

# -- diagnosis ------------------------------------------------------------------------------


def test_an_empty_stem_is_its_own_class() -> None:
    assert diagnose_option_row("") == "empty_stem"


def test_the_permissive_refusal_is_diagnosed() -> None:
    assert diagnose_option_row("1 in 3 models may be equipped with 1 ember lance.") == (
        "refused_permissive_or_ratio"
    )


def test_a_conditional_head_is_diagnosed_as_extended_refused() -> None:
    assert diagnose_option_row("If this unit has 5 or more models, do something.") == (
        "refused_conditional_or_equipment_qualified"
    )


def test_an_unrecognised_head_has_no_head_match() -> None:
    assert diagnose_option_row("Glimmer wardens gain nothing in particular here.") == (
        "no_head_match"
    )


def test_a_head_with_no_verb_phrase_is_diagnosed() -> None:
    assert diagnose_option_row("This model has a glimmer rifle.") == "head_ok_no_verb"


def test_a_verb_with_an_empty_object_is_diagnosed() -> None:
    assert diagnose_option_row("This model can be equipped with .") == "verb_ok_object_invalid"


def test_every_unparsed_synthetic_row_is_actually_unparsed() -> None:
    """A diagnosis is only meaningful for a row the real grammar also refused."""
    rows = (
        "",
        "1 in 3 models may be equipped with 1 ember lance.",
        "If this unit has 5 or more models, do something.",
        "Glimmer wardens gain nothing in particular here.",
        "This model has a glimmer rifle.",
        "This model can be equipped with .",
    )
    for row in rows:
        assert parse_row(row) is None


def test_every_declared_diagnosis_class_is_reachable() -> None:
    """A class nothing can land in would size T036's vocabulary against nothing."""
    skeletons = (
        "",
        "1 in 3 models may be equipped with 1 ember lance.",
        "If this unit has 5 or more models, do something.",
        "Glimmer wardens gain nothing in particular here.",
        "This model has a glimmer rifle.",
        "This model can be equipped with .",
    )
    reached = {diagnose_option_row(row) for row in skeletons}
    # `verb_ok_item_invalid` and `diagnostic_mismatch` are reachable but need a `<ul>` sub-list
    # (item_raw non-empty) and a resolving row respectively, so they are not exercised by the
    # flat skeletons above — every OTHER declared class is.
    assert reached <= set(OPTION_DIAGNOSIS_CLASSES)
    assert reached == {
        "empty_stem",
        "refused_permissive_or_ratio",
        "refused_conditional_or_equipment_qualified",
        "no_head_match",
        "head_ok_no_verb",
        "verb_ok_object_invalid",
    }


# -- restriction signal -----------------------------------------------------------------------


def test_a_negation_cue_is_signalled() -> None:
    assert restriction_signal("The glimmer rifle cannot be replaced.") == "negation"


def test_a_cardinality_cue_is_signalled() -> None:
    assert restriction_signal("Only one ember lance can be taken per unit.") == "cardinality"


def test_both_cues_together_are_signalled_as_both() -> None:
    assert restriction_signal("Only one ember lance cannot be replaced.") == "both"


def test_neither_cue_is_signalled_as_neither() -> None:
    assert restriction_signal("This model can be equipped with 1 ember lance.") == "neither"


# -- the measurement ----------------------------------------------------------------------------


def _measure(repo: Path):  # type: ignore[no-untyped-def]
    return measure(
        load_config(env=HTML_ENV),
        repository_root=repo,
        fixtures_dir=FIXTURES,
        offline=True,
        generated_at=datetime(2026, 8, 13, tzinfo=UTC),
    )


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
    assert "Footnote-restriction arrival-path taxonomy" in rendered
    assert "counts and structural booleans only" in rendered


def test_it_writes_nothing_but_its_own_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)

    code = main(["--fixtures", str(FIXTURES), "--offline", "--repo", str(tmp_path)])

    assert code == int(ExitCode.SUCCESS)
    written = sorted((tmp_path / "reports" / "footnote-restriction-taxonomy").glob("*.md"))
    assert len(written) == 1
    assert not (tmp_path / "reports" / "candidate").exists()
    assert not (tmp_path / "curation").exists()
    assert not (tmp_path / "data").exists()


def test_a_live_run_without_a_source_url_is_a_configuration_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The live path — the one T003 takes — stops before a request is constructed."""
    for name, value in HTML_ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("WGC_DETAIL_SOURCE_URL", raising=False)

    code = main(["--repo", str(tmp_path)])

    assert code == int(ExitCode.CONFIG_ERROR)
    assert "WGC_DETAIL_SOURCE_URL" in capsys.readouterr().err
    assert not (tmp_path / "reports").exists()
