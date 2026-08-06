# AI-Assisted: Claude Code (model: claude-opus-5) - New tests for the chapter-keyword narrowing
# step added to D5 stage 2 (pipeline/reconcile/match.py), the rung docs/follow-ups.md item 4
# sketched: under html mode the detail source publishes a chapter's copy of a shared datasheet on
# the parent's own page, under the same name and the same publication, so neither the Legends flag
# nor detail_source_publication_id can separate the pair -- but the chapter's card carries the
# chapter's faction keyword and the parent's does not.
"""Chapter-keyword narrowing, ahead of ``REC-AMBIGUOUS-MATCH`` (D5 stage 2, extended).

Same fixture-construction style as ``tests/reconcile/test_publication_preference.py``, with
invented faction, chapter and unit names — this project's fixtures are synthetic without
exception. The structural shape under test is the real one: two detail-source candidates share a
normalised name and a publication, neither is Legends, and the *only* thing that tells them apart
is that one of them carries a chapter's faction keyword.

The rung is driven by ``curation/keyword-classes.json``, which is curator-authored and already
asserted against the faction tree (FR-019). That matters more than the convenience: the signal is
**declared**, so this is still stage 2 refusing to guess rather than a fuzzy match wearing a
different hat. Every case below where the declaration does not resolve the pair to exactly one
candidate must still block.
"""

from __future__ import annotations

from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import FactionMapEntry, KeywordClassEntry
from pipeline.models.findings import Severity
from pipeline.reconcile.identity import IdRegistry
from pipeline.reconcile.match import match_units, resolve_factions

# Two chapters of one parent, both modelled by the points source as their own faction — the shape
# all five Space Marine chapters have in curation/faction-map.json.
EMBER = FactionMapEntry(
    mfm_slug="ember-chapter",
    faction_id="f-ember-chapter",
    parent_faction_id="f-ember-legion",
    detail_source_faction_id="EL",
)
ASH = FactionMapEntry(
    mfm_slug="ash-chapter",
    faction_id="f-ash-chapter",
    parent_faction_id="f-ember-legion",
    detail_source_faction_id="EL",
)
PARENT = FactionMapEntry(
    mfm_slug="ember-legion", faction_id="f-ember-legion", detail_source_faction_id="EL"
)

# The curator's declaration that these two keywords name chapters, and which curated faction each
# chapter is. `parent_faction_id` agrees with the faction map's, which is what FR-019 checks.
EMBER_KEYWORD = KeywordClassEntry(
    keyword="EMBER CHAPTER",
    keyword_class="chapter",
    parent_faction_id="f-ember-legion",
    chapter_faction_id="f-ember-chapter",
)
ASH_KEYWORD = KeywordClassEntry(
    keyword="ASH CHAPTER",
    keyword_class="chapter",
    parent_faction_id="f-ember-legion",
    chapter_faction_id="f-ash-chapter",
)

# The collision: one shared datasheet published twice on the parent's page, once plain and once
# carrying the Ember Chapter's own keyword. Same name, same publication, neither Legends.
CANDIDATES = {"EL04": "Ember Halberdiers", "EL09": "Ember Halberdiers"}
KEYWORDS = {
    "EL04": frozenset({"EMBER LEGION"}),
    "EL09": frozenset({"EMBER LEGION", "EMBER CHAPTER"}),
}


def authored(**overrides: object) -> AuthoredContent:
    base: dict[str, object] = {
        "faction_map": (EMBER, ASH, PARENT),
        "keyword_classes": (EMBER_KEYWORD, ASH_KEYWORD),
    }
    base.update(overrides)
    return AuthoredContent(**base)  # type: ignore[arg-type]


def scope_for(slug: str, content: AuthoredContent):  # type: ignore[no-untyped-def]
    outcome = resolve_factions([slug], content)
    assert outcome.scopes, f"{slug} did not resolve to a scope"
    return outcome.scopes[0]


def run(slug: str, content: AuthoredContent, **overrides: object):  # type: ignore[no-untyped-def]
    kwargs: dict[str, object] = {
        "display_names": ["EMBER HALBERDIERS"],
        "detail_names": CANDIDATES,
        "detail_is_legends": {},
        "detail_source_ids": {"EL04": "000000139", "EL09": "000000139"},
        "detail_faction_keywords": KEYWORDS,
        "authored": content,
        "registry": IdRegistry(),
    }
    kwargs.update(overrides)
    return match_units(scope_for(slug, content), **kwargs)  # type: ignore[arg-type]


