# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the default-equipment grammar of
# 006 research D1e (006 task T028): six subject productions, the compound/conditional refusals
# ahead of them, `;`-then-`,` item splitting with a leading-count reader, and the three-state
# machine of data-model.md section 3 — in its own module, because its residual rule is the
# opposite of the composition grammar's.
"""Resolve one default-equipment sentence into a subject and the items it names.

The source prints, inside the ``UNIT COMPOSITION`` block and after the composition lists, a
sentence of the form *subject* ``is equipped with:`` *item*``;`` *item*. Research D1e measured
1 932 of them across 1 676 of 1 688 cached datacards, and this module turns one into structure or
says it could not.

**Six subject productions, in a fixed order** (D1e's table; counts are groups)::

    This model is equipped with:              -> unit           1 143
    Every model is equipped with:             -> unit             367
    Every <MODEL> is equipped with:           -> model_group      163
    The <MODEL> is equipped with:             -> model_group      137
    Each <MODEL> is equipped with:            -> model_group       18
    <MODEL> is equipped with:                 -> model_group       (the residual's own tail)

The first five cover ≈99.5 %; the sixth takes the unclassified remainder to 9 sentences in 1 942.
**The order is load-bearing**: ``^Every (.+) is equipped with:`` matches ``Every model is equipped
with:`` perfectly well and would publish a model group named ``model``, so the two fixed subjects
are tried to exhaustion first.

**The tail is refused, not approximated.** ``Every <MODEL> with <ITEM> …``, ``One <MODEL> …``,
``INT <MODEL> …``, ``A <MODEL> …``, ``For every INT models, …``, ``If the unit has INT models, …``
— 104 measured groups, the same compound-and-conditional shape family as option class 9. Every one
of them matches a production above and resolves to a *model name that is not a model*, which is
worse than no answer: it publishes a model group nobody can find, attached to a loadout somebody
will read. They return ``None`` and the caller raises the advisory ``EQP-UNPARSED``.

**Why this is not a branch inside :mod:`pipeline.parse.composition_grammar`** (plan.md Structure
Decision #1): the two have *incompatible residual rules*. An unresolved composition line suppresses
the whole datasheet's composition, because a partial composition under-counts a unit and therefore
mis-prices it; an unresolved equipment sentence suppresses **only itself**, because a partial
loadout under-states what a model carries and what did resolve is still true. One module cannot
hold both rules without one of them becoming a special case of the other.

Like its two siblings this module is **mode-blind**: it takes a description *string*, so the DOM
extractor feeds it exactly as a curator's override or a test does.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from pipeline.models.curated import DefaultEquipmentState, EquipmentAppliesTo
from pipeline.parse.composition_grammar import MAX_MODEL_NAME_CHARS, pre_pass

#: The table the ``html``-mode extractor delivers these sentences in. The export publishes no
#: such file, and that asymmetry is deliberate: its **absence** under ``csv`` mode is what
#: data-model.md section 3 means by "the source was not consulted", so no stage below ``acquire``
#: needs to know which mode ran.
EQUIPMENT_TABLE: Final = "Datasheets_unit_equipment.csv"

#: The ceiling the curated schema puts on ``item_name``. Shared with ``model_name``'s, because a
#: "name" past it has stopped being a name whichever column it was heading for.
MAX_ITEM_NAME_CHARS: Final = MAX_MODEL_NAME_CHARS

#: The marker that splits a sentence into its subject and its item list. ``are`` is accepted
#: beside ``is`` so a plural subject reaches the refusals below rather than falling out of the
#: grammar for a reason no reader could see.
_MARKER: Final = re.compile(r"\b(?:is|are)\s+equipped\s+with\s*:", re.IGNORECASE)

#: Subjects a **built** production would otherwise swallow. Each one is a refusal, not a
#: production: it sends its sentence to ``EQP-UNPARSED``, where a human sees it, and resolves
#: nothing. Ordered before the head table for the same reason ``options_grammar._REFUSED`` is.
_REFUSED: Final[tuple[re.Pattern[str], ...]] = (
    # `Every <MODEL> with <ITEM>` (21 measured groups): the qualifier is part of neither the
    # model name nor the loadout, and swallowing it names a model group that does not exist.
    re.compile(r"\bwith\b", re.IGNORECASE),
    # `One <MODEL>` (18), `INT <MODEL>` (15), `A <MODEL>` (9): a subset of a model group is not
    # the model group, and this feature has nowhere to state "one of them".
    re.compile(r"^(?:One|A|An)\s", re.IGNORECASE),
    re.compile(r"^\d"),
    # `For every INT models, …` (6) and `If the unit has INT models, …` (2): conditional and
    # distributive subjects, refused on exactly the terms US1 refuses their option counterparts.
    re.compile(r"^(?:For every|If|Unless|Up to)\b", re.IGNORECASE),
    re.compile(r","),
)

#: The subject table, in the fixed order it is tried. A pattern with no group is a whole-unit
#: subject; a pattern with one group names the model the sentence restricts itself to.
_SUBJECTS: Final[tuple[tuple[re.Pattern[str], EquipmentAppliesTo], ...]] = (
    (re.compile(r"^This model$", re.IGNORECASE), EquipmentAppliesTo.UNIT),
    (re.compile(r"^Every model$", re.IGNORECASE), EquipmentAppliesTo.UNIT),
    (re.compile(r"^Every (\S.*)$"), EquipmentAppliesTo.MODEL_GROUP),
    (re.compile(r"^The (\S.*)$"), EquipmentAppliesTo.MODEL_GROUP),
    (re.compile(r"^Each (\S.*)$"), EquipmentAppliesTo.MODEL_GROUP),
    (re.compile(r"^(\S.*)$"), EquipmentAppliesTo.MODEL_GROUP),
)

#: ``INT <name>`` — the count the source states for one item. **Never defaulted to 1**: absence
#: means the source said nothing, and 1 would be this pipeline saying it instead.
_LEADING_COUNT: Final = re.compile(r"^(\d+)\s+(\S.*)$")


@dataclass(frozen=True, slots=True)
class EquipmentItemParse:
    """One item of a sentence's list. ``weapon_line`` is linked separately, never guessed."""

    item_name: str
    count: int | None = None


