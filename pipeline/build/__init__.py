# AI-Assisted: Claude Code (model: claude-opus-5) - Package marker for the build stage, created
# alongside the canonical serialiser (task T019).
"""The ``build`` stage: the pure transformation from curated tree to published bundle.

The build takes no network access, no source re-acquisition, and no input the curated tree does
not already contain (``curated-snapshot-format.md`` §3). ``canonical_json`` is the single
serialiser every artifact in this repository is written through, because the manifest checksum
is computed over the bundle's bytes (FR-033, SC-006).
"""
