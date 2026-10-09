# AI-Assisted: Claude Code (model: claude-sonnet-5) - 2026-10-09 pipeline P2 task 4: failing-first
# tests for `wargearOptionsText` (Owner ruling 3): a datasheet's option rows' text, markup
# stripped, NFKC-normalised, whitespace folded -- case and punctuation KEPT, unlike
# `hard_normalise`'s digest projection. Proves `_option_structure` populates `_OptionOutcome.text`
# from EVERY option row regardless of whether `parse_row` can resolve it structurally, that the
# field reaches the bundle via `omit_absent` (present/absent symmetry), and that a full offline
# build over `fixtures/minimal` wires the reader end to end.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Fix round 1 (review findings 2 and 3): added
# a direct `published_text` NFKC receipt (nothing else here pinned the NFKC step), and put real
# `<b>...</b>` markup into the injected option row so the end-to-end test's `"<" not in ...`
# assertion has something to catch rather than being vacuously true.
"""Tests for the one field downstream of `normalize` the Owner has ruled publishable."""

from __future__ import annotations

import shutil
from pathlib import Path

from pipeline.build.bundle_emit import emit_bundle
from pipeline.curate.assemble import _option_structure
from pipeline.curate.authored import AuthoredContent
from pipeline.normalize.ip_strip import published_text
from pipeline.parse.wahapedia_csv import read_text
from pipeline.schema_validation import validate_bundle
from tests import factories


def test_published_text_applies_nfkc_and_keeps_case_and_punctuation() -> None:
    """Direct unit receipt for the NFKC step, which nothing else in this file pins: deleting the
    `unicodedata.normalize("NFKC", ...)` call from `published_text` fails no other test, because
    every other fixture's invented prose is already NFKC-normal. `ﬁeld` (U+FB01, the "fi"
    ligature) is a synthetic compatibility character no ordinary sentence would contain; NFKC
    decomposes it to the two letters `f` + `i`, so its presence in the output is the receipt.
    Case (`Test`) and the trailing full stop are asserted in the same test so a future change
    cannot "fix" one by discarding the other."""
    raw = "This Test ﬁeld can be used."
    assert published_text(raw, field="test.field") == "This Test field can be used."


ROWS = (
    "datasheet_id|line|button|description|\n"
    "FX01|1|Wargear Options|<b>This model</b> can be equipped with 1   test lantern.|\n"
    "FX01|2|Wargear Options|This model's test blade can be replaced with 1 test maul.|\n"
)


def test_option_rows_publish_as_text_with_markup_stripped_and_case_kept() -> None:
    """Red before: `_OptionOutcome` has no `text`. Also pins the `hard_normalise` contradiction:
    the expected value keeps its capital T and its full stops."""
    outcome = _option_structure(
        "FX01",
        "ds-fx-one",
        {"Datasheets_options.csv": read_text("Datasheets_options.csv", ROWS)},
        AuthoredContent(),
        weapons=(),
        priced=(),
    )
    assert outcome.text == (
        "This model can be equipped with 1 test lantern.\n"
        "This model's test blade can be replaced with 1 test maul."
    )


def test_no_option_rows_means_no_text() -> None:
    outcome = _option_structure(
        "FX02",
        "ds-fx-two",
        {
            "Datasheets_options.csv": read_text(
                "Datasheets_options.csv", "datasheet_id|line|button|description|\n"
            )
        },
        AuthoredContent(),
        weapons=(),
        priced=(),
    )
    assert outcome.text is None


def test_the_text_reaches_the_bundle_and_is_absent_without_rows() -> None:
    with_text = factories.datasheet().model_copy(
        update={"wargear_options_text": "This model can be equipped with 1 test lantern."}
    )
    without = factories.datasheet().model_copy(
        update={"datasheet_id": "ds-fx-plain", "name": "Test Plain"}
    )
    bundle = emit_bundle(factories.snapshot(datasheets=[with_text, without]), factories.meta())
    validate_bundle(bundle, source="options text emit test")
    rows = {r["id"]: r for r in bundle["datasheets"]}
    assert (
        rows[with_text.datasheet_id]["wargearOptionsText"]
        == "This model can be equipped with 1 test lantern."
    )
    assert "wargearOptionsText" not in rows["ds-fx-plain"]


