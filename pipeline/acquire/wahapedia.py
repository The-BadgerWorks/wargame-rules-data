# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented detail-source acquisition (task
# T056): retrieval of the CSV export into work/, BOM-aware, with the same SourceAcquisition
# recording and declared_edition_code from WGC_DETAIL_EDITION (FR-003, FR-005).
# AI-Assisted: Claude Code (model: claude-opus-5) - Refuse an unset WGC_DETAIL_SOURCE_URL before
# it is interpreted as a relative path (004 T075 follow-up): an empty location resolved to the
# working directory and reported the first absent export file as an FR-008 partial export.
"""Acquire the datasheet-detail source: the CSV export, into ``work/``.

Two things are worth stating plainly.

**The export lands in `work/` and nowhere else.** `work/` is gitignored, emptied at the start of
every command that writes to it and again in a `finally` (FR-010). Nothing here writes outside
it, and the records handed downstream are the parsed ones, not the files.

**The declared edition is configuration, not inference** (FR-005). The export is 10th Edition
today and the points source is 11th, which is why hybrid pairing is the normal case at launch
rather than an edge case (research §0.1). When the export moves to 11th, the adoption is a
variable change — and no published snapshot is altered or invalidated by it (FR-061). Sniffing
the edition out of the data would make that a code change and, worse, would make it silent.
"""

from __future__ import annotations

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
from pipeline.models.source import AcquisitionOutcome, SourceAcquisition, SourceKey
from pipeline.workspace import work_dir

#: The export files the pipeline reads. Listed rather than discovered, because a file appearing
#: or disappearing upstream should be a visible failure here rather than a quiet change in what
#: the snapshot was built from. Files carrying only rules text — stratagems, detachment
#: abilities — are absent by design: they are read for structural facts only, and nothing in
#: this feature needs one (research D8).
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
    "Detachments.csv",
    "Enhancements.csv",
    "Factions.csv",
    "Source.csv",
)


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
    """
    if fixtures_dir is not None:
        return acquire_from_fixtures(
            fixtures_dir, SourceKey.WAHAPEDIA, config, retrieved_at=retrieved_at
        )

    # Refused here rather than interpreted: an empty location is a relative path, and a relative
    # path is the working directory. See `PipelineConfig.require_detail_source`.
    location = config.require_detail_source()
    directory = _local_directory(location)
    request_count = 0

    if directory is not None:
        payloads = _read_local(directory)
    else:
        owned = client is None
        active = client or PoliteClient(config, offline=offline)
        try:
            payloads = _fetch_remote(active, location)
            request_count = active.request_count
        except AcquisitionError:
            raise
        finally:
            if owned:
                active.close()

    if workspace is not None:
        target = workspace / "wahapedia"
        target.mkdir(parents=True, exist_ok=True)
        for payload in payloads:
            (target / payload.name).write_text(payload.text, encoding="utf-8", newline="\n")

    moment = (retrieved_at or datetime.now(UTC)).astimezone(UTC)
    fingerprint = content_fingerprint(payloads)
    acquisition = SourceAcquisition(
        acquisition_id=f"wahapedia-{moment.strftime('%Y%m%dT%H%M%SZ')}-{fingerprint[:8]}",
        source_key=SourceKey.WAHAPEDIA,
        source_base_url=location,
        declared_edition_code=config.detail_edition,
        retrieved_at=moment.isoformat().replace("+00:00", "Z"),
        content_fingerprint=f"sha256:{fingerprint}",
        coverage={"csv_files": len(payloads)},
        request_count=request_count,
        request_interval_ms=config.request_interval_ms,
        outcome=AcquisitionOutcome.OK,
    )
    return acquisition, payloads


def default_workspace() -> Path:
    """The ``work/`` directory the export lands in when no other is given."""
    return work_dir()
