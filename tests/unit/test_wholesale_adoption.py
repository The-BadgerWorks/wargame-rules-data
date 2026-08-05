# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts wholesale edition adoption end to end
# (004 task T074): with WGC_DETAIL_ACQUISITION_MODE=html and WGC_DETAIL_EDITION=wh40k-11e the
# whole run re-reads the current edition and EDN-HYBRID-ENTITY stops being raised, while under
# csv mode nothing moves at all (FR-003 wholesale, spec Clarifications, research D1d).
"""Both halves of T074, against one fixture set built twice.

``fixtures/minimal`` carries the same invented units in **both** source shapes — the export in
``wahapedia/`` and the datacards in ``wahapedia-html/`` — which is what lets these tests do the
thing that actually proves the design: build the set in each mode and compare the two curated
snapshots against each other.

The result is the strongest statement of mode-blindness available: every datasheet id, every
model line, every weapon profile, every composition entry and every price is **identical**, and
the only differences are the ones the two editions genuinely disagree about. The hybrid marker
is not one of those differences — it clears, which is what wholesale adoption means.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping
from pathlib import Path

import pytest

from pipeline.cli import BuildResult, run_build
from pipeline.config import load_config
from pipeline.models.curated import CuratedDatasheet

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "fixtures" / "minimal"

#: The one difference the two fixture shapes deliberately carry, so it is named rather than
#: silently tolerated: the current-edition page publishes `DEDICATED TRANSPORT` as a keyword
#: where the export published it as a role, and the html twin carries the keyword.
EXPECTED_KEYWORD_ADDITION = "DEDICATED TRANSPORT"


def _build(temp_repo: Callable[[], Path], tmp_path: Path, name: str, **env: str) -> BuildResult:
    return run_build(
        config=load_config(env=dict(env)),
        rules_version_id=name,
        fixtures_dir=FIXTURES,
        offline=True,
        output_root=tmp_path / name,
        repository_root=temp_repo(),
    )


def _by_id(result: BuildResult) -> Mapping[str, CuratedDatasheet]:
    return {sheet.datasheet_id: sheet for sheet in result.snapshot.datasheets}


def _codes(result: BuildResult) -> Counter[str]:
    return Counter(finding.finding_code for finding in result.findings)


@pytest.fixture(scope="module")
def csv_build(tmp_path_factory: pytest.TempPathFactory) -> BuildResult:
    """The mode that has been producing published snapshots. It must not move."""
    root = tmp_path_factory.mktemp("csv")
    return run_build(
        config=load_config(env={}),
        rules_version_id="adoption-csv",
        fixtures_dir=FIXTURES,
        offline=True,
        output_root=root / "out",
        repository_root=_empty_repo(root / "repo"),
    )


@pytest.fixture(scope="module")
def html_build(tmp_path_factory: pytest.TempPathFactory) -> BuildResult:
    """Wholesale adoption: the current-edition source, declared as the current edition."""
    root = tmp_path_factory.mktemp("html")
    return run_build(
        config=load_config(
            env={"WGC_DETAIL_ACQUISITION_MODE": "html", "WGC_DETAIL_EDITION": "wh40k-11e"}
        ),
        rules_version_id="adoption-html",
        fixtures_dir=FIXTURES,
        offline=True,
        output_root=root / "out",
        repository_root=_empty_repo(root / "repo"),
    )


def _empty_repo(path: Path) -> Path:
    """An empty repository root, so the coverage baseline is never the ambient checkout's."""
    (path / "data").mkdir(parents=True, exist_ok=True)
    (path / "state").mkdir(parents=True, exist_ok=True)
    return path


# -- the first half: the hybrid markers clear --------------------------------------------------


def test_csv_mode_still_reports_every_entity_as_hybrid(csv_build: BuildResult) -> None:
    """Today's behaviour, unchanged: 11e points against a 10e export is a hybrid entity."""
    assert _codes(csv_build)["EDN-HYBRID-ENTITY"] == len(csv_build.snapshot.datasheets)
    assert all(sheet.provenance.is_hybrid_edition for sheet in csv_build.snapshot.datasheets)


def test_html_mode_at_the_current_edition_raises_no_hybrid_finding(html_build: BuildResult) -> None:
    """FR-003 wholesale: both halves of every entity now come from the current edition."""
    assert _codes(html_build)["EDN-HYBRID-ENTITY"] == 0
    assert not any(sheet.provenance.is_hybrid_edition for sheet in html_build.snapshot.datasheets)


def test_the_adopted_edition_is_carried_into_every_entitys_provenance(
    html_build: BuildResult,
) -> None:
    assert {sheet.provenance.detail_edition_code for sheet in html_build.snapshot.datasheets} == {
        "wh40k-11e"
    }
    # A same-edition datasheet omits the field rather than repeating the snapshot's own edition
    # (`curated-snapshot-format.md` §5), which is how a consumer sees the adoption at all.
    emitted = {
        sheet.provenance.emitted_detail_edition_code for sheet in html_build.snapshot.datasheets
    }
    assert emitted == {None}


