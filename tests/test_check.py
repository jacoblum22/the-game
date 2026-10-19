"""The continuity checker (dm/check.py): what it reads, which of its problems the game acts on, and what the game does
with them: a text fix in the reply and in the DM's conversation, or the reply sent back to the DM to write again."""
import asyncio
import json
from pathlib import Path
from typing import Any

import pytest
from test_model import WHOLE, Fake, new_game, reply, text, use

from dm import check, model, play

EARLIER = "The foreman says the barge leaves at dawn, and the toll is twelve silver."
NOW = "The foreman nods. 'The barge leaves at noon, friend, and the toll is twelve silver.'"


def problem(**kw: Any) -> dict[str, Any]:
    return {"quote": "leaves at noon", "clashes_with": "the barge leaves at dawn", "severity": 3, "fix": "text",
            "replacement": "leaves at dawn", "earlier_quote": "the barge leaves at dawn",
            "earlier_where": "earlier play", "topics": ["place"]} | kw


STATE = f"NOTEBOOK\n\nEARLIER PLAY\n{EARLIER}\n\nNEW REPLY\n{NOW}"


def test_cutoffs_are_by_topic() -> None:
    assert check.acts(problem(severity=2, topics=["items"]))
    assert not check.acts(problem(severity=2, topics=["deeds"]))
    assert check.acts(problem(severity=3, topics=["deeds"]))
    assert not check.acts(problem(severity=3, topics=["time"]))
    assert check.acts(problem(severity=4, topics=["time"]))
    assert check.acts(problem(severity=2, topics=["time", "items"]))  # the lowest of its topics
    assert not check.acts(problem(severity=1, topics=["count"]))


def test_a_problem_whose_earlier_line_is_not_there_is_dropped() -> None:
    ok = problem(earlier_quote="the barge leaves at DAWN")  # case and spacing don't matter
    assert [p["quote"] for p in check.kept({"problems": [ok]}, STATE)] == ["leaves at noon"]
    assert check.kept({"problems": [problem(earlier_quote="the barge never leaves")]}, STATE) == []
    # 'same reply' looks only in the reply, other places only before it
    assert check.kept({"problems": [problem(earlier_where="same reply")]}, STATE) == []


def test_what_goes_back_to_the_dm() -> None:
    reply_ = "It leaves at noon."
    whole = problem()
    assert check.sort([whole], reply_, False) == ([], [whole])
    for p in (problem(topics=["time"]), problem(topics=["items"]), problem(topics=["mechanics"]), problem(fix="dm"),
              problem(replacement=""), problem(quote="words that are not in the reply")):
        assert check.sort([p], reply_, False) == ([p], [])
    assert check.sort([whole | {"topics": ["count"]}], reply_, False)[1] != []
    assert check.sort([whole | {"topics": ["count"]}], reply_, True)[0] != []  # enemies in a fight


def test_the_opening_is_not_checked(monkeypatch: Any, tmp_path: Path) -> None:
    monkeypatch.setattr(check, "ENABLED", True)
    g = new_game(tmp_path)
    fake = Fake([say(LONG)])
    monkeypatch.setattr(model, "client", lambda: fake)
    monkeypatch.setattr(play, "print", lambda *a, **k: None, raising=False)
    asyncio.run(play.turn(g, "[Start]"))
    assert not any(e["kind"] == "check" for e in g.transcript)
    assert "NEW REPLY" in check.context(g.lore, g.transcript, "x")  # no player line yet: no crash


def test_the_checker_reads_notes_turns_and_reply() -> None:
    from dm import lore as notebook
    lore, _ = notebook.write(notebook.new(), {"create": "Hale", "kind": "person", "description": "the foreman"}, 1)
    t = [{"kind": "player", "text": "I ask about the barge"}, {"kind": "dm", "text": EARLIER},
         {"kind": "player", "text": "I ask again"}]
    s = check.context(lore, t, "Hale nods.")
    assert "the foreman" in s and EARLIER in s and s.endswith("NEW REPLY\nHale nods.")
    assert s.index("Hale") < s.index("EARLIER PLAY") < s.index("NEW REPLY")


