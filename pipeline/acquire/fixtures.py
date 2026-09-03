# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the fixture source adapter
# (task T037): --fixtures <dir> sources both upstreams from a synthetic tree with no network,
# producing the same SourceAcquisition records as the live path so there is no CI-only code
# path (contracts/pipeline-run-interface.md §1).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 rung R05-fix2 item 3: added
# `acquire_from_fixtures`'s `corpus_filter` parameter. Before this, the function fingerprinted
# every loaded payload unconditionally, so a source with its own non-corpus probe file --
# `pipeline.acquire.wahapedia`'s `Last_update.csv` is the only one today -- had that probe
# fingerprinted as corpus under `--fixtures`, in every `fixtures/detection/*` set, even though
# the live adapter already excluded it. A caller that has such a file passes the SAME predicate
# its live path uses; every other caller passes nothing and this is a total no-op.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 rung R05-fix2 item 4: added the
# `corpus_files` coverage figure alongside `coverage[coverage_key]` whenever `corpus_filter` is
# given, so a reader cannot mistake "every payload this run loaded" for "what the fingerprint
# actually covers" -- the same pairing `pipeline.acquire.wahapedia.acquire_wahapedia`'s own live
# path now reports (`csv_files` / `corpus_files`).
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
from collections.abc import Callable, Sequence
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
    corpus_filter: Callable[[Sequence[FixturePayload]], Sequence[FixturePayload]] | None = None,
) -> tuple[SourceAcquisition, list[FixturePayload]]:
    """Acquire one source from a fixture set, with no network access whatsoever.

    Returns the acquisition record and its payloads, exactly as the live adapters do.

    ``corpus_filter`` (009 rung R05-fix2 item 3): applied to the loaded payloads before the
    content fingerprint is computed, so a source whose live adapter excludes a non-corpus file of
    its own -- ``pipeline.acquire.wahapedia``'s ``Last_update.csv`` is the only one today --
    excludes it here too, on the exact predicate that adapter passes
    (:func:`pipeline.acquire.wahapedia._corpus_payloads`) rather than this module reimplementing
    the exclusion by name. ``None`` (every other caller) is a total no-op: every loaded payload is
    corpus, exactly as before this parameter existed. ``payloads`` — what is returned and what
    ``coverage[coverage_key]`` counts — is never filtered; only the fingerprint and the
    ``corpus_files`` figure below are.
    """
    resolved = layout or _LAYOUT[source_key]
    payloads = load_fixture_payloads(fixtures_dir, source_key, layout=resolved)
    corpus = list(corpus_filter(payloads)) if corpus_filter is not None else payloads
    fingerprint = content_fingerprint(corpus)
    moment = (retrieved_at or datetime.now(UTC)).astimezone(UTC)
    stamp = moment.strftime("%Y%m%dT%H%M%SZ")

    declared_edition = config.mfm_edition if source_key is SourceKey.MFM else config.detail_edition
    coverage_key = resolved.coverage_key
    coverage = {coverage_key: len(payloads)}
    if corpus_filter is not None:
        # R05-fix2 item 4: named apart from `coverage_key` rather than left to silently disagree
        # with what the fingerprint above covers -- the same pairing the live wahapedia path now
        # reports (`csv_files` / `corpus_files`).
        coverage["corpus_files"] = len(corpus)

    acquisition = SourceAcquisition(
        acquisition_id=f"{source_key.value}-{stamp}-{fingerprint[:8]}",
        source_key=source_key,
        source_base_url=f"fixtures://{fixtures_dir.name}",
        declared_edition_code=declared_edition,
        retrieved_at=moment.isoformat().replace("+00:00", "Z"),
        content_fingerprint=f"sha256:{fingerprint}",
        coverage=coverage,
        request_count=0,
        request_interval_ms=0,
        outcome=AcquisitionOutcome.OK,
    )
    return acquisition, payloads
