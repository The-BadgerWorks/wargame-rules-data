# AI-Assisted: Claude Code (model: claude-opus-5) - Defined EntityProvenance with the derived
# is_hybrid_edition property and the three-state PricingConfidence machine of data-model.md §5
# (task T024).
"""Provenance and pricing confidence — carried by **every** curated entity, not only disputed
ones.

Two producer-side guarantees made expressible in the artifact:

* :class:`EntityProvenance` records which acquisition supplied which half of an entity. Only
  ``detail_edition_code`` is emitted to the bundle (contract v1.2.0, C5/R4), which is enough to
  make a hybrid entity self-describing; the rest stays producer-side because no consumer reads
  it.
* :class:`PricingConfidence` states how much the producer trusts a price. ``unverified`` is
  **advisory**: the unit ships with the best price known, never withheld and never dropped
  (FR-035). ``unpriced`` is the only pricing state that blocks, because there is no value to
  publish at all (FR-026).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from pipeline.models.source import SourceKey


class PointsSource(StrEnum):
    """Where an entity's points came from this release."""

    MFM = SourceKey.MFM.value
    LAST_KNOWN = "last_known"
    """Carried forward: the authoritative source did not publish the unit this release."""

    NONE = "none"


class DetailSource(StrEnum):
    """Where an entity's datasheet detail came from."""

    WAHAPEDIA = SourceKey.WAHAPEDIA.value
    NONE = "none"


class PricingConfidenceState(StrEnum):
    """The closed pricing-confidence set (``reference-db-schema.md`` §3.3).

    ``verified`` and ``unverified`` are the two the consumer contract carries; ``unpriced`` is
    producer-side and blocking, because a datasheet with no price from any source, ever, cannot
    be published at all.
    """

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    UNPRICED = "unpriced"


class EntityProvenance(BaseModel):
    """Which acquisition, and which declared edition, supplied each half of an entity."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    points_source: PointsSource
    points_acquisition_id: str | None = None
    points_edition_code: str
    detail_source: DetailSource
    detail_acquisition_id: str | None = None
    detail_edition_code: str

    @property
    def is_hybrid_edition(self) -> bool:
        """Derived: the detail came from a different edition than the points (FR-060).

        Never stored — a stored copy is a second source of truth that can go stale. At launch
        this is the *normal* case, not an edge case: the points source is 11th Edition and the
        detail export is 10th (research §0.1).
        """
        return self.detail_edition_code != self.points_edition_code

    @property
    def emitted_detail_edition_code(self) -> str | None:
        """What ``datasheet.detail_edition_code`` carries: the code, or absent when same-edition.

        ``curated-snapshot-format.md`` §5: a same-edition datasheet **omits** the field rather
        than repeating the snapshot's own edition.
        """
        return self.detail_edition_code if self.is_hybrid_edition else None


class PricingConfidence(BaseModel):
    """The ``verified | unverified | unpriced`` state and its carry-forward bookkeeping.

    Transitions (data-model.md §5.2)::

        verified   --authoritative source silent this release-->  unverified
        unverified --authoritative source publishes it again-->   verified  (cleared
                                                                   automatically, FR-035a)
        (no price from any source, ever) -------------------->    unpriced  (BLOCKING)

    ``consecutive_unverified_releases`` escalates past ``WGC_UNVERIFIED_ESCALATE_RELEASES`` to
    the advisory ``PRC-UNVERIFIED-STALE``, which is the early signal that a unit has quietly
    left the authoritative source's listing.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    state: PricingConfidenceState
    unverified_since_version: str | None = Field(
        default=None, description="the rulesVersionId at which the unit first fell back"
    )
    consecutive_unverified_releases: int = 0
    last_verified_version: str | None = None
    last_verified_points_digest: str | None = Field(
        default=None, description="sha256 over the carried-forward values"
    )

    @property
    def is_blocking(self) -> bool:
        """Only ``unpriced`` blocks publication (FR-026)."""
        return self.state is PricingConfidenceState.UNPRICED
