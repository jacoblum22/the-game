# 03 — Tags and Evidence

> This chapter is the memory of who a character has **become**. It owns two things the whole growth system
> stands on: the **content of the tag vocabulary** below level 2 (`data/tags.yaml`), and the **evidence
> mechanism** (`tag_event`, recorded with `record_evidence`). Every resolved moment that shows something about
> a character becomes one atomic, neutrally worded evidence event. Each event is tagged with the most specific
> deed tag of its *method* and, where a value was at stake, a signed conduct axis. The engine weighs it by how
> hard the moment was *for this character*, how much was at stake, how it went and whether it was new. It then
> **settles** it at the end of the scene. Settlement applies diminishing returns at every level of the tag tree,
> so a scene shows a skill once and grinding shows almost nothing. It also keeps a **recent** window that
> follows what the character is doing now. The results are sealed. Chapter 04 reads them through one family of
> functions (`tally`, `detail`, `share`, `dominance`, `cooccurrence`, `diversity`, `conduct`, `counted`).
> Chapter 11 reads only what was witnessed (`public`). The DM's significance call, which the constitution
> leaves to judgment and which research shows is biased toward leniency, is broken into checks. Whether a deed
> counts follows from the stakes, opposition and tier the DM already committed to in the frame *before* the
> roll. Judgment is kept only where nothing else can do the job: naming the tag, and deciding whether a choice
> expressed a value. Every secondary tag and every conduct entry must cite something on record. That is how
> the game's emergent-identity premise can survive a lenient AI.

---

## Design intent

**Goals served.** Goal 1: whatever the player tries, in any pillar, leaves a fair, durable trace that can grow
into an identity. There is no "this doesn't count because it isn't combat", and clever play is never taxed.
Goal 2: the AI DM never adds a number, never keeps a count in its head, never sees a tally, and makes at most
one classification per deed. Every other step is a deterministic function of state it has already written
[BRIEF §3; C:P5; C:III].

**What the research forced.**
- *Evidence quality over quantity; cheap evidence must saturate; higher tiers need qualitatively different
  evidence* (HWFWM's self-limiting core path; Cradle and Stormlight's "cannot just say the words") [R2 #5,
  §03]. That gives this chapter its relative **quality rung**, **diminishing returns at every node**, a
  **routine cap**, and a quality and band profile exposed to 04 (03.4, 03.5, 03.9).
