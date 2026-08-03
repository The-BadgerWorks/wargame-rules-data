# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the determinism tests (task T051): two
# builds from an identical curated tree produce a byte-identical bundle and an identical sha256,
# and a wall-clock timestamp outside snapshotMeta.publishedAt fails with exit 50.
"""Tests for FR-033 / SC-006 determinism.

The manifest's `sha256` is computed over the bundle, so "the same inputs produce the same bytes"
is not tidiness — it is what makes the checksum mean anything, and it is what lets the publish
job assert that an approved artifact and a rebuilt artifact are the same artifact (FR-039).

The failure mode this guards is a wall-clock timestamp or an iteration-order-dependent array
sneaking into the emitter, where it is invisible until two builds of the same commit disagree.
"""

from __future__ import annotations

import pytest

from pipeline.build.bundle_emit import emit_bundle
from pipeline.build.canonical_json import encode_bundle
from pipeline.build.checksum import (
    BundleChecksum,
    DeterminismError,
    assert_reproducible,
    checksum,
)
from pipeline.exit_codes import ExitCode
from tests import factories


def _bytes(snapshot=None, meta=None) -> bytes:  # type: ignore[no-untyped-def]
    return encode_bundle(emit_bundle(snapshot or factories.snapshot(), meta or factories.meta()))


def test_two_builds_of_the_same_tree_are_byte_identical() -> None:
    assert _bytes() == _bytes()


def test_two_builds_of_the_same_tree_share_a_checksum() -> None:
    first = checksum(_bytes())
    second = checksum(_bytes())
    assert first == second
    assert isinstance(first, BundleChecksum)
    assert len(first.sha256) == 64
    assert first.size_bytes == len(_bytes())


def test_dictionary_insertion_order_does_not_reach_the_bytes() -> None:
    forwards = factories.snapshot(
        factions=[factories.faction("f-aaa"), factories.faction("f-zzz")]
    )
    backwards = factories.snapshot(
        factions=[factories.faction("f-zzz"), factories.faction("f-aaa")]
    )
    assert _bytes(forwards) == _bytes(backwards)


def test_the_only_timestamp_in_the_bundle_is_published_at() -> None:
    bundle = emit_bundle(factories.snapshot(), factories.meta())
    text = encode_bundle(bundle).decode("utf-8")
    assert text.count("2026-06-13T00:00:00Z") == 1
    assert bundle["snapshotMeta"]["publishedAt"] == "2026-06-13T00:00:00Z"


def test_published_at_is_a_build_input_not_now() -> None:
    """Changing it changes the bytes; not passing it is not an option the emitter offers."""
    other = factories.meta().replace(published_at="2026-07-01T00:00:00Z")
    assert _bytes(meta=other) != _bytes()


def test_the_bundle_carries_no_floats_anywhere() -> None:
    def _walk(node: object) -> None:
        assert not isinstance(node, float)
        if isinstance(node, dict):
            for value in node.values():
                _walk(value)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(emit_bundle(factories.snapshot(), factories.meta()))


def test_a_rebuild_whose_checksum_differs_fails_with_the_determinism_code() -> None:
    payload = _bytes()
    assert_reproducible(payload, expected_sha256=checksum(payload).sha256)

    with pytest.raises(DeterminismError) as raised:
        assert_reproducible(payload, expected_sha256="0" * 64)
    assert raised.value.exit_code == ExitCode.NONDETERMINISTIC
    assert raised.value.finding_code == "CON-NONDETERMINISTIC"


def test_the_determinism_failure_names_both_checksums_and_no_content() -> None:
    payload = _bytes()
    with pytest.raises(DeterminismError) as raised:
        assert_reproducible(payload, expected_sha256="0" * 64)
    message = str(raised.value)
    assert checksum(payload).sha256 in message
    assert "0" * 64 in message
    assert "Ember Sentinel" not in message


def test_the_bundle_ends_with_exactly_one_newline() -> None:
    payload = _bytes()
    assert payload.endswith(b"\n")
    assert not payload.endswith(b"\n\n")
    assert b"\r\n" not in payload
