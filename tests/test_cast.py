"""Casting a spell with change_pc cast: the slot, the casting time, the duration's timer, concentration, and the
reminders. The code starts things; it ends nothing: the DM does, with concentration_end and change_time."""
import asyncio
import json
import re
from pathlib import Path

from dm import mechanics as m
from dm import play, srd

CHAR = Path(__file__).parent.parent / "dm" / "characters"


def game(tmp_path: Path, timed: bool = True) -> tuple[play.Game, object]:
    sheet = json.loads((CHAR / "wizard.json").read_text(encoding="utf-8"))  # Wren: 2 level-1 slots
    sc = sheet["spellcasting"]
    sc["spellbook"] += ["Hold Person", "Identify"]
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
    assert len(g.clock["timers"]) == 2  # the refused cast left no timer


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


def test_ritual_casting_time_and_no_slot(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    text = call("change_pc", cast="Detect Magic", ritual=True)[0]
    assert text.startswith("Wren casts Detect Magic as a ritual: no spell slot, 10 minutes longer than its casting time "
                           "(1 action); the casting took 10 minutes: now Day 1, 10:10 AM; timer Wren's Detect Magic: "
                           "10 minutes; concentrating on Detect Magic")
    assert g.clock["timers"]["Wren's Detect Magic"] == g.clock["now"] + 600  # the timer starts once the casting is done
    assert g.sheet["spell_slots"]["1"]["left"] == 2
    text = call("change_pc", cast="Identify", ritual=True)[0]  # 1 minute casting time + 10
    assert "the casting took 11 minutes: now Day 1, 10:21 AM" in text
    assert "isn't a ritual spell" in call("change_pc", cast="Sleep", ritual=True)[0]
    text = call("change_pc", cast="Fireball", level=3, no_slot="spell scroll")[0]
    assert text == "Wren casts Fireball at level 3 without a spell slot (spell scroll)"
    assert g.sheet["spell_slots"]["3"]["left"] == 1


def test_concentration_is_reminded_not_ended(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    call("change_pc", cast="Detect Magic", ritual=True)
    text = call("change_pc", cast="Hold Person", level=2)[0]
    assert "concentration on Detect Magic ends: a new concentration spell ends it (remove its timer" in text
    assert g.sheet["concentration"] == "Hold Person"
    assert set(g.clock["timers"]) == {"Wren's Detect Magic", "Wren's Hold Person"}  # the DM removes timers
    assert "Concentrating on: Hold Person" in g.status()  # shown every turn
    text = call("change_pc", damage=3)[0]
    assert text.endswith("Wren is concentrating on Hold Person: Constitution saving throw, DC 10 (10 or half the damage, "
                         "whichever is higher); on a failure, end it with concentration_end (and remove the spell's timer)")
    call("change_pc", temp_hp=20)
    assert "DC 11" in call("change_pc", damage=22)[0]  # half of all the damage, temporary HP or not
    text = call("change_pc", damage=10)[0]
    assert text.endswith("Wren is unconscious while concentrating on Hold Person: being incapacitated or killed ends "
                         "concentration. End it with concentration_end (and remove the spell's timer)")
    assert g.sheet["concentration"] == "Hold Person"  # still: the DM ends it
    assert call("change_pc", concentration_end=True)[0].startswith("concentration on Hold Person ends")
    assert "concentration" not in g.sheet and "Wren's Hold Person" in g.clock["timers"]
    assert "isn't concentrating" in call("change_pc", concentration_end=True)[0]


def test_conditions_and_manual_concentration(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    assert call("change_pc", concentration_start="Bless") == ("concentrating on Bless", False)  # no timer, no slot
    assert not g.clock["timers"]
    assert "doesn't need concentration" in call("change_pc", concentration_start="Mage Armor")[0]
    assert call("change_pc", conditions_added=["prone"])[0] == "condition added: prone"  # not incapacitating
    assert "stunned while concentrating on Bless" in call("change_pc", conditions_added=["stunned"])[0]
    assert "leave out spend_slot, concentration_start" in call("change_pc", cast="Witch Bolt", level=1,
                                                               concentration_start="Bless")[0]
    assert m.incapacitating() == {"incapacitated", "paralyzed", "petrified", "stunned", "unconscious"}


def test_higher_level_duration(tmp_path: Path) -> None:
    g, call = game(tmp_path)
    assert "timer Wren's Hunter's Mark: 1 hour;" in call("change_pc", cast="Hunter's Mark", level=1)[0]
    text = call("change_pc", cast="Hunter's Mark", level=3)[0]
    assert "with a level-3 slot it lasts: up to 8 hours; timer Wren's Hunter's Mark: 8 hours" in text
    # Major Image with a 6th-level slot: "lasts until dispelled, without requiring your concentration"
    g.sheet["spellcasting"]["prepared"].append("Major Image")
    g.sheet["spell_slots"]["6"] = {"max": 1, "left": 1, "recharge": "long"}
    text = call("change_pc", cast="Major Image", level=6)[0]
    assert "lasts until dispelled: no timer" in text and "concentrat" not in text
    assert g.sheet["concentration"] == "Hunter's Mark"


def test_higher_duration_table_matches_the_srd() -> None:
    """HIGHER_DURATION is typed in; each entry is pinned here to the spell's own higher-level text."""
    said = {s["name"]: " ".join(s.get("higher_level", [])) for s in srd.table("Spells").values()}
    assert set(m.HIGHER_DURATION) == {n for n, h in said.items() if re.search(r"duration|lasts|concentration", h)}
    pins = {
        "Animal Messenger": ["increases by 48 hours for each slot level above 2nd"],
        "Bestow Curse": ["4th level or higher, the duration is concentration, up to 10 minutes",
                         "5th level or higher, the duration is 8 hours", "7th level or higher, the duration is 24 hours",
                         "9th level spell slot, the spell lasts until it is dispelled"],
        "Dominate Beast": ["5th-level spell slot, the duration is concentration, up to 10 minutes",
                           "6th-level spell slot, the duration is concentration, up to 1 hour",
                           "7th level or higher, the duration is concentration, up to 8 hours"],
        "Dominate Monster": ["9th-level spell slot, the duration is concentration, up to 8 hours"],
        "Dominate Person": ["6th-level spell slot, the duration is concentration, up to 10 minutes",
                            "7th-level spell slot, the duration is concentration, up to 1 hour",
                            "8th level or higher, the duration is concentration, up to 8 hours"],
        "Geas": ["7th or 8th level, the duration is 1 year", "9th level, the spell lasts until it is ended"],
        "Hunter's Mark": ["3rd or 4th level, you can maintain your concentration on the spell for up to 8 hours",
                          "5th level or higher, you can maintain your concentration on the spell for up to 24 hours"],
        "Magic Circle": ["increases by 1 hour for each slot level above 3rd"],
        "Major Image": ["6th level or higher, the spell lasts until dispelled, without requiring your concentration"],
        "Mass Suggestion": ["7th-level spell slot, the duration is 10 days", "8th-level spell slot, the duration is 30 days",
                            "9th-level spell slot, the duration is a year and a day"],
        "Planar Binding": ["10 days with a 6th-level slot", "30 days with a 7th-level slot", "180 days with an 8th-level slot",
                           "a year and a day with a 9th-level spell slot"],
    }
    for name, phrases in pins.items():
        for p in phrases:
            assert p in said[name], (name, p)
    t = m.HIGHER_DURATION
    assert t["Animal Messenger"][3] == "72 hours" and t["Magic Circle"][4] == "2 hours" and t["Magic Circle"][9] == "7 hours"
    assert t["Bestow Curse"][4].startswith("Up to") and not t["Bestow Curse"][5].startswith("Up to")


def test_companion_casts(tmp_path: Path) -> None:
    """The caster is `who`: their slot, their timer, their concentration."""
    g, call = game(tmp_path)
    g.companions.append(json.loads(json.dumps(g.sheet)) | {"name": "Dunmar Stone"})
    text = call("change_pc", who="Dunmar", cast="Hold Person", level=2)[0]
    assert text == ("Dunmar casts Hold Person at level 2; timer Dunmar's Hold Person: 1 minute; "
                    "Dunmar Stone: level-2 spell slots: 0/1; concentrating on Hold Person")
    assert g.sheet["spell_slots"]["2"]["left"] == 1 and "concentration" not in g.sheet
    assert "Dunmar is concentrating on Hold Person" in call("change_pc", who="Dunmar", damage=2)[0]
    assert "concentrating" not in call("change_pc", damage=2)[0]
