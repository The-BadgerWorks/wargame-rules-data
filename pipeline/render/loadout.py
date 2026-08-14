# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the reference renderer for
# `WargameCompanion:specs/007-loadout-display-fidelity/contracts/rendering-contract.md` v1.0.0
# (007 tasks T044-T046): the template catalogue (contract §3), the total selection tables (§4)
# evaluated top to bottom with a final omission fallthrough on every table, deterministic
# ordering and block assembly (§6, nested groups, depth cap, cycle detection), and the segment
# stream (§7.2) built by construction from the same pass that builds the canonical string, never
# by a second, divergent code path.
"""The Loadout Rendering contract's Python reference implementation.

Reads ONLY item rows for wargear-choice semantics (contract §2.1, tasks.md rule 8): every
dataclass this module defines carries an ``items`` tuple and never a ``grants_weapon_line`` /
``replaces_weapon_line`` field, so the deprecated singular columns cannot be read even by
accident -- there is nowhere on these types for them to live.

Public entry points:

* :func:`render_composition_block` / :func:`render_options_block` -- the typed core, taking this
  module's own snake_case dataclasses (contract §2's SQLite naming).
* :func:`render_case` -- a thin adapter from the bundle wire form (camelCase, exactly
  ``contracts/rendering-fixtures/cases.json``'s ``input`` shape) onto the typed core. The mapping
  is name-only (contract §2); no value differs between the two wire forms.

Every literal string below is authored template text from the contract's own §3 catalogue -- no
publisher wording, no card-specific text (contract §0.1).
"""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final, Literal

#: The contract version this module implements (contract §8.3, drift-checked against the
#: vendored fixture corpus's own ``contractVersion`` stamp by
#: ``tests/contract/test_rendering_conformance.py``).
RENDERING_CONTRACT_VERSION: Final = "1.0.0"

# ---------------------------------------------------------------------------------------------
# Input DTOs -- contract §2's SQLite (snake_case) naming, restricted to the fields rendering
# actually reads. These are deliberately NOT the pydantic CuratedXxx models: those carry a full
# datasheet's worth of fields rendering never touches (pricing, provenance, ids not used here),
# and a fixture corpus case has no owning datasheet at all. A future caller (US5's equivalence
# check) constructs these same dataclasses directly from curated data; this phase only needs
# to construct them from the synthetic conformance corpus via `render_case`.
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CompositionRow:
    """One `datasheet_composition` row (contract §3.2, §4.1)."""

    line: int
    model_name: str | None = None
    min_count: int | None = None
    max_count: int | None = None


@dataclass(frozen=True, slots=True)
class EquipmentItem:
    """One `datasheet_equipment_item` row (contract §3.3)."""

    item_index: int
    item_name: str
    count: int | None = None


@dataclass(frozen=True, slots=True)
class EquipmentGroup:
    """One `datasheet_equipment_group` row and its items (contract §3.3, §4.2)."""

    id: str
    line: int
    applies_to: str
    model_name: str | None = None
    items: tuple[EquipmentItem, ...] = ()


@dataclass(frozen=True, slots=True)
class OptionChoiceItem:
    """One `datasheet_option_choice_item` row -- the sole source of truth for a choice's items
    (contract §2.1). ``role`` is ``'granted'`` or ``'replaced'``.
    """

    role: str
    item_index: int
    item_name: str
    count: int | None = None


@dataclass(frozen=True, slots=True)
class OptionChoice:
    """One `datasheet_option_choice` row. Deliberately carries no singular
    `grants_weapon_line` / `replaces_weapon_line` field -- only `items` (contract §2.1, rule 8).
    """

    id: str
    items: tuple[OptionChoiceItem, ...] = ()
    is_no_change: bool = False


@dataclass(frozen=True, slots=True)
class OptionGroup:
    """One `datasheet_option_group` row and its choices (contract §3.4, §4.3, §4.4)."""

    id: str
    line: int
    scope: str
    scope_n: int | None = None
    eligible_model_name: str | None = None
    eligible_max_count: int | None = None
    is_per_model: bool | None = None
    max_choices: int | None = None
    parent_group_id: str | None = None
    choices: tuple[OptionChoice, ...] = ()


