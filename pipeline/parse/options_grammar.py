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
from collections.abc import Callable, Mapping, Sequence
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


# -- `006-unit-loadout-fidelity`: everything below is appended AFTER every `004` production ------
#
# **The ordering is the guarantee, not a convention.** :func:`_match_head` runs the `004` table
# to exhaustion before it looks at ``_EXTENDED_HEADS``, and :func:`_match_verb` runs `004`'s two
# verbs before ``_DISTRIBUTIVE_REPLACE``. A row the baseline resolved therefore never reaches a
# line of `006` code, which is FR-009 made structural: there is no path by which a new production
# can change an old result, so the zero-regression claim does not rest on a test remembering to
# cover a row (research D5, layer 0).
#
# The vocabulary is the **live corpus's**, measured by ``tools/option_taxonomy.py`` into
# ``reports/option-taxonomy/2026-08-10.md`` over 2 452 rows, and not research D1's ≈81 % sample.
# Where the two disagree the measurement wins; where the measurement says zero, no production is
# built, so a vocabulary shift shows up as a falling coverage figure rather than as a guess.

#: The distributive replace verb — research D1b class 1, **283 of 571 unparsed rows (49.6 %)**
#: and the single highest-yield production in the feature (T016). The possessive side is captured
#: rather than discarded: it names what the eligible models give up, and it is the only place the
#: sentence states it.
_DISTRIBUTIVE_REPLACE: Final = re.compile(
    r"can each have\s+(?P<side>.+?)\s+replaced with\b", re.IGNORECASE
)

#: Determiners the possessive side opens with. Stripped so the side reads as item names; the
#: strip is a fixed closed list rather than a "leading word" rule, because a leading word is
#: sometimes the item.
_POSSESSIVE: Final = re.compile(r"^(?:its|their|the|this model's|this model’s)\s+", re.IGNORECASE)

#: A footnote marker glued to a model name inside the stem — 24 measured rows carry one. A head
#: that cannot read past it loses the row to a typographic convention.
_FOOTNOTE_MARK: Final = re.compile(r"[*†‡¹²³]+")

#: The apostrophe, in both forms the source uses. NFKC does not fold ``’`` to ``'``, so a
#: production spelling only one of them matches roughly half the possessive heads it should.
_APOS: Final = r"['’]"

#: A model-name phrase inside a head: title-cased words, which is how the source names a model.
_MODEL: Final = r"[A-Z][\w'’-]*(?:[ -][A-Z][\w'’-]*)*"

#: Forms an ``_EXTENDED_HEADS`` production would otherwise swallow, refused before that table is
#: reached — and **only** before that table, so no row the `004` heads resolve can see them.
#:
#: Both classes state a **predicate** the curated schema has nowhere to hold: a unit-size or
#: equipment condition on whether the option is available at all. Resolving one would publish
#: "any unit may take this" where the source says "a unit of six or more may", which is the
#: over-grant this feature exists to stop, not a coverage figure worth having. Research D1c.5
#: makes the same ruling for class 9's verbless conditionals; these are the same predicate
#: wearing a verb, and they stay ``OPT-UNPARSED`` and curator-override material.
#:
#: Measured: 27 conditional rows and 14 equipment-qualified subjects, of class 2's 105.
_EXTENDED_REFUSED: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"^(?:If|Unless)\b", re.IGNORECASE),
    re.compile(r"^[^,]*\bequipped with\b.*\bcan be\b", re.IGNORECASE),
    re.compile(r"^For each\b", re.IGNORECASE),
)


@dataclass(frozen=True, slots=True)
class _Head:
    """What a head production resolves to, beyond the scope `004` already carries."""

    scope: OptionScope
    scope_n: int | None = None
    eligible_model_name: str | None = None
    eligible_max_count: int | None = None
    is_per_model: bool | None = None


def _scoped_max(match: re.Match[str]) -> _Head:
    """``Up to INT <MODEL>`` — class 1c, 41 rows. The cap is the *model's*, not the unit's."""
    return _Head(
        scope=OptionScope.UNIT,
        eligible_model_name=_model_name(match.group(2)),
        eligible_max_count=int(match.group(1)),
    )


