# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the table-driven IP-strip tests (task
# T046): one case per quirk class in research §0.1, each asserting the output is mechanical only
# and that the discarded content appears in no return value.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added the variant matrix (009 task T029,
# plan.md finding 6): space-variant open/close tags, an unterminated tag, a self-closing space
# variant, and the "a <b and c> d" over-strip trap -- against T007's CM01 forms -- plus the
# paired source-level assertion that models/mechanical.py's markup pattern stays in lockstep.
"""Tests for the normalize stage's IP strip (FR-011, FR-012, FR-013, research D8).

Two assertions per case, and the second is the one that earns its keep:

1. the transform yields the mechanical value it is supposed to, and
2. **the discarded content appears nowhere in the return value** — not in the text, not in a
   finding's detail, not in a diagnostic. A stripper that reports what it stripped has not
   stripped it, it has moved it, and FR-013 covers reports and logs as well as data.
"""

from __future__ import annotations

import pytest

from pipeline.models.mechanical import NON_MECHANICAL_PATTERNS
from pipeline.normalize.ip_strip import _HAS_MARKUP, StripResult, strip_field


def _codes(result: StripResult) -> list[str]:
    return [finding.finding_code for finding in result.findings]


def _all_strings(result: StripResult) -> str:
    parts = [result.text, *_codes(result)]
    for finding in result.findings:
        parts.extend(str(v) for v in finding.detail.values())
        parts.extend(finding.entity_refs)
    return " ".join(parts)


@pytest.mark.parametrize(
    ("raw", "expected", "expected_codes", "must_not_survive"),
    [
        pytest.param(
            '<span class="kwb">5 Cinder Wardens</span>',
            "5 Cinder Wardens",
            ["DQ-MARKUP-IN-FIELD"],
            ["span", "kwb", "class"],
            id="markup",
        ),
        pytest.param(
            "marshal&#8217;s hammer",
            "marshal’s hammer",
            [],
            ["&#8217;"],
            id="numeric-entity",
        ),
        pytest.param(
            "a &amp; b &#8212; c&nbsp;d",
            "a & b — c d",
            [],
            ["&amp;", "&nbsp;", "&#8212;"],
            id="named-entities",
        ),
        pytest.param(
            "<table><tr><td>Distance</td><td>Effect</td></tr></table>Invented tail.",
            "Invented tail.",
            ["DQ-MARKUP-IN-FIELD"],
            ["Distance", "Effect", "table"],
            id="table-content-is-dropped-not-flattened",
        ),
        pytest.param(
            '<img src="https://example.invalid/icon.png"/>Invented tail.',
            "Invented tail.",
            ["DQ-MARKUP-IN-FIELD"],
            ["example.invalid", "icon.png", "img"],
            id="image-reference-is-dropped",
        ),
        pytest.param(
            "Invented placeholder prose adding $BONUS$ to a characteristic.",
            "Invented placeholder prose adding $BONUS$ to a characteristic.",
            ["DQ-PLACEHOLDER-TOKEN"],
            [],
            id="unresolved-token-is-reported",
        ),
        pytest.param(
            "  spaced   out\n\ttext  ",
            "spaced out text",
            [],
            [],
            id="whitespace-is-collapsed",
        ),
        pytest.param("", "", [], [], id="empty"),
    ],
)
def test_quirk_class(
    raw: str, expected: str, expected_codes: list[str], must_not_survive: list[str]
) -> None:
    result = strip_field(raw, field="description")

    assert result.text == expected
    assert _codes(result) == expected_codes

    surface = _all_strings(result)
    for fragment in must_not_survive:
        assert fragment not in surface, f"{fragment!r} survived the strip"


def test_table_and_image_together_report_one_markup_finding_not_three() -> None:
    result = strip_field("<table><tr><td>x</td></tr></table><img src='a.png'/><b>y</b>", field="d")
    assert _codes(result) == ["DQ-MARKUP-IN-FIELD"]


