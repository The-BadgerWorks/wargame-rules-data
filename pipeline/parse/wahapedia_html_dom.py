# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the current-edition datacard DOM
# extraction (004 task T073): class-anchored card and column discovery, label-anchored block
# identity, homoglyph-folded class comparison, and export-shaped records so the composition and
# option grammars, the keyword split, and the ability join are reused unmodified under html mode
# (risk R-A, research D1c-D1d, docs/verification/html-markup-spike.md).
# AI-Assisted: Claude Code (model: claude-opus-5) - Fixed the cost-table tier boundary: a repeated
# header row before any price is the same heading, not the next tier. Reading it as the next tier
# ended the read with nothing and left 160 live datasheets priced by no source at all.
"""Extract the current-edition datacard pages into the **same record shape** ``csv`` mode reads.

This module is the whole of the difference between the two detail-acquisition modes. Above it,
:mod:`pipeline.acquire.detail_source` chose which source to read; below it, every stage receives
one ``file name -> CsvReadResult`` mapping and cannot tell which mode produced it. That is not a
tidiness point — it is what lets :mod:`pipeline.parse.composition_grammar`,
:mod:`pipeline.parse.options_grammar`, the keyword classifier, and the ability digest join be
written once, measured once against the better-understood export shape, and then reused
**unmodified** against the current edition.

Emitting the export's own table names is the mechanism. ``Datasheets_unit_composition.csv`` does
not exist as a file in ``html`` mode; it exists as *the name of the table* the composition lines
arrive in, because that is the name every consumer of them downstream already asks for. The
alternative — a second set of record types, joined by a second set of readers — is the second
code path this design exists to avoid.

Structure, as ``docs/verification/html-markup-spike.md`` (`004` T002) established it against the
real markup, and as the fixtures reproduce it:

============================  ==========================================================
Datacard                      ``div.dsOuterFrame.datasheet``, one per datasheet
Datasheet identity            the ``<a name="…">`` anchor immediately preceding the card
Block identity                the **label** in a ``div.dsHeader``, never a class
Keyword split                 ``div.ds2colKW``'s two columns, ``KEYWORDS`` / ``FACTION KEYWORDS``
Weapon profiles               ``table.wTable``, one ``tbody`` per weapon
Characteristics               ``div.dsProfileBaseWrap`` per model profile
Detachment roster             ``label.DetFilterItem[data-det-code][data-det-name]``
============================  ==========================================================

**Two traps, both defended against here rather than commented about.**

1. *A Cyrillic homoglyph in four column class names.* ``dsLeftСol``, ``dsRightСol``,
   ``dsLeftСolKW`` and ``dsRightСolKW`` are spelled with ``U+0421 CYRILLIC CAPITAL LETTER ES``,
   so the ASCII selector ``.dsLeftCol`` matches **nothing, silently** — a zero-row extraction
   that reads as a source change rather than as a typo. Nothing here selects on those names at
   all: columns are taken as the positional children of ``div.ds2col`` / ``div.ds2colKW``, and
   every class comparison that does happen goes through
   :func:`pipeline.normalize.homoglyphs.fold_homoglyphs` first, so both spellings match and the
   day the publisher fixes the typo is a day nothing here notices.
2. *Faction-varying colour classes.* ``dsColorBgAS`` / ``dsColorBgTAU``, ``dsColorFr…``, and the
   per-faction keyword-code tokens differ per faction. **No selector here names one.**

**The heading vocabulary is asserted structurally, and a move fails the run loudly.** Not by
listing every label — the label set is genuinely open, because a datasheet may head its own
ability block with anything — but by requiring the blocks this feature *consumes* to be present
at the rate the spike measured them: ``ABILITIES`` and ``UNIT COMPOSITION`` on every card, one
keyword block on every card. A relabelling upstream therefore stops the run with a diagnostic
naming the label and the count, which is the discipline :mod:`pipeline.parse.mfm_dom` applies.

**Faction identity under this mode is the page slug** (``adepta-sororitas``), because that is the
identifier the source itself uses for a faction page and there is no code column to read. It is
deliberately *not* inferred into the previous export's two-letter codes. Adopting this mode
therefore includes one curator edit — ``curation/faction-map.json``'s
``detail_source_faction_id`` values become the slugs already sitting in the same records'
``mfm_slug`` — which is a reviewed change to an authored file, exactly where a change of identity
belongs.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

from selectolax.lexbor import LexborHTMLParser, LexborNode

from pipeline.acquire.fixtures import FixturePayload
from pipeline.models.source import WahapediaRow
from pipeline.normalize.homoglyphs import fold_homoglyphs
from pipeline.parse.wahapedia_csv import CsvReadResult

#: The datacard root. Both tokens, because ``dsOuterFrame`` alone is also used for other frames.
CARD_SELECTOR: Final = "div.dsOuterFrame.datasheet"

#: Block labels this module consumes. Everything else on a card is a datasheet-specific ability
#: heading and is passed over — recorded in :attr:`DatacardPage.unconsumed_labels` so a
#: vocabulary shift is visible rather than silent.
ABILITIES_LABEL: Final = "ABILITIES"
WARGEAR_ABILITIES_LABEL: Final = "WARGEAR ABILITIES"
COMPOSITION_LABEL: Final = "UNIT COMPOSITION"
OPTIONS_LABEL: Final = "WARGEAR OPTIONS"
LEADER_LABEL: Final = "LEADER"
LED_BY_LABEL: Final = "LED BY"
DETACHMENT_ABILITY_LABEL: Final = "DETACHMENT ABILITY"

CONSUMED_LABELS: Final[frozenset[str]] = frozenset(
    {
        ABILITIES_LABEL,
        WARGEAR_ABILITIES_LABEL,
        COMPOSITION_LABEL,
        OPTIONS_LABEL,
        LEADER_LABEL,
        LED_BY_LABEL,
        DETACHMENT_ABILITY_LABEL,
    }
)

#: Labels that must appear on **every** card. The spike counted each at exactly one per card on
#: both faction pages it read (63/63 and 38/38), so a shortfall is a structural change upstream
#: and not a quirk of one datasheet.
REQUIRED_CARD_LABELS: Final[tuple[str, ...]] = (ABILITIES_LABEL, COMPOSITION_LABEL)

#: ``DAMAGED: 1-6 WOUNDS REMAINING`` — the one label that embeds integers, matched as a pattern
#: rather than as a literal, exactly as the spike's §3 requires.
_DAMAGED_LABEL: Final = re.compile(r"^DAMAGED:\s*(\d+\s*-\s*\d+)\s+WOUNDS?\s+REMAINING$")

#: The characteristic row, in the fixed order the page prints it. Asserted rather than trusted:
#: reading positionally is only safe while the order is what it says it is.
CHARACTERISTIC_NAMES: Final[tuple[str, ...]] = ("M", "T", "SV", "W", "LD", "OC")

#: The weapon table's stat columns, in the fixed order the page prints them, mapped onto the
#: export's own field names so the assemble stage reads them unchanged.
_WEAPON_FIELDS: Final[tuple[str, ...]] = ("range", "A", "BS_WS", "S", "AP", "D")

_RANGED_SECTION: Final = "RANGED WEAPONS"
_MELEE_SECTION: Final = "MELEE WEAPONS"

#: A "the source publishes none" placeholder in an option or composition list.
_NONE_TEXT: Final = "none"

#: The rule the page draws between two things printed inside one element: two named abilities,
#: or two model-scoped keyword groups. It is a ``div.dsLineHor`` in the first case and a
#: ``span.dsVertLine`` in the second, so the pattern names both rather than one — a separator
#: missed is two records silently merged into one, which reads downstream as a keyword nobody
#: can classify rather than as a parse defect.
_GROUP_SEPARATOR: Final = re.compile(
    r"<(?:div|span)[^>]*\bclass=\"[^\"]*\b(?:dsLineHor|dsVertLine)\b[^\"]*\"[^>]*>\s*"
    r"</(?:div|span)>"
)

#: The qualifier in ``KEYWORDS – THE <model>``: everything after the dash names the models the
#: list applies to, and is the export's own ``model`` column by another spelling.
_KEYWORD_QUALIFIER: Final = re.compile(r"\s*[–—-]\s*")

#: ``#tooltip_content00079`` -> ``00079``.
_TOOLTIP_ID: Final = re.compile(r"#?tooltip_content(\w+)$")

#: The source ids the emitted ``Source.csv`` carries. Two rows, because the only fact the
#: assemble stage reads out of that table is "which publication makes a datasheet Legends", and
#: the datacard page states that as a class token on the card rather than as a publication.
LEGENDS_SOURCE_ID: Final = "legends"
CURRENT_SOURCE_ID: Final = "current"

#: The table names emitted, each mapped to its field names in the export's own order. Declared
#: as one table so "what html mode produces" is answerable by reading a single object, and so a
#: table that is emitted empty still arrives with its header — the difference between "the source
#: published none" and "the source was not consulted" (FR-016) is carried by the table's
#: presence, and losing it would silently change a state.
EMITTED_TABLES: Final[Mapping[str, tuple[str, ...]]] = {
    "Source.csv": ("id", "name", "type", "edition"),
    "Factions.csv": ("id", "name", "link"),
    "Datasheets.csv": ("id", "name", "faction_id", "source_id", "role", "damaged_w", "legend"),
    "Datasheets_models.csv": (
        "datasheet_id",
        "line",
        "name",
        "M",
        "T",
        "Sv",
        "inv_sv",
        "W",
        "Ld",
        "OC",
        "base_size",
    ),
    "Datasheets_wargear.csv": (
        "datasheet_id",
        "line",
        "name",
        "type",
        "range",
        "A",
        "BS_WS",
        "S",
        "AP",
        "D",
    ),
    "Datasheets_keywords.csv": ("datasheet_id", "keyword", "model", "is_faction_keyword"),
    "Datasheets_abilities.csv": (
        "datasheet_id",
        "line",
        "ability_id",
        "model",
        "name",
        "description",
        "type",
    ),
    "Abilities.csv": ("id", "name", "legend", "faction_id", "description"),
    "Datasheets_unit_composition.csv": ("datasheet_id", "line", "description"),
    "Datasheets_options.csv": ("datasheet_id", "line", "button", "description"),
    "Datasheets_models_cost.csv": ("datasheet_id", "line", "description", "cost"),
    "Datasheets_leader.csv": ("leader_id", "attached_id"),
    "Detachments.csv": ("id", "faction_id", "name", "legend", "type"),
    "Detachment_abilities.csv": ("id", "detachment_id", "name", "legend", "description"),
}


class HtmlStructureError(ValueError):
    """The page no longer has the structure every extractor here depends on.

    Raised rather than reported, and deliberately: a structural move upstream turns every
    extractor below into a silent zero-row read, and a snapshot missing an army's composition is
    far worse than a run that stops with a diagnostic naming what moved. The sibling of
    :class:`pipeline.parse.wahapedia_csv.CsvShapeError`, on the same reasoning.
    """


# -- small DOM helpers -----------------------------------------------------------------------


def _text(node: LexborNode | None) -> str:
    """The node's whole text, **element boundaries separated**, whitespace-collapsed.

    The separation is the point, and it is not cosmetic. The page spells one keyword as several
    adjacent ``<span>`` elements — they are line-break opportunities, not tokens — with no text
    between them, so the parser's own ``text()`` concatenates them into one run and a two-word
    keyword arrives as one unspaced word. Inserting a boundary space and collapsing afterwards
    recovers exactly what a reader sees, which is what every name extracted here has to be.

    ``None`` reads as empty, never as a crash.
    """
    if node is None:
        return ""
    fragments: list[str] = []
    _collect_text(node, fragments)
    return " ".join("".join(fragments).split())


def _collect_text(node: LexborNode, into: list[str]) -> None:
    for child in node.iter(include_text=True):
        if child.tag == "-text":
            into.append(child.text(deep=False) or "")
        else:
            into.append(" ")
            _collect_text(child, into)
            into.append(" ")


def _own_text(node: LexborNode) -> str:
    """Only the node's own text, so a block's label is not confused with its content."""
    return " ".join((node.text(deep=False) or "").split())


def _class_tokens(node: LexborNode) -> frozenset[str]:
    """The node's class tokens, **homoglyph-folded** — see trap 1 in the module docstring."""
    tokens = (node.attributes.get("class") or "").split()
    return frozenset(fold_homoglyphs(token) for token in tokens)


