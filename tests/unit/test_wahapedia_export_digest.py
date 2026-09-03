# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the export-timestamp short-circuit's
# own receipts (009 rung R05, T087-T094, FR-030/FR-031/FR-032): the skip is visible and named
# (T087), the content fingerprint is never a substitute for -- and is never gated behind -- the
# timestamp digest (T088, T092), any one export file failing fails the whole run, extended to
# Last_update.csv itself (T089), the politeness interval is unmoved and the surface reduction is
# recorded (T093), and no raw publisher timestamp is ever persisted (T094, alongside the ip/ scan
# it also extends).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix (gate on PR #30): item 1's own
# both-directions receipt (the probe alone must never move the fingerprint or acquisition_id; a
# real corpus change still must), item 4's receipt (a corrupt state file raises the mapped
# ExportStateCorrupt instead of an unhandled JSONDecodeError/AttributeError -- confirmed against
# today's code first), and item 5's receipt (a digest match recorded under a different source
# identity is "no comparable prior", not a skip). Every test that used two separate directories
# to stand in for "the same source polled twice" was rewritten onto one directory mutated in
# place, because two directories are, correctly, two different `source_base_url` identities now
# -- the original shape would have made several of these pass vacuously off the identity check
# alone rather than off the mechanism each one names.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix2 item 3 (gate on PR #30): item 1's
# both-directions receipt, extended to the `--fixtures` path the previous round's own test never
# exercised (the fixture adapter names the probe by its stem, and the previous fix's
# `_corpus_payloads` matched only the exact string `"Last_update.csv"`, so under `--fixtures` the
# probe WAS corpus in every `fixtures/detection/*` set -- confirmed red against today's code
# first, per this repository's own "failing-first is the house form" rule).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix2 item 2 (gate on PR #30): the
# empty-corpus constant `content_fingerprint([])` must never surface as an UNCHANGED
# acquisition's own `content_fingerprint` or `acquisition_id` -- confirmed red against today's
# code first, per the same house rule.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix2 item 4 (gate on PR #30):
# `coverage["csv_files"]` and the content fingerprint described different sets (the former
# counted the probe, the latter excluded it) under one shared name -- two new tests assert the
# now-separately-named `csv_files` / `corpus_files` figures agree with what each actually counts,
# on both the live path and `--fixtures`.
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
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pytest_httpx import HTTPXMock

from pipeline.acquire.fixtures import FixturePayload, content_fingerprint
from pipeline.acquire.http import PoliteClient, SourceUnreachable
from pipeline.acquire.wahapedia import (
    EXPORT_FILES,
    LAST_UPDATE_FILE,
    ExportStateCorrupt,
    acquire_wahapedia,
    export_digest_state_for,
    load_export_digest_state,
    save_export_digest_state,
)
from pipeline.config import PipelineConfig, load_config
from pipeline.models.source import AcquisitionOutcome, SourceAcquisition

pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)

#: A placeholder body good enough for every table this suite never inspects the contents of --
#: only ``Last_update.csv`` and (in the T088 receipt) ``Abilities.csv`` carry meaningful text.
_PLACEHOLDER = "id|name|\n"


def _config(location: str, **overrides: str) -> PipelineConfig:
    return load_config(env={"WGC_DETAIL_SOURCE_URL": location, **overrides})


