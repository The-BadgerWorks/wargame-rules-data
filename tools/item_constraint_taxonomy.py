#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the footnote-restriction-
# arrival-path classifier (007 task T002): acquire the detail source in the configured mode into
# an ephemeral work/, run every row of the options, composition, and equipment grammars' own
# residuals through a structural classifier, and report per-class counts — retaining no source
# text anywhere, modelled directly on tools/option_taxonomy.py's acquire-into-ephemeral-work-
# then-discard shape (006 task T001/T002).
"""Classify where a footnote-style item restriction arrives, before its vocabulary is fixed.

research.md D4.2 found that the restriction sentence a footnote marker points at is not part of
the marked item's own line — it is refused today, wherever it lands, and dropped on the floor.
What is **UNVERIFIED** is whether it lands *only* in the options grammar's own refusal lists
(``_REFUSED`` / ``_EXTENDED_REFUSED`` in :mod:`pipeline.parse.options_grammar`), or whether a
second arrival path exists inside the composition or equipment residual too (risk R-J).

This tool answers the question structurally, without ever deciding it by reading a sentence::

    python tools/item_constraint_taxonomy.py                                       # live
    python tools/item_constraint_taxonomy.py --fixtures fixtures/minimal --offline  # rehearsal

**Method.** Every row of all three grammars' source tables is fed through the pipeline's own
parse functions (:func:`pipeline.parse.options_grammar.parse_row`,
:func:`pipeline.parse.composition_grammar.parse_entry`,
:func:`pipeline.parse.equipment_grammar.parse_sentence`). A row that resolves is not a candidate —
it is already correctly something else. A row that does **not** resolve is diagnosed by *which
internal step* refused it, using the grammar's own private control-flow functions directly (never
a re-implementation that could quietly drift from the real one), and separately tagged with two
purely structural signals that never quote or retain the row's text:

* **negation-shaped** — the normalised stem matches a generic negation cue (``cannot``,
  ``must not``, ``no more than``) — the shape ``not_replaceable`` would take.
* **cardinality-shaped** — the normalised stem matches a generic per-unit/per-model cardinality
  cue (``only one``, ``once per``, ``one per unit``) — the shape ``one_per_unit`` would take.

Neither signal is drawn from any inspected source sentence; both are generic English phrasings
implied by the two vocabulary members `data-model.md` §1.1 already names
(``not_replaceable``, ``one_per_unit``). A row bearing either signal, inside a class this
classifier finds, is a **candidate** restriction row for T036/T039 to size against — never a
certainty, and this tool asserts nothing about what any row actually says.

**Four properties, matching ``option_taxonomy.py``'s own:**

* **It uses the pipeline's own parse path** for the resolve/does-not-resolve split on all three
  grammars, and the options grammar's own private refusal functions for the diagnosis, so a
  drifted copy of the regex tables can never be the reason a class over- or under-counts.
* **The acquired text is discarded.** It lives inside a workspace emptied on exit, whatever
  happens, and nothing but counts and booleans leaves this process.
* **No source text reaches the report.** Not a sentence, not a fragment, not an item name.
* **It writes nothing outside ``reports/footnote-restriction-taxonomy/``.**
"""

from __future__ import annotations

import argparse
import re
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
from pipeline.parse.composition_grammar import parse_entry, pre_pass
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE, parse_sentence
from pipeline.parse.options_grammar import (
    _EXTENDED_REFUSED,  # noqa: SLF001 - the ground truth this tool exists to diagnose against
    _FOOTNOTE_MARK,  # noqa: SLF001
    _REFUSED,  # noqa: SLF001
    _match_head,  # noqa: SLF001
    _match_verb,  # noqa: SLF001
    _parse_object,  # noqa: SLF001
    parse_row,
    split_sublist,
)
from pipeline.workspace import workspace

PROG: Final = "item_constraint_taxonomy.py"

#: Where the measurement lands. Its own directory, distinct from every run report and from
#: ``option-taxonomy/``, so a reviewer never mistakes this for either.
REPORTS_DIR: Final = Path("reports") / "footnote-restriction-taxonomy"

_OPTIONS_TABLE: Final = "Datasheets_options.csv"
_COMPOSITION_TABLE: Final = "Datasheets_unit_composition.csv"

_I: Final = re.IGNORECASE

#: Generic negation cue — the shape ``not_replaceable`` would take. Not drawn from any inspected
#: sentence: it is the plain-English phrasing the vocabulary member's own name implies.
_NEGATION_SIGNAL: Final = re.compile(
    r"\bcannot\b|\bcan\s+not\b|\bmust\s+not\b|\bno\s+more\s+than\b", _I
)

