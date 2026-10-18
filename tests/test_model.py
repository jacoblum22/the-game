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
# a whole reply: after tool calls, a reply under play.FULL_REPLY characters is taken for a stub and asked for again
WHOLE = ("You climb the wall, hand over hand, and pull yourself onto the ledge. " * 5).strip()


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
        reply(text(WHOLE)),
    ], g, "I climb")
    roles = [mm["role"] for mm in g.messages]
    assert roles == ["user", "assistant", "user", "assistant"]
    results = g.messages[2]["content"]
    assert [r["tool_use_id"] for r in results] == ["t1", "t2"]
    assert results[0]["content"][0]["text"].startswith("dice ") and "is_error" not in results[0]
    assert g.messages[1]["content"][0] == {"type": "thinking", "thinking": "", "signature": "sig"}  # sent back as it came
    assert any(WHOLE in s for s in said)
    assert [t["text"] for t in g.transcript if t["kind"] == "dm"] == [WHOLE]  # words before the calls: a note
    assert [t["text"] for t in g.transcript if t["kind"] == "stub"] == ["Roll for it."]
    # what went to the API
    first = fake.calls[0]
    assert first["system"] == play.system_prompt(g.sheet, g.companions) and first["cache_control"] == {"type": "ephemeral", "ttl": "1h"}
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
        reply(text(WHOLE)),
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
    # the reply is asked for once (CUT_SHORT_ASK), and that runs out of calls too
    _, said = run(monkeypatch, [reply(use(f"t{i}", "next_turn"), stop="tool_use") for i in range(2 * model.MAX_ROUNDS)],
                  g, "go")
    assert any(f"more than {model.MAX_ROUNDS}" in s for s in said)
    assert len([t for t in g.transcript if t["kind"] == "failed"]) == 2
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


def test_session(monkeypatch: Any, tmp_path: Path) -> None:
    """The terminal and the browser page both drive a Session a line at a time."""
    monkeypatch.setattr(play, "SAVES", tmp_path)
    fake, said = Fake([reply(text("You stand at the gate.")), reply(text("You open it."))]), []
    monkeypatch.setattr(model, "client", lambda: fake)
    monkeypatch.setattr(play, "print", lambda *a, **k: said.append(" ".join(map(str, a))), raising=False)
    s = play.Session()

    async def go() -> list[bool]:
        await s.new("fighter")
        return [await s.line("  "), await s.line("/sheet"), await s.line("I open the gate"), await s.line("/quit")]
    assert asyncio.run(go()) == [True, True, True, False]
    assert said[0].startswith("Brakka Ironvein, Hill Dwarf fighter 1") and "You stand at the gate." in said[1]
    assert said[2].startswith("Brakka Ironvein: Hill Dwarf fighter 1") and "Abilities:" in said[2]  # the sheet, no model call
    assert "You open it." in said[3] and said[4].startswith("Saved.")
    data = json.loads(s.game.path.read_text(encoding="utf-8"))  # type: ignore[union-attr]
    assert play.resumable(data) == "" and len(data["messages"]) == 4
    assert "> I open the gate" in play.history(data)
    assert play.resumable({"sheet": {}, "session_id": "x"}) == ""  # the terminal runs both kinds
    assert play.resumable({"sheet": {}, "session_id": "x"}, "api").startswith("that save runs on the owner's own")


def test_sdk_session(monkeypatch: Any, tmp_path: Path) -> None:
    """The owner's own version: the same game, with the DM's conversation in Claude Code (a stand-in here)."""
    from dm import sdk
    opened: list[Any] = []

    class FakeClient:
        def __init__(self, model_name: str, system: str, tools: list[Any], cwd: str, session_id: str | None,
                     fork_at: str | None = None, done: Any = None) -> None:
            self.tools, self.cwd, self.session_id, self.closed, self.size = {t.name: t for t in tools}, cwd, session_id, False, 0
            opened.append(self)

        async def open(self) -> None:
            pass

        async def close(self) -> None:
            self.closed = True

        async def respond(self, text: str, on_text: Any) -> None:
            await self.tools["roll"].handler({"dice": "1d20", "reason": "a test"})  # the tools reach the same game
            on_text(WHOLE)
            self.session_id = "sess-1"

    monkeypatch.setattr(sdk, "Client", FakeClient)
    monkeypatch.setattr(play, "SAVES", tmp_path)
    monkeypatch.setattr(play, "print", lambda *a, **k: None, raising=False)
    s = play.Session(backend="sdk")

    async def go() -> None:
        await s.new("fighter")
        await s.line("I look")
        await s.line("/quit")
    asyncio.run(go())
    data = json.loads(s.game.path.read_text(encoding="utf-8"))  # type: ignore[union-attr]
    assert data["backend"] == "sdk" and data["session_id"] == "sess-1" and "messages" not in data
    assert data["cwd"] == play.home_relative(str(sdk.DM_HOME)) and opened[0].closed
    assert sum(t["kind"] == "tool" and t["text"].startswith("dice ") for t in data["transcript"]) == 2
    # resumed: the same Claude Code conversation
    s2 = play.Session(backend="api")  # a save carries on the way it was started
    asyncio.run(s2.play(play.Game(data, s.game.path)))  # type: ignore[union-attr]
    assert opened[-1].session_id == "sess-1" and s2.game.backend == "sdk"  # type: ignore[union-attr]
    assert s2.game.cwd == str(sdk.DM_HOME)  # type: ignore[union-attr]