def _has_class(node: LexborNode, token: str) -> bool:
    return token in _class_tokens(node)


def _children(node: LexborNode) -> list[LexborNode]:
    return list(node.iter(include_text=False))


def _text_without(node: LexborNode, *class_tokens: str) -> str:
    """The node's text with any descendant carrying one of ``class_tokens`` removed.

    Works on a re-parse of the node rather than on the node, so the page itself is never
    mutated: two extractors reading the same element must not depend on which ran first.
    """
    tree = LexborHTMLParser(node.html or "")
    body = tree.body
    if body is None:
        return ""
    for candidate in body.css("*"):
        if _class_tokens(candidate) & frozenset(class_tokens):
            candidate.decompose()
    return _text(body)


# -- block segmentation ----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Block:
    """One labelled block of a datacard: its label, and the elements beneath it."""

    label: str
    nodes: tuple[LexborNode, ...]


def _block_sequences(container: LexborNode, depth: int = 0) -> Iterator[list[LexborNode]]:
    """Yield each run of siblings that a ``div.dsHeader`` introduces.

    One level of plain wrapper is followed, because the feature columns wrap their block in an
    unclassed ``div`` while the datacard body does not, and treating those two as different
    layouts would mean two segmenters that can disagree.
    """
    children = _children(container)
    if any(child.tag == "div" and _has_class(child, "dsHeader") for child in children):
        yield children
        return
    if depth >= 2:
        return
    for child in children:
        yield from _block_sequences(child, depth + 1)


