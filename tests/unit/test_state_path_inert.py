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
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Closed the guard's own exemption gap (009
# rung R05-fix4 item 2): "any `state_path=state_path` call is plumbing" ignored scope, so a
# locally-bound `state_path` -- exactly what `run_detect` (`pipeline/cli.py`) binds today,
# `state_path = root / DIGEST_STATE_RELATIVE_PATH`, not a parameter -- forwarded under the same
# name and passed silently. Rewrote the walk as an `ast.NodeVisitor` that tracks each function's
# own parameter set while descending, so the passthrough exemption only fires when the forwarded
# name is literally a parameter of the function doing the forwarding. Verified by reconstructing
# the exact wiring this feature reverted directly in `pipeline/cli.py`, confirming the old check
# missed it and the new one catches it, then reverting the reconstruction (not committed).
# Documented, rather than silently claimed away, two pre-existing blind spots the review also
# raised: `**kwargs` forwarding and callers outside `pipeline/` (e.g.
# `tools/table_coverage_report.py`) are both outside what an AST walk scoped to `pipeline/`'s own
# keyword arguments can see.
"""The short-circuit mechanism is proven correct in isolation (`test_wahapedia_export_digest.py`)
but wired into nothing. That is a property of the source code, checked here, not a fact anyone
has to take on faith from a comment.

**Known limits of this scan** (R05-fix4 item 2): it walks explicit keyword arguments only, so a
call that forwards `state_path` via `**kwargs` (a dict spread carrying the key) is invisible to
it; and it only parses modules under `pipeline/`, so a caller elsewhere in the repository --
`tools/table_coverage_report.py` is the one such script that imports from `pipeline` today -- is
never inspected at all. Neither gap is new to this fix; both existed under the previous,
laxer check too. They are named here rather than left implicit because `docs/follow-ups.md`
items 31-34 cite this test as proof that four dormant defects are unreachable, and that proof is
only as strong as what this scan actually looks at.
"""

from __future__ import annotations

import ast
from pathlib import Path

_PIPELINE_ROOT = Path(__file__).resolve().parents[2] / "pipeline"


