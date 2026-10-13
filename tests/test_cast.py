"""Casting a spell with change_pc cast: the slot, the duration's timer, concentration, and the damage reminder."""
import asyncio
import json
from pathlib import Path

from dm import mechanics as m
from dm import play

CHAR = Path(__file__).parent.parent / "dm" / "characters"


def game(tmp_path: Path, timed: bool = True) -> tuple[play.Game, object]:
    sheet = json.loads((CHAR / "wizard.json").read_text(encoding="utf-8"))  # Wren: 2 level-1 slots
    sc = sheet["spellcasting"]
    sc["spellbook"] += ["Hold Person"]
    sc["prepared"] += ["Hold Person", "Witch Bolt"]  # two concentration spells (Witch Bolt: just for the test)
    sc["known"] = ["Hunter's Mark"]  # its higher-level text changes the duration
    sheet["spell_slots"]["2"] = {"max": 1, "left": 1, "recharge": "long"}
    sheet["spell_slots"]["3"] = {"max": 1, "left": 1, "recharge": "long"}
    g = play.Game({"sheet": sheet}, tmp_path / "save.json")
    tools = {t.name: t.handler for t in g.tools()}

    def call(name: str, **args: object) -> tuple[str, bool]:
        res = asyncio.run(tools[name](args))
        return res["content"][0]["text"], bool(res.get("is_error"))
    if timed:
        call("change_time", set={"day": 1, "time": "10:00"})
    return g, call


