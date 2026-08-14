# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the equivalence check's functional
# tests (007 US5, T050 — match/mismatch/not_compared against `check_equivalence` directly) and
# its retention test (T051 — the whole pipeline, grepped). Per tasks.md rule 6 the retention test
# below was written and confirmed failing (`ModuleNotFoundError`) before
# `pipeline/validate/equivalence.py` existed; quickstart §3 calls it "the cheapest test in the
# feature and the most important."
"""T050: does `check_equivalence` produce the right one of three outcomes? T051: does a real
build ever write the source text it compared anywhere?

T050 calls :func:`pipeline.validate.equivalence.check_equivalence` directly, against a
hand-built ``detail`` mapping and :func:`tests.factories.loadout_datasheet` /
:func:`tests.factories.datasheet` — the same narrow-unit-test shape every other `007` "confirm
the independent test" module in this suite uses, since `fixtures/enrichment` (the shared
grammar/curate fixture set) has no `mfm/` directory and cannot drive a full
:func:`pipeline.cli.run_build` (research this module's own docstring below expands on).

T051 needs a *real* build, because the property under test is what a run **writes to disk**, not
what one function returns. It builds a throwaway fixture set of its own (a copy of
`fixtures/minimal`, the one committed set that already builds end to end, plus one new synthetic
datasheet) rather than reusing the committed `GF16`/`GF17` pair `fixtures/enrichment/README.md`
describes for this purpose — two independent problems with using them as *this* test's vehicle,
both recorded in `.impl-progress.md`'s US5 section: `fixtures/enrichment` cannot build at all,
and both GF16's `qzolthgeist` and GF17's `glow lance` are *also* printed as that card's own
ranged-weapon profile, extracted independently of the equipment sentence — so grepping a real
build of either for its own token would find a legitimate hit with nothing to do with retention.
This test's own fixture keeps its distinctive token in exactly one place: the raw default-
equipment sentence, replaced before publication by a `curation/equipment-overrides.json` entry
that names a different item — the same escape hatch GF17 already demonstrates.
"""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

import pytest

from pipeline.cli import run_build
from pipeline.config import load_config
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.report.catalogue import CATALOGUE
from pipeline.validate.equivalence import EquivalenceSummary, check_equivalence
from tests.factories import datasheet, loadout_datasheet, snapshot

REPO_ROOT = Path(__file__).resolve().parents[2]
MINIMAL = REPO_ROOT / "fixtures" / "minimal"

#: The Setup phase's own retention fixture pair (GF16 `qzolthgeist`, GF17 `glow lance`) is a
#: matching/mismatching pair for T050's `render/loadout.py`-facing story, referenced here only in
#: prose (see module docstring) — this file's own fixtures below stand in for both T050 and T051
#: for the reasons recorded in `.impl-progress.md`.
DISTINCTIVE_TOKEN = "qzolthgeist"


def _csv(file_name: str, rows: list[dict[str, str]]) -> CsvReadResult:
    """A minimal, hand-built `CsvReadResult` — the same shape `read_file` would produce, without
    needing a real export file on disk for a narrow unit test."""
    from pipeline.models.source import WahapediaRow

    return CsvReadResult(
        file_name=file_name,
        field_names=("datasheet_id", "line", "description"),
        rows=tuple(
            WahapediaRow(file_name=file_name, line_number=index, fields=row)
            for index, row in enumerate(rows, start=1)
        ),
        repairs=0,
        findings=(),
    )


# -- T050: match / mismatch / not_compared, against check_equivalence directly -----------------


def test_matching_rendered_and_source_blocks_yield_no_finding() -> None:
    ds = loadout_datasheet()
    detail = {
        "Datasheets_unit_composition.csv": _csv(
            "Datasheets_unit_composition.csv",
            [
                {"datasheet_id": "GF-PROBE", "line": "1", "description": "1 Sootveil Warden"},
                {"datasheet_id": "GF-PROBE", "line": "2", "description": "4-8 Sootveil Trooper"},
            ],
        ),
        EQUIPMENT_TABLE: _csv(
            EQUIPMENT_TABLE,
            [
                {
                    "datasheet_id": "GF-PROBE",
                    "line": "1",
                    "description": (
                        "Every Sootveil Warden is equipped with: Glow lance; Storm maul."
                    ),
                }
            ],
        ),
        "Datasheets_options.csv": _csv(
            "Datasheets_options.csv",
            [
                {
                    "datasheet_id": "GF-PROBE",
                    "line": "1",
                    "description": (
                        "Up to 4 Sootveil Trooper in this unit can be equipped with one of the "
                        "following: Marsh axe; Storm maul, no change. Only one model in this "
                        "unit can be equipped with Marsh axe. Storm maul cannot be replaced."
                    ),
                }
            ],
        ),
    }

    findings, summary = check_equivalence(
        snapshot(datasheets=[ds]), detail, wahapedia_datasheet_ids={ds.datasheet_id: "GF-PROBE"}
    )

    assert summary == EquivalenceSummary(matched=2, mismatched=0, not_compared=0)
    assert findings == []


