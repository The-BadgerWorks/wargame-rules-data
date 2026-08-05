# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the orphan and digest-limitation suite
# (004 task T060), confirmed failing before check_glossary_orphans and glossary_current_digests
# existed: GLS-ORPHANED, the stem-digest fallback of contract §5.1, and the enumerability of the
# digest-less subset from summary-coverage.md (004 FR-023, research D6).
"""The limitation, tested as a limitation.

`contracts/authored-summary-gates.md` §5.1 records something uncomfortable and declines to
engineer around it: **no keyword glossary source exists**. Where the edition publishes no
description for a keyword, the digest is over the normalised keyword stem, which is stable by
construction — so such an entry **never auto-flags for re-review**, forever.

The temptation is to test the happy property ("digests are stable!") and let the consequence go
unstated. This suite tests the consequence directly, because a limitation nobody has written a
failing-if-it-changes test for is a limitation that quietly becomes a bug. Two compensating
controls are tested beside it:

* `GLS-ORPHANED`, so a definition that has fallen out of use is named rather than accumulating
  silently — the only automatic signal a stem-digested entry can ever produce; and
* the digest-less subset being **enumerable from `summary-coverage.md`**, which is what makes
  contract §7 item 4's manual reviewer sweep a thing someone can actually perform.

The digest key here is invented and local to the test. Nothing prints it.
"""

from __future__ import annotations

from pathlib import Path

from pipeline.curate.authored import load_authored
from pipeline.curate.summaries import (
    SummaryStatus,
    digestless_keyword_keys,
    effective_status,
    glossary_current_digests,
    glossary_key,
)
from pipeline.models.curated import CuratedKeyword, KeywordClass
from pipeline.models.findings import Severity
from pipeline.report.catalogue import CATALOGUE
from pipeline.report.coverage import render_summary_coverage
from pipeline.validate.gates import check_glossary_orphans, glossary_summaries, used_keyword_keys
from tests import factories
from tests.enrichment.conftest import weapon

FIXTURE_CURATION = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "curation"

#: Invented, and local to this module. The digest key is a repository secret in a real run; what
#: the assertions below are about is the *comparison*, not the hash, so any key serves.
DIGEST_KEY = b"invented-test-key-not-the-repositorys"


def _entries():  # type: ignore[no-untyped-def]
    return load_authored(FIXTURE_CURATION).glossary_entries


def _snapshot(*keywords: str, weapon_keywords: tuple[str, ...] = ()):  # type: ignore[no-untyped-def]
    datasheet = factories.datasheet("ds-fen-warden", faction_id="f-glimmerfen-covenant").model_copy(
        update={
            "keywords": [
                CuratedKeyword(keyword=keyword, keyword_class=KeywordClass.UNIT)
                for keyword in keywords
            ],
            "weapons": [
                weapon(1, "Fen glaive").model_copy(
                    update={"ability_keywords": list(weapon_keywords)}
                )
            ],
        }
    )
    return factories.snapshot(datasheets=[datasheet], keyword_glossary=_entries())


# --- GLS-ORPHANED (contract §3.1, FR-023) -------------------------------------------------------


def test_a_definition_no_datasheet_or_weapon_uses_is_an_orphan() -> None:
    snapshot = _snapshot(
        "Tidewalk", "Fenlight", weapon_keywords=("SUSTAINED HITS 1", "LETHAL HITS")
    )

    findings = check_glossary_orphans(snapshot, _entries())

    # `void shrouded` and `twin linked` are defined in the fixture set and used by nothing here.
    assert {f.finding_code for f in findings} == {"GLS-ORPHANED"}
    assert [f.entity_refs[0] for f in findings] == [
        "glossary:twin linked",
        "glossary:void shrouded",
    ]


def test_the_orphan_finding_is_advisory_at_its_catalogued_severity() -> None:
    """Editorial debt, not a defect in this candidate — it must never refuse a release."""
    finding = check_glossary_orphans(_snapshot("Tidewalk"), _entries())[0]

    assert finding.severity is Severity.ADVISORY
    assert finding.severity is CATALOGUE["GLS-ORPHANED"].severity


def test_a_definition_used_only_on_a_weapon_profile_is_not_an_orphan() -> None:
    snapshot = _snapshot(weapon_keywords=("TWIN-LINKED",))

    orphans = {f.entity_refs[0] for f in check_glossary_orphans(snapshot, _entries())}

    assert "glossary:twin linked" not in orphans


