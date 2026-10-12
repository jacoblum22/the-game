import json
import random
from pathlib import Path

import pytest

from dm import mechanics as m

CHAR = Path(__file__).parent.parent / "dm" / "characters"


def sheet(name: str) -> dict:
    return json.loads((CHAR / f"{name}.json").read_text(encoding="utf-8"))


def test_dice() -> None:
    r = m.roll("2d6+1d4-1", rng=random.Random(1))
    assert r["total"] == sum(r["parts"][0]["rolls"]) + sum(r["parts"][1]["rolls"]) - 1
    adv = m.roll("1d20+5", "advantage", random.Random(2))
    assert adv["parts"][0]["kept"] == max(adv["parts"][0]["rolls"]) and adv["total"] == adv["natural"] + 5
    dis = m.roll("1d20", "disadvantage", random.Random(2))
    assert dis["total"] == min(dis["parts"][0]["rolls"])
    for bad in ("", "d", "1d20+x", "2d6 and 3"):
        with pytest.raises(m.Refused):
            m.roll(bad)
    with pytest.raises(m.Refused):
        m.roll("2d6", "advantage")


def test_damage_heal_and_dying() -> None:
    s = sheet("fighter")  # 14 HP
    s, _ = m.change_pc(s, {"temp_hp": 3})
    s, _ = m.change_pc(s, {"damage": 5})
    assert (s["hp"]["temp"], s["hp"]["current"]) == (0, 12)
    s, _ = m.change_pc(s, {"damage": 20})
    assert s["hp"]["current"] == 0 and "unconscious" in s["conditions"] and "dead" not in s["conditions"]
    s, _ = m.change_pc(s, {"damage": 2})
    assert s["death_saves"]["failures"] == 1
    s, _ = m.change_pc(s, {"heal": 4})
    assert s["hp"]["current"] == 4 and "unconscious" not in s["conditions"] and s["death_saves"]["failures"] == 0
    dead, _ = m.change_pc(sheet("fighter"), {"damage": 28})  # 14 left over >= max 14
    assert "dead" in dead["conditions"]


def _down(name: str = "fighter") -> dict:
    s, _ = m.change_pc(sheet(name), {"damage": 20})  # 14 HP fighter at 0 HP, unconscious
    return s


def test_critical_hit_at_zero_hp() -> None:
    s, text = m.change_pc(_down(), {"damage": 3, "critical_hit": True})
    assert s["death_saves"]["failures"] == 2 and "two death save failures" in text[0]
    s, _ = m.change_pc(s, {"damage": 3})  # an ordinary hit adds one: 3 failures, dead
    assert "dead" in s["conditions"]
    s, _ = m.change_pc(_down(), {"damage": 14, "critical_hit": True})  # damage >= max HP is still instant death
    assert "dead" in s["conditions"]


def test_stable_resets_and_ends_on_damage() -> None:
    s, _ = m.change_pc(_down(), {"death_save_failures": 2})
    s, _ = m.change_pc(s, {"death_save_successes": 3})
    assert "stable" in s["conditions"] and s["death_saves"] == {"successes": 0, "failures": 0}
    assert "Stable" in m.status(s)
    for kind in ("death_save_successes", "death_save_failures"):
        with pytest.raises(m.Refused, match="stable"):
            m.change_pc(s, {kind: 1})
    s, _ = m.change_pc(s, {"damage": 2})
    assert "stable" not in s["conditions"] and s["death_saves"] == {"successes": 0, "failures": 1}
    s, _ = m.change_pc(s, {"death_save_successes": 1})  # death saves start again
    assert s["death_saves"]["successes"] == 1
    first_aid, _ = m.change_pc(s, {"conditions_added": ["stable"]})  # first aid also resets both counts
    assert first_aid["death_saves"] == {"successes": 0, "failures": 0}


def test_dead_and_revival() -> None:
    dead, _ = m.change_pc(_down(), {"death_save_failures": 3})
    assert "dead" in dead["conditions"]
    with pytest.raises(m.Refused, match="dead"):
        m.change_pc(dead, {"death_save_successes": 1})
    with pytest.raises(m.Refused, match="conditions_removed"):
        m.change_pc(dead, {"heal": 5})
    alive, _ = m.change_pc(dead, {"conditions_removed": ["dead"]})
    alive, _ = m.change_pc(alive, {"heal": 1})
    assert alive["hp"]["current"] == 1 and "dead" not in alive["conditions"] and "unconscious" not in alive["conditions"]