def test_instructions_follow_the_sheets(monkeypatch: Any, tmp_path: Path) -> None:
    """After a sheet change that the instructions show (a level-up, a companion joining), the next turn sends them
    built again."""
    g = new_game(tmp_path)
    g.system = play.system_prompt(g.sheet, g.companions)
    fake, _ = run(monkeypatch, [reply(text("One."))], g, "a")
    first = fake.calls[0]["system"]
    g.sheet["features"].append("Tough as Old Boots: a new feature")
    fake, _ = run(monkeypatch, [reply(text("Two."))], g, "b")
    assert fake.calls[0]["system"] != first and "Tough as Old Boots" in fake.calls[0]["system"]


def test_sdk_reconnects_for_new_instructions(monkeypatch: Any, tmp_path: Path) -> None:
    from dm import sdk
    opened: list[Any] = []

    class FakeClient:
        def __init__(self, model_name: str, system: str, tools: list[Any], cwd: str, session_id: str | None,
                     fork_at: str | None = None, done: Any = None) -> None:
            self.system, self.session_id, self.closed, self.size = system, session_id, False, 0
            opened.append(self)

        async def open(self) -> None:
            pass

        async def close(self) -> None:
            self.closed = True

        async def respond(self, text: str, on_text: Any) -> None:
            self.session_id = "sess-1"

    monkeypatch.setattr(sdk, "Client", FakeClient)
    monkeypatch.setattr(play, "SAVES", tmp_path)
    monkeypatch.setattr(play, "print", lambda *a, **k: None, raising=False)
    s = play.Session(backend="sdk")

    async def go() -> None:
        await s.new("fighter")
        await s.line("I look")
        s.game.sheet["features"].append("Tough as Old Boots: a new feature")  # type: ignore[union-attr]
        await s.line("I look again")
    asyncio.run(go())
    assert len(opened) == 2 and opened[0].closed and not opened[1].closed
    assert opened[1].session_id == "sess-1" and "Tough as Old Boots" in opened[1].system  # the same conversation


def test_sdk_api_error_is_a_failure(tmp_path: Path) -> None:
    """Claude Code's own error message ("API Error: ... safeguards flagged this message") isn't the DM's reply."""
    from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock

    from dm import sdk
    g = play.Game({"sheet": json.loads((CHAR / "fighter.json").read_text(encoding="utf-8"))}, Path("unused.json"))
    c = sdk.Client("m", "system", g.tools(), str(tmp_path), None)
    flagged = "API Error: Sonnet 5.5's safeguards flagged this message."

    class Stub:
        async def query(self, text: str) -> None:
            pass

        async def receive_response(self) -> Any:
            yield AssistantMessage([TextBlock(flagged)], "<synthetic>", error="invalid_request")
            yield ResultMessage("success", 1, 1, False, 1, "sess-1")
    c.client = Stub()  # type: ignore[assignment]
    said: list[str] = []
    assert asyncio.run(c.respond("I slip in", said.append)) == flagged and said == []


