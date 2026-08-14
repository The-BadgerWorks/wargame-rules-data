# AI-Assisted: Claude Code (model: claude-sonnet-5) - User Story 4's independent test (007 task
# T035): T007's unit-size-header fixtures (GF13/GF14/GF15) produce no composition row for either
# header shape while the near-miss genuine model row still resolves, and T009's
# `loadout_datasheet()` fixture's equipment-field additions are visible in a regenerated `data/`
# tree's own written JSON — not merely in the round-tripped Python object (FR-010, FR-012,
# SC-003, SC-004).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Half one rewritten for the Product Owner's
# 2026-08-14 decision (T061 review): a flagged header-shape row now SURVIVES as an advisory
# CMP-HEADER-ROW finding instead of being auto-dropped, because the live corpus proved the
# automatic conjunction had real false positives (three duo-sheet first models). See
# tests/enrichment/test_composition_header_refusal.py for the full account and the curator
# `remove` override that is now the only way a confirmed phantom leaves the composition.
"""User Story 4, end to end: trust the Kill Team cluster and the curated review surface.

The tests beside this one prove the pieces: the five-signal conjunction
(``test_composition_header_refusal.py``) and the write/read round trip
(``test_curated_roundtrip.py``). This one proves the **story** — a reviewer reading a rebuilt
Kill Team datasheet sees a fabricated "MODELS MAXIMUM" row flagged for their own review rather
than either silently kept or silently dropped, and a reviewer reading a regenerated `data/` tree's
diff sees every `006` structure this feature stops silently losing, in the tree's own bytes, not
only in memory.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from pipeline.curate.assemble import _composition_entries
from pipeline.curate.authored import AuthoredContent
from pipeline.curate.prior import read_curated_tree
from pipeline.curate.writer import write_tree
from pipeline.parse.wahapedia_csv import CsvReadResult, read_file
from tests.enrichment.conftest import curated_models
from tests.factories import faction, loadout_datasheet, snapshot

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "wahapedia"


def _composition_detail() -> Mapping[str, CsvReadResult]:
    return {
        "Datasheets_unit_composition.csv": read_file(FIXTURES / "Datasheets_unit_composition.csv"),
    }


# --- half one: no Kill Team datasheet carries a fabricated header row --------------------------


def test_header_row_candidates_are_flagged_for_review_while_every_row_still_resolves() -> None:
    detail = _composition_detail()

    two_row_header, two_row_findings = _composition_entries(
        "GF13", "ds-fenward-cohort-alpha", detail, AuthoredContent(), curated_models("GF13")
    )
    single_row_header, single_row_findings = _composition_entries(
        "GF14", "ds-fenward-cohort-beta", detail, AuthoredContent(), curated_models("GF14")
    )
    near_miss, near_miss_findings = _composition_entries(
        "GF15", "ds-fenward-relict-watch", detail, AuthoredContent(), curated_models("GF15")
    )

    # Both measured header shapes: the fabricated row SURVIVES (2026-08-14 PO decision), flagged
    # via an ADVISORY finding a reviewer can act on rather than a blocking auto-drop.
    assert [e.model_name for e in two_row_header] == [
        "Fenward Cohort",
        "Fenward Sergeant",
        "Fenward Trooper",
    ]
    assert "CMP-HEADER-ROW" in [f.finding_code for f in two_row_findings]
    assert [e.model_name for e in single_row_header] == [
        "Fenward Vanguard Squad",
        "Fenward Outrider",
    ]
    assert "CMP-HEADER-ROW" in [f.finding_code for f in single_row_findings]

    # The near-miss: every genuine row still resolves, and nothing is ever flagged.
    assert [e.model_name for e in near_miss] == [
        "Fenward Relict Warden",
        "Fenward Relict Line",
        "Fenward Relict Skirmisher",
    ]
    assert "CMP-HEADER-ROW" not in [f.finding_code for f in near_miss_findings]


# --- half two: the curated tree's own diff shows what a reviewer is approving ------------------


def test_the_equipment_field_additions_are_visible_in_the_written_trees_own_json(
    tmp_path: Path,
) -> None:
    datasheet = loadout_datasheet()
    original_snapshot = snapshot(factions=[faction()], datasheets=[datasheet])

    data_dir = tmp_path / "data" / "wh40k-11e"
    write_tree(original_snapshot, data_dir=data_dir, curation_dir=tmp_path / "curation")

    datasheet_file = (
        data_dir
        / "factions"
        / datasheet.faction_id
        / "datasheets"
        / f"{datasheet.datasheet_id}.json"
    )
    raw = datasheet_file.read_text(encoding="utf-8")

    # A reviewer reading a diff of THIS file — not a round-tripped Python object — sees every
    # class research D2 found missing: equipment groups (with items), default_equipment_state,
    # option_choices[].items, and the three option-group eligibility columns. Each substring
    # below is a key this feature adds to the writer's own serialisation (`_datasheet` in
    # writer.py), so its presence in the raw bytes is exactly what "visible in the diff" means.
    for expected_key in (
        '"equipment_groups"',
        '"default_equipment_state"',
        '"eligible_model_name"',
        '"eligible_max_count"',
        '"is_per_model"',
        '"items"',
    ):
        assert expected_key in raw, f"{expected_key} missing from the written datasheet file"

    # Round-tripping the same tree confirms the diff is not cosmetic: what a reviewer sees in the
    # file is what a rebuild-from-tree (what `validate` does) actually reconstructs.
    rebuilt = read_curated_tree(data_dir)
    assert rebuilt is not None
    (rebuilt_datasheet,) = rebuilt.datasheets
    assert rebuilt_datasheet.equipment_groups != ()
    assert rebuilt_datasheet.default_equipment_state is not None
    assert any(choice.items for choice in rebuilt_datasheet.option_choices)
    assert rebuilt_datasheet.option_groups[0].eligible_model_name is not None
