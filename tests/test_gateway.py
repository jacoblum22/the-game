"""A model behind an OpenAI-style gateway (dm/gateway.py), with a fake gateway: no network, no model calls.
The request is turned into a chat-completions body and the reply back, so the DM's loop, the save and the tools
are the ones the Claude models use."""
import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from dm import check, gateway, model, play

CHAR = Path(__file__).parent.parent / "dm" / "characters"
WHOLE = ("You climb the wall, hand over hand, and pull yourself onto the ledge. " * 5).strip()
TOOL = {"name": "roll", "description": "Roll dice.", "input_schema": {"type": "object", "properties": {"dice": {"type": "string"}}}}


def chat(content: str | None = None, calls: list[dict[str, Any]] | None = None, finish: str = "stop",
         prompt: int = 10, out: int = 5, cached: int = 0) -> dict[str, Any]:
    msg: dict[str, Any] = {"role": "assistant", "content": content}
    if calls:
        msg["tool_calls"] = calls
    return {"id": "c1", "model": "m", "choices": [{"index": 0, "message": msg, "finish_reason": finish}],
            "usage": {"prompt_tokens": prompt, "completion_tokens": out, "prompt_tokens_details": {"cached_tokens": cached}}}


def call(i: str, name: str, **args: Any) -> dict[str, Any]:
    return {"id": i, "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}


def test_request_becomes_a_chat_body(monkeypatch: Any) -> None:
    monkeypatch.delenv("DM_GATEWAY_PARAMS", raising=False)
    body = gateway.to_chat({
        "model": "ali/x", "max_tokens": 99, "system": "You are the DM.", "tools": [TOOL],
        "thinking": {"type": "adaptive"}, "output_config": {"effort": "medium"}, "cache_control": {"type": "ephemeral"},
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": "[Start]"}]},
            {"role": "assistant", "content": [{"type": "thinking", "thinking": "", "signature": "s"},
                                              {"type": "text", "text": "Roll for it."},
                                              {"type": "tool_use", "id": "t1", "name": "roll", "input": {"dice": "1d20"}},
                                              {"type": "tool_use", "id": "t2", "name": "roll", "input": {"dice": "1d6"}}]},
            {"role": "user", "content": [
                {"type": "text", "text": "I climb."},  # the player's line came before the results were added
                {"type": "tool_result", "tool_use_id": "t1", "content": [{"type": "text", "text": "dice 1d20 = 7"}]},
                {"type": "tool_result", "tool_use_id": "t2", "content": "dice 1d6 = 2", "is_error": True}]},
            {"role": "assistant", "content": "A plain string."},
        ]})
    assert set(body) == {"model", "messages", "max_tokens", "tools"}  # nothing of Anthropic's own goes across
    assert body["max_tokens"] == 99
    assert body["tools"] == [{"type": "function", "function": {"name": "roll", "description": "Roll dice.",
                                                              "parameters": TOOL["input_schema"]}}]
    m = body["messages"]
    assert [x["role"] for x in m] == ["system", "user", "assistant", "tool", "tool", "user", "assistant"]
    assert m[0]["content"] == "You are the DM." and m[1]["content"] == "[Start]"
    assert m[2]["content"] == "Roll for it." and "thinking" not in json.dumps(m[2])
    assert [(c["id"], c["function"]["name"], json.loads(c["function"]["arguments"])) for c in m[2]["tool_calls"]] == [
        ("t1", "roll", {"dice": "1d20"}), ("t2", "roll", {"dice": "1d6"})]
    assert (m[3]["tool_call_id"], m[3]["content"]) == ("t1", "dice 1d20 = 7")
    assert (m[4]["tool_call_id"], m[4]["content"]) == ("t2", "dice 1d6 = 2")
    assert m[5]["content"] == "I climb." and m[6] == {"role": "assistant", "content": "A plain string."}


def test_provider_switches_come_from_the_environment(monkeypatch: Any) -> None:
    monkeypatch.setenv("DM_GATEWAY_PARAMS", '{"reasoning_effort": "medium"}')
    body = gateway.to_chat({"model": "ali/x", "max_tokens": 9, "system": "s", "messages": [{"role": "user", "content": "hi"}]})
    assert body["reasoning_effort"] == "medium" and "tools" not in body


