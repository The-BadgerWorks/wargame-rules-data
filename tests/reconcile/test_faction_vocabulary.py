# AI-Assisted: Claude Code (model: claude-sonnet-5) - New tests for REC-DETAIL-FACTION-EMPTY (009
# task T018, data-model.md §2, plan.md finding 2): a mapped detail faction resolving to zero
# detail rows must be a LOUD, blocking failure, not the silent one `curate/assemble.py:1497-1501`
# produces today by comparing a slug against the export's own vocabulary and finding nothing.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - New tests for arm-appropriate faction
# identifier selection (009 task T020, data-model.md §2): a record's optional
# detail_source_faction_code widens scope.detail_faction_ids to both vocabularies rather than
# choosing one, so resolution stays driven entirely by curated data and the acquired rows
# themselves, with no mode parameter anywhere in reconcile (rule 4/FR-012).
"""``REC-DETAIL-FACTION-EMPTY`` — the migration's actual cutover guard.

`plan.md` finding 2 is why this cannot be delegated to the coverage ratchets: a faction that
matches zero detail rows still publishes with every OTHER faction's coverage intact, so
``loadout.options_resolved`` and ``loadout.default_equipment`` both read exactly as they did
before — **100% of nothing is 100%.** The only place this can be caught is at the moment a
mapped faction's own detail-source vocabulary turns out to match none of what was actually
acquired, which is what :func:`pipeline.reconcile.match.resolve_factions` is extended to do here.

Reuses ``fixtures_009_disambiguation.py``'s ``GHOST_ARCHIVE``/``DETAIL_ROWS_NO_GHOST_ARCHIVE``
pair, built in Setup (T010) for exactly this test to consume.

**Arm-blindness, not a mode parameter.** `resolve_factions` takes what it actually observed in
the acquired ``Datasheets.csv`` — a plain set of strings, ``detail_faction_ids_present`` — never
which mode produced them (rule 4, FR-012). The same test data below stands in for either arm's
vocabulary: nothing about the check cares whether a string in the set looks like a page slug or
an export code.
"""

from __future__ import annotations

from pipeline.cli import _verdict
from pipeline.curate.authored import AuthoredContent
from pipeline.exit_codes import ExitCode
from pipeline.models.authored import FactionMapEntry
from pipeline.models.findings import Severity
from pipeline.reconcile.match import resolve_factions
from tests.reconcile.fixtures_009_disambiguation import (
    DETAIL_ROWS_NO_GHOST_ARCHIVE,
    GHOST_ARCHIVE,
    ghost_archive_authored,
)

#: The faction ids `DETAIL_ROWS_NO_GHOST_ARCHIVE` actually carries — what an acquisition of
#: either arm would have reported as "present this run", standing in for the real read of
#: `Datasheets.csv`'s `faction_id` column in `curate/assemble.py`.
_PRESENT_IN_DETAIL_ROWS = frozenset(row["faction_id"] for row in DETAIL_ROWS_NO_GHOST_ARCHIVE)


def test_a_mapped_faction_matching_zero_detail_rows_blocks_and_names_the_faction() -> None:
    outcome = resolve_factions(
        ["ghost-archive"],
        ghost_archive_authored(),
        detail_faction_ids_present=_PRESENT_IN_DETAIL_ROWS,
    )

    codes = [f.finding_code for f in outcome.findings]
    assert codes == ["REC-DETAIL-FACTION-EMPTY"]
    assert outcome.findings[0].severity is Severity.BLOCKING
    assert outcome.findings[0].detail.get("faction_id") == "f-ghost-archive"