def _named_subset(match: re.Match[str]) -> _Head:
    """``Any number of <MODEL>`` — class 1b, 42 rows. A subset with no cap."""
    return _Head(scope=OptionScope.UNIT, eligible_model_name=_model_name(match.group(1)))


def _whole_unit(_match: re.Match[str]) -> _Head:
    """``All models in this unit`` / ``This unit`` — no subset and no cap."""
    return _Head(scope=OptionScope.UNIT)


def _this_model_items(_match: re.Match[str]) -> _Head:
    """``Each of this model's <ITEM>`` — 21 rows. One model, distributed over its own weapons."""
    return _Head(scope=OptionScope.MODEL)


def _one_named(match: re.Match[str]) -> _Head:
    """``One <MODEL>'s <ITEM>`` / ``One <MODEL>`` — a subset of exactly one, by name."""
    return _Head(
        scope=OptionScope.UNIT,
        eligible_model_name=_model_name(match.group(1)),
        eligible_max_count=1,
    )


def _one_anonymous(_match: re.Match[str]) -> _Head:
    """``One model's <ITEM>`` / ``One model`` — a subset of exactly one, unnamed."""
    return _Head(scope=OptionScope.UNIT, eligible_max_count=1)


def _each_named(match: re.Match[str]) -> _Head:
    """``Each <MODEL>`` — every model of a named type, which is distributive by construction."""
    return _Head(
        scope=OptionScope.UNIT,
        eligible_model_name=_model_name(match.group(1)),
        is_per_model=True,
    )


def _each_model(_match: re.Match[str]) -> _Head:
    """``Each model's <ITEM>`` — every model of the unit, distributively."""
    return _Head(scope=OptionScope.UNIT, is_per_model=True)


def _per_named(match: re.Match[str]) -> _Head:
    """``For every INT <MODEL> in this unit,`` — `004`'s ratio head with a named model."""
    return _Head(scope=OptionScope.PER_N_MODELS, scope_n=int(match.group(1)))


#: The `006` head table, tried in this fixed order **only after** every `004` head has failed.
#: The order is fixed so the same input picks the same production on every run, and the more
#: specific possessive forms are tried ahead of the bare ones they would otherwise lose to.
#:
#: T017 builds the first three (research D1b classes 1b, 1c, 1e); T055 builds the rest, which are
#: class 2's measured heads — a family whose verb `004` already carried and whose head it did not.
_EXTENDED_HEADS: Final[tuple[tuple[re.Pattern[str], Callable[[re.Match[str]], _Head]], ...]] = (
    # -- T017: the distributive-replace family's heads (classes 1b, 1c, 1e) --------------------
    (re.compile(rf"^Up to (\d+)\s+({_MODEL}|models?)\b"), _scoped_max),
    (re.compile(r"^All models in this unit\b", re.IGNORECASE), _whole_unit),
    (re.compile(rf"^Any number of ({_MODEL})\b"), _named_subset),
    # -- T055: class 2's measured heads ---------------------------------------------------------
    (re.compile(rf"^(?:Each|Both) of this model{_APOS}s\b", re.IGNORECASE), _this_model_items),
    (re.compile(rf"^One model{_APOS}s\b", re.IGNORECASE), _one_anonymous),
    (re.compile(rf"^(?:One|An?) ({_MODEL}){_APOS}s\b"), _one_named),
    (re.compile(r"^One model\b", re.IGNORECASE), _one_anonymous),
    (re.compile(rf"^One ({_MODEL})\b"), _one_named),
    (re.compile(r"^This unit\b", re.IGNORECASE), _whole_unit),
    (re.compile(rf"^Each model{_APOS}s\b", re.IGNORECASE), _each_model),
    (re.compile(rf"^Each ({_MODEL})\b"), _each_named),
    (re.compile(rf"^For every (\d+) (?:{_MODEL})s? in this unit\b"), _per_named),
)

