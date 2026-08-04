# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented V7, the ability-summary
# blocking and advisory checks (task T129): SUM-MISSING, SUM-UNAPPROVED, SUM-NEEDS-REREVIEW as
# blocking, and SUM-OVERLENGTH as advisory (FR-020, FR-022, FR-023).
"""V7 — every ability the snapshot uses carries an approved, current, in-length summary.

The three blocking codes are three different reasons publication is refused, kept distinct
because a curator reading the report needs to know which one to act on: `SUM-MISSING` means
"nobody has started this one", `SUM-UNAPPROVED` means "someone has, it is not signed off yet",
and `SUM-NEEDS-REREVIEW` means "it was signed off, but the mechanic moved since". Only the last
of the three can ever apply to a key a curator has already worked on — the state machine only
reaches it from `approved` (data-model.md §4.1).
"""

from __future__ import annotations

from collections.abc import Mapping

from pipeline.curate.summaries import SummaryStatus, summary_statuses
from pipeline.models.authored import AbilitySummary
from pipeline.models.curated import CuratedSnapshot
from pipeline.models.findings import Finding
from pipeline.report.catalogue import build_finding

_STATUS_CODE: Mapping[SummaryStatus, str] = {
    SummaryStatus.MISSING: "SUM-MISSING",
    SummaryStatus.DRAFT: "SUM-UNAPPROVED",
    SummaryStatus.IN_REVIEW: "SUM-UNAPPROVED",
    SummaryStatus.NEEDS_REREVIEW: "SUM-NEEDS-REREVIEW",
}


def used_ability_keys(snapshot: CuratedSnapshot) -> set[str]:
    """Every ability key at least one shipped datasheet references."""
    return {key for datasheet in snapshot.datasheets for key in datasheet.ability_keys}


def check_summaries(
    snapshot: CuratedSnapshot,
    *,
    authored_summaries: Mapping[str, AbilitySummary],
    current_digests: Mapping[str, str] | None = None,
    summary_max_chars: int,
) -> list[Finding]:
    """V7: the blocking summary-coverage checks, plus the advisory length check.

    Args:
        authored_summaries: the freshly loaded `curation/abilities/` content — **not**
            necessarily `snapshot.ability_summaries`, which a snapshot reconstructed from
            `data/` alone (a bare `validate` re-run) never carries, since authored content is
            never written to the curated tree (FR-017).
        current_digests: this run's freshly computed digests, or ``None`` when this run
            acquired no source text (see :func:`pipeline.curate.summaries.effective_status`).
    """
    statuses = summary_statuses(
        used_ability_keys(snapshot), authored=authored_summaries, current_digests=current_digests
    )

    findings: list[Finding] = []
    for key, status in sorted(statuses.items()):
        code = _STATUS_CODE.get(status)
        if code is not None:
            findings.append(build_finding(code, entity_refs=[key], detail={"ability_key": key}))
            continue

        # APPROVED: the only status left, and the only one an overlength check applies to —
        # a summary that is not approved yet is already blocking for a different reason, and
        # reporting both would ask a curator to fix a length problem on a draft they have not
        # finished writing.
        summary = authored_summaries[key]
        if len(summary.summary) > summary_max_chars:
            findings.append(
                build_finding(
                    "SUM-OVERLENGTH",
                    entity_refs=[key],
                    detail={
                        "ability_key": key,
                        "length": len(summary.summary),
                        "max_chars": summary_max_chars,
                    },
                )
            )

    return findings
