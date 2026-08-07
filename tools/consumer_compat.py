# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the consumer-compatibility check
# (task T077): ingest a bundle into the exact schema reference-db-schema.md v1.2.0 declares,
# enforce the §1 guarantees at ingestion time, and price a multi-detachment army from the result.
# AI-Assisted: Claude Code (model: claude-opus-5) - Fixed the two tool-side defects the first run
# against a real bundle exposed (docs/follow-ups.md item 8): foreign keys are now deferred to
# COMMIT, so a self-referencing faction key survives the contract's own id sort; and duplicate
# primary keys are DETECTED and reported rather than crashing the run — including the ones SQLite
# cannot see, where a key component is NULL. The schema stays at v1.2.0 deliberately.
"""Prove a bundle is ingestible, by ingesting it.

`reference-db-schema.md` calls the SQLite schema the **ingestion target** and the bundle the
**wire format**, and puts the obligation on the producer to emit a bundle from which exactly
that schema can be built *with no additional input*. This module is that claim, executed: it
creates the schema verbatim, loads every array into its table mechanically, turns on real
foreign keys, and then prices an army the way the consuming app will.

**Why this lives here rather than in the app.** The app is the natural home for its own
ingestor, and when it exists this check should be replaced by a run of it. Until then the
producer would otherwise be shipping a wire format nobody has ever read, and "it validates
against our schema" is a much weaker claim than "it loads, its foreign keys resolve, and an
army priced from it comes to the number we expect".

The pricing exercise is deliberately the awkward case: copy-indexed tiers, a squad size that is
not a listed band, a wargear cost, two detachments, and an enhancement on each — every rule the
v1.2.0 additions exist for, in one army.

**The schema below stays at v1.2.0 on purpose.** This module is the stand-in for the *released*
consumer, and `tests/publication/test_consumer_compat_enriched.py` asserts it names none of
`004`'s arrays or columns — that assertion is the additive-compatibility proof. Teaching it the
v1.3.x tables would quietly delete that evidence. What it must keep up with is not the schema
but the **ingestion behaviour**: how a real ingestor handles a self-referencing foreign key, and
what it does when the wire format hands it two rows for one primary key.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

#: The schema exactly as `reference-db-schema.md` §3 declares it. Copied rather than generated,
#: because the point of the check is to fail when the producer and that document disagree.
SCHEMA: Final = """
CREATE TABLE snapshot_meta (
  schema_contract_version        INTEGER NOT NULL,
  restriction_vocabulary_version INTEGER NOT NULL,
  rules_version_id               TEXT    NOT NULL,
  published_at                   TEXT    NOT NULL,
  source_note                    TEXT    NOT NULL
);
CREATE TABLE edition (
  id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
  display_order INTEGER NOT NULL
);
CREATE TABLE edition_rule (
  edition_id TEXT NOT NULL REFERENCES edition(id), rule_key TEXT NOT NULL,
  value_json TEXT NOT NULL, PRIMARY KEY (edition_id, rule_key)
);
CREATE TABLE game_size_rule (
  id TEXT PRIMARY KEY, edition_id TEXT NOT NULL REFERENCES edition(id), label TEXT NOT NULL,
  min_points INTEGER NOT NULL, max_points INTEGER NOT NULL,
  detachment_points_budget INTEGER NOT NULL, max_detachments INTEGER NOT NULL,
  max_enhancements INTEGER NOT NULL
);
CREATE TABLE faction (
  id TEXT PRIMARY KEY, edition_id TEXT NOT NULL REFERENCES edition(id), code TEXT NOT NULL,
  name TEXT NOT NULL, parent_faction_id TEXT REFERENCES faction(id)
);
CREATE TABLE detachment (
  id TEXT PRIMARY KEY, edition_id TEXT NOT NULL REFERENCES edition(id),
  faction_id TEXT NOT NULL REFERENCES faction(id), name TEXT NOT NULL,
  detachment_points_cost INTEGER NOT NULL, is_legends BOOLEAN NOT NULL DEFAULT 0
);
CREATE TABLE detachment_restriction (
  id TEXT PRIMARY KEY, edition_id TEXT NOT NULL REFERENCES edition(id),
  detachment_id TEXT REFERENCES detachment(id), restriction_type TEXT NOT NULL,
  params_json TEXT NOT NULL, message_template TEXT NOT NULL
);
CREATE TABLE enhancement (
  id TEXT PRIMARY KEY, edition_id TEXT NOT NULL REFERENCES edition(id),
  detachment_id TEXT NOT NULL REFERENCES detachment(id), name TEXT NOT NULL,
  points INTEGER NOT NULL, max_per_army INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE enhancement_eligibility (
  enhancement_id TEXT NOT NULL REFERENCES enhancement(id), rule_type TEXT NOT NULL,
  value TEXT NOT NULL, PRIMARY KEY (enhancement_id, rule_type, value)
);
CREATE TABLE datasheet (
  id TEXT PRIMARY KEY, edition_id TEXT NOT NULL REFERENCES edition(id),
  faction_id TEXT NOT NULL REFERENCES faction(id), name TEXT NOT NULL, role TEXT,
  is_legends BOOLEAN NOT NULL DEFAULT 0, is_character BOOLEAN NOT NULL DEFAULT 0,
  is_epic_hero BOOLEAN NOT NULL DEFAULT 0, is_battleline BOOLEAN NOT NULL DEFAULT 0,
  is_dedicated_transport BOOLEAN NOT NULL DEFAULT 0, max_copies_per_army INTEGER,
  damaged_threshold INTEGER, detail_edition_code TEXT
);
CREATE TABLE datasheet_keyword (
  datasheet_id TEXT NOT NULL REFERENCES datasheet(id), keyword TEXT NOT NULL,
  is_faction_keyword BOOLEAN NOT NULL DEFAULT 0, model_scope TEXT,
  PRIMARY KEY (datasheet_id, keyword, model_scope)
);
CREATE TABLE datasheet_model (
  datasheet_id TEXT NOT NULL REFERENCES datasheet(id), line INTEGER NOT NULL,
  name TEXT NOT NULL, movement TEXT NOT NULL, toughness INTEGER NOT NULL, save TEXT NOT NULL,
  invuln_save TEXT, wounds INTEGER NOT NULL, leadership TEXT NOT NULL,
  objective_control INTEGER NOT NULL, base_size TEXT, PRIMARY KEY (datasheet_id, line)
);
CREATE TABLE datasheet_cost (
  datasheet_id TEXT NOT NULL REFERENCES datasheet(id), model_count INTEGER NOT NULL,
  points INTEGER NOT NULL, label TEXT NOT NULL,
  pricing_confidence TEXT NOT NULL DEFAULT 'verified',
  PRIMARY KEY (datasheet_id, model_count)
);
CREATE TABLE datasheet_cost_tier (
  datasheet_id TEXT NOT NULL REFERENCES datasheet(id), model_count INTEGER NOT NULL,
  copy_index_min INTEGER NOT NULL, points INTEGER NOT NULL, label TEXT NOT NULL,
  pricing_confidence TEXT NOT NULL DEFAULT 'verified',
  PRIMARY KEY (datasheet_id, model_count, copy_index_min)
);
CREATE TABLE datasheet_wargear_option (
  id TEXT PRIMARY KEY, datasheet_id TEXT NOT NULL REFERENCES datasheet(id),
  group_key TEXT NOT NULL, name TEXT NOT NULL, points_delta INTEGER NOT NULL,
  max_per_unit INTEGER, models_per_instance INTEGER
);
CREATE TABLE datasheet_weapon (
  datasheet_id TEXT NOT NULL REFERENCES datasheet(id), line INTEGER NOT NULL, name TEXT NOT NULL,
  is_melee BOOLEAN NOT NULL, range TEXT, attacks TEXT NOT NULL, skill TEXT NOT NULL,
  strength TEXT NOT NULL, armour_penetration TEXT NOT NULL, damage TEXT NOT NULL,
  ability_keywords TEXT, PRIMARY KEY (datasheet_id, line)
);
CREATE TABLE datasheet_ability (
  datasheet_id TEXT NOT NULL REFERENCES datasheet(id), name TEXT NOT NULL,
  ability_type TEXT NOT NULL, summary TEXT NOT NULL, PRIMARY KEY (datasheet_id, name)
);
CREATE TABLE datasheet_leader_pair (
  leader_datasheet_id TEXT NOT NULL REFERENCES datasheet(id),
  bodyguard_datasheet_id TEXT NOT NULL REFERENCES datasheet(id),
  PRIMARY KEY (leader_datasheet_id, bodyguard_datasheet_id)
);
CREATE TABLE datasheet_detachment_eligibility (
  datasheet_id TEXT NOT NULL REFERENCES datasheet(id),
  detachment_id TEXT NOT NULL REFERENCES detachment(id), is_allowed BOOLEAN NOT NULL,
  PRIMARY KEY (datasheet_id, detachment_id)
);
"""

#: bundle array -> (table, columns in declaration order). The load is mechanical: this mapping
#: is the whole ingestor, which is what `curated-snapshot-format.md` §3 promises the app.
TABLES: Final[Mapping[str, tuple[str, tuple[str, ...]]]] = {
    "editions": ("edition", ("id", "code", "name", "displayOrder")),
    "editionRules": ("edition_rule", ("editionId", "ruleKey", "valueJson")),
    "gameSizeRules": (
        "game_size_rule",
        (
            "id",
            "editionId",
            "label",
            "minPoints",
            "maxPoints",
            "detachmentPointsBudget",
            "maxDetachments",
            "maxEnhancements",
        ),
    ),
    "factions": ("faction", ("id", "editionId", "code", "name", "parentFactionId")),
    "detachments": (
        "detachment",
        ("id", "editionId", "factionId", "name", "detachmentPointsCost", "isLegends"),
    ),
    "detachmentRestrictions": (
        "detachment_restriction",
        ("id", "editionId", "detachmentId", "restrictionType", "paramsJson", "messageTemplate"),
    ),
    "enhancements": (
        "enhancement",
        ("id", "editionId", "detachmentId", "name", "points", "maxPerArmy"),
    ),
    "enhancementEligibility": (
        "enhancement_eligibility",
        ("enhancementId", "ruleType", "value"),
    ),
    "datasheets": (
        "datasheet",
        (
            "id",
            "editionId",
            "factionId",
            "name",
            "role",
            "isLegends",
            "isCharacter",
            "isEpicHero",
            "isBattleline",
            "isDedicatedTransport",
            "maxCopiesPerArmy",
            "damagedThreshold",
            "detailEditionCode",
        ),
    ),
    "datasheetKeywords": (
        "datasheet_keyword",
        ("datasheetId", "keyword", "isFactionKeyword", "modelScope"),
    ),
    "datasheetModels": (
        "datasheet_model",
        (
            "datasheetId",
            "line",
            "name",
            "movement",
            "toughness",
            "save",
            "invulnSave",
            "wounds",
            "leadership",
            "objectiveControl",
            "baseSize",
        ),
    ),
    "datasheetWeapons": (
        "datasheet_weapon",
        (
            "datasheetId",
            "line",
            "name",
            "isMelee",
            "range",
            "attacks",
            "skill",
            "strength",
            "armourPenetration",
            "damage",
            "abilityKeywords",
        ),
    ),
    "datasheetAbilities": (
        "datasheet_ability",
        ("datasheetId", "name", "abilityType", "summary"),
    ),
    "datasheetCosts": (
        "datasheet_cost",
        ("datasheetId", "modelCount", "points", "label", "pricingConfidence"),
    ),
    "datasheetCostTiers": (
        "datasheet_cost_tier",
        ("datasheetId", "modelCount", "copyIndexMin", "points", "label", "pricingConfidence"),
    ),
    "datasheetWargearOptions": (
        "datasheet_wargear_option",
        ("id", "datasheetId", "groupKey", "name", "pointsDelta", "maxPerUnit", "modelsPerInstance"),
    ),
    "datasheetLeaderPairs": (
        "datasheet_leader_pair",
        ("leaderDatasheetId", "bodyguardDatasheetId"),
    ),
    "datasheetDetachmentEligibility": (
        "datasheet_detachment_eligibility",
        ("datasheetId", "detachmentId", "isAllowed"),
    ),
}

MIN_CUSTOM_POINT_LIMIT: Final = 500
MAX_CUSTOM_POINT_LIMIT: Final = 5000


def _snake(column: str) -> str:
    return "".join(f"_{c.lower()}" if c.isupper() else c for c in column)


@dataclass(slots=True)
class CompatResult:
    """What the check found. ``violations`` empty is the pass condition."""

    tables: dict[str, int] = field(default_factory=dict)
    violations: list[str] = field(default_factory=list)
    army_total: int = 0
    army_lines: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations


#: Table -> the primary key `reference-db-schema.md` §3 declares for it, in bundle column names.
#: Only the tables this v1.2.0 ingestor builds; the mapping is per-array in :data:`TABLES`.
PRIMARY_KEYS: Final[Mapping[str, tuple[str, ...]]] = {
    "editions": ("id",),
    "editionRules": ("editionId", "ruleKey"),
    "gameSizeRules": ("id",),
    "factions": ("id",),
    "detachments": ("id",),
    "detachmentRestrictions": ("id",),
    "enhancements": ("id",),
    "enhancementEligibility": ("enhancementId", "ruleType", "value"),
    "datasheets": ("id",),
    "datasheetKeywords": ("datasheetId", "keyword", "modelScope"),
    "datasheetModels": ("datasheetId", "line"),
    "datasheetWeapons": ("datasheetId", "line"),
    "datasheetAbilities": ("datasheetId", "name"),
    "datasheetCosts": ("datasheetId", "modelCount"),
    "datasheetCostTiers": ("datasheetId", "modelCount", "copyIndexMin"),
    "datasheetWargearOptions": ("id",),
    "datasheetLeaderPairs": ("leaderDatasheetId", "bodyguardDatasheetId"),
    "datasheetDetachmentEligibility": ("datasheetId", "detachmentId"),
}


def duplicate_keys(bundle: Mapping[str, Any]) -> list[str]:
    """Rows that share a declared primary key, checked **before** the load rather than by it.

    Two reasons it cannot be left to SQLite. The first is that an `IntegrityError` on the first
    collision ends the run, and a report that names one duplicate out of hundreds is not a
    report. The second is the load-bearing one: SQLite treats NULLs in a unique index as
    *distinct*, so `datasheet_keyword`'s trailing nullable `model_scope` means it accepts
    duplicate keyword rows without a murmur and the app shows the keyword twice. Absence has to
    compare equal to absence here, because the engine will not do it.

    Byte-identical rows and rows that disagree are reported separately. They are different
    defects: the first is one source page printed twice and collapses losslessly, the second is
    two answers to one question and needs a human.
    """
    violations: list[str] = []

    for array, keys in TABLES.items():
        primary = PRIMARY_KEYS.get(array)
        if primary is None:  # pragma: no cover - TABLES and PRIMARY_KEYS are written together
            continue

        table = keys[0]
        grouped: dict[tuple[str, ...], list[Mapping[str, Any]]] = {}
        for row in bundle[array]:
            identity = tuple(_key_part(row.get(column)) for column in primary)
            grouped.setdefault(identity, []).append(row)

        colliding = {key: rows for key, rows in grouped.items() if len(rows) > 1}
        if not colliding:
            continue

        identical = sum(
            1
            for rows in colliding.values()
            if len({json.dumps(row, sort_keys=True) for row in rows}) == 1
        )
        excess = sum(len(rows) - 1 for rows in colliding.values())
        violations.append(
            f"guarantee 12: {table} has {len(colliding)} duplicate primary key(s) "
            f"({excess} excess row(s); {identical} of the keys carry identical rows, "
            f"{len(colliding) - identical} disagree)"
        )

    return violations


def _key_part(value: Any) -> str:
    """One key component as text, with absence written as a value rather than left out."""
    return "\x00" if value is None else f"{type(value).__name__}:{value}"


def ingest(bundle: Mapping[str, Any], connection: sqlite3.Connection) -> dict[str, int]:
    """Build the schema and load every array into its table. Foreign keys are enforced.

    **Deferred, not disabled.** `faction.parent_faction_id` is self-referencing and
    `curated-snapshot-format.md` requires arrays sorted by id for determinism, so a chapter whose
    id sorts before its parent's is the normal case rather than a malformed bundle. A per-row
    check fails on it; `PRAGMA defer_foreign_keys` moves every check to `COMMIT`, where the whole
    table is present. Nothing is relaxed — a genuinely dangling reference still fails the commit,
    and `PRAGMA foreign_key_check` below re-reads the loaded database independently.
    """
    connection.executescript(SCHEMA)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA defer_foreign_keys = ON")

    meta = bundle["snapshotMeta"]
    connection.execute(
        "INSERT INTO snapshot_meta VALUES (?,?,?,?,?)",
        (
            meta["schemaContractVersion"],
            meta["restrictionVocabularyVersion"],
            meta["rulesVersionId"],
            meta["publishedAt"],
            meta["sourceNote"],
        ),
    )

    counts: dict[str, int] = {}
    for array, (table, columns) in TABLES.items():
        rows = _first_row_per_key(array, bundle[array])
        placeholders = ",".join("?" * len(columns))
        connection.executemany(
            f"INSERT INTO {table} ({','.join(_snake(c) for c in columns)}) VALUES ({placeholders})",
            [tuple(row.get(column) for column in columns) for row in rows],
        )
        counts[table] = len(rows)
    connection.commit()
    return counts


def _first_row_per_key(array: str, rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """Drop rows whose primary key has already been seen, keeping the first.

    Not a repair, and not a silent one: :func:`duplicate_keys` has already reported every key
    this drops, with its counts. Dropping here is what lets the *rest* of the check still say
    something — the guarantees and the pricing exercise run and produce answers instead of the
    whole run ending on the first `IntegrityError`. Constraint enforcement itself is untouched:
    no `OR IGNORE`, no relaxed pragma, so a NOT NULL or foreign-key breach still fails the load.
    """
    primary = PRIMARY_KEYS.get(array)
    if primary is None:  # pragma: no cover - TABLES and PRIMARY_KEYS are written together
        return list(rows)

    seen: dict[tuple[str, ...], Mapping[str, Any]] = {}
    for row in rows:
        seen.setdefault(tuple(_key_part(row.get(column)) for column in primary), row)
    return list(seen.values())


def check_guarantees(connection: sqlite3.Connection) -> list[str]:
    """The §1 guarantees, enforced at ingestion time exactly as the app must enforce them."""
    violations: list[str] = []
    cursor = connection.cursor()

    for row in cursor.execute("PRAGMA foreign_key_check").fetchall():
        violations.append(f"guarantee 4: foreign key violation in {row[0]}")

    orphans = cursor.execute(
        "SELECT d.id FROM datasheet d LEFT JOIN datasheet_cost c ON c.datasheet_id = d.id "
        "WHERE c.datasheet_id IS NULL"
    ).fetchall()
    violations.extend(f"guarantee 3: {row[0]} has no datasheet_cost row" for row in orphans)

    mismatched = cursor.execute(
        "SELECT c.datasheet_id, c.model_count FROM datasheet_cost c "
        "LEFT JOIN datasheet_cost_tier t ON t.datasheet_id = c.datasheet_id "
        "AND t.model_count = c.model_count AND t.copy_index_min = 1 "
        "AND t.points = c.points AND t.label = c.label "
        "WHERE t.datasheet_id IS NULL"
    ).fetchall()
    violations.extend(
        f"guarantee 7: {row[0]}/{row[1]} is not the first-copy projection" for row in mismatched
    )

    bands = cursor.execute(
        "SELECT min_points, max_points FROM game_size_rule ORDER BY min_points"
    ).fetchall()
    cursor_points = MIN_CUSTOM_POINT_LIMIT
    for low, high in bands:
        if low != cursor_points:
            violations.append(f"guarantee 3: bands are not contiguous at {cursor_points}")
        cursor_points = high + 1
    if cursor_points != MAX_CUSTOM_POINT_LIMIT + 1:
        violations.append(
            f"guarantee 3: bands stop at {cursor_points - 1}, not {MAX_CUSTOM_POINT_LIMIT}"
        )

    empty = cursor.execute(
        "SELECT COUNT(*) FROM datasheet_ability WHERE TRIM(summary) = ''"
    ).fetchone()[0]
    if empty:
        violations.append(f"guarantee 5: {empty} ability row(s) carry an empty summary")

    return violations


def price_unit(
    connection: sqlite3.Connection, datasheet_id: str, *, models: int, copy_index: int
) -> int:
    """Price one entry, applying §3.2's round-up and §3.1's copy-index lookup.

    A unit of *n* models pays the smallest listed `model_count` >= *n*, and the price is the row
    with the greatest `copy_index_min` that is <= this copy's index. A `copy_index_min = 1` row
    always exists, so the lookup can never miss.
    """
    band = connection.execute(
        "SELECT MIN(model_count) FROM datasheet_cost WHERE datasheet_id = ? AND model_count >= ?",
        (datasheet_id, models),
    ).fetchone()[0]
    if band is None:
        raise LookupError(f"{datasheet_id} lists no band that can hold {models} models")

    return int(
        connection.execute(
            "SELECT points FROM datasheet_cost_tier WHERE datasheet_id = ? AND model_count = ? "
            "AND copy_index_min <= ? ORDER BY copy_index_min DESC LIMIT 1",
            (datasheet_id, band, copy_index),
        ).fetchone()[0]
    )


def price_army(
    connection: sqlite3.Connection, army: Sequence[Mapping[str, Any]]
) -> tuple[int, list[str]]:
    """Price a multi-detachment army and return the total plus a readable breakdown."""
    total = 0
    lines: list[str] = []
    seen: dict[str, int] = {}

    for entry in army:
        kind = entry["kind"]
        if kind == "detachment":
            name, dp = connection.execute(
                "SELECT name, detachment_points_cost FROM detachment WHERE id = ?",
                (entry["id"],),
            ).fetchone()
            lines.append(f"detachment {name} ({dp}DP)")
            continue
        if kind == "enhancement":
            name, points = connection.execute(
                "SELECT name, points FROM enhancement WHERE id = ?", (entry["id"],)
            ).fetchone()
            total += points
            lines.append(f"  enhancement {name}: {points}")
            continue
        if kind == "wargear":
            name, delta = connection.execute(
                "SELECT name, points_delta FROM datasheet_wargear_option WHERE id = ?",
                (entry["id"],),
            ).fetchone()
            total += delta
            lines.append(f"    wargear {name}: {delta:+d}")
            continue

        copy_index = seen.get(entry["id"], 0) + 1
        seen[entry["id"]] = copy_index
        points = price_unit(connection, entry["id"], models=entry["models"], copy_index=copy_index)
        total += points
        name = connection.execute(
            "SELECT name FROM datasheet WHERE id = ?", (entry["id"],)
        ).fetchone()[0]
        lines.append(f"  {name} x{entry['models']} (copy {copy_index}): {points}")

    return total, lines


#: The exercise army. Every v1.2.0 addition in one list: two detachments, an escalating unit past
#: its threshold, a squad size that is not a listed band, a cost-bearing wargear option, and an
#: enhancement from each detachment.
EXERCISE_ARMY: Final[tuple[dict[str, Any], ...]] = (
    {"kind": "detachment", "id": "d-ashen-vanguard"},
    {"kind": "datasheet", "id": "ds-ashen-warden", "models": 3},
    {"kind": "datasheet", "id": "ds-ashen-warden", "models": 3},
    {"kind": "datasheet", "id": "ds-ashen-warden", "models": 3},
    {"kind": "enhancement", "id": "e-cinderbrand"},
    {"kind": "detachment", "id": "d-cinder-host"},
    {"kind": "datasheet", "id": "ds-ashen-sentinel", "models": 6},
    {"kind": "wargear", "id": "wo-ashen-sentinel-sentinel-banner"},
    {"kind": "datasheet", "id": "ds-lord-ashen", "models": 1},
    {"kind": "enhancement", "id": "e-emberward"},
)


def army_is_present(connection: sqlite3.Connection, army: Sequence[Mapping[str, Any]]) -> bool:
    """Does this bundle contain every entity the exercise army names?

    :data:`EXERCISE_ARMY` is written against the minimal fixture, whose ids are invented. Run
    against a real bundle it names nothing, and pricing it would report "pricing failed" — a
    violation that says the *army* is wrong, next to violations that say the *bundle* is. Two
    unlike things under one word is how a real defect gets read as the known noise, so the
    absence is detected first and reported as a skip.
    """
    tables: Final[Mapping[str, str]] = {
        "detachment": "detachment",
        "enhancement": "enhancement",
        "wargear": "datasheet_wargear_option",
    }
    for entry in army:
        table = tables.get(str(entry["kind"]), "datasheet")
        found = connection.execute(
            f"SELECT 1 FROM {table} WHERE id = ?",  # noqa: S608 - table comes from the map above
            (entry["id"],),
        ).fetchone()
        if found is None:
            return False
    return True


def run(bundle_path: Path, army: Sequence[Mapping[str, Any]] = EXERCISE_ARMY) -> CompatResult:
    """Ingest ``bundle_path`` and price ``army`` from the result."""
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    result = CompatResult()

    with sqlite3.connect(":memory:") as connection:
        duplicates = duplicate_keys(bundle)
        result.tables = ingest(bundle, connection)
        result.violations = [*duplicates, *check_guarantees(connection)]
        if not army_is_present(connection, army):
            result.army_lines = [
                "pricing exercise skipped: this bundle does not carry the exercise army's "
                "entities, which is expected for any bundle but the minimal fixture"
            ]
        else:
            try:
                result.army_total, result.army_lines = price_army(connection, army)
            except (LookupError, TypeError) as exc:
                result.violations.append(f"pricing failed: {type(exc).__name__}: {exc}")

    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args(argv)

    result = run(args.bundle)
    for line in result.army_lines:
        print(line)
    print(f"total {result.army_total} points")
    for violation in result.violations:
        print(f"VIOLATION {violation}", file=sys.stderr)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
