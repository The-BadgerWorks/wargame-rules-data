#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Self-approval guard for ability summaries
# (task T131): a PR that introduces `review_state: "approved"` on a record whose `reviewed_by`
# is the PR's own actor fails CI, complementing the CODEOWNERS routing on `curation/abilities/`
# (research D6). CODEOWNERS alone is not sufficient at this repository's current single-
# maintainer roster (see `.github/CODEOWNERS`'s own note) — this check is data-level and does
# not depend on a second reviewer existing.
"""Self-approval guard for `curation/abilities/*.json`.

  check_summary_approvals.py diff --base <ref> --head <ref> --actor <login>
      Used in CI on pull_request events. For every `curation/abilities/*.json` file the PR
      touches, compares the base and head content record by record. A record that is
      `approved` at head but was not `approved` at base (a new record, or one whose state just
      changed) is "newly approved" by this PR. If any newly approved record's `reviewed_by`
      equals `--actor`, the PR is a self-approval and this check fails.

The comparison is by `ability_key`, not by file position, so reordering or an unrelated edit
elsewhere in the same file never produces a false positive.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Sequence
from typing import Any

ABILITIES_GLOB_PREFIX = "curation/abilities/"


def changed_ability_files(base: str, head: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [
        line
        for line in result.stdout.splitlines()
        if line.strip().startswith(ABILITIES_GLOB_PREFIX) and line.strip().endswith(".json")
    ]


def read_records_at(ref: str, path: str) -> list[dict[str, Any]]:
    """The JSON array a `curation/abilities/*.json` file held at `ref`, or `[]` if it did not
    exist there yet (a brand-new file — every record in it is, by definition, newly approved
    wherever it says so)."""
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    text = result.stdout.strip()
    if not text:
        return []
    parsed = json.loads(text)
    if not isinstance(parsed, list):
        raise ValueError(f"{ref}:{path} is not a JSON array of ability-summary records")
    return parsed


def newly_approved(
    base_records: Sequence[dict[str, Any]], head_records: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Records `approved` at head that were not `approved` at base — new or just transitioned.

    A record that was already `approved` at base and remains `approved` at head (carried
    forward untouched, FR-024) is deliberately excluded: this PR did not introduce that
    approval, so it is not this PR's self-approval to fail on.
    """
    base_by_key = {record.get("ability_key"): record for record in base_records}
    result = []
    for record in head_records:
        if record.get("review_state") != "approved":
            continue
        prior = base_by_key.get(record.get("ability_key"))
        if prior is None or prior.get("review_state") != "approved":
            result.append(record)
    return result


def self_approved_keys(records: Sequence[dict[str, Any]], *, actor: str) -> list[str]:
    """`ability_key`s among `records` whose `reviewed_by` is `actor` — a self-approval."""
    return sorted(
        str(record.get("ability_key"))
        for record in records
        if actor and record.get("reviewed_by") == actor
    )


def cmd_diff(args: argparse.Namespace) -> int:
    offending: list[str] = []
    for path in changed_ability_files(args.base, args.head):
        base_records = read_records_at(args.base, path)
        head_records = read_records_at(args.head, path)
        for key in self_approved_keys(newly_approved(base_records, head_records), actor=args.actor):
            offending.append(f"{path}: {key}")

    if offending:
        print(
            f'FAIL: this PR introduces review_state: "approved" on a record authored by its '
            f"own actor ({args.actor!r}). Only a pull request approved by someone other than "
            "the record's author may introduce an approved summary (research D6):",
            file=sys.stderr,
        )
        for entry in offending:
            print(f"  {entry}", file=sys.stderr)
        return 1

    print("OK: no newly approved ability summary is self-authored")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)

    diff_parser = sub.add_parser("diff", help="check a PR's newly approved ability summaries")
    diff_parser.add_argument("--base", required=True)
    diff_parser.add_argument("--head", required=True)
    diff_parser.add_argument("--actor", default="")
    diff_parser.set_defaults(func=cmd_diff)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
