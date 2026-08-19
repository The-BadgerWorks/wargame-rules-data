# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added for 009 task T049 (FR-013, SC-004,
# Product Owner decision T047/O2 2026-08-18): the identity-survival check that O2's decision
# designates as the standing guard for the id-stability risk (R-B) rather than pre-authoring the
# whole `-N`-suffix crosswalk population -- every consumer-facing identifier the previous
# published version carried MUST be present, with the same identity, in a migrated build.
"""Identity survival — every consumer-facing id the previous version carried, still present.

FR-013 is stated as a **presence** guarantee, not a coverage ratio: a faction id, datasheet id, or
ability key that existed before and is gone now is a defect regardless of how small a share of
the total roster it is — the coverage ratchets (``validate/coverage.py``) would not necessarily
catch a single dropped id inside an otherwise-healthy percentage. This is the other half of the
same discipline `REC-DETAIL-FACTION-EMPTY` established for a whole-faction loss (`plan.md`
finding 2: a collapsed roster can still read 100 on a ratio).

Deliberately **not wired into any always-on gate here** — the same pattern
``check_unit_map_reverse_coverage`` already established (`validate/refs.py`): a caller passes the
previous version's identifier sets explicitly, so this stays a function a build can call once it
has something to compare against, not a hidden default.
"""

from __future__ import annotations

import json
from collections.abc import Set
from dataclasses import dataclass
from pathlib import Path

from pipeline.models.curated import CuratedSnapshot
from pipeline.models.findings import Finding
from pipeline.report.catalogue import build_finding


@dataclass(frozen=True, slots=True)
class IdentityBaseline:
    """The consumer-facing identifier sets one published version carried (`fixtures/
    identity-baseline/README.md`'s own shape, T014). Carries no name, no value, no prose — every
    member is an identifier this project minted itself."""

    rules_version_id: str
    faction_ids: frozenset[str]
    datasheet_ids: frozenset[str]
    ability_keys: frozenset[str]


def load_identity_baseline(path: Path) -> IdentityBaseline:
    """Read a baseline in `fixtures/identity-baseline/wh40k-11e-2026-08-4.json`'s own shape."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return IdentityBaseline(
        rules_version_id=payload["rules_version_id"],
        faction_ids=frozenset(payload["faction_ids"]),
        datasheet_ids=frozenset(payload["datasheet_ids"]),
        ability_keys=frozenset(payload["ability_keys"]),
    )


def snapshot_identifiers(
    snapshot: CuratedSnapshot,
) -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
    """The same three sets, extracted from a freshly built snapshot rather than a baseline file."""
    return (
        frozenset(faction.faction_id for faction in snapshot.factions),
        frozenset(datasheet.datasheet_id for datasheet in snapshot.datasheets),
        frozenset(snapshot.ability_summaries),
    )


def check_identity_survival(
    baseline: IdentityBaseline,
    *,
    current_faction_ids: Set[str],
    current_datasheet_ids: Set[str],
    current_ability_keys: Set[str],
) -> list[Finding]:
    """FR-013/SC-004: every baseline identifier present, with the same identity, in ``current``.

    One blocking ``CON-IDENTITY-DROPPED`` per missing identifier, naming its kind and value —
    never a count alone, because the whole point (against ``plan.md`` finding 2's "an empty
    roster reads 100" lesson) is that a reader must be able to name exactly which id vanished.
    """
    dropped: list[tuple[str, str]] = [
        *(("faction_id", value) for value in sorted(baseline.faction_ids - current_faction_ids)),
        *(
            ("datasheet_id", value)
            for value in sorted(baseline.datasheet_ids - current_datasheet_ids)
        ),
        *(("ability_key", value) for value in sorted(baseline.ability_keys - current_ability_keys)),
    ]
    return [
        build_finding("CON-IDENTITY-DROPPED", detail={"kind": kind, "id": value})
        for kind, value in dropped
    ]