def play_turn(monkeypatch: Any, tmp_path: Path, script: list[Any], answer: Any, fight: bool = False) -> tuple[Fake, list[str], play.Game]:
    monkeypatch.setattr(check, "ENABLED", True)
    seen: list[str] = []

    async def fake_check(backend: str, system: str, state: str) -> dict[str, Any]:
        seen.append(state)
        if isinstance(answer, Exception):
            raise answer
        return answer
    monkeypatch.setattr(check, "ask_model", fake_check)
    g = new_game(tmp_path)
    g.backend, g.fight = "api", ({"order": []} if fight else None)
    g.log("dm", EARLIER)
    g.log("player", "I ask again")
    fake = Fake(script)
    monkeypatch.setattr(model, "client", lambda: fake)
    said: list[str] = []
    monkeypatch.setattr(play, "print", lambda *a, **k: said.append(" ".join(map(str, a))), raising=False)
    asyncio.run(play.turn(g, "[The player]\nI ask again"))
    return fake, said, g


def say(t: str) -> Any:
    return reply(use("r", "reply", text=t), stop="tool_use")


def answer(*ps: dict[str, Any]) -> dict[str, Any]:
    return {"problems": [p | {"earlier_quote": EARLIER[:40]} for p in ps]}


LONG = ("The foreman leans on the rail. " * 4) + "The barge leaves at noon, friend. What do you do?"


def test_a_text_fix_is_in_the_reply_and_the_conversation(monkeypatch: Any, tmp_path: Path) -> None:
    ps = answer(problem(quote="The barge leaves at noon, friend.", replacement="The barge leaves at dawn, friend.",
                        earlier_quote="The foreman says the barge"))
    fake, said, g = play_turn(monkeypatch, tmp_path, [say(LONG), reply(text("ok"))], ps)
    shown = [e["text"] for e in g.transcript if e["kind"] == "dm"][-1]
    assert "leaves at dawn" in shown and "noon" not in shown and "leaves at dawn" in said[-1]
    assert len(fake.calls) == 1  # no second DM call
    assert "noon" not in json.dumps(g.messages) and "leaves at dawn" in json.dumps(g.messages)
    assert any(e["kind"] == "check" for e in g.transcript)


def test_a_clash_over_time_goes_back_to_the_dm(monkeypatch: Any, tmp_path: Path) -> None:
    ps = answer(problem(topics=["time"], severity=4, quote="leaves at noon", earlier_quote="The foreman says the barge"))
    fixed = LONG.replace("noon", "dawn")
    fake, said, g = play_turn(monkeypatch, tmp_path, [say(LONG), say(fixed)], ps)
    assert len(fake.calls) == 2
    assert "NOT shown" in json.dumps(fake.calls[1]["messages"][-1]) and "leaves at noon" in json.dumps(fake.calls[1]["messages"][-1])
    assert [e["text"] for e in g.transcript if e["kind"] == "dm"][-1] == fixed
    assert sum("barge leaves" in x for x in said) == 1  # the first reply was never shown
    assert "leaves at dawn" in json.dumps(g.messages[-2:])  # the conversation goes on from the second reply


def test_a_failed_hand_back_shows_the_first_reply(monkeypatch: Any, tmp_path: Path) -> None:
    ps = answer(problem(topics=["time"], severity=4, quote="leaves at noon", earlier_quote="The foreman says the barge"))
    fake, said, g = play_turn(monkeypatch, tmp_path, [say(LONG), model.Failed("down")], ps)
    assert [e["text"] for e in g.transcript if e["kind"] == "dm"][-1] == LONG


def test_a_checker_that_fails_changes_nothing(monkeypatch: Any, tmp_path: Path) -> None:
    fake, said, g = play_turn(monkeypatch, tmp_path, [say(LONG)], model.Failed("overloaded"))
    assert [e["text"] for e in g.transcript if e["kind"] == "dm"][-1] == LONG and len(fake.calls) == 1
    fake, said, g = play_turn(monkeypatch, tmp_path, [say(LONG)], {"problems": [{"quote": "x"}]})  # a bad answer
    assert [e["text"] for e in g.transcript if e["kind"] == "dm"][-1] == LONG


