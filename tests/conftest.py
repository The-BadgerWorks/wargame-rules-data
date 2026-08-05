# AI-Assisted: Claude Code (model: claude-opus-5) - Shared pytest fixtures (task T038):
# fixture-set discovery, a run_cli helper asserting exit codes, a temporary-repository factory
# for publication tests, and a session-wide guard that fails any test which opens a socket.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the run-ledger write guard and the
# `throwaway_repository_root` redirection (004 Phase 3 pre-task), after the suite was found to
# append a `verify` row to the real state/run-ledger.jsonl on every run.
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
from pipeline.observability.ledger import LEDGER_RELATIVE_PATH

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


@pytest.fixture(autouse=True)
def _repository_state_is_read_only() -> Iterator[None]:
    """Fail any test that writes to the repository's own ``state/run-ledger.jsonl``.

    Autouse, like the socket guard, and for the same reason. The ledger's entire value is that
    a line in it means *a real run happened* — silence is a fault signal (FR-054), so a test
    that appends to it corrupts the one artifact nobody can reconstruct. The failure mode is
    quiet: the suite passes, the working tree shows a modified file, and it gets committed
    alongside a code change by someone who assumes the pipeline wrote it.

    The guard is a comparison, not a permission: a test that legitimately exercises a ledger
    write points the code at ``tmp_path`` or at :func:`throwaway_repository_root` instead.
    """
    ledger = REPO_ROOT / LEDGER_RELATIVE_PATH
    before = ledger.read_bytes() if ledger.is_file() else None
    yield
    after = ledger.read_bytes() if ledger.is_file() else None
    if after != before:
        if before is not None:
            ledger.write_bytes(before)
        elif after is not None:
            ledger.unlink()
        raise AssertionError(
            f"this test wrote to {LEDGER_RELATIVE_PATH} in the repository itself. The ledger is "
            "append-only run history; point the code under test at tmp_path or at the "
            "`throwaway_repository_root` fixture. (The file has been restored.)"
        )


@pytest.fixture
def throwaway_repository_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect :func:`pipeline.config.repo_root` at a throwaway tree for the whole CLI.

    ``pipeline.cli`` resolves the repository root once per command and writes the ledger, the
    detection digest, and the channel manifests beneath it. A test invoking a command through
    :func:`pipeline.cli.main` therefore writes into the developer's checkout unless the root is
    redirected — which is exactly the defect this fixture exists to make impossible rather than
    to remember.
    """
    root = tmp_path / "throwaway-repo"
    for relative in (
        "data/wh40k-11e/factions",
        "curation/abilities",
        "reports",
        "state",
        "site/prerelease",
        "work",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("pipeline.cli.repo_root", lambda: root)
    return root


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
