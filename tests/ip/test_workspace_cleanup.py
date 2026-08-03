# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts work/ is empty after a forced
# exception (task T018), which is the case FR-010 actually depends on: a crashed run must not
# leave raw source on disk.
"""``work/`` holds raw acquired source and nothing else may.

The happy path is easy. The case that matters is the crash: if an exception mid-acquisition
left the directory populated, a later step — or a careless ``git add -A`` — could commit
publisher material. So the cleanup lives in a ``finally``, and this is the test that proves it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.workspace import WORK_DIR_NAME, empty, is_empty, work_dir, workspace


class Boom(RuntimeError):
    """A forced failure standing in for a crashed acquisition."""


def test_workspace_creates_the_directory(tmp_path: Path) -> None:
    with workspace(tmp_path) as work:
        assert work == tmp_path / WORK_DIR_NAME
        assert work.is_dir()


def test_workspace_is_emptied_on_entry(tmp_path: Path) -> None:
    stale = work_dir(tmp_path)
    stale.mkdir(parents=True)
    (stale / "left-over.html").write_text("stale", encoding="utf-8")

    with workspace(tmp_path) as work:
        assert is_empty(work), "a previous run's material survived into this one"


def test_workspace_is_emptied_after_a_forced_exception(tmp_path: Path) -> None:
    with pytest.raises(Boom), workspace(tmp_path) as work:
        (work / "faction.html").write_text("acquired", encoding="utf-8")
        (work / "nested").mkdir()
        (work / "nested" / "export.csv").write_text("a|b", encoding="utf-8")
        raise Boom("acquisition failed midway")

    assert is_empty(work_dir(tmp_path)), "a crashed run left raw source in work/ (FR-010)"


def test_workspace_is_emptied_on_a_clean_exit(tmp_path: Path) -> None:
    with workspace(tmp_path) as work:
        (work / "page.html").write_text("acquired", encoding="utf-8")
    assert is_empty(work_dir(tmp_path))


def test_empty_removes_nested_trees_and_tolerates_a_missing_directory(tmp_path: Path) -> None:
    target = tmp_path / "work"
    (target / "a" / "b").mkdir(parents=True)
    (target / "a" / "b" / "c.csv").write_text("x", encoding="utf-8")
    empty(target)
    assert is_empty(target)
    assert target.is_dir(), "the directory itself is kept so a later run finds a stable path"

    empty(tmp_path / "never-existed")  # must not raise
    assert is_empty(tmp_path / "never-existed")
