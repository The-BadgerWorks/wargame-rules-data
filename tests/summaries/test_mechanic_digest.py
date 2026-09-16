# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the mechanic-digest test suite (task
# T123), confirmed failing before pipeline.normalize.mechanic_digest existed, covering the
# keying property, the hard-normalisation projection, and the "text never leaves the function"
# guarantee (FR-013, FR-024, C6/R8).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the table-content receipt (010 rung R9,
# task 3), written failing-first: a table cell's number changing must move the digest, and the
# paired direction that an img/svg/script/style edit still must not. The superseded
# `test_table_and_image_content_is_dropped_before_digesting` was narrowed to image alone.
"""The keyed digest: keying is not decoration, and normalisation is not lossy of mechanics.

Every text used here is invented placeholder prose (research D10) — never real MFM or
Wahapedia wording.
"""

from __future__ import annotations

import logging

import pytest

from pipeline.config import load_config
from pipeline.normalize.mechanic_digest import (
    DigestKeyMissingError,
    hard_normalise,
    mechanic_digest,
    resolve_digest_key,
)


def test_digest_is_stable_and_keyed() -> None:
    text = "Invented placeholder prose describing one mechanic, for this data set only."
    digest = mechanic_digest(text, key=b"repository-key")

    assert digest == mechanic_digest(text, key=b"repository-key")
    assert digest != mechanic_digest(text, key=b"a-different-key")


def test_digest_is_128_bits_of_hex_and_reveals_nothing_of_its_input() -> None:
    text = "Roll one D6; on a 4+, this unit regains up to invented-count lost wounds."
    digest = mechanic_digest(text, key=b"k")

    assert len(digest) == 32  # 128 bits, hex
    assert all(c in "0123456789abcdef" for c in digest)
    assert "invented" not in digest
    assert "wounds" not in digest


def test_an_unkeyed_hash_of_the_same_text_would_be_a_verification_oracle_but_this_is_not() -> None:
    """The property C6/R8 exists for: two different keys never agree, so nobody holding a
    candidate wording and only a public algorithm can confirm it against a committed digest."""
    text = "Add one to hit rolls for models in this unit while it remains stationary."
    by_key_a = mechanic_digest(text, key=b"key-a")
    by_key_b = mechanic_digest(text, key=b"key-b")

    assert by_key_a != by_key_b


def test_markup_only_edit_leaves_the_digest_unchanged() -> None:
    key = b"repository-key"
    plain = "Add 1 to the roll."
    marked_up = '<span class="kwb">Add 1</span> to the roll.'

    assert mechanic_digest(plain, key=key) == mechanic_digest(marked_up, key=key)


def test_whitespace_and_entity_reflow_leaves_the_digest_unchanged() -> None:
    key = b"repository-key"
    tidy = "Add 1 to the roll."
    reflowed = "Add&nbsp;1   to\nthe   roll."

    assert mechanic_digest(tidy, key=key) == mechanic_digest(reflowed, key=key)


def test_casing_and_punctuation_changes_leave_the_digest_unchanged() -> None:
    key = b"repository-key"
    assert mechanic_digest("Add 1 to the roll.", key=key) == mechanic_digest(
        "ADD 1 TO THE ROLL", key=key
    )


def test_image_content_is_dropped_before_digesting() -> None:
    """010 R9 task 3 narrowed this test from "table and image" to image alone. The table half
    asserted the change-detection gap round 8 measured — a cell could move without the digest
    moving — and is now inverted by `test_a_table_cell_change_moves_the_digest` below. The image
    half is unchanged and still load-bearing: an artwork reference is never a mechanic."""
    key = b"repository-key"
    with_image = '<img src="https://example.invalid/x.png"/> Add 1 to the roll.'
    assert mechanic_digest(with_image, key=key) == mechanic_digest("Add 1 to the roll.", key=key)


