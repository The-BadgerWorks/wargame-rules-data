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

from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path
from typing import Final, Protocol

from pipeline.acquire.fixtures import FixturePayload
from pipeline.acquire.http import PoliteClient
from pipeline.acquire.wahapedia import acquire_wahapedia
from pipeline.acquire.wahapedia_html import acquire_wahapedia_html
from pipeline.config import ConfigError, DetailAcquisitionMode, PipelineConfig
from pipeline.models.source import SourceAcquisition
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text
from pipeline.parse.wahapedia_html_dom import read_datacard_payloads


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


class DetailReader(Protocol):
    """The one signature both modes' readers implement.

    The reader is the second — and last — place the mode is visible. Both arms return the same
    ``file name -> CsvReadResult`` mapping, keyed by the export's own table names, so every stage
    from ``normalize`` down receives a shape that carries no trace of which source produced it.
    """

    def __call__(
        self, payloads: Sequence[FixturePayload], *, edition_code: str = ...
    ) -> dict[str, CsvReadResult]: ...


def read_export_payloads(
    payloads: Sequence[FixturePayload], *, edition_code: str = ""
) -> dict[str, CsvReadResult]:
    """The ``csv``-mode reader: one acquired export file per payload.

    A payload's name is the file name, with or without its suffix — the live adapter carries
    ``Datasheets.csv`` and the fixture adapter carries the stem — so the suffix is normalised
    here rather than at each call site. ``edition_code`` is accepted and unused: the signature is
    shared with the html reader on purpose, since a reader that had to be called differently per
    mode would put the mode back into every caller.
    """
    del edition_code
    return {
        (name if (name := payload.name).endswith(".csv") else f"{name}.csv"): read_text(
            name if name.endswith(".csv") else f"{name}.csv", payload.text
        )
        for payload in payloads
    }


#: mode -> acquirer. A table rather than a branch, so adding a mode is adding a row and the
#: dispatch itself has nothing to get wrong.
ACQUIRERS: Final[dict[DetailAcquisitionMode, DetailAcquirer]] = {
    DetailAcquisitionMode.CSV: acquire_wahapedia,
    DetailAcquisitionMode.HTML: acquire_wahapedia_html,
}

#: mode -> reader, the same table discipline. Adding a mode is adding a row to each table and
#: writing nothing else anywhere.
READERS: Final[dict[DetailAcquisitionMode, DetailReader]] = {
    DetailAcquisitionMode.CSV: read_export_payloads,
    DetailAcquisitionMode.HTML: read_datacard_payloads,
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
    return ACQUIRERS[_resolved(mode)]


def reader_for(mode: DetailAcquisitionMode | str) -> DetailReader:
    """The reader for ``mode``, validated on the same terms as :func:`acquirer_for`.

    Raises:
        ConfigError: ``mode`` is not one of the documented values.
    """
    return READERS[_resolved(mode)]


def _resolved(mode: DetailAcquisitionMode | str) -> DetailAcquisitionMode:
    try:
        return DetailAcquisitionMode(mode)
    except ValueError as exc:
        allowed = ", ".join(m.value for m in DetailAcquisitionMode)
        raise ConfigError(
            f"WGC_DETAIL_ACQUISITION_MODE must be one of {allowed}, got {mode!r}"
        ) from exc


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


def read_detail(
    config: PipelineConfig, payloads: Sequence[FixturePayload]
) -> dict[str, CsvReadResult]:
    """Read what :func:`acquire_detail` returned into the export's own table shape.

    This is the last function in the pipeline that knows a mode exists. What it returns is
    keyed by the export's table names in both modes, so ``curate``, ``reconcile``, and the two
    grammars below it are written once and exercised by both.
    """
    return reader_for(config.detail_acquisition_mode)(payloads, edition_code=config.detail_edition)