def test_the_marker_is_driven_by_the_declared_edition_and_not_by_the_mode(
    temp_repo: Callable[[], Path], tmp_path: Path
) -> None:
    """The mode selects a parser; the *edition* is what the marker is about (FR-005).

    Stated as a test because the two are adopted together and it would be easy to write code
    that conflated them — after which a mode change would silently restate an edition claim.
    """
    same_edition_csv = _build(temp_repo, tmp_path, "csv-11e", WGC_DETAIL_EDITION="wh40k-11e")
    assert _codes(same_edition_csv)["EDN-HYBRID-ENTITY"] == 0

    older_edition_html = _build(
        temp_repo,
        tmp_path,
        "html-10e",
        WGC_DETAIL_ACQUISITION_MODE="html",
        WGC_DETAIL_EDITION="wh40k-10e",
    )
    assert _codes(older_edition_html)["EDN-HYBRID-ENTITY"] == len(
        older_edition_html.snapshot.datasheets
    )


# -- the second half: nothing else moves --------------------------------------------------------


def test_both_modes_curate_the_same_datasheets(
    csv_build: BuildResult, html_build: BuildResult
) -> None:
    assert set(_by_id(csv_build)) == set(_by_id(html_build))
    assert len(csv_build.snapshot.datasheets) == len(html_build.snapshot.datasheets)


def test_every_characteristic_weapon_and_composition_entry_is_identical(
    csv_build: BuildResult, html_build: BuildResult
) -> None:
    """The mode-blindness proof at snapshot level: the same values from two source shapes."""
    csv_sheets, html_sheets = _by_id(csv_build), _by_id(html_build)
    for identifier in sorted(csv_sheets):
        left, right = csv_sheets[identifier], html_sheets[identifier]
        assert [m.model_dump() for m in left.models] == [m.model_dump() for m in right.models]
        assert [w.model_dump() for w in left.weapons] == [w.model_dump() for w in right.weapons]
        assert [c.model_dump() for c in left.composition] == [
            c.model_dump() for c in right.composition
        ]
        # Every field of a cost row but the acquisition id, which embeds the retrieval's own
        # content fingerprint and is *supposed* to differ: the two runs read two documents.
        assert [c.model_dump(exclude={"source_acquisition_id"}) for c in left.costs] == [
            c.model_dump(exclude={"source_acquisition_id"}) for c in right.costs
        ]
        assert left.ability_keys == right.ability_keys
        assert left.is_legends == right.is_legends
        assert left.damaged_threshold == right.damaged_threshold


def test_the_only_keyword_difference_is_the_one_the_editions_genuinely_disagree_about(
    csv_build: BuildResult, html_build: BuildResult
) -> None:
    csv_sheets, html_sheets = _by_id(csv_build), _by_id(html_build)
    added: set[str] = set()
    for identifier in sorted(csv_sheets):
        left = {k.keyword for k in csv_sheets[identifier].keywords}
        right = {k.keyword for k in html_sheets[identifier].keywords}
        assert left <= right, f"{identifier} lost a keyword under html mode"
        added |= right - left
    assert added == {EXPECTED_KEYWORD_ADDITION}


def test_a_dedicated_transport_is_recognised_from_the_keyword_the_current_edition_publishes(
    html_build: BuildResult,
) -> None:
    """The current-edition page publishes no role column, so the flag reads the keyword."""
    transports = [
        sheet.datasheet_id
        for sheet in html_build.snapshot.datasheets
        if sheet.is_dedicated_transport
    ]
    assert transports == ["ds-ashen-carrier"]


def test_the_leader_pairings_survive_the_mode_change(
    csv_build: BuildResult, html_build: BuildResult
) -> None:
    csv_sheets, html_sheets = _by_id(csv_build), _by_id(html_build)
    assert {i: s.leader_pairs for i, s in csv_sheets.items()} == {
        i: s.leader_pairs for i, s in html_sheets.items()
    }


def test_no_finding_category_appears_under_html_mode_that_csv_mode_did_not_already_raise(
    csv_build: BuildResult, html_build: BuildResult
) -> None:
    """Other than the hybrid marker clearing, the shape of the run is unchanged."""
    csv_codes = set(_codes(csv_build)) - {"EDN-HYBRID-ENTITY"}
    html_codes = set(_codes(html_build))
    assert html_codes <= csv_codes


def test_both_modes_price_every_datasheet_the_points_source_priced(
    csv_build: BuildResult, html_build: BuildResult
) -> None:
    """SC-004's priced projection, restated across the mode boundary: same units, same prices."""

    def priced(result: BuildResult) -> dict[str, list[tuple[int, int]]]:
        return {
            sheet.datasheet_id: [(cost.model_count, cost.points) for cost in sheet.costs]
            for sheet in result.snapshot.datasheets
        }

    assert priced(csv_build) == priced(html_build)
