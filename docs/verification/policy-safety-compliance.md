<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded the T156 policy and safety
     compliance audit: the IP-scan test suite actually run, an actual grep of the repository for
     endorsement-claim language, and an actual reading of pipeline/acquire/http.py confirming
     robots.txt-honouring and never-escalate-on-refusal behaviour, with line citations. Closes
     out spec.md's Policy and Safety Constraints section, Constitution Principle 4, and SC-003. -->
# T156 — policy and safety compliance validation

FR-007, FR-010, FR-013, FR-050, spec's *Policy and Safety Constraints* section, Constitution
Principle 4, SC-003. This page records exactly what was checked, the commands run, and their
actual output — evidentiary, not asserted — matching the style of
`docs/verification/approval-rehearsal.md` and `docs/verification/withdrawal-rehearsal.md`.

**Status: complete.** All three checks pass / confirm the required behaviour, with no exceptions
found.

Run: 2026-08-04, against commit `50a3640` (docs branch `docs/polish-002-rules-data-pipeline`,
worktree checkout of `main`), Python 3.12.13 in a fresh `uv`-managed virtualenv
(`.venv`, `uv venv --python 3.12`, `uv pip install -e ".[dev]"`).

## Check 1 — the IP-scan and no-raw-source-committed test suites actually pass

Command:

```bash
.venv/Scripts/python.exe -m pytest tests/ip/ -v
```

Output (verbatim, trimmed of the collection header only):

```text
============================= test session starts =============================
platform win32 -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0
plugins: anyio-4.14.2, httpx-0.36.2
collecting ... collected 31 items

tests/ip/test_ip_scan.py::test_the_scanner_covers_every_directory_the_requirement_names PASSED [  3%]
tests/ip/test_ip_scan.py::test_a_clean_tree_yields_no_findings PASSED    [  6%]
tests/ip/test_ip_scan.py::test_the_real_repository_is_clean PASSED       [  9%]
tests/ip/test_ip_scan.py::test_markup_in_a_curated_file_is_a_blocking_boundary_finding PASSED [ 12%]
tests/ip/test_ip_scan.py::test_the_finding_names_the_violation_class_and_never_the_offending_text PASSED [ 16%]
tests/ip/test_ip_scan.py::test_each_violation_class_is_detected PASSED   [ 19%]
tests/ip/test_ip_scan.py::test_a_file_under_work_is_itself_a_violation PASSED [ 22%]
tests/ip/test_ip_scan.py::test_the_built_bundle_is_scanned_too PASSED    [ 25%]
tests/ip/test_ip_scan.py::test_keys_are_scanned_as_well_as_values PASSED [ 29%]
tests/ip/test_ip_scan.py::test_a_bare_ampersand_or_dollar_sign_is_not_a_false_positive PASSED [ 32%]
tests/ip/test_ip_strip.py::test_quirk_class[markup] PASSED               [ 35%]
tests/ip/test_ip_strip.py::test_quirk_class[numeric-entity] PASSED       [ 38%]
tests/ip/test_ip_strip.py::test_quirk_class[named-entities] PASSED       [ 41%]
tests/ip/test_ip_strip.py::test_quirk_class[table-content-is-dropped-not-flattened] PASSED [ 45%]
tests/ip/test_ip_strip.py::test_quirk_class[image-reference-is-dropped] PASSED [ 48%]
tests/ip/test_ip_strip.py::test_quirk_class[unresolved-token-is-reported] PASSED [ 51%]
tests/ip/test_ip_strip.py::test_quirk_class[whitespace-is-collapsed] PASSED [ 54%]
tests/ip/test_ip_strip.py::test_quirk_class[empty] PASSED                [ 58%]
tests/ip/test_ip_strip.py::test_table_and_image_together_report_one_markup_finding_not_three PASSED [ 61%]
tests/ip/test_ip_strip.py::test_a_cyrillic_classification_artefact_is_not_the_strippers_business PASSED [ 64%]
tests/ip/test_ip_strip.py::test_free_text_composition_is_stripped_before_it_is_parsed PASSED [ 67%]
tests/ip/test_no_raw_source_committed.py::test_nothing_under_work_is_tracked PASSED [ 70%]
tests/ip/test_no_raw_source_committed.py::test_no_csv_is_tracked_outside_fixtures PASSED [ 74%]
tests/ip/test_no_raw_source_committed.py::test_no_html_is_tracked_outside_fixtures PASSED [ 77%]
tests/ip/test_no_raw_source_committed.py::test_the_fixture_files_that_do_exist_are_declared_synthetic PASSED [ 80%]
tests/ip/test_no_raw_source_committed.py::test_gitignore_still_excludes_work_first PASSED [ 83%]
tests/ip/test_workspace_cleanup.py::test_workspace_creates_the_directory PASSED [ 87%]
tests/ip/test_workspace_cleanup.py::test_workspace_is_emptied_on_entry PASSED [ 90%]
tests/ip/test_workspace_cleanup.py::test_workspace_is_emptied_after_a_forced_exception PASSED [ 93%]
tests/ip/test_workspace_cleanup.py::test_workspace_is_emptied_on_a_clean_exit PASSED [ 96%]
tests/ip/test_workspace_cleanup.py::test_empty_removes_nested_trees_and_tolerates_a_missing_directory PASSED [100%]

============================= 31 passed in 0.69s ==============================
```

