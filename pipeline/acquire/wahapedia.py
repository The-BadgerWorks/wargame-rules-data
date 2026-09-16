# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented detail-source acquisition (task
# T056): retrieval of the CSV export into work/, BOM-aware, with the same SourceAcquisition
# recording and declared_edition_code from WGC_DETAIL_EDITION (FR-003, FR-005).
# AI-Assisted: Claude Code (model: claude-opus-5) - Refuse an unset WGC_DETAIL_SOURCE_URL before
# it is interpreted as a relative path (004 T075 follow-up): an empty location resolved to the
# working directory and reported the first absent export file as an FR-008 partial export.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added check_table_coverage
# (SRC-TABLE-MISSING, 009 tasks T027/T028, FR-018) and Detachment_abilities.csv to EXPORT_FILES
# (FR-019 parity restoration -- curate/assemble.py already consumed it when html mode supplied
# it; this closes the csv-mode gap the same file's own comment used to explain away).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix (gate on PR #30, item 1):
# `Last_update.csv` is excluded from `content_fingerprint`/`acquisition_id` by
# `_corpus_payloads` -- the one place that decides what the corpus is, so a republish with no
# rules change does not move the authoritative signal.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix2 item 3 (gate on PR #30):
# `_corpus_payloads`'s probe exclusion now matches by `Path(name).stem` rather than the exact
# string `"Last_update.csv"`, so it recognises the fixture adapter's own spelling (`"Last_update"`,
# no suffix) too -- plumbed into `acquire_from_fixtures` via its new `corpus_filter` parameter
# (`pipeline/acquire/fixtures.py`), the one place that adapter now excludes anything. Before this
# fix, `acquire_from_fixtures` fingerprinted every loaded payload unconditionally, so under
# `--fixtures` the probe WAS corpus in every `fixtures/detection/*` set, even though the live path
# already excluded it.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix2 item 4 (gate on PR #30):
# `coverage["csv_files"]` counted every file a run touched, probe included, while the content
# fingerprint excluded it -- the two figures described different sets under the same run.
# `csv_files` keeps its original meaning; a new `coverage["corpus_files"]` names what the
# fingerprint actually covers, so a reader cannot mistake one for the other.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R5: dropped the accepted-and-unused
# `carried_forward_slugs` parameter along with the per-faction carry-forward mechanism. The bulk
# export answers whole or not at all, so no per-faction declaration has anything here to apply to.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R9 task 1: deleted the export-timestamp
# short-circuit outright (Owner ruling 2026-09-15). `ExportDigestState` and its load/save/derive
# helpers, `ExportStateCorrupt`, `_one_way_export_digest`, `EXPORT_DIGEST_STATE_RELATIVE_PATH`,
# the `state_path` opt-in parameter, the skip branch and the `SRC-EXPORT-UNCHANGED` finding are
# all gone, along with the tracked state file they read. The mechanism had no caller from the day
# it landed and could not acquire one: a build cannot consume a skipped fetch when the corpus is
# never retained, so the saving it offered was never available to the one stage that reads the
# detail source. `Last_update.csv` stays in `EXPORT_FILES` and stays out of the corpus
# (`_corpus_payloads`), which is independent of the skip and is what keeps a bare regeneration
# timestamp from moving the content fingerprint. Guarded by
# `tests/unit/test_no_export_short_circuit.py`, which replaces `test_state_path_inert.py`.
"""Acquire the datasheet-detail source: the CSV export, into ``work/``.

Three things are worth stating plainly.

**The export lands in `work/` and nowhere else.** `work/` is gitignored, emptied at the start of
every command that writes to it and again in a `finally` (FR-010), and the records handed
downstream are the parsed ones, not the files. This module writes nothing outside `work/` and
the caller's own ``workspace``.

**The declared edition is configuration, not inference** (FR-005). The export is 10th Edition
today and the points source is 11th, which is why hybrid pairing is the normal case at launch
rather than an edge case (research §0.1). When the export moves to 11th, the adoption is a
variable change — and no published snapshot is altered or invalidated by it (FR-061). Sniffing
the edition out of the data would make that a code change and, worse, would make it silent.

**The publisher's own change marker is never corpus** (FR-030). ``Last_update.csv`` is
fetched/read like any other export file — `_read_local`/`_fetch_remote`'s all-or-nothing
guarantee covers it exactly as it covers every other table (FR-032) — but it is excluded from
:func:`~pipeline.acquire.fixtures.content_fingerprint` by :func:`_corpus_payloads` (R05-fix item
1), so a republish that moves only the regeneration timestamp cannot move the fingerprint or the
``acquisition_id`` derived from it. The fingerprint is computed over whatever was actually
retrieved, every run, and is the only thing a caller trusts.

The short-circuit that once compared that marker's digest against a tracked state file was
deleted in 010 R9: it had no caller and could not acquire one, because nothing downstream can
consume a fetch that did not happen when the corpus is never retained.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Final
from urllib.parse import unquote, urlparse

from pipeline.acquire.fixtures import FixturePayload, acquire_from_fixtures, content_fingerprint
from pipeline.acquire.http import (
    AcquisitionError,
    PoliteClient,
    SourceUnreachable,
)
from pipeline.config import PipelineConfig
from pipeline.models.findings import Finding
from pipeline.models.source import SourceAcquisition, SourceKey
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.report.catalogue import build_finding
from pipeline.workspace import work_dir

#: The export files the pipeline reads. Listed rather than discovered, because a file appearing
#: or disappearing upstream should be a visible failure here rather than a quiet change in what
#: the snapshot was built from. Files carrying only rules text — stratagems — are absent by
#: design: they are read for structural facts only, and nothing in this feature needs one
#: (research D8). ``Detachment_abilities.csv`` (009 task T028, FR-019) is the one exception: it is
#: read for the STRUCTURAL fact of which rule names accompany a detachment, exactly as
#: ``Datasheets_abilities.csv`` already is for datasheets — an acquisition-list change restoring
#: parity with the html arm, explicitly not a coverage expansion (FR-024's no-expansion rule; see
#: `curate/assemble.py::_source_detachment_rules`, which already consumes this file when present
#: and previously only saw it under `html` mode). ``Last_update.csv`` (009 task T090, FR-030) is
#: read by nothing downstream: it carries only the publisher's own whole-export change marker.
#: It is listed here so the all-or-nothing fetch guarantee (FR-032) covers it like every other
#: table, and excluded from the corpus by :func:`_corpus_payloads` so it can never move the
#: content fingerprint.
EXPORT_FILES: Final[tuple[str, ...]] = (
    "Abilities.csv",
    "Datasheets.csv",
    "Datasheets_abilities.csv",
    "Datasheets_keywords.csv",
    "Datasheets_leader.csv",
    "Datasheets_models.csv",
    "Datasheets_models_cost.csv",
    "Datasheets_options.csv",
    "Datasheets_unit_composition.csv",
    "Datasheets_wargear.csv",
    "Detachment_abilities.csv",
    "Detachments.csv",
    "Enhancements.csv",
    "Factions.csv",
    "Last_update.csv",
    "Source.csv",
)

#: The export's own whole-export change marker (T090). A module-level name rather than a literal
#: repeated at each call site, so "which file is the change marker" is one fact instead of
#: several strings that could drift apart.
LAST_UPDATE_FILE: Final = "Last_update.csv"

#: :data:`LAST_UPDATE_FILE`'s own name, normalised to its stem. The live path names the probe's
#: payload ``"Last_update.csv"`` (`_read_local`/`_fetch_remote` keep the file's own name); the
#: fixture adapter names it ``"Last_update"`` (`load_fixture_payloads` uses ``Path.stem`` for
#: every payload). R05-fix2 item 3: comparing by stem is the ONE normalisation both spellings
#: resolve to, so there is exactly one place this decision is made rather than two that can
#: silently drift apart -- which is exactly what happened before this fix: `_corpus_payloads`
#: excluded the exact string ``"Last_update.csv"``, which the fixture adapter's payload never is,
#: so under ``--fixtures`` the probe was corpus in every `fixtures/detection/*` set.
_PROBE_STEM: Final = Path(LAST_UPDATE_FILE).stem


def _is_probe(payload: FixturePayload) -> bool:
    """Whether ``payload`` is the export's own change marker, regardless of which adapter
    read it."""
    return Path(payload.name).stem == _PROBE_STEM


#: The files that count as the export's own content — what may move the content fingerprint and
#: the acquisition_id derived from it. The **only** place that decision is made (R05-fix item 1;
#: made spelling-independent by R05-fix2 item 3): :data:`LAST_UPDATE_FILE` is fetched like any
#: other table (the all-or-nothing guarantee still covers it) but is never corpus, so a bare
#: regeneration timestamp can never masquerade as a rules change. A file added to
#: :data:`EXPORT_FILES` later is corpus by default and has to be excluded here deliberately, the
#: same way this one was -- exactly the property that was missing before this fix. Passed to
#: :func:`~pipeline.acquire.fixtures.acquire_from_fixtures` as its ``corpus_filter`` (R05-fix2
#: item 3) so the SAME function decides this under ``--fixtures`` too, rather than that module
#: reimplementing the exclusion by name.
def _corpus_payloads(payloads: Sequence[FixturePayload]) -> list[FixturePayload]:
    return [payload for payload in payloads if not _is_probe(payload)]


def _local_directory(location: str) -> Path | None:
    """The local directory ``location`` names, or ``None`` when it names an HTTP resource.

    A curator running against a locally held export should exercise the same code path as CI
    does against the hosted one — the alternative is a second acquisition path that only ever
    runs on a laptop, which is exactly what contract §1 rules out.
    """
    parsed = urlparse(location)
    if parsed.scheme == "file":
        return Path(unquote(parsed.netloc + parsed.path))
    if parsed.scheme in {"http", "https"}:
        return None
    return Path(location)


def _read_local(directory: Path) -> list[FixturePayload]:
    """Read :data:`EXPORT_FILES` from ``directory``, in order, failing whole on the first miss
    (FR-032). A partial export is a failed acquisition, never a smaller snapshot.

    010 R9: the ``names`` parameter is gone with the short-circuit, which was the only caller
    that ever passed anything but the default. One list, read whole, one guarantee.
    """
    if not directory.is_dir():
        raise SourceUnreachable(
            f"the detail source's export directory does not exist: {directory} "
            "(WGC_DETAIL_SOURCE_URL)"
        )
    payloads: list[FixturePayload] = []
    for name in EXPORT_FILES:
        path = directory / name
        if not path.is_file():
            raise SourceUnreachable(
                f"the detail source's export is missing {name}; a partial export is a failed "
                "acquisition rather than a smaller snapshot (FR-008)"
            )
        payloads.append(FixturePayload(name=name, text=path.read_text(encoding="utf-8-sig")))
    return payloads


def _fetch_remote(client: PoliteClient, base: str) -> list[FixturePayload]:
    """Fetch :data:`EXPORT_FILES` from ``base``, in order, failing whole on the first miss
    (FR-032). Same whole-list contract as :func:`_read_local`'s, and 010 R9 dropped its
    ``names`` parameter for the same reason."""
    payloads: list[FixturePayload] = []
    for name in EXPORT_FILES:
        response = client.get(f"{base.rstrip('/')}/{name}")
        if response.status_code != 200:
            raise SourceUnreachable(
                f"the detail source responded {response.status_code} for {name}; a partial "
                "export is a failed acquisition (FR-008)"
            )
        # The export is UTF-8 with a BOM; decoding it away here means no parser downstream has
        # to know that, and a fixture may carry a BOM exactly as the real file does.
        payloads.append(FixturePayload(name=name, text=response.content.decode("utf-8-sig")))
    return payloads


def acquire_wahapedia(
    config: PipelineConfig,
    *,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    client: PoliteClient | None = None,
    retrieved_at: datetime | None = None,
    workspace: Path | None = None,
) -> tuple[SourceAcquisition, list[FixturePayload]]:
    """Acquire the detail-source export.

    When ``workspace`` is given the retrieved files are written into it — that is ``work/``, and
    it is the only place they are ever written.

    Every file in :data:`EXPORT_FILES` is fetched, every run, whole or not at all (FR-032), and
    :func:`~pipeline.acquire.fixtures.content_fingerprint` runs over that complete set minus the
    change marker (:func:`_corpus_payloads`, R05-fix item 1). 010 R9 deleted the ``state_path``
    opt-in that once let a matching change-marker digest skip the rest of the fetch: it had no
    caller and could acquire none, because the corpus is never retained between runs, so no
    downstream stage can consume a fetch that did not happen.
    """
    if fixtures_dir is not None:
        # R05-fix2 item 3: `corpus_filter=_corpus_payloads` so the fixture adapter excludes the
        # change marker on the SAME predicate the live path below uses, rather than never
        # excluding it at all -- see `_corpus_payloads`'s own docstring.
        return acquire_from_fixtures(
            fixtures_dir,
            SourceKey.WAHAPEDIA,
            config,
            retrieved_at=retrieved_at,
            corpus_filter=_corpus_payloads,
        )

    # Refused here rather than interpreted: an empty location is a relative path, and a relative
    # path is the working directory. See `PipelineConfig.require_detail_source`.
    location = config.require_detail_source()
    directory = _local_directory(location)
    request_count = 0

    owned = client is None
    active: PoliteClient | None = None
    try:
        if directory is not None:
            payloads = _read_local(directory)
        else:
            active = client or PoliteClient(config, offline=offline)
            payloads = _fetch_remote(active, location)
            request_count = active.request_count
    except AcquisitionError:
        raise
    finally:
        if owned and active is not None:
            active.close()

    if workspace is not None:
        target = workspace / "wahapedia"
        target.mkdir(parents=True, exist_ok=True)
        for payload in payloads:
            (target / payload.name).write_text(payload.text, encoding="utf-8", newline="\n")

    moment = (retrieved_at or datetime.now(UTC)).astimezone(UTC)
    # R05-fix item 1: the change marker is fetched (above) but never counted as corpus -- see
    # _corpus_payloads's own docstring for why this is the one place that decision is made.
    corpus = _corpus_payloads(payloads)
    fingerprint = content_fingerprint(corpus)
    # R05-fix2 item 4: `csv_files` counts every file THIS RUN touched, change marker included,
    # and `corpus_files` names what the fingerprint actually covers, so a reader cannot mistake
    # one count for the other the way a single `csv_files` key invited.
    coverage = {"csv_files": len(payloads), "corpus_files": len(corpus)}

    acquisition = SourceAcquisition(
        acquisition_id=f"wahapedia-{moment.strftime('%Y%m%dT%H%M%SZ')}-{fingerprint[:8]}",
        source_key=SourceKey.WAHAPEDIA,
        source_base_url=location,
        declared_edition_code=config.detail_edition,
        retrieved_at=moment.isoformat().replace("+00:00", "Z"),
        content_fingerprint=f"sha256:{fingerprint}",
        coverage=coverage,
        request_count=request_count,
        request_interval_ms=config.request_interval_ms,
    )
    return acquisition, payloads


def default_workspace() -> Path:
    """The ``work/`` directory the export lands in when no other is given."""
    return work_dir()


def check_table_coverage(
    detail: Mapping[str, CsvReadResult], *, consumed_tables: Sequence[str]
) -> list[Finding]:
    """``SRC-TABLE-MISSING`` (009 FR-018, rule 3): a table the build consumes is absent or empty.

    Asserted against ``detail`` — the parsed reader output of an actual acquisition
    (:func:`pipeline.acquire.detail_source.read_detail`'s return shape) — never against a fixture
    directory listing. A file existing on disk (which ``_read_local``'s ``EXPORT_FILES`` sweep
    already guards, by raising :class:`~pipeline.acquire.http.SourceUnreachable`) proves nothing
    about whether the acquisition actually produced usable rows from it; this catches the case
    that check misses, a table present but genuinely empty.

    ``consumed_tables`` is deliberately a parameter rather than a hardcoded list: which tables
    the build actually indexes into varies by stage and by arm (``Detachment_abilities.csv`` is
    html-only until T028's own change; the derived equipment table is Phase 5's), so the caller
    states its own scope rather than this function guessing it.
    """
    return [
        build_finding("SRC-TABLE-MISSING", detail={"table": table})
        for table in consumed_tables
        if not (result := detail.get(table)) or not result.rows
    ]
