# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added the Cyrillic/Latin homoglyph fold to
# the normalize stage, so a detail-source name whose only defect is a look-alike character
# reaches the curated tree as the Latin name it was always meant to be, rather than as a
# blocking CON-IP-BOUNDARY the IP scan cannot tell apart from a real Cyrillic artefact.
"""Fold Cyrillic look-alike characters back to Latin in an otherwise-Latin name.

**Why this exists.** The detail source's own export carries a handful of names whose leading
character is a Cyrillic letter that renders identically to its Latin twin — the observed case is
a combi-weapon name beginning with ``U+0421 CYRILLIC CAPITAL LETTER ES`` where
``U+0043 LATIN CAPITAL LETTER C`` was meant. Nothing downstream can distinguish that from a
genuine Cyrillic scraper artefact: :mod:`pipeline.validate.ip_scan` raises the same blocking
``CON-IP-BOUNDARY`` for both, correctly, because it is not the scanner's job to guess which
Cyrillic character was a typing slip. The fix belongs **upstream of the scanner**, in the one
stage still permitted to read the source's own text, so the scanner sees already-clean names and
keeps working exactly as designed.

**The heuristic, and why it is deliberately timid.** A fold only happens when every one of the
following holds:

1. the string contains at least one Cyrillic character (otherwise there is nothing to do);
2. **every** Cyrillic character in it has a Latin homoglyph in :data:`CYRILLIC_TO_LATIN` — one
   unmappable Cyrillic letter means the string is Cyrillic *text*, not a Latin name with a
   slipped keystroke;
3. it carries at least :data:`MIN_LATIN_LETTERS` Latin letters, so there is real evidence the
   string is Latin-script in the first place;
4. there are at most :data:`MAX_INTERLOPERS` Cyrillic characters in absolute terms; and
5. they are at most :data:`MAX_INTERLOPER_SHARE` of the string's letters.

Conditions 3-5 are what keep the fold off a string that is genuinely Cyrillic. An all-Cyrillic
word made entirely of homoglyphs would otherwise be silently transliterated into a plausible-
looking Latin word — the worst possible outcome, because the result looks correct. The observed
classification artefacts (``Special (...)`` with a Cyrillic parenthetical) fail conditions 2 and
5 together, so they stay exactly as published and remain the business of
:mod:`pipeline.normalize.ability_types` and the IP scan, unchanged.

**Direction is one-way and Cyrillic-only.** Latin is never rewritten to Cyrillic, and no other
script is folded — Greek look-alikes are not in the scanned classes and have never been observed
here, and mapping a script nothing reports on would be a transform nobody could review against
evidence.
"""

from __future__ import annotations

import re
from typing import Final

