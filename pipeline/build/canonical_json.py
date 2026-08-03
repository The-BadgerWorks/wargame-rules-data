# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the single canonical JSON
# serialiser (task T019) per curated-snapshot-format.md §1 and §6: sorted keys at every depth,
# compact separators for the bundle and two-space indent for the tree, ensure_ascii=False, LF,
# one trailing newline, integers only, absent values omitted rather than null.
"""The canonical JSON serialiser.

**This module is determinism.** The published manifest carries a sha256 over the bundle's
bytes, so "the same curated inputs produce the same bytes" is a contract guarantee
(``reference-db-schema.md`` guarantee 6, FR-033, SC-006) and every artifact this repository
writes goes through here. A second serialiser anywhere would silently reopen the gap.

Two surfaces, one set of rules:

============  ===========================  ==========================================
Surface       Function                     Shape
============  ===========================  ==========================================
Bundle        :func:`dumps_bundle`         ``(",", ":")`` separators, one line
Curated tree  :func:`dumps_tree`           two-space indent, ``(",", ": ")`` separators
============  ===========================  ==========================================

Rules applied to both (``curated-snapshot-format.md`` §1, §6):

* Object keys sorted lexicographically **at every depth**.
* ``ensure_ascii=False`` — a name keeps its own characters rather than becoming an escape.
* UTF-8, no BOM, LF line endings, exactly one trailing newline in the file.
* **Integers only.** A float is rejected, not rounded: floats are the classic source of a
  platform-dependent byte difference, and no value in the curated tree or the bundle is
  fractional.
* **Absent values are omitted, never ``null``** (§5). ``None`` is therefore rejected too —
  build the mapping with :func:`omit_absent` instead. Absence is meaningful: the consuming app
  ingests an omitted optional as SQL ``NULL`` and reports the rule as *unevaluated*, whereas a
  serialised ``null`` invites a "we said nothing" value to be read as "we said nothing is
  there".

Array ordering is **not** this module's business — arrays are emitted in their declared key
order by whoever builds them (§2 per array; §3 by table primary key), because only the caller
knows what the declared key is.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final

#: Compact separators for the published bundle — one document, parsed once, never hand-read.
BUNDLE_SEPARATORS: Final[tuple[str, str]] = (",", ":")

#: Readable separators for the curated tree, which is reviewed in a pull request.
TREE_SEPARATORS: Final[tuple[str, str]] = (",", ": ")

#: Two-space indent for the curated tree (``curated-snapshot-format.md`` §1).
TREE_INDENT: Final = 2

#: What a canonical document may contain.
type JsonValue = str | int | bool | Sequence[JsonValue] | Mapping[str, JsonValue]


class CanonicalJsonError(TypeError):
    """A value that cannot appear in a canonical document.

    Raised for a float, a ``None``, a non-string object key, or any type outside
    :data:`JsonValue`. It is a hard failure by design: the alternative is a bundle whose bytes
    depend on the platform, which would make the manifest checksum meaningless.
    """


def _check(value: object, path: str) -> None:
    """Recursively assert ``value`` is representable canonically."""
    if value is None:
        raise CanonicalJsonError(
            f"{path}: null is not representable — omit the key instead "
            "(curated-snapshot-format.md §5)"
        )
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        raise CanonicalJsonError(f"{path}: floats are not representable — integers only (§1)")
    if isinstance(value, str):
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise CanonicalJsonError(f"{path}: object keys must be strings, got {type(key)}")
            _check(item, f"{path}.{key}")
        return
    if isinstance(value, Sequence):
        for index, item in enumerate(value):
            _check(item, f"{path}[{index}]")
        return
    raise CanonicalJsonError(f"{path}: {type(value)} is not representable in canonical JSON")


def _dumps(value: JsonValue, *, separators: tuple[str, str], indent: int | None) -> str:
    _check(value, "$")
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=separators,
        indent=indent,
        allow_nan=False,
    )


def dumps_bundle(value: JsonValue) -> str:
    """Serialise ``value`` in bundle form: sorted keys, compact separators, no trailing newline.

    The trailing newline is a property of the *file*; see :func:`encode_bundle`.
    """
    return _dumps(value, separators=BUNDLE_SEPARATORS, indent=None)


def dumps_tree(value: JsonValue) -> str:
    """Serialise ``value`` in curated-tree form: sorted keys, two-space indent, no trailing
    newline."""
    return _dumps(value, separators=TREE_SEPARATORS, indent=TREE_INDENT)


def encode_bundle(value: JsonValue) -> bytes:
    """Bundle bytes exactly as published: UTF-8, LF, one trailing newline.

    This is what the manifest's ``sha256`` and ``sizeBytes`` are computed over.
    """
    return (dumps_bundle(value) + "\n").encode("utf-8")


def encode_tree(value: JsonValue) -> bytes:
    """Curated-tree file bytes: UTF-8, LF, one trailing newline."""
    return (dumps_tree(value) + "\n").encode("utf-8")


def _write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Binary mode: never let the platform translate LF to CRLF (FR-033 is byte-level).
    path.write_bytes(payload)


def write_bundle(path: Path, value: JsonValue) -> bytes:
    """Write the bundle to ``path`` and return the bytes written."""
    payload = encode_bundle(value)
    _write(path, payload)
    return payload


def write_tree_file(path: Path, value: JsonValue) -> bytes:
    """Write one curated-tree file to ``path`` and return the bytes written."""
    payload = encode_tree(value)
    _write(path, payload)
    return payload


def omit_absent(mapping: Mapping[str, JsonValue | None]) -> dict[str, JsonValue]:
    """Drop keys whose value is ``None`` — the shallow helper for building canonical objects.

    Shallow on purpose: a nested object is built by its own emitter, which knows which of its
    own optionals are absent. A deep prune would happily delete a key some caller meant to
    keep.
    """
    return {key: value for key, value in mapping.items() if value is not None}
