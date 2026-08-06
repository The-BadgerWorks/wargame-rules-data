# AI-Assisted: Claude Code (model: claude-opus-5) - Shared mechanical-string guard backing the
# "no field typed to hold prose" invariant used by the finding detail (task T025) and the run
# ledger (task T031); the same quirk classes the IP scan (V8) asserts zero of.
# AI-Assisted: Claude Code (model: claude-opus-5) - Extended for 004-rules-data-enrichment (004
# task T011): assert_mechanical_fields() applies the guard across every string field of a whole
# record, which is how the feature's new models assert the invariant at the model boundary
# rather than relying on the scan that runs later. The scalar set stays float-free; see the note
# on MechanicalScalar for why the coverage ratchet reports integer percents instead.
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

from pydantic import BaseModel

#: The length above which a value has stopped being a name, label, or code. This governs
#: finding *detail* values, which stay terse; it is deliberately **not** the authored-summary
#: target (``WGC_SUMMARY_MAX_CHARS``, FR-022), which the Product Owner raised to 1 000 on
#: 2026-08-06 so a summary may carry a full multi-clause mechanic.
MECHANICAL_STRING_MAX_CHARS: Final = 240

#: reason -> pattern. Every one of these is a class observed in a real source (research §0.1).
NON_MECHANICAL_PATTERNS: Final[Mapping[str, re.Pattern[str]]] = {
    "markup": re.compile(r"</?[A-Za-z][A-Za-z0-9]*[\s/>]"),
    "html_entity": re.compile(r"&(?:[A-Za-z][A-Za-z0-9]{1,31}|#[0-9]{1,7}|#[Xx][0-9A-Fa-f]{1,6});"),
    "placeholder_token": re.compile(r"\$[A-Za-z_{]"),
    "cyrillic": re.compile(r"[Ѐ-ӿ]"),
}

#: What a mechanical field may hold: ids, names, numbers, enumerated codes, and lists of those.
#:
#: **No ``float``, deliberately.** `004`'s coverage ratchet
#: (``contracts/authored-summary-gates.md`` §4) describes ``COV-SUMMARY-REGRESSION``'s ``detail``
#: as carrying ``previous_ratio`` / ``current_ratio`` / ``tolerance``, and the obvious reading is
#: a proportion. It cannot be one: :data:`pipeline.build.canonical_json.JsonValue` excludes
#: ``float`` so that a bundle's bytes are reproducible (FR-039, SC-012), and a finding's detail
#: is canonically encoded like everything else. Every proportion already in the report is emitted
#: as an integer percent (``ratio_percent``, ``proportion_percent``), and the ratchet follows the
#: same convention. The requirement is satisfied; the representation is the one that stays
#: deterministic.
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


def assert_mechanical_fields(
    record: BaseModel,
    *,
    max_chars: Mapping[str, int] | None = None,
    default_max_chars: int = MECHANICAL_STRING_MAX_CHARS,
) -> None:
    """Assert every string this record declares is a mechanical value.

    The strongest control over the IP boundary is not the scan that runs at the end of a build —
    it is that **no field is typed to hold prose** (research D9 control 1). This function is how
    a record asserts that of itself, at construction, so an offending value never reaches the
    curated tree, a report, or a log in the first place. It is applied by every model
    `004-rules-data-enrichment` adds: composition is integers plus a model name, an option choice
    is a name plus integers plus an enumerated scope, keyword classes and states are enumerated
    codes, and the three authored ``summary`` fields are human-written under
    ``contracts/authored-summary-gates.md``.

    Args:
        record: the model to check. Nested models are skipped — each asserts itself.
        max_chars: per-field length ceilings, for the authored summary fields whose target is
            their class's own configured length rather than the name-length default.
        default_max_chars: the ceiling for every other string field.

    Raises:
        NonMechanicalValueError: naming the field and the violation *class* — never the
            offending text, since a diagnostic that quotes source text is itself a leak.
    """
    ceilings = max_chars or {}
    for name in type(record).model_fields:
        value = getattr(record, name, None)
        if value is None or isinstance(value, BaseModel):
            continue
        limit = ceilings.get(name, default_max_chars)
        label = f"{type(record).__name__}.{name}"
        if isinstance(value, str):
            assert_mechanical_string(value, field=label, max_chars=limit)
        elif isinstance(value, Sequence):
            for index, item in enumerate(value):
                if isinstance(item, str):
                    assert_mechanical_string(item, field=f"{label}[{index}]", max_chars=limit)
