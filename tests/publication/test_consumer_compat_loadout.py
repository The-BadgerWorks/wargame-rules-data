# AI-Assisted: Claude Code (model: claude-opus-5) - The FR-020 fixture dry-run (006 task T042):
# tools/consumer_compat.py run UNMODIFIED against a loadout-extended bundle carrying the three new
# arrays and four new columns, ingesting into the literal reference-db-schema.md v1.2.0 schema with
# foreign keys on and pricing an army with zero differences from the pre-006 run.
"""The released consumer, unchanged again, reading a loadout-extended bundle.

`tools/consumer_compat.py` builds the SQLite schema exactly as `reference-db-schema.md` **v1.2.0**
declares it — the version the released consumers were built against, *not* v1.5.0 — turns on real
foreign keys, loads every array it knows about, and prices an army. Its own docstring says it
"stays at v1.2.0 on purpose", and this module is why: teaching it the newer tables would quietly
delete the evidence that a consumer which never learned them is unaffected.

Three comparisons, because each rules out a different way of being wrong:

* against the **same bundle with `006`'s additions stripped out** — the honest baseline, since it
  is the same build minus exactly the additions, so a difference cannot come from the fixture
  having moved;
* against the **`004` enriched run**, whose priced total and breakdown lines must be identical,
  which is what "zero differences from the pre-006 fixture run" means in terms; and
* against the ingestor's own `TABLES` map, which must name none of the three arrays and none of
  the four columns — so "it ignored them" is a property of the ingestor rather than a coincidence
  of this fixture.

This is the dry run. `T045` repeats it against a real pre-release candidate; catching a schema
mistake here costs a test run, catching it there costs an acquisition.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pipeline.build.bundle_emit import emit_bundle
from pipeline.build.canonical_json import encode_bundle
from tests import factories
from tests.contract.enrichment_bundle import enriched_snapshot
from tests.contract.loadout_bundle import EXERCISE_ARMY, EXERCISE_ARMY_TOTAL, loadout_snapshot
from tests.contract.test_additive_compatibility import (
    LOADOUT_ARRAYS,
    LOADOUT_COLUMN_PAIRS,
    NEW_ARRAYS,
    NEW_COLUMN_PAIRS,
)
from tools.consumer_compat import TABLES, run

#: The table whose row count the loadout fixture legitimately moves, and the only one.
#:
#: `tests/contract/loadout_bundle.py` gives the Warden two extra weapon lines so the multi-item
#: swap has a genuinely distinct pair on each side — otherwise a per-item link could not be told
#: from a coincidence. That is a change to the *fixture*, not to what a consumer sees of `006`, so
#: it is named here and asserted, rather than skipped over by comparing a filtered subset.
_FIXTURE_WIDENED_TABLE = "datasheet_weapon"


def _write(bundle: dict[str, Any], path: Path) -> Path:
    path.write_bytes(encode_bundle(bundle))
    return path


def _stripped(bundle: dict[str, Any]) -> dict[str, Any]:
    """The same bundle as the producer emitted it **before** `006`.

    `004`'s arrays and columns stay: this is the pre-*loadout* baseline, not the
    pre-enrichment one, because the consumer whose compatibility `006` promises is the one
    released after `004`.
    """
    out = {name: value for name, value in bundle.items() if name not in LOADOUT_ARRAYS}
    for array, column in sorted(LOADOUT_COLUMN_PAIRS):
        out[array] = [
            {key: value for key, value in row.items() if key != column} for row in out[array]
        ]
    return out


@pytest.fixture(scope="module")
def bundles(tmp_path_factory) -> tuple[Path, Path, Path]:  # type: ignore[no-untyped-def]
    directory = tmp_path_factory.mktemp("fr020")
    loadout = emit_bundle(loadout_snapshot(), factories.meta())
    return (
        _write(loadout, directory / "rules-loadout.json"),
        _write(_stripped(loadout), directory / "rules-pre-loadout.json"),
        _write(
            emit_bundle(enriched_snapshot(), factories.meta()), directory / "rules-enriched.json"
        ),
    )


@pytest.fixture(scope="module")
def loadout_result(bundles: tuple[Path, Path, Path]):  # type: ignore[no-untyped-def]
    return run(bundles[0], EXERCISE_ARMY)


@pytest.fixture(scope="module")
def pre_loadout_result(bundles: tuple[Path, Path, Path]):  # type: ignore[no-untyped-def]
    return run(bundles[1], EXERCISE_ARMY)


@pytest.fixture(scope="module")
def enriched_result(bundles: tuple[Path, Path, Path]):  # type: ignore[no-untyped-def]
    return run(bundles[2], EXERCISE_ARMY)


# --- the fixture really is loadout-extended, or nothing below proves anything --------------------


def test_the_bundle_under_test_carries_every_array_and_every_column(
    bundles: tuple[Path, Path, Path],
) -> None:
    """All twenty-nine arrays non-empty and all seven added columns set.

    This is the assertion `tests/publication/test_consumer_compat_enriched.py` had to scope to
    `004`'s own additions, because a `004`-era fixture carries no `006` row to check. It is
    unscoped here — `NEW_ARRAYS` and `NEW_COLUMN_PAIRS` are the full sets — which is what makes
    everything below a proof rather than a proof about eight of eleven arrays.
    """
    bundle = json.loads(bundles[0].read_text(encoding="utf-8"))

    assert all(bundle[array] for array in NEW_ARRAYS)
    for array, column in sorted(NEW_COLUMN_PAIRS | LOADOUT_COLUMN_PAIRS):
        assert any(column in row for row in bundle[array]), f"{array}.{column} is never set"


# --- the unmodified consumer ingests it ----------------------------------------------------------


def test_the_loadout_bundle_ingests_with_foreign_keys_enforced(loadout_result) -> None:  # type: ignore[no-untyped-def]
    assert loadout_result.tables["datasheet"] == 2
    assert loadout_result.tables["detachment"] == 2
    # v1.2.0 declares no table for any of `006`'s arrays, so none is loaded and none is reported.
    # Asserted as an absence from the result rather than as a zero count, because a zero count
    # would mean the ingestor had grown the table and found nothing to put in it.
    assert "datasheet_option_choice_item" not in loadout_result.tables
    assert "datasheet_equipment_group" not in loadout_result.tables


def test_every_v1_2_0_guarantee_still_holds(loadout_result) -> None:  # type: ignore[no-untyped-def]
    assert loadout_result.violations == []
    assert loadout_result.ok


def test_the_ingestor_names_none_of_the_loadout_arrays_or_columns() -> None:
    """ "It ignored them" is a property of the ingestor, not a coincidence of this fixture."""
    assert set(TABLES) & LOADOUT_ARRAYS == set()

    named_columns = {column for _table, columns in TABLES.values() for column in columns}
    assert named_columns & {column for _array, column in LOADOUT_COLUMN_PAIRS} == set()


# --- and prices identically to the pre-006 run (FR-020, SC-006) ---------------------------------


def test_the_priced_total_is_unchanged_by_the_loadout_additions(  # type: ignore[no-untyped-def]
    loadout_result, pre_loadout_result, enriched_result
) -> None:
    """One number, three ways of arriving at it, including the `004` run's own."""
    assert (
        loadout_result.army_total
        == pre_loadout_result.army_total
        == enriched_result.army_total
        == EXERCISE_ARMY_TOTAL
    )


