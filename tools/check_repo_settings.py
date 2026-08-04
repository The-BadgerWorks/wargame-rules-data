#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Repo-settings drift checker (task T148):
# reads the live environment reviewers, branch protection, and Pages source back through the
# GitHub API and fails on divergence from `docs/repo-settings.md`, the compensating control the
# plan's Principle 5 exception names for the three classes of setting that cannot be expressed as
# code. Wired into the new `.github/workflows/settings-drift.yml`, never into `ci.yml`: the
# default Actions `GITHUB_TOKEN` has no `administration` scope (it is an app-installation-only
# permission, not something `permissions:` in a workflow can grant), so branch-protection and
# environment reads are impossible with it regardless of trigger, and a `pull_request`-triggered
# job is the wrong place for an admin-capable credential even where GitHub already withholds
# secrets from fork-originated `pull_request` runs.
"""Repo-settings drift checker for `wargame-rules-data`.

Reads three GitHub API endpoints and compares them against the desired state
`docs/repo-settings.md` §1-§3 tabulates:

* ``GET /repos/{repo}/environments`` -- the `published` and `prerelease` environments' required
  reviewers.
* ``GET /repos/{repo}/branches/main/protection`` -- the branch-protection table.
* ``GET /repos/{repo}/pages`` -- the Pages source (`build_type`).

All three need push-level (in practice, admin-capable) authentication; there is no read scope
short of that. This script never publishes anything and never touches `data/` or `curation/` --
it only reads settings and prints a diagnosis, via a token read from the ``WGC_SETTINGS_AUDIT_
TOKEN`` environment variable (a fine-grained, read-only, administration-read PAT scoped to this
one repository -- see ``.github/workflows/settings-drift.yml``'s header for the full rationale).
That token is a deliberate, narrow exception to "no long-lived PAT anywhere in this design"
(``contracts/pipeline-run-interface.md`` §5, ``pipeline/publish/github_api.py``'s own docstring):
it is read-only over settings, never a publishing credential, and it is never wired into a
``pull_request``-triggered job.

The desired-state constants below are copied from ``docs/repo-settings.md`` §1-§3, not derived
from it programmatically -- **changing one means changing both**. That duplication is the price
of the documented setting being reviewable prose rather than a machine format; keeping the
comment here pointing back at the doc is what makes the duplication a known cost rather than a
silent one.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Mapping, Sequence
from typing import Any, Final

import httpx

API_BASE: Final = "https://api.github.com"
DEFAULT_TIMEOUT_SECONDS: Final = 30.0

#: `owner/name`, exactly the form `GITHUB_REPOSITORY` is set to inside every Actions job.
DEFAULT_REPOSITORY: Final = "The-BadgerWorks/wargame-rules-data"

#: docs/repo-settings.md §1 -- required reviewer, by environment name.
DESIRED_ENVIRONMENT_REVIEWERS: Final[Mapping[str, str]] = {
    "published": "adhoxx",
    "prerelease": "adhoxx",
}

#: docs/repo-settings.md §2 -- the branch-protection table on `main`, in the doc's own order.
DESIRED_REQUIRED_APPROVING_REVIEW_COUNT: Final = 1
DESIRED_REQUIRE_CODE_OWNER_REVIEWS: Final = True
DESIRED_DISMISS_STALE_REVIEWS: Final = True
DESIRED_REQUIRED_STATUS_CHECK_CONTEXTS: Final[frozenset[str]] = frozenset(
    {"lint, typecheck, test", "change-class guard"}
)
DESIRED_REQUIRE_STRICT_STATUS_CHECKS: Final = True
DESIRED_REQUIRE_CONVERSATION_RESOLUTION: Final = True
DESIRED_ENFORCE_ADMINS: Final = False
DESIRED_ALLOW_FORCE_PUSHES: Final = False
DESIRED_ALLOW_DELETIONS: Final = False

#: docs/repo-settings.md §3 -- the Pages source.
DESIRED_PAGES_BUILD_TYPE: Final = "workflow"


class GitHubApiError(RuntimeError):
    """A GitHub API call failed. Carries the response body so a CI log is self-explanatory."""


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get(client: httpx.Client, path: str, *, token: str) -> Any:
    response = client.get(path, headers=_headers(token))
    if response.status_code >= httpx.codes.BAD_REQUEST:
        raise GitHubApiError(f"GET {path} failed: {response.status_code} {response.text}")
    return response.json()


def fetch_environments(client: httpx.Client, *, repo: str, token: str) -> Any:
    """`GET /repos/{repo}/environments`, raw."""
    return _get(client, f"/repos/{repo}/environments", token=token)


def fetch_branch_protection(
    client: httpx.Client, *, repo: str, token: str, branch: str = "main"
) -> Any:
    """`GET /repos/{repo}/branches/{branch}/protection`, raw."""
    return _get(client, f"/repos/{repo}/branches/{branch}/protection", token=token)


def fetch_pages(client: httpx.Client, *, repo: str, token: str) -> Any:
    """`GET /repos/{repo}/pages`, raw."""
    return _get(client, f"/repos/{repo}/pages", token=token)


def _environment_reviewer_logins(environment: Mapping[str, Any]) -> list[str]:
    """The `login`s named as `required_reviewers` on one environment entry."""
    logins: list[str] = []
    for rule in environment.get("protection_rules", []):
        if rule.get("type") != "required_reviewers":
            continue
        for entry in rule.get("reviewers", []):
            reviewer = entry.get("reviewer", {})
            login = reviewer.get("login")
            if login:
                logins.append(str(login))
    return logins


def check_environment_reviewers(environments_response: Mapping[str, Any]) -> list[str]:
    """Compare each environment's required reviewers against §1. Pure; no I/O."""
    by_name = {str(env.get("name")): env for env in environments_response.get("environments", [])}
    divergences: list[str] = []
    for name, desired_reviewer in sorted(DESIRED_ENVIRONMENT_REVIEWERS.items()):
        environment = by_name.get(name)
        if environment is None:
            divergences.append(f"environment {name!r} does not exist (expected it to)")
            continue
        logins = _environment_reviewer_logins(environment)
        if logins != [desired_reviewer]:
            divergences.append(
                f"environment {name!r} required reviewers are {logins!r}, expected "
                f"[{desired_reviewer!r}]"
            )
    return divergences


