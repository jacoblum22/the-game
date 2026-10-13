"""The DM's loop on the API, with a fake model: tool calls run and their results go back, refusals are marked,
a failed call leaves a conversation that can go on, and the conversation lives in the save."""
import asyncio
import json
from pathlib import Path
from typing import Any

import anthropic
import httpx
from anthropic.types import Message

from dm import model, play

CHAR = Path(__file__).parent.parent / "dm" / "characters"


class Fake:
    """Answers each call with the next reply in the script; an exception in the script is raised instead."""

    def __init__(self, script: list[Any]) -> None:
        self.script, self.calls = script, []
        self.messages = self

    async def create(self, **kw: Any) -> Message:
        self.calls.append(json.loads(json.dumps(kw)))  # a copy: the list grows after the call
        r = self.script.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def reply(*content: dict[str, Any], stop: str = "end_turn") -> Message:
    return Message.model_validate({"id": "msg_1", "type": "message", "role": "assistant", "model": "m",
                                   "content": list(content), "stop_reason": stop, "stop_sequence": None,
                                   "usage": {"input_tokens": 1, "output_tokens": 1}})


def use(i: str, name: str, **inp: Any) -> dict[str, Any]:
    return {"type": "tool_use", "id": i, "name": name, "input": inp}


def text(t: str) -> dict[str, Any]:
    return {"type": "text", "text": t}


def run(monkeypatch: Any, script: list[Any], game: play.Game, line: str) -> tuple[Fake, list[str]]:
    fake = Fake(script)
    monkeypatch.setattr(model, "client", lambda: fake)
    said: list[str] = []
    monkeypatch.setattr(play, "print", lambda *a, **k: said.append(" ".join(map(str, a))), raising=False)
    asyncio.run(play.turn(game, line))
    return fake, said


def new_game(tmp_path: Path) -> play.Game:
    g = play.Game({"sheet": json.loads((CHAR / "fighter.json").read_text(encoding="utf-8"))}, tmp_path / "save.json")
    g.system = "You are the DM."
    return g


def test_tools_run_and_answer(monkeypatch: Any, tmp_path: Path) -> None:
    g = new_game(tmp_path)
    fake, said = run(monkeypatch, [
        reply({"type": "thinking", "thinking": "", "signature": "sig"}, text("Roll for it."),
              use("t1", "roll", dice="1d20+5", reason="Athletics"), use("t2", "change_pc", heal=99999, damage=0),
              stop="tool_use"),
        reply(text("You climb the wall.")),
    ], g, "I climb")
    roles = [mm["role"] for mm in g.messages]
    assert roles == ["user", "assistant", "user", "assistant"]
    results = g.messages[2]["content"]
    assert [r["tool_use_id"] for r in results] == ["t1", "t2"]
    assert results[0]["content"][0]["text"].startswith("dice ") and "is_error" not in results[0]
    assert g.messages[1]["content"][0] == {"type": "thinking", "thinking": "", "signature": "sig"}  # sent back as it came
    assert any("You climb the wall." in s for s in said)
    assert [t["text"] for t in g.transcript if t["kind"] == "dm"] == ["Roll for it.", "You climb the wall."]
    # what went to the API
    first = fake.calls[0]
    assert first["system"] == "You are the DM." and first["cache_control"] == {"type": "ephemeral", "ttl": "1h"}
    assert first["thinking"]["type"] == "adaptive"
    assert {t["name"] for t in first["tools"]} >= {"roll", "change_pc", "lookup", "level_up"}
    assert first["messages"][0]["content"][0]["text"].startswith("[Status now]")
    assert fake.calls[1]["messages"][-1]["content"][0]["type"] == "tool_result"
    # the conversation is in the save, and a resumed game has it
    again = play.Game(json.loads((tmp_path / "save.json").read_text(encoding="utf-8")), tmp_path / "save.json")
    assert again.messages == g.messages


def test_refusal_and_unknown_tool(monkeypatch: Any, tmp_path: Path) -> None:
    g = new_game(tmp_path)
    run(monkeypatch, [
        reply(use("t1", "change_pc", use_resource="Nonsense"), use("t2", "fly"), stop="tool_use"),
        reply(text("Fine.")),
    ], g, "go")
    r1, r2 = g.messages[2]["content"]
    assert r1["is_error"] and r1["content"][0]["text"].startswith("REFUSED")
    assert r2["is_error"] and "no tool called fly" in r2["content"][0]["text"]


def test_failed_call_can_go_on(monkeypatch: Any, tmp_path: Path) -> None:
    g = new_game(tmp_path)
    err = anthropic.APIConnectionError(request=httpx.Request("POST", "https://x"))
    _, said = run(monkeypatch, [err], g, "first")
    assert any("the DM call failed" in s for s in said)
    assert [mm["role"] for mm in g.messages] == ["user"]
    fake, _ = run(monkeypatch, [reply(text("Back."))], g, "second")
    sent = fake.calls[0]["messages"]
    assert [mm["role"] for mm in sent] == ["user"]  # the new line joined the unanswered one
    assert len(sent[0]["content"]) == 2 and "second" in sent[0]["content"][1]["text"]


def test_too_many_rounds(monkeypatch: Any, tmp_path: Path) -> None:
    g = new_game(tmp_path)
    _, said = run(monkeypatch, [reply(use(f"t{i}", "next_turn"), stop="tool_use") for i in range(model.MAX_ROUNDS)],
                  g, "go")
    assert any(f"more than {model.MAX_ROUNDS}" in s for s in said)
    assert g.messages[-1]["role"] == "user"  # the results are kept; the next line joins them


def test_convert_session(tmp_path: Path) -> None:
    """Claude Code's session file: one line per block, blocks of one message share its id; its own rows are dropped."""
    from dm import convert
    rows = [
        {"type": "queue-operation"},
        {"type": "user", "message": {"role": "user", "content": "[Start]"}},
        {"type": "attachment", "attachment": {"type": "date"}},
        {"type": "assistant", "message": {"id": "a", "role": "assistant", "content": [text("Hi.")]}},
        {"type": "assistant", "message": {"id": "a", "role": "assistant", "content": [use("t1", "mcp__dm__roll")]}},
        {"type": "assistant", "message": {"id": "a", "role": "assistant", "content": [use("t2", "mcp__dm__lookup")]}},
        {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "4"}]}},
        {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t2", "content": "x"}]}},
        {"type": "assistant", "message": {"id": "b", "role": "assistant", "content": [text("Done.")]}},
    ]
    p = tmp_path / "s.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    out = convert.messages_from_session(p)
    assert [mm["role"] for mm in out] == ["user", "assistant", "user", "assistant"]
    assert [b.get("name") for b in out[1]["content"]] == [None, "roll", "lookup"]
    assert [b["tool_use_id"] for b in out[2]["content"]] == ["t1", "t2"]
