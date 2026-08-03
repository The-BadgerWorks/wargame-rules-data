# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented points-source acquisition (task
# T055): sitemap-driven faction enumeration, one polite fetch each, and a SourceAcquisition
# recording source, declared edition, retrieval time, fingerprint, coverage, request count and
# interval, with an outcome that fails the run rather than degrading (FR-003, FR-004, FR-007).
"""Acquire the points source: every faction page the publisher lists, once each.

The faction list is **read from the publisher's own sitemap**, not from a list we maintain. That
is what makes FR-004 — "the faction set is whatever the publisher currently publishes" —
true rather than aspirational, and it is what lets a faction appearing or disappearing surface
as a finding instead of as silence.

The acquisition record is the provenance root: every published value traces back to one of
these (FR-003). It carries the politeness evidence too — how many requests were made and at
what interval — because "we were polite" is a claim the pipeline should be able to substantiate
rather than assert.

**A partial sweep is a failed sweep.** If a page is unreachable or the host refuses, the run
stops with a named diagnostic (FR-007, FR-008). Degrading to "we got 28 of 30 factions" is how
a coverage collapse becomes a published snapshot missing two armies.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Final
from urllib.parse import urlparse

from pipeline.acquire.fixtures import FixturePayload, acquire_from_fixtures, content_fingerprint
from pipeline.acquire.http import AcquisitionError, PoliteClient, SourceUnreachable
from pipeline.config import PipelineConfig
from pipeline.models.source import AcquisitionOutcome, SourceAcquisition, SourceKey

#: ``<loc>`` entries in a sitemap. A three-line XML document does not need an XML parser, and a
#: regex cannot be talked into resolving an external entity.
_SITEMAP_LOC: Final = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>", re.IGNORECASE)

SITEMAP_PATH: Final = "sitemap.xml"


def _slug_of(url: str, base_path: str) -> str | None:
    """The faction slug a sitemap entry names, or ``None`` when it is not a faction page.

    The sitemap lists **locale-neutral** URLs at the host root — ``/necrons``, not
    ``/en/necrons`` — and carries the locales as ``xhtml:link`` alternates. The configured base
    URL names the locale we request, so a slug is accepted one segment below either the base
    path or the host root, and the request is then made against the base.

    Anything deeper, and the index itself, is not a faction page and is skipped rather than
    guessed at.
    """
    path = urlparse(url).path.rstrip("/")
    for base in (base_path.rstrip("/"), ""):
        prefix = f"{base}/"
        if not path.startswith(prefix):
            continue
        remainder = path[len(prefix) :]
        if remainder and "/" not in remainder:
            return remainder
    return None


def enumerate_faction_slugs(client: PoliteClient, base_url: str) -> list[str]:
    """The faction slugs the publisher currently lists, sorted and de-duplicated.

    Sorted because acquisition order must not reach anything downstream: nothing in this
    pipeline is paired by document order (research D4a), and a stable order keeps the content
    fingerprint stable too.
    """
    parsed = urlparse(base_url)
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/{SITEMAP_PATH}"
    response = client.get(sitemap_url)
    if response.status_code != 200:
        raise SourceUnreachable(
            f"the points source's sitemap responded {response.status_code}; the faction list "
            "cannot be enumerated and the run stops rather than guessing at it (FR-004)"
        )
    slugs = {
        slug
        for url in _SITEMAP_LOC.findall(response.text)
        if (slug := _slug_of(url, parsed.path)) is not None
    }
    if not slugs:
        raise SourceUnreachable(
            "the points source's sitemap listed no faction page under the configured base URL; "
            "either the base URL is wrong or the site's layout changed (FR-004, FR-008)"
        )
    return sorted(slugs)


def acquire_mfm(
    config: PipelineConfig,
    *,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    client: PoliteClient | None = None,
    retrieved_at: datetime | None = None,
) -> tuple[SourceAcquisition, list[FixturePayload]]:
    """Acquire every points-source faction page.

    With ``fixtures_dir`` the synthetic tree is the source and no socket is opened; the records
    produced are the same either way, so there is no CI-only code path (contract §1).
    """
    if fixtures_dir is not None:
        return acquire_from_fixtures(fixtures_dir, SourceKey.MFM, config, retrieved_at=retrieved_at)

    owned = client is None
    active = client or PoliteClient(config, offline=offline)
    base = config.mfm_base_url.rstrip("/")
    try:
        slugs = enumerate_faction_slugs(active, base)
        payloads: list[FixturePayload] = []
        for slug in slugs:
            response = active.get(f"{base}/{slug}")
            if response.status_code != 200:
                raise SourceUnreachable(
                    f"the points source responded {response.status_code} for faction page "
                    f"{slug!r}; a partial sweep is a failed sweep (FR-008)"
                )
            payloads.append(FixturePayload(name=slug, text=response.text))
        request_count = active.request_count
    except AcquisitionError:
        # The politeness layer already carries the finding code and the exit code; re-raising
        # unchanged is what keeps the diagnostic the operator sees identical to the contract's.
        raise
    finally:
        if owned:
            active.close()

    moment = (retrieved_at or datetime.now(UTC)).astimezone(UTC)
    fingerprint = content_fingerprint(payloads)
    acquisition = SourceAcquisition(
        acquisition_id=f"mfm-{moment.strftime('%Y%m%dT%H%M%SZ')}-{fingerprint[:8]}",
        source_key=SourceKey.MFM,
        source_base_url=base,
        declared_edition_code=config.mfm_edition,
        retrieved_at=moment.isoformat().replace("+00:00", "Z"),
        content_fingerprint=f"sha256:{fingerprint}",
        coverage={"faction_pages": len(payloads)},
        request_count=request_count,
        request_interval_ms=config.request_interval_ms,
        outcome=AcquisitionOutcome.OK,
    )
    return acquisition, payloads