def test_a_cyrillic_classification_artefact_is_not_the_strippers_business() -> None:
    """The artefact class lives in a *classification* field, and ability_types.py owns it.

    The stripper must not quietly launder it into something that looks legitimate — it passes
    the value through unchanged so the mapping table is the single place that decides.
    """
    raw = "Special (правая колонка)"
    assert strip_field(raw, field="type").text == raw


def test_free_text_composition_is_stripped_before_it_is_parsed() -> None:
    """Strip-then-parse, never parse-then-strip: markup reaches unit_composition too (§0.1)."""
    result = strip_field('<span class="kwb">5 Cinder Wardens</span>', field="description")
    assert result.text == "5 Cinder Wardens"


# -- 009 T029: the variant matrix, against T007's CM01 forms (plan.md finding 6) ----------------
#
# `test_quirk_class` above exercises only well-formed, closed, flush tags (`<span class="kwb">`).
# These five mirror `fixtures/enrichment/wahapedia/Datasheets_options.csv`'s `CM01` rows
# verbatim: a space-variant open tag, a space-variant close tag, an unterminated tag, a
# self-closing space variant, and the "looks like a tag but is prose" over-strip trap.


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param(
            "This model can be equipped with 1 marsh lantern< b>ornate</b> and a tide hammer.",
            "This model can be equipped with 1 marsh lantern ornate and a tide hammer.",
            id="space-variant-open-tag",
        ),
        pytest.param(
            "This model can be equipped with 1 marsh lantern<b>ornate</ b> and a tide hammer.",
            "This model can be equipped with 1 marsh lantern ornate and a tide hammer.",
            id="space-variant-close-tag",
        ),
        pytest.param(
            "This model can be equipped with 1 marsh lantern< br/>and a tide hammer.",
            "This model can be equipped with 1 marsh lantern and a tide hammer.",
            id="self-closing-space-variant",
        ),
    ],
)
def test_space_variant_tag_forms_are_stripped_and_reported(raw: str, expected: str) -> None:
    result = strip_field(raw, field="description")

    assert result.text == expected
    assert _codes(result) == ["DQ-MARKUP-IN-FIELD"]
    assert "<" not in result.text
    assert ">" not in result.text


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param("<b x", id="unterminated-minimal"),
        pytest.param('<img src="a"', id="unterminated-with-attribute"),
        pytest.param(
            "This model can be equipped with 1 marsh lantern<b unclosed and a tide hammer.",
            id="unterminated-mid-sentence",
        ),
    ],
)
def test_an_unterminated_tag_is_removed_not_merely_reported(raw: str) -> None:
    result = strip_field(raw, field="description")

    assert "<" not in result.text
    assert _codes(result) == ["DQ-MARKUP-IN-FIELD"]


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param("</ b>trailing text", id="close-with-leading-space"),
        pytest.param("< /b>trailing text", id="close-with-space-before-slash"),
    ],
)
def test_close_tag_space_variants_are_recognised(raw: str) -> None:
    result = strip_field(raw, field="description")

    assert "<" not in result.text
    assert ">" not in result.text
    assert _codes(result) == ["DQ-MARKUP-IN-FIELD"]


def test_the_over_strip_trap_does_not_lose_ordinary_words_in_brackets() -> None:
    """`a <b and c> d` LOOKS like a tag (`<` + letter + ... + `>`) but is not one: `and`/`c` are
    bare words with no `=`, which is what a genuine attribute in this export always has. Losing
    "b and c" here was the old, looser pattern's actual defect (`plan.md` finding 6) — verified
    empirically against the pre-T030 pattern before this fix landed."""
    raw = "a <b and c> d"

    result = strip_field(raw, field="description")

    assert result.text == raw
    assert _codes(result) == []


def test_the_mechanical_markup_pattern_stays_in_lockstep_with_the_stripper() -> None:
    """`models/mechanical.py`'s `NON_MECHANICAL_PATTERNS["markup"]` must catch every form
    `_HAS_MARKUP` catches -- character-for-character identical today (009 task T030), asserted
    as a source-level equality rather than trusted as a comment, so a future edit to either
    cannot silently open a blind spot in the other."""
    assert NON_MECHANICAL_PATTERNS["markup"].pattern == _HAS_MARKUP.pattern


