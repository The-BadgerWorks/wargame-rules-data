# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the FR-004 pre-request
# disallowed-path deny-list (004 task T003): the two paths the source's published crawling rules
# forbid, checked before a request is constructed so a disallowed path issues zero requests
# (research D1a, verified again by the T002 markup spike).
"""The pre-request path deny-list.

`002` recorded the source's crawling permissions as "verified ``Allow: /``". `004`'s research
(D1a) re-read the file and found that is **not** what it says: the previous-edition tree — the
exact path the previous edition's bulk export sits under — is explicitly `Disallow`ed, as is the
underscore-suffixed staging tree. The current-edition tree is not listed and is therefore
permitted, and its sitemap is advertised in the same group. Moving the detail source onto it is
what brings this pipeline into demonstrable compliance, which makes FR-004 **a compliance fix as
well as an enrichment**.

**Why this exists when :mod:`pipeline.acquire.http` already fetches and honours ``robots.txt``.**
That check is the right general mechanism and is unchanged. It is not sufficient as the control
for a path we *already know* is forbidden, because every one of these reopens it:

* an unreachable or truncated ``robots.txt`` — which :mod:`~pipeline.acquire.http` reads, quite
  correctly, as "no rules stated";
* a future edit that drops or renames a rule;
* any code path that fetches without going through the honouring check.

So the deny-list is evaluated **before a request is constructed**, refuses with a named
diagnostic, and issues **zero requests** — which is precisely what `spec.md`'s verification plan
asks to be demonstrated. It is deliberately a *short, closed list of paths this pipeline could
plausibly be pointed at*, not a second `robots.txt` parser: duplicating the file would create two
sources of truth, while two named prefixes are auditable at a glance.

The check is **host-agnostic**. A mirror, a proxy, or a rehosted copy serving the same path is
serving the same forbidden tree, and matching on the path alone means a changed host cannot
quietly route around the guard.
"""

from __future__ import annotations

import re
from typing import Final
from urllib.parse import unquote, urlparse

from pipeline.acquire.http import AcquisitionError
from pipeline.exit_codes import ExitCode

#: The paths the source's published crawling rules forbid, as read from the live ``robots.txt``
#: on 2026-08-05 (research D1a; re-confirmed by ``docs/verification/html-markup-spike.md``).
#: ``/wh40k11ed/`` — the current-edition tree this feature moves onto — is **not** listed there
#: and is therefore permitted; it must never be added here.
DISALLOWED_PATH_PREFIXES: Final[tuple[str, ...]] = (
    "/wh40k10ed/",
    "/wh40k11ed_/",
)

_SLASH_RUN: Final = re.compile(r"/{2,}")


class DisallowedPath(AcquisitionError):
    """A request for a path the source's published crawling rules forbid (FR-004).

    An **invocation** error rather than a source failure, in the same sense as
    :class:`~pipeline.acquire.http.OfflineViolation`: nothing is wrong upstream: the run asked
    for something the source has said it may not have. The finding code is ``SRC-REFUSED``
    because that is what the catalogue already names for "the source refuses us this", and the
    exit code is ``CONFIG_ERROR`` because the fix is to the invocation, never to a retry.
    """

    finding_code = "SRC-REFUSED"
    exit_code = ExitCode.CONFIG_ERROR


def normalised_path(url: str) -> str:
    """The comparison form of ``url``'s path.

    Percent-encoding is decoded, repeated slashes collapse, and the result is casefolded, so
    ``/WH40K10ED/x``, ``//wh40k10ed//x``, and ``/wh40k10ed%2Fx`` all compare as the one path
    they resolve to. A bare path with no scheme or host is accepted unchanged, so a caller may
    check a path it has not yet joined to a base URL.
    """
    path = urlparse(url).path or "/"
    decoded = unquote(path)
    collapsed = _SLASH_RUN.sub("/", decoded)
    if not collapsed.startswith("/"):
        collapsed = "/" + collapsed
    return collapsed.casefold()


def disallowed_prefix(url: str) -> str | None:
    """The deny-list prefix ``url`` falls under, or ``None`` when it is permitted.

    Returned rather than a bare boolean so the diagnostic can name *which* rule was hit — a
    reader of a failed run should not have to guess which tree they pointed at.
    """
    path = normalised_path(url)
    for prefix in DISALLOWED_PATH_PREFIXES:
        # The trailing-slash-less form is covered too: a request for the directory itself is a
        # request for the tree, and the source's own server answers it with a redirect into it.
        if path == prefix.rstrip("/") or path.startswith(prefix):
            return prefix
    return None


def assert_path_permitted(url: str) -> str:
    """Return ``url`` when its path is permitted, else raise :class:`DisallowedPath`.

    Call this **before** constructing a request. It performs no I/O of its own, which is what
    makes "zero requests were issued" a property of the code rather than of a test fixture.
    """
    prefix = disallowed_prefix(url)
    if prefix is not None:
        raise DisallowedPath(
            f"the source's published crawling rules disallow {prefix} — refusing to request it "
            "(FR-004). No request was issued. The current-edition tree /wh40k11ed/ is the "
            "permitted path; set WGC_DETAIL_SOURCE_URL to it."
        )
    return url
