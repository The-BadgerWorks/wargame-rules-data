# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the presentation-free
# projection of a parsed points-source faction page (task T104), per research D4b: only the
# faction slug, normalised unit name, cost-table label, model-count label, points, detachment
# name, DP cost, force disposition, and enhancement name/points survive; everything else the
# page carries is presentation of the page, not of a rule, and is deliberately left out.
"""Project a parsed faction page to the canonical, presentation-free structure D4b digests.

**What is projected, and why each field earns its place** (research D4b): faction slug,
normalised unit name, cost-table label (tier detection keys on it, C1), each row's model-count
label and points, detachment name, DP cost, force disposition, and each enhancement's name and
points. Every one of these is a value a player pays or a fact a list-builder needs.

**What is deliberately excluded, and why excluding it is the point**: the ``▲ (+15)`` /
``▼ (-10)`` delta prefixes, the ``UPDATED`` and ``FORCE DISPOSITION(S) CHANGED`` tags, colour
classes, element ids, whitespace, and document order. Those are presentation *of change*, not
change itself, and the publisher clears its own markers on an unannounced schedule — including
them would make an unchanged release look changed the moment that happens, which is exactly the
false positive FR-053 prohibits.

The projection is sorted at every level before it reaches the digest (:mod:`pipeline.detect.
digest`), so page ordering never affects the result, and it is serialised through the one
canonical serialiser (``pipeline.build.canonical_json``) so no second set of formatting rules
can quietly reopen the determinism gap ``canonical_json`` exists to close.
"""

from __future__ import annotations

from dataclasses import dataclass

from pipeline.build.canonical_json import JsonValue
from pipeline.normalize.names import normalize_name
from pipeline.parse.mfm_dom import MfmPage


@dataclass(frozen=True, slots=True, order=True)
class _UnitCostLine:
    """One presentation-free unit cost row, orderable so sorting needs no key function."""

    unit_name: str
    cost_table_label: str
    model_count_label: str
    points: int


@dataclass(frozen=True, slots=True, order=True)
class _EnhancementLine:
    name: str
    points: int


def _unit_lines(page: MfmPage) -> tuple[_UnitCostLine, ...]:
    lines = [
        _UnitCostLine(
            unit_name=normalize_name(block.unit_display_name),
            cost_table_label=block.cost_table_label,
            model_count_label=row.model_count_label.strip(),
            points=row.points,
        )
        for block in page.unit_blocks
        for row in block.rows
    ]
    return tuple(sorted(lines))


def _detachment_json(
    *,
    name: str,
    dp_cost: int,
    force_disposition: str | None,
    enhancements: tuple[_EnhancementLine, ...],
) -> dict[str, JsonValue]:
    body: dict[str, JsonValue] = {
        "detachment_name": name,
        "dp_cost": dp_cost,
        "enhancements": [
            {"name": entry.name, "points": entry.points} for entry in sorted(enhancements)
        ],
    }
    if force_disposition is not None:
        body["force_disposition"] = force_disposition
    return body


def project_faction(page: MfmPage) -> JsonValue:
    """The presentation-free projection of one faction page (FR-053, research D4b).

    Deterministic regardless of the order the source's fragments happened to arrive in: every
    list is sorted before it is returned, and the caller (:mod:`pipeline.detect.digest`)
    serialises the result through the canonical serialiser before hashing it.
    """
    units: list[JsonValue] = [
        {
            "unit_name": line.unit_name,
            "cost_table_label": line.cost_table_label,
            "model_count_label": line.model_count_label,
            "points": line.points,
        }
        for line in _unit_lines(page)
    ]

    detachment_entries: list[tuple[str, dict[str, JsonValue]]] = [
        (
            normalize_name(card.detachment_name),
            _detachment_json(
                name=normalize_name(card.detachment_name),
                dp_cost=card.dp_cost,
                force_disposition=card.force_disposition,
                enhancements=tuple(
                    _EnhancementLine(name=normalize_name(entry.name), points=entry.points)
                    for entry in card.enhancements
                ),
            ),
        )
        for card in page.detachments
    ]
    detachments: list[JsonValue] = [
        entry for _, entry in sorted(detachment_entries, key=lambda pair: pair[0])
    ]

    return {
        "faction_slug": page.faction_slug,
        "units": units,
        "detachments": detachments,
    }
