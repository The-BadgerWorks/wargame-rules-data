# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the FR-007 production-ordering test
# (008 task T015, Foundational phase): every FIXTURE_GOLDEN/INLINE_GOLDEN row that resolves today
# must resolve without the resolution ever reaching `_COMPLETION_HEADS`/`_COMPLETION_VERBS`,
# proven by monkeypatching both tables to entries that raise if invoked rather than by inspecting
# which branch fired. Confirmed failing before T016 lands the (empty) tables into
# `_match_head`/`_match_verb` -- `options_grammar` carries neither symbol yet, so
# `monkeypatch.setattr` itself raises `AttributeError` on every test in this file.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 008 US1 (T029): pinned `_COMPLETION_VERBS`'
# three new entries by builder name and position, so a later refactor that reorders the tuple
# fails here rather than surfacing only as a moved coverage figure.
"""FR-007's ordering guarantee, proven structurally rather than left to review.

`plan.md`'s *Architecture* section states the control-flow guarantee in full: a row any prior
release (`004`, `006`) resolved must exit `parse_row` before a line of this feature's code runs.
Research D5 (`006`) proved the equivalent claim for its own two tables with a frozen golden
(`test_options_grammar_regression.py`, layer 1) plus this ordering test's `006` sibling. This file
is `008`'s version of the second half: the golden alone only proves the *value* did not change; it
says nothing about *which table produced it*, and a production subtly mis-ordered ahead of an
existing one could in principle still reproduce the same value by coincidence on today's fixture
set. Monkeypatching `_COMPLETION_HEADS`/`_COMPLETION_VERBS` to entries that raise closes that gap:
if a baseline row's resolution ever touches either table, the test fails loudly, in the table it
happened in, rather than quietly matching a golden value that happened to still be right.

**Scope.** Every row `FIXTURE_GOLDEN`/`INLINE_GOLDEN` (both imported, not re-declared, from the
layer-1 harness) records as resolving *today* — a `None` expectation is the harness's own refusal
population and is out of scope here; the two files together already prove a refusal stays a
refusal (FR-006, R-B), and this test's only question is "did a *resolving* row's path change".
"""

from __future__ import annotations

import re
from typing import NoReturn

import pytest

from pipeline.parse import options_grammar
from pipeline.parse.options_grammar import OptionRowParse as R
from pipeline.parse.options_grammar import parse_row
from tests.enrichment.test_options_grammar_regression import (
    FIXTURE_GOLDEN,
    INLINE_GOLDEN,
    _fixture_rows,
)

#: Only the rows that resolve today — see the module docstring's *Scope*.
_RESOLVING_FIXTURE_GOLDEN: dict[tuple[str, int], R] = {
    key: expected for key, expected in FIXTURE_GOLDEN.items() if expected is not None
}
_RESOLVING_INLINE_GOLDEN: dict[str, R] = {
    description: expected for description, expected in INLINE_GOLDEN.items() if expected is not None
}

#: A head pattern that matches everything reachable — `.*` matches the empty string too, so this
#: fires on any stem `_match_head` still hands `_COMPLETION_HEADS` after `004`'s and `006`'s own
#: tables have both failed to match.
_MATCH_ANYTHING: re.Pattern[str] = re.compile(r".*")


def _raise_if_head_reached(match: re.Match[str]) -> NoReturn:
    raise AssertionError(
        f"a baseline-resolving row reached _COMPLETION_HEADS (matched {match.group(0)!r}); "
        "FR-007's ordering guarantee is broken"
    )


def _raise_if_verb_reached(match: re.Match[str], stem: str, head_end: int) -> NoReturn:
    raise AssertionError(
        f"a baseline-resolving row reached _COMPLETION_VERBS (matched {match.group(0)!r} in "
        f"{stem!r} at head_end={head_end}); FR-007's ordering guarantee is broken"
    )


@pytest.fixture(autouse=True)
def _completion_tables_raise_if_reached(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every test in this file runs with both `008` tables swapped for raising stand-ins.

    `raising=True` is `monkeypatch.setattr`'s default and is exactly what makes this test fail
    correctly *before* T016: with neither symbol defined yet, the patch itself raises
    `AttributeError`, which is this test file's own "confirm failing" (tasks.md T015).
    """
    monkeypatch.setattr(
        options_grammar, "_COMPLETION_HEADS", ((_MATCH_ANYTHING, _raise_if_head_reached),)
    )
    monkeypatch.setattr(
        options_grammar, "_COMPLETION_VERBS", ((_MATCH_ANYTHING, _raise_if_verb_reached),)
    )


@pytest.mark.parametrize(("key", "expected"), sorted(_RESOLVING_FIXTURE_GOLDEN.items()))
def test_a_resolving_fixture_row_never_reaches_the_008_tables(
    key: tuple[str, int], expected: R
) -> None:
    description = _fixture_rows()[key]
    assert parse_row(description) == expected


@pytest.mark.parametrize(("description", "expected"), sorted(_RESOLVING_INLINE_GOLDEN.items()))
def test_a_resolving_inline_description_never_reaches_the_008_tables(
    description: str, expected: R
) -> None:
    assert parse_row(description) == expected


def test_the_resolving_population_is_non_empty() -> None:
    """A guard against the golden's own resolving rows silently emptying out from under this file.

    If every row in both goldens ever became a refusal, every test above would vacuously pass
    with zero parametrizations and this file would stop proving anything without a single red
    test to say so.
    """
    assert _RESOLVING_FIXTURE_GOLDEN
    assert _RESOLVING_INLINE_GOLDEN


def test_the_three_us1_productions_are_named_and_ordered_as_measured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T029: T001's measured zero-group-closure order (class 3 > class 4 > class 5) is a design
    decision, not an accident of tuple iteration. Pinning the builders by name, in order, is what
    makes a later reorder of `_COMPLETION_VERBS` fail here — loudly, by name — rather than only
    as a coverage figure that moved for a reason nobody wrote down.

    This file's own `_completion_tables_raise_if_reached` fixture is `autouse` — every other test
    here deliberately never sees the real table. This is the one test in the file that must, so
    it explicitly undoes that patch first (the `monkeypatch` fixture is function-scoped, and this
    test receives the identical instance the autouse fixture already patched with).
    """
    monkeypatch.undo()
    names = [build.__name__ for _, build in options_grammar._COMPLETION_VERBS]
    assert names == [
        "_distributive_equip",
        "_active_replace_per_unit",
        "_replace_have_singular",
    ]
