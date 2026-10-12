"""SRD sections the dataset lacked, added from the PDF (dm/srd/gapfill, dm/srd/corrections), seen through the lookup the DM uses."""
import json

import pytest

from dm import srd
from dm.lookup import lookup


def test_improvised_weapons() -> None:
    text = lookup("Improvised Weapons")
    assert "deals 1d4 damage" in text
    assert "normal range of 20 feet and a long range of 60 feet" in text


def test_getting_into_and_out_of_armor_has_its_table() -> None:
    text = lookup("Getting Into and Out of Armor")
    assert "You benefit from the armor's AC only if you take the full time to don the suit of armor." in text
    assert "| Shield       | 1 action   | 1 action  |" in text
    assert "| Heavy Armor  | 10 minutes | 5 minutes |" in text


def test_armor_and_weapons_come_with_the_magic_items_of_the_same_name() -> None:
    armor = lookup("Armor")
    assert "RULE Armor:" in armor and "Armor Proficiency." in armor and "MAGIC ITEM Armor, +1, +2, or +3" in armor
    for name, line in (("Light Armor", "add your Dexterity modifier to the base number"),
                       ("Medium Armor", "to a maximum of +2"), ("Heavy Armor", "doesn't let you add your Dexterity modifier")):
        assert line in lookup(name)
    assert "RULE Weapons:" in lookup("Weapons") and "The two categories are simple and martial." in lookup("Weapon Proficiency")
    assert "You can silver a single weapon or ten pieces of ammunition for 100 gp." in lookup("Silvered Weapons")


def test_range_is_a_weapon_property() -> None:
    text = lookup("Range", "weapon_property")
    assert text.startswith("WEAPON PROPERTY Range:") and "You can't attack a target beyond the weapon's long range." in text


def test_equipment_chapter_prose() -> None:
    assert "fetch half their cost when sold in a market" in lookup("Selling Treasure")
    assert "| Backpack*        | 1 cubic foot/30 pounds of gear         |" in lookup("Container Capacity")
    assert "* You can also strap items" in lookup("Container Capacity")
    assert "you can purchase a pack for the price shown" in lookup("Equipment Packs")
    assert "Tool use is not tied to a single ability" in lookup("Tools")
    mounts = lookup("Mounts and Vehicles")
    assert "five times its base carrying capacity" in mounts and "***Vehicle Proficiency.***" in mounts
    assert "| 500 gp | 1 lb. of platinum" in lookup("Trade Goods")
    assert "basic necessities" in lookup("Expenses")
    assert "Proficiency in the Survival skill lets you live at the equivalent of a comfortable lifestyle." in lookup("Self-Sufficiency")
    assert "| Wine                 |       |" in lookup("Food, Drink, and Lodging")
    services = lookup("Services")
    assert "| Skilled           | 2 gp per day  |" in services and "no established pay rates exist" in lookup("Spellcasting Services")


def test_lifestyle_expenses_has_both_versions() -> None:
    text = lookup("Lifestyle Expenses")
    assert "RULE Lifestyle Expenses:" in text and "RULE Lifestyle Expenses (SRD 5.1 pp.72-73):" in text
    assert "Between adventures, you choose a particular quality of life" in text  # Between Adventures (p.88)
    assert "| Aristocratic | 10 gp minimum |" in text and "***Wretched.***" in text  # Equipment (pp.72-73)
    assert {"lifestyle-expenses", "lifestyle-expenses-equipment"} <= set(srd.table("Rules"))


