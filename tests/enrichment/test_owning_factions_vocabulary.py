# AI-Assisted: Claude Code (model: claude-sonnet-5) - New failing-first test for a proven
# arm-vocabulary defect found while diagnosing 009's live coverage collapse (shape-decision
# session): `_owning_factions` (`curate/assemble.py`) keys its detail-source-faction-id -> owning
# scope map by `scope.entry.detail_source_faction_id` alone, never consulting
# `detail_source_faction_code` the way `resolve_factions`/`match_units`'s `in_scope` filter
# already does (009 T020/T021, `_detail_ids_for`). Under `csv` mode every unclaimed export row's
# `faction_id` is the export's own code, which never appears in this dict, so the FR-026/FR-035
# "ships on the best price known" detail-only safety net silently recovers zero datasheets instead
# of the several hundred `html` mode recovers from the identical live roster -- proven live this
# session to be effectively the whole of the measured ~646-datasheet collapse.
"""``_owning_factions`` must honour both arm vocabularies, exactly as `resolve_factions` does.

Reuses `pipeline.reconcile.match.FactionScope`/`FactionMapEntry` directly rather than building a
whole snapshot — `_owning_factions` is a pure function of a scope sequence, and the defect is
entirely in which key it builds, not in anything downstream.
"""

from __future__ import annotations

from pipeline.curate.assemble import _owning_factions
from pipeline.models.authored import FactionMapEntry
from pipeline.reconcile.match import FactionScope


def _scope(entry: FactionMapEntry, *, detail_faction_ids: tuple[str, ...]) -> FactionScope:
    return FactionScope(
        faction_id=entry.faction_id, entry=entry, detail_faction_ids=detail_faction_ids
    )


def test_a_faction_with_no_code_is_owned_by_its_id_alone() -> None:
    """Unchanged behaviour: a record with no `detail_source_faction_code` set."""
    entry = FactionMapEntry(
        mfm_slug="unchanged-faction",
        faction_id="f-unchanged-faction",
        detail_source_faction_id="unchanged-faction",
    )
    scope = _scope(entry, detail_faction_ids=("unchanged-faction",))

    owners = _owning_factions([scope])

    assert owners == {"unchanged-faction": scope}


def test_a_csv_shaped_export_row_finds_its_owner_by_code() -> None:
    """The proven live defect: under `csv` mode an unclaimed row's `faction_id` is the export's
    own code (e.g. `"SM"`), never the html-arm slug `detail_source_faction_id` carries. Before
    the fix, `owners.get("SM")` is `None` for a scope whose `detail_source_faction_id` is
    `"space-marines"` even though its `detail_source_faction_code` is `"SM"` — exactly the gap
    that silently discarded the whole FR-026/FR-035 detail-only recovery pass this session
    measured live.
    """
    entry = FactionMapEntry(
        mfm_slug="space-marines",
        faction_id="f-space-marines",
        detail_source_faction_id="space-marines",
        detail_source_faction_code="SM",
    )
    scope = _scope(entry, detail_faction_ids=("space-marines", "SM"))

    owners = _owning_factions([scope])

    assert owners.get("SM") is scope, (
        "a csv-mode row keyed by the export's own code must resolve to the same owning scope an "
        "html-mode row keyed by the slug already does -- both are the SAME faction's detail id, "
        "in the two vocabularies FactionMapEntry itself documents"
    )
    assert owners.get("space-marines") is scope


def test_a_chapter_group_still_prefers_the_parent_root_under_either_vocabulary() -> None:
    """`_owning_factions`'s own docstring: several curated factions can share one detail id, and
    an unclaimed row must file under the group's root parent so every chapter can see it (§3.5
    query rule) -- unaffected by which vocabulary supplied the shared id.
    """
    parent = FactionMapEntry(
        mfm_slug="space-marines",
        faction_id="f-space-marines",
        detail_source_faction_id="space-marines",
        detail_source_faction_code="SM",
    )
    chapter = FactionMapEntry(
        mfm_slug="ember-chapter",
        faction_id="f-ember-chapter",
        parent_faction_id="f-space-marines",
        detail_source_faction_id="space-marines",
        detail_source_faction_code="SM",
    )
    parent_scope = _scope(parent, detail_faction_ids=("space-marines", "SM"))
    chapter_scope = _scope(chapter, detail_faction_ids=("space-marines", "SM", "space-marines"))

    owners = _owning_factions([parent_scope, chapter_scope])

    assert owners["SM"] is parent_scope
    assert owners["space-marines"] is parent_scope
