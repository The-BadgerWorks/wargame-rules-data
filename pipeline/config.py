# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R7 task 1: added the three
# summary-drafting variables (WGC_ANTHROPIC_API_KEY, WGC_DRAFT_MODEL, WGC_REVIEW_MODEL) for the
# Owner's amended standing rule 3. The key is the second SENSITIVE variable in the table and is
# therefore redacted by the existing `redacted()`/`log_resolved()` paths with no change to them;
# it is a separate secret from WGC_MECHANIC_DIGEST_KEY because the two rotate independently.
# AI-Assisted: Claude Code (model: Claude Opus 5) - 010 R5 final-review fix items 4 and 5:
# corrected the 004 block's variable count (thirteen, counted in the tree) and removed the
# `detail_mode` ValueKind member, which no ConfigVar declared and no `_as_*` handler implemented
# after 010 R5 deleted the second detail arm.
# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the configuration surface of
# contracts/pipeline-run-interface.md §5 (task T016): every documented variable with its
# documented default, layered resolution (defaults -> environment -> --config), non-sensitive
# resolved values logged by name and value, sensitive values never logged.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added 004-rules-data-enrichment's fourteen
# variables (004 task T008): the detail-acquisition mode selector, the three per-class summary
# gates, their three length targets, three coverage-collapse ratios, and four ratchet
# tolerances. Every one non-sensitive and defaulted, per contracts/authored-summary-gates.md
# sections 2-4 and research D9.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added require_detail_source (004 T075
# follow-up): the unset default is refused at the point of use rather than interpreted as a
# relative path, so a live run that was never configured reports a configuration error instead of
# an FR-008 partial export.
# AI-Assisted: Claude Code (model: claude-opus-5) - Strip a dotenv value's own quoting as the
# environment is read (004 T076 follow-up): a `.env.local` secret loaded by a hand-rolled
# `KEY=VALUE` split keyed the mechanic digest on a quoted string, which silently re-reviewed
# every approved ability summary rather than failing anything (see `unquote_env_value`).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added WGC_EQUIVALENCE_CHECK_ENABLED (007
# task T014, plan.md Environment gate): the one on/off switch for the Part C equivalence check,
# non-sensitive, defaulted true. The comparison's elision-word set is deliberately NOT a second
# env-driven variable — it is authored, versioned-with-the-check configuration documented in
# docs/configuration.md, per contract §9.1's "not derived from any source page."
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


class Gate(StrEnum):
    """A per-class publication gate (`contracts/authored-summary-gates.md` §3).

    **A gate selects which finding code is emitted, never a severity.** Severity is a property
    of the code and is fixed in :mod:`pipeline.report.catalogue`
    (``validation-report.md`` non-negotiable #1). Off, an entry lacking an approved summary
    emits its class's advisory ``-OUTSTANDING``; on, it emits the blocking ``-MISSING``,
    ``-UNAPPROVED``, or ``-NEEDS-REREVIEW``. Implemented carelessly — as a severity switch —
    this would turn a governance guarantee into a per-run judgement call, which is exactly what
    the contract's §3 exists to prevent.
    """

    OFF = "off"
    ON = "on"

    @property
    def is_on(self) -> bool:
        return self is Gate.ON