def test_monsters_introduction() -> None:
    assert "| 1/4       | 50      |" in lookup("Experience Points")
    assert "| 30        | 155,000 |" in lookup("Experience Points")
    assert "| 30        | +9                |" in lookup("Saving Throws")
    assert "| Gargantuan   | d20     | 10½                |" in lookup("Hit Points")
    assert "pinpoint the origin of vibrations" in lookup("Tremorsense")
    assert "roll a d6" in lookup("Limited Usage") and "***Recharge X-Y.***" in lookup("Limited Usage")
    assert "On initiative count 20 (losing all initiative ties)" in lookup("Lair Actions")
    assert "it doesn't need to make an additional ability check" in lookup("Grapple Rules for Monsters")
    assert "Only one legendary action option can be used at a time" in lookup("Legendary Actions")
    assert "Assume that a creature is proficient with its armor, weapons, and tools." in lookup("Armor, Weapon, and Tool Proficiencies")
    for heading in ("Size", "Modifying Creatures", "Type", "Tags", "Alignment", "Armor Class", "Burrow", "Climb", "Fly", "Swim",
                    "Ability Scores", "Vulnerabilities, Resistances, and Immunities", "Blindsight", "Darkvision", "Truesight", "Languages",
                    "Telepathy", "Challenge", "Special Traits", "Innate Spellcasting", "Psionics", "Actions", "Melee and Ranged Attacks",
                    "Multiattack", "Ammunition", "Equipment", "Legendary Creatures", "A Legendary Creature's Lair", "Regional Effects"):
        assert "RULE " + heading + ":" in lookup(heading), heading


def test_monster_rules_sharing_a_heading_with_an_adventuring_rule_come_together() -> None:
    for name in ("Hit Points", "Speed", "Saving Throws", "Skills", "Spellcasting", "Reactions", "Equipment"):
        assert lookup(name).count(f"RULE {name}") == 2 and f"RULE {name}:" in lookup(name), name
    assert "A monster's hit points are presented both as a die expression" in lookup("Hit Points")


def test_legendary_action_introduction_is_printed_before_the_options() -> None:
    red = lookup("Adult Red Dragon")
    intro = ("The dragon can take 3 legendary actions, choosing from the options below. Only one legendary action option can be used at "
             "a time and only at the end of another creature's turn. The dragon regains spent legendary actions at the start of its turn.")
    assert f"Legendary actions:\n{intro}\n- Detect:" in red
    assert "The aboleth can take 3 legendary actions" in lookup("Aboleth")
    assert "The tarrasque can take 3 legendary actions" in lookup("Tarrasque")
    assert all("The vampire can take 3 legendary actions" in lookup(f"Vampire, {form}") for form in ("Vampire Form", "Bat Form", "Mist Form"))
    legendary = [m for m in srd.table("Monsters").values() if m.get("legendary_actions")]
    assert len(legendary) == 32 and all(m["legendary_actions_intro"].startswith("The ") for m in legendary)
    assert "legendary actions, choosing" not in lookup("Goblin")


def test_other_sections() -> None:
    template = lookup("Half-Dragon Template")
    assert "| Brass, gold, or red | Fire              |" in template and "| Huge             | As a young dragon  | Challenge 7 or higher |" in template
    assert "A creature either has a condition or doesn't." in lookup("Conditions", "rule")
    assert "***Spell Swaps.***" in lookup("Customizing NPCs")


def test_every_new_section_names_its_pdf_pages() -> None:
    new = [r for r in srd.table("Rules").values() if r.get("source", "").endswith("(gap-fill)") and "for" not in r]
    assert len(new) > 60 and all(r["source"].startswith("SRD 5.1 p") and r["desc"] for r in new)


def test_a_correction_can_add_a_field_but_not_overwrite_one(tmp_path, monkeypatch) -> None:
    (tmp_path / "corrections").mkdir()
    (tmp_path / "5e-SRD-Foo.json").write_text(json.dumps([{"index": "a", "name": "A", "x": 1}]), encoding="utf-8")
    fix = tmp_path / "corrections" / "5e-SRD-Foo.json"
    monkeypatch.setattr(srd, "DIR", tmp_path)
    fix.write_text(json.dumps([{"index": "a", "source": "test", "add": {"y": 2}}]), encoding="utf-8")
    assert srd.table("Foo")["a"]["y"] == 2
    srd.table.cache_clear()
    fix.write_text(json.dumps([{"index": "a", "source": "test", "add": {"x": 2}}]), encoding="utf-8")
    with pytest.raises(ValueError, match="already there"):
        srd.table("Foo")
    srd.table.cache_clear()
