"""level_up_options: what the next level gives and asks, worked by hand from the SRD class tables and feature text."""
import re

import pytest

from dm import create, srd
from tests.test_create import BRAKKA, WREN
from tests.test_levels import (
    FIXED,
    LOCK,
    LOCK_LEVELS,
    PAL,
    VEX,
    WREN_LEVELS,
    _auto,
    built,
)


def text_of(feature: str) -> str:
    """A feature's SRD text, as the options show it."""
    return " ".join(srd.table("Features")[feature]["desc"])


def skeleton(text: str) -> dict[str, str]:
    """The record skeleton at the end of the text: {field: its line}."""
    block = text.split("== Level record for level")[1]
    return {m.group(1): m.group(0) for m in re.finditer(r'^  "(\w+)": .*$', block, re.MULTILINE)}


def required(text: str) -> set[str]:
    return {k for k, line in skeleton(text).items() if "(optional)" not in line and "(only if" not in line}


def test_fighter_3_to_4_is_an_ability_score_improvement() -> None:
    # Brakka: Hill dwarf fighter 3, CON 16 (+3). d10 fixed value 6 (the SRD: "1d10 (or 6)"); Dwarven Toughness +1.
    s3 = built(BRAKKA, [FIXED, {"hp": {"rolled": 7}}])
    t = create.level_up_options(s3)
    assert "level 3 -> 4" in t and "Hit Die d10: take the fixed value 6" in t and "Constitution modifier now: +3 (CON 16)" in t
    assert "Dwarven Toughness: " in t and "Fixed: 10 hit points" in t and "Hit Dice: 3 -> 4" in t  # 6 + 3 + 1
    assert "HOUSE RULE (the owner's, not in the SRD" in t
    assert "== Proficiency bonus ==" not in t  # +2 until level 5
    assert "(no new class features)" in t
    assert "Second Wind: now 1d10 + 4 hit points (was: 1d10 + 3 hit points)" in t  # "1d10 + your fighter level"
    assert text_of("fighter-ability-score-improvement-1") in t and "== Ability Score Improvement ==" in t
    assert "Scores now: STR 15, DEX 10, CON 16, INT 8, WIS 14, CHA 12" in t and "+2 possible for: STR, DEX, CON, INT, WIS, CHA" in t
    assert set(skeleton(t)) == {"hp", "asi"} and required(t) == {"hp", "asi"}
    assert "Constitution modifier changes" in t  # an increase to CON changes the hit points of every level
    # the same fighter at 4 -> 5: proficiency +2 -> +3, Extra Attack, no ASI
    s4 = built(BRAKKA, s3["build"]["levels"] + [{"hp": "fixed", "asi": {"STR": 2}}])
    t5 = create.level_up_options(s4)
    assert "+2 -> +3" in t5 and "- Extra Attack: " + text_of("extra-attack-1") in t5 and "Ability Score Improvement" not in t5
    # a score at 19 can take +1 only, at 20 nothing: STR 15 -> 17 (4th) -> 19 (6th) -> 20 (8th, +1)
    s7 = built(BRAKKA, [FIXED, FIXED, {"hp": "fixed", "asi": {"STR": 2}}, FIXED, {"hp": "fixed", "asi": {"STR": 2}}, FIXED])
    t7 = create.level_up_options(s7)
    assert "STR 19" in t7 and "only +1 for: STR" in t7 and "+2 possible for: DEX, CON, INT, WIS, CHA" in t7
    ch, levels = _auto("fighter")  # the auto records raise the two highest scores: by level 12 one may be at 20
    s11 = built(ch, levels[:10])
    top = ", ".join(a for a in create.ABILITIES if s11["scores"][a] >= 20) or "none"
    assert f"no increase for: {top}" in create.level_up_options(s11)



def test_rogue_2_to_3_subclass_and_sneak_attack() -> None:
    # Vex: CON 14 (+2), d8 fixed value 5
    t = create.level_up_options(built(VEX, [FIXED]))
    assert "Fixed: 7 hit points" in t and "+2 -> +3" not in t
    assert "Subclass gained now: Thief (Roguish Archetype)" in t
    for f in ("roguish-archetype", "fast-hands", "second-story-work"):
        assert f"- {srd.table('Features')[f]['name']}: {text_of(f)}" in t
    assert "Sneak Attack: now the extra damage is 2d6 (was: the extra damage is 1d6)" in t  # Rogue table: 1d6, 2d6 at 3rd
    assert set(skeleton(t)) == {"hp"} and "== Spells" not in t and "Eldritch" not in t


