#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the equipment-sentence taxonomy
# classifier (008 task T002), modelled directly on tools/option_taxonomy.py's acquire-into-
# ephemeral-work/-then-discard shape: classify every EQP-UNPARSED sentence's subject by which
# `equipment_grammar.py::_REFUSED` pattern rejected it (or that it reached `_SUBJECTS` and matched
# none), collapse to card shapes, and write reports/equipment-taxonomy/<date>.md — retaining no
# source text anywhere. Retires risk R-H; the `One`/`INT`/`A`-subject count is the number Open
# Decision O1 turns on.
"""Re-derive the equipment-sentence residual's shape, before Open Decision O1 is decided.

`006` research D1e sized the equipment tail once, against the cached ~81% sample the whole `006`
campaign was measured against (the same sample risk `tools/option_taxonomy.py`'s own module
docstring names for the option side — this tool is that same confirm-or-contradict step, for the
sibling grammar). This tool re-derives it against a corpus the candidate itself acquired::

    python tools/equipment_taxonomy.py                              # live, configured source
    python tools/equipment_taxonomy.py --fixtures fixtures/minimal --offline  # rehearsal

Four properties, on the same terms `tools/option_taxonomy.py` holds itself to:

* **It uses the pipeline's own parse path.** Every sentence is resolved by
  :func:`pipeline.parse.equipment_grammar.parse_sentence`. A classifier with its own idea of what
  fails to parse would measure itself.
* **The acquired text is discarded** inside its own ``with workspace(...)`` block; nothing but
  counts and structural class labels leaves this process.
* **No source text reaches the report.** Not a sentence, not a fragment, not a model or item name.
* **It writes nothing outside ``reports/equipment-taxonomy/``.**

**Classification is disjoint and ordered**, mirroring :func:`pipeline.parse.equipment_grammar.
_match_subject`'s own control flow exactly — this tool calls no private function of that module
(unlike ``tools/item_constraint_taxonomy.py``'s options-side diagnosis) because the equipment
grammar's refusal shape is simple enough to classify from the subject string alone, by the same
patterns `_REFUSED` uses, in the same order.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from pipeline.acquire.detail_source import acquire_detail, read_detail
from pipeline.acquire.http import AcquisitionError
from pipeline.config import ConfigError, PipelineConfig, load_config, repo_root
from pipeline.curate.prior import previous_published_version, read_curated_tree
from pipeline.exit_codes import ExitCode
from pipeline.models.curated import CuratedSnapshot, DefaultEquipmentState
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE, parse_sentence
from pipeline.workspace import workspace

PROG: Final = "equipment_taxonomy.py"

#: Its own directory, on the same "never `reports/candidate/`" terms as the options taxonomy.
REPORTS_DIR: Final = Path("reports") / "equipment-taxonomy"

#: The classes, in the fixed order `equipment_grammar._REFUSED` tries them — disjoint, so the
#: per-class counts sum to the residual. Named after the shape each one names, not after the
#: pattern, so a reader does not need the grammar module open to follow the report.
_EQUIPMENT_QUALIFIED: Final = re.compile(r"\bwith\b", re.IGNORECASE)
_SUBSET_ONE: Final = re.compile(r"^One\s", re.IGNORECASE)
_SUBSET_A: Final = re.compile(r"^A[n]?\s", re.IGNORECASE)
_SUBSET_INT: Final = re.compile(r"^\d")
_CONDITIONAL_WORD: Final = re.compile(r"^(?:For every|If|Unless|Up to)\b", re.IGNORECASE)
_CONDITIONAL_COMMA: Final = re.compile(r",")

#: The sentence-level marker, restated rather than imported: this tool calls no private symbol of
#: `equipment_grammar` (module docstring), and `_MARKER` is one. Kept byte-identical to that
#: module's own pattern; a divergence would be a `diagnostic_mismatch`-shaped bug with nothing to
#: catch it, so this is the one place a future edit to that pattern must be mirrored by hand.
_MARKER: Final = re.compile(r"\b(?:is|are)\s+equipped\s+with\s*:", re.IGNORECASE)

#: Class key -> label, in report order. O1's own table names the first three by these labels.
CLASS_LABELS: Final[Mapping[str, str]] = {
    "equipment_qualified": "Equipment-qualified subject — `Every [MODEL] with [ITEM] …`",
    "subset_one": "Subset subject, `One [MODEL] …` (O1)",
    "subset_a": "Subset subject, `A`/`An [MODEL] …` (O1)",
    "subset_int": "Subset subject, `INT [MODEL] …` (O1)",
    "conditional": "Conditional or distributive subject — `For every`/`If`/`Unless`/`Up to`/`,`",
    "no_marker": "No `is`/`are equipped with:` marker at all (not an equipment sentence)",
    "empty_items": "Marker present, item list empty",
    "subject_unmatched": "Reached `_SUBJECTS` and matched no production (the residual's own tail)",
}


def classify_subject(subject: str) -> str:
    """Which class owns this refused subject — mirrors `_match_subject`'s own control flow.

    Only meaningful for a subject :func:`pipeline.parse.equipment_grammar.parse_sentence` already
    returned `None` for. Order matches `_REFUSED` exactly: an equipment qualifier is checked
    before a subset word, because `Every Trooper with a lantern` would otherwise present as an
    unnamed subject shape rather than the equipment-qualified one it is.
    """
    if not subject:
        return "subject_unmatched"
    if _EQUIPMENT_QUALIFIED.search(subject) is not None:
        return "equipment_qualified"
    if _SUBSET_ONE.match(subject) is not None:
        return "subset_one"
    if _SUBSET_A.match(subject) is not None:
        return "subset_a"
    if _SUBSET_INT.match(subject) is not None:
        return "subset_int"
    if _CONDITIONAL_WORD.match(subject) is not None or _CONDITIONAL_COMMA.search(subject):
        return "conditional"
    # Fell through every _REFUSED pattern: this is the residual `_SUBJECTS` itself could not
    # match (the bare-subject production's own tail, or a genuinely novel shape).
    return "subject_unmatched"


def diagnose_sentence(description: str) -> str:
    """The class one whole sentence belongs to — `no_marker`/`empty_items` before the subject is
    even split out, on the same terms `parse_sentence` itself refuses in that order."""
    marker = _MARKER.search(description)
    if marker is None:
        return "no_marker"
    subject = description[: marker.start()].strip()
    items_text = description[marker.end() :].strip().rstrip(".").strip()
    if not items_text:
        return "empty_items"
    return classify_subject(subject)


@dataclass(frozen=True, slots=True)
class EquipmentTaxonomyReport:
    """The whole measurement: counts and class labels, and only those."""

    generated_at: str
    mode: str
    edition: str
    source: str
    sentences: int
    unparsed: int
    classes: Mapping[str, int] = field(default_factory=dict)

    @property
    def ratio(self) -> float:
        return self.unparsed / self.sentences if self.sentences else 0.0

    def share(self, *keys: str) -> float:
        covered = sum(self.classes.get(key, 0) for key in keys)
        return covered / self.unparsed if self.unparsed else 0.0


def measure(
    config: PipelineConfig,
    *,
    repository_root: Path,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    generated_at: datetime | None = None,
) -> EquipmentTaxonomyReport:
    """Acquire, classify, discard — the equipment-sentence sibling of
    :func:`tools.option_taxonomy.measure`. Every acquired string lives inside the
    ``with workspace(...)`` block and never leaves it; what comes back out is integers."""
    class_counts: dict[str, int] = {key: 0 for key in CLASS_LABELS}
    sentences = 0
    unparsed = 0

    with workspace(repository_root) as work:
        acquisition, payloads = acquire_detail(
            config, fixtures_dir=fixtures_dir, offline=offline, workspace=work
        )
        source = acquisition.source_base_url
        tables = read_detail(config, payloads)
        rows = tables.get(EQUIPMENT_TABLE)
        if rows is not None:
            for row in rows.rows:
                description = row.fields.get("description", "")
                sentences += 1
                if parse_sentence(description) is not None:
                    continue
                unparsed += 1
                class_counts[diagnose_sentence(description)] += 1

    moment = (generated_at or datetime.now(UTC)).astimezone(UTC)
    return EquipmentTaxonomyReport(
        generated_at=moment.isoformat().replace("+00:00", "Z"),
        mode=config.detail_acquisition_mode.value,
        edition=config.detail_edition,
        source=source,
        sentences=sentences,
        unparsed=unparsed,
        classes=dict(class_counts),
    )


def _percent(part: int, whole: int) -> str:
    return f"{part / whole:.1%}" if whole else "—"


def render(report: EquipmentTaxonomyReport) -> str:
    """The measurement as Markdown. Counts and class labels only — never a sentence."""
    lines = [
        "<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Generated by "
        "tools/equipment_taxonomy.py (008 T002). -->",
        "# Equipment-sentence taxonomy",
        "",
        f"- Generated: `{report.generated_at}`",
        f"- Detail acquisition mode: `{report.mode}`",
        f"- Declared detail edition: `{report.edition}`",
        f"- Source: `{report.source}`",
        "",
        "**Non-destructive, and text-free.** Nothing under `data/`, `curation/`, or `state/` was "
        "written, the acquired pages were discarded with `work/` when the run ended, and no "
        "source sentence, model name, or item name appears on this page. It carries counts.",
        "",
        "## Corpus",
        "",
        "| Equipment sentences | `EQP-UNPARSED` | Share unparsed |",
        "|---:|---:|---:|",
        f"| {report.sentences} | **{report.unparsed}** | {report.ratio:.1%} |",
        "",
        "## The residual, by class",
        "",
        "Disjoint and ordered — mirrors `_REFUSED`'s own control flow, so these counts sum to the "
        "residual above.",
        "",
        "| Class | Shape | Sentences | Share of residual |",
        "|---|---|---:|---:|",
    ]
    for key, label in CLASS_LABELS.items():
        count = report.classes.get(key, 0)
        lines.append(f"| `{key}` | {label} | {count} | {_percent(count, report.unparsed)} |")

    lines += [
        "",
        "## Open Decision O1's own number",
        "",
        f"`subset_one` + `subset_a` + `subset_int` = "
        f"{sum(report.classes.get(k, 0) for k in ('subset_one', 'subset_a', 'subset_int'))} "
        "sentences — the non-predicate, non-conditional subset-subject family O1 is about "
        "(`One [MODEL]`, `A`/`An [MODEL]`, `INT [MODEL]`).",
        "",
        "## Reading this",
        "",
        "- **`equipment_qualified` and `conditional` are the same permission problem "
        "`refused_conditional_or_equipment_qualified` names on the options side** — resolving "
        "either would publish a model group nobody can find, or a permission the source did not "
        "state unconditionally. No production is planned for either class here.",
        "- **`subset_one`/`subset_a`/`subset_int` are what O1 decides**: curator override "
        "(`curation/equipment-overrides.json`) under option A, or an additive schema column "
        "under option B.",
        "- Nothing here is a defect list.",
        "",
    ]
    return "\n".join(lines)


def _summary_line(report: EquipmentTaxonomyReport) -> str:
    top = sorted(report.classes.items(), key=lambda item: (-item[1], item[0]))[:1]
    leader = f"{top[0][0]} ({top[0][1]})" if top and top[0][1] else "none"
    return (
        f"{PROG}: {report.unparsed} of {report.sentences} equipment sentences unparsed "
        f"({report.ratio:.1%}); largest class {leader}"
    )


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Classify the unparsed default-equipment sentences of a corpus, retaining "
        "nothing.",
    )
    parser.add_argument("--fixtures", type=Path, help="source from a synthetic fixture set")
    parser.add_argument(
        "--offline", action="store_true", help="refuse network access; requires --fixtures"
    )
    parser.add_argument(
        "--out", type=Path, help="report path (default reports/equipment-taxonomy/<date>.md)"
    )
    parser.add_argument("--repo", type=Path, help="repository root (default: this checkout)")
    parser.add_argument(
        "--print-only", action="store_true", help="render to stdout and write no file"
    )
    return parser.parse_args(list(argv) if argv is not None else None)


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
    snapshot = read_curated_tree(root / "data" / config.detail_edition)
    if snapshot is not None:
        breakdown = equipment_partial_breakdown(snapshot)
        baseline = default_equipment_ratchet_baseline(root)
        rendered += render_snapshot_sections(breakdown=breakdown, baseline=baseline)
        candidate_evidence = equipment_override_candidate_worklist(root)
        if candidate_evidence is not None:
            rules_version_id, worklist = candidate_evidence
            rendered += render_equipment_override_candidate_worklist(rules_version_id, worklist)

    if args.print_only:
        print(rendered)
    else:
        destination = args.out or (root / REPORTS_DIR / f"{report.generated_at[:10]}.md")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"{PROG}: wrote {destination}")

    print(_summary_line(report))
    return int(ExitCode.SUCCESS)


def iter_class_keys() -> Iterable[str]:
    """Every taxonomy class key, in report order — a convenience for tests and reports."""
    return list(CLASS_LABELS)


# =================================================================================================
# 008 task T002's own card-shape collapse, and T005's baseline confirmation — the equipment
# siblings of `tools/option_taxonomy.py`'s published-snapshot section, reading the same two
# committed sources (this checkout's own `data/<edition-code>/` curated tree and the previous
# published version's retained `report.json`) for the identical reason: neither requires a live
# fetch, and both are already governed by the pipeline's own ordinary acquisition.
# =================================================================================================


@dataclass(frozen=True, slots=True)
class EquipmentPartialBreakdown:
    """T002's own card-shape number: the 47/24 US3 is sized against."""

    partial_datasheets: int
    partial_shapes: int
    partial_ids: tuple[str, ...]


