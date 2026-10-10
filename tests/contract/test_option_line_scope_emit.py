# AI-Assisted: Claude Code (model: claude-sonnet-5) - 2026-10-09 pipeline P3 task 3 (spec §4.2
# P4b): failing-first tests that `datasheetOptionGroups.eligibleCompositionLines` reaches the
# bundle via `omit_absent` -- present for a scoped group, absent for an unscoped sibling -- and
# that `bundleFormatVersion` stays 1 (the addition is additive, not a layout release).
"""`eligibleCompositionLines` reaches the bundle, present/absent exactly as curated."""

from __future__ import annotations

from pipeline.build.bundle_emit import emit_bundle
from pipeline.models.curated import CuratedOptionGroup, OptionScope
from pipeline.schema_validation import validate_bundle
from tests import factories


def test_a_scoped_group_publishes_its_lines_and_an_unscoped_sibling_carries_no_key() -> None:
    scoped = CuratedOptionGroup(
        id="og-fx-scoped",
        line=1,
        scope=OptionScope.UNIT,
        eligible_composition_lines=(2, 3),
    )
    unscoped = CuratedOptionGroup(id="og-fx-unscoped", line=2, scope=OptionScope.UNIT)

    datasheet = factories.datasheet("ds-fx-line-scope-emit").model_copy(
        update={"option_groups": [scoped, unscoped]}
    )
    bundle = emit_bundle(factories.snapshot(datasheets=[datasheet]), factories.meta())
    validate_bundle(bundle, source="option line scope emit test")

    rows = {row["id"]: row for row in bundle["datasheetOptionGroups"]}
    assert rows["og-fx-scoped"]["eligibleCompositionLines"] == [2, 3]
    assert "eligibleCompositionLines" not in rows["og-fx-unscoped"]
    assert bundle["bundleFormatVersion"] == 1
