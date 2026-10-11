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