def _enclosing_function_param_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Every name that ``node`` itself binds as a parameter -- positional, keyword-only,
    ``*args``, and ``**kwargs`` alike."""
    args = node.args
    names = {a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)}
    if args.vararg is not None:
        names.add(args.vararg.arg)
    if args.kwarg is not None:
        names.add(args.kwarg.arg)
    return names


class _StatePathCallVisitor(ast.NodeVisitor):
    """Walks a module tracking, at every point, which function (if any) encloses the node being
    visited -- because whether ``state_path=state_path`` is plumbing or a real wiring depends on
    whether ``state_path`` names a parameter of *that specific enclosing function*, not merely on
    the string on both sides of the ``=``.

    R05-fix4 item 2: the previous version of this scan checked only the shape
    ``state_path=state_path`` (a keyword bound to a bare ``Name`` reading ``state_path``),
    anywhere in the tree, with no notion of scope at all. That exempts a locally-bound
    ``state_path`` just as readily as a forwarded parameter -- and `run_detect` (`pipeline/cli.py`)
    binds exactly that: a *local* ``state_path = root / DIGEST_STATE_RELATIVE_PATH``, not a
    parameter. Re-adding the exact wiring this feature reverted --
    ``acquire_detail(config, state_path=state_path)`` inside `run_detect` -- reads as a
    passthrough under the old check and passes the guard silently. A passthrough is only ever the
    mechanism's own plumbing when the name being forwarded is the *enclosing function's own
    parameter*; a module-level or locally-bound ``state_path`` is a wiring, not plumbing, because
    the function had to go get a real value for it before handing it on.
    """

    def __init__(self) -> None:
        self.hits: list[int] = []
        self._param_stack: list[set[str]] = []

    def _current_params(self) -> set[str]:
        return self._param_stack[-1] if self._param_stack else set()

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._param_stack.append(_enclosing_function_param_names(node))
        self.generic_visit(node)
        self._param_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802 - ast.NodeVisitor API
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        self._visit_function(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802 - ast.NodeVisitor API
        params = self._current_params()
        for keyword in node.keywords:
            if keyword.arg != "state_path":
                continue
            value = keyword.value
            is_none = isinstance(value, ast.Constant) and value.value is None
            is_passthrough = (
                isinstance(value, ast.Name) and value.id == "state_path" and "state_path" in params
            )
            if not is_none and not is_passthrough:
                self.hits.append(node.lineno)
        self.generic_visit(node)


def _wired_state_path_calls(tree: ast.AST) -> list[int]:
    """Line numbers of every call in ``tree`` that passes ``state_path=`` something other than a
    bare ``None`` or a straight passthrough of the *enclosing function's own* ``state_path``
    parameter (``state_path=state_path`` where that function itself declares a ``state_path``
    parameter it is forwarding onward).

    The passthrough shape is not a caller opting in — it is the mechanism's own plumbing.
    ``acquire_detail`` (``pipeline/acquire/detail_source.py``) forwards its own ``state_path``
    parameter to whichever arm ran with exactly that shape, and every arm's own default is
    ``None``, so a passthrough alone can never smuggle a real path in. Anything else — a literal
    path expression, a variable with a different name, an attribute access, or a name that reads
    ``state_path`` but is bound locally (or at module scope) rather than received as this
    function's own parameter — is what a real caller opting in looks like, and nothing in
    ``pipeline/`` may look like that today.

    Known blind spots, documented rather than silently assumed away: this walk does not follow
    ``**kwargs`` forwarding (a call spreading a dict that happens to carry ``state_path`` reads as
    clean), and it only ever looks under ``pipeline/`` — a caller outside that tree entirely (for
    example `tools/table_coverage_report.py`) is invisible to it. Both are pre-existing limits of
    this scan, not new ones introduced by this fix; see this module's own docstring and
    :func:`test_no_caller_wires_state_path`.
    """
    visitor = _StatePathCallVisitor()
    visitor.visit(tree)
    return visitor.hits


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


def test_the_scan_catches_a_locally_bound_state_path_forwarded_under_the_same_name() -> None:
    """R05-fix4 item 2: the exemption used to hold for *any* ``state_path=state_path`` call, with
    no check that ``state_path`` was the enclosing function's own parameter. That let a locally
    bound ``state_path`` forward silently, which is exactly the shape `run_detect`
    (`pipeline/cli.py`) has: it binds ``state_path = root / DIGEST_STATE_RELATIVE_PATH`` as a
    local variable -- `run_detect` takes no ``state_path`` parameter at all -- so re-adding the
    exact wiring this feature reverted, ``acquire_detail(config, state_path=state_path)`` inside
    that function, reads as a same-name passthrough under the old check and passes the guard
    silently (reconstructed and verified against the real file for this fix's own receipt; not
    committed). A local binding is a wiring the function did work to produce, not plumbing it
    merely forwards, so this must be caught even though the names match exactly.
    """
    reconstructed_run_detect_wiring = ast.parse(
        "def run_detect(*, config, repository_root=None):\n"
        "    root = repository_root or repo_root()\n"
        "    state_path = root / DIGEST_STATE_RELATIVE_PATH\n"
        "    acquire_detail(config, state_path=state_path)\n"
    )
    module_level_state_path = ast.parse(
        "state_path = Path('state/wahapedia-export-digest.json')\n\n"
        "def run_something(config):\n"
        "    acquire_detail(config, state_path=state_path)\n"
    )

    assert _wired_state_path_calls(reconstructed_run_detect_wiring) == [4]
    assert _wired_state_path_calls(module_level_state_path) == [4]


def test_the_scan_still_accepts_the_one_legitimate_passthrough_in_pipeline() -> None:
    """After the fix, `acquire_detail`'s own forwarding call -- the one real
    ``state_path=state_path`` site under `pipeline/` -- must still read as plumbing, because
    `state_path` there genuinely is that function's own parameter being handed on unchanged."""
    genuine_passthrough = ast.parse(
        "def acquire_detail(config, *, state_path=None):\n"
        "    return acquire(config, state_path=state_path)\n"
    )
    assert _wired_state_path_calls(genuine_passthrough) == []
