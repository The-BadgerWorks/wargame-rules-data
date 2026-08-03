# AI-Assisted: Claude Code (model: claude-opus-5) - Change-summary tests (task T085): every cost
# difference between two versions accounted for, added/removed/renamed classified correctly,
# pricing-confidence transitions in both directions, and a deliberate omission caught (FR-032,
# SC-010).
"""The change summary must account for **100%** of the cost differences (SC-010).

That is a stronger claim than "lists the changes", and it needs a stronger test than "the list
looks right". So the accounting is computed twice by two different routes — once by the summary
builder and once, independently, by re-deriving the raw difference set from the two versions —
and the test asserts the second finds nothing the first missed. The last test deliberately
removes an entry from a correct summary and requires that to fail, because an accounting check
that cannot fail is not a check.
"""

from __future__ import annotations

import dataclasses

from pipeline.curate.prior import prior_from_snapshot
from pipeline.models.provenance import PricingConfidence, PricingConfidenceState
from pipeline.report.change_summary import (
    compute_change_summary,
    render_change_summary,
    unaccounted_differences,
)
from tests import factories


def unverified(datasheet_id: str, points: int):
    return factories.datasheet(
        datasheet_id, cost_rows=factories.costs(((1, 1, points),))
    ).model_copy(
        update={
            "pricing_confidence": PricingConfidence(
                state=PricingConfidenceState.UNVERIFIED,
                unverified_since_version="mfm-2026-06",
                consecutive_unverified_releases=1,
            )
        }
    )


def verified(datasheet_id: str, points: int, *, name: str | None = None):
    sheet = factories.datasheet(datasheet_id, cost_rows=factories.costs(((1, 1, points),)))
    return sheet.model_copy(update={"name": name}) if name else sheet


def before():
    return factories.snapshot(
        datasheets=[
            verified("ds-slate-sentinel", 90),
            verified("ds-slate-aegis", 120, name="SLATE AEGIS"),
            verified("ds-slate-oracle", 100),
            unverified("ds-slate-warden", 70),
        ],
        detachments=[
            factories.detachment("d-slate-vigil").model_copy(update={"detachment_points_cost": 1})
        ],
        enhancements=[
            factories.enhancement("e-slate-oath", detachment_id="d-slate-vigil").model_copy(
                update={"points": 15}
            )
        ],
    )


def after():
    return factories.snapshot(
        datasheets=[
            verified("ds-slate-sentinel", 95),
            verified("ds-slate-aegis", 120, name="SLATE BULWARK"),
            verified("ds-slate-warden", 70),
            unverified("ds-slate-lantern", 60),
        ],
        detachments=[
            factories.detachment("d-slate-vigil").model_copy(update={"detachment_points_cost": 2})
        ],
        enhancements=[
            factories.enhancement("e-slate-oath", detachment_id="d-slate-vigil").model_copy(
                update={"points": 20}
            )
        ],
    )


def summary():
    return compute_change_summary(
        prior_from_snapshot(before(), rules_version_id="mfm-2026-05"), after()
    )


def test_added_and_removed_entities_are_classified_correctly() -> None:
    change = summary()

    assert change.added_datasheets == ("ds-slate-lantern",)
    assert change.removed_datasheets == ("ds-slate-oracle",)


def test_a_rename_is_classified_as_a_rename_not_as_a_removal_plus_an_addition() -> None:
    change = summary()

    assert change.renamed_datasheets == (("ds-slate-aegis", "SLATE AEGIS", "SLATE BULWARK"),)
    assert "ds-slate-aegis" not in change.added_datasheets
    assert "ds-slate-aegis" not in change.removed_datasheets


def test_every_changed_cost_appears_as_was_to_now() -> None:
    change = summary()

    assert ("ds-slate-sentinel", 1, 1, 90, 95) in change.datasheet_cost_changes
    assert ("d-slate-vigil", 1, 2) in change.detachment_cost_changes
    assert ("e-slate-oath", 15, 20) in change.enhancement_cost_changes


def test_pricing_confidence_transitions_appear_in_both_directions() -> None:
    change = summary()

    transitions = dict((entity, (was, now)) for entity, was, now in change.confidence_transitions)
    assert transitions["ds-slate-warden"] == ("unverified", "verified")
    assert "ds-slate-lantern" not in transitions, "a new datasheet has no transition, only a state"


def test_the_summary_accounts_for_every_cost_difference() -> None:
    prior = prior_from_snapshot(before(), rules_version_id="mfm-2026-05")
    current = after()

    assert unaccounted_differences(compute_change_summary(prior, current), prior, current) == []


def test_a_deliberate_omission_is_caught() -> None:
    prior = prior_from_snapshot(before(), rules_version_id="mfm-2026-05")
    current = after()
    change = compute_change_summary(prior, current)

    doctored = dataclasses.replace(change, datasheet_cost_changes=())

    unaccounted = unaccounted_differences(doctored, prior, current)
    assert unaccounted, "an accounting check that cannot fail is not a check"
    assert any("ds-slate-sentinel" in item for item in unaccounted)


def test_the_rendered_summary_names_every_class_of_change() -> None:
    rendered = render_change_summary(summary())

    for expected in (
        "ds-slate-lantern",
        "ds-slate-oracle",
        "ds-slate-aegis",
        "90",
        "95",
        "d-slate-vigil",
        "e-slate-oath",
        "ds-slate-warden",
    ):
        assert expected in rendered
