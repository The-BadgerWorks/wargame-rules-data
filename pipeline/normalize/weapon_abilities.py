# AI-Assisted: Claude Code (model: claude-opus-5) - Added the weapon-ability-keyword field
# reader shared by both detail modes (issue #4): the bracketed-group rule that recovers
# Rapid Fire N / Lethal Hits / Anti-X N+ from the export's `description` field without ever
# carrying the prose that field also holds.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 PR32: bounded the bracket-free
# acceptance (Finding B's fix had none -- a comma-split publisher sentence with no terminal
# punctuation read straight through as ability keywords) and made the punctuation guard
# per-item so one stray period no longer empties every keyword on the row.
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

**The bracket-free rule is bounded per item, not just per row (009 PR32).** Finding B's fix
established that the real bulk export states its keyword list bare, with no bracket; its own
guard -- "no sentence-final punctuation anywhere in the field" -- has no bound on what a
comma-split fragment may contain, so a publisher sentence with an internal comma and no
terminal punctuation (invented example, shaped like rules text: ``"Each time this weapon
targets a unit within 6 inches, that unit suffers a mortal wound on a roll of 4 or more"``) read
straight through as two ability keywords: an IP-boundary violation, not a parsing edge case. The
bound chosen is a per-item ceiling of
:data:`_MAX_UNBRACKETED_ITEM_WORDS` words and :data:`_MAX_UNBRACKETED_ITEM_LENGTH` characters,
measured from the only keyword-shaped vocabulary this repository holds in usable form --
``curation/glossary.json``'s 70 approved entries (a live bulk-export corpus is not available
outside a network-connected run, so the glossary is the real distribution on hand). Every
approved entry's printed form (parameter placeholder included, e.g. ``"Anti-Epic Hero X+"``,
``"Devastating Wounds: Monster/Vehicle"``) tops out at 3 words / 35 characters; the ceiling of
4 words / 40 characters keeps headroom for a real keyword not yet authored while still
rejecting anything sentence-shaped -- the shorter half of the invented sentence above is still
10 words / 52 characters, well past the ceiling. Matching against the glossary's vocabulary
directly was considered and
rejected: an unauthored keyword is expected to ship with no glossary row at all
(:func:`pipeline.build.bundle_emit._emit_keyword_glossary`), so an allow-list would silently
drop a real, currently-unauthored keyword -- the opposite failure from the one this bound
exists to close.

The punctuation guard from Finding B's fix is kept, but applied **per item, not per row**: one
unusable item must not empty every other keyword on the same row. A single trailing period is
forgiven only on the last item of a field that a separator actually split (the shape a bare
list's own end-of-row artifact would take); a lone field with no separator and a trailing
period, or any ``!``/``?`` anywhere, still disqualifies -- that shape is indistinguishable from
an ordinary sentence.
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

#: Per-item bound on a bracket-free field (009 PR32). Measured from `curation/glossary.json`'s
#: 70 approved entries, the only keyword-shaped vocabulary this repository holds in usable form:
#: every entry's printed form (parameter placeholder included) tops out at 3 words / 35
#: characters. 4 words / 40 characters keeps headroom for a real keyword not yet authored while
#: still rejecting anything sentence-shaped -- see the module docstring for the full measurement.
_MAX_UNBRACKETED_ITEM_WORDS: Final = 4
_MAX_UNBRACKETED_ITEM_LENGTH: Final = 40


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


def _clean(part: str) -> str:
    """Collapse internal whitespace and trim -- the one normalisation every part gets."""
    return _WHITESPACE_RUN.sub(" ", part).strip()


def _bracket_free_item(part: str, *, is_last: bool, multi_item: bool) -> str | None:
    """One bracket-free item, or ``None`` if it fails the bound (009 PR32).

    A single trailing period is forgiven only on the last item of a field a separator actually
    split -- the shape a bare list's own end-of-row artifact takes (``"Assault, Rapid Fire 1."``
    must still yield both keywords). A lone field with no separator at all gets no such
    forgiveness: a trailing period there is indistinguishable from an ordinary sentence, and any
    ``!``/``?`` anywhere never gets forgiveness regardless of position -- this repository's
    keyword vocabulary never prints either character.
    """
    cleaned = _clean(part)
    if is_last and multi_item and cleaned.endswith("."):
        cleaned = cleaned[:-1].rstrip()
    if not cleaned or _SENTENCE_PUNCTUATION.search(cleaned):
        return None
    if (
        len(cleaned.split()) > _MAX_UNBRACKETED_ITEM_WORDS
        or len(cleaned) > _MAX_UNBRACKETED_ITEM_LENGTH
    ):
        return None
    return cleaned


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
    selects the same splitting rule applied to the whole field, with each resulting item bound
    per :func:`_bracket_free_item` (009 PR32) rather than the field checked once as a whole — a
    bracket-free field is only as trustworthy as its least trustworthy item, and one prose-shaped
    item must not cost the row every other, genuine keyword on it.
    """
    if not description:
        return ()

    bracket_free = "[" not in description
    groups: Iterable[str] = (description,) if bracket_free else _GROUP.findall(description)

    keywords: list[str] = []
    seen: set[str] = set()
    for group in groups:
        parts = _split_group(group)
        multi_item = bracket_free and len(parts) > 1
        for index, part in enumerate(parts):
            if bracket_free:
                keyword = _bracket_free_item(
                    part, is_last=index == len(parts) - 1, multi_item=multi_item
                )
            else:
                keyword = _clean(part) or None
            if keyword is None:
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
