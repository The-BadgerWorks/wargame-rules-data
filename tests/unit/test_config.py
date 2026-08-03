# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the configuration surface of
# contracts/pipeline-run-interface.md §5 (task T016): documented defaults, layered resolution,
# and sensitive values that never reach a log (Principle 7).
"""Configuration: the documented defaults, the resolution order, and the redaction rule."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from pipeline.config import CONFIG_VARS, REDACTED, Channel, ConfigError, load_config

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
