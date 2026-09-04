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
    CuratedCompositionEntry,
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    CuratedItemConstraint,
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedWargearOption,
    CuratedWeaponLine,
    DefaultEquipmentState,
    EquipmentAppliesTo,
    ItemConstraintType,
    OptionItemRole,
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


# AI-Assisted: Claude Code (model: claude-sonnet-5) - R06a-fix item 2: confirmed red the same way
# as item 1 -- `test_a_class_with_no_matching_prior_datasheet_id_is_reported_not_silenced` found
# zero findings against the stashed `continue` before the fix added the
# `SRC-FACTION-CARRY-FORWARD-NO-PRIOR` report.
# -- R06a-fix item 2: a class carry that matches no current datasheet id is reported, not silent -


def test_a_class_with_no_matching_prior_datasheet_id_is_reported_not_silenced() -> None:
    """Prior data exists for the faction, but under a NEW datasheet id -- so nothing in this
    run's own assembly for the faction has a matching prior row to compose the class from. Before
    the fix this was `if not composed: continue` with zero findings; the class ships blank AND
    silent, contradicting the module's own "never silent" contract (R06a-fix item 2)."""
    prior_datasheet = datasheet("ds-retired-mixed-vintage-unit", faction_id=MIXED_FACTION_ID)
    published = snapshot(
        factions=[
            faction(MIXED_FACTION_ID, parent=None).model_copy(
                update={"detail_source_faction_id": MIXED_SLUG}
            )
        ],
        datasheets=[prior_datasheet],
    )
    candidate = _mixed_vintage_candidate()  # datasheet_id == MIXED_DATASHEET_ID, no match above

    merged, findings = apply_carried_forward(
        candidate,
        previous_tree=published,
        carried_slugs=frozenset(),
        unused_declaration_slugs=frozenset({MIXED_SLUG}),
        previous_version_id="wh40k-11e-2026-08-3",
        class_carried_slugs={"options": frozenset({MIXED_SLUG})},
    )

    # Nothing composed -- the candidate's own datasheet comes through untouched.
    (result,) = [d for d in merged.datasheets if d.datasheet_id == MIXED_DATASHEET_ID]
    assert result.wargear_option_state is None

    codes = [f.finding_code for f in findings]
    assert "SRC-FACTION-CARRY-FORWARD-NO-PRIOR" in codes, (
        "the no-match case must produce a finding -- absent before this fix (item 2)"
    )
    no_match = next(f for f in findings if f.finding_code == "SRC-FACTION-CARRY-FORWARD-NO-PRIOR")
    assert no_match.severity.value == "blocking"
    assert no_match.detail["data_class"] == "options"
    assert no_match.detail["faction_slug"] == MIXED_SLUG


# -- R06a-fix2 item 1: a frozen ordinal must not point into THIS run's weapons/composition ------
#
# `item_constraints[].weapon_line`, `option_choices[].{grants,replaces}_weapon_line` (and its own
# `items[].weapon_line`), `equipment_groups[].composition_line`, and
# `equipment_groups[].items[].weapon_line` are frozen from the PREVIOUS publish by the per-class
# splice above, onto a datasheet whose `weapons`/`composition` are THIS run's own. THIS run's own
# weapon/composition table is built once here and shared by every case below: line 1 ("Bolt
# pistol" / "Leader") is the SAME referent in both runs; line 2 held "Plasma gun" / "Trooper" in
# the previous publish and now holds something else ("Chainsword" / "Leader" is already taken, so
# the model MOVES to line 2) -- the referent still exists, just under a different ordinal; "Storm
# bolter" / "Retired Model" existed in the previous publish and does not exist THIS run at all.
#
# Confirmed red: every "moved" and "removed" assertion below fails against the carry_forward.py
# on `main` at this rung (`a915acf5`) -- the per-class splice composes `item_constraints`,
# `option_choices`, and `equipment_groups` wholesale from the prior datasheet with no
# re-resolution step at all, so a moved referent's frozen ordinal is published unchanged (pointing
# at the WRONG current row) and a removed referent's frozen ordinal is published unchanged too
# (pointing at nothing, or coincidentally at a row that exists but is not it), with zero findings
# either way. Reproduced by `git stash`-ing this rung's fix and re-running this module.

