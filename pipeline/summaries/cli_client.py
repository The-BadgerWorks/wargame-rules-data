# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 R7c task 1: a second transport for the
# drafting client that shells out to the Claude Code CLI in print mode, so a drafting run bills
# the Owner's subscription rather than the messages API `client.py` posts to. Same interface
# (`draft`/`review`), plus a batched `review_many` the tool uses to re-review several redrafts in
# one process spawn rather than one per entry.
"""The CLI transport for the drafting and reviewing passes.

Same contract as :class:`pipeline.summaries.client.SummaryClient`: :meth:`CliSummaryClient.draft`
and :meth:`CliSummaryClient.review` ask the same two questions, validate the reply with
``pydantic`` before anything downstream sees it, and never let the reply body reach a log or an
exception message. What differs is the transport: a subprocess call to the ``claude`` CLI in
print mode instead of an HTTP POST, so the request is billed against a Claude Code subscription
seat instead of the Anthropic API.

**Observed CLI behaviour (smoke-tested 2026-09-15, CLI version 2.1.252):** ``--bare`` is
deliberately absent from the argv below. ``claude -p --bare ...`` returns exit 1 with
``is_error: true`` and ``result: "Not logged in · Please run /login"`` — it skips loading the
user's own credentials, which defeats the entire point of this transport (paying against the
subscription rather than a key). Every other flag below was verified working (exit 0) in the same
smoke. ``--tools ""`` only disarms tool use because the user prompt travels on stdin; putting the
prompt on the argv as a positional instead would let the empty string swallow it, so the prompt
stays on stdin here even though nothing else about the call resembles an HTTP body.
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
from collections.abc import Callable, Sequence
from typing import Any, Final, Literal

from pydantic import BaseModel, ValidationError

from pipeline.summaries import prompts
from pipeline.summaries.client import (
    Draft,
    DraftingError,
    Verdict,
    _DraftReply,
    _ReviewReply,
    _validate,
)

LOGGER: Final = logging.getLogger("pipeline.summaries.cli_client")

#: Generous for a subprocess spawn plus a model turn; matches the CLI smoke's own patience.
REQUEST_TIMEOUT_SECONDS: Final = 180

#: "Come back later" for this transport is a phrase in the reply, not a status code — the CLI's
#: print mode reports everything, success or failure, as exit code plus one JSON object. A whole
#: minute rather than `client.py`'s two seconds because a CLI-side rate limit is the subscription
#: seat's shared allowance, not a per-key backoff.
RATE_LIMIT_BACKOFF_SECONDS: Final = 60.0

#: `review_many` batches at most this many triples per call; more than this and the reply's own
#: numbering becomes the harder thing to get right, not the request.
MAX_BATCH_ITEMS: Final = 10


class _ReviewBatchReply(BaseModel):
    verdicts: list[_ReviewReply]


class CliSummaryClient:
    """Drafts and reviews mechanical summaries by shelling out to the Claude Code CLI.

    Args:
        model: the model id passed to ``--model``. As with ``SummaryClient``, the drafting and
            reviewing passes use different models, so a caller building both constructs two
            clients.
        executable: the CLI's name or path. Overridable so a test or an unusual install does not
            need ``claude`` on ``PATH``.
        runner: the subprocess entry point. Defaults to ``subprocess.run``; every test in
            ``tests/unit/test_cli_summary_client.py`` supplies a fake instead, so no test spawns
            the real CLI.
    """

    def __init__(
        self,
        *,
        model: str,
        executable: str = "claude",
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ) -> None:
        self._model = model
        self._executable = executable
        self._runner = runner

    # -- the two passes, plus the batch --------------------------------------------------

    def draft(
        self,
        name: str,
        mechanic_text: str,
        *,
        ability_class: Literal["ability", "detachment_rule"],
        hint: str | None = None,
    ) -> Draft:
        """Restate one mechanic as a summary. Identical contract to ``SummaryClient.draft``."""
        payload = self._run(
            prompts.DRAFT_SYSTEM,
            prompts.draft_user(name, mechanic_text, ability_class, hint=hint),
            prompts.DRAFT_SCHEMA,
            purpose="draft",
        )
        reply = _validate(_DraftReply, payload)
        return Draft(summary=reply.summary, used_verbatim=reply.used_verbatim)

    def review(self, name: str, mechanic_text: str, summary: str) -> Verdict:
        """Ask a second model whether ``summary`` still means what the rules text means."""
        payload = self._run(
            prompts.REVIEW_SYSTEM,
            prompts.review_user(name, mechanic_text, summary),
            prompts.REVIEW_SCHEMA,
            purpose="review",
        )
        reply = _validate(_ReviewReply, payload)
        return Verdict(decision=reply.decision, reason_code=reply.reason_code)

    def review_many(self, items: Sequence[tuple[str, str, str]]) -> list[Verdict]:
        """Review up to :data:`MAX_BATCH_ITEMS` ``(name, mechanic_text, summary)`` triples in
        one call, returning one :class:`Verdict` per item, in the order given.

        Raises:
            DraftingError: ``items`` is empty or longer than :data:`MAX_BATCH_ITEMS`, or the
                reply's verdict list does not have exactly ``len(items)`` entries — always with
                detail ``"cli-batch-shape"``, so a caller never mis-aligns a verdict with the
                wrong item.
        """
        if not items or len(items) > MAX_BATCH_ITEMS:
            raise DraftingError(None, "cli-batch-shape")

        payload = self._run(
            prompts.REVIEW_BATCH_SYSTEM,
            prompts.review_batch_user(items),
            prompts.REVIEW_BATCH_SCHEMA,
            purpose="review_many",
        )
        try:
            reply = _ReviewBatchReply.model_validate(payload)
        except ValidationError as exc:
            raise DraftingError(None, "cli-batch-shape") from exc
        if len(reply.verdicts) != len(items):
            raise DraftingError(None, "cli-batch-shape")
        return [Verdict(decision=v.decision, reason_code=v.reason_code) for v in reply.verdicts]

    # -- transport -----------------------------------------------------------------------

    def _argv(self, system: str, schema: dict[str, Any]) -> list[str]:
        """The CLI invocation. Shape verified by smoke (see module docstring); do not reorder or
        add ``--bare``."""
        return [
            self._executable,
            "-p",
            "--no-session-persistence",
            "--tools",
            "",
            "--model",
            self._model,
            "--system-prompt",
            system,
            "--output-format",
            "json",
            "--json-schema",
            json.dumps(schema),
        ]

    def _run(self, system: str, user: str, schema: dict[str, Any], *, purpose: str) -> Any:
        """Run the CLI once, retrying once on a rate-limit-shaped failure.

        The body is built here and referenced nowhere else: every diagnostic below names the
        purpose, the model and the return code — never the argv's system prompt, never stdin,
        never stdout or stderr.
        """
        argv = self._argv(system, schema)

        for attempt in (1, 2):
            try:
                completed = self._runner(
                    argv,
                    input=user,
                    text=True,
                    encoding="utf-8",
                    timeout=REQUEST_TIMEOUT_SECONDS,
                    capture_output=True,
                )
            except subprocess.TimeoutExpired as exc:
                raise DraftingError(None, "cli") from exc

            try:
                return _payload(completed)
            except DraftingError:
                LOGGER.debug(
                    "cli drafting call did not succeed (purpose=%s, model=%s, "
                    "returncode=%s, attempt=%s)",
                    purpose,
                    self._model,
                    completed.returncode,
                    attempt,
                )
                if attempt == 1 and _rate_limited(completed):
                    time.sleep(RATE_LIMIT_BACKOFF_SECONDS)
                    continue
                raise

        # Unreachable: the loop either returns or raises on its second pass. Present so the
        # function has one exit type rather than an implicit `None`.
        raise DraftingError(None, "cli")  # pragma: no cover


def _payload(completed: subprocess.CompletedProcess[str]) -> Any:
    """Pull the single JSON object out of one CLI print-mode reply.

    Prefers ``structured_output`` (already parsed) and falls back to ``json.loads(result)``.
    Every failure here is reported as the same fixed detail, ``"cli"`` — never a rendering of
    ``stdout``, ``stderr``, or anything inside the envelope: that is the one place an export's
    rules text, or the model's restatement of it, lives in this process.
    """
    if completed.returncode != 0:
        raise DraftingError(completed.returncode, "cli")

    try:
        envelope = json.loads(completed.stdout)
    except ValueError as exc:
        raise DraftingError(None, "cli") from exc
    if not isinstance(envelope, dict):
        raise DraftingError(None, "cli")
    if envelope.get("is_error"):
        raise DraftingError(completed.returncode, "cli")

    payload = envelope.get("structured_output")
    if payload is None:
        result = envelope.get("result")
        if not isinstance(result, str):
            raise DraftingError(None, "cli")
        try:
            payload = json.loads(result)
        except ValueError as exc:
            raise DraftingError(None, "cli") from exc
    return payload


def _rate_limited(completed: subprocess.CompletedProcess[str]) -> bool:
    """Whether this failure looks like "come back later" rather than a fact about the request.

    Checked in ``stderr`` and, if the envelope parses, its ``result`` string — lower-cased,
    looking for ``rate`` or ``limit``. Never raises and never logs what it found: the values it
    inspects are the same reply body the rest of this module keeps out of every diagnostic.
    """
    haystack = completed.stderr or ""
    try:
        envelope = json.loads(completed.stdout)
    except (ValueError, TypeError):
        envelope = None
    if isinstance(envelope, dict):
        result = envelope.get("result")
        if isinstance(result, str):
            haystack = f"{haystack} {result}"
    haystack = haystack.lower()
    return "rate" in haystack or "limit" in haystack
