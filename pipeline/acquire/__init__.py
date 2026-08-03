# AI-Assisted: Claude Code (model: claude-opus-5) - Package marker for the acquire stage,
# created alongside the polite HTTP client (task T027) and the fixture adapter (task T037).
"""The ``acquire`` stage: retrieval, and the politeness rules that govern it.

Two source adapters produce the same :class:`~pipeline.models.source.SourceAcquisition` records:
:mod:`pipeline.acquire.http` against the live upstreams, and
:mod:`pipeline.acquire.fixtures` against a synthetic tree. **There is no CI-only code path** —
a curator reproduces any run, and any failure, on a laptop
(``contracts/pipeline-run-interface.md`` §1).

Acquired material lands in ``work/`` and nowhere else (FR-010).
"""
