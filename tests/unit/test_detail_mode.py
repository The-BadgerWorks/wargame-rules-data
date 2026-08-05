# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the WGC_DETAIL_ACQUISITION_MODE
# dispatch (004 task T018): csv routes to the existing export acquirer unchanged, html routes to
# the datacard acquirer, the two signatures and return shapes agree, and an unrecognised mode is
# a configuration error (004 research D1d, plan Architecture).
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

from pipeline.acquire.detail_source import ACQUIRERS, acquire_detail, acquirer_for
from pipeline.acquire.wahapedia import acquire_wahapedia
from pipeline.acquire.wahapedia_html import acquire_wahapedia_html
from pipeline.config import ConfigError, DetailAcquisitionMode, PipelineConfig, load_config
from pipeline.models.source import SourceAcquisition, SourceKey

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "minimal"


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


def test_html_mode_is_not_implemented_yet_and_says_so() -> None:
    config = _config(WGC_DETAIL_ACQUISITION_MODE="html")
    assert config.detail_acquisition_mode is DetailAcquisitionMode.HTML

    with pytest.raises(NotImplementedError, match="T072"):
        acquire_detail(config, fixtures_dir=FIXTURES, offline=True)


def test_selecting_html_mode_changes_no_other_configured_value() -> None:
    # The mode selects a parser and nothing else. Anything else moving with it would be a
    # behaviour branch wearing a variable's clothes.
    csv_config = _config()
    html_config = _config(WGC_DETAIL_ACQUISITION_MODE="html")

    csv_values = dataclasses.asdict(csv_config)
    html_values = dataclasses.asdict(html_config)
    differing = {k for k in csv_values if csv_values[k] != html_values[k]}
    assert differing == {"detail_acquisition_mode"}