_CURRENT_WEAPONS = [
    CuratedWeaponLine(
        line=1,
        name="Bolt pistol",
        is_melee=False,
        range='12"',
        attacks="1",
        skill="3+",
        strength="4",
        armour_penetration="0",
        damage="1",
    ),
    CuratedWeaponLine(
        line=2,
        name="Chainsword",
        is_melee=True,
        attacks="3",
        skill="3+",
        strength="4",
        armour_penetration="-1",
        damage="1",
    ),
    CuratedWeaponLine(
        line=3,
        name="Plasma gun",
        is_melee=False,
        range='24"',
        attacks="1",
        skill="3+",
        strength="7",
        armour_penetration="-2",
        damage="2",
    ),
    # Deliberately NO "Storm bolter" -- the removed-referent case.
]

_CURRENT_COMPOSITION = [
    CuratedCompositionEntry(line=1, model_name="Leader", min_count=1, max_count=1, model_line=1),
    CuratedCompositionEntry(line=2, model_name="Trooper", min_count=1, max_count=5, model_line=2),
    # Deliberately NO "Retired Model" -- the removed-referent case.
]


def _reresolution_prior_datasheet() -> object:
    """The previous published tree's own datasheet: every ordinal below was correct THEN --
    `weapon_line=2` genuinely named "Plasma gun" and `composition_line=2` genuinely named
    "Trooper" at THAT publish. Neither is stated on THIS run's own weapons/composition above,
    which is the whole point: this object supplies only the frozen fields the splice composes,
    never the pool a re-resolution reads.
    """
    return datasheet(MIXED_DATASHEET_ID, faction_id=MIXED_FACTION_ID).model_copy(
        update={
            "wargear_option_state": WargearOptionState.EXTRACTED,
            "default_equipment_state": DefaultEquipmentState.EXTRACTED,
            "item_constraints": [
                CuratedItemConstraint(  # unchanged referent
                    constraint_index=1,
                    constraint_type=ItemConstraintType.NOT_REPLACEABLE,
                    item_name="Bolt pistol",
                    weapon_line=1,
                ),
                CuratedItemConstraint(  # moved referent: line 2 named Plasma gun back then
                    constraint_index=2,
                    constraint_type=ItemConstraintType.NOT_REPLACEABLE,
                    item_name="Plasma gun",
                    weapon_line=2,
                ),
                CuratedItemConstraint(  # removed referent
                    constraint_index=3,
                    constraint_type=ItemConstraintType.ONE_PER_UNIT,
                    item_name="Storm bolter",
                    weapon_line=3,
                ),
            ],
            "option_choices": [
                CuratedOptionChoice(  # unchanged referent
                    id="oc-mixed-vintage-unit-1-1",
                    group_id="og-mixed-vintage-unit-1",
                    name="Take Bolt pistol",
                    grants_weapon_line=1,
                    items=[
                        CuratedOptionChoiceItem(
                            role=OptionItemRole.GRANTED,
                            item_index=1,
                            item_name="Bolt pistol",
                            weapon_line=1,
                        )
                    ],
                ),
                CuratedOptionChoice(  # moved referent
                    id="oc-mixed-vintage-unit-1-2",
                    group_id="og-mixed-vintage-unit-1",
                    name="Take Plasma gun",
                    grants_weapon_line=2,
                    items=[
                        CuratedOptionChoiceItem(
                            role=OptionItemRole.GRANTED,
                            item_index=1,
                            item_name="Plasma gun",
                            weapon_line=2,
                        )
                    ],
                ),
                CuratedOptionChoice(  # removed referent
                    id="oc-mixed-vintage-unit-1-3",
                    group_id="og-mixed-vintage-unit-1",
                    name="Take Storm bolter",
                    grants_weapon_line=3,
                    items=[
                        CuratedOptionChoiceItem(
                            role=OptionItemRole.GRANTED,
                            item_index=1,
                            item_name="Storm bolter",
                            weapon_line=3,
                        )
                    ],
                ),
            ],
            "equipment_groups": [
                CuratedEquipmentGroup(  # unchanged referent, both composition_line and item
                    id="eq-mixed-vintage-unit-1",
                    line=1,
                    applies_to=EquipmentAppliesTo.MODEL_GROUP,
                    model_name="Leader",
                    composition_line=1,
                    items=[
                        CuratedEquipmentItem(item_index=1, item_name="Bolt pistol", weapon_line=1)
                    ],
                ),
                CuratedEquipmentGroup(  # moved referent: Trooper was composition line 1 back then
                    id="eq-mixed-vintage-unit-2",
                    line=2,
                    applies_to=EquipmentAppliesTo.MODEL_GROUP,
                    model_name="Trooper",
                    composition_line=1,
                    items=[
                        CuratedEquipmentItem(item_index=1, item_name="Plasma gun", weapon_line=2)
                    ],
                ),
                CuratedEquipmentGroup(  # removed referent, both composition_line and item
                    id="eq-mixed-vintage-unit-3",
                    line=3,
                    applies_to=EquipmentAppliesTo.MODEL_GROUP,
                    model_name="Retired Model",
                    composition_line=2,
                    items=[
                        CuratedEquipmentItem(item_index=1, item_name="Storm bolter", weapon_line=3)
                    ],
                ),
            ],
        }
    )


