"""The DM's model behind an OpenAI-style gateway (OmniRoute, OpenRouter, ...), for models that are not Claude.

dm/model.py sends one Anthropic-style request and expects the reply as an Anthropic-style dict. For a model name with a
slash in it (`ali/qwen3.7-plus`, `zai/glm-5.3`: the gateway's own names) model.send comes here instead: the request
becomes a chat-completions request, and the reply is turned back, so nothing above model.send changes and the save
keeps its conversation as Anthropic messages.

    DM_GATEWAY_URL     the gateway's /v1 address (default http://localhost:20128/v1, OmniRoute's)
    DM_GATEWAY_KEY     the gateway's API key (sent as a Bearer token)
    DM_GATEWAY_PARAMS  optional JSON merged into each request body, for a provider's own switches
    DM_GATEWAY_CHECK_PARAMS  the same, merged on top for the continuity checker's requests only
                       (for example {"reasoning_effort": "medium"}); none are sent by default

Left out on the way: `thinking`, `output_config` and `cache_control` (Anthropic's own), and the model's thinking blocks in
the conversation. Whether a provider caches the start of the conversation is up to the provider; the reply's usage says
(cache_read_input_tokens is filled from prompt_tokens_details.cached_tokens).

    py -3.12 -m dm.gateway <model> [<model> ...]    one small tool-call check per model (3 calls each)
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

from dm import model

URL = "http://localhost:20128/v1"
RETRY = (429, 500, 502, 503, 504, 529)  # as the Anthropic library retries, twice
STOPS = {"stop": "end_turn", "tool_calls": "tool_use", "length": "max_tokens"}


def _text(content: Any) -> str:
    """The words of a message's content or a tool result's content (a string, or a list of blocks)."""
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content or [] if b.get("type") == "text")


def to_chat(request: dict[str, Any]) -> dict[str, Any]:
    """An Anthropic-style request as a chat-completions body."""
    msgs: list[dict[str, Any]] = []
    if request.get("system"):
        msgs.append({"role": "system", "content": _text(request["system"])})
    for m in request["messages"]:
        content = m["content"]
        if m["role"] == "assistant":
            blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content
            calls = [{"id": b["id"], "type": "function",
                      "function": {"name": b["name"], "arguments": json.dumps(b["input"])}}
                     for b in blocks if b["type"] == "tool_use"]
            out: dict[str, Any] = {"role": "assistant", "content": _text([b for b in blocks if b["type"] == "text"])}
            if os.environ.get("DM_GATEWAY_PASS_REASONING") and (why := "".join(
                    b.get("thinking", "") for b in blocks if b["type"] == "thinking")):
                out["reasoning_content"] = why  # DeepSeek: with tools, its thinking must go back in every later request
            if calls:
                out["tool_calls"] = calls
            msgs.append(out)  # thinking blocks are dropped (they belong to the model that wrote them), unless DM_GATEWAY_PASS_REASONING is set
            continue
        if isinstance(content, str):
            msgs.append({"role": "user", "content": content})
            continue
        for b in content:  # tool results answer the assistant's calls and come first, then what the player said
            if b["type"] == "tool_result":
                msgs.append({"role": "tool", "tool_call_id": b["tool_use_id"], "content": _text(b["content"])})
        words = [b for b in content if b["type"] == "text"]
        if words:
            msgs.append({"role": "user", "content": _text(words)})
    body: dict[str, Any] = {"model": request["model"], "messages": msgs, "max_tokens": request["max_tokens"]}
    if request.get("tools"):
        body["tools"] = [{"type": "function", "function": {"name": t["name"], "description": t.get("description", ""),
                                                           "parameters": t["input_schema"]}} for t in request["tools"]]
    if schema := ((request.get("output_config") or {}).get("format") or {}).get("schema"):
        # a reply in a set shape (the checker's): JSON mode, and the shape told in words, as not every model takes a schema
        body["response_format"] = {"type": "json_object"}
        note = "Reply with only a JSON object that matches this JSON schema, nothing else:\n" + json.dumps(schema)
        if msgs and msgs[0]["role"] == "system":
            msgs[0] = {"role": "system", "content": msgs[0]["content"] + "\n\n" + note}
        else:
            msgs.insert(0, {"role": "system", "content": note})
    if extra := os.environ.get("DM_GATEWAY_PARAMS"):
        body |= json.loads(extra)
    if schema and (extra := os.environ.get("DM_GATEWAY_CHECK_PARAMS")):
        body |= json.loads(extra)  # the checker's own settings (e.g. how long to think), on top of the DM's
    return body


def from_chat(reply: dict[str, Any]) -> dict[str, Any]:
    """A chat-completions reply as an Anthropic-style one. Raises model.Failed when it can't be read."""
    try:
        choice = reply["choices"][0]
        message = choice["message"]
    except (KeyError, IndexError, TypeError) as e:
        raise model.Failed(f"the gateway's reply has no message: {str(reply)[:300]}") from e
    content: list[dict[str, Any]] = []
    if os.environ.get("DM_GATEWAY_PASS_REASONING") and (message.get("reasoning_content") or "").strip():
        content.append({"type": "thinking", "thinking": message["reasoning_content"], "signature": ""})
    if (message.get("content") or "").strip():
        content.append({"type": "text", "text": message["content"]})
    for c in message.get("tool_calls") or []:
        try:
            args = json.loads(c["function"]["arguments"] or "{}")
            if not isinstance(args, dict):
                raise ValueError("not an object")
        except (ValueError, KeyError) as e:
            raise model.Failed(f"the model's arguments for a tool call aren't JSON: {str(c)[:300]}") from e
        content.append({"type": "tool_use", "id": c["id"], "name": c["function"]["name"], "input": args})
    use = reply.get("usage") or {}
    cached = (use.get("prompt_tokens_details") or {}).get("cached_tokens") or 0
    finish = choice.get("finish_reason")
    return {"id": reply.get("id", ""), "type": "message", "role": "assistant", "model": reply.get("model", ""),
            "content": content, "stop_reason": "tool_use" if any(b["type"] == "tool_use" for b in content)
            else STOPS.get(finish, finish), "stop_sequence": None,
            "usage": {"input_tokens": max((use.get("prompt_tokens") or 0) - cached, 0),
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": cached,
                      "output_tokens": use.get("completion_tokens") or 0}}


