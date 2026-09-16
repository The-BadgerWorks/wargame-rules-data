# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the ability-type mapping table
# (task T063): an explicit mapping onto the closed core|faction|datasheet vocabulary, including
# the observed Cyrillic artefacts; any unmapped value raises DQ-ABILITY-TYPE and is never passed
# through (FR-006, research §0.1).
# AI-Assisted: Claude Code (model: Claude Sonnet 5) - 010 R13 task 4: mapped `psychic ->
# AbilityType.DATASHEET` (it was previously unmapped and raised DQ-ABILITY-TYPE, dropping every
# Psychic binding) and added `source_class`, which reports the source's own classification
# (`wargear`, `wargear-profile`, `primarch`, `psychic`) separately from the closed vocabulary so
# the app can carry it as an optional `abilityClass` tag without moving a single published key.
# AI-Assisted: Claude Code (model: Claude Sonnet 5) - 010 R13 task 13: withdrew the `psychic ->
# AbilityType.DATASHEET` mapping. A live build showed it mints three new ability keys (Orks
# psychic powers) that have no approved summaries, which the publish gate blocks with
# SUM-MISSING; admitting those keys is a curation-and-drafting round of its own, not a pipeline
# change. A Psychic row is once again dropped with DQ-ABILITY-TYPE; `source_class` is unaffected.
"""Map the detail source's classification field onto the contract's closed vocabulary.

The consumer contract's `datasheet_ability.ability_type` is `core | faction | datasheet` and
nothing else. The source's own values are richer, inconsistent, and — for three of them —
Cyrillic scraper artefacts rather than classifications at all: research §0.1 counted
`Special (правая колонка)` 165 times, `Fortification (левая колонка)` 109 times and
`Без заголовка` once. They are real, they are concentrated in this one field, and they mean
"the right-hand column" / "the left-hand column" / "no heading" — layout, not taxonomy.

**The table is explicit and closed, and an unmapped value is never passed through.** A
pass-through would put an untranslated Cyrillic string into a published column that the app
renders, and the app has one evaluator per vocabulary member and no branch for anything else.
So an unmapped value raises `DQ-ABILITY-TYPE`, the binding is dropped, and a human adds a row
here — which is a one-line change, reviewed, and permanent.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final, Literal

from pipeline.models.findings import Finding
from pipeline.models.normalized import AbilityType
from pipeline.report.catalogue import build_finding

#: Source value (casefolded, whitespace-collapsed) -> contract vocabulary member.
#:
#: Everything that is neither a Core ability nor a Faction ability is a *datasheet* ability: the
#: contract's three-way split is about where a player looks the ability up, and `Wargear`,
#: `Primarch`, a right-hand-column special and an unheaded block are all printed on the
#: datasheet itself.
ABILITY_TYPE_MAP: Final[Mapping[str, AbilityType]] = {
    "core": AbilityType.CORE,
    "faction": AbilityType.FACTION,
    "datasheet": AbilityType.DATASHEET,
    "wargear": AbilityType.DATASHEET,
    "wargear profile": AbilityType.DATASHEET,
    "primarch": AbilityType.DATASHEET,
    # "psychic" is deliberately absent: 010 R13 task 4 mapped it onto AbilityType.DATASHEET, but
    # task 13 withdrew that mapping. A live build showed it mints three new ability keys (Orks
    # psychic powers) that have no approved summaries, which the publish gate blocks with
    # SUM-MISSING. Admitting those keys is a curation-and-drafting round of its own, not a
    # pipeline change, so a Psychic row is once again unmapped and raises DQ-ABILITY-TYPE,
    # dropping the binding. `source_class("Psychic")` still reports "psychic" unchanged.
    # The observed Cyrillic scraper artefacts (research §0.1). Layout labels, not taxonomy.
    "special (правая колонка)": AbilityType.DATASHEET,
    "fortification (левая колонка)": AbilityType.DATASHEET,
    "без заголовка": AbilityType.DATASHEET,
}


class AbilityTypeUnmapped(ValueError):
    """A classification value outside the mapping table."""


#: Source value (casefolded, whitespace-collapsed) -> the source's own class tag.
#:
#: A strict subset of `ABILITY_TYPE_MAP`'s keys: `core`, `faction`, `datasheet` and the three
#: Cyrillic layout artefacts carry no class of their own (`None`), because they are not the
#: thing this tag distinguishes — where a Wargear, Wargear profile, Primarch or Psychic entry
#: all collapse to the SAME `AbilityType.DATASHEET`, this is what tells them apart again without
#: moving the published key.
_SOURCE_CLASS_MAP: Final[
    Mapping[str, Literal["wargear", "wargear-profile", "primarch", "psychic"]]
] = {
    "wargear": "wargear",
    "wargear profile": "wargear-profile",
    "primarch": "primarch",
    "psychic": "psychic",
}


def source_class(raw: str) -> Literal["wargear", "wargear-profile", "primarch", "psychic"] | None:
    """The source's own classification, or `None` for core/faction/datasheet and the artefacts.

    Uses the same `_key` normalisation as `coerce_ability_type` so the two functions agree on
    what one raw value means, but this one is total — an unmapped value is simply `None`, never
    a finding, because the class is an OPTIONAL tag and `classify` already reports the raw value
    it cannot place at all.
    """
    return _SOURCE_CLASS_MAP.get(_key(raw))


def _key(raw: str) -> str:
    return " ".join(raw.split()).casefold()


def coerce_ability_type(raw: str) -> AbilityType:
    """Map one classification value, or raise :class:`AbilityTypeUnmapped`.

    The diagnostic states the length of the unmapped value rather than the value itself when
    the value carries non-Latin characters, on the same principle as everywhere else: name the
    shape, not the content.
    """
    try:
        return ABILITY_TYPE_MAP[_key(raw)]
    except KeyError as exc:
        raise AbilityTypeUnmapped(
            f"ability type not in the mapping table ({len(raw)} characters); it is never passed "
            "through to the closed vocabulary — add a row to ABILITY_TYPE_MAP instead"
        ) from exc


def classify(
    raw: str, *, entity_ref: str | None = None
) -> tuple[AbilityType | None, Finding | None]:
    """Map one value, returning a finding instead of raising when it is unmapped.

    The stage form: a single unmapped value should cost one dropped ability binding and one
    advisory finding, not a failed run over a few thousand datasheets.
    """
    try:
        return coerce_ability_type(raw), None
    except AbilityTypeUnmapped:
        return None, build_finding(
            "DQ-ABILITY-TYPE",
            entity_refs=[entity_ref] if entity_ref else (),
            detail={"value_length": len(raw)},
        )
