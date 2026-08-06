# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented validation V8 (task T067): the
# scan over data/, curation/, reports/, state/ and the built bundle, plus the work/-emptiness
# assertion, raising the blocking CON-IP-BOUNDARY (SC-003, FR-012, FR-013).
"""V8 — prove the IP boundary held, rather than assume it.

Two independent mechanisms back the boundary (research D8). The first is that there is nowhere
to *put* prose: no field anywhere downstream of `normalize` is typed to hold it, so the policy
holds by schema design rather than by review vigilance. This module is the second — the scan
that turns the claim into a monitored control, and the one that would notice if the first ever
developed a hole.

It scans for the classes actually observed in the sources rather than for prose in the abstract:
markup, HTML entities, unresolved `$` tokens, Cyrillic scraper artefacts, and any string long
enough to have stopped being a name. Plus one structural check: `work/` must be empty, because
a leftover acquired page is raw source material sitting in the repository whatever else is true.

**A finding never carries the offending text.** It names the file, the JSON pointer, and the
violation class. Reporting the string would move it from `data/` into `reports/`, which the same
requirement covers (FR-013).
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Final

from pipeline.models.findings import Finding
from pipeline.models.mechanical import NON_MECHANICAL_PATTERNS, is_mechanical_string
from pipeline.report.catalogue import build_finding

#: The directories V8 covers, exactly as data-model.md §8 names them.
SCANNED_DIRECTORIES: Final[tuple[str, ...]] = ("data", "curation", "reports", "state")

#: Files worth reading. Anything else in these trees is a marker file or a lock.
SCANNED_SUFFIXES: Final[frozenset[str]] = frozenset({".json", ".jsonl", ".md"})

#: The hard ceiling on a single string value, above which it is prose whatever it claims to be.
#:
#: Deliberately **not** the 1 000-character summary target. That target is an editorial one and
#: overshooting it is the advisory `SUM-OVERLENGTH`; this is the length at which a value cannot
#: be a name, a label, or a mechanics-only summary at all, and it matches the hard cap the
#: bundle schema enforces. Using one number for both would make every slightly long summary a
#: blocking IP violation, which is not what either requirement says.
IP_SCAN_MAX_CHARS: Final = 1000

#: The gitignored workspace. Its emptiness is part of V8, not a separate check.
WORK_DIRECTORY: Final = "work"

#: What a finding names when the scanned document is the in-memory bundle rather than a file.
BUNDLE_PATH: Final = "bundle"

# AI-Assisted: Claude Code (model: claude-sonnet-5) - Exempted the report renderer's own
# collapsible-section tags from the "markup" violation class (CI run 30939452542 on PR #1,
# candidate/mfm-2026-08's first committed report.md): `pipeline/report/validation.py`'s
# `render_report_markdown` deliberately emits `<details><summary>...</summary>` around each
# findings class so a report with thousands of advisory rows stays readable, and that is
# pipeline-authored formatting, never upstream data -- exactly what the "markup" class does not
# exist to catch (see this module's own docstring: it is watching for un-stripped source markup
# like `<span class="kwb">`). Every real build with any findings produces this markup, so this
# was latent since T067 and only surfaced once a real report.md was first committed.
#: The exact structural tags the report renderer emits. Stripped only before the "markup"
#: pattern runs against free text (`_scan_text` -- `.md` files and any malformed-JSON fallback);
#: `_scan_json_document` and every other violation class are unaffected, so a `<span>` or other
#: tag genuinely leaked from data, in a report or anywhere else, is still caught undiminished.
REPORT_STRUCTURAL_TAGS: Final[tuple[str, ...]] = (
    "<details>",
    "</details>",
    "<summary>",
    "</summary>",
)


def _strip_report_structural_markup(text: str) -> str:
    for tag in REPORT_STRUCTURAL_TAGS:
        text = text.replace(tag, "")
    return text


def _violations(value: str, *, check_length: bool) -> list[str]:
    found = [reason for reason, pattern in NON_MECHANICAL_PATTERNS.items() if pattern.search(value)]
    if check_length and len(value) > IP_SCAN_MAX_CHARS:
        found.append("over_length")
    return sorted(found)


def _walk_json(node: Any, pointer: str = "") -> Iterator[tuple[str, str]]:
    """Yield ``(json pointer, string)`` for every string in the document — keys included.

    Keys are scanned because a key is a string the producer chose, and a document whose *keys*
    carry markup is exactly as broken as one whose values do.
    """
    if isinstance(node, str):
        yield pointer or "/", node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield f"{pointer}/{key}", key
            yield from _walk_json(value, f"{pointer}/{key}")
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from _walk_json(item, f"{pointer}/{index}")


#: What a pointer segment becomes when the segment is itself the problem. A pointer is built
#: from *keys*, and a document whose keys carry markup would otherwise smuggle that markup into
#: the report through the very field meant to locate it.
REDACTED_SEGMENT: Final = "(redacted)"


def _safe_pointer(pointer: str) -> str:
    """A JSON pointer with any non-mechanical segment replaced rather than quoted."""
    segments = pointer.split("/")
    return "/".join(
        segment if is_mechanical_string(segment, max_chars=64) else REDACTED_SEGMENT
        for segment in segments
    )


def _finding(path: str, violation: str, pointer: str | None = None) -> Finding:
    detail: dict[str, str | int] = {"path": path, "violation": violation}
    if pointer:
        detail["pointer"] = _safe_pointer(pointer)
    return build_finding("CON-IP-BOUNDARY", entity_refs=[path], detail=detail)


def _scan_json_document(relative: str, document: Any) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[str] = set()
    for pointer, value in _walk_json(document):
        for violation in _violations(value, check_length=True):
            if violation in seen:
                continue
            seen.add(violation)
            findings.append(_finding(relative, violation, pointer))
    return findings


def _scan_text(relative: str, text: str) -> list[Finding]:
    """Markdown and JSON-lines: the pattern classes only.

    Length is not checked here. A report's prose *about* the data is authored by the producer
    and is meant to be readable, so a long sentence in `report.md` is not an IP violation — the
    length rule is about a *field* that has stopped being a field.

    The report renderer's own `<details>`/`<summary>` collapsible-section tags are stripped
    before the pattern classes run (`REPORT_STRUCTURAL_TAGS`) — pipeline-authored formatting,
    not upstream data, so it is not what "markup" exists to catch. Nothing else about the text
    is touched: any other tag, real or not, still matches undiminished.
    """
    findings: list[Finding] = []
    seen: set[str] = set()
    for violation in _violations(_strip_report_structural_markup(text), check_length=False):
        if violation not in seen:
            seen.add(violation)
            findings.append(_finding(relative, violation))
    return findings


def scan_file(path: Path, *, relative: str) -> list[Finding]:
    """Scan one file. An unreadable or malformed file is scanned as raw text rather than skipped."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".json":
        try:
            return _scan_json_document(relative, json.loads(text))
        except json.JSONDecodeError:
            return _scan_text(relative, text)
    if path.suffix == ".jsonl":
        findings: list[Finding] = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                findings.extend(_scan_json_document(relative, json.loads(line)))
            except json.JSONDecodeError:
                findings.extend(_scan_text(relative, line))
        return findings
    return _scan_text(relative, text)


def scan_bundle(bundle: Any) -> list[Finding]:
    """Scan the built bundle in memory, before it is ever written or uploaded."""
    return _scan_json_document(BUNDLE_PATH, bundle)


def scan_repository(root: Path) -> list[Finding]:
    """Scan every covered directory plus the ``work/`` emptiness assertion.

    Findings are returned sorted by ``(path, violation)`` so two runs over the same tree report
    the same thing in the same order — a report that reshuffles itself is one nobody diffs.
    """
    findings: list[Finding] = []

    for name in SCANNED_DIRECTORIES:
        directory = root / name
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
                continue
            findings.extend(scan_file(path, relative=path.relative_to(root).as_posix()))

    work = root / WORK_DIRECTORY
    if work.is_dir():
        leftovers = sorted(p for p in work.rglob("*") if p.is_file())
        if leftovers:
            findings.append(
                build_finding(
                    "CON-IP-BOUNDARY",
                    entity_refs=[WORK_DIRECTORY],
                    detail={
                        "path": WORK_DIRECTORY,
                        "violation": "work_not_empty",
                        "file_count": len(leftovers),
                    },
                )
            )

    return sorted(findings, key=lambda f: (str(f.detail.get("path")), str(f.detail["violation"])))
