# AI-Assisted: Claude Code (model: claude-opus-5) - Curate stage package (tasks T064, T065).
"""The ``curate`` stage: read authored content, write the curated tree.

The stage exists on one side of a boundary that never moves. **The pipeline writes ``data/``
and never ``curation/``; humans write ``curation/`` and never hand-edit ``data/``.** That is
what makes FR-017's and FR-024's carry-forward guarantees structural rather than procedural: a
rebuild rewrites ``data/`` wholesale and *physically cannot* clobber an authored ability
summary, because no code path in this package opens a ``curation/`` file for writing.
"""