def test_cast_spends_and_times(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    text, err = call("change_pc", cast="Mage Armor", level=1, ac_set=13, ac_reason="Mage Armor: 13 + DEX")
    assert not err and text.startswith("Wren casts Mage Armor at level 1; timer Wren's Mage Armor: 8 hours; ")
    assert "level-1 spell slots: 1/2" in text and "AC now 13" in text
    assert call("change_pc", cast="Fire Bolt") == ("Wren casts Fire Bolt", False)  # a cantrip: nothing else changes
    assert g.sheet["spell_slots"]["1"]["left"] == 1
    assert call("change_pc", cast="Shield", level=1)[0].endswith("timer Wren's Shield: 6 seconds; level-1 spell slots: 0/2")
    assert "no level-1 spell slots left" in call("change_pc", cast="Magic Missile", level=1)[0]
    assert "Wren's Shield" in g.clock["timers"] and len(g.clock["timers"]) == 2  # the refused cast left no timer


def test_refusals(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    assert "a cantrip: leave out level" in call("change_pc", cast="Fire Bolt", level=1)[0]
    assert "which spell slot Magic Missile is cast with" in call("change_pc", cast="Magic Missile")[0]
    assert "not among their spells" in call("change_pc", cast="Fireball", level=3)[0]
    assert "only as a ritual" in call("change_pc", cast="Detect Magic", level=1)[0]  # in the book, not prepared
    assert "level: the slot level, 2 (Hold Person's level) to 9" in call("change_pc", cast="Hold Person", level=1)[0]
    assert "a rest is a call of its own" in call("change_pc", cast="Fire Bolt", long_rest=True)[0]
    assert "go with cast" in call("change_pc", level=1)[0]
    assert call("change_pc", cast="Magic Missile", level=1, items_lost=[{"item": "Nothing"}])[1]
    assert g.sheet["spell_slots"]["1"]["left"] == 2  # all-or-nothing
    _, untimed = game(tmp_path, timed=False)
    assert "the time isn't set yet" in untimed("change_pc", cast="Mage Armor", level=1)[0]
    assert untimed("change_pc", cast="Magic Missile", level=1)[0].startswith("Wren casts Magic Missile")  # no timer needed


def test_ritual_and_no_slot(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    text = call("change_pc", cast="Detect Magic", ritual=True)[0]
    assert text.startswith("Wren casts Detect Magic as a ritual: no spell slot, and it takes 10 minutes longer")
    assert "Wren's Detect Magic (concentration)" in g.clock["timers"] and g.sheet["spell_slots"]["1"]["left"] == 2
    assert "isn't a ritual spell" in call("change_pc", cast="Sleep", ritual=True)[0]
    text = call("change_pc", cast="Fireball", level=3, no_slot="spell scroll")[0]
    assert text == "Wren casts Fireball at level 3 without a spell slot (spell scroll)"
    assert g.sheet["spell_slots"]["3"]["left"] == 1


def test_concentration(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    call("change_pc", cast="Detect Magic", ritual=True)
    text = call("change_pc", cast="Hold Person", level=2)[0]
    assert "Wren stops concentrating on Detect Magic (concentrating on Hold Person instead)" in text
    assert list(g.clock["timers"]) == ["Wren's Hold Person (concentration)"]
    assert "Timers: Wren's Hold Person (concentration): 1 minute left" in g.status()  # shown every turn
    text = call("change_pc", damage=3)[0]
    assert text.endswith("Wren is concentrating on Hold Person: Constitution saving throw, DC 10 (10 or half the damage, "
                         "whichever is higher); on a failure the spell ends (remove its timer)")
    call("change_pc", temp_hp=20)
    assert "DC 11" in call("change_pc", damage=22)[0]  # half of all the damage, temporary HP or not
    assert call("change_pc", damage=10)[0].endswith("Wren stops concentrating on Hold Person (unconscious)")
    assert "unconscious" in g.sheet["conditions"] and not g.clock["timers"]  # 0 HP: unconscious ends it


def test_incapacitated_and_run_out(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    call("change_pc", cast="Hold Person", level=2)
    assert call("change_pc", conditions_added=["prone"])[0] == "condition added: prone"  # not incapacitating
    text = call("change_pc", conditions_added=["stunned"])[0]
    assert text.endswith("Wren stops concentrating on Hold Person (stunned)") and not g.clock["timers"]
    call("change_pc", conditions_removed=["stunned"])
    call("change_pc", cast="Witch Bolt", level=1)
    call("change_time", advance={"minutes": 2})
    assert "Constitution" not in call("change_pc", damage=1)[0]  # the timer ran out: no longer concentrating
    assert m.incapacitating() == {"incapacitated", "paralyzed", "petrified", "stunned", "unconscious"}


def test_higher_level_duration(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    assert "timer Wren's Hunter's Mark (concentration): 1 hour;" in call("change_pc", cast="Hunter's Mark", level=1)[0]
    g, call = game(tmp_path)
    text, err = call("change_pc", cast="Hunter's Mark", level=3)
    assert err and "may change how long it lasts" in text and "Pass duration" in text
    assert call("change_pc", cast="Hunter's Mark", level=3, duration={"hours": 8, "concentration": True})[0].endswith(
        "timer Wren's Hunter's Mark (concentration): 8 hours; level-3 spell slots: 0/1")
    # Major Image with a 6th-level slot: "lasts until dispelled, without requiring your concentration"
    g.sheet["spellcasting"]["prepared"].append("Major Image")
    g.sheet["spell_slots"]["6"] = {"max": 1, "left": 1, "recharge": "long"}
    text = call("change_pc", cast="Major Image", level=6, duration={})[0]
    assert "lasts until dispelled or ended: no timer" in text and "stops concentrating" not in text
    assert "Wren's Hunter's Mark (concentration)" in g.clock["timers"]  # still concentrating on it
    assert "only for a spell cast at a higher level" in call("change_pc", cast="Mage Armor", level=1,
                                                             duration={"hours": 1})[0]


def test_companion_casts(tmp_path: Path) -> None:
    """The caster is `who`; their name keeps their timers apart."""
    g, call = game(tmp_path)
    g.companions.append(json.loads(json.dumps(g.sheet)) | {"name": "Dunmar Stone"})
    text = call("change_pc", who="Dunmar", cast="Hold Person", level=2)[0]
    assert text.startswith("Dunmar casts Hold Person at level 2; timer Dunmar's Hold Person (concentration): 1 minute; "
                           "Dunmar Stone: level-2 spell slots: 0/1")
    assert g.sheet["spell_slots"]["2"]["left"] == 1
    assert "Dunmar is concentrating on Hold Person" in call("change_pc", who="Dunmar", damage=2)[0]
    assert "concentrating" not in call("change_pc", damage=2)[0]
