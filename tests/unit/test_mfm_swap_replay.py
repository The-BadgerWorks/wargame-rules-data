# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the swap-replay tests (task T043):
# replay is reference-based and total, an unfilled placeholder or an unclaimed source block is
# SRC-STRUCTURE-CHANGED at exit 41, and replaying the same input twice yields an identical tree.
"""Tests for the points source's deferred-placeholder replay (FR-008, research D4a).

The single claim under test is that **nothing is paired by document order**. The page hands us
an explicit id-to-id move instruction for every deferred fragment, so reconstruction is a
lookup, not a zip. That matters because the failure mode of positional pairing — every unit on
a page priced one row off — is invisible without a second source and lands in a player's hands
at a tournament.

The second claim is that replay is **total**: a leftover placeholder or a source block nobody
claimed means some value is unknowable, and the run must stop rather than emit the rest.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.exit_codes import ExitCode
from pipeline.parse.mfm_swap_replay import StructureChanged, replay

SAMPLE_MFM = Path(__file__).resolve().parents[2] / "fixtures" / "sample" / "mfm"


def _page(name: str) -> str:
    return (SAMPLE_MFM / f"{name}.html").read_text(encoding="utf-8")


def test_replay_fills_every_placeholder_from_its_named_source() -> None:
    result = replay(_page("emberwrights"))

    assert result.unfilled_placeholders == ()
    assert result.unclaimed_sources == ()
    assert result.swaps_applied > 0
    assert "<template" not in result.html
    assert "hidden id=" not in result.html


def test_replay_is_reference_based_not_positional() -> None:
    """The block whose placeholder appears FIRST is not the one whose source appears first.

    ``P:9``/``S:9`` (FORGE MARSHAL) is declared third in the grid but its source block is
    emitted after ``S:4``'s, and its own nested ``P:b`` is filled later still. If replay were
    positional the marshal would collect the warden's numbers.
    """
    html = replay(_page("emberwrights")).html

    marshal = html[html.index("FORGE MARSHAL") :]
    marshal = marshal[: marshal.index("</div>", marshal.index("155 pts"))]
    assert "155 pts" in marshal
    assert "90 pts" not in marshal


def test_nested_placeholder_is_filled_by_a_later_swap() -> None:
    """``S:9``'s own body carries ``P:b``, which only a subsequent instruction fills."""
    result = replay(_page("emberwrights"))
    assert "P:b" not in result.html
    assert result.unfilled_placeholders == ()


def test_replay_is_deterministic() -> None:
    source = _page("emberwrights")
    assert replay(source).html == replay(source).html


def test_unfilled_placeholder_is_a_structural_failure() -> None:
    with pytest.raises(StructureChanged) as raised:
        replay(_page("glasswold-covenant"))

    assert raised.value.finding_code == "SRC-STRUCTURE-CHANGED"
    assert raised.value.exit_code == ExitCode.SOURCE_STRUCTURE_CHANGED


def test_structural_failure_names_shapes_not_source_text() -> None:
    """A diagnostic may name ids and counts. It may never quote the page (FR-013)."""
    with pytest.raises(StructureChanged) as raised:
        replay(_page("glasswold-covenant"))

    message = str(raised.value)
    assert "P:2" in message
    assert "S:9" in message
    assert "GLASSWOLD SKIRMISHER" not in message


def test_source_block_with_no_placeholder_is_a_structural_failure() -> None:
    html = (
        "<div><template id='P:1'></template></div>"
        "<div hidden id='S:1'><span>1 pts</span></div>"
        '<script>$RS("S:1","P:1")</script>'
        "<div hidden id='S:2'><span>2 pts</span></div>"
    )
    with pytest.raises(StructureChanged, match="S:2"):
        replay(html)


def test_placeholder_named_by_no_instruction_is_a_structural_failure() -> None:
    html = "<div><template id='P:1'></template></div>"
    with pytest.raises(StructureChanged, match="P:1"):
        replay(html)


def test_boundary_reveal_form_takes_its_arguments_the_other_way_round() -> None:
    """``$RC("B:n","S:n")`` names the placeholder first; ``$RS("S:n","P:n")`` names it second."""
    html = (
        "<div><template id='B:0'></template></div>"
        "<div hidden id='S:0'><span>ok</span></div>"
        '<script>$RC("B:0","S:0")</script>'
    )
    result = replay(html)
    assert "ok" in result.html
    assert result.unfilled_placeholders == ()


def test_instruction_naming_a_missing_element_is_a_structural_failure() -> None:
    html = '<div><template id=\'P:1\'></template></div><script>$RS("S:1","P:1")</script>'
    with pytest.raises(StructureChanged, match="S:1"):
        replay(html)