@dataclass(frozen=True, slots=True)
class ItemConstraint:
    """One `datasheet_item_constraint` row (contract §3.5, §4.6)."""

    constraint_index: int
    constraint_type: str
    item_name: str
    model_name: str | None = None


# ---------------------------------------------------------------------------------------------
# Output types (contract §7)
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Segment:
    """One element of the segment stream (contract §7.2)."""

    kind: Literal["literal", "slot"]
    text: str
    slot: str | None = None
    ref: str | None = None


@dataclass(frozen=True, slots=True)
class RenderResult:
    """The output of rendering one block (contract §6, §7).

    ``canonical`` is the normative output (§7.1); ``segments`` concatenate to it byte for byte by
    construction (§7.2); ``omitted`` is the ordered list of `RND-*` reason codes for every row
    that did not resolve, in the order they were encountered while assembling the block (§5.2).
    """

    canonical: str
    segments: tuple[Segment, ...]
    omitted: tuple[str, ...]


def _name(value: str) -> str:
    """Unicode NFC normalisation, and nothing else (contract §3.1)."""
    return unicodedata.normalize("NFC", value)


class _Builder:
    """Accumulates one rendered line's segments. Internal, mutable by design -- the canonical
    string for a line is derived from its segments, never built by a second, parallel path.
    """

    __slots__ = ("segments",)

    def __init__(self) -> None:
        self.segments: list[Segment] = []

    def literal(self, text: str) -> None:
        if text:
            self.segments.append(Segment("literal", text))

    def slot(self, text: str, name: str) -> None:
        self.segments.append(Segment("slot", text, slot=name))

    def extend(self, other: _Builder) -> None:
        self.segments.extend(other.segments)

    def copy(self) -> _Builder:
        clone = _Builder()
        clone.segments.extend(self.segments)
        return clone


def _render_item(builder: _Builder, item_name: str, count: int | None) -> None:
    """`E.item.counted` / `E.item.plain` -- the same two templates the equipment block and a
    wargear choice's item list both use (contract §3.3, §4.5).
    """
    if count is not None:
        builder.slot(str(count), "count")
        builder.literal(" ")
    builder.slot(_name(item_name), "itemName")


def _render_item_list(builder: _Builder, items: Sequence[EquipmentItem | OptionChoiceItem]) -> None:
    """`L.join` -- items joined by `"; "`, no conjunction (contract §3.6). Unreachable on an
    empty list by construction of every caller (`L.empty`).
    """
    for index, item in enumerate(items):
        if index > 0:
            builder.literal("; ")
        _render_item(builder, item.item_name, item.count)


# ---------------------------------------------------------------------------------------------
# §4.1 Composition line
# ---------------------------------------------------------------------------------------------


def _render_composition_line(builder: _Builder, row: CompositionRow) -> str | None:
    """Returns an `RND-*` omission code, or `None` on success (contract §4.1)."""
    if not row.model_name:
        return "RND-COMP-NO-NAME"
    if row.min_count is not None and row.max_count is not None:
        if row.min_count == row.max_count:
            builder.slot(str(row.min_count), "count")
            builder.literal(" ")
            builder.slot(_name(row.model_name), "modelName")
            return None
        if row.min_count < row.max_count:
            builder.slot(str(row.min_count), "minCount")
            builder.literal("-")
            builder.slot(str(row.max_count), "maxCount")
            builder.literal(" ")
            builder.slot(_name(row.model_name), "modelName")
            return None
    return "RND-COMP-BAD-RANGE"


# ---------------------------------------------------------------------------------------------
# §4.2 Equipment group
# ---------------------------------------------------------------------------------------------


