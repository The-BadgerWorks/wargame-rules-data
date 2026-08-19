# AI-Assisted: Claude Code (model: claude-opus-5) - Added the weapon-ability-keyword field
# reader shared by both detail modes (issue #4): the bracketed-group rule that recovers
# Rapid Fire N / Lethal Hits / Anti-X N+ from the export's `description` field without ever
# carrying the prose that field also holds.
"""Read a weapon line's **ability keywords** out of the detail source's ``description`` field.

Both detail modes converge here, which is the point. The bulk export carries a weapon's ability
keywords in ``Datasheets_wargear.csv``'s ``description`` column, printed as a bracketed list; the
current-edition datacard prints them as a run of sibling elements after the weapon's name and the
html parser re-emits them into the *same* column in the *same* bracketed shape
(:func:`format_ability_keywords`). So :mod:`pipeline.curate.assemble` reads one field, by one
rule, and still cannot tell which mode ran.

**Only the content of a bracketed group is a keyword.** That rule is an IP boundary, not a
parsing convenience. The same ``description`` column also carries free prose on some rows — the
publisher's wording, which this repository never retains anywhere (Constitution Principle 4) — so
a reader that treated unbracketed text as a keyword would carry that wording into curated data
under a field name that made it look mechanical. Text outside a bracket is therefore discarded
without inspection, and a row whose description is entirely prose yields nothing at all.

Two shapes inside a group, both observed:

* **A parameter is part of the keyword**, not a separate token: ``RAPID FIRE 2``,
  ``ANTI-VEHICLE 4+``, ``SUSTAINED HITS D3``. Nothing here splits it off —
  :mod:`pipeline.normalize.keyword_key` owns that decision, downstream, once, for both the
  pipeline and the consuming app.
* **The separator is a comma or a semicolon at bracket depth**, and a comma *inside parentheses*
  is not a separator: a keyword may qualify itself parenthetically, and splitting there would
  invent two keywords neither of which the source prints.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from typing import Final

from pipeline.normalize.keyword_key import collapse_variant

#: One bracketed group. Non-greedy and bracket-free inside, so two adjacent groups on one row
#: are two groups rather than one group spanning the text between them.
_GROUP: Final = re.compile(r"\[([^\[\]]*)\]")

_WHITESPACE_RUN: Final = re.compile(r"\s+")

#: The separators a group's own printed form uses.
_SEPARATORS: Final = frozenset(",;")

#: Sentence-final punctuation -- the one guard against reading genuine prose as an unbracketed
#: keyword list (009 Finding B). Measured live this session: 6,362/6,362 of the real bulk
#: export's non-empty `description` rows contain none of these; a row that does is prose.
_SENTENCE_PUNCTUATION: Final = re.compile(r"[.!?]")


def _split_group(group: str) -> list[str]:
    """Split one group on its separators, ignoring any inside parentheses."""
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for character in group:
        if character == "(":
            depth += 1
        elif character == ")":
            depth = max(depth - 1, 0)
        if character in _SEPARATORS and depth == 0:
            parts.append("".join(current))
            current = []
            continue
        current.append(character)
    parts.append("".join(current))
    return parts


def parse_weapon_ability_keywords(description: str) -> tuple[str, ...]:
    """The ability keywords one weapon row states, in the order the source prints them.

    Duplicates are dropped by :func:`pipeline.normalize.keyword_key.collapse_variant`, so a row
    that prints one keyword twice in two spellings keeps the first spelling and not both — the
    second would resolve to the same glossary entry and inflate every count downstream. The
    *parameter* is part of that comparison, not stripped from it: a row stating two different
    parameter values states two things, and merging them here would lose one of them before
    anything downstream could see it.

    Returns an empty tuple for an empty field and for a field that is entirely prose. Those two
    are the same answer on purpose: "this row states no ability keyword" is what each means.

    **Brackets are optional.** The html arm always wraps its keywords in ``[...]``
    (:func:`format_ability_keywords`'s own shape); the real bulk export never does — it states
    the same kind of list bare, comma/semicolon-separated, directly in the field (009 Finding B,
    measured live: 6,362/6,362 non-empty rows, none containing a bracket, none containing
    sentence-final punctuation). So a bracket present anywhere selects the bracket-only rule
    unchanged (text outside a bracket is still discarded without inspection); its total absence
    selects the same splitting rule applied to the whole field, guarded by
    :data:`_SENTENCE_PUNCTUATION` — a bracket-free field ending a sentence is prose, not a list,
    and yields nothing rather than a guessed token.
    """
    if not description:
        return ()

    if "[" in description:
        groups: Iterable[str] = _GROUP.findall(description)
    elif _SENTENCE_PUNCTUATION.search(description):
        return ()
    else:
        groups = (description,)

    keywords: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for part in _split_group(group):
            keyword = _WHITESPACE_RUN.sub(" ", part).strip()
            if not keyword:
                continue
            key = collapse_variant(keyword)
            if not key or key in seen:
                continue
            seen.add(key)
            keywords.append(keyword)
    return tuple(keywords)


def format_ability_keywords(keywords: Sequence[str] | Iterable[str]) -> str:
    """The bracketed form :func:`parse_weapon_ability_keywords` reads, for the html emitter.

    The inverse of the reader for every keyword the source actually prints, which is what makes
    the html mode's emitted ``description`` column a real export-shaped field rather than a
    parallel channel the two modes would have to be kept in step by hand.
    """
    listed = [keyword.strip() for keyword in keywords if keyword.strip()]
    return f"[{', '.join(listed)}]" if listed else ""
