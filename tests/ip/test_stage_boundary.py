# AI-Assisted: Claude Code (model: claude-sonnet-5) - Static stage-boundary check (task T161.2):
# walks pipeline/reconcile/, pipeline/curate/, pipeline/validate/, pipeline/build/, and
# pipeline/publish/ and asserts, by parsing each file's AST rather than by regex, that none of
# them imports anything from pipeline.models.source -- research D8's IP-strip boundary, which
# pipeline/models/source.py's own docstring states as "ephemeral, never committed" and readable
# by exactly one stage, normalize.
"""No stage downstream of `normalize` may import a source-side model.

The pipeline's stage order is `acquire -> parse -> normalize -> reconcile -> curate -> validate
-> build -> publish` (`pipeline/models/source.py`'s own module docstring). Every record in that
module — `SourceAcquisition`, the `MfmUnitCostBlock`/`MfmDetachmentCard` family, `WahapediaRow`
— lives only in memory and in `work/` for the duration of one run and is deleted at the end of it
(FR-010); `WahapediaRow` additionally carries publisher prose in specific fields that only
`normalize`'s IP strip may read (FR-013). Importing the module at all downstream of `normalize`
is the thing to catch here, prose-bearing or not: an ephemeral, `work/`-scoped record reaching a
stage that persists to `data/` is the shape of the leak this boundary exists to prevent, whether
or not the particular class happens to carry a prose field today.

AST parsing (not a text/regex search) is deliberate, the same reasoning
`tools/check_change_classes.py` and the other `tests/ip/` checks already apply to their own
targets: an import wrapped across lines, aliased, or written as `from pipeline.models import
source` rather than `from pipeline.models.source import ...` must be caught exactly as reliably
as the common form.

**One documented, narrow exception.** `pipeline/curate/assemble.py` already imports
`SourceAcquisition`, `MfmUnitCostBlock`, and `MfmDetachmentCard` directly — none of which carry a
prose-bearing field (`pipeline.models.source.PROSE_BEARING_FIELDS` lists an empty set for all
three), but all three are still source-side records by this module's own definition, so this is
a real, pre-existing instance of exactly what this test otherwise forbids. `assemble.py` is
owned by a matcher-enhancement change landing in parallel with this task and is out of scope to
edit here; the exception below names the file and the exact three symbols so this test still
fails the moment anything else — most of all `WahapediaRow`, the one type that actually carries
prose — is imported anywhere in these five packages, including a fourth symbol added to this
same import. See this task's final report for the recommendation to resolve the exception itself
as follow-up work.
"""

from __future__ import annotations

import ast
from collections.abc import Mapping
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

#: The stages downstream of `normalize`, per the module docstring above.
DOWNSTREAM_PACKAGES: tuple[str, ...] = (
    "pipeline/reconcile",
    "pipeline/curate",
    "pipeline/validate",
    "pipeline/build",
    "pipeline/publish",
)

FORBIDDEN_MODULE = "pipeline.models.source"

#: `relative posix path -> exactly the symbol names that file may import from
#: pipeline.models.source`. Anything not listed here, or any symbol beyond what is listed for a
#: path that is, is a real violation. See the module docstring for why this one entry exists.
KNOWN_EXCEPTIONS: Mapping[str, frozenset[str]] = {
    "pipeline/curate/assemble.py": frozenset(
        {"SourceAcquisition", "MfmUnitCostBlock", "MfmDetachmentCard"}
    ),
}


def _python_files(package_relpath: str) -> list[Path]:
    package_dir = REPO_ROOT / package_relpath
    return sorted(package_dir.rglob("*.py"))


def _imported_source_symbols(tree: ast.Module) -> set[str]:
    """Every name this module imports from `pipeline.models.source`, however it was spelled."""
    symbols: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == FORBIDDEN_MODULE:
                symbols.update(alias.name for alias in node.names)
            elif node.module == "pipeline.models":
                # `from pipeline.models import source` -- the submodule itself, not a symbol
                # from it. Recorded as "*" so it always counts as a violation: there is no
                # legitimate reason to import the whole ephemeral module downstream of normalize.
                symbols.update("*" for alias in node.names if alias.name == "source")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == FORBIDDEN_MODULE or alias.name.startswith(f"{FORBIDDEN_MODULE}."):
                    symbols.add("*")
    return symbols


def _violations() -> list[str]:
    violations: list[str] = []
    for package in DOWNSTREAM_PACKAGES:
        for path in _python_files(package):
            relpath = path.relative_to(REPO_ROOT).as_posix()
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relpath)
            imported = _imported_source_symbols(tree)
            if not imported:
                continue
            allowed = KNOWN_EXCEPTIONS.get(relpath, frozenset())
            offending = sorted(imported - allowed)
            if offending:
                violations.append(f"{relpath} imports {offending} from {FORBIDDEN_MODULE}")
    return violations


def test_no_downstream_stage_imports_a_source_side_model() -> None:
    violations = _violations()
    assert violations == [], (
        "a stage downstream of normalize imports pipeline.models.source (research D8, FR-010, "
        "FR-013):\n" + "\n".join(f"  {v}" for v in violations)
    )


def test_the_downstream_packages_being_walked_actually_exist() -> None:
    # A typo in DOWNSTREAM_PACKAGES that silently walked zero files would make the test above
    # pass for the wrong reason -- this catches that.
    for package in DOWNSTREAM_PACKAGES:
        assert _python_files(package), f"{package} has no .py files; is the path right?"


def test_the_documented_exception_is_exact_not_a_blanket_allowance() -> None:
    # If assemble.py's import ever grows to include WahapediaRow -- the one type that actually
    # carries prose -- this must fail even though the file is already listed in
    # KNOWN_EXCEPTIONS: the allowance is per-symbol, not per-file.
    relpath = "pipeline/curate/assemble.py"
    path = REPO_ROOT / relpath
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=relpath)
    imported = _imported_source_symbols(tree)
    assert "WahapediaRow" not in imported, (
        "pipeline/curate/assemble.py now imports WahapediaRow, the prose-bearing source record "
        "-- KNOWN_EXCEPTIONS intentionally does not cover this and must not be widened to do so"
    )
    assert imported == KNOWN_EXCEPTIONS[relpath], (
        f"pipeline/curate/assemble.py's imports from {FORBIDDEN_MODULE} changed to {imported}; "
        "update KNOWN_EXCEPTIONS deliberately (and re-check whether the exception can be "
        "removed entirely) rather than letting this test silently pass a wider import"
    )