def assemble(text: str) -> dict[str, Any]:
    """A streamed answer (server-sent events of chat-completions chunks) as the one reply a plain call would give.
    The model's thinking (`reasoning_content`) is kept in the message for from_chat to use or drop; the text, the tool calls and the usage are put together."""
    reply: dict[str, Any] = {"id": "", "model": "", "usage": None}
    content, reasoning, calls, finish = "", "", {}, None
    for line in text.splitlines():
        if not line.startswith("data:") or line[5:].strip() in ("", "[DONE]"):
            continue
        try:
            chunk = json.loads(line[5:])
        except ValueError:
            continue
        if "error" in chunk and not chunk.get("choices"):
            raise model.Failed(str(chunk["error"])[:300])
        reply["id"], reply["model"] = chunk.get("id") or reply["id"], chunk.get("model") or reply["model"]
        reply["usage"] = chunk.get("usage") or reply["usage"]
        for ch in chunk.get("choices") or []:
            delta = ch.get("delta") or {}
            content += delta.get("content") or ""
            reasoning += delta.get("reasoning_content") or ""
            for c in delta.get("tool_calls") or []:
                t = calls.setdefault(c.get("index", 0), {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                t["id"] = c.get("id") or t["id"]
                t["function"]["name"] += (c.get("function") or {}).get("name") or ""
                t["function"]["arguments"] += (c.get("function") or {}).get("arguments") or ""
            finish = ch.get("finish_reason") or finish
    message: dict[str, Any] = {"role": "assistant", "content": content}
    if reasoning:
        message["reasoning_content"] = reasoning
    if calls:
        message["tool_calls"] = [calls[i] for i in sorted(calls)]
    reply["choices"] = [{"index": 0, "message": message, "finish_reason": finish}]
    return reply


def _post(body: dict[str, Any]) -> tuple[int, str]:
    """One HTTP call: (status, text). Status 0 when there was no answer at all."""
    req = urllib.request.Request(
        os.environ.get("DM_GATEWAY_URL", URL).rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + os.environ.get("DM_GATEWAY_KEY", "")})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, f"couldn't reach the gateway ({e})"


async def send(request: dict[str, Any]) -> dict[str, Any]:
    """model.send for a gateway model: the Anthropic-style request, and the reply as an Anthropic-style dict."""
    body = to_chat(request) | {"stream": True, "stream_options": {"include_usage": True}}
    # streamed: a model that thinks for a while before it writes (Qwen) keeps the gateway's no-answer timeout from firing
    for attempt in range(3):
        status, text = await asyncio.to_thread(_post, body)
        if status == 200:
            try:
                return from_chat(assemble(text) if text.lstrip().startswith(("data:", ":")) else json.loads(text))
            except ValueError as e:
                raise model.Failed(f"the gateway's reply isn't JSON: {text[:300]}") from e
        if status not in (0, *RETRY) or attempt == 2:
            try:
                why = json.loads(text)["error"]["message"]
            except (ValueError, KeyError, TypeError):
                why = text[:300]
            raise model.Failed(f"{status}: {why}" if status else why)
        await asyncio.sleep(2 * 2 ** attempt)
    raise AssertionError


# ---- the small check: `py -3.12 -m dm.gateway <model> ...` ----------------------------------------------------------

_ROLL = {"name": "roll", "description": "Roll dice for the player. Always use this to roll; never invent a result.",
         "input_schema": {"type": "object", "properties": {"dice": {"type": "string", "description": "like 1d20+5"},
                                                           "reason": {"type": "string"}},
                          "required": ["dice", "reason"]}}
# long enough (a few thousand tokens) for a provider that caches the start of a conversation to do so
_SYSTEM = "You are the Dungeon Master of a fantasy game. Use the roll tool for every roll.\n\n" + "\n".join(
    f"Lore note {i}: the village of Hollowmere keeps its {['bells', 'granary', 'ledgers', 'wells'][i % 4]} "
    f"under the care of warden {['Ansa', 'Brom', 'Cael', 'Dessa', 'Edric'][i % 5]}, who answers to no one." for i in range(160))


async def check(name: str) -> None:
    ask = {"model": name, "max_tokens": 2000, "system": _SYSTEM, "tools": [_ROLL], "messages": [
        {"role": "user", "content": "[The player]\nI try to force the cellar door open. Roll it, then describe the result."}]}
    first = await send(ask)
    print(f"\n== {name}\ncall 1: stop={first['stop_reason']}  usage={first['usage']}")
    uses = [b for b in first["content"] if b["type"] == "tool_use"]
    print("  tool calls:", [(b["name"], b["input"]) for b in uses] or "NONE")
    if not uses:
        print("  text:", _text(first["content"])[:200])
        return
    ask["messages"] += [{"role": "assistant", "content": first["content"]},
                        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": u["id"],
                                                      "content": [{"type": "text", "text": "dice 1d20+5 = 14 + 5 = 19"}]}
                                                     for u in uses]}]
    second = await send(ask)
    print(f"call 2: stop={second['stop_reason']}  usage={second['usage']}")
    print("  text:", _text(second["content"])[:300].replace("\n", " "))
    third = await send(ask)  # the same request again: a provider that caches shows cache_read_input_tokens here
    print(f"call 3 (same as 2): usage={third['usage']}")


