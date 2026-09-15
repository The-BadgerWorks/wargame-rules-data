# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R9 task 1: the structural guard that
# replaces `test_state_path_inert.py`. That test asserted the export-timestamp short-circuit was
# wired to nothing; this one asserts the mechanism does not exist at all. Scoped deliberately to
# the export-digest mechanism's own named symbols rather than to any identifier spelled
# `state_path`: `pipeline/cli.py`'s `run_detect` binds a local `state_path` for
# `state/detection-digest.json`, an unrelated and entirely live mechanism, so the parameter scan
# below is confined to `pipeline/acquire/` and to *parameters*, never to local bindings.
"""The export-timestamp short-circuit is deleted, and that is a property of the source.

The mechanism (`acquire_wahapedia`'s `state_path` opt-in, its `ExportDigestState` persistence,
and the `SRC-EXPORT-UNCHANGED` outcome it reported) had no caller from the day it landed and
could not acquire one: a build cannot consume a skipped fetch when the corpus is never retained.
It was deleted rather than left dormant, and this file is what makes "deleted" checkable instead
of a claim in a commit message.

**What is asserted.** No module under `pipeline/` binds, defines, references or imports any of
the mechanism's own names, and no string literal under `pipeline/` is `SRC-EXPORT-UNCHANGED`. No
function under `pipeline/acquire/` takes a parameter named `state_path`.

**What is deliberately NOT asserted.** Nothing about the identifier `state_path` outside
`pipeline/acquire/`, and nothing about local variables anywhere. `run_detect`'s
`state_path = root / DIGEST_STATE_RELATIVE_PATH` is the detection-digest sweep's own local, in
service and unrelated to any of this; a scan that flagged it would be a false positive, so the
false-positive direction is asserted below alongside the true-positive one.

**Known limits.** An AST walk sees code, not comments: a `#` comment naming a deleted symbol is
invisible here, as is any caller outside `pipeline/` (every script under `tools/` included).
"""

from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PIPELINE_ROOT = _REPO_ROOT / "pipeline"
_ACQUIRE_ROOT = _PIPELINE_ROOT / "acquire"

#: The export-digest mechanism's own names. Every one of these existed only to serve the
#: short-circuit, so any surviving occurrence is a piece of the mechanism that outlived the
#: deletion. Named exhaustively rather than matched by prefix, so an unrelated future symbol
#: cannot be caught by accident and a genuine survivor cannot slip through a pattern.
_FORBIDDEN_SYMBOLS = frozenset(
    {
        "ExportDigestState",
        "EXPORT_DIGEST_STATE_RELATIVE_PATH",
        "load_export_digest_state",
        "save_export_digest_state",
        "export_digest_state_for",
        "_one_way_export_digest",
        "ExportStateCorrupt",
    }
)

#: The finding code the short-circuit emitted. Compared for equality against whole string
#: constants: a code is always written as its own literal at the sites that matter (the
#: catalogue row, `build_finding`'s argument, a test's expectation), never spliced into prose.
_FORBIDDEN_LITERAL = "SRC-EXPORT-UNCHANGED"

#: The opt-in switch's parameter name. Scoped to `pipeline/acquire/` and to parameters because
#: that is the whole of what the mechanism owned -- see this module's docstring.
_FORBIDDEN_PARAMETER = "state_path"


def _python_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if path.is_file())


def _label(path: Path) -> str:
    return path.relative_to(_REPO_ROOT).as_posix()


def _symbol_occurrences(tree: ast.AST, label: str) -> list[str]:
    """Every occurrence of a forbidden symbol name or the forbidden literal in ``tree``.

    Covers every syntactic position a surviving fragment of the mechanism could occupy: a class
    or function definition, a reference by bare name, an attribute access (``module.symbol``),
    an ``import``/``from ... import`` alias, a keyword-argument name at a call site, and a
    parameter name. Returned as ``path:line:name`` strings so a failure names the survivor and
    where it is rather than only that one exists.
    """
    found: list[str] = []

    def record(name: str | None, node: ast.AST) -> None:
        if name in _FORBIDDEN_SYMBOLS:
            found.append(f"{label}:{getattr(node, 'lineno', 0)}:{name}")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            record(node.name, node)
        elif isinstance(node, ast.Name):
            record(node.id, node)
        elif isinstance(node, ast.Attribute):
            record(node.attr, node)
        elif isinstance(node, ast.alias):
            record(node.name.rsplit(".", 1)[-1], node)
            record(node.asname, node)
        elif isinstance(node, ast.keyword | ast.arg):
            record(node.arg, node)
        elif isinstance(node, ast.Constant) and node.value == _FORBIDDEN_LITERAL:
            found.append(f"{label}:{node.lineno}:{_FORBIDDEN_LITERAL}")
    return found


