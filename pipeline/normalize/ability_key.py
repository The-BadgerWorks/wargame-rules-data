# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 R6b Task 1: the single `ability_key`
# helper both minting call sites (`curate/assemble.py`, `curate/summaries.py`) now delegate to,
# joining a binding's `parameter` column into its name before slugifying so a Core or Faction
# key reproduces the published tree's parameterised form (`core:feel-no-pain-5`) instead of the
# CSV arm's bare `core:feel-no-pain` (round 6's Tier 1: 1150 missing `core:` bindings).
"""Mint an ability key exactly as the site publishes it.

The published tree's `core:` and `faction:` keys carry the ability's parameter where one exists
(`core:feel-no-pain-5`, `core:firing-deck-10`, `core:deadly-demise-d3`). The CSV export states
that parameter separately, in `Datasheets_abilities.csv`'s own `parameter` column — never in
`name`. Published keys are the identifiers of record, so the reader reproduces them by joining
the parameter into the name before slugifying, rather than slugifying the bare name alone.

This is the **only** function that may build an ability key. A key and its digest are minted at
two separate call sites (`curate/assemble.py`'s `ability_keys` list and `curate/summaries.py`'s
`compute_current_digests`), and if those two sites ever derived a key by different rules, a
digest would land under a key `ability_keys` never lists — silently orphaning a mechanic. Both
call sites delegate here so that cannot happen.

**Deliberately does no parenthesis handling.** A proposed extension — stripping one trailing
parenthesised group from the name — was measured against the live export and the published tree
and refuted: the published tree's keys *carry* the parenthetical tag, and stripping it would move
257 further published `datasheet:` keys and 4 `faction:` keys, which is a Tier 1 identifier move.
See `task-1-brief.md` for the measurement. Do not add parenthesis handling here.
"""

from __future__ import annotations

from pipeline.models.normalized import AbilityType
from pipeline.reconcile.identity import slugify


def ability_key(ability_type: AbilityType, name: str, *, parameter: str = "") -> str:
    """Reproduce the published ability key: ``<type>:<slug of name, parameter joined in>``.

    ``parameter`` is stripped and, when non-empty, appended to ``name`` with a single space
    before slugifying; an empty (or whitespace-only) parameter leaves the key bare. No other
    transformation — in particular, no parenthesis stripping (see module docstring).
    """
    p = parameter.strip()
    joined = f"{name} {p}" if p else name
    return f"{ability_type.value}:{slugify(joined)}"
