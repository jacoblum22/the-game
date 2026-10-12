from pathlib import Path
from typing import Any

import pytest

from dm import lookup as L
from dm import srd


def test_entries() -> None:
    goblin = L.lookup("goblin")
    assert "AC 15 (armor: Leather Armor, Shield); HP 7 (2d6)" in goblin and "Challenge 0.25 (50 XP)" in goblin
    assert "Scimitar: Melee Weapon Attack: +4 to hit" in goblin
    shield = L.lookup("Shield")  # a spell and a piece of equipment
    assert "SPELL Shield: level 1 abjuration" in shield and "EQUIPMENT Shield" in shield
    assert L.lookup("shield", "spell").count("SPELL") == 1 and "EQUIPMENT" not in L.lookup("shield", "spell")
    assert "range 150/600" in L.lookup("Longbow")
    assert L.lookup("ability score improvement").count("FEATURE") < 5  # the same text at many levels shows once


def test_not_found() -> None:
    assert "Rules sections whose text mentions it: Melee Attacks" in L.lookup("grappling")
    assert "Adult Red Dragon (monster)" in L.lookup("red dragon")
    assert "may not be in the SRD" in L.lookup("beholder")


def test_every_entry_formats() -> None:
    for t in L.KINDS.values():
        for x in srd.table(t).values():
            assert L.FORMAT[t](x), (t, x["index"])


def test_a_procedure_comes_with_the_rules_its_steps_name() -> None:
    names = lambda t: [x.split(":")[0] for x in t.split("\n") if x.startswith("RULE ")]
    assert names(L.lookup("Combat Step by Step")) == ["RULE Combat Step by Step", "RULE Surprise", "RULE The Order of Combat",
                                                    "RULE Initiative"]
    assert names(L.lookup("Making an Attack")) == ["RULE Making an Attack", "RULE Attack", "RULE Cover",
                                                 "RULE Advantage and Disadvantage"]
    assert names(L.lookup("Surprise")) == ["RULE Surprise"]  # a section without steps comes alone


def test_linked_sections_go_one_level_deep_only() -> None:
    biggest = 0
    for r in srd.table("Rules").values():
        text = L.lookup(r["name"], "rule")
        assert text.count("The rules sections these steps name") <= 1  # linked sections never bring their own
        biggest = max(biggest, len(text))
    assert biggest < 12_000, biggest


def test_the_gap_fill_sections_the_dataset_lacks() -> None:
    squash = lambda t: " ".join(t.split())
    beyond = squash(L.lookup("Beyond 1st Level"))
    assert "| 300 | 2 | +2 |" in beyond and "| 355,000 | 20 | +6 |" in beyond and "gaining a level" in beyond
    assert "gap-fill" in srd.table("Rules")["beyond-1st-level"]["source"]
    # multiclassing and feats are optional rules the game doesn't use (owner): not in the lookup
    assert "multiclassing" not in srd.table("Rules") and "feats" not in srd.table("Rules")


# ---------- classes (the rows below are the SRD 5.1 PDF's) ----------

def test_a_class_lookup_is_its_rules_text_without_the_features() -> None:
    wiz = L.lookup("Wizard", "class")  # a caster (PDF p.52)
    assert wiz.startswith("CLASS Wizard") and "FEATURE" not in wiz
    assert "Hit Dice: 1d6 per wizard level" in wiz
    assert "Hit Points at Higher Levels: 1d6 (or 4) + your Constitution modifier per wizard level after 1st" in wiz
    assert "Weapons: Daggers, darts, slings, quarterstaffs, light crossbows" in wiz and "- A spellbook" in wiz
    assert "| Level | Proficiency Bonus | Features | Cantrips Known | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th | 9th |" in wiz
    assert "| 9th | +4 | — | 4 | 4 | 3 | 3 | 3 | 1 | — | — | — | — |" in wiz
    assert "| 20th | +6 | Signature Spell | 5 | 4 | 3 | 3 | 3 | 3 | 2 | 2 | 1 | 1 |" in wiz
    assert wiz.count("\n| ") == 21  # the header and one row per level
    assert "Spellcasting: Preparing and Casting Spells:\nThe Wizard table shows" in wiz and "School of Evocation:" in wiz
    heads = ["Hit Points:", "Proficiencies:", "Equipment:", "The Wizard:", "Spellcasting: Cantrips:", "Spellcasting: Spellbook:",
             "Spellcasting: Preparing and Casting Spells:", "Spellcasting: Spellcasting Ability:", "Spellcasting: Ritual Casting:",
             "Spellcasting: Spellcasting Focus:", "Learning Spells of 1st Level and Higher:", "Your Spellbook:", "School of Evocation:"]
    at = [wiz.index(h) for h in heads]
    assert at == sorted(at)  # in the PDF's order
    barb = L.lookup("barbarian", "class")  # a non-caster (p.8)
    assert "Spellcasting" not in barb and "Hit Points at 1st Level: 12 + your Constitution modifier" in barb
    assert "| Level | Proficiency Bonus | Features | Rages | Rage Damage |" in barb
    assert "| 9th | +4 | Brutal Critical (1 die) | 4 | +3 |" in barb and "| 20th | +6 | Primal Champion | Unlimited | +4 |" in barb
    monk, warlock = L.lookup("Monk", "class"), L.lookup("Warlock", "class")  # columns the PDF prints, not the dataset's field names
    assert "| Level | Proficiency Bonus | Martial Arts | Ki Points | Unarmored Movement | Features |" in monk
    assert "| 6th | +3 | 1d6 | 6 | +15 ft. | Ki Empowered Strikes, Monastic Tradition feature |" in monk
    assert "| Slot Level | Invocations Known |" in warlock and "| 6th | +3 | Otherworldly Patron feature | 3 | 7 | 2 | 3rd | 3 |" in warlock
    for c in srd.table("Classes").values():
        assert len(L.lookup(c["name"], "class")) < 20_000, c["name"]