async def check_checker(name: str) -> None:
    """One call of the game's continuity checker on this model, with a plain clash planted: is the answer JSON the
    checker can read (`py -3 -m dm.gateway --checker <model>`)?"""
    from dm import check
    check.CHECK_MODEL = name
    state = ("NOTEBOOK (the DM's notes, as they were before the new reply)\nWarden Ansa keeps the granary key. The granary holds "
             "40 sacks of barley.\n\nEARLIER PLAY (the last 5 turns, word for word)\nDM: The warden shows you the granary: "
             "forty sacks of barley stand in rows.\n\nNEW REPLY\nYou count the sacks again and find only twelve in the "
             "granary, as the warden said.")
    answer = await check.ask_model("api", check.SYSTEM, state)
    print(f"\n== {name} (checker)\nanswer: {json.dumps(answer)[:600]}\nkept: {check.kept(answer, state)}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--checker"]:
        for n in sys.argv[2:] or ["ali/qwen3.7-plus"]:
            try:
                asyncio.run(check_checker(n))
            except (model.Failed, ValueError, StopIteration) as e:
                print(f"\n== {n} (checker)\nFAILED: {type(e).__name__}: {e}")
        sys.exit()
    for n in sys.argv[1:] or ["ali/qwen3.7-plus", "zai/glm-5.3"]:
        try:
            asyncio.run(check(n))
        except model.Failed as e:
            print(f"\n== {n}\nFAILED: {e}")
