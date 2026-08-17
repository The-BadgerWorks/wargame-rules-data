# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the wargear-option grammar of
# 004 research D3 (004 task T028): the `<li>` split ahead of the clause grammar, the clause
# head and verb table with its measured frequencies, the `with N` quantifier, and the residual
# marker that makes a vocabulary shift a coverage figure rather than missing data.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 007 US3 (T038, T039): stripped the footnote
# marker at `_parse_object` and `_item` (research D4.1, guarantee 21); added the item-constraint
# production `parse_constraint_row`/`is_constraint_shaped` against the closed two-member
# vocabulary (research D4.2), tried by the caller only after `parse_row` has already refused a row.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 008 US1 (T030-T032): appended the three
# highest-yield `head_ok_no_verb` verb productions to `_COMPLETION_VERBS` — distributive equip,
# active-voice replace per-unit, and the non-distributive `can have … replaced with` sibling of
# `006`'s distributive production — closing the 42 zero-group datasheets / 28 card shapes.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 008 US2 (T040-T042): appended the three
# remaining measured `head_ok_no_verb` verb productions — active-voice replace distributive,
# item-subject passive, and the pure-grant `can [each] have INT <ITEM>` (which also discharges
# `007` T033's deferred "N models can each have …" family) — over the 120 some-group datasheets /
# 80 card shapes. `_COMPLETION_HEADS` deliberately stays empty (T043): the measured `no_head_match`
# residual is predominantly extractor artifacts, not a grammar gap, and routes to Phase 7 override
# authoring instead (`reports/option-taxonomy/2026-08-15.md` Section (a2)).
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

from pipeline.models.curated import ItemConstraintType, OptionScope, WargearOptionState
from pipeline.parse.composition_grammar import FOOTNOTE_MARK, pre_pass

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
    #: What the eligible subject gives **up**, captured from EITHER of two places the source
    #: states it (007 research D3.1): the distributive stem's own possessive head (`006`), or —
    #: new here — the plain text between a legacy `_REPLACE_VERB` row's head match and its verb
    #: phrase, which `004` matched for its head shape and then discarded. ``None`` only for a
    #: row whose verb is not a replacement at all (`_EQUIP_VERB`, or no verb matched); a legacy
    #: replacement row with literally nothing stated between head and verb captures ``""``, never
    #: ``None`` — the distinction the `_option_structure` role ternary depends on (007 D3).
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

    matched_head = _match_head(stem)
    if matched_head is None:
        return None
    head, head_end = matched_head

    verb, object_clause, replaced_clause, is_distributive = _match_verb(stem, head_end)
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
    #
    # **Keyed on `is_distributive`, not on `replaced_clause is not None`** (007 T021): the legacy
    # `_REPLACE_VERB` shape now populates `replaced_clause` too, and it is not distributive — a
    # singular "One <Model>'s <item> can be replaced with ..." row must keep `is_per_model` at
    # whatever its head said (`None` for a singular head), never forced `True` by the mere
    # presence of a given-up-item capture.
    is_per_model = True if is_distributive else head.is_per_model

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


def _match_head(stem: str) -> tuple[_Head, int] | None:
    """`004`'s head table to exhaustion, and only then `006`'s. The order is FR-009.

    Returns the match's end offset alongside the head (007 T021): it is where a legacy
    replacement clause's given-up item, if any, begins.
    """
    for pattern, scope in _HEADS:
        match = pattern.match(stem)
        if match is None:
            continue
        scope_n = int(match.group(1)) if scope is OptionScope.PER_N_MODELS else None
        return _Head(scope=scope, scope_n=scope_n), match.end()

    if any(pattern.search(stem) for pattern in _EXTENDED_REFUSED):
        return None
    for pattern, build in _EXTENDED_HEADS:
        match = pattern.match(stem)
        if match is not None:
            return build(match), match.end()
    # `008`, last: `_EXTENDED_REFUSED`'s early `return None` above already stands between this
    # loop and every conditional/equipment-qualified row, exactly as it does for `_EXTENDED_HEADS`.
    for pattern, build in _COMPLETION_HEADS:
        match = pattern.match(stem)
        if match is not None:
            return build(match), match.end()
    return None


