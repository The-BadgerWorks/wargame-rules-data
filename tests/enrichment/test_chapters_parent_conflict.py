# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the parent-agreement test (004 task
# T037), confirmed failing before pipeline/reconcile/chapters.py existed: a curator record whose
# chapter_faction_id names a faction with a different parent is the blocking
# KWD-CHAPTER-PARENT-CONFLICT (004 FR-019, data-model.md §1.6).
"""One side declares, the other is asserted against it.

Two structures describe the same hierarchy here — `curation/keyword-classes.json`'s chapter
records and `002`'s existing parent/child faction tree — and two structures describing one
hierarchy drift apart unless one of them is made to answer to the other. `002` closed exactly
this failure mode for the point range (R9); this is the same fix in the same shape, and the
reason it has to be **blocking** rather than advisory is that a silent contradiction here
double-counts a chapter's units under two different parents.
"""

from __future__ import annotations

from collections.abc import Mapping

from pipeline.models.authored import KeywordClassEntry
from pipeline.models.findings import Severity
from pipeline.reconcile.chapters import classify_keywords, observed_keywords
from pipeline.report.catalogue import CATALOGUE
from tests.enrichment.conftest import (
    CHAPTER_FACTIONS,
    KEYWORD_CLASS_RECORDS,
    curated_keywords,
)
from tests.factories import datasheet, faction

KeywordRows = Mapping[str, list[tuple[str, bool, str | None]]]

#: The same `BRACKLIGHT HOST` record, but claiming a parent the faction tree disagrees with.
CONFLICTING = KeywordClassEntry(
    keyword="BRACKLIGHT HOST",
    keyword_class="chapter",
    parent_faction_id="f-sedgeward-conclave",
    chapter_faction_id="f-bracklight-host",
)


def _classify(keyword_rows: KeywordRows, *, authored, factions=CHAPTER_FACTIONS):  # type: ignore[no-untyped-def]
    sheets = [
        datasheet("ds-gf02").model_copy(update={"keywords": curated_keywords(keyword_rows, "GF02")})
    ]
    return classify_keywords(
        observed=observed_keywords(sheets), factions=factions, authored=authored
    )


def test_a_disagreeing_parent_is_blocking(keyword_rows: KeywordRows) -> None:
    classification = _classify(keyword_rows, authored=(CONFLICTING,))

    conflicts = [
        f for f in classification.findings if f.finding_code == "KWD-CHAPTER-PARENT-CONFLICT"
    ]
    assert len(conflicts) == 1
    assert conflicts[0].severity is Severity.BLOCKING
    assert conflicts[0].severity is CATALOGUE["KWD-CHAPTER-PARENT-CONFLICT"].severity


def test_the_conflict_names_both_parents_so_a_curator_knows_which_to_change(
    keyword_rows: KeywordRows,
) -> None:
    classification = _classify(keyword_rows, authored=(CONFLICTING,))
    conflict = next(
        f for f in classification.findings if f.finding_code == "KWD-CHAPTER-PARENT-CONFLICT"
    )

    assert conflict.entity_refs == ("keyword:BRACKLIGHT HOST",)
    assert conflict.detail == {
        "keyword": "BRACKLIGHT HOST",
        "chapter_faction_id": "f-bracklight-host",
        "record_parent_faction_id": "f-sedgeward-conclave",
        "faction_parent_faction_id": "f-glimmerfen-covenant",
    }


def test_agreement_raises_nothing(keyword_rows: KeywordRows) -> None:
    classification = _classify(keyword_rows, authored=KEYWORD_CLASS_RECORDS)
    assert classification.findings == ()


def test_a_chapter_faction_with_no_parent_at_all_still_conflicts(
    keyword_rows: KeywordRows,
) -> None:
    """A parentless faction agrees with no record that names a parent — the same contradiction."""
    orphaned = (faction("f-glimmerfen-covenant"), faction("f-bracklight-host"))

    classification = _classify(keyword_rows, authored=KEYWORD_CLASS_RECORDS, factions=orphaned)

    codes = [f.finding_code for f in classification.findings]
    assert "KWD-CHAPTER-PARENT-CONFLICT" in codes


def test_a_record_with_no_chapter_faction_id_is_never_checked(keyword_rows: KeywordRows) -> None:
    """Nothing to assert against: `THORNLIGHT CHORUS` names no faction of its own."""
    record = KeywordClassEntry(
        keyword="THORNLIGHT CHORUS",
        keyword_class="chapter",
        parent_faction_id="f-sedgeward-conclave",
    )
    sheets = [
        datasheet("ds-gf01").model_copy(update={"keywords": curated_keywords(keyword_rows, "GF01")})
    ]

    classification = classify_keywords(
        observed=observed_keywords(sheets), factions=CHAPTER_FACTIONS, authored=(record,)
    )

    assert [f.finding_code for f in classification.findings] == []
    assert classification.chapter_keywords[0].parent_faction_id == "f-sedgeward-conclave"
