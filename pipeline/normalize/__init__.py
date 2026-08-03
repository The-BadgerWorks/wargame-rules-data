# AI-Assisted: Claude Code (model: claude-opus-5) - Normalize stage package (tasks T060-T063).
"""The ``normalize`` stage: the IP boundary, in one place.

This is the **last** stage permitted to read the publisher's prose fields (research D8).
Everything it emits is a :mod:`pipeline.models.normalized` record, and no field of those records
is typed to hold prose. The invariant downstream is therefore structural rather than
procedural: no stage after this one has ever held publisher wording, so none of them can leak it.
"""
