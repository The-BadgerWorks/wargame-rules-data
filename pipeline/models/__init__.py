# AI-Assisted: Claude Code (model: claude-opus-5) - Package marker for the typed record spine
# (tasks T020-T025), organised by the stage that owns each family per data-model.md.
"""The pipeline's typed records, grouped by the stage that owns them.

The controlling rule is the **IP boundary** (data-model.md, research D8):

* :mod:`pipeline.models.source` records may hold publisher prose. They exist only in memory and
  in ephemeral ``work/`` and are never committed.
* Everything downstream — :mod:`~pipeline.models.normalized`, :mod:`~pipeline.models.curated`,
  :mod:`~pipeline.models.authored`, :mod:`~pipeline.models.provenance`,
  :mod:`~pipeline.models.findings` — has **no field typed to hold prose**. The policy holds by
  schema design rather than by review vigilance.

:mod:`pipeline.models.mechanical` carries the shared guard that makes "no prose here" checkable
rather than merely intended.
"""