def _model_name(text: str) -> str | None:
    """A head's model-name capture, or ``None`` where the head names no subset.

    ``models`` is the source's word for "the unit's own models", which is the absence of a
    subset rather than the name of one. The footnote marker is stripped because it is
    typography; nothing else is, because everything else is the name as the source states it —
    in particular the plural is **not** singularised, which would be inference dressed as
    tidying (spec Clarifications, 2026-08-09: carried unchecked).
    """
    cleaned = FOOTNOTE_MARK.sub("", text).strip()
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


def _match_verb(stem: str, head_end: int) -> tuple[OptionVerb | None, str, str | None, bool]:
    """The clause's verb, the text following it, the side it takes away, and whether that side
    is `006`'s distributive shape.

    ``replace`` is tested first: a row carrying both phrases is describing a replacement whose
    alternatives are then equipped, and reading it as additive would publish an upgrade the
    player has not paid for a swap to take.

    **007 T021**: the legacy ``_REPLACE_VERB`` phrase now also captures a given-up clause — the
    stem text between the head's own match end (``head_end``) and the verb phrase's start, which
    `004` matched for its head shape and then discarded (research D3.1's "single missing
    capture"). It is captured even when empty (``""``, never ``None``): an empty span is D3.3's
    "no given-up item at all" case, and `_option_structure`'s role ternary needs to tell that
    apart from a row whose verb was never a replacement in the first place.

    `006`'s distributive verb is tested **last**, after both `004` phrases have failed, so a row
    the baseline resolved cannot reach it. Its third return value is the possessive side — the
    only place a distributive stem names what is given up. The fourth return value,
    ``is_distributive``, is true only for this branch — the legacy capture above must not be
    read as evidence of distributivity too (007 T021, guards `is_per_model`).
    """
    replace_index = stem.find(_REPLACE_VERB)
    if replace_index >= 0:
        given_up = stem[head_end:replace_index].strip()
        return (
            OptionVerb.REPLACE,
            stem[replace_index + len(_REPLACE_VERB) :].strip(),
            given_up,
            False,
        )

    equip_index = stem.find(_EQUIP_VERB)
    if equip_index >= 0:
        return OptionVerb.EQUIP, stem[equip_index + len(_EQUIP_VERB) :].strip(), None, False

    distributive = _DISTRIBUTIVE_REPLACE.search(stem)
    if distributive is not None:
        remainder = stem[distributive.end() :].strip()
        return OptionVerb.REPLACE, remainder, distributive.group("side").strip(), True

    # `008`, last: reached only after every `004` and `006` verb has failed to match.
    for pattern, build in _COMPLETION_VERBS:
        match = pattern.search(stem)
        if match is not None:
            return build(match, stem, head_end)
    return None, "", None, False


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
    """One conjunct, with its own leading count where the source states one.

    **007 T038**: the footnote marker is stripped here too, not only in :func:`_parse_object`.
    A conjunct built from a choice's own (already-clean) ``name`` never carries one, but a
    conjunct built from a legacy replacement's possessive ``replaced_clause`` — captured directly
    from the stem by :func:`_match_verb` and never routed through ``_parse_object`` — can, and
    this is the only extraction point that ever sees that span (research D4.1, guarantee 21).
    """
    counted = _LEADING_COUNT.match(text)
    name = counted.group(2).strip() if counted is not None else text
    name = FOOTNOTE_MARK.sub("", name).strip()
    return ItemParse(name=name, count=int(counted.group(1)) if counted is not None else None)


def _parse_object(text: str, verb: OptionVerb) -> OptionChoiceParse | None:
    """One clause object — ``with INT name``, ``name``, or an explicit "no change".

    **007 T038**: the footnote marker is stripped from the name here — the extraction point for
    ``option_choices[].name`` — so a published choice name is never the display artifact of a
    restriction stated elsewhere on the card (research D4.1, guarantee 21). Stripped after the
    ``no change`` check (that literal never carries one) and before the length ceiling, so a name
    that is only over length *because* of a trailing marker run is correctly rescued.
    """
    cleaned = text.strip().rstrip(".;,:").strip()
    if not cleaned:
        return None

    if cleaned.casefold() == _NO_CHANGE:
        return OptionChoiceParse(name=NO_CHANGE_NAME, is_no_change=True, verb=verb)

    counted = _LEADING_COUNT.match(cleaned)
    count = int(counted.group(1)) if counted else None
    name = FOOTNOTE_MARK.sub("", (counted.group(2) if counted else cleaned).strip()).strip()
    if not name or len(name) > MAX_CHOICE_NAME_CHARS:
        return None
    return OptionChoiceParse(name=name, count=count, verb=verb)


