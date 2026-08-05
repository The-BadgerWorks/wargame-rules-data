# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the curated-tree writer (task
# T065): edition.json, game-sizes.json, factions.json and per faction detachments.json,
# enhancements.json and datasheets/<id>.json, written through the canonical serialiser with
# sorted keys and sorted arrays (FR-016, research D3, curated-snapshot-format.md §1-§2).
# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote 004-rules-data-enrichment's composition,
# option groups and choices, and wargear_option_state into the datasheet file (004 task T031), so
# the curated tree carries them and `curate/prior.py` can read them back as a baseline.
"""Write the curated tree — the artifact a human reviews.

The layout exists for **diff quality**, which FR-016 and FR-037 make a requirement rather than
a nicety. One datasheet per file means a points release produces a diff whose *file list alone*
names the changed datasheets; a single multi-megabyte document produces a diff nobody can
review, and an unreviewable diff is an unreviewed one.

Formatting is part of the contract for the same reason (§1). Sorted keys at every depth, arrays
sorted by their declared key, two-space indent, LF, one trailing newline, integers only, absent
optionals omitted rather than `null`. An unstable serialiser turns "three points changed" into
"every file changed", which destroys the property the layout was chosen for.

The writer **replaces** the edition's tree wholesale. That is deliberate: a retired datasheet
must leave, and a merge-in-place writer leaves its file behind forever. It is also safe, because
authored content lives in `curation/` and this module cannot write there (T064's guard).
"""

from __future__ import annotations

import shutil
from collections.abc import Mapping, Sequence
from pathlib import Path

from pipeline.build.canonical_json import JsonValue, omit_absent, write_tree_file
from pipeline.curate.authored import assert_not_authored
from pipeline.models.curated import (
    CuratedDatasheet,
    CuratedDatasheetCost,
    CuratedDetachment,
    CuratedDetachmentRestriction,
    CuratedEnhancement,
    CuratedFaction,
    CuratedSnapshot,
)
from pipeline.models.provenance import EntityProvenance, PricingConfidence


def _pricing_confidence(confidence: PricingConfidence) -> dict[str, JsonValue]:
    """The carry-forward bookkeeping, CURATED-ONLY.

    Written to the tree because the tree is the only durable record of it, and FR-035's
    "unverified since version X, for N consecutive releases" is meaningless if it resets every
    run. It also belongs in the *diff*: a unit falling back to last-known pricing is exactly the
    kind of change a reviewer should see happen, rather than discover in a report.
    """
    return omit_absent(
        {
            "state": confidence.state.value,
            "unverified_since_version": confidence.unverified_since_version,
            "consecutive_unverified_releases": confidence.consecutive_unverified_releases,
            "last_verified_version": confidence.last_verified_version,
            "last_verified_points_digest": confidence.last_verified_points_digest,
        }
    )


def _provenance(provenance: EntityProvenance) -> dict[str, JsonValue]:
    return omit_absent(
        {
            "points_source": provenance.points_source.value,
            "points_acquisition_id": provenance.points_acquisition_id,
            "points_edition_code": provenance.points_edition_code,
            "detail_source": provenance.detail_source.value,
            "detail_acquisition_id": provenance.detail_acquisition_id,
            "detail_edition_code": provenance.detail_edition_code,
            "is_hybrid_edition": provenance.is_hybrid_edition,
        }
    )


def _restriction(restriction: CuratedDetachmentRestriction) -> dict[str, JsonValue]:
    return omit_absent(
        {
            "id": restriction.id,
            "restriction_type": restriction.restriction_type,
            "params": dict(restriction.params),
            "message_template": restriction.message_template,
        }
    )


def _cost(cost: CuratedDatasheetCost) -> dict[str, JsonValue]:
    return omit_absent(
        {
            "model_count": cost.model_count,
            "copy_index_min": cost.copy_index_min,
            "points": cost.points,
            "label": cost.label,
            "pricing_confidence": cost.pricing_confidence.value,
            "source_acquisition_id": cost.source_acquisition_id,
        }
    )


