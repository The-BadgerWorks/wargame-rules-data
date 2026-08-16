# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts severity is a property of the code
# and cannot be overridden per occurrence (task T026, validation-report.md §1.1), and
# transcribes the whole §3 catalogue so a code's severity cannot drift silently.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Transcribed 007-loadout-display-fidelity's
# nine new codes (007 task T013) from data-model.md §4, independently of catalogue.py.
"""Severity belongs to the code, not to the occurrence.

``curation/resolutions.json`` entries reference finding codes, so a code whose severity moved
would silently change what a recorded resolution suppresses. The expected table below is
transcribed from ``validation-report.md`` §3 independently of the implementation, which is the
only way this test catches a drift rather than restating it.
"""

from __future__ import annotations

import inspect

import pytest

from pipeline.models.findings import Finding, FindingClass, Severity
from pipeline.report.catalogue import (
    BLOCKING_CODES,
    CATALOGUE,
    SeverityOverrideError,
    UnknownFindingCodeError,
    assert_catalogued,
    build_finding,
    severity_of,
)

B = "blocking"
A = "advisory"

#: Transcribed from validation-report.md §3.
CONTRACT_SEVERITIES = {
    "REC-UNMATCHED-POINTS-ONLY": A,
    "REC-UNMATCHED-DETAIL-ONLY": A,
    "REC-NEVER-PRICED": B,
    "REC-AMBIGUOUS-MATCH": B,
    "REC-BAND-MISMATCH": A,
    "REC-COMPOSITION-UNPARSED": A,
    "REC-VALUE-CONFLICT": A,
    "REC-RENAME": A,
    "REC-FACTION-ADDED": A,
    "REC-FACTION-REMOVED": A,
    "REC-FACTION-UNMAPPED": B,
    "REC-DETAIL-FACTION-ORPHAN": A,
    "PRC-UNVERIFIED": A,
    "PRC-REVERIFIED": A,
    "PRC-UNVERIFIED-STALE": A,
    "PRC-TIER-INCOMPLETE": B,
    "PRC-TIER-DETECTED": A,
    "DQ-MALFORMED-ROW": A,
    "DQ-MARKUP-IN-FIELD": A,
    "DQ-PLACEHOLDER-TOKEN": A,
    "DQ-ABILITY-TYPE": A,
    "DQ-DROPPED-FIELD": A,
    "SRC-UNREACHABLE": B,
    "SRC-REFUSED": B,
    "SRC-STRUCTURE-CHANGED": B,
    "COV-COLLAPSE": B,
    "CON-NO-COST": B,
    "CON-ORPHAN-ENHANCEMENT": B,
    "CON-BAND-GAP": B,
    "CON-BAND-OVERLAP": B,
    "CON-DANGLING-REF": B,
    "CON-RESTRICTION-VOCAB": B,
    "CON-VERSION-STAMP": B,
    "CON-IP-BOUNDARY": B,
    "CON-WARGEAR-COST-MISSING": A,
    "CON-NONDETERMINISTIC": B,
    "CON-DUPLICATE-KEY": B,
    "AUT-DANGLING-REF": B,
    "SUM-MISSING": B,
    "SUM-UNAPPROVED": B,
    "SUM-NEEDS-REREVIEW": B,
    "SUM-OVERLENGTH": A,
    "EDN-HYBRID-ENTITY": A,
    "CHG-DELTA-DISAGREEMENT": A,
}

#: Transcribed from 004's contracts/authored-summary-gates.md §3 and §3.1 and from
#: contracts/bundle-schema-delta.md guarantees 8-10, by hand and independently of
#: pipeline/report/catalogue.py. The point of writing all fifteen summary codes out rather than
#: generating them the way the implementation does is that a generator bug in the implementation
#: cannot be reproduced by the same generator in the test.
ENRICHMENT_SEVERITIES = {
    "CMP-UNRESOLVED": A,
    "OPT-UNPARSED": A,
    "OPT-LINK-AMBIGUOUS": A,
    "OPT-PRICED-UNMATCHED": A,
    "OPT-PROJECTION-DISAGREE": B,
    "KWD-UNCLASSIFIED": A,
    "KWD-CHAPTER-PARENT-CONFLICT": B,
    "FRL-OUTSTANDING": A,
    "FRL-MISSING": B,
    "FRL-UNAPPROVED": B,
    "FRL-NEEDS-REREVIEW": B,
    "FRL-OVERLENGTH": A,
    "DRL-OUTSTANDING": A,
    "DRL-MISSING": B,
    "DRL-UNAPPROVED": B,
    "DRL-NEEDS-REREVIEW": B,
    "DRL-OVERLENGTH": A,
    "GLS-OUTSTANDING": A,
    "GLS-MISSING": B,
    "GLS-UNAPPROVED": B,
    "GLS-NEEDS-REREVIEW": B,
    "GLS-OVERLENGTH": A,
    "GLS-ORPHANED": A,
    "COV-SUMMARY-REGRESSION": B,
}

