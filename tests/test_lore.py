"""The DM's notebook: entries, relationships shown on every entry they mention, connections, recall, the notes each
turn, and that the player never sees any of it."""
import asyncio
import json
from pathlib import Path

import pytest

from dm import lore as nb
from dm import play
from dm.mechanics import Refused

CHAR = Path(__file__).parent.parent / "dm" / "characters"


def said(*turns: tuple[str, str]) -> list[dict[str, str]]:
    """A transcript: the opening (DM), then (player line, DM reply) for each turn."""
    t = [{"kind": "dm", "text": "You stand at the gate of Millbrook."}]
    for p, d in turns:
        t += [{"kind": "player", "text": p}, {"kind": "dm", "text": d}]
    return t


def book() -> dict:
    lore = nb.new()
    for a, turn in (
        ({"create": "Vessa", "kind": "person", "other_names": ["the Fence"], "description": "Half-elf, fifties.",
          "relationships": ["runs the [[Thieves Guild]] from the back of the [[Copper Kettle]]"]}, 2),
        ({"create": "Thieves Guild", "kind": "group", "other_names": ["the Guild"], "description": "Millbrook's thieves."}, 2),
        ({"create": "Copper Kettle", "kind": "place", "description": "A tavern by the river."}, 2),
        ({"create": "Captain Orm", "kind": "person", "description": "Head of the watch.",
          "relationships": ["takes the Guild's bribes"]}, 4),
        ({"create": "Brakka", "kind": "person", "description": "The PC."}, 1),
        ({"entry": "Vessa", "add_relationships": ["owes [[Brakka]] a favour"]}, 5),
    ):
        lore, _ = nb.write(lore, a, turn)
    return lore


def test_write() -> None:
    lore = nb.new()
    lore, text = nb.write(lore, {"create": "Vessa", "kind": "person", "description": "Half-elf.",
                                 "relationships": ["runs the [[Thieves Guild]]"]}, 3)
    assert text == ("entry Vessa (person) created; relationship [1] added to Vessa; no entry yet for Thieves Guild "
                    "(create one if it matters)")
    assert lore["relationships"] == [{"id": 1, "from": "Vessa", "text": "runs the [[Thieves Guild]]", "turn": 3}]
    with pytest.raises(Refused, match="already an entry"):
        nb.write(lore, {"create": "vessa", "kind": "person", "description": "x"}, 4)
    lore, _ = nb.write(lore, {"entry": "Vessa", "add_other_names": ["the Fence"]}, 4)
    with pytest.raises(Refused, match="another name of Vessa"):
        nb.write(lore, {"create": "The Fence", "kind": "person", "description": "x"}, 4)
    lore, _ = nb.write(lore, {"entry": "the fence", "add_to_description": "Lost an eye."}, 9)
    assert lore["entries"]["Vessa"]["description"] == [{"text": "Half-elf.", "turn": 3}, {"text": "Lost an eye.", "turn": 9}]
    lore2, _ = nb.write(lore, {"entry": "Vessa", "description": "One-eyed half-elf."}, 10)
    assert lore2["entries"]["Vessa"]["description"] == [{"text": "One-eyed half-elf.", "turn": 10}]
    lore, _ = nb.write(lore, {"change_relationship": 1, "text": "ran the [[Thieves Guild]]"}, 11)
    assert lore["relationships"][0] | {} == {"id": 1, "from": "Vessa", "text": "ran the [[Thieves Guild]]", "turn": 11}
    with pytest.raises(Refused, match="no relationship"):
        nb.write(lore, {"remove_relationship": 5}, 11)
    with pytest.raises(Refused, match="no entry 'Vesa': close matches"):
        nb.write(lore, {"entry": "Vesa", "kind": "x"}, 11)  # nothing changed: all-or-nothing
    with pytest.raises(Refused, match="say which entry"):
        nb.write(lore, {"description": "x"}, 11)
    with pytest.raises(Refused, match="nothing to write"):
        nb.write(lore, {}, 11)


def test_rename_and_merge() -> None:
    lore = book()
    lore, text = nb.write(lore, {"entry": "Vessa", "rename": "Vessa Thorne"}, 6)
    assert nb.find(lore, "vessa") == "Vessa Thorne" and lore["relationships"][0]["from"] == "Vessa Thorne"
    lore, _ = nb.write(lore, {"create": "Old Ma", "kind": "person", "description": "A crone.",
                              "relationships": ["sells to [[Captain Orm]]"]}, 7)
    lore, text = nb.write(lore, {"merge": "Old Ma", "into": "the Fence"}, 8)
    assert "Old Ma merged into Vessa Thorne" in text and nb.find(lore, "old ma") == "Vessa Thorne"
    e = lore["entries"]["Vessa Thorne"]
    assert [p["text"] for p in e["description"]] == ["Half-elf, fifties.", "A crone."]
    assert lore["relationships"][-1]["from"] == "Vessa Thorne"


