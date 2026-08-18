# AI-Assisted: Claude Code (model: claude-opus-5) - The choice-to-weapon join's contract (004
# task T023): exactly one normalised-name match links, zero or two-or-more report
# OPT-LINK-AMBIGUOUS and ship unlinked, and the clause verb decides which of the two link fields
# the match lands in (FR-011).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 007 US2 (T019/T023): rewrote
# `link_choice_weapons`'s own tests for its new contract — it reports `OPT-LINK-AMBIGUOUS` and
# writes NOTHING, since `link_choice_items`'s per-role loop is the singular fields' sole writer
# now (research D3, contract guarantee 19).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 008 US2 (T045): a granted bundle and a
# replaced set produced by one of Phase 4's new `_COMPLETION_VERBS` productions link through
# `link_choice_items` on the identical exactly-one-match rule as a `004`/`006` row's — the join
# does not know or care which production built the choice it is handed.
"""The join the source does not publish, and what it does when it cannot be made.

There is no foreign key from an option row to a wargear row, and the wargear rows have no stable
row key — up to 18 of them share a ``(datasheet_id, line, line_in_wargear, name)`` quadruple. So
the join is by normalised name, it succeeds for about four choices in five, and the interesting
behaviour is the fifth: it is **left unlinked and named in the report**, never attached to
whichever profile happened to sort first.
"""

from __future__ import annotations

import pytest

from pipeline.models.curated import (
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    OptionItemRole,
)
from pipeline.models.findings import Severity
from pipeline.parse.options_grammar import (
    NO_CHANGE_NAME,
    parse_row,
    split_conjuncts,
    split_replaced,
)
from pipeline.reconcile.options_link import link_choice_items, link_choice_weapons
from pipeline.report.catalogue import CATALOGUE
from tests.enrichment.conftest import weapon

DATASHEET = "ds-sedgeward-conclave"


def choice(index: int, name: str, **overrides: object) -> CuratedOptionChoice:
    return CuratedOptionChoice(
        id=f"oc-sedgeward-conclave-1-{index}",
        group_id="og-sedgeward-conclave-1",
        name=name,
        **overrides,  # type: ignore[arg-type]
    )


def test_an_exact_match_reports_nothing_and_writes_nothing() -> None:
    # 007 T023: `link_choice_weapons` no longer writes either singular field, for either verb —
    # `link_choice_items`'s per-role loop is the sole writer now.
    linked, findings = link_choice_weapons(
        datasheet_id=DATASHEET,
        choices=[choice(1, "sedge halberd")],
        weapons=[weapon(1, "Warding rod"), weapon(2, "Sedge halberd")],
    )
    assert findings == []
    assert linked[0].replaces_weapon_line is None
    assert linked[0].grants_weapon_line is None
    assert linked[0] == choice(1, "sedge halberd")  # unchanged, byte for byte


def test_zero_matches_reports_and_writes_nothing() -> None:
    linked, findings = link_choice_weapons(
        datasheet_id=DATASHEET,
        choices=[choice(1, "glimmer lantern")],
        weapons=[weapon(1, "Warding rod")],
    )
    assert linked[0].grants_weapon_line is None
    assert linked[0].replaces_weapon_line is None
    assert [f.finding_code for f in findings] == ["OPT-LINK-AMBIGUOUS"]
    assert findings[0].detail["match_count"] == 0


def test_two_or_more_matches_report_and_write_nothing() -> None:
    # The export really does publish two rows under one name — a weapon with two profiles — and
    # picking either would silently attach the choice to the wrong one half the time.
    linked, findings = link_choice_weapons(
        datasheet_id=DATASHEET,
        choices=[choice(1, "mire censer")],
        weapons=[weapon(3, "Mire censer"), weapon(4, "Mire censer")],
    )
    assert linked[0].replaces_weapon_line is None
    assert findings[0].detail["match_count"] == 2


def test_the_link_is_never_guessed_and_the_finding_is_advisory() -> None:
    # Advisory, because an unlinked choice is a navigational gap in one datasheet — not a reason
    # to refuse a whole release.
    assert CATALOGUE["OPT-LINK-AMBIGUOUS"].severity is Severity.ADVISORY


def test_the_join_folds_casing_spacing_and_punctuation() -> None:
    linked, findings = link_choice_weapons(
        datasheet_id=DATASHEET,
        choices=[choice(1, "SEDGE  HALBERD")],
        weapons=[weapon(7, "Sedge halberd")],
    )
    assert findings == []
    assert linked[0].grants_weapon_line is None


