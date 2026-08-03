# AI-Assisted: Claude Code (model: claude-opus-5) - Shared pytest fixtures (task T038):
# fixture-set discovery, a run_cli helper asserting exit codes, a temporary-repository factory
# for publication tests, and a session-wide guard that fails any test which opens a socket.
"""Shared test fixtures.

The socket guard is the important one. The whole suite is supposed to run offline — that is
what ``--offline`` and the synthetic fixture sets are for — so a test that reaches the network
is a bug in the test *or* a bug in the politeness layer, and either way it should fail loudly
rather than pass slowly on a good day and flake on a bad one.
"""

from __future__ import annotations

import socket
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path

import pytest

from pipeline.cli import main as cli_main
from pipeline.config import PipelineConfig, load_config

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_ROOT = REPO_ROOT / "fixtures"


class SocketAccessError(RuntimeError):
    """A test tried to open a network connection."""


@pytest.fixture(autouse=True, scope="session")
def _no_sockets() -> Iterator[None]:
    """Fail any test that opens a socket.

    Autouse and session-scoped so it cannot be forgotten. ``pytest-httpx`` intercepts at the
    transport layer and never reaches here, so mocked HTTP still works.
    """
    real_connect = socket.socket.connect
    real_create_connection = socket.create_connection

    def _blocked_connect(self: socket.socket, address: object) -> None:
        raise SocketAccessError(
            f"a test attempted a network connection to {address!r}; the suite runs offline "
            "(use --offline, --fixtures, or pytest-httpx)"
        )

    def _blocked_create_connection(address: object, *args: object, **kwargs: object) -> None:
        raise SocketAccessError(
            f"a test attempted a network connection to {address!r}; the suite runs offline"
        )

    socket.socket.connect = _blocked_connect  # type: ignore[method-assign, assignment]
    socket.create_connection = _blocked_create_connection  # type: ignore[assignment]
    try:
        yield
    finally:
        socket.socket.connect = real_connect  # type: ignore[method-assign]
        socket.create_connection = real_create_connection  # type: ignore[assignment]


@pytest.fixture
def fixture_set() -> Callable[[str], Path]:
    """Resolve a fixture set by name, skipping the test when the set has not landed yet."""

    def _resolve(name: str) -> Path:
        path = FIXTURES_ROOT / name
        if not path.is_dir():
            pytest.skip(f"fixture set {name!r} does not exist yet ({path})")
        return path

    return _resolve


@pytest.fixture
def config() -> PipelineConfig:
    """A configuration resolved from documented defaults only — no ambient environment.

    Passing an empty environment matters: a developer with ``WGC_*`` variables exported would
    otherwise get different test behaviour than CI, which is the classic "works on my machine".
    """
    return load_config(env={})


@pytest.fixture
def run_cli() -> Callable[..., int]:
    """Invoke the CLI and assert its exit code.

    ``run_cli(["build", "--offline"], expect=60)`` returns the code and fails the test if it
    differs, so a test reads as an assertion about the operator contract rather than about
    process plumbing.
    """

    def _run(argv: Sequence[str], *, expect: int | None = None) -> int:
        code = cli_main(list(argv))
        if expect is not None:
            assert code == expect, f"{' '.join(argv)} exited {code}, expected {expect}"
        return code

    return _run


@pytest.fixture
def temp_repo(tmp_path: Path) -> Callable[[], Path]:
    """Create a throwaway repository tree with the directories the pipeline writes to.

    Publication and workspace tests need a root that looks like the repository without being
    it — writing to the real ``state/`` or ``site/`` from a test would be a very quiet way to
    corrupt the ledger.
    """

    def _make() -> Path:
        root = tmp_path / f"repo-{len(list(tmp_path.iterdir()))}"
        for relative in (
            "data/wh40k-11e/factions",
            "curation/abilities",
            "reports",
            "state",
            "site/prerelease",
            "work",
        ):
            (root / relative).mkdir(parents=True, exist_ok=True)
        return root

    return _make
