# AI-Assisted: Claude Code (model: claude-sonnet-5) - Tests for the per-faction carry-forward
# splice (008 FR-024/FR-025, Product Owner decision 2026-08-17). Written against
# `pipeline.curate.carry_forward.apply_carried_forward` before any caller in `pipeline/cli.py`
# depended on it, on the same terms every other 008 production was TDD'd: confirmed these fail
# against a stashed-out `apply_carried_forward` (ImportError), then pass once it exists.
"""The three outcomes `apply_carried_forward` can reach, each its own finding, plus the no-op.

Modelled on `tests/factories.py`'s existing snapshot builders rather than hand-rolling minimal
`CuratedSnapshot` scaffolding a second time.
"""

from __future__ import annotations

from pipeline.curate.carry_forward import apply_carried_forward
from tests.factories import datasheet, faction, snapshot

CARRIED_SLUG = "carried-faction-slug"
LIVE_SLUG = "live-faction-slug"


def _published_with_two_factions() -> object:
    """The previous published tree: faction A (live-fetched every run) and faction B (the one
    this run's acquisition could not reach)."""
    faction_a = faction("f-live-faction", parent=None)
    faction_b = faction("f-carried-faction", parent=None).model_copy(
        update={"detail_source_faction_id": CARRIED_SLUG}
    )
    faction_a = faction_a.model_copy(update={"detail_source_faction_id": LIVE_SLUG})
    return snapshot(
        factions=[faction_a, faction_b],
        datasheets=[
            datasheet("ds-live-unit", faction_id="f-live-faction"),
            datasheet("ds-carried-unit", faction_id="f-carried-faction"),
        ],
    )


def _live_only_candidate() -> object:
    """This run's own candidate: only faction A came through acquisition."""
    faction_a = faction("f-live-faction", parent=None).model_copy(
        update={"detail_source_faction_id": LIVE_SLUG}
    )
    return snapshot(
        factions=[faction_a],
        datasheets=[datasheet("ds-live-unit", faction_id="f-live-faction")],
    )


def test_a_carried_faction_is_spliced_in_from_the_previous_tree() -> None:
    candidate = _live_only_candidate()
    published = _published_with_two_factions()

    merged, findings = apply_carried_forward(
        candidate,
        previous_tree=published,
        carried_slugs=frozenset({CARRIED_SLUG}),
        unused_declaration_slugs=frozenset(),
        previous_version_id="wh40k-11e-2026-08-3",
    )

    assert {d.datasheet_id for d in merged.datasheets} == {"ds-live-unit", "ds-carried-unit"}
    assert len(findings) == 1
    finding = findings[0]
    assert finding.finding_code == "SRC-FACTION-CARRIED-FORWARD"
    assert finding.severity.value == "advisory"
    assert finding.detail["faction_id"] == "f-carried-faction"
    assert finding.detail["faction_slug"] == CARRIED_SLUG
    assert finding.detail["frozen_at_version"] == "wh40k-11e-2026-08-3"


def test_a_carried_faction_never_duplicates_a_datasheet_already_present() -> None:
    """A carried faction that somehow shares an id with something already live-fetched does not
    get a second copy — the live copy always wins, since it is strictly newer information."""
    candidate = _live_only_candidate()
    candidate = candidate.model_copy(
        update={
            "datasheets": [
                *candidate.datasheets,
                datasheet("ds-carried-unit", faction_id="f-live-faction"),
            ]
        }
    )
    published = _published_with_two_factions()

    merged, _findings = apply_carried_forward(
        candidate,
        previous_tree=published,
        carried_slugs=frozenset({CARRIED_SLUG}),
        unused_declaration_slugs=frozenset(),
        previous_version_id="wh40k-11e-2026-08-3",
    )

    ids = [d.datasheet_id for d in merged.datasheets]
    assert ids.count("ds-carried-unit") == 1
    # And it is the live-fetched copy (faction f-live-faction), never the carried one.
    (kept,) = [d for d in merged.datasheets if d.datasheet_id == "ds-carried-unit"]
    assert kept.faction_id == "f-live-faction"


def test_a_faction_fetched_live_despite_being_declared_is_marked_unused_not_carried() -> None:
    candidate = _live_only_candidate()
    published = _published_with_two_factions()

    merged, findings = apply_carried_forward(
        candidate,
        previous_tree=published,
        carried_slugs=frozenset(),
        unused_declaration_slugs=frozenset({LIVE_SLUG}),
        previous_version_id="wh40k-11e-2026-08-3",
    )

    # Nothing spliced in — the live data (already in `candidate`) is what publishes.
    assert {d.datasheet_id for d in merged.datasheets} == {"ds-live-unit"}
    assert len(findings) == 1
    assert findings[0].finding_code == "SRC-FACTION-CARRY-FORWARD-UNUSED"
    assert findings[0].severity.value == "advisory"
    assert findings[0].detail["faction_slug"] == LIVE_SLUG


def test_a_declared_faction_with_no_prior_data_blocks_rather_than_fabricating() -> None:
    """FR-008's guarantee holds even through the escape hatch: a declaration cannot manufacture
    data that was never published — this is a first-release faction, or a slug typo."""
    candidate = _live_only_candidate()
    published = _live_only_candidate()  # no second faction anywhere in the prior tree either

    merged, findings = apply_carried_forward(
        candidate,
        previous_tree=published,
        carried_slugs=frozenset({"never-published-slug"}),
        unused_declaration_slugs=frozenset(),
        previous_version_id="wh40k-11e-2026-08-3",
    )

    assert {d.datasheet_id for d in merged.datasheets} == {"ds-live-unit"}
    assert len(findings) == 1
    assert findings[0].finding_code == "SRC-FACTION-CARRY-FORWARD-NO-PRIOR"
    assert findings[0].severity.value == "blocking"
    assert findings[0].detail["faction_slug"] == "never-published-slug"


def test_a_declared_faction_with_no_previous_tree_at_all_blocks() -> None:
    """A first release has no `previous_tree` (``None``) — the same refusal, not a crash."""
    candidate = _live_only_candidate()

    merged, findings = apply_carried_forward(
        candidate,
        previous_tree=None,
        carried_slugs=frozenset({CARRIED_SLUG}),
        unused_declaration_slugs=frozenset(),
        previous_version_id="(none)",
    )

    assert merged.datasheets == candidate.datasheets
    assert len(findings) == 1
    assert findings[0].finding_code == "SRC-FACTION-CARRY-FORWARD-NO-PRIOR"


def test_no_declaration_at_all_is_a_true_no_op() -> None:
    candidate = _live_only_candidate()

    merged, findings = apply_carried_forward(
        candidate,
        previous_tree=_published_with_two_factions(),
        carried_slugs=frozenset(),
        unused_declaration_slugs=frozenset(),
        previous_version_id="wh40k-11e-2026-08-3",
    )

    assert merged is candidate
    assert findings == ()
