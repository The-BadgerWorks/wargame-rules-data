# AI-Assisted: Claude Code (model: claude-opus-5) - The FR-034 fixture dry-run (004 task T071):
# tools/consumer_compat.py run UNMODIFIED against an enriched bundle carrying the seven new
# arrays and three new columns, ingesting into the literal reference-db-schema.md v1.2.0 schema
# with foreign keys on and pricing an army with zero differences from the pre-enrichment run.
"""The released consumer, unchanged, reading an enriched bundle.

`tools/consumer_compat.py` is the stand-in for `001`'s ingestor: it builds the SQLite schema
exactly as `reference-db-schema.md` **v1.2.0** declares it — the version the released consumers
were built against, *not* v1.3.0 — turns on real foreign keys, loads every array it knows about
into its table, and prices an army. This module runs it **unmodified** against a bundle that
carries every one of `004`'s additions.

The comparison is the point, and it is done twice over:

* against the **same bundle with the additions stripped out**, which is precisely what the
  producer emitted before this feature. Table counts, the priced total, and every line of the
  breakdown must be identical, because a consumer that does not read the new arrays must not be
  able to tell that they arrived.
* against the schema itself: the module's `TABLES` mapping is asserted to name **none** of the
  seven new arrays and **none** of the three new columns, so "it ignored them" is a property of
  the ingestor rather than a coincidence of this fixture.

This is the dry-run. Phase 9's T081 repeats it against a real pre-release candidate; catching a
schema mistake here costs a test run, catching it there costs an acquisition.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pipeline.build.bundle_emit import emit_bundle
from pipeline.build.canonical_json import encode_bundle
from tests import factories
from tests.contract.enrichment_bundle import (
    EXERCISE_ARMY,
    EXERCISE_ARMY_TOTAL,
    enriched_snapshot,
)
from tests.contract.test_additive_compatibility import (
    ENRICHMENT_ARRAYS,
    ENRICHMENT_COLUMN_PAIRS,
    NEW_ARRAYS,
    NEW_COLUMN_PAIRS,
)
from tools.consumer_compat import TABLES, run


def _write(bundle: dict[str, Any], path: Path) -> Path:
    path.write_bytes(encode_bundle(bundle))
    return path


def _stripped(bundle: dict[str, Any]) -> dict[str, Any]:
    """The same bundle as the producer emitted it **before** `004` — the honest baseline.

    Not a hand-written pre-enrichment fixture: the same build, with exactly the additions
    removed. Anything else would let a difference in the *fixture* masquerade as a difference in
    the consumer's behaviour, which is the one thing this comparison must not tolerate.
    """
    out = {name: value for name, value in bundle.items() if name not in NEW_ARRAYS}
    for array, column in sorted(NEW_COLUMN_PAIRS):
        out[array] = [
            {key: value for key, value in row.items() if key != column} for row in out[array]
        ]
    return out


@pytest.fixture(scope="module")
def bundles(tmp_path_factory) -> tuple[Path, Path]:  # type: ignore[no-untyped-def]
    directory = tmp_path_factory.mktemp("fr034")
    enriched = emit_bundle(enriched_snapshot(), factories.meta())
    return (
        _write(enriched, directory / "rules-enriched.json"),
        _write(_stripped(enriched), directory / "rules-pre-enrichment.json"),
    )


@pytest.fixture(scope="module")
def enriched_result(bundles: tuple[Path, Path]):  # type: ignore[no-untyped-def]
    return run(bundles[0], EXERCISE_ARMY)


@pytest.fixture(scope="module")
def pre_enrichment_result(bundles: tuple[Path, Path]):  # type: ignore[no-untyped-def]
    return run(bundles[1], EXERCISE_ARMY)


# --- the fixture really is enriched, or nothing below proves anything ---------------------------


def test_the_bundle_under_test_carries_all_seven_arrays_and_three_columns(
    bundles: tuple[Path, Path],
) -> None:
    bundle = json.loads(bundles[0].read_text(encoding="utf-8"))

    # Scoped to what 004 added, because that is what this fixture carries. 006's three arrays
    # and its two eligibility/equipment columns are emitted empty and omitted until T021 and
    # T030 populate them, and T042 is where this same proof is re-run over a loadout-extended
    # bundle.
    assert all(bundle[array] for array in ENRICHMENT_ARRAYS)
    for array, column in sorted(ENRICHMENT_COLUMN_PAIRS):
        assert any(column in row for row in bundle[array]), f"{array}.{column} is never set"


# --- the unmodified consumer ingests it ----------------------------------------------------------


def test_the_enriched_bundle_ingests_with_foreign_keys_enforced(enriched_result) -> None:  # type: ignore[no-untyped-def]
    assert enriched_result.tables["datasheet"] == 2
    assert enriched_result.tables["detachment"] == 2


def test_every_v1_2_0_guarantee_still_holds(enriched_result) -> None:  # type: ignore[no-untyped-def]
    assert enriched_result.violations == []


def test_the_ingestor_names_none_of_the_new_arrays_or_columns() -> None:
    """ "It ignored them" is a property of the ingestor, not a coincidence of this fixture."""
    assert set(TABLES) & NEW_ARRAYS == set()

    named_columns = {column for _table, columns in TABLES.values() for column in columns}
    assert named_columns & {column for _array, column in NEW_COLUMN_PAIRS} == set()


# --- and prices identically to the pre-enrichment run (FR-034) ----------------------------------


def test_the_priced_total_is_unchanged_by_the_additions(  # type: ignore[no-untyped-def]
    enriched_result, pre_enrichment_result
) -> None:
    assert enriched_result.army_total == pre_enrichment_result.army_total == EXERCISE_ARMY_TOTAL


def test_every_line_of_the_breakdown_is_unchanged(  # type: ignore[no-untyped-def]
    enriched_result, pre_enrichment_result
) -> None:
    assert enriched_result.army_lines == pre_enrichment_result.army_lines


def test_every_table_loads_the_same_number_of_rows(  # type: ignore[no-untyped-def]
    enriched_result, pre_enrichment_result
) -> None:
    assert enriched_result.tables == pre_enrichment_result.tables


def test_the_awkward_pricing_cases_are_actually_exercised(enriched_result) -> None:  # type: ignore[no-untyped-def]
    """A run that priced nothing interesting would pass the comparison and prove nothing.

    Every one of these three is a v1.2.0 addition, and each changes the answer: without the
    copy-index lookup the third Warden costs 90, without the round-up the six-model unit costs
    90, and without the wargear row the banner is free.
    """
    warden = [line for line in enriched_result.army_lines if "FEN WARDEN" in line]

    assert [line.rsplit(": ", 1)[1] for line in warden] == ["90", "90", "100", "175"]
    assert any("+15" in line for line in enriched_result.army_lines)