def test_a_chapter_takes_the_candidate_carrying_its_own_keyword() -> None:
    outcome = run("ember-chapter", authored())

    assert not outcome.findings, "the chapter keyword resolved the ambiguity; nothing to report"
    assert [m.stage for m in outcome.matches] == ["exact"], (
        "still stage 2 — the chapter keyword is one more disambiguating signal within it, exactly "
        "as the Legends flag and the publication id are"
    )
    assert outcome.matches[0].wahapedia_datasheet_id == "EL09"


def test_the_parent_takes_the_candidate_carrying_no_chapters_keyword() -> None:
    outcome = run("ember-legion", authored())

    assert not outcome.findings
    assert outcome.matches[0].wahapedia_datasheet_id == "EL04", (
        "a datasheet carrying a chapter's keyword can only be fielded by that chapter, so the "
        "parent is entitled to the copy that carries none"
    )


def test_a_sibling_chapter_also_takes_the_candidate_carrying_no_chapters_keyword() -> None:
    outcome = run("ash-chapter", authored())

    assert not outcome.findings
    assert outcome.matches[0].wahapedia_datasheet_id == "EL04", (
        "the Ember Chapter's copy is not the Ash Chapter's to field either — a sibling is in the "
        "same position as the parent, not in the chapter's"
    )


def test_no_authored_chapter_record_leaves_the_ambiguity_blocking() -> None:
    outcome = run("ember-chapter", authored(keyword_classes=()))

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert outcome.findings[0].severity is Severity.BLOCKING
    assert not outcome.matches, (
        "the rung is driven by a curator's declaration and by nothing else; with no declaration "
        "the pipeline has not been told anything and must not infer it from the keyword's spelling"
    )


def test_a_chapter_keyword_on_every_candidate_still_blocks() -> None:
    outcome = run(
        "ember-chapter",
        authored(),
        detail_faction_keywords={
            "EL04": frozenset({"EMBER LEGION", "EMBER CHAPTER"}),
            "EL09": frozenset({"EMBER LEGION", "EMBER CHAPTER"}),
        },
    )

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert not outcome.matches, "narrowing that leaves two is not a resolution"


def test_a_chapter_keyword_on_no_candidate_still_blocks_for_the_chapter() -> None:
    outcome = run(
        "ember-chapter",
        authored(),
        detail_faction_keywords={
            "EL04": frozenset({"EMBER LEGION"}),
            "EL09": frozenset({"EMBER LEGION"}),
        },
    )

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert not outcome.matches, (
        "with neither copy claimed by a chapter, nothing distinguishes them and the chapter has "
        "no more right to one than to the other"
    )


def test_two_foreign_chapters_leave_the_parent_with_nothing_to_prefer() -> None:
    outcome = run(
        "ember-legion",
        authored(),
        detail_faction_keywords={
            "EL04": frozenset({"EMBER LEGION", "ASH CHAPTER"}),
            "EL09": frozenset({"EMBER LEGION", "EMBER CHAPTER"}),
        },
    )

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert not outcome.matches, (
        "both copies belong to a chapter, so discarding the ones the parent cannot field leaves "
        "it none — which is still not a match"
    )


def test_a_chapter_keyword_from_another_faction_tree_is_never_consulted() -> None:
    # A chapter of a completely unrelated parent. Its keyword must not narrow anything here, or a
    # curator's authoring in one faction would quietly change matching in another.
    outsider = KeywordClassEntry(
        keyword="EMBER CHAPTER",
        keyword_class="chapter",
        parent_faction_id="f-distant-host",
        chapter_faction_id="f-distant-chapter",
    )
    outcome = run("ember-legion", authored(keyword_classes=(outsider,)))

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert not outcome.matches


def test_a_chapter_the_points_source_does_not_model_as_a_faction_narrows_nothing() -> None:
    # `chapter_faction_id` absent means the points source prices this chapter's units on the
    # parent's own page, so the parent IS entitled to them and must not discard them.
    unmodelled = KeywordClassEntry(
        keyword="EMBER CHAPTER", keyword_class="chapter", parent_faction_id="f-ember-legion"
    )
    outcome = run("ember-legion", authored(keyword_classes=(unmodelled,)))

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert not outcome.matches


def test_the_rung_is_only_reached_once_a_name_is_genuinely_ambiguous() -> None:
    # One candidate, carrying a foreign chapter's keyword. Narrowing never runs, so the match is
    # what it always was: the rung must not be able to *remove* a faction's only candidate.
    outcome = run(
        "ember-legion",
        authored(),
        detail_names={"EL09": "Ember Halberdiers"},
        detail_faction_keywords={"EL09": frozenset({"EMBER LEGION", "EMBER CHAPTER"})},
    )

    assert not outcome.findings
    assert outcome.matches[0].wahapedia_datasheet_id == "EL09"
