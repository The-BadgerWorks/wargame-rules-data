# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the wargear-option grammar of
# 004 research D3 (004 task T028): the `<li>` split ahead of the clause grammar, the clause
# head and verb table with its measured frequencies, the `with N` quantifier, and the residual
# marker that makes a vocabulary shift a coverage figure rather than missing data.
"""Resolve one wargear-option row into a group scope and its choices.

The source publishes one row per option, as free text with an optional ``<li>`` sub-list, **no
cost column and no foreign key to a wargear row** (research D3). This module turns that into
structure, or says it could not.

**The `<li>` split happens before the clause grammar.** 1 025 of 2 832 measured rows are a stem
clause plus N alternatives, and running the clause grammar over the whole string first would
read the first alternative as part of the stem. The split matches ``<\\s*ul`` rather than
``<ul>``: the export emits unclosed and space-variant forms — 2 050 occurrences, exactly one of
which is the literal string ``<ul>``.

**The clause table is closed, and short** (research D3):

============================  =================================  ======
Production                    Maps to                            Rows
============================  =================================  ======
``^This model``               ``scope = model``                   1 353
``^Any number of ...models``  ``scope = unit``                      243
``^For every INT models``     ``scope = per_n_models``              198
``^INT `` / ``^The``          ``scope = unit``                      452
``can be replaced with``      replacement choice                  1 198
``can be equipped with``      additive choice                       816
``with INT``                  ``count = INT``                     1 413
============================  =================================  ======

Productions **deliberately not built**, because they are verified absent from the baseline (0
occurrences each): ``may``, ``may replace``, ``1 in N``, lowercase ``for every``, ``only one``.
The baseline text is heavily normalised — **but the parser must not assume that holds under the
current edition**, so an unmatched row returns ``None`` and the caller raises the advisory
``OPT-UNPARSED``. A vocabulary shift then shows up as a falling coverage figure rather than as
data that quietly stopped being extracted.

**A head alone is not enough.** A row whose head matches but whose text carries neither verb
yields no object to name a choice with, and inventing one would be the guess this whole design
exists to avoid. It is reported as unparsed on the same terms.

Like :mod:`pipeline.parse.composition_grammar`, this module is **mode-blind**: it takes a
description *string*, so `csv` mode and `html` mode (task T073) feed it identically.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from pipeline.models.curated import OptionScope, WargearOptionState
from pipeline.parse.composition_grammar import pre_pass

#: The sub-list opener. ``<\s*ul``, never ``<ul>`` — see the module docstring.
_SUBLIST: Final = re.compile(r"<\s*ul", re.IGNORECASE)

#: One alternative inside the sub-list. The closing tag is optional in the export.
_ITEM: Final = re.compile(r"<\s*li\s*/?\s*>", re.IGNORECASE)

#: Clause heads, in the fixed order they are tried. ``For every`` is tried ahead of the bare
#: ``^INT`` head it would otherwise never reach, and ``Any number of`` ahead of nothing in
#: particular — the order is fixed so the same input picks the same production on every run.
_HEADS: Final[tuple[tuple[re.Pattern[str], OptionScope], ...]] = (
    (re.compile(r"^This model\b"), OptionScope.MODEL),
    (re.compile(r"^For every (\d+) models\b"), OptionScope.PER_N_MODELS),
    (re.compile(r"^Any number of\b.*\bmodels\b"), OptionScope.UNIT),
    (re.compile(r"^\d+ "), OptionScope.UNIT),
    (re.compile(r"^The\b"), OptionScope.UNIT),
)

#: Forms that a **built** production would otherwise swallow, refused before the head table.
#:
#: ``1 in every N models can be equipped with …`` matches the bare ``^INT`` head perfectly well
#: and resolves to a unit-scoped group — publishing "any model may take this" where the rule is
#: "one model in three may". The permissive forms are the same story for the verb: research D3
#: verified ``may`` and ``may replace`` absent from the baseline and deliberately built no
#: production for them, and a refusal is what keeps that decision honest if they reappear.
#:
#: **These are refusals, not productions.** Each one sends its row to ``OPT-UNPARSED``, where a
#: human sees it; none of them resolves anything.
_REFUSED: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"^\d+\s+in\s+(?:every\s+)?\d+\b", re.IGNORECASE),
    re.compile(r"\bmay\b", re.IGNORECASE),
)

#: The two verbs, and what a choice under each one *is*. Substring searches, exactly as research
#: D3 counted them, because the object of the clause is whatever follows the phrase.
_REPLACE_VERB: Final = "can be replaced with"
_EQUIP_VERB: Final = "can be equipped with"

#: ``with INT``: the count the clause grants. Applied to the clause's object, where the integer
#: is the first token after the verb phrase.
_LEADING_COUNT: Final = re.compile(r"^(\d+)\s+(\S.*)$")

#: An explicit "no change" alternative, in normalised form. It carries ``is_no_change`` and
#: **never** a price — publishing one priced would present "take nothing" as a purchasable item.
_NO_CHANGE: Final = "no change"

#: The label a "no change" alternative is published under. Fixed here rather than taken from the
#: source, so every such choice reads identically across every datasheet.
NO_CHANGE_NAME: Final = "No change"

#: The ceiling the curated schema puts on a choice ``name``.
MAX_CHOICE_NAME_CHARS: Final = 120


class OptionVerb(StrEnum):
    """What the clause does with its object."""

    REPLACE = "replace"
    EQUIP = "equip"


@dataclass(frozen=True, slots=True)
class OptionChoiceParse:
    """One selectable alternative, before it is linked or priced."""

    name: str
    count: int | None = None
    is_no_change: bool = False
    verb: OptionVerb = OptionVerb.EQUIP


@dataclass(frozen=True, slots=True)
class OptionRowParse:
    """One source option row, resolved into a group and its choices."""

    scope: OptionScope
    scope_n: int | None
    choices: tuple[OptionChoiceParse, ...]


def group_id(datasheet_id: str, line: int) -> str:
    """``og-<datasheet-stem>-<line>`` — derived from the source's own row ordinal (FR-015).

    The ordinal is unique per ``(datasheet_id, line)`` and involves zero inference, which is
    what makes the identity stable across snapshots and an upstream relabelling a **rename**
    (same id, changed choice names) rather than a removal plus an addition.
    """
    return f"og-{datasheet_id.removeprefix('ds-')}-{line}"


def choice_id(group: str, index: int) -> str:
    """``oc-<group-stem>-<index>``, with ``index`` 1-based in the source's own order."""
    return f"oc-{group.removeprefix('og-')}-{index}"


