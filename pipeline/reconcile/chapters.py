# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented keyword classification and the
# enumerable chapter vocabulary (004 task T038): data-model.md §1.6's three default rules, the
# curator's exceptions from curation/keyword-classes.json, CuratedChapterKeyword construction
# with FR-018's uniform-enumeration flag, and FR-019's blocking parent-agreement check.
"""Classify every keyword, and enumerate the chapter (sub-faction) vocabulary.

The detail source separates faction keywords from non-faction ones, but it does **not** separate
a parent faction's keyword from a chapter's — and 661 of 1 716 datasheets in the measured
baseline carry two faction keywords, which is the normal shape of a chapter unit rather than a
defect (FR-017, research D7). So the class is derived where it can be derived and authored where
it cannot:

===========================================  =========================
Source signal                                 Default
===========================================  =========================
``is_faction_keyword = false``                ``unit``
``true``, resolves to a parentless faction    ``faction``
``true``, otherwise                           **unclassified**
===========================================  =========================

Unclassified means unclassified. The keyword ships **exactly as it does today** — ``keyword_class``
omitted, its row byte-identical — publication is not blocked, and ``KWD-UNCLASSIFIED`` (advisory)
names it in the report (FR-020). A guessed class is worse than none, because a consumer cannot
tell a guess from a curated fact.

The curator writes only the exceptions, in ``curation/keyword-classes.json``. Of 1 423 distinct
keywords in the baseline only 46 are faction keywords, so the authoring surface is at most 46
records — the cheapest of this feature's content gaps by a wide margin.

**Why the parent-agreement check is blocking.** Two structures describe one hierarchy here: these
chapter records, and `002`'s existing parent/child faction tree. Two structures describing one
hierarchy drift apart unless one is made to answer to the other, so ``chapter_faction_id`` is
asserted against that faction's own ``parent_faction_id`` and a contradiction stops the run
(``KWD-CHAPTER-PARENT-CONFLICT``, FR-019). Advisory would not do: a silent contradiction files one
chapter's units under two different parents, and the resulting double count is invisible in the
data itself.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from pipeline.models.authored import KeywordClassEntry
from pipeline.models.curated import (
    CuratedChapterKeyword,
    CuratedDatasheet,
    CuratedFaction,
    CuratedKeyword,
    KeywordClass,
)
from pipeline.models.findings import Finding
from pipeline.reconcile.identity import slugify
from pipeline.report.catalogue import build_finding


@dataclass(frozen=True, slots=True)
class KeywordClassification:
    """What one run decided about every keyword the snapshot uses."""

    classes: Mapping[str, KeywordClass]
    """``keyword -> class``, carrying **only** the classified ones — an unclassified keyword is
    absent rather than mapped to a sentinel, so :func:`apply_keyword_classes` cannot accidentally
    stamp a default onto a row FR-020 requires be left alone."""

    chapter_keywords: tuple[CuratedChapterKeyword, ...]
    """The enumerable chapter vocabulary, sorted by ``keyword`` (§1.5)."""

    findings: tuple[Finding, ...]
    unclassified: tuple[str, ...]

    observed_count: int = 0
    """Distinct keywords in use — the denominator of the ``keyword_classification`` figure."""

    @property
    def classified_count(self) -> int:
        """Distinct keywords carrying a class — the numerator (SC-005, data-model.md §5)."""
        return len(self.classes)


def observed_keywords(datasheets: Sequence[CuratedDatasheet]) -> dict[str, bool]:
    """``keyword -> is_faction_keyword``, over every keyword at least one datasheet carries.

    A keyword bound on two datasheets is one keyword: the class is a property of the keyword, not
    of the binding, which is what lets ``chapterKeywords`` be keyed by ``keyword`` alone. Where
    two bindings disagree about ``is_faction_keyword`` — which the source should never do — the
    *faction* reading wins, because that is the reading that can still be classified rather than
    silently collapsing a chapter into ``unit``.
    """
    observed: dict[str, bool] = {}
    for datasheet in datasheets:
        for keyword in datasheet.keywords:
            observed[keyword.keyword] = observed.get(keyword.keyword, False) or (
                keyword.is_faction_keyword
            )
    return observed


def _parentless_faction_slugs(factions: Sequence[CuratedFaction]) -> frozenset[str]:
    """The slugs a faction keyword may resolve to under the ``faction`` default rule.

    Both the curated ``code`` and the slugified display name are accepted: the two are the same
    token for every faction this pipeline mints, and accepting both means a faction whose name
    and code were mapped apart in ``curation/faction-map.json`` still resolves.
    """
    slugs: set[str] = set()
    for faction in factions:
        if faction.parent_faction_id is not None:
            continue
        slugs.add(faction.code)
        slugs.add(slugify(faction.name))
    return frozenset(slugs)


def _chapter_keyword(
    record: KeywordClassEntry, factions_by_id: Mapping[str, CuratedFaction]
) -> tuple[CuratedChapterKeyword | None, Finding | None]:
    """One curator record as a curated row, plus the parent-agreement verdict (FR-019)."""
    if record.parent_faction_id is None:
        # The schema requires it for `keyword_class: chapter`, so reaching this means the file
        # bypassed validation. Refuse to invent a parent rather than emit a row keyed to nothing.
        return None, None

    finding: Finding | None = None
    if record.chapter_faction_id is not None:
        chapter_faction = factions_by_id.get(record.chapter_faction_id)
        # A `chapter_faction_id` naming no faction at all is the blocking AUT-DANGLING-REF that
        # V9 already raises from `authored_entity_refs`; raising a second code here would report
        # one defect twice.
        if (
            chapter_faction is not None
            and chapter_faction.parent_faction_id != record.parent_faction_id
        ):
            finding = build_finding(
                "KWD-CHAPTER-PARENT-CONFLICT",
                entity_refs=[f"keyword:{record.keyword}"],
                detail={
                    "keyword": record.keyword,
                    "chapter_faction_id": record.chapter_faction_id,
                    "record_parent_faction_id": record.parent_faction_id,
                    "faction_parent_faction_id": chapter_faction.parent_faction_id or "",
                },
            )

    return (
        CuratedChapterKeyword(
            keyword=record.keyword,
            parent_faction_id=record.parent_faction_id,
            chapter_faction_id=record.chapter_faction_id,
            is_modelled_as_faction=record.chapter_faction_id is not None,
        ),
        finding,
    )


def classify_keywords(
    *,
    observed: Mapping[str, bool],
    factions: Sequence[CuratedFaction],
    authored: Sequence[KeywordClassEntry],
) -> KeywordClassification:
    """Classify every observed keyword and build the chapter vocabulary.

    Args:
        observed: ``keyword -> is_faction_keyword`` from :func:`observed_keywords`.
        factions: the curated faction tree — the authority the chapter records answer to.
        authored: ``curation/keyword-classes.json``, the curator's exceptions.
    """
    by_keyword = {record.keyword: record for record in authored}
    factions_by_id = {faction.faction_id: faction for faction in factions}
    parentless = _parentless_faction_slugs(factions)

    classes: dict[str, KeywordClass] = {}
    unclassified: list[str] = []
    findings: list[Finding] = []

    for keyword in sorted(observed):
        record = by_keyword.get(keyword)
        if record is not None:
            # The curator's record wins over the default, in both directions: it is how a
            # chapter that *does* resolve to a faction is told apart from a parent, and how a
            # keyword the source mislabels is corrected.
            classes[keyword] = KeywordClass(record.keyword_class)
            continue
        if not observed[keyword]:
            classes[keyword] = KeywordClass.UNIT
            continue
        if slugify(keyword) in parentless:
            classes[keyword] = KeywordClass.FACTION
            continue

        unclassified.append(keyword)
        findings.append(
            build_finding(
                "KWD-UNCLASSIFIED",
                entity_refs=[f"keyword:{keyword}"],
                detail={"keyword": keyword},
            )
        )

    chapters: list[CuratedChapterKeyword] = []
    for record in sorted(authored, key=lambda r: r.keyword):
        if record.keyword_class != KeywordClass.CHAPTER.value:
            continue
        row, conflict = _chapter_keyword(record, factions_by_id)
        if row is not None:
            chapters.append(row)
        if conflict is not None:
            findings.append(conflict)

    return KeywordClassification(
        classes=classes,
        chapter_keywords=tuple(chapters),
        findings=tuple(findings),
        unclassified=tuple(unclassified),
        observed_count=len(observed),
    )


def apply_keyword_classes(
    datasheets: Sequence[CuratedDatasheet], classes: Mapping[str, KeywordClass]
) -> list[CuratedDatasheet]:
    """Stamp ``keyword_class`` onto every classified binding, and nothing onto the rest.

    A datasheet whose keywords are all unclassified is returned **unchanged by value**: every
    field of every row, including ``keyword_class``'s absence, is what it was — which is FR-020's
    guarantee stated as an operation rather than as an intention.
    """
    updated: list[CuratedDatasheet] = []
    for datasheet in datasheets:
        keywords = [
            CuratedKeyword(
                keyword=keyword.keyword,
                is_faction_keyword=keyword.is_faction_keyword,
                model_scope=keyword.model_scope,
                keyword_class=classes.get(keyword.keyword),
            )
            for keyword in datasheet.keywords
        ]
        updated.append(datasheet.model_copy(update={"keywords": keywords}))
    return updated
