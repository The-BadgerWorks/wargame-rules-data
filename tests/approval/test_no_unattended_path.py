# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the no-unattended-path tests (task
# T114): a static sweep over .github/workflows/*.yml asserting `publish.yml` is
# `workflow_dispatch` only, is the sole workflow that can reach Pages, and is bound to a GitHub
# Environment; plus a code-level check that a points-only candidate with a clean report still
# reaches no publish path without a recorded approval (FR-038, SC-012).
"""Tests for FR-038 and SC-012: there is no unattended publication path, of any kind.

The static half reads the workflow files as text rather than through a YAML parser — this
repository carries no YAML dependency (`pipeline/` has none, and adding one only for a test
would be exactly the kind of tool `research.md`'s Principle 14 discipline argues against for
something this small). "Collect lines until the next line starting in column 0" is exact for
every workflow file actually committed here, which the section-extraction tests below confirm
before relying on it.

The dynamic half proves the refusal does not become conditional on how clean the candidate is:
"a points-only run with a clean report" is exactly the case someone might plausibly special-case
past the gate, so it is asserted explicitly rather than only implied by the CI-context check.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from pipeline.config import load_config
from pipeline.publish.gate import OutsideApprovedContextError, run_publish

WORKFLOWS_DIR = Path(__file__).resolve().parents[2] / ".github" / "workflows"


def _workflow_files() -> list[Path]:
    files = sorted(WORKFLOWS_DIR.glob("*.yml"))
    assert files, f"no workflow files found under {WORKFLOWS_DIR}"
    return files


def _top_level_section(text: str, key: str) -> str:
    """The indented block under a top-level ``key:`` in a workflow file's raw text.

    Collects from the ``key:`` line up to (not including) the next line that starts in column 0
    and is not a comment — which is exactly a top-level YAML mapping key at this file's
    indentation, without needing a YAML parser to say so.
    """
    lines = text.splitlines()
    out: list[str] = []
    collecting = False
    for line in lines:
        if line.startswith(f"{key}:"):
            collecting = True
            out.append(line)
            continue
        if collecting:
            if line and not line[0].isspace() and not line.startswith("#"):
                break
            out.append(line)
    return "\n".join(out)


def test_the_section_extractor_finds_every_top_level_key_once() -> None:
    """Confirms the text-based extractor is safe to rely on before the real assertions do."""
    for path in _workflow_files():
        text = path.read_text(encoding="utf-8")
        assert _top_level_section(text, "on"), f"{path.name} has no top-level 'on:'"
        assert _top_level_section(text, "jobs"), f"{path.name} has no top-level 'jobs:'"


def test_publish_is_workflow_dispatch_only() -> None:
    """Never `schedule`, never `push`, never called by another workflow (FR-038, FR-052)."""
    text = (WORKFLOWS_DIR / "publish.yml").read_text(encoding="utf-8")
    on_section = _top_level_section(text, "on")
    assert "workflow_dispatch:" in on_section
    for forbidden in ("schedule:", "push:", "pull_request:", "workflow_call:"):
        assert forbidden not in on_section, f"publish.yml's 'on:' must never declare {forbidden}"


def test_only_publish_and_withdraw_can_reach_pages() -> None:
    """`pages: write` is the capability that matters — `contents: write` alone is legitimately
    shared with `candidate.yml`, which pushes the candidate branch but cannot deploy Pages or
    create a Release asset (contract §3's capability-not-policy design). `withdraw.yml` (task
    T142) is the one other workflow that legitimately needs it: it is deliberately not part of
    the `publish` job (contract §4), but it is the only other code path allowed to touch
    `site/`, and it is gated by the same kind of environment approval."""
    capable = [
        path.name
        for path in _workflow_files()
        if "pages: write" in _top_level_section(path.read_text(encoding="utf-8"), "permissions")
    ]
    assert capable == ["publish.yml", "withdraw.yml"]


def test_publish_is_bound_to_a_github_environment() -> None:
    text = (WORKFLOWS_DIR / "publish.yml").read_text(encoding="utf-8")
    jobs_section = _top_level_section(text, "jobs")
    assert re.search(r"^\s*environment:\s*\S", jobs_section, re.MULTILINE), (
        "publish.yml's job must declare 'environment:' -- that is what makes the reviewer "
        "requirement a GitHub-enforced gate rather than a convention"
    )


def test_only_publish_and_withdraw_declare_an_environment() -> None:
    """`withdraw.yml` (task T142) binds to an environment too, for the same reason `publish.yml`
    does: a named reviewer must approve before the job can start, whether it is about to create
    a Release or only flip one manifest entry's withdrawal fields."""
    bound = [
        path.name
        for path in _workflow_files()
        if re.search(
            r"^\s*environment:\s*\S",
            _top_level_section(path.read_text(encoding="utf-8"), "jobs"),
            re.MULTILINE,
        )
    ]
    assert bound == ["publish.yml", "withdraw.yml"]


def _rebuild_stub(*, findings: list[object]):  # type: ignore[no-untyped-def]
    from pipeline.publish.gate import RebuildOutcome

    def _rebuild() -> RebuildOutcome:
        return RebuildOutcome(
            payload=b'{"bundleFormatVersion":1}\n',
            findings=findings,  # type: ignore[arg-type]
            display_name="Invented Fixture",
            edition_codes=["wh40k-11e"],
            published_at="2026-06-13T00:00:00Z",
        )

    return _rebuild


@pytest.mark.parametrize(
    "env",
    [
        {},
        {"GITHUB_ACTIONS": "true"},
        {"GITHUB_ACTIONS": "true", "GITHUB_JOB": "publish"},
    ],
)
def test_a_clean_candidate_still_refuses_outside_the_gated_job_context(
    tmp_path: Path, env: dict[str, str]
) -> None:
    """No env short of the full triple the gated `publish` job itself sets is accepted -- and a
    *clean* rebuild (no findings at all) does not relax that one bit (FR-038, SC-012)."""
    for relative in ("site/prerelease", "state"):
        (tmp_path / relative).mkdir(parents=True, exist_ok=True)
    (tmp_path / "site" / "manifest.json").write_text(
        '{"manifestVersion":1,"generatedAt":"x","versions":[]}', encoding="utf-8"
    )
    (tmp_path / "site" / "prerelease" / "manifest.json").write_text(
        '{"manifestVersion":1,"generatedAt":"x","versions":[]}', encoding="utf-8"
    )

    with pytest.raises(OutsideApprovedContextError):
        run_publish(
            config=load_config(env={}),
            commit_sha="deadbeef",
            expect_sha256="0" * 64,
            rules_version_id="candidate-2026-01",
            rebuild=_rebuild_stub(findings=[]),
            api=None,  # type: ignore[arg-type]
            site_dir=tmp_path / "site",
            state_dir=tmp_path / "state",
            generated_at="2026-06-13T00:00:00Z",
            env=env,
        )