def equipment_partial_breakdown(snapshot: CuratedSnapshot) -> EquipmentPartialBreakdown:
    """Every `default_equipment_state = partial` datasheet, collapsed to distinct card shapes by
    case-insensitive name — the same method `tools.option_taxonomy._card_shapes` uses, confirmed
    against the spec's own committed census on the option side (42/28, 120/80)."""
    partial = sorted(
        (
            d
            for d in snapshot.datasheets
            if d.default_equipment_state == DefaultEquipmentState.PARTIAL
        ),
        key=lambda d: d.datasheet_id,
    )
    shapes = len({d.name.strip().casefold() for d in partial})
    return EquipmentPartialBreakdown(
        partial_datasheets=len(partial),
        partial_shapes=shapes,
        partial_ids=tuple(d.datasheet_id for d in partial),
    )


@dataclass(frozen=True, slots=True)
class DefaultEquipmentRatchetBaseline:
    """T005: does the previous published `report.json` carry a `loadout.default_equipment`
    percent FR-021's new ratchet can floor on. `None` fields mean it does not — the case T014
    must be told about (tasks.md T005)."""

    rules_version_id: str
    current: int | None
    previous: int | None
    ratio_percent: int | None
    threshold_percent: int | None


def default_equipment_ratchet_baseline(
    root: Path, *, manifest_relative_path: str = "site/manifest.json"
) -> DefaultEquipmentRatchetBaseline | None:
    """Read `loadout.default_equipment` straight from the previous published version's own
    retained `report.json` — the exact figure `pipeline.curate.prior.previous_loadout_coverage`
    already reads generically (T005's trace: no code change needed for FR-021 to have a floor)."""
    rules_version_id = previous_published_version(root / manifest_relative_path)
    if rules_version_id is None:
        return None
    report_path = root / "reports" / rules_version_id / "report.json"
    if not report_path.is_file():
        return None
    document = json.loads(report_path.read_text(encoding="utf-8"))
    figure = document.get("coverage", {}).get("loadout.default_equipment")
    if not isinstance(figure, Mapping):
        return DefaultEquipmentRatchetBaseline(rules_version_id, None, None, None, None)
    return DefaultEquipmentRatchetBaseline(
        rules_version_id=rules_version_id,
        current=figure.get("current"),
        previous=figure.get("previous"),
        ratio_percent=figure.get("ratio_percent"),
        threshold_percent=figure.get("threshold_percent"),
    )


