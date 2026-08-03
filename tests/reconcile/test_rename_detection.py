# AI-Assisted: Claude Code (model: claude-opus-5) - Rename-detection tests (task T082): a rename
# is ONE finding on an unchanged curated id, never a removal plus an addition, and the saved-army
# resolution property that depends on it (FR-015, spec Edge Cases).
"""An upstream rename.

This is the case where getting it wrong is invisible until it is expensive. If a rename is
reported as a removal plus an addition, the curated id changes with the name — and every saved
army that names the old id stops resolving, months later, on a player's phone, with no
explanation. FR-015 exists to stop that, and the mechanism is stage 1 of the matching ladder:
the pairing is confirmed once, so a later run recognises the unit by identity rather than by
name and only the *display name* moves.
"""

from __future__ import annotations

from pipeline.curate.prior import prior_from_snapshot
from pipeline.models.findings import Severity
from pipeline.reconcile.conflicts import detect_faction_changes, detect_renames
from tests import factories


def renamed_pair(*, was: str, now: str):
    before = factories.snapshot(
        datasheets=[factories.datasheet("ds-slate-aegis").model_copy(update={"name": was})]
    )
    after = factories.snapshot(
        datasheets=[factories.datasheet("ds-slate-aegis").model_copy(update={"name": now})]
    )
    return prior_from_snapshot(before, rules_version_id="mfm-2026-05"), after


def test_a_rename_is_one_finding_on_an_unchanged_curated_id() -> None:
    prior, current = renamed_pair(was="SLATE AEGIS", now="SLATE BULWARK")

    findings = detect_renames(prior, current)

    assert [f.finding_code for f in findings] == ["REC-RENAME"]
    assert findings[0].severity is Severity.ADVISORY
    assert findings[0].entity_refs == ("ds-slate-aegis",)
    assert findings[0].detail["previous_name"] == "SLATE AEGIS"
    assert findings[0].detail["name"] == "SLATE BULWARK"


def test_a_rename_is_never_a_removal_plus_an_addition() -> None:
    prior, current = renamed_pair(was="SLATE AEGIS", now="SLATE BULWARK")

    assert set(prior.datasheets) == {d.datasheet_id for d in current.datasheets}, (
        "the id is what carries across the rename; if this set differs, a saved army breaks"
    )


def test_a_saved_army_naming_the_id_still_resolves_after_the_rename() -> None:
    _, current = renamed_pair(was="SLATE AEGIS", now="SLATE BULWARK")

    saved_army_entry = "ds-slate-aegis"

    assert any(d.datasheet_id == saved_army_entry for d in current.datasheets)


def test_an_unchanged_name_reports_nothing() -> None:
    prior, current = renamed_pair(was="SLATE AEGIS", now="SLATE AEGIS")

    assert detect_renames(prior, current) == []


def test_a_new_datasheet_is_not_a_rename() -> None:
    before = factories.snapshot(datasheets=[factories.datasheet("ds-slate-sentinel")])
    after = factories.snapshot(
        datasheets=[
            factories.datasheet("ds-slate-sentinel"),
            factories.datasheet("ds-slate-herald"),
        ]
    )

    assert detect_renames(prior_from_snapshot(before, rules_version_id="mfm-2026-05"), after) == []


def test_the_publishers_faction_list_changing_is_reported_both_ways() -> None:
    before = factories.snapshot(
        factions=[factories.faction("f-slateguard"), factories.faction("f-retired-host")]
    )
    after = factories.snapshot(
        factions=[factories.faction("f-slateguard"), factories.faction("f-quill-covenant")]
    )

    findings = detect_faction_changes(prior_from_snapshot(before, rules_version_id="x"), after)

    assert sorted(f.finding_code for f in findings) == ["REC-FACTION-ADDED", "REC-FACTION-REMOVED"]
    assert all(f.severity is Severity.ADVISORY for f in findings)
