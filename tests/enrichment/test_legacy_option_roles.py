# AI-Assisted: Claude Code (model: claude-sonnet-5) - User Story 2's independent test (007 task
# T027): one candidate built from T005's GF12 fixture through `_option_structure`, asserting the
# sergeant-shape subject, the removed item, and the granted item resolve as three distinct
# structured facts, the legacy singular field matches contract §4.1's derivation table in every
# one of research D3.3's three transition cases, and `OPT-SCOPE-UNRESOLVED` fires on the one row
# whose subject names no model of its own datasheet.
"""User Story 2, end to end, over GF12 — the fixture built to carry every D3.3 outcome.

The tests beside this one prove the pieces: the grammar's new stem production
(``test_options_grammar.py``), the total-function derivation (``test_options_link.py``), and the
transition-class report (``test_option_regression.py``). This one proves the **story**: a reader
of GF12's own card sees the sergeant/power-fist shape resolve with the eligibility subject, the
removed item, and the granted item as three distinct facts — never the granted item alone,
mislabelled as the thing removed.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from pipeline.curate.assemble import _composition_entries, _option_structure
from pipeline.curate.authored import AuthoredContent
from pipeline.models.curated import (
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
    CuratedWeaponLine,
    OptionItemRole,
)
from pipeline.parse.wahapedia_csv import CsvReadResult, read_file
from pipeline.report.catalogue import CATALOGUE
from tests.enrichment.conftest import curated_models, weapon

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "wahapedia"
DETAIL_ID = "GF12"
DATASHEET = "ds-marshlight-vigil"

#: Deliberately covers "storm maul" and "glow lance" only. "Ceremonial rod" (row 2's given-up
#: item) is deliberately absent — that absence IS the D3.3 "stated but unlinked" case.
WEAPONS: Sequence[CuratedWeaponLine] = (
    weapon(1, "Storm maul"),
    weapon(2, "Glow lance"),
)


def _detail() -> Mapping[str, CsvReadResult]:
    return {
        "Datasheets_options.csv": read_file(FIXTURES / "Datasheets_options.csv"),
        "Datasheets_unit_composition.csv": read_file(FIXTURES / "Datasheets_unit_composition.csv"),
    }


def _outcome() -> tuple[
    Mapping[str, CuratedOptionGroup], Mapping[str, CuratedOptionChoice], list[str]
]:
    """GF12 built exactly as `_datasheet_for` builds it: composition first, options reading it."""
    detail = _detail()
    composition, _composition_findings = _composition_entries(
        DETAIL_ID, DATASHEET, detail, AuthoredContent(), curated_models("GF12")
    )
    outcome = _option_structure(
        DETAIL_ID, DATASHEET, detail, AuthoredContent(), WEAPONS, (), composition
    )
    groups = {group.id: group for group in outcome.groups}
    choices = {choice.id: choice for choice in outcome.choices}
    finding_codes = [finding.finding_code for finding in outcome.findings]
    return groups, choices, finding_codes


def _items(choice: CuratedOptionChoice, role: OptionItemRole) -> list[CuratedOptionChoiceItem]:
    return [item for item in choice.items if item.role is role]


# --- the sergeant/power-fist shape: subject, removed item, and granted item all distinct -------


def test_the_eligibility_subject_is_a_distinct_fact_from_either_item() -> None:
    # GF12|1 - `One Marshlight Warden's storm maul can be replaced with 1 glow lance.`
    groups, _choices, _findings = _outcome()
    group = groups["og-marshlight-vigil-1"]
    assert group.eligible_model_name == "Marshlight Warden"
    assert group.eligible_max_count == 1


def test_d3_3_case_1_the_given_up_item_resolves_and_links() -> None:
    _groups, choices, _findings = _outcome()
    choice = choices["oc-marshlight-vigil-1-1"]

    granted = _items(choice, OptionItemRole.GRANTED)
    replaced = _items(choice, OptionItemRole.REPLACED)
    assert [(i.item_name, i.weapon_line) for i in granted] == [("glow lance", 2)]
    assert [(i.item_name, i.weapon_line) for i in replaced] == [("storm maul", 1)]

    # Contract §4.1's derivation table: exactly one linked item on each role -> both singular
    # fields present, equal to that item's line. Never the granted item's own line under
    # `replaces_weapon_line` — that IS the inversion this feature corrects.
    assert choice.grants_weapon_line == 2
    assert choice.replaces_weapon_line == 1


def test_d3_3_case_2_the_given_up_item_is_stated_but_does_not_link_uniquely() -> None:
    # GF12|2 - `One Marshlight Warden's ceremonial rod can be replaced with 1 glow lance.` No
    # weapon row of GF12 is named "ceremonial rod" (WEAPONS above), so it ships unlinked.
    _groups, choices, findings = _outcome()
    choice = choices["oc-marshlight-vigil-2-1"]

    replaced = _items(choice, OptionItemRole.REPLACED)
    assert [(i.item_name, i.weapon_line) for i in replaced] == [("ceremonial rod", None)]

    # The derivation table's middle row: one item, unlinked -> the singular field is OMITTED,
    # never the granted item's line under a `replaces`-shaped name.
    assert choice.replaces_weapon_line is None
    assert choice.grants_weapon_line == 2
    assert "OPT-BUNDLE-UNLINKED" in findings


def test_d3_3_case_3_an_equip_only_row_states_no_given_up_item_at_all() -> None:
    # GF12|3 - `The Marshlight Warden can be equipped with 1 glow lance.` A plain additive
    # choice: no REPLACED role at all, on either side.
    _groups, choices, _findings = _outcome()
    choice = choices["oc-marshlight-vigil-3-1"]

    assert _items(choice, OptionItemRole.REPLACED) == []
    assert choice.replaces_weapon_line is None
    assert choice.grants_weapon_line == 2


def test_opt_scope_unresolved_fires_on_a_subject_naming_no_model() -> None:
    # GF12|4 - `One Marshguard Sentinel's storm maul can be replaced with 1 glow lance.` No
    # model row of GF12 is named "Marshguard Sentinel" (research D3.4's edge case) — `006`
    # catalogued the code and never wired it; `007` T025 gives it its producer.
    groups, _choices, findings = _outcome()
    group = groups["og-marshlight-vigil-4"]
    # Ships exactly as the source states it, unchecked — advisory, never a suppression.
    assert group.eligible_model_name == "Marshguard Sentinel"
    assert "OPT-SCOPE-UNRESOLVED" in findings
    assert CATALOGUE["OPT-SCOPE-UNRESOLVED"].severity.value == "advisory"


def test_no_object_clause_item_is_ever_labelled_replaced_once_replaced_clause_is_populated() -> (
    None
):
    # research D3's "single site that decides an object clause's side": every choice above whose
    # row captured a given-up item (rows 1, 2, 4) must carry its GRANTED item under `granted`,
    # never under `replaced` — the inversion, corrected at its source.
    _groups, choices, _findings = _outcome()
    for choice_id in (
        "oc-marshlight-vigil-1-1",
        "oc-marshlight-vigil-2-1",
        "oc-marshlight-vigil-4-1",
    ):
        granted_names = {i.item_name for i in _items(choices[choice_id], OptionItemRole.GRANTED)}
        assert "glow lance" in granted_names
        replaced_names = {i.item_name for i in _items(choices[choice_id], OptionItemRole.REPLACED)}
        assert "glow lance" not in replaced_names
