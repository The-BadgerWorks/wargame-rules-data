# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the configuration surface of
# contracts/pipeline-run-interface.md §5 (task T016): every documented variable with its
# documented default, layered resolution (defaults -> environment -> --config), non-sensitive
# resolved values logged by name and value, sensitive values never logged.
"""Pipeline configuration.

Every variable in ``contracts/pipeline-run-interface.md`` §5 appears here exactly once, with
the default that contract documents. Resolution is layered, most general first:

1. the documented default,
2. the process environment (repository variables in CI),
3. the ``--config`` file, which is the per-run override a curator reaches for locally.

Resolved **non-sensitive** names and values are logged (Principle 7, FR-055 diagnostics).
**Sensitive** values are never logged — only whether they are set.

Two things are deliberately *not* configuration:

* The custom point-limit range. ``reference-db-schema.md`` §3.4 declares ``500``..``5000`` as
  the single source of truth shared with the consuming app (C7/R9). The pipeline reads it from
  the contract; making it a variable is exactly the silent divergence that resolution closed.
* The channel's *behaviour*. ``WGC_DATA_CHANNEL`` selects a path and a tag prefix and nothing
  else — there is no branch on channel name below the CLI entry point (plan.md Environment
  gate).
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final, Literal

LOGGER: Final = logging.getLogger("pipeline.config")

#: Placeholder printed in place of any sensitive value. The value itself never reaches a log.
REDACTED: Final = "<redacted>"


class ConfigError(ValueError):
    """An invalid, unknown, or unparseable configuration value.

    Raised during resolution and mapped by the CLI to ``ExitCode.CONFIG_ERROR`` (60).
    """


class Channel(StrEnum):
    """The two consumer-facing channels. Identical structure; different path only (FR-047)."""

    PRERELEASE = "prerelease"
    PUBLISHED = "published"


ValueKind = Literal["str", "int", "ratio", "channel"]


@dataclass(frozen=True, slots=True)
class ConfigVar:
    """One documented configuration variable (contract §5)."""

    env_name: str
    attr: str
    default: str
    kind: ValueKind
    sensitive: bool
    purpose: str


#: The contract's §5 table, in the contract's order. Adding a variable here is a contract
#: change, not an implementation detail.
CONFIG_VARS: Final[tuple[ConfigVar, ...]] = (
    ConfigVar(
        "WGC_MFM_BASE_URL",
        "mfm_base_url",
        "https://mfm.warhammer-community.com/en",
        "str",
        False,
        "points source",
    ),
    ConfigVar(
        "WGC_DETAIL_SOURCE_URL",
        "detail_source_url",
        "",
        "str",
        False,
        "datasheet-detail source (export location; must be set for a live acquisition)",
    ),
    ConfigVar(
        "WGC_MFM_EDITION", "mfm_edition", "wh40k-11e", "str", False, "declared points edition"
    ),
    ConfigVar(
        "WGC_DETAIL_EDITION", "detail_edition", "wh40k-10e", "str", False, "declared detail edition"
    ),
    ConfigVar(
        "WGC_REQUEST_INTERVAL_MS",
        "request_interval_ms",
        "2000",
        "int",
        False,
        "polite per-host request interval (FR-007)",
    ),
    ConfigVar(
        "WGC_MAX_RETRIES",
        "max_retries",
        "2",
        "int",
        False,
        "retry ceiling; never escalates on refusal (FR-007)",
    ),
    ConfigVar("WGC_DETECT_CRON", "detect_cron", "0 9,21 * * *", "str", False, "detection schedule"),
    ConfigVar(
        "WGC_DETECT_STALENESS_HOURS",
        "detect_staleness_hours",
        "48",
        "int",
        False,
        "staleness alarm (FR-055)",
    ),
    ConfigVar(
        "WGC_COVERAGE_MIN_FACTION_RATIO",
        "coverage_min_faction_ratio",
        "0.95",
        "ratio",
        False,
        "collapse threshold, factions (FR-009)",
    ),
    ConfigVar(
        "WGC_COVERAGE_MIN_DATASHEET_RATIO",
        "coverage_min_datasheet_ratio",
        "0.90",
        "ratio",
        False,
        "collapse threshold, datasheets (FR-009)",
    ),
    ConfigVar(
        "WGC_COVERAGE_MIN_PRICED_RATIO",
        "coverage_min_priced_ratio",
        "0.90",
        "ratio",
        False,
        "collapse threshold, priced datasheets (FR-009)",
    ),
    ConfigVar(
        "WGC_DATA_CHANNEL", "data_channel", "prerelease", "channel", False, "channel selector"
    ),
    ConfigVar(
        "WGC_PUBLISHED_MANIFEST_PATH",
        "published_manifest_path",
        "manifest.json",
        "str",
        False,
        "Pages path, published channel",
    ),
    ConfigVar(
        "WGC_PRERELEASE_MANIFEST_PATH",
        "prerelease_manifest_path",
        "prerelease/manifest.json",
        "str",
        False,
        "Pages path, pre-release channel",
    ),
    ConfigVar(
        "WGC_SCHEMA_CONTRACT_VERSION",
        "schema_contract_version",
        "1",
        "int",
        False,
        "stamped into snapshotMeta; MAJOR of reference-db-schema.md (FR-030)",
    ),
    ConfigVar(
        "WGC_RESTRICTION_VOCABULARY_VERSION",
        "restriction_vocabulary_version",
        "1",
        "int",
        False,
        "stamped into snapshotMeta",
    ),
    ConfigVar(
        "WGC_SUMMARY_MAX_CHARS",
        "summary_max_chars",
        "240",
        "int",
        False,
        "summary length target (FR-022)",
    ),
    ConfigVar(
        "WGC_UNVERIFIED_ESCALATE_RELEASES",
        "unverified_escalate_releases",
        "2",
        "int",
        False,
        "consecutive releases before escalation",
    ),
    ConfigVar(
        "WGC_NOTIFY_WEBHOOK_URL",
        "notify_webhook_url",
        "",
        "str",
        True,
        "SENSITIVE: notification and alert destination (secret store only)",
    ),
    ConfigVar(
        "WGC_MECHANIC_DIGEST_KEY",
        "mechanic_digest_key",
        "",
        "str",
        True,
        "SENSITIVE: HMAC key for the keyed mechanic digest (research D6, C6/R8)",
    ),
)

_BY_ENV_NAME: Final[Mapping[str, ConfigVar]] = {var.env_name: var for var in CONFIG_VARS}


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """The resolved configuration for one run."""

    mfm_base_url: str
    detail_source_url: str
    mfm_edition: str
    detail_edition: str
    request_interval_ms: int
    max_retries: int
    detect_cron: str
    detect_staleness_hours: int
    coverage_min_faction_ratio: float
    coverage_min_datasheet_ratio: float
    coverage_min_priced_ratio: float
    data_channel: Channel
    published_manifest_path: str
    prerelease_manifest_path: str
    schema_contract_version: int
    restriction_vocabulary_version: int
    summary_max_chars: int
    unverified_escalate_releases: int
    notify_webhook_url: str
    mechanic_digest_key: str

    @property
    def manifest_path(self) -> str:
        """The Pages manifest path for the active channel — the only channel difference."""
        if self.data_channel is Channel.PUBLISHED:
            return self.published_manifest_path
        return self.prerelease_manifest_path

    def redacted(self) -> dict[str, str]:
        """Every variable as ``env_name -> printable value``, sensitive values replaced.

        A sensitive variable reports only whether it is set, never its value (Principle 7).
        """
        out: dict[str, str] = {}
        for var in CONFIG_VARS:
            value = getattr(self, var.attr)
            if var.sensitive:
                out[var.env_name] = f"{REDACTED} (set)" if value else f"{REDACTED} (unset)"
            else:
                out[var.env_name] = str(value)
        return out

    def log_resolved(self, logger: logging.Logger | None = None) -> None:
        """Log the resolved configuration: names and values, sensitive values redacted."""
        log = logger if logger is not None else LOGGER
        for env_name, printable in self.redacted().items():
            log.info("config %s=%s", env_name, printable)


def repo_root() -> Path:
    """The repository root — the parent of the ``pipeline`` package."""
    return Path(__file__).resolve().parents[1]


def _read_config_file(path: Path) -> dict[str, str]:
    """Read a ``--config`` JSON file of ``WGC_*`` keys to scalar values."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"config file not readable: {path}") from exc
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"config file is not valid JSON: {path}") from exc
    if not isinstance(parsed, dict):
        raise ConfigError(f"config file must hold a JSON object of WGC_* keys: {path}")

    values: dict[str, str] = {}
    for key, value in parsed.items():
        if key not in _BY_ENV_NAME:
            known = ", ".join(sorted(_BY_ENV_NAME))
            raise ConfigError(f"unknown configuration key {key!r} in {path}; known keys: {known}")
        if isinstance(value, bool) or not isinstance(value, str | int | float):
            raise ConfigError(f"configuration value for {key} must be a string or a number")
        values[key] = str(value)
    return values


