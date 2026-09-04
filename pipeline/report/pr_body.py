# AI-Assisted: Claude Code (model: claude-opus-5) - Extended the reviewer view for the enriched
# release (004 task T084): the per-class authored-summary coverage table, each class's gate state
# beside its figure, and the churn dry-run reference. The four classes get their own table rather
# than four more rows in Scale, because Scale answers "how big is this?" and a gated class answers
# "may this ship?" -- and because a class at 100% with its gate OFF and a class at 5% with its gate
# ON are the two states an approver most needs told apart.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the candidate reviewer view
# (task T119): the PR body assembles, in the approver's reading order, the verdict and scale
# table, the change summary, the unverified-pricing and edition-mismatch reports, the
# summary-coverage report, and a pointer to the changed-file list that names the changed
# datasheets (FR-037, quickstart.md §5).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the loadout coverage table and the
# option-regression pointer (006 task T039): the two `loadout.*` rows say which of them the
# ratchet guards, and FR-009's zero-regression evidence gets a named place in the reading order
# rather than living in a report nobody is told to open (006 FR-022).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 008 task T062: `default_equipment` joins
# `options_resolved` as a figure the table marks "blocks below X%" (the two-step ratchet, FR-021)
# -- the explanatory footer is rewritten to match, since it used to explain why the figure had NO
# ratchet.
"""What an approver reads first, in the order they should read it.

`docs/approval-checklist.md` (task T121) states the same order in prose, for a human skimming
the repository rather than reading a generated PR. Keeping both in one place would be neater,
but the checklist has to be readable *before* any candidate exists, so this module and that
document agree by convention rather than by import.

This module reads the same JSON `report.json` already writes (`validation-report.md` §2) rather
than the in-process :class:`~pipeline.models.findings.ValidationReport` object, on purpose:
`candidate.yml` runs `build` as one process and assembles the PR body as a separate shell step
afterwards (`tools/render_pr_body.py`), so the input this module actually has at that point is
the file on disk, and testing against that same shape is what keeps the test honest about it.

Nothing here re-derives a verdict or re-classifies a finding — every fact rendered was already
computed by the `validate` stage; this module only orders and links it the way FR-037 asks for.
**A clean report changes none of this ordering or content** — `docs/approval-checklist.md` says
explicitly what a clean report does not excuse, and this module has no code path that skips a
section because nothing was found in it.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from pipeline.models.findings import Verdict
from pipeline.report.validation import SUB_REPORT_FILES, VERDICT_LINE

#: The approver's reading order (FR-037): verdict and scale first (can this ship, and how much
#: of it is uncertain?), then what changed, then the two provenance-quality reports, then the
#: editorial backlog. Deliberately not `SUB_REPORT_FILES`' own iteration order, which is
#: alphabetical and was never meant to be a reading order.
READING_ORDER: tuple[str, ...] = (
    "change_summary",
    "unverified_pricing",
    "edition_mismatch",
    "summary_coverage",
)

_SECTION_TITLE: Mapping[str, str] = {
    "change_summary": "What changed",
    "unverified_pricing": "Unverified pricing",
    "edition_mismatch": "Edition mismatch",
    "summary_coverage": "Authored summary coverage, all four classes",
}


#: The `coverage` key prefix the four authored-summary classes report under.
_SUMMARY_COVERAGE_PREFIX = "summaries."

#: Where the churn dry-run's measured re-review wave is recorded (research D8, 004 T075/T076).
_CHURN_DRY_RUN_DIR = "reports/churn-dry-run"

#: The `coverage` key prefix `006`'s two loadout figures report under.
_LOADOUT_COVERAGE_PREFIX = "loadout."

#: The loadout figures the ratchet guards -- both, since `008`'s 2026-08-15 two-step ruling
#: (FR-021). `item_constraints` and `rendering_equivalence` (`007` FR-022, PO decision
#: 2026-08-13) are still absent -- new report-only baselines with no prior release to compare
#: against -- and a table that showed every figure without saying which is which would let an
#: approver read a falling unratcheted number as something a gate had already considered.
_RATCHETED_LOADOUT_FIGURES: frozenset[str] = frozenset({"options_resolved", "default_equipment"})

#: `pipeline.cli option-regression`'s report: FR-009's layer-2 evidence, rebuilt from the previous
#: published version's own source rows and diffed per choice and per field.
_OPTION_REGRESSION_FILE = "option-regression.md"


def _loadout_coverage_section(coverage: Mapping[str, Mapping[str, Any]]) -> list[str]:
    """`006`'s two loadout figures, and which of them can refuse a release.

    Separate from the summary table above rather than folded into it, because they answer
    different questions: that one is editorial backlog a curator works through, this one is how
    much of the source the *pipeline* managed to resolve. A curator cannot act on this row by
    writing anything, and an approver reading them as one list would be looking for the wrong
    kind of fix.
    """
    figures = {
        key.removeprefix(_LOADOUT_COVERAGE_PREFIX): figure
        for key, figure in sorted(coverage.items())
        if key.startswith(_LOADOUT_COVERAGE_PREFIX)
    }
    if not figures:
        return []

    out = [
        "",
        "## Loadout coverage",
        "",
        "| figure | resolved | of the previous release | resolved coverage | ratchet |",
        "|---|---|---|---|---|",
    ]
    for name, figure in figures.items():
        floor = round(float(figure.get("threshold", 0.0)) * 100)
        guard = f"blocks below {floor}%" if name in _RATCHETED_LOADOUT_FIGURES else "reported only"
        out.append(
            f"| `{name}` | {figure.get('current', 0)} | {figure.get('previous', 0)} | "
            f"{figure.get('ratio_percent', 0)}% | {guard} |"
        )
    out += [
        "",
        "`options_resolved` and `default_equipment` are **both ratcheted, with no absolute "
        "ceiling on either** (`008` FR-021, Clarifications 2026-08-15 Q2's two-step ruling): "
        "each must not fall below the previous *published* version's own percent, less its own "
        "configured tolerance, and no threshold blocks a release on its own — so source-wording "
        "drift cannot wedge a release ahead of a parser fix. A rejected candidate never moves "
        "either baseline. `default_equipment` reported without a ratchet in `006`'s first "
        "extended release, because no version had yet published the figure to compare against "
        "(research D4); two releases later that baseline exists, and the ratchet is on. "
        "`item_constraints` and `rendering_equivalence` (`007` US5) are still new report-only "
        "baselines, reported from their first release and ratcheted by no version of this "
        "pipeline yet (PO decision 2026-08-13, untouched by this feature). "
        "`rendering_equivalence_not_compared` is a **raw count**, not a proportion — read its "
        "`resolved` column, not its `%`, which is always 100 by construction: it is the number "
        "of datasheet/block comparisons the check could not make this run (source unavailable, "
        "or the rendered block legitimately empty), excluded from `rendering_equivalence`'s own "
        "numerator and denominator so a shrinking denominator can never read as an improving "
        "figure.",
    ]
    return out


def _summary_coverage_section(coverage: Mapping[str, Mapping[str, Any]]) -> list[str]:
    """The four classes' approved coverage, one row each, or nothing when none is reported.

    Rendered separately from Scale on purpose. Scale is "how big is this candidate"; this is "may
    it ship, and what is still outstanding" — and a class sitting at 100% with its gate off is a
    materially different thing from one sitting at 5% with its gate on. An approver who cannot
    tell those apart at a glance is being asked to approve on the wrong information.

    A class whose gate is on and whose coverage is short would already have raised a blocking
    finding, so this table never *decides* anything. It exists so the approver sees the shape of
    the editorial backlog without opening `summary-coverage.md`.
    """
    classes = {
        key.removeprefix(_SUMMARY_COVERAGE_PREFIX): figure
        for key, figure in sorted(coverage.items())
        if key.startswith(_SUMMARY_COVERAGE_PREFIX)
    }
    if not classes:
        return []

    out = [
        "",
        "## Authored summary coverage",
        "",
        "| class | approved | of the previous release | approved coverage |",
        "|---|---|---|---|",
    ]
    out += [
        f"| `{name}` | {figure.get('current', 0)} | {figure.get('previous', 0)} | "
        f"{figure.get('ratio_percent', 0)}% |"
        for name, figure in classes.items()
    ]
    out += [
        "",
        "Each class's gate is switched independently and a gate selects a *code*, never a "
        "severity — a class below full coverage with its gate off is outstanding editorial work, "
        "not a defect, and appears above rather than under **Blocking findings**. Which gates are "
        "on for this build is recorded in `docs/verification/gate-switch-on-rehearsal.md`.",
        "",
        f"The re-review wave every ability summary was measured against is in "
        f"[`{_CHURN_DRY_RUN_DIR}/`]({_CHURN_DRY_RUN_DIR}/) — the churn dry run is what sizes an "
        "ability re-review campaign, and it runs before the campaign, never after it.",
    ]
    return out


def _carried_line(finding: Mapping[str, Any]) -> str:
    """One `SRC-FACTION-CARRIED-FORWARD` row (R06a-fix item 4).

    The per-class composition (009 rung R06a, T096, FR-033) reuses this same code and detail
    shape for a four-field freeze, distinguished only by `detail.data_class` being present. Left
    unrendered, a reader sees "frozen (N datasheets)" and reads it as the WHOLE datasheet frozen
    whole-faction-style — the four-field freeze is a much smaller, much less alarming thing, and
    a reader who cannot tell them apart is being asked to approve on the wrong information.
    """
    detail = finding["detail"]
    base = (
        f"- `{detail.get('faction_id')}` frozen at `{detail.get('frozen_at_version')}` "
        f"({detail.get('datasheets_carried')} datasheet(s))"
    )
    data_class = detail.get("data_class")
    if data_class is None:
        return base
    return f"{base} — **`{data_class}` class only**, not the whole datasheet"


def _carried_forward_section(findings: Sequence[Mapping[str, Any]]) -> list[str]:
    """008 FR-025 (Product Owner decision 2026-08-17): every carry-forward substitution named
    explicitly, never left to a reviewer noticing an advisory finding among thousands of others.

    Renders **only** when at least one `SRC-FACTION-CARRIED-FORWARD` or
    `SRC-FACTION-CARRY-FORWARD-UNUSED` finding exists this run — a candidate with no declarations
    active gets no section at all, so its absence is itself the "nothing was substituted" signal.

    R06a-fix2 item 2: `SRC-FACTION-CARRIED-FORWARD` covers TWO different facts (`_carried_line`'s
    own docstring) — a whole-faction freeze (`detail.data_class` absent), where the faction truly
    could not be fetched this run, and a per-class freeze (`detail.data_class` present), which
    happens exactly when the configured arm DID fetch the faction and only one class's own
    declared arm did not. Rendering both under one "could not be fetched this run" heading states
    something false of every per-class row, and — because the same slug can simultaneously be
    `unused` with `answers_per_faction: False` under a bulk hybrid (FR-032) — puts one faction
    under two headings that contradict each other. Split into two headings, each true of the rows
    under it, so a reader sees one coherent statement per faction.
    """
    carried = [f for f in findings if f.get("finding_code") == "SRC-FACTION-CARRIED-FORWARD"]
    unused = [f for f in findings if f.get("finding_code") == "SRC-FACTION-CARRY-FORWARD-UNUSED"]
    if not carried and not unused:
        return []

    whole_faction = [f for f in carried if f["detail"].get("data_class") is None]
    per_class = [f for f in carried if f["detail"].get("data_class") is not None]

    out = ["", "## Carried-forward factions", ""]
    if whole_faction:
        out.append(
            "**These factions could not be fetched this run and are frozen at the previous "
            "published version** (`curation/carried-forward-factions.json`):"
        )
        out += [_carried_line(f) for f in whole_faction]
    if per_class:
        if whole_faction:
            out.append("")
        out.append(
            "**These factions were fetched successfully this run overall — only one data "
            "class's own declared arm could not answer for them, and just that class is frozen "
            "at the previous published version** (`curation/detail-source-authority.json`):"
        )
        out += [_carried_line(f) for f in per_class]
    if unused:
        if whole_faction or per_class:
            out.append("")
        # R06a-fix item 3: `detail.answers_per_faction` (default True — an older report without
        # the field predates this rung and behaved as `html` always did) tells apart a genuine
        # per-faction fetch from a bulk arm's all-or-nothing answer. "This arm cannot answer
        # per-faction at all" and "this faction answered live, so retire the declaration" are
        # opposite facts, and only the first is true under a bulk arm — rendering the second for
        # it would advise deleting the declaration that stops the per-faction sweep hard-failing
        # once the arm returns to it.
        per_faction = [f for f in unused if f["detail"].get("answers_per_faction", True)]
        bulk_answered = [f for f in unused if not f["detail"].get("answers_per_faction", True)]
        if per_faction:
            out.append(
                "**These declarations were not needed this run** — the source answered live, so "
                "the declaration in `curation/carried-forward-factions.json` may be retired:"
            )
            out += [f"- `{f['detail'].get('faction_slug')}`" for f in per_faction]
        if bulk_answered:
            if per_faction:
                out.append("")
            out.append(
                "**These declarations were not evaluated per faction this run — do not retire "
                "them.** The configured detail arm answers as one bulk export, never one page "
                "per faction, so a declared faction showing here as unused is not evidence its "
                "own page would still be reachable; retiring it now would remove the guard that "
                "stops the per-faction sweep hard-failing once the arm returns to it:"
            )
            out += [f"- `{f['detail'].get('faction_slug')}`" for f in bulk_answered]
    return out


def render_pr_body(
    report_json: Mapping[str, Any], *, reports_relative_dir: str | None = None
) -> str:
    """The candidate PR body: verdict, scale, then a pointer to each sub-report in reading order.

    ``report_json`` is exactly what :func:`pipeline.report.validation.report_json` produces and
    ``write_reports`` writes to ``reports/<rulesVersionId>/report.json`` — this function's only
    job is to read it back and order it for a reviewer. ``reports_relative_dir`` is where the
    sub-report files live relative to the PR diff root, defaulting to the real repository's
    ``reports/<rulesVersionId>``.
    """
    rules_version_id = str(report_json["rules_version_id"])
    directory = reports_relative_dir or f"reports/{rules_version_id}"
    verdict = Verdict(report_json["verdict"])
    scale: Mapping[str, Mapping[str, Any]] = report_json["scale"]
    findings: Sequence[Mapping[str, Any]] = report_json["findings"]
    sub_reports: Mapping[str, str] = report_json.get("sub_reports", SUB_REPORT_FILES)

    out: list[str] = [
        f"Candidate `{rules_version_id}`. Never auto-published — see "
        "`.github/workflows/publish.yml` for the approval gate.",
        "",
        VERDICT_LINE[verdict],
        "",
        "## Scale",
        "",
        "| category | count | proportion of the snapshot |",
        "|---|---|---|",
    ]
    out += [
        f"| {name.replace('_', ' ')} | {figure['count']} | {figure['proportion_percent']}% |"
        for name, figure in sorted(scale.items())
    ]

    out += _carried_forward_section(findings)
    out += _summary_coverage_section(report_json.get("coverage") or {})
    out += _loadout_coverage_section(report_json.get("coverage") or {})

    blocking = [f for f in findings if f.get("severity") == "blocking" and not f.get("resolution")]
    out += ["", "## Blocking findings", ""]
    if not blocking:
        out.append("None.")
    else:
        out += [
            f"- `{finding['finding_code']}` "
            f"{', '.join(finding.get('entity_refs', ())) or '(snapshot-wide)'}"
            for finding in blocking
        ]

    out += ["", "## Reports, in reading order", ""]
    for key in READING_ORDER:
        file_name = sub_reports.get(key, SUB_REPORT_FILES[key])
        out.append(f"1. [{_SECTION_TITLE[key]}]({directory}/{file_name})")
    out.append(f"1. [Full validation report]({directory}/report.md)")
    # FR-022: the zero-regression evidence is named here rather than left to whoever remembers
    # it exists. It is written by `rules-pipeline option-regression`, which is evidence tooling
    # and deliberately NOT on the approval-gate path -- so the link is stated unconditionally,
    # and its absence is itself something an approver is meant to notice.
    out.append(
        f"1. [Option-regression evidence]({directory}/{_OPTION_REGRESSION_FILE}) — "
        "`rules-pipeline option-regression` rebuilds the previous published version's option "
        "tree with this pipeline and diffs it per choice and per field. A non-empty "
        "**Corrected** section means a new production reached a row the baseline already "
        "resolved, which FR-009 forbids."
    )

    out += [
        "",
        "## Changed datasheets",
        "",
        "The **Files changed** tab names every changed, added, or removed datasheet directly — "
        "one JSON file per datasheet under `data/wh40k-11e/factions/*/datasheets/` — so the "
        "file list alone is the fastest way to see the scope of this candidate before reading "
        "any report (research D3).",
    ]
    return "\n".join(out).rstrip() + "\n"
