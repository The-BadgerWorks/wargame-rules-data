# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the build-time ephemeral
# rendering equivalence check (007 US5, tasks T052-T053): renders each published datasheet's Unit
# Composition and Wargear Options blocks via `render/loadout.py`'s typed core, reads the same
# blocks from the source card's in-memory `detail` (research D6, `reports/equivalence-
# availability/2026-08-13.md`), compares both sides under `rendering-contract.md` §9's normal
# form, and retains nothing from either side beyond the call that compares them (FR-019..FR-021).
"""The Part C equivalence check: does the rendering read like the card?

**The single fact this module exists to prove**: nothing here is typed to hold source text past
the comparison that reads it. :class:`EquivalenceSummary` — the only thing
:func:`check_equivalence` returns besides findings — carries three integers and nothing else.
Every :class:`~pipeline.models.findings.Finding` this module raises carries a datasheet id and a
block name and nothing else (contract §9.1, data-model.md §3-4). The source and rendered strings
themselves live in local variables for the span of one loop iteration and are never assigned to
an attribute, a return value, or a log call — so a retention bug has nowhere to write even by
accident, the same structural argument research D6 makes for the check as a whole.

**Called from exactly one place**: `pipeline.cli.run_build`'s own `with workspace(root) as work:`
block, alongside the mechanic-digest computation that already has the same reason to be there
(`reports/equivalence-availability/2026-08-13.md`, T001). Never from `check_snapshot` or
`run_validate` — neither has source text in scope by the time it runs.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final, Literal

from pipeline.models.curated import (
    CuratedCompositionEntry,
    CuratedDatasheet,
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    CuratedItemConstraint,
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
    CuratedSnapshot,
)
from pipeline.models.findings import Finding
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.render.loadout import (
    CompositionRow,
    EquipmentGroup,
    EquipmentItem,
    ItemConstraint,
    OptionChoice,
    OptionChoiceItem,
    OptionGroup,
    render_composition_block,
    render_options_block,
)
from pipeline.report.catalogue import build_finding

_Block = Literal["composition", "options"]
_Outcome = Literal["match", "mismatch", "not_compared"]

#: The detail source's own table names this module reads raw block text from (contract §9,
#: research D6). Never a new acquisition — these are the same tables `curate/assemble.py` already
#: reads from `detail` inside the same `with workspace()` block.
_COMPOSITION_TABLE: Final = "Datasheets_unit_composition.csv"
_OPTIONS_TABLE: Final = "Datasheets_options.csv"

#: Zero-width characters step 1 of contract §9 strips. U+FEFF (BOM), U+200B-200D
#: (zero-width space/non-joiner/joiner).
_ZERO_WIDTH_CHARS: Final = frozenset("﻿​‌‍")

#: Punctuation contract §9 step 3 maps to a single space before whitespace collapse.
_PUNCTUATION_CHARS: Final = frozenset(".,;:—–-()[]")

#: The comparison's closed elision-word set (contract §9 step 4). **Authored, versioned with this
#: module, deliberately NOT a second environment variable** — `pipeline/config.py` T014's own
#: decision, because contract §9.1 requires the normal form to be "not derived from any source
#: page," which is exactly what a runtime override would risk. Documented in
#: `docs/configuration.md` beside `WGC_EQUIVALENCE_CHECK_ENABLED`.
_ELISION_WORDS: Final[frozenset[str]] = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "of",
        "in",
        "with",
        "this",
        "that",
        "its",
        "is",
        "are",
        "to",
        "for",
        "on",
        "one",
    }
)


@dataclass(frozen=True, slots=True)
class EquivalenceSummary:
    """Counts only — the one thing that leaves the workspace block besides findings (FR-021).

    No field here, or anywhere reachable from it, is typed to hold either side's text. This is
    what the equivalence figure (`pipeline/validate/coverage.py::loadout_coverages`) is computed
    from once `detail` and the source text it carries have already gone out of scope.
    """

    matched: int = 0
    mismatched: int = 0
    not_compared: int = 0


def _normalize(text: str) -> tuple[str, ...]:
    """Contract §9's normal form, steps 1-4, ending in the token sequence step 5 compares."""
    folded = unicodedata.normalize("NFC", text)
    folded = "".join(ch for ch in folded if ch not in _ZERO_WIDTH_CHARS)
    folded = folded.replace(" ", " ")
    folded = folded.casefold()
    folded = "".join(" " if ch in _PUNCTUATION_CHARS else ch for ch in folded)
    return tuple(token for token in folded.split() if token not in _ELISION_WORDS)