def _seed_state(
    config: PipelineConfig, state_path: Path
) -> tuple[SourceAcquisition, list[FixturePayload]]:
    """Acquire once, then persist the resulting digest state -- the same two calls a real
    opted-in caller makes only after its own downstream work succeeds (R05-fix item 2).
    `acquire_wahapedia` deliberately no longer saves its own state, so every test in this file
    that needs "a prior run on record" goes through this helper rather than relying on a single
    `acquire_wahapedia(..., state_path=...)` call to have written anything.
    """
    acquisition, payloads = acquire_wahapedia(config, offline=True, state_path=state_path)
    state = export_digest_state_for(config, acquisition, payloads)
    assert state is not None, "a real acquisition always carries Last_update.csv"
    save_export_digest_state(state_path, state)
    return acquisition, payloads


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
    directory = tmp_path / "export"
    config = _config(str(directory))

    # Seeds state_path with the source's own Last_update.csv digest.
    _write_export(directory, last_update=same_timestamp, abilities="id|name|\n1|Bolter|\n")
    _seed_state(config, state_path)

    # The SAME source (item 5: identical source_base_url/declared_edition_code/mode) polled
    # again: its own timestamp is byte-identical, so the short-circuit fires -- even though
    # Abilities.csv genuinely changed underneath it.
    _write_export(directory, last_update=same_timestamp, abilities="id|name|\n1|Las Cannon|\n")
    skipped, skipped_payloads = acquire_wahapedia(config, offline=True, state_path=state_path)
    # What a full, unshortcircuited fetch of the (now-changed) source would have fingerprinted.
    full, _ = acquire_wahapedia(config, offline=True)

    assert skipped.outcome is AcquisitionOutcome.UNCHANGED
    assert [p.name for p in skipped_payloads] == [LAST_UPDATE_FILE]
    assert skipped.content_fingerprint != full.content_fingerprint, (
        "the short-circuit's own fingerprint covers only what it fetched and must never read as "
        "though it verified the whole, genuinely-changed export"
    )


# -- T087 -- the skip is visible, and says why -------------------------------------------------


def test_an_unmoved_export_timestamp_skips_the_fetch_and_says_why(tmp_path: Path) -> None:
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    directory = tmp_path / "export"
    _write_export(directory, last_update="2026-08-01T00:00:00Z")
    config = _config(str(directory))

    first, first_payloads = _seed_state(config, state_path)
    second, second_payloads = acquire_wahapedia(config, offline=True, state_path=state_path)

    assert first.outcome is AcquisitionOutcome.OK
    assert len(first_payloads) == len(EXPORT_FILES)

    assert second.outcome is AcquisitionOutcome.UNCHANGED
    assert [p.name for p in second_payloads] == [LAST_UPDATE_FILE]
    assert len(second.findings) == 1
    assert second.findings[0].finding_code == "SRC-EXPORT-UNCHANGED"
    assert second.findings[0].detail == {"table": LAST_UPDATE_FILE}


def test_a_moved_export_timestamp_does_not_skip(tmp_path: Path) -> None:
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    directory = tmp_path / "export"
    config = _config(str(directory))

    _write_export(directory, last_update="2026-08-01T00:00:00Z")
    _seed_state(config, state_path)

    _write_export(directory, last_update="2026-08-08T00:00:00Z")
    second, second_payloads = acquire_wahapedia(config, offline=True, state_path=state_path)

    assert second.outcome is AcquisitionOutcome.OK
    assert second.findings == ()
    assert len(second_payloads) == len(EXPORT_FILES)


def test_the_first_run_never_skips_there_is_nothing_to_compare_against(tmp_path: Path) -> None:
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    directory = tmp_path / "export"
    _write_export(directory, last_update="2026-08-01T00:00:00Z")
    config = _config(str(directory))

    acquisition, payloads = acquire_wahapedia(config, offline=True, state_path=state_path)

    assert acquisition.outcome is AcquisitionOutcome.OK
    assert len(payloads) == len(EXPORT_FILES)
    assert not state_path.exists(), (
        "R05-fix item 2: acquisition alone never advances the state, whatever `state_path` says "
        "-- only a caller whose own downstream work has succeeded does, by calling "
        "export_digest_state_for/save_export_digest_state itself"
    )

    state = export_digest_state_for(config, acquisition, payloads)
    assert state is not None
    save_export_digest_state(state_path, state)
    assert state_path.exists(), "the caller's own save is what actually records it"


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

    _seed_state(_config(str(directory)), state_path)

    raw = json.loads(state_path.read_text(encoding="utf-8"))
    # R05-fix item 5: the source identity the digest was taken under joins it -- never anything
    # that could reconstruct the raw text. R05-fix2 item 2: `content_fingerprint` joins it too --
    # a corpus fingerprint, not the raw text either.
    assert set(raw) == {
        "digest",
        "content_fingerprint",
        "source_base_url",
        "declared_edition_code",
        "mode",
    }
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
    directory = tmp_path / "export"
    config = _config(str(directory))
    _write_export(directory, last_update="2026-08-01T00:00:00Z")
    _seed_state(config, state_path)

    _write_export(directory, last_update="2026-08-08T00:00:00Z")
    (directory / "Enhancements.csv").unlink()
    with pytest.raises(SourceUnreachable, match="Enhancements.csv"):
        acquire_wahapedia(config, offline=True, state_path=state_path)


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