**Result: 31/31 passed, 0 failed, 0 skipped.** In particular:

- `test_ip_scan.py::test_the_real_repository_is_clean` — the scanner (`pipeline`'s IP-scan
  utility) was run against **this actual repository's committed tree**, not only a synthetic
  fixture, and found no markup/entity/publisher-wording violation anywhere in it.
- `test_no_raw_source_committed.py`'s five tests — `test_nothing_under_work_is_tracked`,
  `test_no_csv_is_tracked_outside_fixtures`, `test_no_html_is_tracked_outside_fixtures`,
  `test_the_fixture_files_that_do_exist_are_declared_synthetic`, and
  `test_gitignore_still_excludes_work_first` — together confirm the two structural invariants the
  README states (`work/` is gitignored and holds nothing tracked; no CSV or HTML lives outside
  `fixtures/`, and everything that does is declared synthetic) hold against the real, current
  commit, not merely in a unit test's synthetic setup.

## Check 2 — no endorsement-claim language in the README or any repo-description string

Two greps, both against the actual working tree at the commit above.

**2a. Repository-wide for endorsement-adjacent phrasing** (`officially licensed`,
`endorsed by`, `approved by Games Workshop`, `partnership with`, `sponsored by`,
`affiliated with Games Workshop`):

```bash
grep -rInE "officially licensed|endorsed by|approved by Games Workshop|partnership with|sponsored by|affiliated with Games Workshop" \
  --exclude-dir=.git --exclude-dir=.venv .
```

Output:

```text
./docs/operational-readiness.md:45:is not official, is not licensed, and is not endorsed by, or affiliated with, any publisher of the
./README.md:22:**This project is not official, is not licensed, and is not endorsed by, or affiliated with,
./wargame_rules_data.egg-info/PKG-INFO:41:**This project is not official, is not licensed, and is not endorsed by, or affiliated with,
```

**Every match is the negation statement itself** — README.md's own explicit non-endorsement
disclaimer (`## What this is not`), a direct quotation of it inside this session's own
`docs/operational-readiness.md` (task T157), and `PKG-INFO`, which is `setuptools`' own build
artifact copying the README verbatim as the package's long description, not separately authored
content. No occurrence is an actual claim of endorsement, license, or affiliation; every one
states the opposite.

**2b. The declared repository description** (`docs/repo-settings.md`, the reviewable source of
truth for the live GitHub repository description, since this is not something expressible as a
file in the repository itself):

```text
"Curated, IP-stripped mechanical rules data for WargameCompanion - versioned JSON snapshots"
```

Factual: names what the data is (curated, IP-stripped, mechanical rules data) and what it is for
(a companion app), makes no claim about the source publisher, and contains no endorsement,
license, or affiliation language of any kind. `docs/repo-settings.md`'s own table already
annotates this line "factual, makes no endorsement claim (FR-050)" — this check independently
confirms that annotation is accurate by reading the actual string rather than trusting the
annotation.

**2c. `displayName` — the one player-visible string this pipeline emits at runtime**, checked
separately from repository description text because it is what a consumer of the *data*, not the
repository, actually sees:

```bash
grep -rIn "displayName" --exclude-dir=.git --exclude-dir=.venv .
```

Output (trimmed to the entries that carry an actual value, not code that merely names the field):

```text
./docs/verification/withdrawal-rehearsal.md:64:  "displayName": "Warhammer 40,000 11th Edition rehearsal-2026-08",
./fixtures/disagreements/previous/site/manifest.json:6:      "displayName": "Invented Baseline 2026.05",
```

Both are factual version labels (an edition name plus a version identifier); neither claims
official status, endorsement, or affiliation. `pipeline/build/manifest.py`'s own `ManifestError`
guard (`"displayName is player-visible and may not be empty"`) is a completeness check, not a
content check — this grep is the check that its actual committed and fixture-emitted values carry
no endorsement language.

**Result: no endorsement-claim language found anywhere in the repository.**

## Check 3 — `robots.txt`-honouring and never-escalate-on-refusal are real, in `pipeline/acquire/http.py`

