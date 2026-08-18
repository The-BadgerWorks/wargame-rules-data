# AI-Assisted: Claude Code (model: claude-opus-5) - Stubbed the html-mode detail acquirer (004
# task T018), so the WGC_DETAIL_ACQUISITION_MODE dispatch has both of its targets and the mode
# selector can be proven mode-blind before the retrieval itself lands in 004 T072.
# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the retrieval (004 task T072):
# sitemap-driven faction-slug enumeration, one polite request per faction datacard page, the
# FR-004 deny-list guard ahead of every request, and a SourceAcquisition whose shape is the csv
# arm's exactly (FR-003, FR-004, research D1c-D1d).
# AI-Assisted: Claude Code (model: claude-opus-5) - Make the unset-source refusal read identically
# in both arms (004 T075 follow-up).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Per-faction carry-forward (008 FR-024/FR-025,
# Product Owner decision 2026-08-17, T077a-h): a *declared* faction whose page cannot be fetched no
# longer fails the whole sweep -- it is skipped here and sourced from the previous published tree
# by `pipeline.curate.carry_forward` instead. An *undeclared* faction that cannot be fetched still
# fails the whole sweep exactly as before (FR-008 unweakened) -- see `acquire_wahapedia_html`'s own
# docstring for the full reasoning.
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
    carried_forward_slugs: frozenset[str] = frozenset(),
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

    ``carried_forward_slugs`` (008 FR-024, Product Owner decision 2026-08-17): the faction slugs a
    curator has **declared**, in ``curation/carried-forward-factions.json``, as acceptable to
    source from the previous published version if this run cannot fetch them live. Three things
    happen to a slug in this set that do not happen to any other:

    1. It is attempted even when the live sitemap does not list it (the candidate slug set is the
       sitemap's own list **union** this one) — the exact gap `008`'s T074 dry-run found: a slug
       can vanish from the sitemap while its page is still live.
    2. If the attempt still fails (404, or any non-200), the sweep does **not** stop for it. No
       payload is produced for that slug; :func:`pipeline.curate.carry_forward.
       apply_carried_forward` is what sources it from ``data/<edition>/factions/f-<slug>/``
       instead, later in the run.
    3. If the attempt succeeds anyway (the source recovered), the **live** payload is used exactly
       as any other faction's — carry-forward is a fallback, never a preference, on the same
       "prefer real data" instruction the Product Owner gave for `008`'s restated SC-002.

    Every slug **not** in this set is held to the unchanged FR-008 rule: a page that does not
    answer stops the whole sweep. That asymmetry is the entire point — a curator has to have
    *looked at* a faction and decided its absence is acceptable before this function will ever
    treat it as anything other than a failed sweep. Which outcome each slug reached (carried,
    unused-declaration, or the ordinary live case) is returned via ``coverage`` on the
    :class:`~pipeline.models.source.SourceAcquisition`, not via a changed return shape — the
    two-tuple stays identical to the csv arm's, so nothing below ``acquire`` has to learn a new
    shape for what is still, from its own point of view, "the faction pages we managed to get."
    """
    if fixtures_dir is not None:
        return acquire_from_fixtures(
            fixtures_dir,
            SourceKey.WAHAPEDIA,
            config,
            retrieved_at=retrieved_at,
            layout=HTML_DETAIL_LAYOUT,
        )

    # The same refusal the csv arm makes, and for the same reason: the mode selects a parser, so
    # a configuration mistake must read identically whichever arm it is made against.
    base = config.require_detail_source().rstrip("/")
    owned = client is None
    active = client or PoliteClient(config, offline=offline)
    carried: list[str] = []
    unused_declarations: list[str] = []
    try:
        sitemap_slugs = enumerate_faction_slugs(active, base)
        candidate_slugs = sorted(set(sitemap_slugs) | carried_forward_slugs)
        payloads: list[FixturePayload] = []
        for slug in candidate_slugs:
            try:
                response = active.get(f"{base}/{FACTION_PAGE.format(slug=slug)}")
            except SourceUnreachable:
                if slug in carried_forward_slugs:
                    carried.append(slug)
                    continue
                raise SourceUnreachable(
                    f"the detail source could not be reached for faction page {slug!r}; a "
                    "partial sweep is a failed sweep (FR-008) -- declare it in "
                    "curation/carried-forward-factions.json if this is expected"
                ) from None
            if response.status_code != 200:
                if slug in carried_forward_slugs:
                    carried.append(slug)
                    continue
                raise SourceUnreachable(
                    f"the detail source responded {response.status_code} for faction page "
                    f"{slug!r}; a partial sweep is a failed sweep (FR-008) -- declare it in "
                    "curation/carried-forward-factions.json if this is expected"
                )
            payloads.append(FixturePayload(name=slug, text=response.text))
            if slug in carried_forward_slugs:
                unused_declarations.append(slug)
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
    # `SourceAcquisition.coverage` is `Mapping[str, int]` (it feeds FR-009's figures, which are
    # all counts) — so it carries *counts* of each carry-forward outcome, never the slugs
    # themselves. A caller that needs the actual slugs (`pipeline.curate.carry_forward`) derives
    # them itself from `carried_forward_slugs` against the payload names this function returns:
    # a slug in the declared set with no payload was carried; a slug in the declared set WITH a
    # payload had its declaration go unused this run. That derivation needs nothing this function
    # does not already return, so no second return value or field had to be invented for it.
    coverage: dict[str, int] = {"faction_pages": len(payloads)}
    if carried_forward_slugs:
        coverage["carried_forward_faction_count"] = len(carried)
        coverage["carry_forward_unused_declaration_count"] = len(unused_declarations)
    return (
        SourceAcquisition(
            acquisition_id=f"wahapedia-{moment.strftime('%Y%m%dT%H%M%SZ')}-{fingerprint[:8]}",
            source_key=SourceKey.WAHAPEDIA,
            source_base_url=base,
            declared_edition_code=config.detail_edition,
            retrieved_at=moment.isoformat().replace("+00:00", "Z"),
            content_fingerprint=f"sha256:{fingerprint}",
            coverage=coverage,
            request_count=request_count,
            request_interval_ms=config.request_interval_ms,
            outcome=AcquisitionOutcome.OK,
        ),
        payloads,
    )


def default_workspace() -> Path:
    """The ``work/`` directory the pages land in when no other is given."""
    return work_dir()
