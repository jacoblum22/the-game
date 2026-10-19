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


def sheet(who: str) -> dict[str, Any]:
    return json.loads((CHAR / f"{who}.json").read_text(encoding="utf-8"))


def game(tmp_path: Path, monkeypatch: Any, who: str, rolls: list[int], foes: list[tuple[str, str, int]],
         mates: list[tuple[str, int]] = ()) -> play.Game:  # type: ignore[assignment]
    """A game with `who` (a sample character) as the PC, in a fight with foes (name, monster, initiative) and
    companions (a sample character, initiative) after it."""
    g = play.Game({"sheet": sheet(who), "companions": [sheet(w) | {"companion": True} for w, _ in mates]},
                  tmp_path / "save.json")
    dice = Dice(rolls)
    monkeypatch.setattr(random, "Random", lambda: dice)
    g.fight, _ = m.add_combatants(None, g.sheet["name"], [{"name": "pc", "initiative": 20}] + [
        {"name": n, "monster": mon, "initiative": i, "hp": 7, "ac": 15} for n, mon, i in foes] + [
        {"name": c["name"], "initiative": i} for c, (_, i) in zip(g.companions, mates)],
        companions=tuple(c["name"] for c in g.companions))
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


def test_a_dropped_target_falls_to_the_next(tmp_path: Path, monkeypatch: Any) -> None:
    """Goblin 1 drops the PC. Goblin 2 was sent at the PC, or else the companion: it attacks the companion. Goblin 3,
    with no one else named, doesn't attack. No stop."""
    g = game(tmp_path, monkeypatch, "wizard", [19, 1, 2], [("Goblin 1", "Goblin", 15), ("Goblin 2", "Goblin", 12),
                                                          ("Goblin 3", "Goblin", 11)], mates=[("rogue", 2)])
    pc, mate = g.sheet["name"], g.companions[0]["name"]
    g.sheet["hp"]["current"] = 3
    g.sheet["spell_slots"]["1"]["left"] = 0  # no Shield
    out = turns(g, {"turns": [{"name": "Goblin 1", "attacks": [{"attack": "Scimitar", "target": pc}]},
                              {"name": "Goblin 2", "attacks": [{"attack": "Scimitar", "target": pc, "or_targets": [mate]}]},
                              {"name": "Goblin 3", "attacks": [{"attack": "Scimitar", "target": pc}]}]})
    assert "STOPPED" not in out and g.sheet["hp"]["current"] == 0 and not g.dice.rolls
    assert f"Goblin 2's Scimitar at {mate}" in out and "Goblin 3's Scimitar isn't made" in out
    assert g.fight["order"][g.fight["turn"]]["name"] == "Goblin 3"


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


def test_a_companions_turn_in_the_batch(tmp_path: Path, monkeypatch: Any) -> None:
    """Goblin 1, the companion (her rapier and Sneak Attack, from her sheet), Goblin 2 at her: one call, up to the PC."""
    g = game(tmp_path, monkeypatch, "fighter", [2, 15, 1, 1, 10, 3], [("Goblin 1", "Goblin", 15), ("Goblin 2", "Goblin", 10)],
             mates=[("rogue", 12)])
    pc, mate = g.sheet["name"], g.companions[0]["name"]
    out = turns(g, {"turns": [{"name": "Goblin 1", "attacks": [{"attack": "Scimitar", "target": "pc"}]},
                              {"name": mate.split()[0], "attacks": [{"attack": "Rapier", "target": "Goblin 2",
                                                                    "extra_damage": "1d6"}]},
                              {"name": "Goblin 2", "attacks": [{"attack": "Scimitar", "target": mate}]}]})
    assert "STOPPED" not in out and not g.dice.rolls
    assert m._find(g.fight, "Goblin 2")["hp"] == 7 - 5 and g.companions[0]["hp"]["current"] == 10 - 5
    assert g.sheet["hp"]["current"] == 14 and f"Next is {pc}'s turn" in out
    assert "action" in m._find(g.fight, mate)["used"]


