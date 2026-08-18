# AI-Assisted: Claude Code (model: claude-opus-5) - The default-equipment grammar's contract (006
# task T025): research D1e's five subject productions plus the bare-model one, item-list splitting
# on `;` and on a bare `,`, the refusals that keep a compound subject out of a model name, and the
# none/extracted/partial/omitted state machine of data-model.md section 3.
"""What a default-equipment sentence resolves to, and what it deliberately does not.

Research D1e measured 1 932 equipment groups over 1 676 of 1 688 cached datacards. Five subject
productions cover ≈99.5 % of them; a sixth — the bare ``<MODEL> is equipped with:`` — takes the
residual to 9 in 1 942. Everything past that is the **compound and conditional** tail (``Every
<MODEL> with <ITEM> …``, ``One <MODEL> …``, ``If the unit has INT models, …``), and this module
asserts it is refused rather than resolved: every one of those subjects matches a built production
perfectly well and resolves to a *model name that is not a model*, which would attach a squad's
loadout to a model group nobody can find.

The state machine is the other half. ``none`` / ``extracted`` / ``partial`` are
:class:`pipeline.models.curated.WargearOptionState`'s three codes reused without variation, and the
fourth fact — *the source was not consulted, **or** this datasheet's composition did not resolve*
— is the value's **absence**. FR-016 is the second half of that sentence and it is asserted here
against ``_equipment`` itself, because a fixture whose composition fails is the only place the
rule is visible.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pytest

from pipeline.curate.assemble import _equipment
from pipeline.curate.authored import AuthoredContent
from pipeline.models.curated import (
    CuratedCompositionEntry,
    DefaultEquipmentState,
    EquipmentAppliesTo,
)
from pipeline.parse.equipment_grammar import (
    EQUIPMENT_TABLE,
    equipment_group_id,
    equipment_state,
    parse_sentence,
)
from pipeline.parse.wahapedia_csv import CsvReadResult, read_file, read_text
from pipeline.parse.wahapedia_html_dom import Datacard, parse_faction_page
from tests.enrichment.conftest import weapon

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "enrichment"
    / "wahapedia-html"
    / "glimmerfen-covenant.html"
)
SLUG = "glimmerfen-covenant"

EQUIPMENT_CSV = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "enrichment"
    / "wahapedia"
    / "Datasheets_unit_equipment.csv"
)


@pytest.fixture(scope="module")
def cards() -> Mapping[str, Datacard]:
    """The T004 quirk-class fixtures, by anchor, read through the extractor a run uses."""
    page = parse_faction_page(SLUG, FIXTURE.read_text(encoding="utf-8"))
    return {card.detail_id.rpartition(":")[2]: card for card in page.cards}


# --- the five measured subject productions, plus the bare one ----------------------------------


def test_every_model_is_a_whole_unit_subject() -> None:
    # 367 measured groups. The subject names no subset, so the sentence covers the unit and
    # carries no model name at all — which is the biconditional the curated model enforces.
    parsed = parse_sentence("Every model is equipped with: glimmer rifle; fen halberd.")
    assert parsed is not None
    assert parsed.applies_to is EquipmentAppliesTo.UNIT
    assert parsed.model_name is None


def test_this_model_is_a_whole_unit_subject() -> None:
    # 1 143 measured groups — the single largest shape in the corpus, and a unit of one model.
    parsed = parse_sentence("This model is equipped with: sentinel lance.")
    assert parsed is not None
    assert parsed.applies_to is EquipmentAppliesTo.UNIT
    assert parsed.model_name is None


@pytest.mark.parametrize(
    ("sentence", "model_name"),
    [
        ("Every Mirebound Chorister is equipped with: void net.", "Mirebound Chorister"),
        ("The Mirebound Cantor is equipped with: chime flail.", "Mirebound Cantor"),
        ("Each Mirebound Chorister is equipped with: void net.", "Mirebound Chorister"),
        # D1e's sixth production: the bare subject, which takes the residual from 25 to 9.
        ("Glimmerfen Warden is equipped with: glimmer lantern.", "Glimmerfen Warden"),
    ],
)
def test_a_named_subject_is_a_model_group_carrying_that_name(
    sentence: str, model_name: str
) -> None:
    parsed = parse_sentence(sentence)
    assert parsed is not None
    assert parsed.applies_to is EquipmentAppliesTo.MODEL_GROUP
    assert parsed.model_name == model_name


def test_every_model_is_matched_before_the_named_subject_production() -> None:
    # Ordering, asserted rather than assumed: `^Every (.+) is equipped with:` matches
    # `Every model …` perfectly well and would publish a model group named "model".
    parsed = parse_sentence("Every model is equipped with: snare net.")
    assert parsed is not None
    assert parsed.model_name is None


# --- the item list ----------------------------------------------------------------


def test_items_split_on_the_semicolon_the_source_uses() -> None:
    # 1 646 of 1 655 multi-item groups separate with `;`.
    parsed = parse_sentence("Every model is equipped with: glimmer rifle; fen halberd.")
    assert parsed is not None
    assert [item.item_name for item in parsed.items] == ["glimmer rifle", "fen halberd"]


def test_items_split_on_a_bare_comma_only_when_no_semicolon_is_present() -> None:
    # 9 measured groups. The comma is the fallback and never a second splitter: a list that
    # already separates with `;` may legitimately carry a comma inside one item's name.
    parsed = parse_sentence("Every model is equipped with: gloam pistol, gloam blade.")
    assert parsed is not None
    assert [item.item_name for item in parsed.items] == ["gloam pistol", "gloam blade"]

    mixed = parse_sentence("Every model is equipped with: gloam pistol, and shield; gloam blade.")
    assert mixed is not None
    assert [item.item_name for item in mixed.items] == ["gloam pistol, and shield", "gloam blade"]


def test_a_single_item_sentence_is_one_item_and_not_a_failure() -> None:
    # 259 measured groups state one item. `count` stays absent because the source states none —
    # absence means the source said nothing, and 1 would be this pipeline saying it instead.
    parsed = parse_sentence("Every model is equipped with: snare net.")
    assert parsed is not None
    assert [(item.item_name, item.count) for item in parsed.items] == [("snare net", None)]


def test_a_leading_integer_is_the_items_count_and_leaves_the_name() -> None:
    parsed = parse_sentence("This model is equipped with: 2 void nets; snare net.")
    assert parsed is not None
    assert [(item.item_name, item.count) for item in parsed.items] == [
        ("void nets", 2),
        ("snare net", None),
    ]


# --- the residual: refused, never resolved -------------------------------------------------------


@pytest.mark.parametrize(
    "sentence",
    [
        # The 104-group compound/conditional tail of D1e, one representative per shape. Each of
        # these matches a built production and would resolve to a model name that is not one.
        "Every Fenmire Skirmisher with a marsh carbine is equipped with: tanglelance.",
        "One Gloamtide Wretch is equipped with: gloam banner.",
        "2 Bracklight Outriders are equipped with: marsh carbine.",
        "A Thornlight Chorister is equipped with: chime flail.",
        "For every 5 models in the unit, 1 model is equipped with: resonance shard.",
        "If the unit has 10 models, 2 models are equipped with: void net.",
    ],
)
def test_a_compound_or_conditional_subject_is_refused(sentence: str) -> None:
    assert parse_sentence(sentence) is None


def test_a_sentence_with_no_equipped_with_marker_is_refused() -> None:
    assert parse_sentence("Every model in this unit is arrayed for war.") is None


def test_a_sentence_naming_no_item_at_all_is_refused() -> None:
    # A subject with an empty object names nothing to carry, and an empty item row would be a
    # loadout that says a model is equipped with the absence of a weapon.
    assert parse_sentence("Every model is equipped with:") is None


def test_a_subject_longer_than_a_name_is_refused() -> None:
    # The curated ceiling is 120 characters. A "name" past it has stopped being a name, and
    # emitting it would fail schema validation at write time instead of here, where the sentence
    # can still be reported as unresolved and handed to a curator.
    assert parse_sentence(f"The {'x' * 121} is equipped with: snare net.") is None


# --- identity ------------------------------------------------------------------------------------


def test_the_group_id_is_derived_from_the_sources_own_ordinal() -> None:
    # `eq-<datasheet-stem>-<line>`, the same identity discipline as `og-`: zero inference, so an
    # upstream relabelling is a rename rather than a removal plus an addition.
    assert equipment_group_id("ds-mirebound-choir", 2) == "eq-mirebound-choir-2"


# --- the state machine of data-model.md section 3 -------------------------------------------------


@pytest.mark.parametrize(
    ("sentences", "unparsed", "expected"),
    [
        (0, 0, DefaultEquipmentState.NONE),
        (2, 0, DefaultEquipmentState.EXTRACTED),
        (2, 1, DefaultEquipmentState.PARTIAL),
        (1, 1, DefaultEquipmentState.PARTIAL),
    ],
)
def test_the_three_stated_codes(
    sentences: int, unparsed: int, expected: DefaultEquipmentState
) -> None:
    assert equipment_state(sentence_count=sentences, unparsed_count=unparsed) is expected


COMPOSITION = (
    CuratedCompositionEntry(line=1, model_name="Snarebound Wretch", min_count=5, max_count=5),
)


def _detail(description: str) -> Mapping[str, CsvReadResult]:
    return {
        EQUIPMENT_TABLE: read_text(
            EQUIPMENT_TABLE, f"datasheet_id|line|description|\nGF11|1|{description}|\n"
        )
    }


def test_a_datasheet_whose_source_was_never_consulted_carries_no_state() -> None:
    # The fourth fact, expressed by absence: no equipment table in this mapping at all.
    outcome = _equipment("GF11", "ds-x", {}, AuthoredContent(), COMPOSITION, ())
    assert outcome.state is None
    assert outcome.groups == ()


def test_a_consulted_datasheet_with_no_sentence_is_none_and_not_absent() -> None:
    detail = {EQUIPMENT_TABLE: read_text(EQUIPMENT_TABLE, "datasheet_id|line|description|\n")}
    outcome = _equipment("GF11", "ds-x", detail, AuthoredContent(), COMPOSITION, ())
    assert outcome.state is DefaultEquipmentState.NONE


def test_a_resolved_sentence_is_extracted() -> None:
    outcome = _equipment(
        "GF11",
        "ds-x",
        _detail("Every model is equipped with: snare net."),
        AuthoredContent(),
        COMPOSITION,
        (),
    )
    assert outcome.state is DefaultEquipmentState.EXTRACTED
    assert len(outcome.groups) == 1


def test_an_unresolved_sentence_suppresses_only_itself() -> None:
    # The asymmetry with composition, and it is deliberate: a partial equipment list under-states
    # what a model carries, while a partial composition under-states how many models exist and
    # therefore mis-prices the unit. Only the second is worse than nothing.
    detail = {
        EQUIPMENT_TABLE: read_text(
            EQUIPMENT_TABLE,
            "datasheet_id|line|description|\n"
            "GF11|1|Every model is equipped with: snare net.|\n"
            "GF11|2|If the unit has 10 models, 2 models are equipped with: void net.|\n",
        )
    }
    outcome = _equipment("GF11", "ds-x", detail, AuthoredContent(), COMPOSITION, ())
    assert outcome.state is DefaultEquipmentState.PARTIAL
    assert [group.line for group in outcome.groups] == [1]
    assert "EQP-UNPARSED" in [finding.finding_code for finding in outcome.findings]


def test_a_datasheet_whose_composition_did_not_resolve_carries_no_equipment_at_all() -> None:
    # FR-016. `_composition_entries` publishes an empty composition for a datasheet one of whose
    # lines it could not resolve, and equipment must not attach to a structure that does not
    # exist — so the state is OMITTED, which is a different fact from `none`.
    outcome = _equipment(
        "GF11",
        "ds-x",
        _detail("Every model is equipped with: snare net."),
        AuthoredContent(),
        (),
        (),
    )
    assert outcome.state is None
    assert outcome.groups == ()


# --- the fixture's own sentences, end to end ------------------------------------------------------


def test_every_sentence_the_quirk_fixtures_state_resolves(cards: Mapping[str, Datacard]) -> None:
    """The T004 carriers, read out of the html fixture and through the grammar."""
    resolved = {
        anchor: [parse_sentence(sentence) for sentence in cards[anchor].equipment]
        for anchor in ("Purgeflight-Wardens", "Mirebound-Choir", "Gloamtide-Host")
    }
    assert all(parse is not None for parses in resolved.values() for parse in parses)

    (wardens,) = resolved["Purgeflight-Wardens"]
    assert wardens is not None
    assert wardens.applies_to is EquipmentAppliesTo.UNIT
    assert [item.item_name for item in wardens.items] == ["glimmer rifle", "fen halberd"]

    cantor, choristers = resolved["Mirebound-Choir"]
    assert cantor is not None and choristers is not None
    assert (cantor.applies_to, cantor.model_name) == (
        EquipmentAppliesTo.MODEL_GROUP,
        "Mirebound Cantor",
    )
    assert (choristers.applies_to, choristers.model_name) == (
        EquipmentAppliesTo.MODEL_GROUP,
        "Mirebound Chorister",
    )


def test_a_card_stating_no_sentence_yields_none(cards: Mapping[str, Datacard]) -> None:
    assert cards["Fenwatch-Sentinel"].equipment == ()


# --- 008 Phase 5 (US3): the multi-model-group differentiated-equipment shape ---------------------
#
# T051 measured (`reports/equipment-taxonomy/2026-08-15.md`'s dated addendum) that
# `_COMPLETION_SUBJECTS` has no reachable production to add: `_SUBJECTS`'s own bare-subject sixth
# entry already resolves every subject `_REFUSED` does not reject, and the six representative
# shapes above (`test_a_compound_or_conditional_subject_is_refused`, unmodified since 006) already
# prove the whole compound/conditional tail stays refused by design. These three tests therefore
# pass **today**, before this phase changes a line of `equipment_grammar.py` — the point, on the
# same "confirm passing, say why" terms `tasks.md` T056 states for its own no-op ratchet test, is
# to prove FR-008's differentiated-equipment shape already resolves per-sentence end to end
# (through `_equipment` and `link_equipment` together, not just `parse_sentence`), and that the
# 47-datasheet residual is entirely the O1 subset family plus the permanently refused tail.

GF24_COMPOSITION = (
    CuratedCompositionEntry(line=1, model_name="Watch Trooper", min_count=4, max_count=4),
    CuratedCompositionEntry(line=2, model_name="Watch Sergeant", min_count=1, max_count=1),
)


def _gf24_detail() -> Mapping[str, CsvReadResult]:
    return {EQUIPMENT_TABLE: read_file(EQUIPMENT_CSV)}


def test_the_multi_model_group_differentiated_shape_already_resolves_per_sentence() -> None:
    """US3 Independent Test, adapted to GF24 as it was actually built (008 task T009) rather than
    to `tasks.md` T048's pre-T014 aspirational wording. GF24 states differentiated default
    equipment for two model groups: row 1 (`The Watch Sergeant is equipped with: ...`) is a
    subject shape `_SUBJECTS` already resolves; row 2 (`One Watch Trooper is equipped with:
    ...`) is the O1 subset shape `_REFUSED` rejects. That pairing — not "both resolve" — is what
    `tasks.md` T009 itself named this fixture for.
    """
    outcome = _equipment(
        "GF24",
        "ds-gf24",
        _gf24_detail(),
        AuthoredContent(),
        GF24_COMPOSITION,
        (weapon(1, "signal lantern"), weapon(2, "ember blade"), weapon(3, "marsh blade")),
    )
    assert outcome.state is DefaultEquipmentState.PARTIAL

    (group,) = outcome.groups
    assert group.line == 1
    assert group.applies_to is EquipmentAppliesTo.MODEL_GROUP
    assert group.model_name == "Watch Sergeant"
    assert group.composition_line == 2
    assert [(item.item_name, item.weapon_line) for item in group.items] == [
        ("signal lantern", 1),
        ("ember blade", 2),
    ]

    assert [finding.finding_code for finding in outcome.findings] == ["EQP-UNPARSED"]
    (unparsed,) = outcome.findings
    assert unparsed.detail["line"] == 2


def test_an_equipment_qualified_subject_stays_refused_through_the_full_pipeline() -> None:
    """FR-006's rule wearing an equipment costume (US3 paired refusal, `tasks.md` T049). `GF25`'s
    equipment-qualified sentence (`Every Marsh Sentry with a lantern is equipped with: ...`) was
    named in the Setup-phase ledger at T010 but never actually landed in
    `Datasheets_unit_equipment.csv` until this task needed a full-pipeline (not just
    `parse_sentence`) case for it. The conditional-subject half of T049's pairing is already
    proven at the `_equipment` level by 006's own pre-008
    `test_an_unresolved_sentence_suppresses_only_itself` above — not duplicated here.
    """
    composition = (
        CuratedCompositionEntry(line=1, model_name="Marsh Sentry", min_count=3, max_count=3),
    )
    detail = {EQUIPMENT_TABLE: read_file(EQUIPMENT_CSV)}
    outcome = _equipment("GF25", "ds-gf25", detail, AuthoredContent(), composition, ())
    assert outcome.state is DefaultEquipmentState.PARTIAL
    assert outcome.groups == ()
    assert [finding.finding_code for finding in outcome.findings] == ["EQP-UNPARSED"]


def test_an_unlinkable_item_ships_unlinked_beside_a_still_refused_sibling_row() -> None:
    """US3 Acceptance Scenario 3, proven through `_equipment` end to end rather than only at
    `link_equipment`'s own pre-008 unit level (`test_equipment_link.py`'s
    `test_an_item_matching_no_weapon_row_ships_unlinked_beside_its_siblings` already covers that
    case in isolation). Weapon coverage for `ember blade` is deliberately omitted: the item still
    ships, unlinked, beside its linked sibling and beside row 2's still-refused sentence.
    """
    outcome = _equipment(
        "GF24",
        "ds-gf24",
        _gf24_detail(),
        AuthoredContent(),
        GF24_COMPOSITION,
        (weapon(1, "signal lantern"),),
    )
    (group,) = outcome.groups
    assert [(item.item_name, item.weapon_line) for item in group.items] == [
        ("signal lantern", 1),
        ("ember blade", None),
    ]
    assert group.composition_line == 2

    codes = sorted(finding.finding_code for finding in outcome.findings)
    assert codes == ["EQP-ITEM-UNLINKED", "EQP-UNPARSED"]
