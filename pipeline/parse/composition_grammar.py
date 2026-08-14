# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the composition grammar of
# 004 research D2 (004 task T027): the fixed-order pre-pass, exactly two productions, and the
# exactly-one-match model link — with no fuzzy matching, no spelled-numeral dictionary, and no
# "and"-splitting heuristic anywhere.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 007 US3 (T038): relocated the footnote-marker
# expression here from `options_grammar` (now public `FOOTNOTE_MARK`) so both grammars reuse the
# one expression without a circular import, and stripped it from `model_name` (research D4.1,
# guarantee 21).
"""Resolve one composition line into a model name and an integer count range.

**Two productions, and no more** (research D2)::

    entry := INT WS name                    -> min = max = INT
    entry := INT "-" INT WS name            -> min = INT1, max = INT2

They resolve 98.7% of the measured baseline after the pre-pass. The remaining 1.3% — leading
section labels ending in a colon, ``and``-joined multi-model lines, spelled-out numerals — is
**not** parsed heuristically. :func:`parse_entry` returns ``None``, the caller raises the
advisory ``CMP-UNRESOLVED``, the datasheet publishes without composition (FR-008), and a curator
resolves it once in ``curation/composition-overrides.json``. `002`'s D5 rule holds: *the pipeline
never acts on its own suggestion*. A 1.3% tail a human resolves once and that carries forward is
cheaper and safer than a heuristic that mis-prices a unit silently.

**The pre-pass order is load-bearing**, and the hyphen mapping is not cosmetic: 11 rows of the
measured baseline write their range with a non-breaking hyphen and would otherwise fall to the
residual for a reason no reader could see.

**A fixed count is not missing data.** ``min == max`` is the majority shape (1 669 of 2 168 rows)
and the first production produces it deliberately, not as a fallback.

This module is **mode-blind** (research D1d): it takes a description *string*, so the `csv`-mode
reader and the `html`-mode DOM segmenter (task T073) feed it the same way and it is proven once.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from pipeline.normalize.ip_strip import strip_field
from pipeline.normalize.names import normalize_name

#: Every dash form that appears in a range position, mapped to ASCII ``-``. ``U+2011`` is the
#: one research D2 measured; ``U+2010`` is included because NFKC *produces* it from ``U+2011``,
#: so omitting it would make the pre-pass's own second step undo its third.
_DASHES: Final[dict[int, str]] = {
    ord("‐"): "-",  # hyphen
    ord("‑"): "-",  # non-breaking hyphen — 11 rows of the measured baseline
    ord("–"): "-",  # en dash
    ord("—"): "-",  # em dash
    ord("−"): "-",  # minus sign
}

#: ``INT-INT WS name``. Tried first: ``5-10 Fenmire Skirmisher`` also satisfies the fixed
#: production's ``INT WS name`` if the fixed one is tried first, and would resolve to a unit of
#: five models called ``-10 Fenmire Skirmisher``.
_RANGE: Final = re.compile(r"^(\d+)\s*-\s*(\d+)\s+(\S.*)$")

#: ``INT WS name``.
_FIXED: Final = re.compile(r"^(\d+)\s+(\S.*)$")

#: The ceiling the curated schema puts on ``model_name``. A "name" longer than this has stopped
#: being a name, and emitting it would fail schema validation at write time instead of here,
#: where the row can still be reported as unresolved and handed to a curator.
MAX_MODEL_NAME_CHARS: Final = 120

#: A second count clause inside what would otherwise be the name — the ``and``-joined
#: multi-model line that research D2 counts in the residual.
#:
#: **This is a refusal, not a production.** Both productions match such a row perfectly well and
#: resolve it to the *first* count with the rest of the line swallowed into the name, which is a
#: five-model unit published as a one-model unit: an answer, and a wrong one. There is
#: deliberately no ``and``-splitting heuristic to go with the refusal — the row goes to
#: ``CMP-UNRESOLVED`` and a curator resolves it once in
#: ``curation/composition-overrides.json``.
_MULTI_MODEL: Final = re.compile(r"\band\s+\d")

#: A footnote marker glued to a name (007 research D4.1) — 24 measured option-row heads and 6
#: measured composition ``model_name`` rows carry one. **Public and defined here, not in
#: ``options_grammar``**, so both grammars reuse the same one expression rather than each keeping
#: their own copy: ``options_grammar`` already imports :func:`pre_pass` from this module, and a
#: second definition of the same pattern is exactly the drift research D4a's "reuse the
#: expression that already exists" decision exists to prevent. The name normaliser used for
#: *joins* (:func:`pipeline.normalize.names.normalize_name`) collapses non-alphanumeric runs, so
#: a marker is invisible to a link and fully visible in the stored display name until stripped
#: here at extraction (007 T038, guarantee 21).
FOOTNOTE_MARK: Final = re.compile(r"[*†‡¹²³]+")


@dataclass(frozen=True, slots=True)
class CompositionParse:
    """One resolved composition line. ``model_line`` is linked separately, never guessed."""

    model_name: str
    min_count: int
    max_count: int


def pre_pass(raw: str, *, field: str = "composition.description") -> str:
    """Normalise one description, in the fixed order of research D2.

    Strip markup, NFKC, map the dash forms, collapse whitespace. The markup strip runs through
    :func:`pipeline.normalize.ip_strip.strip_field` rather than a second regex of its own, so
    "what counts as markup" has exactly one definition in this repository. Its findings are
    dropped here on purpose: the call site in ``curate/assemble.py`` already strips the same
    field and keeps them, and raising ``DQ-MARKUP-IN-FIELD`` twice for one field would
    double-count one defect in the report's scale figures.

    ``field`` names the field for that dropped finding only. :mod:`pipeline.parse.options_grammar`
    shares this pre-pass rather than growing a second one, because two normalisers that disagree
    by a character are how ``5-10`` and ``5–10`` end up on different sides of a production.
    """
    text = strip_field(raw, field=field).text
    text = unicodedata.normalize("NFKC", text).translate(_DASHES)
    return " ".join(text.split())


def parse_entry(description: str) -> CompositionParse | None:
    """Resolve one composition line, or ``None`` when neither production matches.

    ``None`` is a *result*, not an error: it is the 1.3% tail, and the caller's job is to report
    it and publish the datasheet without composition rather than to try harder.
    """
    text = pre_pass(description)
    if not text:
        return None

    ranged = _RANGE.match(text)
    if ranged is not None:
        minimum, maximum = int(ranged.group(1)), int(ranged.group(2))
        name = _strip_marker(ranged.group(3).strip())
        # A range that runs backwards is a parse defect, not data. Reporting it as unresolved
        # hands it to a curator; emitting it would raise inside the curated model at write time,
        # where the failure is a stack trace rather than a finding.
        if maximum < minimum or not _is_name(name):
            return None
        return CompositionParse(model_name=name, min_count=minimum, max_count=maximum)

    fixed = _FIXED.match(text)
    if fixed is None:
        return None
    count = int(fixed.group(1))
    name = _strip_marker(fixed.group(2).strip())
    if not _is_name(name):
        return None
    return CompositionParse(model_name=name, min_count=count, max_count=count)


def _strip_marker(name: str) -> str:
    """Strip a footnote marker from a captured name (007 T038, guarantee 21).

    The marker is typography, never part of the name — the same ruling
    :func:`pipeline.parse.options_grammar._model_name` already makes for an eligibility
    subject's name, applied here to ``composition[].model_name``.
    """
    return FOOTNOTE_MARK.sub("", name).strip()


def _is_name(value: str) -> bool:
    return bool(value) and len(value) <= MAX_MODEL_NAME_CHARS and _MULTI_MODEL.search(value) is None


def link_model_line(model_name: str, model_lines: Mapping[int, str]) -> int | None:
    """The datasheet model row this entry names, or ``None`` when the match is not unique.

    74% of the measured baseline's descriptions contain a model row's name as a substring. Where
    **exactly one** does, the entry carries ``model_line``; where zero or two or more do, it is
    **omitted** — FR-011's "never guessed and never silently attached to the wrong profile",
    applied to composition.

    The comparison is over :func:`pipeline.normalize.names.normalize_name` forms, so casing,
    punctuation, and spacing variants of one name agree while two genuinely different names
    stay apart. Containment rather than equality, because a composition line legitimately reads
    ``3 Bracklight Outrider`` against a model row named ``Bracklight Outrider`` with the count
    already stripped — and because a row whose name is a prefix of another's therefore matches
    twice and is correctly refused.
    """
    haystack = normalize_name(model_name)
    if not haystack:
        return None
    matches = [
        line
        for line, name in sorted(model_lines.items())
        if (needle := normalize_name(name)) and needle in haystack
    ]
    return matches[0] if len(matches) == 1 else None
