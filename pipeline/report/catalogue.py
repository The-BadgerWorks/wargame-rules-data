# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the finding catalogue of
# validation-report.md §3 (task T026): every code with its FIXED severity, class, and
# requirement reference, plus the only sanctioned constructor for a Finding, so severity can
# never be decided per occurrence (§1.1).
"""The finding catalogue.

``validation-report.md`` §1.1: **severity is a property of the code, not of the occurrence.** A
run may not decide that a normally-blocking finding is advisory today. This module is where
that rule is made mechanical:

* :data:`CATALOGUE` fixes each code's class, severity, and requirement reference.
* :func:`build_finding` is the sanctioned constructor. It takes **no severity argument** —
  there is no way to pass one — so an occurrence cannot override the catalogue.
* :func:`assert_catalogued` proves a finding built some other way agrees with the catalogue.

Codes are stable identifiers. A code's meaning or severity may not change without a MAJOR bump
of ``validation-report.md``, because ``curation/resolutions.json`` entries reference them.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from pipeline.models.findings import Finding, FindingClass, FindingDetail, Severity, Suggestion

_B: Final = Severity.BLOCKING
_A: Final = Severity.ADVISORY


class UnknownFindingCodeError(KeyError):
    """A finding code that is not in the catalogue.

    Hard failure by design: an uncatalogued code has no fixed severity, so a report containing
    one could not be trusted to refuse publication correctly (FR-029).
    """


class SeverityOverrideError(ValueError):
    """A finding whose severity or class disagrees with the catalogue (§1.1)."""


@dataclass(frozen=True, slots=True)
class FindingDefinition:
    """One catalogued code: its class, its fixed severity, and what it means."""

    code: str
    finding_class: FindingClass
    severity: Severity
    requirement: str
    raised_when: str
    escalated: bool = False
    """``PRC-UNVERIFIED-STALE`` is advisory but escalated past the configured threshold."""


def _d(
    code: str,
    finding_class: FindingClass,
    severity: Severity,
    requirement: str,
    raised_when: str,
    *,
    escalated: bool = False,
) -> FindingDefinition:
    return FindingDefinition(code, finding_class, severity, requirement, raised_when, escalated)


_REC: Final = FindingClass.RECONCILIATION
_DQ: Final = FindingClass.DATA_QUALITY
_CON: Final = FindingClass.CONTRACT
_AUT: Final = FindingClass.AUTHORED_REFERENCE
_COV: Final = FindingClass.COVERAGE
_EDN: Final = FindingClass.EDITION
_SUM: Final = FindingClass.SUMMARY

_DEFINITIONS: Final[tuple[FindingDefinition, ...]] = (
    # §3.1 Reconciliation
    _d("REC-UNMATCHED-POINTS-ONLY", _REC, _A, "FR-026", "a points unit matches no datasheet"),
    _d(
        "REC-UNMATCHED-DETAIL-ONLY",
        _REC,
        _A,
        "FR-026, FR-035",
        "a datasheet has no points entry this release; ships on last-known pricing",
    ),
    _d("REC-NEVER-PRICED", _REC, _B, "FR-026", "no source has ever published a price"),
    _d(
        "REC-AMBIGUOUS-MATCH",
        _REC,
        _B,
        "FR-014",
        "candidates remain after faction scope and Legends disambiguation; treated as NO match",
    ),
    _d("REC-BAND-MISMATCH", _REC, _A, "FR-027", "bands unreconcilable with the composition"),
    _d("REC-COMPOSITION-UNPARSED", _REC, _A, "FR-027", "composition free text yielded no count"),
    _d(
        "REC-VALUE-CONFLICT",
        _REC,
        _A,
        "FR-028",
        "both sources publish a value and disagree; points source wins, loser carried nowhere",
    ),
    _d("REC-RENAME", _REC, _A, "FR-015", "a curated id's display name changed"),
    _d("REC-FACTION-ADDED", _REC, _A, "FR-004", "the publisher's faction list gained a faction"),
    _d("REC-FACTION-REMOVED", _REC, _A, "FR-004", "the publisher's faction list lost a faction"),
    _d("REC-FACTION-UNMAPPED", _REC, _B, "C3/R6", "a points-source slug has no faction-map entry"),
    _d("REC-DETAIL-FACTION-ORPHAN", _REC, _A, "C3/R6", "a detail faction id is referenced by none"),
    # §3.2 Pricing confidence
    _d("PRC-UNVERIFIED", _REC, _A, "FR-035", "priced from last-known values; marker set"),
    _d("PRC-REVERIFIED", _REC, _A, "FR-035a", "the authority published it again; marker cleared"),
    _d(
        "PRC-UNVERIFIED-STALE",
        _REC,
        _A,
        "spec config",
        "unverified for more than the configured consecutive releases",
        escalated=True,
    ),
    _d(
        "PRC-TIER-INCOMPLETE",
        _REC,
        _B,
        "contract v1.2.0 guarantee 7",
        "a copy_index_min > 1 tier exists for some model_count but not others, or the "
        "copy_index_min = 1 row is missing",
    ),
    _d("PRC-TIER-DETECTED", _REC, _A, "C1/R2", "a datasheet gained or lost an escalating tier"),
    # §3.3 Data quality
    _d("DQ-MALFORMED-ROW", _DQ, _A, "FR-006", "a source record needed structural repair"),
    _d("DQ-MARKUP-IN-FIELD", _DQ, _A, "FR-006", "markup found in a field before stripping"),
    _d("DQ-PLACEHOLDER-TOKEN", _DQ, _A, "FR-006", "an unresolved $ token"),
    _d("DQ-ABILITY-TYPE", _DQ, _A, "FR-006", "a classification value outside the mapping table"),
    _d("DQ-DROPPED-FIELD", _DQ, _A, "C4/R7", "a source field deliberately not carried"),
    # §3.4 Source and coverage
    _d("SRC-UNREACHABLE", _COV, _B, "FR-008", "a source did not respond"),
    _d("SRC-REFUSED", _COV, _B, "FR-007", "a source refused or throttled; the run stops"),
    _d("SRC-STRUCTURE-CHANGED", _COV, _B, "FR-008", "values can no longer be extracted reliably"),
    _d("COV-COLLAPSE", _COV, _B, "FR-009", "coverage fell below the configured proportion"),
    # §3.5 Contract, authored content, summaries, edition
    _d("CON-NO-COST", _CON, _B, "FR-030", "a datasheet has no cost row"),
    _d("CON-ORPHAN-ENHANCEMENT", _CON, _B, "FR-030", "an enhancement's detachment is absent"),
    _d("CON-BAND-GAP", _CON, _B, "FR-030, C7/R9", "point bands are not contiguous"),
    _d("CON-BAND-OVERLAP", _CON, _B, "FR-030, C7/R9", "point bands overlap"),
    _d("CON-DANGLING-REF", _CON, _B, "FR-030", "an intra-snapshot reference does not resolve"),
    _d("CON-RESTRICTION-VOCAB", _CON, _B, "FR-030", "a restriction_type outside the closed set"),
    _d("CON-VERSION-STAMP", _CON, _B, "FR-030, FR-049", "a version stamp is missing or mismatched"),
    _d(
        "CON-IP-BOUNDARY",
        _CON,
        _B,
        "FR-012, FR-013, SC-003",
        "the IP scan found markup, an entity, a $ token, a Cyrillic artefact, over-length free "
        "text, or a file under work/",
    ),
    _d(
        "CON-WARGEAR-COST-MISSING",
        _CON,
        _A,
        "C8/R3",
        "an option's structure is known but the points source publishes no cost; never a zero",
    ),
    _d("CON-NONDETERMINISTIC", _CON, _B, "FR-033", "a rebuild produced a different checksum"),
    _d("AUT-DANGLING-REF", _AUT, _B, "FR-018", "an authored record references a missing entity"),
    _d("SUM-MISSING", _SUM, _B, "FR-020", "an ability binding has no summary record"),
    _d("SUM-UNAPPROVED", _SUM, _B, "FR-023", "a summary is draft or in_review"),
    _d("SUM-NEEDS-REREVIEW", _SUM, _B, "FR-024", "mechanic_digest moved; awaiting re-approval"),
    _d("SUM-OVERLENGTH", _SUM, _A, "FR-022", "a summary exceeds the configured length target"),
    _d("EDN-HYBRID-ENTITY", _EDN, _A, "FR-058, FR-060", "detail is from an older edition"),
    _d(
        "CHG-DELTA-DISAGREEMENT",
        _DQ,
        _A,
        "FR-032 cross-check",
        "our change summary disagrees with the source's own delta markers",
    ),
)

#: The catalogue, by code. The single source of truth for a finding's class and severity.
CATALOGUE: Final[Mapping[str, FindingDefinition]] = {d.code: d for d in _DEFINITIONS}

#: The codes that refuse publication when unresolved (FR-029).
BLOCKING_CODES: Final[frozenset[str]] = frozenset(
    d.code for d in _DEFINITIONS if d.severity is Severity.BLOCKING
)


def definition(code: str) -> FindingDefinition:
    """Look up ``code``, or raise :class:`UnknownFindingCodeError`."""
    try:
        return CATALOGUE[code]
    except KeyError as exc:
        raise UnknownFindingCodeError(f"{code} is not in the finding catalogue") from exc


def severity_of(code: str) -> Severity:
    """The code's fixed severity."""
    return definition(code).severity


