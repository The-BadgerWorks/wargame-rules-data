# AI-Assisted: Claude Code (model: claude-sonnet-5) - New tests for FR-014's reverse-direction
# crosswalk check (009 tasks T025/T026, data-model.md §1/§5): a datasheet with no unit-map.json
# entry, once the export arm is authoritative for it, must be reported exactly as a dangling
# forward reference already is -- "validated on load, in both directions".
"""FR-014's crosswalk, dangling in either direction.

The forward direction (`unit-map.json` naming a `datasheet_id` the snapshot does not contain) is
already covered by `AUT-DANGLING-REF` (`curate/authored.py:authored_entity_refs`,
`validate/refs.py::check_authored_references`) — this file's first test pins that it still holds.
The reverse direction — a datasheet the crosswalk should pin but does not — is what
`check_unit_map_reverse_coverage` adds.

**Why this is not wired into the live build yet.** Which datasheets the export arm is
authoritative for is Open Decision O2 (collision set only, plus every `-N`-suffixed slug, or the
whole corpus), not decided until T047. Wiring an unconditional "every datasheet needs a pin"
check into `check_authored_references` today — before a single `unit-map.json` entry has been
authored (Setup's own note: "the file itself does not exist") — would immediately block every
build on thousands of missing entries it was never anyone's job to author yet. So the function
takes its scope as an explicit parameter with no default, and this file exercises it directly
rather than through the pipeline's always-on validation entry point.
"""

from __future__ import annotations

from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import UnitMapEntry
from pipeline.models.findings import Severity
from pipeline.validate.refs import check_authored_references, check_unit_map_reverse_coverage
from tests import factories


def _entry(datasheet_id: str, *, wahapedia_datasheet_id: str = "W01") -> UnitMapEntry:
    return UnitMapEntry(
        datasheet_id=datasheet_id,
        mfm_display_name="Placeholder Unit",
        wahapedia_datasheet_id=wahapedia_datasheet_id,
        confirmed_at="2026-08-18",
        confirmed_by="test-curator",
    )


def test_forward_direction_still_holds_a_dangling_crosswalk_entry_is_reported() -> None:
    """`AUT-DANGLING-REF` for an entry naming a datasheet the snapshot does not contain."""
    authored = AuthoredContent(unit_map=(_entry("ds-does-not-exist"),))
    snapshot = factories.snapshot(datasheets=[factories.datasheet(datasheet_id="ds-real")])

    findings = check_authored_references(snapshot, authored)
    dangling = [f for f in findings if f.finding_code == "AUT-DANGLING-REF"]

    assert len(dangling) == 1
    assert dangling[0].severity is Severity.BLOCKING
    assert dangling[0].detail == {
        "file_name": "unit-map.json",
        "field": "datasheet_id",
        "missing_id": "ds-does-not-exist",
    }


def test_reverse_direction_a_datasheet_with_no_crosswalk_entry_is_reported() -> None:
    authored = AuthoredContent(unit_map=(_entry("ds-pinned"),))

    findings = check_unit_map_reverse_coverage(
        authored, authoritative_datasheet_ids=frozenset({"ds-pinned", "ds-unpinned"})
    )

    assert len(findings) == 1
    assert findings[0].finding_code == "AUT-DANGLING-REF"
    assert findings[0].severity is Severity.BLOCKING
    assert findings[0].detail == {
        "file_name": "unit-map.json",
        "field": "datasheet_id",
        "missing_id": "ds-unpinned",
    }


def test_a_datasheet_with_a_pin_is_not_reported() -> None:
    authored = AuthoredContent(unit_map=(_entry("ds-pinned"),))

    findings = check_unit_map_reverse_coverage(
        authored, authoritative_datasheet_ids=frozenset({"ds-pinned"})
    )

    assert findings == []


def test_an_empty_authoritative_scope_reports_nothing() -> None:
    """No caller has passed a real scope yet (O2 undecided) -- the function must not invent one."""
    authored = AuthoredContent()

    findings = check_unit_map_reverse_coverage(authored, authoritative_datasheet_ids=frozenset())

    assert findings == []


def test_multiple_missing_pins_are_each_reported_and_sorted() -> None:
    authored = AuthoredContent()

    findings = check_unit_map_reverse_coverage(
        authored, authoritative_datasheet_ids=frozenset({"ds-b", "ds-a"})
    )

    assert [f.detail["missing_id"] for f in findings] == ["ds-a", "ds-b"]
