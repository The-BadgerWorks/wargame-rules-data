# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the table-driven IP-strip tests (task
# T046): one case per quirk class in research §0.1, each asserting the output is mechanical only
# and that the discarded content appears in no return value.
"""Tests for the normalize stage's IP strip (FR-011, FR-012, FR-013, research D8).

Two assertions per case, and the second is the one that earns its keep:

1. the transform yields the mechanical value it is supposed to, and
2. **the discarded content appears nowhere in the return value** — not in the text, not in a
   finding's detail, not in a diagnostic. A stripper that reports what it stripped has not
   stripped it, it has moved it, and FR-013 covers reports and logs as well as data.
"""

from __future__ import annotations

import pytest

from pipeline.normalize.ip_strip import StripResult, strip_field


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


def test_mechanic_digest_is_keyed_and_does_not_reveal_its_input() -> None:
    from pipeline.normalize.ip_strip import mechanic_digest

    text = "Invented placeholder prose describing one mechanic."
    digest = mechanic_digest(text, key=b"repository-key")

    assert digest == mechanic_digest(text, key=b"repository-key")
    assert digest != mechanic_digest(text, key=b"another-key")
    assert len(digest) == 32  # 128 bits, hex
    assert "Invented" not in digest


def test_mechanic_digest_ignores_presentation_but_not_mechanics() -> None:
    from pipeline.normalize.ip_strip import mechanic_digest

    key = b"k"
    assert mechanic_digest("<b>Add 1 to the roll.</b>", key=key) == mechanic_digest(
        "Add  1  to the roll", key=key
    )
    assert mechanic_digest("Add 1 to the roll.", key=key) != mechanic_digest(
        "Add 2 to the roll.", key=key
    )
