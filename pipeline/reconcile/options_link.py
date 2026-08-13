# AI-Assisted: Claude Code (model: claude-opus-5) - Joined option choices to weapon profiles and
# to the priced projection (004 task T030): the normalised-name join with exactly-one-match
# linking, OPT-LINK-AMBIGUOUS on zero or many, and guarantee 8's priced projection — which is
# implemented by linking TO the pre-existing CuratedWargearOption producer and never touching it.
"""Two joins the source does not publish, both refusing to guess.

**Choice to weapon profile (FR-011).** There is no foreign key, and the wargear rows have no
stable row key — ``(datasheet_id, line, line_in_wargear, name)`` is *still* not unique, with up
to 18 rows sharing a triple. The only viable join is the normalised name. 81.2% of measured
option rows contain an exact wargear name from the same datasheet. Where **exactly one** row
matches, the choice carries the line; where zero or two or more do, it ships **unlinked** with
an advisory, per FR-011's "never guessed and never silently attached to the wrong profile".

**Choice to priced option (guarantee 8, FR-012..FR-014).** The direction matters and runs one
way: a choice points at a priced option, never the reverse.
:func:`pipeline.curate.assemble._costs` keeps building ``CuratedWargearOption`` from the points
source's ``+``-prefixed rows exactly as it did, with the same fields, the same producer and the
same id scheme. **Preserving that representation by not touching it** is what makes SC-004's
byte-identical row set a structural guarantee rather than a test that happens to pass.

What follows from that:

* a priced option matching exactly one choice — the choice adopts the delta and the id (FR-012);
* a choice with no matching priced option — **no ``points_delta`` field at all**, omitted rather
  than zero, so a consumer reports it as uncosted and never as free (FR-013);
* a priced option matching no choice — ``OPT-PRICED-UNMATCHED``, **advisory**: the priced row
  still ships and still prices correctly, so blocking would stall a release on a parse tail;
* a priced option matching *several* choices — the same advisory, and **none** of them is
  linked. Guarantee 8 allows at most one choice per priced row, and picking one would be the
  guess this module exists to refuse;
* the two disagreeing about the same option's cost or count — ``OPT-PROJECTION-DISAGREE``,
  **blocking**, because FR-014 says so in terms.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from pipeline.models.curated import (
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedWargearOption,
    CuratedWeaponLine,
    OptionItemRole,
)
from pipeline.models.findings import Finding
from pipeline.normalize.names import normalize_name
from pipeline.parse.options_grammar import OptionVerb
from pipeline.report.catalogue import build_finding


def link_choice_weapons(
    *,
    datasheet_id: str,
    choices: Sequence[CuratedOptionChoice],
    verbs: Mapping[str, OptionVerb],
    weapons: Sequence[CuratedWeaponLine],
) -> tuple[list[CuratedOptionChoice], list[Finding]]:
    """Attach each choice to the weapon row it names, or report that it could not be.

    ``verbs`` maps a choice id to the clause verb that produced it, which is what decides
    whether the matched line lands in ``grants_weapon_line`` or in ``replaces_weapon_line``.
    A choice carrying ``is_no_change`` is skipped in silence: "take nothing" names no weapon, so
    an unlinked-name finding for it would be noise in a report whose value is its signal.
    """
    linked: list[CuratedOptionChoice] = []
    findings: list[Finding] = []

    for choice in choices:
        if choice.is_no_change:
            linked.append(choice)
            continue

        matches = _weapon_lines_named(choice.name, weapons)
        if len(matches) != 1:
            findings.append(
                build_finding(
                    "OPT-LINK-AMBIGUOUS",
                    entity_refs=[datasheet_id, choice.id],
                    detail={
                        "datasheet_id": datasheet_id,
                        "choice_id": choice.id,
                        "match_count": len(matches),
                    },
                )
            )
            linked.append(choice)
            continue

        field = (
            "replaces_weapon_line"
            if verbs.get(choice.id) is OptionVerb.REPLACE
            else "grants_weapon_line"
        )
        linked.append(choice.model_copy(update={field: matches[0]}))

    return linked, findings


def link_choice_items(
    *,
    datasheet_id: str,
    choices: Sequence[CuratedOptionChoice],
    weapons: Sequence[CuratedWeaponLine],
) -> tuple[list[CuratedOptionChoice], list[Finding]]:
    """Link each bundle item on its own, then check the two representations agree (`006`).

    **The same join, applied per item.** :func:`link_choice_weapons` above is untouched and stays
    untouched: it is what sets the singular fields `004` publishes, and FR-009 is a promise about
    those values. This function reads them, never rewrites them, and adds a second array beside
    them.

    Three rules, and each one is a decision the design makes explicitly:

    * **Exactly one match links; zero or two-or-more ship unlinked** with the advisory
      ``OPT-BUNDLE-UNLINKED``, per item. Neither the item's siblings nor its choice is discarded
      — one ambiguous name in a bundle must not cost the whole swap (FR-007).
    * **A sole item supplies the singular field it mirrors**, where the baseline left it absent.
      A distributive stem names the removed weapon in its own head rather than in its object
      clause, so the item is the only place that link can come from; leaving it absent would
      publish a one-element bundle that disagrees with its own choice by omission.
    * **A multi-item side carries no singular field at all**, and one that contradicts its items
      raises the blocking ``OPT-BUNDLE-DISAGREE`` (guarantee 12). The field is never *repaired*
      from the items: a contradiction between two representations of one swap is a defect to be
      read, not a value to be picked.
    """
    linked: list[CuratedOptionChoice] = []
    findings: list[Finding] = []

    for choice in choices:
        items: list[CuratedOptionChoiceItem] = []
        for item in choice.items:
            matches = _weapon_lines_named(item.item_name, weapons)
            if len(matches) != 1:
                findings.append(
                    build_finding(
                        "OPT-BUNDLE-UNLINKED",
                        entity_refs=[datasheet_id, choice.id],
                        detail={
                            "datasheet_id": datasheet_id,
                            "choice_id": choice.id,
                            "role": item.role.value,
                            "item_index": item.item_index,
                            "match_count": len(matches),
                        },
                    )
                )
                items.append(item)
                continue
            items.append(item.model_copy(update={"weapon_line": matches[0]}))

        update: dict[str, object] = {"items": tuple(items)}
        for role, field in (
            (OptionItemRole.GRANTED, "grants_weapon_line"),
            (OptionItemRole.REPLACED, "replaces_weapon_line"),
        ):
            side = [item for item in items if item.role is role]
            stated = getattr(choice, field)
            disagreement = _bundle_disagreement(side, stated)
            if disagreement is not None:
                findings.append(
                    build_finding(
                        "OPT-BUNDLE-DISAGREE",
                        entity_refs=[datasheet_id, choice.id],
                        detail={
                            "datasheet_id": datasheet_id,
                            "choice_id": choice.id,
                            "field": field,
                            **disagreement,
                        },
                    )
                )
                continue
            if stated is None and len(side) == 1 and side[0].weapon_line is not None:
                update[field] = side[0].weapon_line

        linked.append(choice.model_copy(update=update))

    return linked, findings


def _bundle_disagreement(
    side: Sequence[CuratedOptionChoiceItem], stated: int | None
) -> dict[str, int | str] | None:
    """Guarantee 12, asserted in both directions.

    A singular field is a claim about a one-element bundle, so it is a contradiction both when
    the bundle has a different number of elements and when its one element names a different
    weapon. Checking only the first direction would pass a field pointing at a line its own item
    does not name, which is the wrong link — the exact failure the exactly-one-match rule exists
    to prevent.
    """
    if stated is None:
        return None
    if len(side) != 1:
        return {"item_count": len(side), "stated_weapon_line": stated}
    linked = side[0].weapon_line
    if linked is not None and linked != stated:
        return {"item_weapon_line": linked, "stated_weapon_line": stated}
    return None


def _weapon_lines_named(name: str, weapons: Sequence[CuratedWeaponLine]) -> list[int]:
    needle = normalize_name(name)
    if not needle:
        return []
    return sorted({weapon.line for weapon in weapons if normalize_name(weapon.name) == needle})


def project_priced_options(
    *,
    datasheet_id: str,
    choices: Sequence[CuratedOptionChoice],
    priced: Sequence[CuratedWargearOption],
) -> tuple[list[CuratedOptionChoice], list[Finding]]:
    """Carry each priced option's delta onto the one choice it prices. Guarantee 8."""
    findings: list[Finding] = []
    by_option: dict[str, list[CuratedOptionChoice]] = {option.id: [] for option in priced}
    by_choice: dict[str, list[CuratedWargearOption]] = {}

    for choice in choices:
        if choice.is_no_change:
            # An explicit "no change" alternative is never priced — the curated model refuses it
            # outright, because publishing one priced presents "take nothing" as a purchasable
            # item. It is therefore not a candidate for any priced row either.
            continue
        needle = normalize_name(choice.name)
        matches = sorted(
            (option for option in priced if normalize_name(option.name) == needle),
            key=lambda option: option.id,
        )
        by_choice[choice.id] = matches
        for option in matches:
            by_option[option.id].append(choice)

    adoptable = {option_id for option_id, matched in by_option.items() if len(matched) == 1}

    projected: list[CuratedOptionChoice] = []
    for choice in choices:
        matches = by_choice.get(choice.id, [])
        eligible = [option for option in matches if option.id in adoptable]
        if not eligible:
            projected.append(choice)
            continue

        disagreement = _disagreement(choice, eligible)
        if disagreement is not None:
            findings.append(
                build_finding(
                    "OPT-PROJECTION-DISAGREE",
                    entity_refs=[datasheet_id, choice.id],
                    detail={
                        "datasheet_id": datasheet_id,
                        "choice_id": choice.id,
                        **disagreement,
                    },
                )
            )
            projected.append(choice)
            continue

        option = eligible[0]
        projected.append(
            choice.model_copy(
                update={"points_delta": option.points_delta, "priced_option_id": option.id}
            )
        )

    findings.extend(
        build_finding(
            "OPT-PRICED-UNMATCHED",
            entity_refs=[datasheet_id, option.id],
            detail={
                "datasheet_id": datasheet_id,
                "priced_option_id": option.id,
                "match_count": len(by_option[option.id]),
            },
        )
        for option in sorted(priced, key=lambda option: option.id)
        if len(by_option[option.id]) != 1
    )

    return projected, findings


def _disagreement(
    choice: CuratedOptionChoice, eligible: Sequence[CuratedWargearOption]
) -> dict[str, int | str] | None:
    """Do the two representations contradict each other about this option? (FR-014)

    Two contradictions are reachable and both are blocking. **Cost**: two priced rows whose
    names normalise together but whose ids — and prices — differ, so there is no single delta to
    adopt. **Count**: the points source states how many of the item a unit may take and the
    detail source states a different number, which is a mispriced unit either way round.
    """
    deltas = sorted({option.points_delta for option in eligible})
    if len(deltas) > 1:
        return {
            "field": "points_delta",
            "priced_values": ",".join(str(delta) for delta in deltas),
        }

    option = eligible[0]
    if (
        option.max_per_unit is not None
        and choice.count is not None
        and option.max_per_unit != choice.count
    ):
        return {
            "field": "count",
            "priced_option_id": option.id,
            "priced_count": option.max_per_unit,
            "choice_count": choice.count,
        }
    return None