def _faction(faction: CuratedFaction) -> dict[str, JsonValue]:
    return omit_absent(
        {
            "faction_id": faction.faction_id,
            "code": faction.code,
            "name": faction.name,
            "parent_faction_id": faction.parent_faction_id,
            "mfm_slug": faction.mfm_slug,
            "detail_source_faction_id": faction.detail_source_faction_id,
            "provenance": _provenance(faction.provenance),
        }
    )


def _detachment(detachment: CuratedDetachment) -> dict[str, JsonValue]:
    return omit_absent(
        {
            "detachment_id": detachment.detachment_id,
            "name": detachment.name,
            "detachment_points_cost": detachment.detachment_points_cost,
            "is_legends": detachment.is_legends,
            "force_disposition": detachment.force_disposition,
            "is_unique": detachment.is_unique,
            "restrictions": [
                _restriction(r) for r in sorted(detachment.restrictions, key=lambda r: r.id)
            ]
            or None,
            "provenance": _provenance(detachment.provenance),
        }
    )


def _enhancement(enhancement: CuratedEnhancement) -> dict[str, JsonValue]:
    return omit_absent(
        {
            "enhancement_id": enhancement.enhancement_id,
            "detachment_id": enhancement.detachment_id,
            "name": enhancement.name,
            "points": enhancement.points,
            "max_per_army": enhancement.max_per_army,
            "eligibility": [
                {"rule_type": e.rule_type, "value": e.value}
                for e in sorted(enhancement.eligibility, key=lambda e: (e.rule_type, e.value))
            ]
            or None,
            "provenance": _provenance(enhancement.provenance),
        }
    )


