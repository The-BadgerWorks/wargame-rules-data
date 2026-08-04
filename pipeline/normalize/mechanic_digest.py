# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the canonical home for the
# keyed mechanic digest (task T127): hard normalisation and the HMAC-truncated digest, with the
# key read from configuration and never logged, and the source text discarded the moment the
# digest is taken (FR-013, FR-024, C6/R8).
"""The keyed, truncated mechanic digest — US5's answer to "did the mechanic actually change".

**Why keyed.** A plain sha256 of a short, publicly known string is a verification oracle: anyone
holding a candidate wording can hash it and compare. FR-013 forbids retaining the publisher's
wording anywhere, including version control, and re-review detection naively implies retaining
the previous wording to compare against. A digest keyed under a repository-held secret closes
that gap — it can be neither inverted nor used to confirm a guess — which is what makes FR-024's
change detection cleanly compatible with FR-013 (research D6, C6/R8).

**Why hard-normalised first.** Two texts that differ only in *how* they are written (markup,
whitespace, casing, punctuation) must digest identically, or every markup reflow in the source
would falsely flag every ability using it for re-review. Two texts that differ in what the
mechanic *does* must digest differently.

This module previously lived inside :mod:`pipeline.normalize.ip_strip`, where the digest logic
was first built out to make :class:`~pipeline.models.normalized.NormalizedAbilityBinding`
type-check (T060). It moved here to its own contract path once US5 needed to call it from the
curate and validate stages independently of the IP-strip pipeline; ``ip_strip`` re-exports both
names for backward compatibility so no existing caller needed to change.
"""

from __future__ import annotations

import hashlib
import hmac
import re
import unicodedata
from typing import Final

from pipeline.config import PipelineConfig
from pipeline.normalize.ip_strip import strip_field

#: Punctuation removed before a mechanic digest is taken, so re-punctuation is not a change.
_PUNCTUATION: Final = re.compile(r"[^\w\s]", re.UNICODE)

#: 128 bits, per data-model.md §2. Long enough that a collision is not a practical concern and
#: short enough to keep the curated tree readable.
_DIGEST_BITS: Final = 128


def _collapse(value: str) -> str:
    return " ".join(value.split())


def hard_normalise(text: str) -> str:
    """The presentation-free projection a mechanic digest is taken over.

    Markup gone, entities decoded, `<table>`/`<img>` content dropped, whitespace collapsed,
    casefolded, punctuation stripped. Two texts that differ only in how they are *written*
    produce the same projection; two that differ in what they *do* do not.
    """
    stripped = strip_field(text, field="mechanic").text
    folded = unicodedata.normalize("NFKC", stripped).casefold()
    return _collapse(_PUNCTUATION.sub(" ", folded))


def mechanic_digest(text: str, *, key: bytes) -> str:
    """A keyed, truncated digest of a mechanic. **The text itself is discarded immediately.**

    Keying is the point (C6/R8). An unkeyed hash of a short, publicly known string can be
    *confirmed* by anyone holding the text — you guess the wording, hash it, and compare. A
    keyed digest can be neither inverted nor used to verify a guess, which is what makes
    FR-024's change detection cleanly compatible with FR-013's prohibition on retaining the
    publisher's wording anywhere, even unpublished.
    """
    projection = hard_normalise(text).encode("utf-8")
    return hmac.new(key, projection, hashlib.sha256).hexdigest()[: _DIGEST_BITS // 4]


class DigestKeyMissingError(ValueError):
    """``WGC_MECHANIC_DIGEST_KEY`` is unset. Never logged — the message names no value."""


def resolve_digest_key(config: PipelineConfig) -> bytes:
    """The configured HMAC key as bytes, read once at the point of use and never logged.

    Raises:
        DigestKeyMissingError: the secret is unset. Refusing loudly here is preferable to
            silently keying on an empty string, which would make every digest reproducible by
            anyone — exactly the oracle the keying exists to prevent (C6/R8).
    """
    if not config.mechanic_digest_key:
        raise DigestKeyMissingError(
            "WGC_MECHANIC_DIGEST_KEY is not set; the mechanic digest may not be computed with "
            "an empty key (research D6, C6/R8)"
        )
    return config.mechanic_digest_key.encode("utf-8")