# `mechanic_digest` and `hard_normalise` moved to `pipeline.normalize.mechanic_digest` (T127);
# their tests moved with them to `tests/summaries/test_mechanic_digest.py` (T123).


# -- 009 R01a: the no-regression matrix (the direction T029/T030 never proved) -------------------
#
# The matrices above prove the OLD holes are closed. They prove nothing about holes the tightening
# might have OPENED, which is exactly how two regressions shipped through a green suite and a
# green CI. This matrix pins the other direction as a fixed contract.
#
# Every `main_text` / `main_codes` literal below was captured first-hand by running
# `strip_field(raw, field="description")` against `origin/main` at commit `2c603c7f` -- the
# revision `009-csv-migration` branched from. They are hard-coded, never recomputed: nothing here
# imports, checks out, or shells out to `main` at test time, so this is a frozen contract rather
# than a comparison that moves whenever `main` does.
#
# Inputs are synthetic throughout (standing rule 1): invented placeholder prose, invented weapon
# names, `example.invalid` hosts.


@pytest.mark.parametrize(
    ("raw", "main_text", "main_codes"),
    [
        pytest.param(
            '<span class="kwb">5 Cinder Wardens</span>',
            "5 Cinder Wardens",
            ["DQ-MARKUP-IN-FIELD"],
            id="quoted-attribute",
        ),
        pytest.param(
            "<td colspan=2>Bolt rifle</td>",
            "Bolt rifle",
            ["DQ-MARKUP-IN-FIELD"],
            id="unquoted-attribute-value",
        ),
        pytest.param(
            "<a href=#note>Bolt rifle</a>",
            "Bolt rifle",
            ["DQ-MARKUP-IN-FIELD"],
            id="unquoted-attribute-value-punctuation",
        ),
        pytest.param(
            "<img src=x.png>",
            "",
            ["DQ-MARKUP-IN-FIELD"],
            id="unquoted-attribute-self-closing-subtree",
        ),
        pytest.param(
            '<img src="https://example.invalid/icon.png"/>Invented tail.',
            "Invented tail.",
            ["DQ-MARKUP-IN-FIELD"],
            id="quoted-attribute-self-closing-subtree",
        ),
        pytest.param(
            "Roll 2D6; if the result is < the target, nothing happens",
            "Roll 2D6; if the result is < the target, nothing happens",
            [],
            id="prose-less-than-before-a-word",
        ),
        pytest.param(
            "Roll 2D6; if the result is < the target and < 4, nothing happens",
            "Roll 2D6; if the result is < the target and < 4, nothing happens",
            [],
            id="prose-less-than-twice",
        ),
        pytest.param("2 < 3", "2 < 3", [], id="numeric-less-than-spaced"),
        pytest.param("2<3", "2<3", [], id="numeric-less-than-flush"),
        pytest.param("a<b", "a<b", [], id="prose-less-than-flush-at-end"),
    ],
)
def test_no_regression_against_main(raw: str, main_text: str, main_codes: list[str]) -> None:
    """Whatever `origin/main` stripped is still stripped; whatever it left alone is still left
    alone. Anything `main` did not report is still not reported, and anything it did report still
    is. A row here failing means the tightening opened a hole `main` did not have."""
    result = strip_field(raw, field="description")

    assert result.text == main_text
    assert _codes(result) == main_codes


