# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the record-aware CSV reader tests
# (task T045): the unescaped-newline row is rejoined and counted as DQ-MALFORMED-ROW, the BOM is
# stripped, and an unrepairable shape raises rather than silently mis-parsing.
"""Tests for the detail source's record-aware reader (FR-006, FR-008, research §0.1).

A line-based reader over this export is *quietly* wrong: two of 1 484 stratagem lines carry an
unescaped newline inside a description, so a naive reader produces two malformed records and
never says so. The reader here counts fields per record against the header, rejoins
continuation lines until the count is satisfied, and raises when the shape cannot be repaired.

Nothing in this module asserts anything about field *contents* beyond their count and their
identifiers — quoting a description into an assertion message would put source text in CI logs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.parse.wahapedia_csv import CsvShapeError, read_file, read_text

SAMPLE_CSV = Path(__file__).resolve().parents[2] / "fixtures" / "sample" / "wahapedia"


def test_bom_is_stripped_from_the_first_header_field() -> None:
    result = read_file(SAMPLE_CSV / "Factions.csv")
    assert result.field_names[0] == "id"
    assert "﻿" not in "".join(result.field_names)


def test_every_well_formed_file_reads_without_repair() -> None:
    for path in sorted(SAMPLE_CSV.glob("*.csv")):
        if path.name == "Stratagems.csv":
            continue
        result = read_file(path)
        assert result.repairs == 0, f"{path.name} needed a repair it should not need"
        assert all(len(row.fields) == len(result.field_names) for row in result.rows)


def test_the_unescaped_newline_record_is_rejoined_and_counted() -> None:
    result = read_file(SAMPLE_CSV / "Stratagems.csv")

    assert len(result.rows) == 3
    assert result.repairs == 1
    assert [f.finding_code for f in result.findings] == ["DQ-MALFORMED-ROW"]

    finding = result.findings[0]
    assert finding.detail["file_name"] == "Stratagems.csv"
    assert finding.detail["expected_fields"] == len(result.field_names)
    assert finding.detail["physical_lines"] == 2


def test_a_repaired_row_is_flagged_on_the_record_itself() -> None:
    result = read_file(SAMPLE_CSV / "Stratagems.csv")
    repaired = [row for row in result.rows if row.repaired]
    assert len(repaired) == 1
    assert repaired[0].fields["id"] == "S002"


def test_the_rejoined_record_keeps_its_field_boundaries() -> None:
    """The split falls inside one field; rejoining must not shift any other field."""
    result = read_file(SAMPLE_CSV / "Stratagems.csv")
    row = next(r for r in result.rows if r.fields["id"] == "S002")
    assert row.fields["faction_id"] == "EW"
    assert row.fields["detachment_id"] == "D001"
    assert row.fields["cp_cost"] == "2"


def test_a_record_with_too_many_fields_is_unrepairable_and_raises() -> None:
    text = "a|b|\n1|2|3|\n"
    with pytest.raises(CsvShapeError) as raised:
        read_text("Broken.csv", text)
    assert "Broken.csv" in str(raised.value)
    assert "3" in str(raised.value)


def test_a_trailing_short_record_is_unrepairable_and_raises() -> None:
    """A short final record has no continuation line to absorb it, so it cannot be repaired."""
    text = "a|b|c|\n1|2|3|\n4|5\n"
    with pytest.raises(CsvShapeError):
        read_text("Truncated.csv", text)


def test_the_diagnostic_quotes_the_shape_and_never_the_content() -> None:
    text = "a|b|\nkeep-this-secret|2|3|\n"
    with pytest.raises(CsvShapeError) as raised:
        read_text("Broken.csv", text)
    assert "keep-this-secret" not in str(raised.value)


def test_an_empty_file_is_a_shape_error_rather_than_zero_rows() -> None:
    with pytest.raises(CsvShapeError):
        read_text("Empty.csv", "")


def test_blank_lines_between_records_are_ignored() -> None:
    result = read_text("Spaced.csv", "a|b|\n1|2|\n\n3|4|\n")
    assert len(result.rows) == 2
    assert result.repairs == 0
