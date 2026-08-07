# AI-Assisted: Claude Code (model: claude-opus-5) - Captured the unit section's heading as
# `cost_section_label`, which is the only signal distinguishing the points source's two cost
# tables for one Imperial Agents unit from a reprint of one table.
# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented points-source DOM extraction
# (task T058): unit cost tables with their label literals preserved for tier detection,
# model-count labels, points, delta markers, detachment cards with DP, force disposition and
# tags, enhancement name/points pairs, and Leader/Support lists — all read by reference.
"""Extract mechanical values from the reconstructed points-source DOM (FR-001, C1).

**Everything here is read through a containment relationship, never through document order.** A
points value is read from inside the ``<li>`` that also carries its model-count label; a DP cost
from inside the card header that also carries the detachment name; an enhancement's cost from
inside the row that carries its name. Change the order the fragments arrive in and every value
extracted here is identical, which is the property
``tests/unit/test_mfm_dom_extraction.py`` pins.

Selection keys on **structure and literal text**, not on the source's utility classes. A
Tailwind class list churns on every redesign; ``YOUR UNIT COSTS`` and ``2DP`` are the page's
actual vocabulary. The one exception is ``text-xl``, which is how a card states "this is my
title" and has no textual equivalent — it is matched as a substring of the class attribute so a
reordering of the class list does not break it.

Two things are captured but deliberately not authoritative:

* ``cost_table_label`` keeps the observed literal (``YOUR UNIT COSTS`` /
  ``YOUR 1ST TO 2ND UNITS COST`` / ``YOUR 3RD + UNIT COSTS``) because copy-indexed tier
  detection keys on it (C1);
* ``cost_section_label`` keeps the heading of the *section* the block sits in, for the same
  reason and with the same discipline — it is the only place the page says that a second cost
  table for a unit it has already priced is a **different price under a stated condition**
  rather than a reprint; and
* ``delta_marker`` captures the page's own ``▲ (+15)`` change annotation, which research D4d
  makes a *witness* for the change summary and never an authority — the markers persist across
  a release cycle and are cleared unannounced.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from selectolax.lexbor import LexborHTMLParser, LexborNode

from pipeline.models.source import (
    MfmCostRow,
    MfmDetachmentCard,
    MfmEnhancementEntry,
    MfmUnitCostBlock,
)

#: A cost-table heading. The literal is preserved verbatim; only the *match* is normalised.
_COST_TABLE_LABEL: Final = re.compile(r"^YOUR\b.*\bCOSTS?$", re.IGNORECASE)

#: ``▲ (+15) 155 pts`` / ``▼ (-10) 85 pts`` / ``40 pts``. The points are the trailing number;
#: the delta is optional and is captured separately so it can never be mistaken for a price.
_COST_CELL: Final = re.compile(r"(?:[▲▼]\s*\((?P<delta>[+-]\d+)\)\s*)?(?P<points>\d+)\s*pts\b")

#: ``2DP`` in a detachment card header.
_DP_COST: Final = re.compile(r"^(\d+)\s*DP$", re.IGNORECASE)

#: The headings that introduce a list of related unit names inside a unit block.
_RELATED_HEADINGS: Final[frozenset[str]] = frozenset({"LEADER", "LEADERS", "SUPPORT"})

_ENHANCEMENTS_HEADING: Final = "ENHANCEMENTS"


@dataclass(frozen=True, slots=True)
class MfmPage:
    """One points-source faction page, reduced to the mechanical facts it publishes."""

    faction_slug: str
    unit_blocks: tuple[MfmUnitCostBlock, ...] = ()
    detachments: tuple[MfmDetachmentCard, ...] = ()


def _text(node: LexborNode | None) -> str:
    """The node's whole text, whitespace-collapsed. ``None`` reads as empty, never as a crash."""
    if node is None:
        return ""
    return " ".join((node.text(deep=True) or "").split())


def _own_text(node: LexborNode) -> str:
    """Only the node's direct text, so a heading is not confused with the section under it."""
    return " ".join((node.text(deep=False) or "").split())


def _has_class(node: LexborNode, fragment: str) -> bool:
    return fragment in (node.attributes.get("class") or "")


def _child_elements(node: LexborNode) -> list[LexborNode]:
    return [child for child in node.iter(include_text=False)]


def _first_titled(node: LexborNode) -> str:
    """A card's own title: the first descendant that declares itself one."""
    for candidate in node.css("*"):
        if _has_class(candidate, "text-xl"):
            return _text(candidate)
    return ""


def _cost_rows(table: LexborNode) -> tuple[MfmCostRow, ...]:
    """One row per ``<li>``, pairing the label and the price *within* the same list item."""
    rows: list[MfmCostRow] = []
    for item in table.css("li"):
        spans = item.css("span")
        if not spans:
            continue
        label = _text(spans[0])
        for span in spans[1:]:
            match = _COST_CELL.search(_text(span))
            if match is None:
                continue
            rows.append(
                MfmCostRow(
                    model_count_label=label,
                    points=int(match.group("points")),
                    delta_marker=match.group("delta"),
                )
            )
            break
    return tuple(rows)