#: Generic cardinality cue — the shape ``one_per_unit`` would take.
_CARDINALITY_SIGNAL: Final = re.compile(
    r"\bonly\s+one\b|\bonce\s+per\b|\bone\s+per\s+(?:unit|model)\b", _I
)

#: The options-grammar diagnosis classes, in the order :func:`diagnose_option_row` can return
#: them. Disjoint: exactly one owns any given unparsed row.
OPTION_DIAGNOSIS_CLASSES: Final[tuple[str, ...]] = (
    "empty_stem",
    "refused_permissive_or_ratio",
    "refused_conditional_or_equipment_qualified",
    "no_head_match",
    "head_ok_no_verb",
    "verb_ok_item_invalid",
    "verb_ok_object_invalid",
    "diagnostic_mismatch",
)


def diagnose_option_row(description: str) -> str:
    """Which internal step of :func:`options_grammar.parse_row` refused this row.

    Mirrors ``parse_row``'s own control flow exactly, calling its private helpers directly rather
    than a second copy of its regex tables, so the diagnosis cannot silently drift from the
    grammar it describes. Only meaningful when ``parse_row(description)`` is already ``None``;
    ``"diagnostic_mismatch"`` is the defensive branch for a row this function's own mirroring
    disagrees with the real function about, which a live corpus run treats as a finding about
    this tool, not about the row.
    """
    stem_raw, item_raw = split_sublist(description)
    stem = pre_pass(stem_raw, field="option.description")
    if not stem:
        return "empty_stem"
    if any(pattern.search(stem) for pattern in _REFUSED):
        return "refused_permissive_or_ratio"

    matched_head = _match_head(stem)
    if matched_head is None:
        if any(pattern.search(stem) for pattern in _EXTENDED_REFUSED):
            return "refused_conditional_or_equipment_qualified"
        return "no_head_match"
    _head, head_end = matched_head

    verb, object_clause, _replaced_clause, _is_distributive = _match_verb(stem, head_end)
    if verb is None:
        return "head_ok_no_verb"

    if item_raw:
        for item in item_raw:
            choice = _parse_object(pre_pass(item, field="option.choice"), verb)
            if choice is None:
                return "verb_ok_item_invalid"
        return "diagnostic_mismatch"

    choice = _parse_object(object_clause, verb)
    if choice is None:
        return "verb_ok_object_invalid"
    return "diagnostic_mismatch"


def restriction_signal(stem: str) -> str:
    """``"negation"``, ``"cardinality"``, ``"both"``, or ``"neither"`` — never the text itself."""
    negation = _NEGATION_SIGNAL.search(stem) is not None
    cardinality = _CARDINALITY_SIGNAL.search(stem) is not None
    if negation and cardinality:
        return "both"
    if negation:
        return "negation"
    if cardinality:
        return "cardinality"
    return "neither"


@dataclass(frozen=True, slots=True)
class ConstraintTaxonomyReport:
    """The whole measurement: counts, and only counts."""

    generated_at: str
    mode: str
    edition: str
    source: str
    equipment_table_present: bool
    option_rows: int
    option_unparsed: int
    option_cells: dict[tuple[str, str], int] = field(default_factory=dict)
    option_marker_cells: dict[tuple[str, str], int] = field(default_factory=dict)
    option_parsed_but_signalled: dict[str, int] = field(default_factory=dict)
    composition_rows: int = 0
    composition_unresolved: int = 0
    composition_signal_counts: dict[str, int] = field(default_factory=dict)
    equipment_rows: int = 0
    equipment_unresolved: int = 0
    equipment_signal_counts: dict[str, int] = field(default_factory=dict)

    @property
    def option_unparsed_ratio(self) -> float:
        return self.option_unparsed / self.option_rows if self.option_rows else 0.0


