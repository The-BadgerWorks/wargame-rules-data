# AI-Assisted: Claude Code (model: claude-opus-5) - Joined default-equipment sentences to
# composition rows and their items to weapon profiles (006 task T029): the exactly-one-match NAME
# join for `composition_line` with no ordinal fallback anywhere, and the per-item weapon join that
# reports what it could not resolve instead of dropping it.
"""Two joins the source does not publish, both refusing to guess.

**A sentence to a composition row (FR-013).** There is no foreign key. Research D1e measured what
a positional pairing would cost: 1 331 cards carry one composition line and one sentence, and
**195 carry two lines and one sentence** — so on one card in seven an ordinal pairing attaches the
squad's loadout to the leader, confidently and invisibly. The link is therefore the same
exactly-one-match *name* join :func:`pipeline.parse.composition_grammar.link_model_line` already
performs for composition itself, and there is deliberately no ordinal fallback for it to fall back
to. Zero or two-or-more matches omit the link and raise the advisory ``EQP-GROUP-UNRESOLVED``.

A sentence whose subject covers the whole unit is **not** a failed link and raises nothing: the
absence of ``composition_line`` beside ``applies_to = unit`` is the source's own statement. That
is exactly why ``applies_to`` is an explicit code rather than the presence of the link — a
nullable foreign key alone cannot tell *"this covers everything"* from *"I could not find it"*,
and FR-015 requires those two to be distinguishable.

**An item to a weapon row (FR-014).** `004`'s ``OPT-LINK-AMBIGUOUS`` discipline applied to a second
class: exactly one match links, zero or two-or-more ship the item **unlinked** with
``EQP-ITEM-UNLINKED``, and neither the item's siblings nor its group is discarded. One ambiguous
name in a loadout must not cost the whole loadout.

**Its own module, not a function in :mod:`pipeline.reconcile.options_link`**, for the reason `004`
kept ``composition_bands.py`` separate: different entities, different tables, different findings.
The two share :func:`pipeline.normalize.names.normalize_name` and nothing else.
"""

from __future__ import annotations

from collections.abc import Sequence

from pipeline.models.curated import (
    CuratedCompositionEntry,
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    CuratedWeaponLine,
    EquipmentAppliesTo,
)
from pipeline.models.findings import Finding
from pipeline.normalize.names import normalize_name
from pipeline.parse.composition_grammar import link_model_line
from pipeline.report.catalogue import build_finding


def link_equipment(
    *,
    datasheet_id: str,
    groups: Sequence[CuratedEquipmentGroup],
    composition: Sequence[CuratedCompositionEntry],
    weapons: Sequence[CuratedWeaponLine],
) -> tuple[list[CuratedEquipmentGroup], list[Finding]]:
    """Attach each sentence to the composition row it names and each item to its weapon row."""
    model_lines = {entry.line: entry.model_name for entry in composition}
    linked: list[CuratedEquipmentGroup] = []
    findings: list[Finding] = []

    for group in groups:
        update: dict[str, object] = {"items": _linked_items(group, weapons, datasheet_id, findings)}

        if group.applies_to is EquipmentAppliesTo.MODEL_GROUP and group.model_name is not None:
            composition_line = link_model_line(group.model_name, model_lines)
            if composition_line is None:
                findings.append(
                    build_finding(
                        "EQP-GROUP-UNRESOLVED",
                        entity_refs=[datasheet_id, group.id],
                        detail={
                            "datasheet_id": datasheet_id,
                            "equipment_group_id": group.id,
                            "line": group.line,
                        },
                    )
                )
            else:
                update["composition_line"] = composition_line

        linked.append(group.model_copy(update=update))

    return linked, findings


def _linked_items(
    group: CuratedEquipmentGroup,
    weapons: Sequence[CuratedWeaponLine],
    datasheet_id: str,
    findings: list[Finding],
) -> tuple[CuratedEquipmentItem, ...]:
    items: list[CuratedEquipmentItem] = []
    for item in group.items:
        matches = _weapon_lines_named(item.item_name, weapons)
        if len(matches) != 1:
            findings.append(
                build_finding(
                    "EQP-ITEM-UNLINKED",
                    entity_refs=[datasheet_id, group.id],
                    detail={
                        "datasheet_id": datasheet_id,
                        "equipment_group_id": group.id,
                        "item_index": item.item_index,
                        "match_count": len(matches),
                    },
                )
            )
            items.append(item)
            continue
        items.append(item.model_copy(update={"weapon_line": matches[0]}))
    return tuple(items)


def _weapon_lines_named(name: str, weapons: Sequence[CuratedWeaponLine]) -> list[int]:
    needle = normalize_name(name)
    if not needle:
        return []
    return sorted({weapon.line for weapon in weapons if normalize_name(weapon.name) == needle})
