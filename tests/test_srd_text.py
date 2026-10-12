"""SRD text corrected to the PDF (dm/srd/corrections, dm/srd/gapfill), seen through the lookup the DM uses."""
from dm.lookup import lookup


def test_spell_casting_time_keeps_its_trigger() -> None:
    assert "Casting time 1 reaction, which you take when you are hit by an attack or targeted by the magic missile spell" \
        in lookup("Shield", "spell")
    assert "1 reaction, which you take when you see a creature within 60 feet of you casting a spell" in lookup("Counterspell")
    assert "Casting time 1 action or 8 hours" in lookup("Plant Growth")


def test_spell_text_is_the_pdfs() -> None:
    assert "worth at least 10 gp, which the spell consumes" in lookup("Magic Mouth")
    assert "inches" not in lookup("Magic Mouth")
    assert "At the end of each of the frightened creature's turns" in lookup("Weird")
    assert "1d10 for each slot level above 2nd" in lookup("Moonbeam")
    assert "10d10" in lookup("Symbol") and "10d 10" not in lookup("Symbol")
    assert "range Self (15-foot cone)" in lookup("Burning Hands")
    assert "When you cast this spell with a 5th-level spell slot" in lookup("Dominate Beast")


def test_spell_upcast_lines_the_dataset_lacked() -> None:
    assert "you can target one additional creature for each slot level above 1st" in lookup("Heroism")
    friend = lookup("Animal Friendship")  # the PDF's own text is damaged here; repaired by the owner's decision
    assert "you can affect one additional beast for each slot level above 1st." in friend and "beast t level" not in friend


def test_spell_level_school_and_classes() -> None:
    assert "SPELL Revivify: level 3 necromancy" in lookup("Revivify")
    assert "Classes: Cleric" in lookup("Divination", "spell")


def test_magic_items() -> None:
    shield = lookup("Shield, +1, +2, or +3")
    assert "MAGIC ITEM Shield, +1, +2, or +3" in shield and "Armor (shield), uncommon (+1), rare (+2), or very rare (+3)" in shield
    assert "You have darkvision out to a range of 60 feet." in lookup("Belt of Dwarvenkind")
    deck = lookup("Deck of Many Things")
    assert "Avatar of Death" in deck and "Challenge — (0 XP)" in deck and "Reaping Scythe" in deck
    assert "***The Void.***" in deck and "***Star.***" in deck