def _reresolution_candidate_datasheet() -> object:
    """THIS run's own assembly: the export arm answered (current weapons/composition/name), but
    the options-arm class's own arm did not fetch this faction's page at all."""
    return datasheet(MIXED_DATASHEET_ID, faction_id=MIXED_FACTION_ID).model_copy(
        update={
            "weapons": _CURRENT_WEAPONS,
            "composition": _CURRENT_COMPOSITION,
            "wargear_option_state": None,
            "default_equipment_state": None,
            "item_constraints": [],
            "option_choices": [],
            "equipment_groups": [],
        }
    )


def _reresolution_published_tree() -> object:
    return snapshot(
        factions=[
            faction(MIXED_FACTION_ID, parent=None).model_copy(
                update={"detail_source_faction_id": MIXED_SLUG}
            )
        ],
        datasheets=[_reresolution_prior_datasheet()],
    )


def _run_reresolution(data_class: str) -> tuple[object, object]:
    """Compose ``data_class`` onto :func:`_reresolution_candidate_datasheet` and return
    ``(result_datasheet, findings)``."""
    candidate = snapshot(
        factions=[
            faction(MIXED_FACTION_ID, parent=None).model_copy(
                update={"detail_source_faction_id": MIXED_SLUG}
            )
        ],
        datasheets=[_reresolution_candidate_datasheet()],
    )
    merged, findings = apply_carried_forward(
        candidate,
        previous_tree=_reresolution_published_tree(),
        carried_slugs=frozenset(),
        unused_declaration_slugs=frozenset({MIXED_SLUG}),
        previous_version_id="wh40k-11e-2026-08-3",
        class_carried_slugs={data_class: frozenset({MIXED_SLUG})},
    )
    (result,) = [d for d in merged.datasheets if d.datasheet_id == MIXED_DATASHEET_ID]
    return result, findings


# -- options side ---------------------------------------------------------------------------


def test_options_side_a_moved_weapon_resolves_to_its_new_line_not_the_stale_one() -> None:
    """`weapon_line=2` was frozen from the previous publish, when line 2 named "Plasma gun".
    THIS run's own line 2 is "Chainsword" -- a different weapon -- and "Plasma gun" now sits at
    line 3. The frozen ordinal must resolve to 3, never silently stay at 2 (a mis-point onto
    "Chainsword") and never be dropped."""
    result, _findings = _run_reresolution("options")

    moved_constraint = next(c for c in result.item_constraints if c.item_name == "Plasma gun")
    assert moved_constraint.weapon_line == 3

    moved_choice = next(c for c in result.option_choices if c.name == "Take Plasma gun")
    assert moved_choice.grants_weapon_line == 3
    assert moved_choice.items[0].weapon_line == 3


def test_options_side_a_removed_weapon_referent_produces_a_finding_not_a_silent_mispoint_or_drop() -> (  # noqa: E501
    None
):
    """The weapon "Storm bolter" does not exist in THIS run's weapons at all. The frozen ordinal
    must not be republished pointing at whatever line 3 happens to hold now (a silent mis-point),
    and the constraint/choice row itself must not vanish (a silent drop) -- only its weapon_line
    goes absent, and a finding says why."""
    result, findings = _run_reresolution("options")

    removed_constraint = next(c for c in result.item_constraints if c.item_name == "Storm bolter")
    assert removed_constraint.weapon_line is None  # not silently mis-pointed at line 3 (Plasma gun)
    assert any(  # not silently dropped: the row itself is still published
        c.constraint_index == 3 for c in result.item_constraints
    )
    assert any(
        f.finding_code == "CST-UNLINKED" and f.detail.get("item_name") == "Storm bolter"
        for f in findings
    )

    removed_choice = next(c for c in result.option_choices if c.name == "Take Storm bolter")
    assert removed_choice.grants_weapon_line is None
    assert removed_choice.items[0].weapon_line is None
    assert any(  # not silently dropped
        c.id == "oc-mixed-vintage-unit-1-3" for c in result.option_choices
    )
    assert any(
        f.finding_code == "OPT-BUNDLE-UNLINKED" and f.detail.get("choice_id") == removed_choice.id
        for f in findings
    )


