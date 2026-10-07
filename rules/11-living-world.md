# 11 — The Living World

> This chapter makes the world move on its own, react to what the character does, keep offering
> things to do forever, remember everything, and let the player end a character's story on their own
> terms while the world goes on. It is built for an AI Dungeon Master, which is good at voicing a
> world and bad at remembering promises, paying off foreshadowing and pacing a long game. So nothing
> here depends on the DM remembering or deciding to make the world act: a **World Turn** runs at every
> `week` boundary and a **Season Turn** at every `season` boundary (00.7), as fixed, engine-run
> procedures; factions are records with tiers, ratings, goal clocks, linchpins and a status toward the
> character with a behavior contract per rung; situations carry default timelines that run when the
> character does nothing; every thread has three or more clue placements, a proactive fallback and a
> lifecycle that always ends; every rumor carries a sealed truth value fixed at birth; reputation is
> Ars Magica's `{content, scope, score}` fed only by witnessed deeds; holdings and great projects
> change the map through a closed list of world changes; the calendar, aging and the chronicle give
> the long game a shape and a memory; and retirement turns a finished character into world state, a
> legend that is partly wrong, threads that pass on, and a successor who starts at the floor in a world
> that remembers. Every change the world makes leaves a perceivable trace, because a simulation the
> player cannot perceive is wasted [R6 B-20], and every trace is computed, never improvised.

**Reading this chapter.** Rules are numbered `11.S.R` in thirteen parts: 11.1 the world's shape and
its state; 11.2 the World Turn; 11.3 factions; 11.4 situations, bangs and consequences; 11.5 threads
and hooks; 11.6 rumors, news and how information travels; 11.7 reputation; 11.8 institutions and
ranks; 11.9 holdings, great projects and rulership; 11.10 the calendar and aging; 11.11 the Season
Turn and the Year Turn; 11.12 the chronicle; 11.13 retirement and legacy. Procedures are PR-11-*,
tables T-11-*, worked examples WE-11-*. Machine-readable companions: `data/factions.yaml` (faction
templates, generic factions, the agenda and entanglement tables), `data/world_turn.yaml` (the steps,
world-reaction rules, rumor, hook, epithet and seasonal tables, thread ranks, attention),
`data/calendar.yaml` (the engine; the region's seed names months and festivals, 12.16.15, and a pre-made
setting may use its owner-block) and
`data/legacy.yaml` (endings, settlement, legend ranks, ledgers, inheritance, timeskips). Additions to
shared files are in `data/boundaries.yaml owner-block 11`, `effects.11.yaml` and `tags.11.yaml`.

---

## Design intent

**Goals served.** Goal 1 (the player feels free to try any creative idea) is served here at the scale
of a campaign: the player may go anywhere, take any side, ignore any hook, found a town, topple a
guild, swear a vow or walk away, and the world answers each choice through the same procedures. Goal 2
(the AI responds correctly) is served by turning every living-world duty an AI does badly into engine
state with a trigger: faction intentions are clocks with omens; the world's default future is a
timeline of observable steps; foreshadowing is a sealed fact with a gate; a hook is a record with
three placements and a fallback; consequence is a rule keyed to a fact pattern; memory is an
append-only chronicle; pacing is chapter 12's director choosing among this chapter's bangs.