#: Implemented **ahead of** its contract row, and kept in its own block so the transcription
#: above stays a faithful copy of what the contracts actually say. `validation-report.md` is
#: Frozen (002 accepted 2026-08-04) and states that any further change to it is a cross-feature
#: versioning exercise, so a bug fix may not edit it as a side effect — see `docs/follow-ups.md`
#: item 5 for the additive §3.4 row this code needs. `CON-DUPLICATE-KEY` left this block on
#: 2026-08-06 when `validation-report.md` 1.1.0 catalogued it (follow-up item 8). Severity is
#: asserted here exactly as it is for every catalogued code, so the drift protection is
#: unchanged; only the paperwork is owed.
PENDING_CONTRACT_SEVERITIES = {
    "COV-WEAPON-ABILITIES-EMPTY": A,
    # 008-wargear-option-completion (plan.md "New finding codes", tasks.md T018/T019): both new,
    # both ahead of validation-report.md's own §3 row on the identical terms
    # COV-WEAPON-ABILITIES-EMPTY already sits in this block for (docs/follow-ups.md item 5's
    # precedent, extended by this feature's own follow-up entry).
    "OPT-OVERRIDE-REDUNDANT": A,
    "COV-EQUIPMENT-REGRESSION": B,
}

#: Transcribed by hand from 006's data-model.md §5 table and its contracts/
#: loadout-schema-delta.md guarantees 12-16, independently of pipeline/report/catalogue.py.
#: Two of seven block, which is 004's proportion and deliberately so: a parse tail is editorial
#: work and a release that stalls on it teaches people to route around the gate. Both blockers
#: are contradictions rather than gaps -- a bundle disagreeing with itself, and a coverage
#: figure that moved the wrong way -- and neither is fixable by waiting.
LOADOUT_SEVERITIES = {
    "OPT-SCOPE-UNRESOLVED": A,
    "OPT-BUNDLE-UNLINKED": A,
    "OPT-BUNDLE-DISAGREE": B,
    "EQP-UNPARSED": A,
    "EQP-GROUP-UNRESOLVED": A,
    "EQP-ITEM-UNLINKED": A,
    "COV-OPTION-REGRESSION": B,
}

#: Transcribed by hand from 007's data-model.md §4 table, independently of
#: pipeline/report/catalogue.py. At first release, two of nine blocked, both guarantee breaches
#: (guarantees 20 and 21) rather than gaps -- the same split 004 and 006 already use: a
#: contradiction with what was already promised blocks, a gap in what the grammar could resolve
#: is advisory. CMP-HEADER-ROW was demoted to advisory by Product Owner decision on 2026-08-14
#: (T061 review of the live corpus's T031 re-derivation, which found real false positives among
#: the rows the automatic conjunction would have dropped) -- one of nine blocks now. See
#: pipeline/curate/assemble.py::_flag_header_row_candidate.
DISPLAY_FIDELITY_SEVERITIES = {
    "CST-UNLINKED": A,
    "CST-UNPARSED": A,
    "CST-MARKER-RESIDUE": B,
    "CMP-HEADER-ROW": A,
    "OPT-LEGACY-CORRECTED": A,
    "OPT-ITEM-OVERLONG": A,
    "RND-OMITTED": A,
    "RND-EQV-MISMATCH": A,
    "RND-EQV-NOT-COMPARED": A,
}

CONTRACT_SEVERITIES.update(ENRICHMENT_SEVERITIES)
CONTRACT_SEVERITIES.update(LOADOUT_SEVERITIES)
CONTRACT_SEVERITIES.update(PENDING_CONTRACT_SEVERITIES)
CONTRACT_SEVERITIES.update(DISPLAY_FIDELITY_SEVERITIES)


