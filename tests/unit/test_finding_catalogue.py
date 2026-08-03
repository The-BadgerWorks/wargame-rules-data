# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts severity is a property of the code
# and cannot be overridden per occurrence (task T026, validation-report.md §1.1), and
# transcribes the whole §3 catalogue so a code's severity cannot drift silently.
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
    "AUT-DANGLING-REF": B,
    "SUM-MISSING": B,
    "SUM-UNAPPROVED": B,
    "SUM-NEEDS-REREVIEW": B,
    "SUM-OVERLENGTH": A,
    "EDN-HYBRID-ENTITY": A,
    "CHG-DELTA-DISAGREEMENT": A,
}


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