# -- 008 Phase 7 (T071/T072 preparation) ---------------------------------------------------------
# The equipment twin of `tools/option_taxonomy.py::override_candidate_worklist` — same shape, same
# staleness caveat, same text-free discipline, over `EQP-UNPARSED` instead of `OPT-UNPARSED`.


@dataclass(frozen=True, slots=True)
class EquipmentOverrideCandidateWorklist:
    """Every `EQP-UNPARSED` row the retained report names, grouped by datasheet.

    A worklist, not a set of overrides: no item name, no `applies_to`, no model name ever appears
    here, because none is derivable from `report.json`'s text-free finding detail. It is also
    stale by construction, on the identical terms `tools.option_taxonomy.
    OverrideCandidateWorklist`'s own docstring explains — this predates Phase 5's own measurement
    (which added zero grammar productions but still moved which rows count) and every row named
    here needs T074's mid-campaign dry-run to confirm it is still unresolved, and which of the
    three permanently-refused/subset/O1 classes it falls into, before a curator authors it.
    """

    rows_by_datasheet: Mapping[str, tuple[int, ...]]
    total_rows: int
    total_datasheets: int


def equipment_override_candidate_worklist(
    root: Path, *, manifest_relative_path: str = "site/manifest.json"
) -> tuple[str, EquipmentOverrideCandidateWorklist] | None:
    """The previous published version's retained `EQP-UNPARSED` findings, grouped by datasheet.

    Returns ``None`` on the same terms `default_equipment_ratchet_baseline` does: no previous
    published version, or its `report.json` absent — never an error, since a fresh checkout
    legitimately has neither yet.
    """
    rules_version_id = previous_published_version(root / manifest_relative_path)
    if rules_version_id is None:
        return None
    report_path = root / "reports" / rules_version_id / "report.json"
    if not report_path.is_file():
        return None
    document = json.loads(report_path.read_text(encoding="utf-8"))
    findings = document.get("findings", [])
    if not isinstance(findings, list):
        findings = []

    per_datasheet: dict[str, list[int]] = {}
    for finding in findings:
        if not isinstance(finding, Mapping) or finding.get("finding_code") != "EQP-UNPARSED":
            continue
        detail = finding.get("detail")
        if not isinstance(detail, Mapping):
            continue
        datasheet_id = detail.get("datasheet_id")
        line = detail.get("line")
        if isinstance(datasheet_id, str) and isinstance(line, int):
            per_datasheet.setdefault(datasheet_id, []).append(line)

    rows_by_datasheet = {
        datasheet_id: tuple(sorted(lines)) for datasheet_id, lines in sorted(per_datasheet.items())
    }
    return rules_version_id, EquipmentOverrideCandidateWorklist(
        rows_by_datasheet=rows_by_datasheet,
        total_rows=sum(len(lines) for lines in rows_by_datasheet.values()),
        total_datasheets=len(rows_by_datasheet),
    )


