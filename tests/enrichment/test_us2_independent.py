# AI-Assisted: Claude Code (model: claude-opus-5) - User Story 2's independent test (006 task
# T032): four candidates carrying the T004 quirk shapes, asserting the whole-unit sentence and the
# leader/squad-differentiated pair each resolve at the granularity the source states, every
# resolvable item linked, and a datasheet whose composition does not resolve carrying no equipment
# rows at all.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the second-assembly-path regression (006
# T048 triage): the same tables driven through `_detail_only_datasheet`, so an unpriced datasheet
# is proven to carry its loadout, both paths are proven to agree, and FR-016 is proven still to
# suppress on the path the fix touched.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R5: ported off the deleted html arm. The
# same invented sentences now arrive the way the only remaining arm delivers them -- as
# `Datasheets.csv`'s `loadout` column, split into equipment rows by `read_export_payloads` -- so
# every assertion below is unchanged while the tables it reads are the export's own shape.
"""User Story 2, end to end, over the shapes it exists to resolve.

The tests beside this one prove the pieces: the grammar's productions, the two joins. This one
proves the **story** -- a reader asking "what does this unit actually come with" gets an answer at
whatever granularity the source states it, from the same ``_equipment`` call, with nothing
attached to a model group the source did not name and nothing attached to a composition structure
that does not exist.

It runs through :func:`pipeline.acquire.detail_source.read_export_payloads` rather than handing
``_equipment`` a pre-built equipment table, because the derivation from the ``loadout`` column is
part of what has to hold: a test that started from an equipment table would prove the grammar and
the join twice over, and the row routing that feeds them not at all.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import pytest

from pipeline.acquire.detail_source import read_export_payloads
from pipeline.acquire.fixtures import FixturePayload
from pipeline.curate.assemble import (
    _composition_entries,
    _detail_datasheet_fields,
    _detail_only_datasheet,
    _equipment,
    _EquipmentOutcome,
)
from pipeline.curate.authored import AuthoredContent
from pipeline.curate.summaries import ability_name_index
from pipeline.models.curated import (
    CuratedDatasheet,
    CuratedEquipmentGroup,
    CuratedModelLine,
    CuratedWeaponLine,
    DefaultEquipmentState,
    EquipmentAppliesTo,
)
from pipeline.models.findings import Finding
from pipeline.models.provenance import DetailSource, EntityProvenance, PointsSource
from pipeline.models.source import SourceAcquisition, SourceKey
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.reconcile.identity import IdRegistry

#: The export's four tables for one invented faction, carrying exactly the quirk shapes 004's
#: T004 fixtures carried: a whole-unit sentence over a two-line composition (``GF01``), a
#: leader/squad-differentiated pair whose items include one printed twice and one not printed at
#: all (``GF02``), a card stating no sentence (``GF03``), a second whole-unit card (``GF04``), and
#: a card stating a perfectly resolvable sentence over a composition row that cannot resolve
#: (``GF05``). Every id, name, item and sentence here is invented.
_DATASHEETS = (
    "id|name|faction_id|source_id|role|damaged_w|legend|loadout|\n"
    "GF01|Purgeflight Wardens|glimmerfen-covenant|current||||"
    "<b>Every model</b> is equipped with: glimmer rifle; fen halberd.|\n"
    "GF02|Mirebound Choir|glimmerfen-covenant|current||||"
    "<b>The Mirebound Cantor</b> is equipped with: chime flail; tide hammer."
    "<b>Every Mirebound Chorister</b> is equipped with: resonance shard; void net.|\n"
    "GF03|Fenwatch Sentinel|glimmerfen-covenant|current|||||\n"
    "GF04|Gloamtide Host|glimmerfen-covenant|current||||"
    "<b>Every model</b> is equipped with: gloam pistol; gloam blade.|\n"
    "GF05|Snarebound Wretches|glimmerfen-covenant|current||||"
    "<b>Every model</b> is equipped with: snare net.|\n"
)

_MODELS = """\
datasheet_id|line|name|M|T|Sv|inv_sv|W|Ld|OC|base_size|
GF01|1|Purgeflight Adept|6"|3|3+||2|6+|1|(25mm)|
GF01|2|Purgeflight Warden|6"|3|3+||1|6+|1|(25mm)|
GF02|1|Mirebound Cantor|5"|3|4+||2|7+|1|(25mm)|
GF02|2|Mirebound Chorister|5"|3|4+||1|7+|1|(25mm)|
GF03|1|Fenwatch Sentinel|8"|6|3+||8|6+|2|(60mm)|
GF04|1|Gloamtide Herald|6"|3|4+||2|7+|1|(25mm)|
GF04|2|Gloamtide Wretch|6"|3|5+||1|7+|1|(25mm)|
GF05|1|Snarebound Wretch|6"|3|5+||1|8+|1|(25mm)|
"""

#: ``GF02`` prints `Tide hammer` twice -- once ranged, once melee -- and never prints `void net`.
#: Both are what `test_an_unresolvable_item_costs_its_link_and_nothing_else` rests on.
_WARGEAR = """\
datasheet_id|line|name|description|type|range|A|BS_WS|S|AP|D|
GF01|1|Glimmer rifle||Ranged|18"|2|4+|4|0|1|
GF01|2|Ember lance||Ranged|18"|2|4+|4|0|1|
GF01|3|Psilent coil||Ranged|18"|2|4+|4|0|1|
GF01|4|Tide hammer||Ranged|18"|2|4+|4|0|1|
GF01|5|Fen halberd||Melee|Melee|2|4+|4|-1|1|
GF01|6|Close combat weapon||Melee|Melee|2|4+|4|-1|1|
GF01|7|Tide hammer||Melee|Melee|2|4+|4|-1|1|
GF02|1|Chime flail||Ranged|18"|2|4+|4|0|1|
GF02|2|Tide hammer||Ranged|18"|2|4+|4|0|1|
GF02|3|Tide hammer||Melee|Melee|2|4+|4|-1|1|
GF02|4|Resonance shard||Melee|Melee|2|4+|4|-1|1|
GF03|1|Sentinel lance||Ranged|18"|2|4+|4|0|1|
GF04|1|Gloam pistol||Ranged|18"|2|4+|4|0|1|
GF04|2|Gloam blade||Melee|Melee|2|4+|4|-1|1|
GF05|1|Snare net||Ranged|18"|2|4+|4|0|1|
"""

#: ``GF05``'s single row is prose the composition grammar cannot resolve -- the FR-016 case.
_COMPOSITION = """\
datasheet_id|line|description|
GF01|1|1 Purgeflight Adept|
GF01|2|4-8 Purgeflight Warden|
GF02|1|1 Mirebound Cantor|
GF02|2|4-9 Mirebound Chorister|
GF03|1|1 Fenwatch Sentinel|
GF04|1|1 Gloamtide Herald|
GF04|2|5-10 Gloamtide Wretch|
GF05|1|Every model in this unit is arrayed for war.|
"""


#: The detail source's own prices, so the unpriced-assembly-path tests below have something
#: to build a datasheet FROM (`_detail_only_datasheet` reports and drops a never-priced one).
_MODEL_COSTS = """\
datasheet_id|line|description|cost|
GF01|1|5 models|90|
GF01|2|9 models|170|
GF02|1|5 models|75|
GF02|2|10 models|150|
GF03|1|1 model|110|
GF04|1|6 models|80|
GF04|2|11 models|155|
GF05|1|5 models|60|
"""


#: The tables this story does not exercise, present and empty so the assembly path reads the same
#: table set a run reads rather than a subset chosen to suit the test.
_EMPTY_TABLES = {
    "Datasheets_keywords.csv": "datasheet_id|keyword|model|is_faction_keyword|\n",
    "Datasheets_abilities.csv": "datasheet_id|line|ability_id|model|name|description|type|\n",
    "Datasheets_options.csv": "datasheet_id|line|button|description|\n",
    "Datasheets_leader.csv": "leader_id|attached_id|\n",
    "Abilities.csv": "id|name|legend|faction_id|description|\n",
    "Detachments.csv": "id|faction_id|name|legend|type|\n",
    "Detachment_abilities.csv": "id|detachment_id|name|legend|description|\n",
}


@pytest.fixture(scope="module")
def detail() -> Mapping[str, CsvReadResult]:
    """The invented export, read exactly as a run reads it -- equipment rows included, which is
    to say derived from the ``loadout`` column rather than supplied ready-made."""
    return read_export_payloads(
        [
            FixturePayload(name="Datasheets.csv", text=_DATASHEETS),
            FixturePayload(name="Datasheets_models.csv", text=_MODELS),
            FixturePayload(name="Datasheets_wargear.csv", text=_WARGEAR),
            FixturePayload(name="Datasheets_unit_composition.csv", text=_COMPOSITION),
            FixturePayload(name="Datasheets_models_cost.csv", text=_MODEL_COSTS),
            *(FixturePayload(name=name, text=header) for name, header in _EMPTY_TABLES.items()),
        ]
    )


def _outcome(detail: Mapping[str, CsvReadResult], detail_id: str, stem: str) -> _EquipmentOutcome:
    """One datasheet's equipment, built the way ``_datasheet_for`` builds it."""
    datasheet_id = f"ds-{stem}"
    fields, _ = _detail_datasheet_fields(detail_id, detail, frozenset(), ability_names={})
    models: Sequence[CuratedModelLine] = fields.get("models", ())  # type: ignore[assignment]
    weapons: Sequence[CuratedWeaponLine] = fields.get("weapons", ())  # type: ignore[assignment]
    composition, _ = _composition_entries(
        detail_id, datasheet_id, detail, AuthoredContent(), models
    )
    return _equipment(detail_id, datasheet_id, detail, AuthoredContent(), composition, weapons)


