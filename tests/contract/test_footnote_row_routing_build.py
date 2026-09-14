# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 4 task 1 end-to-end receipt: a
# footnote-marked options row (`button` `*`) is routed out of the options table before the
# grammar sees it, so it never demotes an otherwise-fully-resolved datasheet to `partial`, and
# `OPT-FOOTNOTE-ROW` reports the omission. The paired `•` build is the receipt's other half:
# identical `wargearOptionState` distributions in both arms would mean the routing is not wired.
"""The footnote-row reader is wired through a full offline build (html parity, 010 R4)."""

from __future__ import annotations

import shutil
from pathlib import Path

from pipeline.cli import run_build
from pipeline.config import load_config
from pipeline.exit_codes import ExitCode

MINIMAL = Path(__file__).resolve().parents[2] / "fixtures" / "minimal"
FIRST_ID = "AV01"
#: Invented, deliberately unparseable by the options grammar: no head production, no
#: item-constraint vocabulary member. Its purpose is only to prove the control arm actually
#: lands `partial` via `OPT-UNPARSED`, not to exercise any production.
_UNPARSEABLE_TEXT = "Zzq florvex quantum widget arrangement."


def _empty_repo(tmp: Path) -> Path:
    for relative in (
        "data/wh40k-11e/factions",
        "curation/abilities",
        "reports",
        "state",
        "site/prerelease",
        "work",
    ):
        (tmp / relative).mkdir(parents=True, exist_ok=True)
    return tmp


def _fixture_with_option_row(tmp: Path, *, button: str) -> Path:
    fixtures = tmp / "fixtures"
    shutil.copytree(MINIMAL, fixtures, ignore=shutil.ignore_patterns("build"))
    path = fixtures / "wahapedia" / "Datasheets_options.csv"
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    row = f"{FIRST_ID}|1|{button}|{_UNPARSEABLE_TEXT}|"
    path.write_text("﻿" + "\n".join([*lines, row]) + "\n", encoding="utf-8")
    return fixtures


def _run(tmp_path: Path, *, button: str):  # noqa: ANN201 - result type is the cli's own
    fixtures = _fixture_with_option_row(tmp_path / "f", button=button)
    return run_build(
        config=load_config(env={}),
        rules_version_id="fixture-footnote",
        fixtures_dir=fixtures,
        offline=True,
        output_root=tmp_path / "out",
        repository_root=_empty_repo(tmp_path / "repo"),
    )


def _state_counts(result) -> dict[str, int]:  # noqa: ANN001 - result type is the cli's own
    """How many datasheets landed in each ``wargearOptionState`` for one build.

    The bundle's datasheet ids are the slugified ``ds-<slug>`` form, not the export's raw
    ``datasheet_id`` (``AV01``), so a single changed datasheet is isolated by counting the whole
    distribution rather than looking one id up — the same pattern
    ``test_loadout_equipment_build.py`` uses for the equipment table.
    """
    counts: dict[str, int] = {}
    for ds in result.bundle["datasheets"]:
        state = ds.get("wargearOptionState") or "absent"
        counts[state] = counts.get(state, 0) + 1
    return counts


def test_a_footnote_row_never_demotes_the_datasheet_to_partial(tmp_path: Path) -> None:
    baseline = _run(tmp_path / "base", button="•")
    baseline_counts = _state_counts(baseline)

    footnote = _run(tmp_path / "footnote", button="*")
    assert footnote.exit_code in (ExitCode.SUCCESS, ExitCode.ADVISORY_ONLY), [
        f.finding_code for f in footnote.findings if f.severity == "blocking"
    ]
    codes = [f.finding_code for f in footnote.findings]
    assert "OPT-FOOTNOTE-ROW" in codes, codes

    footnote_counts = _state_counts(footnote)
    # The `•` control arm resolves the invented row as an option row the grammar cannot parse,
    # so it lands `partial` (OPT-UNPARSED); the `*` arm routes the same row out before the
    # grammar sees it, so the datasheet's option table is never populated for it and its state
    # is not `partial`.
    assert baseline_counts.get("partial", 0) > 0, baseline_counts
    assert footnote_counts.get("partial", 0) < baseline_counts.get("partial", 0), (
        baseline_counts,
        footnote_counts,
    )


def test_the_bullet_and_footnote_arms_yield_different_state_distributions(tmp_path: Path) -> None:
    """The receipt: an identical row differing only in `button` must yield a different bundle,
    or the footnote routing is not actually wired into the build."""
    bullet_result = _run(tmp_path / "bullet", button="•")
    assert bullet_result.exit_code in (ExitCode.SUCCESS, ExitCode.ADVISORY_ONLY), [
        f.finding_code for f in bullet_result.findings if f.severity == "blocking"
    ]
    footnote_result = _run(tmp_path / "footnote", button="*")
    assert footnote_result.exit_code in (ExitCode.SUCCESS, ExitCode.ADVISORY_ONLY), [
        f.finding_code for f in footnote_result.findings if f.severity == "blocking"
    ]
    assert _state_counts(bullet_result) != _state_counts(footnote_result), (
        "both arms produced the same wargearOptionState distribution: the footnote routing is "
        "not wired through the build"
    )
