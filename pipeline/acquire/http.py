# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the polite HTTP client
# (task T027): per-host rate limiting with jitter, a retry ceiling that never escalates on
# refusal, robots.txt fetch-and-honour, a browser User-Agent with Accept-Language: en, and an
# --offline mode that raises rather than opening a socket (FR-007, research D4a).
# AI-Assisted: Claude Code (model: claude-opus-5) - Wired pipeline.acquire.robots' pre-request
# deny-list ahead of both the --offline check and the robots.txt fetch-and-honour check, so a
# disallowed path issues zero requests and cannot be reopened by a permissive or unreachable
# robots.txt (004 task T005, FR-004).
"""The polite HTTP client.

FR-007 is not a performance setting, it is a behaviour contract: request politely, honour
``robots.txt``, and **stop rather than evade** when a source refuses. Everything here follows
from that.

* **Rate limiting is per host**, at ``WGC_REQUEST_INTERVAL_MS`` plus jitter. Jitter exists so a
  sweep does not present as a metronome; it only ever *adds* delay.
* **Retries never escalate on refusal.** A ``403`` or ``429`` raises immediately, no retry, and
  latches the client closed so no further request is made against that host. Retrying a refusal
  is the definition of evading one. Transient transport failures and ``5xx`` responses are
  retried up to ``WGC_MAX_RETRIES``, at the same polite interval — never faster.
* **A closed deny-list of paths is refused before a request is constructed.** The detail
  source's published rules forbid two trees outright (`004` research D1a), and the check for
  them runs ahead of everything else here — including the ``robots.txt`` fetch — so no
  permissive edit, truncated response, or unreachable ``robots.txt`` can reopen them
  (FR-004). See :mod:`pipeline.acquire.robots`.
* **``robots.txt`` is fetched once per host and honoured.** A disallowed path stops the sweep
  with a named diagnostic rather than being skipped quietly. (The points source's
  ``robots.txt`` is ``Allow: /`` — research §0.2 records that as the evidence for automated
  retrieval being permitted, not as a reason to skip the check.)
* **``--offline`` raises rather than opening a socket.** This is the mode fixture tests run in,
  so "the test suite made a network request" is a failure with a stack trace rather than a
  flake.

Errors carry the finding code and the exit code the contract assigns them, so the CLI maps a
failure to an exit status without re-deriving the mapping.
"""

from __future__ import annotations

import random
import time
import urllib.robotparser
from collections.abc import Callable, Mapping
from types import TracebackType
from typing import Final
from urllib.parse import urlparse

import httpx

from pipeline.config import PipelineConfig
from pipeline.exit_codes import ExitCode

#: A browser User-Agent and an explicit language, as research D4a specifies. The points source
#: serves different markup to unrecognised agents, so this is a correctness requirement as much
#: as a courtesy one.
USER_AGENT: Final = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS: Final[Mapping[str, str]] = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en",
}

#: Status codes that mean "the source is refusing". Never retried (FR-007).
REFUSAL_STATUSES: Final[frozenset[int]] = frozenset({403, 429})

#: Fraction of the configured interval added, at most, as jitter.
JITTER_FRACTION: Final = 0.25

DEFAULT_TIMEOUT_SECONDS: Final = 30.0


class AcquisitionError(RuntimeError):
    """A retrieval failure that ends the run, carrying its finding code and exit code."""

    finding_code: str = "SRC-UNREACHABLE"
    exit_code: ExitCode = ExitCode.SOURCE_UNAVAILABLE


class SourceRefused(AcquisitionError):
    """The source refused or throttled us. The run stops; it does not evade (FR-007)."""

    finding_code = "SRC-REFUSED"
    exit_code = ExitCode.SOURCE_UNAVAILABLE


class SourceUnreachable(AcquisitionError):
    """The source did not respond within the retry ceiling (FR-008)."""

    finding_code = "SRC-UNREACHABLE"
    exit_code = ExitCode.SOURCE_UNAVAILABLE


class RobotsDisallowed(AcquisitionError):
    """``robots.txt`` disallows the path. The sweep stops rather than skipping quietly."""

    finding_code = "SRC-REFUSED"
    exit_code = ExitCode.SOURCE_UNAVAILABLE


class OfflineViolation(AcquisitionError):
    """A network request was attempted in ``--offline`` mode.

    An invocation error, not a source failure: nothing is wrong upstream, the run asked for
    something ``--offline`` forbids.
    """

    finding_code = "SRC-UNREACHABLE"
    exit_code = ExitCode.CONFIG_ERROR


