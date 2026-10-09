# AI-Assisted: Claude Code (model: Claude Sonnet 5) - 2026-10-09 pipeline P2 task 3: the spec's
# own failing-first receipt for `detachments.chapterKeyword` -- removing the emitter change
# (`_emit_detachments`'s `chapterKeyword` key) makes this fail on the missing key, and removing
# the schema property instead fails `validate_bundle` on the unmapped `additionalProperties`.
"""`detachments.chapterKeyword` is emitted when curation binds one, and omitted otherwise."""

from __future__ import annotations

from pipeline.build.bundle_emit import BUNDLE_FORMAT_VERSION, emit_bundle
from pipeline.schema_validation import validate_bundle
from tests import factories


def test_exactly_one_of_two_detachments_carries_the_chapter_keyword() -> None:
    """Remove the emitter change and this fails on a missing key (the spec's own receipt)."""
    scoped = factories.detachment("d-anvil-vigil").model_copy(
        update={"chapter_keyword": "FEN WARDENS"}
    )
    plain = factories.detachment("d-fx-charge").model_copy(update={"name": "Thornlight Charge"})
    bundle = emit_bundle(factories.snapshot(detachments=[scoped, plain]), factories.meta())
    validate_bundle(bundle, source="chapter-keyword emit test")
    rows = {row["id"]: row for row in bundle["detachments"]}
    assert rows["d-anvil-vigil"]["chapterKeyword"] == "FEN WARDENS"
    assert "chapterKeyword" not in rows["d-fx-charge"], "absence must be omission, never null"
    assert bundle["bundleFormatVersion"] == BUNDLE_FORMAT_VERSION == 1
