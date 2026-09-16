# AI-Assisted: Claude Code (model: Claude Sonnet 5) - New test for 010 R13 task 1: the authored
# WargearAbilityEntry model, its schema, and load_authored's new "wargear-abilities" stem.
"""010 R13 task 1: authored wargear-abilities entries.

`WargearAbilityEntry` is the Owner-authored, faction-scoped record round 13 adds ahead of the
curated table, emitter, and linker (later tasks). This file proves only what task 1 owns: the
model's id derivation and its two blocking validations (`review_state` and `reviewed_by`), and
that `load_authored` treats an absent `wargear-abilities.json` as empty and a present one as
loaded -- the same "authored, validated on read, never written by the pipeline" contract every
other `curation/` file already has.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from pydantic import ValidationError

from pipeline.curate.authored import load_authored
from pipeline.models.authored import WargearAbilityEntry

FIXTURE_CURATION = Path(__file__).resolve().parents[2] / "fixtures" / "sample" / "curation"

ENTRY = {
    "faction_id": "f-example",
    "name": "Hover Limpet",
    "aliases": ["hover limpet (one per unit)"],
    "summary": "Placeholder: the bearer's unit ignores one placeholder modifier.",
    "review_state": "approved",
    "reviewed_by": "owner-placeholder",
    "reviewed_at": "2026-09-16",
}


def test_entry_id_is_derived_from_faction_and_name() -> None:
    assert WargearAbilityEntry.model_validate(ENTRY).id == "wga-example-hover-limpet"


def test_only_approved_entries_are_valid() -> None:
    with pytest.raises(ValidationError):
        WargearAbilityEntry.model_validate({**ENTRY, "review_state": "draft"})


def test_reviewed_by_is_required() -> None:
    with pytest.raises(ValidationError):
        WargearAbilityEntry.model_validate({k: v for k, v in ENTRY.items() if k != "reviewed_by"})


def test_missing_file_loads_as_empty(tmp_path: Path) -> None:
    shutil.copytree(FIXTURE_CURATION, tmp_path / "curation")
    content = load_authored(tmp_path / "curation")
    assert content.wargear_abilities == ()


def test_present_file_loads(tmp_path: Path) -> None:
    shutil.copytree(FIXTURE_CURATION, tmp_path / "curation")
    (tmp_path / "curation" / "wargear-abilities.json").write_text(
        json.dumps([ENTRY]), encoding="utf-8"
    )
    content = load_authored(tmp_path / "curation")
    assert [e.id for e in content.wargear_abilities] == ["wga-example-hover-limpet"]
