# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the end-to-end weapon-ability-keyword
# suite (issue #4), confirmed failing against the code that shipped 9,305 empty keyword lists:
# the keywords reach curated data, the bundle, and the glossary denominator, and an empty class
# now trips an advisory finding instead of shipping silently.
"""From the export's own column to the glossary denominator, in one run.

Issue #4 was not a parsing bug in the ordinary sense: nothing failed, nothing was reported, and
every value that *was* extracted was correct. A whole class of mechanical data — the one class
of keyword that is a mechanic by construction — simply never left the source, and the pipeline
had no figure that would have shown it. So this suite asserts two different things:

* the **flow**, end to end over a fixture set, because the defect lived in the joins between
  stages rather than in any one of them; and
* the **visibility**, because a fix that restores the class without measuring it leaves the next
  regression exactly as silent as this one was.

Every keyword below is invented. The fixture set is synthetic and so is its vocabulary.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.cli import run_build
from pipeline.config import load_config
from pipeline.exit_codes import ExitCode
from pipeline.models.curated import CuratedWeaponLine
from pipeline.models.findings import FindingClass, Severity
from pipeline.report.catalogue import CATALOGUE
from pipeline.report.validation import scale_figures
from pipeline.validate.coverage import check_weapon_ability_keywords
from pipeline.validate.gates import used_keyword_keys
from tests import factories

MINIMAL = Path(__file__).resolve().parents[2] / "fixtures" / "minimal"

#: What `fixtures/minimal/wahapedia/Datasheets_wargear.csv` states, per detail datasheet id.
EXPECTED: dict[str, tuple[str, ...]] = {
    "Ashen Sentinel blade": ("GLIMMERBURST",),
    "Ashen Warden blade": ("MARSHBIND 2", "GLIMMERBURST"),
    "Lord Ashen blade": ("FENLOCK 4+",),
    "Ashen Captain blade": ("Marshbind 1",),
}


@pytest.fixture(scope="module")
def build(tmp_path_factory: pytest.TempPathFactory):  # type: ignore[no-untyped-def]
    repository_root = tmp_path_factory.mktemp("keyword-repo")
    for relative in (
        "data/wh40k-11e/factions",
        "curation/abilities",
        "reports",
        "state",
        "site/prerelease",
        "work",
    ):
        (repository_root / relative).mkdir(parents=True, exist_ok=True)
    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-weapon-keywords",
        fixtures_dir=MINIMAL,
        offline=True,
        output_root=tmp_path_factory.mktemp("keyword-build"),
        repository_root=repository_root,
    )
    assert result.exit_code in (ExitCode.SUCCESS, ExitCode.ADVISORY_ONLY), [
        f.finding_code for f in result.findings if f.severity == "blocking"
    ]
    return result


# -- the flow ---------------------------------------------------------------------------------


def test_the_curated_weapon_lines_carry_the_keywords_the_source_states(build) -> None:  # type: ignore[no-untyped-def]
    found = {
        weapon.name: tuple(weapon.ability_keywords)
        for datasheet in build.snapshot.datasheets
        for weapon in datasheet.weapons
        if weapon.ability_keywords
    }

    assert found == EXPECTED


def test_a_weapon_the_source_states_no_keyword_for_carries_none(build) -> None:  # type: ignore[no-untyped-def]
    unstated = [
        weapon.name
        for datasheet in build.snapshot.datasheets
        for weapon in datasheet.weapons
        if not weapon.ability_keywords
    ]

    assert unstated and set(unstated).isdisjoint(EXPECTED)


def test_the_bundles_weapon_rows_carry_them_too(build) -> None:  # type: ignore[no-untyped-def]
    """FR-009's consumers render a weapon profile from this row and nothing else."""
    rows = {
        row["name"]: row.get("abilityKeywords")
        for row in build.bundle["datasheetWeapons"]  # type: ignore[index]
    }

    assert rows["Ashen Warden blade"] == "MARSHBIND 2,GLIMMERBURST"
    assert rows["Ashen Relic Walker blade"] is None


def test_the_keywords_reach_the_glossary_denominator(build) -> None:  # type: ignore[no-untyped-def]
    """The denominator already walked weapon ability keywords; there were none to walk."""
    keys = used_keyword_keys(build.snapshot)

    assert {"glimmerburst", "marshbind", "fenlock"} <= set(keys)


def test_one_entry_serves_every_parameter_variant_of_a_weapon_keyword(build) -> None:  # type: ignore[no-untyped-def]
    """``MARSHBIND 2`` and ``Marshbind 1`` are printed twice and counted once (FR-023)."""
    assert used_keyword_keys(build.snapshot).count("marshbind") == 1