@dataclass(frozen=True, slots=True)
class EquipmentParse:
    """One resolved sentence. ``composition_line`` is linked separately, and **by name**."""

    applies_to: EquipmentAppliesTo
    model_name: str | None
    items: tuple[EquipmentItemParse, ...]


def equipment_group_id(datasheet_id: str, line: int) -> str:
    """``eq-<datasheet-stem>-<line>`` — the sentence's own ordinal, and zero inference.

    The same identity discipline as ``og-`` (`004` FR-015), for the same reason: an upstream
    relabelling is then a **rename** — same id, changed items — rather than a removal plus an
    addition that a consumer's diff reports as two changes to two things.
    """
    return f"eq-{datasheet_id.removeprefix('ds-')}-{line}"


def parse_sentence(description: str) -> EquipmentParse | None:
    """Resolve one default-equipment sentence, or ``None`` when it matched no production.

    ``None`` is a *result*, not an error: it is D1e's compound-and-conditional tail, and the
    caller's job is to report it as ``EQP-UNPARSED`` and publish the sentences that did resolve.
    """
    text = pre_pass(description, field="equipment.description")
    marker = _MARKER.search(text)
    if marker is None:
        return None

    subject = text[: marker.start()].strip()
    items = _parse_items(text[marker.end() :])
    if not items:
        # A subject with an empty object names nothing to carry, and an empty group would say a
        # model is equipped with the absence of a weapon.
        return None

    resolved = _match_subject(subject)
    if resolved is None:
        return None

    applies_to, model_name = resolved
    return EquipmentParse(applies_to=applies_to, model_name=model_name, items=items)


def _match_subject(subject: str) -> tuple[EquipmentAppliesTo, str | None] | None:
    if not subject or any(pattern.search(subject) for pattern in _REFUSED):
        return None
    for pattern, applies_to in _SUBJECTS:
        match = pattern.match(subject)
        if match is None:
            continue
        if applies_to is EquipmentAppliesTo.UNIT:
            return applies_to, None
        name = match.group(1).strip()
        return (applies_to, name) if _is_name(name) else None
    return None


def _parse_items(clause: str) -> tuple[EquipmentItemParse, ...]:
    """Split the list the source states, and read each item's leading count.

    ``;`` separates 1 646 of the 1 655 multi-item groups; a bare ``,`` separates 9 and is the
    **fallback only**, never a second splitter — a list that already separates with ``;`` may
    legitimately carry a comma inside one item's name, and splitting on both would cut it in two.
    """
    body = clause.strip().rstrip(".").strip()
    if not body:
        return ()
    separator = ";" if ";" in body else ","
    items: list[EquipmentItemParse] = []
    for raw in body.split(separator):
        name = raw.strip().rstrip(".").strip()
        if not name:
            continue
        counted = _LEADING_COUNT.match(name)
        count = int(counted.group(1)) if counted else None
        if counted:
            name = counted.group(2).strip()
        if not _is_name(name):
            return ()
        items.append(EquipmentItemParse(item_name=name, count=count))
    return tuple(items)


def _is_name(value: str) -> bool:
    return bool(value) and len(value) <= MAX_ITEM_NAME_CHARS


def equipment_state(*, sentence_count: int, unparsed_count: int) -> DefaultEquipmentState:
    """Data-model.md section 3's three stated codes, as one function so it is spelled once.

    ``none`` when the datacard states no sentence, ``extracted`` when every sentence resolved,
    ``partial`` when at least one did not — and what resolved still ships. The **fourth** fact,
    *the source was not consulted or this datasheet's composition did not resolve*, is the
    absence of a value altogether and is the caller's decision to make: this function is only
    ever asked about a datasheet whose equipment rows were read and whose composition stands.
    """
    if sentence_count == 0:
        return DefaultEquipmentState.NONE
    return DefaultEquipmentState.PARTIAL if unparsed_count else DefaultEquipmentState.EXTRACTED
