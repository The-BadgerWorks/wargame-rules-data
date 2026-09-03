# AI-Assisted: Claude Code (model: claude-opus-5) - Reproduction and receipt for 009 rung R01b:
# `REC-DETAIL-FACTION-EMPTY` (009 T018/T019) fires on 008's carried-forward factions and turns a
# survivable, Product-Owner-approved condition into exit 30. Every carried-forward faction is
# parentless, so `resolve_factions`' ancestor walk -- which is what spares the Space Marine
# chapters -- saves none of them, and `curate/carry_forward.py` runs AFTER `assemble` with no
# suppression path, so the blocking finding still stands at `_verdict`.
"""The carry-forward exemption, and the two directions that prove it is an exemption not a hole.

`REC-DETAIL-FACTION-EMPTY` exists for the *unexplained* empty faction (`plan.md` finding 2: a
curated-vocabulary mismatch ships an empty roster and the coverage ratchets read 100 on it).
008 FR-024's carry-forward is the *explained* one: a curator declared, in
``curation/carried-forward-factions.json``, that this faction's detail page may be sourced from
the previous published tree when a run cannot fetch it. `SRC-FACTION-CARRIED-FORWARD` already
reports that, advisory, and no second code is minted here (rule 10).

**The exemption is keyed on "declared AND absent", never on "declared".** A declared faction
whose page answered this run is not carried that run -- `pipeline/cli.py` computes the carried
set as ``declared - fetched`` -- and stays fully subject to the guard, which matters because
"page answered, rows carry a vocabulary nothing maps" is precisely `plan.md` finding 2's shape.

Everything below is synthetic: invented faction ids, invented page slugs, invented unit names.
"""

from __future__ import annotations

from pipeline.cli import _verdict
from pipeline.curate.authored import AuthoredContent
from pipeline.curate.carry_forward import apply_carried_forward
from pipeline.exit_codes import ExitCode
from pipeline.models.authored import CarriedForwardFactionEntry, FactionMapEntry
from pipeline.models.findings import Finding, Severity
from pipeline.reconcile.match import resolve_factions
from tests.factories import datasheet, faction, snapshot

#: The detail source's own page slug for the declared faction -- the vocabulary
#: `curation/carried-forward-factions.json` and `FactionMapEntry.detail_source_faction_id` both
#: speak, and the one `curate/carry_forward.py` keys its splice on.
CARRIED_PAGE_SLUG = "veiled-conclave"
CARRIED_MFM_SLUG = "the-veiled-conclave"
CARRIED_FACTION_ID = "f-veiled-conclave"

LIVE_PAGE_SLUG = "tarnish-host"
LIVE_MFM_SLUG = "tarnish-host"
LIVE_FACTION_ID = "f-tarnish-host"

#: **Parentless**, exactly as every entry of the real declarations file is: the ancestor walk in
#: `resolve_factions` that rescues a Space Marine chapter has nothing to walk here.
VEILED_CONCLAVE = FactionMapEntry(
    mfm_slug=CARRIED_MFM_SLUG,
    faction_id=CARRIED_FACTION_ID,
    parent_faction_id=None,
    detail_source_faction_id=CARRIED_PAGE_SLUG,
)
TARNISH_HOST = FactionMapEntry(
    mfm_slug=LIVE_MFM_SLUG,
    faction_id=LIVE_FACTION_ID,
    parent_faction_id=None,
    detail_source_faction_id=LIVE_PAGE_SLUG,
)

#: This run's acquired `Datasheets.csv` rows: the live faction only. The declared faction's page
#: was not fetched, so nothing of its carries a `faction_id` here.
DETAIL_ROWS_WITHOUT_THE_CONCLAVE: tuple[dict[str, str], ...] = (
    {"id": "TH01", "name": "Emberward Vigilant", "faction_id": LIVE_PAGE_SLUG},
    {"id": "TH02", "name": "Emberward Sentinel", "faction_id": LIVE_PAGE_SLUG},
)

#: What `curate/assemble.py` builds from those rows and hands to `resolve_factions`.
PRESENT_THIS_RUN = frozenset(row["faction_id"] for row in DETAIL_ROWS_WITHOUT_THE_CONCLAVE)


def _authored(*, declared: bool) -> AuthoredContent:
    return AuthoredContent(
        faction_map=(VEILED_CONCLAVE, TARNISH_HOST),
        carried_forward_factions=(
            (
                CarriedForwardFactionEntry(
                    faction_slug=CARRIED_PAGE_SLUG,
                    declared_at="2026-08-17",
                    reason="synthetic declaration; this faction exists only in this test",
                ),
            )
            if declared
            else ()
        ),
    )


def _resolve(*, declared: bool, carried: frozenset[str]) -> tuple[Finding, ...]:
    outcome = resolve_factions(
        [CARRIED_MFM_SLUG, LIVE_MFM_SLUG],
        _authored(declared=declared),
        detail_faction_ids_present=PRESENT_THIS_RUN,
        carried_forward_detail_ids=carried,
    )
    return tuple(outcome.findings)


def _previous_tree() -> object:
    """The last published tree, holding both factions -- what the splice reads from."""
    return snapshot(
        factions=[
            faction(LIVE_FACTION_ID, parent=None).model_copy(
                update={"detail_source_faction_id": LIVE_PAGE_SLUG}
            ),
            faction(CARRIED_FACTION_ID, parent=None).model_copy(
                update={"detail_source_faction_id": CARRIED_PAGE_SLUG}
            ),
        ],
        datasheets=[
            datasheet("ds-emberward-vigilant", faction_id=LIVE_FACTION_ID),
            datasheet("ds-veiled-archivist", faction_id=CARRIED_FACTION_ID),
        ],
    )


