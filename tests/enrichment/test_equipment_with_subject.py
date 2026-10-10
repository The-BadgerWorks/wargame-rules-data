# AI-Assisted: Claude Code (model: claude-sonnet-5) - 2026-10-09 pipeline P3 task 2 (Owner ruling
# 5): the variant subject `<base model name> with <phrase>`'s own contract -- the grammar accepts
# exactly one `with` and refuses two, and the caller (`assemble._equipment`) publishes the group
# only when the whole subject names exactly one composition line by exact normalised name, never
# by containment and never positionally.
"""`<base model name> with <phrase>` subjects: accepted by the grammar, scoped by the caller.

Task 1 measured this class (B) at 1 sentence on the live export -- non-zero, so this task runs.
The grammar (`equipment_grammar.parse_variant_sentence`) is string-only and never sees
composition; it is the caller's job to require that the whole subject names exactly one
composition line of the same datasheet, else the sentence stays `EQP-UNPARSED` with
`detail["reason"] = "variant-no-exact-line"`.

D (how often a variant subject's own BASE name collides with the base subject's composition line
under the existing containment join) was measured at 0, so Step 3b
(`link_model_line_exact_first`) was never built -- `test_the_base_subject_still_resolves_beside_
its_variant` documents what `link_model_line`'s containment join already does today, unchanged.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from pipeline.curate.assemble import _equipment
from pipeline.curate.authored import AuthoredContent
from pipeline.models.curated import (
    CuratedCompositionEntry,
    CuratedEquipmentGroup,
    CuratedWeaponLine,
)
from pipeline.models.findings import Finding
from pipeline.parse.equipment_grammar import (
    EQUIPMENT_TABLE,
    parse_sentence,
    parse_variant_sentence,
)
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text
from tests.enrichment.conftest import weapon

#: Every item name the sentences below state, each naming its own weapon row so the item-to-weapon
#: join (a different concern from this task's subject-to-composition-line one) never leaves an
#: `EQP-ITEM-UNLINKED` advisory sitting in a `findings == ()` assertion.
WEAPONS: tuple[CuratedWeaponLine, ...] = (
    weapon(1, "test shield"),
    weapon(2, "test blade"),
    weapon(3, "test maul"),
)

#: Three composition lines on one datasheet: an unrelated model, the variant's own base name, and
#: the variant line itself -- letter-identical to the subject a sentence states, per the brief's
#: synthetic-data rule.
LINES = (
    CuratedCompositionEntry(line=1, model_name="Test Sergeant", min_count=1, max_count=1),
    CuratedCompositionEntry(line=2, model_name="Test Trooper", min_count=4, max_count=4),
    CuratedCompositionEntry(
        line=3, model_name="Test Trooper with test shield", min_count=2, max_count=2
    ),
)


def _equipment_for_test(
    sentences: Sequence[str],
    composition: Sequence[CuratedCompositionEntry],
    weapons: Sequence[CuratedWeaponLine] = WEAPONS,
) -> tuple[tuple[CuratedEquipmentGroup, ...], tuple[Finding, ...]]:
    """A thin wrapper around `_equipment`, building its CSV detail inline (copying the call shape
    `tests/enrichment/test_equipment_grammar.py`'s own `_detail`/`_equipment` calls use)."""
    rows = "".join(f"GF11|{line}|{sentence}|\n" for line, sentence in enumerate(sentences, start=1))
    detail: Mapping[str, CsvReadResult] = {
        EQUIPMENT_TABLE: read_text(EQUIPMENT_TABLE, f"datasheet_id|line|description|\n{rows}")
    }
    outcome = _equipment("GF11", "ds-gf11", detail, AuthoredContent(), composition, weapons)
    return outcome.groups, tuple(outcome.findings)


# --- the grammar: one `with` accepted, two refused, base grammar unchanged ----------------------


def test_the_variant_grammar_accepts_one_with_and_refuses_two() -> None:
    ok = parse_variant_sentence(
        "Every Test Trooper with test shield is equipped with: test shield; test blade."
    )
    assert ok is not None
    assert (ok.model_name, [item.item_name for item in ok.items]) == (
        "Test Trooper with test shield",
        ["test shield", "test blade"],
    )

    nested = parse_variant_sentence(
        "Every Test Trooper with test shield with test lantern is equipped with: test blade."
    )
    assert nested is None

    # The base grammar is untouched: the same sentence that resolves through the variant entry
    # point still matches `_REFUSED`'s bare `with` rule and is refused by `parse_sentence`.
    assert (
        parse_sentence("Every Test Trooper with test shield is equipped with: test shield.") is None
    )


# --- the caller: exact-line scoping, never containment, never positional -----------------------


def test_a_variant_subject_naming_an_exact_line_resolves_to_it() -> None:
    """Red before: EQP-UNPARSED and no group (the grammar refused the sentence outright)."""
    groups, findings = _equipment_for_test(
        sentences=[
            "Every Test Trooper with test shield is equipped with: test shield; test blade."
        ],
        composition=LINES,
    )
    (group,) = groups
    assert (group.model_name, group.composition_line) == ("Test Trooper with test shield", 3)
    assert findings == ()


def test_a_variant_subject_naming_no_exact_line_stays_unparsed() -> None:
    groups, findings = _equipment_for_test(
        sentences=["Every Test Trooper with test lantern is equipped with: test lantern."],
        composition=LINES,
    )
    assert groups == ()
    (finding,) = findings
    assert (finding.finding_code, finding.detail["reason"]) == (
        "EQP-UNPARSED",
        "variant-no-exact-line",
    )


def test_the_base_subject_still_resolves_beside_its_variant() -> None:
    """Documents today's behaviour for the base subject beside its variant line (D measured 0, so
    Step 3b -- `link_model_line_exact_first` -- was never built).

    `link_model_line`'s containment join compares the GROUP's subject name as the haystack
    against each composition line's name as the needle (`needle in haystack`). "Test Trooper"
    (the base subject) is the haystack; "Test Trooper with test shield" (line 3's name) is
    LONGER than it and can never be a substring of it, so only line 2's own name ("Test Trooper")
    matches, and the base subject resolves cleanly to its own line even with the variant line
    sitting right beside it. This is the existing containment join doing what it always did --
    nothing in this task changes it.
    """
    groups, findings = _equipment_for_test(
        sentences=[
            "Every Test Trooper is equipped with: test maul.",
            "Every Test Trooper with test shield is equipped with: test shield; test blade.",
        ],
        composition=LINES,
    )
    by_line = {group.line: group for group in groups}
    assert by_line[1].composition_line == 2
    assert by_line[2].composition_line == 3
    assert findings == ()