# -- R05-fix item 1 -- the probe must not enter the content fingerprint or acquisition_id -------
#
# PR #30's gate: `Last_update.csv` was folded into `EXPORT_FILES`, and `content_fingerprint`
# fingerprints every fetched payload unconditionally -- including on the plain `state_path=None`
# path every existing caller (including `run_build`) uses. Verified against the real mirror, the
# file is a bare export-regeneration timestamp, so this moved the authoritative change signal on
# every republish with no rules change at all. These two tests are the rung's own both-directions
# receipt: the first is red against the code this rung inherited.


def test_changing_only_the_probe_does_not_move_the_fingerprint_or_acquisition_id(
    tmp_path: Path,
) -> None:
    """Direction 1: the probe alone moves. Nothing that matters may move with it."""
    directory_a = tmp_path / "export-a"
    _write_export(directory_a, last_update="2026-08-01T00:00:00Z")
    directory_b = tmp_path / "export-b"
    _write_export(directory_b, last_update="2026-08-08T00:00:00Z")  # only the probe differs

    same_moment = datetime(2026, 8, 9, tzinfo=UTC)
    acquisition_a, _ = acquire_wahapedia(
        _config(str(directory_a)), offline=True, retrieved_at=same_moment
    )
    acquisition_b, _ = acquire_wahapedia(
        _config(str(directory_b)), offline=True, retrieved_at=same_moment
    )

    assert acquisition_a.content_fingerprint == acquisition_b.content_fingerprint, (
        "Last_update.csv is a probe, not corpus content -- its own text moving must never move "
        "the content fingerprint"
    )
    assert acquisition_a.acquisition_id == acquisition_b.acquisition_id, (
        "acquisition_id is derived from the fingerprint -- it must not move either"
    )


def test_changing_a_real_export_file_still_moves_the_fingerprint(tmp_path: Path) -> None:
    """Direction 2: the complementary half -- fixing direction 1 must not numb the fingerprint
    to an actual rules change."""
    directory_a = tmp_path / "export-a"
    _write_export(
        directory_a, last_update="2026-08-01T00:00:00Z", abilities="id|name|\n1|Bolter|\n"
    )
    directory_b = tmp_path / "export-b"
    _write_export(
        directory_b, last_update="2026-08-01T00:00:00Z", abilities="id|name|\n1|Las Cannon|\n"
    )

    acquisition_a, _ = acquire_wahapedia(_config(str(directory_a)), offline=True)
    acquisition_b, _ = acquire_wahapedia(_config(str(directory_b)), offline=True)

    assert acquisition_a.content_fingerprint != acquisition_b.content_fingerprint, (
        "a genuine corpus change must still move the fingerprint"
    )


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
        # R05-fix item 2: the caller persists the state itself, only once its own downstream
        # work (nothing, in this test) has succeeded -- acquire_wahapedia no longer does.
        first_state = export_digest_state_for(_remote_config(), first, first_payloads)
        assert first_state is not None
        save_export_digest_state(state_path, first_state)
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


# -- R05-fix item 4 -- a corrupt state file is a mapped failure, not a bare traceback -----------
#
# Confirmed against today's code first: a JSON-decode failure on `state_path` propagated as a
# bare `json.decoder.JSONDecodeError` -- not an `AcquisitionError` -- so the CLI's exit-code
# mapping never saw it and the process died with an unmapped traceback instead of a clean exit.


