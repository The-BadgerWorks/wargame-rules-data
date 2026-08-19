# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added for 009 task T048 (FR-010,
# data-model.md §3, Product Owner decision T047 2026-08-18: hybrid now, full later):
# `apply_detail_source_authority`, the per-class dual-acquisition overlay that lets
# `curation/detail-source-authority.json` send exactly the two classes FR-009 measured below
# their floor (options, default_equipment) back to the html arm while every other class stays on
# the build's configured arm -- expressed entirely as data resolved in `pipeline/acquire/`, never
# as a mode branch below it (rule 4).
"""``apply_detail_source_authority`` -- the hybrid, expressed as which arm populates which table.

Every acquisition here is stubbed (no network, no fixture tree): the function under test only
orchestrates ``acquirer_for``/``reader_for`` calls and merges their output, so what matters is
call count and merge shape, not real csv/html content. The mode-containment extension at the
bottom is the structural guard: no scanned module may compare a bare ``arm`` name, the same
discipline T016 already established for ``mode``.
"""

from __future__ import annotations

import ast
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

import pytest

from pipeline.acquire.detail_source import apply_detail_source_authority
from pipeline.config import DetailAcquisitionMode, load_config
from pipeline.models.authored import DetailSourceAuthorityEntry
from pipeline.models.findings import Finding
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE
from pipeline.parse.wahapedia_csv import CsvReadResult


def _config(**overrides: str) -> object:
    return load_config(env=dict(overrides))


def _table(name: str, *, findings: tuple[Finding, ...] = ()) -> CsvReadResult:
    return CsvReadResult(file_name=name, field_names=(), rows=(), repairs=0, findings=findings)


def _primary_detail() -> dict[str, CsvReadResult]:
    return {
        "Datasheets_options.csv": _table("Datasheets_options.csv"),
        EQUIPMENT_TABLE: _table(EQUIPMENT_TABLE),
        "Datasheets_unit_composition.csv": _table("Datasheets_unit_composition.csv"),
    }


def _entry(data_class: str, arm: str) -> DetailSourceAuthorityEntry:
    return DetailSourceAuthorityEntry.model_validate(
        {
            "data_class": data_class,
            "arm": arm,
            "reason": "test fixture, not a real criterion measurement",
            "declared_at": "2026-08-18",
        }
    )


class _StubAcquirer:
    """A drop-in for one arm's acquirer -- counts calls, returns a marked table set."""

    def __init__(
        self, arm: DetailAcquisitionMode, options_marker: str, equipment_marker: str
    ) -> None:
        self.arm = arm
        self.calls = 0
        self._options_marker = options_marker
        self._equipment_marker = equipment_marker

    def __call__(self, config: object, **_kwargs: object) -> tuple[None, list[object]]:
        self.calls += 1
        return None, [object()]  # payloads content is never read by the stubbed reader below


def _stub_reader_factory(options_marker: str, equipment_marker: str):
    def _reader(payloads: object, *, edition_code: str = "") -> dict[str, CsvReadResult]:
        del payloads, edition_code
        return {
            "Datasheets_options.csv": _table(options_marker),
            EQUIPMENT_TABLE: _table(equipment_marker),
        }

    return _reader


