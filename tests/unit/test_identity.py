# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the four identity rules (task T040):
# an id is minted once and never re-minted, a renamed unit keeps its id, two distinct entities
# never share an id, and an id is never reused after a removal (FR-014, FR-015).
"""Curated identity is what makes a player's saved army survive an upstream rename.

The failure this guards against is not cosmetic: reusing a retired id would make a saved army
silently resolve to a *different* unit, and a rename handled as removal-plus-addition would drop
the unit out of the army entirely.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline.reconcile.identity import (
    ID_PREFIXES,
    EntityKind,
    IdentityError,
    IdRegistry,
    load_registry,
    slugify,
)


def test_an_id_is_minted_once_and_never_re_minted() -> None:
    registry = IdRegistry()
    first = registry.mint(EntityKind.DATASHEET, "WHP-1001", "Aether Wardens")
    again = registry.mint(EntityKind.DATASHEET, "WHP-1001", "Aether Wardens")
    assert first == again == "ds-aether-wardens"
    assert registry.issued_ids == {"ds-aether-wardens"}


def test_a_renamed_unit_keeps_its_id() -> None:
    registry = IdRegistry()
    original = registry.mint(EntityKind.DATASHEET, "WHP-1001", "Aether Wardens")
    after_rename = registry.mint(EntityKind.DATASHEET, "WHP-1001", "Aether Wardens Elite")

    assert after_rename == original, "a rename must not mint a new id (FR-015)"
    assert registry.existing(EntityKind.DATASHEET, "WHP-1001") == original


def test_two_distinct_entities_never_share_an_id() -> None:
    registry = IdRegistry()
    first = registry.mint(EntityKind.DATASHEET, "WHP-1001", "Storm Riders")
    second = registry.mint(EntityKind.DATASHEET, "WHP-2002", "Storm Riders")

    assert first == "ds-storm-riders"
    assert second == "ds-storm-riders-2"
    assert first != second
    assert len(registry.issued_ids) == 2


def test_an_id_is_never_reused_after_a_removal() -> None:
    registry = IdRegistry()
    retired = registry.mint(EntityKind.DATASHEET, "WHP-1001", "Storm Riders")
    assert registry.retire(EntityKind.DATASHEET, "WHP-1001") == retired

    # The key is gone, but the id is reserved forever.
    assert registry.existing(EntityKind.DATASHEET, "WHP-1001") is None
    assert retired in registry.retired_ids

    reborn = registry.mint(EntityKind.DATASHEET, "WHP-3003", "Storm Riders")
    assert reborn != retired, "a retired id must never be issued again (FR-014)"
    assert reborn == "ds-storm-riders-2"


def test_retiring_and_re_encountering_the_same_key_still_mints_a_fresh_id() -> None:
    registry = IdRegistry()
    original = registry.mint(EntityKind.FACTION, "alpha-legion", "Alpha Legion")
    registry.retire(EntityKind.FACTION, "alpha-legion")
    again = registry.mint(EntityKind.FACTION, "alpha-legion", "Alpha Legion")
    assert again != original


@pytest.mark.parametrize(
    ("kind", "prefix"), [(kind, prefix) for kind, prefix in ID_PREFIXES.items()]
)
def test_each_kind_mints_with_its_contract_prefix(kind: EntityKind, prefix: str) -> None:
    registry = IdRegistry()
    assert registry.mint(kind, "key-1", "Example Name").startswith(f"{prefix}-")


def test_ids_are_scoped_by_kind_so_a_faction_and_a_datasheet_may_share_a_key() -> None:
    registry = IdRegistry()
    faction = registry.mint(EntityKind.FACTION, "shared", "Iron Wardens")
    datasheet = registry.mint(EntityKind.DATASHEET, "shared", "Iron Wardens")
    assert faction == "f-iron-wardens"
    assert datasheet == "ds-iron-wardens"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("T’au Empire", "tau-empire"),
        ("T'au Empire", "tau-empire"),
        ("Emperor's Children", "emperors-children"),
        ("ASSAULT INTERCESSOR SQUAD", "assault-intercessor-squad"),
        ("Hammerfall  Bunker", "hammerfall-bunker"),
    ],
)
def test_slugify_produces_a_stable_ascii_token(name: str, expected: str) -> None:
    assert slugify(name) == expected


def test_a_name_that_yields_no_slug_is_a_hard_failure() -> None:
    with pytest.raises(IdentityError):
        slugify("!!!")


def test_adopting_a_conflicting_assignment_is_refused() -> None:
    registry = IdRegistry()
    registry.adopt(EntityKind.DATASHEET, "WHP-1001", "ds-storm-riders")

    with pytest.raises(IdentityError, match="already assigned"):
        registry.adopt(EntityKind.DATASHEET, "WHP-1001", "ds-something-else")

    with pytest.raises(IdentityError, match="already held"):
        registry.adopt(EntityKind.DATASHEET, "WHP-2002", "ds-storm-riders")


def test_the_registry_is_read_from_the_authored_maps(tmp_path: Path) -> None:
    (tmp_path / "faction-map.json").write_text(
        json.dumps(
            [
                {
                    "mfm_slug": "iron-wardens",
                    "faction_id": "f-iron-wardens",
                    "detail_source_faction_id": "IW",
                }
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "unit-map.json").write_text(
        json.dumps(
            [
                {
                    "datasheet_id": "ds-storm-riders",
                    "mfm_display_name": "STORM RIDERS",
                    "wahapedia_datasheet_id": "WHP-1001",
                    "confirmed_at": "2026-08-02T00:00:00Z",
                    "confirmed_by": "curator",
                }
            ]
        ),
        encoding="utf-8",
    )

    registry = load_registry(tmp_path)

    # Stage 1 of the ladder: a confirmed pairing is returned without consulting a name at all.
    assert registry.mint(EntityKind.DATASHEET, "WHP-1001", "Anything At All") == "ds-storm-riders"
    assert registry.mint(EntityKind.FACTION, "iron-wardens", "Renamed") == "f-iron-wardens"


def test_a_missing_curation_directory_yields_an_empty_registry(tmp_path: Path) -> None:
    assert load_registry(tmp_path / "absent").issued_ids == frozenset()
