# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the FR-007/rule-5 no-new-productions
# assertion (009 task T044): every grammar production table in `parse/options_grammar.py` and
# `parse/equipment_grammar.py` is pinned to the exact regex-pattern content it carried before this
# feature touched anything, stated as a diff rather than a count -- a swap of one production for
# an equal-sized replacement would still be caught, which a length-only assertion would miss.
"""Rule 5: no grammar production is authored by this feature, in either forbidden file.

`options_grammar.py` and `equipment_grammar.py` are the two files 009's own rules block names
explicitly (rule 5) and forbids editing: FR-007 requires the denominator and normalization causes
be eliminated or explicitly accepted before a production closes any remaining gap, and this
feature's own diagnosis (T036-T043) is exactly that accounting, never a production. This test is
the mechanical half of that promise -- the prose says no production was added; this proves it by
diffing every production table's own pattern strings against the set captured going into Phase 3,
before any US1 code was written.

Six tables carry FR-006/FR-007's productions, split across the two files research.md and `plan.md`
both describe as the pipeline's whole option/equipment vocabulary:

* `options_grammar.py`: ``_HEADS``, ``_EXTENDED_HEADS``, ``_COMPLETION_HEADS`` (the head
  productions), and ``_COMPLETION_VERBS`` (the verb productions).
* `equipment_grammar.py`: ``_SUBJECTS`` and ``_COMPLETION_SUBJECTS`` (the subject productions).

Two of the six (``_COMPLETION_HEADS``, ``_COMPLETION_SUBJECTS``) are empty today -- research D1c/
D2 left them as the extension points a later feature's productions would land in, and an empty
table growing by even one entry is exactly what this test exists to catch, not a special case it
carves out.
"""

from __future__ import annotations

from pipeline.parse import equipment_grammar as eg
from pipeline.parse import options_grammar as og

#: Pinned going into Phase 3 (009 task T044), before any US1 code was written. Each entry is the
#: raw ``.pattern`` string of a production's own regex -- the content that actually defines what
#: the production matches, not merely how many productions exist.
_BASELINE: dict[str, tuple[str, ...]] = {
    "options_grammar._HEADS": (
        r"^This model\b",
        r"^For every (\d+) models\b",
        r"^Any number of\b.*\bmodels\b",
        r"^\d+ ",
        r"^The\b",
    ),
    "options_grammar._EXTENDED_HEADS": (
        r"^Up to (\d+)\s+([A-Z][\w'’-]*(?:[ -][A-Z][\w'’-]*)*|models?)\b",
        r"^All models in this unit\b",
        r"^Any number of ([A-Z][\w'’-]*(?:[ -][A-Z][\w'’-]*)*)\b",
        r"^(?:Each|Both) of this model['’]s\b",
        r"^One model['’]s\b",
        r"^(?:One|An?) ([A-Z][\w'’-]*(?:[ -][A-Z][\w'’-]*)*)['’]s\b",
        r"^One model\b",
        r"^One ([A-Z][\w'’-]*(?:[ -][A-Z][\w'’-]*)*)\b",
        r"^This unit\b",
        r"^Each model['’]s\b",
        r"^Each ([A-Z][\w'’-]*(?:[ -][A-Z][\w'’-]*)*)\b",
        r"^For every (\d+) (?:[A-Z][\w'’-]*(?:[ -][A-Z][\w'’-]*)*)s? in this unit\b",
    ),
    "options_grammar._COMPLETION_HEADS": (),
    "options_grammar._COMPLETION_VERBS": (
        r"\bcan each be equipped with\b",
        r"\bcan replace\s+(?P<side>(?:its|their)\s+.+?)\s+with\b",
        r"\bcan have\s+(?P<side>.+?)\s+replaced with\b",
        r"\bcan each replace\s+(?P<side>(?:its|their)\s+.+?)\s+with\b",
        r"\bcan each be replaced with\b",
        r"\bcan(?:\s+each)?\s+have\b(?=\s+\d)",
    ),
    "equipment_grammar._SUBJECTS": (
        r"^This model$",
        r"^Every model$",
        r"^Every (\S.*)$",
        r"^The (\S.*)$",
        r"^Each (\S.*)$",
        r"^(\S.*)$",
    ),
    "equipment_grammar._COMPLETION_SUBJECTS": (),
}


def _patterns(table: object) -> tuple[str, ...]:
    return tuple(entry[0].pattern for entry in table)  # type: ignore[index]


def _current() -> dict[str, tuple[str, ...]]:
    return {
        "options_grammar._HEADS": _patterns(og._HEADS),
        "options_grammar._EXTENDED_HEADS": _patterns(og._EXTENDED_HEADS),
        "options_grammar._COMPLETION_HEADS": _patterns(og._COMPLETION_HEADS),
        "options_grammar._COMPLETION_VERBS": _patterns(og._COMPLETION_VERBS),
        "equipment_grammar._SUBJECTS": _patterns(eg._SUBJECTS),
        "equipment_grammar._COMPLETION_SUBJECTS": _patterns(eg._COMPLETION_SUBJECTS),
    }


def test_the_baseline_itself_covers_every_production_table_rule_5_names() -> None:
    """A table missing from `_BASELINE` would make every other assertion in this file vacuous."""
    assert set(_BASELINE) == {
        "options_grammar._HEADS",
        "options_grammar._EXTENDED_HEADS",
        "options_grammar._COMPLETION_HEADS",
        "options_grammar._COMPLETION_VERBS",
        "equipment_grammar._SUBJECTS",
        "equipment_grammar._COMPLETION_SUBJECTS",
    }


def test_no_grammar_production_table_grew_or_changed() -> None:
    """FR-007, rule 5: not one production was added, removed, or edited in either forbidden file.

    Asserted as a diff against the exact pattern strings, table by table, so the failure message
    names which table and which pattern moved rather than only reporting a count mismatch.
    """
    current = _current()
    assert current == _BASELINE


def test_the_two_completion_tables_are_still_the_unfilled_extension_point() -> None:
    """`_COMPLETION_HEADS` and `_COMPLETION_SUBJECTS` are empty by design (research D1c/D2's own
    extension points), not merely empty today -- a future feature fills them, this one never
    does."""
    assert og._COMPLETION_HEADS == ()
    assert eg._COMPLETION_SUBJECTS == ()
