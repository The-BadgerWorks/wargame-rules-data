<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the failed-then-fixed standing rule
     (task T154): any defect that reaches a published version ships its correction with a
     fixture-based regression test reproducing the defect before the fix and passing after it,
     composed with fixtures/README.md's synthetic-fixture policy, plus a worked example of the
     test shape. -->
# Failed then fixed: the standing rule for a published defect

**Any data defect that reaches a *published* version must ship its correction together with a
fixture-based regression test that reproduces the defect before the fix and passes after it.**
Not "should" — must. A fix without that test closes today's symptom and leaves the door open for
the same class of defect to recur silently, which is exactly the failure mode this rule exists to
close off.

## Why "published," specifically

A defect caught by validation before publication (a blocking finding, a coverage collapse, a
determinism check) already has an automated gate refusing to ship it — the gate itself *is*
evidence the class of defect is covered. A defect that reaches a published version is, by
definition, one none of those gates caught. That is the signal this rule reacts to: something a
player could see and be wrongly charged or wrongly informed by got through everything else, so the
fix is incomplete until there is a test that would have caught it — otherwise the same gap in
coverage is still there, unaddressed, only patched around for this one instance.

## What the test has to do

1. **Reproduce the defect, not just the fix.** A fixture (see below) shaped so that, run against
   the pipeline code *as it stood before the fix*, it produces the same wrong output the real
   incident produced — a mispriced datasheet, a missed structural change, a wrongly-derived
   `is_hybrid_edition`, whatever the actual defect was. If the test cannot be shown to fail against
   the pre-fix code (by literally running it against the parent commit, or by inspection of the
   logic it exercises), it is not evidence the defect is covered — it may simply be exercising a
   code path the bug was never in.
2. **Pass after the fix**, deterministically, with no dependency on anything the fix itself did not
   change.
3. **Live under `tests/`, alongside the pipeline code it exercises**, using the same test
   conventions (fixtures, assertions, naming) the surrounding test module already uses — this is a
   permanent regression test, not a one-off script that gets deleted once the incident is closed.

## Composing with the synthetic-fixture policy

`fixtures/README.md` is unambiguous and this rule does not get an exception from it: **every
fixture is synthetic** — hand-authored HTML/CSV reproducing an observed *structure and quirk
class*, using invented faction names, invented unit names, invented placeholder prose. Capturing
the real page that actually triggered the incident and committing it — even redacted, even
partially — is prohibited by the same two requirements that prohibit it everywhere else in this
repository: FR-010 (no raw acquired source material in any repository) and FR-013 (no publisher
wording in curated data, intermediate artifacts, version control, logs, or reports). A captured
incident page is not exempt because it is "evidence of a bug" rather than routine test data — it
is exactly as much raw source material either way.

What this means in practice: when a real defect is diagnosed, the fixture that reproduces it is
authored from a *description* of what was structurally or mechanically wrong — the specific quirk
class (an unfilled placeholder, a cost cell whose delta marker was misread as the price, a
detachment card whose DP literal changed case) — using invented names, exactly like every other
fixture in this repository. The fixture proves the pipeline handles *that class* of input
correctly; it does not, and must not, prove anything about the specific real page, because it
never contains the specific real page's content.

## Worked example: the shape such a test takes

This is illustrative — the concrete defect below is constructed to show the shape, not a
transcription of a real incident — but it is the shape every real one should follow.

**Suppose**: a published version shipped a unit's points cost read from the wrong `<li>` because a
cost-table cell's delta marker (`▲ (+15)`) was captured as part of the points figure instead of
being parsed out separately, so a unit that should have cost `155` shipped as `▲(+15)155`
truncated to some wrong integer by a downstream cast. Detected after publication, e.g. by a spot
check (`docs/verification/spot-check-template.md`) or a player report.

**1. A fixture row reproducing the specific malformed input.** Add (or extend) a synthetic
fixture page under `fixtures/sample/mfm/<invented-faction>.html` containing a unit cost cell
written the same structural way the real page's cell was — literal text shaped like
`▲ (+15) 155 pts` inside the `<li>` `pipeline/parse/mfm_dom.py`'s `_COST_CELL` pattern reads —
for an invented unit, e.g. `"Emberwright Vanguard"`, never any real unit's name.

**2. A test asserting the old wrong output would have failed.** In
`tests/unit/test_mfm_dom_extraction.py` (or wherever the surrounding suite for this parser
already lives):

```python
def test_a_delta_marker_never_leaks_into_the_points_figure():
    """Regression for <incident reference>: a cost cell's delta annotation
    ('(+15)') must never be read as part of the points value itself.

    Fixture: fixtures/sample/mfm/emberwrights.html, unit "Emberwright Vanguard",
    cost cell "▲ (+15) 155 pts".
    """
    page = extract_mfm_page(parse_fixture("fixtures/sample/mfm/emberwrights.html"))
    vanguard = _find_unit(page, "Emberwright Vanguard")

    # Pinned to the correct value. Before the fix, the parser produced a value
    # derived from the concatenated "15155" or similar malformed read, which is
    # exactly what this assertion would have caught: it is written to fail
    # against the pre-fix extraction, not merely to pass against the fixed one.
    assert vanguard.cost_rows[0].points == 155
    assert vanguard.cost_rows[0].delta_marker == "+15"
```

The comment inside the test says explicitly what incident it is a regression for and what the
old, wrong behaviour was — a regression test that does not say why it exists reads, a year later,
as an arbitrary assertion nobody can explain, and someone eventually "simplifies" it away.

**3. The pipeline change plus the trailer that accompanies it.** The actual fix (in this example,
tightening `_COST_CELL`'s capture groups in `pipeline/parse/mfm_dom.py` so the delta group can
never bleed into the points group) ships in the same PR as the fixture and the test above, and the
commit carries this repository's standard attribution trailer for AI-assisted work:

```text
Fix cost-cell delta marker leaking into the points figure

A unit cost cell whose delta annotation immediately preceded the points
figure (e.g. "▲ (+15) 155 pts") could have its delta text read as part of
the points value. Tightens _COST_CELL's capture groups so the two are
never conflated, and adds a synthetic fixture + regression test that
fails against the prior extraction and passes against this one.

AI-Assisted-By: Claude Code (model: claude-sonnet-5)
```

Every file the fix or the test touches that is new or substantially edited also carries the
per-file `AI-Assisted:` header comment this repository's Principle 16 convention requires,
independent of the commit trailer.

## What this does not cover

This rule is about a defect that reached a **published** version. A defect caught earlier —
blocked by validation before ever publishing, or found in review of a candidate PR — is still
worth a regression test as good practice, but is not bound by this page's "must ship with the
fix" rule in the same way, because the gate that caught it is already the evidence of coverage
this rule exists to produce for the case where nothing caught it.
