# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the per-record IP strip (task
# T060), ported from the Dart strip-wahapedia-ip precedent and narrowed so that no rules text of
# any kind is carried (FR-011, FR-012, FR-013, research D8).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Folded Cyrillic/Latin homoglyphs at the end
# of strip_field, the single funnel every detail-source name and label passes through, so a
# source-side look-alike character is corrected upstream of the IP scan instead of blocking the
# release as an indistinguishable Cyrillic artefact (pipeline/normalize/homoglyphs.py).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Tightened _TAG/_HAS_MARKUP into a two-branch
# pattern (009 task T030, plan.md finding 6): a CLOSED-tag branch tolerating space-variant
# `<`/`</` forms and requiring quoted attributes only (so `a <b and c> d` no longer parses as a
# tag), and an UNTERMINATED-tag branch for a tag with no closing `>` anywhere later in the field.
# Edited in lockstep with models/mechanical.py's NON_MECHANICAL_PATTERNS["markup"] (T029's paired
# assertion) -- parse/options_grammar.py and equipment_grammar.py are untouched (rule 5).
"""Strip everything the product may not carry, and keep only mechanical values.

**Relationship to the `strip-wahapedia-ip` precedent.** That skill's per-record classification —
what is expression versus what is function — is adopted wholesale. Two deliberate narrowings are
recorded here so nobody "reuses" the skill and smuggles content in:

* the skill *keeps* mechanical rules text, such as stratagem `WHEN`/`TARGET`/`EFFECT` bodies.
  **This pipeline carries no rules text of any kind**, because the frozen consumer schema has no
  column for it. The skill is a superset; this is a strict subset of it.
* the skill emits stratagems, missions and detachment ability text. None of those are in scope
  here: those files are read only where they contribute a *structural* fact.

**The order of operations is load-bearing.** Markup is removed before entities are decoded,
because decoding first turns `&lt;b&gt;` into something that looks like markup and gets
stripped on the second pass — silently deleting a legitimate value. `<table>` and `<img>`
content is dropped **whole** rather than flattened: a flattened table is still the publisher's
tabular rules, just harder to notice.

**A finding never quotes what it found.** `DQ-MARKUP-IN-FIELD` names the field, not the markup.
A stripper that reports what it stripped has moved the text into the report rather than removed
it, and FR-013 covers reports and logs as well as data.

**The homoglyph fold runs here, last**, because this function is the single funnel every
detail-source name and label passes through on its way to the curated tree (see the call sites
in `pipeline/curate/assemble.py`: datasheet, model, weapon, ability and keyword names, the
cost-table label, the role and the composition line). Folding at that funnel is what lets
`pipeline/validate/ip_scan.py` stay exactly as strict as it is: the scanner sees names that are
already clean, rather than needing an exception for the source's own typing slips. See
`pipeline.normalize.homoglyphs` for the heuristic and for why it refuses far more often than it
acts.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from typing import Final

from pipeline.models.findings import Finding
from pipeline.normalize.homoglyphs import fold_homoglyphs
from pipeline.report.catalogue import build_finding

#: Elements whose *content* is dropped along with the element: publisher artwork references and
#: tabular rules. Research §0.1 counted 87 `<table>` and 27 `<img>` in one export file alone.
_DROPPED_SUBTREES: Final = re.compile(
    r"<(table|img|svg|picture|figure|script|style)\b[^>]*>.*?</\1\s*>|<(img|br|hr)\b[^>]*/?>",
    re.IGNORECASE | re.DOTALL,
)

#: A genuine tag name: a letter, then letters/digits. No interior whitespace -- that is what
#: keeps `<b and c>` from parsing as a tag named `b` at all (see `_TAG` below).
_TAG_NAME: Final = r"[A-Za-z][A-Za-z0-9]*"

#: The opening of a tag, or a closing tag's opening: `<`, then an OPTIONAL `/` with OPTIONAL
#: whitespace on EITHER side of it (`</b>`, `< /b>`, `</ b>`, `< / b>` all recognised — every
#: space-variant form `plan.md` finding 6 measured), before the name.
_TAG_OPEN: Final = r"<\s*/?\s*"

#: One `key="value"` or `key='value'` attribute, the ONLY attribute shape a well-formed tag may
#: carry here. Deliberately excludes a bare (unquoted, no `=`) attribute — real markup in this
#: export never needs one, and allowing it is exactly what let `<b and c>` parse as tag `b` with
#: two boolean attributes `and`/`c` under the old, looser pattern (009 task T030, `plan.md`
#: finding 6's "over-strip" case).
_ATTR: Final = r"""(?:\s+[A-Za-z][A-Za-z0-9-]*=(?:"[^"]*"|'[^']*'))"""

#: Branch 1 — a genuine, CLOSED tag: `_TAG_OPEN`, zero or more quoted attributes, an optional
#: self-closing `/`, and a `>`. `<b and c>` fails this branch: after the name `b`, the literal
#: text `and c` matches neither an `_ATTR` group nor the `\s*/?>` tail, so the whole alternative
#: does not match — which is what leaves ordinary prose using angle brackets untouched.
_CLOSED_TAG: Final = rf"{_TAG_OPEN}{_TAG_NAME}{_ATTR}*\s*/?>"

#: Branch 2 — an UNTERMINATED tag: `_TAG_OPEN` and a name, and — checked by the lookahead — no
#: `>` appears anywhere later in the field. Removed to the end of the field rather than left in
#: place (a scraper artefact with no closing bracket has no well-defined extent, and rule FR-013
#: treats "leave it in" as the greater risk). The lookahead is checked right after `<`, before
#: `_TAG_OPEN`'s own optional `/`/whitespace are consumed, which is exactly what stops this branch
#: from also swallowing `<b and c>`: that field DOES have a `>` later on, so the lookahead fails
#: and branch 1's refusal stands.
_UNTERMINATED_TAG: Final = rf"<(?!.*>)\s*/?\s*{_TAG_NAME}.*$"

#: Any remaining element. Its *content* survives; the tag does not.
_TAG: Final = re.compile(rf"(?:{_CLOSED_TAG})|(?:{_UNTERMINATED_TAG})")

#: Does this field carry markup at all? Cheap, and asked before anything is removed. Character-
#: identical to `pipeline.models.mechanical.NON_MECHANICAL_PATTERNS["markup"]` — see that
#: module's own comment for why the two must never drift apart (009 task T030). Reuses `_TAG`'s
#: own two branches rather than a third pattern, so "found markup" and "would strip something"
#: can never disagree with each other.
_HAS_MARKUP: Final = re.compile(rf"(?:{_CLOSED_TAG})|(?:{_UNTERMINATED_TAG})")

#: An unresolved scraper placeholder, e.g. `$FAQ$`. Low volume in the observed data, but a live
#: class: emitting one would publish a token that means nothing to a player.
_PLACEHOLDER_TOKEN: Final = re.compile(r"\$[A-Za-z_{]")


@dataclass(frozen=True, slots=True)
class StripResult:
    """A stripped field and the data-quality findings observed while stripping it."""

    text: str
    findings: tuple[Finding, ...] = ()


def _collapse(value: str) -> str:
    """Collapse every run of Unicode whitespace — including `&nbsp;` — to one space."""
    return " ".join(value.split())


def strip_field(raw: str, *, field: str, entity_ref: str | None = None) -> StripResult:
    """Reduce one source field to its mechanical content.

    Args:
        raw: the field exactly as the source published it.
        field: the field's *name*, for the finding. Never its value.
        entity_ref: the record the field belongs to, so a finding can be located without
            quoting anything.
    """
    if not raw:
        return StripResult("")

    findings: list[Finding] = []
    refs = [entity_ref] if entity_ref else []

    if _HAS_MARKUP.search(raw):
        findings.append(
            build_finding("DQ-MARKUP-IN-FIELD", entity_refs=refs, detail={"field": field})
        )

    without_subtrees = _DROPPED_SUBTREES.sub(" ", raw)
    without_tags = _TAG.sub(" ", without_subtrees)
    decoded = html.unescape(without_tags)
    # Folded after the collapse, never before: the fold weighs look-alikes against the string's
    # other letters, and a value still carrying markup would be weighed against the tag names
    # too. It is a no-op for every string with no Cyrillic in it, which is nearly all of them.
    text = fold_homoglyphs(_collapse(decoded))

    if _PLACEHOLDER_TOKEN.search(text):
        findings.append(
            build_finding("DQ-PLACEHOLDER-TOKEN", entity_refs=refs, detail={"field": field})
        )

    return StripResult(text, tuple(findings))


# `hard_normalise` and `mechanic_digest` moved to their own contract path,
# `pipeline.normalize.mechanic_digest` (task T127), once US5 needed to call them from the
# curate and validate stages independently of the IP-strip pipeline. They are not re-exported
# here: importing `strip_field` back into that module (which they depend on) while importing
# them back into this one would be circular. Import them from
# `pipeline.normalize.mechanic_digest` directly.