def _host_of(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _assert_path_permitted(url: str) -> None:
    """Refuse a deny-listed path before a request is constructed (FR-004).

    The import is deferred rather than module-level because
    :class:`pipeline.acquire.robots.DisallowedPath` subclasses this module's
    :class:`AcquisitionError` — so that the CLI's single ``except AcquisitionError`` maps it to
    an exit code like every other retrieval failure — and a module-level import here would
    close the cycle. The lookup is a ``sys.modules`` hit; the guard performs no I/O.
    """
    from pipeline.acquire.robots import assert_path_permitted

    assert_path_permitted(url)


class PoliteClient:
    """A rate-limited, ``robots.txt``-honouring HTTP client.

    Args:
        config: supplies ``WGC_REQUEST_INTERVAL_MS`` and ``WGC_MAX_RETRIES``.
        offline: when true every request raises :class:`OfflineViolation` before a socket is
            opened.
        client: an ``httpx.Client`` to use instead of one of our own — the injection point for
            tests and for a caller that needs its own transport.
        sleep: the delay function; injected so a test can assert the interval was observed
            without spending it.
        monotonic: the clock; injected for the same reason.
        jitter: returns the extra delay in seconds. Injected so tests are deterministic.
    """

    def __init__(
        self,
        config: PipelineConfig,
        *,
        offline: bool = False,
        client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
        jitter: Callable[[], float] | None = None,
    ) -> None:
        self._config = config
        self._offline = offline
        self._client = client
        self._owns_client = client is None
        self._sleep = sleep
        self._monotonic = monotonic
        interval_seconds = config.request_interval_ms / 1000.0
        self._interval = interval_seconds
        self._jitter = (
            jitter
            if jitter is not None
            else (
                lambda: random.uniform(0.0, interval_seconds * JITTER_FRACTION)  # noqa: S311
            )
        )
        self._last_request_at: dict[str, float] = {}
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self._refused_hosts: set[str] = set()
        self.request_count = 0

    # -- lifecycle ---------------------------------------------------------------------

    def __enter__(self) -> PoliteClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying client if this instance created it."""
        if self._owns_client and self._client is not None:
            self._client.close()
            self._client = None

    def _http(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                headers=dict(DEFAULT_HEADERS),
                timeout=DEFAULT_TIMEOUT_SECONDS,
                follow_redirects=True,
            )
        return self._client

    # -- politeness --------------------------------------------------------------------

    def _throttle(self, host: str) -> None:
        """Wait out the remainder of the polite interval for ``host``, plus jitter."""
        last = self._last_request_at.get(host)
        now = self._monotonic()
        if last is not None:
            wait = self._interval + self._jitter() - (now - last)
            if wait > 0:
                self._sleep(wait)
        self._last_request_at[host] = self._monotonic()

    def _robots_for(self, host: str) -> urllib.robotparser.RobotFileParser | None:
        """Fetch and parse ``robots.txt`` once per host.

        A missing or unreadable ``robots.txt`` means "no rules stated", which is allow-all —
        the standard reading, and the conservative one is not available: refusing every source
        without a robots file would stop the pipeline against a source that never objected.
        """
        if host in self._robots:
            return self._robots[host]

        parser: urllib.robotparser.RobotFileParser | None = None
        try:
            response = self._request_once(f"{host}/robots.txt", host=host, check_robots=False)
        except AcquisitionError:
            response = None
        if response is not None and response.status_code == 200:
            parser = urllib.robotparser.RobotFileParser()
            parser.parse(response.text.splitlines())
        self._robots[host] = parser
        return parser

    def _check_robots(self, url: str, host: str) -> None:
        parser = self._robots_for(host)
        if parser is not None and not parser.can_fetch(USER_AGENT, url):
            raise RobotsDisallowed(f"robots.txt disallows {url}; the sweep stops here (FR-007)")

    # -- requests ----------------------------------------------------------------------

    def _request_once(self, url: str, *, host: str, check_robots: bool) -> httpx.Response:
        # FR-004, ahead of the robots.txt honouring check and unconditional on `check_robots`:
        # the deny-list must not be bypassable by a permissive or unreachable robots.txt, and
        # this is the one funnel every request in this client passes through — including the
        # robots.txt fetch itself, which reaches here with `check_robots=False`.
        _assert_path_permitted(url)
        if check_robots:
            self._check_robots(url, host)
        self._throttle(host)
        self.request_count += 1
        try:
            response = self._http().get(url)
        except httpx.HTTPError as exc:
            raise SourceUnreachable(f"transport failure for {url}: {type(exc).__name__}") from exc
        if response.status_code in REFUSAL_STATUSES:
            self._refused_hosts.add(host)
            raise SourceRefused(
                f"{host} responded {response.status_code}; the run stops rather than evading "
                "(FR-007). No further request is made against this host."
            )
        return response

    def get(self, url: str) -> httpx.Response:
        """Fetch ``url`` politely.

        Raises:
            OfflineViolation: the client is offline.
            SourceRefused: the host refused or throttled, now or earlier in this run.
            RobotsDisallowed: ``robots.txt`` disallows the path.
            SourceUnreachable: the retry ceiling was reached without a usable response.
            DisallowedPath: the source's published rules forbid this path (FR-004).
        """
        # First of all, and ahead of the offline check: a disallowed path is disallowed in
        # every mode, and an offline run must report the policy violation it actually made
        # rather than the network access it incidentally also attempted.
        _assert_path_permitted(url)

        if self._offline:
            raise OfflineViolation(
                f"--offline forbids network access; refusing to request {url}. "
                "Use --fixtures to source from a synthetic tree."
            )

        host = _host_of(url)
        if host in self._refused_hosts:
            raise SourceRefused(
                f"{host} already refused this run; no further request is made against it (FR-007)"
            )

        attempts = self._config.max_retries + 1
        last_error: AcquisitionError | None = None
        for _ in range(attempts):
            try:
                response = self._request_once(url, host=host, check_robots=True)
            except SourceRefused:
                raise  # A refusal is never retried. That is the whole rule.
            except RobotsDisallowed:
                raise
            except SourceUnreachable as exc:
                last_error = exc
                continue
            if response.status_code >= 500:
                last_error = SourceUnreachable(
                    f"{url} responded {response.status_code} after {self.request_count} requests"
                )
                continue
            if response.status_code >= 400:
                raise SourceUnreachable(f"{url} responded {response.status_code}")
            return response

        raise last_error or SourceUnreachable(f"{url} did not respond within the retry ceiling")
