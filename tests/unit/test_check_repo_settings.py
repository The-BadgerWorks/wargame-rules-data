# AI-Assisted: Claude Code (model: claude-sonnet-5) - Unit tests for the comparison logic of
# tools/check_repo_settings.py (task T148): canned JSON fixtures shaped exactly like the three
# GitHub API responses, asserting a clean fixture set diverges on nothing and each individual
# divergence from docs/repo-settings.md §1-§3 is caught. tools/ is not an installed package, so
# the module is loaded directly from its file path (mirrors
# tests/unit/test_check_change_classes.py). The fetch layer (fetch_environments/
# fetch_branch_protection/fetch_pages/run_check) is exercised with pytest-httpx, never a real
# socket -- the suite-wide guard in tests/conftest.py would fail any test that tried.
from __future__ import annotations

import importlib.util
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from pytest_httpx import HTTPXMock

_MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "check_repo_settings.py"
_spec = importlib.util.spec_from_file_location("check_repo_settings", _MODULE_PATH)
assert _spec is not None and _spec.loader is not None
check_repo_settings = importlib.util.module_from_spec(_spec)
sys.modules["check_repo_settings"] = check_repo_settings
_spec.loader.exec_module(check_repo_settings)

pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)

REPO = "The-BadgerWorks/wargame-rules-data"
TOKEN = "gh-fine-grained-test-token"


def _environments_response() -> dict[str, Any]:
    """Shaped exactly like `GET /repos/{repo}/environments` — §1, both environments compliant."""

    def _env(name: str) -> dict[str, Any]:
        return {
            "name": name,
            "protection_rules": [
                {
                    "type": "required_reviewers",
                    "reviewers": [{"type": "User", "reviewer": {"login": "adhoxx"}}],
                }
            ],
        }

    return {"total_count": 2, "environments": [_env("published"), _env("prerelease")]}


def _branch_protection_response() -> dict[str, Any]:
    """Shaped exactly like `GET /repos/{repo}/branches/main/protection` — §2, fully compliant."""
    return {
        "required_status_checks": {
            "strict": True,
            "contexts": ["lint, typecheck, test", "change-class guard"],
        },
        "enforce_admins": {"enabled": False},
        "required_pull_request_reviews": {
            "required_approving_review_count": 1,
            "require_code_owner_reviews": True,
            "dismiss_stale_reviews": True,
        },
        "restrictions": None,
        "required_conversation_resolution": {"enabled": True},
        "allow_force_pushes": {"enabled": False},
        "allow_deletions": {"enabled": False},
    }


def _pages_response() -> dict[str, Any]:
    """Shaped exactly like `GET /repos/{repo}/pages` — §3, fully compliant."""
    return {
        "url": "https://api.github.com/repos/The-BadgerWorks/wargame-rules-data/pages",
        "status": "built",
        "build_type": "workflow",
    }


# --- environments (§1) ------------------------------------------------------------------------


def test_compliant_environments_have_no_divergence() -> None:
    assert check_repo_settings.check_environment_reviewers(_environments_response()) == []


def test_a_missing_environment_is_a_divergence() -> None:
    response = _environments_response()
    response["environments"] = [
        env for env in response["environments"] if env["name"] != "prerelease"
    ]

    divergences = check_repo_settings.check_environment_reviewers(response)

    assert any("prerelease" in d and "does not exist" in d for d in divergences)


def test_a_wrong_reviewer_is_a_divergence() -> None:
    response = _environments_response()
    response["environments"][0]["protection_rules"][0]["reviewers"][0]["reviewer"]["login"] = (
        "someone-else"
    )

    divergences = check_repo_settings.check_environment_reviewers(response)

    assert len(divergences) == 1
    assert "someone-else" in divergences[0]


def test_no_required_reviewers_rule_at_all_is_a_divergence() -> None:
    response = _environments_response()
    response["environments"][0]["protection_rules"] = []

    divergences = check_repo_settings.check_environment_reviewers(response)

    assert len(divergences) == 1
    assert "published" in divergences[0]


# --- branch protection (§2) -------------------------------------------------------------------


def test_compliant_branch_protection_has_no_divergence() -> None:
    assert check_repo_settings.check_branch_protection(_branch_protection_response()) == []


def test_wrong_required_approving_review_count_is_a_divergence() -> None:
    response = _branch_protection_response()
    response["required_pull_request_reviews"]["required_approving_review_count"] = 0

    divergences = check_repo_settings.check_branch_protection(response)

    assert any("required_approving_review_count" in d for d in divergences)


def test_missing_status_check_context_is_a_divergence() -> None:
    response = _branch_protection_response()
    response["required_status_checks"]["contexts"] = ["lint, typecheck, test"]

    divergences = check_repo_settings.check_branch_protection(response)

    assert any("contexts" in d for d in divergences)


def test_enforce_admins_flipped_to_true_is_a_divergence() -> None:
    # Deliberate: docs/repo-settings.md records `enforce_admins: false` as today's documented
    # reality, not a floor. A flip either way is drift from what the doc currently says.
    response = _branch_protection_response()
    response["enforce_admins"]["enabled"] = True

    divergences = check_repo_settings.check_branch_protection(response)

    assert any("enforce_admins" in d for d in divergences)


