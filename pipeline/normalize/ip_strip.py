# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the per-record IP strip (task
# T060), ported from the Dart strip-wahapedia-ip precedent and narrowed so that no rules text of
# any kind is carried (FR-011, FR-012, FR-013, research D8).
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
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from typing import Final

from pipeline.models.findings import Finding
from pipeline.report.catalogue import build_finding

#: Elements whose *content* is dropped along with the element: publisher artwork references and
#: tabular rules. Research §0.1 counted 87 `<table>` and 27 `<img>` in one export file alone.
_DROPPED_SUBTREES: Final = re.compile(
    r"<(table|img|svg|picture|figure|script|style)\b[^>]*>.*?</\1\s*>|<(img|br|hr)\b[^>]*/?>",
    re.IGNORECASE | re.DOTALL,
)

#: Any remaining element. Its *content* survives; the tag does not.
_TAG: Final = re.compile(r"</?[A-Za-z][^>]*>")

#: Does this field carry markup at all? Cheap, and asked before anything is removed.
_HAS_MARKUP: Final = re.compile(r"</?[A-Za-z][A-Za-z0-9]*[\s/>]")

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
    text = _collapse(decoded)

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
