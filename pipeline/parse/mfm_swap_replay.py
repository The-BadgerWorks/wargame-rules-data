# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the deferred-placeholder replay
# (task T057): each $RS("S:a","P:b") is applied as an explicit id-to-id move of the hidden
# block's children into the placeholder, and any unfilled placeholder or unclaimed source block
# fails the run as a structural breakage (FR-008, research D4a).
"""Reconstruct the points source's finished DOM in-process.

The page ships every value we need in **one** HTTP response. What is deferred is not the
content but its *placement*: the grid carries empty ``<template id="P:n">`` holes, and later in
the same response come ``<div hidden id="S:n">`` blocks each followed by an instruction naming
both ends of the move. Replaying those instructions reconstructs the finished tree exactly,
with no browser and no JavaScript engine.

**Why this is the most important module in the parser.** The obvious alternative — zip
document-ordered unit names against document-ordered ``pts`` values — mis-prices an entire
faction by one row when a single fragment is absent, and nothing detects it. Here the pairing is
carried *by the page itself*, so there is no ordering assumption to be wrong about.

Two instruction forms appear, and they take their arguments the other way round from each other:

``$RS("S:a","P:b")``
    The streamed-content swap. The page's own definition removes ``S:a`` from its parent, moves
    its children in before ``P:b``, then removes ``P:b`` — i.e. *replace the placeholder with
    the source block's children*.

``$RC("B:a","S:b")``
    The suspense-boundary reveal, whose real implementation schedules the same effect through an
    animation frame. Same outcome, arguments reversed: the **placeholder** is named first.

Both reduce to one operation, which is why this module has one.

**Totality is the safety property.** After every instruction has been applied, no ``<template>``
may remain and no ``hidden`` source block may be left over. Either condition means some value on
the page is unknowable, and FR-008 requires the run to stop rather than publish the rest.

> **Principle 14 exception (recorded in research D4a).** This module re-implements a small piece
> of another system's client-side behaviour, which is normally exactly the sort of thing to
> avoid. The alternative is a headless browser in CI — a heavyweight, slow, non-deterministic
> dependency executing JavaScript we have shown we do not need. The replay is about thirty lines
> and is total by construction; the browser is neither.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from selectolax.lexbor import LexborHTMLParser, LexborNode

from pipeline.acquire.http import AcquisitionError
from pipeline.exit_codes import ExitCode

#: ``$RS("S:a","P:b")`` — source named first, placeholder second.
_RS_CALL: Final = re.compile(r"\$RS\(\s*[\"']([^\"']+)[\"']\s*,\s*[\"']([^\"']+)[\"']\s*\)")

#: ``$RC("B:a","S:b")`` — placeholder named first, source second.
_RC_CALL: Final = re.compile(r"\$RC\(\s*[\"']([^\"']+)[\"']\s*,\s*[\"']([^\"']+)[\"']\s*\)")

#: Comments are dropped before parsing. The page's own streaming markers (``<!--$?-->``) are
#: presentation, and a fixture's header comment may legitimately *describe* an instruction
#: without being one — reading either as content is how a document ends up executing its own
#: documentation.
_COMMENT: Final = re.compile(r"<!--.*?-->", re.DOTALL)


class StructureChanged(AcquisitionError):
    """Values can no longer be extracted reliably from the points source (FR-008).

    Raised for an unfilled placeholder, an unclaimed source block, or an instruction naming an
    element the response does not contain. All three mean the same thing operationally: the
    parser's assumptions about the page no longer hold, so the run stops and a human looks at it.
    """

    finding_code = "SRC-STRUCTURE-CHANGED"
    exit_code = ExitCode.SOURCE_STRUCTURE_CHANGED


@dataclass(frozen=True, slots=True)
class ReplayResult:
    """The reconstructed document plus the evidence that reconstruction was total."""

    html: str
    swaps_applied: int
    unfilled_placeholders: tuple[str, ...]
    unclaimed_sources: tuple[str, ...]


def _instructions(tree: LexborHTMLParser) -> list[tuple[str, str]]:
    """Every move instruction in the response, in document order, as ``(source_id, target_id)``.

    Read from ``<script>`` **elements**, never from the raw response text. A regex over the
    whole document also matches an instruction quoted inside a comment — which is how a fixture
    that merely *describes* the mechanism ends up being executed by it.

    Order matters and is the page's, not ours: a source block may itself carry a placeholder that
    a later instruction fills, so the instructions are a sequence rather than a set.
    """
    instructions: list[tuple[str, str]] = []
    for script in tree.css("script"):
        text = script.text(deep=True, strip=False)
        if not text:
            continue
        found: list[tuple[int, tuple[str, str]]] = []
        found.extend((m.start(), (m.group(1), m.group(2))) for m in _RS_CALL.finditer(text))
        found.extend((m.start(), (m.group(2), m.group(1))) for m in _RC_CALL.finditer(text))
        instructions.extend(pair for _, pair in sorted(found, key=lambda item: item[0]))
    return instructions


def _by_id(tree: LexborHTMLParser, element_id: str) -> LexborNode | None:
    return tree.css_first(f'[id="{element_id}"]')


def _apply(source: LexborNode, target: LexborNode) -> None:
    """Replace ``target`` with ``source``'s children, then discard both wrappers.

    ``insert_before`` on a node that is itself being moved invalidates the iterator, so the
    children are snapshotted first. ``<template>`` content lives in a separate document fragment
    in a real browser; here the placeholder is always empty, so replacing the node is exact.
    """
    children = list(source.iter(include_text=True))
    for child in children:
        target.insert_before(child)
    target.decompose(recursive=False)
    source.decompose(recursive=False)


def replay(html: str) -> ReplayResult:
    """Reconstruct the finished DOM, or raise :class:`StructureChanged`.

    The return value carries the leftovers even though a non-empty leftover always raises —
    a caller that wants to *report* on structure without failing can catch and inspect, and the
    dataclass documents what "total" means without anyone having to read the loop.
    """
    tree = LexborHTMLParser(_COMMENT.sub("", html))
    instructions = _instructions(tree)

    applied = 0
    for source_id, target_id in instructions:
        source = _by_id(tree, source_id)
        target = _by_id(tree, target_id)
        if source is None or target is None:
            missing = source_id if source is None else target_id
            raise StructureChanged(
                f"the points source names element {missing!r} in a move instruction but the "
                f"response does not contain it ({len(instructions)} instructions, {applied} "
                f"applied before this one)"
            )
        _apply(source, target)
        applied += 1

    # The instructions have been consumed; the scripts that carried them are not content, and
    # keeping the publisher's JavaScript in the reconstructed tree serves nothing downstream.
    for script in tree.css("script"):
        script.decompose(recursive=True)

    unfilled = tuple(node.attributes.get("id") or "<anonymous>" for node in tree.css("template"))
    unclaimed = tuple(
        node.attributes.get("id") or "<anonymous>"
        for node in tree.css("div[hidden]")
        if node.attributes.get("id")
    )

    if unfilled or unclaimed:
        raise StructureChanged(
            "the points source's deferred-content structure changed: "
            f"{len(unfilled)} placeholder(s) still unfilled {sorted(unfilled)} and "
            f"{len(unclaimed)} source block(s) claimed by no placeholder {sorted(unclaimed)} "
            f"after replaying {applied} of {len(instructions)} instruction(s)"
        )

    return ReplayResult(
        html=tree.html or "",
        swaps_applied=applied,
        unfilled_placeholders=unfilled,
        unclaimed_sources=unclaimed,
    )
