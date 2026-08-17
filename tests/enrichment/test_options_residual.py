# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the FR-016/SC-006 residual-honesty
# test (008 task T023, Foundational phase): over GF22 (the five refused shape families), GF23
# (no_head_match, plus the deliberately-unresolvable override-material fragment), and GF25 (the
# override-target carriers) -- every option row this feature's own fixtures name as permanently
# unresolvable today -- confirms each one raises its advisory naming datasheet and row ordinal,
# and that none of the three fixture datasheets is ever reported `extracted` while a row of
# theirs stays unresolved. Written before a single Phase 3/4 production exists, so a later
# production that quietly starts resolving one of GF22's refusals (or reports a partial
# datasheet as complete) is caught here rather than only at Polish-phase review.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 008 US1 (T035): the US1 Acceptance Scenario
# 4 test, narrowed to GF23|3 specifically -- confirms the guarantee still holds now that Phase 3's
# three `_COMPLETION_VERBS` productions exist beside it.
"""FR-016 / SC-006: an unresolved row is always visible, never silently absorbed.

`pipeline/curate/assemble.py::_option_structure` reports two facts about a row it cannot resolve
as an option: the advisory (``OPT-UNPARSED``, or ``CST-UNPARSED`` for a row that looks like a
restriction but matches neither member of the closed vocabulary — `007` research D4.2) and the
datasheet's own state, which must never read `extracted` while any row of it is still counted
`unparsed`. Both are `004`/`007` guarantees this feature inherits rather than earns; this file
is where `008`'s own fixtures prove they still hold, over the three populations `008` specifically
adds: refusals (GF22), the `no_head_match` residual (GF23), and the override-target carriers
(GF25) T028/T068-T070's later tests still need standing at `partial`.

None of the nine rows below is restriction-shaped (confirmed directly against
``is_constraint_shaped``, not assumed from reading the sentences) — every one raises
``OPT-UNPARSED``. The expectation is still carried per-row rather than as one blanket assertion,
so a fixture added later that *does* carry a restriction shape only has to change its own line.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pytest

from pipeline.curate.assemble import _option_structure, _OptionOutcome
from pipeline.curate.authored import AuthoredContent
from pipeline.models.curated import WargearOptionState
from pipeline.parse.options_grammar import is_constraint_shaped
from pipeline.parse.wahapedia_csv import CsvReadResult, read_file

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "wahapedia"

#: The three fixture datasheets this file exists to protect, and the internal id each resolves
#: to — kept as one mapping so a test failure's own id is legible without cross-referencing
#: `conftest.py`.
_DATASHEET_IDS: Mapping[str, str] = {
    "GF22": "ds-gf22-refusals",
    "GF23": "ds-gf23-no-head-match",
    "GF25": "ds-gf25-override-target",
}

#: ``(detail id, line, advisory code)`` for every row `008`'s T007/T008/T010 fixtures name as
#: permanently unresolvable. GF22 carries the five refused shape families (T007); GF23 carries
#: the `no_head_match` structural shapes plus the deliberately-unresolvable fragment (T008); GF25
#: carries the option-row override target (T010). GF25's equipment-sentence half is
#: `test_equipment_grammar.py`'s own concern, not this file's — this file is option rows only.
_UNRESOLVABLE_ROWS: tuple[tuple[str, int, str], ...] = (
    ("GF22", 1, "OPT-UNPARSED"),
    ("GF22", 2, "OPT-UNPARSED"),
    ("GF22", 3, "OPT-UNPARSED"),
    ("GF22", 4, "OPT-UNPARSED"),
    ("GF22", 5, "OPT-UNPARSED"),
    ("GF23", 1, "OPT-UNPARSED"),
    ("GF23", 2, "OPT-UNPARSED"),
    ("GF23", 3, "OPT-UNPARSED"),
    ("GF25", 1, "OPT-UNPARSED"),
)


def _detail() -> Mapping[str, CsvReadResult]:
    """The real fixture export, read through the ordinary reader a run uses."""
    return {"Datasheets_options.csv": read_file(FIXTURES / "Datasheets_options.csv")}


def _outcome(detail_id: str) -> _OptionOutcome:
    return _option_structure(
        detail_id, _DATASHEET_IDS[detail_id], _detail(), AuthoredContent(), (), ()
    )


@pytest.mark.parametrize(("detail_id", "line", "code"), _UNRESOLVABLE_ROWS)
def test_every_unresolvable_row_raises_its_advisory_by_datasheet_and_line(
    detail_id: str, line: int, code: str
) -> None:
    """One row, one assertion, named by the row — a failure says which row stopped being visible."""
    datasheet_id = _DATASHEET_IDS[detail_id]
    outcome = _outcome(detail_id)

    matches = [
        finding
        for finding in outcome.findings
        if finding.finding_code == code
        and finding.detail.get("datasheet_id") == datasheet_id
        and finding.detail.get("line") == line
    ]

    assert len(matches) == 1, (
        f"expected exactly one {code} finding for {detail_id}#{line}, found {len(matches)} "
        f"among {[(f.finding_code, f.detail) for f in outcome.findings]}"
    )


@pytest.mark.parametrize("detail_id", sorted(_DATASHEET_IDS))
def test_a_datasheet_carrying_only_unresolvable_rows_is_never_reported_extracted(
    detail_id: str,
) -> None:
    """FR-016's three-state rule: what did not resolve keeps the datasheet at `partial`, never
    promotes it to `extracted`, and is never silently dropped to `none` either."""
    outcome = _outcome(detail_id)

    assert outcome.state is WargearOptionState.PARTIAL
    assert outcome.state is not WargearOptionState.EXTRACTED
    assert outcome.state is not WargearOptionState.NONE


def test_the_unresolvable_rows_are_confirmed_none_of_them_restriction_shaped() -> None:
    """States the module docstring's own claim as an assertion rather than leaving it read-only.

    If a future fixture edit accidentally makes one of these rows restriction-shaped, its
    advisory becomes `CST-UNPARSED` (research D4.2) and the per-row table above would then be
    wrong rather than merely stale — this is what turns that silently-wrong table into a failing
    test instead.
    """
    rows_by_detail_id: dict[str, list[tuple[int, str]]] = {}
    for row in read_file(FIXTURES / "Datasheets_options.csv").rows:
        rows_by_detail_id.setdefault(row.fields["datasheet_id"], []).append(
            (int(row.fields["line"]), row.fields["description"])
        )

    for detail_id, line, code in _UNRESOLVABLE_ROWS:
        description = dict(rows_by_detail_id[detail_id])[line]
        assert not is_constraint_shaped(description), (
            f"{detail_id}#{line} is now restriction-shaped; its expected code above must become "
            "CST-UNPARSED"
        )
        assert code == "OPT-UNPARSED"


def test_a_row_no_us1_production_reaches_stays_unresolved_and_the_datasheet_stays_partial() -> None:
    """US1 Acceptance Scenario 4 (T035).

    GF23|3 ("See the appendix for further wargear notes.") is T008's own deliberately-
    unresolvable fragment — override material, not a shape any production this feature builds
    could ever legitimately close. Now that Phase 3's three `_COMPLETION_VERBS` productions exist
    beside it, this row must still raise its advisory and GF23 must still read `partial`, never
    `extracted` — the promise US1 Acceptance Scenario 4 states, re-checked with the productions
    in place rather than only against their absence (T023's original form).
    """
    outcome = _outcome("GF23")

    matches = [
        finding
        for finding in outcome.findings
        if finding.finding_code == "OPT-UNPARSED"
        and finding.detail.get("datasheet_id") == _DATASHEET_IDS["GF23"]
        and finding.detail.get("line") == 3
    ]
    assert len(matches) == 1

    assert outcome.state is WargearOptionState.PARTIAL
    assert outcome.state is not WargearOptionState.EXTRACTED