def choice_names(parsed: OptionRowParse) -> Sequence[str]:
    """The parsed choice names, in source order — a convenience for reports and tests."""
    return [choice.name for choice in parsed.choices]


# -- `008-wargear-option-completion`: everything below is appended AFTER every `004` AND `006` ---
# production
#
# **The same ordering guarantee, extended by one more stage.** :func:`_match_head` runs `004`'s
# table to exhaustion, then `006`'s ``_EXTENDED_HEADS`` to exhaustion, and only then looks at
# ``_COMPLETION_HEADS``; :func:`_match_verb` runs `004`'s two verbs and `006`'s
# ``_DISTRIBUTIVE_REPLACE`` before ``_COMPLETION_VERBS``. A row any prior release resolved
# therefore never reaches a line of `008` code, on exactly the terms research D5 established for
# `006` (plan.md's *Architecture*, "The ordering guarantee, restated as control flow"). This is
# proven, not merely arranged: `tests/enrichment/test_options_grammar_ordering.py` monkeypatches
# both tables below to entries that raise if a resolving row's path ever touches them.
#
# **Both tables are EMPTY here** (008 Foundational task T016) — the guarantee lands, tested,
# before a single production exists. Phase 3 and Phase 4 only ever *append* an entry; nothing
# about the tables' position, their being tried last, or the refusal tables ahead of them
# (``_REFUSED``, ``_EXTENDED_REFUSED``, both already run before either table is reached and are
# never modified here) changes when they do.

#: One `008` head production: a pattern, and the builder its match is handed to — the identical
#: shape `_EXTENDED_HEADS` already uses, so a `008` head production is written exactly like a
#: `006` one.
_CompletionHeadBuilder = Callable[[re.Match[str]], _Head]

#: One `008` verb production: a pattern searched (not anchored) against the stem, and a builder
#: that is handed the match, the whole stem, and the head's own match end — the same three
#: values `_DISTRIBUTIVE_REPLACE`'s own inline handling already closes over, generalised into a
#: table because `008` appends more than one verb shape rather than exactly one.
_CompletionVerbBuilder = Callable[
    [re.Match[str], str, int], tuple[OptionVerb, str, str | None, bool]
]

# -- Phase 3 (US1, T030-T032): the three highest-yield `head_ok_no_verb` verb shapes, in T001's
# measured zero-group-closure order (`reports/option-taxonomy/2026-08-15.md` Section (a),
# 2026-08-10 classes 3, 4, 5 — 34, 31, and 30 rows respectively). All three reuse a head `004` or
# `006` already carries; the residual on these rows was always the verb, never the head, which is
# why none of them needs a `_COMPLETION_HEADS` entry.

#: ``can each be equipped with`` — T030, class 3, 34 measured rows. The distributive sibling of
#: the legacy ``_EQUIP_VERB`` ("can be equipped with"): `is_distributive` is set true exactly as
#: `_DISTRIBUTIVE_REPLACE` sets it, and — because nothing is given up, only granted — it captures
#: no `replaced_clause`.
_DISTRIBUTIVE_EQUIP: Final = re.compile(r"\bcan each be equipped with\b", re.IGNORECASE)


def _distributive_equip(
    match: re.Match[str], stem: str, _head_end: int
) -> tuple[OptionVerb, str, str | None, bool]:
    """T030: ``can each be equipped with`` — distributive, no given-up side."""
    return OptionVerb.EQUIP, stem[match.end() :].strip(), None, True


