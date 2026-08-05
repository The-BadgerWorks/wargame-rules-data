# AI-Assisted: Claude Code (model: claude-opus-5) - The curator escape hatch's contract (004 task
# T026): an override resolves its keyed row and the finding disappears with it, and an override
# naming a datasheet, line, or model that does not exist is the blocking AUT-DANGLING-REF.
"""The two override files, and why they are what makes "never guess" affordable.

Without them a 1.3% composition tail and a ~20% option tail would be permanent defects. With them
they are a bounded, one-time, carry-forward cost — exactly how `002` made ability summaries
tractable. The price of that is the second half of this module: an override outlives the data it
points at, so a retired line has to be reconciled in the release that retires it rather than
never.
"""

from __future__ import annotations

from pipeline.curate.assemble import _composition_entries, _option_structure
from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import (
    CompositionOverrideEntry,
    OptionOverrideChoice,
    OptionOverrideEntry,
)
from pipeline.models.curated import OptionScope, WargearOptionState
from pipeline.models.findings import Severity
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text
from pipeline.report.catalogue import CATALOGUE
from pipeline.validate.refs import check_authored_references, check_override_references
from tests import factories
from tests.enrichment.conftest import curated_models, weapon

DETAIL_ID = "GF05"
DATASHEET = "ds-mirefen-tanglers"

UNRESOLVABLE_COMPOSITION = (
    "datasheet_id|line|description|\nGF05|1|Every model in this unit is equipped with:|\n"
)
UNPARSED_OPTIONS = (
    "datasheet_id|line|button|description|\n"
    "GF05|1|Wargear Options|Each Mirefen Tangler may take a snare net.|\n"
)


def detail(
    composition: str = UNRESOLVABLE_COMPOSITION, options: str = UNPARSED_OPTIONS
) -> dict[str, CsvReadResult]:
    return {
        "Datasheets_unit_composition.csv": read_text(
            "Datasheets_unit_composition.csv", composition
        ),
        "Datasheets_options.csv": read_text("Datasheets_options.csv", options),
    }


def composition_override(**overrides: object) -> AuthoredContent:
    base: dict[str, object] = {
        "datasheet_id": DATASHEET,
        "line": 1,
        "model_name": "Mirefen Tangler",
        "min_count": 3,
        "max_count": 6,
        "model_line": 1,
    }
    base.update(overrides)
    return AuthoredContent(composition_overrides=(CompositionOverrideEntry.model_validate(base),))


def option_override(**overrides: object) -> AuthoredContent:
    base: dict[str, object] = {
        "datasheet_id": DATASHEET,
        "line": 1,
        "scope": "unit",
        "choices": [OptionOverrideChoice(name="snare net", count=1, grants_weapon_line=1)],
    }
    base.update(overrides)
    return AuthoredContent(option_overrides=(OptionOverrideEntry.model_validate(base),))


# --- an override resolves its row, and the finding goes with it -------------------------------


def test_without_an_override_the_row_is_unresolved_and_reported() -> None:
    entries, findings = _composition_entries(
        DETAIL_ID, DATASHEET, detail(), AuthoredContent(), curated_models("GF05")
    )
    assert entries == []
    assert [f.finding_code for f in findings] == ["CMP-UNRESOLVED"]


def test_a_composition_override_resolves_the_row_and_the_finding_disappears() -> None:
    entries, findings = _composition_entries(
        DETAIL_ID, DATASHEET, detail(), composition_override(), curated_models("GF05")
    )
    assert findings == []
    (entry,) = entries
    assert (entry.model_name, entry.min_count, entry.max_count, entry.model_line) == (
        "Mirefen Tangler",
        3,
        6,
        1,
    )


def test_without_an_override_the_option_row_is_unparsed_and_the_state_is_partial() -> None:
    outcome = _option_structure(
        DETAIL_ID, DATASHEET, detail(), AuthoredContent(), [weapon(1, "Snare net")], []
    )
    assert outcome.groups == []
    assert outcome.state is WargearOptionState.PARTIAL
    assert [f.finding_code for f in outcome.findings] == ["OPT-UNPARSED"]


