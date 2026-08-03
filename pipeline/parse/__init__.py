# AI-Assisted: Claude Code (model: claude-opus-5) - Parse stage package (tasks T057-T059).
"""The ``parse`` stage: acquired bytes to structured source records.

Together with ``acquire`` this is one of the only two stages permitted to read the publisher's
prose fields (research D8). Everything it hands downstream is a
:mod:`pipeline.models.source` record, and ``normalize`` is the last place those records' prose
fields are ever read.
"""