#: Cyrillic characters that render identically — not merely similarly — to a Latin letter, and
#: the Latin letter each becomes. Every row names its key's Unicode character in a trailing
#: comment, because a table of look-alikes is otherwise unreviewable: the two columns are
#: *supposed* to be indistinguishable on screen, so the name is the only thing a reader can
#: check. Pairs that merely resemble each other are deliberately absent — Cyrillic `к` is not
#: Latin `k` at any normal size, and folding it would rewrite real Cyrillic text.
CYRILLIC_TO_LATIN: Final[dict[str, str]] = {
    # Uppercase.
    "А": "A",  # CYRILLIC CAPITAL LETTER A
    "В": "B",  # CYRILLIC CAPITAL LETTER VE
    "Е": "E",  # CYRILLIC CAPITAL LETTER IE
    "К": "K",  # CYRILLIC CAPITAL LETTER KA
    "М": "M",  # CYRILLIC CAPITAL LETTER EM
    "Н": "H",  # CYRILLIC CAPITAL LETTER EN
    "О": "O",  # CYRILLIC CAPITAL LETTER O
    "Р": "P",  # CYRILLIC CAPITAL LETTER ER
    "С": "C",  # CYRILLIC CAPITAL LETTER ES — the observed combi-weapon case
    "Т": "T",  # CYRILLIC CAPITAL LETTER TE
    "У": "Y",  # CYRILLIC CAPITAL LETTER U
    "Х": "X",  # CYRILLIC CAPITAL LETTER HA
    "Ѕ": "S",  # CYRILLIC CAPITAL LETTER DZE
    "І": "I",  # CYRILLIC CAPITAL LETTER BYELORUSSIAN-UKRAINIAN I
    "Ј": "J",  # CYRILLIC CAPITAL LETTER JE
    "Ѵ": "V",  # CYRILLIC CAPITAL LETTER IZHITSA
    "Ү": "Y",  # CYRILLIC CAPITAL LETTER STRAIGHT U
    "Ӏ": "I",  # CYRILLIC LETTER PALOCHKA
    "Ԍ": "G",  # CYRILLIC CAPITAL LETTER KOMI SJE
    "Ԛ": "Q",  # CYRILLIC CAPITAL LETTER QA
    "Ԝ": "W",  # CYRILLIC CAPITAL LETTER WE
    # Lowercase.
    "а": "a",  # CYRILLIC SMALL LETTER A
    "е": "e",  # CYRILLIC SMALL LETTER IE
    "о": "o",  # CYRILLIC SMALL LETTER O
    "р": "p",  # CYRILLIC SMALL LETTER ER
    "с": "c",  # CYRILLIC SMALL LETTER ES
    "у": "y",  # CYRILLIC SMALL LETTER U
    "х": "x",  # CYRILLIC SMALL LETTER HA
    "ѕ": "s",  # CYRILLIC SMALL LETTER DZE
    "і": "i",  # CYRILLIC SMALL LETTER BYELORUSSIAN-UKRAINIAN I
    "ј": "j",  # CYRILLIC SMALL LETTER JE
    "ѵ": "v",  # CYRILLIC SMALL LETTER IZHITSA
    "ү": "y",  # CYRILLIC SMALL LETTER STRAIGHT U
    "ӏ": "l",  # CYRILLIC SMALL LETTER PALOCHKA
    "ԍ": "g",  # CYRILLIC SMALL LETTER KOMI SJE
    "ԛ": "q",  # CYRILLIC SMALL LETTER QA
    "ԝ": "w",  # CYRILLIC SMALL LETTER WE
}

#: Every Cyrillic block, not only the mapped characters: an *unmapped* Cyrillic letter is the
#: signal that stops a fold, so it has to be seen. Deliberately wider than the scan's own class
#: (``pipeline.models.mechanical.NON_MECHANICAL_PATTERNS``) — noticing more can only make this
#: module refuse more often, which is the safe direction.
_CYRILLIC: Final = re.compile(r"[Ѐ-ӿԀ-ԯⷠ-ⷿꙀ-ꚟ]")

#: Latin letters. ASCII only: a name that needs accents has been through NFKD elsewhere.
_LATIN: Final = re.compile(r"[A-Za-z]")

#: The most look-alikes a fold will touch, in absolute terms. A "name" carrying four of them is
#: not a slipped keystroke; it is a different string, and a human should look at it.
MAX_INTERLOPERS: Final = 3

#: ...and at most this share of the string's letters, so length cannot smuggle in a rewrite.
MAX_INTERLOPER_SHARE: Final = 0.25

#: Below this many Latin letters there is not enough evidence the string is Latin-script at all.
#:
#: Arithmetically redundant — :data:`MAX_INTERLOPER_SHARE` already implies at least three Latin
#: letters whenever a fold happens — and stated separately anyway. The all-Cyrillic case is the
#: one whose failure mode is a silent, plausible-looking transliteration that nothing downstream
#: can flag, and it should take two independent loosenings to reach it, not one.
MIN_LATIN_LETTERS: Final = 3

_TRANSLATION: Final[dict[int, str]] = {ord(k): v for k, v in CYRILLIC_TO_LATIN.items()}


def has_homoglyphs(value: str) -> bool:
    """True when :func:`fold_homoglyphs` would change ``value``."""
    return fold_homoglyphs(value) != value


def fold_homoglyphs(value: str) -> str:
    """Return ``value`` with Cyrillic look-alikes mapped to Latin, or unchanged.

    Idempotent, and a no-op for every string that carries no Cyrillic at all — which is nearly
    all of them, so the cheap test comes first.
    """
    if not value:
        return value

    interlopers = _CYRILLIC.findall(value)
    if not interlopers:
        return value
    if any(character not in CYRILLIC_TO_LATIN for character in interlopers):
        return value

    latin_count = len(_LATIN.findall(value))
    if latin_count < MIN_LATIN_LETTERS:
        return value
    if len(interlopers) > MAX_INTERLOPERS:
        return value
    if len(interlopers) > MAX_INTERLOPER_SHARE * (latin_count + len(interlopers)):
        return value

    return value.translate(_TRANSLATION)
