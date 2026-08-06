# AI-Assisted: Claude Code (model: claude-sonnet-5) - New tests for the publication-id
# disambiguation step added to D5 stage 2 (pipeline/reconcile/match.py): the real Black Templars
# case, where a chapter's own supplement republishes a core-codex datasheet under a colliding
# name and neither copy is Legends, so the existing Legends-flag narrowing cannot separate them.
# AI-Assisted: Claude Code (model: claude-opus-5) - Passed detail_faction_keywords={} at every
# call site here when the chapter-keyword narrowing step made that parameter required; an empty
# view keeps these cases about the publication id alone, which is what they are for.
"""The publication-id narrowing step, ahead of ``REC-AMBIGUOUS-MATCH`` (D5 stage 2, extended).

Mirrors ``tests/reconcile/test_match_ladder.py``'s fixture-construction style with fictional
faction and unit names (this project's absolute fixture-synthetic policy — no publisher IP in
any file, fixture or otherwise). The structural shape under test is the real one: two
chapter-scoped detail-source candidates share a normalised name, neither is Legends, and only a
``detail_source_publication_id`` on the mapping can tell them apart — and even then, only when
it narrows the candidates to exactly one. The single most important case is the last one: a
``detail_source_publication_id`` that matches *no* candidate must still block as ambiguous, never
silently resolve to the wrong one.
"""

from __future__ import annotations

from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import FactionMapEntry
from pipeline.models.findings import Severity
from pipeline.reconcile.identity import IdRegistry
from pipeline.reconcile.match import match_units, resolve_factions

# A chapter sub-faction whose detail-source faction id collides with its parent's, the way all
# five Space Marine chapters collide on "SM" — and which carries its own publication id, the way
# Black Templars carries its supplement's real source_id (curation/faction-map.json).
CHAPTER = FactionMapEntry(
    mfm_slug="ember-chapter",
    faction_id="f-ember-chapter",
    parent_faction_id="f-ember-legion",
    detail_source_faction_id="EL",
    detail_source_publication_id="000000162",
)
# The same shape, but with no publication id authored — standing in for the other four SM
# chapters, which are not affected by this specific ambiguity and must see unchanged behaviour.
CHAPTER_UNSET = FactionMapEntry(
    mfm_slug="ash-chapter",
    faction_id="f-ash-chapter",
    parent_faction_id="f-ember-legion",
    detail_source_faction_id="EL",
)
PARENT = FactionMapEntry(
    mfm_slug="ember-legion", faction_id="f-ember-legion", detail_source_faction_id="EL"
)


def authored(**overrides: object) -> AuthoredContent:
    base: dict[str, object] = {"faction_map": (CHAPTER, CHAPTER_UNSET, PARENT)}
    base.update(overrides)
    return AuthoredContent(**base)  # type: ignore[arg-type]


def scope_for(slug: str, content: AuthoredContent):
    outcome = resolve_factions([slug], content)
    assert outcome.scopes, f"{slug} did not resolve to a scope"
    return outcome.scopes[0]


def test_publication_id_narrows_an_otherwise_ambiguous_pair_to_the_chapters_own_datasheet() -> None:
    content = authored()
    outcome = match_units(
        scope_for("ember-chapter", content),
        display_names=["EMBER CHAPLAIN"],
        # Same normalised name, both filed under the parent's "EL" detail-source faction id
        # (the collision), neither Legends (Legends narrowing cannot help), and only one of the
        # two was published by the chapter's own supplement.
        detail_names={"EL04": "Ember Chaplain", "EL09": "Ember Chaplain"},
        detail_is_legends={},
        detail_source_ids={"EL04": "000000139", "EL09": "000000162"},
        detail_faction_keywords={},
        authored=content,
        registry=IdRegistry(),
    )

    assert not outcome.findings, "the publication id resolved the ambiguity; nothing to report"
    assert [m.stage for m in outcome.matches] == ["exact"], (
        "still stage 2 — the publication id is an extra disambiguating signal within it, the "
        "same way the Legends-flag narrowing a few lines above gets no stage of its own"
    )
    assert outcome.matches[0].wahapedia_datasheet_id == "EL09", (
        "the chapter's own supplement copy is preferred over the core-codex twin"
    )


def test_unset_publication_id_leaves_the_existing_ambiguous_match_behaviour_unchanged() -> None:
    content = authored()
    outcome = match_units(
        scope_for("ash-chapter", content),  # no detail_source_publication_id authored
        display_names=["EMBER CHAPLAIN"],
        detail_names={"EL04": "Ember Chaplain", "EL09": "Ember Chaplain"},
        detail_is_legends={},
        detail_source_ids={"EL04": "000000139", "EL09": "000000162"},
        detail_faction_keywords={},
        authored=content,
        registry=IdRegistry(),
    )

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert outcome.findings[0].severity is Severity.BLOCKING
    assert not outcome.matches, "with no authored publication id, nothing has changed"


def test_a_publication_id_matching_no_candidate_still_blocks_rather_than_mis_resolving() -> None:
    content = authored()
    outcome = match_units(
        scope_for("ember-chapter", content),
        display_names=["EMBER CHAPLAIN"],
        detail_names={"EL04": "Ember Chaplain", "EL09": "Ember Chaplain"},
        detail_is_legends={},
        # Neither candidate carries the chapter's authored publication id (000000162) — a stale
        # or typo'd value. This must still raise REC-AMBIGUOUS-MATCH, never guess.
        detail_source_ids={"EL04": "000000139", "EL09": "000000140"},
        detail_faction_keywords={},
        authored=content,
        registry=IdRegistry(),
    )

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert outcome.findings[0].severity is Severity.BLOCKING
    assert not outcome.matches, (
        "an authored publication id that matches nothing is not a resolution — it is still an "
        "ambiguous match, and must still block"
    )


def test_a_publication_id_matching_every_candidate_still_blocks() -> None:
    content = authored()
    outcome = match_units(
        scope_for("ember-chapter", content),
        display_names=["EMBER CHAPLAIN"],
        detail_names={"EL04": "Ember Chaplain", "EL09": "Ember Chaplain"},
        detail_is_legends={},
        # Both candidates carry the chapter's publication id — narrowing leaves 2, not 1, so it
        # is still ambiguous.
        detail_source_ids={"EL04": "000000162", "EL09": "000000162"},
        detail_faction_keywords={},
        authored=content,
        registry=IdRegistry(),
    )

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert not outcome.matches
