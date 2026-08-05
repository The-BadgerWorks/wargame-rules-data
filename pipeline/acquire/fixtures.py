# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the fixture source adapter
# (task T037): --fixtures <dir> sources both upstreams from a synthetic tree with no network,
# producing the same SourceAcquisition records as the live path so there is no CI-only code
# path (contracts/pipeline-run-interface.md §1).
"""The fixture source adapter.

``--fixtures <dir>`` sources both upstreams from a synthetic tree. The point is not
convenience: it is that **the same code runs in CI and on a laptop**, so a curator can
reproduce any run and any failure locally (contract §1). This adapter therefore produces the
same :class:`~pipeline.models.source.SourceAcquisition` records the live path does — same
fields, same fingerprinting, same coverage counts — and the stages downstream cannot tell which
adapter they are reading from.

Layout (``fixtures/README.md``)::

    fixtures/<set>/mfm/<slug>.html
    fixtures/<set>/wahapedia/<Name>.csv        # detail source, csv mode
    fixtures/<set>/wahapedia-html/<slug>.html  # detail source, html mode (004 T072)

A set may carry both detail shapes, describing the *same* invented units. Where it does, a test
can build it twice and compare — which is how "every stage below ``acquire`` is mode-blind" is
proven rather than asserted.

Fixtures are **synthetic** — hand-authored structures with invented faction names, invented unit
names, and invented placeholder prose. Capturing a real page or a real CSV export as a golden
file is prohibited, not merely discouraged (FR-010, FR-013, research D10).
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from pipeline.acquire.http import AcquisitionError
from pipeline.build.canonical_json import dumps_bundle
from pipeline.config import PipelineConfig
from pipeline.exit_codes import ExitCode
from pipeline.models.source import AcquisitionOutcome, SourceAcquisition, SourceKey


@dataclass(frozen=True, slots=True)
class FixtureLayout:
    """Where one source's documents live in a fixture set, and how they are read."""

    subdirectory: str
    glob: str
    coverage_key: str
    encoding: str


#: The default layout per source, matching the documented naming convention.
#:
#: The detail source's CSVs are UTF-8 **with BOM** (research §0.1); ``utf-8-sig`` strips it, so
#: a fixture may carry a BOM exactly as the real export does without every parser needing to
#: know.
_LAYOUT: Final[dict[SourceKey, FixtureLayout]] = {
    SourceKey.MFM: FixtureLayout("mfm", "*.html", "faction_pages", "utf-8"),
    SourceKey.WAHAPEDIA: FixtureLayout("wahapedia", "*.csv", "csv_files", "utf-8-sig"),
}

#: The detail source read in ``html`` mode (`004` T072): the same source key — the acquisition
#: record must not say which mode produced it, or nothing below ``acquire`` would be mode-blind —
#: read from its own sub-directory, so one fixture set can carry the *same* invented units in
#: both source shapes and the grammars can be proven mode-blind against them (research D1d).
HTML_DETAIL_LAYOUT: Final = FixtureLayout("wahapedia-html", "*.html", "faction_pages", "utf-8")


class FixtureSetError(AcquisitionError):
    """A missing or empty fixture set — an invocation error, not a source failure."""

    finding_code = "SRC-UNREACHABLE"
    exit_code = ExitCode.CONFIG_ERROR


@dataclass(frozen=True, slots=True)
class FixturePayload:
    """One acquired document: its name and its text, exactly as the live path would hold it."""

    name: str
    """The faction slug (points source) or the file name (detail source)."""

    text: str


def fixture_source_dir(
    fixtures_dir: Path, source_key: SourceKey, *, layout: FixtureLayout | None = None
) -> Path:
    """The per-source sub-directory of a fixture set."""
    return fixtures_dir / (layout or _LAYOUT[source_key]).subdirectory


def load_fixture_payloads(
    fixtures_dir: Path, source_key: SourceKey, *, layout: FixtureLayout | None = None
) -> list[FixturePayload]:
    """Read every document of one source from a fixture set, sorted by name.

    Sorted because acquisition order must not affect the fingerprint or anything downstream —
    nothing in this pipeline is matched by document order (research D4a).
    """
    resolved = layout or _LAYOUT[source_key]
    directory = fixture_source_dir(fixtures_dir, source_key, layout=resolved)
    if not directory.is_dir():
        raise FixtureSetError(
            f"fixture set has no {resolved.subdirectory}/ directory for the "
            f"{source_key.value} source: {directory}"
        )

    paths = sorted(directory.glob(resolved.glob))
    if not paths:
        raise FixtureSetError(f"fixture set holds no {resolved.glob} files: {directory}")

    return [
        FixturePayload(name=p.stem, text=p.read_text(encoding=resolved.encoding)) for p in paths
    ]


def content_fingerprint(payloads: Sequence[FixturePayload]) -> str:
    """A sha256 over the canonicalised acquired set.

    Computed over a canonical map of ``name -> sha256(text)`` rather than over the concatenated
    text, so the fingerprint is order-independent and carries no source material itself — the
    same one-way-digest argument that lets ``state/detection-digest.json`` be committed at all
    (FR-010).
    """
    per_document = {
        payload.name: hashlib.sha256(payload.text.encode("utf-8")).hexdigest()
        for payload in payloads
    }
    canonical = dumps_bundle(per_document).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def acquire_from_fixtures(
    fixtures_dir: Path,
    source_key: SourceKey,
    config: PipelineConfig,
    *,
    retrieved_at: datetime | None = None,
    layout: FixtureLayout | None = None,
) -> tuple[SourceAcquisition, list[FixturePayload]]:
    """Acquire one source from a fixture set, with no network access whatsoever.

    Returns the acquisition record and its payloads, exactly as the live adapters do.
    """
    resolved = layout or _LAYOUT[source_key]
    payloads = load_fixture_payloads(fixtures_dir, source_key, layout=resolved)
    fingerprint = content_fingerprint(payloads)
    moment = (retrieved_at or datetime.now(UTC)).astimezone(UTC)
    stamp = moment.strftime("%Y%m%dT%H%M%SZ")

    declared_edition = config.mfm_edition if source_key is SourceKey.MFM else config.detail_edition
    coverage_key = resolved.coverage_key

    acquisition = SourceAcquisition(
        acquisition_id=f"{source_key.value}-{stamp}-{fingerprint[:8]}",
        source_key=source_key,
        source_base_url=f"fixtures://{fixtures_dir.name}",
        declared_edition_code=declared_edition,
        retrieved_at=moment.isoformat().replace("+00:00", "Z"),
        content_fingerprint=f"sha256:{fingerprint}",
        coverage={coverage_key: len(payloads)},
        request_count=0,
        request_interval_ms=0,
        outcome=AcquisitionOutcome.OK,
    )
    return acquisition, payloads