def blocks_of(card: LexborNode) -> list[Block]:
    """Every labelled block of one datacard, in document order.

    Label-anchored, because block identity genuinely is not carried by a class: a
    ``UNIT COMPOSITION`` line and an ``ABILITIES`` entry are *both* ``div.dsAbility`` and only
    the preceding ``div.dsHeader`` tells them apart (spike §3). The weapon table's column heads
    share the class and are excluded structurally — they live inside ``table.wTable``, and this
    walk never descends into a table.
    """
    found: list[Block] = []
    for column_group in card.css("div.ds2col"):
        for column in _children(column_group):
            for sequence in _block_sequences(column):
                label: str | None = None
                nodes: list[LexborNode] = []
                for node in sequence:
                    if node.tag == "div" and _has_class(node, "dsHeader"):
                        if label is not None:
                            found.append(Block(label, tuple(nodes)))
                        label, nodes = _text(node).upper(), []
                    elif label is not None:
                        nodes.append(node)
                if label is not None:
                    found.append(Block(label, tuple(nodes)))
    return found


# -- extracted records -----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ModelProfile:
    """One model line: the six characteristics, the invulnerable save, and the base size."""

    line: int
    name: str
    characteristics: tuple[str, ...]
    invuln_save: str | None
    base_size: str | None


