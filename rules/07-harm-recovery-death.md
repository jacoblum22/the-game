# 07 — Harm, Recovery, and Death

> This chapter governs what happens to a body and a mind when things go wrong, and how they come back.
> It defines what Vitality is, the ladder a character descends when Vitality runs out (Staggered, wounds,
> Dying, the Threshold), the exact two conditions that must both hold before a player character can die,
> the warning the player always sees first, the closed menu of prices offered at the brink in place of a
> death roll, what Yield and Retreat buy, what each kind of victor does with a beaten character and what
> that writes into the world, the marks that near-death leaves, the three rests and what they restore,
> wounds and their treatment, poisons, diseases and curses as staged afflictions, mental strain as a
> track that ends careers and never lives, and harm to companions. It is shaped by two findings that
> pull in opposite directions and are both true: the owner's lock that death is real but telegraphed
> (a single unlucky roll never ends a character without warning), and the research finding that an AI
> referee's dominant failure is leniency, a reluctance to impose loss. The design answer is the same
> for both: every transition on the ladder is a state change the engine makes from declared stakes, and
> the narrator has no tool that softens or undoes one. The player holds the last choice; the DM never
> holds mercy.

**Reading this chapter.** Standard format (00.19). Rules are 07.1–07.12. The algorithms are PR-07-1…12.
Tables are T-07-1…20. Worked examples WE-07-1…7 continue 00's character **Wren**. The machine-readable
companions are `data/harm.yaml` (ladder, keys, warning, rests, dispositions, dread, fatigue, templates),
`data/injuries.yaml` (wounds, scars, brink marks, maims, haunts), `data/afflictions.yaml` (poisons,
diseases, curses) and `data/last_chance.yaml` (the nine options), with contributions to shared files in
`data/conditions.yaml owner-block 07` and the 07 owner-blocks of `data/effects.yaml` and `data/boundaries.yaml` [verification: V2a-006]. The simulation is
`rules/_process/simulation/07-harm-sim.py`, written up in `07-harm-sim.md`.

---

## Design intent

**Goals served.** Goal 1: a player who knows that death cannot arrive unannounced tries bold things, and
a player who knows that defeat opens a new situation (a cell, a debt, a scar, a lost cache) instead of
ending the game is free to lose. Goal 2: an AI that cannot be argued into mercy, because mercy is not
one of its decisions, rules harm correctly on the thousandth use [BRIEF §3; R4 §6.1].

