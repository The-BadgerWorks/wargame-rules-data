# AI-Assisted: Claude Code (model: claude-opus-5) - Tests for the D5 normalisation ladder (task
# T061): the observed real cases, and the guarantee that no stemming, singularisation, or
# synonym expansion happens.
"""Tests for name normalisation (research D5 stage 2).

Half these tests assert that two spellings converge. The other half assert that two *different*
names do **not**, which is the half that earns its keep: a normaliser that folds too hard turns
a missed match — a finding a human resolves once — into a wrong match, which is a silently
mispriced unit.
"""

from __future__ import annotations

import pytest

from pipeline.normalize.names import normalize_name


@pytest.mark.parametrize(
    ("left", "right"),
    [
        pytest.param("T’au Empire", "T'au Empire", id="typographic-apostrophe"),
        pytest.param("Emperor’s Children", "Emperor's Children", id="possessive"),
        pytest.param("ASSAULT INTERCESSOR SQUAD", "Assault Intercessor Squad", id="case"),
        pytest.param("Land  Raider\tCrusader", "Land Raider Crusader", id="whitespace"),
        pytest.param("Adeptus Custodes", "The Adeptus Custodes", id="leading-article"),
        pytest.param("Astra Militarum", "Astra-Militarum", id="hyphen"),
        pytest.param("Écorché Guard", "Ecorche Guard", id="combining-marks"),
        pytest.param("Ｎｅｃｒｏｎｓ", "Necrons", id="full-width"),
    ],
)
def test_two_spellings_of_one_name_converge(left: str, right: str) -> None:
    assert normalize_name(left) == normalize_name(right)


@pytest.mark.parametrize(
    ("left", "right"),
    [
        pytest.param("Land Raider Crusader", "Land Raider Redeemer", id="different-variant"),
        pytest.param("Intercessor Squad", "Intercessors", id="no-singularisation"),
        pytest.param("Heavy Intercessor Squad", "Intercessor Squad", id="no-substring-match"),
        pytest.param("Terminator Squad", "Terminators", id="no-stemming"),
        pytest.param("Wraithlord", "Wraithguard", id="no-synonym-expansion"),
    ],
)
def test_different_names_stay_different(left: str, right: str) -> None:
    assert normalize_name(left) != normalize_name(right)


def test_an_apostrophe_separates_rather_than_disappears() -> None:
    """`Emperor’s` normalises to `emperor s`, so it does **not** meet a written `Emperors`.

    That is the ladder as D5 specifies it, and it is the conservative direction: the two spellings
    stay a reported non-match a curator confirms once into `unit-aliases.json`, rather than an
    automatic match nobody reviewed. Recorded as a test so the behaviour is a decision rather
    than an accident of the regex.
    """
    assert normalize_name("Emperor’s Children") == "emperor s children"
    assert normalize_name("Emperors Children") == "emperors children"


def test_the_result_is_lower_case_alphanumerics_and_single_spaces() -> None:
    assert normalize_name("  T’au  Empire — Kroot!  ") == "t au empire kroot"


def test_normalisation_is_idempotent() -> None:
    once = normalize_name("Emperor’s Children")
    assert normalize_name(once) == once


def test_an_empty_name_normalises_to_empty_rather_than_raising() -> None:
    assert normalize_name("") == ""
    assert normalize_name("   ") == ""


def test_a_leading_article_is_dropped_but_an_internal_one_is_not() -> None:
    assert normalize_name("The Lion") == "lion"
    assert normalize_name("Sons of the Lion") == "sons of the lion"


def test_digits_survive_because_names_carry_them() -> None:
    assert normalize_name("1st Company Task Force") == "1st company task force"
