# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the repository-wide raw-source scan
# (task T053): no tracked file under work/, no .csv outside fixtures/, no committed HTML outside
# fixtures/. Runs in CI on every PR.
# AI-Assisted: Claude Code (model: claude-opus-5) - Extended the scan to the current-edition HTML
# acquisition path (004 task T083). The extension-based rules below already catch a committed
# `datasheets.html`, but they catch it as "an .html file", which says nothing about where it came
# from -- and a page saved under a different extension, or a directory named after the source
# tree, would sail past all three. The new test asserts on the PATH, which is the thing FR-004
# and FR-010 actually care about.
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


#: Path fragments that only appear if something from the publisher's tree was written down.
#: `wh40k11ed` / `wh40k10ed` are the edition tree segments `WGC_DETAIL_SOURCE_URL` points at;
#: `SiteMap.xml` and `datasheets.html` are the two documents the `html`-mode sweep retrieves.
ACQUISITION_PATH_MARKERS: tuple[str, ...] = (
    "wh40k11ed",
    "wh40k10ed",
    "sitemap.xml",
    "datasheets.html",
)


def test_no_artefact_of_the_html_acquisition_path_is_tracked() -> None:
    """FR-004's permitted path is a thing to *request*, never a thing to keep.

    The `html`-mode sweep retrieves `SiteMap.xml` and 26 `factions/<slug>/datasheets.html` pages
    into ephemeral `work/`, digests what it needs, and discards them. None of it may reach version
    control under any name, in any directory, at any extension -- which is a statement about the
    path, not about the file type, and so is not covered by the extension rules above.
    """
    offenders = [
        path
        for path in _tracked_files()
        if not path.startswith("fixtures/")
        and any(marker in path.lower() for marker in ACQUISITION_PATH_MARKERS)
    ]

    assert offenders == [], (
        "these tracked paths name the publisher's acquisition tree, which is retrieved into "
        f"work/ and discarded, never committed (FR-004, FR-010): {offenders}"
    )
