# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the digest-projection tests (task
# T101): the projection carries only the documented fields, excludes delta prefixes/change
# tags/colours/ids/whitespace/ordering, and the digest is stable across two renders of unchanged
# values (FR-053, research D4b).
"""The projection is the whole detection contract, so these tests are about its *shape*.

Two claims: the projection contains exactly the documented fields and nothing a presentation
detail could reach, and the digest built from it is therefore stable whenever the underlying
values are — including across a page that reorders everything, renumbers every element id,
recolours everything, adds change markers, and adds whitespace.
"""

from __future__ import annotations

from pathlib import Path

from pipeline.detect.digest import digest_json
from pipeline.detect.projection import project_faction
from pipeline.parse.mfm_dom import MfmPage, parse_faction_page
from pipeline.parse.mfm_swap_replay import replay

DETECTION = Path(__file__).resolve().parents[2] / "fixtures" / "detection"


def _page(set_name: str, slug: str) -> MfmPage:
    html = (DETECTION / set_name / "mfm" / f"{slug}.html").read_text(encoding="utf-8")
    return parse_faction_page(slug, replay(html).html)


def test_projection_carries_only_the_documented_fields() -> None:
    projection = project_faction(_page("baseline", "verdant-marchers"))

    assert set(projection) == {"faction_slug", "units", "detachments"}
    assert projection["faction_slug"] == "verdant-marchers"

    units = projection["units"]
    assert len(units) == 2
    for unit in units:
        assert set(unit) == {"unit_name", "cost_table_label", "model_count_label", "points"}

    detachments = projection["detachments"]
    assert len(detachments) == 1
    allowed = {"detachment_name", "dp_cost", "force_disposition", "enhancements"}
    required = {"detachment_name", "dp_cost", "enhancements"}
    for detachment in detachments:
        assert set(detachment) <= allowed
        assert required <= set(detachment)


def test_projection_carries_the_normalised_names_and_the_mechanical_values() -> None:
    projection = project_faction(_page("baseline", "verdant-marchers"))

    unit = next(u for u in projection["units"] if u["model_count_label"] == "5 models")
    assert unit["unit_name"] == "thicket stalker"
    assert unit["cost_table_label"] == "YOUR UNIT COSTS"
    assert unit["points"] == 80

    detachment = projection["detachments"][0]
    assert detachment["detachment_name"] == "warden s oath"
    assert detachment["dp_cost"] == 2
    assert detachment["force_disposition"] == "GUARD THE GROVE"
    assert detachment["enhancements"] == [{"name": "bloomward sigil", "points": 20}]


def test_projection_excludes_delta_markers_change_tags_colours_ids_and_whitespace() -> None:
    """The presentation-only variant renders the same values through a completely different
    page: reordered sections, renumbered `P:`/`S:` ids, different colour classes, an added
    `UPDATED` tag, an added delta marker on an unchanged value, and extra whitespace. None of
    that may reach the projection (research D4b)."""
    baseline = project_faction(_page("baseline", "verdant-marchers"))
    presentation_only = project_faction(_page("presentation-only", "verdant-marchers"))

    assert presentation_only == baseline


def test_digest_is_stable_across_two_renders_of_unchanged_values() -> None:
    baseline_digest = digest_json(project_faction(_page("baseline", "verdant-marchers")))
    presentation_digest = digest_json(
        project_faction(_page("presentation-only", "verdant-marchers"))
    )
    replay_digest = digest_json(project_faction(_page("baseline", "verdant-marchers")))

    assert baseline_digest == presentation_digest == replay_digest


def test_digest_moves_only_for_the_faction_whose_value_actually_changed() -> None:
    """Per-faction isolation: only `verdant-marchers`' digest differs after its 5-model band
    moves from 80 to 85 pts. `duskrail-cabal` is byte-identical between the two sets and its
    digest must therefore be identical too."""
    changed_digest = digest_json(project_faction(_page("mechanical-change", "verdant-marchers")))
    baseline_digest = digest_json(project_faction(_page("baseline", "verdant-marchers")))
    assert changed_digest != baseline_digest

    unaffected_baseline = digest_json(project_faction(_page("baseline", "duskrail-cabal")))
    unaffected_changed_set = digest_json(
        project_faction(_page("mechanical-change", "duskrail-cabal"))
    )
    assert unaffected_baseline == unaffected_changed_set
