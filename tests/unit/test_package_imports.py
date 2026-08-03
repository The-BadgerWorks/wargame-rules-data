# AI-Assisted: Claude Code (model: claude-sonnet-5) - Minimal smoke test so `pytest` collects
# and passes against the otherwise-empty package during the Setup phase (task T010's CI
# checkpoint: "CI is green on an empty package").
"""Smoke test: the pipeline package imports cleanly."""

import pipeline


def test_pipeline_package_imports() -> None:
    assert pipeline.__all__ == []