def test_wizard_2_to_3_two_spells_and_second_level_slots() -> None:
    # Wren: INT 16 (+3), CON 13 (+1), d6 fixed 4. Spellbook 8 at level 2.
    s2 = built(WREN, WREN_LEVELS[:1])
    t = create.level_up_options(s2)
    assert "Fixed: 5 hit points" in t  # 4 + 1
    assert "Spell slots at level 3: 1st-level x4, 2nd-level x2 (was: 1st-level x3)" in t and "Highest spell level you can cast: 2nd." in t
    assert "add exactly 2 wizard spells of level 1 to 2 (the spellbook has 8)" in t
    eligible = t.split("Eligible:")[1].split("== Level record")[0]
    assert "2nd-level: " in eligible and "Invisibility" in eligible and "Misty Step" in eligible and "3rd-level" not in eligible
    assert "Thunderwave" not in eligible and "Identify" not in eligible  # already in the spellbook (level 2's two)
    assert "Magic Missile" not in eligible  # in the spellbook since level 1
    assert "Prepared spells now: up to 6 (was 5)" in t  # INT modifier 3 + wizard level
    assert set(skeleton(t)) == {"hp", "spells"} and "[<2 spell names>]" in skeleton(t)["spells"]
    assert "New cantrips" not in t  # the Cantrips Known column stays at 3 until level 4
    t4 = create.level_up_options(built(WREN, WREN_LEVELS[:2]))  # 3 -> 4: ASI and the fourth cantrip
    assert set(skeleton(t4)) == {"hp", "asi", "cantrips", "spells"}


def test_paladin_1_to_2_first_prepared_list() -> None:
    # PAL: CHA 14 + 1 = 15 (+2), CON 14 (+2). Paladin table, level 2: two 1st-level slots; prepare CHA 2 + half of 2 = 3.
    t = create.level_up_options(built(PAL, []))
    assert "Fixed: 8 hit points" in t  # d10 fixed 6 + 2
    assert text_of("paladin-fighting-style") in t and "[feature.paladin-fighting-style] Fighting Style: choose 1" in t
    assert "Fighting Style: Defense: While you are wearing armor, you gain a +1 bonus to AC." in t
    assert "- Divine Smite: " + text_of("divine-smite") in t and "- Spellcasting: " in t
    assert "Lay on Hands: now a pool of 10 hit points (was: a pool of 5 hit points)" in t
    assert "Spell slots at level 2: 1st-level x2 (was: none)" in t
    assert "choose 1 to 3 spells (the most you can prepare), each of level 1." in t
    assert "choose a number of paladin spells equal to your Charisma modifier + half your paladin level" in t  # the class text
    assert "1st-level: Bless, Command, Cure Wounds" in t and "Divine Favor" in t
    assert "New cantrips" not in t and "Replace one spell" not in t
    sk = skeleton(t)
    assert set(sk) == {"hp", "choices", "prepared"} and "[<1 to 3 spell names>]" in sk["prepared"]
    assert '"feature.paladin-fighting-style": <1 pick>' in sk["choices"]


def test_warlock_2_to_3_pact_boon_unlocks_invocations_in_the_same_record() -> None:
    s2 = built(LOCK, LOCK_LEVELS[:1])  # invocations Armor of Shadows, Beast Speech; Eldritch Blast known
    t = create.level_up_options(s2)
    assert "Invocations Known column: 2 -> 2 (no new invocation at this level)" in t and "Known now: Armor of Shadows, Beast Speech" in t
    assert "[feature.pact-boon] Pact Boon: choose 1" in t and "Pact of the Tome: " + text_of("pact-of-the-tome") in t
    assert "Spell slots at level 3: 2nd-level x2 (was: 1st-level x2)" in t and "Pact Magic: all your slots are the same level" in t
    # Book of Ancient Secrets needs Pact of the Tome, Voice of the Chain Master needs Pact of the Chain: both come with the boon
    later = t.split("Eligible if the player picks that Pact Boon in this same record:")[1].split("Not eligible")[0]
    assert "Book of Ancient Secrets (needs: Pact of the Tome)" in later and "[needs Pact of the Tome]" in later
    assert "Voice of the Chain Master" in later and "[needs Pact of the Chain]" in later
    # Thirsting Blade needs level 5 as well as the Blade: not eligible, with the reason
    assert "- Thirsting Blade: needs warlock level 5 (this is level 3)" in t
    assert "Agonizing Blast (needs: the Eldritch Blast cantrip): " + text_of("eldritch-invocation-agonizing-blast") in t
    # Pact of the Tome: three cantrips from any class; the invocations don't go up
    sk = skeleton(t)
    assert "tome" in sk and "(only if Pact of the Tome is chosen)" in sk["tome"] and "invocations" not in sk
    assert "replace_invocation" in sk and "(optional)" in sk["replace_invocation"] and "rituals" in sk
    assert required(t) == {"hp", "choices", "spells"}
    # the house rule for Beguiling Influence: LOCK already has Deception
    assert "Beguiling Influence" in t.split("Eligible now:")[1].split("Eligible if")[0] and "HOUSE RULE (the Player's Handbook" in t
    assert "invocation_skills" in sk


