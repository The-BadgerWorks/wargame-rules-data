# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the FR-005/FR-006 cause-attribution
# test (009 task T033): each hypothesis is tested against its own synthetic fixture rows (CM01,
# T007; CM02, T008), asserting both whether the row resolves and which FR-005 kind the outcome
# belongs to, per `tools/diagnosis_causes.HYPOTHESIS_KIND`.
"""FR-006's three named hypotheses, each proven against a fixture rather than assumed.

**(a) markup-form asymmetry** — CM01's five rows (T007): a space-variant open tag, a
space-variant close tag, an unterminated tag, a self-closing space variant, and the
`a <b and c> d` over-strip case. T030 tightened `ip_strip.py`'s `_TAG`/`_HAS_MARKUP` in Phase 2,
*before* this phase runs, so every row here is expected to **resolve** now — the fixture that
demonstrated the defect is the same fixture that proves the fix, on the terms task T029 built it.

**(b) extractor-side row drops** — CM02's two rows (T008): a misfiled default-equipment sentence
(the html extractor's shape 1, `wahapedia_html_dom.py:910-924`) and the `None.` placeholder (shape
2). Neither is a real option sentence under either arm's own accounting — the html extractor
discards both at extraction, and the export delivers both as ordinary, unparseable rows. Both are
expected to stay **unresolved**, classified as `option_taxonomy.classify()` classes 6 and 11
respectively, and both are a **denominator** cause: no production could ever resolve a sentence
that never described an option.

**(c) row granularity** — not row-fixture-testable (research.md Q1's own text: "What would close
it" is the aggregate per-datasheet row-count comparison `option_taxonomy.py --compare-modes`
already produces, never a single crafted row — three single-row candidates were tried by hand
against the live post-T030 grammar during this task's own investigation and all three resolved,
confirming the mechanism is a cross-arm geometry question, not a per-row parse failure). This file
therefore asserts the **kind** research.md's own fallback commits to if the aggregate measurement
ever shows the cause is real: **vocabulary**, which routes to the hybrid path (FR-009 criterion 1)
and never to a production, per rule 5.
"""

from __future__ import annotations

from pathlib import Path

from pipeline.parse.composition_grammar import pre_pass
from pipeline.parse.options_grammar import parse_row, split_sublist
from pipeline.parse.wahapedia_csv import read_file
from tools.diagnosis_causes import HYPOTHESIS_KIND
from tools.option_taxonomy import classify

ENRICHMENT = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "wahapedia"


def _rows(datasheet_id: str) -> list[tuple[int, str]]:
    grouped: dict[str, list[tuple[int, str]]] = {}
    for row in read_file(ENRICHMENT / "Datasheets_options.csv").rows:
        grouped.setdefault(row.fields["datasheet_id"], []).append(
            (int(row.fields["line"]), row.fields["description"])
        )
    return sorted(grouped[datasheet_id])


def test_markup_form_asymmetry_rows_all_resolve_after_the_normalization_fix() -> None:
    """CM01's five rows (T007) — hypothesis (a). T030 already landed (Phase 2 runs ahead of this
    phase's checkpoint), so every space-variant/unterminated form is expected to parse now."""
    rows = _rows("CM01")
    assert len(rows) == 5, "CM01 is expected to carry exactly the five T007 markup-variant forms"
    for line, description in rows:
        assert parse_row(description) is not None, (
            f"CM01|{line} should resolve post-T030 -- if this fails, the normalization fix "
            "regressed or the fixture changed shape"
        )


def test_markup_form_asymmetry_is_classified_as_a_normalization_cause() -> None:
    assert HYPOTHESIS_KIND["markup_form_asymmetry"] == "normalization"


def test_the_misfiled_default_equipment_shape_stays_unresolved_as_class_6() -> None:
    """CM02|1 (T008 shape 1) — the same shape `wahapedia_html_dom.py` drops at extraction."""
    (line, description) = next(row for row in _rows("CM02") if row[0] == 1)
    assert parse_row(description) is None
    stem_raw, _items = split_sublist(description)
    stem = pre_pass(stem_raw, field="option.description")
    assert classify(stem) == "6"


def test_the_none_placeholder_shape_stays_unresolved_as_class_11() -> None:
    """CM02|2 (T008 shape 2) — the other html-extractor-dropped shape."""
    (line, description) = next(row for row in _rows("CM02") if row[0] == 2)
    assert parse_row(description) is None
    stem_raw, _items = split_sublist(description)
    stem = pre_pass(stem_raw, field="option.description")
    assert classify(stem) == "11"


def test_extractor_row_drop_is_classified_as_a_denominator_cause() -> None:
    assert HYPOTHESIS_KIND["extractor_row_drop"] == "denominator"


def test_row_granularity_is_classified_as_a_vocabulary_cause_if_real() -> None:
    """research.md Q1's stated fallback: IF granularity is a real cause, it is vocabulary-class
    and routes to the hybrid (FR-009 criterion 1) -- never a production (rule 5). Not proven real
    or refuted by this test; that is the aggregate measurement's job (T039), not a fixture's."""
    assert HYPOTHESIS_KIND["row_granularity"] == "vocabulary"


def test_every_fr_006_hypothesis_has_a_recorded_kind() -> None:
    """FR-006 names exactly three hypotheses; none may be silently missing an outcome."""
    assert set(HYPOTHESIS_KIND) == {
        "markup_form_asymmetry",
        "extractor_row_drop",
        "row_granularity",
    }
    assert set(HYPOTHESIS_KIND.values()) <= {"denominator", "normalization", "vocabulary"}