def test_a_non_json_state_file_raises_the_mapped_error(tmp_path: Path) -> None:
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text("not json{{{", encoding="utf-8")

    with pytest.raises(ExportStateCorrupt):
        load_export_digest_state(state_path)


def test_a_state_file_holding_a_json_array_raises_the_mapped_error(tmp_path: Path) -> None:
    """Valid JSON, wrong shape: a list has no `.get`, which is `AttributeError` today -- also
    unmapped, also fixed the same way."""
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text("[1, 2, 3]", encoding="utf-8")

    with pytest.raises(ExportStateCorrupt):
        load_export_digest_state(state_path)


def test_a_corrupt_state_file_fails_the_whole_acquisition_rather_than_fetching_blindly(
    tmp_path: Path,
) -> None:
    """Fail closed end to end: the corrupt file must stop the run through `acquire_wahapedia`
    itself, not merely through the loader in isolation -- and it must never be silently treated
    as "no prior" and let the short-circuit fire (or even attempt to)."""
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text("not json{{{", encoding="utf-8")
    directory = tmp_path / "export"
    _write_export(directory, last_update="2026-08-01T00:00:00Z")

    with pytest.raises(ExportStateCorrupt):
        acquire_wahapedia(_config(str(directory)), offline=True, state_path=state_path)


# -- R05-fix item 5 -- the digest is only comparable under a matching source identity -----------


def test_a_digest_match_under_a_different_source_base_url_does_not_skip(tmp_path: Path) -> None:
    """The exact hazard item 5 closes: two differently-configured sources whose probes happen to
    carry byte-identical text must never let one's prior state wrongly skip the other's fetch."""
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    same_timestamp = "2026-08-01T00:00:00Z"

    directory_a = tmp_path / "export-a"
    _write_export(directory_a, last_update=same_timestamp)
    directory_b = tmp_path / "export-b"
    _write_export(directory_b, last_update=same_timestamp)

    _seed_state(_config(str(directory_a)), state_path)
    # directory_b is a DIFFERENT source_base_url carrying the SAME Last_update.csv text -- the
    # digest alone would match, but the identity does not.
    second, second_payloads = acquire_wahapedia(
        _config(str(directory_b)), offline=True, state_path=state_path
    )

    assert second.outcome is AcquisitionOutcome.OK, (
        "a digest match recorded under a different source is not comparable -- it must fetch, "
        "never skip"
    )
    assert second.findings == ()
    assert len(second_payloads) == len(EXPORT_FILES)


def test_a_digest_match_under_a_different_declared_edition_does_not_skip(tmp_path: Path) -> None:
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    directory = tmp_path / "export"
    _write_export(directory, last_update="2026-08-01T00:00:00Z")

    _seed_state(_config(str(directory)), state_path)
    reconfigured = _config(str(directory), WGC_DETAIL_EDITION="wh40k-11e")
    second, second_payloads = acquire_wahapedia(reconfigured, offline=True, state_path=state_path)

    assert second.outcome is AcquisitionOutcome.OK, (
        "a digest recorded under a different declared edition is not comparable -- it must "
        "fetch, never skip"
    )
    assert len(second_payloads) == len(EXPORT_FILES)


def test_an_identity_mismatch_is_not_an_error(tmp_path: Path) -> None:
    """The other half of item 5: a mismatch is an ordinary "no comparable prior", never a
    failure -- distinct from item 4's corrupt-file case, which IS one."""
    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    directory_a = tmp_path / "export-a"
    _write_export(directory_a, last_update="2026-08-01T00:00:00Z")
    directory_b = tmp_path / "export-b"
    _write_export(directory_b, last_update="2026-08-01T00:00:00Z")

    _seed_state(_config(str(directory_a)), state_path)
    second, _ = acquire_wahapedia(_config(str(directory_b)), offline=True, state_path=state_path)

    assert second.outcome is AcquisitionOutcome.OK
    assert second.findings == ()


