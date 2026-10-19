"""Creatures' turns run by code (dm/fight.py): attacks and damage from the stat block, the stops where a party member
can react or a hit does more than damage, and going on from a stop."""
import json
import random
from pathlib import Path
from typing import Any

import pytest

from dm import fight, play
from dm import mechanics as m

CHAR = Path(__file__).parent.parent / "dm" / "characters"


class Dice:
    """random.Random stand-in: each randint gives the next scripted number."""

    def __init__(self, rolls: list[int]) -> None:
        self.rolls = rolls

    def randint(self, a: int, b: int) -> int:
        v = self.rolls.pop(0)
        assert a <= v <= b, (v, a, b)
        return v


def game(tmp_path: Path, monkeypatch: Any, who: str, rolls: list[int], foes: list[tuple[str, str, int]]) -> play.Game:
    """A game with `who` (a sample character) as the PC, in a fight with foes (name, monster, initiative) after it."""
    g = play.Game({"sheet": json.loads((CHAR / f"{who}.json").read_text(encoding="utf-8"))}, tmp_path / "save.json")
    dice = Dice(rolls)
    monkeypatch.setattr(random, "Random", lambda: dice)
    g.fight, _ = m.add_combatants(None, g.sheet["name"], [{"name": "pc", "initiative": 20}] + [
        {"name": n, "monster": mon, "initiative": i, "hp": 7, "ac": 15} for n, mon, i in foes])
    g.fight, _ = m.next_turn(g.fight)  # the PC's turn, now over
    g.dice = dice
    return g


def turns(g: play.Game, a: dict[str, Any]) -> str:
    return fight.Turns(g, a).run()


def test_two_goblins_then_the_pc(tmp_path: Path, monkeypatch: Any) -> None:
    g = game(tmp_path, monkeypatch, "fighter", [15, 3, 2], [("Goblin 1", "Goblin", 15), ("Goblin 2", "Goblin", 12)])
    pc = g.sheet["name"]
    out = turns(g, {"turns": [{"name": "Goblin 1", "attacks": [{"attack": "Scimitar", "target": pc}]},
                              {"name": "Goblin 2", "attacks": [{"attack": "Scimitar", "target": pc}]}]})
    assert g.sheet["hp"]["current"] == 14 - 5  # 1d6+2 = 3+2
    assert "a miss" in out and g.fight["order"][g.fight["turn"]]["name"] == "Goblin 2" and "start it with next_turn" in out
    assert "STOPPED" not in out and not g.dice.rolls
    shown = [e["text"] for e in g.transcript if e["kind"] == "tool"]
    assert any(t.startswith("dice Goblin 1's Scimitar at") for t in shown) and shown[-1].endswith("a miss")


def test_out_of_order_is_refused_and_nothing_changes(tmp_path: Path, monkeypatch: Any) -> None:
    g = game(tmp_path, monkeypatch, "fighter", [], [("Goblin 1", "Goblin", 15), ("Goblin 2", "Goblin", 12)])
    with pytest.raises(m.Refused, match="Goblin 1's turn comes next"):
        turns(g, {"turns": [{"name": "Goblin 2", "attacks": [{"attack": "Scimitar", "target": g.sheet["name"]}]}]})
    with pytest.raises(m.Refused, match="no attack 'Bite'"):
        turns(g, {"turns": [{"name": "Goblin 1", "attacks": [{"attack": "Bite", "target": g.sheet["name"]}]}]})
    assert g.fight["turn"] == 0 and g.sheet["hp"]["current"] == 14


