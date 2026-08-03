# AI-Assisted: Claude Code (model: claude-opus-5) - Publish stage package (task T071).
"""The ``publish`` stage: the only code path in the repository that writes a consumer artifact.

That exclusivity is the control, not a description of it. `candidate.yml` has no credential and
no path that reaches Releases or Pages, so FR-052's "automated runs must not publish" holds by
**capability** rather than by policy — and FR-040's "rejection creates no consumer-visible
artifact" follows for free, because declining the environment approval means this code never
runs.
"""
