# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented report.json and report.md
# (task T095) exactly per validation-report.md §2 and §4: a derived verdict, the coverage block,
# a scale block stating count AND proportion for every category, counts by class and severity,
# and a human report opening with verdict, scale, and blocking findings in that order (FR-031).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Exported the verdict-line table as
# `VERDICT_LINE` (task T119) so pipeline.report.pr_body can open the candidate PR body with the
# same headline wording report.md already uses.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added `trends` to `SUB_REPORT_FILES`
# (task T149) for `pipeline.report.trends.render_trends`'s unverified/hybrid-count trend, wired
# in the same way as every other sub-report already listed here.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added 004-rules-data-enrichment's scale
# figures (004 task T033, data-model.md §5): composition and wargear-option resolution as a
# proportion of published datasheets, plus the unparsed-row and unlinked-choice tails, each
# stated as a count AND a proportion.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the `keyword_classification` figure
# (004 task T041, SC-005), the one figure here carrying its own denominator.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the `weapon_ability_keywords` figure
# (issue #4), the second one carrying its own denominator, so a weapon-ability class that is
# empty on every published weapon line is a number an approver reads rather than a silence.
"""`reports/<rulesVersionId>/report.json` and `report.md`.

Every run produces this, whether or not it publishes (FR-031), and the report of a run that
*did* publish is retained for the life of that version — because a support enquiry about a
mispriced unit has to be answerable from it without re-running the pipeline or re-acquiring any
source (spec: *Support implications*).

Two structural properties, both from `validation-report.md` §1:

* **`verdict` is derived, never authored.** It is a property of the findings, computed by
  :class:`~pipeline.models.findings.ValidationReport`. Nothing in this module can set it, which
  is what makes "there is no override flag" a fact about the code rather than a policy.
* **Every category states a count and a proportion.** A bare enumeration at a few thousand
  datasheets is unreadable; the approver's question is *how much* of this release is uncertain.

`report.md` opens with the verdict, then the scale table, then the blocking findings, in that
order, so an approver's first screen answers "can this ship, and how much of it is uncertain?".
Everything else follows.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from pipeline.build.canonical_json import JsonValue, omit_absent, write_tree_file
from pipeline.models.curated import CuratedSnapshot, WargearOptionState
from pipeline.models.findings import (
    CoverageFigure,
    Finding,
    ScaleFigure,
    Severity,
    ValidationReport,
    Verdict,
)
from pipeline.models.mechanical import MechanicalValue
from pipeline.models.provenance import PricingConfidenceState
from pipeline.models.source import SourceAcquisition

#: The sub-report file names, fixed by `validation-report.md` §4.
SUB_REPORT_FILES: Mapping[str, str] = {
    "change_summary": "change-summary.md",
    "edition_mismatch": "edition-mismatch.md",
    "unverified_pricing": "unverified-pricing.md",
    "summary_coverage": "summary-coverage.md",
    "trends": "trends.md",
}


def report_dir(root: Path, rules_version_id: str) -> Path:
    """`reports/<rulesVersionId>/`."""
    return root / "reports" / rules_version_id


def scale_figures(snapshot: CuratedSnapshot, findings: Sequence[Finding]) -> dict[str, ScaleFigure]:
    """The `scale` block: a count **and** a proportion for every category (§1.3)."""
    total = len(snapshot.datasheets)

    def figure(count: int) -> ScaleFigure:
        return ScaleFigure(count=count, proportion=round(count / total, 4) if total else 0.0)

    unverified = sum(
        1
        for datasheet in snapshot.datasheets
        if datasheet.pricing_confidence.state is PricingConfidenceState.UNVERIFIED
    )
    hybrid = sum(1 for d in snapshot.datasheets if d.provenance.is_hybrid_edition)
    escalating = sum(
        1 for d in snapshot.datasheets if any(cost.copy_index_min > 1 for cost in d.costs)
    )
    outstanding = sum(
        1
        for datasheet in snapshot.datasheets
        for key in datasheet.ability_keys
        if key not in snapshot.ability_summaries
        or snapshot.ability_summaries[key].review_state.value != "approved"
    )

    # 004-rules-data-enrichment (data-model.md §5). `composition` and `wargear_options` also
    # appear in the *coverage* block, where they carry FR-038's ratio against the previous
    # release. These two are the other half of the same question and the one SC-001 and SC-002
    # actually measure: **how much of this release**, not how much of last release's. FR-008
    # asks for the proportion in terms, because a systematic extraction failure has to be
    # visible at a glance rather than derivable from a list of a few thousand datasheets.
    resolved_composition = sum(1 for d in snapshot.datasheets if d.composition)
    options_resolved = sum(
        1
        for d in snapshot.datasheets
        if d.wargear_option_state in {WargearOptionState.NONE, WargearOptionState.EXTRACTED}
    )
    unparsed_option_rows = sum(1 for f in findings if f.finding_code == "OPT-UNPARSED")
    unlinked_choices = sum(1 for f in findings if f.finding_code == "OPT-LINK-AMBIGUOUS")

    # `keyword_classification` is the one figure here whose denominator is **not** the datasheet
    # count: SC-005 asks what proportion of the *keywords in use* carry a class, and dividing a
    # keyword count by a datasheet count would produce a number that means nothing and moves
    # whenever either changes. Stated with its own denominator rather than approximated with the
    # shared one (data-model.md §5).
    # `weapon_ability_keywords` is the second figure with its own denominator, and for the same
    # reason: the question is what proportion of *weapon lines* state an ability keyword, and a
    # datasheet count is not that. It exists because the class was empty on every published
    # weapon line for the life of the project (issue #4) and no figure here would have shown it —
    # the emptiness is per-record correct, so only a count of the class itself makes it visible.
    weapon_lines = sum(len(datasheet.weapons) for datasheet in snapshot.datasheets)
    weapons_with_keywords = sum(
        1
        for datasheet in snapshot.datasheets
        for weapon in datasheet.weapons
        if weapon.ability_keywords
    )

    keywords_in_use = {keyword.keyword for d in snapshot.datasheets for keyword in d.keywords}
    classified = {
        keyword.keyword
        for d in snapshot.datasheets
        for keyword in d.keywords
        if keyword.keyword_class is not None
    }

    return {
        "unverified_pricing": figure(unverified),
        "hybrid_edition": figure(hybrid),
        "escalating_price_datasheets": figure(escalating),
        "summaries_outstanding": figure(outstanding),
        "composition_resolved": figure(resolved_composition),
        "wargear_options_resolved": figure(options_resolved),
        # **Expected to persist.** The residual tail is normal work, budgeted rather than
        # chased: what matters is that it is measured every release, so a *change* in it is
        # visible where a standing figure would not be.
        "unparsed_option_rows": figure(unparsed_option_rows),
        "unlinked_choices": figure(unlinked_choices),
        "keyword_classification": ScaleFigure(
            count=len(classified),
            proportion=(
                round(len(classified) / len(keywords_in_use), 4) if keywords_in_use else 0.0
            ),
        ),
        "weapon_ability_keywords": ScaleFigure(
            count=weapons_with_keywords,
            proportion=(round(weapons_with_keywords / weapon_lines, 4) if weapon_lines else 0.0),
        ),
    }


def _acquisition_row(acquisition: SourceAcquisition) -> dict[str, MechanicalValue]:
    return {
        "acquisition_id": acquisition.acquisition_id,
        "source_key": acquisition.source_key.value,
        "declared_edition_code": acquisition.declared_edition_code,
        "retrieved_at": acquisition.retrieved_at,
        "content_fingerprint": acquisition.content_fingerprint,
        # 009 rung R05 (T087, T091, FR-031): the outcome is what lets a curator reading the run
        # record tell a skipped-because-unchanged acquisition (`unchanged`) from a normal one
        # (`ok`) from a failed one, without cross-referencing the findings list.
        "outcome": acquisition.outcome.value,
        **{f"coverage_{key}": value for key, value in sorted(acquisition.coverage.items())},
    }


def build_report(
    *,
    run_id: str,
    rules_version_id: str,
    channel: str,
    generated_at: str,
    acquisitions: Sequence[SourceAcquisition],
    coverage: Mapping[str, CoverageFigure],
    snapshot: CuratedSnapshot,
    findings: Sequence[Finding],
) -> ValidationReport:
    """Assemble the report. The verdict is not a parameter — it is derived from ``findings``."""
    return ValidationReport(
        run_id=run_id,
        rules_version_id=rules_version_id,
        channel=channel,
        generated_at=generated_at,
        source_acquisitions=[_acquisition_row(a) for a in acquisitions],
        coverage=dict(coverage),
        scale=scale_figures(snapshot, findings),
        findings=sorted(findings, key=lambda f: (f.finding_code, tuple(f.entity_refs))),
        sub_reports=dict(SUB_REPORT_FILES),
    )


def report_json(report: ValidationReport) -> dict[str, JsonValue]:
    """`report.json` exactly as §2 shapes it."""
    return {
        "report_contract_version": report.report_contract_version,
        "run_id": report.run_id,
        "rules_version_id": report.rules_version_id,
        "channel": report.channel,
        "generated_at": report.generated_at,
        "verdict": report.verdict.value,
        "source_acquisitions": [dict(row) for row in report.source_acquisitions],
        "coverage": {
            name: {
                "current": figure.current,
                "previous": figure.previous,
                "ratio_percent": round(figure.ratio * 100),
                "threshold_percent": round(figure.threshold * 100),
            }
            for name, figure in sorted(report.coverage.items())
        },
        "scale": {
            name: {"count": figure.count, "proportion_percent": round(figure.proportion * 100)}
            for name, figure in sorted(report.scale.items())
        },
        "counts": report.counts(),
        "findings": [
            omit_absent(
                {
                    "finding_code": finding.finding_code,
                    "class": finding.finding_class.value,
                    "severity": finding.severity.value,
                    "entity_refs": list(finding.entity_refs),
                    "detail": dict(finding.detail),
                    "data_digest": finding.data_digest,
                    "suggestions": [
                        {"entity_ref": s.entity_ref, "score_percent": round(s.score * 100)}
                        for s in finding.suggestions
                    ]
                    or None,
                    "resolution": finding.resolution,
                }
            )
            for finding in report.findings
        ],
        "sub_reports": dict(sorted(report.sub_reports.items())),
    }


#: Public so :mod:`pipeline.report.pr_body` (task T119) can open the approver's PR body with the
#: same headline sentence `report.md` opens with, rather than inventing a second wording of it.
VERDICT_LINE: Mapping[Verdict, str] = {
    Verdict.CLEAN: "**CLEAN** — nothing to report. Eligible for publication.",
    Verdict.ADVISORY_ONLY: "**ADVISORY ONLY** — eligible for publication pending approval.",
    Verdict.BLOCKED: "**BLOCKED** — publication refused. There is no override flag (FR-029).",
}


def render_report_markdown(report: ValidationReport) -> str:
    """`report.md`: verdict, scale, blocking findings — in that order (§4)."""
    counts = report.counts()
    out: list[str] = [
        f"# Validation report — {report.rules_version_id}",
        "",
        VERDICT_LINE[report.verdict],
        "",
        f"Run `{report.run_id}` on the `{report.channel}` channel, {report.generated_at}.",
        "",
        "## Scale",
        "",
        "| category | count | proportion of the snapshot |",
        "|---|---|---|",
    ]
    out += [
        f"| {name.replace('_', ' ')} | {figure.count} | {figure.proportion * 100:.1f}% |"
        for name, figure in sorted(report.scale.items())
    ]

    if report.coverage:
        out += [
            "",
            "## Coverage against the previous published version",
            "",
            "| category | current | previous | ratio | threshold |",
            "|---|---|---|---|---|",
        ]
        out += [
            f"| {name.replace('_', ' ')} | {figure.current} | {figure.previous} | "
            f"{figure.ratio * 100:.1f}% | {figure.threshold * 100:.1f}% |"
            for name, figure in sorted(report.coverage.items())
        ]

    blocking = report.unresolved_blocking
    out += ["", "## Blocking findings", ""]
    if not blocking:
        out.append("None.")
    else:
        out += [
            f"- `{finding.finding_code}` {', '.join(finding.entity_refs) or '(snapshot-wide)'}"
            for finding in blocking
        ]

    out += [
        "",
        "## All findings",
        "",
        f"{counts['blocking']} blocking, {counts['advisory']} advisory, "
        f"{counts['suppressed']} suppressed.",
        "",
    ]
    by_class: dict[str, list[Finding]] = {}
    for finding in report.findings:
        by_class.setdefault(finding.finding_class.value, []).append(finding)
    for class_name in sorted(by_class):
        out += [
            f"<details><summary>{class_name} ({len(by_class[class_name])})</summary>",
            "",
            "| code | severity | entities | resolved |",
            "|---|---|---|---|",
        ]
        out += [
            f"| `{f.finding_code}` | {f.severity.value} | "
            f"{', '.join(f'`{ref}`' for ref in f.entity_refs) or '—'} | "
            f"{f.resolution or '—'} |"
            for f in by_class[class_name]
        ]
        out += ["", "</details>", ""]

    out += ["## Sub-reports", ""]
    out += [f"- [{title}]({file})" for title, file in sorted(report.sub_reports.items())]
    return "\n".join(out).rstrip() + "\n"


def write_reports(
    report: ValidationReport, *, directory: Path, sub_reports: Mapping[str, str]
) -> Path:
    """Write `report.json`, `report.md`, and each sub-report. Returns the directory written."""
    directory.mkdir(parents=True, exist_ok=True)
    write_tree_file(directory / "report.json", report_json(report))
    (directory / "report.md").write_bytes(render_report_markdown(report).encode("utf-8"))
    for key, body in sorted(sub_reports.items()):
        file_name = SUB_REPORT_FILES.get(key, f"{key.replace('_', '-')}.md")
        (directory / file_name).write_bytes(body.encode("utf-8"))
    return directory


def blocking_codes(findings: Sequence[Finding]) -> list[str]:
    """The unresolved blocking codes, sorted — what the CLI names on stdout (FR-029)."""
    return sorted(
        {
            finding.finding_code
            for finding in findings
            if finding.severity is Severity.BLOCKING and not finding.is_suppressed
        }
    )