def render_equipment_override_candidate_worklist(
    rules_version_id: str, worklist: EquipmentOverrideCandidateWorklist
) -> str:
    """T071/T072 preparation, as its own Markdown section — counts and `datasheet_id#line` pairs
    only, never a sentence, a subject, or an item name."""
    lines = [
        "",
        "## Override-candidate worklist (T071/T072 preparation)",
        "",
        f"Read from `reports/{rules_version_id}/report.json`'s own `EQP-UNPARSED` findings — "
        "text-free (`datasheet_id`, `line` only). **Stale by construction and NOT a substitute "
        "for T074's mid-campaign dry-run** — see `EquipmentOverrideCandidateWorklist`'s own "
        "docstring. This section proves the worklist's SHAPE (grouped by datasheet, real line "
        "ordinals) before that live run supplies the current, authoritative list, and before a "
        "curator can tell a genuine O1 subset row apart from a permanently-refused one — that "
        "split needs the sentence text this environment has no route to acquire.",
        "",
        f"**{worklist.total_rows} `EQP-UNPARSED` rows across {worklist.total_datasheets} "
        "datasheets, pre-008 baseline:**",
        "",
    ]
    if worklist.rows_by_datasheet:
        lines += [
            f"`{datasheet_id}`: lines {', '.join(str(line) for line in rows)}"
            for datasheet_id, rows in worklist.rows_by_datasheet.items()
        ]
    else:
        lines.append("(none)")
    lines.append("")
    return "\n".join(lines)


