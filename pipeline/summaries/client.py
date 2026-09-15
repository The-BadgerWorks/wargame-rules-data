# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R7 task 1: the pipeline-owned API client
# that drafts a mechanical summary from an export entry's rules text and reviews it with a second
# model pass, so the Owner's amended standing rule 3 is executed by code in this repository
# rather than by hand in an interactive session. It posts with `httpx` directly rather than
# through `PoliteClient`, which refuses any host outside the declared source set by design, and
# it never logs the request body: the body is the one place an export's rules text exists in
# this process, and standing rule 2 keeps it out of logs, reports and history.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R7 task 2 fix round 1: `draft` takes an
# additive keyword-only `hint`, the reviewing pass's reason code from a previous attempt, so a
# redraft says why the first was sent back instead of being an undirected second sample.
"""The drafting client.

Two calls, one transport. :meth:`SummaryClient.draft` asks a model to restate one mechanic;
:meth:`SummaryClient.review` asks a second model whether that restatement still means the same
thing. Both go to the messages API, both ask for JSON, and both validate the reply with
``pydantic`` before anything downstream sees it.

Three properties are deliberate and load-bearing:

* **Nothing about the body is logged.** Not the name, not the rules text, not the summary, not
  the key. Diagnostics name the purpose, the model and the HTTP status, and stop there.
* **A malformed reply is refused, never salvaged.** ``pydantic``'s own error text quotes the
  input it rejected, so it is never carried into :class:`DraftingError` — the error says what
  shape was expected and says nothing about what arrived.
* **One retry, not a loop.** 429 and 529 are the two statuses the messages API uses for "later";
  everything else is a fact about the request and is reported immediately.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Final, Literal

import httpx
from pydantic import BaseModel, ValidationError

from pipeline.summaries import prompts

LOGGER: Final = logging.getLogger("pipeline.summaries.client")

#: The messages endpoint. A module constant so a test can match on it without repeating it.
MESSAGES_URL: Final = "https://api.anthropic.com/v1/messages"

ANTHROPIC_VERSION: Final = "2023-06-01"

#: Generous for a 600-character summary, and small enough that a runaway reply is cut off
#: rather than billed for.
MAX_TOKENS: Final = 800

#: "Come back later", and the only two statuses worth a second attempt.
RETRY_STATUSES: Final = frozenset({429, 529})

RETRY_BACKOFF_SECONDS: Final = 2.0

REQUEST_TIMEOUT_SECONDS: Final = 120.0


class DraftingError(RuntimeError):
    """A drafting or reviewing call that did not produce a usable reply.

    ``status_code`` carries the HTTP status when the endpoint refused the request, and is
    ``None`` when the request itself succeeded but the reply was not the declared JSON shape —
    the two failure modes a caller actually distinguishes (retry the run vs. re-prompt the
    entry). The message never quotes the reply: a malformed reply may still carry the model's
    restatement of the rules text.
    """

    def __init__(self, status_code: int | None, detail: str | None = None) -> None:
        if detail is None:
            detail = (
                f"the summaries endpoint returned HTTP {status_code}"
                if status_code is not None
                else "the reply was not the expected JSON shape"
            )
        super().__init__(detail)
        self.status_code = status_code


class _TextBlock(BaseModel):
    type: str
    text: str


class _Envelope(BaseModel):
    content: list[_TextBlock]


class _DraftReply(BaseModel):
    summary: str
    used_verbatim: bool


class _ReviewReply(BaseModel):
    decision: Literal["keep", "redraft", "lore"]
    reason_code: Literal["meaning-changed", "too-long", "lore-present", "ok"]


@dataclass(frozen=True, slots=True)
class Draft:
    """One drafted summary, and whether the rules text was used as written."""

    summary: str
    used_verbatim: bool


@dataclass(frozen=True, slots=True)
class Verdict:
    """The reviewing pass's answer. ``reason_code`` is a closed set, never free text."""

    decision: Literal["keep", "redraft", "lore"]
    reason_code: Literal["meaning-changed", "too-long", "lore-present", "ok"]


