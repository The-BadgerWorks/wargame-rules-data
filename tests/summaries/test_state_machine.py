# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the ability-summary state-machine
# test suite (task T124), confirmed failing before pipeline.curate.summaries existed: draft,
# in_review, and needs_rereview each block with their catalogued code; approved carries forward
# untouched while the digest is unchanged; and a moved digest flips exactly one summary (FR-020,
# FR-023, FR-024, SC-011).
"""The effective per-ability status a run observes, and the three catalogued blocking codes."""

from __future__ import annotations

from pipeline.curate.summaries import SummaryStatus, effective_status, summary_statuses
from pipeline.models.authored import AbilitySummary, ReviewState
from pipeline.models.curated import CuratedSnapshot
from pipeline.models.findings import Severity
from pipeline.report.catalogue import CATALOGUE
from pipeline.validate.summaries import check_summaries
from tests.factories import datasheet, snapshot, summaries


def _summary(
    key: str,
    *,
    review_state: ReviewState = ReviewState.APPROVED,
    mechanic_digest: str = "d" * 32,
) -> AbilitySummary:
    return AbilitySummary(
        ability_key=key,
        name=key.split(":")[-1].replace("-", " ").title(),
        summary="Invented mechanics-only summary authored for this data set.",
        review_state=review_state,
        mechanic_digest=mechanic_digest,
        reviewed_by="curator",
        reviewed_at="2026-06-13T00:00:00Z",
    )


def test_draft_blocks_with_sum_unapproved() -> None:
    authored = {"core:deep-strike": _summary("core:deep-strike", review_state=ReviewState.DRAFT)}
    assert (
        effective_status("core:deep-strike", authored=authored, current_digest=None)
        is SummaryStatus.DRAFT
    )
    assert SummaryStatus.DRAFT.blocks_publication


def test_in_review_blocks_with_sum_unapproved() -> None:
    authored = {
        "core:deep-strike": _summary("core:deep-strike", review_state=ReviewState.IN_REVIEW)
    }
    assert (
        effective_status("core:deep-strike", authored=authored, current_digest=None)
        is SummaryStatus.IN_REVIEW
    )
    assert SummaryStatus.IN_REVIEW.blocks_publication


def test_needs_rereview_blocks() -> None:
    authored = {
        "core:deep-strike": _summary("core:deep-strike", review_state=ReviewState.NEEDS_REREVIEW)
    }
    assert (
        effective_status("core:deep-strike", authored=authored, current_digest=None)
        is SummaryStatus.NEEDS_REREVIEW
    )
    assert SummaryStatus.NEEDS_REREVIEW.blocks_publication


def test_missing_key_blocks_as_missing() -> None:
    assert (
        effective_status("core:deep-strike", authored={}, current_digest=None)
        is SummaryStatus.MISSING
    )
    assert SummaryStatus.MISSING.blocks_publication


def test_approved_carries_forward_untouched_while_digest_is_unchanged() -> None:
    authored = {
        "core:deep-strike": _summary(
            "core:deep-strike", review_state=ReviewState.APPROVED, mechanic_digest="d" * 32
        )
    }
    status = effective_status("core:deep-strike", authored=authored, current_digest="d" * 32)
    assert status is SummaryStatus.APPROVED
    assert not status.blocks_publication


def test_no_fresh_digest_trusts_the_stored_approved_state() -> None:
    """A bare `validate` re-run has no source text at all — no evidence, no flip (FR-024)."""
    authored = {
        "core:deep-strike": _summary(
            "core:deep-strike", review_state=ReviewState.APPROVED, mechanic_digest="d" * 32
        )
    }
    status = effective_status("core:deep-strike", authored=authored, current_digest=None)
    assert status is SummaryStatus.APPROVED


