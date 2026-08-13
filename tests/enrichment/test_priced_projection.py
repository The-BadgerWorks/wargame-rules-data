# AI-Assisted: Claude Code (model: claude-opus-5) - Guarantee 8's contract (004 task T024): a
# priced option adopted by exactly one choice, an unmatched priced row that still ships,
# a blocking disagreement on cost or count, and the byte-identical priced projection across the
# enrichment boundary (FR-012..FR-014, SC-004).
"""The priced projection, and why it is preserved by *not touching it*.

``datasheet_wargear_option`` keeps its fields, its producer (``curate/assemble.py::_costs``) and
its id scheme. The full option set links **to** it. That direction is the whole design: re-deriving
the priced rows from the detail source would change existing rows' meaning and breach FR-031
outright, whereas linking means an unchanged datasheet emits the identical priced rows by
construction rather than by a test that happens to pass — which is what the last test here
demonstrates.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from pipeline.build.bundle_emit import emit_bundle
from pipeline.build.canonical_json import dumps_bundle
from pipeline.models.curated import (
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
    CuratedWargearOption,
    OptionItemRole,
    OptionScope,
    WargearOptionState,
)
from pipeline.models.findings import Severity
from pipeline.parse.options_grammar import MAX_CHOICE_NAME_CHARS, NO_CHANGE_NAME, parse_row
from pipeline.reconcile.options_link import project_priced_options
from pipeline.report.catalogue import CATALOGUE
from tests import factories

DATASHEET = "ds-glimmerfen-warden"
GROUP = "og-glimmerfen-warden-1"


def choice(index: int, name: str, **overrides: object) -> CuratedOptionChoice:
    return CuratedOptionChoice(
        id=f"oc-glimmerfen-warden-1-{index}",
        group_id=GROUP,
        name=name,
        **overrides,  # type: ignore[arg-type]
    )


def priced(name: str, points: int, *, max_per_unit: int | None = None) -> CuratedWargearOption:
    slug = name.casefold().replace(" ", "-")
    return CuratedWargearOption(
        id=f"wo-glimmerfen-warden-{slug}",
        group_key=slug,
        name=name,
        points_delta=points,
        max_per_unit=max_per_unit,
    )


def test_a_priced_option_matching_exactly_one_choice_prices_that_choice() -> None:
    projected, findings = project_priced_options(
        datasheet_id=DATASHEET,
        choices=[choice(1, "glimmer lantern", count=1)],
        priced=[priced("Glimmer lantern", 10, max_per_unit=1)],
    )
    assert findings == []
    assert projected[0].points_delta == 10
    assert projected[0].priced_option_id == "wo-glimmerfen-warden-glimmer-lantern"


def test_an_unpriced_choice_carries_no_delta_at_all_rather_than_a_zero() -> None:
    # FR-013 and guarantee 10 in one assertion: a consumer must read "uncosted", never "free".
    projected, findings = project_priced_options(
        datasheet_id=DATASHEET,
        choices=[choice(1, "marsh carbine")],
        priced=[],
    )
    assert findings == []
    assert projected[0].points_delta is None
    assert projected[0].priced_option_id is None
    assert "points_delta" not in projected[0].model_dump(exclude_none=True)


def test_a_priced_option_matching_no_choice_still_ships_and_reports() -> None:
    projected, findings = project_priced_options(
        datasheet_id=DATASHEET,
        choices=[choice(1, "glimmer lantern")],
        priced=[priced("Glimmer lantern", 10), priced("Fen banner", 15)],
    )
    assert projected[0].priced_option_id == "wo-glimmerfen-warden-glimmer-lantern"
    assert [f.finding_code for f in findings] == ["OPT-PRICED-UNMATCHED"]
    assert findings[0].detail["priced_option_id"] == "wo-glimmerfen-warden-fen-banner"
    # Advisory: the priced row prices correctly whatever the parse tail does, so blocking would
    # stall a release over a navigational gap.
    assert CATALOGUE["OPT-PRICED-UNMATCHED"].severity is Severity.ADVISORY


def test_a_priced_option_matching_several_choices_links_none_of_them() -> None:
    # Guarantee 8 allows at most one choice per priced row. Picking one of two would be exactly
    # the guess the whole join refuses to make.
    projected, findings = project_priced_options(
        datasheet_id=DATASHEET,
        choices=[choice(1, "glimmer lantern"), choice(2, "Glimmer Lantern")],
        priced=[priced("Glimmer lantern", 10)],
    )
    assert all(item.priced_option_id is None for item in projected)
    assert findings[0].finding_code == "OPT-PRICED-UNMATCHED"
    assert findings[0].detail["match_count"] == 2


def test_a_disagreement_about_count_is_blocking() -> None:
    projected, findings = project_priced_options(
        datasheet_id=DATASHEET,
        choices=[choice(1, "tanglelance", count=1)],
        priced=[priced("Tanglelance", 20, max_per_unit=2)],
    )
    assert projected[0].points_delta is None
    (finding,) = [f for f in findings if f.finding_code == "OPT-PROJECTION-DISAGREE"]
    assert finding.severity is Severity.BLOCKING
    assert (finding.detail["priced_count"], finding.detail["choice_count"]) == (2, 1)


def test_a_disagreement_about_cost_is_blocking() -> None:
    # Two priced rows whose names normalise together but whose ids — and prices — differ. There
    # is no single delta to adopt, and adopting either would publish a price nobody published.
    dearer = priced("Glimmer lantern", 10)
    cheaper = CuratedWargearOption(
        id="wo-glimmerfen-warden-glimmer-lantern-alt",
        group_key="glimmer-lantern-alt",
        name="Glimmer  lantern",
        points_delta=5,
    )
    projected, findings = project_priced_options(
        datasheet_id=DATASHEET, choices=[choice(1, "glimmer lantern")], priced=[dearer, cheaper]
    )
    assert projected[0].points_delta is None
    assert any(f.finding_code == "OPT-PROJECTION-DISAGREE" for f in findings)
    assert CATALOGUE["OPT-PROJECTION-DISAGREE"].severity is Severity.BLOCKING


def test_a_no_change_alternative_is_never_a_candidate_for_a_price() -> None:
    projected, findings = project_priced_options(
        datasheet_id=DATASHEET,
        choices=[choice(1, NO_CHANGE_NAME, is_no_change=True)],
        priced=[priced("No change", 0)],
    )
    assert projected[0].points_delta is None
    assert [f.finding_code for f in findings] == ["OPT-PRICED-UNMATCHED"]


@pytest.mark.parametrize("repeat", [1, 2])
def test_projection_is_deterministic(repeat: int) -> None:
    del repeat
    args = {
        "datasheet_id": DATASHEET,
        "choices": [choice(2, "fen charm"), choice(1, "glimmer lantern")],
        "priced": [priced("Glimmer lantern", 10), priced("Fen banner", 15)],
    }
    assert project_priced_options(**args) == project_priced_options(**args)  # type: ignore[arg-type]


def test_the_priced_rows_are_byte_identical_across_the_enrichment_boundary() -> None:
    """SC-004, structurally: enrichment adds arrays, it does not touch the priced projection."""
    options = [priced("Glimmer lantern", 10, max_per_unit=1)]
    before = factories.datasheet(datasheet_id=DATASHEET).model_copy(
        update={"wargear_options": options}
    )
    after = before.model_copy(
        update={
            "option_groups": [
                CuratedOptionGroup(id=GROUP, line=1, scope=OptionScope.MODEL),
            ],
            "option_choices": [
                choice(
                    1,
                    "glimmer lantern",
                    count=1,
                    points_delta=10,
                    priced_option_id=options[0].id,
                ),
                choice(2, "fen charm"),
            ],
            "wargear_option_state": WargearOptionState.EXTRACTED,
        }
    )

    meta = factories.meta()
    plain = emit_bundle(factories.snapshot(datasheets=[before]), meta)
    enriched = emit_bundle(factories.snapshot(datasheets=[after]), meta)

    assert dumps_bundle(enriched["datasheetWargearOptions"]) == dumps_bundle(
        plain["datasheetWargearOptions"]
    )
    # ...and the enrichment really did land, so the assertion above is not vacuous.
    assert enriched["datasheetOptionChoices"]


# --- 006 US1: the bundle choice's price (T015) -------------------------------------------------
#
# A bundle choice is priced by the same rule a single-item one is, because it goes through the
# same function unchanged. These cases exist to state that as a contract rather than to exercise
# new code: the trichotomy below is what a consumer renders, and it has to stay total.


def bundle(index: int, name: str, items: int, **overrides: object) -> CuratedOptionChoice:
    """A choice whose joined name prices as a whole and whose items decompose it."""
    return CuratedOptionChoice(
        id=f"oc-glimmerfen-warden-1-{index}",
        group_id=GROUP,
        name=name,
        items=[
            CuratedOptionChoiceItem(
                role=OptionItemRole.GRANTED, item_index=i, item_name=f"part {i}"
            )
            for i in range(1, items + 1)
        ],
        **overrides,  # type: ignore[arg-type]
    )


def test_a_bundles_joined_name_adopts_exactly_the_delta_the_points_source_states() -> None:
    projected, findings = project_priced_options(
        datasheet_id=DATASHEET,
        choices=[bundle(1, "ember lance and close combat weapon", 2)],
        priced=[priced("Ember lance and close combat weapon", 15)],
    )
    assert findings == []
    assert projected[0].points_delta == 15
    assert (
        projected[0].priced_option_id == "wo-glimmerfen-warden-ember-lance-and-close-combat-weapon"
    )


def test_a_bundle_priced_at_a_genuine_zero_carries_that_zero() -> None:
    # "explicitly free" and "uncosted" are different facts and stay distinguishable with no new
    # field: `points_delta` present and 0, versus absent (guarantee 13).
    projected, _findings = project_priced_options(
        datasheet_id=DATASHEET,
        choices=[bundle(1, "ember lance and void net", 2)],
        priced=[priced("Ember lance and void net", 0)],
    )
    assert projected[0].points_delta == 0
    assert projected[0].priced_option_id is not None


def test_an_unpriced_bundle_carries_no_delta_field_at_all() -> None:
    projected, _findings = project_priced_options(
        datasheet_id=DATASHEET,
        choices=[bundle(1, "ember lance and void net", 2)],
        priced=[],
    )
    assert projected[0].points_delta is None
    assert projected[0].priced_option_id is None


@pytest.mark.parametrize("items", [1, 2, 4])
def test_delta_and_priced_id_are_present_together_or_absent_together(items: int) -> None:
    # Guarantee 13's invariant, over a bundle of any width including the one-element case that
    # is what every `004` choice becomes. A consumer derives all three points states from this
    # pair, so a choice carrying one without the other makes the derivation partial.
    projected, _findings = project_priced_options(
        datasheet_id=DATASHEET,
        choices=[bundle(1, "ember lance", items), bundle(2, "void net", items)],
        priced=[priced("Ember lance", 10)],
    )
    for choice_row in projected:
        assert (choice_row.points_delta is None) == (choice_row.priced_option_id is None)


def test_a_joined_name_over_the_ceiling_is_unparsed_rather_than_truncated() -> None:
    # Research D3's 120-character ceiling. Truncating would produce a name that matches no
    # weapon and no priced row while looking like it should - the failure mode a reader cannot
    # see. The row goes to OPT-UNPARSED instead, where a curator can.
    over = "a" * (MAX_CHOICE_NAME_CHARS + 1)
    assert parse_row(f"This model can be equipped with 1 {over}.") is None
    with pytest.raises(ValidationError):
        CuratedOptionChoiceItem(role=OptionItemRole.GRANTED, item_index=1, item_name=over)