def test_a_no_change_alternative_names_no_weapon_and_raises_nothing() -> None:
    linked, findings = link_choice_weapons(
        datasheet_id=DATASHEET,
        choices=[choice(3, NO_CHANGE_NAME, is_no_change=True)],
        weapons=[weapon(1, "Warding rod")],
    )
    assert findings == []
    assert linked[0].grants_weapon_line is None


def test_linking_is_deterministic() -> None:
    args = {
        "datasheet_id": DATASHEET,
        "choices": [choice(1, "mire censer"), choice(2, "sedge halberd")],
        "weapons": [weapon(4, "Mire censer"), weapon(3, "Mire censer"), weapon(2, "Sedge halberd")],
    }
    first = link_choice_weapons(**args)  # type: ignore[arg-type]
    second = link_choice_weapons(**args)  # type: ignore[arg-type]
    assert first == second


# --- 006 US1: per-item linking and guarantee 12 (T014) -----------------------------------------
#
# `link_choice_weapons` above is untouched, and stays untouched: it is what sets the singular
# fields `004` publishes, and FR-009 is a promise about those values. Everything below is a
# second join over a second array, and the one place the two meet is guarantee 12's invariant.


def item(
    role: OptionItemRole, index: int, name: str, **overrides: object
) -> CuratedOptionChoiceItem:
    return CuratedOptionChoiceItem(
        role=role,
        item_index=index,
        item_name=name,
        **overrides,  # type: ignore[arg-type]
    )


def test_each_item_of_a_bundle_links_on_its_own_exactly_one_match() -> None:
    linked, findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[
            choice(
                1,
                "ember lance and 1 close combat weapon",
                items=[
                    item(OptionItemRole.GRANTED, 1, "ember lance", count=1),
                    item(OptionItemRole.GRANTED, 2, "close combat weapon", count=1),
                ],
            )
        ],
        weapons=[weapon(2, "Ember lance"), weapon(6, "Close combat weapon")],
    )
    assert findings == []
    assert [i.weapon_line for i in linked[0].items] == [2, 6]


def test_an_unlinkable_item_never_discards_its_siblings_or_its_choice() -> None:
    # FR-007 in terms: the item ships unlinked and the rest of the bundle ships linked. A join
    # that dropped the bundle would turn one ambiguous name into a whole missing swap.
    linked, findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[
            choice(
                1,
                "ember lance and 1 mire censer",
                items=[
                    item(OptionItemRole.GRANTED, 1, "ember lance", count=1),
                    item(OptionItemRole.GRANTED, 2, "mire censer", count=1),
                ],
            )
        ],
        weapons=[weapon(2, "Ember lance"), weapon(3, "Mire censer"), weapon(4, "Mire censer")],
    )
    assert [i.weapon_line for i in linked[0].items] == [2, None]
    assert [f.finding_code for f in findings] == ["OPT-BUNDLE-UNLINKED"]
    assert findings[0].detail["match_count"] == 2
    assert CATALOGUE["OPT-BUNDLE-UNLINKED"].severity is Severity.ADVISORY


def test_zero_matches_reports_the_same_advisory_and_ships_the_item() -> None:
    linked, findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[choice(1, "void net", items=[item(OptionItemRole.GRANTED, 1, "void net")])],
        weapons=[weapon(1, "Warding rod")],
    )
    assert linked[0].items[0].weapon_line is None
    assert [f.finding_code for f in findings] == ["OPT-BUNDLE-UNLINKED"]
    assert findings[0].detail["match_count"] == 0


def test_a_one_element_bundle_agrees_with_the_singular_field_it_mirrors() -> None:
    # Guarantee 12/19, the direction that matters most: every choice `004` publishes today
    # acquires exactly one mirroring item row carrying the same line, so a consumer can iterate
    # items uniformly and read the same fact either way.
    linked, findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[
            choice(
                1,
                "sedge halberd",
                replaces_weapon_line=2,
                items=[item(OptionItemRole.REPLACED, 1, "sedge halberd")],
            )
        ],
        weapons=[weapon(2, "Sedge halberd")],
    )
    assert findings == []
    assert linked[0].items[0].weapon_line == 2
    assert linked[0].replaces_weapon_line == 2


