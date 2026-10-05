# 13 — The Starter Setting: the Thallen March

> Chapter 13 turns the rules into a place. Forty-one winters ago a silence fell on the Thallen Vale: every
> bell of the old kingdom of Orrow cracked in one night, and everyone inside the vale stood still where they
> were, as if listening. That silence, **the Hush**, is now ebbing a little every year. The land it gives back
> is free for the taking, its ruins are full of the old kingdom's bronze, and the people it froze — **the
> Stilled** — are beginning to wake. The player's character starts in **Tolling**, the market town at the
> vale's mouth whose **Last Bell** has rung every hour for forty-one years, on the morning that bell misses
> a stroke. The region is a West Marches map (one haven, five rings of danger, distance as the difficulty
> dial), a living sandbox (four full factions with running goal clocks and sealed linchpin fates, thirteen
> petty ones, one slow world-scale clock), and a complete data set: places, people, tongues, keepers, magic
> canon, bestiary, encounter tables, cases, stock, storied items, calendar and six ready-made characters,
> all generated and audited against every other chapter's schemas by
> `rules/_process/simulation/13-gen_region.py`. Nothing here adds a rule the other chapters lack; every
> procedure in this chapter is a binding of their procedures to this place.

## Design intent

**What this chapter serves.** Constitution goal 1 (the player feels free to try any idea) needs a world
with enough *stuff* in it that an idea always has something to touch: a person who wants something, a
place with a secret, a faction with a stake, a tool with a use. Goal 2 (the AI DM responds correctly)
needs that stuff to be *data*, so the DM never invents a fact it will later contradict. This chapter is
therefore mostly content in the shapes other chapters fixed — `[N]` description and `[D]` data — with a
handful of procedures (the opening, region binding at creation, regional generation) written in the
00.2.5 template.

**The four design commitments.**
1. **One idea, many uses.** The region is built around a single fictional engine — *sound holds back the
   Quiet* — that every subsystem can touch without special rules. A *true bell* is an ordinary item with
   a fact; a *hush-pool* is an ordinary hazard (00.9 conditions `cond.silenced` and `cond.deafened`); the
   Quiet waking is an ordinary clock; the Woken are an ordinary upbringing; the Hem's retreat is ordinary
   world-turn data. A newcomer learns one idea and can reason from it ("if I ring the bell, the hounds
   flinch"; "magic that needs words fails where sound fails"), and the DM can rule on anything the player
   tries from the same idea, citing data. [C:P3; 00.12.7; 05.7.2]
2. **Distance is the dial, and the dial is legible.** The West Marches shape of T-10-2 is kept exactly: a
   haven and five rings, each ring's band and danger shown to the player in T-10-2's words before any
   journey (10.3.4). The farther from Tolling, the older the silence and the stranger the land. Nothing in
   a ring ever exceeds home + 1 except a *place* the player chose to walk into, signposted by rumor and
   omen (09.8.2). [R6 B-15, B-R7; C:P2]
3. **A sandbox with a pulse, not a plot.** There is no scripted finale. Four full factions pursue goals on
   the World Turn, each with sealed linchpin fates written now; one slow world clock (the Quiet stirring)
   gives the long campaign a horizon the player can push back or ignore. The opening is an *incident*,
   not a quest line: the Last Bell's missed stroke and Harrowby's silent bell are two faces of one sealed
   case, and every scene of the first session offers a lead without requiring one (P16). [R6 B-01, B-08;
   R5 P-37; C:P16]
4. **Original, classic, and kind to a newcomer.** Every name, place and creature concept is original to
   this ruleset; the furniture (a market town, a ruined kingdom, goblins, wolves, a barrow, a hag, a
   dragon in the far mountains) is classic so that the player needs no lore to start. Recognition is
   voiced by mentors, orders, oaths and the bells themselves, never by an announcer (12.14.5). Death is
   real and telegraphed: the region's lethal places are named in rumor, marked by omens, and sit in the
   outer rings.

**What this chapter deliberately avoids.** (a) Lore the player must read: the premise fits in five
sentences (13.1.2); everything else is discovered. (b) A chosen-one frame: the PC is one of many people
drawn to the March, and the world runs whether or not they act (13.17). (c) Region-only mechanics: where
the setting needs a new mechanical idea (the Hush, true bells, waking the Stilled), it is expressed through
existing hazards, conditions, facts, clocks and Oracle odds, so every chapter's rules apply to it unchanged.
(d) Copying: no name, place or text is taken from a published setting.

**How to read this chapter.** Sections 13.1–13.4 are canon (what is true of this world), 13.5–13.14 are the
region's content (each section points at its data), 13.15 is the opening and the first-session teaching arc,
13.16 the ready-made characters, and 13.17 what the world does on its own. The data is canonical for every
id and number (00.1.4 item 5): `data/region_thallen.yaml` (places, people, keepers, tongues, tables, cases,
pregens, opening, clocks) and the owner-block fragments `data/contrib/{origins,licenses,factions,
adversaries,hazards,calendar}.13.yaml`.

## Rules

### 13.1 The region in one page

**13.1.1 Where the game begins.** `[N]` The Thallen March is the frontier of a lowland realm, **Esterlow**,
where it meets the valley of a dead kingdom, **Orrow**. The vale runs north from the market town of Tolling,
where the river **Wend** leaves it, for some ten days' walking to the **Mere of Sael**, the lake that drowned
Orrow's capital. Hills (the **Eastholt**, and beyond them the **Greyfells**) close it to the east; old forest
(the **Rookwood**, deepening into **the Gloaming**) and the **Sallow Fen** close it to the west. South of
Tolling lie the realm's farms and the Margravine's keep. The region is temperate, wet in spring, bright in
summer, cold but rarely snowbound in winter except in the Greyfells.

**13.1.2 The pitch (what the player is told at session zero, verbatim or close).** `[N]`
1. *Forty-one winters ago, on the longest night of the year, every bell in the old kingdom of Orrow cracked,
   and a silence fell on the vale. Everyone in it stopped where they stood.*
2. *That silence — people call it the Hush — is pulling back, a little each spring. The land it gives back
   is anyone's who can hold it, and its ruins are full of the old kingdom's bronze.*
3. *Some of the people it froze are waking up, forty years late, and want their farms back.*
4. *You are in Tolling, the market town at the mouth of the vale. Its one bell, the Last Bell, has rung every
   hour since the Hush fell. Folk say it is the only reason the silence never took the town.*
5. *The farther you go from Tolling, the older the silence and the more dangerous the land. Close by, it is
   farm country. Far off, legends live — and so do the things that killed them.*

**13.1.3 The tone.** `[N]` Classic fantasy with a hush in it: market days and wolf-haunted downs, goblin
tinkers and dwarf bell-founders, barrows, a hag in the fen, a dragon asleep on a far peak. Its particular
note is *quiet*: the uncanny stillness of the Hem, a field of people standing like scarecrows with moss on
their shoulders, a bell that has never missed a stroke missing one. The register is wonder and unease, with
warmth in the inns and danger at the edges; horror is suggested, never dwelt on (14's lines and veils govern
any closer look). The world is morally mixed: the Woken have a just claim the Margravine's law denies; the
cult that would wake the Quiet believes it is offering peace; the salvagers who strip the ruins also feed
the town.

**13.1.4 What the PC can do here, in one list.** `[N]` Salvage the Hem for Orrowan bronze and lost treasure;
take a side in the land war between the Woken and the Margravine's charter; hunt what the silence let in;
find the cult that is silencing bells; learn the old bell-craft and cast a true bell; push the Hem back
village by village; explore the old kingdom to its drowned heart; make a name, a holding, or an order of
one's own; or retire, when the player chooses, into the chronicle (11.13). None of these is required, and
the world moves on all of them whether the PC acts or not (13.17).

**13.1.5 The Truths of the March (optional, at session zero).** `[D]` + `[J:enum]` Following Ironsworn's
truths [R5 P-40], the player may set up to four world truths before play; each choice writes sealed facts
and Oracle odds that the data already supports, never new places or rules. The default (marked ★) is used
for any truth the player does not pick, and is the canon this chapter's other sections assume. Truths are
chosen once, at session zero, and recorded as facts with `source: player_accepted` (00.6.7).

| Truth | ★ Default | Option B | Option C |
|---|---|---|---|
| **T1 What the Hush is** | ★ a sleeping power, **the Quiet**, held asleep under the Mere by the bells of Orrow, half-woken when the Mother Bell cracked | a mercy: Orrow's last Bell-Prior rang the silence on purpose to stop the lowland army, and the Quiet is her rite still running (sets `canon.hush.cause = unsounding_by_choice`; the Quiet clock ticks one slower) | a wound: the Quiet is waking on its own and nothing anyone did caused it (sets `canon.hush.cause = waking_unbidden`; the Quiet clock ticks one faster each Year Turn) |
| **T2 The Woken** | ★ a Stilled wakes at once to a true bell within a day of its stilling; after that it is *set*, and a watch of true sound or the spring ebb wakes it at Oracle **Remote** (about one in ten), once a season (13.2.4) | the set wake readily: the Waking rule's odds are **Likely**, and the spring ebb's Woken arrive by the dozen | the set never wake except to the Mother Bell rung whole: the odds are **Impossible**, and every Woken alive is one of the few woken by a true bell in time |
| **T3 Spirits** | ★ the Hush stilled the vale's spirits; they return slowly behind the Hem (Oracle *Unlikely* in any place, *Likely* at a place with `resonance`) | the spirits never left the Rookwood and the Fen, and fight the Hush from there (*Even* in forest and fen) | the spirits are gone; only the Quiet answers in the vale (*Remote* outside the Gloaming) |
| **T4 The Margravine's charter** | ★ lawful, but it ends in three years unless the vale is settled; the old Treaty of the Ford that would uphold Woken claims is hidden | the treaty is lost for good (case `case.treaty_of_the_ford` is not written; the Woken's claim rests on force and sympathy alone) | the treaty is public and contested in the Margravine's court (the case is replaced by a debate, 15.8.3) |

*Worst case (J):* the DM records the wrong option for a truth the player chose; every option is a set of
facts and odds the data supports, so the error is a different but coherent world, visible in the codex's
chronicle and correctable at the next session start (class iv). Truths are never changed after the first
scene.

### 13.2 Setting canon: what is true of this world

**13.2.1 Canon is data, and the Oracle reads it.** `[D]` Everything this part states is held in
`region_thallen.yaml#canon` as facts with `source: data` (00.6.7). Two lists matter to resolution:
`canon_impossible` (the G4 test 2 of 01: *"Is this impossible for anyone in the setting?"*) and
`canon.facts` (settled world laws the Oracle treats as **Certain** or **Impossible** without a roll,
00.12.7). Anything canon does not settle is an ordinary Oracle question at the odds the established facts
suggest. Canon never grants: a fact here can make a method impossible, or supply a lever when the player
cites it, never hand the PC a result [SG-06; 01.3].

**T-13-1 `canon_impossible` (the Thallen March).** `[D]` (`region_thallen.yaml#canon.impossible`; each row is
G4 for everyone, with the license's or the situation's redirect.)