def test_an_entry_for_an_excluded_faction_keyword_is_not_an_orphan() -> None:
    """Defined-but-excluded is a different thing from unused.

    Calling it an orphan would send a curator to delete a correct entry, so the orphan check
    compares against the **unfiltered** vocabulary while the coverage denominator does not.
    """
    datasheet = factories.datasheet("ds-fen-warden", faction_id="f-glimmerfen-covenant").model_copy(
        update={
            "keywords": [
                CuratedKeyword(keyword="Tidewalk", keyword_class=KeywordClass.FACTION),
            ],
            "weapons": [],
        }
    )
    snapshot = factories.snapshot(datasheets=[datasheet], keyword_glossary=_entries())

    assert "tidewalk" not in used_keyword_keys(snapshot)
    assert "glossary:tidewalk" not in {
        f.entity_refs[0] for f in check_glossary_orphans(snapshot, _entries())
    }


# --- the stem-digest fallback, and what it costs (contract §5.1) ---------------------------------


def test_a_keyword_with_no_published_text_is_digested_over_its_stem() -> None:
    with_text = glossary_current_digests(
        ["lethal hits"],
        mechanic_texts={"lethal hits": "an invented mechanic description"},
        key=DIGEST_KEY,
    )
    without_text = glossary_current_digests(["lethal hits"], key=DIGEST_KEY)

    assert with_text != without_text
    # The stem digest is a pure function of the key, so it is identical every run, forever.
    assert without_text == glossary_current_digests(["lethal hits"], key=DIGEST_KEY)


def test_a_stem_digested_entry_never_auto_flags_for_re_review() -> None:
    """The limitation, stated as an assertion rather than as a comment.

    An entry whose curator stored the stem digest stays `approved` across every run there will
    ever be, because nothing about the keyword's stem can change while the keyword exists. If
    this test ever fails, §5.1 has stopped describing the implementation.
    """
    key = "fenlight"
    summary_key = glossary_key(key)
    stem_digest = glossary_current_digests([key], key=DIGEST_KEY)[summary_key]
    entry = _entries()[key].model_copy(update={"mechanic_digest": stem_digest})
    authored = {summary_key: entry}

    for _run in range(3):
        current = glossary_current_digests([key], key=DIGEST_KEY)
        assert (
            effective_status(summary_key, authored=authored, current_digest=current[summary_key])
            is SummaryStatus.APPROVED
        )


def test_a_keyword_the_source_does_describe_behaves_exactly_like_an_ability_summary() -> None:
    """Where text exists the entry is not exempt — it flags the moment the mechanic moves."""
    key = "lethal hits"
    summary_key = glossary_key(key)
    authored = glossary_summaries(factories.snapshot(), _entries())
    before = glossary_current_digests(
        [key], mechanic_texts={key: "an invented mechanic description"}, key=DIGEST_KEY
    )
    approved = {
        summary_key: authored[summary_key].model_copy(  # type: ignore[attr-defined]
            update={"mechanic_digest": before[summary_key]}
        )
    }
    after = glossary_current_digests(
        [key], mechanic_texts={key: "an invented mechanic description, amended"}, key=DIGEST_KEY
    )

    assert (
        effective_status(summary_key, authored=approved, current_digest=before[summary_key])
        is SummaryStatus.APPROVED
    )
    assert (
        effective_status(summary_key, authored=approved, current_digest=after[summary_key])
        is SummaryStatus.NEEDS_REREVIEW
    )


# --- the subset is enumerable, which is what makes the manual sweep possible ---------------------


def test_the_digestless_subset_is_enumerable_without_the_digest_key() -> None:
    """It is a question about which keywords the source describes, not about any digest value."""
    subset = digestless_keyword_keys(
        ["lethal hits", "sustained hits", "fenlight"],
        mechanic_texts={"lethal hits": "an invented mechanic description"},
    )

    assert subset == ("fenlight", "sustained hits")


def test_the_digestless_subset_is_named_in_summary_coverage_md() -> None:
    snapshot = _snapshot("Tidewalk", "Fenlight")
    subset = digestless_keyword_keys(used_keyword_keys(snapshot))

    rendered = render_summary_coverage(snapshot, authored_summaries={}, digestless_keywords=subset)

    assert "## Glossary entries with no upstream digest" in rendered
    assert "never auto-flag for re-review" in rendered
    for key in subset:
        assert f"- `{key}`" in rendered


def test_the_section_says_so_plainly_when_the_subset_is_empty() -> None:
    rendered = render_summary_coverage(factories.snapshot(), authored_summaries={})

    assert "## Glossary entries with no upstream digest" in rendered
    assert "None." in rendered
