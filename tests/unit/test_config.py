# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the configuration surface of
# contracts/pipeline-run-interface.md §5 (task T016): documented defaults, layered resolution,
# and sensitive values that never reach a log (Principle 7).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the 004-rules-data-enrichment
# variables (004 task T008): every new default resolves, the mode selector and the three gates
# reject a value outside their enum, every new variable is non-sensitive, and an unknown
# --config key still fails the run.
"""Configuration: the documented defaults, the resolution order, and the redaction rule."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from pipeline.config import (
    CONFIG_VARS,
    REDACTED,
    Channel,
    ConfigError,
    DetailAcquisitionMode,
    Gate,
    load_config,
)

#: Transcribed from contracts/pipeline-run-interface.md §5.
CONTRACT_DEFAULTS = {
    "WGC_MFM_BASE_URL": "https://mfm.warhammer-community.com/en",
    "WGC_MFM_EDITION": "wh40k-11e",
    "WGC_DETAIL_EDITION": "wh40k-10e",
    "WGC_REQUEST_INTERVAL_MS": "2000",
    "WGC_MAX_RETRIES": "2",
    "WGC_DETECT_CRON": "0 9,21 * * *",
    "WGC_DETECT_STALENESS_HOURS": "48",
    "WGC_COVERAGE_MIN_FACTION_RATIO": "0.95",
    "WGC_COVERAGE_MIN_DATASHEET_RATIO": "0.90",
    "WGC_COVERAGE_MIN_PRICED_RATIO": "0.90",
    "WGC_DATA_CHANNEL": "prerelease",
    "WGC_PUBLISHED_MANIFEST_PATH": "manifest.json",
    "WGC_PRERELEASE_MANIFEST_PATH": "prerelease/manifest.json",
    "WGC_SCHEMA_CONTRACT_VERSION": "1",
    "WGC_RESTRICTION_VOCABULARY_VERSION": "1",
    "WGC_SUMMARY_MAX_CHARS": "240",
    "WGC_UNVERIFIED_ESCALATE_RELEASES": "2",
}

#: Transcribed from 004's contracts/authored-summary-gates.md §2-§4 and research D9, and from
#: tasks.md T008 — independently of pipeline/config.py, which is the only way this catches a
#: drift rather than restating one.
ENRICHMENT_DEFAULTS = {
    "WGC_DETAIL_ACQUISITION_MODE": "csv",
    "WGC_GATE_FACTION_RULES": "off",
    "WGC_GATE_DETACHMENT_RULES": "off",
    "WGC_GATE_GLOSSARY": "off",
    "WGC_FACTION_RULE_MAX_CHARS": "240",
    "WGC_DETACHMENT_RULE_MAX_CHARS": "240",
    "WGC_GLOSSARY_MAX_CHARS": "240",
    "WGC_COVERAGE_MIN_COMPOSITION_RATIO": "0.90",
    "WGC_COVERAGE_MIN_OPTION_RATIO": "0.90",
    "WGC_COVERAGE_MIN_KEYWORD_CLASS_RATIO": "0.95",
    "WGC_RATCHET_TOLERANCE_ABILITIES": "0.00",
    "WGC_RATCHET_TOLERANCE_FACTION_RULES": "0.00",
    "WGC_RATCHET_TOLERANCE_DETACHMENT_RULES": "0.00",
    "WGC_RATCHET_TOLERANCE_GLOSSARY": "0.00",
}


def test_every_contract_variable_carries_its_documented_default() -> None:
    declared = {var.env_name: var.default for var in CONFIG_VARS}
    for name, default in CONTRACT_DEFAULTS.items():
        assert declared[name] == default, f"{name} drifted from the contract's default"


def test_the_point_limit_range_is_not_a_pipeline_variable() -> None:
    # Contract §5: the custom point-limit range is read from reference-db-schema.md §3.4, which
    # is the single source of truth shared with the app (C7/R9). Making it configurable here is
    # exactly the silent divergence that resolution closed.
    names = {var.env_name for var in CONFIG_VARS}
    assert not any("POINT_LIMIT" in name for name in names)


def test_defaults_resolve_without_any_environment() -> None:
    config = load_config(env={})
    assert config.request_interval_ms == 2000
    assert config.max_retries == 2
    assert config.data_channel is Channel.PRERELEASE
    assert config.coverage_min_faction_ratio == pytest.approx(0.95)


def test_the_environment_overrides_a_default() -> None:
    config = load_config(env={"WGC_REQUEST_INTERVAL_MS": "5000"})
    assert config.request_interval_ms == 5000


def test_a_config_file_overrides_the_environment(tmp_path: Path) -> None:
    path = tmp_path / "run.json"
    path.write_text(json.dumps({"WGC_REQUEST_INTERVAL_MS": 9000}), encoding="utf-8")
    config = load_config(env={"WGC_REQUEST_INTERVAL_MS": "5000"}, config_path=path)
    assert config.request_interval_ms == 9000, "--config is the per-run override"


def test_the_channel_option_beats_everything() -> None:
    config = load_config(env={"WGC_DATA_CHANNEL": "prerelease"}, channel_override="published")
    assert config.data_channel is Channel.PUBLISHED
    assert config.manifest_path == "manifest.json"


def test_the_channel_selects_only_a_path() -> None:
    prerelease = load_config(env={"WGC_DATA_CHANNEL": "prerelease"})
    published = load_config(env={"WGC_DATA_CHANNEL": "published"})
    assert prerelease.manifest_path == "prerelease/manifest.json"
    assert published.manifest_path == "manifest.json"


@pytest.mark.parametrize(
    "env",
    [
        {"WGC_REQUEST_INTERVAL_MS": "soon"},
        {"WGC_COVERAGE_MIN_FACTION_RATIO": "95"},
        {"WGC_COVERAGE_MIN_FACTION_RATIO": "-1"},
        {"WGC_DATA_CHANNEL": "staging"},
    ],
)
def test_an_invalid_value_is_a_configuration_error(env: dict[str, str]) -> None:
    with pytest.raises(ConfigError):
        load_config(env=env)


def test_an_unknown_config_file_key_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "run.json"
    path.write_text(json.dumps({"WGC_NOT_A_THING": "1"}), encoding="utf-8")
    with pytest.raises(ConfigError, match="unknown configuration key"):
        load_config(env={}, config_path=path)


def test_a_malformed_config_file_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "run.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigError, match="not valid JSON"):
        load_config(env={}, config_path=path)


def test_sensitive_values_are_declared_sensitive() -> None:
    sensitive = {var.env_name for var in CONFIG_VARS if var.sensitive}
    assert sensitive == {"WGC_NOTIFY_WEBHOOK_URL", "WGC_MECHANIC_DIGEST_KEY"}


def test_a_sensitive_value_never_appears_in_the_redacted_view() -> None:
    secret = "https://hooks.example/T000/B000/verysecrettoken"
    config = load_config(env={"WGC_NOTIFY_WEBHOOK_URL": secret})
    rendered = config.redacted()
    assert secret not in json.dumps(rendered)
    assert rendered["WGC_NOTIFY_WEBHOOK_URL"] == f"{REDACTED} (set)"


def test_log_resolved_logs_names_and_non_sensitive_values_only(
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret = "https://hooks.example/T000/B000/verysecrettoken"
    config = load_config(env={"WGC_NOTIFY_WEBHOOK_URL": secret, "WGC_MAX_RETRIES": "4"})

    logger = logging.getLogger("test.config")
    with caplog.at_level(logging.INFO, logger="test.config"):
        config.log_resolved(logger)

    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert "WGC_MAX_RETRIES=4" in logged
    assert secret not in logged
    assert "WGC_NOTIFY_WEBHOOK_URL" in logged, "the NAME is logged; only the value is withheld"


# -- 004-rules-data-enrichment (task T008) ------------------------------------------------


def test_every_enrichment_variable_carries_its_documented_default() -> None:
    declared = {var.env_name: var.default for var in CONFIG_VARS}
    for name, default in ENRICHMENT_DEFAULTS.items():
        assert name in declared, f"{name} is not registered in CONFIG_VARS"
        assert declared[name] == default, f"{name} drifted from the contract's default"


def test_the_enrichment_variables_all_resolve_without_any_environment() -> None:
    config = load_config(env={})

    assert config.detail_acquisition_mode is DetailAcquisitionMode.CSV
    # All three new gates start OFF (FR-029, product-owner decision 2026-08-05): the first
    # enriched release must not be held back by three authoring campaigns that have not started.
    assert config.gate_faction_rules is Gate.OFF
    assert config.gate_detachment_rules is Gate.OFF
    assert config.gate_glossary is Gate.OFF
    assert not config.gate_faction_rules.is_on

    assert config.faction_rule_max_chars == 240
    assert config.detachment_rule_max_chars == 240
    assert config.glossary_max_chars == 240

    assert config.coverage_min_composition_ratio == pytest.approx(0.90)
    assert config.coverage_min_option_ratio == pytest.approx(0.90)
    assert config.coverage_min_keyword_class_ratio == pytest.approx(0.95)

    # Zero tolerance: a campaign may advance but may never silently regress (SC-011).
    assert config.ratchet_tolerance_abilities == pytest.approx(0.0)
    assert config.ratchet_tolerance_faction_rules == pytest.approx(0.0)
    assert config.ratchet_tolerance_detachment_rules == pytest.approx(0.0)
    assert config.ratchet_tolerance_glossary == pytest.approx(0.0)


def test_the_detail_acquisition_mode_accepts_exactly_csv_and_html() -> None:
    assert {mode.value for mode in DetailAcquisitionMode} == {"csv", "html"}
    assert (
        load_config(env={"WGC_DETAIL_ACQUISITION_MODE": "html"}).detail_acquisition_mode
        is DetailAcquisitionMode.HTML
    )


@pytest.mark.parametrize(
    "env",
    [
        {"WGC_DETAIL_ACQUISITION_MODE": "xml"},
        {"WGC_DETAIL_ACQUISITION_MODE": "CSV"},
        {"WGC_DETAIL_ACQUISITION_MODE": ""},
        {"WGC_GATE_FACTION_RULES": "true"},
        {"WGC_GATE_DETACHMENT_RULES": "1"},
        {"WGC_GATE_GLOSSARY": "enabled"},
        {"WGC_COVERAGE_MIN_COMPOSITION_RATIO": "90"},
        {"WGC_RATCHET_TOLERANCE_GLOSSARY": "-0.1"},
        {"WGC_GLOSSARY_MAX_CHARS": "long"},
    ],
)
def test_an_invalid_enrichment_value_is_a_configuration_error(env: dict[str, str]) -> None:
    with pytest.raises(ConfigError):
        load_config(env=env)


def test_a_gate_switches_on_from_configuration_only() -> None:
    config = load_config(env={"WGC_GATE_GLOSSARY": "on"})
    assert config.gate_glossary.is_on
    assert not config.gate_faction_rules.is_on, "each gate is switched independently (SC-013)"


def test_no_enrichment_variable_is_sensitive() -> None:
    # The existing digest key is REUSED for the three new classes rather than a second secret
    # being introduced: one secret, one rotation story (004 plan, Security/configuration gate).
    sensitive = {var.env_name for var in CONFIG_VARS if var.sensitive}
    assert sensitive.isdisjoint(ENRICHMENT_DEFAULTS)
    assert sensitive == {"WGC_NOTIFY_WEBHOOK_URL", "WGC_MECHANIC_DIGEST_KEY"}


def test_an_unknown_config_file_key_still_fails_beside_the_new_ones(tmp_path: Path) -> None:
    path = tmp_path / "run.json"
    path.write_text(
        json.dumps({"WGC_GATE_GLOSSARY": "on", "WGC_GATE_STRATAGEMS": "on"}), encoding="utf-8"
    )
    with pytest.raises(ConfigError, match="unknown configuration key"):
        load_config(env={}, config_path=path)
