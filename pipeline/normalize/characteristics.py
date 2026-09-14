# AI-Assisted: Claude Opus 5 - 010 R6 task 5. Created to mint the published tree's printed
# characteristic forms from the export's bare values: 6 720 skill pairs and 4 257 range pairs
# differ from the published tree by format alone, plus 864 invulnerable-save and 2 015 base-size
# pairs. The parity target for the cutover is the published form (owner ruling); cleaning any of
# these up is a later, deliberate change, not this one.
"""The printed form of a characteristic, from whichever form the reader was handed.

One arm of the acquisition states the **printed** value — a skill of ``3+``, a range of ``12"``,
a base size of ``(⌀32mm)`` — and the other states the **bare** one — ``3``, ``12``, ``32mm``.
The published tree carries the printed form, so the bare value is completed here rather than in
either arm's reader, which is what keeps the decision out of a mode branch (standing rule 6).

Every function is **pure and idempotent**: an already-printed value is returned unchanged, so a
value may pass through twice without growing a second suffix, and neither caller has to know
which arm produced it.

Only a bare integer is completed. A value that is not one — the source's ``-``, an ``N/A``, a
word — is not a number missing its suffix and is returned exactly as stated; guessing at one
would invent a characteristic no source published (standing rule 10).
"""

from __future__ import annotations

import re
from typing import Final

#: A bare, unsigned integer — the one shape that is a printed characteristic with its suffix
#: missing. Deliberately the only pattern in this module.
_BARE_INTEGER: Final = re.compile(r"^\d+$")

#: The published tree's base-size wrapper: an open parenthesis, a diameter sign, the measurement.
_BASE_SIZE_PREFIX: Final = "(⌀"
_BASE_SIZE_SUFFIX: Final = ")"


def printed_roll(value: str) -> str:
    """A roll characteristic (skill, invulnerable save) in its printed form: ``3`` -> ``3+``."""
    return f"{value}+" if _BARE_INTEGER.match(value) else value


def printed_range(value: str) -> str:
    """A range characteristic in its printed form: ``12`` -> ``12"``."""
    return f'{value}"' if _BARE_INTEGER.match(value) else value


def printed_base_size(value: str | None) -> str | None:
    """A base size in its published wrapper: ``32mm`` -> ``(⌀32mm)``. Absent stays absent."""
    if value is None:
        return None
    if value.startswith(_BASE_SIZE_PREFIX) and value.endswith(_BASE_SIZE_SUFFIX):
        return value
    return f"{_BASE_SIZE_PREFIX}{value}{_BASE_SIZE_SUFFIX}"
