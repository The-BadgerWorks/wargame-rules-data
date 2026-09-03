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
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added the export-timestamp short-circuit
# (009 rung R05, T090/T091/T092/T093, FR-030/FR-031/FR-032): `Last_update.csv` joins
# `EXPORT_FILES`, is fetched/read on its own ahead of the rest, and its one-way digest is
# compared against `state/wahapedia-export-digest.json`. The short-circuit is opt-in via the new
# `state_path` parameter -- `None` (every existing caller, including `run_build` through
# `acquire_detail`) is a total no-op, byte-for-byte the prior behaviour, which is what keeps this
# addition from ever silently handing a live build a partial export. A future rung's own job,
# flagged as unresolved by `tasks.md`'s own Phase 7 note, is deciding which caller opts in and
# how a skip composes with a full build; this rung delivers the mechanism and proves it correct
# in isolation, never wires it into `run_build`.
"""Acquire the datasheet-detail source: the CSV export, into ``work/``.

Three things are worth stating plainly.

**The export lands in `work/` and nowhere else.** `work/` is gitignored, emptied at the start of
every command that writes to it and again in a `finally` (FR-010). Nothing here writes outside
it, and the records handed downstream are the parsed ones, not the files.

**The declared edition is configuration, not inference** (FR-005). The export is 10th Edition
today and the points source is 11th, which is why hybrid pairing is the normal case at launch
rather than an edge case (research §0.1). When the export moves to 11th, the adoption is a
variable change — and no published snapshot is altered or invalidated by it (FR-061). Sniffing
the edition out of the data would make that a code change and, worse, would make it silent.

**The publisher's own change marker is a convenience, never evidence** (FR-030). ``Last_update
.csv`` is fetched/read like any other export file — `_read_local`/`_fetch_remote`'s all-or-nothing
guarantee covers it exactly as it covers every other table (FR-032) — and when ``state_path`` is
given, its one-way digest is compared against the last recorded one *before* the rest of the
export is retrieved. A match short-circuits the remaining fetch and raises
``SRC-EXPORT-UNCHANGED``; a mismatch (or no prior state) fetches everything and the existing
:func:`~pipeline.acquire.fixtures.content_fingerprint` — computed, as always, over whatever was
actually retrieved — is what a caller must trust, never the digest comparison alone. The
short-circuit sits in front of that fingerprint; nothing here lets it sit over it.
"""

from __future__ import annotations

import hashlib
import json
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
from pipeline.build.canonical_json import write_tree_file
from pipeline.config import PipelineConfig
from pipeline.models.findings import Finding
from pipeline.models.source import AcquisitionOutcome, SourceAcquisition, SourceKey
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
#: the newest addition: read by nothing downstream (`plan.md` finding 9 — greenfield), it carries
#: only the publisher's own whole-export change marker and exists here purely so the short-circuit
#: below is bound by the same all-or-nothing fetch guarantee (FR-032) as every other table.
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

#: The one file the short-circuit probes ahead of the rest (T090). A module-level name rather
#: than a literal repeated at each call site, so the "fetched first, on its own" contract is one
#: fact instead of several strings that could drift apart.
LAST_UPDATE_FILE: Final = "Last_update.csv"

#: ``state/``'s new file for this rung (T090, state/README.md's one-way-digest-only rule). Holds
#: exactly one field, ``digest`` — sha256 hex over ``Last_update.csv``'s own text, never the
#: text itself. Seeded empty (``{}``): no prior run has ever reached the short-circuit.
EXPORT_DIGEST_STATE_RELATIVE_PATH: Final = "state/wahapedia-export-digest.json"


