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

import re
from collections.abc import Callable, Sequence
from dataclasses import replace as _replace_csv_read_result
from datetime import datetime
from pathlib import Path
from typing import Final, Protocol

from pipeline.acquire.fixtures import FixturePayload
from pipeline.acquire.http import PoliteClient
from pipeline.acquire.wahapedia import acquire_wahapedia
from pipeline.acquire.wahapedia_html import acquire_wahapedia_html
from pipeline.config import ConfigError, DetailAcquisitionMode, PipelineConfig
from pipeline.models.source import SourceAcquisition, WahapediaRow
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text
from pipeline.parse.wahapedia_html_dom import read_datacard_payloads

#: `Datasheets_unit_composition.csv`'s export name -- the table
#: :func:`_derive_equipment_from_composition` reads FROM.
_COMPOSITION_TABLE: Final = "Datasheets_unit_composition.csv"

#: The default-equipment marker (009 T057/T058, FR-017, plan.md finding 9). The SAME sentence
#: `parse/equipment_grammar.py::_MARKER` and `parse/wahapedia_html_dom.py::_DEFAULT_EQUIPMENT_
#: SENTENCE` already match, kept as its OWN copy here rather than importing either private
#: symbol -- the same discipline `wahapedia_html_dom.py` already applies to its own copy. This is
#: acquire-layer row-routing (which table a row belongs in), never a grammar concern, and
#: `parse/equipment_grammar.py` is not edited by this feature (rule 5).
_EQUIPMENT_MARKER: Final = re.compile(r"\b(?:is|are)\s+equipped\s+with\s*:", re.IGNORECASE)


def _derive_equipment_from_composition(
    detail: dict[str, CsvReadResult],
) -> dict[str, CsvReadResult]:
    """csv-mode's equivalent of ``wahapedia_html_dom.py::_equipment`` (009 T057/T058, FR-017).

    The real bulk export publishes no ``Datasheets_unit_equipment.csv`` at all (FR-018) — under
    ``html`` mode the equivalent table is manufactured from the datacard's composition block.
    The export instead files the SAME default-equipment sentence as an ordinary row of
    ``Datasheets_unit_composition.csv`` (``plan.md`` finding 9's ``GF05|1``/``CM03|2`` shape).

    Left there, it does double harm: ``composition_grammar.parse_entry`` cannot resolve it
    (correctly — it is not a composition sentence), which sets ``_composition_entries``'s
    ``unresolved`` flag and suppresses the WHOLE datasheet's composition (FR-008's "all or
    none"); and because ``curate/assemble.py::_equipment`` refuses to attach equipment to a
    datasheet whose composition did not resolve, the datasheet's equipment is poisoned too — not
    merely absent, destructive. Splitting the row out here, before it ever reaches
    ``composition_grammar``, fixes both at once: composition no longer sees a row it cannot
    parse, and the equipment table gains exactly the sentence the html arm would have extracted
    from the same datacard, in the identical ``datasheet_id|line|description`` shape.
    """
    composition = detail.get(_COMPOSITION_TABLE)
    if composition is None:
        return detail

    kept: list[WahapediaRow] = []
    derived: list[WahapediaRow] = []
    for row in composition.rows:
        if _EQUIPMENT_MARKER.search(row.fields.get("description", "")):
            derived.append(row.model_copy(update={"file_name": EQUIPMENT_TABLE}))
        else:
            kept.append(row)

    if not derived:
        return detail

    updated = dict(detail)
    updated[_COMPOSITION_TABLE] = _replace_csv_read_result(composition, rows=tuple(kept))
    existing_equipment = detail.get(EQUIPMENT_TABLE)
    updated[EQUIPMENT_TABLE] = CsvReadResult(
        file_name=EQUIPMENT_TABLE,
        field_names=("datasheet_id", "line", "description"),
        rows=(existing_equipment.rows if existing_equipment else ()) + tuple(derived),
        repairs=existing_equipment.repairs if existing_equipment else 0,
        findings=existing_equipment.findings if existing_equipment else (),
    )
    return updated


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
        carried_forward_slugs: frozenset[str] = ...,
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

    009 T057/T058 (FR-017): the raw per-file read is followed by
    :func:`_derive_equipment_from_composition`, which moves any default-equipment sentence out of
    ``Datasheets_unit_composition.csv`` and into a derived ``Datasheets_unit_equipment.csv`` —
    still inside the reader, so every stage below ``acquire`` sees the same table shape both arms
    produce and stays mode-blind (rule 4).
    """
    del edition_code
    results = {
        (name if (name := payload.name).endswith(".csv") else f"{name}.csv"): read_text(
            name if name.endswith(".csv") else f"{name}.csv", payload.text
        )
        for payload in payloads
    }
    return _derive_equipment_from_composition(results)


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
    carried_forward_slugs: frozenset[str] = frozenset(),
) -> tuple[SourceAcquisition, list[FixturePayload]]:
    """Acquire the datasheet-detail source in the configured mode.

    Every caller below ``acquire`` takes what this returns and never asks how it was obtained.

    ``carried_forward_slugs`` (008 FR-024): forwarded to whichever arm ran. Only the html arm
    gives it any meaning — see :func:`pipeline.acquire.wahapedia_html.acquire_wahapedia_html`.
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
        carried_forward_slugs=carried_forward_slugs,
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
