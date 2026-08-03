# AI-Assisted: Claude Code (model: claude-opus-5) - Pricing-confidence state-machine tests (task
# T080): last-known carry-forward with a visible marker and per-unit provenance, the blocking
# never-priced case, automatic clearing when the authority publishes again, and escalation past
# the configured consecutive-release threshold (FR-035, FR-035a, SC-013, SC-014).
"""Pricing confidence in both directions.

FR-035 is a statement about what a player sees: a unit the authoritative source went quiet about
**ships**, on the best price known, marked as unverified — it is never withheld and never
dropped. FR-035a is the other half, and it is the half that rots if it is not tested: when the
source publishes the unit again the marker clears **automatically**, with no curator action, or
the snapshot slowly fills with stale warnings nobody trusts.

``unpriced`` is the one pricing state that blocks, because there is no value to publish at all.
"""

from __future__ import annotations

from pipeline.models.provenance import PricingConfidence, PricingConfidenceState
from pipeline.reconcile.pricing_confidence import points_digest, resolve_confidence
from tests import factories

VERSION = "mfm-2026-06"


def outcome(**overrides: object):
    base: dict[str, object] = {
        "datasheet_id": "ds-slate-lantern",
        "priced_by_authority": False,
        "has_any_price": True,
        "prior": None,
        "rules_version_id": VERSION,
        "escalate_after": 2,
        "carried_points_digest": "sha256:" + "a" * 64,
    }
    base.update(overrides)
    return resolve_confidence(**base)  # type: ignore[arg-type]


def codes(result) -> list[str]:
    return [finding.finding_code for finding in result.findings]


def test_a_unit_the_authority_did_not_price_ships_marked_unverified() -> None:
    result = outcome()

    assert result.confidence.state is PricingConfidenceState.UNVERIFIED
    assert result.confidence.unverified_since_version == VERSION
    assert result.confidence.consecutive_unverified_releases == 1
    assert codes(result) == ["PRC-UNVERIFIED"]
    assert not result.confidence.is_blocking, "an unverified unit ships; it is never withheld"


def test_the_unverified_marker_records_when_it_first_fell_back() -> None:
    prior = PricingConfidence(
        state=PricingConfidenceState.UNVERIFIED,
        unverified_since_version="mfm-2026-04",
        consecutive_unverified_releases=1,
        last_verified_version="mfm-2026-03",
        last_verified_points_digest="sha256:" + "b" * 64,
    )
    result = outcome(prior=prior)

    assert result.confidence.unverified_since_version == "mfm-2026-04"
    assert result.confidence.consecutive_unverified_releases == 2
    assert result.confidence.last_verified_version == "mfm-2026-03"
    assert result.confidence.last_verified_points_digest == "sha256:" + "b" * 64


def test_escalation_past_the_configured_consecutive_releases() -> None:
    prior = PricingConfidence(
        state=PricingConfidenceState.UNVERIFIED,
        unverified_since_version="mfm-2026-03",
        consecutive_unverified_releases=2,
    )
    result = outcome(prior=prior, escalate_after=2)

    assert result.confidence.consecutive_unverified_releases == 3
    assert codes(result) == ["PRC-UNVERIFIED", "PRC-UNVERIFIED-STALE"]


def test_the_marker_clears_automatically_when_the_authority_publishes_again() -> None:
    prior = PricingConfidence(
        state=PricingConfidenceState.UNVERIFIED,
        unverified_since_version="mfm-2026-04",
        consecutive_unverified_releases=2,
    )
    result = outcome(prior=prior, priced_by_authority=True)

    assert result.confidence.state is PricingConfidenceState.VERIFIED
    assert result.confidence.unverified_since_version is None
    assert result.confidence.consecutive_unverified_releases == 0
    assert result.confidence.last_verified_version == VERSION
    assert codes(result) == ["PRC-REVERIFIED"], "no curator action clears the marker"


def test_a_unit_the_authority_prices_normally_reports_nothing() -> None:
    result = outcome(priced_by_authority=True)

    assert result.confidence.state is PricingConfidenceState.VERIFIED
    assert codes(result) == []


def test_a_unit_no_source_has_ever_priced_is_blocking() -> None:
    result = outcome(has_any_price=False, carried_points_digest=None)

    assert result.confidence.state is PricingConfidenceState.UNPRICED
    assert result.confidence.is_blocking
    assert codes(result) == ["REC-NEVER-PRICED"]
    assert result.findings[0].severity.value == "blocking"


def test_the_carried_points_digest_is_stable_and_order_independent() -> None:
    rows = factories.costs(((1, 3, 60), (1, 6, 115)))

    assert points_digest(rows) == points_digest(list(reversed(rows)))
    assert points_digest(rows) != points_digest(factories.costs(((1, 3, 61), (1, 6, 115))))
    assert points_digest(rows).startswith("sha256:")
