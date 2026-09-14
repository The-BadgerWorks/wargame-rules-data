# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 R6b Task 1 end-to-end receipt: a Core
# binding carrying a `parameter` column reaches the published bundle with the parameter joined
# into its ability key, reproducing the site's own `core:feel-no-pain-5` form rather than the
# CSV arm's bare `core:feel-no-pain`. A bare key in the bundle means the parameter is not joined
# — the reader is not wired through the build.
"""The parameter-joined ability key is wired through a full offline build."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from pipeline.cli import run_build
from pipeline.config import load_config
from pipeline.exit_codes import ExitCode
from pipeline.reconcile.identity import slugify

MINIMAL = Path(__file__).resolve().parents[2] / "fixtures" / "minimal"
FIRST_ID = "AV01"
#: Invented ability name (research D10) — never the publisher's wording.
CORE_NAME = "Ember Shield"
PARAMETER = "D3"
#: The fixture's placeholder ability description is identical across every binding row
#: (`fixtures/minimal/wahapedia/Datasheets_abilities.csv`), so it always digests to this value
#: under the empty digest key `load_config(env={})` supplies — matching every other approved
#: curation entry in `fixtures/minimal/curation/abilities/`.
_PLACEHOLDER_DIGEST = "647e4dd518c3b4733ce43bf5963d248f"


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


def _fixture_with_core_parameter(tmp: Path, parameter: str) -> Path:
    """Rewrite AV01's first `Datasheets_abilities.csv` binding to a Core type with a parameter."""
    fixtures = tmp / "fixtures"
    shutil.copytree(MINIMAL, fixtures, ignore=shutil.ignore_patterns("build"))
    path = fixtures / "wahapedia" / "Datasheets_abilities.csv"
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    header = lines[0].split("|")
    name_col = header.index("name")
    type_col = header.index("type")
    parameter_col = header.index("parameter")
    rewritten = [lines[0]]
    replaced = False
    for line in lines[1:]:
        cells = line.split("|")
        if not replaced and cells[0] == FIRST_ID:
            cells[name_col] = CORE_NAME
            cells[type_col] = "Core"
            cells[parameter_col] = parameter
            replaced = True
        rewritten.append("|".join(cells))
    assert replaced, f"fixture has no {FIRST_ID} binding row to rewrite"
    path.write_text("﻿" + "\n".join(rewritten) + "\n", encoding="utf-8")

    _approve_summary(fixtures, joined_key=f"core:{slugify(f'{CORE_NAME} {parameter}'.strip())}")
    return fixtures


def _approve_summary(fixtures: Path, *, joined_key: str) -> None:
    """Give the rewritten binding's new ability key an approved curated summary.

    Without this the build reports `SUM-MISSING` for the new key and never reaches the bundle
    comparison this test is actually about.
    """
    path = fixtures / "curation" / "abilities" / "f-ashen-vigil.json"
    entries = json.loads(path.read_text(encoding="utf-8"))
    entries.append(
        {
            "ability_key": joined_key,
            "mechanic_digest": _PLACEHOLDER_DIGEST,
            "name": CORE_NAME,
            "review_state": "approved",
            "reviewed_at": "2026-06-13T00:00:00Z",
            "reviewed_by": "fixture-curator",
            "summary": f"Invented mechanics-only summary for {CORE_NAME}, authored for this test.",
        }
    )
    path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")


def _all_ability_keys(tmp_path: Path, parameter: str) -> set[str]:
    """Every `ability_keys` entry across every datasheet in one offline build's published
    curated snapshot (the same `ability_keys` list `curate/writer.py` writes to `data/` and
    `curate/assemble.py` mints)."""
    fixtures = _fixture_with_core_parameter(tmp_path / "f", parameter)
    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-core-parameter",
        fixtures_dir=fixtures,
        offline=True,
        output_root=tmp_path / "out",
        repository_root=_empty_repo(tmp_path / "repo"),
    )
    assert result.exit_code in (ExitCode.SUCCESS, ExitCode.ADVISORY_ONLY), [
        f.finding_code for f in result.findings if f.severity == "blocking"
    ]
    keys: set[str] = set()
    for datasheet in result.snapshot.datasheets:
        keys.update(datasheet.ability_keys)
    return keys


def test_a_core_bindings_parameter_reaches_the_bundle_joined_into_the_key(
    tmp_path: Path,
) -> None:
    keys = _all_ability_keys(tmp_path, PARAMETER)
    bare_key = f"core:{slugify(CORE_NAME)}"
    joined_key = f"core:{slugify(f'{CORE_NAME} {PARAMETER}')}"

    assert bare_key not in keys, (
        f"{bare_key!r} was published: a bare key means the parameter is not joined into the "
        f"ability key before it is published — expected {joined_key!r} instead. keys={sorted(keys)}"
    )
    assert joined_key in keys, sorted(keys)
