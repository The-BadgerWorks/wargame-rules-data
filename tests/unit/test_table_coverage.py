# AI-Assisted: Claude Code (model: claude-sonnet-5) - New tests for SRC-TABLE-MISSING (009 tasks
# T027/T028, FR-018, rule 3): a table the build consumes that is absent or empty in the acquired
# set is a blocking finding naming the table, asserted against parsed reader output rather than a
# fixture directory listing.
"""``SRC-TABLE-MISSING`` — presence AND population, asserted against what was acquired.

The existing ``EXPORT_FILES`` sweep in ``_read_local``/``_fetch_remote`` already refuses a run
where a named file is missing from the source entirely — a hard `SourceUnreachable`, because a
partial export is a failed acquisition (FR-008). What that sweep cannot see is a file that is
*present* but was acquired with zero usable rows in it: syntactically a valid export, structurally
an empty table. :func:`check_table_coverage` is the other half.
"""

from __future__ import annotations

from pipeline.acquire.wahapedia import check_table_coverage
from pipeline.models.findings import Severity
from pipeline.parse.wahapedia_csv import read_text

_POPULATED = read_text("Factions.csv", "id|name|\nSM|Space Marines|\n")
_HEADER_ONLY = read_text("Detachment_abilities.csv", "id|detachment_id|name|legend|description|\n")


def test_a_present_and_populated_table_is_not_reported() -> None:
    findings = check_table_coverage({"Factions.csv": _POPULATED}, consumed_tables=["Factions.csv"])

    assert findings == []


def test_a_present_but_empty_table_is_the_blocking_finding_naming_the_table() -> None:
    findings = check_table_coverage(
        {"Detachment_abilities.csv": _HEADER_ONLY}, consumed_tables=["Detachment_abilities.csv"]
    )

    assert len(findings) == 1
    assert findings[0].finding_code == "SRC-TABLE-MISSING"
    assert findings[0].severity is Severity.BLOCKING
    assert findings[0].detail == {"table": "Detachment_abilities.csv"}


def test_a_table_absent_from_the_acquired_mapping_entirely_is_also_reported() -> None:
    """ "Absent" and "empty" are the same finding -- the build cannot tell them apart usefully,
    and a curator does not need to: either way, the table it needed has nothing in it."""
    findings = check_table_coverage({}, consumed_tables=["Datasheets.csv"])

    assert [f.detail["table"] for f in findings] == ["Datasheets.csv"]


def test_only_the_tables_the_caller_names_are_checked() -> None:
    """A table the caller did not list as consumed is never reported, however it is acquired."""
    findings = check_table_coverage({}, consumed_tables=[])

    assert findings == []


def test_multiple_missing_tables_are_each_named() -> None:
    findings = check_table_coverage(
        {"Factions.csv": _POPULATED},
        consumed_tables=["Factions.csv", "Datasheets.csv", "Detachment_abilities.csv"],
    )

    assert sorted(str(f.detail["table"]) for f in findings) == [
        "Datasheets.csv",
        "Detachment_abilities.csv",
    ]


def test_it_is_asserted_against_parsed_rows_not_a_directory_listing() -> None:
    """The whole point: a file's mere PRESENCE (what a directory listing would show) is not what
    is checked -- its parsed ROW COUNT is. `_HEADER_ONLY` exists on disk in every fixture
    directory that lists it; that is exactly the case this function must still flag."""
    assert _HEADER_ONLY.rows == ()
    findings = check_table_coverage(
        {"Detachment_abilities.csv": _HEADER_ONLY}, consumed_tables=["Detachment_abilities.csv"]
    )

    assert len(findings) == 1