def _one_way_export_digest(text: str) -> str:
    """sha256 hex over ``Last_update.csv``'s text — never the text itself.

    ``state/README.md`` permits state files to hold one-way digests and hashes only; a raw
    publisher timestamp is retained publisher data, a Tier 1 defect in this project regardless of
    where it turns up. A digest compares for equality exactly as well as the timestamp does,
    which is the only operation a short-circuit needs (``research.md``, "Explicitly not research
    questions").
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_export_digest(path: Path) -> str | None:
    """The digest the last run that reached ``path`` recorded, or ``None`` (no prior run, or the
    seeded-empty state)."""
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    digest = raw.get("digest")
    return str(digest) if digest else None


def _save_export_digest(path: Path, digest: str) -> None:
    """Persist ``digest`` through the same canonical-JSON writer every other state file uses."""
    write_tree_file(path, {"digest": digest})


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


def _read_local(directory: Path, names: Sequence[str] = EXPORT_FILES) -> list[FixturePayload]:
    """Read ``names`` from ``directory``, in order, failing whole on the first miss (FR-032).

    ``names`` defaults to the full :data:`EXPORT_FILES` list — every existing call keeps its
    exact prior behaviour — but the short-circuit calls this twice, once for
    :data:`LAST_UPDATE_FILE` alone and once for the rest, so it can decide between the two reads
    without weakening the all-or-nothing guarantee either read makes on its own.
    """
    if not directory.is_dir():
        raise SourceUnreachable(
            f"the detail source's export directory does not exist: {directory} "
            "(WGC_DETAIL_SOURCE_URL)"
        )
    payloads: list[FixturePayload] = []
    for name in names:
        path = directory / name
        if not path.is_file():
            raise SourceUnreachable(
                f"the detail source's export is missing {name}; a partial export is a failed "
                "acquisition rather than a smaller snapshot (FR-008)"
            )
        payloads.append(FixturePayload(name=name, text=path.read_text(encoding="utf-8-sig")))
    return payloads


def _fetch_remote(
    client: PoliteClient, base: str, names: Sequence[str] = EXPORT_FILES
) -> list[FixturePayload]:
    """Fetch ``names`` from ``base``, in order, failing whole on the first miss (FR-032).

    Same ``names`` parameter and the same reason as :func:`_read_local`'s.
    """
    payloads: list[FixturePayload] = []
    for name in names:
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


#: Every table but the change marker itself — what the short-circuit still has to fetch when it
#: does not skip. Computed once at import time rather than filtered per call.
_REMAINING_EXPORT_FILES: Final[tuple[str, ...]] = tuple(
    name for name in EXPORT_FILES if name != LAST_UPDATE_FILE
)


def acquire_wahapedia(
    config: PipelineConfig,
    *,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    client: PoliteClient | None = None,
    retrieved_at: datetime | None = None,
    workspace: Path | None = None,
    carried_forward_slugs: frozenset[str] = frozenset(),
    state_path: Path | None = None,
) -> tuple[SourceAcquisition, list[FixturePayload]]:
    """Acquire the detail-source export.

    When ``workspace`` is given the retrieved files are written into it — that is ``work/``, and
    it is the only place they are ever written.

    ``carried_forward_slugs`` is accepted and unused, on the same terms
    :func:`pipeline.acquire.detail_source.read_export_payloads` already accepts and ignores
    ``edition_code``: the signature is shared with the html arm so a caller never learns which
    mode ran (008 FR-024). The bulk export has no per-faction page to fail partway through — it
    is one file or none — so there is nothing here for a carry-forward declaration to apply to.

    ``state_path`` (009 rung R05, T090) is the export-timestamp short-circuit's own opt-in
    switch, pointed at :data:`EXPORT_DIGEST_STATE_RELATIVE_PATH`. **``None`` — the default, and
    every call this rung leaves unchanged, including every call `run_build` makes — is a total
    no-op**: :data:`LAST_UPDATE_FILE` is still fetched (it is simply one more name in
    :data:`EXPORT_FILES` now), but nothing is ever skipped and the fingerprint is computed over
    the complete export exactly as before this rung. When a caller opts in by passing a real
    path: :data:`LAST_UPDATE_FILE` is read first, on its own; if its digest matches the digest
    :func:`_load_export_digest` reads back from ``state_path``, the remaining
    :data:`_REMAINING_EXPORT_FILES` are never requested, ``outcome`` is
    :attr:`~pipeline.models.source.AcquisitionOutcome.UNCHANGED`, and the returned ``findings``
    carry ``SRC-EXPORT-UNCHANGED`` (FR-031) — otherwise every file is fetched exactly as it always
    was, and :func:`~pipeline.acquire.fixtures.content_fingerprint` runs over that complete,
    freshly-fetched set. Either way ``state_path`` (when given) is rewritten with the fresh
    digest before returning, so the *next* call is the one that can skip.

    A fixture run (``fixtures_dir``) never reaches any of this — :func:`acquire_from_fixtures`
    returns before ``state_path`` is even inspected, exactly as it always has.
    """
    del carried_forward_slugs
    if fixtures_dir is not None:
        return acquire_from_fixtures(
            fixtures_dir, SourceKey.WAHAPEDIA, config, retrieved_at=retrieved_at
        )

    # Refused here rather than interpreted: an empty location is a relative path, and a relative
    # path is the working directory. See `PipelineConfig.require_detail_source`.
    location = config.require_detail_source()
    directory = _local_directory(location)
    request_count = 0
    outcome = AcquisitionOutcome.OK
    findings: tuple[Finding, ...] = ()
    coverage: dict[str, int]

    prior_digest = _load_export_digest(state_path) if state_path is not None else None
    owned = client is None
    active: PoliteClient | None = None
    try:
        if directory is not None:
            last_update = _read_local(directory, (LAST_UPDATE_FILE,))[0]
        else:
            active = client or PoliteClient(config, offline=offline)
            last_update = _fetch_remote(active, location, (LAST_UPDATE_FILE,))[0]
            request_count = active.request_count

        fresh_digest = _one_way_export_digest(last_update.text)
        # T088/FR-030's central guarantee lives in this one condition: the short-circuit fires
        # ONLY when a caller opted in (`state_path` given) AND a prior digest exists AND it
        # matches. Every other combination — no `state_path`, first run, or a moved digest —
        # falls through to the full fetch below, where the content fingerprint is computed over
        # real, current bytes exactly as it always has been. The digest is never asked to stand
        # in for that fingerprint; it only ever decides whether the fingerprint's own inputs are
        # worth re-requesting.
        if state_path is not None and prior_digest is not None and fresh_digest == prior_digest:
            payloads = [last_update]
            outcome = AcquisitionOutcome.UNCHANGED
            findings = (build_finding("SRC-EXPORT-UNCHANGED", detail={"table": LAST_UPDATE_FILE}),)
        else:
            if directory is not None:
                rest = _read_local(directory, _REMAINING_EXPORT_FILES)
            else:
                assert active is not None  # narrows for mypy; set above whenever directory is None
                rest = _fetch_remote(active, location, _REMAINING_EXPORT_FILES)
                request_count = active.request_count
            payloads = [last_update, *rest]

        if state_path is not None:
            _save_export_digest(state_path, fresh_digest)
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
    fingerprint = content_fingerprint(payloads)
    coverage = {"csv_files": len(payloads)}
    if outcome is AcquisitionOutcome.UNCHANGED:
        # T093: the surface reduction the short-circuit buys, recorded rather than merely
        # implied by a smaller `csv_files` count -- a curator sees both numbers without having
        # to know EXPORT_FILES's own length.
        coverage["csv_files_total"] = len(EXPORT_FILES)

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
        outcome=outcome,
        findings=findings,
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