def _this_runs_candidate() -> object:
    """This run's own assembly: the live faction only."""
    return snapshot(
        factions=[
            faction(LIVE_FACTION_ID, parent=None).model_copy(
                update={"detail_source_faction_id": LIVE_PAGE_SLUG}
            )
        ],
        datasheets=[datasheet("ds-emberward-vigilant", faction_id=LIVE_FACTION_ID)],
    )


def _chain(*, declared: bool, carried: frozenset[str], unused: frozenset[str]) -> list[Finding]:
    """`pipeline/cli.py`'s own ordering: `assemble` (and its `resolve_factions`) at 797, then
    `apply_carried_forward` at 867, then `_verdict` over the accumulated findings."""
    findings = list(_resolve(declared=declared, carried=carried))
    _merged, carry_findings = apply_carried_forward(
        _this_runs_candidate(),
        previous_tree=_previous_tree(),
        carried_slugs=carried,
        unused_declaration_slugs=unused,
        previous_version_id="wh40k-11e-2026-08-3",
    )
    findings.extend(carry_findings)
    return findings


# -- Direction 1: exempted ----------------------------------------------------------------------


def test_a_declared_and_absent_faction_raises_no_empty_finding() -> None:
    """The reproduction. Fails before the fix: `REC-DETAIL-FACTION-EMPTY` is in the list."""
    findings = _resolve(declared=True, carried=frozenset({CARRIED_PAGE_SLUG}))
    codes = [f.finding_code for f in findings]

    assert "REC-DETAIL-FACTION-EMPTY" not in codes


def test_the_whole_chain_does_not_reach_a_blocking_verdict_on_its_account() -> None:
    """`_verdict` is what a carry-forward run actually pays: exit 30 instead of a green build.

    Fails before the fix with `ExitCode.BLOCKING`, because `resolve_factions` appends the
    blocking finding at `assemble` time and `apply_carried_forward` -- which runs 70 lines later
    -- has no suppression path to withdraw it.
    """
    findings = _chain(declared=True, carried=frozenset({CARRIED_PAGE_SLUG}), unused=frozenset())

    codes = [f.finding_code for f in findings]
    assert "SRC-FACTION-CARRIED-FORWARD" in codes, "the splice must still report itself"
    assert _verdict(findings) is not ExitCode.BLOCKING, [
        (f.finding_code, f.severity.value) for f in findings
    ]


# -- Direction 2: still guarded -----------------------------------------------------------------


def test_the_same_faction_undeclared_still_blocks() -> None:
    """Nothing was declared, so nothing is carried: the unexplained empty faction, unchanged.

    Fails if the fix disabled the guard rather than exempting a declared case: the assertion
    below would find an empty `codes` list.
    """
    findings = _chain(declared=False, carried=frozenset(), unused=frozenset())

    codes = [f.finding_code for f in findings]
    assert "REC-DETAIL-FACTION-EMPTY" in codes
    empty = next(f for f in findings if f.finding_code == "REC-DETAIL-FACTION-EMPTY")
    assert empty.severity is Severity.BLOCKING
    assert empty.detail.get("faction_id") == CARRIED_FACTION_ID
    assert _verdict(findings) is ExitCode.BLOCKING


def test_a_declared_faction_whose_page_answered_is_still_guarded() -> None:
    """Declared, but fetched -- so `declared - fetched` carries nothing and the guard stands.

    This is `plan.md` finding 2's own shape wearing a declaration: the page answered, its rows
    arrived, and their `faction_id` vocabulary matches nothing the mapping names. Keying the
    exemption on `authored.carried_forward_slugs` instead of on the carried set would silence
    exactly this case; that is what this test refuses.
    """
    findings = _chain(declared=True, carried=frozenset(), unused=frozenset({CARRIED_PAGE_SLUG}))

    codes = [f.finding_code for f in findings]
    assert "REC-DETAIL-FACTION-EMPTY" in codes
    assert "SRC-FACTION-CARRY-FORWARD-UNUSED" in codes
    assert _verdict(findings) is ExitCode.BLOCKING


def test_the_live_faction_is_never_touched_in_either_direction() -> None:
    """A faction whose rows are present raises nothing, declared or not, carried or not."""
    for declared, carried in (
        (False, frozenset()),
        (True, frozenset({CARRIED_PAGE_SLUG})),
        (True, frozenset({LIVE_PAGE_SLUG})),
    ):
        findings = _resolve(declared=declared, carried=carried)
        codes = [f.detail.get("faction_id") for f in findings]
        assert LIVE_FACTION_ID not in codes, (declared, carried)


def test_the_exemption_is_inert_when_nothing_is_carried() -> None:
    """The default (`frozenset()`) must reproduce today's behaviour exactly -- a caller that has
    not wired the carried set in sees the guard it saw before this change."""
    outcome = resolve_factions(
        [CARRIED_MFM_SLUG, LIVE_MFM_SLUG],
        _authored(declared=True),
        detail_faction_ids_present=PRESENT_THIS_RUN,
    )

    assert [f.finding_code for f in outcome.findings] == ["REC-DETAIL-FACTION-EMPTY"]