def test_reply_becomes_an_anthropic_message() -> None:
    r = gateway.from_chat(chat("Hello.", [call("t1", "roll", dice="1d20")], finish="tool_calls", prompt=1000, out=40, cached=900))
    assert r["content"] == [{"type": "text", "text": "Hello."},
                            {"type": "tool_use", "id": "t1", "name": "roll", "input": {"dice": "1d20"}}]
    assert r["stop_reason"] == "tool_use"
    assert r["usage"] == {"input_tokens": 100, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 900,
                          "output_tokens": 40}
    assert model.context_size(r["usage"]) == 1040  # everything it read and what it wrote
    assert gateway.from_chat(chat("Done."))["stop_reason"] == "end_turn"
    assert gateway.from_chat(chat("Cut off", finish="length"))["stop_reason"] == "max_tokens"
    assert gateway.from_chat(chat(None, [call("t1", "roll")], finish="stop"))["stop_reason"] == "tool_use"  # some gateways say stop
    assert gateway.from_chat(chat(None, finish="content_filter"))["stop_reason"] == "content_filter"
    assert gateway.from_chat(chat(None))["content"] == []


def test_unreadable_replies_fail() -> None:
    bad = chat(None, [{"id": "t1", "type": "function", "function": {"name": "roll", "arguments": "{not json"}}])
    with pytest.raises(model.Failed, match="aren't JSON"):
        gateway.from_chat(bad)
    with pytest.raises(model.Failed, match="no message"):
        gateway.from_chat({"error": "nope"})


def test_send_retries_then_fails(monkeypatch: Any) -> None:
    sleeps: list[float] = []

    async def no_sleep(s: float) -> None:
        sleeps.append(s)
    monkeypatch.setattr(gateway.asyncio, "sleep", no_sleep)
    answers = [(429, "slow down"), (200, json.dumps(chat("Hi.")))]
    monkeypatch.setattr(gateway, "_post", lambda body: answers.pop(0))
    r = asyncio.run(gateway.send({"model": "ali/x", "max_tokens": 9, "system": "s", "messages": [{"role": "user", "content": "x"}]}))
    assert r["content"][0]["text"] == "Hi." and sleeps == [2]
    monkeypatch.setattr(gateway, "_post", lambda body: (401, json.dumps({"error": {"message": "bad key"}})))
    with pytest.raises(model.Failed, match="401: bad key"):
        asyncio.run(gateway.send({"model": "ali/x", "max_tokens": 9, "system": "s", "messages": [{"role": "user", "content": "x"}]}))
    monkeypatch.setattr(gateway, "_post", lambda body: (0, "couldn't reach the gateway (refused)"))
    with pytest.raises(model.Failed, match="couldn't reach"):
        asyncio.run(gateway.send({"model": "ali/x", "max_tokens": 9, "system": "s", "messages": [{"role": "user", "content": "x"}]}))


def test_only_slashed_names_go_to_the_gateway(monkeypatch: Any) -> None:
    seen: list[str] = []

    async def fake(request: dict[str, Any]) -> dict[str, Any]:
        seen.append(request["model"])
        return {"content": []}
    monkeypatch.setattr(gateway, "send", fake)
    assert asyncio.run(model._send({"model": "zai/glm-5.3"})) == {"content": []} and seen == ["zai/glm-5.3"]


def test_the_dm_loop_runs_on_a_gateway_model(monkeypatch: Any, tmp_path: Path) -> None:
    """Tools run, results go back as tool messages, and the save keeps Anthropic-style messages."""
    sent: list[dict[str, Any]] = []
    answers = [chat("Roll for it.", [call("t1", "roll", dice="1d20+5", reason="Athletics")], finish="tool_calls"),
               chat(WHOLE)]

    def post(body: dict[str, Any]) -> tuple[int, str]:
        sent.append(json.loads(json.dumps(body)))
        return 200, json.dumps(answers.pop(0))
    monkeypatch.setattr(gateway, "_post", post)
    monkeypatch.setattr(check, "ENABLED", False)
    said: list[str] = []
    monkeypatch.setattr(play, "print", lambda *a, **k: said.append(" ".join(map(str, a))), raising=False)
    g = play.Game({"sheet": json.loads((CHAR / "fighter.json").read_text(encoding="utf-8")), "model": "ali/qwen3.7-plus"},
                  tmp_path / "save.json")
    g.system = "You are the DM."
    asyncio.run(play.turn(g, "I climb"))
    assert any(WHOLE in s for s in said)
    assert [mm["role"] for mm in g.messages] == ["user", "assistant", "user", "assistant"]
    assert [b["type"] for b in g.messages[1]["content"]] == ["text", "tool_use"]  # as the Claude models' turns are kept
    assert g.messages[2]["content"][0]["type"] == "tool_result" and g.messages[2]["content"][0]["tool_use_id"] == "t1"
    assert sent[0]["model"] == "ali/qwen3.7-plus"
    assert sent[0]["messages"][0] == {"role": "system", "content": play.system_prompt(g.sheet, g.companions)}
    assert {t["function"]["name"] for t in sent[0]["tools"]} >= {"roll", "change_pc", "lookup"}
    roles = [x["role"] for x in sent[1]["messages"]]
    assert roles[-2:] == ["assistant", "tool"] and sent[1]["messages"][-1]["tool_call_id"] == "t1"
    assert sent[1]["messages"][-1]["content"].startswith("dice ")
    again = play.Game(json.loads((tmp_path / "save.json").read_text(encoding="utf-8")), tmp_path / "save.json")
    assert again.messages == g.messages and again.model == "ali/qwen3.7-plus"


