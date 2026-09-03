# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 rung R05-fix2 item 5: added the
# structural scan asserting no caller anywhere in `pipeline/` wires `state_path` to a real value.
# The export-timestamp short-circuit (`pipeline.acquire.wahapedia.acquire_wahapedia`'s own
# `state_path` opt-in) lands dormant by Product Owner ruling -- the previous round wired
# `run_detect` to it and that ruling was reversed (`pipeline/cli.py`'s own header explains why).
# This test makes "no caller passes state_path" an asserted property of the source rather than a
# claim in a docstring or a commit message, on the same AST-walk discipline
# `tests/unit/test_detail_mode.py::test_no_mode_branch_or_reference_below_acquire` already uses
# for rule 4's "no mode branch below acquire" guarantee -- so the day a caller opts in
# deliberately, this test goes red and tells whoever wired it to come update it.
"""The short-circuit mechanism is proven correct in isolation (`test_wahapedia_export_digest.py`)
but wired into nothing. That is a property of the source code, checked here, not a fact anyone
has to take on faith from a comment.
"""

from __future__ import annotations

import ast
from pathlib import Path

_PIPELINE_ROOT = Path(__file__).resolve().parents[2] / "pipeline"


def _wired_state_path_calls(tree: ast.AST) -> list[int]:
    """Line numbers of every call in ``tree`` that passes ``state_path=`` something other than a
    bare ``None`` or a straight passthrough of the enclosing function's own ``state_path``
    parameter (``state_path=state_path``).

    The passthrough shape is not a caller opting in — it is the mechanism's own plumbing.
    ``acquire_detail`` (``pipeline/acquire/detail_source.py``) forwards its own ``state_path``
    parameter to whichever arm ran with exactly that shape, and every arm's own default is
    ``None``, so a passthrough alone can never smuggle a real path in. Anything else — a literal
    path expression, a variable with a different name, an attribute access — is what a real
    caller opting in looks like, and nothing in ``pipeline/`` may look like that today.
    """
    hits: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg != "state_path":
                continue
            value = keyword.value
            is_none = isinstance(value, ast.Constant) and value.value is None
            is_passthrough = isinstance(value, ast.Name) and value.id == "state_path"
            if not is_none and not is_passthrough:
                hits.append(node.lineno)
    return hits


def _state_path_call_sites() -> list[tuple[Path, int]]:
    """Every flagged call site under ``pipeline/``, across every module."""
    hits: list[tuple[Path, int]] = []
    for module_path in sorted(_PIPELINE_ROOT.rglob("*.py")):
        tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))
        hits.extend((module_path, lineno) for lineno in _wired_state_path_calls(tree))
    return hits


def test_no_caller_wires_state_path() -> None:
    """R05-fix2 item 5: inertness as an asserted property, not a claim.

    Passing today because `run_detect` was reverted to its pre-wiring shape (item 1) and
    `run_build` never passed a real `state_path` in the first place. The day a caller opts in
    deliberately -- R07's own job, per `docs/follow-ups.md` item 30 -- this test goes red at the
    exact call site and has to be updated alongside that change, the same tripwire shape this
    feature's strict `xfail` pins use for a deliberately-left-open residual elsewhere
    (`tests/ip/test_ip_strip.py`).
    """
    hits = _state_path_call_sites()
    assert not hits, (
        f"state_path is wired at: {hits} -- wiring a caller is its own rung, decided once the "
        "detail source is genuinely being consumed (docs/follow-ups.md item 30); update this "
        "test deliberately when that lands, rather than silencing it."
    )


def test_the_scan_actually_finds_a_wired_call_site_when_one_exists() -> None:
    """The scan's own receipt: it is not vacuously empty because it never matches anything.

    Parses a synthetic snippet carrying the exact shape a real wiring commit would add -- a
    keyword argument bound to something other than `None` or a `state_path` passthrough -- and
    confirms `_wired_state_path_calls` catches it. This is what makes
    `test_no_caller_wires_state_path` a receipt rather than a test that would pass identically if
    the scan itself were deleted.
    """
    wired = ast.parse(
        "def run_detect(state_path=None):\n"
        "    acquire_detail(config, state_path=export_state_path)\n"
    )
    unwired_default = ast.parse("acquire_detail(config, state_path=None)\n")
    unwired_passthrough = ast.parse(
        "def acquire_detail(state_path=None):\n    acquire(config, state_path=state_path)\n"
    )

    assert _wired_state_path_calls(wired) == [2]
    assert _wired_state_path_calls(unwired_default) == []
    assert _wired_state_path_calls(unwired_passthrough) == []
