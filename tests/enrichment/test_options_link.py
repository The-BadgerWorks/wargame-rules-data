# AI-Assisted: Claude Code (model: claude-opus-5) - The choice-to-weapon join's contract (004
# task T023): exactly one normalised-name match links, zero or two-or-more report
# OPT-LINK-AMBIGUOUS and ship unlinked, and the clause verb decides which of the two link fields
# the match lands in (FR-011).
"""The join the source does not publish, and what it does when it cannot be made.

There is no foreign key from an option row to a wargear row, and the wargear rows have no stable
row key — up to 18 of them share a ``(datasheet_id, line, line_in_wargear, name)`` quadruple. So
the join is by normalised name, it succeeds for about four choices in five, and the interesting
behaviour is the fifth: it is **left unlinked and named in the report**, never attached to
whichever profile happened to sort first.
"""

from __future__ import annotations

from pipeline.models.curated import CuratedOptionChoice
from pipeline.models.findings import Severity
from pipeline.parse.options_grammar import NO_CHANGE_NAME, OptionVerb
from pipeline.reconcile.options_link import link_choice_weapons
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


def test_exactly_one_match_links_a_replacement_choice_to_the_weapon_it_replaces() -> None:
    linked, findings = link_choice_weapons(
        datasheet_id=DATASHEET,
        choices=[choice(1, "sedge halberd")],
        verbs={"oc-sedgeward-conclave-1-1": OptionVerb.REPLACE},
        weapons=[weapon(1, "Warding rod"), weapon(2, "Sedge halberd")],
    )
    assert findings == []
    assert linked[0].replaces_weapon_line == 2
    assert linked[0].grants_weapon_line is None


def test_exactly_one_match_links_an_additive_choice_to_the_weapon_it_grants() -> None:
    linked, findings = link_choice_weapons(
        datasheet_id=DATASHEET,
        choices=[choice(1, "chime flail")],
        verbs={"oc-sedgeward-conclave-1-1": OptionVerb.EQUIP},
        weapons=[weapon(1, "Chime flail")],
    )
    assert findings == []
    assert linked[0].grants_weapon_line == 1
    assert linked[0].replaces_weapon_line is None


def test_zero_matches_ships_unlinked_and_reports() -> None:
    linked, findings = link_choice_weapons(
        datasheet_id=DATASHEET,
        choices=[choice(1, "glimmer lantern")],
        verbs={},
        weapons=[weapon(1, "Warding rod")],
    )
    assert linked[0].grants_weapon_line is None
    assert linked[0].replaces_weapon_line is None
    assert [f.finding_code for f in findings] == ["OPT-LINK-AMBIGUOUS"]
    assert findings[0].detail["match_count"] == 0


def test_two_or_more_matches_ship_unlinked_and_report() -> None:
    # The export really does publish two rows under one name — a weapon with two profiles — and
    # picking either would silently attach the choice to the wrong one half the time.
    linked, findings = link_choice_weapons(
        datasheet_id=DATASHEET,
        choices=[choice(1, "mire censer")],
        verbs={"oc-sedgeward-conclave-1-1": OptionVerb.REPLACE},
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
        verbs={},
        weapons=[weapon(7, "Sedge halberd")],
    )
    assert findings == []
    assert linked[0].grants_weapon_line == 7


def test_a_no_change_alternative_names_no_weapon_and_raises_nothing() -> None:
    linked, findings = link_choice_weapons(
        datasheet_id=DATASHEET,
        choices=[choice(3, NO_CHANGE_NAME, is_no_change=True)],
        verbs={},
        weapons=[weapon(1, "Warding rod")],
    )
    assert findings == []
    assert linked[0].grants_weapon_line is None


def test_linking_is_deterministic() -> None:
    args = {
        "datasheet_id": DATASHEET,
        "choices": [choice(1, "mire censer"), choice(2, "sedge halberd")],
        "verbs": {"oc-sedgeward-conclave-1-1": OptionVerb.REPLACE},
        "weapons": [weapon(4, "Mire censer"), weapon(3, "Mire censer"), weapon(2, "Sedge halberd")],
    }
    first = link_choice_weapons(**args)  # type: ignore[arg-type]
    second = link_choice_weapons(**args)  # type: ignore[arg-type]
    assert first == second
