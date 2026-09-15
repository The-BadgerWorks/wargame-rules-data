# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R6b Task 2 end-to-end receipt: a
# `Datasheets_wargear.csv` row whose `line` column is empty but whose `line_in_wargear` parses is
# read as a weapon profile, matching the live export's 1990 such rows. Identical weapon-row
# counts between the two arms would mean the reader still rejects empty-`line` rows.
"""The empty-`line` wargear reader is wired through a full offline build."""

from __future__ import annotations

import shutil
from pathlib import Path

from pipeline.cli import run_build
from pipeline.config import load_config
from pipeline.exit_codes import ExitCode

MINIMAL = Path(__file__).resolve().parents[2] / "fixtures" / "minimal"
FIRST_ID = "AV01"
#: Invented weapon name, never the publisher's wording.
WEAPON_NAME = "Test Fixture Blade"


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


def _fixture(tmp: Path, *, append_row: bool) -> Path:
    """Copy `fixtures/minimal`, optionally appending an empty-`line` wargear row for `AV01`.

    The appended row needs no curation approval to reach the bundle: it is an ordinary weapon
    profile, not an ability binding, so both arms (the row present or absent) reach the weapon
    count comparison without blocking on anything upstream of it.
    """
    fixtures = tmp / "fixtures"
    shutil.copytree(MINIMAL, fixtures, ignore=shutil.ignore_patterns("build"))
    if append_row:
        path = fixtures / "wahapedia" / "Datasheets_wargear.csv"
        text = path.read_text(encoding="utf-8-sig")
        # `line` empty, `line_in_wargear` numeric -- the shape round 6 measured 1990 times live.
        row = f"{FIRST_ID}||1||{WEAPON_NAME}||Melee|Melee|3|3+|5|-1|2|"
        path.write_text("﻿" + text.rstrip("\n") + "\n" + row + "\n", encoding="utf-8")
    return fixtures


def _run(tmp_path: Path, *, append_row: bool):  # noqa: ANN201 - result type is the cli's own
    fixtures = _fixture(tmp_path / "f", append_row=append_row)
    return run_build(
        config=load_config(env={}),
        rules_version_id="fixture-weapon-row-parity",
        fixtures_dir=fixtures,
        offline=True,
        output_root=tmp_path / "out",
        repository_root=_empty_repo(tmp_path / "repo"),
    )


def _total_weapon_rows(result) -> int:  # noqa: ANN001 - result type is the cli's own
    """Every weapon row in one offline build's published bundle's flat `datasheetWeapons` table."""
    return len(result.bundle["datasheetWeapons"])


def test_an_empty_line_wargear_row_is_read_as_one_more_weapon_row(tmp_path: Path) -> None:
    baseline = _run(tmp_path / "base", append_row=False)
    assert baseline.exit_code in (ExitCode.SUCCESS, ExitCode.ADVISORY_ONLY), [
        f.finding_code for f in baseline.findings if f.severity == "blocking"
    ]
    baseline_count = _total_weapon_rows(baseline)

    with_row = _run(tmp_path / "with-row", append_row=True)
    assert with_row.exit_code in (ExitCode.SUCCESS, ExitCode.ADVISORY_ONLY), [
        f.finding_code for f in with_row.findings if f.severity == "blocking"
    ]
    with_row_count = _total_weapon_rows(with_row)

    assert with_row_count == baseline_count + 1, (
        "identical weapon-row counts between the two arms mean the reader still rejects "
        f"empty-`line` rows: baseline={baseline_count}, with_row={with_row_count}"
    )