@pytest.fixture
def stubbed(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Replace ``acquirer_for``/``reader_for`` so no real arm ever runs.

    Each stub's returned table's ``file_name`` is the arm's own marker string, which is what the
    merge assertions below check for -- a value the real readers would never coincidentally
    produce.
    """
    csv_acquirer = _StubAcquirer(DetailAcquisitionMode.CSV, "csv-options", "csv-equipment")
    html_acquirer = _StubAcquirer(DetailAcquisitionMode.HTML, "html-options", "html-equipment")
    acquirers = {DetailAcquisitionMode.CSV: csv_acquirer, DetailAcquisitionMode.HTML: html_acquirer}
    readers = {
        DetailAcquisitionMode.CSV: _stub_reader_factory("csv-options", "csv-equipment"),
        DetailAcquisitionMode.HTML: _stub_reader_factory("html-options", "html-equipment"),
    }

    import pipeline.acquire.detail_source as module

    monkeypatch.setattr(module, "acquirer_for", lambda mode: acquirers[DetailAcquisitionMode(mode)])
    monkeypatch.setattr(module, "reader_for", lambda mode: readers[DetailAcquisitionMode(mode)])

    return {"csv": csv_acquirer, "html": html_acquirer}


# -- the reversibility case: empty authority is a strict no-op ------------------------------


def test_empty_authority_returns_the_same_object(stubbed: dict[str, object]) -> None:
    detail = _primary_detail()

    result = apply_detail_source_authority(detail, authority=(), config=_config())

    assert result is detail
    assert stubbed["csv"].calls == 0  # type: ignore[attr-defined]
    assert stubbed["html"].calls == 0  # type: ignore[attr-defined]


def test_a_declaration_naming_the_configured_arm_is_a_no_op(stubbed: dict[str, object]) -> None:
    """Declaring `options -> csv` while the build already runs `csv` triggers no supplement."""
    detail = _primary_detail()
    authority = (_entry("options", "csv"),)

    result = apply_detail_source_authority(
        detail, authority=authority, config=_config(WGC_DETAIL_ACQUISITION_MODE="csv")
    )

    assert result is detail
    assert stubbed["csv"].calls == 0  # type: ignore[attr-defined]
    assert stubbed["html"].calls == 0  # type: ignore[attr-defined]


# -- the hybrid overlay itself ----------------------------------------------------------------


def test_a_declared_class_is_overlaid_from_its_declared_arm(stubbed: dict[str, object]) -> None:
    detail = _primary_detail()
    authority = (_entry("options", "html"),)

    result = apply_detail_source_authority(
        detail, authority=authority, config=_config(WGC_DETAIL_ACQUISITION_MODE="csv")
    )

    assert result["Datasheets_options.csv"].file_name == "html-options"
    # the class NOT declared keeps the primary (csv) arm's own table, untouched:
    assert result[EQUIPMENT_TABLE].file_name == EQUIPMENT_TABLE
    assert result["Datasheets_unit_composition.csv"].file_name == "Datasheets_unit_composition.csv"
    assert stubbed["html"].calls == 1  # type: ignore[attr-defined]
    assert stubbed["csv"].calls == 0  # type: ignore[attr-defined]


def test_the_overlaid_table_carries_a_src_class_arm_finding(stubbed: dict[str, object]) -> None:
    detail = _primary_detail()
    authority = (_entry("options", "html"),)

    result = apply_detail_source_authority(
        detail, authority=authority, config=_config(WGC_DETAIL_ACQUISITION_MODE="csv")
    )

    findings = result["Datasheets_options.csv"].findings
    assert len(findings) == 1
    assert findings[0].finding_code == "SRC-CLASS-ARM"
    assert findings[0].detail == {
        "data_class": "options",
        "arm": "html",
        "table": "Datasheets_options.csv",
    }


def test_two_classes_on_the_same_arm_acquire_that_arm_exactly_once(
    stubbed: dict[str, object],
) -> None:
    detail = _primary_detail()
    authority = (_entry("options", "html"), _entry("default_equipment", "html"))

    result = apply_detail_source_authority(
        detail, authority=authority, config=_config(WGC_DETAIL_ACQUISITION_MODE="csv")
    )

    assert result["Datasheets_options.csv"].file_name == "html-options"
    assert result[EQUIPMENT_TABLE].file_name == "html-equipment"
    assert stubbed["html"].calls == 1  # type: ignore[attr-defined]  # not 2
    assert stubbed["csv"].calls == 0  # type: ignore[attr-defined]


def test_the_two_classes_may_split_across_two_different_arms(stubbed: dict[str, object]) -> None:
    detail = _primary_detail()
    authority = (_entry("options", "html"), _entry("default_equipment", "csv"))

    # configured arm is html here, so `default_equipment -> csv` is the one needing a supplement
    # and `options -> html` is the no-op (already the configured arm).
    result = apply_detail_source_authority(
        detail, authority=authority, config=_config(WGC_DETAIL_ACQUISITION_MODE="html")
    )

    assert result["Datasheets_options.csv"].file_name == "Datasheets_options.csv"  # untouched
    assert result[EQUIPMENT_TABLE].file_name == "csv-equipment"
    assert stubbed["csv"].calls == 1  # type: ignore[attr-defined]
    assert stubbed["html"].calls == 0  # type: ignore[attr-defined]


def test_retrieved_at_and_workspace_reach_the_supplemental_acquirer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The supplement is a real acquisition call, not a stripped-down one -- every parameter the
    primary arm would have received reaches the supplemental arm too."""
    received: dict[str, object] = {}

    def _acquirer(mode: DetailAcquisitionMode) -> object:
        def _call(config: object, **kwargs: object) -> tuple[None, list[object]]:
            received.update(kwargs)
            return None, [object()]

        return _call

    def _reader(mode: DetailAcquisitionMode) -> object:
        return _stub_reader_factory("html-options", "html-equipment")

    import pipeline.acquire.detail_source as module

    monkeypatch.setattr(module, "acquirer_for", _acquirer)
    monkeypatch.setattr(module, "reader_for", _reader)

    moment = datetime(2026, 8, 18, 12, 0, tzinfo=UTC)
    apply_detail_source_authority(
        _primary_detail(),
        authority=(_entry("options", "html"),),
        config=_config(WGC_DETAIL_ACQUISITION_MODE="csv"),
        fixtures_dir=Path("some/fixtures"),
        offline=True,
        retrieved_at=moment,
        workspace=Path("some/workspace"),
        carried_forward_slugs=frozenset({"a-slug"}),
    )

    assert received["fixtures_dir"] == Path("some/fixtures")
    assert received["offline"] is True
    assert received["retrieved_at"] == moment
    assert received["workspace"] == Path("some/workspace")
    assert received["carried_forward_slugs"] == frozenset({"a-slug"})


# -- the structural guard: no scanned module may branch on `arm` either (009 T048, FR-012) ------

_SCANNED_PACKAGES: Final = ("parse", "normalize", "reconcile", "curate", "validate", "build")
_PIPELINE_ROOT = Path(__file__).resolve().parents[2] / "pipeline"


def _iter_scanned_modules() -> list[Path]:
    modules: list[Path] = []
    for package in _SCANNED_PACKAGES:
        package_dir = _PIPELINE_ROOT / package
        if package_dir.is_dir():
            modules.extend(sorted(package_dir.rglob("*.py")))
    return modules


def _arm_branches(tree: ast.AST) -> list[ast.Compare]:
    """The `arm`-named sibling of `test_detail_mode.py::_mode_branches` -- same discipline, the
    hybrid's own comparison variable rather than the single-mode dispatch's."""
    found: list[ast.Compare] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        operands = [node.left, *node.comparators]
        is_arm_name = any(
            isinstance(operand, ast.Name) and operand.id == "arm" for operand in operands
        )
        is_comparison_op = all(
            isinstance(op, ast.Is | ast.IsNot | ast.Eq | ast.NotEq) for op in node.ops
        )
        if is_arm_name and is_comparison_op:
            found.append(node)
    return found


@pytest.mark.parametrize("module_path", _iter_scanned_modules(), ids=lambda p: str(p.name))
def test_no_arm_branch_below_acquire(module_path: Path) -> None:
    tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))

    branches = _arm_branches(tree)
    assert not branches, (
        f"{module_path}: an `arm` comparison at line(s) {[b.lineno for b in branches]} -- "
        "FR-012 (rule 4, extended by 009 T048): the hybrid's per-class authority is resolved in "
        "pipeline/acquire/detail_source.py only, never below it."
    )


#: `DetailSourceAuthorityEntry` itself is deliberately NOT scanned the way `DetailAcquisitionMode`
#: is in `test_detail_mode.py`: it is a plain curated **data model** (`curate/authored.py` loads
#: it into `AuthoredContent.detail_source_authority` on the same terms as every other curated
#: entry type -- `CarriedForwardFactionEntry`, `FactionMapEntry`, ...), not a dispatch enum.
#: Loading a curated record is not the branch rule 4 forbids; comparing its `.arm`/`.data_class`
#: field below `acquire` would be, and `test_no_arm_branch_below_acquire` above is what catches
#: that.
