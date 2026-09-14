# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 1 end-to-end receipt: a loadout
# sentence injected into the minimal fixture's Datasheets export reaches the curated tree as an
# extracted default-equipment group; the unmodified fixture does not. Identical outcomes mean the
# reader is not wired through the build.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 3 task 1: generalised
# `_extracted_count` into `_state_counts` (every `defaultEquipmentState`, counting a wholly
# absent one under "absent") and added the end-to-end receipt that a refused loadout sentence
# reaches the bundle as `partial`, never `none`, closing the round 2 Tier 1.
"""The loadout-column reader is wired through a full offline build."""

from __future__ import annotations

import shutil
from pathlib import Path

from pipeline.cli import run_build
from pipeline.config import load_config
from pipeline.exit_codes import ExitCode

MINIMAL = Path(__file__).resolve().parents[2] / "fixtures" / "minimal"
FIRST_ID = "AV01"
SENTENCE = "Every model is equipped with: glow lantern; tide axe."


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


def _fixture_with_loadout(tmp: Path, loadout: str) -> Path:
    fixtures = tmp / "fixtures"
    shutil.copytree(MINIMAL, fixtures, ignore=shutil.ignore_patterns("build"))
    path = fixtures / "wahapedia" / "Datasheets.csv"
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    header = lines[0].split("|")
    column = header.index("loadout")
    rewritten = [lines[0]]
    for line in lines[1:]:
        cells = line.split("|")
        if cells[0] == FIRST_ID:
            cells[column] = loadout
        rewritten.append("|".join(cells))
    path.write_text("﻿" + "\n".join(rewritten) + "\n", encoding="utf-8")
    return fixtures


def _state_counts(tmp_path: Path, loadout: str) -> dict[str, int]:
    """How many datasheets landed in each ``defaultEquipmentState`` for a build of this loadout.

    A datasheet with no state at all (the table was never populated for the whole build) is
    counted under the key ``"absent"`` rather than dropped, so a caller comparing two builds
    sees every datasheet accounted for in both.
    """
    fixtures = _fixture_with_loadout(tmp_path / "f", loadout)
    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-loadout",
        fixtures_dir=fixtures,
        offline=True,
        output_root=tmp_path / "out",
        repository_root=_empty_repo(tmp_path / "repo"),
    )
    assert result.exit_code in (ExitCode.SUCCESS, ExitCode.ADVISORY_ONLY), [
        f.finding_code for f in result.findings if f.severity == "blocking"
    ]
    counts: dict[str, int] = {}
    for ds in result.bundle["datasheets"]:
        state = ds.get("defaultEquipmentState") or "absent"
        counts[state] = counts.get(state, 0) + 1
    return counts


def _extracted_count(tmp_path: Path, loadout: str) -> int:
    return _state_counts(tmp_path, loadout).get("extracted", 0)


def test_a_loadout_sentence_reaches_the_bundle_as_extracted_equipment(tmp_path: Path) -> None:
    with_sentence = _extracted_count(tmp_path / "a", SENTENCE)
    without = _extracted_count(tmp_path / "b", "")
    assert with_sentence > without, (
        "the bundle is identical with and without a loadout sentence: the loadout reader is not "
        "wired through run_build"
    )


def test_an_ambiguous_loadout_sentence_surfaces_as_a_finding_in_the_build(tmp_path: Path) -> None:
    fixtures = _fixture_with_loadout(
        tmp_path / "f",
        "<b>Every model</b> is equipped with: glow lantern. Some invented trailing prose here.",
    )
    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-ambiguous",
        fixtures_dir=fixtures,
        offline=True,
        output_root=tmp_path / "out",
        repository_root=_empty_repo(tmp_path / "repo"),
    )
    codes = [f.finding_code for f in result.findings]
    assert "EQP-BOUNDARY-AMBIGUOUS" in codes, codes


def test_a_datasheet_with_a_refused_sentence_publishes_as_partial_not_none(tmp_path: Path) -> None:
    """Round 3 receipt: the refused sentence must reach the bundle as an empty row at its own
    ordinal, so the datasheet becomes `partial` — not silently `none` and not left `extracted`.

    The baseline build uses SENTENCE rather than the truly unmodified fixture: AV01's own
    placeholder loadout carries no marker at all, so an untouched fixture never populates the
    equipment table for *any* datasheet, and `defaultEquipmentState` is entirely absent
    (counted as "absent" above) rather than an explicit "none". SENTENCE populates the table
    (AV01 resolves to "extracted", the other datasheets to explicit "none"), which is the same
    table-exists shape the refused-sentence build produces — so the delta below isolates AV01's
    own transition instead of crossing the all-or-nothing table-existence boundary.
    """
    baseline = _state_counts(tmp_path / "base", SENTENCE)
    refused = _state_counts(
        tmp_path / "refused",
        "<b>Every model</b> is equipped with: glow lantern. Some invented trailing prose here.",
    )
    assert refused.get("partial", 0) == baseline.get("partial", 0) + 1, (baseline, refused)
    assert refused.get("none", 0) == baseline.get("none", 0), (baseline, refused)
