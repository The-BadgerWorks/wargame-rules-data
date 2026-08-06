# AI-Assisted: Claude Code (model: claude-opus-5) - The D5 matching-ladder tests (task T079):
# stage order, faction scoping with the parent fallback, Legends disambiguation before any name
# comparison, refusal on ambiguity, and the property that no fuzzy match is ever auto-applied.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Passed detail_source_ids={} at every
# existing match_units() call site to keep this file compiling and passing after that parameter
# became required (see tests/reconcile/test_publication_preference.py for the new coverage of
# what it does).
# AI-Assisted: Claude Code (model: claude-opus-5) - Passed detail_faction_keywords={} at the same
# call sites for the same reason, when the chapter-keyword narrowing step made that parameter
# required (see tests/reconcile/test_chapter_keyword_preference.py for what it does).
"""The matching ladder (FR-014, FR-026, research D5).

The single most important assertion in this file is the negative one: **a suggestion is never
applied.** Edit-distance scoring exists to rank candidates for a human inside the report, and a
test that only checked the happy path would not notice the day someone wires the top-scoring
suggestion into the match. The failure mode is not a missed match — that is a finding a curator
resolves once and which then carries forward — it is a *wrong* match, which is a silently
mispriced unit in a player's hands at a tournament.
"""

from __future__ import annotations

import pytest

from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import FactionMapEntry, UnitAlias, UnitMapEntry
from pipeline.models.findings import Severity
from pipeline.reconcile.identity import IdRegistry
from pipeline.reconcile.match import (
    datasheet_key,
    match_units,
    rank_suggestions,
    report_orphan_detail_factions,
    resolve_factions,
)

SLATEGUARD = FactionMapEntry(
    mfm_slug="slateguard", faction_id="f-slateguard", detail_source_faction_id="SG"
)
WARDENS = FactionMapEntry(
    mfm_slug="slate-wardens",
    faction_id="f-slate-wardens",
    parent_faction_id="f-slateguard",
    detail_source_faction_id="SGW",
)
QUILL = FactionMapEntry(
    mfm_slug="quill-covenant", faction_id="f-quill-covenant", detail_source_faction_id="QC"
)
#: Two *sibling* curated factions the detail source publishes on one page — the Titan Legions
#: shape, and not the chapter shape: neither is the other's parent, so nothing about the
#: parent fallback applies and each names the shared id outright.
FORGE_LOYAL = FactionMapEntry(
    mfm_slug="forgewrights", faction_id="f-forgewrights", detail_source_faction_id="FORGE"
)
FORGE_FALLEN = FactionMapEntry(
    mfm_slug="fallen-forgewrights",
    faction_id="f-fallen-forgewrights",
    detail_source_faction_id="FORGE",
)


def authored(**overrides: object) -> AuthoredContent:
    base: dict[str, object] = {"faction_map": (SLATEGUARD, WARDENS, QUILL)}
    base.update(overrides)
    return AuthoredContent(**base)  # type: ignore[arg-type]


def scope_for(slug: str, content: AuthoredContent):
    outcome = resolve_factions([slug], content)
    assert outcome.scopes, f"{slug} did not resolve to a scope"
    return outcome.scopes[0]


# --- stage 0: faction mapping is authored, and an unmapped slug blocks ------------------------


def test_unmapped_points_slug_is_blocking() -> None:
    outcome = resolve_factions(["slateguard", "unlisted-host"], authored())

    codes = {finding.finding_code for finding in outcome.findings}
    assert codes == {"REC-FACTION-UNMAPPED"}
    assert all(f.severity is Severity.BLOCKING for f in outcome.findings)
    assert [scope.faction_id for scope in outcome.scopes] == ["f-slateguard"]


def test_detail_faction_referenced_by_no_mapping_is_advisory() -> None:
    findings = report_orphan_detail_factions(["SG", "QC", "ZZ"], authored())

    assert [f.finding_code for f in findings] == ["REC-DETAIL-FACTION-ORPHAN"]
    assert findings[0].severity is Severity.ADVISORY


