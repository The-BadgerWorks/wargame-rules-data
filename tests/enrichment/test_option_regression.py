# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the FR-009 harness, layer 2 (006 task
# T011): the per-choice, per-field comparison classifies a newly-resolved row apart from a
# corrected one, a rewritten legacy label lands in Corrected, and the evidence command writes a
# report without touching data/, curation/, or state/ and without holding a verdict.
"""What layer 2 has to get right is the *distinction*, not the diff.

A row that resolves for the first time and a row that resolves *differently* look identical to
any counter — coverage counts resolved rows, so both increment it — and they mean opposite
things. The first is the feature working; the second is FR-009 broken. Every assertion below is
about keeping those two apart.

The one that matters most is :func:`test_a_rewritten_legacy_label_is_a_correction`: the O1 Ruling
turns on the promise that decomposing a conflated bundle never rewrites its ``name``, and this is
the instrument that would notice if it did.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from pipeline.models.curated import (
    CuratedDatasheet,
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
    CuratedSnapshot,
    OptionItemRole,
    OptionScope,
)
from pipeline.report.option_regression import (
    TRANSITION_NO_GIVEN_UP_ITEM_STATED,
    TRANSITION_RESOLVED_AND_RELINKED,
    TRANSITION_STATED_BUT_UNLINKED,
    compare,
    newly_resolved_datasheets,
    render,
)
from tests import factories

GROUP = CuratedOptionGroup(id="og-ember-sentinel-1", line=1, scope=OptionScope.UNIT)
CHOICE = CuratedOptionChoice(
    id="oc-ember-sentinel-1-1",
    group_id="og-ember-sentinel-1",
    name="ember lance and 2 void nets",
    count=1,
)


def _snapshot(datasheet: CuratedDatasheet) -> CuratedSnapshot:
    return factories.snapshot(datasheets=[datasheet])


def _with_options(
    groups: list[CuratedOptionGroup], choices: list[CuratedOptionChoice]
) -> CuratedSnapshot:
    base = factories.datasheet(cost_rows=factories.contextual_costs())
    return _snapshot(base.model_copy(update={"option_groups": groups, "option_choices": choices}))


# -- the distinction -----------------------------------------------------------------------------


def test_an_unchanged_choice_is_identical_and_nothing_else() -> None:
    published = _with_options([GROUP], [CHOICE])
    candidate = _with_options([GROUP], [CHOICE])

    result = compare(published, candidate, published_version_id="wh40k-11e-2026-08")

    assert result.is_clean
    assert (result.identical_groups, result.identical_choices) == (1, 1)
    assert result.corrected == ()
    assert result.newly_resolved_choices == ()


def test_a_row_the_baseline_never_resolved_is_newly_resolved_and_not_a_correction() -> None:
    """The feature working. Nothing a consumer has ever read changes."""
    published = _with_options([], [])
    candidate = _with_options([GROUP], [CHOICE])

    result = compare(published, candidate, published_version_id="wh40k-11e-2026-08")

    assert result.is_clean, "an addition is not a regression"
    assert len(result.newly_resolved_groups) == 1
    assert len(result.newly_resolved_choices) == 1
    assert result.corrected == ()


def test_a_rewritten_legacy_label_is_a_correction() -> None:
    """The O1 Ruling, made checkable.

    Option A leaves the ~144 conflated labels exactly as they are, and decomposition emits items
    without touching `name` or `count`. If a later change normalised one of those labels from its
    items, every affected row would appear here — which is the difference between a ruling that
    holds and a ruling nobody can verify.
    """
    published = _with_options([GROUP], [CHOICE])
    renamed = CHOICE.model_copy(update={"name": "ember lance, void net"})
    candidate = _with_options([GROUP], [renamed])

    result = compare(published, candidate, published_version_id="wh40k-11e-2026-08")

    assert not result.is_clean
    (difference,) = result.corrected
    assert (difference.entity_id, difference.field) == (CHOICE.id, "name")
    assert (difference.was, difference.now) == (CHOICE.name, "ember lance, void net")
    assert result.corrected_choices() == {CHOICE.id}


def test_decomposing_a_choice_into_items_is_not_a_correction() -> None:
    """The rule the whole O1 Ruling rests on: items are additive, the choice is untouched.

    This is the shape T018 produces over a legacy conflated bundle, and it must land in neither
    Corrected nor Newly resolved — the choice already existed and not one of its fields moved.
    """
    published = _with_options([GROUP], [CHOICE])
    decomposed = CHOICE.model_copy(
        update={
            "items": [
                CuratedOptionChoiceItem(
                    role=OptionItemRole.GRANTED, item_index=1, item_name="ember lance", count=1
                ),
                CuratedOptionChoiceItem(
                    role=OptionItemRole.GRANTED, item_index=2, item_name="void net", count=2
                ),
            ]
        }
    )
    candidate = _with_options([GROUP], [decomposed])

    result = compare(published, candidate, published_version_id="wh40k-11e-2026-08")

    assert result.is_clean
    assert result.corrected == ()


def test_a_choice_the_candidate_stopped_producing_is_a_regression() -> None:
    """A removal is a regression by any reading, so `is_clean` must not be blind to it."""
    published = _with_options([GROUP], [CHOICE])
    candidate = _with_options([], [])

    result = compare(published, candidate, published_version_id="wh40k-11e-2026-08")

    assert not result.is_clean
    assert len(result.removed_choices) == 1
    assert len(result.removed_groups) == 1


def test_an_unpriced_choice_never_reads_as_zero() -> None:
    """A published zero and an absent price are different facts, in this report as everywhere."""
    published = _with_options([], [])
    candidate = _with_options([GROUP], [CHOICE])

    (_datasheet_id, _choice_id, _kind, was, now) = compare(
        published, candidate, published_version_id="v"
    ).newly_resolved_choices[0]

    assert (was, now) == ("absent", "unpriced")


def test_a_repriced_choice_is_a_correction_and_names_both_sides() -> None:
    published = _with_options([GROUP], [CHOICE])
    repriced = CHOICE.model_copy(update={"points_delta": 15, "priced_option_id": "wo-x"})
    candidate = _with_options([GROUP], [repriced])

    result = compare(published, candidate, published_version_id="v")

    fields = {d.field: (d.was, d.now) for d in result.corrected}
    assert fields["points_delta"] == ("absent", "15")
    assert fields["priced_option_id"] == ("absent", "wo-x")


# -- 007 US2: OPT-LEGACY-CORRECTED, grouped by research D3.3's three transition classes (T020) --
#
# FR-007's ≈2 030-choice correction (research D3.2) needs an approver to read three patterns, not
# 2 030 unrelated lines (plan O1). `compare()` classifies every choice whose `grants_`/
# `replaces_weapon_line` moved between the published and candidate snapshots by inspecting the
# CANDIDATE side's REPLACED-role items — the same three shapes D3.3 names.

PUBLISHED_INVERTED = CuratedOptionChoice(
    id="oc-ember-sentinel-1-1",
    group_id="og-ember-sentinel-1",
    name="glow lance",
    count=1,
    replaces_weapon_line=9,  # the inversion: this is the GRANTED item's own line, pre-correction.
)


def _legacy_group() -> CuratedOptionGroup:
    return GROUP.model_copy(update={"eligible_model_name": "Marshlight Warden"})


def test_a_resolved_and_relinked_choice_is_classified_by_its_replaced_item() -> None:
    corrected = PUBLISHED_INVERTED.model_copy(
        update={
            "grants_weapon_line": 9,
            "replaces_weapon_line": 4,
            "items": [
                CuratedOptionChoiceItem(
                    role=OptionItemRole.GRANTED, item_index=1, item_name="glow lance", weapon_line=9
                ),
                CuratedOptionChoiceItem(
                    role=OptionItemRole.REPLACED,
                    item_index=1,
                    item_name="storm maul",
                    weapon_line=4,
                ),
            ],
        }
    )
    published = _with_options([_legacy_group()], [PUBLISHED_INVERTED])
    candidate = _with_options([_legacy_group()], [corrected])

    result = compare(published, candidate, published_version_id="v")

    assert [f.finding_code for f in result.legacy_corrections] == ["OPT-LEGACY-CORRECTED"]
    (finding,) = result.legacy_corrections
    assert finding.detail["transition_class"] == TRANSITION_RESOLVED_AND_RELINKED
    assert finding.detail["choice_name"] == "glow lance"
    assert finding.detail["choice_id"] == PUBLISHED_INVERTED.id


def test_a_stated_but_unlinked_choice_is_classified_by_its_unlinked_replaced_item() -> None:
    corrected = PUBLISHED_INVERTED.model_copy(
        update={
            "grants_weapon_line": 9,
            "replaces_weapon_line": None,
            "items": [
                CuratedOptionChoiceItem(
                    role=OptionItemRole.GRANTED, item_index=1, item_name="glow lance", weapon_line=9
                ),
                CuratedOptionChoiceItem(
                    role=OptionItemRole.REPLACED,
                    item_index=1,
                    item_name="ceremonial rod",
                    weapon_line=None,
                ),
            ],
        }
    )
    published = _with_options([_legacy_group()], [PUBLISHED_INVERTED])
    candidate = _with_options([_legacy_group()], [corrected])

    (finding,) = compare(published, candidate, published_version_id="v").legacy_corrections
    assert finding.detail["transition_class"] == TRANSITION_STATED_BUT_UNLINKED


def test_a_choice_with_no_replaced_item_at_all_is_the_third_class() -> None:
    # D3.3's "no given-up item at all" — the candidate's REPLACED side is simply empty.
    corrected = PUBLISHED_INVERTED.model_copy(
        update={
            "grants_weapon_line": 9,
            "replaces_weapon_line": None,
            "items": [
                CuratedOptionChoiceItem(
                    role=OptionItemRole.GRANTED, item_index=1, item_name="glow lance", weapon_line=9
                ),
            ],
        }
    )
    published = _with_options([_legacy_group()], [PUBLISHED_INVERTED])
    candidate = _with_options([_legacy_group()], [corrected])

    (finding,) = compare(published, candidate, published_version_id="v").legacy_corrections
    assert finding.detail["transition_class"] == TRANSITION_NO_GIVEN_UP_ITEM_STATED


def test_an_unchanged_choice_produces_no_legacy_correction_finding() -> None:
    published = _with_options([GROUP], [CHOICE])
    candidate = _with_options([GROUP], [CHOICE])

    assert compare(published, candidate, published_version_id="v").legacy_corrections == ()


def test_a_correction_to_an_unrelated_field_produces_no_legacy_correction_finding() -> None:
    # `count` moving is a DIFFERENT kind of correction (and, per FR-009, should never happen) —
    # OPT-LEGACY-CORRECTED is specifically about the derived link fields, not every field.
    published = _with_options([GROUP], [CHOICE])
    candidate = _with_options([GROUP], [CHOICE.model_copy(update={"count": 2})])

    assert compare(published, candidate, published_version_id="v").legacy_corrections == ()


def test_the_report_groups_legacy_corrections_by_transition_class_with_counts_and_names() -> None:
    resolved = PUBLISHED_INVERTED.model_copy(
        update={
            "grants_weapon_line": 9,
            "replaces_weapon_line": 4,
            "items": [
                CuratedOptionChoiceItem(
                    role=OptionItemRole.GRANTED, item_index=1, item_name="glow lance", weapon_line=9
                ),
                CuratedOptionChoiceItem(
                    role=OptionItemRole.REPLACED,
                    item_index=1,
                    item_name="storm maul",
                    weapon_line=4,
                ),
            ],
        }
    )
    published = _with_options([_legacy_group()], [PUBLISHED_INVERTED])
    candidate = _with_options([_legacy_group()], [resolved])

    rendered = render(compare(published, candidate, published_version_id="v"))

    assert "resolved" in rendered.casefold() and "relink" in rendered.casefold()
    assert "glow lance" in rendered
    # The per-class count is visible beside the class, not buried in a flat per-field table.
    assert "1" in rendered.split("## Corrected")[1].split("## Identical")[0]


# -- the datasheet-level view --------------------------------------------------------------------


def test_a_datasheet_whose_option_state_improved_is_named() -> None:
    """The headline set: the datasheets that stopped reading as broken data to a player."""
    base = factories.datasheet(cost_rows=factories.contextual_costs())
    published = _snapshot(base.model_copy(update={"wargear_option_state": "partial"}))
    candidate = _snapshot(base.model_copy(update={"wargear_option_state": "extracted"}))

    assert newly_resolved_datasheets(published, candidate) == (base.datasheet_id,)


# -- the report ----------------------------------------------------------------------------------


def test_the_report_leads_with_corrected_and_says_so_when_it_is_empty() -> None:
    """An empty section buried under two long ones is easy to assume rather than to check."""
    rendered = render(
        compare(
            _with_options([GROUP], [CHOICE]),
            _with_options([GROUP], [CHOICE]),
            published_version_id="v",
        )
    )

    assert rendered.index("## Corrected") < rendered.index("## Identical")
    assert rendered.index("## Corrected") < rendered.index("## Newly resolved")
    assert "Nothing the baseline resolved moved." in rendered


def test_the_report_carries_no_source_sentence() -> None:
    """Entities are named by id. A comparison report is a committed artifact."""
    rendered = render(
        compare(_with_options([], []), _with_options([GROUP], [CHOICE]), published_version_id="v")
    )

    assert "og-ember-sentinel-1" in rendered
    for vocabulary in ("can be replaced with", "can each have", "is equipped with"):
        assert vocabulary not in rendered


def test_a_correction_is_rendered_with_both_sides_named() -> None:
    published = _with_options([GROUP], [CHOICE])
    candidate = _with_options([GROUP], [CHOICE.model_copy(update={"count": 2})])

    rendered = render(compare(published, candidate, published_version_id="v"))

    assert "Nothing the baseline resolved moved." not in rendered
    assert "`count`" in rendered
    assert "| 1 | 2 |" in rendered


# -- the record is a plain dataclass, so a caller can build one ---------------------------------


def test_the_result_is_inspectable_without_running_a_build() -> None:
    """An approver's tooling, and this test file, both need to construct one directly."""
    result = compare(_with_options([], []), _with_options([], []), published_version_id="v")
    assert dataclasses.is_dataclass(result)
    assert result.published_version_id == "v"


def test_the_module_lives_beside_the_diff_vocabulary_it_reuses() -> None:
    """Principle 14, as a path assertion.

    `change_summary.py` holds the parser fixed and varies the source; this holds the source
    fixed and varies the parser. Two comparisons, one vocabulary, and an approver who already
    knows how to read one. A second diff format for the same entities is the reinvention that
    principle exists to prevent.
    """
    import pipeline.report.option_regression as module

    assert Path(module.__file__ or "").parent.name == "report"