def render_snapshot_sections(
    *, breakdown: EquipmentPartialBreakdown, baseline: DefaultEquipmentRatchetBaseline | None
) -> str:
    """T002's card-shape collapse and T005's ratchet-baseline confirmation, as their own Markdown
    sections. Counts, a ratio, and datasheet ids only."""
    lines = [
        "",
        "## Default-equipment partial breakdown, card-shape collapse (T002)",
        "",
        "| Population | Datasheets | Distinct card shapes |",
        "|---|---:|---:|",
        f"| `defaultEquipmentState=partial` | {breakdown.partial_datasheets} | "
        f"{breakdown.partial_shapes} |",
        "",
        f"`{', '.join(breakdown.partial_ids)}`" if breakdown.partial_ids else "(none)",
        "",
        "## FR-021's ratchet floor, confirmed against the retained report (T005, risk R-D)",
        "",
    ]
    if baseline is None:
        lines += [
            "No previous published version resolves (`site/manifest.json` absent or empty) — "
            "**T014 must be told**: FR-021 would degrade to a first-release report-only figure.",
            "",
        ]
    elif baseline.ratio_percent is None:
        lines += [
            f"Previous published version `{baseline.rules_version_id}` resolves, but its retained "
            "`report.json` carries no `loadout.default_equipment` figure at all — **T014 must be "
            "told**: FR-021 would degrade to a first-release report-only figure.",
            "",
        ]
    else:
        lines += [
            f"Previous published version: `{baseline.rules_version_id}`.",
            "",
            "| current | previous | ratio_percent | threshold_percent (today, unratcheted) |",
            "|---:|---:|---:|---:|",
            f"| {baseline.current} | {baseline.previous} | {baseline.ratio_percent} | "
            f"{baseline.threshold_percent} |",
            "",
            f"**Confirmed: {baseline.ratio_percent}%** — present, non-empty, ready for FR-021's "
            "ratchet to floor on. `threshold_percent` is `0` today because "
            "`DEFAULT_EQUIPMENT_KEY` is not yet in `LOADOUT_RATCHETED_KEYS` "
            "(`pipeline/validate/coverage.py`) — the exact absence FR-021 fills, and the "
            "observable proof, once filled, that the ratchet is on (plan.md).",
            "",
        ]
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
