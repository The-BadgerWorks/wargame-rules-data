# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R7 task 1: the house style for the
# drafting and reviewing passes of the Owner's amended standing rule 3. These are OUR
# instructions, authored here; no publisher wording appears in this file, and the rules it lays
# down are the ones that keep publisher wording out of what comes back.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R7 task 2 fix round 1: `draft_user` takes
# an optional `hint` and appends the reviewing pass's reason code as one instruction line, so the
# standing instructions stay byte-identical between a first attempt and a redraft.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 R7c task 1: the batch review prompt and
# the three JSON schemas the CLI transport's `--json-schema` flag needs. The batch prompt numbers
# each item so a reply's order is unambiguous without inventing a second identifier scheme.
"""The two system prompts, and the two user messages that carry one entry's text.

Standing rule 3 (amended 2026-09-14) permits a summary to be machine-drafted from the export's
rules text and reviewed by a second model pass before the Owner approves it. The line that
never moves is lore: a summary describes what a mechanic *does*, and carries no flavour, no
world text and no publisher name. Where restating a mechanic would change its meaning, the
rules text for that mechanic may be used as written — the drafting pass says so explicitly by
setting ``used_verbatim``, so the reviewer and the Owner can see which entries took that route.

Both prompts ask for JSON and nothing else, because the client validates the reply with
``pydantic`` and refuses anything that is not the declared shape rather than salvaging it.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Final, Literal

# The 600-character target and the four reason codes are stated to the model below and enforced
# by the `Literal` types in `client.py`. They are deliberately not also constants here: a second
# spelling of a closed set is a second place for it to drift.

DRAFT_SYSTEM: Final = """\
You restate a single tabletop wargame rule as a short mechanical summary.

Rules for the summary:
- Describe only what the mechanic does in game terms: conditions, timing, targets, and the
  numeric effect. Nothing else.
- Write in the present tense, in plain declarative sentences.
- Keep it to 600 characters or fewer.
- Carry no lore, no setting or world detail, no unit background, no quoted flavour text, and no
  publisher or product name. If the supplied text mixes flavour with mechanics, keep only the
  mechanics.
- Do not invent, generalise, round, or "tidy up" a value, a range, a keyword, or a condition.
- If the mechanic cannot be restated without changing its meaning, return the supplied rules
  text as written and set "used_verbatim" to true. Otherwise set it to false.

Reply with a single JSON object and no other text:
{"summary": "<the summary>", "used_verbatim": <true|false>}
"""

REVIEW_SYSTEM: Final = """\
You review one mechanical summary against the rules text it was drafted from, as a second pass
before a human approves it.

Decide one of:
- "keep"    - the summary is faithful, mechanical, and within 600 characters.
- "redraft" - the summary changes, drops, or adds meaning, or it exceeds 600 characters.
- "lore"    - the summary carries lore, setting or world detail, unit background, quoted
              flavour, or a publisher or product name.

Then give exactly one reason code:
- "meaning-changed" - a condition, value, timing, target, or keyword differs from the text.
- "too-long"        - the summary exceeds 600 characters.
- "lore-present"    - the summary carries non-mechanical content.
- "ok"              - nothing is wrong with it.

Use "ok" only with "keep", and never invent a code outside those four.