def test_sdk_bridge(tmp_path: Path) -> None:
    """Our tools go to the Agent SDK as they are (nothing connects here)."""
    from dm import sdk
    g = play.Game({"sheet": json.loads((CHAR / "fighter.json").read_text(encoding="utf-8"))}, Path("unused.json"))
    c = sdk.Client("m", "system " * 6000, g.tools(), str(tmp_path), None)
    assert "mcp__dm__roll" in c.options.allowed_tools and "mcp__dm__lookup" in c.options.allowed_tools
    assert c.options.max_turns == model.MAX_ROUNDS and c.options.mcp_servers["dm"]["type"] == "sdk"
    # as on the API: no automatic compaction, and today's instructions on every call (no snapshot)
    assert c.options.env["DISABLE_AUTO_COMPACT"] == "1"
    assert c.options.extra_args == {"system-prompt-snapshot": "off"}
    # the instructions go as a file, since a party's sheets outgrow a Windows command line
    assert c.options.system_prompt["type"] == "file"
    assert Path(c.options.system_prompt["path"]).read_text(encoding="utf-8") == "system " * 6000


def played(g: play.Game, n: int) -> None:
    for i in range(1, n + 1):
        g.log("player", f"line {i}")
        g.log("dm", f"reply {i}")
        g.log("tool", f"dice {i}")
        g.transcript.append({"kind": "call", "tool": "lookup", "input": {}, "result": f"hidden {i}"})


def test_cut(monkeypatch: Any, tmp_path: Path) -> None:
    """Once the conversation is long, the DM writes the story so far; the next turn starts a new conversation with
    that summary and the last turns word for word (no hidden calls), and the summary stays out of the player's view."""
    monkeypatch.setattr(play, "CUT_AT", 2)  # the fake's usage: 1 token in, 1 out
    monkeypatch.setattr(play, "KEEP", 2)
    g = new_game(tmp_path)
    played(g, 4)
    g.messages = [{"role": "user", "content": "old"}, {"role": "assistant", "content": [text("old reply")]}]
    g.log("player", "line 5")
    fake, said = run(monkeypatch, [reply(text("Reply five.")), reply(text("The story: Brakka came."))], g,
                     "[The player]\nline 5")
    assert "turns 4 to 5 word for word" in fake.calls[1]["messages"][-1]["content"][0]["text"]
    assert "end of turn 3" in fake.calls[1]["messages"][-1]["content"][0]["text"]
    assert g.messages == [] and g.story == [{"turn": 3, "text": "The story: Brakka came."}]
    assert not any("The story:" in s for s in said) and g.transcript[-1]["text"].startswith("conversation shortened")
    data = json.loads(g.path.read_text(encoding="utf-8"))
    assert data["story"] == g.story and data["messages"] == []
    monkeypatch.setattr(play, "CUT_AT", 10**6)
    g.log("player", "line 6")
    fake, _ = run(monkeypatch, [reply(text("Reply six."))], g, "[The player]\nline 6")
    first = fake.calls[0]["messages"][0]["content"][0]["text"]
    assert len(fake.calls[0]["messages"]) == 1
    assert first.startswith("[The story so far: your own summary of turns 0 to 3")
    assert "The story: Brakka came." in first and "Turn 4:\nPlayer: line 4\nDM: reply 4\n[dice 4]" in first
    assert "Turn 5:\nPlayer: line 5\nDM: Reply five." in first and "Turn 3:" not in first and "hidden 4" not in first
    assert "Player: line 6" not in first and first.endswith("[The player]\nline 6")
    assert len(g.messages) == 2  # the next call goes on in the same new conversation
    fake, _ = run(monkeypatch, [reply(text("Reply seven."))], g, "[The player]\nline 7")
    assert "story so far" not in fake.calls[0]["messages"][-1]["content"][0]["text"]


def test_no_cut_when_short_or_failed(monkeypatch: Any, tmp_path: Path) -> None:
    g = new_game(tmp_path)
    played(g, 4)
    run(monkeypatch, [reply(text("Fine."))], g, "x")
    assert len(g.messages) == 2 and g.story == []  # under the limit
    monkeypatch.setattr(play, "CUT_AT", 2)
    monkeypatch.setattr(play, "KEEP", 2)
    _, said = run(monkeypatch, [reply(text("Fine.")), reply()], g, "y")  # an empty summary: no cut
    assert len(g.messages) == 6 and g.story == [] and any("trying again next turn" in s for s in said)


