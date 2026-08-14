#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the T031 whole-corpus
# re-derivation of the five-signal composition-header refusal (007 task T031, risk R-1/R-A's own
# mitigation): acquire the detail source in the configured mode into an ephemeral work/, apply
# research D1's full five-signal rule (the same conjunction pipeline/curate/assemble.py::
# _refuse_header_row implements) over every datasheet's composition rows, and report every
# refused row by datasheet id for review before the fix ships — modelled on
# tools/header_refusal_population.py's acquire-into-ephemeral-work-then-discard shape, but
# distinct from it: T004's tool measures signal 4's population only and refuses nothing; this
# tool applies all five signals and reports the actual refusal set T030 will produce.
"""Re-derive the whole-corpus five-signal header-refusal set, for review before T030 ships.

research D1 designs the refusal as a conjunction of five independent structural signals, applied
where composition entries are assembled (never in the line grammar): a row is refused when it is
the first row of its datasheet's composition list, at least one row follows it, its minimum equals
its maximum, its count equals the sum of the maxima of the rows that follow it, and its name
resolves to no model entry of the datasheet.

D8's R-1/R-A: "the five-signal header refusal suppresses a genuine first model row on some card
outside the measured eight [Kill Team datasheets]." The mitigation is this tool — re-deriving the
refusal set over the **whole** corpus and reporting every refused row by datasheet id, so a human
reviews the set before the fix ships. A refusal set larger than the eight known Kill Team
datasheets is a finding to review, not necessarily a defect::

    python tools/composition_header_refusal_report.py                                    # live
    python tools/composition_header_refusal_report.py --fixtures fixtures/minimal --offline

**No source text anywhere.** Only integers, model names already published as composition data,
and datasheet ids reach the report — never a description field or a raw export row.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from pipeline.acquire.detail_source import acquire_detail, read_detail
from pipeline.acquire.http import AcquisitionError
from pipeline.config import ConfigError, PipelineConfig, load_config, repo_root
from pipeline.exit_codes import ExitCode
from pipeline.models.source import WahapediaRow
from pipeline.parse.composition_grammar import CompositionParse, link_model_line, parse_entry
from pipeline.workspace import workspace

PROG: Final = "composition_header_refusal_report.py"

REPORTS_DIR: Final = Path("reports") / "composition-header-refusal"

_COMPOSITION_TABLE: Final = "Datasheets_unit_composition.csv"
_MODELS_TABLE: Final = "Datasheets_models.csv"


@dataclass(frozen=True, slots=True)
class RefusedRow:
    """One row the five-signal rule refuses. A datasheet id, a line ordinal, and a name only."""

    datasheet_id: str
    line: int
    model_name: str


@dataclass(frozen=True, slots=True)
class HeaderRefusalReport:
    generated_at: str
    mode: str
    edition: str
    source: str
    datasheets_with_composition: int
    refused: tuple[RefusedRow, ...] = field(default_factory=tuple)


def refuses(
    first: CompositionParse, rest: Sequence[CompositionParse], *, model_lines: Mapping[int, str]
) -> bool:
    """research D1's five-signal conjunction, over one datasheet's already-ordered rows.

    Signals 1-2 (first row, at least one successor) are the caller's precondition — this function
    is only ever invoked with a genuine first-of-two-or-more row. Signals 3-5 are checked here,
    identically to :func:`pipeline.curate.assemble._refuse_header_row`.
    """
    is_fixed = first.min_count == first.max_count
    sums_to_successors = first.max_count == sum(entry.max_count for entry in rest)
    is_unlinked = link_model_line(first.model_name, model_lines) is None
    return is_fixed and sums_to_successors and is_unlinked


def measure(
    config: PipelineConfig,
    *,
    repository_root: Path,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    generated_at: datetime | None = None,
) -> HeaderRefusalReport:
    """Acquire, classify, discard — and return only counts, ids, and the refused rows' own names.

    Every acquired string lives inside the ``with workspace(...)`` block; a refused row's own
    (already-published) model name is the only text that leaves it, on the same terms
    :mod:`tools.header_refusal_population` already holds itself to.
    """
    datasheets_with_composition = 0
    refused: list[RefusedRow] = []

    with workspace(repository_root) as work:
        acquisition, payloads = acquire_detail(
            config, fixtures_dir=fixtures_dir, offline=offline, workspace=work
        )
        source = acquisition.source_base_url
        tables = read_detail(config, payloads)

        composition = tables.get(_COMPOSITION_TABLE)
        models = tables.get(_MODELS_TABLE)
        if composition is not None:
            models_by_datasheet: Mapping[str, list[WahapediaRow]] = (
                models.grouped_by("datasheet_id") if models is not None else {}
            )
            grouped = composition.grouped_by("datasheet_id")
            for datasheet_id, rows in grouped.items():
                if not datasheet_id:
                    continue
                ordered = sorted(rows, key=lambda row: _line(row.fields.get("line", "")))
                parsed: list[tuple[int, CompositionParse | None]] = [
                    (
                        _line(row.fields.get("line", "")),
                        parse_entry(row.fields.get("description", "")),
                    )
                    for row in ordered
                ]
                if all(entry is None for _line_no, entry in parsed):
                    continue
                datasheets_with_composition += 1

                if len(parsed) < 2:
                    continue
                first_line, first = parsed[0]
                rest = [entry for _line_no, entry in parsed[1:]]
                if first is None or any(entry is None for entry in rest):
                    continue
                resolved_rest = [entry for entry in rest if entry is not None]

                model_lines = {
                    _line(row.fields.get("line", "")): row.fields.get("name", "")
                    for row in models_by_datasheet.get(datasheet_id, [])
                }
                if refuses(first, resolved_rest, model_lines=model_lines):
                    refused.append(
                        RefusedRow(
                            datasheet_id=datasheet_id, line=first_line, model_name=first.model_name
                        )
                    )

    moment = (generated_at or datetime.now(UTC)).astimezone(UTC)
    return HeaderRefusalReport(
        generated_at=moment.isoformat().replace("+00:00", "Z"),
        mode=config.detail_acquisition_mode.value,
        edition=config.detail_edition,
        source=source,
        datasheets_with_composition=datasheets_with_composition,
        refused=tuple(sorted(refused, key=lambda row: row.datasheet_id)),
    )


def _line(raw: str) -> int:
    try:
        return int(raw)
    except ValueError:
        return 0


def render(report: HeaderRefusalReport) -> str:
    """The measurement as Markdown. Datasheet ids, line ordinals, and names already published as
    composition data — never a description field or a raw export row."""
    lines = [
        "<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Generated by "
        "tools/composition_header_refusal_report.py (007 T031). -->",
        "# Composition-header refusal set (research D1, risk R-1/R-A)",
        "",
        f"- Generated: `{report.generated_at}`",
        f"- Detail acquisition mode: `{report.mode}`",
        f"- Declared detail edition: `{report.edition}`",
        f"- Source: `{report.source}`",
        "",
        "**Non-destructive.** Nothing under `data/`, `curation/`, or `state/` was written, the "
        "acquired pages were discarded with `work/` when the run ended, and no composition "
        "description reaches this page — only datasheet ids, line ordinals, and model names "
        "already published as composition data.",
        "",
        "## Every row the five-signal rule refuses",
        "",
        "A row is refused when it is the datasheet's first composition row, at least one row "
        "follows it, its minimum equals its maximum, its count equals the sum of the maxima of "
        "the rows that follow it, and its name resolves to no model entry of the datasheet — "
        "`pipeline/curate/assemble.py::_refuse_header_row`'s own conjunction, re-derived here "
        "over the whole corpus rather than the eight measured Kill Team datasheets.",
        "",
        f"Datasheets with composition: {report.datasheets_with_composition}. Rows refused: "
        f"**{len(report.refused)}**.",
        "",
        "## Reading this",
        "",
        "- **A refusal set of exactly the eight known Kill Team datasheets confirms the fix is "
        "scoped as measured.** research D1 measured all five signals holding on eight affected "
        "datasheets; this report is where that count is checked against the live corpus.",
        "- **A refusal set larger than eight is R-1/R-A's own risk materialising — a finding to "
        "review, not an automatic defect.** Each row below should be read against its own card "
        "before the fix ships: the conjunction is designed so a false positive requires a first "
        "row that is simultaneously unlinkable, fixed-size, and numerically equal to the total "
        "of every other row, which is the 'total' reading anyway — but this report is where a "
        "human confirms that reading holds for each one, not where it is assumed.",
        "",
        "### Refused rows",
        "",
    ]
    if report.refused:
        lines.append("| Datasheet id | Line | Model name |")
        lines.append("|---|---:|---|")
        lines.extend(
            f"| `{row.datasheet_id}` | {row.line} | {row.model_name} |" for row in report.refused
        )
    else:
        lines.append("*(none)*")
    lines.append("")
    return "\n".join(lines)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Re-derive the whole-corpus five-signal composition-header refusal set (research D1, "
            "risk R-1/R-A), retaining no source text beyond already-published names."
        ),
    )
    parser.add_argument("--fixtures", type=Path, help="source from a synthetic fixture set")
    parser.add_argument(
        "--offline", action="store_true", help="refuse network access; requires --fixtures"
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="report path (default reports/composition-header-refusal/<date>.md)",
    )
    parser.add_argument("--repo", type=Path, help="repository root (default: this checkout)")
    parser.add_argument(
        "--print-only", action="store_true", help="render to stdout and write no file"
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _summary_line(report: HeaderRefusalReport) -> str:
    return (
        f"{PROG}: {len(report.refused)} rows refused over "
        f"{report.datasheets_with_composition} datasheets with composition"
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    root = args.repo or repo_root()

    try:
        config = load_config()
        report = measure(
            config, repository_root=root, fixtures_dir=args.fixtures, offline=args.offline
        )
    except ConfigError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)
    except AcquisitionError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(exc.exit_code)

    rendered = render(report)
    if args.print_only:
        print(rendered)
    else:
        destination = args.out or (root / REPORTS_DIR / f"{report.generated_at[:10]}.md")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"{PROG}: wrote {destination}")

    print(_summary_line(report))
    return int(ExitCode.SUCCESS)


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
