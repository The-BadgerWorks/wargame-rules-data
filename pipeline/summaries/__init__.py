# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R7 task 1: the package surface for the
# summary drafting client, so a caller imports the five names it needs from one place and the
# prompts stay reachable as `summaries.prompts` for the tests that assert what was sent.
"""Machine-drafted mechanical summaries, per the Owner's amended standing rule 3.

The rules text an entry is drafted from lives inside the build workspace and inside one HTTP
request body. It never reaches a log, a report, a commit or an interactive session — only the
summary comes out.
"""

from pipeline.summaries import prompts
from pipeline.summaries.client import (
    MESSAGES_URL,
    Draft,
    DraftingError,
    SummaryClient,
    Verdict,
)

__all__ = [
    "MESSAGES_URL",
    "Draft",
    "DraftingError",
    "SummaryClient",
    "Verdict",
    "prompts",
]
