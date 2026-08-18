# AI-Assisted: Claude Code (model: claude-sonnet-5) - Authored the 009 Setup-phase disambiguation
# fixtures (tasks T009, T010): a sibling-faction same-name collision with NO chapter-keyword
# signal and NO distinguishing publication id (so the collision reaches match.py's stage 4 with
# nothing left to narrow on), and a faction-code mismatch (SC-006's deliberately mis-set
# candidate). Built at the same granularity `tests/reconcile/test_chapter_keyword_preference.py`
# already established for this ladder -- inline `FactionMapEntry`/dict constants exercised
# directly through `pipeline.reconcile.match`, not a whole fixture directory + full build, because
# that is the level `resolve_factions`/`match_units` are already unit-tested at.
"""Shared fixture data for T051 (US2, disambiguation) and T050 (US2, loud faction mismatch).

**T009 -- the sibling collision** (`MARCH_LEGION`, `EMBER_HOST`, `ASH_HOST`): two child factions
of one parent share a unit display name (`Bracklight Sentinel`), with neither the Legends flag,
the publication id, nor a chapter-keyword record able to separate the two detail-source rows --
exactly `plan.md` finding 5's measured shape ("the rung resolves exactly one of six" generalised to
zero of two when there is no publication-id split either) and 009 T002's own live measurement (the
export-side collision set, once the ordinary per-chapter roster duplication is excluded, is small
and genuinely nothing-left-to-prefer-with). This module's own sanity check
(`test_009_setup_fixtures.py`) confirms the fixture reproduces TODAY's correctly-blocking shape
(the same "report, never guess" stage-4 refusal `test_chapter_keyword_preference.py`'s own
`test_no_authored_chapter_record_leaves_the_ambiguity_blocking` pins). It intentionally does NOT
assert a resolution: FR-016's replacement rung (faction-scoped `unit-map.json` stage 1, T022-T024,
or whatever research.md Q3/T067 measures) is not implemented in Setup and is Phase 2's and Phase
5's job to land and to test against this same data.

**T010 -- the faction-code mismatch** (`GHOST_ARCHIVE`): a curated faction whose
``detail_source_faction_id`` names a code (``"ZZ"``) that ``DETAIL_ROWS_NO_GHOST_ARCHIVE`` --  a
synthetic `Datasheets.csv`-row set standing in for the accompanying export -- never carries, on the
exact silent-failure shape `plan.md` finding 1 measured live (`curate/assemble.py:1497-1501`'s
membership test: every row of every faction, false). No confirming test is written for it here:
the blocking finding it is meant to prove (`REC-DETAIL-FACTION-EMPTY`) does not exist until Phase 2
(T018/T019) lands, and asserting today's silent (wrong) behaviour would only have to be deleted
the moment the fix arrives. `T050` is where the real assertion belongs.

Named ``detail_source_faction_id`` throughout rather than the schema's still-unlanded
``detail_source_faction_code`` (T021, Phase 2): the mismatch this fixture demonstrates is fully
reproducible on the field that exists today, and is the SAME mismatch shape FR-015 names for
either field name. Phase 2/5 authors adding a ``detail_source_faction_code``-specific case should
extend this module rather than replace it.
"""

from __future__ import annotations

from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import FactionMapEntry
from pipeline.reconcile.identity import IdRegistry
from pipeline.reconcile.match import match_units, resolve_factions

# -- T009: sibling-faction collision, no chapter keyword, no distinguishing publication id -------

MARCH_LEGION = FactionMapEntry(
    mfm_slug="march-legion",
    faction_id="f-march-legion",
    detail_source_faction_id="ML",
)
EMBER_HOST = FactionMapEntry(
    mfm_slug="ember-host",
    faction_id="f-ember-host",
    parent_faction_id="f-march-legion",
    detail_source_faction_id="ML",
)
ASH_HOST = FactionMapEntry(
    mfm_slug="ash-host",
    faction_id="f-ash-host",
    parent_faction_id="f-march-legion",
    detail_source_faction_id="ML",
)