def test_a_subclass_by_the_name_the_srd_gives_it() -> None:
    life = L.lookup("Life Domain")
    assert life.startswith("SUBCLASS Life Domain (Cleric: Divine Domain)")
    assert "Cleric level 7: Death Ward, Guardian of Faith" in life and "Cleric level 1: Bless, Cure Wounds" in life
    assert "(such as Chauntea, Arawai, and Demeter)" in life
    devotion = L.lookup("Oath of Devotion")
    assert "Honesty. Don't lie or cheat." in devotion and "Paladin level 13: Freedom of Movement, Guardian of Faith" in devotion
    fiend = L.lookup("The Fiend")  # by spell level, as the SRD's table is
    assert "The following spells are added to the warlock spell list for you." in fiend
    assert "Spell level 1st: Burning Hands, Command" in fiend and "Spell level 5th: Flame Strike, Hallow" in fiend
    land = L.lookup("Circle of the Land")
    assert "Arctic - Druid level 3: Hold Person, Spike Growth" in land and "Swamp - Druid level 9: Insect Plague, Scrying" in land
    assert "| Silver" in L.lookup("Draconic Bloodline") and "Draconic Ancestry:" in L.lookup("Draconic Bloodline")
    for sub in srd.table("Subclasses").values():  # every SRD subclass is found by its own name
        assert L.lookup(L._SUBCLASS[sub["index"]][0]).startswith("SUBCLASS "), sub["name"]
        assert L.lookup(sub["name"], "class").startswith("SUBCLASS "), sub["name"]  # "Berserker" is also a monster


def test_each_gap_filled_class_passage_is_found_by_its_heading_and_sits_in_its_class_lookup() -> None:
    found = {"Hit Points (Barbarian)": "1d12 (or 7)", "Proficiencies (Druid)": "druids will not wear armor or use shields made of metal",
             "Equipment (Cleric)": "- A shield and a holy symbol", "Learning Spells of 1st Level and Higher": "add two wizard spells",
             "Your Spellbook": "2 hours and costs 50 gp", "Eldritch Invocations": "A level prerequisite refers to your level in this class.",
             "Expanded Spell List": "added to the warlock spell list for you", "Your Pact Boon": "Pact of the Chain",
             "Tenets of Devotion": "Let your word be your promise.", "Breaking Your Oath": "forced to abandon this class",
             "Sacred Plants and Wood": "yucca", "Flexible Casting": "sacrifice spell slots", "Creating Spell Slots": "| 5th",
             "Beast Shapes": "| Giant eagle", "Destroy Undead": "| 17th", "Draconic Ancestry": "| Silver"}
    for heading, text in found.items():
        assert text in L.lookup(heading), heading
    gap = [g for g in srd.table("Rules").values() if g.get("for")]
    assert len(gap) == 49 and all("(gap-fill)" in g["source"] for g in gap)
    for g in gap:
        sub = srd.table("Subclasses").get(g["for"])
        cls = srd.table("Classes")[sub["class"]["index"] if sub else g["for"]]
        assert g["desc"] in L.lookup(cls["name"], "class"), g["name"]  # in place: its `after` heading resolves
        assert g["desc"] in L.lookup(g["name"], "rule"), g["name"]


def test_corrections_make_the_data_the_srds() -> None:
    squash = lambda t: " ".join(t.split())
    assert [srd.table("Levels")[f"warlock-{n}"]["class_specific"]["invocations_known"] for n in range(1, 21)] == \
        [0, 2, 2, 2, 3, 3, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8, 8, 8]  # the PDF's Invocations Known column (p.46)
    life = {s["spell"]["index"]: s["prerequisites"][0]["index"] for s in srd.table("Subclasses")["life"]["spells"]}
    assert life["death-ward"] == life["guardian-of-faith"] == "cleric-7" and len(life) == 10
    rage = squash(L.lookup("Rage", "feature"))
    assert "increases as you gain levels as a barbarian, as shown in the Rage Damage column of the Barbarian table." in rage
    assert "Rages column of the Barbarian table" in rage
    assert "as shown in the Destroy Undead table." in L.lookup("Destroy Undead (CR 4 or below)", "feature")
    assert "(the vampire Count Strahd von Zarovich, for instance)" in L.lookup("Divine Sense", "feature")
    assert "(as described in appendix PH-A)" in L.lookup("Frenzy", "feature")
    assert 'a druidic focus (see "Equipment")' in L.lookup("Druid", "class") and "chapter 5" not in L.lookup("Druid", "class")
    assert "Each domain is detailed at the end of the class description" in L.lookup("Divine Domain", "feature")
    assert "the Archfey, the Fiend, or the Great Old One" in L.lookup("Otherworldly Patron", "feature")
    assert "Additional archetypes" not in L.lookup("Roguish Archetype", "feature")