ValueKind = Literal["str", "int", "ratio", "channel", "gate", "bool"]


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
        "1000",
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
    # -- 004-rules-data-enrichment ---------------------------------------------------------
    # Thirteen variables, every one non-sensitive and defaulted. The digest key above is
    # **reused** for the three new summary classes rather than a second key being introduced:
    # one secret, one rotation story (004 plan, Security/configuration gate).
    ConfigVar(
        "WGC_GATE_FACTION_RULES",
        "gate_faction_rules",
        "off",
        "gate",
        False,
        "publication gate, faction rule summaries (FR-029)",
    ),
    ConfigVar(
        "WGC_GATE_DETACHMENT_RULES",
        "gate_detachment_rules",
        "off",
        "gate",
        False,
        "publication gate, detachment rule summaries (FR-029)",
    ),
    ConfigVar(
        "WGC_GATE_GLOSSARY",
        "gate_glossary",
        "off",
        "gate",
        False,
        "publication gate, keyword glossary (FR-029)",
    ),
    ConfigVar(
        "WGC_FACTION_RULE_MAX_CHARS",
        "faction_rule_max_chars",
        "1000",
        "int",
        False,
        "summary length target, faction rules; over-length is advisory, never blocking",
    ),
    ConfigVar(
        "WGC_DETACHMENT_RULE_MAX_CHARS",
        "detachment_rule_max_chars",
        "1000",
        "int",
        False,
        "summary length target, detachment rules",
    ),
    ConfigVar(
        "WGC_GLOSSARY_MAX_CHARS",
        "glossary_max_chars",
        "1000",
        "int",
        False,
        "summary length target, glossary entries",
    ),
    ConfigVar(
        "WGC_COVERAGE_MIN_COMPOSITION_RATIO",
        "coverage_min_composition_ratio",
        "0.90",
        "ratio",
        False,
        "collapse threshold, resolved composition (FR-038)",
    ),
    ConfigVar(
        "WGC_COVERAGE_MIN_OPTION_RATIO",
        "coverage_min_option_ratio",
        "0.90",
        "ratio",
        False,
        "collapse threshold, extracted wargear options (FR-038)",
    ),
    ConfigVar(
        "WGC_COVERAGE_MIN_KEYWORD_CLASS_RATIO",
        "coverage_min_keyword_class_ratio",
        "0.95",
        "ratio",
        False,
        "collapse threshold, classified keywords (FR-038)",
    ),
    # The ratchet's *tolerance* is configuration; its severity is not. COV-SUMMARY-REGRESSION
    # is one blocking code across all four classes, with the class in its detail — a per-class
    # code would invite a per-class severity (contracts/authored-summary-gates.md §4).
    ConfigVar(
        "WGC_RATCHET_TOLERANCE_ABILITIES",
        "ratchet_tolerance_abilities",
        "0.00",
        "ratio",
        False,
        "approved-coverage regression tolerance, abilities (FR-030)",
    ),
    ConfigVar(
        "WGC_RATCHET_TOLERANCE_FACTION_RULES",
        "ratchet_tolerance_faction_rules",
        "0.00",
        "ratio",
        False,
        "approved-coverage regression tolerance, faction rules (FR-030)",
    ),
    ConfigVar(
        "WGC_RATCHET_TOLERANCE_DETACHMENT_RULES",
        "ratchet_tolerance_detachment_rules",
        "0.00",
        "ratio",
        False,
        "approved-coverage regression tolerance, detachment rules (FR-030)",
    ),
    ConfigVar(
        "WGC_RATCHET_TOLERANCE_GLOSSARY",
        "ratchet_tolerance_glossary",
        "0.00",
        "ratio",
        False,
        "approved-coverage regression tolerance, glossary (FR-030)",
    ),
    # -- 006-unit-loadout-fidelity ----------------------------------------------------------
    # One variable, and deliberately only one. The 2026-08-09 clarification is specific:
    # resolved-option coverage is RATCHETED WITH NO ABSOLUTE CEILING, so source-wording drift
    # cannot wedge a release ahead of a parser fix. A threshold knob would be exactly that
    # ceiling, so none is added — this is the tolerance the ratchet allows either side of the
    # previous PUBLISHED version's percent, and it joins the four above unchanged in shape.
    #
    # `loadout.default_equipment` gets no tolerance because it gets no ratchet in the first
    # extended release: there is nothing yet to compare it against, and inventing a
    # first-release threshold would be the ceiling the clarification rules out (research D4).
    ConfigVar(
        "WGC_RATCHET_TOLERANCE_OPTIONS",
        "ratchet_tolerance_options",
        "0.00",
        "ratio",
        False,
        "resolved-option coverage regression tolerance (006 FR-022)",
    ),
    # -- 007-loadout-display-fidelity ---------------------------------------------------------
    # One variable, deliberately: the Part C equivalence check's on/off switch. The comparison's
    # elision-word set is NOT a second variable here — it is authored configuration versioned
    # with the check itself (docs/configuration.md), because contract §9.1 requires it to be
    # "not derived from any source page," which is exactly what an env override would risk.
    ConfigVar(
        "WGC_EQUIVALENCE_CHECK_ENABLED",
        "equivalence_check_enabled",
        "true",
        "bool",
        False,
        "on/off switch, the build-time rendering equivalence check (007 FR-019..FR-022)",
    ),
    # -- 008-wargear-option-completion ---------------------------------------------------------
    # One variable, and only as a consequence of the Product Owner's two-step ruling
    # (Clarifications 2026-08-15 Q2, FR-021): `loadout.default_equipment` joins the ratcheted set
    # on the same terms `loadout.options_resolved` already does. Same shape as the five
    # `WGC_RATCHET_TOLERANCE_*` variables above -- no absolute threshold or floor is introduced
    # for either figure; this is only the proportion the ratchet allows either side of the
    # previous PUBLISHED version's percent, identically to `WGC_RATCHET_TOLERANCE_OPTIONS`.
    ConfigVar(
        "WGC_RATCHET_TOLERANCE_EQUIPMENT",
        "ratchet_tolerance_equipment",
        "0.00",
        "ratio",
        False,
        "default-equipment coverage regression tolerance (008 FR-021)",
    ),
    # -- 010-csv-cutover, round 7: machine-drafted summaries -----------------------------------
    # Three variables, for the Owner's amended standing rule 3 (2026-09-14): a summary may be
    # drafted by the pipeline's own API client from the export's rules text and reviewed by a
    # second model pass before the Owner approves it. The key is a SECOND secret rather than a
    # reuse of WGC_MECHANIC_DIGEST_KEY, because the two rotate for different reasons and on
    # different authority -- the digest key's rotation re-baselines every approved summary
    # (010 R7), while this credential's rotation changes nothing about the published data.
    ConfigVar(
        "WGC_ANTHROPIC_API_KEY",
        "anthropic_api_key",
        "",
        "str",
        True,
        "SENSITIVE: credential for the summary drafting client (secret store only)",
    ),
    # The two passes are deliberately different models: a second pass by the same model reviews
    # its own reasoning, which is not the independent check standing rule 3 asks for.
    ConfigVar(
        "WGC_DRAFT_MODEL",
        "draft_model",
        "claude-opus-5",
        "str",
        False,
        "model id for the summary drafting pass (standing rule 3, amended 2026-09-14)",
    ),
    ConfigVar(
        "WGC_REVIEW_MODEL",
        "review_model",
        "claude-sonnet-5",
        "str",
        False,
        "model id for the summary reviewing pass (standing rule 3, amended 2026-09-14)",
    ),
    # 010 R7c: a second transport for the drafting client that shells out to the Claude Code CLI
    # in print mode, so a drafting run bills the Owner's subscription instead of the messages API
    # above. "api" keeps the original transport reachable without a code change.
    ConfigVar(
        "WGC_DRAFT_TRANSPORT",
        "draft_transport",
        "cli",
        "str",
        False,
        "transport for the drafting client: cli (subscription) or api (billed messages API)",
    ),
    ConfigVar(
        "WGC_CLAUDE_CLI",
        "claude_cli",
        "claude",
        "str",
        False,
        "executable name/path for the Claude Code CLI transport",
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
    gate_faction_rules: Gate
    gate_detachment_rules: Gate
    gate_glossary: Gate
    faction_rule_max_chars: int
    detachment_rule_max_chars: int
    glossary_max_chars: int
    coverage_min_composition_ratio: float
    coverage_min_option_ratio: float
    coverage_min_keyword_class_ratio: float
    ratchet_tolerance_abilities: float
    ratchet_tolerance_faction_rules: float
    ratchet_tolerance_detachment_rules: float
    ratchet_tolerance_glossary: float
    ratchet_tolerance_options: float
    equivalence_check_enabled: bool
    ratchet_tolerance_equipment: float
    anthropic_api_key: str
    draft_model: str
    review_model: str
    draft_transport: str
    claude_cli: str

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

    def require_detail_source(self) -> str:
        """``detail_source_url``, refusing the unset default before it is interpreted.

        ``WGC_DETAIL_SOURCE_URL`` defaults to empty and has done since `002` shipped, because a
        fixture build never reads it and a live one must state it deliberately. What was missing
        was the refusal: an empty location parsed as a *relative path*, which is the process's
        working directory, so a live run with the variable unset went looking for the export in
        the repository checkout and reported the first file it did not find there as ``the detail
        source's export is missing Abilities.csv ... (FR-008)``. That diagnostic is true of what
        the code did and wrong about what happened: it names an upstream partial export when the
        actual fault is local and configural.

        FR-008's rule is untouched — *a partial export is a failed acquisition*. This says only
        that a source which was never configured is not a partial one, and belongs to
        ``ExitCode.CONFIG_ERROR`` rather than to ``ExitCode.SOURCE_UNAVAILABLE``.

        Raises:
            ConfigError: the variable is unset or blank.
        """
        location = self.detail_source_url.strip()
        if not location:
            raise ConfigError(
                "WGC_DETAIL_SOURCE_URL is not set, so a live acquisition has no source to read. "
                "Set it to the export directory (see docs/configuration.md); or run against a "
                "fixture set, which never reads it."
            )
        return location


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


def unquote_env_value(value: str) -> str:
    """Drop one matched pair of surrounding quotes, as every ``.env`` reader does.

    **Why this exists, in one incident.** A local run is configured from a ``.env.local`` file
    whose secret is written ``WGC_MECHANIC_DIGEST_KEY="…"``, because that is how a secret is
    written in a dotenv file. A hand-rolled ``KEY=VALUE`` loader that splits on the first ``=``
    and stops there puts the **quotes into the value**, so the process keyed its HMAC on a
    64-character secret wrapped in two double quotes — a different key. Nothing failed. Every
    mechanic digest simply came out different from the one the curation was authored under, and
    a build reported that *every single* approved ability summary needed re-review: a phantom
    1 703-record campaign that was very nearly scheduled (see
    ``reports/churn-dry-run/2026-08-05.md``, whose 203 is the real figure).

    Quoting is part of the dotenv convention rather than part of the value, and a configuration
    value that begins and ends with the same quote character has never once meant to carry it.
    Stripping it here — where the environment is read, once, for every variable — is what makes
    the two ways of loading the same file produce the same run.
    """
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


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


#: The two transports a caller may select for the drafting client. Read here rather than in
#: `pipeline.summaries` so `config.py` stays the only place a config value's shape is validated.
_DRAFT_TRANSPORTS: Final[frozenset[str]] = frozenset({"cli", "api"})


def _as_draft_transport(raw: Mapping[str, str], env_name: str) -> str:
    text = raw[env_name]
    if text not in _DRAFT_TRANSPORTS:
        allowed = ", ".join(sorted(_DRAFT_TRANSPORTS))
        raise ConfigError(f"{env_name} must be one of {allowed}, got {text!r}")
    return text


def _as_gate(raw: Mapping[str, str], env_name: str) -> Gate:
    text = raw[env_name]
    try:
        return Gate(text)
    except ValueError as exc:
        allowed = ", ".join(gate.value for gate in Gate)
        raise ConfigError(f"{env_name} must be one of {allowed}, got {text!r}") from exc


#: Accepted spellings, lower-cased before lookup. Deliberately not `bool(text)` — every
#: non-empty string is truthy in Python, which would make `WGC_EQUIVALENCE_CHECK_ENABLED=false`
#: turn the check ON.
_BOOL_VALUES: Final[Mapping[str, bool]] = {
    "true": True,
    "false": False,
    "1": True,
    "0": False,
}


def _as_bool(raw: Mapping[str, str], env_name: str) -> bool:
    text = raw[env_name]
    try:
        return _BOOL_VALUES[text.strip().lower()]
    except KeyError as exc:
        allowed = ", ".join(sorted(_BOOL_VALUES))
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
            # Unquoted here rather than per-variable: a dotenv artefact is a property of *how the
            # environment was loaded*, not of which variable it reached, and a quoted `"5000"`
            # would fail `_as_int` while a quoted secret would fail nothing at all (see
            # `unquote_env_value`). The `--config` file needs no equivalent — JSON has already
            # resolved its own quoting by the time `_read_config_file` returns.
            raw[var.env_name] = unquote_env_value(environ[var.env_name])
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
        gate_faction_rules=_as_gate(raw, "WGC_GATE_FACTION_RULES"),
        gate_detachment_rules=_as_gate(raw, "WGC_GATE_DETACHMENT_RULES"),
        gate_glossary=_as_gate(raw, "WGC_GATE_GLOSSARY"),
        faction_rule_max_chars=_as_int(raw, "WGC_FACTION_RULE_MAX_CHARS"),
        detachment_rule_max_chars=_as_int(raw, "WGC_DETACHMENT_RULE_MAX_CHARS"),
        glossary_max_chars=_as_int(raw, "WGC_GLOSSARY_MAX_CHARS"),
        coverage_min_composition_ratio=_as_ratio(raw, "WGC_COVERAGE_MIN_COMPOSITION_RATIO"),
        coverage_min_option_ratio=_as_ratio(raw, "WGC_COVERAGE_MIN_OPTION_RATIO"),
        coverage_min_keyword_class_ratio=_as_ratio(raw, "WGC_COVERAGE_MIN_KEYWORD_CLASS_RATIO"),
        ratchet_tolerance_abilities=_as_ratio(raw, "WGC_RATCHET_TOLERANCE_ABILITIES"),
        ratchet_tolerance_faction_rules=_as_ratio(raw, "WGC_RATCHET_TOLERANCE_FACTION_RULES"),
        ratchet_tolerance_detachment_rules=_as_ratio(raw, "WGC_RATCHET_TOLERANCE_DETACHMENT_RULES"),
        ratchet_tolerance_glossary=_as_ratio(raw, "WGC_RATCHET_TOLERANCE_GLOSSARY"),
        ratchet_tolerance_options=_as_ratio(raw, "WGC_RATCHET_TOLERANCE_OPTIONS"),
        equivalence_check_enabled=_as_bool(raw, "WGC_EQUIVALENCE_CHECK_ENABLED"),
        ratchet_tolerance_equipment=_as_ratio(raw, "WGC_RATCHET_TOLERANCE_EQUIPMENT"),
        anthropic_api_key=_as_str(raw, "WGC_ANTHROPIC_API_KEY"),
        draft_model=_as_str(raw, "WGC_DRAFT_MODEL"),
        review_model=_as_str(raw, "WGC_REVIEW_MODEL"),
        draft_transport=_as_draft_transport(raw, "WGC_DRAFT_TRANSPORT"),
        claude_cli=_as_str(raw, "WGC_CLAUDE_CLI"),
    )