def test_it_is_not_the_orphan_finding_the_two_are_complements() -> None:
    """`REC-DETAIL-FACTION-ORPHAN` points the other way — a detail id nobody mapped.

    `GHOST_ARCHIVE` maps a code (`ZZ`) nothing published; the export's own code (`GA`) is
    unmapped in the OTHER direction. This test is about the mapped-but-empty half only:
    `resolve_factions` must raise `REC-DETAIL-FACTION-EMPTY`, and must not raise the advisory
    orphan code, which is `report_orphan_detail_factions`'s job and is not called here at all.
    """
    outcome = resolve_factions(
        ["ghost-archive"],
        ghost_archive_authored(),
        detail_faction_ids_present=_PRESENT_IN_DETAIL_ROWS,
    )

    assert "REC-DETAIL-FACTION-ORPHAN" not in [f.finding_code for f in outcome.findings]


def test_a_faction_whose_id_is_present_does_not_block() -> None:
    """The positive case: the id the mapping names is genuinely among what was acquired."""
    present = frozenset({GHOST_ARCHIVE.detail_source_faction_id, "OTHER"})

    outcome = resolve_factions(
        ["ghost-archive"], ghost_archive_authored(), detail_faction_ids_present=present
    )

    assert outcome.findings == []
    assert outcome.scopes and outcome.scopes[0].faction_id == "f-ghost-archive"


def test_an_empty_present_set_is_inert_not_a_universal_failure() -> None:
    """The default (`frozenset()`, "nothing observed yet") must never itself be read as empty.

    A caller that has not wired in the acquired vocabulary at all — every existing call site
    before this feature — must see exactly today's behaviour, not a newly-blocking run.
    """
    outcome = resolve_factions(["ghost-archive"], ghost_archive_authored())

    assert outcome.findings == []


def test_fires_identically_regardless_of_which_arms_vocabulary_shape_is_observed() -> None:
    """Arm-blindness: a csv-shaped code set and an html-shaped slug set are just data.

    Neither is preferred, inspected for shape, or dispatched on — the function does not know or
    care which arm produced the strings it was handed.
    """
    csv_shaped_codes = frozenset({"SM", "AdM", "TAU"})
    html_shaped_slugs = frozenset({"space-marines", "adeptus-mechanicus", "tau-empire"})

    for present in (csv_shaped_codes, html_shaped_slugs, csv_shaped_codes | html_shaped_slugs):
        outcome = resolve_factions(
            ["ghost-archive"], ghost_archive_authored(), detail_faction_ids_present=present
        )
        assert [f.finding_code for f in outcome.findings] == ["REC-DETAIL-FACTION-EMPTY"], present


# -- T050: the loud failure changes the EXIT CODE, under both arms' vocabulary shape -------------
#
# `plan.md` finding 1's whole point: today the mismatch is loud in the report and silent in the
# exit code (a candidate with 30 factions and no datasheets for one of them still exits 0/20). The
# tests above already prove the finding fires identically for a csv-shaped or html-shaped
# vocabulary; this is the other half SC-006 requires — that firing actually moves `_verdict`,
# through the SAME machinery every other blocking finding is refused by
# (`tests/enrichment/test_gates_and_ratchet.py`'s own precedent for importing `_verdict` directly).


def test_the_loud_failure_changes_the_exit_code_under_both_arm_vocabularies() -> None:
    csv_shaped_codes = frozenset({"SM", "AdM", "TAU"})
    html_shaped_slugs = frozenset({"space-marines", "adeptus-mechanicus", "tau-empire"})

    for present in (csv_shaped_codes, html_shaped_slugs):
        outcome = resolve_factions(
            ["ghost-archive"], ghost_archive_authored(), detail_faction_ids_present=present
        )
        assert _verdict(outcome.findings) is ExitCode.BLOCKING, present


def test_the_positive_case_does_not_move_the_exit_code() -> None:
    """The complement: a faction whose mapped id genuinely was observed changes nothing."""
    present = frozenset({GHOST_ARCHIVE.detail_source_faction_id, "OTHER"})

    outcome = resolve_factions(
        ["ghost-archive"], ghost_archive_authored(), detail_faction_ids_present=present
    )

    assert _verdict(outcome.findings) is ExitCode.SUCCESS


# -- T020: arm-appropriate identifier selection, driven by curated data ------------------------