def _items(group: CuratedEquipmentGroup) -> list[tuple[str, int | None]]:
    return [(item.item_name, item.weapon_line) for item in group.items]


# --- the whole-unit sentence over a two-line composition ------------------------------------------


def test_a_whole_unit_sentence_attaches_to_the_unit_and_to_no_composition_row(
    detail: Mapping[str, CsvReadResult],
) -> None:
    # Research D1e's 195-card shape: two composition rows, one sentence. `appliesTo = unit` with
    # no `compositionLine` is exactly what the source says, and an ordinal pairing would instead
    # have given the whole unit's loadout to the Adept alone.
    outcome = _outcome(detail, "GF01", "purgeflight-wardens")
    (group,) = outcome.groups
    assert outcome.state is DefaultEquipmentState.EXTRACTED
    assert group.id == "eq-purgeflight-wardens-1"
    assert group.applies_to is EquipmentAppliesTo.UNIT
    assert group.model_name is None
    assert group.composition_line is None


def test_every_resolvable_item_of_that_sentence_carries_its_weapon_line(
    detail: Mapping[str, CsvReadResult],
) -> None:
    outcome = _outcome(detail, "GF01", "purgeflight-wardens")
    (group,) = outcome.groups
    assert _items(group) == [("glimmer rifle", 1), ("fen halberd", 5)]