def test_a_mismatched_source_block_yields_exactly_one_named_finding() -> None:
    ds = loadout_datasheet()
    detail = {
        "Datasheets_unit_composition.csv": _csv(
            "Datasheets_unit_composition.csv",
            [
                {"datasheet_id": "GF-PROBE", "line": "1", "description": "1 Sootveil Warden"},
                {"datasheet_id": "GF-PROBE", "line": "2", "description": "4-8 Sootveil Trooper"},
            ],
        ),
        EQUIPMENT_TABLE: _csv(
            EQUIPMENT_TABLE,
            [
                {
                    "datasheet_id": "GF-PROBE",
                    "line": "1",
                    # Disagrees in exactly one way: a different weapon than the published one.
                    "description": "Every Sootveil Warden is equipped with: void net.",
                }
            ],
        ),
        # No Datasheets_options.csv row at all -> that block is separately not_compared.
    }

    findings, summary = check_equivalence(
        snapshot(datasheets=[ds]), detail, wahapedia_datasheet_ids={ds.datasheet_id: "GF-PROBE"}
    )

    assert summary.mismatched == 1
    assert summary.not_compared == 1
    mismatches = [f for f in findings if f.finding_code == "RND-EQV-MISMATCH"]
    assert len(mismatches) == 1
    finding = mismatches[0]
    assert finding.entity_refs == (ds.datasheet_id,)
    assert dict(finding.detail) == {"datasheet_id": ds.datasheet_id, "block": "composition"}
    assert finding.severity == CATALOGUE["RND-EQV-MISMATCH"].severity


def test_no_detail_counterpart_yields_not_compared_for_both_blocks() -> None:
    """A datasheet the detail source never contributed to at all — `wahapedia_datasheet_ids`
    carries no entry for it, exactly as `AssemblyResult.wahapedia_datasheet_ids` never does for a
    points-only datasheet (`pipeline/curate/assemble.py`)."""
    ds = loadout_datasheet()

    findings, summary = check_equivalence(
        snapshot(datasheets=[ds]), detail={}, wahapedia_datasheet_ids={}
    )

    assert summary == EquivalenceSummary(matched=0, mismatched=0, not_compared=2)
    codes = {f.finding_code for f in findings}
    assert codes == {"RND-EQV-NOT-COMPARED"}


def test_an_empty_rendered_block_is_not_compared_even_with_source_text_present() -> None:
    """`006`'s FR-015 datasheet: no composition, no options at all, so both blocks render empty
    — `not_compared` per contract §9's second reading ("the block rendered empty because every
    row was legitimately omitted"), regardless of what — if anything — `detail` states."""
    ds = datasheet()
    assert ds.composition == ()
    assert ds.option_groups == ()

    detail = {
        "Datasheets_options.csv": _csv(
            "Datasheets_options.csv",
            [{"datasheet_id": "GF-PROBE", "line": "1", "description": "some unrelated text"}],
        )
    }

    findings, summary = check_equivalence(
        snapshot(datasheets=[ds]), detail, wahapedia_datasheet_ids={ds.datasheet_id: "GF-PROBE"}
    )

    assert summary == EquivalenceSummary(matched=0, mismatched=0, not_compared=2)
    assert {f.finding_code for f in findings} == {"RND-EQV-NOT-COMPARED"}


def test_a_mismatch_finding_never_carries_either_sides_text() -> None:
    """The would-fail property test the orchestrator's brief specifically asked for: a mismatch
    finding's payload cannot carry source (or rendered) tokens, because it is never given any —
    only a datasheet id and a block name (data-model.md §4, contract §9.1)."""
    ds = loadout_datasheet()
    distinctive_source_token = "zzyzxquilverine"  # nonsense, invented, found nowhere published
    detail = {
        EQUIPMENT_TABLE: _csv(
            EQUIPMENT_TABLE,
            [
                {
                    "datasheet_id": "GF-PROBE",
                    "line": "1",
                    "description": f"Every model is equipped with: {distinctive_source_token}.",
                }
            ],
        ),
    }

    findings, _ = check_equivalence(
        snapshot(datasheets=[ds]), detail, wahapedia_datasheet_ids={ds.datasheet_id: "GF-PROBE"}
    )

    mismatches = [f for f in findings if f.finding_code == "RND-EQV-MISMATCH"]
    assert mismatches, "fixture should have produced a mismatch to test the payload of"
    for finding in mismatches:
        serialized = repr(finding.detail)
        assert distinctive_source_token not in serialized
        # And, symmetrically, never the rendered side's own item names either — the payload
        # carries only the datasheet id and the block name, full stop.
        assert set(finding.detail) == {"datasheet_id", "block"}


