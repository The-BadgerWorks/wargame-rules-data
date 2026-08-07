# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the ceiling-agreement test after the
# 2026-08-06 summary-length raise left pipeline/models/authored.py at 400 while six JSON schemas
# had moved to 1 000. Nothing caught it: the fixtures carry no summary long enough to tell the
# two numbers apart, so the first thing to notice was a live build dying in the curation loader
# after it had already acquired every page from both upstreams.
"""The authored-summary ceiling is one number, asserted to be one number.

Four JSON schemas under `schemas/curation/`, one field of `schemas/bundle.schema.json`, a pydantic
model, and `pipeline/validate/ip_scan.py`'s blocking over-length guard all encode the same limit,
and none of them can import from the others. That is six opportunities for a partial edit, and a
partial edit is invisible until a record lands between the old ceiling and the new one.

So the agreement is asserted directly. These tests fail on the *next* partial edit, in under a
second, naming the file that was missed — which is the whole difference from finding out during a
release build.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from pipeline.models.authored import SUMMARY_MAX_LENGTH, FactionRuleSummary
from pipeline.validate.ip_scan import IP_SCAN_MAX_CHARS

ROOT = Path(__file__).resolve().parents[2]

#: Every curation schema whose records carry an authored `summary`.
CURATION_SCHEMAS = (
    "abilities",
    "faction-rules",
    "detachment-rules",
    "glossary",
)


def _schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def _summary_nodes(node: Any) -> list[dict[str, Any]]:
    """Every `summary` property anywhere in a schema, at any depth."""
    found: list[dict[str, Any]] = []
    if isinstance(node, dict):
        properties = node.get("properties")
        if isinstance(properties, dict) and isinstance(properties.get("summary"), dict):
            found.append(properties["summary"])
        for value in node.values():
            found.extend(_summary_nodes(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(_summary_nodes(value))
    return found


@pytest.mark.parametrize("name", CURATION_SCHEMAS)
def test_each_curation_schema_caps_summary_at_the_one_ceiling(name: str) -> None:
    nodes = _summary_nodes(_schema(ROOT / "schemas" / "curation" / f"{name}.schema.json"))

    assert nodes, f"{name}.schema.json declares no summary property at all"
    for node in nodes:
        assert node.get("maxLength") == SUMMARY_MAX_LENGTH, (
            f"schemas/curation/{name}.schema.json caps summary at {node.get('maxLength')}, "
            f"but pipeline/models/authored.py caps it at {SUMMARY_MAX_LENGTH}"
        )


def test_the_bundle_schema_caps_every_summary_at_the_same_ceiling() -> None:
    nodes = _summary_nodes(_schema(ROOT / "schemas" / "bundle.schema.json"))

    assert len(nodes) == 4, f"expected four summary-bearing arrays, found {len(nodes)}"
    for node in nodes:
        assert node.get("maxLength") == SUMMARY_MAX_LENGTH


def test_the_pydantic_model_refuses_exactly_one_character_past_the_ceiling() -> None:
    """The bound is enforced, not merely declared — and at the boundary, not near it."""
    at_the_line = FactionRuleSummary(
        summary_key="faction:f-x:y",
        name="Y",
        summary="m" * SUMMARY_MAX_LENGTH,
        mechanic_digest="d" * 32,
    )
    assert len(at_the_line.summary) == SUMMARY_MAX_LENGTH

    with pytest.raises(ValueError, match="at most"):
        FactionRuleSummary(
            summary_key="faction:f-x:y",
            name="Y",
            summary="m" * (SUMMARY_MAX_LENGTH + 1),
            mechanic_digest="d" * 32,
        )


def test_the_ip_scans_blocking_ceiling_is_not_below_the_summary_ceiling() -> None:
    """A legal summary must never read as retained publisher prose.

    `IP_SCAN_MAX_CHARS` is the length at which V8 calls a string prose whatever it claims to be,
    and it is a **blocking** finding. Left below the summary ceiling it would refuse records the
    schemas and the model both accept, and it would do it in the validate stage of a release
    build rather than at authoring time.
    """
    assert IP_SCAN_MAX_CHARS >= SUMMARY_MAX_LENGTH
