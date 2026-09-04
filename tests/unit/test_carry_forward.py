# AI-Assisted: Claude Code (model: claude-sonnet-5) - Tests for the per-faction carry-forward
# splice (008 FR-024/FR-025, Product Owner decision 2026-08-17). Written against
# `pipeline.curate.carry_forward.apply_carried_forward` before any caller in `pipeline/cli.py`
# depended on it, on the same terms every other 008 production was TDD'd: confirmed these fail
# against a stashed-out `apply_carried_forward` (ImportError), then pass once it exists.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 rung R06a (T096, FR-033): added the
# per-class composition receipts. Confirmed red first: `class_carried_slugs` did not exist as a
# parameter, so every test below raised `TypeError: apply_carried_forward() got an unexpected
# keyword argument 'class_carried_slugs'` against a stashed-out implementation.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R06a-fix item 1: confirmed red by stashing
# `pipeline/curate/carry_forward.py` back to the R06a `_CLASS_FIELDS` (`wargear_options` in,
# `item_constraints` out) -- `test_options_class_carry_...` failed both assertions (costs/
# wargear_options came back frozen at the prior values, item_constraints came back empty) before
# the field-map fix.
"""The three outcomes `apply_carried_forward` can reach, each its own finding, plus the no-op --
and (009 rung R06a) the fourth, per-class outcome that composes on top of any of the three.

Modelled on `tests/factories.py`'s existing snapshot builders rather than hand-rolling minimal
`CuratedSnapshot` scaffolding a second time.
"""

from __future__ import annotations

from pipeline.curate.carry_forward import apply_carried_forward
from pipeline.models.curated import (
    CuratedItemConstraint,
    CuratedWargearOption,
    DefaultEquipmentState,
    ItemConstraintType,
    WargearOptionState,
)
from tests.factories import costs, datasheet, faction, snapshot

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


# -- the per-class outcome: a mixed-vintage datasheet (009 rung R06a, T096, FR-033) -------------
#
# The declared faction's PRIMARY/configured arm answered live this run (it is `unused`, never
# `carried`, at the whole-faction level) -- but `curation/detail-source-authority.json` sends the
# "options" class to a DIFFERENT arm, and THAT arm's own page fetch for this faction failed. Only
# "options" is class-carried; "default_equipment" is not named in `class_carried_slugs` at all,
# because its own arm answered fine. This is deliberately built from a single faction whose
# CLASSES come from different arms -- a faction whose classes all came from one arm would look
# identical whether composition ran per class or per faction, and would not test this.

MIXED_SLUG = "mixed-vintage-faction-slug"
MIXED_FACTION_ID = "f-mixed-vintage"
MIXED_DATASHEET_ID = "ds-mixed-vintage-unit"


def _mixed_vintage_previous_tree() -> object:
    """The previous published tree: the ONLY place `EXTRACTED`/`"Prior Name"` still exist."""
    prior_datasheet = datasheet(MIXED_DATASHEET_ID, faction_id=MIXED_FACTION_ID).model_copy(
        update={
            "name": "Prior Name (should never surface)",
            "wargear_option_state": WargearOptionState.EXTRACTED,
            "default_equipment_state": DefaultEquipmentState.PARTIAL,
        }
    )
    return snapshot(
        factions=[
            faction(MIXED_FACTION_ID, parent=None).model_copy(
                update={"detail_source_faction_id": MIXED_SLUG}
            )
        ],
        datasheets=[prior_datasheet],
    )


def _mixed_vintage_candidate() -> object:
    """This run's own assembly: the configured (export) arm answered for this faction, so a
    datasheet already exists -- current name, current `default_equipment_state` (its own class's
    arm answered) -- but `wargear_option_state` is `None`: the "options" class's OWN arm
    (`html`) could not fetch this faction's page, so this run has nothing of its own to show."""
    current_datasheet = datasheet(MIXED_DATASHEET_ID, faction_id=MIXED_FACTION_ID).model_copy(
        update={
            "name": "Current Name",
            "wargear_option_state": None,
            "default_equipment_state": DefaultEquipmentState.EXTRACTED,
        }
    )
    return snapshot(
        factions=[
            faction(MIXED_FACTION_ID, parent=None).model_copy(
                update={"detail_source_faction_id": MIXED_SLUG}
            )
        ],
        datasheets=[current_datasheet],
    )


