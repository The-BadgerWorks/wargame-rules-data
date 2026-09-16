# AI-Assisted: Claude Code (model: Claude Fable 5.1) - 010 R10: publish.yml run 35047728703
# created the Release and deployed Pages, then its bookkeeping step aborted because the
# rebuild had regenerated data/ in the workspace and `git checkout --detach origin/main`
# refused to overwrite those files. The step must discard everything it does not commit
# before it moves to main. Synthetic assertions over the workflow text only.
"""The publish bookkeeping step discards the rebuild's working-tree changes before it moves.

The step commits only ``site`` and ``state``. Everything else the rebuild wrote (``data/``
carries fresh acquisition ids on every live run) is throwaway, and a dirty working tree makes
``git checkout --detach origin/main`` abort — after the Release and the Pages deploy have
already happened. The ledger and manifest then never reach ``main``.
"""

from __future__ import annotations

import re
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "publish.yml"
STEP_NAME = "Commit the manifest and the checksum ledger"


def _bookkeeping_script() -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    start = text.index(f"- name: {STEP_NAME}")
    rest = text[start + len(STEP_NAME) :]
    end = re.search(r"\n\s*- name:", rest)
    return rest if end is None else rest[: end.start()]


def test_the_step_discards_the_rebuilds_working_tree_before_moving_to_main() -> None:
    script = _bookkeeping_script()
    commit = script.index("git commit -m")
    discard = script.find("git checkout -- .")
    move = script.index("git checkout --detach origin/main")
    assert discard != -1, (
        "the bookkeeping step never discards the rebuild's regenerated files, so a live "
        "rebuild that touches data/ makes the move to main abort after the Release exists"
    )
    assert commit < discard < move, (
        "the discard must come after the bookkeeping commit (so site/ and state/ are already "
        "committed) and before the move to main (so the move cannot abort)"
    )


def test_the_step_still_commits_only_site_and_state() -> None:
    script = _bookkeeping_script()
    assert "git add site state" in script
    assert "git add ." not in script and "git add -A" not in script