def test_the_catalogue_is_exactly_the_contract_catalogue() -> None:
    assert set(CATALOGUE) == set(CONTRACT_SEVERITIES)


@pytest.mark.parametrize(("code", "expected"), sorted(CONTRACT_SEVERITIES.items()))
def test_each_code_carries_its_contract_severity(code: str, expected: str) -> None:
    assert severity_of(code).value == expected


def test_the_blocking_set_matches_the_contract() -> None:
    assert frozenset(c for c, s in CONTRACT_SEVERITIES.items() if s == B) == BLOCKING_CODES


def test_every_definition_names_a_requirement() -> None:
    for spec in CATALOGUE.values():
        assert spec.requirement, f"{spec.code} has no requirement reference"
        assert spec.raised_when, f"{spec.code} does not say when it is raised"


def test_build_finding_offers_no_way_to_declare_a_severity() -> None:
    parameters = inspect.signature(build_finding).parameters
    assert "severity" not in parameters, "an occurrence must not be able to set its own severity"
    assert "finding_class" not in parameters


def test_build_finding_takes_class_and_severity_from_the_catalogue() -> None:
    finding = build_finding("REC-NEVER-PRICED", entity_refs=["ds-example"])
    assert finding.severity is Severity.BLOCKING
    assert finding.finding_class is FindingClass.RECONCILIATION
    assert finding.entity_refs == ("ds-example",)


def test_assert_catalogued_rejects_a_hand_built_severity_override() -> None:
    smuggled = Finding(
        finding_code="REC-NEVER-PRICED",
        finding_class=FindingClass.RECONCILIATION,
        severity=Severity.ADVISORY,
    )
    with pytest.raises(SeverityOverrideError, match="severity is a property of the code"):
        assert_catalogued(smuggled)


def test_assert_catalogued_rejects_a_hand_built_class_override() -> None:
    smuggled = Finding(
        finding_code="REC-NEVER-PRICED",
        finding_class=FindingClass.CONTRACT,
        severity=Severity.BLOCKING,
    )
    with pytest.raises(SeverityOverrideError, match="class is a property of the code"):
        assert_catalogued(smuggled)


def test_an_uncatalogued_code_is_a_hard_failure() -> None:
    with pytest.raises(UnknownFindingCodeError):
        build_finding("REC-MADE-THIS-UP")


def test_finding_detail_refuses_prose_and_markup() -> None:
    with pytest.raises(ValueError, match="markup"):
        build_finding("DQ-MARKUP-IN-FIELD", detail={"field": '<span class="kwb">x</span>'})
    with pytest.raises(ValueError, match="cyrillic"):
        build_finding("DQ-ABILITY-TYPE", detail={"observed": "Special (правая)"})


def test_finding_detail_accepts_ids_names_numbers_and_codes() -> None:
    finding = build_finding(
        "DQ-MALFORMED-ROW",
        detail={"file": "Stratagems.csv", "expected_fields": 12, "actual_fields": 14},
    )
    assert finding.detail["actual_fields"] == 14


def test_only_the_escalated_code_is_marked_escalated() -> None:
    escalated = {spec.code for spec in CATALOGUE.values() if spec.escalated}
    assert escalated == {"PRC-UNVERIFIED-STALE"}


# -- 004-rules-data-enrichment (task T012) ------------------------------------------------


@pytest.mark.parametrize("prefix", ["FRL", "DRL", "GLS"])
def test_each_new_summary_class_carries_the_whole_gate_table(prefix: str) -> None:
    """contracts/authored-summary-gates.md §3: every gate state has a code to emit.

    A missing code here is not a cosmetic gap. If the *off* state had no ``-OUTSTANDING`` code,
    an unauthored entry would either be silent — invisible to the coverage report the campaign
    is tracked by — or would have to borrow a blocking code, which is the gate-as-severity
    mistake §3 exists to prevent.
    """
    for suffix in ("OUTSTANDING", "MISSING", "UNAPPROVED", "NEEDS-REREVIEW", "OVERLENGTH"):
        assert f"{prefix}-{suffix}" in CATALOGUE


