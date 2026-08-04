# AI-Assisted: Claude Code (model: claude-sonnet-5) - Unit tests for the pure classification
# logic of tools/check_change_classes.py (task T014). tools/ is not an installed package, so
# the module is loaded directly from its file path.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added commit-authorship coverage (CI run
# 30936394229 on PR #1, candidate/mfm-2026-08): the data/ writer check moved from the PR
# opener's GitHub login to the git author identity of the commits that touch data/, because this
# repository's org disallows the default GITHUB_TOKEN from opening pull requests, so
# candidate.yml's own commits are bot-authored even on a PR a maintainer had to open by hand.
# These tests build a real throwaway git repository per case -- the thing under test is `git
# log` output, which a fake diff cannot stand in for.
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "check_change_classes.py"
_spec = importlib.util.spec_from_file_location("check_change_classes", _MODULE_PATH)
assert _spec is not None and _spec.loader is not None
check_change_classes = importlib.util.module_from_spec(_spec)
sys.modules["check_change_classes"] = check_change_classes
_spec.loader.exec_module(check_change_classes)

ChangeClass = check_change_classes.ChangeClass
classify = check_change_classes.classify
check_classes = check_change_classes.check_classes
commit_authors = check_change_classes.commit_authors
non_bot_data_authors = check_change_classes.non_bot_data_authors
cmd_diff = check_change_classes.cmd_diff
BOT_NAME = check_change_classes.PIPELINE_BOT_COMMIT_NAME
BOT_EMAIL = check_change_classes.PIPELINE_BOT_COMMIT_EMAIL


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


def test_classify_reports_is_neutral() -> None:
    """`reports/` is deliberately not its own change class (module docstring): a candidate PR

    always carries `data/` and `reports/<rulesVersionId>/` together (`candidate.yml`'s
    `git add data reports`), and neither the class-count check nor the data/-writer check
    should treat that pairing as two classes.
    """
    assert classify("reports/mfm-2026-08/report.json") is None


def test_check_classes_single_class_ok() -> None:
    classes = check_classes(["pipeline/cli.py", "tests/unit/test_cli.py", "README.md"])
    assert classes == [ChangeClass.PIPELINE]


def test_check_classes_two_classes_fails() -> None:
    classes = check_classes(["pipeline/cli.py", "curation/faction-map.json"])
    assert len(classes) == 2


def test_a_candidate_shaped_change_set_is_one_class() -> None:
    """`data/` + `reports/` together -- the exact shape `candidate.yml` commits -- is one class."""
    classes = check_classes(["data/wh40k-11e/edition.json", "reports/mfm-2026-08/report.json"])
    assert classes == [ChangeClass.DATA]


# --- commit-authorship: the actual fact the data/ writer check now trusts -----------------------


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)
    return result.stdout


def _init_repo(tmp_path: Path) -> tuple[Path, str]:
    """A throwaway repo with one commit on ``main``; returns the repo path and that commit's sha."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.name", "seed")
    _git(repo, "config", "user.email", "seed@example.com")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-q", "-m", "seed")
    base = _git(repo, "rev-parse", "HEAD").strip()
    return repo, base


def _commit_as(repo: Path, *, name: str, email: str, message: str, files: dict[str, str]) -> str:
    for relative, content in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        _git(repo, "add", relative)
    _git(
        repo,
        "-c",
        f"user.name={name}",
        "-c",
        f"user.email={email}",
        "commit",
        "-q",
        "-m",
        message,
    )
    return _git(repo, "rev-parse", "HEAD").strip()


def test_commit_authors_reads_name_and_email(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, base = _init_repo(tmp_path)
    head = _commit_as(
        repo,
        name="a curator",
        email="curator@example.com",
        message="hand-authored change",
        files={"curation/faction-map.json": "{}\n"},
    )
    monkeypatch.chdir(repo)

    assert commit_authors(base, head) == [("a curator", "curator@example.com")]


def test_non_bot_data_authors_empty_when_the_bot_committed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, base = _init_repo(tmp_path)
    head = _commit_as(
        repo,
        name=BOT_NAME,
        email=BOT_EMAIL,
        message="Candidate mfm-2026-08",
        files={
            "data/wh40k-11e/edition.json": "{}\n",
            "reports/mfm-2026-08/report.json": "{}\n",
        },
    )
    monkeypatch.chdir(repo)

    assert non_bot_data_authors(base, head) == []


def test_non_bot_data_authors_flags_a_human_commit_touching_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, base = _init_repo(tmp_path)
    head = _commit_as(
        repo,
        name="a maintainer",
        email="maintainer@example.com",
        message="hand-edited data",
        files={"data/wh40k-11e/edition.json": "{}\n"},
    )
    monkeypatch.chdir(repo)

    assert non_bot_data_authors(base, head) == [("a maintainer", "maintainer@example.com")]


def test_cmd_diff_accepts_a_bot_committed_candidate_pr_opened_by_a_human(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The exact regression this guards: PR #1 was bot-committed but human-opened, because this
    org disallows the default GITHUB_TOKEN from opening pull requests (candidate.yml's own
    `Open or update the candidate pull request` step fails with "GitHub Actions is not permitted
    to create or approve pull requests" until that org setting changes). The PR's opener login
    is `--actor`, still accepted for audit context, but must no longer decide the verdict."""
    repo, base = _init_repo(tmp_path)
    head = _commit_as(
        repo,
        name=BOT_NAME,
        email=BOT_EMAIL,
        message="Candidate mfm-2026-08",
        files={
            "data/wh40k-11e/edition.json": "{}\n",
            "reports/mfm-2026-08/report.json": "{}\n",
        },
    )
    monkeypatch.chdir(repo)

    code = cmd_diff(argparse.Namespace(base=base, head=head, actor="a-human-maintainer"))

    assert code == 0
    assert "OK: change class = data" in capsys.readouterr().out


def test_cmd_diff_refuses_a_human_committed_data_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, base = _init_repo(tmp_path)
    head = _commit_as(
        repo,
        name="a maintainer",
        email="maintainer@example.com",
        message="hand-edited data",
        files={"data/wh40k-11e/edition.json": "{}\n"},
    )
    monkeypatch.chdir(repo)

    code = cmd_diff(argparse.Namespace(base=base, head=head, actor="a-maintainer"))

    assert code == 1
    assert "machine-written only" in capsys.readouterr().err


def test_cmd_diff_still_refuses_a_mixed_pr_even_when_bot_committed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Bot authorship on data/ never excuses a *second* change class in the same PR -- a
    pipeline/ + data/ mix stays refused regardless of who or what committed it."""
    repo, base = _init_repo(tmp_path)
    head = _commit_as(
        repo,
        name=BOT_NAME,
        email=BOT_EMAIL,
        message="not actually what candidate.yml would ever commit",
        files={
            "data/wh40k-11e/edition.json": "{}\n",
            "pipeline/cli.py": "# changed\n",
        },
    )
    monkeypatch.chdir(repo)

    code = cmd_diff(argparse.Namespace(base=base, head=head, actor=""))

    assert code == 1
    assert "more than one change class" in capsys.readouterr().err
