# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the mechanic-digest test suite (task
# T123), confirmed failing before pipeline.normalize.mechanic_digest existed, covering the
# keying property, the hard-normalisation projection, and the "text never leaves the function"
# guarantee (FR-013, FR-024, C6/R8).
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


def test_table_and_image_content_is_dropped_before_digesting() -> None:
    key = b"repository-key"
    with_table = (
        "<table><tr><td>Distance</td><td>Effect</td></tr></table>"
        '<img src="https://example.invalid/x.png"/> Add 1 to the roll.'
    )
    assert mechanic_digest(with_table, key=key) == mechanic_digest("Add 1 to the roll.", key=key)


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
