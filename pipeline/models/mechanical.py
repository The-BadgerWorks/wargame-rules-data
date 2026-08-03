# AI-Assisted: Claude Code (model: claude-opus-5) - Shared mechanical-string guard backing the
# "no field typed to hold prose" invariant used by the finding detail (task T025) and the run
# ledger (task T031); the same quirk classes the IP scan (V8) asserts zero of.
"""The shared guard for "this string carries a mechanical value, not prose".

Downstream of ``normalize`` nothing may hold publisher wording (FR-013). Two independent
controls back that: there is nowhere to *put* prose (no prose-typed field anywhere in
:mod:`pipeline.models`), and a scan proves the absence. This module is the predicate both the
typed records and the scan use, so "mechanical" means one thing in this repository.

The quirk classes are the ones actually observed in the sources (research §0.1):

* markup — ``<span class="kwb">`` reaches even ``unit_composition``;
* HTML entities — the residue of a half-stripped field;
* unresolved ``$`` placeholder tokens;
* Cyrillic scraper artefacts — ``Special (правая колонка)`` and friends;
* over-length text — the length at which a "name" has stopped being a name.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Final

#: The length above which a value has stopped being a name, label, or code. Aligned with the
#: ability-summary target (``WGC_SUMMARY_MAX_CHARS``, FR-022), which is the longest authored
#: string the contract permits anywhere.
MECHANICAL_STRING_MAX_CHARS: Final = 240

#: reason -> pattern. Every one of these is a class observed in a real source (research §0.1).
NON_MECHANICAL_PATTERNS: Final[Mapping[str, re.Pattern[str]]] = {
    "markup": re.compile(r"</?[A-Za-z][A-Za-z0-9]*[\s/>]"),
    "html_entity": re.compile(r"&(?:[A-Za-z][A-Za-z0-9]{1,31}|#[0-9]{1,7}|#[Xx][0-9A-Fa-f]{1,6});"),
    "placeholder_token": re.compile(r"\$[A-Za-z_{]"),
    "cyrillic": re.compile(r"[Ѐ-ӿ]"),
}

#: What a mechanical field may hold: ids, names, numbers, enumerated codes, and lists of those.
type MechanicalScalar = str | int | bool
type MechanicalValue = MechanicalScalar | Sequence[MechanicalScalar]


class NonMechanicalValueError(ValueError):
    """A value carrying markup, an entity, a ``$`` token, a Cyrillic artefact, or prose.

    Raised at the typed boundary rather than caught by a scan later, so the offending value
    never reaches a report, a log, or the curated tree in the first place (FR-013).
    """


def mechanical_violations(value: str, *, max_chars: int = MECHANICAL_STRING_MAX_CHARS) -> list[str]:
    """Return the reasons ``value`` is not a mechanical string; empty when it is one.

    The reasons are returned as *codes*, never with the offending substring quoted — a
    diagnostic that quotes source text is itself a leak (``validation-report.md`` §1.4: quote
    the shape, never the content).
    """
    reasons = [
        reason for reason, pattern in NON_MECHANICAL_PATTERNS.items() if pattern.search(value)
    ]
    if len(value) > max_chars:
        reasons.append("over_length")
    return sorted(reasons)


def is_mechanical_string(value: str, *, max_chars: int = MECHANICAL_STRING_MAX_CHARS) -> bool:
    """True when ``value`` carries a mechanical value only."""
    return not mechanical_violations(value, max_chars=max_chars)


def assert_mechanical_string(
    value: str, *, field: str, max_chars: int = MECHANICAL_STRING_MAX_CHARS
) -> str:
    """Return ``value`` if it is mechanical, else raise :class:`NonMechanicalValueError`."""
    reasons = mechanical_violations(value, max_chars=max_chars)
    if reasons:
        raise NonMechanicalValueError(f"{field}: not a mechanical value ({', '.join(reasons)})")
    return value


def assert_mechanical_value(
    value: MechanicalValue, *, field: str, max_chars: int = MECHANICAL_STRING_MAX_CHARS
) -> MechanicalValue:
    """Assert a scalar or a sequence of scalars is mechanical throughout."""
    if isinstance(value, str):
        assert_mechanical_string(value, field=field, max_chars=max_chars)
        return value
    if isinstance(value, bool | int):
        return value
    for index, item in enumerate(value):
        if isinstance(item, str):
            assert_mechanical_string(item, field=f"{field}[{index}]", max_chars=max_chars)
    return value
