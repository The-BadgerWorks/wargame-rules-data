# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the ability-type mapping table
# (task T063): an explicit mapping onto the closed core|faction|datasheet vocabulary, including
# the observed Cyrillic artefacts; any unmapped value raises DQ-ABILITY-TYPE and is never passed
# through (FR-006, research §0.1).
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
from typing import Final

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
    # The observed Cyrillic scraper artefacts (research §0.1). Layout labels, not taxonomy.
    "special (правая колонка)": AbilityType.DATASHEET,
    "fortification (левая колонка)": AbilityType.DATASHEET,
    "без заголовка": AbilityType.DATASHEET,
}


class AbilityTypeUnmapped(ValueError):
    """A classification value outside the mapping table."""


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


def classify(raw: str, *, entity_ref: str | None = None) -> tuple[AbilityType | None, Finding | None]:
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
