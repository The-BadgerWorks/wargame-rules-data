# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the withdrawal tests (task T137):
# withdrawal sets `withdrawn` and `withdrawnReason` on exactly one entry, leaves it listed and
# retrievable, removes it as an update target, edits nothing else, and a correction publishes
# under a new version id (FR-044, SC-009).
"""Tests for FR-044, SC-009: withdrawal marks one entry without touching anything else.

`pipeline.publish.withdraw.run_withdraw` is the exact function `withdraw.yml`'s job step calls
(T141); this suite drives it directly, the same way `tests/approval/` drives
`pipeline.publish.gate.run_publish`.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from pipeline.build.manifest import ManifestError
from pipeline.exit_codes import ExitCode
from pipeline.publish.withdraw import WithdrawalError, run_withdraw


def _manifest(root: Path) -> dict[str, object]:
    text = (root / "site" / "prerelease" / "manifest.json").read_text(encoding="utf-8")
    return json.loads(text)  # type: ignore[no-any-return]


def _withdraw(config, root: Path, rules_version_id: str, reason: str):  # type: ignore[no-untyped-def]
    return run_withdraw(
        config=config,
        rules_version_id=rules_version_id,
        reason=reason,
        site_dir=root / "site",
        generated_at="2026-06-02T00:00:00Z",
        require_ci_context=False,
    )


def test_withdrawal_marks_exactly_one_entry_and_leaves_it_listed(
    channel_repo, publish_version, config
) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("withdraw-one")
    publish_version(root, "mfm-2026-05", "2026-05-01T00:00:00Z")
    publish_version(root, "mfm-2026-06", "2026-06-01T00:00:00Z")

    outcome = _withdraw(config, root, "mfm-2026-05", "Incorrect points for the Emberwrights index.")
    assert outcome.exit_code == ExitCode.SUCCESS

    entries = {e["rulesVersionId"]: e for e in _manifest(root)["versions"]}
    assert set(entries) == {"mfm-2026-05", "mfm-2026-06"}
    assert entries["mfm-2026-05"]["withdrawn"] is True
    assert (
        entries["mfm-2026-05"]["withdrawnReason"] == "Incorrect points for the Emberwrights index."
    )
    # Not offered as an update target: the app's own "newer available" rule (contract §3) is
    # keyed on `withdrawn`, and the other entry is untouched by this withdrawal.
    assert entries["mfm-2026-06"]["withdrawn"] is False


def test_withdrawal_edits_nothing_else_on_the_withdrawn_entry(
    channel_repo, publish_version, config
) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("withdraw-fields")
    publish_version(root, "mfm-2026-05", "2026-05-01T00:00:00Z")
    (before,) = _manifest(root)["versions"]

    _withdraw(config, root, "mfm-2026-05", "Duplicate detachment cost.")

    (after,) = _manifest(root)["versions"]
    expected = copy.deepcopy(before)
    expected["withdrawn"] = True
    expected["withdrawnReason"] = "Duplicate detachment cost."
    assert after == expected


def test_withdrawal_edits_nothing_on_any_other_entry(channel_repo, publish_version, config) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("withdraw-others-untouched")
    publish_version(root, "mfm-2026-05", "2026-05-01T00:00:00Z")
    publish_version(root, "mfm-2026-06", "2026-06-01T00:00:00Z")
    before = next(e for e in _manifest(root)["versions"] if e["rulesVersionId"] == "mfm-2026-06")

    _withdraw(config, root, "mfm-2026-05", "Incorrect points.")

    after = next(e for e in _manifest(root)["versions"] if e["rulesVersionId"] == "mfm-2026-06")
    assert after == before


def test_withdrawing_an_unlisted_version_is_refused(channel_repo, publish_version, config) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("withdraw-unlisted")
    publish_version(root, "mfm-2026-05", "2026-05-01T00:00:00Z")

    with pytest.raises(ManifestError):
        _withdraw(config, root, "mfm-2026-99", "Not a real version.")


def test_a_withdrawal_reason_is_required(channel_repo, publish_version, config) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("withdraw-no-reason")
    publish_version(root, "mfm-2026-05", "2026-05-01T00:00:00Z")

    with pytest.raises(WithdrawalError):
        _withdraw(config, root, "mfm-2026-05", "   ")


def test_a_withdrawn_version_is_still_retrievable(
    channel_repo, publish_version, fake_api, config
) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("withdraw-retrievable")
    result, _outcome = publish_version(root, "mfm-2026-05", "2026-05-01T00:00:00Z")

    _withdraw(config, root, "mfm-2026-05", "Incorrect points.")

    (entry,) = _manifest(root)["versions"]
    fetched = fake_api.download_asset(url=entry["fileUrl"])
    assert fetched == result.payload


def test_a_correction_publishes_under_a_new_version_id_never_replacing_the_withdrawn_one(
    channel_repo, publish_version, config
) -> None:  # type: ignore[no-untyped-def]
    root = channel_repo("withdraw-correction")
    publish_version(root, "mfm-2026-05", "2026-05-01T00:00:00Z")
    _withdraw(config, root, "mfm-2026-05", "Incorrect points.")

    publish_version(root, "mfm-2026-05-b", "2026-06-03T00:00:00Z")

    entries = {e["rulesVersionId"]: e for e in _manifest(root)["versions"]}
    assert set(entries) == {"mfm-2026-05", "mfm-2026-05-b"}
    assert entries["mfm-2026-05"]["withdrawn"] is True
    assert entries["mfm-2026-05-b"]["withdrawn"] is False


def test_withdrawal_never_rebuilds_and_never_touches_the_checksum_ledger(
    channel_repo, publish_version, config
) -> None:  # type: ignore[no-untyped-def]
    """`withdraw.yml` is deliberately not part of the `publish` job (contract §4): manifest-only,
    no rebuild, no source access. `state/published-checksums.json` records what was published,
    not the manifest's current display state, so a withdrawal leaves it untouched (T140/T141)."""
    root = channel_repo("withdraw-ledger-untouched")
    publish_version(root, "mfm-2026-05", "2026-05-01T00:00:00Z")
    before = (root / "state" / "published-checksums.json").read_text(encoding="utf-8")

    _withdraw(config, root, "mfm-2026-05", "Incorrect points.")

    after = (root / "state" / "published-checksums.json").read_text(encoding="utf-8")
    assert after == before
