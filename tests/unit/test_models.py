# AI-Assisted: Claude Code (model: claude-opus-5) - Exercises the typed spine (tasks T020-T025):
# the prose-bearing source fields are declared, nothing downstream is typed to hold prose,
# is_hybrid_edition is derived rather than stored, and absent optionals stay absent.
"""The typed spine, and the two invariants it exists to make structural."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from pipeline.models.authored import BLOCKING_REVIEW_STATES, AbilitySummary, ReviewState
from pipeline.models.curated import (
    RESTRICTION_VOCABULARY,
    CuratedDatasheet,
    CuratedDatasheetCost,
)
from pipeline.models.mechanical import is_mechanical_string, mechanical_violations
from pipeline.models.normalized import AbilityType, NormalizedDatasheet, ParseConfidence
from pipeline.models.provenance import (
    DetailSource,
    EntityProvenance,
    PointsSource,
    PricingConfidence,
    PricingConfidenceState,
)
from pipeline.models.source import PROSE_BEARING_FIELDS, SourceAcquisition, SourceKey

SAME_EDITION = EntityProvenance(
    points_source=PointsSource.MFM,
    points_edition_code="wh40k-11e",
    detail_source=DetailSource.WAHAPEDIA,
    detail_edition_code="wh40k-11e",
)

HYBRID = EntityProvenance(
    points_source=PointsSource.MFM,
    points_edition_code="wh40k-11e",
    detail_source=DetailSource.WAHAPEDIA,
    detail_edition_code="wh40k-10e",
)


def test_only_the_detail_source_record_declares_prose_bearing_fields() -> None:
    assert PROSE_BEARING_FIELDS["WahapediaRow"] == {
        "legend",
        "description",
        "loadout",
        "damaged_description",
        "inv_sv_descr",
    }
    assert PROSE_BEARING_FIELDS["MfmUnitCostBlock"] == frozenset()


def test_normalized_records_reject_unknown_fields() -> None:
    # extra="forbid" is control 1 of research D8: a prose field cannot be smuggled in as an
    # undeclared extra.
    with pytest.raises(ValidationError):
        NormalizedDatasheet(
            wahapedia_datasheet_id="WHP-1",
            display_name="Storm Riders",
            faction_id="IW",
            description="<p>lore</p>",  # type: ignore[call-arg]
        )


def test_a_source_acquisition_defaults_to_ok_with_no_requests() -> None:
    acquisition = SourceAcquisition(
        acquisition_id="mfm-20260802T090000Z-abc12345",
        source_key=SourceKey.MFM,
        source_base_url="https://points.example",
        declared_edition_code="wh40k-11e",
        retrieved_at="2026-08-02T09:00:00Z",
        content_fingerprint="sha256:0",
    )
    assert acquisition.outcome.value == "ok"
    assert acquisition.request_count == 0


def test_is_hybrid_edition_is_derived_not_stored() -> None:
    assert HYBRID.is_hybrid_edition is True
    assert SAME_EDITION.is_hybrid_edition is False
    assert "is_hybrid_edition" not in EntityProvenance.model_fields


def test_a_same_edition_entity_omits_detail_edition_code() -> None:
    # curated-snapshot-format.md §5: a same-edition datasheet omits the field rather than
    # repeating the snapshot's own edition.
    assert SAME_EDITION.emitted_detail_edition_code is None
    assert HYBRID.emitted_detail_edition_code == "wh40k-10e"


def test_unpriced_is_the_only_blocking_pricing_state() -> None:
    for state in PricingConfidenceState:
        confidence = PricingConfidence(state=state)
        assert confidence.is_blocking is (state is PricingConfidenceState.UNPRICED)


def test_a_cost_row_defaults_to_the_first_copy_tier_and_verified_pricing() -> None:
    cost = CuratedDatasheetCost(model_count=5, points=90, label="5 models")
    assert cost.copy_index_min == 1
    assert cost.pricing_confidence is PricingConfidenceState.VERIFIED


def test_copy_index_min_is_one_based() -> None:
    with pytest.raises(ValidationError):
        CuratedDatasheetCost(model_count=5, copy_index_min=0, points=90, label="5 models")


def test_an_uncurated_optional_is_absent_rather_than_guessed() -> None:
    datasheet = CuratedDatasheet(
        datasheet_id="ds-storm-riders",
        edition_id="ed-wh40k-11e",
        faction_id="f-iron-wardens",
        name="Storm Riders",
        costs=[CuratedDatasheetCost(model_count=5, points=90, label="5 models")],
        pricing_confidence=PricingConfidence(state=PricingConfidenceState.VERIFIED),
        provenance=SAME_EDITION,
    )
    assert datasheet.max_copies_per_army is None, "never guessed as 1 (FR-019)"
    assert "max_copies_per_army" not in datasheet.model_dump(exclude_none=True)


def test_the_restriction_vocabulary_is_the_contracts_nine_types() -> None:
    assert len(RESTRICTION_VOCABULARY) == 9
    assert "unique_epic_heroes" in RESTRICTION_VOCABULARY
    assert "force_disposition" not in RESTRICTION_VOCABULARY


def test_every_review_state_but_approved_blocks_publication() -> None:
    assert {
        ReviewState.DRAFT,
        ReviewState.IN_REVIEW,
        ReviewState.NEEDS_REREVIEW,
    } == BLOCKING_REVIEW_STATES
    assert ReviewState.APPROVED.blocks_publication is False


def test_a_new_summary_starts_as_draft_which_blocks() -> None:
    summary = AbilitySummary(
        ability_key="core:deep-strike",
        name="Deep Strike",
        summary="Set up in reserve; arrive later, away from enemy units.",
        mechanic_digest="hmac:0123456789abcdef",
    )
    assert summary.review_state is ReviewState.DRAFT
    assert summary.review_state.blocks_publication


def test_the_ability_type_vocabulary_is_closed() -> None:
    assert {t.value for t in AbilityType} == {"core", "faction", "datasheet"}
    assert {c.value for c in ParseConfidence} == {"exact", "range", "unparsed"}


@pytest.mark.parametrize(
    ("value", "reason"),
    [
        ('<span class="kwb">Bolter</span>', "markup"),
        ("Land&nbsp;Raider", "html_entity"),
        ("$RS_TOKEN", "placeholder_token"),
        ("Без заголовка", "cyrillic"),
        ("x" * 500, "over_length"),
    ],
)
def test_the_mechanical_guard_names_every_observed_quirk_class(value: str, reason: str) -> None:
    assert reason in mechanical_violations(value)
    assert not is_mechanical_string(value)


def test_ordinary_names_and_labels_pass_the_mechanical_guard() -> None:
    for value in ("Storm Riders", "5 models", "YOUR 3RD + UNIT COSTS", "T’au Empire", "ds-a-1"):
        assert is_mechanical_string(value), value