def test_a_correction_to_something_that_is_not_there_raises(tmp_path: Path, monkeypatch: Any) -> None:
    (tmp_path / "corrections").mkdir()
    (tmp_path / "5e-SRD-Rules.json").write_text('[{"index": "a", "name": "A", "xs": [{"v": 1}], "d": {"k": 1}}]', encoding="utf-8")
    fix = tmp_path / "corrections" / "5e-SRD-Rules.json"
    monkeypatch.setattr(srd, "DIR", tmp_path)
    srd.table.cache_clear()
    try:
        fix.write_text('[{"index": "a", "source": "p.1", "set": {"xs.0.v": 2, "d.k": 3}}]', encoding="utf-8")
        assert srd.table("Rules")["a"]["xs"] == [{"v": 2}] and srd.table("Rules")["a"]["d"] == {"k": 3}
        for bad in ('[{"index": "b", "source": "p.1", "set": {"d.k": 3}}]', '[{"index": "a", "source": "p.1", "set": {"d.nope": 3}}]'):
            srd.table.cache_clear()
            fix.write_text(bad, encoding="utf-8")
            with pytest.raises(ValueError):
                srd.table("Rules")
    finally:
        monkeypatch.undo()
        srd.table.cache_clear()


def test_eldritch_invocations_print_the_srds_prerequisite_line() -> None:
    pre = {"Agonizing Blast": "eldritch blast cantrip", "Book of Ancient Secrets": "Pact of the Tome feature",
           "Eldritch Spear": "eldritch blast cantrip", "Repelling Blast": "eldritch blast cantrip",
           "Voice of the Chain Master": "Pact of the Chain feature", "Mire the Mind": "5th level", "One with Shadows": "5th level",
           "Sign of Ill Omen": "5th level", "Thirsting Blade": "5th level, Pact of the Blade feature",
           "Bewitching Whispers": "7th level", "Dreadful Word": "7th level", "Sculptor of Flesh": "7th level",
           "Ascendant Step": "9th level", "Minions of Chaos": "9th level", "Otherworldly Leap": "9th level",
           "Whispers of the Grave": "9th level", "Lifedrinker": "12th level, Pact of the Blade feature",
           "Chains of Carceri": "15th level, Pact of the Chain feature", "Master of Myriad Forms": "15th level",
           "Visions of Distant Realms": "15th level", "Witch Sight": "15th level"}  # SRD 5.1 pp.48-50
    names = [f["name"] for f in srd.table("Features").values() if f["name"].startswith("Eldritch Invocation: ")]
    assert len(names) == 32
    for n in names:
        lines = L.lookup(n, "feature").split("\n")
        want = pre.get(n.split(": ")[1])
        assert (lines[1] == f"Prerequisite: {want}") if want else not any(x.startswith("Prerequisite") for x in lines), n


def test_forgiving_names() -> None:
    assert "FEATURE Ki Empowered Strikes" in L.lookup("Ki-Empowered Strikes") and "may not be in the SRD" not in L.lookup("Ki-Empowered Strikes")
    assert "FEATURE Signature Spell" in L.lookup("Signature Spells") and "FEATURE Signature Spell" in L.lookup("signature spell")
    assert L.lookup("Thieves’ Cant") == L.lookup("Thieves' Cant") and "FEATURE Thieves' Cant" in L.lookup("Thieves’ Cant")
    assert "FEATURE Land's Stride" in L.lookup("Land’s Stride")
    wild = L.lookup("Wild Shape")  # "Name (...)" entries come as one answer
    assert wild.count("FEATURE") == 1 and wild.startswith("FEATURE Wild Shape (CR 1/4 or below, no flying or swim speed) / Wild Shape (CR 1/2")
    channel = L.lookup("Channel Divinity")
    assert "FEATURE Channel Divinity (Paladin level 3)" in channel and "FEATURE Channel Divinity (1/rest)" in channel
    assert "Channel Divinity (2/rest) / Channel Divinity (3/rest)" in channel
    undead = L.lookup("Destroy Undead")
    assert undead.startswith("RULE Destroy Undead") and "FEATURE Destroy Undead (CR 1/2 or below) / Destroy Undead (CR 1 or below)" in undead
    assert "FEATURE Favored Enemy" in L.lookup("Favored Enemy") and "Bardic Inspiration" in L.lookup("Bardic Inspiration")
    assert L.lookup("Shield").count("SPELL") == 1 and "EQUIPMENT Shield" in L.lookup("Shield")  # exact entries stay as they were
