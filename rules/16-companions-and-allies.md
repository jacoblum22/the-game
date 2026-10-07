# 16 — Companions and Allies

> This chapter governs everyone who walks beside the player character: named companions with drives of
> their own, hirelings on contract, followers drawn by the character's name, beasts and mounts, beings
> bound by magic, cohorts that fight as one, and allies who stand with the character for a single scene.
> It fixes how many may follow (Presence, 00.4.4), who will (a serving band always below the character's
> own, so no ally ever out-powers the hero), how they are recruited (chapter 15's requests, terms and
> ceilings), what they are made of (chapter 09's band tables, read as a companion line), how loyal they
> are (chapter 15's standing scale, moved by two sensed clocks — regard and grievance — that read the
> character's witnessed deeds against each companion's own drives), what each rung of loyalty obliges
> them to do and refuse, how they act in a fight (only through chapter 06's command action, their one
> reaction, their standing order and a fixed default), what they do on the road and in downtime, how
> they fall and die (chapter 07's companion ladder, protected by Key 1, telegraphed by a public clock),
> how they grow (slowly, by season, never past the hero), how they witness and voice the character's
> recognition, and how they bring their own stories into the world. It is shaped by one finding and one
> constraint. The finding: in a solo game, companions are where the texture of a party comes from —
> someone to argue with, rely on and lose — and players will try to recruit anyone and ask anything of
> them. The constraint: an AI running a second free-acting character drifts, grants extra actions and
> forgets who a person is; so a companion here never acts except through the player's action, its own
> reaction, or a rule that names the trigger, and its personality is state the narrator reads rather
> than a mood it improvises.

**Reading this chapter.** The rules are in sixteen parts (16.1–16.16). The procedures (PR-16-1…PR-16-12)
are the algorithms the engine and the DM run. The tables (T-16-1…T-16-22) are canonical in
`data/companions.yaml` where they hold numbers. The worked examples follow Wren, 00's continuous
character, through a recruitment, a fight with two commands and one reaction, a loyalty drop and its
confrontation, a hireling's contract ending, and a companion falling. The simulation behind the
companion line, the band cap and the advisory contract is `rules/_process/simulation/16-companion-sim.py`
(output: `16-companion-sim-output.txt`; summary T-16-21). Every number another chapter owns is cited to
its rule; illustrative values are marked *(illustrative; ch.NN owns)*.

---

## Design intent

**Goals served.** Goal 1 (the player feels free to try any creative idea) is served by making every
ally request answerable by a lookup: recruit anyone (16.3 says who will come, at what price, and what
they would need to hear instead of "no"); ask a companion to do anything (16.7–16.8 say what its rung
of loyalty, its drives and its license list allow, and redirect the rest); build any kind of following
(seven kinds, T-16-1, from a hound to a warband to a sworn knight). Goal 2 (the AI responds and reacts
correctly) is served by putting every part of a companion that could drift into state: its numbers
(a band line from chapter 09's tables), its personality (drives and a refusal, rolled and stored, sealed
until learned), its loyalty (a standing rung with a written contract, moved only by listed sources),
its memory (chapter 12's memories) and its every action (chapter 06's command, its reaction, its order,
or a named trigger) [BRIEF §3; C:P13; R4 W4].

**What the research says, and what this chapter takes from it.**
- *Extra bodies are where action economies break.* The side with more bodies wins the action economy
  whatever each body's individual strength; Pathfinder 2e's minions act only when the controller
  spends an action to command them [R1 §01/06 "Extra bodies are the failure point"; R1 #7;
  R: https://2e.aonprd.com/Traits.aspx?ID=653]. Chapter 06 already adopted that model (06.14); this
  chapter builds every companion on it and adds nothing that acts on its own except a reaction and the
  hooks a template lists [00.17.1 Q8; INV-11; R3 G-27].
- *Retainers never outrank their employer, and their number is set by force of personality.* In the
  old-school lineage a retainer is of equal or lower standing than the character who hires them, and
  Charisma sets how many will follow (1 at the bottom of the scale, 4 at the average, more for the
  magnetic) [R: https://oldschoolessentials.necroticgnome.com/srd/index.php/Retainers]. This chapter
  keeps both, in this ruleset's terms: Presence sets the retinue (00.4.4), and a follower serves at a
  band below the character's (16.2.4) — which the simulation shows is exactly what keeps a companion's
  effect on a fight inside chapter 09's "one advisory word gentler" contract (T-16-21).
- *Loyalty is a track the player can read and work, with warnings before anyone walks.* Ironsworn's
  bonds progress by rank and are tested under strain [R5 P-27]; Baldur's Gate 3's approval gives "two
  warnings (once at −20 and once at −40) before" a companion leaves
  [R: https://bg3.wiki/wiki/Approval]; Mount & Blade's companions complain about hunger, missing pay,
  lost battles, moral disagreements and each other before they leave
  [R: https://steamcommunity.com/app/48700/discussions/0/535150948595822006/]; Mausritter's hirelings
  save or flee when "made to go without pay or food, or asked to do something more dangerous than what
  they signed on for" [R: https://loottheroom.uk/the-long-read-mausritter]. This chapter's loyalty is
  chapter 15's standing scale (00.17.1 Q8), its movement is two sensed clocks with mandatory omens
  (INV-14), and its breaking points are a departure clock and a betrayal rule that each require a
  rendered warning first (16.6).
- *A companion's own story is the payoff of loyalty.* Mass Effect 2's loyalty missions and Baldur's
  Gate 3's companion quests tie a companion's devotion to resolving its personal trouble; the solo
  procedures digest asks for companions as "the main social and tactical texture" and as sources of
  hooks [R5 G-3, #8]. Here every principal companion carries a personal thread seeded from its top want
  (16.12), and completing it is a deed of weight (the one road to Devoted besides a rescue).
- *Gangs and experts are different kinds of help.* Blades in the Dark separates cohorts into gangs (a
  group with scale) and experts (one specialist), with a cohort harm ladder of its own
  [R: https://github.com/amazingrando/blades-in-the-dark-srd-content/blob/main/Blades-in-the-Dark-SRD.md].
  This chapter's cohort (16.2.6) is chapter 06's mob seen from the PC's side: one entity, pooled
  Vitality, a numbers step, and one retinue place per member so that a warband costs exactly what the
  same number of individuals would.
- *A companion falling should be a scene, not a die roll.* Ironsworn's Companion Endure Harm leaves a
  companion "out of action. Without aid, they die in an hour or two" on a miss
  [R: https://ironsworn-rpg.fandom.com/wiki/Companion_Endure_Harm]; R6's telegraphed-death model makes
  "Dying … an explicit rescue objective for companions and the scene" [R6 C-R2]. Chapter 07 owns the
  ladder (Down, or bleeding out on a public four-round clock); this chapter owns what the fall does to
  loyalty, grief, the retinue and the world.
- *Witnesses make reputation.* Public recognition requires witnessed evidence; companions are carriers
  who spread a deed (03.10.2) and are the natural voices of several recognition vehicles: the Reflection
  at Rest is staged among "companions by a fire" (V7), the Seer's Reading may be "a companion's remark"
  (V6), the Witnessed Epithet is often first spoken by someone who was there (V1) [R6 A.4; 04.6.4;
  `data/vehicles.yaml`].

**What this chapter deliberately avoids.**
- *A second player character.* No companion has a turn, an action of its own, a free beat outside
  conflict that the party's time budget does not pay for, or a decision the DM improvises (16.13.3).
- *Allies who out-power the hero.* A follower's serving band is capped one below the PC's power band, and
  nobody whose own band exceeds the PC's follows at all (16.2.4); the great may travel with the character,
  but as allies on their own lead (16.7.12), never as a commanded retinue.
- *Loyalty by narrator mood.* Loyalty moves only through chapter 15's listed sources and this chapter's
  two clocks, whose tick sources are a closed list (T-16-8); no companion "comes round" by the DM's
  feeling (15.1.5, 12.11.6).
- *Betrayal without warning.* A companion turns on the character only at Hostile, only after an
  ultimatum omen was rendered, and only through a listed opportunity (16.6.6).
- *A separate companion rules engine.* Companions use the same pipeline (01), conditions (06), harm
  (07), evidence (03), standing (15) and memories (12) as everyone else; this chapter adds only what is
  particular to someone who follows.

**Rule kinds and runtime.** Every rule below carries its kinds (00.2.2). The chapter assumes RC-STORE
(the ally record, retinue, clocks, contracts), RC-SEAL (drives, lines and secrets until learned),
RC-SCHED (upkeep, departure, growth and follower handlers), RC-EVAL (command beats, intercepts, knack
effects), RC-RNG (drives, candidates, betrayal rows), RC-LOG (memories, chronicle lines) and RC-DATA
(`data/companions.yaml`) [00.14.1].

---

## Rules

Rule ids are `16.S.R`. Citations per 00.1.6. In this chapter, "**ally**" means anyone of T-16-1;
"**companion**" in a rule about conflict means any ally fighting on the PC's side, as chapter 06 uses the
word (06.14.1); elsewhere it means the kind `companion` of T-16-1 when the text says "the kind
companion". "The PC" is the player character.

### 16.1 What an ally is

**16.1.1 The seven kinds.** `[D]` + `[J:enum]` Every ally is exactly one kind (T-16-1;
`data/companions.yaml#kinds`). The kind is the *bond* — why they follow — and is independent of the
*template* (16.4), which is what they can do: a soldier may be a hireling (paid), a companion (come for
their own reasons) or a follower (drawn by the PC's name).

**T-16-1 The kinds of ally.**

| Kind | True only when | False for | Loyalty | Paid | Retinue places | NPC depth |
|---|---|---|---|---|---|---|
| `hireling` | a person serves under a recorded **contract** (duty, wage, term; 16.14.2) | a person who would stay unpaid (companion) | standing (16.5) + contract | wage (08.8.8) | 1 | recurring; principal after 4 weeks' service or when named in a thread |
| `companion` | a person (or speaking being) travels with the PC for reasons of their own, recorded as a **joining term** (a want, a bond, a debt, a cause; 16.3.4) | someone paid to (hireling); someone sworn to the PC's name (follower) | standing (16.5) | keep only (16.14.3) | 1 | principal |
| `follower` | a person sworn to the PC through the PC's name, rank or calling (16.3.6), with a recorded **oath of service** | a person recruited by request (companion) | standing (16.5), starts Friendly | keep only | 1 | recurring (principal when named in a thread) |
| `beast` | an animal trained, bonded or tamed to follow the PC (hound, hawk, bonded wolf, familiar), or a mount that is ridden into conflict or bonded (16.15) | a mount or pack animal used only to carry (it is an item with a companion record but takes no retinue place, T-16-2) [verification: V2c-002] | standing on the beast scale (16.15.3) | upkeep (08.10.2) | 1 (none for an unbonded mount or pack beast) | — (beasts have no NPC depth; they have a temperament) |
| `bound` | a being whose service is a working's effect (05): a summoned servant, a raised dead, an automaton, a familiar bound by `rit.bind_familiar` | an animal that follows by bond (beast) | **none**: obedience is the working's text (16.15.6) | Focus or components (05) | 1 if the working is lasting (`duration: permanent`); 0 for a scene's servant | — |
| `cohort` | three to six members of **one** template who act as one entity (a warband, a lance of spears, a militia squad), each serving for the same reason (hire, oath or cause) | a group of named individuals (each its own ally) | one standing for the whole cohort (16.2.6) | per member | 1 per member | the cohort is recurring; its leader, if named, is a separate ally |
| `scene_ally` | a person or group who fights or works beside the PC for one scene without joining (the caravan guard, the village militia, a knight who rides with the PC to the bridge) | anyone who travels on with the PC after `scene_end` (then recruit them by 16.3) | their ordinary standing (15) | — | 0 | as 12 generates them |

*Classifying* `[J:enum]`: when the fiction makes an ally (the player says "the boy wants to come with
us"), the DM classifies the kind by the first row whose "true only when" holds, in table order; a
person who could be two kinds (paid *and* devoted) is the kind of their **recorded** reason (contract →
hireling; joining term → companion; oath → follower). Uncertain → `scene_ally` until a recruitment frame
(16.3) records a reason. *Worst case (J):* the wrong kind for one ally — the wrong upkeep line and loyalty
starting point, both corrected at the next recruitment or contract frame, which is where the reason is
recorded (class iv).

**16.1.2 The ally record.** `[D]` + `[S]` An ally is an entity of kind `companion` (00.6.1; the entity
kind covers all seven of T-16-1, whose ally kind is the field `ally_kind`) that extends 00.6.2's NPC shape
with these fields (`data/companions.yaml#record_fields`; owner 16):

```yaml
Ally (extends NPC):
  ally_kind: hireling | companion | follower | beast | bound | cohort | scene_ally
  template: cmp.*                    # 16.4; T-16-19
  own_band: 1..5                     # what the person is (09's threat-band ladder)
  serving_band: 1..5                 # computed [D]: min(own_band, band_cap(pc)) (16.2.4)
  line: {attributes, competence, defenses, guard, vitality, armor, attacks, focus, size, pace}  # computed from template x serving_band (16.4)
  knacks: [kn.*]                     # <= 3 (16.4.7)
  abilities: [ab.*]                  # <= 3, from the template or a protégé's calling (16.10.4)
  members: int                       # cohort only, 3..6 (16.2.6)
  drives: {values: [{axis: conduct.*, pole: +1|-1, known_to_pc: bool}] (2), want: want_id, refusal: refusal_id}   # sealed until learned (16.5.6)
  temperament: steady | skittish | fierce | gentle      # beasts only (16.15.3)
  standing_to_pc: -3..+3             # = loyalty (15.1.1; 16.5.1)
  regard_clock: clk.16.regard.<id>   # 16.5.3
  grievance_clock: clk.16.grievance.<id>
  departure_clock: clk.16.departure.<id> | null        # 16.6.2
  joining: {kind: want | bond | debt | cause | contract | oath | working, ref: id}   # why they follow (16.3)
  contract: {duty: str, wage_week: int, hazard: R1..R5, term: {weeks: int} | venture | open, share: none | half | full, paid_through: time} | null   # hirelings (16.14.2)
  hears: voice | signs | bond        # 06.14.2 decision 1
  standing_order: guard_me | hold_him | harry_that_one | hold_this_ground | stay_back | null   # in conflict (06.14.4)
  default_order: <one of the five>   # template, adjusted by loyalty (16.7.3)
  orders_allowed: [<ids>]            # T-16-12
  journey_roles: [navigator | lookout | scout | forager | quartermaster]   # 16.8.4
  carry: int                         # load units it carries for the party (08.9; 0 if none)
  supply_need: int                   # per day on a venture (10.6.2; 1 for most, 2 for large beasts not grazing)
  tracks_evidence: bool              # 03.2.7; true only for protégé templates (16.10.4)
  service: {joined_at: time, weeks_served: int, last_growth: time}
  thread: thread_id | null           # its personal thread (16.12)
  harm_state: active | down | bleeding_out | dead | departed    # 07.12
  wound: ref | null                  # at most one (07.12.2)
```

**16.1.3 Visibility.** `[D]` Per 00.6.4, classified once here (the codex renders exactly this, 14):

| Field family | Visibility | Why |
|---|---|---|
| name, kind, template role, retinue places, serving band (as "seasoned", "elite" … words), carry, journey roles, standing order | **shown** | the player commands them and must know what they are |
| line (attack, Guard, Vitality current/max, conditions, wound) | **shown** | an ally is the player's piece, not a foe; its numbers appear in its OFFERs anyway |
| loyalty (standing rung *name*), contract terms, wages owed | **available** | like any NPC's rung (15.1.1); the player may always ask "how does Oda feel about me?" out of fiction and get the rung name |
| regard and grievance clocks | **sensed** (the player knows each exists; fill hidden; every tick renders an omen, INV-14) | loyalty should be read in faces, not a meter |
| drives (values, want, line) | **sealed** until learned (16.5.6), then **available** | discovering who someone is, is play |
| secrets (principal depth, 12.11.1) | **sealed** with a gate | 00.6.5 |
| own band, if above the serving band | **available** ("he was a knight's man once") | the player should know who is being held back by the cap |

**16.1.4 Allies are people first.** `[N]` An ally is an NPC (or a beast) who has chosen to follow. Every
NPC rule still applies to them unless this chapter replaces it: they hold standing toward the PC and
toward each other (15.1.8), keep memories (12.11.7), have voice and habit (12.11.3), wants, a refusal and,
at principal depth, a secret (12.11.1); they may be lied to, persuaded, bribed by others and courted by
factions. This chapter adds the follower's layer: the retinue, the line, loyalty's clocks and contract,
commands, roles, and the fall.

### 16.2 The retinue: how many, and who may follow

**16.2.1 The retinue cap.** `[D]` The **retinue** is every ally who follows the PC from scene to scene:
every ally of T-16-1 except scene allies, plus nothing else. Its size is capped by Presence, the one
derived value 00.4.4 assigns to it:

`retinue_cap = clamp(2 + Presence, 1, 6)` — Presence −1 → **1**; 0 → **2**; +1 → **3**; +2 → **4**; +3 → **5**;
+4 (the lifetime maximum, 00.4.3) → **6**.

The cap counts **retinue places** (16.2.2), not heads. It is recomputed whenever Presence changes (a P1
reroll, the one lifetime +1, a maim, 00.4.3). If a change leaves the retinue over the cap, nobody leaves
at once: the PC must bring it within the cap by the next `week` boundary (dismiss, post someone, 16.2.3,
or release a bound being), or the most recently joined ally whose standing is below Friendly departs at
that boundary (16.6.1, cause `overflow`), announced the day before.
*Why these numbers.* The old-school table gives 1 follower at the bottom of the Charisma scale and 4 at
its middle, for a party of several players sharing a table's attention
[R: https://oldschoolessentials.necroticgnome.com/srd/index.php/Retainers]. A solo character is the
only one giving commands, every command costs one of three actions (06.14.2), and the DM voices every
follower; the simulation shows two followers already move a fight by one to two advisory words and four
by up to four (T-16-21). Two at an average Presence, one for the cold and the awkward, six only for the
most magnetic person in the world, keeps a retinue a party's texture and never a second army [DL-16-02].

**16.2.2 Retinue places.** `[D]` (`data/companions.yaml#retinue.places`)

**T-16-2 Places.**

| Ally | Places |
|---|---|
| hireling, companion, follower | 1 each |
| beast that is trained, bonded or tamed (hound, hawk, bonded wolf or bear) | 1 |
| familiar (`rit.bind_familiar`) or any lasting bound being (`duration: permanent`) | 1 |
| bound being of a scene or shorter duration (`eff.summon` with a duration) | 0 (its working's cost is its price, 05) |
| cohort | 1 per **current** member (a cohort of five is five places; a member who falls frees a place only when it is dead or has departed) |
| mount or pack beast used to ride or carry (08.10.1), including a war mount ridden in conflict (it is part of the rider's participant, 06.15.1) | 0 |
| a mount that is also **bonded** (`rit.beast_bond`, or a beast companion that is ridden) | 1 (it is a beast who carries you) |
| scene ally | 0 |
| household servants a lifestyle includes (08.8.6: the wealthy lifestyle's servant, the noble household of four), staff of a holding (08.8.8), soldiers at a post under a rank (11) who do not travel with the PC | 0: they are not the retinue; they keep a place, not the PC |

**16.2.3 Leaving someone behind on purpose.** `[D]` An ally may be **posted**: left at a holding, a
haven or a named place with a stated task (keep the house, mind the horses, wait at the inn). A posted
ally takes no retinue place while posted, keeps its loyalty, costs keep or wage as usual (16.14), and
rejoins when the PC returns to the place (no frame), but only into a free retinue place: while the retinue is at its cap (16.2.1) it stays posted, and the player chooses who rejoins when more are posted than places are free [verification: V2c-003]. While posted it acts only through its task
(`tbl.16.posted_task`, a d6 per week through `h.16.retinue_upkeep`: 1 a complication at the place (a
thread hook, 11), 2–5 the task kept, 6 the task kept and one useful thing learned (a rumor, 11)). A posted
ally's regard and grievance clocks do not tick from the PC's deeds (it did not witness them) but do from
pay and keep. This is the honest answer to "I want more followers than I can lead": keep them where you
have a home, and take with you the ones the cap allows [R5 NP-05; R6 D-R5].

**16.2.4 The band cap: no ally out-powers the hero.** `[D]` Every ally serves at a band no higher than

`band_cap(pc) = max(1, power_band(pc) − 1)`,   `serving_band = min(own_band, band_cap(pc))`,

where `power_band` is 04's (00.17.1 Q5). A novice (P1) leads allies at band 1; a seasoned character (P2)
at band 1; an elite (P3) at band 2; a champion (P4) at band 3; a legend (P5) at band 4. Two numbers are kept
apart: the ally's **own band** (what the person or creature is) and its **serving band** (how well it fights
under this PC's lead). The ally's **line** (16.4) is built at its serving band; its own band is kept, so the
engine rebuilds the line the moment the cap rises (trigger `trg.16.band_cap_changed` on any `power_band`
change).
- **Who may follow at all:** anyone whose own band is **at or below the PC's power band**. A veteran (own
  band 3) may sign with an elite (P3) and serves at band 2 — under a leader of her own standing she fights to
  the pay and the plan, not to the limit of what she is; when the PC becomes a champion she serves at band 3.
  Chapter 05's `rit.beast_bond` uses the same test ("at or below your power band").
- **Who will not follow:** anyone whose own band **exceeds** the PC's power band. A recruitment frame for
  them is G4 for the intent "follow me" (16.3.1 test 3) — people do not take orders from someone they do not
  look up to, and a beast stronger than its would-be master does not come to hand — and the redirect offers
  what *is* possible: travel together as an **escort** on their own lead (16.7.12), a deal (15.7), or a
  thread that makes the PC someone they would follow. Bound beings follow their working regardless (05),
  at the serving band.
*Why.* Three reasons converge. (1) Precedent: old-school retainers may not outrank their employer
[R: https://oldschoolessentials.necroticgnome.com/srd/index.php/Retainers]. (2) The genre: the hero of a
solo story is the protagonist; a peer travelling under orders is a second protagonist, which constitution
IV puts out of scope. (3) The arithmetic: with one companion of the PC's own band, the fight moves **two**
advisory words in 4 of 16 tested shapes (P2 against two T2 goes from fair to trivial; P5 against one T5 from
hard to easy); with the cap, one companion moves it **at most one** word in every shape (T-16-21) — exactly
chapter 09's contract (09.6.3) [DL-16-01].

**16.2.5 A full retinue.** `[D]` A recruitment that would exceed `retinue_cap` is G4 for the intent
"join me", and the redirect names, in the fiction, the three honest ways forward: let someone go (16.6.4),
post someone (16.2.3), or have this person stand with the PC as a scene ally for what is at hand. Follower
offers (16.3.6) that arrive while the retinue is full are **deferred** automatically and re-presented at
the next `reflection` with a free place (04's standing-offer machinery, 00.6.2 `offer`).

**16.2.6 Cohorts: a band that fights as one.** `[D]` + `[J:flag]` A **cohort** is three to six members of
**one** template, joined for **one** reason (all hired on one contract, all sworn by one oath, all come for
one cause), who move and fight as a single ally — chapter 06's mob seen from the PC's side [06.10.2;
R: https://github.com/amazingrando/blades-in-the-dark-srd-content/blob/main/Blades-in-the-Dark-SRD.md (gangs and experts)].
`[J:flag]` *"Are these allies of one template, joined for one recorded reason, and does the player want
them to act together?"* True → one cohort record. False → separate allies. A named leader is never folded
in: the sergeant of the spears is his own ally. Uncertain → separate allies. *Worst case (J):* a group run as
individuals or the reverse — the same places and wages either way (16.2.2), differing only in command
bookkeeping (class iv: the player may split or merge at any `scene_end`).
- **Line:** the template's line at the serving band; **Vitality pooled** (`members × the line's
  Vitality`); one Guard and one set of defenses; `members_now = ceil(pool ÷ member Vitality)` (06.10.2).
- **Numbers:** its attacks carry 06.10.3's numbers step by `members_now` (1–2: 0; 3–5: +1 rung; 6: +2
  rungs, inside the ±2 effect-step cap). It never Flanks and never grants a Flank.
- **Command:** one Command (06.14.2) buys one beat **of the whole cohort**. It has one reaction and one
  standing order.
- **Places and pay:** one place and one wage (or keep) **per current member**. The simulation shows a
  cohort of four is worth about what four individual allies of the same band are worth (T-16-21: mean
  shift 1.7 words against 2.0), so pricing it per member keeps the two equivalent; what a cohort buys is
  simplicity, not power [DL-16-03].
- **Loyalty:** one standing and one pair of clocks for the whole cohort, voiced by whoever speaks for them;
  a named leader's own standing, if it falls to Wary or worse, ticks the cohort's grievance clock +1 each
  week (T-16-8 source G9).
- **Falling:** members fall as the pool falls past multiples of one member's Vitality (06.10.2). Each
  member felled by a lethal harm event is **bleeding out**; all bleeding members share **one**
  `clk.bleeding_out.<cohort>` (07.12.1: 4 segments, +1 each round, +1 per further lethal harm event on the
  cohort) and **one** stabilizing beat saves them all (they fall together, and one tender works down the
  line). If the clock completes, every bleeding member dies. A cohort reduced below three members becomes
  that many separate allies of its template at the next `scene_end`, each with the cohort's standing.
- **Refilling:** new members of the same template are recruited by 16.3 and join at the cohort's current
  standing minus one (strangers to the band), never above Friendly.

### 16.3 Recruitment

**16.3.1 The recruitment gate.** `[J:enum]` + `[D]` Any attempt to make someone follow — hire, invite,
swear in, tame, bind — passes these tests in order (PR-16-1). Each failure is a redirect, never a bare no
(P16; 00.12.3):

| # | Test | Fails when | Redirect |
|---|---|---|---|
| 1 | **Mind** (09.2.7; 15.2.7) | `mindless` (only a working can bind it: 05); `animal` asked by Talk (beasts are bought, bonded or tamed: 16.3.7) | name the way that works for this mind |
| 2 | **Tongue** (15.2.7) | no shared language and the request is above R2 | an interpreter, or learn the tongue (15.11) |
| 3 | **Band** (16.2.4) | its own band exceeds the PC's power band (it would serve at `band_cap(pc)` otherwise) | escort on its own lead (16.7.12), a deal, a thread |
| 4 | **Places** (16.2.5) | the retinue is full | let someone go, post someone, or a scene ally |
| 5 | **Refusal** (15.2.3) | the person's recorded refusal covers leaving with the PC (e.g. `will not leave this place`) | what would lift it, if anything (15.2.4) |
| 6 | **The frame** | 15's request (16.3.3–16.3.5) at the size of T-16-9 or T-16-10, with its ceiling (15.3.4) | 15's own redirects: a smaller ask, a term, a campaign (15.8.1) |

The only judgment in tests 1–5 is the classification of an unlisted creature's archetype (09.2.4); every
other value is read from state. *Worst case (J):* a test applied to the wrong field (own band read as serving
band) — one refused or one wrongly admitted recruit, visible in the OFFER, which names the cap and the
places (class ii).

**16.3.2 Finding hands: who is available.** `[D]` + `[J:enum]` Hirelings are found by chapter 15's
**Recruit** day activity (`dt.recruit`, 15.13.14): a Talk request against the settlement's tier (camp or
village Easy, town Moderate, city Hard); **delivered reach = the number of candidates presented** (0–4). In
`free` mode the same frame ("I ask around the docks for hands") takes one **watch** instead of a day. The
player names the **role** wanted from the hire roles of T-16-19 (`[J:enum]` when the player names a job
rather than a role — "someone who knows the marsh" → `cmp.guide`; uncertain → the role whose `hire_roles`
text names the job, else the player is asked). Each candidate is generated at once:
1. **Template** = the role's template; **own band** = the template's `hire_band`, lowered to the
   settlement's maximum (camp or village **1**, town **2**, city **3**; a band-4 champion is never found by
   asking around: only through a thread or a named NPC, T-16-9 note) and to the PC's power band (those who
   would not sign with someone below them simply are not among the candidates who come forward).
2. **The person** by 12.11.1 at **recurring** depth (name, gender and pronouns, age, detail, demeanor,
   want, fear, voice, one refusal, knowledge scope), with `tbl.16.hire_quirk` (d12: what makes this one
   different — cheap, eager, scarred, devout, a drinker, knows the country …) as the distinctive detail.
3. **Standing** by the reaction roll (12.11.2, with its modifiers; the PC's reputation for paying well or
   badly is a ±1 modifier when 11's reputation content says so).
4. **Drives** (16.5.5) are rolled only when a contract is signed; until then the candidate is a
   recurring NPC like any other.
Candidates not hired remain in the settlement as recurring NPCs (write-on-mention) and may be hired
later without a second Recruit. *Worst case (J, role classification):* the wrong role for a job described
in words — one candidate of a neighboring template, which the player sees before hiring (class ii).

**16.3.3 Hiring: a deal whose price is the wage.** `[J:rung]` + `[J:flag]` + `[D]`

```
### 16.3.3  Hire                                                     [J:rung] [J:flag] [D]
Trigger [T]:        the PC offers a candidate (or any person) work for wages
Loads in:           situation.social.bargaining, situation.downtime.commerce
License check:      basic verb: verb.talk (request with a deal, 15.4.1, 15.7.1)
Decisions (J):      1. HAZARD [J:rung] "What does the job ask this person to risk?" (T-16-9,
                       data/companions.yaml#hire_sizes), judged ONLY from the job as the PC states it
                       plus facts in state about where it goes (10's danger rating of the route and
                       site; recorded lethal contexts):
                       R1 CAMP WORK -- day labor in a settlement or a haven: carry, cook, groom, guard
                         a door. Typical: porter for a market day. Boundary: carry baggage on a
                         settled road for one day (R1).
                       R2 SAFE ROAD -- travel and work in safe or settled country, nights in havens or
                         camps; no fight expected. Typical: guide to the next town. Boundary: a week's
                         journey on a wild-rated road with no known threat (R2).
                       R3 VENTURE -- wild or perilous country, a site, or a fight expected with no
                         recorded lethal context. Typical: soldier for a bandit-clearing. Boundary:
                         scout a ruin whose dangers are unknown (R3).
                       R4 DEADLY -- deadly country, or a foe with a recorded lethal context, or a site
                         whose danger clock is known to be imminent. Typical: into the wight's barrow.
                         Boundary: a perilous road with a lethal-context beast known on it (R4).
                       R5 FORLORN -- near-certain death, or against the person's own kin, faction or
                         faith. Wages never buy it.
                       Between two rungs: the HIGHER. A job the PC misdescribes is a lie (15.5); the
                       hazard is re-judged when the truth is known (T-16-8 source G6).
                    2. TERMS [J:flag] per 15.3.5, plus two hire-specific terms that need no price
                       test: the WAGE paid in advance (a week's wage, or a day's for a day's job) is one
                       Payment term; HAZARD PAY (the wage doubled for the contract) is a second. A Want
                       term (the work serves their want: "earn enough to leave soldiering") may replace
                       either. At most two terms (15.3.4).
Computation [D]:    request = the hazard rung; effective = hazard - terms (min R1); ceiling, DC and
                    certainty per 15.3.3-15.3.4 and 15.3.10. Wage terms never reduce R5. A band-4 hire
                    (wage.champion) needs a Want term on a thread they believe in; a band-5 person
                    never hires for coin (08.8.8).
                    On success: the contract (16.14.2) {duty: template role + the job as stated,
                    wage_week, hazard accepted = the hazard rung, term as agreed (weeks | venture |
                    open), share by template (veteran half, champion full)}; ally_kind hireling;
                    drives rolled (16.5.5); the advance moved.
Stakes:             Safe at effective R1 (they decline; the candidate stays available); Risky above
                    (a closed door with this candidate, 01.13.9)
State writes:       contract; ally record; coin; relationship; memory (promised: the contract)
Narration may not imply: that the hireling accepted danger above the hazard rung of its contract
Worst case (J):     hazard one rung low: the contract undercounts the danger; when the venture
                    reaches the real danger, the hireling's command refusals (16.7.2) and grievance
                    source G6 fire, so the error is paid for in play, not hidden (class iv). One term
                    wrongly allowed: one rung (class i).
Examples:           inside: a Neutral soldier hired to clear bandits from a wild road (R3) with a
                      week's wage in advance -> effective R2 = Neutral's ceiling -> DC 12 against a
                      defense of 10 (T-15-3). boundary: the same soldier for the wight's barrow (R4):
                      wage + hazard pay -> R2 -> the same roll, at double pay.
                    outside: "a forlorn hope against the dragon" (R5) -> wages never reduce R5; the
                      redirect names what would: a want, a bond, a cause (16.3.4).
                    non-example: "It's an easy job, really" -> phrasing; the hazard follows the
                      facts of where the job goes.
Anchor:             yes. Intent verbs: hire, engage, pay to come, sign on, take into service. Knobs:
                    time_cost (a day per Recruit -> a watch in free mode); reach_unit (candidates ->
                    contract weeks when renegotiating, 16.14.4).
Basis:              [15.3.2-15.3.5] [15.7.1] [08.8.8] [R: https://loottheroom.uk/the-long-read-mausritter
                    (hirelings flee when asked to do more than they signed on for)] [DL-16-05]
```

**16.3.4 Inviting a companion.** `[J:rung]` + `[J:flag]` + `[D]` A person met in play who would come for
their own reasons is asked by a **request** (15.4.1) "come with me", sized `[J:rung]` by what following
costs **them** (T-16-10; `data/companions.yaml#join_sizes`):

| Rung | Following costs them… | Typical | Boundary |
|---|---|---|---|
| R2 | nothing they value: footloose, idle, or the road itself is what they want | a wandering minstrel who wants to see the coast | a sellsword between contracts (R2) |
| R3 | a season away from a trade, a post or a home they can return to | a smith's journeyman; a temple's lay brother | a village's best tracker in harvest season (R3) |
| R4 | leaving home or family duty for good, or walking into a known lethal danger | the miller's daughter leaving her widowed father | a knight's squire leaving his knight (R4) |
| R5 | betraying their lord, kin or faith, or abandoning dependents | a guard deserting his post to follow the PC | a priestess leaving her temple to serve a heretic (R5) |

Between two rungs: the higher. Terms are 15.3.5's: **Want** (following serves a recorded want — "come with
me and we will find your brother" — the strongest and most common), **Obligation** (the PC binds a stated
future act: "I will see you to the coast"), **Leverage** (coercion; allowed, but a companion joined by
leverage records `joining: {kind: leverage}`, starts with its grievance clock at 3 of 6, cannot rise above
Warm while the leverage stands, and its departure clock starts the day the leverage is released or
lapses), **Payment** (coin offered makes the person a **hireling**, not a companion: the frame is 16.3.3).
On success: `ally_kind: companion`, `joining` recorded with the term's id, promotion to **principal**
depth (12.11.1: secret, three ranked wants, ties), drives rolled (16.5.5), and a personal thread seeded
(16.12). A person whose request is above the ceiling by exactly one rung with a term may be won over by a
**persuasion campaign** (15.8.1), which is how most companions worth having are recruited: a few scenes of
showing them the road serves their want. *Worst case (J):* one rung (class i), shown with the ceiling in the
OFFER; the joining term is auditable because it cites a want, commitment or fact id (INV-20).

**16.3.5 Bonds from creation.** `[D]` A person named in a creation bond (02.9.2) may be invited by 16.3.4
at their set standing (an anchor friend at Friendly has ceiling R4, so a "come with me" that costs them
their home is a single roll with one term). An animal named in a bond (02's request: "an animal named in
a bond is a candidate companion") joins as a beast at Friendly with no frame if it is the PC's own (a dog
raised from a pup), and serves at the band cap.

**16.3.6 Followers: drawn by the name.** `[T]` + `[D]` Followers are not asked; they come.
Handler `h.16.follower_offers` (`reflection`, phase 8, after 04's recognition pass) raises one **follower
offer** for the first of these that holds, at most **one per season**:
- a calling tier of 2 or more was **confirmed** (04; not merely granted provisionally) since the last
  follower offer, and its crystallization or any of its evidence in the last season had at least one
  **carrier** witness (03.10.2): the follower comes from that witness's scope (03.10.4: the community
  that saw it);
- an institutional **rank** (11) whose record grants followers was gained: the rank's followers come as
  that rank says (11 owns the count; this chapter applies the retinue cap — followers beyond it serve at
  their post, 16.2.2).
The follower is generated `[D]`: template by the calling's key deed branch (T-16-20:
`data/companions.yaml#follower_templates`), own band `max(1, band_cap(pc) − 1)` (followers are eager,
not yet seasoned), standing **Friendly**, `joining: {kind: oath}`, the oath of service written as a
commitment, and its first drive value fixed to the calling's evidence (a follower drawn by acts of mercy
holds `conduct.mercy +1`: they came because of what they saw). The offer is staged as a scene — someone
waits at the PC's door, asks on the road, kneels at a shrine — and resolved by the offer protocol (00.6.2):
**accept** (joins), **decline** (no follower; a chronicle line), **defer** (the offer stands until the
next season boundary, then lapses). A full retinue defers it automatically (16.2.5). *Why tie followers to
confirmed, witnessed tiers:* the fiction's "people follow you" must rest on something the world saw;
recognition's witness gate is exactly that, and confirmation (not provisional grant) keeps a lapse from
leaving a follower behind a calling the PC no longer holds [04.1; 03.10; R6 A-R1; DL-16-09].

**16.3.7 Beasts.** `[D]` + `[J:flag]` A beast follows by one of three roads:
1. **Bought trained** (a hound from a kennel, a hawk from a falconer, a war dog): an item purchase (08)
   creating a beast ally with standing **Neutral** and its template's training. Prices are 08's; until
   `base_items.yaml` carries them, the `price` field of the template (T-16-19) applies (Interface
   requests).
2. **Bonded** by `rit.beast_bond` (05): standing **Friendly** (the rite's scope), `hears: bond` (it
   understands intent without words), `ab.beast_at_heel` usable with it.
3. **Tamed**: a wild beast of `mind: animal` (09.2.7) held, fed and handled over time. The taming is a
   **project** (15.12) on a 6-segment clock "the <beast> will not come to hand", ticked by one Handle beat
   a day (`deed.wilds.animals.training`, Presence, against the beast's Resolve defense; licensed by
   `lic.training.wilds_animals`, whose crude fallback is a Handle at +5 with Limited reach). Completion: a
   beast ally at standing **Wary** (it tolerates the PC), rising by care (16.15.3). `[J:flag]` *"Is this
   beast one that can be tamed at all?"* True only for `creature.beast` whose archetype is not
   `creature.beast.monstrous` and whose own band ≤ the PC's power band; false for any other creature (a
   monstrous beast can be bound only by a rite that says so). Uncertain → false. *Worst case (J):* a beast
   admitted to taming that should not be — one project's time spent on a clock that the beast's behavior
   list (09) can still end by fleeing (class iv).
Mounts are bought as items (08.10.1) and created as beast allies at once (standing Neutral; 0 places,
16.2.2); they take a retinue place only when bonded.

**16.3.8 Bound beings.** `[D]` Chapter 05's workings create them (`eff.summon` with a template "as a
companion of threat band B (ch.16)"). This chapter supplies only: the templates (`cmp.bound_servant`,
`cmp.bound_dead`, `cmp.bound_automaton`, `cmp.familiar`), the serving-band cap (16.2.4), the places
(16.2.2), and their obedience rule (16.15.6). There is no recruitment frame: the working is the frame.

**16.3.9 Recruiting anyone.** `[D]` + `[J:enum]` *Anchor: yes.* Players will try to recruit the troll under
the bridge, the captive goblin, the ghost in the chapel, the captain who just tried to kill them. The gate
of 16.3.1 answers every case by lookup, and the template follows the creature:
- a **sapient or cunning** creature (09.2.7) that can be talked to joins by 16.3.4 (or 16.3.3 if it will
  work for pay); its template is **`cmp.from_archetype`**: its own archetype's attribute rungs, trained
  defenses, attacks, tags and `cannot` list (09.2) at the serving band, with this chapter's companion
  Vitality and armor (16.4.3) and none of its `adversary_only` powers; its drives are rolled as anyone's,
  but a `cunning` mind rolls its first value on `tbl.16.drive_cunning` (greed, fear, appetite, pride);
- an **alien** mind (a spirit, an elemental) joins only with a license or fact that bridges it (15.2.7:
  its Talk is otherwise capped Limited, and "come with me" is at least R2, which Limited reach cannot
  deliver as a joining); when bridged, as a sapient;
- an **animal** by 16.3.7; a **mindless** thing only by a working (05).
A former foe's starting standing is its current standing (15.1.4: a cunning creature starts Hostile in a
fight), so most such recruitments are campaigns with terms — which is the honest shape of "turn an enemy
into a friend". Intent verbs: recruit, win over to my side, take into service, adopt, tame, enlist.
Knobs: `time_cost` (a scene per campaign beat → a week in downtime), `targets` (one person → a group that
decides together, 15.4.7, joining as a cohort). *Worst case (J, mind classification):* read from 09's
archetype field, so the only judgment is the archetype of an unlisted creature (09.2.4), bounded by 09's
own worst case.

### 16.4 Templates: what an ally is made of

**16.4.1 A template is a role, not a person.** `[D]` A **template** (`cmp.*`, `data/companions.yaml#templates`,
T-16-19) is what an ally can do: its attribute rungs, its trained deed tags, its attacks and armor, its
knacks, its allowed orders and journey roles, its carry and supply, its hire band and wage line, and the
band range it can grow through. The kind (16.1.1) is why the ally follows; the template is what it brings.
Forty templates cover hired hands, soldiers and specialists, people met on the road, protégés,
followers, beasts, mounts, bound beings and the from-archetype template for anything else (T-16-19). A
template is never a stat block that ignores band: every number is read at the **serving band** from
chapter 09's band tables, so one template serves a village porter and a city veteran alike.

**16.4.2 The line at the serving band.** `[D]` The engine builds an ally's line from its template and its
serving band `b` exactly as chapter 09 builds an adversary's (09.3.2–09.3.4), with chapter 09's band table
T-09-2 (`c_b` = +1…+5; rungs apex / high / mid / low / feeble):
- **Attributes:** each of the seven at the template's rung for band `b`.
- **Competence:** `{tag, value: c_b}` on each of the template's `trained` deed tags (two to four tags at
  level 2 or 3); nothing elsewhere. Allies have no PC floor at `deed` (00.3.6's floor is the PC's).
- **Defenses:** `defense[attr] = 10 + attribute + (c_b if attr ∈ trained_defenses)`; **Guard** =
  `10 + Agility + c_b + edge` (+1 edge for a carried shield, 06.4.1).
- **Attacks:** each template attack names a verb (Strike or Grapple), an attribute and harm tags;
  **modifier** = rung(attribute) + `c_b`; **severity** = the band's standard harm (T-09-3: S2, S2, S3, S3,
  S4) plus the template's offset (0 or −1). Allies have **no heavy blows** (no windups): a heavy blow is an
  adversary's two-turn threat (06.9.5), and an ally's turn is the PC's action.
- **Vitality and armor:** 16.4.3. **Focus and abilities:** 16.4.4. **Size and pace:** the template's
  (06.3.10; 06.3.3).
- **Tempo:** none — an ally has no place in the order (06.14.1).
Base modifiers are therefore exactly 09's: a trained `high` attack is +2 / +5 / +7 / +10 / +12 at bands
1–5, a Guard of 12 / 15 / 17 / 20 / 22 — always a band below the PC who leads it (16.2.4), so always
below the PC's own line (T-06-12: +5 / +7 / +9 / +11 / +12, Guard 14–20) [09.3.2; DL-16-04].

**16.4.3 Companion Vitality and armor.** `[D]` (T-16-4; `data/companions.yaml#line_by_band`)

**T-16-4 The companion line by serving band** (a `high` attack and Guard; Vitality for a medium-sized ally).

| Serving band | Attack (high + c_b) | Guard (high Agility) | Vitality (medium) | Standard harm | Reduction (worn, typical) | Focus (casters +1) |
|---|---|---|---|---|---|---|
| 1 | +2 | 12 | **6** | S2 (3) | 0–1 | 0 |
| 2 | +5 | 15 | 12 | S2 (3) | 1–2 | 1 |
| 3 | +7 | 17 | **16** | S3 (5) | 2 | 2 |
| 4 | +10 | 20 | **18** | S3 (5) | 2–3 | 3 |
| 5 | +12 | 22 | 20 | S4 (8) | 3 | 4 (never serves: no PC is P6) |

- **Vitality** is the **lower** of chapter 09's standard Vitality for the band (T-09-3: 5 / 12 / 18 / 24 /
  36) and the PC reference Vitality of the band (T-06-12 with DL-00-04: 12 / 14 / 16 / 18 / 20), except that
  band 1 is **6**, not 5. Two reasons. *The heavy blow:* an S3 strike deals 5, so a band-1 ally at 5
  Vitality falls to the first heavy blow of any band-1 bandit, while at 6 it survives one, which is what a
  porter beside a novice needs to be a person rather than a decoration (the adversary envelope of 00.3.7,
  T1 2–5, governs adversaries; chapter 07 makes allies' Vitality this chapter's, 07.12.1). *The hero:* at
  bands 3–5 an adversary's standard Vitality exceeds the PC's own (adversaries are built to be beaten by a
  PC's damage), and an ally with more staying power than the hero who leads it would out-power the hero on
  the one axis that decides who falls first; the validator caught it (`16-gen_data16.py`), so the line
  takes the PC's figure for the band, which is always below the Vitality of any PC who can lead it
  (16.2.4: a band-*b* ally is led by a PC of band *b* + 1 or more) [DL-16-04].
- **The clamp.** Whatever its size or template, an ally's maximum Vitality is at most the leading PC's
  maximum Vitality − 1 (a large bonded bear is as tough as an ally can be, and no tougher than its
  master).
- **Size:** tiny ×½ (minimum 3; a familiar, a hawk), small ×¾ rounded down, medium ×1, large ×1.5 rounded
  down (a horse, a bear), huge ×2 — then the clamp above.
- **Armor:** worn armor by the template's gear (padded or leather 1, mail 2, plate 3; 08's rungs) or 09's
  natural armor table for beasts (09.3.6); total reduction capped at 4 (07.2.2). Armor given by the PC
  replaces the template's (16.4.8).
- **Recovery:** allies recover Vitality and heal their one wound as PCs do (07.12.2).

**16.4.4 Focus and abilities.** `[D]` An ally's **Focus** is chapter 09's adversary base by serving band
(0 / 1 / 2 / 3 / 4) plus 1 for a template whose `role` is `caster`; it is refilled at each `rest_long` and
at no other time (05's channels are the PC's). An ally holds **at most three abilities** (`ab.*` from
chapter 05's pool, at rank 1 unless 16.10.4 says otherwise), listed by the template or earned as a protégé;
each costs its own Focus from the ally's pool when the PC commands it (06.14.2: "any verb or ability it
could attempt alone"). Reaction abilities (`ab.interpose`, `ab.shield_block`) compete for the ally's one
reaction (06.14.4). Abilities that dictate another's choices or summon further beings cannot be held by an
ally (`dictates_choice: true` or op `create`): a follower never brings its own followers [INV-11; 03's
request on `dictates_choice`].

**16.4.5 Base modifiers for group actions and Help.** `[D]` Chapter 01 asked for these (01.14.7–01.14.8).
An ally's **base modifier** on a beat is `rung(attribute) + competence + edge`, exactly 00.3.5's base for
anyone; its competence is `c_b` when the beat's primary deed tag or an ancestor is one of its trained tags,
and 0 otherwise. T-16-5 is the lookup for the common cases; the engine computes the rest.

**T-16-5 Ally base modifiers by serving band** (`data/companions.yaml#base_modifiers`).

| Attribute rung → | apex, trained | high, trained | mid, trained | high, untrained | mid, untrained | low, untrained |
|---|---|---|---|---|---|---|
| band 1 | +4 | +2 | +1 | +1 | 0 | −1 |
| band 2 | +7 | +5 | +3 | +3 | +1 | −1 |
| band 3 | +9 | +7 | +5 | +4 | +2 | 0 |
| band 4 | +12 | +10 | +7 | +6 | +3 | +1 |

- **Group actions** (01.14.7): an ally is a member like any other; "all must" uses the **lowest** base
  modifier in the group, "any may" the **highest**. A band-1 porter sneaking with the PC sets the party's
  Sneak at his 0 (mid Agility, untrained): bringing people has a price.
- **Help** (01.14.8): an ally is eligible when it could attempt the helped beat alone (it holds any needed
  license — its knacks are its licenses — is in position, and no condition forbids it). In conflict the
  Help is bought with a Command (06.14.2); outside conflict it costs the ally's time in the same time unit
  as the helped beat (16.8.2). One Help lever per beat, however many helpers.
- **The PC's ceiling.** An ally's base modifier on any beat is clamped to the PC's band floor of 00.3.7
  (P1 +4, P2 +6, P3 +8, P4 +10, P5 +12). With the band cap this almost never binds (only an apex-trained
  band-4 ally under a P5 PC reaches +12); it is stated so that no item or knack can make a follower the
  better hand at the hero's own trade [16.2.4; DL-16-04].

**16.4.6 Never out-power the hero: the check.** `[D]` At every line build the engine verifies, and logs a
`rule_conflict` ruling if any fails (it then clamps): the ally's serving band ≤ `band_cap(pc)`; every base
modifier ≤ the PC's band floor (16.4.5); its maximum Vitality < the PC's maximum Vitality; its harm per
blow ≤ the PC's Strike base severity (T-06-12) — the last always holds at the band below. This is the
mechanical form of "a companion never out-powers the PC's band" [00.17.1 Q8].

**16.4.7 Knacks: a small closed set.** `[D]` A **knack** (`kn.*`, T-16-6, `data/companions.yaml#knacks`) is
one of fifteen closed capabilities an ally may have. An ally holds **at most three**: its template's
(`knacks`, zero to two), plus at most one gained by training (16.10.2), plus its template's
`signature_knack` once its personal thread is complete (16.12.3), never more than three in all — a fourth
replaces one, chosen by the player (VI: replace, never stack). A knack is either a **training license**
(the ally may attempt what the license's scope allows, at grade `trained`, `expert` from serving band 3)
or a **bundle of core effects**; none adds an action (INV-11).

**T-16-6 Knacks.**

| Id | Name | What it is (literal scope) | Built from |
|---|---|---|---|
| `kn.trained` | Trained hand | holds the one or two training licenses (`lic.training.*`) its template or its training names, at grade trained (expert from serving band 3) | `grant_license` |
| `kn.shieldbearer` | Shieldbearer | while under the order *guard me* and in the PC's group, the PC has +1 Guard edge | `eff.defense_edge` (amount 1, applies_when the ally is in the PC's group under guard_me) |
| `kn.steadfast` | Steadfast | does not take the automatic *stay back* of 16.7.4 (losing heart) at any standing | flag read by 16.7.4 |
| `kn.healer` | Healer | holds `lic.training.lore_medicine` (trained) and carries a healer's kit (three uses a week, refilled in a settlement at 08's price) | `grant_license` + item |
| `kn.keen_nose` | Keen nose | its Observe beats to track or find by scent, and its Help on the PC's, hold a Precision lever | `eff.grant_lever` (precision, for verb.observe, applies_when tracking or finding by scent) |
| `kn.keen_eyes` | Keen eyes | as lookout (10.5.1) an arrival is seen one band farther again; its Observe beats to spot at distance hold a Precision lever | `eff.grant_lever`; role extension |
| `kn.sentinel` | Sentinel | in camp, sleepers are never `unaware` at an arrival (it wakes them, 10.5.2), even when no one keeps watch | `eff.write_fact` (`camp.alarm` while it is in the camp) |
| `kn.war_trained` | War-trained | a mount that stays steady in conflict (no Handle beat each round, 16.15.4); a beast of family `beast` that may take the orders *harry that one* and *hold this ground* | flag read by 16.15.4 and T-16-12 |
| `kn.pack_beast` | Pack beast | carries its template's `carry` in load units for the party (08.9); forage-fed on grass (10.8.2) | template carry |
| `kn.quartermaster` | Quartermaster | may hold the journey role *quartermaster* (16.8.4) | role extension |
| `kn.sign_trained` | Signs | `hears: signs` — perceives commands by hand signs within sight (06.14.2 decision 1) | flag |
| `kn.rally` | Rally | once per conflict, when the PC is first Staggered and the ally is Friendly or warmer and conscious within `band.near`, it shouts the PC back to their feet: `cond.frightened` and `cond.broken` end on the PC (no action; a hook) | `eff.cleanse` on `on_vitality_threshold` (the PC's, at 0), `limits {per: conflict_end, uses: 1}` |
| `kn.bodyguard` | Bodyguard | its *guard me* Intercept may be used while it is bloodied; harm it takes from an Intercept is reduced by 1 more (within the cap of 4) | flag + `eff.harm_reduction` (amount 1, applies_when intercepting) |
| `kn.loyal` | Loyal | cannot be bribed, courted or turned by another (11's suborn actions and 16.6.6's betrayal rows do not apply to it while it is Neutral or warmer) | flag (Blades' *Loyal* edge) |
| `kn.forager` | Forager | may hold the *forager* role at normal pace as well as slow (10.5.3: "a license whose scope covers a journey task gives the role at the pace it names") | role extension |

Every knack's effect is a core effect from `data/effects.yaml` with parameters, or a flag a named rule
reads; none restates a mechanic in prose (00.16.4). *Why a closed list of fifteen:* an ally's identity
should be legible in one line ("a soldier: trained blade, shieldbearer"), and the AI should never invent
what a hireling "would be able to do"; growth is a choice among these, not a new menu [C:V; R5 NP-05;
R: https://github.com/amazingrando/blades-in-the-dark-srd-content/blob/main/Blades-in-the-Dark-SRD.md
(expert edges: Independent, Loyal, Tenacious, Fearsome); DL-16-06].

**16.4.8 Gear, gifts and loot.** `[D]` An ally carries its template's kit (`kit`: item tags, 02/08's
format) and anything the PC gives it. Given items work for the ally by 08's rules (edge, reduction, harm
tags, the item sub-cap), with three limits: an ally never uses an item-bound **active** ability (it holds
no equipped partition, 05); a relic license works for an ally only if its text says "any bearer"; and
attunement (08) counts against the PC's limit of five, not the ally's, when the PC attuned it. Loot found
is the PC's; a contract's **share** (veteran half, champion full, 08.8.8) is a share of **coin** found in
ventures the hireling took part in, paid at `venture_end` by `h.16.venture_end`; withholding it ticks
grievance (T-16-8 G5). A companion who delivers a killing blow generates loot as `scavenged` (08's edge
case: the PC's own beat did not defeat it).

### 16.5 Loyalty

**16.5.1 Loyalty is standing.** `[D]` An ally's **loyalty** is its standing toward the PC on chapter 15's
scale (−3 Hostile … +3 Devoted; 00.17.1 Q8; 15.1.1). Everything chapter 15 says about standing holds for an
ally: its starting value (15.1.4: a hireling's reaction roll; a bond's set value; a follower's Friendly by
16.3.6), its behavior contract for social play (T-15-1), its movement by 15.1.5's listed sources (a
rescue, a broken promise, a gift, an intimidation, a deed it witnessed through 12's memories) and 15.1.7's
caps. This chapter adds three things, all `[D]`: a **companion contract** per rung saying what the ally
will and will not do as a follower (T-16-7); **two clocks** that turn the many small things a follower sees
into rare standing steps (16.5.3); and the **breaking points** where loyalty runs out (16.6). The two
clocks are a new standing source for allies only, filed as an amendment to 15.1.5 (Interface requests):
*source 8 — an ally's regard or grievance clock completing (16.5.3)*.

**16.5.2 The companion contract per rung.** `[D]` Each rung is a contract the ally keeps whatever the
narrator's mood (15.1.2's principle, extended to following). The stakes column is the WILL test chapter
06 delegates to this chapter (06.14.2 decision 2): a commanded beat is **obeyed** when its frame's stakes
are within the larger of the rung's acceptance and the contract's (16.7.2), and it does not cross its refusal.

**T-16-7 The companion contract** (`data/companions.yaml#loyalty_contract`).

| Rung | Accepts commanded beats up to | *guard me* (Intercept) | Uncommanded, it… | Outside conflict | Unpaid / unfed | Leaves when |
|---|---|---|---|---|---|---|
| +3 Devoted | **lethal** frames | yes, even bloodied; and it may Intercept for the PC with **no order** (its reaction) | keeps its order; reaches the PC if the PC is Dying (its order's movement, 16.7.5) | does anything its refusal allows, unasked if the PC is in danger; follows into captivity | serves on; no grievance for 4 weeks | never by loyalty; only its own death, the PC's dismissal, or its want's end (16.6.1) |
| +2 Friendly | **lethal** frames | yes, while not bloodied (bloodied with `kn.bodyguard`) | keeps its order | any request its refusal allows (15's ceiling R4) | no grievance for 2 weeks | — |
| +1 Warm | Dire, not lethal | yes, while not bloodied | keeps its order | requests to R3; its duty | grievance from the first week | — |
| 0 Neutral | Risky | **no** (unless its contract's duty is to guard the PC) | keeps its order | its duty and requests to R2 (15.4.6) | grievance from the first week; a hireling unpaid two weeks leaves (16.14.5) | — |
| −1 Wary | Safe (and Defend, Withdraw, *stay back*, whatever the stakes) | no | takes *stay back* | its duty at Safe only | leaves | its **departure clock** completes (16.6.2) |
| −2 Unfriendly | nothing but Withdraw and *stay back* | no | takes *stay back*, Withdraws at its first chance | nothing | — | at the next `scene_end` not in danger, announced (16.6.3) |
| −3 Hostile | nothing | no | Withdraws, and may act against the PC only through 16.6.6 | nothing | — | at once; or **betrays** if 16.6.6's conditions hold |

A hireling's **contract** adds acceptance by its hazard rung (16.3.3): R1–R2 → Risky; R3 → Dire, not
lethal; R4 → lethal; R5 → lethal. A Neutral soldier hired at R4 for the barrow obeys lethal commands — he
was paid for them — while a Neutral one hired at R2 for the road does not. A **follower**'s oath adds
acceptance up to lethal while it stands at Warm or better (it swore to). *Why this shape:* old-school
loyalty and morale ask "will they stand?" with a roll; Mausritter's hirelings flee when asked to do more
than they signed for [R: https://loottheroom.uk/the-long-read-mausritter]; Blades' cohorts and
Darkest Dungeon's stressed heroes refuse or act out. Here the same question is answered by a lookup the
player can see before committing (the OFFER names a refusal before any action is spent, 06.14.2) — the
AI-reliable form of morale [R4 W4; DL-16-07].

**16.5.3 Regard and grievance: two clocks.** `[D]` + `[T]` Every ally of kinds hireling, companion,
follower, cohort and beast holds two clocks of 00.8's primitive, created when it joins:

| Clock | Kind | Segments | Visibility | Ticks from | Decays | On completion |
|---|---|---|---|---|---|---|
| `clk.16.regard.<id>` "<Name>'s regard" | progress | 6 | **sensed** (omens every tick, INV-14) | T-16-8 regard sources | never | standing **+1**, never above **Friendly** (Devoted comes only from deeds of weight, 16.5.10); reset to 0; a **regard moment** (16.5.8) |
| `clk.16.grievance.<id>` "<Name>'s grievance" | danger | 6 | **sensed** | T-16-8 grievance sources | −1 at each `week` boundary with no grievance tick that week | standing **−1**; reset to 0; a **confrontation** (16.5.9) |

The two are independent: an ally may at once admire the PC's courage and resent their cruelty, and both
can complete. Completions are this chapter's standing source (16.5.1). Regard completions count against
15.1.7's weekly cap of **+1 per NPC per week from small sources** unless the cycle held a ★ source (R3: a
hard or lethal fight survived together, the one regard source that is a shared deed rather than a
kindness); a capped completion waits at 5 of 6 for the next week. Grievance completions are uncapped, as
every negative step is in 15.1.7.
*Why six segments.* `16-loyalty-sim.py` (T-16-22) plays an ally through 24 sessions at five scenes a session
against three kinds of PC. A PC whose deeds match the ally's values moves it Neutral → Warm in a median of
**3** sessions and to Friendly by session 6 in 89% of runs; an indifferent PC (deeds on its axes both ways,
fair pay, shared roads) reaches Warm by session 6 in 68% and Friendly by session 12 in 57%; a PC whose
deeds affront its values drives it to Wary or worse by session 6 in 83% of runs and loses it (departure)
in every run by session 24. That is the intended shape: slow enough that a single bad day never ends a
friendship (one event is one tick of six), fast enough that a campaign of cruelty in front of a merciful
companion ends the following within two weeks of play [R: https://bg3.wiki/wiki/Approval (approval
accrues from many small reactions and is warned before it breaks); DL-16-08].

**16.5.4 The tick sources (closed).** `[D]` + `[J:flag]` Only these tick an ally's regard or grievance
clock (`data/companions.yaml#loyalty_sources`). The DM decides only *whether* a listed source fired, citing
the event, frame or fact id (00.8.2); the amount is the table's. A posted ally (16.2.3) or one not present
ticks only from sources marked "absent too".

**T-16-8 Regard and grievance sources.**

| Id | Source (true only when…) | Clock | Ticks | Cap |
|---|---|---|---|---|
| R1 | **Value honored:** an evidence event (03) on one of the ally's value axes with the sign of its pole, whose `witnesses` include the ally | regard | +1 | once per axis per scene |
| R2 | **Want served:** a resolved deed of the PC serves the ally's recorded want, by 15.3.5's Want test (a want id cited) | regard | +2 | once per want per season |
| R3 ★ | **Shared danger** (★: exempt from 15.1.7's weekly cap): the ally was a participant in a conflict whose advisory was hard or lethal (09.6), on the PC's side, and both were still on their feet or stabilized at `conflict_end` | regard | +1 | once per scene |
| R4 | **Generosity:** coin, goods or a share beyond what is owed, worth at least 1 Unit of the ally's weekly lifestyle (T-15-19 by role) | regard | +1 | once per week (absent too) |
| R5 | **The road together:** at `venture_end`, the ally took part in the whole venture and it held at least one conflict or one day of want | regard | +1 | once per venture |
| R6 | **Counsel heeded:** the ally voiced an objection (16.5.7) and the PC withdrew or changed the declaration | regard | +1 | once per scene |
| R7 | **Its thread advanced:** a resolved beat ticked the progress clock of the ally's personal thread (16.12) | regard | +1 | once per scene |
| G1 | **Value affronted:** an evidence event on one of the ally's value axes against its pole, witnessed by the ally | grievance | +1; **+2** when the ally itself was commanded to do it | once per axis per scene |
| G2 | **Refusal forced:** the ally was made to act against its refusal by leverage or intimidation (15.3.5, 15.4.3) | grievance | +3 | — |
| G3 | **Danger beyond the bargain:** at `scene_end`, the ally faced stakes above its contract's hazard and its rung's acceptance (T-16-7), because the PC brought it there | grievance | +1 | once per scene |
| G4 | **Unpaid:** at the `week` boundary a wage or keep due was not paid (16.14.5) | grievance | +1 (hireling +2) | once per week (absent too) |
| G5 | **Share withheld:** a contract share due at `venture_end` was not paid | grievance | +2 | once per venture |
| G6 | **Deceived about the work:** the PC lied about the job or the danger (15.5), and the lie was exposed to the ally | grievance | +2 | once per lie |
| G7 | **Left to fall:** the ally was Down or bleeding out in a conflict and was not tended or carried out by the PC or on the PC's command before `scene_end` (07.12) | grievance | +1; **+3** if it was left among enemies and later returns (07.12.3) | once per scene |
| G8 | **Neglect:** in the past day the ally went without food (10.6.2 `went_without`) or without a long rest for two days (07.8.10) while the PC did not | grievance | +1 | once per day |
| G9 | **Friction:** another member of the retinue toward whom the ally stands Unfriendly or worse (15.1.8) stayed in the retinue all week; or a cohort's named leader stands Wary or worse | grievance | +1 | once per week |
| G10 | **A fellow's death:** another ally died after being commanded into a lethal frame or left behind, and this ally witnessed it | grievance | +1 | once per death |

```
### 16.5.4  Did a loyalty source fire?                               [J:flag] [D]
Trigger [T]:        RECORD of any beat or event a present ally witnessed (an evidence event with the
                    ally in `witnesses`; a frame; a pay, supply or rest boundary; a conflict_end)
Loads in:           core while an ally is present; situation.downtime.* for pay sources
License check:      —
Decisions (J):      1. FIRED [J:flag] per row of T-16-8 whose trigger family matches the event: "Does
                       this event meet the row's 'true only when' with a cited id?" True only with the
                       evidence event's axis and sign (R1/G1), the want id (R2), the advisory word on the
                       conflict record (R3), the coin moved (R4), the venture record (R5), the objection
                       and the changed declaration (R6), the thread clock tick (R7), the leverage or
                       intimidation frame (G2), the contract hazard and the frame stakes (G3), the
                       missed upkeep write (G4/G5), the exposed lie (G6), the harm-state record (G7),
                       the went_without fact (G8), the standing records (G9), the death record (G10).
                       False when the only basis is the narration's tone ("she looked unhappy").
                       Uncertain -> false (SG-05: grants and losses both need a cited id).
Computation [D]:    tick_clock(clk.16.regard|grievance.<ally>, n) per the row, within the row's cap;
                    the omen of the clock's stage is selected and must be rendered this turn (16.5.8)
State writes:       clock ticks and history; omen key; drives.known_to_pc for R1/G1's axis
Narration may not imply: a feeling larger than one omen; a standing change before a clock completes
Worst case (J):     one source wrongly judged to fire: 1-3 ticks on one clock (class i), auditable by
                    the cited id; a standing step needs six ticks, so a single error never moves loyalty.
Examples:           inside R1: Wren spares the fleeing bandit (conduct.mercy +1, 03) in front of Oda,
                      whose value is mercy +1 -> regard +1; the omen: "Oda lets out a breath she was
                      holding." boundary: the same mercy, Oda asleep in the wagon -> not a witness ->
                      nothing (a later telling may move standing by 15's heard-of rule, never this clock).
                    inside G7: Brack bled out at 3/4 and Wren finished the duel first and then
                      stabilized him -> he was tended before scene_end -> G7 does not fire.
                    non-example: "Oda must be impressed by how well I fought" -> fighting well is no
                      value axis; only a cited conduct event, want or listed source ticks the clock.
Anchor:             no
Basis:              [00.8.2] [03.10] [15.1.5] [R: https://bg3.wiki/wiki/Approval] [DL-16-08]
```

**16.5.5 Drives: who this person is.** `[D]` + `[S]` Every ally that is a person (hireling, companion,
follower, cohort) holds **drives**, rolled once when it joins and never chosen (`data/companions.yaml#drives`):
- **Two values**: `tbl.16.drive_values` — d10 for the axis (the ten `conduct` axes in 00.5.1 order: mercy,
  honesty, courage, loyalty, generosity, justice, humility, restraint, piety, protection), d6 for the pole
  (1–5 the positive pole, 6 the negative: most people admire virtue; one in six admires its opposite — the
  sellsword who respects ruthlessness, the courtier who prizes a well-told lie); the second roll rerolls a
  repeated axis. A template may **fix** one value (`fixed_value`: the zealot's piety +1, the sworn
  sword's loyalty +1); a follower's first value is fixed by 16.3.6; a `cunning` creature's first value is
  rolled on `tbl.16.drive_cunning` (d6: greed → generosity −1; fear → courage −1; appetite → restraint −1;
  pride → humility −1; spite → mercy −1; cunning → honesty −1).
- **One want**: its top-ranked want from 12.11.1 (principal) or its single want (recurring).
- **One refusal**: its recorded refusal (12.11.1's `tbl.npc_refusal`, semantics 15.2.3); a person who has none
  rolls one on 12's table at joining. The refusal is the one thing it will not do for the PC at any standing.
Drives are the **only** source of an ally's opinions about the PC's conduct: the narrator voices
approval and disapproval only through omens of ticks those drives produced (16.13.3).

**16.5.6 Learning who they are.** `[D]` Drives are **sealed** when rolled and unseal, each separately
(`known_to_pc: true`, then **available** in the codex), when:
1. a regard or grievance tick on that value's axis is rendered (the omen shows what moved them);
2. a Read (15.6.1) of the ally delivers it (a value counts as one item of the read's delivery, like a want);
3. the PC asks (a Talk request at R2, "what matters to you?"): at Neutral one value, at Warm both values,
   at Friendly both values and the want; the refusal is revealed the first time it refuses or at Friendly when asked;
4. the ally's personal thread opens (16.12.2): its want is known.
*Why:* learning what a companion cares about is the companion game in Dragon Age and Baldur's Gate 3, and
the information must be earned by play, not read off a sheet on day one; but it must also be reachable by
an honest question, because a player who asks should be answered (goal 1) [R: https://bg3.wiki/wiki/Approval].

**16.5.7 Counsel: the warning before the deed.** `[J:flag]` + `[D]`

```
### 16.5.7  Counsel                                                   [J:flag] [D]
Trigger [T]:        OFFER of any PC beat, while an ally of kind companion, follower or hireling (not a
                    beast, bound being or scene ally) is present and conscious
Loads in:           core while an ally is present
License check:      —
Decisions (J):      1. AFFRONT [J:flag] "If this beat succeeds as declared, would it be a deed on one of
                       a present ally's KNOWN-OR-SEALED value axes against its pole, or would it command
                       the ally against its refusal?" True only when the beat's declared intent and method
                       name an act that 03's conduct definitions place on that axis and pole (killing a
                       yielded foe -> mercy -; lying to the reeve -> honesty -) or the command's beat is
                       what its refusal forbids. False for an act whose conduct reading depends on facts not
                       yet established. Uncertain -> false.
Computation [D]:    True -> before the commit, the ally speaks ONE line of counsel in its voice
                    (12.11.3) naming what troubles it, never the mechanic ("If you cut his throat while
                    he kneels, I'm done carrying your pack."); the OFFER marks the objection. If the
                    ally is Friendly or warmer and its refusal would be crossed, the counsel states that it will
                    not help and what it will do (16.7.2). The player commits, changes the method or
                    withdraws (01.7.1). Changing or withdrawing ticks R6 (counsel heeded).
Stakes:             none (counsel is a warning, not a frame)
State writes:       objection record {ally, axis, frame}; R6 on a changed declaration
Narration may not imply: that the ally will act to stop the PC (it may only refuse, object, or leave by
                    16.6); a mechanic; an opinion on an axis it does not hold
Worst case (J):     AFFRONT wrongly false: a grievance tick lands without the warning (one tick of
                    six, class i) -- the omen still renders, so the player learns the axis; wrongly
                    true: an unneeded line of counsel (no state effect).
Examples:           inside: Oda (mercy +1) present; Wren declares "I finish the wounded brigand" ->
                      counsel: "He's done, Wren. Leave him." boundary: Wren declares "I tie him up and
                      leave him for the reeve" -> no affront (restraint, mercy neutral) -> no counsel.
                    non-example: "Brack the hound objects" -> beasts do not counsel; they have
                      temperaments, not values (16.15.3).
Anchor:             no
Basis:              [R: https://bg3.wiki/wiki/Approval] [00.3.14 the telegraph principle] [DL-16-10]
```

Counsel is the telegraph of loyalty, as the lethal warning is the telegraph of death: no ally's grievance
should surprise a player who was paying attention.

**16.5.8 Omens of the two clocks.** `[N]` + `[D]` Every tick renders one omen (INV-14), chosen by the
engine from the ally's clock stage and narrated in the ally's voice and manner (T-16-16,
`data/companions.yaml#loyalty_omens`; the narrator chooses the words, never the stage):

**T-16-16 Loyalty omens (defaults; a template or region may replace them).**

| Clock · stage | Examples (the narrator renders one per tick, as action or speech, never as a number) |
|---|---|
| regard · stirring | a nod; a joke at the PC's expense that is really affection; it shares its water first |
| regard · building | it tells a small story from its past unasked; it uses the PC's name; it takes the worse watch without being asked |
| regard · imminent | it says something it has never said ("I'd follow you a long way"); it gives the PC something of its own |
| regard · complete (the **regard moment**) | a confidence: one of its drives, its want, or a piece of its secret's surroundings is shared (16.5.6 item 3 at the new rung); a chronicle line if it reaches Devoted |
| grievance · stirring | silence where there was talk; a look held a beat too long; it eats apart |
| grievance · building | an open complaint naming the cause ("You didn't pay us, Wren"); it does its duty slowly |
| grievance · imminent | an **ultimatum**: it names the cause and what it will do if it happens again ("Do that once more and I walk") |
| grievance · complete | the **confrontation** (16.5.9) |

**16.5.9 The confrontation.** `[D]` + `[J:flag]` When a grievance clock completes, the ally's standing steps
−1 at once (state is never delayed) and the ally **confronts** the PC at the first scene with no threat
present (`scene_start` with no hostile participant; it waits if there is one). The confrontation is a
social scene the player plays: the ally names the sources that filled the clock (their ids are in its
history; it says them in words: "the bandit you killed on his knees, the week you didn't pay us"). The PC
may answer with **amends**: one beat whose method addresses at least one named source — paying the
arrears (G4/G5: coin moved), releasing the leverage (G2), an Obligation term (15.3.5: "I will not do it
again", written as a promise with the ally), a gift, or plain honest talk. Amends are a **win-over** Talk
(15.4.2) against the ally's Resolve defense at its new standing, with this one exception to 15.1.7: a
successful amends **restores** the step just lost (it may return the ally to the rung it held before the
confrontation, never above). `[J:flag]` *"Does this method address a named source?"* True only when it
cites the source's own fact (the coin owed, the leverage fact, the commitment); false for a speech that
names none. Uncertain → false (then it is an ordinary win-over, capped at Warm). A failed amends leaves the
step; **ignoring** the confrontation (leaving the scene, refusing to answer) ticks grievance +1. A promise
made in amends and later broken is 15's `betrayed` (−3). *Worst case (J):* a method wrongly judged to
address a source restores one step that should not have been restored (class i, and only once per
confrontation). *Why a confrontation:* Dragon Age and Mass Effect companions raise their objections in a
scene where the player can answer; a loyalty drop that is only a number teaches nothing [DL-16-10].

**16.5.10 Devotion.** `[D]` An ally reaches **Devoted** only by: a deed of weight from 15.1.7 (a rescue, a
sparing, a kept R4+ promise, an R4+ help — 15's sources; for an ally, being saved from bleeding out or from
captivity is the commonest, 16.9.4); the completion of its personal thread (16.12.3); or a creation bond
(02.9.2). Regard clocks alone stop at Friendly. Devotion is what a follower may become, never what one
starts as, and the simulation shows why the clocks must not reach it: with them uncapped, an aligned PC's
companion was Devoted by session 12 in 93% of runs, which makes the top rung a matter of time rather than
of a deed [T-16-22; DL-16-08].

**16.5.11 Allies toward one another.** `[D]` Allies hold standing toward each other (15.1.8): rolled by the
reaction roll at their first scene together (12.11.2 step 2, no modifiers), moved by 15's sources between
them (one saved the other: rescue; one stole from the other: harmed). Friction between allies is a
grievance source (G9), and a pair at Friendly or warmer toward each other gives each a regard +1 the first
time they share a ★ conflict (they fought well together). This is Mount & Blade's companion likes and
dislikes, made deterministic [R: https://steamcommunity.com/app/48700/discussions/0/535150948595822006/].

### 16.6 Breaking points: departure, dismissal and betrayal

**16.6.1 Why allies leave (closed).** `[D]` An ally stops following for exactly one of these causes
(T-16-18; `data/companions.yaml#departure_causes`), each with its own writes. Nothing else ends a following:
not the DM's sense that "she would have had enough by now".

**T-16-18 Departure causes.**

| Cause | When | What happens | Rule |
|---|---|---|---|
| `dismissed` | the PC lets the ally go (free activity) | arrears and shares due are paid or become a debt commitment; 16.6.4 | 16.6.4 |
| `contract_end` | a hireling's term ends and is not renewed | paid off at the next haven; 16.14.4 | 16.14.4 |
| `unpaid` | a hireling went two `week` boundaries unpaid | leaves at once, with a debt the PC owes (15's `owed`) | 16.14.5 |
| `loyalty_wary` | its departure clock completes | leaves at the next `scene_end` not in danger, announced | 16.6.2 |
| `loyalty_unfriendly` | its standing reaches Unfriendly | announces at once; leaves at the next `scene_end` not in danger | 16.6.3 |
| `loyalty_hostile` | its standing reaches Hostile | leaves at once, or betrays if 16.6.6 holds | 16.6.6 |
| `want_fulfilled` | the want it joined for is fulfilled, and it stands Warm or below | leaves content at the next haven; a friend left behind | 16.6.5 |
| `overflow` | the retinue is over the cap at a `week` boundary (16.2.1) | the most recently joined ally below Friendly leaves, announced the day before | 16.2.1 |
| `death` | 07.12's clock completes, or any death | 16.9.5 | 16.9 |
| `working_ended` | a bound being's working ends (05) | it ends as the working says (16.15.6) | 16.15.6 |
| `pc_retired` | the PC retires or dies (11's legacy) | 16.16 | 16.16 |
Captivity and being lost (07.12.3) are **not** departures: the ally is missing, keeps its retinue place
(the PC may free the place only by dismissing it in absence, which is `dismissed` with 15's `betrayed` if
it is later rescued and learns of it), and a rescue lead is written.

**16.6.2 The departure clock.** `[D]` + `[T]` When an ally's standing becomes **Wary**, the engine creates
`clk.16.departure.<id>` "<Name> means to leave": kind countdown, **4** segments, **public** (the player sees
it, and the ally says it plainly: "When we reach a town, I'm done"), `auto_ticks` +1 at each `day`
boundary, tick source +1 for each grievance tick. It is **voided** the moment the ally's standing returns
to Neutral or warmer. On completion the ally departs (cause `loyalty_wary`) at the next `scene_end` that is
not in danger (no hostile participant present; not in a site's active area; or at once if the PC is in a
haven). *Why four days:* enough time to make amends in play (a gift, an honest word, a want served, a
debt paid: four days is four chances at 15's small sources and any number at its deeds of weight), short
enough that a player who ignores it loses the ally inside a venture. Together with the grievance clock's
ultimatum omen (T-16-16) and the confrontation (16.5.9), the player is warned **three times** before a
loyal ally walks: Baldur's Gate 3 warns twice [R: https://bg3.wiki/wiki/Approval; DL-16-11].

**16.6.3 Unfriendly: leaving now.** `[D]` An ally reaching **Unfriendly** says it is leaving, in its voice,
the moment the step is written, and departs at the next `scene_end` not in danger (cause
`loyalty_unfriendly`). Until then it obeys only Withdraw and *stay back* (T-16-7). It takes what it wears
and its own kit; it hands back party goods it carries (supply, the PC's packs, items lent to carry) unless
it is owed wages, in which case it keeps goods worth the arrears (an engine choice by price among non-relic
items it carries) and says so. A beast that reaches Unfriendly runs off at the next night watch.

**16.6.4 Dismissal.** `[D]` + `[J:flag]` The PC may let any ally go at any time (free activity, no roll).
The engine settles: wages and shares due are paid now or written as a debt commitment to the ally
(15.7.6; unpaid later → `betrayed`); items lent are returned; the ally leaves with a memory of the parting.
`[J:flag]` *"Is the ally being left somewhere it cannot safely get home from (the wild, a site, among
enemies)?"* True only when the place's danger rating (10) is wild or worse, or a hostile participant is
present. True → the memory `harmed` (S2: −1) and, if it survives to be met again, it remembers. False → no
standing change. Uncertain → false. *Worst case (J):* one standing step on a departed NPC (class i).
A dismissed ally remains a recurring or principal NPC at its standing (`exists: departed` is not used: it
simply leaves the retinue and `ally_kind` becomes null), with its memories, its thread (now an ordinary
NPC's want), and its knowledge of the PC — which it may tell (it is a carrier, 03.10.2).

**16.6.5 A want fulfilled.** `[D]` When the want an ally joined for (`joining.kind: want`) is fulfilled —
its thread completed (16.12.3) or the want's fact written true — the ally's choice follows its standing:
- **Warm or below:** it leaves content at the next haven (cause `want_fulfilled`), with a `helped` memory
  and a chronicle line; it is a friend left behind, often a contact (15) and a later source of hooks.
- **Friendly or Devoted:** it stays; its joining becomes `{kind: bond}`; a new want is rolled on 12's
  tables (its story goes on with the PC's).

**16.6.6 Betrayal.** `[T]` + `[D]` + `[J:enum]` An ally betrays the PC only when **all** of these hold:
1. its standing is **Hostile**;
2. its grievance clock's **imminent** omen (the ultimatum) was rendered to the PC at least once since it
   joined (the record is in the clock's history);
3. it does not hold `kn.loyal`;
4. an **opportunity** of `tbl.16.betrayal` exists as a fact: valuables in its reach, a secret of the PC's
   it knows (a knowledge record, 15.9.17), a faction courting it (11's suborn action wrote
   `courted_by`), a crime of the PC's it witnessed, the PC asleep with it on watch, or a conflict in which
   its withdrawal leaves the PC alone.
Then, at the opportunity's moment (`trg.16.betrayal`), the engine rolls `tbl.16.betrayal` (d6, restricted to
the rows whose opportunity holds; `[J:enum]` only to match the fact to the row's opportunity kind, citing
the fact id):

**T-16-11 Betrayal** (`data/companions.yaml#tbl.16.betrayal`).

| d6 | Opportunity | Betrayal | Writes |
|---|---|---|---|
| 1 | valuables in its reach | it steals the most valuable non-relic item it can carry (engine choice by price) and leaves by night | item moved; `stolen_by`; a thread to recover it (11) |
| 2 | a secret it knows | it sells the secret to whoever would pay most for it (a faction or NPC with a want it serves) | `record_knowledge(buyer, secret, how: told)`; 11's attention or notice clock +U(S2) |
| 3 | a faction courting it | it joins them, taking what it knows of the PC's plans and haunts | it becomes the faction's member at Friendly toward them; a recurring foe with its memories (09.9.3's victor-remembers shape, applied to a rival) |
| 4 | a crime it witnessed | it informs the authority of the place | 15/11's `wanted` fact for the PC in that scope |
| 5 | on watch while the PC sleeps | it leaves its watch and slips away: the camp counts as having no lookout that night | the lookout role vacated; the PC is `unaware` at any arrival (10.5.2) — 10's arrival rules and every lethal key still apply |
| 6 | a conflict where its leaving matters | it Withdraws and leaves the fight and the PC | advisory recomputed (09.6.5); a chronicle line |
A betrayal **never** harms the PC directly, never makes any frame lethal, and never bypasses 07's keys: it
changes the situation, as a twist (12) does, after the player was warned. *Worst case (J):* the fact
matched to the wrong row — a different betrayal of the same weight, each a situation change (class iv:
recoverable by the thread it writes). *Why so many conditions:* betrayal is the most memorable thing a
companion can do, and the least forgivable thing an AI can improvise; this chapter makes it earned,
warned, and drawn from what the companion actually had in reach [R6 C (telegraph before loss); DL-16-12].

**16.6.7 Coming back.** `[D]` A departed ally remains in the world at its standing with its memories. It
may be re-recruited by 16.3 (its old drives kept; a fresh reaction roll is never made), met as a contact,
or — if it left Hostile or betrayed — met again as a rival whose memories make it dangerous (11). A
companion who left content (16.6.5) is a standing **successor candidate** (16.16.1).

### 16.7 Allies in conflict

**16.7.1 What chapter 06 fixes.** `[D]` (restated so this card stands alone; 06.14 is canonical) An ally in a
conflict has **0 actions** and **1 reaction** a round, its own position, defenses, Vitality and
conditions, and no place in the tempo order (06.1.1). It acts in exactly three ways (06.14.1): when the PC
spends an action to **Command** it (06.14.2: 1 PC action buys one companion beat; 2 for a beat that costs 2;
the PC must be heard — within `band.near` by voice, or in sight by signs); by its **reaction** (Fend, or
what its **standing order** names: *guard me*, *hold him*, *harry that one*, *hold this ground*, *stay
back*, 06.14.4); and by **hooks and passives** its template lists (knacks with a hook; an aura). Uncommanded,
it keeps its place, its hold and its order, and defends itself. This chapter decides only what 06 left to
it: the ally's **will** (16.7.2), its **default order** (16.7.3), when it **loses heart** (16.7.4), what each
**kind** may be commanded to do (16.7.6), and how allies change the **advisory** (16.7.11) [00.17.1 Q8;
INV-11].

**16.7.2 Will: will it obey?** `[D]` The WILL test of 06.14.2 decision 2. A commanded beat or order is
**obeyed** when all four hold, and **refused** otherwise — the refusal announced, in the ally's voice,
before the PC's action is spent (06.14.2):
1. **Capability:** the beat gates G1 or G2 for the **ally** (its verbs, its knacks' licenses, its
   abilities; 00.12.3). An unlicensed beat is offered as the license's crude fallback (G3), like anyone's.
2. **Stakes within acceptance:** the beat's framed stakes are no higher than the **largest** of: its
   rung's acceptance (T-16-7: Devoted and Friendly lethal; Warm Dire; Neutral Risky; Wary Safe;
   Unfriendly and Hostile nothing but Withdraw and *stay back*), its contract's hazard (R1–R2 Risky; R3
   Dire; R4–R5 lethal), and its oath (a follower at Warm or better: lethal). A frame is "lethal" for the
   ally when its stakes are Dire **and** `lethal` is true **for the ally** (a lethal context recorded for
   the foe it would face, 07.3).
3. **Not against its refusal:** the beat is not what its recorded refusal forbids.
4. **An allowed order:** a standing order is one its template allows (T-16-12).
Defend, Withdraw and *stay back* are always obeyed by anyone conscious who can hear. A refused command
costs nothing; the player may command something else, or try to make the ally obey by Talk (a request at
the beat's size; intimidation or leverage succeeds at the price of G2 if the beat crossed its refusal).
*Worst case:* none — every input is state (a wrong value is a data error, caught by the OFFER, which
shows the refusal and its reason before commitment).

**16.7.3 Default orders: what they do when not told.** `[D]` + `[T]` Handler `h.16.conflict_orders`
(`conflict_start`, phase 9, after `h.06.tempo_setup`) gives every ally present its template's
`default_order` (T-16-12), with no action spent, adjusted by loyalty: an ally whose rung refuses the default
(*guard me* at Neutral or below; anything but *stay back* at Wary or below) takes its template's
`fallback_order` instead (*stay back* for almost all). The player may change any order at any time by Command (06.14.4).
This is the fixed default behavior: a hireling archer starts the fight staying back with its bow; a
soldier starts guarding the PC; a porter stays back; a war-hound harries the nearest foe.

**T-16-12 Orders by template family** (canonical per template in `data/companions.yaml#templates[].orders`).

| Family | Default order | Fallback | Orders allowed |
|---|---|---|---|
| fighters (soldier, sworn sword, veteran, champion, militia, cohort of spears) | *guard me* | *stay back* | all five |
| shooters (archer, cohort of bows) | *stay back* (and shoot when commanded) | *stay back* | *stay back*, *hold this ground*, *guard me* |
| skirmishers (scout, thief) | *stay back* | *stay back* | *stay back*, *harry that one*, *hold this ground* |
| non-combatants (porter, guide, camp hand, healer, sage, minstrel, apprentice, scholar, boatman) | *stay back* | *stay back* | *stay back*, *guard me* (a healer, to keep close) |
| casters (hedge-witch, acolyte, journeyman mage) | *stay back* | *stay back* | *stay back*, *guard me* |
| hounds and war beasts (family `war_beast`: hound, war hound, bonded wolf and bear) | *harry that one* (the nearest foe) | *stay back* | all five |
| other beasts (family `beast`: hawk, familiar) | *stay back* | *stay back* | *stay back* (a hawk may *harry that one* from the air); *harry that one* and *hold this ground* with `kn.war_trained` |
| mounts | carry the rider (06.15.1) | — | none of the five: a mount acts as part of its rider |
| bound beings | as the working's text (05); else *guard me* | *stay back* | all five, unless the working forbids |

**16.7.4 Losing heart.** `[T]` + `[D]` An ally at **Neutral or below** without `kn.steadfast` takes *stay back*
at once (no action; `eff.16.set_order`) the first time in a conflict that any of these happens: it is first
bloodied; another ally falls (Down, bleeding out or dead) within its sight; the PC is Staggered. An ally
at **Warm** loses heart only when the PC is Staggered. **Friendly** and **Devoted** allies never lose heart.
A **cohort** at Neutral or below loses heart when its pool first falls to half. A heartened ally
(`cond.heartened`, 06) ignores this rule while heartened. A Command restores any order (1 action); that
action is the price of fear. *Why:* old-school morale asks hirelings to check when things go badly; this is
the same moment made into a lookup on state the player can see, and it is the reason warm companions are
worth more than paid ones [R: https://oldschoolessentials.necroticgnome.com/srd/index.php/Retainers
(loyalty in the face of danger); R: https://loottheroom.uk/the-long-read-mausritter (morale saves under
stress); DL-16-07].

**16.7.5 To the fallen hero.** `[T]` + `[D]` When the PC enters Dying (07), every **Devoted** ally, and every
**Friendly** ally under *guard me*, takes *guard me* at once (no action) and its order's movement brings it
toward the PC's group one band a round (06.14.4: bounded, free, and adding no beat). There, it Intercepts
by its reaction (Devoted: even with no order; T-16-7). It does **not** stabilize the PC unless commanded:
first aid is a beat, and a Dying PC still has its one action (07's edge case) to command it. This is R6's
"Dying creates an explicit rescue objective for companions" inside INV-11 [R6 C-R2].

**16.7.6 What each kind may be commanded to do.** `[D]` (T-16-13; `data/companions.yaml#command_scope`)

**T-16-13 Commanded beats by kind.**

| Kind | May be commanded to | May not |
|---|---|---|
| person (hireling, companion, follower) | any basic verb (00.12.5) its refusal allows; any beat its knacks' licenses cover; its abilities; Help and Setup (01.14.8–01.14.9); Flank and Screen (06.3.5); first aid (`verb.handle`, stabilize only, unless `kn.healer`: Treat, 07.8.8); carry a fallen body (06's T-06-9 row 38) | anything its WILL refuses (16.7.2); anything needing a license it lacks (G3, crude fallback offered) |
| cohort | Strike, Grapple (holds one foe), Force, Move, Defend, Screen, Help, carry the fallen | Sneak (unless every member could, and then as a group "all must", 01.14.7), Talk beyond a shout, fine work (any licensed craft or lore) |
| beast | Strike (its natural attacks), Grapple (a hold), Move, Setup (bark, harass, flush, swoop: a `distracted` or `off_balance` fact), Help on Strike, Grapple or Observe (by scent or sight), carry (large beasts) | Talk, Handle, Recall, any license; Help on anything else |
| mount (06.15) | its rider's Move; one attack when commanded (a kick, a bite: the mount's own) | anything else in conflict |
| bound being | what its working's text allows (05), and otherwise as a beast | anything the working excludes |
| scene ally under the PC's lead | as a person of its template, within its standing's acceptance (T-16-7 by its standing) | as a person |

**16.7.7 An ally's check: who rolls, with what.** `[D]` The engine rolls every ally beat (00.3.2; the PC
decides, the engine rolls). The commanded beat is framed with the **ally's** numbers: its attribute by the
method, its competence (`c_b` on a trained tag or ancestor, else 0), its edge (gear, knacks), circumstance
(levers and snags citing facts — the PC's Setup facts serve "the actor or an ally", 01.14.9, so a PC's
feint can be cashed by a hireling's spear), and its status (its conditions). DCs are the target's, as for
anyone. The frame is shown to the player as an OFFER (it is the player's declaration, 06.14.2) and resolved
through the whole pipeline with the ally as actor; its costs land on the ally (07 applies harm). Repetition:
each ally keeps its own window per PC turn (its second attack-trait beat in one PC turn takes −2, 06.14.2).
Resisted effects aimed at the ally are rolled by the ally (00.3.3), with its own defenses. Evidence from
the beat is the ally's own (03.2.6; tracked only for protégés, 16.10.4); the PC's Command beat is the PC's.

**16.7.8 Help and Setup between the PC and allies.** `[D]` In conflict, an ally's Help is bought with a
Command and gives the PC's **next** beat one Precision lever (06.14.2; 01.14.8 eligibility: the ally must
be able to attempt the helped beat alone). An ally's commanded Setup creates its fact for the PC's next
beat (01.14.9). A commanded **Flank** (06.3.5: the ally engaged with a foe the PC is engaged with, one
action, no roll) puts `flag.flanked` on that foe, so the PC's melee attacks hold a Precision lever — the
classic two-person trick, priced at one of the PC's three actions. At most one Help lever per beat; the
two-lever cap (00.3.9) holds for everything.

**16.7.9 Reactions.** `[D]` An ally's one reaction a round is: Fend with no order (−2 on one attack against
it, 06.6.3); its standing order's reaction (06.14.4); or a reaction ability or knack (`ab.interpose`,
`ab.shield_block`, `kn.bodyguard`), all competing for the same one. A Devoted ally may Intercept for the PC
by its reaction with **no** order (T-16-7). No effect gives an ally a second reaction unless 06's own grant
rules allow it (06.1.1; `reaction_cap_with_grants: 2`).

**16.7.10 Allies as targets.** `[D]` Adversaries choose among the PC and allies by 06.9.3's attention order
(an enemy engaged with it that dealt it the most harm since its last turn; else the nearest, the PC before
an ally) or by their behavior list (09.7: "the weakest", "the one carrying the light"). An ally that strikes
a foe draws that foe's attention as anyone does — which is how a companion protects the PC without a
reaction: by being the one who harmed it most.

**16.7.11 Allies and the advisory.** `[D]` Chapter 09 makes the advisory **one word gentler** when a
companion fights at the PC's side (09.6.3). This chapter states when that applies and adds one exception,
both from the simulation (T-16-21):
- **Applies** when at least one **able** ally is in the fight: conscious, its standing Warm or better or its
  contract's hazard covering the encounter's stakes (it will fight), and its serving band equal to
  `band_cap(pc)` (an ally below the cap does not count: a band-1 porter beside an elite moves nothing
  the advisory can promise). Mounts and bound beings of a scene count only if their working or template gives them an
  attack.
- **The hard exception:** an encounter estimated **hard** whose estimated win (PR-09-4) without allies is
  **below 75** stays **hard** with allies; the word is shown as "hard, with your companions beside you".
  In the simulation one capped ally moved every lethal estimate to hard (3 of 3), every fair to easy (5 of
  5), every easy to trivial (1 of 1), and hard to fair exactly when the no-ally win was 75 or more (2 of 7;
  the other five, at 41–65, stayed hard) [T-16-21; DL-16-13].
- **Never more than one word**, whatever the number of allies. Two or more allies usually move a fight
  further (T-16-21: two capped allies, mean 1.1 words; three, 1.6; four, 2.0), so the advisory is
  conservative with a large retinue — the safe direction, which 09 already chose for its own tuning
  (09.6.8: gentler misses never outnumber harsher ones).
- **Allies can die too.** When the encounter carries a lethal context, the lethal warning (07.3) names that
  it applies to allies as well ("the wights will kill Brack if they can"), because Key 1 protects allies
  exactly as it protects the PC (07.12.1); the advisory line also names any ally whose Vitality is below the
  encounter's heaviest single blow ("a single blow could drop Oda").

**16.7.12 Scene allies, escorts and held lines.** `[D]` + `[J:enum]` *Anchor: yes.* Allies who are not the
retinue fight in one of two ways:
1. **Under the PC's lead.** A person or group who has granted the PC's request "stand with me" (a Talk
   request sized by T-16-10's logic for one scene: R2 if no lethal context is known, R3 if one is, R4 if
   they would hold a place against certain loss) or whose duty puts them under the PC's command (a rank,
   15.4.6) is commanded exactly like a retinue ally for the scene: no turn, Command for each beat, its
   reaction and an order, WILL by its standing (T-16-7), default order *stay back* (soldiers: *hold this
   ground*). Three or more of one kind are one **cohort for the scene** (16.2.6). They take no retinue
   place and leave at `scene_end` unless recruited (16.3).
2. **On their own lead** (an escort whose own band exceeds the PC's power band, a rival party, the town watch, a knight who will
   not take orders): they form their own side (06's "three sides": each side its own objective and
   morale). Rather than give them turns (which would add beats on the PC's side), the engine resolves
   their part as a **held line**: at `conflict_start` the DM names `[J:enum]`, from the facts, which foes
   their objective engages (the knight holds the bridge: the foes on the bridge; the watch takes the door:
   the foes at the door; default: the foes engaged with them by 06.9.3, else the largest group the PC is
   not engaged with). Those foes leave the PC's fight into a public **tug clock**
   `clk.16.held_line.<id>` "The line at <place>" (6 segments, starting at 3). At each `round` end the
   engine rolls one **fortune check** (01.6.7) for the holders: their best base attack modifier (16.4.5),
   +2 for each numbers step of their own group (06.10.3: 3–5 members +1 step, 6 or more +2), against the
   highest Guard among the held foes, +2 for each numbers step of the held group (counting held individuals
   as members) — critical success **+2**, success **+1**, failure **−1**, critical failure **−2**. At **6** the
   held foes are defeated or flee (the holders' objective is won); at **0** the line breaks: the held foes
   enter the PC's fight at the start of the next round, rendered first by the clock's last tick ("the watch
   is falling back from the door"). The PC may join the line at any time by engaging a held foe (it leaves
   the clock and enters the PC's fight); a PC beat that targets the held group as a whole ticks the clock by
   its delivered reach. When the PC's own fight ends, a held line still running resolves in the same way at
   one check per round until it completes. *Calibration* (`16-heldline-sim.py`, exact): holders of the held
   foes' own band win **62%** (in a mean of 7 rounds); holders a band or more above them, **75–96%** (a band-4
   champion against one band-3 foe 90%; a band-3 knight against one band-1 foe 96%, against a band-1 mob of six
   75%); holders a band below, or facing a mob of four of their own band, **23–34%** — so "the knight holds the bridge" is a
   good bet, "the villagers hold the gate" a hope, and the clock shows which as it moves [DL-16-14].
`[J:enum]` (which foes are held): *Worst case (J):* the wrong group held — a different set of foes in the PC's
fight, which the advisory recomputes and shows (class ii). Intent verbs: hold the line, cover my back,
keep them busy, take the left flank, hold the bridge while I. Knobs: `targets` (which foes are held),
`duration` (clock size 6 → 4 for a small skirmish, 8 for a battle's corner). *Why:* "my allies hold them off
while I go for the leader" is one of the commonest things a player asks, and a third side with its own
turns is exactly the free-beats problem chapter 06 closed; a clock the player can watch and push is the
anchor 06 already uses for chases and battles (06.12; 06's edge case "A battle") [R1 G-5; R3 G-27; DL-16-14].

### 16.8 Allies outside conflict: asking, the party's time, journeys and downtime

**16.8.1 Asking.** `[D]` + `[J:flag]` Outside conflict there is no Command action: the PC asks (the free
activity "speak a few words", 00.12.6) and the ally acts as the actor of its own beat, framed and rolled
with its numbers (16.7.7) and shown to the player as an OFFER. Its will is the same test as in conflict
(16.7.2, stakes and refusal), and, for a hireling or a follower, chapter 15's duty rule (15.4.6): `[J:flag]`
*"Is this within its recorded duty (the contract's duty text; a follower's oath)?"* True → certain
compliance if it is Neutral or warmer; false → a request at its standing (15.4.1), sized by 15.3.2, which
the ally may refuse. *Worst case (J):* an out-of-duty task treated as duty — one act done without a roll (class
i); the grievance sources still read what happened (G3 if it was dangerous). A companion's "duty" is
nothing: everything it does for the PC beyond following is a request at its standing — which, at Friendly
(ceiling R4), is nearly everything.

**16.8.2 The party's time.** `[D]` Allies may not multiply what the party does with its time where time is
the pressure. By time mode (00.7.3):
- **`conflict`**: 16.7 (only Commands, reactions, orders and hooks).
- **`site`**: the party makes **one significant beat per interval** (10's site time): the PC's, or an
  ally's in its place. Another member may give Help (01.14.8) or join a group action (01.14.7), but does
  not make a second significant beat in the same interval. An ally may hold a **standing task** for the
  interval that needs no roll (keep watch at the door, hold the light, guard the packs): that is no beat,
  and it makes the party not `unaware` at an arrival from that side (10).
- **`free`**: allies may work **separate** activities in parallel with the PC (one searches the archive
  while the PC questions the abbot), each taking its listed duration; results arrive when each finishes.
- **`travel`**: one journey role per traveler per watch (16.8.3).
- **`downtime`**: one duty per ally per week, in parallel with the PC's plan (16.8.5).
*Why site mode is one beat per interval:* the site's time-tick checks run on intervals (10.9, 10.13); two bodies
searching two rooms in one interval would halve every site's danger for any party, and the cheapest
exploit would be hiring a porter to search. In free time and downtime parallel work is cheap and true to
life, and nothing listens to the clock as closely [10.5; 10.10; DL-16-15].

**16.8.3 Journey roles.** `[D]` + `[J:enum]` Allies take chapter 10's four roles by 10's rules (10.5.1:
**navigator**, **lookout**, **scout**, **forager**; one role per traveler per watch; evidence by 03's
`cnt.journey` for a tracked protégé), plus this chapter's fifth, as 03 and 10 provided ("10/16 may
extend"):

**T-16-14 Journey and camp roles** (`data/companions.yaml#journey_roles`; 10's four are restated from
`travel.yaml#roles`, which is canonical for them).

| Role | Allowed at | Who may hold it | What it does |
|---|---|---|---|
| navigator | any pace, any moving watch | anyone; the way-finding beat uses the holder's numbers | the day's way-finding beat (10.4.2) |
| lookout | slow or normal travel; ride; any camp watch | anyone conscious; `kn.keen_eyes` adds a band | arrivals never surprise the party; distance +1 band in open and broken country; omens carry the archetype family; sleepers woken in time (10.5.1) |
| scout | slow or normal travel; ride | anyone; the stored Sneak total is the holder's | perceives arrivals first; may slip away; finds the nearest undiscovered site on a discovery face; **starts encounters at `band.far` from the party** (10.5.1) — a scout ally is alone out there |
| forager | slow travel (normal with `kn.forager`, 10.5.3) | anyone; licensed foraging uses `lic.training.wilds_foraging` | a forage beat at the watch's end, snag "on the move", yield delivered reach − 1 (10.5.1) |
| **quartermaster** | any pace; any camp watch | an ally with `kn.quartermaster` or `lic.training.wilds_survival` | **once per day**, a depletion face (`tbl.10.depletion` rows 1–4: spoiled supply, a guttering light, a damaged item) is prevented: the face counts as a lull without its progress point; evidence `deed.wilds.survival.provisioning` (adopted into `data/tags.yaml` at integration) |

- **Assignment.** The player sets the party's **standing roles** once ("Oda scouts, Brack keeps watch, I
  navigate"); the engine writes the `journey_role` facts at each watch's start from them, and from these
  defaults where none is set: navigator — the traveler with the highest base modifier on
  `deed.wilds.navigation`; lookout — the highest Wits base among the rest; scout — at slow or normal pace,
  an ally holding `lic.training.wilds_tracking` or `lic.training.guile_stealth`, else none; forager — at
  slow pace, an ally holding `lic.training.wilds_foraging`, else none. `[J:enum]` only when the player names
  a role in words ("someone watch our back") — classified to the role; uncertain → lookout. *Worst case (J):* a
  role mis-assigned for one watch (class i).
- **The night rota.** In camp, the retinue may keep watch in turns so the PC sleeps: any watch with a
  conscious ally as lookout leaves the PC not `unaware` at an arrival (10.5.2). An ally may hold at most
  **two** of a day's four watches as a role and must sleep through one: an ally that keeps more takes 07's
  sleep-want (`h.07.fatigue`, applied to the ally) and T-16-8's G8.
- **Mounts and pack beasts** are supply consumers (10.6.2: 1 a day unless grazing, 10.8.2) and march units
  (10.3.5, 10.8), carry their load (08.10.1), and hold no role. A porter carries **10** load units (08.8.8); every
  ally's `carry` adds to the party's capacity while it is present.

**16.8.4 Camp and rest.** `[D]` Allies rest as PCs do (07.8: breather, short and long rests, site, quality),
recover Vitality and heal their one wound (07.12.2), and refill Focus at a long rest (16.4.4). An ally with
`kn.healer` may Treat the PC and the others during a rest (07.8.8), which is how a party heals faster than a
lone wanderer: the treated wound heals on the haven or road schedule of 07.8.7.

**16.8.5 Downtime duties.** `[D]` In downtime (15.10), each ally takes **one duty** for the week in parallel
with the PC's own week plan (`h.15.downtime_week` resolves it; `data/companions.yaml#downtime_duties`):

**T-16-15 Downtime duties.**

| Duty | What it does | Rolls |
|---|---|---|
| `rest` | convalesces: heals as bed rest in a haven (07.8.7); counts as rested for G8 | none |
| `work` | works its trade or hires itself out for the week: its keep is paid by its work (no keep cost this week); a hireling on `work` is owed no wage this week | none |
| `train` | trains under a teacher toward a knack (16.10.2); the fee is the PC's to pay (15.11: 7 / 25 / 100 a week) | 15.11's learning clock |
| `gather_word` | asks around in the settlement for the PC (15's `dt.ask_around`, once, with the ally's Talk numbers) | one Talk against the settlement's tier |
| `assist` | helps the PC's week activity: one Precision lever on its roll, if eligible (01.14.8) | none |
| `tend` | treats the PC or another daily (07.8.8, needs `kn.healer` or the medicine license) | Treat beats by 07 |
| `keep` | minds a holding (11: counts as `managed_this_week` for its yield) or a posted task (16.2.3) | none |
| `errands` | buys and sells for the PC at list price (no haggling, 08.8.7) and carries messages | none |
| `leave` | takes the week for itself (family, a shrine, the tavern): its grievance clock −1 more than its decay | none |

*Why each ally gets a duty:* downtime is where the PC's companions become a household; one duty a week each
is the Fellowship phase of The One Ring and the camp of Darkest Dungeon, and none of them is a second PC
activity — they assist, earn their keep, mend, or listen [R5 P-32; DL-16-15].

### 16.9 Harm, falling and death

**16.9.1 Harm is chapter 07's.** `[D]` (07.12 is canonical; restated so this card stands alone) An ally's
Vitality is its template's at its serving band (16.4.3); it has **no Staggered** state. At 0 Vitality: if
the harm event was **not lethal** (07.3.6 applies to allies exactly as to the PC: Key 1 protects them), it
is **Down** — unconscious for the scene, defeated, alive; if it was **lethal**, it is **bleeding out** —
defeated, helpless, on the **public** clock `clk.bleeding_out` (4 segments; +1 at each `round`; +1 for each
further lethal harm event on it). Stabilizing it — first aid (`verb.handle`) against **Moderate (15)**, a
healer's kit as a lever, or any Vitality-restoring effect — voids the clock; one tender may try once a
round (07's edge case). If the clock completes, the ally **dies**. There is no last-chance menu, no
reprieve and no fate for an ally: its second key is the clock running out [00.17.1 Q8; 07.12.1; R6 C-11].
Bound beings have no ladder (they end at 0, 07.12.4); cohorts follow 16.2.6.

**16.9.2 Telegraphed, always.** `[D]` An ally can die only when: (1) the harm came from a source whose
lethal context was recorded **before** the declaration (Key 1, 07.3) — and the lethal warning names the
allies it threatens (16.7.11); (2) the public bleeding-out clock, shown the moment it starts, ran four
rounds; (3) nobody spent one beat to stabilize it. A single unlucky roll can drop an ally; it cannot kill
one. *Why:* the owner's lock — "death is real but telegraphed" — is about characters the player cares
for, and a companion is the second character a solo player cares for [BRIEF §4; DL-16-16].

**16.9.3 Carrying and tending.** `[D]` A fallen ally can be carried out by the PC or by another ally (one
body each, 07.12.1; a commanded ally drags a fallen friend: T-06-9 row 38), stabilized by a commanded ally
(16.7.6: first aid is a person's commanded beat), or reached and tended by the PC. Leaving a fallen ally
among enemies when the PC leaves is 07.12.3 (the victor's disposition toward it: captive, robbed, left for
dead, or killed only under an effective lethal context).

**16.9.4 After the fall: body and loyalty.** `[D]` Body (07.12.2): an ally that was Down wakes at
`scene_end` at Vitality 1 with a Moderate body wound; one stabilized from bleeding out wakes after a long rest
with a Heavy body wound on a 4-segment recovery clock and refuses attack-trait commands until it heals.
Loyalty (this chapter):
- **Saved:** the PC stabilized it, carried it out, or had another ally do so on the PC's command, or freed
  it from captivity → chapter 15's memory `helped (rescue)`: **+2** standing, deed of weight, cap Devoted
  (T-15-2). An ally the PC fought to save is the most loyal ally in the game; this is deliberate.
- **Left to fall:** T-16-8 G7 (+1 grievance; +3 if it was left among enemies and returns).
- **Fallen in the PC's chosen fight:** no grievance by itself — it accepted the stakes (its WILL let it).
  Grievance comes only from G3 (stakes beyond the bargain) and G7 (left to fall).

**16.9.5 Death.** `[D]` + `[T]` When an ally dies, chapter 07 writes `setback.companion_dead` (12.7.5: the
pacing director's recovery), a **dread check at S3** for the PC if it was present (07.11.2), a −1 tick on the
opposing morale clock (06.11.3) and a chronicle line (07.12.3). This chapter adds, in the same RECORD:
1. **The place** in the retinue frees at `scene_end`.
2. **Its belongings**: what it carried stays with its body (recoverable); party goods are the PC's; its own
   things belong to its **kin** — a fact `kin_of.<ally>` from its principal-depth ties (12.11.1), or "no
   one" — and any wages or shares owed become a debt to the kin (a commitment, 15.7.6).
3. **A vow offered.** The out-of-fiction OFFER line offers the player a **vow** (11's thread kind `vow`): to
   bring its effects and its wages home to its kin, to see its killer answer, or to finish its want. Sworn,
   it is a commitment like any vow (fulfilling it is a `fate` trigger by 01's vow-kept rule). Never sworn
   automatically; declined, nothing is written.
4. **The others' grief.** Every ally who witnessed the death: G10 if the death followed a lethal command or
   an abandonment (+1 grievance), and, in a conflict, the loss-of-heart trigger (16.7.4). Allies hold no
   dread (07.12.2): their grief is in their omens and their loyalty, not a meter.
5. **Memory.** Every NPC who knew the ally receives a memory of its death (12.11.7, `how: told` when it
   reaches them); the ally's personal thread, if open, becomes a thread about its absence (16.12.4).
*Grief is real but bounded:* one dread check (07), one vow offered, the pacing director's recovery window
(12.7.5), the other allies' loyalty movements. The dead ally is never a lever ("for Brack!" is narration;
its mechanical form is the vow) [00.3.9; DL-16-16].

**16.9.6 Death is final.** `[D]` A dead ally stays dead: true resurrection is impossible in every region's canon (12.16.5
item 1; 05.7.10 item 1), and there is no ally-specific resurrection [verification: V2b-026]. A raised dead ally is a **bound**
being (16.15.6), not the person it was: it has no standing, no drives, and no memories but what its working
gives it.

### 16.10 Growth: slow, bounded, never past the hero

**16.10.1 Seasoned service.** `[D]` + `[T]` Handler `h.16.season_growth` (`season`, phase 8, after 04's
consolidation) raises an ally's **own band by one** when all hold:
1. its own band is below the top of its template's band range (`band_range`, T-16-19's Bands column) [verification: V2c-011];
2. it served the whole season in the retinue or posted (16.2.3);
3. during the season it took part in at least **two** conflicts in which a foe of threat band ≥ its own
   band was defeated, or in **one** ★ conflict (T-16-8 R3: advised hard or lethal).
At most one band a season. Its line is rebuilt at its serving band, which the cap still bounds (16.2.4): a
veteran under a novice stays a band-1 ally however seasoned it becomes, and steps up the day the PC does.
Beasts grow by the same rule; bound beings and scene allies never do. *Why a season:* chapter 04's
crystallizations and the Season Turn (11) run on the same boundary, so an ally's growth lands with the
world's, and one band a season means a porter becomes a veteran in no less than two seasons of hard road
[C:VI (boundary points); 04.8; DL-16-17].

**16.10.2 Training.** `[D]` An ally may learn **one knack a season** by the downtime duty `train` (T-16-15)
under a teacher (15.11's learning clock and fees, the ally as the learner): a `kn.trained` with a named
training license, or any other knack of T-16-6 its template's family allows (`trainable_knacks`). An ally holds
at most three knacks; a fourth **replaces** one (VI).

**16.10.3 Gear.** `[D]` An ally's power grows also through what the PC gives it (16.4.8), inside 08's item
caps and 16.4.6's ceiling.

**16.10.4 Protégés: a bounded calling of their own.** `[D]` A template marked `protege: true` (the squire, the
apprentice, the novice acolyte; T-16-19) sets `tracks_evidence: true` (03.2.7): the protégé's own resolved
deeds are evidence for **it**, and chapter 04 evaluates it by its own rules with **one deed seat, no oath
seat, and a maximum tier of 3**; its offers are put to the player, who answers for it (04's edge case
"A companion"). What its tiers do is this chapter's, all bounded:
- **Band:** a confirmed tier *n* raises its own band to at least *n* + 1 (tier 1 → band 2; tier 2 → 3; tier
  3 → 4), still served at the cap.
- **Abilities:** its picks (04's pick procedure) go into its three-ability partition (16.4.4); a pick beyond
  three **replaces** one, the player choosing (VI).
- **Competence:** 04's tier competence applies to its calling's key tag, clamped to `c_b + 1` of its serving
  band, so a protégé is better at its calling than another ally of its band and never better than the PC.
- **Focus:** by 16.4.4 only; a calling's Focus rules (05) are the PC's.
*Why allow a companion a calling at all.* The constitution's growth is history-gated (P2, P5), and a squire
who becomes a knight in the PC's service is the genre's best-loved companion arc (Pendragon's squires;
Ironsworn's legacies); refusing it would make every companion static. The bounds — one seat, tier 3, the
band cap, three abilities, the competence clamp — keep the arc under the hero, and a protégé is the natural
successor when the hero retires (16.16) [04's edge case; 03.2.7; R6 D-R4; DL-16-18].

**16.10.5 What never grows.** `[D]` An ally's actions (0), reactions (1), retinue place cost, and the band
cap. An ally never gains a slot partition, fate, dread, marks, a last-chance menu, or an oath seat.

### 16.11 Witnesses, recognition and reputation

**16.11.1 Allies are witnesses and carriers.** `[D]` An ally present at a deed is a **witness** by 03.10.1's
test like anyone, and every ally that can tell others — every person, and any ally flagged `speaks: true`
— is a **carrier** (03.10.2 names "a companion" explicitly). Beasts, bound beings without speech and
mounts witness but do not carry. Consequences, all through other chapters' machinery:
- a deed done in front of a person-ally is **public** (03: witnessed evidence feeds 11's reputation in the
  ally's scope and the PC's), even in an empty wilderness: bringing companions makes the PC's story travel;
- an ally's telling reaches its own scope (03.10.4): a hireling from Ashford carries the PC's deeds to
  Ashford's taverns at its next stay there (11 resolves rumor spread).
**Silence.** The PC may ask an ally to keep a deed to itself: a request (R1 at Warm or better, R2 at
Neutral, sized by 15.3.2 by what silence costs it; R4 if the deed affronted one of its values) whose
success writes the commitment that 03.10.2(c) reads ("no commitment binds it to silence"); breaking it is
the ally's own act (Hostile allies may sell it: T-16-11 row 2).

**16.11.2 Allies as recognition's voices.** `[D]` + `[N]` Chapter 04 chooses the vehicle (04.6;
`data/vehicles.yaml`); allies are valid recognizers or witnesses for these, and the DM, when 04's vehicle
selection returns one of them and an ally is present, stages it through the ally whose drives fit best
(`[J:enum]` among present allies, by the first that holds: a value axis matching the calling's conduct, a
trained tag on the calling's deed branch, the highest standing; default the highest standing).
*Worst case:* a less fitting ally voices it — narration only (class i).

**T-16-17 Allies in recognition vehicles.**

| Vehicle (04) | The ally's part |
|---|---|
| V1 The Witnessed Epithet | a person-ally who witnessed the deeds is often the first to use the name; its telling spreads it (11) |
| V4 The Oath Spoken | an ally of Friendly or warmer may stand as the oath's **sworn witness** (a bonded witness, 03.10.4) if the player names it; it then voices the oath's keeping and its Fraying (V14) |
| V6 The Seer's Reading | "a companion's remark" (04.6.4): an ally at Warm or warmer voices the readiness band at a reflection in its own words — a soldier's "you're becoming something, you know that?" |
| V7 The Reflection at Rest | "companions by a fire" (`vehicles.yaml`): the ally is the one who says what the PC has become |
| V8 The Rival Names You | an ally who left Hostile may be the rival (16.6.7) |
| V14 The Fraying | the oath's sworn witness among the allies is the one who doubts aloud; an ally whose value is the oath's axis ticks grievance by G1 as the Fraying's deeds happen |
An ally voices recognition but never grants it, never names a calling as a mechanic, and never states a
number (12.14.4–12.14.5).

**16.11.3 Allies and the PC's reputation.** `[D]` Reputation is 11's (00.17.1 Q22). This chapter adds only: an
ally's standing toward the PC is information others can learn (a Read, 15.6.1, of the ally; a rumor), and
11 may read "how the PC treats their people" from the retinue's departure record (causes `unpaid`,
`loyalty_*`, `death` after abandonment) as reputation content in the scopes where those allies came from
(Interface requests). Hiring reaction rolls read it (16.3.2 step 3).

### 16.12 Hooks: allies bring their own stories

**16.12.1 Every principal ally has a personal thread.** `[D]` When a person becomes a principal-depth ally
(a companion at joining; a hireling after four weeks; a follower when named in a thread), the engine seeds
a **personal thread** (11's thread record, kind `quest`) from its **top want** (12.11.1) and its **secret**
if it has one: `tbl.16.personal_thread` (d12 by want object: a lost kinsman; a debt to someone dangerous; a
wrong done to its family; a home to win back; a name to clear; a vow it cannot keep alone; a teacher to
find; a rival to face; a thing it stole and must return; a place it fled; a child it left; a faith it
lost). The thread is written **sealed** (its truth and its people) with **at least three clue placements**
(11's and 15's rule for every hook: 15.9.4), and a proactive **fallback** (a person from its past arrives:
12.8's lead injection may draw it) [R5 G-3; R6 B (hooks with three clues and a fallback)].

**16.12.2 When it opens.** `[T]` + `[D]` The thread opens (becomes **shown** in the quest register, 00.6.3)
at the first of: the ally reaches **Friendly** (it confides — the regard moment, T-16-16); the ally joined
with a want term naming it (16.3.4: the thread is why it came); its fallback arrives. Opening unseals the
want (16.5.6 item 4) and places the thread's first clue in the ally's own telling.

**16.12.3 Its completion.** `[D]` A thread completed by resolved beats (11's completion; the progress clock
filled by delivered reach) is a **deed of weight** for that ally: standing **+1** (to Devoted allowed,
16.5.10), its `signature_knack` gained (T-16-19; replacing one if it already holds three), a chronicle line,
and 16.6.5's choice (stay with a new want at Friendly or Devoted; leave content at Warm or below). Each beat
that ticked the thread's clock ticked regard (R7). This is Mass Effect 2's loyalty mission in this ruleset's
terms: the companion's devotion is earned by solving the companion's problem.

**16.12.4 Abandoned, failed, or orphaned.** `[D]` A thread the PC abandons while the ally is present (the
PC declares it closed, or its clock is voided by the PC's choice) ticks grievance **+3** (G2's weight: it was
told it would be helped; record it under G1's row as "value affronted: loyalty"), and the ally's want stays
open. A thread **failed** by the world (its clock voided by a racing clock, 00.8.5) ticks nothing — the
ally grieves the outcome, not the PC. A thread whose ally dies becomes a thread about its **absence** (kin
to tell, a debt to pay, a wrong to right), which is what 16.9.5's vow attaches to.

**16.12.5 Allies as hooks into the world.** `[D]` An ally's ties (12.11.1: factions and NPCs by Oracle) are
facts other chapters use: 11's World Turn may have a faction **court** an ally (`courted_by`, sealed, with
an omen: the ally comes back late from town), a creditor come for its debt, its kin send word. Each such
event is 11's (its clocks, its event tables); this chapter asks only that ally ties be eligible targets
(Interface requests). A courted ally at Neutral or warmer reports the courting to the PC at its next regard
moment (an ally's honesty value +1 reports it at once); one at Wary or worse keeps it (T-16-11 row 3).

### 16.13 Voice, memory, and staying in character

**16.13.1 Voice.** `[N]` + `[D]` Every person-ally keeps 12's **register** and **habit** (12.11.3) — rolled at
recurring depth, kept forever — and speaks in them; its habit is used at most once a scene. A beast is
described, never voiced: its temperament (16.15.3) is shown in its body (a hound's hackles, a mule's ears).
What an ally calls the PC follows its standing (T-15-1's "voiced as" row) and what it knows.

**16.13.2 Memory of shared events.** `[D]` An ally keeps 12.11.7's **memories** of the PC (at most five
active, kept by salience then recency, the rest archived and queryable), written whenever it witnessed or
took part in a beat involving the PC. In addition, the **shared record**: the engine keeps, for each ally,
the list of conflicts, ventures and scenes it shared with the PC (ids and dates, from the scene log), so
that "remember the barrow?" is a lookup, not a recollection. At an ally's first line in a scene the 12.11.7
test applies (`[J:flag]`: does an active memory bear on this exchange?). Narration may never contradict a
memory, and an ally never "remembers" an event it was not present for unless it was told (`how: told`).

**16.13.3 The consistency rule: what may make an ally act.** `[D]` An ally does something only for one of
these reasons, and the narration may imply no other (`Narration may not imply` for every ally card):
1. the PC commanded or asked it (16.7.1, 16.8.1), and its will allowed it (16.7.2);
2. its reaction or its standing order (06.14.4), including the automatic orders of 16.7.3–16.7.5;
3. a hook or passive its template or knacks list (T-16-6);
4. its rung's contract (T-16-7's "uncommanded" and "outside conflict" columns), its duty (16.8.1) or its
   downtime duty (T-16-15);
5. a breaking point (16.6) or a betrayal (16.6.6);
6. when none of these settles what it does and it must do something (a stranger insults it; a guard asks
   it its business), chapter 12's `tbl.npc_action` (12.11.5: d10 + its standing toward the asker), with the
   DM choosing which of its recorded drives or traits the row expresses.
*Never* because the DM thinks it "would" (12.11.4's agreeable-NPC failure in reverse: an ally that acts on
its own initiative is a second PC). An ally acting against its recorded personality — a merciful companion
killing a prisoner unasked, a coward charging — is impossible without a loyalty trigger: it would need a
command (and its WILL would test its refusal) or a breaking point. *Opinions:* an ally expresses approval or
disapproval only through counsel (16.5.7) and the omens of its clocks (16.5.8); elsewhere it may talk, joke,
complain and tell stories in its voice, but it may not state a judgment of the PC's conduct its drives did
not produce [R4 W4; R: https://arxiv.org/abs/2606.20708 (agreeable-persona bias); DL-16-10].

**16.13.4 How much an ally speaks.** `[N]` + `[D]` Allies are company, not a chorus. Per scene, at most: one
line of **banter** from one ally at `scene_start` (rotating among present allies, the one least recently
heard first — the spotlight rule of 12's facets, 16.13.5), plus whatever its counsel, omens, memories,
commanded beats and confrontations require. A player who asks an ally something gets an answer (free
activity) in its voice and within its knowledge (12.10.6).

**16.13.5 Allies are facets of the spotlight.** `[D]` Chapter 12 counts each companion as a **facet** of the PC
(12.9: "each companion (16)"), foregrounded when a resolved frame in a scene cited it (a commanded beat, a
Help, a role, a knack) or the scene's agenda or a delivered lead named it, and rotated like every facet so a
companion untested for a while gets a scene (its thread's clues are the natural material). Ally deaths are
setbacks (12.7.5).

### 16.14 Wages, keep and contracts

**16.14.1 Who costs what.** `[D]` (`data/companions.yaml#upkeep`; prices are 08's, `economy.yaml#wages`)

| Ally | Weekly cost in a settlement or a haven | On a venture |
|---|---|---|
| hireling | its wage (08.8.8: porter 7; skilled hand 10; soldier or scout 14; specialist 21; veteran 50 + half share; champion 150 + full share; legend never for coin) | its wage, and 1 supply a day (10.6.2) |
| companion, follower | its **keep**: the poor lifestyle, **4** coins a week (08.8.6), or nothing if it is lodged at the PC's holding or haven, or paid by its own `work` duty (T-16-15) | 1 supply a day |
| cohort | wage or keep per member | 1 supply per member a day |
| beast | 08.10.2's upkeep when stabled (hound 1, hawk 1, donkey 2, pony 3, mule 3, riding horse 5, draft horse 5, courser 8, destrier 10), nothing when grazing | 1 supply a day unless grazing (10.8.2); hawks and hounds feed on what the forager or the hunt brings (10.6.4 yield counts for them) |
| bound | nothing in coin; the working's own cost (05) | none |

Keeping a companion at the PC's own lifestyle or better (paying its keep at that rung) is generosity: the
weekly difference above 4 counts toward T-16-8 R4 when it is at least 1 Unit of the ally's lifestyle.

**16.14.2 The contract.** `[D]` A hireling's contract (written at hire, 16.3.3) is a commitment of two sides
(15.7.6): `{duty, wage_week, hazard, term: weeks n | venture | open, share, paid_through}`. The PC's side is
to pay; the hireling's is to serve within its duty and hazard. Its **term** is a number of weeks, the
current venture (ends at `venture_end`), or open (ends on a week's notice from either side). A contract may
be **renegotiated** at any haven (a request at the new terms' size: a longer term is one rung lower than a
new hire because the hireling knows the PC; a higher hazard is the new hazard's rung).

**16.14.3 Upkeep at the week.** `[D]` + `[T]` Handler `h.16.retinue_upkeep` (`week`, phase 4; reserved by 00)
for each ally in the retinue or posted: charge its weekly cost (16.14.1) from the PC's coin; on a venture
week only supply is charged (10's daily handler) and wages accrue to be paid at the next haven
(`paid_through` lags); write `paid` or `unpaid`; roll the posted task (16.2.3); run T-16-8's weekly sources
(G4, G8, G9) and the grievance decay of 16.5.3 (via the clock's `decay` row). It runs **after** 08's
`h.08.upkeep` (same phase, owner order), which charges lifestyle, stabling and holdings, so a shortfall falls
first on the PC's own lifestyle (08.8.6) and then on the retinue.

**16.14.4 Contracts that end.** `[D]` + `[T]` Handler `h.16.contract_term` (`day`, phase 6) marks contracts
whose term ends today (or `venture_end` for venture terms). At the end of a term, at the next haven:
1. the hireling is paid off (arrears and shares) — or the unpaid sum becomes a debt it holds (15's `owed`);
2. the PC may **renew** (16.14.2's renegotiation; a hireling at Friendly or warmer renews with certainty at
   the same terms, 15.3.10);
3. a hireling who served **four weeks or more** and stands at **Friendly or warmer** may instead offer to
   **stay as a companion** (no frame: it offers; the player accepts or declines): its kind becomes
   `companion`, its joining `{kind: bond}`, its wage ends (keep only), its contract hazard no longer limits
   it (its rung does);
4. otherwise it departs (cause `contract_end`), a recurring NPC who remembers how it was treated.
*Why the conversion:* the hireling who stays on for the hero rather than the pay is the old-school
henchman's best moment and the M&B companion's; making it an offer at Friendly after a month makes it
earned and visible [R: https://oldschoolessentials.necroticgnome.com/srd/index.php/Retainers; DL-16-19].

**16.14.5 Unpaid.** `[D]` Each `week` boundary at which a wage or keep due is not paid ticks G4 (16.5.4:
hireling +2, others +1). A **Friendly** ally serves two weeks unpaid without grievance, a **Devoted** one four
(T-16-7). A **hireling** unpaid at two consecutive `week` boundaries leaves at once (cause `unpaid`), holding
the debt (15's `owed`); a broken contract is 15's `betrayed` toward it (−3) if the PC refuses the debt when
next met. Followers and companions are never owed wages, only keep; unfed or unkept they tick grievance by
G4 and G8 but do not leave for it alone.

**16.14.6 Shares.** `[D]` Handler `h.16.venture_end` (`venture_end`, phase 9): for every hireling whose
contract has a share, compute its share of coin found during the venture (half share = ½ of one equal
part, full share = one equal part, where parts are the PC plus each sharing hireling), rounded down; pay it
or tick G5. Also: T-16-8 R5 (the road together) for every ally who completed the venture.

### 16.15 Beasts, mounts and bound beings

**16.15.1 Beasts are allies without words.** `[D]` A beast ally has no drives, no counsel, no personal
thread, no Talk, and no NPC depth; it has a **temperament** and a **beast loyalty** on the standing scale
that only care and harm move. It hears by `voice` (it knows its name and simple commands within
`band.near`), by `signs` (`kn.sign_trained`), or by `bond` (`rit.beast_bond`: intent without words, any
distance at which the PC could call it). A beast's commanded beats are T-16-13's beast row.

**16.15.2 Temperament.** `[D]` One of four, from the template (rolled d4 for a tamed wild beast): `steady`
(never loses heart while Neutral or warmer), `skittish` (loses heart at Warm too, 16.7.4), `fierce` (its
default order is *harry that one* if allowed; it will not take *stay back* while a foe is engaged with the
PC — it must be commanded twice), `gentle` (refuses Strike and Grapple against folk unless Devoted). The
narrator shows temperament in the beast's body, never in words it does not have.

**16.15.3 Beast loyalty.** `[D]` A beast's regard and grievance clocks tick only from this list
(`data/companions.yaml#beast_sources`), replacing T-16-8 for beasts:

| Id | Source | Clock | Ticks |
|---|---|---|---|
| B1 | fed and watered every day of the week (no `went_without`) | regard | +1 a week |
| B2 | groomed, praised and kept by the PC's own hand at least one day this week (a free activity the player declares, or the camp hand's `keep` duty) | regard | +1 a week |
| B3 | the PC (or an ally on the PC's command) stabilized it or carried it out (16.9.4) | regard | +3 (and 15's rescue +2 standing, deed of weight) |
| B4 | it fought beside the PC in a ★ conflict and both stood at the end | regard | +1 |
| G-B1 | went without food or water a day | grievance | +1 a day |
| G-B2 | struck, whipped or harmed by the PC (any harm event whose source is the PC) | grievance | +2 |
| G-B3 | overworked: a mount ridden at hard ride or loaded over half for two consecutive watches (10.3) | grievance | +1 |
| G-B4 | left Down or bleeding (G7's test) | grievance | +1 |
A beast at Unfriendly runs off at the next night watch (16.6.3); a Hostile beast attacks its handler if
cornered, otherwise flees. Beasts never betray. A bonded beast (`rit.beast_bond`) cannot fall below Wary while
the bond lasts (the rite's text); its bond ends only with its life or the rite's undoing.

**16.15.4 Mounts in conflict, and fright.** `[D]` + `[J:flag]` A mount carries its rider and shares the
rider's participant (06.15.1). A mount **without** `kn.war_trained` in a conflict needs a **Handle (ride)**
beat at the start of each of the rider's turns (06.15's "controlling a mount amid a melee"; this is the
"16 owns the check" of 08.10.1): `verb.handle`, Presence or Agility, against **Moderate**, Easy if the mount
is Friendly or warmer toward the rider; a Precision lever for `lic.training.martial_mounted`; failure: the
mount shies — the rider's first action this turn is spent keeping the saddle and the rider is
`cond.off_balance`; critical failure: the rider is thrown (a fall from the mount's height, 06.5.8; `flag.mounted`
removed). The beat costs no action on success. **Fright** (10.8.3's "a mount frightened by a creature with
dread (16's check)"): the first time in a scene that a mount without `kn.war_trained` perceives a creature whose
template carries `dread: S<n>` (09), the rider makes the same Handle beat against the tier of that severity
(S1 Easy … S4 Very hard); failure: the mount bolts one band away from the creature, rider and all, and the
rider is `cond.off_balance`. `[J:flag]` *"Does the mount perceive the creature?"* True only when it is within
`band.far` and in sight, or its scent is established on the wind; uncertain → true (a mount knows before its
rider does). *Worst case (J):* one unneeded Handle beat (class i). War mounts never roll either check.

**16.15.5 Familiars.** `[D]` A familiar bound by `rit.bind_familiar` (05) is a band-1 tiny beast ally
(`cmp.familiar`: Vitality 3, one place), understands the PC's speech, lends its senses for one interval a
day (05's scope), and acts only when commanded. Its loyalty is the bond's: it starts Friendly and is moved
by the beast list (16.15.3). It is a valid lookout (it has eyes) but holds no other journey role.

**16.15.6 Bound beings: obedience, not loyalty.** `[D]` A summoned servant, a raised dead or an automaton
(05; templates `cmp.bound_servant`, `cmp.bound_dead`, `cmp.bound_automaton`) has **no standing, no drives, no
clocks, no memories and no will**: it obeys every command its working's text allows (WILL's capability and
order tests only; stakes and refusals do not apply) and nothing else; uncommanded it keeps its order or stands
(05's edge case: "a servant with no one to command it does nothing"). It serves at the band cap; it ends at 0
Vitality (07.12.4) or when its working ends; a lasting one takes a retinue place (T-16-2). It is never a
witness that carries (it does not tell), never a successor, and never counts for the advisory unless its
template has an attack.

### 16.16 Legacy: allies when the hero's road ends

**16.16.1 Allies as successors.** `[D]` When the PC retires or dies (11's legacy procedure; R6 D-R4's three
pre-connected successor candidates), every ally at **Friendly or warmer**, every protégé, and every
companion who left content (16.6.5) is a **successor candidate** for 11 to offer. A chosen successor starts
as a new PC at chapter 02's baseline — never at its ally line, its band or its protégé tier (retirement is
a structural reset, R6 D-R4) — keeping its name, its drives as background hooks (02's aspirations and bonds),
its memories as knowledge, and its standing toward the others as bonds.

**16.16.2 The retinue after the hero.** `[D]` At the PC's retirement each ally's fate follows its standing:
Devoted and Friendly allies stay with the PC's household or legacy (11) and may serve the successor (they
re-join at their standing toward the new PC, which is their old standing toward the predecessor minus one:
loyalty to a person is not loyalty to their heir); Warm and below disperse to their homes as recurring NPCs.
At the PC's death, 16.9.5's writes run for the PC's allies as for a death among them (they grieve), and any
Devoted ally is offered to 11 as the one who carries the PC's last words or effects (a legacy hook).

**16.16.3 Retired heroes as allies.** `[D]` A retired PC becomes a principal NPC of the world (11). To a
successor its own band exceeds the successor's power band, so it never follows as retinue; it is a **mentor** (04's V2 recognizer
for the successor), a patron, a contact (15), or an **escort** on its own lead for a scene (16.7.12) — the
old hero who rides with you to the first bridge and holds it while you cross. This is R6's "retired PCs as
NPCs and mentors" inside the band cap [R6 D-04, D-10, D-R4; DL-16-20].

---

## Procedures

**PR-16-1 Recruit (any road).** `[D]` (16.3)
1. Classify the road: hire (16.3.3), invite (16.3.4), bond from creation (16.3.5), follower offer (16.3.6),
   beast (16.3.7), working (16.3.8). A follower offer and a working skip to step 6.
2. Gate tests 1–5 of 16.3.1 in order (mind, tongue, band, places, refusal); on a failure, stop and give the
   test's redirect in the fiction; no time is spent.
3. Size the request: T-16-9 (hire) or T-16-10 (invite), `[J:rung]`, the higher when between two.
4. Collect terms (15.3.5; for a hire, the wage advance and hazard pay need no price test); effective size;
   compare with the ceiling (15.3.4): above the ceiling by one with a term and Wary or better → offer a
   persuasion campaign (15.8.1); above by more → G4 with 15's redirect.
5. Certain (15.3.10) or frame: OFFER (DC, odds, the ceiling, the places, the band the ally would serve at),
   commit, roll, read.
6. On success: write the ally record (16.1.2): kind, template, own band, serving band, line (PR-16-2),
   joining or contract or oath, standing (its current value; Friendly for a follower or a bonded beast;
   Neutral for a bought beast; Wary for a tamed one), clocks `clk.16.regard.<id>` and
   `clk.16.grievance.<id>` (none for bound beings), default order, journey roles; roll drives (PR-16-4);
   promote to principal if a companion (12.11.1) and seed its personal thread (16.12.1).
7. Codex: shown and available fields per 16.1.3.

**PR-16-2 Build an ally's line.** `[D]` (16.4)
1. `band_cap = max(1, power_band − 1)`; `serving_band = min(own_band, band_cap)`.
2. From the template at the serving band: attributes by rung (T-09-2); competence `c_b` on each trained tag;
   defenses and Guard (09.3.4 with the shield edge); attacks (modifier = rung + `c_b`; severity = the band's
   standard harm + offset); Focus (09.3.8 base, +1 caster); abilities by id at rank 1 (protégés: 16.10.4).
3. Vitality: `min(T-16-4 by band × size, PC max Vitality − 1)`; reduction by gear or natural armor, cap 4.
4. Knacks: the template's, any trained, the signature knack if its thread is complete; at most three.
5. Gear the PC gave it: apply 08's item rules (16.4.8).
6. Check 16.4.6 (base modifiers ≤ the PC's band floor; Vitality below the PC's; harm per blow ≤ the PC's
   Strike base severity); clamp and log a `rule_conflict` ruling on any failure.
7. Store the line; the codex shows it. Rerun on `trg.16.band_cap_changed`, a band rise (16.10.1), a protégé's
   tier, a knack gained, gear changed.

**PR-16-3 Build a template from an archetype (recruiting anyone).** `[D]` (16.3.9)
1. Read the creature's archetype (09.2; an unlisted creature: 09.2.4's classification first).
2. Mind test (09.2.7): mindless → only a working; animal → beast roads; alien → only when bridged.
3. Template `cmp.from_archetype`: the archetype's attribute rungs, trained defenses, evidence tags as trained
   tags, natural attacks (no heavy blow), tags, size, pace and `cannot` list; drop every `adversary_only`
   power and every power whose effect adds an action, summons, or dictates choices; keep at most three
   remaining powers or pool abilities as its abilities.
4. Family by the archetype's role (09.4.2): brute, skirmisher-like and soldier roles → fighter; archer and
   caster roles → shooter or caster; others → skirmisher; beasts → war_beast if the archetype is a predator,
   else beast.
5. PR-16-2 at the serving band. Drives by PR-16-4 (`tbl.16.drive_cunning` first for a `cunning` mind).

**PR-16-4 Roll drives.** `[D]` + `[S]` (16.5.5)
1. If the template or follower rule fixes a value, write it; else roll `tbl.16.drive_values` (d10 axis, d6
   pole: 1–5 positive, 6 negative), or `tbl.16.drive_cunning` (d6) for a cunning mind.
2. Roll the second value (reroll a repeated axis).
3. Want: the top-ranked want (principal) or the single want (recurring); line: the recorded refusal, else
   roll one on `tbl.npc_refusal`.
4. Seal all three; `known_to_pc: false`.

**PR-16-5 A loyalty source fires.** `[D]` (16.5.3–16.5.4)
1. At RECORD of an event a present ally witnessed (or at the boundary for the absent-too sources), test each
   T-16-8 row whose trigger family matches (16.5.4 card), citing ids; beasts use the beast list (16.15.3).
2. Respect each row's cap (per axis per scene, per week …).
3. `tick_clock` regard or grievance by the row's amount; select the omen of the stage (T-16-16); the omen
   must be rendered this turn (INV-14); an R1 or G1 tick unseals that value (16.5.6).
4. On a regard completion: if the standing is below Friendly and the weekly small-source cap allows it (or
   the cycle held an R3 tick), `eff.15.standing_step +1` (cap Friendly); else hold the clock at 5. Reset.
   Render the regard moment (a confidence).
5. On a grievance completion: `eff.15.standing_step −1` at once; reset; queue the confrontation (PR-16-6);
   then run PR-16-7's checks for the new rung.

**PR-16-6 The confrontation.** `[D]` + `[J:flag]` (16.5.9)
1. At the first `scene_start` with no hostile participant present, the ally raises its grievance: name in
   words the sources in the completed clock's history (most recent first).
2. The player answers. If the beat's method addresses a named source (`[J:flag]`, citing its fact), frame
   **amends**: a win-over against the ally's Resolve defense at its new standing (request R2; not limited by
   15.1.7's caps); success → `eff.15.standing_step +1` (back to the previous rung, never above).
3. A failed amends leaves the step. Ignoring the confrontation → grievance +1.
4. Any promise made is written as a commitment with the ally (kept +1, broken → `betrayed` −3).

**PR-16-7 Breaking points.** `[D]` + `[T]` (16.6)
1. Standing becomes Wary → `create_clock(clk.16.departure.<id>)` (public, 4, +1 a day, +1 per grievance tick);
   it voids when standing returns to Neutral or warmer; on completion the ally departs at the next
   `scene_end` not in danger (`loyalty_wary`).
2. Standing becomes Unfriendly → the ally announces; departs at the next `scene_end` not in danger
   (`loyalty_unfriendly`); hands back party goods, keeps goods worth unpaid wages.
3. Standing becomes Hostile → check 16.6.6's four conditions; if all hold, arm `trg.16.betrayal` on the
   opportunity; else depart at once (`loyalty_hostile`).
4. On `trg.16.betrayal`: roll `tbl.16.betrayal` restricted to rows whose opportunity holds; apply its writes;
   the ally departs; chronicle line.
5. Every departure: remove from the retinue (or, for a death, at `scene_end`); settle wages and shares or
   write debts; set `ally_kind: null`; keep the NPC record, memories and standing.

**PR-16-8 A command in conflict (16's part of PR-06-9).** `[D]`
1. Hearing (06.14.2 decision 1, by `hears`).
2. Will (16.7.2): capability (gate for the ally) → stakes against the largest of rung, contract and oath
   acceptance → refusal → allowed order. A refusal is announced and costs no action.
3. Frame the beat with the ally's numbers (16.7.7); OFFER; commit; roll; read; costs land on the ally.
4. Record: evidence for the ally only if `tracks_evidence`; T-16-8 sources that the beat fired.

**PR-16-9 The week for the retinue.** `[D]` (`h.16.retinue_upkeep`, `week`, phase 4, after `h.08.upkeep`)
1. For each ally (retinue or posted): charge its weekly cost (16.14.1) in a settlement or haven; on a venture
   week accrue wages to `paid_through`.
2. Write paid or unpaid; tick G4 for each unpaid (respecting the Friendly and Devoted grace weeks); a hireling
   unpaid at two consecutive weeks departs (`unpaid`) holding a debt.
3. Run the weekly sources: G8 (neglect), G9 (friction), R4 (a gift recorded this week); grievance decay runs
   through the clock's own `decay` row (`h.00.clock_auto`).
4. Posted allies: roll `tbl.16.posted_task`.
5. Overflow (16.2.1): if the retinue exceeds the cap and the warning day has passed, the most recently joined
   ally below Friendly departs (`overflow`).

**PR-16-10 The season for the retinue.** `[D]` (`h.16.season_growth`, `season`, phase 8, after 04's handler)
1. For each ally: test 16.10.1's three conditions; on pass, own band +1 (template max); rebuild the line
   (PR-16-2).
2. Protégés: apply any tier confirmed by 04 this season (16.10.4).
3. Reset per-season caps (R2's once per want per season; the one follower offer per season).

**PR-16-11 The held line.** `[D]` + `[J:enum]` (16.7.12)
1. At `conflict_start`, name the held foes from the independent side's objective (`[J:enum]`, citing the
   fact); move them out of the PC's fight; the advisory is computed without them.
2. `create_clock(clk.16.held_line.<id>)`, tug, 6 segments (4 for a skirmish, 8 for a battle's corner),
   starting at half, public.
3. At each `round` end: one fortune check by the holders — their best base attack modifier, +2 per numbers
   step of their group — against the held foes' highest Guard, +2 per numbers step of the held group:
   critical success +2, success +1, failure −1, critical failure −2.
4. A PC beat against a held foe moves that foe into the PC's fight (it leaves the line); a PC beat that
   targets the held group as a whole adds its delivered reach.
5. At full: the held foes are defeated or flee. At 0: they enter the PC's fight at the next round's start;
   the clock's last tick is rendered as the line giving way.

**PR-16-12 An ally dies.** `[D]` (16.9.5)
1. 07.12.3's writes: `setback.companion_dead`; the PC's dread check at S3 if present; the opposing morale clock
   −1; a chronicle line.
2. Free the retinue place at `scene_end`; belongings stay with the body; party goods are the PC's; wages and
   shares owed become a debt to its kin (`kin_of.<ally>` from its ties, or none).
3. Offer a vow (out of fiction; 11's thread kind `vow`): its kin, its killer, or its want.
4. G10 for each witnessing ally if the death followed a lethal command or an abandonment; 16.7.4 for allies in
   the conflict.
5. Memories to every NPC who knew it; its open personal thread becomes a thread about its absence.

---

## Tables

Tables embedded in the Rules are canonical in `data/companions.yaml` where they carry numbers, and indexed
here: **T-16-1** kinds (16.1.1) · **T-16-2** places (16.2.2) · **T-16-4** the companion line by band (16.4.3)
· **T-16-5** ally base modifiers (16.4.5) · **T-16-6** knacks (16.4.7) · **T-16-7** the companion contract
(16.5.2) · **T-16-8** regard and grievance sources (16.5.4) · **T-16-9** hire sizes (16.3.3) · **T-16-10**
join sizes (16.3.4) · **T-16-11** betrayal (16.6.6) · **T-16-12** orders by family (16.7.3) · **T-16-13**
commanded beats by kind (16.7.6) · **T-16-14** journey and camp roles (16.8.3) · **T-16-15** downtime duties
(16.8.5) · **T-16-16** loyalty omens (16.5.8) · **T-16-17** allies in recognition vehicles (16.11.2) ·
**T-16-18** departure causes (16.6.1). The tables below are defined here.

**T-16-3 The band rule.** `[D]` (`data/companions.yaml#retinue`)

| PC power band | Who may follow (own band) | They serve at | Retinue cap by Presence −1 / 0 / +1 / +2 / +3 / +4 |
|---|---|---|---|
| P1 novice | 1 | 1 | 1 / 2 / 3 / 4 / 5 / 6 (the same at every band) |
| P2 seasoned | 1–2 | 1 | |
| P3 elite | 1–3 | 1–2 | |
| P4 champion | 1–4 | 1–3 | |
| P5 legend | 1–5 | 1–4 | |

**T-16-19 The templates** (`data/companions.yaml#companions`; lines at every band of the range are computed
there by `16-gen_data16.py`). Line shown at the template's lowest band. Wages are 08's `economy.yaml#wages`.

| Template | Family | Kinds | Bands | Line at lowest band (attack · Guard · Vitality · reduction) | Knacks (signature) | Roles | Wage / price |
|---|---|---|---|---|---|---|---|
| `cmp.porter` porter or torchbearer | non-combatant | hire, comp, foll, cohort | 1–2 | +2 · 11 · 6 · 0 | — (steadfast); carry 10 | lookout | 7/wk |
| `cmp.guide` | non-combatant | hire, comp, foll, cohort | 1–3 | +1 · 11 · 6 · 1 | trained: navigation (forager) | navigator, lookout, scout | 10/wk |
| `cmp.camp_hand` cook or groom | non-combatant | hire, comp, foll, cohort | 1–2 | +1 · 11 · 6 · 0 | quartermaster (trained) | quartermaster, lookout | 10/wk |
| `cmp.soldier` | fighter | hire, comp, foll, cohort | 1–4 | +2 · 12 · 6 · 2 | shieldbearer (bodyguard) | lookout | 14/wk |
| `cmp.archer` | shooter | hire, comp, foll, cohort | 1–4 | +2 · 12 · 6 · 1 | — (keen eyes) | lookout, scout | 14/wk |
| `cmp.scout` | skirmisher | hire, comp, foll, cohort | 1–4 | +2 · 12 · 6 · 1 | trained: tracking, stealth (keen eyes) | scout, lookout, forager, navigator | 14/wk |
| `cmp.boatman` | skirmisher | hire, comp, foll, cohort | 1–3 | +2 · 12 · 6 · 0 | trained: seafaring (steadfast) | navigator, lookout | 10/wk |
| `cmp.healer` | non-combatant | hire, comp, foll, cohort | 1–3 | +0 · 11 · 6 · 0 | healer (steadfast) | lookout, forager | 21/wk |
| `cmp.locksmith` | skirmisher | hire, comp, foll, cohort | 1–3 | +4 · 14 · 6 · 1 | trained: thievery (loyal) | scout, lookout | 21/wk |
| `cmp.hedge_witch` | caster | hire, comp, foll, cohort | 1–3 | +0 · 11 · 6 · 0; `ab.evil_eye` | trained: hexcraft (healer) | forager, lookout | 21/wk |
| `cmp.sapper` | non-combatant | hire, comp, foll, cohort | 1–3 | +2 · 11 · 6 · 1 | trained: engineering (steadfast) | lookout | 21/wk |
| `cmp.veteran` sergeant | fighter | hire, comp, foll, cohort | 2–4 | +5 · 14 · 12 · 2 | rally, steadfast (bodyguard) | lookout, navigator | 50/wk + ½ share |
| `cmp.journeyman_mage` | caster | hire, comp, foll, cohort | 2–4 | +3 · 13 · 12 · 0; `ab.flame_lance`, `ab.spell_ward` | trained: arcane fire (steadfast) | lookout | 50/wk + ½ share |
| `cmp.champion` | fighter | hire, comp, foll, cohort | 3–5 | +9 · 17 · 16 · 3 | bodyguard, steadfast (rally) | lookout | 150/wk + share; a thread |
| `cmp.sworn_sword` | fighter | comp, foll | 2–4 | +5 · 14 · 12 · 2 | shieldbearer, steadfast (bodyguard); value loyalty +1 | lookout | keep |
| `cmp.thief` | skirmisher | comp, hire, foll | 1–4 | +4 · 14 · 6 · 1 | trained: thievery (loyal) | scout, lookout | 21/wk or keep |
| `cmp.acolyte` (protégé) | caster | comp, foll | 1–4 [verification: V2c-010] | +0 · 11 · 6 · 1; `ab.mend_flesh` | trained: divine healing (healer); value piety +1 | lookout | keep |
| `cmp.minstrel` | non-combatant | comp, hire, foll | 1–3 | +2 · 12 · 6 · 0; `ab.stirring_song` | trained: performance (rally) | lookout | 10/wk or keep |
| `cmp.sage` | non-combatant | comp, hire, foll | 1–3 | −2 · 10 · 6 · 0 | trained: history (trained) | navigator | 21/wk or keep |
| `cmp.squire` (protégé) | fighter | comp, foll | 1–4 | +2 · 11 · 6 · 1 | quartermaster (shieldbearer) | lookout, quartermaster | keep |
| `cmp.apprentice` (protégé) | non-combatant | comp, foll | 1–4 | +0 · 11 · 6 · 0 | quartermaster (trained) | lookout, quartermaster | keep |
| `cmp.zealot` | fighter | foll | 1–3 | +2 · 11 · 6 · 1 | steadfast (loyal); value piety +1 | lookout | keep |
| `cmp.militia` | fighter | foll, cohort, hire | 1–2 | +1 · 11 · 6 · 1 | — (steadfast) | lookout | 7/wk or keep |
| `cmp.hound` | war beast | beast | 1–2 | +4 / +4 grapple · 12 · 6 · 0 | keen nose, sentinel (war-trained) | lookout | 15 |
| `cmp.war_hound` | war beast | beast | 2–3 | +7 · 15 · 12 · 1 (at band 2) | war-trained, keen nose (bodyguard) | lookout | 60 |
| `cmp.hawk` | beast | beast | 1–2 | +4 · 14 · 3 · 0 | keen eyes (signs) | lookout | 40 |
| `cmp.wolf_bonded` | war beast | beast | 2–4 | +7 · 17 · 12 · 1 | keen nose, war-trained (sentinel) | lookout, scout | by bond |
| `cmp.bear_bonded` | war beast | beast | 3–4 | +9 · 15 · 17 · 1 | war-trained (sentinel); carry 6 | lookout | by bond |
| `cmp.familiar` | beast | bound, beast | 1 | +4 · 14 · 3 · 0 | keen eyes (sentinel) | lookout | by rite |
| `cmp.mount_*` (donkey, pony, mule, riding horse, draft horse, courser, destrier) | mount | beast | 1–3 by kind | e.g. riding horse +4 kick · 11 · 9 · 0; destrier +9 · 15 · 17 · 1 | pack beast; courser and destrier war-trained | — | 08.10.1 |
| `cmp.bound_servant`, `cmp.bound_dead`, `cmp.bound_automaton` | bound | bound | the working's | e.g. raised dead +2 · 10 · 6 · 1 | — | lookout (servant) | the working (05) |
| `cmp.from_archetype` | by role | any | the creature's | the archetype's line (PR-16-3) | its kept powers | lookout | — |

**T-16-20 Follower templates by the calling's key branch** (`data/companions.yaml#follower_templates`).

| Calling key | martial | guile | wilds | lore | arcane | divine | primal | influence | craft | an oath calling |
|---|---|---|---|---|---|---|---|---|---|---|
| Follower | sworn sword | thief | scout | sage | apprentice | acolyte | hedge-witch | minstrel | apprentice | zealot |

**T-16-21 Companions and the advisory** (`16-companion-sim.py`, 3,000 fights a row, chapter 09's extended model
with adversary Fend; the PC's T-06-12 line; one command per PC turn on the PC's target, *guard me* intercepts
while the ally is not bloodied; output `16-companion-sim-output.txt`). Word shift against no ally, over the 16
shapes of the matrix that span trivial-to-lethal at every band (positive = gentler):

| Configuration | Shift 0 / 1 / 2 / 3 / 4 words (count of 16) | Mean | Max |
|---|---|---|---|
| one ally of the PC's own band, commanded | 2 / 10 / 4 / 0 / 0 | 1.12 | **2** |
| one capped ally (band − 1), guarding only | 4 / 12 / 0 | 0.75 | **1** |
| one capped ally, commanded each turn | 5 / 11 / 0 | 0.69 | **1** |
| two capped allies, one commanded | 2 / 8 / 6 | 1.25 | 2 |
| two capped allies, both commanded | 3 / 8 / 5 | 1.12 | 2 |
| three capped allies, two commanded | 0 / 8 / 6 / 2 | 1.62 | 3 |
| four capped allies, two commanded | 0 / 4 / 9 / 2 / 1 | 2.00 | 4 |
| a cohort of four capped members, commanded | 1 / 4 / 10 / 1 | 1.69 | 3 |

*One capped ally, commanded, shape by shape* (win% / Staggered%, no ally → with ally): P1 vs 4 T1 fair 86/32 →
easy 95/12 · P1 vs 6 T1 hard 41/68 → hard 61/49 · P1 vs 2 T2 hard 50/68 → hard 75/39 · P1 vs a T1 mob of 8 hard
84/57 → fair 93/29 · P2 vs 2 T2 fair 90/23 → easy 96/9 · P2 vs 3 T2 lethal 33/84 → hard 48/70 · P2 vs T3 lethal
38/89 → hard 54/77 · P2 vs a T2 mob of 4 hard 43/75 → hard 61/55 · P3 vs 2 T3 hard 62/59 → hard 80/36 · P3 vs T4
hard 65/70 → hard 78/52 · P3 vs 4 T2 easy 99/3 → trivial 99/1 · P4 vs T4 fair 88/42 → easy 99/8 · P4 vs 2 T3
fair 89/27 → easy 99/5 · P4 vs 3 T3 lethal 32/86 → hard 69/52 · P5 vs T5 hard 81/56 → fair 94/26 · P5 vs 2 T4
fair 90/29 → easy 98/9. The ally is felled (Down or bleeding) in 0–42% of these fights (84% against a mob of
eight, where it is a T1 porter-grade body taking hits for a novice): companions pay for what they give.
Reading: the band cap is what makes 09's "one word gentler" true for one ally; the hard exception (hard stays
hard when the no-ally win is below 75) matches all seven hard shapes; larger retinues are under-credited,
which errs toward caution (16.7.11).

**T-16-22 Loyalty pacing** (`16-loyalty-sim.py`, 4,000 runs a profile; 5 scenes a session, 3 sessions a week,
a venture every 3 sessions; output `16-loyalty-sim-output.txt`).

| PC profile (toward this ally's two values) | Median sessions to the first standing change | Standing after 6 sessions | After 12 | After 24 | Wary or worse by 24 |
|---|---|---|---|---|---|
| aligned (honors them often, rarely affronts) | 3 | Warm 11%, Friendly 89% | Friendly 100% | Friendly 99% | 0% |
| indifferent (both ways, now and then) | 5 | Wary 2%, Neutral 25%, Warm 68%, Friendly 5% | Neutral 5%, Warm 37%, Friendly 57% | Warm 21%, Friendly 79% | 3% |
| opposed (affronts them often) | 3 | Hostile 3%, Unfriendly 34%, Wary 46%, Neutral 17% | Hostile 33%, Unfriendly 42%, Wary 21% | Hostile 74% | 100% |
(The model has no counsel heeded, amends, rescues or thread completions, all of which move standing toward the
PC; it is the floor of a player who never works the relationship.)

---

## Worked examples

All examples follow Wren (00's continuous character; *illustrative sheet, ch.02 owns creation*): Might +1,
Agility +3, Endurance +1, Wits +2, Intellect 0, **Presence 0**, Resolve −1; competence floor +1, archery +2,
tracking +2; Vitality 13; Guard 14 (10 + Agility 3 + the floor on her spear's tag); spear Strike +4 (S2),
shortbow +5 (S2). Her **retinue cap** is `clamp(2 + 0, 1, 6)` = **2**. Numbers chapter 16 owns are exact;
chapter 09's adversary lines are the standard lines of T-09-3.

**Brack** is her mastiff, raised from a pup (a creation bond animal, 16.3.5: Friendly, no frame):
`cmp.hound`, own band 1, serving band 1. Line (PR-16-2 at band 1): bite +4 (Might apex +3 + `c_b` +1), S2;
drag down (Grapple) +4; Guard 12 (10 + Agility high +1 + `c_b` +1); Vitality 6; reduction 0; knacks keen nose,
sentinel; family `war_beast` (default order *harry that one*).

### WE-16-1 Recruiting a companion: Oda Venn

*Situation.* Ashford, spring. Oda Venn, a young poacher, has met Wren twice (recurring depth: want "find my
brother Tam", taken by the Salt Guild's press-gang — Wren heard it as a rumor; fear the reeve; voice terse,
habit "calls everyone by their trade"; refusal *will not harm a child*). Her reaction roll on first meeting was
2d6 = 7: **Neutral**. Wren (still P1) says: "Come with me to Grey Keep. If Tam is anywhere, he's in their
ledgers there — and I'll have you home by midsummer, with him or without."

**The gate (PR-16-1, 16.3.1).** Mind: sapient. Tongue: shared. **Band:** Oda's own band 1 ≤ Wren's power
band 1 ✓; she would serve at `band_cap = max(1, 1 − 1)` = 1. **Places:** Brack 1 + Oda 1 = 2 ≤ cap 2 ✓.
Refusal: *will not harm a child* — not covered.

**Size `[J:rung]` (T-16-10).** A season away from a home she can return to (her father's cottage) → **R3**.
**Terms `[J:flag]`.** WANT: the journey serves her recorded want "find Tam" (want id cited; the engine checks
the sealed record) → true. OBLIGATION: "home by midsummer" is written as a commitment (kind promise, due at the
summer boundary) before the roll, and Oda is Wary or better → true. Effective size R3 − 2 = **R1**.
**Certainty (15.3.10).** The certainty size counts one term only: R3 − 1 = R2, above Neutral's certain range
→ **not certain**, a roll at the effective R1 [revision: I-048]: DC = 10 + Oda's Resolve 0 + standing 0 + R1 +0
= **10**; Wren's Talk +1 needs 9: **60%**. d20 = 13 → 14 vs 10 → **success**: she comes. (With one term less
the roll would be at DC 12; with neither, G4: the boundary pair.)

*Boundary pair.*
- With the want term only: effective **R2** = Neutral's ceiling → a roll: DC = 10 + Oda's Resolve 0 + standing
  0 + R2 +2 = **12**; Wren's Talk +1 (Presence 0 + floor) needs 11: **50%**.
- With no term at all: R3 is one rung above the ceiling with **no** term → G4 for the intent; in her voice:
  "And why would I go anywhere with you?" — the redirect (15.3.4): a term, or reading what she wants (15.6.1).
- Had Oda been a veteran forester of band 2, test 3 fails (own band 2 > power band 1): she would not follow a
  novice; she might travel with Wren as an **escort** on her own lead (16.7.12).
*Non-example.* "I'll pay her eight coins to come" — Payment makes her a **hireling** (16.3.4): the frame becomes
16.3.3 with a contract, a wage and a duty, and she follows for pay, not for Tam.

**Writes.** `ally_kind: companion`; `joining: {kind: want, ref: want.oda.find_tam}`; template `cmp.scout`; own
band 1, serving band 1; line: shortbow +2 (Agility high +1 + archery `c_b` +1), knife +1 (S1), Guard 12,
Vitality 6, reduction 1 (leather); knack `kn.trained` (wilds tracking, guile stealth); default order *stay
back*; roles scout, lookout, forager, navigator. Principal depth (12.11.1): a secret (Oracle Even, d100 62 →
yes → sealed with its gate), two more ranked wants, ties. **Drives (PR-16-4):** d10 = 1 → `conduct.mercy`, d6 =
4 → +1; d10 = 4 → `conduct.loyalty`, d6 = 2 → +1; want: find Tam; refusal: will not harm a child — all sealed.
Clocks: `clk.16.regard.oda` 0/6 and `clk.16.grievance.oda` 0/6, sensed. **Personal thread** (16.12.1) "Tam in
the salt pans", sealed, three clue placements (the press-gang's ledger at Grey Keep; the bargeman who carried
the prisoners; the foreman at the pans), fallback "a letter in Tam's hand reaches Ashford" — **open** at once,
because she joined for it (16.12.2). The codex shows Oda's kind, line, order and roles; her standing (Neutral)
is available; her drives are not yet known.

### WE-16-2 A fight: two commands, one command more, and one reaction

*Situation.* The Salt Road, afternoon. Four bandits (T1 standard: attack +2, Guard 12, Vitality 5, S2; no
reaction; nerve skittish, clock 4; disposition `rob`, no lethal context). Two step out to engage Wren (A, B);
two hang back at `band.near` (C, D). Brack is at Wren's heel; Oda is at `band.near` behind a cart.

**Advisory (09.6; 16.7.11).** P1 vs four T1: **fair** (86 / 31). One able ally — Brack, Friendly — makes it one
gentler: **easy**. (Oda, Neutral and on no contract, is not "able" for this count; one is enough.) No lethal
context: nobody can die here, Wren's companions included.
**Orders at `conflict_start` (16.7.3).** Brack: *harry that one* (his family's default), on A. Oda: *stay back*.

**Round 1 — Wren's turn (three actions).**
1. **Command Brack** (1 action): "Brack — to me!" — standing order *guard me*. Hearing: within `band.near` by
   voice ✓. Will: Friendly accepts *guard me* while not bloodied ✓. Brack keeps to Wren's group.
2. **Command Oda** (1 action): "Oda, the one on the left!" — a Strike with her shortbow at C (`band.near`).
   Will (16.7.2): she holds a bow (G1 Strike); stakes **Risky** (a miss draws C's friend's attention: a cost at
   S2 on her); Neutral accepts Risky ✓; no refusal crossed. OFFER (her numbers): +2 vs Guard 12 → needs 10,
   **55%**. Committed. d20 = 14 → 16: **success** → S2 = 3 harm → C 5 → 2, bloodied (morale +1: 1/4).
3. **Wren strikes A** with her spear: +4 vs 12 → needs 8 (65%). d20 = 11 → 15: success → 3 harm → A 5 → 2,
   bloodied (morale 2/4).

**Bandits' turns.** A (engaged with Wren, harmed by her) attacks Wren twice. First: +2, Wren's Fend −2 → +0 vs
Guard 14: d20 = 17 → **hit**, S2 = 3 → **Brack's reaction: Intercept** (*guard me*, 06.6.7): the hit is his —
3 harm, reduction 0 → Brack 6 → **3**, bloodied. Second: +2 −2 (repetition) vs 14: d20 = 6 → miss. B attacks
Wren: +2 vs 14 (her Fend is spent): d20 = 9 → miss; second +0: d20 = 15 → hit → 3 → Wren 13 → 10. C, harmed
most by Oda, spends both actions closing to her and engages; D closes on Wren.

**Round 2 — Wren's turn.**
- *A reaction that no longer comes.* Brack is bloodied (3 of 6). At **Friendly** his *guard me* Intercept is
  available only while he is not bloodied (T-16-7); his reaction this round is Fend. (Devoted, he would still
  take the hit; with `kn.bodyguard`, so would a Friendly ally.)
1. **Command Brack** (1 action): bite A. +4 vs 12 → needs 8: d20 = 13 → 17, success → 3 → A **defeated**
   (morale 3/4). His own repetition window: this is his first attack this PC turn (0).
2. **Wren strikes B:** +4 vs 12: d20 = 8 → 12, success → B 5 → 2, bloodied → morale **4/4: the bandits break**
   (06.11.5). B and D run; C, cornered by the cart with Oda, throws down his knife and kneels.
3. Wren tells Oda to let C go and waves him off down the road (free: a few words; it costs her the reeve's
   bounty on him). The deed resolves as **`conduct.mercy` +1** (03: sparing a defeated foe at a cost), and Oda
   is a witness → **T-16-8 R1** fires: `clk.16.regard.oda` 0 → **1/6** (stirring). The narrator renders one
   omen: *"Oda lets out a breath she didn't know she was holding, and lowers the bow."* Oda's value
   `conduct.mercy +1` is now known to the player (16.5.6 item 1).

*Count.* Brack was commanded twice (an order; a bite) and reacted once (the Intercept); Oda was commanded
once. No ally took an action of its own: every beat was one of Wren's three (INV-11).
*Non-example.* "Brack bites, Oda shoots, and I stab three times" — five beats in a turn of three; the player may
have any three of them (06.14.2's own non-example).
*Evidence.* Oda's shot is her own act (03.2.6) and records nothing (she is not a protégé); Brack's bite records
nothing; Wren's two Commands are hers (`influence.command.directing`, 03's significance permitting).

### WE-16-3 A loyalty drop and a confrontation

*Situation.* Weeks later. Oda stands at **Warm** (a regard completion in the second week). The search for Tam
goes badly, and Wren cuts corners. Each line is one T-16-8 tick with its cited id and its omen (T-16-16):

| # | Event (cited) | Source | Grievance | Omen rendered |
|---|---|---|---|---|
| 1 | Wren told Oda "Tam isn't on the pans' rolls" (lie record `lie.0031`) to keep her from rushing in; two days later Oda reads the roll herself (exposure, 15.5.5) | G6 | +2 → 2/6 (stirring) | *She says nothing at supper and eats apart.* |
| 2 | `week` boundary in Saltmouth: Oda's keep (4 coins) unpaid — Wren is short (`upkeep.oda.unpaid`) | G4 | +1 → 3/6 (building) | *"You didn't pay our board, Wren."* |
| 3 | Wren declares "I break the clerk's fingers until he talks." **Counsel** at OFFER (16.5.7): AFFRONT true (needless suffering of a helpless captive: mercy −; Oda's value is mercy +1) → *"He's a clerk. Not like this."* Wren commits; the beat resolves; 03 records `conduct.mercy −1` with Oda as witness | G1 | +1 → 4/6 (building) | *She walks out of the cellar before he starts to scream.* |
| 4 | At the ford Oda is knocked Down (a cudgel, not lethal); Wren chases the clerk's runner and leaves her in the shallows until the scene ends (`down`, 07.12.1; no tend) | G7 | +1 → 5/6 (**imminent**) | the **ultimatum**: *"Leave me lying in the mud once more and I walk."* |
| 5 | At the pans a guard yields; Wren declares she cuts him down. Counsel: *"He's yielded, Wren!"* Committed; resolved; `conduct.mercy −1`, witnessed | G1 | +1 → **6/6: complete** | — |

**Completion (PR-16-5).** `eff.15.standing_step −1` at once: Oda **Warm → Neutral**; the clock resets to 0. She
now refuses *guard me* (Neutral, T-16-7) and any commanded beat above Risky; she does not yet mean to leave
(only Wary starts the departure clock).

**The confrontation (16.5.9; PR-16-6).** The first calm scene is the common room of the inn at Saltmouth. Oda
names the five things, in her words: the lie about the rolls, the board, the clerk's hands, the ford, the guard
on his knees. Wren answers: she counts four coins onto the table — the board she owed — and says she was wrong
about the guard. `[J:flag]` *Does the method address a named source?* The coin is the unpaid keep's own fact
(`upkeep.oda.unpaid`) → **true**. **Amends:** a win-over (15.4.2) against Oda's Resolve defense at her new
standing: DC = 10 + Resolve 0 + Neutral 0 + R2 +2 = **12**; Wren +1 → needs 11, **50%** (OFFER shown).
d20 = 13 → 14: **success** → `eff.15.standing_step +1`: back to **Warm** (never above the rung she held). Wren
also binds herself: "No more prisoners harmed" — an Obligation written as a promise with Oda (kept → +1 at a
later point; broken → `betrayed`, −3: Warm to Unfriendly, and she leaves at the next safe scene's end).

*Boundary pair.*
- d20 = 7 → 8: **failure** → Oda stays **Neutral**. Nothing else moves; she still travels with Wren, but the
  next completed grievance clock would make her **Wary** and start the public **departure clock** (4 days,
  16.6.2) — the second and third warnings of 16.6.2's three.
- Wren ignores the confrontation (pays nothing, walks out) → grievance +1 at once (1/6), and Oda stays Neutral.
*Non-example.* "I tell Oda she's like a sister to me" as the amends — a speech that names no source → the flag is
false. It is then an ordinary win-over (15.4.2) under 15.1.7's caps: legal only if no small step was taken
with her this week, and it answers nothing she raised; the confrontation still counts as answered (Wren spoke
to it), so no extra grievance, but nothing is restored by right.

### WE-16-4 A hireling's contract ends

*Situation.* Wren is now **P2** (power band 2; `band_cap` still 1). She posts Oda at Ashford for a month to
nurse her father (16.2.3: 0 places while posted; her keep still paid) and needs a sword for the Salt Road toll,
where bandits hold the bridge (a fight expected; no lethal context recorded).

**Finding hands (16.3.2).** `dt.recruit` in Ashford (a town: Moderate, DC 15): Wren +1 → needs 14 (35%); d20 =
17 → 18, success, Standard reach → **2 candidates**. Role: soldier. Own band = min(hire band 2, town 2, Wren's
P2) = **2**. One is Garrick: reaction roll 2d6 = 7 → **Neutral**; quirk (`tbl.16.hire_quirk` d12 = 3)
*scarred: knows what a fight costs*.

**Hire (16.3.3).** HAZARD `[J:rung]`: a fight expected, no recorded lethal context → **R3**. TERMS: a week's wage
in advance (14 coins) → one term → effective **R2** = Neutral's ceiling → a roll. As a candidate he is an NPC at
his own band 2: DC = 10 + Resolve (mid at T2: +1) + 0 + R2 +2 = **13**; Wren +1 → needs 12, **45%**. d20 = 15 →
16: hired. **Contract:** duty "soldier: clear the toll bridge", wage 14/week, hazard R3, term **4 weeks**, no
share. Drives: d10 3 → courage, d6 2 → +1; d10 5 → generosity, d6 6 → **−1** (he respects a tight purse).
**Line at serving band 1** (PR-16-2): sword +2 (Might high +1 + `c_b` +1), S2; Guard 12 (10 + Agility mid 0 +
`c_b` 1 + shield 1); Vitality 6; reduction 2 (mail); knack `kn.shieldbearer` (Wren's Guard 14 → **15** while he
guards her). His own band (2) is *available*: "he was a sergeant's man once"; when Wren reaches P3, he serves at
band 2 (sword +5, Guard 14, Vitality 12) [verification: V2b-027].

**Four weeks** (regard ticks): Wren holds the bridge against the wolves at night (courage +1, witnessed: R1,
1/6); the toll fight is advised *hard* and both stand at the end (R3 ★, 2/6); Wren charges the bandit captain
(R1, 3/6 — another scene); the venture ends at Ashford (R5, 4/6); she gives the toll money she took back to the
robbed carters (`conduct.generosity +1` — against his pole: **G1**, grievance 1/6, omen *"he watches the coin go
and says nothing"*); she gives him a 5-coin bonus (≥ 1 Unit of a common soldier's poor lifestyle, 4: R4, 5/6);
another courageous deed (R1, **6/6**) → standing **Neutral → Warm** (the weekly cap allows it). His grievance
decays to 0 at the next week with no tick.

**The term ends** (`h.16.contract_term`, the fourth `week`). At the haven: paid off — the four weeks were paid on
time. Wren may **renew**: a longer term with someone who knows her is one rung lower than a new hire (16.14.2):
R3 → R2, minus the wage term → **R1** at Warm → **certain** (15.3.10). She renews for four more weeks, no roll.
*Boundary pair.*
- Had Garrick reached **Friendly** with four weeks served, he would **offer** to stay on as a companion (16.14.4
  item 3): keep (4 a week) instead of wages, his contract hazard no longer binding, only his rung.
- Had Wren been unable to pay the fourth week: G4 **+2** (hireling) at that boundary; unpaid again at the next,
  he leaves at once (`unpaid`), holding a 28-coin debt (15's `owed`).
*Non-example.* "He's under contract — he follows me into the wight's barrow." The barrow's wights carry a lethal
context; his contract's hazard is R3 (Dire, not lethal) and Warm accepts Dire, not lethal → every lethal-frame
command there is **refused** (16.7.2), and bringing him into that danger ticks G3 at each scene's end. The road
in is a renegotiation at R4 (hazard pay: double wage, a second term).

### WE-16-5 A companion falls

*Situation.* Summer, under Grey Keep. Wren (P2) with Oda (back from Ashford, **Warm**, serving band 1: Vitality 6,
Guard 12, reduction 1) and Brack. Ghouls (T2: bite +5, S2; **lethal context recorded** when the scene opened —
the lethal warning said, by 16.7.11: *"The ghouls kill. They will kill Oda or Brack as surely as you."* The
advisory also named the risk: *"a single bite could drop Oda."*).

1. Oda shot the first ghoul; by 06.9.3 it goes for her. Bite 1: +5, Oda's Fend −2 → +3 vs 12 → needs 9: d20 =
   **20** → critical success → S3 = 5 − reduction 1 = 4 → Oda 6 → 2. Bite 2: +3 (repetition −2) vs 12: d20 = 13 →
   16 hit → S2 = 3 − 1 = 2 → **0**. The event is lethal (Key 1 on record) → **bleeding out** (07.12.1):
   `clk.bleeding_out.oda` **0/4**, public: *"Oda is down and bleeding. Four rounds."* The advisory recomputes (a
   companion fell, 09.6.5), and Oda's fall ticks the ghouls' morale clock **down** by one (06.11.3: "a companion
   of the PC is defeated: −1"). End of round: **1/4**.
2. Wren's turn: Move near → close (1), close → engaged at Oda's side (1); **first aid** (`verb.handle`, Agility
   +3 + floor +1 = +4, no kit) against **Moderate (15)** → needs 11, 50%: d20 = 9 → 13, failure. Brack is a hound:
   he cannot tend her (T-16-13: a beast may not Handle). The ghoul bites Oda again — a further lethal harm event
   → **2/4** (07.12.1). End of round: **3/4**.
3. Wren's turn: first aid again (one attempt a round, 07's edge case): d20 = 14 → 18: **stabilized**; the clock
   is voided.
**After (16.9.4).** Oda wakes after a long rest with a Heavy body wound on a 4-segment recovery clock and refuses
attack-trait commands until it heals (07.12.2). Wren saved her from death by her own hand → 15's
`helped (rescue)`: **+2** standing, a deed of weight, cap Devoted → **Warm → Devoted**. (No regard tick: the rescue
is 15's source, not the clock's.) The chronicle takes a line.

*The other branch.* Round 3's first aid: d20 = 6 → 10, failure. End of round: **4/4 → Oda dies.** PR-16-12:
`setback.companion_dead` (12.7.5: the director's recovery window); Wren's **dread check at S3** (Endure with
Resolve −1 against Hard, 20: only a natural 20 succeeds, 5%; d20 = 11 → dread +2, by 07.11.2); the ghouls' morale
−1; a chronicle line, *"Oda Venn died under Grey Keep, looking for her brother."* Her place frees at the scene's
end; her bow and kit lie with her; her own things belong to her father in Ashford (`kin_of.oda`); no wages were
owed (a companion). The out-of-fiction line offers a **vow**: *"Swear to find Tam for her?"* — accepted, it is a
vow thread (11; keeping it is a fate trigger, 01), and her personal thread becomes "Tam in the salt pans, for
Oda". Brack, a beast, witnessed it: beasts have no G10 and no dread; his grief is shown, not counted.
*Tempting non-examples.* "The critical bite kills her outright" — no: a lethal harm event at 0 starts the clock;
only the clock's completion kills an ally (16.9.2). "I spend my fate to save her" — fate has no ally use; allies
have no reprieve (07.12.1). "Brack drags her clear" — a hound may not carry a body (T-16-13: carry is for large
beasts); a commanded *person* could.

### WE-16-6 A knight holds the bridge (an escort's held line)

*Situation.* Wren (P2) rides to the Ashford bridge with Ser Aldric, a knight (own band **3** > her power band 2:
he will not join her retinue; he rides with her as an **escort** on his own lead, 16.7.12). Raiders: a leader
(T2), an archer (T1) and a mob of four (T1). Aldric's objective is the bridge.
**Held foes `[J:enum]`** (citing his stated objective): the mob of four on the bridge. They leave Wren's fight;
the advisory is computed for Wren and Brack against the leader and the archer.
**`clk.16.held_line.bridge`**, tug, 6 segments, **3/6**, public. Aldric's fortune check each round: his best base
attack (a band-3 person, blade: high +4 + `c_b` +3 = **+7**) against the mob's Guard 12 **+2** (a mob of four:
one numbers step) = **14** → needs 7: critical success on d20 17+ (20%), success 7–16 (50%), failure 2–6 (25%),
critical failure on a 1 (5%); expected +0.55 a round (the line holds and wins 90% of the time: `16-heldline-sim-output.txt`).
- Round 1: d20 12 → 19, success → **4/6**.
- Round 2: d20 3 → 10, failure → **3/6** — rendered: *"Aldric gives a step on the planks."*
- Round 3: d20 18 → 25, critical success → **5/6**.
- Round 4: d20 9 → 16, success → **6/6**: the raiders on the bridge break and run.
*Boundary.* Had the clock reached **0**, the four would have entered Wren's fight at the next round's start,
the advisory recomputed and shown (P2 against a T2 leader, a T1 archer and a T1 mob of four is far worse).
Wren could have shored the line at any time: a beat of hers against the held mob adds its delivered reach.
*Non-example.* "Aldric charges the leader on his own turn." An escort has no turn; his part is the line (16.7.12).
To have him strike at Wren's word, he would have to follow her — and he does not.

### WE-16-7 Roles on the road

*Situation.* Three days to Grey Keep at slow pace through wild country (10's danger rating `wild`). The
retinue on offer: Oda, Garrick, Hob (a `cmp.camp_hand` hired at R2 for the road, 10/week), Brack, and a mule (`cmp.mount_mule`,
pack beast, 0 places, 30 load). Retinue places: Oda 1 + Garrick 1 + Brack 1 + Hob 1 = 4 against Wren's cap of 2,
so she chooses: Garrick's contract has ended (paid off, 16.14.4) and Brack is posted at Ashford with Oda's
father (16.2.3); Oda and Hob ride with her — *a full retinue is a choice made every week*.
**Standing roles (16.8.3):** the player names Wren navigator, Oda scout, and Hob **quartermaster** (his
`kn.quartermaster`).
- Day 1, afternoon watch: the d12 shows **D** (depletion) → `tbl.10.depletion` d6 = 1: *one supply spoils* — Hob
  prevents it (once a day): the face counts as a lull, without the lull's progress point. Evidence for Hob: none
  (he is not tracked).
- Day 2, night watch: the rota — Oda keeps the evening watch as lookout, Hob the night (each ally at most two
  watches a day). An encounter arrives (E face): a lookout is posted → nobody is `cond.surprised`, and the
  sleepers are woken in time (10.5.1).
- Day 3: an E face while travelling: Oda, scouting, perceives first (the others are `unaware` unless their notice
  beats her stored Sneak) and starts the encounter at **`band.far`** from the party — alone out there. Wren may
  slip the party away without a beat, or ride to her.
- Supply: consumers Wren, Oda, Hob = 3 a day (the mule grazes: spring, wild woodland); the OFFER of the journey
  showed 9 needed against 12 carried.

---

## Edge cases & adaptation anchors

**Reaching for an anchor.** When a player asks an ally to do something no rule here names, reach in this order:
(1) is it a **command or a request** to an ally? → 16.7.2's will test (capability, stakes, line, order) and
06.14.2 in conflict or 16.8.1 outside; (2) does it change **who follows** or **why**? → recruitment (16.3.1's
gate, T-16-9/T-16-10's sizes) or a breaking point (16.6); (3) does it change **how the ally feels**? → T-16-8's
closed sources, or 15.1.5's (a rescue, a gift, a betrayal); nothing else; (4) is it about **others fighting
beside the PC** without joining? → 16.7.12 (led, or a held line); (5) **time**? → 16.8.2. The two-change limit
applies (00.2.7).

**Anchor rules in this chapter** (knobs from T-00-20; defaults → allowed deltas):

| Anchor | Intent verbs | Knobs |
|---|---|---|
| 16.3.3 Hire | hire, engage, pay to come, sign on | `time_cost` (a day per Recruit → a watch in free mode); `reach_unit` (candidates → contract weeks on renegotiation) |
| 16.3.9 Recruiting anyone | recruit, win over to my side, take into service, adopt, tame, enlist | `time_cost` (a scene per campaign beat → a week in downtime); `targets` (one person → a group that decides together, joining as a cohort) |
| 16.7.12 Scene allies and held lines | hold the line, cover my back, keep them busy, take the flank, hold the bridge while I | `targets` (which foes are held); `duration` (clock 6 → 4 skirmish, 8 a battle's corner) |
| 06.14.2 Command (06's anchor, read with 16.7.2) | order, send, sic, have an ally do | `action_cost` (1 → 2 for a two-action beat); `targets` (one ally → every ally in a group for one simple beat) |

**Edge cases.**
- **"Oda, follow him and come back tonight."** A separate activity in `free` mode (16.8.2): she acts as the actor
  of a Sneak/Observe beat set (15.9.15 surveillance), with her numbers, alone; her stakes are hers; she reports at
  the stated time. If the venture is lethal-contexted, her WILL (Warm: Dire, not lethal) applies.
- **The PC is captured; the allies are not.** Allies who were not taken act on their rung's contract (T-16-7):
  Devoted ones attempt a rescue (a lead written; the player plays it as the rescue's scenes), Friendly ones wait
  at the last haven for a week and then seek help (a rumor to 11), Warm and below disperse. Nobody acts off-screen
  beyond writing that fact (12.11.8).
- **The PC wants a companion to kill a prisoner.** A command; Will: its refusal (*will not harm a child* only if the
  prisoner is one); stakes Safe; it obeys if its rung accepts — but the deed is the ally's conduct event *and*
  the PC's command is the PC's (03's "an order from the PC"), and G1 fires +2 if it affronts the ally's value.
- **Two allies' values pull opposite ways** (a merciful acolyte and a ruthless sellsword). One deed ticks one's
  regard and the other's grievance: this is designed friction (Mount & Blade's likes and dislikes); keep both by
  doing things both value, or choose.
- **An ally is charmed or dominated by a foe** (`cond.charmed`, 06): it is the condition's, not loyalty's: it
  cannot make attack-trait beats against the charmer and the narrator may not imply betrayal; when the condition
  ends, standing is unchanged (an ally is not to blame for magic).
- **An ally is a werewolf / possessed / a spy (a secret).** Its secret is sealed (12.11.1) with a gate. Acting on it
  is the secret's own rule (a clock, a trigger) written when the secret is generated; until it unseals, the ally
  behaves by this chapter. A spy's reports are 11's faction intelligence, never a narrator's whim.
- **Hiring a whole company.** A cohort is at most six and costs a place per member (16.2.6). Beyond the cap, a
  company is a **holding** or a **rank** (11): it holds a post, it does not follow (16.2.2).
- **A companion's want would be served by betraying the PC** (Tam is held by the faction the PC fights). Want and
  loyalty are separate state: the ally's thread (16.12) and its standing decide; a Friendly ally asks first
  (counsel), a Wary one may act (its departure clock), a Hostile one may sell the PC out (16.6.6 row 3).
- **An ally drinks a potion or reads a scroll.** Items work for allies by 08 (16.4.8), commanded as a beat; a scroll
  needs the ally's license like anyone's.
- **The PC dies with allies present.** 16.16.2; the allies' grief (16.9.5 item 4); a Devoted ally carries the PC's
  last words (11's legacy hook).
- **Swapping a summoned servant in and out every scene.** A scene's bound being takes no place and costs its
  working's Focus (05) each time: the price is the working, which is why it is free of the retinue.
- **"My hound sniffs out the trail while I talk to the innkeeper."** Parallel work in `free` mode (16.8.2): yes; in
  a site's interval: no — it is the party's one significant beat or a Help (16.8.2).
- **Retinue over the cap after a maim lowers Presence** (00.4.3 c). 16.2.1: a week to fix it, then overflow.
- **An ally aims a crossbow at the PC (betrayal row 6, a Hostile ally in a fight).** It Withdraws and leaves;
  betrayal never harms the PC directly (16.6.6). An ally who *attacks* the PC has become an adversary: it is a new
  conflict participant with 09's behavior list, and Key 1 still governs any lethal harm.

## State touched

- **Entities:** allies (kind `companion`, field `ally_kind`), with the fields of 16.1.2; cohort records; follower
  offers (`offer`, 00.6.2); personal threads (11's thread records); `kin_of` facts.
- **Relationships:** `standing_to_pc` of every ally (15's semantics; loyalty), ally-to-ally standing (15.1.8).
- **Clocks (created and owned by 16):** `clk.16.regard.<id>`, `clk.16.grievance.<id>` (sensed, 6),
  `clk.16.departure.<id>` (public countdown, 4), `clk.16.held_line.<id>` (public tug, 4/6/8); 07 creates
  `clk.bleeding_out.<id>` for allies and cohorts.
- **Commitments:** contracts, oaths of service, amends promises, debts to allies or their kin, silence.
- **Facts:** `journey_role` (10's), `joining`, `posted_at`, `departs_at`, `courted_by` (11 writes), `camp.alarm`
  (sentinel), objection records, the shared record (scene ids per ally).
- **Ledgers:** chronicle lines (devotion, death, betrayal, departure), memories (12's), evidence for protégés.
- **Visibility:** per 16.1.3 (shown / available / sensed clocks / sealed drives until learned).
- **Tools used:** `create_entity`, `set_relationship`, `set_fact`, `create_clock`, `tick_clock`, `set_clock`,
  `frame_check`/`roll_check` (allies' beats, held-line fortune checks), `apply_effect`, `apply_harm` (07),
  `update_quantity` (coin, supply), `record_knowledge`, `offer_create`/`offer_resolve`, `roll_table`, `oracle`,
  `chronicle_append`, `codex`.
- **Hooks subscribed:** `on_vitality_threshold` (`kn.rally`), `on_hit_taken` (Intercept, via 06), `on_dying` (16.7.5),
  `on_tag_event` and `on_fact_set` (T-16-8 sources), `on_clock_complete` (regard, grievance, departure, held line).
- **Boundary handlers registered** (`data/boundaries.yaml owner-block 16`): `h.16.retinue_upkeep` (week, 4; reserved by
  00), `h.16.contract_term` (day, 6), `h.16.conflict_orders` (conflict_start, 9), `h.16.follower_offers`
  (reflection, 8), `h.16.season_growth` (season, 8), `h.16.venture_end` (venture_end, 9), `h.16.held_line`
  (round, 7), `h.16.loyalty_record` (scene_end, 9: commits the scene's ticks' omens check and G7's test).
- **Triggers:** `trg.16.band_cap_changed`, `trg.16.betrayal`, `trg.16.confrontation`, `trg.16.departure`.
- **Runtime capabilities:** RC-STORE, RC-SEAL, RC-SCHED, RC-EVAL, RC-RNG, RC-LOG, RC-DATA, RC-QUERY.

## Interface requests

What this chapter needs from, and offers to, the others (beyond 00.17's binding contracts). Every item names
the rule here that depends on it; "integration edit" means a wording change in a finished chapter that this
chapter's rules already assume.

**To 00 (amendments proposed).**
1. Id prefixes `cmp.` (ally templates) and `kn.` (knacks) in 00.16.2.
2. 00.6.2: the entity kind `companion` covers all seven ally kinds, distinguished by the field `ally_kind`
   (16.1.2); the Ally shape extends NPC with 16.1.2's fields.
3. T-00-9: the handlers of `data/boundaries.yaml owner-block 16` (seven added to the reserved
   `h.16.retinue_upkeep`); triggers `trg.16.band_cap_changed`, `trg.16.betrayal`, `trg.16.confrontation`,
   `trg.16.departure`.
4. SCHEMAS.md#companions.yaml: the required keys are kept (`companions` entries with id, template, loyalty,
   command_actions, journey_roles, harm_rules, wage); every other top-level key of the file is optional and
   documented in 16's Tables (the header lists them).
5. Glossary (00.18): **ally**, **retinue**, **retinue place**, **own band**, **serving band**, **band cap**,
   **regard**, **grievance**, **confrontation**, **amends**, **counsel**, **knack**, **cohort**, **scene ally**,
   **escort**, **held line**, **posted**, **protégé**, **drives** (two values, a want, a refusal), **joining**,
   **departure clock**, **loyalty** (an ally's standing toward the PC).

**To 01.** T-16-5 answers the request "companion base modifiers for group actions and Help": an ally's base
modifier is `rung(attribute) + competence (c_b on a trained tag) + edge`; it is a group member like anyone
(01.14.7) and eligible to Help when it could attempt the beat alone (01.14.8). No change to 01 is needed.

**To 03.** (a) Adopt `deed.wilds.survival.provisioning` (`data/tags.yaml`, adopted at integration) and add `quartermaster` to
`evidence.yaml#journey_roles` (→ that tag), as 03 invited ("10/16 may extend"). (b) `tracks_evidence: true` is
set only by protégé templates (16.10.4). (c) Allies are carriers (03.10.2) and the shared record (16.13.2) lists
the scenes each ally witnessed. (d) A silence commitment (16.11.1) is the commitment 03.10.2(c) reads.

**To 04.** (a) A protégé (04's edge case "A companion": one deed seat, no oath seat, tier ≤ 3) — this chapter
adds what its tiers do: own band = tier + 1, competence clamped to `c_b + 1`, picks into a three-ability
partition that replaces beyond three (16.10.4); please confirm no conflict with 04's pick procedure. (b)
Follower offers (16.3.6) read **confirmed** tiers ≥ 2 and their carrier witnesses: `recognition_event` should
carry `confirmed: bool` (or a separate confirmation event at `h.04.season_consolidation`). (c) T-16-17's
staging of V1, V4, V6, V7, V8 and V14 by allies is consistent with `vehicles.yaml` (no change asked).

**To 05.** (a) `rit.beast_bond`'s "at or below your power band" is exactly 16.2.4's who-may-follow test; the
bonded beast then serves at the band cap (no change asked; integration note). (b) `rit.bind_familiar` →
`cmp.familiar` (band 1, 1 place); `eff.summon` templates for servants, raised dead and automatons → `cmp.bound_*`
(16.15.6). (c) Allies cannot hold abilities that dictate choices or summon (16.4.4). (d) Ally Focus is 09's
adversary base by serving band, refilled only at a long rest (16.4.4) — not 05's channels.

**To 06 (integration edits).** (a) 06.14.2's WILL decision is 16.7.2 (rung, contract and oath acceptance;
refusal; allowed order). (b) Default orders at `conflict_start` (`h.16.conflict_orders`, 16.7.3), automatic
*stay back* on losing heart (16.7.4) and automatic *guard me* toward a Dying PC (16.7.5) are engine writes of an
order, costing no action — 06.14.4 lets only a Command set an order; please add "or a chapter-16 rule".
(c) 06.6.7: a **Devoted** ally may Intercept for the PC by its reaction **without** the *guard me* order (T-16-7);
`kn.bodyguard` lets an ally intercept while bloodied. (d) 06's edge case "Three sides": an independent allied
side is resolved as a held line (16.7.12) rather than given turns. (e) `hears: bond` (a bonded beast) perceives
intent at any distance at which the PC could call it. (f) T-06-13's note "one row gentler for a PC with a
companion" is now 09.6.3 as refined by 16.7.11.

**To 07 (integration edits).** (a) Cohorts: every member felled by lethal harm shares one
`clk.bleeding_out.<cohort>`, and one stabilizing beat saves them all (16.2.6). (b) Ally Vitality is 16.4.3's (6 /
12 / 16 / 18 / 20 by band, size multipliers, clamped below the PC's maximum). (c) `h.07.fatigue` applies to an
ally who keeps more than two watches a day (16.8.3). (d) The lethal warning names the allies it threatens, and
the advisory line names any ally a single blow could drop (16.7.11). (e) 16.9.5 extends 07.12.3's death writes
(belongings, kin debts, the vow offer, the others' grief). (f) "Loyalty effects of being left behind or saved"
(07's request) are T-16-8 G7 and 15's rescue (16.9.4).

**To 08.** (a) Prices for trained beasts: hound 15, war hound 60, hunting hawk 40 (T-16-19); please add them as
base items (a `item.conveyance.mount`-like entry with `companion_hint`, or a new `item.goods.beast` tag) or
adopt the template prices. (b) Shares are computed and paid by `h.16.venture_end` (16.14.6); `h.08.upkeep` runs
before `h.16.retinue_upkeep` at `week` phase 4 so a shortfall falls on the PC's lifestyle first. (c) An ally's
attunements count against the PC's limit of five (16.4.8). (d) 08.10.1's "16 owns the check" for non-war mounts
is 16.15.4. (e) Kit qualities in `companions.yaml` use 08's ladder (worn … storied).

**To 09 (amendment proposed to 09.6.3 and PR-09-4).** (a) The companion adjustment applies when at least one
**able** ally is in the fight (16.7.11: conscious; Warm or better, or its contract covers the stakes; serving band
≥ `band_cap(pc)`), at most **one** word for any number of allies; and a **hard** estimate whose estimated win
without allies is **below 75** stays hard (T-16-21: matches all seven hard shapes; one capped ally otherwise
moves every word by exactly one). (b) `cmp.from_archetype` (PR-16-3) reads an archetype's attribute rungs,
trained defenses, evidence tags, attacks, size, pace, `cannot` and role. (c) Allies' band-1 Vitality is 6 (16.4.3)
— an ally line, not an adversary line; 00.3.7's T1 envelope is untouched.

**To 10.** (a) The fifth journey role **quartermaster** (16.8.3; `companions.yaml#journey_roles`): prevents one
depletion face (rows 1–4) a day; please add it to `travel.yaml#roles`. (b) The night rota: at most two watches a
day per ally as a role (16.8.3). (c) Site mode: the party makes one significant beat per interval (16.8.2) —
consistent with 10.13's interval time; please note it there. (d) 10.8.3's "16's check" for a frightened mount is
16.15.4. (e) An ally scout starts encounters at `band.far` (10.5.1, adopted as written).

**To 11.** (a) Personal threads (16.12) are thread records (kind `quest`) with ≥ 3 clue placements and a fallback;
11's register shows them when open. (b) Factions may **court** allies (`courted_by`, sealed, with an omen) as a
World Turn action (16.12.5); `kn.loyal` allies are immune while Neutral or warmer. (c) Reputation content "how the
PC treats their people" from the retinue's departure record (16.11.3). (d) Ranks that grant followers: the count
is 11's; the retinue cap applies (16.3.6). (e) Successor candidates from allies (16.16.1); an ally's standing
toward an heir is its old standing − 1 (16.16.2). (f) Vows offered at an ally's death (16.9.5) are 11's vow
threads. (g) Allies carry deeds to their home scopes (16.11.1) — 11's rumor spread. (h) In a battle (06's edge
case), the allied army's corners near the PC may be run as held lines (16.7.12).

**To 12.** (a) Companions are facets (12.9; adopted) and allies' banter is budgeted (16.13.4). (b) The consistency
rule (16.13.3) belongs in the claim-vs-state check: a narrated ally act with no listed reason is a claim of class
`action` to flag. (c) An ally's personal-thread fallback is a candidate for lead injection (12.8.2). (d) Allies'
memories follow 12.11.7 unchanged; the shared record (16.13.2) is a scene-log query. (e) Ally deaths are setbacks
(12.7.5; adopted).

**To 13 (now the region's seed, 12.16: T-12-16 `ws.req.16_*`) [revision: I-028].** Regional hire roles and quirks (replacing `tbl.16.hire_quirk` where flavor demands), the region's
settlements' tiers (village / town / city, for 16.3.2's band limit), named NPCs who might be recruited (with
own bands), and beasts and mounts available in the region.

**To 14.** Codex views: **Retinue** (each ally: kind, template role, serving and own band in words, line, order,
roles, standing rung, known drives, contract and wages owed, posted status, sensed clocks as existing), **Offers**
(follower offers), **Departures** (public departure clocks), and the Player's Guide section "Companions":
the retinue cap, the band rule, how loyalty is read (omens, counsel, confrontations), and that allies can die
only in a warned, lethal fight after four rounds bleeding.

**To 15 (amendments proposed).** (a) 15.1.5 gains **source 8**: an ally's regard or grievance clock completing
(16.5.3), regard completions counting against 15.1.7's weekly small-source cap unless the cycle held an R3 tick.
(b) 15.1.7 gains one exception: **amends** in a confrontation (16.5.9) restore the step just lost, once per
confrontation, not limited by the win-over's Warm cap. (c) 15.3.5 Payment: in a **hire** (16.3.3) the wage paid
in advance and hazard pay are terms without the price test (the wage is the market price of the work, 08.8.8).
(d) 15.13.14 Recruit presents candidates no higher than the settlement's band and the PC's power band (16.3.2).
(e) Allies' downtime duties (T-16-15) resolve in `h.15.downtime_week`. (f) Silence (16.11.1) is a request sized by
15.3.2.

**Offers from this chapter.** `data/companions.yaml` (40 templates with lines at every band, 15 knacks, all loyalty
tables); `16-gen_data16.py` (validator); `16-companion-sim.py`, `16-loyalty-sim.py`, `16-heldline-sim.py`
(re-runnable when 06/07/09 numbers change); the held line as a general anchor for "others hold something while
I…"; the counsel card as the pattern for any pre-commit warning by an NPC.

## Open empirical questions

Each ships a concrete default in the rules above and names the test that would settle it.

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-16-1 | Is `2 + Presence` the right retinue size for solo play — enough company, not too much for the DM to voice? | 16.2.1 (1–6) | **T-16-RETINUE**: 5 playtest campaigns of 6+ sessions; per session, ally-narration errors flagged by the claim check (target ≤ 1 per ally per session) and the player's rating "my companions feel like people" (≥ 4 of 5); if errors scale faster than the retinue, cut the cap to `1 + Presence` |
| OEQ-16-2 | Do six-segment regard/grievance clocks pace loyalty right? | 16.5.3; T-16-22 | **T-16-LOYAL**: log every tick for 3 allies over 20 sessions; targets — an aligned PC reaches Friendly in 4–10 sessions; every departure was preceded by ≥ 2 rendered warnings (100%); the player could name an ally's two values by session 6 (≥ 80%) |
| OEQ-16-3 | Does "at most one advisory word gentler" under-credit large retinues so much that players ignore the advisory? | 16.7.11 | **T-16-ADV**: re-run `16-companion-sim.py` with 09's final bestiary for 2–4 allies; if real outcomes are two or more words gentler in > 50% of shapes with ≥ 3 able allies, add a second word for three or more able allies when the no-ally win is ≥ 60 |
| OEQ-16-4 | Can the DM call counsel (AFFRONT) reliably before the roll? | 16.5.7 | **T-16-COUNSEL**: 60 declarations against 10 ally drive profiles × 3 independent DM runs; agreement ≥ 85%; false negatives (a grievance tick with no prior counsel) ≤ 10% |
| OEQ-16-5 | Is one significant beat per interval for the party in sites too tight? | 16.8.2 | **T-16-SITE**: 3 dungeon runs with two allies; players' rate of "I want two of us doing things at once" requests and the site's danger-clock pacing against 10's targets; if > 1 such request per interval-hour and pacing is not harmed, allow a second beat per interval at the cost of one extra site check |
| OEQ-16-6 | Is the held line's balance right (62% at equal band)? | 16.7.12 | **T-16-HOLD**: 10 played battles with escorts; the player's sense that the escort "mattered but did not win it for me" (≥ 4 of 5); re-run `16-heldline-sim.py` with 09's final Guards |
| OEQ-16-7 | Does the band cap feel fair in the fiction (veterans serving at the PC's lead)? | 16.2.4 | **T-16-CAP**: player survey after recruiting an ally whose own band exceeds its serving band: "it makes sense that they fight at my level" (≥ 3.5 of 5); if not, voice the cap more explicitly in narration (the veteran "won't risk more for a green captain") rather than change the numbers, which the advisory contract needs |