def _render_equipment_group(builder: _Builder, group: EquipmentGroup) -> str | None:
    """Returns an `RND-*` omission code, or `None` on success (contract §4.2)."""
    if not group.items:
        return "RND-EQP-NO-ITEMS"
    if group.applies_to == "model_group":
        if not group.model_name:
            return "RND-EQP-NO-SUBJECT"
        builder.literal("Every ")
        builder.slot(_name(group.model_name), "modelName")
        builder.literal(" is equipped with: ")
        _render_item_list(builder, group.items)
        builder.literal(".")
        return None
    if group.applies_to == "unit":
        builder.literal("Every model is equipped with: ")
        _render_item_list(builder, group.items)
        builder.literal(".")
        return None
    return "RND-EQP-UNKNOWN-SCOPE"


def render_composition_block(
    composition: Sequence[CompositionRow], equipment_groups: Sequence[EquipmentGroup]
) -> RenderResult:
    """The Unit Composition block: every composition line, then every equipment group line
    (contract §6 Block assembly).
    """
    lines: list[_Builder] = []
    omitted: list[str] = []
    for row in sorted(composition, key=lambda r: r.line):
        builder = _Builder()
        code = _render_composition_line(builder, row)
        if code is not None:
            omitted.append(code)
        else:
            lines.append(builder)
    for group in sorted(equipment_groups, key=lambda g: g.line):
        builder = _Builder()
        code = _render_equipment_group(builder, group)
        if code is not None:
            omitted.append(code)
        else:
            lines.append(builder)
    return _assemble(lines, omitted)


# ---------------------------------------------------------------------------------------------
# §4.3 Option subject
# ---------------------------------------------------------------------------------------------


def _render_subject(builder: _Builder, group: OptionGroup) -> str | None:
    """Returns an `RND-*` omission code for the WHOLE group, or `None` on success (contract
    §4.3). ``eligible_model_name`` is checked before ``scope``, as the contract requires.
    """
    if group.eligible_model_name and group.eligible_max_count is not None:
        builder.literal("Up to ")
        builder.slot(str(group.eligible_max_count), "eligibleMaxCount")
        builder.literal(" ")
        builder.slot(_name(group.eligible_model_name), "eligibleModelName")
        builder.literal(" in this unit")
        return None
    if group.eligible_model_name and group.is_per_model is True:
        builder.literal("Each ")
        builder.slot(_name(group.eligible_model_name), "eligibleModelName")
        builder.literal(" in this unit")
        return None
    if group.eligible_model_name:
        builder.literal("The ")
        builder.slot(_name(group.eligible_model_name), "eligibleModelName")
        builder.literal(" in this unit")
        return None
    if group.scope == "per_n_models":
        if group.scope_n is None:
            return "RND-OPT-NO-SCOPE-N"
        builder.literal("One model in this unit for every ")
        builder.slot(str(group.scope_n), "scopeN")
        builder.literal(" models it contains")
        return None
    if group.scope == "model":
        builder.literal("Each model in this unit")
        return None
    if group.scope == "unit":
        builder.literal("This unit")
        return None
    return "RND-OPT-UNKNOWN-SCOPE"


# ---------------------------------------------------------------------------------------------
# §4.5 A single choice
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _ChoiceRender:
    kind: Literal["noChange", "replace", "grant", "remove"]
    granted: tuple[OptionChoiceItem, ...]
    replaced: tuple[OptionChoiceItem, ...]


def _classify_choice(choice: OptionChoice) -> _ChoiceRender | str:
    """Returns a resolved `_ChoiceRender`, or an `RND-*` omission code for this choice alone
    (contract §4.5).
    """
    granted = tuple(
        sorted((i for i in choice.items if i.role == "granted"), key=lambda i: i.item_index)
    )
    replaced = tuple(
        sorted((i for i in choice.items if i.role == "replaced"), key=lambda i: i.item_index)
    )
    if choice.is_no_change:
        return _ChoiceRender("noChange", granted, replaced)
    if granted and replaced:
        return _ChoiceRender("replace", granted, replaced)
    if granted:
        return _ChoiceRender("grant", granted, replaced)
    if replaced:
        return _ChoiceRender("remove", granted, replaced)
    return "RND-OPT-NO-ITEMS"