@dataclass(frozen=True, slots=True)
class WeaponProfile:
    """One weapon profile, with the six statistics in the page's own column order."""

    line: int
    name: str
    is_melee: bool
    statistics: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AbilityReference:
    """One ability as the card states it.

    ``ability_id`` names the page's own tooltip when the card refers to a shared ability rather
    than printing it, which is the same indirection ``Datasheets_abilities.ability_id`` carries
    in the export — so the digest join reads it unchanged.
    """

    name: str
    ability_type: str
    ability_id: str = ""
    description: str = ""


@dataclass(frozen=True, slots=True)
class Datacard:
    """One datasheet, reduced to the mechanical facts the page publishes."""

    detail_id: str
    name: str
    faction_id: str
    is_legends: bool = False
    damaged_wounds: str = ""
    models: tuple[ModelProfile, ...] = ()
    weapons: tuple[WeaponProfile, ...] = ()
    keywords: tuple[tuple[str, str, bool], ...] = ()
    abilities: tuple[AbilityReference, ...] = ()
    composition: tuple[str, ...] = ()
    options: tuple[str, ...] = ()
    costs: tuple[tuple[str, str], ...] = ()
    leads: tuple[str, ...] = ()
    led_by: tuple[str, ...] = ()
    detachment_rules: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class Detachment:
    """One detachment the faction publishes, from the page's own detachment roster."""

    code: str
    name: str


@dataclass(slots=True)
class DatacardPage:
    """One faction's datacard page."""

    faction_slug: str
    faction_name: str = ""
    cards: tuple[Datacard, ...] = ()
    detachments: tuple[Detachment, ...] = ()
    ability_texts: Mapping[str, tuple[str, str]] = field(default_factory=dict)
    """``tooltip id -> (name, mechanic text)`` for every shared ability the cards refer to."""
    unconsumed_labels: tuple[str, ...] = ()


# -- per-card extraction ---------------------------------------------------------------------


def _card_anchor(card: LexborNode) -> str:
    """The ``<a name="…">`` immediately preceding the card — the source's own datasheet id.

    The same anchor the publisher's sitemap uses as a per-datasheet URL, so it is an identifier
    the source maintains rather than one this pipeline invents from a display name.
    """
    node = card.prev
    for _ in range(4):
        if node is None:
            break
        if node.tag == "a" and node.attributes.get("name"):
            return node.attributes["name"] or ""
        node = node.prev
    return ""


def _card_name(card: LexborNode) -> str:
    header = card.css_first("div.dsH2Header")
    if header is None:
        return ""
    first = next((child for child in _children(header) if child.tag == "div"), None)
    return _text(first)


def _model_profiles(card: LexborNode, fallback_name: str) -> tuple[ModelProfile, ...]:
    """One profile per ``div.dsProfileBaseWrap``, read positionally against an asserted header.

    The characteristic *names* are printed once, on the first profile only, so every profile
    after it is read by position — which is safe exactly as long as the order is the order the
    first profile declares. That is asserted here rather than assumed.
    """
    profiles: list[ModelProfile] = []
    wraps = card.css("div.dsProfileBaseWrap")
    for index, wrap in enumerate(wraps, start=1):
        if index == 1:
            names = tuple(_text(node).upper() for node in wrap.css("div.dsCharName"))
            if names and names != CHARACTERISTIC_NAMES:
                raise HtmlStructureError(
                    "the datacard's characteristic row is no longer "
                    f"{'/'.join(CHARACTERISTIC_NAMES)} but {'/'.join(names)}; every profile after "
                    "the first is read by position and would now be read wrongly"
                )
        values = tuple(_text(node) for node in wrap.css("div.dsCharValue"))
        if len(values) != len(CHARACTERISTIC_NAMES):
            continue
        name = _text(wrap.css_first("span.dsModelName")) or fallback_name
        base = _text(wrap.css_first("span.dsModelBase")) or _text(
            card.css_first("span.dsModelBase2")
        )
        profiles.append(
            ModelProfile(
                line=index,
                name=name,
                characteristics=values,
                invuln_save=_invuln_after(wrap),
                base_size=base or None,
            )
        )
    return tuple(profiles)


def _invuln_after(wrap: LexborNode) -> str | None:
    """The invulnerable save printed beside one profile, or ``None``.

    Read from the siblings *between* this profile and the next, so a card with two profiles and
    one invulnerable save attaches it to the profile it is printed against rather than to both.
    """
    node = wrap.next
    while node is not None:
        if node.tag != "-text" and _has_class(node, "dsProfileBaseWrap"):
            return None
        if node.tag != "-text" and _has_class(node, "dsInvulWrap"):
            return _text(node.css_first("div.dsCharInvulValue")) or None
        node = node.next
    return None


def _weapon_profiles(card: LexborNode) -> tuple[WeaponProfile, ...]:
    """Every weapon profile, taking its section from the header row that introduces it."""
    weapons: list[WeaponProfile] = []
    line = 0
    for table in card.css("table.wTable"):
        is_melee = False
        for group in _children(table):
            if group.tag != "tbody":
                continue
            heading = _text(group.css_first("td.wTable_WEAPON")).upper()
            if heading in {_RANGED_SECTION, _MELEE_SECTION}:
                is_melee = heading == _MELEE_SECTION
                continue
            for row in group.css("tr"):
                cells = [cell for cell in _children(row) if cell.tag == "td"]
                named = next(
                    (
                        index
                        for index, cell in enumerate(cells)
                        if _has_class(cell, "wTable2_short")
                    ),
                    None,
                )
                if named is None:
                    continue
                statistics = tuple(_text(cell) for cell in cells[named + 1 :])
                if len(statistics) != len(_WEAPON_FIELDS):
                    continue
                line += 1
                weapons.append(
                    WeaponProfile(
                        line=line,
                        # The weapon-ability keywords printed after the name are their own
                        # vocabulary, not part of it — the export keeps them in a separate
                        # column, and leaving them in would make every profile's name unique.
                        name=_text_without(cells[named], "kwbw"),
                        is_melee=is_melee,
                        statistics=statistics,
                    )
                )
    return tuple(weapons)


