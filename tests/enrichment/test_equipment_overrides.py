# AI-Assisted: Claude Code (model: claude-sonnet-5) - Pays research R-6 / pipeline follow-up 14's
# debt (007 task T034): the equipment-override escape hatch (`006` §4) had no test coverage at
# all, unlike its composition- and option-override siblings in
# `test_composition_option_overrides.py`. Mirrors that file's own resolving/dangling-datasheet/
# dangling-line/dangling-weapon shape exactly, applied to `equipment_override_for` and
# `check_override_references`'s equipment-override branch instead.
"""The default-equipment escape hatch's contract, finally exercised.

Unlike GitHub issue #14 (the curated-tree round-trip this feature's own T029/T032 close), this is
`docs/follow-ups.md` item 14 — the pipeline's own numbered follow-up, an unrelated coincidence of
numbering research D8's R-6 calls out explicitly. Landing it here, before this feature's own
linking work (T023, T032) leans further on the same dangling-reference machinery with no test
behind it, is the point.
"""

from __future__ import annotations

from pipeline.curate.assemble import _equipment
from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import EquipmentOverrideEntry, EquipmentOverrideItem
from pipeline.models.curated import CuratedCompositionEntry, DefaultEquipmentState
from pipeline.models.findings import Severity
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text
from pipeline.report.catalogue import CATALOGUE
from pipeline.validate.refs import check_authored_references, check_override_references
from tests import factories
from tests.enrichment.conftest import weapon

DETAIL_ID = "GF18"
DATASHEET = "ds-marshwatch-line"

COMPOSITION = (
    CuratedCompositionEntry(line=1, model_name="Marshwatch Trooper", min_count=5, max_count=5),
)
WEAPONS = (weapon(1, "Snare net"),)

#: A compound-conditional subject (research D1e's tail) — matches no production, so the row is
#: `EQP-UNPARSED` without an override, exactly as `test_equipment_grammar.py`'s own tail cases.
UNPARSEABLE_SENTENCE = "If the unit has 10 or more models, 2 models are equipped with: snare net."


def _detail(description: str = UNPARSEABLE_SENTENCE) -> dict[str, CsvReadResult]:
    return {
        EQUIPMENT_TABLE: read_text(
            EQUIPMENT_TABLE, f"datasheet_id|line|description|\n{DETAIL_ID}|1|{description}|\n"
        )
    }


def equipment_override(**overrides: object) -> AuthoredContent:
    base: dict[str, object] = {
        "datasheet_id": DATASHEET,
        "line": 1,
        "applies_to": "unit",
        "items": [EquipmentOverrideItem(item_name="snare net", count=2, weapon_line=1)],
    }
    base.update(overrides)
    return AuthoredContent(equipment_overrides=(EquipmentOverrideEntry.model_validate(base),))


# --- an override resolves its row, and the finding goes with it -------------------------------


def test_without_an_override_the_sentence_is_unparsed_and_the_state_is_partial() -> None:
    outcome = _equipment(DETAIL_ID, DATASHEET, _detail(), AuthoredContent(), COMPOSITION, WEAPONS)
    assert outcome.groups == ()
    assert outcome.state is DefaultEquipmentState.PARTIAL
    assert [f.finding_code for f in outcome.findings] == ["EQP-UNPARSED"]


def test_an_equipment_override_resolves_the_row_and_the_finding_disappears() -> None:
    outcome = _equipment(
        DETAIL_ID, DATASHEET, _detail(), equipment_override(), COMPOSITION, WEAPONS
    )
    assert outcome.findings == []
    assert outcome.state is DefaultEquipmentState.EXTRACTED
    (group,) = outcome.groups
    assert (group.id, group.line, group.applies_to.value) == (
        "eq-marshwatch-line-1",
        1,
        "unit",
    )
    # The curator's own link is kept: re-joining by name would let a name match overrule the
    # human who wrote the override.
    (item,) = group.items
    assert (item.item_name, item.count, item.weapon_line) == ("snare net", 2, 1)


def test_an_override_never_carries_a_price() -> None:
    """There is deliberately nowhere in the schema to put one (`006` §4, the same terms
    `test_an_override_never_carries_a_price` already holds `OptionOverrideChoice` to)."""
    assert "points_delta" not in EquipmentOverrideEntry.model_fields
    assert "points_delta" not in EquipmentOverrideItem.model_fields


# --- an override that has gone stale ------------------------------------------------------------


def datasheet_with(**overrides: object):  # type: ignore[no-untyped-def]
    base = factories.datasheet(datasheet_id=DATASHEET)
    return base.model_copy(update=overrides)


def snapshot_with(**overrides: object):  # type: ignore[no-untyped-def]
    return factories.snapshot(datasheets=[datasheet_with(**overrides)])


def test_an_override_naming_a_datasheet_that_does_not_exist_is_blocking() -> None:
    authored = equipment_override(datasheet_id="ds-retired-unit")
    findings = check_authored_references(snapshot_with(), authored)
    (finding,) = [f for f in findings if f.detail["missing_id"] == "ds-retired-unit"]
    assert finding.finding_code == "AUT-DANGLING-REF"
    assert CATALOGUE["AUT-DANGLING-REF"].severity is Severity.BLOCKING
    # The row-level check stays silent for it: one defect, one finding, one place to fix it.
    assert check_override_references(snapshot_with(), authored) == []


def test_an_override_naming_a_line_that_no_longer_exists_is_blocking() -> None:
    outcome = _equipment(
        DETAIL_ID,
        DATASHEET,
        _detail("Every model is equipped with: snare net."),
        AuthoredContent(),
        COMPOSITION,
        WEAPONS,
    )
    findings = check_override_references(
        snapshot_with(equipment_groups=outcome.groups), equipment_override(line=9)
    )
    (finding,) = findings
    assert finding.finding_code == "AUT-DANGLING-REF"
    assert finding.detail["field"] == "line"


def test_an_override_naming_a_weapon_row_that_does_not_exist_is_blocking() -> None:
    findings = check_override_references(
        snapshot_with(equipment_groups=(), weapons=WEAPONS),
        equipment_override(items=[EquipmentOverrideItem(item_name="snare net", weapon_line=7)]),
    )
    assert [f.detail["field"] for f in findings] == ["weapon_line"]


def test_a_still_valid_override_on_a_datasheet_with_no_equipment_at_all_is_not_reported() -> None:
    # FR-016's own asymmetry (guarded identically to the composition-override precedent): a
    # datasheet whose composition never resolved, or whose source was never consulted, carries no
    # equipment_groups at all, and the override's line is legitimately absent rather than stale.
    assert check_override_references(snapshot_with(equipment_groups=()), equipment_override()) == []
