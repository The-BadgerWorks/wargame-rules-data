# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the finding data digest and
# digest-matched resolution suppression (task T089) per validation-report.md §5 and FR-034: a
# resolution suppresses its finding only while the digest matches, and lapses on its own when the
# underlying data moves.
"""Binding a finding to the data that produced it.

A dated resolution is a curator saying *"I looked at this one and it is correct as published"*.
The whole design question is how to stop that from silently becoming *"I never want to see this
class of finding again"*, because the second is indistinguishable from the first at the moment it
is written and only differs a year later.

The answer is :func:`data_digest`. The suppression is bound to a hash of the finding's own code,
entity references, and mechanical detail — so when the data moves, the digest moves, the
resolution no longer matches, and the finding is raised again at its catalogue severity. Nobody
has to remember to revisit it. A curator cannot silence a class of finding permanently, only this
occurrence of it, and only while it is *this* occurrence.

**Suppressed findings stay in the report** (§5). A finding that vanishes when it is waved through
is indistinguishable from one that was fixed, and an approver has to be able to tell.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping, Sequence

from pipeline.build.canonical_json import JsonValue, dumps_bundle
from pipeline.models.authored import FindingResolution
from pipeline.models.findings import Finding, FindingDetail


def data_digest(
    finding_code: str, entity_refs: Sequence[str], detail: FindingDetail | None = None
) -> str:
    """The ``sha256:…`` a resolution is bound to.

    Computed over the canonical serialisation of the finding's mechanical content, so it is
    stable across runs, platforms, and dict ordering — the same three properties the bundle
    checksum needs, for the same reason (FR-033).

    The digest deliberately covers the **detail**, not just the entity: a band mismatch on
    ``ds-x`` at 20 models and a band mismatch on ``ds-x`` at 25 models are different facts about
    the same unit, and a resolution for one must not silently cover the other.
    """
    payload: dict[str, JsonValue] = {
        "finding_code": finding_code,
        "entity_refs": sorted(entity_refs),
        "detail": _canonical_detail(detail or {}),
    }
    return f"sha256:{hashlib.sha256(dumps_bundle(payload).encode('utf-8')).hexdigest()}"


def _canonical_detail(detail: FindingDetail) -> dict[str, JsonValue]:
    """``detail`` as canonical JSON. Sequences are materialised; nothing else is transformed."""
    canonical: dict[str, JsonValue] = {}
    for key, value in detail.items():
        canonical[key] = value if isinstance(value, str | int | bool) else list(value)
    return canonical


def with_digest(finding: Finding) -> Finding:
    """Return ``finding`` carrying its :func:`data_digest`.

    Applied once, centrally, rather than at every construction site: a finding built without a
    digest cannot be resolved at all, and "the one place that forgot" would present as a
    resolution that mysteriously never takes effect.
    """
    if finding.data_digest is not None:
        return finding
    return finding.model_copy(
        update={
            "data_digest": data_digest(finding.finding_code, finding.entity_refs, finding.detail)
        }
    )


def apply_resolutions(
    findings: Iterable[Finding], resolutions: Iterable[FindingResolution]
) -> list[Finding]:
    """Attach each matching, unlapsed resolution's explanation to its finding.

    Matching is on ``(finding_code, entity_ref, data_digest)`` — all three. Dropping the digest
    would make the suppression permanent, and dropping the entity would make it a class-wide
    silence; either is the failure this function exists to prevent.
    """
    by_key: dict[tuple[str, str, str], FindingResolution] = {
        (r.finding_code, r.entity_ref, r.data_digest): r for r in resolutions
    }
    if not by_key:
        return [with_digest(finding) for finding in findings]

    resolved: list[Finding] = []
    for raw in findings:
        finding = with_digest(raw)
        match = next(
            (
                by_key[(finding.finding_code, entity_ref, finding.data_digest or "")]
                for entity_ref in finding.entity_refs
                if (finding.finding_code, entity_ref, finding.data_digest or "") in by_key
            ),
            None,
        )
        resolved.append(
            finding.model_copy(update={"resolution": match.explanation}) if match else finding
        )
    return resolved


def counts_by_code(findings: Iterable[Finding]) -> Mapping[str, int]:
    """How many times each code was raised. The report's scale figures are built from this."""
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.finding_code] = counts.get(finding.finding_code, 0) + 1
    return counts