def _datasheet(datasheet: CuratedDatasheet) -> dict[str, JsonValue]:
    return omit_absent(
        {
            "datasheet_id": datasheet.datasheet_id,
            "faction_id": datasheet.faction_id,
            "name": datasheet.name,
            "role": datasheet.role,
            "is_legends": datasheet.is_legends,
            "is_character": datasheet.is_character,
            "is_epic_hero": datasheet.is_epic_hero,
            "is_battleline": datasheet.is_battleline,
            "is_dedicated_transport": datasheet.is_dedicated_transport,
            "max_copies_per_army": datasheet.max_copies_per_army,
            "damaged_threshold": datasheet.damaged_threshold,
            "models": [
                omit_absent(
                    {
                        "line": m.line,
                        "name": m.name,
                        "movement": m.movement,
                        "toughness": m.toughness,
                        "save": m.save,
                        "invuln_save": m.invuln_save,
                        "wounds": m.wounds,
                        "leadership": m.leadership,
                        "objective_control": m.objective_control,
                        "base_size": m.base_size,
                    }
                )
                for m in sorted(datasheet.models, key=lambda m: m.line)
            ]
            or None,
            "weapons": [
                omit_absent(
                    {
                        "line": w.line,
                        "name": w.name,
                        "is_melee": w.is_melee,
                        "range": w.range,
                        "attacks": w.attacks,
                        "skill": w.skill,
                        "strength": w.strength,
                        "armour_penetration": w.armour_penetration,
                        "damage": w.damage,
                        "ability_keywords": sorted(w.ability_keywords) or None,
                    }
                )
                for w in sorted(datasheet.weapons, key=lambda w: w.line)
            ]
            or None,
            "keywords": [
                omit_absent(
                    {
                        "keyword": k.keyword,
                        "is_faction_keyword": k.is_faction_keyword,
                        "model_scope": k.model_scope,
                    }
                )
                for k in sorted(datasheet.keywords, key=lambda k: (k.keyword, k.model_scope or ""))
            ]
            or None,
            # 004-rules-data-enrichment. Composition is written whole or not at all — an empty
            # sequence means the datasheet publishes *without* composition (FR-008), and writing
            # `[]` would say the same thing less clearly than omitting the key.
            "composition": [
                omit_absent(
                    {
                        "line": entry.line,
                        "model_name": entry.model_name,
                        "min_count": entry.min_count,
                        "max_count": entry.max_count,
                        "model_line": entry.model_line,
                    }
                )
                for entry in sorted(datasheet.composition, key=lambda entry: entry.line)
            ]
            or None,
            "option_groups": [
                omit_absent(
                    {
                        "id": group.id,
                        "line": group.line,
                        "scope": group.scope.value,
                        "scope_n": group.scope_n,
                        "parent_group_id": group.parent_group_id,
                        "default_choice_id": group.default_choice_id,
                        "min_choices": group.min_choices,
                        "max_choices": group.max_choices,
                    }
                )
                for group in sorted(datasheet.option_groups, key=lambda group: group.id)
            ]
            or None,
            "option_choices": [
                omit_absent(
                    {
                        "id": choice.id,
                        "group_id": choice.group_id,
                        "name": choice.name,
                        "count": choice.count,
                        "grants_weapon_line": choice.grants_weapon_line,
                        "replaces_weapon_line": choice.replaces_weapon_line,
                        "is_default": choice.is_default,
                        "is_no_change": choice.is_no_change,
                        "points_delta": choice.points_delta,
                        "priced_option_id": choice.priced_option_id,
                    }
                )
                for choice in sorted(datasheet.option_choices, key=lambda choice: choice.id)
            ]
            or None,
            "wargear_option_state": (
                datasheet.wargear_option_state.value
                if datasheet.wargear_option_state is not None
                else None
            ),
            "ability_keys": sorted(datasheet.ability_keys) or None,
            "leader_pairs": sorted(datasheet.leader_pairs) or None,
            "wargear_options": [
                omit_absent(
                    {
                        "id": o.id,
                        "group_key": o.group_key,
                        "name": o.name,
                        "points_delta": o.points_delta,
                        "max_per_unit": o.max_per_unit,
                        "models_per_instance": o.models_per_instance,
                    }
                )
                for o in sorted(datasheet.wargear_options, key=lambda o: o.id)
            ]
            or None,
            "costs": [
                _cost(c)
                for c in sorted(datasheet.costs, key=lambda c: (c.copy_index_min, c.model_count))
            ],
            "pricing_confidence": _pricing_confidence(datasheet.pricing_confidence),
            "provenance": _provenance(datasheet.provenance),
        }
    )


def _group_by_faction(
    snapshot: CuratedSnapshot,
) -> tuple[
    Mapping[str, list[CuratedDetachment]],
    Mapping[str, list[CuratedEnhancement]],
    Mapping[str, list[CuratedDatasheet]],
]:
    detachments: dict[str, list[CuratedDetachment]] = {}
    for detachment in snapshot.detachments:
        detachments.setdefault(detachment.faction_id, []).append(detachment)

    detachment_faction = {d.detachment_id: d.faction_id for d in snapshot.detachments}
    enhancements: dict[str, list[CuratedEnhancement]] = {}
    for enhancement in snapshot.enhancements:
        faction_id = detachment_faction.get(enhancement.detachment_id, "")
        enhancements.setdefault(faction_id, []).append(enhancement)

    datasheets: dict[str, list[CuratedDatasheet]] = {}
    for datasheet in snapshot.datasheets:
        datasheets.setdefault(datasheet.faction_id, []).append(datasheet)

    return detachments, enhancements, datasheets