#: ``can replace its/their … with`` — T031, class 4, 31 measured rows. Active voice, per-unit
#: (not distributive: this shape names no ``each``). The possessive side — captured raw, with
#: its leading determiner — is the same shape of string `_DISTRIBUTIVE_REPLACE`'s own ``side``
#: group already hands `replaced_clause`, so `split_replaced`'s existing `_POSSESSIVE` strip
#: removes the determiner downstream without a second production needing to know that.
_ACTIVE_REPLACE: Final = re.compile(
    r"\bcan replace\s+(?P<side>(?:its|their)\s+.+?)\s+with\b", re.IGNORECASE
)


def _active_replace_per_unit(
    match: re.Match[str], stem: str, _head_end: int
) -> tuple[OptionVerb, str, str | None, bool]:
    """T031: ``can replace its/their … with`` — not distributive."""
    return OptionVerb.REPLACE, stem[match.end() :].strip(), match.group("side").strip(), False


#: ``can have … replaced with`` — T032, class 5, 30 measured rows. The singular sibling of
#: `006`'s distributive ``can each have … replaced with`` (`_DISTRIBUTIVE_REPLACE`), differing
#: from it by exactly the word ``each``. **Not distributive.** Appended after it in
#: `_COMPLETION_VERBS` below, but the guarantee that actually protects a distributive row is
#: `_match_verb`'s own control flow: `_DISTRIBUTIVE_REPLACE` is tried, unconditionally, before
#: `_COMPLETION_VERBS` is even reached — so a "can each have … replaced with" row is resolved by
#: that production and never sees this one. tasks.md calls this pair "the single most dangerous
#: task in this list" for exactly this reason, and it is covered by three independent controls:
#: this ordering, `tests/enrichment/test_options_grammar_ordering.py`'s monkeypatch guarantee, and
#: the layer-1 golden (`test_options_grammar_regression.py`).
_REPLACE_HAVE_SINGULAR: Final = re.compile(
    r"\bcan have\s+(?P<side>.+?)\s+replaced with\b", re.IGNORECASE
)


def _replace_have_singular(
    match: re.Match[str], stem: str, _head_end: int
) -> tuple[OptionVerb, str, str | None, bool]:
    """T032: ``can have … replaced with`` — the non-distributive sibling of `006`'s production."""
    return OptionVerb.REPLACE, stem[match.end() :].strip(), match.group("side").strip(), False


# -- Phase 4 (US2, T040-T042): the three remaining measured `head_ok_no_verb` verb shapes, in
# T001's measured order (`reports/option-taxonomy/2026-08-15.md` Section (a), 2026-08-10 classes
# 7, 8, 10 — 18, 13, and 9 rows respectively). All three reuse a head `004` or `006` already
# carries, exactly as Phase 3's three did.

#: ``can each replace … with`` — T040, class 7, 18 measured rows. The distributive sibling of
#: T031's active-voice ``_ACTIVE_REPLACE``: the possessive side is the ``replaced_clause``, and
#: because the verb phrase carries ``each`` this sets `is_distributive` true exactly as every
#: other ``each`` production in this module does. Distinct phrase from `_ACTIVE_REPLACE` (`can
#: replace` has no ``each`` between the two words), so the two never contend for the same row.
_ACTIVE_REPLACE_DISTRIBUTIVE: Final = re.compile(
    r"\bcan each replace\s+(?P<side>(?:its|their)\s+.+?)\s+with\b", re.IGNORECASE
)


def _active_replace_distributive(
    match: re.Match[str], stem: str, _head_end: int
) -> tuple[OptionVerb, str, str | None, bool]:
    """T040: ``can each replace … with`` — distributive."""
    return OptionVerb.REPLACE, stem[match.end() :].strip(), match.group("side").strip(), True


#: ``<ITEM> can each be replaced with`` — T041, class 8, 13 measured rows. The subject *is* the
#: replaced item, which is the shape's whole difficulty: there is no possessive phrase naming what
#: is given up, because the head itself already named it. The given-up span is read from the head's
#: own match end to this verb's match start — the identical capture `007` T021's legacy
#: `_REPLACE_VERB` shape uses, reused rather than reinvented. Distinct phrase from `_DISTRIBUTIVE_
#: EQUIP` (``equipped`` not ``replaced``) and from `_DISTRIBUTIVE_REPLACE` (which requires ``have``
#: between ``each`` and the possessive side; this shape has no ``have`` at all), so neither
#: contends for the same row.
_ITEM_SUBJECT_PASSIVE: Final = re.compile(r"\bcan each be replaced with\b", re.IGNORECASE)


