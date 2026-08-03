# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the repository-wide raw-source scan
# (task T053): no tracked file under work/, no .csv outside fixtures/, no committed HTML outside
# fixtures/. Runs in CI on every PR.
"""The scan that keeps raw acquired source material out of version control (FR-010, SC-003).

This is deliberately a *git* scan rather than a filesystem scan. A curator's working tree will
have `work/` full of acquired pages mid-run and that is exactly what `work/` is for; what must
never happen is one of them being committed, because git history is effectively permanent and
FR-013 covers version control explicitly.

`fixtures/` is the only place a `.csv` or an `.html` may live, and `fixtures/README.md` states
why the files there are authored rather than captured.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip("not a git checkout")
    return [entry for entry in result.stdout.split("\0") if entry]


def test_nothing_under_work_is_tracked() -> None:
    """`work/` is ephemeral by construction and gitignored by the first line of .gitignore."""
    assert [p for p in _tracked_files() if p == "work" or p.startswith("work/")] == []


def test_no_csv_is_tracked_outside_fixtures() -> None:
    offenders = [
        p for p in _tracked_files() if p.endswith(".csv") and not p.startswith("fixtures/")
    ]
    assert offenders == []


def test_no_html_is_tracked_outside_fixtures() -> None:
    offenders = [
        p
        for p in _tracked_files()
        if p.endswith((".html", ".htm")) and not p.startswith("fixtures/")
    ]
    assert offenders == []


def test_the_fixture_files_that_do_exist_are_declared_synthetic() -> None:
    """Every fixture set carries the note that says where its content came from."""
    fixture_sets = {
        path.parts[1] for path in (Path(p) for p in _tracked_files()) if path.parts[0] == "fixtures"
    }
    fixture_sets.discard("README.md")
    fixture_sets.discard(".gitkeep")
    for name in sorted(fixture_sets):
        assert (REPO_ROOT / "fixtures" / name / "README.md").is_file(), (
            f"fixture set {name!r} has no README stating that it is synthetic"
        )


def test_gitignore_still_excludes_work_first() -> None:
    lines = [
        line.strip()
        for line in (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert lines[0] == "work/"