def test_long_rest_needs_a_hit_point() -> None:
    for s in (_down(), m.change_pc(_down(), {"death_save_failures": 3})[0]):
        with pytest.raises(m.Refused, match="at least 1 hit point"):
            m.change_pc(s, {"long_rest": True})
    hurt, _ = m.change_pc(sheet("fighter"), {"damage": 13})  # 1 HP is enough
    rested, _ = m.change_pc(hurt, {"long_rest": True})
    assert rested["hp"]["current"] == 14


def test_hit_dice_one_at_a_time() -> None:
    w = sheet("wizard")
    w["hit_dice"]["left"] = w["hit_dice"]["max"] = 3
    with pytest.raises(m.Refused, match="one at a time"):
        m.change_pc(w, {"hit_dice_spent": 2})
    w, text = m.change_pc(w, {"hit_dice_spent": 1})
    assert w["hit_dice"]["left"] == 2 and "CON" in text[0] and f"1{w['hit_dice']['die']}" in text[0] and "heal" in text[0]
    w["hit_dice"]["left"] = 0
    with pytest.raises(m.Refused, match="no hit dice left"):
        m.change_pc(w, {"hit_dice_spent": 1})


def test_all_or_nothing_and_resources() -> None:
    w = sheet("wizard")
    w, _ = m.change_pc(w, {"spend_slot": 1})
    w, _ = m.change_pc(w, {"spend_slot": 1})
    with pytest.raises(m.Refused):
        m.change_pc(w, {"spend_slot": 1, "damage": 3})
    assert w["hp"]["current"] == 8  # the damage in the refused change was not applied
    w, _ = m.change_pc(w, {"use_resource": "Arcane Recovery", "restore_slot": 1})
    assert w["spell_slots"]["1"]["left"] == 1
    with pytest.raises(m.Refused):
        m.change_pc(w, {"use_resource": "Arcane Recovery"})
    w, _ = m.change_pc(w, {"long_rest": True})
    assert w["spell_slots"]["1"]["left"] == 2 and w["resources"]["Arcane Recovery"]["left"] == 1


def test_items_and_money() -> None:
    r = sheet("rogue")
    r, _ = m.change_pc(r, {"items_lost": [{"item": "Arrows", "qty": 3}], "coin_change_gp": -0.25})
    assert r["items"]["Arrows"] == 17 and r["coins_cp"] == 1475 and m.coins_text(1475) == "14 gp 7 sp 5 cp"
    for qty in (-5, 0):  # a non-positive quantity must not add items
        with pytest.raises(m.Refused):
            m.change_pc(r, {"items_lost": [{"item": "Arrows", "qty": qty}]})
    with pytest.raises(m.Refused):
        m.change_pc(r, {"items_lost": [{"item": "Longsword"}]})
    with pytest.raises(m.Refused):
        m.change_pc(r, {"coin_change_gp": -100})


def test_fight_order_and_turns() -> None:
    f, _ = m.add_combatants(None, "Brakka", [{"name": "pc", "initiative": 12},
                                             {"name": "Goblin 1", "initiative": 15, "hp": 7, "ac": 15},
                                             {"name": "Goblin 2", "initiative": 8, "hp": 7, "ac": 15}])
    assert [c["name"] for c in f["order"]] == ["Goblin 1", "Brakka", "Goblin 2"] and f["turn"] == -1
    f, text = m.next_turn(f)  # the first next_turn starts the first combatant's turn, not the second's
    assert "Goblin 1" in text and f["round"] == 1
    f, _ = m.add_combatants(f, "Brakka", [{"name": "Goblin 3", "initiative": 20, "hp": 7, "ac": 15}])
    assert f["order"][f["turn"]]["name"] == "Goblin 1"  # an arrival doesn't move whose turn it is
    f, _ = m.change_creature(f, {"name": "Goblin 3", "remove": True})
    f, text = m.next_turn(f)
    assert "Brakka" in text
    f, _ = m.change_creature(f, {"name": "Goblin 1", "damage": 9})
    assert f["order"][0]["hp"] == 0
    f, _ = m.change_creature(f, {"name": "Goblin 1", "remove": True})
    f, text = m.next_turn(f)
    assert "Goblin 2" in text and f["round"] == 1
    f, text = m.next_turn(f)
    assert "Brakka" in text and f["round"] == 2
    with pytest.raises(m.Refused):
        m.change_creature(f, {"name": "Brakka", "damage": 1})
    with pytest.raises(m.Refused):
        m.change_creature(f, {"name": "goblin 2", "damage": 1})
    assert m.end_fight(f)[0] is None