@pytest.mark.parametrize(
    ("raw", "main_text", "main_codes", "text", "codes"),
    [
        pytest.param(
            "a <b and c> d",
            "a d",
            ["DQ-MARKUP-IN-FIELD"],
            "a <b and c> d",
            [],
            id="over-strip-trap-is-no-longer-eaten",
        ),
        pytest.param(
            "This model can be equipped with 1 marsh lantern< br/>and a tide hammer.",
            "This model can be equipped with 1 marsh lantern< br/>and a tide hammer.",
            [],
            "This model can be equipped with 1 marsh lantern and a tide hammer.",
            ["DQ-MARKUP-IN-FIELD"],
            id="self-closing-space-variant-is-now-caught",
        ),
        pytest.param(
            "This model can be equipped with 1 marsh lantern< b>ornate</b> and a tide hammer.",
            "This model can be equipped with 1 marsh lantern< b>ornate and a tide hammer.",
            ["DQ-MARKUP-IN-FIELD"],
            "This model can be equipped with 1 marsh lantern ornate and a tide hammer.",
            ["DQ-MARKUP-IN-FIELD"],
            id="space-variant-open-tag-is-now-fully-removed",
        ),
        pytest.param(
            "This model can be equipped with 1 marsh lantern<b>ornate</ b> and a tide hammer.",
            "This model can be equipped with 1 marsh lantern ornate</ b> and a tide hammer.",
            ["DQ-MARKUP-IN-FIELD"],
            "This model can be equipped with 1 marsh lantern ornate and a tide hammer.",
            ["DQ-MARKUP-IN-FIELD"],
            id="space-variant-close-tag-is-now-fully-removed",
        ),
        pytest.param(
            "</ b>trailing text",
            "</ b>trailing text",
            [],
            "trailing text",
            ["DQ-MARKUP-IN-FIELD"],
            id="space-variant-close-tag-alone-is-now-caught",
        ),
        pytest.param(
            "<b x",
            "<b x",
            ["DQ-MARKUP-IN-FIELD"],
            "",
            ["DQ-MARKUP-IN-FIELD"],
            id="unterminated-tag-is-now-removed-not-merely-reported",
        ),
        pytest.param(
            '<img src="a"',
            '<img src="a"',
            ["DQ-MARKUP-IN-FIELD"],
            "",
            ["DQ-MARKUP-IN-FIELD"],
            id="unterminated-tag-with-attribute-is-now-removed",
        ),
        pytest.param(
            "a<b c",
            "a<b c",
            ["DQ-MARKUP-IN-FIELD"],
            "a",
            ["DQ-MARKUP-IN-FIELD"],
            id="unterminated-tag-main-reported-but-left-in-place",
        ),
    ],
)
def test_the_deliberate_divergences_from_main_are_the_ones_009_intended(
    raw: str, main_text: str, main_codes: list[str], text: str, codes: list[str]
) -> None:
    """The rows where 009 deliberately changed `main`'s behaviour, each pinned on both sides.

    A divergence is only legitimate if it is one of these, and each is asserted to be a real
    divergence -- if a future edit made the new behaviour identical to `main` again, the
    inequality fires rather than the row quietly becoming a tautology.
    """
    result = strip_field(raw, field="description")

    assert (result.text, _codes(result)) != (main_text, main_codes), (
        "this row claims to diverge from origin/main@2c603c7f but no longer does"
    )
    assert result.text == text
    assert _codes(result) == codes


@pytest.mark.xfail(
    strict=True,
    reason="KNOWN RESIDUAL NARROWING against origin/main@2c603c7f: a tag carrying a VALUELESS "
    "(boolean) attribute is not recognised, so it survives in the field and -- because "
    "models/mechanical.py is character-identical -- validate/ip_scan.py will not catch it "
    "either. Deliberately not closed here: the only thing separating `<span hidden>` from the "
    "prose `a <b and c> d` this fix exists to protect is that the latter happens to carry two "
    "bare words rather than one, and fitting a rule to that re-opens the over-strip. See "
    "docs/follow-ups.md.",
)
@pytest.mark.parametrize(
    ("raw", "main_text"),
    [
        pytest.param("<span hidden>Bolt rifle</span>", "Bolt rifle", id="valueless-attribute"),
        pytest.param(
            '<td colspan="2" nowrap>Bolt rifle</td>',
            "Bolt rifle",
            id="valueless-attribute-beside-a-valued-one",
        ),
    ],
)
def test_a_valueless_attribute_is_a_known_open_narrowing_against_main(
    raw: str, main_text: str
) -> None:
    """`main` stripped these; 009 does not. Marked `xfail(strict=True)` deliberately: the day the
    residual is closed this test goes green, which fails the strict xfail and forces whoever
    closed it to promote the row into `test_no_regression_against_main` above."""
    result = strip_field(raw, field="description")

    assert result.text == main_text
    assert _codes(result) == ["DQ-MARKUP-IN-FIELD"]