# -- R05-fix2 item 2 -- an UNCHANGED acquisition never reports the empty-corpus constant --------
#
# `_corpus_payloads` strips the short-circuit's only fetched payload (the probe), so
# `content_fingerprint([])` -- ONE constant, identical for every source and every run -- was
# recorded as BOTH the acquisition's own `content_fingerprint` AND, via its first 8 hex
# characters, its `acquisition_id`, on every UNCHANGED acquisition against every source. That is
# a fingerprint claiming the corpus is empty when it is, by definition, unchanged from whatever
# it was last measured to be.
#
# Decision: an UNCHANGED acquisition carries the PREVIOUS acquisition's own corpus fingerprint
# forward (`ExportDigestState.content_fingerprint`), rather than declining to report one.
# `SourceAcquisition.content_fingerprint` is a required `str` field project-wide -- making it
# optional would ripple into every consumer that reads it (`report/validation.py`'s coverage
# row, `acquisition_id`'s own derivation) for one narrow case. "The same corpus as last time" is
# also exactly what UNCHANGED already means for every OTHER field on the record (the digest
# matched, the identity matched); the fingerprint should say the same thing the outcome already
# does, not something that contradicts it.


def test_the_empty_corpus_constant_is_never_an_acquisition_fingerprint(tmp_path: Path) -> None:
    """Red against the code this rung inherited: before this fix, `skipped.content_fingerprint`
    equalled `f"sha256:{empty_corpus_constant}"` -- the SAME constant on every source, every run.
    """
    empty_corpus_constant = content_fingerprint([])

    state_path = tmp_path / "state" / "wahapedia-export-digest.json"
    directory = tmp_path / "export"
    _write_export(directory, last_update="2026-08-01T00:00:00Z")
    config = _config(str(directory))
    seeded, _ = _seed_state(config, state_path)

    skipped, skipped_payloads = acquire_wahapedia(config, offline=True, state_path=state_path)

    assert skipped.outcome is AcquisitionOutcome.UNCHANGED
    assert len(skipped_payloads) == 1  # only the probe was fetched -- the corpus IS empty here
    assert skipped.content_fingerprint != f"sha256:{empty_corpus_constant}", (
        "an UNCHANGED acquisition must never report the constant an empty corpus hashes to"
    )
    assert not skipped.acquisition_id.endswith(empty_corpus_constant[:8]), (
        "acquisition_id is derived from the fingerprint -- the empty-corpus constant must never "
        "surface there either"
    )
    assert skipped.content_fingerprint == seeded.content_fingerprint, (
        "the decision this fix makes: an UNCHANGED acquisition carries the PREVIOUS "
        "acquisition's own corpus fingerprint forward, because that IS what 'unchanged' means"
    )


# -- R05-fix2 item 3 -- the probe exclusion must hold under --fixtures too ----------------------
#
# The previous round's both-directions receipt (above, `test_changing_only_the_probe_does_not_
# move_the_fingerprint_or_acquisition_id` / `test_changing_a_real_export_file_still_moves_the_
# fingerprint`) only ever exercises `acquire_wahapedia`'s LOCAL-DIRECTORY path -- `_config`
# points `WGC_DETAIL_SOURCE_URL` at a directory, never `--fixtures`. `_corpus_payloads` matched
# the exact string `"Last_update.csv"`; the fixture adapter (`load_fixture_payloads`) names every
# payload by `Path.stem`, so its probe is named `"Last_update"` -- a name `_corpus_payloads`
# never matched, and `acquire_from_fixtures` never applied any exclusion at all before this
# rung's fix. Under `--fixtures`, the probe WAS corpus, in every `fixtures/detection/*` set. That
# is precisely what the previous round's own commit message claimed `--fixtures` made
# structurally impossible.


def _write_fixture_export(
    directory: Path, *, last_update: str, abilities: str = _PLACEHOLDER
) -> None:
    """A synthetic `--fixtures` set carrying the detail source's own export files, the way
    `load_fixture_payloads` reads them: one file per table, under `wahapedia/`, read by `*.csv`
    glob rather than `EXPORT_FILES`'s exact name list."""
    wahapedia_dir = directory / "wahapedia"
    wahapedia_dir.mkdir(parents=True, exist_ok=True)
    for name in EXPORT_FILES:
        text = last_update if name == LAST_UPDATE_FILE else _PLACEHOLDER
        if name == "Abilities.csv":
            text = abilities
        (wahapedia_dir / name).write_text(text, encoding="utf-8-sig")