#: The group-level select quantifier (T019), **derived from the corpus and not from research
#: D1d**. D1d's skeletons were digit-shaped and matched zero rows for one reason: this corpus
#: states the quantifier as a *word* numeral. Measured: ``up to two of the following`` 21 rows,
#: ``up to three of the following`` 4, ``any of the following`` 1 (a cap of nothing, so no value).
#: ``INT different <ITEM> from the following`` — D1d's other skeleton — is **0 rows and is
#: deliberately not built**, on exactly the terms `004` refused ``may`` and ``1 in N``.
#:
#: ``one of the following:`` is the boilerplate 174 stems end with and is **not** a cap of one.
_SELECT_QUANTIFIER: Final = re.compile(
    r"\bup to (?P<count>one|two|three|four|five|six|seven|eight|nine|ten|\d+) of the following\b",
    re.IGNORECASE,
)

#: The word numerals the quantifier uses. A closed list, because a general number-word parser
#: would resolve forms the corpus does not state and has therefore never been measured.
_NUMERALS: Final[Mapping[str, int]] = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

#: A conjunct boundary on the **granted** side: ``and INT <ITEM>``. The leading integer is the
#: evidence a second item started (research D1d measured 137 rows of it). Without one, ``and`` is
#: part of the name, and splitting on it would invent an item the source does not name.
_GRANTED_CONJUNCT: Final = re.compile(r"\s+and\s+(?=\d+\s+\S)", re.IGNORECASE)

#: A conjunct boundary on the **replaced** side. The possessive side lists the model's own
#: weapons and states no counts, so a bare ``and`` — or a semicolon — is the only boundary the
#: source gives. An item that splits wrongly links to nothing and is reported
#: ``OPT-BUNDLE-UNLINKED``, which is the visible failure; not splitting at all is the invisible
#: one this feature exists to remove.
_REPLACED_CONJUNCT: Final = re.compile(r"\s+and\s+|\s*;\s*", re.IGNORECASE)


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
class ItemParse:
    """One item on one side of one choice, before it is linked (`006` FR-005, FR-006).

    ``count`` is the conjunct's own leading integer and is **omitted when the source states
    none** — never defaulted to 1, because absence means the source said nothing.
    """

    name: str
    count: int | None = None


@dataclass(frozen=True, slots=True)
class OptionRowParse:
    """One source option row, resolved into a group and its choices.

    Every field below ``choices`` is `006`'s, and every one of them defaults to ``None``. That
    is the structural half of FR-009: a row `004` resolved takes no new production, so it takes
    no new value either, and the layer-1 harness's golden literals keep comparing equal without
    being edited.
    """

    scope: OptionScope
    scope_n: int | None
    choices: tuple[OptionChoiceParse, ...]
    # -- `006` §2.1: the eligibility scope ------------------------------------------------------
    eligible_model_name: str | None = None
    eligible_max_count: int | None = None
    is_per_model: bool | None = None
    # -- `006` §2.2: the group-level select quantifier ------------------------------------------
    min_choices: int | None = None
    max_choices: int | None = None
    #: The possessive side of a distributive replace stem — what the eligible models give **up**,
    #: which the clause names in its own head rather than after its verb. ``None`` for every
    #: production `004` carries, whose object clause is the only side it states.
    replaced_clause: str | None = None


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

    verb, object_clause, replaced_clause = _match_verb(stem)
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

    # A distributive verb makes the group per-model whatever its head said; a head that is
    # distributive in itself says so too. Neither is ever written as `False`: the source not
    # distinguishing and the source saying "once for the unit" are different facts, and
    # defaulting would over-grant the 350 measured rows that do distribute.
    is_per_model = True if replaced_clause is not None else head.is_per_model

    return OptionRowParse(
        scope=head.scope,
        scope_n=head.scope_n,
        choices=tuple(choices),
        eligible_model_name=head.eligible_model_name,
        eligible_max_count=head.eligible_max_count,
        is_per_model=is_per_model,
        max_choices=_select_quantifier(stem),
        replaced_clause=replaced_clause,
    )