Read in full. Both behaviours are implemented, not merely documented in the module docstring.

**`robots.txt` is fetched once per host and honoured** — `pipeline/acquire/http.py:195-219`:

- `_robots_for` (lines 195-214) fetches `{host}/robots.txt` via `_request_once` with
  `check_robots=False` (avoiding infinite recursion into itself), parses it with
  `urllib.robotparser.RobotFileParser` if the fetch succeeds with a `200`, and **caches the
  result per host** (`self._robots[host]`, checked at line 202 before any fetch) so it is
  consulted, not re-fetched, on every subsequent request to that host.
- `_check_robots` (lines 216-219) calls `parser.can_fetch(USER_AGENT, url)` and raises
  `RobotsDisallowed` — a subclass of `AcquisitionError` mapped to
  `ExitCode.SOURCE_UNAVAILABLE` (exit `40`) — if the parsed rules disallow the path. The
  docstring at line 219 names this "the sweep stops here (FR-007)": a disallowed path is a raised
  exception ending the run, not a silently skipped page.
- `_request_once` (lines 223-238) calls `_check_robots` unconditionally at the top of every real
  request when `check_robots=True` (the default `get()` always passes this), so **no acquisition
  request bypasses the robots check** — it is not opt-in per call site.
- A missing or unreadable `robots.txt` is read as "no rules stated" (allow-all), documented at
  lines 196-201 as the standard, and the conservative, reading — refusing every source without a
  robots file would itself be a policy overreach the code deliberately avoids.

**Retries never escalate on refusal** — `pipeline/acquire/http.py:57-58, 232-238, 256-282`:

- `REFUSAL_STATUSES: Final[frozenset[int]] = frozenset({403, 429})` (line 58) is the closed set of
  status codes the module treats as "the source is refusing," and the docstring at lines 13-16
  states the rule this exists to serve: *"A `403` or `429` raises immediately, no retry, and
  latches the client closed so no further request is made against that host."*
- `_request_once` (lines 223-238): on a `REFUSAL_STATUSES` response, the host is added to
  `self._refused_hosts` (line 233) and `SourceRefused` is raised immediately (lines 234-237) —
  there is no retry loop inside this method for a refusal; it is a direct raise from the single
  attempt.
- `get()`'s retry loop (lines 261-282): the `except SourceRefused: raise` at line 266-267 is the
  concrete never-escalate guarantee — a refusal caught inside the loop is **re-raised
  immediately**, skipping every remaining attempt in `range(attempts)`, in explicit contrast to
  the next `except` clause, `except SourceUnreachable` (lines 270-271), which **does** `continue`
  to the next attempt up to `WGC_MAX_RETRIES`. The comment on line 267, *"A refusal is never
  retried. That is the whole rule,"* is the code's own statement of the behaviour this check
  confirms is real, not aspirational.
- `get()` also checks `self._refused_hosts` **before** making any request at all (lines 256-259):
  once a host has refused once during a run, every subsequent `get()` call against that host
  raises `SourceRefused` immediately without a second network request — refusal latches for the
  remainder of the run, exactly as the module docstring claims.
- `RobotsDisallowed`, raised from `_check_robots` inside `_request_once`, is likewise re-raised
  without retry at `get()`'s `except RobotsDisallowed: raise` (line 268-269) — a robots-disallowed
  path is treated with the same never-escalate discipline as an explicit `403`/`429`.

**Result: both behaviours are real and match their documentation exactly, confirmed by line
number, not merely by reading the module docstring's claims about itself.**

## Verdict

All three checks pass with no exceptions:

1. `pytest tests/ip/ -v` — **31 passed**, including the two named tests
   (`test_ip_scan.py`'s and `test_no_raw_source_committed.py`'s full suites) run against the real
   repository tree, not only synthetic fixtures.
2. No endorsement-claim language exists anywhere in the repository — the only matches for
   endorsement-adjacent phrasing are the README's own explicit disclaimer (and its restatement in
   `docs/operational-readiness.md` and the auto-generated `PKG-INFO`), the declared repository
   description is factual, and the two committed/fixture `displayName` values are plain version
   labels.
3. `pipeline/acquire/http.py`'s robots.txt-honouring (lines 195-219) and never-escalate-on-refusal
   (lines 57-58, 223-238, 260-282) behaviours are implemented exactly as documented, cited by line
   number above.

This closes out spec.md's *Policy and Safety Constraints* section, Constitution Principle 4, and
SC-003 for this audit pass. It should be re-run (the same three checks, same commands) whenever
`pipeline/acquire/http.py`, the README, or the repository description changes, rather than trusted
to still hold indefinitely from this one dated run.
