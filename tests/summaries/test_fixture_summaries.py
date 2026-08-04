# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the fixture-summary integration test
# (task T133): exercises the ability-summary state machine against real fixture files, not a
# synthetic snapshot, using the mixed-state records seeded in
# fixtures/sample/curation/abilities/ and the fully-approved records in
# fixtures/minimal/curation/abilities/ (FR-020, research D10).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Gave both `run_build` calls a throwaway
# `temp_repo()` repository_root (CI run 30936394229 on PR #1, candidate/mfm-2026-08): without
# it, the coverage-collapse baseline fell back to the ambient checkout's real data/ tree
# whenever one was present, raising a spurious COV-COLLAPSE unrelated to ability summaries.
"""`curation/abilities/` fixture data, exercised against the real fixture files.

`fixtures/minimal` is what US1's own tests already build end to end (`test_minimal_fixture_
bundle.py`); this module adds the one thing they do not check — that its ability summaries are
not merely present but **current**, keyed under the documented fixture digest key
(`fixtures/README.md`). `fixtures/sample` seeds one of each `draft`, `in_review`, and
`needs_rereview` state precisely so real fixture text demonstrates each of the three catalogued
blocking codes, not only the unit-level state machine in `test_state_machine.py`.

`fixtures/sample` cannot be run through `pipeline.cli.run_build` — one of its two MFM pages is
*deliberately* structurally broken (task T041, `SRC-STRUCTURE-CHANGED`) to exercise the swap
replay's failure path, so a full build of that set always refuses before curate even starts.
This module reads its detail-source CSVs and authored tree directly instead, the same inputs
`assemble()` would see, and drives them through `pipeline.curate.summaries` and
`pipeline.validate.summaries` exactly as a full build's curate/validate stages would.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from pipeline.cli import run_build
from pipeline.config import load_config
from pipeline.curate.authored import load_authored
from pipeline.curate.summaries import compute_current_digests
from pipeline.models.findings import Severity
from pipeline.parse.wahapedia_csv import read_text as read_csv_text
from pipeline.validate.summaries import check_summaries
from tests.factories import datasheet, snapshot

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE = REPO_ROOT / "fixtures" / "sample"
FIXTURE_DIGEST_KEY = b"fixture-mechanic-digest-key"


def test_fixtures_minimal_summaries_are_fully_approved_and_current(
    tmp_path: Path, temp_repo: Callable[[], Path]
) -> None:
    result = run_build(
        config=load_config(env={"WGC_MECHANIC_DIGEST_KEY": FIXTURE_DIGEST_KEY.decode()}),
        rules_version_id="fixture-minimal-summaries",
        fixtures_dir=REPO_ROOT / "fixtures" / "minimal",
        offline=True,
        output_root=tmp_path,
        # `fixtures/minimal` has no `previous/` of its own, so without an explicit throwaway
        # `repository_root` the build would fall back to the ambient checkout's `data/` as its
        # coverage baseline — hermetic on `main` (empty `data/`) but not on a branch that carries
        # a real published tree. `temp_repo` (tests/conftest.py) gives it an empty one always.
        repository_root=temp_repo(),
    )

    sum_findings = [f for f in result.findings if f.finding_code.startswith("SUM-")]
    assert sum_findings == []


def test_a_run_with_no_digest_key_never_flips_an_approved_summary(
    tmp_path: Path, temp_repo: Callable[[], Path]
) -> None:
    """Without WGC_MECHANIC_DIGEST_KEY there is no fresh text to compare against, so every key
    fixtures/minimal stores as `approved` stays `approved` — no SUM-NEEDS-REREVIEW appears, even
    though it would if the digest key were set and the source text had moved (it has not, here;
    see the "current" test above for the case where it does)."""
    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-minimal-no-key",
        fixtures_dir=REPO_ROOT / "fixtures" / "minimal",
        offline=True,
        output_root=tmp_path,
        repository_root=temp_repo(),
    )

    sum_findings = [f for f in result.findings if f.finding_code.startswith("SUM-")]
    assert sum_findings == []


def test_fixtures_sample_realises_all_three_blocking_summary_codes() -> None:
    detail = {
        name: read_csv_text(name, (SAMPLE / "wahapedia" / name).read_text(encoding="utf-8"))
        for name in ("Datasheets_abilities.csv", "Abilities.csv")
    }
    authored = load_authored(SAMPLE / "curation")
    current_digests = compute_current_digests(detail, key=FIXTURE_DIGEST_KEY)

    emberwrights = datasheet(
        datasheet_id="ds-ew-sample",
        faction_id="f-emberwrights",
        ability_keys=(
            "core:deep-strike",
            "core:leader",
            "datasheet:ember-shield",
            "datasheet:slag-wake",
            "datasheet:kindling-surge",
            "faction:oath-of-ember",
        ),
    )
    glasswold = datasheet(
        datasheet_id="ds-gc-sample",
        faction_id="f-glasswold-covenant",
        ability_keys=("datasheet:glass-veil",),
    )
    snap = snapshot(
        datasheets=[emberwrights, glasswold], ability_summaries=authored.ability_summaries
    )

    findings = check_summaries(
        snap,
        authored_summaries=authored.ability_summaries,
        current_digests=current_digests,
        summary_max_chars=240,
    )

    sum_codes_by_key = {finding.entity_refs[0]: finding.finding_code for finding in findings}

    # core:leader is "in_review" and faction:oath-of-ember is "draft" — both SUM-UNAPPROVED.
    assert sum_codes_by_key["core:leader"] == "SUM-UNAPPROVED"
    assert sum_codes_by_key["faction:oath-of-ember"] == "SUM-UNAPPROVED"
    # datasheet:kindling-surge is stored "needs_rereview" outright.
    assert sum_codes_by_key["datasheet:kindling-surge"] == "SUM-NEEDS-REREVIEW"
    # The remaining used keys are approved and current — no finding for any of them.
    approved_and_current = {
        "core:deep-strike",
        "datasheet:ember-shield",
        "datasheet:slag-wake",
        "datasheet:glass-veil",
    }
    assert approved_and_current.isdisjoint(sum_codes_by_key)

    assert all(finding.severity is Severity.BLOCKING for finding in findings)
