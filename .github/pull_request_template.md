<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - PR template carrying the Principle 15
     disclosure fields, the Principle 16 AI-Assisted-By trailer reminder, and the change-class
     checkbox the CI guard in tools/check_change_classes.py enforces, per Setup task T015. -->
## Summary

<!-- What does this PR do, and why? -->

## Change class (pick exactly one -- a PR touching more than one fails CI)

- [ ] `pipeline/` + `tests/` -- pipeline code and its tests
- [ ] `data/` -- the machine-written curated tree (normally only from a `candidate/*` branch)
- [ ] `curation/` -- human-authored data (`curation/abilities/` requires a non-author reviewer)
- [ ] infrastructure -- `.github/`, `site/`, `docs/repo-settings.md`

## Checklist

- [ ] No raw acquired source material (a captured MFM page, a Wahapedia CSV, or any excerpt of
      either) is added anywhere in this diff, including in a test fixture. Fixtures are
      synthetic only (FR-010, FR-013).
- [ ] No publisher rules text, stratagems, missions, lore, or artwork appears anywhere in this
      diff. Ability summaries (if any) are original mechanics-only descriptions, never a
      paraphrase of publisher wording (FR-012, FR-013).
- [ ] `ruff check`, `ruff format --check`, `mypy`, and `pytest` all pass locally.
- [ ] If this PR touches a contract in `docs/contracts.md`, the version change is coordinated
      with `001-army-builder-app` and not a unilateral edit.

## Principle 15 -- AI-assistance disclosure

- [ ] This PR's changes were authored, reviewed, or substantially assisted by an AI coding tool.
      If checked, every new or substantially edited file carries an `AI-Assisted:` header
      comment, and this PR's commit(s) carry a matching `AI-Assisted-By:` trailer, e.g.:

  ```text
  AI-Assisted-By: Claude Code (model: <model id>)
  ```

## Verification evidence

<!-- How was this verified? Test output, a report path, a manual step performed, etc. -->
