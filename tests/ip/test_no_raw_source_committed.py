# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the repository-wide raw-source scan
# (task T053): no tracked file under work/, no .csv outside fixtures/, no committed HTML outside
# fixtures/. Runs in CI on every PR.
# AI-Assisted: Claude Code (model: claude-opus-5) - Extended the scan to the current-edition HTML
# acquisition path (004 task T083). The extension-based rules below already catch a committed
# `datasheets.html`, but they catch it as "an .html file", which says nothing about where it came
# from -- and a page saved under a different extension, or a directory named after the source
# tree, would sail past all three. The new test asserts on the PATH, which is the thing FR-004
# and FR-010 actually care about.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Extended the walk to
# `state/wahapedia-export-digest.json` (009 rung R05, T094, FR-030): the export-timestamp
# short-circuit's own new state file is the one place this feature could accidentally retain the
# publisher's raw `Last_update.csv` text instead of its one-way digest, so the same mechanism
# that already keeps raw source out of `fixtures/`, `work/`, and the diagnosis reports now also
# keeps it out of this file -- and, as evidence it is not a check that would pass regardless, a
# planted raw-timestamp-shaped value in a synthetic digest object is shown caught before the real
# tracked file is checked.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Extended the walk to
# `reports/009-diagnosis/` (009 task T034): FR-008 requires the diagnosis report to be
# text-free -- cause, row count, residual, finding class, datasheet id only -- which is a
# narrower and different claim than `pipeline.validate.ip_scan`'s markup/entity/placeholder scan
# already makes over the same directory. That scan deliberately does not check prose length or
# quotation (`ip_scan.py::_scan_text`'s own docstring: "a long sentence in report.md is not an
# IP violation" -- the report's own authored analysis prose is expected and fine). What FR-008
# adds on top is narrower: no *quoted* run of source-shaped text, because this report's own
# prose never has a reason to quote anything it describes -- it names causes and classes, it
# never repeats what a row said.
"""The scan that keeps raw acquired source material out of version control (FR-010, SC-003).

This is deliberately a *git* scan rather than a filesystem scan. A curator's working tree will
have `work/` full of acquired pages mid-run and that is exactly what `work/` is for; what must
never happen is one of them being committed, because git history is effectively permanent and
FR-013 covers version control explicitly.

`fixtures/` is the only place a `.csv` or an `.html` may live, and `fixtures/README.md` states
why the files there are authored rather than captured.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError

from pipeline.observability.ledger import RunLedgerEntry

REPO_ROOT = Path(__file__).resolve().parents[2]


def _tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip("not a git checkout")
    return [entry for entry in result.stdout.split("\0") if entry]


def test_nothing_under_work_is_tracked() -> None:
    """`work/` is ephemeral by construction and gitignored by the first line of .gitignore."""
    assert [p for p in _tracked_files() if p == "work" or p.startswith("work/")] == []


def test_no_csv_is_tracked_outside_fixtures() -> None:
    offenders = [
        p for p in _tracked_files() if p.endswith(".csv") and not p.startswith("fixtures/")
    ]
    assert offenders == []


def test_no_html_is_tracked_outside_fixtures() -> None:
    offenders = [
        p
        for p in _tracked_files()
        if p.endswith((".html", ".htm")) and not p.startswith("fixtures/")
    ]
    assert offenders == []


def test_the_fixture_files_that_do_exist_are_declared_synthetic() -> None:
    """Every fixture set carries the note that says where its content came from."""
    fixture_sets = {
        path.parts[1] for path in (Path(p) for p in _tracked_files()) if path.parts[0] == "fixtures"
    }
    fixture_sets.discard("README.md")
    fixture_sets.discard(".gitkeep")
    for name in sorted(fixture_sets):
        assert (REPO_ROOT / "fixtures" / name / "README.md").is_file(), (
            f"fixture set {name!r} has no README stating that it is synthetic"
        )


def test_gitignore_still_excludes_work_first() -> None:
    lines = [
        line.strip()
        for line in (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert lines[0] == "work/"


#: Path fragments that only appear if something from the publisher's tree was written down.
#: `wh40k11ed` / `wh40k10ed` are the edition tree segments `WGC_DETAIL_SOURCE_URL` points at;
#: `SiteMap.xml` and `datasheets.html` are the two documents the `html`-mode sweep retrieves.
ACQUISITION_PATH_MARKERS: tuple[str, ...] = (
    "wh40k11ed",
    "wh40k10ed",
    "sitemap.xml",
    "datasheets.html",
)


def test_no_artefact_of_the_html_acquisition_path_is_tracked() -> None:
    """FR-004's permitted path is a thing to *request*, never a thing to keep.

    The `html`-mode sweep retrieves `SiteMap.xml` and 26 `factions/<slug>/datasheets.html` pages
    into ephemeral `work/`, digests what it needs, and discards them. None of it may reach version
    control under any name, in any directory, at any extension -- which is a statement about the
    path, not about the file type, and so is not covered by the extension rules above.
    """
    offenders = [
        path
        for path in _tracked_files()
        if not path.startswith("fixtures/")
        and any(marker in path.lower() for marker in ACQUISITION_PATH_MARKERS)
    ]

    assert offenders == [], (
        "these tracked paths name the publisher's acquisition tree, which is retrieved into "
        f"work/ and discarded, never committed (FR-004, FR-010): {offenders}"
    )


# --- 009 T034: the diagnosis report is text-free (FR-008, SC-012) ------------------------------

DIAGNOSIS_REPORTS_DIR: str = "reports/009-diagnosis/"

#: The length above which a quoted run reads as a matched sentence or quoted phrasing rather
#: than a short quoted term (a single word, a finding code). Comfortably above any of this
#: report's own short quoted terms, comfortably below the length of an ordinary option or
#: equipment sentence -- which is what a real leak would actually look like.
_QUOTED_RUN_MIN_LENGTH: int = 40

#: Straight and curly double quotes, normalised to one character before pairing. Treated as
#: interchangeable rather than matched open-to-close, because this project's own reports use
#: straight quotes throughout and the distinction buys nothing here.
_QUOTE_CHARS: str = '"“”'


def _quoted_phrase_offenders(text: str) -> list[str]:
    """Every line of ``text`` carrying a quoted run of :data:`_QUOTED_RUN_MIN_LENGTH`+
    characters, for a finding message that names the line without repeating its content.

    Pairs quote marks **positionally** (1st with 2nd, 3rd with 4th, ...) rather than matching
    any quote character to the next one found -- a naive "quote ... quote" regex pairs a
    pair's own CLOSING mark with a LATER, unrelated pair's OPENING mark whenever a line carries
    more than one quotation, which is exactly the shape one of this feature's own already-
    committed report lines has (a short quote of `spec.md`'s own wording, immediately followed
    by the *start* of a second, longer quote that continues on the next line): naive pairing
    would misread the plain prose sitting between the two quotations as though it were itself
    quoted. An odd trailing quote mark (a quotation that continues past this line) is correctly
    left unpaired here rather than reaching for the next line's opening mark, which is also why
    this scan stays per-line instead of running over the whole file.
    """
    offenders: list[str] = []
    for number, line in enumerate(text.splitlines(), start=1):
        positions = [index for index, char in enumerate(line) if char in _QUOTE_CHARS]
        for start, end in zip(positions[0::2], positions[1::2], strict=False):
            if end - start - 1 >= _QUOTED_RUN_MIN_LENGTH:
                offenders.append(f"line {number}")
                break
    return offenders


def test_the_quoted_phrase_scan_catches_a_planted_violation() -> None:
    """The scan is proven against a synthetic string before it is trusted against real reports --
    the same discipline `test_ip_scan.py`'s poisoned-tree cases use."""
    poisoned = (
        "## A finding\n\n"
        'The row reads "This model can be equipped with one ember lance and a tide hammer, '
        'or it can instead take a marsh lantern" and was left unresolved.\n'
    )
    assert _quoted_phrase_offenders(poisoned) == ["line 3"]