def _item_subject_passive(
    match: re.Match[str], stem: str, head_end: int
) -> tuple[OptionVerb, str, str | None, bool]:
    """T041: ``<ITEM> can each be replaced with`` — the subject is the given-up item."""
    given_up = stem[head_end : match.start()].strip()
    return OptionVerb.REPLACE, stem[match.end() :].strip(), given_up, True


#: ``can [each] have INT <ITEM>`` — T042, class 10, 9 measured rows. Verb ``EQUIP``, no
#: ``replaced_clause``: nothing is given up, only granted. The digit lookahead is what tells this
#: apart from T032's `_REPLACE_HAVE_SINGULAR` and `006`'s `_DISTRIBUTIVE_REPLACE` (both require a
#: later ``replaced with``); those two are tried first — `_DISTRIBUTIVE_REPLACE` unconditionally in
#: `_match_verb`, `_REPLACE_HAVE_SINGULAR` earlier in this same tuple — so a row carrying
#: ``replaced with`` is always claimed by one of them before this pattern is ever reached.
#:
#: The optional ``each`` is what discharges `007` T033's deferred "N models can each have …"
#: family (008 T044): that family's head already resolves through `004`'s bare ``^\d+ `` digit
#: head, and this verb was the only piece missing.
_PURE_GRANT: Final = re.compile(r"\bcan(?:\s+each)?\s+have\b(?=\s+\d)", re.IGNORECASE)


def _pure_grant(
    match: re.Match[str], stem: str, _head_end: int
) -> tuple[OptionVerb, str, str | None, bool]:
    """T042: ``can [each] have INT <ITEM>`` — pure grant, no replacement."""
    is_distributive = "each" in match.group(0).casefold()
    return OptionVerb.EQUIP, stem[match.end() :].strip(), None, is_distributive


#: Appended after every `006` head has failed to match. Rule 5 (tasks.md): a class T001 measures
#: at zero gets no entry here, ever. **Still empty after Phase 4** (T043): T001's Section (a2)
#: measured the `no_head_match` residual (17 rows) as predominantly extractor artifacts (2026-08-10
#: classes 11 and 13, 16 of that residual's 17), not a grammar gap — building a production for an
#: extractor bug would be fixing the wrong layer, and there is no vocabulary left to close here.
#: That residual routes to Phase 7's override authoring instead.
_COMPLETION_HEADS: Final[tuple[tuple[re.Pattern[str], _CompletionHeadBuilder], ...]] = ()

#: Appended after `_DISTRIBUTIVE_REPLACE` has failed to match. Same rule 5. Order is T001's
#: measured zero-group-closure order (rule 3 — never reordered by a later phase without also
#: updating `test_options_grammar_ordering.py`'s explicit name pin, T029).
_COMPLETION_VERBS: Final[tuple[tuple[re.Pattern[str], _CompletionVerbBuilder], ...]] = (
    (_DISTRIBUTIVE_EQUIP, _distributive_equip),
    (_ACTIVE_REPLACE, _active_replace_per_unit),
    (_REPLACE_HAVE_SINGULAR, _replace_have_singular),
    (_ACTIVE_REPLACE_DISTRIBUTIVE, _active_replace_distributive),
    (_ITEM_SUBJECT_PASSIVE, _item_subject_passive),
    (_PURE_GRANT, _pure_grant),
)


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