def test_options_side_an_unchanged_weapon_referent_is_left_alone() -> None:
    """The weapon "Bolt pistol" is line 1 in both the previous publish and THIS run. Re-resolution
    must reproduce the same ordinal, not perturb a link that was already correct."""
    result, findings = _run_reresolution("options")

    unchanged_constraint = next(c for c in result.item_constraints if c.item_name == "Bolt pistol")
    assert unchanged_constraint.weapon_line == 1

    unchanged_choice = next(c for c in result.option_choices if c.name == "Take Bolt pistol")
    assert unchanged_choice.grants_weapon_line == 1
    assert unchanged_choice.items[0].weapon_line == 1

    assert not any(
        f.finding_code in ("CST-UNLINKED", "OPT-BUNDLE-UNLINKED")
        and f.detail.get("item_name") == "Bolt pistol"
        for f in findings
    )


# -- equipment side ---------------------------------------------------------------------------
#
# `reconcile.equipment_link` has no test of its own reused here by name, and
# `validate/refs.py::check_intra_snapshot_references` never checks `equipment_groups` at all
# (R06a-fix2 item 1's premise) -- so these receipts assert the re-resolved values directly rather
# than relying on any existing guard to fail if the fix regresses.


def test_equipment_side_a_moved_model_resolves_to_its_new_composition_line_not_the_stale_one() -> (
    None
):
    """The model "Trooper" was composition line 1 at the previous publish; "Leader" occupies THIS
    run's line 1 instead, and "Trooper" is now line 2. `composition_line` must resolve to 2, never
    stay at 1 (a mis-point onto "Leader")."""
    result, _findings = _run_reresolution("default_equipment")

    moved_group = next(g for g in result.equipment_groups if g.model_name == "Trooper")
    assert moved_group.composition_line == 2
    assert moved_group.items[0].weapon_line == 3  # "Plasma gun" also moved, 2 -> 3


def test_equipment_side_a_removed_referent_produces_a_finding_not_a_silent_mispoint_or_drop() -> (
    None
):
    """The model "Retired Model" is absent from THIS run's composition and "Storm bolter" is
    absent from THIS run's weapons. Both frozen ordinals must go absent with a finding, and the
    group/item rows themselves must still publish."""
    result, findings = _run_reresolution("default_equipment")

    removed_group = next(g for g in result.equipment_groups if g.model_name == "Retired Model")
    assert removed_group.composition_line is None
    assert removed_group.items[0].weapon_line is None
    assert any(  # not silently dropped
        g.id == "eq-mixed-vintage-unit-3" for g in result.equipment_groups
    )
    assert any(
        f.finding_code == "EQP-GROUP-UNRESOLVED"
        and f.detail.get("equipment_group_id") == removed_group.id
        for f in findings
    )
    assert any(
        f.finding_code == "EQP-ITEM-UNLINKED"
        and f.detail.get("equipment_group_id") == removed_group.id
        for f in findings
    )


def test_equipment_side_an_unchanged_referent_is_left_alone() -> None:
    """The model "Leader" is composition line 1 and "Bolt pistol" is weapon line 1 in both the
    previous publish and THIS run. Re-resolution must reproduce the same ordinals."""
    result, findings = _run_reresolution("default_equipment")

    unchanged_group = next(g for g in result.equipment_groups if g.model_name == "Leader")
    assert unchanged_group.composition_line == 1
    assert unchanged_group.items[0].weapon_line == 1

    assert not any(
        f.finding_code in ("EQP-GROUP-UNRESOLVED", "EQP-ITEM-UNLINKED")
        and f.detail.get("equipment_group_id") == unchanged_group.id
        for f in findings
    )