def test_the_quoted_phrase_scan_does_not_flag_a_short_quoted_term() -> None:
    """A short quoted word or finding code is not what FR-008 guards against -- only a run long
    enough to be a matched sentence or a quoted phrase from a source row."""
    clean = 'The finding names the class as "footnote fragment" and nothing else.\n'
    assert _quoted_phrase_offenders(clean) == []


def test_the_009_diagnosis_reports_carry_no_quoted_phrase() -> None:
    """FR-008: the published diagnosis report never quotes a source sentence or fragment.

    Walks every tracked file under `reports/009-diagnosis/` rather than one named file, so a
    future dated report added by a later run of this feature is covered without editing this
    test.
    """
    tracked = [p for p in _tracked_files() if p.startswith(DIAGNOSIS_REPORTS_DIR)]
    assert tracked != [], "the diagnosis report directory should be tracked and non-empty by now"

    offenders: dict[str, list[str]] = {}
    for relative in tracked:
        text = (REPO_ROOT / relative).read_text(encoding="utf-8")
        found = _quoted_phrase_offenders(text)
        if found:
            offenders[relative] = found

    assert offenders == {}, (
        f"these reports carry a long quoted run, which FR-008 forbids: {offenders}"
    )


# --- 009 rung R05 T094: no raw publisher timestamp anywhere (FR-030) ---------------------------
#
# The export-timestamp short-circuit's own hazard: `state/wahapedia-export-digest.json` is the
# one file this feature adds that reads the publisher's `Last_update.csv` at all. Everything else
# it could leak through -- a report, a log, the run ledger -- either does not carry the value
# (`pipeline.observability.ledger.RunLedgerEntry`'s `coverage` field is typed `Mapping[str, int]`,
# which structurally cannot hold a timestamp string) or is covered by the scans above.

