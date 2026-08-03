# AI-Assisted: Claude Code (model: claude-sonnet-5) - Release-detection package (task T104-T105):
# the presentation-free projection and the digest comparison behind `rules-pipeline detect`.
"""Release detection: parse-then-digest, never version-marker-then-trust (research D4b).

The points source publishes no version field the pipeline can trust (research §0.2), so a
release is detected by projecting each parsed faction page to a canonical, presentation-free
structure and comparing its digest against the last one recorded. A digest moving is the only
signal; nothing here reads or infers a version number from the source.
"""

from __future__ import annotations