# -- the visibility ----------------------------------------------------------------------------


def test_the_scale_block_states_how_many_weapon_lines_carry_a_keyword(build) -> None:  # type: ignore[no-untyped-def]
    figure = build.report.scale["weapon_ability_keywords"]
    weapon_lines = sum(len(d.weapons) for d in build.snapshot.datasheets)

    assert figure.count == len(EXPECTED)
    assert figure.proportion == pytest.approx(len(EXPECTED) / weapon_lines, abs=1e-4)


def test_the_figure_is_stated_against_weapon_lines_not_datasheets() -> None:
    """Dividing a weapon count by a datasheet count would produce a number that means nothing."""
    one = factories.datasheet("ds-one", faction_id="f-ember")
    two = factories.datasheet("ds-two", faction_id="f-ember").model_copy(
        update={
            "weapons": [
                _weapon(1, "Ember lance", ("GLIMMERBURST",)),
                _weapon(2, "Ember maul", ()),
            ]
        }
    )
    snapshot = factories.snapshot(datasheets=[one, two])

    figure = scale_figures(snapshot, [])["weapon_ability_keywords"]

    assert (figure.count, figure.proportion) == (1, pytest.approx(1 / 3, abs=1e-4))


def test_an_empty_weapon_keyword_class_trips_an_advisory_finding() -> None:
    """The regression this issue was: every value correct, the whole class absent, nothing said."""
    findings = check_weapon_ability_keywords(factories.snapshot())

    assert [(f.finding_code, f.severity) for f in findings] == [
        ("COV-WEAPON-ABILITIES-EMPTY", "advisory")
    ]


def test_a_class_that_is_present_trips_nothing() -> None:
    carrying = factories.datasheet("ds-one", faction_id="f-ember").model_copy(
        update={"weapons": [_weapon(1, "Ember lance", ("GLIMMERBURST",))]}
    )

    assert check_weapon_ability_keywords(factories.snapshot(datasheets=[carrying])) == []


def test_a_snapshot_with_no_weapon_lines_at_all_trips_nothing() -> None:
    """No weapon lines is not an empty keyword class — there is nothing for one to be empty of."""
    weaponless = factories.datasheet("ds-one", faction_id="f-ember").model_copy(
        update={"weapons": []}
    )

    assert check_weapon_ability_keywords(factories.snapshot(datasheets=[weaponless])) == []


def test_a_build_of_a_set_that_states_keywords_does_not_raise_the_advisory(build) -> None:  # type: ignore[no-untyped-def]
    """And the advisory is nowhere near the coverage outcome that would exit 42 on it."""
    assert "COV-WEAPON-ABILITIES-EMPTY" not in [f.finding_code for f in build.findings]
    assert build.coverage.collapsed is False
    assert build.report.scale["weapon_ability_keywords"].count > 0


def test_a_build_of_a_set_that_states_none_raises_it(tmp_path: Path, temp_repo) -> None:  # type: ignore[no-untyped-def]
    """The wiring, not the rule: a run has to actually raise it.

    ``fixtures/disagreements`` states no weapon ability keyword anywhere, which is exactly the
    shape every release had before this fix. Its other findings are that set's own business —
    only this code is asserted.
    """
    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-no-weapon-keywords",
        fixtures_dir=Path(__file__).resolve().parents[2] / "fixtures" / "disagreements",
        offline=True,
        output_root=tmp_path,
        repository_root=temp_repo(),
    )

    assert "COV-WEAPON-ABILITIES-EMPTY" in [f.finding_code for f in result.findings]
    assert result.report.scale["weapon_ability_keywords"].count == 0


def test_the_advisory_is_advisory_in_the_catalogue_and_cannot_be_escalated() -> None:
    """Severity is a property of the code (validation-report.md §1.1), asserted at the source."""
    definition = CATALOGUE["COV-WEAPON-ABILITIES-EMPTY"]

    assert (definition.severity, definition.finding_class) == (
        Severity.ADVISORY,
        FindingClass.COVERAGE,
    )


def _weapon(line: int, name: str, keywords: tuple[str, ...]) -> CuratedWeaponLine:
    return CuratedWeaponLine(
        line=line,
        name=name,
        is_melee=False,
        range='24"',
        attacks="2",
        skill="3+",
        strength="5",
        armour_penetration="-1",
        damage="2",
        ability_keywords=list(keywords),
    )