def build_finding(
    code: str,
    *,
    entity_refs: Sequence[str] = (),
    detail: FindingDetail | None = None,
    data_digest: str | None = None,
    suggestions: Sequence[Suggestion] = (),
    resolution: str | None = None,
) -> Finding:
    """Construct a :class:`~pipeline.models.findings.Finding` from the catalogue.

    There is deliberately **no** ``severity`` or ``finding_class`` parameter: both come from the
    catalogue, which is what makes §1.1 structural rather than a review rule.
    """
    spec = definition(code)
    return Finding(
        finding_code=spec.code,
        finding_class=spec.finding_class,
        severity=spec.severity,
        entity_refs=tuple(entity_refs),
        detail=dict(detail or {}),
        data_digest=data_digest,
        suggestions=tuple(suggestions),
        resolution=resolution,
    )


def assert_catalogued(finding: Finding) -> Finding:
    """Assert a finding's class and severity match its code, or raise.

    Used on any finding that did not come from :func:`build_finding` — for instance one read
    back from a previous run's ``report.json``.
    """
    spec = definition(finding.finding_code)
    if finding.severity is not spec.severity:
        raise SeverityOverrideError(
            f"{finding.finding_code}: severity is a property of the code "
            f"({spec.severity.value}); an occurrence may not declare {finding.severity.value}"
        )
    if finding.finding_class is not spec.finding_class:
        raise SeverityOverrideError(
            f"{finding.finding_code}: class is a property of the code "
            f"({spec.finding_class.value}), not {finding.finding_class.value}"
        )
    return finding