def test_a_gate_switches_the_code_not_the_severity() -> None:
    for prefix in ("FRL", "DRL", "GLS"):
        # Gate off: advisory. Publication is not blocked and the entry ships name-only.
        assert severity_of(f"{prefix}-OUTSTANDING") is Severity.ADVISORY
        # Gate on: the same underlying situation, a different code, and that code is blocking.
        assert severity_of(f"{prefix}-MISSING") is Severity.BLOCKING
        assert severity_of(f"{prefix}-UNAPPROVED") is Severity.BLOCKING
        assert severity_of(f"{prefix}-NEEDS-REREVIEW") is Severity.BLOCKING
        # Over-length is advisory in EITHER state, so a good summary is never refused for a
        # trailing clause (contract §2 item 3).
        assert severity_of(f"{prefix}-OVERLENGTH") is Severity.ADVISORY


def test_the_abilities_class_gains_no_outstanding_code() -> None:
    """The ability gate has no switch and remains always-on; FR-001 forbids weakening it.

    ``SUM-OUTSTANDING`` would be the code for an off state that cannot exist, and adding one
    would be the first step toward giving the pre-existing class a switch.
    """
    assert "SUM-OUTSTANDING" not in CATALOGUE


def test_the_ratchet_is_one_code_across_all_four_classes() -> None:
    # A per-class regression code would invite a per-class severity (contract §4).
    per_class = [c for c in CATALOGUE if c.endswith("-SUMMARY-REGRESSION")]
    assert per_class == ["COV-SUMMARY-REGRESSION"]
    assert severity_of("COV-SUMMARY-REGRESSION") is Severity.BLOCKING


def test_the_summary_codes_are_classed_as_summaries_and_the_coverage_ones_as_coverage() -> None:
    for code in ENRICHMENT_SEVERITIES:
        if code.split("-", 1)[0] in {"FRL", "DRL", "GLS"} and code != "GLS-ORPHANED":
            assert CATALOGUE[code].finding_class is FindingClass.SUMMARY, code
    # The contract's §3.1 table assigns these two to `coverage` explicitly.
    assert CATALOGUE["GLS-ORPHANED"].finding_class is FindingClass.COVERAGE
    assert CATALOGUE["COV-SUMMARY-REGRESSION"].finding_class is FindingClass.COVERAGE


def test_the_two_new_blocking_guarantees_are_contract_findings() -> None:
    # bundle-schema-delta.md guarantees 8 and 9 are consumer-contract guarantees, so a breach
    # is a contract finding rather than a reconciliation one.
    assert CATALOGUE["OPT-PROJECTION-DISAGREE"].finding_class is FindingClass.CONTRACT
    assert CATALOGUE["KWD-CHAPTER-PARENT-CONFLICT"].finding_class is FindingClass.CONTRACT


def test_the_ratchet_detail_reports_percentages_as_integers() -> None:
    """The ratchet's detail is integer percents, not floats — and this is why.

    ``contracts/authored-summary-gates.md`` §4 describes the detail as carrying
    ``previous_ratio`` / ``current_ratio`` / ``tolerance``. It cannot carry a float: canonical
    JSON here excludes floats so a bundle's bytes are reproducible (FR-039, SC-012), and every
    proportion already in the report is emitted as an integer percent. The requirement is met;
    the representation is the one that stays deterministic.
    """
    finding = build_finding(
        "COV-SUMMARY-REGRESSION",
        detail={
            "summary_class": "glossary",
            "previous_ratio_percent": 42,
            "current_ratio_percent": 31,
            "tolerance_percent": 0,
        },
    )
    assert finding.detail["current_ratio_percent"] == 31
    with pytest.raises(ValueError, match="dictionary|float|valid"):
        build_finding("COV-SUMMARY-REGRESSION", detail={"current_ratio": 0.31})


# -- 006-unit-loadout-fidelity (006 task T008) ---------------------------------------------


def test_the_loadout_codes_reuse_the_two_that_already_say_what_they_would_say() -> None:
    """A second code for one fact is a second thing to keep in step.

    `OPT-UNPARSED` already reports a row no production resolves, and `OPT-PROJECTION-DISAGREE`
    already blocks on a priced projection disagreeing with the choice that references it. 006
    FR-010 and FR-021 describe exactly those two situations over a wider grammar, so neither
    gets a new code -- and this test is what stops one being added later by someone reading
    FR-021 as a list of codes to create.
    """
    assert "OPT-UNPARSED" in CATALOGUE
    assert severity_of("OPT-PROJECTION-DISAGREE") is Severity.BLOCKING
    for invented in ("OPT-BUNDLE-UNPARSED", "OPT-ITEM-PROJECTION-DISAGREE", "EQP-PROJECTION"):
        assert invented not in CATALOGUE


