# AI-Assisted: Claude Code (model: Claude Sonnet 5) - 010 R13 task 4 mapped `psychic` onto
# `AbilityType.DATASHEET`; task 13 withdrew that mapping. A live build showed it mints three new
# ability keys (Orks psychic powers) with no approved summaries, which the publish gate blocks
# with SUM-MISSING. Admitting those keys is a curation-and-drafting round of its own, not a
# pipeline change, so `psychic` is unmapped again and `Psychic` rows drop with `DQ-ABILITY-TYPE`,
# exactly as before task 4. `source_class` is unaffected and still reports `"psychic"`.
"""`abilityClass` is a new optional tag; the closed `AbilityType` vocabulary does not grow.

`tests/unit/test_models.py:149` is the Tier 1 guard that `AbilityType` stays exactly
`{core, faction, datasheet}` and is not touched here. What changes instead is `source_class`, a
new function that reports the *source's own* classification (`Wargear`, `Wargear profile`,
`Primarch`, `Psychic`) so the app can distinguish it later without moving a single published key.

The Psychic flip (010 R13 task 4: `psychic -> AbilityType.DATASHEET`) was withdrawn in task 13:
a live build showed it mints three new ability keys with no approved summaries, which the
publish gate blocks with `SUM-MISSING`.
`test_psychic_still_drops_with_dq_ability_type_while_source_class_reports_it` now records the
restored behaviour: a `Psychic` row is unmapped in `ABILITY_TYPE_MAP` and raises
`DQ-ABILITY-TYPE`, dropping the binding, while `source_class("Psychic")` still reports
`"psychic"` unchanged.
"""

from __future__ import annotations

from pipeline.build.bundle_emit import emit_bundle
from pipeline.curate.assemble import _detail_datasheet_fields
from pipeline.curate.summaries import ability_name_index
from pipeline.models.authored import AbilitySummary, ReviewState
from pipeline.models.normalized import AbilityType
from pipeline.normalize.ability_key import ability_key
from pipeline.normalize.ability_types import classify, source_class
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text
from tests import factories

# --- source_class -------------------------------------------------------------------------------


def test_source_class_wargear_profile_is_classed() -> None:
    assert source_class("Wargear profile") == "wargear-profile"


def test_source_class_wargear_is_classed() -> None:
    assert source_class("Wargear") == "wargear"


def test_source_class_primarch_is_classed() -> None:
    assert source_class("Primarch") == "primarch"


def test_source_class_psychic_is_classed() -> None:
    assert source_class("Psychic") == "psychic"


def test_source_class_datasheet_is_none() -> None:
    """`Datasheet` is a real classification, not a source-class tag — it carries no class."""
    assert source_class("Datasheet") is None


def test_source_class_core_is_none() -> None:
    assert source_class("Core") is None


def test_source_class_faction_is_none() -> None:
    assert source_class("Faction") is None


def test_source_class_is_none_for_a_cyrillic_scraper_artefact() -> None:
    """`research §0.1`'s layout artefacts are not a taxonomy member at all."""
    assert source_class("Special (правая колонка)") is None
    assert source_class("Fortification (левая колонка)") is None
    assert source_class("Без заголовка") is None


# --- the Psychic flip, withdrawn -------------------------------------------------------------


def test_psychic_still_drops_with_dq_ability_type_while_source_class_reports_it() -> None:
    """The task-4 flip is withdrawn: a `Psychic` row is dropped with `DQ-ABILITY-TYPE` again,
    because admitting it mints ability keys with no approved summaries (`SUM-MISSING` at
    publish). `source_class` is a separate, unaffected concern and still reports `"psychic"`."""
    ability_type, finding = classify("Psychic", entity_ref="wahapedia:x")

    assert ability_type is None
    assert finding is not None
    assert finding.finding_code == "DQ-ABILITY-TYPE"
    assert source_class("Psychic") == "psychic"


# --- receipt: no published identifier moved --------------------------------------------------


def test_classify_wargear_still_resolves_to_datasheet_type() -> None:
    """The published key's prefix IS `abilityType` — this pins that `Wargear` still maps to
    `datasheet:`, i.e. nothing about the existing mapping table changed, only the new tag."""
    ability_type, finding = classify("Wargear", entity_ref="x")

    assert ability_type is AbilityType.DATASHEET
    assert finding is None
    assert ability_key(AbilityType.DATASHEET, "Hover Limpet").startswith("datasheet:")


# --- assembly: ability_classes populated beside ability_keys ----------------------------------

