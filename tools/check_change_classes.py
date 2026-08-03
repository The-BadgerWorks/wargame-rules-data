#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Change-class guard (task T014):
# enforces that a pull request touches at most one of the four mutually exclusive change
# classes {pipeline/+tests/, data/, curation/, infrastructure}, that a PR touching data/ is
# authored by the pipeline bot, and (in `worktree` mode) that a pipeline run's own working-tree
# diff never touches curation/ -- the data/<->curation/ write boundary (plan.md Separation
# gate, research D2/D3).
"""Change-class guard for wargame-rules-data.

Two invocation modes:

  check_change_classes.py diff --base <ref> --head <ref> [--actor <login>]
      Used in CI on pull_request events. Fails if the file set changed between `base` and
      `head` spans more than one of the four change classes, or if the diff touches `data/`
      and `--actor` is not the pipeline bot.

  check_change_classes.py worktree
      Used after a pipeline invocation (e.g. in candidate.yml, once it exists) to assert the
      run's own uncommitted working-tree diff never touches `curation/` -- the pipeline must
      never write curation/, only data/.

Paths outside the four classes (root project files, fixtures/, schemas/, tools/, docs/ other
than docs/repo-settings.md, state/, reports/) are neutral: they never count as a second class
on their own.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from enum import StrEnum

PIPELINE_BOT_LOGIN = "github-actions[bot]"


class ChangeClass(StrEnum):
    PIPELINE = "pipeline+tests"
    DATA = "data"
    CURATION = "curation"
    INFRASTRUCTURE = "infrastructure"


def classify(path: str) -> ChangeClass | None:
    """Return the change class a path belongs to, or None if it is neutral."""
    if path.startswith("pipeline/") or path.startswith("tests/"):
        return ChangeClass.PIPELINE
    if path.startswith("data/"):
        return ChangeClass.DATA
    if path.startswith("curation/"):
        return ChangeClass.CURATION
    if path.startswith(".github/") or path.startswith("site/") or path == "docs/repo-settings.md":
        return ChangeClass.INFRASTRUCTURE
    return None


def changed_files(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def worktree_changed_files() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    files = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        # porcelain format: "XY path" (rename entries carry "orig -> new"; take the new path)
        path = line[3:].split(" -> ")[-1].strip()
        files.append(path)
    return files


def check_classes(paths: list[str]) -> list[ChangeClass]:
    classes = {c for c in (classify(p) for p in paths) if c is not None}
    return sorted(classes, key=lambda c: c.value)


def cmd_diff(args: argparse.Namespace) -> int:
    paths = changed_files(args.base, args.head)
    classes = check_classes(paths)
    if len(classes) > 1:
        print(
            "FAIL: this PR touches more than one change class: "
            + ", ".join(c.value for c in classes),
            file=sys.stderr,
        )
        for path in paths:
            c = classify(path)
            if c is not None:
                print(f"  [{c.value}] {path}", file=sys.stderr)
        return 1

    if ChangeClass.DATA in classes and args.actor != PIPELINE_BOT_LOGIN:
        print(
            f"FAIL: this PR touches data/ but its actor ({args.actor!r}) is not the "
            f"pipeline bot ({PIPELINE_BOT_LOGIN!r}). data/ is machine-written only.",
            file=sys.stderr,
        )
        return 1

    print(f"OK: change class = {classes[0].value if classes else 'none'}")
    return 0


def cmd_worktree(_args: argparse.Namespace) -> int:
    paths = worktree_changed_files()
    touched_curation = [p for p in paths if classify(p) is ChangeClass.CURATION]
    if touched_curation:
        print(
            "FAIL: this run's working-tree diff touches curation/, which the pipeline must "
            "never write:",
            file=sys.stderr,
        )
        for path in touched_curation:
            print(f"  {path}", file=sys.stderr)
        return 1
    print("OK: working-tree diff does not touch curation/")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)

    diff_parser = sub.add_parser("diff", help="check a PR's changed-file set")
    diff_parser.add_argument("--base", required=True)
    diff_parser.add_argument("--head", required=True)
    diff_parser.add_argument("--actor", default="")
    diff_parser.set_defaults(func=cmd_diff)

    worktree_parser = sub.add_parser("worktree", help="check the current working-tree diff")
    worktree_parser.set_defaults(func=cmd_worktree)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
