#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the digest-churn dry run (004 task
# T075): acquire in html mode into an ephemeral work/, recompute every approved ability summary's
# status against the freshly acquired source WITHOUT writing curation/, report the per-faction and
# total needs_rereview count, and discard the acquired text on exit (research D8, risk R-B,
# quickstart section 3).
# AI-Assisted: Claude Code (model: claude-opus-5) - Exit an unconfigured live run as the
# configuration error it is (004 T075 follow-up): the first real invocation reported an unset
# WGC_DETAIL_SOURCE_URL as a partial upstream export, which is the wrong fault and the wrong exit
# code.
"""Measure the re-review wave before anything commits to it.

`004`'s largest risk is editorial, not technical: wholesale edition adoption re-digests every
detail-sourced value, a new edition re-words its faction packs comprehensively, and
``SUM-NEEDS-REREVIEW`` is always blocking. Research D8 *estimates* 85-100% of the approved ability
summaries flip. **An estimate is not a plan.** This tool turns the estimate into a measurement.

::

    python tools/churn_dry_run.py                       # against the live current-edition source
    python tools/churn_dry_run.py --fixtures fixtures/minimal --offline   # rehearsal, no network

The live invocation reads the source the configuration names, and nothing here guesses at one:
``WGC_DETAIL_ACQUISITION_MODE``, ``WGC_DETAIL_EDITION`` and ``WGC_DETAIL_SOURCE_URL`` are set
together when an edition is adopted, and a live run with any of them unset stops as the
configuration error it is (exit 60) rather than as a source failure.

What it does, in one sentence: acquires the detail source in the configured mode into an
**ephemeral** workspace, computes each ability's current mechanic digest there, compares it with
the digest each approved record was authored against, and writes the counts to
``reports/churn-dry-run/<date>.md``.

Four properties, each of which is the reason a line of this file exists:

* **It writes nothing to ``curation/``.** The wave is a measurement, not an edit. Flipping two
  thousand records to ``needs_rereview`` from a script is the one thing that must not happen by
  accident — a curator re-reviews each record and says so in the file (FR-024, FR-025).
* **The acquired text is discarded.** It lands in a workspace that is emptied on exit, whatever
  happens, and nothing but digests leaves this process (FR-010, FR-027).
* **No digest and no key is printed.** The report carries counts. A digest in a report is a
  fingerprint of the publisher's wording sitting in version control, which is the thing
  ``state/detection-digest.json``'s one-way argument is careful about.
* **The distribution is per faction**, because the campaign it sizes (T077) is scheduled faction
  file by faction file, and a single total of two thousand tells a curator nothing about where to
  start.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from pipeline.acquire.detail_source import acquire_detail, read_detail
from pipeline.acquire.http import AcquisitionError
from pipeline.config import ConfigError, PipelineConfig, load_config, repo_root
from pipeline.curate.summaries import SummaryStatus, compute_current_digests, effective_status
from pipeline.exit_codes import ExitCode
from pipeline.models.authored import AbilitySummary, ReviewState
from pipeline.normalize.mechanic_digest import DigestKeyMissingError, resolve_digest_key
from pipeline.workspace import workspace

PROG: Final = "churn_dry_run.py"

#: Where the measurement lands. A directory of its own, never ``reports/candidate/``: this is not
#: a run report and must never be mistaken for one by a reviewer or by the publish gate.
REPORTS_DIR: Final = Path("reports") / "churn-dry-run"

ABILITIES_DIR: Final = Path("curation") / "abilities"


@dataclass(frozen=True, slots=True)
class FactionChurn:
    """One ``curation/abilities/<faction>.json`` file, measured."""

    faction_id: str
    total: int
    approved: int
    needs_rereview: int
    unapproved: int
    absent_from_source: int

    @property
    def ratio(self) -> float:
        """The share of *approved* records that flip. Zero approved is zero churn, not a crash."""
        return self.needs_rereview / self.approved if self.approved else 0.0


@dataclass(frozen=True, slots=True)
class ChurnReport:
    """The whole measurement: per faction, and in total."""

    generated_at: str
    mode: str
    edition: str
    source: str
    factions: tuple[FactionChurn, ...]

    @property
    def total(self) -> int:
        return sum(faction.total for faction in self.factions)

    @property
    def approved(self) -> int:
        return sum(faction.approved for faction in self.factions)

    @property
    def needs_rereview(self) -> int:
        return sum(faction.needs_rereview for faction in self.factions)

    @property
    def absent_from_source(self) -> int:
        return sum(faction.absent_from_source for faction in self.factions)

    @property
    def ratio(self) -> float:
        return self.needs_rereview / self.approved if self.approved else 0.0


def _load_faction_files(curation_dir: Path) -> dict[str, list[AbilitySummary]]:
    """``faction id -> its authored ability summaries``, read straight from the files.

    Read per file rather than through :func:`pipeline.curate.authored.load_authored`, which
    flattens every faction into one mapping: the per-faction distribution *is* the output here,
    and a flattened mapping has already thrown it away.
    """
    directory = curation_dir / ABILITIES_DIR.name
    if not directory.is_dir():
        return {}
    per_faction: dict[str, list[AbilitySummary]] = {}
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        per_faction[path.stem] = [AbilitySummary.model_validate(record) for record in payload]
    return per_faction


def measure(
    config: PipelineConfig,
    *,
    repository_root: Path,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    curation_dir: Path | None = None,
    generated_at: datetime | None = None,
) -> ChurnReport:
    """Acquire, digest, compare, discard — and return only the counts.

    The acquisition and every digest computed from it live inside the ``with workspace(...)``
    block and nowhere else. That is not a stylistic choice: research D6's rule is that the digest
    may only be computed where the text exists, and this is the shape that makes "the text does
    not exist anywhere else" true rather than asserted.
    """
    per_faction = _load_faction_files(curation_dir or (repository_root / "curation"))
    key = resolve_digest_key(config)

    with workspace(repository_root) as work:
        _acquisition, payloads = acquire_detail(
            config, fixtures_dir=fixtures_dir, offline=offline, workspace=work
        )
        detail = read_detail(config, payloads)
        current = compute_current_digests(detail, key=key)
        source = _acquisition.source_base_url

    measured: list[FactionChurn] = []
    for faction_id, records in sorted(per_faction.items()):
        authored = {record.ability_key: record for record in records}
        statuses = [
            effective_status(
                record.ability_key,
                authored=authored,
                current_digest=current.get(record.ability_key),
            )
            for record in records
        ]
        measured.append(
            FactionChurn(
                faction_id=faction_id,
                total=len(records),
                approved=sum(
                    1 for record in records if record.review_state is ReviewState.APPROVED
                ),
                needs_rereview=sum(1 for s in statuses if s is SummaryStatus.NEEDS_REREVIEW),
                unapproved=sum(
                    1
                    for s in statuses
                    if s not in {SummaryStatus.APPROVED, SummaryStatus.NEEDS_REREVIEW}
                ),
                # An ability the current source does not publish at all cannot flip — it has no
                # fresh digest to differ from. It is counted apart because it is the *other*
                # half of an edition move: records whose ability the edition dropped, which a
                # curator retires rather than re-reviews.
                absent_from_source=sum(
                    1 for record in records if record.ability_key not in current
                ),
            )
        )

    moment = (generated_at or datetime.now(UTC)).astimezone(UTC)
    return ChurnReport(
        generated_at=moment.isoformat().replace("+00:00", "Z"),
        mode=config.detail_acquisition_mode.value,
        edition=config.detail_edition,
        source=source,
        factions=tuple(measured),
    )


def render(report: ChurnReport) -> str:
    """The measurement as Markdown. Counts only — never a digest, never a summary, never a key."""
    lines = [
        "<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Generated by "
        "tools/churn_dry_run.py (004 T075/T076). -->",
        "# Digest-churn dry run",
        "",
        f"- Generated: `{report.generated_at}`",
        f"- Detail acquisition mode: `{report.mode}`",
        f"- Declared detail edition: `{report.edition}`",
        f"- Source: `{report.source}`",
        "",
        "**Non-destructive.** Nothing under `curation/` was written, and the acquired text was "
        "discarded with `work/` when the run ended. This page carries counts and nothing else.",
        "",
        "## Total",
        "",
        "| Authored | Approved | Would need re-review | Share of approved | Absent from source |",
        "|---:|---:|---:|---:|---:|",
        f"| {report.total} | {report.approved} | **{report.needs_rereview}** | "
        f"{report.ratio:.1%} | {report.absent_from_source} |",
        "",
        "## Per faction",
        "",
        "Scheduled faction file by faction file: this is the column a campaign is planned "
        "against, not the total above.",
        "",
        "| Faction | Authored | Approved | Would need re-review | Share | Not approved today | "
        "Absent from source |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for faction in sorted(report.factions, key=lambda f: (-f.needs_rereview, f.faction_id)):
        lines.append(
            f"| `{faction.faction_id}` | {faction.total} | {faction.approved} | "
            f"{faction.needs_rereview} | {faction.ratio:.1%} | {faction.unapproved} | "
            f"{faction.absent_from_source} |"
        )
    lines += [
        "",
        "## Reading this",
        "",
        "- **Would need re-review** is what `SUM-NEEDS-REREVIEW` will report on the next real "
        "run in this mode. It has no gate switch and is always blocking, so it is the size of "
        "the campaign that gates the release (O1 Ruling).",
        "- **Absent from source** is the other half of an edition move: a record whose ability "
        "the current edition no longer publishes. Those are retired, not re-reviewed.",
        "- No digest appears here, in either direction. The comparison happened where the "
        "source text existed and nothing but these counts came back.",
        "",
    ]
    return "\n".join(lines)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=PROG, description="Measure the ability-summary re-review wave without writing it."
    )
    parser.add_argument("--fixtures", type=Path, help="source from a synthetic fixture set")
    parser.add_argument(
        "--offline", action="store_true", help="refuse network access; requires --fixtures"
    )
    parser.add_argument(
        "--out", type=Path, help="report path (default reports/churn-dry-run/<date>.md)"
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
    except (ConfigError, DigestKeyMissingError) as exc:
        # Named without its value, here as everywhere: the diagnostic says which variable is
        # unset and never what it would have contained. `ConfigError` joins it because an
        # unconfigured source and an unconfigured key are the same mistake and must exit the
        # same way — this tool is run by hand more than any other, so a live invocation with a
        # variable unset is its most likely failure and has to say so plainly.
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

    print(
        f"{PROG}: {report.needs_rereview} of {report.approved} approved ability summaries "
        f"would need re-review ({report.ratio:.1%}) across {len(report.factions)} faction files"
    )
    return int(ExitCode.SUCCESS)


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