# --- the differentiated leader/squad pair ------------------------------------------------------


def test_a_differentiated_card_resolves_one_group_per_model_group(
    detail: Mapping[str, CsvReadResult],
) -> None:
    # The datacard states two sentences, one per model group, and this is the granularity
    # question FR-012/FR-013 asks: the answer is whatever the source states, never a level up.
    outcome = _outcome(detail, "GF02", "mirebound-choir")
    cantor, choristers = outcome.groups
    assert outcome.state is DefaultEquipmentState.EXTRACTED
    assert (cantor.applies_to, cantor.model_name) == (
        EquipmentAppliesTo.MODEL_GROUP,
        "Mirebound Cantor",
    )
    assert (choristers.applies_to, choristers.model_name) == (
        EquipmentAppliesTo.MODEL_GROUP,
        "Mirebound Chorister",
    )


def test_each_group_links_to_the_composition_row_it_names(
    detail: Mapping[str, CsvReadResult],
) -> None:
    outcome = _outcome(detail, "GF02", "mirebound-choir")
    cantor, choristers = outcome.groups
    assert (cantor.line, cantor.composition_line) == (1, 1)
    assert (choristers.line, choristers.composition_line) == (2, 2)


def test_an_unresolvable_item_costs_its_link_and_nothing_else(
    detail: Mapping[str, CsvReadResult],
) -> None:
    # `Tide hammer` is printed twice on this card — once ranged, once melee — and `void net` not
    # at all. Both ship unlinked, both keep their siblings' links, and both groups still say what
    # the models carry.
    outcome = _outcome(detail, "GF02", "mirebound-choir")
    cantor, choristers = outcome.groups
    assert _items(cantor) == [("chime flail", 1), ("tide hammer", None)]
    assert _items(choristers) == [("resonance shard", 4), ("void net", None)]
    assert [finding.finding_code for finding in outcome.findings] == [
        "EQP-ITEM-UNLINKED",
        "EQP-ITEM-UNLINKED",
    ]


# --- the two absence classes ---------------------------------------------------------------------


def test_a_card_stating_no_sentence_is_none_rather_than_absent(
    detail: Mapping[str, CsvReadResult],
) -> None:
    outcome = _outcome(detail, "GF03", "fenwatch-sentinel")
    assert outcome.state is DefaultEquipmentState.NONE
    assert outcome.groups == ()
    assert outcome.findings == []


def test_a_card_whose_composition_does_not_resolve_carries_no_equipment_at_all(
    detail: Mapping[str, CsvReadResult],
) -> None:
    # FR-016, and the reason it is worth a rule of its own: this card DOES state a perfectly
    # resolvable equipment sentence, and the pipeline still publishes none of it. There is no
    # composition structure for it to attach to, and a loadout attached to models nobody can
    # enumerate is an assertion this repository will not make.
    detail_id = "GF05"
    assert any(row.fields["datasheet_id"] == detail_id for row in detail[EQUIPMENT_TABLE].rows), (
        "the fixture must still state a sentence, or this test proves nothing"
    )

    outcome = _outcome(detail, "GF05", "snarebound-wretches")
    assert outcome.state is None
    assert outcome.groups == ()
    assert outcome.findings == []