def test_a_mechanic_change_moves_the_digest() -> None:
    key = b"repository-key"
    assert mechanic_digest("Add 1 to the roll.", key=key) != mechanic_digest(
        "Add 2 to the roll.", key=key
    )


def test_hard_normalise_is_the_projection_the_digest_is_taken_over() -> None:
    assert hard_normalise("<b>Add 1</b> to the roll.") == hard_normalise("add   1 to the roll")


def test_resolve_digest_key_reads_configuration_and_never_logs_the_value(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.DEBUG):
        config = load_config(env={"WGC_MECHANIC_DIGEST_KEY": "a-repository-secret"})
        key = resolve_digest_key(config)

    assert key == b"a-repository-secret"
    for record in caplog.records:
        assert "a-repository-secret" not in record.getMessage()


def test_resolve_digest_key_refuses_an_empty_key() -> None:
    config = load_config(env={"WGC_MECHANIC_DIGEST_KEY": ""})
    with pytest.raises(DigestKeyMissingError):
        resolve_digest_key(config)


# -- 010 R9, task 3: the digest covers table content the drafter reads ---------------------------
#
# Round 8 measured 17 keys whose table content never reached `hard_normalise`, and mutating every
# cell in all 17 left the projection unchanged, 17/17. `tools/draft_summaries.py` passes the raw,
# unstripped text to the drafting prompt, so a summary drafted from a tabular mechanic could
# never auto-flag when that table changed. Every text below is invented placeholder prose.


def test_a_table_cell_change_moves_the_digest() -> None:
    """The receipt. Revert the `_DROPPED_SUBTREES` change and these two digests are identical,
    which is the change-detection gap round 8 measured: the drafter reads the cell, the digest
    does not, so the summary can never be flagged when the cell moves."""
    key = b"repository-key"
    before = "Range effect: <table><tr><td>Fen</td><td>3</td></tr></table>"
    after = "Range effect: <table><tr><td>Fen</td><td>4</td></tr></table>"

    assert mechanic_digest(before, key=key) != mechanic_digest(after, key=key), (
        "identical digests mean table content is still dropped before hard_normalise, so a "
        "tabular mechanic can change upstream without its summary ever being flagged"
    )


def test_table_content_reaches_the_projection_the_digest_is_taken_over() -> None:
    key = b"repository-key"
    tabular = "<table><tr><td>Fen</td><td>3</td></tr></table>"

    assert hard_normalise(tabular) == "fen 3"
    assert mechanic_digest(tabular, key=key) == mechanic_digest("Fen 3", key=key)


@pytest.mark.parametrize(
    ("before", "after"),
    [
        pytest.param(
            '<img src="https://example.invalid/a.png">Grelth 7</img> Add 1 to the roll.',
            '<img src="https://example.invalid/b.png">Grelth 8</img> Add 1 to the roll.',
            id="img-subtree",
        ),
        pytest.param(
            "<svg><title>Grelth 7</title></svg> Add 1 to the roll.",
            "<svg><title>Grelth 8</title></svg> Add 1 to the roll.",
            id="svg-subtree",
        ),
        pytest.param(
            "<script>var invented = 7;</script> Add 1 to the roll.",
            "<script>var invented = 8;</script> Add 1 to the roll.",
            id="script-subtree",
        ),
        pytest.param(
            "<style>.invented { top: 7px; }</style> Add 1 to the roll.",
            "<style>.invented { top: 8px; }</style> Add 1 to the roll.",
            id="style-subtree",
        ),
    ],
)
def test_artwork_and_payload_subtrees_still_never_reach_the_digest(before: str, after: str) -> None:
    """The other direction: only `table` moved. An artwork reference or a stylesheet edit must
    still leave the digest exactly where it was, and equal to the bare mechanic's own digest."""
    key = b"repository-key"
    plain = mechanic_digest("Add 1 to the roll.", key=key)

    assert mechanic_digest(before, key=key) == plain
    assert mechanic_digest(after, key=key) == plain
