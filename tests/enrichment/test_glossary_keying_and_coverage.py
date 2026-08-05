# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the glossary keying and coverage suite
# (004 task T059), confirmed failing before pipeline/validate/gates.py's glossary denominator
# existed: one entry serves every use of a keyword across factions, faction and chapter keywords
# are excluded from the denominator, and an undefined keyword still appears on its datasheets
# unchanged and is named in the report (004 FR-023, US5 acceptance scenarios).
"""One entry per keyword, whatever the keyword looks like where it is printed.

The failure this suite exists to catch is silent by construction. If producer and consumer
normalise a keyword differently — or if the producer counts `SUSTAINED HITS 1` and
`Sustained Hits 2` as two keywords — then the keyword is displayed, the definition exists, and
nothing links them. Nothing errors. So the assertions below are about the *key*, which is the
only place the link can be made or lost.

The second half is the exclusion, and it is the reason keyword classification and the glossary
had to ship together. A faction or chapter keyword is a label for whom the unit belongs to, not
a mechanic anyone could define; counting it would make the glossary's denominator permanently
unreachable and its coverage figure meaningless. **Excluded means excluded, not counted as
missing work** — which is a different statement from "outstanding", and the test says so.
"""

from __future__ import annotations

from pathlib import Path

from pipeline.build.bundle_emit import emit_bundle
from pipeline.config import Gate
from pipeline.curate.authored import load_authored
from pipeline.curate.summaries import glossary_key
from pipeline.models.authored import SummaryClass
from pipeline.models.curated import CuratedKeyword, KeywordClass
from pipeline.normalize.keyword_key import normalize_keyword
from pipeline.report.coverage import render_summary_coverage
from pipeline.schema_validation import validate_bundle
from pipeline.validate.gates import (
    ClassCheck,
    class_coverage,
    glossary_keys,
    glossary_summaries,
    used_keyword_keys,
)
from tests import factories
from tests.enrichment.conftest import weapon

FIXTURE_CURATION = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "curation"


def _entries():  # type: ignore[no-untyped-def]
    return load_authored(FIXTURE_CURATION).glossary_entries


def _datasheet(datasheet_id: str, *, faction_id: str, keywords, weapons=()):  # type: ignore[no-untyped-def]
    return factories.datasheet(datasheet_id, faction_id=faction_id).model_copy(
        update={"keywords": list(keywords), "weapons": list(weapons)}
    )


def _keyword(keyword: str, *, keyword_class: KeywordClass | None = None) -> CuratedKeyword:
    return CuratedKeyword(keyword=keyword, keyword_class=keyword_class)


# --- one entry serves every use, across every variant and every faction --------------------------


def test_casing_spacing_and_punctuation_variants_collapse_to_one_key() -> None:
    variants = ("LETHAL HITS", "Lethal Hits", "lethal  hits", "Lethal-Hits", "lethal.hits")

    assert {normalize_keyword(v).key for v in variants} == {"lethal hits"}


def test_a_numeric_parameter_variant_resolves_to_the_same_entry() -> None:
    """One entry serves a keyword and every numeric variant of it (FR-023)."""
    one = normalize_keyword("SUSTAINED HITS 1")
    two = normalize_keyword("Sustained Hits 2")
    bare = normalize_keyword("sustained hits")

    assert one.key == two.key == bare.key == "sustained hits"
    assert (one.has_numeric_parameter, two.has_numeric_parameter) == (True, True)
    assert bare.has_numeric_parameter is False
    assert glossary_key(one.key) in glossary_summaries(factories.snapshot(), _entries())


def test_one_entry_serves_every_use_of_a_keyword_across_factions() -> None:
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                faction_id="f-glimmerfen-covenant",
                keywords=[_keyword("Tidewalk", keyword_class=KeywordClass.UNIT)],
            ),
            _datasheet(
                "ds-brack-rider",
                faction_id="f-bracklight-host",
                keywords=[_keyword("TIDEWALK", keyword_class=KeywordClass.UNIT)],
            ),
        ]
    )

    keys = used_keyword_keys(snapshot)

    assert keys.count("tidewalk") == 1
    coverage = class_coverage(
        ClassCheck(
            summary_class=SummaryClass.GLOSSARY,
            keys=glossary_keys(snapshot),
            authored=glossary_summaries(snapshot, _entries()),
            gate=Gate.OFF,
        )
    )
    assert (coverage.approved, coverage.total) == (1, 1)