def check_branch_protection(protection_response: Mapping[str, Any]) -> list[str]:
    """Compare the branch-protection response against §2. Pure; no I/O."""
    divergences: list[str] = []

    reviews = protection_response.get("required_pull_request_reviews")
    if reviews is None:
        divergences.append(
            "required_pull_request_reviews is not set (expected a PR to be required)"
        )
    else:
        count = reviews.get("required_approving_review_count")
        if count != DESIRED_REQUIRED_APPROVING_REVIEW_COUNT:
            divergences.append(
                f"required_approving_review_count is {count!r}, expected "
                f"{DESIRED_REQUIRED_APPROVING_REVIEW_COUNT!r}"
            )
        code_owners = reviews.get("require_code_owner_reviews")
        if code_owners != DESIRED_REQUIRE_CODE_OWNER_REVIEWS:
            divergences.append(
                f"require_code_owner_reviews is {code_owners!r}, expected "
                f"{DESIRED_REQUIRE_CODE_OWNER_REVIEWS!r}"
            )
        dismiss = reviews.get("dismiss_stale_reviews")
        if dismiss != DESIRED_DISMISS_STALE_REVIEWS:
            divergences.append(
                f"dismiss_stale_reviews is {dismiss!r}, expected {DESIRED_DISMISS_STALE_REVIEWS!r}"
            )

    status_checks = protection_response.get("required_status_checks")
    if status_checks is None:
        divergences.append(
            "required_status_checks is not set (expected status checks to be required)"
        )
    else:
        contexts = frozenset(status_checks.get("contexts", []))
        if contexts != DESIRED_REQUIRED_STATUS_CHECK_CONTEXTS:
            divergences.append(
                f"required_status_checks.contexts are {sorted(contexts)!r}, expected "
                f"{sorted(DESIRED_REQUIRED_STATUS_CHECK_CONTEXTS)!r}"
            )
        strict = status_checks.get("strict")
        if strict != DESIRED_REQUIRE_STRICT_STATUS_CHECKS:
            divergences.append(
                f"required_status_checks.strict is {strict!r}, expected "
                f"{DESIRED_REQUIRE_STRICT_STATUS_CHECKS!r}"
            )

    conversation = protection_response.get("required_conversation_resolution", {})
    resolved = conversation.get("enabled") if isinstance(conversation, Mapping) else None
    if resolved != DESIRED_REQUIRE_CONVERSATION_RESOLUTION:
        divergences.append(
            f"required_conversation_resolution.enabled is {resolved!r}, expected "
            f"{DESIRED_REQUIRE_CONVERSATION_RESOLUTION!r}"
        )

    admins = protection_response.get("enforce_admins", {})
    admins_enabled = admins.get("enabled") if isinstance(admins, Mapping) else None
    if admins_enabled != DESIRED_ENFORCE_ADMINS:
        divergences.append(
            f"enforce_admins.enabled is {admins_enabled!r}, expected {DESIRED_ENFORCE_ADMINS!r}"
        )

    force_pushes = protection_response.get("allow_force_pushes", {})
    force_enabled = force_pushes.get("enabled") if isinstance(force_pushes, Mapping) else None
    if force_enabled != DESIRED_ALLOW_FORCE_PUSHES:
        divergences.append(
            f"allow_force_pushes.enabled is {force_enabled!r}, expected "
            f"{DESIRED_ALLOW_FORCE_PUSHES!r}"
        )

    deletions = protection_response.get("allow_deletions", {})
    deletions_enabled = deletions.get("enabled") if isinstance(deletions, Mapping) else None
    if deletions_enabled != DESIRED_ALLOW_DELETIONS:
        divergences.append(
            f"allow_deletions.enabled is {deletions_enabled!r}, expected "
            f"{DESIRED_ALLOW_DELETIONS!r}"
        )

    return divergences