def _append_choice_tail(builder: _Builder, choice: _ChoiceRender) -> None:
    """Appends `O.choice.*`'s content AFTER the subject has already been written (contract §3.4,
    §4.5).
    """
    if choice.kind == "noChange":
        builder.literal(" can be left unchanged.")
    elif choice.kind == "replace":
        builder.literal(" can have ")
        _render_item_list(builder, choice.replaced)
        builder.literal(" replaced with ")
        _render_item_list(builder, choice.granted)
        builder.literal(".")
    elif choice.kind == "grant":
        builder.literal(" can be equipped with ")
        _render_item_list(builder, choice.granted)
        builder.literal(".")
    elif choice.kind == "remove":
        builder.literal(" can have ")
        _render_item_list(builder, choice.replaced)
        builder.literal(" removed.")


def _render_alternative_line(choice: _ChoiceRender) -> _Builder:
    """`O.alternative.line` / `O.alternative.noChange` -- only the part that differs (contract
    §3.4).
    """
    builder = _Builder()
    builder.literal("- ")
    if choice.kind == "noChange":
        builder.literal("no change")
    else:
        _render_item_list(builder, choice.granted)
    return builder


def _replaced_key(choice: _ChoiceRender) -> tuple[tuple[str, int | None], ...]:
    return tuple((_name(i.item_name), i.count) for i in choice.replaced)


def _render_group_lines(group: OptionGroup) -> tuple[list[_Builder], list[str]]:
    """Renders one option group's own lines (stem then alternatives, or one line per choice),
    per contract §4.3/§4.4/§4.5. Returns `(lines, omitted_codes)`; `lines` is empty exactly when
    the whole group is omitted.
    """
    omitted: list[str] = []
    subject = _Builder()
    subject_code = _render_subject(subject, group)
    if subject_code is not None:
        # A subject that does not resolve omits the WHOLE group (§4.3 rows 5, 8) -- its choices
        # are never evaluated, per the O-007 fixture's own evidence (see .impl-progress.md).
        return [], [subject_code]

    resolved: list[_ChoiceRender] = []
    for choice in group.choices:
        classified = _classify_choice(choice)
        if isinstance(classified, str):
            omitted.append(classified)
        else:
            resolved.append(classified)

    if not resolved:
        omitted.append("RND-OPT-NO-CHOICES")
        return [], omitted

    if len(resolved) == 1:
        line = subject.copy()
        _append_choice_tail(line, resolved[0])
        return [line], omitted

    replaced_sets = {_replaced_key(choice) for choice in resolved}
    if len(replaced_sets) == 1:
        shared_replaced = resolved[0].replaced
        if shared_replaced and (group.max_choices is None or group.max_choices == 1):
            stem = subject.copy()
            stem.literal(" can have ")
            _render_item_list(stem, shared_replaced)
            stem.literal(" replaced with one of the following:")
            return [stem, *(_render_alternative_line(c) for c in resolved)], omitted
        if not shared_replaced and (group.max_choices is None or group.max_choices == 1):
            stem = subject.copy()
            stem.literal(" can be equipped with one of the following:")
            return [stem, *(_render_alternative_line(c) for c in resolved)], omitted
        if not shared_replaced and group.max_choices is not None and group.max_choices > 1:
            stem = subject.copy()
            stem.literal(" can be equipped with up to ")
            stem.slot(str(group.max_choices), "maxChoices")
            stem.literal(" of the following:")
            return [stem, *(_render_alternative_line(c) for c in resolved)], omitted

    # Row 6: the honest fallback, and the table's unconditional final row (rule 9) -- every
    # choice renders as its own full sentence, repeating the group's own subject.
    lines: list[_Builder] = []
    for rendered_choice in resolved:
        line = subject.copy()
        _append_choice_tail(line, rendered_choice)
        lines.append(line)
    return lines, omitted


# ---------------------------------------------------------------------------------------------
# §4.6 An item constraint
# ---------------------------------------------------------------------------------------------


