# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the D5 name-normalisation ladder
# (task T061), with no stemming, singularisation, or synonym expansion.
"""Normalise a display name so two spellings of the same name compare equal.

The ladder, in order (research D5 stage 2):

1. Unicode NFKC, so compatibility forms and full-width characters converge;
2. strip combining marks, so `é` and `e` + combining acute agree;
3. casefold, so `ASSAULT INTERCESSOR SQUAD` and `Assault Intercessor Squad` agree;
4. map typographic punctuation to ASCII, so `T’au` and `T'au` agree;
5. drop a leading `the `;
6. collapse every run of non-alphanumerics to one space;
7. trim.

**And nothing else.** No stemming, no singularisation, no synonym expansion. Those would fold
`Land Raider Crusader` and `Land Raider Redeemer` closer together, and the failure mode of this
function is not a missed match — that becomes a finding a human resolves once — it is a *wrong*
match, which becomes a silently mispriced unit in a player's hands at a tournament. The whole
matching ladder is built around never doing that (D5 stage 4).
"""

from __future__ import annotations

import re
import unicodedata
from typing import Final

#: Typographic forms mapped to their ASCII equivalents before the alphanumeric collapse. The
#: collapse would remove them anyway; doing it explicitly keeps the intent legible and makes the
#: dash and ellipsis cases survive as separators rather than disappearing mid-word.
_TYPOGRAPHIC: Final[dict[int, str]] = {
    ord("’"): "'",  # right single quotation mark — T’au
    ord("‘"): "'",
    ord("′"): "'",
    ord("ʼ"): "'",
    ord("“"): '"',
    ord("”"): '"',
    ord("–"): "-",  # en dash
    ord("—"): "-",  # em dash
    ord("−"): "-",  # minus sign
    ord("…"): "...",
}

_NON_ALNUM: Final = re.compile(r"[^a-z0-9]+")

_LEADING_ARTICLE: Final = "the "


def normalize_name(value: str) -> str:
    """Return the comparison form of a display name.

    Idempotent: normalising a normalised name returns it unchanged, which matters because
    authored aliases are stored normalised and re-normalised on read.
    """
    if not value:
        return ""

    composed = unicodedata.normalize("NFKC", value).translate(_TYPOGRAPHIC)
    decomposed = unicodedata.normalize("NFKD", composed)
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))

    folded = without_marks.casefold()
    if folded.startswith(_LEADING_ARTICLE):
        folded = folded[len(_LEADING_ARTICLE) :]

    return _NON_ALNUM.sub(" ", folded).strip()