def test_a_mixed_vintage_datasheet_composes_only_the_class_that_failed() -> None:
    candidate = _mixed_vintage_candidate()
    published = _mixed_vintage_previous_tree()

    merged, findings = apply_carried_forward(
        candidate,
        previous_tree=published,
        carried_slugs=frozenset(),  # NOT whole-faction carried -- the base arm answered
        unused_declaration_slugs=frozenset({MIXED_SLUG}),  # the base arm's own view of it
        previous_version_id="wh40k-11e-2026-08-3",
        class_carried_slugs={"options": frozenset({MIXED_SLUG})},
    )

    (result,) = [d for d in merged.datasheets if d.datasheet_id == MIXED_DATASHEET_ID]

    # composed: the failed class is frozen at the previous published version, not blanked --
    assert result.wargear_option_state == WargearOptionState.EXTRACTED
    # current: every field NOT named by the "options" class stays this run's own value --
    assert result.default_equipment_state == DefaultEquipmentState.EXTRACTED
    assert result.name == "Current Name"
    # not double-counted: still exactly one datasheet, not a second row appended --
    assert len(merged.datasheets) == len(candidate.datasheets) == 1

    codes = {f.finding_code for f in findings}
    assert codes == {"SRC-FACTION-CARRY-FORWARD-UNUSED", "SRC-FACTION-CARRIED-FORWARD"}, (
        "mixed-vintage must be reported as BOTH signals together, not blended into one -- a "
        "reader sees the base arm answered (unused) AND one class still had to be carried"
    )
    composed_finding = next(f for f in findings if f.finding_code == "SRC-FACTION-CARRIED-FORWARD")
    assert composed_finding.detail["data_class"] == "options"
    assert composed_finding.detail["faction_id"] == MIXED_FACTION_ID
    assert composed_finding.detail["datasheets_carried"] == 1


def test_an_unrelated_faction_is_never_touched_by_per_class_composition() -> None:
    """The per-class splice is keyed to the declared faction alone; a faction sharing nothing
    with the declaration must come through byte-identical."""
    candidate = _mixed_vintage_candidate()
    candidate = candidate.model_copy(
        update={
            "datasheets": [
                *candidate.datasheets,
                datasheet("ds-untouched-unit", faction_id="f-untouched"),
            ]
        }
    )
    published = _mixed_vintage_previous_tree()

    merged, _findings = apply_carried_forward(
        candidate,
        previous_tree=published,
        carried_slugs=frozenset(),
        unused_declaration_slugs=frozenset({MIXED_SLUG}),
        previous_version_id="wh40k-11e-2026-08-3",
        class_carried_slugs={"options": frozenset({MIXED_SLUG})},
    )

    (untouched,) = [d for d in merged.datasheets if d.datasheet_id == "ds-untouched-unit"]
    (original,) = [d for d in candidate.datasheets if d.datasheet_id == "ds-untouched-unit"]
    assert untouched == original


def test_per_class_composition_is_skipped_for_a_slug_already_whole_faction_carried() -> None:
    """FR-033's "not double-counted": a slug already `carried` in full has nothing left for a
    class to compose, and must not report or act a second time."""
    candidate = _mixed_vintage_candidate().model_copy(update={"datasheets": []})
    published = _mixed_vintage_previous_tree()

    merged, findings = apply_carried_forward(
        candidate,
        previous_tree=published,
        carried_slugs=frozenset({MIXED_SLUG}),  # whole faction already carried
        unused_declaration_slugs=frozenset(),
        previous_version_id="wh40k-11e-2026-08-3",
        class_carried_slugs={"options": frozenset({MIXED_SLUG})},
    )

    codes = [f.finding_code for f in findings]
    assert codes == ["SRC-FACTION-CARRIED-FORWARD"]  # the whole-faction splice's own finding ONLY
    assert findings[0].detail.get("data_class") is None  # the whole-faction shape, not per-class
    assert len(merged.datasheets) == 1  # the whole prior datasheet, spliced once -- not twice