def measure(
    config: PipelineConfig,
    *,
    repository_root: Path,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    generated_at: datetime | None = None,
) -> ConstraintTaxonomyReport:
    """Acquire, classify, discard — and return only counts and booleans.

    Every acquired string lives inside the ``with workspace(...)`` block and is classified there;
    what comes back out is integers and short class-key strings. That is the property that makes
    "no source text exists anywhere else" true rather than asserted.
    """
    option_cells: dict[tuple[str, str], int] = {}
    option_marker_cells: dict[tuple[str, str], int] = {}
    option_parsed_but_signalled: dict[str, int] = {"negation": 0, "cardinality": 0, "both": 0}
    composition_signal_counts: dict[str, int] = {
        "negation": 0,
        "cardinality": 0,
        "both": 0,
        "neither": 0,
    }
    equipment_signal_counts: dict[str, int] = dict(composition_signal_counts)

    option_rows = 0
    option_unparsed = 0
    composition_rows = 0
    composition_unresolved = 0
    equipment_rows = 0
    equipment_unresolved = 0
    equipment_table_present = False

    with workspace(repository_root) as work:
        acquisition, payloads = acquire_detail(
            config, fixtures_dir=fixtures_dir, offline=offline, workspace=work
        )
        source = acquisition.source_base_url
        tables = read_detail(config, payloads)

        options = tables.get(_OPTIONS_TABLE)
        if options is not None:
            for row in options.rows:
                description = row.fields.get("description", "")
                option_rows += 1
                parsed = parse_row(description)
                stem_raw, _items = split_sublist(description)
                stem = pre_pass(stem_raw, field="option.description")
                signal = restriction_signal(stem)

                if parsed is not None:
                    if signal != "neither":
                        option_parsed_but_signalled[signal] = (
                            option_parsed_but_signalled.get(signal, 0) + 1
                        )
                    continue

                option_unparsed += 1
                diagnosis = diagnose_option_row(description)
                cell = (diagnosis, signal)
                option_cells[cell] = option_cells.get(cell, 0) + 1
                if _FOOTNOTE_MARK.search(stem) is not None:
                    option_marker_cells[cell] = option_marker_cells.get(cell, 0) + 1

        composition = tables.get(_COMPOSITION_TABLE)
        if composition is not None:
            for row in composition.rows:
                description = row.fields.get("description", "")
                composition_rows += 1
                if parse_entry(description) is not None:
                    continue
                composition_unresolved += 1
                signal = restriction_signal(description)
                composition_signal_counts[signal] += 1

        equipment = tables.get(EQUIPMENT_TABLE)
        if equipment is not None:
            equipment_table_present = True
            for row in equipment.rows:
                description = row.fields.get("description", "")
                equipment_rows += 1
                if parse_sentence(description) is not None:
                    continue
                equipment_unresolved += 1
                signal = restriction_signal(description)
                equipment_signal_counts[signal] += 1

    moment = (generated_at or datetime.now(UTC)).astimezone(UTC)
    return ConstraintTaxonomyReport(
        generated_at=moment.isoformat().replace("+00:00", "Z"),
        mode=config.detail_acquisition_mode.value,
        edition=config.detail_edition,
        source=source,
        equipment_table_present=equipment_table_present,
        option_rows=option_rows,
        option_unparsed=option_unparsed,
        option_cells=option_cells,
        option_marker_cells=option_marker_cells,
        option_parsed_but_signalled=option_parsed_but_signalled,
        composition_rows=composition_rows,
        composition_unresolved=composition_unresolved,
        composition_signal_counts=composition_signal_counts,
        equipment_rows=equipment_rows,
        equipment_unresolved=equipment_unresolved,
        equipment_signal_counts=equipment_signal_counts,
    )


def _percent(part: int, whole: int) -> str:
    return f"{part / whole:.1%}" if whole else "—"


