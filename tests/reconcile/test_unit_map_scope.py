# AI-Assisted: Claude Code (model: claude-sonnet-5) - New tests for `unit-map.json`'s optional
# `faction_id` (009 tasks T022/T023, data-model.md §1, risk R-C): stage 1's index becomes
# faction-scoped when an entry declares it, on the same two-tier shape the sibling alias index
# already uses, so a name shared across sibling factions cannot collapse six per-chapter
# identifiers into one -- the C1-breaching side effect `data-model.md` §1 names explicitly as the
# reason the field is optional in schema but mandatory in the authoring rule.
"""The C1 guard: six sibling factions sharing one unit name must keep six distinct identifiers.

`match_units` runs **once per faction scope**. Without `faction_id`, a single curated entry for
a name six chapters share would be picked up identically by all six calls and `registry.adopt`
the *same* `datasheet_id` under six different `datasheet_key(faction_id, name)` keys — the direct
breach of the Product Owner's C1 ruling (the 30-faction model, chapter identifiers included, is
HELD) that `plan.md` risk R-C names as a side effect a fix for something else could introduce.

The fixture below is the real Space Marine shape generalised to six invented chapters of one
invented parent, all sharing the parent's detail-source faction id (research D5's stage-2
docstring: "five Space Marine chapters ... share the parent's detail-source faction id
outright") and one shared unit name, with **no other narrowing signal available** (no Legends
split, no publication id, no chapter keyword record) — so stage 2 alone would report every one of
the six as `REC-AMBIGUOUS-MATCH` (six candidates, nothing to prefer with) if stage 1's scoped
identity did not resolve each one first.
"""

from __future__ import annotations

from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import FactionMapEntry, UnitMapEntry
from pipeline.reconcile.identity import IdRegistry
from pipeline.reconcile.match import FactionScope, MatchOutcome, match_units, resolve_factions

_CHAPTER_COUNT = 6

PARENT = FactionMapEntry(
    mfm_slug="iron-legion", faction_id="f-iron-legion", detail_source_faction_id="IL"
)
CHAPTERS = tuple(
    FactionMapEntry(
        mfm_slug=f"chapter-{n}",
        faction_id=f"f-chapter-{n}",
        parent_faction_id="f-iron-legion",
        detail_source_faction_id="IL",
    )
    for n in range(1, _CHAPTER_COUNT + 1)
)

#: One shared display name, one detail-source candidate per chapter, ALL visible to every
#: chapter's scope (the parent-fallback shape: `scope.detail_faction_ids` is `("IL",)` for every
#: one of the six, so `in_scope`/`detail_names` in a real build would carry all six candidates to
#: every chapter's own `match_units` call).
SHARED_NAME = "Iron Sentinel"
DETAIL_CANDIDATES = {f"IL0{n}": SHARED_NAME for n in range(1, _CHAPTER_COUNT + 1)}

#: Six curated entries, each scoped to its OWN chapter and naming its OWN detail row — the
#: correctly-authored shape rule 8 requires the moment a name is shared across siblings.
ENTRIES = tuple(
    UnitMapEntry(
        datasheet_id=f"ds-iron-sentinel-{n}",
        mfm_display_name=SHARED_NAME,
        wahapedia_datasheet_id=f"IL0{n}",
        confirmed_at="2026-08-18",
        confirmed_by="test-curator",
        faction_id=f"f-chapter-{n}",
    )
    for n in range(1, _CHAPTER_COUNT + 1)
)


def _authored(unit_map: tuple[UnitMapEntry, ...] = ENTRIES) -> AuthoredContent:
    return AuthoredContent(faction_map=(PARENT, *CHAPTERS), unit_map=unit_map)


def _scope_for(slug: str, content: AuthoredContent) -> FactionScope:
    outcome = resolve_factions([slug], content)
    assert outcome.scopes, f"{slug} did not resolve to a scope"
    return outcome.scopes[0]


