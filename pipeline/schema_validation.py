# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the jsonschema loading and
# validation helpers used by curate, validate, and build (task T035), with schema files
# resolved from schemas/ and a cached registry.
# AI-Assisted: Claude Code (model: claude-opus-5) - Registered 004-rules-data-enrichment's eight
# new schemas (004 task T015): two curated-tree collections and the six curation/ files. Three
# further schemas -- datasheet, factions, detachments -- gained optional properties rather than
# new registrations, since they were already registered.
"""JSON Schema loading and validation.

Three schema sets, one loader:

=================  =========================  =====================================
Set                Directory                  Guards against
=================  =========================  =====================================
Curated tree       ``schemas/curated/``       a pipeline emitter drifting from §2
Published bundle   ``schemas/bundle…``        a bundle the consumer cannot ingest
Authored tree      ``schemas/curation/``      a hand-edited ``curation/`` file typo
=================  =========================  =====================================

Every schema sets ``additionalProperties: false`` throughout, so an unmapped field is a hard
failure rather than a silent pass-through — which is the whole reason the schemas exist rather
than trusting the emitters.

Validation collects **every** error, not just the first, and reports each by JSON pointer. A
curator fixing a hand-edited file wants the whole list, not one error per run.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from functools import cache, lru_cache
from pathlib import Path
from typing import Any, Final

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from pipeline.config import repo_root

#: Curated-tree schema files, by the artifact they validate.
CURATED_SCHEMAS: Final[Mapping[str, str]] = {
    "edition": "curated/edition.schema.json",
    "game-sizes": "curated/game-sizes.schema.json",
    "factions": "curated/factions.schema.json",
    "detachments": "curated/detachments.schema.json",
    "enhancements": "curated/enhancements.schema.json",
    "datasheet": "curated/datasheet.schema.json",
    # 004-rules-data-enrichment
    "chapter-keywords": "curated/chapter-keywords.schema.json",
    "keyword-glossary": "curated/keyword-glossary.schema.json",
}

#: Authored-tree schema files, by the ``curation/`` artifact they validate.
CURATION_SCHEMAS: Final[Mapping[str, str]] = {
    "faction-map": "curation/faction-map.schema.json",
    "unit-map": "curation/unit-map.schema.json",
    "unit-aliases": "curation/unit-aliases.schema.json",
    "abilities": "curation/abilities.schema.json",
    "game-sizes": "curation/game-sizes.schema.json",
    "edition-rules": "curation/edition-rules.schema.json",
    "copy-limits": "curation/copy-limits.schema.json",
    "detachment-restrictions": "curation/detachment-restrictions.schema.json",
    "resolutions": "curation/resolutions.schema.json",
    # 004-rules-data-enrichment. `glossary` is the curator's INPUT file and is deliberately a
    # different schema from `keyword-glossary` above, which is the build-stage computed
    # collection: the input carries authoring state, the output carries none of it.
    "faction-rules": "curation/faction-rules.schema.json",
    "detachment-rules": "curation/detachment-rules.schema.json",
    "glossary": "curation/glossary.schema.json",
    "keyword-classes": "curation/keyword-classes.schema.json",
    "composition-overrides": "curation/composition-overrides.schema.json",
    "option-overrides": "curation/option-overrides.schema.json",
    # 006-unit-loadout-fidelity.
    "equipment-overrides": "curation/equipment-overrides.schema.json",
    # 008-wargear-option-completion FR-024 (Product Owner decision 2026-08-17): a curator's
    # explicit declaration that a faction's detail-source page may be carried forward from the
    # previous published version rather than block the whole sweep.
    "carried-forward-factions": "curation/carried-forward-factions.schema.json",
    # 009-csv-migration §3 (Product Owner decision T047, 2026-08-18: hybrid now, full later): a
    # curated per-class acquisition-arm declaration, authored only because a hybrid was chosen.
    "detail-source-authority": "curation/detail-source-authority.schema.json",
}

#: The published bundle schema.
BUNDLE_SCHEMA: Final = "bundle.schema.json"


class SchemaValidationError(ValueError):
    """One or more schema violations, reported by JSON pointer.

    ``errors`` holds the individual messages so a caller can turn them into findings; the
    exception's own message is the human-readable roll-up.
    """

    def __init__(self, source: str, errors: Sequence[str]) -> None:
        self.source = source
        self.errors = list(errors)
        joined = "\n  ".join(self.errors)
        super().__init__(f"{source}: {len(self.errors)} schema violation(s):\n  {joined}")


def schemas_dir() -> Path:
    """The repository's ``schemas/`` directory."""
    return repo_root() / "schemas"


@cache
def load_schema(relative_path: str) -> Mapping[str, Any]:
    """Load and cache one schema document by its path under ``schemas/``."""
    path = schemas_dir() / relative_path
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SchemaValidationError(relative_path, [f"schema file not readable: {path}"]) from exc
    parsed: Any = json.loads(text)
    if not isinstance(parsed, dict):
        raise SchemaValidationError(relative_path, ["schema file must hold a JSON object"])
    return parsed


@lru_cache(maxsize=1)
def registry() -> Registry[Any]:
    """A cached registry of every schema in ``schemas/``, keyed by ``$id``.

    Built once per process so a cross-schema ``$ref`` resolves without re-reading the tree, and
    so no schema resolution ever reaches the network.
    """
    resources: list[tuple[str, Resource[Any]]] = []
    for path in sorted(schemas_dir().rglob("*.schema.json")):
        relative = path.relative_to(schemas_dir()).as_posix()
        contents = load_schema(relative)
        resource: Resource[Any] = Resource.from_contents(
            contents, default_specification=DRAFT202012
        )
        identifier = contents.get("$id")
        resources.append((identifier if isinstance(identifier, str) else relative, resource))
    return Registry().with_resources(resources)


@cache
def validator_for(relative_path: str) -> Draft202012Validator:
    """A cached validator for one schema."""
    return Draft202012Validator(dict(load_schema(relative_path)), registry=registry())


def validate_instance(relative_path: str, instance: object, *, source: str | None = None) -> None:
    """Validate ``instance`` against a schema, raising with every violation found.

    Args:
        relative_path: the schema's path under ``schemas/``.
        instance: the parsed JSON document.
        source: what to name in the error — a file path, typically.

    Raises:
        SchemaValidationError: with one message per violation, each carrying its JSON pointer.
    """
    validator = validator_for(relative_path)
    messages = [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    ]
    if messages:
        raise SchemaValidationError(source or relative_path, messages)


def validate_curated(kind: str, instance: object, *, source: str | None = None) -> None:
    """Validate one curated-tree artifact (``edition``, ``factions``, ``datasheet``, …)."""
    validate_instance(_lookup(CURATED_SCHEMAS, kind, "curated"), instance, source=source)


def validate_authored(kind: str, instance: object, *, source: str | None = None) -> None:
    """Validate one ``curation/`` artifact (``faction-map``, ``abilities``, …)."""
    validate_instance(_lookup(CURATION_SCHEMAS, kind, "curation"), instance, source=source)


def validate_bundle(instance: object, *, source: str | None = None) -> None:
    """Validate the published snapshot bundle."""
    validate_instance(BUNDLE_SCHEMA, instance, source=source)


def _lookup(table: Mapping[str, str], kind: str, label: str) -> str:
    try:
        return table[kind]
    except KeyError as exc:
        known = ", ".join(sorted(table))
        message = f"no {label} schema named {kind!r}; known: {known}"
        raise SchemaValidationError(kind, [message]) from exc
