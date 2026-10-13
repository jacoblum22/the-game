"""The DM's model: the Anthropic API, called directly. Everything that depends on the model provider is in this file.

The conversation is a plain list of API messages that the game keeps in its save, so nothing lives anywhere else.
The key comes from the ANTHROPIC_API_KEY environment variable.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import anthropic

MAX_ROUNDS = 40  # model calls per reply, as the Agent SDK's max_turns was
MAX_TOKENS = 16000  # one reply's output, thinking included; more needs streaming


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


def tool(name: str, description: str, input_schema: dict[str, Any]) -> Callable[..., Tool]:
    """Our tool decorator, in the shape the Agent SDK's had: the handler takes the input and returns
    {"content": [{"type": "text", "text": ...}]}, with "is_error": True when the tool refused."""
    return lambda fn: Tool(name, description, input_schema, fn)


_client: anthropic.AsyncAnthropic | None = None


def client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic()  # reads ANTHROPIC_API_KEY
    return _client


def _error(text: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "is_error": True}


def add_user(messages: list[dict[str, Any]], content: list[dict[str, Any]]) -> None:
    """A user turn. After a failed call the conversation can already end with one (the player's line, or tool
    results): the new content joins it, so the roles keep alternating."""
    if messages and messages[-1]["role"] == "user":
        last = messages[-1]
        if isinstance(last["content"], str):
            last["content"] = [{"type": "text", "text": last["content"]}]
        last["content"] += content
    else:
        messages.append({"role": "user", "content": content})


async def respond(model: str, system: str, tools: list[Tool], messages: list[dict[str, Any]], text: str,
                  on_text: Callable[[str], None], on_change: Callable[[], None] = lambda: None) -> str | None:
    """Send `text` as the next user turn and run the DM until it finishes its reply: each tool it asks for runs, and
    its result goes back. `messages` grows in place; `on_text` gets each piece of the DM's text and `on_change`
    is called whenever `messages` has grown (to save). Returns None, or why the call failed."""
    add_user(messages, [{"type": "text", "text": text}])
    by_name = {t.name: t for t in tools}
    specs = [{"name": t.name, "description": t.description, "input_schema": t.input_schema} for t in tools]
    for _ in range(MAX_ROUNDS):
        try:
            reply = await client().messages.create(
                model=model, max_tokens=MAX_TOKENS, system=system, tools=specs, messages=messages,
                thinking={"type": "adaptive", "display": "omitted"}, output_config={"effort": "medium"},
                cache_control={"type": "ephemeral", "ttl": "1h"})  # players think for minutes between turns
        except anthropic.APIError as e:
            return str(e)
        content = [b.model_dump(exclude_none=True) for b in reply.content]
        messages.append({"role": "assistant", "content": content})
        on_change()
        for b in reply.content:
            if b.type == "text" and b.text.strip():
                on_text(b.text.strip())
        uses = [b for b in reply.content if b.type == "tool_use"]
        if reply.stop_reason != "tool_use" or not uses:
            return None if reply.stop_reason in ("end_turn", "stop_sequence") else f"the reply stopped: {reply.stop_reason}"
        results = []
        for b in uses:
            t = by_name.get(b.name)
            try:
                res = await t.handler(dict(b.input)) if t else _error(f"no tool called {b.name}")
            except Exception as e:  # noqa: BLE001 - a bug in a tool: the DM hears of it, and the game goes on
                res = _error(f"the tool failed: {type(e).__name__}: {e}")
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": res["content"],
                            **({"is_error": True} if res.get("is_error") else {})})
        add_user(messages, results)
        on_change()
    return f"the reply took more than {MAX_ROUNDS} model calls"
