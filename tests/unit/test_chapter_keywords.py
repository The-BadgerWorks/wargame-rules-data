# AI-Assisted: Claude Opus 5 - 010 R6 task 5. Failing-first receipt for the five
# `curation/keyword-classes.json` records stranded by publishing keywords upper-case, and for the
# `keyword_classification` coverage collapse the stranding is one part of (1 370 -> 1 297); the r6
# build measured this fix recovering 5 of those 73 points (1 297 -> 1 302), so the stranding is not
# the whole cause and the remainder is not accounted for here. The index
# matched `record.keyword` exactly, so a record and an observed keyword that are the same token in
# different case no longer met.
"""A curator's record and an observed keyword are one token, whatever case each states it in.

`curation/` is not editable by this change, and it should not have to be: the case a token is
*printed* in is a presentation fact, and a classification keyed on it is keyed on the wrong
thing. The index therefore folds case on both sides.

All identifiers and names here are invented.
"""

from __future__ import annotations

from pipeline.models.authored import KeywordClassEntry
from pipeline.models.curated import KeywordClass
from pipeline.reconcile.chapters import classify_keywords

#: A curator record as `curation/keyword-classes.json` states one — upper-case token, invented.
_RECORD = KeywordClassEntry(
    keyword="FEN WARDENS",
    keyword_class="chapter",
    parent_faction_id="f-test-parent",
)


def test_a_record_classifies_an_observed_keyword_stated_in_another_case() -> None:
    """The stranded-records receipt.

    Reverted, this is red: `by_keyword` misses, the keyword falls through to the default rules,
    and — being a faction keyword resolving to no parentless faction — it lands in
    `unclassified` with a `KWD-UNCLASSIFIED` finding instead of being classified `chapter`.
    """
    classification = classify_keywords(
        observed={"Fen Wardens": True},
        factions=(),
        authored=(_RECORD,),
    )

    assert classification.classes.get("Fen Wardens") is KeywordClass.CHAPTER, (
        "a curator record was stranded by case: classified "
        f"{classification.classes.get('Fen Wardens')}, "
        f"unclassified {list(classification.unclassified)}"
    )
    assert not classification.unclassified
    assert [f.finding_code for f in classification.findings] == []


def test_an_exact_case_match_still_classifies() -> None:
    """The true positive still fires — folding case must not cost the match it already had."""
    classification = classify_keywords(
        observed={"FEN WARDENS": True},
        factions=(),
        authored=(_RECORD,),
    )

    assert classification.classes.get("FEN WARDENS") is KeywordClass.CHAPTER
    assert not classification.unclassified