def test_no_problems_no_change(monkeypatch: Any, tmp_path: Path) -> None:
    fake, said, g = play_turn(monkeypatch, tmp_path, [say(LONG)], {"problems": []})
    assert [e["text"] for e in g.transcript if e["kind"] == "dm"][-1] == LONG and len(fake.calls) == 1
    assert "EARLIER PLAY" in check_state(g)


def check_state(g: play.Game) -> str:
    return check.context(g.lore, g.transcript, "x")


def test_the_checker_is_called_with_the_api_request(monkeypatch: Any) -> None:
    sent: list[dict[str, Any]] = []

    async def send(req: dict[str, Any]) -> dict[str, Any]:
        sent.append(req)
        return {"content": [{"type": "text", "text": json.dumps({"problems": []})}]}
    monkeypatch.setattr(model, "send", send)
    assert asyncio.run(check.ask_model("api", "sys", "state")) == {"problems": []}
    assert sent[0]["model"] == "claude-sonnet-5-5" and sent[0]["output_config"]["format"]["type"] == "json_schema"


def test_finish_character_needs_the_backstory_and_the_dm_gets_it(tmp_path: Path) -> None:
    c = play.Creation(tmp_path / "new.json")
    tools = {t.name: t for t in c.tools()}
    c.draft = json.loads((play.HERE / "characters" / "fighter.json").read_text(encoding="utf-8"))
    r = asyncio.run(tools["finish_character"].handler({"opening": "At the gate.", "backstory": "  "}))
    assert r.get("is_error") and not c.done
    r = asyncio.run(tools["finish_character"].handler({"opening": "At the gate.", "backstory": "Born in Karrowmere."}))
    assert not r.get("is_error") and c.done and c.draft["backstory"] == "Born in Karrowmere."
    system = play.system_prompt(c.draft, [])
    assert "Born in Karrowmere." in system and "## The character's past" in system
    assert "## The character's past" not in play.system_prompt(c.draft | {"backstory": ""}, [])


def test_start_message_asks_for_the_past_in_the_notebook(monkeypatch: Any, tmp_path: Path) -> None:
    sent: list[str] = []

    async def fake_turn(game: Any, text: str) -> None:
        sent.append(text)
    monkeypatch.setattr(play, "turn", fake_turn)
    monkeypatch.setattr(play, "print", lambda *a, **k: None, raising=False)
    for backstory in ("Born in Karrowmere.", ""):
        g = new_game(tmp_path)
        g.sheet = g.sheet | {"backstory": backstory}
        s = play.Session(backend="api")

        async def connect(x: Any) -> None:
            return None
        monkeypatch.setattr(s, "connect", connect)
        asyncio.run(s.play(g))
    assert "the notebook" in sent[0] and "past" in sent[0] and "the notebook" not in sent[1]


def test_character_creation_opens_with_fixed_words_and_no_model_call(monkeypatch: Any, tmp_path: Path) -> None:
    fake = Fake([reply(text("Human paladin, good choice. Do you want to roll your scores?"))])
    monkeypatch.setattr(model, "client", lambda: fake)
    monkeypatch.setattr(play, "SAVES", tmp_path)
    said: list[str] = []
    monkeypatch.setattr(play, "print", lambda *a, **k: said.append(" ".join(map(str, a))), raising=False)
    s = play.Session(backend="api")
    asyncio.run(s.new("new"))
    assert fake.calls == [] and play.GREETING in "\n".join(said)  # nothing asked of the model yet
    assert s.creation and s.creation.transcript[0] == {"kind": "dm", "text": play.GREETING}
    asyncio.run(s.line("A human paladin"))
    first = fake.calls[0]["messages"][0]["content"]
    first = first if isinstance(first, str) else first[0]["text"]
    assert play.GREETING in first and first.endswith("[The player]\nA human paladin")
    assert len(fake.calls) == 1 and s.creation.greeting is None


def test_sheet_shows_the_backstory(tmp_path: Path) -> None:
    g = new_game(tmp_path)
    assert "Backstory" not in play.sheet_report(g)
    g.sheet = g.sheet | {"backstory": "Born in Karrowmere.\n\nRaised by monks."}
    r = play.sheet_report(g)
    assert "\nBackstory: Born in Karrowmere. Raised by monks.\n" in r
    assert "Backstory" not in play.sheet_text(g.sheet)  # the DM's instructions show the past once, in its own section