def test_per_class_composition_with_no_prior_data_blocks() -> None:
    """The same FR-008 refusal the whole-faction path gives: a class cannot be carried from a
    faction the previous published tree never had."""
    candidate = _mixed_vintage_candidate()

    merged, findings = apply_carried_forward(
        candidate,
        previous_tree=None,
        carried_slugs=frozenset(),
        unused_declaration_slugs=frozenset({MIXED_SLUG}),
        previous_version_id="(none)",
        class_carried_slugs={"options": frozenset({MIXED_SLUG})},
    )

    assert merged.datasheets == candidate.datasheets  # untouched -- nothing to compose from
    codes = [f.finding_code for f in findings]
    assert "SRC-FACTION-CARRY-FORWARD-NO-PRIOR" in codes
    no_prior = next(f for f in findings if f.finding_code == "SRC-FACTION-CARRY-FORWARD-NO-PRIOR")
    assert no_prior.severity.value == "blocking"
    assert no_prior.detail["data_class"] == "options"


# -- R06a-fix item 1: the class field map, verified in both directions ---------------------------
#
# `wargear_options` shares `_costs()`'s producer with `costs` (`curate/assemble.py::_datasheet_for`
# calls `_costs(blocks, ...)` ONCE and destructures both from that single call, over THIS run's own
# points-source blocks) -- it does not belong in `_CLASS_FIELDS["options"]`, the options-ARM class,
# and freezing it there while `costs` (never in any class map) stayed current would price the same
# datasheet from two different points acquisitions. `item_constraints` DOES belong: it is sourced
# from the SAME `_option_structure` call (`options.item_constraints`, the same `_OptionOutcome`
# that fills `option_groups`/`option_choices`), and carrying the groups without it would regress
# `loadout.item_constraints` for exactly the carried faction.


def test_options_class_carry_leaves_costs_and_wargear_options_current_and_carries_item_constraints() -> (  # noqa: E501
    None
):
    prior_option = CuratedWargearOption(
        id="wo-mixed-vintage-unit-prior-relic",
        group_key="relic",
        name="Prior Relic",
        points_delta=15,
    )
    current_option = CuratedWargearOption(
        id="wo-mixed-vintage-unit-current-relic",
        group_key="relic",
        name="Current Relic",
        points_delta=20,
    )
    prior_constraint = CuratedItemConstraint(
        constraint_index=1,
        constraint_type=ItemConstraintType.NOT_REPLACEABLE,
        item_name="Prior Sigil",
    )
    prior_costs = costs(((1, 5, 90),))
    current_costs = costs(((1, 5, 100),))

    prior_datasheet = datasheet(MIXED_DATASHEET_ID, faction_id=MIXED_FACTION_ID).model_copy(
        update={
            "wargear_option_state": WargearOptionState.EXTRACTED,
            "wargear_options": [prior_option],
            "item_constraints": [prior_constraint],
            "costs": prior_costs,
        }
    )
    published = snapshot(
        factions=[
            faction(MIXED_FACTION_ID, parent=None).model_copy(
                update={"detail_source_faction_id": MIXED_SLUG}
            )
        ],
        datasheets=[prior_datasheet],
    )

    current_datasheet = datasheet(MIXED_DATASHEET_ID, faction_id=MIXED_FACTION_ID).model_copy(
        update={
            "wargear_option_state": None,
            "wargear_options": [current_option],
            "item_constraints": [],
            "costs": current_costs,
        }
    )
    candidate = snapshot(
        factions=[
            faction(MIXED_FACTION_ID, parent=None).model_copy(
                update={"detail_source_faction_id": MIXED_SLUG}
            )
        ],
        datasheets=[current_datasheet],
    )

    merged, _findings = apply_carried_forward(
        candidate,
        previous_tree=published,
        carried_slugs=frozenset(),
        unused_declaration_slugs=frozenset({MIXED_SLUG}),
        previous_version_id="wh40k-11e-2026-08-3",
        class_carried_slugs={"options": frozenset({MIXED_SLUG})},
    )
    (result,) = [d for d in merged.datasheets if d.datasheet_id == MIXED_DATASHEET_ID]

    # `costs` and `wargear_options` are BOTH `_costs()`'s output for THIS run -- both current,
    # never split across the prior publish and this run.
    assert [row.points for row in result.costs] == [row.points for row in current_costs]
    assert [o.id for o in result.wargear_options] == [current_option.id]
    assert [o.points_delta for o in result.wargear_options] == [20]

    # `item_constraints` is carried WITH the options-arm class it is sourced from.
    assert [c.item_name for c in result.item_constraints] == ["Prior Sigil"]
    assert result.wargear_option_state == WargearOptionState.EXTRACTED  # the rest of the class


