# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented numeric coercion (task T062):
# points, model counts, DP, wounds and characteristic strings, rejecting rather than defaulting
# on an unparseable value.
"""Coerce the sources' numeric and characteristic fields.

**Rejecting rather than defaulting is the whole design.** A `0` where a points cost should be
is a unit a player can take for free; a `1` where an uncurated copy limit should be is a rule
enforced against a player that nobody ever wrote down. FR-019 makes absence meaningful, so an
unparseable value raises here and becomes a finding, and an *absent* value is returned as
``None`` and omitted downstream.

Characteristics stay **strings** on purpose. `6"`, `3+`, `D6+1` and `-` are the printed forms
the consumer contract stores and the app displays; parsing them into numbers would lose the
distinction between "2 attacks" and "D6 attacks" and gain nothing, since no rule in `001` does
arithmetic on them.
"""

from __future__ import annotations

import re
from typing import Final

#: A plain integer, optionally signed. Surrounding whitespace and thin/space separators are
#: tolerated because they are typography, not data.
_INTEGER: Final = re.compile(r"^[+-]?\d+$")

#: A footnote marker the detail source appends to a characteristic, e.g. `5*`. It marks "see the
#: datasheet's note", which is prose we do not carry; the number in front of it is still the
#: number.
_FOOTNOTE: Final = re.compile(r"[*†‡]+$")

#: A leading count in a free-text label or composition line: `5 models`, `3-6 Ember Sentinels`.
_LEADING_COUNT: Final = re.compile(r"^\s*(\d+)\s*(?:-\s*(\d+))?")

#: An `n-m` range, as `damaged_w` publishes it.
_RANGE: Final = re.compile(r"^\s*(\d+)\s*-\s*(\d+)\s*$")


class NumericParseError(ValueError):
    """A field that should carry a number does not, and no default is available.

    Deliberately not a finding: a finding is something a run reports and continues past, and a
    points cost that cannot be read is not something a run can honestly continue past.
    """


def _clean(raw: str) -> str:
    return _FOOTNOTE.sub("", raw.replace(" ", " ").replace(" ", " ").strip())


def to_int(raw: str, *, field: str) -> int:
    """Parse a required integer, or raise. The diagnostic names the field, never the value."""
    cleaned = _clean(raw)
    if not _INTEGER.match(cleaned):
        raise NumericParseError(
            f"{field}: expected an integer, got a {len(cleaned)}-character value that is not one"
        )
    return int(cleaned)


def optional_int(raw: str | None, *, field: str) -> int | None:
    """Parse an optional integer. Empty is **absent**, never zero (FR-019)."""
    if raw is None or not _clean(raw):
        return None
    return to_int(raw, field=field)


def upper_bound(raw: str | None, *, field: str) -> int | None:
    """Parse `n` or `n-m` to its upper bound; empty is absent.

    The detail source publishes a damaged-state threshold as the wound *range* it applies over,
    so the threshold the consumer contract wants is the top of that range.
    """
    if raw is None or not _clean(raw):
        return None
    cleaned = _clean(raw)
    ranged = _RANGE.match(cleaned)
    if ranged:
        return int(ranged.group(2))
    return to_int(cleaned, field=field)


def leading_count(text: str) -> tuple[int | None, int | None]:
    """The leading `n` or `n-m` of a free-text label, as ``(minimum, maximum)``.

    Used for both the points source's band labels (`5 models`) and the detail source's
    composition lines (`3-6 Ember Sentinels`). A line that opens with no number yields
    ``(None, None)`` — an advisory class, not a failure (FR-027).
    """
    match = _LEADING_COUNT.match(text)
    if match is None:
        return None, None
    low = int(match.group(1))
    high = int(match.group(2)) if match.group(2) else None
    return low, high


def model_count(label: str, *, field: str) -> int:
    """The number of models a points-source band label states, e.g. `5 models` -> 5.

    A **composite** label names the unit's composition instead of its size, and then the band's
    model count is the total the label states rather than the first number in it:
    `1 Sword Brother, 4 Neophytes, 5 Initiates` is a ten-model band, not a one-model band.
    Reading only the leading integer collapsed that band and `1 Sword Brother, 8 Neophytes,
    11 Initiates` — ten models and twenty — onto the same key at two different prices, which is
    exactly what `REC-BAND-MISMATCH` had been reporting against those datasheets.

    Only segments that state a count are summed; a segment that states none contributes nothing
    rather than being guessed at. A label stating no count anywhere is still a parse failure.
    """
    counts = [
        count for segment in label.split(",") if (count := leading_count(segment)[0]) is not None
    ]
    if not counts:
        raise NumericParseError(f"{field}: the band label states no model count")
    return sum(counts)


def characteristic(raw: str, *, field: str) -> str:
    """A required printed characteristic, kept as its printed form."""
    value = raw.strip()
    if not value:
        raise NumericParseError(f"{field}: a required characteristic is empty")
    return value


def optional_characteristic(raw: str | None) -> str | None:
    """An optional printed characteristic. Empty and the source's `-` both mean **absent**.

    `-` is the source's way of writing "this model has none", and the consumer contract says an
    unknown invulnerable save is omitted rather than stored as `"-"` (§5).
    """
    if raw is None:
        return None
    value = raw.strip()
    return None if value in {"", "-", "–", "—"} else value
