#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the line-scoped wargear-option
# measurement tool (pipeline PR P3 task 1): counts only, never a row, a name, or a sentence,
# modelled on tools/equipment_taxonomy.py's acquire-into-ephemeral-work/-then-discard shape. The
# seventh figure G (`with_subject_plural_line`) was added on the controller's 2026-10-09 ruling
# after a failing-first run against the brief's literal synthetic fixture showed the pipeline's
# own `normalize_name` deliberately does no singularisation, so an exact-equality B/C split alone
# could not distinguish a genuine "no matching line" from a plural/singular naming gap.
"""Measure, before any production, how much of the equipment/option residual is line-scoped.

Seven counts, and nothing else leaves this process:

* **A** `with_subjects` — refused (`EQP-UNPARSED`) equipment sentences whose subject (the text
  before the `is`/`are equipped with:` marker, a leading `Every`/`Each`/`The` stripped) contains
  the word "with".
* **B** `with_subject_exact_line` — of A, the subject's normalised form equals exactly one
  composition-line name of the same datasheet.
* **C** `with_subject_no_line` — of A, equals no line exactly. (A subject matching two or more
  lines exactly counts in neither B nor C — an ambiguous exact match is not evidence either way.)
* **D** `exact_name_shadowed` — in a curated tree, equipment groups with `composition_line None`
  whose `model_name` normalises EQUAL to exactly one composition-line name of the same datasheet.
* **E** `n_models_can_stems` — option rows `options_grammar.parse_row` resolves to scope UNIT with
  both `eligible_max_count` and `eligible_model_name` absent, whose pre-passed stem matches
  ``^(\\d+) models? can\\b``.
* **F** `line_scope_candidates` — in a curated tree, option groups with >= 1 `REPLACED` item, on
  datasheets with >= 1 line-resolved equipment group.
* **G** `with_subject_plural_line` (controller ruling, 2026-10-09, measurement-only) — of C,
  subjects that equal exactly one composition-line name once a single trailing "s" is dropped
  from every word on BOTH sides, after `normalize_name`. This is sized, never produced: the
  private helper that does it is documented as measurement-only and must never be imported by
  anything under `pipeline/`. It exists solely to tell "no line at all" (true C) apart from "the
  line is there, spelled with the source's own singular/plural pair" (the fraction of C this
  figure reports), without changing what `pipeline.normalize.names.normalize_name` does anywhere
  else.

Usage::

    python -m tools.line_scope_taxonomy --fixtures fixtures/minimal --offline --out <dir> \\
        --edition-dir data/wh40k-11e                                    # rehearsal
    python -m tools.line_scope_taxonomy --out <dir> --edition-dir data/wh40k-11e  # live

Four properties, on the same terms `tools/equipment_taxonomy.py` holds itself to:

* **It uses the pipeline's own parse paths** — `equipment_grammar.parse_sentence`,
  `composition_grammar.parse_entry`, `options_grammar.parse_row` — never a second idea of what
  resolves.
* **The acquired text is discarded** inside its own ``with workspace(...)`` block.
* **No source text reaches the output.** Not a sentence, not a subject, not a model or item name.
* **It writes nothing but its own JSON file.**
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from re import IGNORECASE, Pattern
from re import compile as re_compile
from typing import Final

from pipeline.acquire.detail_source import acquire_detail, read_detail
from pipeline.acquire.export_rows import OPTIONS_TABLE
from pipeline.acquire.http import AcquisitionError
from pipeline.config import ConfigError, PipelineConfig, load_config, repo_root
from pipeline.curate.prior import previous_published_version, read_curated_tree
from pipeline.exit_codes import ExitCode
from pipeline.models.curated import CuratedSnapshot, OptionItemRole, OptionScope
from pipeline.models.source import SourceAcquisition
from pipeline.normalize.names import normalize_name
from pipeline.parse.composition_grammar import parse_entry, pre_pass
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE, parse_sentence
from pipeline.parse.options_grammar import parse_row, split_sublist
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.workspace import workspace

PROG: Final = "line_scope_taxonomy.py"

#: The export does not publish `Datasheets_unit_composition.csv` under a public table-name
#: constant anywhere (`pipeline/validate/equivalence.py` keeps its own private copy of this exact
#: string, `_COMPOSITION_TABLE`, for the identical reason: no module below `acquire` exports one).
_COMPOSITION_TABLE: Final = "Datasheets_unit_composition.csv"

#: A refused equipment sentence's subject containing "with" — the brief's own literal pattern,
#: not reused from `equipment_grammar._REFUSED` (private) and not case-insensitive, matching the
#: interface exactly as dispatched.
_WITH: Final[Pattern[str]] = re_compile(r"\bwith\b")

#: A single leading article/demonstrative stripped from a sentence's raw subject, mirroring the
#: informal rule `equipment_grammar._SUBJECTS` encodes as separate productions (`Every`/`The`/
#: `Each`) — restated here because this tool reads the *refused* tail those productions never see.
_LEADING: Final[Pattern[str]] = re_compile(r"^(?:every|each|the)\s+", IGNORECASE)

#: Figure E's stem shape: a leading count followed by "model(s) can".
_N_MODELS_CAN: Final[Pattern[str]] = re_compile(r"^(\d+)\s+models?\s+can\b", IGNORECASE)

#: The sentence-level marker, restated rather than imported: this tool calls no private symbol of
#: `equipment_grammar` (its own module docstring makes the same choice), and `_MARKER` is one.
#: Kept byte-identical to that module's own pattern; a divergence here is exactly the
#: `diagnostic_mismatch`-shaped bug `tools/equipment_taxonomy.py`'s own comment on this point
#: already names, with nothing but a future reviewer to catch it.
_EQUIPMENT_MARKER: Final[Pattern[str]] = re_compile(
    r"\b(?:is|are)\s+equipped\s+with\s*:", IGNORECASE
)

OUTPUT_FILENAME: Final = "line-scope-taxonomy.json"


@dataclass(frozen=True, slots=True)
class LineScopeFigures:
    """The whole measurement: seven integers, and only those."""

    with_subjects: int
    with_subject_exact_line: int
    with_subject_no_line: int
    exact_name_shadowed: int
    n_models_can_stems: int
    line_scope_candidates: int
    with_subject_plural_line: int

    def as_dict(self) -> dict[str, int]:
        return asdict(self)


def _exact_match_count(subject: str, line_names: Sequence[str]) -> int:
    """How many of `line_names` normalise EQUAL to `subject`. 0, 1, or 2+ — the caller decides."""
    needle = normalize_name(subject)
    if not needle:
        return 0
    return sum(1 for name in line_names if normalize_name(name) == needle)


def _drop_trailing_s(value: str) -> str:
    """Drop one trailing "s" from every word of an ALREADY-NORMALISED name.

    **Measurement-only — never a production, never imported by `pipeline/`.** The controller's
    2026-10-09 ruling authorises this one narrow comparison for figure G alone, specifically
    because `pipeline.normalize.names.normalize_name` does no singularisation by design (its own
    module docstring: "No stemming, no singularisation, no synonym expansion... those would fold
    [different things] closer together"), and that design stays unchanged in production. This
    helper exists only so this tool can size how much of the "no exact line" residual is really a
    source-stated singular/plural pair (`Test Trooper` vs. `4 Test Troopers`) rather than a
    genuinely absent line — the figure that decides whether Task 2 is worth writing at all.
    """
    return " ".join(
        word[:-1] if len(word) > 1 and word.endswith("s") else word for word in value.split()
    )


def _plural_relaxed_match_count(subject: str, line_names: Sequence[str]) -> int:
    """`_exact_match_count`'s sibling, under `_drop_trailing_s` on both sides. Measurement only."""
    needle = _drop_trailing_s(normalize_name(subject))
    if not needle:
        return 0
    return sum(1 for name in line_names if _drop_trailing_s(normalize_name(name)) == needle)


def _composition_line_names(rows: CsvReadResult | None) -> dict[str, list[str]]:
    """`datasheet_id -> [parsed composition-line model_name, ...]`, in file order.

    A row `parse_entry` cannot resolve contributes no name — the same "report, never guess" rule
    `curate/assemble.py` already applies when it builds `CuratedCompositionEntry` rows from this
    same table.
    """
    if rows is None:
        return {}
    names: dict[str, list[str]] = {}
    for datasheet_id, group in rows.grouped_by("datasheet_id").items():
        resolved: list[str] = []
        for row in group:
            parsed = parse_entry(row.fields.get("description", ""))
            if parsed is not None:
                resolved.append(parsed.model_name)
        names[datasheet_id] = resolved
    return names


def measure_tables(tables: Mapping[str, CsvReadResult]) -> tuple[int, int, int, int, int]:
    """A, B, C, E, G — in that order — from the acquired tables.

    Every acquired description is read and discarded in the same pass; nothing but the five
    counts below is retained.
    """
    with_subjects = 0
    exact_line = 0
    no_line = 0
    n_models_can = 0
    plural_line = 0

    line_names_by_datasheet = _composition_line_names(tables.get(_COMPOSITION_TABLE))

    equipment_rows = tables.get(EQUIPMENT_TABLE)
    if equipment_rows is not None:
        for row in equipment_rows.rows:
            description = row.fields.get("description", "")
            if parse_sentence(description) is not None:
                continue  # resolved; outside this residual entirely

            text = pre_pass(description, field="equipment.description")
            marker = _EQUIPMENT_MARKER.search(text)
            if marker is None:
                continue  # not an equipment sentence at all

            subject = _LEADING.sub("", text[: marker.start()].strip())
            if _WITH.search(subject) is None:
                continue
            with_subjects += 1

            line_names = line_names_by_datasheet.get(row.fields.get("datasheet_id", ""), [])
            matches = _exact_match_count(subject, line_names)
            if matches == 1:
                exact_line += 1
            elif matches == 0:
                no_line += 1
                if _plural_relaxed_match_count(subject, line_names) == 1:
                    plural_line += 1
            # matches >= 2: ambiguous, counted in neither B nor C (and never eligible for G).

    options_rows = tables.get(OPTIONS_TABLE)
    if options_rows is not None:
        for row in options_rows.rows:
            description = row.fields.get("description", "")
            resolved = parse_row(description)
            if resolved is None:
                continue
            if resolved.scope is not OptionScope.UNIT:
                continue
            if resolved.eligible_max_count is not None or resolved.eligible_model_name is not None:
                continue
            stem_raw, _items = split_sublist(description)
            stem = pre_pass(stem_raw, field="option.description")
            if _N_MODELS_CAN.match(stem) is not None:
                n_models_can += 1

    return with_subjects, exact_line, no_line, n_models_can, plural_line


def measure_tree(snapshot: CuratedSnapshot) -> tuple[int, int]:
    """D, F — from a curated tree (the last published `data/<edition>/`)."""
    shadowed = 0
    candidates = 0

    for sheet in snapshot.datasheets:
        line_names = [entry.model_name for entry in sheet.composition]

        for group in sheet.equipment_groups:
            if group.composition_line is not None or group.model_name is None:
                continue
            if _exact_match_count(group.model_name, line_names) == 1:
                shadowed += 1

        if not any(group.composition_line is not None for group in sheet.equipment_groups):
            continue  # F requires >= 1 line-resolved equipment group on this datasheet

        replaced_group_ids = {
            choice.group_id
            for choice in sheet.option_choices
            for item in choice.items
            if item.role is OptionItemRole.REPLACED
        }
        candidates += sum(1 for group in sheet.option_groups if group.id in replaced_group_ids)

    return shadowed, candidates


def measure(
    config: PipelineConfig,
    *,
    repository_root: Path,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    edition_dir: Path | None = None,
) -> tuple[LineScopeFigures, SourceAcquisition]:
    """Acquire, classify, discard — and hand back the one `SourceAcquisition` alongside the
    figures, so `main` can cite its own `retrieved_at` without a second acquisition.

    Adaptation from the brief's literal `-> LineScopeFigures` signature (common-rules: adapt call
    shapes to what exists, list the adaptation): the figures carry no provenance of their own, and
    acquiring the detail source a second time would reach the network twice on a live run.
    """
    with workspace(repository_root) as work:
        acquisition, payloads = acquire_detail(
            config, fixtures_dir=fixtures_dir, offline=offline, workspace=work
        )
        tables = read_detail(payloads)
        with_subjects, exact_line, no_line, n_models_can, plural_line = measure_tables(tables)

    data_dir = (
        edition_dir if edition_dir is not None else repository_root / "data" / config.detail_edition
    )
    snapshot = read_curated_tree(data_dir)
    shadowed, candidates = measure_tree(snapshot) if snapshot is not None else (0, 0)

    figures = LineScopeFigures(
        with_subjects=with_subjects,
        with_subject_exact_line=exact_line,
        with_subject_no_line=no_line,
        exact_name_shadowed=shadowed,
        n_models_can_stems=n_models_can,
        line_scope_candidates=candidates,
        with_subject_plural_line=plural_line,
    )
    return figures, acquisition


def _tool_commit(root: Path) -> str:
    """This checkout's own HEAD commit, or `"unknown"` when it cannot be read.

    Never raises: a tmp-path test fixture outside any git checkout, or an environment with no
    `git` on PATH, degrades to the one value no reader could mistake for a real commit.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except OSError:
        return "unknown"
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and commit else "unknown"


def _summary_line(figures: LineScopeFigures) -> str:
    return (
        f"{PROG}: with_subjects={figures.with_subjects} "
        f"with_subject_exact_line={figures.with_subject_exact_line} "
        f"with_subject_no_line={figures.with_subject_no_line} "
        f"exact_name_shadowed={figures.exact_name_shadowed} "
        f"n_models_can_stems={figures.n_models_can_stems} "
        f"line_scope_candidates={figures.line_scope_candidates} "
        f"with_subject_plural_line={figures.with_subject_plural_line}"
    )


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Measure the line-scoped wargear-option residual, retaining nothing but "
        "seven integers.",
    )
    parser.add_argument("--fixtures", type=Path, help="source from a synthetic fixture set")
    parser.add_argument(
        "--offline", action="store_true", help="refuse network access; requires --fixtures"
    )
    parser.add_argument(
        "--out", type=Path, help=f"output directory (default reports/{OUTPUT_FILENAME!r})"
    )
    parser.add_argument("--repo", type=Path, help="repository root (default: this checkout)")
    parser.add_argument(
        "--edition-dir", type=Path, help="curated tree directory (default data/<detail_edition>)"
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    root = args.repo or repo_root()

    try:
        config = load_config()
        figures, acquisition = measure(
            config,
            repository_root=root,
            fixtures_dir=args.fixtures,
            offline=args.offline,
            edition_dir=args.edition_dir,
        )
    except ConfigError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(ExitCode.CONFIG_ERROR)
    except AcquisitionError as exc:
        print(f"{PROG}: {exc}", file=sys.stderr)
        return int(exc.exit_code)

    document = {
        "figures": figures.as_dict(),
        "rules_version_id": previous_published_version(root / "site" / "manifest.json"),
        "acquired_at": acquisition.retrieved_at,
        "tool_commit": _tool_commit(root),
    }

    out_dir = args.out or (root / "reports" / "line-scope-taxonomy")
    out_dir.mkdir(parents=True, exist_ok=True)
    destination = out_dir / OUTPUT_FILENAME
    destination.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{PROG}: wrote {destination}")
    print(_summary_line(figures))
    return int(ExitCode.SUCCESS)


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
