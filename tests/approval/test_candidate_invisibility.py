# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the candidate-invisibility tests
# (task T112): a built candidate appears in no published manifest, is reachable only through
# the pre-release channel, and no non-publish code path writes site/manifest.json (FR-036,
# FR-047).
"""Tests for FR-036 and FR-047: a candidate is invisible until a human approves it.

`rules-pipeline build` is what `candidate.yml` runs, and `candidate.yml`'s token cannot reach
Releases or Pages at all (contract §3) — so this suite asserts the other half of that guarantee:
even with a full filesystem write and no permission boundary in the way, the build stage itself
never touches either channel's `manifest.json`. The only code path with write access to a
manifest is `pipeline.publish.release.publish`, called only from `pipeline.publish.gate`, called
only by the `publish` CLI command.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parents[2] / "pipeline"

#: The one function in the whole package that may write a channel manifest (`build/manifest.py`
#: defines it; `publish/release.py` is the only caller).
_MANIFEST_WRITER = "regenerate_manifest"


def test_a_build_leaves_both_channel_manifests_untouched(built_candidate) -> None:  # type: ignore[no-untyped-def]
    root, result = built_candidate()
    assert result.exit_code in {0, 20}, "the fixture set is expected to build cleanly or advisory"

    for relative in ("site/manifest.json", "site/prerelease/manifest.json"):
        document = json.loads((root / relative).read_text(encoding="utf-8"))
        assert document["versions"] == [], f"{relative} must list nothing until publish runs"


def test_the_candidate_bundle_and_reports_exist_only_under_the_repository_root(
    built_candidate,
) -> None:  # type: ignore[no-untyped-def]
    """The candidate is reachable through the working tree (what `candidate.yml`'s PR carries),
    never through either served channel."""
    root, result = built_candidate()
    assert result.bundle_path.is_file()
    assert result.report_path.is_dir()
    assert (
        not (root / "site" / "manifest.json")
        .read_text(encoding="utf-8")
        .count(result.checksum.sha256)
    )
    assert (
        not (root / "site" / "prerelease" / "manifest.json")
        .read_text(encoding="utf-8")
        .count(result.checksum.sha256)
    )


def _calls_manifest_writer(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            if name == _MANIFEST_WRITER:
                return True
    return False


def test_no_module_outside_publish_release_calls_the_manifest_writer() -> None:
    """A static sweep, not a runtime one: the invariant this asserts is "cannot", not "did not
    happen to today" (FR-036)."""
    callers = [
        path
        for path in sorted(PIPELINE_ROOT.rglob("*.py"))
        if path.name != "manifest.py" and _calls_manifest_writer(path)
    ]
    assert callers == [PIPELINE_ROOT / "publish" / "release.py"]


def test_a_candidate_is_only_consumable_through_the_prerelease_channel(
    built_candidate,
) -> None:  # type: ignore[no-untyped-def]
    """`candidate.yml` builds on the `prerelease` channel (contract §3); nothing in a build
    result carries a `published`-channel artifact reference at all."""
    _root, result = built_candidate()
    assert "published" not in str(result.bundle_path)