def _run(n: int, content: AuthoredContent, registry: IdRegistry) -> MatchOutcome:
    return match_units(
        _scope_for(f"chapter-{n}", content),
        display_names=[SHARED_NAME],
        detail_names=DETAIL_CANDIDATES,
        detail_is_legends={},
        detail_source_ids={},
        detail_faction_keywords={},
        authored=content,
        registry=registry,
    )


def test_six_siblings_sharing_one_name_each_resolve_to_their_own_datasheet_id() -> None:
    content = _authored()
    registry = IdRegistry()

    resolved_ids = []
    for n in range(1, _CHAPTER_COUNT + 1):
        outcome = _run(n, content, registry)
        assert outcome.findings == [], f"chapter {n} should not need to fall through to stage 2"
        assert len(outcome.matches) == 1
        match = outcome.matches[0]
        assert match.stage == "identity"
        assert match.wahapedia_datasheet_id == f"IL0{n}"
        resolved_ids.append(match.datasheet_id)

    assert resolved_ids == [f"ds-iron-sentinel-{n}" for n in range(1, _CHAPTER_COUNT + 1)]
    assert len(set(resolved_ids)) == _CHAPTER_COUNT, "six distinct identifiers, none collapsed"


def test_a_chapters_scope_never_resolves_to_a_siblings_entry() -> None:
    """Cross-contamination check: chapter 1's own scope must never pick up chapter 2's entry."""
    content = _authored()
    outcome = _run(1, content, IdRegistry())

    assert outcome.matches[0].datasheet_id == "ds-iron-sentinel-1"
    assert outcome.matches[0].datasheet_id != "ds-iron-sentinel-2"


# -- T023: the index is scoped only when `faction_id` is present ---------------------------------


def test_an_entry_with_no_faction_id_still_matches_every_scope() -> None:
    """Omitted keeps today's global (unscoped) behaviour exactly (additive schema change)."""
    global_entry = UnitMapEntry(
        datasheet_id="ds-iron-sentinel-global",
        mfm_display_name=SHARED_NAME,
        wahapedia_datasheet_id="IL01",
        confirmed_at="2026-08-18",
        confirmed_by="test-curator",
        # faction_id omitted entirely.
    )
    content = _authored(unit_map=(global_entry,))

    for n in (1, 2, 3):
        outcome = _run(n, content, IdRegistry())
        assert outcome.matches[0].datasheet_id == "ds-iron-sentinel-global"


def test_a_scoped_entry_is_invisible_to_every_other_scope() -> None:
    """The other half of scoping: an entry naming chapter 3 must not resolve for chapter 4.

    With no unit-map entry at all for chapter 4, and no other narrowing signal, its own call
    falls through to stage 2 and — six candidates, nothing left to prefer with — blocks exactly
    as `test_009_setup_fixtures.py`'s sibling-collision fixture already pins for this shape.
    """
    content = _authored(unit_map=(ENTRIES[2],))  # only chapter 3's own entry
    outcome = _run(4, content, IdRegistry())

    assert outcome.matches == []
    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]


def test_a_scoped_entry_wins_over_a_coexisting_global_entry_for_its_own_scope() -> None:
    """When both a scoped and a global entry exist for one name, the scoped one is more specific
    and must be preferred for the faction it names -- consulted first, per the module's stage-1
    lookup order."""
    scoped = UnitMapEntry(
        datasheet_id="ds-iron-sentinel-1-special",
        mfm_display_name=SHARED_NAME,
        wahapedia_datasheet_id="IL01",
        confirmed_at="2026-08-18",
        confirmed_by="test-curator",
        faction_id="f-chapter-1",
    )
    global_entry = UnitMapEntry(
        datasheet_id="ds-iron-sentinel-global",
        mfm_display_name=SHARED_NAME,
        wahapedia_datasheet_id="IL02",
        confirmed_at="2026-08-18",
        confirmed_by="test-curator",
    )
    content = _authored(unit_map=(scoped, global_entry))

    outcome = _run(1, content, IdRegistry())

    assert outcome.matches[0].datasheet_id == "ds-iron-sentinel-1-special"
