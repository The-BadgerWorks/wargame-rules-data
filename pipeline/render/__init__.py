# AI-Assisted: Claude Code (model: claude-sonnet-5) - New subpackage (007 task T044, plan.md
# Structure Decision #3): the reference implementation of
# `WargameCompanion:specs/007-loadout-display-fidelity/contracts/rendering-contract.md` v1.0.0.
# Belongs to no pipeline stage -- it is a pure function of curated/bundle data, not a stage of
# its own; `validate` will be its first caller (US5, a later phase).
"""The loadout rendering contract's reference implementation."""

from __future__ import annotations