def test_look_entry_orders_by_relevance() -> None:
    lore = book()
    t = said(("hi", "Hello."), ("look", "A tavern."), ("x", "y"), ("I ask about Brakka's debt", "Hm."))
    text = nb.look(lore, ["the guild"], t)
    assert text.startswith("Thieves Guild (group; also: the Guild)\nDescription:\n(t2) Millbrook's thieves.")
    assert "Not mentioned in play yet" in text
    # both relationships mention the Guild: Orm's ("the Guild's bribes", a plain name) and Vessa's (a link)
    assert text.endswith("• [2] Captain Orm: takes the Guild's bribes (t4)\n"
                         "• [1] Vessa: runs the [[Thieves Guild]] from the back of the [[Copper Kettle]] (t2)")
    text = nb.look(lore, ["Vessa"], t)
    assert "Not mentioned in play yet" in text  # Vessa never came up in play
    assert text.splitlines()[-2] == "• [3] Vessa: owes [[Brakka]] a favour (t5) (came up just now)"
    # the Copper Kettle came up in the last turn: that bullet goes first, though it's older
    t2 = said(("hi", "Hello."), ("I ask at the Copper Kettle", "The barman shrugs."))
    lines = nb.look(lore, ["Vessa"], t2).splitlines()
    assert lines[-2].startswith("• [1] Vessa: runs the") and lines[-2].endswith("(came up just now)")
    assert lines[-1] == "• [3] Vessa: owes [[Brakka]] a favour (t5)"


def test_last_mentioned_and_pages() -> None:
    lore = book()
    for i in range(12):
        lore, _ = nb.write(lore, {"entry": "Copper Kettle", "add_relationships": [f"fact {i}"]}, 6)
    t = said(("I go to the kettle", "The Copper Kettle is loud."), ("I sit", "You sit."))
    text = nb.look(lore, ["Copper Kettle"], t)
    assert "Last mentioned in play: turn 1" in text and text.endswith("…and 3 more (page 2)")
    assert len(nb.look(lore, ["Copper Kettle"], t, page=2).split("•")) == 4


def test_connections() -> None:
    lore = book()
    text = nb.look(lore, ["Vessa", "Captain Orm"], [])
    assert text == ("Vessa ↔ Captain Orm\nDirectly: nothing recorded\nThrough one other entry:\n"
                    "• via Thieves Guild: [1] Vessa: runs the [[Thieves Guild]] from the back of the [[Copper Kettle]] (t2)"
                    " / [2] Captain Orm: takes the Guild's bribes (t4)")
    text = nb.look(lore, ["Vessa", "Copper Kettle"], [])
    assert "Directly:\n• [1] Vessa: runs the" in text
    lore, _ = nb.write(lore, {"entry": "Brakka", "add_to_description": "Drinks with Captain Orm."}, 6)
    assert "• Brakka (description): Drinks with Captain Orm. (t6)" in nb.look(lore, ["Brakka", "Captain Orm"], [])
    with pytest.raises(Refused, match="same entry"):
        nb.look(lore, ["Vessa", "the Fence"], [])


def test_recall() -> None:
    lore = book()
    t = said(("I ask the Fence about the key", "Vessa smiles. 'The silver key? Gone.'"),
             ("And the Guild?", "She shrugs."),
             ("I ask about the Guild and Vessa", "'Vessa and the Guild are old friends.'"))
    text = nb.recall(lore, t, ["Vessa"])
    assert text.splitlines()[0] == "4 mentions of 'Vessa', newest first:"
    assert text.splitlines()[1] == "turn 3, DM: 'Vessa and the Guild are old friends.'"
    assert text.splitlines()[-1] == "turn 1, player: I ask the Fence about the key"  # an other name counts
    text = nb.recall(lore, t, ["Vessa", "Thieves Guild"])
    assert text.splitlines()[0] == "2 mentions of 'Vessa' and 'Thieves Guild' in the same turn, newest first:"
    assert nb.recall(lore, t, ["silver key"]).endswith("turn 1, DM: Vessa smiles. 'The silver key? Gone.'")
    assert nb.recall(lore, t, ["gold key"]) == "no mentions of 'gold key'"
    assert nb.recall(lore, t, turn=2) == "Turn 2:\nPlayer: And the Guild?\nDM: She shrugs."
    with pytest.raises(Refused, match="turns run from 0 to 3"):
        nb.recall(lore, t, turn=9)


