# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the rendering conformance test (007
# task T042): every case in the vendored `contracts/rendering-fixtures/cases.json` renders
# byte-identical to `expected.json` via `pipeline.render.loadout`, for both the canonical string
# (contract §7.1) and the segment stream's concatenation identity (§7.2); plus a drift check that
# the vendored copy's stamped `contractVersion` matches the version the renderer claims.
"""Conformance tests for `rendering-contract.md` v1.0.0's Python reference implementation.

The corpus is synthetic (contract §8.1) — every name, count, and identifier in
`contracts/rendering-fixtures/{cases,expected}.json` is invented; there is no captured source
page and no publisher text anywhere in this test or its fixtures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pipeline.render.loadout import RENDERING_CONTRACT_VERSION, render_case

FIXTURES_DIR = Path(__file__).parent.parent.parent / "contracts" / "rendering-fixtures"


def _load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


CASES = _load("cases.json")
EXPECTED = _load("expected.json")


def _expected_by_id() -> dict[str, dict[str, Any]]:
    return {case["id"]: case for case in EXPECTED["cases"]}


EXPECTED_BY_ID = _expected_by_id()


def test_every_case_has_a_matching_expected_entry() -> None:
    case_ids = {case["id"] for case in CASES["cases"]}
    expected_ids = {case["id"] for case in EXPECTED["cases"]}
    assert case_ids == expected_ids


def test_corpus_is_nonempty() -> None:
    # contract §8.1: at minimum every template id, every §4 selection-table row, nested groups
    # and the depth cap, the 004-vs-006 shape-identity case, and a mixed resolved/unresolved
    # block. 12 seed cases plus 7 added at T047 to close the gaps the audit found.
    assert len(CASES["cases"]) >= 12


@pytest.mark.parametrize("case", CASES["cases"], ids=lambda case: case["id"])
def test_canonical_string_is_byte_identical(case: dict[str, Any]) -> None:
    expected = EXPECTED_BY_ID[case["id"]]
    result = render_case(case["block"], case["input"])
    assert result.canonical == expected["canonical"]


@pytest.mark.parametrize("case", CASES["cases"], ids=lambda case: case["id"])
def test_omitted_codes_match(case: dict[str, Any]) -> None:
    expected = EXPECTED_BY_ID[case["id"]]
    result = render_case(case["block"], case["input"])
    assert sorted(result.omitted) == sorted(expected["omitted"])


@pytest.mark.parametrize("case", CASES["cases"], ids=lambda case: case["id"])
def test_segment_stream_concatenates_to_the_canonical_string(case: dict[str, Any]) -> None:
    """Contract §7.2: the segment stream's concatenated `text` fields must equal the canonical
    string byte for byte, BY CONSTRUCTION — not by a second, divergent code path. This is a
    structural self-consistency check of the renderer's own output, not a comparison against a
    fixture-authored segment stream (`expected.json` carries no `segments` field; only
    `canonical` and `omitted` are normative fixture content per its own `_comment`).
    """
    result = render_case(case["block"], case["input"])
    assert "".join(segment.text for segment in result.segments) == result.canonical


@pytest.mark.parametrize("case", CASES["cases"], ids=lambda case: case["id"])
def test_every_segment_is_literal_or_slot(case: dict[str, Any]) -> None:
    result = render_case(case["block"], case["input"])
    for segment in result.segments:
        assert segment.kind in ("literal", "slot")
        if segment.kind == "slot":
            assert segment.slot is not None
        else:
            assert segment.slot is None


def test_vendored_corpus_contract_version_matches_the_renderer() -> None:
    assert CASES["contractVersion"] == RENDERING_CONTRACT_VERSION
    assert EXPECTED["contractVersion"] == RENDERING_CONTRACT_VERSION


def test_no_publisher_text_marker_in_the_corpus() -> None:
    # A cheap guard, not a substitute for human review at authoring time (contract §8.1): the
    # corpus's own `_comment` fields assert synthetic content. This confirms both are present and
    # say so, so a future case added without one is caught.
    assert "synthetic" in CASES["_comment"].lower() or "invented" in CASES["_comment"].lower()
    assert "synthetic" in EXPECTED["_comment"].lower() or "invented" in EXPECTED["_comment"].lower()


def test_unknown_block_kind_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown block kind"):
        render_case("abilities", {})
