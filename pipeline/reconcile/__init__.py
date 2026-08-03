# AI-Assisted: Claude Code (model: claude-opus-5) - Package marker for the reconcile stage,
# created alongside curated identity minting (task T039).
"""The ``reconcile`` stage: curated identity first, then names, then aliases, then report.

The ladder is deterministic and **no automatic fuzzy match is ever accepted** (research D5).
Edit-distance scoring exists only to rank suggestions for a human inside the report; a
suggestion is never applied. The failure mode this guards against is a silently mispriced unit
in a player's hands at a tournament.
"""