**The shape in one paragraph.** Vitality is wind, luck and guard: losing it is being pressed, not being
cut open [R6 C-08; 00.3.12]. At 0 the character is **Staggered**: still acting, but every further blow
is a **wound**, a named lasting thing with its own recovery clock. Wounds add up as a **wound load**; at
load 3 the character falls. *How* it falls depends on one flag set before the blow was declared. Under
a **lethal** frame it falls to **Dying**, a three-step ladder with one action a turn and a check each
turn, entered one step deeper for every recent fall still unhealed. Under any other frame it goes
**Down**: out of the scene, alive, and in the hands of whatever beat it. A step past Dying 3 is the
**Threshold**, where nothing is rolled: the engine builds a menu of prices from state (capture, a maim,
a bargain, being left for dead, a rout that costs the world, a point of fate, a last stand, a gamble,
the end of the road) and the player chooses. Death is written only by a last stand the player chose or
a gamble the player took and lost [R6 §C.3 C-R1…C-R3; BRIEF A2 #3].

**Why leniency cannot enter.** (a) Harm is applied by `apply_harm` from a frame committed before the
roll; narration restates the result [R4 §6.2 items 1–2; INV-2]. (b) Every transition is a `[T]` on
tracked state: Vitality 0, load 3, step 4. (c) Whether an adversary presses is the DM's open pick from the
acts legal now, logged and watched for passivity, and its `defeat_disposition` decides what defeat means (06.9.1; 09)
[revision: R2-M]. (d) Defeat outcomes are a table keyed
to the victor's nature, executed as state writes, so "defeat" cannot quietly become "a lucky escape"
[R4 §6.2 item 5]. (e) The last-chance options are built by the engine from requirements in data, and
the DM may strike one only by citing a fact from a closed list of reasons. (f) The one place softness is
designed in, the menu, belongs to the player, and every option on it is a real, recorded loss.

**Why death is still real.** A character who reaches the Threshold pays something permanent or risks
everything. The always-available options are a maim (an attribute lowered for life), a last stand
(death), the gamble (45% death for an average novice, shown before the choice) and the end of the
character's adventuring life. The escape that costs nothing, a spent point of fate, grows dearer each
time it is used and runs out. The simulation shows what this means in play: in fights 09 advises as
*fair*, a character who never backs down reaches the menu 5 times in 100; one who takes an exit when
Staggered, 2 times in 100; in fights advised *lethal*, 80 in 100 and 34 in 100 (07-harm-sim, sections
C–D). The warning is honest.

**What this chapter deliberately avoids.**
- A death roll. Nothing in this chapter says "roll, and on a failure the character dies" except the
  Gamble, which the player must pick and confirm [R6 C-06 take; C-09 take].
- Negative Vitality, damage overflow, "massive damage". The blow that Staggers does only that (07.2.3),
  which is what makes "never one roll" arithmetic and not hope [BRIEF §4; 06.9.5].
- A death spiral. Wound penalties are status modifiers, and only the worst single one applies to a roll
  (00.3.5); no wound lowers Guard.
- A free rest button. Every rest costs time on the ladder of 00.7, and time runs every clock and every
  encounter check [R1 §07 "easy long rests trivialize"].
- Harm that narration originates. Vitality changes only through a resolved frame, a registered periodic
  effect, or a declared hazard exposure [R3 §07.4].
- Sanity as a second death track. Dread breaks leave haunts; the fourth ends a career [R6 C-R7].
- Permanent deletion of treasured gear as a default. Loss is *recoverable* loss, placed somewhere the
  player can go [R1 §07 "losing gear hurts more than the numbers suggest"].

**Precedents, in one line each** (mechanics described in this ruleset's own words). Pathfinder 2e's
dying 1–4 with a recovery check of rising DC, wounded memory, and a hero-point escape
[R: https://2e.aonprd.com/Rules.aspx?ID=2319]; Cairn's protection-then-flesh split and scars
[R: https://cairnrpg.com/second-edition/wardens-guide/combat/]; Torchbearer's closed doors to death
[R: https://sites.google.com/view/torchbearerwiki/faq]; Blades in the Dark's harm rows, resistance and
trauma [R: https://bladesinthedark.com/consequences-harm]; Dungeon World's revised brink menu
[R: https://www.dungeon-world.com/not-the-end-face-death/]; Ironsworn's bargain with death
[R6 C-14]; Fate's concession [R: https://fate-srd.com/fate-core/conceding-conflict]; 13th Age's flight at
a campaign loss [R: https://www.13thagesrd.com/combat-rules/]; Warhammer's finite fate [R6 C-17];
Darkest Dungeon's acting at Death's Door and its stress breaks
[R: https://darkestdungeon.wiki.gg/wiki/Stress]; The One Ring's Shadow and permanent scars
[R: https://cubicle7games.com/en_US/blog/the-one-ring-the-shadow]; Kenshi and Mount & Blade's
victor-decides defeats [R6 C-19].

---

## Rules

Rule ids are `07.S.R`. Kinds per 00.2.2. Terms used throughout, defined where first ruled and collected
in the glossary additions (Interface requests): **Staggered**, **wound**, **wound load**, **Dying**,
**brink**, **Down**, **Threshold**, **stabilized**, **lethal frame**, **lethal context**, **mark**,
**scar**, **maim**, **haunt**, **dread**, **rest site**, **treated**.

### 07.1 Vitality and the harm states

**07.1.1 What Vitality is.** `[D]` + `[N]` [C:P13; DL-00A-09; revision: I-065] Vitality is the primary harm resource (00.3.12): a character's
wind, luck and guard, the margin by which a blow fails to be telling. Loss of Vitality is being pressed,
bruised, nicked, winded and driven back. While Vitality is above 0 the character has **no wound**: no
bone is broken and nothing needs a healer. Four descriptors are shown to the player and are the only
words narration may use for the PC's state (they refine T-12-10):

| Descriptor | True when | Words the fiction may use |
|---|---|---|
| **fresh** | Vitality = maximum | steady, untouched, breathing easy |
| **worn** | above half, below maximum | scraped, breathing hard, a step slower |
| **bloodied** | at or below half, above 0 (06.7.6) | bleeding from small cuts, battered, every movement costs |
| **Staggered** | Vitality 0 | reeling, on a knee, guard gone, the world narrowing |

*Narration may not imply:* a broken bone, a deep wound, a lost limb, unconsciousness or death for a
character whose state does not hold a wound record, the Down flag, or `harm_state.dead`; a Vitality
number in fiction; a state better than the store holds ("you shrug it off" at bloodied).

**07.1.2 Maximum Vitality.** `[D]` [DL-07-18; DL-00-04; revision: I-065] A PC's maximum Vitality is computed, never set by hand:

`vitality.max = base + 2 × (power_band − 1) + effects − wound penalties`, clamped to **at most 24** and
to **at least half of (base + band growth), rounded up**.

- `base` is chapter 02's creation formula evaluated on the character's **current** attributes (envelope
  10–16, reference 12), so the one lifetime +1 to Endurance or a maim to it moves the base as 02's
  formula says (00.4.4).
- `power_band` is 04's `power_band(pc)`, from **confirmed** tiers only (04.5.6; 00.17.1 Q5). The growth is +2 per
  band above the first: 12 / 14 / 16 / 18 / 20 at the reference base. This is the orchestrator's binding
  decision DL-00-04, taken because with flat Vitality a P4 specialist beat one T4 foe 68% of the time
  and a P5 one T5 foe 57% (against 87% and 80% with growth; `06-conflict-sim.md` section F). It answers
  R3's open question of where Vitality growth comes from without levels: from recognized standing, not
  from a counter and not from gear.
- `effects` are `eff.max_modify` instances (family `adjust`, summed) from abilities and items (05, 08).
- `wound penalties` are 07.2.5's: each unhealed Heavy, Grievous or Catastrophic wound lowers the maximum
  by its unit magnitude (2 / 3 / 4).
- Handler **`h.07.vitality_max`** recomputes the maximum at every `reflection` and `season` boundary
  (phase 9, after 04's passes in phase 8) and at once whenever a wound is taken or healed or an
  `eff.max_modify` begins or ends. When the maximum **rises** because `power_band` rose, current
  Vitality rises by the same amount. When it rises for any other reason, current is unchanged. When it
  **falls**, current is clamped to the new maximum and is never otherwise reduced.
- Adversaries' Vitality is their template's (09, within 00.3.7); companions' is 16's. Neither grows by
  this rule.

**07.1.3 The harm-state ladder.** `[D]` + `[T]` [DL-07-03; DL-07-04; C:V; C:P10; revision: I-065] Every character holds exactly one harm state (00.17.1 Q15;
ids reserved by 00). Harm states are not conditions (00.9.4): nothing cleanses them, and each changes
only by the transitions in this table (`data/harm.yaml#harm_states`).

| State | Entered when `[T]` | While in it | Left when |
|---|---|---|---|
| `harm_state.active` | Vitality > 0 | acts normally; harm lowers Vitality | Vitality reaches 0 → Staggered |
| `harm_state.staggered` | Vitality reaches 0 by any harm (07.2.3) | acts normally (three actions, reaction); **every harm event is a wound** and adds to the wound load (07.2.4–07.2.6); the exits card is shown (07.3.7) | Vitality restored above 0 → active (wounds and load stay); load reaches 3 under a lethal event → Dying; load reaches 3 under a non-lethal event → Down (07.2.9) |
| `harm_state.dying` with `dying_step` 1…**3** | a Staggered PC's wound load reaches 3 under a **lethal** harm event (07.2.6), at step `min(3, 1 + brink)` | prone; **one action** a turn, no reaction; a dying check at each of its `turn_end`s; each lethal harm event adds a step (07.2.7) | step falls to 0 or any Vitality is restored → **stabilized** (07.2.8); step would pass 3 → the **Threshold** (07.5.1) |
| `harm_state.dead` | only by 07.3.1 (both keys) | the character's play is over; chapter 11's legacy procedure runs | never (05.7.10: canon decides whether anything raises the dead; no rule here does) |

Two flags sit beside the ladder. **`down`** (07.2.9): out of the scene and alive. **`defeated`**
(00.17.1 Q15), with a `manner`: `down | yielded | captured | fled | dead` for a PC; for adversaries and
NPCs also `dying` and `driven_off` (06.13.3). A **Dying PC is not yet defeated**: it still has an action
and a voice, and the conflict continues while any side is willing and able to act against it (06.13.1).

**07.1.4 Bloodied.** `[D]` [DL-00A-22; R5 HR-01; revision: I-065] `bloodied(x)` is 06.7.6's expression: `0 < current` and `current × 2 ≤ max`.
It is a shown descriptor and a hook point (`on_vitality_threshold` with `threshold: half`), and it
carries no penalty of its own. For adversaries it is one of the three things the narrator may know
about their Vitality (unhurt, bloodied, down; 00.6.3).

**07.1.5 Harm comes only from state.** `[D]` A character's Vitality, wounds, dread and afflictions change
only through: (1) `apply_harm` called by a resolved frame's success (an attack, 06) or cost
(`cost.harm`, 01.13.2); (2) a registered periodic effect of a condition, affliction stage or place
(00.7.5 phase 2); (3) a hazard exposure declared by chapter 10's procedure (07.10); (4) an ability's
stated price (05.6.6). Narration never originates harm: a sentence that describes the PC being struck,
burned or cut with no such event behind it fails the claim check (12.3) [R3 §07.4; INV-1].

### 07.2 `apply_harm`, wounds, and falling

**07.2.1 `apply_harm`.** `[D]` [C:I; DL-07-03; DL-07-14; revision: I-065] The one tool that changes Vitality downward (00.14.2 #17).

```
apply_harm(target, severity S1..S5, harm_tags [tag],
           source {entity | hazard | affliction, frame_id | null, effect_id | null},
           lethal: bool = false,          # Key 1 for this event (07.3.6); false unless every test holds
           mode: lethal | nonlethal = lethal,   # the attacker's intent at 0 Vitality (06.4.8)
           no_reduction: bool = false,    # internal harm, falls, overdraw (07.2.2)
           periodic: bool = false,        # a condition, affliction or place tick (07.2.4)
           dealt: int | null)             # the dealer-side amount when 06.4.6 already computed it
→ {amount, breakdown, wound | null, load, transition | null, obligations [str]}
```

It runs PR-07-1: the receiver's side of the evaluation pass (00.10.5), then the ladder. `lethal` and
`mode` are different things and both are needed: `lethal` says whether this event carries Key 1 and may
therefore move a PC or companion toward death; `mode` says what the attacker is trying to do to a
target that reaches 0. A PC struck by a `mode: lethal` blow under `lethal: false` is the ordinary case
of a fight that cannot kill: the foe means it, and the rules do not allow it yet.

**07.2.2 Reduction and its cap.** `[D]` Harm taken is lowered by the receiver's reduction, family
`reduction`, summed and capped at **4** (the top of 00's 0…4 envelope; `harm.yaml#reduction_cap`).

| Source of reduction | Amount | Applies to |
|---|---|---|
| worn armor, light / medium / heavy (08; T-06-11) | 1 / 2 / 3 | `harm.physical` from attacks and shaped effects |
| natural armor (09) | per template, 0–3 | as the template says; marked `no_gaps` (06.4.10) |
| items and abilities (`eff.harm_reduction`) | 1–4 by harm tag | the listed harm tags, with cascade |
| a shield | 0 | nothing: a shield adds to Guard (T-06-7) |

Reduction is ignored (`no_reduction: true`) for exactly these: harm from inside the body (`cond.bleeding`,
`cond.choking`, affliction stages, overdraw and Backlash strain, 05.6.6); falls and being crushed by
mass (a fall, a collapse, deep water's weight); starvation, thirst and exhaustion. A weapon with
`armor_breaking` ignores 1 point of worn armor, and a called shot at a gap ignores worn armor entirely
(06.4.10). Resistance and vulnerability (×½, ×2) apply after reduction (E5), by harm tag. Harm is never
below 0, and an attack reduced to 0 still hit (06.4.6): its riders apply and nothing on the ladder
moves. *Why 4:* at the cap a Moderate blow (3) does nothing and a Grievous one (8) still takes 4, so
armor makes a character proof against rabble and never against a troll [R1 §07 "defense stacking needs
hard caps"]. *Check:* Wren in a padded jack (light, 1) takes 2 from a soldier's sword (S2) and 4 from a
reeve's halberd (S3).

**07.2.3 The Stagger rule.** `[D]` + `[T]` When harm would take Vitality below 0, Vitality becomes **0**,
the character becomes **Staggered**, and **the rest of that harm is discarded**. The blow that Staggers
does nothing else: it leaves no wound, adds no wound load, and cannot move anyone to Dying or Down.
This holds for every source and severity, including a Catastrophic blow against a character at 1
Vitality and an overdraw (which 05.6.6 already refuses at 0). It is the arithmetic form of "a single
unlucky roll never ends a character": from any Vitality above 0, one harm event ends at Staggered
[BRIEF §4; 06.9.5; DL-07-03]. On becoming Staggered the engine fires `on_vitality_threshold` (threshold
0), ticks the opposing morale clock −2 (06.11.3), and raises the exits card (07.3.7).

**07.2.4 Wounds.** `[D]` While a character is Staggered or Dying, each harm event with a final amount of
1 or more is a **wound**. Its **severity** is the bucket of the final amount (after reduction and
multipliers), read on the severity scale's own harm values:

| Final amount | 1–2 | 3–4 | 5–7 | 8–11 | 12 or more |
|---|---|---|---|---|---|
| Wound severity | S1 Light | S2 Moderate | S3 Heavy | S4 Grievous | S5 Catastrophic |
| Wound load added, U(severity) | 1 | 1 | 2 | 3 | 4 |

- **A wound record is created** for every such event that is **not periodic**: the engine picks the
  entry in `data/injuries.yaml` keyed by the harm's family, the wound's **site** and its severity
  (PR-07-2), writes it to `wounds`, and applies its effects (07.2.5). The site is the one a called shot
  named (06.4.10: the leg, the arm, the head), else the template's stated site for that attack (09),
  else an engine roll on `tbl.wound_site` (d12: 1–3 arm, 4–6 leg, 7–10 body, 11–12 head).
- **A periodic event** (`periodic: true`: a tick of bleeding, burning, choking, an affliction stage, a
  place's ongoing harm) adds its load and creates **no** record: the condition is its own record. A
  Staggered character who is bleeding is therefore two turns from falling, and staunching it (one
  action, Easy; T-06-10) is the answer the fiction suggests.
- The DM chooses nothing here. *Narration may not imply* a wound of another site, kind or severity than
  the record, or any wound without one [R4 §9 07 item 3: wounds come from a table, never from the narrator].

**07.2.5 What a wound does.** `[D]` A wound acts through one carrier condition for its site
(`cond.wound_arm`, `cond.wound_leg`, `cond.wound_body`, `cond.wound_head`; `data/conditions.yaml owner-block 07`),
applied at the wound's severity with stacking `replace_stronger`: two arm wounds penalize as the worse
one. T-07-4 is the full table; in summary:

| Severity | Status penalty on the site's checks | Also | Maximum Vitality | Heals (07.8.6) |
|---|---|---|---|---|
| S1 Light | none | — | — | at the next rest of any kind, or `scene_end` |
| S2 Moderate | −1 | — | — | at the next long rest of partial or full quality, or when treated |
| S3 Heavy | −2 | the site's restriction, first rung | −2 | a 4-segment recovery clock |
| S4 Grievous | −2 | the site's restriction, second rung; leaves a **scar** | −3 | a 6-segment clock that only care advances |
| S5 Catastrophic | −3 | the site's restriction, third rung; leaves a scar; becomes a **maim** if not operated on within 7 days | −4 | surgery, then a 12-segment clock |

The site's checks: **arm** — beats with `trait.action.attack` or `trait.action.manipulate` made with
that arm, Grapple, and Might-based Force and Exert; **leg** — Move, Evade, and Exert or Sneak that the
legs carry; **body** — Endure with Endurance and sustained Exert; **head** — checks with Wits or
Intellect (including tempo) and beats with `trait.action.concentrate`. Penalties are family `status`:
with any other condition's penalty, only the worst one applies to a roll (00.3.5), so wounds never stack
into a spiral. No wound lowers Guard or any other defense. The dying check, the Gamble and affliction
stage checks ignore wound penalties (07.2.7). **Grit:** a character may declare 05's push (1 Focus,
05.6.7) as grit: that beat ignores status penalties from wounds, and gains no reach from the push
[R1 §07 "act despite harm"].

**07.2.6 Wound load and the fall.** `[D]` + `[T]` `wound_load` is a counter on the character: the sum of
U(severity) over harm events taken while Staggered since the load was last cleared. When a harm event
brings the load to **3 or more** on a Staggered character:

- if that event is **lethal** (07.3.6): the character enters **Dying** at step `min(3, 1 + brink)`
  (07.2.8), falls `cond.prone`, and `on_dying` fires;
- if it is **not lethal**: the character goes **Down** (07.2.9).

So one Grievous wound fells; a Heavy wound and any other; or three lesser ones. Once the load is 3 or
more, any later harm event on a Staggered character fells it again at once. The load is cleared by
handler `h.07.load_clear` at `scene_end` and at the completion of any rest, and by a last-chance outcome
that says so; restoring Vitality in the middle of a scene does not clear it. *Why 3 and not 2:* at 2 the
simulation put a never-yielding character on the menu 9 times in 100 fair fights and 36 in 100 hard
ones; at 3, 5 and 26, which meets the targets of T-07-18 [DL-07-04].

**07.2.7 Dying.** `[D]` + `[T]` [DL-07-04; DL-07-23; R5 HR-03; revision: I-065] Dying is the state at death's door, and the character still acts.
- **While Dying** the character is prone, has **one action** on its turn and no reaction
  (`eff.06.fewer_actions`), may speak, may Yield (free, 07.4.1), may crawl one band with its action, may
  use an item or ability on itself or command a companion (06.14.2), and may strike a last blow (with
  prone's penalty). It may not overdraw (05.6.6), stand, or Retreat under its own power.
- **The dying check.** At each of its `turn_end`s (handler `h.07.dying_check`, phase 2; outside a
  conflict, at each `round`) the engine rolls an Endure check for it: `d20 + Endurance + competence +
  edge`, with no levers, snags or status, against the **stabilize DC** of its current step:

  | Step | Stabilize DC (tier) | critical success | success | failure by 3 or less | failure | critical failure |
  |---|---|---|---|---|---|---|
  | Dying 1 | **10** (Easy) | stabilized | stabilized | holds | Dying 2 | Dying 3 |
  | Dying 2 | **15** (Moderate) | stabilized | Dying 1 | holds | Dying 3 | the Threshold |
  | Dying 3 | **20** (Hard) | stabilized | Dying 2 | holds | the Threshold | the Threshold |

  It is a resisted check, not a declared beat (01.18.3): it takes no action, cannot be pushed, and the
  player may spend fate to reroll it (01.16.3). The degree is 01.8.1's.
- **Lethal harm while Dying** adds **one** step (a wound of S4 or S5: **two**) and its wound record.
  Non-lethal harm to a Dying character changes nothing on the ladder (07.2.11).
- **First aid.** Another character engaged with the Dying one may spend one action on `verb.handle`
  (first aid: stabilize only, 01.18.14) against the same stabilize DC; a healer's kit is a Precision
  lever, and `lic.training.lore_medicine` supplies competence. Success or better: stabilized. Failure:
  nothing changes. A Dying character cannot give itself first aid: its own fight is the dying check (a healer's kit or bandage used on itself is first aid, not the "item on itself" of the first bullet; a draught or an ability that restores Vitality is) [verification: V2c-005].
- **Any effect that restores Vitality** to a Dying character stabilizes it at once and then restores
  the amount (05.7.8's cap applies to the restoring, not to the stabilizing).
- **Time.** While any PC or companion is Dying, time runs in rounds even if no enemy remains; the scene
  does not skip ahead until the ladder has resolved.
- *What the numbers do* (07-harm-sim section B; no help, no further harm): with an Endure modifier of
  +2, a first fall (Dying 1) stabilizes 85% of the time in about two rounds; a fall entered at Dying 2
  stabilizes 44%; at Dying 3, 11%. With a companion giving first aid each round: 98%, 79%, 35%.

**07.2.8 Stabilized, and brink.** `[D]` **Stabilized** means: `dying_step` becomes 0; the harm state
becomes Staggered (Vitality 0, or active if Vitality was restored); the character is conscious and
prone; `on_stabilize` fires; and the character takes one **brink wound**, `inj.the_brink`. This is the
definition 05's `ab.breath_of_life` and every "stabilize" in data refer to.
- **Brink** is the number of unhealed `inj.the_brink` wounds the character carries. It is the ruleset's
  memory of recent falls: the next time the character falls, it enters Dying at `1 + brink`, to a
  maximum of 3 [R: https://2e.aonprd.com/Rules.aspx?ID=2319 (wounded); R6 C-R2]. Entering Dying never by
  itself reaches the Threshold: every fall gives at least one turn at the door.
- A brink wound is a Heavy wound with no site and no status penalty: it lowers maximum Vitality by 2 and
  heals on a 4-segment recovery clock by the same daily ticks as any Heavy wound (07.8.7), one brink
  wound at a time. A character back from the door is therefore two days from whole in a haven with a
  healer and four on the road alone.
- A fate reprieve (07.5.8) stabilizes **without** a brink wound.
- *Check (section F):* the same hard fight entered with brink 0, 1, 2 reaches Dying equally often (19 in
  100) and goes on to the menu 74%, 90% and 98% of those times.

**07.2.9 Down.** `[D]` + `[T]` [DL-07-03; DL-06-23; DL-07-21; revision: I-065] Down is where a fall ends when death was not on the table.
- A character goes Down when its wound load reaches 3 under a non-lethal event (07.2.6), when a
  `mode: nonlethal` attack brings it to 0 Vitality (06.4.8: at once, with no wounds), when it collapses
  from deprivation or lack of sleep (07.8.10), or when a rule says so.
- **Down** means: `down: true`; `defeated` with manner `down`; `cond.unconscious` and `cond.prone`; the
  harm state stays Staggered (Vitality 0); the ladder is frozen: no harm event of any kind moves a Down
  character toward Dying, and a `kill` victor with no lethal context can do no more than leave it for
  dead (T-07-11, row `kill`).
- If the PC is Down, the conflict ends unless companions fight on, and the victor's disposition runs
  (07.6). The PC wakes when the disposition procedure says, or after one interval if nothing took it,
  Staggered, with its wounds.
- An **adversary or NPC** at 0 Vitality follows 07.2.10, not this rule.

**07.2.10 Harm to others.** `[D]` [R1 §09; DL-06-23; revision: I-065] Adversaries and NPCs use a shorter ladder (the asymmetry is deliberate:
the opposition's side must stay cheap to run, R1 §09). At 0 Vitality an adversary is **defeated**
(06.13.3) and its fate is read from the defeating event:

| Defeating event's `mode` | NPC depth `walk-on` (12.11.1) | `recurring` or `principal` |
|---|---|---|
| lethal | **dead** | **Dying**: defeated and helpless; dies at `scene_end` unless stabilized (first aid against Moderate, any healing) or finished (a declared beat; chapter 03 records it) |
| nonlethal | `cond.unconscious` for the scene, alive | the same |

A mob loses members as its pool falls (06.10.2); members are walk-ons. No Key is needed for an
adversary's death: the two keys protect the PC and companions. Companions follow 07.12.

**07.2.11 Lethality is inherited, and non-lethal harm is capped.** `[D]` [DL-06-23; DL-07-01; revision: I-065] (a) A harm event that has no
frame of its own (a condition's tick, an affliction's stage harm, a place's ongoing harm) takes its
`lethal` value from the frame or exposure that started it, re-tested against 07.3.5 at the moment of the
tick. (b) A harm event with `lethal: false` can lower Vitality, Stagger, wound, and put a character
Down; it can **never** move a PC or a companion into Dying, add a dying step, or open the Threshold
(INV-6; 01.13.2; 05.6.6). Applied to a character who is already Dying, non-lethal harm is recorded and
discarded. (c) An overdraw is `lethal: false, no_reduction: true` and is refused if it would bring
Vitality to 0 (05.6.6).

### 07.3 The two keys and the lethal warning

**07.3.1 The Two-Key rule.** `[D]` A player character's harm state becomes `harm_state.dead` only when
**both** keys are turned, and the engine refuses the write otherwise (INV-6).

- **Key 1 — declared lethality.** The harm event, or the chosen act, belongs to a **lethal frame**
  (07.3.6): a lethal context for its source was recorded and shown to the player, and had taken effect,
  **before** the declaration that led to it (07.3.2–07.3.5).
- **Key 2 — the brink, and the player's hand.** One of exactly these:
  (a) the character stood at the **Threshold** (it was already Dying, and lethal harm or a dying check
  carried it past Dying 3), the last-chance menu was shown, and the player chose **Last Stand**
  (07.5.9);
  (b) the same, and the player chose the **Gamble** and its check failed (07.5.10);
  (c) the player declared a **voluntary last stand** in a lethal context and confirmed it out of fiction
  (07.5.13);
  (d) a **Death's Bargain** was forfeited, which returns the character to the Threshold, where (a) or
  (b) then applies (07.5.5).

Nothing else kills a PC: not a critical hit, not a failed check of any kind, not a clock, not an
affliction, not a hazard, not a narrated event. Each of those can bring the character to the Threshold
if Key 1 holds, and to Down if it does not. A companion dies by 07.12's rule, which also requires
Key 1. *Narration may not imply* the PC's death, a mortal wound, or "this is the end" before the write
exists. [R6 §C.3 C-R1; BRIEF A2 #3; R: https://sites.google.com/view/torchbearerwiki/faq; DL-07-01]

**07.3.2 The lethal-context record.** `[D]` [DL-07-01; revision: I-065] A lethal context is a fact with this shape, one per source
per scene (`harm.yaml#lethal_warning.writes`):

```yaml
lethal_context:
  id: str                 # "lc.<scene>.<source>"
  source: id              # the adversary, side, hazard, clock, affliction or place it is about
  cause: enum             # advisory | archetype | disposition | severity | windup | clock | hazard | affliction | deprivation | chosen
  sign: str               # the perceivable sign given in fiction (a tell, an omen, the thing itself)
  warned_at: time         # when the warning was shown
  effective_from: beat    # the beat counter after the player's next declaration or turn (07.3.5)
  shown: true
  ends: scene_end | source_gone | cured
```

Evidence events read it for their `lethal_context` field (00.6.8), and 03's `crisis` flag reads the
actor's harm state at declaration from `harm_state` and `dying_step`, which are plain state.

**07.3.3 The lethal-warning trigger.** `[T]` + `[D]` The engine raises `trg.lethal_warning` for a source
the moment **any** row below becomes true of tracked state and no lethal context for that source exists
in the scene. The DM does not decide whether to warn; the DM delivers the warning the same turn
(`get_active_triggers` returns it until `shown` is written). The list is closed (`harm.yaml#lethal_warning.trigger`).

| Cause | True when | Source of the fact |
|---|---|---|
| `advisory` | `threat_advisory(encounter, pc)` is **lethal** when the encounter is framed, or becomes lethal when its make-up changes (reinforcements, a companion falls) | 09 (T-06-13) |
| `archetype` | a hostile adversary whose archetype or template carries `lethal_context: true` is perceived by the PC, or turns hostile | 09 |
| `disposition` | a side's `defeat_disposition` is or becomes `kill` toward the PC | 09 behaviors, 06.13.2 |
| `severity` | a source that can deliver **S4 or S5** harm to the PC comes within reach: a hazard or trap of that severity once perceived, a height of 40 ft or more beside or beneath the PC, an attack listed at S4+, or raised to S4+ by a mob's or cohort's numbers step (06.10.3) [verification: V2c-006] | 10, 06.5.8, 09 |
| `windup` | an adversary begins a Windup for a heavy blow (06.9.5) | 06 |
| `clock` | a sensed or hidden clock reaches **imminent** and its `on_complete` would expose the PC to lethal harm (PR-00-3 step 3) | 00.8.4 |
| `hazard` | the PC is about to enter, or is in, a hazard whose entry carries `lethal_context: true` | 10 |
| `affliction` | an affliction the PC carries reaches its `warn_stage` (07.9.5) | this chapter |
| `deprivation` | the PC holds three stacks of `cond.exhausted` while starving, parched or sleepless (07.8.10) | this chapter, 10 |
| `chosen` | the player declares an act whose stated outcome is the character's death (07.5.13) | the player |

Two notes. A **Windup counts as the warning for that adversary** (06's question): it is a visible sign
one full turn before the blow, so by 07.3.5 the blow itself may be lethal. An adversary whose template
lists an S4+ attack triggers `severity` when perceived, so in practice the warning comes earlier than
the Windup; the Windup row exists so that a heavy blow improvised onto a creature mid-fight is still
covered. And a fight against foes with **no** row true (robbers who rob, guards who arrest, a brawl, a
duel to first blood) has no lethal context: the worst it can do is Down. [R4 §6.2 item 4; R6 C-01…C-04]

**07.3.4 The warning the player sees.** `[D]` + `[N]` Delivering a warning is two things in the same
turn, and both are required before `shown` is written:
1. **In fiction, one perceivable sign** of the danger: the source's tell (09), the hazard's or clock's
   omen (10, 00.8.4), or the plain sight of the thing ("the gorge drops away sixty feet to white
   water"). The engine supplies the sign; the narrator words it [R6 C-04].
2. **Out of fiction, a `[WARNING]` block in plain words** (format T-07-7), never softened and never
   omitted. It names the source as the character perceives it, says that dying is possible, and lists
   the exits with their stated outcomes:

```
[WARNING] THIS CAN KILL YOU — <source as perceived>. <cause line>
          From your next action on, falling here can mean Dying. Fate: <n>.
          Exits now: Yield — <accepted: they would <disposition in words> | not accepted> ·
                     Retreat — <clean | a chase | a rout, costing <clock named>> (07.4)
```

Cause lines (fixed text per cause): *advisory* "As things stand you are unlikely to win this." ·
*archetype / disposition* "It means to kill." · *severity / hazard* "A <Grievous | Catastrophic>
danger." · *windup* "It is winding up <the attack named>." · *clock* "The signs say something deadly is
very close." (the sealed source is not named) · *affliction* "Untreated, <affliction> will put your life
at risk at its next stage." · *deprivation* "Your body is failing." · *chosen* "You have chosen this."
The OFFER of every lethal frame repeats it as 12.15.2's line `THIS CAN KILL YOU — <source> (warned
<when>)` and shows current fate (01.16.4). When the danger reaches the PC's allies, the warning names the
allies it threatens, and the advisory line names any ally a single blow could drop (16.7.11)
[integration: IR ch.16 to 07 (d)]. *Narration may not imply* that the danger is less than
stated, that the DM will hold back, or that a warning was a bluff.

**07.3.5 When a warning takes effect.** `[D]` A lethal context is **effective** from the end of the
player's next declaration, or the PC's next turn in a conflict, after the warning was shown
(`effective_from`). Until then every harm event from that source is `lethal: false`, whatever its frame
says. So the player always has at least one decision between seeing "this can kill you" and any harm
that can move the character toward death, even in an ambush that opens with the enemy's blows: the
worst a first round can do is Down, and a `kill` victor with no effective context leaves the character
for dead (T-07-11, row `kill`). A context lasts until `scene_end`, or until its source is defeated, gone, cured or
lifted; a new scene with the same source raises the trigger afresh. [R6 C-04 "information, choice,
impact"; DL-07-02]

**07.3.6 The lethal frame.** `[D]` + `[J:flag]` [DL-07-01; revision: I-065] A harm event is `lethal: true` only when **all** hold:
1. a lethal context for its source exists and is effective (07.3.5);
2. the frame that produced it is one of: (i) a **PC-actor frame** with stakes Dire and `lethal: true`
   (01.6.9 decision 3: the DM's one `[J:flag]` here, with its worst case stated there: wrongly false
   errs safe; wrongly true is legal only with the warning on record); (ii) an **adversary-actor frame**
   (06.9.2) whose harm `mode` is lethal; (iii) a **hazard exposure or affliction stage** whose entry is
   lethal (10; 07.9.5); (iv) a periodic tick that inherits from one of these (07.2.11);
3. the target is a PC or a companion (others need no key).
Engine-side this is a lookup; `apply_harm` ignores a `lethal: true` argument that fails test 1 or 3 and
logs the refusal. *Worst case (J):* the DM omits a warning the triggers did not cover (an improvised danger
with no data behind it): the frame cannot be lethal, the worst outcome is Down, and the `severity` row
catches the source the next time it is perceived (class iv, errs safe).

**07.3.7 The exits card.** `[T]` + `[D]` When the PC becomes Staggered, and again when it enters Dying,
the engine raises `trg.exits`, and the turn's out-of-fiction block states where the character stands
and what the exits are, computed from state (T-07-7):

```
[STATUS] STAGGERED — blows now wound you; at wound load 3 you <fall to Dying | go Down>. Load <n>/3.
         Exits: Yield — <…> · Retreat — <…> · or fight on.
[STATUS] DYING <n> of 3 — one action a turn; a check each turn (you need <d> or better; <odds>).
         A blow adds a step. Past 3 you choose from the last-chance menu. Exits: Yield — <…>.
```

This is the "resist or yield option offered at the brink" of R6's Key 2: a player who fights on from
here has been told, twice, what it risks. It is a status block, not a pause: the player declares as
usual. [R6 C-R1, C-R4; R4 §7.3 (locus of control)]

**07.3.8 The danger notice.** `[T]` + `[N]` [DL-07-02; revision: I-065] When `threat_advisory` is **hard** and no lethal-warning row
is true, the engine raises `trg.danger_notice` at framing: the narration carries the adversary's tells
for its band (12.10.7), and one out-of-fiction line says "`[WARNING] A hard fight — you may well lose
this. Losing here means <disposition in words>.`" It writes **no** lethal context. Its purpose is the
same honesty at a lower pitch: the player is told what losing would cost before choosing to fight.

**07.3.9 What the keys never do.** `[D]` [DL-07-01; C:III; revision: I-065] They never make a character safe from loss. Without Key 1 the
PC can still be Staggered, wounded to Grievous, put Down, robbed, captured, cursed, poisoned to its
non-terminal stages, and marked. Key 1 is cheap to turn (anything that kills carries it) and the
warning is short. The keys ration one thing only: the word *dead*.

### 07.4 Yield and Retreat

Yield and Retreat are named uses of basic verbs that are always legal (00.12.5; 01.18.19). They are the
two exits that exist before the brink, and their outcomes are stated **before** the player commits, from
state, as a G0 answer [R6 C-R4; R: https://fate-srd.com/fate-core/conceding-conflict;
R: https://www.13thagesrd.com/combat-rules/].

**07.4.1 Yield.**
```
### 07.4.1  Yield: give up on terms                               [D] [J:enum]
Trigger [T]:        the player declares surrender, or asks what yielding would mean
Loads in:           situation.conflict.*, core (when trg.exits is raised)
License check:      basic verb: verb.talk (named use: Yield). Free (06.1.4), at any moment, never
                    refused as a declaration; legal while Dying.
Decisions (J):      1. TERM [J:enum], chosen by the PLAYER, not the DM: one term from the list the
                       victor's disposition allows (T-07-8). The DM's part is to read out the allowed
                       list. Default if the player names none: `no_further_harm` only.
Computation [D]:    ACCEPTED? A lookup, not a roll (06.11.7): by the opposing side's defeat_disposition
                    and objective. capture, rob, ransom, drive_off, leave: accepted. kill, drag_to_lair:
                    not accepted, unless the side's leader holds a recorded want (15) that the PC can
                    meet, in which case the answer names it ("it would take the lantern and go").
                    The answer is given BEFORE the player commits; asking costs nothing.
                    If accepted and committed: the conflict ends (06.13.1 d); the PC is `defeated`
                    with manner `yielded`; no further harm is applied by that side; the PC stays
                    conscious; if Dying, the victors stabilize it (they accepted a living prisoner);
                    the disposition runs in its YIELDED column (T-07-11) with the chosen term.
Stakes:             none: there is no roll. The price is the disposition's yielded column.
State writes:       defeated {manner: yielded}; setback.yielded (fact, for 12.7.5); the disposition's
                    writes; the term as a commitment on the victor (kind: invariant) that the DM may
                    not break without a recorded cause; knowledge: the PC observed the way to wherever
                    it is taken (a fact it may later cite as a lever).
Narration may not imply: that a refusing foe accepted, or an accepting one refused; harm after the
                    yield; a term the player did not choose; that the victors break the term for no
                    recorded reason.
Worst case (J):     none for the DM: the only enum is the player's. A wrong acceptance lookup is a
                    `defeat_disposition` error, corrected by 12.3.4 before the disposition runs (class iv).
Examples:           inside: Wren, Staggered among Guild riders (disposition capture): "I throw down
                    the spear." Accepted; term "keep one thing": the fang charm stays on its thong.
                    outside: the same words to a barrow-wight (kill): "It does not understand quarter,
                    and would not give it. Yielding will not stop it." Nothing is spent; the exits
                    card still shows Retreat.
                    non-example: "I yield, then stab him when he lowers his guard" is two beats: the
                    Yield (accepted, conflict over) and an attack that starts a new conflict from a
                    captive's position; chapter 03 records the act on conduct.honesty.
Anchor:             yes. Intent verbs: surrender, give up, ask quarter, lay down arms, submit.
                    Knobs: targets (the whole opposing side -> one faction of it, when sides differ
                    in disposition); condition (the term). Also the anchor for an NPC's yield to the
                    PC (06.11.7), read in mirror.
Basis:              [00.12.5] [06.11.7] [R6 C-15, C-R4] [DL-07-08]
```

**07.4.2 Terms.** `[D]` A yield before the brink buys something a defeat does not: the PC is not harmed
further, stays conscious, sees where it is taken, and holds **one term** (T-07-8;
`harm.yaml#yield.terms`): `parole` (not bound; the PC's word is its bond, and breaking it is a
`conduct.honesty` event), `keep_one_thing` (one named item is not taken), `spare_another` (a named
companion or bystander goes free), `send_word` (a message goes to a named NPC or faction: the rescue or
ransom lead starts with one tick), `an_audience` (the PC is brought before the side's leader instead of
to a cell). A yield made **while Dying** buys no term beyond being stabilized. No fate is earned by
yielding: 01.16.2's list is closed, and a reward for surrender would make every hard fight a farm
[DL-07-08].

**07.4.3 Retreat.**
```
### 07.4.3  Retreat: leave the fight at a stated price            [D] [J:flag] [J:enum]
Trigger [T]:        the player declares withdrawal from a conflict, or asks what retreating would cost
Loads in:           situation.conflict.*, core (when trg.exits is raised)
License check:      basic verb: verb.move (named use: Retreat). Legal unless the PC is flag.cornered,
                    cond.restrained, cond.pinned, Dying or Down (those say what must happen first:
                    break free, clear the corner, be carried).
Decisions (J):      1. ROUTE [J:flag]: "Is there an established way out of this scene that the PC can
                       take?" True only when the place graph or a recorded feature gives one (a door,
                       a gap, open ground, the way the PC came). False when every recorded exit is
                       blocked or held. Unestablished -> the Oracle (00.12.7), odds from the scene.
                       False -> the PC is cornered in fact: write flag.cornered; Retreat is illegal.
                    2. WHICH CLOCK [J:enum], only for a rout: among the clocks the engine returns
                       (see below; at most four), the one this fight was about. Default: the first
                       returned.
Computation [D]:    PURSUIT TEST, from state: a pursuer is WILLING when its side's objective is kill,
                    capture or rob toward the PC and the side is not broken; ABLE when its pace is at
                    least the PC's (06.3.3), it is not held or prone, and it has a WAY TO FOLLOW: no
                    shut `barrier` or other recorded feature that blocks movement (`no_line` for
                    Moves: 06.3.8; T-06-9 rows 11, 19, 26) stands between it and the PC's route.
                    A barrier it could break still blocks: breaking it is a Force against the
                    barrier's tier on its own turn, and the PC is gone by then; the OFFER states
                    that tier as the pursuers' delay. [revision: I-076]
                    (a) No pursuer both willing and able -> a CLEAN RETREAT, certain.
                        Price: the parting blow, if the PC is engaged when it declares (once: the
                        heaviest engaged enemy's ordinary attack severity, one rung lighter, through
                        apply_harm with lethal: false); and what is left behind (07.4.4).
                    (b) Some pursuer willing and able -> the player picks one:
                        RUN FOR IT: uncertain, no stated price: a chase (06.12), escape 6 against
                        pursuit 8, starting from the nearest pursuer's band; or
                        ROUT: certain. Price: the parting blow as above; what is left behind; and a
                        WORLD COST: `tick_clock` of U(S3) = 2 on one clock that belongs to the
                        victors or to what the PC was trying to stop. The engine returns candidates
                        in this order: the opposing side's faction goal clock (11); an active danger
                        or countdown clock of the scene owned by that side; the opposing clock of the
                        thread the scene served; if none exists, it creates `clk.grudge` for the
                        victor (danger, 6 segments, hidden with omens, 2 filled).
                    The whole price is shown before the player commits. The Retreat takes the PC's
                    turn; at its end the PC leaves the conflict (06.2.5) for the nearest place the
                    route reaches.
Stakes:             clean retreat and rout: none (certain, with cost: 01.4.5). A chase: 06.12.3's.
State writes:       position; apply_harm (parting blow); objective_lost (fact) when the scene had
                    one; left_behind facts; for a rout: the clock tick and setback.retreated
                    {severity: S3}; conflict_end for the PC.
Narration may not imply: an escape without the stated price; a pursuit the test did not find; a
                    world cost other than the clock named.
Worst case (J):     ROUTE wrongly true: one retreat that the fiction should have blocked (the route
                    becomes an established fact, usable by both sides after; class iv). WHICH CLOCK:
                    another clock of the same side takes the 2 ticks (class i).
Examples:           inside (clean): Wren, not engaged, backs out of a cellar from two ghouls that
                    are slower than she is (pace lower): certain, nothing to pay but the satchel on
                    the far table.
                    boundary (rout): the same cellar, but the thing behind her is a cinder hound
                    (faster, objective kill): "Run for it (a chase), or rout: you get out, and the
                    hound follows your trail toward Ashford (Cinder Hunting Ground +2)."
                    boundary (barred): the hound is on the far side of the cellar door Wren has
                    just slammed and barred (T-06-9 row 11): no way to follow, so the retreat is
                    clean ("it will be through that door with a Force against Moderate; you will
                    be up the stair by then"). [revision: I-076]
                    outside: Wren is flag.cornered in a barrow niche: Retreat is illegal; the card
                    names what would clear the corner (Force past it, 06.5.6).
                    non-example: "I retreat and take the chest with me": the chest was not in hand;
                    it is left behind unless a beat got it first.
Anchor:             yes. Intent verbs: withdraw, pull back, flee the field, break off, get out.
                    Knobs: time_cost (a turn -> an interval when leaving a site by a long route);
                    harm_severity (the parting blow: one rung lighter -> none when a companion
                    screens the withdrawal, 06.14.4 "hold this ground").
Basis:              [00.12.5] [06.12.1] [R6 C-16, C-R4] [01.4.5] [DL-07-09]
```

**07.4.4 What is left behind.** `[D]` [DL-07-09; DL-07-19; revision: I-065] On any Retreat, rout or defeat, each of these is written as a
fact, and none is lost without one: the scene's **objective** (`objective_lost`); every **item** not on
the PC's person or in hand (its location stays where it was); a **companion** who is Down or Dying and
not carried (one body may be carried by the PC or by another companion; carrying lowers the carrier's
pace by one, which enters the pursuit test); a **mount** not ridden. Companions able to move come with
the PC. A companion left Down among enemies follows the victor's disposition toward companions (07.12.3).

### 07.5 The Threshold and the last-chance menu

**07.5.1 The Threshold.** `[T]` + `[D]` [DL-07-05; C:P10; revision: I-065] The Threshold is reached when a Dying character's step would
become 4 or more, by lethal harm or by a dying check (07.2.7). At that instant: the step stays at 3;
nothing further is applied; the conflict, if any, **pauses** (no participant acts); `dread` rises by 2
(07.11.2); the fact `setback.threshold` is written; and the engine builds the last-chance menu
(PR-07-5). The character is not dead and the narration may not say or suggest that it is: the fiction
holds on the moment (the blade at the top of its arc, the water closing over).

**07.5.2 Building the menu.**
```
### 07.5.2  The last-chance menu                                  [D] [J:flag]
Trigger [T]:        the Threshold (07.5.1); a forfeited bargain (07.5.5); a voluntary last stand asks
                    only for option 7 (07.5.13)
Loads in:           core (trigger-loaded)
License check:      none: the menu is offered to every PC
Decisions (J):      1. STRIKE [J:flag], per option that survived the engine's requirement test:
                       "Does a recorded fact of this scene make this option impossible?" True only
                       for a reason on that option's closed `struck_when` list (T-07-10), citing the
                       fact id. Uncertain -> false (the option stays). The DM may not strike an
                       option for tone, mercy, drama, or because another option "fits better".
                    2. BARGAINER [J:flag], only for option 3: "Is there a recorded power here that
                       could take a debt?" True only when an entity present or bound to the scene
                       carries `can_bargain: true` (the victor's master, a keeper the PC serves, the
                       power of the place), or the region's canon names a default bargainer (12.16.6).
Computation [D]:    PR-07-5. The engine evaluates each option's `requires` in data/last_chance.yaml
                    against state, applies strikes, and then VALIDATES: at least three options remain
                    and at least one of them is not death. The three always-available options (maimed
                    or, when that is spent, the road's end; last stand; the gamble) make this hold in
                    every case; if a strike would break it, the engine refuses the strike.
                    Each remaining option is shown with its full price computed from state: who takes
                    the PC and where, which attribute a maim takes, what the bargainer asks, which
                    clock a rout ticks and by how much, the fate cost, the gamble's exact odds.
Stakes:             the menu itself rolls nothing. Option 8 is a lethal frame with its own OFFER.
State writes:       offer {kind: other, content: the menu}; on the choice, the option's `outcome` and
                    `world_writes`; setback facts; the chronicle line; a brink wound (unless the
                    option says not); a mark (07.7).
Narration may not imply: death before a death option is chosen and resolved; an option not on the
                    built menu; a cheaper price than shown; that the DM chose.
Worst case (J):     a wrong strike removes one option of nine while three, one of them not death,
                    always remain; the strike's fact id is on the record for the player to dispute
                    (class iv). A wrong BARGAINER true: a bargain is offered whose asker the DM must
                    then keep as a real entity with a want (class ii: an offer the player may decline).
Examples:           inside (strike): in a sealed, empty tomb no one is present to take a prisoner:
                    the engine's own requirement removes `captured`; the DM strikes nothing.
                    boundary (strike): the victors are slavers but the PC killed their captain this
                    scene: disposition changed to kill (09) before the Threshold: `captured` and
                    `left_for_dead` fail their requirements. Had the DM merely felt they "would be
                    angry", with no recorded change, both stay.
                    non-example: "A last stand suits this moment better, so I offer only that": the
                    engine refuses a menu with fewer than three options or with no survival.
Anchor:             no
Basis:              [R6 §C.3 C-R3] [R4 §9 07 item 5] [R: https://www.dungeon-world.com/not-the-end-face-death/] [INV-6] [DL-07-05]
```

The menu is a pause point (12.2.6, block `[CHOICE]`, format T-07-7): no time passes and nothing else may
be declared until it is answered. If the player stops play, it is re-shown unchanged at the next
session. There is no default choice.

**T-07-10 The nine options** (`data/last_chance.yaml`; A = always available).

| # | Option | Requires `[D]` | Struck when `[J:flag]`, citing a fact | What it costs and writes | Still in the scene? |
|---|---|---|---|---|---|
| 1 | **Captured** `lc.captured` | a victor present whose disposition is capture, ransom, rob or drag_to_lair, or whose objective is to take the PC | the victor's disposition changed to kill this scene; quarter was offered and refused this scene (unless capture was the victor's own objective) | stabilized; the **capture** disposition runs in its *defeated* column (T-07-11): taken, stripped, a captors' clock, three openings; a brink wound; a brink mark | no |
| 2 | **Maimed** `lc.maimed` (A, once a scene, while any attribute can still be lowered) | not already chosen this scene; some attribute not yet maimed and above −2 | never | **a maim** (07.7.4): −1 to an attribute for life and a lasting restriction, chosen by table from the worst fresh wound's site; the blow that should have killed takes that instead; Dying ends; Vitality becomes a quarter of maximum (rounded up); wound load 0; a brink wound; **the character stands** | yes |
| 3 | **Death's Bargain** `lc.bargain` | a bargainer (decision 2); no unpaid bargain already held | the bargainer is the very foe at the Threshold and its objective is the PC's death by sworn duty (a recorded refusal) | stabilized; the bargainer ends the danger in its own way; the curse `aff.deaths_debt` at stage 1; a **vow** thread for what it asks, with the countdown clock `clk.deaths_debt` (8, +1 a week); forfeiting it returns the character here (07.5.5); a brink wound; the mark `inj.mark.deaths_debtor` | no |
| 4 | **Left for Dead** `lc.left_for_dead` | a victor that does not make sure (any disposition but kill and drag_to_lair), or no victor and a hazard a body can survive being left in | the hazard is one nothing is left in (a lava flow, a sealed and flooding vault) | stabilized after one **watch** passes (`advance_time`, every boundary runs); wakes at Vitality 1 where it fell, or at the nearest place downstream or below when the source was water or a fall; the scene's objective is lost; a folk victor takes all carried coin and the single most valuable carried item (07.6.4), any other victor nothing, but what was in hand lies where it fell; a brink wound; a brink mark | no |
| 5 | **Rout** `lc.rout` | Retreat's ROUTE holds and the PC is not cornered, restrained or pinned; or an able companion can carry the PC | every recorded route is held | the PC is carried or drags itself clear: stabilized, Vitality 1, at the nearest safe place the route reaches; fallen companions are carried with it; **a campaign loss**: `tick_clock` of U(S4) = 3 on the clock chosen as in 07.4.3; objective lost; a brink wound; a brink mark | no |
| 6 | **Reprieve** `lc.reprieve` | `fate.current ≥ fate_cost`, where `fate_cost = min(3, 1 + reprieves already taken in this character's life)` | never | `spend_fate(fate_cost)` (01.16.4); the event that carried the character past the door is undone; Dying ends with **no brink wound and no mark**; Vitality a quarter of maximum; wound load 0; the character stands | yes |
| 7 | **Last Stand** `lc.last_stand` (A) | — | never | one last turn of three actions (07.5.9), then **death** | for one turn |
| 8 | **Gamble** `lc.gamble` (A) | — | never | a lethal Endure check against Moderate, odds shown (07.5.10): from standing free to **death** | by result |
| 9 | **The Road Ends** `lc.road_ends` (A) | — | never | the character lives and never adventures again: stabilized, carried from the scene by whoever the fiction provides, and chapter 11's retirement runs at once with the ending *retire to a life* (07.5.11) | no |

**07.5.3 Captured.** `[D]` [DL-07-05; DL-07-19; revision: I-065] As T-07-10 row 1. The difference from an accepted Yield is the column of
T-07-11 used: a character dragged in from the Threshold holds no term, is bound, and wakes later.

**07.5.4 Maimed.** `[D]` [DL-07-05; DL-07-10; revision: I-065] As row 2, with 07.7.4 for what is taken. It is the price of staying on one's
feet: the fight, the fire or the flood is still there, and the character has a quarter of its Vitality
and its wounds. If the Threshold is reached again in the same scene, this option is gone.

**07.5.5 Death's Bargain.** `[D]` + `[J:enum]` The bargainer spares the character for a price it names.
- **The ask** `[J:enum]`: the first recorded `want` of the bargainer that the PC could fulfil (15); if it
  has none, an engine roll on `tbl.bargain_asks` (d6: return what was taken from it; bring it a named
  person or thing; end a named enemy of it; serve it one season in four for a year; carry its sign and
  its message to a named place; give up a named bond or possession). *Worst case (J):* a less fitting ask of
  the same weight; the player sees it before choosing (class ii).
- **The debt.** A vow thread (11) whose progress clock the PC fills, racing `clk.deaths_debt`
  (countdown, 8 segments, public, +1 at each `week`). The curse `aff.deaths_debt` sits at stage 1 while
  the debt is honored. Each time the countdown completes unpaid it resets and the curse advances one
  stage (07.9.7); fulfilling the vow lifts the curse, voids the clock, and earns fate by 01.16.2 ("a vow
  kept").
- **Forfeit.** Refusing the debt outright, or the curse reaching its last stage, returns the character
  to the Threshold at the next `scene_start`, wherever it is: the menu is built again **without** option
  3, under the lethal context `chosen` (the bargain was the warning). [R6 C-14; DL-07-06]

**07.5.6 Left for Dead.** `[D]` [DL-07-05; DL-07-19; revision: I-065] As row 4. The victor records the belief `pc.dead` (a fact with `truth:
false`, sealed from the victor's side), which chapter 11 may let run as a rumor: being thought dead is a
changed situation with uses of its own.

**07.5.7 Rout.** `[D]` [DL-07-05; DL-07-09; revision: I-065] As row 5. A rout from the Threshold costs one rung more than a rout before it
(three ticks, not two): leaving late is dearer than leaving early, and both prices are on the exits card
from the moment the PC is Staggered.

**07.5.8 Reprieve.** `[D]` As row 6. Fate is 01's (0–3; earned only by hard luck, to a ceiling of 2, and
by finished threads and kept vows). The first reprieve of a life costs 1, the second 2, every later one
3, which only deeds can pay. The codex shows the current cost beside fate. Fate at 0 is itself a
telegraph (01.16.4) [R6 C-17; R: https://2e.aonprd.com/Rules.aspx?ID=2319; DL-07-07].

**07.5.9 Last Stand.** `[D]` [DL-07-05; DL-07-01; revision: I-065] The character takes **one final turn of three actions** at the moment the
conflict paused. Every beat in it that would roll is instead resolved as a **critical success** at its
framed reach (so delivered reach is one rung higher, to Exceptional at most); its abilities cost no
Focus (their uses and other limits still apply); no reaction, condition or harm interrupts it; it may
not be used to restore the character's own Vitality or to leave the scene. When the turn ends the
character is **dead**: `harm_state.dead`, with Key 1 on the record and Key 2 (a) chosen. The deed is
written to the chronicle as a legend line with its witnesses (11), and chapter 11's legacy procedure
begins. *Narration may not imply* survival, a later recovery, or a fourth action.

**07.5.10 The Gamble.** `[D]` [DL-07-05; C:P8; revision: I-065] The player stakes the character on one roll, and must confirm it at an
OFFER that shows the exact odds; `auto_commit` never applies (00.13.2). The check is Endure with
Endurance: `d20 + Endurance + competence + edge`, no levers, snags or status, against **Moderate (15)**;
fate may reroll it (01.16.3).

| Degree | Result |
|---|---|
| critical success | as a Reprieve, at no cost: the character stands, no brink wound |
| success | stabilized where it lies and overlooked: as Left for Dead with nothing taken and no mark; a brink wound |
| failure by 3 or less | the player chooses one still-available option from 1–5 and pays it in full |
| failure, critical failure | **death** (Key 2 b) |

At an Endure modifier of +2 that is 5% / 35% / 15% / 45% (07-harm-sim section I). It is the only door on
the menu through which a character can walk away having paid nothing, which is why it is tempting and
why it kills.

**07.5.11 The Road Ends.** `[D]` [DL-07-05; C:VI; revision: I-065] The character survives as a person and ends as an adventurer: too
broken, too frightened or too wise to go on. Chapter 11's retirement procedure runs with this ending,
the character becomes an NPC of the world, and legacy and succession follow 11. It is on the menu so
that "at least one option that is not death" holds even for a character with nothing left to pay with,
and so that a player may choose a life over a limb.

**07.5.12 After the menu.** `[D]` [DL-07-05; R5 HR-02; revision: I-065] Whatever is chosen: `setback.threshold` and the option's own setback
fact are written (12.7.5 gives recovery room afterward); the chronicle gets one line (11); options 1, 3,
4 and 5 grant a **brink mark** (07.7.3); the conflict resumes for options 2 and 6, ends for the PC
otherwise; and the wound load is cleared. Chapter 03 may record the beat in which the fall was taken as
evidence in the ordinary way; surviving the Threshold is not itself a deed (03's request).

**07.5.14 Retire mode.** `[D]` [DL-14-05; revision: I-107] When the player's preference
`pref.death.mode` is `retire` (14.5, T-14-1), any result that would write the PC dead (an option or
disposition whose outcome is death, a lethal harm event, the fourth break) instead resolves as **The Road
Ends** (07.5.11): the character survives, leaves play as an NPC of the world, and 11's retirement,
legacy and succession run unchanged. Nothing before that point changes. The lethal warning (07.3.3), the
lethal frame (07.3.6), the Threshold menu and every odds and cost are computed and shown exactly as under
`die`. Companions and allies are unaffected; the mode covers the PC only.

**07.5.13 A voluntary last stand.** `[D]` + `[J:flag]` [DL-07-01; C:III; revision: I-065] A player may give the character's life on purpose
("I hold the gate so they can get away"). `[J:flag]` *"Does the declared act's stated outcome include
the character's death?"* True only when the player says so in plain words; uncertain → ask (01.2.4's one
question). If true, the engine raises the `chosen` warning; the player confirms out of fiction; a lethal
context of any cause must hold or be written by that confirmation; then 07.5.9 runs from whatever harm
state the character is in. *Worst case (J):* a heroic risk misread as a chosen death; the confirmation step
catches it before anything is written (class ii).

### 07.6 Defeat: what the victor does, and what the world keeps

**07.6.1 When a disposition runs.** `[T]` + `[D]` A side's `defeat_disposition` (09; the enum of 00.6.2)
runs against the PC when the PC is `defeated` with manner `down` or `yielded`, or chooses Captured at
the Threshold; and against a Dying PC as follows: when the PC enters Dying, every opposing side whose
disposition is **not** `kill` treats its objective toward the PC as achieved: it makes no further
attack-trait beats against the PC and proceeds to its disposition. A `kill` side goes on attacking; that
is what brings a Dying character to the Threshold. When several sides beat the PC, the disposition that
runs is the one of the side whose member dealt the felling event. The DM chooses none of this
[R4 §6.2 item 5; R6 C-R5, C-19].

**T-07-11 Dispositions** (`data/harm.yaml#dispositions`). "Defeated" is the column for a PC taken Down
or from the Threshold; "yielded" for an accepted Yield.

| Disposition | Typical victors (09 owns) | If the PC is Dying when it runs | Defeated: world writes | Yielded: world writes |
|---|---|---|---|---|
| `capture` | the law, slavers, cultists, a rival's men, anything that wants answers | the captors stabilize the PC (a prisoner is worth more alive) | bound (`cond.restrained`, `until_cleansed`); moved to the captors' **holding place** (07.6.3) with time advanced by the journey; all carried items taken to a **cache** (07.6.4); `clk.captors_intent` created; three **openings** written; thread `thr.captivity` opened; `setback.captured` | the same, with the chosen term (not bound under `parole`; an item kept under `keep_one_thing`); the PC saw the route |
| `ransom` | bandits with a noble prisoner, a faction with a use for the PC's patron | as capture | as capture, plus a demand sent to the NPC or faction most likely to pay (highest standing toward the PC), a price (08), and `clk.captors_intent` named for the deadline | as capture's yielded column, and the PC may name who is asked |
| `rob` | bandits, thieves, deserters | the robbers take what they came for and go; the PC's dying checks run out alone (07.2.7) | all carried coin and every item above the PC's worn clothing, one weapon and one day's supply go to a cache; the PC is left where it fell and wakes after one interval; `setback.defeated` | coin and valuables only (items with a price at or above 08's "valuable" band); the PC keeps weapons and gear, is unharmed and free to go; `keep_one_thing` protects one valuable |
| `drive_off` | territorial beasts, guards at a post, a rival who wants the ground | they leave the PC to its checks and hold their ground | the PC is moved to the adjacent place on the way it came; the place gains the fact `barred_to_pc` while that side holds it; nothing is taken; the objective is lost | the PC walks out under its own power; the same facts |
| `drag_to_lair` | predators with young, a troll with a larder, spiders, a barrow-thing collecting | nothing stabilizes the PC: its dying checks run during the drag; if they reach the Threshold, the menu is built with Captured available | the PC wakes in the creature's lair (a place created or known, with one recorded exit at least); nothing is taken, but what was in hand lies at the place of the fight; `clk.larder` created (countdown, 4, +1 a watch; at imminent its completion is lethal, so the warning fires); three openings; `setback.captured` | not accepted (07.4.1) |
| `leave` | a victor with somewhere to be; a duel's winner; most hazards' "victors" | they leave; the checks run out alone | the PC wakes after one interval where it fell; the objective is lost; nothing else | the same; a duel's terms (15) are honored |
| `kill` | the mindless dead, assassins, a blood enemy, a hungry thing with no larder | it goes on attacking | **with an effective lethal context**: this row is never reached, because the PC falls to Dying and then to the Threshold, not Down. **Without one** (the PC is Down): the victor can do no more: it believes its work done and leaves the PC for dead: `lc.left_for_dead`'s writes without a brink wound or mark, and the belief `pc.dead` on the victor | not accepted |

A hazard has no disposition: a PC put Down by one is treated as `leave`, with the hazard's own
`aftermath` if chapter 10 gives it one (washed downstream, dug out by someone who heard the slide).

**07.6.2 Defeat always writes the world.** `[D]` Besides its own row, every defeat of the PC writes:
- `victory_over_pc {victor, scene, manner}` as a fact chapter 11 consumes (the victor's side gains
  standing among its own, a named victor may gain rank: the foe who beat you grows) [R6 C-20];
- a reputation packet to 11 scoped to the witnesses (the content "beaten by the Guild's riders at
  Sedge Mill");
- the setback fact for 12.7.5 (`setback.defeated`, `.yielded`, `.captured`, `.dying_entered`,
  `.threshold`, `.retreated {severity}`, `.companion_dead`), which puts the pacing director into
  recovery: what follows a loss is room, not a second blow;
- **at least one actionable lead** (P16): an opening, a cache location, a clock the player can see or
  sense, a named person who knows. PR-07-7 refuses to finish without one.

**07.6.3 Captivity is a situation, not a cutscene.** `[D]` + `[J:enum]` A captured PC is given a place,
a clock, and ways out, in that order (PR-07-7).
- **Holding place** `[J:enum]`: among the places the engine returns (the victor's faction's holds within
  reach, 11 and 13; the victor's lair; else a camp it creates at the nearest suitable place), the first
  by distance unless the victor's recorded objective names another. *Worst case (J):* a different hold of
  the same side (class i: the journey's length).
- **The captors' clock** `clk.captors_intent`: countdown, 6 segments, sensed, +1 a day, named for what
  the captors mean to do (`[J:enum]` from the archetype's `captive_fate`, 09: trial, sale, sacrifice,
  interrogation, ransom, labor, the larder; default by org tag in `harm.yaml#captivity.fates`). Omens
  are mandatory (INV-14). If its completion would be lethal, the lethal warning fires at imminent.
  *Worst case (J):* a neighboring fate of the same clock size; its omens tell the player which (class ii).
- **Three openings** drawn by the engine from `tbl.captivity_openings` (d8, no repeats), each written
  as a fact the player can act on, with at least one that needs no roll to *find*: a careless or
  bribable guard; a bond or bar that can be worked; an ally or rival of the captors who wants the PC
  free; a fellow prisoner who knows the place; a leader who wants to talk; a transfer or change of the
  watch on the clock's next tick; something overlooked in the search (one concealable item, the PC's
  choice, if it held one); a noise outside: someone has come.
- **The thread** `thr.captivity` (kind situation) with a public progress clock "Out of their hands" (6)
  that races the captors' clock (00.8.5). Escape, rescue, ransom paid, a bargain struck, or the captors'
  intent carried out all end it, and each writes what follows.
- Time is advanced through the journey and to the first moment the PC can act (never past the captors'
  clock's first tick). Lines and veils apply to what captors do (12.5.6).
This is the "capture that becomes a new adventure" the owner's lock describes; WE-07-4 runs one.
[R1 §07 "take agency away only with narrative justification… hand back an actionable next step at
once"; C:P16]

**07.6.4 Lost gear, and getting it back.** `[D]` Nothing taken from the PC is deleted. Taken items are
moved, each keeping its id, into a **cache** owned by the taker: `cache.<n> {holder, place, items,
taken_at}`, with the place recorded and, for a capture, usually the holding place itself. The cache has
a countdown clock `clk.cache` (6, hidden, +1 a week): each tick's omen is a trace the PC could hear of
(a rumor, 11: "a spear with a rime-scored blade was on a stall in Ashford"). On completion the cache
**disperses**: mundane items are sold or used (gone, their price lost); every item with a signature
property or an item-bound ability passes to a **named holder** (an NPC the engine creates or selects),
and a rumor pointing to that holder is written. So coin and common gear are recoverable until the clock
runs out, and the things a player is attached to are recoverable always, from someone [R1 §07;
R6 C-20 (lost things lie somewhere you can go back to)]. Recovering a cache is ordinary play: a site, a
theft, a purchase, a favor.

**07.6.5 Prisoners the PC takes.** `[D]` [R5 CF-10; DL-06-23; revision: I-065] A foe that yielded or was dropped alive (06.11.7, 06.4.8) is
the PC's prisoner while `helpless` or under terms. Keeping one costs what it costs in the fiction, and
the rules that apply are already written: binding is `cond.restrained` with duration `until_cleansed`
(a Handle beat; a tier by materials); a bound prisoner counts toward 16's retinue for travel pace and
supply; its standing toward the PC is Hostile unless 15 moves it; an unwatched prisoner tests its bonds
at each `watch` (an engine fortune check against the binding's stored DC); and what the PC does with it
(ransom, release, hand over, kill) is evidence on `conduct.mercy` and `conduct.justice` (03) and a fact
for 11.

### 07.7 Marks: scars, brink marks, maims and haunts

**07.7.1 What a mark is.** `[D]` [R5 HR-02; DL-07-10; revision: I-065] A mark is a permanent change to the character recorded in
`Character.marks`, with an entry in `data/injuries.yaml` (`kind: scar | mark | maim | haunt`). Marks
are never removed by rest, treatment or ordinary healing. Each is a recorded, visible or knowable fact
others may cite (a scar is a lever for anyone identifying the PC, a snag on a disguise: 15), and each
carries `evidence_tags` so that the life it came from can be read off the body (07.7.5). There are four
kinds:

| Kind | Comes from | Mechanical weight |
|---|---|---|
| **scar** | a healed Grievous or Catastrophic wound (07.2.5) | none beyond being a citable fact; named by the wound's harm family |
| **brink mark** | surviving the Threshold by options 1, 3, 4 or 5 (07.5.12) | one bounded upside and one bounded downside, as effect references |
| **maim** | option 2; or a Catastrophic wound not operated on within 7 days | −1 to one attribute for life (00.4.3 c) and one lasting restriction |
| **haunt** | a dread break (07.11.4) | one behavioral trigger; some with an upside; the fourth ends the career |

**Aging** (11.10.5; `calendar.yaml#aging`) writes a mark through this same machinery with `source: aging`: −1
to Might, Agility or Endurance for life under 00.4.3 (c), sharing the −1-per-attribute limit with maims
[integration: IR ch.11 to 07].

**07.7.2 Scars.** `[D]` [R5 HR-02; DL-07-10; revision: I-065] When a wound of S4 or S5 heals, the engine writes the scar entry for its harm
family (`inj.scar.<family>`), noting the site. A scar has no modifier. It is description the narrator
must keep consistent (it is state) and a fact for recognition and reputation.

**07.7.3 Brink marks.** `[D]` + player choice At 07.5.12 the engine draws **three** entries from
`injuries.yaml` (`kind: mark`) whose `gate_tags` match the tags of what brought the character to the
Threshold (the source's creature and harm tags, with cascade; entries tagged `any` always match; recent
draws are halved, as 00.11.3 step 7), and the player **chooses one of the three or the plain mark**
`inj.mark.pale_streak`, which has no mechanics. This follows the shape of the gate→fill generator
(source gates the pool, a `chosen` fill) without registering a domain, and honors constitution P1:
variance after creation is never auto-applied [C:P1; R6 C-R6; R: https://cairnrpg.com/second-edition/wardens-guide/combat/ (scars that change a character)].
Each mark's upside and downside are effect references of the core library's size (an edge of +1 or +2
on one narrow check, a reduction of 1 against one harm branch, a hazard step, a lever on one kind of
Observe; against a −1 status on one narrow family, 1 point of maximum Vitality, a fear that fires once a
scene). T-07-13 lists them.

**07.7.4 Maims.** `[D]` [DL-07-10; DL-00A-07; C:P4; revision: I-065] A maim is drawn by table, never chosen by the DM: the engine takes the site of
the character's worst fresh wound (ties: the latest), rolls between that site's maim entries, and lowers
**the first attribute in the entry's order that no mark has lowered before (a maim or an aging mark) and stands above −2**
(00.4.3 c: at most −1 per attribute from marks of every kind together, never below −2) [verification: V2c-009]. If neither listed attribute qualifies,
the entry's restriction applies alone and the option still counts. The maim's restriction is an effect
that never expires (a lost hand: no method needing two hands; a ruined knee: pace −1; a lost eye: a
Precision snag on ranged attacks beyond `band.near`). A calling's lifetime +1 (04, applied when tier 4
is confirmed) may be spent on a maimed attribute like any other; it does not remove the mark.

**07.7.5 Marks as evidence and identity.** `[D]` A mark is not evidence; the beat in which it was earned
is (03's request). When a mark is written, the engine copies into its `evidence_tags` the tags of the
resolved frame that produced the felling event, read through 03's `evidence_for_frame(frame_id)`
(ledger lines only, no weights). Chapter 04 may read marks when staging recognition: a calling that
embraces a mark (the scarred veteran, the one who came back) is an **offer**, never an imposition
[R2 §07 "scars a character accepts as self"; R3 §07.2]. Chapter 11 reads marks for epithets.

**07.7.6 Offsetting a maim.** `[D]` [DL-08-32; C:P12; revision: I-065] A maim's entry lists its `offset` paths, each a real cost elsewhere:
a made replacement (08: a hook, a brace, a glass eye; `base_items.yaml` entries tagged `item.tool.kit.prosthesis`, whose
`offsets` say what each narrows [revision: I-016]; removes the restriction or narrows it, never restores the attribute); a rite (05, if the region's canon allows regrowth, 12.16.5; default: it does not); a calling
identity that turns the restriction's ground into its own (04). No path is free and none is automatic.

### 07.8 Rest and recovery

**07.8.1 The three rests.** `[D]` [DL-07-11; DL-07-23; R5 HR-05; revision: I-065] Rest durations are fixed by 00.7.2; this chapter owns what a rest is,
what breaks it, its quality, and what it restores to the body. Focus is chapter 05's (05.6.9), which
reads the quality this chapter emits (00.17.1 Q1, Q16).

| Rest | Duration | What the character does | Needs |
|---|---|---|---|
| **breather** | 1 interval | stops, sits, drinks, binds a scrape | no conflict in progress; not Dying |
| **short rest** `rest_short` | 1 hour | sits or lies down, eats, tends gear and wounds | a place to stop; no travel, labor or rolled beats beyond the allowance of 07.8.3 |
| **long rest** `rest_long` | 1 watch, of which at least 4 hours asleep; at most one a day, and none begins until two watches have ended since the last one completed (00.7.2) [revision: I-078] | sleeps | a rest site (07.8.2); not Dying |

A rest is declared as a free activity (00.12.6): it never rolls. The DM calls `advance_time` for its
duration in the current time mode, every boundary inside it runs (10's interval and watch checks, clock
ticks, afflictions), and when the duration has been served this chapter marks the event boundary
(`breather`, `rest_short`, `rest_long`) with the payload `{quality, site, treated}` (PR-07-8). Because
quality is computed when the boundary is marked, every handler on it reads the same value whatever
order the handlers run in; `h.07.rest_recovery` is registered to run before chapter 05's two rest
handlers (05's request), and nothing depends on that order.

**07.8.2 The rest site.**
```
### 07.8.2  Rest site                                             [D] [J:rung]
Trigger [T]:        a rest is declared
Loads in:           situation.rest.*
License check:      free activity (00.12.6)
Decisions (J):      1. SITE [J:rung], only when the place carries no `rest_site` fact (10 and 13
                       write it for known places; then this is a lookup):
                       HAVEN - a place where others keep the door: paid lodging in a settlement, a
                         guarded hold, a tended shrine, a friend's house. No encounter check runs.
                         typical: a room at the Ashford inn. boundary: the hayloft of a farm whose
                         farmer agreed to it (haven); the same loft entered unasked (camp).
                       CAMP - a made camp or a secured room: shelter or fire, a defensible spot,
                         nothing hostile known within reach. Checks run (10).
                         typical: a dry hollow off the road with a fire. boundary: a barricaded
                         cellar in a ruin whose danger clock is not imminent (camp); the same with
                         the clock imminent (rough).
                       ROUGH - no shelter and no fire, or inside a hostile site's active area, or on
                         the march: a ledge in the rain, a cell floor, the back of a cart.
                       Uncertain between two -> the worse.
Computation [D]:    the site feeds quality (07.8.4) and the recovery clocks (07.8.7): bed rest needs
                    a haven; a rough site caps quality at partial.
Stakes:             none
State writes:       place.rest_site (so the next rest here is a lookup)
Narration may not imply: safety the site does not have (a camp is checked; only a haven is not)
Worst case (J):     one rung: one quality step on one rest, or one day's bed-rest tick (class i).
Examples:           above. non-example: "We're careful, so call it a haven": care is a lever on
                    10's watch check, not a change of site.
Anchor:             no
Basis:              [R5 HR-05] [R: https://www.dndbeyond.com/srd (short and long rests)] [R6 B (West Marches: base and wilds)] [DL-07-11]
```

**07.8.3 What interrupts a rest.** `[D]` + `[T]` [DL-07-11; revision: I-065] An **interruption** is any of this closed list happening
to the rester before the duration is served (`harm.yaml#rests[].interrupted_by`):
1. a `conflict_start` in which the rester is a participant;
2. the rester takes harm of any amount, or a condition of S2 or heavier is applied to it;
3. the rester makes a rolled beat, uses an active ability, or performs labor or travel;
4. the rester is moved from the site against its will.

Talk, a free activity, being woken to a quiet word, keeping still while something passes: none of these
interrupts. When `advance_time` halts for an interrupting handler (00.7.8) the rest is suspended, not
broken, until one of the four happens in the scene that follows. A suspended or interrupted rest may be
**resumed** within an allowance, the lost time added to its end:

| Rest | Resumable when | Otherwise |
|---|---|---|
| breather | never: any interruption ends it | quality `interrupted` |
| short rest | one interruption lasting at most 1 interval | `interrupted` |
| long rest | one interruption lasting at most 1 hour, and at least 4 hours of sleep served in all | `interrupted` |

**07.8.4 Quality.** `[D]` [DL-07-11; revision: I-065] Computed at completion, first match (`harm.yaml#rests[].quality_rules`):
1. **`interrupted`**: the rest was broken beyond its allowance (07.8.3).
2. **`partial`**: any of: it was interrupted once and resumed; the site is rough; (long rest) the rester
   slept in medium or heavy armor (08); the rester had no food or no water this day (10's supply at 0);
   the rester was exposed to a weather hazard of S2 or more without shelter (10); the rester carries an
   affliction at stage 2 or higher; a haunt the rester carries says so (07.11.5).
3. **`full`**: none of the above.
The value is emitted on the boundary event. A rest's quality is shown to the player **before** the rest
is begun, as the best it can be given the present facts ("in mail, on a ledge, with no fire: at best a
partial rest"), so the cost of resting badly is known [R4 §9 07 item 4: rest effects as `[D]`].

**07.8.5 What a rest restores.** `[D]` [DL-07-12; C:I; revision: I-065] Handler `h.07.rest_recovery` (phase 3 of each rest boundary).
"Maximum" is the present maximum, after wound penalties (07.1.2).

**T-07-14 Vitality by rest.**

| Rest | `full` | `partial` | `interrupted` | Limit |
|---|---|---|---|---|
| breather | **+2** | +2 | 0 | the first **2** breathers between short rests restore Vitality; later ones restore 0 |
| short rest | **+ half of maximum, rounded up** | + a quarter of maximum, rounded up | +2 | the first **2** short rests of a day restore this much; later ones restore as a breather |
| long rest | **to maximum** | to three quarters of maximum, rounded up (never lowering current) | as a partial short rest | one a day, two watches apart (00.7.2) [revision: I-078] |

The sizes and limits mirror chapter 05's Focus table (05.6.9) on purpose: the body and the well refill
in the same three sizes, so the choice of when to stop is one choice [DL-07-12]. Also at completion:

| Also restored | breather | short rest | long rest |
|---|---|---|---|
| wound load | cleared | cleared | cleared |
| Light wounds (S1) | healed | healed | healed |
| Moderate wounds (S2) | only if treated during it (07.8.8) | only if treated during it | healed (full or partial) |
| `cond.exhausted` | — | — | −1 stack (full or partial); −2 at full quality in a haven; none while its cause continues (07.8.10) |
| dread | — | — | −1 at full quality (07.11.7) |
| recovery clocks (Heavy and worse, brink) | — | — | sets `rested_today` (full or partial); the tick lands at the `day` boundary (07.8.7) |
| afflictions | — | — | at full quality the next stage check holds a Precision lever (07.9.4) |

A Staggered character whose Vitality a rest raises above 0 is active again; its wounds remain.
*Why Vitality comes back fast and wounds slowly:* Vitality is wind and luck, which a night restores;
a broken arm is a broken arm. Attrition across a day lives in wounds, brink, exhaustion, dread, Focus,
supply, and above all in the time every rest spends [R6 C-08; R: https://cairnrpg.com/second-edition/wardens-guide/combat/].

**07.8.6 How wounds heal.** `[D]` [DL-07-13; revision: I-065] By severity (07.2.5): Light and Moderate wounds heal at rests as
T-07-14's second table says. Every wound of S3 or heavier, and each brink wound, has a **recovery
clock** (kind `project`, public, named for the wound; `harm.yaml#clock_templates`): Heavy and brink **4**
segments, Grievous **6**, Catastrophic **12**. A Catastrophic wound's clock does not exist until it has
been operated on (07.8.8); unoperated for 7 days it becomes a maim (07.7.4). Brink wounds heal one at a
time, the oldest first.

**07.8.7 The daily tick.** `[D]` [DL-07-13; revision: I-065] Handler `h.07.natural_recovery` (`day`, phase 3) ticks every recovery
clock from three flags set during the day that just ended:

**T-07-15 Recovery ticks per day.**

| Flag (true when) | Heavy (4) and brink (4) | Grievous (6) | Catastrophic (12, after surgery) |
|---|---|---|---|
| `rested_today`: a long rest of partial or full quality completed | +1 | 0 | 0 |
| `treated_today`: a Treat that delivered reach 1 or more covered this wound (07.8.8) | +1 | +1 | +1 |
| `bed_rest_today`: the whole day in a haven with no venture, travel, conflict or labor | +1 | +1 | +1 |
| **Days to heal:** on the road, untreated | 4 | never | never |
| on the road, treated daily | 2 | 6 | 12 |
| in a haven, bed rest and treated | 2 | 3 | 6 |

When a clock completes the wound is removed, its carrier condition ends, `h.07.vitality_max` runs, and
a wound of S4 or S5 leaves its scar (07.7.2). A Grievous wound that has gained no tick for 7 days
exposes its bearer to `aff.wound_rot` (07.9.8). *What this adds up to* (07-harm-sim section G, survivors
of Dying, who carry 2.9 wounds on average and a brink wound): back to full in a median of **2 days** in a
haven with a healer (3 at the 90th percentile), **2 days** on the road with daily treatment (6 at the
90th), **4 days** on the road with none (8 at the 90th), and 13 in 100 carry a wound that will not heal
without care at all.

**07.8.8 Treat.**
```
### 07.8.8  Treat: tend a wound, a sickness or the dying          [D] [J:enum] [J:flag]
Trigger [T]:        a beat whose intent is to mend, tend, doctor, set, stitch, purge or nurse a being
Loads in:           situation.rest.*, situation.downtime.recovery, situation.conflict.* (first aid only)
License check:      lic.training.lore_medicine (trained or better; 05) for everything below.
                    Without it: G3, redirected to the license's crude fallback: verb.handle "first
                    aid: stabilize only" (stabilize the Dying against its stabilize DC, 07.2.7; staunch
                    cond.bleeding), reach capped Limited; acquisition paths per the license.
Decisions (J):      1. WHAT [J:enum]: wounds | an affliction | the Dying (first aid). One per beat.
                       Default: wounds.
                    2. KIT [J:flag]: "Does the tender hold a healer's kit (item.tool.kit, 08) with a
                       use left?" True -> one Precision lever, engine-cited; one use is spent.
Computation [D]:    attribute Intellect (Agility for first aid in a conflict); competence on
                    deed.lore.medicine. DC, by tier: the worst wound treated: Moderate wound EASY,
                    Heavy MODERATE, Grievous HARD, Catastrophic (SURGERY) VERY HARD, which the
                    license admits only at grade expert or better; an affliction: its virulence
                    tier; the Dying: the stabilize DC. Time: 1 interval a patient; surgery 1 hour;
                    first aid 1 action. One Treat beat for each wound (and each affliction) a day,
                    by anyone: a beat may frame only wounds that are neither `treated_today` nor
                    closed, and a failed Treat closes every wound it framed for the day, whoever
                    would tend it next (01.4.2) [revision: I-078]. First aid on the Dying is
                    07.2.7's, retried each round (Edge cases). Treating oneself: an
                    engine-applied Precision snag; never surgery; never while Dying.
                    REACH LADDER, wounds: 1 the worst wound is `treated_today`; 2 every wound at or
                    below the framed tier is `treated_today`, Moderate wounds heal now, bleeding
                    ends; 3 as 2, and each of those recovery clocks gains 1 tick now; 4 as 3, and
                    the patient's next dying or stage check holds a Precision lever.
                    Surgery, reach 1 or more: the Catastrophic wound's clock is created (and the
                    reach ladder above applies from 2).
                    REACH LADDER, an affliction: 1-2 the patient's next stage check holds a
                    Precision lever; 3-4 that, and the affliction falls one stage now.
Stakes:             SAFE for Moderate and Heavy wounds and for afflictions. RISKY for Grievous
                    wounds and surgery: on a failure the threatened cost is cost.harm to the patient
                    (S2: 3 Vitality, lethal: false, no reduction); alternate cost.time (the day's
                    treatment is lost and the hour is spent). A critical failure at surgery (S3):
                    cost.closed_door: this tender may not operate on this wound again.
State writes:       treated_today per wound; treat_closed_today per wound a failed beat framed; healed wounds; clock ticks; the lever fact; kit use;
                    time; evidence on deed.lore.medicine (03).
Narration may not imply: a wound healed that the reach did not heal; Vitality restored (Treat
                    restores none); a maim or mark undone.
Worst case (J):     WHAT misread: the beat tends wounds when the player meant the fever: one
                    interval, re-declared (class iv). KIT wrongly true: +2 on one roll (class i).
Examples:           inside: a hedge-healer (Intellect +2, medicine +3) tends Wren's cracked ribs
                    (Heavy -> Moderate, DC 15) with a kit: +7, needs 8: 65%. Reach 2: treated today.
                    boundary: the same healer and Wren's frost-dead hand (Grievous -> Hard, DC 20):
                    needs 13 (40%), Risky. Trained grade admits Hard: legal.
                    outside: a Catastrophic wound needs surgery at Very hard, which the trained
                    grade does not admit (05's license text): G3 for this healer; the redirect names
                    who could (an expert: the Ashford barber-surgeon).
                    non-example: "I bandage myself back to full": Treat restores no Vitality; a
                    breather does (+2), and ab.field_surgeon does (3, inside 05's healing cap).
Anchor:             yes. Intent verbs: tend, treat, doctor, bandage, set (a bone), stitch, nurse,
                    purge, draw (a poison). Knobs: dc (wound tier -> virulence tier -> an animal or
                    creature's wound one tier harder); time_cost (interval -> hour for surgery ->
                    a day's nursing in downtime, which sets bed_rest_today as well); targets (one ->
                    several patients at an interval each); stakes (Safe -> Risky).
Basis:              [R5 HR-05, HR-09] [R: https://2e.aonprd.com/Rules.aspx?ID=2319 (treat wounds)] [R: https://bladesinthedark.com/consequences-harm (a recovery clock ticked by treatment)] [05 lic.training.lore_medicine] [DL-07-13]
```

**07.8.9 Healing magic and its edge with this chapter.** `[D]` [DL-05-23; R5 HR-09; revision: I-065] Magical healing restores Vitality and
cleanses conditions (05.7.8), under 05's cap of two Vitality-restoring effects per being between its
long rests. Against this chapter's state: (a) it never removes a wound, a brink wound, a mark or a
stage of an affliction unless the effect names it by id; (b) it stabilizes the Dying at once (07.2.7);
(c) it does not clear the wound load; (d) **Treat restores no Vitality and is therefore outside the
cap**, as are rest and natural recovery; an ability that restores Vitality by mundane means
(`ab.field_surgeon`) is inside it, as 05 assumed; (e) "one recovery step" in `rit.vigil_of_healing`
means **7 ticks** on one wound's recovery clock, and for a Catastrophic wound it also counts as the
surgery; the rite's long rest counts as full quality and treated.

**07.8.10 Sleep, exertion and want.** `[D]` + `[T]` [DL-07-21; R5 HR-07; revision: I-065] Handler `h.07.fatigue` (`watch`, phase 4) keeps
`watches_awake`: watches ended since the last long rest of partial or full quality (an interrupted long
rest sets it to 2). It applies to an ally who keeps more than two watches a day in a journey role
(16.8.3) as to the PC [integration: IR ch.16 to 07 (c)].

| `watches_awake` at the end of a watch | Effect |
|---|---|
| 4 (a day and a night without sleep) | +1 stack of `cond.exhausted` |
| 6 | +1 stack |
| 8 | +1 stack (three: also `cond.slowed`, 06) |
| each watch beyond 8 | S2 harm (3), `lethal: false`, no reduction; at 0 Vitality the character goes **Down**: it sleeps where it drops (a long rest of at best partial quality begins) |

- **Pushing on.** When a stack is about to be applied for want of sleep or a forced march (10), the
  player may declare an Endure beat with Endurance ("keep going", 01.18.15) against Moderate (Hard with
  one stack held, Very hard with two): the stack is deferred by as many watches as the delivered reach.
- **Want.** Chapter 10's supply handler applies one stack for each day without food or water
  (`h.10.supply`). With three stacks held and the want continuing, the `deprivation` warning fires
  (07.3.3); each stack that would then be applied is instead S3 harm (5), no reduction, lethal once the
  warning is effective. Starving is slow, telegraphed, and real.
- `cond.exhausted` is confirmed as 06 defined it: stacking `intensify`, 3 stacks, −1 per stack on all
  checks (the status family's worst-only rule applies), `cond.slowed` at three, removed as T-07-14 says.
  Chapter 05's overdraw adds stacks to the same condition (05.6.6), so a caster who overdraws and a
  traveler who does not sleep meet in the same place.

**07.8.11 Downtime.** `[D]` [DL-07-13; R5 HR-05; revision: I-065] In `downtime` mode chapter 15 owns the activity list; this chapter defines
what its recovery activity does. **Convalesce** (one day or more, in a haven): each day sets
`bed_rest_today`, and `treated_today` if a tender with the license is present (no roll is needed for
ordinary nursing in downtime: the day counts as a Treat at reach 1); removes one stack of
`cond.exhausted`; and a full week of it sets dread to 0 (07.11.7) and counts as `eff.07.affliction_shift`
of one stage against any disease. A week of convalescence therefore heals every Heavy wound, a brink
of up to three, and a Grievous wound; a Catastrophic one takes six days after surgery. Every day of it
runs the world (00.7.7).

**07.8.12 Rest is paid for in time.** `[D]` No rule restores anything without spending an interval, an
hour or a watch, and `advance_time` never skips (INV-15): a breather in a site is one site check (10);
a short rest is six; a long rest in camp is a watch check and a tick of every clock that listens to
time; a week in bed is a World Turn (11). The DM does not decide whether resting is "safe enough to
allow"; the clocks do [R1 §07 "recovery has to be tied to elapsed time"].

### 07.9 Afflictions: poison, disease and curses

**07.9.1 What an affliction is.** `[D]` An affliction is a staged condition sequence
(`data/afflictions.yaml`; R5 HR-08, G-8). It has a **kind** (`poison`, `disease`, `curse`), a
**virulence** (a DC tier), an **onset** (a duration before stage 1), a **cadence** (the boundary at which
its stage check falls), an ordered list of **stages**, and its **cures**. Each stage applies one carrier
condition at a stated severity (`cond.poisoned`, 06; `cond.diseased`, `cond.cursed`, this chapter's
owner-block) and may add harm at each check and other effect references. An entity holds at most one
instance of any affliction id (INV-13). The staged shape is Pathfinder's, described here in this
ruleset's terms [R: https://2e.aonprd.com/Rules.aspx?ID=2319; R5 HR-08].

**07.9.2 Exposure.** `[D]` [DL-07-17; R5 HR-08; revision: I-065] An exposure is a resisted check forced by `eff.force_check` with the
affliction as its degree table (00.3.3: the target rolls; the DC is the virulence tier): Endure with
Endurance for poisons and diseases, with Resolve for curses.

| Degree | Result |
|---|---|
| critical success | not afflicted, and **inured**: no further exposure from this source this scene |
| success | not afflicted |
| failure (including by 3 or less) | afflicted: stage 1 begins when the onset has passed |
| critical failure | afflicted: stage 2 begins when the onset has passed |

Exposures come from: an attack's rider (a bite, a coated blade: 09, 08); eating, drinking or breathing
the thing; a hazard or place (10); close contact with a bearer of a contagious disease (one exposure a
day); a curse laid by a rite, a power or a broken bargain (05, 09, 07.5.5). A **second exposure** to an
affliction already carried adds no instance; it forces one extra stage check at once. An adversary's
exposure is an engine fortune check (01.6.7); a mob rolls once.

**07.9.3 Stage checks.** `[D]` [DL-07-17; C:P8; revision: I-065] At each cadence boundary the bearer makes a **stage check**: the same
check as the exposure, with no status penalty from the affliction's own carrier or from wounds, and
with any engine-cited levers earned by treatment (07.8.8), a full-quality long rest (T-07-14) or a
remedy.

| Degree | The affliction… |
|---|---|
| critical success | falls two stages |
| success | falls one stage |
| failure by 3 or less | holds |
| failure | rises one stage |
| critical failure | rises two stages |

At stage 0 it is **cured** and its carrier ends. A rise past the last stage holds at the last stage and
applies the entry's `terminal` effect at each check. An entry with `max_checks` **runs its course**:
after that many checks it ends at whatever stage it has reached. Cadences and their handlers: `round`
(at the bearer's `turn_end`, through the carrier's periodic entry, 06.1.8); `interval`
(`h.07.affliction_onset`, phase 2); `day` (`h.07.affliction_day`, phase 2); `week` (`h.07.curse_cycle`,
phase 2); `trigger` (a named event in the entry). `advance_time` runs every check a skipped span
crosses (INV-15), which is how "three days later the fever has broken, or has not" is computed rather
than narrated.

**07.9.4 What a stage does.** `[D]` [DL-07-17; revision: I-065] A stage's effects are data: its carrier condition at the stage's
severity (06 gives `cond.poisoned` −1 / −2 / −3 on all checks at S1 / S2–S3 / S4–S5; the two carriers
added here use the same numbers); **stage harm** applied at each stage check through `apply_harm`
(`no_reduction: true`, `periodic: true`, lethality by 07.9.5); and listed effect references (a
condition such as `cond.slowed`, a cap on rest quality, a lowered maximum Vitality, dread).

**07.9.5 Afflictions that can kill.** `[D]` + `[T]` [DL-07-17; revision: I-065] An entry marked `lethal: true` names a `warn_stage`.
When the bearer reaches it, the `affliction` warning fires (07.3.3) in plain words, with what would stop
it (its cures). From the moment that warning is effective, the affliction's stage harm is lethal. An
affliction with `lethal: false`, and any lethal one before its warning, can lower Vitality, Stagger and
put its bearer Down, and no more (07.2.11). So a poison's road to the Threshold is: warned at the warn
stage, harmed to Staggered, loaded by stage harm (which is periodic: load and no wound records) to
Dying, then dying checks. It takes several checks, and every one is a chance to be treated.

**07.9.6 Cures.** `[D]` [DL-07-17; revision: I-065] Each entry lists its cures; these are the kinds:
- **Treat** (07.8.8): a lever on the next stage check, or a stage down.
- **A remedy** (an `item.consumable.remedy`, 08, carrying `eff.07.affliction_shift`): a **specific**
  remedy named for the affliction or its family lowers it two stages; a **general** one (an antidote, a
  febrifuge) lowers a poison or disease one stage. One remedy per stage check period.
- **Cleansing magic.** `eff.cleanse` naming `cond.poisoned` ends a poison at stage 2 or lower and lowers
  a higher one by two stages (this is what `ab.breath_of_life`'s "freed of poisoning" does). It does
  nothing to a disease or curse unless the ability names that carrier.
- **Running its course** (`max_checks`), for poisons the body burns off.
- **A lift** (curses, 07.9.7).

**07.9.7 Curses.** `[D]` [DL-07-17; revision: I-065] A curse is an affliction of kind `curse`: its checks use Resolve; its cadence is
`week` or a named trigger; medicine does not touch it. Every curse entry carries a **`lift`**: a deed or
fact that ends it outright (return the thing; be forgiven by the one who laid it; keep the broken vow;
bathe at a named kind of place), which is sealed until learned and has at least three clue placements
by chapter 15's rule. `eff.05.end_working` against the curse's virulence tier lowers it one stage; only
the lift, or stage 0 by checks, ends it. `aff.deaths_debt` is the exception to the checks: it has none,
and moves only when its countdown completes (07.5.5). Curses laid by `rit.lay_curse` and the draught of
`ab.slow_draught` use entries in this file (05's request).

**07.9.8 Diseases.** `[D]` [DL-07-17; revision: I-065] A disease is an affliction of kind `disease` on a `day` cadence. An entry
marked `contagious` exposes those in close contact once a day. `aff.wound_rot` is the disease of
neglected wounds (07.8.7): while it holds, the wound's recovery clock does not tick. At stage 2 or
higher any disease caps rest quality at partial (07.8.4).

**07.9.9 Poison as a tool.** `[D]` [DL-07-17; C:VII; revision: I-065] A PC who coats a blade or doses a cup uses a license of
`deed.guile.poisoncraft` (05; crude fallback: Handle, with a risk of self-exposure on a critical
failure). The poison rides the Strike or the meal as a rider: on a hit that deals harm of 1 or more
(or on consumption) the target is exposed (07.9.2). What an afflicted adversary suffers is the entry's
stages; chapter 03 records the method.

### 07.10 Harm from hazards

**07.10.1 Consuming a hazard.** `[D]` [DL-07-14; revision: I-065] Chapter 10 owns hazard entries (`data/hazards.yaml`: severity, harm
tags, resist, cadence, conditions, omens, `lethal_context`; 00.17.1 Q18) and decides when an exposure
happens. This chapter owns what the exposure does:
1. The exposed character makes the entry's resisted check (Endure or Evade; the effect DC is the tier
   matching the severity unless the entry lists one, 00.3.8). The result reads 01.18.3's table unless
   the entry has its own: critical success — no effect and a follow-up lever; success — no effect;
   failure by 3 or less — no effect and one cost of another kind; failure — the hazard at its severity;
   critical failure — one rung heavier.
2. `eff.hazard_step` effects the character holds lower the severity first (00.10.4 step E2).
3. `apply_harm(target, severity, the entry's harm tags, source {hazard}, lethal per 07.3.6,
   no_reduction per 07.2.2, periodic: true when the exposure is one tick of a continuing hazard)`, then
   the entry's conditions.
A hazard's first exposure in a scene is a harm event with a wound record if the character is Staggered;
its continuing ticks are periodic.

**07.10.2 Rating an unlisted hazard.**
```
### 07.10.2  Hazard severity                                      [J:rung] [D]
Trigger [T]:        a source of harm with no data entry is about to harm someone (a thing the player
                    or the scene improvised: a toppled brazier, a hive, a millrace)
Loads in:           situation.exploration.*, situation.conflict.*
License check:      none
Decisions (J):      1. SEVERITY [J:rung], by what it would do to an unprotected adult (T-07-17):
                       S1 LIGHT - stings and scrapes: nettles, a slap of hot wax, a tumble of a few
                         feet. boundary: a short fall onto stone (S1) / a 10-ft fall (S2).
                       S2 MODERATE - a real setback: a 10-ft fall, a campfire's flames, a kick from
                         a horse, a minute in freezing water. boundary: a burning brand (S2) / a
                         burning room (S3).
                       S3 HEAVY - a serious blow: a 20-ft fall, a burning room, a river in spate, a
                         night in a blizzard without shelter. boundary: a rockfall at its edge (S3)
                         / under it (S4).
                       S4 GRIEVOUS - could end a life: a 40-ft fall, a collapsing roof, a lightning
                         strike, boiling oil. boundary: a 40-ft fall (S4) / an 80-ft fall (S5).
                       S5 CATASTROPHIC - lethal to most: an 80-ft fall, the heart of a great fire,
                         a falling gate, a flow of molten rock.
                       Uncertain between two -> the lighter, unless a recorded fact gives the
                       measure (a height in feet, a named fire).
Computation [D]:    harm = the rung's value (1 / 3 / 5 / 8 / 12); effect DC = the rung's tier; harm
                    tags by what it is; the rating is stored on the source as a fact (numbers are
                    stable, 00.2.6 #6). A rating of S4 or S5 raises the `severity` warning (07.3.3)
                    when the source is perceived.
Stakes:             the rung is the stakes of resisting it (01.18.3: S1-S2 Risky, S3+ Dire)
State writes:       the source's stored severity; the lethal context if warned
Narration may not imply: harm of another rung; death from a source whose warning was not shown
Worst case (J):     one rung: 2-4 Vitality (class i). Rating a Grievous source Heavy also withholds
                    its warning, so it cannot be lethal this time (errs safe, class iv).
Examples:           in the table. non-example: "The poison needle trap is Catastrophic because
                    it's a deadly trap": the needle's harm is Light; what the poison does is the
                    affliction's stages (07.9).
Anchor:             yes. Intent verbs: (a harm source with no entry) burn, crush, drown, freeze,
                    fall, scald, bury. Knobs: harm_severity; harm_tags; dc (tier by rung -> a
                    listed effect DC); duration (one exposure -> a cadence, 10).
Basis:              [00.3.11] [06.5.8] [01.6.9] [R5 EX (hazards)] [DL-07-14]
```

**07.10.3 Falling.** `[D]` [DL-07-14; revision: I-065] Falls use 06.5.8's heights: 10 ft S2, 20 ft S3, 40 ft S4, 80 ft or more S5,
`harm.physical.crush`, no reduction. A height of 40 ft or more beside or beneath the PC is a `severity`
source: the warning is due when it is perceived, which is why a chasm described with its depth is a
fair lethal risk and one whose depth was never established is not (WE-07-2).

**07.10.4 Breath.** `[D]` [DL-07-14; revision: I-065] A character who cannot breathe (under water, in thick smoke, in a chokehold)
holds its breath for **6 rounds plus 2 per point of Endurance** (at least 2; in other time modes, one
interval is ample warning that it cannot). After that it carries `cond.choking` (06: −2 on all checks, 1
Vitality at each `turn_end`, no reduction) and at each `turn_end` makes an Endure check against Moderate,
then Hard, then Very hard, a tier harder each round: a failure adds a second point of harm that turn.
These ticks are periodic: at 0 Vitality each adds wound load, so a Staggered character out of air falls
within three turns, to Dying if the water or smoke was warned as lethal, else Down, to be found (or
not) by 07.6's `leave` row.

### 07.11 Dread: the strain on the mind

**07.11.1 The track.** `[D]` **Dread** is a shown quantity on every PC: `dread {current, threshold}`,
from 0 to the threshold. The **dread threshold** is the one value Resolve derives (00.4.4):

`threshold = 8 + Resolve + the deltas of marks and haunts`, never below 4.

Dread is the canonical name of this ruleset's mental strain. It is not 03's conduct *strain*, and not
the `harm.mind.strain` Vitality harm of an overdraw: neither of those moves it [DL-07-15].

**07.11.2 What adds dread.** `[T]` + `[D]` [DL-07-15; R5 HR-06; revision: I-065] Only these (T-07-19; `harm.yaml#dread.sources`):

| Source | How much |
|---|---|
| the PC enters Dying | +1, no check |
| the PC reaches the Threshold | +2, no check |
| a companion or bonded NPC dies in the PC's presence | a dread check at S3 |
| the first sight in a scene of an adversary whose template carries `dread: S<n>` (09: the walking dead at S1–S2, a horror at S3, a great fiend at S4) | a dread check at that severity |
| each week of captivity; a place or hazard tagged `harm.mind.strain` (10) on its cadence | a dread check at the listed severity (captivity: S2) |
| an effect that says so (`eff.07.dread`: an ability, a curse's stage, a rite's failure) | as the effect states |

A **dread check** is an Endure check with Resolve against the tier matching the severity (00.3.8):
critical success — no dread, and the character is **inured** to that source's kind until the season
ends (no further checks from it); success — none; failure — dread + U(severity) (1 / 1 / 2 / 3 / 4);
critical failure — dread + U of one rung heavier. Fear in the moment is a separate thing: `cond.frightened`
is a condition of the scene (06); dread is what stays.

**07.11.3 Shaken.** `[D]` [DL-07-15; revision: I-065] While dread is at or above half the threshold the character is **shaken**, a
shown descriptor: any `cond.frightened` applied to it is one rung heavier, to S3 at most. Nothing else
changes; the character acts as its player says.

**07.11.4 Breaking.** `[T]` + `[D]` When dread reaches the threshold the character **breaks**, at once:
the engine rolls an Endure check with Resolve against Hard (20).
- **Success or better — steeled.** Dread falls to half the threshold (rounded down); the character
  gains `cond.heartened` (S2) for the scene; nothing lasting is taken.
- **Otherwise — a haunt.** The engine draws three entries of `kind: haunt` from `injuries.yaml`, gated
  on the tags of what filled the track, and the player chooses one (C:P1). Dread returns to 0, and the
  character carries `cond.frightened` (S2) toward the breaking source for the scene.
Breaking never takes the character out of the player's hands and never harms the body
[R: https://darkestdungeon.wiki.gg/wiki/Stress (a test at the brim that can turn either way); R6 C-12].

**07.11.5 Haunts.** `[D]` [DL-07-15; revision: I-065] A haunt is a permanent mark (07.7.1) with one behavioral trigger written as an
effect, several with a small upside (T-07-13): night terrors (long rests outside a haven are at best
partial), a dread of one kind of thing (frightened S1 at first sight of it each scene), the shakes
(−1 status on `trait.action.manipulate` while shaken), cold (immune to frightened S1; −1 status on Talk
that comforts or befriends), flinching (−2 status on tempo checks), joyless (solace eases 1 less dread;
threshold +1), the stare (+1 edge on Talk that intimidates; −1 status on Talk that persuades), and
obsession (a thread toward the thing that broke it; dread +1 at each `week` in which the thread went
unpursued).

**07.11.6 The fourth break ends the career.** `[T]` + `[D]` A character may carry **three** haunts. If a
character carrying three breaks and is not steeled, it takes no fourth: the fact `career_end` is
written, the character finishes the scene, and at the next `scene_end` chapter 11's retirement
procedure runs with the ending the player picks from those 11 allows (the character lives, and is an
NPC of the world from then on). The codex shows haunts as *n of 3*, so the end is seen coming from the
first. A player may always retire sooner (11). Dread ends careers; it never ends lives
[R6 C-R7; R: https://bladesinthedark.com/consequences-harm (the fourth trauma retires); R: https://cubicle7games.com/en_US/blog/the-one-ring-the-shadow].

**07.11.7 Easing dread.** `[D]` [DL-07-15; revision: I-065] −1 at each long rest of full quality; −2 from a solace activity (15:
carousing, prayer, time with a bond); −2 when a thread is completed or a vow kept; to 0 after a full
week of downtime in a haven. Nothing else lowers it; marks and haunts are never removed.

### 07.12 Companions and other people

**07.12.1 A companion's ladder.** `[D]` A companion (16) has Vitality from its template (16.4.3: 6 / 12 / 16 /
18 / 20 by serving band, with size multipliers, always clamped below the PC's maximum; accepted by the
orchestrator) and no Staggered state [integration: IR ch.16 to 07 (b)]. At 0 Vitality:
- if the felling event was **not lethal** (07.3.6 applies to companions exactly as to the PC: Key 1
  protects them): the companion is **Down**: unconscious for the scene, defeated, alive;
- if it was **lethal**: the companion is **bleeding out**: defeated, helpless, and on the public
  countdown clock `clk.bleeding_out` (4 segments; +1 at each `round`; +1 for each further lethal harm
  event on it). Stabilizing it (first aid against Moderate, a kit as a lever; any Vitality-restoring
  effect) voids the clock. If the clock completes, the companion **dies**. There is no menu, no brink
  and no reprieve: a companion's second key is the clock running out [00.17.1 Q8; R6 C-11].
The clock is the scene's new objective, shown to the player the moment it starts: four rounds to reach
them, command another to tend them (06.14.2), carry them out, or end what is killing them. A **cohort**
(16.2.6) is one bleeder: every member felled by lethal harm shares one `clk.bleeding_out.<cohort>`, and one
stabilizing beat saves all of its fallen [integration: IR ch.16 to 07 (a)].

**07.12.2 After the fall.** `[D]` [DL-07-20; revision: I-065] A companion that was Down wakes at `scene_end` at Vitality 1 with a
Moderate body wound. One that was stabilized from bleeding out wakes after a long rest with a Heavy
body wound on a 4-segment recovery clock (ticked as T-07-15) and cannot be commanded to attack-trait
beats until it heals. Companions regain Vitality by rest as PCs do. They take no marks, hold no dread,
and carry at most one wound at a time (the worse replaces the other): their bookkeeping stays small.
Loyalty after a fall is 16's.

**07.12.3 Left behind, and lost.** `[D]` [DL-07-20; revision: I-065] A companion left Down or bleeding among enemies when the PC
leaves (07.4.4) follows the victor's disposition: `capture`, `ransom`, `rob` or `drag_to_lair` make it a
prisoner (a rescue lead is written); `drive_off` and `leave` leave it where it lies; `kill` with an
effective lethal context kills it, and without one leaves it for dead. When a companion dies the engine
writes `setback.companion_dead` (12.7.5), the PC makes a dread check at S3 (07.11.2), the opposing
morale clock ticks −1 (06.11.3), and the chronicle takes a line. Ch.16 adds what an ally's death leaves
behind (16.9.5: belongings, kin and debts, the vow offered, the others' grief) [integration: IR ch.16 to 07 (e)].

**07.12.4 Mounts, servants and allies.** `[D]` [DL-07-20; revision: I-065] A mount is a companion for this chapter (06.15.3 says what
its fall does to the rider). A summoned servant, a raised corpse or an automaton (05) has no ladder: at 0
Vitality it ends, as its working says. An allied NPC who is not a companion follows 07.2.10 by depth.

---

## Procedures

**PR-07-1 `apply_harm`.** `[D]` (called by PR-06-3 step 5, `apply_costs` for `cost.harm`, periodic handlers,
hazard exposures, affliction stages, 05.6.6)
1. **Event.** Create the harm event with its depth (00.10.8). At depth 0, resolve the target's `prevent`
   and `redirect` subscribers first (PR-00-6); a prevented event ends here.
2. **Lethal test.** Set `lethal` true only if 07.3.6's three tests hold now (for a periodic event, re-test
   the inherited context, 07.2.11). Otherwise false, and log `lethal_refused` with the missing test.
3. **Amount.** If `dealt` is given, start from it; else convert the severity (after any `eff.hazard_step`)
   to 1 / 3 / 5 / 8 / 12. Receiver's side (00.10.5): subtract reduction by harm tag, capped at 4, unless
   `no_reduction`; apply at most one ×½ and one ×2; clamp at 0; round down.
4. **Zero.** If the amount is 0: return `{amount: 0}`. The attack still hit (06.4.6); nothing below runs.
5. **Target not a PC or companion.** Subtract from Vitality; at 0 → 07.2.10 (mode and depth). Return.
6. **Active** (Vitality > 0). Vitality := max(0, Vitality − amount). Fire `on_harm_taken`. If the half
   line was crossed: `on_vitality_threshold(half)`. If Vitality is now 0: harm state := Staggered; discard
   the excess; `on_vitality_threshold(zero)`; morale −2 (06.11.3); raise `trg.exits`. A `mode: nonlethal`
   attack that brought a PC to 0 puts it Down at once instead (06.4.8; 07.2.9). Return.
7. **Staggered.** Bucket the amount (07.2.4). `wound_load += U(bucket)`. If not periodic: PR-07-2 creates
   the wound. If `wound_load ≥ 3`: lethal → `harm_state := dying`, `dying_step := min(3, 1 + brink)`,
   `cond.prone`, `on_dying`, dread +1, `setback.dying_entered`, raise `trg.exits`, and every non-`kill`
   opposing side stops attacking the PC (07.6.1); not lethal → Down (07.2.9), `setback.defeated`. Return.
8. **Dying.** If lethal: `dying_step += 1` (bucket S4 or S5: 2); if not periodic, PR-07-2. If the step
   would be 4 or more: hold it at 3 and open the Threshold (PR-07-5). If not lethal: record and discard.
9. **Down or dead.** Record and discard.
10. **Return** `{amount, breakdown, wound, load, transition, obligations}`. Obligations: the new
    descriptor word (07.1.1), the wound's name if one was made, the `[STATUS]` block if `trg.exits` was
    raised. Chapter 12's claim check holds the narration to them.

**PR-07-2 Making a wound.** `[D]`
1. Family: the first harm tag of the event, matched by cascade to one of `cut`, `pierce`, `crush`, `fire`,
   `frost`, `storm`, `corrosion`, `blight`, `radiance`, `arcane`. (An event tagged only `harm.venom`,
   `harm.mind` or `harm.physical.asphyxia` is internal: it must have been `periodic`; if it was not, it
   is treated as periodic and logged.)
2. Site: the called shot's; else the attack's listed site; else `roll_table(tbl.wound_site)`. S1 has no
   site.
3. Entry: `inj.w.<family>.<site>.<severity>` (S1: `inj.w.<family>.light`). Write the instance to
   `wounds` with `{entry, severity, site, taken_at, frame_id, source}`.
4. Apply the entry's effects: the site's carrier condition at this severity (PR-00-5; `replace_stronger`),
   and for S3 or heavier `eff.07.vitality_max_penalty`; run `h.07.vitality_max`.
5. For S3 or S4 create the recovery clock (07.8.6). For S5 record `needs_surgery` and the day count.
6. Return the wound's name for narration.

**PR-07-3 A Dying character's turn.** `[D]`
1. `turn_start`: the status block shows the step, the number needed on the die and the odds.
2. The player declares at most one action (07.2.7) and any free activity, Yield included.
3. `turn_end` (`h.07.dying_check`): roll the dying check against the step's stabilize DC; offer the fate
   reroll; apply the table. Stabilized → PR-07-3a. Past 3 → PR-07-5.
- **PR-07-3a Stabilizing.** `dying_step := 0`; harm state Staggered (or active if Vitality > 0); add one
  `inj.the_brink` with its clock unless the stabilizing effect says no brink wound; `on_stabilize`.

**PR-07-4 Delivering a warning.** `[T]` + `[N]`
1. `get_active_triggers` returns `trg.lethal_warning {source, cause}` (or `trg.danger_notice`).
2. The engine supplies the sign: the source's first unused tell or omen; for a height or a hazard, its
   recorded measure.
3. The DM narrates the sign in this turn's fiction and appends the `[WARNING]` block with the cause line,
   current fate, and the exits computed by 07.4.1 and 07.4.3.
4. `set_fact(lethal_context {…, shown: true, warned_at, effective_from: the beat counter after the
   player's next declaration or turn})`. A danger notice writes nothing.
5. If the draft narration lacks the sign or the block, the claim check fails the turn (12.3).

**PR-07-5 The Threshold.** `[D]` + `[J:flag]`
1. Pause the conflict. Dread +2. `setback.threshold`.
2. For each option of `last_chance.yaml` in order: evaluate `requires`. Compute its price from state: the
   victor and holding place (1); the maim entry and attribute (2); the bargainer and its ask (3); the
   victor's taking and the waking place (4); the clock and ticks (5); `fate_cost` (6); the Gamble's odds
   from the character's Endure modifier (8).
3. The DM may strike survivors, each strike citing a fact on that option's `struck_when` list.
4. Validate: at least three remain and at least one is not death; otherwise the last strike is refused.
5. Show `[CHOICE]` (T-07-7). Wait. No default.
6. Apply the chosen option's `outcome` and `world_writes`; brink wound and mark as the option says
   (07.7.3: draw three, the player picks, or the plain mark); clear the wound load; `chronicle_append`.
7. Options 2 and 6: the conflict resumes at the point it paused, the PC standing. Option 7: PR of 07.5.9,
   then `harm_state.dead`. Option 8: frame the Gamble as a lethal frame, OFFER, confirm, roll, apply.
   Others: the conflict ends for the PC; PR-07-7 runs where the option says.

**PR-07-6 Retreat.** `[D]` + `[J:flag]`
1. Legal? (07.4.3 license line.) Route? (decision 1; the Oracle if unestablished.)
2. Pursuit test over every hostile participant (ABLE includes a way to follow: no shut `barrier` between,
   [revision: I-076]). None willing and able → clean. Else → the player picks a
   chase or a rout; for a rout the engine lists clock candidates and the DM picks (decision 2).
3. Compute the price: parting blow (severity, after armor), left behind, world cost. Show it. On commit:
   apply in that order; move the PC; mark the PC's `conflict_end`; write the setback fact for a rout.

**PR-07-7 Running a defeat disposition.** `[D]` + `[J:enum]`
1. Pick the side (07.6.1) and its row of T-07-11, and the column (defeated or yielded).
2. If the PC is Dying: apply the row's "if Dying" cell (stabilize, or run the dying checks out by PR-07-3
   with no actions declared; at the Threshold → PR-07-5).
3. Capture, ransom, drag_to_lair: choose the holding place (07.6.3); `advance_time` for the journey
   (every boundary runs; halt on interrupts as usual); move the PC; apply bonds unless `parole`; move
   items to a cache (07.6.4), honoring `keep_one_thing`; create `clk.captors_intent` or `clk.larder`;
   draw three openings and write each as an entity or fact; open `thr.captivity` with its racing clock.
4. Rob: build the cache by the row; leave the PC; advance one interval. Drive off, leave: move or leave
   the PC; write `barred_to_pc`; advance one interval.
5. Kill without Key 1: `lc.left_for_dead`'s writes without brink wound or mark; the belief `pc.dead`.
6. Always: `victory_over_pc`; the reputation packet; the setback fact; the chronicle line.
7. **Lead check:** at least one actionable lead exists in state (an opening, a cache place, a sensed
   clock, a named NPC). If not, add the first unused row of `tbl.captivity_openings` that fits, or a
   rumor of the cache. Then frame the next scene at the first moment the PC can act.

**PR-07-8 Completing a rest.** `[D]`
1. On declaration: read or classify the site (07.8.2); compute and show the best quality possible.
2. `advance_time(the rest's duration)`. On an interrupt: suspend; if an interruption of 07.8.3 occurs,
   apply the allowance; resume or end.
3. At completion compute quality (07.8.4) and `mark_boundary(<rest>, {quality, site, treated})`.
4. `h.07.rest_recovery`: T-07-14 (Vitality, then the second table); then chapter 05's handlers.
5. Narrate from the handler results only (PR-00-2 step 5).

**PR-07-9 An affliction's stage check.** `[D]`
1. For each affliction instance whose cadence is this boundary and whose onset has passed: if it has no
   checks (`aff.deaths_debt`), skip to 4.
2. Assemble the check (07.9.3): attribute, competence, edge; engine-cited levers from treatment, rest or
   remedy; no status from its carrier or from wounds. Roll; offer the fate reroll; read the table.
3. Move the stage; at 0 cure it; past the last stage hold and apply `terminal`; count `max_checks`.
4. Apply the stage: carrier severity; stage harm through PR-07-1 (`periodic`, `no_reduction`, lethal by
   07.9.5); listed effects. If the stage is the `warn_stage`: raise `trg.lethal_warning(affliction)`.
5. Return the stage's text for narration and the codex line (stage n of m, next check when).

**PR-07-10 The daily recovery pass.** `[D]` (`h.07.natural_recovery`, `day`, phase 3)
1. For each recovery clock: ticks by T-07-15 from the three flags; `tick_clock`.
2. Completed clocks: remove the wound and its carrier; write the scar (S4, S5); recompute the maximum.
3. Catastrophic and unoperated for 7 days → replace it with the site's maim (07.7.4). Grievous with no
   tick for 7 days → an exposure to `aff.wound_rot`.
4. Clear `rested_today`, `treated_today`, `treat_closed_today`, `bed_rest_today`.

**PR-07-11 Dread.** `[D]`
1. On a source of T-07-19: add the flat amount, or run the dread check and add by its table.
2. Recompute shaken. If `dread ≥ threshold`: the resolve test (07.11.4). Steeled → set dread, apply
   heartened. Else: if the character carries three haunts → `career_end`; otherwise draw three haunts,
   the player picks, write it, dread := 0, frightened S2 toward the source.
3. `chronicle_append` on a haunt or a career's end.

**PR-07-12 A companion at 0 Vitality.** `[D]`
1. Lethal event? No → Down. Yes → `create_clock(clk.bleeding_out)`; show it.
2. Each `round`: +1. Each lethal harm event on it: +1. Stabilized: void the clock.
3. On completion: dead; 07.12.3's writes.

---

## Tables

Tables embedded in Rules are canonical and indexed here: **T-07-1** harm states (07.1.3); **T-07-2** wound
severity and load (07.2.4); **T-07-3** the dying check (07.2.7); **T-07-5** lethal-warning causes (07.3.3);
**T-07-6** the two keys (07.3.1); **T-07-9** Retreat's price (07.4.3); **T-07-10** the nine options (07.5.2);
**T-07-11** dispositions (07.6.1); **T-07-12** captivity openings (`harm.yaml#tables`, 07.6.3); **T-07-14**
Vitality by rest (07.8.5); **T-07-15** recovery ticks (07.8.7); **T-07-17** hazard severity (07.10.2);
**T-07-19** dread sources (07.11.2). The tables below are defined here. Data is canonical for numbers and
ids (00.1.4 line 5): `data/harm.yaml`, `data/injuries.yaml`, `data/afflictions.yaml`, `data/last_chance.yaml`.

**T-07-4 Wounds by site and severity** (carriers in `data/conditions.yaml owner-block 07`; names by harm family in
`data/injuries.yaml`, 170 entries). Status penalties are family `status`: only the worst applies to a roll.

| Site (d12) | Penalized checks | S2 Moderate | S3 Heavy | S4 Grievous | S5 Catastrophic |
|---|---|---|---|---|---|
| **arm** (1–3) | attack- and manipulate-trait beats with that arm; Grapple; Might-based Force and Exert | −1 | −2; no `heavy` weapon or bow | −2; that hand holds nothing (no shield, second weapon or two-handed method) | −3; and no climbing or swimming without help |
| **leg** (4–6) | Move; Evade; Exert and Sneak carried by the legs | −1 | −2; pace −1 | −2; pace −1; no jumping or running | −3; cannot stand unsupported; one band a turn |
| **body** (7–10) | Endure with Endurance; sustained Exert | −1 | −2; breathers restore no Vitality | −2; that, and `cond.weakened` (S1) | −3; that, and one action fewer each turn |
| **head** (11–12) | checks with Wits or Intellect, tempo included; concentrate-trait beats | −1 | −2; a Precision snag on ranged attacks and sight beyond `band.near` | −2; that, and one sense lost (the entry says which) | −3; that, and one action fewer each turn |
| *any site* | maximum Vitality | — | −2 | −3 | −4 |
| *any site* | heals | next long rest, or treated | clock 4 | clock 6, care only; a scar | surgery, clock 12; a scar; a maim if unoperated 7 days |

Sample names (family × site, S2 → S5): *cut, arm* — gashed forearm · arm laid open to the muscle · severed
tendons in the arm · arm cut to the bone and hanging. *crush, body* — bruised ribs · cracked ribs · broken
ribs · crushed chest. *frost, arm* — frost-nipped fingers · frostbitten hand · dead-white hand · arm frozen
through. *fire, head* — singed face · burned face · seared eyes · burned to the skull.

**T-07-7 Out-of-fiction blocks this chapter adds** (chapter 12 owns the block conventions, 12.15; chapter 14
renders them).

```
[WARNING] THIS CAN KILL YOU — <source as perceived>. <cause line>
          From your next action on, falling here can mean Dying. Fate: <n>.
          Exits now: Yield — <…> · Retreat — <…>
[WARNING] A hard fight — you may well lose this. Losing here means <disposition in words>.
[STATUS]  STAGGERED — blows now wound you; at wound load 3 you <fall to Dying | go Down>. Load <n>/3.
          Exits: Yield — <…> · Retreat — <…> · or fight on.
[STATUS]  DYING <n> of 3 — one action a turn; a check each turn (you need <d> or better; <odds>).
          A blow adds a step. Past 3 you choose from the last-chance menu. Exits: Yield — <…>.
[CHOICE]  THE THRESHOLD — you do not roll to die; you choose.
          (1) Captured — <who, where> · (2) Maimed — <attribute −1; what is lost>; you stand ·
          (3) Death's Bargain — <who asks what> · (4) Left for Dead — <what is taken; where you wake> ·
          (5) Rout — <clock +3> · (6) Reprieve — fate <cost> of <n>; you stand ·
          (7) Last Stand — one turn, then death · (8) Gamble — <odds: free / live / choose / death> ·
          (9) The Road Ends — you live; your adventuring is over.
          Struck: <option — the fact that rules it out>. There is no default: the moment holds.
```

**T-07-8 Yield: acceptance and terms** (`harm.yaml#yield`).

| Victor's disposition | Accepts? | Terms the player may choose one of |
|---|---|---|
| capture | yes | parole · keep one thing · spare another · send word · an audience |
| ransom | yes | parole · keep one thing · spare another · send word · an audience |
| rob | yes | keep one thing · spare another |
| drive_off | yes | spare another · an audience |
| leave | yes | — (no further harm is the whole of it) |
| kill, drag_to_lair | no, unless a recorded want of its leader can be met (the answer names it) | — |

**T-07-13 Marks** (`data/injuries.yaml`; summary).

| Brink mark | Drawn when the source carried | Upside | Downside |
|---|---|---|---|
| Pale streak | always offered | — | — |
| Hard to kill | any | +2 edge on dying checks and the Gamble | maximum Vitality −1 |
| Grave-cold | undead, frost, blight | frost hazards one rung lighter | −1 status on Talk that comforts or befriends |
| Ghost-sight | spectral dead, spirits, blight | a Precision lever on Observe for spirits and the spectral | dread threshold −1 |
| Fire-kissed | fire, fire elementals, dragons | reduce fire harm by 1 | frightened (S1) when first burning in a scene |
| Storm-touched | storm, air elementals | +1 edge on tempo checks | −1 status on manipulate-trait beats |
| Beast-wary | beasts | a Precision lever on Observe for beasts and their sign | −1 status on Handle with animals |
| Iron gut | venom, corrosion | +1 edge on checks against poisons | maximum Vitality −1 |
| Cold nerve | folk; any | immune to frightened at S1 | −1 status on Talk asking a stranger's trust |
| Drowned once | asphyxia, water | holds breath 6 rounds longer | frightened (S1) on first entering deep water in a scene |
| Sun-scarred | radiance | reduce radiance harm by 1 | −1 status on sight-based Observe in dim light |
| Witch-marked | arcane, mind | +1 edge on Endure with Resolve against magic | maximum Vitality −1 |
| Quick to clot | cut, pierce | bleeding ends at the end of each turn | maximum Vitality −1 |
| Light sleeper | any | cannot be surprised while resting | dread eases by rest only in a haven |
| Mended crooked | crush | +1 edge to Might defense against Force and Grapple | −1 status on Exert to jump or run |
| Death's debtor | granted only by the Bargain | — | the visible sign of the debt |

| Maim (site) | Attribute −1 (first eligible) | Lasting restriction |
|---|---|---|
| Lost hand (arm) | Agility, else Might | no method that needs two hands |
| Ruined arm (arm) | Might, else Agility | −2 status on Grapple and Might-based Force and Exert |
| Lost foot (leg) | Agility, else Might | pace −1 |
| Ruined knee (leg) | Agility, else Endurance | −2 status on Exert to jump, run or climb |
| Broken wind (body) | Endurance, else Might | breath held half as long; −2 status on Endure to keep going |
| Gut-scarred (body) | Endurance, else Resolve | −2 status on checks against anything eaten or drunk |
| Lost eye (head) | Wits, else Agility | a Precision snag on ranged attacks and sight beyond `band.near` |
| Deaf ear (head) | Wits, else Presence | a Precision snag on hearing-based Observe |
| Broken face (head) | Presence, else Wits | −1 status on Talk with strangers; no disguise without a full mask |
| Addled (head) | Intellect, else Wits | −1 status on Recall and concentrate-trait beats |
| Hollowed (spirit: blight, arcane, radiance, mind) | Resolve, else Presence | −1 status on dread checks |

Haunts are listed in 07.11.5. Scars: one entry per harm family (`inj.scar.*`).

**T-07-16 Afflictions** (`data/afflictions.yaml`; W = warn stage, × = checks before it runs its course).

| Id | Kind · delivery | Virulence | Onset → cadence | Stages (carrier severity; stage harm) | Lethal | Ends |
|---|---|---|---|---|---|---|
| `aff.adder_venom` | poison · wound | Moderate | 1 round → round | S1; S1 · S2; S2 · S3 + weakened; S2 | no | ×4 |
| `aff.widow_venom` | poison · wound | Hard | 1 interval → interval | S1 + slowed · S2 + slowed, weakened · S3 + cannot move, one action | no | ×6 |
| `aff.nightshade` | poison · eaten | Hard | 1 interval → interval | S2 + distracted · S3; S2 (W) · S4; S3 | yes | ×8 |
| `aff.drowse` | poison · eaten, breathed | Moderate | 1 interval → interval | S1 + distracted · S2 + asleep | no | ×3 |
| `aff.wyvern_venom` | poison · wound | Very hard | 1 round → round | S2; S2 (W) · S3; S3 · S4 + slowed; S3 | yes | ×6 |
| `aff.ghoul_ichor` | poison · wound | Moderate | 1 round → round | S1 + slowed · S2 + rigid one round | no | ×3 |
| `aff.blackroot` | poison · wound, eaten | Hard | 1 interval → interval | S2 · S3; S2 (W) · S4; S3 | yes | ×6 |
| `aff.grey_spore` | poison · breathed | Moderate | 2 rounds → interval | S1 + distracted · S2 + exhausted | no | ×4 |
| `aff.marsh_fever` | disease | Moderate | 2 days → day | S1 · S2 + exhausted · S3; S2 (W) · S4; S3 | yes | cure |
| `aff.wound_rot` | disease | Hard | 2 days → day | S2, the wound stops healing · S3; S2 (W) · S4; S3, the wound worsens | yes | cure |
| `aff.red_flux` | disease, contagious | Moderate | 1 day → day | S1, water use doubled · S2 + exhausted · S3 + exhausted, weakened | no | ×7 |
| `aff.grave_chill` | disease (blight) | Hard | 1 watch → day | S1 · S2, maximum Vitality −2 · S3, −4, dread +1 a day | no | cure |
| `aff.rat_plague` | disease, contagious | Hard | 3 days → day | S1 · S2 + exhausted · S3; S2 (W) · S4; S3 | yes | cure |
| `aff.lockjaw` | disease | Hard | 4 days → day | S1 · S2 + silenced, slowed (W) · S3 + cannot move; S2 | yes | cure |
| `aff.deaths_debt` | curse (the Bargain) | — (no checks) | at once → the debt clock | S1 the sign; rests ease no dread · S2 no healing magic · S3 maximum Vitality −4 (W) · S4 forfeit | yes | the vow kept |
| `aff.evil_eye` | curse | Moderate | 1 day → day | S1 a snag on the first roll each scene · S2 the first two · S3 and stakes +1 on the first Risky frame | no | ×7, or its lift |
| `aff.wasting` | curse | Hard | 1 day → week | S2 maximum Vitality −2 · S3 −4 + exhausted · S4 rests at best partial | no | its lift |
| `aff.grave_bound` | curse | Hard | 1 day → week | S2 rests restore half · S3 no healing magic · S4 nothing restores Vitality | no | its lift |

**T-07-18 Simulation: targets and results** (`07-harm-sim.py`, seeded, 20,000 fights a row; chapter 06's
fight model and T-06-12 lines with this chapter's ladder; PC Vitality 12 / 14 / 16 / 18 / 20 by band; full
write-up `rules/_process/simulation/07-harm-sim.md`).

| Target | Result |
|---|---|
| From any Vitality above 0, one harm event ends at Staggered | exact, by 07.2.3 |
| Hits of one severity, from full, to Staggered and then to Dying (lethal): **P1** (Vitality 12, light armor 1) | S2: 6 then 3 · S3: 3 then 3 · S4: 2 then 2 · S5: 2 then 1. Unarmored: S2 4+3 · S3 3+2 · S4 2+1 · S5 1+1 |
| The same at **P3** (Vitality 16, medium armor 2) | S2: 16 then 3 · S3: 6 then 3 · S4: 3 then 2 · S5: 2 then 1. Unarmored: S2 6+3 · S3 4+2 · S4 2+1 · S5 2+1 |
| A foe of the PC's band needs 3–7 telling blows to Stagger, and never fewer than 2 harm events to reach Dying | met at every band (T-06-12's same-band foes: 6, 7, 6, 6, 4 blows to Stagger) |
| Lethal fights, foes that kill, the PC never backs down: per 100 fights by 09's advisory | **trivial** Staggered 1, Dying 0, menu 0 · **easy** 7, 1, 1 · **fair** 31, 7, **5** · **hard** 67, 32, **26** · **lethal** 96, 84, **80** |
| The same, taking an exit when Staggered (Retreat as a chase won 60%; else cornered) | menu: fair **2** · hard **11** · lethal **34** |
| The same foes, but they capture or rob, and the PC yields when Staggered | menu: fair 0.1 · hard 0.1 · lethal 0.6 |
| **Risky** fights (no lethal context) against **Dire** ones (lethal context), same foes | Risky: Dying **0** at every advisory (by rule), Down 0 / 1 / 7 / 32 / 84 · Dire against capturing foes: Dying 0 / 1 / 7 / 32 / 84, menu 0 / 0.1 / 1 / 5 / 13 · Dire against killing foes: menu 0 / 1 / 5 / 26 / 80 |
| A first fall left alone stabilizes ≥ 80%; a third ≤ 15% (Endure +2) | 85% · 44% (second) · 11%; with first aid each round 98 / 79 / 35 |
| Wounded memory bites | the same hard fight with brink 0 / 1 / 2: of those Dying, 74% / 90% / 98% reach the menu |
| Dying to full (Vitality, every wound, brink) | haven with a healer: median **2** days (90th percentile 3) · road, treated daily: **2** (6) · road, untreated: **4** (8), and 13% carry a wound that needs care to heal |
| Vitality from 0 to maximum with no wounds | one full long rest; or two short rests |
| The Gamble at Endure +2 | 5% stand free · 35% live · 15% choose a price · **45% death** |

The wound load limit was tuned on these: at 2 the fair row read menu 9 and the hard row 36; at 3, 5 and 26
(DL-07-04).

**T-07-20 Numbers other chapters consume.**

| Number | Value | Read by |
|---|---|---|
| PC maximum Vitality | 02's base (10–16) + 2 × (power_band − 1), cap 24, floor half | 02, 04, 06, 09, 14 |
| Reduction cap; armor | 4; light 1 / medium 2 / heavy 3; shields 0 | 06, 08, 09 |
| No-reduction harm | bleeding, choking, affliction stages, overdraw, falls, crushing mass, want | 05, 06, 10 |
| Dying steps; stabilize DCs | 3; 10 / 15 / 20 | 01, 05, 06, 16 |
| Wound load limit; load by bucket | 3; 1 / 1 / 2 / 3 / 4 | 06, 09 |
| Lethal-warning causes | ten (07.3.3); a Windup counts | 06, 09, 10, 11, 12 |
| `fate_cost` of a reprieve | min(3, 1 + reprieves taken) | 01, 14 |
| Rout's world cost | 2 ticks before the Threshold; 3 at it | 11 |
| Rest quality | full / partial / interrupted on the boundary payload, with site and treated | 05, 10, 15 |
| Vitality by rest | breather +2 (first two between short rests) · short +half (first two a day) · long to maximum | 05, 10, 12 |
| Recovery clocks | Heavy and brink 4 · Grievous 6 · Catastrophic 12 after surgery | 05, 15 |
| Treat DC tiers | Moderate wound Easy · Heavy Moderate · Grievous Hard · surgery Very hard | 05, 15, 16 |
| Dread threshold; haunts | 8 + Resolve; three, the fourth break ends the career | 02, 09, 11, 14 |
| Breath | 6 + 2 × Endurance rounds | 06, 10 |
| Companion bleeding out | a 4-segment countdown, +1 a round | 06, 16 |
| Setback facts | `setback.defeated / yielded / captured / dying_entered / threshold / retreated / companion_dead` | 12 |

---

## Worked examples

All examples continue **Wren** (00's sheet): Might +1, Agility +3, Endurance +1, Wits +2, Intellect 0,
Presence 0, Resolve −1; power band P1; Vitality 13 (12 + Endurance +1, 02.7.1) [revision: I-042]; Focus 4; fate 1; Guard 14. From this chapter: Endure
with Endurance **+2** (attribute +1, the competence floor +1); Endure with Resolve **+0**; dread threshold
8 − 1 = **7**. She wears a padded jack (light armor: reduction 1 against `harm.physical`; *illustrative, 08
owns*). Adversary lines are T-06-12's (*illustrative; 09 owns*). Dice are shown as rolled.

### WE-07-1 The Ninefold Barrow: a fight that goes all the way to the menu (both keys shown)

*Situation.* Wren has come for the crown the Salt Guild's factor sold her a map to. In the last chamber
a **barrow-wight** rises (`adv.barrow_wight`: T3; attack +7, *grave-touch* S3 `harm.frost`; Guard 17;
Vitality 18; reduction 1; fearless; `lethal_context: true`; `defeat_disposition: kill`; `dread: S2`; its
master, `npc.barrow_king`, carries `can_bargain: true` and the recorded want "the crown returned").

**The warning (Key 1).** At `scene_start`, `h.07.lethal_scan` finds three rows true for the wight:
`advisory` (P1 against one T3 is two bands up: lethal, T-06-13), `archetype`, `disposition`. One context is
written, with the first true cause. The engine supplies the sign (the wight's tell); the DM narrates it
and appends the block:

> Frost creeps across the grave-goods toward your boots, and where it passes the gold goes dull.
> `[WARNING] THIS CAN KILL YOU — the barrow-wight. As things stand you are unlikely to win this.`
> `From your next action on, falling here can mean Dying. Fate: 1.`
> `Exits now: Yield — not accepted (it does not understand quarter) · Retreat — clean: it is slower than you; nothing to pay.`

`lethal_context {id: lc.barrow.wight, cause: advisory, shown: true, effective_from: after Wren's next
declaration}`. First sight of a `dread: S2` adversary: a dread check, Resolve +0 against Moderate (15):
d20 9 → failure → dread **1/7**.

**The fight.** The player stays for the crown and backs into a burial niche to keep the thing in front of
her. Rounds in brief (Wren's spear: +4 against Guard 17; her hits deal 3 − 1 = 2):

| Round | What happens | Wren's state |
|---|---|---|
| 1 | Wren hits once (wight 16). The wight Moves to the niche's mouth: the feature has one way out and it now stands in it → `flag.cornered` (06.3.6). It Strikes: d20 14 + 7 − 2 (Fend) = 19 against Guard 14: hit; S3 frost = 5; the jack does not reduce frost. | Vitality 13 → **8** (worn) |
| 2 | Wren hits once (14). The wight: d20 12 → 17, hit, 5 → Vitality 3 (**bloodied**). Second Strike (repetition −2): d20 11 → 16, hit, 5: Vitality would be −2 → **0, Staggered; the excess 2 is discarded** (07.2.3). | Staggered; load 0/3 |

`trg.exits` → `[STATUS] STAGGERED — blows now wound you; at wound load 3 you fall to Dying. Load 0/3.
Exits: Yield — not accepted · Retreat — you are cornered: get past it first (06.5.6) · or fight on.`

| Round | What happens | Wren's state |
|---|---|---|
| 3 | Wren tries to Force past (fails), hits once (12). The wight: d20 15 → hit, 5: Staggered, so a **wound**: bucket Heavy (5–7), load +2 = **2**; family frost; site d12 = 8, body → *Frost-burned chest* (`inj.w.frost.body.s3`: −2 on Endure with Endurance, breathers restore nothing, maximum Vitality −2). Second Strike: **natural 20** → critical success → one rung heavier, S4 = 8: bucket Grievous, load +3 = **5 ≥ 3**. The context is effective and the wight's mode is lethal → **Dying 1** (brink 0). Site d12 = 2, arm → *Dead-white hand* (`inj.w.frost.arm.s4`). Prone. Dread +1. | Dying 1; dread 2/7 |

`[STATUS] DYING 1 of 3 — one action a turn; a check each turn (you need 8 or better; 65%). A blow adds a
step. Past 3 you choose from the last-chance menu. Exits: Yield — not accepted.`

| Round | What happens | Wren's state |
|---|---|---|
| 4 | Wren's one action: a last thrust from the floor (prone −2 is the worst status; +2 against 17): d20 7, miss. `turn_end`, **dying check**: d20 5 + 2 = 7 against 10: a failure by 3 → **holds**. The wight (a prone target is a lever): d20 6 + 7 + 2 = 15, hit: lethal harm → **Dying 2**; *Frostbitten foot* (leg, S3). Second Strike misses. | Dying 2 |
| 5 | Wren crawls for the back of the niche. Dying check against 15: d20 9 + 2 = 11: a failure by 4 → **Dying 3**. The wight: d20 13 → hit: the step would be 4 → **the Threshold** (07.5.1). The step is held at 3; this blow's harm is not applied; the conflict pauses; dread +2. | at the Threshold; dread 4/7 (shaken) |

**The menu (PR-07-5).** The engine evaluates the nine options against state:

| Option | Result | Why |
|---|---|---|
| 1 Captured | not offered | the victor's disposition is kill |
| 2 Maimed | **offered**: *Lost hand* — Agility −1 (to +2), no two-handed methods; she stands at Vitality 2 | worst fresh wound: Grievous, arm; d2 between the arm maims |
| 3 Death's Bargain | **offered**: the barrow-king asks "return the crown of the Ninefold Barrow to its head" | a bargainer bound to the scene; its recorded want |
| 4 Left for Dead | not offered | kill makes sure |
| 5 Rout | not offered | cornered; no companion |
| 6 Reprieve | **offered**: fate 1 of 1 (first of her life) | `fate.current ≥ 1` |
| 7 Last Stand | **offered** | always |
| 8 Gamble | **offered**: 5% stand free · 35% live · 15% choose a price · **45% death** | Endure +2 against 15 |
| 9 The Road Ends | **offered** | always |

The DM strikes nothing: no fact rules out any survivor. Six remain; four are not death: valid.

**The two keys at this moment.** Key 1 holds: `lc.barrow.wight`, warned at the scene's start, effective
since Wren's first declaration. Key 2 does **not** hold: she is at the Threshold and has chosen nothing.
If any tool tried to write `harm_state.dead` now, the engine would refuse it. Only options 7 and 8 can
turn the second key.

**The choice.** The player takes the Bargain. Writes: stabilized (Dying ends; Staggered; Vitality 1); one
brink wound; `aff.deaths_debt` stage 1 (`cond.cursed` S1); a vow thread "Return the crown" with
`clk.deaths_debt` 0/8, +1 a week; the mark *Death's debtor* (a rime-white streak in her hair); the fact
"the wight lowers its hand and goes back to its slab"; wound load cleared; `setback.threshold`; chronicle:
"Walked out of the Ninefold Barrow owing the dead a crown." She leaves with three wounds (chest, hand,
foot), brink 1, a maximum Vitality of 7 (13 − 2 − 3 − 2 − 2 would be 4; the floor is half of 13, rounded up),
dread 4/7, and a debt that will come due.

*Boundary: the other cheap door.* Had she taken the **Reprieve**: fate 1 → 0; the last blow is undone;
Dying ends with no brink wound and no mark; Vitality 2; load 0; she stands, still cornered, facing a
wight with 12 Vitality. Her next reprieve would cost 2, and she has none.

*Other side: no Key 1.* Had no warning been shown (say the wight had been an unlisted improvisation and
no row had fired), round 3's second blow would have been `lethal: false`: load 5 → **Down**, not Dying.
A `kill` victor with no effective context can do no more (T-07-11): it leaves her for dead; she wakes a
watch later on the barrow floor with her wounds, and the engine raises the warning for any return.

*Tempting non-example.* "The natural 20: its hand closes on your heart, and you die." A critical success
is one severity rung (01.8.3). To a Staggered character it was a Grievous wound and a fall to Dying 1;
to a character at full Vitality it would have been 8 points and nothing more.

### WE-07-2 The Tarn bridge: a hazard that nearly kills without a lethal frame, and why it cannot

*Situation.* Days earlier. Wren, at Vitality **4** after a scrap with poachers, crosses a rope bridge.
Its rot is a hidden danger (`haz.rotten_bridge`: a 40-ft fall, S4, `harm.physical.crush`; *illustrative, 10
owns*). She did not look it over, so nothing perceivable was established: the `severity` row needs the
source to be **perceived**, and it was not. No warning exists, so no context.

1. A plank goes. The hazard's resisted check: Evade, Agility +3 and the floor +1, against its listed DC,
   Hard (20): d20 9 → 13: failure → the hazard at its severity.
2. `apply_harm(S4, [harm.physical.crush], source {hazard}, lethal: true?)` — the tool tests 07.3.6: no
   effective context → **`lethal: false`**, logged `lethal_refused`. Falls take no reduction: 8.
   Vitality 4 → **0, Staggered; the excess 4 is discarded.** She is in the river.
3. The river in spate (`haz.river_spate`: S3, cadence a round, Endure against Hard; `lethal_context:
   false`) is a second source. Round 1, first exposure: Endure +2: d20 12 → 14: failure: 5, no reduction
   (the weight of water). She is Staggered: bucket Heavy, **load 2**; a first exposure makes a record:
   *Cracked ribs* (crush, body, S3).
4. Her turn: Exert to reach the bank (Might +1, the floor +1, the cracked ribs −2: +0) against Hard:
   d20 10: failure. Round 2, a continuing tick (periodic): Endure d20 4 + 2 − 2 (the ribs) = 4: a
   critical failure, one rung heavier: 8. Bucket Grievous: load 5 ≥ 3, **not lethal → Down** (07.2.9).
   No record (periodic).
5. A hazard's defeat is the `leave` row with its aftermath: she is carried down. One interval later she
   wakes on a gravel bar at the next place downstream, Staggered at Vitality 0, ribs cracked, her spear
   on the riverbed below the bridge (a recorded place: she can go back for it), the objective of the
   crossing lost, `setback.defeated` written.

**Why it could not kill her.** Three independent stops, each a `[D]` rule: (a) no lethal context was
effective for either source, so every harm event was `lethal: false` (07.3.6); (b) the fall's 8 points
could only Stagger a character with 4 Vitality (07.2.3); (c) non-lethal harm at load 3 ends at Down, and
a Down character's ladder is frozen (07.2.9). Nearly drowned is the worst the unannounced world can do.
And the world is now on notice: the gorge has been perceived, so the `severity` warning is raised and
shown; the next crossing is a fair lethal risk.

*Boundary: had she looked.* An Observe of the bridge that found the rot would have fired the warning
before she stepped out: "`[WARNING] THIS CAN KILL YOU — the bridge over the Tarn: a forty-foot drop. A
Grievous danger.`" Crossing would then be an Exert at Dire with `lethal: true`, shown in the OFFER. A
failure: 8 points, lethal: Vitality 4 → 0, Staggered, excess discarded. **Even warned, the fall alone
cannot kill.** Only a character who stepped onto that bridge already Staggered would fall to Dying 1
(a Grievous wound: load 3), and would then have dying checks, and then a menu.

*Tempting non-example.* "You fall forty feet onto rocks. Roll Endurance or die." No rule here rolls for
death. The fall is 8 Vitality through `apply_harm`.

### WE-07-3 Blackroot: a poison runs its stages

*Situation.* Ashford, a fortnight later; Wren is whole (Vitality 13). A Guild knife-man's blade is coated
(`aff.blackroot`: Hard; onset and cadence one interval; stage harm from stage 2; `warn_stage: 2`; six
checks and it runs its course).

| When | Check | Result |
|---|---|---|
| the cut | The Strike hits: 3 − 1 = 2 (Vitality 11). A rider: **exposure**, Endure +2 against 20: d20 11 → 13 | failure → afflicted; onset one interval. He runs. |
| interval 1 | onset ends (`h.07.affliction_onset`) | **stage 1**: `cond.poisoned` S2 (−2 on all checks). "A numb line creeping from the cut." |
| interval 2 | stage check (no penalty from its own carrier): d20 9 → 11: a failure by 9 | **stage 2**: poisoned S3; stage harm S2 = 3, no reduction: Vitality **8**. Stage 2 is the warn stage → `[WARNING] THIS CAN KILL YOU — the blackroot in your blood. Untreated, Blackroot will put your life at risk at its next stage. Fate: 1. What stops it: a bitterwort draught; a healer; time (four more checks).` |
| interval 3 | She has walked to Maren the hedge-healer (an interval). Check: d20 15 → 17: a failure by 3 | **holds** at 2; stage harm 3: Vitality **5** (lethal now, and she is still active: it is only Vitality). |
| the same interval | Maren **Treats** the affliction: Intellect +2, medicine +3, kit lever +2 = +7 against 20: d20 16 → 23: success, reach 2 | Wren's next stage check holds a Precision lever. Maren has no bitterwort; her charcoal purge is a **general remedy**: one stage down → **stage 1**. |
| interval 4 | check with the lever: d20 12 + 2 + 2 = 16: a failure by 4 | **stage 2** again; harm 3: Vitality **2**. (One Treat a day: no second lever. One remedy a period: a second purge → stage 1.) |
| interval 5 | check: d20 18 + 2 = 20 | success → **stage 0: cured**; the carrier ends. Four checks used of six. |

She ends at Vitality 2 with no wound, owing Maren for two purges and a morning. *What a worse fourth
check would have begun:* stage 2's harm takes Vitality 2 → 0 (Staggered, excess discarded); the next
stage harm is periodic at 0 Vitality: load, no record; stage 3's 5 points are load 2; one more such
tick is load 4: Dying 1, lethal because she was warned at stage 2. From the warning to Dying is at least four
more failed checks: forty minutes of chances, each of them visible.

### WE-07-4 Taken in the reeds: a capture that becomes a new adventure

*Situation.* (Chapter 12's WE-12-8 from this chapter's side.) Two Salt Guild riders (T2; `defeat_disposition:
capture`; `lethal_context: false`) run Wren down in the reed beds. P1 against two T2 is **hard**, and no
lethal row is true, so the framing carried the danger notice: "`[WARNING] A hard fight — you may well
lose this. Losing here means being taken alive by the Guild.`" Three rounds in she is Staggered:

> `[STATUS] STAGGERED — blows now wound you; at wound load 3 you go Down. Load 0/3.`
> `Exits: Yield — accepted: they would bind you and take you to the Guild · Retreat — they are mounted and`
> `want you: run for it (a chase), or rout: you get clear and the Guild's hold on the Salt Road tightens`
> `(Corner the Salt Road +2) · or fight on.`

**The yield.** "I throw down the spear." Accepted by lookup (capture). The allowed terms are read out; the
player chooses **keep one thing**: the Ember-Fang Charm. PR-07-7, yielded column:

1. `defeated {manner: yielded}`; `setback.yielded`; the conflict ends. No further harm; she is conscious.
2. Holding place `[J:enum]`: the engine returns the Guild's holds within reach; the nearest is the north
   warehouse in Ashford (00's fact "The Salt Guild owns the north warehouse"), two travel watches off.
   `advance_time` runs both watches and every boundary in them; she arrives at dusk and **saw the way**:
   the back lane and the river door are now facts she knows.
3. Bound (`cond.restrained`, until cleansed). Her spear, bow, rope, rations and 14 coin go to
   `cache.01 {holder: fac.salt_guild, place: the warehouse tally room}` with `clk.cache` 0/6. The charm
   stays on its thong (the term is a commitment on the victors).
4. `clk.captors_intent`, named "The factor's reckoning": 6 segments, sensed, +1 a day; the fate for this
   victor is *sale* (to the salt galleys; *illustrative, 09*). Not lethal: no warning.
5. Three openings, d8 without repeats: 6, 3, 1 → "they move prisoners down to the barge when the factor
   returns" (the clock's next tick) · "a Caravaners' agent has been asking the gate-men about a forester"
   (a rival who wants her free) · "the night guard, Tam, is young, bored and short of coin" (a named
   walk-on with a want). Each is written as a fact or an entity.
6. `thr.captivity` "Out of the Guild's hands": progress 0/6, public, racing the factor's reckoning.
7. `victory_over_pc` (the riders' sergeant is spoken of at the warehouse; 11); a reputation packet scoped
   to those who saw her brought in; chapter 12's director enters recovery.
8. Lead check: three openings, a known cache, a sensed clock. Passed.

**The next scene** is framed at the first moment she can act: a tally-room cage, a lamp, Tam on a stool
with a pair of dice. Everything a sandbox scene needs is in state: a place she has seen the way out of, a
clock with omens, people with wants, her gear forty feet away. She works on Tam (a Talk beat: ch.15): a
success at Standard reach ticks "Out of the Guild's hands" to 2/6. At the `day` boundary the reckoning
ticks to 1/6 with its omen ("the guards talk about someone who is coming"). Whether she bribes, slips
her bonds, waits for the Caravaners, or is marched to the barge and jumps, the capture has become the
adventure.

*Boundary: the same fight, fought to the end.* Staggered, then three wounds: load 3 under no lethal
context → **Down**. The defeated column: no term (the charm goes into the cache), bound, carried
unconscious (she did **not** see the way), waking in the cage with three Light wounds (a soldier's
sword through a padded jack is 2 points: the Light bucket) that her first rest will clear. Yielding
bought her the charm, the route and her senses.

*Tempting non-example.* "The sergeant takes pity and lets her go with a warning." A disposition is data;
the DM does not choose mercy. If the fiction is to free her, it does so through an opening she works.

### WE-07-5 A broken night, and the days after the barrow

*Situation.* The night after WE-07-1. Wren: Vitality 1 of a maximum 7; wounds: chest (Heavy, 0/4), foot
(Heavy, 0/4), hand (Grievous, 0/6), brink 1 (0/4); dread 4/7; cursed at stage 1. She makes a dry camp in
a hollow with a fire: **camp**. Before she lies down the DM states the best case: no cap applies (light
armor, fed, sheltered, the curse is at stage 1), so "a full rest is possible; a watch check will run".

`advance_time(1 watch)`. Three hours in, 10's watch check interrupts: two figures at the edge of the
firelight.

- *Branch A: travelers.* They talk, share the fire, move on: no item of 07.8.3 happened. The rest was
  suspended and resumes; quality **full**. `rest_long {quality: full, site: camp, treated: false}`.
  Vitality 1 → **7**; dread stays 4 (a full rest would ease 1, but the debt's first stage says rests
  ease none); `rested_today`. Chapter 05 restores Focus to its maximum.
- *Branch B: robbers.* `conflict_start` with Wren in it: an interruption. It lasts four rounds (they run
  when she shows steel). She lies down again inside the hour and still gets her four hours: resumed,
  quality **partial**. Vitality to three quarters of 7, rounded up: **6**; dread unchanged;
  `rested_today` still set. Focus to three quarters.
- *Branch C: the same, and she chases them for an hour.* Beyond the allowance: **interrupted**: Vitality
  as a partial short rest: a quarter of 7, rounded up: +2 → 3. No `rested_today`. `watches_awake` is set
  to 2.

**The days after** (T-07-15), two ways:

| Day | On the road, no healer | In Ashford with Maren (haven; bed rest; treated daily) |
|---|---|---|
| 1 | chest 1/4, foot 1/4, brink 1/4; hand 0/6 | Maren's Treat for the hand is Hard (20): +7 with her kit, needs 13. Day 1 she fails (the day's treatment is lost; the Heavy wounds still gain bed rest and rest): chest 2/4, foot 2/4, brink 2/4, hand 1/6 |
| 2 | 2/4, 2/4, 2/4; hand 0/6 | she succeeds, reach 2: everything treated: chest **4/4 healed**, foot **healed**, brink **healed**; hand 3/6. Maximum Vitality 13 − 3 = 10 |
| 3 | 3/4 … | hand 5/6 |
| 4 | chest, foot and brink **healed**; maximum 13 − 3 = 10; hand 0/6 | hand **healed**: maximum 13; a scar: *a dead-white, numb patch* (`inj.scar.frost`) |
| 7 | the hand has had no tick for 7 days: an exposure to `aff.wound_rot` (Endure +2 against Hard) | — |

On the road she is fit to fight in four days and carrying a wound that will not heal and may rot. In a
bed with a healer she is whole in four. Each of those days runs the world: the debt clock among them.

### WE-07-6 Brack, bleeding out; and a break

*Situation.* Months on, under Grey Keep, with a hound companion, Brack (Vitality 8; 16 owns), and dread
at **5/7** (shaken) after a bad week. Ghouls (`lethal_context: true`, warned at the scene's start).

1. A ghoul's bite takes Brack from 3 to 0: a lethal event → **bleeding out**: `clk.bleeding_out` 0/4,
   public. The player sees it at once: "Brack is down and bleeding: four rounds."
2. End of round: 1/4. Wren's turn: Move to him (1 action); first aid, `verb.handle` against Moderate
   (15), Agility +3 and the floor: +4, no kit: needs 11: d20 6: nothing changes. Her third action: a
   Strike at the ghoul over him.
3. The ghoul bites Brack again: a further lethal event: +1 → 2/4. End of round: 3/4.
4. Wren's turn, first aid again (one attempt a round, PR note in Edge cases): d20 13 + 4 = 17: success →
   **stabilized**; the clock is voided. Brack will wake after a long rest with a Heavy body wound and
   cannot be sent to fight until it heals.

*The other branch.* d20 8: failure. End of round: 4/4: **Brack dies.** `setback.companion_dead`; the
ghouls' morale clock ticks −1; a dread check at S3 (Hard, 20) for Wren, Resolve +0: d20 12: failure:
dread +2 → **7/7: she breaks.** The resolve test against Hard: d20 14: not steeled. The engine draws three
haunts gated on what filled the track (the ravenous dead, a companion's death): *night terrors*, *a dread
of the ravenous dead*, *the stare*. The player picks **the stare**. Dread returns to 0; she is frightened
(S2) of the ghouls for the scene (−2 on all checks while she can see them; she cannot willingly close);
the codex shows **haunts 1 of 3**. She still chooses every action she takes.

*Boundary.* Had the resolve test shown a 20: **steeled**: dread to 3, `cond.heartened` (S2) for the scene: +2 on all checks, and the ghouls have made
a mistake.

### WE-07-7 Three ways out of a cellar

Wren, at Vitality 5, wants out of a fight she is losing. The same declaration, four states [revision: I-076]:

| The opposition | Pursuit test | What the DM says before she commits |
|---|---|---|
| two ghouls, slower than she is; she is engaged with one | willing (kill), not able | "**Clean.** One parting blow as you break away: its claw, a rung lighter: Light, which your jack turns (0). You leave the satchel on the far table." Certain. |
| a cinder hound, faster, hunting her; not engaged | willing and able | "**Run for it**: a chase, about three chances in five from here. Or **rout**: you get out for certain, and it follows your trail toward Ashford (Cinder Hunting Ground +2)." |
| the same hound, on the far side of the cellar door she has slammed and barred (T-06-9 row 11) | willing, not able (no way to follow) [revision: I-076] | "**Clean.** It will be through that door with a Force against Moderate; you will be up the stair by then. The satchel stays on the far table." |
| the same hound, and she is `flag.cornered` | — | "You cannot retreat with your back to the wall. Get past it first (Force or Move through, 06.5.6), or Yield (not accepted)." |

If she routs: the clock ticks 2 with its omen; `objective_lost`; `setback.retreated {severity: S3}`; she
is at the nearest place the stair reaches. *Non-example:* "I retreat, and since I got away clean nothing
is lost": the satchel's location is a fact; it is still on the table.

---

## Edge cases & adaptation anchors

### Reaching for an anchor

When something happens to a body or a mind that no rule names, reach first for one of these, change at
most two knobs (00.2.7), and log the ruling. Each is an `Anchor: yes` rule of this chapter.

| Anchor | Reach for it when the intent is to… | Knobs (default → allowed change) |
|---|---|---|
| **07.4.1 Yield** | surrender, submit, bargain from a losing position, play dead *to be spared* | `targets` (the side → one faction of it); `condition` (the term) |
| **07.4.3 Retreat** | get out of any losing situation at a known price: a fight, a riot, a collapsing deal, a burning building | `time_cost` (a turn → an interval); `harm_severity` (the parting blow → none when screened) |
| **07.8.8 Treat** | mend any living thing or slow anything that is killing it: a wound, a fever, a venom, a sick horse, a blighted tree | `dc` (wound tier → virulence → one tier harder for an unfamiliar body); `time_cost`; `targets`; `stakes` |
| **07.10.2 Hazard severity** | be harmed by anything with no entry: a toppled brazier, a hive, a millrace, a collapsing shelf | `harm_severity`; `harm_tags`; `dc`; `duration` |

And these `[D]` structures are anchors by shape, for 12's anchor index:
- **A staged affliction** (07.9) for anything that worsens on a schedule unless resisted or treated: frostbite
  setting in, a spreading rot in a beam, a slow enchantment, an addiction, a panic moving through a crowd.
  Knobs: virulence tier, cadence, the carrier, stage harm, `max_checks`.
- **A recovery clock** (07.8.6) for anything that mends by days with care: a lame horse, a cracked hull,
  a broken trust (15 may reuse the shape). Knobs: size 4 / 6 / 12; which of the three daily flags tick it.
- **The disposition table** (T-07-11) for what any victor does with any loser, including NPCs beaten by
  NPCs and the PC's own prisoners (07.6.5).
- **The dread check** (07.11.2) for any lasting horror, grief or despair, and the **break** for the moment
  it tips.
- **The Threshold menu** (07.5) is not an anchor: it is used only at the Threshold.

### Edge cases

- **A harm event of exactly the remaining Vitality.** Vitality 0: Staggered, nothing discarded, nothing
  else happens. There is no "exactly zero" table; marks come only from the brink (07.7).
- **Several harm events in one beat** (a shaped effect that hits twice, a mob's blow and its rider's
  bleeding). Each `apply_harm` call is its own event, resolved in order: the first can Stagger, the
  second then wounds. The Stagger rule discards only the excess of the event that Staggers.
- **Healed in the middle of a fight, then dropped again.** Vitality above 0 makes the character active,
  but the wound load is not cleared until `scene_end` or a rest (07.2.6): with load 3 or more, the first
  harm event after it is Staggered again fells it again, at `1 + brink`.
- **First aid tried again.** A failed first aid changes nothing; the same tender may try once each round,
  because each round the state it works against has changed (the clock ticked, the step moved). This is
  the one exception to "let it ride" (01.4.2) in this chapter, and it applies to the Dying and to
  `clk.bleeding_out` only.
- **A Dying PC whose companion fights on.** The conflict continues (06.13.1); non-`kill` sides ignore the
  PC; the PC has its one action; a commanded first aid (06.14.2) costs that action.
- **A Dying PC with no enemies left.** Time stays in rounds until the ladder resolves. The player may
  declare one action a round. If the checks stabilize it, it is Staggered and prone, conscious, alone.
- **The Threshold is reached by a dying check with no victor present** (bleeding in an empty hall, a
  poison). Captured fails its requirement; Left for Dead is offered if the place is one a body can be
  left in ("you lie there until the cold wakes you, a watch later"); Rout if the PC could crawl a route.
- **The Threshold is reached while the PC is a captive.** The captors are the victors present: Captured is
  offered only if their intent was not this death; otherwise the usual always-available options.
- **A second Threshold in one scene.** Maimed is gone (once a scene). The Reprieve's cost has risen by one
  if it was used. Everything else is rebuilt from state.
- **The player wants the character to die** outside any danger. That is 07.5.13 (a voluntary last stand)
  only in a lethal context; with none, it is a retirement (11), not a death.
- **A non-lethal frame against a character already Dying** (a companion's clumsy drag, a fall while being
  carried). Recorded and discarded (07.2.11 b). Nothing non-lethal moves a step.
- **A lethal context for one source, harm from another.** Each harm event is tested against its own
  source (07.3.6). In a fight with warned wolves and an unwarned snare, the snare cannot move the PC
  toward death; the wolves can.
- **The warning's source is sealed** (a hidden clock, an unseen assassin). The warning names the sign,
  never the secret (07.3.4, cause `clock`); the context's `source` is the sealed id, held in state.
- **An adversary changes its mind** (a `capture` side turns to `kill` after the PC kills its leader). That
  is a recorded behavior change (09), which makes the `disposition` row true: a new warning, effective
  after the player's next declaration.
- **Poisoned and Dying.** The affliction's stage harm is one more lethal or non-lethal event by its own
  context (07.9.5). Its stage checks continue on their cadence beside the dying checks.
- **Two afflictions.** Each runs its own checks. Their carriers' status penalties do not add (worst only).
- **A wound to a site that already has a worse wound.** A second record is made (it has its own clock and
  its own Vitality penalty); the carrier stays at the worse severity (`replace_stronger`).
- **Maximum Vitality at its floor.** Further wounds still exist, penalize by site and need healing; they
  lower the maximum no further (07.1.2).
- **A character with no Endurance to speak of.** The dying check and the Gamble use the same formula for
  everyone; at −1 Endurance and the floor the modifier is +0: a first fall still stabilizes 74% of the
  time (07-harm-sim section B).
- **Resting while Staggered.** Allowed: a breather restores 2 Vitality and clears the load. Resting while
  Dying is not possible (07.8.1).
- **A rest site changes during the rest** (the haven's door is kicked in). The site is read at completion
  for quality; an interruption is judged by 07.8.3.
- **Skipping a week** ("I recover at the monastery"). `advance_time` runs seven `day` boundaries: seven
  daily passes (PR-07-10), seven sets of stage checks, one World Turn, one tick of every weekly clock
  (the debt, the cache). The DM narrates from the returned list.
- **An NPC the PC loves is dying.** NPCs follow 07.2.10: Dying, dead at `scene_end` unless stabilized.
  The PC's first aid or healing is the answer; the dread check applies if a bonded NPC dies.
- **The PC strikes a helpless or yielded foe.** Legal as a beat (06.11.7); the harm mode decides dead or
  alive; chapter 03 records it. This chapter adds nothing and softens nothing.
- **An effect says "kills outright", "slays" or "destroys"** (a monster power 09 or 13 might want). Against
  a PC or companion it is read as S5 harm through `apply_harm`: the two keys are not optional for
  content. Against others it does what it says.
- **Disputes.** "I should have been warned" is checked against the `lethal_context` record: if no
  effective context existed for the source, the event was not lethal, and 12.3.4's correction restores
  what a lethal ruling took. "I was warned" is the same lookup the other way.

---

## State touched

**Owned by this chapter (00.6.3).** `Character.vitality {current, max}` (shown); `harm_state` and
`dying_step` (shown); `wounds [WoundInstance {entry, severity, site, taken_at, frame_id, source, clock,
treated_today, treat_closed_today}]` (shown) [revision: I-078: `treat_closed_today`]; `marks [ref]` (shown); and, added by this chapter with their visibility:
`wound_load` (shown while Staggered), `down` (shown), `defeated {manner}` (shown), `brink` (derived,
shown), `dread {current, threshold}` (shown), `haunts` (within marks; shown *n of 3*), `afflictions
[{id, stage, onset_ends, checks_made, source, treated_today}]` (shown: name, stage *n of m*, next check; an
unidentified affliction shows its symptoms only; `treated_today`, a Treat beat framed it today whatever its
result, background [revision: I-078]), `watches_awake` (background),
`rested_today / treated_today / bed_rest_today` (background), `last_rest_long_end` (background: the
timestamp 00.7.2's two-watch gap counts from [revision: I-078]), `reprieves_taken` (available),
`lethal_context` records (shown once warned; the sealed source of a `clock` cause stays sealed),
`setback.*` facts (background; 12 reads them), `cache.*` records (available: what was taken and from
whom; the cache's place is known only if learned), `career_end` (shown).

**Read from other chapters.** Attributes and the creation base (02); `power_band` (04); Focus for grit,
overdraw refusals and the healing counter (05); frames, stakes, `lethal`, `fate`, the cost menu (01);
bands, flags, conditions, pace, objectives, morale and chase clocks (06); `threat_advisory`,
`lethal_context`, `defeat_disposition`, `captive_fate`, `dread`, tells, attack severities and sites (09);
hazard entries, supply, weather, `rest_site`, the place graph (10, 13); factions, holds, threads, clocks,
standing (11, 15); item prices, armor, kits and remedies (08); companion templates and loyalty (16);
`evidence_for_frame` (03).

**Tools used (00.14.2).** `apply_harm` (owner; PR-07-1), `update_quantity` (Vitality up, dread),
`apply_condition` / `remove_condition`, `apply_effect`, `set_fact`, `create_entity` (openings, caches,
holders), `set_position`, `advance_time`, `mark_boundary` (the three rests), `create_clock` /
`tick_clock`, `roll_table` (`tbl.wound_site`, `tbl.captivity_openings`, `tbl.bargain_asks`, the mark and
haunt draws), `frame_check` / `roll_check` (dying, stage, dread, Gamble, Treat), `offer_create` /
`offer_resolve` (the menu), `spend_fate` (01.16.4), `record_evidence` (through the frames that fell or
healed), `chronicle_append`, `get_active_triggers` (`trg.lethal_warning`, `trg.danger_notice`,
`trg.exits`), `check_claims`.

**Hooks (00.10.2).** Fires: `on_vitality_threshold` (half, zero), `on_harm_taken`, `on_dying`,
`on_stabilize`, `on_condition_applied` (carriers), `on_clock_complete` (recovery, bleeding out, captors'
intent, the debt, the cache). Subscribes to none: the ladder is core engine behavior and ignores depth
(00.10.8).

**Boundary handlers (00.7.4; `data/boundaries.yaml owner-block 07`).** Reserved by 00 and defined here:
`h.07.after_conflict` (`conflict_end`, 3), `h.07.affliction_onset` (`interval`, 2), `h.07.fatigue`
(`watch`, 4), `h.07.natural_recovery` (`day`, 3), `h.07.rest_recovery` (the three rests, 3). Added:
`h.07.dying_check` (`turn_end` and `round`, 2), `h.07.lethal_scan` (`scene_start`, `conflict_start`, 7),
`h.07.load_clear` (`scene_end`, 1), `h.07.affliction_day` (`day`, 2), `h.07.curse_cycle` (`week`, 2),
`h.07.vitality_max` (`reflection`, `season`, 9), `h.07.career_end` (`scene_end`, 8). Event boundaries this
chapter marks: `breather`, `rest_short`, `rest_long`, each with `{quality, site, treated}`.

**Clocks created (00.8; templates in `harm.yaml#clock_templates`).** `clk.wound_heavy` (4),
`clk.wound_grievous` (6), `clk.wound_catastrophic` (12), `clk.back_from_the_brink` (4), `clk.bleeding_out`
(4), `clk.captors_intent` (6), `clk.larder` (4), `clk.out_of_their_hands` (6), `clk.cache` (6),
`clk.deaths_debt` (8), `clk.grudge` (6). Every sensed or hidden one carries two omens a stage.

**Conditions and effects contributed.** Six carriers (`cond.wound_arm`, `_leg`, `_body`, `_head`,
`cond.diseased`, `cond.cursed`); seven effects (`eff.07.vitality_max_penalty`, `eff.07.dread`,
`eff.07.maim`, `eff.07.stabilize`, `eff.07.affliction_shift`, `eff.07.rest_cap`, `eff.07.block_restore`).

**Runtime capabilities assumed (00.14.1).** RC-STORE (clamped quantities, write history, the refusal of
`harm_state.dead` without both keys); RC-EVAL (the receiver's side of the pass); RC-RNG (dying, stage and
dread checks, sites, draws); RC-SCHED (rests as marked boundaries with a payload, the daily pass,
cadences); RC-SEAL (a warning's sealed source; curse lifts); RC-LOG (`lethal_refused`, setbacks, the
chronicle); RC-RETRIEVE (trigger-loaded cards for the warning, the exits card and the menu); RC-AUDIT
(narration held to descriptors, wound names and the absence of death).

---

## Interface requests

### Requests made of this chapter, and where each is answered

| From | Request | Answer |
|---|---|---|
| orchestrator (DL-00-04) | PC maximum Vitality = creation value + 2 × (power_band − 1), cap 24; 07 owns the text and the recompute handler | 07.1.2; `h.07.vitality_max` (`reflection`, `season`, phase 9, and on any wound change); current rises with a band rise |
| 01 | `apply_harm(lethal: false)` never moves a PC into Dying | 07.2.11 b; PR-07-1 step 7 (non-lethal at load 3 → Down) |
| 01 | `last_chance.yaml` carries `fate_cost` (1–3) | `lc.reprieve`: `min(3, 1 + reprieves_taken)` (07.5.8) |
| 01 | the stabilize DC for first aid | 10 / 15 / 20 by dying step (07.2.7); Moderate (15) for a companion bleeding out and for an NPC |
| 01 | `lethal_context` written before a declaration | 07.3.2–07.3.5: written when the warning is shown, effective after the player's next declaration |
| 05 | emit rest `quality`; `h.07.rest_recovery` before 05's rest handlers | 07.8.1, 07.8.4: quality travels in the boundary payload, so order cannot matter; the `before` request is recorded in `boundaries.07.yaml` and raised to 00 below |
| 05 | `apply_harm(lethal: false, no_reduction: true)` for overdraw; never to 0 | 07.2.1, 07.2.2, 07.2.11 c |
| 05 | confirm `cond.exhausted` | 07.8.10: intensify, 3 stacks, −1 a stack, slowed at 3; removal by long rest (T-07-14) |
| 05 | define *stabilized* | 07.2.8; `eff.07.stabilize` |
| 05 | does mundane treatment count toward the healing cap? | No: Treat restores no Vitality (07.8.9 d). `ab.field_surgeon` does, as 05 assumed. "One recovery step" = 7 clock ticks (07.8.9 e) |
| 05 | staged afflictions as carriers for `rit.lay_curse` and `ab.slow_draught` | `aff.wasting`, `aff.evil_eye`, `aff.grave_bound`; `aff.drowse` |
| 06 | `apply_harm` takes `mode` (lethal, nonlethal) | 07.2.1; 07.2.10 (NPC depth decides dead or Dying); PR-07-1 step 6 |
| 06 | when Retreat is certain and when it is a chase | 07.4.3: the pursuit test; clean, or the player's pick of a chase (escape 6 against pursuit 8) or a rout |
| 06 | may a Windup count as the lethal warning? | Yes: cause `windup` (07.3.3); the blow comes a turn later, so the context is effective for it (07.3.5) |
| 06 | armor 1 / 2 / 3, cap 4; `no_reduction` for bleeding and choking | 07.2.2 (confirmed); the no-reduction list |
| 06 | the real Dying ladder in place of the proxy | 07.2.4–07.2.9; 06's simulation re-run with it: T-07-18 |
| 06 | whether a foe accepts the PC's Yield is 06.11.7; everything after is 07's | 07.4.1–07.4.2, T-07-8, T-07-11 |
| 06 | falls 10 / 20 / 40 / 80 ft = S2 / S3 / S4 / S5 | adopted (07.10.3); 40 ft and more raise the `severity` warning |
| 03 | harm state readable at declaration (the `crisis` flag) | `harm_state`, `dying_step` are plain shown state (07.3.2); every fall also writes `setback.dying_entered` |
| 03 | marks may read `evidence_for_frame` | 07.7.5 |
| 04 | whether the PC was Staggered or Dying in a conflict must be readable (the Taking) | the scene log holds `on_vitality_threshold(zero)` and `on_dying` events with frame ids |
| 04 | Penance uses one S3 cost from 01's menu | no change needed: `cost.harm` at S3 is `apply_harm(S3, lethal: false)` |
| 04 | the lifetime +1 and maims | 07.7.4: the +1 may be spent on a maimed attribute; the mark stays |
| 12 | emit setback facts | 07.6.2: seven `setback.*` facts; PR-07-1, PR-07-5, PR-07-6, PR-07-7, PR-07-12 write them |
| 12 | refine T-12-10's vocabulary | 07.1.1 and `harm.yaml#descriptors` (fresh, worn, bloodied, Staggered, Dying, Down, shaken) |

### What this chapter needs from, or assumes of, other chapters

- **To 00 (proposed amendments).** (1) `apply_harm`'s signature in 00.14.2 #17 gains `lethal`, `mode`,
  `no_reduction`, `periodic`, `dealt`, and returns `wound`, `load`. (2) `Character` gains `wound_load`,
  `down`, `defeated {manner}`, `dread {current, threshold}`, `afflictions`, `reprieves_taken`,
  `watches_awake`; `marks` entries carry `kind`. (3) Rest event boundaries carry a payload `{quality, site,
  treated}` (00.7.2), and handlers may declare `before:` within a phase (05's ordering request; order by
  owner number would otherwise run 05 first). (4) T-00-9 adds the seven handlers of `boundaries.07.yaml`.
  (5) Triggers `trg.lethal_warning`, `trg.danger_notice`, `trg.exits`. (6) Seven effects in
  `effects.07.yaml`, six conditions in `conditions.07.yaml`. (7) Glossary: Staggered and wound as they
  stand; add **wound load**, **brink**, **Down**, **Threshold**, **stabilized**, **lethal frame**, **lethal
  context**, **scar**, **brink mark**, **maim**, **haunt**, **dread** (distinguish: 03's *strain* is
  conduct; `harm.mind.strain` is Vitality harm), **shaken**, **rest site** (haven, camp, rough),
  **treated**, **grit**. (8) SCHEMAS: the optional fields listed in each of this chapter's data headers;
  `harm.yaml` holds many keyed sections beside the seven required. (9) 06.7.6's `defeated(x)` should read
  this chapter's flag: a Dying **PC** is not defeated (07.1.3); a Dying NPC is.
- **To 01.** The dying check, stage checks, dread checks and the Gamble are resisted checks with their
  own degree tables (01.18.3 allows it) and take the fate reroll (01.16.3). The Gamble is a lethal frame
  with an OFFER and no auto-commit. `cost.harm` passes `lethal = frame.lethal`; this chapter re-tests it
  (07.3.6). A rout and a clean Retreat are "certain with cost" (01.4.5). First aid may be re-attempted
  once a round (an exception to 01.4.2 for the Dying only).
- **To 02.** The creation formula for `base` Vitality (10–16), re-evaluated by `h.07.vitality_max` when
  Endurance changes. Dread threshold 8 + Resolve appears on the sheet. A new PC: dread 0, no marks.
- **To 03.** Counted evidence may listen to `on_dying` and `on_stabilize`; a mark is not evidence
  (agreed). Breaking parole and striking the yielded are `conduct.*` events from the facts this chapter
  writes.
- **To 04.** Integration note: `power_band` changes raise maximum Vitality by 2 a band (07.1.2). Marks,
  maims and haunts are readable for staging offers (07.7.5); a calling that embraces one is an offer.
- **To 05.** (a) **Grit** (07.2.5): the push (05.6.7) may be declared as grit: ignore wound status
  penalties for the beat, no reach gained; an integration edit to 05.6.7. (b) Healing abilities stabilize
  the Dying before restoring (07.2.7). (c) `eff.cleanse` naming `cond.poisoned` reads 07.9.6. (d) Curses
  laid by rites name an entry of `afflictions.yaml` and write its `lift`. (e) A licensed poisoner's
  products name affliction ids.
- **To 06.** (a) PR-06-3 step 5 passes `dealt`, `lethal`, `mode`; step 8's "at 0 Vitality: defeat" applies
  to adversaries; a PC at 0 is Staggered and fights on. (b) The Dying state uses `eff.06.fewer_actions`
  (−2, minimum 1) and `cond.prone`. (c) Behavior lists should treat a Dying PC by disposition (07.6.1):
  only `kill` sides attack it. (d) `flag.cornered` should be written when Retreat's ROUTE test is false.
  (e) Time stays in rounds while anyone is Dying. (f) The simulation's proxy is replaced: see T-07-18.
- **To 08.** Armor reduction 1 / 2 / 3 against `harm.physical` from attacks and shaped effects only; total
  reduction from all sources capped at 4. A healer's kit (`item.tool.kit`, uses) is a Precision lever for
  Treat and first aid. Remedies: `item.consumable.remedy` carrying `eff.07.affliction_shift`, specific
  (two stages; named for an affliction or family: bitterwort, feverbark, wyvern-bane) or general (one
  stage). A "valuable" price band for the `rob` row. Replacements for maims (a hook, a brace, a peg, a
  glass eye) as items that narrow a restriction. Sleeping in medium or heavy armor caps a long rest at
  partial. Caches hold item ids; nothing with a signature or bound ability is ever deleted.
- **To 09.** Per archetype or template: `lethal_context` (true for anything that kills);
  `defeat_disposition` from 00's seven, with any switch to `kill` as a recorded behavior change;
  `captive_fate` (trial, sale, sacrifice, interrogation, ransom, labor, the larder); `dread: S1…S4` on
  things that should mark the mind; a listed wound **site** on attacks that always land in one place;
  attack riders that expose to an affliction by id; `can_bargain` on powers. `threat_advisory` *lethal*
  raises the warning and *hard* the danger notice. Templates must not carry "kills outright" effects
  against PCs: such text is read as S5 harm (Edge cases).
- **To 10.** Hazard entries: `lethal_context`, an optional `aftermath` for a PC put Down by them
  (washed downstream, dug out), and whether each is perceived on sight. `place.rest_site` (haven, camp,
  rough) on known places; no encounter check in a haven. `h.10.supply` applies one stack of
  `cond.exhausted` for each day without food or water. Forced marches use 07.8.10's push-on rule.
  Drowning and smoke use 07.10.4.
- **To 11.** Consume `victory_over_pc`, reputation packets from defeats, the belief `pc.dead`, cache
  rumors, and the rout's clock tick (two or three ticks on the returned clock; supply faction goal
  clocks as candidates). The Bargain's vow is a thread with a racing countdown. `lc.road_ends` and the
  fourth break call the retirement procedure with a living character; `lc.last_stand` and a lost Gamble
  call the legacy procedure with a dead one and a legend line. Holds within reach for 07.6.3.
- **To 12.** Out-of-fiction labels `[WARNING]` and `[STATUS]` (T-07-7) beside 12.15's; the menu uses
  `[CHOICE]` with no default. The triggers above are returned by `get_active_triggers`. The claim check
  should fail a turn that owes a warning or a status block and lacks it, and any narration of death
  without `harm_state.dead`. Anchors for the index: 07.4.1, 07.4.3, 07.8.8, 07.10.2 and the five shapes
  listed under Edge cases.
- **To 13 (now the region's seed, 12.16; T-12-16 `ws.req.07_*`) [revision: I-028].** Whether a default bargainer exists in canon (who answers at the door of death); which places
  are consecrated or tended (grave-chill's cure); whether any rite regrows a limb (default: none);
  regional afflictions as an owner-block of `afflictions.yaml` if 00 grants one.
- **To 14.** The codex shows: Vitality and its maximum with what lowers it; the harm state; wounds with
  their clocks; brink; dread *n of threshold* and haunts *n of 3*; afflictions as stage *n of m*; the
  reprieve's current fate cost; lethal contexts in force. Session zero should say in plain words how
  death works here (07.3.1) and that the last-chance menu exists.
- **To 15.** Downtime activities **Convalesce** (07.8.11) and a **solace** activity (dread −2, 07.11.7);
  curse lifts as sealed facts with three clue placements; a scar or maim as a citable snag on disguise;
  ransom negotiation and a captor's audience as social scenes.
- **To 16.** Companion Vitality by template; 07.12 for their fall; loyalty effects of being left behind
  or saved; a companion able to carry one body.

---

## Open empirical questions

Each ships with the default stated in the rules and a named test that would settle it.

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-07-1 | Is a wound load limit of 3 right once chapter 09's real templates and Focus use are in? | 3 (07.2.6) | **T-07-LADDER**: re-run `07-harm-sim.py` on 09's final templates with a Focus-spending policy; targets of T-07-18 (fair: menu ≤ 6 in 100 fighting on, ≤ 3 with an exit; hard ≤ 30 and ≤ 12). If fair exceeds 6, raise the limit to 4 before touching Vitality |
| OEQ-07-2 | Do players read the `[WARNING]` block as a real warning, or does its frequency dull it? | one block per source per scene; two wordings (deadly / means to kill) | **T-07-WARN**: three playtest sessions; count warnings shown, and how often the player changes plan, asks about exits, or names the risk aloud; target ≥ 50% of warnings draw one of those; if below, restrict the full block to `advisory` and `severity` causes and voice the rest in one line |
| OEQ-07-3 | Do players use Yield and Retreat, or fight to the menu? | exits card at Staggered and at Dying | **T-07-EXIT**: over ten Staggered events in live play, the share ending in Yield, Retreat or a chase; target ≥ 40%. If lower, show the exits card at bloodied as well |
| OEQ-07-4 | Is the menu's price felt as loss without ending campaigns? | nine options (T-07-10) | **T-07-MENU**: log every Threshold over twenty sessions: option chosen, and whether the player kept playing the character for three more sessions; targets: no option chosen > 50% of the time; ≥ 70% continue |
| OEQ-07-5 | Is the Gamble too attractive or too deadly at 45% death for a novice? | Endure against Moderate | **T-07-GAMBLE**: T-07-MENU's log: the Gamble should be 10–25% of choices; outside that band move its DC one tier |
| OEQ-07-6 | Does an AI DM strike menu options it should not, or fail to deliver warnings? | strikes need a cited fact; the engine validates | **T-07-STRIKE**: 60 scripted Thresholds × 3 DM runs; strikes outside the closed lists must be 0 after validation; attempted illegal strikes ≤ 5%. **T-07-OMIT**: 60 scripted framings with a true trigger row; warnings narrated with sign and block ≥ 98% |
| OEQ-07-7 | Are rests too generous with Vitality? | T-07-14 | **T-07-DAY**: simulate a venture day of four fair fights with breathers and two short rests, with and without a healer (05's T-05-HEAL in the same run); target: the fourth fight entered at 50–80% of maximum Vitality without a healer |
| OEQ-07-8 | Do recovery clocks keep a wounded character out of play too long for a solo game? | 4 / 6 / 12 with three daily ticks | **T-07-HEAL**: across playtests, days spent with a Heavy or worse wound per venture; target median ≤ 3 in-fiction days, and the player reports the wait as a choice (push on wounded, or pay time), not a wall |
| OEQ-07-9 | Is the dread threshold of 8 + Resolve reached at a meaningful rate? | 07.11.1 | **T-07-DREAD**: simulate 30 sessions with 09's `dread` ratings and the Dying and Threshold rates of T-07-18; target: a first haunt by session 15–40 for an average character, a career's end by dread in under 5% of 60-session campaigns |
| OEQ-07-10 | Does captivity play as a situation or stall as a cell? | three openings, a racing clock | **T-07-CAPTIVE**: five captures in live play; target: the player declares an action that works an opening within three exchanges in at least four of five |