# --- end-to-end: the reader is wired through a full offline build ------------------------------

MINIMAL = Path(__file__).resolve().parents[2] / "fixtures" / "minimal"
FIRST_ID = "AV01"
SECOND_ID = "AV02"
_OPTION_TEXT = "This model can be equipped with 1 <b>test lantern</b> for free."


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


def _fixture_with_option_row(tmp: Path) -> Path:
    """Copy `fixtures/minimal` to `tmp` and append one option row for `FIRST_ID` only — the
    harness `tests/contract/test_loadout_equipment_build.py` and
    `tests/contract/test_footnote_row_routing_build.py` both use for an in-tree-untouched
    receipt. `fixtures/minimal` itself carries zero option rows, so this is the only way to
    prove the reader end to end without editing a tracked fixture (forbidden by this task)."""
    fixtures = tmp / "fixtures"
    shutil.copytree(MINIMAL, fixtures, ignore=shutil.ignore_patterns("build"))
    path = fixtures / "wahapedia" / "Datasheets_options.csv"
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    row = f"{FIRST_ID}|1|Wargear Options|{_OPTION_TEXT}|"
    path.write_text("﻿" + "\n".join([*lines, row]) + "\n", encoding="utf-8")
    return fixtures


def _name_to_detail_id(fixtures: Path) -> dict[str, str]:
    path = fixtures / "wahapedia" / "Datasheets.csv"
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    header = lines[0].split("|")
    id_col = header.index("id")
    name_col = header.index("name")
    mapping: dict[str, str] = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        cells = line.split("|")
        # The bundle publishes datasheet names upper-cased (see `_detail_datasheet_fields`'s
        # own upper-casing of printed characteristics); keyed upper-cased here so the match
        # survives that projection.
        mapping[cells[name_col].upper()] = cells[id_col]
    return mapping


def test_a_full_offline_build_publishes_the_minimal_fixtures_option_rows(tmp_path: Path) -> None:
    """Through `run_build` on an in-tmp copy of `fixtures/minimal`: the one datasheet whose
    `Datasheets_options.csv` row was injected carries `wargearOptionsText`; every other
    datasheet does not. No value contains `<` -- the markup in the row must be stripped, not
    merely passed through."""
    from pipeline.cli import run_build
    from pipeline.config import load_config
    from pipeline.exit_codes import ExitCode

    fixtures = _fixture_with_option_row(tmp_path / "f")
    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-options-text",
        fixtures_dir=fixtures,
        offline=True,
        output_root=tmp_path / "out",
        repository_root=_empty_repo(tmp_path / "repo"),
    )
    assert result.exit_code in (ExitCode.SUCCESS, ExitCode.ADVISORY_ONLY), [
        f.finding_code for f in result.findings if f.severity == "blocking"
    ]

    name_to_detail_id = _name_to_detail_id(fixtures)
    detail_ids_with_rows = {FIRST_ID}  # only FIRST_ID's row was injected

    ids_with_text: set[str] = set()
    ids_without_text: set[str] = set()
    for row in result.bundle["datasheets"]:
        detail_id = name_to_detail_id.get(str(row["name"]).upper())
        if detail_id is None:
            continue
        if "wargearOptionsText" in row:
            ids_with_text.add(detail_id)
            assert "<" not in str(row["wargearOptionsText"])
        else:
            ids_without_text.add(detail_id)

    assert ids_with_text, "nothing carried the field -- the reader is not wired through run_build"
    assert ids_with_text == detail_ids_with_rows
    assert SECOND_ID in ids_without_text