def test_notes_each_turn() -> None:
    lore = book()
    t = said(("hi", "Hello."), ("I go to the Copper Kettle", "Smoke and noise."))
    lore, text = nb.notes(lore, t)
    assert text == ("[Turn 2]\n[Notebook: names from the last turns]\n"
                    "Copper Kettle (place): A tavern by the river.\n"
                    "Thieves Guild (group): Millbrook's thieves. ← linked from Copper Kettle\n"
                    "Vessa (person): Half-elf, fifties. ← linked from Copper Kettle\n" + nb.REMINDER)
    t += [{"kind": "player", "text": "I order an ale at the Kettle... the Copper Kettle"}]
    lore, text = nb.notes(lore, t)
    assert text == "[Turn 3]\n" + nb.REMINDER  # shown last turn: skipped
    t += [{"kind": "dm", "text": "x"}, {"kind": "player", "text": "y"}, {"kind": "dm", "text": "z"},
          {"kind": "player", "text": "Copper Kettle again"}, {"kind": "dm", "text": "z"},
          {"kind": "player", "text": "Copper Kettle again"}]
    lore, text = nb.notes(lore, t)
    assert "[Turn 6]" in text and "Copper Kettle (place)" in text  # 4 turns later: shown again
    assert nb.notes(nb.new(), [])[1] == "[Turn 0]\n" + nb.REMINDER


def test_matching_names() -> None:
    """Capitals count on a name's main words, not on small joining words; the longest name wins (owner, 2026-10-13)."""
    lore = nb.new()
    for a in ({"create": "Lamp", "kind": "creature", "description": "Tull's dog."},
              {"create": "Anvil", "kind": "creature", "description": "The mule."},
              {"create": "Anvil Father", "kind": "god", "description": "The dwarves' god."},
              {"create": "The Butcher of Blackshire", "kind": "person", "description": "A killer."}):
        lore, _ = nb.write(lore, a, 1)
    assert nb.mentioned(lore, "She lit the lamp.") == []
    assert nb.mentioned(lore, "Lamp barks. LAMP! Lamp's tail wags.") == ["Lamp"]
    assert nb.mentioned(lore, "They prayed to the Anvil Father.") == ["Anvil Father"]  # not the mule as well
    assert nb.mentioned(lore, "Anvil brays at the Anvil Father's shrine.") == ["Anvil", "Anvil Father"]
    assert nb.mentioned(lore, "Fear the butcher of Blackshire") == []  # "butcher" is a main word
    assert nb.mentioned(lore, "they fear the Butcher of Blackshire") == ["The Butcher of Blackshire"]
    t = said(("I light a lamp", "The lamp flickers."), ("I pat Lamp", "Lamp licks your hand."))
    assert nb.recall(lore, t, ["Lamp"]).splitlines()[0] == "2 mentions of 'Lamp', newest first:"  # the dog
    assert nb.recall(lore, t, ["flickers"]).endswith("turn 1, DM: The lamp flickers.")  # a keyword: any capitals
    assert "Last mentioned in play: turn 2" in nb.look(lore, ["Lamp"], t)
    t2 = said(("hi", "The Anvil Father watches."))
    assert "Not mentioned in play yet" in nb.look(lore, ["Anvil"], t2)


def test_game_tools_hidden(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """In play: the tools work on the save's notebook, nothing is printed for the player, and it's saved."""
    g = play.Game({"sheet": json.loads((CHAR / "fighter.json").read_text(encoding="utf-8"))}, tmp_path / "save.json")
    g.transcript += [{"kind": "player", "text": "hello"}]
    tools = {t.name: t.handler for t in g.tools()}

    def call(name: str, **args: object) -> tuple[str, bool]:
        res = asyncio.run(tools[name](args))
        return res["content"][0]["text"], bool(res.get("is_error"))
    assert call("write_lore", create="Vessa", kind="person", description="Half-elf.") == (
        "entry Vessa (person) created", False)
    assert call("lore", names=["Vessa"])[0].startswith("Vessa (person)\nDescription:\n(t1) Half-elf.")
    assert call("recall", search=["hello"])[0].endswith("turn 1, player: hello")
    assert call("write_lore", create="Vessa", kind="person", description="x")[1]
    assert capsys.readouterr().out == ""  # the player sees none of it
    data = json.loads((tmp_path / "save.json").read_text(encoding="utf-8"))
    assert list(data["lore"]["entries"]) == ["Vessa"]
    assert data["transcript"][1] == {"kind": "call", "tool": "write_lore", "input": {
        "create": "Vessa", "kind": "person", "description": "Half-elf."}, "result": "entry Vessa (person) created",
        "error": False}
    assert play.Game(data, tmp_path / "save.json").lore == g.lore
    assert "Vessa" not in play.sheet_report(g) and "Vessa" not in play.history(data)