**The research this rests on.**
- *The world moves:* Stars/Worlds Without Number's faction turn (maintain → goal → one action →
  rumors) [R6 B-01; R5 P-23; R: https://takeonrules.com/2018/12/27/lets-read-stars-without-number-factions/];
  Blades in the Dark's tier, hold, status −3…+3 with a behavior contract per rung, faction clocks,
  heat and entanglements [R6 B-02; R5 P-18, P-22; R: https://github.com/amazingrando/blades-in-the-dark-srd-content/blob/main/Blades-in-the-Dark-SRD.md];
  Mausritter's one-d6 faction roll for the small fry [R5 P-25; R: https://mausritter.com/srd/how-to-play/];
  Ars Magica's covenant seasons as an institutional lifecycle [R6 B-05]; Kenshi's world states from
  pivotal NPCs, here linchpins with pre-declared fates [R6 B-08].
- *The world reacts:* Crusader Kings III's on_actions and pulses with weighted eligible events,
  cooldowns and an explicit weight for "nothing happens"
  [R6 B-17; R: https://ck3.paradoxwikis.com/Event_modding]; Valve's and Hades' "most specific
  eligible rule wins" [R6 B-19]; the Alexandrian's situations with if-ignored timelines and bangs
  [R6 B-12; R: https://thealexandrian.net/wordpress/4154/roleplaying-games/dont-prep-plots-prepping-scenario-timelines];
  NCP-Bench's typed commitments and trajectory nodes with observable deltas [R1 #10].
- *The world offers:* the Three Clue Rule and proactive nodes [R6 B-13; R5 P-41]; Mythic's weighted
  threads and characters lists [R5 P-07, P-08]; Ironsworn vows ranked by difficulty [R5 P-14];
  Forbidden Lands' legends with fixed truth values [R6 B-04]; West Marches' rumor-driven frontier
  [R6 B-15].
- *The world is paced:* chapter 12 owns the director (Left 4 Dead, RimWorld); this chapter supplies
  its candidates with `intensity_delta` and a specificity key [R6 B-10, B-11; 12.7.4].
- *The world remembers and finishes:* Dwarf Fortress's legends and retire/abandon [R6 B-07, D-12];
  Pendragon's Winter Phase, heirs and inherited Glory [R6 B-06, D-02; R5 P-44]; Ironsworn's Continue
  a Legacy with bad results that are hooks too [R6 D-04; R5 P-43]; Wildermyth's legend tiers [R6 D-05];
  Rogue Legacy's three heirs with trade-offs [R6 D-13]; Legacy: Life Among the Ruins' age-jumps
  [R6 D-09]; Kingdom's promotion of someone already in the story [R6 D-10].
- *What the AI does badly:* abandoned plot elements and unfired foreshadowing [R4 W11; R1 #10];
  inventing facts late [R4 W8]; positivity bias that keeps factions from acting against the player
  [R4 W3]; repetition [R4 W10]; rule decay over long play [R4 W12]. Each is answered by a `[D]` or
  `[T]` rule below, never by an exhortation.

**Shape decisions (each recorded in the Decision Log).**
- The World Turn has eight fixed steps and runs on the `week` boundary whether the character is in a
  dungeon, a tavern or a timeskip (DL-11-01). Weekly is SWN/WWN's "each downtime or each seven days,
  whichever first" made a single rule [R5 P-23].
- Faction actions are **engine rolls** (d20 + rating + twice the tier against a DC), the action is
  picked by a **temperament agenda table**, never by the DM, and the target by a closed priority list
  (DL-11-03, DL-11-04). This removes the AI's positivity bias from the world's hostility: a faction
  at war with the character acts against them on schedule, not when the DM feels like it.
- Consequence propagation is **one link per World Turn**: an `on_fact_set` reaction may queue,
  tick or write, at depth 1 (INV-12), and what it writes is read by the next World Turn as new input.
  Chains therefore advance a week at a time and cannot run away inside a turn (DL-11-07).
- Every consequential world change emits at least one perceivable trace — a rumor, a news item, a
  visible change, an omen — so the player can read intent into the world [R6 B-20] (DL-11-10).
- Threads, hooks, rumors, reputation entries, situations and world phenomena all have lifecycles
  that end; registers are capped, and the Season Turn consolidates them. Principle VI applies to
  world content as much as to abilities [C:VI; R1 #10] (DL-11-12).
- Reputation is separate from recognition (00.17.1 Q22): the world's words about the character never
  grant capability; ranks are seats with obligations and never tiers (DL-11-15).
- Retirement is the largest structural retirement in the game: everything the character *is* retires;
  only bounded channels carry value forward (DL-11-20).

**What this chapter deliberately avoids.**
- A scripted finale, a plot with required outcomes, or a "main quest". There are situations, and the
  character chooses where to push [R1 11; BRIEF §4].
- The DM deciding *whether* a faction acts, *whether* a rumor is true, *how much* reputation a deed
  earns, *what* a successor inherits. Each is a table, a roll or a formula.
- Simulation the player cannot perceive. Factions the character has never heard of are still run, but
  the petty ones on a single d6 (DL-11-05), and every change of consequence surfaces as a trace.
- Unbounded escalation. Faction clocks complete at roughly one goal per faction per season to year
  (WE-11-1, the simulation in T-11-24); attention decays; entanglements wait for the director's
  phase; the bang queue is capped.
- A diegetic System. Status, renown, legend rank and attention are numbers in the engine and words
  in the world ("the Guild's men have stopped drinking where you drink").
- Inheritance of power. A successor starts at chapter 02's floor (02.2.7); what passes on is renown in
  small measure, one heirloom, ties, places known and troubles owed.

**Kinds of rule in this chapter.** Most rules are `[D]` (the engine runs them at boundaries) and `[T]`
(fired from tracked state). The DM's judgments are few and closed: which listed reaction a fact
pattern matches (`[J:enum]`), whether a deed is known to a faction (`[J:flag]`), the scope of a world
change (`[J:rung]`), the wording of rumors, epithets and chronicle lines (`[N]` inside closed forms).
Each carries its Worst case line (00.2.3).

---

## Rules

### 11.1 The world's shape and its state

**11.1.1 What the living world is made of.** `[D]` The living world is the set of records below, held
in the state store (00.6.1) and owned by this chapter (00.6.3). Every record is an entity or a fact, a
clock or a ledger of 00.6.1; none lives in narration or in the DM's context [C:P13; R1 #1].

| Record | Entity kind / type | What it is | Rule | Visibility (00.6.4) |
|---|---|---|---|---|
| **Faction** | entity `faction` | an organization with tier, hold, ratings, temperament, goal clock, stage, linchpins, relations, status toward the PC | 11.3 | existence and status: available once known; goal, clock, linchpins: sealed (omens shown) |
| **Situation** | entity `object` (subtype `situation`) | a state of affairs with actors, a default timeline of observable steps and an end state | 11.4.1 | sealed (its steps surface as traces) |
| **Bang** | queue entry | an event waiting to come looking for the PC, with `intensity_delta` and a specificity key | 11.4.4 | sealed until fired |
| **World reaction** | data rule `wr.*` | a fact pattern and the eligible responses to it | 11.4.6 | background |
| **Thread** | entity `thread` | an entry in the quest register: vow, quest or situation, with a progress clock, ≥ 3 clue placements and a fallback | 11.5 | shown once active; seeded hooks available as text |
| **Hook** | entity `thread` at status `seeded` | a thread not yet taken up | 11.5.6 | available (text only) |
| **Rumor** | entity `rumor` | a claim in circulation with a sealed truth value and a `points_to` | 11.6 | text shown once heard; truth sealed |
| **News** | fact, `certainty: established`, `visibility: shown` once it reaches the PC | a true public change, spreading by the same rule as rumor | 11.6.6 | shown once heard |
| **Reputation entry** | fact on the PC (or a persona) | `{content, scope, score, valence_by_scope}` | 11.7 | content and scope available; score background |
| **Rank** | relationship `rank` PC→faction | a seat with obligations | 11.8 | shown |
| **Holding** | entity `place` with a `holding` record | a property the PC owns | 11.9 | shown |
| **World phenomenon** | fact with lifecycle | a seasonal condition of a region (a plague, a comet year, a hard winter) | 11.11.4 | shown once perceived |
| **Attention clock** | clock `kind: danger` | a faction's notice of the PC | 11.3.12 | hidden (omens) |
| **Change log** | ledger | every world-relevant fact written since the last World Turn | 11.2.3 | background |
| **Chronicle** | ledger | the append-only history of the world | 11.12 | available |
| **Legacy record** | entity `object` (subtype `legacy`) | a retired or dead PC's settled account | 11.13 | available |

**11.1.2 Regions, scopes and the map.** `[D]` The place graph is chapter 10's (10.1). This chapter
reads three levels of it and uses them as **scopes** everywhere a thing spreads, is known or is held:
- a **settlement** scope: a place tagged `terrain.settlement.*` and everything inside it;
- a **region** scope: a place of chapter 10's kind `region` (one home band and one danger rating);
- the **realm** scope: every region of the campaign (one at the start; a new region joins it by 12.16.18).
A faction id (`fac.*`) is also a scope: the faction's members and officers, wherever they are (03.10.5).
Every NPC that chapter 12 generates at depth recurring or principal has a `home` (a settlement or, for
a wanderer, a region) and its faction memberships (`member_of: [fac.*]`); this chapter writes the
membership of every faction officer and linchpin when the faction is created, and gives each the
faction's `seat` settlement as home unless one is recorded (03's request: scopes need homes).
[03.10.5; R6 A-15 (Ars Magica's reputation types are scopes)]

**11.1.3 Distance in scope steps.** `[D]` Spread, news and reputation move in **scope steps**, counted
on the place graph: two settlements are **neighbors** when a route link joins them in at most **8
travel watches** (two days of travel, 10.3); a settlement's region holds it; the realm holds every
region. The distance from scope A to scope B is the number of steps along settlement → neighbor →
region → realm needed to reach B. All spread timings in this chapter are in World Turns per step
(T-11-12). [R6 A-15 "social distance"; DL-11-11]

**11.1.4 The world's present tense.** `[S]` + `[D]` Every fact this chapter writes is **true now**. The
future lives only in clocks, default timelines and sealed plans; a faction's intention to burn the
mill is a goal clock with omens and a situation step, never a fact "the mill will burn". Secrets are
sealed facts with gates, and every unrevealed thing that matters has a positive-ignorance fact when an
NPC might otherwise be thought to know it ("the reeve does not yet know the well is poisoned")
[R1 #10 (T=0 isolation); SG-27; 00.6.5]. So the narrator's view at any moment contains nothing that
has not happened, and nothing it may not say.

**11.1.5 What the narrator receives from the living world.** `[D]` From this chapter's records the
narrator view (`get_state(view: narrator)`) receives only: faction names, public facts and their
status rung *as behavior* (11.3.8), never the number; omens selected by the engine for hidden clocks
that ticked (INV-14); rumor and news texts that reached the PC's scope; the fired bang's content; the
reputation entries' contents for the current scope and their tone (a band, 11.7.7); the chronicle
lines the scene may cite (11.12.4). Goals, linchpins, timelines, attention, rumor truth and the bang
queue are sealed. Narration may not imply any of them (INV-10).

### 11.2 The World Turn

**11.2.1 When it runs.** `[D]` + `[T]` Handler `h.11.world_turn` runs at every `week` boundary, phase 6
(world), whatever the time mode and wherever the PC is: in a dungeon, on the road, in downtime, in
captivity, or during a retirement timeskip (11.13.8 [verification: V2b-013]). `advance_time` never skips it (00.7.7, INV-15):
three weeks of travel are three World Turns. It runs after the phase-4 upkeep handlers (`h.08.upkeep`,
`h.16.retinue_upkeep`) and after phase 5's automatic clock ticks (`h.00.clock_auto`), and before the
other phase-6 handlers of higher chapter numbers (`h.15.downtime_week`, `h.15.member_standing`), which
therefore see its results [00.7.5; DL-11-01; R5 P-23 "each downtime or each 7 in-world days"].

**11.2.2 The eight steps.** `[D]` The World Turn runs these steps in this order, each over every record
it names, and writes each result through the ordinary tools (`set_fact`, `tick_clock`,
`set_relationship`, `create_entity`, `chronicle_append`). The steps and their handlers are listed in
`data/world_turn.yaml#steps` [R6 B-R1].

| Step | Name | What happens | Rules |
|---|---|---|---|
| 1 | **Elapse** | Close the week's change log (11.2.3); stamp the turn `{year, season, week}`; read where the PC is and whether play is suspended (timeskip) | 11.2.3 |
| 2 | **Maintain** | Holdings' yields and threats; rank obligations due; linchpin fates; slips and recoveries; faction stage effects; pursuits | 11.3.9, 11.8.5, 11.9.4 |
| 3 | **Timelines** | Every active situation's week-cadence steps whose `at` has come or whose trigger holds; completions of clocks that phase 5 ticked | 11.4.2 |
| 4 | **Faction actions** | Each full faction, in order of tier (highest first, ties by id), takes **one** action from its agenda table; each petty faction rolls its d6 | 11.3.5–11.3.7 |
| 5 | **Consequences** | The weekly pulse: each logged change of the week is matched against the world-reaction rules; at most one reaction fires per change, most specific eligible first | 11.4.6–11.4.8 |
| 6 | **Attention** | Attention clocks decay or complete; completions become entanglement bangs | 11.3.12 |
| 7 | **News and rumors** | Every consequential change of steps 2–6 emits its trace; news and rumors spread one scope step; rumors age; what reached the PC's scope is listed for narration | 11.6 |
| 8 | **Queue** | The bang queue is updated; the thread register is upkept (stalls, expiries, retirements); the hook supply rule runs; list weights are adjusted | 11.4.4, 11.5.8–11.5.10 |

Handler `h.11.world_record` (`week`, phase 9) then appends the turn's chronicle lines (11.12.2).

**11.2.3 The change log.** `[D]` Every `set_fact`, `set_relationship`, `create_entity`, clock completion,
`recognition_event`, `public_deed` packet, `victory_over_pc` and setback fact written since the last
World Turn whose key matches a pattern in `world_turn.yaml#logged_patterns` is appended to the **change
log** with its time, writer and depth. Step 1 closes it; steps 2–8 read it; the next turn opens a new
one. The log is how the world reacts to everything that happened during the week without the DM
recalling any of it [R6 B-17 (CK3 pulses read what happened); R4 W12; SG-19].

**11.2.4 What the World Turn may not do.** `[D]` The World Turn never harms the PC, applies a cost to
the PC, moves the PC, grants or removes a license, tier or ability, reveals a sealed fact except
through its gate, or resolves a thread the PC has sworn a vow to or progressed in the last twelve
scenes (12.6.5's protection, which this chapter adopts for every off-screen resolution). What reaches
the PC from the World Turn reaches them as **traces** (11.6) and **bangs** (11.4.4), which chapter 12
frames into scenes, where the PC acts and the ordinary rules apply [R1 #9 "never make hidden
adjustments"; DL-11-02].

**11.2.5 Interrupts.** `[T]` The World Turn is `interrupting` (00.7.8) only when one of its writes puts
an event **at the PC's location now**: a move-on-the-PC action whose target is the place the PC is in
(11.3.6 row `move_on_pc`, `arrives: now`), a situation step whose place is the PC's place, or a
linchpin consequence that changes the PC's place (the town is put to the torch). Then `advance_time`
halts after the week boundary finishes its phases, and chapter 12 frames the scene. Every other result
waits in the bang queue for the pacing director (12.7.4), so the world's pushes arrive when the pacing
allows, not when the clock happens to strike [R6 B-11; 12.7].

**11.2.6 Suspended play.** `[D]` While no PC is in play (a retirement timeskip, 11.13.8 [verification: V2b-013]), steps 1–8 run
unchanged except that: step 4's `move_on_pc` rows read as `goal`; step 6 runs decay only; step 7's
"what reached the PC" list is written to the legacy record instead of narration; and step 8 neither
fires the hook supply rule nor queues bangs (the queue is cleared at the timeskip's start and refilled
for the successor, 11.13.8).

**11.2.7 Output.** `[D]` The World Turn returns, for narration (PR-00-2 step 5): the omens of hidden
clocks that ticked (one per tick, INV-14), the news and rumor texts that reached the PC's current
settlement scope this turn, any interrupt, and the count of bangs queued (not their content). The DM
narrates the passage of the week from this list and adds nothing that is not in it (INV-2). Most weeks,
most of the World Turn is invisible: the player hears of it later, in a tavern, from a road-warden,
from a price, which is the point [R6 B-20].

**11.2.8 Cost and scale.** `[D]` The number of records the World Turn runs is bounded by data so that
it stays cheap at the thousandth week: at most **six full factions** per region and **twelve** in the
realm (the rest are petty, 11.3.2); at most **eight active situations** per region (the Season Turn
retires the oldest beyond that, 11.11.3); at most **six** bangs queued (11.4.4); at most **twelve**
active threads and **eight** seeded hooks known to the PC (11.5.9). These caps are Principle VI at
world scale: the world grows by replacing, never by piling up [C:VI; DL-11-12].

### 11.3 Factions

**11.3.1 The faction record.** `[D]` Every faction conforms to this shape (`data/SCHEMAS.md#factions.yaml`
plus the optional fields listed in T-11-1). Templates and generic factions are in
`data/factions.yaml`; a region's factions are written by its seed (12.16.10; a pre-made setting such as
chapter 13 uses its owner-block) [R6 B-R2; R5 P-22, P-23] [revision: I-028].

```yaml
Faction (extends Entity, kind faction):
  id: fac.*
  org_tags: [org.*]              # the org facet (00.5.1): what kind of organization it is
  patron_deeds: [tag]            # deed branches or tags it honors (institutions_matching; gifts' pool gate)
  values: [{axis: conduct.*, pole: "+" | "-"}]   # what it admires and despises: reputation valence (11.7.7)
  tier: 0..5                     # 11.3.3
  hold: weak | strong            # 11.3.4
  ratings: {force, cunning, wealth, sway}        # 0..tier+2 each; sum = 4 + 2 x tier (11.3.4)
  temperament: aggressive | cautious | mercantile | zealous | secretive | steadfast   # 11.3.7
  lifecycle_stage: rising | flourishing | entrenched | declining | collapsed           # 11.3.9 ("stage")
  full: bool                    # 11.3.2
  goal: {text, kind: grow | dominate | change, scope: local | regional | realm,
         clock: clk.*, rating: force | cunning | wealth | sway, effects: [effect_ref], target: id | null}
  seat: place_id                 # its headquarters; a scope for reputation and rumor
  holds: [place_id]              # places it controls (07.6.3's holding places are drawn from here)
  linchpins: [{npc: npc.* | role slot, consequence: str, fates: {dies, captured, turned, exposed: [effect_ref]}}]
                                 # sealed (11.3.10); `consequence` is SCHEMAS' one-line summary
  officers: [npc.*]              # principal NPCs; each carries one duty (11.3.17) [verification: V2b-013]
  duties: [str]                  # its officers' inviolable duties (15.2.4 item 5)
  relations: {fac.*: -3..+3}     # toward other factions (11.3.14) [verification: V2b-013]
  status_to_pc: -3..+3           # 11.3.8 (00.17.1 Q13: members default to it)
  attention: clk.* | null        # 11.3.12
  pursuit: 0..3                  # 11.3.12
  ranks: rank ladder id | null   # 11.8
  sittings: [calendar ref]       # when its ranks are conferred (11.8.3)
  fields: [{archetype: arch.*, role: rank_and_file | officer | champion}]   # what it sends (09)
  boon_base: item tag            # its customary gift (08.7)
  boon_signature: prop.* | null  # its gifts' identity property (08.7.2)
  courtable: bool                # whether it courts the PC's allies (16.12.5)
  lifecycle: provisional
```

**11.3.2 Full and petty factions.** `[D]` A faction is **full** while any of these holds: its tier is
2 or more; its status toward the PC is not 0; a thread, situation or rank names it; the PC has met one of
its officers. Otherwise it is **petty**. Full factions take the full World Turn action (11.3.5–11.3.7); petty factions
roll one d6 (11.3.14). If a region would have more than six full factions, the six that rank first by (in
order) a non-zero status, a thread naming them, the highest tier, then the lowest id are full and the
rest run as petty factions that turn. A faction that becomes full keeps its record; nothing is generated anew.
Mausritter's single die for the small fry and SWN's full turn for the powers keep the cost proportional
to what the player can perceive [R5 P-25, P-23; R6 B-20; DL-11-05].

**11.3.3 Tier.** `[D]` + `[J:rung]` (the rung only when generating a faction that data does not give)
Tier is a faction's scale and reach on a 0–5 ladder (Blades' tier [R6 B-02]). It sets the dice it rolls
with (11.3.5), the scope of the goals it may pursue, the band of what it fields (09) and the tier cap of
its gifts (08.7.2: tier 0–1 → 1, 2 → 2 … 5 → 5).

| Tier | Anchor: what it is | Typical / near a boundary | Goal scopes | Fields (rank and file / officers / champion) |
|---|---|---|---|---|
| 0 | a handful who matter locally | a gang of five footpads / a hedge-witch's coven of three in one village | local | T1 / T1 / T2 |
| 1 | a local power | a town's chapter of a guild / a bandit company of thirty that owns a road | local | T1 / T2 / T3 |
| 2 | a town's power or a small regional one | a town council and its watch / a hunters' lodge with houses in three villages | local, regional | T2 / T2 / T3 |
| 3 | a regional power | a margrave's household and levy / a merchant house whose caravans cross the region | local, regional | T2 / T3 / T4 |
| 4 | a power of the realm | a great noble house / a church with a cathedral in every region | regional, realm | T2 / T3 / T4 |
| 5 | a power of the age | a kingdom / an ancient order that has outlived three dynasties | regional, realm | T3 / T4 / T5 |

Fielded adversaries are chapter 09's archetypes at those threat bands with the faction's `org_tags`
added (a pool-gate widening only, 09's request). *Worst case (J):* a generated faction one tier off:
its rolls shift by 2 and what it fields by one band; recorded at creation and shown to the player as
words once the PC learns of it (class i).

**11.3.4 Hold and ratings.** `[D]` **Hold** says how securely the faction keeps its tier: `strong` or
`weak`. A faction that **loses hold** goes strong → weak; if it was already weak, it drops one tier and
its hold becomes strong (it consolidates what it has left); a tier-0 faction that loses a weak hold
**collapses** (11.3.9). A faction that **gains hold** goes weak → strong; if it was already strong, it
rises one tier with a weak hold (it has grown faster than it can hold). Rising above tier 3 needs a
completed `grow` goal of `realm` scope; any other gain at tier 3 or more only makes the hold strong
[R6 B-02 (Blades' hold); DL-11-06].

**Ratings** are four integers, each 0 to `tier + 2`, summing to `4 + 2 × tier` (4, 6, 8, 10, 12, 14 for
tiers 0–5): **force** (arms, numbers, violence), **cunning** (spies, secrets, subtlety), **wealth**
(coin, goods, credit), **sway** (faith, law, popularity, legitimacy). When a faction's tier changes the
sum changes by 2: on a rise, its goal rating and then its lowest rating gain +1 each; on a fall, its two
highest lose 1 each (ties broken in the order force, cunning, wealth, sway); every rating is then
clamped to the new cap. Magic is not a fifth rating: an arcane order's sorcery is its force or its
cunning, as its template says, and its `org_tags` say what kind [R6 B-01 (SWN's Force, Cunning, Wealth);
DL-11-06].

**11.3.5 The faction check.** `[D]` Every faction action that can fail is one engine-rolled check with
00.3.10's degrees, logged like any roll (INV-4). The faction is the acting side:

`total = d20 + rating + 2 × tier + stage modifier`, the modifier clamped to −8…+16 (00.3.5).

Stage modifier: rising +1; flourishing 0; entrenched −1 on `goal` and `expand` (complacency) and +1 to
its own defense; declining −1 on everything. A scheme's lever (11.3.6) adds +2, at most one per check.

| DC source | DC |
|---|---|
| a `goal` action | `10 + 2 × tier + scope term` (local 3, regional 5, realm 7). The faction's own tier cancels: great factions chase great goals at the odds small ones chase small goals |
| an action against another faction (`strike`, `scheme`, `court` of a faction) | `10 + the defender's rating named by the action + 2 × the defender's tier`, +1 if the defender is entrenched, +2 if the target is the defender's seat |
| `expand` | `10 + 2 × tier + 5` |
| `recover`, `court` of a person or a neutral | `10 + 2 × tier + 3` |

There is no reach in a faction check; results are by degree only. *Arithmetic* (exhaustive d20 under
00.3.10; scratchpad `world11.py`): a flourishing faction whose goal rating is 3 pursuing a local goal
needs 10+ on the die — success-or-better 55%, critical success 5%, critical failure 5%; the same faction
on a regional goal 45% (critical failure 10%), a realm goal 35% (critical failure 20%: great designs slip
visibly). A strike between equal-tier rivals whose attacking and
defending ratings are equal succeeds 55% [DL-11-03].

**11.3.6 The faction actions (closed list).** `[D]` A full faction takes exactly one action per World
Turn. Every action's results are fixed by this table; the DM chooses nothing in them.

| Action | Check | Critical success | Success | Failure | Critical failure |
|---|---|---|---|---|---|
| `goal`: work toward its goal | goal rating vs goal DC | goal clock +2 | goal clock +1 | no tick | **slip**: no tick; a true trace of the failure; next turn's action is `recover` |
| `strike`: weaken a rival | force vs the defender's higher of force and cunning | the defender loses hold, and d6: 1–3 one of its hold places passes to the striker; 4–6 one non-linchpin officer is killed or taken (if none, a place) | the defender loses hold | a trace (a skirmish heard of) | the striker loses hold (the counterblow) |
| `scheme`: spy, steal, suborn, sabotage | cunning vs the defender's cunning | as success, and one sealed fact of the defender (a linchpin's secret, a hidden hold) is unsealed to the schemer and seeded as a true rumor | the fact `fac.<a>.inside.<b>`: a +2 lever on the schemer's next check against that rival or toward a goal that names it; spent when used | nothing | discovered: the defender's relation toward it −1; a trace |
| `expand`: buy, build, settle | wealth vs its DC | gain hold, and a new hold place in its region | gain hold | nothing | a debt: wealth −1 until its next completed goal |
| `recover`: lick wounds, purge, rebuild | higher of wealth and sway vs its DC | hold strong; slip cleared; goal clock +1 | hold strong; slip cleared | nothing | nothing; the slip stays |
| `court`: win someone over | sway vs its DC | as success, for two targets | the target (11.3.7): an ally of the PC is **courted** (16.12.5: `courted_by`, sealed, with an omen); a faction's relation toward it +1 | nothing | the courted party learns it was being worked on: relation −1, or the ally's standing toward the faction −1 |
| `move_on_pc`: act against the PC | none (certain) | — | an **entanglement** bang is queued from `tbl.11.entanglement` at the faction's pursuit column (11.3.12) | — | — |
| `aid_pc`: act for the PC | none (certain) | — | the first eligible of: pay the PC's ransom (15.7.5) if the PC is a captive with a ransom due; send help (an ally mob of its rank and file, 16) to the PC's holding under a threat bang; write `gift_due.<faction>` if a reward is owed (08.7.2); queue an **opportunity** bang (a job, a tip, a safe house) | — | — |
| `lie_low`: do nothing visible | none | — | its attention clock on the PC decays 1 extra; no trace | — | — |

Every success or critical success of `goal`, `strike`, `scheme` (critical only), `expand` and `court` is
a **consequential change** (11.6.2) and emits a trace. A goal clock that is `hidden` or `sensed` renders
one omen per tick (INV-14). Goal clocks list `{on: random_event, ticks: 1}` and, for the factions the PC
can fight, `{on: rout, ticks: U(S3)}` among their tick sources, so that chapter 12's random events and
chapter 07's rout may move them (12.6.5; 07.4.3) [R6 B-01, B-02; R5 P-23; DL-11-04].

**11.3.7 Which action: the agenda table.** `[D]` The DM never chooses what a faction does. Before
rolling, the first of these that holds is the action: (a) a **slip** last turn → `recover`; (b) the
faction is **at war** (relation −3) with a faction that has its seat or a hold in the same region, and a
d6 shows 1–3 → `strike` against it; (c) its status toward the PC is +2 or more and either one of
`aid_pc`'s first three results is due (a ransom due, a threat bang naming the PC's holding, a reward owed) or a
d6 shows 1 (it brings the PC work: the opportunity bang) → `aid_pc` [revision: I-032: the opportunity bang is
always eligible, so the unqualified override made a friendly faction aid the PC every week and never work its
own goal]. Otherwise the engine rolls a d6 on the faction's **temperament** row
(`factions.yaml#agenda`); a row whose condition fails reads as `goal`:

| d6 | aggressive | cautious | mercantile | zealous | secretive | steadfast |
|---|---|---|---|---|---|---|
| 1 | strike (a rival at ≤ −2) | recover (if weak) | expand | strike (a rival at ≤ −2) | scheme (a rival at ≤ −1) | recover (if weak) |
| 2 | strike (a rival at ≤ −2) | scheme (a rival at ≤ −1) | scheme (a rival at ≤ −1) | court | scheme (a rival at ≤ −1) | aid_pc (status ≥ +2) |
| 3 | move_on_pc (status ≤ −2 and the PC in its region) | court | court | move_on_pc (status ≤ −2) | move_on_pc (status ≤ −1 and its attention at half or more) | strike (a rival at −3) |
| 4 | expand | goal | goal | goal | lie_low (its attention on the PC at imminent) | goal |
| 5 | goal | goal | goal | goal | goal | goal |
| 6 | goal | goal | goal | goal | goal | goal |

**Targets** `[D]`: a `strike` or `scheme` goes to the eligible rival with the lowest relation; ties to
the rival whose goal clock is fullest (stop the leader), then the highest tier, then the lowest id. A
`court` goes, first match, to (i) an ally of the PC (16) who has a recorded tie to the faction's
`org_tags` and whose standing toward the PC is Warm or lower, if the faction is `courtable` and its status
toward the PC is 0 or lower; (ii) the non-rival faction whose relation toward it is highest below +2;
(iii) else the action reads as `goal`. A `kn.loyal` ally at Neutral or warmer is never a target
(16.12.5). Roughly half of every row is `goal`, so a faction spends most turns on its own project and
the rest on rivals, the PC and itself. *The positivity-bias guard:* because the row is rolled and its
condition is read from state, a faction at −2 toward the PC moves against the PC on schedule whether or
not the DM is inclined to be kind [R6 B-01; R4 W3; DL-11-04].

**11.3.8 Status toward the PC: the behavior contract.** `[D]` A faction's status toward the PC is a
standing (00.3.16), −3…+3, moved only by 11.3.11's steps. Each rung is a contract that the faction, its
officers and its members keep; the DM plays them literally. Members' standing is the status plus their
personal offset (15.1.3), recomputed by `h.15.member_standing` at once whenever this chapter writes a
status [R6 B-02; R5 P-22; 00.17.1 Q13].

| Status | Rung | The faction… | World Turn rows it enables | What the PC can see |
|---|---|---|---|---|
| +3 | Devoted | helps even at a cost to itself; shares what it knows when asked; its holds are havens for the PC (`safe: true` for the PC); offers a rank at its next sitting if it has ranks and the PC holds none there | `aid_pc` (override c; steadfast row 2) | members greet the PC by name; doors open |
| +2 | Friendly | helps when the cost is not serious; brings the PC work (opportunity bangs); gives when a reward is owed; its holds take the PC in for the night | `aid_pc` | jobs offered; credit extended |
| +1 | Warm | helps when it is cheap; trades fairly; passes on news (what it tells the PC is never a rumor it knows to be false) | — | a fair price; a tip |
| 0 | Neutral | deals on ordinary terms; neither helps nor hinders | — | business as usual |
| −1 | Wary | makes trouble when it is cheap; watches the PC (an attention clock exists, 11.3.12); refuses its hospitality | secretive `move_on_pc` | doors shut; questions asked |
| −2 | Unfriendly | harms the PC when the cost to itself is not serious; denies the PC its holds' services and tells its members to | `move_on_pc` (aggressive, zealous, secretive) | warnings; refusals; a price on small favors |
| −3 | Hostile | goes out of its way to harm the PC even at a cost; every loud deed against it ticks its attention one more (11.3.12); its pursuit column counts one higher; its strikes may target the PC's holdings as if they were a rival's holds | `move_on_pc`; strikes at the PC's holdings | open war: bounties, ambushes, burned bridges |

*Narration may not imply* a status the record does not hold, or behavior outside the rung: an officer of
a Hostile faction who helps the PC does so through a personal offset that is written (15.1.3), never
"because she likes them" [R4 W3, W4].

**11.3.9 The faction's life: stages.** `[D]` Every faction is in one **stage**, the institutional lifecycle
of Ars Magica's covenant seasons [R6 B-05]. The stage modifies its checks (11.3.5) and changes only by
these rules, which the Season Turn applies (11.11.3 step 2 [verification: V2b-013]) except where "at once" is stated:

| From | To | When |
|---|---|---|
| rising | flourishing | it has completed a goal since entering the stage, or has spent 4 Season Turns rising |
| flourishing | entrenched | its tier is 4 or more, or it has spent 8 Season Turns flourishing |
| flourishing or entrenched | declining | it lost hold twice or more in the last four seasons; or its tier fell; or a linchpin fate names `declining` (at once) |
| declining | rising | it completes a goal while declining (renewal; at once) |
| declining | collapsed | it loses a weak hold at tier 0 (at once); or it has spent 4 Season Turns declining at tier 0 |
| any | collapsed | a linchpin fate names `collapse` (at once) |

**The weight of size.** At each Season Turn a faction of tier 3 or more rolls `d20 + its highest rating +
stage modifier` against `10 + 2 × tier`; on a failure it loses hold. Great institutions bleed without
anyone attacking them, which is what keeps the map from filling with tier-5 powers (T-11-24: across 300
two-year runs the mean tier rose about 0.6 and no faction passed tier 3) [revision: I-032] [R6 B-05; DL-11-06] [integration: I-026].

**A collapse** removes the faction from the World Turn. Its holds become unowned places; its officers
become free NPCs who keep their records; its members keep their personal offsets toward the PC; it
writes a chronicle line and a news item; and the Season Turn (or at once, if mid-season) rolls
`tbl.11.vacuum` (d6) for who fills the gap: 1–2 its strongest rival takes its seat (a gain of hold); 3–4
a new faction rises from its remnants (a template of the same `org_tags`, tier 1, rising, one former
officer as its head); 5 the region is lawless for a season (a situation, 11.4.1); 6 nobody yet, and a
seeded hook says so (the PC could fill it: a great project, 11.9.7 [verification: V2b-013]). No faction is ever deleted (00.16.3);
it stays in state as `collapsed` so the chronicle and old rumors still resolve.

**11.3.10 Linchpins.** `[S]` + `[T]` + `[D]` Each full faction names one to three **linchpins**: NPCs
whose fate deterministically rewires the world (Kenshi's world states [R6 B-08]). Each linchpin carries,
**sealed and written when the faction is created**, four fates — `dies`, `captured`, `turned`,
`exposed` — each a list of effect references (state writes: a hold lost, a stage change, a goal
replaced, a new situation from a template, a relation changed, a successor named). They fire by
`on_fact_set` hooks on these facts, never by narration:
- **dies**: `npc.<id>.exists` becomes `dead`;
- **captured**: a captivity fact names the NPC as held by anyone other than its own faction;
- **turned**: the NPC's `member_of` gains a different faction, or the NPC accepts the PC's cause by a
  recorded agreement (15.7.6) that its faction would forbid;
- **exposed**: one of the NPC's sealed secrets is made public in the faction's scope (a `public` news
  item, 11.6.6, or `cost.exposure` at S5 against it, 01.13.6).
A fate fires **once**; its writes are depth 1 (INV-12), and what they write the next World Turn reads
as input (11.4.7). The narrator is told nothing until the writes surface as traces. A fate is never
"decided when it happens": a world that will lose its toll-bridge if the bridge-warden dies has known so
since the warden was written, which is what makes killing him a choice rather than a gamble
[R1 #10; R6 B-08; DL-11-08].

**11.3.11 How the PC's deeds move status.** 

```
### 11.3.11  Faction status from the PC's deeds                    [J:flag] [D]
Trigger [T]:        a logged change (11.2.3) or a resolved beat names the faction, its members, its
                    holds, its goal clock or its rival: one of the rows of T-11-3
Loads in:           core while any faction status is non-zero; situation.social, situation.conflict
License check:      n/a
Decisions (J):      1. KNOWN [J:flag] "Does this faction know the PC did it?" True only when (first
                       match): a public_deed packet's scopes include the faction's id or its seat
                       settlement (03.10.5); an aftermath link names one of its members (03.10.3); the
                       PC told, claimed or showed it to a member (record_knowledge, 15); one of its
                       schemes unsealed it (11.3.6); a news item carrying it reached its seat (11.6.6).
                       False otherwise, including a deed with no carrier. Uncertain -> false (Blades:
                       a job kept perfectly quiet moves nothing).
                    2. ROW [J:enum] of T-11-3, by the deed's literal effect on the faction; a deed that
                       fits two rows uses the one with the larger step; uncertain -> the smaller.
Computation [D]:    steps per T-11-3 (data: world_turn.yaml#status_steps). Caps: rows marked
                    "small" move status at most 1 per faction per World Turn in total; deeds of
                    weight (marked "weight") may move it 2; the total change per faction per World
                    Turn is at most 2. Unknown deeds are held in the change log with known: false and
                    are re-tested when an aftermath link appears; they move status then. Then:
                    set_relationship(faction -> pc); h.15.member_standing at once; if status fell to -1
                    or lower and no attention clock exists, create it (11.3.12).
Stakes:             none (a world write)
State writes:       relationship faction->PC; attention clock; change log entry
Narration may not imply: that a faction reacts to a deed it does not know; a step larger than the
                    row; a faction "softening" with no row
Worst case (J):     KNOWN wrongly true: one step too early (the deed would usually have reached them;
                    class iii); wrongly false: the step is applied when the aftermath link appears
                    (class iv). ROW one step off: one standing rung (class i).
Examples:           inside: Wren burns the Salt Guild's tally-house in front of two carters whose home
                      is Ashford, the Guild's seat -> known; row "struck its holds" (weight) -> -2.
                    outside: she burns it alone at night and is never seen -> unknown; the Guild's
                      status does not move; the change log keeps it; if a fence later sells her out
                      (an aftermath link), -2 then.
                    boundary: a carter who saw her lives in Ditchling, not Ashford, and is no Guild
                      member -> the packet's scopes are Ditchling's; the Guild learns it when the news
                      reaches Ashford (two World Turns later, 11.6.6) -> the step lands then.
                    non-example: "The Guild must hate me now" (the player's assertion) -> nothing.
Anchor:             no
Basis:              [R6 B-02 (an operation shifts status -1/-2 with those it hurts, +1 with those it
                    helps, 0 if quiet)] [R5 P-22] [03.10.5] [DL-11-09]
```

**T-11-3 Status steps** (canonical: `world_turn.yaml#status_steps`).

| Deed (as known to the faction) | Step | Class |
|---|---|---|
| completed a thread the faction is patron of (it asked, or it benefits as the thread records) | +1; +2 if the thread's rank is formidable or higher | weight at formidable+ |
| accepted its institutional offer (V3, V9) or a rank | +1 | small |
| kept a rank obligation due this season (11.8.5) | +1, once per season | small |
| a week of service, a gift of 1 Unit or more of its lifestyle, or a deed its `values` admire done in its scope (a noteworthy `public_deed` with a conduct entry on an admired pole) | +1, once per season per source kind | small |
| spared, freed or ransomed its members; returned what was taken from it | +1 | small |
| helped its rival (completed a thread for a faction at −2 or worse toward it) | −1 | small |
| a deed its `values` despise done in its scope (noteworthy, on a despised pole) | −1 | small |
| robbed, defrauded or lied to it (an exposed lie, 15.5) | −1 | small |
| broke a rank obligation; sold its gift (08's anti-minting) | −1 | small |
| declined its offer with a `decline_cost` (04.7.8) | the cost's amount | small |
| killed or maimed its rank and file | −1 (once per scene) | small |
| killed, took or turned an officer; struck one of its holds | −2 | weight |
| foiled its goal (its goal clock voided by a racing clock the PC filled, or a thread completed against it) | −2 | weight |
| a linchpin's fate fired by the PC's hand | −3 if `dies` or `captured`; −2 if `turned` or `exposed` | weight (the per-turn cap does not apply) |

**11.3.12 Attention and pursuit: the world notices.** `[D]` + `[T]` A faction that is Wary or worse toward
the PC, or against which the PC has done a loud deed, keeps a hidden **attention clock**
`clk.11.attention.<fac>`: kind `danger`, **8** segments, visibility `hidden`, `then: reset`, with omens
from the faction's template (stirring: "a stranger asks the innkeeper which room is yours"; building:
"the same two men at the market two days running"; imminent: "your door's latch has been tried in the
night"). It is Blades' heat and The One Ring's Eye Awareness generalized to every faction [R5 P-18,
P-26; R6 B-02; DL-11-13].
- **Tick sources** (`world_turn.yaml#attention`): at `venture_end`, the venture's **loudness** toward the
  faction (11.3.13's reckoning: quiet 0, contained 1, loud 2, wild 3), +1 if the venture touched its seat
  settlement, +1 if any of its members died, +1 if the faction is Hostile; `cost.exposure` at S3 or
  heavier paid against its members or in its holds: U(severity); a noteworthy `public_deed` it would
  despise in its scope: 1; `random_event`: 1.
- **Decay:** −1 at each `week` with no tick (00.8.1 `decay`); `dt.lie_low` (15.13.15): −2 for each
  faction whose seat or hold is in the region where the PC lies low; `lie_low` action: −1.
- **Completion:** the faction's **pursuit** rises by 1 (0–3), and an **entanglement** bang is queued:
  `roll_table(tbl.11.entanglement, {column: pursuit + (1 if Hostile)})`, d6 + (status −2: +1; −3: +2),
  capped at 8. Each row arrives already in motion and names its ways out (Blades' entanglements
  [R6 B-02]). The clock then resets to 0.
- **Pursuit** falls by 1 at a Season Turn in which the clock did not complete, and to 0 when status
  rises to Neutral or warmer.

**T-11-4 Entanglements** (canonical: `factions.yaml#tbl.11.entanglement`; columns by pursuit 0–3,
rows d6 + status modifier). Every row is a bang (11.4.4) with its `intensity_delta`, its specificity
`faction`, and at least two ways out written into it.

| Row | Pursuit 0–1 | Pursuit 2 | Pursuit 3+ |
|---|---|---|---|
| 1–2 | **Questions**: an officer comes to ask what the PC was doing (social, 1) | **Watchers**: two of its rank and file shadow the PC; a sensed clock (social, 1) | **Warrant**: its writ or its price is posted in its scope; holds closed to the PC (threat, 3) |
| 3–4 | **Shakedown**: it demands a fee or a favor to forget it (social, 1) | **Reprisal**: it strikes something the PC values — a bond, a holding, an ally's livelihood (threat, 3) | **Show of force**: a band of its rank and file at the PC's lodging (threat, 3) |
| 5–6 | **Snare**: a false plea for help that leads to a place it holds (threat, 3) | **Ambush**: its fielded rank and file at the next route the PC takes (threat, 3) | **Champion**: its champion is sent with orders (threat, 3) |
| 7–8 | **Ultimatum**: leave its region within a season or face it (social, 1) | **Bounty**: a bounty clock (hunters, 6, public) (threat, 3) | **Abduction**: it takes a bond or ally to force a meeting (threat, 3) |

**11.3.13 The reckoning: what a venture cost the world.** `[D]` Handler `h.11.reckoning` (`venture_end`,
phase 6) reads chapter 10's venture record (10.2.2) and the change log of the venture, and for each
faction the venture touched computes its **loudness** toward that faction, first match from the top:

| Loudness | True when (all from state) |
|---|---|
| **wild** (3) | five or more of its members died; or one of its holds was seized, burned or destroyed; or a linchpin's fate fired |
| **loud** (2) | any of its members died; or a danger or alarm clock of a site it owns completed; or the PC took or freed a captive from it |
| **contained** (1) | `cost.exposure` at S3 or heavier was paid against its members or in its holds; or a carried `public_deed` names the PC acting against it |
| **quiet** (0) | none of the above |

Then, in order: (1) tick each faction's attention clock by its loudness and the modifiers of 11.3.12;
(2) apply the status steps of every deed it now knows (11.3.11); (3) for every site the record marks
`cleared` (10), write the world change "the wild draws back" (T-11-17 row `pacify`): the area's danger
rating steps down one rung (never below `settled`) until the next Season Turn, and permanently if a
holding or a faction hold is established within it before then; (4) write `occupants` changes and
evaded pending threats into the change log so that the next World Turn's consequences (11.4.6) read
them; (5) accept chapter 12's venture chronicle line (12.4.9) as one chronicle entry (11.12.2); (6) mark
every thread the venture touched (weights, 12.6.6; fallback counters, 11.5.7). The reckoning is how a
loud expedition becomes a world that has noticed, with no one remembering to make it so [R5 P-12, P-18;
10's request; DL-11-13].

**11.3.14 Factions against factions.** `[D]` Each faction holds a relation toward every other faction it
knows, on the standing scale (−3…+3; default 0, data or the region's seed sets the rest, 12.16.10). Relations move only
by these rows: the defender of a successful `strike` → its relation toward the striker −1 (−2 on a
critical success); a `scheme` discovered → −1; a successful `court` → +1 toward the courtier; a completed
`dominate` goal → the target's relation toward the victor −1; a faction at +3 toward a struck faction →
its relation toward the striker −1 (allies are dragged in); a thread completed by the PC that ends a
feud (T-11-17 row `reconcile`) → both set to −1 or the value the thread states. **War** is relation −3
in either direction: it enables override (b) of 11.3.7, and war between two factions is news in both
seats. **Cooling:** at a Season Turn, a pair at −3 that exchanged no strike or scheme that season moves
to −2; nothing else drifts on its own (enmity outlasts its causes). Faction-versus-faction outcomes are
always faction checks (11.3.5): opposed d20 rolls, the SWN shape on this ruleset's dice, with no
reasoning about who "should" win [R6 B-01; DL-11-03].

**11.3.15 Muster and clash: battles.**

```
### 11.3.15  Muster and clash: two forces in the field                [J:enum] [J:rung] [D]
Trigger [T]:        two factions at war meet in the field in the PC's scene (a strike resolved as a
                    battle because the PC is present at the target place), a siege of a place the PC
                    is in, or the PC leads a force (11.9.8) against a faction
Loads in:           situation.conflict.skirmish; situation.conflict
License check:      basic verbs and the PC's licenses for the PC's own beats; the factions need none
Decisions (J):      1. FRONT [J:enum]: the field (open battle), the wall (a siege or defended place),
                       the raid (a fast strike on a hold). Default: the field.
                    2. TIME UNIT [J:rung]: hour (a skirmish of dozens), watch (a battle of hundreds),
                       day (a siege). Default by the larger side's tier: 0-2 hour, 3 watch, 4-5 day.
Computation [D]:    each side has a BREAKING clock (kind danger, public to the PC once the
                    battle is joined, size by its tier: 0-1 -> 4, 2 -> 6, 3 -> 8, 4-5 -> 12; the wall
                    adds +4 to the defender's). At each time unit each side makes a faction check
                    (force vs the other's force; the wall: the defender's DC +2): critical success 2
                    ticks, success 1 on the OTHER side's clock. The PC's resolved beats in the battle
                    tick the enemy's clock by delivered reach (tick source pc_beat): holding a line
                    (16.7.12), felling a champion or officer (+2 extra), taking a standard, rallying a
                    broken flank (Talk to command, ticks own clock down by delivered reach: the only
                    tug in the procedure). The first clock to complete breaks its side (racing,
                    00.8.5): the broken side loses hold (twice if the field was its seat), the victor
                    takes the place if the front was the wall or the raid, and the losers flee (07's
                    dispositions govern the PC if the PC was on the losing side).
Stakes:             the PC's own beats carry their own stakes; a battle declares lethal_context for
                    the PC only through 07's warning
State writes:       breaking clocks; holds; places' owners; relations; chronicle line; news in both
                    seats; setback facts if the PC's side broke
Narration may not imply: the battle's result before a clock completes; that the PC's deeds decide it
                    beyond their ticks
Worst case (J):     FRONT wrong: the wall's +4 / +2 misapplied (class i); TIME UNIT one rung off: the
                    battle takes more or fewer hours, which the boundary handlers then run (class i).
Examples:           inside: the Ash Wardens (tier 1) meet the Ember Cult (tier 1) at the Cinder Ford
                      with Wren among the Wardens: field, hour; clocks 4 and 4; Wren kills the cult's
                      champion (delivered reach 2, +2) -> the cult's clock 4/4 at the first hour; the
                      cult breaks, loses hold.
                    outside: the Wardens strike the cult's shrine while Wren is two days away: an
                      ordinary strike (11.3.6), one roll.
                    non-example: a brawl of eight in a tavern: that is a conflict (06), mobs and all.
Anchor:             yes. Intent verbs: "lead", "hold the line", "storm", "besiege", "break their
                    ranks". Knobs: targets (the sides and their clocks; default as computed; allowed
                    delta: a third side with its own clock), time_cost (default by tier; allowed delta
                    one rung), dc (default force vs force; allowed delta +2 for a prepared position or
                    a wall), reach_unit (default delivered reach -> ticks; allowed delta: +2 for an
                    officer or champion felled). Covers: any clash of organized forces too large for
                    06's mobs. Does not cover: fights the PC can resolve as a conflict (06).
Basis:              [R6 B-01 (SWN opposed rating rolls)] [R5 P-21 (a progress track against a tension
                    clock)] [00.8.5 racing clocks] [16.7.12 held lines] [DL-11-14]
```

**11.3.16 Petty factions.** `[D]` A petty faction rolls one **d6** per World Turn for its goal (a local
goal on a 6-segment clock, hidden with omens): 1–3 nothing, 4–5 +1 tick, 6 +2 ticks; +1 to the die while
rising, −1 while declining. Its completion writes its goal's effects (`factions.yaml#petty_goals` [verification: V2b-013]: it
grows — hold, then tier, and at tier 2 it becomes full; it takes a place; it starts a situation; it
feuds — relation −2 with a named neighbor) and seeds one hook. Petty factions never take `move_on_pc`; one whose
status toward the PC leaves 0 becomes full at once (11.3.2) [R5 P-25; DL-11-05].

**11.3.17 Officers, members and what a faction sends.** `[D]`
- **Officers** are principal NPCs (12.11.1): a full faction keeps one to four. Each holds one **duty**
  from the faction's `duties`, written as that officer's refusal of kind `refusal.duty`, `absolute` (15.2.4 item 5; `social.yaml#refusal_kinds`) [verification: V2c-007]:
  the Watch-captain's "never opens the gate after curfew", the Guild factor's "never sells below the
  tally price". A new officer created by any chapter takes the next duty in the list (cycling).
- **Members** are NPCs with `member_of: [fac.*]`. Their standing toward the PC defaults to the status
  (15.1.3); this chapter writes membership for every NPC a faction fields or names.
- **What it sends** `[D]`: when any rule has a faction field people (an entanglement, a strike resolved
  in the PC's presence, `aid_pc` help, a battle), the engine draws from its `fields` by role, at the
  bands of T-11-2 (11.3.3) for its tier, with its `org_tags` added to each adversary's tags (09's
  request), using chapter 09's group shapes. The DM chooses no number of people.
- **Victors grow** `[D]`: when a member of a faction is the `victor` of `victory_over_pc` (07.6.2), the
  faction's status does not move, but the victor gains standing among its own: if it is rank and file it
  becomes an officer (taking the next duty) when a seat is open, and its Nemesis result
  (`tbl.09.nemesis`, 09.9.3) is written; a `nem.boast` result is a rumor of this chapter (11.6.3, source
  `boast`, truth by T-11-11); `nem.hunts` creates its hunt clock as a danger clock owned by this chapter
  (6, hidden, +1 a week, omens), which on completion queues a threat bang with specificity `pc_deed`.

**11.3.18 Where factions come from.** `[D]` + `[J:enum]`
- **Data:** the region's seed writes its factions (12.16.10: at least three full, goal clocks running), and a
  pre-made setting writes them in its owner-block of `factions.yaml` (chapter 13); either way they conform
  to 11.3.1 and to a template (`factions.yaml#templates`) [revision: I-028].
- **Templates:** `factions.yaml#templates` holds eighteen templates, each keyed to a level-2 `org`
  kind, eight of them also marked as their branch's default (`branch_default_for`): ratings by tier, temperament, values, patron deeds, rank ladder,
  duties, fields, boon base and signature, omens for its goal and attention clocks, and its goal list.
  Choosing the template is `[J:enum]` over the faction's `org_tags`: the deepest tag with a template,
  else its branch's (most-specific-wins, 00.5.4). *Worst case (J):* a sibling template (a smugglers'
  template for a thieves' guild): ratings and temperament of a near kind, fixed at creation (class i).
- **Vacuums** (11.3.9) and **new regions** (a region discovered or generated by chapter 10's procedures
  or 12.16.18 with no factions recorded) roll `tbl.11.faction_seed` (d12 by the region's settlement
  tier and terrain) for one to three factions, tier by `tbl.11.faction_tier` (d6: 1–2 tier 0, 3–4 tier
  1, 5 tier 2, 6 tier 3), each written with its linchpins' fates sealed at once (11.3.10).
- **The PC's own:** a faction the PC founds (11.9.7) or a holding large enough to be one (a keep is a
  tier-1 faction, 08.8.8) is created from the template of its `org_tags` with the PC as its head; it
  takes the World Turn by 11.9.8.
A faction is never invented in narration. A name spoken in a tavern belongs to a faction in state or is
written as one, by these rules, before the narration is delivered (00.6.6).

### 11.4 Situations, bangs and consequences

**11.4.1 Situations.** `[D]` + `[S]` A **situation** is a state of affairs that will change if nobody
intervenes: the Alexandrian's "situation, not plot" with its if-ignored timeline [R6 B-12], made of
NCP-Bench's trajectory nodes, each a trigger and an observable change [R1 #10].

```yaml
Situation (entity kind object, subtype situation):
  id: sit.*
  title: str                       # names the state of affairs, never the PC's task ("The Mill Feud")
  template: sit_t.* | null         # world_turn.yaml#situation_templates
  region: place_id
  actors: [fac.* | npc.*]          # who drives it; filled from state when created
  premise: [fact_id]               # what is true now (present tense only, 11.1.4)
  cadence: day | week              # how often its steps are tested
  timeline:                        # the default future, sealed
    - {n: 1, at: {after: "3 days" | "2 weeks"} | null, trigger: fact pattern | clock completion | null,
       requires: [step n],         # earlier steps that must have fired
       prevented_by: [fact pattern],   # PC-made facts that stop this step
       key_delta: [effect_ref],    # the observable world change (state writes)
       trace: str,                 # the perceivable sign, seeded as news or rumor (11.6)
       bang: bang template | null} # the step comes looking for the PC
  end_state: [effect_ref]          # the new status quo if every step fires
  if_prevented: [effect_ref]       # the status quo if the PC stopped it
  thread: thr.* | null             # the situation thread, once the PC knows of it (11.5.2)
  status: active | concluded | defused | retired
  lifecycle: provisional
```

A situation's timeline is written **whole and sealed when the situation is created**, from its template
with the role slots filled from state (which faction, which NPC, which place) and every step's `at`
fixed. It is never "decided later" [R4 W8; 00.6.5]. Templates (`world_turn.yaml#situation_templates`,
sixteen generic shapes: feud, sickness, road of knives, succession, hunger, the hunting ground, the
rite, war comes, flood and fire, the debt, the missing, the festival's trouble, the cursed ground, the
prisoner, the scandal, the enemy) are what the world seed (12.16.12) and the generators instantiate.

**11.4.2 Running the timelines.** `[D]` + `[T]` Handler `h.11.situation_timelines` (`day`, phase 6,
interrupting per 11.2.5) tests every active situation of cadence `day`; World Turn step 3 tests those of
cadence `week`. A step **fires** when its `at` time has passed (counted from the situation's start) or its
`trigger` holds, all its `requires` have fired, and none of its `prevented_by` patterns holds. Firing
applies its `key_delta` (state writes), seeds its `trace` (11.6.2) and, if it has one, queues its `bang`
(11.4.4). A step whose `prevented_by` holds is **skipped**, permanently. When the last step fires, the
`end_state` is written; when every remaining step has been skipped, the `if_prevented` writes are made
instead; either way the situation is `concluded` or `defused`, a chronicle line and a news item are
written, and its thread (if any) is completed or failed (11.5.5). So an ignored situation reaches its
own conclusion on schedule, and a PC who acts changes which steps happen — never by the DM deciding
that the PC "probably stopped it", but by the facts their deeds wrote [R6 B-12; R1 #10; DL-11-07].

**11.4.3 Where situations come from.** `[D]` Only these create a situation (closed list): a faction's
`change` goal completing (its `effects` name the template); a linchpin fate; a collapse (11.3.9, vacuum
row 5); a seasonal event (11.11.4); a world reaction (11.4.6) whose candidate names a template; chapter
12's random event handing over a situation seed (12.6.5 item iv); `tbl.twist_s5` row 8 (the land
changes: 12's table, written here by `new_situation(template, region)`); a world change of a great
project (T-11-17); the region's seed (12.16.12); and a creation hook of kind `question` or `enemy` when it is
activated (11.5.6). A region holds at most eight active situations; the Season Turn retires the oldest
whose actors have all left or collapsed, then the oldest concluded-but-unretired (11.11.3).

**11.4.4 Bangs.** `[D]` A **bang** is an event waiting to come looking for the PC, kept in one queue that
chapter 12's pacing director draws from (12.7.4) [R6 B-12 "bangs"; R5 P-08].

```yaml
Bang:
  id: bang.*
  kind: timeline | fallback | entanglement | kicker | opportunity | world   # who made it
  source: id                       # the situation step, thread, faction, hook or reaction
  content: str                     # what happens, who comes, where: a template filled from state
  tag: threat | social | opportunity
  intensity_delta: 0..4            # default by tag: threat 3, social 1, opportunity 0 (12.7.4)
  specificity: pc_deed | npc | faction | region | generic    # 12.7.4's ranking key
  eligible_when: expr              # e.g. the PC is in its region; not in RELAX for a threat
  ways_out: [str]                  # at least two (Blades' entanglements list theirs)
  expires: {after: "4 weeks"} | condition
  if_unmet: [effect_ref]           # what happens off-screen if it expires unfired
  queued_at: time
```

Rules: (a) **specificity** is set by the bang's source: a bang caused by a deed of the PC's (a
reprisal, a boast, a victor's hunt, a witness to the PC's act) is `pc_deed`; one keyed to an NPC the PC
has met, `npc`; to a faction the PC has dealt with, `faction`; to the region, `region`; otherwise
`generic`. (b) The queue holds at most **six**; when a seventh arrives, the queued bang of the lowest
specificity (oldest among equals) is dropped and its `if_unmet` runs. (c) A bang that **expires**
unfired runs its `if_unmet` off-screen — the reprisal lands on the bond's workshop, the champion
waits at the bridge and moves on — and its trace reaches the PC as news. `if_unmet` writes may never
touch the PC's person, the possessions the PC carries, or the PC's licenses (11.2.4). (d) A **fallback**
bang (11.5.7) is not subject to the push's selection: chapter 12 fires it at the next `scene_start`
after it is queued (12.8.4). (e) A timeline bang expires when its situation's next step fires.
[R6 B-12; 12.7.4; 12's request (b); DL-11-10]

**11.4.5 The queue is never empty of the PC.** `[D]` At step 8 of each World Turn, if no queued bang has
specificity `pc_deed` or `npc` and the PC has an unfulfilled drive, an open bond, an aspiration or an
ally's personal thread that is not yet open, the engine queues one **kicker** from the most overdue of
them (chapter 12's rotation ledger, 12.9.2, names the most overdue facet): a bond's word arrives, a
rival's rumor, a chance at the drive. This is how the sandbox keeps offering the player their own story
among the world's [R5 P-46 (Beliefs tell the GM what to challenge); R6 A-R7; 02.9; DL-11-10].

**11.4.6 Consequences: the world reactions.** `[D]` + `[J:enum]` A **world reaction** is a data rule
(`world_turn.yaml#reactions`, `wr.*`): a fact pattern, conditions, and a weighted list of eligible
responses, each with a specificity, a cooldown and its writes, plus an explicit weight for "nothing
happens" — CK3's on_actions [R6 B-17; R: https://ck3.paradoxwikis.com/Event_modding].

```yaml
WorldReaction:
  id: wr.*
  on: fact key pattern             # e.g. "victory_over_pc", "fac.*.lost_hold", "pc.reputation.*.score>=3",
                                   # "loc.*.cleared", "npc.*.exists=dead", "recognition_event.kind=tier"
  when: expr                       # conditions on state
  candidates:
    - {id, specificity, weight: 1..6, cooldown: "4 weeks", scope: settlement | region | faction,
       writes: [effect_ref], bang: bang template | null, situation: sit_t.* | null}
  nothing_weight: int              # the weight of "the world shrugs"
```

```
### 11.4.6  Matching a change to a world reaction                        [J:enum] [D]
Trigger [T]:        World Turn step 5 for each entry of the change log; or an on_fact_set hook in play
                    (11.4.7) for patterns marked immediate
Loads in:           none (an engine step; the DM is consulted only for decision 1)
License check:      n/a
Decisions (J):      1. FAMILY [J:enum], only when the change is a deed line with free text (a
                       public_deed, a recognition_event's epithet_seed, a victory_over_pc's manner):
                       which reaction family its deed belongs to, from world_turn.yaml#deed_families
                       (eight: violence against folk, mercy, theft or fraud, sacrilege or piety, a
                       great beast slain, a place opened or cleared, a rescue, a betrayal). True only
                       when the deed line's literal act is of that kind; uncertain -> no family (the
                       change is matched by its key alone).
Computation [D]:    1. Collect every reaction whose `on` matches the change's key (and family) and
                       whose `when` holds. 2. Drop candidates on cooldown in their scope. 3. Keep only
                       the candidates of the HIGHEST specificity present (pc_deed > npc > faction >
                       region > generic): the most specific eligible wins (Valve, Hades). 4. Roll the
                       kept candidates' weights plus the reaction's nothing_weight (roll_table, RC-RNG).
                       5. Apply the winner's writes, queue its bang, create its situation (World Turn
                       only); start its cooldown. At most ONE reaction per logged change; at most SIX
                       reactions per region per World Turn (excess changes wait, in log order, for the
                       next turn).
Stakes:             none
State writes:       the winner's writes; bang queue; situations; cooldown facts; change log mark
Narration may not imply: a reaction that did not fire; a reaction to a change nobody in that scope knows
Worst case (J):     FAMILY wrong: a reaction of a neighboring family fires (an act of mercy read as a
                    rescue) - one bang or a fact the world keeps, of the same scope and weight
                    (class iv: later facts build on it; it cannot cost the PC directly, 11.2.4).
Examples:           inside: Wren kills the cinder drake that hunted the Ashwood (the change
                      great_beast_slain, family "a great beast slain"); reactions: "hunters flood the
                      wood" (region, 3), "the drake's mate comes for its killer" (pc_deed, 2), nothing
                      (2). Only pc_deed candidates are kept: the mate (2) vs nothing (2): d4 (1-2 the mate, 3-4
                      nothing) -> 2: the mate [verification: V2b-014]. A hunt clock and a threat bang (pc_deed).
                    outside: the same kill unwitnessed and unknown: the key fires (the drake is dead,
                      a fact), but the pc_deed candidate requires a carrier; only "hunters flood the
                      wood" and nothing remain eligible.
                    non-example: the DM feels the town "should" throw a feast: no reaction lists it;
                      nothing happens unless a table says so.
Anchor:             no
Basis:              [R6 B-17, B-19] [R4 SG-12] [DL-11-07]
```

**11.4.7 Two speeds of consequence.** `[D]` A reaction is either **immediate** (marked so in data) or
**weekly** (the default):
- **Immediate** reactions are `on_fact_set` subscribers (00.10.2). They fire during play on depth-0 writes
  and their own writes are depth 1, so they fire nothing further (INV-12). They may only queue a bang,
  tick a clock or write a fact — never create a situation or move a status. Use: a linchpin's fate, a
  witness running for the watch, an alarm raised by a death.
- **Weekly** reactions run in World Turn step 5 over the change log, and may do anything a world write may
  do (11.2.4). Their writes are new depth-0 changes **logged for the next World Turn**.
So a chain of consequences advances **one link per week**: the Guild loses its tally-house; next week its
rival moves on the Guild's roads; the week after, the margrave raises tolls to pay for the patrols. A
chain cannot run away inside a turn, and every link leaves a trace the player can see coming
[00.10.8; R6 B-17; DL-11-07].

**11.4.8 The pulse of the PC's own deeds.** `[D]` Every `public_deed` packet (03.10.5) and
`recognition_event` (04.7.8) of the week is a logged change; reputation (11.7) reads them first, then the
reactions. A deed seen by no carrier changes the world only through its physical facts (a dead drake is
dead), never through anyone's opinion of the PC [03.10; DL-11-09].

**11.4.9 Commitments the world keeps.** `[D]` World obligations are typed commitments (00.6.1) of three
kinds [R1 #10 (NCP-Bench)]:
- **invariant** — must stay true or false across a span ("the archive is locked at night"; "the Baron
  does not know of the smuggling ring until exposed");
- **ordering** — one event before another ("the heir is named before the old lord's funeral");
- **achievement** — a milestone that will happen unless foiled ("the cult completes the rite at the
  new moon": a situation step or a clock).
Each carries a `satisfaction_condition` and a `violation_condition`, written as fact patterns the engine
can test without interpretation. The engine tests them at every matching `set_fact` and at World Turn
step 5. In a sandbox a world commitment **foiled by the PC is not an error**: the violation is a recorded
outcome, its `on_foiled` writes run, and it is a logged change that reactions read. A narration that
breaks an invariant without a recorded cause is a claim-check error (12.3). The PC's own debts and
obligations are commitments too; `h.15.commitments_due` checks their dates; `tbl.twist_s5` row 7
("a debt is called in, now") reads `commitments_owed(pc)` (11.4.10).

**11.4.10 The world's answers to chapter 12's twists.** `[D]` Chapter 12's S5 twist rows need world facts
(12's request g). This chapter provides three queries: `havens(pc)` — every place with `safe: true` the
PC has used as a rest site in the last season, the PC's holdings first (row 2 "a haven falls" writes
`safe: false` on the first, with an occupying faction or a cause from the region's active situations);
`commitments_owed(pc)` — the PC's unfulfilled commitments of kind debt, obligation or vow with a creditor
in state (row 7 calls the first due); and `new_situation(template, region)` — row 8 creates a situation
from `tbl.11.land_changes` (d6: a road closes, a bridge falls, war reaches the region, a plague, a flood, a
famine), each a template of 11.4.1. Row 4 ("a patron withdraws support") withdraws the PC's
highest-ranked rank's privileges for a season (11.8.6) or, with no rank, sets the most favorable
faction's status one step lower.

### 11.5 Threads and hooks: the quest register

**11.5.1 The thread record.** `[D]` A **thread** is an entry in the quest register: an open matter the
PC has taken on, or that the world has offered. It extends 00.6.2's `Thread` shape [R5 P-07, P-08, P-14;
R1 #10]:

```yaml
Thread (entity kind thread):
  id: thr.*
  title: str                     # names the obstacle, never the method ("The Last Egg", not "Find the egg")
  kind: vow | quest | situation  # 11.5.2
  owner: pc | ally.<id> | world  # whose matter it is
  source: hook | drive | bond | aspiration | faction | situation | ally | rite | bargain | restitution
          | grief | case | bequest | rumor
  rank: troublesome | dangerous | formidable | extreme | epic          # 11.5.3
  progress_clock: clk.*          # kind progress; size by rank; public once active
  opposing: clk.* | null         # a racing clock (00.8.5): the threat that wins if the PC is slow
  patron: fac.* | npc.* | null   # who asked, or who benefits (status steps, rewards)
  against: fac.* | npc.* | null  # whom it opposes
  case: case.* | null            # chapter 15's clue graph (sealed nodes, placements, reserves)
  clue_placements: [ref]         # >= 3, of at least two holder kinds (11.5.6)
  fallback: [{trigger, form, delivers}]   # >= 1 (11.5.7)
  reward: fact_id | null         # what is owed on completion (a gift_due, coin, a rank)
  status: seeded | active | stalled | completed | failed | expired | abandoned | retired | bequeathed
  weight: 1..3                   # 12.6.6's list weight
  protected_until: scene index   # 12.6.5: progressed in the last 12 scenes, or a vow
  created_at / activated_at / closed_at: time
  lifecycle: provisional
```

**11.5.2 Kinds.** `[D]` + `[J:enum]`
- **vow** — the PC has sworn it (a commitment of kind vow written first): creation's long vow (02.9.1),
  the Bargain's debt (07.5.5), a vow offered at an ally's death (16.9.5), any solemn promise recorded by
  04.7.4's free-promise path. Vows never expire; they end completed, failed (made impossible by a fact)
  or abandoned. Fulfilling one emits `vow_kept` (01.16.2: fate +1).
- **quest** — someone asked, or the PC took a matter up: a job, a faction's commission, an ally's personal
  thread (16.12), a rite's "first you must" (05), a spirit's bargain (05), restitution (04.9.4), a case
  the PC opened (15), a dread obsession (07.11).
- **situation** — the PC has taken on a situation of 11.4.1 (its thread is created when the PC learns of
  it and acts on it; until then the situation runs unseen).
`[J:enum]` only when a matter could be two kinds: true **vow** only when a commitment of kind vow or oath
is written for it; true **situation** only when it is a situation's own thread; else **quest**. Uncertain
→ quest. *Worst case (J):* a vow filed as a quest could expire unseen; vows are always written as
commitments first, so the engine checks the commitment before expiring anything (class iv).

**11.5.3 Rank and size.**

```
### 11.5.3  Thread rank                                               [J:rung] [D]
Trigger [T]:        a thread is activated (11.5.6) without a rank given by its source's data
Loads in:           situation.downtime; situation.investigation; core at activation
License check:      n/a
Decisions (J):      1. RANK [J:rung] by what stands in the way (anchors):
                       troublesome - one obstacle, one or two scenes, within a day's travel
                         (fetch the stolen ledger from a tavern back room / talk a sulking heir home)
                       dangerous   - a few obstacles across a venture; real risk (clear the barrow /
                         find who is poisoning the wells of two villages)
                       formidable  - several ventures or a strong foe; a season's matter (break the
                         bandit company's hold on the road / win the guildmaster's seat)
                       extreme     - a regional power or a legend-band foe; a year's matter (bring down
                         the Salt Guild / slay the drake of the Cinder Hills)
                       epic        - the realm changes if it is done (end the war / wake the old king)
Computation [D]:    progress clock: troublesome 4, dangerous 6, formidable 8, extreme 12, epic 12
                    followed by a linked second 12 (two stages). Rank feeds: status steps (T-11-3),
                    the legacy Deeds ledger (11.13.5: 1/2/3/4/5 points), expiry timing (11.5.5), and
                    the chronicle (formidable and higher always get a line).
Stakes:             none
State writes:       thread.rank; progress clock
Narration may not imply: the size of the clock as a measure of how close the PC is (the clock is public
                    in the codex; narration speaks of the matter)
Worst case (J):     one rung off -> 2-4 segments or one stage (class i), shown in the codex at once,
                    where the player may question it.
Examples:           inside: "find who burned the ferry" with one suspect gang in town -> troublesome.
                    boundary: the gang turns out to be the Salt Guild's men -> the thread is not
                      re-ranked (ranks never move); a NEW thread "The Guild's Hand" is seeded.
                    non-example: rank by how much the player cares: no; rank is what stands in the way.
Anchor:             no
Basis:              [R5 P-14 (Ironsworn ranks: troublesome ... epic)] [00.8.3 clock sizes] [DL-11-16]
```

**11.5.4 Progress.** `[D]` + `[J:flag]` A thread's progress clock ticks only from its listed sources
(00.8.2):
- a resolved beat that **serves** the thread → **delivered reach** (0–4). `[J:flag]` *"Does this beat's
  intent move the thread's named obstacle?"* True only when the beat's intent, if it succeeds, changes a
  fact about the obstacle, its holder, its place or its clue graph; false for beats that merely happen
  near it. Uncertain → false. *Worst case (J):* one beat's reach ticked wrongly, logged with its frame id
  (class i);
- a **core clue** of its case found (15.9) → 1;
- a **milestone** → 2: a necessary node of its case reached, a step of its situation prevented, its
  opposing clock voided, an officer or linchpin of the `against` party removed;
- `random_event` → 1 (12.6.5; never to completion: a random event cannot fill the last segment);
- for a vow racing a countdown (07.5.5) or a case's opposition clock (15.9.13), the racing rule decides.
**Flashpoints.** When the clock first reaches half and when it first reaches imminent (remaining ≤
max(1, size ÷ 4)), the trigger `trg.11.flashpoint` is raised: the next scene chapter 12 frames for this
thread must unseal the next sealed fact of its case's path or bring its `against` party onto the stage
(a bang, specificity `npc` or `faction`) — Mythic's flashpoints, which make long matters turn rather
than drift [R5 P-08; DL-11-16]. A thread completes when its last clock fills.

**11.5.5 The lifecycle.** `[D]` Every thread ends. Statuses, and what moves a thread into each:

| Status | Enters when | Writes |
|---|---|---|
| **seeded** | a hook is made (11.5.6) | text available to the player once it reaches them (a rumor, a person, a letter) |
| **active** | the PC takes it up: says so, accepts the job or vow, or a beat serves it | clue placements, fallback and rank written if not yet; progress clock public; weight 2 |
| **stalled** | the live-lead audit finds no live lead (12.8.4) | the fallback bang queued to fire at the next `scene_start` |
| **completed** | the progress clock fills | `thread_completed` event (01.16.2: fate +1, if the PC pursued it); `vow_kept` if a vow; reward facts (`gift_due.<patron>` when one was promised); status steps (T-11-3); a chronicle line (formidable and higher, or any vow); 04 may read it as a crisis or reflection moment |
| **failed** | its opposing clock completes; its situation concludes without the PC; or a fact makes it impossible (the heir is dead) | the opposing clock's `on_complete`; news; a chronicle line if formidable or higher; the thread's patron's status −1 only if the PC had accepted it from them |
| **expired** | a seeded hook untaken for **8 weeks**; or an active quest or situation thread with no progress for **13 weeks** (a season) that is not protected (12.6.5) and is not a vow | its rumors turn `outdated`; the world settles it off-screen by its situation's timeline or its patron's `if_unmet` (someone else took the job); news |
| **abandoned** | the player declares it closed; a drive rewritten (02.9.1) closes the long vow | only the costs its source states: 07.5.5's forfeit, 16.12.4's grievance, an oath's strain (04); nothing else |
| **retired** | at a Season Turn, every entity it needs is gone (patron dead with no heir, object destroyed) and it is not a vow; or the register is over its cap (11.5.9) | a one-line news item; no cost |
| **bequeathed** | at retirement, passed to the successor (11.13.4) | the progress halved (rounded down) onto a new thread owned by the successor |

So a hook dangles at most eight weeks, a quest nobody pursues settles itself within a season, and the
only threads that wait forever are the vows the player swore. This is R1's hook lifecycle applied to the
register: the "abandoned plot element" error has no state in which to exist [R1 #10; R4 W11; C:VI;
DL-11-12].

**11.5.6 Hooks.** `[D]` + `[J:flag]` A **hook** is a thread at status `seeded`. Making one writes the
thread record and its text; **activating** it writes the rest:
1. **Bind** its entities, reusing first: the people, places and factions it names are bound to existing
   entities when any fits (`[J:flag]` *"Does an existing entity of this kind satisfy the hook's text?"*;
   uncertain → yes if the entity is within the region and not dead or departed), else created
   (12.11.1 for NPCs; 10 for places; 11.3.18 for factions) [R1 11 "improvise, write it down, bring it
   back"; R4 W10]. *Worst case (J):* a reused NPC fits less well than a new one would: a written fact the
   world keeps (class iv).
2. **Graph:** a case of chapter 15's shape is generated (PR-15-6) with at least **three clue placements**
   per necessary conclusion, of at least **two holder kinds** (person, place, object, rumor), one of them a
   **core** placement delivered without a roll, and the reserve and fallbacks 15.9 requires
   [R6 B-13; R5 P-41; 12's request d].
3. **Rank** (11.5.3), **opposing clock** if its source has a threat (a situation's next step, a faction's
   goal, a monster's hunt), **reward** if a patron promised one, and **fallback** (11.5.7).
Creation hooks (02.9.7) are consumed by kind: `thread` → a seeded hook shown to the player at once (the
long vow is activated at once as a vow); `rumor` → a rumor (11.6) pointing to a placement of a new hook;
`npc` → bound to the bond NPC, who becomes the hook's first placement; `place` → a place hook whose
first placement is the place; `debt` → a commitment of kind debt with a creditor, and a quest thread;
`enemy` → a faction tie at −2 (11.3) or an NPC enemy, and a situation from template `the_enemy`;
`question` → a sealed fact with a case. A lost bond's sealed fate (02.9.2) is kept sealed with its gate
as a clue of the case it belongs to.

**11.5.7 Fallbacks.** `[T]` + `[D]` Every thread holds at least one **fallback**, a proactive node that
comes to the PC [R6 B-13; R5 P-41]: `{trigger, form, delivers}`. Triggers (closed): the thread becomes
`stalled` (12.8.4); its opposing clock reaches a named fill; or **three** consecutive scenes in which the
PC pursued the thread (it was the scene's agenda) and its progress clock did not tick. Handler
`h.11.fallback_counters` (`scene_end`, phase 6) keeps the counter and also counts chapter 15's case
fallbacks (15.9.12) and chapter 16's personal-thread fallbacks (16.12.1), firing them from their own data.
Firing queues the fallback as a bang (kind `fallback`, specificity `npc` or `faction`), which chapter 12
fires at the next `scene_start` (12.8.4); it **delivers** one core placement of an unfound necessary node,
in the world as it fires (the witness arrives knowing it). A thread may fire fallbacks repeatedly; once
no unfound necessary node remains, its fallback form is a confrontation with its `against` party.
`form` comes from the source's data or `tbl.11.fallback_form` (d8: a witness seeks the PC out; the
opposition acts and leaves evidence; a new victim; a messenger with a demand; the patron's impatience;
an object turns up; a rival claims the prize; a rumor sharpens) [DL-11-17].

**11.5.8 Register upkeep.** `[D]` World Turn step 8, for every thread: expire what 11.5.5 expires; mark
stalled and queue the fallback for any active thread with no live lead (repeating 12.8.4's scene-end audit
at the week, for weeks spent off-screen); check opposing clocks that phase 5 ticked; update
`protected_until`; and reduce by one the weight of every thread not featured in six scenes (12.6.6).

**11.5.9 Caps.** `[D]` At most **twelve** threads active or stalled; at most **eight** seeded hooks known
to the PC (beyond that, the oldest seeded hook expires early); at most one personal thread per ally. When
an activation would make thirteen active threads, the player chooses one non-vow thread to set aside
(it becomes `retired`, its progress kept on the record, and may be taken up again as a new hook); vows
are never set aside by the cap. These caps keep the register a list the player can hold, which the
sandbox would otherwise grow without end [C:VI; C:P3 (player-facing state)].

**11.5.10 The hook supply rule.** `[D]` At World Turn step 8, if the PC knows of fewer than **three**
open matters (seeded hooks the PC has heard of, plus active or stalled threads that are not vows), the
engine makes one hook from the first source of this ladder that yields one, and delivers it as a trace
(a rumor that reaches the PC's settlement, a person who comes looking, a letter):
1. the PC's own: an unfulfilled drive with no thread, an aspiration, an open bond, a thorn (02.9);
2. an ally's personal thread not yet open (16.12.2: its fallback is the delivery);
3. a faction whose status toward the PC is not 0 (its next goal step, a job at +1 or better, a threat
   at −1 or worse);
4. an active situation of the region the PC does not yet know of (its next step's trace);
5. `tbl.11.hook` for the region (a d20 of generic seeds by terrain and settlement tier; a region's seed or a
   pre-made setting may override it [verification: V2b-013]).
In the simulation the PC knew of at least three open matters in 100 of 104 weeks and never of more
than ten (T-11-24): a steady stream with no flood [R6 B-R4; R5 P-07; DL-11-17].

**11.5.11 What finishing earns.** `[D]` A completed thread earns, and only earns: fate +1 (01.16.2;
+1 more if it was a vow); the status steps of T-11-3; the reward its patron promised (`gift_due`, coin
from the patron's means at 08's wage scale, a rank at the next sitting); the reputation that its deeds
earned on the way (11.7, through witnesses, not through the completion itself); a chronicle line; a
Deeds-ledger entry for legacy (11.13.5). It never grants a license, a tier or an ability (INV-7):
chapter 04 may treat the completing beat as a crisis or the next reflection as its moment, as 04
rules [R5 AD-06; 04.6].

**11.5.12 Other chapters' threads.** `[D]` Threads created by other chapters use this register with these
defaults (data: `world_turn.yaml#thread_sources`):

| Source | Kind | Rank default | Opposing clock | Fallback |
|---|---|---|---|---|
| creation's long vow (02.9.1) | vow | formidable | none | a person from the PC's past |
| restitution (04.9.4) | quest | dangerous | none | the wronged party's kin seek the PC out |
| the Bargain's debt (07.5.5) | vow | as the ask | `clk.deaths_debt` (countdown 8, +1 a week) | the curse's next stage shows itself |
| a dread obsession (07.11) | quest | dangerous | none (dread +1 a week unpursued is 07's) | the haunt's object appears |
| an ally's personal thread (16.12) | quest | dangerous | per its want (a creditor's clock, a rival's) | a person from the ally's past (16.12.1) |
| a vow at an ally's death (16.9.5) | vow | dangerous | none | the dead ally's kin or killer |
| a rite's condition, a spirit's bargain (05) | quest | troublesome or dangerous | the rite's window if it has one | the spirit's reminder |
| a case (15.9) | quest | by the case | the case's opposition clock (15.9.13) | the case's fallbacks (15.9.12) |
| a faction's commission | quest | by the job | the rival faction's goal clock when it races | the patron's impatience |
| a cache to recover (07.6.4) | quest | troublesome | `clk.cache` (6, +1 a week) | a cache rumor sharpens (11.6) |
| a bequest (11.13.4) | as the original | as the original | as the original, advanced by the timeskip | as the original |

### 11.6 Rumors, news and how information travels

**11.6.1 The rumor record.** `[S]` + `[D]` A **rumor** is a claim in circulation whose truth was fixed when
it was born and is never changed to suit play — Forbidden Lands' legends with a truth the GM sets
privately [R6 B-04, B-R6; 00.6.2]:

```yaml
Rumor (entity kind rumor):
  id: rum.*
  text_seed: str               # the claim as carried, built by 11.6.3 (the DM words it)
  about: id | fact_id          # the entity or fact it concerns
  source: eyewitness | hearsay | boast | official | planted | legend | trace
  truth: true | partial | false | outdated     # SEALED; fixed at birth except true/partial -> outdated
  distortion: {field: who | where | when | how_many | why, form: str} | null   # for partial and false
  points_to: placement | node | place | npc    # always an existing target (11.6.4)
  origin: settlement scope
  reached: [scope]             # where it circulates now
  born_at: time
  status: circulating | faded
  lifecycle: provisional
```

**11.6.2 Traces: every change of consequence is perceivable.** `[D]` A **consequential change** is any
write this chapter makes that changes who holds what (a hold, a place, a seat, a rank), who stands where
(a relation, a status, war), what is true of a place (safe, danger rating, owner, a new building, a
plague), or who lives (a linchpin, an officer, a named NPC), and every completed goal or situation step.
Each emits **at least one trace**, by T-11-10, in the World Turn's step 7 or at once if it happened in
play. A trace is one of four things (closed list): **news** (true, public: 11.6.6), a **rumor** (truth
by 11.6.3), a **visible change** (a fact on a place the PC could see: a banner on the gate, a burned
mill, a new toll, a price), or an **omen** (for a hidden clock's tick, INV-14). Tynan Sylvester's rule
made a rule: simulation the player cannot perceive is wasted, so there is none here [R6 B-20;
DL-11-10].

**T-11-10 Traces by change** (canonical: `world_turn.yaml#traces`).

| Change | Trace(s) |
|---|---|
| a hidden or sensed goal clock ticks | one omen of its stage (INV-14), visible where the faction acts |
| a faction goal completes | news in its seat; a rumor (`official`) wherever it acts; a visible change named by the goal's effects |
| a strike succeeds | a rumor (`eyewitness`) in both seats; a visible change at the struck place |
| a hold or place changes hands; a collapse; war declared or ended | news in the region; a visible change at the place |
| a situation step fires | its own `trace` as news in its place and a rumor (`hearsay`) one step beyond |
| a linchpin's fate | news in the faction's seat; a rumor (`hearsay`) in the region |
| a noteworthy `public_deed` of the PC | a rumor (`eyewitness`) in each carrier scope (reputation is 11.7's) |
| a recognition staged before witnesses (04.6.3 item 6) | a rumor (`eyewitness`) in each scope of its witnesses |
| `victory_over_pc` | a rumor (`boast` if the victor's Nemesis result is `nem.boast`, else `eyewitness`) in the victor's scope |
| the belief `pc.dead` (07.5.6) | a rumor, truth `false`, `official`, in the victor's faction scope and seat |
| a cache's clock ticks or disperses (07.6.4) | a rumor (`hearsay`, true) pointing to the cache's place, or to its named holder |
| a seasonal phenomenon begins (11.11.4) | news in the region |
| a world change of a great project (11.9.7) [verification: V2b-013] | news in its scope; a visible change |

**11.6.3 How truth is fixed.** `[D]` + `[N]` At birth the engine rolls `tbl.11.rumor_truth` (d10 by
source; `world_turn.yaml`), then, for a `partial` or `false` result, `tbl.11.distortion` (d6) for what is
wrong:

| Source | true | partial | false |
|---|---|---|---|
| eyewitness (someone saw it) | 1–6 | 7–9 | 10 |
| official (a faction's own word) | 1–5 | 6–9 | 10 |
| hearsay (carried past its first scope) | 1–4 | 5–7 | 8–10 |
| boast (a victor's or rival's telling) | 1–2 | 3–7 | 8–10 |
| legend (11.13.3; old tales) | 1–3 | 4–7 | 8–10 |
| planted (a deception, 11.6.9) | — | 9–10 | 1–8 |
| trace (an omen's rumor; a cache's) | 1–10 | — | — |

Distortion (d6): 1 **who** (the deed is credited to someone else, or the victim is wrong); 2 **where**; 3
**when** (a month ago, or "tonight"); 4 **how many** (doubled or halved); 5 **why** (a motive is
invented); 6 **what** (the deed is inverted: rescued becomes kidnapped). A `partial` rumor carries one
distortion; a `false` one carries one distortion of form 1 or 6 (re-roll others), or is a plain
falsehood if it was planted. The DM words the rumor from its `text_seed` and its distortion `[N]`, and
may not add a second distortion or correct it. **Outdated:** when the fact a rumor is about is superseded
(a `set_fact` with `supersedes`), a `true` or `partial` rumor's truth becomes `outdated` (it was so once);
nothing else ever changes a rumor's truth [R6 B-04, B-R6; R4 W7 (secrets kept as committed state);
DL-11-11].

**11.6.4 Every rumor points somewhere real.** `[D]` A rumor's `points_to` is an existing placement, case
node, place or NPC where its claim can be tested: a `true` rumor points to a placement that confirms it; a
`partial` one to a placement that confirms the true part and shows the changed detail; a `false` one to a
placement that **refutes** it (15.9.18: "a false rumor still leads somewhere real"); an `outdated` one to the
place where the change can be seen. If no target exists, one is written (a placement in the case, an NPC
by 12.11.1) before the rumor is created; a rumor with nowhere to lead is never made. So every rumor is a
lead (15.9.8; P16), and the player who follows a lie learns something true [R5 P-41; 12's request e].

**11.6.5 How information travels.** `[D]` News and rumors spread at World Turn step 7 by scope steps
(11.1.3), along route links that are open (a closed road or a quarantined town stops spread along it):

**T-11-12 Spread** (canonical: `world_turn.yaml#spread`).

| From → to | Takes | Condition |
|---|---|---|
| its origin settlement → each neighbor settlement | 1 World Turn | a route link open between them |
| settlements → the region | 2 World Turns after it is in two settlements of the region, or 1 if it is in the region's largest settlement | — |
| the region → the realm | 4 World Turns after it reached the region | only news, rumors of a tier-3 or higher faction, war, a collapse, a linchpin, or the PC's deeds once the PC's reputation in the region is 4 or more |
| beyond **two** steps from its origin | a rumor arrives as a **new** rumor, source `hearsay`, with its truth rolled again and never truer than the original (a false original stays false) | — |
| spreading stops | 8 weeks after birth, or 4 steps from the origin | then it **fades** 8 weeks later (`status: faded`: no longer drawn; kept in state) |

This is how far news travels in a world of roads and carts: a town knows by next week, the region by the
end of the month, the realm in a season, and a tale told three towns away is someone else's tale
[R6 A-15 (scopes by social distance); DL-11-11].

**11.6.6 News.** `[D]` **News** is a true public change, spread like a rumor but always true, written as a
fact with `certainty: established` in each scope it reaches. The PC hears news on **arriving** in a
settlement scope it has reached — at most three items, most recent first, in the arrival narration, the
rest available by asking — and by every means that hears rumors. An NPC knows the news of its home scope
(12.10.6 c).

**11.6.7 Hearing rumors.** `[D]` The PC hears rumors by: Ask around (15.13.9: those about the named
subject in the settlement); Carouse (15.13.8); a tavern the PC owns (one per week, the newest in its
scope, 08.8.8); an NPC at Warm or better who knows one and is asked (12.10.6); a rumor table roll that
another rule calls for (`roll_table(tbl.11.rumors, {scope})` draws among the rumors circulating in the
scope, weighted 3 for born in the last two weeks, 2 for the last month, 1 otherwise, with recency). Each
hearing writes `record_knowledge(pc, rumor, how: heard)` and the journal shows its text, never its truth
(15.9.18). NPCs in a scope know its circulating rumors when their role hears talk (innkeepers, guards,
merchants, priests, carters: always; anyone else: the Oracle, Even) (12.10.6 c).

**11.6.8 Rumors about the PC, and the PC thought dead.** `[D]` Every noteworthy deed the PC does before
carriers seeds a rumor (T-11-10) whose `about` is the PC (or the persona, 03's `as_identity`); this is the
"word on the street" that reputation (11.7) scores. The belief **`pc.dead`** (07.5.6) is a rumor, truth
`false`, born in the victor's faction scope. While it circulates in a faction's seat, that faction's
attention clock on the PC is **paused** and its `move_on_pc` rows read as `goal`; the moment a carrier of
that faction perceives the PC alive (an aftermath link, 03.10.3), news "alive" is born in its seat and
its attention clock ticks **+2** (they were wrong, and now they are paying attention). Being thought
dead is a situation with uses of its own, exactly as 07 intends [07.5.6].

**11.6.9 Rumors the PC starts.** `[D]` A PC may plant a rumor with a Talk beat (deceive or inform) in a
settlement (15.5), or Carouse to spread one. Success writes a rumor with source `planted` (truth from
the facts: `false` if what it says is not so, `true` if it is) and the PC's beat's delivered reach as the
number of settlements it starts in (1–4, the scene's settlement first, then its neighbors). It then spreads
by 11.6.5. A world reaction (`wr.rumor_believed`) lets a faction act on a rumor about its rival once it
reaches its seat, as if it were known (a planted lie can start a feud). Lies so planted are recorded lies
(15.5), with their truth-out clocks.

### 11.7 Reputation: what the world says

**11.7.1 The reputation entry.** `[D]` Reputation is Ars Magica's triple — *content*, *scope*, *score* —
kept separate from recognition (capability is chapter 04's; 00.17.1 Q22) and fed only by witnessed
deeds [R6 A-15, R-A3; 03.10]:

```yaml
ReputationEntry (fact on the PC or a persona):
  id: rep.*
  actor: pc.* | persona id     # 03's as_identity: a disguise earns its own name
  key: deed branch (deed.*) | conduct axis and pole (conduct.*:+|-) | defeat | scandal
  content: str                 # what is said: a deed line, the most striking so far ("held the ford
                               # while the carters crossed")
  scope: settlement | region | realm | fac.*
  points: int                  # 11.7.3
  score: 0..5                  # from points
  epithet: str | null          # 11.7.5
  sources: [event id]          # every packet, event or fact that added to it
  last_point_at: time
  visibility: content and scope available; points and score background (00.6.3)
  lifecycle: provisional
```

**11.7.2 Sources (closed list).** `[D]` Only these add to reputation:
1. **`public_deed` packets** (03.10.5): one per scope in the packet's `scopes`.
2. **`recognition_event`s** with witnesses (04.7.8): a grant, an accepted offer, a confirmation or a tier
   staged before carriers adds to the calling's deed-branch key in each witness scope; a `fraying_stage`,
   `revocation` or `turn` before witnesses, and every one in the keeper's or institution's scope, adds to
   the conduct key of the oath's broken axis (the world remembers an oath broken); an `atonement` adds to
   its positive pole in the keeper's scope.
3. **Defeats** (07.6.2): the reputation packet of a defeat adds to key `defeat` in its witnesses' scopes
   (content: "beaten by the Guild's riders at Sedge Mill").
4. **Exposure at S5** (01.13.6): the exposed deed and identity add 2 points to key `scandal` (or the deed's
   own key if it is no crime) in the observer's faction scope and settlement.
5. **Chapter 15's social records**: an exposed lie, a broken obligation or agreement, a wrong accusation,
   each adds to the conduct key `conduct.honesty:-` (or `conduct.loyalty:-` for a broken obligation) in the
   scope of those who learned it; a week of service at a faith (15.13.12) adds to `conduct.piety:+` in the
   faith's scope.
6. **Chapter 16's retinue record**: an ally's departure in grievance adds to `conduct.loyalty:-` and one in
   contentment or a completed personal thread to `conduct.loyalty:+`, in the ally's home scope — "how the PC
   treats their people" (16.11.3).
7. **World changes** of great projects (T-11-17): their stated reputation writes.
Nothing else does: not a claim, not a boast by the PC, not a deed no carrier saw (03.10) [DL-11-15].

**11.7.3 Keys, content and points.** `[D]` A packet joins the entry with the same **key** in the same
scope, or makes one. Its key is: the conduct axis and pole of its strongest conduct entry when that
entry's magnitude is 2 or more (a values-expressive deed is remembered for its values); else the
packet's deed **branch** (`deed.martial`, `deed.influence`…). Points: a **noteworthy** packet (03's
definition: a difficult, risky success or better, or a conduct entry of magnitude 4) adds **1 point**;
three carried packets that are not noteworthy add 1 point between them (a counter per entry); a
`recognition_event` adds 1 point; exposure at S5 adds 2. The entry's `content` is the deed line of its
first noteworthy packet, replaced by a later one only if that one's challenge band is higher.

**Score** from points (Ars Magica's slow, skill-like growth [R6 A-15]): score 1 at 1 point, 2 at 3, 3 at
6, 4 at 10, 5 at 15. So one noteworthy deed makes a name known in a village; six on the same matter make
the PC talked of there; fifteen make a legend of the place. *Arithmetic:* a PC whose play centers on one
branch and who does one or two noteworthy deeds per session before carriers of one town reaches score 3
there in four to six sessions and 5 in ten to fifteen (03's calibration: noteworthy events are the
difficult, risky successes, about one in four evidence events).

**11.7.4 How far a name travels.** `[D]` At each Season Turn (11.11.3 step 6 [verification: V2b-013]): every settlement entry of
score 3 or more gives its **region** an entry of the same key at `score − 2` (if higher than the region's
own); every region entry of score 4 or more gives the **realm** one at `score − 2`; faction-scope entries
do not spread (they are what members say among themselves). Spreading is by points: the derived entry
takes the points of its derived score. Rumors carry the words (11.6.8); reputation carries the weight.

**11.7.5 Epithets.** `[D]` + `[N]` When an entry first has score 2 or more **and** at least two noteworthy
packets on its key in its scope, the community coins an **epithet** (the saga byname: conferred, not
chosen, often unflattering, anchored in an incident [R6 A-19; R: https://journals.lub.lu.se/index.php/anf/article/viewFile/11525/10217]).
The engine rolls its form on `tbl.11.epithet_forms` (d8: "the <noun of the deed>" — the Ford-Warden;
"<place>'s <noun>" — Ashford's Arrow; a kenning "<adjective>-<noun>" — Quiet-Match; "the one who <did
it>" — the one who held the ford; "<name> <byname>" — Wren Two-Fires; a mocking form for a negative valence
— Wren Run-Away; "<name> of <place>"; the community's own word for what they fear or love), and the DM fills
it from the entry's content `[N]`. Rules for the words: it names **what was done**, never a calling's name
or any rules term (04.6.3 item 2; T-00-22); it uses only nouns the deed line or the place supplies; one
epithet per entry; the PC is called by at most **three** at once (the three highest-scoring entries'), and
the others sleep until an entry overtakes them. The fact `pc.epithet.<scope> = <words>` is written; V1's
staging (04.6) is chapter 04's, and its words are these. The player may embrace or resent a name; they
cannot un-earn it [R6 A-18, A-19; DL-11-15].

**11.7.6 Valence: the same deed, praised and damned.** `[D]` An entry's **valence** in a scope is computed,
never judged: the scope's **values** are the values of the faction whose seat is that settlement (or the
faction itself for a faction scope; the region's dominant faction or the seed's regional values (12.16.10) for a
region). Valence is **admired** (+) when the key is a pole those values admire or a deed branch among that
faction's `patron_deeds`; **despised** (−) when the key is a pole they despise, or `defeat`, or `scandal`;
**neutral** otherwise (renown without judgment). So "the one who burned the Guild's pens" is a hero in
the Wardens' village and a murderer in the Guild's town, as the modern Fable makes reputation plural
[R6 A-18]. The narrator receives each entry's content, epithet and a **tone band** by score — 1 "a few have
heard", 2 "known here", 3 "talked of", 4 "famous here", 5 "a legend here" — and its valence word
(admired / feared / despised / spoken of), never a number.

**11.7.7 What reputation does (closed list).** `[D]`
1. **First impressions** (12.11.2): an NPC whose scope holds an entry of score 2 or more about the PC
   takes +1 on its reaction roll if that entry's valence there is admired, −1 if despised (the strongest
   entry of the scope decides).
2. **It precedes the PC** (Forbidden Lands, made deterministic [R6 A-16]): arriving in a settlement, every
   NPC whose role hears talk knows the PC's entries of score 2 or more there; at score 1, a given NPC knows
   by the Oracle, Even (12.10.6 c).
3. **A citable fact:** an entry of score 3 or more in the scene's scope is an established fact the PC may
   cite as a lever (00.3.9) when the method uses it (an intimidation by the Wolf of Harl's Crossing; a plea
   by the one who held the ford), typed by 00.3.9's test.
4. **Institutions** hear it: `institutions_matching` reports `heard` from it (11.8.1); rank criteria read
   it (11.8.2).
5. **Status** reads it: deeds a faction's values admire or despise move status (T-11-3).
6. **Great projects** read it: an entry of score 3 or more in the project's scope is an Amplifying lever on
   its weekly beat (11.9.7 [verification: V2b-013]).
7. **Legacy** reads it: renown, breadth and legend rank (11.7.10; 11.13.3).
Reputation never changes a DC, a defense, a tally, a tier or a license [00.17.1 Q22].

**11.7.8 Personas.** `[D]` Deeds done under a persona (03's `as_identity`) build the persona's entries,
not the PC's. An **unmasking** (an aftermath link, 03.10.3, tying the persona to the PC in a scope) moves
the persona's entries in that scope onto the PC, adding points key by key; elsewhere the persona keeps
its name until unmasked there too.

**11.7.9 Fading and folding (VI).** `[D]` At each Season Turn: an entry that gained no point for four
seasons loses one score (its points drop to the threshold of the lower score), unless its score is 4 or 5
(legends stick); and no scope holds more than **three** entries for one actor — when a fourth would form,
it **folds** into the entry of that scope with the same valence and the lowest score (points added; the
higher-challenge content kept). Nothing is deleted; the sources list keeps every packet. Reputation grows
by consolidating, as Principle VI requires of every growing record [C:VI; DL-11-15].

**11.7.10 Renown.** `[D]` `renown(pc)` = the highest score of any of the PC's entries; `breadth(pc)` = the
number of scopes in which the PC has an entry of score 2 or more. Legend rank (11.13.3), inheritance
(11.13.5), great projects and the hook supply read them.

### 11.8 Institutions and ranks

**11.8.1 `institutions_matching(deed_branch, region)`.** `[D]` The interface chapter 04 calls for V3 and V9
(00.17.1 Q4; 04.6). It returns a list, ordered by status toward the PC (highest first), then tier, then id,
of every non-collapsed faction with its seat or a hold in the region whose `patron_deeds` match the branch
(00.5.4 ancestor match, in either direction):

```yaml
- faction_id: fac.*
  status_to_pc: -3..+3
  has_ranks: bool              # it has a rank ladder with a rung the PC could hold
  next_sitting: time           # the next date its ranks are conferred (11.8.3)
  heard: bool                  # public(pc, branch, faction scope or seat) > 0, or a reputation entry
                               # of score >= 1 on that branch in its seat or scope
  teachers: [npc.*]            # its officers and members holding a training license of the branch at
                               # expert or master (15.11; 15's request)
```

Chapter 04 applies its own filters (V3: status ≥ 0 and `heard`). This chapter never grants capability;
it seats, obliges and rewards [04.11; DL-11-18].

**11.8.2 Rank ladders.** `[D]` A rank is a **seat** in an institution: social standing, resources and
obligations, never capability (04.11.1). Each template with ranks carries a ladder of five rungs
(`factions.yaml#rank_ladders`; names per template — a guild's apprentice, journeyman, master, warden,
guildmaster; an order's novice, brother, knight, commander, grand master):

| Rung | Seats | Requires (all) |
|---|---|---|
| 1 associate | unlimited | status ≥ +1, or an accepted V3 offer |
| 2 sworn | unlimited | status ≥ +1; a reputation entry of score ≥ 1 in its scope or seat on a key it honors; one season at rung 1 with every obligation kept |
| 3 officer | `tier + 1` | status ≥ +2; such an entry of score ≥ 2; a seat free (or won, 11.8.6); conferred at a sitting |
| 4 high officer | `1 + tier ÷ 2` (round down) | status ≥ +2; score ≥ 3; a seat free or won; a sitting |
| 5 head | 1 | status +3; score ≥ 4; the head's seat empty (a linchpin fate, a retirement, a death) or won |

**11.8.3 Sittings and offers.** `[D]` Ranks are conferred at the faction's **sittings** (its `sittings`;
default the first week of each season; the region's seed names festivals, 12.16.15). `next_sitting` is the first sitting
after now. Rung 1 may be given at any time by an accepted offer. A rank is offered through chapter 04's
protocol (V3 the order seeks you out; V9 the rite or trial; 04.7), or, for rungs 2–5, at a sitting when its
requirements hold (a sitting offer, institutional, with the price `obligation`). A trial decides only when
the rank is given (04.11.2). An offer not answered expires at the next sitting after next.

**11.8.4 What a rank gives (closed list).** `[D]`
1. **A title** the fiction uses (the rung's name in the template).
2. **Access:** from rung 2 its holds are havens to the PC (`safe: true` for the PC) and its stores sell at
   list price with no haggling needed; from rung 1 its mentors teach (15.11) and from rung 2 without fee.
3. **Followers** (16's request d): rung 3 brings 2 followers, rung 4 brings 4, rung 5 brings 6, from its
   rank and file at its band, inside the PC's retinue cap (16.3.6); they serve as chapter 16's followers
   and leave if the rank is lost.
4. **Means:** rung 3 pays the PC's `modest` lifestyle while in its seat; rung 4 `comfortable`; rung 5
   `wealthy`, or `noble` for a tier-4+ crown faction (economy.yaml: noble is expected of crown rung 2+, so a
   crown faction's rung 2 pays `comfortable`).
5. **Authority:** the PC's requests of the faction's members on its business count one request rung lower
   (15.3.2), within their ceilings.
6. **A gift** at each promotion to rung 3, 4 or 5: `gift_due.<faction>` with circumstance `earned` (08.7.2).
7. **Standing:** the first rank is +1 status (T-11-3).
Nothing else: no license, no competence, no tier (04.11.3).

**11.8.5 Obligations.** `[D]` Every rank carries its template's **obligations**, written as commitments of
kind obligation when the rank is accepted (the price `obligation`, 04.7.5): (a) its **duty**, as an
officer's (11.3.17), held as a refusal the PC has promised to keep; (b) **service**, from rung 2: one week
per season of downtime in its cause (15.13.12's service, or the template's), and answering a **muster** when
the faction is at war (a bang the PC must answer within two weeks); (c) its **values**: a noteworthy deed on
a pole the faction despises, done in its scope, is a broken obligation. `h.15.commitments_due` tests them;
the Season Turn sums them: every obligation kept that season → +1 status (small); one broken → −1 status
and a warning from an officer; two seasons in a row with one broken → the rank falls one rung.

**11.8.6 Seats, contests and loss.** `[D]` Seat-limited rungs (3–5) are held by NPCs too, by name. A
seat is freed by its holder's death, departure, retirement, promotion or a linchpin fate. A PC who meets
every requirement but the free seat may **contest** an occupied seat through the template's challenge
(a V9 trial against the holder: a duel, a debate, a test of craft — AD&D's druid and monk seats [R6 A-22]);
losing the contest never costs capability and the PC may contest again after a season. A rank is
**lost** by: two seasons of broken obligations (one rung); status falling below +1 (rungs 2–5 are
suspended until it recovers) or below 0 (all ranks lost); a linchpin fate that expels; `tbl.twist_s5` row
4 ("a patron withdraws support": the privileges of 11.8.4 are suspended for one season). **A newly
granted rank is provisional for its first season** and is confirmed at the Season Turn if no obligation
was broken, else it lapses back one rung (VI at the scale of a character's seats; an extrapolation from
PoE leagues recorded as such, BRIEF A3) [C:VI; 04.11.1; DL-11-18].

### 11.9 Holdings, great projects, gifts and rulership

**11.9.1 The holding record.** `[D]` A **holding** is a place the PC owns, priced by chapter 08
(`economy.yaml#holdings`: cottage 150 … keep 25,000; build weeks, weekly upkeep and staff alongside) and
run as play by this chapter (08's request) [R5 EQ-12, LW-09, LW-10; R6 B-04 (strongholds)]:

```yaml
Holding (record on a place entity):
  place: loc.*
  type: hold.cottage | hold.townhouse | hold.workshop | hold.shop | hold.tavern | hold.farmstead
        | hold.watchtower | hold.manor | hold.keep
  owner: pc.* | fac.* | npc.*
  acquired: bought | built | granted | inherited | seized
  steward: npc.* | null        # who runs it when the PC does not
  staff: int                   # 08's staff count, paid by 08's upkeep
  garrison: 0..3               # 0 none; 1 watchtower or walls; 2 manor or walls + garrison; 3 keep
  damage: clk.11.damage.<id>   # 6 segments, public; complete -> ruined (or seized, 11.9.5)
  improvements: [imp.*]        # 11.9.6
  safe: bool                   # a haven (10.2.3) while held, staffed and not ruined
  lifecycle: provisional
```

**11.9.2 Getting one.** `[D]` A holding is acquired by: **buying** (08's price and a charter, `bi.charter`,
from the faction that holds the settlement's seat, which sells it at status ≥ 0; whether one is for sale
is an Oracle question, Likely in a town or city, Unlikely in a village); **building** (chapter 15's
project, 15.12, on 08's build weeks, the price paid as materials over the build); **grant** (a rank's
privilege, a thread's reward); **inheritance** (11.13.5); or **seizure** (taking a faction's hold by force,
which is a `strike` the PC makes in play: status −2 with that faction and the place's ownership written).
The holding is a **haven** for the PC (`safe: true`, 10.2.3) while it is held, staffed as 08 requires and not
ruined; while the PC lives there, 08's lifestyle line applies.

**11.9.3 Holdings in the World Turn.** `[D]` In step 2 (Maintain), for each holding: (1) 08's upkeep has
already run in phase 4; if it went unpaid, the damage clock ticks +1 and, after two unpaid weeks, the staff
leave (as hirelings do, 16); (2) the **yield** is rolled (11.9.4); (3) threats against it resolve (11.9.5);
(4) a steward with no master's visit for a season (no `managed_this_week` in 13 weeks) rolls the yield with
a snag (−2): absentee ownership costs.

**11.9.4 The yield.** `[D]` A holding with a yield (08: workshop, shop, tavern, farmstead, manor, keep) makes
one **stewardship check** per week: `d20 + the steward's modifier`, +2 as a Precision lever when
`managed_this_week` is set (15.13.11: a day of the PC's oversight), against **Moderate (15)**, or **Hard
(20)** while a situation or a Hostile faction's attention is active in its settlement. The steward's
modifier is a hired steward's +3 (a skilled hand, 08.8.8), a specialist's +5, an ally's own (Presence and
its competence on `deed.influence.trade`, 16), or the PC's own base modifier on `deed.influence.trade` when
the PC managed it that week, whichever is best. The degree says how 08's yield dice are read:

| Degree | Yield |
|---|---|
| critical success | the higher of two rolls of 08's yield dice |
| success | one roll of 08's yield dice |
| failure | the lower of two rolls |
| critical failure | nothing; and a **trouble** bang (social, intensity 1, specificity `npc`: theft by a servant, a brawl, a dispute over a boundary, a fire threatened) |

Yields are gross, before 08's wages and upkeep; they never exceed labor and rents (08's anti-inflation
rule AI-6): a holding is a living, never a mint. A tavern also gives its owner the newest rumor in its scope
each week (11.6.7); a farmstead gives supply in season (08). *Arithmetic:* a hired steward (+3) succeeds
45% and fails critically 10%; with the PC's day of oversight (+5) 55%, critically failing 5% [08.8.8;
15.13.11; DL-11-19].

**11.9.5 Threats to holdings.** `[D]` A holding can be struck: by a Hostile faction (11.3.8 lets its
`strike` target the PC's holdings), by a situation step that names its place, by an entanglement's
reprisal, by `tbl.twist_s5` row 2 (a haven falls). A faction's strike on a holding is a faction check
against `10 + 2 × garrison + 2 × the PC's domain tier (11.9.8; 0 if none)`, +2 with walls: success ticks the
damage clock +2, critical success +4. A completed damage clock **ruins** the holding (no yield, `safe:
false`; repair is a project of half its build weeks) or, for a manor or keep struck by a faction whose
`fields` could hold it, **seizes** it (ownership passes; status −1 more; a thread to retake it is seeded).
`aid_pc` of a friendly faction sends help when a threat bang names the holding (11.3.6). A week of repair
(15.13.11) ticks the damage clock down 2.

**11.9.6 Improvements.** `[D]` A holding may carry improvements from this closed list
(`world_turn.yaml#improvements`; price, build weeks, effect, minimum holding): **walls** (400, 8 weeks;
garrison +1, +2 against strikes; townhouse or larger); **garrison** (4 guards at 08's soldier wage; garrison
+1; watchtower or larger); **shrine** (300, 6 weeks; a keeper's place: rites kept there, Solace as at a
temple, 15.13.2); **library** (500, 8 weeks; a tier-1 collection for 15's research week); **workshop
wing** (400, 8 weeks; a workplace for one craft, 08.6); **stables** (150, 4 weeks; the owner's mounts
stabled without cost); **hall** (800, 10 weeks; may host a faction's sitting: hosting is a week of
service, +1 status with that faction once a season); **hidden room** (200, 4 weeks; a cache only the PC
and those told know, which 07's dispositions never find); **market charter** (1,000 and a grant from the
seat faction at status ≥ +2; a shop's yield dice doubled in a town). A holding below a manor carries at
most three improvements, a manor or keep six.

**11.9.7 Great projects: changing the map.** `[D]` + `[J:enum]` + `[J:rung]` When the PC sets out to change
the world beyond what one adventure does — found a village, bridge a river, end a feud, topple a guild,
clear a valley for good — chapter 15 runs the project (15.12: a clock by scope, a weekly roll, coin by
scope, obstacles that are threads) and this chapter decides **what changes** when it completes [R5 P-24;
R5 §2.4 (WWN's project rules)].

```
### 11.9.7  Great project: the world change                             [J:enum] [J:rung] [D]
Trigger [T]:        the player declares a project whose intent changes a place, a route, a faction or a
                    custom (15.12's project beat)
Loads in:           situation.downtime.project
License check:      the project's weekly beats use their own licenses (15.12)
Decisions (J):      1. KIND [J:enum] (T-11-17): found, connect, pacify, reconcile, raise, topple, reform,
                       establish, cleanse, restore. True only when the intended end state is that row's
                       "changes"; uncertain -> the row whose writes are smallest.
                    2. SCOPE [J:rung]: personal (a holding, a hut), local (a village, a valley, one
                       feud), regional (a road across the region, a regional faction), realm (a law of
                       the realm, a great faction). Anchor: who would notice it done.
                    3. OBSTACLES [J:flag] per 15.12: each named blocker that is a fact becomes a thread
                       (11.5) whose completion removes it.
Computation [D]:    15.12's clock and coin by scope; a reputation entry of score >= 3 in the project's
                    scope on a key the project expresses is an Amplifying lever on its weekly beat (the
                    PC's name opens doors); a faction whose status toward the PC is +2 or more and whose
                    values the project serves may lend a delegated tick per week (15.12's delegation);
                    a faction the project harms (topple, reform against its values) treats each week's
                    progress as a known deed against it (T-11-3, small) and may oppose with a racing
                    clock (its goal re-aimed: the rival's counter-project). On completion: the row's
                    writes; a consequential change (traces, 11.6.2); a chronicle line; +2 points of
                    reputation on the project's key in its scope.
Stakes:             15.12's
State writes:       the world change; reputation; chronicle; status steps
Narration may not imply: the change before the clock fills; a larger change than the row
Worst case (J):     KIND one row off: a change of the same scope with smaller writes (class i); SCOPE one
                    rung off: 15.12's clock 4 segments or a linked clock larger or smaller, shown before
                    the project starts (class i).
Examples:           inside: Wren's charcoal camps want a road to Ashford: connect, local -> a new route
                      link of 6 travel watches where there was 10.
                    boundary: "a road all the way to the capital" -> regional; the Guild, whose tolls it
                      bypasses, opposes with a racing clock.
                    non-example: "I make the Guild like me": that is status, moved by deeds (11.3.11), not
                      a project.
Anchor:             yes. Intent verbs: "build", "found", "clear for good", "unite", "bring down",
                    "change the law". Knobs: time_cost (scope), targets (the place or faction),
                    reach_unit (ticks per week). Covers any deliberate, lasting change to the map.
                    Does not cover: a change one scene makes (that is a beat).
Basis:              [R5 P-24, LW-09] [15.12] [DL-11-19]
```

**T-11-17 World changes** (canonical: `world_turn.yaml#world_changes`).

| Kind | Changes | Writes on completion |
|---|---|---|
| **found** | a new settlement, waystation or holding | a new place in the graph (10.1), `safe: true` if garrisoned; a petty faction (its people) at tier 0, Warm toward the PC |
| **connect** | a road, bridge, ferry or pass | a new route link, or an existing one shortened by a third (rounded down) or made passable in winter |
| **pacify** | an area made safe for good | its danger rating down one rung permanently (never below `settled`), and its home band down one where a hold stands |
| **reconcile** | a feud ended | the two parties' relations set to −1 (or the value agreed); the feud situation `defused` |
| **raise** | a faction lifted | its hold gained (11.3.4); stage `rising` if it was declining |
| **topple** | a faction brought down | it loses hold twice; stage `declining`; a linchpin's `exposed` fate fires if the project exposed one |
| **reform** | a law or custom changed | a regional fact; each faction's status toward the PC ±1 by its values (admired +1, despised −1) |
| **establish** | an institution founded | a faction from the template of its `org_tags` at tier 0, rising, the PC its head (11.9.8) |
| **cleanse** | a cursed, haunted or fouled place set right | its situation `defused`; its resonance or `cursed` fact removed (05, 13) |
| **restore** | a ruin made whole | the place's `safe` restored, its owner named, 10's `cleared` sites made a settlement or a hold |

**11.9.8 Rulership.** `[D]` When the PC heads a faction — rung 5 of its ladder, a faction the PC
established, or a keep (which is a tier-1 faction, 08.8.8) — that faction is the PC's **domain**, and it
takes the World Turn like any faction with two differences: (1) its action is **chosen by the player**
(out of fiction, at any time during the week; with no choice, `goal`), from the closed list of 11.3.6
except `move_on_pc` and `aid_pc`, against targets the player names among the eligible; (2) its goal is
chosen by the player from its template's goal kinds at the scopes its tier allows. Its ratings are its
template's at its tier, then: wealth +1 for each holding of its yielding 35 coins a week or more on
average (up to +2); force +1 with walls and a garrison at its seat; sway +1 while the PC's reputation in
its seat's region is 3 or more; each clamped to the cap. A week the PC spends governing in the seat
(15.13.11's week of oversight applied to the seat) is a +2 Precision lever on that week's domain check.
The PC's own threads may tick the domain's goal clock as milestones (+2) when they serve it. The domain is
not a second character: it never acts in a scene except through the people it fields, and it loses hold,
falls and collapses like any faction [R5 LW-10 (WWN rulership; ACKS domains); R6 D-14; DL-11-19].

**11.9.9 Gifts.** `[D]` Whether anyone gives is this chapter's (08.7.1); what is given is chapter 08's. The
fact `gift_due.<giver>` (which makes 08's `gen.gift` run) is written only by: (a) a completed thread whose
patron promised a reward (`earned`); (b) a promotion to rung 3, 4 or 5 (`earned`); (c) a faction at +3 at a
Season Turn, at most once a year (`favored`); (d) `aid_pc` when a reward is owed (`earned`); (e) a bargain
with a power whose new obligation is written first (`bargained`, 05, 04). Every faction carries its
`boon_base` (its customary gift) and `boon_signature` (its gifts' identity property) in data (08's
request): an order's blade with `prop.bane_undead`, a guild's ring with `prop.haggler`. A gift sold is a
deed against its giver (T-11-3) if the giver learns of it.

### 11.10 The calendar and aging

**11.10.1 The year.** `[D]` The calendar engine sits on 00's arithmetic (00.7.1; 00.17.1 Q19): a year is
**364 days** = four **seasons** (`spring`, `summer`, `autumn`, `winter`, in that order; the ids chapter 10's
weather regimes read) of **13 weeks** = **91 days** each. Within a season, day 1 is the season's **quarter
day**, which belongs to no month (spring's quarter day is the year's first day), and days 2–91 are three
**months** of 30 days. Weeks of 7 days run unbroken through the year, so every season begins on the first
day of a week and every year on the same weekday; the year has 52 weeks and 12 months. The region's seed names the
months, weekdays, quarter days, festivals and the era (`calendar`, 12.16.15; a pre-made setting may use
its owner-block of `calendar.yaml`); until one does,
the engine's neutral names stand ("the second month of spring") [R5 TM-07; DL-11-21].

**11.10.2 Dates.** `[D]` `date(timestamp)` renders `{quarter day of <season> | <day> of <month>}, <weekday>,
year <n> <era>` and the watch; the codex shows it (shown, 00.6.3). Campaign year 1 begins on spring's quarter
day unless the region's seed sets an opening date (12.16.15). All of this chapter's durations ("8 weeks", "a season") are
counted in the ladder's units, so the calendar's names never change a duration.

**11.10.3 The moon.** `[D]` The moon runs a 28-day cycle, thirteen to the year, starting new on the year's
first day: day 1 of each cycle **new**, day 8 **waxing half**, day 15 **full**, day 22 **waning half**.
The fact `moon.phase` is written at each `day` boundary for rites, tides, beasts and situations that key on
it (05's rites, a werewolf's nature, "the cult completes the rite at the new moon").

**11.10.4 Festivals.** `[D]` A festival is `{id, name, season, week, day, effects}` in `calendar.yaml`, with
effects from this closed list: **market** (that week, find-buyer clocks tick +1 and one price notch is
waived in haggling, 08/15); **sitting** (factions whose sittings name it confer ranks, 11.8.3); **rumor
surge** (all rumors circulating in the scope are drawn at weight 3; Carouse yields one more); **truce** (in
its scope that week, faction strikes read as `goal`); **rite day** (a named school's rituals there count one
scale lower in cost, 05); **hiring fair** (16's recruiting delivers one more candidate). The four quarter
days are festivals with `market` and `sitting` unless the region's seed says otherwise.

**11.10.5 Aging.** `[D]` + `[T]` A PC has an **age** in years: the one the player stated, or by 02's
`age_band` young 18, grown 30, old 55; it rises by 1 at each Year Turn. A character's people fix when
**aging** begins (`calendar.yaml#lifespans`, by `creature.folk` tag; a pre-made setting may adjust): orc and
goblin 35; human, halfling and beastfolk 50; giant 80; dwarf 120; elf 300. From that age, at each Year
Turn, the PC makes an **aging check**: Endure with Endurance (00.12.5), the engine rolling, against
**Easy** in the first decade of aging, **Moderate** in the second, **Hard** in the third, **Very hard**
thereafter; fate may reroll it (01.16.3).

| Degree | Result |
|---|---|
| critical success | nothing, and no aging check next year |
| success | nothing |
| failure | an **aging mark**: −1 to Might, Agility or Endurance, the player's choice among those not yet lowered by age or by a maim (07.7.4), under 00.4.3 (c)'s limits (at most −1 per attribute from marks of every kind together, never below −2) [verification: V2c-009]; once all three are lowered, the mark is counted and changes nothing more |
| critical failure | an aging mark, and the retirement offer (11.13.1) at the next reflection |

At **three** aging marks the retirement offer comes at every Year Turn; at **five**, the career ends
(`career_end`, as 07.11.6's fourth break): retirement runs with an ending the player picks. **Age ends
careers; it never ends lives in play** (INV-6 holds: no death without two keys). Named NPCs age too: a
recurring or principal NPC past its people's aging age asks the Oracle once a Year Turn "does this person
die this year?" (Remote in their first decade of aging, Unlikely in the second, Even in the third, Likely
after), and a "yes" writes the death within the year at a time the engine rolls — firing a linchpin's
`dies` fate if they are one [R5 HR-10, P-44 (Pendragon and Ars Magica aging); DL-11-22]. At the reference
rate of world time (12.7.7: about two weeks a session, a tier-5 career in 2–3 years) aging reaches a PC
who starts old within one career and otherwise arrives through timeskips and successions: a long-campaign
rule by design [revision: I-085].

### 11.11 The Season Turn and the Year Turn

**11.11.1 The boundary point.** `[D]` Principle VI asks that retirement and consolidation be bundled into
**infrequent, clearly telegraphed boundary points**, never piecemeal [C:VI]. The season boundary is that
point for this game. Handler `h.11.season_turn` (`season`, phase 6, interrupting per 11.2.5) runs after
`h.10.weather_regime` (phase 6, chapter 10) and before `h.04.season_consolidation` (phase 8), so the world
settles first and the character's consolidation reads the settled world (04's request). Nothing in this
chapter consolidates, retires or folds anything at any other time, except a retirement (11.13) and the
caps that bound a register when it overflows (11.2.8) [R1 #15 "put VI's boundary points in the world";
R2 #15; R5 P-44; DL-11-23].

**11.11.2 The herald: one week's warning.** `[D]` + `[N]` At the World Turn of the season's 12th week
(step 8), the engine writes the **season herald**, an out-of-fiction notice (`[SEASON]`, rendered by 14 and
12) listing, from player-facing state only, everything the coming boundary will settle: chapter 04's
provisional grants awaiting confirmation or lapse (read from 04's state); this chapter's provisional ranks;
the world phenomena up for confirmation or retirement; threads that will expire; reputation entries that
will fade or fold. In fiction, the turn of the season is voiced as itself — the first frost, the spring
fair, the long days — never as an announcement. The player has a week to act on what is due (keep an
obligation, take up a thread, visit a mentor), which is what "telegraphed" means here [C:VI; R3 11.7
(publish the why); DL-11-23].

**11.11.3 The Season Turn's steps.** `[D]` In this order (`world_turn.yaml#season_steps`):
1. **Calendar.** Write the season; the quarter day's festival (11.10.4).
2. **Factions.** Stage transitions and the weight of size (11.3.9); cooling (11.3.14); pursuit decay
   (11.3.12); obligations tallied and provisional ranks confirmed or lapsed (11.8.5–11.8.6); sittings
   held (11.8.3); a `favored` gift for each faction at +3 not yet so rewarded this year (11.9.9).
3. **Situations.** Over the cap of eight per region, retire the oldest whose actors have all left or
   collapsed, then the oldest concluded (11.4.3).
4. **Seasonal events and world phenomena.** For each region, roll `tbl.11.season_events.<season>` (d12,
   `world_turn.yaml`; a region's seed or setting may give it its own): about one result in three is a **world
   phenomenon** (11.11.4), one in four a new situation, the rest nothing remarkable. Then review the
   phenomena of the season just ended (11.11.4).
5. **Threads.** Retire threads per 11.5.5; enforce the caps (11.5.9).
6. **Reputation.** Spread (11.7.4); fade and fold (11.7.9).
7. **Holdings.** Absentee penalties (11.9.3); seasonal yields (a farmstead yields no supply in winter).
8. **Seams.** Mark the retirement offer for the next reflection if a seam holds (11.13.1).
9. **Record.** The season's digest line in the chronicle, built from the season's raw entries (11.12.5).
The season boundary also fires `reflection` (`h.00.reflection`, phase 8), at which 04 consolidates.

**11.11.4 World phenomena: provisional content at world scale.** `[D]` A **world phenomenon** is a
condition laid on a region for a season — a sickness in the cattle, a comet year, a hard winter, a
bandit summer, a pilgrimage, a good harvest, a war levy — written as a fact `{region, phenomenon, effects,
season, status: provisional}` with effects from `world_turn.yaml#phenomena` (each a closed set of state
writes: a danger rating up or down one rung, prices one notch, a situation template, a festival, a
faction's goal rolls +1 or −1). It is the world's provisional content, R3's seasonal phenomena under
Principle VI [R3 11.3]: at the next Season Turn each phenomenon is **retired** (the default: its effects
end, a news item says so) or **confirmed** — made a permanent regional fact — only if its
`confirm_when` holds (a sickness no one cured becomes endemic: its situation concluded with no PC
intervention). A phenomenon never extends itself by narration.

**11.11.5 The Year Turn.** `[D]` Handler `h.11.year_turn` (`year`, phase 6) runs after the spring Season
Turn of the same instant (00.7.6: `season` before `year`): (1) **aging** for the PC and named NPCs
(11.10.5); (2) the **annual festival** of the region's calendar, if any (12.16.15); (3) the **year's digest** line,
built from the year's raw chronicle entries, never from the season digests (00.6.9 d); (4) **legend
review**: every reputation entry of score 5 writes its epithet as permanent world vocabulary (it no longer
fades even if its points fall), the first quiet step of a legend; (5) each retired PC still living as an
NPC rolls its aging (11.13.7).

### 11.12 The chronicle

**11.12.1 The world's memory.** `[D]` The **chronicle** is the append-only history of the world (00.6.1
ledger; tool `chronicle_append`, 00.14.2). It is the true record — rumors are the distorted layer — and the
long game's continuity rests on it rather than on anyone's recollection (Dwarf Fortress's legends; the
Alexandrian's campaign status document) [R6 B-07, B-12, B-R8; R2 11 "durable memory"; DL-11-24].

```yaml
ChronicleEntry (extends 00.6.2):
  id: chr.*
  time: time                    # when it happened (prologue lines are dated before play)
  text: str                     # <= 30 words, past tense, neutral; names, places, deeds
  kind: prologue | deed | thread | defeat | death | faction | situation | world_change | recognition
        | holding | season | year | legend | retirement
  entities: [id]
  tags: [tag]
  scope: public | [scope]       # who could know it (the witnesses' scopes; public once it is news)
  source: rule id               # which rule wrote it
  supersedes: chr.* | null      # a correction (11.12.3)
```

**11.12.2 Who writes it (closed list).** `[D]`
- creation's **prologue** lines (02.11.2), tagged `prologue`;
- chapter 12's **scene-end** line when a scene answered a thread's agenda (12.4.8) and **venture-end** line
  (12.4.9), accepted as offered, at most one each (12's request f);
- chapter 07's **legend line** of a Last Stand (07.5.9), the line of every brink choice (07.5.12) and of
  every defeat (07.6.2);
- the **World Turn's record** (`h.11.world_record`, phase 9): at most five lines per turn, in this order:
  linchpin fates, collapses, wars begun or ended, goal completions of tier-2+ factions, situations
  concluded or defused, holds changing hands;
- **threads**: every completed vow and every completed or failed thread of rank formidable or higher;
- **recognitions** staged before witnesses at tier 3 or higher (04.7.8);
- **deaths** of named NPCs; **world changes** of great projects; **holdings** acquired, ruined or lost;
- the **season** and **year digests** (11.11.3, 11.11.5);
- **retirement**: the period and its events (11.13.3).
The DM never appends a line freely; wording is `[N]` within these occasions [R4 W8, W9].

**11.12.3 Append-only.** `[D]` No entry is edited or deleted. A line found to be wrong (12's claim check
finds a chronicle line that contradicts state) is answered by a **correction** entry that `supersedes` it;
both remain. Summaries are never summarized again (00.6.9 d).

**11.12.4 How the chronicle is used.** `[D]`
1. **Recaps** (12.5.2) are generated from the entries since the last recap, and from nothing else.
2. **Continuity:** before any generator or rule writes content about the past of a place, person or faction
   (a rumor's text, an NPC's memory of an event, a legend), it queries the chronicle by entity id; content
   that contradicts an entry is refused and redrafted (the claim check treats it as a `state` error, 12.3).
3. **Citation:** an NPC may cite a line only when the line's `scope` reaches the NPC's home or factions, or
   the NPC is among its entities; this is 12.10.6's knowledge rule applied to history.
4. **Legend:** retirement builds the character's period from it (11.13.3); `legend` rumors draw on public
   lines older than a year (11.6.3).
5. **The successor's world:** a successor's codex shows the public chronicle of their region as known
   history (11.13.8).
The player may read the chronicle (visibility available) as far as their character knows it: lines whose
scope reaches the PC, or that the PC witnessed.

**11.12.5 Digests.** `[D]` A season digest is one entry of at most 60 words listing the season's three to
five weightiest raw entries (weight: retirement, death of a linchpin, collapse, war, world change, thread
completion of rank extreme or epic, recognition tier 4+, then everything else by time); a year digest is
built the same way from the year's raw entries. Neither is ever an input to another digest.

### 11.13 Retirement and legacy

The sandbox has no finale. "Finish" is the player's choice to end a character's story, and the world
keeps the character: as an NPC, a legend that is partly wrong, threads that pass on, places that remember
and a successor who begins at the floor in a world that has moved [BRIEF §4; R6 §D]. Retirement is also
the largest structural retirement Principle VI could ask for: everything the character *is* retires
wholesale, and only bounded channels carry value forward [C:VI; R6 D-R2 step 5; 04.11.4].

**11.13.1 When: seams, offers and forced ends.** `[D]` + `[T]`
- **Always:** the player may retire the character at any `reflection` or session start (out of fiction).
- **Offered** (never forced; 04.7's protocol: accept, decline, defer — a deferred offer returns at the
  next seam), at the next reflection after any of these: `apotheosis_available(pc)` becomes true (04.11.4);
  the long vow (02.9.1) is kept; a thread of rank extreme or epic is completed, or one of rank formidable is
  completed in a season that has just ended (an arc closed at a seam [R6 D-15]); the third aging mark, and
  every Year Turn after it (11.10.5); an aging check's critical failure; the third haunt (07.11.6) or the
  third brink mark (07.7.3).
- **The career ends** (the player picks the ending from those allowed, but cannot decline the end): The Road
  Ends (07.5.11: ending `retire_to_a_life`, at once); the fourth dread break (07.11.6: `career_end`, at the
  next `scene_end`; endings `retire_to_a_life`, `patron` or `depart`); the fifth aging mark (11.10.5: any
  living ending).
- **Death** (07.3.1's two keys; a Last Stand, 07.5.9; a lost Gamble, 07.5.10) runs the same procedure with the
  ending `remembered`.
The offer is an out-of-fiction `[RETIRE]` block (12.15; 14 renders) listing the endings available and
what each would write, then a CHOICE [R6 D-R1; 07's request].

**11.13.2 The endings (closed list).** `[D]` (`legacy.yaml#endings`)

| Ending | Available | The character afterward | Writes |
|---|---|---|---|
| **retire_to_a_life** | always (living) | a principal NPC at home (its home holding, or the settlement the player names), living at the settlement's lifestyle (11.13.4) | `exists: exists`; home; standing toward a successor (11.13.9) |
| **patron** | living, with a holding, a rank of rung 3+, or a faction status of +2 somewhere | a principal NPC who stays a power in the world: keeps its holdings, its reputation, its faction ties as a member (not its seats) | as above; may be the successor's V2 mentor (04) or patron (a faction-like source of opportunity bangs at +2) |
| **apotheosis** | `apotheosis_available(pc)` | the calling's authored ending: the form from `legacy.yaml#apotheosis_forms` by the calling's deed branch (two forms each; the player picks): the paladin taken up, the ranger gone into the wood, the sorcerer become a storm | `exists: departed`; a **place of the legend** (11.13.3) with `resonance` for the calling's key (04's V11 may answer a successor there); legend rank +1 |
| **depart** | living | gone beyond the map: the sea, the far road, the West | `exists: departed`; a rumor of where (legend source) |
| **remembered** | after death | dead; a grave or a cairn where the body lies, or a place of the death | `exists: dead`; a place of the legend at legend rank 2+ |

**11.13.3 The epilogue.** `[D]` + `[N]` PR-11-6 runs it. In order:
1. **Ending** — the player's choice (11.13.2).
2. **Settlement** — the estate and what persists (11.13.4).
3. **Legend** — the **legend rank** (T-11-20), the **period**, the **legend rumors** and the **permanent
   epithets**:
   - The rank is computed: 0 *unremembered* (renown 0); 1 *a local name* (renown ≥ 1); 2 *known in the
     region* (a region entry ≥ 2, or breadth ≥ 3); 3 *famed* (a region entry ≥ 4, or a realm entry ≥ 2); 4 *a
     legend* (a realm entry ≥ 4, or a region entry 5 and a calling confirmed at tier 5); 5 *a myth* (a realm
     entry 5, and the ending `apotheosis` or an epic thread completed). Apotheosis adds one rank, to 5 at most
     [R6 D-05 (Wildermyth's Folk Hero … Mythwalker)].
   - The **period** (Microscope's history-as-product [R6 D-11]): one chronicle entry naming the character's
     span ("The Quiet Fires, the third to fifth years") and three to five **event** entries selected
     deterministically from the chronicle lines naming the PC, by weight (the heaviest first: a linchpin's
     fate by the PC's hand; an extreme or epic thread; a recognition at tier 4+; a world change; a war ended;
     a formidable thread; a defeat survived at the brink; then by time). The DM words the period line `[N]`;
     the events quote their chronicle lines.
   - **Legend rumors** (rank 0: none; 1: one; 2–3: two; 4–5: three): rumors with `about` the PC, source
     `legend`, truth by T-11-11's legend row (so the legend is partly wrong, as legends are), each pointing to
     a real placement (the grave, the old camp, a former ally's door) a successor can test (11.6.4).
   - **Epithets** of score 3 or more become **permanent world vocabulary** (a fact the realm's NPCs may use).
   - At legend rank 3 or more, or for the endings `apotheosis` and `remembered` at rank 2+, a **place of the
     legend** is written: a statue in the square, a cairn at the ford, a shrine where the character was taken
     up — a place in the graph that later characters can visit (Wildermyth's statue; Dwarf Fortress's
     graves [R6 D-05, D-12]).
4. **Threads** — each open thread is, by the player's choice: **bequeathed** (11.13.6), **left to the world**
   (it runs on as its situation, its opposing clock or its patron's `if_unmet` — the world settles it), or
   **abandoned** (only its source's stated costs; 11.5.5).
5. **Structural retirement** — 11.13.7.
6. **The character becomes an NPC** (or departs, or lies dead) — 11.13.7.
7. **Timeskip** — the player chooses (11.13.8).
8. **Successor** — three candidates and a newcomer (11.13.9).
9. **Inheritance** — the bounded channels (11.13.10).
10. **Chronicle** — the retirement entry (kind `retirement`), the period and events (step 3), the legacy
    record written as an entity (`legacy.<pc id>`: ending, settlement, legend rank, ledgers, bequests,
    successor) [R6 D-R2; R4 11 #5 (a scripted sequence of state summaries so the epilogue cannot contradict
    history)].

**11.13.4 Settlement: the estate and what persists.** `[D]` The **estate** is the character's coin, plus half
the list price of its items that have a price (08.8.5), plus the buy price of its holdings. The **settlement
lifestyle** is the highest of 08's lifestyles (`economy.yaml#lifestyles`) whose weekly cost × 104 (two
years) is at most the estate plus 104 × the holdings' average net weekly yield; owning the home holding it
lives in raises it one rung (no rent). With the reference costs that is: poor at 416, modest at 728,
comfortable at 1,456, wealthy at 3,640, noble at 10,400 (Blades' stash tiers, at this economy's scale
[R6 D-01]). **What persists:** each holding **persists** if someone runs it — a steward, staff of one or
more, an ally at Friendly or Devoted, a successor who inherits it, or the retired character living there —
and keeps yielding to its owner's household; otherwise it **falls**: it becomes a site of chapter 10 (theme
by its type — a manor becomes a ruin of the `fortress` kind) with the legend as its rumor and the
character's hidden room, if any, still inside it (Dwarf Fortress's abandoned fortress, reclaimable
[R6 D-12]). Coin is not inherited except through 11.13.10's purse; invested wealth (holdings, improvements,
the successor's training) is what lasts [R6 D-13].

**11.13.5 Legacy ledgers.** `[D]` Three ledgers are scored 0–10 from the record (Ironsworn's legacies
[R6 D-04; R5 P-43]; 03's request: "the settled ledger and tallies are the record legacy reads"):
- **Deeds** = (the sum over completed threads of their rank points — troublesome 1, dangerous 2, formidable
  3, extreme 4, epic 5 — plus 2 per great project completed) ÷ 3, rounded down, capped at 10;
- **Bonds** = the number of NPCs and allies at Friendly or Devoted toward the character, plus the factions at
  +2 or +3, capped at 10;
- **Discoveries** = (places discovered ÷ 3, rounded down) + sites cleared + 2 per world change, capped at 10.
For each ledger the engine rolls `d20 + ledger`: **20 or more, a strong inheritance** (something concrete);
**12–19, an opportunity**; **11 or less, trouble** — and trouble is a hook too (T-11-21; `legacy.yaml#ledgers`).
At ledger 0 that is 5% / 40% / 55%; at ledger 5, 30% / 40% / 30%; at ledger 10, 55% / 40% / 5%: a rich life
leaves a rich legacy, and even a short one leaves something to do.

**11.13.6 Bequests.** `[D]` A **bequeathed** thread passes to the successor as a new thread of the same kind
and rank with **half** its progress (rounded down; Ironsworn's weak hit), its clue graph, its opposing clock
(which kept running through the timeskip) and its fallback; a strong Deeds result keeps its full progress for
one thread. A vow is bequeathed only if the successor swears it at creation (it is offered then as a hook; a
successor who declines leaves it to the world). At most **three** threads may be bequeathed.

**11.13.7 What retires, and what the character becomes.** `[D]`
- **Retired wholesale:** every calling, tier, pick and library entry (04.11.4); every ability, slot, shelf
  entry and the Focus pool (05); every license, competence entry, attribute, Vitality, wound, mark, haunt,
  dread and fate point (they belong to the person, who is no longer played); every rank seat (freed at once,
  11.8.6; a hereditary crown or clan rank becomes a **claim** thread a kin successor may take up); the
  attention clocks and pursuit aimed at the character (enemies' interest in the successor comes only through
  the ledgers' trouble and 11.13.10 item 6).
- **Kept by the world:** the chronicle; the character's reputation entries, as the retired NPC's; its
  epithets; its holdings (as persisting or fallen, 11.13.4); its relationships, as the NPC's.
- **The character as an NPC** (living endings): a principal NPC (12.11.1) whose record is its final sheet,
  sealed as a stat block at its final power band (16.16.3: above the successor's band, it never follows as
  retinue); its standing toward the successor is fixed by their relation (02.9.2's bond table: kin or ward
  +2, friend +2, mentor +1; any other successor +1); it may be the successor's **V2 mentor** (04.11.4) or
  **patron**; it ages (11.10.5) and may die off-screen by the aging Oracle; it acts by chapter 12's NPC rules
  and never takes a player's turn again (R6 D-05: never back as a PC at full power). Chapter 16's retinue
  rules say what its allies do (16.16.2).

**11.13.8 The timeskip.** `[D]` Before the successor begins, the player chooses how long the world runs
without a PC (`legacy.yaml#timeskips`): **none** (the successor begins the next morning); **a season** (13
World Turns and one Season Turn); **a year** (52, four and one Year Turn); **five years**; **a generation**
(twenty years; required when the successor is a child of the character not yet grown). `advance_time` runs
every boundary of the span with every handler (00.7.7, INV-15) under 11.2.6's suspended rules: factions
act, situations conclude, bequeathed threads' opposing clocks advance but **stop one segment short of completion** (the successor inherits a crisis, never a loss
already suffered), holdings yield or decay, the retired character ages, rumors fade and legends spread. Nothing is narrated during the
skip; the successor's first session opens with the **digests** of the span (season digests for a skip of a
year or less, year digests beyond) and the news of their home scope (Legacy's age-jump; Pendragon's winter at
scale [R6 D-09, D-02, D-R3]). A generation-long skip is 1,040 World Turns: engine work, never narration.

**11.13.9 The successor: three from the story, and a newcomer.** `[D]` + `[J:flag]` The engine fills three
candidate slots, first from the first source, then the next, with people who are alive, not departed and
in state (Kingdom's promotion of someone already in the story; Pendragon's heir [R6 D-10, D-02, D-R4]):
1. a **protégé** (16), an **heir or ward** (02's ward bond, a recorded child), the subject of a completed
   **Train-a-Successor** (11.13.10 item 4);
2. an **ally** at Friendly or Devoted, or a companion who left content (16.16.1);
3. a **bond** NPC of the character's (anchor or thorn);
4. someone the character **rescued, freed or spared** who is at Warm or better toward it;
5. a **rival's child** or a former enemy at Neutral or better (the Kingdom shape: a lesser character
   promoted).
Ties within a source: the higher standing toward the character, then more scenes shared. Each candidate is
shown with one **tie** (+) and one **thorn** (−) read from their own record: the tie is their best faction
status or bond, the thorn their worst faction status or an owed commitment (`[J:flag]` per candidate, only
when their record holds neither: "does any recorded fact give this person an ally or an enemy?"; false →
`tbl.11.successor_traits`, d8 pairs; *worst case (J):* a rolled pair where a recorded one existed: a written
tie the world keeps, class iv) — Rogue Legacy's three heirs with visible trade-offs [R6 D-13]. The **newcomer**
is always offered: chapter 02's full procedure, from anywhere. Whoever is chosen is made by **02.2.7**: the
floor, nothing of the predecessor's power, origins fixed by recorded facts, a fresh birth draw.

**11.13.10 Inheritance: the bounded channels (closed list).** `[D]` A successor receives these and nothing
else (02.2.7 forbids the rest) [R6 D-R5]:
1. **A share of renown.** In each scope where the predecessor has an entry of score 3 or more and the
   successor is connected (home there, a member of that faction, or kin, ward, protégé or ally of the
   predecessor known there), the successor gains an entry with key `legacy` ("the Match's girl") at
   **score 1**, or **2** if the predecessor's score there is 5 and the successor is kin or protégé.
   (Score 1 is 1 point of the predecessor's 6–15; score 2 is 3 of 15: Pendragon's fraction at 7–20%
   [R6 D-02].)
2. **One heirloom.** One item of the predecessor's, the player's choice, added to the successor's kit
   beyond 02's limits (02.2.7); its properties and any bound ability are kept; attunement resets; a gifted
   item keeps its `gifted_by` (its giver may remember).
3. **The ledgers' results** (11.13.5; T-11-21): each as hooks, bonds, places known or trouble owed.
4. **Training.** Each tag banked by Train-a-Successor (below) becomes one of 03's backstory events at
   creation (03.2.8: 24 points each, at most three tags, each a different tag [revision: I-087]), the only backstory
   evidence in the game.
5. **The predecessor itself** (living endings): an NPC with a fixed standing (11.13.7), who may be the
   successor's anchor bond (02.2.7 item 3) and mentor.
6. **Standing that transfers:** a kin, ward, protégé or ally successor starts with each faction's status
   toward them at the faction's status toward the predecessor moved one step toward 0 (loyalty to a person is
   not loyalty to their heir, 16.16.2; neither is enmity); any other successor starts at 0 with every faction
   except as the ledgers say.
7. **A home.** A kin, ward or protégé successor inherits the predecessor's home holding if it is a cottage,
   townhouse, workshop, shop, tavern or farmstead (while a living predecessor still lives in it, the successor
   has it as a haven and inherits it at the predecessor's death); a manor or keep passes to the **household** (the domain
   faction, or a new one at tier 1 from the `org.clan.family` template, the predecessor its head while it
   lives), in which the successor holds rung 1, with a claim thread for more.
8. **A purse.** A kin, ward or protégé successor: coin equal to 10 weeks of the settlement lifestyle, at most
   350. Any other: none.

**Train-a-Successor** (`dt.11.train_successor`, week; 11 defines it and asks 15 to list it in its menu):
with a named candidate NPC who is present and willing (standing Warm or better), the PC spends a week teaching
one deed tag at level 2 or 3 in which the PC holds competence +3 or more: a check `d20 + the PC's base modifier
on that tag` against Moderate (15), Safe stakes; delivered reach ticks the candidate's **training clock**
(public, 12 segments). Every 4 ticks bank one tag (the one taught most that stretch among the tags not yet
banked; a stretch that taught only banked tags banks nothing), at most three, **each a different tag**; the
clock then closes [revision: I-087]. So one tag is at most one 24-point event, a session's head start, and three
banked tags need three taught; teaching one tag twelve weeks banks it once. The banked tags are written to the candidate's record and used only if the candidate becomes the
successor (The One Ring's Raise an Heir [R6 D-03]).

**11.13.11 After the hand-off.** `[D]` The bang queue, cleared at the timeskip's start, is refilled for the
successor: each ledger result that is a hook becomes a kicker (11.4.5), a bequeathed thread's fallback is
queued, and a living predecessor arrives in the successor's first or second scene. The hook supply rule
(11.5.10) runs at once. Chapter 16 decides which allies stay (16.16.2). The world the successor walks into is
the same world, a little older, with a statue in the square.

---

## Procedures

**PR-11-1 The World Turn.** `[D]` (`h.11.world_turn`, `week`, phase 6)
1. **Elapse.** Close the change log; open the next. Stamp `{year, season, week}`. Read `pc.location`,
   `pc.on_venture`, and whether play is suspended (11.2.6).
2. **Maintain.** For each holding: unpaid upkeep → damage +1; yield check (11.9.4); threats due (11.9.5). For
   each rank: obligations falling due this week are passed to `h.15.commitments_due`'s record. For each
   linchpin whose fate fact was set this week and has not fired (an off-screen death): fire it (11.3.10). For
   each faction: clear spent scheme levers older than a season.
3. **Timelines.** For each active situation of cadence `week` (region order, then id): fire due steps
   (11.4.2). For each clock that completed in phase 5: run what its owner's rule says (a thread's opposing
   clock → the thread fails; a hunt clock → a threat bang).
4. **Factions.** Order full factions by tier (highest first), then id. For each: overrides (a)–(c), else the d6
   agenda row (11.3.7); targets (11.3.7); the check (11.3.5) if the action has one; results (11.3.6); every
   status, hold, relation or place write is logged as a change; a status write triggers
   `h.15.member_standing` at once. Then each petty faction's d6 (11.3.16).
5. **Consequences.** For each change in the closed log (log order): match reactions (11.4.6); at most one
   per change, six per region; apply; start cooldowns. Unknown deeds stay in the log (11.3.11).
6. **Attention.** Attention clocks have already decayed in phase 5 (their `decay` rows); for each that
   completed this week: pursuit +1, roll `tbl.11.entanglement`, queue the bang, reset (11.3.12).
7. **News and rumors.** For each consequential change of steps 2–6 and of play this week: emit its traces
   (T-11-10; PR-11-7 for rumors). Spread everything circulating by one step (T-11-12). Fade what is due.
   List what reached the PC's settlement scope this turn.
8. **Queue.** Expire bangs; drop beyond six (lowest specificity first) running `if_unmet`; a kicker if no
   personal bang is queued (11.4.5); register upkeep (11.5.8); the hook supply rule (11.5.10); at week 12,
   the season herald (11.11.2). Return the narration list (11.2.7).

**PR-11-2 A faction's turn.** `[D]`
1. If the faction is collapsed: skip. If petty: d6 (11.3.16); stop.
2. Overrides, first match: slip → `recover`; at war in region and d6 ≤ 3 → `strike` at the war enemy;
   status ≥ +2 and (a ransom, a threatened holding or a reward is due, or d6 = 1) → `aid_pc` [revision: I-032].
3. Else roll d6 on its temperament row; if the row's condition fails, `goal`.
4. Target by 11.3.7's ladder; if no target, `goal`.
5. Compute the DC (11.3.5); roll `d20 + rating + 2 × tier + stage + lever`; read the degree (00.3.10).
6. Apply the action's row (11.3.6). Goal clock completion → its `effects`; a new goal from the template's
   goal list (d6 by kind, scope by tier); a stage change if declining (→ rising).
7. Log every write; emit traces in step 7 of PR-11-1.

**PR-11-3 The Season Turn.** `[D]` (`h.11.season_turn`, `season`, phase 6) Steps 1–9 of 11.11.3, each over
every record it names, in that order; then return the season's news for narration (the turn of the season
is voiced in fiction; the herald already told the player what is due).

**PR-11-4 Consuming other chapters' events.** `[D]` (each as it arrives; each is also a logged change)

| Event (source) | This chapter writes |
|---|---|
| `public_deed` packet (03.10.5) | reputation per scope (11.7.3); a rumor if noteworthy (T-11-10); status steps for factions that know it and whose values judge it (T-11-3); the change log |
| `recognition_event` (04.7.8), kind first, tier, hybrid, variant, fork, consolidation, confirm | with witnesses: reputation +1 on the calling's branch key per witness scope; an epithet from `epithet_seed` when 11.7.5 allows; a rumor; a chronicle line at tier 3+; with `institution` and answer `accept`: membership, rank rung 1 (V3) or the trial's rung (V9), the price's obligations as commitments (11.8.5), status +1 |
| `recognition_event`, answer `decline` with `decline_cost` | the institution's status −(the cost's amount); otherwise nothing |
| `recognition_event`, answer `defer` | nothing (04's standing offer persists; 11.8.3's expiry for ranks) |
| `recognition_event`, kind `fraying_stage` / `revocation` / `turn` | reputation on the oath's axis, negative pole, in the keeper's and institution's scopes (and witnesses'); an institution whose `values` admire that axis counts stage 2+ as a broken obligation (11.8.5) and a `revocation` as loss of its ranks (11.8.6) |
| `recognition_event`, kind `atonement` | reputation on the axis's positive pole in the keeper's scope; the restitution thread, if any, completes (04.9.4) |
| `recognition_event`, kind `lapse`, `release` | nothing public unless witnessed |
| `victory_over_pc` (07.6.2) | the victor grows (11.3.17); the reputation packet (11.7.2 item 3); a rumor (T-11-10); the change log (reactions read it) |
| setback facts (07.6.2) | the change log only (chapter 12's director reads them) |
| the rout's world cost (07.4.3) | the returned clock ticks; this chapter supplies faction goal clocks first among the candidates (`tick_sources` include `{on: rout}`) |
| the belief `pc.dead` (07.5.6) | the rumor and its effects (11.6.8) |
| a cache and its clock (07.6.4) | cache rumors (T-11-10); a quest thread to recover it (11.5.12) when the PC learns where |
| `lc.road_ends`, `career_end`, death (07) | retirement or legacy (11.13.1) |
| `cost.exposure` at S5 (01.13.6) | reputation (11.7.2 item 4); a rumor; the observer's faction learns the deed (11.3.11 known: true) |
| creation's hooks, long vow, faction ties, prologue (02.9, 02.11.2) | hooks (11.5.6); the long vow's thread; each faction tie: the faction of that `org` kind in the region (the seed's org-tie map, 12.16.10) gets status +1, or +2 and −2 for "sworn and hunted"; prologue lines appended |
| the venture record (10.2.2) | the reckoning (11.3.13) |
| a Nemesis result (09.9.3) | boasts as rumors (source `boast`); hunt clocks; victors' promotion (11.3.17) |
| chapter 12's chronicle offers (12.4.8–9) | accepted as entries (11.12.2) |
| chapter 12's random event (12.6.5) | a tick on a clock listing `random_event`; a situation seed → a situation (11.4.3) |
| chapter 15's exposed lies, broken deals, wrong accusations, service weeks | reputation (11.7.2 item 5); status steps (T-11-3) |
| chapter 16's departures, courting reports, ally deaths | reputation (11.7.2 item 6); a vow thread at an ally's death if sworn (11.5.12); personal threads (11.5.12) |

**PR-11-5 Making and activating a hook.** `[D]`
1. Make: write the thread at `seeded` with its text, source, the entities it names (unbound allowed), and
   how it reaches the PC (a rumor, a person, a letter) — a trace written at once.
2. Activate (the PC takes it up): bind entities, reusing first (11.5.6 step 1); generate the case (PR-15-6):
   ≥ 3 placements per necessary conclusion, ≥ 2 holder kinds, one core, reserves and fallbacks; rank
   (11.5.3); opposing clock if its source has a threat; reward if promised; fallback (11.5.7); progress
   clock public; weight 2; `activated_at`.
3. Audit: fewer than three placements in total is a content defect: generate placements until three exist
   and log a `rule_conflict` (12.8.4).

**PR-11-6 The epilogue.** `[D]` Steps 1–10 of 11.13.3, with 11.13.4–11.13.11; every computation from
state; the DM words only the period line, the legend rumors' texts and the apotheosis form's narration.

**PR-11-7 Birth of a rumor.** `[D]`
1. Find or write its `points_to` target (11.6.4); without one, no rumor.
2. Roll truth on `tbl.11.rumor_truth` by source (11.6.3); for partial or false, `tbl.11.distortion`.
3. Write the record, `origin` the settlement where the change is first known, `reached: [origin]`.
4. The DM words `text_seed` from the change, its truth and its distortion `[N]`; the claim check compares the
   words with the record (a second distortion, or none where one is due, is a `state` error).

**PR-11-8 Creating a faction.** `[D]`
1. Template by `org_tags` (11.3.18). Tier: data, `tbl.11.faction_tier`, or 11.3.3's rung.
2. Ratings from the template's distribution at that tier; hold strong; stage rising if new, flourishing for
   data factions unless stated; temperament, values, patron deeds, duties, fields, boons, rank ladder.
3. Seat and holds: data, or the region's settlement of the template's preferred tier.
4. Officers (one to four principal NPCs, 12.11.1; each a duty) and one to three linchpins, each with four
   fates written and **sealed now** from the template's fate list (11.3.10).
5. Goal: d6 on the template's goal list (kind and text), scope by tier, clock by scope (local 8, regional 12,
   realm two linked 12s), hidden with the template's omens, tick sources including `random_event` and `rout`.
6. Relations: 0 to all, then data's; status toward the PC 0 (or by a creation tie).

---

## Tables

Tables embedded in Rules are canonical in their data files and indexed here: **T-11-2** tier (11.3.3);
**T-11-3** status steps (11.3.11; `world_turn.yaml#status_steps`); **T-11-4** entanglements (11.3.12;
`factions.yaml#tbl.11.entanglement`); the agenda (11.3.7; `factions.yaml#agenda`); the actions (11.3.6;
`factions.yaml#actions`); **T-11-10** traces (11.6.2); **T-11-11** rumor truth (11.6.3;
`world_turn.yaml#tbl.11.rumor_truth`); **T-11-12** spread (11.6.5); **T-11-17** world changes (11.9.7);
the endings (11.13.2; `legacy.yaml#endings`). The tables below are defined here.

**T-11-1 Optional fields this chapter adds to its data files** (SCHEMAS.md requires only the core
fields; these are documented here per SCHEMAS.md's preamble).

| File | Optional fields |
|---|---|
| `factions.yaml` | `templates` [{id `ftpl.*`, org_tags, temperament, values, patron_deeds, ratings_by_tier, rank_ladder, duties, fields, boon_base, boon_signature, goal_list, goal_omens, attention_omens, fate_list, courtable}], `agenda`, `actions`, `rank_ladders`, `tbl.11.entanglement`, `tbl.11.vacuum`, `tbl.11.faction_seed`, `tbl.11.faction_tier`, `minor_goals`; per faction: `patron_deeds`, `values`, `temperament`, `stage`, `full`, `seat`, `holds`, `officers`, `duties`, `relations`, `attention`, `pursuit`, `ranks`, `sittings`, `fields`, `boon_base`, `boon_signature`, `courtable`, `template` |
| `world_turn.yaml` | `logged_patterns`, `season_steps`, `status_steps`, `attention`, `reactions`, `deed_families`, `situation_templates`, `traces`, `spread`, `tbl.11.rumor_truth`, `tbl.11.distortion`, `tbl.11.epithet_forms`, `tbl.11.hook`, `tbl.11.fallback_form`, `tbl.11.land_changes`, `tbl.11.season_events.*`, `phenomena`, `thread_ranks`, `thread_sources`, `world_changes`, `improvements`, `caps` |
| `calendar.yaml` | `quarter_days`, `months`, `moon`, `lifespans`, `aging`, `festival_effects`, `era` |
| `legacy.yaml` | `seams`, `apotheosis_forms`, `legend_ranks`, `ledgers`, `ledger_results`, `successor_sources`, `tbl.11.successor_traits`, `train_successor` |

**T-11-20 Legend ranks** (canonical: `legacy.yaml#legend_ranks`).

| Rank | Name | Computed when (first match from the top) | Legend rumors | Place of the legend | Epithets made permanent |
|---|---|---|---|---|---|
| 5 | a myth | a realm entry of score 5, and the ending `apotheosis` or an epic thread completed | 3 | yes | all of score ≥ 3 |
| 4 | a legend | a realm entry ≥ 4; or a region entry 5 and a calling confirmed at tier 5 | 3 | yes | all of score ≥ 3 |
| 3 | famed | a region entry ≥ 4, or a realm entry ≥ 2 | 2 | yes | all of score ≥ 3 |
| 2 | known in the region | a region entry ≥ 2, or breadth ≥ 3 | 2 | for `apotheosis` and `remembered` | all of score ≥ 3 |
| 1 | a local name | renown ≥ 1 | 1 | no | all of score ≥ 3 |
| 0 | unremembered | renown 0 | 0 | no | — |
`apotheosis` adds one rank, to 5 at most.

**T-11-21 Legacy ledger results** (canonical: `legacy.yaml#ledger_results`; d20 + ledger: strong ≥ 20,
opportunity 12–19, trouble ≤ 11).

| Ledger | Strong: something concrete | Opportunity | Trouble (a hook too) |
|---|---|---|---|
| **Deeds** | one bequeathed thread keeps its full progress; or an institution that held the predecessor at rung 2+ offers the successor rung 1 at once (an open V3 offer) | the bequests at half progress (11.13.6); one hook from the predecessor's unfinished business | a foe has grown: the faction or NPC most hostile to the predecessor gains pursuit +1 toward the successor (or a Nemesis promotion, 09.9.3); or an obligation the predecessor owed falls to the successor (a commitment of kind debt) |
| **Bonds** | an ally or bond NPC of the predecessor serves the successor at its old standing − 1 (16.16.2), and one faction at +2 or more toward the predecessor is +1 toward the successor even for a stranger successor | one of the predecessor's bond NPCs becomes the successor's anchor bond (02.9.2's standing for the relation) | someone who loved the predecessor blames the successor: a thorn bond (rival −1 or enemy −2, 02.9.2); or the successor rejects one of the predecessor's values (the player names a creed of theirs that is the predecessor's inverted: a drive) |
| **Discoveries** | the predecessor's map: every place they discovered in the region is discovered by the successor; their hidden room or cache passes to the successor | one meaningful place known to the successor, with one sealed fact of it unsealed | what the predecessor found bites back: a situation from the place they last opened (the thing they woke stirs); or an enemy faction learns the predecessor's paths (its next strike or hunt finds the successor's haven) |

**T-11-24 Simulation results** (`rules/_process/simulation/11-world-sim.py`, output beside it; 300 seeds ×
104 weeks; four full factions — tiers 2, 1, 3, 1, two at war, one feud — three petty factions; the PC pursues threads 70% of
weeks; p10 / median / p90 per two years). **Re-run at integration** (issue I-026): the script's `gain_hold()` now
follows 11.3.4 (rising above tier 3 needs a completed realm-scope `grow` goal; any other gain at tier 3+ only
strengthens the hold), and its AGENDA carries 11.3.7's `steadfast` row; the numbers below are the re-run's, with every
random draw seeded so the output reproduces exactly (the
first version let `expand` raise tier-3+ factions and reported tier 5 in 7–8% of faction-runs) [integration: I-026].
**Re-run for I-032** [revision: I-032]: the script's agenda is now 11.3.7 cell for cell — the three overrides first
(slip, war on a d6 of 1–3, `aid_pc`), each row's own condition (a failed one reads as `goal`), the target ladders,
and `court`, `aid_pc` and `lie_low` with their 11.3.6 effects — where the first version read several rows as `goal`
and let steadfast strike at −2. `recover` uses its 11.3.6 DC. The figures below are this re-run's.

| Measure | Engaged PC | PC at war with one faction | No PC (a timeskip) |
|---|---|---|---|
| faction goals completed (region) | 13 / 15 / 18 | 13 / 15 / 18 | 13 / 16 / 19 |
| goals completed per faction | 2 / 4 / 5 | 2 / 4 / 5 | 2 / 4 / 5 |
| tier rises / tier falls | 5 / 5 (medians) | 6 / 5 | 5 / 5 |
| collapses (a vacuum filled) | 1 / 2 / 2 | 1 / 2 / 2 | 1 / 2 / 2 |
| strikes / strikes that landed | 17 / 9 (medians) | 16 / 9 | 16 / 8.5 |
| entanglements + moves on the PC | 0 + 0 (p90 0 + 1) | 0 + 0 (p90 4 + 2) | 0 |
| hooks seeded | 54 / 59 / 65 | 54 / 59 / 65 | 51 / 55 / 58 |
| threads taken up / completed / failed | 33 / 19 / 11 (medians) | 32 / 19 / 11 | — |
| hooks expired untaken | 18 / 23 / 28 | 18 / 23 / 28 | 47 / 50 / 54 |
| situations created | 8 / 12 / 16 | 8 / 12 / 16 | 9 / 13 / 16 |
| traces emitted (rumors, news, omens) | 234 / 249 / 267 | 233 / 250 / 268 | 241 / 257 / 273 |
| most open matters known at once | 8 / 9 / 10 | 8 / 9 / 10 | 6 / 7 / 8 |
| weeks the PC knew fewer than three | 3 / 4 / 5 (of 104) | 3 / 4 / 5 | — |
| bang queue at its fullest | 1 / 1 / 2 | 1 / 1 / 2 | 0 |
| faction turns by action (11.3.7) | goal 67.6%, recover 9.4%, court 6.0%, expand 5.4%, strike 4.4%, scheme 3.9%, aid_pc 3.2% | goal 67.3%, recover 9.7%, court 6.0%, expand 5.4%, strike 4.4%, scheme 4.0%, aid_pc 3.0%, move_on_pc 0.2%, lie_low 0.1% | goal 70.0%, recover 10.1%, court 6.1%, expand 5.3%, strike 4.3%, scheme 4.0% |
| the Wardens–Cult war (relation −3): week the Cult collapsed | 5 / 10.5 / 35 (104 = still standing) | 5 / 12 / 44 | 6 / 10 / 38 |
| final tiers (start mean 1.75) | mean 2.37; highest tier reached 3; tier 5 in 0% of faction-runs | mean 2.38; 0% | mean 2.41; 0% |

*Reading.* The world produces a steady stream: about one faction goal every seven weeks in a region, about
two and a half traces a week, a new hook every twelve or thirteen days, and a new situation every eight or nine
weeks, whether or not the PC acts. Two faction turns in three go to the faction's own goal; the rest go to rivals,
to itself and, when its status allows, to the PC. The PC's register never empties (fewer than three known matters in four weeks
of 104, each then refilled by the supply rule) and never floods (at most ten). Escalation is bounded: tiers
drift up by about 0.6 over two years while the weight of size, strikes and collapses pull them down, and no
faction passes tier 3 in two years, because rising above it needs a completed realm-scope grow goal (11.3.4).
**War is decisive:** override (b) has two tier-1 neighbours at relation −3 strike each other on half their turns,
so the Ember Cult falls at a median week 10–12 (p90 35–44) and the Ash Wardens in about half the runs; each
vacuum is refilled by a rising faction (11.3.9). Because this model's hostile faction is the Cult, its "PC at war"
column mostly measures a war that ends early (entanglements p90 4); the Thallen re-run, whose hostile faction
stands, gives 8 entanglements in two years (p10 5, p90 11), about one every thirteen weeks and never a pile-up
(the queue held two at most) (`13-world-sim-output.txt`) [revision: I-032]. An earlier draft with goal ticks of 3/2/1 completed goals every eight weeks per faction and
drove 47% of factions to tier 5 in two years; the halved ticks, scope terms and the weight of size are what
fixed it (DL-11-03, DL-11-06).

---

## Worked examples

All examples follow **Wren** (00's continuous character) in a region of the West Marches shape (10.2.4; the world seed's, 12.16).
Places, factions and NPCs are *illustrative; the region's seed owns the content*; every mechanic of this chapter is
exact. Dice are the engine's.

The region (*illustrative*): **Ashford** (a town, the haven; seat of the Salt Guild), **Harl's Crossing**
(a village a day east; seat of the Ash Wardens), **Ditchling** (a village a day north), the **Cinder Shrine**
(a hill site two days east; seat of the Ember Cult). Neighbors: Ashford–Harl's Crossing (4 watches),
Ashford–Ditchling (4), Harl's Crossing–Cinder Shrine (8).

| Faction | Tier / hold | Ratings (force, cunning, wealth, sway) | Temperament / stage | Goal (clock) | Status to Wren | Relations |
|---|---|---|---|---|---|---|
| `fac.salt_guild` | 2 / strong | 1, 2, 3, 2 (sum 8) | mercantile / flourishing | "Corner the Salt Road" — regional, wealth, 7/12, hidden | −1 Wary; attention 3/8 | Wardens −2 |
| `fac.ash_wardens` | 1 / strong | 3, 1, 0, 2 (sum 6) | zealous / rising | "Burn the Cinder Shrine" — local, force, 5/8, hidden | +2 Friendly | Guild −2; Cult −3 (war) |
| `fac.ember_cult` | 1 / strong | 1, 3, 1, 1 (sum 6) | secretive / rising | "Wake the Ember in the Hill" — local, cunning, 6/8, hidden | −2 Unfriendly; attention 5/8; pursuit 0 | Wardens −3 (war) |

### WE-11-1 A World Turn in full, with three factions

*Spring, year 2, week 6; the `week` boundary at dawn. Wren is in Ashford.* The change log holds: Wren's
`public_deed` from three days ago ("pulled a carter from the cult's pyre at the Cinder Ford"; noteworthy;
conduct `conduct.mercy` +4; carriers: two carters whose home is Ashford), and a bribe she paid a Guild tally
clerk at night with no witness (a fact, no carrier).

**Phase 5 (before the World Turn).** `h.00.clock_auto`: the Guild's attention clock had no tick this week →
decays 3 → 2 (no omen on decay). The cult's attention clock ticked at the venture's reckoning on Wren's
return (loudness *contained* — a carried deed against it — +1, Hostile? no, −2: no extra) → no decay; it
stands at 5/8.

**Step 1 — Elapse.** The log is closed with 2 entries. Turn stamp {2, spring, 6}. Wren is not on a venture.

**Step 2 — Maintain.** Wren's cottage has no yield. No linchpin fact was set. No slips.

**Step 3 — Timelines.** The situation **The Mill Feud** (cadence week) has step 2 `at: after 3 weeks` from its
start in week 3: it fires. `key_delta`: `npc.miller_son.held_by = fac.salt_guild`; trace: news in Ashford,
"the Guild's factor has jailed the miller's son for unpaid tolls". Its step 3 (`at: after 6 weeks`, "the mill
is sold to the Guild") is `prevented_by: npc.miller_son.freed`.

**Step 4 — Faction actions,** full factions by tier then id: the Guild (2), then the Wardens and the Cult (1; `ash` <
`ember`).
- **Salt Guild.** Overrides: no slip; no war; status −1 (no `aid_pc`). Agenda d6 = **3**, mercantile → `court`.
  Target ladder: (i) an ally of Wren's with a tie to `org.guild.merchant` at Warm or lower: **Dunn**, her porter
  (Warm; his father was a Guild carter), the Guild is `courtable` and its status ≤ 0 → Dunn. Check: sway 2 +
  2 × 2 + 0 = **+6** vs `10 + 2 × 2 + 3` = **17**. d20 = 14 → 20, margin +3: **success**. `courted_by:
  fac.salt_guild` on Dunn (sealed); 16's omen is owed.
- **Ash Wardens.** Override (b): at war with the Cult, whose seat is in the region; d6 = **2** ≤ 3 → `strike`
  the Cult. The Cult holds only its seat → the target is the seat (+2). Check: force 3 + 2 × 1 + rising 1 =
  **+6** vs `10 + max(1, 3) + 2 × 1 + 2` = **17**. d20 = 15 → 21: **success**. The Cult **loses hold**: strong →
  weak. Its relation toward the Wardens −1 (already −3; clamped).
- **Ember Cult.** Overrides: none. Agenda d6 = **3**, secretive → `move_on_pc` (status −2 ≤ −1 ✓; attention 5/8 ≥
  half ✓). An entanglement: column pursuit 0 (+0: not Hostile) → "0–1"; row d6 = 4 + 1 (status −2) = **5** →
  **Snare**: a false plea for help that leads to a place it holds (threat, intensity 3, specificity `faction`,
  ways out: see through the plea; go in prepared; send someone else; ignore it, and the pleader is real next
  time). Queued.
- **Petty:** the Ditchling Reeve's men roll d6 = 5 → +1 on their 6-clock (3/6).

**Step 5 — Consequences** (the closed log, in order).
1. *Wren's rescue.* Reputation first (11.7.3): its key is `conduct.mercy:+` (magnitude 4 ≥ 2). Ashford's entry
   had 2 points → **3: score 2**; it now holds two noteworthy packets on the key → an **epithet**: d8 = 4, form
   "the one who <did it>": *the one who pulled the carter from the coals*; `pc.epithet.ashford` written. Valence
   in Ashford (the Guild's seat; Guild values admire `conduct.generosity`, despise `conduct.honesty:-`):
   **neutral** there. Then reactions: family *a rescue* (`[J:enum]`, the deed line's literal act). `wr.rescue`
   candidates: "the carter's kin owe you a favor" (npc, 3), "the cult marks the one who robbed its pyre"
   (pc_deed, 2), nothing (2). Highest specificity present: pc_deed → the mark (2) against nothing (2): d4 = **1** →
   **the mark**: the Cult's attention +1 → 6/8.
2. *The bribe.* `[J:flag]` known to the Guild? No carrier, no aftermath link, nothing told → **false**. No
   status step; the entry stays in the log, re-tested if a link appears.
Two changes, two reactions considered, one fired (cap six: not reached).

**Step 6 — Attention.** The Cult's clock 6/8: remaining 2 ≤ max(1, 8 ÷ 4) → **imminent**; the tick renders its
omen: *"your door's latch has been tried in the night"*. No completion. The Guild's 2/8: no change.

**Step 7 — News and rumors.**
- The Wardens' strike: a rumor (`eyewitness`), born at Harl's Crossing and at the Cinder Shrine. Truth d10 = 8 →
  **partial**; distortion d6 = 4, *how many*: "the Wardens burned the whole shrine to the ground" (they fired
  its outer hall). `points_to`: the shrine's outer hall, burned (a placement that shows the truth). Visible
  change: smoke-black on the shrine's eastern wall.
- The Mill Feud step: news in Ashford (true).
- Wren's rescue: a rumor (`eyewitness`) born in Ashford, truth d10 = 3 → **true**, points to the carter himself.
- Dunn's courting: no public trace; 16's omen (*Dunn comes back late from town with the Guild's wine on his
  breath*) is owed at his next scene.
- Spread: last week's rumors move one step (the price of salt rising in Ashford reaches Ditchling).
- Reached Wren's settlement this turn: the mill news; the rumor of her own rescue.

**Step 8 — Queue.** Queue: the Snare (faction). No `pc_deed` or `npc` bang is queued, and Wren has an open
anchor bond untested for six scenes (her sister Maren) → a **kicker**: "word from Maren — she needs you at the
temple" (social 1, npc). Register: "The Missing Ferryman" (active, last progress 9 days ago): fine. Wren knows 5
open matters → no supply hook. Week 6 is not week 12: no herald.

**Phase 9.** `h.11.world_record`: no line qualifies (no linchpin, collapse, war begun or ended, tier-2+ goal
completion, concluded situation, or place changing hands); the week passes unrecorded.

**What the DM narrates** (from the returned list only): the latch tried in the night (the omen); in the
morning the market talks of the miller's son jailed (news) and, half-embarrassingly, of "the one who pulled the
carter from the coals" (Wren's own rumor). Nothing about the Wardens' strike reaches Ashford until next week; the
Snare and Maren's word wait for chapter 12's pacing director.

*Boundary pair.* Had the Cult's d6 shown **4** — secretive row 4, `lie_low` if its attention is **imminent** —
the condition fails (it was 5/8, *building*, when the action was chosen) → `goal`: cunning 3 + 2 + 1 = +6 vs
`10 + 2 + 3` = 15; d20 = 9 → 15, success → "Wake the Ember" 7/8 (imminent: an omen, *"the hill's springs run
warm"*). *Non-example.* The DM, knowing about the bribe, has the Guild "start asking questions": no row fires on
an unknown deed, so nothing happens; the claim check would flag such narration.

### WE-11-2 A thread from seeding to resolution

*Week 9.* Wren killed the cinder drake of the Tangle last week (a resolved Strike, witnessed by two Warden
scouts). Step 5's reaction to `great_beast_slain` fired "a rumor of the clutch" (pc_deed). It writes a hook,
**The Last Egg**, and a rumor: "the drake was the last of its clutch" — source `eyewitness`, truth d10 = 10 →
**false** (one egg survives in the lair). `points_to`: the cracked shell in the lair's back chamber (a placement
that refutes it).

1. **Seeded → heard.** Wren Asks around in Harl's Crossing (15.13.9): she hears the rumor (journal: its text).
   The hook is seeded and known (she now knows 5 matters).
2. **Activated.** She says she'll go back to the lair "to be sure". PR-11-5: entities bound, reusing first — the
   wyrm-cult elder **Oskar Venn** already exists (met in week 4) → bound as the `against` party. Case: one
   necessary conclusion ("an egg survives and the cult means to hatch it") with **three placements** of **three
   kinds**: a hunter's boast in Harl's Crossing (person, core), the cracked shell (object, in the lair), the
   cult's tithe ledger (object, at the Cinder Shrine); a reserve (a charcoal-burner who saw cultists on the
   lair path); fallback: an acolyte seeks Wren out to sell the elder out. **Rank** `[J:rung]`: a few obstacles
   across a venture, real risk → **dangerous**: progress clock **6**, public. **Opposing clock**: "The Egg
   Hatches", countdown 8, sensed, +1 at each `week`, omens (stirring: *"the hill's springs run warm"*).
3. **Progress.** Week 10: the hunter's boast (core clue) → +1 (1/6). At the lair: Observe, success at Standard
   reach (delivered 2) → 3/6 = **half: flashpoint** (`trg.11.flashpoint`): chapter 12's next scene for the thread
   must unseal the next sealed fact or bring Venn on stage — he arrives at the lair mouth with two acolytes. Week
   11: two scenes pursuing it with no tick (Wren chases the acolytes and loses them); `h.11.fallback_counters`
   stands at 2. The third scene: Wren takes the tithe ledger from a fleeing acolyte (core clue +1 → 4/6). The
   counter resets.
4. **Climax.** Week 12, with "The Egg Hatches" at 5/8: in the egg chamber, Wren's Strike on the egg — success,
   Great reach by an Amplifying lever (the cracked shell's weak seam, a fact) → delivered 3 → **6/6: completed**,
   before the countdown. The countdown is **voided** (00.8.5).
5. **What completion writes.** `thread_completed` (01.16.2: fate +1, to 2). Status: the Wardens are the patron
   (they asked her to be sure) → +1 (dangerous: small) → **+3 Devoted**; the Cult: a thread completed against it
   (`against` is its elder) → **−2** (weight) → −3 Hostile (capped at 2 per turn: fine). Chronicle: a dangerous
   thread earns no line of its own; chapter 12's scene-end line for the scene is accepted ("Wren of Ashford broke
   the last drake egg in the Tangle"). The false rumor stays false and keeps circulating until it fades; anyone
   who repeats it is simply wrong.

*Boundary pair.* Had Wren stayed in Ashford from week 12, "The Egg Hatches" would have completed first (8/8 at the
World Turn of week 15) and voided the thread [verification: V2b-014]: **failed**; its `on_complete`: a young drake (T2) and the situation **The Hunting Ground** in the
Tangle; news in Harl's Crossing; the Wardens' status unchanged (Wren had not accepted a commission from them, only
told them her plan). *Non-example.* Narrating "you find the egg; it's dead already" to wrap the thread up: the
clock decides completion, and a sealed fact (the egg is alive) cannot be contradicted.

### WE-11-3 A thread that expires (and one that cannot)

- **A hook untaken.** Week 10: the supply rule had nothing personal and no faction job, so it rolled
  `tbl.11.hook` (Ditchling, village): **The Drowned Bell** ("the old chapel's bell rings under the millpond on
  still nights"), delivered as a rumor heard in Ditchling's tavern. Wren never takes it up. At week 18 (8
  weeks) step 8 marks it **expired**: its rumor's truth becomes `outdated`; its patron's `if_unmet` runs — the
  Ditchling priest hired two divers from Ashford, and news says the bell was raised. Cost to Wren: nothing.
- **A quest left to lie.** Wren had taken "The Tax-Collector's Ledger" for the reeve of Ditchling (troublesome,
  1/4) in week 5, then never touched it. At the World Turn of week 18 — thirteen weeks with no progress, not
  protected (last progress 30 scenes ago; not a vow) — it **expires**: the reeve "found someone else" (news); no
  status step (expiry is not failure).
- **A vow that waits.** Wren's long vow, "Find who burned the ferry" (02.9.1), has had no progress in a year. It is
  a vow: it never expires; it waits in the register (and chapter 12's rotation keeps offering it a scene).
*Non-example.* Expiring a quest that Wren progressed eleven scenes ago because a season has passed in fiction: the
protection (12 scenes) holds; the rule counts both.

### WE-11-4 A season boundary

*Spring, year 2 ends.* **Week 12's herald** (`[SEASON]`, out of fiction): "At the turn of the season: your second
step as a ranger awaits confirmation (04); your seat as a sworn Warden is provisional — a week of service is due;
the late frost will lift; *Ford-arrow* is fading in Ditchling." In fiction: the first warm rain. Wren spends week 13
serving at the Wardens' hall (15.13.12): her rank obligation is kept.

**The boundary** (00.7.6: `week` then `season`; phases 1–9 of the season boundary).
- Phase 6, `h.10.weather_regime` (summer's table), then **`h.11.season_turn`**:
  1. *Calendar:* summer's quarter day, a festival with `market` and `sitting`.
  2. *Factions:* the Guild has spent 8 Season Turns flourishing → **entrenched** (−1 on goal and expand, +1 to its
     defense). The Wardens completed "Burn the Cinder Shrine" in week 11 → rising → **flourishing**. The Cult lost
     hold twice this season (the strike of WE-11-1, then the Wardens' completed goal, a `dominate`) and fell to
     **tier 0**, hold strong; being **rising**, it does not decline (that row reads flourishing or entrenched), but
     one more lost weak hold at tier 0 collapses it (11.3.4). The margrave (tier 3) rolls the weight of size: d20 13 + 4 − 1 (entrenched) =
     16 vs `10 + 6` = 16 → holds. Cooling: the Wardens and the Cult exchanged a strike → stay at war. The Cult's
     pursuit was 0. **Ranks:** Wren's rung 2 (provisional) — every obligation kept → **confirmed**. The Wardens'
     **sitting**: rung 3 (officer; seats tier + 1 = 2, one held by Captain Odo, one free) — status +3 ✓, her
     mercy entry in Harl's Crossing has score 3 ✓ → an **offer** of rung 3, *Warden-sergeant*, at the sitting, by
     04's protocol, price `obligation`. The Wardens at +3 have not given a favored gift this year → `gift_due.
     fac.ash_wardens` (favored; 08 places their boon signature `prop.bane_fiend` on a masterwork base).
  3. *Situations:* five active in the region; under the cap.
  4. *Seasonal events:* `tbl.11.season_events.summer`, d12 = **2** → the phenomenon **bandit summer** (provisional):
     route links of the Marches at danger +1 rung for the season, and a situation from template *road of knives*.
     Review of spring's phenomenon **late frost**: no `confirm_when` → **retired** (news: the frost has lifted).
  5. *Threads:* none to retire.
  6. *Reputation:* Ashford's `conduct.mercy:+` entry is score 3 → the Marches region gets an entry at **1**
     (3 − 2). Ditchling's *Ford-arrow* (`deed.martial`, score 1, no point in four seasons) **fades** to 0 (kept in
     sources; no longer said).
  7. *Holdings:* Wren's cottage has no yield.
  8. *Seams:* no thread of rank formidable or higher completed this season; no seam.
  9. *Record:* the spring digest: "Spring, year 2: the Wardens burned the Cinder Shrine's hall; the last drake egg
     was broken in the Tangle; the Guild jailed the miller's son."
- Phase 8: `h.04.season_consolidation` confirms Wren's tier 2 (04's V10, "the body remembers"), reading a world
  already settled; `h.00.reflection` fires; 04's recognition pass and standing offers run, and chapter 12 stages the
  Wardens' sitting offer at the summer quarter-day festival.

*Boundary pair.* Had Wren skipped her week of service, the Season Turn would have **lapsed** her provisional rung 2
back to rung 1, and the sitting's offer would not arise (rung 3 needs rung 2 confirmed). *Non-example.* Confirming
the rank mid-season "because she's clearly earned it": nothing in this chapter confirms or retires outside the
boundary (11.11.1).

### WE-11-5 Retirement → timeskip → successor

*Autumn, year 6.* Wren (ranger, tier 4 confirmed; Warden-sergeant, rung 3; a cottage in Ashford and a workshop in
Harl's Crossing) completes her long vow: the ferry was burned on the Salt Guild's orders (a formidable thread,
completed in the season's last week). `vow_kept` (fate +1). At the season's reflection, **two seams** hold (the long
vow kept; a formidable thread completed at a seam): the `[RETIRE]` offer. The player accepts; ending **patron**
(she holds a rung-3 rank and holdings).

1. **Settlement.** Estate: coin 412 + half the price of her priced items 180 + holdings at buy price (cottage 150,
   workshop 400) = **1,142**; the workshop's average net yield is 8 a week → + 104 × 8 = 832 → **1,974** ≥ 1,456 →
   *comfortable*; she lives in her own cottage → one rung up: **wealthy**. Both holdings **persist** (the
   workshop has staff 1; she lives in the cottage).
2. **Legend.** Entries: Ashford `conduct.mercy:+` **4**; Harl's Crossing `deed.martial` 3; the Marches region
   `conduct.mercy:+` 2; no realm entry. Renown 4; breadth 3. Rank: region ≥ 4? no; realm ≥ 2? no; region ≥ 2 → **2,
   known in the region**. Two **legend rumors** (legend row): d10 = 5 → **partial**, distortion *how many*: "she
   pulled forty carters from the coals" (one), pointing to the carter's family in Ashford; d10 = 9 → **false**,
   distortion *what*: "she was the cult's own priestess before she turned on them", pointing to the Cinder
   Shrine's ledger, which refutes it. **Permanent epithets** (score ≥ 3): *the one who pulled the carter from the
   coals*; *Harl's Arrow*. A place of the legend? Rank 2 and ending `patron` → no. **Period** (`[N]` for its line):
   "The Ashford years: the shrine, the egg and the ferry's ashes (years 2–6)", with four events by weight: the
   ferry vow kept; the drake of the Tangle slain; recognition at tier 4 before the Wardens; the road to the charcoal
   camps built.
3. **Threads.** "The Guild's Hand" (formidable, 5/8, against the Guild) → **bequeathed**; Dunn's personal thread
   (2/6) → **left to the world**; "Salt in the Wells" (troublesome, 0/4) → abandoned (no cost).
4. **Structural retirement.** Her ranger calling and its tiers and picks (04.11.4), her abilities, slots and Focus
   (05), her licenses and competence, her fate: **retired**. Her Warden-sergeant seat is **freed** (the Wardens
   will fill it at their next sitting). The Cult's attention on her ends with her career.
5. **Wren becomes an NPC:** principal, at her cottage, *wealthy*, a patron; band 4 (above any successor's: never
   retinue).
6. **Timeskip:** the player chooses **one year**. 52 World Turns, 4 Season Turns and a Year Turn run. In digest:
   the Salt Guild, by now tier 3 and entrenched, fails its weight-of-size roll once (a weak hold) and drops to tier 2
   when the Wardens strike that weak hold in the winter (11.3.4; the roll applies only from tier 3) [verification: V2b-014]; the Cult wakes the Ember in the Hill (its goal completes: a situation, *the rite*);
   "The Guild's Hand"'s opposing clock ("the Guild buys the ferry landing", 8) reaches **7/8 and stops** — the
   bequest is a crisis waiting; Wren, 35, makes no aging check.
7. **Successors** (sources in order): (1) **Tamsin**, the freed carter's daughter Wren trained for 8 weeks
   (Train-a-Successor: 8 ticks → two tags banked, `deed.wilds.tracking` and `deed.martial.archery`) — tie: the
   Caravaners' Compact +1 toward her; thorn: the Guild's factor −2 toward her (recorded); (2) **Dunn**, Friendly
   ally — tie: the Salt Guild +1 (courted); thorn: owes a creditor 30 coin (a commitment); (3) **Maren**, Wren's
   sister (anchor bond) — tie: Ashford's temple +1; thorn: none recorded → `tbl.11.successor_traits` d8 = 5: *a
   rival at the market* (a thorn bond −1). Plus the newcomer.
8. **Ledgers.** Deeds: thread rank points 3 + 8 + 6 + 3 (the vow) = 20, + 2 (the road) = 22 ÷ 3 = **7**. Bonds: 5
   NPCs at Friendly or Devoted + 2 factions at +2/+3 = **7**. Discoveries: 14 places ÷ 3 = 4 + 3 sites cleared + 2
   (one world change) = **9**. Rolls: Deeds d20 = 9 → 16, **opportunity**: the bequest at half progress; Bonds d20 =
   14 → 21, **strong**: Dunn serves the successor at Warm (Friendly − 1), and the Wardens are +1 to any successor;
   Discoveries d20 = 1 → 10, **trouble**: what she found bites back — the Ember the Cult woke stirs under the hill
   (the situation *the rite* gains a step aimed at Harl's Crossing).
9. **The player picks Tamsin.** Inheritance: **renown** — Ashford's mercy entry is 4 ≥ 3 and Tamsin's home is
   Ashford → a `legacy` entry at **score 1** ("Wren's girl"); **heirloom** — the Ember-Fang Charm (its fire ward
   and scent lever kept; attunement reset); **training** — two backstory tags at 24 points each (03.2.8); **Wren**
   as an NPC at standing **+1** (mentor, 02.9.2) and her V2 mentor-to-be; **standing** — a protégé: each faction's
   status toward Wren moved one step toward 0 (Wardens +3 → +2; Guild −3 → −2; Cult −3 → −2); **home** — Wren still
   lives in the cottage: a haven for Tamsin, hers at Wren's death; **purse** — 10 weeks of *wealthy* = 350.
10. **Hand-off.** Tamsin is made by 02.2.7: the floor, an empty calling partition, fate 1. The queue is refilled:
    "The Guild's Hand" (Tamsin's, 2/8 — half of 5, rounded down; its opposing clock at **7/8**), the rite's new
    step, Dunn's arrival, and Wren's visit in Tamsin's second scene. The chronicle gains the retirement entry, the
    period and its events. Sessions later, when Tamsin starts tracking the Cult through the Tangle, it is Wren who
    notices.

*Boundary pair.* Had Wren died at the Cinder Ford instead (a Last Stand), the ending is **remembered**: no
settlement for her (her estate passes only through the purse and heirloom channels); legend rank 2 with
`remembered` → a **place of the legend** (a cairn at the ford, written into the graph); her allies grieve (16.9.5);
the same successor procedure follows. *Non-example.* Starting Tamsin "a little ahead because she trained with a
legend" (a +1 competence, a tier): forbidden (02.2.7); what the training buys is evidence, which she still has to
live up to.

---

## Edge cases & adaptation anchors

**Anchors of this chapter** (`Anchor: yes`, for chapter 12's index): **11.3.15 Muster and clash** (lead, hold
the line, storm, besiege; knobs `targets`, `time_cost`, `dc`, `reach_unit`) and **11.9.7 Great project: the world
change** (build, found, clear for good, unite, bring down, change the law; knobs `time_cost`, `targets`,
`reach_unit`). Reach for the rest of this chapter's machinery like this:
- **Anything a group does over time** → a faction check (11.3.5) against a clock: a village raising a palisade, a
  mercenary company's siege, a guild's boycott. Two-change limit (00.2.7): the rating and the DC term are the
  usual knobs.
- **Anything the world would do if no one stopped it** → a situation (11.4.1) with a timeline of observable steps
  and `prevented_by` facts. A flood coming down the valley is a situation of cadence `day`.
- **Anything the world says about someone** → reputation (11.7) for weight, a rumor (11.6) for words. A false
  accusation against an NPC is a planted rumor about them (11.6.9).
- **Anything someone owes** → a commitment (11.4.9) with satisfaction and violation conditions, and a thread if
  pursuing it takes more than a scene.

**Cases.**
- **The PC joins a faction that is hostile to another the PC is Friendly with.** Statuses are separate records;
  the second faction moves only by known deeds (T-11-3): joining is not itself a deed against it, but service
  against it in its scope is (a row "helped its rival").
- **The PC plays both sides.** Each faction reacts only to what it knows (11.3.11); a scheme by either may
  unseal the other (11.3.6), which is how double-dealing comes out — by the dice, not by the DM's sense of justice.
- **A linchpin dies of something the PC did not do** (a rival's strike took an officer, the aging Oracle). The
  fate fires all the same (11.3.10); the status steps of T-11-3 apply only when the PC's hand is in it.
- **The PC kills every member of a faction.** A tier-0 faction losing its last members collapses (11.3.9 by fiat
  of fact: no members, no faction); any larger faction loses hold per strike of the PC's that its fielded people
  suffered (a massacre at its seat is a `strike` at the seat by the PC, critical success), and its rank and file
  regenerate by tier. Factions are not hit-point bags; their tier falls by hold.
- **The PC wants to found a religion, a guild, a kingdom.** `establish` (T-11-17), then rulership (11.9.8); the
  domain climbs tiers only by its own goal completions and holds, like every other faction.
- **The PC is captured by a faction that is Friendly to them** (a misunderstanding, a writ). Captivity is 07's;
  the faction's contract (+2: it helps when the cost is not serious) makes release an R1-sized request to its
  officers (15).
- **A rumor is true about something sealed.** A rumor's `points_to` must lead to a placement the case's gate
  allows; the rumor never unseals the fact itself (11.6.4; INV-10).
- **A faction would act on the PC while the PC is in a timeskip or captive.** `move_on_pc` reads as `goal` in a
  timeskip (11.2.6); a captive PC is acted on by the captor's clocks (07.6.3), not by World Turn moves of other
  factions (their bangs wait in the queue).
- **Two factions' goals are mutually exclusive** (both want the same ferry). Their goal clocks are linked as racing
  clocks when created (00.8.5); the first to complete voids the other, which gets a new goal.
- **The player asks out of fiction "what is the Guild up to?"** The codex shows what is available: the faction's
  existence, status rung name, its seat, and the traces the PC has seen; never its goal or clock (sealed; 00.6.3).
- **The PC asks an NPC about a faction's plans.** The NPC knows only by 12.10.6 (a member may know its goal by its
  role: an officer knows; rank and file know the omens).
- **A keeper's faith (05.7.4).** Where a divine keeper is a faith with a faction record, "standing with the keeper's
  faith" is that faction's status toward the PC (11.3.8); where the keeper is a power without a faction, 04's
  bonded-witness rules and 05's regard govern alone.
- **Holdings in a region the PC never visits.** The steward's yield takes the absentee snag after a season
  (11.9.3); Hostile factions may strike it (11.9.5); the PC hears by news.
- **A successor wants to be the predecessor's rival.** The Kingdom shape allows it (source 5); the ledgers'
  trouble "the successor rejects one of the predecessor's values" is the mechanical form.
- **The player retires and immediately wants the old character back.** The retired PC is an NPC (11.13.7); it may
  be persuaded to help, by 15's rules, at its fixed standing; it never takes a player's turn again.
- **A world reaction would harm the PC directly** (an assassin's poison in the cup). Reactions and the World Turn
  may only queue a bang (11.2.4); the assassin arrives as a scene with stakes, warnings and a frame (07's lethal
  warning applies).
- **Several boundaries at once** (the last week of winter is also the year's end). 00.7.6: `week` (World Turn),
  then `season` (Season Turn, which runs the herald's promises), then `year` (Year Turn: aging).

## State touched

- **Read:** the place graph and venture records (10); evidence packets `public_deed` and `public()` (03);
  `recognition_event` and `apotheosis_available` (04); harm states, setbacks, `victory_over_pc`, caches,
  `career_end` (07); holdings' prices and gift configuration (08); archetypes and Nemesis results (09); NPC
  records, scene records, pacing phase, rotation ledger, cast and thread lists (12); standing, commitments,
  cases, lies, downtime (15); allies, retinue, personal threads (16); creation hooks, ties, prologue (02);
  calendar names (the region's seed, 12.16.15).
- **Written (owned by this chapter, 00.6.3):** factions (entities) and their clocks; relationships faction→PC and
  faction→faction; situations; the bang queue; world reactions' cooldowns; threads and hooks; rumors and news;
  reputation entries and epithets; ranks and obligations (commitments); holdings records and their damage clocks;
  world phenomena; attention clocks and pursuit; the change log; the chronicle; legacy records; the calendar
  position and moon; ages and aging marks (with 07's mark machinery).
- **Tools used:** `advance_time`, `mark_boundary`, `create_entity`, `set_fact`, `set_relationship`,
  `create_clock`, `tick_clock`, `set_clock`, `roll_table`, `oracle`, `record_knowledge`, `seal`/`unseal`,
  `offer_create`/`offer_resolve` (institutional offers through 04's protocol), `generate` (via 08's `gen.gift`),
  `chronicle_append`, `apply_effect`, `get_state`.
- **Hooks subscribed:** `on_fact_set` (immediate world reactions, linchpin fates, outdated rumors, commitments'
  conditions); `on_clock_complete` (attention, opposing clocks, goal clocks, hunt clocks).
- **Handlers registered** (`data/boundaries.yaml` reserved, defined here; additions in
  `data/boundaries.yaml owner-block 11`): `h.11.world_turn` (week, 6), `h.11.season_turn` (season, 6),
  `h.11.year_turn` (year, 6), `h.11.situation_timelines` (day, 6), `h.11.fallback_counters` (scene_end, 6),
  `h.11.reckoning` (venture_end, 6); added: `h.11.world_record` (week, 9: the turn's chronicle lines), `h.11.moon`
  (day, 9: `moon.phase`), `h.11.festival` (day, 6: a festival's effects on its day). The season herald is World
  Turn step 8 at a season's 12th week, not a handler of its own.
- **Clocks created:** faction goal clocks (faction_goal; hidden or sensed; local 8, regional 12, realm 12+12);
  attention clocks (danger 8, hidden); thread progress clocks (progress, public; 4/6/8/12/12+12); thread
  opposing clocks; hunt clocks (danger 6, hidden); holdings' damage clocks (6, public); battle breaking clocks;
  bounty clocks (6, public); training clocks (12, public).
- **Runtime capabilities assumed:** RC-RNG (every faction check, table, truth roll), RC-STORE, RC-SEAL (goals,
  linchpin fates, situation timelines, rumor truth, the bang queue), RC-SCHED (the three turns and their
  handlers, interrupts, timeskips that run every boundary), RC-LOG (change log, chronicle), RC-DATA, RC-QUERY
  (scope distance on the place graph; pattern matching for reactions; ancestor match for `patron_deeds`), RC-EVAL
  (effects of fates, phenomena and world changes), RC-RETRIEVE, RC-AUDIT (the claim check against the chronicle).
- **Visibility** (00.6.4): factions' existence and status rung — available once known; goals, clocks, linchpins,
  relations — sealed (omens and news shown); threads — shown when active, seeded hooks available as text;
  rumors' text — shown once heard, truth sealed; reputation content, scope and epithets — available, points and
  score background; ranks, holdings, calendar, chronicle (as known) — shown/available; the bang queue, change log,
  attention — background/sealed.

## Interface requests

**T-11-25 Requests made of chapter 11, and where each is satisfied** (`_process/INTERFACE-REQUESTS.md`; each
chapter's "To 11" section).

| From | Request | Satisfied by |
|---|---|---|
| 00 / contract | World Turn on `week`; Season Turn on `season`; factions; situations and timelines; threads; rumors with truth values; reputation; ranks; holdings; calendar engine; chronicle; retirement and legacy; `institutions_matching` | 11.2; 11.11; 11.3; 11.4; 11.5; 11.6; 11.7; 11.8; 11.9; 11.10; 11.12; 11.13; 11.8.1 |
| 01 | `thread completed` and `vow kept` as fate triggers | 11.5.5 (completed row emits `thread_completed`, `vow_kept`); 11.5.11 |
| 01 | reputation content entries from `cost.exposure` at S5 | 11.7.2 item 4; PR-11-4 |
| 01 / 12 | S5 twist rows need haven, commitment and situation facts | 11.4.10 (`havens`, `commitments_owed`, `new_situation`, row 4's withdrawal) |
| 02 | consume `CreationHook`s and own their lifecycle | 11.5.6 (by kind), 11.5.5 |
| 02 | the long vow as a vow thread; closed as abandoned if the drive is rewritten | 11.5.2, 11.5.5 (abandoned), 11.5.12 |
| 02 | map each faction tie's `org` kind to a faction and write its status (+1; or +2 and −2) | PR-11-4 (the region's seed maps the kind, 12.16.10; this chapter writes) [verification: V2b-013] |
| 02 | prologue lines | 11.12.2 |
| 02 | keep a lost bond's sealed fate for a later clue | 11.5.6 |
| 02 | successors: candidates with recorded origins, one heirloom, the renown share, legacy results as hooks and bonds, Train-a-Successor whose output is ≤ 3 tags for 03.2.8; emit `vow_kept` | 11.13.9, 11.13.10, Train-a-Successor; 11.5.5 |
| 03 | consume `public_deed` packets and `public()` | 11.7.2–11.7.3; 11.3.11; 11.8.1 (`heard`) |
| 03 | NPC home and faction memberships | 11.1.2; 11.3.17 |
| 03 | reputation by persona when `as_identity` is set | 11.7.8 |
| 03 | the chronicle may quote deed lines; at retirement the settled ledger is what legacy reads | 11.12; 11.13.5 |
| 04 | consume `recognition_event` (with its `confirmed` meaning) for reputation, epithets (V1's wording), rumors, status, ranks; a standing step only when `decline_cost` is set | PR-11-4; 11.7.2 item 2; 11.7.5; T-11-20 reads "confirmed" tiers |
| 04 | `institutions_matching(branch, region) → [{faction_id, status_to_pc, has_ranks, next_sitting}]` | 11.8.1 (adds `heard` and `teachers`) |
| 04 | restitution as a thread | 11.5.12 |
| 04 | `h.11.season_turn` (phase 6) before `h.04.season_consolidation` (phase 8) | 11.11.1 |
| 04 | retirement reads `apotheosis_available` and retires every calling | 11.13.1, 11.13.2, 11.13.7 |
| 04 | a crystallization staged before carriers sends a public packet; a tier-5 recognition's regional spread | PR-11-4; 11.7.4 |
| 05 | standing with a keeper's faith; settlement tiers for abilities (the region's seed, 12.16.9); threads from rites and spirit bargains | Edge cases (keeper's faith = faction status); 11.5.12 |
| 07 | consume `victory_over_pc`, defeat reputation packets, the belief `pc.dead`, cache rumors, the rout's clock tick (faction goal clocks as candidates) | 11.3.17; 11.7.2 item 3; 11.6.8; T-11-10; 11.3.6 (goal clocks list `rout`) |
| 07 | the Bargain's vow as a thread racing a countdown | 11.5.12 |
| 07 | retirement from The Road Ends and the fourth break; legacy for Last Stand and a lost Gamble | 11.13.1 |
| 07 | holds within reach for captivity (07.6.3) | 11.3.1 (`holds`) |
| 08 | holdings' prices, upkeep, staff; yields are labor and rents | 11.9 (11.9.4 yields on 08's dice) |
| 08 | faction `boon_signature` and `boon_base`; `gift_due` triggers | 11.9.9; `factions.yaml` templates |
| 08 | lifestyle shortfall writes a debt; cache dispersal and rumors; glut and find-buyer may feed rumors | 11.4.9 (debts are commitments); T-11-10; 11.10.4 (market festivals) |
| 09 | Nemesis results: boast rumors, hunt clocks, promotions of named victors | 11.3.17; 11.6.3 (`boast`) |
| 09 | factions field adversaries by archetype and band with the org tag added | 11.3.3; 11.3.17 |
| 10 | consume the venture record at `h.11.reckoning`; occupants, cleared sites, evaded threats | 11.3.13 |
| 10 | `safe` changes are 11's writes | 11.3.13 (pacify), 11.9.2, 11.9.5, 11.4.10, T-11-17 |
| 10 | regional events table `tbl.<region>.events`; calendar season ids for weather | `world_turn.yaml#tbl.11.local_events` (generic V-face table a region's seed or setting may replace); 11.10.1 (`spring`…`winter`) |
| 12 | clocks list `random_event` as a tick source | 11.3.6; 11.5.4 |
| 12 | bangs carry `intensity_delta` (threat 3 / social 1 / opportunity 0) and a specificity key | 11.4.4 |
| 12 | thread status `stalled` with its fallback queued | 11.5.5; 11.5.7 |
| 12 | every hook ≥ 3 clue placements | 11.5.6; PR-11-5 |
| 12 | rumors carry `points_to` | 11.6.1; 11.6.4 |
| 12 | accept chronicle-line offers (scene end, venture end) | 11.12.2; 11.3.13 |
| 15 | officers' duties as refusals | 11.3.17 |
| 15 | trigger member-standing recompute on every status change | 11.3.8; PR-11-1 step 4 |
| 15 | fire case fallbacks through `h.11.fallback_counters` | 11.5.7 |
| 15 | an attention clock for Lie low | 11.3.12 (−2 per week of `dt.lie_low`) |
| 15 | holdings' yield reads `managed_this_week` | 11.9.4 |
| 15 | projects' world changes (LW-09); ranks that carry training; `institutions_matching` returns teachers; the ransom countdown | 11.9.7, T-11-17; 11.8.4 item 2; 11.8.1; 11.3.6 (`aid_pc` pays a due ransom) |
| 15 | reputation entries for exposed lies, broken obligations, wrong accusations | 11.7.2 item 5 |
| 16 | companion personal threads (kind quest, ≥ 3 placements, fallback) | 11.5.12; 11.5.6 |
| 16 | factions court allies (`courted_by`, sealed, with an omen; `kn.loyal` immune at Neutral+) | 11.3.6–11.3.7 |
| 16 | reputation for how the PC treats their people | 11.7.2 item 6 |
| 16 | ranks that grant followers (count is 11's) | 11.8.4 item 3 |
| 16 | allies as successor candidates; standing toward an heir = old − 1 | 11.13.9; 11.13.10 item 6 |
| 16 | vows at an ally's death | 11.5.12 |
| 16 | allies carry deeds to their home scopes | 03's carrier rule feeds 11.6/11.7 |
| 16 | battles: the allied army's corners as held lines | 11.3.15 |

**Requests this chapter makes.**
- **To 00 (no amendment needed; notes for integration):** (a) `data/SCHEMAS.md` sections for `factions.yaml`,
  `world_turn.yaml`, `calendar.yaml` and `legacy.yaml` should list T-11-1's optional keys; (b) entity kind
  `object` carries the subtypes `situation` and `legacy` (no new kind); (c) id prefixes this chapter uses:
  `sit.` (situations), `sit_t.` (situation templates), `bang.` (bangs), `wr.` (world reactions), `thr.`
  (threads), `rum.` (rumors), `rep.` (reputation entries), `chr.` (chronicle entries), `imp.` (improvements),
  `ftpl.` (faction templates), `legacy.` (legacy records) — proposed for 00.16.2; (d) triggers
  `trg.11.flashpoint` and the out-of-fiction labels `[SEASON]` and `[RETIRE]` (12.15, 14).
- **To 04:** the `[RETIRE]` offer uses 04.7's offer protocol (accept, decline, defer); `apotheosis_forms` in
  `legacy.yaml` are keyed by deed branch until 04's callings carry their own ending text (04 may add
  `apotheosis` to a calling entry and this chapter reads it first).
- **To 07:** an **aging mark** is a permanent mark under 00.4.3 (c) and 07.7's machinery, with its source
  `aging`; it shares the −1-per-attribute limit with maims.
- **To 12:** the pacing push draws from this chapter's queue as 12.7.4 says; fallback bangs fire at the next
  `scene_start` (12.8.4); kickers (11.4.5) read the rotation ledger (12.9.2); render `[SEASON]` and `[RETIRE]`;
  NPC generation writes `home` and `member_of` (11.1.2).
- **To 13 (now the region's seed, 12.16, which writes them for any region: T-12-16 `ws.req.11_*`; ch.13 is one
  optional pre-made seed) [revision: I-028]:** factions in the `factions.yaml` owner-block conforming to 11.3.1 with linchpin fates sealed;
  the mapping from 02's tie kinds to regional factions; month, weekday, quarter-day, festival and era names in
  `calendar.yaml`; regional `tbl.11.season_events.<region>`, `tbl.11.hook` and `tbl.<region>.events`; regional
  values for region scopes (11.7.6); lifespans for its peoples if they differ.
- **To 14:** codex views — Factions (known factions, status rung name, seat, traces seen), Register (threads with
  their public clocks; hooks as text), Reputation (entries by scope: content, epithet, tone band, valence word),
  Ranks and obligations, Holdings, Calendar (date, moon, festivals), Chronicle (as known), Legacy (after a
  retirement).
- **To 15:** list `dt.11.train_successor` in the downtime menu (11.13.10); `h.15.member_standing` runs at once on
  every status write (it already does by 15.1.3).

## Open empirical questions

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-11-1 | Does a weekly World Turn give the right density of world change for a solo player? | weekly; ≈ one faction goal per seven weeks per region (T-11-24; [revision: I-032]) | **T-11-PULSE**: 3 campaigns × 20 sessions; after each session the player rates "the world moved on its own" and "too much happened to follow" (1–5); target ≥ 4 and ≤ 2 respectively; adjust goal ticks (crit 2 / success 1) before cadence |
| OEQ-11-2 | Are faction goals paced right (not too fast, not stalled)? | local 8 / regional 12 / realm 12+12, DC 13/15/17 net | **T-11-GOALS**: re-run `11-world-sim.py` with a world seed's factions (`12-world-seed-example.yaml`; chapter 13's are one pre-made set, `13-world-sim.py`); target 1.5–3.5 goal completions per faction per year and ≤ 10% of factions at tier 5 after two years |
| OEQ-11-3 | Does the hook supply keep the register full without flooding? | ≥ 3 known open matters; seeded hooks expire at 8 weeks; caps 8 seeded / 12 active | **T-11-HOOKS**: playtest logs; count sessions that open with no actionable lead (target 0) and sessions where the player says they have "too many threads" (target ≤ 1 in 10) |
| OEQ-11-4 | Do players perceive the World Turn's traces? | ≥ 1 trace per consequential change; news on arrival ≤ 3 items | **T-11-TRACE**: after 10 sessions, ask the player to name three things a faction did off-screen; target ≥ 2 correct |
| OEQ-11-5 | Is reputation's growth rate right? | triangular thresholds 1/3/6/10/15 | **T-11-REP**: 3 campaigns; record sessions to score 3 in the home settlement; target 4–8 sessions for a focused PC; epithet coined by session 3–5 |
| OEQ-11-6 | Are rumor truth rates believable and useful? | T-11-11 | **T-11-RUMOR**: 50 rumors heard in play; the player's estimate of how many were wrong vs actual; target the player investigates ≥ 30% and finds the false ones "fair" (≥ 4/5) |
| OEQ-11-7 | Do retirement seams feel like culminations, and do successors feel connected? | 11.13.1 seams; three candidates from the story | **T-11-LEGACY**: 3 retirements; the player rates "the ending felt earned" and "my new character belongs to this world" (target ≥ 4/5); count candidates drawn from sources 1–3 (target ≥ 2 of 3) |
| OEQ-11-8 | Does attention produce pressure without persecution? | clock 8, decay 1/week, entanglement per completion | **T-11-HEAT**: the war scenario of the sim (one entanglement or move per ≈ 9 weeks) against 3 playtests; the player rates "the enemy felt active" ≥ 4 and "relentless" ≤ 2 |