def render(report: ConstraintTaxonomyReport) -> str:
    """The measurement as Markdown. Counts only — never a sentence, never an item name."""
    lines = [
        "<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Generated by "
        "tools/item_constraint_taxonomy.py (007 T002/T003). -->",
        "# Footnote-restriction arrival-path taxonomy",
        "",
        f"- Generated: `{report.generated_at}`",
        f"- Detail acquisition mode: `{report.mode}`",
        f"- Declared detail edition: `{report.edition}`",
        f"- Source: `{report.source}`",
        "",
        "**Non-destructive, and text-free.** Nothing under `data/`, `curation/`, or `state/` was "
        "written, the acquired pages were discarded with `work/` when the run ended, and no "
        "source sentence, fragment, or item name appears on this page. It carries counts and "
        "structural booleans only.",
        "",
        "## Options grammar — unparsed rows, by diagnosis and restriction signal",
        "",
        "Diagnosis is exact: it calls the options grammar's own private refusal/head/verb/object "
        "functions directly, never a second copy of their patterns. Restriction signal is a "
        "generic negation or cardinality cue implied by the two vocabulary members "
        "(`not_replaceable`, `one_per_unit`) — never drawn from an inspected sentence, and never "
        "a claim about what any row actually says.",
        "",
        "| Options rows | Unparsed | Share unparsed |",
        "|---:|---:|---:|",
        f"| {report.option_rows} | {report.option_unparsed} | {report.option_unparsed_ratio:.1%} |",
        "",
        "| Diagnosis | Signal | Rows | Of which carry a footnote marker |",
        "|---|---|---:|---:|",
    ]
    for diagnosis in OPTION_DIAGNOSIS_CLASSES:
        for signal in ("negation", "cardinality", "both", "neither"):
            count = report.option_cells.get((diagnosis, signal), 0)
            if count == 0:
                continue
            marker = report.option_marker_cells.get((diagnosis, signal), 0)
            lines.append(f"| `{diagnosis}` | {signal} | {count} | {marker} |")

    lines += [
        "",
        "**Rows that DID parse but still carry a restriction signal** — a sanity check: a row a "
        "baseline production already resolves is not a constraint candidate, and a non-zero count "
        "here is a class T039's vocabulary match must not steal from an already-correct option.",
        "",
        "| Signal | Rows |",
        "|---|---:|",
    ]
    for signal in ("negation", "cardinality", "both"):
        lines.append(f"| {signal} | {report.option_parsed_but_signalled.get(signal, 0)} |")

    lines += [
        "",
        "## Composition grammar's own residual (`CMP-UNRESOLVED`)",
        "",
        "Tests the same two signals against every composition row the grammar does not resolve — "
        "the first of D4.2's two candidate second arrival paths.",
        "",
        "| Composition rows | Unresolved | Share unresolved |",
        "|---:|---:|---:|",
        f"| {report.composition_rows} | {report.composition_unresolved} | "
        f"{_percent(report.composition_unresolved, report.composition_rows)} |",
        "",
        "| Signal | Rows |",
        "|---|---:|",
    ]
    for signal in ("negation", "cardinality", "both", "neither"):
        lines.append(f"| {signal} | {report.composition_signal_counts.get(signal, 0)} |")

    lines += [
        "",
        "## Equipment grammar's own residual (`EQP-UNPARSED`)",
        "",
        f"- Equipment table present in this run: `{report.equipment_table_present}` (absent under "
        "`csv` mode — data-model.md §3's fourth state, not a defect of this run)",
        "",
        "| Equipment rows | Unresolved | Share unresolved |",
        "|---:|---:|---:|",
        f"| {report.equipment_rows} | {report.equipment_unresolved} | "
        f"{_percent(report.equipment_unresolved, report.equipment_rows)} |",
        "",
        "| Signal | Rows |",
        "|---|---:|",
    ]
    for signal in ("negation", "cardinality", "both", "neither"):
        lines.append(f"| {signal} | {report.equipment_signal_counts.get(signal, 0)} |")

    lines += [
        "",
        "## Reading this",
        "",
        "- **A row's presence here is a candidate, never a certainty.** Only a human vocabulary "
        "match (T039) or a curator can say what a row actually states; this tool tests structural "
        "shape only.",
        "- **If every restriction-signalled row lands under the options grammar's own diagnosis "
        "classes, and the composition/equipment residual tables both carry a `neither`-only "
        "signal distribution, R-J is confirmed**: every footnote-style restriction arrives as a "
        "refused option row, and T036's constraint vocabulary needs no second production site.",
        "- **A non-zero negation/cardinality count in either residual table is the opposite "
        "finding**: a second arrival path exists, and T039's production must be added there too.",
        "- `diagnostic_mismatch` should be zero on every run. A non-zero count means this tool's "
        "mirroring of `parse_row`'s control flow has drifted from the real function and needs "
        "fixing before its counts are trusted.",
        "",
    ]
    return "\n".join(lines)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            "Classify where a footnote-style item restriction arrives, retaining no source text."
        ),
    )
    parser.add_argument("--fixtures", type=Path, help="source from a synthetic fixture set")
    parser.add_argument(
        "--offline", action="store_true", help="refuse network access; requires --fixtures"
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="report path (default reports/footnote-restriction-taxonomy/<date>.md)",
    )
    parser.add_argument("--repo", type=Path, help="repository root (default: this checkout)")
    parser.add_argument(
        "--print-only", action="store_true", help="render to stdout and write no file"
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def _summary_line(report: ConstraintTaxonomyReport) -> str:
    return (
        f"{PROG}: {report.option_unparsed} of {report.option_rows} option rows unparsed "
        f"({report.option_unparsed_ratio:.1%}); composition residual "
        f"{report.composition_unresolved}/{report.composition_rows}; equipment residual "
        f"{report.equipment_unresolved}/{report.equipment_rows}"
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
