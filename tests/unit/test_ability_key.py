# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 R6b Task 1, failing-first: the single
# `ability_key` helper (pipeline/normalize/ability_key.py) that joins a binding's `parameter`
# column into the name before slugifying, reproducing the published tree's `core:feel-no-pain-5`
# style keys instead of the CSV arm's bare `core:feel-no-pain`. Also the agreement receipt: the
# two call sites that mint a key (assemble.py, summaries.py) must never diverge, because a key
# and its digest are minted separately. Invented names throughout (Tide Ward, Fen Pike).
"""``ability_key`` joins a binding's parameter into its name before slugifying.

The published tree's `core:` keys carry the ability's parameter (`core:feel-no-pain-5`); the CSV
export states it in `Datasheets_abilities.csv`'s own `parameter` column, separate from `name`.
This is the one function that may build an ability key — both call sites delegate to it so a key
and its digest can never be minted by two different rules.

The trailing-parenthetical strip that round 7's Task 1a proposed is deliberately **not** done
here: measured against the live export and the published tree, it moves 257 further published
`datasheet:` keys and 4 `faction:` keys that this task's parameter-join alone does not move — a
Tier 1 identifier move this task refuses to cause. See task-1-brief.md for the measurement.
"""

from __future__ import annotations

from collections.abc import Mapping

from pipeline.curate.assemble import _detail_datasheet_fields
from pipeline.curate.summaries import ability_name_index, compute_current_digests
from pipeline.models.normalized import AbilityType
from pipeline.normalize.ability_key import ability_key
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text

# -- ability_key unit tests -----------------------------------------------------------------


def test_parameter_is_joined_before_slugifying() -> None:
    assert ability_key(AbilityType.CORE, "Tide Ward", parameter="D3") == "core:tide-ward-d3"


def test_a_plus_suffixed_parameter_slugifies_with_the_plus_dropped() -> None:
    assert ability_key(AbilityType.CORE, "Tide Ward", parameter="5+") == "core:tide-ward-5"


def test_an_inches_suffixed_parameter_slugifies_with_the_mark_dropped() -> None:
    assert ability_key(AbilityType.CORE, "Tide Ward", parameter='6"') == "core:tide-ward-6"


def test_an_empty_parameter_leaves_the_key_bare() -> None:
    assert ability_key(AbilityType.CORE, "Tide Ward", parameter="") == "core:tide-ward"


def test_a_whitespace_only_parameter_leaves_the_key_bare() -> None:
    assert ability_key(AbilityType.CORE, "Tide Ward", parameter="  ") == "core:tide-ward"


def test_default_parameter_is_empty_and_leaves_the_key_bare() -> None:
    assert ability_key(AbilityType.CORE, "Tide Ward") == "core:tide-ward"


def test_a_trailing_parenthesised_group_is_preserved_not_stripped() -> None:
    """The parenthetical strip is refused (see module docstring) — a real published key carries
    the parenthetical tag, and stripping it would move published `datasheet:` and `faction:`
    identifiers this task must not touch."""
    assert (
        ability_key(AbilityType.DATASHEET, "Fen Pike (Once Per Battle)")
        == "datasheet:fen-pike-once-per-battle"
    )


def test_a_non_trailing_parenthesis_is_likewise_untouched() -> None:
    assert ability_key(AbilityType.DATASHEET, "Fen (Pike) Strike") == "datasheet:fen-pike-strike"


def test_the_prefix_is_the_ability_types_value_for_every_member() -> None:
    for member in AbilityType:
        assert ability_key(member, "Tide Ward").startswith(f"{member.value}:")


# -- agreement receipt: the two call sites must never diverge --------------------------------

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

_CORE_BINDING = f"ds1|1|A1|||{_INVENTED_DESCRIPTION}|Core|D3|\n"
_FACTION_BINDING = f"ds1|2|||Coral Ward|{_INVENTED_DESCRIPTION}|Faction||\n"
_DATASHEET_BINDING = f"ds1|3|||Fen Pike (Once Per Battle)|{_INVENTED_DESCRIPTION}|Datasheet||\n"

_ABILITY_A1 = f"A1|Tide Ward||TF|{_INVENTED_DESCRIPTION}|\n"


def _detail() -> dict[str, CsvReadResult]:
    bindings = _CORE_BINDING + _FACTION_BINDING + _DATASHEET_BINDING
    return {
        "Datasheets.csv": read_text("Datasheets.csv", _DATASHEETS_CSV),
        "Datasheets_wargear.csv": read_text("Datasheets_wargear.csv", _EMPTY_WARGEAR_CSV),
        "Datasheets_models.csv": read_text("Datasheets_models.csv", _EMPTY_MODELS_CSV),
        "Datasheets_keywords.csv": read_text("Datasheets_keywords.csv", _EMPTY_KEYWORDS_CSV),
        "Datasheets_abilities.csv": read_text(
            "Datasheets_abilities.csv", _BINDINGS_HEADER + bindings
        ),
        "Abilities.csv": read_text("Abilities.csv", _ABILITIES_HEADER + _ABILITY_A1),
    }


def test_summary_digest_keys_are_a_subset_of_assemble_ability_keys() -> None:
    """The two call sites mint a key and its digest separately — if they ever derive the key
    differently, a digest would be filed under a key `ability_keys` never lists, and the app
    would silently fail to resolve the mechanic for a published ability."""
    detail: Mapping[str, CsvReadResult] = _detail()

    fields, findings = _detail_datasheet_fields(
        "ds1", detail, frozenset(), ability_names=ability_name_index(detail)
    )
    assert [f.finding_code for f in findings] == []
    assembled_keys: set[str] = set(fields["ability_keys"])  # type: ignore[arg-type]

    digest_keys = set(compute_current_digests(detail, key=b"0" * 32).keys())

    assert digest_keys <= assembled_keys, (
        "a digest key is missing from ability_keys — the two call sites derive keys "
        f"differently: digest keys {sorted(digest_keys)}, assembled keys "
        f"{sorted(assembled_keys)}"
    )
    # Non-vacuous: both call sites actually produced keys for this fixture.
    assert assembled_keys == {
        "core:tide-ward-d3",
        "faction:coral-ward",
        "datasheet:fen-pike-once-per-battle",
    }