_DATASHEETS_CSV = (
    "id|name|faction_id|source_id|legend|role|loadout|transport|virtual|leader_head|"
    "leader_footer|damaged_w|damaged_description|link|\n"
    "ds1|Test Unit|TF|1||Battleline|||0|||||https://example.invalid/ds/ds1|\n"
)
_EMPTY_MODELS_CSV = (
    "datasheet_id|line|name|M|T|Sv|inv_sv|inv_sv_descr|W|Ld|OC|base_size|base_size_descr|\n"
)
_EMPTY_KEYWORDS_CSV = "datasheet_id|keyword|model|is_faction_keyword|\n"
_EMPTY_WARGEAR_CSV = (
    "datasheet_id|line|line_in_wargear|dice|name|description|range|type|A|BS_WS|S|AP|D|\n"
)
_ABILITIES_HEADER = "id|name|legend|faction_id|description|\n"
_BINDINGS_HEADER = "datasheet_id|line|ability_id|model|name|description|type|parameter|\n"

#: Invented placeholder prose (research D10) — never the publisher's wording.
_INVENTED_DESCRIPTION = "Invented placeholder prose describing one mechanic, for this test only."

_WARGEAR_BINDING = f"ds1|1|A1||Hover Limpet|{_INVENTED_DESCRIPTION}|Wargear||\n"


def _detail(*, bindings: str, abilities: str = "") -> dict[str, CsvReadResult]:
    return {
        "Datasheets.csv": read_text("Datasheets.csv", _DATASHEETS_CSV),
        "Datasheets_wargear.csv": read_text("Datasheets_wargear.csv", _EMPTY_WARGEAR_CSV),
        "Datasheets_models.csv": read_text("Datasheets_models.csv", _EMPTY_MODELS_CSV),
        "Datasheets_keywords.csv": read_text("Datasheets_keywords.csv", _EMPTY_KEYWORDS_CSV),
        "Datasheets_abilities.csv": read_text(
            "Datasheets_abilities.csv", _BINDINGS_HEADER + bindings
        ),
        "Abilities.csv": read_text("Abilities.csv", _ABILITIES_HEADER + abilities),
    }


def test_a_wargear_typed_binding_populates_both_ability_keys_and_ability_classes() -> None:
    detail = _detail(bindings=_WARGEAR_BINDING)
    fields, findings = _detail_datasheet_fields(
        "ds1", detail, frozenset(), ability_names=ability_name_index(detail)
    )

    assert [finding.finding_code for finding in findings] == []
    assert fields["ability_keys"] == ["datasheet:hover-limpet"]
    assert fields["ability_classes"] == {"datasheet:hover-limpet": "wargear"}


def test_a_core_typed_binding_gets_no_ability_class() -> None:
    """A `core:` key never carries a class — the raw source value maps to no `source_class`."""
    core_binding = f"ds1|1|A1||Harbour Watch|{_INVENTED_DESCRIPTION}|Core||\n"
    detail = _detail(bindings=core_binding)
    fields, _findings = _detail_datasheet_fields(
        "ds1", detail, frozenset(), ability_names=ability_name_index(detail)
    )

    assert fields["ability_keys"] == ["core:harbour-watch"]
    assert fields["ability_classes"] == {}


# --- emitter: abilityClass through omit_absent -------------------------------------------------


def _summary(key: str) -> AbilitySummary:
    return AbilitySummary(
        ability_key=key,
        name=key.split(":")[-1].replace("-", " ").title(),
        summary="Invented mechanics-only summary authored for this data set.",
        review_state=ReviewState.APPROVED,
        mechanic_digest="0" * 32,
        reviewed_by="curator",
        reviewed_at="2026-06-13T00:00:00Z",
    )


def test_emitter_sets_ability_class_only_on_the_classed_row() -> None:
    classed_key = "datasheet:hover-limpet"
    unclassed_key = "core:deep-strike"
    sheet = factories.datasheet("ds-classed", ability_keys=(classed_key, unclassed_key)).model_copy(
        update={"ability_classes": {classed_key: "wargear"}}
    )
    snapshot = factories.snapshot(
        datasheets=[sheet],
        ability_summaries={
            classed_key: _summary(classed_key),
            unclassed_key: _summary(unclassed_key),
        },
    )

    bundle = emit_bundle(snapshot, factories.meta())

    rows = {row["name"]: row for row in bundle["datasheetAbilities"]}
    classed_row = rows[_summary(classed_key).name]
    unclassed_row = rows[_summary(unclassed_key).name]

    assert classed_row["abilityClass"] == "wargear"
    assert "abilityClass" not in unclassed_row
