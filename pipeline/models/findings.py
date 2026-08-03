# AI-Assisted: Claude Code (model: claude-opus-5) - Defined Finding and ValidationReport
# (task T025) per data-model.md §6.2 and validation-report.md §1.4 and §2, with `detail` typed
# to accept ids, names, numbers, and enumerated codes only — never free text.
"""Findings and the validation report.

Two non-negotiables from ``validation-report.md`` §1 are enforced by the types themselves:

* **No publisher prose, anywhere in the report** (FR-013). A finding's ``detail`` carries
  curated ids, names, numbers, and enumerated codes. It never quotes source text — not even to
  explain a parse failure, where the temptation is greatest. Quote the *shape*
  (``{"expected_fields": 12, "actual_fields": 14}``), never the content. The
  :class:`FindingDetail` validator rejects a value that looks like prose or markup.
* **Severity is a property of the code, not of the occurrence.** :class:`Finding` therefore
  carries a severity, but :mod:`pipeline.report.catalogue` is the only sanctioned way to set
  it, and :func:`~pipeline.report.catalogue.assert_catalogued` proves a hand-built finding
  agrees with the catalogue.

``verdict`` is **derived, never authored**: blocked if any unresolved blocking finding exists,
advisory_only if only advisory findings remain, clean if none. Only the latter two are eligible
for publication (FR-029).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from pipeline.models.mechanical import MechanicalValue, assert_mechanical_value

#: The report contract this module emits (``validation-report.md``).
REPORT_CONTRACT_VERSION = "1.0.0"


class FindingClass(StrEnum):
    """The closed finding-class set (data-model.md §6.2)."""

    RECONCILIATION = "reconciliation"
    DATA_QUALITY = "data_quality"
    CONTRACT = "contract"
    AUTHORED_REFERENCE = "authored_reference"
    COVERAGE = "coverage"
    EDITION = "edition"
    SUMMARY = "summary"


class Severity(StrEnum):
    """A finding's severity. Any unresolved ``blocking`` finding refuses publication (FR-029)."""

    BLOCKING = "blocking"
    ADVISORY = "advisory"


class Verdict(StrEnum):
    """The report's derived verdict. Only ``clean`` and ``advisory_only`` may publish."""

    CLEAN = "clean"
    ADVISORY_ONLY = "advisory_only"
    BLOCKED = "blocked"


#: One finding ``detail`` object: mechanical values only.
FindingDetail = Mapping[str, MechanicalValue]


class Suggestion(BaseModel):
    """A ranked candidate for a human. **Never auto-applied** (research D5, §1.5)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    entity_ref: str
    score: float = Field(ge=0.0, le=1.0)


class Finding(BaseModel):
    """One reported disagreement, gap, or defect."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    finding_code: str
    finding_class: FindingClass
    severity: Severity
    entity_refs: Sequence[str] = ()
    detail: FindingDetail = Field(
        default_factory=dict,
        description="Mechanical values only — ids, names, numbers, enumerated codes. Never "
        "publisher prose, and never a quoted source fragment (FR-013).",
    )
    data_digest: str | None = Field(
        default=None, description="matched against a FindingResolution (FR-034)"
    )
    suggestions: Sequence[Suggestion] = ()
    resolution: str | None = Field(
        default=None, description="the explanation of a matched, unlapsed resolution"
    )

    @field_validator("detail")
    @classmethod
    def _detail_is_mechanical(cls, value: FindingDetail) -> FindingDetail:
        for key, item in value.items():
            assert_mechanical_value(item, field=f"detail.{key}")
        return value

    @property
    def is_suppressed(self) -> bool:
        """True when a dated resolution currently covers this finding (FR-034)."""
        return self.resolution is not None


class CoverageFigure(BaseModel):
    """One coverage comparison against the previous published version (FR-009)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    current: int
    previous: int
    ratio: float
    threshold: float


class ScaleFigure(BaseModel):
    """A count **and** a proportion of the snapshot.

    Every category states its scale, not merely an enumeration (FR-031, §1.3): at a few thousand
    datasheets a bare list is unreadable, and the approver's actual question is "how much of
    this release is hybrid/unverified?".
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    count: int
    proportion: float


class ValidationReport(BaseModel):
    """``reports/<rulesVersionId>/report.json`` (``validation-report.md`` §2)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    report_contract_version: str = REPORT_CONTRACT_VERSION
    run_id: str
    rules_version_id: str
    channel: str
    generated_at: str
    source_acquisitions: Sequence[Mapping[str, MechanicalValue]] = ()
    coverage: Mapping[str, CoverageFigure] = Field(default_factory=dict)
    scale: Mapping[str, ScaleFigure] = Field(default_factory=dict)
    findings: Sequence[Finding] = ()
    sub_reports: Mapping[str, str] = Field(default_factory=dict)

    @property
    def unresolved_blocking(self) -> list[Finding]:
        """Blocking findings no dated resolution currently covers."""
        return [f for f in self.findings if f.severity is Severity.BLOCKING and not f.is_suppressed]

    @property
    def verdict(self) -> Verdict:
        """Derived, never authored (§2)."""
        if self.unresolved_blocking:
            return Verdict.BLOCKED
        if any(not f.is_suppressed for f in self.findings):
            return Verdict.ADVISORY_ONLY
        return Verdict.CLEAN

    def counts(self) -> dict[str, int | dict[str, int]]:
        """``counts`` exactly as §2 shapes it: by severity, suppressed, and by class."""
        by_class = {finding_class.value: 0 for finding_class in FindingClass}
        blocking = advisory = suppressed = 0
        for finding in self.findings:
            by_class[finding.finding_class.value] += 1
            if finding.is_suppressed:
                suppressed += 1
            elif finding.severity is Severity.BLOCKING:
                blocking += 1
            else:
                advisory += 1
        return {
            "blocking": blocking,
            "advisory": advisory,
            "suppressed": suppressed,
            "by_class": by_class,
        }
