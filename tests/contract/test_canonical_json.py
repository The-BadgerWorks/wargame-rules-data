# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts byte-stability across dict
# insertion orders and every other rule of curated-snapshot-format.md §1 and §6 (task T019).
# The manifest checksum is computed over these bytes, so this test is what makes the checksum
# mean anything.
"""The canonical serialiser is determinism. These are its properties.

FR-033/SC-006 require a rebuild from an unchanged tree to produce a byte-identical bundle. The
serialiser is the only place that can be true or false, so the tests below are stated as
byte-level assertions rather than round-trip ones: a round trip would pass happily while the
bytes moved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.build.canonical_json import (
    CanonicalJsonError,
    dumps_bundle,
    dumps_tree,
    encode_bundle,
    encode_tree,
    omit_absent,
    write_bundle,
    write_tree_file,
)


def test_insertion_order_does_not_change_the_bytes() -> None:
    forwards = {"alpha": 1, "beta": 2, "gamma": 3}
    backwards = {"gamma": 3, "beta": 2, "alpha": 1}
    assert encode_bundle(forwards) == encode_bundle(backwards)
    assert encode_tree(forwards) == encode_tree(backwards)


def test_keys_are_sorted_at_every_depth() -> None:
    nested = {"b": {"z": 1, "a": {"n": 2, "m": 3}}, "a": [{"y": 1, "x": 2}]}
    assert dumps_bundle(nested) == '{"a":[{"x":2,"y":1}],"b":{"a":{"m":3,"n":2},"z":1}}'


def test_bundle_uses_compact_separators_and_the_tree_uses_two_space_indent() -> None:
    value = {"a": 1, "b": [1, 2]}
    assert dumps_bundle(value) == '{"a":1,"b":[1,2]}'
    assert dumps_tree(value) == '{\n  "a": 1,\n  "b": [\n    1,\n    2\n  ]\n}'


def test_files_end_with_exactly_one_lf() -> None:
    for payload in (encode_bundle({"a": 1}), encode_tree({"a": 1})):
        assert payload.endswith(b"\n")
        assert not payload.endswith(b"\n\n")
        assert b"\r" not in payload, "CRLF would make the checksum platform-dependent"


def test_non_ascii_is_preserved_rather_than_escaped() -> None:
    # ensure_ascii=False: a name keeps its own characters. The apostrophe difference between the
    # two sources (T'au vs T’au) is normalised for MATCHING, never for emission.
    text = dumps_bundle({"name": "T’au Empire"})
    assert "T’au Empire" in text
    assert "\\u" not in text


def test_floats_are_rejected_rather_than_rounded() -> None:
    with pytest.raises(CanonicalJsonError, match="integers only"):
        dumps_bundle({"points": 1.5})
    with pytest.raises(CanonicalJsonError):
        dumps_tree({"nested": [{"ratio": 0.95}]})


def test_null_is_rejected_because_absence_is_expressed_by_omission() -> None:
    with pytest.raises(CanonicalJsonError, match="omit the key"):
        dumps_bundle({"invuln_save": None})


def test_unsupported_types_are_rejected() -> None:
    with pytest.raises(CanonicalJsonError):
        dumps_bundle({"when": object()})  # type: ignore[dict-item]


def test_booleans_and_integers_are_representable() -> None:
    assert dumps_bundle({"is_legends": False, "points": 90}) == '{"is_legends":false,"points":90}'


def test_omit_absent_drops_none_and_keeps_falsy_values() -> None:
    built = omit_absent({"a": 1, "b": None, "c": 0, "d": False, "e": ""})
    assert built == {"a": 1, "c": 0, "d": False, "e": ""}
    assert "b" not in built


def test_written_files_carry_the_same_bytes_the_encoder_produced(tmp_path: Path) -> None:
    value = {"beta": [3, 1, 2], "alpha": "T’au"}
    bundle_path = tmp_path / "nested" / "rules-x.json"
    tree_path = tmp_path / "nested" / "datasheet.json"

    assert write_bundle(bundle_path, value) == encode_bundle(value)
    assert write_tree_file(tree_path, value) == encode_tree(value)
    assert bundle_path.read_bytes() == encode_bundle(value)
    assert tree_path.read_bytes() == encode_tree(value)
    assert b"\r\n" not in tree_path.read_bytes()


def test_two_serialisations_of_the_same_value_are_byte_identical() -> None:
    value = {"costs": [{"points": 90, "model_count": 5}, {"model_count": 10, "points": 180}]}
    assert encode_bundle(value) == encode_bundle(dict(value))