def check_pages(pages_response: Mapping[str, Any]) -> list[str]:
    """Compare the Pages response against §3. Pure; no I/O."""
    build_type = pages_response.get("build_type")
    if build_type != DESIRED_PAGES_BUILD_TYPE:
        return [f"Pages build_type is {build_type!r}, expected {DESIRED_PAGES_BUILD_TYPE!r}"]
    return []


def run_check(*, repo: str, token: str, client: httpx.Client | None = None) -> list[str]:
    """Fetch all three settings and return every divergence found, in check order."""
    owns_client = client is None
    http_client = client or httpx.Client(base_url=API_BASE, timeout=DEFAULT_TIMEOUT_SECONDS)
    try:
        divergences: list[str] = []
        divergences += check_environment_reviewers(
            fetch_environments(http_client, repo=repo, token=token)
        )
        divergences += check_branch_protection(
            fetch_branch_protection(http_client, repo=repo, token=token)
        )
        divergences += check_pages(fetch_pages(http_client, repo=repo, token=token))
        return divergences
    finally:
        if owns_client:
            http_client.close()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPOSITORY),
        help="owner/name (default: $GITHUB_REPOSITORY, else the known repository)",
    )
    args = parser.parse_args(argv)

    token = os.environ.get("WGC_SETTINGS_AUDIT_TOKEN", "")
    if not token:
        print(
            "check_repo_settings: WGC_SETTINGS_AUDIT_TOKEN is not set; this check needs a "
            "read-only, administration-read PAT (see .github/workflows/settings-drift.yml)",
            file=sys.stderr,
        )
        return 1

    try:
        divergences = run_check(repo=args.repo, token=token)
    except GitHubApiError as exc:
        print(f"check_repo_settings: {exc}", file=sys.stderr)
        return 1

    if divergences:
        print(
            f"FAIL: {args.repo} has drifted from docs/repo-settings.md:",
            file=sys.stderr,
        )
        for divergence in divergences:
            print(f"  {divergence}", file=sys.stderr)
        return 1

    print(f"OK: {args.repo} matches docs/repo-settings.md §1-§3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