def _keywords(card: LexborNode) -> tuple[tuple[str, str, bool], ...]:
    """``(keyword, model scope, is_faction_keyword)`` from the page's own two labelled columns.

    FR-017's faction/non-faction split is carried by the markup: the two columns of
    ``div.ds2colKW`` are labelled separately, so the split is read rather than inferred.

    Two further shapes the columns really carry:

    * **A keyword is split across several ``span.kwb`` elements** — they are line-break
      opportunities, not tokens — so the list is split on the separator the page *prints*
      (``;``), never on the span boundaries, or a two-word keyword would arrive as two.
    * **A column may hold more than one group**, separated by a horizontal rule, where each
      group after the first is labelled with the model it applies to. That label is exactly the
      export's ``model`` column, so it is read into the same field and the keyword classifier
      does not learn that two sources exist.
    """
    block = card.css_first("div.ds2colKW")
    if block is None:
        return ()
    entries: list[tuple[str, str, bool]] = []
    for column in _children(block):
        for group in _GROUP_SEPARATOR.split(column.html or ""):
            tree = LexborHTMLParser(group)
            if tree.body is None:
                continue
            label, separator, listed = _text(tree.body).partition(":")
            if not separator:
                continue
            heading = label.upper()
            is_faction = "FACTION KEYWORD" in heading
            if "KEYWORD" in heading:
                # ``KEYWORDS`` alone, or ``KEYWORDS – THE <model>`` naming what the list
                # applies to. The dash is the qualifier's only marker.
                qualifier = _KEYWORD_QUALIFIER.split(label, maxsplit=1)
                scope = qualifier[1].strip() if len(qualifier) > 1 else ""
            else:
                # A second group in the same column is labelled with the model it applies to.
                scope = label.strip()
            for keyword in listed.split(";"):
                cleaned = keyword.strip()
                if cleaned:
                    entries.append((cleaned, scope, is_faction))
    return tuple(entries)


def _split_named_abilities(node: LexborNode) -> list[tuple[str, str]]:
    """``(name, mechanic text)`` for every ability printed inside one block element.

    Several named abilities share one element, separated by a horizontal rule, so the element is
    split on that rule first. Within a segment the name is the **leading** bold run ending in a
    colon; a bold run anywhere else is emphasis inside the mechanic and is not a name.
    """
    found: list[tuple[str, str]] = []
    for segment in _GROUP_SEPARATOR.split(node.html or ""):
        tree = LexborHTMLParser(segment)
        body = tree.body
        if body is None:
            continue
        first = next((child for child in body.css("*") if child.tag in {"b", "strong"}), None)
        if first is None:
            continue
        name = _text(first).strip()
        if not name.endswith(":"):
            continue
        name = name.rstrip(":").strip()
        whole = _text(body)
        mechanic = whole[len(_text(first)) :].strip() if whole.startswith(_text(first)) else whole
        if name:
            found.append((name, mechanic))
    return found


def _abilities(block: Block) -> list[AbilityReference]:
    """One block's abilities, whichever of the two shapes the card states them in."""
    default_type = "Wargear" if block.label == WARGEAR_ABILITIES_LABEL else "Datasheet"
    found: list[AbilityReference] = []
    for node in block.nodes:
        prefix = _own_text(node).strip().rstrip(":").upper()
        referenced = node.css("[data-tooltip-content]")
        if prefix in {"CORE", "FACTION"} and referenced:
            for reference in referenced:
                match = _TOOLTIP_ID.search(reference.attributes.get("data-tooltip-content") or "")
                found.append(
                    AbilityReference(
                        name=_text(reference),
                        ability_type=prefix.title(),
                        ability_id=match.group(1) if match else "",
                    )
                )
            continue
        for name, mechanic in _split_named_abilities(node):
            found.append(
                AbilityReference(name=name, ability_type=default_type, description=mechanic)
            )
    return found


