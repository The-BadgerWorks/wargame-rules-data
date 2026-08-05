# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the normative keyword-key procedure
# of 004 contracts/bundle-schema-delta.md §4 (004 task T017): casing, spacing, and punctuation
# variants collapse to one key, and SUSTAINED HITS 1 / SUSTAINED HITS 2 collapse to the same key
# with has_numeric_parameter = true (FR-023, spec Edge Cases).
"""One entry per keyword, however the publisher spelled it that day.

This is a **shared** procedure, not an internal one: the consuming app derives the same key from
the same five steps, and if the two ever disagree the failure is silent — the keyword renders,
the definition exists, and nothing joins them. So these tests are written against the contract's
wording rather than against the implementation's behaviour, and every keyword in them is
invented.
"""

from __future__ import annotations

import pytest

from pipeline.normalize.keyword_key import KeywordKey, keyword_key, normalize_keyword


@pytest.mark.parametrize(
    "spelling",
    [
        "GLIMMERSTRIKE",
        "Glimmerstrike",
        "glimmerstrike",
        "  Glimmerstrike  ",
        "GLIMMER-STRIKE",
        "Glimmer strike",
        "Glimmer  Strike",
        "Glimmer_Strike",
        "Glimmer/Strike",
        "(Glimmerstrike)",
    ],
)
def test_casing_spacing_and_punctuation_variants_collapse_to_one_key(spelling: str) -> None:
    # Whatever the publisher's typography did this printing, the curator authors ONE entry.
    assert keyword_key(spelling) in {"glimmerstrike", "glimmer strike"}


def test_the_hyphen_and_the_space_spelling_are_the_same_key() -> None:
    assert keyword_key("Glimmer-Strike") == keyword_key("glimmer strike") == "glimmer strike"


def test_a_numeric_parameter_is_stripped_and_recorded() -> None:
    one = normalize_keyword("SUSTAINED HITS 1")
    two = normalize_keyword("Sustained Hits 2")
    ten = normalize_keyword("sustained hits 10")

    assert one.key == two.key == ten.key == "sustained hits"
    assert one.has_numeric_parameter
    assert two.has_numeric_parameter
    assert ten.has_numeric_parameter


def test_the_parameterless_spelling_shares_the_key_without_the_flag() -> None:
    # The same entry serves both; only the flag records that this particular input carried a
    # parameter. That is the whole point: one definition, every numeric variant.
    bare = normalize_keyword("Sustained Hits")
    assert bare.key == normalize_keyword("SUSTAINED HITS 3").key
    assert not bare.has_numeric_parameter


@pytest.mark.parametrize(
    "value",
    [
        "Warpfire 2000",
        "Emberlance 1",
    ],
)
def test_only_a_trailing_digit_run_counts_as_a_parameter(value: str) -> None:
    assert normalize_keyword(value).has_numeric_parameter


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # A digit inside the name is part of the name, not a parameter.
        ("Mark 3 Emberplate", KeywordKey("mark 3 emberplate", False)),
        # A bare number has no preceding space, so nothing is stripped.
        ("7", KeywordKey("7", False)),
        # Trailing punctuation becomes a space (step 3) and is trimmed (step 4) BEFORE the
        # parameter rule runs (step 5), so a trailing "1." is still a parameter. The step order
        # is the contract's and this test exists to pin it: reordering 4 and 5 would silently
        # give this spelling its own glossary entry.
        ("Emberlance 1.", KeywordKey("emberlance", True)),
        ("", KeywordKey("", False)),
        ("   ", KeywordKey("", False)),
    ],
)
def test_the_parameter_rule_does_not_over_reach(value: str, expected: KeywordKey) -> None:
    assert normalize_keyword(value) == expected


def test_compatibility_forms_and_full_width_characters_converge() -> None:
    # NFKC is step 1 precisely so a full-width or compatibility spelling is not a second entry.
    assert keyword_key("ＧＬＩＭＭＥＲ") == "glimmer"
    assert keyword_key("ﬁrestrike") == "firestrike"


def test_an_accented_letter_survives_rather_than_being_stripped() -> None:
    # Step 3 removes non-alphanumerics; an accented letter IS alphanumeric. Stripping it would
    # fold two genuinely different keywords together, which is the failure mode that matters
    # here — a wrong join, not a missed one.
    assert keyword_key("Éclat") == "éclat"


def test_the_key_is_idempotent() -> None:
    once = keyword_key("SUSTAINED HITS 1")
    assert keyword_key(once) == once


def test_the_flag_is_deliberately_not_idempotent() -> None:
    """Re-normalising a key reports no parameter, because the key has none left.

    Stated as a test because it looks like a bug the first time someone sees it. The flag
    describes *what happened to this input*, not a property of the key, and the caller that
    needs it (the glossary's ``has_numeric_parameter``) always has the original spelling.
    """
    first = normalize_keyword("SUSTAINED HITS 1")
    assert first.has_numeric_parameter
    assert not normalize_keyword(first.key).has_numeric_parameter


def test_no_placeholder_token_is_introduced() -> None:
    # data-model.md §2.4: the parameter is REMOVED, not replaced with a sentinel, so the IP
    # scan's unresolved-placeholder check needs no allowlist for glossary keys.
    key = keyword_key("SUSTAINED HITS 1")
    assert "$" not in key
    assert "{" not in key
    assert "n" not in key.split()[-1] or key == "sustained hits"
