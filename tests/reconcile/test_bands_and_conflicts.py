# AI-Assisted: Claude Code (model: claude-opus-5) - Band-reconciliation and value-conflict tests
# (task T081): the two separately counted advisory classes of FR-027, and the FR-028 authority
# applied so the losing value is carried nowhere.
"""Model-count bands, and what happens when both sources publish the same value.

Two advisory classes, deliberately **separate**: "the composition could not be read at all" and
"the composition was read and the band does not fit inside it" are different problems with
different fixes, and collapsing them into one number tells an approver neither.

The conflict rule is the sharper one. FR-002 makes the points source authoritative for every
value a player pays, so a disagreement is not a negotiation: the points value wins, both values
are recorded in the report so the disagreement is visible, and the losing value is carried
**nowhere** — not into the tree, not into the bundle, not as a fallback.
"""

from __future__ import annotations

import pytest

from pipeline.models.findings import Severity
from pipeline.reconcile.bands import BandClass, parse_composition, reconcile_bands
from pipeline.reconcile.conflicts import resolve_cost_conflict


def codes(findings) -> list[str]:
    return [finding.finding_code for finding in findings]


# --- composition parsing (FR-027, research D5) ------------------------------------------------


@pytest.mark.parametrize(
    ("lines", "expected"),
    [
        (["1 Slate Sentinel"], (1, 1, BandClass.EXACT)),
        (["5-10 Slate Phalanx"], (5, 10, BandClass.RANGE)),
        (["1 Warboss", "3-6 Nobz"], (4, 7, BandClass.RANGE)),
        (["A cohort of Slate Wardens"], (None, None, BandClass.UNPARSED)),
        ([], (None, None, BandClass.UNPARSED)),
    ],
)
def test_composition_free_text_yields_a_representable_size_range(lines, expected) -> None:
    parsed = parse_composition(lines)

    assert (parsed.minimum, parsed.maximum, parsed.classification) == expected


def test_a_band_inside_the_composition_reports_nothing() -> None:
    findings = reconcile_bands(
        datasheet_id="ds-slate-phalanx",
        model_counts=[5, 10],
        composition_lines=["5-10 Slate Phalanx"],
    )

    assert findings == []


def test_a_band_outside_the_composition_is_a_separate_advisory_class() -> None:
    findings = reconcile_bands(
        datasheet_id="ds-slate-phalanx",
        model_counts=[5, 20],
        composition_lines=["5-10 Slate Phalanx"],
    )

    assert codes(findings) == ["REC-BAND-MISMATCH"]
    assert findings[0].severity is Severity.ADVISORY
    assert findings[0].detail["model_count"] == 20
    assert findings[0].detail["composition_max"] == 10


def test_unparseable_composition_is_the_other_advisory_class_and_is_reported_once() -> None:
    findings = reconcile_bands(
        datasheet_id="ds-slate-warden",
        model_counts=[1, 5],
        composition_lines=["A cohort of Slate Wardens"],
    )

    assert codes(findings) == ["REC-COMPOSITION-UNPARSED"], (
        "an unreadable composition cannot also produce band mismatches — that would double-count "
        "one defect into two categories"
    )


# --- value conflicts (FR-028) -----------------------------------------------------------------


def test_the_points_source_wins_and_both_values_are_recorded() -> None:
    resolved = resolve_cost_conflict(
        datasheet_id="ds-slate-phalanx", model_count=5, points_value=90, detail_value=85
    )

    assert resolved.value == 90, "FR-002: the points source owns every value a player pays"
    (finding,) = resolved.findings
    assert finding.finding_code == "REC-VALUE-CONFLICT"
    assert finding.severity is Severity.ADVISORY
    assert finding.detail["points_source_value"] == 90
    assert finding.detail["detail_source_value"] == 85


def test_agreement_reports_nothing() -> None:
    resolved = resolve_cost_conflict(
        datasheet_id="ds-slate-phalanx", model_count=5, points_value=90, detail_value=90
    )

    assert resolved.value == 90
    assert resolved.findings == []


def test_a_value_only_one_source_publishes_is_not_a_conflict() -> None:
    resolved = resolve_cost_conflict(
        datasheet_id="ds-slate-phalanx", model_count=5, points_value=90, detail_value=None
    )

    assert resolved.value == 90
    assert resolved.findings == []
