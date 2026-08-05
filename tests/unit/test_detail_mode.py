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
"""Mode-blindness is a property to be proven, not a comment to be believed.

The design's load-bearing claim is that everything below ``acquire`` cannot tell which mode ran.
The only way that stays true is if the two arms are interchangeable *in shape* — same call
signature, same return type — so these tests compare the two arms against each other rather than
checking that each one works in isolation.

Everything here runs offline against a synthetic fixture tree; nothing opens a socket.
"""

from __future__ import annotations

import dataclasses
import inspect
from datetime import UTC, datetime
from pathlib import Path

import pytest

from pipeline.acquire.detail_source import (
    ACQUIRERS,
    READERS,
    acquire_detail,
    acquirer_for,
    read_detail,
    reader_for,
)
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


def test_selecting_html_mode_changes_no_other_configured_value() -> None:
    # The mode selects a parser and nothing else. Anything else moving with it would be a
    # behaviour branch wearing a variable's clothes.
    csv_config = _config()
    html_config = _config(WGC_DETAIL_ACQUISITION_MODE="html")

    csv_values = dataclasses.asdict(csv_config)
    html_values = dataclasses.asdict(html_config)
    differing = {k for k in csv_values if csv_values[k] != html_values[k]}
    assert differing == {"detail_acquisition_mode"}