def _render_constraint(builder: _Builder, constraint: ItemConstraint) -> str | None:
    """Returns an `RND-*` omission code, or `None` on success (contract §4.6)."""
    if constraint.constraint_type == "not_replaceable":
        if constraint.model_name:
            builder.literal("The ")
            builder.slot(_name(constraint.item_name), "itemName")
            builder.literal(" of ")
            builder.slot(_name(constraint.model_name), "modelName")
            builder.literal(" cannot be replaced.")
            return None
        builder.slot(_name(constraint.item_name), "itemName")
        builder.literal(" cannot be replaced.")
        return None
    if constraint.constraint_type == "one_per_unit":
        builder.literal("Only one model in this unit can be equipped with ")
        builder.slot(_name(constraint.item_name), "itemName")
        builder.literal(".")
        return None
    return "RND-CST-UNKNOWN-TYPE"


# ---------------------------------------------------------------------------------------------
# §4.4 / §6 Option group ordering, nesting, and block assembly
# ---------------------------------------------------------------------------------------------


def render_options_block(
    option_groups: Sequence[OptionGroup], item_constraints: Sequence[ItemConstraint] = ()
) -> RenderResult:
    """The Wargear Options block: every option group's lines (stem then alternatives, nested
    children indented immediately after their parent, depth capped at 2), then every constraint
    line (contract §6 Block assembly).
    """
    by_id = {g.id: g for g in option_groups}
    children: dict[str | None, list[OptionGroup]] = {}
    for g in option_groups:
        children.setdefault(g.parent_group_id, []).append(g)
    for child_list in children.values():
        child_list.sort(key=lambda g: (g.line, g.id))

    depth_cache: dict[str, int | None] = {}

    def compute_depth(group_id: str, trail: frozenset[str]) -> int | None:
        """`None` means "part of a parent-chain cycle" (`RND-OPT-GROUP-CYCLE`)."""
        if group_id in depth_cache:
            return depth_cache[group_id]
        if group_id in trail:
            depth_cache[group_id] = None
            return None
        g = by_id[group_id]
        if g.parent_group_id is None or g.parent_group_id not in by_id:
            depth_cache[group_id] = 0
            return 0
        parent_depth = compute_depth(g.parent_group_id, trail | {group_id})
        result = None if parent_depth is None else min(parent_depth + 1, 2)
        depth_cache[group_id] = result
        return result

    numbered: list[tuple[int, _Builder]] = []
    omitted: list[str] = []
    visited: set[str] = set()

    def emit(g: OptionGroup) -> None:
        visited.add(g.id)
        depth = compute_depth(g.id, frozenset())
        if depth is None:
            omitted.append("RND-OPT-GROUP-CYCLE")
        else:
            group_lines, group_omitted = _render_group_lines(g)
            omitted.extend(group_omitted)
            for line in group_lines:
                numbered.append((depth, line))
        for child in children.get(g.id, []):
            if child.id not in visited:
                emit(child)

    roots = [
        g for g in option_groups if g.parent_group_id is None or g.parent_group_id not in by_id
    ]
    for g in sorted(roots, key=lambda g: (g.line, g.id)):
        if g.id not in visited:
            emit(g)
    # Any group not yet reached has a parent chain that is entirely a cycle (every member has a
    # valid, existing parent, so none of them qualified as a root above).
    for g in sorted(option_groups, key=lambda g: (g.line, g.id)):
        if g.id not in visited:
            emit(g)

    constraint_lines: list[_Builder] = []
    for constraint in sorted(
        item_constraints,
        key=lambda c: (_name(c.item_name), c.constraint_type, c.constraint_index),
    ):
        builder = _Builder()
        code = _render_constraint(builder, constraint)
        if code is not None:
            omitted.append(code)
        else:
            constraint_lines.append(builder)

    all_lines = [*numbered, *((0, line) for line in constraint_lines)]
    return _assemble([line for _, line in all_lines], omitted, [depth for depth, _ in all_lines])


