# AI-Assisted: Claude Code (model: claude-opus-5) - User Story 1's independent test (006 task
# T024): one candidate built from the T003 quirk fixtures, asserting the Purgation-Squad-shape
# choice carries its model name, its maximum, every replaced item, every granted item with its
# own count and weapon link, and the exact delta a fixture points source prices -- and that an
# unrelated pre-existing single-item option still resolves to the shape it resolved to before.
"""User Story 1, end to end, over the fixture that carries every shape it exists to resolve.

The tests beside this one prove the pieces: the grammar's productions, the per-item join, the
priced projection. This one proves the **story** — a reader asking "what can this unit actually
take, and what does it cost" gets a complete answer out of one `_option_structure` call, with
nothing truncated to the first item and nothing invented for the rest.

The second half matters as much as the first. `004`'s single-item shapes are re-asserted here
against the same code path, because a feature that resolves new shapes by disturbing old ones has
not delivered the story — it has traded one defect for another that is harder to see.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

from pipeline.curate.assemble import _option_structure
from pipeline.curate.authored import AuthoredContent
from pipeline.models.curated import (
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
    CuratedWargearOption,
    CuratedWeaponLine,
    OptionItemRole,
    OptionScope,
)
from pipeline.parse.wahapedia_csv import CsvReadResult, read_file
from tests.enrichment.conftest import weapon

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "wahapedia"

#: GF07's weapon rows, as a run reads them from ``Datasheets_wargear.csv``. Every name is
#: invented, and the set is deliberately *complete* for the fixture's option rows: an item that
#: fails to link is covered by its own test, and mixing that case in here would make this one
#: assert two things at once.
WEAPONS: Sequence[CuratedWeaponLine] = (
    weapon(1, "Glimmer rifle"),
    weapon(2, "Ember lance"),
    weapon(3, "Psilent coil"),
    weapon(4, "Void net"),
    weapon(5, "Fen halberd"),
    weapon(6, "Close combat weapon"),
    weapon(7, "Tide hammer"),
)

#: What a fixture points source prices. The joined bundle name is priced as a whole, which is the
#: FR-008 case: the delta belongs to the swap, not to either item of it.
PRICED: Sequence[CuratedWargearOption] = (
    CuratedWargearOption(
        id="wo-purgeflight-wardens-ember-lance-and-close-combat-weapon",
        group_key="ember-lance-and-close-combat-weapon",
        name="Ember lance and 1 close combat weapon",
        points_delta=15,
    ),
)


def _detail() -> Mapping[str, CsvReadResult]:
    """The real fixture export, read through the ordinary reader a run uses."""
    return {"Datasheets_options.csv": read_file(FIXTURES / "Datasheets_options.csv")}


@pytest.fixture(scope="module")
def wardens() -> Mapping[str, CuratedOptionChoice]:
    """GF07's resolved choices, by id — the Purgation-Squad-shape datasheet."""
    outcome = _option_structure(
        "GF07", "ds-purgeflight-wardens", _detail(), AuthoredContent(), WEAPONS, PRICED
    )
    return {choice.id: choice for choice in outcome.choices}


@pytest.fixture(scope="module")
def warden_groups() -> Mapping[str, CuratedOptionGroup]:
    outcome = _option_structure(
        "GF07", "ds-purgeflight-wardens", _detail(), AuthoredContent(), WEAPONS, PRICED
    )
    return {group.id: group for group in outcome.groups}


def _items(choice: CuratedOptionChoice, role: OptionItemRole) -> list[CuratedOptionChoiceItem]:
    return [item for item in choice.items if item.role is role]


# --- the story: a scoped, multi-item, priced swap ----------------------------------------------


def test_the_group_carries_the_model_name_and_the_maximum_the_stem_states(
    warden_groups: Mapping[str, CuratedOptionGroup],
) -> None:
    group = warden_groups["og-purgeflight-wardens-1"]
    assert group.scope is OptionScope.UNIT
    assert group.eligible_model_name == "Purgeflight Wardens"
    assert group.eligible_max_count == 4
    assert group.is_per_model is True


