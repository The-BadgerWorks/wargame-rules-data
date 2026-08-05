# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the keyword-classification test suite
# (004 task T035), confirmed failing before pipeline/reconcile/chapters.py existed: the three
# default rules of data-model.md §1.6, the advisory KWD-UNCLASSIFIED that leaves the keyword row
# exactly as it was, and the two-faction-keyword datasheet that is the normal shape of a chapter
# unit rather than an error (004 FR-017, FR-020).
"""Default classification, the unclassified tail, and the two-faction-keyword datasheet.

The rule this suite exists to hold still is FR-020's: **an unclassified keyword ships exactly as
it does today.** Not "ships with a sensible default", not "ships with `unit`" — unchanged, with
`keyword_class` omitted, blocking nothing. A classification that guesses is worse than no
classification, because a consumer cannot tell a guess from a curated fact.
"""

from __future__ import annotations

from collections.abc import Mapping

from pipeline.models.curated import KeywordClass
from pipeline.models.findings import Severity
from pipeline.reconcile.chapters import (
    apply_keyword_classes,
    classify_keywords,
    observed_keywords,
)
from pipeline.report.catalogue import CATALOGUE
from tests.enrichment.conftest import (
    CHAPTER_FACTIONS,
    KEYWORD_CLASS_RECORDS,
    curated_keywords,
)
from tests.factories import datasheet

KeywordRows = Mapping[str, list[tuple[str, bool, str | None]]]


def _classify(keyword_rows: KeywordRows, *, datasheet_ids: tuple[str, ...] = ("GF01",)):  # type: ignore[no-untyped-def]
    sheets = [
        datasheet(f"ds-{detail_id.lower()}").model_copy(
            update={"keywords": curated_keywords(keyword_rows, detail_id)}
        )
        for detail_id in datasheet_ids
    ]
    classification = classify_keywords(
        observed=observed_keywords(sheets),
        factions=CHAPTER_FACTIONS,
        authored=KEYWORD_CLASS_RECORDS,
    )
    return sheets, classification


def test_a_non_faction_keyword_defaults_to_unit(keyword_rows: KeywordRows) -> None:
    _, classification = _classify(keyword_rows)
    assert classification.classes["INFANTRY"] is KeywordClass.UNIT


def test_a_faction_keyword_with_no_parent_faction_defaults_to_faction(
    keyword_rows: KeywordRows,
) -> None:
    """`GLIMMERFEN COVENANT` resolves to a faction carrying no `parent_faction_id`."""
    _, classification = _classify(keyword_rows)
    assert classification.classes["GLIMMERFEN COVENANT"] is KeywordClass.FACTION


def test_a_faction_keyword_the_curator_has_not_recorded_is_unclassified(
    keyword_rows: KeywordRows,
) -> None:
    """`MIREFEN ENCLAVE` is a faction keyword resolving to no parentless faction."""
    _, classification = _classify(keyword_rows, datasheet_ids=("GF05",))

    assert "MIREFEN ENCLAVE" not in classification.classes
    assert classification.unclassified == ("MIREFEN ENCLAVE",)


def test_an_unclassified_keyword_raises_the_advisory_and_blocks_nothing(
    keyword_rows: KeywordRows,
) -> None:
    _, classification = _classify(keyword_rows, datasheet_ids=("GF05",))

    unclassified = [f for f in classification.findings if f.finding_code == "KWD-UNCLASSIFIED"]
    assert [f.entity_refs[0] for f in unclassified] == ["keyword:MIREFEN ENCLAVE"]
    assert unclassified[0].severity is Severity.ADVISORY
    assert unclassified[0].severity is CATALOGUE["KWD-UNCLASSIFIED"].severity
    assert all(f.severity is Severity.ADVISORY for f in classification.findings)


def test_an_unclassified_keywords_row_is_unchanged_by_the_classification(
    keyword_rows: KeywordRows,
) -> None:
    """FR-020: byte-identical to what it was before this classification existed."""
    sheets, classification = _classify(keyword_rows, datasheet_ids=("GF05",))
    before = {k.keyword: k for k in sheets[0].keywords}

    after = {
        k.keyword: k for k in apply_keyword_classes(sheets, classification.classes)[0].keywords
    }

    assert after["MIREFEN ENCLAVE"].keyword_class is None
    assert after["MIREFEN ENCLAVE"] == before["MIREFEN ENCLAVE"]
    # Every other field of every other row is untouched too — only `keyword_class` may move.
    for keyword, row in after.items():
        assert row.model_dump(exclude={"keyword_class"}) == before[keyword].model_dump(
            exclude={"keyword_class"}
        )


def test_two_faction_keywords_on_one_datasheet_classify_without_any_error(
    keyword_rows: KeywordRows,
) -> None:
    """The normal shape of a chapter unit — 38.5% of the baseline — never an error (FR-017)."""
    sheets, classification = _classify(keyword_rows, datasheet_ids=("GF01",))

    assert sum(1 for k in sheets[0].keywords if k.is_faction_keyword) == 2
    assert classification.findings == ()
    assert classification.classes["GLIMMERFEN COVENANT"] is KeywordClass.FACTION
    assert classification.classes["THORNLIGHT CHORUS"] is KeywordClass.CHAPTER


def test_three_faction_keywords_on_one_datasheet_are_equally_fine(
    keyword_rows: KeywordRows,
) -> None:
    """GF03 carries the parent and *both* chapters; nothing about that is a defect either."""
    sheets, classification = _classify(keyword_rows, datasheet_ids=("GF03",))

    classes = {k.keyword: classification.classes.get(k.keyword) for k in sheets[0].keywords}
    assert classes == {
        "MOUNTED": KeywordClass.UNIT,
        "GLIMMERFEN COVENANT": KeywordClass.FACTION,
        "THORNLIGHT CHORUS": KeywordClass.CHAPTER,
        "BRACKLIGHT HOST": KeywordClass.CHAPTER,
    }
    assert classification.findings == ()


def test_a_curator_record_overrides_the_default(keyword_rows: KeywordRows) -> None:
    """`BRACKLIGHT HOST` resolves to a faction, but the curator says it is a chapter."""
    _, classification = _classify(keyword_rows, datasheet_ids=("GF02",))
    assert classification.classes["BRACKLIGHT HOST"] is KeywordClass.CHAPTER


def test_the_coverage_figure_counts_classified_over_distinct_keywords_in_use(
    keyword_rows: KeywordRows,
) -> None:
    _, classification = _classify(keyword_rows, datasheet_ids=("GF01", "GF05"))

    # INFANTRY, GLIMMERFEN COVENANT, THORNLIGHT CHORUS classified; MIREFEN ENCLAVE not.
    assert classification.observed_count == 4
    assert classification.classified_count == 3