def test_a_keyword_used_only_on_a_weapon_profile_is_counted() -> None:
    """Weapon ability keywords are mechanics by construction; none of them is a faction label."""
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                faction_id="f-glimmerfen-covenant",
                keywords=[],
                weapons=[
                    weapon(1, "Fen glaive").model_copy(
                        update={"ability_keywords": ["TWIN-LINKED", "SUSTAINED HITS 1"]}
                    )
                ],
            )
        ]
    )

    assert used_keyword_keys(snapshot) == ("sustained hits", "twin linked")


# --- the exclusion (contract §4.1) ---------------------------------------------------------------


def test_faction_and_chapter_keywords_are_excluded_from_the_denominator() -> None:
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                faction_id="f-glimmerfen-covenant",
                keywords=[
                    _keyword("GLIMMERFEN COVENANT", keyword_class=KeywordClass.FACTION),
                    _keyword("THORNLIGHT CHORUS", keyword_class=KeywordClass.CHAPTER),
                    _keyword("Tidewalk", keyword_class=KeywordClass.UNIT),
                ],
            )
        ]
    )

    assert used_keyword_keys(snapshot) == ("tidewalk",)


def test_an_unclassified_keyword_is_still_counted() -> None:
    """ "Nobody has classified this yet" is not evidence that it needs no definition."""
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                faction_id="f-glimmerfen-covenant",
                keywords=[_keyword("MIREFEN ENCLAVE"), _keyword("Fenlight")],
            )
        ]
    )

    assert used_keyword_keys(snapshot) == ("fenlight", "mirefen enclave")


# --- an undefined keyword ships unchanged and is reported ---------------------------------------


def test_an_undefined_keyword_still_appears_on_its_datasheet_unchanged() -> None:
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                faction_id="f-glimmerfen-covenant",
                keywords=[_keyword("Duskrail", keyword_class=KeywordClass.UNIT)],
            )
        ],
        keyword_glossary=_entries(),
    )

    bundle = emit_bundle(snapshot, factories.meta())
    validate_bundle(bundle)

    assert [row["keyword"] for row in bundle["datasheetKeywords"]] == ["Duskrail"]
    assert "duskrail" not in {row["keywordKey"] for row in bundle["keywordGlossary"]}


def test_an_undefined_keyword_is_named_in_the_coverage_report() -> None:
    snapshot = factories.snapshot(
        datasheets=[
            _datasheet(
                "ds-fen-warden",
                faction_id="f-glimmerfen-covenant",
                keywords=[_keyword("Duskrail", keyword_class=KeywordClass.UNIT)],
            )
        ]
    )
    coverage = class_coverage(
        ClassCheck(
            summary_class=SummaryClass.GLOSSARY,
            keys=glossary_keys(snapshot),
            authored=glossary_summaries(snapshot, _entries()),
            gate=Gate.OFF,
        )
    )

    assert coverage.outstanding == ("glossary:duskrail",)

    rendered = render_summary_coverage(snapshot, authored_summaries={}, class_coverages=[coverage])
    assert "`glossary:duskrail`" in rendered
    assert "| `glossary` | off | 0 / 1 |" in rendered


def test_only_an_approved_entry_reaches_the_bundle() -> None:
    """`twin linked` is a draft in the fixture set, so it defines nothing yet."""
    snapshot = factories.snapshot(keyword_glossary=_entries())

    bundle = emit_bundle(snapshot, factories.meta())
    validate_bundle(bundle)

    emitted = [row["keywordKey"] for row in bundle["keywordGlossary"]]
    assert emitted == sorted(emitted)
    assert "twin linked" not in emitted
    assert "sustained hits" in emitted
