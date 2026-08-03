# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the points-source DOM extraction tests
# (task T044): cost tables, tier labels, detachment cards, DP, force disposition, enhancement
# name/points pairs, and the standing assertion that nothing is paired by document order.
"""Tests for points-source extraction from the reconstructed DOM (FR-001, C1/R2).

Every value here is read **through a reference** — a cost cell is read from inside the ``li``
that also carries its model-count label, a DP cost from inside the card header that also carries
the detachment name. The test that matters most is the last one: shuffling the order in which
the deferred fragments arrive must not change a single extracted number.
"""

from __future__ import annotations

import re
from pathlib import Path

from pipeline.parse.mfm_dom import parse_faction_page
from pipeline.parse.mfm_swap_replay import replay

SAMPLE_MFM = Path(__file__).resolve().parents[2] / "fixtures" / "sample" / "mfm"


def _parsed():  # type: ignore[no-untyped-def]
    html = (SAMPLE_MFM / "emberwrights.html").read_text(encoding="utf-8")
    return parse_faction_page("emberwrights", replay(html).html)


def _block(page, name: str, label: str):  # type: ignore[no-untyped-def]
    matches = [
        b for b in page.unit_blocks if b.unit_display_name == name and b.cost_table_label == label
    ]
    assert len(matches) == 1, f"expected exactly one {name!r} / {label!r} block"
    return matches[0]


def test_plain_cost_table_is_extracted_with_its_label_literal() -> None:
    block = _block(_parsed(), "EMBER SENTINEL", "YOUR UNIT COSTS")
    assert [(row.model_count_label, row.points) for row in block.rows] == [
        ("3 models", 60),
        ("6 models", 115),
    ]
    assert block.faction_slug == "emberwrights"


def test_requisition_threshold_pair_keeps_both_label_literals() -> None:
    """Tier detection keys on the labels, so they are preserved verbatim (data-model §1.2)."""
    page = _parsed()
    first = _block(page, "CINDER WARDEN", "YOUR 1ST TO 2ND UNITS COST")
    later = _block(page, "CINDER WARDEN", "YOUR 3RD + UNIT COSTS")

    assert [(r.model_count_label, r.points) for r in first.rows] == [("5 models", 90), ("10 models", 175)]
    assert [(r.model_count_label, r.points) for r in later.rows] == [("5 models", 100), ("10 models", 195)]


def test_delta_markers_are_captured_but_never_treated_as_points() -> None:
    """``▲ (+15) 155 pts`` is 155 points and a witness for D4d, not 15 and not 170."""
    block = _block(_parsed(), "FORGE MARSHAL", "YOUR UNIT COSTS")
    (row,) = block.rows
    assert row.points == 155
    assert row.delta_marker == "+15"


def test_a_cost_cell_without_a_delta_records_none() -> None:
    block = _block(_parsed(), "EMBER SENTINEL", "YOUR UNIT COSTS")
    assert all(row.delta_marker is None for row in block.rows)


def test_leader_and_support_lists_are_extracted_as_names() -> None:
    """The list is a comma-separated run of unit names, not prose, and stays a list of names."""
    block = _block(_parsed(), "FORGE MARSHAL", "YOUR UNIT COSTS")
    assert list(block.support_targets) == ["EMBER SENTINEL", "CINDER WARDEN"]


def test_a_unit_with_no_leader_or_support_list_records_none() -> None:
    assert list(_block(_parsed(), "EMBER SENTINEL", "YOUR UNIT COSTS").support_targets) == []


def test_detachment_card_carries_dp_disposition_tags_and_enhancements() -> None:
    page = _parsed()
    cards = {card.detachment_name: card for card in page.detachments}
    assert set(cards) == {"ANVIL VIGIL", "CRUCIBLE HOST"}

    anvil = cards["ANVIL VIGIL"]
    assert anvil.dp_cost == 2
    assert anvil.force_disposition == "HOLD THE LINE"
    assert [(e.name, e.points) for e in anvil.enhancements] == [
        ("Emberbound Oath", 25),
        ("Slagged Aegis", 30),
    ]
    assert "UPDATED" in anvil.tags

    crucible = cards["CRUCIBLE HOST"]
    assert crucible.dp_cost == 3
    assert crucible.force_disposition == "BREAK THE SIEGE"
    assert "Unique" in crucible.tags


def test_enhancement_delta_marker_does_not_leak_into_its_points() -> None:
    anvil = next(c for c in _parsed().detachments if c.detachment_name == "ANVIL VIGIL")
    aegis = next(e for e in anvil.enhancements if e.name == "Slagged Aegis")
    assert aegis.points == 30


def test_extraction_is_not_positional() -> None:
    """Reverse the order the deferred fragments arrive in; every extracted value is unchanged.

    The fragments are self-describing (``$RS`` names both ends), so their arrival order is
    presentation. If any assertion below moves, something is being read by document order.
    """
    source = (SAMPLE_MFM / "emberwrights.html").read_text(encoding="utf-8")
    head, _, tail = source.partition('<script>$RC("B:0","S:0")</script>')
    fragments = re.findall(
        r'<div hidden id="[^"]+">.*?</div>\s*<script>\$RS\("[^"]+","[^"]+"\)</script>',
        tail,
        flags=re.DOTALL,
    )
    assert len(fragments) >= 6
    # Emit the independent fragments last-first. Nested ones must still follow their parent, so
    # only the leading independent run is reversed.
    shuffled = head + '<script>$RC("B:0","S:0")</script>' + "".join(fragments[-3::-1] + fragments[-2:])

    original = parse_faction_page("emberwrights", replay(source).html)
    reordered = parse_faction_page("emberwrights", replay(shuffled).html)

    def key(blocks):  # type: ignore[no-untyped-def]
        return sorted(
            (b.unit_display_name, b.cost_table_label, tuple((r.model_count_label, r.points) for r in b.rows))
            for b in blocks
        )

    assert key(reordered.unit_blocks) == key(original.unit_blocks)


def test_a_page_with_no_units_section_yields_no_unit_blocks_rather_than_guessing() -> None:
    page = parse_faction_page("empty", "<html><body><div>nothing here</div></body></html>")
    assert page.unit_blocks == ()
    assert page.detachments == ()