def test_a_record_with_no_code_keeps_todays_single_identifier() -> None:
    entry = FactionMapEntry(
        mfm_slug="unchanged-faction",
        faction_id="f-unchanged-faction",
        detail_source_faction_id="UF",
    )
    content = AuthoredContent(faction_map=(entry,))

    outcome = resolve_factions(["unchanged-faction"], content)

    assert outcome.scopes[0].detail_faction_ids == ("UF",)


def test_a_record_with_a_code_carries_both_the_slug_and_the_code() -> None:
    """Both `detail_source_faction_id` (html's slug) and the new csv-export code are acceptable.

    Not a choice between them, because nothing here knows or asks which arm ran (FR-012).
    Whichever arm actually acquired the data, only its own vocabulary's value will ever appear in
    a real row's `faction_id` column.
    """
    entry = FactionMapEntry(
        mfm_slug="space-marines",
        faction_id="f-space-marines",
        detail_source_faction_id="space-marines",
        detail_source_faction_code="SM",
    )
    content = AuthoredContent(faction_map=(entry,))

    outcome = resolve_factions(["space-marines"], content)

    assert set(outcome.scopes[0].detail_faction_ids) == {"space-marines", "SM"}


def test_a_chapters_parent_code_is_also_carried_through_the_ancestor_fallback() -> None:
    parent = FactionMapEntry(
        mfm_slug="space-marines",
        faction_id="f-space-marines",
        detail_source_faction_id="space-marines",
        detail_source_faction_code="SM",
    )
    chapter = FactionMapEntry(
        mfm_slug="ember-chapter",
        faction_id="f-ember-chapter",
        parent_faction_id="f-space-marines",
        detail_source_faction_id="space-marines",
        detail_source_faction_code="SM",
    )
    content = AuthoredContent(faction_map=(parent, chapter))

    outcome = resolve_factions(["ember-chapter"], content)

    assert set(outcome.scopes[0].detail_faction_ids) == {"space-marines", "SM"}


def test_matching_against_either_vocabulary_resolves_correctly_with_no_mode_involved() -> None:
    """The end-to-end proof: a csv-shaped acquired row and an html-shaped one both resolve.

    Two separate runs, each against a DIFFERENT single acquired faction id -- one the export
    code, one the html slug -- and both find the scope's roster non-empty. No parameter here
    says which arm ran; only the data does.
    """
    entry = FactionMapEntry(
        mfm_slug="space-marines",
        faction_id="f-space-marines",
        detail_source_faction_id="space-marines",
        detail_source_faction_code="SM",
    )
    content = AuthoredContent(faction_map=(entry,))

    csv_shaped_run = resolve_factions(
        ["space-marines"], content, detail_faction_ids_present=frozenset({"SM"})
    )
    html_shaped_run = resolve_factions(
        ["space-marines"], content, detail_faction_ids_present=frozenset({"space-marines"})
    )

    assert csv_shaped_run.findings == []
    assert html_shaped_run.findings == []


def test_the_ancestor_fallback_id_also_counts_as_present() -> None:
    """A chapter scope's own id is absent, but its parent's — the fallback id — is present.

    `resolve_factions` already builds `detail_faction_ids` as [own, *ancestors]; the emptiness
    check must consult the same tuple, or a legitimately-resolvable chapter (via the parent
    fallback) would be wrongly reported as empty.
    """
    parent = FactionMapEntry(
        mfm_slug="parent-legion", faction_id="f-parent-legion", detail_source_faction_id="PL"
    )
    chapter = FactionMapEntry(
        mfm_slug="child-chapter",
        faction_id="f-child-chapter",
        parent_faction_id="f-parent-legion",
        detail_source_faction_id="CC",
    )
    content = AuthoredContent(faction_map=(parent, chapter))

    outcome = resolve_factions(
        ["child-chapter"], content, detail_faction_ids_present=frozenset({"PL"})
    )

    assert outcome.findings == []
