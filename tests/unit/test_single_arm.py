# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R5 step 4: the structural guard that
# replaces `tests/unit/test_detail_mode.py`'s AST scan. That scan proved no stage below `acquire`
# branched on a mode; with one arm the stronger and simpler property is that the second arm's
# modules and the mode enum are referenced from nowhere under `pipeline/` at all, and that
# `acquire/detail_source.py` exposes exactly one acquirer and one reader.
"""One acquisition arm, checked against the source rather than asserted in a comment.

A deletion is only finished when nothing can quietly re-grow. Three names are what the second
arm was reached through -- the two modules and the enum that selected between them -- so a
module that names any of them is either a leftover or a reintroduction, and either way this
fails. The scan reads every module under ``pipeline/`` as text and as an AST: as text because a
docstring or comment naming a deleted module is a defect of its own (a reader is told to go look
at something that is not there), and as an AST because an import is what would actually make it
run again.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Final

import pytest

from pipeline.acquire import detail_source

_PIPELINE_ROOT: Final = Path(__file__).resolve().parents[2] / "pipeline"

#: The three names the deleted arm was reached through.
_DELETED_NAMES: Final = ("wahapedia_html", "wahapedia_html_dom", "DetailAcquisitionMode")


def _iter_modules() -> list[Path]:
    return sorted(
        path
        for path in _PIPELINE_ROOT.rglob("*.py")
        if "__pycache__" not in path.parts and path.name != "__init__.py"
    )


@pytest.mark.parametrize("module_path", _iter_modules(), ids=lambda p: str(p.name))
def test_no_module_names_the_deleted_arm(module_path: Path) -> None:
    """Text-level: not in code, not in a docstring, not in a comment.

    ``WGC_DETAIL_ACQUISITION_MODE`` is deliberately NOT scanned for -- ``detail_source.py``'s own
    module docstring records that the variable once existed and what the design rule around it
    was, which is history a reader benefits from. The three names here are different: each one
    points at something a reader could try to open or import, and none of them exists.
    """
    source = module_path.read_text(encoding="utf-8")
    named = [name for name in _DELETED_NAMES if name in source]
    assert named == [], (
        f"{module_path.relative_to(_PIPELINE_ROOT.parent)} names {named}, which 010 R5 deleted"
    )


@pytest.mark.parametrize("module_path", _iter_modules(), ids=lambda p: str(p.name))
def test_no_module_imports_the_deleted_arm(module_path: Path) -> None:
    """AST-level: the half that would make the deleted arm run again rather than merely read.

    Separate from the text scan on purpose. The text scan is the broader net and would catch
    every import too, but it would catch them for the wrong stated reason -- and if a later
    rung ever relaxes the text scan for one prose mention, this one must not relax with it.
    """
    tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
            imported.extend(alias.name for alias in node.names)

    offending = [
        name
        for name in imported
        for deleted in _DELETED_NAMES
        if name == deleted or name.endswith(f".{deleted}")
    ]
    assert offending == [], f"{module_path.relative_to(_PIPELINE_ROOT.parent)} imports {offending}"


def test_the_scan_covers_a_nonempty_module_set() -> None:
    """A scan over nothing passes over nothing. 010 R5's own deletions removed two modules from
    this set, so a path mistake here would look exactly like success."""
    modules = _iter_modules()
    assert len(modules) > 50, f"only {len(modules)} modules scanned -- the path is wrong"
    assert (_PIPELINE_ROOT / "acquire" / "detail_source.py") in modules


def test_detail_source_exposes_exactly_one_acquirer_and_one_reader() -> None:
    """The positive half: not merely "the second arm is gone" but "there is one of each".

    A dispatch table, a protocol pair, or a second public acquirer reappearing in this module is
    what a re-grown second arm looks like from the outside, whatever it is called.
    """
    public = {name for name in vars(detail_source) if not name.startswith("_")}

    assert "acquire_detail" in public
    assert "read_detail" in public
    for gone in ("ACQUIRERS", "READERS", "acquirer_for", "reader_for", "DetailAcquirer"):
        assert gone not in public, f"{gone} is back in pipeline/acquire/detail_source.py"

    # `acquire_detail` calls the one acquirer, and `read_detail` the one reader, by name --
    # no table lookup in between. Read off the source so a re-introduced indirection fails here
    # rather than only in whatever test happens to exercise a build.
    source = (_PIPELINE_ROOT / "acquire" / "detail_source.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    called = {
        node.name: sorted(
            {
                inner.func.id
                for inner in ast.walk(node)
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
            }
        )
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name in {"acquire_detail", "read_detail"}
    }
    assert called["acquire_detail"] == ["acquire_wahapedia"]
    assert called["read_detail"] == ["read_export_payloads"]