- *Burning Wheel's Routine / Difficult / Challenging mix*, in which difficulty is measured against the
  character's current ability and routine tests stop counting as ability rises [R6 A-06; R: http://questingblog.com/wp-content/uploads/2015/02/Burning-Wheel-Procedural-Guide-V2.pdf].
  This game reads the same relativity straight from the frame's computed odds (03.4.1). It is the harder-when-higher
  curve of Pendragon's d20-must-exceed check and RuneQuest's "roll over your skill" experience check, done
  without any extra roll [R6 A-04; R: https://rqwiki.chaosium.com/rules/experience.html]. Skyrim prices each
  skill step by `(level−1)^1.95`, which bakes the same idea into a curve [R: https://en.uesp.net/wiki/Skyrim:Leveling].
- *Grinding is the failure every use-based system documents.* Skyrim's own wiki recommends levelling Sneak by
  stabbing a purchased horse and healing it, or by sneak-attacking a sickly soldier who never moves
  [R: https://en.uesp.net/wiki/Skyrim:Sneak]. Ultima IV had to add a step-counter cooldown before a second
  gift to the same beggar counted again [R: https://bumbershootsoft.wordpress.com/2017/09/29/hacking-the-virtues-becoming-the-avatar-in-five-easy-steps/;
  R: https://gamefaqs.gamespot.com/pc/562660-ultima-iv-quest-of-the-avatar/faqs/7515/quick-relatively-walkthrough].
  WoW's diminishing-returns shape (1, ½, ¼, then immune, with a reset window) is the template [R3 03.9]. Hence
  03.5: DR per node per scene, a routine cap per day, a same-target cap per day, and a pressure requirement
  that excludes practice.
- *Two evidence kinds* (Delve's Primary and Secondary requirements): judged events and engine-counted events,
  kept in separate tallies so that 04 can require both and the counted one cannot be inflated by judgment
  [R3 03.4, #4; C:P5 dual-tier].
- *NCP fact-update discipline*: record only completed, atomic, observable acts with a one-line justification;
  split compound actions; supersede only by explicit logged events; judge significance on a neutral
  restatement, never on dramatic prose [R1 §03, #11].
- *Leniency is the dominant AI failure* (false passes run about 120× false checks; a plausible justification
  roughly quadruples the error rate) and it will skew "does this count?" toward yes [R4 W2–W3, §9 03;
  R: https://arxiv.org/abs/2607.02802]. Hence 03.3: significance is computed from fields committed before the
  roll, judgment survives only as tag classification and conduct, each conduct call must cite a state write,
  and the narrator never sees a tally.
- *Signed conduct with strain → break → atonement* (Stormlight's dimming bond; the Paladin who atones;
  Ultima IV's eighths that are lost and regained) [R2 #6; R6 A-01–A-03, V14]. Hence 03.8: signed points, net
  values, **strain** and explicit atonement supersession.
- *Witness × scope*: deeds feed the private tally whether or not anyone sees them; only witnessed deeds feed
  public reputation, scoped to the communities whose members saw them and will talk (Ars Magica's
  Local/Ecclesiastical/Hermetic reputations; the new Fable's per-settlement reputation; saga bynames)
  [R6 A-15, A-18, A-19, R-A1, R-A3]. Hence 03.10.
- *Recency versus cumulative* (Delve and EVE never forget; Wandering Inn and Azarinth follow drift): recognition
  thresholds use cumulative weight, while maintenance and relabelling use a recent window measured in active
  play, so a winter spent in a monastery does not erase a ranger [R3 T-8, 03.10; R6 A-08].

**What this chapter deliberately avoids.**
- *A significance question asked after the outcome.* Whether a deed counts is never decided from how the
  scene felt. It comes from the frame (stakes, opposition, tier, delivered reach), which was committed before
  the d20 was rolled (03.3.2).
- *Witness-weighted capability.* A hermit wizard is no less a wizard. Witnesses gate *public* recognition only
  (03.4.6, 03.10).
- *Calendar decay.* Recency is counted in evidence-bearing scenes, never in days (03.6.1).
- *Numbers in the DM's hands.* The DM supplies tags, flags, ids and one line of text; the engine computes
  every point (INV-3).
- *Aspirations as weight.* A player's stated aspiration (02) raises *salience* in scene generation (12) and
  never adds evidence weight [R6 R-A7; DL-03-22].
- *Tags of scenes as evidence of people.* A scene tagged `situation.investigation` is not evidence that the
  PC investigated. Only the beat's method tag is [R1 §03, retrieval vs evidence semantics].
- *Compelled behaviour.* Tallies never make the character do anything (Pendragon's trait compulsion is
  rejected) [R6 A-04, anti-patterns].

**Runtime capability assumed.** A deterministic, sealed tally store with an append-only evidence ledger
(RC-STORE, RC-SEAL, RC-LOG), tag-ancestry queries (RC-QUERY), the boundary scheduler (RC-SCHED) for scene
settlement and reflection, and hook dispatch (RC-EVAL) for counted evidence. No model call is needed after the
DM's one classification per deed.

---

## Rules

Rule ids are `03.S.R`. Kinds per 00.2.2. Digest shorthand per 00.1.6. "PC" covers any actor whose evidence is
tracked (03.2.7).

### 03.1 The tag vocabulary: content, classification, authoring

**03.1.1 What the vocabulary must answer.** `[N]` One hierarchy (00.5.1) answers four questions, and each
facet's depth was set by the question it serves:

| Question | Facets | Who keys on it | Depth this chapter gives it |
|---|---|---|---|
| What did the character do (method)? | `deed` | evidence, competence (00.3.6), callings (04), ability pools (05), license tags | **every level-2 deed tag has level-3 children** (T-03-1): weapon families, techniques, schools by function, trades by product |
| What value did the act express? | `conduct` | conduct evidence, oaths, shadows, the Fraying (04) | ten signed axes, leaves at level 1 (00.5.1); poles and act tests in T-03-4 |
| What is this thing or being? | `creature`, `material`, `item`, `harm`, `terrain` | pool gates (00.11), absorbable pools (04), context classes for novelty (03.4.4), grounding (03.1.6) | level 3 where 08, 09 and 10 will key loot, weapons, materials and site themes (T-03-12); stewards propose the rest |
| Which rules load? | `situation`, `trait`, `org` | rule cards (12), general trait rules (01), factions and vehicles (11, 04) | levels 1–2 as seeded by 00; this chapter adds none and leaves them to stewards' proposals |

**03.1.2 Depth policy.** `[D]` Deed tags go to **level 3** (four segments, e.g. `deed.martial.archery.bow`)
across the whole facet. Level 4 (five segments, the 00.5.5 maximum) is **reserved**. It is added only by
PR-03-6 when a calling, ability pool or competence entry needs a distinction that no level-3 tag can make, and
the need is shown by a data entry, not by flavour. Why stop at level 3: a branch already has 6–13 level-2 children,
each of those has 2–6 level-3 children, and the AI classifies level by level (00.5.6), so every extra level is
one more confusable choice [R4 §3.2 S1]. Competence, pool gates and callings get all the granularity they need at level 3. Level 4 would
mostly split by object brand (longbow vs shortbow), which the item facet already records [DL-03-15].

**03.1.3 Level-2 additions.** `[D]` Under 00.5.5 this chapter appends two level-2 deed children, each with a
DL entry. Neither renames or retires a seeded tag.
- `deed.influence.teaching`: passing a skill or understanding to another person (instruction, mentoring).
  Without it, the mentor callings and the "taught" recognition path (R6 A-21, V2) have no evidence axis.
- `deed.craft.scribing`: making written works (fair copies, illumination, maps, bound books). Without it,
  cartography and copying fall between `lore` (which knows) and `enchanting` (which needs magic).
[DL-03-16]

**03.1.4 Reading a tag entry.** `[N]` Every entry in `data/tags.yaml` carries `id`, `name`, `parent`,
`level`, `lifecycle` and a `definition` of the form "True only when … False for … (sibling id)". Entries
below level 2 also carry `distinguish`, which is the test against the nearest overlapping sibling or cousin,
and `aliases`, which are natural-language words for retrieval and classification. Aliases are not tags. A
player's word that matches an alias is only a hint; the definition decides (SG-06).

**03.1.5 Classifying the primary deed tag.** `[J:enum]` + `[D]`

```
### 03.1.5  Primary deed tag                                   [J:enum] [D]
Trigger [T]:        a beat reaches FRAME (01.6) — the frame needs `deed_tag` (00.13.1)
Loads in:           core (the classification card travels with every frame)
License check:      n/a (classification, not an attempt)
Decisions (J):      1. BRANCH [J:enum] among the 9 deed branches by their definitions (00.5.2):
                       the branch whose "true only when" fits the METHOD as described; not the intent,
                       not the target, not the scene's situation. Default when uncertain: the basic
                       verb's default tag in T-03-2 (e.g. Strike -> martial).
                    2. CHILD [J:enum] among the branch's level-2 children by their definitions; uncertain
                       -> stop at the branch.
                    3. GRANDCHILD [J:enum] among the child's level-3 children; uncertain -> stop at the
                       child. The engine never accepts a deeper tag than the data holds.
Computation [D]:    competence = highest entry on the tag or any ancestor (00.3.6); the tag is copied
                    to the evidence event as `primary_tag` (03.2.1).
Stakes:             none (classification)
State writes:       frame.deed_tag
Narration may not imply: that the classification is a judgment about the character
Worst case (J):     one level too shallow (competence from an ancestor, same or lower; evidence credits
                    the ancestors only; class i), or the wrong sibling (the floor or a lower specialty
                    applies, shown in the OFFER breakdown, so the player may object; evidence lands on a
                    sibling under the same parent, so every ancestor is still credited correctly; class ii/iii).
Examples:           inside: "I loose an arrow at the wolf" -> martial -> archery -> bow.
                    inside: "I put an arrow in the sentry from the hayloft before he knows I'm there",
                      framed against the shot's difficulty -> martial -> archery -> bow, with
                      guile.ambush.sniping as a secondary grounded by position (03.1.6, 03.1.7 rule 2).
                    inside: "I creep up and cut his throat", framed against his awareness ->
                      guile -> ambush -> assassination, with blade.dagger grounded by the knife.
                    boundary: "I shoot the rope holding the chandelier" -> martial.archery.bow (the method
                      is a shot; the intent, dropping a chandelier on a foe, does not change the method).
                    boundary: "I hurl my dagger" -> martial.thrown.blades, not blade.dagger (throwing is
                      the method).
                    non-example: "I fight like a true knight" -> not a method; ask what the character does
                      (00.6.7); no tag is classified from a self-description.
Anchor:             no (classification card; the anchors are the verb cards it feeds)
Basis:              [00.5.6] [C:P5 cascade] [R4 §9 03 #4 one classification, engine cascades] [R4 SG-04]
```

**03.1.6 Secondary deed tags and grounding.** `[J:flag]` + `[D]` A beat may carry up to two secondary deed
tags (00.5.6). Each one earns evidence at **half** the event's points, rounded down (03.4.2). The leniency risk
is obvious: an agreeable DM would add "tactics" to every shot. So a secondary tag is accepted only when it is
**grounded**, meaning the frame names a thing that carries the tag:

| Ground kind | A secondary tag S is grounded when… | Example |
|---|---|---|
| `ability` / `license` | an ability or license cited in the beat's gate (`frame.gate.license`) or fired in the beat carries S or a descendant of S | a fire-arrow ability tagged `deed.arcane.fire.blast` used on a bow shot → `arcane.fire.blast` secondary |
| `item` | an item used as the beat's tool or weapon maps to S in T-03-3 (item → deed grounding) | a throat cut from behind (primary `guile.ambush.assassination`) made with a knife → `martial.blade.dagger` |
| `position` | S is under `deed.guile.ambush`, and when the beat was declared the actor had `flag.hidden` toward the target or the target's alertness was `unaware` (cite the flag or fact) | a bow shot from the hayloft at an unaware sentry (primary `martial.archery.bow`) → `guile.ambush.sniping` |
| `setup_beat` | a lever cited by this frame was created by an earlier beat of the same scene whose primary tag is S or a descendant | a Setup that drove the foe onto the ice (primary `martial.tactics.ground`) → the follow-up spear thrust carries `tactics.ground` |
| `companion` | a companion or follower acting by the PC's command contributed this beat's lever (16) | a hound's flushing gives the shot its lever → `wilds.animals.training` |
| `mount` | the PC is mounted (`flag.mounted`) and the beat is an attack | a shot from the saddle → `martial.mounted.skirmish` |

The DM proposes the secondary tag and cites the ground. The flag decided is *"Does the cited ground carry this
tag?"*, and the engine checks it against the data, so it is in effect `[D]`. An ungrounded secondary is
refused with the reason logged, and the primary tag is unaffected. *Worst case (J):* a grounded but irrelevant
secondary (the item was carried but barely mattered) adds half-weight evidence to an ancestor-related node;
diminishing returns cap it at that node's per-scene budget (03.5.2), and it is visible on the ledger line
(class iii). The simulation's ungrounded-leniency case (every beat tagged `tactics`) grew a spurious tactics
node to **49%** of the real archery node by session 20. With grounding (a tactics Setup in about 15% of
beats) it reached **15%** (T-03-9, scenarios E/E2) [DL-03-14].

**03.1.7 Method, not intent, scene or target.** `[D]` These rules apply in order; the first that matches
wins (SG-10):
1. **The method decides.** Throwing a dagger is `thrown`; stabbing with it is `blade.dagger`; poisoning its
   edge is `guile.poisoncraft.envenoming`.
2. **A strike on an unaware target** is classified by the contest the frame rolls [00.5.2: guile "when
   concealment is the point"]. If the frame rolls against the target's **awareness** (whether the blow lands
   before they know: the approach decides), the primary tag is `deed.guile.ambush.*` and the weapon is a
   grounded secondary. If the frame rolls against the target's **Guard or the shot's difficulty** (the strike
   decides), the primary tag is the weapon's or spell's own tag, and `deed.guile.ambush.*` is a secondary
   grounded by position (03.1.6). This keeps a hunter's shot at an unwary deer an archer's deed, with the
   archer's competence, and keeps the knife in a sleeper's ribs a deed of guile [DL-03-24].
3. **When the deed is magic**, the primary tag is the magic branch of the license used (`arcane`, `divine`,
   `primal`), whatever the effect looks like. A fire spell shot like an arrow is `arcane.fire.blast`. Under
   `gate.mode: emulate` the primary tag is the **emulated** technique's first deed tag (the evidence lands
   where its learning clock is); a small working (05.7.6) takes the school's level-2 tag
   [integration: IR ch.05 to 03].
4. **When the deed is knowing** (a check whose method is recall, deduction or study), it is `lore.*`, even
   when the subject is a weapon or a monster.
5. **The scene's situation tag and the target's creature tag are never deed tags.** They feed the context
   class (03.4.4) and the diversity measures (03.9.3).

**03.1.8 The conduct axes.** `[J:enum]` + `[J:flag]` The ten axes are leaves at level 1 (00.5.3). Each has a
positive and a negative pole, an **act test** for each pole, and exclusions. These are in T-03-4, canonical in
`data/evidence.yaml#conduct_tests`. They sharpen the one-line definitions 00 seeded in `data/tags.yaml`
(rows this chapter may not edit) and are the tests the DM applies. A
conduct event names the axis and the sign, and grounds them in a state write (03.3.3). At most **two** conduct
axes may be recorded per beat, and they may carry different signs (freeing a guilty man out of pity: mercy +1,
justice −1). The decisions, their defaults and their *Worst case (J)* line are in 03.3.3: one wrong entry is at
most 4 points on one axis, capped at 7 per scene, and voidable.

**03.1.9 Tags proposed by other chapters.** `[D]` Any chapter may use a level-3 tag that is not yet in the
file if it follows 00.5.5 and lists the tag under its Interface requests or in `data/contrib/tags.NN.yaml`.
This chapter (or the orchestrator acting under these rules) reconciles each proposal by PR-03-6. If the
proposal is the same kind as an existing tag, it becomes an **alias** of that tag and the proposing data is
rewritten to the existing id. Otherwise it is admitted with the full entry form. Two tags for one kind are
never kept.

**03.1.10 The non-deed facets in evidence.** `[D]` Evidence reads the other facets in exactly three places:
(a) the **context class** of an event (03.4.4) is built from the opposing entity's `creature` tag at level 2,
or the obstacle's own most specific tag at level 2, or the scene's `situation` tag at level 2;
(b) **grounding** (03.1.6) reads `item` tags through T-03-3;
(c) **diversity** measures (03.9.3) count distinct `creature` level-2 tags among opponents and distinct
`terrain` level-2 tags among places.
`harm`, `material`, `trait` and `org` tags never become evidence.

### 03.2 The evidence event and `record_evidence`

**03.2.1 The EvidenceEvent schema.** `[D]` It extends 00.6.8. The fourteen core fields are unchanged; every
field below the divider is added by this chapter. Fields marked *(engine)* are computed by `record_evidence`
and settlement, never supplied by the DM. Fields marked *(sealed)* are never returned to the narrator.

```yaml
EvidenceEvent:
  # ---- 00.6.8 core (unchanged) ----
  id: str                    # "ev.000123"
  actor: id                  # pc.* or a tracked companion (03.2.7)
  time: time
  deed: str                  # neutral one-line restatement of the observable act (03.2.4)
  tags: [tag]                # = [primary_tag] + secondary tags + conduct axes (for 00 consumers)
  conduct_sign: {tag: +1|-1} # one entry per conduct axis in `conduct`
  kind: enum                 # judged | counted   (03 adds the subkinds in `basis`)
  frame_id: str|null         # the resolved frame; null only for basis choice/hook/training/atonement
  degree: enum|null          # critical_success|success|failure|critical_failure (success_at_cost -> success, 03.2.2)
  challenge_band: int        # 1..5 (engine, 03.4.3)
  stakes: enum               # safe | risky | dire
  lethal_context: bool
  witnesses: [id]            # carriers who perceived it (03.10)
  scope: str|null            # primary scope id; the full list is in `scopes`
  # ---- 03 extensions ----
  basis: enum                # roll | success_at_cost | good_idea | take_the_time | certain_with_cost
                             #   | choice | hook | training | atonement | origin   (03.3.1)
  beat_id: str|null
  scene_id: str              # the scene it settles in
  day: int                   # (engine) the day index of `time`, for the per-day caps
  primary_tag: tag|null      # the frame's deed_tag (03.1.5); null for a conduct-only event
  secondary: [{tag: tag, ground: {kind: ability|license|item|setup_beat|companion|mount|position, ref: id}}]   # <= 2
  conduct: [{axis: tag, sign: +1|-1, magnitude: 2|4, ground_ref: write_ref,
             alternative_ref: id|null, forbidden_ref: commitment_id|null}]                            # <= 2
  target: id|null            # the opposing entity, or the obstacle entity the beat acted on
  context_class: tag         # (engine) 03.4.4
  base_odds: int|null        # (engine) success-or-better % with circumstance = 0 (03.4.1)
  quality: enum|null         # (engine) routine | difficult | challenging
  significance: {consequential: bool, pressured: bool, own_act: bool, cites: [id]}   # (engine) 03.3.2
  justification: str         # one line: why these tags fit, naming the observable facts (NCP)
  novel: bool                # (engine) 03.4.4
  contest: {kind: social|craft|lore, band: 1-5, one_from_full: bool, opposition: id}|null   # (engine) 03.4.3; null outside a contest; I-046; opposition: I-083
  ruinous: bool              # (engine) 03.4.5: Dire stakes with an irreversible threatened cost, outside conflict
  crisis: bool               # (engine) 03.4.5
  peak: bool                 # (engine) 03.4.5
  points: int                # (engine, sealed) pre-settlement points, 03.4.2
  counter: str|null          # counted events: the counter id (03.7)
  units: int|null            # counted events: units before DR
  witness_detail: [{entity: id, how: present|aftermath|bonded, carrier: bool}]   # 03.10
  as_identity: id|null       # the persona the witnesses took the actor for, when disguised (Edge cases)
  scopes: [str]              # (engine) every scope the carriers reach (03.10.3)
  status: enum               # pending | settled | void | superseded
  settled: {at: time, points_by_node: {tag: int}}      # (engine, sealed)
  supersedes: [id]           # atonement events only (03.8.4)
  void_reason: str|null
```

**03.2.2 `record_evidence` semantics.** `[D]` Tool #25 (00.14.2). Input: an EvidenceEvent with the fields the
DM supplies (actor, deed, basis, frame_id or the grounding refs, primary_tag, secondary, conduct, target,
witnesses, justification). The tool:
1. **Validates eligibility** (03.3.1). It refuses with a named reason any event that has no resolved basis,
   any primary tag that is not in `tags.yaml`, any secondary tag without a valid ground, any conduct entry
   without a `ground_ref` that resolves to a write made in this scene (03.3.3), and more than one judged deed
   event per beat (03.2.5).
2. **Copies from the frame** `degree`, `stakes`, `lethal_context`, `primary_tag` (it must equal
   `frame.deed_tag`) and the obstacle id. A success-at-cost (01.9.3) is recorded with `degree: success` and
   `basis: success_at_cost`. 01 records the frame's own degree as `failure` with
   `success_at_cost_taken: true`; for evidence it is a success [Interface request from 01].
3. **Computes** `base_odds`, `quality`, `challenge_band`, `context_class`, `novel`, `crisis`, `peak`,
   `significance`, `points` and `day` (03.3–03.4).
4. **Drops** the event with reason `not_significant` if the significance predicate is false (03.3.2), and logs
   the drop. A dropped event is never shown as recorded.
5. **Stores** the event as `pending` in the ledger. Its points join the scene's settlement at `scene_end`
   (03.5.1).
6. **Returns** the event id and nothing else. No tally, weight, point or threshold is ever returned (00.14.2
   #25; INV-10).

**03.2.3 Kinds and bases.** `[D]` `kind: judged` covers every event the DM records at RECORD: the bases
`roll`, `success_at_cost`, `good_idea`, `take_the_time`, `certain_with_cost` and `choice`. `kind: counted`
covers events written by the engine's counters (`basis: hook`) and by downtime training (`basis: training`).
`basis: atonement` is written only by 04's atonement procedure (03.8.4). `basis: origin` is written once, at
creation (03.2.8), and feeds the weighted tally like a judged event. Judged and counted events are never
summed into the same tally (03.7.1).

**03.2.4 The deed line.** `[D]` + `[N]` The `deed` field is one sentence, written before any narration
(01.12.1), that restates the **observable act and its resolved result** in neutral words. It contains no
adjective of merit ("heroic", "brilliant"), no inner state ("out of compassion"), no player framing, and no
number. *Good:* "Shot the bandit captain's horse from the treeline at dusk; the horse fell; the captain fled
on foot." *Bad:* "Wren's masterful shot showed her deadly skill and her mercy." The deed line is what the codex
shows and what 04's vehicles quote ("you held the bridge alone…") [R1 §03 neutral restatement; R2 §03 Voyager
descriptions]. The `justification` line names the facts that make the tags fit: "bow (item.i0031) used; target
unaware (fact guard_07.alertness=unaware) → ambush.sniping".

**03.2.5 Atomicity.** `[D]` One beat (00.18) yields at most **one judged deed event** (with up to two grounded
secondaries) and at most **two conduct entries**, carried on that same event or on one conduct-only event for
the beat. A compound declaration is already split into beats by 01.14; each beat records its own evidence. A
conduct choice made without a beat (basis `choice`) is its own event. This keeps the cascade countable and the
ledger auditable [R1 §03 atomicity; C:P5].

**03.2.6 What is never an evidence event.** `[D]` These are refused by the tool, and none of them is a
judgment call:
- an outcome that was narrated or asserted but not resolved: no frame degree and none of the no-roll bases
  (INV-9; [R3 01.8] the Feature 003 scripted-kill finding);
- a G0 question, a G3 redirect the player did not take up, a G4 impossibility, a free activity (00.12.6), a
  trivial no-roll beat, or a riding beat (01.4.2), which repeats an already resolved obstacle;
- an inconclusive beat (01.11.4), which fails the consequential test of 03.3.2 automatically;
- a resisted-effect check the actor did not declare (00.3.3): being poisoned and holding out is not a deed.
  A *declared* feat of endurance ("I hold my breath and swim the flooded passage") is a beat like any other;
- an act performed while the actor is under `cond.charmed` or any condition, ability or effect that dictates
  the actor's choices: such acts give **no conduct** evidence. Deed evidence still records, because the skill
  was the actor's [DL-03-19];
- an act by someone else: a companion, ally, summoned being or item acting on its own. Each of these is
  evidence for its own actor if that actor is tracked (03.2.7). The PC's command of it is a separate beat
  (`influence.command.directing` or `wilds.animals.training`);
- a player's description of the character's virtues or skills ("as a seasoned tracker, I…"), which is an
  assertion (00.6.7).

**03.2.7 Whose evidence is tracked.** `[D]` Evidence is tracked for every PC. It is also tracked for any
companion whose template sets `tracks_evidence: true` (16 decides; for example a squire who can grow), and for
no one else. NPC and adversary deeds are never evidence. Their reputations are 11's, and their growth is
authored [DL-03-20].

**03.2.8 Backstory evidence.** `[D]` A character has a past before play. An origin (02) may declare
`backstory: [tag]` with at most **three** deed tags at level 2 or 3. At creation the engine writes one settled
event per tag with `basis: origin`, **24 points** (one median session's yield at a focus node, T-03-10),
quality recorded as difficult, band 1, no witnesses, and a deed line taken from the origin's text ("Grew up
hunting the Ashwood with her mother's bow"). These events sit **before** the evidence-bearing list, so they
add to `weighted` and `raw` (as one event each), never to `recent`, `distinct.scenes`, `crises` or `peaks`.
A backstory gives a head start of one session toward an identity the player chose at creation. It cannot
satisfy a floor that asks for deeds in play. 02 decides whether to use it [DL-03-25].

### 03.3 Significance: does this moment count?

The constitution leaves this question to the DM's own judgment and rejects a bounded *taxonomy of trigger
types*, because such a taxonomy only moves the judgment one step earlier [C:P5 sixth pass]. This chapter keeps
the judgment. For deeds it reads judgments the DM **has already made, before the roll**: the obstacle tier,
the stakes rung and the opposition, all committed in the frame (00.13). No new question is asked once the
outcome is known, which is where leniency lives (R4 W2: post-hoc softening; R4 R-05: pre-declared stakes
prevent it). This does move the judgment earlier, as the constitution predicted. But it moves it onto a
judgment that already exists and is already committed, so it adds no complexity and gains the one safety
property the research shows actually works [DL-03-01]. Judgment proper stays where nothing else can work:
classifying the tag (03.1.5), and deciding whether a choice expressed a value (03.3.3). Both must cite state.

**03.3.1 Stage A — eligibility.** `[D]` An event is eligible only if its `basis` is one of the following,
checked against state:

| Basis | Eligible when (engine-checked) | Quality source (03.4.1) |
|---|---|---|
| `roll` | `frame_id` names a frame with a computed degree | base odds of the frame |
| `success_at_cost` | the frame's `success_at_cost_taken = true` | base odds of the frame |
| `good_idea` | `frame.necessity.reason = good_idea` (01.4.3), success delivered | the base odds the frame would have had, capped at **difficult** |
| `take_the_time` | `frame.necessity.reason = take_the_time` (01.4.4) | **routine** always |
| `certain_with_cost` | `frame.necessity.reason = certain_with_cost` (01.4.5) | **routine** always |
| `choice` | no frame; a conduct-only event whose every conduct entry has a `ground_ref` to a write made this scene | n/a (conduct points, 03.8.1) |
| `hook` | written by an engine counter (03.7) | n/a (counted units) |
| `training` | written by 15's downtime training activity at its week boundary | **routine** (03.5.5) |
| `atonement` | written by 04's atonement procedure | n/a |
| `origin` | written once at creation by 02's procedure, from the origin's `backstory` list (03.2.8) | fixed points; counts as difficult |

Everything else is refused (03.2.6). *Rationale:* evidence fires only on **resolved** outcomes [Interface
request from 01; R3 #8]. Note that a take-the-time success is, by 01.4.4, unopposed and unclocked, and its
quality is always routine. It therefore passes D2 (03.3.2) only when the beat ticks a progress or project
clock, as craft and research work does (WE-03-11).

**03.3.2 Stage B — the deed significance predicate.** `[D]` For a judged deed event, `significant =
consequential AND pressured AND own_act`, and each part is computed from the frame:

| Test | True only when (all engine-checked) | False for |
|---|---|---|
| **D1 consequential** | the beat delivered reach ≥ 1, **or** it failed and `apply_costs` applied the declared cost (a Risky or Dire attempt that really cost something), **or** it was a no-roll success (good idea, take the time, certain with cost) | Safe failures (nothing happened); inconclusive beats (01.11.4) |
| **D2 pressured** | any of: stakes ≥ Risky; an aware opposing entity (`frame.obstacle.defender` aware, or an opposing entity present and aware in the scene); a danger or countdown clock active in the scene; the beat ticks a progress or project clock; quality ≥ difficult | practice: a Safe, unopposed, unclocked, routine beat (shooting at a stump at leisure) |
| **D3 own act** | `frame.beat.actor` = the event's actor, the beat was **declared** by that actor, and the gate cites the actor's own verb or license | a companion's act; an item or effect acting on its own; an ally's beat the PC only helped (the Help beat is its own event, with its own tag); a resisted-effect check the actor did not declare (an Endure or Evade forced by a poison, a spell or a hazard, 00.3.3), because withstanding something is not a chosen method |

The DM's only input to Stage B is the frame it already built. *Worst case:* none is introduced here, because
every input is a field committed before the roll and shown in the OFFER. A mis-framed stakes rung (a one-rung
error under 00.3.14) changes D2 only at the Safe/Risky edge. It adds at most one routine-quality event, worth
2–4 points before settlement (class i), and the routine cap then holds that to one per node per day (03.5.3).

**03.3.3 Conduct significance.** `[J:flag]` ×2 + `[J:enum]` + `[D]`

```
### 03.3.3  Conduct evidence                         [J:flag] [J:flag] [J:enum] [D]
Trigger [T]:        RECORD of a beat, or a no-roll choice, after which state shows a write that
                    affected another being's welfare, a promise, a truth, a rite, or the actor's own gain
Loads in:           core
License check:      n/a
Decisions (J):      1. ALTERNATIVE [J:flag] "Was a different course plainly open to the character at that
                       moment, on record or visible in the scene?" True only when the DM can cite the
                       alternative: a fact, an entity or a frame option (e.g. the foe yielded and was at the
                       PC's mercy: npc.bandit_03.harm_state=defeated; the PC armed and unhindered). False when
                       the act was forced (no other path existed), compelled (03.2.6), or the alternative
                       exists only in the player's commentary. Uncertain -> false.
                    2. AXIS AND POLE [J:enum] among the 10 axes, by the act tests of T-03-4; at most two
                       axes, each with exactly one sign. Uncertain between two axes -> record the one whose
                       act test is met word for word; neither met -> no conduct entry.
                    3. GROUND [J:flag] "Does a write made this scene show the price or the harm?" The DM
                       cites `ground_ref`; the engine checks that the cited write exists and is of an
                       allowed kind:
                       POSITIVE pole: a cost applied to the actor (apply_costs; apply_harm; update_quantity
                       < 0 with reason gift or loss), a forgone gain written as a fact (npc.*.spared_by; a
                       reward refused; a lie refused while a falsehood would have served), a risk accepted
                       (a frame at Risky or Dire taken for another's sake), a commitment kept at cost.
                       NEGATIVE pole: harm or loss written to another being (apply_harm; apply_condition; a
                       relationship step down; an item or coin taken; a falsehood recorded in an NPC's
                       knowledge for the actor's gain), or a commitment broken.
                       No such write -> no conduct entry. Uncertain -> no.
Computation [D]:    magnitude per T-03-4: positive 2 (a cost or risk at S1-S2 or Risky; a forgone gain) or
                    4 (S3+, Dire, lethal context, or a forgone gain flagged irreplaceable); negative 2 (harm
                    or loss at S1-S2 equivalent) or 4 (S3+, death, maiming, ruin, or a helpless or trusting
                    victim). The engine reads the severity off the cited write; the DM never picks 2 or 4.
                    forbidden_ref: if the actor holds an oath commitment (04) that lists this act as
                    forbidden, the DM cites it [J:flag "Does the act match a forbidden act of a sworn oath,
                    word for word?" uncertain -> no]; 04 consumes it.
Stakes:             none
State writes:       the event's `conduct` entries and `conduct_sign`
Narration may not imply: that the character is now "good", "cruel" or any pole; that anyone judged them
                    (unless a witness reacts under its own rules, 15/11)
Worst case (J):     a lenient positive call adds 2 or 4 to one axis (a mis-signed one subtracts the same).
                    Bounded because the ground must be a real write (a cost or a harm); DR per axis per sign
                    per scene (03.5.2) caps one scene at 4 + 2 + 1 = 7 points; 04 offers rather than grants on
                    conduct (class ii); the player sees the deed line and may dispute it (12.3.6; class iv).
                    Simulated: a DM recording mercy roughly twice as often as warranted inflated it about
                    2.6x with no grounding (46 vs 18 points by session 20) and about 1.2x with grounding
                    (22 vs 18) (T-03-9, scenarios E/E2).
Examples:           inside (+mercy, 4): the yielded bandit who shot Wren's horse is bound and left alive by
                      the road with water. Ground: fact npc.bandit_03.spared_by=pc.wren, plus the Dire frame
                      she survived. Alternative: he was helpless (harm_state defeated).
                    inside (-mercy, 4): Wren kills a disarmed, yielded scout to save the trouble of guarding
                      him. Ground: apply_harm on a defeated target; the victim was helpless -> 4.
                    boundary (no conduct): she spares the scout because the captain is watching and ordered
                      it. The alternative is false (the order is a fact; disobeying was not plainly open), so
                      this is not mercy. It may still be loyalty (+) if obeying cost her something, by
                      loyalty's own test.
                    boundary (+honesty, 2): she admits to the reeve that she broke the archive hasp, and pays
                      the fine. Ground: update_quantity coin -6, reason fine. Alternative: the reeve had no
                      suspect.
                    non-example: the player writes "Wren feels terrible about the scout and resolves to do
                      better." -> inner state; no write; no conduct entry (and no assertion becomes a fact).
                    non-example: Wren gives a copper to a beggar while rich. Generosity's act test needs a
                      gift "that matters to the giver" (T-03-4); a gift under the ground's severity floor (S1 =
                      at least one Unit of the actor's weekly lifestyle cost, 08) fails -> no entry.
Anchor:             no
Basis:              [C:P5 values-expressive evidence] [R1 §03 T-9: record the act, not the inner state]
                    [R4 §9 03 #1: a cited concrete action; explicit exclusions] [R2 #6] [R6 A-02: BG3's
                    brittle single-trigger breaks -> magnitude by severity, strain instead of instant breaks]
```

**03.3.4 Designing for a lenient judge.** `[N]` A binding summary of what keeps the judged surface honest:
1. **Pre-commitment.** Deed significance is computed from frame fields fixed before the roll (03.3.2).
2. **Citations.** Every judged element must cite something in state: secondaries cite their ground (03.1.6);
   conduct cites its ground and alternative (03.3.3). No citation, no evidence.
3. **Tie-breaks toward "no".** Every uncertain judgment in this chapter defaults to *not recording*: the
   shallower tag, no secondary, no conduct (SG-05: "does this grant something? no").
4. **Blindness.** The DM classifies without ever seeing a tally, threshold, nearness or recent value. An
   agreeable model that knew the PC was one deed from a calling would nudge the fiction toward it [R4 §9 03
   #2]. Tallies are `[S]`; recognition arrives as a `[T]` from 04.
5. **Neutral wording.** Classification is made on the deed line (03.2.4), never on the scene's prose or the
   player's framing [R1 §03; "The Story Shapes the Agent"].
6. **Structural caps.** No single wrong call can move a node by more than its per-scene budget (03.5.2), and
   routine evidence cannot pile up (03.5.3). The largest possible single event (16 points, 03.4.2) is about
   **two-thirds** of a median focused session's yield on its level-2 node (≈24 points per session, T-03-10)
   and **20%** of a first-recognition threshold of 80 (T-03-10). One bad call is less than one session's play and never makes
   a calling on its own (class iii).
7. **Two keys for growth.** 04 is asked to require both judged weight and engine-counted evidence (03.7), so
   inflated judgment alone cannot cross a threshold.
8. **Audit.** The ledger is `available`: the player sees every deed line and its tags (03.11) and may
   dispute them. A dispute that succeeds voids the event (PR-03-4).
9. **Calibration test.** OEQ-03-1 runs R4's T-R4-05 "Evidence calibration" on the rules as shipped.

**03.3.5 Reflection sweep: catching omissions without adding leniency.** `[D]` + `[J:flag]` At each
`reflection` (03.6.4) the engine lists the frames since the last reflection that passed D1–D3 but produced no
judged event (the DM forgot to record one). For each, the DM may record the event now under the same frame
and the same rules. The event keeps its original scene and time and settles into that scene's budget after
the fact. The sweep can only restore evidence that a frame already qualified. It cannot add moments that had
no frame, and it never prompts for conduct. *Worst case (J):* no more than 03.3.2's, because the inputs are the
same pre-committed frames [R6 A-14, Forbidden Lands' end-of-session questions, adapted to frames; DL-03-21].

### 03.4 Weighting

Every number in this part is in `data/evidence.yaml#weights` (canonical). Points are integers (SG-23); the only
division is "halve, rounding down", applied at fixed steps.

**03.4.1 The quality rung: how hard this was for this character.** `[D]` Quality is read from the frame's
**base odds**: the success-or-better percentage that PR-00-1 step 8 would compute if `circumstance = 0`. Levers
and snags are removed, and attribute, competence, edge and status are kept.

| Quality | Base odds (success or better) | Anchor (Burning Wheel's rung) | Typical case |
|---|---|---|---|
| **routine** | **70% or more** | well within the character's ability | a P1 archer (+5) at an Easy shot (80%) |
| **difficult** | **40%–65%** | at the edge of ability | the same archer at a Moderate shot (55%) |
| **challenging** | **35% or less** | beyond normal ability | the same archer at a Hard shot (30%) |

Why base odds: (a) the measure is **relative**, so it rises with the character. An untrained PC (+1) climbing
an Easy wall (60%) is doing something difficult. A P3 expert (+9) at a Moderate task (75%) is doing something
routine. This is Burning Wheel's mix and Pendragon's harder-when-higher check, computed with no extra roll
[R6 A-04, A-06; R: https://forums.burningwheel.com/t/errata-number-of-tests-for-advancement/3833]. (b) It is
already computed for the OFFER, so it costs nothing. (c) **Levers are excluded** so that clever play is never
taxed. A player who sets up a Precision lever gets better odds *and* keeps full evidence quality. The Setup
beat earns its own evidence, and a lever's fact can ground a secondary tag (03.1.6). (d) Status is
**included**: fighting while bloodied, blinded or exhausted makes the deed genuinely harder for the character,
so it counts as more. [DL-03-02]

No-roll bases take their quality from 03.3.1's table. An opposed frame uses the same base odds against the
defender's defense.

**03.4.2 Points.** `[D]` A judged deed event's pre-settlement `points`:

| Component | Value |
|---|---|
| Quality | routine **2** · difficult **4** · challenging **6** |
| Stakes | safe **+0** · risky **+2** · dire **+4** |
| Lethal (`frame.stakes.lethal = true`), or **ruinous** outside conflict (03.4.5) `[revision: I-003]` | **+2** |
| Critical success | **+2** |
| Novelty (03.4.4) | **+2** |
| Failure or critical failure | the sum above is **halved, rounded down**. A Safe failure is never significant (D1). |
| Success at cost | counted as a success (no halving, no crit bonus) |

Range: 2 (routine, Safe, plain success; possible only for no-roll successes or under pressure from an
opponent or clock) to **16** (challenging, Dire, lethal, critical success, novel). A typical risky success at
the edge of ability scores 6; the same success when new scores 8. Each **secondary** tag receives
`floor(points / 2)`.

Why these steps: quality spans ×3 and stakes adds up to +4, so a challenging Dire success (10) is worth five
routine no-stakes successes (2). That is the scale of "real danger" versus "practice" in HWFWM's honest and
cheap paths [R2 §03], at a ratio small enough that one lucky, dramatic moment cannot outweigh a session of
steady play (03.3.4 item 6). Failure counts half because attempting hard things is itself how a character
grows, as in Burning Wheel, where failed tests count toward advancement and Blades rewards desperate rolls
whatever the outcome [R6 A-06, A-12]. It counts only half because a career of failures should not equal a
career of successes. The critical-success bonus is kept small (+2) because it is a 5–50% event that is mostly
luck [DL-03-03, DL-03-04].

**03.4.3 Challenge band.** `[D]` The 00.6.8 field `challenge_band` (1–5) is the **absolute** difficulty of the
obstacle, read from the frame's final DC: DC ≤ 12 → **1**; 13–17 → **2**; 18–22 → **3**; 23–27 → **4**; ≥ 28 →
**5**. This maps the reference ladder 10/15/20/25/30 one to one onto the five threat bands, and an opposed
defense of a band-N adversary falls in band N (00.3.7). A no-roll event uses the obstacle's stored DC or its
tier. A conduct-only event uses the highest threat band among aware opposing entities present, else 1. Quality
says how hard the deed was *for the character*; band says how great the deed was *in the world*. 04 needs
both. A tier-4 crystallization should be able to require a band-4 deed whatever the character's modifiers are
[R6 R-A4] [DL-03-23].
- **In a conflict** (a beat inside round-by-round play), `challenge_band` is instead the actor's
  `power_band` shifted by the conflict's `threat_advisory` word computed at framing (PR-09-4): trivial −2,
  easy −1, fair 0, hard +1, lethal +2, clamped 1–5. A hard fight is a band-up deed whether its difficulty
  came from one strong foe or from many weak ones, which T-09-10 makes the normal fair fight; with the foe's
  own band, a crowd of lower-band foes counted as a low-band deed and stalled tiers 3–5 (09.12.3: median tier
  sessions 7 / 20 / 31 / 46 / never, against 5 / 11 / 22 / 39 / 60 with this rule) [integration: DL-00-05;
  closes I-005]. Outside conflict the DC rule above stands, except in a contest.
- **In a contest** `[revision: I-003]`. A **contest** is a non-conflict undertaking with an opposing party or a
  work at stake, resolved over several beats: a social contest (a Talk frame on a request, bargain,
  deception, intimidation, interrogation, persuasion campaign or debate aimed at a principal or at someone who
  speaks for a faction; 15.3.11. The methods are closed `[revision: I-071]`: `smethod.request`, `bargain`,
  `deceive`, `intimidate`, `interrogate`, and every beat of a campaign (15.8.1) or a debate (15.8.3); never
  win over, provoke, perform, command or read, which move a person's feeling or obey an existing authority,
  not a party's position, and so earn the DC's band only), a craft contest (a step of a crafting project, 08.6.4) or a lore contest (a beat on
  a case or on research whose truth a principal or a faction keeps; 15.9.20). A beat in a contest takes
  `challenge_band = max(the DC's band, the contest band)`. The **contest band** is the opposition's, rated as
  a fight's is. For social and lore it is the opposing party's **own band** (its threat band where it has an
  adversary line, 09, else the `band` its NPC record holds, 12.11.1, 12.16.11; a principal with neither, 1),
  raised to the tier of the faction it acts for (11.3; tier 0–1 → 1, 2 → 2 … 5 → 5) **only when the party can
  bind that faction on the matter**: the faction's head or an officer (its `officers`, 11.3.17, 12.16.11), or
  a faction that keeps a truth itself (15.9.20). Anyone else who speaks for a faction (a door-warden, a clerk,
  a sworn member petitioned at the gate) counts its own band [revision: I-039]. For craft it is the work's
  **type-tier** (08.6.1). In every contest the contest band is **at most the actor's `power_band` + 2**, the
  most a fight lends (lethal +2) [revision: I-039]: a novice who bargains with a duke does a band-3 deed, not a band-5
  one, as a novice who survives a dragon does. It is engine-read from those records, never chosen. The
  record of the beat carries the contest's **opposition** (the party, case, research project or work), which
  04.3.4's great-deed count reads [revision: I-083]. *Why:* a deed's band is how great it is in the world, and a
  bargain struck with a duke or a blade made from dragon steel is a band-5 deed even when one exchange's DC
  is moderate; with the DC alone a smith's work could never rise above band 4 (wondrous work is Very hard)
  and the tier-5 great-deed requirement was closed to every crafter (`04-recog-parity.py`: tier 3 never
  reached in 90 sessions; with this rule 18 and tier 5 at 45, beside the archer's 19 and 51).

**03.4.4 Novelty and the context class.** `[D]` Each event's `context_class` is the first of:
(a) the opposing entity's most specific `creature` tag, truncated to level 2 (`creature.undead.ravenous`);
(b) the obstacle entity's most specific tag in any facet, truncated to level 2 (`item.tool.container`,
`terrain.highland.cliffs`);
(c) the scene's `situation` tag at level 2.
An event is **novel** when its context class does not appear among the actor's settled events on the same
**level-2 deed node** (the primary tag truncated to level 2, or the tag itself if shallower) within the recency
window (03.6.2). Novelty adds +2 (03.4.2). This rewards range within a skill (an archer who has shot wolves,
men, ghouls and a wyvern) without rewarding switching skills: the window is per node, and diminishing returns
apply anyway (03.5.2). The Alexandrian's diversification point is that varied tasks prevent
hyper-specialisation, and novelty is its positive form [R2 §03] [DL-03-08].

**03.4.5 Crisis and peak flags.** `[D]` Two flags that 04's crystallization and V5 awakening rules read
(T-03-11):
- **crisis** is true when any of: `lethal_context` is true; the actor's harm state was `staggered` or `dying`
  when the beat was declared; stakes are Dire **and** quality is challenging; the frame is **ruinous**; or
  the beat is declared in a contest **one from full** `[revision: I-003]` `[revision: I-046]`.
- **ruinous** `[revision: I-003]` is true for a frame outside conflict whose stakes are Dire and whose
  threatened cost at its critical-failure severity is irreversible in the world, read from the frame:
  `cost.closed_door` at S4–S5 against a principal NPC or a faction (a refusal for good, standing or
  faction status lost; 15.3.8); `cost.gear` on a unique item or an irreplaceable material (rarity 4, or a
  harvested part of a named source; 08.6.4); a necessary clue node or the case itself lost (15.9.20); or a
  project's spoilage completing on an irreplaceable material. Ruinous is to a contest what lethal is to a
  fight: it adds the same +2 (03.4.2) and makes a crisis. It is engine-derived from the declared cost, never
  judged after the roll.
- **one from full** `[revision: I-003]` (named so since [revision: I-046]; "brink" is chapter 07's word only: brink
  wounds, the brink menu, Dying at 1 + brink): a contest beat declared while the contest's opposing clock stands
  one segment from full (a persuasion campaign's patience, 15.8.1; a case's opposition clock, 15.9.13; a
  project's spoilage clock, 08.6.4). It is the contest's Staggered: the last chance before it is lost.
- **peak** is true when the degree is success or better **and** `challenge_band ≥ power_band(actor) + 1`
  (04's `power_band`; an unrecognized PC is band 1). A peak deed is beyond the character's established level
  of power. In a conflict this means a success in a fight whose advisory was hard or lethal (03.4.3).
Neither flag changes points. They are counted (`detail.crises`, `detail.peaks`) so that a higher tier can
demand "qualitatively distinct" evidence: deeds in crisis, and deeds beyond one's band [R2 #5;
R6 V5] [DL-03-18].

**03.4.6 Witnesses do not weight capability.** `[D]` Points are the same whether or not anyone saw the deed.
Witnesses decide only the **public** tally and its scope (03.10). Reasons: (a) a deed done alone in a dark
tomb is still done; (b) weighting by witnesses would push the player to perform for crowds and penalise the
stealth and wilderness callings, whose deeds are unseen by design; (c) the research separates the tally from
the witness and the moment [R6 executive summary #1, R-A1] [DL-03-09].

**03.4.7 Conduct and counted points are separate scales.** `[D]` Conduct points (±2 or ±4, 03.3.3) and counted
units (03.7) never mix with deed points. Each has its own tally family (03.9).

### 03.5 Settlement, saturation and anti-grind

**03.5.1 Evidence is settled at the end of the scene.** `[D]` `record_evidence` stores events as `pending`.
Settlement runs in the reserved handler **`h.03.antigrind_reset`** (`scene_end`, phase 9), whose behaviour this
rule defines (the reserved id is kept as 00 seeded it). It also runs in the added handler `h.03.day_settle`
(`day`, phase 9), which settles any scene still open when a day ends, so that a siege lasting three days
settles three times. Settlement is PR-03-2. Why settle per scene: a scene is one continuous situation with one
focus (00.18). It is the natural unit of "one demonstration", and settling as a batch lets diminishing returns
keep the **best** moments rather than the first ones [DL-03-05].

**03.5.2 Diminishing returns at every node.** `[D]` During settlement, every node of the tag tree (the primary
tag and every ancestor, and each secondary tag and every ancestor) collects the scene's contributions to it. An
event contributes to a node at most once, at its larger contribution there. The contributions are sorted
highest first:

| Rank in the scene at this node | Counts |
|---|---|
| 1st | full |
| 2nd | half (rounded down) |
| 3rd | a quarter (rounded down) |
| 4th and later | **0** |

The scene's settled contribution to a node is therefore at most 16 + 8 + 4 = **28**. Because diminishing
returns run independently at every level, switching weapons in one fight gains nothing at `deed.martial`. In
the simulation, identical fights fought with six different weapons gave `deed.martial` 1,106 points over 20
sessions, against 1,191 for the same fights with one weapon (T-03-9 C/C2). A fight with twelve beats shows the
skill about as well as a fight with three, which is the WoW diminishing-returns shape with the scene as the
reset window [R3 03.9; R: https://en.uesp.net/wiki/Skyrim:Sneak]. Conduct uses the same rule per axis and per
sign; counted evidence uses it per counter and node (03.7.3).

**03.5.3 The routine cap.** `[D]` At each node, **at most one routine-quality contribution counts per day**:
the highest. Later routine contributions to that node on the same day settle as 0 there. This is Burning
Wheel's "routine tests stop counting" stated per day, and it is what defeats grinding easy opposition. In the
simulation, a character who fought cellar rats in every scene of 20 sessions gathered **2,196** archery points
with no protection, **910** with diminishing returns alone, and **340** with diminishing returns and the
routine cap. A focused adventurer playing the same number of scenes as real fights gathered **≈1,030**. The
grinder's 340 points were also 100% routine quality, which 04's quality floors exclude (T-03-9 B) [DL-03-06].

**03.5.4 The same-target cap.** `[D]` An event whose `target` and level-2 deed node match an event already
settled **in an earlier scene of the same day** settles as 0 at every node. Within one scene, repeated beats
against one target are already handled by 03.5.2. This closes the farm-one-target loop: the healed horse, the
sparring dummy that is "risky" because it hits back, the guard who is persuaded again and again. A rematch on
a later day counts normally [R: https://en.uesp.net/wiki/Skyrim:Sneak; Ultima IV's step-counter cooldown]
[DL-03-07].

**03.5.5 Practice and training.** `[D]` Practice (Safe, unopposed, unclocked, routine) fails D2 and is never
judged evidence. Deliberate training is a downtime activity owned by 15. Each completed **week** of training
on a tag writes one counted event, `cnt.training` (1 unit, on the trained tag), and never judged points. 04
may let training count toward a tier's counted requirement (Kingdom Come's trainers: a mentor can speed
recognition up but never substitute for it [R6 A-27]). This keeps EVE-style time-gated learning available to
04 and 05 [C:P15] without letting a montage stand in for deeds.

**03.5.6 Provisional reading mid-scene.** `[D]` `tally(actor, tag, include_pending: true)` returns the values as
if the scene settled now. Only 04's crisis check (V5 awakening, which must fire inside a scene) may call it. The
pending events then settle normally at `scene_end`, so nothing is counted twice.

### 03.6 Recency, decay and supersession

**03.6.1 The recency clock is play, not the calendar.** `[D]` Each actor has an ordered list of
**evidence-bearing scenes**: scene-days in which the actor received at least one settled judged deed
contribution greater than 0. Recency is counted along this list, never in days or weeks. A winter spent
recovering in a monastery does not make a ranger forget the woods. The next time they act, their recent
history is still their history. A pivot in what the character does shows up as soon as they do it [R3 T-8,
G-3; R6 A-08 Avatar Legends' fast balance versus slow center] [DL-03-10].

**03.6.2 The recent value.** `[D]` For any node:
`recent = Σ settled points in the newest 12 evidence-bearing scenes + floor(Σ settled points in scenes 13–24 / 2)`.
Scenes older than 24 contribute nothing to `recent`. They remain in `weighted` permanently. The half-weighted
second block smooths the cliff at the window's edge. At the model's rate of five evidence-bearing scenes per
session, the window covers about five sessions of play. In the simulation, a character who switched from
archery to fire sorcery at session 11 had recent fire above recent archery by **session 12** (median; 10th–90th
percentile: 12–13), and recent archery reached 0 by session 15, five sessions after the switch (T-03-9 D).

**03.6.3 Cumulative weight never decays.** `[D]` `weighted` and `raw` only grow, except by the two explicit,
logged operations below. Who a character has been does not fade on its own (Delve's and EVE's counters are
permanent). Whether they still *are* that person is read from `recent`, and 04 uses it for maintenance,
provisional confirmation and relabelling offers [R3 T-8] [DL-03-11].
- **Void** (PR-03-4): an event recorded in error (a successful dispute, a claim-check correction, a reverted
  write per 12's `revert_writes`) is set `void`. Its scene is **re-settled** without it, so that other events
  can move up the diminishing-returns ranks, and every tally is recomputed.
- **Supersede** (03.8.4): only an `atonement` event supersedes, and only negative conduct entries.
Nothing else removes evidence. Evidence is never "reinterpreted" [R1 §03 explicit supersession].

**03.6.4 The reflection update.** `[D]` The reserved handler **`h.03.recency_update`** (`reflection`, phase 8)
runs before 04's `h.04.recognition_pass` in the same phase (registry order: owner 03 before 04, 00.7.5). It:
(1) runs the reflection sweep (03.3.5) and settles any events it adds; (2) recomputes `recent` for every node
and conduct axis; (3) builds the **reflection digest** for 04. The digest is sealed and lists: every node
whose `weighted` or `recent` changed since the last reflection (the dirty nodes); new crisis and peak events;
new conduct entries and changes in strain; new forbidden-act citations. 04 then evaluates only the candidates
keyed on dirty nodes or axes, which keeps the recognition pass bounded as the tag tree grows (Hades' and
Delve's low-cardinality keying, applied to work rather than to data) [R3 03.6, 03.11].

**03.6.5 `last_exercised`.** `[D]` For each node: the number of evidence-bearing scenes since its last settled
contribution, and the game time since then. Visibility is `background`. 12's rotation ledger may read it as a
complement to its own frame-based facet count (12.9.1) [R1 §03 spotlight data; R1 #8].

### 03.7 Counted evidence

**03.7.1 Two kinds of evidence, two tallies.** `[D]` Judged events (03.3) feed the **weighted** tallies.
Engine counters feed a separate **counted** tally per node, and the two are never summed. This is Delve's
dual-tier shape. The weighted tally is the "primary" (how well and how bravely the character has done this
kind of thing). The counted tally is the "secondary": a cumulative tally of mechanical outcomes (foes
defeated, Focus spent, harm warded, clocks advanced, things made) that no judgment touched [R3 03.4, 04.1, #4;
C:P5 dual-tier]. 04 is asked to require **both** for every recognition (Interface requests). Judgment can
inflate the first; nothing but play can inflate the second [DL-03-12].

**03.7.2 The counters.** `[D]` Each counter is an engine listener registered on one 00.10.2 hook. It is not an
effect. It observes the hook's event at **any depth**, because recording evidence is a core engine write and
never itself causes an event, so INV-12's loop concern cannot arise. Counters never listen to `on_tag_event`.
Canonical list: `data/evidence.yaml#counted`.

| Id | Hook | Fires when | Tag credited | Units |
|---|---|---|---|---|
| `cnt.defeat` | `on_defeat` | the actor's beat or ability defeats a foe (Staggered, Dying, dead, yields or flees) | the defeating frame's primary deed tag, or the ability's first deed tag | the foe's threat band (1–5); a mob or swarm entity counts once, at its band |
| `cnt.focus` | `on_focus_spent` | the actor spends Focus on an ability, or on a push (05.6.7) [integration: IR ch.05 to 03] | the ability's first deed tag; for a push, the frame's primary deed tag | Focus spent |
| `cnt.ward` | `on_harm_taken` (on the actor or on a being in the actor's scene) | harm of 1 or more was reduced or prevented by the actor's ability, item, or `shield.cover` or Help beat | the source's deed tag (through T-03-3 for items) | 1; **2** when the protected being is not the actor |
| `cnt.control` | `on_condition_applied` (`by` the actor, `to` a foe) | a condition of category physical, sensory, mental or positional, applied by the actor's beat or ability | that beat's primary tag or the ability's first deed tag | 1 |
| `cnt.progress` | `on_clock_tick` | a progress, project or tug clock ticks in the actor's favour from the actor's frame | the frame's primary deed tag | ticks |
| `cnt.made` | `on_item_acquired` | the item's provenance domain is `gen.craft` and its maker is the actor | the crafting frame's primary deed tag | the quality rung's index in 08's ladder (lowest = 1) |
| `cnt.discovery` | `on_fact_set` (`loc.*.discovered = true`) | written as the delivered result of the actor's frame; a discovery written with `frame_id: null` (mere arrival, 10.1.5) never counts: wandering in is not finding [integration: IR ch.10 to 03] | the frame's primary deed tag | 1 |
| `cnt.clue` | `on_fact_set` (`clu.*.found`, 15) | written as the delivered result of the actor's frame | the frame's primary deed tag | 1 |
| `cnt.lifesave` | `on_stabilize` (another being) | the stabilizing frame or ability was the actor's | that frame's or ability's tag | 3 |
| `cnt.journey` | `on_boundary` (`watch`) | time mode `travel`, and the actor held a journey role (10/16) for the whole watch | by role, `evidence.yaml#journey_roles` (navigator → `wilds.navigation.wayfinding`; scout → `wilds.tracking.sign`; forager → `wilds.foraging.food`; lookout → `wilds.survival.weathersense`; quartermaster → `wilds.survival.provisioning`, added by 16 at integration; 10/16 may extend) | 1; at most 2 per day |
| `cnt.training` | written by 15's training activity | a completed downtime week of training on a tag | the trained tag | 1 |

Counted events are `kind: counted` with `basis: hook` or `training`. They carry `frame_id` where one exists.
They pass no significance test, since a mechanical outcome is its own proof. They are pending until the scene
settles.

**03.7.3 Counted saturation.** `[D]` At settlement, counted units are capped per counter and per node exactly
as in 03.5.2 (1st full, 2nd half, 3rd a quarter, rest 0, sorted by units). The same-target day cap of 03.5.4
also applies (one counted defeat of one foe per day; a foe "defeated" twice by a yield and a re-escape counts
once). The routine cap does not apply, because counted events carry no quality. *Measured yield* `[revision:
I-004]` (`03-counted-yield.py`: chapter 06's conflict engine, 4,000 fights a row, this chapter's points and
saturation applied to every beat, defeat, flight and push): per fight at the weapon node a fighter of band
1–5 earns **1–4 counted units without Focus and 2–7 with pushes**, against 6–15 weighted points, a counted
share of **0.11 / 0.15 / 0.22 / 0.23 / 0.33** at bands 1–5 without Focus and **0.26–0.44** when pushing. The
social, craft and lore contests of 03.4.3 yield 0.31, 0.76 and 0.31 at the median (never below 0.24 at the
tenth percentile; `04-recog-parity.py` R9). Integer halving makes a
second band-1 defeat in one scene worth 0, which is why band 1 sits lowest; 04.3.3's divisor of 10 binds only
a band-1 fighter who meets nothing but mobs and never spends Focus, and costs that one fighter one extra fight
in eight (OEQ-03-4 answered; the live-play test stays).

**03.7.4 Counted evidence and abilities.** `[D]` `cnt.focus` is the evidence channel for magic and
active-ability callings, and it costs the DM nothing (R3 03.12: Delve counts the resource spent *through* a category of ability). Because
Focus is one pool [C:P9], spending it "through" an ability's tag is unambiguous. 05 must give every ability
at least one deed tag (its first `tags` entry is the one credited).

### 03.8 Conduct tallies

**03.8.1 Signed points.** `[D]` Each conduct entry carries an axis, a sign (+1 or −1) and a magnitude (2 or 4)
read from its ground (03.3.3). The conduct tally keeps the positive and negative poles separately; it never
nets them inside an event.

**03.8.2 Settlement.** `[D]` Per scene, per axis, per sign: diminishing returns of 03.5.2 (best full, second
half, third a quarter, rest 0). One scene's conduct on one axis and one sign is therefore at most 4 + 2 + 1 =
**7**.

**03.8.3 The conduct measures.** `[D]` For each actor and axis:
- `pos` (cumulative settled positive points); `neg` (cumulative settled negative points **not** superseded by
  atonement); `atoned` (negative points that atonement has superseded);
- `net = pos − neg` (may be negative: 00.5.3);
- `recent_net`: the same measure over the recency window of 03.6.2;
- **`strain`**: at each settlement, `strain = max(0, strain + neg_settled − floor(pos_settled / 2))`. Contrary
  deeds work strain off at **half** the rate at which wrongs build it. This is Stormlight's dimming bond and
  the Paladin who must atone rather than simply out-weigh [R2 #6; R6 A-01, A-02]. Strain never decays with
  time, only with deeds or atonement;
- `forbidden`: the count of unatoned events whose conduct entry cites a `forbidden_ref` (an act its oath
  forbids in advance; Ultima IV's Skull, R6 A-03);
- `last_negative_at`, `scenes_since_negative`;
- `witnessed_pos` and `witnessed_neg`: the parts of `pos` and `neg` whose events had at least one carrier
  (03.10). These are infamy and good name, for 11.

**03.8.4 Atonement.** `[D]` Atonement is 04's procedure (the V14 Fraying offers "atone or turn"). When an
atonement is completed, 04 calls `record_evidence` with `basis: atonement`, the axis, and `supersedes`: the
negative events it answers for (default: every unatoned negative event on that axis). The engine moves their
points from `neg` to `atoned`, sets that axis's `strain` to 0, and clears superseded forbidden citations unless
04's oath entry marks that act as unatonable. The ledger keeps every superseded event, marked `superseded`,
because the world remembers: `witnessed_neg` and 11's reputation are unchanged. Atonement changes who the
character is, not what they did [R1 §03; C:P5 "atone rather than instantly and irreversibly losing power"]
[DL-03-13].

**03.8.5 What 04 reads for oaths, shadows and the Fraying.** `[D]` This chapter supplies measures, and 04
supplies thresholds and staging:
- **Oaths:** an oath commitment (04) names one or more axes, and it may list forbidden acts. Its health reads
  `conduct(axis)`: `strain` (the Fraying track), `forbidden` (a break) and `net` or `recent_net` (whether the
  oath is being *lived*, for crystallization).
- **Shadows:** a calling's shadow (R6 R-A6) is authored by 04 as (a) a negative pole on one or two axes and/or
  (b) **excess** on its own deed key. For (a), 04 reads `recent_net` and `strain` on those axes. For (b), it
  reads `dominance` and `share` of the calling's key against its siblings and parent (03.9.3), for example a
  protector whose `martial` share of `deed` passes 3/4 while `conduct.restraint` is net negative.
- **The Fraying:** 04 stages its warnings on `strain`. *Defaults this chapter proposes, from the simulation:*
  an honest, occasionally merciful character gained about **1 positive mercy point per session** (median net
  +12 by session 20; T-03-9 A). One grave act (4 points of strain) then takes **8** positive points to work
  off, which is several sessions of real mercy. That gives proposed stages of **4** (first warning: the
  witness withdraws), **8** (the witness speaks), **12**, or any forbidden citation (the offer: atone or
  turn), so that a single act only warns. This follows R6 V14's "a single contradictory act only warns" [R6
  V14]. 04 owns the final numbers.

### 03.9 The sealed tally functions

**03.9.1 Access.** `[S]` + `[D]` Every function in this part is sealed (00.6.5). They are callable by 04's
recognition handlers and tools (`evaluate_recognition`, `h.04.*`). Three are exposed to other chapters and
return no weights: `public` to 11, `last_exercised` to 12, and `evidence_for_frame` to 07 and 11 (background). Nothing here is ever returned to the narrator's
context. The codex shows the ledger lines only (03.11). Seer-type readings (04's V6) are 04's qualitative
bands computed from these values, never the values themselves [R4 §9 03 #2].

**03.9.2 `tally(actor, tag, include_pending = false) → {raw, weighted, recent}`.** `[D]` The 00.17.2 contract
function, defined exactly:
- `raw`: the number of settled judged deed events whose settled contribution to `tag`'s node is greater than
  0;
- `weighted`: the sum of settled judged contributions to the node, all time (03.6.3);
- `recent`: 03.6.2;
- the node of a tag includes its descendants, by cascade (00.5.4). For a conduct axis, use `conduct()`
  (03.9.3). `tally` on a conduct tag returns `{raw, weighted: pos − neg, recent: recent_net}`, for 00
  consumers that ask generically.

**03.9.3 Derived measures for scoring.** `[D]` All are integers or rational pairs `{num, den}` compared by
cross-multiplication (`share ≥ p/q ⇔ q·num ≥ p·den`). Percentages are never stored (SG-23) [DL-03-17].

| Function | Returns | Definition |
|---|---|---|
| `detail(actor, tag, since = null)` | `{raw, weighted, recent, secondary_weighted, successes, failures, by_quality {routine, difficult, challenging}, by_band [b1..b5], success_by_band [b1..b5], peak_band, crises, peaks, distinct {scenes, days, contexts, opponent_kinds, opponent_kinds_nonfolk, places, children}, first_at, last_at, scenes_since_last}` | counts are of settled contributions > 0 at the node. `since` restricts every field to events after a time **or a scene index** (04 passes the last crystallization); `distinct.scenes` under `since` is the evidence-bearing scene count since then. `by_band` counts every settled contribution; `success_by_band` counts successes only, and `peak_band` is the highest band **among successes**. `distinct.opponent_kinds_nonfolk` counts distinct opposing creature kinds outside `creature.folk` (04's Devourer). `distinct.children` = how many of the node's direct children have weighted > 0 [integration: IR ch.04 to 03] |
| `share(actor, tag)` | `{num, den}` | `num = weighted(tag)`; `den = weighted(parent(tag))`. For `deed` itself, `{num, num}` |
| `dominance(actor, tag)` | `{lead, rival, num, den}` | `rival` = the sibling with the largest weighted (ties: data order); `lead = weighted(tag) − weighted(rival)`; `num = weighted(tag)`; `den = weighted(tag) + weighted(rival)` |
| `profile(actor, facet = deed, level = 1)` | `[{tag, weighted, recent, raw}]` | every tag of that facet at that level with weighted > 0, sorted by weighted, highest first |
| `cooccurrence(actor, a, b)` | `{weighted_a, weighted_b, min, balance {num, den}, joint_events, joint_scenes, recent_min}` | `a` and `b` must not be ancestor-related. `min` = the smaller weighted; `balance = {min, max}`; `joint_events` = settled events that credited both nodes (a primary and a grounded secondary); `joint_scenes` = evidence-bearing scenes in which both nodes received > 0; `recent_min` = the smaller recent |
| `diversity(actor, tag)` | `detail(...).distinct` | for hybrid and generalist callings, and anti-grind floors |
| `conduct(actor, axis)` | `{pos, neg, atoned, net, recent_net, strain, forbidden, last_negative_at, scenes_since_negative, witnessed_pos, witnessed_neg, pos_events, pos_events_m4}` | 03.8.3; `pos_events` = settled positive entries, `pos_events_m4` = those of magnitude 4 (for qualitative vow-tier requirements) [integration: IR ch.04 to 03] |
| `counted(actor, tag)` | `{units, recent_units, by_counter {cnt.*: units}}` | 03.7; `recent_units` over the window of 03.6.2 |
| `public(actor, tag, scope)` | `{weighted, events, last_at}` | 03.10.5 |
| `last_exercised(actor, tag)` | `{scenes_since, time_since}` | 03.6.5 |
| `evidence_for_frame(frame_id)` | `[{event_id, tags}]` | ledger lines only (no points); for 07's marks and 11's chronicle |

**03.9.4 Specialist, hybrid and qualitatively distinct evidence: what 04 can require.** `[N]` These are
illustrations of the measure shapes 04 can combine into its dual-tier thresholds. The numbers are 04's to set,
with T-03-10 as calibration:
- *Specialist at any depth* [C:P5]: `tally(tag).weighted ≥ W` **and** `counted(tag).units ≥ C` **and**
  `detail(tag).by_quality.difficult + challenging ≥ k` **and** `detail(tag).distinct.scenes ≥ s`. The quality
  floor is what makes the grinder ineligible (100% routine, T-03-9 B). The distinct-scenes floor is what makes
  a single lucky fight ineligible.
- *Hybrid* [C:P5 curated table keyed on two deed branches]: `cooccurrence(a, b).min ≥ M` **and** `balance ≥
  1/3` **and** `joint_scenes ≥ j`. In the simulation, a branch used in 15% of scenes reached a balance of 0.12
  (influence) or 0.23 (wilds) against the main branch; a branch that was a second pillar of play (stealth
  in 25% of scenes, plus ambush secondaries) reached 0.34; deliberate hybrid play reached about 1.0. A floor
  of 1/3 therefore rejects incidental play, admits deliberate hybrids, and puts the two-pillar character on
  the line, where an *offer* (never a grant) is the right policy (T-03-10; R3 G-1's acceptance test).
- *Qualitatively distinct evidence for higher tiers* [R2 #5; R6 R-A4]: `detail(tag, since = last_tier)` with
  `crises ≥ 1`, `peaks ≥ 1` or `peak_band ≥ N`, `distinct.contexts ≥ c`, or `by_quality.challenging ≥ k`.
  Each is a different *kind* of evidence that repetition cannot produce: a crisis cannot be ground out, a peak
  needs a stronger foe, and new contexts need new places and foes.
- *Maintenance and relabel* [R3 T-8]: `tally(tag).recent ≥ R` to confirm a provisional grant, and `recent`
  falling to 0 (or below a rival's recent) to trigger a relabel *offer*.
- *Confidence* (04 must define it [BRIEF A3]): suggested inputs are threshold margins expressed as rational
  pairs, `balance`, and `recent / weighted`. This chapter fixes the inputs, never the formula.

**03.9.5 Determinism and audit.** `[D]` Every function is a pure function of the settled ledger, so recomputing
from the ledger alone gives the same values (RC-LOG + RC-QUERY). Any value 04 used to grant or offer is
logged with the offer (04's `recognition_event`), so the reason for any recognition can be audited back to deed
lines.

### 03.10 Witness and scope

**03.10.1 Who witnessed.** `[J:flag]` per present entity, with an engine default

```
### 03.10.1  Witnesses of a deed                                  [J:flag] [D]
Trigger [T]:        record_evidence for a judged event (and each conduct-only event)
Loads in:           core
License check:      n/a
Decisions (J):      1. PERCEIVED [J:flag] for each entity present in the scene: "Could this entity perceive
                       the act as it happened?" Engine default TRUE when the entity is in the scene,
                       conscious, not `unaware` (alertness), and the beat carries trait.sense.visible (line of
                       sight per 06's bands and flags) or trait.sense.audible/loud (within hearing); default
                       FALSE otherwise. The DM may flip a default only by citing a fact id (darkness,
                       a wall, flag.hidden, a sense condition). A successful stealth beat is, by its own
                       result, unperceived by those it evaded.
Computation [D]:    witness_detail; carriers (03.10.2); scopes (03.10.4) at settlement
Stakes:             none
State writes:       event.witnesses, witness_detail
Narration may not imply: that a witness will talk, or what it thinks (11/15 decide reactions)
Worst case (J):     a witness wrongly included adds the event to the public tally of one or a few scopes
                    (reputation, 11): no capability changes (class iv, correctable by PR-03-4); wrongly
                    excluded: the deed stays private, recoverable by an aftermath witness (03.10.3).
Examples:           inside: the caravan guards watch Wren's arrow drop the wyvern at the ford -> witnesses
                      (visible, near).
                    boundary: the same shot from a hidden hayloft, the guards facing away -> not witnesses;
                      the wyvern is a witness but not a carrier (a beast).
                    non-example: "Everyone in town will hear about this!" -> an assertion; carriers are
                      decided by 03.10.2, rumor by 11.
Anchor:             no
Basis:              [R6 A-15 Ars Magica: witnesses who will talk; R-A1 witness gate] [00.6.8 witnesses]
```

**03.10.2 Carriers.** `[D]` A witness is a **carrier** (it can spread the deed) when all hold at settlement:
(a) it can tell others: a being of `creature.folk`, `creature.spirit`, `creature.fiend` or
`creature.undead.sovereign`, or any entity flagged `speaks: true` (09, 16), or a companion; (b) it still exists
or has departed (`exists ∈ {exists, departed}`), so a captured witness counts and a slain one does not; (c) no
commitment binds it to silence about this act (a bribe, an oath of secrecy, a fact). Beasts, mindless undead
and constructs witness but do not carry. Foes who survive are carriers. Their recognition often comes first
(R6 V8, the Nemesis rival) [R6 A-20].

**03.10.3 Aftermath witnesses.** `[D]` + `[J:flag]` A deed can become known later: bodies found with the PC's
fletching, a theft traced through a fence. When a fact written later links a recorded event to its actor in
some NPC's knowledge (`record_knowledge`, 15), the DM calls `add_witness(event_id, entity, how: aftermath,
fact_id)`. The flag is *"Does the cited fact identify this actor as the doer to this entity?"*; uncertain →
no. The event enters that entity's scopes at the next settlement. Capability is unchanged. *Worst case (J):* a
reputation entry in one scope (class iv).

**03.10.4 Bonded witnesses.** `[D]` An entity named in a bond or oath record by 04 (a god, a patron, an order,
a bonded spirit) witnesses **every** event on the bond's axes and tags wherever it happens (`how: bonded`). It
carries only to its own scope (the order's faction id), and it never counts toward local reputation. This is
how an oath's keeper "knows" without being present (R6 A-01, A-02).

**03.10.5 Scope and the public tally.** `[D]` An event's `scopes` are the union, over its carriers, of each
carrier's home settlement (the nearest ancestor place tagged `terrain.settlement.*`), each carrier's faction
memberships (`fac.*`), and the scene's settlement if the act happened inside one with any carrier present.
`scope` (the 00.6.8 field) is the most local of these. `public(actor, tag, scope)` sums settled contributions
of events whose scopes include `scope`. At each settlement the engine sends 11 one **`public_deed`** packet per
carried event: `{event_id, actor, deed line, primary_tag, branch, conduct entries (axis, sign, magnitude),
noteworthy: bool, scopes, carriers}`. `noteworthy` is true when the event's settled contribution at its
primary node is at least **6** (a difficult, risky success or better), or any conduct entry has magnitude 4.
This is Ars Magica's "noteworthy act in front of witnesses who will talk" made exact [R6 A-15]. 11 owns
reputation content, score and spread, and epithets (V1) [00.17 Q22].

**03.10.6 Witnesses never change points.** `[D]` See 03.4.6.

### 03.11 The evidence ledger and the codex

**03.11.1 What the player sees.** `[D]` The evidence ledger is `available` (00.6.3). On request, the codex
(14) shows each settled event's deed line, primary and secondary tags, conduct axes and signs (not
magnitudes), scene and time, and witnesses the PC knows of, plus each event's status (settled, void,
superseded). It never shows points, tallies, recent values, thresholds or nearness. Pending events appear once
settled. The ledger is the player's view into "what the world has seen me do", and it is the basis for
disputes [R2 §03 Voyager; R6 A.5 item 1].

**03.11.2 Disputes and corrections.** `[D]` A player may dispute a ledger line out of fiction (12.3.6): wrong
tag, wrong sign, or "that never happened". If 12's dispute procedure upholds the objection, PR-03-4 voids or
re-records the event. If 12's claim check (12.3) or a `revert_writes` removes a write that an event cited as its
ground or frame, the event is voided automatically. A lenient error in the player's favour is still an error.
The DM corrects it when found, and the correction is logged like any other.

---

## Procedures

**PR-03-1 Recording evidence at RECORD.** `[J:enum]` + `[J:flag]` + `[D]` (the DM's steps; 01.12.1 step 4,
turn-loop step T6 of PR-12-1)
1. For each beat resolved this turn, check its basis (03.3.1). A beat with no resolved basis is skipped.
2. Write the **deed line** (03.2.4) from the frame's neutral restatement (01.2.6) and its recorded result.
3. The primary tag is the frame's `deed_tag` (03.1.5). Do not re-classify after the roll.
4. Propose at most two **secondary** tags, each with a ground (03.1.6). If there is no ground, propose none.
5. Ask the conduct trigger of 03.3.3: did this beat or choice write something that affected another being's
   welfare, a promise, a truth, a rite, or the actor's own gain? If yes, answer its three decisions and cite
   the refs. If any answer is "uncertain", record no conduct.
6. List **witnesses**: accept the engine's default list, and flip an entry only with a fact id (03.10.1).
7. Write the one-line **justification**.
8. Call `record_evidence`. The tool validates, computes and stores, and returns only an id (03.2.2). On a
   refusal, read the reason; correct an input error once; never re-submit a refused event with a different
   basis.
9. Do not mention the recording in narration. Narration may not imply that a deed "counted" (00.1.7).

**PR-03-2 Scene settlement.** `[D]` (handler `h.03.antigrind_reset` at `scene_end`, phase 9; `h.03.day_settle`
at `day`, phase 9, for scenes still open)
1. Collect the scene's pending events, by actor.
2. **Witnesses and carriers:** for each event, mark carriers (03.10.2) using the entities' state now, add
   bonded witnesses, and compute `scopes` (03.10.5).
3. **Same-target cap:** set to 0 the points of any judged or counted event whose (target, level-2 deed node)
   was settled in an earlier scene of the same day (03.5.4).
4. **Contributions:** for each judged deed event, the primary tag contributes `points` to its node and every
   ancestor. Each secondary tag contributes `floor(points / 2)` to its node and every ancestor. An event
   contributes to a node once, at the larger value.
5. **Routine cap:** at each node, among routine-quality contributions, keep only the highest if no routine
   contribution has yet counted at that node today; otherwise keep none (03.5.3).
6. **Diminishing returns:** at each node, sort the remaining contributions highest first (ties: earlier event
   first); settle the 1st in full, the 2nd at half, the 3rd at a quarter (each rounded down), and the rest at
   0 (03.5.2).
7. **Conduct:** per axis and sign, apply step 6 to the entries' magnitudes; update `pos`, `neg` and `strain`
   (03.8.3).
8. **Counted:** per counter and node, apply steps 3 and 6 to the units; add to the counted tallies.
9. Write `settled.points_by_node` on each event; set `status: settled`; update `raw`, `weighted` and the
   detail counters (quality, band, crises, peaks, distinct sets).
10. If the actor received any judged deed contribution greater than 0, append this scene-day to the actor's
    evidence-bearing list (03.6.1) and update `last_exercised`.
11. Send 11 one `public_deed` packet per carried event (03.10.5).
12. Fire `on_tag_event` once per settled event with points greater than 0 (a depth-0 boundary-handler event,
    00.10.8), with the event's tags as parameters. Counters ignore it.
13. Return nothing to the narrator.

**PR-03-3 Reflection update.** `[D]` (handler `h.03.recency_update` at `reflection`, phase 8, before
`h.04.recognition_pass`)
1. Run the reflection sweep (03.3.5): list qualifying frames with no judged event; for each one the DM
   records, settle it into its original scene by re-running PR-03-2 steps 3–10 for that scene.
2. Recompute `recent`, `recent_net` and `recent_units` for every node and axis touched since the last
   reflection.
3. Build the sealed reflection digest (03.6.4) and hand it to `h.04.recognition_pass`.

**PR-03-4 Voiding and correcting.** `[D]` + `[J:flag]`
1. Trigger: a dispute upheld under 12.3.6; a claim-check correction; a `revert_writes` that removed a write an
   event cites; or the DM finding its own error (`[J:flag]`: *"Does state no longer support this event's
   basis, tag or ground?"* True only when the cited frame, write or fact is gone or contradicts the event.
   *Worst case:* a correct event voided; it can be re-recorded from its frame at the next reflection sweep,
   class iv).
2. Set the event `void` with `void_reason`. A wrong tag or sign is corrected by voiding and re-recording from
   the same frame, never by editing.
3. Re-settle the event's scene (PR-03-2 steps 3–10) without the voided event. Recompute every tally,
   evidence-bearing list entry and public tally that the scene touched.
4. If 04 granted or offered anything on values that included the voided event, 04's own rules decide what
   happens; provisional grants are re-checked at the next boundary (00.17 Q12). This chapter only reports the
   change in the next reflection digest.
5. Log the correction in the write log. Tell the player out of fiction that a ledger line was corrected
   (12's corrections ledger).

**PR-03-5 Adding an aftermath witness.** `[J:flag]` + `[D]` See 03.10.3: cite the fact;
`add_witness(event_id, entity, how: aftermath, fact_id)`; the next settlement recomputes that event's scopes
and sends 11 a `public_deed` packet for the new scopes only.

**PR-03-6 Admitting a tag (levels 3 and 4).** `[D]` (extends PR-00-8; used for other chapters' proposals in
`data/contrib/tags.NN.yaml` and for this chapter's own later additions)
1. **Search.** Does an existing tag's definition already cover the proposed kind? If so, add the proposal's
   name to that tag's `aliases` and rewrite the proposing data to the existing id. Stop.
2. **Facet and parent.** Exactly one parent. The parent's definition must be true of the new kind. If two
   parents fit, the proposal is two kinds, or the parent tags need a sharper distinguishing test first.
3. **Depth.** Level 3 freely. Level 4 only if a data entry (a calling key, a pool gate, a competence entry,
   an archetype) needs a distinction that no level-3 tag makes; cite the entry.
4. **Kind, not individual** (00.5.5 rule 7). "Cinder hound" as a kind of fire-touched canine is a tag
   candidate only if several data entries share it. One creature is an entity.
5. **Entry form.** Snake_case segment; "True only when … False for … (sibling id)"; a `distinguish` test
   against every sibling whose scope it could overlap; positive scope only (SG-15); at least two `aliases`;
   `lifecycle: provisional`.
6. **Sibling budget.** A parent keeps at most **8** children (the `[J:enum]` limit of 00.2.2). A ninth
   requires first regrouping the siblings under the parent, with a DL entry.
7. **Never rename.** A wrong name is fixed by a new tag plus `lifecycle: retired` and `superseded_by` on the
   old one. Evidence already recorded on a retired tag is carried to its successor by the engine (the
   successor's node includes the retired tag's settled contributions).
8. Record the admission in the Decision Log (one line per batch).

---

## Tables

Tables embedded in Rules are canonical there and indexed here: **T-03-5** quality rungs (03.4.1); **T-03-6**
points (03.4.2); **T-03-7** counters (03.7.2); **T-03-11** sealed functions (03.9.3). Every number is in
`data/evidence.yaml`; every tag is in `data/tags.yaml`.

**T-03-1 The deed vocabulary at level 3.** `[D]` (index; definitions, tests and aliases are in `data/tags.yaml`, which is canonical). 9 branches, 81 level-2 tags (79 seeded by 00, 2 added here, marked +), 270 level-3 tags.

| Level-2 tag | Level-3 children |
|---|---|
| `deed.martial.blade` | `sword`, `greatsword`, `fencing`, `dagger` |
| `deed.martial.axe` | `hand`, `great` |
| `deed.martial.bludgeon` | `club`, `mace`, `hammer`, `flail` |
| `deed.martial.polearm` | `spear`, `halberd`, `staff` |
| `deed.martial.archery` | `bow`, `crossbow`, `sling` |
| `deed.martial.thrown` | `javelin`, `blades`, `improvised`, `entangling` |
| `deed.martial.unarmed` | `striking`, `wrestling`, `natural` |
| `deed.martial.shield` | `block`, `bash`, `cover` |
| `deed.martial.armor` | `bulwark`, `encumbered` |
| `deed.martial.tactics` | `ground`, `maneuver`, `reading`, `single_combat`, `battle`, `siege` |
| `deed.martial.mounted` | `charge`, `skirmish`, `beast` |
| `deed.martial.athletics` | `climbing`, `jumping`, `swimming`, `running`, `lifting`, `acrobatics` |
| `deed.guile.stealth` | `hiding`, `sneaking`, `shadowing`, `infiltration` |
| `deed.guile.thievery` | `lockpicking`, `pickpocketing`, `sleight`, `traps` |
| `deed.guile.deception` | `lying`, `misdirection`, `feint`, `con` |
| `deed.guile.disguise` | `costume`, `impersonation`, `forgery` |
| `deed.guile.ambush` | `assassination`, `waylaying`, `sniping` |
| `deed.guile.poisoncraft` | `envenoming`, `dosing` |
| `deed.guile.escape` | `bonds`, `breakout`, `evasion` |
| `deed.guile.streetwise` | `fences`, `informants`, `smuggling`, `cant` |
| `deed.wilds.survival` | `shelter`, `firecraft`, `weathersense`, `hardship`, `provisioning` (adopted at integration) |
| `deed.wilds.tracking` | `trailing`, `sign`, `hunting` |
| `deed.wilds.navigation` | `wayfinding`, `underways`, `stars`, `mapping` |
| `deed.wilds.animals` | `riding`, `training`, `calming`, `husbandry`, `falconry` (adopted at integration) |
| `deed.wilds.foraging` | `food`, `water`, `herbs`, `harvest` |
| `deed.wilds.seafaring` | `sailing`, `piloting`, `boatwork` |
| `deed.lore.history` | `heraldry`, `ruins`, `legends` |
| `deed.lore.languages` | `ancient`, `ciphers`, `translation` |
| `deed.lore.bestiary` | `beasts`, `monsters`, `dead`, `otherworldly`, `dragons` |
| `deed.lore.medicine` | `surgery`, `diagnosis`, `remedies`, `toxicology` |
| `deed.lore.engineering` | `mechanisms`, `structures`, `siegecraft`, `waterworks` |
| `deed.lore.law` | `courts`, `custom`, `contracts` |
| `deed.lore.arcana` | `identification`, `theory`, `planes` |
| `deed.lore.religion` | `pantheon`, `rites`, `profane` |
| `deed.lore.investigation` | `search`, `deduction`, `records`, `inquiry` |
| `deed.arcane.fire` | `blast`, `shaping` |
| `deed.arcane.frost` | `blast`, `shaping` |
| `deed.arcane.storm` | `lightning`, `wind`, `thunder` |
| `deed.arcane.earth` | `stone`, `metal`, `tremor` |
| `deed.arcane.illusion` | `glamour`, `phantasm`, `veiling` |
| `deed.arcane.divination` | `scrying`, `foresight`, `tracing`, `detection` |
| `deed.arcane.warding` | `shielding`, `sealing`, `dispelling`, `countering` |
| `deed.arcane.mind` | `charm`, `compulsion`, `telepathy`, `memory` |
| `deed.arcane.summoning` | `calling`, `binding`, `banishing`, `familiar` |
| `deed.arcane.necromancy` | `raising`, `draining`, `communing`, `withering` |
| `deed.arcane.alteration` | `transmutation`, `flesh`, `enhancement`, `motion`, `translocation` |
| `deed.divine.healing` | `mending`, `purging`, `sustaining` |
| `deed.divine.warding` | `sanctuary`, `consecration`, `blessing` |
| `deed.divine.smiting` | `radiance`, `weapon`, `judgment` |
| `deed.divine.rites` | `funerary`, `bonding`, `seasonal`, `purification` |
| `deed.divine.oaths` | `swearing`, `binding` |
| `deed.divine.revelation` | `visions`, `prophecy`, `discernment` |
| `deed.divine.exorcism` | `turning`, `banishing`, `dispossession` |
| `deed.divine.pact` | `invocation`, `bargaining`, `sacrifice` |
| `deed.primal.growth` | `entangling`, `bounty`, `thorns`, `renewal` |
| `deed.primal.beastkin` | `speech`, `calling`, `senses`, `bond` |
| `deed.primal.weather` | `wind`, `rain`, `storm`, `mist`, `calm` |
| `deed.primal.shapeshifting` | `beast_form`, `partial`, `elemental_form` |
| `deed.primal.spirits` | `speaking`, `bargaining`, `binding`, `ancestors` |
| `deed.primal.elements` | `fire`, `water`, `earth`, `air` |
| `deed.primal.hexcraft` | `cursing`, `unhexing`, `charms` |
| `deed.influence.persuasion` | `argument`, `appeal`, `rapport` |
| `deed.influence.command` | `rallying`, `directing`, `discipline` |
| `deed.influence.performance` | `music`, `oratory`, `storytelling`, `spectacle` |
| `deed.influence.intimidation` | `threat`, `display`, `interrogation` |
| `deed.influence.intrigue` | `networks`, `alliances`, `leverage` |
| `deed.influence.trade` | `haggling`, `appraisal`, `venture` |
| `deed.influence.etiquette` | `courtly`, `foreign` |
| `deed.influence.insight` | `lies`, `motives`, `empathy` |
| `deed.influence.teaching` + | `instruction`, `mentoring` |
| `deed.craft.smithing` | `weapons`, `armor`, `tools` |
| `deed.craft.woodcraft` | `bowyery`, `carpentry`, `carving` |
| `deed.craft.leathercraft` | `tanning`, `goods` |
| `deed.craft.textiles` | `weaving`, `tailoring`, `ropework` |
| `deed.craft.alchemy` | `potions`, `poisons`, `reagents`, `incendiaries` |
| `deed.craft.cookery` | `provisions`, `feasting`, `brewing` |
| `deed.craft.building` | `masonry`, `fortification`, `field_works` |
| `deed.craft.artifice` | `locks`, `traps`, `clockwork`, `siege_engines` |
| `deed.craft.jewelcraft` | `gemcutting`, `goldwork` |
| `deed.craft.enchanting` | `inscription`, `imbuing` |
| `deed.craft.scribing` + | `copying`, `cartography` |

**T-03-2 Default tag by basic verb, used when the branch is uncertain.** `[D]` (`evidence.yaml#verb_default_tag`)

| Verb | Default tag | Note |
|---|---|---|
| `verb.strike` | `deed.martial` | then child by the weapon (T-03-3) |
| `verb.grapple` | `deed.martial.unarmed.wrestling` | |
| `verb.force` | `deed.martial.athletics.lifting` | |
| `verb.exert`, `verb.move` | `deed.martial.athletics` | a quiet move is `guile.stealth` by method |
| `verb.evade` | `deed.martial` | |
| `verb.sneak` | `deed.guile.stealth` | |
| `verb.talk` | `deed.influence` | a falsehood is `guile.deception` by method |
| `verb.recall` | `deed.lore` | |
| `verb.observe`, `verb.handle`, `verb.endure` | `deed` (the root) | noticing, plain handling and enduring show no branch; a searching, crafting, animal-handling or knowledge method takes that branch's tag |
| `verb.setup`, `verb.help` | by method | the tag of what the character does to set up or help |
| `verb.ready` | none | no roll, no evidence |

**T-03-3 Item → deed grounding.** `[D]` (`evidence.yaml#item_grounding`; summary) An item used as the beat's
tool or weapon grounds the listed deed tag as a secondary (03.1.6). Each `item.weapon.*` level-3 tag maps to
the `deed.martial.*` level-3 tag of the same weapon (`item.weapon.blade.rapier` → `deed.martial.blade.fencing`;
`item.weapon.polearm.lance` → `deed.martial.mounted.charge`; every bow → `deed.martial.archery.bow`). Shields
→ `deed.martial.shield`. Medium and heavy armor → `deed.martial.armor`. Kits: thieves' → `deed.guile.thievery`;
healer's → `deed.lore.medicine`; climbing → `deed.martial.athletics.climbing`; disguise →
`deed.guile.disguise.costume`; forgery → `deed.guile.disguise.forgery`. Instruments →
`deed.influence.performance.music`. Trade tools → `deed.craft`. Bottled poison → `deed.guile.poisoncraft`.
Mounts → `deed.wilds.animals.riding`. Vessels → `deed.wilds.seafaring`. **Implements ground nothing**: a magic
tag is grounded by the ability or license used, never by holding a wand.

**T-03-4 Conduct act tests.** `[J:enum]` Canonical in `data/evidence.yaml#conduct_tests`. An entry is recorded only when the pole's test is met word for word **and** 03.3.3's alternative and ground flags are true. Magnitude (2 or 4) is read by the engine from the ground.

| Axis (+ pole / − pole) | Positive act test (+1) | Negative act test (−1) | Not evidence | Sibling test |
|---|---|---|---|---|
| `conduct.mercy` (merciful / cruel) | Spares, heals, frees or eases a defeated, helpless or surrendering being that was in the actor's power, at a cost or risk to the actor (a threat left alive, a gain forgone, time or supply spent). | Kills, maims, torments or leaves to die a being that was helpless, surrendering or no longer a threat, when sparing it was plainly open. | sparing because ordered or forced; killing a foe who is still fighting; letting a foe go who had already escaped (no power over them) | vs protection: the being was in YOUR power -> mercy; in danger from OTHERS -> protection. vs restraint: mastering your own rage -> restraint (both may apply). |
| `conduct.honesty` (truthful / deceitful) | Tells a truth, admits a fault, or refuses a useful lie when the falsehood would plainly have served the actor, and it costs them standing, coin, position or safety. | Deceives a being who trusted or relied on the actor's word, for the actor's own gain or to escape a deserved consequence. | lying to an enemy during a fight, infiltration or con (a guile deed; no trust was given); tact, silence or keeping a secret without a falsehood; deceiving to protect an innocent, with no gain to the actor | vs loyalty: honesty is about truth told; loyalty about faith kept. |
| `conduct.courage` (brave / craven) | Takes on a declared Dire or lethal danger, or stands when flight was plainly open, for a purpose beyond the actor's own gain or survival. | Abandons a charge, companion or sworn post to danger out of fear when standing was plainly possible. | recklessness with no purpose; a prudent retreat that takes one's charges along; fighting when cornered (no alternative) | vs protection: facing the danger -> courage; doing it for the vulnerable's sake -> protection (both may apply). |
| `conduct.loyalty` (faithful / treacherous) | Keeps faith with a person, bond, oath or cause when breaking it would plainly have profited or protected the actor. | Betrays a person, bond, oath or cause that trusted the actor: breaks a promise, changes sides, sells them out. | declining to make a promise; leaving after a bond was openly and lawfully ended; obeying under immediate threat (compelled) | vs honesty (above). vs piety: a bond with people or a cause -> loyalty; with the sacred -> piety. |
| `conduct.generosity` (generous / greedy) | Gives away wealth, supply, a reward or a benefit that matters to the giver (at or above the ground floor), with nothing asked in return. | Takes, withholds or hoards at clear expense to those in need or those owed: robbing the poor, refusing owed wages, profiteering on distress. | buying, tipping or paying a debt; a gift made to purchase influence (an intrigue or trade deed); a gift below the ground floor for the giver's means | vs protection: giving goods -> generosity; giving safety -> protection. |
| `conduct.justice` (just / unjust) | Upholds a fair outcome or rights a wrong at cost or risk: returns what was stolen, testifies, refuses a bribe, brings the guilty to answer by fair means. | Punishes one known or likely innocent, frames someone, or lets the guilty escape for the actor's own gain. | private vengeance without process (test restraint instead); sparing the guilty out of pity (mercy +, and justice - only if the guilty thereby escapes answer) | vs mercy: justice weighs deserts; mercy tempers them. One act may score both, with opposite signs. |
| `conduct.humility` (humble / proud) | Yields credit, rank, precedence or pride to another's good when it was the actor's to claim. | Demands deference, takes credit owed to another, or humiliates someone of lower station to assert rank. | self-deprecating talk; modest manners (an etiquette deed) | vs generosity: giving up goods -> generosity; giving up standing or credit -> humility. |
| `conduct.restraint` (temperate / wrathful) | Holds back anger, appetite or vengeance at a moment of real provocation or temptation, when giving way was plainly open and would have harmed another or the actor's charge. | Gives way to rage, excess or vengeance so that others are harmed or a duty is broken: a beating in fury, a drunken dereliction, slaughter past need. | calm when nothing provoked; abstaining where there was no temptation on record | vs mercy: restraint masters one's own impulse; mercy is how one treats a being in one's power (both may apply). |
| `conduct.piety` (reverent / profane) | Honors the sacred, the dead or a power's rites at cost or risk: buries the dead where it is dangerous, keeps a fast, makes a real offering, defends a holy place. | Desecrates: robs a consecrated grave or temple, defiles a holy place, mocks a rite to a believer's harm, breaks a sacred taboo. | prayer or observance that costs nothing; knowledge about religion (a lore deed); looting a ruin with no fact marking it consecrated or tended | vs loyalty (above). |
| `conduct.protection` (protective / callous) | Shields a vulnerable being from harm by others, at cost or risk to the actor: takes the blow, stays behind, escorts, gives up safety. | Abandons a helpless being to a harm the actor could plainly have prevented at acceptable risk, or uses the vulnerable as a shield. | defending oneself; protecting a capable ally in an ordinary fight (a shield.cover deed) | vs mercy and courage (above). |

**T-03-8 What is not evidence.** `[D]` (`evidence.yaml#exclusions`) The tempting cases, each with the rule
that excludes it:

| Tempting case | Why it is not evidence | Rule |
|---|---|---|
| "I kill it." narrated with no frame | not resolved | 03.3.1 |
| The player says "my character is a master tracker" | assertion | 03.2.6, INV-9 |
| Shooting at a stump for an afternoon | practice: Safe, unopposed, routine | 03.3.2 D2 |
| The tenth arrow of the same fight | settles at 0 (4th and later at a node) | 03.5.2 |
| A second scene of sparring the same partner today | same target, same day | 03.5.4 |
| A fifth easy lock today | routine cap: one per node per day | 03.5.3 |
| The hound brings the fugitive down | the hound's act; the command is the PC's deed | 03.3.2 D3 |
| Surviving a poison | a resisted-effect check, not a declared method | 03.3.2 D3 |
| Greeting the innkeeper politely | no frame; no stakes | 03.3.1 |
| An inconclusive search (nothing found, nothing changed) | not consequential | 03.3.2 D1 |
| Feeling remorse | inner state; no write | 03.3.3 |
| Sparing a foe because one was ordered to | no alternative | 03.3.3 decision 1 |
| Lying to the sentry while infiltrating | a guile deed; no trust was given, so not honesty − | T-03-4 |
| Tipping a stable boy | below the ground floor | T-03-4 generosity |
| Killing under a domination spell | compelled: no conduct (deed evidence stays) | 03.2.6 |
| The scene was an investigation scene | scene tags are not deed tags | 03.1.7 rule 5 |
| "Tactics" added to every attack | ungrounded secondary | 03.1.6 |
| A deed done through a relic's license or bound power (`feeds_evidence: false`) | relics license borrowed capability and never feed calling tiers; the event is dropped at RECORD | 00.11.5, 00.12.1, 08.4.4 [integration: IR ch.04 #11, IR ch.08] |
| Arriving somewhere new without a frame (`frame_id: null`) | wandering in is not finding | 10.1.5 [integration: IR ch.10] |

**T-03-9 Simulation results.** `[D]` Scratchpad `evidence03.py` and `reach03.py`, copied with full output to
`rules/_process/simulation/`. The model: 20 sessions (30 for the reach table) of 5 scenes each. Scenes are 45%
conflict (3–6 PC beats, opposition from the PC's band to band + 2, a quarter of them Dire), 25% stealth or
site, 15% social, 15% travel. Checks are resolved with the reference ladder and the degree rule of 01.8.
Success at cost is taken on 60% of near misses. The rules of this chapter are applied exactly. 200 seeds
unless noted. Medians with the 10th and 90th percentiles where shown.

| Scenario | Result |
|---|---|
| **A. Focused archer who scouts by stealth** (weighted, p10/median/p90) | `martial.archery`: session 1 **8/26/43**; s3 **48/75/104**; s5 **91/127/161**; s10 **213/260/314**; s20 **406/493/554**. `martial`: s5 116/152/188; s20 528/608/681. `guile`: s5 32/49/69; s20 167/209/250. `guile.stealth`: s20 123/165/204. `influence` (incidental): s20 51/71/100. `deed`: s20 850/900/954. |
| A, recent (median) | `martial.archery`: 26, 50, 69, 88, 95, 80, 78 at sessions 1, 2, 3, 5, 10, 15, 20: it plateaus near 78–95 once the window is full. `martial`: plateau 100–116. |
| A, quality mix on `martial.archery` over 20 sessions (median event counts) | routine 13, difficult 55, challenging 98 |
| A, mercy | net +12 by session 20 (about one positive point per session); after one grave cruel act at session 9, strain 4 fell to 2 by session 15 and to 0 by session 20 (seed 7) |
| **B. Rat grinder** (every scene a Risky fight with band-1 vermin, 4–6 shots) | archery at s20: **2,196** with no anti-grind; **910** with diminishing returns only; **340** under the full rules. Quality mix: **100% routine**. |
| Focused play at the same number of fight scenes | archery at s20: **1,033** |
| Focused play, mixed scenes (A), with and without anti-grind (50 seeds) | archery at s20: **486** under the full rules; 958 with none |
| **C. Weapon switcher** (six weapon families in every fight) vs **C2** the same fights with one weapon | `martial` at s20: **1,106** vs **1,191**. Switching gains nothing. |
| **D. Pivot to fire sorcery at session 11** | recent(fire) passes recent(archery) at session **12** (p10 12, p90 13); recent(archery) is 0 by session 15; weighted(archery) stays at its session-10 value for good. |
| **E. Lenient DM, no grounding** (a `tactics` secondary on every beat; mercy recorded about twice as often) | `tactics` at s20: **236** (49% of archery 481); mercy positive **46** (honest: 18) |
| **E2. The same DM under the grounding rules** | `tactics` at s20: **74** (15% of archery 483); mercy positive **22** |
| **F. Generalist** (five deed tags in rotation; seed 7) | no branch above 450 at s20 (`martial` 443, `influence` 288, `arcane` 275), against 608 for the focused character's main branch |
| **G. Deliberate hybrid, archery and fire sorcery** | the smaller of the two level-2 nodes reaches 60 at session 2/3/5 and 120 at 5/6/8 |
| Largest single event observed / possible | 16 / 16 points |
| Largest single-scene contribution at the focus node | median 19, maximum 27 (cap 28) |

**T-03-10 Calibration figures for chapter 04.** `[D]` (reference only; `evidence.yaml#calibration`) The session
at which a node's **weighted** tally first reaches a value (p10 / median / p90), scenario A unless noted:

| Node | 40 | 60 | 80 | 120 | 160 | 200 | 300 | 450 |
|---|---|---|---|---|---|---|---|---|
| focus level-2 node (`martial.archery`) | 1/2/3 | 2/3/4 | 3/4/5 | 4/5/7 | 6/7/8 | 7/8/10 | 10/12/15 | 16/19/22 |
| focus branch (`martial`) | 1/2/3 | 2/2/3 | 2/3/4 | 3/4/6 | 5/6/7 | 6/7/8 | 9/10/12 | 13/15/18 |
| second branch (`guile`) | 3/5/7 | 5/6/9 | 6/8/11 | 10/12/15 | 13/16/20 | 16/20/24 | 25/30/— | — |
| secondary level-2 node (`guile.stealth`) | 4/6/9 | 6/8/11 | 8/10/15 | 12/15/20 | 15/20/26 | 20/25/— | — | — |
| incidental branch (`wilds`) | 4/6/9 | 6/9/13 | 9/12/16 | 14/18/23 | 18/23/29 | 24/29/— | — | — |
| root (`deed`) | 1/1/2 | 1/2/2 | 2/2/3 | 3/3/3 | 3/4/5 | 4/5/5 | 6/7/8 | 9/10/11 |
| hybrid G: the smaller of two level-2 nodes | 2/2/4 | 2/3/5 | 3/4/6 | 5/6/8 | 7/8/11 | 8/10/13 | 13/16/20 | 21/24/30 |

Per-session yields (median): focus level-2 node **≈24**; focus branch **≈30**; a second-pillar branch **≈10**;
an incidental branch **≈4–7**; root **≈45**. Branch balance against the main branch at session 20: 0.12 and
0.23 for branches used in 15% of scenes; 0.34 for a second pillar (25% of scenes); about 1.0 for a deliberate
hybrid. Counted units at the focus node: an estimated 6–9 per session (03.7.3; not simulated). *What this
means for 04* (suggestions only; 04 owns the thresholds): a first specialist recognition at a level-2 key set
near **weighted 80** lands at session 3–5 for focused play. Rising tiers near 200 and 450 land at about
sessions 8 and 19, which gives the slowing curve the precedents show without any separate level number. A
hybrid floor of `min ≥ 60` with `balance ≥ 1/3` admits the deliberate hybrid by session 2–5, rejects incidental
play, and leaves the two-pillar character at the line for an offer.

**T-03-12 Level-3 tags in the other facets.** `[D]` Seeded so that 08, 09 and 10 can key pools, weapons, materials and sites, and so that grounding (T-03-3) and context classes (03.4.4) have targets. Stewards propose more by PR-03-6.

| Level-2 tag | Level-3 children |
|---|---|
| `creature.beast.predator` | `canine`, `feline`, `ursine` |
| `creature.beast.herd` | `cervine`, `swine`, `bovine`, `equine`, `caprine` (adopted at integration) |
| `creature.beast.vermin` | `rodent`, `insect`, `arachnid`, `swarm` |
| `creature.beast.reptile` | `serpent`, `lizard`, `crocodilian` |
| `creature.beast.avian` | `raptor`, `corvid`, `giant` |
| `creature.beast.aquatic` | `fish`, `shark`, `cephalopod` |
| `creature.beast.monstrous` | `hybrid`, `magical`, `dire` |
| `creature.folk.giant` | `ogre`, `troll`, `true_giant` |
| `creature.folk.beastfolk` | `gnoll`, `lizardfolk`, `ratfolk` |
| `creature.undead.mindless` | `skeleton`, `zombie` |
| `creature.undead.ravenous` | `ghoul`, `wight`, `vampire` |
| `creature.undead.spectral` | `ghost`, `wraith` |
| `creature.undead.sovereign` | `lich`, `deathlord` |
| `creature.spirit.fey` | `court`, `wild`, `hag` |
| `creature.spirit.celestial` | `messenger`, `guardian` |
| `creature.fiend.demon` | `lesser`, `greater` |
| `creature.fiend.devil` | `tempter`, `enforcer` |
| `creature.construct.golem` | `clay`, `stone`, `iron`, `flesh` |
| `creature.dragon.great` | `wyrmling`, `elder` |
| `creature.horror.ooze` | `slime`, `jelly` |
| `creature.horror.plant` | `creeper`, `treant` |
| `creature.spirit.place` | `water`, `wood`, `stone` (adopted at integration) |
| `creature.fiend.hellbeast` | `hound` (adopted at integration) |
| `creature.dragon.drake` | `fire` (adopted at integration) |
| `material.metal.iron` | `cold` |
| `material.metal.silver` | `pure` |
| `material.wood.fine` | `yew`, `ironwood` |
| `material.hide.fur` | `winter` |
| `material.hide.scale` | `dragon` |
| `material.botanical.herb` | `healing`, `toxic`, `arcane` |
| `material.essence.gland` | `venom`, `fire` |
| `material.essence.heart` | `elemental`, `beast` |
| `material.essence.residue` | `ectoplasm`, `grave_dust` |
| `item.weapon.blade` | `sword`, `greatsword`, `rapier`, `dagger` |
| `item.weapon.axe` | `hand`, `great` |
| `item.weapon.bludgeon` | `club`, `mace`, `hammer`, `flail`, `whip` (adopted at integration) |
| `item.weapon.polearm` | `spear`, `halberd`, `staff`, `lance` |
| `item.weapon.bow` | `shortbow`, `longbow`, `sling` |
| `item.weapon.crossbow` | `light`, `heavy` |
| `item.weapon.thrown` | `javelin`, `knife`, `net` |
| `item.weapon.ammunition` | `arrow`, `bolt`, `stone` |
| `item.armor.light` | `padded`, `leather` |
| `item.armor.medium` | `mail`, `scale`, `brigandine` |
| `item.armor.heavy` | `plate`, `splint` |
| `item.tool.kit` | `thieves`, `healer`, `climbing`, `disguise`, `forgery` |
| `item.tool.implement` | `wand`, `staff`, `orb`, `holy_symbol`, `totem` |
| `item.consumable.potion` | `healing`, `elixir`, `toxin` |
| `item.shield.light` | `buckler`, `round` (adopted at integration) |
| `item.shield.heavy` | `kite`, `tower` (adopted at integration) |
| `item.goods.treasure` | `gem`, `art`, `coinage` (adopted at integration) |
| `item.goods.document` | `text`, `map` (adopted at integration) |
| `item.consumable.oil` | `weapon`, `incendiary` (adopted at integration) |
| `item.consumable.remedy` | `antidote` (adopted at integration) |
| `item.conveyance.mount` | `war` (adopted at integration) |
| `item.conveyance.vehicle` | `cart` (adopted at integration) |
| `item.conveyance.vessel` | `boat`, `ship` (adopted at integration) |
| `terrain.settlement.city` | `district`, `slum`, `docks` |
| `terrain.forest.deepwood` | `ancient`, `tangle` |
| `terrain.highland.mountains` | `pass`, `peak` |
| `terrain.water.coast` | `cliffs`, `shallows` |
| `terrain.underground.cave` | `flooded`, `vast`, `volcanic` |
| `terrain.ruin.dungeon` | `vault`, `warren` |
| `terrain.ruin.tomb` | `barrow`, `catacomb`, `crypt` |
| `terrain.ruin.fortress` | `tower` (adopted at integration) |
| `terrain.water.river` | `ford` (adopted at integration) |
| `situation.conflict.skirmish` | `battle` (adopted at integration) |
| `situation.social.court` | `sitting` (adopted at integration) |
| `situation.downtime.project` | `domain` (adopted at integration) |

---

## Worked examples

All examples use **Wren** (00's continuous character): Agility +3, Might +1, Wits +2; competence `deed` +1,
`deed.martial.archery` +2, `deed.wilds.tracking` +2; unrecognized, so power band 1. Odds are from T-00-6's
rule. Numbers owned by other chapters are marked *(illustrative; ch.NN owns)*. Every point value below is
computed by 03.4.2 and settled by PR-03-2.

### WE-03-1 One deed, end to end (the shot of WE-00-8)

*Situation.* Dusk on the Salt Road. A bandit who has just loosed at Wren turns his horse to flee. Wren shoots
the horse from the treeline. Frame *(illustrative; 01/06 own)*: Strike, Agility +3, competence +2 → +5 against
DC 15 (a moving horse at the near band, tier Moderate). Lever: `fact.treeline_cover` (Protective). Stakes
Risky. d20 = 12 → 17, **success**. The horse falls; the bandit is thrown.

1. **Stage A.** Basis `roll`: the frame has a degree. Eligible.
2. **Tag.** The method is a bow shot at a foe who knows he is in a fight, so `deed.martial.archery.bow`. It is
   not `guile.ambush.sniping`: the bandit had just shot at her.
3. **Stage B.** D1: delivered reach 2 ≥ 1 → true. D2: stakes Risky → true. D3: Wren's declared beat, basic
   verb → true. Significant.
4. **Quality.** Base odds with circumstance 0: +5 vs 15 → needs 10 → **55%** → **difficult** (the Protective
   lever would not change the roll in any case; a Precision lever would be removed here).
5. **Band.** DC 15 → `challenge_band` **2**.
6. **Context class.** Opposing entity: the horse, `creature.beast.herd.equine` → truncated to
   `creature.beast.herd`. Wren has no settled archery event against that class → **novel**.
7. **Points.** difficult 4 + Risky 2 + novel 2 = **8**. Not lethal, not critical. Crisis: no. Peak: band 2 ≥
   power band 1 + 1 → **yes**.
8. **Witnesses.** `npc.bandit_03` (in the scene, aware, the shot visible) → present. He is `creature.folk`, so
   he is a carrier if he still exists at settlement.
9. **Deed line.** "Shot a fleeing bandit's horse from the treeline at dusk; the horse fell and the rider was
   thrown." **Justification.** "Shortbow (item.i0031) loosed at an aware, fleeing foe → martial.archery.bow."
10. `record_evidence` returns `ev.000212`. Nothing else.

*Then the choice.* The bandit lies winded with Wren's next arrow on him. The player says she lets him run.
There is no roll. Conduct trigger: the choice writes `npc.bandit_03.spared_by = pc.wren`, and he remains
hostile (standing −3), so a threat is left alive. Decision 1 (alternative): he was at her mercy (prone, she
armed and unhindered) → true, citing `cond.prone` on him and her nocked arrow. Decision 2: `conduct.mercy`,
positive test met ("spares … a defeated … being that was in the actor's power, at a cost or risk … a threat
left alive"). Decision 3 (ground): the fact just written, a forgone gain. Magnitude: the frame that put him
there was Risky → **2**. Event `ev.000213`, basis `choice`, `conduct: [{axis: conduct.mercy, sign: +1,
magnitude: 2, …}]`.

*Settlement at scene end.* The scene's other archery beats: an earlier success (difficult, Risky, not novel:
4 + 2 = **6**) and a miss that cost her the declared S2 harm ((4 + 2) ÷ 2 = **3**). At `deed.martial.archery.bow`
the contributions sort 8, 6, 3 → 8 + 3 + 0 = **11** (the quarter of 3 rounds down to 0). The same 11 settles at
`deed.martial.archery`, `deed.martial` and `deed`. Mercy: one entry, 2 → `pos` 2. The bandit survived and can
talk: scopes = his faction (`fac.salt_road_bandits`) and nothing else. `public_deed` packets go to 11:
`ev.000212` noteworthy (8 ≥ 6); `ev.000213` not noteworthy (magnitude 2).

*Non-example.* Had the player written "Wren, being merciful, would never shoot a fleeing man", nothing would
be recorded: no beat, no write, an inner state.

### WE-03-2 Practice, a contest, and "she practices every evening"

- **Outside (practice).** Behind the Ashford inn, Wren shoots at a straw butt for an hour. If the DM frames
  it at all: Easy target (DC 10), +5 → 80% → routine; Safe; no opponent; no clock. D2 is false. `record_evidence`
  drops it as `not_significant`. This is correct, since nothing was at risk.
- **Inside (the contest).** At the Ashford fair she enters the archery contest: an entry fee of 2 coin is
  lost on failure (Risky), and she shoots against `npc.reeve_son` (opposed, aware). Final shot: opposed defense
  16, +5 → 50% → difficult. Success. Context class `creature.folk.human` (the rival is the opposing entity);
  she has settled archery events against men before, so it is not novel. Points: 4 + 2 = **6**. The crowd,
  the reeve and the rival are witnesses and carriers → scope `loc.ashford`. Noteworthy (6 ≥ 6).
- **Non-example.** The player says: "Wren practices every evening on the road." This is narration and it
  changes no tally. If the player wants practice to matter, it is 15's downtime training activity. Each
  completed week writes `cnt.training` (1 unit at `deed.martial.archery`) and no judged points (03.5.5).

### WE-03-3 The same wall, two climbers (relative quality)

A rough stone wall, Easy (DC 10), climbed under a guard's eye (Risky).
- Wren: Might +1, floor +1 → +2 → **65%** → **difficult**: 4 + 2 = 6 points at `martial.athletics.climbing`.
- A recognized climber at +9: **95%** → **routine**: 2 + 2 = 4, and only one routine counts at that node that
  day.
The sheer cliff beside it, Hard (DC 20): Wren 15% → **challenging** (6 + 2 = 8 on a success; 4 on a failure
that cost her). The expert at 50% → **difficult** (6).
*Boundary:* Wren ties off a rope first (a Precision lever, +2 on the roll). Her odds become 25%, but her
**base odds stay 15%** and the quality stays challenging. The rope makes success likelier. It does not make
the deed count for less (03.4.1c).

### WE-03-4 A whole fight settled (the cinder hound of WE-00-1/WE-00-2)

The hound: T2, Guard 13, `creature.beast.predator` and `creature.elemental.fire` (the first listed is the most
specific tie-break, so the context class is `creature.beast.predator`). Wren has shot wolves before, so the
class is not novel for archery. Stakes Risky throughout (its bite is S2). Her beats:

| # | Beat | Frame | Result | Points |
|---|---|---|---|---|
| 1 | bow shot as it circles | +5 vs 13 → 65% → difficult | success | 4 + 2 = **6** |
| 2 | second shot | same | failure; the bite lands (S2 applied) | (4 + 2) ÷ 2 = **3** |
| 3 | spear thrust as it closes | Agility +3, floor +1 → +4 vs 13 → 60% → difficult; `martial.polearm.spear`; first polearm event → novel | success | 4 + 2 + 2 = **8** |
| 4 | the shot of WE-00-2 | +5 vs 13; d20 19 → total 24, margin +11 | critical success | 4 + 2 + 2 = **8** |

Settlement by node (PR-03-2):
- `deed.martial.archery.bow` and `deed.martial.archery`: 8, 6, 3 → 8 + 3 + 0 = **11**.
- `deed.martial.polearm.spear` and `deed.martial.polearm`: **8**.
- `deed.martial`: 8 (shot 4), 8 (thrust), 6, 3 → 8 + 4 + 1 + 0 = **13**.
- `deed`: the same four → **13**.
Had she shot four times and never drawn the spear (8, 6, 6, 3), `deed.martial` would settle 8 + 3 + 1 = 12.
The weapon switch changed the branch total by one point.

*Counted.* `on_defeat` fires on beat 4: `cnt.defeat`, 2 units (threat band 2) at `deed.martial.archery.bow`.
Quarry's Mark (WE-00-6's ability, Focus 1), if it fired this fight, adds `cnt.focus` 1 unit at the ability's
first deed tag *(illustrative; 05 owns the ability's tags)*.

*Witnesses.* None but the hound, which is a beast and not a carrier → private. No packet to 11.

### WE-03-5 The caps on both sides

- **Same target.** In the morning Wren spars with the caravan's guard-sergeant for a wager (Risky, opposed):
  `martial.polearm.spear`, 6 points, settled. In the afternoon, in a new scene, they spar again. The (target,
  `deed.martial.polearm`) pair was already settled today → the second event settles as **0**. *Other side:*
  the next day's rematch counts, and so does a bout against a different guard that same afternoon.
- **Routine cap.** A locksmith's apprentice (+9 on locks) opens five Easy desk locks in one searched house
  under a ticking alarm clock (pressured by the clock). Each is routine: 2 + 2 = 4. It is one day, however the DM cuts the scenes: at
  `guile.thievery.lockpicking` the first counts 4 and the other four count **0**. *Other side:* one Hard
  strongbox lock in the same house (50%, difficult: 4 + 2 = 6) counts in full, because the cap applies to
  routine evidence only.
- **Diminishing returns.** Nine arrows in one fight: the three best count as full, half and a quarter, and
  six count 0 (03.5.2).

### WE-03-6 Secondary tags: grounded, ungrounded

- **Grounded by position (inside).** From the hayloft Wren shoots a sentry who has not seen her (the fact
  `guard_07.alertness = unaware` is on record; she has `flag.hidden`). The frame rolls against the shot's
  difficulty (Hard, far band: DC 20), so the contest is the shot and the primary stays
  `deed.martial.archery.bow` (03.1.7 rule 2): +5 vs 20 → 30% → **challenging**. Secondary
  `deed.guile.ambush.sniping`, ground `{kind: position, ref: guard_07.alertness}` → accepted. Dire (the
  garrison wakes on a miss). Success: 6 + 4 + 2 (novel) = **12** to `martial.archery.bow`, `martial.archery`
  and `martial`; **6** to `guile.ambush.sniping`, `guile.ambush` and `guile`; `deed` receives 12 once.
- **The other side (the approach decides).** She instead creeps up behind the sentry to cut his throat. 06
  frames this against his awareness (will the blow land before he knows?) *(illustrative; 06 owns the
  frame)*. The contest is the approach, so the primary is `deed.guile.ambush.assassination`, and
  `deed.martial.blade.dagger` is the secondary, grounded by the knife (`{kind: item, ref: item.i0007}`;
  T-03-3). Her competence here is the floor, since she has no guile training, and the OFFER shows that before
  she commits.
- **Ungrounded (refused).** The player adds "and I use good tactics." No ability, item, Setup, companion or
  mount carries `martial.tactics`. The secondary is refused; the primary is unaffected.
- **Grounded by a Setup (inside).** Earlier in a fight Wren used Setup to drive an ogre onto the frozen pond
  (primary `deed.martial.tactics.ground`; success; that beat is its own event). Her next thrust cites the
  lever `fact.ogre_on_ice`. Secondary `martial.tactics.ground`, ground `{kind: setup_beat, ref: beat.4471}` →
  accepted at half the thrust's points.
- **Tempting non-example.** A wand is in her off hand while she shoots. Implements ground nothing (T-03-3). No
  arcane secondary.

### WE-03-7 Conduct: boundary cases across the axes

| Case | Decision | Why |
|---|---|---|
| Wren binds a yielded bandit who nearly killed her (the frame was Dire) and leaves him water | mercy **+4** | alternative: he was helpless; ground: `spared_by` fact, a threat left alive; Dire → 4 |
| She cuts his throat instead "to be safe" | mercy **−4** | harm to a helpless victim → 4 |
| She kills him while he is still swinging at her | none | no alternative on record: the fight was on |
| She spares him because Captain Hesk, standing over her, ordered it | none for mercy | forced; test loyalty only if obeying cost her |
| She lies to the gate sentry about her business while slipping into Grey Keep | none for honesty | a guile deed (`deception.lying`); the sentry gave no trust; no gain beyond the infiltration itself |
| She tells the reeve, who trusts her as the town's hired tracker, that the tracks led north when they led to her friend's barn, and keeps the bounty | honesty **−2** (and loyalty to the friend is not scored: the test needs a cost to her) | deceiving one who relied on her word, for gain; loss to another at S2 equivalent |
| She admits to the reeve that she broke the archive hasp, and pays the 6-coin fine | honesty **+2** | costly truth; the lie would have served |
| She charges a troll alone "because it will make a good story" | none for courage | recklessness with no purpose beyond her own |
| She holds the ford against the troll so that the carters can get their wagons across (declared Dire, lethal) | courage **+4** and protection **+4** | two axes, both tests met; each grounded in the lethal frame taken for others' sake |
| She frees a horse-thief the village means to hang, out of pity; he rides off | mercy **+2**, justice **−2** | one act, two axes, opposite signs: the guilty escaped answer |
| She takes the grave goods from a barrow the local shrine still tends (the fact `barrow.tended_by = shrine_of_the_ford`) | piety **−2** | a consecrated grave robbed |
| She takes coins from an unmarked ruin's rubble | none | no fact marks it consecrated or tended |
| A fey's glamour has her charmed when she hands over the ward-key | none | compelled (03.2.6); no conduct |
| She gives her last three days' rations to refugees and goes hungry (supply 3 → 0) | generosity **+2** | above the floor: she now lacks supply |
| She tosses a beggar one copper from a purse of 40 | none | below the ground floor |

### WE-03-8 Witness and scope

- **Witnessed.** At the ford Wren's arrow takes a wyvern in the eye in front of six caravan guards and their
  master. The guards are present, aware, and the shot is visible → witnesses. They are folk and alive at
  scene end → carriers. Their homes and factions: `loc.ashford` (four of them), `fac.caravaners_compact`
  (all). Scopes: both. The event (challenging, Dire, lethal, novel: 6 + 4 + 2 + 2 = 14) is noteworthy. 11
  receives the packet and may begin an epithet (V1) in those two scopes.
- **Unwitnessed.** The same shot from a hidden ledge with the guards facing the river: the default is false
  for each guard (no line of sight, `flag.hidden` on Wren). The wyvern perceives it, but a beast is no
  carrier. Private: full points to her tallies, nothing to `public`.
- **Witnesses who do not survive.** Wren kills all four bandits in the gully. At settlement none exists. The
  deed is private, although the points are unchanged.
- **Aftermath.** Three days later the reeve's men find the bodies and recognize her fletching (the fact
  `fact.gully_arrows_identified`, written when 15's investigation by the NPCs succeeds). The DM calls
  `add_witness(ev.000301, npc.reeve, how: aftermath, fact.gully_arrows_identified)`. At the next settlement
  the event enters `loc.ashford`. The reputation is 11's to shape: a bandit-killer in Ashford, and a murderer
  to the bandits' kin.
- **Bonded.** If Wren had sworn the Ford-Warden's oath (04), the shrine's power would witness every
  `conduct.protection` event wherever she was, and carry it only to the shrine's own scope.

### WE-03-9 Recency: a winter away, and a change of ways

- **A winter away.** After 10 sessions Wren's `martial.archery` is weighted 260, recent 95 (the simulation's
  medians). She spends 13 weeks healing at a monastery. `advance_time` runs every boundary (INV-15). No judged
  deed is recorded, so no evidence-bearing scene is added, and her recent value on leaving is still **95**. A
  calendar window of 4 weeks would have read 0.
- **A change of ways.** At session 11 she apprentices to a fire-sorcerer and stops carrying the bow. Each new
  evidence-bearing scene pushes one old scene down the window. In the simulation her recent fire sorcery
  passed her recent archery in session **12**. By session 15 her recent archery was **0**, while her weighted
  archery stayed where it was at session 10 (263 in the seed shown) and her weighted fire sorcery had reached
  96. What 04 does with a strong cumulative archer whose recent life is sorcery (an offer to relabel, a fork,
  a hybrid) is 04's rule. This chapter guarantees that both facts are visible.

### WE-03-10 Strain and atonement arithmetic

Wren holds an oath that names `conduct.mercy` *(illustrative; 04 owns oaths)*. Her mercy: `pos` 12, `neg` 0,
`strain` 0.
1. In a rage she kills a yielded scout: −4. Settlement: `neg` 4, `net` +8, `strain` 0 + 4 = **4**. Under the
   stages this chapter proposes to 04, that is the first warning (the witness withdraws).
2. Next session she spares two foes at real cost (+2, +2 in different scenes): `pos` 16; strain 4 − floor(2/2)
   − floor(2/2) = **2**.
3. A second killing of a helpless man (−4): `neg` 8, strain **6**. One more grave act would reach 10, past
   the second stage (8).
4. She accepts the atonement 04 offers (carry the scout's sword to his kin and stand their judgment). On
   completion 04 records the `atonement` event superseding both killings: `neg` 0, `atoned` 8, `net` +16,
   `strain` **0**. The ledger still shows both deeds, marked superseded. `witnessed_neg` is unchanged: the
   scout's company still calls her a butcher.
*Boundary:* had the oath listed "slay one who has yielded" as a forbidden act, each killing would also carry
a `forbidden_ref`, `forbidden` would read 2, and 04's break rule would apply at once, whatever the strain.

### WE-03-11 No-roll resolutions

- **Good Idea (inside).** Wren waits for the gap in the patrol schedule she established earlier
  (`fact.patrol_gap_midnight`) and walks through the postern. 01.4.3 rules it a Good Idea: success, no roll.
  Basis `good_idea`. The frame the beat would have had: Sneak, +4 vs Moderate 15 → 50% → difficult (the cap
  is difficult anyway). Stakes Risky. D1 true (no-roll success), D2 true (Risky), D3 true. Points 4 + 2 = 6
  at `guile.stealth.infiltration`. Clever play that removes a roll still leaves evidence.
- **Take the time (outside).** She searches an empty cellar with no clock, no observer and no hazard: 01.4.4,
  success with doubled time. Quality routine; Safe; unopposed; no clock → D2 false → not evidence.
- **Take the time on a project (inside).** She spends an evening fletching arrows as one tick source of a
  4-segment project clock (15). The beat ticks a project clock → D2 true. Routine, Safe: 2 points at
  `craft.woodcraft.bowyery` (one such routine event per day at that node). The counter records
  `cnt.progress` for the ticks.
- **A resisted effect (outside).** The hedge-witch's sleep-smoke forces an Endure check, which Wren passes. She
  did not declare it. No evidence.

### WE-03-12 Counted evidence beside judged evidence

In the Grey Keep archive (WE-00-5) Wren's two successful search beats ticked `clk.find_ledger` by 2 and by 3.
- Judged: two events at `deed.lore.investigation.search` (the floor only: +2 Wits +1 = +3 vs Moderate 15 →
  45% → difficult; Risky): 6 and 6, and the second used an Amplifying lever (no effect on quality). Settled:
  6 + 3 = **9**.
- Counted: `cnt.progress`, units 2 and 3 at the same tag → sorted 3, 2 → 3 + 1 = **4** units. `cnt.clue` if
  15 wrote a `clu.*.found` fact: 1 unit.
04 can now ask both questions of `lore.investigation`: "how well and how riskily has she searched?" (weighted
9) and "how much has her searching actually moved?" (counted 4 or 5).

### WE-03-13 A disputed ledger line

After the session the player reads the codex ledger and sees: "Killed a wounded poacher who had dropped his
knife. Tags: martial.blade.dagger; conduct.mercy (−)." The player objects: the poacher had drawn a second
blade. 12's dispute procedure checks the turn log. The frame's record shows `npc.poacher_02` with
`cond.prone` and no weapon fact, but the narration two turns earlier did mention "a skinning knife at his
belt", and by write-on-mention it was recorded (`item.i0450`, held by the poacher).
The DM's flag (PR-03-4): does state still support the conduct ground ("a helpless victim")? The poacher was
prone and armed, and the fight had not ended (no yield, no defeated state). The alternative flag fails:
sparing was not *plainly* open. The event is voided and re-recorded from the same frame without the conduct
entry. Its scene is re-settled: mercy `neg` 4 → 0, strain 4 → 0. The player is told, out of fiction, that the
line was corrected.
*Other side:* had the log shown the poacher yielding (`harm_state: defeated`) before the blow, the line would
stand, and the DM would say so plainly (12.3.6).

### WE-03-14 Tempting non-examples, with the refusal each gets

| The player says or the DM is tempted to record | What happens |
|---|---|
| "I shoot it ten more times." (the probe's turn 13) | 01.14 resolves about three shots; each resolved shot may be evidence; at most three count in the scene |
| "After all these weeks Wren is clearly a master archer by now." | assertion; no event; tallies are sealed and say what they say |
| The DM, after a moving scene, wants to record "courage" for Wren walking into the burnt chapel | no declared Dire or lethal danger, no cost, no write → no entry (C3) |
| "Record mercy; I didn't kill the merchant I was haggling with." | no alternative on record: killing him was never a course the scene held; no write |
| A critical success on a trivial jump (Trivial tier: no roll) | no frame; no evidence |
| An NPC praises Wren's swordsmanship | narration by an NPC changes no tally; it is 11's reputation speaking |
| The DM wants to add `influence.intimidation.display` because Wren "looked fierce" while fighting | not the method of the beat; no ground; refused |

### WE-03-15 What chapter 04 sees (and nobody else)

At the reflection after session 5, in one simulated run (seed 7), `h.03.recency_update` hands 04 a digest with
dirty nodes including `deed.martial.archery`. 04 calls:
- `tally(pc.wren, deed.martial.archery)` → `{raw: 35, weighted: 155, recent: 108}`
- `detail(pc.wren, deed.martial.archery)` → `by_quality {routine: 3, difficult: 14, challenging: 18}`,
  `by_band [2, 12, 16, 5, 0]`, `peak_band: 4`, `crises: 3`, `peaks: 10`,
  `distinct {scenes: 14, days: 9, contexts: 5, opponent_kinds: 4, places: 6, children: 1}` *(the breakdown is
  illustrative)*
- `share(pc.wren, deed.martial.archery)` → `{num: 155, den: 178}`: archery is most of her martial weight.
  04 can test any ratio exactly: `share ≥ 7/8` ⇔ `8·155 ≥ 7·178` ⇔ 1,240 ≥ 1,246, which is false by six
  points; `share ≥ 3/4` ⇔ 620 ≥ 534, true. Integers only.
- `dominance(pc.wren, deed.martial)` → `{lead: 130, rival: deed.guile, num: 178, den: 226}`
- `cooccurrence(pc.wren, deed.martial, deed.guile)` → `{weighted_a: 178, weighted_b: 48, min: 48, balance {48,
  178}, joint_events: 4, joint_scenes: 6, recent_min: 38}`: the balance is below 1/3 (3·48 = 144 < 178), so
  under the suggested floor no hybrid is offered yet.
- `conduct(pc.wren, conduct.mercy)` → `{pos: 8, neg: 0, net: 8, recent_net: 8, strain: 0, forbidden: 0, …}`
- `counted(pc.wren, deed.martial.archery)` → `{units: 38, recent_units: 38, by_counter {cnt.defeat: 31,
  cnt.focus: 7}}` *(illustrative)*
The narrator's context receives none of this. If 04 decides to offer, the DM receives a recognition packet
with a calling, a policy and vehicle candidates, and the deed lines to quote. It receives no numbers (00.14.2
#26).

### WE-03-16 The grinder and the adventurer, side by side

Two archers play 20 sessions of five scenes. One clears rats from cellars every scene (Easy shots, Risky
because they bite). The other takes real fights at her band and above.

| Measure at session 20 (medians) | Rat grinder | Adventurer (fights in every scene) | Adventurer (mixed play, scenario A) |
|---|---|---|---|
| `tally(martial.archery).weighted` | **340** | **1,033** | **493** |
| events by quality | 100% routine | mostly difficult and challenging | routine 13 / difficult 55 / challenging 98 |
| `detail.peaks`, `detail.crises` | 0, 0 | many | many |
| novelty | one context class | many | many |

Under a 04 rule of the shape "weighted ≥ 80 **and** at least 6 events of difficult or better", the adventurer
qualifies in session 3–5 and the grinder never does, although the grinder's weighted tally passes 80 by about
session 5. Weight alone is not the gate. The quality profile is (03.9.4).

---

## Edge cases & adaptation anchors

**No rule in this chapter is an action anchor.** Every rule here is `Anchor: no`. This chapter adjudicates no
player action: it classifies and counts what the action rules resolved, so it adds nothing to
`data/anchors.yaml`. What it gives improvisation is the **vocabulary**: when the DM anchors a novel action
(01.5), the 270 level-3 deed definitions and their distinguishing tests are what let it say "this is basically
a grapple" or "this is basically sleight of hand", and competence and evidence then follow the tag with no
further ruling. The cases below show how to reach and adapt the evidence rules themselves.

**Classification**
- **A method fits no level-3 tag.** Stop at the level-2 tag, or at the branch (03.1.5 decision 3). Evidence
  and competence work at any depth. Log a ruling with tag `tag_gap` naming the method. Three `tag_gap` rulings
  under one parent make a PR-03-6 candidate. Never invent a tag in play.
- **A method fits two branches equally** (a war-song that steadies allies: `influence.performance.music` or
  `influence.command.rallying`; a blessing spoken as a threat). Take the tag of the *contest the frame rolls*:
  what the roll is against decides it, as in 03.1.7 rule 2. The other tag is a secondary only if grounded.
  Still tied: the tag listed first in `tags.yaml` (00.5.4b).
- **A weapon used as something else** (a lute swung at a head, a shield thrown). The method decides: the lute
  is `martial.bludgeon.club`; the thrown shield is `martial.thrown.improvised`. T-03-3 grounds nothing here,
  because the item was not used as its kind.
- **Magic through a weapon** (a sacred strike, a flaming arrow). The primary is the magic tag of the license
  used (03.1.7 rule 3). The weapon's tag is a secondary grounded by the item. This is how a spellblade's
  history shows on both branches, at full weight on one and half on the other, and how
  `cooccurrence.joint_events` counts it.
- **Deeds in another shape.** A shapeshifted PC who bites and claws records `martial.unarmed.natural`; the act
  of changing is its own beat (`primal.shapeshifting.*`). A secondary for the shifting needs the ability as
  its ground.
- **A setting adds a kind of deed** (black-powder weapons, airships). Until PR-03-6 admits a tag, classify at
  the nearest parent (`martial.archery` for a handgonne; `wilds.seafaring` for an airship) and list the gap.

**Significance and weighting**
- **Extended tasks and clocks.** Each beat that ticks a clock is its own event. Diminishing returns settle the
  scene, and `cnt.progress` counts the ticks. A 12-segment project is evidence across the many scenes it takes,
  which is the intended shape.
- **Time skips and montage.** "I spend the winter hunting." 15's downtime activities resolve as frames at
  their own cadence (one per activity per week), so the winter yields a handful of judged events and
  `cnt.training` or `cnt.progress` units. It never yields ninety days of deeds. `advance_time` invents no
  evidence.
- **Group actions and Help.** The helper's Help beat is the helper's event, under the tag of what the helper
  did. The leader's beat is the leader's. Nobody gets evidence for a beat they did not declare.
- **Mass battle.** Only the PC's own resolved beats count. Commanding a company is `influence.command.*` and
  `martial.tactics.battle`; the company's kills are not the PC's `cnt.defeat`.
- **A deed inside an illusion, dream or vision.** If 01 resolved frames there, the deeds are the character's
  (the skill and the choice were real) and record normally, with no witnesses outside the vision. Conduct
  records only if the character believed it real: the alternative flag is judged from what the character knew.
- **The same foe twice in one day by a new method.** The same-target cap is keyed to (target, level-2 deed
  node). Out-talking a sentry in the morning and out-sneaking him in the evening are two nodes; both count.
- **A very long scene.** `h.03.day_settle` settles at each day boundary. If play shows single scenes with
  more than a dozen PC beats inside one day to be common, OEQ-03-8's test adds a settlement at `conflict_end`.
- **A critical failure with heavy cost.** It is a failure: half points, if a cost applied. A disaster shows
  that the character tried something hard. It does not show mastery.

**Conduct**
- **Wrongs of omission.** "Abandons … to a harm one could have prevented" needs the harm on record. If the
  PC walks away and the harm falls later (off-scene, in a World Turn), the conduct entry is recorded when the
  harm is written, citing the earlier choice fact (`pc.wren.left npc.miller at the mill`), and it settles in
  the scene where it is recorded.
- **Who can be wronged.** A "being" in T-03-4 is any creature that can suffer or hold trust: everything
  except `creature.undead.mindless`, mindless `creature.construct` kinds, and `creature.horror.ooze` or
  `creature.horror.plant` kinds without speech. Destroying a skeleton that has stopped attacking is not
  cruelty. A beast counts: tormenting a trapped wolf is mercy −.
- **An act under a false belief.** The alternative and the test are judged on what the character knew, from
  recorded knowledge (15). Killing a "bandit" who was an innocent in a mask is not justice − at the time. If
  the truth is learned and the character does nothing, that is a new choice.
- **An order from the PC.** If a companion commits the cruelty on the PC's command, the command beat is the
  PC's act and carries the conduct entry: the ground is the harm the command caused, and the alternative is
  not giving it.
- **A player who wants a dark character.** Negative poles are evidence too. `net` goes negative, and 04's
  shadow callings and dark offers (V13) key on it. Nothing in this chapter punishes a pole.
- **Atonement without an oath.** `strain` is tracked for every actor and axis, sworn or not. 04 decides
  whether an unsworn character is ever offered atonement. Positive deeds lower strain at the half rate either
  way.

**Witness and reputation**
- **Disguise.** If the PC acts under a persona (a `guile.disguise` fact is in force), witnesses carry the deed
  as the persona's: set `as_identity`. Capability tallies are the PC's. `public` is credited to the persona
  for 11. Unmasking later is an aftermath link (03.10.3) that moves the public credit to the PC.
- **A witness who misread the deed** (thought the fireball was the hedge-witch's). The DM's perceived flag is
  about perceiving the act, not attributing it. Misattribution is 11's rumor truth value.
- **Animals and familiars as witnesses.** They are not carriers, unless a speaker can question them
  (`primal.beastkin.speech`): then an aftermath witness is added when that happens.

**Analogical anchors for evidence questions**

| When the question is… | Reach for… |
|---|---|
| "Does repeating this count?" | diminishing returns (03.5.2), the routine cap (03.5.3), the same-target cap (03.5.4) |
| "Does practice or training count?" | D2 (pressure) and `cnt.training` (03.5.5) |
| "Does it count if nobody saw?" | yes for capability (03.4.6); no for `public` (03.10) |
| "Does a failed attempt count?" | half, if it cost something (03.4.2) |
| "Does being clever instead of rolling count?" | `good_idea` basis (03.3.1) |
| "Do feelings or intentions count?" | no: only writes (03.3.3) |
| "Can evidence be taken back?" | void (error) or atonement (conduct) only (03.6.3) |
| "Has the character changed?" | `recent` against `weighted` (03.6) |
| "Is this who they are, or a one-off?" | `detail.distinct` and the quality profile (03.9.3) |

---

## State touched

**State families read** (00.6.3 names): frames and OFFER fields (01): degree, stakes, lethal,
`success_at_cost_taken`, `necessity.reason`, `deed_tag`, obstacle and defender ids, delivered reach, costs
applied, levers; entities and their tags (creature, item, terrain); conditions on the actor (`cond.charmed`
and any choice-dictating effect); harm state at declaration (07); relationship-state flags (`flag.hidden`,
`flag.mounted`; 06); NPC alertness (15); clocks active in the scene (00.8); licenses and abilities cited in
the gate (05) and their tags; commitments of kind oath and bond (04); `power_band` (04); NPC homes and faction
memberships (11, 13, 15); journey roles (10, 16); time and scene ids (00, 12).

**State families written** (owner: 03):

| Family | Type (00.6.1) | Visibility (00.6.4) | Notes |
|---|---|---|---|
| Evidence ledger (events) | ledger | **available**: deed line, tags, conduct axis and sign, scene, time, known witnesses, status. Points, magnitudes and settled values are **sealed** fields. | append-only; void and superseded are statuses, never deletions |
| Weighted tallies (`raw`, `weighted`, `recent`, detail counters) per actor × node | tally | **sealed** | pure function of the settled ledger |
| Counted tallies per actor × counter × node | tally | **sealed** | |
| Conduct tallies (`pos`, `neg`, `atoned`, `strain`, `forbidden`, …) per actor × axis | tally | **sealed** | |
| Evidence-bearing scene list; `last_exercised` | meta | **background** | read by 12 |
| Public tallies per actor × node × scope | tally | **background** | read by 11 |
| Reflection digest | meta | **sealed** | consumed by `h.04.recognition_pass` |

**Tools used.** `record_evidence` (#25, owner 03): records, and with the requested `op` field also voids, adds
aftermath witnesses and writes atonement (Interface requests). It reads through `get_state` (audit view) only
inside the engine. No other tool is called by this chapter's rules; the DM's inputs are tags, ids, flags and
two lines of text (INV-3).

**Hooks.** Listened to by counters (03.7.2), as engine listeners at any depth: `on_defeat`, `on_focus_spent`,
`on_harm_taken`, `on_condition_applied`, `on_clock_tick`, `on_item_acquired`, `on_fact_set`, `on_stabilize`,
`on_boundary`. Fired by this chapter: `on_tag_event`, once per settled event, as a depth-0 boundary-handler
event (PR-03-2 step 12).

**Boundary handlers.** Reserved and defined here: `h.03.antigrind_reset` (`scene_end`, phase 9; PR-03-2) and
`h.03.recency_update` (`reflection`, phase 8; PR-03-3). Added in `data/boundaries.yaml owner-block 03`:
`h.03.day_settle` (`day`, phase 9; PR-03-2 for scenes still open).

**Clocks created.** None.

**Data files.** `data/tags.yaml` (content below level 2, and two level-2 additions); `data/evidence.yaml`.

**Runtime capabilities assumed** (00.14.1): RC-STORE (typed tallies and events), RC-SEAL (sealed tallies; a
narrator view that never includes them), RC-LOG (the append-only ledger), RC-QUERY (tag ancestry for cascade,
context classes and grounding), RC-SCHED (settlement and reflection handlers), RC-EVAL (hook dispatch to
counters; base-odds evaluation with circumstance set to 0), RC-DATA (validation of every tag and counter id).

---

## Interface requests

**Offered to every chapter.** The level-3 vocabulary (T-03-1, T-03-12); PR-03-6 for proposals
(`data/contrib/tags.NN.yaml`); `record_evidence` at any resolved beat.

**To 00 (proposed amendments; this chapter works within 00 as written meanwhile).**
1. **Tool #25** `record_evidence` gains an `op` field: `record` (default) | `void` (event_id, reason) |
   `add_witness` (event_id, entity, how, fact_id) | `atonement` (04 only). Meanwhile these are described as
   operations of the same tool.
2. **`data/SCHEMAS.md#evidenceyaml`**: document the optional keys this chapter added (`quality`,
   `quality_by_basis`, `flags`, `blast_radius`, `counted_rules`, `conduct`, `conduct_tests`, `witness`,
   `verb_default_tag`, `item_grounding`, `functions`, `ledger_view`, `calibration`, `backstory`), and that a
   counter's `tags` may be empty when it has a `tag_source`.
3. **00.6.8**: note that `degree` is recorded as `success` for a success-at-cost, and that the event shape is
   extended in 03.2.1 (fields added, none renamed).
4. **00.5.6**: add "a secondary tag earns evidence only when grounded (03.1.6)". Competence still reads only
   the primary tag.
5. **00.10.2**: clarify that 03's counters are engine listeners on hooks, at any depth, and are not effect
   subscribers under INV-12.
6. **Glossary (00.18)** additions: **quality** (routine / difficult / challenging: how hard a deed was for
   its actor); **settlement** (the scene-end pass that applies saturation); **evidence-bearing scene**;
   **ground** (the state write or frame element a judged evidence element must cite); **carrier** (a witness
   who can spread a deed); **strain** (unatoned contrary conduct on an axis); **deed line**.
7. **T-00-9**: add `h.03.day_settle` (`day`, phase 9).
8. **`trait.*` definitions in `tags.yaml`** (levels 1–2, 00's rows): add "(general rule: 01.17, T-01-13)" to
   each, as 01 asked. This chapter may not edit those rows.

**To 01 (Resolution).** (a) `frame_check` stores `base_odds`: success or better with `circumstance = 0`.
(b) The deed-tag classification card at FRAME is 03.1.5 with T-03-2. (c) RECORD step 4 runs PR-03-1.
(d) Confirmed as asked: evidence only on resolved outcomes; success-at-cost is a success; inconclusive beats
are not evidence. (e) A resisted-effect check is flagged in the frame (`beat.declared: false`) so that D3 can
read it.

**To 02 (Character).** Origins grant competence on tags from T-03-1. Tallies start at zero, except optional
`backstory` (03.2.8: up to three tags, 24 points each). Aspirations never weight evidence.

**To 04 (Recognition and growth).** (a) Require **both** a judged threshold and a counted threshold for every
recognition, plus a quality floor and a distinct-scenes floor (03.9.4); the grinder passes weight alone.
(b) Use `detail(tag, since)` for qualitatively distinct tier requirements. (c) Define confidence over the
inputs of 03.9.4. (d) Write `atonement` events through `record_evidence`; mark unatonable forbidden acts in
the oath entry. (e) Name bonded witnesses in oath and bond records. (f) Provide `power_band(pc)` to the `peak`
flag. (g) Call `tally(include_pending: true)` only from the crisis check. (h) Log the tally values used with
each `recognition_event`. (i) The proposed Fraying stages (strain 4 / 8 / 12, or any forbidden citation) and
the calibration of T-03-10 are suggestions. (j) Every calling key must be a tag in `tags.yaml`; hybrids key on
two deed branches, and `cooccurrence` accepts any two non-ancestor nodes should 04 want finer hybrids.

**To 05 (Abilities, Focus, magic).** Every ability's first `tags` entry is a deed tag at level 2 or 3
(`cnt.focus` and grounding read it). Ability pools may gate on any deed tag in T-03-1. Any effect that
dictates the actor's choices must be marked so (`dictates_choice: true` on the condition or effect) for 03.2.6.

**To 06 (Conflict).** Say which defense a strike on an unaware target rolls against (awareness or Guard):
03.1.7 rule 2 reads it. Keep `flag.hidden` and `flag.mounted` current. `on_defeat` must carry the defeating
frame or ability. A mob or swarm is one entity with one threat band.

**To 07 (Harm, recovery, death).** The actor's harm state at declaration is readable for the `crisis` flag. A
wound or mark is not itself evidence; the beat in which it was taken is. For `injuries.yaml#evidence_tags`,
07 may read `evidence_for_frame(frame_id) → [event_id, tags]` (ledger lines only) to give a mark the tags of
the deed that earned it.

**To 08 (Items, loot, crafting).** Give every weapon, shield, armor, kit and instrument base item a level-3
(or level-2) `item` tag from T-03-12 so that T-03-3 grounds it. Crafted items carry `provenance.maker` and
`domain: gen.craft`; quality rungs have an index (lowest = 1) for `cnt.made`. The generosity ground floor
uses the actor's weekly lifestyle cost.

**To 09 (Adversaries).** Archetypes list `creature_tags` most specific first; the first is the context class
(03.4.4), and `evidence_tags` (SCHEMAS) default to the same list. `speaks: true|false` per archetype for
carriers. Threat band on every adversary, for `cnt.defeat` and conduct-only bands.

**To 10 (Exploration, travel, sites).** `loc.*.discovered` is written as a delivered result with its frame
id. Journey roles are facts on the actor per watch. Places carry `terrain` tags and a settlement ancestor
where one exists (scope).

**To 11 (Living world).** Consume `public_deed` packets and `public()`; own reputation content, score, spread
beyond the listed scopes, and epithets. NPCs need a `home` place and faction memberships for scope. Reputation
by persona when `as_identity` is set. The chronicle may quote deed lines. At retirement, the settled ledger
and tallies are the record legacy reads.

**To 12 (DM procedures).** T6 WRITE runs PR-03-1 for every resolved beat. The reflection sweep (03.3.5) is a
prompt at `reflection`. Disputes about ledger lines route to PR-03-4. `scene_end` must be marked reliably,
since settlement hangs on it. `last_exercised` is available to the rotation ledger. Narration never mentions
recording.

**To 13 (Starter setting; now the region's seed, 12.16).** Facts that mark graves, shrines and holy places as consecrated or tended (piety): the world seed writes them (12.16.9, 12.16.12; T-12-16 `ws.req.03_consecrated`) [revision: I-028].
Setting-specific tags by PR-03-6. NPC homes.

**To 14 (Player's guide).** A codex view "Deeds" rendering `evidence.yaml#ledger_view`. The guide should tell
players plainly that what counts is what the character does under pressure, that repetition and practice do
not, and that the numbers are hidden.

**To 15 (Social, investigation, downtime).** `clu.*.found` facts with frame ids; the training activity writes
`cnt.training`; the alertness value `unaware` (position grounding); NPC knowledge writes that link deeds to
actors (aftermath witnesses); social progress tracked on clocks so that `cnt.progress` sees it.

**To 16 (Companions).** `tracks_evidence` per template; companions' acts are their own; companions are
carriers; journey roles.

**To the orchestrator.** A constitution PATCH candidate: P5's sixth-pass paragraph says the significance call
"MUST be the narrating AI's own base-model judgment". This chapter satisfies it by reading that judgment from
the frame's pre-committed fields and keeping fresh judgment only for tags and conduct (DL-03-01). A sentence
recording that reading would prevent a later audit from flagging it.

---

## Open empirical questions

Each has a shipped default and a named test.

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-03-1 | Do the judged calls (conduct, secondaries, witnesses) still skew lenient under the citation rules? | 03.3.3, 03.1.6, 03.3.4 | **T-03-CALIB** (R4's T-R4-05): 60 narrated moments, half built as non-evidence, on the production model; target ≤ 10% false-positive conduct entries, 0 ungrounded secondaries accepted, and no change when tallies are hidden vs shown (they are always hidden in play) |
| OEQ-03-2 | Can the DM classify level-3 deed tags reliably? | 270 level-3 tags; stop when unsure | **T-03-TAG**: 100 novel methods × 3 independent runs; target ≥ 90% same branch, ≥ 85% same level-2 tag, ≥ 70% same level-3 tag; sibling pairs confused more than 20% of the time get a sharper test or are merged |
| OEQ-03-3 | Do the point steps give the intended yields in real play? | quality 2/4/6; stakes 0/2/4; +2 lethal, crit, novelty | **T-03-YIELD**: log settled points per session over 10 real sessions; target 15–35 per session at the player's focus level-2 node; if outside, 04 moves thresholds (the points stay) |
| OEQ-03-4 | What do the counters actually yield? | units per T-03-7; measured (revision I-004): 1–4 counted units a fight without Focus, 2–7 pushing; counted share 0.11–0.33 / 0.26–0.44 by band; contests 0.31 / 0.76 / 0.31 (03.7.3) | **T-03-COUNT**: the same 10 sessions of live play; report units per counter per session; 04 re-checks its divisor against it |
| OEQ-03-5 | Is a 24-scene window (12 full, 12 half) the right recency? | 03.6.2 | **T-03-PIVOT**: three playtests with a deliberate change of style; target the new style's recent passing the old within 2–4 sessions, and no loss of recent across a downtime skip |
| OEQ-03-6 | Does one routine event per node per day starve honestly routine trades (crafters, healers treating many patients)? | 03.5.3 | **T-03-ROUTINE**: in the same logs, the share of a crafter's or healer's eligible events removed by the cap; if above 60%, raise the cap to 2 per day for `deed.craft` and `deed.lore.medicine` |
| OEQ-03-7 | Is working strain off at half rate felt as fair? | 03.8.3 | **T-03-STRAIN**: playtests with one grave act; sessions until strain 0 without atonement; target 4–8 sessions; ask the player whether the road back felt earned |
| OEQ-03-8 | Do long scenes under-credit play? | settle at `scene_end` and `day` | **T-03-SCENE**: settled points per 10 PC beats, by scene length; if scenes of more than 12 PC beats yield under half the rate of short ones and are more than 20% of scenes, also settle at `conflict_end` |
| OEQ-03-9 | Do witness defaults match what a careful reader would say? | 03.10.1 | **T-03-WIT**: 40 scenes annotated by two readers; target ≥ 85% agreement with the engine default plus DM flips |