def test_two_sibling_factions_may_share_one_detail_source_faction_id() -> None:
    """The Titan Legions shape: one detail-source page, two curated factions (C3/R6).

    The taxonomies genuinely disagree in both directions — the chapters split one detail id
    across five curated factions *via the parent fallback*, and the Titan Legions split one
    across two curated factions that are **not** related. `detail_source_faction_id` is the
    publisher's own identifier for the page a faction's datasheets are read from, so two records
    naming the same page is a statement of fact about the source rather than a collision to be
    de-duplicated: the split between them comes from the points source, which prices each
    faction's own units on its own page.

    Live consequence, and the reason this test exists: pointing either record at an id the
    source does not publish (`titan-legions`, `chaos-titan-legions`) silently drops **both**
    factions' datasheets and raises `REC-DETAIL-FACTION-ORPHAN` for the page nobody claimed.
    """
    content = authored(faction_map=(FORGE_LOYAL, FORGE_FALLEN))
    outcome = resolve_factions(["forgewrights", "fallen-forgewrights"], content)

    assert not outcome.findings
    assert {scope.faction_id: scope.detail_faction_ids for scope in outcome.scopes} == {
        "f-forgewrights": ("FORGE",),
        "f-fallen-forgewrights": ("FORGE",),
    }
    # The shared page is claimed, so it is nobody's orphan.
    assert report_orphan_detail_factions(["FORGE"], content) == []

    # And the datasheets divide by what the points source prices where: each faction matches the
    # units listed on its own points page out of the one shared detail pool, and gets its own
    # curated id for a name they both publish.
    registry = IdRegistry()
    detail_names = {"FR01": "Forge Colossus", "FR02": "Fallen Colossus"}
    by_id = {scope.faction_id: scope for scope in outcome.scopes}
    loyal = match_units(
        by_id["f-forgewrights"],
        display_names=["FORGE COLOSSUS"],
        detail_names=detail_names,
        detail_is_legends={},
        detail_source_ids={},
        detail_faction_keywords={},
        authored=content,
        registry=registry,
    )
    fallen = match_units(
        by_id["f-fallen-forgewrights"],
        display_names=["FALLEN COLOSSUS"],
        detail_names=detail_names,
        detail_is_legends={},
        detail_source_ids={},
        detail_faction_keywords={},
        authored=content,
        registry=registry,
    )

    assert not loyal.findings and not fallen.findings
    assert loyal.matches[0].wahapedia_datasheet_id == "FR01"
    assert fallen.matches[0].wahapedia_datasheet_id == "FR02"
    assert loyal.matches[0].datasheet_id != fallen.matches[0].datasheet_id


def test_a_chapter_scope_falls_back_to_its_parent_faction() -> None:
    scope = scope_for("slate-wardens", authored())

    assert scope.detail_faction_ids == ("SGW", "SG"), (
        "the points source lists a chapter unit the detail source files under the parent"
    )


# --- stage 1: stable identity precedes every name comparison ----------------------------------


def test_stable_identity_is_consulted_before_any_name_comparison() -> None:
    content = authored(
        unit_map=(
            UnitMapEntry(
                datasheet_id="ds-slate-aegis",
                mfm_display_name="SLATE BULWARK",
                wahapedia_datasheet_id="SG09",
                confirmed_at="2026-05-04T00:00:00Z",
                confirmed_by="curator",
            ),
        )
    )
    outcome = match_units(
        scope_for("slateguard", content),
        display_names=["SLATE BULWARK"],
        # The detail source calls it something else entirely. Stage 2 could not match it, and
        # that is the point: the confirmed pairing is never re-derived.
        detail_names={"SG09": "Slate Aegis"},
        detail_is_legends={},
        detail_source_ids={},
        detail_faction_keywords={},
        authored=content,
        registry=IdRegistry(),
    )

    assert [(m.datasheet_id, m.stage) for m in outcome.matches] == [("ds-slate-aegis", "identity")]
    assert outcome.matches[0].wahapedia_datasheet_id == "SG09"
    assert not outcome.findings


# --- stage 2: normalised exact match, faction-scoped ------------------------------------------


@pytest.mark.parametrize(
    "points_name",
    ["SLATE SENTINEL", "Slate  Sentinel", "The Slate Sentinel", "Slate–Sentinel"],
)
def test_normalised_exact_match_folds_the_observed_spelling_classes(points_name: str) -> None:
    content = authored()
    outcome = match_units(
        scope_for("slateguard", content),
        display_names=[points_name],
        detail_names={"SG01": "Slate Sentinel"},
        detail_is_legends={},
        detail_source_ids={},
        detail_faction_keywords={},
        authored=content,
        registry=IdRegistry(),
    )

    assert [m.stage for m in outcome.matches] == ["exact"]
    assert outcome.matches[0].wahapedia_datasheet_id == "SG01"


def test_the_same_display_name_in_two_factions_gets_two_ids() -> None:
    content = authored()
    registry = IdRegistry()

    first = match_units(
        scope_for("quill-covenant", content),
        display_names=["SLATE WARDEN"],
        detail_names={"QC01": "Slate Warden"},
        detail_is_legends={},
        detail_source_ids={},
        detail_faction_keywords={},
        authored=content,
        registry=registry,
    )
    second = match_units(
        scope_for("slateguard", content),
        display_names=["SLATE WARDEN"],
        detail_names={"SG03": "Slate Warden"},
        detail_is_legends={},
        detail_source_ids={},
        detail_faction_keywords={},
        authored=content,
        registry=registry,
    )

    ids = {first.matches[0].datasheet_id, second.matches[0].datasheet_id}
    assert len(ids) == 2, "two datasheets in different factions may never share a curated id"
    assert not first.findings and not second.findings, "the faction scope keeps them apart"


def test_the_registry_key_is_faction_scoped_and_legends_discriminated() -> None:
    plain = datasheet_key("f-slateguard", "slate revenant")
    legends = datasheet_key("f-slateguard", "slate revenant", is_legends=True)
    other = datasheet_key("f-quill-covenant", "slate revenant")

    assert len({plain, legends, other}) == 3