class SummaryClient:
    """Drafts and reviews mechanical summaries through the messages API.

    Args:
        api_key: the credential. Held only to build a request header; never logged, never
            rendered, never carried into an exception message.
        model: the model id this instance talks to. The drafting and reviewing passes use
            different models (``WGC_DRAFT_MODEL``, ``WGC_REVIEW_MODEL``), so a caller building
            both constructs two clients rather than passing a model per call.
        http: an ``httpx.Client`` to use instead of one of our own — the injection point for a
            caller that needs its own transport. ``PoliteClient`` is deliberately not used
            here: it honours ``robots.txt`` and refuses hosts outside the declared source set,
            which is correct for acquisition and wrong for an API we hold a key to.
    """

    def __init__(self, api_key: str, *, model: str, http: httpx.Client | None = None) -> None:
        self._api_key = api_key
        self._model = model
        self._http = http
        self._owns_http = http is None

    # -- lifecycle ---------------------------------------------------------------------

    def __enter__(self) -> SummaryClient:
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
        if self._owns_http and self._http is not None:
            self._http.close()
            self._http = None

    # -- the two passes ----------------------------------------------------------------

    def draft(
        self,
        name: str,
        mechanic_text: str,
        *,
        ability_class: Literal["ability", "detachment_rule"],
        hint: str | None = None,
    ) -> Draft:
        """Restate one mechanic as a summary, or return it verbatim if restating would change it.

        ``hint`` (010 R7 task 2 fix round 1) is the reviewing pass's reason code from a previous
        attempt at this same entry. Additive and keyword-only: every existing caller is
        unaffected, and omitting it produces byte-identical request content to before. It is one
        of our own four closed reason codes, never publisher material, so appending it to the
        user message carries nothing out of the workspace that was not already going in.
        """
        payload = self._exchange(
            prompts.DRAFT_SYSTEM,
            prompts.draft_user(name, mechanic_text, ability_class, hint=hint),
            purpose="draft",
        )
        reply = _validate(_DraftReply, payload)
        return Draft(summary=reply.summary, used_verbatim=reply.used_verbatim)

    def review(self, name: str, mechanic_text: str, summary: str) -> Verdict:
        """Ask a second model whether ``summary`` still means what the rules text means."""
        payload = self._exchange(
            prompts.REVIEW_SYSTEM,
            prompts.review_user(name, mechanic_text, summary),
            purpose="review",
        )
        reply = _validate(_ReviewReply, payload)
        return Verdict(decision=reply.decision, reason_code=reply.reason_code)

    # -- transport ---------------------------------------------------------------------

    def _client(self) -> httpx.Client:
        if self._http is None:
            self._http = httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS)
        return self._http

    def _exchange(self, system: str, user: str, *, purpose: str) -> Any:
        """Post one message and return the JSON object the model's text block carries.

        The body is built here and referenced nowhere else. Every diagnostic below names the
        purpose, the model and the status — never the body, and never the key.
        """
        body = {
            "model": self._model,
            "max_tokens": MAX_TOKENS,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        }

        for attempt in (1, 2):
            response = self._client().post(MESSAGES_URL, json=body, headers=headers)
            if response.status_code == httpx.codes.OK:
                return _text_payload(response)
            LOGGER.debug(
                "summaries endpoint returned %s (purpose=%s, model=%s, attempt=%s)",
                response.status_code,
                purpose,
                self._model,
                attempt,
            )
            if attempt == 1 and response.status_code in RETRY_STATUSES:
                time.sleep(RETRY_BACKOFF_SECONDS)
                continue
            raise DraftingError(response.status_code)

        # Unreachable: the loop either returns or raises on its second pass. Present so the
        # function has one exit type rather than an implicit `None`.
        raise DraftingError(None)  # pragma: no cover


def _text_payload(response: httpx.Response) -> Any:
    """Pull the single JSON object out of the reply's first text block.

    Every failure here is the same failure to a caller — the model did not answer in the shape
    it was asked for — and none of them may quote what arrived.
    """
    try:
        envelope = _Envelope.model_validate(response.json())
    except (ValidationError, ValueError) as exc:
        raise DraftingError(None, "the reply was not a messages-API envelope") from exc

    text = next((block.text for block in envelope.content if block.type == "text"), None)
    if text is None:
        raise DraftingError(None, "the reply carried no text block")

    try:
        return json.loads(text)
    except ValueError as exc:
        raise DraftingError(None, "the reply's text block was not JSON") from exc


def _validate[ModelT: BaseModel](model: type[ModelT], payload: Any) -> ModelT:
    """Validate ``payload`` as ``model``, without letting the rejected input into the error.

    ``ValidationError``'s own text quotes the input it rejected, which here may be the model's
    restatement of the rules text. It is kept as the ``__cause__`` for a debugger and never
    rendered into the message.
    """
    try:
        return model.model_validate(payload)
    except ValidationError as exc:
        raise DraftingError(None) from exc