def test_every_replaced_item_survives_rather_than_only_the_first(
    wardens: Mapping[str, CuratedOptionChoice],
) -> None:
    # The stem names two weapons the eligible models give up. `004` had nowhere to put either.
    replaced = _items(wardens["oc-purgeflight-wardens-1-1"], OptionItemRole.REPLACED)
    assert [(item.item_index, item.item_name, item.weapon_line) for item in replaced] == [
        (1, "glimmer rifle", 1),
        (2, "fen halberd", 5),
    ]


def test_every_granted_item_carries_its_own_count_and_its_own_weapon_link(
    wardens: Mapping[str, CuratedOptionChoice],
) -> None:
    granted = _items(wardens["oc-purgeflight-wardens-1-1"], OptionItemRole.GRANTED)
    assert [
        (item.item_index, item.item_name, item.count, item.weapon_line) for item in granted
    ] == [(1, "ember lance", 1, 2), (2, "close combat weapon", 1, 6)]


def test_a_multi_item_choice_carries_no_singular_field_filled_from_its_first_item(
    wardens: Mapping[str, CuratedOptionChoice],
) -> None:
    # Guarantee 12's converse, which is the whole point of the feature: showing half a swap as
    # the whole swap is a worse failure than showing an unlinked choice.
    choice = wardens["oc-purgeflight-wardens-1-1"]
    assert choice.grants_weapon_line is None
    assert choice.replaces_weapon_line is None


def test_the_bundle_carries_the_exact_delta_the_points_source_prices(
    wardens: Mapping[str, CuratedOptionChoice],
) -> None:
    choice = wardens["oc-purgeflight-wardens-1-1"]
    assert choice.points_delta == 15
    assert choice.priced_option_id == "wo-purgeflight-wardens-ember-lance-and-close-combat-weapon"


def test_the_unpriced_alternative_of_the_same_group_carries_no_delta(
    wardens: Mapping[str, CuratedOptionChoice],
) -> None:
    # Uncosted, never free (FR-013). The two alternatives of one group differ by exactly this.
    choice = wardens["oc-purgeflight-wardens-1-2"]
    assert choice.points_delta is None
    assert choice.priced_option_id is None


def test_a_conflated_legacy_label_gains_items_without_being_renamed(
    wardens: Mapping[str, CuratedOptionChoice],
) -> None:
    # The O1 Ruling over GF07|2, a row that parses TODAY and whose name conflates a bundle. The
    # name and the count are exactly what `004` produced; the items are new beside them.
    choice = wardens["oc-purgeflight-wardens-2-1"]
    assert (choice.name, choice.count) == ("ember lance and 2 void nets", 1)
    granted = _items(choice, OptionItemRole.GRANTED)
    assert [(item.item_name, item.count, item.weapon_line) for item in granted] == [
        ("ember lance", 1, 2),
        ("void nets", 2, None),
    ]


# --- and nothing 004 resolved has moved --------------------------------------------------------


def test_a_pre_existing_single_item_option_resolves_exactly_as_it_did() -> None:
    outcome = _option_structure(
        "GF01",
        "ds-glimmerfen-warden",
        _detail(),
        AuthoredContent(),
        [weapon(1, "Glimmer lantern")],
        [],
    )
    (group,) = outcome.groups
    (choice,) = outcome.choices
    assert (group.scope, group.scope_n) == (OptionScope.MODEL, None)
    assert (choice.name, choice.count) == ("glimmer lantern", 1)
    assert choice.grants_weapon_line == 1
    # Every `006` column stays omitted on a row no `006` production touched.
    assert (group.eligible_model_name, group.eligible_max_count, group.is_per_model) == (
        None,
        None,
        None,
    )
    assert (group.min_choices, group.max_choices) == (None, None)


def test_a_pre_existing_single_item_option_gains_exactly_one_mirroring_item() -> None:
    # The redundancy `006` §1.1 calls deliberate: the consumer's read becomes uniform, and the
    # one-element bundle is checkable against the singular field on every build.
    outcome = _option_structure(
        "GF01",
        "ds-glimmerfen-warden",
        _detail(),
        AuthoredContent(),
        [weapon(1, "Glimmer lantern")],
        [],
    )
    (choice,) = outcome.choices
    (item,) = choice.items
    assert (item.role, item.item_index, item.item_name, item.count, item.weapon_line) == (
        OptionItemRole.GRANTED,
        1,
        "glimmer lantern",
        1,
        1,
    )