def test_an_option_override_resolves_the_row_and_the_finding_disappears() -> None:
    outcome = _option_structure(
        DETAIL_ID, DATASHEET, detail(), option_override(), [weapon(1, "Snare net")], []
    )
    assert outcome.findings == []
    assert outcome.state is WargearOptionState.EXTRACTED
    (group,) = outcome.groups
    assert (group.id, group.line, group.scope) == ("og-mirefen-tanglers-1", 1, OptionScope.UNIT)
    (choice,) = outcome.choices
    # The curator's own link is kept: re-joining by name would let a name match overrule the
    # human who wrote the override.
    assert (choice.name, choice.count, choice.grants_weapon_line) == ("snare net", 1, 1)


def test_an_override_never_carries_a_price() -> None:
    """There is deliberately nowhere in the schema to put one (004 FR-013, C8/R3)."""
    assert "points_delta" not in OptionOverrideChoice.model_fields
    outcome = _option_structure(
        DETAIL_ID, DATASHEET, detail(), option_override(), [weapon(1, "Snare net")], []
    )
    assert outcome.choices[0].points_delta is None


# --- an override that has gone stale ----------------------------------------------------------


def datasheet_with(**overrides: object):  # type: ignore[no-untyped-def]
    base = factories.datasheet(datasheet_id=DATASHEET)
    return base.model_copy(update=overrides)


def snapshot_with(**overrides: object):  # type: ignore[no-untyped-def]
    return factories.snapshot(datasheets=[datasheet_with(**overrides)])


def test_an_override_naming_a_datasheet_that_does_not_exist_is_blocking() -> None:
    authored = composition_override(datasheet_id="ds-retired-unit")
    findings = check_authored_references(snapshot_with(), authored)
    (finding,) = [f for f in findings if f.detail["missing_id"] == "ds-retired-unit"]
    assert finding.finding_code == "AUT-DANGLING-REF"
    assert CATALOGUE["AUT-DANGLING-REF"].severity is Severity.BLOCKING
    # The row-level check stays silent for it: one defect, one finding, one place to fix it.
    assert check_override_references(snapshot_with(), authored) == []


def test_an_override_naming_a_line_that_no_longer_exists_is_blocking() -> None:
    entries, _ = _composition_entries(
        DETAIL_ID,
        DATASHEET,
        detail("datasheet_id|line|description|\nGF05|1|1 Mirefen Tangler|\n"),
        AuthoredContent(),
        curated_models("GF05"),
    )
    findings = check_override_references(
        snapshot_with(composition=entries), composition_override(line=7)
    )
    (finding,) = findings
    assert finding.finding_code == "AUT-DANGLING-REF"
    assert finding.detail["field"] == "line"


def test_an_override_naming_a_model_row_that_does_not_exist_is_blocking() -> None:
    findings = check_override_references(
        snapshot_with(composition=()), composition_override(model_line=9)
    )
    assert [f.detail["field"] for f in findings] == ["model_line"]


def test_a_still_valid_override_on_a_suppressed_composition_is_not_reported() -> None:
    # FR-008 suppresses the whole datasheet's composition as soon as any one line is unresolved,
    # so the override's line is legitimately absent. Reporting it would send the curator to fix
    # the one record that is already correct.
    assert check_override_references(snapshot_with(composition=()), composition_override()) == []


def test_an_option_override_naming_a_weapon_row_that_does_not_exist_is_blocking() -> None:
    outcome = _option_structure(
        DETAIL_ID, DATASHEET, detail(), option_override(), [weapon(1, "Snare net")], []
    )
    findings = check_override_references(
        snapshot_with(option_groups=outcome.groups, weapons=[weapon(1, "Snare net")]),
        option_override(choices=[OptionOverrideChoice(name="snare net", replaces_weapon_line=4)]),
    )
    assert [f.detail["field"] for f in findings] == ["replaces_weapon_line"]
