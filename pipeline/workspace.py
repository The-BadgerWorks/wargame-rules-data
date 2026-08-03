# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the work/ lifecycle (task T018):
# created, emptied at the start of every command that writes to it, and emptied again in a
# finally so a crashed run leaves no raw source behind (FR-010).
"""The ephemeral ``work/`` directory.

``work/`` is where raw acquired source material lives, and it is the only place it ever lives.
It is gitignored (the first rule in ``.gitignore``), emptied when a command that writes to it
starts, and emptied again in a ``finally`` so an exception — including a crash mid-acquisition —
cannot leave publisher material on disk (FR-010).

Nothing outside this module may create ``work/``, so there is exactly one lifecycle to audit.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Final

from pipeline.config import repo_root

#: The directory name, fixed because ``.gitignore``, CI, and the IP scan all name it.
WORK_DIR_NAME: Final = "work"


def work_dir(root: Path | None = None) -> Path:
    """The absolute path of ``work/`` under ``root`` (the repository root by default)."""
    return (root if root is not None else repo_root()) / WORK_DIR_NAME


def empty(path: Path) -> None:
    """Remove every child of ``path``, leaving the directory itself in place.

    A missing directory is not an error: the postcondition is "nothing under ``work/``", and a
    directory that does not exist satisfies it.
    """
    if not path.exists():
        return
    for child in path.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def is_empty(path: Path) -> bool:
    """True when ``path`` holds no entries (or does not exist)."""
    return not path.exists() or next(path.iterdir(), None) is None


@contextmanager
def workspace(root: Path | None = None) -> Iterator[Path]:
    """Create and empty ``work/``, yield it, and empty it again whatever happens.

    Usage::

        with workspace() as work:
            (work / "faction.html").write_text(response.text, encoding="utf-8")

    On leaving the block — normally, by exception, or by ``KeyboardInterrupt`` — the directory
    is emptied. The directory itself is left behind so a later run finds a stable path.
    """
    path = work_dir(root)
    path.mkdir(parents=True, exist_ok=True)
    empty(path)
    try:
        yield path
    finally:
        empty(path)