def _rows_text(table: CsvReadResult | None, detail_id: str) -> list[str]:
    """One detail table's rows for one datasheet, in source line order — the raw sentences the
    card prints, exactly as `detail` already carries them (no new acquisition, research D6)."""
    if table is None:
        return []
    rows = table.grouped_by("datasheet_id").get(detail_id, [])

    def _line(row: Any) -> int:
        try:
            return int(row.fields.get("line", ""))
        except ValueError:
            return 0

    ordered = sorted(rows, key=_line)
    return [row.fields.get("description", "") for row in ordered]


def _source_text(
    detail: Mapping[str, CsvReadResult], detail_id: str | None, block: _Block
) -> str | None:
    """The raw source block text for one datasheet, or ``None`` when unavailable.

    ``None`` covers both readings contract §9 gives `not_compared`'s "one side unavailable": no
    `detail_id` (the datasheet has no detail-source counterpart at all) and zero rows for it in
    the relevant table (the source states nothing for this block).
    """
    if detail_id is None:
        return None
    if block == "composition":
        parts = [
            *_rows_text(detail.get(_COMPOSITION_TABLE), detail_id),
            *_rows_text(detail.get(EQUIPMENT_TABLE), detail_id),
        ]
    else:
        parts = _rows_text(detail.get(_OPTIONS_TABLE), detail_id)
    if not parts:
        return None
    return "\n".join(parts)


# ---------------------------------------------------------------------------------------------
# Curated -> render/loadout.py typed-core adapters. A direct field-name mapping, never a JSON
# round trip -- `pipeline/render/loadout.py`'s own US1 handoff note names this module as the
# caller meant to construct its dataclasses directly from curated data (.impl-progress.md).
# ---------------------------------------------------------------------------------------------


def _composition_row(entry: CuratedCompositionEntry) -> CompositionRow:
    return CompositionRow(
        line=entry.line,
        model_name=entry.model_name,
        min_count=entry.min_count,
        max_count=entry.max_count,
    )


def _equipment_item(item: CuratedEquipmentItem) -> EquipmentItem:
    return EquipmentItem(item_index=item.item_index, item_name=item.item_name, count=item.count)


def _equipment_group(group: CuratedEquipmentGroup) -> EquipmentGroup:
    return EquipmentGroup(
        id=group.id,
        line=group.line,
        applies_to=group.applies_to.value,
        model_name=group.model_name,
        items=tuple(_equipment_item(item) for item in group.items),
    )


def _option_choice_item(item: CuratedOptionChoiceItem) -> OptionChoiceItem:
    return OptionChoiceItem(
        role=item.role.value,
        item_index=item.item_index,
        item_name=item.item_name,
        count=item.count,
    )


def _option_choice(choice: CuratedOptionChoice) -> OptionChoice:
    return OptionChoice(
        id=choice.id,
        items=tuple(_option_choice_item(item) for item in choice.items),
        is_no_change=choice.is_no_change,
    )


