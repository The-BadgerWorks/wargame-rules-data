# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 rung R06a (T101, FR-033): the two
# receipts that must hold for the export-only inert path specifically -- the declaration file is
# read-only to every run, and the escape hatch a declaration cannot open
# (`SRC-FACTION-CARRY-FORWARD-NO-PRIOR`) stays blocking. Exercises the REAL
# `curation/carried-forward-factions.json` (19 declared factions as of this rung -- corrected by
# R06a-fix, which found the file had grown to 19 while this header still said five) rather than a
# synthetic one, because "unchanged by any run" is a claim about that specific file.
"""009 T101: the declaration file is read-only, and the no-prior refusal still blocks.

Parametrized across the same two csv payload-naming shapes `tests/unit/test_detail_mode.py` uses
(fixtures vs. live-directory) — this rung's own standing instruction is that every assertion here
must hold on both, from one parametrization, because a fix that only holds on one has broken this
feature before.
"""

from __future__ import annotations

import pytest

from pipeline.acquire.detail_source import resolve_carried_forward
from pipeline.acquire.fixtures import FixturePayload
from pipeline.config import load_config
from pipeline.curate.authored import load_authored
from pipeline.curate.carry_forward import apply_carried_forward
from pipeline.models.findings import Severity
from pipeline.report.catalogue import severity_of
from tests.conftest import REPO_ROOT
from tests.factories import snapshot

CURATION_DIR = REPO_ROOT / "curation"
DECLARATION_FILE = CURATION_DIR / "carried-forward-factions.json"

_CSV_PAYLOAD_NAME_STYLES = pytest.mark.parametrize(
    "csv_payload_name",
    [
        pytest.param("Datasheets.csv", id="live-directory"),
        pytest.param("Datasheets", id="fixtures"),
    ],
)


def test_the_no_prior_refusal_stays_blocking() -> None:
    """A declaration still cannot manufacture data that was never published -- checked at the
    single source of truth for a finding's severity, `pipeline/report/catalogue.py`, so this
    fails the instant anyone tries to soften it there."""
    assert severity_of("SRC-FACTION-CARRY-FORWARD-NO-PRIOR") is Severity.BLOCKING


@_CSV_PAYLOAD_NAME_STYLES
def test_the_declaration_file_is_unchanged_by_a_run_under_export_only_arm(
    csv_payload_name: str,
) -> None:
    """Reads the REAL declaration file, runs the whole inert path on its actual declared slugs,
    and re-reads the file — byte for byte, before and after.

    Neither `resolve_carried_forward` nor `apply_carried_forward` nor `load_authored` accepts a
    curation *write* path at all — there is no parameter here that could point either function at
    this file for anything but a read — but this proves it rather than arguing it from the
    absence of a parameter.
    """
    before = DECLARATION_FILE.read_bytes()

    authored = load_authored(CURATION_DIR)
    declared = authored.carried_forward_slugs
    assert declared, "the fixture this test depends on: at least one faction must be declared"

    config = load_config(env={})  # WGC_DETAIL_ACQUISITION_MODE defaults to csv (export-only)
    outcome = resolve_carried_forward(
        config, [FixturePayload(name=csv_payload_name, text="")], declared_slugs=declared
    )

    # T095/T100's shape: reported, never dropped, and never fabricated as `carried` either.
    assert outcome.carried == frozenset()
    assert outcome.unused == declared

    # The inert path never needs a previous published tree — nothing is spliced, so `None` (a
    # first release, or simply "this test does not have one to hand") must never raise, and must
    # never touch a NO-PRIOR finding: there is nothing here for a declaration to fail to open.
    merged, findings = apply_carried_forward(
        snapshot(factions=[], datasheets=[]),
        previous_tree=None,
        carried_slugs=outcome.carried,
        unused_declaration_slugs=outcome.unused,
        previous_version_id="(none)",
    )

    codes = {f.finding_code for f in findings}
    assert codes == {"SRC-FACTION-CARRY-FORWARD-UNUSED"}
    assert "SRC-FACTION-CARRY-FORWARD-NO-PRIOR" not in codes
    assert not merged.datasheets

    after = DECLARATION_FILE.read_bytes()
    assert after == before
