# AI-Assisted: Claude Code (model: claude-sonnet-5) - User Story 3's tests for the item-constraint
# production (007 task T037): GF12 rows 5-10 through `_option_structure`, exercising a linked
# `not_replaceable` restriction, a model-scoped linked `not_replaceable` restriction, a linked
# `one_per_unit` restriction, an unlinkable restriction, a restriction-shaped row matching no
# vocabulary member, and the marker strip on an ordinary (non-restriction) choice's own name.
"""User Story 3: a footnote-style restriction becomes a structured `CuratedItemConstraint` row.

research D4.2 found that a footnote-style restriction reaches the pipeline as an option row
`parse_row` cannot resolve — not a second arrival path inside the composition or equipment block
— and is dropped on the floor today. `parse_constraint_row`/`is_constraint_shaped`
(`pipeline/parse/options_grammar.py`, T039) and `_item_constraint`
(`pipeline/curate/assemble.py`, T040) give it a producer: a closed two-member vocabulary
(`not_replaceable`, `one_per_unit`) tried only after `parse_row` has already refused the row, so
no row that resolves as an option today can reach it (rule 3/4 of this feature's own rules).

GF12 rows 5-10 (`fixtures/enrichment/wahapedia/Datasheets_options.csv`, T006) carry every shape:

* row 5 `The Marshlight Sentry can be equipped with 1 marsh axe*.` — an ORDINARY equip choice
  whose granted item name carries a trailing footnote marker (T038's strip, not a constraint).
* row 6 `The marsh axe cannot be replaced.` — `not_replaceable`, unscoped, linked.
* row 7 `The Marshlight Warden's storm maul cannot be replaced.` — `not_replaceable`, scoped to
  the model "Marshlight Warden", linked.
* row 8 `Only one glow lance can be taken per unit.` — `one_per_unit`, linked.
* row 9 `Only one ceremonial standard can be taken per unit.` — `one_per_unit`, deliberately
  unlinkable: no weapon row below is named "ceremonial standard".
* row 10 `The Marshlight Sentry's glow lance may only be fired while stationary.` —
  restriction-shaped (`is_constraint_shaped` — it contains "may only") but matches neither
  vocabulary member — `CST-UNPARSED`, no row, never a nearest-member guess.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from pipeline.curate.assemble import _composition_entries, _option_structure
from pipeline.curate.authored import AuthoredContent
from pipeline.models.curated import CuratedItemConstraint, CuratedWeaponLine, ItemConstraintType
from pipeline.parse.wahapedia_csv import CsvReadResult, read_file
from tests.enrichment.conftest import curated_models, weapon

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "wahapedia"
DETAIL_ID = "GF12"
DATASHEET = "ds-marshlight-vigil"

#: `test_legacy_option_roles.py`'s WEAPONS, extended with "Marsh axe" — GF12|6/7's linking
#: targets. "Ceremonial standard" (row 9's item) is deliberately absent, exactly as
#: "ceremonial rod" (row 2's given-up item) is: that absence IS the unlinkable case.
WEAPONS: Sequence[CuratedWeaponLine] = (
    weapon(1, "Storm maul"),
    weapon(2, "Glow lance"),
    weapon(3, "Marsh axe"),
)


def _detail() -> Mapping[str, CsvReadResult]:
    return {
        "Datasheets_options.csv": read_file(FIXTURES / "Datasheets_options.csv"),
        "Datasheets_unit_composition.csv": read_file(FIXTURES / "Datasheets_unit_composition.csv"),
    }


def _build():  # type: ignore[no-untyped-def]
    """GF12 built exactly as `_datasheet_for` builds it: composition first, options reading it."""
    detail = _detail()
    composition, _composition_findings = _composition_entries(
        DETAIL_ID, DATASHEET, detail, AuthoredContent(), curated_models("GF12")
    )
    return _option_structure(
        DETAIL_ID, DATASHEET, detail, AuthoredContent(), WEAPONS, (), composition
    )


def _outcome() -> tuple[Mapping[int, CuratedItemConstraint], list[str]]:
    outcome = _build()
    constraints = {c.constraint_index: c for c in outcome.item_constraints}
    finding_codes = [f.finding_code for f in outcome.findings]
    return constraints, finding_codes


# --- the marker strip on an ordinary choice, not a constraint (T038, guarantee 21) --------------


def test_an_ordinary_choices_own_name_is_never_left_carrying_a_marker() -> None:
    # GF12|5 - `The Marshlight Sentry can be equipped with 1 marsh axe*.` This row is NOT a
    # restriction: it is a plain EQUIP choice whose granted item's own name happens to carry the
    # marker. The marker is stripped at extraction; no CuratedItemConstraint is produced for it.
    outcome = _build()
    choice = next(c for c in outcome.choices if c.group_id == "og-marshlight-vigil-5")
    assert choice.name == "marsh axe"
    assert "*" not in choice.name
    constraints, _findings = _outcome()
    assert 5 not in constraints


# --- the constraint vocabulary itself (T037, T039, T040) -----------------------------------------


def test_a_not_replaceable_restriction_resolves_linked() -> None:
    # GF12|6 - `The marsh axe cannot be replaced.`
    constraints, _findings = _outcome()
    constraint = constraints[6]
    assert constraint.constraint_type is ItemConstraintType.NOT_REPLACEABLE
    assert constraint.item_name == "marsh axe"
    assert constraint.weapon_line == 3
    assert constraint.model_name is None


def test_a_not_replaceable_restriction_scoped_to_a_named_model_group_resolves_linked() -> None:
    # GF12|7 - `The Marshlight Warden's storm maul cannot be replaced.`
    constraints, _findings = _outcome()
    constraint = constraints[7]
    assert constraint.constraint_type is ItemConstraintType.NOT_REPLACEABLE
    assert constraint.item_name == "storm maul"
    assert constraint.weapon_line == 1
    assert constraint.model_name == "Marshlight Warden"


def test_a_one_per_unit_restriction_resolves_linked() -> None:
    # GF12|8 - `Only one glow lance can be taken per unit.`
    constraints, _findings = _outcome()
    constraint = constraints[8]
    assert constraint.constraint_type is ItemConstraintType.ONE_PER_UNIT
    assert constraint.item_name == "glow lance"
    assert constraint.weapon_line == 2
    assert constraint.model_name is None


def test_an_unlinkable_restriction_ships_with_weapon_line_omitted_never_guessed() -> None:
    # GF12|9 - `Only one ceremonial standard can be taken per unit.` No weapon row above is named
    # "ceremonial standard".
    constraints, findings = _outcome()
    constraint = constraints[9]
    assert constraint.constraint_type is ItemConstraintType.ONE_PER_UNIT
    assert constraint.item_name == "ceremonial standard"
    assert constraint.weapon_line is None
    assert "CST-UNLINKED" in findings


def test_a_restriction_shaped_row_matching_no_vocabulary_member_produces_no_row() -> None:
    # GF12|10 - `The Marshlight Sentry's glow lance may only be fired while stationary.`
    constraints, findings = _outcome()
    assert 10 not in constraints
    assert "CST-UNPARSED" in findings
    # Never double-reported: the row's fate is fully described by CST-UNPARSED, not also
    # OPT-UNPARSED (research D4.2, one code per row's actual fate).
    assert findings.count("OPT-UNPARSED") == 0 or "CST-UNPARSED" in findings


def test_constraint_index_is_each_rows_own_source_ordinal() -> None:
    constraints, _findings = _outcome()
    assert set(constraints) == {6, 7, 8, 9}


def test_no_row_that_resolves_as_an_option_is_ever_reinterpreted_as_a_constraint() -> None:
    """Rule 3/4: the constraint vocabulary is tried only after `parse_row` has already refused a
    row. GF12's own options (rows 1-5, 11) all resolve as options and none of them is also
    counted as a constraint."""
    outcome = _build()
    resolved_lines = {5, *range(1, 5)}
    constraints, _findings = _outcome()
    assert resolved_lines.isdisjoint(constraints)
    assert len(outcome.choices) >= 5
