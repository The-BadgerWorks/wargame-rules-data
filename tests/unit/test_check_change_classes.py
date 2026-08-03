# AI-Assisted: Claude Code (model: claude-sonnet-5) - Unit tests for the pure classification
# logic of tools/check_change_classes.py (task T014). tools/ is not an installed package, so
# the module is loaded directly from its file path.
import importlib.util
import sys
from pathlib import Path

_MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "check_change_classes.py"
_spec = importlib.util.spec_from_file_location("check_change_classes", _MODULE_PATH)
assert _spec is not None and _spec.loader is not None
check_change_classes = importlib.util.module_from_spec(_spec)
sys.modules["check_change_classes"] = check_change_classes
_spec.loader.exec_module(check_change_classes)

ChangeClass = check_change_classes.ChangeClass
classify = check_change_classes.classify
check_classes = check_change_classes.check_classes


def test_classify_each_class() -> None:
    assert classify("pipeline/acquire/http.py") is ChangeClass.PIPELINE
    assert classify("tests/unit/test_foo.py") is ChangeClass.PIPELINE
    assert classify("data/wh40k-11e/edition.json") is ChangeClass.DATA
    assert classify("curation/faction-map.json") is ChangeClass.CURATION
    assert classify("curation/abilities/f-necrons.json") is ChangeClass.CURATION
    assert classify(".github/workflows/ci.yml") is ChangeClass.INFRASTRUCTURE
    assert classify("site/manifest.json") is ChangeClass.INFRASTRUCTURE
    assert classify("docs/repo-settings.md") is ChangeClass.INFRASTRUCTURE


def test_classify_neutral_paths() -> None:
    assert classify("README.md") is None
    assert classify("pyproject.toml") is None
    assert classify("fixtures/sample/mfm/necrons.html") is None
    assert classify("docs/contracts.md") is None
    assert classify("state/run-ledger.jsonl") is None


def test_check_classes_single_class_ok() -> None:
    classes = check_classes(["pipeline/cli.py", "tests/unit/test_cli.py", "README.md"])
    assert classes == [ChangeClass.PIPELINE]


def test_check_classes_two_classes_fails() -> None:
    classes = check_classes(["pipeline/cli.py", "curation/faction-map.json"])
    assert len(classes) == 2