| Id | What no one can do | Scope |
|---|---|---|
| `ci.resurrection` | return the truly dead to life (a soul over Weyla's ford stays over; the Stilled are not dead) | magic |
| `ci.time` | travel in time, or undo what happened | magic |
| `ci.soul_making` | make a soul (golems, bell-wardens and homunculi have none) | magic |
| `ci.absent_mind` | read or speak into a mind not present in the scene | magic |
| `ci.unmaking_keepers` | destroy a keeper (they may be bound, starved, bargained with) | magic |
| `ci.transmutation` | make gold, silver, ringsilver or any metal from another substance; conjure lasting food, coin or goods (08's AI-1) | magic |
| `ci.regrowth` | regrow a lost limb, eye or organ (07's maims stand) | magic |
| `ci.sound_in_the_hush` | make or hear sound in hushed ground, except a true bell's peal and speech within it | world |
| `ci.spirits_in_the_hush` | have a spirit, ghost or summoned servant present in hushed ground | world |
| `ci.waking_the_stilled` | wake a Stilled by any means but the Waking rule (13.2.4) | world |
| `ci.harming_the_quiet` | strike, wound or slay the Quiet: it has no body | world |
| `ci.unaided_flight` | fly in one's own shape without magic, wings or a flying mount | world |

**13.2.2 The Quiet.** `[N]` + `[S]` Under the Mere of Sael sleeps a power older than Orrow: **the Quiet**, a
vast stillness that would still everything if it woke. It is not a keeper (it has no name and grants no
divine working), not a spirit of place (it stills them), and not a creature (it has no body: `ci.harming_the_quiet`).
Orrow's bell-founders held it asleep with **true sound**; their great bell, the **Mother Bell** of Sael, was the
lullaby. On Hush-eve, year 0, the Mother Bell cracked and the Quiet half-woke: that waking is **the Hush**. The
cause is sealed (`canon.hush.cause`, gate: the Bell-Prior's confession or the Mother Bell itself); the narrator
has only its permitted slice: *the bells stopped, and the silence came*. 13.1.5's truth T1 may change the cause.

**13.2.3 The Hush on the map.** `[D]` The Hush is expressed only through data the other chapters already read:
- **Hushed ground** is any place with the fact `hushed` (the Quietlands, the Mere, Sael, the Kingsbarrows) or a
  standing hazard `haz.thallen.hush_pool` / `haz.thallen.deep_hush` (owner-block of `hazards.yaml`, 10.12.8).
- Inside it every creature holds `cond.silenced` and `cond.deafened` (06's definitions, unchanged): no Talk, no
  speech-borne working (so no arcane and no divine working, 05.7.2's limitations), no hearing; a
  `trait.sense.loud` beat makes no noise, which is a Precision lever on Sneak there.
- Each watch inside is a dread exposure (07.11.2): S1 in a hush-pool (Endure, Resolve, Moderate), S2 in the deep
  Hush (Hard, Dire). A creature Staggered or Down inside at a watch boundary is **stilled** (13.2.4) — in the deep
  Hush at once, which is why `haz.thallen.deep_hush` carries `lethal_context: true` and the lethal warning (07)
  fires before anyone walks in.
- **True sound** is the counter: a bell with the fact `true_bell` (cast with ringsilver in Orrow's alloy, or
  consecrated to Saint Thallow with `rit.consecrate_ground` while it hangs in the circle) opens hushed ground
  within `band.far` for as long as it is rung (one action a round in a conflict, one interval out of one), and a
  full watch of ringing over a hush-pool ends the pool (a written world change, 10.2.3). A plain bell is an
  instrument like any other and is silent in the Hush.
- The Hem retreats each spring (`tbl.11.season_events.thallen.spring`, rows 1–4) and can advance if the Quiet
  stirs (`clk.thallen.quiet_wakes`, 13.17.3). Distance from Tolling is therefore also *time since the silence*.

*Why this shape:* every consequence of the setting's central idea resolves through existing conditions,
hazards, dread and Oracle odds, so the DM needs no new rule to adjudicate "I stuff wool in my ears", "I sing to
keep my courage up", or "I cast fire in the pool" — each has an answer in 06, 05 and 07 [C:P3; DL-13-06].

**13.2.4 The Waking rule.** `[D]` + `[J:flag]`

```
### 13.2.4  The Waking rule                                         [D] [J:flag]
Trigger [T]:        true sound reaches a Stilled (a true bell rung within band.far of them), or a
                    spring Season Turn's ebb passes their place (tbl.11.season_events.thallen.spring 1-4),
                    or the Mother Bell is rung whole (obj.mother_bell, cracked: false)
Loads in:           situation.exploration.*, situation.downtime.project
License check:      basic verb: verb.handle (ringing a bell is basic; a true bell needs no license)
Decisions (J):      1. OVER THEM [J:flag] "Is the true bell being rung within band.far of the Stilled,
                       in the same place?" True only when a fact or the scene's positions put the ringer
                       there (06's bands, or the same site area / building). False for a bell rung in
                       another area, or one not being rung (carried is not rung). Uncertain -> ask where
                       the ringer stands (it is a position, 00.6.1).
Computation [D]:    (a) FRESH: stilled less than a day ago (the fact stilled_at) -> wakes at once
                        (Certain). The Harrowby three are fresh until clk.thallen.harrowby_stillness
                        completes.
                    (b) SET (a day or more): one full watch of ringing over them, or the spring ebb
                        passing their place -> Oracle at REMOTE (13.1.5 T2 may make it Likely or
                        Impossible), at most once per Stilled per season (fact last_waking_try).
                    (c) the Mother Bell rung whole -> every Stilled in the March wakes (Certain).
                    A Woken keeps the body of the night they were stilled and ages from waking
                    (canon.woken).
Stakes:             none (no roll in (a) and (c); (b) is an Oracle question, not a check)
State writes:       npc.<id>.stilled = false; exists unchanged; the Waking House records them (fact);
                    an NPC woken becomes recurring (12.11.1) and rolls its reaction toward the waker
                    with +1 (12.11.2's shared-origin row does not apply; the waking is a recorded deed)
Narration may not imply: that a set Stilled is "about to wake", or that any other means could wake
                    them (ci.waking_the_stilled)
Worst case (J):     OVER THEM wrongly true: one Oracle question asked a season early or a fresh
                    Stilled woken from too far away (class i: one Stilled, one rung of timing).
Examples:           inside: Tamsin rings the recovered clapper in Harrowby's bell on the green; the
                      three in the north lane are within band.near: fresh -> all wake.
                    boundary: Pip rings a true handbell from the alehouse door; Nell Cask stands at
                      band.far in the lane -> over them; the miller's boy, round the corner in
                      another place, is not.
                    non-example: "I ring my plain handbell at them" -> not a true bell; nothing
                      happens, and the narration says so.
Anchor:             no
Basis:              [13.2.2] [00.12.7] [R5 P-40 (truths change odds)] [DL-13-05]
```

**13.2.5 The Stilled and the Woken.** `[D]` A Stilled is an NPC with the fact `stilled` (fresh or set): it does
not age, eat or breathe; moss grows on it; it is heavy as stone (moving one is an Exert beat against Hard,
`verb.exert`); it cannot be harmed by hunger, cold or Vitality loss (it is not a combatant), but it can be broken
(`cost.gear`-style destruction of a body is killing it: `exists: dead`, and the fordwardens will want it given to
the ford). A **Woken** is an ordinary person of the origin `orig.up.woken` or an NPC woken in play; their
Orrowan, their forty-year-old clothes and their claims are facts other NPCs react to (12.11.2 reads the
reaction modifiers; the Wakeful's status reads their membership).

**13.2.6 The world beyond the map.** `[N]` Esterlow (the lowland realm) lies south past Vantry Keep, with
cities, a crown and courts the March only hears of: news from it arrives through 11's spread rules as rumors
with sealed truth. Nothing south of Vantry Keep is a place in the graph; a PC who travels there leaves the
region, and the DM generates the journey by 10.1.8 at band 1, settled, until a new region is authored. No
city exists in the March (`canon.no_cities`), so no curio dealer exists either, except the regional exception
at Pell's yard (13.11.4).

### 13.3 Magic canon (05.7.10's eight items)

**13.3.1 Where magic comes from (item 2).** `[D]` The three sources in the world's own words
(`canon.magic.item_2_sources`):
- **Arcane** is *bell-grammar*: Orrow's art of knowing the true measures of things as its founders knew the
  measures of a bell. Anyone literate with a teacher or a text may learn it (05's default kept). Regional
  tightening (05's item f): texts in Orrowan also need `lic.lang.orrowan` at accented to study.
- **Divine** is the regard of a **keeper** (13.4). Anyone a keeper accepts may learn it: acceptance is standing
  Neutral or better with the keeper's faith, or an oath sworn (05.7.4).
- **Primal** is the living voice of the land and its spirits, stilled by the Hush and returning behind the Hem.
  Anyone a place accepts may learn it: one of the **places of acceptance** (13.5.6).

**13.3.2 What magic can never do (item 1).** `[D]` The seven magic rows of T-13-1 plus `ci.spirits_in_the_hush`.
05's defaults are all kept (true resurrection, time, souls, absent minds, destroying a keeper); the region adds
transmutation (08's request AI-1) and regrowth (07's request: none).

**13.3.3 Keepers (item 3).** `[D]` Six powers, 13.4 and `region_thallen.yaml#keepers`.

**13.3.4 Places of power (item 4).** `[D]` `resonance` on places (T-13-6's column) and the facts `consecrated`,
`tended_by`, `desecrated`, `dead_ground`, `haunted`, `hushed` (10.1.2's readable list; T-13-7). Dead ground is
rare: only the iron-bound Toll-tower of Caddow (primal workings are G4 there, 05.7.2). Desecrated ground: Mother
Sallow's Hollow. Hushed ground (13.2.3) is this setting's great "magic is wrong here" zone: it silences arcane and
divine workings and empties a place of spirits, but leaves primal workings of the elements and growth whose
source is present. *Mother Sallow* is not a place-spirit: her "acceptance" of a hexcraft or weather student is a
bargain (a commitment written first, 08.7.2's *bargained*), not 02.5.5's acceptance by a place; a PC who takes it
holds a primal school on a debt.

**13.3.5 Spirits (item 5) and what they understand (01's request).** `[D]` Oracle odds that a spirit is present
(`canon.magic.item_5_spirit_frequency`): **Unlikely** in any given place; **Likely** at a place with `resonance`;
**Even** in the Rookwood, the Gloaming and the Sallow Fen (their spirits held the Hush back at the treeline);
**Impossible** on hushed ground. Spirits of place understand heartfelt speech in any tongue and, where there is no
speech, gesture and offering; they do not understand lies (a Deceive aimed at a spirit is G4 by canon), written
words, or anything said inside hushed ground (they cannot be there). Talk with a spirit is therefore G1 with no
tongue license needed (01's WE-01-11 assumed exactly this).

**13.3.6 Is magic lawful (item 6)?** `[D]` Yes, with two limits (`canon.magic_lawful`): necromancy that raises
the dead is a hanging crime in Vantry lands (one of House Vantry's duties); a working with `trait.sense.visible`
inside Tolling's market or the bell-tower close is a method consequence (01.11.2) that reaches the Bellwardens as
a knowledge record. Woken find arcane workings unremarkable (Orrow was full of bell-mages); lowlanders find them
alarming (a reaction-roll modifier only where 12.11.2 lists one).

**13.3.7 Components, teachers and texts (item 7).** `[D]` 05's rites name components by 08's price band; the
March sells them under regional names (`canon.components`):

| Band | Regional component | Stands for |
|---|---|---|
| 1 | bell-dust (Pell's yard, by the pinch) | silver dust or thread; chalk, salt and iron filings |
| 1 | Wend water from the Ford-garden | running or blessed water |
| 1 | hearth-ash from a hearth unbroken a year | a keeper's customary offering (Aumbry) |
| 2 | Thallow's oil (blessed at the Last Bell) | water, salt or oil blessed at a keeper's shrine |
| 2 | moss from a Stilled (the Mossmothers will not touch it) | a thing the land would miss; a token of the cursed |
| 3 | ringsilver (one ingot casts a handbell) | a gating material (imbue); a gift the land would miss (call rain) |

Teachers and texts are settlement data (`places[].settlement.teachers`, `.texts`; T-13-9). The rites known in the
region are `rites_known` per settlement: ten in Tolling (all six divine rites the keepers practice plus
`rit.augury`, `rit.ward_threshold`, `rit.seal_the_way`, `rit.purification`), primal rites at the Greenwell and
Hollin Hall by acceptance, `rit.lay_curse` and `rit.lift_curse` only from Mother Sallow.

**13.3.8 Schools closed or opened (item 8).** `[D]` None closed, none opened. `deed.arcane.necromancy.raising`
and `deed.divine.pact` write conduct evidence when used on the unwilling (05's default). The hybrid table's four
**none** pairs (04, T-04-3) all hold in this setting (DL-13-09): Orrow's bell-grammar is learned in a study, not
the field (wilds × arcane); the Unsounding itself is the proof that formula cannot command the living silence
(arcane × primal); the keepers are named and the land's spirits and the Quiet are nameless, so no servant has both
(divine × primal); spirits are bargained with, not persuaded (primal × influence).

**13.3.9 Relics and the `magic` refusal (15's request).** `[J:flag]` A relic or storied item counts as magic for
`refusal.magic` only when its use is a visible working (`trait.sense.visible`) or the NPC holds a fact about its
properties; carrying one does not trigger the refusal. True when the NPC saw it work or was told what it does;
false for a sword the NPC has only seen worn. Uncertain → false (the refusal does not fire). *Worst case:* one
refusal fires or fails to fire for one request (class ii: the player sees the refusal and its lift).

### 13.4 Keepers and faiths

**13.4.1 The six keepers.** `[D]` (`region_thallen.yaml#keepers`; each keeper's faith is a faction, 11; a
divine caster's regard holds while their standing with that faith is Neutral or better, 05.7.4.)

| Keeper | What | Cares for (+) | Despises | Sign (`item.tool.implement.holy_symbol`) | Faith (faction) | Schools | Rites taught |
|---|---|---|---|---|---|---|---|
| **Saint Thallow, the Ringer** (saint) | Orrow's first bell-founder; true sound, watchfulness | courage, protection | cowardice; profaning | a bronze handbell | the Bellwardens | warding, exorcism, oaths | consecrate ground, great exorcism, oath-binding, funeral |
| **Aumbry of the Hearth** (god) | hearths, hospitality, the sick-bed | generosity, mercy | meanness | an iron hearth-key | the Hearthkeepers | healing, rites, warding | vigil of healing, purification, seasonal blessing, funeral |
| **Merrow the Weigher** (god) | law, true weight, the given word | justice, honesty | lies | a brass balance-pin | the Weigh-house | revelation, oaths, smiting | oath-binding, augury |
| **Weyla at the Ford** (god) | the dead and their crossing | piety, restraint | profaning the dead | a ford-stone (holed pebble) | the Fordwardens | rites, exorcism, healing | funeral, great exorcism, purification |
| **The Warden's Vow** (oath) | "No bell in my keeping falls silent while I breathe" | loyalty, protection | betrayal | a pewter lantern-over-bell badge | the Bellwardens | oaths, smiting, warding | oath-binding |
| **The Lantern-Man of the Fen** (pact) | Orrow's sunken keeper of lamps and lost travellers | loyalty (keep the bargain), indulgence (restraint −) | broken bargains | a corpse-candle in an iron cage | the Lantern-bound | pact, revelation | augury, oath-binding |

Every Acolyte school of 02.5.5 is served by at least one keeper (healing, warding, smiting, rites, oaths,
revelation, exorcism, pact). The Lantern-Man is the only keeper whose axis has a negative pole (he rewards
indulgence): 05.7.4's regard works unchanged, and his pacts write conduct evidence on the unwilling (13.3.8).

**13.4.2 Weyla, the default bargainer (07's request).** `[D]` In the March, Weyla answers at the door of death
for anyone dying outside hushed ground (`canon.default_bargainer = keeper.weyla`; `can_bargain: true`). 07.5.5's
*ask* reads her recorded wants first (that the dead be given to the ford; a restless dead laid; a Stilled woken
or given to the ford; a coin carried for one who died unburied in the Hem); the d6 `tbl.bargain_asks` is read
through them (`keepers[].bargain_asks`). Inside hushed ground no keeper answers (no speech, no presence): the
bargain option is struck there by 07's own rule (no bargainer) unless a `can_bargain` entity is present.

**13.4.3 Consecrated and tended places (03's and 07's requests).** `[D]` The facts 03's piety evidence and 07's
grave-chill cure read (T-13-7): consecrated — the bell-tower (Thallow), Aumbry's Hearth (Aumbry), the
Weigh-house and Vantry Keep's chapel (Merrow), the Ford-garden and the Nine Sisters (Weyla), the Chapel of the
Ringer (Thallow, untended); tended — the bell-tower (Bellwardens), Aumbry's Hearth, Harrowby's green and its
bell-pit (Hearthkeepers), the Ford-garden and the Nine Sisters (Fordwardens), the Greenwell (Mossmothers). Robbing
the Nine Sisters' grave-goods is therefore a piety −2 event under 03.12; robbing an untended ruin is not.

### 13.5 Peoples, tongues, names and setting origins

**13.5.1 Peoples present (02's request).** `[D]` All eight of 02's peoples live in or pass through the March;
none is marked absent (02.4.8; `absent_origins: []`), so every creation choice of 02 is open.

| People | Presence | Who they are here | Where | Common faiths |
|---|---|---|---|---|
| Human | common | Lowlanders of Esterlow (settlers, the Margravine's folk, most of Tolling) and Orrowans (the Woken, and border families outside the vale on Hush-eve) | Tolling, Harrowby, Vantry Keep, Bellhollow | Aumbry, Merrow, Thallow, Weyla |
| Halfling | common | the Wend-folk: river farmers, millers and bargees | Copsey, Tolling's water-stairs | Aumbry, Weyla |
| Dwarf | uncommon | Clan Gorrund: miners and the last founders of true bells | Gorrund's Delve, Tolling | Thallow, Merrow |
| Elf | rare | the Lingerers of Hollin Hall, who remember Orrow; the Hush stopped at their trees | Hollin Hall in the Gloaming | none (the wood itself) |
| Goblin-kin | uncommon | the Tinkettle clan, who moved into the empty Rookwood during the Hush: traders, tinkers, salvagers | Tinkettle, Tolling | the Lantern-Man |
| Orc-kin | uncommon | Clan Ruvag of the Greyfells; orc-kin sell-swords of the Red Lanterns | Ruvag's Fold, Tolling | none |
| Giant-kin | rare | ogre-blooded drovers; the hill giants of the Greyfells | the Eastholt, the Greyfells | none |
| Beastfolk | rare | the reedfolk of the Sallow Fen (lizard-kin) | Reedmere | the Lantern-Man |

**13.5.2 Lifespans (11's request).** `[D]` 11's defaults stand for every people (`calendar.13.yaml` restates
them); one regional rule: a Woken's age counts only waking years (`canon.woken`), so a Woken stilled at 25 who
woke last spring is 26, not 67, for 11.10.5's aging.

**13.5.3 Tongues and their fallbacks (01's and 02's requests).** `[D]` (`region_thallen.yaml#tongues`.) 02's nine
tongues keep their ids; the region names them in narration only. One tongue is added by owner-block:
**Orrowan, the bell-tongue** (`lic.lang.orrowan`, `data/licenses.yaml owner-block 13`), spoken natively by the Woken,
sung in the Bellwardens' offices, and carved on every ruin in the vale. It is the region's **second tongue**
(02.2.2's default tongue pick and learning pick). Its crude fallback (01.18) is 02's: gesture, tone and shared
nouns, DC +5, reach Limited — and Orrowan shares many nouns with Plain speech (bell, field, kin, bread, the
keepers' names), which is why the fallback is usable at all. An Orrowan inscription without the license yields
numerals, seals, the bell-sign and the keepers' names only. 02's Old Tongue is, here, **the Deep Tongue** of the
lowest vaults of Sael and the Ringsilver Deeps: older than Orrow, dead, at most accented.

| License | Regional name | Who speaks it |
|---|---|---|
| `lic.lang.common` | Plain speech | everyone |
| `lic.lang.orrowan` | Orrowan, the bell-tongue | the Woken; old border folk; the Bellwardens' offices; every ruin |
| `lic.lang.old_tongue` | the Deep Tongue | no one living |
| `lic.lang.elvish` | Lingerers' speech | Hollin Hall |
| `lic.lang.dwarvish` | Gorrund-tongue | Clan Gorrund |
| `lic.lang.goblin` | Tinkettle chatter | the Tinkettle clan |
| `lic.lang.orcish` | Orcish | Clan Ruvag; the Red Lanterns' orc-kin |
| `lic.lang.giantish` | Giantish | the Greyfells' giants and drovers |
| `lic.lang.kinspeech` | reed-talk | the reedfolk |
| `lic.lang.cant` | cellar-talk | the Cellar Kin and the Wend's smugglers |

**13.5.4 Setting origins (02.4.8).** `[D]` Two origins are added in `origins.yaml`'s owner-block "13" (with their
packs in `kits.13.yaml`); both pass PR-02-9 in the generator.
- **Woken of Orrow** (`orig.up.woken`, upbringing): you grew up in Orrow, were stilled on Hush-eve and woke when
  the Hem passed you. Three units exactly: Focus 4 (1), `lic.lang.letters` (1: Orrow's bell-schools taught
  everyone), Orrowan at accented (1). Wealth destitute (1 coin), a pack of forty-year-old clothes and a charm of
  dead Orrowan pennies. Open to the peoples who lived in Orrow (human, halfling, dwarf, giant-kin). Ties suggest
  `org.crown.royal` (the Wakeful) and `org.faith.temple` (the Bellwardens). Bond seeds: *kin — a younger brother or
  sister outside the vale on Hush-eve, old now, in Tolling*; *lost — the one whose hand you were holding when the
  bells stopped, who has not woken*.
- **Salvager (Hemrunner)** (`orig.life.salvager`, livelihood): you went into the edge of the silence for the old
  kingdom's bronze. Seven trainings (stealth, survival, navigation, history, thievery, athletics, engineering);
  default Focused on stealth and navigation; kit of rope, torches, crowbar, dagger, a plain signalling handbell and
  a salvage sack; ties to `org.company.exploring` (Pell & Daughters) and `org.outlaw.smugglers` (the Cellar Kin);
  hooks *thread: you saw something moving among the Stilled on your last run* and *debt: you owe Pell & Daughters
  for your kit*.

**13.5.5 Names (02's and 12's requests).** `[D]` Nine d20 name tables, one per people and two for humans
(`tbl.thallen.names.lowlander`, `.orrowan`; `.halfling`, `.dwarf`, `.elf`, `.goblin`, `.orc`, `.giant`,
`.reedfolk`), each 20 given and 20 family names; the engine rolls both and offers three (02.9.6; 12.11.1). A
human NPC's table follows their origin: Woken and border families roll Orrowan, settlers roll Lowlander. 12's
generic name tables are used only for a people the region does not list (none).

**13.5.6 Places of acceptance (02's and 05's requests).** `[D]` Where a primal caster is accepted (02.5.5's
`pc.accepted.primal.<school>`; `region_thallen.yaml#places_of_acceptance`):

| Place | Spirit | Schools it accepts | What it asks | Who brings candidates |
|---|---|---|---|---|
| the Greenwell (the Gloaming) | the Lady of the Greenwell (water) | growth, spirits, beastkin | leave one living thing better than you found it each season | Ilsabet Grey, the Mossmother |
| the Weir Stones (the Reedwend) | the Weir-voice (water) | weather, elements | never dam running water | the bargees know the stones |
| Hallow Crag (the Eastholt) | the Old Man of the Crag (stone) | elements, shapeshifting | a stone carried from another hill laid at his foot | Founder-Mother Ama Gorrund |
| the Thornheart (the Gloaming) | the Heart-tree (wood) | growth, shapeshifting, spirits | a season guarding the Gloaming's edge | Lisanne of Hollin Hall |
| Mother Sallow's Hollow (the Fen) | a hag, not a spirit: a bargain (13.3.4) | hexcraft, weather | a thing of your own she names | Mother Sallow herself |

The asks are commitments (00.6.1) written at acceptance; breaking one is a standing step with the
Mossmothers (11) and, for a primal caster, an evidence event on the conduct the ask names (03).

### 13.6 Geography: the place graph

**13.6.1 The rings (T-10-2, kept).** `[D]` The region's 64 places (1 region, 14 areas, 10 settlements, 15
buildings, 14 sites, 10 landmarks) are joined by 39 routes (78 links). The generator computes each place's
distance from Tolling by the shortest *known* route and checks it against T-10-2's bounds (1 day = 2 watches,
10.3.5); every place passes. The secret causeway to Sael is excluded until found (it would bring Sael to 19
watches: ring 4 by distance, which is exactly why Pell keeps it secret).

| Ring | Words to the player (T-10-2) | Areas (home band, danger) | Settlements and sites (watches from Tolling) |
|---|---|---|---|
| 0 | safe under the walls | — | **Tolling** (haven) |
| 1 | farm country; trouble is rare and small | the Wend Meads (1, settled), the Brightfields (1, settled), the Lowroad (1, settled) | Copsey 1, Harrowby 1–2, Vantry Keep 2, the Bell-pit under Harrowby 1, the Treaty Stone 2 |
| 2 | the borderland: wild, but folk pass through | the Rookwood Eaves (1, wild), the Standing Downs (2, wild), the Eastholt (2, wild), the Reedwend (2, wild) | Tinkettle 3, the Weir Stones 3, the Standing Folk 3, Bellhollow 4, Gorrund's Delve 4, the Bellhollow Undercroft 4, the Copper Delving 5, Hallow Crag 5, the Hem-cairns 5, the Nine Sisters 5 |
| 3 | the deep wilds: dangerous things live here | the Hem (3, perilous), the Gloaming (3, wild), the Sallow Fen (3, perilous) | the Chapel of the Ringer 7, Hollin Hall 8, Orsolin Manor 8, Reedmere 8, the Ringsilver Deeps 8, the Greenwell 9, the Thornheart 10, Mother Sallow's Hollow 10 |
| 4 | the old lands: only the strong travel here | the Quietlands (4, perilous), the Greyfells (4, perilous) | Ruvag's Fold 12, the Toll-tower of Caddow 13, Wyvernscar 14, the Kingsbarrows 15 |
| 5 | the far reaches: legends live here, and so do the things that killed them | the Mere of Sael (5, deadly), the Cinderhorn (5, deadly) | Sael 21, the Cinder Hall 22 |

**13.6.2 The shape on the ground.** `[N]` Tolling sits where the Wend leaves the vale. North, the Brightfields
(resettled thirty years) give way to the Standing Downs (freed in the last fifteen), then the Hem (this year's
edge of the silence), then the Quietlands and the drowned capital. West, the Rookwood deepens into the Gloaming
and slopes into the Sallow Fen; the Reedwend is the water road there. East, the Eastholt's copper hills rise to
the Greyfells and, at the end of them, the smoking Cinderhorn. South is the Lowroad to Vantry Keep and the realm.
Three roads matter: the north road to Harrowby, Pell's cart-track over the downs to Bellhollow, and the Eastholt
track to the Delve. Everything beyond is trackless, river, or a secret.

**13.6.3 The place record (10.1.2).** `[D]` Every place in `region_thallen.yaml#places` carries every 10.1.2
field (the generator fills nulls explicitly, so no field is ever "missing"): `place_kind`, `parent`, `band`,
`danger`, `safe`, `rest_site`, `terrain`, `climate` (temperate; highland for the Greyfells and the Cinderhorn —
10.11.2's existing regimes, so no new weather regime is needed), `nav_tier`, `forage_tier`, `game_tier`
(null = 10's terrain defaults), `openness`, `landmarks`, `water_source`, `grazing`, `encounter_table`,
`hazards`, `resonance`, `settlement_scope`, `known`, `discovered`, `site`, `state_log`, `links`, and
`watches_from_haven`. Everything in rings 0–1 and every area is `known` at the start (the town knows its own
country); ring 2–5 settlements and sites are known by rumor or not at all (`visibility` follows 10.1.5).

**13.6.4 The haven.** `[D]` Tolling is the region's one haven (`safe: true`, `rest_site: haven`; 10.2.3): no
time-tick check runs there and ventures end there. Its inn (the Cracked Clapper) and Harrowby's alehouse are rest
sites of kind haven; Harrowby itself is **not** a haven (a village becomes one only by 10.2.3's hospitality rule:
standing Friendly or better with its people). Tolling can lose its safety only by a written world change: the
Hushed Choir's goal completing (13.7.4) or the Quiet rising (13.17.3).

**13.6.5 Sites (10.13).** `[D]` Fourteen sites are placed by hand, each with theme, domain, band, size and an
authored objective (10.13.10's closed kinds); danger and explore tier are computed from theme and domain (+1 rung
at band 4–5), and the two clocks from the size (`sites.yaml#sizes`).

| Site | Ring | Theme × domain | Band | Size | Objective |
|---|---|---|---|---|---|
| the Bell-pit under Harrowby | 1 | ancient × crypt | 1 | small | the lost: Harrowby's stolen clapper (the opening's case) |
| the Nine Sisters | 2 | ancient × barrow | 2 | small | hoard: nine bell-priestesses' grave-goods (tended: piety) |
| the Bellhollow Undercroft | 2 | ravaged × underkeep | 2 | medium | hoard: the bell-town's treasury |
| the Copper Delving | 2 | infested × mine | 2 | medium | sealed way: the lower gate to the Ringsilver Deeps |
| the Chapel of the Ringer | 3 | hallowed × temple | 3 | medium | the lost: Thallow's Handbell (storied) |
| Orsolin Manor | 3 | haunted × stronghold | 3 | large | the lost: the true Orsolin Vey, stilled |
| the Thornheart | 3 | wild × tanglewood | 3 | medium | place of power: the Heart-tree |
| Mother Sallow's Hollow | 3 | corrupted × fen | 3 | medium | guardian: Mother Sallow (who would rather bargain) |
| the Ringsilver Deeps | 3 | ancient × mine | 3 | large | hoard: the last ringsilver lode, kept by the Deep Warden |
| the Kingsbarrows | 4 | haunted × crypt | 4 | large | guardian: the Barrow-King, holding Clapperfall |
| the Toll-tower of Caddow | 4 | ancient × tower | 4 | small | the lost: Bell-Prior Aude's journal (dead ground) |
| Wyvernscar | 4 | wild × cavern | 4 | medium | guardian: the wyvern matriarch |
| Sael, the Drowned Bell-city | 5 | ancient × underkeep | 5 | vast | place of power: the Mother Bell (and Aude, stilled beside it) |
| the Cinder Hall | 5 | ravaged × cavern | 5 | large | guardian: Ashgorge on Orrow's tribute |

Sites generated in play roll `tbl.thallen.sites` (d12 by ring) and take the ring's terrain from
`terrain_by_ring` (10.1.8); a generated site in the vale proper at ring 3+ carries hush-pools in d3 of its
areas (ring 3) or the deep Hush throughout (rings 4–5).

**13.6.6 Settlements: tier, market, crafters, teachers, hire, sentries (08, 15, 16).** `[D]`
(`places[].settlement`; T-13-9 summarizes.)

| Settlement | Tier | Values from | Common / scarce goods | Crafters (grade) | Max hire band | Sentry floors (day / night) |
|---|---|---|---|---|---|---|
| Tolling | town | the Bridgemoot | grain, furs, timber, salvage bronze / salt, iron, spices, wine | smith-founder Hrolla (expert), scribe Quillon (expert), remedies Marrow (trained), joiners, leather, textiles | 2 | ringers of the Last Bell suspicious / suspicious; bridge gate suspicious / alert; Pell's yard unaware / suspicious; Weigh-house suspicious / suspicious |
| Copsey | village | the Hearthkeepers | grain / iron, salt | the Mill-mother's ovens (expert cookery) | 1 | — |
| Harrowby | village | the Hearthkeepers | grain / iron, salt, wine | a farrier (trained) | 1 | — |
| Vantry Keep | town | House Vantry | grain, iron, cloth / salvage | armorer, saddler (expert) | 2 | keep gate suspicious / alert; muniment room suspicious / suspicious |
| Bellhollow | camp | Pell & Daughters | salvage / everything else | — | 1 | palisade gate suspicious / alert |
| Gorrund's Delve | village | Clan Gorrund | iron (and copper, tin, bell-metal) / grain, cloth, wine | Founder-Mother Ama (master), jewellers (expert) | 1 | stone gate suspicious / alert |
| Tinkettle | camp | the Tinkettle Clan | tinker-work, salvage / salt, grain | Old Nackle (expert artifice) | 1 | warren mouth suspicious / suspicious |
| Hollin Hall | village | the Mossmothers | — / salt, iron, wine, spices (they give, or do not) | bowyers (master) | 1 (they do not hire out) | the holly ring alert / alert |
| Reedmere | camp | the Lantern-bound | eels, reed-cloth / iron, salt, grain | reed-cloth weavers (expert) | 1 | stake-path gate suspicious / suspicious |
| Ruvag's Fold | camp | Clan Ruvag | furs / salt, grain, wine, iron | — | 1 | fold dogs suspicious / alert |

Market depth, gluts and asking prices are 08's (08.8.4–08.8.5); "common" and "scarce" are the settlement facts
08.8.5's trade-goods row reads. Teacher odds: 15.11.2's Oracle rungs, overridden by the data where a named
teacher exists (then no Oracle is asked: the teacher is there).

**13.6.7 Fight locations (06's request).** `[D]` Seven places carry feature lists in 06's feature kinds
(`fight_locations`): the Wend Bridge (chokepoint, height, the river, loose carts), Harrowby green (the hush-pool's
edge as a hazard that silences casters, the bell-frame as cover, the duck-pond's mud, the alehouse door), the
Bell-pit (a casting-hole drop, a choke stair, dust), the Standing Folk (thirty stone-heavy Stilled as cover inside
a hush-pool), Bellhollow (palisade, cracked tower, salvage heaps), the Chapel of the Ringer (tower stair, the porch
choke where Jonquil Pell stands, a nave pool ended by ringing the tower bell), the Weir Stones (the weir's fall).
Regional chase ground: `tbl.thallen.chase_ground` (d6 for Tolling, the open country, and the fen; 06.12).

### 13.7 Factions

**13.7.1 The powers of the March.** `[D]` Nineteen factions in `factions.yaml`'s owner-block "13"
(`data/factions.yaml owner-block 13`), each conforming to 11.3.1 and to an 11.3.18 template, with every rating
0…tier + 2 and summing to 4 + 2 × tier (checked). **Four are full at the start** (11.3.2: tier 2+, or named by a
thread — the Choir by the opening case); fifteen are **petty** (one d6 a week on a 6-segment goal, 11.3.16) and
become full by 11.3.2 the moment the PC meets an officer or gains status with them. Blades' starting-situation
triangle is built in [R5 P-37]: the Margravine and the Woken want the same land; Pell profits from both and
answers to neither; the Bellwardens hold the line everyone needs; the Choir works inside it.

| Faction | Kind (template) | Tier, hold | Force / Cunning / Wealth / Sway | Temperament, stage | Goal (scope, kind) | Clock at start |
|---|---|---|---|---|---|---|
| **House Vantry**, Margraves of the Wend | noble (crown_noble) | 3, strong | 3 / 2 / 3 / 2 | cautious, flourishing | charter and settle the Standing Downs before the crown's term runs out (regional, dominate → the Wakeful) | 3/12 |
| **The Bellwardens of Tolling** | monastic order (faith_temple) | 2, strong | 2 / 1 / 1 / 4 | steadfast, flourishing | raise the Hem-tower at Bellhollow with a true bell in it (local, grow) | 2/8 |
| **Pell & Daughters**, salvagers | trading company (company_trading) | 2, weak | 1 / 3 / 4 / 0 | mercantile, rising | open the drowned road to Sael before the Margravine can charter the Mere (regional, change) | 4/12 |
| **The Hushed Choir** | doomsday cult (cult) | 1, strong | 1 / 3 / 1 / 1 | secretive, rising | silence the Last Bell (local, change) — `clk.thallen.choir_goal`, the opening case's opposition clock | 1/8 |
| The Wakeful | royal claimants (crown_noble) | 1, weak | 1 / 1 / 1 / 3 | zealous, rising | seat an Orrowan steward in Harrowby's old hall (take) | 1/6 |
| The Bridgemoot of Tolling | civic council (crown_civic) | 1, strong | 1 / 1 / 3 / 1 | mercantile, flourishing | a toll-charter that keeps soldiers off the bridge (grow) | 0/6 |
| The Hearthkeepers of Aumbry | shrine (faith_shrine) | 1, strong | 0 / 1 / 2 / 3 | cautious, flourishing | a second Waking House at Harrowby (grow) | 1/6 |
| The Fordwardens of Weyla | mission (faith_shrine) | 0, strong | 1 / 1 / 0 / 2 | steadfast, flourishing | give the Standing Folk to the ford (stir) | 0/6 |
| The Weigh-house of Merrow | temple (faith_temple) | 1, strong | 0 / 1 / 2 / 3 | cautious, entrenched | a true copy of every Brightfields claim (grow) | 2/6 |
| The Lamplit Library | scholars and bell-mages (guild_scholarly) | 0, strong | 0 / 2 / 1 / 1 | cautious, flourishing | a reading of the Unsounding's bell-grammar (stir) | 2/6 |
| The Mossmothers | druidic circle (order_druidic) | 0, strong | 1 / 1 / 0 / 2 | cautious, flourishing | holly-rings round every hush-pool in the Eaves (grow) | 1/6 |
| Clan Gorrund of the Eastholt | lineage and founders (guild_craft) | 1, strong | 2 / 0 / 3 / 1 | steadfast, declining | take back the Copper Delving (take) | 1/6 |
| The Tinkettle Clan | goblin tribe (clan_family) | 1, strong | 2 / 2 / 1 / 1 | mercantile, flourishing | a goblin stall in Saltgate Square every market day (grow) | 2/6 |
| The Hemrats | bandits (outlaw_bandits) | 0, strong | 2 / 1 / 1 / 0 | aggressive, rising | every salvage cart on the downs paying toll (take) | 1/6 |
| The Cellar Kin | thieves and smugglers (outlaw_thieves) | 0, strong | 0 / 2 / 2 / 0 | secretive, flourishing | a cellar-way under the Weigh-house (take) | 2/6 |
| Clan Ruvag | orc tribe (clan_family) | 1, strong | 3 / 1 / 1 / 1 | aggressive, flourishing | the Eastholt's summer grazing from Clan Gorrund (feud) | 2/6 |
| The Wolfwatch | hunters (order_hunters) | 0, strong | 2 / 1 / 0 / 1 | steadfast, rising | find and burn the hush-hounds' den (stir) | 0/6 |
| The Red Lanterns | free company (company_mercenary) | 1, strong | 3 / 1 / 2 / 0 | mercantile, flourishing | a year's contract from whoever pays (grow) | 1/6 |
| The Lantern-bound | the Lantern-Man's faith (cult) | 0, strong | 0 / 2 / 1 / 1 | secretive, flourishing | a lantern on the Treaty Stone for a year and a day (stir) | 3/6 |

Every faction also carries (data): `values` (its reputation valence, 11.7.6), `patron_deeds`, a rank ladder from
11's `rl.*` and its sittings (quarter days for most; the Choir at the new moon; Gorrund at Founders' Pour), three
duties (its officers' absolute refusals, 11.3.17), `fields` (what it sends, by archetype), `boon_base` and
`boon_signature` (08.7.2: Vantry a sword with `prop.commanding`; the Bellwardens a handbell with
`prop.ward_fear`; Pell a climbing kit with `prop.sig_ruin_lore`; the Choir a cloak with `prop.stalkers`; Gorrund a
hammer with `prop.sig_deep_forged`; the rest in data), relations, seat and holds.

**13.7.2 Relations at the start.** `[D]` The rivalries that drive 11.3.7's agenda: House Vantry ↔ the Wakeful
−2 (the land); House Vantry ↔ Pell −2 (the Mere's bronze and the untithed salvage); the Choir → the Bellwardens
−2 (the Choir's view: gaolers of the sleepers; the Bellwardens do not yet know the Choir exists: 0); Pell ↔ the
Hemrats −2; Gorrund ↔ Ruvag −2; House Vantry → the Weigh-house +2; the Bellwardens → the Hearthkeepers +2.
The full list is each record's `relations`.

**13.7.3 Linchpins and their sealed fates (11.3.10).** `[S]` + `[D]` Every faction names one to three linchpins
whose four fates (`dies`, `captured`, `turned`, `exposed`) are written now as effect lists and sealed. The
narrator sees none of this until the writes surface as traces. The full factions':

| Linchpin | Faction | dies | captured | turned | exposed |
|---|---|---|---|---|---|
| Margravine Aldis Vantry | Vantry | hold −1, declining, a succession; the Wakeful hold +1 | hold −1; next action strike/court the captor | relation to the Wakeful +3; goal becomes "settle the vale under the Treaty"; Wakeful hold +1 | hold −1, a scandal; Wakeful +1; the treaty public |
| Reeve Corbin Hask | Vantry | Tolling's tithe lapses to the next quarter day; Cellar Kin hold −1 | the tithe lapses | reveals the treaty secret to the PC; Bridgemoot relation −1 | Cellar Kin hold −1; Bridgemoot → Vantry −1; Hask dismissed |
| Prior Hollis Brede | Bellwardens | hold −1, succession, **Choir goal clock +2** | hold −1, Choir clock +1 | reveals the confession to the PC; Wakeful +1 | hold −1, declining, scandal; Wakeful → Bellwardens −2 |
| Warden-Sergeant Bram Ottery | Bellwardens | hold −1 | strike/court the captor | hold −1 | hold −1 |
| Mother Hesper Pell | Pell | hold −1; goal becomes "wake Jonquil"; succession | hold −1; court the captor | reveals the causeway to the PC | the causeway known region-wide; a salvage rush (`sit_t.road_of_knives`); Vantry → Pell −1 |
| Wick Pell | Pell | hold −1; Bellhollow abandoned until a new crew-boss | court the captor | hold −1 | hold −1 |
| Sister Ysmay (the Cantor) | Choir | hold −2, declining | hold −1; strike/court the captor | **the Choir collapses**; reveals the filed pin | Choir hold −2; Bellwardens hold −1 and a scandal; Bellwardens → Choir −3 |
| Dunstan Fell | Choir | hold −1 | interrogable (n2.p4) | reveals the Cantor to the PC; hold −1 | hold −1 |

The petty factions' linchpins (Lady Orsolin and the true Orsolin for the Wakeful; Alderman Cotter; Abel Marrow;
Gammer Thrush; Justiciar Ferrant; Ansel Quillon; the Mossmother; Founder-Mother Ama; Old Nackle; Red Gil; Lark
Mossbank; Ruvag Two-Axe; Fenna Underby; Captain Ghessa; Ssessa) are in the same file with the same four fates.
*Why a fate per linchpin:* a world that will lose its tithe if the reeve dies has known so since the reeve was
written, which makes killing him a choice, not a gamble (11.3.10).

**13.7.4 The Choir's goal is the opening's countdown.** `[D]` `clk.thallen.choir_goal` is both the Hushed
Choir's goal clock (ticked only by its World Turn actions, 11.3.6, and by the linchpin fates above) and
`case.silent_bells`' opposition clock (15.9.13), so the case and the faction cannot disagree. Its completion
writes: the Last Bell silent; a situation of template `sit_t.cursed_ground` on Tolling (a hush-pool over the north
ward until a true bell is rung there for a watch); `clk.thallen.quiet_wakes` +3; the Brightfields' danger
settled → wild. Tolling stays a haven (its rest site and no-check rule are untouched), but its north ward is
hushed ground: the town's safety now visibly depends on someone ringing true. With no PC interference the
re-run World Turn simulation (13.17.2) puts this at a median of **week 11** (p10 week 8, p90 week 16): around the
end of spring, before Longday Fair — which is what Dunstan Fell was told to aim for.

**13.7.5 The org-tie map (02.9.5; 11's PR-11-4).** `[D]` A faction tie names an `org.*` kind; this table names
the faction that holds it here (first matching row; `factions.org_tie_map`). Every kind any origin suggests is
covered (checked).

| Org kind | Faction | Exceptions |
|---|---|---|
| clan.family | the Bridgemoot (Tolling's bridge-families) | a Woken PC: the Wakeful |
| clan.tribe | the Tinkettle Clan | an orc-kin PC: Clan Ruvag |
| clan.lineage | Clan Gorrund | a Woken PC: the Wakeful |
| crown.royal | the Wakeful (Orrow's claimants; Esterlow's crown is off the map) | — |
| crown.noble, crown.military, order.knightly | House Vantry | — |
| crown.civic, guild.merchant | the Bridgemoot | — |
| faith.temple, order.monastic | the Bellwardens | a PC sworn to Merrow: the Weigh-house |
| faith.shrine | the Hearthkeepers | keeper Weyla: Fordwardens; the Lantern-Man: Lantern-bound; Thallow or the Vow: Bellwardens |
| faith.mission | the Fordwardens | — |
| order.arcane, guild.scholarly | the Lamplit Library | — |
| order.druidic | the Mossmothers | — |
| order.hunters | the Wolfwatch | — |
| guild.craft | Clan Gorrund | — |
| company.trading, company.exploring | Pell & Daughters | — |
| company.mercenary | the Red Lanterns | — |
| outlaw.thieves, outlaw.smugglers | the Cellar Kin | — |
| outlaw.bandits | the Hemrats | — |
| cult.forbidden, cult.doomsday | the Hushed Choir (the PC knows it exists and one member's face; the Cantor stays sealed) | — |
| outlaw.assassins, cult.fiendish, cult.undeath | **none** in the March: the tie is held open (02.9.8) | — |

**13.7.6 Institutions per deed branch (04's V3 and V9).** `[D]` What `institutions_matching(branch, region)`
returns here, in order (`factions.institutions`): martial — House Vantry, the Bellwardens, the Red Lanterns;
guile — the Cellar Kin, Pell; wilds — the Wolfwatch, Pell, the Mossmothers; lore — the Lamplit Library, the
Weigh-house; arcane — the Lamplit Library, House Vantry (its court magus); divine — the Bellwardens, the
Hearthkeepers, the Weigh-house, the Fordwardens, the Lantern-bound; primal — the Mossmothers; influence — the
Bridgemoot, House Vantry, Pell; craft — Clan Gorrund, the Bridgemoot. The first institution of every branch has a rank ladder (V9 needs one).

### 13.8 The cast

**13.8.1 Who matters, by depth.** `[D]` Forty-four NPCs (`region_thallen.yaml#npcs`): 10 principal, 31
recurring, 3 walk-on (the three stilled in Harrowby's lane). Each carries 12.11.1's fields for its depth and
15.2.1's social record: role, people, pronouns, age band, distinctive detail, demeanor, voice (one of 12's eight
registers plus a habit), ranked wants with tags, a fear, refusals of 15's kinds, knowledge, sealed secrets each
with its gate, a **home** (03's and 11's request), memberships, a lifestyle (15's roles; overrides noted), the
tongues they speak, a threat band where they might fight or follow, and a recruit record where 16 could recruit
them. Before 12.11.1 generates anyone, the DM checks this roster (12's `[J:flag]`: does an existing NPC's role
and place match?).

**13.8.2 The principal NPCs.** `[D]` (wants ranked; secrets sealed — only their gates are listed here.)

| NPC | Role, home | Wants (1st) | Fear | Refusal | Secret's gate |
|---|---|---|---|---|---|
| Prior Hollis Brede | head of the Bellwardens; the bell-tower | the Last Bell never falls silent while he lives | the bell cracking in his lifetime | will not lie on the Ringer's oath | the bell's crack: Observe (Hard) in the loft, or Devoted; the confession: case n4 or the archive |
| Sister Ysmay Tollard | sacristan of the Last Bell; the bell-tower | to give the Stilled the peace she had | being woken again into noise | will not harm an innocent | she is the Cantor: case n3/n5 |
| Mother Hesper Pell | head of Pell & Daughters; the yard | the drowned road to Sael opened first | losing a second daughter | will not lend; will not betray her daughters | the causeway: Friendly, surveillance of her boats, or her fate; Jonquil's place: Wick at Friendly |
| Reeve Corbin Hask | the Margravine's reeve; the Weigh-house | a fat tithe and a quiet town | an honest audit | will not break the law where seen | his bribes: the ledgers vs Pell's books, or Lark; the treaty: case n1 |
| Ansel Quillon | keeper of the Lamplit Library | to read the Unsounding's bell-grammar whole | fire in the library | will not lend a book out | the copy he made for Ysmay: Warm and shown the sign |
| "Lady" Orsolin Vey | leader of the Wakeful; the Waking House | Orrowan land under Orrowan law | being a relic | will not speak of Hush-eve; will not kneel to the Margravine | she is the maid Lisbet Mereling: case.orsolin_signet |
| Dunstan Fell | Woken drover, the Choir's hands; Bellhollow | the Last Bell silent by Longday Fair | waking into a world that sent him to sleep | will not betray the Cantor | the theft: case n1 |
| Margravine Aldis Vantry | ruler of the March; Vantry Keep | every acre chartered before the term ends | the crown taking the March back | will not defy the crown | the charter's term: muniment room or a clerk at R4; the treaty: case n2 |
| Orsolin Vey (the true one) | stilled in Orsolin Manor's solar | (stilled) her people restored | — | will not kneel to a lowland lord | that she exists: case.orsolin_signet |
| Aude, last Bell-Prior of Sael | stilled at the Mother Bell | (stilled) that Orrow not be taken | — | will not be judged by lowlanders | why she rang the Unsounding: her journal at Caddow, or the Mother Bell |

**13.8.3 The recurring cast.** `[N]` In Tolling: Warden-Sergeant **Bram Ottery** (drill-master; terse; taps a
bell-stroke on whatever is near), **Mother Dace Wollin** (halfling keeper of the Cracked Clapper; calls everyone
"duck"; knows every rumor that crossed the bridge), **Alderman Mabry Cotter** (the Bridgemoot), **Justiciar Oda
Ferrant** (Merrow's priest; weighs both sides aloud), **Hearthkeeper Abel Marrow** (the Waking House; hands people
things to hold), **Gammer Thrush** (the fordwarden; talks to graves), **Hrolla Gorrund** (dwarf smith who dreams of
great bells), **Lark Mossbank** (the Cellar Kin's fence; never uses a name), **Captain Ghessa Ironjaw** (the Red
Lanterns), **Brother Jory Halloway** (a novice ringer), **Old Ned Rook** (a beekeeper of seventy, Tamsin Rook's
little brother). In Harrowby: **Cob Tenney** (the rider), **Goodwife Merrin Cask**, her daughter **Jessamy**, and
**Old Tobin Reave** (Woken, bitter, honest). Beyond: **Wick Pell** (Bellhollow), **Captain Roderic Stane** and
**Master Fennick Ashby** (Vantry Keep), **Founder-Mother Ama Gorrund** and **Bruni Bellmaw** (the Delve), **Old
Nackle Tinkettle**, **Ilsabet Grey** the Mossmother, **Lisanne of Hollin Hall**, **Ssessa Reed-in-Water** and
**Perrin Rushlight** (the Lantern-bound), **Ruvag Two-Axe**, **Red Gil Rush**, **Fenna Underby**, **Tansy
Thistledown**; and, sealed in the Hush, **Sergeant Hollin Peal** and **Jonquil Pell**.

**13.8.4 Who can be recruited (16's request).** `[D]` Named recruits with own bands and joining terms
(`npcs[].recruit`): Bram Ottery (companion, band 2, a thread against the Hush or the Choir at R3), Wick Pell
(companion, band 2, a venture to the Chapel of the Ringer at R3), Ansel Quillon (companion as `cmp.sage`, band 1, a
thread toward Orrowan texts), Fenna Underby (companion as `cmp.scout`, band 2, the hush-hound hunt), Captain
Ghessa Ironjaw (hireling as `cmp.veteran`, band 3: found only through her, never by Recruit, 16.3.2). Everyone
else follows 16.3.2 from the settlement's hire list.

**13.8.5 Bond placement (02.9.2).** `[D]` Where creation's bonds are bound (`bond_placement`; PR-13-3): anchor
**kin** in Tolling, Copsey or Harrowby (a Woken PC's kin is an old Orrowan relative in Tolling); anchor **friend**
in Tolling (default Mother Dace); anchor **mentor** in Tolling or the teacher's settlement (Acolyte: the keeper's
priest — Brede, Marrow, Ferrant or Thrush; Hedge-taught: Ilsabet Grey; Apprentice: Ansel Quillon; Artisan: Hrolla
Gorrund); anchor **ward** in Tolling (the Waking House if Woken); thorn **rival** among Pell's crews or the
Bellwardens' novices; thorn **creditor** in Tolling (Pell, the Cellar Kin or Reeve Hask); thorn **enemy** among
the Margravine's outriders, the Hemrats or the Choir (the PC knows a face, not a name); thorn **lost**: 02.9.2's
sealed Oracle question (Even: does this person still live?) is followed, on a yes, by a second sealed question
at Even — *are they Stilled somewhere in the Hush?* — whose gate is a clue (15.9.19).

### 13.9 Calendar, festivals and values

**13.9.1 The reckoning of the March (11's request; 00.17.1 Q19).** `[D]` (`data/calendar.yaml owner-block 13`;
names only — 11's engine and 00's 364-day year are unchanged.) Seasons: **Thawing**, **High Summer**,
**Tithing**, **the Long Dark**. Quarter days: **Ringing Day** (spring; the year's first day; the Last Bell's great
peal), **Longday Fair** (summer), **Tithe Day** (autumn; the Margravine's tithe falls due), **Hush-eve** (winter;
the anniversary of the Hush, when every bell is rung all night). Months: Rimewane, Furrowtide, Blossomfall ·
Haysel, Highsun, Reaping · Gleaning, Russet, Emberfall · Deepcold, Wolfmonth, Thawhope. Weekdays: Dawnday,
Hearthday, Weighday, Fordsday, Toilday, Marketday, Bellday. Era: years **since the Hush (S.H.)**. **The game opens
at the dawn watch of Ringing Day, year 42 S.H.** (a new moon, 11.10.3).

**13.9.2 Festivals.** `[D]` With 11's closed festival effects:

| Festival | When | Effects (`fx.*`) |
|---|---|---|
| Ringing Day | spring, week 1, day 1 | market, sitting, hiring fair |
| Longday Fair | summer, week 1, day 1 | market, sitting, truce |
| Tithe Day | autumn, week 1, day 1 | market, sitting, hiring fair |
| Hush-eve (the Long Peal) | winter, week 1, day 1 | market, sitting, rumor surge, rite day (divine warding) |
| Waking Day | spring, week 6, Bellday | rumor surge (the Wakeful's feast for the year's Woken) |
| Founders' Pour | summer, week 9, Marketday | market (Clan Gorrund pours its bells; outsiders welcome) |
| Fordwake | autumn, week 13, Fordsday | rite day (divine rites: lamps floated down the Wend for the dead and the Stilled) |

The annual chronicle festival 11.12 asks for is Hush-eve.

**13.9.3 Regional values (11.7.6).** `[D]` For region-scope reputation the March admires **courage**,
**protection** and **generosity** and despises the profane (`conduct.piety −`): it praises those who walk toward
the silence for someone else's sake and share what they bring back, and it damns grave-robbers of the tended dead,
bell-breakers, and anyone who leaves a neighbor standing in the Hush. Settlement scopes read their named faction's
values (T-13-9's "values from" column): so the same deed — turning a Woken family off a farm under the charter —
is *admired* in Vantry Keep (loyalty, justice under the crown) and *despised* in Harrowby (the Hearthkeepers'
mercy and generosity).

### 13.10 The bestiary of the March

**13.10.1 The regional subset (09's request).** `[D]` Sixty-two of 09's adversaries are used by the region's
tables and sites (`bestiary.subset`): the wolves (wolf, pack, dire, warg), great cat and bears, boar and aurochs,
vermin and swarms, constrictor, crocodile and the long thing in the mere (great squid), the manticore; brigands
(footpad, archer, highwayman, captain, band), soldiers (watch, man-at-arms, sergeant), the knight errant (a Woken
knight who thinks the war is on), cultists, hedge-witch and bog hag, dwarf holdguard, orcs (raider, warband,
warchief), goblins (skulk, mob, boss), lizardfolk (the reedfolk), ogre, troll, hill giant, frost jarl; the dead
(skeletons, barrow wight, wight lord, ghast, wailing ghost, wraith, dread wraith); dryad, Gloaming knight
(`adv.sidhe_knight`), river spirit, cairn guardian; ochre jelly, blighted treant; lindworm, wyvern and matriarch,
sea serpent, young dragon, water elemental. Names in 09's file are 09's; the region names them in narration
(the "Gloaming knight", "the Mere-mother").

**13.10.2 Regional adversaries (owner-block, PR-09-1).** `[D]` Thirty-three entries in
`data/adversaries.yaml owner-block 13`, each a roster line in 09's form built by **09's own `build()`**
(`09-gen_data09.py`, executed unchanged by the generator), so every number — defenses, tempo, Vitality solved
against the band's standard, severity compensation, Focus, nerve, morale break, reactions, lethal context,
disposition, captive fate, lore DC, loot contract, advisory by power band — is PR-09-1's, not ours. Their
nerve and objective (06's request) are therefore set by their archetypes, with the overrides noted.

| Group | Entries (archetype, band, variant) | What they are |
|---|---|---|
| The Hush's creatures | **hush-hound** (wolf 1), **hush-hound pack** (wolf 1, mob of 5), **grey bitch** (wolf 2, the downs' pack leader), **hollow** (zombie 1; disposition drag to lair, not lethal), **throng of hollows** (zombie 2, mob of 6), **quiet-wraith** (wraith 3), **voice-eater** (wraith 4), **Unsounding** (wraith 4 elite, with `pow.focus_leech`), **drowned ringer of Sael** (wraith 5), **a lone drowned ringer** (wraith 5 minion), **wight of the stilled host** (wight 4) | silent things the Quiet made or kept: hounds that make no sound, Stilled who woke empty and drag the living toward the pools, ringers the silence took whole |
| Orrow's works | **bronze bell-warden** (clockwork 3; rings true as it walks), **the Deep Warden** (golem 3 elite, huge), **bell-colossus of Sael** (golem 5) | the old kingdom's guardians of towers and ringsilver |
| People and named foes | **Vantry outrider** (soldier 2), **singer of the Hushed Choir** (cultist 2), **Sister Ysmay, the Cantor** (cultist 3 elite caster), **Dunstan Fell** (cultist 2), **Mother Sallow** (hag 3, can bargain), **the Barrow-King of Orrow** (wight 4 elite leader, holds Clapperfall), **Ashgorge** (great dragon 5 solo, can bargain), **a bell-mage of Sael** (folk mage 5: forty years awake alone in the Hush), **Ashgorge's fire-witch** (folk mage 5) | |
| Beasts and the far rings | **Rookwood tusker** (herd beast 2), **fen-light** (wild fey 2: lures and leaves), **thorn-walker** (monstrous plant 3), **the Mere-worm** (wyrm 5), **drowning-weed** (plant 5), **fire-root** (plant 5), **ash-drake** (drake 4), **cinder giant** (giant 5), **cinder giant outcast** (giant 5 minion), **cinder-lord** (fire elemental 5: a denizen of the Cinder Hall, not a wanderer) | |

**13.10.3 Why minions at the far edge.** `[D]` The audit (13.10.4) found what 09 predicted: against a reference PC
of band 4, *every* band-5 standard is lethal alone, so a ring-4 table's three home + 1 faces cannot hold one.
09's minion variant (Vitality ×½) of a band-5 archetype, alone, is **hard** at P4 — a straggler from the far
reaches, not its champion. The ring-4 tables therefore field a lone drowned ringer and a cinder-giant outcast at
home + 1 (DL-13-11). At home band 5 there is no band 6: the three home + 1 faces are filled by a band-5 solo
(the Mere-mother; Ashgorge abroad), each **hard** at P5, and the home rows mix band-5 minions alone and the weaker
band-5 archetypes (plants and bell-mages: **fair**) with standards (**hard**) so that two thirds of the threat
weight stays fair or easier.

**13.10.4 The encounter tables and their audit (10.10.1, PR-10-8).** `[D]` Fourteen regional tables, one per area,
each a d20 threat sub-table (6 / 11 / 3 faces at home − 1 / home / home + 1) and a d6 non-threat sub-table (the
deadly tables carry two sign rows and may otherwise be all threats). Every row cites adversary ids; counts are 1,
2, a mob, or a leader with a lower-band mob (T-09-10); four or more of one template are a mob; no row holds three
individuals; at home bands 4–5 no row holds two individuals of the home band. The generator fields each threat
row against 09's reference PC of the home band with **09's estimator** (`09_core.estimate`, PR-09-4) and
classifies the word with 06's thresholds, as if the PC holds the adversary's counter (09.4.4's convention — the
word *without* the counter is printed beside it, and such rows' counters are in the adversary's lore). Every table
passes:

| Table | Home band, danger | Bands (−1 / 0 / +1) | Words over 20 faces | Non-threat |
|---|---|---|---|---|
| the Brightfields | 1, settled | 6 / 11 / 3 | trivial 14, easy 6 | 6 |
| the Wend Meads | 1, settled | 6 / 11 / 3 | trivial 14, easy 6 | 6 |
| the Lowroad | 1, settled | 6 / 11 / 3 | trivial 14, easy 4, fair 2 | 6 |
| the Rookwood Eaves | 1, wild | 6 / 11 / 3 | trivial 14, easy 6 | 6 |
| the Standing Downs | 2, wild | 6 / 11 / 3 | trivial 8, easy 2, fair 5, hard 5 | 6 |
| the Eastholt | 2, wild | 6 / 11 / 3 | trivial 12, fair 5, hard 3 | 6 |
| the Reedwend | 2, wild | 6 / 11 / 3 | trivial 12, fair 5, hard 3 | 6 |
| the Hem | 3, perilous | 6 / 11 / 3 | trivial 9, easy 4, fair 4, hard 3 | 6 |
| the Gloaming | 3, wild | 6 / 11 / 3 | trivial 9, easy 4, fair 4, hard 3 | 6 |
| the Sallow Fen | 3, perilous | 6 / 11 / 3 | trivial 15, fair 2, hard 3 | 6 |
| the Quietlands | 4, perilous | 6 / 11 / 3 | trivial 6, fair 9, hard 5 | 6 |
| the Greyfells | 4, perilous | 6 / 11 / 3 | trivial 4, fair 13, hard 3 | 6 |
| the Mere of Sael | 5, deadly | 6 / 11 / 3 | trivial 6, easy 3, fair 5, hard 6 | 2 (signs) |
| the Cinderhorn | 5, deadly | 6 / 11 / 3 | trivial 6, easy 3, fair 5, hard 6 | 2 (signs) |

No row anywhere is lethal; the hard rows carry no complication (10.10.2 item 3). The full row-by-row audit (word,
estimated win and Staggered percentages, the no-counter word) is `region_thallen.yaml#encounter_table_audit`. The
Hush's rows carry their own signs (`HUSH_SIGNS`: paw-prints that end at a silent patch of grass; dogs whining at
nothing, all facing the same way; `HOLLOW_SIGNS`: trampled crops leading toward a pool with no tracks coming back);
every other row uses 10's `archetype_signs`.

### 13.11 Treasure, stock and trade

**13.11.1 The rare metal: ringsilver (08's request).** `[D]` The region's `material.metal.rare` is
**ringsilver**: a pale, faintly singing metal mined only in the Ringsilver Deeps; one part in nine in
bell-bronze makes a true bell. An ingot is band 3 (120 coin); Clan Gorrund sells one a season, if any. A true
handbell is a band-3 crafting project (08.6) for a smith holding `lic.training.craft_smithing` at expert who knows
the old alloy (Clan Gorrund teaches it at Friendly); a great bell is a great project (11.9.7). True handbells are
special stock in Tolling (Pell's yard: d2 a month, 60 coin) and at the Delve (d3 a year after Founders' Pour, to
friends of the clan).

**13.11.2 Storied items (08.4.8).** `[D]` Five authored rung-6 items (`storied_items`), each a fixed property set
inside the item share and the attunement limit; every property is checked against its tier count and its base
kinds:

| Item | Base | Signature · magnitude | Facts | Where |
|---|---|---|---|---|
| **Thallow's Handbell** (the Ringer's Own) | holy symbol | `prop.conduit_divine` · `prop.conduit_divine_thrift`, `prop.glowing` | a true bell whose peal opens hushed ground to `band.distant`; Thallow's sign | the Chapel of the Ringer's altar |
| **Clapperfall** | war hammer | `prop.bane_undead` (t2) · `prop.onhit_stagger` (t2) | forged from the Mother Bell's broken clapper; each hit rings true (hushed ground opens within `band.close` for the round) | the Barrow-King, the Kingsbarrows |
| **The Signet of Orrow** | signet | `prop.commanding` · `prop.fine_cut` | the seal of Orrow's royal cousins | on "Lady" Orsolin's thumb |
| **The First Warden's Lantern** | lantern | `prop.glowing` · `prop.wayfinder` | burns without oil while its bearer keeps the Warden's Vow; given at the Bellwardens' rank 3 or for saving the Last Bell | the bell-tower chapter-house |
| **A shard of the Mother Bell** | charm | `prop.resist_mind` (t2) | struck, opens hushed ground within `band.close` for a round; one of the pieces a recasting needs | Sael's nave |

No storied *set* is authored: a set needs a named composite in 05's `composites.yaml`, which has no owner-block
for 13 (DL-13-15; an interface request offers one for 05 at integration).

**13.11.3 Regional stock (08's request).** `[D]` Each settlement's `market.common` and `market.scarce` are 08.8.5's
trade-goods facts (T-13-9's columns); salvage bronze (`bi.trade_stock`) is common in Tolling and Bellhollow and
scarce at Vantry Keep, so carrying the Hem's haul south is how a salvager makes a notch. Special stock: handbells
(plain, 5 coin: an instrument, silent in the Hush), true handbells (60), bell-dust (20 a pinch), ringsilver
(120, the Delve). Lifestyles follow 08 and 15; the Woken of the Waking House live destitute (15's request:
lifestyles where they differ).

**13.11.4 The curio dealer at Pell's yard (08's request).** `[D]` The March has no city, so 08.8.4 would give it
no curio dealer. One regional exception (DL-13-14): Pell & Daughters' yard stocks **d2** property items a week
(generated as `scavenged` at band 2) at list + 2 notches, and buys property items at the completion of 08.8.5's
`clk.find_buyer` like a city's dealer — because the Hem's salvage passes through it. Pell's goal and fate data
make this stock a target the world can take away.

**13.11.5 Gifts and boons.** `[D]` Factions give by 08.7 with their `boon_base` and `boon_signature` (13.7.1).
Powers that may give an *ability* (08.7.3): the keepers (13.4) and the places of acceptance's spirits (13.5.6);
Mother Sallow and the Lantern-Man give only by bargain (08.7.2's *bargained*: wondrous, chosen fill, the
commitment written first).

### 13.12 Investigations

**13.12.1 The silent bells (`case.silent_bells`).** `[S]` + `[D]` The opening case (`cases[0]`). *Atmosphere: a
gentle hand that wants everyone asleep.* Solution (sealed): Dunstan Fell, a Woken drover of the Hushed Choir,
stole Harrowby's clapper on Ringing-eve and hid it in the bell-pit; Sister Ysmay, sacristan of the Last Bell, has
been filing its clapper-pin night by night (the missed stroke was the pin binding); both serve the Choir, which
means to silence the Last Bell; Ysmay is the Cantor; the Choir meets among the Standing Folk at each new moon.
Five necessary nodes, sixteen clue contents, seventeen placements, ten reserves, three fallbacks; the opposition
clock is the Choir's own goal clock (13.7.4).

| Node | Placements (holder · method · access) | Kinds / methods / core / places / reserves |
|---|---|---|
| n1 Harrowby's bell was silenced on purpose | the bell-frame · search · core; the clapper in the bell-pit · search · core (direct); Tobin · inquiry R2 · core (when no Cask is accusing him); Jessamy · inquiry R1 · core (away from her mother); the bell-pit stair · search · core | 2 / 2 / 5 / 4 / 2 |
| n2 the thief is Dunstan Fell | the stair (crook-print, moss); Wick Pell · inquiry R1 · core; Lark Mossbank · inquiry R3 · rolled; Dunstan · interrogation R5 · rolled (direct); Tobin; Jessamy | 2 / 3 / 4 / 5 / 2 |
| n3 the Hushed Choir means to silence the Last Bell | the clapper and its moss sign; Ilsabet Grey · inquiry R1 · core (once the sign is seen); Quillon · inquiry R2 · rolled; Copple Field at the new moon · surveillance · rolled; Dunstan | 3 / 4 / 2 / 5 / 2 |
| n4 the Last Bell's pin was filed | the pin in the loft · study · rolled Hard; Brother Jory · inquiry R1 · core; Hrolla Gorrund · inquiry R2 · core (once the symptom is known); Lark; Ysmay's cell | 2 / 3 / 2 / 3 / 2 |
| n5 Sister Ysmay is the Cantor | Bram Ottery · R1 · core; Prior Brede · R1 · core ("only the sacristan touches the pin"); Quillon; Copple Field; Ysmay's cell · search · rolled Hard; Dunstan | 3 / 5 / 2 / 4 / 2 |

Fallbacks (15.9.12): at `choir_goal` 4 the culprit makes a mistake (Ysmay seen buying a second file from the Cellar
Kin); if stalled, a witness seeks the PC out (a Woken asked to join "the quiet singers", or — if the Harrowby three
were woken — Hester Tenney remembering a voice humming in Orrowan as the quiet came); after three scenes without a
clue, the hush-hounds return to Harrowby and one wears a Choir thong.

**13.12.2 Whose ring is it? (`case.orsolin_signet`).** `[S]` + `[D]` *A servant wearing her mistress's name for
her mistress's people.* The Wakeful's "Lady Orsolin" is Lisbet Mereling, the true Orsolin's maid, who woke beside
her stilled mistress four springs ago and took the signet; the true Orsolin stands set and stilled in Orsolin
Manor's solar. Two necessary nodes (the claimant is not Orsolin: court-roll, Tobin, Abel Marrow, a Read of her,
the gatehouse roll, her confession; the true one is at the manor: the solar, Wick Pell, the gatehouse roll, the
confession) and one optional (she took the signet). Opposition: `clk.thallen.vantry_digs` (8, hidden, +1 a
fortnight) — the Margravine's clerks find the maid first and expose her in court, firing the Wakeful's linchpin
fate `exposed`. The case is a moral fork, not a puzzle: the impostor is the Woken's best advocate.

**13.12.3 The Treaty of the Ford (`case.treaty_of_the_ford`).** `[S]` + `[D]` *A promise a lord would rather
nobody remembered.* Written only under truth T4's default (13.1.5). A treaty sealed at the Treaty Stone a hundred
and sixty years ago binds Esterlow's lords to honor Orrowan holdings; the Margravine had Tolling's copy taken from
the Weigh-house two winters ago (it is in her iron chest); a sealed copy survives in Orsolin Manor's muniment
chest. Three necessary nodes, eleven placements, six reserves; opposition `clk.thallen.treaty_burned` (6, hidden)
which starts ticking only when the fact `vantry.alerted_treaty` is set (the PC asks Hask, a clerk or the
Margravine about the treaty, or the Wakeful petition with it). Producing the treaty in the Margravine's court is a
debate (15.8.3) whose outcome feeds Vantry's linchpin fate `turned` or `exposed`.

**13.12.4 Validity.** `[D]` The generator runs 15.9.4 on every necessary node of every case: at least three
placements, two holder kinds, two method kinds, one core, two places and two reserves — all pass (the table above;
`cases[].validity_check`). Every case has a core placement within a day of Tolling, and a fallback. Small
mysteries 13 seeds without full graphs (the lost bond's fate, Jonquil Pell, the bell under the Reedwend) are
15.9.19's and 11.5's.

### 13.13 Hiring and allies

**13.13.1 Who can be hired where (16's request).** `[D]` (`places[].settlement.hire`; 16.3.2's settlement maximum
band: camp and village 1, town 2.)

| Settlement | Roles (`cmp.*`) | Max band |
|---|---|---|
| Tolling | porter, guide (the only place besides Bellhollow with Hem-guides), camp hand, soldier, archer, scout, boatman, healer, locksmith, minstrel, sage, sapper, thief, militia; hound; donkey, pony, mule, riding horse | 2 |
| Copsey | porter, boatman, camp hand; hound; donkey, pony | 1 |
| Harrowby | porter, camp hand, militia, guide; hound; pony | 1 |
| Vantry Keep | soldier, archer, scout, camp hand; riding horse, draft horse, mule | 2 |
| Bellhollow | porter, guide, scout, sapper, thief | 1 |
| Gorrund's Delve | sapper, porter; mule | 1 |
| Tinkettle | guide, scout, sapper, locksmith (goblin tinkers) | 1 |
| Reedmere | guide, boatman | 1 |
| Ruvag's Fold | soldier, guide (orc sell-swords, against a rival clan only) | 1 |
| Hollin Hall | none (a Lingerer may join a cause by a joining term) | — |

**13.13.2 Hire quirks.** `[D]` `tbl.thallen.hire_quirk` (d12) replaces 16's: *Woken, forty years out of date and
wants to see everything · has walked the Hem and come back, and will not say what they saw · carries a handbell and
rings it at every crossroads · afraid of quiet: talks to fill every silence · wants a claim of their own past the
Brightfields · a Vantry deserter: someone will come asking · knows the country (one route known: a way-finding
lever) · devout to Weyla: will not leave the dead unburied · owes Pell & Daughters money · a Tinkettle goblin, sharp
with tools and sharper with prices · kin stilled in the Hem: will go anywhere that might wake them · a drinker,
steady until there is drink.*

### 13.14 Regional tables

**13.14.1 What replaces what.** `[D]` (`region_thallen.yaml#tables`, `rumor_tables`, `names`.) The engine uses a
regional table in place of the generic one named in its `replaces` field whenever play is in the March:

| Regional table | Die | Replaces | Content |
|---|---|---|---|
| `tbl.thallen.events` | d12 | `tbl.11.local_events` (10's V face) | news, a faction passing, a trace, a rumor, an omen; the Last Bell carrying too far; a hook; the weather; a Woken out of the north; **a hush-pool moved in the night** (a written week-long hazard); salvagers who will share; a walking lantern-light |
| `tbl.11.season_events.thallen.<season>` | d12 ×4 | 11's seasonal tables | spring: **the Hem's ebb** (rows 1–4: a ring-3 pool lifts, d6 Stilled get the Waking roll, Woken arrive), late frost, pilgrims, a farm feud, the Wend in spate; summer: bandit summer, drought, hush-hounds on the flocks, a salvage rush, Longday trouble, a comet; autumn: good harvest, cattle sickness, the Margravine's levy, the Waking House overfull, the Choir's rite, Ruvag coming down; winter: hard winter, sickness, a child walking north toward the quiet, a pool on the Lowroad, **Hush-eve** (if every Bellwarden bell rang, the Quiet's clock skips its next Year Turn tick) |
| `tbl.11.hook.thallen` | d20 | `tbl.11.hook` | twenty regional seeds, each a situation template or a quest/question kind |
| `tbl.thallen.rumors` | d20 | 11's rumor table for the region | twenty rumors, truth **sealed at authoring** (true / partial / false), each with `points_to` |
| `tbl.thallen.chase_ground` | d6 | `tbl.chase_ground` | Tolling, open country, fen |
| `tbl.thallen.sites` | d12 by ring | `sites.yaml#site_generation` | theme × domain lists per ring |
| `tbl.thallen.npc_role` | d20 | `tbl.npc_role` | Brightfields farmer, newly Woken, Hemrunner, bargee, Bellwarden novice, Pell crew-hand, Vantry outrider or tithe-man, drover … |
| `tbl.thallen.npc_detail` | d20 | `tbl.npc_detail` (rolled first; 12's on a repeat) | moss-stained clothes, a handbell on the belt, wool in the ears "against the quiet", a pierced Orrowan coin … |
| `tbl.thallen.npc_refusal_extra` | d6 | rows 11–12 of `tbl.npc_refusal` | will not go past the Hem-cairns; will not stay where they cannot hear a bell; will not deal with the Woken; will not cross the Margravine; will not sell what was taken from a grave; will not let strangers touch a bell |
| `tbl.thallen.omens` | d12 | the twist templates' generic omens (12) | a bell misses a stroke; birds fall silent mid-song; a ring of quiet round a standing stone; a Stilled in a far field has turned its head … |
| `tbl.thallen.furnishings` | d12 | — (12's furnishing request) | a cracked Orrowan bell as a planter; a Hem-cairn stone in the hearth; a handbell by the door "in case" … |
| names (nine tables) | d20 + d20 | `tbl.name_given`, `tbl.name_family` | 13.5.5 |

12's gender table is kept (DL-13-12).

### 13.15 The opening and the first-session teaching arc

**13.15.1 Session zero in the March.** `[D]` 14's session zero runs first (tone, the lethality promise, lines and
veils, flags, pacing profile, auto-commit; 12.5.1). The March adds three things, in this order: (1) the pitch of
13.1.2, read close to verbatim; (2) the optional Truths of 13.1.5 ("Want to shape the world a little? Four
questions; skip any and I'll use the usual answer"); (3) the character, by 02's paths — a pregen (13.16), the fast
path, or the full path — bound to the region by PR-13-3. The region's opening has no content that touches a
common veil beyond peril and the uncanny; the Stilled are described as still, mossed and breathing-less, never as
corpses, and a recorded veil on "the dead" makes the DM narrate them only as statues (12.5.6).

**13.15.2 The inciting incident.** `[N]` + `[D]` The first scene opens **in medias res** (12.4.3's strong start)
at the dawn watch of Ringing Day on the Wend Bridge. The moment: market carts queued at the toll-house, frost on
the parapets, the whole town waiting for the Last Bell's great peal. The impetus: *the Last Bell rings the hour,
and misses the third stroke.* For a breath all of Tolling stands as still as the Stilled. Then hooves on the
bridge: Cob Tenney on a lathered farm pony, shouting that Harrowby's bell has gone quiet in the night, and the
quiet came with it, and his mother is standing in the lane and will not move. Present (written on mention):
Cob, Mother Dace at the inn door, Alderman Cotter at the toll-house, Bellwarden novices on the tower stair,
Vantry tithe-men, pilgrims, carters, a Pell & Daughters wagon. The open prompt: *What do you do?*

The incident is half of every pregen's start (02.9.1: the drive is the other half): Tamsin's watch was Orrow's;
Pip's road runs north past Harrowby; Corin was on the bridge when his bell missed; Orla's want is the bell that
cannot be silenced; Ithren's question is why the Hush moves; Bee's ballad ends at the Mother Bell. A player-built
character's drive is bound to the region by PR-13-3 step 6.

**13.15.3 The situation the PC walks into.** `[D]` Two situations are already running (`situations`):
- **The quiet in Harrowby** (`sit.thallen.harrowby_quiet`). Harrowby's bell fell silent before midnight when its
  clapper was stolen; a hush-pool crept over the north lane and the green's edge; Nell Cask, Hester Tenney and the
  miller's boy Wat Copley stand stilled in it. **`clk.thallen.harrowby_stillness`** ("Before the stillness sets in
  Harrowby": countdown, 6, **public**, 1 filled, +1 a watch) completes at the next dawn; at completion the three
  are *set* (13.2.4) and a hook seeds the village's quarrel over giving them to the ford. The clock is public
  because the lore is common: Gammer Thrush and Abel Marrow both say "a day, and then they set". Default timeline:
  the next dawn the three set; day 2 Merrin Cask accuses Tobin before the village and he is beaten unless someone
  stands between them; day 3 the hush-hounds take a dog at the pool's edge; week 1 half the lowland families go to
  Tolling and Vantry's outriders arrive "to keep order"; week 2 the Wakeful petition to seat a steward in
  Harrowby's empty hall.
- **Cask and Reave** (`sit.thallen.harrowby_feud`, template `sit_t.feud`): Merrin Cask's family has farmed Cask Farm
  thirty years; Tobin Reave, Woken last spring, farmed it before the Hush; Merrin believes Tobin stole the bell to
  drive her off. Default timeline: day 2 the accusation; week 2 the Wakeful take up Tobin's claim; week 4 the
  reeve rules for the Casks under the charter and Tobin is turned out.

How the three can be woken in time (13.2.4 (a)): rehang Harrowby's own bell — it is a true bell, Orrowan-cast —
with its clapper, which is in the bell-pit under the green (a small site, band 1; the case's direct clue); borrow a
true handbell from the Bellwardens (the Prior lends one at Warm, or as an R2 request with the term "for
Harrowby's sake", which serves his first want); buy one at Pell's yard (60 coin — Mother Pell will sell on credit,
a deal with a commitment); or have Hrolla forge a plain clapper for the old bell (a day's work: only with a forced
march both ways). Ringing a true bell over the green for one full watch also ends the pool.

**13.15.4 PR-13-1 The opening.** (the procedure in 00.2.5's form)

```
### 13.15.4  The opening of the Thallen March                      [D] [J:enum]
Trigger [T]:        mark_boundary(session_start) for the campaign's first session, after PR-02-6
                    (a new character) or PR-02-3 (a pregen) hands over (02.1's step C9)
Loads in:           situation.social, situation.exploration.settlement
License check:      none (it frames; the player's beats are checked as usual)
Decisions (J):      1. OPENING FRAME [J:enum]: STANDARD (true only when the PC is in Tolling at
                       Ringing Day's dawn: every pregen, and any PC PR-13-3 places in Tolling) |
                       ON THE ROAD (true only when PR-13-3 placed the PC elsewhere within a day:
                       the scene opens on the north road as Cob's pony overtakes them, the missed
                       stroke heard faint from the south) | default: STANDARD
Computation [D]:    1. Write the start state (13.17.1): date, weather (data for the first day),
                       moon, the festival, every clock and situation, the Harrowby pool hazard.
                    2. Write on mention the scene's present NPCs from the roster (12.11.1's
                       roster check first: every named one already exists).
                    3. Frame the scene (12.4.3) from INCITING: moment, impetus (the missed stroke,
                       then Cob), in medias res, the open prompt; at most 200 words.
                    4. While the teaching arc runs (13.15.5), each mechanic's FIRST use in this
                       campaign appends its one-line out-of-fiction note (TEACHING_ARC[].oof_line),
                       never again unless the player asks (14 renders [HOW THIS WORKS]).
                    5. The always-available leads (13.15.6) are loaded as live leads for 12.8.
Stakes:             none of its own
State writes:       time; weather.today; moon.phase; clocks (13.17.1); situations; the pool
                    hazard on loc.harrowby.green; npc entities on mention; teaching_arc.used flags
Narration may not imply: that the PC must go to Harrowby; anything about the Choir; that the
                    Last Bell is cracked (sec.brede.crack is sealed)
Worst case (J):     ON THE ROAD chosen for a PC in Tolling: the PC starts a few hours north of
                    where they were placed; the next scene's framing corrects it (class iv).
Examples:           inside STANDARD: Corin Ashby, Bellwarden novice, starts on the tower stair
                      with the rope still in his hands.
                    boundary ON THE ROAD: a player-built drover PR-13-3 placed at Harrowby's
                      edge: Cob gallops past them toward Tolling, shouting.
                    non-example: opening "a week later in Harrowby, after the bells were fixed"
                      skips the decision the incident exists to pose.
Anchor:             no
Basis:              [R5 P-37, P-40, §4 onboarding] [12.4.3] [12.5.2] [02.9.1] [DL-13-04]
```

**13.15.5 The teaching arc.** `[N]` + `[D]` The first session teaches the core loop by *opportunity*, not by
gate: each beat below is something the opening's situation makes natural, in any order, and the player may skip
all of them and ride south instead (the world then runs its default timelines). Each carries one out-of-fiction
line, shown the first time that mechanic fires and never again (`opening.teaching_arc`).

| Beat | Where it naturally happens | What it teaches | The one-line note (first use only) |
|---|---|---|---|
| T1 talk | the bridge, the inn | say what you do in plain words; the OFFER before any roll (01.7) | "[HOW THIS WORKS] Just say what your character does or says. When the outcome is uncertain I'll show you the odds and what's at stake before anything is rolled, and you can change your mind." |
| T2 a journey choice | leaving Tolling | the journey OFFER: routes in watches, danger in words, the watch die (10.3.4) | "[JOURNEY] Two ways to Harrowby: the road (about a day, can't get lost) or across the fields (half that, but you have to find the way). Farm country: trouble is rare and small." |
| T3 explore and find a clue | the bell-frame, the stair | searching; clues are what you find, not conclusions (15.9.3) | "[CLUE] Clues go in your journal as what you found. Putting them together is up to you; when you think you know something, say so and I'll tell you whether what you hold supports it." |
| T4 a social knot | Merrin accusing Tobin on the green | refusals and terms: a wall no roll passes, which the situation can lift (15.2.3) | "[REFUSAL] Tobin won't talk while someone's calling him a thief. That's a wall no roll gets through, but you can change the situation." |
| T5 the first fight, with exits | the pool's edge at dusk | omens before a threat, the threat word, conflict turns, retreat and morale | "[WARNING] Two hounds, silent. My read: <the advisory word for this PC>. You can fight, run for the alehouse, or try something else entirely." |
| T6 a deed that counts | any pressured, resolved beat | nothing out loud: evidence is hidden (03) | — |
| T7 ringing true | Harrowby green | the setting's one idea; a public clock beaten in time | "[CLOCK] Before the stillness sets: 4 of 6. When it fills, the three in the lane are set for good, or near enough." |

**T5 in numbers.** The first fight is two hush-hounds (band 1, skittish, `drive_off`, no lethal context) arriving
as 10.9.5's pending threat at dusk if the PC is still in Harrowby — dogs whining at nothing first, then paw-prints
ending at the silence. Against 09's band-1 reference PC the estimator calls it **trivial** (win 100%, Staggered
0%); the real word is computed from the PC's own line (09's PR-04 request: starting characters vary — a new caster
in melee is the case it protects). Its exits are data (`teaching_arc[T5].encounter.exits`): the alehouse door
(shelter at `band.near`), fire (the hounds' nerve is skittish), a true bell rung (a Protective lever, and their
morale clock +1), or the sheep-pen. If the PC stays a second night, the grey bitch comes with them (the generator's
options: the grey bitch alone is **easy**, the grey bitch with two hounds **fair** at P1) — so the second fight is
a real one, and the omens of the first night have said so.

**13.15.6 Leads that are always there (P16).** `[D]` Loaded as live leads for 12.8 (`opening.leads`): in Tolling,
Mother Dace ("Tobin saw something that night, but he'll not speak to Merrin's lot; and Gammer Thrush says they set
by the next dawn"); at the bell-tower, Prior Brede at Neutral or better asks the PC privately to find out who has
been in his tower (an offer: a thread with an earned reward, 08.7.2); on the road, Cob, who talks; in Harrowby,
Jessamy humming an Orrowan lullaby alone by the duck-pond, and the bell-frame and its stair (core clues: no roll
to find); anywhere, stalled, the case's fallbacks and 12.8.2's lead injection.

### 13.16 The ready-made characters

**13.16.1 Six pregens (02.2.5; PR-02-9).** `[D]` (`region_thallen.yaml#pregens`.) Each is a complete creation
record; the generator re-derives every number from the origins (licenses, competence, tongues, Vitality,
Focus, coin, kit, faction ties, hooks) and runs PR-02-9's thirteen tests on it: all pass. Birth (C6) is drawn live
when the player picks one; the name may be changed; the creation window applies. Between them: a fighter, a
sneak, a talker, two workers of magic (divine and primal) and a crafter; three non-humans.

| Pregen | People · upbringing · livelihood | One sentence | Good at | Wants (the long vow) | Numbers |
|---|---|---|---|---|---|
| **Tamsin Rook** (she) | human · Woken of Orrow · Soldier | a soldier of Orrow's border watch, stilled at her post forty-one years ago and woken last spring | sword and shield; standing her ground; Orrowan | find out what became of the twelve of her watch on the Caddow road | Might +3 End +2 Agi +1; V14 F4; blade +2, shield +2; polearm; letters; Orrowan |
| **Pip Thistledown** (he) | halfling · Village · Salvager | a Copsey miller's son who runs salvage out of the Hem and owes Pell for every rope | moving unseen; finding the way in the Hem; climbing in | one great find, and buy his mother's mill back | Agi +3 Wits +2 End +2; V14 F4; stealth +2; survival, navigation; animals, cookery; Orrowan |
| **Corin Ashby** (he) | human · Cloister · Acolyte of Saint Thallow | a Bellwarden novice who rang the night hours, on the bridge when the bell missed | Thallow's warding (*Sanctuary*); faith and offices of the bells | learn why the Last Bell missed, and make sure it never misses again | Pre +3 Res +2 Wits +1; V12 F5; divine warding +2; religion; letters |
| **Orla Gorrund** (she) | dwarf · Townhouse · Artisan | a Gorrund smith raised in Tolling's forge-house | smithing and founding; a fair bargain; knowing old Orrowan work | cast a great bell in the old alloy, one the Quiet itself will hear | Might +3 Int +2 End +2; V14 F3; smithing +2, trade +2; letters; Orrowan, history (learning picks) |
| **Ithren of the Rookwood** (he) | elf · Wilds · Hedge-taught, accepted at the Greenwell | a young elf sent out by the Mossmother to learn why the Hush stopped at the trees | growth magic (*Root Snare*); living off the land; starsight | find out why the Hush stopped at the Gloaming's edge, and whether it will stop there again | Res +3 Wits +2 Agi +2; V11 F4; primal growth +2; survival, foraging |
| **Sabine "Bee" Marlow** (she) | human · Road · Performer | a road-singer whose satire of the Margravine every tavern knows | singing a room into her hand; talking her way in and out; every road's gossip | find the end of the Ballad of the Mother Bell | Pre +3 Agi +2 Wits +1; V12 F4; performance +2, persuasion +2; history, navigation; Orrowan |

Bonds, each bound to a region NPC (PR-02-9 test 13): Tamsin — kin Old Ned Rook (her brother, seventy, by the
Ford-garden), lost Sergeant Hollin Peal (sealed: stilled at the Caddow road gate); Pip — kin Tansy Thistledown
(Copsey), creditor Mother Pell (12 coin due at Longday Fair); Corin — mentor Prior Brede, rival Brother Jory
Halloway; Orla — mentor Hrolla Gorrund, rival Bruni Bellmaw; Ithren — mentor Ilsabet Grey, enemy Reeve Hask;
Bee — friend Mother Dace, rival Master Fennick Ashby. Faction ties: Tamsin the Wakeful +1; Pip Pell +1; Corin the
Bellwardens +1 (the keeper's faith at Warm, 02.5.5); Orla Clan Gorrund +1; Ithren the Mossmothers +1; Bee the
Bridgemoot +2 and House Vantry −2 (sworn and hunted). Each has five or six hooks (one per origin, the drive, each
bond, an enemy tie), all pointing at region entities.

**13.16.2 How to offer them.** `[N]` PR-02-3 step 1 shows each as name, the one sentence, what they are good at
and what they want (the first, third, fourth and fifth columns above) — four lines each, nothing more. A newcomer
who cannot choose is offered Tamsin (the most forgiving in a fight) or Corin (the closest to the opening's heart).

### 13.17 The sandbox's starting state

**13.17.1 What is running at the first scene.** `[D]` (`opening.starting_state`.)

| Clock | Visibility | Start | What fills it | When it fills |
|---|---|---|---|---|
| `clk.thallen.harrowby_stillness` | public | 1/6 | +1 a watch | the Harrowby three are set |
| `clk.thallen.choir_goal` (the Last Bell falls silent) | hidden | 1/8 | the Choir's World Turn goal actions; linchpin fates | 13.7.4 |
| `clk.thallen.vantry_goal` | hidden | 3/12 | Vantry's goal actions | the Standing Downs chartered; the Wakeful lose hold |
| `clk.thallen.bellwardens_goal` | hidden | 2/8 | the Bellwardens' goal actions | the Hem-tower at Bellhollow rings: a ring-2 pool lifts |
| `clk.thallen.pell_goal` | hidden | 4/12 | Pell's goal actions | the drowned road open: a situation (salvage rush to Sael) |
| fifteen petty goals | hidden | 0–3/6 | one d6 a week | 11.3.16's writes and a hook |
| `clk.thallen.quiet_wakes` (the Quiet stirs) | hidden | 5/12 | +1 a Year Turn (skipped after a Hush-eve on which every Bellwarden bell rang); +3 if the Last Bell falls silent; +1 if a true bell is destroyed; +2 if the Mother Bell is rung cracked; −1 a season in which a great bell was hung or recast | the Hem becomes hushed; the downs perilous; `clk.thallen.quiet_rises` begins (12, +2 a Season Turn: the Hush reaches the Brightfields and threatens Tolling) |
| `clk.thallen.vantry_digs` | hidden | 0/8 | +1 a fortnight | the false Orsolin exposed in court |
| `clk.thallen.treaty_burned` | hidden | 0/6, dormant | +1 a week once `vantry.alerted_treaty` | the Vey copy of the treaty burned |

**13.17.2 If the PC does nothing for a month (and after).** `[D]` The World Turn re-run (13-world-sim.py: 11's
`run()` verbatim with these factions, 300 seeds) projects, with the default timelines of 13.15.3:
- **Day 1–2.** The Harrowby three set at the next dawn; Merrin accuses Tobin; the village splits.
- **Week 1.** Half of Harrowby's lowland families come to Tolling; Vantry's outriders arrive in Harrowby; the
  hush-hounds take a dog. The faction clocks move a tick or two each.
- **Week 4.** Median goal fills: Vantry 5/12, the Bellwardens 5/8, Pell 6/12, the Choir 4/8 (p10 2, p90 5); no full
  faction has completed its goal in the first month (0–2%). The reeve rules for the Casks; Tobin is turned out; the
  Wakeful have taken up his claim.
- **Week 8–16.** The Choir silences the Last Bell at a median of **week 11** (p10 8, p90 16; 75–81% by week 13,
  every run by week 26): Tolling's north ward goes quiet, the Quiet's clock jumps three, and the Brightfields turn
  wild. The Bellwardens' Hem-tower is usually raised in the same season (they complete about three goals a year).
- **The long run.** Each full faction completes 2.0–3.0 goals a year (mean 2.57–2.71 across scenarios; target
  1.5–3.5), no faction collapses in two years, and the Quiet, untouched, wakes in seven years (seven Year Turns), in
  four if the Last Bell falls silent. The campaign's horizon is therefore real but
  distant: something the player can push back (recast bells, the Mother Bell) or ignore for years.

**13.17.3 The long horizon: the Quiet.** `[S]` + `[D]` `clk.thallen.quiet_wakes` and `clk.thallen.quiet_rises` are a
realm-scale situation in 00.8's sizes (12 + 12, linked). They are hidden and carry omens (the Hem's ebb is smaller
this year; a hush-pool forms where none was; the Hem advances in summer for the first time in forty years; the
Standing Folk all turn their heads north one night). They can be pushed back only by true sound at scale: a great
bell hung or recast (a great project, 11.9.7) takes a segment off at the next Season Turn; the Mother Bell recast
whole voids both clocks and wakes every Stilled in the March (13.2.4 (c)) — the one campaign-ending *world change*
the setting holds, and it ends nothing but the Hush: the world runs on, and the player retires when they choose
(11.13).

## Procedures

**PR-13-1 The opening.** `[D]` 13.15.4 (in 00.2.5's form).

**PR-13-2 Using the region's data in play.** `[D]` Whenever a rule asks for region content:
1. **A place**: read `places[]`; a place not there is generated by 10.1.8 with the region's ring data
   (`terrain_by_ring`, the ring's band and danger) and `tbl.thallen.sites`, written before it is narrated.
2. **A person**: 12.11.1's roster check against `npcs[]` first; otherwise generate with the regional tables
   (`tbl.thallen.npc_role`, `.npc_detail`, the people's name table, `.npc_refusal_extra` on rows 11–12 of 12's
   refusal table) and 12's tables for every field the region does not replace.
3. **A random event, hook, rumor, season event or chase ground**: the regional table named in 13.14.1.
4. **An encounter**: the place's `encounter_table`; a building or landmark uses its area's.
5. **What is true of the world**: `canon.facts` and `canon_impossible` before the Oracle (00.12.7); the spirit
   odds of 13.3.5; the Waking rule for the Stilled.
6. **A faction**: `factions.13.yaml` (the record), the org-tie map and institutions (`region.factions`).

**PR-13-3 Binding a new character to the March.** `[D]` + `[J:enum]` Run at C9 after PR-02-6 writes the character
(pregens arrive already bound):
1. **Place**: the PC starts in Tolling unless their upbringing or livelihood names a ring-1 settlement as home
   (village-raised: the player picks Copsey or Harrowby; a Woken: Tolling's Waking House). `[J:enum]` STANDARD vs
   ON THE ROAD for PR-13-1 follows.
2. **Bonds**: each bond NPC is created at its place by `bond_placement` (13.8.5); an anchor is within a day of
   Tolling. Where an existing NPC fits the bond's words (the roster check), that NPC *is* the bond (Mother Dace for
   a Tolling friend; Brede for a Thallow mentor).
3. **Faction ties**: each tie's `org` kind resolves by `org_tie_map` (first row; its people / Woken / keeper
   exceptions); 11 writes the status (PR-11-4). A kind with `none` is held open (02.9.8).
4. **A lost bond**: 02.9.2's sealed Oracle (Even: alive?) and, on a yes, a second sealed Oracle at Even (Stilled in
   the Hush?); the answer's gate is a clue placement 15.9.19 builds.
5. **Magic**: an Acolyte's keeper is one of the six (13.4.1) whose schools include the chosen school; a
   Hedge-taught's place is one of the places of acceptance whose schools include it (its ask becomes a
   commitment); an Apprentice's master is Ansel Quillon (or Fennick Ashby at Vantry Keep) and their text is one of
   Tolling's.
6. **The drive**: a *want* becomes a thread (11) with its first clue placed in the region; the DM binds the
   want's object to the nearest fitting entity in data (`[J:enum]` over the roster, the sites and the factions;
   default when none fits: a hook of `tbl.11.hook.thallen` rolled and bound to it). *Worst case:* a less apt
   binding; the thread's text is the player's own and the binding is shown, so the player can redirect it
   (class iv).
7. **Hooks**: each origin hook's text is bound to region entities by the same `[J:enum]` (the Woken's
   "the house you were stilled in" → a Brightfields or Downs farm the generator places; the Salvager's debt →
   Pell & Daughters).

**PR-13-4 Regenerating and auditing the region.** `[D]` `python rules/_process/simulation/13-gen_region.py`
re-derives every file from `13_data_*.py`, runs every audit (PR-10-8, 11.3.1, PR-02-9, 15.9.4, 10.1.2, the rings,
05.7.10, the checklist), and writes nothing if any error remains. `--tables-only` prints the encounter audit row by
row. `python 13-world-sim.py [seeds] [--rule-cap]` re-runs 11's World Turn with the region's factions. Since
integration `11-world-sim.py` follows 11.3.4 and carries the `steadfast` row itself, so `--rule-cap` changes
nothing: the verbatim re-run gives 2.66–2.71 goals per full faction per year and 0% at tier 5
(`13-world-sim-output.txt`) [integration: I-026].

## Tables

Tables embedded in the Rules are canonical and indexed here; the data files are canonical for every id and number
(00.1.4 item 5): `data/region_thallen.yaml` and `data/contrib/{origins,kits,licenses,factions,adversaries,hazards,
calendar}.13.yaml`, all generated by `13-gen_region.py` (report: `13-gen_region-output.txt`).

- **T-13-1** `canon_impossible` (13.2.1).
- **T-13-2** Truths of the March (13.1.5).
- **T-13-3** Keepers (13.4.1).
- **T-13-4** Peoples present (13.5.1); tongues (13.5.3); places of acceptance (13.5.6).
- **T-13-5** Rings and places (13.6.1).
- **T-13-6** Sites (13.6.5).
- **T-13-7** Consecrated and tended places (13.4.3); readable place facts: `consecrated`, `tended_by`,
  `desecrated`, `dead_ground`, `haunted`, `hushed`, `true_bell`.
- **T-13-8** Factions (13.7.1); linchpin fates (13.7.3); org-tie map (13.7.5).
- **T-13-9** Settlements (13.6.6); hire lists (13.13.1).
- **T-13-10** Calendar names and festivals (13.9).
- **T-13-11** Regional adversaries (13.10.2); encounter-table audit (13.10.4).
- **T-13-12** Storied items (13.11.2).
- **T-13-13** Case validity (13.12).
- **T-13-14** Regional tables (13.14.1).
- **T-13-15** Teaching arc (13.15.5); pregens (13.16.1); starting clocks (13.17.1).
- **T-13-16 The region file's keys.** `[D]` SCHEMAS' required keys for `region_*.yaml` (`places`, `npcs`,
  `factions`, `clocks`, `encounter_tables`, `rumor_tables`, `names`, `canon_impossible`) are present; the optional
  keys this chapter adds (for SCHEMAS' integration): `region`, `canon`, `keepers`, `tongues`, `peoples`,
  `absent_origins`, `places_of_acceptance`, `fight_locations`, `objects`, `bond_placement`, `values`, `situations`,
  `encounter_table_audit`, `tables`, `terrain_by_ring`, `cases`, `bestiary`, `storied_items`, `storied_sets`,
  `stock`, `pregens`, `opening`, `interface_checklist`.

## Worked examples

### WE-13-1 The first hour, with Corin Ashby (the teaching arc in play)

*Setup.* The player picks Corin (PR-02-3); the birth draw gives a knack on `deed.divine.warding` and the quirk
*hums when nervous*. PR-13-1: STANDARD. Ringing Day, dawn; frost; new moon. Corin is on the tower stair with the
rope-burn still warm.
1. **The impetus.** The Last Bell rings the hour and misses the third stroke; Cob gallops onto the bridge. The
   player: *"I run down to the boy and get him off the pony before he falls."* No roll (no uncertainty, 15.3.10);
   Cob's knowledge is shared at R1 (he is Warm, +1, toward a Bellwarden who helped him: 12.11.2's reaction roll
   gave +1). T1's note shows once.
2. **The Prior.** *"I go up to the loft and ask the Prior what happened."* Brede is Corin's mentor (+1 Warm);
   "what happened" is R1 (certain at Warm). He tells what he knows (the stroke missed) and, at Warm, makes the
   offer of 13.15.6: find who has been in his tower. He does not mention the crack (sealed). The player accepts:
   a thread (`case.silent_bells`, kind situation) with an earned reward (08.7.2).
3. **The road.** *"Harrowby, the quick way."* The journey OFFER: across the Brightfields, 1 watch, trackless,
   way-finding Easy, settled. Way-finding: Wits +1, floor +1, vs Easy 10 → needs 8 (65%). d20 = 12 → success; the
   watch die (settled, day) shows nothing. T2's note shows once.
4. **The green.** Three people standing in the lane, moss already greying their hands; Merrin Cask shouting at
   Tobin. The clock is public: *Before the stillness sets: 2 of 6.* *"I look at the bell."* The bell-frame
   placement is core: reached is found (15.9.5): c1, the clapper lifted off its pin by someone who knew bells.
   T3's note. *"I ask the old man what he saw."* Tobin's refusal (not while a Cask calls him a thief) holds: G4
   with the redirect. T4's note. *"I ask Goodwife Cask to come with me to see her sister, and leave Tobin be."*
   Persuade, R2 for a frightened woman: Presence +3, floor +1 = +4 vs her Resolve defense 10 + 0 + 0 + standing 0
   + R2 2 = 12 → needs 8 (65%). d20 = 15 → success. With Merrin gone, Tobin talks (R2, core): c3, the tall Woken
   drover from Caddow with a bell-tongue on his crook. *The stair*, then: c2. The bell-pit, a small band-1 site:
   Explore onward twice, a rat swarm met and driven off (easy), and the clapper itself, with the moss sign (c5,
   direct). Clock: 4 of 6.
5. **Ringing true.** *"We hang the clapper and I ring it."* Rehanging is Handle with help (Cob), no danger: certain.
   The Waking rule (13.2.4): FRESH, OVER THEM (the lane is within band.near of the green) → the three wake. A full
   watch of ringing also ends the pool. T7. Corin's deed — carrying the bell's weight back from the pit and ringing
   the lane awake before the stillness set, under a public clock — is a resolved, pressured success: evidence
   under 03, unseen by the player (T6).
6. **What the world does next.** The thread is active; the case's n1 is reached (deducible from c1 + c2), n2 is
   suggested (c3); Brede's want "a quiet town" is served (a memory, 12.11.7). Nothing told Corin about the Choir:
   the moss sign's meaning waits for Ilsabet Grey or the Library.

### WE-13-2 The Waking rule's boundaries

- **Inside (fresh, over them):** WE-13-1 step 5 → woken (Certain).
- **Boundary (set, a watch of true sound):** six weeks later Pip carries a true handbell (bought on Pell's credit)
  to the Chapel of the Ringer and rings it over Jonquil Pell for a full watch, while the hush-pool in the porch
  opens. Set → Oracle at **Remote** (91+): d100 = 37 → no. The fact `last_waking_try.jonquil = summer, year 42`
  is written; the next try is at the next season. The narration: *she does not move; somewhere under the moss
  her eyes are open.*
- **Boundary (over them is false):** Pip rings from the chapel tower while Jonquil stands in the porch below, in
  another area of the site → not over them; no question is asked (the DM says so plainly).
- **Tempting non-example:** *"I cast Mend Flesh on her."* `ci.waking_the_stilled`: G4 for everyone, with the
  redirect naming true sound.

### WE-13-3 A linchpin fate fires

The PC, sure that Reeve Hask is the Choir's man, publishes his bribe-ledger at the Bridgemoot (`cost.exposure` at
S5 against him: the secret `sec.hask.bribes` made public in Vantry's scope). 11.3.10's `exposed` hook fires
Hask's sealed fate: the Cellar Kin lose hold (strong → weak); the Bridgemoot's relation toward House Vantry −1;
Hask dismissed. Nothing in the fate touches the Choir — he was never its man — and the Choir's goal clock keeps
ticking. The world answered the deed exactly as written forty-two years of setting ago, which is what makes the
mistake the PC's, not the DM's.

### WE-13-4 An encounter row fielded (PR-10-8 in miniature)

Ithren crosses the Standing Downs at night. The watch die shows an encounter face; danger wild: d12 = 5 → threat
(1–7); d20 = 8 → row 7–9: the grey bitch and her silent pack (home, leader + mob). 09.8.3 fields the band-2
leader and the band-1 mob of five. The advisory against Ithren's own line (V11, Root Snare, staff) is computed
(09's estimator) — against the reference P2 line it is **fair** (win 96.7%, Staggered 20.7%). The pending threat
arrives with an omen first (10.9.5): *dogs at a distant farm whining at nothing, all facing the same way*. Ithren
can still choose: wait in a hollow, light a fire (the pack is skittish), or go round.

*Non-example.* "A band-4 troll on the downs because the player is strong" — no: tables are fixed by the place, not
the PC (09.8.2); a troll is on the Hem's table at home + 1, and only there.

## Edge cases & adaptation anchors

- **Speech in the Hush.** A PC in a hush-pool who wants to warn a companion: no Talk (cond.silenced); gesture is
  01.18's crude fallback with no tongue at all (DC +5, reach Limited). A written note works (letters), and so does
  a true bell's peal (speech within it is heard).
- **Magic in the Hush.** Arcane and divine workings are impossible (speech); primal workings of elements and growth
  work where the source is present; `deed.primal.spirits` fails (no spirits). An item-bound working follows its
  ability's own limitation (05).
- **Wool in the ears.** Deafness by choice gives `cond.deafened` everywhere and protects from nothing in the Hush
  (the Hush is not a sound). It is a lever against an Orrowan bell-mage's sung working only if that working is a
  hearing-borne effect (05's literal text).
- **Moving a Stilled.** Exert vs Hard to carry one; a cart makes it a Handle beat. Carrying a fresh Stilled out of
  the pool does not wake them; only true sound does.
- **Breaking a Stilled.** A Stilled can be killed (it is a body): `exists: dead`, a piety event if tended (03), and
  the Wakeful's and the fordwardens' memories (12.11.7).
- **Ringing the Last Bell yourself.** The ringing-loft is the Bellwardens' (a refusal of the Prior: will not let a
  stranger into the loft); the bell needs four ringers for a full peal (a group beat, 01).
- **A PC who leaves the region.** South of Vantry Keep the map ends: 13.2.6.
- **No anchor rules in this chapter.** Every rule here is setting content or a binding; adaptation reaches for the
  owning chapters' anchors (the Waking rule is not an anchor: it is canon).

## State touched

- **Read:** every family other chapters own, through their interfaces.
- **Written at the opening (PR-13-1):** time and calendar position; `weather.today` (data, day 1 only);
  `moon.phase`; clocks (13.17.1, owner 13 for the region clocks; faction goal clocks are 11's records); situations
  (`sit.thallen.harrowby_quiet`, `sit.thallen.harrowby_feud`); the Harrowby pool hazard fact; NPC entities on
  mention from the roster; offer (the Prior's); thread (the case).
- **Written by PR-13-3:** location; bond NPCs and relationships; faction-tie statuses (via 11); sealed facts of a
  lost bond; magic facts (`pc.keeper.*`, `pc.accepted.primal.*`); commitments (a place's ask); hooks bound.
- **Written by the Waking rule:** `npc.*.stilled`, `last_waking_try`.
- **Tools used:** `create_entity`, `set_fact`, `set_relationship`, `create_clock`, `tick_clock`, `roll_table`,
  `oracle`, `offer_create`, `mark_boundary`.
- **Hooks / handlers registered:** none new (the region's clocks tick on existing boundaries: `watch`,
  `year`, `season`, and facts the World Turn writes).
- **Clocks created:** `clk.thallen.harrowby_stillness`, `.quiet_wakes`, `.quiet_rises`, `.vantry_digs`,
  `.treaty_burned`; each faction's goal clock (in `factions.13.yaml`).

## Interface requests

**To 00 (and SCHEMAS).** (1) Adopt the `keeper.` id prefix for keepers (powers that hold divine regard; six in
the region). (2) Document `region_*.yaml`'s optional keys (T-13-16). (3) Accept `obj.` for named objects (11's
`object` entity subtype already exists; 15's `case.mill_fire` uses it). (4) 10.1.2's readable place facts gain
`hushed` and `true_bell` (the region's two setting facts; both are read only through the region's hazards and the
Waking rule).

**To 05.** Offer: a named composite for a storied *set* if 05 wants one at integration (13.11.2 authors none).
Canon: 13.3 answers the eight items of 05.7.10; magic `requires` tightened only for Orrowan texts (13.3.1).

**To 08.** The curio exception at Pell's yard (13.11.4) is a regional settlement fact, not a change to 08.8.4.
Ringsilver's price band (3) and the true-bell crafting band (3) use 08's tables.

**To 09.** The generator executes `09-gen_data09.py` up to its write step and calls its `build()` on 13's roster
lines; any change to 09's build is picked up on regeneration. **Finding:** against 09's reference lines, every
band-5 standard is *lethal* to a P4 PC alone, so a home-4 table cannot place a band-5 standard at home + 1 and stay
non-lethal; 13 uses 09's minion variant alone (13.10.3). 09 or 10 may want to state this in 09.8.2 (DL-13-11).

**To 10.** PR-10-8's "word" step is ambiguous about adversary counters; 13 computes it with the counter held
(09.4.4's convention) and prints the no-counter word (DL-13-11). The generic tables of `travel.yaml` were audited
on bands only; run the word step on them (10's own claim "pass by construction" covers bands, not words).

**To 11.** (1) `11-world-sim.py`'s `gain_hold()` lets `expand` raise a tier-3+ faction, against 11.3.4 ("rising
above tier 3 needs a completed grow goal of realm scope"); with the rule as written the region's tier-5 share
after two years is 0% (verbatim sim: 10.0–10.4%). (2) Its AGENDA lacks 11.3.7's `steadfast` row (13-world-sim adds
it). Both resolved at integration (I-026). (3) A data-authored situation (`sit.thallen.*`, no template or a template plus roles) is used for the opening
(11.4.3 lists 13's data as a source).

**To 12.** The regional tables replace 12's as listed in 13.14.1; 12's gender table is kept.

**To 14.** Render the Truths (13.1.5) at session zero; the `[HOW THIS WORKS]`, `[JOURNEY]`, `[CLUE]`,
`[REFUSAL]`, `[WARNING]`, `[CLOCK]` first-use notes of the teaching arc; the pregen cards (13.16.2).

**To 15.** Three cases in the region file (`cases`) — moved into `investigation.yaml#cases` at integration (the region's
`cases` key now lists their ids) [integration: IR ch.13 to 15]; 15 may move them into `investigation.yaml#cases` at
integration (the shape is identical, validity re-checked).

**To 02.** The two setting origins and their kits are in owner-blocks; `orig.up.woken` adds an optional `peoples`
field (which peoples may take it).

## Open empirical questions

| # | Question | Shipped default | Test |
|---|---|---|---|
| OEQ-13-1 | Does a newcomer reach the case's first two nodes in the first session without prompting? | the teaching arc as opportunities, core clues on the green | **T-13-OPEN**: five newcomer sessions (pregens and built characters); target ≥ 4 of 5 reach n1 and n2 in session 1; if fewer, add a third core placement on the road (Cob) |
| OEQ-13-2 | Is the Last Bell's countdown (median week 11) the right pressure for a sandbox newcomer? | Choir goal starts 1/8 | **T-13-PACE**: log the week the player first acts on the Choir across five campaigns; if most never engage before it fires, start at 0 |
| OEQ-13-3 | Is the Waking rule's Remote too stingy to make the long arc feel winnable? | Remote, once a season | **T-13-WAKE**: count waking attempts and successes over a campaign year; if attempts fall off after the first failure, use 13.1.5 T2's Likely as the default |
| OEQ-13-4 | Are the ring-2 tables (two hard rows of five) too sharp for P1 characters drifting out of ring 1? | 6/11/3 with a band-2 home | **T-13-RING2**: simulate P1 vs the Downs and Eastholt tables over 20 journeys (09's estimator per row); if more than one Staggered in four journeys, set the Downs' home band to 1 for its southern half |

