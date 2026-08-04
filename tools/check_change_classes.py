#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Change-class guard (task T014):
# enforces that a pull request touches at most one of the four mutually exclusive change
# classes {pipeline/+tests/, data/, curation/, infrastructure}, that a PR touching data/ was
# committed by the pipeline bot, and (in `worktree` mode) that a pipeline run's own working-tree
# diff never touches curation/ -- the data/<->curation/ write boundary (plan.md Separation
# gate, research D2/D3).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Switched the data/ writer check from the
# PR's opener login to the git author identity of the commits that touch data/ (CI run
# 30936394229 on PR #1, candidate/mfm-2026-08): this repository's org disallows "GitHub Actions
# is not permitted to create or approve pull requests" for the default `GITHUB_TOKEN`
# (confirmed in candidate.yml's `Open or update the candidate pull request` step failing with
# that exact message), so `candidate.yml` pushes the candidate branch under the commit identity
# it sets (`git config user.name "wargame-rules-data bot"`) but a maintainer must open the PR by
# hand until that org policy changes -- `github.event.pull_request.user.login` is then the
# maintainer, not the bot, even though every byte in data/ still came from the pipeline commit.
# The commit's author is the fact that actually answers "did the pipeline write this," and
# reading it from `git log` rather than PR metadata also matches how `worktree` mode below
# already inspects git state directly instead of trusting an external actor string.
"""Change-class guard for wargame-rules-data.

Two invocation modes:

  check_change_classes.py diff --base <ref> --head <ref> [--actor <login>]
      Used in CI on pull_request events. Fails if the file set changed between `base` and
      `head` spans more than one of the four change classes, or if the diff touches `data/` and
      any commit in `base..head` was not authored under the pipeline bot's git identity
      (`PIPELINE_BOT_COMMIT_NAME`/`PIPELINE_BOT_COMMIT_EMAIL`) -- regardless of which account
      opened the pull request itself. `--actor` is accepted for interface compatibility with
      `check_summary_approvals.py`'s identical flag but no longer decides this check's verdict;
      the commit author is the fact that matters.

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

# The git identity `candidate.yml` (and any future data-writing workflow) commits under -- see
# that workflow's `git config user.name`/`user.email` in its "Push the candidate branch" step.
# This is the provenance signal the guard actually trusts for data/, independent of which GitHub
# account ends up as the pull request's opener (see the module docstring).
PIPELINE_BOT_COMMIT_NAME = "wargame-rules-data bot"
PIPELINE_BOT_COMMIT_EMAIL = "noreply@users.noreply.github.com"


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


def commit_authors(base: str, head: str) -> list[tuple[str, str]]:
    """The ``(name, email)`` of every commit reachable from ``head`` but not from ``base``.

    Two-dot, not three-dot: this asks "what did this branch add," which is the PR's own
    commits, the same commits ``candidate.yml`` created. A three-dot (merge-base) diff would
    answer a different question and is what :func:`changed_files` uses instead, correctly, for
    the file set.
    """
    result = subprocess.run(
        ["git", "log", "--format=%an\t%ae", f"{base}..{head}"],
        capture_output=True,
        text=True,
        check=True,
    )
    authors = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        name, _, email = line.partition("\t")
        authors.append((name, email))
    return authors


def non_bot_data_authors(base: str, head: str) -> list[tuple[str, str]]:
    """Commit authors in ``base..head`` that are not the pipeline bot's git identity.

    Empty when every commit -- there is always at least one, or ``data/`` could not have
    changed -- was committed as the bot. That is the actual claim "data/ is machine-written
    only" needs verified; who clicked "Create pull request" is a different, weaker fact (see
    the module docstring).
    """
    bot_identity = (PIPELINE_BOT_COMMIT_NAME, PIPELINE_BOT_COMMIT_EMAIL)
    return [author for author in commit_authors(base, head) if author != bot_identity]


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

    if ChangeClass.DATA in classes:
        offending = non_bot_data_authors(args.base, args.head)
        if offending:
            bot = f"{PIPELINE_BOT_COMMIT_NAME} <{PIPELINE_BOT_COMMIT_EMAIL}>"
            print(
                f"FAIL: this PR touches data/ but was not committed entirely under the "
                f"pipeline bot's git identity ({bot!r}). data/ is machine-written only. "
                "Offending commit author(s):",
                file=sys.stderr,
            )
            for name, email in offending:
                print(f"  {name} <{email}>", file=sys.stderr)
            return 1

    class_label = classes[0].value if classes else "none"
    actor_note = f" (PR opened by {args.actor!r})" if args.actor else ""
    print(f"OK: change class = {class_label}{actor_note}")
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