def test_sdk_cut(monkeypatch: Any, tmp_path: Path) -> None:
    """The owner's version: the summary comes from the old Claude Code conversation, and a new one starts."""
    from dm import sdk
    opened: list[Any] = []

    class FakeClient:
        def __init__(self, model_name: str, system: str, tools: list[Any], cwd: str, session_id: str | None,
                     fork_at: str | None = None, done: Any = None) -> None:
            self.session_id, self.closed, self.size, self.got = session_id, False, 0, []
            opened.append(self)

        async def open(self) -> None:
            pass

        async def close(self) -> None:
            self.closed = True

        async def respond(self, text: str, on_text: Any) -> None:
            self.got.append(text)
            on_text("Summary." if "cut short" in text else "Reply.")
            self.session_id, self.size = self.session_id or f"sess-{len(opened)}", 300_000

    monkeypatch.setattr(play, "KEEP", 20)
    monkeypatch.setattr(sdk, "Client", FakeClient)
    monkeypatch.setattr(play, "SAVES", tmp_path)
    monkeypatch.setattr(play, "print", lambda *a, **k: None, raising=False)
    s = play.Session(backend="sdk")

    async def go() -> None:
        await s.new("fighter")
        played(s.game, 25)  # type: ignore[arg-type]
        await s.line("I look")
        await s.line("I look again")
    asyncio.run(go())
    g = s.game
    assert g is not None and g.story[0] == {"turn": 6, "text": "Summary."}
    assert opened[0].closed and opened[1].closed and len(opened) == 3
    assert opened[1].got[0].startswith("[The story so far: your own summary of turns 0 to 6")
    assert "Turn 26:\nPlayer: I look\nDM: Reply." in opened[1].got[0] and "Turn 6:" not in opened[1].got[0]
    assert g.session_id is None and g.story[1]["turn"] == 7  # the size stayed large: the next turn cut again


def test_stub_is_asked_for_again(monkeypatch: Any, tmp_path: Path) -> None:
    """A few words after tool calls is a stub: the DM drafted its reply in thinking and never wrote it. The player
    sees only the full reply asked for in its place (owner, 2026-10-14)."""
    g = new_game(tmp_path)
    fake, said = run(monkeypatch, [
        reply(use("t1", "roll", dice="1d20", reason="Perception"), stop="tool_use"),
        reply(text("Both are recorded on your sheet.")),
        reply(text(WHOLE)),
    ], g, "I look")
    assert [t["text"] for t in g.transcript if t["kind"] == "stub"] == ["Both are recorded on your sheet."]
    assert [t["text"] for t in g.transcript if t["kind"] == "dm"] == [WHOLE]
    assert not any("Both are recorded" in s for s in said) and any(WHOLE in s for s in said)
    asked = fake.calls[2]["messages"][-1]["content"]
    assert play.STUB_ASK.format("Both are recorded on your sheet.") in json.loads(json.dumps(asked))[-1]["text"]


def test_reply_cut_short_is_asked_for(monkeypatch: Any, tmp_path: Path) -> None:
    """A turn that runs out of model calls after tool calls, with no reply written: the DM is asked once for it."""
    g = new_game(tmp_path)
    monkeypatch.setattr(model, "MAX_ROUNDS", 2)
    fake, said = run(monkeypatch, [
        reply(use("t1", "roll", dice="1d20", reason="claw"), stop="tool_use"),
        reply(use("t2", "roll", dice="1d20", reason="claw"), stop="tool_use"),
        reply(text(WHOLE)),
    ], g, "I hold my ground")
    assert [t["text"] for t in g.transcript if t["kind"] == "failed"] == ["the reply took more than 2 model calls"]
    assert [t["text"] for t in g.transcript if t["kind"] == "dm"] == [WHOLE] and any(WHOLE in s for s in said)
    asked = json.dumps(fake.calls[2]["messages"][-1]["content"])
    assert "Your turn stopped before you wrote your reply (the reply took more than 2 model calls)" in asked
    assert "t2" in asked  # the last tool results and the ask go in the same user turn


def test_failure_without_tools_is_not_asked_again(monkeypatch: Any, tmp_path: Path) -> None:
    g = new_game(tmp_path)
    fake, _ = run(monkeypatch, [reply(text("Half a"), stop="max_tokens")], g, "I look")
    assert len(fake.calls) == 1
    assert [t["text"] for t in g.transcript if t["kind"] == "failed"] == ["the reply stopped: max_tokens"]


