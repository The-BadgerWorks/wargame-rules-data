# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the normative keyword-key
# procedure of 004 contracts/bundle-schema-delta.md §4 / data-model.md §2.4 (004 task T017):
# NFKC, casefold, punctuation to spaces, collapse whitespace, strip a trailing integer
# parameter, returning the key and whether a parameter was stripped (FR-023).
"""Normalise a keyword to its glossary key.

**This procedure is normative and shared with the consuming app.**
``contracts/bundle-schema-delta.md`` §4 owns it, in the same way ``reference-db-schema.md`` §3.4
owns the point-limit range. Producer and consumer must derive the key by the *same five steps*
or a glossary lookup silently fails to resolve — the keyword is displayed, the definition exists,
and nothing links them. That failure is invisible in every test either side writes alone, which
is exactly why the procedure is written down in a contract rather than agreed informally.

The five steps, in order::

    1. Unicode NFKC
    2. casefold
    3. every non-alphanumeric, non-space character becomes a space
    4. runs of whitespace collapse to one space; trim
    5. a trailing run of digits preceded by a space is removed, and
       has_numeric_parameter is set

Step 5 is what makes **one entry serve a keyword and every numeric variant of it** — the
difference between a glossary of 60-100 entries and one that grows a row for every parameter
value a publisher ever prints. No placeholder token is introduced: the parameter is *removed*,
not replaced with a sentinel, so the IP-boundary scan's unresolved-placeholder check needs no
allowlist for glossary keys.

**Two things this deliberately does not do**, both of which the sibling
:mod:`pipeline.normalize.names` ladder does:

* **No homoglyph folding**, though this repository owns
  :mod:`pipeline.normalize.homoglyphs` and the acquisition path genuinely encounters
  homoglyphs. Folding here would be a *sixth step*, and the consumer implements five. A key that
  resolves in the pipeline and not in the app is worse than a key that resolves in neither.
* **No leading-article strip, no combining-mark strip.** Same reason. Where those matter they
  belong in the contract, not in this module.

If either turns out to be needed, the contract moves first and both sides move together.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Final, NamedTuple

_WHITESPACE_RUN: Final = re.compile(r"\s+")

#: A trailing integer parameter: one or more digits, preceded by a space, at the very end.
_TRAILING_PARAMETER: Final = re.compile(r" (\d+)$")


class KeywordKey(NamedTuple):
    """The normalised key, and whether a numeric parameter was stripped to reach it."""

    key: str
    has_numeric_parameter: bool


def collapse_variant(value: str) -> str:
    """Steps 1-4 only: the printed form reduced to a comparable shape, **parameter intact**.

    Exists for the one caller that has to tell ``MARSHBIND 1`` from ``MARSHBIND 3`` while still
    treating ``Marshbind 2`` and ``MARSHBIND-2`` as the same printed value — deduplicating a
    weapon row's own keyword list (:mod:`pipeline.normalize.weapon_abilities`), where the key
    would merge two genuinely different parameters. Not a sixth normalisation: it is the first
    four steps of the one procedure below, shared rather than re-implemented.
    """
    composed = unicodedata.normalize("NFKC", value).casefold()
    kept = "".join(ch if (ch.isalnum() or ch.isspace()) else " " for ch in composed)
    return _WHITESPACE_RUN.sub(" ", kept).strip()


def normalize_keyword(value: str) -> KeywordKey:
    """Return ``value``'s glossary key and whether a numeric parameter was stripped.

    Idempotent on the key: normalising a key returns it unchanged. ``has_numeric_parameter``
    is **not** idempotent and is not meant to be — it records what happened to *this* input, so
    a keyword printed with a parameter and the same keyword printed without one produce the same
    key while remaining distinguishable at the point of use.

    Examples:
        ``SUSTAINED HITS 1`` and ``Sustained Hits 2`` both give ``("sustained hits", True)``.
        ``Lethal Hits``, ``LETHAL  HITS``, and ``lethal-hits`` all give ``("lethal hits", False)``.
    """
    if not value:
        return KeywordKey("", False)

    collapsed = collapse_variant(value)
    stripped = _TRAILING_PARAMETER.sub("", collapsed)
    return KeywordKey(stripped, stripped != collapsed)


def keyword_key(value: str) -> str:
    """Just the key, for callers that do not care whether a parameter was stripped."""
    return normalize_keyword(value).key