# -- 007-loadout-display-fidelity: the item-constraint production (US3, research D4.2) -----------
#
# **Tried by the caller, never inside `parse_row` above.** `pipeline/curate/assemble.py::
# _option_structure` calls :func:`parse_constraint_row` only for a row `parse_row` has already
# failed to resolve as an option (`line is not None and parsed is None`) — the row genuinely is
# refused by `004`'s and `006`'s own tables, one way or another, before this module's constraint
# vocabulary is ever consulted. This keeps rule 4's ordering guarantee literal: nothing below
# changes what any row that resolves today resolves to, because nothing below runs before that
# resolution is already known to have failed.
#
# Measured (research D4.2): a small closed set of restriction sentence shapes reach the pipeline
# as refused option rows rather than as a second arrival path inside the composition or equipment
# block — T003's whole-corpus measurement could not run this session (no live/cached-corpus
# access), so this vocabulary is fixture-proven against T006's GF12 rows 6-10 rather than
# corpus-measured, exactly as `.impl-progress.md` records.


@dataclass(frozen=True, slots=True)
class ItemConstraintParse:
    """One footnote-style restriction, resolved against the closed vocabulary (FR-009)."""

    constraint_type: ItemConstraintType
    item_name: str
    model_name: str | None = None


#: ``The [<MODEL>'s] <ITEM> cannot be replaced.`` — the item may not be exchanged through any
#: wargear option, optionally scoped to a named model group exactly as a `006` distributive
#: stem's own possessive head is (the same ``_MODEL``/``_APOS`` vocabulary, reused rather than
#: reinvented).
_NOT_REPLACEABLE: Final = re.compile(
    rf"^The (?:(?P<model>{_MODEL}){_APOS}s\s+)?(?P<item>.+?)\s+cannot be replaced\.?$"
)

#: ``Only one <ITEM> can be taken per unit.`` — at most one model of the unit may carry it.
_ONE_PER_UNIT: Final = re.compile(r"^Only one (?P<item>.+?)\s+can be taken per unit\.?$")

#: **Restriction-shaped, not necessarily vocabulary-matched.** Broader than either production
#: above on purpose: a row this matches but neither production resolves is a restriction the
#: closed vocabulary does not (yet) cover — the advisory ``CST-UNPARSED``, never ``OPT-UNPARSED``,
#: because ``OPT-UNPARSED`` says "this looked like an option and did not resolve", which is the
#: wrong fact for a row that was never an option attempt to begin with. A row this does **not**
#: match falls through to ``OPT-UNPARSED`` exactly as it does today — this detector only ever
#: narrows which advisory a refused row receives, never whether a row resolves.
_RESTRICTION_SHAPED: Final = re.compile(
    r"\bcannot be\b|\bonly one\b.*\bcan\b|\bmay only\b", re.IGNORECASE
)


def parse_constraint_row(description: str) -> ItemConstraintParse | None:
    """Resolve one restriction row against the closed two-member vocabulary, or ``None``.

    Never a nearest-member guess (contract §3.2): a row that looks like a restriction but matches
    neither production returns ``None`` here, and the caller checks :func:`is_constraint_shaped`
    separately to decide whether that ``None`` means ``CST-UNPARSED`` or plain ``OPT-UNPARSED``.
    """
    stem = pre_pass(description, field="option.description")
    if not stem:
        return None

    replace_match = _NOT_REPLACEABLE.match(stem)
    if replace_match is not None:
        item = FOOTNOTE_MARK.sub("", replace_match.group("item")).strip()
        if not item or len(item) > MAX_CHOICE_NAME_CHARS:
            return None
        model = replace_match.group("model")
        return ItemConstraintParse(
            constraint_type=ItemConstraintType.NOT_REPLACEABLE,
            item_name=item,
            model_name=_model_name(model) if model is not None else None,
        )

    per_unit_match = _ONE_PER_UNIT.match(stem)
    if per_unit_match is not None:
        item = FOOTNOTE_MARK.sub("", per_unit_match.group("item")).strip()
        if not item or len(item) > MAX_CHOICE_NAME_CHARS:
            return None
        return ItemConstraintParse(constraint_type=ItemConstraintType.ONE_PER_UNIT, item_name=item)

    return None


def is_constraint_shaped(description: str) -> bool:
    """Whether a row *looks like* a restriction, whether or not it matched the vocabulary.

    This is what lets the caller tell "a restriction the vocabulary does not cover"
    (``CST-UNPARSED``) apart from "not a restriction at all" (``OPT-UNPARSED``, unchanged).
    """
    stem = pre_pass(description, field="option.description")
    return bool(_RESTRICTION_SHAPED.search(stem))
