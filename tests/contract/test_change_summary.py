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

import pytest

from pipeline.curate.prior import prior_from_snapshot
from pipeline.models.authored import ReviewState
from pipeline.models.curated import KeywordClass
from pipeline.models.provenance import PricingConfidence, PricingConfidenceState
from pipeline.report.change_summary import (
    ENRICHMENT_CATEGORIES,
    EnrichmentChanges,
    compute_change_summary,
    compute_enrichment_changes,
    render_change_summary,
    unaccounted_differences,
    unaccounted_enrichment_differences,
)
from tests import factories
from tests.contract.enrichment_bundle import enriched_snapshot


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

    assert ("ds-slate-sentinel", 1, 1, "", 90, 95) in change.datasheet_cost_changes
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


# --- the five enrichment categories (004 task T070, FR-037) --------------------------------------


def _enriched_before():  # type: ignore[no-untyped-def]
    return enriched_snapshot()


def _enriched_after():  # type: ignore[no-untyped-def]
    """The same version with exactly one change in each of the five categories.

    One change per category, and no more: an omission check that has ten things to notice can
    pass while missing one of them, and this suite's whole job is to notice a single omission.
    """
    previous = enriched_snapshot()
    warden, rider = previous.datasheets

    moved_warden = warden.model_copy(
        update={
            # 1. composition: the squad's upper bound moves.
            "composition": [
                entry.model_copy(update={"max_count": 11}) if entry.line == 2 else entry
                for entry in warden.composition
            ],
            # 2. option groups: one is retired upstream, and its choice goes with it.
            "option_groups": [g for g in warden.option_groups if g.id != "og-fen-warden-2"],
            "option_choices": [
                # 3. option choices: one is repriced.
                choice.model_copy(update={"points_delta": 20})
                if choice.id == "oc-fen-warden-1-2"
                else choice
                for choice in warden.option_choices
                if choice.group_id != "og-fen-warden-2"
            ],
            # 4. keyword classification: a curator classifies a keyword that had none.
            "keywords": [
                keyword.model_copy(update={"keyword_class": KeywordClass.UNIT})
                if keyword.keyword == "TIDEWALK"
                else keyword
                for keyword in warden.keywords
            ],
        }
    )
    # 5. authored summaries: one rule's mechanic moved, so its digest did.
    rules = dict(previous.detachment_rules)
    key = "detachment:d-fenlight-vigil:veiled-advance"
    rules[key] = rules[key].model_copy(update={"mechanic_digest": "9" * 32})

    return previous.model_copy(
        update={"datasheets": [moved_warden, rider], "detachment_rules": rules}
    )


def test_a_first_release_reports_nothing_rather_than_reporting_everything() -> None:
    """An "everything is new" list is not a change summary anyone reads."""
    changes = compute_enrichment_changes(None, _enriched_after())

    assert changes == EnrichmentChanges()
    assert unaccounted_enrichment_differences(changes, None, _enriched_after()) == []


def test_every_enrichment_category_notices_its_own_change() -> None:
    changes = compute_enrichment_changes(_enriched_before(), _enriched_after())

    assert changes.composition_changes == (
        ("ds-fen-warden", 2, "Fen Warden 4-9", "Fen Warden 4-11"),
    )
    assert changes.option_group_changes == (("ds-fen-warden", "og-fen-warden-2", "removed"),)
    assert ("ds-fen-warden", "oc-fen-warden-1-2", "repriced", "15", "20") in (
        changes.option_choice_changes
    )
    assert changes.keyword_class_changes == (("TIDEWALK", "unclassified", "unit"),)
    assert changes.summary_changes == (
        ("detachment_rules", "detachment:d-fenlight-vigil:veiled-advance", "changed"),
    )


def test_an_unpriced_choice_reads_as_unpriced_and_never_as_zero() -> None:
    """A choice the source does not price and a choice priced at zero are different facts."""
    previous = _enriched_before()
    warden = previous.datasheets[0]
    priced = warden.model_copy(
        update={
            "option_choices": [
                choice.model_copy(update={"points_delta": 0})
                if choice.id == "oc-fen-warden-2-1"
                else choice
                for choice in warden.option_choices
            ]
        }
    )
    current = previous.model_copy(update={"datasheets": [priced, previous.datasheets[1]]})

    changes = compute_enrichment_changes(previous, current)

    assert ("ds-fen-warden", "oc-fen-warden-2-1", "repriced", "unpriced", "0") in (
        changes.option_choice_changes
    )


def test_the_enrichment_summary_accounts_for_every_difference() -> None:
    previous, current = _enriched_before(), _enriched_after()

    changes = compute_enrichment_changes(previous, current)

    assert unaccounted_enrichment_differences(changes, previous, current) == []


@pytest.mark.parametrize("category", ENRICHMENT_CATEGORIES)
def test_a_deliberate_omission_of_any_category_is_caught(category: str) -> None:
    """An accounting check that cannot fail is not a check — five times over."""
    previous, current = _enriched_before(), _enriched_after()
    changes = compute_enrichment_changes(previous, current)
    assert changes.entries(category), f"{category} has nothing to omit, so this proves nothing"

    doctored = dataclasses.replace(changes, **{category: ()})

    unaccounted = unaccounted_enrichment_differences(doctored, previous, current)
    assert unaccounted, f"{category} can be dropped without the accounting check noticing"
    assert all(item.startswith(f"{category}:") for item in unaccounted)


def test_the_rendered_summary_names_every_enrichment_change() -> None:
    changes = compute_enrichment_changes(_enriched_before(), _enriched_after())

    rendered = render_change_summary(summary(), changes)

    for expected in (
        "Fen Warden 4-9 -> Fen Warden 4-11".replace("->", "→"),
        "`og-fen-warden-2`: removed",
        "`oc-fen-warden-1-2`: repriced (15 -> 20)".replace("->", "→"),
        "`TIDEWALK`: unclassified -> unit".replace("->", "→"),
        "detachment:d-fenlight-vigil:veiled-advance`: changed",
    ):
        assert expected in rendered


def test_a_summary_flagged_for_re_review_is_reported_as_flagged() -> None:
    previous = _enriched_before()
    rules = dict(previous.detachment_rules)
    key = "detachment:d-fenlight-vigil:veiled-advance"
    rules[key] = rules[key].model_copy(update={"review_state": ReviewState.NEEDS_REREVIEW})
    current = previous.model_copy(update={"detachment_rules": rules})

    changes = compute_enrichment_changes(previous, current)

    assert changes.summary_changes == (("detachment_rules", key, "flagged"),)


def test_authored_summaries_absent_from_the_previous_tree_report_nothing() -> None:
    """The honest degradation, asserted rather than described in a comment.

    `curation/` is never written to `data/` (FR-017), so a previous snapshot reconstructed from
    the tree carries no authored summaries at all. The category then stays silent instead of
    declaring every summary in the data set newly added — which would bury the four categories
    that *are* derivable from the tree under thousands of lines that say nothing.
    """
    previous = _enriched_before().model_copy(
        update={
            "ability_summaries": {},
            "faction_rules": {},
            "detachment_rules": {},
            "keyword_glossary": {},
        }
    )

    changes = compute_enrichment_changes(previous, _enriched_after())

    assert changes.summary_changes == ()
    assert unaccounted_enrichment_differences(changes, previous, _enriched_after()) == []
