# AI-Assisted: Claude Code (model: claude-opus-5) - User Story 2's independent test (006 task
# T032): four candidates built from the T004 quirk fixtures through the html extractor a run
# uses, asserting the whole-unit sentence and the leader/squad-differentiated pair each resolve at
# the granularity the source states, every resolvable item linked, and a datasheet whose
# composition does not resolve carrying no equipment rows at all.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the second-assembly-path regression (006
# T048 triage): the same fixture driven through `_detail_only_datasheet`, so an unpriced datasheet
# is proven to carry its loadout, both paths are proven to agree, and FR-016 is proven still to
# suppress on the path the fix touched.
"""User Story 2, end to end, over the fixtures that carry every shape it exists to resolve.

The tests beside this one prove the pieces: the grammar's productions, the two joins. This one
proves the **story** — a reader asking "what does this unit actually come with" gets an answer at
whatever granularity the datacard states it, from the same ``_equipment`` call, with nothing
attached to a model group the source did not name and nothing attached to a composition structure
that does not exist.

It runs through the **html extractor**, not through hand-written table text, because the sentence
is html-mode's alone: no export publishes it, and a test that fed the grammar a string would prove
the grammar twice and the extraction not at all.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

from pipeline.curate.assemble import (
    _composition_entries,
    _detail_datasheet_fields,
    _detail_only_datasheet,
    _equipment,
    _EquipmentOutcome,
)
from pipeline.curate.authored import AuthoredContent
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
from pipeline.parse.wahapedia_html_dom import emit_records, parse_faction_page
from pipeline.reconcile.identity import IdRegistry

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "enrichment"
    / "wahapedia-html"
    / "glimmerfen-covenant.html"
)
SLUG = "glimmerfen-covenant"


@pytest.fixture(scope="module")
def detail() -> Mapping[str, CsvReadResult]:
    """The fixture page as export-shaped tables, exactly as an ``html``-mode run reads it."""
    return emit_records([parse_faction_page(SLUG, FIXTURE.read_text(encoding="utf-8"))])


def _outcome(detail: Mapping[str, CsvReadResult], anchor: str, stem: str) -> _EquipmentOutcome:
    """One datasheet's equipment, built the way ``_datasheet_for`` builds it."""
    detail_id = f"{SLUG}:{anchor}"
    datasheet_id = f"ds-{stem}"
    fields, _ = _detail_datasheet_fields(detail_id, detail, frozenset())
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
    outcome = _outcome(detail, "Purgeflight-Wardens", "purgeflight-wardens")
    (group,) = outcome.groups
    assert outcome.state is DefaultEquipmentState.EXTRACTED
    assert group.id == "eq-purgeflight-wardens-1"
    assert group.applies_to is EquipmentAppliesTo.UNIT
    assert group.model_name is None
    assert group.composition_line is None


def test_every_resolvable_item_of_that_sentence_carries_its_weapon_line(
    detail: Mapping[str, CsvReadResult],
) -> None:
    outcome = _outcome(detail, "Purgeflight-Wardens", "purgeflight-wardens")
    (group,) = outcome.groups
    assert _items(group) == [("glimmer rifle", 1), ("fen halberd", 5)]


# --- the differentiated leader/squad pair ------------------------------------------------------


def test_a_differentiated_card_resolves_one_group_per_model_group(
    detail: Mapping[str, CsvReadResult],
) -> None:
    # The datacard states two sentences, one per model group, and this is the granularity
    # question FR-012/FR-013 asks: the answer is whatever the source states, never a level up.
    outcome = _outcome(detail, "Mirebound-Choir", "mirebound-choir")
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
    outcome = _outcome(detail, "Mirebound-Choir", "mirebound-choir")
    cantor, choristers = outcome.groups
    assert (cantor.line, cantor.composition_line) == (1, 1)
    assert (choristers.line, choristers.composition_line) == (2, 2)


def test_an_unresolvable_item_costs_its_link_and_nothing_else(
    detail: Mapping[str, CsvReadResult],
) -> None:
    # `Tide hammer` is printed twice on this card — once ranged, once melee — and `void net` not
    # at all. Both ship unlinked, both keep their siblings' links, and both groups still say what
    # the models carry.
    outcome = _outcome(detail, "Mirebound-Choir", "mirebound-choir")
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
    outcome = _outcome(detail, "Fenwatch-Sentinel", "fenwatch-sentinel")
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
    detail_id = f"{SLUG}:Snarebound-Wretches"
    assert any(row.fields["datasheet_id"] == detail_id for row in detail[EQUIPMENT_TABLE].rows), (
        "the fixture must still state a sentence, or this test proves nothing"
    )

    outcome = _outcome(detail, "Snarebound-Wretches", "snarebound-wretches")
    assert outcome.state is None
    assert outcome.groups == ()
    assert outcome.findings == []


def test_the_whole_page_resolves_every_sentence_it_states(
    detail: Mapping[str, CsvReadResult],
) -> None:
    """No card of the fixture leaves a sentence in the residual — SC-005's shape, in miniature."""
    unparsed = [
        (anchor, finding.finding_code)
        for anchor, stem in (
            ("Purgeflight-Wardens", "purgeflight-wardens"),
            ("Mirebound-Choir", "mirebound-choir"),
            ("Gloamtide-Host", "gloamtide-host"),
            ("Fenwatch-Sentinel", "fenwatch-sentinel"),
        )
        for finding in _outcome(detail, anchor, stem).findings
        if finding.finding_code == "EQP-UNPARSED"
    ]
    assert unparsed == []


# --- both assembly paths, not only the matched one ---------------------------------------------


def _detail_only(
    detail: Mapping[str, CsvReadResult], anchor: str, display_name: str
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
        f"{SLUG}:{anchor}",
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
    datasheet, _ = _detail_only(detail, "Purgeflight-Wardens", "Purgeflight Wardens")
    assert datasheet is not None
    assert datasheet.default_equipment_state is DefaultEquipmentState.EXTRACTED
    (group,) = datasheet.equipment_groups
    assert group.applies_to is EquipmentAppliesTo.UNIT
    assert _items(group) == [("glimmer rifle", 1), ("fen halberd", 5)]


def test_both_assembly_paths_agree_about_one_card_s_equipment(
    detail: Mapping[str, CsvReadResult],
) -> None:
    """Priced or not, the same card yields the same loadout — the property that was asymmetric."""
    for anchor, stem, display_name in (
        ("Purgeflight-Wardens", "purgeflight-wardens", "Purgeflight Wardens"),
        ("Mirebound-Choir", "mirebound-choir", "Mirebound Choir"),
        ("Gloamtide-Host", "gloamtide-host", "Gloamtide Host"),
    ):
        matched = _outcome(detail, anchor, stem)
        datasheet, _ = _detail_only(detail, anchor, display_name)
        assert datasheet is not None
        assert datasheet.default_equipment_state is matched.state
        assert [_items(group) for group in datasheet.equipment_groups] == [
            _items(group) for group in matched.groups
        ]


def test_fr_016_still_suppresses_equipment_on_the_unpriced_path_too(
    detail: Mapping[str, CsvReadResult],
) -> None:
    """The fix carries FR-016 with it rather than around it: no composition, no equipment."""
    datasheet, _ = _detail_only(detail, "Snarebound-Wretches", "Snarebound Wretches")
    assert datasheet is not None
    assert list(datasheet.composition) == []
    assert datasheet.default_equipment_state is None
    assert list(datasheet.equipment_groups) == []
