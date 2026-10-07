# 09 — Adversaries

> This chapter governs everything that opposes the player character in a fight and much of what it
> meets outside one: what a creature fundamentally *is* (its **archetype**, a manufacturer whose one tag set
> drives the evidence a fight with it counts toward, the loot pool its defeat opens, the powers a Devourer
> could take from it, how it behaves, and what it categorically cannot be or do); how dangerous it is
> without character levels (its **threat band** T1–T5, read against the PC's power band P1–P5); how an
> archetype plus a band, a role and a variant produce a complete, sealed stat block deterministically; how
> the engine runs it (flat first-match **behavior lists**, morale, parley, yield and retreat conditions);
> how the engine tells the player, before the fight, how that fight is likely to go
> (**`threat_advisory`**, a precise estimator validated against chapter 06's simulation, feeding chapter 07's
> lethal warning); how a lone character's encounters are budgeted and diversified; what a victor does with
> a defeated PC and how it remembers; and what the narrator may say instead of numbers. It ships a 63-archetype
> library, a 68-power library, 40 behavior lists, and a 123-adversary bestiary from rat swarms to elder
> dragons, every number derived by one procedure and every advisory checked by simulation. It is shaped by one
> finding repeated across the research: in a solo game the danger is in *how many* and *what kind*, not in how
> big the numbers are, and an AI referee is reliable at classifying a creature onto closed lists and unreliable
> at choosing its actions, its mercy, or its difficulty. So the creature is data, its turn is a lookup, its
> difficulty is computed and shown before the first blow, and the only thing left to the narrator is the
> fiction.

**Reading this chapter.** The Rules are in twelve parts: what an adversary is (09.1), archetypes (09.2),
threat bands and the band tables (09.3), building a stat block (09.4), powers (09.5), the advisory (09.6),
behavior (09.7), encounters (09.8), defeat, lethality and memory (09.9), knowledge and tells (09.10), what a
defeat produces (09.11), and the bestiary (09.12). Procedures PR-09-1…PR-09-8, Tables T-09-1…T-09-16, worked
examples WE-09-1…WE-09-9. The machine-readable companions are `data/archetypes.yaml` (archetypes, band tables,
powers, resisted-effect degree tables), `data/adversaries.yaml` (the bestiary, with an owner-block for 13),
`data/behaviors.yaml` (behavior lists, the closed predicate and macro vocabularies, encounter tables). All three
are **generated** by `rules/_process/simulation/09-gen_data09.py` from authored modules (`09_data_*.py`) and
validated against every canonical id they cite; the simulation is `09-adversary-sim.py` (output and summary
beside it). Numbers marked *(06 owns)*, *(07 owns)* and so on are consumed from those chapters unchanged.

---

## Design intent

**Goals served.** Goal 1 (the player feels free to try any creative idea): every adversary is a set of
named, citable facts — a weak spot, a `cannot` list, tells, a morale clock, a parley row, a counter to its
resistance — so a clever plan always has something real to grab (a lever, a called shot, a Talk that ticks
morale, a fire that stops a troll's healing), and an encounter that is going badly always has an exit whose
price is stated before the player commits. Goal 2 (the AI responds correctly): the DM never picks a
creature's numbers, its target, its action, its mercy or its difficulty. It classifies (which archetype,
which band rung, which role, which variant, which flag is true), and the engine computes, looks up and rolls.

**What the research said, and what this chapter does with it.**
- *Archetypes are manufacturers* [R3 §6 #14; R3 §09.1–09.3]. Borderlands' manufacturers express identity
  "through mechanics, not just flavor text"; Risk of Rain 2 keeps some items away from enemies and some
  powers uncopyable by tag. Here one archetype entry carries the creature tags that gate loot (08.3.4), the
  deed tags it practices, the absorbable pool and its exclusions (04.10), its behaviors, and a `cannot` list
  of categorical impossibilities (a ghost cannot be grappled; a fey noble cannot speak a direct lie). → 09.2.
- *Threat band is item level* [R3 §09.2; R3 §08.4 (Diablo II alvl)]. The band is the tier cap of what it
  drops, the challenge band of the evidence it yields, and the row of its stat line. → 09.3, 09.11.
- *A single difficulty scalar fails; count and action economy must be budgeted separately* [R2 #11; R2 §09
  "CR ignores action economy"; R1 #7]. The advisory is computed from every participant's own line, with the
  count, the turn order, the mob numbers step and the morale clock in the arithmetic, not from a summed
  rating. → 09.6.
- *Solo play needs its own body-count curve* [R1 §06 "3–12 opponents would be lethal against a single PC";
  06.10]. Chapter 06 found the curve; this chapter adopts it as the encounter budget (T-09-10) and fields
  crowds as mobs. → 09.8.
- *Challenge through kinds of problem, not stat inflation; every build has a structural weakness*
  [R1 #8; R2 #12 (Jason vs swarms; the Alexandrian on arms races)]. Encounters record which of eight
  challenge axes they present and the engine rotates toward the stalest (09.8.5); resistances are puzzles
  with named counters, not bigger numbers (09.4.4, 09.6.4).
- *Out-of-band foes must be telegraphed* [R2 §09 (Underworld's level-200 enemy); BRIEF §4]. Any adversary a
  band or more above the PC shows a band tell at first sight; two bands above, the advisory is lethal and
  chapter 07's warning fires. → 09.6.6.
- *Death is real but telegraphed; defeat usually changes the situation* [BRIEF §4; R6 §C.3 C-R5; R6 C-19
  (Kenshi, Mount & Blade: the victor's nature decides); R6 C-20 (Nemesis)]. Every archetype carries a
  `lethal_context` default and one of chapter 07's seven defeat dispositions, a captive fate, and the closed
  conditions under which it switches to `kill`; a victor remembers (09.9.3).
- *Threat actors driven by engine processes, never by a narrator who would rather be nice* [R4 §6.2 item 3;
  R4 §9 09 items 1–4]. Behavior is a flat first-match priority list over a closed predicate vocabulary;
  morale is chapter 06's clock; the DM chooses nothing for an adversary. → 09.7.
- *Bands are a ≤5-rung ladder classified from the creature's nature, never from title, location, hostility
  or dramatic importance alone* [R4 §6.3 (Story-Engine's guard)]. → 09.3.1.
- *Intelligent tactics beat stat inflation; play monsters with goals, preferred range, retreat conditions,
  what they protect* [R1 §09 (behavior script)]. Every behavior list has an instinct, a parley, a yield and a
  retreat condition (Dungeon World's instinct and moves, made into lookup rows
  [R: https://www.dungeonworldsrd.com/monsters/]). → 09.7.
- *Top-down creature design* [R: https://2e.aonprd.com/Rules.aspx?ID=2874 (Pathfinder 2e builds creatures
  from benchmark tables by level and "roadmaps": brute, skirmisher, soldier, sniper, spellcaster)]. Here a
  band table plus a role produce the line, and Vitality is *solved* so that every adversary of a band is
  worth the same as the band's standard (09.4.4) — the step Pathfinder leaves to designer judgment is made
  arithmetic. 13th Age's mooks and its "large counts as 2, huge as 3" rule
  [R: https://www.13thagesrd.com/monsters/monster-creation/] and Lancer's NPC templates (Grunt, Elite,
  Ultra) [R: https://lancer-faq.netlify.app/] are the precedent for the four variants (09.4.6).

**What this chapter deliberately avoids.**
- *Character levels and a challenge rating.* There is no number that sums a fight. The advisory reads the
  whole encounter and the PC's actual line [C:P2; R2 #11].
- *Hidden adjustment.* Nothing about an adversary changes once a conflict starts except through chapter
  06's state (06.9.7). Difficulty is set before the fight and shown [R1 #9; R4 §6.3].
- *Party-scale encounter math.* Pathfinder's encounter budget assumes four characters and multiplicative bodies
  [R: https://2e.aonprd.com/Rules.aspx?ID=2718]; it is cited only to show why it does not transfer.
- *A creature the AI improvises out of nothing.* An unanticipated creature is still built by PR-09-1 from an
  archetype, a band, a role and a variant (PR-09-2), so it is as computable as the bestiary.
- *Monsters as omniscient counters.* Behavior rows read only state the creature could know (09.7.4)
  [R1 §09 "the GM is a fan, not an adversary"].
- *Extra actions for big creatures.* Every adversary has two actions at every band, fixed by 06.1.2; a dragon
  is dangerous through what its two actions contain (heavy blows, shaped powers, Focus, reactions), never
  through more of them [C:P9; INV-11].

**Rule kinds used here** (00.2.2): `[D]` engine, `[J:flag]`, `[J:enum]`, `[J:rung]`, `[T]` trigger, `[S]`
sealed, `[N]` narration. Every `[J:*]` decision carries a *Worst case* line with its P-B class.

---

## Rules

Rule ids are `09.S.R`. Digest shorthand per 00.1.6.

### 09.1 What an adversary is

**09.1.1 The adversary record.** `[D]` An adversary is an entity of kind `adversary` (00.6.1) whose record
extends 00.6.2's `Adversary` shape with the fields of T-09-14. Every field is computed by PR-09-1 from four
inputs — **archetype** (09.2), **threat band** (09.3), **role** (09.4.2) and **variant** (09.4.6) — plus at
most a handful of named overrides an entry may carry (a level-3 creature tag, a size, which of the
archetype's attacks it uses, powers added or dropped, pool abilities, gear). The record is stored in
`data/adversaries.yaml` for the bestiary and in state (`create_entity(kind: adversary, template_id)`) for
each instance met in play; a mob is one entity with a `members` count (06.10.2). An instance keeps its
template id, so the codex, chapter 03's evidence, chapter 08's generator and chapter 04's Taking all read the
same nature [R3 §09.1; 00.6.2].

**09.1.2 Sealed state.** `[S]` An adversary's stat block (attributes, competence, defenses, Vitality, attacks,
powers, Focus, effect DCs, reaction kinds, morale nerve, weak spot, behavior list, disposition switches,
calibration) is **sealed** (00.6.3, 00.6.5). The narrator's permitted slice is, and is only: its name as
perceived; its size; its **tells** (09.10.1: presence, the band tell, wounded, breaking, windup); the shown
descriptors `bloodied` and `down` (06.7.6); its visible conditions; a Windup in progress (06.9.5); its
side's morale omens (06.11.4); the number the PC needs on the die, inside an OFFER (01.7.1); and whatever the
PC has learned (09.10.2), which becomes `available` in the codex item by item. A secret in the narrator's
context leaks [R4 §5.1]; a stat block never enters it.
*Narration may not imply:* any number of the stat block; a resistance, weakness or power the PC has not
perceived or learned; that the creature is weaker or stronger than its tells say.

**09.1.3 Deliberate asymmetries.** `[D]` The opposition is cheaper to run than the PC, by design [R1 §09
(Lancer: NPCs cannot Brace or Overcharge); 07.2.10]:
- **Two actions a turn at every band**, a reaction by band (06.1.1, 06.6.5; 09.3.9). No variant, power or
  ruling adds an action (INV-11; 06.1.2).
- **No push, no fate, no last-chance menu.** An adversary's Focus buys only its listed powers and pool
  abilities (09.5.3); it never pushes a roll (05.6.7 is the PC's). It has no fate (01.16). It uses chapter
  07's short ladder: at 0 Vitality it is defeated (07.2.10).
- **No mastery rung** (06.4.5): its attack severities are listed in its record, which is the same idea as
  data.
- **Its rolls are fortune checks** (01.6.7): the engine frames and rolls them with `offer.choice: auto`.

**09.1.4 Nothing changes mid-fight.** `[D]` Restating 06.9.7 for this chapter's fields: once
`conflict_start` has run, an adversary's record changes only by harm, conditions, positions, the morale
clock, its own powers' declared effects (a solo's phase, 09.7.7; a Shrug, 09.5.1), and reinforcements on a
clock whose omens were rendered. The DM may not re-band, re-role or re-variant a creature, add or remove a
foe, alter Vitality, or have a creature "hold back". A creature met again in a later scene keeps its record
(and its wounds, until chapter 07's recovery for NPCs says otherwise) unless chapter 11 or 09.9.3 has
written a change [R1 §4 T-5; R4 §6.3].

### 09.2 Archetypes: the manufacturers

**09.2.1 One tag set drives four things.** `[D]` An **archetype** (`arch.*`, `data/archetypes.yaml`) is a kind
of creature: wolves and hounds, brigands, barrow-wights, golems, great dragons. Its tag set is read, without
restatement, by four consumers [R3 §6 #14; C:P5]:

| Consumer | Reads | Rule |
|---|---|---|
| Evidence (03) | `creature_tags` (opponent kind), the adversary's threat band (through the advisory word and for conduct-only events, 03.4.3), its `lethal_context` [verification: V2b-002] | 09.11.2 |
| Loot (08) | `creature_tags` (most specific first), `harm_tags`, `evidence_tags`, `org_tags`, `loot.*`, `gear`, `purse` | 08.3.4; 09.11.1 |
| Absorption (04) | `absorbable.pool_gate_tags`, `absorbable.cannot_absorb`, `absorbable.signature` | 04.10; 09.11.3 |
| Behavior (this chapter, 06) | `behaviors`, `morale`, `default_behavior_role`, `mind` | 09.7 |

`evidence_tags` are the deed tags the creature **practices** (a brigand: `deed.martial.blade`,
`deed.guile.ambush`; a lich: `deed.arcane.necromancy`, `deed.lore.arcana`). They are its competence keys
(09.3.2), they open folk-made and practice-themed loot (08.3.4 item 1), and they tell chapter 03 what a fight
with it was *about* when 03 records secondary context. They are never evidence for the PC by themselves:
evidence comes from the PC's own method (00.5.6).

**09.2.2 The archetype record.** `[D]` Every archetype carries the fields of T-09-1, all data, none prose-only
(00.16.4): identity (`creature_tags` most specific first, `harm_tags`, `evidence_tags`, `org_tags`, `mind`,
`speaks` and `tongue`, `size`, `bands` (the lowest and highest band it is fielded at), `roles`); its body
(seven `attribute_rungs`, `trained_defenses`, `armor`, natural `attacks` with severity offsets, `powers`,
`traits` as effect references); its limits (`cannot`); its conduct (`behaviors`, `default_behavior_role`,
`morale {nerve, break_then}`, `reaction`, `reaction_roll`, `pace`); its stakes (`lethal_context`,
`defeat_disposition`, `kill_when`, `captive_fate`, `can_bargain`, `dread`); its voice (`tells`, `weak_spot`);
its outputs (`loot`, `gear`, `purse`, `harvest`, `absorbable`); its knowledge (`lore {deed_tag, rarity}`); and
its place in the world (`encounter {terrain, group, objective_default}`). T-09-2's band tables turn the rungs
into numbers (09.3).

**09.2.3 The library covers every creature branch.** `[D]` Sixty-three archetypes span all nine branches of
the creature facet (00.5.1) and every level-2 tag under them except where one archetype honestly covers two
(T-09-12): beasts 10, folk 14 (human brigands, soldiers, knights, cultists and mages; elves; dwarves; orcs;
goblins; gnolls; lizardfolk; ogres; trolls; true giants), undead 9, spirits 6, fiends 6, constructs 4,
elementals 5, dragons 4, horrors 5. The count is deliberately high: archetypes are *instances* of the nine
low-cardinality families, which are what key hybrid and absorption tables (R3 §09.6). A new archetype is a
data entry in 09's file (or a pre-made setting's owner-block for adversaries, 13), never a new rule.

**09.2.4 Classifying an unlisted creature.** `[J:enum]`
```
### 09.2.4  Which archetype is this creature?                     [J:enum] [D]
Trigger [T]:        a creature is introduced (write-on-mention, 00.6.6) that matches no bestiary entry
                    and no region entry (12.16.12; a pre-made setting's), or a player asks what kind of thing it is (G0)
Loads in:           situation.conflict.*, situation.exploration.*
License check:      none (classification)
Decisions (J):      1. BRANCH [J:enum] the creature facet's nine branches, by data/tags.yaml's definitions
                       (beast: no speech or culture; folk: speech and culture of a living people; undead:
                       the dead made to move or linger; spirit: native spirit, not dead, not fiend; fiend:
                       infernal or abyssal; construct: a made thing given motion; elemental: of a raw
                       element; dragon: dragon or dragon-kin; horror: unnatural, fits no other branch).
                       Tie-break: the branch of what the creature IS, not what it does (a wolf ridden by a
                       goblin is two creatures; a wolf-shaped fire is elemental). Default: horror only
                       when nothing else fits.
                    2. ARCHETYPE [J:enum] among that branch's archetypes (T-09-12), by `summary` and
                       creature tags. Default: the archetype whose creature_tags include the most
                       specific matching tag.
Computation [D]:    the archetype id; PR-09-2 builds the rest.
Stakes:             none
State writes:       entity.archetype; entity.creature_tags (the archetype's, plus a level-3 tag if one
                    matches exactly)
Narration may not imply: a power, weakness or immunity of an archetype not chosen
Worst case (J):     a neighboring archetype of the same branch: the loot pool, absorbable pool and
                    behavior list differ, the band and numbers do not (bands are 09.3.1's). The id is in
                    state; a later contradiction is corrected by 12.3.4 before the creature acts again
                    (class iv). A wrong branch is two rungs of error and is the reason decision 1 comes
                    first with the facet's own definitions.
Examples:           inside: "a hulking thing of stitched corpses" -> horror -> arch.abomination.
                    boundary: "a wolf of living flame" -> elemental (what it is), not beast ->
                    arch.fire_elemental with the presence tell of a wolf.
                    non-example: "the bandit leader is basically a demon" -> a figure of speech; he is folk
                    (arch.brigand), and the player's words create no fact (SG-06).
Anchor:             yes. Intent verbs: identify, classify, what is it, size it up.
                    Knobs: [revision: I-031] (the two enums decide; only these are fixed) targets (one
                    creature; each creature of a mixed group is classified alone), time_cost (none).
Basis:              [00.5.1] [data/tags.yaml creature facet] [R4 §9 09 item 4] [DL-09-02]
```

**09.2.5 What it categorically cannot be or do.** `[D]` An archetype's `cannot` list states, positively and
literally (SG-15), what is impossible for every creature of that kind: a ghost "cannot leave the place it
haunts"; a golem "cannot disobey its command"; a vampire "cannot cross running water by its own power"; a
plant "cannot pursue". Each entry is backed by state wherever it has mechanics: a restriction effect
(`eff.restrict`), a condition immunity (`eff.condition_immunity`), a fact the behavior predicates read, or a
rule of another chapter it cites (06.10.5 for swarms). Three uses:
1. **Gate G4** (00.12.3): a beat whose intent needs the creature to do what it cannot ("I lure the
   ghost out to the road") is impossible for that intent, and the redirect names what *is* possible
   ("it cannot leave the mill; you can leave it").
2. **Behavior.** No behavior row may produce an act on the `cannot` list; the engine refuses the row and
   takes the next (09.7.1).
3. **Recognizable provenance and crisp legality** [R3 §6 #14]: loot and absorbed powers carry the source's
   identity, and a power that would make the source do the impossible is never in its pools.
Immunities that follow from the body (`pow.mindless`, `pow.deathless`, `pow.unliving`, `pow.amorphous`,
`pow.incorporeal`) are written as powers so that they compose through the substrate (00.10) and are listed
once.

**09.2.6 Flags that keep effects on the right side.** `[D]` Three flags, all chapter 00's and 08's, are honored
by every adversary entry [R3 §09.3 (Risk of Rain 2's AIBlacklist and CannotCopy)]:
- `adversary_only` — every `pow.*` power is adversary-only: it never enters a pick, a learning clock, a loot
  pool or a gift. A Devourer takes *abilities* from 04's pool (`ab.abs_*`), never a `pow.*` entry.
- `player_only` — an effect so flagged is never given to an adversary; specifically, no adversary holds any
  effect that would bypass the two keys (07.3.1): there is no "kills outright", "dies at once" or "no
  saving the target" effect in this chapter's data, and chapter 07's edge case reads any such text as S5
  harm against PCs.
- `cannot_absorb` — named per archetype in `absorbable.cannot_absorb`: the pool entries a Devourer may not
  take from it even though the gate matches (a celestial's sight is its god's, not its own).

**09.2.7 Mind.** `[D]` Every archetype has one `mind` from a closed list; it decides which social and mental
rules apply, with no further judgment:

| Mind | Means | Effects bearing `trait.nature.mental` | Talk (parley, intimidate, demand) | Yields when broken (06.11.5) | Reaction roll (12.11.2) |
|---|---|---|---|---|---|
| `mindless` | no will of its own (skeletons, zombies, golems, oozes) | no effect (`pow.mindless`) | G4: there is no one to talk to | never: fearless | no: its behavior list decides |
| `animal` | a beast's mind | yes | Talk is G4 except calming and intimidating by manner (Handle, Presence) | no: it flees or cowers | no: `tbl.09.beast_mood` (09.8.7) |
| `cunning` | sly, hungry, little culture (ogres, ghouls, lesser demons) | yes | yes; its standing starts Hostile in a fight | if it `speaks` | only if `reaction_roll: true` |
| `sapient` | a person or a power with a will | yes | yes | yes | if `reaction_roll: true` |
| `alien` | a mind, but not one like ours (spirits of place, elementals, aberrations) | yes | Talk's reach is capped Limited unless the PC holds a license or fact that bridges it | per its `break_then` | if `reaction_roll: true` |

*Basis:* 06.11.5's state table; 12.11.2 step 4; the `trait.nature.mental` definition in `data/tags.yaml`
("mindless beings are unaffected").

### 09.3 Threat bands (no character levels)

**09.3.1 Assigning a threat band.** `[J:rung]` Every adversary entry in data carries its band; the DM assigns
one only when building an unlisted creature (PR-09-2) or when a pre-made setting adds one.
```
### 09.3.1  Threat band                                             [J:rung] [D]
Trigger [T]:        PR-09-2 builds an unlisted adversary; 13 or 11 adds an entry
Loads in:           situation.conflict.*, situation.exploration.*
License check:      none
Decisions (J):      1. BAND [J:rung] by the creature's NATURE, anchored by who it threatens (T-09-11):
                       T1 rabble — untrained folk, vermin, the walking dead: a trained person handles one
                         easily; numbers make them dangerous. (village thugs; a lone wolf / a goblin skulk)
                       T2 trained — soldiers, hunting beasts, ghouls: an even match for a seasoned fighter,
                         dangerous to a novice in pairs. (a man-at-arms; a dire wolf / a giant spider)
                       T3 elite — knights, ogres, wights, sorcerers: a veteran's match; a novice's death.
                         (an owlbear; a barrow-wight / a sabre-tooth in its den)
                       T4 champion — heroes, trolls, young dragons, demons of name: they end careers.
                         (a troll; a champion of the realm / a hill giant)
                       T5 legend — ancient dragons, liches, demon lords: regions arrange themselves around
                         avoiding them. (an elder dragon; a lich / a frost-giant jarl)
                       NEVER from title, location, hostility or dramatic importance alone: a "bandit king"
                       is the band of what he can do; a frightening scene is not a stronger monster.
                       Tie-break: the lower rung (a wrong high band manufactures a lethal warning; a wrong
                       low band is caught by the advisory, which reads the real numbers). The archetype's
                       `bands` [min, max] bound the choice.
Computation [D]:    T-09-2 and T-09-3 give every number for that band (PR-09-1).
Stakes:             none
State writes:       entity.threat_band (and every number PR-09-1 derives from it)
Narration may not imply: a band other than the stored one (tells are by the stored band)
Worst case (J):     one rung: every number shifts by one row of T-09-2/T-09-3, loot tier cap by 1,
                    evidence challenge band by 1. The advisory (09.6) is computed from the resulting
                    numbers and shown before the fight, so the player sees the consequence before
                    committing (class ii); the band is in state and can be corrected between scenes
                    (12.3.4, class iv).
Examples:           inside: an old soldier turned highwayman -> T2 (trained), whatever his reputation.
                    boundary: a goblin chieftain with a magic sword: the sword is an item (08), the goblin
                    is T2 at most (arch.goblin bands 1-2); his elite variant (09.4.6) is the "chieftain".
                    non-example: "it's the final boss, make it T5" -> drama is not nature; build what it
                    IS, and let 09.6 report how hard it is.
Anchor:             no
Basis:              [00.3.7] [R4 §6.3 (Story-Engine: "never use boss from title, location, hostility, or
                    dramatic importance alone")] [R2 #11] [DL-09-03]
```

**09.3.2 Band competence and attribute rungs.** `[D]` An adversary's numbers are top-down: its band fixes a
**band competence** `c_b` and the value of five **attribute rungs**; its archetype names a rung for each of
the seven attributes (`attribute_rungs`) and which defenses it is trained in (`trained_defenses`).

**T-09-2 Band tables** (`data/archetypes.yaml#band_tables`).

| Band | `c_b` | apex | high | mid | low | feeble | none (mindless mental) |
|---|---|---|---|---|---|---|---|
| T1 | +1 | +3 | +1 | 0 | −1 | −3 | −5 |
| T2 | +2 | +5 | +3 | +1 | −1 | −3 | −5 |
| T3 | +3 | +6 | +4 | +2 | 0 | −2 | −5 |
| T4 | +4 | +8 | +6 | +3 | +1 | −2 | −5 |
| T5 | +5 | +9 | +7 | +4 | +1 | −2 | −5 |

Every value sits inside 00.3.5 and 00.4.3: attributes −5…+10; competence 0…+6; base modifier (apex + `c_b`)
at most +14, reached only at T5 (INV-18). Competence entries are written on the adversary as
`{tag, value: c_b}` for each of its `evidence_tags` and for `deed.martial.unarmed` (its natural weapons), so
00.3.6's lookup works on it like on anyone.
*Why these numbers.* With rung `high` and `c_b`, an attack is +2 / +5 / +7 / +10 / +12 and a Guard 12 / 15 /
17 / 20 / 22 — exactly chapter 06's reference lines (T-06-12), which sit inside 00.3.7's typical
attack/defense modifiers (+0…+2, +3…+5, +6…+8, +9…+11, +12…+14). With rung `mid` and no training, tempo is
10 / 11 / 12 / 13 / 14 — 06.2.2's reference by band. The rungs are the same for every archetype, so an ogre
and an elf at T3 differ only in *which* attributes are high, never in the scale
[R: https://2e.aonprd.com/Rules.aspx?ID=2874 (benchmarks by tier: extreme, high, moderate, low)].

**09.3.3 The standard line.** `[D]` The **standard** of a band is the line an average adversary of that band
fights with. It is chapter 06's reference line with the two changes the full rules require (DL-09-04):

**T-09-3 The standard line by band** (`data/archetypes.yaml#band_tables.standard`).

| Band | Attack | Guard | Vitality | Harm (standard) | Heavy blow | Reduction | Nerve (clock) | Tempo DC | Reaction |
|---|---|---|---|---|---|---|---|---|---|
| T1 | +2 | 12 | 5 | S2 | S3 | 0 | skittish (4) | 10 | none |
| T2 | +5 | 15 | 12 | S2 | S3 | 0 | steady (6) | 11 | Opportunity Strike |
| T3 | +7 | 17 | 18 | S3 | S4 | 1 | steady (6) | 12 | OS + Fend |
| T4 | +10 | 20 | **24** | S3 | S4 | 2 | resolute (8) | 13 | OS + Fend |
| T5 | +12 | 22 | **36** | S4 | S5 | 2 | resolute (8) | 14 | OS + Fend |

The two changes from T-06-12: (1) adversaries of T3 and above **Fend** the PC's first attack each round,
which 06.6.5 states but 06's script did not model; (2) with Fend in, T4 and T5 Vitality are lowered from 26
and 40 to **24** and **36** so that 06.10.6's target still holds: one foe of the PC's own band is beaten 80%
or more of the time with no Focus. Simulated, extended model with Fend, 8,000 fights a row (section A of the
output):

| One foe of the PC's band | win% / Staggered% | Word |
|---|---|---|
| P1 vs T1 | 100 / 0.1 | trivial |
| P2 vs T2 | 99.9 / 0.7 | trivial |
| P3 vs T3 | 99.4 / 4.7 | easy |
| P4 vs T4 (Vitality 24) | 87.8 / 42.8 | fair (26 would give 81.6 / 53.5: hard) |
| P5 vs T5 (Vitality 36) | 80.2 / 58.2 | hard (40 would give 73.6 / 65.4) |

Both values are inside 00.3.7's envelope (T4 20–32, T5 32–60). Harm severity values are 00.3.11's
(1 / 3 / 5 / 8 / 12) and are never changed by this chapter.

**09.3.4 Defenses.** `[D]` Every adversary stores Guard and all seven attribute defenses (06.4.1; 01's
request):
- `Guard = 10 + Agility + c_b + edge` (edge +1 for a carried shield; 06.4.1's guard tag is its natural
  weapons or its weapon, at `c_b`);
- `defense[attr] = 10 + attribute + (c_b if attr is in trained_defenses else 0)`;
- `tempo = 10 + Wits` (06.2.2; adversaries are not trained in `deed.martial.tactics.reading` unless their
  entry says so, which none in the bestiary does: alert creatures have a high Wits rung instead).
Defenses are stored numbers (`defenses` in T-09-14), read sealed by `frame_check`; status from conditions
applies on top (00.3.5).

**09.3.5 Attacks and severity.** `[D]` Each archetype lists its natural attacks; each attack has a verb
(Strike, Grapple or Force), the attribute it uses, the bands it reaches (06.3.2), harm tags, a **severity
offset** in rungs from the band's standard harm, and optionally `heavy`, a `shape` (06.8), a wound `site`
(07.2.4) and riders (powers that apply on a hit, 09.5). An attack's:
- **modifier** = rung(attribute) + `c_b` (the record stores it);
- **severity** = the band's standard harm + offset, or, for a `heavy` attack, the band's heavy-blow
  severity + offset (T-09-3), clamped S1–S5;
- **windup**: true for every heavy attack, every attack whose severity is S4 or more, and every shaped
  attack (06.9.5; the engine enforces it regardless of the flag);
- **action cost**: 1 (a heavy blow's price is its Windup on an earlier turn, 06.9.5);
- **site**: where its wounds land (07.2.4) when the attack always lands in one place (a lance in the body,
  a hamstringing glaive in the leg); otherwise 07's site roll.

**09.3.6 Reduction.** `[D]` From the archetype's `armor` (T-09-5b), capped at 4 (07.2.2):

| Armor | T1 | T2 | T3 | T4 | T5 | `no_gaps` |
|---|---|---|---|---|---|---|
| natural: none | 0 | 0 | 0 | 0 | 0 | — |
| natural: hide (thick skin, scale, chitin, bark) | 0 | 1 | 1 | 2 | 2 | yes |
| natural: plate (stone, iron, carapace) | 1 | 2 | 2 | 3 | 3 | yes |
| worn: from its gear (padded, leather or hide 1; mail, scale or brigandine 2; plate 3) | by gear | | | | | no |

Natural armor is `no_gaps`: 06.4.10's called shot at the gap does not bypass it. Worn armor has gaps.
Reduction applies to `harm.physical` only (06's T-06-11); elemental harm goes around it.

**09.3.7 Size and pace.** `[D]` Size is from the archetype or the entry (06.3.10's six rungs: tiny, small,
medium, large, huge, colossal); it sets reach, engagement capacity and grapple scale (06's table). Pace is
06.3.3's `speed`: 1 by default; 2 for runners and fliers (wolves, cats, raptors, fire elementals, hellbeasts);
0 for things that cannot move (a rooted creeper: Move is G4 for it); a creature with `pow.flight`,
`pow.swimmer`, `pow.climber` or `pow.burrower` moves in that mode (`slot.movement_mode`).

**09.3.8 Focus and effect DCs.** `[D]` An adversary's **Focus** is its special budget, spent only on its
powers and pool abilities (09.5.3): base by band 0 / 1 / 2 / 3 / 4, +1 elite, +2 solo, +1 for the `caster`
role, 0 for minions. Focus does not recover during a conflict; an adversary met again in a later scene has
its full Focus. Its **effect DC** for each attribute its powers name (`effect_dc_source`) is
`10 + attribute + c_b` (00.3.8), stored per attribute in `effect_dc` (05's request d).

**09.3.9 Reactions.** `[D]` By the adversary's **effective band** (its band, +1 for an elite), following
06.6.5: T1 none; T2 one reaction, Opportunity Strike only; T3 and above one reaction, Opportunity Strike or
Fend (Fend spent on the first attack against it each round from the attacker with the highest modifier it
has seen, 06.6.5). A **solo** has Opportunity Strike and Fend at any band; a **minion** and every **mob**
have none (06.10.2). An archetype may set `reaction: false`. Reaction *abilities* an adversary holds by id
(05) compete for the same one reaction.

### 09.4 Building a stat block

**09.4.1 Archetype + band + role + variant → stat block.** `[D]` PR-09-1 is the only way an adversary's
numbers come to exist, for the bestiary and for every creature improvised in play (PR-09-2). The DM supplies
four classifications and the engine does the rest. The data generator runs the same procedure, so every
bestiary entry is reproducible from its four inputs plus its listed overrides.

**09.4.2 Roles.** `[J:enum]` + `[D]` A **role** is how a creature fights: it picks the primary attack, the
default behavior list where the archetype names several, and chapter 06's default-behavior family when no
list applies. Roles do not change the band's scale; numbers stay budget-neutral through the Vitality solve
(09.4.4) [R: https://2e.aonprd.com/Rules.aspx?ID=2874 (roadmaps); R1 §06 (Lancer's NPC templates);
R3 §09.4 (GW2: no encounter requires a role of the PC)].

**T-09-4 Roles.**

| Role | Fights by | Primary attack | 06's default family | True only when… / false for… |
|---|---|---|---|---|
| `soldier` | holding a line, steady blows | its primary melee attack | melee | its strength is trained, even fighting; not when it relies on one huge blow (brute) or on range (archer) |
| `brute` | heavy blows behind a Windup, absorbing harm | its primary attack; its heavy attack is the threat | melee / beast | it is big and hits like a falling tree; Guard tends low, Vitality high |
| `skirmisher` | speed, hit-and-withdraw, flanking | its primary attack | melee / beast | it moves more than it stands; pace 2 is common |
| `archer` | range and cover | its first ranged attack | ranged | it would rather shoot than close |
| `caster` | workings from range | its attack working | ranged | its threat is magic; it carries pool abilities and +1 Focus |
| `controller` | conditions, holds, terrain | its primary attack (often a Grapple) | melee / beast | its threat is what it does to your options, not your Vitality |
| `leader` | making its side better | its primary attack | melee | it rallies, commands and is its side's morale anchor (06.11.2) |
| `lurker` | ambush from hiding | its primary attack | beast | it strikes from concealment and leaves fair fights |
| `swarm` | many tiny bodies (06.10.5) | its primary attack, one roll per engaged Guard | mob | it is a swarm or a mob of tiny things |

*Decision* `[J:enum]` (improvised creatures only): the role whose "true only when" fits the creature's
fiction; tie-break: the archetype's first listed role. *Worst case (J):* a neighboring role: a different primary
attack and default list; the numbers are re-solved to the same band budget, so the fight is no harder or
easier than the band says, only different in shape (class i).

**09.4.3 Powers and the power premium.** `[D]` An adversary's **powers** are its archetype's plus any its
entry adds (09.5). A power that adds threat beyond the attack line carries a **premium** (T-09-6): 0.06 for
each rider, offensive action or aura; 0.03 for each lesser power (pack tactics, shield wall, frenzy, ambush,
blink, glamour, mend, rally, call, drag, Shrug, second wind); 0.10 for a summoning; 0.04 for each pool ability
held; total capped at 0.40. Movement modes, senses and bodily immunities carry none: their worth is
situational and they are the creature's identity, not its weight. Resistances and regeneration carry none
either, because they are handled as counters (09.4.4).

**09.4.4 The Vitality solve: every adversary of a band is worth the band.** `[D]` Vitality is not chosen.
The engine computes the **harm ratio** that one standard adversary of the band inflicts on the reference PC
of the same band (PR-09-4, the advisory's estimator: expected harm taken before the foe falls or breaks,
over the PC's Vitality), divides it by `1 + premium`, and takes the Vitality, inside the band's envelope
(00.3.7: T1 2–5, T2 6–12, T3 12–20, T4 20–32, T5 32–60), whose harm ratio is nearest that target
(log-distance; ties to the lower). So a dodgy skirmisher with Guard 17 at T2 has less Vitality than a
lumbering brute with Guard 13, and both are worth one T2 standard; a creature with three riders has less
Vitality than a plain one. Resistance and regeneration are **not** counted in the solve: Vitality is solved
as if the PC holds the **counter** (silver, a magical property, fire, acid, a blunt weapon), and the advisory
(09.6.4) reports how much harder the creature is when the PC does not. Resistances are puzzles with a named
answer, not weight [R2 #12; DL-09-05].

**09.4.5 Severity compensation.** `[D]` If the solve lands at the envelope's floor and the creature is still
stronger than the band by more than half again (fidelity > 1.5; at T1 > 2.0), its primary attack and its
non-shaped heavy attack drop one severity rung and the solve runs again; if it lands at the ceiling and is
weaker by more than a third (fidelity < 0.67; at T1 < 0.5), they rise one rung. At most two steps. The
record keeps `calibration {premium, solved_vitality, fidelity, severity_compensation, line}`. Across the
123-entry bestiary, 11 entries took one compensation step (nine up, two down) and every entry's
final fidelity lies within
0.67–1.5 (T1: 0.5–2.0) (`09-gen_data09-output.txt`).

**09.4.6 Variants.** `[D]` One template, four uses [R: https://www.13thagesrd.com/monsters/monster-creation/
(mooks; large ×2 and huge ×3); R: https://lancer-faq.netlify.app/ (Grunt, Elite, Ultra templates);
R1 §09 (Sly Flourish: double a monster's health and call it an elite)]:

**T-09-5 Variants.**

| Variant | Vitality | Reaction | Nerve | Focus | Gains | Use |
|---|---|---|---|---|---|---|
| `minion` | ½ of the solved Vitality (min 1) | none | one rung lower (steady → skittish, resolute → steady) | 0 | — | the body of a mob (06.10.2), an escort, a crowd |
| `standard` | the solved Vitality | by band (09.3.9) | the archetype's | by band | — | most foes |
| `elite` | × 2 at T1–T3, × 1.25 at T4–T5 | as one band higher | one rung higher (skittish → steady → resolute) | +1 | usually one added power; a leader is usually elite | a sergeant, a pack alpha, a chieftain |
| `solo` | × 4 at T1, × 3 at T2–T3, × 1.75 at T4, × 1.5 at T5 | Opportunity Strike and Fend at any band | one rung higher | +2 | `pow.shrug`, `pow.second_wind`, a heavy blow (its primary at the band's heavy severity, wound up) if it had none; `beh.09.solo_overlay` before its list | a creature built to be fought alone: the troll under the bridge, the dragon in the hill |

*Why the multipliers fall at the top.* At P1–P3 the lone PC's three actions against two dominate (06.1.1);
at P4–P5 armor and Vitality outgrow unaided output (T-06-13: "the curve steepens at the top"). One multiplier
for every band would make an elite T2 trivial and an elite T5 lethal. The multipliers were fitted so that,
against a PC of its own band with no Focus, an **elite** is one or two words harsher than a standard of its
band and never lethal, and a **solo** is **hard** from T3 up and at the edge of hard at T2 (simulated,
section C of the output, 3,000 fights a row; win% / Staggered%):

| Against P(b), no Focus | T1 | T2 | T3 | T4 | T5 |
|---|---|---|---|---|---|
| standard | trivial 100/0 | trivial 100/1 | easy 99/5 | fair 88/43 | hard 80/58 |
| elite | trivial 100/1 | fair 97/15 | fair 90/36 | hard 74/63 | hard 63/75 |
| solo | easy 99/9 | fair 86/46 | hard 68/68 | hard 43/86 | hard 46/86 |
| solo, with a Focus push each turn | 100/5 | 93/29 | 83/51 | 70/67 | 66/69 |
| elite vs P(b+1) | trivial | trivial | easy 98/14 | trivial 100/1 | — |
| solo vs P(b+1) | trivial | trivial | fair 92/38 | easy 99/4 | — |

(A T1 solo cannot be made harder inside bounded accuracy: a novice's three actions against a band-1
creature's two are decisive. A T1 "boss" is a leader with a mob, 09.8.1.) The 00.3.7 Vitality envelope
applies to `standard` (and to `minion` from below); elite, solo and mob pools exceed it the way a mob's
pooled Vitality already does (06.10.2). This is filed as an amendment to 00.3.7 (Interface requests).

**09.4.7 Mobs and swarms.** `[D]` Chapter 06 owns mobs and swarms (06.10). This chapter's part: a mob entry
is a `minion` (or `standard`) template with `members` 3 or more; its Vitality is pooled (`members ×
per_member`), it has two actions, no reaction, one Guard and one morale clock; its numbers step is 06.10.3's.
A swarm entry carries `swarm: true` and a tiny size; 06.10.5's three differences apply (it engages everyone
in a group to four targets, unshaped attacks harm it one rung lighter, it cannot be grappled, shoved,
flanked or knocked prone). A leader, a champion or anything named is never folded into a mob (06.10.2); the
archetype's `encounter.group` names its usual leader.

**09.4.8 Improvising an adversary.** `[J:enum]` + `[J:rung]` + `[D]` *Anchor: yes.* When play needs a
creature no data holds, the DM classifies and the engine builds (PR-09-2):
```
### 09.4.8  Improvise an adversary                                   [J:enum] [J:rung] [D]
Trigger [T]:        a hostile creature enters a scene with no bestiary or region entry
Loads in:           situation.conflict.*, situation.exploration.*
License check:      none
Decisions (J):      1. ARCHETYPE [J:enum] (09.2.4).
                    2. BAND [J:rung] (09.3.1), inside the archetype's bands.
                    3. ROLE [J:enum] (T-09-4), among the archetype's roles.
                    4. VARIANT [J:enum] minion | standard | elite | solo (T-09-5): true only when the
                       fiction establishes it: a crowd of the same kind -> minion members of a mob; one of
                       many -> standard; the named or leading one of its kind -> elite; a creature that
                       fights alone and is the scene's whole opposition -> solo. Default: standard.
Computation [D]:    PR-09-1 with the archetype's attacks and powers and no overrides; the result is
                    written as an entity of kind adversary with template_id "improvised" and the four
                    inputs; a ruling is logged (signature arch+band+role+variant) so the same creature
                    is built the same way next time (00.15.6).
Stakes:             none
State writes:       entity (adversary) with its full record; ruling ledger
Narration may not imply: any number; any power not on the archetype
Worst case (J):     each decision is bounded by its own rule (09.2.4, 09.3.1, 09.4.2); a wrong variant is
                    at most one word of advisory, and the advisory is shown before the fight (class ii).
Examples:           inside: "a giant one-eyed boar with a broken spear in its side" -> arch.herd_beast, T2,
                    brute, elite (one of its kind, the named one) -> PR-09-1 builds it.
                    boundary: "a pack of ten of them" -> T1 minion, a mob of 10 (06.10.2), no elite unless
                    one is named.
                    non-example: "a dragon, but weak" -> a drake (arch.drake) at T2, not a great dragon
                    at a band below its range: the archetype's bands are its nature.
Anchor:             yes. Intent verbs: there is a creature, a monster appears, what attacks.
                    Knobs: band (rung), role (enum), variant (enum), members (count, for a mob).
Basis:              [PR-09-1] [00.15.6] [R3 §09.1] [DL-09-06]
```

### 09.5 Powers

**09.5.1 The power record.** `[D]` A **power** (`pow.*`, `data/archetypes.yaml#powers`, 68 entries) is an
adversary-only mechanic beyond its attacks. Every power has: `kind` (`rider` on a hit; `action` costing
`action_cost` actions; `passive`; `trigger` on one hook of 00.10.2; `reaction`); `effects` (effect references
into `data/effects.yaml` and contrib blocks, never prose); `cost` (adversary Focus) or `limits {per, uses}`;
`windup: true` for every shaped or heavy power (06.9.5); `shape` where it has one (06.8, T-06-15); `min_band`
where the power is legal only from a band up; `text` (positive, literal, rendered verbatim into the narration
packet: SG-15); and `tell` (what the narrator shows when it is readied or used). The library is closed in the
same sense as the substrate: a new creature reuses a power with parameters before a new power is written
(PR-00-8, "expand before you add"). Resisted powers name a degree table: one of chapter 07's afflictions
(`aff.*`, 07.9.2) or one of this chapter's nine (`tbl.09.knockdown`, `.fear`, `.blast`, `.charm`, `.hold`,
`.daze`, `.drain`, `.push`, `.choke`; T-09-7), each a four-degree table of effect references.

**09.5.2 Pool abilities.** `[D]` An adversary may hold abilities of chapter 05's pool by id (`abilities` in its
record): a sorcerer holds `ab.flame_lance`, `ab.spell_ward` and `ab.counterspell`; a cult priest `ab.wither`
and `ab.drain_life`. It uses them exactly as their entries say, paying their Focus cost from its own Focus,
with its effect DC from 09.3.8 where the ability is resisted and its attack modifier where it is aimed.
`adversary_only` entries of chapter 05 do not exist; `pow.*` powers are this chapter's adversary-only
mechanics and never enter 05's pool, a pick, a learning clock or a loot pool [05 Interface requests (a)].

**09.5.3 Adversary Focus.** `[D]` Focus (09.3.8) is the adversary's special-action budget. A power or ability
with a `cost` spends it; one with `limits` counts uses instead. When an adversary cannot pay, the behavior
predicate `can_pay` is false and its list falls through to the next row (09.7.1). Adversary Focus never buys
an action, a reroll or a bonus (05.6.14).

**09.5.4 Witnessing.** `[D]` When an adversary uses a power, an ability or a movement mode where the PC
perceives it (the PC is a participant in the scene and is not `cond.blinded` toward it, or the power is
audible and the PC could hear it), the engine writes the fact `witnessed.<pc>.<power or ability id>.<adversary
id>` with the scene and the frame id. Three chapters read it: 04's Taking (the PC must have seen the creature
act, 04.10), 05's emulate (a technique witnessed may be emulated, 00.12.4), and 09.10.2 (a witnessed power is
one fewer thing to learn). The narration of the use carries the power's `tell` [04 and 05 Interface requests].

**09.5.5 Focus-emptying powers.** `[D]` A power that drains Focus uses `eff.drain` with units of U(severity),
resisted by Endure with Resolve, and counts toward 05.6.13's cap of 4 Focus lost to drains a scene. A power
that would **empty** the pool (`pow.null_field`) is legal only at threat band 5 (`min_band: 5`), and only
after its tell has been rendered (its Windup, 06.9.5); `pow.focus_leech` (a drain rider) only from band 4.
The generator refuses an entry that breaks either rule [05.6.13; R2 §05].

**09.5.6 What no power does.** `[D]` No power: adds an action (INV-11); kills, petrifies, disintegrates or
removes a PC from play outright (07.3.1: anything that kills goes through Dying and the two keys; text of that
kind is read as S5 harm, 07's Edge cases); prevents the last-chance menu or the exits; changes a PC's
attributes (00.4.3); grants a license to the PC; or acts at depth 2 (a rider is depth 1 and fires no further
hooks, INV-12). A power's harm is a severity on 00.3.11's scale: `BAND` means the band's standard harm and
`BAND+1` its heavy-blow severity (T-09-3), so a dragon's breath is S4 at T4 and S5 at T5, always wound up and
always resisted by Evade for less (`tbl.09.blast`).

**09.5.7 Recharge.** `[D]` Every power's recharge is data (`limits {per, uses}` or a Focus cost), refreshed
on the named boundary's recover phase (00.10.9). "Once per fight" is `per: conflict_end`. A breath weapon
recharges by Windup: it can be used whenever the creature has spent a Windup for it on an earlier turn and
holds the Focus or uses it lists.

### 09.6 `threat_advisory`: how hard is this fight?

**09.6.1 The contract.** `[D]` `threat_advisory(encounter, pc) → trivial | easy | fair | hard | lethal`
(00.17.1 Q5). **Inputs:** every participant of the opposing side with its line (attack modifier, Guard,
current Vitality per member and members, primary severity, heavy severity, reduction, Fend, nerve, tempo DC,
resistance to the PC's harm, regeneration, swarm, leader), all read from state; and the PC's **actual line**
read from state (02's request): its best Strike or attack-working modifier (the frame's computed total with
no levers), the base severity of that attack with mastery (06.4.5), its Guard, its armor reduction, its
**current** Vitality (not its maximum), its tempo modifier, the harm tags of that attack and whether it has a
reaction to Fend with. **Output:** the word, the estimated win and Staggered percentages and the harm ratio,
logged with the encounter; the word only is shown to the player (09.6.5). **Consumers:** chapter 07's lethal
warning (cause `advisory`: the word is lethal) and danger notice (the word is hard) (07.3.3, 07.3.8);
chapter 12's pacing (the push filter of 12.7.4 and the recovery cap of 12.7.5: "fair or easier"); a region's
encounter tables (09.8.3; the world seed's, 12.16.13, or a pre-made setting's); chapter 04's evidence pacing (I-005, 09.8.9).

**09.6.2 The estimator.** `[D]` The word is computed by **PR-09-4**, a closed-form estimate of the fight
chapter 06 simulates, not a lookup of a summed rating. In outline:
1. **Rates.** For each adversary, the PC's expected harm per round against it (three Strikes at 0 / −2 / −4,
   its Fend on the first, its reduction, a swarm's −1 rung, its resistance floor-rounded per outcome) and
   its own expected harm per round against the PC (two attacks at 0 / −2, the PC's Fend on the first attack
   of the most dangerous foe, a heavy blow on alternate turns, a mob's numbers step at its current size), each
   with its variance, by exact enumeration of the d20.
2. **Timeline.** The PC defeats the lowest-Vitality foe first (06's reference policy), member by member for
   a mob, each taking its Vitality divided by the PC's rate against it; a regenerating foe heals its listed
   amount each round unless the PC's attack is its counter.
3. **Morale.** Chapter 06's tick sources are laid on the timeline (first bloodied, each defeat, a leader's
   defeat, half and quarter strength); the side breaks when the ticks reach its nerve; a fearless member
   keeps the side from breaking.
4. **Harm taken.** Each foe deals its rate from the start until it falls (a mob at full numbers until its
   first member falls), truncated at the break, plus its tempo edge (the chance it acts before the PC).
5. **Outcome.** With the harm's mean and variance, the probability the PC is Staggered is
   `1 − Φ((Vitality − 1 − H) / σ)` and the probability it is beaten is the same past Vitality plus 1.75 landed
   blows (`1 − Φ((Vitality + 1.75·h̄ − ½ − H) / σ)`), where `h̄` is the opposition's mean harm per landed blow.
   (The two constants, a one-point Staggered margin and 1.75 blows, were tuned against the simulation:
   `09-estimator-tune.py`; DL-09-09.)
6. **Word** by chapter 06's thresholds (T-06-13): **trivial** win ≥ 99 and Staggered ≤ 3; **easy** ≥ 95 and
   ≤ 15; **fair** ≥ 80 and ≤ 50; **hard** win ≥ 40; **lethal** below.
Every input is state; every step is arithmetic; the same encounter always gets the same word. The estimator
models no Focus, no levers, no terrain and no tactics beyond Fend, which is why it is a **floor**: "this is how
the fight goes for a fighter who just swings" (09.6.7).

**09.6.3 Adjustments.** `[D]` After the estimate, in this order:
- **Companion.** A companion fighting at the PC's side makes the word **one gentler** (06's contract,
  T-06-13 note); never gentler than easy for an encounter estimated hard or worse. It applies only when at
  least one **able** ally is in the fight: conscious; Warm or better, or its contract's hazard covers the
  encounter's stakes; and serving at `band_cap(pc)` (an ally below the cap does not count). **One word at
  most**, whatever the number of allies. **The hard exception:** an encounter estimated hard whose
  estimated win without allies is **below 75** stays hard, shown as "hard, with your companions beside you"
  (16.7.11; T-16-21; DL-16-13) [integration: IR ch.16 to 09].
- **No martial calling.** Not applied: the PC's actual line already carries it (02's request supersedes 06's
  "one row harsher for a PC with no martial calling").
- **Surprise.** If the PC is `cond.surprised` at `conflict_start` (06.2.4), the word is **one harsher**.
Nothing else adjusts it: not the scene's drama, not the PC's past, not the player's mood (06.9.7).

**09.6.4 Counters.** `[D]` A resistance (`eff.harm_resistance`) or regeneration applies in the estimate only
if the PC's attack is not its counter: the resisted harm tags do not cover the PC's attack's harm tags (with
cascade, 00.5.4), the weapon is not silvered and carries no magical property where the archetype's resistance
says "unless", and, for regeneration, the PC's attack is not fire or acid. So a troll is a fair fight for a
champion with a torch and a hard one for the same champion without. Every adversary record stores
`advisory_alone` (its word against a reference PC of each band, counter held) and, where it has a
resistance or regeneration, `advisory_without_counter` and the named `counter`. The lore check (09.10.2)
learns the counter; a player told "hard" who then learns "unless you bring fire" has been given a plan, not a
number [R2 #12 (every build has a structural weakness)].

**09.6.5 When it is computed, and what the player sees.** `[T]` + `[D]` The engine computes the advisory:
(a) when an encounter is framed (`scene_start` with hostiles present, or a hostile creature first perceived);
(b) when the opposition's make-up changes (reinforcements arrive, a member flees or yields, a companion
falls); (c) when the PC asks (G0, out of fiction, free). It is shown out of fiction as one word with the
odds, in the `[WARNING]`/status line formats of 07.3.4 and 12.15: **hard** raises chapter 07's danger notice
(07.3.8), **lethal** raises the lethal warning (cause `advisory`, 07.3.3). Trivial, easy and fair are shown
only on request or in the codex; the narrator voices them through the band tells (09.10.1). The advisory is
computed **before** the first beat of the conflict, so a player always knows how bad a fight is before
choosing to fight it; it is never recomputed to make a fight easier or harder once it has begun (06.9.7), only
re-shown when the make-up changes.

**09.6.6 Out-of-band foes are always telegraphed.** `[T]` + `[N]` When the PC first perceives an adversary
whose threat band exceeds `power_band(pc)`:
- by **one** band: the narration carries one band tell of the adversary's band (T-09-13), chosen by the
  engine, in the same turn — a soldier sees that this one is different;
- by **two or more**: the advisory is lethal for any count (T-09-9 shows no exception: a P1 PC against one T3
  wins 6% of the time), so chapter 07's lethal warning fires at first perception, with the band tell as its
  sign (07.3.4 item 1).
This is a `[T]` on the perception fact, not a DM judgment, and it holds even when the creature has not yet
noticed the PC: the warning is how the player learns that the right move is to leave, hide or parley
[R2 §09 (Underworld); BRIEF §4].

**09.6.7 What the advisory is not.** `[N]` It is not a promise (a fair fight is lost about one time in
twelve); not a difficulty knob (nothing tunes it); not a measure of the PC's whole power (Focus, abilities,
levers, terrain, allies and tactics all make real fights better than the floor: a Focus push on the first
Strike each turn lifts a hard solo's win by 15–27 points, to 83 / 70 / 66 at T3 / T4 / T5, though by the word it
stays hard, 09.4.6 [verification: V2b-001]); and not a scene-builder's target.
Encounters are drawn from places, not built to the PC (09.8.2); the advisory tells the truth about what was
drawn.

**09.6.8 How well the estimator matches the simulation.** `[D]` `09-adversary-sim.py` section D compares the
estimator's word with the Monte-Carlo word (3,000 fights a row, the extended model) on 586 encounters: every
T-06-13 shape; every bestiary adversary alone against the PC bands at, below and above its own; every
resistant adversary without the counter; 38 mixed encounters built from the bestiary (leaders with mobs,
archers behind soldiers, casters with escorts, bosses with retinues); and five different band-1 PC lines
(martial, a caster in melee, a caster with a zero-cost working, the weakest legal character, a heavily armored
one) against six band-1 and band-2 encounters each (02's request). Results are reported in 09.6.9; the
contract with chapter 07 (menu rates by word) is checked in 09.9.5.

**09.6.9 Results.** `[D]` (section D of the output; 3,000 fights per row; constants as tuned by
`09-estimator-tune.py`.)

| Encounters | Rows | Exact word | Within one word |
|---|---|---|---|
| every T-06-13 shape, standard lines | 110 | 92.7% | 100% |
| every bestiary adversary alone, at P(b−1), P(b), P(b+1) | 333 | 91.6% | 100% |
| every resistant or regenerating adversary without its counter | 75 | 86.7% | 100% |
| 38 mixed encounters from the bestiary | 38 | 78.9% | 100% |
| five band-1 PC builds × six encounters | 30 | 93.3% | 100% |
| **all** | **586** | **90.4%** | **100%** |

Confusion (rows: the simulated word; columns: the estimator's):

| sim \ est | trivial | easy | fair | hard | lethal |
|---|---|---|---|---|---|
| trivial | 218 | 1 | 0 | 0 | 0 |
| easy | 13 | 66 | 7 | 0 | 0 |
| fair | 0 | 8 | 52 | 13 | 0 |
| hard | 0 | 0 | 4 | 80 | 9 |
| lethal | 0 | 0 | 0 | 1 | 114 |

The 56 misses split 26 gentler, 30 harsher, and **none is more than one word**. The constants were chosen as
the setting with the most exact words among those whose gentler misses do not outnumber the harsher ones: an
advisory may err toward warning, never toward leniency (R4 §1: the dominant AI-referee failure is the lenient
one). The one simulated-lethal fight the estimator calls hard is a P4 against three T3 (simulated wins 31%):
the warning it gets is the danger notice, and the player still reads "you may well lose this". The largest
systematic miss is harsher: a leader with an equal or near-equal escort at P5 (a vampire count with its spawn,
a frost-giant jarl with a hill giant) is estimated lethal and simulates hard (52–60% wins). The band-1 builds
show the advisory reading the actual character (02's request): against one man-at-arms a martial starter is
*easy* (97 / 14), a caster with a zero-cost attack working *hard* (83 / 50), a caster swinging a staff *hard*
(57 / 71), the weakest legal character *lethal* (32 / 89), a heavily armored starter *trivial* (100 / 0) — the
same encounter, five honest answers.

### 09.7 Behavior: the DM never chooses for an adversary

**09.7.1 Behavior lists.** `[D]` A **behavior list** (`beh.09.*`, `data/behaviors.yaml`, 40 lists) is a flat,
first-match priority list of rows `{when, do, arg, note}` [R4 SG-10; 06.9.1]. On each of an adversary's two
actions, the engine evaluates the rows top to bottom and takes the **first row whose `when` is true** of the
current state and whose `do` is legal; it never skips a true row for a "better" one, never combines rows, and
never chooses where a row leaves a choice (06.9.3's attention picks the target; the engine rolls any tie,
INV-4). Grammar:
- `when` is one predicate or a conjunction (`&`) or disjunction (`|`) of predicates from the **closed
  predicate vocabulary** (T-09-8a: 44 predicates, each defined over state — `bloodied`, `held`,
  `windup_held`, `heavy_ready`, `can_pay`, `target_held_by_self`, `target_unaware`, `ally_engaged_target`,
  `pc_staggered`, `offered_terms`, `insulted`, `light_bright`, `fire_near`, …). No predicate reads anything the
  creature could not know (09.7.4).
- `do` is one macro from the **closed macro vocabulary** (T-09-8b: 32 macros, each a T-06-1 action or a
  power: `strike`, `strike_twice`, `windup`, `heavy`, `grapple`, `use`, `move_engage`, `withdraw`,
  `withdraw_shoot`, `flee`, `yield`, `cower`, `fighting_withdrawal`, `frenzy`, `defend`, `aim`, `reload`,
  `flank`, `screen`, `hide`, `ready`, `rally`, `call_help`, `talk`, `drag_off`, `feed`, `hold_ground`, …).
- A row whose act is illegal now (its power cannot be paid, its attack's bands do not reach, the act is on
  the creature's `cannot` list, a condition forbids the verb) is **false** for this action and the engine
  moves on. The last row of every list is `always`, so every action resolves.
- A macro costing two actions (`strike_twice`, a two-action power) consumes both; `windup` consumes one and
  the list is evaluated again for the second.
Every list also states the creature's **instinct** (Dungeon World's one line of what it wants that causes
problems for others) and three data fields read by other rules: `parley_when`, `yield_when`, `retreat_when`
(09.7.6). The generator rejects any list that uses a predicate or macro outside the vocabularies.

**09.7.2 Which list.** `[D]` First match: (1) the adversary record's `behaviors` (its archetype's list; a
mob's is `beh.09.mob` or `beh.09.swarm`); (2) a solo prepends `beh.09.solo_overlay` (its phase-2 rows and its
Shrug); (3) a side with a `leader` gives every member the leader's rally row if the member's own list has none
(the leader rallies; members do not); (4) chapter 06's default family by `default_behavior_role` (06.9.4)
when an improvised creature has no list. An adversary whose `defeat_disposition` toward the PC is `kill`
(09.9.2) runs the same list; disposition changes what it does to a *defeated* PC (07.6.1), not how it fights.

**09.7.3 Targets.** `[D]` The target is chapter 06's attention order (06.9.3: its objective's named target;
an engaged enemy who harmed it most; the enemy who harmed it most; the nearest, the PC before a companion;
a roll) unless the row names one ("its captive", "the one holding the lantern", "a helpless enemy"). A
behavior row never targets by the narrator's sense of drama.

**09.7.4 Intelligent, not omniscient.** `[J:flag]` A predicate that depends on what the creature knows is
true only when state establishes that the creature could know it: it perceived the thing (a resolved
Observe or passive notice of its own, 01.4.6), was told it (a fact on its side's knowledge, 15), or it is
plainly visible in the scene. *"Could this creature know this?"* True only for a perceived, told, or plainly
visible fact; false for what only the player or the narrator knows (the PC's Vitality number, a hidden
companion, an unspoken plan, the PC's power band). Uncertain → false. *Worst case (J):* a creature acts on
something it could not know: one action of one turn, corrected by 12.3.4 (class iv); the opposite error
makes it act a turn late (class i). [R1 §09 ("smart adversaries must not become omniscient counters"); 15's
knowledge records]. The `mind` sets the *quality* of tactics, and the lists already encode it: mindless lists
have no `flank`, `withdraw` or `talk` rows; animal lists flee when wounded and alone; cunning lists gang up and
prey on the helpless; sapient lists rally, parley, protect their leader and take prisoners; alien lists pursue
their nature.

**09.7.5 Morale.** `[D]` Chapter 06 owns the morale clock (06.11). This chapter supplies, per adversary:
`morale.nerve` (skittish 4 / steady 6 / resolute 8 / fearless — no clock), read from the side's leader, else
its most numerous template (06.11.2); and `morale.break_then`, one of `flee`, `yield`, `cower`, `frenzy`,
`fighting_withdrawal` (06's closed list), which is what each member does on its turn once the side breaks
(06.11.5). Variants shift nerve (T-09-5). `frenzy` is the break of creatures that cannot run from what they
are (zealots, abominations, lesser demons): broken, they stop defending and spend both actions striking the
nearest enemy until defeated; their clock still closes, so their side stops rallying. A side containing a
fearless member that is not broken fights on with that member alone (06.11.5).

**09.7.6 Parley, yield and retreat.** `[D]` + `[J:flag]` Three fields on every list, read by other rules:
- `parley_when`: the state in which a parley Talk (06.11.7) is **not** G4 for this side; elsewhere the
  redirect names the condition ("they would hear you if you showed them the debt is paid"). Robbers, the
  law, bargainers and fey always parley; mindless things and frenzied fiends never.
- `yield_when`: when the side accepts *its own* yield (it surrenders) besides its break row.
- `retreat_when`: when the side leaves the fight short of breaking (06.13.1 b): a lurker after its first
  failed ambush, a caster bloodied and engaged, a territorial beast once the intruder has left.
Whether a recorded fact makes a row's condition true is the `[J:flag]` of 09.7.4. *Worst case (J):* a parley
allowed one round early or late (class iv: the next behavior row corrects it).

**09.7.7 Solo phases.** `[D]` A solo's `pow.second_wind` fires once, the first time it is bloodied, writing
`phase = 2` and rendering its tell in the same turn (06.9.6's obligation applies to it like a Windup). From
its next turn the phase-2 rows of its overlay and list apply (a dragon takes to the air; a lich raises its
dead; a troll stops defending). Phases are declared in data before the fight, so they are state changes the
player was told were possible (the band tell and the archetype's tells), never a hidden escalation (06.9.7).
`pow.shrug` ends one control condition at the start of the solo's turn once a conflict, so a lone boss is
never locked down for a whole fight; 06.7.4's diminishing still applies to everyone [R: https://www.13thagesrd.com/monsters/monster-rules/].

**09.7.8 Villains act like villains.** `[N]` Hostile creatures act on their instinct with real hostility,
inside the player's lines and veils (14, 12.5.6). Narration does not soften a behavior row's result, invent
mercy the list did not produce, or make a foe "hesitate" without a row that says so [R1 §09 ("Content
Guardrail Backlash")]. Mercy comes from state: a morale break, a disposition other than `kill`, an accepted
yield, a parley row.

### 09.8 Encounters for one character

**09.8.1 The body-count curve and the encounter budget.** `[D]` For a lone PC, the number of foes matters more
than their band: a second foe of the PC's own band is about as dangerous as one foe a band higher, and a third
is lethal from P2 up (T-06-13; T-09-9). **T-09-10** turns the curve into a budget: for each PC band, the
largest group of each shape that stays at each word, simulated with the standard lines (section F; extended
model). Encounter tables (10, 13) and the pacing director (12.7.4) read it to know what a "fair fight" looks
like before computing the real advisory:

| PC | Individuals of its band | One band below | Two bands below | One band above | As one mob (its band / one below) |
|---|---|---|---|---|---|
| P1 | 1–2 trivial · 3 easy · 4 fair · 5–6 hard · 7 lethal | — | — | 1 T2 easy · 2 T2 hard | T1: 3–4 easy, 6 fair, 8–12 hard |
| P2 | 1 trivial · 2 fair · 3 lethal | T1: 1–3 trivial · 4 easy · 5–6 fair · 7–8 hard | — | 1 T3 lethal (39/88, the edge) | T2: 3–4 hard, 6 lethal · T1: 6 easy, 8–12 fair |
| P3 | 1 easy · 2 hard · 3 lethal | T2: 1–3 trivial · 4 easy · 5 fair · 6–7 hard · 8 lethal | T1: 8+ trivial | 1 T4 hard · 2 lethal | T3: 3 lethal · T2: 6–8 fair, 10–12 hard |
| P4 | 1 fair · 2 lethal | T3: 1 trivial · 2 fair · 3 lethal | T2: 1–5 trivial · 6 easy · 7–8 fair | 1 T5 lethal | T4: 3 lethal · T3: 3–4 hard, 6 lethal |
| P5 | 1 hard · 2 lethal | T4: 1 trivial · 2 fair · 3 lethal | T3: 1–2 trivial · 3 easy · 4 fair · 5–6 hard | — | T5: 3 lethal · T4: 3 hard, 4 lethal |

Three consequences are rules:
1. **Crowds are mobs.** Four or more foes of one kind are one mob unless named (06.10.2); individuals are
   fielded at most two of the PC's band, three or more only from a band or two below.
2. **A boss is a solo or a leader with a mob, not a pair of equals.** At P4 and P5 two equal-band foes are
   lethal in every simulation (3–4% wins), so champion- and legend-band set pieces are one solo, or one
   elite with lower-band help, or a fight the PC wins with Focus, ground and allies — which the advisory, a
   no-Focus floor, will call hard or lethal and say so [I-011].
3. **A "fair" fight is the default for an encounter the PC is meant to fight; "hard" is the ceiling of a
   fight the place throws at the PC without warning.** Encounter tables are built so that, against a PC of
   the region's band, rolled fights land fair or easier at least two times in three and are never lethal
   without a telegraphed source (a lair, an omen, a reputation) — see 09.8.2.

**09.8.2 Encounters belong to places.** `[D]` + `[N]` In a sandbox the world does not scale to the PC: a
region, a site and a lair have bands of their own (10, 13), and their encounter tables field what lives
there. The advisory tells the truth about what was rolled. What keeps that fair is structure, not tuning:
- **Danger rings.** A region's encounter table is written for a **home band** (its area's ring, 12.16.8, 10.2.4): most rows at the home
  band or one below, a few at one above, and the rows above that are **lairs, not wanderers** — a place
  with a known occupant, reachable only by going there, signposted by rumor and omen (11, 10).
- **Distance and notice.** A rolled encounter begins at the distance the terrain and the watch allow
  (10's encounter distance; 06.3.9), and creatures that have not noticed the PC are not yet hostile: the PC
  may avoid, hide, parley or prepare. A lethal advisory at first perception (09.6.6) is a reason to do so.
- **The mix.** A complication from `tbl.09.complication` (09.8.5) is rolled on encounters the tables mark
  so, to vary the problem rather than its size.
- **The weekly picture.** Across a campaign, a PC who adventures where its band says it should meets
  opposition at about **Δ −1 / 0 / +1 = 30 / 55 / 15 %** of fights, and Δ +2 only as a telegraphed lair it
  chooses to enter. This is the distribution chapter 04's pacing must assume (I-005, 09.8.9).
- **The top ring.** Against a reference PC of band 4, **every** band-5 standard is lethal alone, so a
  home-4 table cannot place a band-5 standard among its home + 1 faces and stay non-lethal; it fields band-5
  **minions** alone there (hard at P4), and a home-5 table fills its home + 1 faces with band-5 solos
  (13.10.3; DL-13-11) [integration: IR ch.13 to 09].

**09.8.3 From a table row to a scene.** `[D]` An encounter row names an archetype's group (or an adversary
id) and a count (`encounter.group` in the archetype: "mob 4–8, leader elite"). The engine: rolls the count
(`tbl.09.group_shape`: d6 1–2 low end, 3–4 middle, 5–6 high end); folds four or more of one template into one
mob (06.10.2) unless the row names them; adds the leader as a separate participant (an elite of the same
archetype) when the group lists one; computes the advisory (09.6) for the PC as it stands; and frames the
scene with the band tells (09.10.1) and, if the advisory is hard or lethal, chapter 07's notice or warning
before the first beat. The DM's part is the fiction of who they are and what they are doing, from the
archetype's tells and instinct.

**09.8.4 Reinforcements.** `[D]` + `[T]` Reinforcements enter only on a clock whose omens were rendered, or by a
behavior row that calls for help (06.2.5). This chapter's template is `clk.09.reinforcements` (countdown, 4,
sensed; +1 each round; `pow.call_kin` ticks it 2; omens mandatory; on completion the group's reinforcements
enter at `band.far` and the side's morale clock falls 2, 06.11.3). Who arrives is the encounter row's group,
rolled again, and the advisory is recomputed and re-shown (09.6.5 b).

**09.8.5 Challenge diversification as data.** `[D]` + `[J:flag]` Every framed encounter records which of eight
**challenge axes** it presents (T-09-15: `axis.numbers`, `axis.toughness`, `axis.reach`, `axis.control`,
`axis.ground`, `axis.objective`, `axis.clock`, `axis.talk`), each a `[J:flag]` against its "true only when"
definition in `data/behaviors.yaml#challenge_axes`. Chapter 12's rotation ledger (12.9.2) keeps when each axis
last appeared; when a table offers a complication, or the pacing director needs one, the engine draws from
`tbl.09.complication` (d12: slick footing, a height, the dark, a hazard, a chokepoint, something else they
want, someone to protect, a clock, reinforcements, they would rather talk, a split position, mixing) and
rerolls a result whose axis is not the stalest available, up to twice [R1 #8 (terrain, intelligent tactics,
outnumbering, objectives, time pressure, mixing); R2 #12]. *Worst case (J) of an axis flag:* the rotation ledger
is one entry off; the next draw is one axis less stale than it could be (class i). The six levers of R1 #8
are all present: terrain (`axis.ground`), tactics (the behavior lists), outnumbering (`axis.numbers`, mobs),
objectives (`axis.objective`, 06.13.2), time pressure (`axis.clock`) and mixing (`tbl.09.mixing`); two are
added for a solo game: `axis.talk` (a fight that can end in words) and `axis.control` (a fight against your
options rather than your Vitality).

**09.8.6 Mixing.** `[D]` A complication result of 12, or a table that says "mixed", rolls the place's table a
second time and combines the two with `tbl.09.mixing` (d8): at each other's throats (three sides); the
aftermath (the winners bloodied, the losers' bodies to harvest); hunter and quarry; allies (one side); a deal
in progress (a parley open with either); captor and captive (a rescue, a ransom or a witness). Each result
states the sides; the advisory is computed per hostile side, and for "allies" over both
[R1 §09 (encounter mixing: "roll twice and combine")].

**09.8.7 Meeting creatures outside a fight.** `[D]` + `[J:flag]` Whether a met creature fights at once is
never the DM's choice:
- **Sapient and cunning creatures** whose archetype has `reaction_roll: true` take chapter 12's reaction roll
  (12.11.2) when the PC first interacts; their behavior list begins when a conflict starts (06.2.1).
- **Animals**, and any archetype with `reaction_roll: false` that is not mindless, roll `tbl.09.beast_mood`
  (2d6: 2–4 hunting, 5–6 territorial, 7–9 wary, 10–11 indifferent, 12 curious; −2 if starving or near its
  young or lair, +2 if offered food, +1 if the PC is downwind and quiet; each modifier a `[J:flag]` citing a
  fact). *Worst case (J):* one flag wrong is a two-point shift: one row of the table, shown in fiction before
  any blow (class i).
- **Mindless creatures** follow their behavior list from first perception: a guard attacks intruders on its
  ground; a horde moves toward the living.
- **Adversaries on a mission** (an objective recorded by 11 or a clock) act on the objective (06.13.2).

**09.8.8 Objectives.** `[D]` The opposing side's objective at `conflict_start` (06.13.2) defaults from its
`defeat_disposition` (kill → `kill`, capture and ransom and drag_to_lair → `capture`, rob → `rob`, drive_off →
`drive_off`, leave → `defeat`) unless the archetype's `encounter.objective_default`, a complication or chapter
11's situation names another (a soldier patrol holds a gate: `hold`; a homunculus spies: `escape`).

**09.8.9 Issue I-005: what 04's pacing should assume.** `[D]` Chapter 04's pacing simulation drew conflicts at
the PC's band to band+2 (tiers b, b+1, b+1, b+2; mean +1). This chapter's budget fields Δ −1 / 0 / +1 at
30 / 55 / 15 % and Δ +2 only by choice. `09-i005-check.py` re-runs 04's R1 pacing rows with both
distributions (09.12 reports the result and the recommendation to 04).

### 09.9 Defeat: lethality, dispositions, and the victor who remembers

**09.9.1 `lethal_context`.** `[D]` Every archetype carries `lethal_context: true | false` and every adversary
record carries the value and its causes (`lethal_causes`): `archetype` when the archetype's flag is true (it
kills: trolls, wraiths, demons, dragons, the ravenous dead, horrors) or its disposition is `kill`;
`severity` when any of its attacks or powers is S4 or more. These are inputs to chapter 07's lethal-warning
trigger (07.3.3 causes `archetype`, `disposition`, `severity`); 07 writes the lethal context, delivers the
warning and decides when it takes effect (07.3.5). An adversary whose record has no cause is not lethal by
itself: robbers who rob, guards who arrest and a pack that wants the PC gone can put a PC Down, not kill it,
unless the advisory is lethal (07.3.3 `advisory`) or its disposition switches (09.9.2) [07 Interface
requests; BRIEF §4].

**09.9.2 `defeat_disposition` and when it switches to kill.** `[D]` + `[J:flag]` Every archetype carries one
of chapter 07's seven dispositions (T-07-11: `capture`, `ransom`, `rob`, `drive_off`, `drag_to_lair`, `leave`,
`kill`), chosen by the victor's nature — slavers enslave, bandits rob, beasts drag you off, the law arrests
[R6 C-19; R4 §6.2 item 5]. The library's split over 63 archetypes: capture 17, drag to lair 17, drive off 14,
kill 11, rob 2, leave 2 (ransom is used by 11's factions and appears here as a captive fate). Each archetype also
lists `kill_when`: the closed set of recorded facts that switch its side's disposition toward the PC to
`kill` for the rest of the scene ("the PC killed their chief"; "the PC desecrated their altar"; "a thief of
its hoard"). `[J:flag]` *"Is a `kill_when` fact of this side now true in state?"* True only when the fact
named is recorded this scene (a defeat, a write on the altar, the item in the PC's possessions); false for
anything the side merely suspects. Uncertain → false. When true, the switch is a recorded behavior change
(`set_fact(side.defeat_disposition_toward_pc = kill)`), which raises 07's `disposition` warning (07.3.3)
before it can matter. *Worst case (J):* a wrong true is a warning the player sees and a fight that can now kill
(class ii: the warning takes effect only after the player's next declaration, 07.3.5); a wrong false leaves
the disposition milder (errs safe, class iv).

**09.9.3 The victor remembers (Nemesis).** `[D]` + `[T]` Defeat writes the world (07.6.2), and the foe who
beat the PC grows [R6 C-20 (Shadow of Mordor: the orc who killed you is promoted and remembers; burned orcs
fear fire); R: https://www.gamesradar.com/shadow-mordor-nemesis-system-amazing-how-works/]. Trigger: an
adversary that defeats the PC (07's `victory_over_pc`), or escapes a conflict with the PC alive (fled or broke
and got away), or is of depth `recurring` or `principal` (12.11.1) and survives a conflict with the PC. The
engine promotes it to depth `recurring` if it was a walk-on, gives it a name if it had none (12's name
tables), and rolls once on `tbl.09.nemesis` (d8, no repeats for the same adversary; a promoted adversary keeps
every result):

| d8 | Result | State |
|---|---|---|
| 1 | **Scarred**: it carries the wound the PC gave it | a new weak spot fact: called shots at the old wound work as at a weak spot (06.4.10) |
| 2 | **Afraid**: it fears the harm or method that beat it | `cond.frightened` (S1) at first sight of that harm tag or tactic each scene |
| 3 | **Learned**: it knows the PC's way of fighting | +1 to its defenses against the PC's recorded signature deed tag (`eff.defense_edge`) |
| 4 | **Grudge**: it wants the PC dead | disposition toward the PC becomes `kill` (07's warning fires when it is next perceived) |
| 5 | **Promoted**: its kind honors it | standard → elite (once; an elite rolls again) |
| 6 | **Retinue**: it has gathered followers | it now travels with a minion mob of 3 of its kind or faction |
| 7 | **Boasts**: it tells the story its way | a rumor naming the PC and the encounter spreads in its region (11) |
| 8 | **Hunts**: it comes looking | a hidden clock (11: danger, 6, +1 a week, omens mandatory) ends with it arriving where the PC is |

It also writes `knows_pc` (the PC's face, name if spoken, and signature tactic) as knowledge (15), which
behavior predicates may then read (09.7.4), and its next appearance carries the tell "it knows you". A rival is
also chapter 04's recognizer V8 ("the Rival Names You"): its epithet for the PC is a recognition vehicle
04 may stage [R6 §A V8]. Nemesis results are capped by the band: a promotion never raises the threat band
(it changes the variant), so loot and evidence stay honest.

**09.9.4 Captive fate, bargains and dread.** `[D]` Three more stakes fields, all chapter 07's inputs:
- `captive_fate` — one of 07's closed list (trial, sale, sacrifice, interrogation, ransom, labor, the larder),
  naming the captors' clock when the disposition takes the PC (07.6.3). Default by org tag when absent
  (`harm.yaml#captivity.fates`). Sacrifice and the larder are lethal on completion, so 07's warning fires at
  their clock's imminent stage.
- `can_bargain: true` — the power can take a debt at the Threshold (07.5.5's Death's Bargain bargainer):
  vampires, liches and death-kings, fey nobles, wild fey and hags, spirits of place, ancestors and celestials,
  greater demons, devil tempters and possessors, great dragons (13 archetypes). False for everything that cannot
  or would not.
- `dread: S1–S4` — the severity of the dread check at first sight in a scene (07.11.2): the walking dead S1–S2,
  ghouls and wights S2, wraiths, vampires, aberrations and abominations S3, liches, death-kings and great
  demons S4. Absent for creatures that are only dangerous (25 archetypes carry a dread rung).

**09.9.5 The contract with chapter 07's ladder.** `[D]` Chapter 07 set targets for how often a PC who fights on
to the end in a lethal context reaches the last-chance menu, by advisory word: trivial 0, easy 1, fair 5,
hard 26, lethal 80 per 100 fights. Section E of `09-adversary-sim.py` runs 07's own ladder (`07-harm-sim.py`'s
`fight07`: wound load 3, Dying 3 steps, dying checks, foes that kill) on 481 encounters built from this
chapter's final templates (the matrix shapes, the bestiary alone at three bands, the mixed encounters), pooled
by the word **this chapter's estimator** returns:

| Advisory (estimator) | Fights | Staggered | Dying | Menu per 100 | 07's target |
|---|---|---|---|---|---|
| trivial | 153,000 | 0.5 | 0.0 | **0.0** | 0 |
| easy | 48,000 | 7.1 | 0.6 | **0.4** | 1 |
| fair | 32,250 | 22.9 | 3.5 | **2.3** | 5 |
| hard | 56,250 | 57.8 | 24.0 | **18.4** | 26 |
| lethal | 71,250 | 92.2 | 81.1 | **77.7** | 80 |

Every word lands at or slightly below its target, never above: the advisory never under-warns relative to
07's promise. "Hard" is gentler than 07's pooled rows (18 against 26) because 09's hard bucket contains every
hard fight of the bestiary, many of them armored or slow foes that rarely finish a PC, where 07's five
reference rows were the steepest equal-band pairs. The wound-load limit of 3 holds (no row needed 2).
This closes issue I-013's check on 07's side; 09.12.3 summarizes all three issues.

### 09.10 Knowledge: tells, lore, and the graduated reveal

**09.10.1 Tells.** `[N]` + `[S]` A **tell** is what the narrator may say instead of a number (06.9.6; 12.10.7).
Every archetype has five, all data (`tells`): **presence** (the sign of it before it is seen: "a ring of eyes
at the edge of the firelight"), **wounded** (its `bloodied` descriptor in fiction), **breaking** (its morale
omens' last stage), **weak_hint** (a clue to its weak spot, perceivable to an attentive character), and a
**windup** tell on each heavy attack or shaped power (06.9.5). On top of these, chapter 09's **band tells**
(T-09-13; `behaviors.yaml#band_tells`) voice threat: four lines per band, from rabble ("moves like it has never
really had to fight") to legend ("standing near it, you feel how small a life is"). Rules for using them:
- At first perception the narration carries the presence tell and one band tell (engine-chosen, no repeats
  in the scene); 09.6.6 makes the band tell mandatory when the creature is above the PC's band.
- `bloodied` is narrated with the wounded tell; a break with the breaking tell; a Windup with its windup tell.
- A tell never states a number or a rules term ("it has 12 Vitality left", "it is resistant to fire") and
  never implies what the record does not hold (00.6.4, INV-2).
- A weak-spot hint is narrated the first time the PC Observes the creature or sees it act in a way that shows
  it ("the biggest one never commits first"); learning it as a fact (09.10.2) is what makes it citable.

**09.10.2 Lore: what the PC knows about a kind of creature.** `[J:enum]` + `[D]` *Anchor: yes.*
```
### 09.10.2  Know the creature (lore)                               [J:enum] [D]
Trigger [T]:        the PC declares a Recall about a creature or kind it has perceived or heard of
Loads in:           situation.conflict.*, situation.exploration.*, situation.investigation.*
License check:      basic verb: verb.recall covers common knowledge of the PC's origin and trade (a
                    farmer knows wolves, a soldier knows soldiers: the archetype's `lore.rarity` is
                    common AND the PC's origin or livelihood touches its terrain or org tags); otherwise
                    the archetype's `lore.deed_tag` names the licensed lore (lic.training.lore_bestiary,
                    _religion, _arcana, _history, _engineering): G2 with it, G3 without (crude fallback:
                    Observe it in action, 06.9.6).
Decisions (J):      1. ITEMS RANKED [J:enum, by the PLAYER]: the player ranks what it wants to know from the
                       closed list below (P17); the DM's part is to read out the list.
                    2. COMMON KNOWLEDGE [J:flag]: "Does the PC's recorded origin, livelihood or experience
                       touch this creature's kind?" (true only with a fact: an origin's terrain or org tags
                       matching the archetype's, a past encounter recorded as knowledge). Uncertain -> false.
Computation [D]:    DC = the tier in the record's `lore.dc_tier`: by band T1-2 Easy, T3 Moderate, T4 Hard,
                    T5 Very hard, one rung harder for uncommon kinds, two for rare, three for legendary
                    (T-09-16). Stakes Safe (Risky in a fight: the action is the price). Reach Standard.
                    Delivered items = 01's deliver_count(N, delivered reach) over the ranked list:
                      1. its kind and threat in words (archetype name, band tell, the advisory if a
                         fight is framed)                 4. its nerve and what makes it break; its
                      2. its heaviest attack and its        disposition (what it does to the beaten)
                         windup tell                      5. its weak spot (the fact: citable as a lever
                      3. one resistance or vulnerability     or called shot, 06.4.10)
                         and its COUNTER (09.6.4)         6. its cannot list (one entry per item)
                    Critical success: all six. Success: about half, in the player's order. Failure: one
                    vague impression (item 1 only, as rumor-certainty). Critical failure: nothing reliable
                    (optionally a wrong belief, written with truth: false, P17).
Stakes:             Safe; in a conflict the action is spent
State writes:       knowledge records (15) for each delivered item; the items move from sealed to
                    `available` in the codex (00.6.4); a retry about the same creature in the same scene
                    costs Risky stakes (cost.time or cost.exposure) (P17's "not a free retry")
Narration may not imply: an item not delivered; a number of the stat block (items are delivered as facts
                    in fiction: "trolls heal from anything but fire or acid")
Worst case (J):     the only DM decision is the common-knowledge flag: wrongly true lets a G1 Recall in
                    where a license was needed: at most the delivered items early, from a roll the
                    player still had to make (class ii); wrongly false redirects to the licensed lore or
                    to Observe (class iv: the player can cite the origin fact).
Examples:           inside: a forester recalls wolves (common, origin terrain forest): G1, Easy for T1:
                    success, 3 items: kind and threat, the bite's knockdown, the pack follows its leader.
                    boundary: the same forester and a barrow-wight (uncommon, religion): G3 without
                    lic.training.lore_religion: redirect to Observe it, or ask the priest in town.
                    non-example: "I know trolls are weak to fire, everyone knows that" -> an assertion
                    (SG-06): the Recall decides what the PC knows.
Anchor:             yes. Intent verbs: recall, what do I know about, identify, study the beast.
                    Knobs: dc (tier), reach_unit (items), time_cost (a beat -> an interval of study of a
                    body, a book, a witness: reach Great).
Basis:              [C:P17] [R7 §5 Ex.8 (the probe's bundled monster question, re-ruled)] [R3 §09.5]
                    [06.9.6] [DL-09-10]
```

**09.10.3 Observing in a fight.** `[D]` 06.9.6's Observe of a foe (one action; against its Wits defense; reach
in information items) uses the same ranked list with these differences: it learns about **this** creature (its
Guard as a number is item 0 and comes first if the player ranks it), not its kind; it needs no license; and a
power the PC has already witnessed (09.5.4) is delivered free. `ab.read_the_field` and `ab.know_the_beast`
(05) unseal from the same list.

**09.10.4 What becomes known stays known.** `[D]` A delivered item is a knowledge record on the PC with its
source; it is `available` in the codex under the creature or kind (14), citable as a fact for levers and called
shots from the next beat (00.3.9a), and never re-sealed. A later encounter with the same kind shows the known
items in the codex without a roll.

### 09.11 What a defeat produces

**09.11.1 Loot (08's contract).** `[D]` Every archetype satisfies `gen_loot.yaml#contract_09`: `creature_tags`
most specific first, `harm_tags`, `evidence_tags` (its deed tags), `org_tags` for folk, the threat band as tier
cap; `loot.yield` (`trophy` by default; `none` for vermin swarms, the walking dead's hordes, spirits of place,
possessors and oozes, which yield materials only; `hoard` for dragons, giants, liches, wyrms and greater
demons; `always` for principal NPCs and named foes); `loot.trophy_base` where the branch default would starve
the pool; `loot.flaw` for sources whose nature curses what they leave (a lich's and a tempter's
`flaw.binding`; a hag's and a greater demon's `flaw.thirsty`); `gear` (folk, base item ids, mundane);
`purse` (`band` = 08.3.11's purse by band, `hoard`, or `none`); `harvest` (default: 08's materials by source
tags). **Validation** (08.3.4), run by the generator with 08's own pool code at tier cap 1 on every base each
archetype can drop: **57 of 58** archetypes that drop items hold 3 or more pool entries on every base (the
smallest are 3); the exception is the water elemental's amulet and ring, 2 entries, filed with 08 (the water
branch has the fewest loot properties; 08's own reference set had the same shape of exception for one
aberration).

**09.11.2 Evidence (03).** `[D]` An adversary's threat band reaches the **challenge band** of an evidence event
through 03.4.3: in a conflict, the challenge band is the PC's power band shifted by the advisory word computed at
framing (DL-00-05), which this chapter's estimator derives from the foes' lines; for a conduct-only event, the
highest threat band among aware opposing entities present [verification: V2b-002]. Its
`creature_tags` are the opponent kind 03 counts (03's non-folk opponent-kind counters); its `lethal_context`
feeds the event's `lethal_context`. A mob is one source (06.10.2). The deed tags of evidence are always the
PC's own method's.

**09.11.3 Absorption (04).** `[D]` Every archetype carries `absorbable {pool_gate_tags, eligible, cannot_absorb,
signature}`: the gate is its creature tags; `eligible` lists the `gen_absorb.yaml` entries the gate admits
(computed by the generator); `cannot_absorb` names the exclusions; `signature` names the one entry
`gen.item_ability` and the Taking's decisive fill use (which 04 records as `signature_of` on that entry:
Interface requests). The human-like folk have no pool (04's `no_pool`: human, elf, dwarf, halfling, orc,
goblin; their arts are learned); giant-kin and beastfolk (ogres, trolls, true giants, gnolls, lizardfolk) have
natural powers (a troll's grip, a gnoll's nose), and their archetypes list their eligible entries [revision:
I-020: 04 narrowed `no_pool` and records `signature_of`; this chapter's generator reads `no_pool` from the data
and fails when `signature_of` disagrees with the archetypes]. The Taking
needs the PC to have witnessed the creature act (09.5.4).

### 09.12 The bestiary

**09.12.1 What ships.** `[D]` `data/adversaries.yaml` holds **123 fully statted adversaries** built by PR-09-1
from the 63 archetypes: 25 at T1, 33 at T2, 33 at T3, 21 at T4, 11 at T5; 77 standard, 15 minion (all of them
mobs or swarms), 16 elite, 15 solo; every creature branch at several bands (beasts 24, folk 34, undead 16,
spirits 8, fiends 8, constructs 7, elementals 6, dragons 9, horrors 11). Every entry carries every field of
T-09-14, every id it cites is validated against the canonical data (tags, effects and contrib effects,
conditions, abilities, afflictions, base items, flaws, the absorbable pool), and every entry's band fidelity
is within tolerance (09.4.5). T-09-12b indexes them. A region's seed lists the subset its tables field (`bestiary`, 12.16.12); a pre-made
setting (chapter 13) may add its own
in the file's owner-block (`blocks: [{owner: "13", entries: [...]}]`), built by the same procedure (PR-09-1;
the generator accepts 13's roster lines in the same five-field form).

**09.12.2 Using an entry.** `[D]` A bestiary entry is a **template**. `create_entity(kind: adversary,
template_id: adv.*)` makes an instance with its own id, Vitality, Focus, conditions and position; the
template is never written to in play. A named instance (a principal NPC built on `adv.bandit_captain`)
keeps the template's numbers and adds its own facts (name, wants, knowledge, 15; Nemesis results, 09.9.3).

**09.12.3 Issues this chapter closes or answers.** `[N]`
- **I-011** (T4/T5 pairs lethal; three equal-band foes lethal from P2): confirmed with the final templates and
  adversary Fend (T-09-9: P4 vs two T4 4/100, P5 vs two T5 3/99; P2 vs three T2 34/83, P3 vs three T3 6/98),
  and **reflected in the rules**: 09.8.1's budget fields individuals at most two of the PC's band and never two
  at T4–T5; bosses are solos or leaders with lower-band help; the advisory reports pairs as lethal. Closed.
- **I-013** (re-run 06 and 07 on 09's templates): done. 06's script re-run with the final standard (its model,
  no adversary Fend) and the extended model (with Fend) both reproduce T-06-13's shape; the only word changes
  from 06's published matrix are listed in T-09-9's note. 07's ladder on the final templates gives menu rates
  0 / 0.4 / 2.3 / 18.4 / 77.7 per 100 by word against targets 0 / 1 / 5 / 26 / 80, with the wound-load limit
  at 3 (09.9.5). Closed.
- **I-005** (04's pacing assumed opposition at band to band+2): **answered, and handed to 03/04 with a
  measured proposal.** Re-running 04's own R1 pacing (`09-i005-check.py`, 100 seeds) with this chapter's
  budget (Δ −1 / 0 / +1 = 30 / 55 / 15 %) and challenge band = the foe's threat band slows the focused archer
  badly (median tier sessions 7 / 20 / 31 / 46 / never, against 4 / 9 / 19 / 34 / 56). The cause is that a
  crowd of lower-band foes, which T-09-10 makes the normal fair fight, counts as a low-band deed. The fix this
  chapter proposes to 03 (owner of `challenge_band`): **a conflict's challenge band is the PC's power band
  shifted by the advisory word computed at framing — trivial −2, easy −1, fair 0, hard +1, lethal +2 —
  clamped 1–5**, so that a hard fight is a band-up deed whether the difficulty came from one strong foe or many
  weak ones. With a realistic word mix (easy 25 / fair 40 / hard 30 / lethal 5 %), 04's pacing comes back to
  within 2–5 sessions of its targets (archer 5 / 11 / 22 / 39 / 60, swordsman 3 / 8 / 15 / 25 / 38; the archer
  reaches tier 5 within 60 sessions in 59 of 100 runs against 82). **Adopted** as the orchestrator's decision
  DL-00-05 and written into 03.4.3 at integration; I-005 is closed [integration: DL-00-05].
- **I-006** (Focus-binary equal-band fights) remains resolved for martial characters with the final
  templates: one standard foe of the PC's band is beaten 100 / 99.9 / 99.4 / 87.8 / 80.2 % of the time with no
  Focus (T-09-3); the caster part is I-009 (05).

---

## Procedures

**PR-09-1 Build an adversary (archetype + band + role + variant → stat block).** `[D]` (`09-gen_data09.py`
`build()`; also the engine's `create_entity` for an improvised creature.)
1. **Validate.** The band lies in the archetype's `bands`; the role is one of its `roles` (or T-09-4's for an
   improvised one); the variant is one of four.
2. **Attributes.** For each of the seven, `RUNG[archetype rung][band]` (T-09-2), or the entry's override.
3. **Competence.** `{tag, c_b}` for each `evidence_tag` and for `deed.martial.unarmed`.
4. **Defenses.** Guard = 10 + Agility + `c_b` + 1 if it carries a shield; each attribute defense = 10 +
   attribute + (`c_b` if trained). Tempo = 10 + Wits.
5. **Attacks.** The archetype's attacks (or the entry's subset): modifier = rung(attribute) + `c_b`; severity =
   standard (or heavy) severity of the band + offset, clamped S1–S5; windup if heavy, S4+ or shaped. The
   primary attack by role: archer → first ranged; caster → first working; else the first primary that is not
   heavy. A **solo** with no heavy attack gains a heavy copy of its primary at the band's heavy severity.
6. **Reduction.** From `armor` (T-09-5b); worn armor from its gear.
7. **Powers.** The archetype's powers, plus the entry's, minus its drops; a solo adds `pow.shrug` and
   `pow.second_wind`. Refuse any power whose `min_band` exceeds the band.
8. **Nerve and reaction.** The archetype's nerve shifted by variant (T-09-5); reactions by effective band and
   variant (09.3.9).
9. **Vitality solve** (09.4.4). Target = the band standard's harm ratio against the band's reference PC ÷
   (1 + premium); search the envelope for the nearest Vitality with resistance and regeneration ignored;
   compensation steps per 09.4.5; then × the variant multiplier (T-09-5).
10. **Focus, effect DCs.** Focus by band and variant (09.3.8); `effect_dc` for each attribute any of its
    powers names (10 + attribute + `c_b`).
11. **Stakes and voice.** Copy `lethal_context` (with causes), `defeat_disposition`, `kill_when`,
    `captive_fate`, `can_bargain`, `dread`, `mind`, `speaks`, `reaction_roll`, `tells`, `weak_spot`, `lore`
    (with its DC tier, T-09-16), `loot`, `objective`.
12. **Advisories.** Compute `advisory_alone` against the reference PC of each band (PR-09-4), and
    `advisory_without_counter` if it resists or regenerates.
13. **Write** the record with `calibration {premium, solved_vitality, fidelity, severity_compensation, line}`;
    for an improvised creature, log the ruling (00.15.6).

**PR-09-2 Improvise an adversary at the table.** `[J:enum]` `[J:rung]` `[D]`
1. `find_rulings` for an earlier improvisation of this creature (00.15.6); reuse it if found.
2. Classify branch then archetype (09.2.4).
3. Classify the band (09.3.1), inside the archetype's bands, tie to the lower.
4. Classify the role (09.4.2) and the variant (09.4.8).
5. PR-09-1. Write the entity; log the ruling.
6. Frame the encounter as PR-09-5.

**PR-09-3 Run an adversary's turn.** `[D]`
1. `turn_start` (06.1.8): its reaction refreshes; its triggers fire (regeneration, a solo's Shrug); periodic
   conditions apply.
2. For the first action: evaluate its behavior list (09.7.2: overlay rows first for a solo; its own list;
   the leader's rally row) top to bottom; skip a row whose `when` is false **or** whose act is illegal now
   (cannot pay, out of reach, on its `cannot` list, forbidden by a condition); take the first that remains.
3. Pick the target by the row, else by 06.9.3's attention order; roll any tie.
4. Build the beat as an engine frame (06.9.2): the attack's verb and modifier, the target's defense, levers
   and snags cited by the engine in 06's order, stakes Safe, reach Standard, `lethal` per 07.3.6. Offer the PC
   its Fend or reaction ability. Roll; apply harm and riders through the substrate (00.10).
5. Write `witnessed` for any power or ability the PC perceived (09.5.4); render the power's tell.
6. If the macro used one action, repeat from step 2 for the second; if it used two, stop.
7. `turn_end` (06.1.8). Narrate from the frames and the tells only (06.9.6).

**PR-09-4 `threat_advisory(encounter, pc)`.** `[D]` (`09_core.estimate`; the engine's implementation must
reproduce `09-adversary-sim.py` section D within one word on its rows.)
1. **Read the PC's line**: best attack modifier (no levers), its base severity with mastery, Guard, worn
   reduction, **current** Vitality, tempo modifier, whether it has a reaction available for Fend, and its
   attack's harm tags and properties (silvered, magical).
2. **Read each opposing participant's line**: attack modifier, Guard, Vitality per member and members,
   primary severity, heavy severity (if any heavy attack), reduction, Fend (reaction kinds), nerve, tempo DC,
   leader flag, swarm flag; **resistance factor** 0.5 if a resistance covers the PC's attack and its "unless"
   does not, else 1; **regeneration** if it regenerates and the PC's attack is neither fire nor acid.
3. **Rates** by exact enumeration of the d20 (00.3.10 degrees, critical one rung heavier): the PC's harm per
   round against each (Strikes at 0, −2, −4; −2 more on the first if it Fends; minus reduction; a swarm one rung
   lighter; × resistance, floored per outcome; minus regeneration, never below a tenth); each foe's harm per
   round against the PC (attacks at 0 and −2; the PC's Fend −2 on the first attack of the foe with the highest
   rate; a heavy blow on alternate turns; a mob's numbers step at its current members); and their variances.
4. **Timeline**: order foes by total Vitality, lowest first; each member falls after its Vitality ÷ the PC's
   rate against it.
5. **Morale events** on the timeline: an individual's first bloodied +1 at the midpoint of its segment; each
   member defeated +1 (a leader +2); side strength first at half +2, at a quarter +2. The side breaks at the
   first time the sum reaches the side's nerve (the highest nerve present); a side with a fearless member
   never breaks.
6. **Harm**: H = Σ over foes of (rate × time alive, truncated at the break), with a mob at full members until
   its first member falls; plus each foe's rate × (its chance to act before the PC − ½). Variance likewise,
   plus the timeline's own variance (the PC's harm variance over its rate³, times the opposition's rate²).
7. **Probabilities**: Staggered = 1 − Φ((V − 1 − H)/σ); beaten = 1 − Φ((V + 1.75·h̄ − ½ − H)/σ), where V is
   current Vitality and h̄ the opposition's mean harm per landed blow; win = 1 − beaten.
8. **Word** by T-06-13's thresholds; then a companion one gentler (only with an able ally, never more
   than one word, and not from a hard estimate whose no-ally win is below 75: 09.6.3, 16.7.11), surprise
   one harsher (09.6.3) [integration: IR ch.16 to 09].
9. **Return** the word, the two percentages and H/V; log them with the encounter.

**PR-09-5 Frame an encounter.** `[D]` `[J:flag]`
1. From the place's table row (10, 13): the group and its count (`tbl.09.group_shape`); fold four or more of a
   kind into a mob; add the leader as a separate elite.
2. Roll a complication if the row says so (`tbl.09.complication`; reroll toward the stalest axis twice at
   most); a result of 12 mixes (`tbl.09.mixing`).
3. Set starting bands and flags from the terrain and notice (06.3.9; 10's encounter distance).
4. If the creatures have not noticed the PC: no conflict yet; a sapient side rolls its reaction when the PC
   interacts (12.11.2); an animal rolls `tbl.09.beast_mood`; a mindless side follows its list.
5. Compute the advisory (PR-09-4). Hard → 07's danger notice; lethal → 07's lethal warning (cause
   `advisory`); any adversary above the PC's band → its band tell (09.6.6).
6. Narrate presence and band tells; record the challenge axes presented (09.8.5).

**PR-09-6 Deliver what the PC learns about a creature.** `[D]` `[J:flag]`
1. Gate: common knowledge (G1 by origin or experience) or the archetype's lore license (G2), else G3 with the
   Observe redirect.
2. The player ranks items from 09.10.2's list.
3. Frame at the record's `lore.dc_tier`; roll; `deliver_count(N, reach)`.
4. Write each delivered item as knowledge (15) and unseal it to `available`; write witnessed powers free.
5. On a critical failure, optionally write one wrong belief (`truth: false`), never about a lethal fact (a
   wrong belief may not hide that something kills).

**PR-09-7 The victor remembers.** `[T]` `[D]`
1. Trigger on `victory_over_pc`, on an adversary leaving a conflict alive, or on a recurring or principal
   adversary surviving a conflict with the PC.
2. Promote to `recurring`; name it if unnamed.
3. Roll `tbl.09.nemesis` (no repeats); write the result's state.
4. Write `knows_pc` knowledge; queue chapter 04's V8 staging and 11's rumor and clock where the result says.

**PR-09-8 A morale break, from tick to row.** `[D]` (chapter 06 owns the clock; this is the per-adversary part.)
1. When the side's morale clock completes, each member gains `cond.broken` (06.11.5).
2. On its next turn, the member's list's first row (`broken`) fires its `morale.break_then`: `flee`,
   `yield`, `cower`, `frenzy` or `fighting_withdrawal` — or, where its state forbids that (cornered, held),
   06.11.5's state table.
3. A fearless member is unaffected and fights on.
4. Each member that leaves or yields is recorded `drive_off` or `yielded` for 03, 08 and 04 (06.11.5).

---

## Tables

Tables embedded in the Rules are canonical and indexed here: **T-09-2** band tables (09.3.2); **T-09-3** the
standard line (09.3.3); **T-09-4** roles (09.4.2); **T-09-5** variants (09.4.6); **T-09-5b** reduction by armor
(09.3.6); **T-09-10** the solo encounter budget (09.8.1); **T-09-11** band anchors (09.3.1's rungs). The data
files are canonical for every id and number.

**T-09-1 The archetype record** (`data/archetypes.yaml#archetypes`; SCHEMAS.md#archetypes.yaml's required
fields first, then this chapter's optional fields).

| Field | Type | Meaning | Rule |
|---|---|---|---|
| `id`, `name`, `tags`, `lifecycle`, `basis` | common envelope | `tags` = creature tags + harm tags | 00.16.1 |
| `creature_tags` | [tag] | most specific first (03's request) | 09.2.1 |
| `harm_tags` | [tag] | the harm it deals by nature | 08.3.4 |
| `evidence_tags` | [deed tag] | the deeds it practices; its competence keys | 09.2.1, 09.3.2 |
| `org_tags` | [org tag] | folk only | 08.3.4 |
| `loot` | {yield, trophy_base, pool_gate_tags, flaw, signature_property} | 08's contract | 09.11.1 |
| `absorbable` | {pool_gate_tags, eligible, cannot_absorb, signature} or {pool: none} | 04's contract | 09.11.3 |
| `behaviors` | [beh id] | its list(s) | 09.7.2 |
| `lethal_context`, `defeat_disposition` | bool, enum (07's seven) | stakes | 09.9.1–2 |
| `tells` | {presence, wounded, breaking, weak_hint, windup} | what the narrator may say | 09.10.1 |
| `signature_property` | in `loot` | default: 08's per-tag signature | 08.3.4 |
| `summary`, `mind`, `speaks`, `tongue` | str, enum, bool, str | who it is | 09.2.7 |
| `size`, `bands`, `roles` | enum, [min, max], [role] | | 09.3.1, 09.3.7, 09.4.2 |
| `attribute_rungs`, `trained_defenses` | {attr: rung}, [attr] | | 09.3.2, 09.3.4 |
| `armor` | {kind, rung, no_gaps} | | 09.3.6 |
| `attacks` | [{id, name, verb, attr, off, harm, bands, weight, heavy, shape, site, riders, primary}] | | 09.3.5 |
| `powers`, `traits` | [pow id], [effect_ref] | traits = resistances, vulnerabilities, immunities | 09.5 |
| `cannot` | [str] | categorical impossibilities | 09.2.5 |
| `default_behavior_role` | melee / ranged / beast / mob | 06.9.4's families | 09.7.2 |
| `morale` | {nerve, segments, break_then} | 06's clock | 09.7.5 |
| `reaction`, `reaction_roll`, `pace` | by_band or false; bool; int | 06.6.5; 12.11.2; 06.3.3 | 09.3.9, 09.8.7 |
| `kill_when`, `captive_fate`, `can_bargain`, `dread` | [str], enum, bool, S1–S4 | 07's inputs | 09.9.2, 09.9.4 |
| `weak_spot` | {text, fact, effect} | the citable weakness | 09.10.1, 06.4.10 |
| `gear`, `purse`, `harvest` | [bi id], band / hoard / none, default | 08.3.10–11 | 09.11.1 |
| `lore` | {deed_tag, rarity} | | 09.10.2 |
| `encounter` | {terrain, group, objective_default} | for 10, 13 | 09.8.3 |

**T-09-6 Power premium** (`band_tables.power_premium`). Rider 0.06 · offensive or control action 0.06 · aura
0.06 · lesser (pack tactics, shield wall, frenzy, ambush, mend, blink, glamour, rally, call, drag, Shrug, second
wind, spell turning) 0.03 · summoning 0.10 · pool ability held 0.04 · movement, senses and bodily immunities 0
· total cap 0.40. Resistances and regeneration are counters (09.4.4), not premium.

**T-09-7 Resisted-effect degree tables** (`archetypes.yaml#degree_tables`). The target rolls the named verb
against the power's effect DC (00.3.3; 06.4.11); an affliction id is its own table (07.9.2).

| Id | Verb (attribute) | Critical success | Success | Failure | Critical failure |
|---|---|---|---|---|---|
| `tbl.09.knockdown` | Evade (Agility) | — | — | `cond.prone` | prone and `cond.off_balance` 1 round |
| `tbl.09.fear` | Endure (Resolve) | inured for the scene | — | `cond.frightened` S1, scene | frightened S2, scene |
| `tbl.09.blast` | Evade (Agility) | harm two rungs lighter | harm one rung lighter | full harm | harm one rung heavier |
| `tbl.09.charm` | Endure (Resolve) | inured for the scene | — | `cond.charmed` 1 round | charmed 2 rounds |
| `tbl.09.hold` | Evade (Agility) | — | — | `cond.restrained` 1 round | restrained 2 rounds |
| `tbl.09.daze` | Endure (Resolve) | — | — | `cond.dazed` 1 round | `cond.stunned` 1 round |
| `tbl.09.drain` | Endure (Resolve) | — | Focus −1 | Focus −2 | Focus −3 (05.6.13 cap 4 a scene) |
| `tbl.09.push` | Evade (Agility) | — | — | one band back | one band back and prone |
| `tbl.09.choke` | Endure (Endurance) | — | — | `cond.choking` S2 while held | choking S3 while held |

**T-09-8 Behavior vocabularies** (`behaviors.yaml#predicates`, `#macros`; closed). *Predicates (44):* always,
broken, held, prone, bloodied, phase2, windup_held, heavy_ready, can_pay, not_engaged, engaged_target,
engaged_other, target_in_reach, target_prone, target_held_by_self, target_helpless, target_bloodied,
target_unaware, target_in_cover, target_aloft_or_far, ally_engaged_target, target_not_flanked, alone,
outnumbered, ally_defeated, leader_defeated, is_leader, side_bloodied, pc_staggered, pc_dying, objective_met,
hidden, cover_near, not_loaded, in_water, lair_adjacent, light_bright, fire_near, host_present, thrall_near,
offered_terms, insulted, pc_fled, reinforcements_possible. *Macros (32):* strike, strike_twice, windup, heavy,
grapple, use, move_engage, move_cover, move_far, withdraw, withdraw_shoot, flee, yield, cower,
fighting_withdrawal, frenzy, defend, aim, reload, flank, screen, hide, ready, stand, break_free, rally,
call_help, talk, drag_off, retreat_lair, feed, hold_ground. Each is defined over state in the data file.

**T-09-9 The advisory matrix, re-run on the final templates** (section B of the output; extended model with adversary Fend; 3,000 fights per cell; word win% / Staggered%). This is the reference the estimator is checked against (09.6.9) and the shape encounter budgets read (09.8.1). It differs from T-06-13 in five cells, all harsher because adversaries of T3+ now Fend: P3 vs one T3 trivial → easy; P2 vs one T3 hard → lethal (39%, the edge); P4 vs three T3 hard → lethal; P5 vs four T3 easy → fair; P5 vs a T4 mob of four hard → lethal. Cells marked "-" were not simulated (three or more foes a band above are lethal, as in T-06-13).

*Foes two bands below the PC*

| PC | 1 foe | 2 | 3 | 4 | 6 | mob of 4 | mob of 6 | mob of 8 |
|---|---|---|---|---|---|---|---|---|
| P3 (T1) | trivial 100/0 | trivial 100/0 | trivial 100/0 | trivial 100/0 | trivial 100/0 | trivial 100/0 | trivial 100/0 | trivial 100/1 |
| P4 (T2) | trivial 100/0 | trivial 100/0 | trivial 100/0 | trivial 100/0 | easy 98/5 | trivial 100/0 | easy 100/4 | fair 97/17 |
| P5 (T3) | trivial 100/0 | trivial 100/0 | trivial 99/3 | fair 92/13 | hard 50/64 | easy 99/6 | fair 93/23 | fair 84/47 |

*Foes one band below*

| PC | 1 foe | 2 | 3 | 4 | 6 | mob of 4 | mob of 6 | mob of 8 |
|---|---|---|---|---|---|---|---|---|
| P2 (T1) | trivial 100/0 | trivial 100/0 | trivial 100/1 | easy 99/5 | fair 83/27 | trivial 100/2 | easy 100/9 | fair 97/29 |
| P3 (T2) | trivial 100/0 | trivial 100/0 | trivial 100/0 | easy 98/3 | hard 77/34 | trivial 100/2 | easy 96/15 | fair 83/42 |
| P4 (T3) | trivial 100/1 | fair 89/29 | lethal 31/87 | lethal 3/98 | lethal 0/100 | hard 49/74 | lethal 15/96 | lethal 4/99 |
| P5 (T4) | trivial 100/0 | fair 90/28 | lethal 34/81 | lethal 4/98 | lethal 0/100 | lethal 39/80 | lethal 12/96 | lethal 5/98 |

*Foes of the PC's band*

| PC | 1 foe | 2 | 3 | 4 | 6 | mob of 4 | mob of 6 | mob of 8 |
|---|---|---|---|---|---|---|---|---|
| P1 (T1) | trivial 100/0 | trivial 100/1 | easy 97/8 | fair 84/32 | hard 41/69 | easy 99/13 | fair 94/28 | hard 84/57 |
| P2 (T2) | trivial 100/1 | fair 90/23 | lethal 34/83 | lethal 2/99 | lethal 0/100 | hard 41/76 | lethal 9/98 | lethal 2/100 |
| P3 (T3) | easy 99/5 | hard 62/61 | lethal 6/98 | lethal 0/100 | lethal 0/100 | lethal 17/93 | lethal 1/100 | lethal 0/100 |
| P4 (T4) | fair 87/42 | lethal 4/100 | lethal 0/100 | lethal 0/100 | lethal 0/100 | lethal 0/100 | lethal 0/100 | lethal 0/100 |
| P5 (T5) | hard 80/58 | lethal 3/99 | lethal 0/100 | lethal 0/100 | lethal 0/100 | lethal 1/100 | lethal 0/100 | lethal 0/100 |

*Foes one band above*

| PC | 1 foe | 2 | 3 | 4 | 6 | mob of 4 | mob of 6 | mob of 8 |
|---|---|---|---|---|---|---|---|---|
| P1 (T2) | easy 98/10 | hard 50/69 | lethal (as T-06-13) | - | - | - | - | - |
| P2 (T3) | lethal 39/88 | lethal 0/100 | lethal (as T-06-13) | - | - | - | - | - |
| P3 (T4) | hard 65/69 | lethal 1/100 | lethal (as T-06-13) | - | - | - | - | - |
| P4 (T5) | lethal 7/99 | lethal 0/100 | lethal (as T-06-13) | - | - | - | - | - |

*Foes two bands above*

| PC | 1 foe | 2 | 3 | 4 | 6 | mob of 4 | mob of 6 | mob of 8 |
|---|---|---|---|---|---|---|---|---|
| P1 (T3) | lethal 6/99 | lethal 0/100 | lethal (as T-06-13) | - | - | - | - | - |
| P2 (T4) | lethal 0/100 | lethal 0/100 | lethal (as T-06-13) | - | - | - | - | - |
| P3 (T5) | lethal 0/100 | lethal 0/100 | lethal (as T-06-13) | - | - | - | - | - |

**T-09-12 The archetype library** (`data/archetypes.yaml`; 63 entries). Bands are the lowest and highest the kind is fielded at; *nerve / break* is 06.11's; *disp.* the defeat disposition (07.6.1); *L* lethal context; *dread* the first-sight check (07.11.2).

| Archetype | Branch | Bands | Roles | Mind | Nerve / break | Disp. | L | Dread | Absorb signature |
|---|---|---|---|---|---|---|---|---|---|
| `arch.wolf` Wolf and hound | beast | T1–T3 | skirmisher, soldier | animal | skittish / flee | drive_off | — | — | ab.abs_predators_nose |
| `arch.great_cat` Great cat | beast | T2–T3 | lurker, skirmisher | animal | skittish / flee | drag_to_lair | — | — | ab.abs_pounce |
| `arch.bear` Bear | beast | T2–T4 | brute | animal | skittish / flee | drive_off | — | — | ab.abs_thick_hide |
| `arch.herd_beast` Maddened herd beast | beast | T1–T3 | brute | animal | steady / flee | drive_off | — | — | ab.abs_thick_hide |
| `arch.giant_vermin` Giant vermin | beast | T1–T3 | lurker, controller | animal | skittish / flee | drag_to_lair | — | S1 | ab.abs_wall_crawl |
| `arch.vermin_swarm` Vermin swarm | beast | T1–T2 | swarm | animal | skittish / flee | drive_off | — | — | — |
| `arch.reptile` Great reptile | beast | T1–T4 | controller, lurker | animal | skittish / flee | drag_to_lair | — | — | ab.abs_scale_ward |
| `arch.raptor` Raptor and great bird | beast | T1–T4 | skirmisher | animal | skittish / flee | drag_to_lair | — | — | ab.abs_night_eyes |
| `arch.water_beast` Beast of the deep | beast | T2–T4 | brute, controller | animal | skittish / flee | drag_to_lair | — | — | ab.abs_gills |
| `arch.monstrous_beast` Monstrous beast | beast | T2–T5 | brute, soldier | animal | steady / flee | drag_to_lair | — | — | ab.abs_pounce |
| `arch.brigand` Brigand | folk | T1–T3 | soldier, archer, skirmisher, leader | sapient | skittish / yield | rob | — | — | none (folk) |
| `arch.soldier` Soldier and guard | folk | T1–T4 | soldier, archer, leader | sapient | steady / fighting_withdrawal | capture | — | — | none (folk) |
| `arch.knight` Knight | folk | T2–T5 | soldier, leader | sapient | resolute / yield | capture | — | — | none (folk) |
| `arch.cultist` Cultist | folk | T1–T4 | caster, soldier, leader | sapient | resolute / frenzy | capture | — | — | none (folk) |
| `arch.folk_mage` Hedge-witch and sorcerer | folk | T1–T5 | caster, controller | sapient | skittish / yield | capture | — | — | none (folk) |
| `arch.elf_warden` Elven warden | folk | T2–T4 | archer, skirmisher, leader | sapient | steady / fighting_withdrawal | drive_off | — | — | none (folk) |
| `arch.dwarf_holdguard` Dwarven holdguard | folk | T2–T4 | soldier, brute | sapient | resolute / fighting_withdrawal | capture | — | — | none (folk) |
| `arch.orc` Orc raider | folk | T1–T4 | brute, soldier, leader | sapient | steady / flee | capture | — | — | none (folk) |
| `arch.goblin` Goblin | folk | T1–T2 | skirmisher, archer, swarm | sapient | skittish / flee | rob | — | — | none (folk) |
| `arch.gnoll` Gnoll | folk | T1–T3 | brute, skirmisher | sapient | steady / flee | drag_to_lair | — | S1 | — |
| `arch.lizardfolk` Lizardfolk | folk | T1–T3 | soldier, brute | sapient | steady / fighting_withdrawal | drag_to_lair | — | — | — |
| `arch.ogre` Ogre | folk | T2–T4 | brute | cunning | steady / flee | drag_to_lair | — | — | — |
| `arch.troll` Troll | folk | T3–T5 | brute | cunning | resolute / flee | drag_to_lair | yes | S1 | ab.abs_stone_grip |
| `arch.giant` True giant | folk | T4–T5 | brute, leader | sapient | resolute / fighting_withdrawal | capture | yes | — | ab.abs_stone_grip |
| `arch.skeleton` Skeleton | undead | T1–T3 | soldier, archer, swarm | mindless | fearless / — | drive_off | — | S1 | ab.abs_grave_chill |
| `arch.zombie` Walking dead | undead | T1–T2 | brute, swarm | mindless | fearless / — | kill | yes | S2 | ab.abs_grave_chill |
| `arch.ghoul` Ghoul | undead | T1–T3 | skirmisher, swarm | cunning | steady / flee | drag_to_lair | yes | S2 | ab.abs_life_drink |
| `arch.wight` Wight | undead | T2–T4 | soldier, leader | sapient | resolute / fighting_withdrawal | drag_to_lair | yes | S2 | ab.abs_grave_chill |
| `arch.vampire` Vampire | undead | T3–T5 | skirmisher, leader | sapient | resolute / fighting_withdrawal | capture | yes | S3 | ab.abs_life_drink |
| `arch.ghost` Ghost | undead | T1–T4 | controller | sapient | steady / flee | drive_off | — | S2 | ab.abs_ghost_step |
| `arch.wraith` Wraith | undead | T3–T5 | skirmisher | sapient | resolute / flee | kill | yes | S3 | ab.abs_ghost_step |
| `arch.lich` Lich | undead | T4–T5 | caster | sapient | fearless / — | capture | yes | S4 | ab.abs_dread_gaze |
| `arch.deathlord` Death-king | undead | T4–T5 | soldier, leader | sapient | fearless / — | capture | yes | S4 | ab.abs_dread_gaze |
| `arch.fey_noble` Fey noble | spirit | T3–T5 | skirmisher, caster, leader | sapient | steady / yield | capture | — | — | ab.abs_glamour_skin |
| `arch.wild_fey` Wild fey | spirit | T1–T3 | skirmisher, controller, swarm | sapient | skittish / flee | leave | — | — | ab.abs_glamour_skin |
| `arch.hag` Hag | spirit | T2–T4 | caster, controller | sapient | steady / yield | capture | yes | S2 | ab.abs_glamour_skin |
| `arch.place_spirit` Spirit of place | spirit | T2–T5 | controller, brute | alien | resolute / flee | drive_off | — | — | ab.abs_spirit_sight |
| `arch.ancestor` Ancestor spirit | spirit | T2–T4 | soldier, leader | sapient | resolute / flee | drive_off | — | — | ab.abs_spirit_sight |
| `arch.celestial` Celestial | spirit | T3–T5 | soldier, leader | sapient | resolute / flee | drive_off | — | — | — |
| `arch.lesser_demon` Lesser demon | fiend | T1–T3 | brute, skirmisher, swarm | cunning | steady / frenzy | kill | yes | S2 | ab.abs_hellfire_blood |
| `arch.greater_demon` Greater demon | fiend | T4–T5 | brute, leader | sapient | fearless / — | kill | yes | S4 | ab.abs_dread_gaze |
| `arch.tempter` Devil tempter | fiend | T2–T5 | caster, leader | sapient | steady / yield | capture | — | S1 | ab.abs_hellfire_blood |
| `arch.enforcer` Devil enforcer | fiend | T3–T5 | soldier, controller | sapient | resolute / fighting_withdrawal | capture | — | S2 | ab.abs_hellfire_blood |
| `arch.possessor` Possessing spirit | fiend | T2–T4 | controller, caster | sapient | steady / flee | capture | yes | S3 | — |
| `arch.hellbeast` Hellbeast | fiend | T2–T4 | skirmisher, brute | animal | steady / flee | kill | yes | S1 | ab.abs_hellfire_blood |
| `arch.golem` Golem | construct | T2–T5 | brute, soldier | mindless | fearless / — | drive_off | — | — | ab.abs_stone_flesh |
| `arch.animated` Animated object | construct | T1–T3 | soldier, swarm | mindless | fearless / — | drive_off | — | — | — |
| `arch.clockwork` Clockwork | construct | T1–T4 | soldier, archer | mindless | fearless / — | capture | — | — | ab.abs_tireless |
| `arch.homunculus` Homunculus | construct | T1–T2 | skirmisher | cunning | skittish / flee | leave | — | — | ab.abs_tireless |
| `arch.fire_elemental` Fire elemental | elemental | T2–T5 | skirmisher, brute | alien | fearless / — | kill | yes | — | ab.abs_ember_heart |
| `arch.earth_elemental` Earth elemental | elemental | T2–T5 | brute, soldier | alien | fearless / — | drive_off | — | — | ab.abs_stone_flesh |
| `arch.water_elemental` Water elemental | elemental | T2–T5 | controller, brute | alien | fearless / — | kill | yes | — | ab.abs_gills |
| `arch.air_elemental` Air elemental | elemental | T2–T5 | skirmisher, controller | alien | fearless / — | drive_off | — | — | ab.abs_storm_step |
| `arch.frost_elemental` Frost elemental | elemental | T2–T5 | brute, controller | alien | fearless / — | kill | yes | — | ab.abs_rime_breath |
| `arch.great_dragon` Great dragon | dragon | T4–T5 | solo | sapient | resolute / fighting_withdrawal | kill | yes | S3 | ab.abs_dragon_breath |
| `arch.drake` Drake | dragon | T2–T4 | brute, skirmisher | animal | steady / flee | drag_to_lair | yes | — | ab.abs_scale_ward |
| `arch.wyvern` Wyvern | dragon | T3–T4 | skirmisher, brute | animal | steady / flee | drag_to_lair | yes | — | ab.abs_scale_ward |
| `arch.wyrm` Wyrm and sea serpent | dragon | T3–T5 | brute, controller | animal | steady / flee | drag_to_lair | yes | S2 | ab.abs_scale_ward |
| `arch.aberration` Aberration | horror | T3–T5 | caster, controller | alien | steady / flee | capture | yes | S3 | ab.abs_alien_mind |
| `arch.ooze` Ooze | horror | T1–T4 | brute, controller | mindless | fearless / — | kill | yes | S1 | ab.abs_acid_touch |
| `arch.fungal` Fungal host | horror | T1–T3 | controller, swarm | alien | fearless / — | drag_to_lair | yes | S2 | ab.abs_spore_cloud |
| `arch.monstrous_plant` Monstrous plant | horror | T1–T5 | controller, brute | alien | fearless / — | drag_to_lair | yes | — | ab.abs_rooted |
| `arch.abomination` Abomination | horror | T2–T5 | brute | cunning | resolute / frenzy | kill | yes | S3 | — |

**T-09-12b The bestiary index** (`data/adversaries.yaml`; 123 entries). Primary attack modifier and severity, Guard, Vitality (a mob: members × per member), reduction, Focus; the word is `advisory_alone` against a reference PC of the adversary's own band with the counter held († the word without the counter, where it differs: 09.6.4).

| Adversary | Archetype | Band | Variant | Role | Attack | Guard | Vitality | Red. | Focus | vs P(own band) |
|---|---|---|---|---|---|---|---|---|---|---|
| `adv.wolf` Wolf | wolf | T1 | standard | skirmisher | +1 S2 | 12 | 5 | 0 | 0 | trivial |
| `adv.wolf_pack` Wolf pack | wolf | T1 | minion | skirmisher | +1 S2 | 12 | 5 × 2 | 0 | 0 | trivial |
| `adv.dire_wolf` Dire wolf | wolf | T2 | standard | soldier | +3 S3 | 15 | 9 | 0 | 1 | trivial |
| `adv.warg_alpha` Warg alpha | wolf | T3 | elite | soldier | +5 S3 | 17 | 40 | 0 | 3 | fair |
| `adv.panther` Panther | great_cat | T2 | standard | lurker | +5 S2 | 17 | 11 | 0 | 1 | trivial |
| `adv.sabre_cat` Sabre-tooth | great_cat | T3 | standard | lurker | +7 S3 | 19 | 20 | 0 | 2 | easy |
| `adv.black_bear` Black bear | bear | T2 | standard | brute | +7 S2 | 13 | 11 | 1 | 1 | trivial |
| `adv.cave_bear` Cave bear | bear | T3 | elite | brute | +9 S3 | 15 | 36 | 1 | 3 | fair |
| `adv.wild_boar` Wild boar | herd_beast | T1 | standard | brute | +4 S2 | 11 | 4 | 0 | 0 | trivial |
| `adv.aurochs` Aurochs | herd_beast | T2 | standard | brute | +7 S2 | 13 | 9 | 1 | 1 | trivial |
| `adv.giant_spider` Giant spider | giant_vermin | T2 | standard | lurker | +3 S2 | 15 | 12 | 1 | 1 | trivial |
| `adv.giant_centipede` Giant centipede | giant_vermin | T1 | standard | lurker | +1 S2 | 12 | 5 | 0 | 0 | trivial |
| `adv.rat_swarm` Rat swarm | vermin_swarm | T1 | minion | swarm | -2 S2 | 12 | 6 × 2 | 0 | 0 | easy |
| `adv.bat_swarm` Bat swarm | vermin_swarm | T1 | minion | swarm | -2 S2 | 12 | 6 × 2 | 0 | 0 | easy |
| `adv.giant_constrictor` Giant constrictor | reptile | T2 | standard | controller | +7 S2 | 13 | 10 | 1 | 1 | trivial |
| `adv.great_crocodile` Great crocodile | reptile | T3 | standard | brute | +9 S3 | 15 | 20 | 1 | 2 | trivial |
| `adv.giant_eagle` Giant eagle | raptor | T2 | standard | skirmisher | +3 S2 | 17 | 12 | 0 | 1 | trivial |
| `adv.roc` Roc | raptor | T4 | solo | skirmisher | +7 S3 | 22 | 56 | 0 | 5 | hard |
| `adv.reef_shark` Reef shark | water_beast | T2 | standard | brute | +7 S3 | 15 | 7 | 0 | 1 | trivial |
| `adv.great_squid` Great squid | water_beast | T4 | standard | controller | +12 S3 | 20 | 32 | 0 | 3 | fair |
| `adv.owlbear` Owlbear | monstrous_beast | T3 | standard | brute | +9 S3 | 15 | 18 | 1 | 2 | easy |
| `adv.griffon` Griffon | monstrous_beast | T3 | standard | skirmisher | +9 S3 | 15 | 18 | 1 | 2 | easy |
| `adv.manticore` Manticore | monstrous_beast | T4 | standard | soldier | +12 S3 | 17 | 26 | 2 | 3 | fair |
| `adv.chimera` Chimera | monstrous_beast | T4 | solo | brute | +12 S3 | 17 | 40 | 2 | 5 | hard |
| `adv.footpad` Footpad (halfling cutpurse) | brigand | T1 | standard | skirmisher | +1 S2 | 11 | 4 | 1 | 0 | trivial |
| `adv.brigand_archer` Brigand archer | brigand | T1 | standard | archer | +1 S2 | 11 | 4 | 1 | 0 | trivial |
| `adv.highwayman` Highwayman | brigand | T2 | standard | soldier | +3 S3 | 13 | 10 | 1 | 1 | trivial |
| `adv.bandit_captain` Bandit captain | brigand | T2 | elite | leader | +3 S2 | 13 | 24 | 1 | 2 | easy |
| `adv.brigand_band` Brigand rabble | brigand | T1 | minion | soldier | +1 S2 | 11 | 4 × 2 | 1 | 0 | trivial |
| `adv.town_watch` Town watchman | soldier | T1 | standard | soldier | +2 S2 | 12 | 2 | 2 | 0 | trivial |
| `adv.levy_mob` Levy | soldier | T1 | minion | soldier | +2 S2 | 12 | 6 × 1 | 2 | 0 | easy |
| `adv.man_at_arms` Man-at-arms | soldier | T2 | standard | soldier | +5 S2 | 14 | 6 | 2 | 1 | trivial |
| `adv.crossbowman` Crossbowman | soldier | T2 | standard | archer | +3 S2 | 14 | 7 | 2 | 1 | trivial |
| `adv.sergeant` Sergeant | soldier | T3 | elite | leader | +7 S3 | 16 | 30 | 2 | 3 | fair |
| `adv.knight_errant` Knight errant | knight | T3 | standard | soldier | +9 S3 | 16 | 12 | 3 | 2 | fair |
| `adv.champion` Champion of the realm | knight | T4 | elite | soldier | +12 S3 | 18 | 25 | 3 | 4 | hard |
| `adv.cult_initiate` Cult initiates | cultist | T1 | minion | soldier | +1 S2 | 11 | 4 × 2 | 1 | 0 | trivial |
| `adv.cult_fanatic` Cult fanatic | cultist | T2 | standard | soldier | +3 S2 | 13 | 12 | 1 | 1 | trivial |
| `adv.cult_priest` Cult priest | cultist | T3 | elite | caster | +7 S3 | 15 | 40 | 1 | 4 | fair |
| `adv.hedge_witch` Hedge-witch | folk_mage | T2 | standard | caster | +7 S2 | 13 | 12 | 0 | 2 | trivial |
| `adv.sorcerer` Sorcerer | folk_mage | T3 | standard | caster | +9 S3 | 15 | 20 | 0 | 3 | trivial |
| `adv.court_magus` Court magus | folk_mage | T4 | elite | caster | +12 S3 | 17 | 40 | 0 | 5 | fair |
| `adv.elf_warden` Elven warden | elf_warden | T3 | standard | archer | +9 S3 | 19 | 12 | 1 | 2 | easy |
| `adv.dwarf_holdguard` Dwarven holdguard | dwarf_holdguard | T3 | standard | soldier | +7 S3 | 14 | 15 | 3 | 2 | easy |
| `adv.orc_raider` Orc raider | orc | T2 | standard | brute | +5 S2 | 14 | 9 | 1 | 1 | trivial |
| `adv.orc_warband` Orc warband | orc | T2 | minion | soldier | +5 S2 | 14 | 5 × 6 | 1 | 0 | hard |
| `adv.orc_warchief` Orc warchief | orc | T3 | elite | leader | +7 S3 | 16 | 36 | 1 | 3 | fair |
| `adv.goblin_skulk` Goblin skulk | goblin | T1 | standard | skirmisher | +2 S2 | 12 | 3 | 1 | 0 | trivial |
| `adv.goblin_mob` Goblin mob | goblin | T1 | minion | skirmisher | +2 S2 | 12 | 6 × 2 | 1 | 0 | easy |
| `adv.goblin_boss` Goblin boss | goblin | T2 | elite | leader | +5 S2 | 15 | 14 | 1 | 2 | easy |
| `adv.gnoll_reaver` Gnoll reaver | gnoll | T2 | standard | brute | +5 S2 | 13 | 10 | 1 | 1 | trivial |
| `adv.gnoll_pack` Gnoll pack | gnoll | T1 | minion | skirmisher | +2 S2 | 11 | 4 × 2 | 1 | 0 | trivial |
| `adv.lizardfolk_hunter` Lizardfolk hunter | lizardfolk | T2 | standard | soldier | +5 S2 | 13 | 11 | 1 | 1 | trivial |
| `adv.ogre` Ogre | ogre | T3 | standard | brute | +9 S3 | 11 | 20 | 1 | 2 | trivial |
| `adv.ogre_chief` Ogre chief | ogre | T3 | solo | brute | +9 S3 | 11 | 60 | 1 | 4 | fair |
| `adv.troll` Troll | troll | T4 | standard | brute | +12 S3 | 17 | 26 | 2 | 3 | fair († lethal) |
| `adv.hill_giant` Hill giant | giant | T4 | standard | brute | +12 S3 | 12 | 32 | 2 | 3 | fair |
| `adv.frost_giant_jarl` Frost giant jarl | giant | T5 | solo | leader | +14 S5 | 13 | 69 | 2 | 6 | hard |
| `adv.skeleton_rabble` Skeleton rabble | skeleton | T1 | minion | soldier | +1 S2 | 11 | 3 × 2 | 1 | 0 | trivial |
| `adv.skeleton_warrior` Skeleton warrior | skeleton | T1 | standard | soldier | +1 S2 | 11 | 4 | 1 | 0 | trivial |
| `adv.skeleton_archer` Skeleton archer | skeleton | T2 | standard | archer | +3 S2 | 13 | 12 | 1 | 1 | trivial |
| `adv.zombie_horde` Zombie horde | zombie | T1 | minion | brute | +2 S2 | 8 | 6 × 2 | 0 | 0 | trivial |
| `adv.plague_zombie` Plague zombie | zombie | T2 | standard | brute | +5 S3 | 9 | 12 | 0 | 1 | trivial |
| `adv.ghoul` Ghoul | ghoul | T2 | standard | skirmisher | +3 S2 | 15 | 12 | 0 | 1 | trivial |
| `adv.ghast` Ghast | ghoul | T3 | elite | skirmisher | +5 S3 | 17 | 40 | 0 | 3 | fair |
| `adv.barrow_wight` Barrow-wight | wight | T3 | standard | soldier | +7 S3 | 15 | 15 | 2 | 2 | trivial |
| `adv.wight_lord` Wight lord | wight | T4 | elite | leader | +10 S3 | 17 | 35 | 2 | 4 | hard |
| `adv.vampire_spawn` Vampire spawn | vampire | T3 | standard | skirmisher | +9 S3 | 19 | 14 | 0 | 2 | easy († hard) |
| `adv.vampire_count` Vampire count | vampire | T5 | solo | leader | +14 S4 | 24 | 48 | 0 | 6 | hard († lethal) |
| `adv.wailing_ghost` Wailing ghost | ghost | T2 | standard | controller | +5 S2 | 13 | 12 | 0 | 1 | trivial († fair) |
| `adv.wraith` Wraith | wraith | T3 | standard | skirmisher | +7 S3 | 17 | 19 | 0 | 2 | trivial († fair) |
| `adv.dread_wraith` Dread wraith | wraith | T4 | elite | skirmisher | +10 S3 | 20 | 39 | 0 | 4 | hard († lethal) |
| `adv.lich` Lich | lich | T5 | solo | caster | +14 S4 | 19 | 62 | 0 | 7 | hard |
| `adv.death_king` Death-king | deathlord | T5 | elite | leader | +14 S4 | 19 | 40 | 3 | 5 | hard |
| `adv.pixie_swarm` Pixie host | wild_fey | T1 | minion | swarm | +4 S1 | 14 | 6 × 2 | 0 | 0 | hard |
| `adv.dryad` Dryad | wild_fey | T2 | standard | controller | +7 S2 | 17 | 9 | 0 | 1 | trivial |
| `adv.sidhe_knight` Sidhe knight | fey_noble | T3 | standard | skirmisher | +9 S3 | 19 | 13 | 0 | 2 | easy |
| `adv.fey_queen` Queen of the hollow hill | fey_noble | T5 | solo | leader | +14 S4 | 24 | 48 | 0 | 6 | hard |
| `adv.bog_hag` Bog hag | hag | T3 | standard | caster | +5 S3 | 15 | 20 | 0 | 3 | trivial |
| `adv.river_spirit` Spirit of the river | place_spirit | T3 | standard | controller | +9 S3 | 15 | 20 | 0 | 2 | trivial |
| `adv.cairn_guardian` Cairn guardian | ancestor | T2 | standard | soldier | +3 S3 | 13 | 10 | 0 | 1 | trivial († fair) |
| `adv.temple_warden` Temple warden | celestial | T4 | standard | soldier | +10 S3 | 22 | 29 | 0 | 3 | fair |
| `adv.imp` Imp | lesser_demon | T1 | standard | skirmisher | +2 S2 | 12 | 4 | 0 | 0 | trivial |
| `adv.dretch_mob` Dretch swarm | lesser_demon | T1 | minion | brute | +2 S2 | 12 | 4 × 2 | 0 | 0 | trivial |
| `adv.vrock` Vulture demon | lesser_demon | T3 | standard | brute | +7 S3 | 17 | 19 | 0 | 2 | trivial |
| `adv.pit_lord` Pit lord | greater_demon | T5 | solo | brute | +14 S5 | 22 | 48 | 0 | 6 | lethal |
| `adv.smiling_stranger` The smiling stranger | tempter | T3 | standard | caster | +9 S3 | 15 | 20 | 0 | 3 | trivial |
| `adv.chain_devil` Chain devil | enforcer | T4 | standard | controller | +12 S3 | 20 | 20 | 2 | 3 | hard |
| `adv.whisperer` Whisperer in the walls | possessor | T3 | standard | controller | +9 S3 | 15 | 20 | 0 | 2 | trivial († fair) |
| `adv.hell_hound` Hell hound | hellbeast | T2 | standard | skirmisher | +5 S2 | 15 | 10 | 0 | 1 | trivial |
| `adv.animated_armor` Animated armor | animated | T1 | standard | soldier | +2 S2 | 11 | 5 | 0 | 0 | trivial |
| `adv.flying_blades` Flying blades | animated | T2 | minion | swarm | +5 S1 | 13 | 4 × 6 | 1 | 0 | lethal |
| `adv.brass_sentinel` Brass sentinel | clockwork | T2 | standard | soldier | +5 S2 | 15 | 6 | 2 | 1 | trivial |
| `adv.clay_golem` Clay golem | golem | T3 | standard | brute | +9 S3 | 11 | 20 | 2 | 2 | trivial († fair) |
| `adv.flesh_golem` Flesh golem | golem | T3 | elite | brute | +9 S3 | 11 | 40 | 2 | 3 | fair († lethal) |
| `adv.iron_golem` Iron golem | golem | T4 | solo | soldier | +12 S3 | 12 | 54 | 3 | 5 | hard († lethal) |
| `adv.homunculus` Homunculus | homunculus | T1 | standard | skirmisher | +4 S2 | 14 | 3 | 0 | 0 | trivial |
| `adv.salamander` Salamander | fire_elemental | T2 | standard | skirmisher | +7 S2 | 17 | 7 | 0 | 1 | trivial († fair) |
| `adv.fire_elemental` Fire elemental | fire_elemental | T3 | standard | brute | +9 S3 | 19 | 14 | 0 | 2 | easy († hard) |
| `adv.earth_elemental` Earth elemental | earth_elemental | T4 | standard | brute | +12 S3 | 12 | 32 | 3 | 3 | fair († lethal) |
| `adv.water_elemental` Water elemental | water_elemental | T3 | standard | controller | +9 S3 | 17 | 16 | 0 | 2 | trivial († hard) |
| `adv.air_elemental` Air elemental | air_elemental | T3 | standard | skirmisher | +5 S3 | 19 | 20 | 0 | 2 | easy († fair) |
| `adv.ice_colossus` Ice colossus | frost_elemental | T5 | solo | brute | +14 S4 | 19 | 60 | 2 | 6 | hard |
| `adv.fire_drake` Fire drake | drake | T2 | standard | brute | +5 S2 | 15 | 8 | 1 | 1 | trivial |
| `adv.rock_drake` Rock drake | drake | T3 | elite | brute | +7 S3 | 17 | 32 | 1 | 3 | fair |
| `adv.wyvern` Wyvern | wyvern | T3 | standard | skirmisher | +9 S3 | 17 | 14 | 1 | 2 | easy |
| `adv.wyvern_matriarch` Wyvern matriarch | wyvern | T4 | elite | skirmisher | +12 S3 | 20 | 25 | 2 | 4 | hard |
| `adv.red_wyrmling` Red wyrmling | great_dragon | T4 | standard | brute | +12 S3 | 17 | 20 | 2 | 3 | fair |
| `adv.young_dragon` Young dragon | great_dragon | T4 | solo | brute | +12 S3 | 17 | 35 | 2 | 5 | hard |
| `adv.elder_dragon` Elder dragon | great_dragon | T5 | solo | brute | +14 S4 | 19 | 51 | 2 | 6 | hard |
| `adv.lindworm` Lindworm | wyrm | T4 | standard | brute | +12 S3 | 17 | 23 | 2 | 3 | fair |
| `adv.sea_serpent` Sea serpent | wyrm | T5 | solo | controller | +14 S5 | 19 | 48 | 2 | 6 | hard |
| `adv.brain_eater` Brain-eater | aberration | T4 | standard | caster | +12 S3 | 17 | 32 | 0 | 4 | fair |
| `adv.eye_tyrant` Eye tyrant | aberration | T5 | solo | caster | +14 S4 | 19 | 66 | 0 | 7 | hard |
| `adv.green_slime` Green slime | ooze | T1 | standard | brute | +2 S3 | 8 | 5 | 0 | 0 | trivial |
| `adv.ochre_jelly` Ochre jelly | ooze | T2 | standard | controller | +5 S3 | 9 | 12 | 0 | 1 | trivial († easy) |
| `adv.black_pudding` Black pudding | ooze | T4 | standard | brute | +10 S4 | 12 | 32 | 0 | 3 | easy († fair) |
| `adv.myconid_mob` Myconid colony | fungal | T1 | minion | controller | +1 S2 | 10 | 4 × 2 | 0 | 0 | trivial |
| `adv.spore_shambler` Spore shambler | fungal | T2 | standard | controller | +3 S3 | 11 | 12 | 0 | 1 | trivial |
| `adv.strangling_creeper` Strangling creeper | monstrous_plant | T2 | standard | controller | +7 S2 | 9 | 12 | 1 | 1 | trivial |
| `adv.blighted_treant` Blighted treant | monstrous_plant | T4 | standard | brute | +12 S3 | 12 | 32 | 2 | 3 | easy († hard) |
| `adv.stitched_horror` Stitched horror | abomination | T3 | standard | brute | +9 S3 | 15 | 18 | 1 | 2 | easy († fair) |
| `adv.vat_titan` Vat titan | abomination | T5 | solo | brute | +14 S4 | 19 | 52 | 2 | 6 | hard († lethal) |

**T-09-13 Band tells** (`behaviors.yaml#band_tells`; four per band; the engine draws without repeats in a scene).

| Band | Tells |
|---|---|
| T1 rabble | poorly armed, or armed with whatever came to hand · nervous: looks to the others before acting · thin, hungry, or young · moves like it has never really had to fight |
| T2 trained | kept gear, used well · moves with purpose and keeps its footing · watches your hands, not your face · the scars of a few fights |
| T3 elite | unhurried: it has done this many times · the others give it room · fine or terrible arms, kept with care · it reads your stance before you move |
| T4 champion | the ground seems smaller around it · veterans would turn back here · its presence is a pressure you feel · a reputation runs ahead of it: songs, warnings, bones |
| T5 legend | the world bends near it: weather, light, animals · stories name it, and the stories are not exaggerated · a whole region arranges itself around avoiding it · standing near it, you feel how small a life is |

**T-09-14 The adversary record** (`data/adversaries.yaml#adversaries`; SCHEMAS.md#adversaries.yaml's required
fields plus these optional fields).

| Field | Meaning |
|---|---|
| `archetype`, `threat_band`, `variant`, `role`, `default_behavior_role` | the four inputs and 06's family |
| `creature_tags`, `tags`, `size`, `members`, `swarm`, `leader`, `npc_depth` | identity (06.10, 12.11.1) |
| `attributes`, `competence`, `defenses` {guard, might, agility, endurance, wits, intellect, presence, resolve}, `tempo` | numbers (09.3.2–4) |
| `vitality` (int, or {per_member, pool} for a mob), `reduction` {amount, harm_tags, kind, no_gaps}, `resistances` | |
| `attacks` [{id, name, verb, attribute, modifier, harm {severity, harm_tags}, bands, weight, action_cost, shape, windup, site, riders, primary}] | 09.3.5 |
| `abilities` (05 ids), `powers` (pow ids), `focus`, `effect_dc` {attr: DC} | 09.5 |
| `reaction` {count, kinds}, `behaviors`, `morale` {nerve, segments, break_then}, `pace` | 09.3.9, 09.7 |
| `tells`, `weak_spot`, `lore` {deed_tag, rarity, dc_tier} | 09.10 |
| `lethal_context`, `lethal_causes`, `defeat_disposition`, `kill_when`, `captive_fate`, `can_bargain`, `dread`, `speaks`, `mind`, `reaction_roll`, `objective` | 09.9 |
| `loot` {yield, tier_cap, trophy_base, flaw, gear, purse} | 09.11.1 |
| `advisory_alone` {P1..P5}, `advisory_without_counter`, `counter` | 09.6.4 |
| `calibration` {premium, solved_vitality, fidelity, severity_compensation, line} | 09.4.4–5 |

**T-09-15 Challenge axes and complications** (`behaviors.yaml#challenge_axes`, `#complications`). The eight
axes are listed in 09.8.5. `tbl.09.complication` (d12): 1 footing (slick ground) · 2 height · 3 dark · 4 a
hazard of the place · 5 chokepoint · 6 something else they want · 7 someone to protect · 8 the clock runs
(4 rounds) · 9 reinforcements (`clk.09.reinforcements`) · 10 they would rather talk · 11 split position (one
of them at range or in cover) · 12 mixed (`tbl.09.mixing`). Each result names its axis and its effect
references. `tbl.09.mixing` (d8): 1–2 at each other's throats · 3 the aftermath · 4 hunter and quarry · 5–6
allies · 7 a deal in progress · 8 captor and captive. `tbl.09.beast_mood` (2d6) and `tbl.09.nemesis` (d8) are
in 09.8.7 and 09.9.3; `tbl.09.group_shape` (d6) in 09.8.3.

**T-09-16 Lore DC tier** (09.10.2; stored as `lore.dc_tier`).

| Band | common | uncommon | rare | legendary |
|---|---|---|---|---|
| T1 | Easy | Moderate | Hard | Very hard |
| T2 | Easy | Moderate | Hard | Very hard |
| T3 | Moderate | Hard | Very hard | Legendary |
| T4 | Hard | Very hard | Legendary | Legendary |
| T5 | Very hard | Legendary | Legendary | Legendary |

---

## Worked examples

Numbers are exact from `data/adversaries.yaml` and `09_core.py`; the reference PC lines are T-06-12's
(P2: +7, Guard 16, Vitality 14, armor 1, Strike S2; P3: +9, Guard 18, Vitality 16, armor 2, Strike S3).

### WE-09-1 Building an adversary: the dire wolf, and its alpha

*Inputs.* `arch.wolf` (attribute rungs M H H H L L M for might, agility, endurance, wits, intellect, presence,
resolve; trained in Agility and Wits; natural armor none; bite: Might, offset 0, rider `pow.knockdown`;
powers pack tactics, keen scent, night eyes; nerve skittish, break flee; disposition drive off), band **T2**,
role **soldier**, variant **standard**; entry overrides: creature tags `creature.beast.predator.canine`,
`creature.beast.monstrous.dire`, size large.

1. **Attributes** (T-09-2, T2): might +1, agility +3, endurance +3, wits +3, intellect −1, presence −1, resolve
   +1. `c_b` = +2.
2. **Defenses**: Guard 10 + 3 + 2 = **15**; agility 15 and wits 15 (trained); might 11; endurance 13;
   intellect 9; presence 9; resolve 11. **Tempo** 10 + 3 = **13** (it often acts before a novice).
3. **Bite**: Might +1 + 2 = **+3**; T2 standard harm S2, offset 0 → S2; rider knockdown with effect DC
   10 + 1 + 2 = **13** (Evade or prone).
4. **Premium**: knockdown rider 0.06 + pack tactics 0.03 = **0.09** (scent and night eyes carry none).
5. **Solve**: the T2 standard's harm ratio against P2, ÷ 1.09, is the target. With the bite at S2, even the
   envelope's ceiling (12) leaves the wolf too weak (fidelity under 0.67): a +3 bite at Moderate harm does too
   little against Guard 16 and armor 1. **Compensation** (09.4.5): the bite rises one rung to **S3**, and the
   solve lands at **Vitality 9**, fidelity 0.95.
6. **Variant** standard: × 1. **Reaction** (T2): Opportunity Strike. **Nerve** skittish (4). **Focus** 1.
   **Pace** 2 (from the archetype). **Lethal context** false; **disposition** drive off.
7. **Advisory alone**: P1 easy, P2 trivial, P3–P5 trivial.

*The alpha (boundary pair).* `adv.warg_alpha`: the same archetype at **T3**, **elite**, with `pow.howl` and
`pow.call_kin` added. T3 rungs give might +2, agility +4 …; bite +2 + 3 = **+5**, standard harm S3; Guard 10 +
4 + 3 = **17**; premium 0.18 (two more actions); solved Vitality 20, **× 2 = 40**; reaction as T4: Opportunity
Strike and **Fend**; nerve skittish → **steady (6)**; Focus 2 + 1 = **3**. Advisory alone: P2 lethal, **P3
fair**, P4 trivial. It is the pack's leader (`leader: true`): its defeat ticks the pack's morale +2.
*Tempting non-example.* "It leads the pack, so make it T4." Leading is the elite variant and the leader flag;
the band is what it *is* (09.3.1). A T4 wolf would drop tier-4 loot and count as a band-4 deed for a wolf.

### WE-09-2 The advisory for a mixed encounter

*Situation.* A P3 character (the reference line) meets an orc warchief (`adv.orc_warchief`: T3 elite leader;
axe +7, S3; Guard 16; reduction 1; Vitality 36; Fend; nerve resolute) and his warband (`adv.orc_warband`: a mob
of five T2 minions; axe +5, S2; Guard 14; reduction 1; 6 Vitality each, pool 30; nerve skittish).

1. **Rates** (exact d20 enumeration). The PC deals the warband 10.2 a round (three Strikes at +9, +7, +5 vs
   Guard 14; S3 = 5 − 1 reduction, a critical 8 − 1) and the warchief 7.55 (his Fend makes the first −2). The
   warchief deals 3.0 a round, the warband 2.4 (numbers step +1 at three to five members) and 0.9 at one or two.
   The PC's Fend goes to the higher rate: the warchief's 3.0 becomes **2.7**.
2. **Timeline.** Lowest total Vitality first: the warband (30) falls member by member every 6 ÷ 10.2 = 0.59
   rounds, the last at **2.94**; then the warchief, 36 ÷ 7.55 = 4.77 rounds, to **7.71**.
3. **Morale.** The side's nerve is the leader's: resolute, **8**. Ticks: five members defeated (+5 by 2.94);
   strength first at half (33 of 66) when the warchief has taken 3, at 2.94 + 4.77 × 3/36 = **3.34** (+2 → 7);
   the warchief first bloodied at 2.94 + 2.39 = **5.32** (+1 → 8): **the side breaks at 5.32 rounds.**
4. **Harm.** Warchief 2.7 × 5.32 = 14.36; warband 2.4 × 1.76 + 0.9 × 1.18 = 5.28; tempo edges (the warchief
   acts first 35% of the time, the warband 30%) −0.89. **H = 18.8** against Vitality 16: ratio 1.17.
5. **Outcome.** σ = 7.8; mean landed blow h̄ = 2.27. Staggered = 1 − Φ((16 − 1 − 18.8)/7.8) = **69%**;
   win = Φ((16 + 1.75 × 2.27 − 0.5 − 18.8)/7.8) = **54%**.
6. **Word**: win ≥ 40 → **hard**. The Monte Carlo (10,000 fights) gives 46% / 66%: also hard.
7. **What the player sees.** Chapter 07's danger notice: "`[WARNING] A hard fight — you may well lose this.
   Losing here means they take you for labor.`" (the orcs capture; captive fate labor). In fiction: drums, a
   burned farmstead, the band tell "the others give it room".
*Boundary pair.* The same encounter for a P4 character is **fair** (90 / 28); with the PC's hireling at its
side, **fair** (one word gentler, 09.6.3); if the orcs ambush a P3 character who did not notice them
(`cond.surprised`), **lethal** (one word harsher), and chapter 07's lethal warning fires — but takes effect only
after the player's first declaration (07.3.5), so the ambush's opening blows can at worst put the character
Down.
*Tempting non-example.* "The warchief is T3 and so is the PC, and the warband is weaker: call it fair." Band
alone is the challenge-rating failure (R2 #11): five extra bodies are most of this fight's danger.

### WE-09-3 Running an adversary's turn from its list

*Situation.* A barrow-wight (`adv.barrow_wight`: T3; blade +7 S3, draining touch +7 S3 with grave chill and
life drink; Guard 15; Vitality 15; Focus 2; `pow.summon_dead`; list `beh.09.grave_lord`) at `band.near` from a
P3 character who has just broken its barrow's seal. Rows (09.7.1):

| # | when | do |
|---|---|---|
| 1 | broken | fighting_withdrawal |
| 2 | can_pay & reinforcements_possible & not_engaged | use pow.summon_dead |
| 3 | windup_held & target_in_reach | heavy |
| 4 | heavy_ready | windup |
| 5 | can_pay & engaged_target | use pow.dread_gaze |
| 6 | not_engaged | move_engage |
| 7 | always | strike (primary) |

- **Round 1, action 1.** Row 1 false. Row 2: it can pay (2 Focus), the summon is unused, nobody is engaged
  with it → **use `pow.summon_dead`** (two actions, 2 Focus): a mob of three `adv.skeleton_rabble` claws up at
  `band.far`. The tell is narrated ("it chants; the ground at the edge of the light begins to move"); the
  engine writes `witnessed.pc.pow.summon_dead.<wight>`; the advisory is recomputed and re-shown (09.6.5 b).
  Both actions are spent.
- **Round 2, action 1.** Row 2: Focus 0 → false. Row 3: no windup. Row 4: `heavy_ready` false (no heavy attack
  on its record). Row 5: it holds no `pow.dread_gaze` → the row's act is illegal → skipped. Row 6: not engaged →
  **Move** near → close (1 action). **Action 2**: evaluated again: still not engaged → Move close → engaged.
- **Round 3.** Row 7 → **strike** with its primary (the blade), twice; target by attention: the enemy engaged
  with it. First Strike +7 against Guard 18, the PC Fends (−2): needs 13 (40%); second at −2: needs 13 (40%).
  On a hit, 5 − 2 (armor) = 3 harm.
*Boundary.* Had the PC rushed it in round 1 (engaged before its turn), row 2 is false (`not_engaged` fails) and
it strikes at once: whether the dead rise depends on what the PC does first. *Non-example.* "It's a dramatic
moment, it should use its draining touch." The list says `strike (primary)`; the primary is the blade. Drama
does not choose rows (06.9.1).

### WE-09-4 A morale break, and prisoners

*Situation.* A P1 character fights a bandit captain (`adv.bandit_captain`: T2 elite leader; +3, S2; Guard 13;
Vitality 24; nerve steady, break yield) and four brigands (`adv.brigand_band`: a T1 minion mob of 4, 2 each,
pool 8). The advisory: **hard** (79 / 49: one point short of fair), so 07's danger notice is shown ("losing here
means they rob you"). The side reads the leader's nerve: **steady (6)**.
1. The PC's first turn drops two brigands (each hit: 3 − 1 armor = 2, one member's whole Vitality): +1, +1 →
   **2**. Omen (stirring): "one of them glances back at the road".
2. Second turn: the last two brigands fall (+2 → **4**). The captain, alone, rallies (`pow.rally_cry`,
   a fortune check against Moderate: success, reach Standard → −2 → **2**).
3. Third turn: two Strikes put the captain at 12 of 24: first bloodied (+1 → **3**) and the side's strength
   (32 at the start) is past half — 8 + 12 = 20 removed — (+2 → **5**, building: "he gives ground a step at
   a time"). The PC's third action is a Talk to demand surrender — "Drop it and walk, and you keep your life"
   — against the captain's Resolve defense **11**: success, reach Standard → **+2 → 7 ≥ 6: the side breaks.**
4. The break row: the archetype's `break_then` is **yield** (09.7.5): the captain drops his sword and asks
   quarter. He is `defeated` with manner `yielded` (06.11.7) and is the PC's prisoner (07.6.5); sparing or
   killing him is chapter 03's `conduct.mercy` evidence. Loot: one generation for the side (08.3.1),
   circumstance **merciful** if he is spared (the chosen fill).
*Boundary.* Had the captain been defeated first, his defeat ticks +2 (leader) and the brigands, now leaderless,
read the most numerous template's nerve, skittish (4), for their remaining clock. *Non-example.* "They're
bandits, they'd run." They would — if the clock completed. Until it does, they fight (06.11.1).

### WE-09-5 A defeat disposition fires, and a switch to kill

*Situation A (drag to lair).* A P2 character is beaten by gnolls (`arch.gnoll`: disposition **drag_to_lair**,
captive fate **the larder**, `lethal_context` false). No lethal context was recorded (no row of 07.3.3 true:
the advisory was fair, the gnolls' disposition is not kill, no S4 attack), so the falling blow puts the
character **Down**, not Dying (07.2.9). The disposition runs its *defeated* column (T-07-11): the PC wakes in
the gnolls' den (a place created with one recorded exit), its weapon lying where it fell, `clk.larder`
created (countdown 4, +1 a watch; at imminent its completion is lethal, so 07's warning fires then), three
openings written, `setback.captured`. A rescue, an escape, or a bargain is the next scene.
*Situation B (the switch).* Brigands (`arch.brigand`: disposition rob; `kill_when`: "the PC killed one of
theirs and they outnumber the PC 3 to 1"). In the fight the PC kills a brigand outright while four remain.
`[J:flag]` *"Is a kill_when fact now true?"* — a brigand is recorded dead by the PC's lethal Strike, and four
against one is 4 : 1 → **true**. The engine writes `side.defeat_disposition_toward_pc = kill`; 07's `disposition`
warning fires ("It means to kill"), effective from the player's next declaration. Yield is now refused (07.4.1:
kill does not accept); the exits card shows Retreat. *Boundary:* had the brigand been dropped with a nonlethal
blow, no one is dead: the flag is false and the brigands still only rob.

### WE-09-6 Learning what a troll is (P17)

*Situation.* A P3 forester sees a troll (`adv.troll`: T4; advisory alone vs P3 **hard**; without the counter
**lethal**; counter "fire or acid"). The player asks what the character knows about trolls.
- **Gate.** `lore` is `deed.lore.bestiary`, rarity common; the troll's terrain (highland, deepwood,
  underground) touches the forester's origin (forest): **common knowledge true** → G1 Recall (Intellect).
- **DC.** Common at T4 → **Hard (20)**. The forester's Intellect 0 + floor 1 = +1: success on 19+ (10%),
  natural 20 a critical. The player ranks: (1) kind and threat, (3) resistance and counter, (5) weak spot.
- **Roll** 19 → success; delivered items by 01's `deliver_count(3 ranked, Standard)`: about half → the
  first two of the ranked list: "a troll, and a big one"; "it heals from anything but fire or acid". Both are
  written as knowledge and become `available` in the codex.
- **What changes.** The advisory is re-read against the PC's actual attack: with a torch's fire as the
  attack's harm (06.5.10), regeneration does not apply → **hard**; with the spear alone → **lethal**, and 07's
  warning fires. The player was given a plan, not a number.
*Boundary.* A city-born character has no common knowledge here: without `lic.training.lore_bestiary` the
Recall is G3, redirected to Observe it in action (06.9.6) or to asking the old hunter. *Non-example.* "Everyone
knows trolls hate fire" is an assertion (SG-06) until a Recall or a source delivers it.

### WE-09-7 The victor remembers

*Situation.* The orc warchief of WE-09-2 breaks at 5.32 rounds (his `break_then` is flee), is not cornered,
and gets away. Trigger (09.9.3): an adversary escaped a conflict with the PC alive. The engine promotes him to
`recurring`, names him (12's tables: "Gorbrak Vey"), and rolls `tbl.09.nemesis`: **4, Grudge** — his disposition toward the PC becomes
**kill**. It writes `knows_pc` (face, the PC's spear-work). Three weeks later the warband is rolled on the hill
road's table: when the PC perceives him, 07's `disposition` warning fires at first sight, the narrator voices
"he knows you, and he has not come for captives", and the advisory is computed for a T3 elite leader and his
new warband (a second roll, months later, gave **6, Retinue**). Chapter 04 may stage V8: he calls the PC by the
name the hill-clans now use.
*Non-example.* "He'd hold a grudge, so he's stronger now." A grudge changes what he wants, not his numbers; only
result 5 changes a variant (he is already elite, so a 5 would be rerolled), and nothing changes his band.

### WE-09-8 Out of band: the barrow at P1

*Situation.* A P1 character pries open a barrow. Inside stands a barrow-wight: T3, **two bands above**. At
first perception (09.6.6) the advisory is lethal (P1 vs the wight: 3% / 99%), so 07's lethal warning fires in
the same turn, its sign the band tell ("it reads your stance before you move") and the wight's presence tell
("frost on the grave-goods; a handprint on the inside of the seal"). The `[WARNING]` block lists the exits: Yield
— not accepted (it drags to its lair; T-07-11); Retreat — the barrow door, a chase. The wight's list has a
parley row ("when the PC returns what was taken from its barrow"): if the character drops the grave-gold and
backs out, the parley is legal. *Boundary:* a P2 character gets the same warning (14% / 96%); a P3 character
meets a **trivial** wight (99.99% / 1.4%), with no warning and no band tell. *Non-example:* "The PC is only P1;
make the wight T1 so it's fair." Encounters belong to places; 09.3.1 forbids banding by the scene's needs and
06.9.7 forbids tuning.

### WE-09-9 A structural weakness: the swarm

*Situation.* A P1 martial character (sword S2) meets a rat swarm (`adv.rat_swarm`: T1 minion swarm, members 6,
2 each, pool 12). Advisory: easy. Every unshaped sword Strike harms it one rung lighter (S1: 1 Vitality), so
the PC's three Strikes a turn chip it; the swarm engages the PC and makes one roll against its Guard each turn
(06.10.5). The player asks what else might work. *Boundary pair:* a torch swept through it (06.5.10's
environment use, a `burst`-shaped fire through a feature) applies full harm several times over and the swarm's
fire vulnerability doubles it; a lantern smashed on the floor is a hazard feature it must cross. *The lesson the
data encodes:* the single-target fighter's weakness against swarms (R2 #12, Jason vs swarms) is real, and the
answer is a different kind of action, not a bigger number.

---

## Edge cases & adaptation anchors

### Reaching for an anchor

Three rules of this chapter are `Anchor: yes` (00.2.6) and are entered in the anchor index:

| Anchor | Intent verbs | Knobs (T-00-20) and allowed deltas |
|---|---|---|
| 09.2.4 Which archetype | identify, classify, what is it, size it up | none beyond the two enums |
| 09.4.8 Improvise an adversary | there is a creature, a monster appears, what attacks | band (one rung), role (enum), variant (enum), `targets` → members (a mob's count) |
| 09.10.2 Know the creature | recall, what do I know about, identify, study the beast | `dc` (tier ± one rung for a source: a bestiary book is a Precision lever, not a DC change), `reach_unit` (items), `time_cost` (beat → an interval of study) |

Other chapters' anchors that this chapter's creatures plug into: 06.4.3 Strike (a creature's attack is its
row), 06.5.2 Grapple (a constrictor's coils, a swarm's ungrabbability), 06.4.10 Called shots (a weak spot is
a recorded fact), 06.11.7 Yield and parley (a list's `parley_when`), 07.4.1 Yield (a disposition's acceptance),
08.3.10 Harvest (the archetype's body), 04.10 the Taking (its absorbable pool).

### Edge cases

- **A creature with no behavior row that fits.** The last row of every list is `always`; for an improvised
  creature with no list, 06.9.4's default family by role. A row that cannot be executed is false (09.7.1).
- **A creature asked to do what it cannot.** G4 for that intent; the redirect names what it can do (09.2.5).
  The player may still exploit the `cannot` ("the ghost cannot leave the mill — so I burn the mill").
- **A creature of two natures** (a wolf of flame, a skeleton dragon). Classify by what it *is* (09.2.4); add
  the second nature's level-3 creature tag where one exists (it widens loot and absorption gates, 00.5.4) and
  one power from the other archetype's library (counted in the premium). Never two archetypes.
- **A creature far above every PC band** (a god's avatar, a primordial). It is out of the bands: G4 to fight
  it as a foe; it is a situation (11) with clocks and terms, not an adversary. Dungeon World's "stat-less"
  monsters are the precedent [R: https://www.dungeonworldsrd.com/monsters/]. Its servants are adversaries.
- **A named NPC who fights.** Built from the nearest archetype by PR-09-1 (a bandit king on `arch.brigand`
  at T2 elite); its depth (12.11.1) decides Dying vs dead at 0 Vitality (07.2.10), its wants and secrets are
  15's.
- **A companion-shaped foe** (a rival adventurer with a hound). Two participants: the rival and the hound
  (each its own entry); the hound acts on its own turn, unlike a PC's companion (06.14) — the opposition is
  not bound by the PC's command economy.
- **An adversary mounted on another.** One participant per 06.15.1 (rider and mount share a band); the
  rider's line attacks, the mount's pace moves; both are defeated separately; the advisory counts both lines.
- **A resistance whose counter the PC holds only sometimes** (a silvered dagger and a plain sword). The
  advisory reads the PC's best attack: if the best is the dagger, the counter is held. The PC may switch
  weapons in the fight; the advisory is not recomputed for it (09.6.5).
- **A fight that changes kind mid-way** (the bandits flee and a troll arrives). Reinforcements or a new side
  recompute and re-show the advisory (09.6.5 b); a new side has its own morale clock (06.11.6).
- **Two sides that hate each other and the PC** (mixing result 1–2). Each side has its own behavior lists and
  attention; a creature's attention can fall on the other side's members by 06.9.3 (they are enemies to it).
  The advisory is computed per hostile side; the PC fighting both is the sum.
- **The PC wants to recruit, tame or bind an adversary.** Not this chapter's: taming is Handle with Presence
  and a license (05, 16); binding a spirit is a ritual (05); recruiting a yielded foe is 15 and 16. The
  adversary's `mind` and `cannot` say what is possible (a mindless creature cannot be recruited; a golem
  obeys its command word).
- **A creature fought in its lair.** The lair is a site (10) with its own features and hazards; the archetype's
  `kill_when` may switch near its young or its hoard; its `lair_adjacent` predicate turns on its drag rows.
- **A swarm against a PC with an area working.** Shaped effects apply their harm k times and a rung heavier
  (06.10.4–5): the swarm is the area caster's easy fight and the fencer's hard one — by design (R2 #12).
- **The adversary would be stronger with Focus it does not have.** It does not have it. Adversary Focus is
  09.3.8's, spent only on its listed powers and pool abilities (09.5.3).
- **An adversary with a pool ability that grants an extra reaction** (a stance). Never above two reactions a
  round (06.1.2); an adversary's reaction count stays its record's plus what the ability grants, capped.
- **Death of a recurring adversary.** Chapter 07's short ladder: lethal harm to a recurring or principal NPC
  makes it Dying, dead at `scene_end` unless stabilized or finished (07.2.10). A Nemesis can survive by that
  rule; finishing it is a declared beat (03 records it).
- **The same encounter met at different bands.** A place's T2 wolves are T2 whatever the PC's band; a P5 PC
  meets trivial wolves (no evidence quality worth having, 03) — the world does not grow with the PC.

## State touched

- **Entities** (00.6.1): adversary instances (`create_entity(kind: adversary, template_id)`), mob members
  as counts, summoned creatures (`eff.summon`), Nemesis names. **Reads** templates from
  `data/adversaries.yaml` and `data/archetypes.yaml`.
- **Quantities:** adversary Vitality (06/07 semantics), adversary Focus (09.3.8), a mob's pool.
- **Flags and facts:** `threat_band`, `variant`, `leader`, `phase`, `windup.<adv>.<attack>` (06),
  `defending.<adv>` (06), `side.defeat_disposition_toward_pc` (09.9.2), `knows_pc` (09.9.3), weak-spot facts,
  `witnessed.<pc>.<power>.<adv>` (09.5.4), Nemesis results.
- **Knowledge** (15): lore items delivered (09.10.2), observed items (09.10.3), adversaries' knowledge of the PC.
- **Clocks** created: `clk.09.reinforcements` (09.8.4); `clk.09.nemesis_hunt` (hidden, via 11; 09.9.3); the
  morale clock is 06's, sized by this chapter's nerve.
- **Conditions** applied by powers: only reserved and 06-defined ids (T-00-15, `data/conditions.yaml`) and 07's
  affliction carriers through `aff.*` exposures.
- **Ledgers:** the encounter's advisory log (word, percentages, ratio), the ruling ledger for improvised
  creatures (00.15.6), the chronicle via 11 for Nemesis boasts.
- **Tools used** (00.14.2): `create_entity`, `set_fact`, `update_quantity`, `apply_effect`, `apply_harm`,
  `apply_condition`, `roll_table` (`tbl.09.*`), `frame_check`/`roll_check` (fortune checks), `record_knowledge`,
  `seal`/`unseal`, `create_clock`/`tick_clock`, `generate` (08, 04), `get_active_triggers`.
  **New engine function:** `threat_advisory(encounter, pc)` (PR-09-4), required of the engine as specified;
  its reference implementation is `rules/_process/simulation/09_core.py:estimate`.
- **Hooks subscribed** by powers (00.10.2): `on_turn_start` (regeneration, Shrug), `on_turn_end` (auras),
  `on_hit_taken` (divide), `on_vitality_threshold` (second wind), `on_attack_hit` (riders).
- **Boundary handlers registered:** none new; reinforcement and Nemesis clocks run on `h.00.clock_auto`.
- **Triggers raised:** the out-of-band telegraph (09.6.6, on a perception fact); the advisory computation
  (09.6.5); the Nemesis promotion (09.9.3, on `victory_over_pc` and on an adversary leaving a conflict alive).
- **Runtime capabilities assumed:** RC-RNG (fortune checks, tables), RC-STORE, RC-SEAL (stat blocks sealed),
  RC-DATA (templates), RC-EVAL (powers through the substrate; the advisory's arithmetic), RC-QUERY (tag
  matching for pools and counters), RC-LOG.
- **Visibility** (00.6.4): stat blocks **sealed**; tells, `bloodied`, `down`, visible conditions, windups
  **shown**; learned items **available**; advisory word **shown** at hard and lethal (07's blocks), available
  otherwise; Nemesis results background until perceived.

## Interface requests

### To 00 (amendments proposed)

1. **Id prefix `pow.`** for adversary powers, defined in `data/archetypes.yaml#powers` (00.16.2). `ab.` is
   chapter 05's file; adversary-only mechanics need their own prefix so the loader knows where they live.
2. **00.3.7's Vitality envelope applies to `standard` (and from below to `minion`) templates.** Elite and solo
   variants multiply past it (× 2 / × 1.25 elite; × 4 / × 3 / × 1.75 / × 1.5 solo), as mob pools already do
   (06.10.2). Without this, a T1 elite could not exist (T1's ceiling is 5).
3. **The 00.3.7 coherence paragraph and `scales.yaml#bands.advisory_by_difference`** are superseded by
   T-09-9 and PR-09-4 (06 already proposed yielding them to T-06-13; this chapter's estimator replaces the
   table lookup). Proposed `owner_of_values: "09"` stays.
4. **T-00-4 / scales.yaml:** T4 and T5 typical Vitality references (26, 40 in T-06-12) are now **24** and **36**
   (inside the envelope; DL-09-04).

### To 03 (Tags & Evidence)

- **Challenge band of a conflict = `power_band(pc)` + the advisory offset at framing** (trivial −2, easy −1,
  fair 0, hard +1, lethal +2; clamped 1–5), instead of the opposing threat band. Evidence (09.8.9, 09.12.3):
  with 09's encounter budget and the foe's band as challenge band, 04's archer reaches tier 2/3/4 at median
  sessions 20/31/46 and never tier 5; with the advisory offset, 11/22/39 and tier 5 at 60 (59 of 100 runs),
  within 2–5 sessions of 04's targets. This is what closes I-005.
- `creature_tags` are listed most specific first on every archetype and adversary; `speaks` and `mind` per
  archetype; threat band on every adversary (03's requests): done.
- Proposed level-3 creature tags (`data/tags.yaml`, adopted at integration): `creature.spirit.place.water`,
  `.place.wood`, `.place.stone`; `creature.fiend.hellbeast.hound`; `creature.dragon.drake.fire`;
  `creature.beast.herd.caprine`. None is used by this chapter's data yet (all its tags exist), so adoption is
  optional; they let 13 gate regional loot more finely.

### To 04 (Recognition & Growth)

- `absorbable` on every archetype, with `eligible`, `cannot_absorb` and `signature` (09.11.3): done. Please
  record **`signature_of`** on the `gen_absorb.yaml` entries named as signatures (the list is
  `archetypes.yaml`'s `absorbable.signature` values; 46 archetypes name one). **Met** (revision I-020): 25
  entries carry it.
- **Narrow `no_pool: [creature.folk]`** to the human-like folk (human, elf, dwarf, halfling, orc, goblin):
  giant-kin and beastfolk have natural powers; `ab.abs_stone_grip` already gates on `creature.folk.giant`,
  which the current `no_pool` contradicts. **Met** (revision I-020); beastfolk gates added to Predator's Nose, Night Eyes,
  Gills and Scale Ward so gnolls, ratfolk and lizardfolk have entries.
- The pacing assumption (opposition at band to band+2) should become 09.8.2's 30/55/15 with 03's
  advisory-offset challenge band (above); if 03 declines, 04's great-deed gate should accept deeds at the
  current band for tiers 2–3.
- `witnessed` facts for the Taking are written per 09.5.4.

### To 05 (Abilities, Focus, Magic)

- Adversaries hold pool abilities by id (09.5.2); `pow.*` are the adversary-only mechanics (no `adversary_only`
  entries needed in 05's pool); witnessed facts per 09.5.4; Focus-emptying only at T5 and Focus drains only
  from T4, each with a tell (09.5.5); every adversary stores `effect_dc` per attribute (05's request d).
- I-009 is visible in this chapter's data: a band-1 caster with a zero-cost attack working is *fair* against
  one highwayman where a caster swinging a staff is *hard* (09.6.9). The zero-cost working matters.

### To 06 (Conflict)

- Every field 06 asked for is in every adversary record (T-09-14): Guard and the seven defenses, tempo, size,
  reaction kinds, windup on S4+ and shaped attacks, nerve and break, role (`default_behavior_role` in 06's
  four families, plus 09's own role), objective, weak spot, members, swarm, pace. Two actions for every
  template (no exception).
- **Adversary Fend at T3+** (06.6.5) is now in the arithmetic; with it, T4/T5 standard Vitality is 24/36 so
  that 06.10.6's targets hold (T-09-3). The re-run matrix (T-09-9) differs from T-06-13 in five cells, all
  harsher (Fend): P3 vs one T3 trivial → easy; P2 vs one T3 hard → lethal (39% wins, the edge); P4 vs three T3
  hard → lethal; P5 vs four T3 easy → fair; P5 vs a T4 mob of four hard → lethal. 06 may adopt T-09-9 as its
  matrix.
- OEQ-06-1 (T-06-ECON) is answered for bands 1–3: equal-band duels stay ≥ 99% (T-09-3), so the 3/2 economy
  holds with the real bestiary.
- `beh.default_*` remain 06's fallbacks; 09's lists are the norm (09.7.2).

### To 07 (Harm, Recovery, Death)

- Every archetype and adversary carries `lethal_context` (with causes), one of the seven dispositions,
  `kill_when` switches, `captive_fate`, `can_bargain`, `dread` (S1–S4), and wound sites on attacks that always
  land in one place (09.3.5, 09.9); no "kills outright" effect exists (09.5.6).
- The advisory → menu contract is met (09.9.5) on the final templates.

### To 08 (Items, Loot, Crafting)

- Every archetype satisfies `contract_09` (09.11.1). **Pool exception:** `arch.water_elemental` holds 2 tier-1
  entries on its amulet and ring bases (every other dropping archetype ≥ 3). Request: one more loot property
  gated on `creature.elemental.water` (e.g. a water-breathing or current-reading charm property) — or 08 marks
  the elemental's trophy base `item.armor.medium` acceptable (4 entries).
- `loot.flaw` uses `flaw.binding` (lich, tempter) and `flaw.thirsty` (hag, greater demon).

### To 10 (Exploration, Travel, Sites) and 13 (Starter setting; now the region's seed, 12.16, T-12-16 `ws.req.06_bestiary`, `ws.req.09_subset`, `ws.req.07_bargainer`) [revision: I-028]

- Encounter tables cite archetype groups or adversary ids, a home band, and which rows roll a complication;
  lairs above the home band are places, not wanderers (09.8.2). Encounter distance and notice are 10's.
- the region's seed lists the subset of the bestiary it fields (12.16.12); a pre-made setting (13) may add entries in `adversaries.yaml`'s owner-block "13"
  built by PR-09-1 (the roster line form of `09_data_adv.py`).
- the region's seed names the default bargainer for 07.5.5 if any (12.16.6); this chapter's `can_bargain` archetypes are the
  candidates.

### To 11 (Living World)

- Consume Nemesis results (09.9.3): boast rumors, hunt clocks, rank promotions of named victors; and
  `victory_over_pc` already flows from 07.
- Factions field adversaries by archetype and band; a faction's soldiers are `arch.soldier` etc. with the
  faction's org tag added (a pool-gate widening only).

### To 12 (DM Procedures)

- `reaction_roll: true|false` per archetype (12.11.2 step 4) — named `reaction_roll` to avoid a collision with
  06's combat `reaction`; tells by band (T-09-13); `threat_advisory` as the push filter and recovery cap
  (12.7.4–5).
- The rotation ledger (12.9.2) records 09.8.5's challenge axes.

### To 14 (Player's Guide)

- Codex views: a creature's learned items under its kind (`available`), the advisory word with its odds on
  request, the `[WARNING]` blocks at hard and lethal (07's formats).

### To 15 and 16

- 15: lore items as knowledge records; parley and yield read the lists' `parley_when` / `yield_when`.
- 16: companions are built on this chapter's templates at their band (00.17.1 Q8) where 16 wants an
  adversary-like line; the advisory treats a companion as one word gentler.

## Open empirical questions

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-09-1 | Does the closed-form advisory stay within one word of real play, not just of the reference simulation? | PR-09-4 with buffer 1.75 and Staggered margin 0.5 (09-estimator-tune.py) | **T-09-ADV**: log the advisory and the outcome of the first 200 played conflicts; target ≥ 85% of outcomes inside the word's band (e.g. a fair fight won without the menu) and no word whose observed menu rate exceeds 07's target by more than half again |
| OEQ-09-2 | Are mixed groups with a leader estimated well? | leader's nerve, strength interpolated (79% exact, 100% within one) | **T-09-MIX**: 100 mixed encounters from a world seed's tables (`12-world-seed-example.yaml`) simulated and estimated; if exact < 80%, model the escort's own break when the leader falls |
| OEQ-09-3 | Is the power premium the right price for riders and powers? | T-09-6 (0.06 / 0.03 / 0.10 / 0.04, cap 0.40) | **T-09-PREM**: extend the fight model with riders (knockdown, grab, bleed) and shaped powers; compare each bestiary entry's simulated difficulty with the standard's; refit the premiums so 90% of entries sit within fidelity 0.8–1.25 |
| OEQ-09-4 | Do the variant multipliers give the intended words with Focus and abilities in play? | T-09-5 (no-Focus fit) | **T-09-VAR**: 20 played solo fights per band; target solos won 55–85% with the PC spending Focus |
| OEQ-09-5 | Does the encounter budget produce the intended mix of words over a campaign? | 09.8.2 (fair or easier two in three; Δ 30/55/15) | **T-09-MIX-CAMPAIGN**: simulate a world seed's tables (`12-world-seed-example.yaml`) over 60 sessions of travel; target the word distribution easy 25 / fair 40 / hard 30 / lethal ≤ 5 at the region's home band |
| OEQ-09-6 | Do tells carry threat without numbers? | band tells T-09-13 + archetype tells | **T-09-TELL**: in 3 playtests, ask the player to rank five unseen creatures by danger from narration alone; target Spearman ≥ 0.8 against their bands |
| OEQ-09-7 | Do Nemesis results produce memorable rivals without punishing play? | tbl.09.nemesis | **T-09-NEM**: across 3 long campaigns, count rivals and the player's rating of their returns; target ≥ 1 rival per 10 sessions and no Nemesis result rated unfair |