# -- T051: the retention test, over a real build --------------------------------------------


def _insert_retention_datasheet(av_html_path: Path) -> None:
    """Splice one synthetic detail-only datasheet into a copy of `fixtures/minimal`'s `AV.html`
    — same DOM shape `fixtures/enrichment`'s GF16/GF17 already use (composition + equipment
    sentence + a "YOUR UNIT COSTS" table, the detail-only path's own price source), with its own
    harmless weapon so `DISTINCTIVE_TOKEN` is not also printed as a weapon profile (the trap
    GF16/GF17 fall into — see this module's own docstring and `.impl-progress.md`)."""
    char_row = "".join(
        f'<div class="dsCharWrap"><div class="dsCharName">{label}</div>'
        f'<div class="dsCharFrame dsColorBgAV"><div class="dsCharFrameBack">'
        f'<div class="dsCharValue dsColorAV">{value}</div>'
        f"</div></div></div>\n        "
        for label, value in (
            ("M", '6"'),
            ("T", "4"),
            ("SV", "4+"),
            ("W", "2"),
            ("LD", "7+"),
            ("OC", "1"),
        )
    )
    block = f"""
<a name="Retention-Probe"></a>
<div class="dsOuterFrame datasheet pagebreak clFl AVAV AVAG" style="position:relative">
  <div class="dsBannerWrap">
    <div class="dsH2Header"><div>Retention Probe</div></div>
    <div class="dsProfileBaseWrap">
      <div class="dsProfileWrapLeft"><div class="dsProfileWrap">
        {char_row}
      </div></div>
      <div class="dsProfileWrapRight">
        <span class="dsModelName dsModelNameTop">Retention Probe</span>
      </div>
    </div>
  </div>
  <div class="ds2col">
    <div class="dsLeftСol dsColorFrAV">
      <table class="wTable" width="100%">
        <tbody><tr>
          <td class="dsHeader dsColorBgAV"><div class="dsMeleeIcon"></div></td>
          <td class="wTable_WEAPON">
            <div class="dsHeader dsColorBgAV">MELEE WEAPONS</div>
          </td>
          <td><div class="ct dsHeader dsColorBgAV">RANGE</div></td>
          <td><div class="ct dsHeader dsColorBgAV">A</div></td>
          <td><div class="ct dsHeader dsColorBgAV">WS</div></td>
          <td><div class="ct dsHeader dsColorBgAV">S</div></td>
          <td><div class="ct dsHeader dsColorBgAV">AP</div></td>
          <td><div class="ct dsHeader dsColorBgAV">D</div></td>
        </tr></tbody>
        <tbody class="bkg">
          <tr class="wTable2_long"><td></td>
            <td colspan="6" class="pad2626"><span>Training baton</span></td>
          </tr>
          <tr><td></td><td class="wTable2_short pad2626"><span>Training baton</span></td>
            <td><div class="ct pad2626">Melee</div></td>
            <td><div class="ct pad2626">1</div></td>
            <td><div class="ct pad2626">4+</div></td>
            <td><div class="ct pad2626">3</div></td>
            <td><div class="ct pad2626">0</div></td>
            <td><div class="ct pad2626">1</div></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="dsRightСol dsColorFrAV">
      <div class="dsHeader dsColorBgAV">ABILITIES</div>
      <div class="dsAbility"><b>Probe Ward:</b>Invented placeholder mechanic.</div>
      <div class="dsHeader dsColorBgAV">UNIT COMPOSITION</div>
      <div class="dsAbility">
        <ul class="dsUl"><li>1 Retention Probe</li></ul>
        <b>Every model is equipped with:</b>{DISTINCTIVE_TOKEN} rod.</div>
      <div class="dsAbility">
        <table width="100%" border="0" cellspacing="0" cellpadding="2"><tbody>
        <tr><td colspan="2" class="dsUnitCostHeader">YOUR UNIT COSTS</td></tr>
        <tr><td>1 model</td><td><div class="PriceTag">40</div></td></tr>
      </tbody></table></div>
    </div>
  </div>
  <div class="ds2colKW dsColorFrAV">
    <div class="dsLeftСolKW">KEYWORDS: <span class="kwb kwbu">INFANTRY</span>;</div>
    <div class="dsRightСolKW">FACTION KEYWORDS:
      <span class="kwb kwbu">ASHEN</span><span class="kwb kwbu">VIGIL</span>;
    </div>
  </div>
</div>

<a name="Ashen-Warden"></a>"""
    text = av_html_path.read_text(encoding="utf-8")
    marker = '<a name="Ashen-Warden"></a>'
    assert marker in text, "AV.html's own structure moved; this splice point needs updating"
    av_html_path.write_text(text.replace(marker, block, 1), encoding="utf-8")