def test_warlock_4_to_5_one_new_invocation() -> None:
    s4 = built(LOCK, LOCK_LEVELS[:3])  # Tome; Armor of Shadows and Beast Speech; Eldritch Blast, Minor Illusion, Chill Touch
    t = create.level_up_options(s4)
    assert "Invocations Known column: 2 -> 3 (learn 1 new)" in t and "+2 -> +3" in t  # the Warlock table: 3 at 5th level
    assert "Spell slots at level 5: 3rd-level x2 (was: 2nd-level x2)" in t and "New spells known: choose 1, each of level 1 to 3" in t
    assert "Eldritch Blast: 2 beams, each with its own attack roll" in t  # "two beams at 5th level"
    eligible = t.split("Eligible now:")[1].split("Not eligible")[0]
    for name in ("Mire the Mind", "One with Shadows", "Sign of Ill Omen", "Book of Ancient Secrets"):  # warlock level 5 / the Tome
        assert f"- {name} (" in eligible, name
    assert "Mire the Mind (needs: warlock level 5)" in eligible and "Armor of Shadows" not in eligible  # already known
    no = t.split("Not eligible (why):")[1].split("Replace one invocation")[0]
    assert "- Thirsting Blade: needs Pact of the Blade" in no and "- Voice of the Chain Master: needs Pact of the Chain" in no
    assert "- Bewitching Whispers: needs warlock level 7 (this is level 5)" in no and "- Lifedrinker: needs warlock level 12" in no
    assert "Book of Ancient Secrets needs \"rituals\": exactly two 1st-level spells" in t and "Find Familiar" in t.split('needs "rituals"')[1]
    sk = skeleton(t)
    assert required(t) == {"hp", "spells", "invocations"} and "[<1 invocation name>]" in sk["invocations"]
    assert "(only if Book of Ancient Secrets is learned in this record)" in sk["rituals"]
    assert "chosen" not in sk and "tome" not in sk  # no Pact Boon choice at 5th level


def test_bard_9_to_10_magical_secrets_count_in_spells_known() -> None:
    ch, levels = _auto("bard")
    s9 = built(ch, levels[:8])
    t = create.level_up_options(s9)
    assert text_of("magical-secrets-1") in t and "- Expertise: " in t
    assert "[feature.bard-expertise-2] Expertise: choose 2" in t
    # the Bard table: Spells Known 12 at 9th, 14 at 10th, and the two chosen "are included in the number"
    assert 'they "are included in the number in the Spells Known column", which goes 12 -> 14' in t
    assert "No other new spells known at this level (the new Spells Known are the Magical Secrets below)" in t
    assert "New cantrips: choose 1" in t  # Cantrips Known 3 -> 4
    secrets = t.split("Magical Secrets: choose 2 spells from any class, of level 5 or lower or a cantrip.")[1]
    assert "Cone of Cold" in secrets and "Fireball" in secrets and "Fire Bolt" in secrets  # any class; a cantrip too
    assert "Chain Lightning" not in secrets and "Disintegrate" not in secrets  # 6th level: no 6th-level slots yet
    listed = {n.strip() for line in secrets.split("== Level record")[0].splitlines() if line.startswith("    ")
              for n in line.split(": ", 1)[1].split(",")}
    assert not listed & set(s9["spellcasting"]["known"] + s9["spellcasting"]["cantrips"])  # spells already held aren't offered
    sk = skeleton(t)
    assert required(t) == {"hp", "choices", "cantrips", "secrets"} and "replace" in sk and "spells" not in sk
    # Lore's Additional Magical Secrets at 6th level do NOT count against the spells known
    t6 = create.level_up_options(built(ch, levels[:4]))
    assert 'they come on top of the new spells the Spells Known column gives' in t6 and "don't count against the number of bard spells you know" in t6
    assert {"spells", "secrets"} <= set(skeleton(t6))