def test_every_line_of_the_breakdown_is_unchanged(  # type: ignore[no-untyped-def]
    loadout_result, pre_loadout_result, enriched_result
) -> None:
    """Not just the total: a compensating pair of errors sums to the right answer."""
    assert loadout_result.army_lines == pre_loadout_result.army_lines
    assert loadout_result.army_lines == enriched_result.army_lines


def test_every_table_loads_the_same_number_of_rows(  # type: ignore[no-untyped-def]
    loadout_result, pre_loadout_result
) -> None:
    assert loadout_result.tables == pre_loadout_result.tables


def test_only_the_fixture_widened_table_differs_from_the_enriched_run(  # type: ignore[no-untyped-def]
    loadout_result, enriched_result
) -> None:
    """The one difference from `004`'s run, named rather than filtered away.

    A comparison that quietly excluded a table would be the easiest place to hide a real
    regression, so the difference is stated as an equality on everything else and an inequality
    on the one table the fixture deliberately widened.
    """
    differing = {
        name
        for name, count in loadout_result.tables.items()
        if enriched_result.tables[name] != count
    }

    assert differing == {_FIXTURE_WIDENED_TABLE}
    assert loadout_result.tables[_FIXTURE_WIDENED_TABLE] == (
        enriched_result.tables[_FIXTURE_WIDENED_TABLE] + 2
    )


def test_the_awkward_pricing_cases_are_still_exercised(loadout_result) -> None:  # type: ignore[no-untyped-def]
    """A run that priced nothing interesting would pass every comparison and prove nothing."""
    warden = [line for line in loadout_result.army_lines if "FEN WARDEN" in line]

    assert [line.rsplit(": ", 1)[1] for line in warden] == ["90", "90", "100", "175"]
    assert any("+15" in line for line in loadout_result.army_lines)
