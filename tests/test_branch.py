"""Going back (dm/branch.py): a fork from one of the player's earlier lines puts the game back as it was, in a new
save; the DM's latest reply can be edited, in the transcript and in its conversation; a closing read-out of the sheet
is taken out of the reply and the conversation."""
import asyncio
import json
from pathlib import Path
from typing import Any

from test_model import CHAR, WHOLE, Fake, reply, text, use

from dm import branch, model, play

STAT = "You have 17 of 17 hit points, three slots and three Bardic Inspirations."


def session(monkeypatch: Any, tmp_path: Path, script: list[Any]) -> tuple[play.Session, Fake, list[str]]:
    fake = Fake(script)
    monkeypatch.setattr(model, "client", lambda: fake)
    monkeypatch.setattr(play, "SAVES", tmp_path)
    said: list[str] = []
    monkeypatch.setattr(play, "print", lambda *a, **k: said.append(" ".join(map(str, a))), raising=False)
    s = play.Session(backend="api")
    g = play.Game({"sheet": json.loads((CHAR / "fighter.json").read_text(encoding="utf-8")),
                   "transcript": [{"kind": "dm", "text": "You stand at the gate."}],
                   "messages": [{"role": "user", "content": "[Start]"},
                                {"role": "assistant", "content": [text("You stand at the gate.")]}]},
                  tmp_path / "game.json")
    asyncio.run(s.play(g))
    return s, fake, said


def test_redo_puts_the_game_back_in_a_new_save(monkeypatch: Any, tmp_path: Path) -> None:
    hurt = WHOLE + " The claw opens your arm."
    s, fake, said = session(monkeypatch, tmp_path, [
        reply(text(WHOLE)),
        reply(use("t1", "change_pc", damage=5, heal=0), stop="tool_use"), reply(text(hurt)),
        reply(text(WHOLE + " This time you step aside.")),
    ])
    first = s.game
    assert first
    asyncio.run(s.line("I open the gate"))
    hp = first.sheet["hp"]["current"]
    asyncio.run(s.line("I fight the bear"))
    assert first.sheet["hp"]["current"] == hp - 5
    asyncio.run(s.line("/redo 2 I climb the wall instead"))
    fork = s.game
    assert fork is not first and fork.path != first.path and first.path.exists()
    assert fork.sheet["hp"]["current"] == hp  # the damage of the old turn 2 is undone
    assert [e["text"] for e in fork.transcript if e["kind"] == "player"] == ["I open the gate", "I climb the wall instead"]
    sent = fake.calls[-1]["messages"]
    assert "I fight the bear" not in json.dumps(sent) and "I climb the wall instead" in json.dumps(sent[-1])
    assert len(sent) == 5  # start, reply, turn 1 and its reply, the new line
    saved = json.loads(first.path.read_text(encoding="utf-8"))
    assert [e["text"] for e in saved["transcript"] if e["kind"] == "player"] == ["I open the gate", "I fight the bear"]


def test_redo_without_a_line_sends_the_same_one(monkeypatch: Any, tmp_path: Path) -> None:
    s, fake, _ = session(monkeypatch, tmp_path, [reply(text(WHOLE)), reply(text(WHOLE + " Again."))])
    asyncio.run(s.line("I knock"))
    asyncio.run(s.line("/redo 1"))
    assert s.game and [e["text"] for e in s.game.transcript if e["kind"] == "player"] == ["I knock"]
    assert len(fake.calls) == 2


def test_redo_of_an_unknown_turn_changes_nothing(monkeypatch: Any, tmp_path: Path) -> None:
    s, fake, said = session(monkeypatch, tmp_path, [reply(text(WHOLE))])
    g = s.game
    asyncio.run(s.line("/redo 7"))
    assert s.game is g and not fake.calls and any("no going back to turn 7" in x for x in said)


def test_fork_after_a_cut_opens_with_the_turns_so_far(monkeypatch: Any, tmp_path: Path) -> None:
    s, fake, _ = session(monkeypatch, tmp_path, [reply(text(WHOLE)), reply(text(WHOLE)), reply(text(WHOLE))])
    asyncio.run(s.line("I knock"))
    asyncio.run(s.line("I wait"))
    g = s.game
    assert g
    g.story.append({"turn": 1, "text": "Summary."})  # a cut after turn 1
    g.messages = []
    asyncio.run(s.line("/redo 2 I shout"))
    first = json.dumps(fake.calls[-1]["messages"][0])
    assert "The game so far, word for word" in first and "I knock" in first and "I wait" not in first


def test_edit_changes_the_reply_and_the_conversation(monkeypatch: Any, tmp_path: Path) -> None:
    s, fake, said = session(monkeypatch, tmp_path, [reply(text(WHOLE + " You could fight or flee.")),
                                                     reply(text(WHOLE))])
    asyncio.run(s.line("I knock"))
    asyncio.run(s.line("/edit The door opens.\\nA dog barks."))
    g = s.game
    assert g
    assert [e["text"] for e in g.transcript if e["kind"] == "dm"][-1] == "The door opens.\nA dog barks."
    assert any(e["kind"] == "edited" and "You could fight or flee." in e["text"] for e in g.transcript)
    asyncio.run(s.line("I go in"))
    sent = json.dumps(fake.calls[-1]["messages"])
    assert "fight or flee" not in sent and "The door opens.\\nA dog barks." in sent