def test_force_pushes_allowed_is_a_divergence() -> None:
    response = _branch_protection_response()
    response["allow_force_pushes"]["enabled"] = True

    divergences = check_repo_settings.check_branch_protection(response)

    assert any("allow_force_pushes" in d for d in divergences)


def test_deletions_allowed_is_a_divergence() -> None:
    response = _branch_protection_response()
    response["allow_deletions"]["enabled"] = True

    divergences = check_repo_settings.check_branch_protection(response)

    assert any("allow_deletions" in d for d in divergences)


def test_conversation_resolution_not_required_is_a_divergence() -> None:
    response = _branch_protection_response()
    response["required_conversation_resolution"]["enabled"] = False

    divergences = check_repo_settings.check_branch_protection(response)

    assert any("required_conversation_resolution" in d for d in divergences)


def test_no_pull_request_reviews_required_at_all_is_a_divergence() -> None:
    response = _branch_protection_response()
    response["required_pull_request_reviews"] = None

    divergences = check_repo_settings.check_branch_protection(response)

    assert any("required_pull_request_reviews" in d for d in divergences)


# --- pages (§3) --------------------------------------------------------------------------------


def test_compliant_pages_has_no_divergence() -> None:
    assert check_repo_settings.check_pages(_pages_response()) == []


def test_legacy_pages_build_type_is_a_divergence() -> None:
    response = _pages_response()
    response["build_type"] = "legacy"

    divergences = check_repo_settings.check_pages(response)

    assert len(divergences) == 1
    assert "legacy" in divergences[0]


# --- the fetch layer, mocked (no real network; tests/conftest.py blocks real sockets) ----------


def test_run_check_against_a_fully_compliant_repo_finds_nothing(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url=f"{check_repo_settings.API_BASE}/repos/{REPO}/environments",
        json=_environments_response(),
    )
    httpx_mock.add_response(
        url=f"{check_repo_settings.API_BASE}/repos/{REPO}/branches/main/protection",
        json=_branch_protection_response(),
    )
    httpx_mock.add_response(
        url=f"{check_repo_settings.API_BASE}/repos/{REPO}/pages",
        json=_pages_response(),
    )

    assert check_repo_settings.run_check(repo=REPO, token=TOKEN) == []


def test_run_check_collects_divergences_from_every_endpoint(httpx_mock: HTTPXMock) -> None:
    bad_environments = deepcopy(_environments_response())
    bad_environments["environments"][0]["protection_rules"][0]["reviewers"][0]["reviewer"][
        "login"
    ] = "someone-else"
    bad_pages = deepcopy(_pages_response())
    bad_pages["build_type"] = "legacy"

    httpx_mock.add_response(
        url=f"{check_repo_settings.API_BASE}/repos/{REPO}/environments", json=bad_environments
    )
    httpx_mock.add_response(
        url=f"{check_repo_settings.API_BASE}/repos/{REPO}/branches/main/protection",
        json=_branch_protection_response(),
    )
    httpx_mock.add_response(
        url=f"{check_repo_settings.API_BASE}/repos/{REPO}/pages", json=bad_pages
    )

    divergences = check_repo_settings.run_check(repo=REPO, token=TOKEN)

    assert any("someone-else" in d for d in divergences)
    assert any("legacy" in d for d in divergences)


def test_a_failed_api_call_raises_github_api_error(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url=f"{check_repo_settings.API_BASE}/repos/{REPO}/environments",
        status_code=403,
        text="token lacks administration:read",
    )

    with pytest.raises(check_repo_settings.GitHubApiError):
        check_repo_settings.run_check(repo=REPO, token=TOKEN)


# --- main() ---------------------------------------------------------------------------------


def test_main_fails_fast_with_no_diagnostic_leak_when_token_is_unset(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("WGC_SETTINGS_AUDIT_TOKEN", raising=False)

    code = check_repo_settings.main(["--repo", REPO])

    assert code == 1
    assert "WGC_SETTINGS_AUDIT_TOKEN" in capsys.readouterr().err


def test_main_reports_ok_on_a_compliant_repo(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], httpx_mock: HTTPXMock
) -> None:
    monkeypatch.setenv("WGC_SETTINGS_AUDIT_TOKEN", TOKEN)
    httpx_mock.add_response(
        url=f"{check_repo_settings.API_BASE}/repos/{REPO}/environments",
        json=_environments_response(),
    )
    httpx_mock.add_response(
        url=f"{check_repo_settings.API_BASE}/repos/{REPO}/branches/main/protection",
        json=_branch_protection_response(),
    )
    httpx_mock.add_response(
        url=f"{check_repo_settings.API_BASE}/repos/{REPO}/pages",
        json=_pages_response(),
    )

    code = check_repo_settings.main(["--repo", REPO])

    assert code == 0
    assert "OK" in capsys.readouterr().out
