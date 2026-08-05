# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote US2's independent test (004 task
# T036), confirmed failing before pipeline/reconcile/chapters.py and the chapterKeywords emitter
# existed: a chapter keyword resolves to exactly the datasheets carrying it, the chapter
# vocabulary is directly enumerable with each entry's parent, and a chapter the points source
# already models as a faction of its own still appears, flagged (004 FR-018).
"""US2's independent test, stated against the **bundle** rather than an internal structure.

The capability US2 exists to unlock is navigational: a consumer that has never been told a
chapter name can enumerate the chapter vocabulary and resolve each entry to its exact unit set.
So the assertions below go through `emit_bundle` and join `chapterKeywords.keyword` against
`datasheetKeywords.keyword` — a plain join, no composite lookup, which is precisely what keying
`chapterKeywords` by `keyword` alone buys (FR-019 guarantees one parent per chapter keyword).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pipeline.build.bundle_emit import emit_bundle
from pipeline.reconcile.chapters import (
    apply_keyword_classes,
    classify_keywords,
    observed_keywords,
)
from tests.enrichment.conftest import (
    CHAPTER_FACTIONS,
    KEYWORD_CLASS_RECORDS,
    curated_keywords,
)
from tests.factories import datasheet, meta, snapshot

KeywordRows = Mapping[str, list[tuple[str, bool, str | None]]]

#: Every datasheet the keyword fixture describes. GF01 carries one chapter, GF02 the other,
#: GF03 both, GF04/GF06 neither, GF05 the unclassified faction keyword.
FIXTURE_DATASHEETS = ("GF01", "GF02", "GF03", "GF04", "GF05", "GF06")


def _bundle(keyword_rows: KeywordRows) -> dict[str, Any]:
    sheets = [
        datasheet(f"ds-{detail_id.lower()}", faction_id="f-glimmerfen-covenant").model_copy(
            update={"keywords": curated_keywords(keyword_rows, detail_id)}
        )
        for detail_id in FIXTURE_DATASHEETS
    ]
    classification = classify_keywords(
        observed=observed_keywords(sheets),
        factions=CHAPTER_FACTIONS,
        authored=KEYWORD_CLASS_RECORDS,
    )
    snap = snapshot(
        factions=list(CHAPTER_FACTIONS),
        datasheets=apply_keyword_classes(sheets, classification.classes),
        chapter_keywords=list(classification.chapter_keywords),
        detachments=[],
        enhancements=[],
    )
    return emit_bundle(snap, meta())


def _datasheets_carrying(bundle: Mapping[str, Any], keyword: str) -> list[str]:
    """The join a consumer performs: chapter keyword -> its exact unit set."""
    return sorted(
        row["datasheetId"] for row in bundle["datasheetKeywords"] if row["keyword"] == keyword
    )


def test_a_chapter_keyword_resolves_to_exactly_the_datasheets_carrying_it(
    keyword_rows: KeywordRows,
) -> None:
    bundle = _bundle(keyword_rows)

    assert _datasheets_carrying(bundle, "THORNLIGHT CHORUS") == ["ds-gf01", "ds-gf03"]
    assert _datasheets_carrying(bundle, "BRACKLIGHT HOST") == ["ds-gf02", "ds-gf03"]


def test_the_chapter_vocabulary_is_directly_enumerable_with_its_parent(
    keyword_rows: KeywordRows,
) -> None:
    """No scan of every datasheet, and no chapter name known in advance."""
    bundle = _bundle(keyword_rows)

    assert [(row["keyword"], row["parentFactionId"]) for row in bundle["chapterKeywords"]] == [
        ("BRACKLIGHT HOST", "f-glimmerfen-covenant"),
        ("THORNLIGHT CHORUS", "f-glimmerfen-covenant"),
    ]


def test_chapter_keywords_is_sorted_by_keyword(keyword_rows: KeywordRows) -> None:
    bundle = _bundle(keyword_rows)
    keywords = [row["keyword"] for row in bundle["chapterKeywords"]]
    assert keywords == sorted(keywords)


def test_a_chapter_modelled_as_a_faction_still_appears_flagged(keyword_rows: KeywordRows) -> None:
    """FR-018's uniform enumeration: one mechanism for every chapter grouping."""
    bundle = _bundle(keyword_rows)
    by_keyword = {row["keyword"]: row for row in bundle["chapterKeywords"]}

    bracklight = by_keyword["BRACKLIGHT HOST"]
    assert bracklight["isModelledAsFaction"] is True
    assert bracklight["chapterFactionId"] == "f-bracklight-host"
    # It is a faction *as well*, and both statements resolve.
    assert any(row["id"] == "f-bracklight-host" for row in bundle["factions"])

    thornlight = by_keyword["THORNLIGHT CHORUS"]
    assert thornlight["isModelledAsFaction"] is False
    # A flag without an id tells a consumer nothing it can act on, so the id is simply absent.
    assert "chapterFactionId" not in thornlight


def test_the_keyword_class_column_is_emitted_and_omitted_when_unclassified(
    keyword_rows: KeywordRows,
) -> None:
    bundle = _bundle(keyword_rows)
    rows = {(row["datasheetId"], row["keyword"]): row for row in bundle["datasheetKeywords"]}

    assert rows[("ds-gf01", "GLIMMERFEN COVENANT")]["keywordClass"] == "faction"
    assert rows[("ds-gf01", "THORNLIGHT CHORUS")]["keywordClass"] == "chapter"
    assert rows[("ds-gf01", "INFANTRY")]["keywordClass"] == "unit"
    assert "keywordClass" not in rows[("ds-gf05", "MIREFEN ENCLAVE")]


def test_a_datasheet_carrying_neither_chapter_appears_under_neither(
    keyword_rows: KeywordRows,
) -> None:
    bundle = _bundle(keyword_rows)
    for chapter in ("THORNLIGHT CHORUS", "BRACKLIGHT HOST"):
        assert "ds-gf04" not in _datasheets_carrying(bundle, chapter)
        assert "ds-gf06" not in _datasheets_carrying(bundle, chapter)
