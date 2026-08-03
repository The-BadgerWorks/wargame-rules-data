# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented curator notification (task
# T107): delivery to the secret-store webhook destination with the change summary attached,
# never echoing the secret itself (FR-052, FR-055, Principle 7).
"""Curator notification: a raised candidate, a detection failure, or a staleness alarm.

**The webhook URL is never logged, printed, or included in an exception message.** Only whether
a notification was attempted and its outcome are observable — the same discipline
``pipeline.config`` applies to every sensitive value (Principle 7). ``.github/workflows/
detect.yml`` additionally captures this module's own output and greps it for the configured
secret as a second, independent check that the discipline held (task T107).

An unconfigured webhook is not an error: notifications are optional (``WGC_NOTIFY_WEBHOOK_URL``
defaults to empty), and a curator running locally against fixtures should never see a delivery
failure for a destination nobody configured.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from typing import Final

import httpx

from pipeline.config import PipelineConfig, load_config

LOGGER: Final = logging.getLogger("pipeline.notify")

DEFAULT_TIMEOUT_SECONDS: Final = 10.0


class NotifyError(RuntimeError):
    """A configured webhook rejected the notification or could not be reached.

    The message never carries the webhook URL — only what kind of failure it was.
    """


def send_notification(
    config: PipelineConfig,
    *,
    title: str,
    message: str,
    client: httpx.Client | None = None,
) -> bool:
    """Send one notification, or skip silently when no webhook is configured.

    Returns:
        ``True`` if a notification was sent, ``False`` if skipped because
        ``WGC_NOTIFY_WEBHOOK_URL`` is unset.

    Raises:
        NotifyError: the webhook was configured but delivery failed.
    """
    if not config.notify_webhook_url:
        LOGGER.info("notify: no webhook configured; skipping %r", title)
        return False

    owns_client = client is None
    active = client if client is not None else httpx.Client(timeout=DEFAULT_TIMEOUT_SECONDS)
    try:
        response = active.post(config.notify_webhook_url, json={"title": title, "text": message})
        response.raise_for_status()
    except httpx.HTTPError as exc:
        LOGGER.warning("notify: delivery failed (%s)", type(exc).__name__)
        raise NotifyError(f"notification delivery failed: {type(exc).__name__}") from exc
    finally:
        if owns_client:
            active.close()

    LOGGER.info("notify: sent %r", title)
    return True


def main(argv: Sequence[str] | None = None) -> int:
    """The workflow-facing entry point: ``python -m pipeline.observability.notify``.

    Not one of the eight contract commands (``contracts/pipeline-run-interface.md`` §1) —
    notification is workflow plumbing, not an operator-facing pipeline stage — so it is invoked
    directly rather than through ``rules-pipeline``.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    parser = argparse.ArgumentParser(prog="python -m pipeline.observability.notify")
    parser.add_argument("--title", required=True)
    parser.add_argument("--message", required=True)
    args = parser.parse_args(argv)

    config = load_config()
    try:
        sent = send_notification(config, title=args.title, message=args.message)
    except NotifyError as exc:
        print(f"notify: {exc}", file=sys.stderr)
        return 1

    print("notify: sent" if sent else "notify: skipped (no webhook configured)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
