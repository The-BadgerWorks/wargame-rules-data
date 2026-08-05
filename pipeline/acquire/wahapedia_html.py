# AI-Assisted: Claude Code (model: claude-opus-5) - Stubbed the html-mode detail acquirer (004
# task T018), so the WGC_DETAIL_ACQUISITION_MODE dispatch has both of its targets and the mode
# selector can be proven mode-blind before the retrieval itself lands in 004 T072.
# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the retrieval (004 task T072):
# sitemap-driven faction-slug enumeration, one polite request per faction datacard page, the
# FR-004 deny-list guard ahead of every request, and a SourceAcquisition whose shape is the csv
# arm's exactly (FR-003, FR-004, research D1c-D1d).
"""Acquire the datasheet-detail source: the current-edition datacard pages.

One page per faction, and every datacard for that faction is on it — so the sweep is *tens* of
requests, not thousands, and its politeness budget is the same order as the existing points
sweep's (research D1c). The permitted tree is ``/wh40k11ed/``; the previous-edition and staging
trees are refused before a request is constructed by :mod:`pipeline.acquire.robots`, which is
reached through :class:`~pipeline.acquire.http.PoliteClient` and therefore cannot be bypassed
here.

**The faction list is read from the publisher's own sitemap**, exactly as the points sweep reads
its own — so "the faction set is whatever the publisher currently publishes" is true rather than
aspirational. What the sitemap lists under this tree is one URL *per datasheet*, not the
aggregate faction page:

.. code-block:: text

    https://wahapedia.ru/wh40k11ed/factions/<slug>/<Datasheet-Anchor>

so the slug set is the distinct second segment of those paths (verified live on 2026-08-05:
1 442 entries, 1 427 of them faction-scoped, 24 distinct slugs). The aggregate page each sweep
actually requests is ``factions/<slug>/datasheets.html``, which is the page the `004` T002 markup
spike analysed.

**A partial sweep is a failed sweep** (FR-008), on the same terms as the points sweep: a faction
page that does not answer stops the run with a named diagnostic rather than yielding a snapshot
quietly missing an army.

What the markup itself looks like is not this module's business — that is
:mod:`pipeline.parse.wahapedia_html_dom`, and the split is what keeps the acquisition record's
shape identical to the csv arm's so every stage below ``acquire`` stays mode-blind.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Final
from urllib.parse import urlparse

from pipeline.acquire.fixtures import (
    HTML_DETAIL_LAYOUT,
    FixturePayload,
    acquire_from_fixtures,
    content_fingerprint,
)
from pipeline.acquire.http import AcquisitionError, PoliteClient, SourceUnreachable
from pipeline.config import PipelineConfig
from pipeline.models.source import AcquisitionOutcome, SourceAcquisition, SourceKey
from pipeline.workspace import work_dir

#: ``<loc>`` entries in a sitemap. A sitemap does not need an XML parser, and a regex cannot be
#: talked into resolving an external entity — the same reasoning
#: :mod:`pipeline.acquire.mfm` records for its own sitemap read.
_SITEMAP_LOC: Final = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>", re.IGNORECASE)

#: The sitemap's own name under this tree, as ``robots.txt`` advertises it (research D1a, and
#: re-confirmed by the T002 spike). The capital ``M`` is the publisher's spelling.
SITEMAP_PATH: Final = "SiteMap.xml"

#: A faction-scoped path under the configured base: ``factions/<slug>/<anything>``.
_FACTION_PATH: Final = re.compile(r"/factions/([^/]+)/")

#: The aggregate page requested per faction. Every datacard for the faction is on it.
FACTION_PAGE: Final = "factions/{slug}/datasheets.html"

#: The sub-directory of ``work/`` the retrieved pages land in. Named apart from the csv arm's so
#: a run that switches mode cannot read a stale page from the other shape.
WORKSPACE_DIR: Final = "wahapedia-html"


def _slug_of(url: str, base_path: str) -> str | None:
    """The faction slug a sitemap entry names, or ``None`` when it is not faction-scoped.

    Accepted one segment below ``<base>/factions/`` or below ``/factions/`` at the host root, so
    a locale-neutral or differently-rooted sitemap entry resolves to the same slug the request
    is then made against the configured base for.
    """
    path = urlparse(url).path
    prefix = f"{base_path.rstrip('/')}/factions/"
    if not (path.startswith(prefix) or path.startswith("/factions/")):
        return None
    match = _FACTION_PATH.search(path)
    return match.group(1) if match else None


def enumerate_faction_slugs(client: PoliteClient, base_url: str) -> list[str]:
    """The faction slugs the publisher currently lists, sorted and de-duplicated.

    Sorted because acquisition order must not reach anything downstream: nothing here is paired
    by document order (research D4a), and a stable order keeps the content fingerprint stable.
    """
    base = base_url.rstrip("/")
    response = client.get(f"{base}/{SITEMAP_PATH}")
    if response.status_code != 200:
        raise SourceUnreachable(
            f"the detail source's sitemap responded {response.status_code}; the faction list "
            "cannot be enumerated and the run stops rather than guessing at it (FR-004)"
        )
    slugs = {
        slug
        for url in _SITEMAP_LOC.findall(response.text)
        if (slug := _slug_of(url, urlparse(base).path)) is not None
    }
    if not slugs:
        raise SourceUnreachable(
            "the detail source's sitemap listed no faction page under the configured base URL; "
            "either the base URL is wrong or the site's layout changed (FR-004, FR-008)"
        )
    return sorted(slugs)


def acquire_wahapedia_html(
    config: PipelineConfig,
    *,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    client: PoliteClient | None = None,
    retrieved_at: datetime | None = None,
    workspace: Path | None = None,
) -> tuple[SourceAcquisition, list[FixturePayload]]:
    """Acquire the current-edition datacard pages.

    The signature is deliberately identical to
    :func:`pipeline.acquire.wahapedia.acquire_wahapedia`'s, and so is the return shape: one
    :class:`~pipeline.models.source.SourceAcquisition` plus the retrieved payloads, under the
    **same** source key. That parity is what makes every stage below ``acquire`` mode-blind — it
    cannot tell which arm ran, because there is nothing in what it receives that says.

    Each payload's ``name`` is the faction slug and its ``text`` the retrieved page. With
    ``workspace`` given the pages are written into it — that is ``work/``, and it is the only
    place they are ever written (FR-010).
    """
    if fixtures_dir is not None:
        return acquire_from_fixtures(
            fixtures_dir,
            SourceKey.WAHAPEDIA,
            config,
            retrieved_at=retrieved_at,
            layout=HTML_DETAIL_LAYOUT,
        )

    base = config.detail_source_url.rstrip("/")
    owned = client is None
    active = client or PoliteClient(config, offline=offline)
    try:
        slugs = enumerate_faction_slugs(active, base)
        payloads: list[FixturePayload] = []
        for slug in slugs:
            response = active.get(f"{base}/{FACTION_PAGE.format(slug=slug)}")
            if response.status_code != 200:
                raise SourceUnreachable(
                    f"the detail source responded {response.status_code} for faction page "
                    f"{slug!r}; a partial sweep is a failed sweep (FR-008)"
                )
            payloads.append(FixturePayload(name=slug, text=response.text))
        request_count = active.request_count
    except AcquisitionError:
        # The politeness layer already carries the finding code and the exit code; re-raising
        # unchanged keeps the diagnostic the operator sees identical to the contract's.
        raise
    finally:
        if owned:
            active.close()

    if workspace is not None:
        target = workspace / WORKSPACE_DIR
        target.mkdir(parents=True, exist_ok=True)
        for payload in payloads:
            (target / f"{payload.name}.html").write_text(
                payload.text, encoding="utf-8", newline="\n"
            )

    moment = (retrieved_at or datetime.now(UTC)).astimezone(UTC)
    fingerprint = content_fingerprint(payloads)
    return (
        SourceAcquisition(
            acquisition_id=f"wahapedia-{moment.strftime('%Y%m%dT%H%M%SZ')}-{fingerprint[:8]}",
            source_key=SourceKey.WAHAPEDIA,
            source_base_url=base,
            declared_edition_code=config.detail_edition,
            retrieved_at=moment.isoformat().replace("+00:00", "Z"),
            content_fingerprint=f"sha256:{fingerprint}",
            coverage={"faction_pages": len(payloads)},
            request_count=request_count,
            request_interval_ms=config.request_interval_ms,
            outcome=AcquisitionOutcome.OK,
        ),
        payloads,
    )


def default_workspace() -> Path:
    """The ``work/`` directory the pages land in when no other is given."""
    return work_dir()
