# Source of this data

The JSON files here are copied unchanged from the 5e-bits project:
https://github.com/5e-bits/5e-srd-api, commit `ecfddae2f1738d7f917154a81fbce04aca56cdd1`,
path `packages/5e-database/src/2014/en`. The project's code is under the MIT licence (`LICENSE-5e-bits.md`).

The content is the System Reference Document 5.1:

This work includes material taken from the System Reference Document 5.1 ("SRD 5.1") by Wizards of the Coast
LLC and available at https://dnd.wizards.com/resources/systems-reference-document. The SRD 5.1 is licensed
under the Creative Commons Attribution 4.0 International License available at
https://creativecommons.org/licenses/by/4.0/legalcode.

Known gap: the Acolyte's prayer book (or prayer wheel), 5 sticks of incense and vestments are missing from its
starting equipment. `dm/create.py` adds them (`ACOLYTE_PRAYER`, `ACOLYTE_ITEMS`); the data here stays unchanged.

Gap-fill: `dm/srd/gapfill/5e-SRD-Rules.json` holds rules sections the dataset lacks, taken word for word from the
official SRD 5.1 PDF (`SRD_CC_v5.1.pdf`, https://dnd.wizards.com/resources/systems-reference-document), with only
the PDF's text-extraction artefacts (spacing, split words, broken hyphens, ligatures) repaired. `dm/srd.py` `table()`
adds these entries to the dataset's (an index that is already in the dataset raises). Each entry has a `source` field.
- Beyond 1st Level, with the Character Advancement table (p.56)
- Class passages the dataset lacks, for the "class" lookup. An entry with `for` (a class or subclass index) and `after`
  (the heading of the block it follows in the class lookup; "" = first) is printed there in place, and is also found
  by its own heading:
  - Hit Points, Proficiencies and Equipment, one entry each for all 12 classes (Barbarian p.8, Bard p.11, Cleric p.15,
    Druid p.19, Fighter p.24, Monk p.26, Paladin p.30, Ranger p.35, Rogue p.39, Sorcerer p.42, Warlock p.46, Wizard p.52)
  - Wizard: Learning Spells of 1st Level and Higher (p.53), Your Spellbook (pp.54-55)
  - Warlock: Eldritch Invocations, the paragraph on prerequisites (p.48); Fiend Expanded Spell List (p.50); Your Pact
    Boon (p.51)
  - Paladin: Tenets of Devotion (p.33), Breaking Your Oath (pp.33-34)
  - Druid: Beast Shapes table (p.20), Sacred Plants and Wood (p.22)
  - Cleric: Destroy Undead table (p.17)
  - Sorcerer: Flexible Casting, Creating Spell Slots table (p.43); Draconic Ancestry table (p.44)
- Magic items: `dm/srd/gapfill/5e-SRD-Magic-Items.json` has "Shield, +1, +2, or +3" (p.242), which the dataset lacks
The SRD's Multiclassing (pp.56-58) and Feats (p.75) sections are left out on purpose: the game doesn't use those
optional rules (owner, 2026-10-11), and the DM's prompt says so.

Corrections: `dm/srd/corrections/5e-SRD-<Table>.json` holds the places where the dataset differs from the SRD 5.1 PDF.
`dm/srd.py` `table()` applies them after loading and gap-fill. Each is {"index", "source", "set": {path: value}}; a path
is dotted and may index a list by number ("class_specific.invocations_known", "spellcasting.info.4.desc"). An index
that is not in the table, or a dict field that does not exist, raises. The text is the PDF's, word for word. Entries
(PDF page):
- Levels: Warlock levels 4 and 6, Invocations Known 2 and 3 (the dataset had 3 and 4) (p.46)
- Subclasses: Life Domain, Guardian of Faith added to the domain spells at Cleric level 7; the introduction gets the
  PDF's examples of gods back (p.17)
- Features, text brought to the PDF's:
  - Rage: the Rage Damage and Rages columns of the table, not fixed numbers (p.8)
  - Frenzy: "appendix PH-A" (p.9); Retaliation: "melee weapon attack" (p.10)
  - Divine Domain and its four improvement placeholders: the dataset's non-SRD domain names removed (p.16)
  - Destroy Undead at CR 1/2, 1, 2, 3, 4: "as shown in the Destroy Undead table" (p.17)
  - Martial Arts, Ki, Unarmored Movement (both): "the Monk table" for "Table: The Monk"; "two-handed" (pp.26-27)
  - Divine Sense: the Count Strahd example (p.30); Lay on Hands: "level × 5" (p.31)
  - Roguish Archetype and its three improvement placeholders: a non-SRD sentence removed (p.40)
  - Otherworldly Patron and its three improvement placeholders: the dataset's non-SRD patron names removed (p.46)
  - Mystic Arcanum (6th to 9th): "6th-level" for "6th- level" (p.48)
- Classes: Druid Spellcasting Focus, 'see "Equipment"' for "see chapter 5" (p.20); Paladin (p.31) and Wizard (p.52)
  spellcasting text, a space after a hyphen removed
- Spells (`5e-SRD-Spells.json`, 80 of the 319 spells; pp.105-193): all 319 were compared with the PDF field by field
  (casting time, range, components and material, duration, text, higher levels, level, school, ritual, class lists;
  the 7 spells with tables also cell by cell). The corrected values are copied from the PDF text by script, only
  extraction artefacts repaired. What changed:
  - Casting time with its trigger: Counterspell, Feather Fall, Hellish Rebuke, Shield; Plant Growth "1 action or 8 hours"
  - Range with its area ("Self (15-foot cone)" and the like) for 16 self spells; duration for Etherealness,
    Find the Path, Forbiddance, Glyph of Warding, Prestidigitation, Project Image, Symbol, Thaumaturgy, Weird
  - Material component: Confusion, Create or Destroy Water, Detect Thoughts, Enlarge/Reduce, Feather Fall, Fire Shield,
    Hold Monster, Illusory Script, Magic Mouth ("10 gp"), See Invisibility, Shatter, Stone Shape, Water Breathing
  - Text reworded or with a missing or extra sentence: Blight, Compulsion, Conjure Animals, Contingency, Create or Destroy
    Water, Dominate Beast (the upcast tiers), Druidcraft, Entangle, Find Familiar, Find Steed, Fire Shield, Floating Disk,
    Goodberry, Hallow, Heroism, Hideous Laughter, Hold Monster, Legend Lore, Longstrider, Magic Circle, Magic Mouth,
    Mending, Moonbeam ("1d10"), Phantasmal Killer and Weird ("end of"), Polymorph, Prestidigitation, Reincarnate ("d100"),
    See Invisibility, Shatter, Shillelagh, Speak with Animals, Spike Growth, Spiritual Weapon, Symbol ("10d10"),
    Thaumaturgy, True Polymorph, Wall of Fire (a repeated sentence removed), Water Breathing, Zone of Truth
  - Level, school or class list: Arcane Eye, Create Food and Water, Divination, Faerie Fire, Meld into Stone (classes);
    Mass Cure Wounds and Mass Heal (evocation), Revivify (necromancy)
  - Animal Friendship, At Higher Levels (p.115): the dataset lacks it. The PDF's own text is damaged ("one additional
    beast t level above 1st."); repaired to "one additional beast for each slot level above 1st." by the owner's decision
    (2026-10-12), the wording of the other spells' upcast lines. The entry has no `higher_level` field, which a
    correction can't add, so the paragraph is the last entry of `desc` (as is Heroism's, p.154)
  Left as the dataset has it (formatting only): ability names in lower case in the spell text ("wisdom saving throw"),
  the material's capital letter and full stop, "25gp" for "25 gp", markdown for run-in headings and tables, bullets
  as "- ", and "Concentration" kept as the `concentration` flag (the dataset's duration reads "Up to 1 minute").
- Magic Items (`5e-SRD-Magic-Items.json`): Belt of Dwarvenkind, the bullet "You have darkvision out to a range of 60
  feet." (p.211); Deck of Many Things, the Avatar of Death stat block (p.217) after the Skull card, and the cards the
  dataset stops short of: Star, Sun, Talons, Throne, Vizier, The Void (pp.216-217)
Not corrected: the `aura-improvements` feature (Paladin Aura of Protection levels), which the dataset invented and the
PDF does not have; and the eldritch invocations' prerequisites, which come from the dataset's `prerequisites` and are
printed in the PDF's wording by `dm/lookup.py` (checked against pp.48-50).

The "class" lookup (`dm/lookup.py`) builds the class table from the dataset's Levels rows with the PDF's column headings
(Features names come from the dataset), and a subclass's spell list from its `spells` and the PDF's headings
(`_SUBCLASS`).

The gap-fill is under the same licence and attribution as the rest of the SRD content here. The PDF's legal page asks
for this attribution statement:

This work includes material taken from the System Reference Document 5.1 ("SRD 5.1") by Wizards of the Coast
LLC and available at https://dnd.wizards.com/resources/systems-reference-document. The SRD 5.1 is licensed
under the Creative Commons Attribution 4.0 International License available at
https://creativecommons.org/licenses/by/4.0/legalcode.
