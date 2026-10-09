# AI-Assisted: Claude Code (model: Claude Sonnet 5) - New test for pipeline P2 task 1: the
# authored DetachmentChapterEntry model, its schema, and load_authored's new
# "detachment-chapters" stem.
"""Pipeline P2 task 1: authored detachment-chapters entries.

`DetachmentChapterEntry` is the Owner-authored record that binds a keyword-only-chapter
detachment, on a parent faction's page, to its chapter keyword (spec 2026-10-09 §1.2). This
file proves only what task 1 owns: the model's two required fields plus the optional `note`,
that an unknown key is refused by both the model and the schema, and that `load_authored` treats
an absent `detachment-chapters.json` as empty and a present one as loaded and referenced -- the
same "authored, validated on read, never written by the pipeline" contract every other
`curation/` file already has.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from pydantic import ValidationError

from pipeline.curate.authored import authored_entity_refs, load_authored
from pipeline.models.authored import DetachmentChapterEntry
from pipeline.schema_validation import SchemaValidationError, validate_authored

FIXTURE_CURATION = Path(__file__).resolve().parents[2] / "fixtures" / "sample" / "curation"

ENTRY = {"faction_id": "f-test-parent", "name": "Test Vigil", "chapter_keyword": "FEN WARDENS"}


def test_a_minimal_entry_validates() -> None:
    entry = DetachmentChapterEntry.model_validate(ENTRY)
    assert (entry.faction_id, entry.name, entry.chapter_keyword, entry.note) == (
        "f-test-parent",
        "Test Vigil",
        "FEN WARDENS",
        None,
    )


def test_an_unknown_key_is_refused() -> None:
    with pytest.raises(ValidationError):
        DetachmentChapterEntry.model_validate({**ENTRY, "detachment_id": "d-test-vigil"})


def test_the_schema_refuses_an_id_keyed_entry() -> None:
    with pytest.raises(SchemaValidationError, match="Additional properties"):
        validate_authored("detachment-chapters", [{**ENTRY, "detachment_id": "d-test-vigil"}])


def test_missing_file_loads_as_empty(tmp_path: Path) -> None:
    shutil.copytree(FIXTURE_CURATION, tmp_path / "curation")
    assert load_authored(tmp_path / "curation").detachment_chapters == ()


def test_present_file_loads_and_references_its_faction(tmp_path: Path) -> None:
    shutil.copytree(FIXTURE_CURATION, tmp_path / "curation")
    (tmp_path / "curation" / "detachment-chapters.json").write_text(
        json.dumps([ENTRY]), encoding="utf-8"
    )
    content = load_authored(tmp_path / "curation")
    assert [e.name for e in content.detachment_chapters] == ["Test Vigil"]
    assert ("detachment-chapters.json", "faction_id", "f-test-parent") in authored_entity_refs(
        content
    )