#: Two detail rows, one shared name, same faction code, neither Legends, no publication id set on
#: either sibling's `FactionMapEntry` (so the publication-id rung -- already measured insufficient
#: for the real Space Marine collision, `plan.md` finding 5 -- is inert here too) and no
#: `keyword_classes` record accompanies this fixture at all (so the chapter-keyword rung is
#: unreached, on the same terms `test_chapter_keyword_preference.py`'s own no-record case is).
SIBLING_COLLISION_CANDIDATES = {"ML04": "Bracklight Sentinel", "ML09": "Bracklight Sentinel"}
SIBLING_COLLISION_LEGENDS: dict[str, bool] = {"ML04": False, "ML09": False}
SIBLING_COLLISION_SOURCE_IDS: dict[str, str] = {}
SIBLING_COLLISION_KEYWORDS: dict[str, frozenset[str]] = {
    "ML04": frozenset({"MARCH LEGION"}),
    "ML09": frozenset({"MARCH LEGION"}),
}


def sibling_authored(**overrides: object) -> AuthoredContent:
    base: dict[str, object] = {
        "faction_map": (MARCH_LEGION, EMBER_HOST, ASH_HOST),
        "keyword_classes": (),
    }
    base.update(overrides)
    return AuthoredContent(**base)  # type: ignore[arg-type]


def _scope_for(slug: str, content: AuthoredContent):  # type: ignore[no-untyped-def]
    outcome = resolve_factions([slug], content)
    assert outcome.scopes, f"{slug} did not resolve to a scope"
    return outcome.scopes[0]


def run_sibling_match(slug: str, content: AuthoredContent | None = None, **overrides: object):  # type: ignore[no-untyped-def]
    """Run stages 1-4 for one of the three sibling factions against the collision candidates.

    Ready for T051 to call with a resolving rung wired in (a `unit-map.json` entry once T024's
    `faction_id` field lands, or whatever research.md Q3 measures); today, with nothing overridden,
    it reproduces the currently-blocking shape.
    """
    resolved_content = content or sibling_authored()
    registry = overrides.pop("registry", None) or IdRegistry()
    kwargs: dict[str, object] = {
        "display_names": ["BRACKLIGHT SENTINEL"],
        "detail_names": SIBLING_COLLISION_CANDIDATES,
        "detail_is_legends": SIBLING_COLLISION_LEGENDS,
        "detail_source_ids": SIBLING_COLLISION_SOURCE_IDS,
        "detail_faction_keywords": SIBLING_COLLISION_KEYWORDS,
        "authored": resolved_content,
        "registry": registry,
    }
    kwargs.update(overrides)
    return match_units(_scope_for(slug, resolved_content), **kwargs)  # type: ignore[arg-type]


# -- T010: faction-code mismatch (SC-006's deliberately mis-set candidate) -----------------------

#: A curated faction naming a detail-source code the accompanying export never publishes -- the
#: exact silent-failure shape `plan.md` finding 1 measured live in `curate/assemble.py:1497-1501`.
GHOST_ARCHIVE = FactionMapEntry(
    mfm_slug="ghost-archive",
    faction_id="f-ghost-archive",
    detail_source_faction_id="ZZ",
)

#: A synthetic `Datasheets.csv` row set standing in for the accompanying export: every row uses a
#: DIFFERENT code (`"GA"`), so `GHOST_ARCHIVE`'s mapped code (`"ZZ"`) matches zero of them --
#: `scope.detail_faction_ids` (from `resolve_factions`) filtered against these rows' `faction_id`
#: values is the empty set T019 is meant to catch. Field-dict shape only (not a full
#: `WahapediaRow`/`CsvReadResult`): the code that will actually consume these
#: (`curate/assemble.py`'s `in_scope` construction) reads `row.fields.get("faction_id")`, so a
#: bare mapping is sufficient for whatever shape T050 wires this into.
DETAIL_ROWS_NO_GHOST_ARCHIVE: tuple[dict[str, str], ...] = (
    {"id": "GA01", "name": "Watch Warden", "faction_id": "GA"},
    {"id": "GA02", "name": "Watch Sentinel", "faction_id": "GA"},
)


def ghost_archive_authored(**overrides: object) -> AuthoredContent:
    base: dict[str, object] = {"faction_map": (GHOST_ARCHIVE,)}
    base.update(overrides)
    return AuthoredContent(**base)  # type: ignore[arg-type]