def _match_head(stem: str) -> _Head | None:
    """`004`'s head table to exhaustion, and only then `006`'s. The order is FR-009."""
    for pattern, scope in _HEADS:
        match = pattern.match(stem)
        if match is None:
            continue
        scope_n = int(match.group(1)) if scope is OptionScope.PER_N_MODELS else None
        return _Head(scope=scope, scope_n=scope_n)

    if any(pattern.search(stem) for pattern in _EXTENDED_REFUSED):
        return None
    for pattern, build in _EXTENDED_HEADS:
        match = pattern.match(stem)
        if match is not None:
            return build(match)
    return None


def _model_name(text: str) -> str | None:
    """A head's model-name capture, or ``None`` where the head names no subset.

    ``models`` is the source's word for "the unit's own models", which is the absence of a
    subset rather than the name of one. The footnote marker is stripped because it is
    typography; nothing else is, because everything else is the name as the source states it —
    in particular the plural is **not** singularised, which would be inference dressed as
    tidying (spec Clarifications, 2026-08-09: carried unchecked).
    """
    cleaned = _FOOTNOTE_MARK.sub("", text).strip()
    if not cleaned or cleaned.casefold() in {"model", "models"}:
        return None
    return cleaned


def _select_quantifier(stem: str) -> int | None:
    """The group-level cap the stem states, or ``None`` — `006` T019."""
    match = _SELECT_QUANTIFIER.search(stem)
    if match is None:
        return None
    count = match.group("count").casefold()
    return _NUMERALS.get(count, int(count) if count.isdigit() else None)


def _match_verb(stem: str) -> tuple[OptionVerb | None, str, str | None]:
    """The clause's verb, the text following it, and the side it takes away.

    ``replace`` is tested first: a row carrying both phrases is describing a replacement whose
    alternatives are then equipped, and reading it as additive would publish an upgrade the
    player has not paid for a swap to take.

    `006`'s distributive verb is tested **last**, after both `004` phrases have failed, so a row
    the baseline resolved cannot reach it. Its third return value is the possessive side — the
    only place a distributive stem names what is given up.
    """
    for phrase, verb in ((_REPLACE_VERB, OptionVerb.REPLACE), (_EQUIP_VERB, OptionVerb.EQUIP)):
        index = stem.find(phrase)
        if index >= 0:
            return verb, stem[index + len(phrase) :].strip(), None

    distributive = _DISTRIBUTIVE_REPLACE.search(stem)
    if distributive is not None:
        remainder = stem[distributive.end() :].strip()
        return OptionVerb.REPLACE, remainder, distributive.group("side").strip()
    return None, "", None


def split_conjuncts(name: str, count: int | None = None) -> tuple[ItemParse, ...]:
    """Decompose a choice's object clause into its granted items, in source order (T018).

    **This never rewrites the choice it decomposes.** It is handed the ``name`` and ``count``
    the baseline productions produced and returns a new structure beside them; the O1 Ruling
    says a legacy conflated label stays exactly as it is, and the way to keep that promise is a
    function that cannot express the alternative.

    The caller is responsible for the other half of the rule: decomposition is **refused
    outright** for any choice whose singular ``grants_``/``replaces_weapon_line`` the baseline
    already set, because an exactly-one weapon-name match is itself the evidence the name is one
    item and there is nothing to split.
    """
    text = f"{count} {name}" if count is not None else name
    parts = [part.strip() for part in _GRANTED_CONJUNCT.split(text) if part.strip()]
    return tuple(_item(part) for part in parts) or (ItemParse(name=name, count=count),)


def split_replaced(clause: str) -> tuple[ItemParse, ...]:
    """Decompose a distributive stem's possessive side into its replaced items (T018, FR-005)."""
    side = _POSSESSIVE.sub("", clause.strip())
    parts = [part.strip().rstrip(".;,:").strip() for part in _REPLACED_CONJUNCT.split(side)]
    return tuple(_item(part) for part in parts if part)


def _item(text: str) -> ItemParse:
    """One conjunct, with its own leading count where the source states one."""
    counted = _LEADING_COUNT.match(text)
    if counted is None:
        return ItemParse(name=text)
    return ItemParse(name=counted.group(2).strip(), count=int(counted.group(1)))


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
