#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wired the candidate reviewer view into
# `candidate.yml` (task T119): a thin script that reads report.json off disk and prints the
# approver's PR body, since the build and the PR-body assembly are separate steps of one
# workflow job rather than one Python process (FR-037).
"""Print the candidate PR body for one already-built report.

::

    python -m tools.render_pr_body reports/<rulesVersionId>/report.json

Used by `.github/workflows/candidate.yml` after `rules-pipeline build`: the report is already on
disk, so this only has to read it back and order it (`pipeline.report.pr_body`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pipeline.report.pr_body import render_pr_body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report_json", type=Path, help="path to reports/<id>/report.json")
    parser.add_argument(
        "--reports-relative-dir",
        default=None,
        help="the sub-report directory relative to the PR diff root (default: reports/<id>)",
    )
    args = parser.parse_args(argv)

    report_json = json.loads(args.report_json.read_text(encoding="utf-8"))
    sys.stdout.write(render_pr_body(report_json, reports_relative_dir=args.reports_relative_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