def test_a_sole_item_that_links_supplies_the_singular_field_it_mirrors() -> None:
    # The other half of the biconditional. A distributive stem names the removed weapon in its
    # own head rather than in the object clause, so the singular field can only come from the
    # item - and leaving it absent would publish a one-element bundle that disagrees with its
    # own choice by omission.
    linked, findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[
            choice(
                1,
                "ember lance",
                grants_weapon_line=2,
                items=[
                    item(OptionItemRole.GRANTED, 1, "ember lance"),
                    item(OptionItemRole.REPLACED, 1, "sedge halberd"),
                ],
            )
        ],
        weapons=[weapon(2, "Ember lance"), weapon(3, "Sedge halberd")],
    )
    assert findings == []
    assert linked[0].replaces_weapon_line == 3


def test_a_multi_item_side_carries_no_singular_field_at_all() -> None:
    # Filling it from the first item is precisely the truncation this feature exists to remove.
    linked, findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[
            choice(
                1,
                "ember lance and 1 void net",
                items=[
                    item(OptionItemRole.GRANTED, 1, "ember lance"),
                    item(OptionItemRole.GRANTED, 2, "void net"),
                ],
            )
        ],
        weapons=[weapon(2, "Ember lance"), weapon(7, "Void net")],
    )
    assert findings == []
    assert linked[0].grants_weapon_line is None


# --- 007 US2: the singular field as a TOTAL FUNCTION of the item rows (T019, contract guarantee
# 19, replacing the "partial fill" reading of the two tests above) -----------------------------
#
# `link_choice_weapons` no longer writes `grants_`/`replaces_weapon_line` at all (T023): every
# choice reaching `link_choice_items` therefore carries `stated = None` on both fields in
# production, and the field the caller reads afterwards is *entirely* `link_choice_items`'s own
# computation — never a value it merely left alone because something upstream got there first.
# `OPT-BUNDLE-DISAGREE` stays wired for a value that arrives already populated (a curator override
# merge, a future regression) but defends a coding error now, not divergent extraction (research
# D3, contract §4.1).


@pytest.mark.parametrize(
    ("item_names", "expected"),
    [
        # exactly one item, linked -> present, equal to its line (D3.3 case 1: "resolved and
        # relinked").
        (["storm maul"], 4),
        # exactly one item, matching no weapon -> omitted (D3.3 case 2: "stated but unlinked").
        (["ceremonial rod"], None),
        # zero items on the role -> omitted (D3.3 case 3: "no given-up item stated").
        ([], None),
    ],
)
def test_the_singular_field_is_present_exactly_when_its_role_holds_one_linked_item(
    item_names: list[str], expected: int | None
) -> None:
    items = [
        item(OptionItemRole.REPLACED, index, name) for index, name in enumerate(item_names, start=1)
    ]
    linked, _findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[choice(1, "glow lance", items=items)],
        weapons=[weapon(4, "Storm maul")],
    )
    assert linked[0].replaces_weapon_line == expected


def test_two_or_more_items_on_a_role_carry_no_singular_field_either() -> None:
    linked, findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[
            choice(
                1,
                "storm maul and ceremonial rod",
                items=[
                    item(OptionItemRole.REPLACED, 1, "storm maul", weapon_line=4),
                    item(OptionItemRole.REPLACED, 2, "ceremonial rod", weapon_line=5),
                ],
            )
        ],
        weapons=[weapon(4, "Storm maul"), weapon(5, "Ceremonial rod")],
    )
    assert findings == []
    assert linked[0].replaces_weapon_line is None


def test_a_stale_stated_value_is_cleared_when_its_own_item_fails_to_link() -> None:
    # The case that tells "total function" apart from "fill the gap `link_choice_weapons` left":
    # a `stated` value that is present and does NOT contradict the items (its one item simply
    # failed to link, so `_bundle_disagreement` sees nothing to compare) is not a disagreement —
    # but under `link_choice_weapons` no longer writing this field at all (T023), a stale
    # `stated` value must never survive un-recomputed. The old "only fill an absent field"
    # reading would have left `5` in place; the derivation clears it, because the total function
    # of contract §4.1 is "exactly one linked item", not "whatever was already there".
    linked, findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[
            choice(
                1,
                "ceremonial rod",
                replaces_weapon_line=5,
                items=[item(OptionItemRole.REPLACED, 1, "ceremonial rod")],
            )
        ],
        weapons=[weapon(4, "Storm maul")],
    )
    assert [f.finding_code for f in findings] == ["OPT-BUNDLE-UNLINKED"]
    assert linked[0].replaces_weapon_line is None