@pytest.fixture
def retention_fixture_dir(tmp_path: Path) -> Path:
    """A throwaway copy of `fixtures/minimal`, plus one synthetic detail-only datasheet whose
    default-equipment sentence carries `DISTINCTIVE_TOKEN`, plus a `curation/equipment-
    overrides.json` entry that publishes a wholly different item instead — the mismatch shape
    (`pipeline/curate/assemble.py::_equipment`'s override branch), never re-derived from the
    source it replaces.
    """
    fixture_dir = tmp_path / "fixture-src"
    shutil.copytree(MINIMAL, fixture_dir)
    _insert_retention_datasheet(fixture_dir / "wahapedia-html" / "AV.html")
    overrides_path = fixture_dir / "curation" / "equipment-overrides.json"
    overrides_path.write_text(
        """[
  {
    "datasheet_id": "ds-retention-probe",
    "line": 1,
    "applies_to": "unit",
    "items": [{"item_name": "training harness", "count": 1}],
    "note": "007 T051 retention-test fixture: publishes an unrelated name."
  }
]
""",
        encoding="utf-8",
    )
    return fixture_dir


def _iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, ValueError):
            # A binary artifact (e.g. an sqlite snapshot) cannot carry the token as readable
            # text under this reader either way; skipped rather than mis-decoded.
            continue


def test_the_source_text_used_for_a_mismatched_comparison_is_never_written_anywhere(
    retention_fixture_dir: Path, tmp_path: Path, temp_repo: Callable[[], Path]
) -> None:
    """The retention test (T051). Written to fail before `pipeline/validate/equivalence.py`
    existed (`ModuleNotFoundError` on this file's own top-level import), per tasks.md rule 6 and
    quickstart §3."""
    repository_root = temp_repo()
    output_root = tmp_path / "out"

    result = run_build(
        config=load_config(env={"WGC_DETAIL_ACQUISITION_MODE": "html"}),
        rules_version_id="retention-probe",
        fixtures_dir=retention_fixture_dir,
        offline=True,
        output_root=output_root,
        repository_root=repository_root,
    )

    # Confirm the scenario actually exercised what it claims to: the override took effect (the
    # published item is NOT the card's own word), and the comparison happened and disagreed.
    probe = next(d for d in result.snapshot.datasheets if d.name == "Retention Probe")
    assert probe.datasheet_id == "ds-retention-probe"
    published_items = [item.item_name for group in probe.equipment_groups for item in group.items]
    assert published_items == ["training harness"]
    assert DISTINCTIVE_TOKEN not in " ".join(published_items).lower()

    mismatch_findings = [
        f
        for f in result.findings
        if f.finding_code == "RND-EQV-MISMATCH" and probe.datasheet_id in f.entity_refs
    ]
    assert mismatch_findings, "the override should have produced a detectable mismatch"

    # The actual retention proof: every artifact this run wrote, anywhere under output_root
    # (data/, the bundle, reports/) or repository_root (state/, and anything else `temp_repo`
    # seeded) -- zero occurrences of the token the comparison read in memory. Case-sensitive
    # match is deliberate: the token is a nonsense word invented for this test, so a
    # case-folded published fragment would be just as much a finding.
    hits: list[str] = []
    for root in (output_root, repository_root):
        for path, text in _iter_text_files(root):
            if DISTINCTIVE_TOKEN in text.lower():
                hits.append(str(path))
    assert hits == [], f"retention violated -- source token leaked into: {hits}"

    # And a sanity check on the test itself: the token really was available in memory during
    # this build (otherwise the assertion above would be vacuous) -- it is exactly the fixture
    # source file the build read from, which is OUTSIDE both trees just grepped.
    fixture_html = (retention_fixture_dir / "wahapedia-html" / "AV.html").read_text(
        encoding="utf-8"
    )
    assert DISTINCTIVE_TOKEN in fixture_html.lower()
