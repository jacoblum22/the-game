# 04 — Recognition and Growth

> This chapter is how a character **becomes** something. There are no experience points and no character
> levels. A **calling** (the ruleset's word for class) is never chosen from a menu: it is a label the engine
> derives from the sealed record of what the character actually did (chapter 03), and the only way a character
> grows in power is by a recognized calling deepening through five **tiers**. Eligibility is decided by
> deterministic, Delve-style dual thresholds over a small fixed set of tag keys. The engine then computes a
> **confidence** from five yes/no confirmations and resolves it with a three-valued policy: **grant** (the
> world already treats you as it), **offer** (someone asks, and the player accepts, declines or defers), or
> **abstain** (nothing happens, and at most a seer reads you vaguely). Every recognition is voiced by the
> fiction through one of fourteen **vehicles** (a title people start using, a mentor's question, an order's
> letter, an oath spoken, a power that wakes in a crisis), with a single out-of-fiction marker so the player
> always knows an offer is live and exactly what it costs. A calling hands out **no ability list**: a tier
> grants a competence value, grades in shared training licenses, one of five universal capabilities, **picks**
> into the one shared, tag-gated ability pool of chapter 05, and (for hybrids only) one bounded named composite.
> Everything granted is **provisional** until the character has lived it; callings fold, fork and consolidate
> at telegraphed boundaries so that power is restated and never merely stacked; oath-bound callings can
> **fray**, in three warned stages, and are never lost by surprise.

**Reading this chapter.** Standard format (00.19). *Rules* has eleven parts (04.1–04.11). The machine-readable
companions are `data/callings.yaml` (183 callings and every number), `data/hybrids.yaml` (the 36-pair table),
`data/vehicles.yaml` (V1–V14, prices, readings, marker texts), `data/gen_absorb.yaml` (the absorption
domain), and four contrib fragments (`composites.04`, `licenses.04`, `boundaries.04`, `tags.04`). Data is
canonical for every number and id (00.1.4 line 5). The calibration is in
`rules/_process/simulation/04-recognition-sim.md`. Worked examples follow **Wren** (00's continuous
character) across fifty sessions, then boundary cases with other characters.

---

## Design intent

**Goals served.** Goal 1: whatever the player actually does, in any pillar and at any breadth, can become an
identity with real capability; the player can pursue an identity on purpose (the *Leanings* view and the
seer's reading say what kind of deed is still missing) and is never told "that is not on the list". Goal 2:
the AI DM never decides who the character is. It classifies one staging from at most three the engine
returns, checks one flag when an oath is spoken, and classifies one enum when a power is taken. Every
threshold, score, policy, grant, lapse and revocation is computed by the engine from sealed tallies the
narrator never sees [BRIEF §3; C:P5; C:P13; R4 §9 04 #1–#4].

**What the research forced.**
- *Tally × witness × moment.* Every working hidden-mechanics recognition system separates the hidden
  deterministic tally, the question of who in the world could plausibly notice, and when the fiction stages it
  (Ultima IV's counters, seer and shrine) [R6 §0 #1, R-A1; R2 #1]. Hence 04.3–04.4 (tally and policy), 04.6
  (vehicle and witness), 04.7 (moment and protocol).
- *Delve's dual-tier threshold over low-cardinality keys* [C:P5; R3 04.1, #4], with numbers scaled to this
  game's event rate by simulation and never copied [R3 G-2]. Hence 04.3 and T-04-8.
- *A tally has no confidence unless one is defined* [R2 T-1; R3 T-4; BRIEF A3]. Hence 04.4.2, a definition
  chosen because it is **calibrated**: in simulation a higher score predicts a higher chance that the
  recognition is confirmed by later play (37, 59, 64, 73, 91, 97 in 100 for scores 0–5).
- *Hybrids are named consolidations keyed to branch pairs, reachable below full specialist depth, with an
  original merge trigger that must be simulated* [R3 #5, 04.3, 04.4, 04.9, G-1; Hades' duo table]. Hence
  04.2.4, `hybrids.yaml`, and R4 of the simulation.
- *Stormlight's Ideals*: a fixed ladder with a hard top, universal checkpoints at fixed tiers, readiness
  tracked but the words the player's own, and permanence as the top tier's reward [R2 #2; R6 A-01]. Hence 04.5.
- *Tier rewards are capabilities, never filler; each step adds something qualitatively new; a tier-up
  restates text and never appends* [R3 #11, 04.6; R1 §04; R2 #3]. Hence 04.5.3–04.5.5.
- *Higher tiers need a different kind of evidence* (HWFWM's Essence Revelation; Cradle's understanding;
  Burning Wheel's difficult and challenging tests) [R2 #5; R6 R-A4]. Hence the since-last-tier requirements
  of 04.3.4: great deeds, crises, new contexts.
- *Every offer in the corpus is legible, standing and priced; recognizers must not be killable; revocation is
  gradual first* [R6 A.3, A.5, V14, A-02 (the Oathbreaker Knight bug)]. Hence 04.7 and 04.9.
- *Additive stacking without retirement is the failure every source shares*; the working precedents are the
  provisional league (PoE), fold-into-base (PoE2), fork-replacement (Dungeon Crawler Carl) and consolidation
  (The Wandering Inn) [C:VI; R3 #10, 04.3, 04.16; R2 4d]. Hence 04.8.
- *Rework a recognized identity only at telegraphed boundaries, and write retirement as transformation*
  (Survival Hunter; players "dislike losing things they spent points on") [R3 04.14; R1 T-16]. Hence
  consolidation that keeps every pick and specialty (04.8.5).
- *The grant branch is the riskiest for the player's sense of authorship* [R1 §04]. Hence every grant is
  provisional and can be set aside at any rest at no cost (04.8.2).
- *No source gives rules for monster-power absorption* [R2 4e, gap 1; R3 G-19]. Hence 04.10 authors trigger,
  cap, cost and failure, borrowing the learn-by-witnessing-and-winning rule of Final Fantasy's Blue Magic
  [R: https://finalfantasy.fandom.com/wiki/Learning], the library-and-active-set split [R3 04.18], and
  Hemalurgy's qualitative tax [R2 #47].

**What this chapter deliberately avoids.**
- *A calling that owns abilities.* No calling entry lists an ability. Picks are drawn from ch.05's shared pool
  through a pool gate on the calling's tags (04.8.4) [C:P5].
- *Conferral of capability.* No mentor, order, ruler or god can give a calling; they can only voice one the
  tallies support, and they can give **rank**, which is ch.11's and never capability (04.11) [R3 T-13].
- *Witness-gated capability.* A hermit's deeds make the hermit what they are. Witnesses decide only which
  vehicles are available and what ch.11's reputation hears (04.6.2) [03.4.6].
- *Compelled behaviour and surprise loss.* A calling never makes the character do anything, and nothing is
  taken without at least one earlier warning in fiction and out of it (04.8.2, 04.9) [R6 anti-patterns].
- *Attribute-ratio gates.* No requirement reads an attribute, so no calling is locked at creation [R3 T-19].
- *The calling's name in anyone's mouth as a bestowed title.* Epithets name deeds; tier words never appear in
  fiction (12.14.5; `vehicles.yaml#may_not_say`).
- *Numbers in the DM's hands.* The narrator's packet for a recognition holds a calling id, a policy, up to
  three vehicles and deed lines to quote. It holds no tally, threshold or score (00.14.2 #26; INV-3, INV-10).

**Runtime capability assumed.** The sealed tally store and functions of 03.9 (RC-SEAL, RC-QUERY); the
boundary scheduler for `reflection`, `season`, `scene_start` and `beat_end` handlers (RC-SCHED); the offer
log and typed store for callings, commitments and offers (RC-STORE, RC-LOG); the generator for `gen.absorb`
and the pick procedure (RC-RNG, RC-DATA); trigger surfacing (`get_active_triggers`, RC-RETRIEVE). No model call
is needed to decide any recognition.

---

## Rules

Rule ids are `04.S.R`. Kinds per 00.2.2. Digest shorthand per 00.1.6. Every number is in `data/callings.yaml`
unless another file is named. "PC" covers any actor whose evidence is tracked (03.2.7).

### 04.1 Foundations

**04.1.1 A calling is a derived label.** `[D]` A **calling** is an entry of `data/callings.yaml`: a name, one
or two **key tags**, a requirement set per tier, and the references a tier grants. A character *holds* a
calling when the engine has recognized it (04.4) and the grant stands (04.8). The label is computed over the
character's state; it owns nothing. What a tier grants is always one of five things, each drawn from a shared
source that the calling's tags only **gate** [C:P5; DL-04-01]:

| A tier grants | Drawn from | Gated by |
|---|---|---|
| a **competence** value (00.3.6) | `tier_ladder.competence` | the calling's key tag (or roads, for a hybrid) |
| a **training grade** | ch.05's training licenses (`lic.training.*`) | every such license whose first tag is at or under the key |
| one **universal capability** | `data/licenses.yaml owner-block 04` (five licenses, the same for every calling) | the tier number |
| **picks** | ch.05's one ability pool (`data/abilities.yaml`) | the pool gate of 04.8.4 on the calling's tags |
| a **composite**, **Focus trigger** or **boon** | one bounded entry per hybrid / deed family / conduct calling | the calling's kind |

**04.1.2 Callings in state.** `[D]` `Character.callings` (00.6.2) holds, per calling:
`{calling_id, tier, lifecycle (provisional | permanent | retired), granted_at {time, scene, evidence_scene_index},
crystallized_by (event id), vehicle, roads {branch: tag} (hybrids), seat (deed | oath), fraying_stage 0..3,
suspended bool, legacy_picks int, specialties [{tag, value}], inherited_band int, declined_until}`. The owning
family is "Callings, tiers, provisional status" (00.6.3): **shown once recognized**. Tallies stay sealed.
Commitments of kind oath and bond, and standing offers of kind recognition, are also this chapter's.

**04.1.3 The words.** `[N]` **Recognition** is a calling or tier being granted, offered or withheld.
**Crystallization** is the moment a tier takes effect. A **vehicle** is the fictional staging. A **seat** is
one of the places a held calling occupies (04.8.1). **Rank** is a seat in an institution (ch.11) and is never
capability (04.11). **Band** is the power band P1–P5 (04.5.6). The tier names (*Called, Proven, Tempered,
Exalted, Paragon*) are codex words. No one in the world says them (12.14.5).

**04.1.4 Sealed inputs, shown outputs.** `[S]` + `[D]` Everything this chapter *reads* is sealed (03.9.1).
Everything it *writes* to the character is shown: callings, tiers, provisional flags, licenses, competence
entries, picks, oaths with their forbidden acts, Fraying stages, standing offers. The gate between the two is
the policy of 04.4. The narrator receives packets (04.4.6), never values. The codex adds one `available`
view, **Leanings** (04.6.5), which names key tags and readiness bands and never a number.

### 04.2 The callings

**04.2.1 The roster.** `[D]` `data/callings.yaml` holds **183** callings in seven groups. Each is evaluated
**independently against its own requirement set** (04.3), so a broad calling never competes with a narrow one
for evidence [C:P5; R3 03.7 Threadbare]:

| Group | Key | Count | Ladder | Examples |
|---|---|---|---|---|
| **Branch callings** (`breadth: broad`) | one `deed` branch (level 1) | 9 | broad | Warrior, Rogue, Wayfarer, Scholar, Wizard, Priest, Druid, Envoy, Artisan |
| **Level-2 callings** (`narrow`) | one level-2 `deed` tag | 81 (every level-2 deed tag has one) | narrow | Archer, Thief, Tracker, Physician, Pyromancer, Healer, Skinchanger, Bard, Merchant, Alchemist |
| **Level-3 callings** (`fine`) | one level-3 `deed` tag | 40 (curated) | fine | Duelist, Assassin, Herbalist, Falconer, Surgeon, Gravekeeper, Minstrel, Bowyer, Cartographer |
| **Variants** | the same key as a level-2 calling, plus an added requirement | 2 | narrow + | Monk (Brawler's key + restraint), Devourer (Bestiarist's key + a hunter's record) |
| **Hybrids** | a pair of distinct `deed` branches | 32 named (+ 4 explicit "no hybrid") | hybrid | Ranger, Spellblade, Paladin, Berserker, Spy, Artificer, Hedgewitch |
| **Vows** | one `conduct` axis, positive pole | 10 | vow | Hospitaller (mercy), Justiciar (justice), Shieldsworn (protection) |
| **Dark callings** | one `conduct` axis, negative pole | 9 (courage has none) | dark | Pitiless, Betrayer, Tyrant, Defiler |

Why a calling for **every** level-2 deed tag: the level-2 tags are the game's vocabulary of things a person
can be good at, each already has a definition and distinguishing tests (03.1), and independent evaluation
costs the engine nothing. A roster with holes would be a menu by omission; with full coverage, any sustained
way of playing reaches a name [goal 1; DL-04-02]. Level 3 is curated, because a level-3 calling exists only
where the narrower identity is one the fiction recognizes as its own (a duelist is not "a blade-user who
fences"); `tags.04` proposed one new level-3 tag, `deed.wilds.animals.falconry`, for the Falconer, adopted into
`data/tags.yaml` at integration, so `call.falconer` keeps its key [DL-04-03; integration: IR ch.04 to 03].

**04.2.2 Families.** `[D]` Each calling belongs to one **family**: its deed branch for deed-keyed callings
(`martial`, `guile`, `wilds`, `lore`, `arcane`, `divine`, `primal`, `influence`, `craft`), `sacred` for vows,
`dark` for dark callings; a hybrid takes the family of its first branch unless it carries an oath, when it is
`divine` for staging. The family supplies defaults (`callings.yaml#families`): the two attributes eligible
for the tier-4 increase, the default shadow, the vehicle lists by policy outcome, the `org` tags that
`institutions_matching` is asked for, and the specialist's **Focus trigger** (04.5.4). A calling overrides a
default only by listing its own value.

**04.2.3 Specialists at three depths.** `[D]` A specialist's requirement set reads the node of its key (the
key and all its descendants, by cascade 00.5.4). The three depths differ in threshold and in what the
competence covers, which is how breadth is paid for [C:P4; R2 #10]:

| Depth | Weighted to tier 1 | Competence at tier 1 / 5 | Covers | Extra requirement |
|---|---|---|---|---|
| fine (level 3) | 60 | +3 / +6 | one technique or trade | none |
| narrow (level 2) | 80 | +3 / +6 | one weapon family, school, skill or trade | none |
| broad (level 1) | 120 | +2 / +5 | a whole branch | **breadth**: at least 3 level-2 children at weighted ≥ 30 each, and the largest child's share of the branch ≤ 2/3 |

The breadth requirement is what makes "Warrior" mean someone who fights with many things. In simulation a
mixed-weapons fighter was offered Warrior at session 3 (p10–p90: 3–4); a single-track swordsman in 1 of 200
runs within 30 sessions; a bow-focused archer who also climbs and knife-fights in 34 of 200 (T-04-8 R3)
[R1 T-13: broad callings need a narrower anchor; DL-04-04].

**04.2.4 Hybrids: the curated table.** `[D]` `data/hybrids.yaml` has one row for each of the C(9,2) = **36**
pairs of deed branches: 32 name a hybrid calling and 4 are explicit `calling: none` with the reason
(wilds × arcane, arcane × primal, divine × primal, primal × influence). The table is keyed **only** to branch
pairs, never to deeper tags or abilities; that is the sense in which it is sparse [C:P5; R3 04.9, T-5]. A
hybrid:
- is **eligible** when `cooccurrence(a, b)` shows `min ≥ 60`, `balance ≥ 2/5`, `joint_scenes ≥ 5`,
  `recent_min ≥ 15`, each branch has at least 4 difficult-or-better events over at least 4 scenes, and
  `counted ≥ 6` on each branch (`req.hybrid.1`). Both floors are **below** a specialist's (80 at one level-2
  node), so a hybrid is reachable without deep single-track investment, while the two together cost more
  evidence than one specialist [R3 04.4 Cataclysm's lesson; R2 #10];
- is **always an offer**, presented beside whatever single-track candidates are eligible in the same pass
  (04.7.6);
- grants competence on two **roads**: for each branch, the level-2 child with the largest weighted tally at
  the moment of recognition, fixed thereafter (04.5.2);
- carries the one **named composite** of its row (04.5.4) and no Focus trigger;
- may carry an **oath** (Paladin, Veiled Hand, Pilgrim, Inquisitor, Theurge, Preacher, Reliquarist).
The numeric trigger is original work [R3 G-1]. Acceptance test, simulated over 200 runs per mix: play that is
95/5 between two branches was never offered the hybrid; 90/10 in 9 of 200 runs; 80/20 in 173; 70/30 and more
balanced in all 200 by session 3 (median). A character with a second pillar in a quarter of scenes sat on
the line (65 of 200), which is where an offer rather than a grant is the right policy (T-04-8 R4) [DL-04-05].

**04.2.5 Vows and dark callings (conduct-keyed).** `[D]` A specialist may key on a `conduct` axis [C:P5].
The ten **vows** key on positive poles and are sworn (vehicle V4); the nine **dark callings** key on negative
poles and are bargains with an interested power (V13). `conduct.courage` has no dark calling: cowardice is
not an identity anyone is offered. Conduct callings:
- read `conduct(axis)` (03.8.3) and have no counted requirement, because every conduct entry is already
  grounded in a state write (03.3.3): vow `pos ≥ 16`, `net ≥ ¾ pos`, `recent_net ≥ 6`, `strain = 0`,
  `forbidden = 0`; dark `neg ≥ 16`, `neg ≥ ¾ (pos + neg)`, `recent_net ≤ −6`;
- grant **no competence**. They grant a **boon** (one effect, restated at tiers 3 and 5), oath picks (04.8.4),
  and capabilities at tiers 1, 2 and 5;
- occupy the single **oath seat** (04.8.1), so a character lives under at most one of them at a time;
- always carry an oath (04.9): a vow's forbidden act is written on its entry; a dark calling's oath is
  **reversed** (it frays when the character does good on its axis).
Pace (T-04-8 R10): a character who takes the costly choice in 60% of fights reaches a vow's first threshold at
session 5 (median); one who does so now and then (03's honest baseline) at session 18 [DL-04-07].

**04.2.6 Variants.** `[D]` A **variant** shares a level-2 calling's key and adds one requirement of a
different kind: Delve's shape of one primary with different secondaries [R3 04.1]. Two exist. **Monk**
(`variant_of: call.brawler`): the Brawler's requirement plus `conduct(conduct.restraint).net ≥ 8` with no
strain. Its pool gate adds `conduct.restraint` at the positive pole (`pole: positive`), so its picks may
take the restraint vow's abilities (04.8.4) [revision: I-007; DL-04-25]. **Devourer** (`variant_of: call.bestiarist`): the Bestiarist's requirement plus a hunter's record
(at least 5 distinct non-folk opponent kinds, counted defeats ≥ 20 at the root, and one crisis against a
non-folk creature); it is offered only by V13 and is the gate of 04.10. A variant and its base share one
lineage (04.8.3): holding one, the other arrives as a fork [DL-04-06].

**04.2.7 Coverage audit: the iconic archetypes.** `[D]` Each is reachable from the first session by deeds a
new character can attempt. "Start" names what begins the evidence; magic branches need a first license,
which ch.02's origins, ch.05's mentor and project paths, or an item supply (Interface requests).

| Archetype | In this ruleset | Key | Start |
|---|---|---|---|
| Fighter | **Warrior** (broad); Blade, Hewer, Mauler, Spearhand, Shieldbearer, Ironclad, Tactician, Champion | `deed.martial` and children | basic Strike, Grapple, Force |
| Ranger | **Ranger** (martial × wilds); Archer, Tracker, Hunter, Pathfinder, Survivor | `deed.martial` × `deed.wilds` | Strike, Observe, Handle |
| Rogue | **Rogue** (broad); Thief, Shadow, Trickster, Assassin, Lockbreaker, Swashbuckler (martial × guile) | `deed.guile` | Sneak, Talk (deceive); lockwork needs its training license |
| Bard | **Bard** (performance); Minstrel, Skald; Spellsinger (arcane × influence) | `deed.influence.performance` | Talk (perform) |
| Cleric | **Priest** (broad); Healer, Sanctifier, Celebrant, Exorcist, Oracle | `deed.divine` | a first divine license (origin or a shrine's teaching) |
| Paladin | **Paladin** (martial × divine, oath-bearing); Templar; plus any vow | `deed.martial` × `deed.divine` | Strike + a first divine license; the oath is the price |
| Druid | **Druid** (broad); Greenwarden, Beast-speaker, Weather-worker, Skinchanger; Wildwarden (wilds × primal) | `deed.primal` | a first primal license |
| Wizard | **Wizard** (broad); Pyromancer … Transmuter; Magister (lore × arcane) | `deed.arcane` | a first arcane license (apprentice origin, mentor, study project) |
| Sorcerer | **Elementalist** (innate living force, `deed.primal.elements`), usually first voiced by V5 | `deed.primal.elements` | a birth spark from `gen.birth` (ch.02) |
| Warlock | **Pactbound** (`deed.divine.pact`), offered by V13, oath to a patron | `deed.divine.pact` | a bargain (V13 acquisition path `bargain`) |
| Monk | **Monk** (variant: unarmed + restraint), or Brawler + the Ascetic vow | `deed.martial.unarmed` | Strike unarmed; restraint under provocation |
| Barbarian | **Berserker** (martial × primal); the Wrathful (dark) for the unrestrained | `deed.martial` × `deed.primal` | Strike + a first primal license |
| Necromancer | **Necromancer**; Bonecaller | `deed.arcane.necromancy` | a first necromancy license |
| Artificer | **Artificer** (arcane × craft); Tinker, Clockmaker, Enchanter, Runescribe | `deed.arcane` × `deed.craft` | crude making (Handle) + a craft training license |
| Alchemist | **Alchemist**; Apothecary; Hedgewitch (primal × craft) | `deed.craft.alchemy` | the alchemy training license |
| Merchant-prince | **Merchant**, Venturer; Magnate (influence × craft); the *prince* part is rank and holdings (ch.11) | `deed.influence.trade` | Talk (bargain) |
| Scholar | **Scholar** (broad); Antiquarian, Linguist, Loremaster, Investigator; Counselor (lore × influence) | `deed.lore` | Recall, Observe (study) |
| Knight | **Cavalier**, Lancer; knighthood itself is a rank (ch.11) | `deed.martial.mounted` | riding + Strike |
| Witch | **Hexer**, Cursebreaker; Hedgewitch; Cunning-folk (lore × primal) | `deed.primal.hexcraft` | a first primal license |
| Shaman | **Spirit-talker** | `deed.primal.spirits` | a first primal license |
| Assassin, Spy | **Assassin** (fine); **Spy** (guile × lore) | `deed.guile.ambush.assassination`; pair | Sneak, Strike from hiding |
| Healer (mundane) | **Physician**, Surgeon, Herbalist | `deed.lore.medicine`; `deed.wilds.foraging.herbs` | first aid (Handle) + the medicine license |
| Monster-hunter | **Slayer** (martial × lore); Bestiarist; **Devourer** | pair; `deed.lore.bestiary` | Strike + Recall |
| Captain | **Captain**; Marshal (martial × influence) | `deed.influence.command` | Talk (command), Help |
| Smith and trades | **Artisan** (broad); Smith, Wright, Weaver, Builder, Jeweler, Scribe and their fine callings | `deed.craft.*` | crude making + the trade's license |

### 04.3 Requirements: the dual thresholds

**04.3.1 Shape.** `[D]` Every tier of every calling has a **requirement set** `req.<ladder>.<tier>`
(`callings.yaml#requirements`), built as Delve's two requirements [C:P5; R3 04.1]:
- the **primary requirement** (eligibility) reads *judged* evidence: the weighted tally at the key plus
  quality and breadth floors;
- the **secondary requirement** (trigger) reads *counted* evidence: engine-counted outcomes at the key
  (foes defeated, Focus spent, clocks advanced, things made; 03.7).
A candidate is **eligible** for a tier only when **both** hold. Judgment can inflate the first; nothing but
play can inflate the second [03.7.1; R3 #4]. Every field is read through one sealed function of 03.9:

| Field | Function (03.9) | Meaning |
|---|---|---|
| `weighted`, `recent` | `tally(pc, key)` | cumulative and recent settled points at the key's node |
| `counted` | `counted(pc, key).units` | cumulative counted units at the node |
| `quality_events` | `detail(pc, key).by_quality.difficult + .challenging` | events at the edge of ability or beyond |
| `distinct_scenes` | `detail(pc, key).distinct.scenes` | separate scenes in which the key was shown |
| `great_deeds` | `detail(pc, key, since).by_band[t..5]` summed, with `success_by_band[t..5]` summed ≥ 1 (equivalently `peak_band ≥ t`, the highest band among successes) | settled deeds whose challenge band is at least the tier being entered, at least one a success (exact since 03 added `success_by_band` at integration) |
| `crises` | `detail(pc, key, since).crises` | deeds done in lethal context, while Staggered or Dying, or at Dire stakes and challenging odds (03.4.5) |
| `contexts` | `detail(pc, key, since).distinct.contexts` | distinct kinds of opposition or obstacle |
| `children`, top child share | `profile(pc, deed, 2)` within the branch; `share` | breadth of a branch |
| `min`, `balance`, `joint_scenes`, `recent_min` | `cooccurrence(pc, a, b)` | the hybrid's two branches together |
| `pos`, `neg`, `net`, `recent_net`, `strain`, `forbidden`, `scenes_since_negative` | `conduct(pc, axis)` | conduct callings and the Fraying |

`since` is the time of the calling's last crystallization. Ratios are compared by cross-multiplication on
integers (03.9.3); no percentage is stored (SG-23).

**04.3.2 First recognition (tier 1).** `[D]`

| Ladder | Weighted | Counted | Quality events | Distinct scenes | Also |
|---|---|---|---|---|---|
| fine | ≥ 60 | ≥ 6 | ≥ 6 | ≥ 5 | — |
| narrow | ≥ 80 | ≥ 8 | ≥ 6 | ≥ 5 | — |
| broad | ≥ 120 | ≥ 12 | ≥ 6 | ≥ 5 | ≥ 3 level-2 children at ≥ 30 each; largest child ≤ 2/3 of the branch |
| hybrid | `min` ≥ 60 | ≥ 6 on **each** branch | ≥ 4 on each branch | ≥ 4 on each branch | `balance` ≥ 2/5; `joint_scenes` ≥ 5; `recent_min` ≥ 15 |
| vow | `pos` ≥ 16 | — | — | (≥ 3 scenes follows from the cap of 7 per scene, 03.8.2) | `net` ≥ ¾ `pos`; `recent_net` ≥ 6; `strain` 0; `forbidden` 0 |
| dark | `neg` ≥ 16 | — | — | (as vow) | `neg` ≥ ¾ (`pos` + `neg`); `recent_net` ≤ −6 |

The **quality floor** is what excludes the grinder: in 03's simulation a character who shot cellar rats in
every scene passed weighted 80 by about session 5 with 100% routine events; under this rule the same
character was recognized in **0 of 200** runs over 20 sessions (weighted 340, counted 100, quality events 0)
(T-04-8 R5). The **distinct-scenes floor** excludes the single lucky fight: one scene can settle at most 28
points at a node (03.5.2), so 80 already needs three scenes; five makes it a pattern [03 Interface requests
(a); DL-04-08].

**04.3.3 The counted requirement.** `[D]` Counted = the weighted threshold ÷ 10, rounded down, at every tier
(8, 20, 44, 80, 130 for a narrow calling). Any counter of 03.7.2 credited at the key's node counts.
`cnt.training` units (a completed week of downtime training, 03.5.5) count toward **at most half** of it: a
mentor speeds recognition up and never substitutes for deeds [R6 A-27]. **Measured** `[revision: I-004]`:
on chapter 06's conflict engine with 03's rules applied to every beat, defeat and push (`03-counted-yield.py`)
a fighter's counted share at the weapon node is 0.11 / 0.15 / 0.22 / 0.23 / 0.33 at bands 1–5 without Focus
and 0.26–0.44 when pushing; the social, craft and lore contests run 0.31 / 0.76 / 0.31 (T-04-8 R12). A tenth
therefore binds only judged evidence with nothing behind it, and one corner of honest play: a band-1 fighter
who meets nothing but mobs and never spends Focus needs one fight more than the weighted line already asks
(9 instead of 8). The divisor stays at 10 (OEQ-04-2) [DL-04-09; DL-04-27].

**04.3.4 Deepening (tiers 2–5): a different kind of evidence each time.** `[D]` A higher tier needs the
cumulative weighted and counted totals of its ladder **and** a set of things done **since the last
crystallization**. Each tier asks for a kind of evidence that repetition cannot produce [R2 #5; R6 R-A4]:

| Tier | Weighted (fine / narrow / broad / hybrid min) | Since the last tier: quality events · scenes | Great deeds (band ≥ tier) | Crises | Contexts | In fiction |
|---|---|---|---|---|---|---|
| 2 Proven | 150 / 200 / 300 / 150 | 10 · 8 | 5 at band ≥ 2 | — | — | proven against what is beyond the ordinary |
| 3 Tempered | 330 / 440 / 660 / 330 | 14 · 10 | 6 at band ≥ 3 | 2 | — | tempered where it could have ended |
| 4 Exalted | 600 / 800 / 1,200 / 600 | 18 · 12 | 6 at band ≥ 4 | 3 | 5 | done in many countries, against champions |
| 5 Paragon | 975 / 1,300 / 1,950 / 975 | 22 · 14 | 4 at band 5 | 4 | 5 | done at the edge of what mortals can do |

A **great deed** is a settled deed at the key whose `challenge_band` (03.4.3: the obstacle's absolute rung,
DC 13–17 is band 2 … DC ≥ 28 is band 5; in a conflict the fight's advisory band; in a social, craft or lore
**contest** the opposing party's or the work's band) is at least the number of the tier being entered; at least one of the
required deeds must be a success. The band is tied to **this calling's** tier and not to `power_band`, so a
second calling deepens on its own merits (a Paragon archer's new Tracker calling needs band-2 deeds for tier
2, not band-5 ones). For a hybrid the since-fields are summed over both branches, with at least one great
deed and half the scenes on each. For a vow or dark calling the ladder is `pos` (or `neg`) ≥ 16, 40, 80, 140,
220 with the tier-1 conditions, and from tier 3 `scenes_since_negative ≥ 24` (48 at tier 5): a full window of
faithfulness [DL-04-08].

**04.3.5 Pacing targets and what the simulation gives.** `[D]` Targets, chosen before calibration: first
recognition in sessions 3–5 of focused play; tier 2 near session 9; tier 3 near session 18; tier 4 near
session 32; tier 5 not before session 50, and not reached by most characters (Stormlight: "many stop at the
Third") [R2 #2; R1 §04 "excessive investment kills an option"]. Results (200 runs, 5 scenes per session,
p10 / median / p90; T-04-8 R1–R4):

| Character | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tier 5 |
|---|---|---|---|---|---|
| Archer who scouts (03's scenario A), key `martial.archery` | 3 / **4** / 5 | 7 / **9** / 11 | 16 / **19** / 22 | 31 / **34** / 38 | 52 / **56** / — (165 of 200 within 60) |
| Swordsman who fights in 70% of scenes | 2 / 2 / 3 | 5 / 6 / 7 | 11 / 12 / 13 | 19 / 21 / 23 | 32 / 35 / 37 |
| Burglar, key `guile.thievery` | 3 / 4 / 5 | 8 / 10 / 11 | 18 / 21 / 29 | 32 / 35 / 40 | 53 / 59 / — |
| Envoy, key `influence.persuasion` (before revision A; see below) | 4 / 5 / 7 | 9 / 12 / 14 | 23 / 28 / 48 | 44 / 49 / — | not within 60 |
| Mixed-weapons Warrior (broad) | 3 / 3 / 4 | 7 / 8 / 9 | 14 / 15 / 17 | 26 / 29 / 31 | 46 / 49 / 52 |
| Deliberate 50/50 hybrid | 2 / 3 / 4 | 5 / 6 / 8 | 11 / 13 / 14 | 21 / 23 / 25 | 36 / 39 / 42 |
| Lockbreaker (fine key) under the burglar | 3 / 4 / 6 | 8 / 10 / 12 | 18 / 22 / 37 | 34 / 38 / 46 | 58 / — / — |

A whole character with every key live and three seats held three callings by session 10 if every offer was
accepted, with the highest tier at sessions 10 / 20 / 40 / 60 at 2 / 3 / 4 / 5 (archer) (T-04-8 R6).

**Non-combat parity** `[revision: I-003]`. The envoy's lag above came from the evidence rules: a social,
craft or lore deed could not be rated by what it faced, a crafting step was never Dire, and nothing outside
a fight was ever as grave as a lethal frame. 03.4.3's **contest band**, 03.4.5's **ruinous** and **brink**
crises, 15.3.11, 15.9.20 and 08.6.4 (item 6) close that gap. `04-recog-parity.py` gives every pillar the
same play shape (55% of scenes in one's own pillar, 3–6 beats, a quarter of them Dire; conflicts at the
advisory offsets of DL-00-05; 200 seeds, 90 sessions) and compares (median sessions; T-04-8 R11):

| Calling (key) | Tier 3 | vs archer | Tier 5 | vs archer |
|---|---|---|---|---|
| Archer `martial.archery` (combat) | 19 | — | 51 | — |
| Envoy `influence.persuasion` | 18 | −5% | 46 | −10% |
| Smith `craft.smithing` | 18 | −5% | 45 | −12% |
| Scholar `lore.history` | 17 | −11% | 46 | −10% |
| *the smith under the earlier rules* | *never* | | *never* | |

All three are within ±20% of the combat calling at both tiers. With 04's thinner social shape (2–4 beats,
15% Dire) the envoy reaches tier 3 at 20 and tier 5 at 54 [DL-03-26; DL-04-28].

### 04.4 Confidence and the three-valued policy

**04.4.1 Why a score at all.** `[N]` The constitution asks for a per-candidate confidence resolved by a
three-valued policy, and its body text still speaks of a calibrated classifier in a different model family
[C:P5]. The sixth pass chose a deterministic tally scorer; BRIEF A3 requires this chapter to say what
"confidence" then means. A deterministic scorer satisfies the independence requirement trivially (it is not a
model) [R3 T-4]. What remains is to make the score **mean** something. The definition below was chosen by
measuring, in simulation, which facts about a just-eligible candidate predict that play goes on to confirm it
(T-04-8 R7; `04-feat04.py`) [DL-04-10].

**04.4.2 Confidence.** `[D]` For an eligible deed-keyed candidate, **confidence** is the number of these five
**confirmations** that hold, an integer 0–5:

| Id | Confirmation | Test (integers; `W1` = the ladder's tier-1 weighted threshold) | Why it predicts (candidates confirmed with it true / false, R7's feature study) |
|---|---|---|---|
| K1 | **Current** | `2·recent ≥ W1` | the character is living this now (85 / 51 in 100) |
| K2 | **Rising** | `2·recent ≥ weighted` | most of the evidence is recent: a pursuit, not a slow accretion (89 / 55) |
| K3 | **Central** | `5·weighted(key) ≥ weighted(deed)` | the key holds a fifth of everything the character has done (87 / 47) |
| K4 | **Leading** | the key is among the three largest of `profile(pc, deed, level of key)` | one of the character's three strongest nodes at its level (84 / 47) |
| K5 | **Margin** | `4·weighted ≥ 5·W(tier)` | a quarter past the line; the largest possible single event is 16 (03.4.2), so no one event, and no one mistaken call, put it there (80 / 67) |

Separately, the **currency floor** `4·recent ≥ W1` must hold or the candidate is **stale** (confirmed in 34 of
100 when false). Counted margins and quality margins were tested and predicted nothing beyond their floors, so
they are requirements and not confirmations. **Calibration** (1,723 level-2 candidates across six play
styles, scored at the pass where each first became eligible): the share that play went on to confirm (recent
≥ 24 after 24 further evidence-bearing scenes) was **37, 59, 64, 73, 91 and 97 in 100** for scores 0–5; the
share that were a designed pillar of the play style was 21, 41, 76, 72, 98 and 100 in 100. The score is
monotone in both, which is what "calibrated" means here.

**04.4.3 The policy.** `[D]` First match wins (SG-10):

| # | Condition | Outcome |
|---|---|---|
| 1 | the candidate is not eligible (04.3), or is stale, or is under a decline cooldown (04.7.7) | **abstain** |
| 2 | confidence = 0 | **abstain** ("thin": eligible by slow accretion with nothing confirming it; re-checked every pass) |
| 3 | confidence ≥ 4 **and** all of: tier 1; ladder fine or narrow; not a variant; no `oath` block; **clear field**; a free seat; no lineage conflict (04.8.3); never declined or renounced | **grant** |
| 4 | otherwise | **offer** |

**Clear field**: no other candidate keyed in the same deed branch is eligible in this pass and no hybrid
containing that branch is eligible. A mixed history is therefore never resolved by the engine: it is
surfaced as named alternatives for the player to choose among [C:P5]. Tier-ups, hybrids, variants,
oath-bearing callings, vows, dark callings, branch callings, forks and consolidations are **always offers**
[C:P2]. In simulation the grant bucket was confirmed by later play in 91 of 100 cases, the offer bucket in
74, the abstain bucket in 38 (T-04-8 R7). A grant is still the player's to refuse: it is provisional and may
be renounced at any rest (04.8.2) [R1 §04].

**04.4.4 The largest wrong outcome.** `[D]` No judgment is made in this part, but the inputs include judged
evidence (03.3), so the blast radius is stated: one mistaken evidence event is at most 16 points (20% of a
narrow tier-1 threshold); K5 exists so that a grant never rests on the last 20 points; a wrong grant is
provisional, shown, renounceable, and lapses unless lived (class ii, iii and iv of 00.2.1 P-B at once).

**04.4.5 When recognition is evaluated.** `[T]` + `[D]` Four triggers, and no others:
- **reflection**: `h.04.recognition_pass` at every `reflection` (each completed long rest, each downtime week,
  each season boundary; 00.7.2), after 03's digest (03.6.4). It evaluates only candidates keyed on the
  digest's dirty nodes and axes, so its cost stays bounded as the roster grows.
- **crisis**: `h.04.crisis_check` at `beat_end`. *True only when* this beat recorded an evidence event with
  `crisis: true` (03.4.5) whose primary or grounded secondary tag is at or under the key of a candidate, or
  of a held calling's next tier, whose readiness band is `on_the_threshold` or `ready` (04.6.5). The engine
  then evaluates that one candidate with pending evidence included (`tally(include_pending: true)`, the only
  caller allowed, 03.5.6) and, if it is eligible and the policy is offer or grant, raises `trg.04.crisis_offer`.
  At most one per scene.
- **arrival**: the PC enters a place, or meets a person or institution, named by a standing offer or carrying
  a matching `resonance` (04.7.3).
- **request**: the player asks a reader for a reading (04.6.4) or asks, out of fiction, to take up a standing
  or declined offer.
Triggers surface through `get_active_triggers` and are handled in the turn they fire (12.2.3 item 6). A
recognition offer is the one trigger 12.2.3 allows to wait: the engine, not the DM, holds it until the
vehicle's `when` is met.

**04.4.6 `evaluate_recognition(trigger)`.** `[D]` + `[S]` Tool #26 (00.14.2). Input: the trigger. Output: a list
of **packets**, each
`{calling_id, tier, kind (first | tier | hybrid | variant | fork | consolidation | pick | confirm |
lapse_warning | fraying | shadow), policy (grant | offer | abstain), vehicles [≤ 3 vehicle ids], price_ids,
deed_lines [event ids to quote], alternatives [calling ids presented beside it], reading {band, lacking}?}`.
A packet contains **no** tally, threshold, score or nearness. Abstain packets are returned only for the
`request` trigger and for a band change (they carry the `reading`); otherwise abstain is silence. The tool
writes the tally values it used to the sealed `tally_snapshot` of the offer log (04.7.8).

### 04.5 The tier ladder

**04.5.1 Five tiers, and no sixth.** `[D]` The maximum tier is **5**. The ladder is closed: no rule, item,
boon or future content adds a tier above Paragon; growth past it is breadth (another calling, within the
seats) or the character's ending (04.11.4) [R2 #3: HWFWM's bolted-on top tiers]. What each tier grants:

| Tier | Competence at the key (fine, narrow / broad, hybrid roads) | Training grade (fine, narrow / broad, hybrid) | Universal capability | Picks, cumulative (deed / oath) | Family mechanic | Other |
|---|---|---|---|---|---|---|
| 1 **Called** | +3 / +2 | trained / trained | `lic.call.mark` | 2 / 1 | hybrid: composite rank 1 · vow, dark: boon rank 1 | seat taken; shadow recorded |
| 2 **Proven** | +4 / +3 | trained / trained | `lic.call.proof` (you can teach it) | 3 / 1 | specialist: Focus trigger rank 1 | — |
| 3 **Tempered** | +5 / +4 | expert / trained | `lic.call.sure_hand` (a lever when you stretch or emulate) | 4 / 2 | hybrid: composite rank 2 · vow, dark: boon rank 2 | — |
| 4 **Exalted** | +5 / +4 | expert / expert | `lic.call.masters_eye` (read the task before you commit) | 5 / 2 | specialist: Focus trigger rank 2 | **+1 to one attribute**, once in a lifetime |
| 5 **Paragon** | +6 / +5 | master / expert | `lic.call.open_art` (emulate anything of your art) | 6 / 3 | hybrid: composite rank 3 · vow, dark: boon rank 3 | **permanence** (04.9.6); the calling's ending becomes available (04.11.4) |

Every tier grants a capability or a behaviour change; none is a bare number [R3 04.6]. The competence column
keeps the game inside 00.3.7's envelope: with the best attribute (+3, or +4 after tier 4) and edge 0–2, a
narrow specialist's best-domain base modifier is +6 at tier 1, +7 to +8 at tier 2, +8 to +10 at tier 3, +9
to +11 at tier 4 and +10 to +12 at tier 5, which are the bands P1–P5 [00.3.7; DL-00A-04; DL-04-23].

**04.5.2 Competence.** `[D]` On crystallization the engine writes a competence entry `{tag, value, source:
calling id}` (00.3.6): at the key for a specialist; for a hybrid, at each **road** (the level-2 child of
each branch with the largest weighted tally when the hybrid is first recognized; ties by data order). Roads
are fixed; they change only by a season re-pick (04.8.7). Competence is highest-only, so entries from several
callings never add. A vow or dark calling writes none.

**04.5.3 Capabilities.** `[D]` The five universal licenses are defined in `data/licenses.yaml owner-block 04`
with full scope, exclusions and fallbacks (00.12.1). Each is held **once** (INV-13) and its scope reads "the
key of any calling you hold, unsuspended, at this tier or higher", so a second calling widens it. In brief:
**Mark** (tier 1) lets the character use every training license under the key at the tier's grade and stand
as a recognized practitioner where a rule or institution requires one. **Proven** (2) makes the character a
valid mentor for others' training under the key. **Sure Hand** (3) grants a Precision lever on any stretch
or emulation under the key (it counts toward the two-lever limit, 00.3.9 f). **Master's Eye** (4), once per
scene, shows the obstacle's DC and one sealed tell before the player commits to a beat under the key.
**The Open Art** (5) allows emulation of any ability under the key without having witnessed it, at the
emulate price. A vow or dark calling grants Mark, Proven and Open Art only (tiers 1, 2 and 5), read against
its conduct axis.

**04.5.4 The family mechanic.** `[D]` One bounded, authored entry gives each kind of calling a distinct feel
without a list of its own [C:P5 "a small, bounded, audited synergy bonus"; R3 04.15, T-1]:
- **Specialists: a Focus trigger** (`callings.yaml#families[].focus_trigger`), one per deed family, active
  from tier 2: on its hook and condition, regain 1 Focus, once per scene (twice from tier 4). Martial: when a
  deed of the calling defeats a foe at or above the PC's band. Guile: a critical success against one who never
  saw it coming. Wilds: a breather outside any settlement. Lore: a deed that uncovers a clue or a sealed fact.
  Arcane: a working that critically succeeds. Divine: lifting a condition from another, or bringing another
  back from Dying. Primal: dawn under open sky. Influence: a deed that moves someone's standing upward.
  Craft: a deed that completes a project clock. Focus stays one pool [C:P9]; only how it refills differs.
- **Hybrids: a named composite** (`data/composites.yaml owner-block 04`, 32 entries, `key_kind: deed_branch`):
  rank 1 at tier 1, a success on one road grants a lever of the composite's type on a later beat of the other
  road, once per scene (Ranger's *Hunter's Quarry*: a successful wilds deed grants an Amplifying lever on a
  martial beat). Rank 2 at tier 3: either direction, twice per scene, and a **fused deed** (primary tag under
  one branch, a grounded secondary under the other, 03.1.6) gains +1 edge. Rank 3 at tier 5: three times per
  scene, the player chooses the lever's type, and once per scene a fused deed's reach is one rung higher.
  Every piece is a core effect and sits under 00's caps (two levers, ±4 circumstance, +2 edge) [DL-04-11].
- **Vows and dark callings: a boon** (`callings.yaml`, the entry's `boon`): one effect by rank. The
  Shieldsworn takes a hit meant for an ally once, twice, then three times per scene; the Dauntless gains +1
  against fear, then cannot be frightened, then neither can allies close by.

**04.5.5 Restated, never appended.** `[D]` Whatever has ranks (a composite, a Focus trigger, a boon, an
ability picked from the pool) has **one** active rank: the highest whose tier the calling has reached. The
higher rank's text and effects **replace** the lower rank's entirely; nothing accumulates [R2 #3: HWFWM's
ability text that only grows]. An ability's rank is `1 + floor((calling tier − ability min_tier) ÷ 2)`,
capped at the ability's highest authored rank, where the calling is the one whose pick holds it. The codex
shows only the active rank's literal text. A Fraying suspension (04.9.3) lowers the tier that these formulas
read.

**04.5.6 `power_band(pc)`.** `[D]` The contract function for ch.09 and for 03's `peak` flag (00.17 Q5). It is
computed from recognized tiers only:

`power_band(pc) = max(1, max over held callings that are not suspended, provisional included, of
band_by_tier[ladder][tier], and each calling's inherited_band)`.

The band also sets the PC's maximum Vitality: **+2 per band above the first** (creation value + 2 ×
(power_band − 1), cap 24), applied by ch.07's `h.07.vitality_max`; current Vitality rises by the same amount when
the band rises (07.1.2) [integration: DL-00-04]. (07.1.2 reads the band "from confirmed tiers only", while this
rule counts provisional tiers: see issue I-037 [verification: V1-006].)

| Ladder | Tier 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| fine, narrow (and variants) | 1 | 2 | 3 | 4 | 5 |
| broad, hybrid | 1 | 2 | 3 | 4 | 4 |
| vow, dark | 1 | 1 | 1 | 2 | 2 |

An unrecognized character is band 1 (P1 novice, 00.3.7). `inherited_band` is the band of a calling retired
into this one by consolidation (04.8.5), so consolidating never lowers the band. Nothing else enters: not
items, not fame, not narration.

**04.5.7 The one attribute increase.** `[D]` The first time any calling of a character reaches tier 4, the
player raises **one** attribute by 1, chosen from that calling's `attributes` (two options for a specialist,
a vow or a dark calling: the family default or the calling's own; for a hybrid, the defaults of both its
families), to at most +4 (00.4.3 b). It happens once in a lifetime: later tier-4 crystallizations
grant everything else of the tier and no increase. If every listed attribute is already +4, the player
chooses any attribute below +4.

**04.5.8 The crystallization moment.** `[T]` + `[D]` A tier is never applied the instant a counter crosses a
line. When a held calling's next tier becomes eligible the engine marks it **ready** and it is staged at the
first of [C:P2]:
(a) the same beat, if the event that completed the requirement was flagged crisis (the crisis check, 04.4.5),
by V5 or, for an oath-bearing calling, V4;
(b) the next arrival at a place or person a vehicle of the tier needs (V2, V9, V11);
(c) the next reflection, by the first vehicle whose requirements hold; V7 always does.
The **crystallizing event** is the settled event that completed the requirement set (if several did in one
settlement, the one with the most points). Its deed line is what the vehicle quotes and what
`recognition_event.epithet_seed` carries. Readiness persists until answered: a tier is offered, never
withheld for a "better" moment, and never lost by waiting.

### 04.6 Voicing: the vehicles

**04.6.1 Fourteen vehicles, each outcome with a voice.** `[D]` A **vehicle** is a staging template the DM
applies to a recognition the engine has decided. `data/vehicles.yaml` holds V1–V14 with their recognizer,
staging, accept / decline / defer forms, requirements, prices and forbidden phrasings [R6 A.4]. Each policy
outcome has its own voices, so no outcome is left to a bare notice [R6 R-A2]:

| Outcome | Vehicles | The world's stance |
|---|---|---|
| **grant** | V1 Witnessed Epithet · V8 Rival Names You · V7 Reflection at Rest (when no one saw) · V11 Place Answers (a small boon) | it already treats you as this |
| **offer** | V2 Mentor's Acknowledgement · V3 Order Seeks You Out · V4 Oath Spoken · V5 Awakening in Crisis · V7 Reflection at Rest · V9 Rite or Trial · V11 Place Answers · V12 Master of the Fusion · V13 Interested Power | someone, or something, asks |
| **abstain** | V6 Seer's Reading, or silence | someone reads you, vaguely |
| **revocation** | V14 The Fraying | the bond dims, then speaks, then asks |
| small confirmations | V10 The Body Remembers | you notice it yourself |

**04.6.2 Choosing the vehicle.**

```
### 04.6.2  Vehicle selection                                     [D] [J:enum] [N]
Trigger [T]:        evaluate_recognition returns a packet whose policy is grant or offer, or a fraying,
                    confirm or reading packet (04.4.6)
Loads in:           core when trg.04.* is active; situation.rest.*, situation.downtime.* for reflections
License check:      n/a (staging, not an attempt)
Computation [D]:    PR-04-3. The engine filters the calling tier's vehicle list by (1) policy outcome,
                    (2) trigger class (crisis | reflection | arrival | request), (3) each vehicle's
                    `requires` against state: public tallies and scopes (03.10) for V1, V3, V8, V9; an NPC
                    of depth recurring or principal with matching role_tags and standing >= 1 for V2 (or
                    one placed by 12's lead engine); institutions_matching(branch, region) for V3 and V9
                    (ch.11); a place `resonance` for V11; an oath block for V4; (4) drops any vehicle used
                    for this character's last two recognitions unless none would remain; (5) orders by
                    `specificity`; (6) returns at most three.
Decisions (J):      1. VEHICLE [J:enum] among the returned vehicles (<= 3): the one whose staging the
                       scene's established facts support word for word (the named NPC is here; the letter
                       could have arrived; the place is this place). Each option's inclusions and
                       exclusions are its `requires` and `rules` in vehicles.yaml. Default when unsure:
                       the first returned.
Stakes:             none
State writes:       offer.vehicle (or calling.vehicle for a grant); the recognizer entity if one is
                    introduced (write-on-mention, 00.6.6); a fact for a letter, token or sign
Narration may not imply: the calling's name as a bestowed title; any tier word; any number; that
                    something was "gained" or "unlocked" (12.14.5); that the recognizer CAUSED the
                    capability; anything in the vehicle's may_not_say list
Worst case (J):     a staging that fits less well than another returned vehicle. Nothing mechanical
                    differs between vehicles except the price, which is shown in the CHOICE block before
                    the player answers (class ii).
Examples:           inside: grant of Archer; caravan guards witnessed the shots (public events 3 in
                      fac.caravaners_compact) -> V1, a carter uses a name for her.
                    inside: the same grant, every witness dead and no one told -> V1 and V8 fail
                      `requires`; V7 remains: she wakes knowing it.
                    boundary: an offer at a reflection in the wild; a mentor exists but is three days
                      away -> V2 fails "reachable within one watch"; V7 now, and the offer's
                      represent_when adds "return_to_person" so the mentor may voice the tier later.
                    non-example: the DM wants a dramatic awakening for a tier that became ready at a
                      quiet rest -> V5 is not returned (trigger class is reflection); it may not be staged.
Anchor:             no
Basis:              [R6 R-A1, R-A2, A.3] [R4 §9 04 #2: forms from a table, engine-varied] [DL-04-12]
```

**04.6.3 Staging rules common to all vehicles.** `[N]` + `[D]`
1. **The tally is the cause; the vehicle is the voice.** An NPC with standing may *name* what the record
   already shows; no NPC's opinion changes a tally or a tier [R6 A-09].
2. **Quote deeds, not qualities.** The staging cites one to three deed lines from the packet (03.2.4): "you
   held the ford while the carters crossed", never "you are brave".
3. **The recognizer is replaceable.** If a mentor, emissary or master dies or leaves, the offer continues
   at the next reflection by V7 at the same terms minus that vehicle's price. A recognition is never
   stranded behind one mortal [R6 A-02].
4. **Scale the herald to the calling.** A fine or narrow trade is voiced at the scale of a workshop or a
   village; a tier-5 crystallization may be voiced across a region (ch.11 decides the spread from
   `recognition_event`) [R6 A-23].
5. **Witnesses shape the voice, never the fact.** With no public tally only private vehicles are available
   (V5, V7, V10, V11, V4, V13); the capability is identical [03.4.6].
6. **A visible tell.** A crystallization staged in front of carriers is itself a witnessed event: the
   engine adds one `public_deed`-style packet to ch.11 through `recognition_event` (04.7.8) [R2 #19].

**04.6.4 The Seer's Reading (V6): the voice of abstain.**

```
### 04.6.4  The Seer's Reading                                    [D] [N]
Trigger [T]:        (a) the player has the character ask a reader what they see in them: an NPC with
                    role_tags under deed.influence.insight, deed.divine.revelation, deed.arcane.divination
                    or deed.lore.religion, or any NPC of standing >= 2 who has witnessed the PC's deeds
                    (trigger class request); (b) at a reflection, a readiness band changed since the last
                    one (at most one reading per reflection, voiced as a dream or a companion's remark)
Loads in:           situation.social.*; situation.rest.*
License check:      basic verb: verb.talk (asking costs nothing and needs no roll; the reader's
                    willingness is ch.15's)
Computation [D]:    For each of the up to three candidates nearest recognition (and any the PC's
                    aspirations name, ch.02), the engine computes the READINESS BAND from the next tier's
                    weighted threshold W: unformed (weighted < W/4); leaning (< W/2); becoming (< 3W/4);
                    on_the_threshold (>= 3W/4 and not offered); ready (an offer is open or standing).
                    For on_the_threshold it also returns the first unmet requirement KIND in the order
                    of vehicles.yaml#readings.lacking (quality, scenes, counted, great deeds, crises,
                    contexts, breadth, balance, currency, conduct). The packet carries {key tag name,
                    band, lacking kind, deed lines}; no number.
Stakes:             none
State writes:       knowledge: the PC has heard this reading (journal, ch.15); nothing else
Narration may not imply: a calling's name; a count, a threshold or how near in any measure; a promise
                    that anything will come; that the reader caused or can grant anything
Examples:           inside: Wren, 3 sessions in, asks the hedge-witch. Archery weighted 52 of 80 [verification: V2a-002] ->
                      becoming: "You are becoming it. Others would see it before you do," and she
                      names the shot at the ford.
                    inside (threshold): weighted 84, counted 9, but quality events 4 of 6 ->
                      on_the_threshold, lacking quality: "You have done it often, and seldom when it
                      was hard."
                    non-example: "How many more fights until I'm an archer?" (out of fiction) -> the
                      DM answers what the codex shows: the Leanings view (04.6.5); numbers stay sealed.
Anchor:             yes. Intent verbs: "be read", "ask what I am becoming", "have my fortune told".
                    Knobs: targets (which leanings the reader speaks to: default the top three; allowed
                    delta: only the one the question names); time_cost (default none; allowed delta: the
                    reader's ritual takes 1 interval). No other knob moves. Degree table: none (no
                    roll). Covers: any in-fiction request to know one's own trajectory. Does not cover:
                    learning another being's tallies (never possible) or the future of the world (the
                    Oracle and ch.15).
Basis:              [R6 V6, A-03 Hawkwind's graded reports] [R3 04.13, G-16] [DL-04-13]
```

**04.6.5 Leanings: what the codex shows of the unrecognized.** `[D]` The codex has one `available` view,
**Leanings**: up to three rows, each a **key tag's plain name** ("the bow", "tracking", "mercy") with its
band word (*leaning, becoming, on the threshold, ready*). Rows at `unformed` are not shown, except a key
named by one of the player's aspirations. The view never shows a calling's name, a number, a threshold or a
lacking kind (the lacking kind is spoken only by a reader in fiction). This is the middle course the research
supports: recognized callings are shown in full, and for the rest only nearness, so a player can pursue an
identity on purpose without the mechanics being announced [R3 04.13, T-6, G-16; DL-04-13]. An aspiration
(ch.02) adds its row to the view and puts its candidate first when several offers are presented; it never
adds weight to any threshold or confirmation [R6 R-A7; 03 Design intent].

### 04.7 The offer protocol

**04.7.1 An offer has three answers, always.**

```
### 04.7.1  Recognition offer                                     [D] [T]
Trigger [T]:        a packet with policy offer (04.4.6); a standing offer whose represent_when is met;
                    a player request to take up a standing or declined offer
Loads in:           core while an offer is open (pause point 7, 12.2.6)
License check:      n/a
Computation [D]:    offer_create {kind: recognition, content: {calling, tier, alternatives}, vehicle,
                    price, represent_when, expires}. The fiction voices the vehicle; then ONE CHOICE
                    block (12.15.6; text in vehicles.yaml#markers) shows, out of fiction, exactly what
                    each answer does. Answers:
                      ACCEPT  -> offer_resolve(accept): PR-04-4 applies the tier as provisional, writes
                                 the price's commitment, starts the pick (PR-04-5), emits recognition_event.
                      DECLINE -> recorded; nothing changes; the calling is not raised again by the engine
                                 until 24 evidence-bearing scenes have passed AND its weighted tally has
                                 grown by W1/2 since the decline; the player may ask for it at any
                                 reflection while it is still eligible. A vehicle's stated decline cost
                                 (V3 refused to the emissary's face: one standing step; V13: the power
                                 remembers) applies only if it was shown in the block.
                      DEFER   -> the offer becomes a STANDING OFFER (04.7.3).
                    If the player moves on without choosing: DEFER.
Stakes:             none (no roll). The price is the stake, and it is shown before the answer.
State writes:       offer (open | accepted | declined | deferred | expired); on accept: callings,
                    competence, licenses, commitments, slots (by ch.05's tools); offer log; recognition_event
Narration may not imply: that declining or deferring loses anything not stated in the block; any number
Examples:           inside: Tracker offered by an old trapper (V2); the player says "not yet" -> defer;
                      the offer stands and returns when she next meets him or at a reflection.
                    inside: the same, "no, I'm no woodsman" -> decline; cooldown; no cost.
                    boundary: the player ignores the block and declares a new action -> defer (12.2.6:
                      offers from ch.04 stay open); nothing is lost.
                    non-example: an NPC in fiction says "choose now or lose it forever" for a personal
                      calling -> forbidden: no personal offer expires while it is eligible (04.7.3).
Anchor:             yes. Intent verbs: "be offered", "take up", "turn down", "put off" a lasting
                    change the world proposes to the character (a pact, a title, a transformation, a
                    post). Knobs: duration (how long the offer stands: default until its expiry rule;
                    allowed delta: a shorter stated window for an institution's or a power's offer,
                    never for a personal one); condition (the price attached, from the closed price
                    list; allowed delta: one price kind). Degree table: none (a choice, not a roll).
                    Covers: any standing proposal with a price. Does not cover: trades and bargains for
                    goods (ch.08, ch.15), institutional ranks (ch.11's offers use this same protocol).
Basis:              [R6 A.5 items 1-6] [C:P5 offer; C:P1 "the player MAY defer"] [12.2.6, 12.15.6] [DL-04-14]
```

**04.7.2 The out-of-fiction marker.** `[D]` The player must always know when an offer is live and what it
costs, and the world must never say so (BRIEF §4; C:VII). So: the fiction comes first and stages the vehicle;
then exactly one OOF block follows, last in the response (12.15 order). A crisis offer is preceded by the
one-line marker `[RECOGNITION] An offer is open (see below). Nothing is lost by waiting; play continues when
you answer or move on.` so that a player in the middle of a fight sees it. The CHOICE block lists, for
**accept**: every competence value, training grade, capability, pick count and family mechanic gained, the
price in full (for an oath, every forbidden act word for word), and the confirmation rule; for **decline**:
the re-offer condition; for **defer**: when it returns and whether it expires. A grant uses one RESULT line
(`grant_result`) with the same contents and the words "you may set it aside at any rest". Texts:
`vehicles.yaml#markers`. Ch.14 renders them; ch.12 owns the block formats (Interface requests propose the
`[RECOGNITION]` label).

**04.7.3 Standing offers.** `[D]` A deferred offer persists in state (`Offer`, 00.6.2) and is listed in the
codex and in the session-start SITUATION block ("Open offers"). `h.04.standing_offers` runs at every
reflection:
- **Re-present** when the vehicle's `represent_when` holds: the next reflection (V7), returning to the
  person (V2, V12) or place (V11, V3's institution), the next crisis on the key (V4, V5), the next sitting
  (V9). The player may also take it up by asking, at any reflection or whenever the recognizer is present.
- **Expire** only as the vehicle states: V3 at the season boundary after next or when the institution's
  status toward the PC falls below 0; V12 after one season (it then continues as V7); V9 per ch.11's
  schedule. **Personal offers (V4, V5, V7, V11) never expire while the candidate stays eligible.** An expired
  institutional offer removes the staging and its price, not the eligibility: the tier is offered again by V7.
- **Withdraw** if the candidate is no longer eligible (events voided, 03 PR-03-4) or a lineage change made it
  moot (04.8.3). A withdrawal is told out of fiction in one RESULT line and voiced by a reading.
- At most **three** recognition offers are presented at one reflection, highest confidence first, an
  aspiration's candidate before others of equal confidence; the rest wait in the queue. At most **one**
  crisis offer per scene.

**04.7.4 The words of an oath.**

```
### 04.7.4  Swearing                                              [J:flag] [D]
Trigger [T]:        the player accepts an offer whose price is price.oath (V4; V11 or V13 for an
                    oath-bearing calling)
Loads in:           core while the offer is open
License check:      n/a (speaking is verb.talk; no roll)
Decisions (J):      1. FAITHFUL WORDS [J:flag] "Do the player's words commit the character to the oath's
                       axes, and contradict none of its forbidden acts?" True only when the text, read
                       plainly, promises conduct on every axis listed in the calling's oath block and
                       excuses none of the listed forbidden acts. False when it promises something
                       else, hedges an axis away ("unless it is inconvenient"), or carves out a
                       forbidden act. Uncertain -> false: say out of fiction which axis or act the
                       words missed and ask once more; the offer stays open. For `words: fixed`
                       callings the block shows the oath text and the player may simply accept it.
Computation [D]:    On true: set_fact(kind commitment, subtype oath) {wording: the player's text verbatim,
                    keeper: the named bonded witness, axes, forbidden_acts [ids], calling, tier};
                    the keeper is registered as a bonded witness on those axes (03.10.4). Each later
                    tier of the same calling ADDS a line the player writes (the oath is restated whole,
                    with the new line, never a second oath).
Stakes:             none at the swearing. The oath's stakes are the Fraying (04.9).
State writes:       commitments; bonded witness; calling.tier
Narration may not imply: that the words themselves are magic formulae; that anyone judged the
                    character's heart (only the record is read)
Worst case (J):     words wrongly accepted that hedge an axis: the stored oath block (axes and forbidden
                    acts from data) still governs, so the hedge has no mechanical effect (class iv);
                    words wrongly refused: one more exchange, nothing lost (class ii).
Examples:           inside: Paladin (axes protection, mercy): "I will stand between the helpless and the
                      blade, and I will not strike the one who yields." -> true.
                    boundary: "I'll protect people when I can." -> uncertain (mercy is not addressed)
                      -> false; the DM says the words left out how she treats the beaten.
                    non-example: the player says only "I accept" to a `words: personal` oath -> not
                      words; ask for them, or the player defers.
Anchor:             yes. Intent verbs: "swear", "vow", "promise before a witness", "bind myself".
                    Knobs: condition (which axes and forbidden acts bind: default those of the calling;
                    allowed delta: for a free promise outside any calling, none: it is a plain
                    commitment of ch.11 with no Fraying); duration (default until released at a season
                    boundary; allowed delta: a stated term). Covers: any solemn promise the player wants
                    recorded. Does not cover: a promise extracted under compulsion (no commitment is
                    written, 03.2.6).
Basis:              [R6 V4, A-01 "spoken in pieces across a conversation"] [R2 #2, #5 individualized
                    truths] [03.10.4] [DL-04-16]
```

**04.7.5 Prices.** `[D]` Every accepted offer binds at most one **price** [verification: V2a-003] from the closed list
(`vehicles.yaml#prices`) in addition to the seat and the shadow, which every calling carries: **oath** (V4;
axes, forbidden acts, a bonded witness), **obligation** (V3, V9; an institution's duties, written by ch.11),
**bond** (V2, V12; a debt to a teacher: a named service or a season's work), **bane** (V13; a standing
weakness shown in full). An offer by V5, V7 or V11 for a calling without an oath carries only the seat and
the shadow. Price-free power feels purchased [R6 A.3]; here even the quietest recognition costs a seat and
records a shadow that may one day show.

**04.7.6 Hybrids, forks and consolidations are offered beside.** `[D]` When a pass finds several candidates
that share a lineage or a branch (a hybrid and the specialist under one of its branches; a broad calling and
a narrow one beneath it; a variant and its base), they are presented in **one** CHOICE block as named
alternatives (`multi_choice` or `replace_choice`), and the engine computes no winner [C:P5; R6 A.5 item 5].
Accepting one withdraws the others that would need the same seat; they return later as fork or consolidation
offers under 04.8.

**04.7.7 Re-offer after a decline.** `[D]` A declined calling is not raised again until 24 evidence-bearing
scenes have passed (03.6.1) and its weighted tally has grown by half its tier-1 threshold since the decline.
The same vehicle is not used for the re-offer. The player may ask for a declined calling at any reflection
while it is eligible; asking is never refused and never priced beyond the calling's own price.

**04.7.8 `recognition_event`.** `[D]` On every grant, accepted, declined or deferred offer, confirmation,
lapse, consolidation, fork, release, Fraying stage change, atonement, turn and revocation, the engine emits
to ch.11 (00.17 Q4):

```yaml
recognition_event:
  id: str
  time: time
  actor: id
  calling: call.*                 # the calling's id; ch.11 never shows the name as a title
  tier: int
  kind: enum        # first | tier | hybrid | variant | fork | consolidation | fold | release | confirm | lapse
                    # | shadow | fraying_stage | atonement | turn | revocation
  policy: enum      # grant | offer | abstain
  answer: enum|null # accept | decline | defer | renounce
  vehicle: veh.*
  witnesses: [id]   # carriers present at the staging (03.10.2); empty for a private vehicle
  scope: [str]      # the scopes of those carriers, plus the institution's or keeper's scope
  institution: fac.*|null         # V3, V9: the faction that asked (ch.11 writes membership, rank, obligations)
  keeper: id|null                 # the bonded witness of an oath
  price: price.*|null
  decline_cost: {kind, amount}|null   # ch.11 applies a standing step only when this is set
  epithet_seed: str|null          # the deed line of the crystallizing event (what ch.11 may build a name from)
  confirmed: bool                 # true when the tier is confirmed (no longer provisional); ch.16's follower
                                  # offers read confirmed tiers >= 2 [integration: IR ch.16 to 04 (b)]
  deed_events: [event id]         # ledger lines quoted in the staging
  fraying_stage: int|null
  tally_snapshot: sealed          # the 03.9 values the decision used (never shown; audit only)
```
Ch.11 uses it for reputation content and score, faction status, rumors and ranks. Ch.04 never writes faction
state; ch.11 never grants capability. `tally_snapshot` satisfies 03.9.5: any recognition can be audited back
to deed lines.

### 04.8 Seats, picks, provisional status and consolidation (Principle VI at character scale)

Principle VI forbids pure additive stacking and asks that new content be provisional by default and that
retirement be structural, telegraphed and bundled at boundary points [C:VI]. At character scale that means:
a fixed number of seats; a fixed pick allowance under ch.05's hard ceiling; every grant on trial until lived;
and four structural retirements (**lapse, fork, consolidation, fold**) that happen only at reflections and
season boundaries, each offered and none imposed. Applying the league idea to one character's grants is an
extrapolation from Path of Exile's content leagues, recorded as such [BRIEF A3; R3 T-3; 00.17 Q12; DL-04-15].

**04.8.1 Seats.** `[D]` A character holds at most **three** deed-keyed callings (specialists, variants,
hybrids) and at most **one** conduct-keyed calling (a vow or a dark calling): three **deed seats** and one
**oath seat** [R3 04.12: Azarinth's two slots, Wandering Inn's merges; DL-04-17]. When a new calling is
eligible and its seat type is full, it is offered with `replace_choice`: consolidate, fork, release, decline
or defer (04.7.6). The engine never evicts.

**04.8.2 Provisional grants: confirmed or lapsed.** `[D]` + `[T]` Every first recognition, tier, pick,
fork and consolidation is `lifecycle: provisional` when made. It works in full; the codex marks it
"(provisional)"; the fiction may voice it as a name that has not yet stuck.
- **Lived.** The measure is the evidence at the calling's key **since the grant**:
  `lived = detail(pc, key, since: granted_at).weighted` (a hybrid: the smaller of its two branches' values;
  a vow: `recent_net ≥ 3` at Fraying stage 0; a dark calling: `recent_net ≤ −3`). Time is counted in
  **evidence-bearing scenes** (03.6.1), so a winter of rest neither confirms nor lapses anything.
- **Confirm** at any `reflection` or `season` boundary (`h.04.provisional_check`,
  `h.04.season_consolidation`) at which at least **12** evidence-bearing scenes have passed since the grant
  and `lived ≥` 18 (fine), 24 (narrow), 36 (broad), 18 on each branch (hybrid). These are three-tenths of
  the tier-1 thresholds: about one session's yield, earned after the grant. The grant becomes `permanent`;
  V10 voices it in one line.
- **Lapse** at the first such boundary at which **24** evidence-bearing scenes have passed and it is still
  unconfirmed.
- **What lapses** is exactly what that grant gave: the tier's competence step, training
  grade, capability, family-mechanic rank and the pick made with it (the ability returns to the pool; its
  slot is freed). A lapsed tier 1 retires the calling and frees its seat. Evidence is untouched, so the
  calling can be recognized again (the decline cooldown of 04.7.7 applies).
- **Warning.** `trg.04.lapse_warning` fires at any reflection where a provisional grant is at least 8
  evidence-bearing scenes old and `lived` is under half of what confirmation needs. The DM voices it (V6 or V10: "the string feels strange
  under your fingers") and shows `lapse_warning`. No lapse happens without at least one earlier warning.
- **Renounce.** At any reflection the player may set aside any provisional grant at no cost (it is treated as
  a lapse with `answer: renounce`). This is what keeps a grant the player's choice [R1 §04].
- **The tier-4 attribute increase** is applied when tier 4 is **confirmed**, never while provisional, so an
  attribute never rises and falls (00.4.3).
In simulation a tier-2 grant lapsed in 181 of 199 runs when the archer stopped shooting at once, in 65 of
199 when she kept on for one more session, in 9 of 199 after two, and in 0 of 199 when she never stopped
(T-04-8 R8).

**04.8.3 Lineage: one identity per line.** `[D]` Two callings are in one **lineage** when their keys are
identical (a variant and its base) or one key is an ancestor of the other (Warrior and Archer; Thief and
Lockbreaker). A character never holds two callings of one lineage. When a candidate is eligible and a calling
of its lineage is held, the candidate is a **fork** offer (04.8.6); when both become eligible in one pass they
are presented as alternatives (04.7.6). Hybrids are not in the lineage of their branches' callings: a hybrid
and a specialist under one of its branches may be held together, or consolidated (04.8.5).

**04.8.4 Picks: abilities come from the shared pool.** `[D]` A calling grants no ability. Each tier raises
the character's **pick allowance**, and a pick is the right to fill one slot of the `calling` partition
(00.17 Q2) from ch.05's one ability pool, gated by the calling's tags.
- **Allowance.** `A = min(S, Σ over held callings of picks_total[tier] + legacy_picks)`, where `S` is the size
  of ch.05's calling partition (reference 12). Cumulative picks by tier: 2, 3, 4, 5, 6 for a deed-keyed
  calling; 1, 1, 2, 2, 3 for a vow or dark calling. Three callings at tier 3 fill a 12-slot partition exactly.
- **Pool gate.** An ability is eligible for a pick made through calling X at tier T when: it is
  `slot_class: calling` and not retired or `adversary_only`; it is not held; its `min_tier ≤ T`; and its
  *first tag* is at or under one of X's `pool_gate.own` tags (**own**), or at or under a `pool_gate.kin` tag,
  the rest of X's branch (**kin**), or it carries a conduct axis in X's `pool_gate.conduct` (**conduct**); an
  oath-gated ability (one with a `conduct_pole`) is eligible only through a calling whose `pole` equals it, so
  a vow never draws a dark ability on the same axis, nor the reverse [integration: IR ch.05 to 04 (a)]. An
  ability the character already holds in the **acquired** partition or on the **shelf** counts as not held
  for this test (promotion, 05.8.6) [integration: IR ch.05 to 04 (b)]. A level-3 calling's own pool is its level-2
  parent's subtree; a branch calling's own pool is the branch; a hybrid's is both branches. An ability whose
  `mod_group` equals a held calling ability's is excluded unless it `replaces` that ability.
- **Candidates.** The engine shows **up to three** eligible abilities, ranked: (0) any eligible ability the
  character already holds in the acquired partition or on the shelf (a **promotion**: it moves into the calling
  slot and keeps its learning; 05.8.6) [integration: IR ch.05 to 04 (b)]; (1) for a V5 awakening, any
  whose first tag is at, under or above the crisis deed's primary tag; (2) any that `replaces` an ability the
  character holds at its top rank; (3) own-pool abilities before kin-pool ones; (4) by the character's own
  weighted tally at the ability's first tag, highest first; (5) an ability shown and passed over at this
  calling's previous pick ranks as if its tally were halved; (6) ties by the engine's logged draw. **What a character is offered is what their deeds point
  to**: the pool is shared, but the three on the table are derived from history, not browsed [C:P5; R3 04.7
  one-of-three; DL-04-18].
- **Choice.** The player picks one, or **keeps the pick** (P1: defer and gamble). An unspent pick is
  re-presented at each reflection with candidates recomputed from the tallies as they then stand.
- **At the cap.** When the allowance already equals the picks held (S reached, or legacy picks outstanding),
  a new pick **replaces** a held calling-partition ability of the player's choice: fork-replacement, never a
  thirteenth slot [C:V; C:VI].
- **Ranks.** A picked ability's rank follows the tier of the calling that holds the pick (04.5.5). For a pick
  carried through a consolidation or fork, the tier read is the higher of the new calling's tier and the
  specialty's `tier_reached` (05.3.9), and so is `T_high` for the Focus maximum (05.6.1): nothing is lost on the
  day, as 04.8.5 promises [integration: IR ch.05 to 04 (c); DL-05-27].
- **Procedure and tools:** PR-04-5. This is "an equivalent tag-gated selection" to a `chosen` fill of the
  00.11 generator: it uses the generator's pool gate, tier gate, `chosen` presentation and mod-group
  exclusion, replaces the weights with evidence, and creates no object because the ability already exists.
  It is registered as the generator domain `gen.pick` (00.11.1, amended at integration).

**04.8.5 Consolidation: several callings become one.** `[D]`

| Kind | Offered when | Target |
|---|---|---|
| **branch** | two or more held callings have keys under the same deed branch | that branch's calling (Archer + Blade → Warrior) |
| **hybrid** | one held calling is keyed under each branch of a named pair in `hybrids.yaml`, and `req.hybrid.1` holds | that pair's hybrid (Archer + Tracker → Ranger) |

Offered at each `season` boundary, and at once when a recognition needs a seat. On acceptance
(`grant`/`retire`, tool #28):
1. **Tier.** The new calling's tier is the highest tier, not above the highest constituent tier, whose
   weighted threshold the new key meets (minimum 1). Its `since` clock starts now.
2. **Retired.** The constituents are set `lifecycle: retired, superseded_by: <new>`: their labels, tier
   ladders, Focus triggers, composites and seats. Their growth paths end [DCC's fork: the generic path is
   retired, R2 4c].
3. **Kept: specialties.** Each constituent's competence entry and training grade persist at their current
   values as a **specialty** of the new calling `{tag, value, grade, tier_reached}`. A specialty no longer
   grows on its own; the new calling's own entries grow with its tiers. Universal capabilities already
   granted are kept: for their scope a specialty counts as a held calling at the tier it had reached.
4. **Kept: picks.** Every held ability stays. `legacy_picks = picks held − picks_total[new tier]`; each later
   tier's new pick first cancels one legacy pick instead of adding a slot. Nothing is lost on the day;
   future growth is partly pre-paid. This is the re-allocation of the calling partition the contract asks
   for: the partition never grows, and consolidation converts two callings' separate allowances into one.
5. **Kept: band.** `inherited_band` = the highest band among the constituents (04.5.6).
6. **Oaths carry.** A constituent's oath continues, restated in the new calling's oath block (every target
   that can absorb a divine-keyed calling carries one). A calling at Fraying stage 1 or higher cannot be
   consolidated, forked or folded: the Fraying is answered first (04.9).
7. **Freed.** Seats: several become one. The consolidation is provisional (04.8.2); a lapse restores the
   constituents as they were.
Retirement here is written as transformation [R1 T-16]: six labels may become one (the Wandering Inn's
*Worldly Princess*), and the character on the day is exactly as capable as before, with a broader name and
room to become something else [R3 04.3, #5; DL-04-17].

**04.8.6 Fork and fold.** `[D]`
- **Fork (replacement inside a lineage).** *Narrow*: a held broad or level-2 calling is replaced by an
  eligible calling keyed beneath it (Thief → Lockbreaker). *Broaden*: a held narrower calling is replaced by
  an eligible calling keyed above it (Archer → Warrior), which is consolidation with one constituent. *Variant*:
  a base and its variant replace each other (Brawler → Monk). In each case the rules of 04.8.5 steps 1–7
  apply with one constituent: the old key's competence persists as a frozen specialty, picks stay, the old
  ladder is retired. A fork is the DCC specialization fork: the growth path forks into a replacement, never
  an addition [C:VI].
- **Fold into base.** The player may fold any confirmed calling at a `season` boundary, and the engine
  **offers** a fold when a permanent calling has `recent(key) = 0` over 48 evidence-bearing scenes (a
  relabel offer for an identity no longer lived; 03.9.4, R3 T-8). Folding retires the calling and frees its
  seat. Folded into the character's base, permanently: its training licenses at grade `trained`, and a
  specialty of **+2** at its key (an origin's value, 00.3.6). Released: its tier capabilities (unless another
  calling grants them), family mechanic, and picks (the abilities return to the pool). This is PoE2's
  fold-into-base: what was a build choice becomes part of the floor, and the choice is retired
  [R3 #10]. A fold is never automatic: declining the offer leaves the calling as it is, and capability
  earned by deeds never decays on its own (03.6.3).

**04.8.7 The season boundary.** `[D]` `h.04.season_consolidation` (PR-04-8) is the one bundled, telegraphed
point for structural change [C:VI]: (1) test provisional grants (04.8.2); (2) offer consolidations, forks and
folds that have become available; (3) allow **one re-pick per calling**: swap one held calling ability for
another eligible candidate (PR-04-5), free of charge; a hybrid may instead re-choose one road; (4) lapse any
calling held at Fraying stage 3 since the season boundary before last (04.9.6). Outside the season, a pick
may be swapped by ch.15's **Retrain** downtime activity (one week per pick) [R5 AD-05]. A recognized
calling's grants never change at any other time, and never by reinterpretation [R3 04.14].

### 04.9 Shadows, forbidden acts and the Fraying

**04.9.1 Every calling has a shadow.** `[D]` + `[T]` Each calling entry carries a **shadow**: a name, one or
two conduct axes, and the dark calling it **turns to**. The shadow is the direction the identity corrupts
when pursued without its counterweight: the Warrior's *Butcher* (mercy, restraint), the Scholar's *Hoarder of
Secrets* (generosity, humility), the Merchant's *Profiteer* [R6 A-11, R-A6]. The shadow **shows** when, on any
of its axes, `recent_net ≤ −6` or `strain ≥ 4` (`req.shadow`), checked at each `scene_start`
(`h.04.fraying_check`). When it shows: the engine emits `recognition_event(kind: shadow)` so that ch.11 may
turn an epithet or seed a rumor; V8 becomes available; and, if the matching dark calling is itself eligible,
its V13 offer may be made. **For a calling without an oath, the shadow removes nothing**: a cruel archer is
still an archer. The world notices; that is all.

**04.9.2 Oaths, forbidden acts, and the three stages.** `[D]` + `[T]` Callings with an `oath` block (every
divine-keyed calling, the seven oath-bearing hybrids, the Monk, every vow, every dark calling) name a
**keeper** (the bonded witness), one or two **axes**, and their **forbidden acts**, each a sentence shown in
full before the oath is sworn and matched word for word when cited (03.3.3's `forbidden_ref`). The
**Fraying stage** is a pure function of ch.03's conduct measures on the oath's axes (the worst axis counts):

| Stage | Entered when (oath) | Entered when (dark calling: its reversed oath) | Voice (V14) |
|---|---|---|---|
| 0 Clear | strain 0–3 and no unatoned forbidden act | `recent_net` on its axis ≤ +3 | — |
| 1 **Dimmed** | `strain ≥ 4` | `recent_net ≥ +4` | the keeper withdraws: dimmer power, a cooler welcome |
| 2 **Fraying** | `strain ≥ 8` | `recent_net ≥ +8` | the keeper speaks |
| 3 **The Choice** | `strain ≥ 12`, **or** any unatoned forbidden act | `recent_net ≥ +12` | the keeper asks: atone, or turn |

Strain rises by the settled negative points and falls by half the positive ones (03.8.3), so **a single
contrary act only warns**: the gravest single entry is 4 points (stage 1), and one scene can settle at most 7
(03.8.2). Stage 3 from strain alone needs at least two scenes of grave wrong. Only an act the oath named in
advance can reach stage 3 at once, and the player read that sentence before swearing [R6 V14; Ultima IV's
Skull]. Every stage change raises `trg.04.fraying`, is voiced in the fiction in the scene it is detected, and
is shown in `fraying_result` with what is now inactive, what clears it, and what would cause the next stage.
A stage falls again as strain falls (deeds of the positive pole, at the half rate) or by atonement.

**04.9.3 What each stage does.** `[D]`

| Stage | Mechanical state of the calling |
|---|---|
| 1 Dimmed | its family mechanic (composite, boon or Focus trigger) is inactive; abilities carrying `requires_conduct` on the strained axis are unusable (G4 by an active restriction, 00.9.3 b); it cannot crystallize a new tier |
| 2 Fraying | as stage 1, and its **highest tier is suspended**: competence, training grade, capability, ranks and that tier's pick are read as one tier lower (a tier-1 calling instead pays +1 Focus on each of its abilities, `eff.focus_cost_step`) |
| 3 The Choice | the calling is **suspended**: none of its grants apply and it does not count toward `power_band`; its training licenses stay at `trained`; nothing is yet removed |

Suspended grants are inactive, not deleted: they return in full when the stage clears. Narration may not
describe a suspended power working (INV-8), nor may it call the character any pole.

**04.9.4 Atonement.**

```
### 04.9.4  Atonement                                             [J:enum] [D]
Trigger [T]:        the player chooses "atone" at stage 3 (the CHOICE block), or asks to atone at stage 1
                    or 2 (it is always available once a stage is entered)
Loads in:           core while trg.04.fraying is active; situation.downtime.*, situation.rest.sanctuary
License check:      n/a (the atoning deeds are ordinary beats under their own licenses)
Decisions (J):      1. FORM [J:enum], proposed by the DM from the three forms and chosen by the player:
                       RESTITUTION: true only when a wronged party or their kin or community exists in
                         state and can be reached; the DM names a concrete undertaking that makes them
                         whole or submits to their judgment, written as a thread (ch.11) with its own
                         clue placements. False when no wronged party survives or can be found.
                       PENANCE: true only when the keeper has a place or representative the PC can reach
                         (a shrine, an order's house, the ideal's own ground); one week of downtime
                         there and one cost at S3 from 01's menu, of the form the keeper's nature
                         suggests (coin given away, a relic surrendered, harm borne). False for a keeper
                         with no place (then service or restitution).
                       SERVICE: always available: deeds of the oath's positive pole, each a conduct
                         entry grounded as 03.3.3 requires.
                       Default when unsure: service.
Computation [D]:    create_clock {id: clk.atonement.<calling>, kind: progress, segments: 4 (stage 1 or 2)
                    or 6 (stage 3), visibility: public, tick_sources: a settled positive conduct entry on
                    the strained axis of magnitude 2 -> 1, of magnitude 4 -> 2; the penance week completed
                    -> 3; the restitution thread completed -> fills it}. While the clock is open at stage
                    3 the calling is read at stage 2 (it works, one tier down), unless a new negative
                    entry settles, which re-suspends it. On completion: record_evidence(op: atonement,
                    axis, supersedes: every unatoned negative event on the axis) (03.8.4): strain 0, the
                    forbidden citations cleared unless marked unatonable, stage 0, the clock closed.
                    recognition_event(kind: atonement).
Stakes:             none of its own; each atoning deed has its own frame
State writes:       clock; thread (restitution); commitments (the oath restated); evidence (atonement
                    event); calling.fraying_stage, suspended
Narration may not imply: that atonement erased what was done (the ledger keeps every deed, marked
                    superseded; witnesses and ch.11's reputation remember); that the keeper is appeased
                    before the clock completes
Worst case (J):     a form offered that cannot be completed (the wronged party proves unreachable): the
                    player may switch forms at any reflection, keeping the ticks already made (class iv).
Examples:           inside (restitution): Wren killed a yielded scout under the Ford-Warden's oath
                      (WE-03-10). The DM names it: carry his sword to his kin at Harl's Crossing and
                      stand their judgment; a thread with three clue placements; completing it fills the
                      clock.
                    inside (service): a Hospitaller at strain 5 spares two foes at real cost in later
                      scenes (magnitudes 2 and 4) -> 1 + 2 ticks of 4; one more completes it.
                    boundary: an unatonable act (the Pactbound broke the pact's stated term) -> atone is
                      not offered; the choice is turn or release (04.9.5).
                    non-example: "I say a prayer and feel sorry." -> no write, no tick (03.3.3: remorse
                      is not a deed).
Anchor:             yes. Intent verbs: "atone", "make it right", "do penance", "make amends". Knobs:
                    time_cost (the penance: default 1 week; allowed delta: 1 day at a keeper's own high
                    place); duration (clock size: default per stage; allowed delta: one size smaller when
                    the wrong was a single magnitude-2 entry); stakes (the cost severity of penance:
                    default S3; allowed delta: S2 when strain < 8). Degree table: none of its own (the
                    clock). Covers: making amends to any keeper, person or community with a record of
                    the wrong, including NPC grudges with no oath involved (the clock's completion then
                    writes a standing step, ch.15). Does not cover: undoing reputation (ch.11).
Basis:              [C:P5 "atone rather than instantly and irreversibly losing power"] [R6 V14, A-02]
                    [R2 #6] [03.8.4] [DL-04-22]
```

**04.9.5 Turn.** `[D]` At stage 3 the player may instead **turn**: the calling is replaced, as a fork
(04.8.6), by its shadow's `turns_to` calling at the same tier if that calling's `neg` threshold for the tier
is met, else at the highest tier that is (minimum 1). A deed-keyed calling that turns keeps its key
competence as a frozen specialty and its picks other than those with `requires_conduct`; the dark calling
takes the oath seat (displacing any vow, which is released) and frees the deed seat. V13 voices it and its
price (the bane on the entry) is shown first. A vow turns to the dark calling of the same axis. A dark
calling at its own stage 3 has no further fall: its choices are **recommit** (deeds of its pole bring
`recent_net` down), or **release**, after which the vow of the same axis may be offered when eligible.
"Atone or turn" is offered, never imposed; a third answer, **release**, lets the calling go with no
replacement, and **defer** leaves it suspended.

**04.9.6 Revocation, and permanence.** `[D]` A calling still at stage 3 at the **second** `season` boundary
after the stage began, with no atonement completed, **lapses**: it is retired, its picks return to the pool,
its seat is freed, its training licenses stay at `trained` (`recognition_event(kind: revocation)`). By then
the player has seen every stage notice (one when a forbidden act opened stage 3, three when strain did) [verification: V2a-004], the CHOICE block at every reflection, and `lapse_warning` at the
first of the two boundaries. That is the meaning of "never a surprise". A **Paragon** calling (tier 5) cannot
lapse and cannot be revoked: at stage 3 it stays suspended until atoned, however long that takes
[Stormlight's Fifth Ideal: R2 #2]. Tier 5 is also exempt from the staleness fold offer.

### 04.10 The gated special trait: the Taking

Constitution P5 reserves the direct taking of a defeated creature's power as a calling-gated capability, not
the default reward of combat (which is loot, ch.08). This part authors what no source supplies: trigger, cap,
cost and failure [R2 4e; R3 04.18; C:P5].

**04.10.1 The gate.** `[D]` Only the **Devourer** (`call.devourer`, a variant of the Bestiarist, offered
only by V13) grants `lic.call.taking`. Anyone else who declares "I absorb its power" is at gate class G3:
the license's crude fallback is to harvest the body for materials (ch.08), and its acquisition path is the
Devourer's recognition. A suspended or lapsed Devourer keeps the **library** (04.10.4) but can neither take
nor use slotted powers until restored.

**04.10.2 The Taking.**

```
### 04.10.2  The Taking                                           [J:enum] [D]
Trigger [T]:        the player declares a Taking on a creature the PC defeated, and data/gen_absorb.yaml
                    #trigger holds (engine-checked): the defeat is RESOLVED by the PC's own declared beat
                    or ability; the archetype has an absorbable pool after the pool gate; the PC perceived
                    the creature act in this scene; the declaration is before scene_end or within 1
                    interval, engaged with the body or the yielded creature; no Taking was attempted on
                    this creature; none has succeeded since the last rest_long
Loads in:           situation.conflict.* (at conflict_end), situation.exploration.*
License check:      lic.call.taking (G2). Without it: G3 redirect (04.10.1)
Decisions (J):      1. CIRCUMSTANCE [J:enum], how the character engaged it (the fill-quality axis, 00.11.2):
                       decisive: true only when the PC's own resolved success defeated it in a fight in
                         which the PC was never Staggered or Dying. False for a foe finished by an ally,
                         a companion or a hazard.
                       narrow_survival: true only when the PC's own success defeated it AND the PC was
                         Staggered or Dying during the conflict, or the defeating frame was lethal.
                       merciful: true only when it yielded or was subdued alive by the PC's own beat and
                         is spared (a mercy fact is written). False for a mindless thing that cannot
                         yield; false if it is then killed.
                       scavenged (default when unsure): none of the above. The pool gate refuses: no
                         Taking is possible.
                       The engine checks each against the scene log (harm states, frame ids, facts);
                       the DM classifies only between options the log leaves open.
Computation [D]:    PR-04-9. Spend 2 Focus. Frame: verb.endure, Resolve, deed tag
                    deed.lore.bestiary.monsters (the calling's competence applies); DC = the effect DC
                    of the creature's threat band tier (T1 Easy ... T5 Legendary); stakes Risky when the
                    creature's band <= power_band + 1, Dire when higher; never lethal; reach Standard.
                    The OFFER is shown; the player may withdraw (the Focus is then not spent).
                    SUCCESS: generate(gen.absorb, creature, circumstance, degree): pool gate by the
                      creature's tags (excluding cannot_absorb, adversary_only, creature.folk); tier cap
                      by its band and by calling tier + 1; fill by circumstance: decisive -> signature
                      (the creature's signature power, guaranteed); narrow_survival -> biased (weights
                      x3 for entries with bias `ward`); merciful -> chosen (the player picks from up to
                      three). ONE power is written to the library.
                    CRITICAL SUCCESS: the same, Greater (+1 tier within the tier rule).
                    FAILURE: nothing is taken; the declared cost applies (01's READ table: S2 at Risky,
                      S3 at Dire) as cost.harm (the creature's own harm tag) or cost.drain; no second
                      attempt on this creature.
                    CRITICAL FAILURE: as failure, one severity rung higher, and the creature family's
                      bane attaches until the next rest_long.
Stakes:             declared before the roll: success -> one power of the stated tier range; failure ->
                    the cost shown; never death
State writes:       Focus; frame; library (acquired-partition candidates); effect_instance (bane on
                    critical failure); evidence (the Taking is the PC's declared deed, 03)
Narration may not imply: a power the generated output does not hold; a weakness, appetite or change of
                    nature beyond the bane's literal text (SG-15; the probe's invented cold
                    vulnerability); that the creature's mind or memories came with it
Worst case (J):     circumstance one option off: the fill method differs (a guaranteed signature instead
                    of a biased draw, or the reverse) for one power in a library of 4 to 12; the
                    circumstance and the log entries it cited are in the generation log (class iv).
Examples:           inside (decisive): Wren's arrow kills the cinder hound (T2) and she was never below
                      1 Vitality -> decisive -> signature: Ember Heart at tier min(2, calling tier + 1).
                    inside (narrow_survival): the same hound dropped her to Staggered before she killed
                      it -> biased toward wards: Thick Hide is three times as likely as Predator's Nose.
                    boundary (merciful): a drake yields and is spared -> chosen: she picks among up to
                      three of its powers. If she then kills it, the circumstance is false and the
                      Taking is refused.
                    non-example: the hound was killed by the caravan guards while she watched ->
                      scavenged -> refused; she may harvest the body (ch.08).
Anchor:             yes. Intent verbs: "take", "absorb", "drink in", "carry away" a quality of a thing
                    one has overcome. Knobs: dc (source: default the creature's band tier; allowed delta:
                    one tier lower when the creature is spared and willing); stakes (default by band
                    difference; allowed delta: none upward); focus_cost (default 2; allowed delta: none);
                    targets (default one creature). Degree table: above. Covers: any attempt by a holder
                    of the license to draw a lasting power from a defeated or yielding being. Does not
                    cover: items (ch.08 loot), learned arts (ch.05 emulate), possession or mind-reading.
Basis:              [C:P5] [00.11] [R2 4e, #43, #47] [R3 04.18] [R6 A-28]
                    [R: https://finalfantasy.fandom.com/wiki/Learning] [DL-04-19, DL-04-20]
```

**04.10.3 The cap: a library and an active set.** `[D]` Powers taken go to a **library** whose size is 4, 6,
8, 10, 12 by the Devourer's tier; at the cap a new power replaces one the player names. A power is usable
only while **slotted** in the `acquired` partition (ch.05; reference 4 slots, shared with everything else
acquired), and the slotted set changes only at a `rest_long`. Taking the same power again at a higher tier
replaces it (INV-13). Uncapped copying is the failure the constitution names; the library keeps the
collecting and the slots keep the power bounded [C:V; R3 04.18; Final Fantasy XIV's limited active set].

**04.10.4 The cost.** `[D]` Three costs, kept separate [C:P12]: **Focus** 2 per attempt; a **slot** per
power in use; and a **bane** while any power of a creature branch is slotted (`gen_absorb.yaml#banes`): beasts
scent a rival (−2 on Talk and Handle with beasts); undead powers double radiant harm taken; fiendish powers
double holy harm and make sacred wards treat the carrier as a fiend; and so on, one instance per branch
however many of its powers are slotted. The bane is the qualitative tax that Hemalurgy charges and that the
healer-who-stopped-needing-anyone lacked [R2 #47, #56]. The Devourer's shadow is **the Hunger** (mercy,
restraint); it turns to the Pitiless.

**04.10.5 The pool.** `[D]` `gen_absorb.yaml#pool` holds 27 powers gated by creature tags (beast, undead,
spirit, fiend, construct, elemental, dragon, horror), each a short list of core effects by tier, with literal
positive-scoped text. The **human-like folk** (human, elf, dwarf, halfling, orc, goblin; `no_pool`) have no
pool: what they can do is learned, and is learned by emulation (ch.05). Giant-kin and beastfolk carry
natural powers and are gated like any creature (a troll's or giant's Stone Grip; a gnoll's or ratfolk's
Predator's Nose; a lizardfolk's Gills and Scale Ward). Ch.09 names each archetype's signature entry and any
`cannot_absorb` exclusions; each named entry records the archetypes that name it in `signature_of` (25
entries, 46 archetypes), which the decisive fill and `gen.item_ability` read, and ch.09's generator fails if
the two disagree [revision: I-020; DL-04-21; DL-04-26].

### 04.11 Ranks, teachers and endings

**04.11.1 Tier is capability; rank is a seat.** `[D]` A **tier** comes only from the character's own
evidence and is never limited by how many others hold it. A **rank** is a title, office or seat in an
institution, owned by ch.11: it may be seat-limited, contested, granted and stripped, and it confers
standing, resources and obligations. **Losing a rank never removes a tier, and holding a rank never grants
one** [00.17 Q22; R6 R-A5, A-22].

**04.11.2 Trials.** `[D]` A rite or trial (V9) tests for rank. If the character accepts a tier offer staged
as a trial, the tier is applied on acceptance; the trial's check decides only whether the rank is given now
or at a later sitting. A failed trial delays the rank and nothing else.

**04.11.3 No conferral of capability.** `[D]` No authority can give a calling to a character whose record
does not support it [C:P5; R3 T-13]. What an authority **can** do, each through its own chapter: give
**rank** (ch.11); give **training** by a license's mentor path and ch.15's training activity, whose
`cnt.training` units count toward at most half of a counted requirement (04.3.3); lend an **item** that
licenses a capability while carried (ch.08; a relic never feeds a tier, 00.11.5); and **voice** a recognition
the tallies already support (V2, V3, V9). A patron's "gift of power" (V13) is an offer of a calling the
record already supports, with a price.

**04.11.4 The calling's ending.** `[D]` When any calling is confirmed at tier 5, `apotheosis_available(pc)`
becomes true. Ch.11's retirement procedure may then offer the **Apotheosis** ending (the paladin's
ascension, the ranger who walks into the wood), always as an offer and never forced [R6 D-06, D-07, D-R1]. The
retirement offer (`[RETIRE]`, 11.13) uses this chapter's offer protocol (04.7: accept, decline, defer), and its
Apotheosis forms are `legacy.yaml#apotheosis_forms`, keyed by deed branch until a calling entry carries its
own `apotheosis` text, which ch.11 then reads first [integration: IR ch.11 to 04]. At
any retirement or death, every calling, tier, pick and library entry is retired wholesale (ch.11's legacy
procedure, R6 D-R2 step 5): the largest structural retirement in the game. A successor starts unrecognized,
at the floor of 00.3.6; a predecessor who survives may be the successor's V2 mentor.

---

## Procedures

**PR-04-1 The recognition pass.** `[D]` (handler `h.04.recognition_pass` at `reflection`, phase 8, after
`h.03.recency_update`; also the body of `evaluate_recognition(reflection)`)
1. Read 03's reflection digest (03.6.4): dirty nodes and axes, new crisis and peak events, strain changes,
   forbidden citations.
2. **Fraying first.** Run PR-04-7 for every oath-bearing calling. A calling at stage 1 or higher is skipped
   in steps 3–6.
3. **Tier readiness.** For each held calling whose key (or roads, or axis) is dirty: evaluate
   `req.<ladder>.<tier + 1>` with `since` = its last crystallization. If met, mark the tier **ready** and
   record the crystallizing event (04.5.8).
4. **Candidates.** For each calling in `callings.yaml` keyed on a dirty node or axis and not held: evaluate
   its tier-1 requirement set (and a variant's added requirement). Collect the eligible ones.
5. **Confidence and policy** for each eligible candidate (04.4.2, 04.4.3), including the currency floor, the
   decline cooldown, clear field, seats and lineage. Mark forks and consolidations (04.8.3, 04.8.5).
6. **Order and cap.** Sort offers by confidence, highest first (an aspiration's candidate first among
   equals; tier-ups before first recognitions). Keep three; queue the rest for the next reflection.
7. For each grant: PR-04-4 steps 4–8 with `policy: grant`. For each offer and each ready tier: PR-04-3, then
   `offer_create`; alternatives in one block (04.7.6).
8. Compute readiness bands (04.6.4) for the Leanings view; if a band changed and nothing else was voiced this
   reflection, return one reading packet.
9. Write the `tally_snapshot` of every decision to the offer log. Return the packets (04.4.6).

**PR-04-2 The crisis check.** `[D]` (handler `h.04.crisis_check` at `beat_end`, phase 8)
1. If this beat recorded no evidence event with `crisis: true`, or a crisis offer was already made in this
   scene, stop.
2. Find the callings (held, for their next tier; or unheld, for tier 1) whose key covers the event's primary
   tag or a grounded secondary, and whose readiness band was `on_the_threshold` or `ready` at the last
   reflection. If none, stop.
3. Evaluate each with `include_pending: true` (03.5.6). Keep the eligible ones; apply the policy (a grant is
   staged as an offer in a crisis: the player is busy, and nothing is lost by asking).
4. Take the one of highest confidence. PR-04-3 with trigger class `crisis` (V5, or V4 for an oath-bearing
   calling). Raise `trg.04.crisis_offer`; the turn loop reaches pause point 7 after the beat's narration.
5. Accept → PR-04-4 now, and the first pick's candidates rank the crisis deed's tag first (PR-04-5).
   Let it pass → standing offer. Refuse → decline.

**PR-04-3 Selecting the vehicle.** `[D]` + `[J:enum]` See 04.6.2 and `vehicles.yaml#selection.steps`. If the
only vehicle that fits needs an NPC who does not exist yet (V2, V12), the engine asks ch.12's lead engine to
place one as a lead (12.8) with `role_tags` from the calling's key or branches; until that NPC is in a scene,
the offer is made by V7 and gains `represent_when: return_to_person`.

**PR-04-4 Resolving an offer and applying a tier.** `[D]`
1. Present: fiction (the vehicle), then the CHOICE block (04.7.2). The turn pauses (12.2.6 point 7).
2. `offer_resolve(offer_id, answer)`. **Decline:** record `declined_until`; apply a decline cost only if the
   block showed one; emit `recognition_event(answer: decline)`; stop. **Defer or no answer:** status
   `deferred`; set `represent_when`; emit; stop.
3. **Accept.** If the price is an oath: 04.7.4. Write the price's commitment. If a seat is needed and none is
   free, the block was `replace_choice`: carry out the chosen consolidation, fork or release first
   (PR-04-8 steps 3–5).
4. `grant(pc, calling tier, provisional: true, source: offer id)`: set `callings[].tier`, `lifecycle:
   provisional`, `granted_at` (time, scene, evidence-scene index), `crystallized_by`, `vehicle`.
5. Competence (04.5.2); training grades; the tier's capability license; the family mechanic's rank (04.5.5).
   Tier 4: note the attribute increase as pending confirmation (04.8.2).
6. Raise the pick allowance; run PR-04-5 for each new pick (a legacy pick is cancelled instead, 04.8.5).
7. Emit `recognition_event` (04.7.8). Ch.12 adds a rotation facet for a new calling (12.9.1).
8. Show the RESULT line of changed shown state. Narration follows the vehicle's rules; one line, no list.

**PR-04-5 A pick.** `[D]` (player choice at pause point 8)
1. Build the eligible set by the pool gate of 04.8.4 (own, kin, conduct; `min_tier` ≤ the calling's tier).
2. Rank (04.8.4) and take the first three. If fewer than one is eligible, the pick is **kept** and
   re-presented at the next reflection.
3. Show `pick_choice` with each ability's literal active-rank text (ch.05's data, verbatim).
4. The player picks one → ch.05's `grant` writes it to `slots.calling` with `source: {calling, tier}`,
   provisional. If the allowance is full, the player first names the held ability it replaces; that ability
   is retired from the character (`retire`), not from the pool.
5. Or the player keeps the pick. Nothing is lost; candidates are recomputed next time.

**PR-04-6 Testing provisional grants.** `[D]` (`h.04.provisional_check` at `reflection`;
`h.04.season_consolidation` at `season`)
1. For each provisional grant, count the evidence-bearing scenes since `granted_at` (n) and compute `lived`
   (04.8.2).
2. If n ≥ 12 and `lived` meets the ladder's value: `lifecycle: permanent`; apply a pending tier-4 attribute
   increase (the player chooses the attribute now); emit `recognition_event(kind: confirm)`; V10. Stop.
3. If n ≥ 24: if a warning for this grant was shown at an earlier boundary, **lapse** it (04.8.2), emit, show
   `lapse_result`; if none was ever shown (it aged past the test with no reflection between), show the
   warning now and test again at the next boundary.
4. Otherwise, if n ≥ 8 and `lived` is under half the ladder's value: raise `trg.04.lapse_warning` (once per
   grant per boundary).
5. `renounce` by the player at any reflection: as step 3's lapse, at once.

**PR-04-7 The Fraying check.** `[D]` (`h.04.fraying_check` at `scene_start`, phase 8; also PR-04-1 step 2)
1. For each oath-bearing calling: read `conduct(axis)` for each oath axis; stage = the highest stage any axis
   reaches (04.9.2). For a dark calling read `recent_net`.
2. If the stage rose: set `fraying_stage`; apply 04.9.3; raise `trg.04.fraying`; V14 is voiced in this scene's
   opening; show `fraying_result`; at stage 3 show `fraying_choice` (pause point 7) and start the lapse count.
3. If the stage fell: lift the corresponding suspensions; one V10 line; RESULT.
4. Tick open atonement clocks from the newly settled positive entries (04.9.4); complete them if full.
5. For every calling: if `req.shadow` newly holds on a shadow axis, emit `recognition_event(kind: shadow)`
   once per season per axis.

**PR-04-8 The season boundary.** `[D]` (`h.04.season_consolidation` at `season`, phase 8)
1. PR-04-6 for every provisional grant.
2. Revocation: any calling at stage 3 since the season boundary before last, with no atonement completed and
   tier below 5, lapses (04.9.6).
3. Consolidations: for each branch with two or more held callings, and each named pair with a held calling
   under each branch and `req.hybrid.1` met, create a consolidation offer (V12 for a hybrid, V7 otherwise).
4. Forks: for each held calling with an eligible lineage candidate, a fork offer. Folds: for each permanent
   calling below tier 5 with `recent = 0` over 48 evidence-bearing scenes, a fold offer; and the player may
   fold or release any confirmed calling.
5. On acceptance of 3 or 4: apply 04.8.5 steps 1–7 (or 04.8.6); emit `recognition_event`.
6. Re-pick: offer each calling one swap (PR-04-5 with the swapped ability returned to the eligible set), or
   one road for a hybrid.
7. Everything this handler changes is shown in one RESULT block; everything it offers, in at most three
   CHOICE blocks, the rest queued to the next reflection.

**PR-04-9 The Taking.** `[J:enum]` + `[D]` (04.10.2)
1. GATE: `lic.call.taking` held and not suspended; `gen_absorb.yaml#trigger.conditions` all true. Otherwise
   G3 with the fallback and path, or G4 with the failed condition named ("you were not the one who brought it
   down").
2. Classify the circumstance; the engine checks it against the scene log. `scavenged` → refuse.
3. `frame_check` with the taking_check fields; show the OFFER (the tier range that success would give, the
   bane of the creature's branch, the cost on failure). Commit → spend 2 Focus → `roll_check`.
4. Success or better: `generate(gen.absorb, creature, circumstance, degree, options)`; for `chosen`, the
   player picks among up to three (pause point 8). Write the power to the library; if the library is full the
   player names the power it replaces.
5. Failure: `apply_costs` with a form from `failure.cost_forms_allowed`; on a critical failure also apply the
   branch's bane until `rest_long`.
6. RECORD: the frame; evidence (PR-03-1); the generation log. Narrate only what the output holds.
7. Slotting happens at the next `rest_long`: the player chooses which library powers fill free acquired
   slots; each slotted branch's bane is applied (`apply_effect`).

---

## Tables

Tables embedded in Rules are canonical there and indexed here: **T-04-4** requirement sets (04.3.2, 04.3.4);
**T-04-6** tier grants (04.5.1) and power band (04.5.6); **T-04-7** coverage audit (04.2.7). Every number is
in `data/callings.yaml`; every vehicle in `data/vehicles.yaml`.

**T-04-1 The roster by family.** `[D]` (index; `data/callings.yaml` is canonical. Level-3 callings in italics
under their parent.)

| Family (branch calling) | Level-2 callings (tag → name) | Level-3 callings |
|---|---|---|
| martial (**Warrior**) | blade Blade · axe Hewer · bludgeon Mauler · polearm Spearhand · archery Archer · thrown Hurler · unarmed Brawler · shield Shieldbearer · armor Ironclad · tactics Tactician · mounted Cavalier · athletics Athlete | *Duelist* (blade.fencing) · *Wrestler* (unarmed.wrestling) · *Lancer* (mounted.charge) · *Acrobat* (athletics.acrobatics) · *Champion* (tactics.single_combat) · *Siege-master* (tactics.siege) |
| guile (**Rogue**) | stealth Shadow · thievery Thief · deception Trickster · disguise Masquer · ambush Ambusher · poisoncraft Poisoner · escape Escapist · streetwise Fixer | *Assassin* (ambush.assassination) · *Lockbreaker* · *Cutpurse* · *Trapspringer* (thievery.*) · *Forger* (disguise.forgery) · *Swindler* (deception.con) · *Smuggler* (streetwise.smuggling) · *Infiltrator* (stealth.infiltration) |
| wilds (**Wayfarer**) | survival Survivor · tracking Tracker · navigation Pathfinder · animals Beast-handler · foraging Forager · seafaring Mariner | *Herbalist* (foraging.herbs) · *Falconer* (animals.falconry, proposed tag) · *Rider* (animals.riding) · *Hunter* (tracking.hunting) · *Delver* (navigation.underways) · *Pilot* (seafaring.piloting) |
| lore (**Scholar**) | history Antiquarian · languages Linguist · bestiary Bestiarist · medicine Physician · engineering Engineer · law Jurist · arcana Loremaster · religion Theologian · investigation Investigator | *Surgeon* (medicine.surgery) · *Cryptographer* (languages.ciphers) · *Barrow-reader* (history.ruins) |
| arcane (**Wizard**) | fire Pyromancer · frost Frostbinder · storm Stormcaller · earth Geomancer · illusion Illusionist · divination Diviner · warding Abjurer · mind Mesmerist · summoning Summoner · necromancy Necromancer · alteration Transmuter | *Spellbreaker* (warding.countering) · *Bonecaller* (necromancy.raising) |
| divine (**Priest**; all oath-bearing) | healing Healer · warding Sanctifier · smiting Templar · rites Celebrant · oaths Oathkeeper · revelation Oracle · exorcism Exorcist · pact Pactbound | *Gravekeeper* (rites.funerary) |
| primal (**Druid**) | growth Greenwarden · beastkin Beast-speaker · weather Weather-worker · shapeshifting Skinchanger · spirits Spirit-talker · elements Elementalist · hexcraft Hexer | *Cursebreaker* (hexcraft.unhexing) |
| influence (**Envoy**) | persuasion Advocate · command Captain · performance Bard · intimidation Menace · intrigue Schemer · trade Merchant · etiquette Courtier · insight Confidant · teaching Mentor | *Minstrel* (performance.music) · *Skald* (performance.storytelling) · *Questioner* (intimidation.interrogation) · *Venturer* (trade.venture) |
| craft (**Artisan**) | smithing Smith · woodcraft Wright · leathercraft Tanner · textiles Weaver · alchemy Alchemist · cookery Victualler · building Builder · artifice Tinker · jewelcraft Jeweler · enchanting Enchanter · scribing Scribe | *Bowyer* (woodcraft.bowyery) · *Weaponsmith* · *Armorer* (smithing.*) · *Brewer* (cookery.brewing) · *Apothecary* (alchemy.potions) · *Cartographer* (scribing.cartography) · *Clockmaker* · *Trapwright* (artifice.*) · *Runescribe* (enchanting.inscription) |

Variants: **Monk** (Brawler's key + restraint) · **Devourer** (Bestiarist's key + a hunter's record).

**T-04-2 Optional fields of `callings.yaml`.** `[D]` Added by this chapter to SCHEMAS' required fields:
`breadth` (fine | narrow | broad | hybrid | vow | dark) · `family` · `pole` · `attributes` [2] · `pool_gate`
{own, kin, conduct} · `variant_of`, `variant_requirement` · `hybrid` (row id), `roads` · `consolidates_from` ·
`special_capability`, `generator` · `price` · `boon` [{rank, at_tier, effect_id, params, text}] ·
`focus_trigger` (id into `families`). Top-level keys: `tier_ladder`, `power_band`, `requirements`, `policy`,
`seats`, `picks`, `provisional`, `consolidation`, `fraying`, `readiness`, `families`. A hybrid's competence
tag is written `road:<branch>`.

**T-04-3 The hybrid table (all 36 pairs).** `[D]` (`data/hybrids.yaml`; composite in
`data/composites.yaml owner-block 04`. The lever shown is rank 1's: a success on the first-named road grants it
on the second.)

| | guile | wilds | lore | arcane | divine | primal | influence | craft |
|---|---|---|---|---|---|---|---|---|
| **martial** | **Swashbuckler** · *Feint and Thrust* (guile → martial, Precision) | **Ranger** · *Hunter's Quarry* (wilds → martial, Amplifying) | **Slayer** · *Know the Beast* (lore → martial, Precision) | **Spellblade** · *Spellstrike* (Focus spent on arcane → martial, Amplifying) | **Paladin** ⚖ · *Sworn Strike* (divine → martial, Protective) | **Berserker** · *Red Mist* (bloodied → martial, Amplifying) | **Marshal** · *Lead from the Front* (a martial defeat → influence, Precision) | **Battlesmith** · *Maker's Edge* (craft → martial, Protective) |
| **guile** | | **Stalker** · *Patient Hunter* (wilds → guile, Precision) | **Spy** · *The Dossier* (lore → guile, Precision) | **Shadowmage** · *Smoke and Glamour* (Focus on arcane → guile, Protective) | **Veiled Hand** ⚖ · *Sanctioned Silence* (divine → guile, Precision) | **Changeling** · *Borrowed Face* (Focus on primal → guile, Precision) | **Charlatan** · *The Long Con* (influence → guile, Amplifying) | **Saboteur** · *Rigged* (craft → guile, Amplifying) |
| **wilds** | | | **Naturalist** · *Field Notes* (wilds → lore, Precision) | **none**: formula is learned in a study; hold both callings | **Pilgrim** ⚖ · *Road Blessing* (divine → wilds, Protective) | **Wildwarden** · *The Land Answers* (wilds → primal, Amplifying) | **Caravaneer** · *Trail Law* (wilds → influence, Precision) | **Trapper** · *Field-Made* (wilds → craft, Precision) |
| **lore** | | | | **Magister** · *Theory into Practice* (lore → arcane, Precision) | **Inquisitor** ⚖ · *Cited Scripture* (lore → divine, Precision) | **Cunning-folk** · *Old Knowing* (lore → primal, Precision) | **Counselor** · *Precedent* (lore → influence, Amplifying) | **Inventor** · *Worked Out on Paper* (lore → craft, Protective) |
| **arcane** | | | | | **Theurge** ⚖ · *Twin Invocation* (Focus on arcane → divine, Precision) | **none**: formula commands, the living force is asked | **Spellsinger** · *Voice and Weave* (influence → arcane, Amplifying) | **Artificer** · *Bound in the Making* (craft → arcane, Amplifying) |
| **divine** | | | | | | **none**: a named power and the nameless world share no servant (a pre-made setting may author one; the world seed never does, 12.16.5) | **Preacher** ⚖ · *Word and Witness* (influence → divine, Amplifying) | **Reliquarist** ⚖ · *Hallowed Work* (craft → divine, Precision) |
| **primal** | | | | | | | **none**: spirits are bargained with, not persuaded; the Spirit-talker covers it | **Hedgewitch** · *Cauldron and Charm* (craft → primal, Amplifying) |
| **influence** | | | | | | | | **Magnate** · *Name on the Work* (craft → influence, Amplifying) |

⚖ = oath-bearing (V4 is its first vehicle; forbidden acts on the entry). 32 named, 4 none.

**T-04-5 The vehicles.** `[D]` (`data/vehicles.yaml`. Optional fields added by this chapter: `when`,
`requires`, `families`, `specificity`, `price_kinds`, `decline_cost`, `represent_when`, `expires`,
`may_not_say`, `seeds`; top-level `selection`, `prices`, `readings`, `markers`.)

| Vehicle | Voices | When | Needs (engine-checked) | Price | Witness |
|---|---|---|---|---|---|
| V1 The Witnessed Epithet | grant | reflection, arrival | ≥ 2 public events on the key in a scope the PC is in, one noteworthy | shadow | required |
| V2 The Mentor's Acknowledgement | offer | reflection, arrival, request | an NPC of depth recurring or principal, matching role, standing ≥ +1, within a watch | bond | no |
| V3 The Order Seeks You Out | offer | reflection, arrival | `institutions_matching` returns a faction at status ≥ 0 that has heard of the deeds | obligation | required |
| V4 The Oath Spoken | offer | crisis, reflection, arrival | the calling has an oath block | oath | no |
| V5 The Awakening in Crisis | offer | crisis | a crisis event on the key this beat; none yet this scene | shadow | no |
| V6 The Seer's Reading | abstain | request, reflection | a reader asked, or a band changed | — | no |
| V7 The Reflection at Rest | grant, offer | reflection, request | nothing | shadow | no |
| V8 The Rival Names You | grant, shadow | reflection, arrival | ≥ 2 public events in a hostile scope, or a surviving adversary carrier | shadow | required |
| V9 The Rite or Trial | offer | reflection, arrival | membership in, or a V3 offer from, an institution with ranks | obligation | required |
| V10 The Body Remembers | small confirmations | reflection | the change is a confirmation, a rank, a grade | — | no |
| V11 The Place Answers | offer, small grant | arrival, reflection | the place carries a matching `resonance` | shadow (oath if the calling has one) | no |
| V12 The Master of the Fusion | offer (hybrid) | reflection, arrival | a figure embodying both branches (placed by ch.12's lead engine) | bond | no |
| V13 The Interested Power | offer (dark, pact, Devourer, turn) | crisis, reflection, arrival | the candidate is of those kinds | bane (oath for a pact) | no |
| V14 The Fraying | revocation | scene start, reflection | a Fraying stage was entered | — | no |

**T-04-8 Simulation results.** `[D]` Scratchpad `recog04.py` (rules as written; 03's evidence model and its
play assumptions: 5 scenes per session, opposition from the PC's band to band + 2), `feat04.py`, `wren04.py`;
copied with full output to `rules/_process/simulation/`. 200 seeds unless noted; p10 / median / p90.

| Id | Question | Result |
|---|---|---|
| R1 | Sessions to each tier, four play styles | the table in 04.3.5 |
| R2 | A level-3 key (Lockbreaker) | tiers at 3/4/6 · 8/10/12 · 18/22/37 · 34/38/46 · 58/—/— |
| R3 | Who is offered the branch calling Warrior at tier 1, within 30 sessions | mixed-weapons fighter 200 of 200 (session 3/3/4) · bow-focused archer 34 of 200 · single-track swordsman 1 of 200. Largest child's share of `martial` at session 10: 0.41–0.55 mixed, 0.71–0.85 archer, 0.81–0.91 swordsman |
| R4 | Hybrid offered within 20 sessions, by mix of two branches | 100/0: 0 · 95/5: 0 · 90/10: 9 · 80/20: 173 · 70/30: 200 · 60/40: 200 · 50/50: 200 (of 200). Second-pillar archer (stealth in 25% of scenes): 65 of 200. Deliberate hybrid's tiers: 2/3/4 · 5/6/8 · 11/13/14 · 21/23/25 · 36/39/42 |
| R5 | The rat grinder, 20 sessions | recognized in 0 of 200 (weighted 340, counted 100, quality events 0) |
| R6 | A whole character accepting everything (100 seeds) | archer: first recognition at session 3/4/5 (Archer in 91 of 100); callings held at sessions 5 / 10 / 20 / 40: 1 / 3 / 3 / 3; highest tier at 10 / 20 / 40 / 60: 2 / 3 / 4 / 5. Three-branch generalist: first recognition at 3/5/7; highest tier 1 / 2 / 3 / 4 |
| R7 | Calibration of confidence (1,723 level-2 candidates, nothing accepted) | would be confirmed, by score 0–5: 37, 59, 64, 73, 91, 97 in 100. By policy: grant 91, offer 74, abstain 38 in 100. A designed pillar of the play style: grant 98, offer 74, abstain 22 in 100 |
| R8 | A tier-2 grant, then a turn to fire sorcery | tier 2 lapsed in 181 of 199 runs when the archer stopped at once; 65 of 199 after one more session of archery; 9 of 199 after two; 0 of 199 when she never stopped. The new calling was first recognized 2 / 3 / 5 sessions after the turn |
| R9 | Counted against weighted at a focus node, session 10 | archery 50 vs 237 (0.21) · thievery 42 vs 220 (0.19) · persuasion 27 vs 176 (0.15) |
| R11 | Non-combat parity (`04-recog-parity.py`, revision I-003) | medians to tier 3 / 5: archer 19 / 51; envoy 18 / 46; smith 18 / 45; scholar 17 / 46 (earlier rules: smith never past tier 2) |
| R12 | Counted share measured (`03-counted-yield.py` on 06's engine; parity R9; revision I-004) | fighter bands 1–5: 0.11 / 0.15 / 0.22 / 0.23 / 0.33 without Focus, 0.26–0.44 pushing; contests: social 0.31, craft 0.76, lore 0.31 (medians) |
| R10 | Sessions for one conduct axis to reach 16 / 40 / 80 / 140 / 220 positive points | costly choice taken in 60% of fights: 5 / 12 / 24 / 42 / 65 (medians) · in 30%: 10 / 24 / 47 / 83 / — · in 15%: 18 / 48 / — / — / — |
| Wren | One continuous character, seed 7 | the long example WE-04-1 |

**T-04-9 `gen_absorb.yaml`.** `[D]` Optional keys added to the gen_* schema: `requires`, `trigger`,
`taking_check`, `caps`, `costs`, `failure`, `banes`, `no_pool`, `evidence`; per pool entry `name`,
`activation`, `cost`, `limits`, `bias`, `opposed_harm_tag`, `text`. Pool by creature branch: beast 7
(Predator's Nose, Thick Hide, Pounce, Venom Gland, Night Eyes, Wall-Crawl, Gills) · undead 4 (Grave Chill,
Deathless Calm, Life-Drink, Ghost-Step) · spirit 2 (Glamour-Skin, Spirit-Sight) · fiend 2 (Hellfire Blood,
Dread Gaze) · construct 2 (Stone-Flesh, Tireless) · elemental 4 (Ember Heart, Rime Breath, Stone Grip,
Storm-Step) · dragon 2 (Dragon's Breath, Scale-Ward) · horror 4 (Acid Touch, Spore Cloud, Rooted, Alien
Mind) · folk 0.

**T-04-10 Vows and dark callings.** `[D]` (`callings.yaml`; boons by rank on the entries)

| Axis | Vow (forbidden act, in short) | Boon at tier 1 | Dark calling | Boon at tier 1 |
|---|---|---|---|---|
| mercy | **Hospitaller** (slay the yielded or helpless) | a Precision lever on Talk to make a beaten foe yield | **Pitiless** | +1 harm against a bloodied target |
| honesty | **Truthsworn** (deceive one who relies on your word) | a Precision lever on Talk when a cited fact supports what you say | **Deceiver** | +1 edge on deception against one who thinks well of you |
| courage | **Dauntless** (abandon a charge out of fear) | +1 against being frightened | none | — |
| loyalty | **Liegesworn** (betray the one or the cause you named) | +1 edge on Help and service to the sworn | **Betrayer** | an Amplifying lever on an ambush against one who trusts you |
| generosity | **Almsgiver** (take from those in need) | an Amplifying lever on Talk with one you have given to | **Grasping** | +1 edge on trade and theft |
| justice | **Justiciar** (punish the innocent; free the guilty for gain) | a Precision lever to expose a wrong, citing evidence | **Tyrant** | a Precision lever on intimidation and command over those beneath you |
| humility | **Penitent** (demand deference; take another's credit) | regain 1 Focus when an attempt you Helped succeeds | **Vainglorious** | +1 Resolve defense against being talked round |
| restraint | **Ascetic** (give way to rage or appetite to another's harm) | +1 Resolve defense against effects on the mind | **Wrathful** | +1 harm while bloodied |
| piety | **Devout** (desecrate what you honor) | a Protective lever on rites and on consecrated ground | **Defiler** | halve holy harm taken |
| protection | **Shieldsworn** (abandon the helpless you could have shielded) | once per scene, take a hit meant for an ally | **Coldheart** | +1 Resolve defense against appeals to pity or duty |

**T-04-11 Default shadows by family.** `[D]` martial *The Butcher* (mercy, restraint → Wrathful) · guile *The
Faithless* (honesty, loyalty → Betrayer) · wilds *The Feral* (protection, generosity → Coldheart) · lore *The
Hoarder of Secrets* (generosity, humility → Vainglorious) · arcane *The Overreacher* (humility, restraint →
Vainglorious) · divine *The Zealot* (mercy, humility → Defiler) · primal *The Wild-Lost* (restraint,
protection → Wrathful) · influence *The Manipulator* (honesty, justice → Tyrant) · craft *The Covetous*
(generosity, honesty → Grasping). Eleven level-2 keys override (for example Necromancer: *The Grave-Robber
of Souls*; Ambusher: *The Murderer*; Merchant: *The Profiteer*).

**T-04-12 Numbers other chapters consume.** `[D]`

| Number | Value | Consumer |
|---|---|---|
| Maximum tier | 5 | all |
| Competence by tier | fine, narrow 3/4/5/5/6 · broad, hybrid roads 2/3/4/4/5 · vow, dark none | 01 (modifiers), 02 (origins stay at +2), 09 |
| `power_band` by tier | fine, narrow 1–5 · broad, hybrid 1/2/3/4/4 · vow, dark 1/1/1/2/2 | 09, 07, 03 (`peak`) |
| Seats | 3 deed + 1 oath | 05, 12 (rotation facets), 14 |
| Picks, cumulative | 2/3/4/5/6 (deed) · 1/1/2/2/3 (oath); partition assumed 12 | 05 |
| Ability rank | 1 + floor((tier − min_tier) ÷ 2) | 05 |
| Pick candidates | 3 shown; own pool before kin; then by the character's weighted tally at the ability's first tag | 05 |
| Training grades | trained, expert, master by tier and breadth | 05 |
| Attribute increase | +1 once, at a confirmed tier 4, cap +4 | 02, 00.4.3 |
| Focus trigger | 1 Focus, once per scene (twice from tier 4) | 05 |
| Provisional test | confirm from 12 evidence-bearing scenes after the grant at since-grant weighted ≥ 18 / 24 / 36; lapse at 24 | 11 (season turn), 14 |
| Decline cooldown | 24 evidence-bearing scenes and + W1/2 | 12 |
| Fraying stages | strain 4 / 8 / 12, or a forbidden act | 03, 11 |
| Atonement clock | 4 or 6 segments | 11 (threads), 15 (penance week) |
| Library cap | 4/6/8/10/12; Taking: 2 Focus, 1 per long rest | 05, 09 |
| Offers per reflection / per scene | 3 / 1 | 12 |

---

## Worked examples

**Wren** is 00's continuous character: Agility +3, Might +1, Wits +2; competence `deed` +1 (floor),
`deed.martial.archery` +2 and `deed.wilds.tracking` +2 from a forester's origin; unrecognized, so
`power_band` 1. WE-04-1 follows her through one simulated campaign (`wren04.py`, seed 7: an archer who
tracks and scouts). **Every tally below is that run's value, read through 03.9's functions**; the fiction
around the numbers, and every ability, NPC and faction named, is illustrative *(ch.05, 11, 12, 13 own them)*.
The player never sees a number in this example except in the `[CHOICE]` and `[RESULT]` blocks, which show
only shown state.

### WE-04-1 One character from the first name to a consolidation and beyond

**Session 4, a long rest at the Ashwood waystation (reflection). The first recognition: a grant.**
03's digest marks `deed.martial.archery` dirty. PR-04-1 step 4 evaluates `call.archer` (`req.narrow.1`):

| Requirement | Needs | Wren | |
|---|---|---|---|
| weighted | ≥ 80 | 85 | ✓ |
| counted | ≥ 8 | 18 (`cnt.defeat` and `cnt.focus`) | ✓ |
| quality events | ≥ 6 | 15 (3 challenging, 12 difficult; 3 routine do not count) | ✓ |
| distinct scenes | ≥ 5 | 9 | ✓ |

Eligible. Confidence (her `recent` at the key is 64; `weighted(deed)` is 177):
K1 Current `2·64 = 128 ≥ 80` ✓ · K2 Rising `128 ≥ 85` ✓ · K3 Central `5·85 = 425 ≥ 177` ✓ · K4 Leading
(archery is her largest level-2 node) ✓ · K5 Margin `4·85 = 340 ≥ 400` ✗. **Confidence 4.** Currency floor
`4·64 ≥ 80` ✓. Policy (04.4.3): tier 1, narrow, no oath, a free seat, no lineage held, never declined, and the
field is clear (no other `martial` candidate is eligible; the martial × wilds hybrid is far from it) →
**grant**.

Vehicle (PR-04-3): the family's grant list is V8, V1, V7. Two of her shots at the ford were seen by caravan
guards who lived (`public(wren, deed.martial.archery, fac.caravaners_compact).events = 3`, one noteworthy):
V1's `requires` hold; V8's do not (no hostile scope has two events). The engine returns [V1, V7]; the DM
picks V1.

> The waystation's cook, who was not at the ford, sets down a bowl and looks at the bow propped by the door.
> "So you're the one. Two wagons through and a wyvern in the river, they're saying. *Ford-arrow*, the guards
> call you." She seems to think you knew.
>
> `[RESULT] Changed: calling — Archer, tier 1 (Called), provisional · competence: archery +3 · training
> under archery: trained · capability: The Mark of the Calling · 2 picks · you may set it aside at any rest
> (say "renounce Archer")`
> `[CHOICE] A pick for Archer — (a) Pinning Shot: <literal text> · (b) Steady Draw: <literal text> ·
> (c) Quarry's Mark: <literal text> · (d) keep the pick for later`

State: `callings: [{call.archer, tier 1, provisional, crystallized_by: ev.000188 (the wyvern shot), vehicle:
veh.V1}]`; competence `deed.martial.archery` +3 (her origin's +2 is now the lower entry); `lic.call.mark`;
`recognition_event {kind: first, policy: grant, vehicle: veh.V1, witnesses: [the cook], scope:
[fac.caravaners_compact, loc.ashwood_waystation], epithet_seed: "Shot a wyvern through the eye at the ford
while the wagons crossed"}`. Ch.11 owns what becomes of "Ford-arrow". The three pick candidates are the
eligible abilities whose first tags she has the most evidence on (04.8.4); she takes two over two prompts.

**Session 7, a camp in the deepwood. A broad offer, deferred; then a narrow one beside it.** At a
reflection after scene 32, `call.wayfarer` (key `deed.wilds`, broad) becomes eligible: weighted 123 ≥ 120,
counted 19 ≥ 12, quality events 16, scenes 15, three level-2 children at 30 or more, the largest (tracking)
under two-thirds of the branch. Confidence 4. A branch calling is never granted (04.4.3) → **offer**. No one
is within a watch of her camp, so V2 and V3 fail their requirements and the engine returns [V7].

> You wake before the fire has died, knowing which way the wind will turn by noon. You did not always know
> such things.
>
> `[CHOICE] Recognition — The Reflection at Rest: Wayfarer, tier 1 (Called)`
> `  (a) Accept — you gain: competence across the wilds +2 · training in every craft of the wilds: trained ·
>      The Mark of the Calling · 2 picks · price: a seat (2 of 3 deed seats used) and the calling's shadow ·
>      provisional until a season's turn or 24 scenes of deeds`
> `  (b) Decline — nothing changes; not raised again until you have lived more of it (you may ask at any rest)`
> `  (c) Defer — the offer stands; it returns at each rest`
> `  If you move on without choosing: (c) defer`

The player says "not yet". The offer becomes a standing offer. Three scenes later, at the session's last
rest, `call.tracker` (key `deed.wilds.tracking`) is eligible: weighted 80, counted 14, quality events 6
(exactly the floor), scenes 9; confidence 4 (K5 fails: `4·80 = 320 < 400`). It would be a grant, except the
field is **not clear**: another candidate keyed in `deed.wilds` is open. So it is an **offer**, and because
Wayfarer and Tracker share a lineage (04.8.3) they are put in one block (04.7.6). She is back at the
waystation, where the old trapper Odo Kettle (`npc.odo_kettle`, depth recurring, role
`deed.wilds.tracking.trailing`, standing +1) has watched her read sign for a week: V2's requirements hold.

> Odo turns the snare over in his hands. "You found the doe's bed from one bent stem. I've men who've trapped
> twenty winters who'd have walked past it. I could show you the rest. It'd cost you a winter pelt, and your
> patience."
>
> `[CHOICE] Recognition — more than one road is open in the wilds (they share a seat: choose one, or neither)`
> `  (1) The Mentor's Acknowledgement: Tracker, tier 1 — tracking +3 · training in tracking: trained ·
>      2 picks · price: a bond to Odo Kettle (one winter pelt by the season's end)`
> `  (2) The Reflection at Rest: Wayfarer, tier 1 — the wilds +2 (all of it) · 2 picks · price: none beyond the seat`
> `  Accept by number · decline by number · anything unanswered is deferred`

She accepts (1). Tracker, tier 1, provisional; a commitment of kind bond is written. The Wayfarer offer is
**withdrawn** (one seat per lineage); it can return later only as a *broaden* fork. Seats: 2 of 3.

**Session 9. Tier 2 of Archer, voiced by an order's letter.** At a reflection after scene 42 the Archer's
next tier is ready (`req.narrow.2`): weighted 212 ≥ 200; counted 49 ≥ 20; **since** tier 1: quality events
25 ≥ 10, scenes 12 ≥ 8, great deeds at band 2 or higher 25 ≥ 5 (15 of them successes). No crisis completed
it, so 04.5.8 (c) applies: the next reflection. `institutions_matching(deed.martial, region.ashwood)` returns
the Caravaners' Compact at status +1, which has heard of her (public events 5): V3's requirements hold.

> A letter has been waiting at the waystation three days, sealed with a wheel in blue wax. The Compact
> wants an outrider for the Salt Road before the autumn caravans; it names a wage, and it names you.
>
> `[CHOICE] Recognition — The Order Seeks You Out: Archer, tier 2 (Proven)`
> `  (a) Accept — you gain: archery +4 · Proven (you may teach archery) · 1 pick · when your bow fells a foe
>      at or above your measure, regain 1 Focus (once per scene) · price: service to the Caravaners' Compact
>      as outrider (its duties are shown under Factions) · provisional`
> `  (b) Decline — nothing changes. Refusing the Compact's rider to his face costs one step of its regard;
>      leaving the letter unanswered costs nothing.`
> `  (c) Defer — the letter can be presented at any Compact house until the season after next`

She accepts. The **rank** of outrider and its obligations are ch.11's (`recognition_event.institution`); had
she declined the post, the tier would still be hers at the next rest by V7, at no price beyond the seat
(04.11.1). `power_band` is now 2. Twelve evidence-bearing scenes after each grant, a reflection confirms it: her archery
since tier 1 passed 24 within a session, and her tracking since its grant by session 10.

**Session 15, the ford again: a tier seized in a crisis.** In scene 74 she looses at a drake under a lethal
frame while Staggered. The shot's evidence event is flagged `crisis`. `h.04.crisis_check` runs at
`beat_end`: the Archer's tier 3 was `on_the_threshold` at the last reflection; with pending evidence
included, weighted is 450 ≥ 440, counted 101 ≥ 44, and since tier 2: quality events 52, scenes 21, great
deeds at band 3 or higher 41 (23 successes), crises 13 ≥ 2. Eligible → `trg.04.crisis_offer` → V5.

> The string is against your cheek and the world has gone very quiet. Your hands are steady. They have
> never been this steady.
>
> `[RECOGNITION] An offer is open (see below). Nothing is lost by waiting; play continues when you answer or move on.`
> `[CHOICE] Recognition — The Awakening in Crisis: Archer, tier 3 (Tempered)`
> `  (a) Seize it — archery +5 · training: expert · Sure Hand (a Precision lever whenever you stretch or
>      emulate with the bow) · 1 pick, now, from what this shot was · price: none beyond what you already carry`
> `  (b) Refuse it · (c) Let it pass — it returns at your next rest or your next such moment`

She seizes it. The pick's candidates rank first the abilities whose first tag matches the crisis deed
(`deed.martial.archery.bow`). `power_band` 3; picks held: Archer 4, Tracker 2.

**Session 17. The hybrid surfaces as a consolidation, and she waits.** After scene 85,
`cooccurrence(wren, deed.martial, deed.wilds)` gives weighted 591 and 240, `min` 240 ≥ 60, `balance`
240/591 (`5·240 = 1,200 ≥ 2·591 = 1,182` ✓, by eighteen points), `joint_scenes` 5 ≥ 5, `recent_min` 53 ≥ 15,
counted 120 and 37. `call.ranger` is eligible, and she holds a calling under each of its branches: a
**consolidation** offer (04.8.5). The tier would be the highest not above 3 that `min` supports: 240 meets
tier 2's 150 and not tier 3's 330 → **Ranger, tier 2**. Ch.12's lead engine places a principal who embodies
both roads; V12.

> The warden who has shadowed the caravan since the hills steps out where you can see her, an unstrung
> longbow across her shoulders and a brace of hares at her belt. "You shoot like the Compact's best and you
> read ground like Odo's. You keep them in two hands. I keep them in one."
>
> `[CHOICE] Recognition — The Master of the Fusion: Ranger, tier 2 (consolidating Archer 3 + Tracker 1)`
> `  (a) Accept — one calling in place of two (1 of 3 seats used). You keep: archery +5 and tracking +3 as
>      specialties, every pick you hold (6), Sure Hand, your training. You gain: Hunter's Quarry (when a deed
>      of the wilds succeeds, an Amplifying lever on one later martial beat that scene). You give up: the
>      Archer's Focus trigger, and separate growth: your next 3 Ranger picks are already counted.
>      price: a bond to Sefa (a season's patrols when she calls) · provisional`
> `  (b) Decline · (c) Defer — she walks these woods until the season turns; after that it returns at your rests`

The player reads that the label would be tier 2 and defers: the wilds half is thin. Nothing is lost.
*This is the engine declining to compute a winner for a mixed history* [C:P5]: Archer and Tracker stand, the
named hybrid stands beside them, and the player chooses when.

**Session 20. Abstain, then an offer one scene later, and a decline.** Wren scouts by stealth in about a
quarter of her scenes. After scene 97, `call.shadow` (key `deed.guile.stealth`) is eligible: weighted 99,
counted 9, quality events 14, scenes 14. Its confidence is **0**: recent 28 (`2·28 = 56 < 80`; `56 < 99`),
`5·99 = 495 < 966`, not among her three strongest level-2 nodes, `4·99 = 396 < 400`. The currency floor holds
(`4·28 = 112 ≥ 80`), so it is not stale, only thin → **abstain** (04.4.3 row 2). Nothing is voiced; her
Leanings view shows "stealth: on the threshold". Two scenes later weighted is 103: K5 holds (`412 ≥ 400`),
confidence 1 → **offer**, by V7.

> `[CHOICE] Recognition — The Reflection at Rest: Shadow, tier 1 (Called) … (b) Decline …`

"I hide when I must. It is not what I am." **Decline**: recorded with `weighted_at_decline: 103`. The engine
will not raise it again until 24 more evidence-bearing scenes have passed **and** weighted reaches 143; she
may ask for it at any rest. No cost, and her stealth competence is unaffected (it has none beyond the floor).

**Session 25.** Tracker's tier 2 is ready (weighted 201; counted 22; since tier 1: quality events 24, scenes
18, great deeds at band 2 or higher 24 with 5 successes) and Odo voices it (V2, `return_to_person`). Accepted.

**The season turns after session 26 (`h.04.season_consolidation`).** PR-04-8: (1) the Tracker's tier 2 has
only 5 evidence-bearing scenes behind it, so it is not yet tested. (3) The standing Ranger offer is
re-presented; now `martial` 770, `wilds` 403, `min` 403 ≥ 330 → **Ranger, tier 3**. She accepts.

| | Before | After |
|---|---|---|
| Callings (seats) | Archer 3, Tracker 2 (2 seats) | **Ranger 3** (1 seat); Archer and Tracker `retired, superseded_by: call.ranger` |
| Competence | archery +5, tracking +4 | roads archery +4, tracking +4; **specialties** archery +5 (expert), tracking +4 (trained): highest-only, so every roll is as before |
| Picks | 4 + 3 = 7 held | 7 held; `picks_total[3]` = 4, so `legacy_picks` = 3 |
| Capabilities | Mark, Proven, Sure Hand | the same (held once; the specialties keep their scope) |
| Family mechanic | martial Focus trigger, rank 1 | **Hunter's Quarry**, rank 2: a success on either road gives an Amplifying lever on the other, twice per scene; fused deeds +1 edge |
| `power_band` | 3 | 3 (`inherited_band` 3; a hybrid's tier 3 is also 3) |

`recognition_event {kind: consolidation, calling: call.ranger, tier: 3, vehicle: veh.V12, …}`. Two labels,
two ladders and a Focus trigger are retired; nothing she could do yesterday is gone today; her next three
Ranger picks are pre-paid; and two seats are free for whatever she becomes next (VI: structural retirement,
written as a transformation).

**Session 37. Tier 4, and the one attribute increase.** After scene 182: `min` = 605 ≥ 600 (martial 998,
wilds 605); counted 194 and 74 ≥ 60 each; since the consolidation: quality events 57 + 49, scenes 21 and 30,
great deeds at band 4 or higher 47 + 38 (18 successes), crises 14 + 2 ≥ 3, contexts 10 + 7 ≥ 5. Offered at a
rest by V11 (the old wardens' cairn, a place with `resonance: [deed.wilds, deed.martial.archery]`) and
accepted: Master's Eye; training on her roads at expert; the tier's pick cancels one legacy pick (2 remain).
The attribute increase waits for confirmation (04.8.2); twelve evidence-bearing scenes later the tier is
confirmed and she raises **Agility +3 → +4**, the one increase of her life. `power_band` 4: ch.09's advisory
now rates a T4 champion as a fair fight.

**Sessions 38–60.** Tier 5 needs `min` 975; her wilds reach 907 by session 60. She does not become a Paragon
in this campaign. Most characters do not (in the simulation, 165 of 200 focused archers reached tier 5 of a
single narrow calling by session 60; a hybrid's median is session 39 only for evenly split play). The ladder
has a top, and it is far away on purpose.

### WE-04-2 Abstain, three ways

| Case | Tallies | Why abstain | What the player can learn |
|---|---|---|---|
| **Not eligible: the grinder.** Brann shoots cellar rats in every scene for 20 sessions. | archery weighted 340, counted 100, quality events **0** (all routine), scenes 60 | the quality floor (6) is unmet | Leanings: "the bow: on the threshold". A reader: "You have done it often, and seldom when it was hard." |
| **Stale: the old soldier.** Hesk fought with the sword for years and has kept an inn for the last forty scenes of play. | `martial.blade` weighted 300, recent 12 | eligible, but `4·12 = 48 < 80`: stale | A reader: "That was who you were. I am asked who you are." If he takes up the sword again, recent passes 20 within a session and the offer comes. |
| **Thin: Wren's stealth at scene 97.** | weighted 99, recent 28, confidence 0 | eligible and current, with nothing confirming it | silence; two scenes later the margin holds and it is offered |

*Other side of each boundary:* give Brann one real fight a session and his quality events pass 6 by about
session 4; give Hesk recent 20; give Wren four more points. *Tempting non-example:* the DM feels Brann has
"earned it by persistence". There is no such input: the packet for Brann is empty, and the narrator has no
tally to be moved by.

### WE-04-3 Grant against offer: the same tallies, two fields

Two archers reach scene 17 with Wren's exact numbers (weighted 85, confidence 4). **A** has done little else:
no other candidate is eligible → clear field → **grant**. **B** has also fought with the spear enough that
`call.spearhand` is eligible in the same pass (weighted 82) → the field is not clear → **offer**, with both
named in one block, and the branch calling Warrior beside them if its breadth requirement holds. The engine
does not rank B's identities; the player does. *Non-example:* B's player says "obviously I'm an archer first".
That is an answer to the block, and the right place for it.

### WE-04-4 Defer, a standing offer, and an expiry that takes nothing

Wren had answered the Compact's letter (WE-04-1, session 9) with (c). The offer stands:
`{status: deferred, vehicle: veh.V3, represent_when: [arrival_at_institution, reflection_in_its_region],
expires: season boundary after next}`. It appears under "Open offers" at each session start. Two seasons
pass. At that boundary `h.04.standing_offers` expires the **staging**: the outrider's post is gone (ch.11
gives it to someone else). The tier's eligibility is untouched, so at the same reflection the engine offers
Archer tier 2 again by V7, with no obligation attached. *Boundary:* had the Compact's status toward her
fallen below 0 in the meantime, the letter would have expired then, in the same way. *Non-example:* "You
ignored the letter, so the skill fades." Nothing fades: capability never depends on an institution (04.11.1).

### WE-04-5 A pick, with the numbers the player never sees

Archer tier 1, first pick. Eligible by the pool gate (04.8.4) *(abilities illustrative; ch.05 owns)*:

| Ability | First tag | `min_tier` | Pool | Wren's weighted at the tag | Rank |
|---|---|---|---|---|---|
| Pinning Shot | `deed.martial.archery.bow` | 1 | own | 85 | 1st |
| Steady Draw | `deed.martial.archery` | 1 | own | 85 (tie; engine draw) | 2nd |
| Volley | `deed.martial.archery.bow` | 2 | own | — | not eligible: `min_tier 2 > 1` |
| Tumbling Escape | `deed.martial.athletics.acrobatics` | 1 | kin | 21 | 3rd (kin ranks after own) |
| Read the Field | `deed.martial.tactics.reading` | 1 | kin | 12 | 4th: not shown |

The block shows Pinning Shot, Steady Draw and Tumbling Escape, each with its literal rank-1 text. Her second
pick shows the remaining two and Read the Field. At tier 2 Volley joins the eligible set; at tier 3 a picked
`min_tier 1` ability is restated at rank 2 (`1 + floor((3 − 1) ÷ 2)`). *Boundary:* an archer who had spent
her fights reading ground (tactics weighted 90) would see Read the Field ahead of Tumbling Escape. The table
she is offered is her own history.
*Non-example:* "Can I just take Fireball?" Its first tag is `deed.arcane.fire.blast`: not under any gate of
this calling. The redirect names the paths: an arcane calling's pick, or learning it by ch.05's own paths.

### WE-04-6 The Fraying: a warning that clears, and a forbidden act

**Corin** is a Paladin, tier 2 (roads `martial.blade` and `divine.smiting` at +3; oath axes protection and
mercy; keeper: the Shrine of the Ford; forbidden acts: "Slay a being that has yielded to you." and "Abandon
to harm one under your sworn protection."). Mercy: `pos` 14, `neg` 0, `strain` 0.

*A single contrary act warns.* In a rage he beats a bound cultist for answers (mercy −4: harm to a helpless
victim, 03.3.3). At settlement `neg` 4, `strain` 4. At the next `scene_start`, PR-04-7: stage **1, Dimmed**.

> The morning prayer comes out as only words. The warmth that has sat behind your breastbone since the ford
> is still there, but it has drawn back, as a friend does who has seen something and not yet decided what
> to say.
>
> `[RESULT] Changed: Paladin — Dimmed (stage 1 of 3). Now inactive: Sworn Strike; abilities that need your
> oath of mercy. No new tier while dimmed. Clears by: deeds of mercy, or atonement (ask at any rest).
> Next stage if: more cruelty to the helpless.`

Next session he spares two beaten foes at real cost (+2, +2, in different scenes): strain 4 − 1 − 1 = **2** →
stage 0. Sworn Strike returns; one V10 line; a RESULT line.

*A forbidden act goes to the Choice at once.* Instead, suppose the cult's captain throws down his blade and
Corin kills him. The DM cites `forb.paladin.slay_yielded` (03.3.3: the act matches the sentence word for
word). `forbidden` = 1 → stage **3** whatever the strain. The calling is suspended: roads fall to the floor,
no composite, no oath abilities, and `power_band` falls from 2 to 1.

> `[CHOICE] Paladin — The Choice (stage 3). The calling is suspended until you answer.`
> `  (a) Atone — carry the captain's body to his kin at Harl's Crossing and stand their judgment (a thread)
>      · keep a week's vigil at the Shrine and give up your sword to it (S3) · or deeds of mercy at real
>      cost (a 6-segment clock; the calling returns one tier down while it runs)`
> `  (b) Turn — become the Defiler in its place, tier 1 · price: the first time each scene that you do a
>      reverent deed, lose 1 Focus`
> `  (c) Release — let the calling go; its 3 picks return to the pool; your training stays`
> `  (d) Defer — it stays suspended; it lapses at Midwinter (the second season's turn) if nothing is done`

He chooses service. `clk.atonement.paladin` (6, public) opens; the calling is read at stage 2 (tier 1's
values). Over three sessions: a +4 mercy entry (2 ticks), a +2 (1), a +4 (2), a +2 (1) → 6 of 6.
`record_evidence(op: atonement, axis: conduct.mercy, supersedes: [the killing])`: `neg` 0, `atoned` 4,
`strain` 0, the citation cleared → stage 0, tier 2 restored in full. The ledger still shows the killing,
marked superseded; the cult still calls him a murderer (ch.11).

*Tempting non-example:* Corin kills the captain **mid-fight**, before any yield. No alternative was plainly
open (03.3.3): no conduct entry, no citation, no stage. The oath forbids slaying the yielded, not winning.

### WE-04-7 The Taking: a success, a failure, and what narration may not add

**Tamsin** is a Devourer, tier 1 (Resolve +1; competence `deed.lore.bestiary` +3; library 0 of 4; Focus 4).
She has just killed a cinder hound (T2; `creature.beast.predator`, `creature.elemental.fire`) with her own
spear, never below 4 Vitality, and it breathed fire at her this scene. PR-04-9:
1. Gate: license held; every trigger condition holds.
2. Circumstance: her own resolved success; never Staggered → **decisive**.
3. Frame: Endure, Resolve +1, competence +3 → +4 against the effect DC of a T2 creature, Moderate 15: needs
   11, **50%**. Stakes Risky (band 2 ≤ her band 1 + 1). The OFFER shows: "Success: its signature power at
   tier 2. Bane while slotted: double cold harm. Failure: the fire answers (harm S2)." She commits; Focus 4 → 2.
4. d20 = 14 → 18: **success**. `generate(gen.absorb, adv.cinder_hound_07, decisive, success)`: pool gate →
   Ember Heart (the archetype's signature *(ch.09)*), Predator's Nose, Thick Hide, Night Eyes, Pounce;
   fill `signature` → **Ember Heart**; tier `min(tier_cap 2, calling tier + 1 = 2)` = 2: "halve fire harm you
   take, rounded down". Library 1 of 4. At her next long rest she slots it; the elemental bane applies:
   double `harm.frost` taken.

*The other side.* d20 = 5 → 9, margin −6: **failure**. Nothing is taken; `apply_costs(cost.harm, S2)`: 3
Vitality of `harm.fire`. No second attempt on this hound; the next hound she defeats may be tried.
*Boundary (narrow survival).* Had the hound Staggered her first, the fill is `biased`: among the non-signature
entries Thick Hide (bias `ward`, weight 2 × 3 = 6) against Predator's Nose 3, Night Eyes 2, Pounce 2.
*Non-example.* "The flames part around you as you walk through the burning barn." Ember Heart halves fire
harm taken; it parts nothing (INV-8). The claim check cuts the sentence.

### WE-04-8 A provisional grant that lapses, with its warning

A second archer (the simulation's seed 10) is offered tier 2 at the last rest of session 11 and accepts. From
session 12 she apprentices to a fire-sorcerer and puts the bow away (03's scenario D). The grant is
provisional; `lived` is her archery evidence since that rest.
- Session 13, a reflection: 9 evidence-bearing scenes since the grant; `lived` 0, under half of 24 →
  `trg.04.lapse_warning`:
  `[RESULT] Notice: Archer tier 2 is provisional and is not being lived; it will lapse after about fifteen
  more scenes of other deeds unless that changes. Nothing else is at risk.` and one line of fiction: the
  bowstring has gone stiff in its case.
- Session 14: 12 or more since the grant; `lived` 0 < 24 → not confirmed; not yet 24 → no lapse.
- Session 16, the first reflection at 24 since the grant: `lived` 0 → **lapse**: archery +4 → +3, the tier's
  pick returns to the pool, the Proven license and the Focus trigger go (unless another calling grants
  them). Tier 1 was confirmed long before and is untouched: she is still an Archer. Meanwhile
  `call.pyromancer` has been offered (in the simulation the new calling came a median of 3 sessions after the turn).
*Other side:* had she fought one more session with the bow before turning, `lived` would have passed 24 and
the tier would have been confirmed at the first reflection twelve scenes after the grant (it confirmed in
134 of 199 such runs). *Non-example:* a season spent healing in a monastery adds no evidence-bearing scenes,
so the count does not advance and nothing lapses (03.6.1).

### WE-04-9 Tempting non-examples, with the refusal each gets

| The player says, or the DM is tempted to | What happens |
|---|---|
| "The duke knights me. So now I'm a Cavalier." | A knighthood is a rank (ch.11). `call.cavalier` comes from deeds of mounted combat. The duke's act creates no packet (04.11.3). |
| "My mentor is a great wizard; she makes me one." | She can teach a first arcane license (ch.05's mentor path) and her teaching counts as `cnt.training`, for at most half a counted requirement. The calling waits on deeds. |
| The DM narrates "you feel yourself growing stronger" after a hard fight | Forbidden: implies a mechanic with no recognition packet behind it (12.14.5). Evidence was recorded; nothing is said. |
| "I renounce my oath so the Fraying can't touch me." | Releasing the calling is always possible (04.9.5 release): the calling, its picks and its boon go with the oath. There is no keeping the power without the keeper. |
| The DM wants to stage V5 because the scene is dramatic | V5 is returned only when the engine flagged a crisis event on a candidate at the threshold. Drama is not a trigger. |
| "I'll consolidate to dodge the Dimmed stage." | A calling at stage 1 or higher cannot be consolidated, forked or folded (04.8.5 step 6). |
| A fourth deed-keyed calling is eligible and the DM quietly drops the least used | The engine never evicts. The block offers consolidate, fork, release, decline or defer (04.8.1). |
| "Show me how close I am to Tracker." | The codex shows Leanings: "tracking: becoming". Numbers are sealed; a reader in the world can say what kind of deed is missing. |

---

## Edge cases & adaptation anchors

**Anchor rules of this chapter** (`Anchor: yes`; each card carries its knobs):

| Rule | Reach for it when the player… | Knobs (00.2.6; two-change limit) |
|---|---|---|
| 04.7.1 Recognition offer | is offered any lasting change by the world: a pact, a post, a transformation, a patron's gift | `duration` (how long it stands), `condition` (the price, from the closed list) |
| 04.7.4 Swearing | wants to bind themselves by words: a vow of vengeance, a promise to the dying, a geas accepted | `condition` (axes and forbidden acts; none for a free promise), `duration` |
| 04.9.4 Atonement | wants to make something right: with a god, an order, a village, one wronged person | `time_cost`, `duration` (clock size), `stakes` (the penance's severity) |
| 04.10.2 The Taking | (holding the license) tries to draw a lasting quality out of something overcome | `dc`, `stakes`, `focus_cost`, `targets` |
| 04.6.4 The Seer's Reading | asks anyone in the world what they are becoming | `targets`, `time_cost` |

**Recognition and eligibility**
- **A deed whose tag stopped shallow.** Evidence classified only to a level-2 tag (03.1.5) feeds the level-2
  and branch callings and no level-3 calling. That is correct: the fine identity needs the fine deed.
- **Evidence voided after a grant** (a dispute upheld, 03 PR-03-4). The next reflection re-evaluates. A
  provisional grant whose requirement set no longer holds lapses at its test, with the usual warning; a
  confirmed tier is **not** unwound (C:VI: no piecemeal rework of a settled identity), and the shortfall
  simply delays the next tier. An open offer whose candidate is no longer eligible is withdrawn (04.7.3).
- **Backstory evidence** (03.2.8) adds weighted points only. It can never meet the quality, scenes, counted
  or currency requirements, so no one is recognized at creation.
- **Two candidates with identical keys** (a base and its variant, both eligible): one block, both named
  (04.7.6). The variant's added requirement is shown as its price line ("requires your restraint to hold").
- **A calling whose tag is retired** by ch.03 (PR-03-6 step 7): the engine carries the evidence to the
  successor tag; the calling entry is retired with `superseded_by` and held instances move to the successor
  at the same tier, as a fork with no choice needed and no loss.
- **Recognition during a time skip.** `advance_time` runs every reflection it crosses (INV-15). Offers raised
  inside the skip are queued and presented when play resumes, at most three; grants are applied and shown in
  one RESULT block. Nothing is decided for the player while they are not there to answer.
- **A companion.** A companion whose template sets `tracks_evidence` (ch.16) is evaluated by the same rules
  with one deed seat, no oath seat and a maximum tier of 3; its offers are put to the player, who answers for
  it [DL-04-24]. Ch.16's protégé (16.10.4) fits this procedure as written: own band = tier + 1, competence
  clamped to `c_b + 1`, and picks into a three-ability partition that replaces beyond three, which is 04.8.4's
  at-the-cap rule with S = 3 [integration: IR ch.16 to 04 (a)].
- **Unlicensed deeds.** A character with no magic license does no deeds of that branch (C:VII), so no magic
  calling can surface. The road in is the license's acquisition paths, never recognition first.

**Offers and vehicles**
- **The recognizer dies mid-offer.** The offer continues by V7 at the next reflection without that
  vehicle's price (04.6.3 rule 3).
- **The player wants the offer staged differently** ("I'd rather swear it at the shrine"). Defer, travel,
  and the arrival trigger returns V11 or V4 there: vehicles are affordances of the world.
- **Two crisis offers in one scene.** The second waits: one per scene (04.7.3). It is presented at the next
  reflection or the next scene's crisis.
- **An offer during a lethal moment.** The pause is safe: at pause point 7 no time passes and no state
  changes (12.2.6). Accepting takes effect before the next beat.
- **The player asks out of fiction, "is anything on offer?"** The codex lists open and standing offers
  (shown). It never lists candidates under abstain.
- **A patron or order offers a calling the tallies do not support.** It cannot (04.11.3). The DM stages the
  patron's interest as what it can truly give: training, a rank, an item, or a reading of what is missing.

**Tiers, picks and seats**
- **Fewer than three eligible abilities.** The block shows what there is; with none, the pick is kept
  (PR-04-5 step 2). The engine never invents an ability and never widens the gate. No calling meets this
  case with the shipped pool: every negative pole now has abilities at `min_tier` 1, 3 and 5, so a dark
  calling's tier-5 pick has its candidate, and `05-ladder-check.py` proves every calling × axis × tier ladder
  complete under this gate (the Monk's restraint gate needed `pole: positive` to admit its oath's abilities)
  [revision: I-007; DL-05-33].
- **An ability picked through one calling when that calling is consolidated or forked.** It stays (04.8.5
  step 4). If its first tag is outside the new calling's pool gate it is kept as **legacy**: usable at the
  rank it had, never ranked up, and the first to be named when a replacement is needed.
- **A lapse or release frees a slot holding an ability another pick could not reach.** The ability returns
  to the pool; nothing else moves.
- **The +1 attribute and a second tier 4.** One per lifetime (04.5.7). The second tier-4 calling still grants
  Master's Eye, the pick and the rank step.
- **Suspension and picks.** A suspended tier's pick is inactive (its slot stays reserved); it is not offered
  to another calling.
- **Power band during suspension or provisional grants.** Provisional tiers count; suspended callings do not
  (04.5.6). Ch.09's advisories therefore follow what the character can actually do today.

**Oaths and the Fraying**
- **Two oath-bearing callings** (a Healer who is also Shieldsworn). Each is staged separately by its own
  axes; one deed can advance both stages. Atonement on an axis clears it for every oath that names it.
- **Conduct under compulsion or false belief.** No conduct evidence is recorded (03.2.6; 03 Edge cases), so
  no strain and no stage.
- **An order strips the character's rank for oath-breaking.** That is ch.11 reacting to
  `recognition_event(kind: fraying_stage)`. The tier is governed only by 04.9.
- **An unatonable act** (`unatonable: true`; only the Pactbound's broken term ships so). Atone is not
  offered; the choices are turn, release or defer, and the lapse date stands.
- **A dark calling's holder does good.** Its reversed oath frays (04.9.2); its price drains 1 Focus the
  first time each scene. Redemption is release, after which the vow of the same axis may be offered.
- **The player wants to play a villain.** Negative conduct is evidence like any other; dark callings are
  real callings with real boons. Nothing in this chapter punishes a pole; it prices bargains.

**The Taking**
- **A creature with two creature tags** (the cinder hound). The pool gate is the union of both tags'
  entries; the bane is that of the branch of the power actually slotted.
- **A power whose source the PC never saw act** fails the trigger (witnessed). The DM says so plainly: "You
  never saw what it could do."
- **Taking from a willing, living being** (a spirit that offers its gift). Circumstance `merciful`; the
  anchor's `dc` knob may move one tier lower.
- **Non-Devourers who want a monster's power.** Loot (ch.08: a trophy with a property), an item-bound
  ability, or ch.05's emulate for learned arts. The capability itself is the Devourer's alone.

**Analogical anchors for growth questions**

| When the question is… | Reach for… |
|---|---|
| "Has the character become X?" | never a ruling: the next reflection's packets, or a reading (04.6.4) |
| "Can the king / the god / my mentor make me X?" | 04.11.3: rank, training, an item or a voice; never the calling |
| "Do I lose it if I stop?" | confirmed tiers never decay (03.6.3); provisional ones are tested (04.8.2); a fold is offered, never forced (04.8.6) |
| "Can I be two things?" | three deed seats; hybrids and consolidation (04.8.1, 04.8.5) |
| "Can I change what I picked?" | one re-pick per calling per season; Retrain in downtime (04.8.7) |
| "What does breaking my oath do?" | the three stages, each warned (04.9.2–04.9.3) |
| "How do I get it back?" | atonement's clock (04.9.4) |
| "Why did that NPC call me that?" | V1 or V8: a name for a deed, from ch.11 |

---

## State touched

**State families read** (00.6.3 names). Tallies, counted tallies, conduct tallies, the evidence-bearing scene
list and the reflection digest (03; sealed or background) through `tally`, `detail`, `share`, `dominance`,
`profile`, `cooccurrence`, `diversity`, `conduct`, `counted`, `public` (03.9); the evidence ledger's deed
lines (available); callings, licenses, slots and abilities (04, 05); attributes (02); commitments (04, 11);
NPC role tags, depth and standing (12, 15); faction status and `institutions_matching` (11); place
`resonance` (10, 13); harm states and the scene log (07, 12) for the Taking's circumstance; adversary tags,
threat band and `absorbable` (09); time, scenes and boundaries (00, 12); aspirations (02).

**State families written** (owner: 04).

| Family | Type (00.6.1) | Visibility (00.6.4) | Notes |
|---|---|---|---|
| Callings, tiers, lifecycle, roads, specialties, seats, Fraying stage, suspension | fields of the PC entity | **shown** once recognized | `Character.callings` extended per 04.1.2 |
| Competence entries with `source: call.*` | competence map | available | highest-only (00.3.6) |
| Capability licenses `lic.call.*`; training grades | license | shown | via `grant` / `revoke` |
| Pick allowance, unspent picks, legacy picks | quantity / meta | shown | slots themselves are ch.05's |
| Standing offers of kind recognition | offer | shown | 04.7.3 |
| Oaths and bonds | commitment | shown, forbidden acts in full | keeper registered as bonded witness (03.10.4) |
| Atonement clocks `clk.atonement.<calling>` | clock (progress; public) | shown | created by 04.9.4 |
| The Devourer's library | list on the PC | shown | slotted powers are ch.05's acquired slots |
| Readiness bands (Leanings) | meta | **available** (band words only) | 04.6.5 |
| Offer log with `tally_snapshot` | ledger | available; snapshot **sealed** | audit (03.9.5) |
| `recognition_event` | ledger | background (ch.11 consumes) | 04.7.8 |
| Decline records, vehicle recency, pending attribute increase | meta | background | |
| Atonement evidence events | via `record_evidence(op: atonement)` | per 03 | 03.8.4 |

**Tools used** (00.14.2). `evaluate_recognition` (#26, owner 04); `offer_create` / `offer_resolve` (#27);
`grant` / `revoke` / `retire` (#28); `generate` (#24) for `gen.absorb`; `frame_check`, `roll_check`,
`apply_costs` (#1, #2, #5) for the Taking; `create_clock` / `tick_clock` (#23) for atonement; `set_fact`
(#10) for commitments and tokens; `record_evidence` (#25) with `op: atonement`; `apply_effect` (#16) for
banes and boons; `get_active_triggers` (#30). The DM supplies only ids, enum values and the player's words.

**Hooks subscribed** (through effects in data): `on_defeat`, `on_degree`, `on_boundary`, `on_fact_set`,
`on_condition_removed`, `on_stabilize`, `on_clock_complete` (the nine Focus triggers); `on_degree`,
`on_focus_spent`, `on_defeat`, `on_vitality_threshold` (hybrid composites); `on_tag_event` (a dark calling's
price); `on_harm_dealt`, `on_frame` (absorbed powers; Master's Eye). All are depth-0 subscribers (INV-12).

**Boundary handlers.** Reserved and defined here: `h.04.recognition_pass` (`reflection`, 8; PR-04-1),
`h.04.standing_offers` (`reflection`, 8; 04.7.3), `h.04.season_consolidation` (`season`, 8; PR-04-8). Added
in `data/boundaries.yaml owner-block 04`: `h.04.crisis_check` (`beat_end`, 8; PR-04-2), `h.04.provisional_check`
(`reflection`, 8; PR-04-6), `h.04.fraying_check` (`scene_start`, 8; PR-04-7).

**Triggers raised** (`trg.` prefix, 12): `trg.04.crisis_offer`, `trg.04.offer_due`, `trg.04.lapse_warning`,
`trg.04.fraying`, `trg.04.pick_due`.

**Clocks created.** `clk.atonement.<calling>` (progress; 4 or 6 segments; public). No readiness clock is
created: readiness is a derived band, so that no second copy of a sealed tally exists to drift (DL-04-13).

**Data files.** `data/callings.yaml`, `data/hybrids.yaml`, `data/vehicles.yaml`, `data/gen_absorb.yaml`;
contrib: `composites.04.yaml`, `licenses.04.yaml`, `boundaries.04.yaml`, `tags.04.yaml`.

**Runtime capabilities assumed** (00.14.1). RC-SEAL and RC-QUERY (sealed tallies, tag ancestry, 03.9);
RC-STORE (callings, offers, commitments, library); RC-SCHED (handlers at `reflection`, `season`,
`scene_start`, `beat_end`); RC-LOG (offer log, recognition events); RC-RNG and RC-DATA (the generator, pick
tie-breaks, data validation); RC-EVAL (effects of triggers, composites, boons, banes); RC-RETRIEVE (trigger
surfacing and card loading).

---

## Interface requests

**To 00 (proposed amendments; this chapter works within 00 as written meanwhile).**
1. **`gen.pick`.** Register the pick procedure (04.8.4, PR-04-5) as a generator domain with fill method
   `chosen`, or accept it as "an equivalent tag-gated selection". It uses 00.11.3 steps 1, 2, 4 and 6.
2. **T-00-19:** allow an owner-block "04" in `licenses.yaml` (the six `lic.call.*` licenses now in
   `data/licenses.yaml owner-block 04`).
3. **Expression context** for `applies_when` / `when` (effects.yaml header): add `secondary_tags`,
   `gate.mode`, and the resolver "your calling key". Until then composites read the frame's recorded
   grounded secondaries.
4. **Tool #26:** the trigger enum is `reflection | crisis | arrival | request`; the packet shape is 04.4.6.
5. **Tool #28:** `retire` takes `superseded_by` and leaves specialties (04.8.5); `grant` takes
   `provisional: true` and a `source` offer id.
6. **T-00-9:** add `h.04.crisis_check` (`beat_end`, 8), `h.04.provisional_check` (`reflection`, 8),
   `h.04.fraying_check` (`scene_start`, 8).
7. **00.6.2:** `Character.callings` gains the fields of 04.1.2; `Offer.content` is `{calling, tier,
   alternatives}`.
8. **00.4.3 (b):** note that the one attribute increase is applied when tier 4 is confirmed.
9. **Glossary:** seat, pick, pick allowance, lineage, road, specialty, legacy pick, variant, keeper, shadow,
   Fraying (stages Dimmed / Fraying / the Choice), lapse, fold, fork, consolidation, turn, readiness band,
   Leanings, confirmation (K1–K5), the Taking, library, bane.
10. **Constitution PATCH candidates:** (a) P5's "calibrated classifier … MUST NOT share a model family" →
    "a deterministic scorer whose per-candidate confidence is defined and calibrated in chapter 04" (04.4.1,
    DL-04-10); (b) VI: record that per-character provisional status is an extrapolation from content
    leagues (DL-04-15); (c) P5's "hybrids key only on pairs of deed branches" is kept; variants (same key,
    added requirement) are a Delve-shaped addition (DL-04-06).
11. **00.11.5** says relics never feed calling tiers. Nothing in 03 or 04 yet excludes deeds done through a
    relic's license. Proposed: ch.08 marks relic-granted licenses `feeds_evidence: false` and 03 drops deed
    events gated by them. Until then such deeds count.

**To 02 (Character).** Origins grant competence of at most +2 (so tier 1's +3 is a step up). At least one
origin per magic branch should grant a first license of that branch, and `gen.birth` should be able to grant
an innate `deed.primal.elements` license (the sorcerer's spark). Aspirations should carry tags (`{text, tags}`)
so that the Leanings view and offer ordering can match them. Optional backstory evidence (03.2.8) is
compatible: it cannot satisfy any floor.

**To 03 (Tags and evidence).** (a) Confirm `detail().peak_band` is the highest challenge band among
**successes** at the node, and that `by_band` counts every settled contribution; a `success_by_band` array
would make the great-deed rule exact (the simulation used one). (b) `detail(tag, since)` should accept a
scene index or time, and the evidence-bearing scene count since a time should be readable. (c) For the
Devourer: a count of distinct opponent kinds outside `creature.folk` at the root; until it exists the rule
reads `detail(pc, deed).distinct.opponent_kinds ≥ 6`. (d) Optional: `conduct().pos_events` and a count of
magnitude-4 positive entries, to allow a qualitative requirement for higher vow tiers. (e) Reconcile
`data/tags.yaml`, adopted at integration (`deed.wilds.animals.falconry`); if it is ruled an alias of
`deed.wilds.animals.training`, re-key `call.falconer` to that tag. (f) Satisfied here: judged and counted
thresholds together, quality and distinct-scenes floors (04.3.2); atonement events (04.9.4); bonded
witnesses named (04.7.4); `power_band` (04.5.6); confidence defined (04.4.2); tally values logged with each
recognition (04.7.8); `include_pending` used only by the crisis check (04.4.5); Fraying stages at strain
4 / 8 / 12 or a forbidden citation, as 03 suggested.

**To 05 (Abilities, Focus, magic). The pool this chapter draws from.** Callings own no abilities; every
pick is drawn from `data/abilities.yaml`. For that to work, 04 needs:
1. **Sizes.** The calling partition's size `S` (04 assumes 12; the rules hold for 9–16) and the acquired
   partition's size (assumed 4).
2. **Fields on every `slot_class: calling` ability:** the first `tags` entry a deed tag at level 2 or 3 (as
   03 also asks); `min_tier` 1–5; `mod_group`; `ranks: [{rank, text, effects, cost, limits}]`, each rank a
   **complete restatement** (at most 3); optional `replaces: [ab.*]` (an upgrade path: the new ability takes
   the old one's slot); optional `requires_conduct: [axis]` and a conduct tag for oath-gated abilities;
   `adversary_only` where it applies.
3. **Coverage.** At least two calling abilities under every level-2 deed tag, one of them `min_tier` 1; at
   least twelve per branch with two or more at each `min_tier` 1–5; at least two per positive conduct axis
   (`min_tier` 1 and 3). Where 05 authors fewer, the kin pool fills the candidates and unfillable picks are
   kept; nothing breaks.
4. **Rank rule.** `rank = 1 + floor((calling tier − min_tier) ÷ 2)`, capped at the authored ranks (04.5.5).
   05 may replace the formula; 04 needs only that rank is a function of the holding calling's tier.
5. **Training licenses.** One or more `lic.training.*` per level-2 deed tag whose methods the basic verbs
   exclude, with ordered grades `trained < expert < master` and `recognition` among the acquisition paths.
   04 sets the grade by tier (04.5.1); 05 owns what each grade's scope is.
6. **Focus triggers.** The nine family triggers (`callings.yaml#families`) each restore 1 Focus once per
   scene (twice from tier 4). 05 owns Focus and may retune units, limits or hooks.
7. **Emulate and stretch.** Sure Hand and the Open Art read `frame.gate.mode` and each license's `emulate`
   price; every license needs those fields (as 01 also asks).
8. **Absorbed powers.** The 27 pool entries of `gen_absorb.yaml` are abilities with `slot_class: acquired`;
   05 mirrors them by reference, and provides the re-slot at `rest_long`.
9. **Composites.** Merge `data/composites.yaml owner-block 04` as owner-block 04; `ranks` and `rank_rule` are
   optional fields.
10. **Tools.** `grant` / `retire` on `slots.calling` with `source: {calling, tier}` and `provisional`.

**To 06.** The conditions and flags used in data are 00's reserved ids. "Bloodied" (Vitality at or below
half) must be readable as a state expression. The martial Focus trigger reads the defeated foe's threat band.

**To 07.** Whether the PC was Staggered or Dying at any point in a conflict must be readable from the scene
log (the Taking's circumstance). Penance uses one S3 cost from 01's menu.

**To 08.** The Taking's crude fallback is harvesting materials; see item 11 to 00 about relics.

**To 09.** Each archetype: `absorbable {pool_gate_tags, cannot_absorb}`, at most one `signature_of` entry
among `gen_absorb.yaml#pool` (09's requests to 04 on `signature_of` and on narrowing `no_pool` are met:
revision I-020), and a record in the scene log when a creature uses a power (the "witnessed"
condition). `threat_advisory` consumes `power_band`. The simulation assumed opposition from the PC's band to
band + 2; encounter budgets that differ will move the pacing of tiers 3–5 (OEQ-04-1).

**To 10 and 13 (now the region's seed, 12.16; ch.13 is one optional pre-made seed).** Places may carry
`resonance: [tag]` (deed keys, branches or conduct axes) for V11. The region's seed: the powers that serve
as keepers, with the conduct axes each cares for (12.16.6); institutions per deed branch for V3 and V9
(12.16.10); whether the four `none` pairs hold in the setting (12.16.5: they do; only a pre-made setting may
author a hybrid for `divine × primal`). T-12-16 checks all three (`ws.req.04_*`) [revision: I-028].

**To 11.** Consume `recognition_event` (04.7.8) for reputation, epithets (V1's wording is 11's), rumors,
faction status and ranks; apply a standing step only when `decline_cost` is set. Provide
`institutions_matching(branch, region) → [{faction_id, status_to_pc, has_ranks, next_sitting}]`. Restitution
is a thread. `h.11.season_turn` (phase 6) runs before `h.04.season_consolidation` (phase 8). Retirement reads
`apotheosis_available(pc)` and retires every calling (04.11.4).

**To 12.** Recognition offers are pause point 7 rendered by 12.15.6; this chapter's texts are in
`vehicles.yaml#markers`. **Proposed label** `[RECOGNITION]` (one line, before a crisis offer's CHOICE block).
The lead engine places the NPC that V2 or V12 needs (role tags supplied). Open offers appear in the
SITUATION block. New callings create rotation facets (12.9.1). 12.14.5's forbidden list governs every
staging.

**To 14.** Codex views: **Callings** (shown: name, tier and tier name, provisional flag, competence, grades,
capabilities with literal text, picks with literal text, composite or boon or trigger, shadow name, seats);
**Oaths** (wording, keeper, forbidden acts in full, Fraying stage); **Offers** (open and standing, with
their CHOICE text); **Leanings** (available: key tag name and band word only). The guide should say plainly:
you become what you do under pressure; nothing is taken without warning; every offer can wait.

**To 15.** The training activity writes `cnt.training` (with a mentor holding `lic.call.proof`, at the
mentor's rate); a **Retrain** activity (one week, one pick swapped by PR-04-5); a **Penance** activity (one
week at the keeper's place). NPC `role_tags` use deed tags so that V2 and V6 can find mentors and readers.

**To 16.** `tracks_evidence` companions follow 04's Edge cases (one seat, tier ≤ 3). Companions are valid
witnesses and carriers for V1.

---

## Open empirical questions

Each has a shipped default and a named test.

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-04-1 | Do the thresholds give the intended pacing in real play, where scene mix and opposition differ from the model? | W 80 / 200 / 440 / 800 / 1,300 (narrow) and the other ladders; 04.3 | **T-04-PACE**: log the session of each recognition over three campaigns of 20+ sessions; target tier 1 at sessions 3–6, tier 2 at 8–12, tier 3 at 16–24; if outside, scale every W by one common factor (the since-requirements stay) |
| OEQ-04-2 | What do the counters actually yield, by pillar? | counted = W ÷ 10 (04.3.3) | **T-04-COUNT** (with 03's T-03-COUNT): counted ÷ weighted at each PC's top three nodes after 10 sessions; target 0.10 never binding for honest play in any pillar. **Measured** (revision I-004; T-04-8 R12): binds only a band-1, mob-only, no-Focus fighter, by one fight in eight; ÷ 10 kept (DL-04-27). Live-play test kept: lower the divisor if it delays any pillar's tier by more than one session |
| OEQ-04-3 | Is confidence calibrated in live play as it is in simulation? | K1–K5; grant at 4+ (04.4.2–04.4.3) | **T-04-CALIB**: for every first-eligible candidate, record its score and whether the grant or accepted offer was later confirmed; target confirmation ≥ 85% at scores 4–5 and a rate that rises with the score; if grants confirm under 80%, raise the grant cutoff to 5 |
| OEQ-04-4 | Does the hybrid trigger separate deliberate mixing from incidental use? | min 60, balance 2/5, joint scenes 5 (04.2.4) | **T-04-HYB** (R3 G-1): in the same logs, classify each PC's play by hand as single-track, second-pillar or mixed; target no hybrid offer for single-track, an offer for every mixed PC by session 6 |
| OEQ-04-5 | Do players feel a grant as recognition or as an imposition? | grant, provisional and renounceable (04.4.3, 04.8.2) | **T-04-GRANT**: after each grant ask one out-of-fiction question ("did that feel like yours?"); if more than a quarter say no, make every first recognition an offer (the policy's row 3 is removed) |
| OEQ-04-6 | Does vehicle selection vary enough, and does the DM pick the fitting one? | recency of two; DM picks among ≤ 3 (04.6.2) | **T-04-VEH**: over 30 recognitions, no vehicle used more than 40% of the time; two readers agree with the DM's pick in ≥ 80% |
| OEQ-04-7 | Are the Fraying stages felt as fair warning? | strain 4 / 8 / 12; forbidden act → stage 3 (04.9.2) | **T-04-FRAY** (with 03's T-03-STRAIN): playtests with one grave act and with one forbidden act; the player can state, before stage 3, what would cause it; time from stage 1 to clear by deeds 2–6 sessions |
| OEQ-04-8 | Is 12 / 24 evidence-bearing scenes the right trial? | confirm from 12, lapse at 24 (04.8.2) | **T-04-PROV** (R3 G-4): lapse rate of provisional grants in live play; target under 10% for players who did not change style, over 70% for those who abandoned the key at once; ask whether a lapse was expected |
| OEQ-04-9 | Are three deed seats and one oath seat the right cap? | 3 + 1 (04.8.1) | **T-04-SEATS**: how often a fourth candidate arrives before session 20 and what the player does; if consolidation is declined and a release is chosen more than half the time, test 4 seats with S unchanged |
| OEQ-04-10 | Can non-combat callings meet the crisis and great-deed requirements of tiers 3–5? | crises 2 / 3 / 4; great deeds by band (04.3.4) | **T-04-CRISIS**: sessions to tier 3 for PCs whose key is in lore, influence or craft; target within 1.5× the combat median. **Answered** (revision I-003): with 03.4.3's contest band and 03.4.5's ruinous and brink crises, envoy, smith and scholar reach tier 3 at 18 / 18 / 17 and tier 5 at 46 / 45 / 46 against the archer's 19 / 51 (within ±20%; T-04-8 R11). Live-play test kept as stated |
| OEQ-04-11 | Is the Taking worth its seat, and bounded? | 2 Focus; one per long rest; library 4–12; banes (04.10) | **T-04-TAKE**: simulate a Devourer against ch.09's bestiary for 30 sessions; target 4–8 library powers by session 20, never more than the acquired slots in use, and a win rate within 5 points of a same-tier Slayer |
| OEQ-04-12 | Is the Leanings view the right transparency? | key name and band word only (04.6.5) | **T-04-LEAN** (R3 G-16): two groups, one with the view and one without; compare how often players report pursuing an identity on purpose and whether recognition still surprised them pleasantly |