def split_sublist(raw: str) -> tuple[str, tuple[str, ...]]:
    """Split one row into its stem clause and its ``<li>`` alternatives, before any parsing."""
    opener = _SUBLIST.search(raw)
    if opener is None:
        return raw, ()
    stem, remainder = raw[: opener.start()], raw[opener.end() :]
    items = [segment for segment in _ITEM.split(remainder)[1:] if segment.strip()]
    return stem, tuple(items)


def parse_row(description: str) -> OptionRowParse | None:
    """Resolve one option row, or ``None`` when it matched no production.

    ``None`` is the residual, and the caller reports it as ``OPT-UNPARSED`` rather than dropping
    the row: a row nobody can see is a row nobody fixes.
    """
    stem_raw, item_raw = split_sublist(description)
    stem = pre_pass(stem_raw, field="option.description")
    if not stem or any(pattern.search(stem) for pattern in _REFUSED):
        return None

    head = _match_head(stem)
    if head is None:
        return None
    scope, scope_n = head

    verb, object_clause = _match_verb(stem)
    if verb is None:
        return None

    choices: list[OptionChoiceParse] = []
    if item_raw:
        for item in item_raw:
            choice = _parse_object(pre_pass(item, field="option.choice"), verb)
            if choice is None:
                return None
            choices.append(choice)
    else:
        choice = _parse_object(object_clause, verb)
        if choice is None:
            return None
        choices.append(choice)

    return OptionRowParse(scope=scope, scope_n=scope_n, choices=tuple(choices))


def _match_head(stem: str) -> tuple[OptionScope, int | None] | None:
    for pattern, scope in _HEADS:
        match = pattern.match(stem)
        if match is None:
            continue
        if scope is OptionScope.PER_N_MODELS:
            return scope, int(match.group(1))
        return scope, None
    return None


def _match_verb(stem: str) -> tuple[OptionVerb | None, str]:
    """The clause's verb and the text following it.

    ``replace`` is tested first: a row carrying both phrases is describing a replacement whose
    alternatives are then equipped, and reading it as additive would publish an upgrade the
    player has not paid for a swap to take.
    """
    for phrase, verb in ((_REPLACE_VERB, OptionVerb.REPLACE), (_EQUIP_VERB, OptionVerb.EQUIP)):
        index = stem.find(phrase)
        if index >= 0:
            return verb, stem[index + len(phrase) :].strip()
    return None, ""


def _parse_object(text: str, verb: OptionVerb) -> OptionChoiceParse | None:
    """One clause object — ``with INT name``, ``name``, or an explicit "no change"."""
    cleaned = text.strip().rstrip(".;,:").strip()
    if not cleaned:
        return None

    if cleaned.casefold() == _NO_CHANGE:
        return OptionChoiceParse(name=NO_CHANGE_NAME, is_no_change=True, verb=verb)

    counted = _LEADING_COUNT.match(cleaned)
    count = int(counted.group(1)) if counted else None
    name = (counted.group(2) if counted else cleaned).strip()
    if not name or len(name) > MAX_CHOICE_NAME_CHARS:
        return None
    return OptionChoiceParse(name=name, count=count, verb=verb)


def choice_names(parsed: OptionRowParse) -> Sequence[str]:
    """The parsed choice names, in source order — a convenience for reports and tests."""
    return [choice.name for choice in parsed.choices]


def option_state(*, row_count: int, unparsed_count: int) -> WargearOptionState:
    """The three-state rule of FR-016, as one function so it cannot be spelled twice.

    ``none`` when the source describes no options, ``extracted`` when every row resolved, and
    ``partial`` when at least one did not — what resolved still ships. The **fourth** state is
    the absence of a value altogether, which means the source was not consulted, and that is
    the caller's decision to make: this function is only ever asked about a datasheet whose
    option rows were read.
    """
    if row_count == 0:
        return WargearOptionState.NONE
    return WargearOptionState.PARTIAL if unparsed_count else WargearOptionState.EXTRACTED
