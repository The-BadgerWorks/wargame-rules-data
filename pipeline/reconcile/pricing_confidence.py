# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the verified | unverified |
# unpriced state machine with its carry-forward bookkeeping (task T091): last-known pricing keeps
# the unit in the snapshot, the marker clears automatically when the authority publishes again,
# and unpriced is the only blocking pricing state (FR-035, FR-035a, FR-035b).
"""Pricing confidence, in both directions.

FR-035 is a statement about what a player sees. A unit the authoritative source went quiet about
**ships**, at the best price known, marked as unverified. It is not withheld and it is not
dropped: an army list missing a unit the player owns is a worse outcome than one carrying a price
that is probably still right and is labelled as such.

FR-035a is the other half, and it is the half that rots if nobody watches it. When the source
publishes the unit again the marker clears **automatically** — no curator action, no ticket, no
list of things to go back and un-flag. Markers that only ever accumulate stop being read, and a
marker nobody reads is worse than no marker at all.

``unpriced`` is the one state that blocks. It is not a confidence level; it is the absence of any
value to publish, from any source, ever. There is nothing to carry forward and nothing to label,
so the run stops and a human decides whether the unit belongs in this edition at all (FR-026).
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass, field

from pipeline.build.canonical_json import dumps_bundle
from pipeline.models.curated import CuratedDatasheet, CuratedDatasheetCost
from pipeline.models.findings import Finding
from pipeline.models.mechanical import MechanicalValue
from pipeline.models.provenance import PricingConfidence, PricingConfidenceState
from pipeline.report.catalogue import build_finding


@dataclass(slots=True)
class PricingOutcome:
    """One datasheet's resolved confidence and everything it caused to be reported."""

    confidence: PricingConfidence
    findings: list[Finding] = field(default_factory=list)


def points_digest(costs: Sequence[CuratedDatasheetCost]) -> str:
    """A ``sha256:…`` over the priced values, independent of row order.

    Recorded as ``last_verified_points_digest`` so a later run can state not merely *that* a unit
    was last verified at some version but that the values it is still carrying are the ones that
    were verified then. Order-independent for the same reason every other digest here is: nothing
    downstream is matched by row order, so nothing may depend on it (FR-033).
    """
    rows = sorted((cost.copy_index_min, cost.model_count, cost.points) for cost in costs)
    payload = [{"copy_index_min": c, "model_count": m, "points": p} for c, m, p in rows]
    return f"sha256:{hashlib.sha256(dumps_bundle(payload).encode('utf-8')).hexdigest()}"


def resolve_confidence(
    *,
    datasheet_id: str,
    priced_by_authority: bool,
    has_any_price: bool,
    prior: PricingConfidence | None,
    rules_version_id: str,
    escalate_after: int,
    carried_points_digest: str | None,
) -> PricingOutcome:
    """Run the state machine for one datasheet.

    Args:
        priced_by_authority: the points source published a cost for it **this** release.
        has_any_price: any source has, now or in a previous release. The distinction between
            this and ``priced_by_authority`` is the whole of FR-035: the first decides whether
            the unit ships at all, the second decides how much we trust the number.
        prior: the confidence the previous release recorded, if there was one.
        escalate_after: ``WGC_UNVERIFIED_ESCALATE_RELEASES``.
    """
    if not has_any_price:
        return PricingOutcome(
            confidence=PricingConfidence(state=PricingConfidenceState.UNPRICED),
            findings=[
                build_finding(
                    "REC-NEVER-PRICED",
                    entity_refs=[datasheet_id],
                    detail={"datasheet_id": datasheet_id},
                )
            ],
        )

    if priced_by_authority:
        cleared = prior is not None and prior.state is PricingConfidenceState.UNVERIFIED
        outcome = PricingOutcome(
            confidence=PricingConfidence(
                state=PricingConfidenceState.VERIFIED,
                last_verified_version=rules_version_id,
                last_verified_points_digest=carried_points_digest,
            )
        )
        if cleared:
            assert prior is not None
            outcome.findings.append(
                build_finding(
                    "PRC-REVERIFIED",
                    entity_refs=[datasheet_id],
                    detail={
                        "datasheet_id": datasheet_id,
                        "unverified_since_version": prior.unverified_since_version or "",
                        "consecutive_unverified_releases": prior.consecutive_unverified_releases,
                    },
                )
            )
        return outcome

    # Unverified: the unit ships on the best price known, and says so.
    was_unverified = prior is not None and prior.state is PricingConfidenceState.UNVERIFIED
    consecutive = (prior.consecutive_unverified_releases if was_unverified and prior else 0) + 1
    since = (
        prior.unverified_since_version
        if was_unverified and prior and prior.unverified_since_version
        else rules_version_id
    )

    confidence = PricingConfidence(
        state=PricingConfidenceState.UNVERIFIED,
        unverified_since_version=since,
        consecutive_unverified_releases=consecutive,
        last_verified_version=prior.last_verified_version if prior else None,
        last_verified_points_digest=(prior.last_verified_points_digest if prior else None),
    )
    detail: dict[str, MechanicalValue] = {
        "datasheet_id": datasheet_id,
        "unverified_since_version": since,
        "consecutive_unverified_releases": consecutive,
    }
    outcome = PricingOutcome(
        confidence=confidence,
        findings=[
            build_finding("PRC-UNVERIFIED", entity_refs=[datasheet_id], detail=detail),
        ],
    )
    if consecutive > escalate_after:
        outcome.findings.append(
            build_finding(
                "PRC-UNVERIFIED-STALE",
                entity_refs=[datasheet_id],
                detail={**detail, "escalate_after": escalate_after},
            )
        )
    return outcome


def apply_pricing_confidence(
    datasheets: Sequence[CuratedDatasheet],
    *,
    prior_confidence: dict[str, PricingConfidence],
    rules_version_id: str,
    escalate_after: int,
) -> tuple[list[CuratedDatasheet], list[Finding]]:
    """Resolve every datasheet's confidence against the previous release.

    A datasheet is "priced by the authority" exactly when at least one of its cost rows was
    carried from the points source — which the assembler already records per row, so this does
    not have to re-derive it and cannot disagree with it.
    """
    resolved: list[CuratedDatasheet] = []
    findings: list[Finding] = []

    for datasheet in datasheets:
        priced_by_authority = any(
            cost.pricing_confidence is PricingConfidenceState.VERIFIED for cost in datasheet.costs
        )
        outcome = resolve_confidence(
            datasheet_id=datasheet.datasheet_id,
            priced_by_authority=priced_by_authority,
            has_any_price=bool(datasheet.costs),
            prior=prior_confidence.get(datasheet.datasheet_id),
            rules_version_id=rules_version_id,
            escalate_after=escalate_after,
            carried_points_digest=points_digest(datasheet.costs) if datasheet.costs else None,
        )
        findings.extend(outcome.findings)
        resolved.append(datasheet.model_copy(update={"pricing_confidence": outcome.confidence}))

    return resolved, findings
