# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 1 end-to-end receipt: a loadout
# sentence injected into the minimal fixture's Datasheets export reaches the curated tree as an
# extracted default-equipment group; the unmodified fixture does not. Identical outcomes mean the
# reader is not wired through the build.
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


def _extracted_count(tmp_path: Path, loadout: str) -> int:
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
    return sum(
        1 for ds in result.bundle["datasheets"] if ds.get("defaultEquipmentState") == "extracted"
    )


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
