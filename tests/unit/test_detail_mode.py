# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added the source-level mode-containment
# scan (009 task T016, FR-012): an AST walk over pipeline/parse, normalize, reconcile, curate,
# validate and build asserting no module below acquire branches on a `mode` comparison or
# references `DetailAcquisitionMode` at all. A hybrid (T048) is expressed as which arm populates
# which table, declared in curation/ and resolved at acquisition -- never as a conditional in one
# of these six stages -- so this is the structural guard for rule 4, not a style preference.
# AI-Assisted: Claude Code (model: claude-opus-5) - Extended the mode-parity assertions to the
# real html arm and to the reader table (004 task T074): both modes now acquire and both
# produce the same file-name -> CsvReadResult mapping, which is the whole of mode-blindness.
# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the WGC_DETAIL_ACQUISITION_MODE
# dispatch (004 task T018): csv routes to the existing export acquirer unchanged, html routes to
# the datacard acquirer, the two signatures and return shapes agree, and an unrecognised mode is
# a configuration error (004 research D1d, plan Architecture).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the unset-source-URL assertions (004
# T075 follow-up): both arms refuse the empty default rather than interpreting it, and a fixture
# run still never reads it.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the `resolve_carried_forward` receipts
# (009 rung R01b): the carried/unused split is the one mode question carry-forward involves, so it
# is resolved in `acquire/detail_source.py` and must stay empty under every arm that has no
# per-faction page -- otherwise a csv payload's file name would read as a carried faction slug and
# exempt every declared faction from `REC-DETAIL-FACTION-EMPTY`.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 rung R06a (T095/T100, FR-033): replaced
# `test_a_declaration_never_leaks_into_csv_mode`'s "unused stays empty" assertion, which was
# pinning the exact silent-discard behaviour this rung fixes, with the T095/T100 receipt --
# confirmed red against `main` at `6b7fd150` first -- and parametrized both csv-mode tests across
# the fixtures adapter's and the live adapter's own payload-naming shapes from one place, per this
# rung's own standing instruction: a fix that only holds on one path has broken this feature four
# times before.
"""Mode-blindness is a property to be proven, not a comment to be believed.

The design's load-bearing claim is that everything below ``acquire`` cannot tell which mode ran.
The only way that stays true is if the two arms are interchangeable *in shape* — same call
signature, same return type — so these tests compare the two arms against each other rather than
checking that each one works in isolation.

Everything here runs offline against a synthetic fixture tree; nothing opens a socket.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

import pytest

from pipeline.acquire.detail_source import (
    ACQUIRERS,
    READERS,
    acquire_detail,
    acquirer_for,
    read_detail,
    reader_for,
    resolve_carried_forward,
)
from pipeline.acquire.fixtures import FixturePayload
from pipeline.acquire.wahapedia import acquire_wahapedia
from pipeline.acquire.wahapedia_html import acquire_wahapedia_html
from pipeline.config import ConfigError, DetailAcquisitionMode, PipelineConfig, load_config
from pipeline.models.source import SourceAcquisition, SourceKey
from pipeline.parse.wahapedia_csv import CsvReadResult

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "minimal"
#: The html-mode fixture set: the same invented units in the datacard shape (research D1d).
ENRICHMENT = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment"


def _config(**overrides: str) -> PipelineConfig:
    return load_config(env=dict(overrides))


# -- the dispatch ---------------------------------------------------------------------------


def test_the_table_covers_every_documented_mode() -> None:
    assert set(ACQUIRERS) == set(DetailAcquisitionMode)


def test_csv_routes_to_the_existing_export_acquirer_unchanged() -> None:
    # "Unchanged" is the requirement, not "equivalent": the csv path is the one that has been
    # producing published snapshots, and this feature must not perturb it.
    assert acquirer_for(DetailAcquisitionMode.CSV) is acquire_wahapedia
    assert acquirer_for("csv") is acquire_wahapedia


def test_html_routes_to_the_datacard_acquirer() -> None:
    assert acquirer_for(DetailAcquisitionMode.HTML) is acquire_wahapedia_html
    assert acquirer_for("html") is acquire_wahapedia_html


def test_the_default_mode_is_csv() -> None:
    assert _config().detail_acquisition_mode is DetailAcquisitionMode.CSV


@pytest.mark.parametrize("mode", ["xml", "CSV", "", "html ", "csv,html"])
def test_an_unrecognised_mode_is_a_configuration_error(mode: str) -> None:
    with pytest.raises(ConfigError, match="WGC_DETAIL_ACQUISITION_MODE"):
        acquirer_for(mode)


def test_an_unrecognised_mode_is_refused_even_on_a_hand_built_config() -> None:
    """``load_config`` validates, but it is not the only way a config is constructed.

    A ``dataclasses.replace`` in a test, or a future caller building one directly, would
    otherwise reach the dispatch with an unvalidated string and fail as a ``KeyError`` deep in a
    stage rather than as the configuration error it is.
    """
    smuggled = dataclasses.replace(_config(), detail_acquisition_mode="parquet")  # type: ignore[arg-type]
    with pytest.raises(ConfigError):
        acquire_detail(smuggled, fixtures_dir=FIXTURES, offline=True)


# -- the source location: configured, never inferred ----------------------------------------


@pytest.mark.parametrize("mode", list(DetailAcquisitionMode))
@pytest.mark.parametrize("url", ["", "   "])
def test_a_live_acquisition_without_a_source_url_is_a_configuration_error(
    mode: DetailAcquisitionMode, url: str
) -> None:
    """The defect the first real ``html``-mode invocation found, in both arms.

    ``WGC_DETAIL_SOURCE_URL`` defaults to empty. Under ``csv`` mode that empty string parsed as a
    *relative path*, a relative path is the process's working directory, and the repository
    checkout is not an export — so a run that had simply not been configured went looking for the
    export beside its own source and stopped with an FR-008 partial-export diagnostic naming
    `Abilities.csv`. Wrong fault, wrong exit code, and it pointed the investigation at a parser
    that had never run.
    """
    config = _config(WGC_DETAIL_ACQUISITION_MODE=mode.value, WGC_DETAIL_SOURCE_URL=url)

    with pytest.raises(ConfigError, match="WGC_DETAIL_SOURCE_URL"):
        acquire_detail(config, fixtures_dir=None, offline=True)


@pytest.mark.parametrize("mode", list(DetailAcquisitionMode))
def test_the_unset_source_is_never_reported_as_a_partial_export(
    mode: DetailAcquisitionMode,
) -> None:
    """FR-008 is about a source that answered incompletely. This one was never asked."""
    config = _config(WGC_DETAIL_ACQUISITION_MODE=mode.value, WGC_DETAIL_SOURCE_URL="")

    with pytest.raises(ConfigError) as raised:
        acquire_detail(config, fixtures_dir=None, offline=True)

    message = str(raised.value)
    assert "FR-008" not in message
    assert "Abilities.csv" not in message
    assert "partial" not in message


@pytest.mark.parametrize("mode", list(DetailAcquisitionMode))
def test_a_fixture_run_never_reads_the_source_url(mode: DetailAcquisitionMode) -> None:
    """Which is why the fixture path stayed green while the live path could not run at all.

    The refusal must not spread to the rehearsal: a fixture set *is* the source, and every test
    in this repository — and the whole of CI — would otherwise need a live URL configured.
    """
    config = _config(WGC_DETAIL_ACQUISITION_MODE=mode.value, WGC_DETAIL_SOURCE_URL="")
    fixtures = FIXTURES if mode is DetailAcquisitionMode.CSV else ENRICHMENT

    _acquisition, payloads = acquire_detail(config, fixtures_dir=fixtures, offline=True)

    assert payloads


# -- shape parity: the mode-blindness proof -------------------------------------------------


def test_both_arms_take_the_same_arguments() -> None:
    csv_signature = inspect.signature(acquire_wahapedia)
    html_signature = inspect.signature(acquire_wahapedia_html)
    assert list(csv_signature.parameters) == list(html_signature.parameters)
    for name, csv_parameter in csv_signature.parameters.items():
        html_parameter = html_signature.parameters[name]
        assert csv_parameter.kind is html_parameter.kind, name
        assert csv_parameter.default == html_parameter.default, name


def test_the_dispatch_takes_the_same_arguments_as_both_arms() -> None:
    dispatch = inspect.signature(acquire_detail)
    assert list(dispatch.parameters) == list(inspect.signature(acquire_wahapedia).parameters)


def test_csv_mode_produces_a_source_acquisition_through_the_dispatch() -> None:
    acquisition, payloads = acquire_detail(_config(), fixtures_dir=FIXTURES, offline=True)

    assert isinstance(acquisition, SourceAcquisition)
    assert acquisition.source_key is SourceKey.WAHAPEDIA
    assert payloads, "the fixture tree carries an export"


def test_the_dispatch_is_the_same_call_as_the_arm_it_routes_to() -> None:
    # If these two ever produced different records, "mode-blind below parse" would be false the
    # moment a second mode existed. `retrieved_at` is pinned because an acquisition_id embeds
    # the retrieval timestamp, and comparing two records taken a millisecond apart would compare
    # the clock rather than the dispatch.
    moment = datetime(2026, 8, 5, 12, 0, tzinfo=UTC)
    through_dispatch, dispatch_payloads = acquire_detail(
        _config(), fixtures_dir=FIXTURES, offline=True, retrieved_at=moment
    )
    directly, direct_payloads = acquire_wahapedia(
        _config(), fixtures_dir=FIXTURES, offline=True, retrieved_at=moment
    )

    assert through_dispatch == directly
    assert [p.name for p in dispatch_payloads] == [p.name for p in direct_payloads]


def test_html_mode_produces_the_same_record_shape_through_the_dispatch() -> None:
    """The parity that matters, now that both arms really acquire (`004` T072).

    Same record type, same source key, same coverage vocabulary: an acquisition record cannot be
    read to discover which mode produced it, which is what "mode-blind below acquire" means in
    practice rather than in a comment.
    """
    config = _config(WGC_DETAIL_ACQUISITION_MODE="html")
    assert config.detail_acquisition_mode is DetailAcquisitionMode.HTML

    acquisition, payloads = acquire_detail(config, fixtures_dir=ENRICHMENT, offline=True)

    assert isinstance(acquisition, SourceAcquisition)
    assert acquisition.source_key is SourceKey.WAHAPEDIA
    assert acquisition.declared_edition_code == config.detail_edition
    assert payloads, "the fixture tree carries a datacard page"


def test_both_readers_return_the_same_mapping_shape() -> None:
    csv_records = read_detail(_config(), acquire_detail(_config(), fixtures_dir=FIXTURES)[1])
    html_config = _config(WGC_DETAIL_ACQUISITION_MODE="html")
    html_records = read_detail(html_config, acquire_detail(html_config, fixtures_dir=ENRICHMENT)[1])

    for records in (csv_records, html_records):
        assert all(name.endswith(".csv") for name in records)
        assert all(isinstance(result, CsvReadResult) for result in records.values())

    # Every table the assemble stage indexes into by name, both arms carry — that is what lets
    # `curate` read `detail["Datasheets_options.csv"]` without asking which mode ran.
    # `Enhancements.csv` is deliberately not among them: it is in the export and no stage has
    # ever read it, since enhancement pricing comes from the points source (FR-001).
    consumed = {
        "Abilities.csv",
        "Datasheets.csv",
        "Datasheets_abilities.csv",
        "Datasheets_keywords.csv",
        "Datasheets_leader.csv",
        "Datasheets_models.csv",
        "Datasheets_models_cost.csv",
        "Datasheets_options.csv",
        "Datasheets_unit_composition.csv",
        "Datasheets_wargear.csv",
        "Detachments.csv",
        "Source.csv",
    }
    assert consumed <= set(csv_records)
    assert consumed <= set(html_records)

    # And one the csv export does not publish at all: the detachment rules US4's denominator is
    # measured against, which only the current-edition source states (004 T072 handoff).
    assert "Detachment_abilities.csv" in html_records


def test_the_reader_table_covers_every_documented_mode() -> None:
    assert set(READERS) == set(DetailAcquisitionMode)


@pytest.mark.parametrize("mode", ["xml", "CSV", "", "html "])
def test_an_unrecognised_mode_is_a_configuration_error_for_the_reader_too(mode: str) -> None:
    with pytest.raises(ConfigError, match="WGC_DETAIL_ACQUISITION_MODE"):
        reader_for(mode)


# -- the structural guard: no module below acquire may branch on mode (009 T016, FR-012) --------

#: Every stage rule 4 names by name. `pipeline/acquire`, `pipeline/cli.py`, `pipeline/config.py`,
#: `pipeline/models`, `pipeline/report`, `pipeline/detect`, `pipeline/render`, `pipeline/publish`
#: and `pipeline/observability` are deliberately NOT scanned: the rule's own wording is "parsing,
#: normalization, reconciliation, curation, validation, or build", not "everywhere the identifier
#: `mode` appears". `pipeline/cli.py:843`'s own `if config.detail_acquisition_mode is
#: DetailAcquisitionMode.HTML` is the orchestration layer selecting which carry-forward slug sets
#: apply -- above every one of these six stages, not below them -- and is unaffected by this scan.
_SCANNED_PACKAGES: Final = (
    "parse",
    "normalize",
    "reconcile",
    "curate",
    "validate",
    "build",
)

_PIPELINE_ROOT = Path(__file__).resolve().parents[2] / "pipeline"


def _iter_scanned_modules() -> list[Path]:
    modules: list[Path] = []
    for package in _SCANNED_PACKAGES:
        package_dir = _PIPELINE_ROOT / package
        if not package_dir.is_dir():
            continue
        modules.extend(sorted(package_dir.rglob("*.py")))
    return modules


def _mode_branches(tree: ast.AST) -> list[ast.Compare]:
    """Every `ast.Compare` node comparing a bare `mode` name with `is`/`is not`/`==`/`!=`.

    An AST walk rather than a text search on purpose: `equipment_grammar.py`'s own docstring
    reads "...its absence under csv mode is what..." and `wahapedia_html_dom.py`'s reads
    "Faction identity under this mode is the page slug" -- both perfectly legitimate prose that a
    substring search on `"mode is"` would misreport as a branch. A comment or a docstring is not
    part of the AST's `Compare`/`Name` nodes, so this scan is blind to prose by construction and
    can only ever find an actual conditional.
    """
    found: list[ast.Compare] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        operands = [node.left, *node.comparators]
        is_mode_name = any(
            isinstance(operand, ast.Name) and operand.id == "mode" for operand in operands
        )
        is_comparison_op = all(
            isinstance(op, ast.Is | ast.IsNot | ast.Eq | ast.NotEq) for op in node.ops
        )
        if is_mode_name and is_comparison_op:
            found.append(node)
    return found


def _detail_acquisition_mode_references(tree: ast.AST) -> list[ast.Name]:
    """Every reference to the `DetailAcquisitionMode` name itself, import or use.

    Not just comparisons: a module below `acquire` that imports the enum at all has already
    started down the path the design-loss warning names, even before it writes a branch.
    """
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id == "DetailAcquisitionMode"
    ]


@pytest.mark.parametrize("module_path", _iter_scanned_modules(), ids=lambda p: str(p.name))
def test_no_mode_branch_or_reference_below_acquire(module_path: Path) -> None:
    tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))

    branches = _mode_branches(tree)
    assert not branches, (
        f"{module_path}: a `mode` comparison at line(s) "
        f"{[b.lineno for b in branches]} -- FR-012 (rule 4): if a mode branch appears anywhere "
        "below acquire, the design has been lost. Express a hybrid as which arm populates which "
        "table, declared in curation/ and resolved at acquisition, never as a conditional here."
    )

    references = _detail_acquisition_mode_references(tree)
    assert not references, (
        f"{module_path}: `DetailAcquisitionMode` is referenced at line(s) "
        f"{[r.lineno for r in references]} -- this stage should never need to know the mode "
        "exists at all, let alone which one ran."
    )


def test_the_scan_covers_a_nonempty_module_set() -> None:
    """A scan over zero files would pass vacuously and prove nothing."""
    assert len(_iter_scanned_modules()) > 10


def test_selecting_html_mode_changes_no_other_configured_value() -> None:
    # The mode selects a parser and nothing else. Anything else moving with it would be a
    # behaviour branch wearing a variable's clothes.
    csv_config = _config()
    html_config = _config(WGC_DETAIL_ACQUISITION_MODE="html")

    csv_values = dataclasses.asdict(csv_config)
    html_values = dataclasses.asdict(html_config)
    differing = {k for k in csv_values if csv_values[k] != html_values[k]}
    assert differing == {"detail_acquisition_mode"}


# -- the carry-forward split, and why it lives in `acquire/` (009 rung R01b) --------------------
#
# `REC-DETAIL-FACTION-EMPTY` (009 T018/T019) blocks a mapped faction that resolves to zero detail
# rows. 008's carry-forward (FR-024) is the Product-Owner-approved answer for exactly that
# condition, and every declared faction is parentless, so `resolve_factions`' ancestor walk -- the
# thing that spares a Space Marine chapter -- rescued none of them. The exemption needs the set of
# ids actually carried, which is a MODE question (is a payload name a faction slug at all?), so it
# is answered here and travels below `acquire` as plain data.


def _payload(name: str) -> FixturePayload:
    return FixturePayload(name=name, text="")


_DECLARED: Final = frozenset({"veiled-conclave", "tarnish-host"})


def test_html_mode_splits_declared_slugs_by_what_acquisition_returned() -> None:
    outcome = resolve_carried_forward(
        _config(WGC_DETAIL_ACQUISITION_MODE="html"),
        [_payload("tarnish-host"), _payload("emberwrights")],
        declared_slugs=_DECLARED,
    )

    assert outcome.carried == frozenset({"veiled-conclave"})
    assert outcome.unused == frozenset({"tarnish-host"})
    # R06a-fix item 3: `html` genuinely fetches one page per faction, so an `unused` slug here IS
    # evidence that faction's own page answered -- `answers_per_faction` is true.
    assert outcome.answers_per_faction is True


#: The two shapes the same table's payload name takes depending which path acquired it (009 rung
#: R06a, T095/T100): `acquire_wahapedia`'s live path keeps the export's own file name
#: (`Datasheets.csv`); `acquire_from_fixtures` carries the file's bare stem (`Datasheets`) --
#: `pipeline/acquire/wahapedia.py`'s own module docstring names this exact pair, and
#: `_corpus_payloads`'s `Path(name).stem` matching exists because a fix here has drifted between
#: the two shapes before (R05-fix2 item 3, same underlying discrepancy). Parametrized from here so
#: a fix that only holds on one path fails loudly rather than shipping green.
_CSV_PAYLOAD_NAME_STYLES: Final = pytest.mark.parametrize(
    "csv_payload_names",
    [
        pytest.param(("Datasheets.csv", "Datasheets_options.csv"), id="live-directory"),
        pytest.param(("Datasheets", "Datasheets_options"), id="fixtures"),
    ],
)


@_CSV_PAYLOAD_NAME_STYLES
def test_a_declaration_never_leaks_into_carried_under_csv_mode(
    csv_payload_names: tuple[str, str],
) -> None:
    """A csv payload's name is a file name, never a faction slug -- live or fixtures.

    Splitting `carried` on it would put every declared slug there -- exempting every one of them
    from the faction guard (`REC-DETAIL-FACTION-EMPTY`) on a run where the export was read
    perfectly well. `carried` stays empty regardless of which path's payload-naming shape
    acquisition used.
    """
    outcome = resolve_carried_forward(
        _config(),
        [_payload(name) for name in csv_payload_names],
        declared_slugs=_DECLARED,
    )

    assert outcome.carried == frozenset()


@_CSV_PAYLOAD_NAME_STYLES
def test_a_declaration_is_reported_unused_not_dropped_under_csv_mode(
    csv_payload_names: tuple[str, str],
) -> None:
    """009 rung R06a (T095/T100, FR-033): before this rung, a declaration under any arm but
    `html` was dropped here unconditionally -- `outcome.unused` was `frozenset()` regardless of
    what was declared, on both payload-naming shapes (confirmed red against `main` at
    `6b7fd150`: this assertion failed with the extra items being the whole of `_DECLARED`).

    A bulk export answers whole or not at all (FR-032): a run that reaches this point already
    means the export answered, declared faction rows included, so `unused` -- "the declaration
    did nothing this run, a curator may retire it" -- is a true description here too, and reusing
    it is what keeps a declaration visible without minting a new finding code for a condition
    this vocabulary already reports correctly (rule 10).
    """
    outcome = resolve_carried_forward(
        _config(),
        [_payload(name) for name in csv_payload_names],
        declared_slugs=_DECLARED,
    )

    assert outcome.unused == _DECLARED
    assert not (outcome.carried & outcome.unused)
    # R06a-fix item 3: a bulk export answers whole or not at all -- `unused` here is NOT evidence
    # any one declared faction's own page would be reachable, unlike under `html`. A consumer
    # (`pr_body.py`) must be able to tell the two apart before advising a declaration's retirement.
    assert outcome.answers_per_faction is False


def test_no_declaration_is_still_a_true_no_op_under_csv_mode() -> None:
    """An empty declared set stays empty both ways -- a declaration-free build pays nothing for
    this rung's change, exactly as before it."""
    outcome = resolve_carried_forward(
        _config(),
        [_payload("Datasheets.csv")],
        declared_slugs=frozenset(),
    )

    assert outcome.carried == frozenset()
    assert outcome.unused == frozenset()


def test_the_two_halves_are_disjoint_and_cover_the_declared_set_under_html() -> None:
    """A slug in both sets would be carried AND reported as an unused declaration."""
    outcome = resolve_carried_forward(
        _config(WGC_DETAIL_ACQUISITION_MODE="html"),
        [_payload("tarnish-host")],
        declared_slugs=_DECLARED,
    )

    assert not (outcome.carried & outcome.unused)
    assert outcome.carried | outcome.unused == _DECLARED