def test_only_a_contradiction_blocks_among_the_loadout_codes() -> None:
    """The severities in one sentence: what is missing is advisory, what disagrees blocks."""
    blocking = {code for code, severity in LOADOUT_SEVERITIES.items() if severity == B}
    assert blocking == {"OPT-BUNDLE-DISAGREE", "COV-OPTION-REGRESSION"}
    assert blocking <= BLOCKING_CODES

    for code in set(LOADOUT_SEVERITIES) - blocking:
        assert severity_of(code) is Severity.ADVISORY, (
            f"{code} reports something the grammar could not resolve, and an unresolved row is "
            "editorial work rather than a reason to refuse a release"
        )


def test_an_unlinked_item_and_an_unresolved_group_are_reconciliation_findings() -> None:
    """Class is a property of the code too, and it decides which report section a reader looks
    in. A linking failure is reconciliation; a sentence that matched no production is data
    quality; a self-contradicting bundle is a contract breach."""
    assert CATALOGUE["OPT-BUNDLE-UNLINKED"].finding_class is FindingClass.RECONCILIATION
    assert CATALOGUE["EQP-GROUP-UNRESOLVED"].finding_class is FindingClass.RECONCILIATION
    assert CATALOGUE["EQP-ITEM-UNLINKED"].finding_class is FindingClass.RECONCILIATION
    assert CATALOGUE["EQP-UNPARSED"].finding_class is FindingClass.DATA_QUALITY
    assert CATALOGUE["OPT-BUNDLE-DISAGREE"].finding_class is FindingClass.CONTRACT
    assert CATALOGUE["COV-OPTION-REGRESSION"].finding_class is FindingClass.COVERAGE


# -- 007-loadout-display-fidelity (007 task T013) ------------------------------------------


def test_only_one_guarantee_breach_blocks_among_the_display_fidelity_codes() -> None:
    """CST-MARKER-RESIDUE still blocks: a marker character is either present in a name or it is
    not, with no false-positive risk. CMP-HEADER-ROW no longer does — Product Owner decision,
    2026-08-14 T061 review: the automatic five-signal conjunction had real false positives on the
    live corpus (three duo-sheet first models), so it is advisory-only now, flagging a candidate
    for a curator's review rather than dropping a row by itself."""
    blocking = {code for code, severity in DISPLAY_FIDELITY_SEVERITIES.items() if severity == B}
    assert blocking == {"CST-MARKER-RESIDUE"}
    assert blocking <= BLOCKING_CODES

    for code in set(DISPLAY_FIDELITY_SEVERITIES) - blocking:
        assert severity_of(code) is Severity.ADVISORY


def test_the_display_fidelity_codes_are_classed_where_the_fact_they_report_belongs() -> None:
    """Class is a property of the code: a linking failure is reconciliation, an unresolved
    shape is data quality, a guarantee breach is a contract finding, and an equivalence-check
    outcome feeds a coverage figure."""
    assert CATALOGUE["CST-UNLINKED"].finding_class is FindingClass.RECONCILIATION
    assert CATALOGUE["CST-UNPARSED"].finding_class is FindingClass.DATA_QUALITY
    assert CATALOGUE["CST-MARKER-RESIDUE"].finding_class is FindingClass.CONTRACT
    assert CATALOGUE["CMP-HEADER-ROW"].finding_class is FindingClass.CONTRACT
    assert CATALOGUE["OPT-LEGACY-CORRECTED"].finding_class is FindingClass.RECONCILIATION
    assert CATALOGUE["OPT-ITEM-OVERLONG"].finding_class is FindingClass.DATA_QUALITY
    assert CATALOGUE["RND-OMITTED"].finding_class is FindingClass.DATA_QUALITY
    assert CATALOGUE["RND-EQV-MISMATCH"].finding_class is FindingClass.COVERAGE
    assert CATALOGUE["RND-EQV-NOT-COMPARED"].finding_class is FindingClass.COVERAGE