def test_a_singular_field_its_items_contradict_is_blocking() -> None:
    linked, findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[
            choice(
                1,
                "sedge halberd",
                replaces_weapon_line=2,
                items=[
                    item(OptionItemRole.REPLACED, 1, "sedge halberd"),
                    item(OptionItemRole.REPLACED, 2, "mire censer"),
                ],
            )
        ],
        weapons=[weapon(2, "Sedge halberd"), weapon(3, "Mire censer")],
    )
    assert [f.finding_code for f in findings] == ["OPT-BUNDLE-DISAGREE"]
    assert CATALOGUE["OPT-BUNDLE-DISAGREE"].severity is Severity.BLOCKING
    assert linked[0].replaces_weapon_line == 2


def test_the_disagreement_is_checked_in_the_other_direction_too() -> None:
    # A singular field pointing at a line its one item does not name is the same contradiction
    # read from the other end, and a check that only looked one way would miss it.
    _linked, findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[
            choice(
                1,
                "sedge halberd",
                grants_weapon_line=9,
                items=[item(OptionItemRole.GRANTED, 1, "sedge halberd")],
            )
        ],
        weapons=[weapon(2, "Sedge halberd"), weapon(9, "Warding rod")],
    )
    assert [f.finding_code for f in findings] == ["OPT-BUNDLE-DISAGREE"]


def test_a_no_change_alternative_carries_no_items_and_raises_nothing() -> None:
    linked, findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[choice(3, NO_CHANGE_NAME, is_no_change=True)],
        weapons=[weapon(1, "Warding rod")],
    )
    assert findings == []
    assert linked[0].items == ()


def test_item_linking_is_deterministic() -> None:
    args = {
        "datasheet_id": DATASHEET,
        "choices": [
            choice(
                1,
                "mire censer and 1 sedge halberd",
                items=[
                    item(OptionItemRole.GRANTED, 1, "mire censer"),
                    item(OptionItemRole.GRANTED, 2, "sedge halberd"),
                ],
            )
        ],
        "weapons": [weapon(4, "Mire censer"), weapon(3, "Mire censer"), weapon(2, "Sedge halberd")],
    }
    first = link_choice_items(**args)  # type: ignore[arg-type]
    second = link_choice_items(**args)  # type: ignore[arg-type]
    assert first == second


# --- 008 US2: a Phase 4 production's bundle and replaced set link the same way (T045) -----------


def test_a_phase_4_bundle_and_replaced_set_link_by_the_same_exactly_one_match_rule() -> None:
    """`link_choice_items` does not know which production built the choice it is handed — a
    Phase 4 row's granted bundle and replaced set go through the identical exactly-one-match join
    as a `004`/`006` row's, and an item that fails to link still ships, named in the report,
    rather than dropped or guessed (FR-007).
    """
    parsed = parse_row(
        "Any number of Watch Sentinel models can each replace their signal flare and marker "
        "beacon with 1 ember coil and 1 pulse rod."
    )
    assert parsed is not None
    assert parsed.replaced_clause is not None
    (choice_parse,) = parsed.choices

    granted = split_conjuncts(choice_parse.name, choice_parse.count)
    replaced = split_replaced(parsed.replaced_clause)
    assert [i.name for i in granted] == ["ember coil", "pulse rod"]
    assert [i.name for i in replaced] == ["signal flare", "marker beacon"]

    linked, findings = link_choice_items(
        datasheet_id=DATASHEET,
        choices=[
            choice(
                1,
                choice_parse.name,
                count=choice_parse.count,
                items=[
                    item(OptionItemRole.GRANTED, 1, granted[0].name, count=granted[0].count),
                    item(OptionItemRole.GRANTED, 2, granted[1].name, count=granted[1].count),
                    item(OptionItemRole.REPLACED, 1, replaced[0].name),
                    item(OptionItemRole.REPLACED, 2, replaced[1].name),
                ],
            )
        ],
        weapons=[
            weapon(1, "Ember coil"),
            weapon(2, "Pulse rod"),
            weapon(3, "Signal flare"),
            # "Marker beacon" is deliberately absent from the weapon lines - the unlinkable item.
        ],
    )
    assert [i.weapon_line for i in linked[0].items] == [1, 2, 3, None]
    assert [f.finding_code for f in findings] == ["OPT-BUNDLE-UNLINKED"]
    assert findings[0].detail["match_count"] == 0