def test_a_moved_digest_flips_exactly_one_summary_to_needs_rereview_and_no_others() -> None:
    authored = {
        "core:deep-strike": _summary(
            "core:deep-strike", review_state=ReviewState.APPROVED, mechanic_digest="d" * 32
        ),
        "core:leader": _summary(
            "core:leader", review_state=ReviewState.APPROVED, mechanic_digest="e" * 32
        ),
        "datasheet:ember-shield": _summary(
            "datasheet:ember-shield", review_state=ReviewState.APPROVED, mechanic_digest="f" * 32
        ),
    }
    # Only "core:deep-strike"'s source text changed this run; the other two digest identically.
    current_digests = {
        "core:deep-strike": "9" * 32,  # moved
        "core:leader": "e" * 32,  # unchanged
        "datasheet:ember-shield": "f" * 32,  # unchanged
    }

    statuses = summary_statuses(authored.keys(), authored=authored, current_digests=current_digests)

    assert statuses["core:deep-strike"] is SummaryStatus.NEEDS_REREVIEW
    assert statuses["core:leader"] is SummaryStatus.APPROVED
    assert statuses["datasheet:ember-shield"] is SummaryStatus.APPROVED
    flipped = [key for key, status in statuses.items() if status is SummaryStatus.NEEDS_REREVIEW]
    assert flipped == ["core:deep-strike"]


def _catalogue_severity(code: str) -> Severity:
    return CATALOGUE[code].severity


def test_check_summaries_raises_the_catalogued_blocking_codes() -> None:
    ds = datasheet(
        ability_keys=("core:deep-strike", "core:leader", "datasheet:ember-shield", "core:missing")
    )
    snap = snapshot(
        datasheets=[ds],
        ability_summaries={
            "core:deep-strike": _summary("core:deep-strike", review_state=ReviewState.DRAFT),
            "core:leader": _summary("core:leader", review_state=ReviewState.IN_REVIEW),
            "datasheet:ember-shield": _summary(
                "datasheet:ember-shield", review_state=ReviewState.NEEDS_REREVIEW
            ),
            # "core:missing" has no authored record at all.
        },
    )

    findings = check_summaries(
        snap,
        authored_summaries=snap.ability_summaries,
        current_digests=None,
        summary_max_chars=240,
    )

    by_key = {finding.entity_refs[0]: finding for finding in findings}
    assert by_key["core:deep-strike"].finding_code == "SUM-UNAPPROVED"
    assert by_key["core:leader"].finding_code == "SUM-UNAPPROVED"
    assert by_key["datasheet:ember-shield"].finding_code == "SUM-NEEDS-REREVIEW"
    assert by_key["core:missing"].finding_code == "SUM-MISSING"
    for finding in findings:
        assert finding.severity is Severity.BLOCKING
        assert finding.severity is _catalogue_severity(finding.finding_code)


def test_check_summaries_raises_advisory_overlength_only_for_approved_summaries() -> None:
    ds = datasheet(ability_keys=("core:deep-strike",))
    overlength = _summary("core:deep-strike", mechanic_digest="d" * 32)
    overlength = overlength.model_copy(update={"summary": "x" * 241})
    snap = snapshot(datasheets=[ds], ability_summaries={"core:deep-strike": overlength})

    findings = check_summaries(
        snap,
        authored_summaries=snap.ability_summaries,
        current_digests={"core:deep-strike": "d" * 32},
        summary_max_chars=240,
    )

    assert len(findings) == 1
    assert findings[0].finding_code == "SUM-OVERLENGTH"
    assert findings[0].severity is Severity.ADVISORY
    assert findings[0].severity is _catalogue_severity("SUM-OVERLENGTH")


def test_check_summaries_is_clean_when_every_used_key_is_approved_and_current() -> None:
    ds = datasheet(ability_keys=("core:deep-strike",))
    snap = snapshot(datasheets=[ds], ability_summaries=summaries(("core:deep-strike",)))

    findings = check_summaries(
        snap,
        authored_summaries=snap.ability_summaries,
        current_digests={"core:deep-strike": "0" * 32},
        summary_max_chars=240,
    )

    assert findings == []


def test_a_snapshot_carrying_no_datasheets_reports_no_summary_findings() -> None:
    empty = CuratedSnapshot(edition=snapshot().edition)
    assert (
        check_summaries(empty, authored_summaries={}, current_digests=None, summary_max_chars=240)
        == []
    )
