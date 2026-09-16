# AI-Assisted: Claude Code (model: Claude Sonnet 5) - 010 R13 task 3: the item-to-wargear-ability
# join -- the same normalised, faction-scoped, exactly-one-match join
# `options_link.py`'s `weapon_lines_named` already performs for weapon rows, applied to the
# curated `wargear_abilities` mapping task 2 built.
"""One join the source does not publish: an item's name to a curated wargear ability.

**Faction-scoped, exact name, never guessed.** An option choice item or a default-equipment item
whose name equals a curated `CuratedWargearAbility`'s own name or one of its aliases -- after
`normalize_name`, and nothing else -- links to it. `normalize_name` is the only comparison
allowed: no substring, no fuzzy match, no stripping of parentheticals. Zero matches is the
overwhelmingly common case (most items are weapons, and legitimately link nowhere), so it raises
no finding. Two-or-more matches is the advisory `WGA-LINK-AMBIGUOUS`, and the item ships
unlinked -- the identical `OPT-LINK-AMBIGUOUS` discipline applied to a third class.
"""

from __future__ import annotations

from collections.abc import Sequence

from pipeline.models.curated import CuratedWargearAbility
from pipeline.normalize.names import normalize_name


def wargear_ability_ids_named(
    name: str, faction_id: str, entries: Sequence[CuratedWargearAbility]
) -> list[str]:
    """Sorted ids of every entry whose `faction_id` matches and whose name or alias equals.

    Callers apply `ids[0] if len(ids) == 1 else None`: exactly one match links, zero or
    two-or-more ship unlinked.
    """
    needle = normalize_name(name)
    if not needle:
        return []
    return sorted(
        {
            entry.id
            for entry in entries
            if entry.faction_id == faction_id
            and (
                normalize_name(entry.name) == needle
                or any(normalize_name(alias) == needle for alias in entry.aliases)
            )
        }
    )
