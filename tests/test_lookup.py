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
    multi = L.lookup("Multiclassing")
    assert multi.startswith("RULE Multiclassing:") and "never looking back at the class you left behind" in multi
    assert "| Wizard | Intelligence 13 |" in squash(L.lookup("Multiclassing: Prerequisites"))
    assert "| 20th | 4 | 3 | 3 | 3 | 3 | 2 | 2 | 1 | 1 |" in squash(L.lookup("Multiclassing: Spellcasting"))
    assert "Grappler feat requires you to have a Strength of 13" in L.lookup("Feats")
    assert "A feat represents a talent" in L.lookup("feats", "rule") and "gap-fill" in srd.table("Rules")["feats"]["source"]
    assert "grappler" in srd.table("Feats")  # the feat itself is in the dataset
    # the dataset's own sections are still the only ones under their bare names
    assert L.lookup("Proficiency Bonus").count("RULE") == 1 and L.lookup("Spellcasting").count("RULE") == 1
