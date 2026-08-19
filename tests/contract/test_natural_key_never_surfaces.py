# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added for 009 task T056 (FR-013): the
# export's numeric `datasheet_id` is adopted as an internal natural key only and MUST NOT
# surface as, or displace, a consumer-facing id anywhere in the bundle.
"""FR-013's other half: the numeric export id stays internal.

`data-model.md` §0 states the bundle schema is frozen and unamended by this feature -- this test
is the structural pin for that claim, read three ways: the schema itself has no property shaped
to carry a bare numeric id where an identifier belongs, `CuratedDatasheet.datasheet_id` always
carries the `ds-<slug>[-N]` scheme (never the export's own digits), and the one place the numeric
id genuinely lives -- `curation/unit-map.json`'s `wahapedia_datasheet_id`, an AUTHORED, internal
field -- has no schema path into `schemas/bundle.schema.json` at all.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from tests.factories import datasheet, snapshot

_DATASHEET_ID_PATTERN = re.compile(r"^ds-[a-z0-9-]+$")
_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_curated_datasheet_id_never_reads_as_a_bare_numeric_string() -> None:
    built = snapshot(datasheets=[datasheet()])

    for sheet in built.datasheets:
        assert _DATASHEET_ID_PATTERN.match(sheet.datasheet_id), sheet.datasheet_id
        assert not sheet.datasheet_id.isdigit()


def test_the_bundle_schema_declares_no_numeric_datasheet_identifier_property() -> None:
    """A textual scan of the frozen schema itself: no property named for a numeric export id."""
    schema = json.loads((_REPO_ROOT / "schemas" / "bundle.schema.json").read_text(encoding="utf-8"))
    serialized = json.dumps(schema)

    for forbidden in ("wahapediaDatasheetId", "wahapedia_datasheet_id", "numericDatasheetId"):
        assert forbidden not in serialized, forbidden


def test_wahapedia_datasheet_id_lives_only_in_the_authored_crosswalk() -> None:
    """The numeric id's one legitimate home: `curation/unit-map.schema.json`, an authored INPUT
    schema, never a curated/published one -- `pipeline.curate.authored` reads it, nothing in
    `pipeline.build` or `pipeline.models.curated` re-exports it toward the bundle."""
    unit_map_schema = (_REPO_ROOT / "schemas" / "curation" / "unit-map.schema.json").read_text(
        encoding="utf-8"
    )
    assert "wahapedia_datasheet_id" in unit_map_schema

    curated_module = (_REPO_ROOT / "pipeline" / "models" / "curated.py").read_text(encoding="utf-8")
    assert "wahapedia_datasheet_id" not in curated_module
