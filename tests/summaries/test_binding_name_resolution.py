# AI-Assisted: Claude Code (model: claude-opus-5) - Failing-first test for 010 R6: the digest
# join in `compute_current_digests` reads the binding's own `name` column, which is empty on
# every Core and on 1437 of 1442 Faction rows of the live CSV export — so those keys were
# digested for nobody, exactly as `assemble` bound no key for them. Invented ids, names and
# prose throughout.
"""``compute_current_digests`` keys on the same resolved name ``assemble`` binds.

The two are one rule stated twice: if the digest join and the key assembly disagree about what a
nameless binding is called, a key exists with no digest (never flags for re-review) or a digest
exists for a key nothing binds (never read). Both read
:func:`pipeline.curate.summaries.ability_name_index`.
"""

from __future__ import annotations

import pytest

from pipeline.curate.summaries import ability_name_index, compute_current_digests
from pipeline.normalize.mechanic_digest import mechanic_digest
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text

_KEY = b"binding-name-resolution-test-key"

_ABILITIES_HEADER = "id|name|legend|faction_id|description|\n"
_BINDINGS_HEADER = "datasheet_id|line|ability_id|model|name|description|type|parameter|\n"

#: Invented placeholder prose (research D10) — never the publisher's wording.
_JOINED_DESCRIPTION = "Invented placeholder prose stating one joined mechanic, for this test."
_LOCAL_DESCRIPTION = "Invented placeholder prose stating one datasheet-local mechanic instead."


def _detail(*, bindings: str, abilities: str) -> dict[str, CsvReadResult]:
    return {
        "Datasheets_abilities.csv": read_text(
            "Datasheets_abilities.csv", _BINDINGS_HEADER + bindings
        ),
        "Abilities.csv": read_text("Abilities.csv", _ABILITIES_HEADER + abilities),
    }


def test_the_index_maps_an_ability_id_to_its_stripped_name() -> None:
    index = ability_name_index(
        _detail(
            bindings="",
            abilities=f"A1|<b>Tidal Step</b>||TF|{_JOINED_DESCRIPTION}|\n",
        )
    )

    assert index == {"A1": "Tidal Step"}


def test_the_index_is_read_only_because_every_datasheet_shares_it() -> None:
    index = ability_name_index(
        _detail(bindings="", abilities=f"A1|Tidal Step||TF|{_JOINED_DESCRIPTION}|\n")
    )

    with pytest.raises(TypeError):
        index["A1"] = "Harbour Watch"  # type: ignore[index]


def test_a_nameless_core_binding_is_digested_under_its_joined_key() -> None:
    digests = compute_current_digests(
        _detail(
            bindings="ds1|1|A1||||Core||\n",
            abilities=f"A1|Tidal Step||TF|{_JOINED_DESCRIPTION}|\n",
        ),
        key=_KEY,
    )

    assert digests == {"core:tidal-step": mechanic_digest(_JOINED_DESCRIPTION, key=_KEY)}


def test_a_named_bindings_digest_is_unchanged_by_the_join() -> None:
    """The regression direction: a binding that states its own name keeps its own text."""
    digests = compute_current_digests(
        _detail(
            bindings=f"ds1|1|A1||Harbour Watch|{_LOCAL_DESCRIPTION}|Datasheet||\n",
            abilities=f"A1|Tidal Step||TF|{_JOINED_DESCRIPTION}|\n",
        ),
        key=_KEY,
    )

    assert digests == {"datasheet:harbour-watch": mechanic_digest(_LOCAL_DESCRIPTION, key=_KEY)}


def test_an_unresolvable_nameless_binding_produces_no_digest() -> None:
    digests = compute_current_digests(
        _detail(
            bindings="ds1|1|A9||||Core||\n",
            abilities=f"A1|Tidal Step||TF|{_JOINED_DESCRIPTION}|\n",
        ),
        key=_KEY,
    )

    assert digests == {}
