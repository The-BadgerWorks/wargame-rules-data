# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R9 task 5: wrote this suite red, before
# `used_keyword_keys` excluded unit names, against the Owner's ruling of 2026-09-15 that a keyword
# equal to a datasheet or model name is not a glossary candidate. It pins the exclusion, the
# boundary it must NOT cross (a keyword that merely CONTAINS a unit name stays in), the flow
# through to `glossary_keys`, the wiring through `run_build`, and the advisory that keeps the
# shrink visible.
"""A keyword that names a unit is not a glossary candidate.

The denominator this touches is `GLS-OUTSTANDING`'s. Round 8 measured it at 1264 keys, of which
1030 were datasheet or model names and none had source text anywhere in the export — so the
outstanding figure was measuring work no curator could ever do. The exclusion here is the same
argument `used_keyword_keys` already makes for faction and chapter keywords: a label for *which
model this is* is not a mechanic anyone could define.

The dangerous half is over-exclusion. A denominator that shrinks further than the ruling
authorised reads green for the same reason an empty roster does, so every boundary below is
asserted in the positive direction too: the keyword that is merely *near* a unit name stays in.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from pipeline.cli import run_build
from pipeline.config import load_config
from pipeline.models.curated import CuratedKeyword, CuratedModelLine, KeywordClass
from pipeline.validate.gates import (
    check_unit_name_exclusions,
    glossary_keys,
    used_keyword_keys,
)
from tests import factories


def _keyword(keyword: str, *, keyword_class: KeywordClass | None = KeywordClass.UNIT):
    return CuratedKeyword(keyword=keyword, keyword_class=keyword_class)


def _model(name: str) -> CuratedModelLine:
    return CuratedModelLine(
        line=1,
        name=name,
        movement='6"',
        toughness=4,
        save="4+",
        wounds=2,
        leadership="6+",
        objective_control=1,
    )


def _datasheet(  # type: ignore[no-untyped-def]
    datasheet_id: str,
    *,
    name: str,
    faction_id: str = "f-glimmerfen-covenant",
    keywords=(),
    models=None,
):
    return factories.datasheet(datasheet_id, faction_id=faction_id).model_copy(
        update={
            "name": name,
            "keywords": list(keywords),
            "models": list(models if models is not None else [_model(name)]),
        }
    )


def test_a_keyword_equal_to_a_datasheet_name_leaves_the_denominator() -> None:
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                name="Fen Warden",
                keywords=[_keyword("Fen Warden"), _keyword("Infantry")],
            )
        ]
    )

    assert used_keyword_keys(snapshot) == ("infantry",)
    assert glossary_keys(snapshot) == ("glossary:infantry",)


def test_a_keyword_equal_to_a_model_line_name_leaves_the_denominator() -> None:
    """The model line carries the name the keyword repeats; the datasheet is named otherwise."""
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-brackrider-column",
                name="Brackrider Column",
                keywords=[_keyword("Fen Warden"), _keyword("Infantry")],
                models=[_model("Fen Warden")],
            )
        ]
    )

    assert used_keyword_keys(snapshot) == ("infantry",)


def test_casing_and_punctuation_variants_of_a_unit_name_are_excluded_too() -> None:
    """Both sides resolve through `keyword_key`, so the printed form cannot smuggle one back."""
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                name="Fen Warden",
                keywords=[_keyword("FEN-WARDEN"), _keyword("Infantry")],
            )
        ]
    )

    assert used_keyword_keys(snapshot) == ("infantry",)


def test_a_keyword_that_merely_contains_a_unit_name_stays_in_the_denominator() -> None:
    """The boundary. Equality excludes; containment is a different keyword and stays."""
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                name="Fen Warden",
                keywords=[_keyword("Fen Warden Bond"), _keyword("Warden")],
            )
        ]
    )

    assert used_keyword_keys(snapshot) == ("fen warden bond", "warden")


def test_the_exclusion_is_snapshot_wide_not_per_faction() -> None:
    """One key serves every faction, so the exclusion cannot be scoped narrower than the key."""
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                name="Fen Warden",
                faction_id="f-glimmerfen-covenant",
                keywords=[_keyword("Infantry")],
            ),
            _datasheet(
                "ds-brackrider-column",
                name="Brackrider Column",
                faction_id="f-bracklight-host",
                keywords=[_keyword("Fen Warden"), _keyword("Infantry")],
            ),
        ]
    )

    assert used_keyword_keys(snapshot) == ("infantry",)


def test_a_weapon_ability_keyword_equal_to_a_unit_name_is_excluded_as_well() -> None:
    """The enumeration excludes by key, wherever the key was printed."""
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                name="Fen Warden",
                keywords=[_keyword("Infantry")],
                models=[_model("Fen Warden")],
            )
        ]
    )
    datasheet = snapshot.datasheets[0]
    weapon = datasheet.weapons[0].model_copy(update={"ability_keywords": ["FEN WARDEN"]})
    snapshot = factories.snapshot(datasheets=[datasheet.model_copy(update={"weapons": [weapon]})])

    assert used_keyword_keys(snapshot) == ("infantry",)


def test_a_faction_keyword_that_names_no_unit_is_still_excluded_for_its_own_reason() -> None:
    """The pre-existing exclusion is untouched; this one is additive."""
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                name="Fen Warden",
                keywords=[
                    _keyword("GLIMMERFEN COVENANT", keyword_class=KeywordClass.FACTION),
                    _keyword("Tidewalk"),
                ],
            )
        ]
    )

    assert used_keyword_keys(snapshot) == ("tidewalk",)


# --- the advisory that keeps the shrink visible --------------------------------------------------


def test_the_advisory_carries_the_count_of_keys_the_exclusion_removed() -> None:
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                name="Fen Warden",
                keywords=[_keyword("Fen Warden"), _keyword("Infantry")],
                models=[_model("Duskrail Outrider")],
            ),
            _datasheet(
                "ds-brackrider-column",
                name="Brackrider Column",
                faction_id="f-bracklight-host",
                keywords=[_keyword("Duskrail Outrider"), _keyword("Tidewalk")],
            ),
        ]
    )

    findings = check_unit_name_exclusions(snapshot)

    assert [finding.finding_code for finding in findings] == ["GLS-UNIT-NAME-EXCLUDED"]
    assert findings[0].detail["excluded_keys"] == 2
    assert findings[0].detail["candidate_keys"] == 2


def test_the_advisory_is_silent_when_no_keyword_names_a_unit() -> None:
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                name="Fen Warden",
                keywords=[_keyword("Tidewalk"), _keyword("Infantry")],
                models=[_model("Duskrail Outrider")],
            )
        ]
    )

    assert check_unit_name_exclusions(snapshot) == []


# --- the wiring: a run has to actually apply it and actually report it ---------------------------


def test_a_build_applies_the_exclusion_and_raises_the_advisory(tmp_path, temp_repo) -> None:  # type: ignore[no-untyped-def]
    """The wiring, not the rule.

    Built on a throwaway copy of ``fixtures/disagreements`` with one extra keyword row — a
    keyword printed with the same name as its own datasheet, which is the shape the exclusion
    exists for. The copy is deliberate: the tracked fixture is shared with the coverage-collapse
    and publication-refusal suites, and changing what they build would make this test's evidence
    about those suites rather than about this wiring.
    """
    source = Path(__file__).resolve().parents[2] / "fixtures" / "disagreements"
    fixtures = tmp_path / "fixtures"
    shutil.copytree(source, fixtures)
    keywords = fixtures / "wahapedia" / "Datasheets_keywords.csv"
    keywords.write_text(
        keywords.read_text(encoding="utf-8") + "SG01|SLATE SENTINEL||false|\n", encoding="utf-8"
    )

    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-unit-name-keyword",
        fixtures_dir=fixtures,
        offline=True,
        output_root=tmp_path / "out",
        repository_root=temp_repo(),
    )

    advisories = [f for f in result.findings if f.finding_code == "GLS-UNIT-NAME-EXCLUDED"]
    assert [f.severity for f in advisories] == ["advisory"]
    assert advisories[0].detail["excluded_keys"] == 1
    outstanding = [f for f in result.findings if f.finding_code == "GLS-OUTSTANDING"]
    assert "glossary:slate sentinel" not in {
        ref for finding in outstanding for ref in finding.entity_refs
    }