def _composition_and_costs(block: Block) -> tuple[tuple[str, ...], tuple[tuple[str, str], ...]]:
    """The composition lines and, separately, the unit-cost rows printed in the same block.

    A composition line is the list item **without** its trailing status keywords: the page prints
    ``1 <model> – EPIC HERO`` where the export publishes only the count and the name, and leaving
    the marker in would make it part of the model name the grammar resolves.

    Only the **first** cost tier is read. A datasheet priced in two tiers prints two, and both
    are keyed by model count — so reading the second would overwrite the base price with the
    requisition-threshold one. The points source is the pricing authority regardless; these rows
    exist to price a datasheet it did not publish and to notice a disagreement about one it did.

    **A tier boundary is a header row that follows a cost row, not merely a second header row.**
    Some cards repeat the heading one or more times before printing anything, and treating the
    repeat as the next tier ends the read before a single price has been taken — which is not a
    misread price but no price at all, and a datasheet with no price anywhere is the blocking
    ``REC-NEVER-PRICED``. That is what it did: of the 170 raised by the 2026-08-05 live html
    sweep, 160 were against cards whose cost table was sitting right there.
    """
    lines: list[str] = []
    costs: list[tuple[str, str]] = []
    for node in block.nodes:
        for item in node.css("ul.dsUl > li"):
            text = _text_without(item, "kwb").strip().rstrip("-–—").strip()
            if text and text.casefold() != _NONE_TEXT:
                lines.append(text)
        if costs:
            continue
        for table in node.css("table"):
            if table.css_first("td.dsUnitCostHeader") is None:
                continue
            for row in table.css("tr"):
                cells = [cell for cell in _children(row) if cell.tag == "td"]
                if any(_has_class(cell, "dsUnitCostHeader") for cell in cells):
                    if costs:
                        break  # the next tier begins; see the docstring
                    continue  # the heading, or a repeat of it before any price
                if len(cells) >= 2:
                    costs.append((_text(cells[0]), _text(cells[1])))
            break
    return tuple(lines), tuple(costs)


def _options(block: Block) -> tuple[str, ...]:
    """One description per top-level option, as **markup**, so nested choices survive.

    The inner HTML is handed on rather than the text because
    :func:`pipeline.parse.options_grammar.split_sublist` splits a stem clause from its
    alternatives on the ``<ul>`` the export also carries — so the same row shape reaches the same
    grammar from both modes, and the grammar is reused with no html-specific branch.
    """
    rows: list[str] = []
    for node in block.nodes:
        if node.tag != "ul":
            continue
        for item in _children(node):
            if item.tag != "li":
                continue
            inner = item.html or ""
            if _text(item).strip().casefold() == _NONE_TEXT:
                continue
            rows.append(_strip_outer_tag(inner))
    return tuple(rows)


def _strip_outer_tag(html: str) -> str:
    """``<li>x</li>`` -> ``x``. The element's own tag is markup *about* the row, not in it."""
    opened = html.find(">")
    closed = html.rfind("</")
    return html[opened + 1 : closed] if opened >= 0 and closed > opened else html


def _linked_datasheets(block: Block, slug: str) -> tuple[str, ...]:
    """The datasheet ids a ``LEADER`` / ``LED BY`` block names, from the page's own links."""
    linked: list[str] = []
    for node in block.nodes:
        for anchor in node.css("a[href]"):
            href = anchor.attributes.get("href") or ""
            path, _, fragment = href.partition("#")
            if not fragment:
                continue
            match = re.search(r"/factions/([^/]+)/", path)
            linked.append(detail_id(match.group(1) if match else slug, fragment))
    return tuple(dict.fromkeys(linked))


