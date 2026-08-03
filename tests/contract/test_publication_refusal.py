# AI-Assisted: Claude Code (model: claude-opus-5) - Publication-refusal tests (task T087): a run
# holding any unresolved blocking finding exits 30, names the blocking findings, reaches no
# publication code path, and there is no override flag anywhere in the operator surface (FR-029,
# SC-005).
"""There is no override flag.

FR-029 is not "publication is discouraged while a blocking finding stands" — it is that the run
*cannot* publish. So this file asserts three separate things, because any one of them alone can
be true while the guarantee is false: the exit code, the absence of any published artifact, and
the absence of an escape hatch in the CLI surface. The only ways past a blocking finding are to
fix the data or to record a dated resolution.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from pipeline.build.manifest import MANIFEST_PATHS
from pipeline.cli import build_parser, run_build, run_validate
from pipeline.config import load_config
from pipeline.curate.prior import read_curated_tree
from pipeline.exit_codes import ExitCode
from pipeline.models.findings import Severity, Verdict

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
DISAGREEMENTS = FIXTURES / "disagreements"


def build(tmp_path: Path):
    return run_build(
        config=load_config(env={}),
        rules_version_id="fixture-disagreements",
        fixtures_dir=DISAGREEMENTS,
        offline=True,
        output_root=tmp_path / "out",
        reports_root=tmp_path,
        prior_dir=DISAGREEMENTS / "previous",
        published_at="2026-08-02T00:00:00Z",
    )


def test_a_blocking_finding_refuses_publication_with_exit_30(tmp_path: Path) -> None:
    result = build(tmp_path)

    blocking = [
        f for f in result.findings if f.severity is Severity.BLOCKING and not f.is_suppressed
    ]
    assert blocking, "the disagreement set is authored to hold blocking findings"
    assert result.exit_code is ExitCode.BLOCKING
    assert result.report.verdict is Verdict.BLOCKED


def test_the_blocking_findings_are_named(tmp_path: Path) -> None:
    result = build(tmp_path)

    codes = {f.finding_code for f in result.findings if f.severity is Severity.BLOCKING}
    assert "REC-NEVER-PRICED" in codes, "a unit no source has ever priced"
    assert "CON-BAND-GAP" in codes, "a point limit the snapshot cannot validate"


def test_no_publication_artifact_is_produced(tmp_path: Path) -> None:
    result = build(tmp_path)

    for relative in MANIFEST_PATHS.values():
        assert not (result.output_root / "site" / relative).exists()
    assert not list((tmp_path / "out").rglob("manifest.json"))


def test_the_report_is_still_written_and_its_path_is_returned(tmp_path: Path) -> None:
    result = build(tmp_path)

    assert result.report_path is not None
    assert (result.report_path / "report.json").is_file()
    assert (result.report_path / "report.md").is_file(), (
        "every run produces the report, whether or not it publishes (FR-031)"
    )


def test_validate_re_runs_from_the_tree_without_acquiring_anything(tmp_path: Path) -> None:
    """`validate` is answerable from the checkout alone — no source, no network (contract §1).

    The socket guard in `conftest` is the other half of this assertion: if the re-run reached
    either upstream, the test would fail on the connection rather than on the verdict.
    """
    root = tmp_path / "checkout"
    shutil.copytree(DISAGREEMENTS / "curation", root / "curation")
    shutil.copytree(DISAGREEMENTS / "previous" / "site", root / "site")
    run_build(
        config=load_config(env={}),
        rules_version_id="fixture-disagreements",
        fixtures_dir=DISAGREEMENTS,
        offline=True,
        output_root=root,
        reports_root=tmp_path,
        prior_dir=DISAGREEMENTS / "previous",
        published_at="2026-08-02T00:00:00Z",
    )

    exit_code, report, directory = run_validate(
        config=load_config(env={}),
        rules_version_id="fixture-disagreements",
        repository_root=root,
        reports_root=tmp_path / "revalidated",
    )

    assert exit_code is ExitCode.BLOCKING
    assert report.verdict is Verdict.BLOCKED
    assert "CON-BAND-GAP" in {f.finding_code for f in report.findings}
    assert directory is not None and (directory / "report.md").is_file()


def test_the_pricing_carry_forward_survives_the_round_trip(tmp_path: Path) -> None:
    """A rebuild rewrites `data/` wholesale, so the bookkeeping has to be *in* the tree."""
    root = tmp_path / "checkout"
    shutil.copytree(DISAGREEMENTS / "curation", root / "curation")
    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-disagreements",
        fixtures_dir=DISAGREEMENTS,
        offline=True,
        output_root=root,
        reports_root=tmp_path,
        prior_dir=DISAGREEMENTS / "previous",
        published_at="2026-08-02T00:00:00Z",
    )

    read_back = read_curated_tree(root / "data" / "wh40k-11e")
    assert read_back is not None

    written = {d.datasheet_id: d.pricing_confidence for d in result.snapshot.datasheets}
    recovered = {d.datasheet_id: d.pricing_confidence for d in read_back.datasheets}
    assert recovered == written, (
        "unverified_since_version and the consecutive count are only meaningful if they survive"
    )


def test_the_operator_surface_carries_no_override_flag() -> None:
    parser = build_parser()

    rendered = parser.format_help().lower()
    for escape_hatch in ("--force", "--override", "--ignore-blocking", "--allow-blocking", "--yes"):
        assert escape_hatch not in rendered