def test_changing_only_the_probe_does_not_move_the_fingerprint_under_fixtures(
    tmp_path: Path,
) -> None:
    """Direction 1, through `--fixtures`: the probe alone moves. Nothing that matters may move
    with it. Red against the code this rung inherited -- `acquire_from_fixtures` fingerprinted
    every loaded payload unconditionally, so this assertion failed before the fix."""
    set_a = tmp_path / "set-a"
    _write_fixture_export(set_a, last_update="2026-08-01T00:00:00Z")
    set_b = tmp_path / "set-b"
    _write_fixture_export(set_b, last_update="2026-08-08T00:00:00Z")  # only the probe differs

    same_moment = datetime(2026, 8, 9, tzinfo=UTC)
    acquisition_a, _ = acquire_wahapedia(_config(""), fixtures_dir=set_a, retrieved_at=same_moment)
    acquisition_b, _ = acquire_wahapedia(_config(""), fixtures_dir=set_b, retrieved_at=same_moment)

    assert acquisition_a.content_fingerprint == acquisition_b.content_fingerprint, (
        "Last_update.csv is a probe, not corpus content, under --fixtures exactly as it is on "
        "the live path -- its own text moving must never move the content fingerprint"
    )
    assert acquisition_a.acquisition_id == acquisition_b.acquisition_id, (
        "acquisition_id is derived from the fingerprint -- it must not move either"
    )


def test_changing_a_real_export_file_still_moves_the_fingerprint_under_fixtures(
    tmp_path: Path,
) -> None:
    """Direction 2, through `--fixtures`: the complementary half -- fixing direction 1 must not
    numb the fingerprint to an actual rules change reaching it via `--fixtures`."""
    set_a = tmp_path / "set-a"
    _write_fixture_export(
        set_a, last_update="2026-08-01T00:00:00Z", abilities="id|name|\n1|Bolter|\n"
    )
    set_b = tmp_path / "set-b"
    _write_fixture_export(
        set_b, last_update="2026-08-01T00:00:00Z", abilities="id|name|\n1|Las Cannon|\n"
    )

    acquisition_a, _ = acquire_wahapedia(_config(""), fixtures_dir=set_a)
    acquisition_b, _ = acquire_wahapedia(_config(""), fixtures_dir=set_b)

    assert acquisition_a.content_fingerprint != acquisition_b.content_fingerprint, (
        "a genuine corpus change reaching --fixtures must still move the fingerprint"
    )


# -- R05-fix2 item 4 -- coverage and fingerprint must describe the same set ---------------------


def test_the_coverage_and_fingerprint_counts_agree_on_a_full_fetch(tmp_path: Path) -> None:
    """The live path: `csv_files` counts every file this run touched (the probe included), and
    the new `corpus_files` names what the fingerprint actually covers -- the probe is the +1
    between them, rather than the two disagreeing under one shared name."""
    directory = tmp_path / "export"
    _write_export(directory, last_update="2026-08-01T00:00:00Z")

    acquisition, payloads = acquire_wahapedia(_config(str(directory)), offline=True)

    assert acquisition.coverage["csv_files"] == len(payloads) == len(EXPORT_FILES)
    assert acquisition.coverage["corpus_files"] == len(EXPORT_FILES) - 1


def test_the_coverage_and_fingerprint_counts_agree_under_fixtures(tmp_path: Path) -> None:
    """The same agreement, through `--fixtures`."""
    fixtures_dir = tmp_path / "set"
    _write_fixture_export(fixtures_dir, last_update="2026-08-01T00:00:00Z")

    acquisition, payloads = acquire_wahapedia(_config(""), fixtures_dir=fixtures_dir)

    assert acquisition.coverage["csv_files"] == len(payloads) == len(EXPORT_FILES)
    assert acquisition.coverage["corpus_files"] == len(EXPORT_FILES) - 1