def _state_path_parameters(tree: ast.AST, label: str) -> list[str]:
    """Every function in ``tree`` that declares a parameter named ``state_path``.

    Parameters only. A local variable of that name is not the short-circuit's switch and is not
    this scan's business -- see this module's docstring.
    """
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        args = node.args
        declared = {a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)}
        if args.vararg is not None:
            declared.add(args.vararg.arg)
        if args.kwarg is not None:
            declared.add(args.kwarg.arg)
        if _FORBIDDEN_PARAMETER in declared:
            found.append(f"{label}:{node.lineno}:{node.name}")
    return found


def test_no_module_under_pipeline_carries_an_export_digest_symbol() -> None:
    """The mechanism's own names and its finding code are gone from `pipeline/` entirely."""
    survivors: list[str] = []
    for path in _python_files(_PIPELINE_ROOT):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        survivors.extend(_symbol_occurrences(tree, _label(path)))

    assert survivors == [], (
        "the export-timestamp short-circuit was deleted in 010 R9, but these occurrences of its "
        f"own symbols survive under pipeline/: {survivors}"
    )


def test_no_function_under_acquire_takes_a_state_path_parameter() -> None:
    """The opt-in switch itself: `acquire_wahapedia`'s parameter and `acquire_detail`'s
    passthrough were the only two, and both go with the mechanism."""
    survivors: list[str] = []
    for path in _python_files(_ACQUIRE_ROOT):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        survivors.extend(_state_path_parameters(tree, _label(path)))

    assert survivors == [], (
        "the short-circuit's opt-in switch was deleted in 010 R9, but these functions under "
        f"pipeline/acquire/ still declare a `state_path` parameter: {survivors}"
    )


def test_the_symbol_scan_catches_a_planted_symbol(tmp_path: Path) -> None:
    """Anti-vacuity: a scan that never fires proves nothing. Plant each shape the real scan is
    meant to see -- a definition, a bare reference, an attribute access, an import alias, a
    keyword argument and a parameter -- in a module of its own and require every one to be
    reported.
    """
    planted = tmp_path / "planted.py"
    planted.write_text(
        "from pipeline.acquire.wahapedia import load_export_digest_state\n"
        "\n"
        "class ExportDigestState:\n"
        "    pass\n"
        "\n"
        "def _one_way_export_digest(text):\n"
        "    return text\n"
        "\n"
        "def use(module, state_path=None):\n"
        "    module.save_export_digest_state(state_path)\n"
        "    helper(ExportStateCorrupt=1)\n"
        "    return export_digest_state_for, EXPORT_DIGEST_STATE_RELATIVE_PATH\n",
        encoding="utf-8",
    )
    tree = ast.parse(planted.read_text(encoding="utf-8"))
    occurrences = _symbol_occurrences(tree, "planted")
    reported = {occurrence.rsplit(":", 1)[-1] for occurrence in occurrences}

    assert reported == set(_FORBIDDEN_SYMBOLS), (
        f"the symbol scan missed {sorted(set(_FORBIDDEN_SYMBOLS) - reported)}"
    )


def test_the_symbol_scan_catches_a_planted_finding_code_literal() -> None:
    """The finding code is a string constant, not a name, so it needs its own planted case."""
    tree = ast.parse('row = build_finding("SRC-EXPORT-UNCHANGED", detail={})\n')
    assert _symbol_occurrences(tree, "planted") == ["planted:1:SRC-EXPORT-UNCHANGED"]


def test_the_parameter_scan_catches_a_planted_state_path_parameter() -> None:
    """Anti-vacuity for the second scan: the opt-in switch's exact shape, reconstructed."""
    tree = ast.parse(
        "def acquire_wahapedia(config, *, workspace=None, state_path=None):\n    return None\n"
    )
    assert _state_path_parameters(tree, "planted") == ["planted:1:acquire_wahapedia"]


def test_the_parameter_scan_ignores_a_local_variable_named_state_path() -> None:
    """The other direction, and the reason this scan is parameter-scoped: `run_detect` binds a
    local `state_path` for `state/detection-digest.json`, a live and unrelated mechanism. A scan
    that flagged that would be a false positive, and silencing it later would cost the real
    assertion above.
    """
    tree = ast.parse(
        "def run_detect(*, config, repository_root=None):\n"
        "    root = repository_root or repo_root()\n"
        "    state_path = root / DIGEST_STATE_RELATIVE_PATH\n"
        "    return load_detection_state(state_path)\n"
    )
    assert _state_path_parameters(tree, "planted") == []
