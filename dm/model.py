"""The DM's model: the Anthropic API, called directly. Everything that depends on the model provider is in this file.

The conversation is a plain list of API messages that the game keeps in its save, so nothing lives anywhere else.
In the terminal the call goes through Anthropic's Python library, with the key from the ANTHROPIC_API_KEY
environment variable; the browser page has no such library and puts its own call in `send` (dm/browser.py).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

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


class Failed(Exception):
    """The model call failed (after the retries): why, for the player."""


_client: Any = None


def client() -> Any:
    global _client
    if _client is None:
        import anthropic  # here, not at the top: the browser has no such library
        _client = anthropic.AsyncAnthropic()  # reads ANTHROPIC_API_KEY
    return _client


async def _send(request: dict[str, Any]) -> dict[str, Any]:
    import anthropic
    try:
        reply = await client().messages.create(**request)
    except anthropic.APIError as e:
        raise Failed(str(e)) from e
    return reply.model_dump(exclude_none=True)


send: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]] = _send  # one API call: the request, and the reply as JSON


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
            reply = await send({
                "model": model, "max_tokens": MAX_TOKENS, "system": system, "tools": specs, "messages": messages,
                "thinking": {"type": "adaptive", "display": "omitted"}, "output_config": {"effort": "medium"},
                "cache_control": {"type": "ephemeral", "ttl": "1h"}})  # players think for minutes between turns
        except Failed as e:
            return str(e)
        content = reply["content"]
        messages.append({"role": "assistant", "content": content})
        on_change()
        for b in content:
            if b["type"] == "text" and b["text"].strip():
                on_text(b["text"].strip())
        uses = [b for b in content if b["type"] == "tool_use"]
        stop = reply.get("stop_reason")
        if stop != "tool_use" or not uses:
            return None if stop in ("end_turn", "stop_sequence") else f"the reply stopped: {stop}"
        results = []
        for b in uses:
            t = by_name.get(b["name"])
            try:
                res = await t.handler(dict(b["input"])) if t else _error(f"no tool called {b['name']}")
            except Exception as e:  # noqa: BLE001 - a bug in a tool: the DM hears of it, and the game goes on
                res = _error(f"the tool failed: {type(e).__name__}: {e}")
            results.append({"type": "tool_result", "tool_use_id": b["id"], "content": res["content"],
                            **({"is_error": True} if res.get("is_error") else {})})
        add_user(messages, results)
        on_change()
    return f"the reply took more than {MAX_ROUNDS} model calls"