def test_a_reply_in_a_set_shape_asks_for_json_mode() -> None:
    schema = {"type": "object", "properties": {"problems": {"type": "array"}}}
    body = gateway.to_chat({"model": "zai/glm-5.3", "max_tokens": 10, "system": "Check.", "messages": [{"role": "user", "content": "x"}],
                            "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": schema}}})
    assert body["response_format"] == {"type": "json_object"}
    assert body["messages"][0]["content"].startswith("Check.") and json.dumps(schema) in body["messages"][0]["content"]
    plain = gateway.to_chat({"model": "zai/glm-5.3", "max_tokens": 10, "messages": [{"role": "user", "content": "x"}]})
    assert "response_format" not in plain


def test_a_streamed_answer_is_put_together() -> None:
    sse = "\n".join("data: " + json.dumps(c) for c in [
        {"id": "x", "model": "m", "choices": [{"delta": {"reasoning_content": "hmm"}}]},
        {"choices": [{"delta": {"content": "You roll "}}]},
        {"choices": [{"delta": {"tool_calls": [{"index": 0, "id": "t1", "function": {"name": "roll", "arguments": "{\"dice\":"}}]}}]},
        {"choices": [{"delta": {"tool_calls": [{"index": 0, "function": {"arguments": "\"1d20\"}"}}]}, "finish_reason": "tool_calls"}]},
        {"choices": [], "usage": {"prompt_tokens": 100, "completion_tokens": 7, "prompt_tokens_details": {"cached_tokens": 60}}}]) + "\ndata: [DONE]\n"
    out = gateway.from_chat(gateway.assemble(sse))
    assert out["stop_reason"] == "tool_use" and out["content"][0] == {"type": "text", "text": "You roll "}
    assert out["content"][1]["input"] == {"dice": "1d20"} and out["content"][1]["id"] == "t1"
    assert out["usage"] == {"input_tokens": 40, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 60, "output_tokens": 7}


def test_send_asks_for_a_stream_and_reads_one(monkeypatch: pytest.MonkeyPatch) -> None:
    sent: list[dict[str, Any]] = []

    def post(body: dict[str, Any]) -> tuple[int, str]:
        sent.append(body)
        return 200, "data: " + json.dumps({"choices": [{"delta": {"content": "Hi."}, "finish_reason": "stop"}]}) + "\n\ndata: [DONE]\n"
    monkeypatch.setattr(gateway, "_post", post)
    out = asyncio.run(gateway.send({"model": "ali/q", "max_tokens": 5, "messages": [{"role": "user", "content": "x"}]}))
    assert sent[0]["stream"] is True and out["content"] == [{"type": "text", "text": "Hi."}] and out["stop_reason"] == "end_turn"


def test_a_models_reasoning_goes_back_only_when_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    reply = {"id": "c", "model": "m", "choices": [{"index": 0, "finish_reason": "stop", "message": {
        "role": "assistant", "content": "Done.", "reasoning_content": "hmm, think"}}], "usage": {}}
    assert [b["type"] for b in gateway.from_chat(reply)["content"]] == ["text"]
    monkeypatch.setenv("DM_GATEWAY_PASS_REASONING", "1")
    got = gateway.from_chat(reply)["content"]
    assert [b["type"] for b in got] == ["thinking", "text"] and got[0]["thinking"] == "hmm, think"
    req = {"model": "deepseek/deepseek-v4-pro", "max_tokens": 5, "messages": [
        {"role": "user", "content": "x"}, {"role": "assistant", "content": got}, {"role": "user", "content": "y"}]}
    assert gateway.to_chat(req)["messages"][1]["reasoning_content"] == "hmm, think"
    monkeypatch.delenv("DM_GATEWAY_PASS_REASONING")
    assert "reasoning_content" not in gateway.to_chat(req)["messages"][1]
    sse = "data: " + json.dumps({"choices": [{"delta": {"reasoning_content": "a"}}]}) + "\ndata: " + json.dumps(
        {"choices": [{"delta": {"reasoning_content": "b", "content": "Hi"}, "finish_reason": "stop"}]}) + "\n"
    assert gateway.assemble(sse)["choices"][0]["message"]["reasoning_content"] == "ab"
