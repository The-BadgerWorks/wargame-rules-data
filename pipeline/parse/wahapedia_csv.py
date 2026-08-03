# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the record-aware CSV reader
# (task T059): per-file expected field count, continuation-line rejoining for the
# unescaped-newline case, BOM stripping, one DQ-MALFORMED-ROW per repair, and a hard failure on
# an unrepairable shape (FR-006, FR-008).
"""Read the detail source's pipe-delimited export **by record, not by line**.

Research §0.1 measured the problem: 2 of 1 484 rows in one export file carry an unescaped
newline inside a description, so a line-based reader turns one record into two malformed ones
and reports nothing. The damage is not the two rows — those files are not carried into curated
data — it is that the same reader is used on every file, and the *next* file it happens in might
be one that is.

So the reader counts fields against the header and rejoins continuation lines until the count is
satisfied. A record it cannot repair — too many fields, or a short record at end of file with
nothing left to absorb — raises rather than guessing, because a mis-split record silently shifts
every field after the split and there is no way to notice downstream.

**Diagnostics quote the shape, never the content** (`validation-report.md` §1.4). "expected 12
fields, got 14" is exactly as useful as quoting the row, and does not put source text in a CI
log.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pipeline.models.findings import Finding
from pipeline.models.source import WahapediaRow
from pipeline.report.catalogue import build_finding

#: The export's delimiter. Not a CSV dialect: there is no quoting, which is why an embedded
#: newline cannot be escaped and the repair below exists at all.
DELIMITER = "|"


class CsvShapeError(ValueError):
    """A record whose field count cannot be reconciled with the header.

    Distinct from a data-quality *finding*: a finding is something the run reports and carries
    on from, and this is something the run cannot honestly continue past.
    """


@dataclass(frozen=True, slots=True)
class CsvReadResult:
    """One export file, read into records."""

    file_name: str
    field_names: tuple[str, ...]
    rows: tuple[WahapediaRow, ...]
    repairs: int
    findings: tuple[Finding, ...]

    def by_id(self, key: str) -> dict[str, WahapediaRow]:
        """Index the records by one field. Later records win, matching the export's own order."""
        return {row.fields[key]: row for row in self.rows if row.fields.get(key)}

    def grouped_by(self, key: str) -> dict[str, list[WahapediaRow]]:
        """Group the records by one field, preserving file order within each group."""
        groups: dict[str, list[WahapediaRow]] = {}
        for row in self.rows:
            value = row.fields.get(key)
            if value:
                groups.setdefault(value, []).append(row)
        return groups


def _split_header(line: str) -> tuple[tuple[str, ...], int]:
    """Return the field names and how many trailing empty tokens the delimiter style produces.

    The export terminates each record with a trailing delimiter, so splitting yields one empty
    token past the last named field. That token is part of what a reader has to *count*, but it
    is not a field — so counts reported to a human are in named fields, which is the number they
    can check against the header.
    """
    tokens = line.split(DELIMITER)
    if tokens and tokens[-1] == "":
        return tuple(tokens[:-1]), 1
    return tuple(tokens), 0


def read_text(file_name: str, text: str) -> CsvReadResult:
    """Read one export file's text into records."""
    body = text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    lines = body.split("\n")

    header_index = next((i for i, line in enumerate(lines) if line.strip()), None)
    if header_index is None:
        raise CsvShapeError(f"{file_name}: the file carries no header record")

    field_names, trailing = _split_header(lines[header_index])
    expected_fields = len(field_names)
    expected_tokens = expected_fields + trailing

    rows: list[WahapediaRow] = []
    findings: list[Finding] = []
    repairs = 0

    buffer = ""
    buffer_line = 0
    buffer_parts = 0

    for offset, line in enumerate(lines[header_index + 1 :], start=header_index + 2):
        if not buffer and not line.strip():
            continue

        if buffer:
            # The split fell inside a field, so the newline is part of that field's value.
            buffer = f"{buffer}\n{line}"
            buffer_parts += 1
        else:
            buffer, buffer_line, buffer_parts = line, offset, 1

        tokens = buffer.split(DELIMITER)
        if len(tokens) < expected_tokens:
            continue
        if len(tokens) > expected_tokens:
            raise CsvShapeError(
                f"{file_name}: the record starting at line {buffer_line} has "
                f"{len(tokens) - trailing} fields where the header declares {expected_fields}; "
                "the shape cannot be repaired"
            )

        if buffer_parts > 1:
            repairs += 1
            findings.append(
                build_finding(
                    "DQ-MALFORMED-ROW",
                    entity_refs=[f"{file_name}:{buffer_line}"],
                    detail={
                        "file_name": file_name,
                        "line_number": buffer_line,
                        "expected_fields": expected_fields,
                        "physical_lines": buffer_parts,
                    },
                )
            )

        rows.append(
            WahapediaRow(
                file_name=file_name,
                line_number=buffer_line,
                fields=dict(zip(field_names, tokens, strict=False)),
                repaired=buffer_parts > 1,
            )
        )
        buffer, buffer_parts = "", 0

    if buffer:
        raise CsvShapeError(
            f"{file_name}: the record starting at line {buffer_line} runs to end of file with "
            f"{len(buffer.split(DELIMITER)) - trailing} of {expected_fields} fields; there is "
            "no continuation line left to repair it with"
        )

    return CsvReadResult(
        file_name=file_name,
        field_names=field_names,
        rows=tuple(rows),
        repairs=repairs,
        findings=tuple(findings),
    )


def read_file(path: Path) -> CsvReadResult:
    """Read one export file from disk. ``utf-8-sig`` strips the BOM the real export carries."""
    return read_text(path.name, path.read_text(encoding="utf-8-sig"))
