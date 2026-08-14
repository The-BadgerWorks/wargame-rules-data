#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the R-2 non-summing-header
# population probe (007 task T004): acquire the detail source in the configured mode into an
# ephemeral work/, find every datasheet's first composition row whose min_count equals
# max_count, test whether that count equals the sum of the maxima of the rows that follow it,
# and report the population of both outcomes by datasheet id only — never a line of source
# text — modelled on tools/option_taxonomy.py's acquire-into-ephemeral-work-then-discard shape.
"""Measure the population risk R-2 leaves open, before the five-signal header rule is fixed.

research.md D1 designs a five-signal conjunction that refuses a datasheet's first composition row
when it is, among other things, a *total* of the rows that follow it (signal 4: its count equals
the sum of their maxima). D8's R-2 is **UNVERIFIED**: does the unit-size-header shape (a first row
whose ``min_count == max_count``) ever occur on a card where the successor rows do **not** sum to
it — an arithmetic mismatch that would leave a genuine phantom-header row unrefused?

This tool measures the population directly, without deciding any single row's fate::

    python tools/header_refusal_population.py                                       # live
    python tools/header_refusal_population.py --fixtures fixtures/minimal --offline  # rehearsal

**What it does not do.** It does not implement T030's five-signal rule (only signals 1, 2, and 3
are needed to find a "header candidate" here — first row, at least one successor, fixed count —
signals 4 and 5 are what this tool exists to *measure the population of*, not to apply as a
refusal). It never modifies ``data/`` and never reads or writes ``curation/composition-
overrides.json``; it is a measurement, not a fix.

**No source text anywhere.** Only integers and datasheet ids reach the report — a datasheet id is
an identifier the pipeline already assigns and publishes, not a fragment of publisher prose, the
same standard :mod:`tools.option_taxonomy` and :mod:`tools.item_constraint_taxonomy` hold
themselves to.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from pipeline.acquire.detail_source import acquire_detail, read_detail
from pipeline.acquire.http import AcquisitionError
from pipeline.config import ConfigError, PipelineConfig, load_config, repo_root
from pipeline.exit_codes import ExitCode
from pipeline.parse.composition_grammar import CompositionParse, parse_entry
from pipeline.workspace import workspace

PROG: Final = "header_refusal_population.py"

#: Where the measurement lands. Its own directory, distinct from ``option-taxonomy/`` and
#: ``footnote-restriction-taxonomy/``.
REPORTS_DIR: Final = Path("reports") / "header-refusal-population"

_COMPOSITION_TABLE: Final = "Datasheets_unit_composition.csv"


@dataclass(frozen=True, slots=True)
class HeaderPopulationReport:
    """The whole measurement: counts and datasheet ids, never a line of source text."""

    generated_at: str
    mode: str
    edition: str
    source: str
    datasheets_with_composition: int
    header_candidates: int
    summing: int
    non_summing: int
    non_summing_datasheet_ids: tuple[str, ...] = field(default_factory=tuple)
    summing_datasheet_ids: tuple[str, ...] = field(default_factory=tuple)

    @property
    def non_summing_share(self) -> float:
        return self.non_summing / self.header_candidates if self.header_candidates else 0.0


def measure(
    config: PipelineConfig,
    *,
    repository_root: Path,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    generated_at: datetime | None = None,
) -> HeaderPopulationReport:
    """Acquire, classify, discard — and return only counts and datasheet ids.

    Every acquired string lives inside the ``with workspace(...)`` block and is resolved to a
    count there; what comes back out is integers and ids the pipeline already publishes.
    """
    datasheets_with_composition = 0
    header_candidates = 0
    summing_ids: list[str] = []
    non_summing_ids: list[str] = []

    with workspace(repository_root) as work:
        acquisition, payloads = acquire_detail(
            config, fixtures_dir=fixtures_dir, offline=offline, workspace=work
        )
        source = acquisition.source_base_url
        tables = read_detail(config, payloads)

        composition = tables.get(_COMPOSITION_TABLE)
        if composition is not None:
            grouped = composition.grouped_by("datasheet_id")
            for datasheet_id, rows in grouped.items():
                if not datasheet_id:
                    continue
                ordered = sorted(rows, key=lambda row: _line(row.fields.get("line", "")))
                parsed = [parse_entry(row.fields.get("description", "")) for row in ordered]
                if all(entry is None for entry in parsed):
                    continue
                datasheets_with_composition += 1

                outcome = classify_datasheet(parsed)
                if outcome in ("not_a_candidate", "successor_unresolved"):
                    continue
                header_candidates += 1
                if outcome == "sums":
                    summing_ids.append(datasheet_id)
                else:
                    non_summing_ids.append(datasheet_id)

    moment = (generated_at or datetime.now(UTC)).astimezone(UTC)
    return HeaderPopulationReport(
        generated_at=moment.isoformat().replace("+00:00", "Z"),
        mode=config.detail_acquisition_mode.value,
        edition=config.detail_edition,
        source=source,
        datasheets_with_composition=datasheets_with_composition,
        header_candidates=header_candidates,
        summing=len(summing_ids),
        non_summing=len(non_summing_ids),
        non_summing_datasheet_ids=tuple(sorted(non_summing_ids)),
        summing_datasheet_ids=tuple(sorted(summing_ids)),
    )


def _line(raw: str) -> int:
    try:
        return int(raw)
    except ValueError:
        return 0


def classify_datasheet(parsed: Sequence[CompositionParse | None]) -> str:
    """One datasheet's ordered composition rows, classified as a header-population question.

    ``"not_a_candidate"`` — no rows resolved, fewer than two rows, or the first row is not a
    fixed count (signals 1-3 of research D1's five-signal rule are not all present).
    ``"successor_unresolved"`` — the first row is a candidate but a successor did not resolve, so
    the sum is undefined; excluded from both buckets rather than guessed into either.
    ``"sums"`` / ``"non_sums"`` — the candidate's count does or does not equal the sum of its
    resolved successors' maxima (signal 4, the population this tool exists to measure).

    A pure function over already-parsed rows so it can be tested without going through
    acquisition — the same separation :func:`pipeline.parse.options_grammar.classify` (via
    ``tools/option_taxonomy.py``) keeps between parsing and classification.
    """
    if len(parsed) < 2:
        return "not_a_candidate"
    first, *rest = parsed
    if first is None or first.min_count != first.max_count:
        return "not_a_candidate"
    if any(entry is None for entry in rest):
        return "successor_unresolved"
    successor_sum = sum(entry.max_count for entry in rest if entry is not None)
    return "sums" if first.max_count == successor_sum else "non_sums"


def render(report: HeaderPopulationReport) -> str:
    """The measurement as Markdown. Counts and datasheet ids only — never a description field."""
    lines = [
        "<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Generated by "
        "tools/header_refusal_population.py (007 T004). -->",
        "# Unit-size-header non-summing population (risk R-2)",
        "",
        f"- Generated: `{report.generated_at}`",
        f"- Detail acquisition mode: `{report.mode}`",
        f"- Declared detail edition: `{report.edition}`",
        f"- Source: `{report.source}`",
        "",
        "**Non-destructive, and text-free.** Nothing under `data/`, `curation/`, or `state/` was "
        "written, the acquired pages were discarded with `work/` when the run ended, and no "
        "composition description reaches this page — only counts and the pipeline's own "
        "datasheet ids.",
        "",
        "## Header candidates",
        "",
        "A header candidate is a datasheet's first composition row where `min_count == max_count` "
        "and at least one row follows it — signals 1-3 of research D1's five-signal rule. This "
        "tool measures signal 4 (does the count equal the sum of the successors' maxima) over "
        "every candidate; it does not apply signal 5 (name resolves to no model) and refuses "
        "nothing.",
        "",
        "| Datasheets with composition | Header candidates | Sums to successors | Does NOT sum |",
        "|---:|---:|---:|---:|",
        f"| {report.datasheets_with_composition} | {report.header_candidates} | "
        f"{report.summing} | **{report.non_summing}** |",
        "",
        f"Non-summing share of candidates: {report.non_summing_share:.1%}",
        "",
        "## Reading this",
        "",
        "- **`non_summing == 0` confirms R-2's safe direction holds over this corpus**: every "
        "header-shaped first row this tool found is also a total of its successors, so T030's "
        "signal 4 does not under-refuse a genuine phantom row it should catch.",
        "- **A non-zero `non_summing` count is not evidence of a defect in T030.** research D8 "
        "R-2 already accepts this as the correct failure direction: such a row is simply not "
        "refused and ships as it does today, which under-delivers rather than over-refuses. It "
        "sizes how large that residual is, nothing more.",
        "- Ids are listed below for **review**, never as a re-derivation prompt: T030's own "
        "signal 5 (name resolution) and human review are what decide each one, not this tool.",
        "",
        "### Non-summing datasheet ids",
        "",
    ]
    if report.non_summing_datasheet_ids:
        lines.extend(f"- `{ds_id}`" for ds_id in report.non_summing_datasheet_ids)
    else:
        lines.append("*(none)*")
    lines.append("")
    return "\n".join(lines)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Measure the population of unit-size-header candidates whose successors do not sum "
            "to them (risk R-2), retaining no source text."
        ),
    )
    parser.add_argument("--fixtures", type=Path, help="source from a synthetic fixture set")
    parser.add_argument(
        "--offline", action="store_true", help="refuse network access; requires --fixtures"
    )
    parser.add_argument(
        "--out", type=Path, help="report path (default reports/header-refusal-population/<date>.md)"
    )
    parser.add_argument("--repo", type=Path, help="repository root (default: this checkout)")
    parser.add_argument(
        "--print-only", action="store_true", help="render to stdout and write no file"
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _summary_line(report: HeaderPopulationReport) -> str:
    return (
        f"{PROG}: {report.header_candidates} header candidates over "
        f"{report.datasheets_with_composition} datasheets; {report.summing} sum, "
        f"{report.non_summing} do not ({report.non_summing_share:.1%})"
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