def _assemble(
    lines: Sequence[_Builder], omitted: Sequence[str], depths: Sequence[int] | None = None
) -> RenderResult:
    """Joins rendered lines with `"\\n"`, no leading or trailing whitespace, applying two spaces
    of indentation per level of nesting depth (contract §6 Block assembly). Builds the segment
    stream and the canonical string from ONE pass, never two (§7.2).
    """
    segments: list[Segment] = []
    for index, line in enumerate(lines):
        if index > 0:
            segments.append(Segment("literal", "\n"))
        depth = depths[index] if depths is not None else 0
        if depth:
            segments.append(Segment("literal", " " * (depth * 2)))
        segments.extend(line.segments)
    canonical = "".join(segment.text for segment in segments)
    return RenderResult(canonical=canonical, segments=tuple(segments), omitted=tuple(omitted))


# ---------------------------------------------------------------------------------------------
# Bundle wire-form adapter (contract §2) -- used by the conformance test against
# `contracts/rendering-fixtures/cases.json`.
# ---------------------------------------------------------------------------------------------


def _composition_row_from_json(raw: Mapping[str, Any]) -> CompositionRow:
    return CompositionRow(
        line=raw["line"],
        model_name=raw.get("modelName"),
        min_count=raw.get("minCount"),
        max_count=raw.get("maxCount"),
    )


def _equipment_item_from_json(raw: Mapping[str, Any]) -> EquipmentItem:
    return EquipmentItem(
        item_index=raw["itemIndex"], item_name=raw["itemName"], count=raw.get("count")
    )


def _equipment_group_from_json(raw: Mapping[str, Any]) -> EquipmentGroup:
    return EquipmentGroup(
        id=raw["id"],
        line=raw["line"],
        applies_to=raw["appliesTo"],
        model_name=raw.get("modelName"),
        items=tuple(_equipment_item_from_json(item) for item in raw.get("items", [])),
    )


def _option_choice_item_from_json(raw: Mapping[str, Any]) -> OptionChoiceItem:
    return OptionChoiceItem(
        role=raw["role"],
        item_index=raw["itemIndex"],
        item_name=raw["itemName"],
        count=raw.get("count"),
    )


def _option_choice_from_json(raw: Mapping[str, Any]) -> OptionChoice:
    return OptionChoice(
        id=raw["id"],
        is_no_change=raw.get("isNoChange", False),
        items=tuple(_option_choice_item_from_json(item) for item in raw.get("items", [])),
    )


def _option_group_from_json(raw: Mapping[str, Any]) -> OptionGroup:
    return OptionGroup(
        id=raw["id"],
        line=raw["line"],
        scope=raw["scope"],
        scope_n=raw.get("scopeN"),
        eligible_model_name=raw.get("eligibleModelName"),
        eligible_max_count=raw.get("eligibleMaxCount"),
        is_per_model=raw.get("isPerModel"),
        max_choices=raw.get("maxChoices"),
        parent_group_id=raw.get("parentGroupId"),
        choices=tuple(_option_choice_from_json(choice) for choice in raw.get("choices", [])),
    )


def _item_constraint_from_json(raw: Mapping[str, Any]) -> ItemConstraint:
    return ItemConstraint(
        constraint_index=raw["constraintIndex"],
        constraint_type=raw["constraintType"],
        item_name=raw["itemName"],
        model_name=raw.get("modelName"),
    )


def render_case(block: str, data: Mapping[str, Any]) -> RenderResult:
    """Renders one `contracts/rendering-fixtures/cases.json` case's `input` object, dispatched by
    its `block` field (`'composition'` or `'options'`). Adapts the JSON bundle wire form
    (camelCase) onto this module's snake_case dataclasses -- a name-only mapping (contract §2),
    never a value change.
    """
    if block == "composition":
        composition = tuple(_composition_row_from_json(row) for row in data.get("composition", []))
        equipment_groups = tuple(
            _equipment_group_from_json(group) for group in data.get("equipmentGroups", [])
        )
        return render_composition_block(composition, equipment_groups)
    if block == "options":
        option_groups = tuple(
            _option_group_from_json(group) for group in data.get("optionGroups", [])
        )
        item_constraints = tuple(
            _item_constraint_from_json(c) for c in data.get("itemConstraints", [])
        )
        return render_options_block(option_groups, item_constraints)
    raise ValueError(f"unknown block kind: {block!r}")