Reply with a single JSON object and no other text:
{"decision": "<keep|redraft|lore>", "reason_code": "<one of the four codes>"}
"""

#: How each class is named to the model. The label is ours, not the export's.
_CLASS_LABEL: Final[dict[str, str]] = {
    "ability": "datasheet ability",
    "detachment_rule": "detachment rule",
}


#: How a redraft hint is named to the model. One line, appended after the entry, because the
#: reviewing pass's reason code is a closed set of OUR own codes: it says why the previous
#: attempt was sent back, and nothing about it is publisher material.
_HINT_LABEL: Final[dict[str, str]] = {
    "meaning-changed": "changed, dropped or added meaning",
    "too-long": "exceeded the character limit",
    "lore-present": "carried lore, flavour or world text",
    "ok": "was sent back without a stated reason",
}


def draft_user(
    name: str,
    mechanic_text: str,
    ability_class: Literal["ability", "detachment_rule"],
    *,
    hint: str | None = None,
) -> str:
    """The user message for the drafting pass.

    ``hint`` is the reviewing pass's reason code from a previous attempt at this same entry
    (010 R7 task 2 fix round 1). It is appended as **one instruction line** rather than folded
    into the system prompt, so the standing instructions are byte-identical on a first attempt
    and on a redraft, and the only difference is the stated reason the first was rejected. An
    unrecognised code is passed through as itself rather than dropped: a code outside the
    closed set is a surprise worth seeing in the request, not worth silently discarding.
    """
    message = (
        f"Entry class: {_CLASS_LABEL[ability_class]}\nName: {name}\nRules text:\n{mechanic_text}"
    )
    if hint:
        described = _HINT_LABEL.get(hint, hint)
        message += (
            f"\n\nA previous attempt at this entry was rejected on review: it {described}. "
            f"(reason code: {hint}) Draft it again and avoid that."
        )
    return message


def review_user(name: str, mechanic_text: str, summary: str) -> str:
    """The user message for the reviewing pass."""
    return f"Name: {name}\nRules text:\n{mechanic_text}\n\nProposed summary:\n{summary}"


REVIEW_BATCH_SYSTEM: Final = """\
You review several mechanical summaries in one pass, each against the rules text it was
drafted from, before a human approves them. The items are numbered.

For each item, independently decide one of:
- "keep"    - the summary is faithful, mechanical, and within 600 characters.
- "redraft" - the summary changes, drops, or adds meaning, or it exceeds 600 characters.
- "lore"    - the summary carries lore, setting or world detail, unit background, quoted
              flavour, or a publisher or product name.

Then give exactly one reason code per item:
- "meaning-changed" - a condition, value, timing, target, or keyword differs from the text.
- "too-long"        - the summary exceeds 600 characters.
- "lore-present"    - the summary carries non-mechanical content.
- "ok"              - nothing is wrong with it.

Use "ok" only with "keep", and never invent a code outside those four.

Reply with one verdict per item, in the same order the items were given, one object per item,
never fewer, and no other text:
{"verdicts": [{"decision": "<keep|redraft|lore>", "reason_code": "<one of the four codes>"}, ...]}
"""


def review_batch_user(items: Sequence[tuple[str, str, str]]) -> str:
    """The user message for a batched reviewing pass: one numbered block per ``(name, text,
    summary)`` triple, so the reply's order is unambiguous."""
    blocks = [
        f"Item {index}\nName: {name}\nRules text:\n{mechanic_text}\n\nProposed summary:\n{summary}"
        for index, (name, mechanic_text, summary) in enumerate(items, start=1)
    ]
    return "\n\n".join(blocks)


#: The three JSON schemas the CLI transport's `--json-schema` flag validates a reply against.
#: Shaped to match `_DraftReply` / `_ReviewReply` / the batch reply model in `cli_client.py` —
#: `additionalProperties: false` and every field required, so a malformed reply is refused by the
#: CLI itself rather than only by our own `pydantic` pass.
DRAFT_SCHEMA: Final[dict[str, Any]] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "used_verbatim": {"type": "boolean"},
    },
    "required": ["summary", "used_verbatim"],
    "additionalProperties": False,
}

REVIEW_SCHEMA: Final[dict[str, Any]] = {
    "type": "object",
    "properties": {
        "decision": {"type": "string", "enum": ["keep", "redraft", "lore"]},
        "reason_code": {
            "type": "string",
            "enum": ["meaning-changed", "too-long", "lore-present", "ok"],
        },
    },
    "required": ["decision", "reason_code"],
    "additionalProperties": False,
}

REVIEW_BATCH_SCHEMA: Final[dict[str, Any]] = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "decision": {"type": "string", "enum": ["keep", "redraft", "lore"]},
                    "reason_code": {
                        "type": "string",
                        "enum": ["meaning-changed", "too-long", "lore-present", "ok"],
                    },
                },
                "required": ["decision", "reason_code"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["verdicts"],
    "additionalProperties": False,
}