def test_lore_bard_2_to_3_three_skills() -> None:
    ch, levels = _auto("bard")
    s2 = built(ch, levels[:1])
    t = create.level_up_options(s2)
    assert "Subclass gained now: Lore (Bard College)" in t
    assert "[feature.bonus-proficiencies] Bonus Proficiencies: choose 3" in t and text_of("bonus-proficiencies") in t
    mine = [x.rsplit(" ", 1)[0] for x in s2["skills"].split(" (* proficient")[0].split(", ") if x.endswith("*")]
    refused = t.split("Already proficient (refused, they would be gained twice): ")[1].split("\n")[0]
    assert refused == ", ".join(mine)
    assert "[feature.bard-expertise-1] Expertise: choose 2" in t and "Only a proficiency the character has, without expertise yet." in t
    assert '"feature.bonus-proficiencies": <3 picks>' in skeleton(t)["choices"]
    assert "Cutting Words: " + text_of("cutting-words") in t


def test_a_dwarf_and_a_draconic_sorcerer_get_the_extra_hit_point() -> None:
    sorc, levels = _auto("sorcerer")
    t = create.level_up_options(built(sorc, levels[:1]))
    assert "Draconic Resilience: " in t and "Fixed: " in t
    assert "metamagic" in t.lower()


def test_refusals() -> None:
    ch, levels = _auto("fighter")
    s20 = built(ch, levels)
    with pytest.raises(create.Bad, match="is level 20, the highest level"):
        create.level_up_options(s20)
    s19 = built(ch, levels[:-1])
    assert "level 19 -> 20" in create.level_up_options(s19)
    with pytest.raises(create.Bad, match="no build record"):
        create.level_up_options({k: v for k, v in s19.items() if k != "build"})


@pytest.mark.parametrize("cls", sorted(srd.table("Classes")))
def test_every_class_every_level_names_the_fields_of_the_next_record(cls: str) -> None:
    ch, levels = _auto(cls)
    for n in range(1, 20):
        t = create.level_up_options(built(ch, levels[: n - 1]))
        rec = {k: v for k, v in levels[n - 1].items() if v}  # the auto records carry an empty "choices" when there is none
        sk = skeleton(t)
        assert f"level {n} -> {n + 1}" in t
        assert set(rec) <= set(sk), (cls, n, set(rec) - set(sk))
        assert required(t) <= set(rec), (cls, n, required(t) - set(rec))
        for cid in rec.get("choices", {}):
            assert f'"{cid}"' in sk["choices"], (cls, n, cid)
        for cid, _, _ in create.level_sets(cls, n + 1):
            assert f"[{cid}]" in t
        assert "HOUSE RULE (the owner's" in t


def test_biggest_output() -> None:
    sizes = {}
    for cls in srd.table("Classes"):
        ch, levels = _auto(cls)
        for n in range(1, 20):
            sizes[(cls, n + 1)] = len(create.level_up_options(built(ch, levels[: n - 1])))
    worst = max(sizes, key=sizes.get)
    assert sizes[worst] < 40000, (worst, sizes[worst])


def test_beguiling_influence_house_rule_is_shown_only_when_it_applies() -> None:
    inv = ["Armor of Shadows", "Beast Speech"]
    free = LOCK | {"choices": LOCK["choices"] | {"class.proficiencies.1": ["Arcana", "History"]}}
    t = create.level_up_options(built(free, [FIXED | {"spells": ["Comprehend Languages"], "invocations": inv}]))
    assert "- Beguiling Influence (needs: none): " + text_of("eldritch-invocation-beguiling-influence") in t  # nothing added
    assert "Player's Handbook" not in t and "invocation_skills" not in t
    t = create.level_up_options(built(LOCK, [FIXED | {"spells": ["Comprehend Languages"], "invocations": inv}]))
    assert "the character already has Deception, so the player chooses 1 other skill instead" in t
    offered = t.split("not Deception or Persuasion): ")[1].split(".\n")[0].split(", ")
    assert "Nature" in offered and not {"Deception", "Persuasion", "Arcana", "Insight", "Religion"} & set(offered)  # held ones left out
