# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the finding catalogue of
# validation-report.md §3 (task T026): every code with its FIXED severity, class, and
# requirement reference, plus the only sanctioned constructor for a Finding, so severity can
# never be decided per occurrence (§1.1).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added 004-rules-data-enrichment's codes (004
# task T012): composition and option findings, keyword classification findings, the fifteen
# per-class summary codes generated from contracts/authored-summary-gates.md §3's gate table,
# the glossary orphan advisory, and the single blocking coverage ratchet code.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added COV-WEAPON-ABILITIES-EMPTY (issue #4):
# the advisory that makes a whole extracted class going empty visible, which is the one shape of
# defect every other code here is blind to because nothing about it is wrong per record.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added 007-loadout-display-fidelity's nine
# codes (007 task T013, data-model.md §4): item-constraint linking/parsing, the marker-residue
# and header-row guarantee breaches, the legacy-value-correction and over-length-item advisories,
# the generic rendering-omission code, and the two equivalence-check outcomes.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Demoted CMP-HEADER-ROW from blocking to
# advisory (007 Release phase, Product Owner decision 2026-08-14 T061 review): the live corpus's
# T031 re-derivation found real false positives among the rows the automatic conjunction would
# have dropped. See `pipeline/curate/assemble.py::_flag_header_row_candidate`.
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
    _d(
        "COV-WEAPON-ABILITIES-EMPTY",
        _COV,
        _A,
        "issue #4",
        "the snapshot publishes weapon lines and not one of them states an ability keyword; "
        "every value present is still correct, which is why nothing else would notice",
    ),
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
    _d(
        "CON-DUPLICATE-KEY",
        _CON,
        _B,
        "contract v1.3.2 guarantee 12, issue: follow-ups item 8",
        "two rows of one bundle array share the consumer's primary key and disagree; identical "
        "rows have already collapsed at emission, so what is left is a content decision the "
        "producer may not make on the app's behalf",
    ),
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
    # -- 004-rules-data-enrichment ---------------------------------------------------------
    # Composition and options (004 FR-007..FR-016, data-model.md §1.1-§1.4).
    _d(
        "CMP-UNRESOLVED",
        _DQ,
        _A,
        "004 FR-008",
        "a composition line resolved to neither production; the whole datasheet's composition "
        "is suppressed rather than published with a guessed count",
    ),
    _d(
        "OPT-UNPARSED",
        _DQ,
        _A,
        "004 FR-010",
        "an option clause head matched no production; the row is reported, never dropped",
    ),
    _d(
        "OPT-LINK-AMBIGUOUS",
        _REC,
        _A,
        "004 FR-011",
        "a choice's name matched zero or two-or-more weapon rows; it ships unlinked, never guessed",
    ),
    _d(
        "OPT-PRICED-UNMATCHED",
        _REC,
        _A,
        "004 FR-013",
        "a priced option matched no extracted choice; the priced row still ships and still "
        "prices correctly",
    ),
    _d(
        "OPT-PROJECTION-DISAGREE",
        _CON,
        _B,
        "004 FR-014, contract guarantee 8",
        "a priced option and the choice referencing it disagree on cost or count",
    ),
    # Keyword classification (004 FR-017..FR-020, data-model.md §1.5-§1.6).
    _d(
        "KWD-UNCLASSIFIED",
        _COV,
        _A,
        "004 FR-020",
        "a faction keyword resolves to no parentless faction and no curator record classifies "
        "it; the keyword ships exactly as before, classification omitted",
    ),
    _d(
        "KWD-CHAPTER-PARENT-CONFLICT",
        _CON,
        _B,
        "004 FR-019, contract guarantee 9",
        "a chapter record's chapter_faction_id names a faction whose own parent_faction_id "
        "disagrees with the record's",
    ),
    # The three new authored summary classes. Every code below is generated from
    # contracts/authored-summary-gates.md §3's table, whose single most important rule is that
    # **a gate selects a code, never a severity**: switching WGC_GATE_<CLASS> on does not make
    # an advisory code blocking, it changes which code is emitted. Severity stays a property of
    # the code (validation-report.md non-negotiable #1), which is what stops a switchable gate
    # turning a governance guarantee into a per-run judgement call.
    *(
        finding
        for prefix, requirement in (
            ("FRL", "004 FR-021, FR-029"),
            ("DRL", "004 FR-022, FR-029"),
            ("GLS", "004 FR-023, FR-029"),
        )
        for finding in (
            _d(
                f"{prefix}-OUTSTANDING",
                _SUM,
                _A,
                requirement,
                "GATE OFF: the entry has no approved summary; it ships with its NAME only, "
                "publication is not blocked, and it is named in the coverage report",
            ),
            _d(
                f"{prefix}-MISSING",
                _SUM,
                _B,
                requirement,
                "GATE ON: no authored record exists for the entry",
            ),
            _d(
                f"{prefix}-UNAPPROVED",
                _SUM,
                _B,
                requirement,
                "GATE ON: a record exists but its review_state is not approved",
            ),
            _d(
                f"{prefix}-NEEDS-REREVIEW",
                _SUM,
                _B,
                requirement,
                "GATE ON: the summary is approved but its mechanic_digest moved",
            ),
            _d(
                f"{prefix}-OVERLENGTH",
                _SUM,
                _A,
                "004 FR-024, contract §2 item 3",
                "an approved summary exceeds its class's configured length target; advisory in "
                "either gate state, so a good summary is never refused for a trailing clause",
            ),
        )
    ),
    _d(
        "GLS-ORPHANED",
        _COV,
        _A,
        "004 FR-023",
        "a glossary entry's keyword is used by no published datasheet or weapon",
    ),
    # Deliberately ONE code across all four classes, with the class in its detail. A per-class
    # code would invite a per-class severity, which is the failure §3 exists to prevent
    # (contracts/authored-summary-gates.md §4). The ratchet applies whether or not that class's
    # gate is on — that is what makes the gates-off first release safe.
    _d(
        "COV-SUMMARY-REGRESSION",
        _COV,
        _B,
        "004 FR-030",
        "a class's approved-summary coverage fell below the previously published version's, "
        "beyond that class's configured tolerance",
    ),
    # -- 006-unit-loadout-fidelity (006 data-model.md §5, FR-021) ---------------------------
    # Seven codes, of which two block. That is `004`'s proportion and the reason is unchanged:
    # a parse tail is editorial work, and a release that stalls on editorial work teaches
    # people to route around the gate. The two that block are both *contradictions* — a bundle
    # that disagrees with itself, and a coverage figure that moved the wrong way — and neither
    # is fixable by waiting.
    #
    # Two existing codes are REUSED rather than duplicated: `OPT-UNPARSED` still reports a row
    # neither production set resolves (006 FR-010), and `OPT-PROJECTION-DISAGREE`, already
    # blocking, covers FR-021's "the priced projection disagrees with the new bundle structure"
    # because it is the same disagreement about the same choice, and a second code for it would
    # be a second thing to keep in step.
    _d(
        "OPT-SCOPE-UNRESOLVED",
        _REC,
        _A,
        "006 FR-004, FR-021",
        "a group's eligible_model_name matches no composition row of its datasheet; the value "
        "ships as the source states it, unchecked, per the 2026-08-09 clarification",
    ),
    _d(
        "OPT-BUNDLE-UNLINKED",
        _REC,
        _A,
        "006 FR-007",
        "a replaced-set or granted-bundle item's name matches zero or two-or-more weapon "
        "lines; the item ships unlinked and neither its siblings nor its choice is discarded",
    ),
    _d(
        "OPT-BUNDLE-DISAGREE",
        _CON,
        _B,
        "006 contract guarantee 12",
        "a choice's singular grants_/replaces_weapon_line and its item rows contradict each "
        "other; the one-element bundle and the single-item fields must agree, not diverge",
    ),
    _d(
        "EQP-UNPARSED",
        _DQ,
        _A,
        "006 FR-012, FR-015",
        "a default-equipment sentence resolved to no production; the datasheet's state becomes "
        "partial and what did resolve still ships, reported by shape and never by quotation",
    ),
    _d(
        "EQP-GROUP-UNRESOLVED",
        _REC,
        _A,
        "006 FR-013",
        "an equipment sentence's subject names a model group matching zero or two-or-more "
        "composition rows; the link is omitted rather than resolved positionally",
    ),
    _d(
        "EQP-ITEM-UNLINKED",
        _REC,
        _A,
        "006 FR-014",
        "an equipment item's name matches zero or two-or-more weapon lines; it ships unlinked "
        "rather than guessed or silently dropped",
    ),
    _d(
        "COV-OPTION-REGRESSION",
        _COV,
        _B,
        "006 FR-022, spec Clarifications 2026-08-09",
        "loadout.options_resolved fell below the previous PUBLISHED version's percent, less "
        "the configured tolerance; a rejected candidate never moves the baseline",
    ),
    # -- 007-loadout-display-fidelity (007 data-model.md §4) --------------------------------
    # Nine codes. One blocks -- a marker artifact left in a published name (guarantee 21), the
    # same "a contradiction blocks, a gap is advisory" split `004`/`006` already use.
    # CMP-HEADER-ROW (guarantee 20) was ALSO blocking at first release of this feature, but was
    # demoted to advisory by Product Owner decision on 2026-08-14 (T061 review of the live
    # corpus's T031 re-derivation): the automatic conjunction proved to have real false positives
    # on the live corpus (three duo-sheet first models), so it no longer drops a row by itself --
    # see `pipeline/curate/assemble.py::_flag_header_row_candidate` for the full account. A
    # confirmed phantom is now removed only via a curator's `remove` entry in
    # `curation/composition-overrides.json`.
    _d(
        "CST-UNLINKED",
        _REC,
        _A,
        "007 FR-009",
        "an item constraint's item_name matches zero or two-or-more weapon lines; the row ships "
        "with weapon_line omitted, never guessed",
    ),
    _d(
        "CST-UNPARSED",
        _DQ,
        _A,
        "007 FR-009",
        "a restriction-shaped line matched no member of the closed item-constraint vocabulary; "
        "no row is produced",
    ),
    _d(
        "CST-MARKER-RESIDUE",
        _CON,
        _B,
        "007 SC-002, contract guarantee 21",
        "a published name field still carries a footnote-marker artifact; blocking because it is "
        "the exact defect this feature exists to remove, and cheap to detect",
    ),
    _d(
        "CMP-HEADER-ROW",
        _CON,
        _A,
        "007 FR-010, SC-003, contract guarantee 20",
        "a composition row's first-of-two-or-more line matches the unit-size header shape "
        "(fixed-count, unlinked, equal to the sum of its successors) -- advisory since the "
        "Product Owner's 2026-08-14 decision (T061 review): flags the row for a curator's "
        "review, never drops it automatically. A confirmed phantom is removed only via "
        "curation/composition-overrides.json's `remove` entry",
    ),
    _d(
        "OPT-LEGACY-CORRECTED",
        _REC,
        _A,
        "007 FR-007",
        "a derived singular grants_/replaces_weapon_line value differs from the previously "
        "published one; enumerated by name in option-regression.md's Corrected section",
    ),
    _d(
        "OPT-ITEM-OVERLONG",
        _DQ,
        _A,
        "007 research D3.4",
        "an item name exceeded the 120-character ceiling and was dropped; today this happens "
        "silently, which is how a bundle can lose an item with no trace",
    ),
    _d(
        "RND-OMITTED",
        _DQ,
        _A,
        "007 rendering-contract.md §4, §5",
        "a row was omitted from a rendered block, carrying one of that contract's RND-* reason "
        "codes in its detail; the enclosing block still renders every sibling that resolved",
    ),
    _d(
        "RND-EQV-MISMATCH",
        _COV,
        _A,
        "007 FR-019, contract §9",
        "a rendered block and the source block disagree under the §9 comparison normal form; "
        "carries datasheet_id and block name only, never either side's text",
    ),
    _d(
        "RND-EQV-NOT-COMPARED",
        _COV,
        _A,
        "007 FR-021, contract §9",
        "the source block could not be read on this run, or the rendered block was empty "
        "because every row was legitimately omitted; excluded from both sides of the figure",
    ),
    # -- 008-wargear-option-completion (plan.md "New finding codes") -----------------------
    # Two codes, both new additions to the catalogue rather than changes to an existing one
    # (FR-001). One is advisory -- a curator override quietly outliving the production that
    # made it redundant is editorial tidying, never a contradiction. The other blocks, on the
    # identical terms `COV-OPTION-REGRESSION` already does: `loadout.default_equipment` joins
    # the ratcheted set (FR-021, Clarifications 2026-08-15 Q2) and a figure that falls below
    # the previous PUBLISHED version's percent is exactly the kind of contradiction this
    # catalogue's two-code proportion (`004`/`006`) already reserves blocking severity for.
    _d(
        "OPT-OVERRIDE-REDUNDANT",
        _REC,
        _A,
        "008 FR-011",
        "a curator override resolves a row a production now resolves independently; the "
        "override's value is published and the entry can be retired deliberately",
    ),
    _d(
        "COV-EQUIPMENT-REGRESSION",
        _COV,
        _B,
        "008 FR-021, spec Clarifications 2026-08-15 Q2",
        "loadout.default_equipment fell below the previous PUBLISHED version's percent, less "
        "the configured tolerance; the symmetric twin of COV-OPTION-REGRESSION for the second "
        "ratcheted loadout figure",
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