def test_the_whole_page_resolves_every_sentence_it_states(
    detail: Mapping[str, CsvReadResult],
) -> None:
    """No card of the fixture leaves a sentence in the residual — SC-005's shape, in miniature."""
    unparsed = [
        (detail_id, finding.finding_code)
        for detail_id, stem in (
            ("GF01", "purgeflight-wardens"),
            ("GF02", "mirebound-choir"),
            ("GF04", "gloamtide-host"),
            ("GF03", "fenwatch-sentinel"),
        )
        for finding in _outcome(detail, detail_id, stem).findings
        if finding.finding_code == "EQP-UNPARSED"
    ]
    assert unparsed == []


# --- both assembly paths, not only the matched one ---------------------------------------------


def _detail_only(
    detail: Mapping[str, CsvReadResult], detail_id: str, display_name: str
) -> tuple[CuratedDatasheet | None, list[Finding]]:
    """One datasheet down the **unpriced** assembly path, as `assemble()` drives it."""
    acquisition = SourceAcquisition(
        acquisition_id="wahapedia-fixture",
        source_key=SourceKey.WAHAPEDIA,
        source_base_url="https://example.invalid/fixture",
        declared_edition_code="wh40k-11e",
        retrieved_at="2026-08-11T00:00:00Z",
        content_fingerprint="0" * 64,
    )
    return _detail_only_datasheet(
        detail_id,
        display_name=display_name,
        faction_id="f-glimmerfen-covenant",
        detail=detail,
        authored=AuthoredContent(),
        edition_id="ed-wh40k-11e",
        provenance=EntityProvenance(
            points_source=PointsSource.NONE,
            points_edition_code="wh40k-11e",
            detail_source=DetailSource.WAHAPEDIA,
            detail_acquisition_id=acquisition.acquisition_id,
            detail_edition_code="wh40k-11e",
        ),
        registry=IdRegistry(),
        detail_acquisition=acquisition,
        legends_sources=frozenset(),
        # 010 R6: the ability-name index is a build-level value the caller passes in.
        ability_names=ability_name_index(detail),
    )


def test_a_datasheet_the_points_source_never_priced_still_carries_its_equipment(
    detail: Mapping[str, CsvReadResult],
) -> None:
    """The `wh40k-11e-2026-08-2` regression, stated as the rule it broke.

    Whether the points authority priced a datasheet is a fact about *pricing*. It says nothing
    about what the models carry, and it must not decide whether the loadout is published. The
    candidate carried 647 datasheets down this path with a composition, weapons and a
    `wargear_option_state` but **no** `default_equipment_state` at all — which a consumer reads
    as "the equipment source was never consulted" for cards the pipeline had read end to end,
    and which raised no finding because the extraction was never attempted.
    """
    datasheet, _ = _detail_only(detail, "GF01", "Purgeflight Wardens")
    assert datasheet is not None
    assert datasheet.default_equipment_state is DefaultEquipmentState.EXTRACTED
    (group,) = datasheet.equipment_groups
    assert group.applies_to is EquipmentAppliesTo.UNIT
    assert _items(group) == [("glimmer rifle", 1), ("fen halberd", 5)]


def test_both_assembly_paths_agree_about_one_card_s_equipment(
    detail: Mapping[str, CsvReadResult],
) -> None:
    """Priced or not, the same card yields the same loadout — the property that was asymmetric."""
    for detail_id, stem, display_name in (
        ("GF01", "purgeflight-wardens", "Purgeflight Wardens"),
        ("GF02", "mirebound-choir", "Mirebound Choir"),
        ("GF04", "gloamtide-host", "Gloamtide Host"),
    ):
        matched = _outcome(detail, detail_id, stem)
        datasheet, _ = _detail_only(detail, detail_id, display_name)
        assert datasheet is not None
        assert datasheet.default_equipment_state is matched.state
        assert [_items(group) for group in datasheet.equipment_groups] == [
            _items(group) for group in matched.groups
        ]


def test_fr_016_still_suppresses_equipment_on_the_unpriced_path_too(
    detail: Mapping[str, CsvReadResult],
) -> None:
    """The fix carries FR-016 with it rather than around it: no composition, no equipment."""
    datasheet, _ = _detail_only(detail, "GF05", "Snarebound Wretches")
    assert datasheet is not None
    assert list(datasheet.composition) == []
    assert datasheet.default_equipment_state is None
    assert list(datasheet.equipment_groups) == []