# --- the ambiguity guards ---------------------------------------------------------------------


def test_legends_status_is_consulted_before_the_name_is_trusted() -> None:
    content = authored()
    outcome = match_units(
        scope_for("slateguard", content),
        display_names=["SLATE REVENANT"],
        detail_names={"SG04": "Slate Revenant", "SG05": "Slate Revenant"},
        detail_is_legends={"SG05": True},
        detail_source_ids={},
        detail_faction_keywords={},
        authored=content,
        registry=IdRegistry(),
    )

    assert not outcome.findings
    assert outcome.matches[0].wahapedia_datasheet_id == "SG04"


def test_an_ambiguous_pair_is_treated_as_no_match_and_blocks() -> None:
    content = authored()
    outcome = match_units(
        scope_for("slateguard", content),
        display_names=["SLATE REVENANT"],
        detail_names={"SG04": "Slate Revenant", "SG05": "Slate Revenant"},
        detail_is_legends={},  # neither is Legends, so the guard cannot separate them
        detail_source_ids={},
        detail_faction_keywords={},
        authored=content,
        registry=IdRegistry(),
    )

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert outcome.findings[0].severity is Severity.BLOCKING
    assert not outcome.matches, "an ambiguous match is treated as NO match"


# --- stage 3: authored aliases ----------------------------------------------------------------


def test_an_authored_alias_resolves_the_curated_id_and_the_detail_pairing() -> None:
    content = authored(
        unit_aliases=(
            UnitAlias(
                faction_id="f-slateguard", alias="Slate Bulwark", datasheet_id="ds-slate-aegis"
            ),
        ),
        unit_map=(
            UnitMapEntry(
                datasheet_id="ds-slate-aegis",
                mfm_display_name="SLATE AEGIS",
                wahapedia_datasheet_id="SG09",
                confirmed_at="2026-05-04T00:00:00Z",
                confirmed_by="curator",
            ),
        ),
    )
    outcome = match_units(
        scope_for("slateguard", content),
        display_names=["SLATE BULWARK"],
        detail_names={"SG09": "Slate Aegis"},
        detail_is_legends={},
        detail_source_ids={},
        detail_faction_keywords={},
        authored=content,
        registry=IdRegistry(),
    )

    assert [(m.datasheet_id, m.stage) for m in outcome.matches] == [("ds-slate-aegis", "alias")]
    assert outcome.matches[0].wahapedia_datasheet_id == "SG09"


# --- stage 4: report, never guess --------------------------------------------------------------


def test_an_unmatched_points_unit_is_reported_and_still_ships() -> None:
    content = authored()
    outcome = match_units(
        scope_for("slateguard", content),
        display_names=["SLATE HERALD"],
        detail_names={"SG01": "Slate Sentinel"},
        detail_is_legends={},
        detail_source_ids={},
        detail_faction_keywords={},
        authored=content,
        registry=IdRegistry(),
    )

    assert [f.finding_code for f in outcome.findings] == ["REC-UNMATCHED-POINTS-ONLY"]
    assert outcome.findings[0].severity is Severity.ADVISORY
    assert [m.stage for m in outcome.matches] == ["unmatched"]
    assert outcome.matches[0].wahapedia_datasheet_id is None


def test_a_near_miss_is_ranked_as_a_suggestion_and_never_applied() -> None:
    content = authored()
    outcome = match_units(
        scope_for("slateguard", content),
        display_names=["SLATE SENTINELS"],
        detail_names={"SG01": "Slate Sentinel", "SG02": "Slate Phalanx"},
        detail_is_legends={},
        detail_source_ids={},
        detail_faction_keywords={},
        authored=content,
        registry=IdRegistry(),
    )

    (finding,) = outcome.findings
    assert finding.finding_code == "REC-UNMATCHED-POINTS-ONLY"
    assert [s.entity_ref for s in finding.suggestions][:1] == ["wahapedia:SG01"], (
        "the closest candidate is ranked first, for a human"
    )
    assert outcome.matches[0].wahapedia_datasheet_id is None, (
        "a suggestion is NEVER auto-applied — a wrong match is a mispriced unit at a tournament"
    )


def test_suggestions_are_ranked_deterministically_and_bounded() -> None:
    ranked = rank_suggestions(
        "slate sentinel",
        {
            "SG01": "Slate Sentinel",
            "SG02": "Slate Phalanx",
            "SG03": "Slate Warden",
            "SG04": "Quill",
        },
        limit=2,
    )

    assert [s.entity_ref for s in ranked] == ["wahapedia:SG01", "wahapedia:SG03"]
    assert ranked == rank_suggestions(
        "slate sentinel",
        {
            "SG04": "Quill",
            "SG03": "Slate Warden",
            "SG02": "Slate Phalanx",
            "SG01": "Slate Sentinel",
        },
        limit=2,
    ), "ranking may not depend on candidate iteration order"
    assert all(0.0 <= s.score <= 1.0 for s in ranked)
