# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the WGC_DETAIL_ACQUISITION_MODE
# dispatch (004 task T018): csv routes to the existing export acquirer unchanged, html routes to
# the datacard acquirer, both producing the same SourceAcquisition record shape so every stage
# below parse is mode-blind (004 research D1d, plan Architecture).
"""Which shape the datasheet-detail source is read in — and nothing else.

``WGC_DETAIL_ACQUISITION_MODE`` selects **a parser, not a behaviour**. This is the same
discipline ``WGC_DATA_CHANNEL`` already follows: *variables, never logic*. The two modes read
genuinely different things —

===========  ==========================================  =====================================
Mode         Source                                      Edition of the *content*
===========  ==========================================  =====================================
``csv``      the bulk export on the permitted path       the **previous** edition
``html``     the current-edition datacard pages          the **current** edition (FR-003)
===========  ==========================================  =====================================

— but they emit the same :class:`~pipeline.models.source.SourceAcquisition` record shape, so
every stage below ``parse`` cannot tell which one ran. That is not a tidiness point. It is what
lets the composition and option grammars be written once, tested once against the better-measured
``csv`` shape, and then reused **unmodified** under ``html`` mode; and it is what lets the
edition move be a variable change rather than a second code path nobody exercises until the day
it matters.

**The whole of the mode's influence is in this module.** If a `if mode is …` appears anywhere
below ``acquire``, the design has been lost.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Final, Protocol

from pipeline.acquire.fixtures import FixturePayload
from pipeline.acquire.http import PoliteClient
from pipeline.acquire.wahapedia import acquire_wahapedia
from pipeline.acquire.wahapedia_html import acquire_wahapedia_html
from pipeline.config import ConfigError, DetailAcquisitionMode, PipelineConfig
from pipeline.models.source import SourceAcquisition


class DetailAcquirer(Protocol):
    """The one signature both modes implement.

    Written down as a protocol rather than left implicit so "the two arms agree" is checked by
    the type system rather than by a reviewer noticing.
    """

    def __call__(
        self,
        config: PipelineConfig,
        *,
        fixtures_dir: Path | None = ...,
        offline: bool = ...,
        client: PoliteClient | None = ...,
        retrieved_at: datetime | None = ...,
        workspace: Path | None = ...,
    ) -> tuple[SourceAcquisition, list[FixturePayload]]: ...


#: mode -> acquirer. A table rather than a branch, so adding a mode is adding a row and the
#: dispatch itself has nothing to get wrong.
ACQUIRERS: Final[dict[DetailAcquisitionMode, DetailAcquirer]] = {
    DetailAcquisitionMode.CSV: acquire_wahapedia,
    DetailAcquisitionMode.HTML: acquire_wahapedia_html,
}


def acquirer_for(mode: DetailAcquisitionMode | str) -> DetailAcquirer:
    """The acquirer for ``mode``.

    Accepts a raw string as well as the enum and re-validates it. :func:`load_config` already
    refuses an unrecognised value, so this is the second of two checks — worth having because a
    :class:`~pipeline.config.PipelineConfig` can also be built directly (``dataclasses.replace``
    in tests, for one), and a mode that reached this far unvalidated would fail as a ``KeyError``
    deep in a stage rather than as the configuration error it is.

    Raises:
        ConfigError: ``mode`` is not one of the documented values.
    """
    try:
        resolved = DetailAcquisitionMode(mode)
    except ValueError as exc:
        allowed = ", ".join(m.value for m in DetailAcquisitionMode)
        raise ConfigError(
            f"WGC_DETAIL_ACQUISITION_MODE must be one of {allowed}, got {mode!r}"
        ) from exc
    return ACQUIRERS[resolved]


def acquire_detail(
    config: PipelineConfig,
    *,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    client: PoliteClient | None = None,
    retrieved_at: datetime | None = None,
    workspace: Path | None = None,
) -> tuple[SourceAcquisition, list[FixturePayload]]:
    """Acquire the datasheet-detail source in the configured mode.

    Every caller below ``acquire`` takes what this returns and never asks how it was obtained.
    """
    acquire: Callable[..., tuple[SourceAcquisition, list[FixturePayload]]] = acquirer_for(
        config.detail_acquisition_mode
    )
    return acquire(
        config,
        fixtures_dir=fixtures_dir,
        offline=offline,
        client=client,
        retrieved_at=retrieved_at,
        workspace=workspace,
    )
