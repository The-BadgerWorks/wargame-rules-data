# AI-Assisted: Claude Code (model: claude-opus-5) - Dated-resolution tests (task T084): a
# resolution suppresses its finding only while data_digest matches, lapses automatically when the
# data moves, and a suppressed finding is still listed with its explanation (FR-034,
# validation-report.md §5).
"""Dated resolutions, and the lapse that makes them safe.

A resolution is a curator saying "I looked at this one and it is correct as published". The
digest binding is what stops that from becoming "I never want to see this class of finding
again": the suppression is bound to the *data* that produced the finding, so when the data moves
the resolution lapses on its own and the finding comes back at its catalogue severity. Nobody has
to remember to revisit it, which is the only kind of control that survives a year of releases.

Suppressed findings stay in the report. An approver has to be able to see what was waved through
and why — a silenced finding that leaves no trace is indistinguishable from one that was fixed.
"""

from __future__ import annotations

from pipeline.models.authored import FindingResolution
from pipeline.models.findings import Severity
from pipeline.reconcile.findings import apply_resolutions, data_digest, with_digest
from pipeline.report.catalogue import build_finding


def band_finding(model_count: int = 20):
    return with_digest(
        build_finding(
            "REC-BAND-MISMATCH",
            entity_refs=["ds-slate-phalanx"],
            detail={"datasheet_id": "ds-slate-phalanx", "model_count": model_count},
        )
    )


def resolution_for(
    finding, *, explanation: str = "The band is correct as published."
) -> FindingResolution:
    return FindingResolution(
        finding_code=finding.finding_code,
        entity_ref=finding.entity_refs[0],
        data_digest=finding.data_digest or "",
        resolved_at="2026-08-02T00:00:00Z",
        resolved_by="curator",
        explanation=explanation,
    )


def test_the_digest_is_a_function_of_the_data_and_nothing_else() -> None:
    first = data_digest("REC-BAND-MISMATCH", ("ds-a",), {"model_count": 20})
    again = data_digest("REC-BAND-MISMATCH", ("ds-a",), {"model_count": 20})
    moved = data_digest("REC-BAND-MISMATCH", ("ds-a",), {"model_count": 25})

    assert first == again
    assert first != moved
    assert first.startswith("sha256:")


def test_a_matching_resolution_suppresses_the_finding() -> None:
    finding = band_finding()

    (resolved,) = apply_resolutions([finding], [resolution_for(finding)])

    assert resolved.is_suppressed
    assert resolved.resolution == "The band is correct as published."
    assert resolved.severity is Severity.ADVISORY, "the catalogue severity is unchanged"


def test_the_resolution_lapses_automatically_when_the_underlying_data_changes() -> None:
    stale = resolution_for(band_finding(model_count=20))

    (raised,) = apply_resolutions([band_finding(model_count=25)], [stale])

    assert not raised.is_suppressed
    assert raised.resolution is None, (
        "a curator may not silence a class of finding permanently; the digest binds the "
        "suppression to the data that produced it"
    )


def test_a_resolution_for_another_entity_suppresses_nothing() -> None:
    finding = band_finding()
    elsewhere = resolution_for(finding).model_copy(update={"entity_ref": "ds-something-else"})

    (raised,) = apply_resolutions([finding], [elsewhere])

    assert not raised.is_suppressed


def test_a_blocking_finding_can_be_resolved_but_stays_blocking_severity() -> None:
    finding = with_digest(
        build_finding(
            "REC-NEVER-PRICED",
            entity_refs=["ds-slate-cipher"],
            detail={"datasheet_id": "ds-slate-cipher"},
        )
    )

    (resolved,) = apply_resolutions([finding], [resolution_for(finding)])

    assert resolved.severity is Severity.BLOCKING
    assert resolved.is_suppressed, "the only ways past a blocking finding are a fix or a resolution"


def test_suppressed_findings_are_still_listed_with_their_explanation() -> None:
    finding = band_finding()

    resolved = apply_resolutions([finding, band_finding(model_count=25)], [resolution_for(finding)])

    assert len(resolved) == 2, "suppression never removes a finding from the report"
    assert [f.is_suppressed for f in resolved] == [True, False]