def write_tree(snapshot: CuratedSnapshot, *, data_dir: Path, curation_dir: Path) -> list[Path]:
    """Write the whole curated tree for one edition and return the files written.

    Args:
        data_dir: the edition's directory, e.g. ``data/wh40k-11e``. Replaced wholesale.
        curation_dir: the authored tree, passed only so every write can be checked against it.
    """
    assert_not_authored(data_dir, curation_dir)
    if data_dir.exists():
        shutil.rmtree(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []

    def _write(path: Path, payload: JsonValue) -> None:
        assert_not_authored(path, curation_dir)
        write_tree_file(path, payload)
        written.append(path)

    _write(
        data_dir / "edition.json",
        {
            "edition": {
                "id": snapshot.edition.id,
                "code": snapshot.edition.code,
                "name": snapshot.edition.name,
                "display_order": snapshot.edition.display_order,
            },
            "edition_rules": [
                {"rule_key": rule.rule_key, "value": rule.value}
                for rule in sorted(snapshot.edition_rules, key=lambda r: r.rule_key)
            ],
        },
    )

    _write(
        data_dir / "game-sizes.json",
        [
            {
                "id": band.id,
                "label": band.label,
                "min_points": band.min_points,
                "max_points": band.max_points,
                "detachment_points_budget": band.detachment_points_budget,
                "max_detachments": band.max_detachments,
                "max_enhancements": band.max_enhancements,
            }
            for band in sorted(snapshot.game_sizes, key=lambda b: b.min_points)
        ],
    )

    _write(
        data_dir / "factions.json",
        [_faction(f) for f in sorted(snapshot.factions, key=lambda f: f.faction_id)],
    )

    by_detachment, by_enhancement, by_datasheet = _group_by_faction(snapshot)

    for faction in sorted(snapshot.factions, key=lambda f: f.faction_id):
        faction_dir = data_dir / "factions" / faction.faction_id
        faction_dir.mkdir(parents=True, exist_ok=True)

        _write(
            faction_dir / "detachments.json",
            {
                "detachments": [
                    _detachment(d)
                    for d in sorted(
                        by_detachment.get(faction.faction_id, []),
                        key=lambda d: d.detachment_id,
                    )
                ]
            },
        )
        _write(
            faction_dir / "enhancements.json",
            {
                "enhancements": [
                    _enhancement(e)
                    for e in sorted(
                        by_enhancement.get(faction.faction_id, []),
                        key=lambda e: e.enhancement_id,
                    )
                ]
            },
        )

        datasheet_dir = faction_dir / "datasheets"
        datasheet_dir.mkdir(parents=True, exist_ok=True)
        for datasheet in sorted(
            by_datasheet.get(faction.faction_id, []), key=lambda d: d.datasheet_id
        ):
            _write(datasheet_dir / f"{datasheet.datasheet_id}.json", _datasheet(datasheet))

    return written


def tree_json(snapshot: CuratedSnapshot) -> Sequence[tuple[str, JsonValue]]:
    """The tree as ``(relative path, payload)`` pairs, without touching the filesystem.

    Used by tests and by a dry run, so "what would this write" is answerable without writing it.
    """
    pairs: list[tuple[str, JsonValue]] = []
    by_detachment, by_enhancement, by_datasheet = _group_by_faction(snapshot)
    for faction in sorted(snapshot.factions, key=lambda f: f.faction_id):
        base = f"factions/{faction.faction_id}"
        pairs.append(
            (
                f"{base}/detachments.json",
                {
                    "detachments": [
                        _detachment(d)
                        for d in sorted(
                            by_detachment.get(faction.faction_id, []),
                            key=lambda d: d.detachment_id,
                        )
                    ]
                },
            )
        )
        pairs.append(
            (
                f"{base}/enhancements.json",
                {
                    "enhancements": [
                        _enhancement(e)
                        for e in sorted(
                            by_enhancement.get(faction.faction_id, []),
                            key=lambda e: e.enhancement_id,
                        )
                    ]
                },
            )
        )
        for datasheet in sorted(
            by_datasheet.get(faction.faction_id, []), key=lambda d: d.datasheet_id
        ):
            pairs.append(
                (f"{base}/datasheets/{datasheet.datasheet_id}.json", _datasheet(datasheet))
            )
    return pairs