def test_shield_stops_and_goes_on(tmp_path: Path, monkeypatch: Any) -> None:
    """A hit that Shield could turn into a miss stops before the damage; Shield cast, the attack misses."""
    g = game(tmp_path, monkeypatch, "wizard", [10, 9], [("Goblin 1", "Goblin", 15), ("Goblin 2", "Goblin", 12)])
    pc = g.sheet["name"]
    out = turns(g, {"turns": [{"name": "Goblin 1", "attacks": [{"attack": "Scimitar", "target": pc}]},
                              {"name": "Goblin 2", "attacks": [{"attack": "Scimitar", "target": pc}]}]})
    assert "STOPPED for a reaction" in out and "Shield" in out and "Ask the player" in out
    assert g.sheet["hp"]["current"] == 8 and g.fight["pending"]["name"] == "Goblin 1"
    assert "STOPPED" in m.fight_text(g.fight, g.sheet)
    with pytest.raises(m.Refused, match="with resume"):
        turns(g, {"turns": [{"name": "Goblin 2", "attacks": [{"attack": "Scimitar", "target": pc}]}]})
    g.sheet["ac_now"] = {"value": 16, "reason": "Shield"}  # what change_pc cast Shield with ac_set records
    g.fight, _ = m.use(g.fight, "reaction", pc)
    out = turns(g, {"resume": {}})  # Goblin 2's turn, as sent, goes on by itself
    assert "now a miss against AC 16" in out and "a miss" in out and g.sheet["hp"]["current"] == 8
    assert "pending" not in g.fight and g.fight["order"][g.fight["turn"]]["name"] != pc


def test_no_stop_when_shield_cant_matter(tmp_path: Path, monkeypatch: Any) -> None:
    g = game(tmp_path, monkeypatch, "wizard", [20, 2, 3], [("Goblin 1", "Goblin", 15)])  # a natural 20
    out = turns(g, {"turns": [{"name": "Goblin 1", "attacks": [{"attack": "Scimitar", "target": g.sheet["name"]}]}]})
    assert "STOPPED" not in out and "critical hit" in out and g.sheet["hp"]["current"] == 8 - 7  # 2d6+2 = 2+3+2


def test_rider_stops_after_the_damage(tmp_path: Path, monkeypatch: Any) -> None:
    g = game(tmp_path, monkeypatch, "fighter", [19, 2, 2], [("Wolf", "Wolf", 15)])
    out = turns(g, {"turns": [{"name": "Wolf", "attacks": [{"attack": "Bite", "target": g.sheet["name"]}]}]})
    assert "STOPPED: Wolf's Bite hit" in out and "prone" in out and g.sheet["hp"]["current"] == 14 - 6
    out = turns(g, {"resume": {}})
    assert "pending" not in g.fight and "start it with next_turn" in out


def test_opportunity_attack_stop(tmp_path: Path, monkeypatch: Any) -> None:
    g = game(tmp_path, monkeypatch, "fighter", [], [("Goblin 1", "Goblin", 15)])
    pc = g.sheet["name"]
    out = turns(g, {"turns": [{"name": "Goblin 1", "leaves_reach_of": [pc], "note": "runs for the door"}]})
    assert "Opportunity Attack" in out and g.fight["pending"]["name"] == "Goblin 1"
    g.fight, _ = m.change_creature(g.fight, {"name": "Goblin 1", "remove": True})  # the attack killed it
    out = turns(g, {"resume": {}})
    assert "pending" not in g.fight
    # its reaction used: no stop
    g2 = game(tmp_path, monkeypatch, "fighter", [], [("Goblin 1", "Goblin", 15)])
    g2.fight, _ = m.use(g2.fight, "reaction", pc)
    assert "STOPPED" not in turns(g2, {"turns": [{"name": "Goblin 1", "leaves_reach_of": [pc]}]})


def test_melee_hit_on_an_unconscious_pc_is_a_critical(tmp_path: Path, monkeypatch: Any) -> None:
    g = game(tmp_path, monkeypatch, "fighter", [15, 1, 1], [("Goblin 1", "Goblin", 15)])
    g.sheet["hp"]["current"] = 0
    g.sheet["conditions"] = ["unconscious"]
    out = turns(g, {"turns": [{"name": "Goblin 1", "attacks": [{"attack": "Scimitar", "target": g.sheet["name"]}]}]})
    assert "2d6+2" in out and g.sheet["death_saves"]["failures"] == 2