def test_edit_with_no_reply_since_the_last_line_is_refused(monkeypatch: Any, tmp_path: Path) -> None:
    s, _, said = session(monkeypatch, tmp_path, [model.Failed("down")])
    asyncio.run(s.line("I knock"))
    asyncio.run(s.line("/edit Something."))
    assert any("no reply from the DM since your last line" in x for x in said)


def test_closing_stat_line_is_taken_out(monkeypatch: Any, tmp_path: Path) -> None:
    s, fake, said = session(monkeypatch, tmp_path, [reply(text(f"{WHOLE}\n\nIt's dusk. {STAT} What do you do?")),
                                                     reply(text(WHOLE))])
    asyncio.run(s.line("I rest by the fire"))
    g = s.game
    assert g
    assert [e["text"] for e in g.transcript if e["kind"] == "dm"][-1] == f"{WHOLE}\n\nIt's dusk. What do you do?"
    assert [e["text"] for e in g.transcript if e["kind"] == "trimmed"] == [STAT]
    assert not any("17 of 17" in x for x in said)
    asyncio.run(s.line("I sleep"))
    assert "17 of 17" not in json.dumps(fake.calls[-1]["messages"])


def test_stat_line_stays_when_asked_or_not_closing() -> None:
    assert branch.without_stat_line(f"{WHOLE}\n\n{STAT}", "DM: how am I doing?")[1] == ""
    assert branch.without_stat_line(f"{STAT} The bear charges.\n\nWhat do you do?", "I wait")[1] == ""
    assert branch.without_stat_line(STAT, "I wait") == (STAT, "")  # never the whole reply


def test_lore_is_built_again_from_the_calls() -> None:
    t = [{"kind": "player", "text": "hi"},
         {"kind": "call", "tool": "write_lore", "input": {"create": "Vessa", "kind": "person", "description": "a fence"}},
         {"kind": "call", "tool": "write_lore", "input": {"entry": "Nobody", "description": "x"}}]  # refused: skipped
    assert list(branch.rebuilt_lore(t)["entries"]) == ["Vessa"]


# ---------- a new PC after a death ----------
DUNMAR = {"name": "Dunmar", "race": "Human", "class": "Cleric", "ability_method": "standard_array",
          "base_scores": {"STR": 8, "DEX": 10, "CON": 13, "INT": 12, "WIS": 15, "CHA": 14},
          "choices": {"race.languages": "a", "class.proficiencies.1": ["c", "d"], "class.equipment.1": "a",
                      "class.equipment.2": "b", "class.equipment.3": "a", "class.equipment.4": "a",
                      "class.equipment.5": "Emblem", "background.languages": ["Dwarvish", "Giant"],
                      "background.equipment.1": "Emblem", "background.equipment.prayer": "a"},
          "cantrips": ["Light", "Sacred Flame", "Thaumaturgy"], "spells": [], "prepared": ["Sanctuary", "Healing Word"]}


def test_new_pc_only_after_a_death_and_after_a_yes(tmp_path: Path) -> None:
    g = play.Game({"sheet": json.loads((CHAR / "fighter.json").read_text(encoding="utf-8"))}, tmp_path / "g.json")
    old = g.sheet["name"]
    try:
        g.new_pc({"character": DUNMAR})
        raise AssertionError("refused while alive")
    except play.m.Refused as e:
        assert "only when the PC is dead" in str(e)
    g.sheet["conditions"].append("dead")
    shown = g.new_pc({"character": DUNMAR})
    assert shown.startswith("BUILT, nothing changed yet") and g.sheet["name"] == old
    try:
        g.new_pc({"character": DUNMAR, "confirm": True})
        raise AssertionError("refused without an opening")
    except play.m.Refused as e:
        assert "opening is empty" in str(e)
    g.new_pc({"character": DUNMAR, "confirm": True, "opening": "Dunmar comes down the north road a year later."})
    assert g.sheet["name"] == "Dunmar" and g.sheet["opening"].startswith("Dunmar comes")
    assert [p["name"] for p in g.past_pcs] == [old] and "dead" in g.past_pcs[0]["conditions"]
    assert "Dunmar" in play.system_prompt(g.sheet, g.companions)
    g.save()
    again = play.Game(json.loads(g.path.read_text(encoding="utf-8")), g.path)
    assert again.sheet["name"] == "Dunmar" and again.past_pcs[0]["name"] == old


def test_new_pc_rolls_once(tmp_path: Path) -> None:
    g = play.Game({"sheet": json.loads((CHAR / "fighter.json").read_text(encoding="utf-8"))}, tmp_path / "g.json")
    g.sheet["conditions"].append("dead")
    assert g.roll_new_scores().startswith("ability scores rolled") and len(g.new_rolled or []) == 6
    try:
        g.roll_new_scores()
        raise AssertionError("rolled twice")
    except play.m.Refused:
        pass