def test_companion_turn_refusals(tmp_path: Path, monkeypatch: Any) -> None:
    g = game(tmp_path, monkeypatch, "fighter", [], [("Goblin 1", "Goblin", 15)], mates=[("rogue", 16)])
    mate = g.companions[0]["name"]
    two = [{"attack": "Rapier", "target": "Goblin 1"}] * 2
    with pytest.raises(m.Refused, match="makes 1 attack with the Attack action"):
        turns(g, {"turns": [{"name": mate, "attacks": two}]})
    with pytest.raises(m.Refused, match="no attack 'Greatsword' on their sheet"):
        turns(g, {"turns": [{"name": mate, "attacks": [{"attack": "Greatsword", "target": "Goblin 1"}]}]})
    g.companions[0]["hp"]["current"] = 0
    with pytest.raises(m.Refused, match="death save"):
        turns(g, {"turns": [{"name": mate, "attacks": [{"attack": "Rapier", "target": "Goblin 1"}]}]})
    g.companions[0]["hp"]["current"] = 10
    turns(g, {"turns": [{"name": mate, "note": "hides"}, {"name": "Goblin 1", "note": "waits"}]})
    with pytest.raises(m.Refused, match="is the PC"):
        turns(g, {"turns": [{"name": "pc", "attacks": [{"attack": "Longsword", "target": "Goblin 1"}]}]})


def test_rage_halves_and_adds(tmp_path: Path, monkeypatch: Any) -> None:
    """Spending a Rage use starts its timer; while it runs, slashing is halved and the barbarian's melee hits add 2."""
    g = game(tmp_path, monkeypatch, "fighter", [19, 5, 15, 1], [("Goblin 1", "Goblin", 15)], mates=[("rogue", 12)])
    for s in (g.sheet, g.companions[0]):
        s["features"].append("Rage: In battle, you fight with primal ferocity. ... You have resistance to "
                             "bludgeoning, piercing, and slashing damage.")
        s["resources"]["Rage"] = {"max": 2, "left": 2, "recharge": "long"}
    g.clock, _ = m.change_time(g.clock, {"set": {"day": 1, "time": "12:00"}})
    assert "Rage: 1 minute" in g.change_party_member({"use_resource": "Rage"})
    g.change_party_member({"use_resource": "Rage", "who": g.companions[0]["name"]})
    out = turns(g, {"turns": [{"name": "Goblin 1", "attacks": [{"attack": "Scimitar", "target": "pc"}]},
                              {"name": g.companions[0]["name"], "attacks": [{"attack": "Rapier", "target": "Goblin 1"}]}]})
    assert g.sheet["hp"]["current"] == 14 - 3 and "resistant (Rage) to slashing: 7 -> 3" in out  # (5+2)//2
    assert m._find(g.fight, "Goblin 1")["hp"] == 7 - 6  # 1d8+3 = 1+3, +2 rage damage
    assert not fight.raging(g.sheet, m.advance(g.clock, 60))


def test_creature_resistances_and_parry(tmp_path: Path, monkeypatch: Any) -> None:
    """A skeleton is vulnerable to the quarterstaff's bludgeoning; a knight parries a hit that 2 more AC turns away."""
    g = game(tmp_path, monkeypatch, "fighter", [15, 4, 14], [("Skeleton", "Skeleton", 15), ("Knight", "Knight", 14)],
             mates=[("wizard", 12)])
    wiz = g.companions[0]["name"]
    g.fight, _ = m.next_turn(g.fight)  # the skeleton's turn
    g.fight, _ = m.next_turn(g.fight)  # the knight's
    out = turns(g, {"turns": [{"name": wiz, "attacks": [{"attack": "Quarterstaff", "target": "Skeleton"}]}]})
    assert m._find(g.fight, "Skeleton")["hp"] == 7 - 6 and "vulnerable to bludgeoning: 3 -> 6" in out
    g.fight, _ = m.next_turn(g.fight)
    g.fight, _ = m.next_turn(g.fight)
    g.fight, _ = m.next_turn(g.fight)  # the knight's again; the wizard's next
    out = turns(g, {"turns": [{"name": wiz, "attacks": [{"attack": "Quarterstaff", "target": "Knight"}]}]})
    assert "Knight uses Parry" in out and m._find(g.fight, "Knight")["hp"] == 7
    assert "reaction" in m._find(g.fight, "Knight")["used"]


