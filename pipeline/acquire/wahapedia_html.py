# AI-Assisted: Claude Code (model: claude-opus-5) - Stubbed the html-mode detail acquirer (004
# task T018), so the WGC_DETAIL_ACQUISITION_MODE dispatch has both of its targets and the mode
# selector can be proven mode-blind before the retrieval itself lands in 004 T072.
"""Acquire the datasheet-detail source: the current-edition datacard pages.

**Not implemented yet.** The retrieval lands in `004` T072, guarded by
:mod:`pipeline.acquire.robots`' deny-list (which never triggers on this permitted path) and by
the existing ``robots.txt`` honouring, sweeping roughly 26 faction pages at the configured polite
interval — the same order of magnitude as the existing 30-page points sweep, so the politeness
budget is unchanged in character.

The module exists now, raising, for a specific reason: the dispatch in
:mod:`pipeline.acquire.detail_source` has **two** targets from the day it is written, so the
mode selector is exercised and proven mode-blind against the shape it will really have. A
dispatch written with one arm and extended later is a dispatch nobody tested.

What is already settled about it, from ``docs/verification/html-markup-spike.md`` (004 T002,
which retired risk R-A against the real markup):

* datacards enumerate as ``div.dsOuterFrame.datasheet``;
* block identity inside a card is **label-anchored** on ``div.dsHeader``, because
  ``div.dsAbility`` is shared by unrelated blocks and a class alone cannot tell them apart;
* ``KEYWORDS`` and ``FACTION KEYWORDS`` arrive as separately labelled blocks, so FR-017's split
  is carried by the markup itself;
* two traps: four column class names are spelled with a Cyrillic homoglyph, and the colour and
  faction class tokens vary per faction and may never be selected on.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pipeline.acquire.fixtures import FixturePayload
from pipeline.acquire.http import PoliteClient
from pipeline.config import PipelineConfig
from pipeline.models.source import SourceAcquisition


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
    :class:`~pipeline.models.source.SourceAcquisition` plus the retrieved payloads. That parity
    is what makes every stage below ``parse`` mode-blind — it cannot tell which arm ran, because
    there is nothing in what it receives that says.

    Raises:
        NotImplementedError: always, until `004` T072.
    """
    raise NotImplementedError(
        "html-mode detail acquisition lands in 004 T072. Set WGC_DETAIL_ACQUISITION_MODE=csv "
        "(the default) to acquire from the bulk export under the permitted current-edition path."
    )