def test_dropping_the_pc_goes_on_unless_a_turn_aims_at_them(tmp_path: Path, monkeypatch: Any) -> None:
    """Goblin 1 drops the PC; Goblin 2 was sent at the PC, so the code stops before its turn for the DM to decide it
    again. A turn aimed elsewhere would have gone on."""
    g = game(tmp_path, monkeypatch, "wizard", [19, 1], [("Goblin 1", "Goblin", 15), ("Goblin 2", "Goblin", 12)])
    pc = g.sheet["name"]
    g.sheet["hp"]["current"] = 3
    g.sheet["spell_slots"]["1"]["left"] = 0  # no Shield
    out = turns(g, {"turns": [{"name": "Goblin 1", "attacks": [{"attack": "Scimitar", "target": pc}]},
                              {"name": "Goblin 2", "attacks": [{"attack": "Scimitar", "target": pc}]}]})
    assert "STOPPED before Goblin 2's turn" in out and "dropped to 0 HP" in out and g.sheet["hp"]["current"] == 0
    assert g.fight["order"][g.fight["turn"]]["name"] == "Goblin 1"
    assert "STOPPED before" in turns(g, {"resume": {}})  # still the same
    out = turns(g, {"resume": {}, "turns": [{"name": "Goblin 2", "note": "loots the body"}]})
    assert "pending" not in g.fight and g.fight["order"][g.fight["turn"]]["name"] != pc


def test_an_already_downed_target_is_no_change(tmp_path: Path, monkeypatch: Any) -> None:
    g = game(tmp_path, monkeypatch, "fighter", [2, 2], [("Goblin 1", "Goblin", 15), ("Goblin 2", "Goblin", 12)])
    pc = g.sheet["name"]
    g.sheet["hp"]["current"], g.sheet["conditions"] = 0, ["unconscious"]
    out = turns(g, {"turns": [{"name": "Goblin 1", "attacks": [{"attack": "Scimitar", "target": pc}]},
                              {"name": "Goblin 2", "attacks": [{"attack": "Scimitar", "target": pc}]}]})
    assert "STOPPED" not in out


def test_creature_without_stat_block_is_refused(tmp_path: Path, monkeypatch: Any) -> None:
    g = game(tmp_path, monkeypatch, "fighter", [], [])
    g.fight, _ = m.add_combatants(g.fight, g.sheet["name"], [{"name": "Thing", "initiative": 5, "hp": 9, "ac": 12}])
    with pytest.raises(m.Refused, match="no SRD stat block"):
        turns(g, {"turns": [{"name": "Thing", "attacks": [{"attack": "Claw", "target": g.sheet["name"]}]}]})
    with pytest.raises(m.Refused, match="no SRD monster"):
        m.add_combatants(g.fight, g.sheet["name"], [{"name": "X", "initiative": 5, "hp": 9, "ac": 12, "monster": "Beholder"}])


def test_reactions_of_sheets() -> None:
    wiz = json.loads((CHAR / "wizard.json").read_text(encoding="utf-8"))
    assert "Shield" in fight.reactions_of(wiz)
    wiz["spell_slots"]["1"]["left"] = 0
    assert "Shield" not in fight.reactions_of(wiz)
    assert fight.crit_dice("2d4+1d6+2") == "4d4+2d6+2"
    assert fight.rider("Melee Weapon Attack: +4 to hit. Hit: 5 (1d6 + 2) slashing damage.") == ""


def test_target_names_and_a_choice_of_damage(tmp_path: Path, monkeypatch: Any) -> None:
    """'pc' is the PC; a versatile weapon is one-handed unless damage is passed; another choice is the DM's."""
    g = game(tmp_path, monkeypatch, "fighter", [19, 5, 19, 5], [("Drider", "Drider", 15), ("Djinni", "Djinni", 12)])
    turns(g, {"turns": [{"name": "Drider", "attacks": [{"attack": "Longsword", "target": "pc"}]}]})
    assert g.sheet["hp"]["current"] == 14 - 8  # 1d8+3
    with pytest.raises(m.Refused, match="choice of damage"):
        turns(g, {"turns": [{"name": "Djinni", "attacks": [{"attack": "Scimitar", "target": "pc"}]}]})
