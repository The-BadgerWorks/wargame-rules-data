# AI-Assisted: Claude Code (model: claude-sonnet-5) - New test for pipeline P2 task 2:
# `_attach_chapter_keywords` stamps `chapter_keyword` onto a curated detachment from an authored
# `detachment-chapters.json` entry, blocking with `DET-CHAPTER-UNMATCHED` when the entry binds
# nothing, and the scale figure `detachments.chapter_scoped` counts the result. Also a full
# `run_build` end-to-end receipt that an unmatched entry refuses the offline build.
"""Pipeline P2 task 2: the chapter-scoped detachment attach pass.

`_attach_chapter_keywords` is the sole producer of `CuratedDetachment.chapter_keyword`: it reads
`curation/detachment-chapters.json` entries (task 1) and stamps the keyword onto the matching
minted detachment, by `(faction_id, normalised name)`. An entry that matches no detachment, names
a keyword that is not a chapter keyword of that faction, or repeats an earlier entry binds
nothing and raises the blocking `DET-CHAPTER-UNMATCHED` instead of stamping anything (spec
2026-10-09 §1.2).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from pipeline.cli import run_build
from pipeline.config import load_config
from pipeline.curate.assemble import _attach_chapter_keywords
from pipeline.curate.authored import AuthoredContent
from pipeline.exit_codes import ExitCode
from pipeline.models.authored import DetachmentChapterEntry
from pipeline.models.curated import CuratedChapterKeyword
from pipeline.models.findings import Severity
from pipeline.report.validation import scale_figures
from tests import factories

MINIMAL = Path(__file__).resolve().parents[2] / "fixtures" / "minimal"

CHAPTERS = (CuratedChapterKeyword(keyword="FEN WARDENS", parent_faction_id="f-emberwrights"),)
VIGIL = factories.detachment("d-anvil-vigil")  # name "Anvil Vigil"
CHARGE = factories.detachment("d-fx-charge").model_copy(update={"name": "Thornlight Charge"})


def _authored(*entries: dict[str, str]) -> AuthoredContent:
    return AuthoredContent(
        detachment_chapters=tuple(DetachmentChapterEntry.model_validate(e) for e in entries)
    )


def test_a_named_detachment_gains_the_keyword_and_its_sibling_does_not() -> None:
    """Reverted, this is red: chapter_keyword is None on both rows."""
    updated, findings = _attach_chapter_keywords(
        [VIGIL, CHARGE],
        authored=_authored(
            {
                "faction_id": "f-emberwrights",
                "name": "ANVIL VIGIL",
                "chapter_keyword": "FEN WARDENS",
            }
        ),
        chapter_keywords=CHAPTERS,
    )
    assert [d.chapter_keyword for d in updated] == ["FEN WARDENS", None]
    assert findings == []


@pytest.mark.parametrize(
    ("entry", "reason"),
    [
        (
            {
                "faction_id": "f-emberwrights",
                "name": "Test Nothing",
                "chapter_keyword": "FEN WARDENS",
            },
            "detachment",
        ),
        (
            {
                "faction_id": "f-emberwrights",
                "name": "Anvil Vigil",
                "chapter_keyword": "TEST NOWHERE",
            },
            "keyword",
        ),
        (
            {"faction_id": "f-other", "name": "Anvil Vigil", "chapter_keyword": "FEN WARDENS"},
            "detachment,keyword",
        ),
    ],
)
def test_an_entry_that_binds_nothing_blocks_and_stamps_nothing(
    entry: dict[str, str], reason: str
) -> None:
    updated, findings = _attach_chapter_keywords(
        [VIGIL, CHARGE], authored=_authored(entry), chapter_keywords=CHAPTERS
    )
    assert [d.chapter_keyword for d in updated] == [None, None]
    (finding,) = findings
    assert finding.finding_code == "DET-CHAPTER-UNMATCHED"
    assert finding.severity is Severity.BLOCKING
    assert finding.detail["reason"] == reason


def test_a_duplicate_entry_is_reported_once_and_the_first_wins() -> None:
    """Two identical entries: the first stamps the detachment, the second is refused as a
    duplicate and stamps nothing on top of it -- exactly one finding, reason "duplicate"."""
    entry = {
        "faction_id": "f-emberwrights",
        "name": "Anvil Vigil",
        "chapter_keyword": "FEN WARDENS",
    }
    updated, findings = _attach_chapter_keywords(
        [VIGIL, CHARGE], authored=_authored(entry, entry), chapter_keywords=CHAPTERS
    )
    assert [d.chapter_keyword for d in updated] == ["FEN WARDENS", None]
    (finding,) = findings
    assert finding.finding_code == "DET-CHAPTER-UNMATCHED"
    assert finding.severity is Severity.BLOCKING
    assert finding.detail["reason"] == "duplicate"


def test_the_scale_block_counts_scoped_detachments() -> None:
    snap = factories.snapshot(
        detachments=[VIGIL.model_copy(update={"chapter_keyword": "FEN WARDENS"}), CHARGE]
    )
    figure = scale_figures(snap, [])["detachments.chapter_scoped"]
    assert (figure.count, figure.proportion) == (1, 0.5)


def _empty_repo(tmp: Path) -> Path:
    for relative in (
        "data/wh40k-11e/factions",
        "curation/abilities",
        "reports",
        "state",
        "site/prerelease",
        "work",
    ):
        (tmp / relative).mkdir(parents=True, exist_ok=True)
    return tmp


def test_an_unmatched_entry_refuses_a_full_offline_build(tmp_path: Path) -> None:
    """End-to-end through run_build on fixtures/minimal with a copied curation tree naming no
    detachment. Identical outcomes (a clean build) would mean the attach pass is not wired
    through the real build -- this asserts it blocks instead."""
    fixtures = tmp_path / "fixtures"
    shutil.copytree(MINIMAL, fixtures, ignore=shutil.ignore_patterns("build"))
    curation_dir = fixtures / "curation"
    curation_dir.mkdir(parents=True, exist_ok=True)
    (curation_dir / "detachment-chapters.json").write_text(
        '[{"faction_id": "f-ashen-vigil", "name": "Test Nothing", '
        '"chapter_keyword": "TEST NOWHERE"}]',
        encoding="utf-8",
    )
    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-chapter-unmatched",
        fixtures_dir=fixtures,
        offline=True,
        output_root=tmp_path / "out",
        repository_root=_empty_repo(tmp_path / "repo"),
    )
    codes = [f.finding_code for f in result.findings]
    assert "DET-CHAPTER-UNMATCHED" in codes, codes
    assert result.exit_code not in (ExitCode.SUCCESS, ExitCode.ADVISORY_ONLY), result.exit_code