def _related_units(block: LexborNode) -> tuple[str, ...]:
    """The Leader / Support list: a comma-separated run of unit **names**, kept as names."""
    for section in block.css("div"):
        children = _child_elements(section)
        if len(children) < 2:
            continue
        heading = _text(children[0]).upper()
        if heading not in _RELATED_HEADINGS:
            continue
        listed = _text(children[1])
        return tuple(name.strip() for name in listed.split(",") if name.strip())
    return ()


def _section_label(block: LexborNode) -> str:
    """The heading of the section a unit block sits in, or `""` for the page's default section.

    The page groups its unit blocks into sections: a container holding a grid of blocks,
    optionally preceded by that section's own heading. Two kinds of heading are published
    through the same structure and only the reader can tell them apart — a *grouping*
    (`ULTRAMARINES`, one section per chapter, disjoint unit sets) and a *condition*
    (`EVERY MODEL HAS THE IMPERIUM KEYWORD`, the **same** unit priced a second time). Both are
    kept verbatim here for the same reason `cost_table_label` is: this module reports what the
    page says, and :mod:`pipeline.curate.assemble` decides what it means (C1).

    Read by containment, like everything else here: the section is the block's grid's parent,
    and the heading is the direct child of that section which holds no cost row. A section that
    states nothing yields `""`, which is the ordinary case on twenty-nine of the thirty pages.
    """
    grid = block.parent
    section = grid.parent if grid is not None else None
    if section is None:
        return ""
    for child in _child_elements(section):
        if child.css("li"):
            continue
        heading = _text(child)
        if heading:
            return heading
    return ""


def _unit_blocks(tree: LexborHTMLParser, slug: str) -> tuple[MfmUnitCostBlock, ...]:
    blocks: list[MfmUnitCostBlock] = []
    for label_node in tree.css("div"):
        label = _own_text(label_node)
        if not _COST_TABLE_LABEL.match(label):
            continue
        table = label_node.parent
        block = table.parent if table is not None else None
        if table is None or block is None:
            continue
        rows = _cost_rows(table)
        if not rows:
            continue
        blocks.append(
            MfmUnitCostBlock(
                faction_slug=slug,
                unit_display_name=_first_titled(block),
                cost_table_label=label,
                cost_section_label=_section_label(block),
                rows=rows,
                support_targets=_related_units(block),
            )
        )
    return tuple(blocks)


def _enhancements(card: LexborNode) -> tuple[MfmEnhancementEntry, ...]:
    entries: list[MfmEnhancementEntry] = []
    for section in card.css("div"):
        if _own_text(section).upper() != _ENHANCEMENTS_HEADING:
            continue
        listing = section.parent
        if listing is None:
            continue
        for item in listing.css("li"):
            spans = item.css("span")
            if len(spans) < 2:
                continue
            match = _COST_CELL.search(_text(spans[1]))
            if match is None:
                continue
            entries.append(
                MfmEnhancementEntry(name=_text(spans[0]), points=int(match.group("points")))
            )
        break
    return tuple(entries)


def _card_tags(card: LexborNode, header: LexborNode) -> tuple[str, ...]:
    """A tag is a direct child of the card carrying exactly one span and nothing else.

    That is how ``UPDATED``, ``FORCE DISPOSITION(S) CHANGED`` and ``Unique`` are all published,
    and it distinguishes them from the two-span header and from the enhancement section.
    """
    tags: list[str] = []
    for child in _child_elements(card):
        if child is header:
            continue
        inner = _child_elements(child)
        if len(inner) == 1 and inner[0].tag == "span":
            text = _text(child)
            if text:
                tags.append(text)
    return tuple(tags)


def _force_disposition(card: LexborNode, header: LexborNode) -> str | None:
    """The coloured band directly under the header. The colour is the page's only marker for it."""
    for child in _child_elements(card):
        if child is header or child.tag != "div":
            continue
        if "background-color" in (child.attributes.get("style") or ""):
            return _text(child) or None
    return None


def _detachment_cards(tree: LexborHTMLParser, slug: str) -> tuple[MfmDetachmentCard, ...]:
    cards: list[MfmDetachmentCard] = []
    for header in tree.css("div"):
        spans = [child for child in _child_elements(header) if child.tag == "span"]
        if len(spans) != 2 or not _has_class(spans[0], "text-xl"):
            continue
        dp = _DP_COST.match(_text(spans[1]))
        if dp is None:
            continue
        card = header.parent
        if card is None:
            continue
        cards.append(
            MfmDetachmentCard(
                faction_slug=slug,
                detachment_name=_text(spans[0]),
                dp_cost=int(dp.group(1)),
                force_disposition=_force_disposition(card, header),
                tags=_card_tags(card, header),
                enhancements=_enhancements(card),
            )
        )
    return tuple(cards)


def parse_faction_page(slug: str, html: str) -> MfmPage:
    """Parse one reconstructed faction page.

    ``html`` is the output of :func:`pipeline.parse.mfm_swap_replay.replay`, never a raw
    response — parsing before the replay would see empty placeholders where the prices are.
    """
    tree = LexborHTMLParser(html)
    return MfmPage(
        faction_slug=slug,
        unit_blocks=_unit_blocks(tree, slug),
        detachments=_detachment_cards(tree, slug),
    )