def test_note_before_tool_calls_is_not_shown(monkeypatch: Any, tmp_path: Path) -> None:
    """A few words, then tool calls, then the reply: the words were a note, not part of the reply."""
    g = new_game(tmp_path)
    _, said = run(monkeypatch, [
        reply(text("Miss. Next."), use("t1", "roll", dice="1d20", reason="bite"), stop="tool_use"),
        reply(text(WHOLE)),
    ], g, "I attack")
    assert [t["text"] for t in g.transcript if t["kind"] == "stub"] == ["Miss. Next."]
    assert [t["text"] for t in g.transcript if t["kind"] == "dm"] == [WHOLE]
    assert not any("Miss. Next." in s for s in said)


def test_short_reply_without_tools_stands(monkeypatch: Any, tmp_path: Path) -> None:
    g = new_game(tmp_path)
    fake, _ = run(monkeypatch, [reply(text("Yes, you can."))], g, "DM: can I?")
    assert len(fake.calls) == 1 and [t["text"] for t in g.transcript if t["kind"] == "dm"] == ["Yes, you can."]


def test_bookkeeping_with_the_reply_ends_the_turn(monkeypatch: Any, tmp_path: Path) -> None:
    """The reply and the record of it in one model call: the tools run and the DM isn't called again to read them."""
    g = new_game(tmp_path)
    g.clock, _ = play.m.change_time(g.clock, {"set": {"day": 1, "time": "17:50"}})
    fake, said = run(monkeypatch, [
        reply(text(WHOLE), use("t1", "change_time", advance={"minutes": 7}),
              use("t2", "write_lore", create="The Ledge", kind="place", description="A ledge above the wall."), stop="tool_use"),
    ], g, "I climb")
    assert len(fake.calls) == 1 and "Day 1, 5:57 PM" in play.m.clock_text(g.clock)
    assert [t["text"] for t in g.transcript if t["kind"] == "dm"] == [WHOLE] and any(WHOLE in s for s in said)
    assert [mm["role"] for mm in g.messages] == ["user", "assistant", "user"]
    fake2, _ = run(monkeypatch, [reply(text(WHOLE))], g, "I look around")
    assert [mm["role"] for mm in g.messages] == ["user", "assistant", "user", "assistant"]
    assert g.messages[2]["content"][-1]["text"].endswith("I look around")  # joins the tool results


def test_bookkeeping_error_goes_back(monkeypatch: Any, tmp_path: Path) -> None:
    """A bookkeeping call that fails goes back to the DM; its words after that are not shown."""
    g = new_game(tmp_path)
    fake, said = run(monkeypatch, [
        reply(text(WHOLE), use("t1", "change_pc", items_lost=[{"item": "Nothing Such"}]), stop="tool_use"),
        reply(text("Fixed.")),
    ], g, "I go on")
    assert len(fake.calls) == 2 and g.messages[2]["content"][0].get("is_error")
    assert [t["text"] for t in g.transcript if t["kind"] == "dm"] == [WHOLE]


def test_a_reply_needing_a_result_goes_on(monkeypatch: Any, tmp_path: Path) -> None:
    """A lookup with the reply is not bookkeeping: the DM is called again, as before."""
    g = new_game(tmp_path)
    fake, _ = run(monkeypatch, [
        reply(text(WHOLE), use("t1", "lore", names=["Nobody"]), stop="tool_use"),
        reply(text("ok")),
    ], g, "I go on")
    assert len(fake.calls) == 2


def test_call_after_the_reply(monkeypatch: Any, tmp_path: Path) -> None:
    """After a full reply, a call still counts and a roll is refused; what the DM writes then is never shown."""
    g = new_game(tmp_path)
    g.clock, _ = play.m.change_time(g.clock, {"set": {"day": 1, "time": "17:50"}})
    _, said = run(monkeypatch, [
        reply(text(WHOLE), use("t1", "change_time", advance={"minutes": 7}),
              use("t2", "roll", dice="1d20", reason="late"), stop="tool_use"),
        reply(text("The clock now reads 5:57 PM.")),
    ], g, "I go on")
    r1, r2 = g.messages[2]["content"]
    assert "Day 1, 5:57 PM" in play.m.clock_text(g.clock) and play.LATE not in json.dumps(r1)
    assert r2["is_error"] and r2["content"][0]["text"].startswith("REFUSED, nothing rolled")
    assert not any(t["kind"] == "tool" and t["text"].startswith("dice ") for t in g.transcript)
    assert [t["text"] for t in g.transcript if t["kind"] == "dm"] == [WHOLE]
    assert [t["text"] for t in g.transcript if t["kind"] == "hidden"] == ["The clock now reads 5:57 PM."]
    assert not any("clock now reads" in s for s in said)