def _as_str(raw: Mapping[str, str], env_name: str) -> str:
    return raw[env_name]


def _as_int(raw: Mapping[str, str], env_name: str) -> int:
    text = raw[env_name]
    try:
        return int(text)
    except ValueError as exc:
        raise ConfigError(f"{env_name} must be an integer, got {text!r}") from exc


def _as_ratio(raw: Mapping[str, str], env_name: str) -> float:
    text = raw[env_name]
    try:
        value = float(text)
    except ValueError as exc:
        raise ConfigError(f"{env_name} must be a number between 0 and 1, got {text!r}") from exc
    if not 0.0 <= value <= 1.0:
        raise ConfigError(f"{env_name} must be between 0 and 1, got {value}")
    return value


def _as_channel(raw: Mapping[str, str], env_name: str) -> Channel:
    text = raw[env_name]
    try:
        return Channel(text)
    except ValueError as exc:
        allowed = ", ".join(c.value for c in Channel)
        raise ConfigError(f"{env_name} must be one of {allowed}, got {text!r}") from exc


def load_config(
    env: Mapping[str, str] | None = None,
    config_path: Path | str | None = None,
    channel_override: str | None = None,
) -> PipelineConfig:
    """Resolve the configuration: defaults, then environment, then ``--config``.

    ``channel_override`` is the CLI's ``--channel`` option, which is the most specific input of
    all and therefore applied last.

    Raises:
        ConfigError: an unknown key, an unparseable value, or an out-of-range ratio.
    """
    environ: Mapping[str, str] = os.environ if env is None else env

    raw: dict[str, str] = {var.env_name: var.default for var in CONFIG_VARS}
    for var in CONFIG_VARS:
        if var.env_name in environ:
            raw[var.env_name] = environ[var.env_name]
    if config_path is not None:
        raw.update(_read_config_file(Path(config_path)))
    if channel_override is not None:
        raw["WGC_DATA_CHANNEL"] = channel_override

    return PipelineConfig(
        mfm_base_url=_as_str(raw, "WGC_MFM_BASE_URL"),
        detail_source_url=_as_str(raw, "WGC_DETAIL_SOURCE_URL"),
        mfm_edition=_as_str(raw, "WGC_MFM_EDITION"),
        detail_edition=_as_str(raw, "WGC_DETAIL_EDITION"),
        request_interval_ms=_as_int(raw, "WGC_REQUEST_INTERVAL_MS"),
        max_retries=_as_int(raw, "WGC_MAX_RETRIES"),
        detect_cron=_as_str(raw, "WGC_DETECT_CRON"),
        detect_staleness_hours=_as_int(raw, "WGC_DETECT_STALENESS_HOURS"),
        coverage_min_faction_ratio=_as_ratio(raw, "WGC_COVERAGE_MIN_FACTION_RATIO"),
        coverage_min_datasheet_ratio=_as_ratio(raw, "WGC_COVERAGE_MIN_DATASHEET_RATIO"),
        coverage_min_priced_ratio=_as_ratio(raw, "WGC_COVERAGE_MIN_PRICED_RATIO"),
        data_channel=_as_channel(raw, "WGC_DATA_CHANNEL"),
        published_manifest_path=_as_str(raw, "WGC_PUBLISHED_MANIFEST_PATH"),
        prerelease_manifest_path=_as_str(raw, "WGC_PRERELEASE_MANIFEST_PATH"),
        schema_contract_version=_as_int(raw, "WGC_SCHEMA_CONTRACT_VERSION"),
        restriction_vocabulary_version=_as_int(raw, "WGC_RESTRICTION_VOCABULARY_VERSION"),
        summary_max_chars=_as_int(raw, "WGC_SUMMARY_MAX_CHARS"),
        unverified_escalate_releases=_as_int(raw, "WGC_UNVERIFIED_ESCALATE_RELEASES"),
        notify_webhook_url=_as_str(raw, "WGC_NOTIFY_WEBHOOK_URL"),
        mechanic_digest_key=_as_str(raw, "WGC_MECHANIC_DIGEST_KEY"),
    )
