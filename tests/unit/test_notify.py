# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote tests for curator notification (task
# T107): an unconfigured webhook is skipped rather than treated as an error, a configured one is
# posted to, a delivery failure raises NotifyError, and the webhook URL never appears in the
# exception text (Principle 7).
"""Curator notification: optional by default, and its secret never leaks into a diagnostic."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from pipeline.config import load_config
from pipeline.observability.notify import NotifyError, send_notification

pytestmark = pytest.mark.httpx_mock(assert_all_responses_were_requested=False)

WEBHOOK = "https://hooks.example/secret-path-abc123"


def test_an_unconfigured_webhook_is_skipped_not_an_error() -> None:
    config = load_config(env={})
    assert send_notification(config, title="t", message="m") is False


def test_a_configured_webhook_is_posted_to(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(url=WEBHOOK, method="POST")
    config = load_config(env={"WGC_NOTIFY_WEBHOOK_URL": WEBHOOK})

    assert send_notification(config, title="Points release detected", message="details") is True

    request = httpx_mock.get_requests()[-1]
    assert request.url == WEBHOOK


def test_a_delivery_failure_raises_notify_error_without_naming_the_webhook(
    httpx_mock: HTTPXMock,
) -> None:
    httpx_mock.add_response(url=WEBHOOK, status_code=500)
    config = load_config(env={"WGC_NOTIFY_WEBHOOK_URL": WEBHOOK})

    with pytest.raises(NotifyError) as raised:
        send_notification(config, title="t", message="m")

    assert WEBHOOK not in str(raised.value)
    assert "secret-path" not in str(raised.value)