def _option_group(
    group: CuratedOptionGroup, choices_by_group: Mapping[str, Sequence[CuratedOptionChoice]]
) -> OptionGroup:
    """``CuratedOptionGroup`` carries no nested ``choices`` -- unlike the render dataclass and
    unlike ``CuratedEquipmentGroup.items``, a curated datasheet's groups and choices are two flat
    sibling sequences on ``CuratedDatasheet``, joined by ``CuratedOptionChoice.group_id``
    (`pipeline/models/curated.py`). ``choices_by_group`` is that join, computed once per
    datasheet by the caller rather than once per group.
    """
    return OptionGroup(
        id=group.id,
        line=group.line,
        scope=group.scope.value,
        scope_n=group.scope_n,
        eligible_model_name=group.eligible_model_name,
        eligible_max_count=group.eligible_max_count,
        is_per_model=group.is_per_model,
        max_choices=group.max_choices,
        parent_group_id=group.parent_group_id,
        choices=tuple(_option_choice(choice) for choice in choices_by_group.get(group.id, ())),
    )


def _item_constraint(constraint: CuratedItemConstraint) -> ItemConstraint:
    return ItemConstraint(
        constraint_index=constraint.constraint_index,
        constraint_type=constraint.constraint_type.value,
        item_name=constraint.item_name,
        model_name=constraint.model_name,
    )


def _render_block(datasheet: CuratedDatasheet, block: _Block) -> str:
    """The published rendering of one block, via `render/loadout.py`'s typed core directly."""
    if block == "composition":
        result = render_composition_block(
            [_composition_row(entry) for entry in datasheet.composition],
            [_equipment_group(group) for group in datasheet.equipment_groups],
        )
    else:
        choices_by_group: dict[str, list[CuratedOptionChoice]] = {}
        for choice in datasheet.option_choices:
            choices_by_group.setdefault(choice.group_id, []).append(choice)
        result = render_options_block(
            [_option_group(group, choices_by_group) for group in datasheet.option_groups],
            [_item_constraint(constraint) for constraint in datasheet.item_constraints],
        )
    return result.canonical


def _compare(rendered: str, source: str | None) -> _Outcome:
    """Contract §9's three outcomes. Neither argument is retained by this function's return."""
    if not rendered:
        return "not_compared"
    if not source:
        return "not_compared"
    return "match" if _normalize(rendered) == _normalize(source) else "mismatch"


def check_equivalence(
    snapshot: CuratedSnapshot,
    detail: Mapping[str, CsvReadResult],
    *,
    wahapedia_datasheet_ids: Mapping[str, str],
) -> tuple[list[Finding], EquivalenceSummary]:
    """Per published datasheet, per block: render, read, compare, forget (FR-019..FR-021).

    Must be called while ``detail`` is still in scope — see this module's docstring and
    `reports/equivalence-availability/2026-08-13.md`. ``wahapedia_datasheet_ids`` is
    `AssemblyResult.wahapedia_datasheet_ids` (`pipeline/curate/assemble.py`, 007 T053): the join
    from a curated datasheet back to the detail source's own id for it, carried out of the
    assemble stage rather than re-derived here.
    """
    findings: list[Finding] = []
    matched = mismatched = not_compared = 0
    blocks: Sequence[_Block] = ("composition", "options")

    for datasheet in snapshot.datasheets:
        detail_id = wahapedia_datasheet_ids.get(datasheet.datasheet_id)
        for block in blocks:
            rendered = _render_block(datasheet, block)
            source = _source_text(detail, detail_id, block)
            outcome = _compare(rendered, source)

            if outcome == "match":
                matched += 1
            elif outcome == "mismatch":
                mismatched += 1
                findings.append(
                    build_finding(
                        "RND-EQV-MISMATCH",
                        entity_refs=[datasheet.datasheet_id],
                        detail={"datasheet_id": datasheet.datasheet_id, "block": block},
                    )
                )
            else:
                not_compared += 1
                findings.append(
                    build_finding(
                        "RND-EQV-NOT-COMPARED",
                        entity_refs=[datasheet.datasheet_id],
                        detail={"datasheet_id": datasheet.datasheet_id, "block": block},
                    )
                )
            # `rendered` and `source` fall out of scope at the top of the next iteration. Neither
            # is captured by the closure above, assigned to `findings`/the summary, or returned —
            # this loop body is the whole span of their lifetime (FR-020).

    return findings, EquivalenceSummary(
        matched=matched, mismatched=mismatched, not_compared=not_compared
    )