def _detachment_rules(block: Block, codes: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    """``(detachment code, rule name)`` for each rule the card's detachment block prints.

    The owning detachment is carried by a class token that is the roster's own group code
    followed by its detachment code, so only tokens that resolve against the roster are read —
    the card also carries several faction-wide tokens of the same shape, and matching them
    positionally would attach a rule to a detachment that does not exist.
    """
    rules: list[tuple[str, str]] = []
    for node in block.nodes:
        for entry in [node, *node.css("div")]:
            tokens = _class_tokens(entry) & set(codes)
            if not tokens:
                continue
            name = _text(entry.css_first("[data-tooltip-content]")) or _text(entry)
            for token in sorted(tokens):
                if name:
                    rules.append((codes[token], name))
    return tuple(dict.fromkeys(rules))


def _damaged_wounds(blocks: Sequence[Block]) -> str:
    for block in blocks:
        match = _DAMAGED_LABEL.match(block.label)
        if match is not None:
            return match.group(1).replace(" ", "")
    return ""


def detail_id(slug: str, anchor: str) -> str:
    """``<faction slug>:<anchor>`` — one datasheet's identity under this mode.

    Faction-qualified because a datacard anchor is unique on its own page and two factions do
    publish a datasheet of the same name.
    """
    return f"{slug}:{anchor}"


# -- page extraction -------------------------------------------------------------------------


def _detachment_roster(tree: LexborHTMLParser) -> tuple[tuple[Detachment, ...], dict[str, str]]:
    """The faction's detachments, and the class token that marks each one on a card."""
    roster: list[Detachment] = []
    tokens: dict[str, str] = {}
    for entry in tree.css("[data-det-code]"):
        code = (entry.attributes.get("data-det-code") or "").strip()
        name = (entry.attributes.get("data-det-name") or "").strip()
        group = (entry.attributes.get("data-det-group") or "").strip()
        if not code or not name:
            continue
        roster.append(Detachment(code=code, name=name))
        tokens[f"{group}{code}"] = code
    return tuple(dict.fromkeys(roster)), tokens


def _ability_texts(tree: LexborHTMLParser, wanted: Iterable[str]) -> dict[str, tuple[str, str]]:
    """``tooltip id -> (name, mechanic text)`` for the shared abilities the cards refer to.

    The flavour paragraph is dropped where the page marks one, because it is not a mechanic and
    including it would make an ability's digest move when its prose is re-edited and its rule is
    not.
    """
    texts: dict[str, tuple[str, str]] = {}
    for identifier in sorted(set(wanted)):
        node = tree.css_first(f"#tooltip_content{identifier}")
        if node is None:
            continue
        heading = node.css_first("div.abName")
        if heading is None:
            continue
        name = _text_without(heading, "h_number")
        mechanic = _text_without(node, "abNameWrap", "abLegend", "abIcon")
        texts[identifier] = (name, mechanic)
    return texts


def parse_faction_page(slug: str, html: str) -> DatacardPage:
    """Parse one faction's datacard page.

    Raises:
        HtmlStructureError: the page carries no datacard, or a block every card is required to
            carry is missing from one — either of which would otherwise be a quiet, partial
            extraction (FR-008).
    """
    tree = LexborHTMLParser(html)
    cards = tree.css(CARD_SELECTOR)
    if not cards:
        raise HtmlStructureError(
            f"the faction page for {slug!r} carries no {CARD_SELECTOR} element; the datacard "
            "layout has moved and no datasheet would be extracted from it"
        )

    detachments, det_tokens = _detachment_roster(tree)
    extracted: list[Datacard] = []
    unconsumed: set[str] = set()
    referenced: set[str] = set()

    for card in cards:
        card_blocks = blocks_of(card)
        labels = {block.label for block in card_blocks}
        missing = [label for label in REQUIRED_CARD_LABELS if label not in labels]
        if missing:
            raise HtmlStructureError(
                f"a datacard on the {slug!r} page carries no {missing[0]!r} block; the label was "
                "present on every card the T002 markup spike measured, so its absence is a "
                "structural change upstream rather than a quirk of one datasheet"
            )
        if card.css_first("div.ds2colKW") is None:
            raise HtmlStructureError(
                f"a datacard on the {slug!r} page carries no keyword block; the FR-017 "
                "faction/non-faction split is carried by that element and by nothing else"
            )

        name = _card_name(card)
        anchor = _card_anchor(card)
        abilities: list[AbilityReference] = []
        composition: tuple[str, ...] = ()
        costs: tuple[tuple[str, str], ...] = ()
        options: tuple[str, ...] = ()
        leads: tuple[str, ...] = ()
        led_by: tuple[str, ...] = ()
        rules: tuple[tuple[str, str], ...] = ()

        for block in card_blocks:
            if block.label in {ABILITIES_LABEL, WARGEAR_ABILITIES_LABEL}:
                abilities.extend(_abilities(block))
            elif block.label == COMPOSITION_LABEL:
                composition, costs = _composition_and_costs(block)
            elif block.label == OPTIONS_LABEL:
                options = _options(block)
            elif block.label == LEADER_LABEL:
                leads = _linked_datasheets(block, slug)
            elif block.label == LED_BY_LABEL:
                led_by = _linked_datasheets(block, slug)
            elif block.label == DETACHMENT_ABILITY_LABEL:
                rules = _detachment_rules(block, det_tokens)
            elif _DAMAGED_LABEL.match(block.label) is None:
                unconsumed.add(block.label)

        referenced.update(ability.ability_id for ability in abilities if ability.ability_id)
        extracted.append(
            Datacard(
                detail_id=detail_id(slug, anchor or _slug_fallback(name)),
                name=name,
                faction_id=slug,
                is_legends=_has_class(card, "sLegendary"),
                damaged_wounds=_damaged_wounds(card_blocks),
                models=_model_profiles(card, name),
                weapons=_weapon_profiles(card),
                keywords=_keywords(card),
                abilities=tuple(abilities),
                composition=composition,
                options=options,
                costs=costs,
                leads=leads,
                led_by=led_by,
                detachment_rules=rules,
            )
        )

    return DatacardPage(
        faction_slug=slug,
        faction_name=slug,
        cards=tuple(extracted),
        detachments=detachments,
        ability_texts=_ability_texts(tree, referenced),
        unconsumed_labels=tuple(sorted(unconsumed)),
    )


def _slug_fallback(name: str) -> str:
    """A datasheet id when the page prints no anchor: its own name, punctuation removed."""
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-") or "unnamed"


# -- record emission -------------------------------------------------------------------------


def _result(file_name: str, records: Sequence[Mapping[str, str]]) -> CsvReadResult:
    """One emitted table, in the record shape the csv reader produces.

    ``line_number`` counts from 2 exactly as the reader's does — a header line, then the records
    — so a diagnostic naming a row means the same thing whichever mode produced it.
    """
    fields = EMITTED_TABLES[file_name]
    return CsvReadResult(
        file_name=file_name,
        field_names=fields,
        rows=tuple(
            WahapediaRow(
                file_name=file_name,
                line_number=index,
                fields={name: record.get(name, "") for name in fields},
            )
            for index, record in enumerate(records, start=2)
        ),
        repairs=0,
        findings=(),
    )


def emit_records(
    pages: Sequence[DatacardPage], *, edition_code: str = ""
) -> dict[str, CsvReadResult]:
    """Turn extracted pages into the export-shaped tables every stage below already reads."""
    tables: dict[str, list[dict[str, str]]] = {name: [] for name in EMITTED_TABLES}

    tables["Source.csv"] = [
        {
            "id": LEGENDS_SOURCE_ID,
            "name": "Legends",
            "type": "legends",
            "edition": edition_code,
        },
        {"id": CURRENT_SOURCE_ID, "name": "Faction Pack", "type": "pack", "edition": edition_code},
    ]

    for page in pages:
        tables["Factions.csv"].append(
            {"id": page.faction_slug, "name": page.faction_name, "link": ""}
        )
        for detachment in page.detachments:
            tables["Detachments.csv"].append(
                {
                    "id": detachment.code,
                    "faction_id": page.faction_slug,
                    "name": detachment.name,
                    "legend": "",
                    "type": "",
                }
            )
        for identifier, (name, description) in sorted(page.ability_texts.items()):
            tables["Abilities.csv"].append(
                {
                    "id": identifier,
                    "name": name,
                    "legend": "",
                    "faction_id": page.faction_slug,
                    "description": description,
                }
            )

        rules_seen: set[tuple[str, str]] = set()
        for card in page.cards:
            _emit_card(card, tables)
            for code, rule_name in card.detachment_rules:
                if (code, rule_name) in rules_seen:
                    continue
                rules_seen.add((code, rule_name))
                tables["Detachment_abilities.csv"].append(
                    {
                        "id": f"{code}-{_slug_fallback(rule_name).lower()}",
                        "detachment_id": code,
                        "name": rule_name,
                        "legend": "",
                        "description": "",
                    }
                )

    return {name: _result(name, records) for name, records in tables.items()}


def _emit_card(card: Datacard, tables: dict[str, list[dict[str, str]]]) -> None:
    """One datacard's rows, spread across the tables the export splits them over."""
    tables["Datasheets.csv"].append(
        {
            "id": card.detail_id,
            "name": card.name,
            "faction_id": card.faction_id,
            "source_id": LEGENDS_SOURCE_ID if card.is_legends else CURRENT_SOURCE_ID,
            "role": "",
            "damaged_w": card.damaged_wounds,
            "legend": "",
        }
    )
    for model in card.models:
        movement, toughness, save, wounds, leadership, control = model.characteristics
        tables["Datasheets_models.csv"].append(
            {
                "datasheet_id": card.detail_id,
                "line": str(model.line),
                "name": model.name,
                "M": movement,
                "T": toughness,
                "Sv": save,
                "inv_sv": model.invuln_save or "",
                "W": wounds,
                "Ld": leadership,
                "OC": control,
                "base_size": model.base_size or "",
            }
        )
    for weapon in card.weapons:
        row = {
            "datasheet_id": card.detail_id,
            "line": str(weapon.line),
            "name": weapon.name,
            "type": "Melee" if weapon.is_melee else "Ranged",
        }
        row.update(dict(zip(_WEAPON_FIELDS, weapon.statistics, strict=True)))
        tables["Datasheets_wargear.csv"].append(row)
    for keyword, scope, is_faction in card.keywords:
        tables["Datasheets_keywords.csv"].append(
            {
                "datasheet_id": card.detail_id,
                "keyword": keyword,
                "model": scope,
                "is_faction_keyword": "true" if is_faction else "false",
            }
        )
    for line, ability in enumerate(card.abilities, start=1):
        tables["Datasheets_abilities.csv"].append(
            {
                "datasheet_id": card.detail_id,
                "line": str(line),
                "ability_id": ability.ability_id,
                "model": "",
                "name": ability.name,
                "description": ability.description,
                "type": ability.ability_type,
            }
        )
    for line, description in enumerate(card.composition, start=1):
        tables["Datasheets_unit_composition.csv"].append(
            {"datasheet_id": card.detail_id, "line": str(line), "description": description}
        )
    for line, description in enumerate(card.options, start=1):
        tables["Datasheets_options.csv"].append(
            {
                "datasheet_id": card.detail_id,
                "line": str(line),
                "button": "Wargear Options",
                "description": description,
            }
        )
    for line, (label, price) in enumerate(card.costs, start=1):
        tables["Datasheets_models_cost.csv"].append(
            {
                "datasheet_id": card.detail_id,
                "line": str(line),
                "description": label,
                "cost": price,
            }
        )
    for target in card.leads:
        tables["Datasheets_leader.csv"].append({"leader_id": card.detail_id, "attached_id": target})
    for leader in card.led_by:
        tables["Datasheets_leader.csv"].append({"leader_id": leader, "attached_id": card.detail_id})


def read_datacard_payloads(
    payloads: Sequence[FixturePayload], *, edition_code: str = ""
) -> dict[str, CsvReadResult]:
    """The ``html``-mode reader: acquired faction pages in, export-shaped tables out.

    The counterpart of :func:`pipeline.parse.wahapedia_csv.read_text` over the whole acquisition,
    and the reason the two modes are interchangeable below ``acquire``: both return the same
    ``file name -> CsvReadResult`` mapping, and nothing downstream asks which one ran.
    """
    pages = [parse_faction_page(payload.name, payload.text) for payload in payloads]
    return emit_records(pages, edition_code=edition_code)