def test_resistances_from_sheets_and_stat_blocks() -> None:
    assert fight.member_resists(sheet("fighter"), m.new_clock()) == {"poison": {"resistant": "Dwarven Resilience"}}
    s = sheet("wizard") | {"features": [
        "Hellish Resistance: You have resistance to fire damage.",
        "Damage Resistance: You have resistance to the damage type associated with your draconic ancestry.",
        "Draconic Ancestry (Blue): breath weapon 5 by 30 ft line, DEX save DC 12, 2d6 Lightning damage (half on a "
        "success); resistance to that damage type"]}
    assert set(fight.member_resists(s, m.new_clock())) == {"fire", "lightning"}
    from dm import srd
    wolf = srd.find("Monsters", "Werewolf, Hybrid Form")
    assert fight.creature_resists(wolf, weapon=True)[0]["slashing"] == {"immune"}
    assert fight.creature_resists(wolf, weapon=False)[0] == {}
    assert fight.resisted(7, {"resistant", "vulnerable"}) == 6 and fight.resisted(7, {"immune"}) == 0


def test_opportunity_attacks_the_call_gives(tmp_path: Path, monkeypatch: Any) -> None:
    """The call says Goblin 1 takes opportunity attacks with its scimitar, and the companion with her rapier: the code
    makes them as the other leaves its reach. Goblin 2, given none, makes none."""
    g = game(tmp_path, monkeypatch, "fighter", [15, 2, 17, 6], [("Goblin 1", "Goblin", 15), ("Goblin 2", "Goblin", 11)],
             mates=[("rogue", 12)])
    mate = g.companions[0]["name"]
    out = turns(g, {"reactions": {"Goblin 1": {"opportunity_attack": "Scimitar"},
                                  mate: {"opportunity_attack": "Rapier"}},
                    "turns": [{"name": "Goblin 1", "note": "waits"},
                              {"name": mate, "leaves_reach_of": ["Goblin 1", "Goblin 2"], "note": "runs"},
                              {"name": "Goblin 2", "leaves_reach_of": [mate], "note": "chases"}]})
    assert "STOPPED" not in out and not g.dice.rolls
    assert g.companions[0]["hp"]["current"] == 10 - 4 and m._find(g.fight, "Goblin 2")["hp"] == 7 - 9 + 2  # 0
    assert "reaction" in m._find(g.fight, "Goblin 1")["used"] and "reaction" in m._find(g.fight, mate)["used"]


def test_companion_reactions_and_concentration(tmp_path: Path, monkeypatch: Any) -> None:
    """The companion wizard casts Shield when it turns a hit into a miss (the call says she does); hit later, she
    saves for her concentration, rolled by the code."""
    g = game(tmp_path, monkeypatch, "fighter", [10, 18, 3, 4], [("Goblin 1", "Goblin", 15), ("Goblin 2", "Goblin", 14)],
             mates=[("wizard", 12)])
    wiz = g.companions[0]["name"]
    g.clock, _ = m.change_time(g.clock, {"set": {"day": 1, "time": "12:00"}})
    g.companions[0]["concentration"] = "Sleep"
    out = turns(g, {"reactions": {wiz: {"take": ["Shield"]}},
                    "turns": [{"name": "Goblin 1", "attacks": [{"attack": "Scimitar", "target": wiz}]},
                              {"name": "Goblin 2", "attacks": [{"attack": "Scimitar", "target": wiz}]}]})
    assert "STOPPED" not in out and g.companions[0]["ac_now"]["value"] == 16 and "now a miss against AC 16" in out
    assert g.companions[0]["spell_slots"]["1"]["left"] == 1 and g.companions[0]["hp"]["current"] == 8 - 5
    assert "concentration on Sleep (CON save, DC 10)" in out and "it's lost" in out and not g.companions[0].get("concentration")
    with pytest.raises(m.Refused, match="the PC's reactions are the player's"):
        turns(g, {"reactions": {"pc": {"take": ["Shield"]}}, "turns": [{"name": wiz, "note": "x"}]})
