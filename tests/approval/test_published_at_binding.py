# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the published-at binding tests after
# the 006 release hit exit 51 on a rebuild that crossed 00:00Z. `published_at` was documented as
# a build input (`pipeline/cli.py`'s `run_build` docstring, curated-snapshot-format.md §6) and
# was never reachable from the CLI, so `publish.yml`'s rebuild stamped the DISPATCH day and the
# FR-039 assertion compared an approved bundle against a differently dated one (FR-033, FR-039).
"""Tests for FR-033/FR-039: the published date is an input, and a rebuild honours the approval.

The failure this pins is not a wrong value — it is a value the operator surface had no way to
supply. `curated-snapshot-format.md` §6 says the build must produce a byte-identical bundle from
an unchanged tree and that `snapshotMeta.publishedAt` is "an explicit build input rather than
'now'". Until this fix the only input was the wall clock, so an unchanged tree produced two
different bundles either side of midnight UTC and the approval assertion refused the rebuild it
was supposed to authorise.

Every test here drives the real `rules-pipeline build` command against the synthetic `minimal`
fixture set, copied out of the repository first: the defect lived in the CLI wiring, so a test
that called `run_build` directly (which has always taken `published_at`) would have passed
against the broken build and proved nothing.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pytest

from pipeline.cli import main as cli_main
from pipeline.exit_codes import ExitCode

FIXTURES_ROOT = Path(__file__).resolve().parents[2] / "fixtures"
MINIMAL = FIXTURES_ROOT / "minimal"

#: The candidate's own build date. Deliberately not today: every assertion below is about a
#: rebuild that happens on a *different* day from the build it must reproduce, which is the
#: whole of the defect.
CANDIDATE_DAY = "2026-01-02T00:00:00Z"

RULES_VERSION_ID = "fixture-published-at"


@pytest.fixture
def fixture_copy(tmp_path: Path) -> Path:
    """A private copy of `fixtures/minimal`, because a CLI build writes into the fixture set.

    `run_build` sends a fixture-sourced run's output to `<fixtures>/build/`, and
    `fixtures/minimal/build/` is a **committed** artifact the consuming app's CI ingests
    (FR-048, `.gitignore`'s own note). A test that built against the real path would rewrite a
    reviewed file as a side effect of asserting something else entirely.
    """
    if not MINIMAL.is_dir():
        pytest.skip(f"fixture set 'minimal' does not exist ({MINIMAL})")
    destination = tmp_path / "minimal"
    shutil.copytree(MINIMAL, destination)
    shutil.rmtree(destination / "build", ignore_errors=True)
    return destination


@pytest.fixture
def build(
    fixture_copy: Path, throwaway_repository_root: Path
) -> Callable[..., tuple[int, dict[str, object]]]:
    """Run `rules-pipeline build` against the copy and return the exit code and the bundle."""

    def _run(*options: str, expect: int | None = None) -> tuple[int, dict]:  # type: ignore[type-arg]
        code = cli_main(
            [
                "build",
                "--offline",
                "--fixtures",
                str(fixture_copy),
                "--rules-version-id",
                RULES_VERSION_ID,
                *options,
            ]
        )
        # A synthetic set carries advisory findings by construction (its slugs are invented), so
        # a successful build is 0 or 20 — the pair `candidate.yml` and `publish.yml` both accept.
        allowed = (
            {expect} if expect is not None else {int(ExitCode.SUCCESS), int(ExitCode.ADVISORY_ONLY)}
        )
        assert code in allowed, f"build {' '.join(options)} exited {code}, expected {allowed}"
        bundle_path = fixture_copy / "build" / f"rules-{RULES_VERSION_ID}.json"
        if not bundle_path.is_file():
            return code, {}
        return code, json.loads(bundle_path.read_bytes().decode("utf-8"))

    return _run


def _recorded(fixture_copy: Path) -> dict:  # type: ignore[type-arg]
    report = fixture_copy / "build" / "reports" / RULES_VERSION_ID / "report.json"
    return json.loads(report.read_bytes().decode("utf-8"))


# --- the defect, and its fix ---------------------------------------------------------------


def test_a_rebuild_on_a_later_day_reproduces_the_approved_bundle(
    build: Callable[..., tuple[int, dict]],  # type: ignore[type-arg]
    fixture_copy: Path,
) -> None:
    """The regression. Pre-fix this cannot even be expressed: the flags did not exist.

    The candidate is built on its own day; the rebuild runs today, from the same tree, and must
    produce the same bytes — which is precisely what `publish.yml` asserts against
    `--expect-sha256` (FR-039) and what `curated-snapshot-format.md` §6 promises (FR-033).
    """
    _, approved = build("--published-at", CANDIDATE_DAY)
    approved_bytes = (fixture_copy / "build" / f"rules-{RULES_VERSION_ID}.json").read_bytes()
    assert approved["snapshotMeta"]["publishedAt"] == CANDIDATE_DAY
    assert CANDIDATE_DAY[:10] != datetime.now(UTC).date().isoformat(), (
        "this test only means anything when the rebuild happens on a different day"
    )

    _, rebuilt = build("--published-at-from-report")
    rebuilt_bytes = (fixture_copy / "build" / f"rules-{RULES_VERSION_ID}.json").read_bytes()

    assert rebuilt["snapshotMeta"]["publishedAt"] == CANDIDATE_DAY
    assert rebuilt_bytes == approved_bytes


def test_the_recorded_date_comes_from_the_checked_out_commits_own_report(
    build: Callable[..., tuple[int, dict]],  # type: ignore[type-arg]
    fixture_copy: Path,
) -> None:
    """`reports/<id>/report.json` is committed by `candidate.yml`, so the approved commit carries
    its own published date. Nothing a dispatcher types can disagree with the approval."""
    build("--published-at", CANDIDATE_DAY)
    assert _recorded(fixture_copy)["generated_at"] == CANDIDATE_DAY

    # Move the record, and the rebuild moves with it: the date is read, not remembered.
    moved = "2026-03-04T00:00:00Z"
    report_path = fixture_copy / "build" / "reports" / RULES_VERSION_ID / "report.json"
    recorded = _recorded(fixture_copy)
    recorded["generated_at"] = moved
    report_path.write_text(json.dumps(recorded), encoding="utf-8")

    _, rebuilt = build("--published-at-from-report")
    assert rebuilt["snapshotMeta"]["publishedAt"] == moved


def test_without_a_supplied_date_a_build_still_stamps_today(
    build: Callable[..., tuple[int, dict]],  # type: ignore[type-arg]
) -> None:
    """The first build of a fresh candidate: the build day IS the published date (`candidate.yml`).

    This is the behaviour the defect consisted of *only* on the rebuild path, so it is asserted
    rather than removed — and it is what makes the test above a real difference.
    """
    _, bundle = build()
    today = f"{datetime.now(UTC).date().isoformat()}T00:00:00Z"
    assert bundle["snapshotMeta"]["publishedAt"] == today
    assert bundle["snapshotMeta"]["publishedAt"] != CANDIDATE_DAY


def test_a_bare_date_is_accepted_and_normalised(
    build: Callable[..., tuple[int, dict]],  # type: ignore[type-arg]
) -> None:
    _, bundle = build("--published-at", "2026-01-02")
    assert bundle["snapshotMeta"]["publishedAt"] == CANDIDATE_DAY


# --- refusals: the fix must fail loudly, never quietly fall back to the clock ---------------


def test_a_missing_recorded_report_refuses_rather_than_stamping_today(
    build: Callable[..., tuple[int, dict]],  # type: ignore[type-arg]
) -> None:
    """A silent fallback here would rebuild the exact defect: a wrong date nobody sees until 51."""
    build("--published-at-from-report", expect=int(ExitCode.CONFIG_ERROR))


def test_a_recorded_report_without_a_date_refuses(
    build: Callable[..., tuple[int, dict]],  # type: ignore[type-arg]
    fixture_copy: Path,
) -> None:
    build("--published-at", CANDIDATE_DAY)
    report_path = fixture_copy / "build" / "reports" / RULES_VERSION_ID / "report.json"
    recorded = _recorded(fixture_copy)
    del recorded["generated_at"]
    report_path.write_text(json.dumps(recorded), encoding="utf-8")

    build("--published-at-from-report", expect=int(ExitCode.CONFIG_ERROR))


def test_the_two_date_options_are_mutually_exclusive(
    build: Callable[..., tuple[int, dict]],  # type: ignore[type-arg]
) -> None:
    """Two answers to one question is the shape of the bug, not a convenience."""
    build(
        "--published-at",
        CANDIDATE_DAY,
        "--published-at-from-report",
        expect=int(ExitCode.CONFIG_ERROR),
    )


@pytest.mark.parametrize(
    "value",
    ["", "yesterday", "2026-13-45", "2026-01-02T00:00:00", "2026-01-02T00:00:00+01:00"],
)
def test_a_malformed_date_is_an_invocation_error(
    build: Callable[..., tuple[int, dict]],  # type: ignore[type-arg]
    value: str,
) -> None:
    build("--published-at", value, expect=int(ExitCode.CONFIG_ERROR))


def test_a_refused_date_never_reaches_a_build(
    build: Callable[..., tuple[int, dict]],  # type: ignore[type-arg]
    fixture_copy: Path,
) -> None:
    """The check is up front: a live rebuild costs an acquisition sweep, and an invocation error
    discovered twenty minutes in is an invocation error discovered too late."""
    build("--published-at", "yesterday", expect=int(ExitCode.CONFIG_ERROR))
    assert not (fixture_copy / "build" / f"rules-{RULES_VERSION_ID}.json").exists()


# --- the workflow half: the rebuild the approval gate performs uses the recorded date -------


def test_the_publish_workflow_rebuilds_with_the_recorded_date() -> None:
    """`publish.yml` is the only caller that must never stamp `now`, and the only one that can.

    Asserted as text for the same reason `test_no_unattended_path.py` reads workflows as text:
    this repository carries no YAML dependency, and the string is unambiguous.
    """
    publish = (
        Path(__file__).resolve().parents[2] / ".github" / "workflows" / "publish.yml"
    ).read_text(encoding="utf-8")
    assert "--published-at-from-report" in publish

    candidate = (
        Path(__file__).resolve().parents[2] / ".github" / "workflows" / "candidate.yml"
    ).read_text(encoding="utf-8")
    assert "--published-at" not in candidate, (
        "a fresh candidate's published date IS its build day; only the rebuild is bound"
    )