_HEX_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")

EXPORT_DIGEST_STATE_PATH = "state/wahapedia-export-digest.json"


def _non_digest_string_values(raw: dict[str, object]) -> list[str]:
    """Every top-level string value in a digest-state JSON object that is not a bare sha256 hex
    digest -- the shape a raw publisher timestamp (or any other un-hashed value) would take if
    it were accidentally persisted here instead of hashed (FR-030).
    """
    return [
        f"{key}={value!r}"
        for key, value in raw.items()
        if isinstance(value, str) and not _HEX_DIGEST_PATTERN.fullmatch(value)
    ]


def test_the_digest_shape_scan_catches_a_planted_raw_timestamp() -> None:
    """Proof the scan can fail before it is trusted against the real tracked file -- the same
    poisoned-then-clean discipline `test_ip_scan.py` and this file's own quoted-phrase scan use.
    """
    poisoned = {"digest": "2026-08-30T12:00:00Z"}
    assert _non_digest_string_values(poisoned) == ["digest='2026-08-30T12:00:00Z'"]


def test_the_digest_shape_scan_accepts_a_real_one_way_digest() -> None:
    clean = {"digest": hashlib.sha256(b"placeholder export text").hexdigest()}
    assert _non_digest_string_values(clean) == []


def test_the_digest_shape_scan_accepts_the_seeded_empty_state() -> None:
    assert _non_digest_string_values({}) == []


def test_the_tracked_export_digest_state_file_holds_only_a_digest() -> None:
    """FR-030: whatever the tracked `state/wahapedia-export-digest.json` currently holds --
    seeded empty, or carrying a digest from a real run -- it is never the publisher's raw
    `Last_update.csv` text."""
    tracked = _tracked_files()
    assert EXPORT_DIGEST_STATE_PATH in tracked, (
        "the export-digest state file should exist and be tracked (state/README.md)"
    )
    raw = json.loads((REPO_ROOT / EXPORT_DIGEST_STATE_PATH).read_text(encoding="utf-8"))
    offenders = _non_digest_string_values(raw)
    assert offenders == [], (
        f"state/wahapedia-export-digest.json carries a non-digest string value, which FR-030 "
        f"forbids -- it must hold a one-way digest, never the raw timestamp: {offenders}"
    )


def test_the_run_ledger_entry_schema_structurally_cannot_carry_a_timestamp_string() -> None:
    """A second, mechanical guarantee alongside the tracked-file scan above: even if some future
    caller tried to smuggle the raw `Last_update.csv` text into a ledger line's `coverage` map --
    the one place acquisition-shaped counts reach `state/run-ledger.jsonl` -- the schema itself
    refuses it, because `coverage` is typed `Mapping[str, int]`, not `Mapping[str, str]`.
    """
    with pytest.raises(ValidationError):
        RunLedgerEntry(
            run_id="local-test",
            command="build",
            trigger="manual",
            channel="production",
            started_at="2026-08-01T00:00:00Z",
            coverage={"last_update": "2026-08-01T00:00:00Z"},  # type: ignore[dict-item]
        )
