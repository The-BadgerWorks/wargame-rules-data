# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the summary-coverage report test
# suite (task T125), confirmed failing before pipeline.report.coverage existed: the report
# states count and proportion before the enumeration, and names every ability lacking an
# approved summary, per faction (FR-025, FR-031, validation-report.md §1.3).
"""`summary-coverage.md`: the standing editorial backlog, stated before it is enumerated."""

from __future__ import annotations

from pipeline.models.authored import AbilitySummary, ReviewState
from pipeline.report.coverage import render_summary_coverage
from tests.factories import datasheet, snapshot


def _summary(
    key: str, *, review_state: ReviewState, mechanic_digest: str = "d" * 32
) -> AbilitySummary:
    return AbilitySummary(
        ability_key=key,
        name=key.split(":")[-1].replace("-", " ").title(),
        summary="Invented mechanics-only summary authored for this data set.",
        review_state=review_state,
        mechanic_digest=mechanic_digest,
        reviewed_by="curator",
        reviewed_at="2026-06-13T00:00:00Z",
    )


def test_scale_line_leads_the_report_before_any_enumeration() -> None:
    ds = datasheet(faction_id="f-emberwrights", ability_keys=("core:deep-strike", "core:leader"))
    snap = snapshot(datasheets=[ds])
    authored = {
        "core:deep-strike": _summary("core:deep-strike", review_state=ReviewState.APPROVED),
        "core:leader": _summary("core:leader", review_state=ReviewState.DRAFT),
    }

    rendered = render_summary_coverage(snap, authored_summaries=authored)
    lines = rendered.splitlines()

    assert lines[0] == "# Summary coverage"
    scale_line = next(line for line in lines if line.startswith("**"))
    scale_index = lines.index(scale_line)
    table_index = next(i for i, line in enumerate(lines) if line.startswith("|"))
    assert scale_index < table_index
    assert "1" in scale_line and "2" in scale_line and "50.0%" in scale_line


def test_names_every_ability_lacking_an_approved_summary() -> None:
    ds = datasheet(faction_id="f-emberwrights", ability_keys=("core:deep-strike", "core:leader"))
    snap = snapshot(datasheets=[ds])
    authored = {
        "core:deep-strike": _summary("core:deep-strike", review_state=ReviewState.APPROVED),
        "core:leader": _summary("core:leader", review_state=ReviewState.IN_REVIEW),
    }

    rendered = render_summary_coverage(snap, authored_summaries=authored)

    assert "`core:leader`" in rendered
    assert "core:deep-strike`" not in rendered.split("outstanding")[-1].split("core:leader")[0]


def test_a_key_with_no_authored_record_at_all_is_named_outstanding() -> None:
    ds = datasheet(faction_id="f-emberwrights", ability_keys=("core:deep-strike",))
    snap = snapshot(datasheets=[ds])

    rendered = render_summary_coverage(snap, authored_summaries={})

    assert "`core:deep-strike`" in rendered
    assert "0 / 1" in rendered


def test_a_stale_digest_counts_as_outstanding_even_though_curation_still_says_approved() -> None:
    """The coverage figure and the blocking SUM-NEEDS-REREVIEW check must never disagree about
    one key's status, or an approver reading a clean-looking coverage table would be misled."""
    ds = datasheet(faction_id="f-emberwrights", ability_keys=("core:deep-strike",))
    snap = snapshot(datasheets=[ds])
    authored = {
        "core:deep-strike": _summary(
            "core:deep-strike", review_state=ReviewState.APPROVED, mechanic_digest="d" * 32
        )
    }

    rendered = render_summary_coverage(
        snap, authored_summaries=authored, current_digests={"core:deep-strike": "9" * 32}
    )

    assert "`core:deep-strike`" in rendered
    assert "0 / 1" in rendered


def test_an_unchanged_digest_counts_as_approved() -> None:
    ds = datasheet(faction_id="f-emberwrights", ability_keys=("core:deep-strike",))
    snap = snapshot(datasheets=[ds])
    authored = {
        "core:deep-strike": _summary(
            "core:deep-strike", review_state=ReviewState.APPROVED, mechanic_digest="d" * 32
        )
    }

    rendered = render_summary_coverage(
        snap, authored_summaries=authored, current_digests={"core:deep-strike": "d" * 32}
    )

    assert "1 / 1" in rendered


def test_breaks_down_per_faction() -> None:
    ember = datasheet(
        datasheet_id="ds-ember-sentinel", faction_id="f-emberwrights", ability_keys=("core:leader",)
    )
    ashen = datasheet(
        datasheet_id="ds-ashen-warden",
        faction_id="f-ashen-vigil",
        ability_keys=("core:deep-strike",),
    )
    snap = snapshot(datasheets=[ember, ashen])
    authored = {
        "core:leader": _summary("core:leader", review_state=ReviewState.APPROVED),
        "core:deep-strike": _summary("core:deep-strike", review_state=ReviewState.DRAFT),
    }

    rendered = render_summary_coverage(snap, authored_summaries=authored)

    assert "| `f-ashen-vigil` | 0 / 1 | `core:deep-strike` |" in rendered
    assert "| `f-emberwrights` | 1 / 1 | — |" in rendered
