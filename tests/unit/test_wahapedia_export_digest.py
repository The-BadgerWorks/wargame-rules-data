# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the export-timestamp short-circuit's
# own receipts (009 rung R05, T087-T094, FR-030/FR-031/FR-032): the skip is visible and named
# (T087), the content fingerprint is never a substitute for -- and is never gated behind -- the
# timestamp digest (T088, T092), any one export file failing fails the whole run, extended to
# Last_update.csv itself (T089), the politeness interval is unmoved and the surface reduction is
# recorded (T093), and no raw publisher timestamp is ever persisted (T094, alongside the ip/ scan
# it also extends).
"""FR-030's whole hazard in one sentence: a cheap check that says "nothing changed" when
something did. Every test here either proves the short-circuit cannot do that, or proves the
mechanism that lets it skip real work at all still behaves.

All offline. The remote-path tests use ``pytest_httpx``'s mocked transport, the same way
``test_http_politeness.py`` does; the rest use a local export directory under ``tmp_path``, which
is both the fastest way to exercise `_read_local`'s side of the short-circuit and, since
`WGC_DETAIL_SOURCE_URL` accepts a bare path, no different a code path from the one CI would run
against a mounted export.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from pipeline.acquire.http import PoliteClient, SourceUnreachable
from pipeline.acquire.wahapedia import (
    EXPORT_FILES,
    LAST_UPDATE_FILE,
    acquire_wahapedia,
)
from pipeline.config import PipelineConfig, load_config
from pipeline.models.source import AcquisitionOutcome

pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)

#: A placeholder body good enough for every table this suite never inspects the contents of --
#: only ``Last_update.csv`` and (in the T088 receipt) ``Abilities.csv`` carry meaningful text.
_PLACEHOLDER = "id|name|\n"


def _config(location: str, **overrides: str) -> PipelineConfig:
    return load_config(env={"WGC_DETAIL_SOURCE_URL": location, **overrides})


def _write_export(directory: Path, *, last_update: str, abilities: str = _PLACEHOLDER) -> None:
    """A complete, minimal, synthetic export directory -- every name `EXPORT_FILES` lists."""
    directory.mkdir(parents=True, exist_ok=True)
    for name in EXPORT_FILES:
        text = last_update if name == LAST_UPDATE_FILE else _PLACEHOLDER
        if name == "Abilities.csv":
            text = abilities
        (directory / name).write_text(text, encoding="utf-8")


# -- T088 -- the rung's central receipt: the timestamp is never a substitute ------------------


def test_content_fingerprint_detects_a_changed_payload_despite_an_unmoved_export_timestamp(
    tmp_path: Path,
) -> None:
    """FR-030, SC-010: fetch two full exports whose ``Last_update.csv`` bytes are IDENTICAL --
    the timestamp has not moved -- but whose ``Abilities.csv`` differs. The content fingerprint,
    computed as it always has been over every fetched payload, must still differ.

    No ``state_path`` is given: this is the code path every caller uses today, including
    `run_build` through `acquire_detail`, and it is the one FR-030 says must never be gated,
    weakened, or replaced by the timestamp check. If a change to `acquire_wahapedia` ever made
    the fingerprint depend on (or be skipped in favour of) the `Last_update.csv` digest, this is
    the assertion that would catch it: reusing or deriving the fingerprint from the unmoved
    timestamp would make these two acquisitions compare equal, which is exactly the failure this
    test exists to make impossible.
    """
    same_timestamp = "2026-08-01T00:00:00Z"

    directory_a = tmp_path / "export-a"
    _write_export(directory_a, last_update=same_timestamp, abilities="id|name|\n1|Bolter|\n")
    directory_b = tmp_path / "export-b"
    _write_export(directory_b, last_update=same_timestamp, abilities="id|name|\n1|Las Cannon|\n")

    # The setup's own precondition, stated as code rather than left implicit: the timestamp
    # really is byte-for-byte unmoved between the two exports.
    text_a = (directory_a / LAST_UPDATE_FILE).read_text()
    text_b = (directory_b / LAST_UPDATE_FILE).read_text()
    assert text_a == text_b

    acquisition_a, _ = acquire_wahapedia(_config(str(directory_a)), offline=True)
    acquisition_b, _ = acquire_wahapedia(_config(str(directory_b)), offline=True)

    assert acquisition_a.content_fingerprint != acquisition_b.content_fingerprint, (
        "the payload changed and the fingerprint must say so, regardless of what the export's "
        "own timestamp did"
    )
    assert acquisition_a.outcome is AcquisitionOutcome.OK
    assert acquisition_b.outcome is AcquisitionOutcome.OK


def test_the_short_circuits_own_fingerprint_never_claims_full_verification(
    tmp_path: Path,
) -> None:
    """The complementary half of T088/T092: when the short-circuit DOES fire (opted in, digest
    matched), its acquisition record must never be mistaken for "the full export was checked and
    is identical". It fingerprints only what it actually fetched -- `Last_update.csv` alone --
    which is a different, and smaller, value than the full export's fingerprint would be. A
    caller that needs the authoritative "is the content really identical" answer cannot get it
    from `outcome is UNCHANGED` alone; it has to fetch fully, which is exactly what NOT opting in
    (the default, and the only thing `run_build` does) still guarantees.
    """
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    same_timestamp = "2026-08-01T00:00:00Z"

    directory_a = tmp_path / "export-a"
    _write_export(directory_a, last_update=same_timestamp, abilities="id|name|\n1|Bolter|\n")
    directory_b = tmp_path / "export-b"
    _write_export(directory_b, last_update=same_timestamp, abilities="id|name|\n1|Las Cannon|\n")

    # Seeds state_path with directory A's Last_update.csv digest.
    acquire_wahapedia(_config(str(directory_a)), offline=True, state_path=state_path)
    # Directory B's own timestamp is byte-identical to A's, so the short-circuit fires -- even
    # though B's Abilities.csv genuinely differs from A's.
    skipped, skipped_payloads = acquire_wahapedia(
        _config(str(directory_b)), offline=True, state_path=state_path
    )
    # What a full, unshortcircuited fetch of directory B would have fingerprinted.
    full_b, _ = acquire_wahapedia(_config(str(directory_b)), offline=True)

    assert skipped.outcome is AcquisitionOutcome.UNCHANGED
    assert [p.name for p in skipped_payloads] == [LAST_UPDATE_FILE]
    assert skipped.content_fingerprint != full_b.content_fingerprint, (
        "the short-circuit's own fingerprint covers only what it fetched and must never read as "
        "though it verified the whole, genuinely-changed export"
    )


# -- T087 -- the skip is visible, and says why -------------------------------------------------


def test_an_unmoved_export_timestamp_skips_the_fetch_and_says_why(tmp_path: Path) -> None:
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    same_timestamp = "2026-08-01T00:00:00Z"

    directory_a = tmp_path / "export-a"
    _write_export(directory_a, last_update=same_timestamp)
    directory_b = tmp_path / "export-b"
    _write_export(directory_b, last_update=same_timestamp)

    first, first_payloads = acquire_wahapedia(
        _config(str(directory_a)), offline=True, state_path=state_path
    )
    second, second_payloads = acquire_wahapedia(
        _config(str(directory_b)), offline=True, state_path=state_path
    )

    assert first.outcome is AcquisitionOutcome.OK
    assert len(first_payloads) == len(EXPORT_FILES)

    assert second.outcome is AcquisitionOutcome.UNCHANGED
    assert [p.name for p in second_payloads] == [LAST_UPDATE_FILE]
    assert len(second.findings) == 1
    assert second.findings[0].finding_code == "SRC-EXPORT-UNCHANGED"
    assert second.findings[0].detail == {"table": LAST_UPDATE_FILE}


def test_a_moved_export_timestamp_does_not_skip(tmp_path: Path) -> None:
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"

    directory_a = tmp_path / "export-a"
    _write_export(directory_a, last_update="2026-08-01T00:00:00Z")
    directory_b = tmp_path / "export-b"
    _write_export(directory_b, last_update="2026-08-08T00:00:00Z")

    acquire_wahapedia(_config(str(directory_a)), offline=True, state_path=state_path)
    second, second_payloads = acquire_wahapedia(
        _config(str(directory_b)), offline=True, state_path=state_path
    )

    assert second.outcome is AcquisitionOutcome.OK
    assert second.findings == ()
    assert len(second_payloads) == len(EXPORT_FILES)


def test_the_first_run_never_skips_there_is_nothing_to_compare_against(tmp_path: Path) -> None:
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    directory = tmp_path / "export"
    _write_export(directory, last_update="2026-08-01T00:00:00Z")

    acquisition, payloads = acquire_wahapedia(
        _config(str(directory)), offline=True, state_path=state_path
    )

    assert acquisition.outcome is AcquisitionOutcome.OK
    assert len(payloads) == len(EXPORT_FILES)
    assert state_path.exists(), "the digest is recorded even on the run that could not skip"


def test_no_state_path_is_a_total_no_op(tmp_path: Path) -> None:
    """The default. Calling `acquire_wahapedia` exactly as every existing caller (and `run_build`
    through `acquire_detail`) does must never skip anything, whatever `Last_update.csv` says."""
    directory = tmp_path / "export"
    _write_export(directory, last_update="2026-08-01T00:00:00Z")

    first, first_payloads = acquire_wahapedia(_config(str(directory)), offline=True)
    second, second_payloads = acquire_wahapedia(_config(str(directory)), offline=True)

    assert first.outcome is AcquisitionOutcome.OK
    assert second.outcome is AcquisitionOutcome.OK
    assert len(first_payloads) == len(EXPORT_FILES)
    assert len(second_payloads) == len(EXPORT_FILES)


# -- T090 -- the digest is one-way, and never the raw timestamp --------------------------------


def test_the_persisted_state_holds_a_digest_never_the_raw_timestamp(tmp_path: Path) -> None:
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    directory = tmp_path / "export"
    raw_timestamp = "2026-08-01T00:00:00Z"
    _write_export(directory, last_update=raw_timestamp)

    acquire_wahapedia(_config(str(directory)), offline=True, state_path=state_path)

    raw = json.loads(state_path.read_text(encoding="utf-8"))
    assert set(raw) == {"digest"}
    assert raw["digest"] != raw_timestamp
    assert raw_timestamp not in state_path.read_text(encoding="utf-8")
    # sha256 hex: 64 lowercase hex characters, nothing else.
    assert len(raw["digest"]) == 64
    assert all(c in "0123456789abcdef" for c in raw["digest"])


# -- T089 -- no partial export, extended to Last_update.csv and the derived tables -------------


def test_a_missing_last_update_csv_fails_the_whole_local_run(tmp_path: Path) -> None:
    directory = tmp_path / "export"
    _write_export(directory, last_update="2026-08-01T00:00:00Z")
    (directory / LAST_UPDATE_FILE).unlink()

    with pytest.raises(SourceUnreachable, match=LAST_UPDATE_FILE):
        acquire_wahapedia(_config(str(directory)), offline=True)


def test_a_missing_file_among_the_rest_still_fails_the_whole_local_run_no_partial_export(
    tmp_path: Path,
) -> None:
    """The pre-existing FR-032 guarantee, pinned rather than changed, extended to prove it still
    holds once `Last_update.csv` is read first and separately from the rest: a caller cannot walk
    away with `Last_update.csv` plus a partial remainder."""
    directory = tmp_path / "export"
    _write_export(directory, last_update="2026-08-01T00:00:00Z")
    (directory / "Detachment_abilities.csv").unlink()

    with pytest.raises(SourceUnreachable, match="Detachment_abilities.csv"):
        acquire_wahapedia(_config(str(directory)), offline=True)


def test_a_missing_file_among_the_rest_fails_even_when_the_short_circuit_does_not_fire(
    tmp_path: Path,
) -> None:
    """The same pin, under `state_path`: a moved timestamp forces the full fetch, and that full
    fetch must still fail whole on one missing file rather than silently returning a partial
    set with an `UNCHANGED`-shaped outcome."""
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    directory_a = tmp_path / "export-a"
    _write_export(directory_a, last_update="2026-08-01T00:00:00Z")
    directory_b = tmp_path / "export-b"
    _write_export(directory_b, last_update="2026-08-08T00:00:00Z")
    (directory_b / "Enhancements.csv").unlink()

    acquire_wahapedia(_config(str(directory_a)), offline=True, state_path=state_path)
    with pytest.raises(SourceUnreachable, match="Enhancements.csv"):
        acquire_wahapedia(_config(str(directory_b)), offline=True, state_path=state_path)


# -- T092 -- the fingerprint is computed over every fetched payload, unconditionally -----------


def test_the_fingerprint_is_never_computed_from_last_update_csv_alone_on_a_full_fetch(
    tmp_path: Path,
) -> None:
    """A full fetch's fingerprint must be sensitive to every file, not just the one the
    short-circuit probes first. Change ONLY a file that is not `Last_update.csv` or `Abilities.csv`
    and confirm the fingerprint still moves."""
    directory_a = tmp_path / "export-a"
    _write_export(directory_a, last_update="2026-08-01T00:00:00Z")
    (directory_a / "Factions.csv").write_text("id|name|\nSM|Space Marines|\n", encoding="utf-8")

    directory_b = tmp_path / "export-b"
    _write_export(directory_b, last_update="2026-08-01T00:00:00Z")
    (directory_b / "Factions.csv").write_text("id|name|\nOR|Orks|\n", encoding="utf-8")

    acquisition_a, _ = acquire_wahapedia(_config(str(directory_a)), offline=True)
    acquisition_b, _ = acquire_wahapedia(_config(str(directory_b)), offline=True)

    assert acquisition_a.content_fingerprint != acquisition_b.content_fingerprint


# -- T093 -- politeness unchanged; the surface reduction is recorded ---------------------------

HOST = "https://wahapedia.example"
ROBOTS = f"{HOST}/robots.txt"
ALLOW_ALL = "User-agent: *\nAllow: /\n"


class _Recorder:
    """A stand-in clock and sleeper (the same shape `test_http_politeness.py` uses), so the
    polite interval is asserted rather than actually spent."""

    def __init__(self) -> None:
        self.sleeps: list[float] = []

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)

    def monotonic(self) -> float:
        return 0.0


def _remote_config(**overrides: str) -> PipelineConfig:
    return load_config(
        env={
            "WGC_DETAIL_SOURCE_URL": HOST,
            "WGC_REQUEST_INTERVAL_MS": "1500",
            **overrides,
        }
    )


def test_the_smaller_request_set_still_honours_the_configured_interval_and_is_recorded(
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(url=ROBOTS, text=ALLOW_ALL, is_reusable=True)
    same_timestamp = "2026-08-01T00:00:00Z"
    for name in EXPORT_FILES:
        text = same_timestamp if name == LAST_UPDATE_FILE else _PLACEHOLDER
        httpx_mock.add_response(url=f"{HOST}/{name}", text=text, is_reusable=True)

    recorder = _Recorder()

    with (
        PoliteClient(
            _remote_config(),
            sleep=recorder.sleep,
            monotonic=recorder.monotonic,
            jitter=lambda: 0.0,
        ) as client,
        tempfile.TemporaryDirectory() as tmp,
    ):
        state_path = Path(tmp) / "wahapedia-export-digest.json"

        first, first_payloads = acquire_wahapedia(
            _remote_config(), client=client, state_path=state_path
        )
        requests_after_first = client.request_count
        sleeps_after_first = len(recorder.sleeps)

        second, second_payloads = acquire_wahapedia(
            _remote_config(), client=client, state_path=state_path
        )

    assert first.outcome is AcquisitionOutcome.OK
    assert len(first_payloads) == len(EXPORT_FILES)
    assert requests_after_first == 1 + len(EXPORT_FILES)  # robots.txt + every export file

    assert second.outcome is AcquisitionOutcome.UNCHANGED
    assert len(second_payloads) == 1
    # Politeness is unchanged (FR-032): the one new request the short-circuit makes still waits
    # out the SAME configured interval as every other request did -- no faster path for a
    # smaller request set.
    new_sleeps = recorder.sleeps[sleeps_after_first:]
    assert new_sleeps == [pytest.approx(1.5)]
    # The surface reduction itself: one request instead of seventeen.
    assert client.request_count - requests_after_first == 1

    # T093's other half: the reduction is recorded in the run record, not just observable via
    # the client's own counter, which a curator reading a report never sees.
    assert second.coverage["csv_files"] == 1
    assert second.coverage["csv_files_total"] == len(EXPORT_FILES)
