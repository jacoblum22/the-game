# 06 — Conflict

> This chapter governs every moment in which someone is trying to harm, hold, drive off, capture or
> escape someone else, round by round. It is written for a game with **one player character against
> groups**, played **in text with no map**, and run by an AI. So it does four things other fantasy
> rulesets leave to a human referee's eye. It gives every participant a small fixed budget of actions
> (three for the PC, two for an adversary, none for a companion unless commanded) so that what a turn
> *contains* matters and how many turns a build gets never does. It stores position as a handful of
> named relations (five range bands, engagement links, ten flags) that only one tool may change and that
> narration must name whenever they change. It makes the opposition run itself: adversaries act from
> priority lists, choose targets by a fixed attention rule, announce their heaviest blows a turn ahead,
> and lose heart on a clock the player can see moving. And it treats the fight as one long invitation to
> improvise: sand, chandeliers, rope bridges, an ogre's leg and "ten arrows" each resolve by reaching
> for a named anchor and turning at most two of its knobs. Harm itself, the dying ladder and death are
> chapter 07's; adversary templates and behavior lists are chapter 09's; this chapter is the procedure
> that joins them.

**Reading this chapter.** *Rules* run 06.1–06.15. *Procedures* are PR-06-1…10. *Tables* T-06-1…15 are
mirrored in `data/conflict.yaml` and `data/conditions.yaml`, which are canonical for ids and numbers
(00.1.4 item 5). *Worked examples* follow **Wren** (00's continuous character) through one complete fight
at Sedge Mill (WE-06-1) and eight shorter cases. Numbers this chapter does not own are marked
*(reference; ch.NN owns)*. The Monte-Carlo behind every tuning claim is
`rules/_process/simulation/06-conflict-sim.py`, with its output beside it; its results are reported in
06.10.6 and T-06-13.

---

## Design intent

**Goals served.** Goal 1: in a fight the player will try the wildest things in the whole game, and the
rules must answer each with a fair, legible ruling instead of a menu. Goal 2: fights are where an AI
referee drifts worst: it forgets who stands where, picks targets by whim, softens blows it should land,
lets one sentence do ten things, and loses count of conditions [R4 §3.3 W3, W12; R4 §9 06;
R: https://arxiv.org/abs/2502.19519; R1 §4 T-5].

**The shape, in six commitments.**
1. **A fixed budget that creates decisions.** Three actions and one reaction for the PC (Pathfinder 2e's
   pool, constitution P9); two actions for every adversary (Lancer's deliberately smaller NPC sets);
   none for a companion, who acts only when the PC spends an action to command it (00.17.1 Q8). Costs
   vary by what is done (a heavy weapon's blow costs two; a dash across a field costs two), and repeating
   an attack in one turn is snagged 0 / −2 / −4. Quantity is never difficulty [R1 #7, M-11, M-14;
   R7 §5 Ex.7; R: https://2e.aonprd.com/Rules.aspx?ID=220].
2. **Cadence without extra actions.** Constitution P14 lets groups differ in cadence; P9 forbids
   differing budgets; INV-11 makes the second binding. This chapter puts cadence in three places only:
   what one action contains (weapon weight), who acts before whom (tempo, fed by Wits), and what a
   reaction may be (the defense-reaction slot). DL-06-02.
3. **Position is state, in words.** Range bands from the PC to each participant, engagement links, and
   flags; written only by `set_position`; every change named in narration with fixed words (T-12-11).
   Area effects select over those relations with fixed caps and one priority order, never over
   geometry [R3 #7, §06.2–06.3, §06.14; R1 §06 "positions must be state"].
4. **The opposition runs itself.** The DM never chooses a target, softens a hit, or decides that the
   bandits "would probably" flee. Behavior lists (09), a deterministic attention rule, an engine-rolled
   attack, a windup tell before any Grievous blow, and a morale clock with listed tick sources do that
   work [R4 §6.2 items 1 and 3; R3 §06.8].
5. **One PC must be able to face many.** Body count is the dominant variable for a solo character
   [R1 §06; R2 #11]. Three tools keep crowds playable: adversaries' smaller budget; **mobs** (many
   bodies, one entity, one turn); and morale, which ends most fights before the last foe falls. The
   simulated solo curve (T-06-13) tells chapter 09 what each encounter shape costs.
6. **Every exit is a rule.** Yield, Retreat, a foe's surrender, a rout, a parley and a chase are named
   procedures with clocks, because "defeat usually means capture, loss or a changed situation" is only
   true if leaving a fight is as well-specified as winning it [BRIEF §4; R6 §C.3 C-R4; R3 §06.10].

**What this chapter deliberately avoids.**
- A grid, distances in feet, facing, or cones measured in degrees.
- Harm dice, hit locations as a default, or armor as a second defense number (armor reduces harm; 07/08).
- Any way for a build, calling, item or effect to take more actions (INV-11).
- Hidden difficulty adjustment. Mid-fight changes come only from logged world events: reinforcements on
  a clock, morale, a retreat [R1 §4 T-5].
- Random target choice by the narrator, in either direction.
- Death by one roll. A blow of base S4 or more is announced one turn before it can land (06.9.5); death
  itself needs chapter 07's two keys (INV-6).

**How to read the kinds.** Almost everything here is `[D]`: the engine holds the budget, the order, the
bands, the conditions and the clocks. The DM's judgments are narrow: which anchor a wild action
resembles (`[J:enum]`), whether a fact is established (`[J:flag]`), which rung an improvised object
sits on (`[J:rung]`). Each carries its worst case.

---

## Rules

Rule ids are `06.S.R`. Citations per 00.1.6. "The PC" means the player character; "an adversary" means
any hostile non-player participant; "a companion" means a ch.16 companion, hireling or follower, a
summoned servant, a raised dead or an automaton fighting on the PC's side.

### 06.1 The action economy

**06.1.1 The budget.** `[D]` In `conflict` mode (00.7.3) time runs in **rounds** of six seconds. In each
round every participant able to act takes one **turn**, in tempo order (06.2). On its turn a
participant has a budget of **actions**; between its turns it has **reactions**.

| Participant | Actions per turn | Reactions per round | Source |
|---|---|---|---|
| The PC | **3** | **1** | this rule [C:P9] |
| An adversary or hostile NPC (any threat band) | **2** | by band: T1 none; T2 and above 1 (06.6.5; 09 may set `reaction: false`) | [R1 M-14 Lancer] |
| A mob or swarm (06.10), whatever its size | **2** (one entity) | 0 | 06.10.2 |
| A companion | **0**: it acts only when the PC spends an action to command it (06.14) | **1** | 00.17.1 Q8 |
| A bystander or neutral NPC | acts through ch.12's world-response step (12.2.9 item 2), outside this budget | 0 | — |

Unused actions are lost at the end of the turn. A reaction refreshes at the start of the owner's turn.
A turn is also the unit of one declaration: the PC declares up to three beats, one per action spent
(01.2.3), and they resolve in order through chapter 01's pipeline. *Narration may not imply* an act that
no action or reaction paid for.

**06.1.2 Nothing adds actions.** `[D]` No calling, ability, item, condition, composite, rite, boon, fate
spend, Focus spend or ruling gives any participant a fourth action, a second turn in a round, or an
action outside its turn (INV-11). The only economy effects that exist are:
- **fewer actions** (`eff.06.fewer_actions`: `cond.dazed`, `cond.stunned`, `cond.surprised`);
- **one more reaction**, by `eff.reaction_grant`, only from a stance, a calling capability or an
  ability of the Exception form, and never above **two reactions per round** in total;
- **a different reaction** (06.6.4, the defense-reaction slot).
An adversary's budget of two is its base, fixed by this rule for every threat band; chapter 09 may not
raise it for any template (a lone ogre is dangerous through what its two actions contain, 06.9.5).
[C:P9; R1 §06 "extra bodies are the failure point"; DL-06-01]

**06.1.3 What an action buys.** `[D]` [DL-06-01; C:P9; revision: I-065] One action buys **one beat of one basic verb**, or one beat of
an ability whose timing is `beat` (05.3.4), unless T-06-1 lists a different cost. Costs are atomic: an
activity that costs two actions must be paid within one turn. The DM never sets a cost; the anchor
card's `action_cost` knob may be moved only to a value T-06-1 lists for that verb (00.2.7).

**T-06-1 Action costs.** (`data/conflict.yaml#economy.action_costs`)

| What | Cost | Notes |
|---|---|---|
| **Move** one step between adjacent bands: engaged↔close, close↔near | 1 | leaving `band.engaged` this way provokes (06.6.2) |
| **Move** near↔far (a dash) | 2 | |
| **Move** far↔distant | 3 | usually the start of a chase (06.12) |
| **Withdraw**: engaged→close, guarded | 1 | provokes nothing; cannot be combined with any other band change in the same action |
| **Stand** from `cond.prone`; **mount** or **dismount** | 1 | |
| **Strike** with an unarmed blow, a light or one-handed weapon, a bow or a sling | 1 | T-06-6 |
| **Strike** with a heavy weapon | 2 | counts as one attack for repetition (06.1.6) |
| **Reload** a light crossbow / a heavy crossbow | 1 / 2 | writes `<weapon>.loaded = true` (06.4.9); bows and slings reload inside the Strike |
| **Grapple**, **Force** (shove, trip, break), **Exert** (climb, leap, swing), **Sneak** (hide), **Handle** (use, light, tie, bandage), **Setup**, **Observe** (search, study a foe), **Recall**, **Evade** (take cover) | 1 each | Force against a Hard or sturdier object: one interval, not one action (01.18.10) |
| **Talk** as a beat (intimidate, taunt, demand surrender, parley, command a stranger) | 1 | a few words are free (00.12.6) |
| **Defend** (06.1.5) | 1 | |
| **Flank** (T-06-4), **Screen** an ally (06.3.5), turn to clear `flag.flanked` | 1 each | named uses of Move; no roll |
| **Aim** (06.5.9) | 1 | |
| **Command** a companion (06.14) | 1 | 2 for a companion beat that itself costs 2 |
| **Ready** (06.6.6) | 1, plus the reaction when it fires | the readied beat must cost 1 |
| **Help** (01.14.8) | 1 of the helper's | a companion's Help is bought with Command |
| An ability with timing `beat` | the cost of its `check.verb` in this table | 05.3.4 |
| An ability with timing `rider`, a flare, a push, an OFFER trade | 0 | they ride a beat that was paid for |
| A resisted check (Endure, Evade against an effect DC) | 0 | it is not a declared beat (00.3.3) |
| **Break free** of a hold | 1 | Grapple, 06.5.2 |
| Recover footing (end `cond.off_balance`), beat out flames (end `cond.burning`), staunch a wound (end `cond.bleeding`) | 1 each | Handle; no roll unless something opposes it |

**06.1.4 Free activities in a conflict.** `[D]` [DL-00A-19; DL-06-01; revision: I-065] These cost no action and never roll (00.12.6 applied to
rounds): speaking a sentence; dropping what is held; releasing a hold; ending a stance, an aura or a
sustained working of one's own; **one free handling per turn** (draw, stow, pick up or pass one
unattended item; a second in the same turn costs an action); looking around (passive noticing, 01.4.6);
asking the DM an out-of-fiction question, including "what would it take?" (01.7.1), which runs
GATE→FRAME→OFFER and spends nothing; **Yield** (06.11.7), which may be declared at any moment,
including in answer to an attack's announcement.

**06.1.5 Defend.** `[D]` [DL-06-22; DL-12-26; revision: I-065] *Anchor: yes (below).* **Defend** is a named use of `verb.evade` that costs one
action and does not roll: the actor gives its attention to not being hit. It writes the fact
`defending.<actor>` until the start of the actor's next turn. While the fact stands, **every aimed attack
against the actor carries one engine-applied Precision snag (−2)** citing it. The snag is outside the
two-cited-snag count and inside the ±4 cap, exactly like a repetition snag (00.3.9 g). Defend does not
stack with itself, ends at once if the actor becomes `cond.stunned` or `cond.unconscious`, and does
stack with Fend (06.6.3), to the cap.
- *Anchor.* Intent verbs: guard, parry everything, keep my shield up, fight defensively, hold them off.
  Knobs: `action_cost` (1 → 2: **Full defense**, which also gives the actor `flag.in_cover` against
  ranged attacks if it holds a shield or stands at a named cover feature); `targets` (self → self and one
  engaged ally, a knob change: the snag then applies to attacks on either, and the actor may not
  Strike this turn). Covers: making oneself harder to hit. Does not cover: reducing harm already rolled
  (that is a defense reaction, 06.6.4) or avoiding an area effect (a resisted Evade, free).
- *Simulated worth:* against one foe of the PC's band, replacing the third Strike with Defend loses the
  fight slightly more often (T-06-14: 99.4% against 99.7% at P3 against T3); against three or more
  attackers it prevents more harm than the third Strike deals. It is a real choice, not a default.

**06.1.6 Repeated attacks.** `[D]` [DL-06-03; C:P9; revision: I-065] This chapter adopts chapter 01's repetition shape unchanged
(01.14.3; DL-06-03). Within one **turn**, an actor's k-th beat bearing `trait.action.attack` carries
engine-applied Precision snags:

| Attack this turn | 1st | 2nd | 3rd |
|---|---|---|---|
| Snag on the roll | 0 | −2 | −4 |

(`data/conflict.yaml#repeated_attack`.) Rules: (a) every attack-trait beat counts, whatever its verb or
target: Strike, Grapple, a harmful Force, a Setup that hinders a creature, an aimed working; (b) a heavy
weapon's two-action Strike is one attack; (c) an attack made as a **reaction** is outside the window: it
carries no snag and does not count; (d) each commanded companion keeps its own window per PC turn; (e)
the snags sit inside the ±4 circumstance cap, so levers offset them and a snagged third attack against a
target in cover is no worse than −4; (f) **quantity never changes the DC** (01.14.3). "I fire ten arrows"
is throttled to the actions available (three, or two and a Move) and each shot rolls against the same
Guard. *Arithmetic:* Wren (+5) at Guard 15 hits on 10, 12, 14: 55%, 45%, 35%; at least one hit 84%
(WE-06-2).

**06.1.7 P9 and P14 together: where cadence lives.** `[D]` [DL-06-02; C:P14; revision: I-065] A calling group may feel faster or heavier
than another only through these three channels, each of which leaves the budget untouched (INV-11;
00.17.1 Q21; DL-06-02):

| Channel | What differs | Where it is set |
|---|---|---|
| **What one action contains** | weapon weight: a light or one-handed weapon gives up to three Moderate blows a turn; a heavy weapon gives one Heavy blow and one spare action (T-06-6). Riders, flares and the push change what a single beat delivers (05.3.4, 05.6.7–05.6.8) | this chapter; 05; 08 |
| **Tempo** | who acts before whom: the tempo check (06.2.2) reads Wits and competence in `deed.martial.tactics.reading`; edges on it come only through `eff.check_edge` | this chapter; 04/05 data |
| **Reactions** | which defense reaction a character has (06.6.4), and whether a stance grants a second reaction (06.1.2) | this chapter; 05 data |

No fourth channel exists. A proposed ability that would "act twice", "attack as a free action" or "take
an extra turn" is not an ability of this game (05.3.2's closed forms have no place for it).

**06.1.8 The turn.** `[D]` + `[T]` [DL-06-01; R5 CF-02; revision: I-065] Each turn has three parts, run by handler `h.06.turn_effects`:
1. **Start** (`turn_start`): the owner's reaction refreshes; `on_turn_start` subscribers fire; a
   readied beat that has not fired lapses (01.14.10); conditions whose `periodic` names `turn_start`
   apply; `defending.<actor>` and Fend facts of the owner expire.
2. **Actions**: the budget is spent beat by beat. The PC's beats pass through the full pipeline with an
   OFFER each (01.7), subject to the player's `auto_commit` preference; an adversary's are engine
   frames (06.9.2).
3. **End** (`turn_end`): conditions whose `periodic` names `turn_end` apply (bleeding, burning,
   choking); durations counted in the owner's turns tick down ("until the end of its next turn" is
   `rounds:1` measured here); `on_turn_end` subscribers fire; `cond.frightened` decays one rung.

### 06.2 Starting a conflict, tempo, and surprise

**06.2.1 When a conflict starts.** `[T]` + `[D]` [DL-00A-12; R5 CF-01; revision: I-065] `conflict_start` is marked, and the time mode becomes
`conflict` (12's T-12-3), at the first of: an adversary's behavior list yields an attack; the PC
declares a beat with `trait.action.attack` against a creature that will resist; a hostile NPC action
result says "attacks"; a clock completion creates an attacking encounter. At that instant the engine
(PR-06-1): lists the **participants** and their **sides**; records each side's **objective** (06.13.2);
sets every participant's band to the PC and flags from the scene's established positions (06.3.9);
creates the opposing side's **morale clock** (06.11.2); marks who is `cond.surprised` (06.2.4); and runs
the tempo check. The narration of the opening must state each participant's band to the PC and every
flag on the PC (12.14.6).
**The attack roll states whether it starts the fight** `[D]` [revision: R2-M2; DL-06-42] With tools, every attack roll
(Strike, Grapple, Force) at an able creature or person carries a field: *starts the fight*, yes or no, and the start
band. Left blank with no fight on: the fight starts, at the default band, logged `not_chosen:fight.starts` (and
`not_chosen:fight.to` for the band). With a fight already on, the field is ignored. The DM may still start a fight any
other way, whenever it likes (an ambush, a foe striking first), with `change fight`. Code never decides that a fight
began from the words of a beat, only from this field, the tool, or its logged default (constitution VIII.9). Default
start band by the chosen verb and weapon ids: `band.engaged` for a Grapple, a Force or a melee Strike; the weapon's
first band (T-06-6) for a ranged Strike.

**06.2.2 Tempo.** `[D]` Handler `h.06.tempo_setup`. Tempo is the one value Wits derives (00.4.4).
- Each adversary has a static **tempo DC** = `10 + Wits + competence(deed.martial.tactics.reading or
  an ancestor) + edge + status` (chapter 09 stores it as `tempo`; reference by band T1…T5: 10, 11, 12,
  13, 14).
- The PC makes **one tempo check**: `d20 + Wits + competence(deed.martial.tactics.reading or an
  ancestor; the floor applies) + edge + status`. It is a frame with stakes Safe, no cost, and
  `offer.choice: auto`. The **same total is compared to every adversary's tempo DC**.
- **Order within every round of this conflict:** adversaries whose tempo DC is **greater than** the
  PC's total act first, highest DC first; then the PC; then the remaining adversaries, highest DC
  first. Ties among adversaries: the one nearer the PC by band first, then by id.
- A **natural 20** places the PC first whatever the totals and gives the fact `tempo.seized` (a
  Precision lever on the PC's first beat). A **natural 1** places the PC last and gives no lever to
  anyone.
- Members of one mob act on the mob's turn. A companion has no place in the order (06.14).
- The order is fixed for the conflict except by **Delay** (below), surprise (06.2.4), and arrivals: a
  participant who joins later is placed by comparing its tempo DC to the PC's recorded total.
- **Delay.** On its turn, before spending any action, the PC may move its turn to immediately after
  any later participant; the new place holds for the rest of the conflict. Adversaries delay only
  when a behavior row says so.
*Why one roll.* The acting side rolls once (00.3.3); a roll per participant would be six rolls of
bookkeeping before anyone acts, and side-based order would make Wits matter only on round one. One
total against several static DCs interleaves the PC among foes at the cost of one die
[R: https://2e.aonprd.com/Rules.aspx?ID=2423 (initiative from Perception); R: https://troikasrd.ttrpg.tools/the-rules/05-initiative/ (considered and rejected: a token bag is randomness the player cannot plan around); R3 §06.5; DL-06-04].

**06.2.3 Rounds.** `[D]` [DL-00A-12; R5 CF-01; revision: I-065] When the last participant in the order has finished its turn, the `round`
boundary fires (00.7.5): `h.00.durations` (1), `h.06.ongoing_harm` (2: periodic effects of the *place*,
not of a bearer: a burning room, rising water), `h.05.round_recharge` (3), `h.00.clock_auto` (5: morale
clocks' and chase clocks' automatic rows, reinforcement countdowns), `h.06.chase_round` (5),
`h.06.diminishing_window` (9), `h.06.objective_check` (9: the end test of 06.13.1). Then the next round
begins with the same order.

**06.2.4 Surprise.** `[D]` + `[J:flag]`
```
Trigger [T]:        conflict_start
Loads in:           situation.conflict
License check:      —
Decisions (J):      1. UNAWARE [J:flag], per participant: "At the instant the conflict began, was this
                       participant unaware of every enemy who then acted against it?" True only when
                       state says so: its alertness toward them is `unaware` (15), or every such enemy
                       held flag.hidden toward it, or it was cond.unconscious. False when it had been
                       told, had perceived them by a resolved Observe or passive notice (01.4.6), or
                       the enemies had been talking with it. Uncertain -> false (no surprise).
Computation [D]:    each participant for whom it is true gains cond.surprised (T-06-10): it acts after
                    every unsurprised participant in round 1 whatever its tempo; it has ONE action on
                    its first turn; it has no reaction until that turn ends; attackers hold a Precision
                    lever against it (the condition grants it). The condition ends at the end of its
                    first turn. Passive noticing is the engine's comparison of stored Sneak totals with
                    notice (01.4.6), run BEFORE conflict_start, so surprise is settled by state.
Stakes:             —
State writes:       condition instances; round-1 order
Narration may not imply: that a surprised participant acted before the ambush landed
Worst case (J):     one participant wrongly surprised or wrongly ready: at most two of its actions and
                    one lever, for one round (class i). The flag cites the alertness fact or the hidden
                    flag, so it is auditable.
Examples:           inside: Wren, flag.hidden in the loft, looses at a sentry whose alertness is
                    `unaware` -> the sentry is surprised. outside: the same sentry heard the stair
                    creak (alertness `suspicious`) -> not surprised; hidden still gives Wren her lever
                    (06.3.6) but the sentry acts on its tempo with full actions.
                    non-example: "I attack first, so they're surprised" -> speed is tempo's business;
                    surprise needs unawareness in state.
Anchor:             no
Basis:              [R5 CF-01] [R: https://2e.aonprd.com/Rules.aspx?ID=2541 (unnoticed foes at the start of an encounter)] [BRIEF §4 lethality] [DL-06-05]
```
A surprised PC always keeps the free activities of 06.1.4, including Yield. Being surprised is
survivable by construction: a P1 character ambushed by two T2 foes faces at most four attacks before
acting, expected harm about 5 to 8 of 12 Vitality by her armor *(reference lines, T-06-12)*: bloodied,
not down.

**06.2.5 Leaving and joining.** `[D]` [DL-00A-20; R5 CF-01; revision: I-065] A participant leaves the conflict when it is defeated (06.13.3),
when its band to every enemy is `band.distant` and no chase clock involves it, or when it yields and
the yield is accepted. Reinforcements enter only through a clock whose omens were rendered (INV-14) or
a behavior row "call for help" that names who can hear; they enter at the band the clock's template
states (default `band.far`).

### 06.3 Position: bands, engagement, and flags

**06.3.1 Position is relationship-state.** `[D]` [DL-06-07; C:IV; C:P3; C:P13; revision: I-065] In a conflict, position is exactly this state and
nothing else (00.6.1 `position`; 00.17.1 Q14):
- for every participant other than the PC, one **range band to the PC** (`band.*`, five rungs);
- a set of **engagement links** between pairs of participants;
- per participant, an optional **group** label (a named spot or formation: "the gallery", "the three
  at the door"), default `main`;
- per participant, a set of **positional flags** (`flag.*`, T-06-4);
- the scene's **features** (06.3.8), each an entity.

It is written **only by `set_position`** (tool #13), called by a resolved Move, by a maneuver's
delivered reach, by a cost (`cost.footing`), by an effect of operation `move`, or by this chapter's `[T]`
rules. Narration never moves anyone. **Every change of a band, link or flag that involves the PC is named
in that turn's narration in the fixed words of T-12-11** (12.14.6; INV-2), and a change among others is
named when the PC could perceive it. The claim-versus-state check treats an unnamed change, or a named
one the store does not hold, as an error of class `position`.

**06.3.2 The five range bands.** `[D]` [DL-06-07; revision: I-065] (`data/conflict.yaml#range_bands`.) Bands are relations, not
distances; the measures are for the narrator's sense of scale only (12.14.6 item 3).

| Band | In words (T-12-11) | True only when | What it allows between the two | Rough scale |
|---|---|---|---|---|
| `band.engaged` | at blade's reach; locked together | an engagement link joins them (06.3.5) | melee Strikes, Grapple, Force, touch effects, taking things from each other; ranged Strikes are snagged (06.4.7) | arm's and weapon's reach |
| `band.close` | a few strides off; a lunge away | one Move step from engaged | reach weapons' Strikes; thrown weapons with no snag; any ranged Strike; speech in a low voice | up to about 5 paces |
| `band.near` | across the room; a stone's throw | two Move steps from engaged | thrown weapons with a snag; bows, slings, crossbows; spoken words; most workings name this band | up to about 20 paces |
| `band.far` | a long bowshot; across the field | a dash beyond near | longbows and crossbows; short bows and slings with a snag; shouting | up to about 100 paces |
| `band.distant` | at the edge of sight; far beyond reach | beyond far | nothing aimed reaches; signals and sight only. A participant distant from every enemy is out of the fight (06.2.5) | beyond that |

*Worst case of a one-band error at scene framing* (`[J:rung]`, 06.3.9): one action's worth of movement,
or one range snag (class i), visible in the first OFFER.

**06.3.3 Moving.** `[D]` [DL-06-07; revision: I-065] A Move beat (01.18.4) names a **destination**: *toward* a participant or
feature, *away from* one, or *to* a named feature. Its delivered reach of 2 or more changes the mover's
band to the destination's holder **by the one transition paid for** (T-06-1), symmetric for both
parties.
- **Unopposed** movement over passable ground is Trivial: no roll (01.4.1), still an action.
- **Opposed** movement (past a blocker, through a foe's space, out of a hold) rolls per the Move card.
- **Others.** Participants in the **same group** as the destination change with it. Every other band
  stays as it was, unless an established fact puts that participant on the path or behind the mover
  (`[J:flag]`: *"Does a recorded feature or group place this participant between the mover and the
  destination, or directly behind the mover?"* True → its band shifts one step the same way or the
  opposite way respectively; uncertain → unchanged). *Worst case:* one participant one band off
  (class i).
- **Engagement.** Moving away from an engaged enemy by a plain Move provokes that enemy's Opportunity
  Strike (06.6.2) and breaks the link. Withdraw breaks the link and provokes nothing. Moving to
  `band.engaged` with a participant creates the link, if its capacity allows (06.3.5).
- **Pace.** The quantity `speed` (T-00-13) is **pace**: 1 by default. Pace 2 (a mount, a wolf, a
  running hare) halves each transition's cost, rounded up (1, 1, 1, 2). `cond.slowed` and difficult
  ground (a feature fact) each add 1 action to every transition; `cond.prone` adds 1 and forbids
  crossing more than one band a turn.
- **Narration.** "You close with the reeve: you are at blade's reach. The archer on the gallery is
  still across the room, above you."

**06.3.4 Bands between two participants who are not the PC.** `[D]` [DL-06-07; revision: I-065] Needed for area effects,
companions and adversaries who target companions. First match:
1. an engagement link joins them → `band.engaged`;
2. they share a group → `band.close`;
3. otherwise → the farther of their two bands to the PC, and never nearer than `band.near`.
A companion standing with the PC (the default) is in the PC's own group: its band to any adversary is
the PC's band to that adversary, except that an engagement link is always per pair.

**06.3.5 Engagement.** `[D]` [DL-06-07; revision: I-065]
- A link forms when a Move, a Grapple, a charge or an effect brings two enemies to `band.engaged`, and
  breaks when either leaves, is moved, or is defeated.
- **Capacity.** At most **four** enemies of the target's own size may be engaged with one target at
  once; **two** when the target holds `flag.in_chokepoint`; each size step by which the target is
  larger adds two; a mob counts as its current members, to the capacity.
- **Screening.** A participant engaged with nobody may spend one action to **screen** one ally in its
  group (a named use of Move; no roll): until it moves or falls, an enemy that Moves to engage the
  screened ally must first get past the screener (a Move opposed by the screener's Might or Agility
  defense, whichever is higher) or accept the screener's Opportunity Strike and stop engaged with the
  screener instead.
- Being engaged with an enemy is the fact `engaged.<a>.<b>`; abilities and behaviors read it.

**06.3.6 The positional flags.** `[D]` [DL-06-07; revision: I-065] (`data/conflict.yaml#positional_flags`.) Seven are reserved by
00; this chapter adds three (`flag.obscured`, `flag.in_chokepoint`, `flag.aloft`; DL-06-07). Each flag
is carried by one participant, is set and cleared only as listed, and does only what is listed. Lever
and snag effects are **engine-cited**: they count toward the two-lever or two-snag limit of the roll
they touch and sit inside the ±4 cap (00.3.9).

**T-06-4 Positional flags.**

| Flag (words) | Carried by one who… | Set by | Cleared by | Effect |
|---|---|---|---|---|
| `flag.flanked` (caught between them) | is engaged with two or more enemies, at least one of which has taken the **Flank** action | Flank: an enemy engaged with the target, while an ally of that enemy is also engaged with it, spends 1 action (a Move, no roll) | the carrier ends a turn engaged with fewer than two enemies; or spends 1 action to turn and reset (clears it until someone Flanks again); or gains `flag.in_chokepoint` | enemies' melee attacks against the carrier hold a **Precision lever**. A mob never needs it and never grants it (06.10.3) |
| `flag.cornered` (your back to the wall) | has no band to withdraw into | a completed pursuit clock (06.12.4); `cost.footing` S3; a foe's Force or Move that delivers it; scene framing when a feature fact says so | a Move through an enemy (opposed), a Force that moves an enemy, or a new exit established (Oracle or Handle) | the carrier cannot Withdraw, Retreat, or increase its band to any enemy engaged with it. A cornered adversary whose side breaks cannot flee (06.11.5). Talk demanding its surrender holds a Precision lever |
| `flag.in_cover` (behind *the cover named*) | has put a named cover feature between itself and enemies not engaged with it | Evade "take cover" (reach 2+); Move reach 3+; Full defense with a shield; a stance or ability | the carrier Moves (other than along the cover), makes a melee Strike, or the feature is destroyed; an enemy that reaches `band.engaged` ignores it | **ranged** attacks against the carrier take a **Precision snag**; the carrier's Evade against an area effect from the far side holds a Protective lever; the carrier may Sneak to hide while watched (06.3.7) |
| `flag.elevated` (above them: *the height named*) | stands on a named height feature above its enemies | Move or Exert onto the feature | leaving it; being shoved off (Force reach 2+ → a fall, 06.5.8) | the carrier's attacks against lower enemies hold a **Precision lever**; enemies must spend 1 extra action (a climb, Exert) to reach `band.engaged` unless a stair or ramp is named; melee attacks from below without a reach weapon take a Precision snag |
| `flag.hidden` (unseen) | no enemy knows its position | Sneak reach 3+ (01.18.13), when cover, `flag.obscured` or darkness makes hiding possible (06.3.7); scene framing | any beat of the carrier with `trait.sense.visible` or `.loud` other than a Sneak (so: after its first attack resolves); `cost.exposure` S3+; an enemy's Observe that beats the stored Sneak total | enemies cannot target the carrier with aimed beats (G4: they may Observe to search, 1 action, or attack the place they suspect at two snags); the carrier's first attack holds a **Precision lever** and its target has no reaction to it. Grounds `deed.guile.ambush` evidence (03.1.7) |
| `flag.mounted` (in the saddle) | rides a mount or has climbed onto a larger creature | the Mount action; Grapple reach 2+ on a creature at least one size step larger (01.18.9) | Dismount; being unhorsed (Force or Grapple reach 2+ against the rider; the mount defeated) | 06.15: the rider moves at the mount's pace; `flag.elevated` against enemies on foot of its own size or smaller; grounds `deed.martial.mounted` evidence |
| `flag.lined_up` (strung out in a line) | stands in file with at least one other carrier, as seen from an attacker | a feature fact (a corridor, a bridge, a stair, a ford) at framing; a column of march; a Setup or Move that draws enemies into a line (delivered reach 2+) | the carrier leaves the feature or the file breaks (any carrier Moves sideways: 1 action) | the `pierce` spread selects carriers, nearest first (06.8); at most **one** carrier of a line may be engaged with a target at the line's head |
| `flag.obscured` (half-seen: *the smoke, the dark, the mist named*) | is veiled by darkness, smoke, fog, rain, foliage or dust that does not stop a blow | a feature or scene fact (`light: dark` gives it to everyone for observers without a light or night-sight); a Handle or Force that raises smoke or dust; an effect | leaving the veil; the veil ending; a light brought to bear | aimed attacks against the carrier **that rely on sight** take a **Precision snag**; the carrier may Sneak to hide. Concealment is not cover: it never helps an Evade |
| `flag.in_chokepoint` (holding the gap: *the door, the bridge named*) | stands in a named gap only two can reach at once | Move to a chokepoint feature (no roll if unopposed) | leaving it; being pushed out (Force reach 2+); the feature destroyed | engagement capacity 2 (06.3.5); the carrier cannot be `flag.flanked`; enemies beyond it gain `flag.lined_up` if they queue to reach it |
| `flag.aloft` (in the air above) | flies or hovers out of reach of the ground | a `slot.movement_mode` claim of mode `fly`; a creature's template (09) | landing; `cond.prone`, `restrained`, `stunned` or `unconscious` (it falls, 06.5.8) | cannot be engaged or struck in melee from the ground (G4; ranged, reach from a height, or a leap by Exert remain); it may engage by descending (a Move); it ignores ground features |

Two general rules: **(a)** one fact, one lever (00.3.9 d): a flag gives its effect once per roll however
many enemies share it; **(b)** when two flags apply to one roll in opposite directions (the attacker is
elevated, the target in cover), both are cited and they sum inside the cap.

**06.3.7 Cover, concealment and hiding.** `[D]` + `[J:flag]` [DL-06-07; R5 CF-11; C:VII; revision: I-065]
- **Cover** is a solid thing that could stop the blow: it is a *feature* (06.3.8), and `flag.in_cover`
  is the state of using it. **Total cover** (no line at all: around the corner, behind a shut door) is
  the fact `no_line.<a>.<b>`: aimed beats between the two are G4 until someone moves.
- **Concealment** stops sight, not blows: `flag.obscured`.
- **Hiding** needs one of: cover, `flag.obscured`, or an enemy's attention established elsewhere
  (`cond.distracted`, alertness below `alert`). `[J:flag]` *"Is there a recorded cover feature, veil or
  distraction between this actor and every enemy who could see it?"* True → the Sneak may be
  attempted (against the highest notice among them, 01.18.13); false → G4 for hiding, with the
  redirect "get behind something first". Uncertain → false. *Worst case (J):* a hide attempt wrongly
  allowed still has to succeed against notice, and yields one lever on one attack (class i).
- **Darkness.** `scene.light` is `bright`, `dim` or `dark` (ch.10 owns light sources). Dim: everyone
  beyond `band.close` is `flag.obscured` to observers without night-sight. Dark: everyone not in a
  light is; an observer with no light and no night-sight is `cond.blinded` for sight-reliant beats.

**06.3.8 Features: the ground is part of the fight.** `[J:enum]` + `[D]` [DL-06-11; C:III; revision: I-065] Anything in the scene a
participant could use, hide behind, fall off, set alight or drop on someone is a **feature**: an entity
(kind `object` or `place`) written on mention (00.6.6) with a `feature_kind` from this closed list. The
kind fixes what the feature does, so an improvised use is a lookup (06.5.10, T-06-9).

| `feature_kind` | True only when it is… | It enables |
|---|---|---|
| `cover` | a solid thing a body can get behind (a pillar, an overturned table, a wagon, a low wall) | `flag.in_cover`; hiding; it has a Force tier and can be broken or pushed |
| `height` | a place above the floor one can stand on (a gallery, a wagon bed, a boulder, a stair head); records its drop in feet | `flag.elevated`; falls (06.5.8) |
| `chokepoint` | a gap two abreast or narrower (a door, a bridge, a stair, an alley mouth) | `flag.in_chokepoint`; `flag.lined_up` for those queuing |
| `hazard` | a thing that harms what enters or touches it (a fire, a drop, deep water, a pit, a mill wheel); a ch.10 hazard entry with severity | Force and Grapple into it; `cost.footing` S4; periodic harm by `h.06.ongoing_harm` |
| `difficult_ground` | footing that slows (mud, rubble, ice, a crowd, knee-deep water) | +1 action per transition across it; a snag on Exert and on Moves opposed there |
| `veil` | something that hides without stopping (smoke, mist, darkness, tall grain, hanging cloth) | `flag.obscured`; hiding |
| `loose_object` | a thing that can be thrown, dropped, toppled, swung on or pulled (a chandelier on a rope, a stack of barrels, a rug, a brazier, a hanging chain); records its size rung (T-06-8) | improvised weapons; dropped-object Strikes; Exert swings; Force topples |
| `barrier` | a thing that can be shut, barred or dropped to stop passage (a door, a portcullis, a gate) | `no_line` and blocked Moves when shut; Handle to shut, Force to break |

*Decision* `[J:enum]`: when narration introduces something usable, the DM classifies it once (default
when uncertain between two kinds: the first in this table's order; a thing honestly of two kinds, such
as an overturned brazier that is `hazard` and `veil`, is written as two features). *Worst case (J):* a
feature classified as the neighboring kind gives the neighboring kind's single effect (class i), and
the classification is a stored fact the player can question. A feature the scene would plausibly hold
but narration has not established ("surely there's a chandelier") is a G0 question for the Oracle
(00.12.7), asked **before** the frame, never granted by the asking (SG-06).

**06.3.9 Framing positions at the start.** `[J:rung]` + `[D]` [DL-06-07; R5 CF-03; revision: I-065] At `conflict_start` the DM **states** each
participant's band to the PC [revision: R2-M; DL-06-41] (with tools: `change fight` with `to`, and `change position`
for anyone placed otherwise; code never reads a band from the scene's words, constitution VIII.9), guided by what the
scene has established: a participant the PC was speaking
with at arm's length is `band.engaged` only if a weapon was already at a throat, else `band.close`;
someone across a room is `near`; someone across a field or on a far wall is `far`. Default when
the DM states none [revision: R2-M2; DL-06-42]: for a fight started by an attack roll, the band of the attack's own
default (06.2.1: `band.engaged` for a Grapple, a Force or a melee Strike; the weapon's first band for a ranged
Strike); for a fight started by `change fight` alone, `band.near`; each logged (`not_chosen:fight.to`). Flags are set only from recorded facts (a participant on a gallery feature
gets `flag.elevated`). *Worst case (J):* one band (class i).

**06.3.10 Size.** `[D]` [DL-06-30; C:VII; revision: I-065] Every creature has a **size** from a six-rung ladder stored in its template
(09; a PC is `medium`): `tiny` · `small` · `medium` · `large` · `huge` · `colossal`. The DM never picks
a size in play. A **size step** is one rung. Size does five things (`data/conflict.yaml#sizes`):

| Where | Rule |
|---|---|
| Grapple, Force (shove, trip, throw) against a **larger** target | one step larger: reach −1 rung (an engine-cited Amplifying snag, "scale"); two steps: reach −2 (so Zero unless levers offset it: G4 for moving or holding the whole creature, with the redirect "seize a limb, climb it, or trip it with something"); three or more: G4 for the whole creature, always |
| The same against a **smaller** target | one Amplifying lever (once, however many steps) |
| Melee reach | a large creature's melee Strikes reach `band.close`; a huge or colossal one's reach `band.near` |
| Engagement capacity | +2 per step the target is larger (06.3.5) |
| Mounts and cover | a mount must be at least one step larger than its rider; a creature two steps larger than another is a `cover` feature for it |

### 06.4 Attacks, defenses and harm

**06.4.1 Guard and the other defenses.** `[D]` [DL-06-08; R5 CF-05; revision: I-065] Every creature has one defense per attribute
(00.3.8): `10 + attribute + competence + edge + status`. Chapter 09 stores all seven for adversaries.
One of them has a name because every Strike uses it:

- **Guard** is the **Agility defense as it stands against aimed physical attacks**:
  `Guard = 10 + Agility + competence(guard tag) + edge + status`.
  The **guard tag** is the deed tag of what the defender holds ready to fight with: its readied melee
  weapon or its shield (the higher competence of the two), else `deed.martial.unarmed`; ancestors count
  (00.3.6), so `deed.martial` and the PC floor at `deed` always apply. A weapon that only shoots (a
  bow, a crossbow, a sling) gives no guard tag; its holder uses `deed.martial.unarmed` and ancestors.
  Edge on Guard comes through `eff.defense_edge` (a shield gives +1, T-06-7; stances and items give the
  rest, to the family's cap of +2). Status on Guard comes only from conditions (T-06-10).
  *Check:* Wren (Agility +3) holds a spear with no polearm competence: floor +1 → Guard **14**, 00's
  reference value. Captain Hesk (Agility +2, `deed.martial` +4) → Guard **16** (WE-00-6).

**T-06-5 Which defense answers which attack.** (`data/conflict.yaml#defenses`)

| The acting side's method | Rolled against |
|---|---|
| Strike (melee, thrown, shot); an aimed working that must hit a body | **Guard** |
| Grapple; Force (shove, trip, throw) | the higher of the target's **Might** or **Agility** defense (01.18.9–10); breaking a hold: the holder's Might defense |
| Move through or past a blocker | the higher of the blocker's Might or Agility defense (01.18.4) |
| Setup by feint, or any trick on the senses | **Wits** defense; a blinding or tripping throw: Guard |
| Sneak, hide, lift from a belt | the highest notice (**Wits** defense) among those who could perceive it |
| Talk to frighten, taunt or demand surrender | **Resolve** defense. Standing does **not** enter a frighten, taunt or demand (fear and anger ignore regard, DL-15-14); it enters a **parley** request, composed by 15 (15.3.3; in a conflict standing is Hostile unless state says otherwise) [integration: IR ch.15 to 06] |
| A **resisted** effect (poison, fear, fire filling a room, a spell that says so) | the *target* rolls Endure (Endurance or Resolve) or Evade (Agility) against the **effect DC** (00.3.3; 01.18.3); it costs the target no action |

**06.4.2 A Strike at an unaware target still rolls against Guard.** `[D]` Awareness is settled *before*
the Strike, by the Sneak or by scene state that produced `flag.hidden` or the alertness `unaware`. The
Strike is then an ordinary aimed attack against Guard, with what unawareness gives in state: the
attacker's `flag.hidden` lever, the target's `cond.surprised` lever if the conflict begins with it (one
of the two is cited; they are the same opening and the engine cites the condition first), no reaction
by the target, and, for a target that is `helpless` (06.7.6), the helpless lever. So the primary deed
tag of such a Strike is the **weapon's** tag, and `deed.guile.ambush` is earned as a secondary tag
grounded by position (03.1.7, DL-03-24's second branch). An **ability** may say otherwise in its own
text (`ab.throat_of_night` rolls against the Wits defense and is ambush-primary). [DL-06-08]

**06.4.3 The Strike in a conflict.**
```
### 06.4.3  Strike (conflict frame)                               [J:enum] [J:flag] [D]
Trigger [T]:        a beat whose intent is to harm a creature with body, weapon or thrown or shot
                    object, declared in conflict mode
Loads in:           situation.conflict.*
License check:      basic verb: verb.strike (anchor card 01.18.8). From the saddle: 06.15.
Decisions (J):      1. IN REACH [D after a J:enum of weapon]: the weapon's bands (T-06-6) must include
                       the band to the target. If not: G4 for this beat, redirect "Move first (1
                       action), or throw it, or pick another target". Nothing is spent.
                       [revision: R2-M2; DL-06-42] Only a RECORDED band out of reach refuses. A band never
                       recorded is an omitted detail (D3): a melee Strike at someone with no band on record
                       takes `band.engaged`, logged `not_chosen:fight.to`, and the attack goes ahead. The
                       roll also carries the start-the-fight field (06.2.1).
                    2. ATTRIBUTE [J:enum] Might | Agility. Agility only when the weapon is `finesse`,
                       thrown or shot (T-06-7), or the method is unarmed and precise. Default Might.
                       When both fit equally the frame uses the lower and names the other (00.4.5).
                       Exception: a branch working (05.7.11) is a Strike with its branch's casting
                       attribute, not Might or Agility; it needs no weapon and reaches as 05.7.11
                       says (05 owns the working; precedence 00.1.4) [revision: I-057].
                    3. HARM MODE [J:enum] lethal | nonlethal | restraint (06.4.8). Default: lethal
                       against a hostile creature unless the player said otherwise.
                    4. LEVERS [J:flag per fact]: the player may cite up to two established facts
                       (a flag, a condition on the target, a feature, a Setup, a tell learned). The
                       engine first cites those this chapter makes automatic (T-06-4, T-06-10), which
                       count toward the two.
Computation [D]:    modifier = attribute + competence(weapon's deed tag or ancestor) + edge
                      + circumstance (levers; snags: repetition 06.1.6, cover/obscured/range/crowding
                      06.4.7, Defend 06.1.5, Fend 06.6.3; cap +-4) + status (the actor's conditions)
                    DC = the target's Guard (06.4.1), read sealed for adversaries: the OFFER shows the
                      number needed on the die, as always (01.7.1).
                    Stakes = SAFE (01.6.9: a miss costs only the foe's own turn). Reach = STANDARD.
                    The player may trade (01.7.3 "go big": reach Great, stakes Risky = a RECKLESS
                      blow) or push (05.6.7: 1 Focus, reach +1).
                    Harm on a success: base severity (06.4.4 and 06.4.5) shifted by
                      (delivered reach - 2) rungs, then the evaluation pass twice (00.10.5; 06.4.6),
                      then apply_harm (07).
Stakes:             Safe: failure = a miss, no cost; critical failure = one S1 cost, threatened
                    cost.footing (cond.off_balance) or cost.gear (the weapon dropped at your feet).
                    Risky (reckless): failure = one S2 cost, threatened cost.harm from the engaged
                    target's answering blow (3 Vitality before armor), alternate cost.footing
                    (cond.prone); critical failure = S3 (5).
State writes:       frame; target's Vitality and harm state (07); conditions from riders; ammunition
                    -1 and `<weapon>.loaded` (06.4.9); on_attack_hit / on_attack_miss / on_hit_taken /
                    on_harm_dealt hooks; the morale clock's sources (06.11.3); evidence (03).
Narration may not imply: harm of another severity or type; a condition no rider applied; a maiming,
                    disarming, tripping or killing blow that the frame did not deliver; the target's
                    Vitality as a number.
Worst case (J):     a wrong attribute: at most the difference of the two, shown in the OFFER (class
                    ii). A lever wrongly allowed: +2, or one severity rung (class i), with its fact id
                    on the frame.
Examples:           inside: "I thrust at the reeve" at band.engaged with a spear -> Strike, Safe,
                    Standard, S2 on a success.
                    boundary: the same thrust at band.close: a spear is a `reach` weapon -> legal.
                    With a sword -> decision 1 fails -> "he is a lunge away: close first".
                    outside: "I slam him back against the wheel" -> the intended change is position:
                    Force (06.5.3), not Strike.
                    non-example: "I cut his head off" -> an assertion of outcome (SG-06); it is a
                    Strike, and what it does is what the degree and the weapon deliver.
Anchor:             yes. Intent verbs: hit, cut, stab, shoot, throw at, punch, kick, bash, club.
                    Knobs: harm_severity (weapon base -> improvised by resemblance, T-06-8 -> a
                    dropped object's hazard severity); harm_tags; dc (Guard -> object tier, T-06-9);
                    targets (one -> the object whose fall or swing affects another); condition
                    (none -> one called-shot effect, 06.4.10); stakes (Safe -> Risky by the trade);
                    action_cost (1 -> 2 for heavy weapons only).
Basis:              [01.18.8] [00.3.3] [00.3.15] [R7 §5 Ex.7, Ex.9] [R: https://2e.aonprd.com/Rules.aspx?ID=220]
```

**06.4.4 Weapon weights: base severity, cost and cadence.** `[D]` [DL-06-06; DL-06-02; revision: I-065] Chapter 08 builds every weapon item
on this table (00.17.2 "weapon harm base severities (with 08)"; `data/conflict.yaml#weapon_weights`).
A weapon has exactly one **weight**, which fixes its base severity, its Strike's action cost, the hands
it needs and the bands it reaches. Weight is the cadence channel of 06.1.7.

**T-06-6 Weapon weights.**

| Weight | Base severity | Strike costs | Hands | Bands | Examples (08 owns the items) | Deed tag family |
|---|---|---|---|---|---|---|
| **unarmed** | S1 Light | 1 | 0 | engaged | fist, kick, elbow, head; a natural weapon is the creature's own (09) | `deed.martial.unarmed` |
| **light** | S2 Moderate | 1 | 1 | engaged; thrown: close (near with a snag) | dagger, knife, hand axe, club, sap, short sword, sickle, thrown knife, dart | by kind (`.blade.dagger`, `.axe.hand`, `.bludgeon.club`, `.thrown.blades`) |
| **one-handed** | S2 Moderate | 1 | 1 (2 if `versatile` is used) | engaged (`reach`: also close) | sword, axe, mace, hammer, flail, spear, javelin (thrown: close–near) | `.blade.sword`, `.axe`, `.bludgeon.*`, `.polearm.spear`, `.thrown.javelin` |
| **heavy** | S3 Heavy | **2** | 2 | engaged (`reach`: also close) | greatsword, great axe, maul, halberd, pike, lance (from the saddle) | `.blade.greatsword`, `.axe.great`, `.bludgeon.hammer`, `.polearm.halberd`, `.mounted.charge` |
| **bow** | S2 Moderate | 1 | 2 | close–near (far with a snag); longbow close–far | shortbow, longbow, sling (1 hand) | `.archery.bow`, `.archery.sling` |
| **crossbow** | light S2 / heavy S3 | 1 | 2 | close–far | light crossbow (reload 1), heavy crossbow (reload 2) | `.archery.crossbow` |

Why two real severities and not five: with harm fixed at 1 / 3 / 5 / 8 / 12, a Light weapon would be
one third of a Moderate one and no one would carry it. So every real weapon is Moderate or Heavy, and
weapons differ by **cost, hands, bands and one or two properties** (T-06-7). A heavy weapon's two-action
Heavy blow delivers about the same expected harm as two Moderate blows against an unarmored foe (3.7
against 4.0 at the reference numbers), **more** against armor (reduction is paid once, not twice), more
with every lever, push and rider (each is spent on one roll), and leaves one action for a Move, a
Defend or a Setup. That is the consistent-versus-burst trade [R3 §06.4 (a), F-2; DL-06-06].

**T-06-7 Weapon and shield properties** (closed list; an item carries at most two; `data/conflict.yaml#weapon_properties`).

| Property | Effect | Typical on |
|---|---|---|
| `finesse` | Agility is allowed for melee Strikes | dagger, short sword, rapier, spear, staff |
| `reach` | Strikes at `band.close`; an enemy Moving from close to engaged with the wielder provokes its Opportunity Strike | spear, halberd, pike, lance, whip |
| `thrown` | may be thrown: close with no snag, near with a Precision snag; the weapon is then at the target's position | dagger, hand axe, javelin, spear, dart |
| `versatile` | wielded in two hands, the Strike holds harm edge +1 (`eff.harm_edge`) | sword, axe, spear, staff |
| `parrying` | +1 edge to Guard against melee attacks while the other hand holds no shield (`eff.defense_edge`) | sword, rapier, staff |
| `armor_breaking` | ignores 1 point of the target's worn-armor reduction | mace, hammer, maul, pick, heavy crossbow |
| `close_quarters` | usable while `cond.grabbed` or `cond.restrained` with no status penalty from the hold | dagger, knife, unarmed |
| `entangling` | a Strike with it may be declared as a Grapple at its band (the thrown net, the whip, the bolas): Grapple's ladder, capped at `cond.grabbed` S2 | net, whip, bolas |
| `loading` | must be reloaded (T-06-1) | crossbows |
| `concealable` | a Sneak to hide it holds a Precision lever (08) | dagger, sap, dart |
| `shield` (light) | +1 edge to Guard; enables shield abilities and Full defense's cover | buckler, round shield |
| `shield` (heavy) | +1 edge to Guard; while Defending, `flag.in_cover` against ranged attacks; Exert and Sneak take a snag (08) | kite or tower shield |

**06.4.5 Mastery: the baseline that grows without Focus.** `[D]` A Strike's **base severity** is its
weapon's weight severity, raised by the wielder's **training grade** in the license that covers the
weapon's deed tag (`lic.training.martial_*`, 05.9.2; grades are set by calling tier, 04.5.1):

| Grade held in the weapon's training license | Base severity of the wielder's Strikes with it |
|---|---|
| none, or `trained` | the weight's (T-06-6) |
| `expert` (narrow and fine callings: tier 3; broad and hybrid: tier 4) | **one rung heavier** |
| `master` (narrow and fine callings only: tier 5) | **two rungs heavier** |

The mastery rung is part of the **base** (evaluation pass step E1), not an effect step, so it does not
use the ±2 cap on steps from effects and it composes with riders, flares, levers and the push in the
ordinary way; severity still clamps at S5. It applies to unarmed Strikes under `martial_unarmed` and to
shot and thrown weapons under their own licenses. It does **not** apply to workings: a spell's severity
is its rank's (05.3.9). Adversaries do not use this rule: their attacks' severities are listed in their
templates (09), which is the same idea expressed as data.
*Why.* Harm is fixed by severity and nothing may add actions, so without this a swordsman at tier 5
would deal the 3 Vitality he dealt at tier 1 while his foes' Vitality grew tenfold; every martial
character's output would then be Focus and nothing else. The simulation shows the effect directly
(06.10.6): with mastery, a specialist who spends **no** Focus beats one foe of his own band 99.7% of the
time at P3, 87% at P4 and 80% at P5; a broad-calling fighter, whose grade comes one tier later, 87% at
P3 and 73% at P4. Every published game that scales its foes scales the baseline blow: thirteenth Age
gives a weapon die for each step of a character's advancement, Pathfinder adds weapon specialization
and striking runes, D&D adds
attacks [R: https://www.13thagesrd.com/combat-rules/; R1 §06; DL-06-09; issue I-006].

**06.4.6 Harm through the evaluation pass.** `[D]` [DL-00A-16; DL-00A-29; C:P8; revision: I-065] (00.10.5; PR-06-3.)
*Dealer's side:* E1 base severity (06.4.4–06.4.5; a `slot.strike_delivery` owner replaces the harm
type and may set the form) → E2 steps: delivered reach − 2 first (uncapped: Limited −1, Standard 0,
Great +1, Exceptional +2), then effect steps (riders, flares, `cond.weakened`, a mob's numbers; summed,
capped ±2) → E3 convert (1 / 3 / 5 / 8 / 12) → E4 harm edge (cap +2).
*Receiver's side:* E4 reduction (worn armor and effects, by harm tag; chapter 07's cap) → E5 resistance
or vulnerability by harm tag → E6 never below 0 → E7 round down → `apply_harm` (07 applies it to
Vitality, wounds and harm states).
A **critical success** is one more rung through delivered reach (01.9.1): there is no separate critical
table. An attack that succeeds and is reduced to 0 still **hit**: `on_attack_hit` and `on_hit_taken`
fire, riders that apply on a hit apply, and narration says the blow landed and did nothing through the
armor.

**T-06-11 Armor (reference; chapters 07 and 08 own the numbers).** This chapter's math assumes worn
armor reduces `harm.physical` by **light 1, medium 2, heavy 3**, that a shield reduces nothing (it adds
to Guard), and that the total reduction cap is 4 with magic. Reduction is strong against Moderate
blows (3 becomes 1 through mail) and modest against Grievous ones (8 becomes 6): armor is how one
character survives a crowd, and why a crowd needs a hammer, a gap (06.4.10) or a Heavy blow against a
knight. Chapter 08 sets armor's price in the other pillars (weight, noise, swimming, sleep).

**06.4.7 Range, crowding, cover and sight snags on attacks.** `[D]` [DL-00A-10; R5 CF-11; revision: I-065] Engine-cited Precision snags
(−2 each, at most two cited per roll, ±4 cap), each naming its fact:

| Snag | Applies when |
|---|---|
| **long range** | a thrown weapon at `band.near`; a shortbow or sling at `band.far` |
| **crowded** | a shot or thrown Strike made while the attacker is engaged with any enemy |
| **into a melee** | a shot or thrown Strike at a target engaged with the attacker's ally: on a **critical failure** the threatened cost is `cost.harm` to that ally at the weapon's severity one rung lighter |
| **cover** | the target holds `flag.in_cover` and the attack is ranged |
| **unseen** | the target holds `flag.obscured` and the attacker relies on sight |
| **from below** | a melee Strike without `reach` at a target holding `flag.elevated` |
| **prone target at range** | a ranged Strike from `band.near` or farther at a `cond.prone` target |
| **guarded** | the target has `defending.<target>` (06.1.5); the target Fended this attack (06.6.3) |

When more than two apply, the engine cites the two that the scene established earliest and logs the
rest as not counted; the cap makes a third irrelevant to the number. **Outside the two-cited count**
(00.3.9 g, like repetition and this chapter's Defend, Fend, called and nonlethal snags): the snags the
actor's own worn armor carries (`base_items.yaml` `snags`, 08.1.5) and `burdened` (08.9.2); each still
counts toward the ±4 cap [integration: IR ch.08 to 06].

**06.4.8 Harm mode: lethal, nonlethal, restraint.** `[J:enum]` + `[D]` Every attack frame carries a
**harm mode**, chosen by the attacker when declaring (adversaries: from `defeat_disposition`, 09).
- **lethal** (default against hostile creatures): at 0 Vitality the target is **defeated**; chapter 07
  decides dead or Dying. For an NPC of depth `recurring` or `principal` (12.11.1), 07's default is
  Dying, so a named person never dies off-hand.
- **nonlethal**: the attacker pulls the blow, uses the flat, the butt or the fist. Blunt weapons and
  unarmed Strikes: no change. Edged, pointed and shot weapons: one Precision snag. At 0 Vitality the
  target is defeated and `cond.unconscious` for the scene, alive. Harm dealt is the same.
- **restraint**: the intent is to hold, not harm. It is not a Strike: use Grapple (06.5.2).
*Worst case (J):* the default applied where the player meant mercy: the OFFER states the mode in its beat
line ("to kill" / "to drop him alive"), so it is seen before commitment (class ii). Chapter 03 reads
the mode for `conduct.mercy`. [R4 §9 06 item 2; R5 CF-10]

**06.4.9 Ammunition and loading are state.** `[D]` [DL-06-06; DL-08-04; revision: I-065] Each shot or throw writes `ammunition −1`
(`update_quantity`, 08's quantity) or the thrown item's new location. A `loading` weapon carries the
fact `<weapon>.loaded` (true after a Reload, false after its Strike), and a creature spanning or
loading carries `<entity>.loaded = false`. Both are ordinary facts, so they can be cited: a foe caught
reloading is a Precision lever for a rush (WE-12-2). Arrows that missed may be recovered after the
conflict: half, rounded down (08).

**06.4.10 Called shots.** `[J:enum]` + `[D]` *Anchor: yes.* A Strike may be **called**: the attacker
accepts an engine-applied Precision snag (−2, "called"; outside the two-cited count, inside the cap) to
get **one** effect from this closed list on a success. One call per Strike. (`data/conflict.yaml#called_shots`.)

| Call | Also needs | On a success |
|---|---|---|
| **the gap** | the target's armor is worn, not grown (09 marks natural armor `no_gaps`) | the Strike ignores worn-armor reduction |
| **the leg** | — | harm one rung lighter; the target is `cond.slowed` until the end of its next turn |
| **the arm or hand** | — | harm one rung lighter; the target is `cond.weakened` (S1) until the end of its next turn; on a **critical success** it also drops what that hand holds |
| **the head or eyes** | a second snag (−4 in all) | full harm; the target is `cond.dazed` until the end of its next turn (a control condition: 06.7.4) |
| **a weak spot** | a recorded fact naming one (a tell learned, `ab.read_the_field`, 09's `weak_spot`) | the Strike holds an Amplifying lever in addition to any other two |
| **a held or worn object** | — | no harm to the creature; the object takes the Strike as a Force against its tier (a rope Easy, a strap Moderate, a staff Hard), or is knocked from the hand on reach 2+ (it falls at the holder's position) |

`[J:enum]` *Decision:* which call the player's words name; default when the words name a body part not
listed: **the leg** for anything that carries the creature, **the arm** for anything that holds or
strikes, else no call (an ordinary Strike, and the narration may still place the blow there). *Worst
case (J):* the neighboring call applied: one rung of harm or one short condition (class i). Called shots
are the no-Focus answer to armor: against a T4 foe with reduction 2, calling the gap raised the
simulated baseline from 62% to 73% at P3 (T-06-14). *Tempting non-example:* "I shoot him in the eye, so
he's blind for the fight" → the call's own result is the list's: dazed until the end of his next turn;
lasting blindness is chapter 07's wound table, reached only by harm.
[R: https://samhaine.wordpress.com/2020/04/06/savage-worlds-rules-summary/ (Savage Worlds: a called shot is a fixed penalty for a fixed effect: limb −2, head −4); DL-06-10]

**06.4.11 Resisted effects in a conflict.** `[D]` [DL-00A-03; R5 CF-04; revision: I-065] When an effect lands unless withstood (00.3.3), its
target rolls Endure or Evade against the effect DC as chapter 01 frames it (01.18.3): free of action,
not a declared beat, never pushed. Against an **area** effect each target rolls for itself (a mob rolls
once, 06.10.4). An adversary's resisted roll is an engine fortune check (01.6.7). The effect's
severity sets the stakes and the result follows 01.18.3 unless the effect has its own table.

### 06.5 Maneuvers and improvisation

Everything in this part is a basic verb used in a fight. Each rule restates its anchor's ladder with
conflict-specific numbers and is **Anchor: yes**, so an action no rule names is ruled by picking the
nearest of these and turning at most two knobs (00.2.7). T-06-9 lists forty such rulings ready-made.

**06.5.1 The general shape of a maneuver.** `[D]` [DL-00A-19; DL-00A-24; C:P8; revision: I-065] A maneuver is one action, one roll by the actor
against a defense from T-06-5, stakes **Safe** by default, reach **Standard**, and it carries
`trait.action.attack` when it hinders a creature against its will (so it counts for repetition). Its
result is a **condition, a band change, a flag or an object's state**, never harm; harm is a Strike's.
An effect *beyond* the verb's own ladder is not a free rider: it is a second beat, or the reach ladder's
next rung, or an ability (01.18.8 "distinguish").

**06.5.2 Grapple: seize and hold.** `[D]` + `[J:enum]` [DL-00A-19; C:P8; revision: I-065] *Anchor: yes.* Card 01.18.9.
- **Needs** a free hand (or an `entangling` weapon, or jaws) and `band.engaged`. Against a larger
  target: 06.3.10. No band on record to the target: `band.engaged`, logged; a recorded band short of it refuses
  [revision: R2-M2; DL-06-42]. The roll carries the start-the-fight field (06.2.1).
- **Ladder** (delivered reach): 1 → `cond.grabbed` S1; 2 → `cond.grabbed` S2; 3 → `cond.restrained`;
  4 → `cond.pinned`. The condition's source is the holder; its duration is `while` the hold lasts.
- **The hold is state, not words** [revision: R2-J; DL-06-31]. Code applies the ladder's condition to the held one at
  RECORD (T-06-10) and ends it only by the breaking-free and ending rules below. T-12-18's posture line ("held fast
  by you") is the condition's visible face: written from it, cleared with it, never a second hold. No manner label
  is written for the held one, and no scene label is a lever or snag (01.6.8); the condition's own entry is.
- **The held one's turn.** A held adversary or NPC tries to break free first (06.9.4's "held → break free" row;
  06.9.2; PR-06-6), and while the condition lasts its turn respects the condition's limits (T-06-10): no Move away
  from the holder; restrained, Strikes only with `close_quarters` weapons and no Fend; pinned, only break free,
  Talk, Endure and workings needing no hands. *Retires:* the hold kept as scene words while the foe's turn ignored
  it (round 6, I3 §1: 8 of 13 foe hits landed while the foe was held).
- **Holding** costs no action. The holder keeps one hand on the hold, cannot Move except by dragging
  (each transition costs +1 action, and the held one comes along if `grabbed` S2 or worse), and is
  itself engaged with the held one.
- **Tightening.** A further Grapple by the holder against the same target holds a Precision lever
  (the existing hold) and, on a success, raises the condition one step on the ladder
  (`exclusion_group: hold`).
- **Breaking free**: one action, Grapple with Might or Agility against the holder's Might defense;
  success ends the hold; a critical success also leaves the holder `cond.off_balance`. The hold also
  ends if the holder lets go, is moved away, or is `stunned`, `unconscious` or defeated.
- **What else a hold may do**, each a further action by the holder with its own roll: *choke*
  (condition knob → `cond.choking`; needs `restrained` or `pinned`); *use as a shield* (the holder
  gains `flag.in_cover` against ranged attacks, and a critical failure of such an attack threatens the
  held one); *take an item* (Grapple, snatch: reach 2+ takes it, 1 knocks it loose); *throw* (a Force
  against the held one with a Precision lever).
- **Climbing onto a larger creature** is this card with the mount clause: reach 2+ gives the climber
  `flag.mounted` on it (06.15.5).
- Knobs: `condition` (grabbed → restrained, pinned, choking as above); `attribute` (Might → Agility to
  slip a hold); `targets` (one → a limb of a creature two or more sizes larger: the scale snag is waived
  and the condition applies to that limb only: the creature is `cond.slowed` for a leg, `cond.weakened`
  for an arm, while held); `dc`; `duration`.
- *Decision* `[J:enum]`: Grapple or Force? The actor keeps hold → Grapple; the target is moved away or
  down → Force. Default: Grapple when the declaration says "hold", "grab", "pin", "wrestle". *Worst
  case (J):* the other verb's ladder, same defense, same cost (class i).

**06.5.3 Shove, trip and throw (Force).** `[D]` [DL-00A-19; C:P8; revision: I-065] *Anchor: yes.* Card 01.18.10, against the higher of
Might or Agility defense. Ladder: 1 → `cond.off_balance`; 2 → pushed **one band** away (the engagement
link breaks) **or** `cond.prone`, the actor's choice declared in the beat (undeclared: pushed, logged as `not_chosen:force`) [revision: R2-M; DL-06-41]; the roll carries the
start-the-fight field (06.2.1) and, with no band on record, takes `band.engaged`, logged [revision: R2-M2; DL-06-42]; 3 → pushed two bands, or
prone and off-balance; 4 → as 3 and a follow-up lever. **Into or off something:** when a recorded
`hazard` or `height` feature lies where the push sends the target (`[J:flag]`: *"Is the feature in
the target's group or named as behind it?"*; uncertain → false; *worst case:* one push that should have
reached the hazard does not, or the reverse: one hazard entry's effect, stated in the OFFER, class ii), a
push of one band delivers the target to it: the hazard then acts by its own entry (10), and a fall follows 06.5.8. This is the Force card
with the `reach_unit` knob at "position into a feature"; the OFFER states the hazard's severity before
commitment, and the frame's stakes do not change, because the danger is the target's. Size: 06.3.10.

**06.5.4 Disarm.** `[D]` [DL-00A-19; DL-12-26; revision: I-065] *Anchor: yes* (Intent verbs: "disarm", "knock it from his hand", "make her drop it",
"take his sword". Knobs: `targets` (the held object, or the arm); `reach_unit` (2+: in the actor's hand or fallen
at the holder's position; 1: it falls); `condition` (the arm route: cond.weakened). Examples: T-06-9 row 24)
[revision: I-031]. Three routes, each already a rule; the player's method picks:
(a) **snatch it** (Grapple, a free hand; reach 2+ and it is in the actor's hand, reach 1 and it falls);
(b) **beat it from the grip** (a called shot at a held object, 06.4.10: reach 2+ and it falls at the
holder's position); (c) **wrench the arm** (a called shot at the arm: `cond.weakened`, and on a
critical success the hand opens). A dropped weapon is picked up with the turn's free handling or one
action; an adversary that loses its weapon uses its template's fallback attack (09) or its fists (S1).
A weapon bound to its wielder (08's `cost_immune`) cannot be disarmed.

**06.5.5 Feint, distract, blind (Setup).** `[D]` [DL-00A-19; DL-00A-10; revision: I-065] *Anchor: yes.* Card 01.18.16 and 01.14.9. One action,
against the Wits defense for a trick, Guard for a throw. It creates **one lever fact** (two uses on a
critical success) for the actor or an ally, lasting until used or the end of the actor's next turn; the
DM classifies the lever's type by what the fact does (01.6.8), and the player picks when it honestly
fits two. With the `condition` knob the Setup instead applies one of `cond.distracted`,
`cond.off_balance`, `cond.exposed`, or (grit, glare, a flung cloak, lamp-oil smoke) `cond.blinded`,
until the end of the target's next turn. `cond.blinded` and `cond.dazed` are control conditions
(06.7.4). *Worth, simulated at reference numbers:* a Setup that gives an Amplifying lever to a Moderate
Strike adds about 0.9 expected harm for its action, against 1.45 for a third Strike at −4; a Setup that
blinds an elite foe removes about a third of that foe's expected harm for a round. Setups win when the
foe hits hard or the next blow is big.

**06.5.6 Getting past (Move through).** `[D]` [DL-00A-19; DL-06-07; revision: I-065] *Anchor: yes.* Card 01.18.4 with the `dc` knob at
"opposed": to pass a blocker, slide under an ogre, or break out of a ring, Move against the higher of
the blocker's Might or Agility defense. Reach 2+ → the mover ends on the far side (`band.close` beyond,
or engaged with whoever was screened) and the blocker has no Opportunity Strike; 1 → partway: the mover
stays engaged and has provoked; failure → no movement, and on a critical failure `cost.footing` S1. A
size step in either direction of two or more makes it unopposed (between the giant's legs; over the
goblins' heads by Exert).

**06.5.7 The charge.** `[D]` [DL-00A-10; DL-06-07; revision: I-065] A Move of one transition that ends at `band.engaged`, followed in the
same turn by a melee Strike at the one just reached, lets that Strike cite the fact
`charged.<actor>.<target>` as a **Precision lever** (a running start, 00.3.9). It needs a clear line
(no `difficult_ground`, no screener) and the Move must not have been a Withdraw. Abilities (`ab.lance_charge`)
and the lance from the saddle do more.

**06.5.8 Falls, drops and thrown things.** `[D]` + `[J:rung]` [DL-06-11; DL-06-27; R5 CF-12; revision: I-065] A body that falls, or an object dropped
or toppled onto a body, deals harm as a **hazard** with these severities *(falls: reference; ch.10
owns)*: a fall of 10 ft S2, 20 ft S3, 40 ft S4, 80 ft or more S5, `harm.physical.crush`; the faller
lands `cond.prone`. A falling creature rolls nothing. Who rolls for a falling *object* follows 00.3.3:
when an actor **aims** the fall (cuts the rope, tips the cask: 06.5.10), the actor rolls once and no
one Evades; when nothing aims it (a roof gives way, a trap drops, a rockslide), each creature under it
makes a resisted Evade against the tier that matches the severity (00.3.11), reading 01.18.3. A
creature shoved toward a drop it could catch itself at gets that Evade too.

**T-06-8 Improvised objects by size rung** `[J:rung]` (`data/conflict.yaml#improvised`).

| Rung | Anchor sentence | As a held or thrown weapon | Dropped, toppled or swung onto someone | Examples (typical / boundary) |
|---|---|---|---|---|
| **hand** | one hand lifts and throws it | unarmed weight, S1; or "resembles a light weapon" → S2 (01.18.8) | S1 | a mug, a stone, a stool leg / a full wine bottle (resembles a club → S2) |
| **body** | about a person's weight or bulk; two hands or a shove move it | heavy weight, S3, two actions, a Precision snag (unwieldy) | S2 | a bench, a barrel, a sack of grain, a table tipped / a shield-sized door wrenched off |
| **heavy** | several people or a mechanism move it; it hangs, leans or rolls | cannot be wielded | S3 | an iron chandelier, a statue, a loaded cart, a stack of casks / a ship's boom swinging |
| **massive** | part of the building or the land | cannot be wielded | S4 | a wall section, a felled tree, a boulder / a collapsing roof (S5 as a ch.10 hazard) [revision: I-075: a portcullis is a `barrier`, T-06-9 row 19] |

*Worst case (J) of a one-rung error:* 2–4 Vitality (class i), shown in the OFFER as the harm on a hit.

**Footprint.** `[D]` [revision: I-075] A dropped, toppled, swung or rolled object selects at most its rung's
**count** of creatures, inside its shape's cap: hand 1, body 2, heavy 3, massive 4. Against a mob each selected
member takes one share, and a share never exceeds one member's Vitality (06.10.4), so the object fells at most
its count. Once it has fallen the object is the fact `<feature>.fallen` and is not dropped again; another drop
needs another feature established (06.3.8). (Basis: `06-conflict-sim.py` section L.)

**06.5.9 Aim.** `[D]` [DL-00A-10; DL-06-03; revision: I-065] One action, no roll, only while engaged with nobody and not `cond.off_balance`:
the actor steadies and picks its moment. It writes `aimed.<actor>.<target>`, a **Precision lever** for
the actor's next shot or throw at that target, lost if the actor Moves or is harmed first. Aim exactly
cancels the second shot's repetition snag (Strike, Aim, Strike rolls at 0 and 0); it never exceeds the
two-lever limit. *Anchor: yes.* Intent verbs: aim, steady, wait for the gap, line it up. Knobs:
`duration` (next shot → held until the end of the next turn); `targets`.

**06.5.10 Using the environment.** `[J:enum]` + `[J:flag]` + `[D]`
```
### 06.5.10  Environment use                                      [J:enum] [J:flag] [J:rung] [D]
Trigger [T]:        a declared beat in a conflict whose method uses a feature (06.3.8) or a loose
                    object rather than only the actor's body and weapon
Loads in:           situation.conflict.*
License check:      basic verbs (the anchor's); a feature must be ESTABLISHED: an entity with a
                    feature_kind. Unestablished -> G0, the Oracle, before framing (06.3.8).
Decisions (J):      1. ANCHOR [J:enum]: by the INTENDED CHANGE, first match -
                       the actor's own position            -> Move / Exert (swing, leap, climb)
                       a creature's position or footing    -> Force
                       a hold on a creature                -> Grapple
                       a lever or a short condition        -> Setup
                       harm to a creature via an object    -> Strike with knobs (object as target;
                                                              the object's severity, T-06-8)
                       an object's state (shut, lit, cut)  -> Handle (as its nature suggests) or
                                                              Force (against its resistance)
                       Default when two fit: the one whose ladder names the intended change at
                       reach 2. Look the case up in T-06-9 first; then the ruling ledger (INV-19).
                    2. SIZE RUNG [J:rung] of any object that will strike someone (T-06-8).
                    3. IN PLACE [J:flag]: "Is the creature to be affected recorded at or under the
                       feature (same group, or named so in narration)?" True -> it is a legal target
                       of the object's effect. Uncertain -> false: the DM says where the creature
                       is and what would bring it there (a Force, a taunt, a Setup).
Computation [D]:    the anchor's frame with at most TWO knob changes (00.2.7), from: dc (-> the
                    object's tier, T-06-9), harm_severity and harm_tags (-> the object's or hazard's),
                    targets (-> the object, or those in its group via a spread, 06.8, at most the
                    object's footprint count, T-06-8 [revision: I-075]), condition,
                    stakes (-> the height or hazard the actor itself risks), reach_unit.
                    A hit through an object rolls ONE d20 against the higher of the object's DC and
                    the Guard (or the resisting defense) of the creature it must reach.
Stakes:             the anchor's default; raised only by a source the actor itself is exposed to (a
                    drop under a swing, a fire being kicked): 01.6.9.
State writes:       the feature's new state (cut, toppled, burning, shut) as facts; bands and flags by
                    set_position; conditions; harm via apply_harm; the ruling (signature = anchor +
                    sorted deltas) to the ruling ledger.
Narration may not imply: a second effect the frame did not name (the fire "also" spreading; the fall
                    "also" disarming); harm of another rung; that the feature still stands if it fell.
Worst case (J):     a neighboring anchor (same cost, a different ladder: class i, logged and
                    reusable as precedent or correctable as one, class iv); one size rung = 2-4
                    Vitality; IN PLACE wrongly true: one creature affected that was a step away.
Examples:           inside: "I cut the rope and drop the chandelier on him" -> Strike, knobs targets
                    (the rope) and harm_severity (heavy object S3); DC = the higher of the rope (Hard
                    at range; Moderate with a blade in reach) and his Guard.
                    boundary: he stands two strides from under it -> IN PLACE false -> "he is not
                    under it; a shove or a taunt could put him there".
                    outside: "I swing on the chandelier across the hall" -> the change is the actor's
                    position: Exert (01.18.11), no harm, stakes from the drop.
                    non-example: "I throw sand, and while he's blinded I also trip him and take his
                    sword" -> three intended changes are three beats (Setup, Force, Grapple), each
                    with its own action and roll; sand buys only the Setup's result.
Anchor:             yes (this rule is the anchor index for T-06-9). Intent verbs: swing from, drop
                    on, kick over, pull down, throw (a thing), slam, cut the rope, use the (thing).
                    Knobs: [revision: I-031] at most two per frame (00.2.7), from reach_unit, dc (the
                    object's tier), harm_severity, harm_tags, targets, condition, stakes (the drop or fire).
Basis:              [R7 §3.4, §5 Ex.1, Ex.9] [01.5.3] [R1 §06 "the environment is the cheapest source
                    of variety"] [R5 CF-12] [R7 §2.8 (improvised weapons by resemblance), §2.21 (stunts are just attacks)] [DL-06-11]
```

### 06.6 Reactions

**06.6.1 What a reaction is.** `[D]` [DL-06-01; DL-00A-17; R5 CF-07; revision: I-065] A reaction is one act taken **outside** the owner's turn, in answer
to a listed trigger. One per round (06.1.1); at most one per trigger event; refreshed at the start of
the owner's turn. A reaction is caused by a hook, so what it does is **depth 1** (00.10.8): it fires no
further subscribers, and it can be prevented only by the target's own `prevent`. It carries no
repetition snag and joins no window (06.1.6 c). Every participant that has a reaction has the three
**basic reactions** below; abilities of the Reaction form add others (05.3.2), each naming its hook.
The PC is asked each time a trigger occurs, unless the player has set a standing answer per reaction in
the codex (`always`, `ask`, `never`; 05.3.4's convention).

**06.6.2 Opportunity Strike.** `[D]` *Trigger:* an enemy engaged with you (a) leaves `band.engaged`
by a plain Move, (b) makes a beat with `trait.action.manipulate` other than with a weapon in hand
(reloading, drinking, picking something up, working a lock), or (c) stands from prone; with a `reach`
weapon, also (d) an enemy Moves from `band.close` to engaged with you. *Effect:* one melee Strike at
that enemy, framed and rolled in the ordinary way (the PC sees an OFFER and may decline, keeping the
reaction). It resolves before the triggering act completes; it does not stop the act unless its result
does (a rider that prevents movement; the target defeated). Withdraw, a successful Move-through at
reach 2+, and `ab.saddle_born` avoid it. [R: https://2e.aonprd.com/Actions.aspx?ID=2256; R5 CF-07]

**06.6.3 Fend.** `[D]` [DL-06-22; C:P10; revision: I-065] *Trigger:* an aimed attack is declared against you by an attacker you can
perceive (`on_check_against`), before its roll. *Effect:* that one attack takes an engine-applied
**Precision snag (−2)** citing `fend.<you>`: a dodge, a parry, a shield turned. Fend is the default
occupant of `slot.defense_reaction` at priority rank 0. It cannot be used while `cond.surprised`,
`blinded` (against what you cannot see), `restrained`, `pinned`, `stunned` or `unconscious`.
*Simulated worth:* without Fend, a P3 fighter's chance against one T4 foe falls from 62% to 46%
(T-06-14).

**06.6.4 The defense-reaction slot.** `[D]` [DL-06-22; C:P6; revision: I-065] `slot.defense_reaction` (T-00-14) holds **one** way of
answering an attack. Fend claims it at rank 0. An ability that claims it (`eff.05.defense_reaction`:
a shield block that lightens the harm, a spell ward, a parry-and-riposte) at rank 10 or more **replaces**
Fend while it is available (highest rank owns the slot; the holder may drop its claim as a free activity
to use Fend instead, 05.10.3). So a character has one defensive answer per round, and which one it is
differs by build: this is the reaction channel of cadence (06.1.7). Reaction abilities that are not
defenses (`ab.riposte` on a failed attack, `ab.set_spear` on a charge) do not claim the slot; they
compete only for the one reaction.

**06.6.5 Adversaries' reactions.** `[D]` [DL-06-01; DL-09-04; revision: I-065] By default a T1 adversary has none; a T2 adversary has one
reaction and may use only Opportunity Strike; a T3 or higher adversary has one and may also Fend, which
its behavior list spends on **the first attack against it each round whose attacker's modifier is the
highest it has seen this conflict** (in practice: the PC's first Strike). Chapter 09 may set
`reaction: false`, or list reaction abilities, per archetype (12's request). A mob has none.

**06.6.6 Ready.** `[D]` + `[J:flag]` [DL-06-01; R5 CF-07; revision: I-065] Card 01.18.18 and 01.14.10. For **one action** the actor frames a
one-action beat and a trigger; the OFFER is shown and committed then. When the trigger occurs before
the start of the actor's next turn, the beat resolves **as the actor's reaction** (so it needs the
reaction to be unspent, and it uses it). A readied attack is outside any repetition window. If the
trigger never occurs the action is spent and the reaction is kept. The trigger must be an observable
event (`[J:flag]`, 01.14.10: true only for something the actor would perceive; *worst case (J):* a beat
readied on an unobservable trigger simply never fires, class iv). A readied beat is a *declared* beat:
depth 0 (hooks fire on it). Adversaries Ready only when a behavior row names the trigger ("hold the
shot until someone shows at the door").

**06.6.7 Interception by companions.** `[D]` [DL-06-19; R5 CF-13; revision: I-065] A companion under the standing order *guard me* (06.14.4)
may spend its reaction as `eff.intercept`: it takes a hit meant for the PC while engaged with or in
the PC's group. This is the only basic reaction that redirects harm; the PC's own interceptions are
abilities (`ab.interpose`, `ab.take_the_blow`). An ally whose loyalty is **Devoted** may Intercept for the PC
by its reaction without the *guard me* order (T-16-7), and an ally with `kn.bodyguard` may Intercept while
bloodied (16.4.7) [integration: IR ch.16 to 06 (c)].

### 06.7 Conditions

**06.7.1 The list.** `[D]` [DL-06-12; R5 CF-06; revision: I-065] `data/conditions.yaml` defines **27** conditions in 00.9's schema: the 23
ids 00 reserved (T-00-15) and four added by this chapter (`cond.surprised`, `cond.silenced`,
`cond.broken`, `cond.heartened`; DL-06-12). Chapter 07 adds affliction stages and wound carriers in its
own owner-block. T-06-10 summarizes; the data file is canonical. Every effect below is an effect
reference in data (00.9.3 f).

**06.7.2 The three voices of a condition.** `[D]` [DL-06-13; revision: I-065] A condition changes play only through these three
channels, so that conditions compose without pairwise rules (00.9.3; DL-06-13):
1. **Status**: modifiers on the *bearer's own* checks and defenses (family `status`: only the worst
   penalty and the best bonus apply to any one roll, −4 to +2). Stacking three conditions never stacks
   three penalties.
2. **Levers and snags for others**: a condition that makes its bearer easier (or harder) to act
   against grants an **engine-cited lever** to those acting against it (`eff.grant_lever`), or a snag
   (`eff.06.grant_snag`). They count toward the two per roll and the ±4 cap: a prone, exposed, flanked
   target gives an attacker +4, not +6.
3. **Restrictions and periodic effects**: forbidden verbs, methods and senses (a union across
   conditions; a forbidden method is G4 for the beat), fewer actions, and harm or checks on a schedule.

**T-06-10 Conditions** (summary; S = default severity; "ENT" = until the end of the bearer's next
turn, the duration form `rounds:1` counted at its `turn_end`).

| Id | Category · stacking | Bearer's status | Others acting against the bearer | Restrictions / periodic | Default duration · how it ends |
|---|---|---|---|---|---|
| `cond.off_balance` S1 | physical · refresh | −2 on Might- and Agility-based checks | citable as **one lever** (type by use; the engine does not cite it automatically) | — | ENT; or 1 action to recover footing |
| `cond.prone` S2 | positional · unique | −2 on melee Strikes, Force, Grapple | melee attackers: Precision lever; ranged from near or farther: Precision snag | Move: +1 action per transition, one band a turn at most | until it stands (1 action; provokes) |
| `cond.grabbed` S1/S2 | positional · replace_stronger · group `hold` rank 1 | S2: −2 on beats with `trait.action.manipulate` and on Strikes with weapons lacking `close_quarters` | — | cannot change band away from the holder; S2: is dragged when the holder Moves | while the hold lasts; break free (06.5.2) |
| `cond.restrained` S3 | positional · replace_stronger · group `hold` rank 2 · **control** | −2 on all physical checks; Guard −2 | Precision lever | Move forbidden; Strikes only with `close_quarters` weapons; no Fend | while the hold or bonds last; break free; `deed.guile.escape` licenses do more |
| `cond.pinned` S4 | positional · replace_stronger · group `hold` rank 3 · **control** | Guard −4 | Precision lever; the bearer is **helpless** (06.7.6) | Move, Strike, Force, Exert, manipulate forbidden; only break free, Talk, Endure, workings needing no hands | as restrained |
| `cond.blinded` S3 | sensory · refresh · **control** | −4 on checks that rely on sight (Strikes, aimed workings, opposed Moves); Guard −2 | Precision lever | sight-based Observe forbidden; no reactions against what it cannot see; may not target beyond engaged except at a suspected place (two snags) | ENT by default; by source |
| `cond.deafened` S2 | sensory · refresh | −2 on tempo checks and on notice against unseen movers | — | hearing-based Observe forbidden; unaffected by beats with `trait.action.speech` (commands, taunts, songs) | by source; ENT default |
| `cond.dazed` S2 | mental · refresh · **control** | — | — | **one action fewer** each turn (minimum one); no reaction | ENT |
| `cond.stunned` S3 | mental · refresh · **control** | Guard −2 | Precision lever | **no actions, no reactions**; sustained workings end | ENT (one turn lost) |
| `cond.unconscious` S4 | physical · unique | Guard −4 | Precision lever; **helpless**; `unaware` | no actions, reactions or perception; falls `cond.prone` | by source: nonlethal defeat → scene; sleep → until woken (1 action by another, or any harm) |
| `cond.frightened` S1–S3 | mental · replace_stronger · severity variable | −1 (S1) / −2 (S2, S3) on all checks while the source is perceived | — | cannot willingly Move closer to the source; S3: must spend its first action each turn moving away if it can | decays one rung at each of the bearer's `turn_end`; applying it to an adversary ticks its side's morale clock |
| `cond.charmed` S2 | mental · unique | — | the source's Talk holds a Precision lever | cannot make attack-trait beats against the source; ends if the source or its allies harm the bearer; its social meaning (requests, standing, what the bearer realizes after) is 15's (Edge cases, "Charm and compulsion magic") [integration: IR ch.15 to 06] | by source |
| `cond.distracted` S1 | mental · refresh | −2 on Wits-based checks; Wits defense −2 | — (the lowered defense is the opening: Sneak, feint) | — | ENT |
| `cond.exposed` S1 | physical · refresh | — | attackers' Strike, Grapple, Force and aimed workings hold a **Precision lever** | — | by source (ENT from a Setup; scene from Quarry's Mark) |
| `cond.slowed` S2 | physical · refresh | — | — | every band transition costs +1 action; cannot Withdraw and Strike in one turn | by source; ENT default |
| `cond.weakened` S1/S2 | physical · replace_stronger · severity variable | −2 on Might-based checks | — | harm it deals is one rung lighter (S2: two rungs) | by source; ENT default |
| `cond.exhausted` S2 | physical · intensify, max 3 | −1 per stack on all checks | — | at 3 stacks: also `cond.slowed` | `until_rest:rest_long` (07 removes one stack per long rest) |
| `cond.bleeding` S1 | physical · intensify, max 3 | — | — | at the bearer's `turn_end`: 1 Vitality per stack (`harm.physical.cut`, no reduction) | until staunched (Handle, 1 action, Easy; any magical healing) or `scene_end` |
| `cond.burning` S1 | physical · intensify, max 3 · neutralizes chilled, frozen | — | — | at `turn_end`: S1 `harm.fire.flame` per stack (reduction applies per stack) | until put out (1 action; water or a roll in the dirt: the bearer goes prone and it ends) or 3 rounds |
| `cond.chilled` S1 | physical · escalate (2 → frozen) · neutralizes burning | −1 on Agility-based checks | — | — | 2 rounds; `scene` while in a cold hazard |
| `cond.frozen` S3 | physical · unique · **control** | −2 on physical checks; Guard −2 | Precision lever | Move forbidden | 1 round, then becomes `cond.chilled` (1 stack) |
| `cond.choking` S2 | physical · refresh | −2 on all checks | — | speech forbidden; at `turn_end`: 1 Vitality (`harm.physical.asphyxia`, no reduction) while the source lasts | while in the source (a hold, smoke, water); holding breath is ch.07's Endure |
| `cond.poisoned` S1–S5 | affliction_stage · replace_stronger · severity variable | −1 (S1) / −2 (S2, S3) / −3 (S4, S5) on all checks | — | periodic effects per the affliction (07) | by the affliction's stage (07) |
| `cond.surprised` S2 | mental · unique | — | Precision lever | acts last in round 1; one action on its first turn; no reaction | the end of its first turn |
| `cond.silenced` S2 | sensory · refresh | — | — | speech forbidden; workings that need the voice are G4 | by source |
| `cond.broken` S3 | mental · unique | −2 on attack-trait checks | Talk demanding surrender: Precision lever | may make attack-trait beats only when `flag.cornered` or attacked while unable to flee; behavior switches to its break row (06.11.5) | the conflict; ends if its side rallies (06.11.6) |
| `cond.heartened` S1/S2 | mental · replace_stronger · severity variable | **+1** (S1) / **+2** (S2) on all checks (the status family's one bonus) | — | immune to `cond.frightened` S1 | by source; the scene at most |

**06.7.3 Durations are counted by the engine.** `[D]` + `[T]` Every instance has a duration form
(`substrate.yaml#duration_forms`) and a source; `h.00.durations` and `h.06.turn_effects` end them.
A visible condition must be named in the narration of the turn it is applied and the turn it ends
(PR-00-5 step 6). `get_active_triggers` returns every active condition on every participant at the
start of each turn, so none is forgotten [R4 §9 06 item 5: "ignoring active status effects" is a
documented failure of agent DMs].

**06.7.4 Control diminishes.** `[D]` Eight conditions are **control**: `restrained`, `pinned`,
`blinded`, `dazed`, `stunned`, `frozen`, plus `charmed` and `frightened` at S3. They share one counter
per target (`diminishing.group: control`), kept by `h.06.diminishing_window`:

| Control conditions already applied to this target, counted | The next application |
|---|---|
| 0 | full duration |
| 1 | **half** duration, rounded down, at least one turn |
| 2 or more | **fails**: the target has the measure of it; the attempt's other effects (harm, movement) still land |

The counter rises by one each time any control condition is applied (a stronger hold replacing a
weaker one in the same exclusion group counts once), and falls by one at the end of each round in
which the target carried no control condition. It resets at `conflict_end`. It applies to the PC and
to adversaries alike: no one is locked down, and the PC can never be kept from acting for more than
one full turn and a half in a row by conditions alone [R3 §06.7; BRIEF §4 "a single unlucky roll never
ends a character"; DL-06-14]. The OFFER for a beat that would apply a control condition shows which row
applies.

**06.7.5 Opposites and exclusion.** `[D]` [DL-00A-21; revision: I-065] `cond.burning` and `cond.chilled`/`cond.frozen` neutralize
each other (PR-00-5 step 1; WE-00-7). `cond.heartened` and `cond.frightened` S1 neutralize each other.
The `hold` exclusion group keeps one of `grabbed`, `restrained`, `pinned` active per holder-and-target
pair. A stance (`slot.stance`) is not a condition; a stance ends at `conflict_end` unless its text says
`scene` (05's request), and the stance and aura slots are separate.

**06.7.6 State expressions other chapters may read.** `[D]` [DL-00A-16; DL-06-07; revision: I-065] (`data/conflict.yaml#expressions`; each is
computed by the engine and usable in any `applies_when`.)

| Expression | True when |
|---|---|
| `bloodied(x)` | `0 < x.vitality.current` and `x.vitality.current × 2 ≤ x.vitality.max`. A shown descriptor (00.6.3). For a mob: its pooled Vitality |
| `helpless(x)` | x carries `cond.unconscious` or `cond.pinned`, or is bound (`cond.restrained` with duration `until_cleansed`) |
| `unaware(x, y)` | x's alertness toward y is `unaware`, or y holds `flag.hidden` toward x, or x carries `cond.surprised` or `cond.unconscious` |
| `engaged(x, y)` | an engagement link joins them |
| `outnumbered(x)` | enemies engaged with x number two or more |
| `defeated(x)` | 07's disposition flag: out of the fight (dead, unconscious, Down, yielded, fled; a Dying NPC or adversary). A Dying **PC** is not defeated: it still acts (07.1.3) [integration: IR ch.07 #6] |
| `alone(x)` | no ally of x is a participant within `band.near` of it |
| `size_steps(x, y)` | y's size rung minus x's |

A **helpless** target gives attackers a Precision lever (from its condition) and, as a second fact, an
Amplifying lever (`helpless.<x>`); chapter 07 owns what it means to strike one down, and chapter 03
what it says about the striker.

### 06.8 Effects on more than one target

**06.8.1 Shapes select over relationship-state.** `[D]` [DL-06-15; C:P6; revision: I-065] No effect asks "who is inside the circle". An
effect that touches several targets carries one **shape**, and a shape is a selection rule over bands,
links, groups and flags, with a cap (`data/conflict.yaml#multi_target`). Five are chapter 05's spread
tags, adopted here with 05's caps and order unchanged (05.10.4); the sixth, `cone`, is added for
adversary powers and falling or swung objects (DL-06-15).

**T-06-15 Shapes.** When several shapes meet on one effect they apply in this order, each to the
targets the previous one produced, **never above six targets in total**.

| Order | Shape | Selects, in priority order | Cap | Harm to each |
|---|---|---|---|---|
| 1 | `pierce` | the primary target, then each participant carrying `flag.lined_up` in the same line, nearest to the source first | 4 | full |
| 2 | `burst` | the primary target (or the named point), then each participant engaged with it, then each in its group; friend and foe alike | 6 | full |
| 3 | `cone` | each participant at `band.engaged` with the source, then each at `band.close` in the primary target's group; friend and foe | 4 | full |
| 4 | `fork` | the primary target and one more eligible participant within `band.close` of it per extra target the effect grants | 5 | full |
| 5 | `chain` | after the primary resolves, the nearest other participant within `band.close` of the last target (06.3.4), friend or foe | 3 | one rung lighter at each leap |
| 6 | `linger` | the place: any participant that enters the named group or feature, or ends its turn there, for the duration | 5 | as the effect states |

**06.8.2 Resolving a shaped effect.** `[D]` [DL-06-15; revision: I-065] (PR-06-5.)
- **Selection is the engine's.** Ties within a priority step: the participant nearer the source by
  band; then lower current Vitality; then id. The player or behavior list chooses only the *primary*
  target or point. An effect whose text says "foes" drops allies from the selection; otherwise a shape
  is indifferent to side, and the OFFER lists every name it will touch before commitment.
- **One roll serves an aimed effect**: the same total is compared to each target's defense, so each
  target has its own degree (05.10.4). **Each target of a resisted effect rolls for itself.**
- **A mob** is one target that absorbs more than one share (06.10.4).
- **Features.** A `burst` or `cone` of fire, force or a falling mass also applies to features in the
  selected group when the effect's harm tags could affect them (`[J:flag]`: *"Is the feature made of
  something this harm type plainly destroys or sets alight?"* uncertain → false; *worst case:* one
feature's state wrong by one step of the object ladder, class i): the feature takes
  the Force result "weakened" at S2, "broken" at S3 or more (01.18.10's object ladder).
- **Cover** against a shaped effect is a Protective lever on the Evade, never immunity.

### 06.9 Running the opposition

**06.9.1 The DM chooses for each adversary, from the acts legal now.** `[D]` + `[J:enum]` [revision: R2-M; DL-06-40]
An adversary acts **after** the PC's beat in the exchange has resolved, so the PC's result (a grapple that holds it, a
shove off the ledge, a blow that drops it) is already state when its act is chosen. For each able adversary the engine
lists the acts its state allows now (T-06-16) and the DM picks one act and its target, and whether a Strike is
nonlethal (06.4.8); with tools this is one extra DM call per settled fight exchange (owner ruling 2026-10-10, D2). The
engine checks legality, frames and rolls the act (06.9.2) and applies its result (harm, holds, positions); narration
follows the result and cannot soften it (INV-2). **What the DM omits is defaulted and logged** (`not_chosen:<field>`):
the act is the first legal row of the adversary's behavior list (09, else 06.9.4), the target the PC; a pick outside
the listed acts counts as omitted. Code never infers an adversary's choice from the narration or the scene's words
(constitution VIII.9). *Worst case (J):* a weak pick (an unhurt adversary waits when it should strike): one adversary turn spent in the PC's favor, open in the log and counted by the passivity measure below (class i). *Retired rationale, kept as a watch:* this card once took the choice from the DM entirely,
because measured AI referees in fights picked targets that made no sense and declined to press [R4 §9 06 item 4, §6.2
item 3; R: https://arxiv.org/abs/2502.19519; R3 §06.8]. The DM now sees only legal acts, which answers the first; the
second is watched by the **passivity measure** (spec 033 P7): the share of turns an engaged adversary strikes, and the
`wait` and `yield` picks made for adversaries that are unhurt. *Transition:* the pipeline engine keeps evaluating the
lists itself until its deletion spec.

**06.9.2 An adversary's beat.** `[D]` [DL-06-16; C:I; revision: I-065] Each adversary action is a frame built by the engine with
`offer.choice: auto` (a fortune check, 01.6.7): verb and attribute from the template's attack entry;
target as the DM picked it (06.9.1; 06.9.3 is its guidance) [revision: R2-M]; levers and snags **cited by the engine** in this fixed order until two of each are
cited: (1) conditions on the target that grant levers (T-06-10), (2) flags (T-06-4), (3) a lever fact
the adversary's own earlier Setup created; snags per 06.4.7. Stakes: Safe. Reach: Standard. `lethal`:
legal only under chapter 07's lethal warning (00.3.14). Before the roll the PC is offered Fend and any
reaction ability whose trigger fits (06.6); after it, the harm is applied by the engine and cannot be
softened by narration (INV-2, 01.8.5).

**06.9.3 Attention: who it goes for.** `[D]` [revision: R2-M; DL-06-40] Guidance shown to the DM for its target pick (06.9.1); the DM's pick stands, and an omitted target is the PC. Unless the behavior row names its target ("the one
holding the lantern", "whoever harmed its master"), an adversary's target is the first of:
1. the participant its **objective** names (06.13.2: the captive it came to take, the PC it was paid
   to kill);
2. an enemy **engaged with it** — if several, the one that dealt it the most harm since its last turn
   (the attention score: a background counter per adversary, reset at its turn end);
3. the enemy that dealt it the most harm since its last turn, wherever it is;
4. the **nearest** enemy by band — if several, the PC before a companion;
5. an engine roll among those still tied.
A **Dying PC** is a target only for a side whose objective or `defeat_disposition` is `kill` (07.6.1); every other side's attention passes over it to the next enemy [integration: IR ch.07 to 06]; this binds the DM's pick too.
An ability that says it "draws attention" (a taunt, a challenge) adds to the attention score: a
successful Talk taunt adds harm-equivalent equal to twice the delivered reach, so position 2 and 3
can be bought [R3 §06.8; DL-06-16]. *Narration may not imply* an intention the DM's pick did not state.

**06.9.4 Default behavior lists.** `[D]` [DL-06-16; revision: I-065] [revision: R2-M; DL-06-40] Every behavior list is guidance shown to the DM and the logged default for an omitted pick (06.9.1); the acts it may pick are T-06-16's. Until chapter 09's lists exist, and whenever an adversary has
none, the engine uses one of four defaults by the template's `role`
(`data/conflict.yaml#default_behaviors`; each `do` is a macro of T-06-1 actions):

| `beh.default_melee` | `beh.default_ranged` | `beh.default_beast` | `beh.default_mob` |
|---|---|---|---|
| 1. `cond.broken` → break row (06.11.5) | 1. broken → break row | 1. broken → break row | 1. broken → break row |
| 2. held (`grabbed` or worse) → break free | 2. an enemy engaged with it → Withdraw, then shoot | 2. held → break free | 2. not engaged with its target → Move to engage |
| 3. prone → Stand | 3. no line to any enemy → Move toward the nearest cover with a line | 3. bloodied and not cornered and its nerve is `skittish` → Withdraw and flee | 3. Strike (numbers apply), twice |
| 4. a heavy blow is listed and no windup is held → Windup (06.9.5) | 4. not loaded → Reload | 4. not engaged → Move to engage the target (pace as its template) | |
| 5. not engaged with its target → Move toward it (Withdraw first if engaged elsewhere) | 5. target in cover and a second action remains → Aim | 5. target is prone or `grabbed` by it → Strike | |
| 6. engaged, an ally also engaged with the target, target not flanked → Flank (once) | 6. shoot the target | 6. it has a grab attack and the target is not held → Grapple | |
| 7. Strike the target | 7. else Defend | 7. Strike the target | |

**T-06-16 Adversary acts legal now** [revision: R2-M; DL-06-40]. The acts the DM may pick for an able adversary
(06.9.1), by its state after the PC's beat; melee only until chapter 09's lists add windup, flank, aim, reload, shoot
and defend. `close_in` is a Move to engage (PR-06-4); `withdraw` and `flee` are 06.12's ways out (`flee` leaves the
scene); `stand` rises from prone; `break_free` is 06.5.2's; `yield` is 06.11.7's; `wait` spends the turn.

| Adversary state | strike | close_in | withdraw | stand | break_free | grapple | flee | yield | wait |
|---|---|---|---|---|---|---|---|---|---|
| engaged, free | yes | no | yes | no | no | yes | yes | yes | yes |
| close, near or far, free | no | yes | no | no | no | no | yes | yes | yes |
| prone | no | no | no | yes | no | no | no | yes | yes |
| grabbed by the PC | yes | no | no | no | yes | yes | no | yes | yes |
| restrained by the PC | yes (a close-quarters weapon) | no | no | no | yes | no | no | yes | yes |
| pinned by the PC | no | no | no | no | yes | no | no | yes | yes |
Down, dead or fled: no acts, and the DM is not asked. A Dying PC is a legal target only as 06.9.3 allows.

**06.9.5 Heavy blows are announced.** `[D]` + `[T]` + `[N]` An adversary attack whose **base severity
is S4 or more**, and every adversary attack with a shape (06.8), is a **heavy blow**. A heavy blow
needs a **Windup**: one action, on a turn **before** the turn of the blow, which writes
`windup.<adversary>.<attack>`; the blow may be made only on a later turn while the fact stands. The
Windup is visible: the turn's narration must show it with the template's tell ("the ogre draws the
maul back over its shoulder, both hands"; "the wyvern's throat swells and glows"), and the PC's status
line carries "winding up: *the attack named*". The fact ends if the adversary is moved against its
will, becomes `cond.prone`, `dazed`, `stunned` or `blinded`, or takes harm of S3 or more from one hit
(the blow is **spoiled**; it must wind up again).
So the PC always has one full turn to answer the worst an enemy can do: get out of reach or behind
cover, spoil it, Defend, or accept it. No Grievous blow ever arrives unannounced, and a critical
success on one (S5, 12 Vitality) cannot take a character from full Vitality to anything worse than
Staggered (00.3.12). This is the conflict half of telegraphed lethality; the lethal warning and the
two keys are chapter 07's [BRIEF §4; R6 §C.2.1; R4 §6.2 item 4; DL-06-17]. It also sets a solo
adversary's rhythm: a heavy blow at most every other turn, with ordinary Strikes between.

**06.9.6 Tells instead of numbers.** `[S]` + `[N]` [DL-06-16; C:P3; C:P17; revision: I-065] An adversary's stat block is sealed (00.6.3). The
narrator receives: its tells (09); `bloodied` and `down` (shown); its visible conditions; its windup;
its side's morale omens (06.11.4); and, in the PC's OFFERs, the number needed on the die. `ab.read_the_field`
and a resolved Observe of a foe (one action; against its Wits defense; reach in information items)
unseal items in this order of the player's ranking: its Guard as a number, its heaviest attack and
windup, one resistance or vulnerability, its nerve, its weak spot if it has one.

**06.9.7 No hidden adjustment.** `[D]` Once `conflict_start` has run, nothing about the opposition
changes except through this chapter's state: harm, conditions, positions, the morale clock, and
reinforcements on a clock whose omens were rendered. The DM may not add or remove a foe, alter
Vitality, or have an adversary "hold back" in secret, however the fight is going (its acts are picked openly and logged, 06.9.1) [revision: R2-M] [R1 §4 T-5; 01.7.2]. Difficulty
is set before the fight, by 09's advisory, and telegraphed (07).

### 06.10 Mobs, swarms and the solo curve

**06.10.1 Why mobs exist.** `[N]` Six goblins as six participants are twelve enemy actions a round
against the PC's three: slow to run, and nearly always lethal (T-06-13: four individual foes of the
PC's own band are "lethal" at every band but P1). The same six as one **mob** are one turn, two attacks
and one Vitality pool: a crowd the hero can wade into. Mobs are how this game fields numbers
[R1 §06, #7; R: https://pelgranepress.com/2016/07/11/13th-age-mooks-destined-to-die/;
R: https://2e.aonprd.com/Rules.aspx?ID=3365 (troops); R: https://cairnrpg.com/first-edition/cairn-srd/ (detachments)].

**06.10.2 A mob is one entity.** `[D]` + `[J:flag]` [DL-06-20; revision: I-065] A **mob** is three or more creatures of one
template acting together, written as a single adversary entity with a `members` count. `[J:flag]`
*"Are these creatures of one kind, in one group, with one purpose?"* True → one mob. False → separate
participants; a leader, a champion or anything with its own name is **never** folded into a mob.
Uncertain → a mob when they number four or more. *Worst case (J):* a crowd run as individuals or the
reverse; the advisory (T-06-13) is computed for the form chosen and shown before the fight (class ii).
- **Vitality** is pooled: `members × the template's Vitality`. Each time the pool falls past a multiple
  of one member's Vitality, a member is **defeated** (harm carries over: one great blow can drop two).
  `members_now = ceil(pool ÷ member Vitality)`.
- **One turn, two actions, no reactions** (06.1.1). One threat band, one tempo DC, one Guard, one set
  of conditions (06.10.5). One evidence source: defeating a mob is one deed at its band (03's request).
- **One position:** one band to the PC and one group; it is engaged as a whole and fills the target's
  engagement capacity by `members_now` (06.3.5); members beyond the capacity wait their turn and add
  nothing but numbers.

**06.10.3 Numbers.** `[D]` [DL-06-20; revision: I-065] A mob's attacks use the template's attack and modifier, and their severity
steps up by its **current** size (an effect step, inside the ±2 cap):

| `members_now` | 1–2 | 3–5 | 6 or more |
|---|---|---|---|
| Severity step on the mob's attacks | 0 | +1 | +2 |

A mob never Flanks and its target is never `flag.flanked` on its account: the numbers step is that
benefit, counted once. As members fall the step falls with them, so a mob weakens as it is cut down.

**06.10.4 Fighting a mob.** `[D]` [DL-06-20; DL-06-27; revision: I-065]
- A single-target attack harms the pool once.
- A **shaped** effect (06.8) that would have selected *k* members (by its cap, limited to
  `members_now`) applies its harm *k* times to the pool, and a resisted effect is rolled **once** for
  the mob and, if it lands, lands *k* times.
- A condition applied to a mob applies to the whole mob only if its source was shaped and selected at
  least half of `members_now`; otherwise it applies to **one member**, which is tracked as the fact
  `mob.<id>.member_out` for the condition's duration: `members_now` counts one fewer for numbers and
  engagement, and nothing else changes. Grapple against a mob holds one member in the same way.
- A dropped, toppled, swung or rolled **object** (T-06-8) selects at most its footprint count of members
  (hand 1, body 2, heavy 3, massive 4), and each share is at most one member's Vitality: it fells at most
  that many, whatever its rung's harm. [revision: I-075]
- Morale: each member that falls ticks the clock (06.11.3), which is why mobs usually break rather
  than die to the last.

**06.10.5 Swarms.** `[D]` [DL-06-20; revision: I-065] A **swarm** is a mob of `tiny` creatures (rats, bats, wasps, crawling
hands): it has the template flag `swarm: true`, and three differences. (a) It occupies its target's
own space: it is engaged with everyone in a group at once, to its cap of four targets, and makes one
attack roll compared to each Guard. (b) Attacks **without a shape** deal harm to it one severity rung
lighter (`eff.harm_severity_step −1`, a weapon can only kill so many rats); shaped effects deal harm
one rung heavier. (c) It cannot be grappled, shoved, flanked or made prone; fire, smoke, water and wind
are what the fiction says they are, through 06.5.10.

**06.10.6 The solo curve: what the simulation found.** `[D]` [DL-06-25; revision: I-065] `06-conflict-sim.py` plays this chapter's
economy, repetition, Fend, Defend, mastery, morale, mobs and windups, 20,000 fights per row, seeded.
The PC is a **baseline martial character**: a narrow martial calling's competence, band-appropriate
plain gear, no abilities, **no Focus**, three Strikes a turn. Lines and assumptions: T-06-12.
Section L (revision I-075): one established object dropped as the PC's first beat moves a mob fight at
most one advisory word gentler (T-06-13), and only for a heavy or massive object; under the footprint rule
(T-06-8) it never fells more members than its count, where the old burst reading felled a whole band-1 mob
of up to six on every hit (55% of fights at P1).

**T-06-12 Reference lines used by the simulation** *(PC Vitality and armor: assumed, chapters 02/07/08
own; adversary lines: inside 00.3.7's envelope, chapter 09 owns the final templates and should re-run
the script with them)*.

| Band | PC attack | PC Guard | PC Vitality | PC Strike base (mastery) | PC armor | Foe attack | Foe Guard | Foe Vitality | Foe harm | Foe reduction | Nerve (clock) | Tempo DC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | +5 | 14 | 12 | S2 | 1 | +2 | 12 | 5 | S2 | 0 | skittish (4) | 10 |
| 2 | +7 | 16 | 14 | S2 | 1 | +5 | 15 | 12 | S2 | 0 | steady (6) | 11 |
| 3 | +9 | 18 | 16 | S3 (expert) | 2 | +7 | 17 | 18 | S3 | 1 | steady (6) | 12 |
| 4 | +11 | 19 | 18 | S3 | 2 | +10 | 20 | 26 | S3; heavy blow S4 | 2 | resolute (8) | 13 |
| 5 | +12 | 20 | 20 | S4 (master) | 3 | +12 | 22 | 40 | S4; heavy blow S5 | 2 | resolute (8) | 14 |

**Targets this chapter set, and what the numbers do** (win = the opposition defeated or broken; Stag. =
the PC reached Vitality 0 at any point; "Dying" in the script is a proxy: two further hits taken while
Staggered, chapter 07 owns the real ladder):

| Target | Result (win% / Staggered% / rounds / Vitality lost) |
|---|---|
| **One foe of the PC's band, no Focus: win ≥ 80%.** | P1 100 / 0 / 1.5 / 1.0 · P2 100 / 0.5 / 2.9 / 3.7 · P3 99.7 / 3 / 3.2 / 6.3 · P4 **87** / 45 / 5.7 / 13.9 · P5 **80** / 60 / 5.0 / 17.3 — met at every band; the top two bands are meant to cost (a troll, a dragon) |
| **Fights last 3–6 rounds once foes are of consequence.** | T3 and above: 3.2–6.4 rounds; rabble 1.5–3 |
| **One foe a band above: winnable, not likely, no Focus (35–70%).** | P1 vs T2 98.7 (a lone soldier does not stop a novice; two do: 49) · P2 vs T3 **44.5** · P3 vs T4 **62** · P4 vs T5 3.7 (a legend-band foe is "lethal" to a champion alone: by design, OEQ-00-7) |
| **One foe two bands above: ≤ 10%.** | 8.0 · 0.0 · 0.4 |
| **Two foes of the PC's band: hard.** | P1 99.9 · P2 90 / 22 · P3 73 / 48 · P4 3 · P5 3 |
| **A mob lets a crowd be fought.** | four T2 as individuals against P2: 3%; the same four as a mob: 43%; P3 against a T2 mob of six: 95 / 15; P1 against a T1 mob of six: 95 / 27 |
| **Focus accelerates; it does not decide (I-006).** | a push on the first Strike each turn: P2 vs T3 44.5 → 72 · P3 vs T4 62 → 84 · P4 vs T4 87 → 96 · P3 vs two T3 73 → 90; rounds fall by about a fifth, Vitality lost by a fifth to a third |
| **A broad calling pays for breadth.** | no mastery rung until tier 4: P3 vs T3 87 / 38 (specialist 99.7 / 3); P4 vs T4 73 / 64 (specialist 87 / 45) |
| **Morale ends fights.** | against groups, 60–100% of wins are breaks, not exterminations; against fearless foes two T3 fall from 73% to 68% and a T1 mob of six from 95% to 74% |

**On issue I-006.** The chapter 05 finding (a tier-3 character who spends no Focus wins 0.1% against
one T3 foe) was a caster reduced to a quarterstaff (+2, S2, Guard 12). This simulation reproduces it
(0.4%; against one T2 foe the same Spent caster wins 65%) and shows it is not the martial baseline: a
tier-3 specialist with no Focus wins 99.7% against that foe, a broad-calling fighter 87%. What changed
is 06.4.5 (mastery), the three-action economy against the adversary's two, and Fend. A Spent caster
remains nearly helpless in melee against an elite, which is the correct picture of that character and
is answered by the exits (Defend, Withdraw, Retreat, a chase: 70% from `band.near`) and by keeping a
last point of Focus; this chapter recommended, and asked of 05, one zero-cost attack working per magic
branch at Moderate severity so that "Spent" is weak, not weaponless (Interface requests). **Done
(revision I-009):** 05.7.11's branch workings (Force Bolt, Rebuke, Wild Lash) cost no Focus and one
action, and their severity follows the casting school's grade as a weapon's follows mastery (06.4.5).
Simulation J (`06-conflict-sim.py`): a Spent tier-3 caster now beats one T3 80.7–91.0% (74.5–86.8% when
it Fends), a new caster beats one T2 92.8–93.6%, and at every band the working stays below the
no-Focus specialist (P4 11–48% against 87%, P5 7–30% against 80%).

**T-06-13 The advisory matrix** is in Tables. It is this chapter's contract with chapter 09
(00.17.1 Q5): `threat_advisory` should return the cell's word for the encounter's shape, read one row
harsher for a PC with no martial calling and one row gentler for a PC with a companion in the fight.
Chapter 09 adopted it, re-run on the final templates with adversary Fend, as **T-09-9** (five cells
harsher) with the estimator **PR-09-4**, which is now the contract (00.3.7, amended); the companion
adjustment is 09.6.3 as refined by 16.7.11 (one word gentler with at least one able ally; a hard estimate
whose no-ally win is below 75% stays hard) [integration: IR ch.09 to 06, IR ch.16 to 06 (f)].

### 06.11 Morale, surrender and parley

**06.11.1 Morale is a clock the player can work.** `[D]` Every opposing side that can feel fear has
one **morale clock**, an instance of 00.8's primitive: named for what it measures ("The reavers'
nerve"), kind `tug`, visibility `sensed`, owned by this chapter. It replaces dice-and-threshold morale
checks with listed, visible causes: the player sees the foes waver (omens are mandatory, INV-14) and
can push on purpose, by killing the leader, by a show of force, by an offer of quarter
[R: https://oldschoolessentials.necroticgnome.com/srd/index.php/Morale_(Optional_Rule) (checks at the
first death and at half strength: the two moments kept as tick sources);
R: https://billhook.bearblog.dev/saves-and-morale-in-shadowdark/; R1 §4 T-5; `ab.commanding_ground`
already ticks "the enemy's morale clock"; DL-06-18].

**06.11.2 Size: nerve.** `[D]` [DL-06-18; revision: I-065] The clock's size is the side's **nerve**, a field of the archetype (09:
`morale`), read from the side's leader if it has one, else from its most numerous template:

| Nerve | Segments | Anchor | Examples |
|---|---|---|---|
| `skittish` | 4 | fights for gain or food, not to the death | bandits' hirelings, goblins, wolves, a hungry bear |
| `steady` | 6 | trained or committed | soldiers, guards, a pack with its leader, cultists |
| `resolute` | 8 | sworn, cornered in its home, or proud | knights, a mother defending young, an ogre in its den, zealots |
| `fearless` | no clock | cannot or will not break | mindless undead, constructs, the enthralled; anything immune to `trait.nature.mental` |

**06.11.3 Tick sources (closed).** `[D]` [DL-06-18; revision: I-065] (`data/conflict.yaml#morale.tick_sources`.) The DM adds none.

| Event | Ticks |
|---|---|
| a member of the side is defeated | +1 (its **leader**: +2) |
| the side's **strength** (current Vitality of members still in the fight ÷ their maximum) first falls to half or less | +2, once |
| …first falls to a quarter or less | +2, once |
| an individual member (not a mob) is first `bloodied` | +1 |
| one blow deals 8 or more harm to a member | +1 |
| `cond.frightened` is applied to a member | +1, at most once a round |
| the PC's Talk beat aimed at their will (threaten, demand surrender, offer quarter, a show of force) succeeds against the leader's Resolve defense | + delivered reach |
| an effect that says so (`eff.tick_clock` on `clk.morale.*`) | as stated |
| the PC is first `bloodied` | −1 |
| the PC is Staggered | −2 |
| a companion of the PC is defeated | −1 |
| reinforcements for the side arrive | −2 |
| the side's leader spends an action to rally (a behavior row; a fortune check against Moderate) | − delivered reach |

**06.11.4 Omens.** `[N]` + `[D]` [DL-06-18; DL-00A-20; revision: I-065] Every tick renders one omen of the clock's stage (00.8.4), chosen by
the engine from the template or these defaults: *stirring* — "one of them glances back at the door";
"their shouting has gone quiet"; *building* — "they give ground a step at a time"; "the big one looks
to the others and none of them meet his eye"; *imminent* — "one has already lowered his blade";
"they are calling to each other, and it is not orders". The fill is never stated.

**06.11.5 Breaking.** `[D]` + `[T]` [DL-06-18; revision: I-065] When the clock completes, the side **breaks**: every member gains
`cond.broken`, and on its turn each follows its archetype's `morale_break.then` (09), or this default
by its state:

| Member's state | It… |
|---|---|
| can get away (not `flag.cornered`, not held, its pace at least the PC's or the PC engaged elsewhere) | **flees**: Withdraws if engaged, then Moves away each turn; it leaves the conflict at `band.distant` (06.2.5). The PC may let it go, shoot it as it runs, or give chase (06.12.6) |
| cannot get away and is a thinking creature (`creature.folk` and any template with `speaks`) | **yields**: drops its weapon and asks quarter (06.11.7) |
| cannot get away and is a beast or the like | **cowers** (Defend only), and fights only if attacked (`cond.broken`'s exception) |
| is `fearless` | is unaffected; a fearless member of a broken side fights on alone |

A break is a defeat of the side for chapter 03's evidence, chapter 08's generator circumstance and the
martial Focus trigger only for members actually **defeated** before it; those who fled or yielded are
recorded as `drive_off` and `yielded`. `on_defeat` fires for each with the frame id that caused the
completing tick.

**06.11.6 A break is final for the fight.** `[D]` [DL-06-18; revision: I-065] A completed morale clock closes. If reinforcements
arrive afterward, they form a new side with a new clock; broken members who have not left may rejoin it
only if its leader rallies them (one action, fortune check against Hard).

**06.11.7 Yielding: theirs and yours.** `[D]` + `[J:flag]` [DL-06-18; C:VII; C:P16; R5 CF-10; revision: I-065]
- **A foe yields** by its break row or by a successful demand (a Talk whose ticks complete the clock).
  A yielded foe is `defeated(x)` with disposition `yielded`: it takes no hostile action while its
  terms hold. The PC decides what to do with it; chapter 15 runs the talk and chapter 07 the keeping
  of prisoners. Striking a yielded foe is legal as a beat and is recorded by chapter 03 (a
  `conduct.mercy` event, negative).
- **A foe that will never yield** has that as a recorded refusal (15); demanding it is G4 for that
  intent and the redirect names what the foe *would* accept (to be let run, a ransom, a duel).
- **The PC yields** with the named use of Talk (00.12.5): free, at any moment (06.1.4), never
  refused as a declaration. Whether the other side **accepts** is `[D]` from its `defeat_disposition`
  (09) and objective: `capture`, `rob`, `ransom`, `drive_off` accept; `kill` and `drag_to_lair` do not
  accept by default, and the DM says so *before* the player commits to yielding (it is a G0 answer
  from state). Chapter 07 owns everything after acceptance.
- **Parley.** Any Talk beat proposing to stop (one action; against the leader's Resolve defense, with
  ch.15's standing) that delivers reach 2 or more creates a **truce**: `conflict_end` is marked with
  outcome `truce`, bands and facts persist in the scene, and the first attack-trait beat by anyone
  marks a new `conflict_start` with the old positions. `[J:flag]` *"Does a recorded objective of this
  side forbid stopping (it was sent to kill; it is starving)?"* True → G4 for the truce, with what it
  would stop for. *Worst case (J):* a truce allowed that the objective forbade: one round's pause, undone
  by that side's next behavior row (class iv).

### 06.12 Getting away, and running down

**06.12.1 Three ways out.** `[D]` [DL-06-21; C:P16; R5 CF-09; revision: I-065] A participant leaves a fight it has not won by one of:
1. **Yield** (06.11.7).
2. **Retreat** (00.12.5; chapter 07): the always-legal withdrawal whose outcome and price chapter 07
   states before the player commits. It needs only that the PC is not `flag.cornered`, `cond.restrained`
   or `cond.pinned`. Where chapter 07 rules the escape **uncertain**, or the player prefers to try for
   a clean escape with no stated price, it is resolved as a **chase**.
3. **Flight and pursuit**: the chase, below.

**06.12.2 When a chase begins.** `[T]` + `[D]` [DL-06-21; revision: I-065] A chase begins when the PC, engaged with no enemy,
declares flight and at least one enemy's behavior says it pursues (default: yes for objectives `kill`,
`capture` and `rob` unless the side is broken; beasts pursue while hungry; guards pursue to the edge of
their post). If none pursues, the PC simply leaves (06.2.5). The situation tag becomes
`situation.conflict.chase`; turns give way to **chase rounds**, in which each side makes **one** beat.
The engine creates two racing clocks (00.8.5; templates in `data/conflict.yaml#clock_templates`):

| Clock | Kind · visibility | Size | Starts at | Ticked by |
|---|---|---|---|---|
| `clk.escape` "The way clear" | progress · public | **6** | 0 | the fleer's flight beat: delivered reach |
| `clk.pursuit` "They close in" | danger · public | **8** | by the nearest pursuer's band: close 2, near 1, far 0 | the pursuers' beat: delivered reach; and `cost.time` paid on the fleer's beats: U(severity) |

**06.12.3 The flight beat.** `[J:enum]` + `[D]` [DL-06-21; C:P8; revision: I-065] *Anchor: yes.* Each chase round the fleer declares one
beat by any method that could gain ground: run (Move), climb, leap or swim (Exert), lose them (Sneak:
needs a `cover` or `veil` feature or a crowd), burst through (Force), bar the way behind (Handle or
Force on a `barrier` or `loose_object`), throw them off (Setup), call on bystanders (Talk). The
obstacle is the round's **ground**: the engine draws it from `tbl.chase_ground` for the terrain
(T-06-9b: a tier and what it is: "a crowded market lane, Moderate"), writes it as a feature, and it is
the DC for both sides this round unless the method opposes a pursuer directly. (A way barred **before** the
Retreat is declared is not a chase beat: a pursuer with a shut `barrier` between it and the PC is not ABLE,
and the retreat is clean, 07.4.3 [revision: I-076].) When a recorded
feature lies on the stated route (the door, the plank, the wall just named), that feature is the round's
ground in place of a draw. Stakes **Risky**;
threatened cost `cost.time` (the pursuit clock ticks: 1 at S2, 2 at S3), alternate `cost.footing`.
Reach Standard: 2 ticks; levers, the push and the "go big" trade apply as anywhere. **Varied approach**
(01.14.6): the same verb may not tick the escape clock on two rounds running, so a chase is a string of
different ideas. Knobs: `dc` (ground tier → opposed by the lead pursuer); `reach_unit` (ticks);
`time_cost` (a chase round → an interval, for a long pursuit across country, 10); `stakes`.
*Decision* `[J:enum]`: the anchor verb for the declared method, as 06.5.10 decision 1. *Worst case (J):* a
neighboring verb, same DC, same ticks (class i).

**06.12.4 The pursuit beat and the finish.** `[D]` [DL-06-21; revision: I-065] Handler `h.06.chase_round`: after the fleer's beat
the engine makes one fortune check for the pursuing side: the lead pursuer's best of Might or Agility
modifier with its competence, against the round's ground. Its reach is Standard (2 ticks), **Limited**
if the pursuers' pace is lower than the fleer's, **Great** if higher (a rider after a runner). A
pursuer with a ranged attack may instead shoot (an ordinary attack on the fleer at the current band,
which stays what the pursuit clock implies: under half, `far`; half or more, `near`; one from full,
`close`).
- **`clk.escape` completes first** (the acting side's ticks land first, 00.8.5): the fleer is at
  `band.distant` and leaves the conflict; `clk.pursuit` is voided. What the pursuers do next is
  chapter 10's (tracking) and 11's (a grudge).
- **`clk.pursuit` completes**: the fleer is caught: the lead pursuer is at `band.engaged`, the fleer
  gains **`flag.cornered`**, ordinary rounds resume with the pursuers acting first, and the fleer may
  not start another chase until the flag is cleared (06.3.6).
*Simulated:* a P1 character fleeing T2 pursuers escapes 70% of the time from `band.near` (60% from
close, 79% from far), in about 3.4 chase rounds; 81% with a cited lever each round; 51% from riders;
45% for a character with no competence in running or climbing (06-conflict-sim, section I). Escape is
likelier than not, and never free.

**06.12.5 Hiding instead of running.** `[D]` [DL-06-21; revision: I-065] A fleer who reaches a `cover` or `veil` feature with the
pursuit clock under half may Sneak against the pursuers' highest notice: reach 3 or more completes the
escape clock at once (they lose the trail); reach 2 ticks 2; failure is `cost.exposure` and ticks the
pursuit clock by U(severity).

**06.12.6 The PC as pursuer.** `[D]` [DL-06-21; revision: I-065] The mirror: the quarry's flight is `clk.quarry_away` (danger,
public, 6, ticked by the engine's fortune check for the quarry: 2 a round on a success), and the PC's
beats tick `clk.run_down` (progress, public, 8, starting at close 2 / near 1 / far 0) by delivered
reach, with the same ground, the same varied-approach rule and stakes **Safe** unless the ground
itself is dangerous. Completion of `clk.run_down`: the PC is engaged with the quarry, which is
`flag.cornered`. A shot at a running quarry is an ordinary Strike at the band the clocks imply.

### 06.13 Ending a conflict

**06.13.1 When it ends.** `[T]` + `[D]` [R1 §06; DL-00A-12; revision: I-065] `h.06.objective_check` runs at every `round` boundary and after
any defeat, break, yield, truce or clock completion. `conflict_end` is marked at the first of:
(a) no hostile participant is both able and willing to act (all defeated, fled, yielded or broken and
cowering) [12's T-12-3]; (b) a side's **objective** is achieved and its behavior list says it then
leaves; (c) a truce (06.11.7); (d) the PC has left (escape, Retreat, an accepted Yield) or is defeated
(07). The time mode returns to the previous mode. If anyone is Dying when it ends, time stays in rounds
until each Dying character's ladder resolves (`h.07.after_conflict`, 07.6.1) [integration: IR ch.07 to 06].

**06.13.2 Objectives.** `[J:enum]` + `[D]` At `conflict_start` each side's objective is recorded from
this closed list, the opposition's from its `defeat_disposition` and situation (09, 11), the PC's from
the player's stated intent (default `defeat`):
`defeat` (put the other side out of the fight) · `kill` (a named target) · `capture` (a named target
alive) · `rob` · `drive_off` · `escape` · `hold` (keep a place or person until a named clock
completes) · `reach` (get to a place or person) · `protect` (a named person or thing) · `delay`.
Objectives make the fight's end legible ("they want the ledger, not you") and feed attention (06.9.3)
and acceptance of a Yield. *Worst case (J) of a wrong classification:* the opposition leaves a round early
or late, or accepts a Yield it should not (class iv: the next behavior row corrects it)
[R1 §06 "victory conditions should be a field of the encounter"].

**06.13.3 Defeat.** `[D]` [DL-06-23; revision: I-065] An adversary at 0 Vitality is **defeated** and out of the fight. Whether it
is dead, Dying, unconscious or maimed is chapter 07's, read from the defeating frame's harm mode
(06.4.8) and the NPC's depth. The engine fires **`on_defeat`** for the entity that defeated it, carrying
`{defeated: id, frame_id, ability_id | null, harm_mode, manner: defeated | drive_off | yielded}`
(03's request), which chapters 03 (evidence), 05 (the martial Focus trigger), 08 (the generator's
circumstance) and 04 (the Taking) read. A mob's defeat fires it once.

**06.13.4 What `conflict_end` clears.** `[D]` [C:VI; C:P16; revision: I-065] Handler `h.06.clear_conflict_state` (phase 1): range
bands, engagement links, groups and conflict-only flags (`flanked`, `lined_up`, `in_chokepoint`) are
cleared and each participant's place returns to the place graph (10); `flag.hidden`, `flag.mounted`,
`flag.elevated`, `flag.in_cover`, `flag.obscured`, `flag.aloft` and `flag.cornered` persist as scene
state if still true; conditions and effects with duration `conflict` end; **stances end** (unless their
text says `scene`); Defend, Fend, Aim, windup, tempo and momentum facts end; the diminishing counter
resets; morale and chase clocks close. Then `h.05.conflict_recharge` and `h.07.after_conflict` (3),
`h.12.intensity` (9). The narration of the end must say who is down, who fled, who yielded, and what
the PC can now do (P16).

### 06.14 Companions and allies

**06.14.1 A companion has no turn.** `[D]` Whatever fights on the PC's side — a hound, a hireling, a
sworn sword, a summoned servant, a raised dead, an automaton — is a **companion** for this chapter: it
has **no actions of its own**, one reaction, and its own position, defenses, Vitality and conditions
(templates: 16; harm: 07). It acts in exactly three ways (00.17.1 Q8; INV-11):
1. when the PC **commands** it (06.14.2);
2. by its **reaction** (06.14.4);
3. by **hooks and passives** of its own (an aura, a `prevent`), which need no action.
A companion given no command "uses no actions except to defend itself": it keeps its place, keeps a
hold or a guard it was ordered to keep, and is a legal target
[R: https://2e.aonprd.com/Traits.aspx?ID=653 (minions act when commanded); R1 §06, G-5; R5 CF-13].

**06.14.2 Command.**
```
### 06.14.2  Command a companion                                  [J:flag] [D]
Trigger [T]:        the PC declares that a companion does something, in conflict mode
Loads in:           situation.conflict.*
License check:      basic verb: verb.talk (a named use: Command); the COMPANION must pass the gate
                    for the commanded beat (its own verbs, licenses and abilities, 16)
Decisions (J):      1. CAN HEAR [J:flag]: "Can this companion perceive the command?" True only when
                       it is within band.near and neither it is cond.deafened, cond.unconscious or
                       cond.stunned nor the PC cond.silenced or cond.choking; a companion trained to
                       hand signs (16) needs sight instead; a bonded beast (`hears: bond`, 16.1.2)
                       perceives the PC's intent at any distance at which the PC could call it.
                       Uncertain -> false. [integration: IR ch.16 to 06 (e)]
                    2. WILL [D, from 16]: a companion refuses a command its loyalty rules forbid;
                       16.7.2 decides it (the ally's standing rung, its contract or oath, and the
                       order allowed); the refusal is announced before the action is spent
                       [integration: IR ch.16 to 06 (a)].
Computation [D]:    cost: 1 PC action (2 if the commanded beat costs 2 in T-06-1). The companion at
                    once performs ONE beat: any verb or ability it could attempt alone. The beat is
                    framed with the COMPANION's attribute, competence, edge and status, shown to the
                    player as an OFFER (it is the player's declaration), and resolved by the engine.
                    Repetition: each companion keeps its own window per PC turn (its second attack
                    this turn takes -2). A commanded Help gives the PC's next beat one Precision
                    lever (01.14.8: the companion must be eligible). A commanded Move places the
                    companion; a commanded Flank, Screen, Grapple or Setup does what that rule says.
Stakes:             the commanded beat's own; its costs land on the companion (07 applies harm).
State writes:       the PC's action; the companion's beat, position, conditions; evidence carries the
                    grounding kind `companion` (03.1.7).
Narration may not imply: that the companion did anything it was not commanded to do, except by its
                    reaction or standing order.
Worst case (J):     a command allowed that could not be heard: one companion beat (class i).
Examples:           inside: "Brack, take him!" -> 1 action; the hound Grapples the cutthroat with
                    its own +4. outside: the hound is across a roaring millrace (band.far) -> cannot
                    hear -> the PC must close or signal.
                    non-example: "My three hirelings each attack while I do my own three things" ->
                    three commands are the PC's three actions; there are no others (INV-11).
Anchor:             yes. Intent verbs: order, send, sic, tell (an ally) to, have (an ally) do. Knobs:
                    action_cost (1 -> 2 for a two-action beat; 1 -> 0 never); targets (one companion
                    -> every companion in one group for ONE identical simple beat: Move, Defend or
                    a standing order, never an attack-trait beat).
Basis:              [00.17.1 Q8] [INV-11] [R: https://2e.aonprd.com/Traits.aspx?ID=653] [DL-06-19]
```

**06.14.3 What a companion is worth.** `[N]` [DL-06-19; revision: I-065] A command trades one PC action for one companion beat, so
a companion never adds a beat to the round. It adds what one body cannot be: a second position (a
flank, a screen, a held door), a held foe, a second set of defenses for the opposition to spend
attacks on (06.9.3), a reaction, and capabilities the PC lacks. Commanded Strikes escape the PC's own
repetition snags, which is a real but bounded gain: one action each, the companion's modifier, and
never more than the retinue Presence allows (00.4.4).

**06.14.4 Standing orders and companion reactions.** `[D]` [DL-06-19; C:V; revision: I-065] A command may instead set one **standing
order** (closed list; `data/conflict.yaml#companion_command.standing_orders`), which lasts until
changed, the companion is defeated, or `conflict_end`. An order may also be set by a chapter-16 rule, at no
PC action: the default orders at `conflict_start` (`h.16.conflict_orders`, 16.7.3), *stay back* when an ally
loses heart (16.7.4), and *guard me* toward a Dying PC (16.7.5) [integration: IR ch.16 to 06 (b)]. Under an order the companion still takes no
action; the order says what it *keeps* and what its **one reaction** is for:

| Order | Keeps | Its reaction |
|---|---|---|
| **guard me** | stays in the PC's group; moves with the PC | Intercept: takes one hit meant for the PC (06.6.7) |
| **hold him** | a hold it has (it need not be commanded again to maintain it) | resists the first attempt to break free each round with its Might defense +2 (an engine snag on the breaker) |
| **harry that one** | engagement with the named enemy, following it one band a round | Opportunity Strike against that enemy (06.6.2) |
| **hold this ground** | its place; `flag.in_chokepoint` if it stands in one; it screens whoever is behind it | Opportunity Strike against anyone passing |
| **stay back** | `band.near` from every enemy it can see, moving one band a round to keep it | Fend |

With no order a companion's reaction is Fend. An order's movement is free because it is bounded (one
band a round, toward a state named in advance) and adds no beat.

**06.14.5 Companions as targets, and as casualties.** `[D]` [DL-06-19; revision: I-065] Adversaries choose among the PC and
companions by 06.9.3. A companion at 0 Vitality is defeated under chapter 07's companion rules
(protected by Key 1; no last-chance menu). A companion's defeat ticks the opposing morale clock down
by one (06.11.3).

### 06.15 Mounted conflict

**06.15.1 Mount and rider are one participant.** `[D]` [DL-16-24; R5 CF-14; revision: I-065] A rider with `flag.mounted` and its mount share
one position and one turn: **the rider's**. The mount is a companion (06.14) that needs no Command to
*carry*: its movement is the rider's Move, at the mount's pace (a horse: 2, so transitions cost 1, 1,
1, 2). The mount takes no other action unless commanded (a kick, a bite: one action, the mount's own
attack). Each has its own Vitality and conditions; attacks name which is aimed at.

**06.15.2 Riding is basic; fighting from the saddle is licensed.** `[D]` [C:VII; R5 CF-14; revision: I-065] Moving a mount over passable
ground is `verb.handle` (ride) and usually Trivial. Making attack-trait beats while mounted, or
controlling a mount amid a melee, is the scope of **`lic.training.martial_mounted`**. Without it the
gate is G3 and the license's own crude fallback applies (`data/licenses.yaml`): a Handle check at DC
+5 to "stay in the saddle and strike as you can", after which the Strike is made at reach Limited, and
`cond.off_balance` on a failed Handle. With it:
- the rider holds **`flag.elevated`** against enemies on foot of the mount's size or smaller (T-06-4);
- a mounted **charge** (06.5.7) with a lance, spear or heavy weapon holds an **Amplifying** lever in
  place of the Precision one (the mount's mass), and a `lance` strikes at one action from the saddle;
- leaving engagement provokes as usual; the mount's pace lets the rider Withdraw and still cross a
  band in the same turn;
- shooting from a moving mount takes the *crowded* snag unless an ability removes it.

**06.15.3 Unhorsing and a mount's fall.** `[D]` [R5 CF-14; revision: I-065] A Force or Grapple against the rider that delivers
reach 2 or more unhorses: the rider lands `cond.prone` at `band.engaged` beside the mount and takes a
10-ft fall's harm (S2) only if the mount was moving this round. If the mount is defeated the rider
makes a resisted Evade against Moderate: failure is `cond.prone` and S2 harm; success lands standing.
A panicked mount (`cond.frightened` S3, or `cond.broken`) carries its rider one band away from the
source each round unless the rider spends an action and succeeds at Handle (Presence or Agility)
against Moderate.

**06.15.4 Fighting a mounted foe.** `[D]` [R5 CF-14; revision: I-065] From the ground, melee Strikes at the rider take the *from
below* snag without a `reach` weapon; the mount may be attacked instead with none. A `reach` weapon set
against a charge is the Opportunity Strike of 06.6.2 (d) (and `ab.set_spear` improves it).

**06.15.5 On a creature's back.** `[D]` [R5 CF-14; DL-06-07; revision: I-065] A character who has climbed onto a larger creature (06.5.2)
has `flag.mounted` on it without controlling it: it is engaged with it whatever the creature does,
goes where it goes, its melee Strikes at the creature hold a Precision lever, and the creature's own
attacks against it take two snags unless the template lists a way to reach its own back. The creature
may spend an action to **shake it off**: Force against the rider's higher of Might or Agility defense;
reach 2 or more throws the rider (prone, `band.close`, a fall by the creature's height). Staying on
through a creature's Move needs nothing; staying on through its roll, plunge or flight is an Exert
against the tier the template states (default Hard), Risky.

---

## Procedures

**PR-06-1 Starting a conflict.** `[D]` (at `conflict_start`; handler `h.06.tempo_setup`)
0. The trigger is the DM's `change fight`, or an attack roll whose start-the-fight field says yes or is left blank
   with no fight on (06.2.1) [revision: R2-M2; DL-06-42]; code never starts a fight from a beat's words.
1. List participants; assign sides; record each side's objective (06.13.2).
2. For each participant other than the PC: set its band to the PC as the DM states it (06.3.9; default by the opening attack's verb and weapon, else near, logged)
   [revision: R2-M], and its group and flags from recorded scene facts, with `set_position`. Write engagement links for any pair already at
   blade's reach.
3. Run the unaware test per participant (06.2.4); apply `cond.surprised`.
4. Create the opposing side's morale clock at its nerve's size (06.11.2), unless `fearless`.
5. Roll the PC's tempo check; store the total; compute the order (06.2.2); move surprised
   participants to the end of round 1.
6. Ask chapter 09 for `threat_advisory` if it was not already shown (07 consumes `lethal`).
7. Load `situation.conflict.*` cards. Narrate the opening: every participant's band to the PC in
   T-12-11's words, every flag on the PC, features in reach, who looks ready and who does not.

**PR-06-2 A round.** `[D]`
1. For each participant in order: `turn_start` (06.1.8 step 1) → its actions → `turn_end`.
   - The PC: up to three beats, each through 01's pipeline; reactions offered to adversaries per
     06.6.5.
   - An adversary: PR-06-6.
   - After each beat: write state; fire hooks; test `h.06.objective_check` conditions that can end the
     fight at once (a defeat, a break, a yield).
2. After the last turn: the `round` boundary (06.2.3).
3. Narrate from the record only (12.2.8): each band, link, flag and visible condition that changed
   is named once.

**PR-06-3 Resolving an attack and its harm.** `[D]`
1. GATE: verb or license; reach (06.4.3 decision 1); restrictions from the actor's conditions.
2. FRAME: attribute; primary deed tag (the weapon's, 06.4.2); DC = the defense of T-06-5; cited
   levers and snags, then engine snags (repetition, called, nonlethal, Defend, Fend); stakes Safe unless
   traded; reach Standard unless a lever, push or trade moves it; harm mode.
3. Offer reactions to the target (`on_check_against`): Fend or the slot's owner; prevent and redirect
   effects resolve first (00.10.7).
4. OFFER (PC) or auto (adversary); ROLL; degree.
5. On success or better: dealer's side (06.4.6) → receiver's side → `apply_harm(target, severity,
   harm_tags, source {entity, frame_id}, lethal: frame.lethal, mode, dealt)`, passing `dealt`, the
   dealer-side amount already computed here (07.2.1) [integration: IR ch.07 to 06]. Fire `on_attack_hit`,
   `on_hit_taken`, `on_harm_dealt`, `on_harm_taken`, `on_vitality_threshold`; riders apply.
6. On failure: `on_attack_miss`; reactions keyed to a miss (`ab.riposte`); the cost, if the frame was
   Risky or the degree a critical failure.
7. Morale sources (06.11.3); attention score (06.9.3); ammunition and `loaded`; a spoiled windup
   (06.9.5) if the harm was S3 or more.
8. If the target is at 0 Vitality: defeat (06.13.3) → `on_defeat` → the objective check.

**PR-06-4 Changing position.** `[D]` (`set_position`)
1. Validate the cause: a resolved Move or maneuver's delivered reach, a cost, an effect of operation
   `move`, a `[T]` of this chapter. Refuse any other.
2. Compute the cost paid against T-06-1 with pace, `slowed`, `prone`, difficult ground.
3. Before the change: offer Opportunity Strikes it provokes (06.6.2); resolve them.
4. Write the band (both directions), links, group and flags; clear flags the change ends (T-06-4).
5. Fire `on_move`. Return the changes as narration obligations in T-12-11's words.

**PR-06-5 Resolving a shaped effect.** `[D]`
1. Take the primary target or point from the declaration or behavior row.
2. Apply the shapes in T-06-15's order; select by each shape's priority steps and tie-breaks; stop at
   each cap and at six in all. For a mob, compute *k* (06.10.4).
3. Show the selected names in the OFFER (PC effects), with allies marked.
4. Aimed: one roll; compare to each defense. Resisted: each target rolls; a mob once.
5. Apply harm per target through PR-06-3 steps 5–8; apply conditions through PR-00-5 (control
   diminishes per target).

**PR-06-6 An adversary's turn.** `[D]` + `[N]`
1. `turn_start`. If the adversary cannot act (`stunned`, `unconscious`), skip to step 6.
2. Actions available: 2, less `dazed` or `surprised`.
3. For each action: take the DM's pick (06.9.1, from T-06-16), else the first true legal row of the behavior
   list (09, else 06.9.4), logged as a default [revision: R2-M; DL-06-40]; resolve it: a Move by PR-06-4; an attack
   by PR-06-3 with the target the DM picked, else the PC; a Windup by writing the fact and its tell; a break row by 06.11.5.
4. A row that cannot be carried out (no path, no reach) is skipped for this action and logged.
5. Never re-evaluate a resolved action; never substitute an action the DM's pick (or the logged default) did not produce.
6. `turn_end`. The narration packet holds: what it did, bands and flags changed, conditions applied,
   harm as the fiction of its severity, its tell if it wound up, any morale omen.

**PR-06-7 Morale.** `[D]` On each event of 06.11.3: `tick_clock` with that source (the tool refuses
others); render the stage's omen; on completion apply `cond.broken` to the side, switch behaviors,
fire the objective check. A demand for surrender is PR-06-3 without harm: Talk against the leader's
Resolve defense, ticks = delivered reach.

**PR-06-8 A chase round.** `[D]`
1. Draw the round's ground from `tbl.chase_ground` for the terrain (no repeat of the last draw);
   write it as a feature with its tier.
2. The fleer's (or pursuer-PC's) beat: anchor by method (06.12.3); refuse the verb used last round;
   frame against the ground tier or the opposed defense; OFFER; roll; tick the PC's clock by delivered
   reach; apply any `cost.time` to the other clock.
3. If the PC's clock completed, stop (00.8.5: the acting side first).
4. The other side's fortune check against the same ground; tick its clock.
5. Completion effects (06.12.4, 06.12.6). Otherwise the next chase round; `advance_time` one round.

**PR-06-9 Commanding a companion.** `[D]` Check hearing and will (06.14.2); spend the PC's action;
frame the companion's beat with its own numbers; OFFER; resolve through the pipeline with the
companion as actor; or write the standing order and its reaction (06.14.4).

**PR-06-10 Ending.** `[D]` On `conflict_end`: run `h.06.clear_conflict_state`; record each
adversary's disposition (defeated, fled, yielded) with the frame ids; hand to 07 (`h.07.after_conflict`),
05 (`h.05.conflict_recharge`), 03 (evidence settlement), 08 (generation from resolved defeats only,
00.11.2), 12 (mode change, intensity). Narrate the aftermath and one actionable next step (P16).

---

## Tables

T-06-1 (action costs), T-06-4 (flags), T-06-5 (defenses), T-06-6 and T-06-7 (weapons), T-06-8
(improvised objects), T-06-10 (conditions), T-06-11 (armor reference), T-06-12 (reference lines) and
T-06-15 (shapes) are in Rules. Data: `data/conflict.yaml`, `data/conditions.yaml` (canonical).

**T-06-2 The PC's turn at a glance.**

| Spend | To | See |
|---|---|---|
| 1 action | Strike (light, one-handed, bow) · Grapple · shove or trip · Setup · Aim · Defend · Move one step · Withdraw · stand · hide · use or grab something · command a companion · threaten or parley · Ready · study a foe | T-06-1 |
| 2 actions | Strike with a heavy weapon · dash from near to far · reload a heavy crossbow · Full defense · command a two-action beat | T-06-1 |
| 3 actions | run from far to the edge of sight | T-06-1 |
| free | a sentence · drop or let go · one draw, stow or pick-up · end a stance · Yield · ask the odds | 06.1.4 |
| the reaction | Fend one attack · an Opportunity Strike · a readied beat · a reaction ability | 06.6 |
| Focus, with a beat | a push (reach +1 or stakes −1) · a rider · a flare | 05.6.7–05.6.8 |
| a trade, with a beat | go big (reach +1, stakes +1) · play it safe (both −1) | 01.7.3 |

**T-06-3 Movement** (restating T-06-1 for the anchor index).

| Transition | Actions at pace 1 | Pace 2 | With `cond.slowed`, `prone` or difficult ground |
|---|---|---|---|
| engaged ↔ close | 1 | 1 | 2 |
| close ↔ near | 1 | 1 | 2 |
| near ↔ far | 2 | 1 | 3 |
| far ↔ distant | 3 | 2 | not within one turn: a chase or travel |

**T-06-9 Environment and improvisation anchors.** `[D]` Each row is a ready ruling: the anchor card,
the knobs turned (never more than two), the DC source, and what success gives. A case not listed is
ruled by 06.5.10 and logged; a logged ruling is reused before this table is consulted again (INV-19).
(`data/conflict.yaml#environment_anchors`.)

| # | "I…" | Anchor | Knobs turned | Rolled against | On a success (reach 2) | Notes |
|---|---|---|---|---|---|---|
| 1 | throw sand, flour, ash in its eyes | Setup | `condition` → blinded | Guard | `cond.blinded` ENT (control) | needs the stuff established within reach |
| 2 | fling my cloak over its head | Setup | `condition` → blinded | Guard | as 1; the cloak is on the foe | the foe ends it with 1 action |
| 3 | kick the table over for cover | Force (object) | `reach_unit` → feature state | the table's tier (Easy) | a `cover` feature in my group; `flag.in_cover` costs a further Evade or Move | loud |
| 4 | swing on the chandelier or rope across the room | Exert | `dc` → re-derived tier (Hard; Moderate for a short swing); `stakes` → the drop | the tier | I am at the place named, one or two bands crossed in one action | precedent r.0412 (WE-00-9) |
| 5 | cut the rope and drop the chandelier (sacks, a hoist's load) on them | Strike | `targets` → the rope; `harm_severity` → the object's rung | the higher of the rope's tier and each Guard | up to the object's count under it (T-06-8 footprint: heavy 3, massive 4; 06.5.10 decision 3; shape `burst` on that group) take the object's harm; a mob takes that many shares, each at most one member's Vitality (06.10.4) | WE-01-9; pinning needs reach 3+; the object has fallen and is not dropped again [revision: I-075] |
| 6 | shove it into the fire, off the ledge, into the millrace | Force | `reach_unit` → position into a feature | higher of Might or Agility defense | pushed one band into the feature: the hazard's entry or the fall applies | the OFFER states the hazard's severity |
| 7 | kick the brazier (lamp, cauldron) over at them | Strike | `targets` → the object; `harm_severity`/`harm_tags` → the hazard's | higher of the object's tier (Easy) and Guard | S2 `harm.fire.flame`, and `cond.burning` only at reach 3+; a `hazard` feature (fire) remains there | the fire is now a fact for both sides |
| 8 | pull the rug or tarpaulin from under them | Force | `targets` → those standing on it (`cone`, cap 4) | each one's higher of Might or Agility defense, one roll | `cond.prone` for each beaten | body-size rug: reach −1 against larger creatures |
| 9 | topple the shelves, barrels or woodpile onto them | Force (object) | `harm_severity` → the object's rung; `targets` → its group | higher of the object's tier (Moderate) and each Guard | body rung S2 to each, at most 2 (T-06-8 footprint) [revision: I-075]; `difficult_ground` there afterward | loud |
| 10 | hold the doorway (stair, bridge) so they come one at a time | Move | none | unopposed: Trivial | `flag.in_chokepoint`; they gain `flag.lined_up` if they queue | |
| 11 | slam and bar the door between us | Handle (bar it) or Force (hold it) | `reach_unit` → feature state | Trivial if no one contests; else the pusher's Might defense | `barrier` shut: `no_line`; breaking it is their Force against its tier | Handle needs a bar established |
| 12 | throw the lantern (oil flask) at it | Strike (thrown) | `harm_severity` → S1; `condition` → burning | Guard | S1 `harm.fire`, and one stack of `cond.burning`; the light source is gone (10) | improvised: hand rung |
| 13 | leap down on it from the gallery | Exert, then Strike | Exert: `stakes` → the drop | Exert: tier by height (10 ft Moderate); Strike: Guard | the Exert's success is the fact `plunging.<actor>`: an **Amplifying** lever on the Strike that follows this turn; I end engaged | failing the Exert: the fall's harm to me, and no Strike |
| 14 | slide under the ogre / vault the goblins | Move through | `dc` → opposed | higher of Might or Agility defense (unopposed at two size steps) | on the far side, no reaction provoked | R7 Ex.1 |
| 15 | use him as a shield against the archers | Grapple (holding `restrained`) | none: a listed use of a hold | — (1 action, no roll) | `flag.in_cover` vs ranged; their critical failure threatens him | 06.5.2 |
| 16 | blow out the lamps / douse the fire | Handle | `targets` → the light | Trivial, or Easy under threat | `scene.light` one step darker: `flag.obscured` per 06.3.7 | both sides affected |
| 17 | throw a net, bolas or weighted rope | Grapple at range (`entangling`) | `dc` unchanged; band → close | higher of Might or Agility defense | `cond.grabbed` (S1 at reach 1, S2 at 2+) by the net; no hold to maintain | break free against the net's tier (Moderate) |
| 18 | stampede the horses (loose the hounds, the hive) at them | Handle or Talk (animals) | `targets` → the animals; `reach_unit` → a created mob | the animals' Resolve defense or Easy tier | the animals become a **mob** acting on its own default list toward the nearest creatures away from the actor, for 2 rounds | the mob is no one's companion |
| 19 | drop the portcullis / release the counterweight | Handle | `reach_unit` → feature state | the mechanism's tier | `barrier` shut; one under it: Evade vs Hard or S3 and `restrained` | the portcullis's one anchor: it falls in its slot onto one, so T-06-8's massive drop never applies to it [revision: I-075] |
| 20 | fight on the ice, in the surf, on the roof ridge | Move (across a `difficult_ground` or `hazard` feature) [revision: I-031] | `action_cost` → +1 per Move | — | Moves cost +1; a critical failure on any physical beat there threatens `cost.footing` | applies to everyone on it |
| 21 | grab its leg (tail, wing) | Grapple | `targets` → a limb | higher of Might or Agility defense | the creature is `cond.slowed` (leg) or `cond.weakened` (arm) while held; no size snag | 06.5.2; WE-06-3 |
| 22 | climb onto its back | Grapple (mount clause) | `condition` → `flag.mounted` | higher of Might or Agility defense | `flag.mounted` on it at reach 2+ | 06.15.5 |
| 23 | trip it with my staff, a rope, a chain | Force | `condition` → prone | higher of Might or Agility defense | `cond.prone`; a rope held by two cancels one size step | |
| 24 | knock the weapon from its hand | Strike, called at the held object, or Grapple (snatch) [revision: I-031] | `condition` (the arm); `reach_unit` (the snatch) | Guard, or higher of Might or Agility defense | the weapon falls, or is in my hand | 06.5.4 |
| 25 | pin its cloak (sleeve) to the wall with a knife or arrow | Strike | `condition` → grabbed S1; `harm_severity` → none | Guard, with the *called* snag | `cond.grabbed` S1 (by the object) until it spends 1 action | needs a wall or post in its group |
| 26 | smash the bridge ropes / kick away the ladder | Force (object) | `reach_unit` → feature state | the object's tier (rope Moderate; ladder Easy) | the feature is gone: those on it fall (06.5.8); `no_line` for movement across | stakes rise if I am on it |
| 27 | shout to startle it, bang my shield, flash the mirror | Setup | `condition` → distracted | Wits defense | `cond.distracted` ENT | loud |
| 28 | taunt it into charging me (onto the trap, under the hoist) | Talk | `reach_unit` → the listener's next Move | Resolve defense | its next turn's first action is a Move toward me; +attention (06.9.3) | mindless: G4 |
| 29 | roll the cask (cart, boulder) down at them | Force (object), shape `pierce` | `harm_severity` → the object's rung; `targets` → `flag.lined_up` carriers | higher of the object's tier and each Guard | the object's harm to each in the line, nearest first, capped at the object's count (T-06-8 footprint: a cask 2, a boulder 4) [revision: I-075] | needs a slope established |
| 30 | pour the oil (marbles, caltrops) across the floor | Handle | `reach_unit` → feature state | Trivial unless contested | a `difficult_ground` feature; a creature Moving across it fast (2+ bands a turn) Evades vs Moderate or falls prone | lamp oil can then be lit (row 7) |
| 31 | set the thatch (hay, dry reeds) alight | Handle | `reach_unit` → feature state | Easy with a flame in hand | a `hazard` (fire S2) and a `veil` (smoke) feature growing one group a round (10) | harms both sides; ticks nearby clocks listing loud or fire |
| 32 | hide under the wagon and stab at their legs | Sneak, then called Strike (the leg) | none beyond the two cards | notice; then Guard | `flag.hidden`, then the leg's result | two beats |
| 33 | parry with the chair, the lantern pole, a cloak round my arm | Evade as Defend (06.1.5) [revision: I-031] | none | — | the Defend snag; the object is then a body- or hand-rung improvised item | flavor costs nothing |
| 34 | throw my weapon | Strike (thrown) | — if `thrown`; else `harm_severity` → hand rung S1 and a Precision snag | Guard | the weapon's harm; it lies at the target's position | |
| 35 | dive behind the pillar as the breath comes | Evade, resisted (free) [revision: I-031] | — | the effect DC | `flag.in_cover` was needed *before*: now it is a Protective lever only if already held | 06.8.2 |
| 36 | wedge the door with my dagger / spike the wheel | Handle | `reach_unit` → feature state; `duration` | Easy | the `barrier` or mechanism holds against one Force attempt | the dagger stays there (`cost.gear` by choice) |
| 37 | hang by one hand from the gallery and kick | Force, with a snag fact | — | higher of Might or Agility defense | as Force; my `hanging` fact is a Precision snag | WE-12-2 |
| 38 | drag my fallen friend out of the fight | Move, carrying | `action_cost` → +1 per transition | Trivial unless opposed | both move; I provoke as usual | a companion can be commanded to do it |
| 39 | dig in behind my shield and wait them out | Evade as Full defense (06.1.5) [revision: I-031] | `action_cost` → 2 | — | the Defend snag and `flag.in_cover` vs ranged | 06.1.5 |
| 40 | fire ten arrows / swing as many times as I can | Strike, repeated | none: throttled by 06.1.6 | Guard | up to three Strikes at 0 / −2 / −4 | never a higher DC (WE-06-2) |

**T-06-9b Chase ground** `[D]` (`data/conflict.yaml#chase.ground_tables`; the engine draws one row a
round with `roll_table`, d6, no immediate repeat; a region's seed or a pre-made setting may replace these
with regional tables; the world seed keeps them, 12.16.17).

| d6 | Settlement | Wild (forest, hill, marsh) | Indoors or underground |
|---|---|---|---|
| 1 | an open street: Easy | open ground: Easy | a straight passage: Easy |
| 2 | a crowded lane: Moderate | thick brush: Moderate | a stair, up or down: Moderate |
| 3 | carts and stalls across the way: Moderate | a stream or ditch to cross: Moderate | a door to get through and shut: Moderate |
| 4 | a wall or fence to get over: Moderate | a steep bank: Moderate | a junction where the way must be chosen: Moderate (Wits or Intellect allowed) |
| 5 | rooftops or a canal to leap: Hard | a ravine, deadfall or bog: Hard | a gap, a pit, a collapsed stretch: Hard |
| 6 | a dead end: Hard, and only Exert, Sneak or Force may be used | broken ground in poor light: Hard | darkness without a light: Hard |

**T-06-13 The advisory matrix (the solo curve).** Simulated with T-06-12's lines: baseline martial PC,
no Focus. Each cell: advisory word, win% / Staggered%. Words: **trivial** win ≥ 99 and Staggered ≤ 3 ·
**easy** ≥ 95 and ≤ 15 · **fair** ≥ 80 and ≤ 50 · **hard** win ≥ 40 · **lethal** below. Chapter 09's
`threat_advisory` returns the word (06.10.6); a mixed group is read by its worst row, raised one word
for each further group of two or more foes.

*Foes two bands below the PC*

| PC | 1 foe | 2 | 3 | 4 | 6 | mob of 4 | mob of 6 | mob of 8 |
|---|---|---|---|---|---|---|---|---|
| P3 (T1) | trivial 100/0 | trivial 100/0 | trivial 100/0 | trivial 100/0 | trivial 100/0 | trivial 100/0 | trivial 100/0 | trivial 100/2 |
| P4 (T2) | trivial 100/0 | trivial 100/0 | trivial 100/0 | trivial 100/0 | easy 97/5 | trivial 100/0 | easy 99/4 | fair 97/17 |
| P5 (T3) | trivial 100/0 | trivial 100/0 | trivial 99/2 | easy 95/9 | hard 62/51 | easy 99/5 | fair 95/18 | fair 89/41 |

*Foes one band below*

| PC | 1 foe | 2 | 3 | 4 | 6 | mob of 4 | mob of 6 | mob of 8 |
|---|---|---|---|---|---|---|---|---|
| P2 (T1) | trivial 100/0 | trivial 100/0 | trivial 100/1 | easy 99/5 | fair 84/26 | trivial 100/2 | easy 99/8 | fair 97/28 |
| P3 (T2) | trivial 100/0 | trivial 100/0 | trivial 100/0 | easy 99/3 | hard 77/33 | trivial 100/2 | easy 95/15 | fair 83/43 |
| P4 (T3) | trivial 100/1 | fair 93/21 | hard 43/80 | lethal 6/97 | lethal 0/100 | hard 57/68 | lethal 20/94 | lethal 7/98 |
| P5 (T4) | trivial 100/0 | fair 89/30 | lethal 32/83 | lethal 4/97 | lethal 0/100 | hard 46/74 | lethal 17/94 | lethal 9/97 |

*Foes of the PC's band*

| PC | 1 foe | 2 | 3 | 4 | 6 | mob of 4 | mob of 6 | mob of 8 |
|---|---|---|---|---|---|---|---|---|
| P1 (T1) | trivial 100/0 | trivial 100/1 | easy 97/7 | fair 86/31 | hard 42/68 | easy 99/13 | fair 95/27 | hard 83/57 |
| P2 (T2) | trivial 100/0 | fair 90/22 | lethal 32/84 | lethal 3/98 | lethal 0/100 | hard 43/74 | lethal 8/98 | lethal 2/99 |
| P3 (T3) | trivial 100/3 | hard 73/48 | lethal 13/96 | lethal 1/100 | lethal 0/100 | lethal 24/89 | lethal 2/100 | lethal 1/100 |
| P4 (T4) | fair 87/45 | lethal 3/99 | lethal 0/100 | lethal 0/100 | lethal 0/100 | lethal 0/100 | lethal 0/100 | lethal 0/100 |
| P5 (T5) | hard 80/59 | lethal 3/99 | lethal 0/100 | lethal 0/100 | lethal 0/100 | lethal 0/100 | lethal 0/100 | lethal 0/100 |

*Foes one band above*

| PC | 1 foe | 2 | 3 or more, or any mob |
|---|---|---|---|
| P1 (T2) | easy 99/9 | hard 49/69 | lethal |
| P2 (T3) | hard 45/86 | lethal 0/100 | lethal |
| P3 (T4) | hard 62/72 | lethal 0/100 | lethal |
| P4 (T5) | lethal 4/100 | lethal | lethal |

*Foes two bands above:* lethal in every cell (best case P1 against one T3: 8 / 99).

What the matrix says in words: **(1)** count matters more than band: a second foe of the PC's own
band is roughly as dangerous as one foe a band higher, and a third is lethal from P2 up. **(2)** A mob
is worth between one and two of its members as individuals, which is the tool for fielding crowds.
**(3)** The curve steepens at the top: from T4, armor and Vitality outgrow a lone character's
unassisted output, so champions' and legends' fights are won with Focus, preparation, ground and
allies (the Focus column of 06.10.6, and T-06-14's tactics rows).

**T-06-14 Kit and tactics on the same fights** (win% / Staggered%; baseline martial PC, no Focus).

| Fight | Three Strikes | Two Strikes + Defend | Shield, two Strikes + Defend | Heavy weapon + Defend | Reckless first Strike | Called shots at gaps | No armor | No Fend |
|---|---|---|---|---|---|---|---|---|
| P1 vs T2 | 98.7 / 9 | 97.0 / 14 | 98.2 / 11 | 90.9 / 25 | 93.6 / 24 | — | 94.7 / 26 | 97.5 / 13 |
| P2 vs T3 | 44.5 / 86 | 33.3 / 90 | 45.0 / 85 | 39.6 / 87 | **57.1** / 80 | — | 32.0 / 94 | 33.7 / 92 |
| P3 vs T3 | 99.7 / 3 | 99.4 / 5 | 99.7 / 3 | 98.8 / 6 | 99.6 / 4 | — | 98.0 / 17 | 99.5 / 4 |
| P3 vs T4 | 62.3 / 72 | 50.4 / 80 | 60.6 / 72 | 55.1 / 75 | **73.7** / 63 | **73.1** / 58 | 39.2 / 91 | 45.6 / 85 |
| P4 vs T4 | 87.3 / 45 | 78.9 / 55 | 85.6 / 46 | 81.0 / 50 | **93.8** / 30 | **92.5** / 31 | 71.6 / 72 | 78.5 / 60 |
| P4 vs T5 | 3.7 / 100 | 2.0 / 100 | 3.9 / 100 | 5.9 / 99 | 16.6 / 98 | 14.1 / 98 | 2.1 / 100 | 1.5 / 100 |

Readings: against one strong foe, **offense is the better defense** (Defend in a duel loses a few
points; the reckless trade and the called shot each gain ten against armored foes); armor is worth
2–23 points and Fend 0–17 [verification: V2a-010], more the harder the foe hits; a heavy weapon is close to even with a
one-handed one unaided, and pulls ahead with Focus (P2 vs T3: 78% against 72%) and against armor.
None of these is dominant in every row, which is the test of 06.1's economy [R3 §06.6: "does the
restriction create a decision?"].

---

## Worked examples

**Wren** (00's sheet): Might +1, Agility +3, Endurance +1, Wits +2, Intellect 0, Presence 0, Resolve −1;
competence `deed` +1, `deed.wilds.tracking` +2, `deed.martial.archery` +2; Vitality 13 (12 + Endurance +1, 02.7.1) [revision: I-042], Focus 4, fate
1; no armor; spear (one-handed, `reach`, `finesse`; S2 pierce), shortbow (S2 pierce). Power band P1.
Her Guard with the spear: 10 + 3 + 1 (floor; she has no polearm competence) = **14**.
**Brack**, her mastiff *(illustrative; ch.16 owns companions)*: bite +4 (Might +2, competence +2), S2;
Grapple +4; Guard 13; Might defense 14; Vitality 8. Die results are shown as d20 = n; every roll is the
engine's.

### WE-06-1 Sedge Mill: a whole fight

*Situation.* Dusk. Three river-reavers are robbing the miller of Sedge Ford. Established at the scene's
opening, each written on mention: `feat.grain_hoist` (`loose_object`, rung **heavy**: three full sacks
on a chain over the foot of the loft stair, its rope tied off at the stair's top post); `feat.loft_stair`
(`height` 10 ft and `chokepoint`); `feat.millstones` (`cover`); `feat.flour_bin` (`loose_object`, hand:
an open bin at the stair's foot); `feat.race_door` (`chokepoint`; beyond it a plank over the millrace).
Opposition *(reference lines, T-06-12; ch.09 owns)*:
- **Corvin Rusk**, their leader, T2: sword +5, S2; Guard 15; Might and Agility defenses 15; Resolve
  defense 12; Vitality 12; tempo DC 11; one reaction (Opportunity Strike); nerve `steady`.
- **Odo** and **Pell**, cutthroats, T1: club or knife +2, S2; Guard 12; other defenses 12; Vitality 5;
  tempo DC 10; no reactions. Two creatures are not a mob (06.10.2: three or more).
Their objective: `rob`. `lethal_context` is not recorded: no frame in this fight may be lethal (INV-6).
Advisory (T-06-13, P1 against one foe a band up plus two of her band): **hard**; the player was told.

**Start (PR-06-1).** Pell is watching the yard door: `band.close` to Wren, alertness `alert`. Rusk and
Odo are at the strongbox by the millstones, group `stones`: `band.near`. Nobody is unaware: no
surprise. Morale clock `clk.morale.reavers` "The reavers' nerve": tug, sensed, **6** (steady), 0 filled.
Tempo: d20 = 13, +2 Wits, +1 floor = **16**: above every tempo DC (11, 10, 10), so each round runs
Wren, Rusk, then the cutthroats, nearer first.

> The door bangs back on its strap. Rusk looks up from the miller's strongbox across the room, Odo
> beside him; the third man, Pell, is a few strides off with a knife already out. Flour hangs in the
> lantern light. The loft stair is on your left, three fat sacks swaying on the hoist above its foot.

**Round 1, Wren (3 actions).**
1. **Command** (1): "Brack, on him!" Brack hears (he is at her heel). The commanded beat is a Move to
   Pell: unopposed, no roll. `set_position`: Brack–Pell `band.engaged`; Brack leaves her group.
2. **Strike** Pell with the spear (1). In reach: Pell is `close`, the spear has `reach`. Agility +3
   (`finesse`), competence +1 (floor), first attack: **+4** against Guard 12: needs 8 (65%). Safe;
   Standard. d20 = 15 → 19, margin +7: **success**. Harm: base S2, reach 2 → S2 → 3; Pell's reduction
   0. Pell 5 → **2**: `bloodied` (shown). Morale source "an individual first bloodied": +1 → **1/6**,
   stage *stirring*, omen: "one of them glances back at the door".
3. **Command** (1): "Hold him!" Brack's own first attack this turn: Grapple +4 against Pell's higher of
   Might or Agility defense, 12: needs 8. d20 = 11 → 15: **success**, reach 2: `cond.grabbed` **S2**
   on Pell, source Brack. Visible: named.

> Your spear takes Pell high in the arm and Brack hits him a heartbeat later, jaws shut on his forearm;
> he is held, bleeding and shouting. By the stones Odo glances at the door behind you.

**Round 1, the reavers (PR-06-6; `beh.default_melee`).**
- *Rusk.* Rows 1–4 false. Row 5: not engaged with his target. Target (06.9.3): no objective target;
  nobody engaged with him; the one who harmed him most: nobody; nearest: Wren at `near`, Brack at `near`
  (06.3.4: the farther of their two bands to the PC, never nearer than near) → the PC before a
  companion → **Wren**. Action 1: Move near → close. Action 2: Move close → engaged. The second Move
  comes from `band.close` to engaged with a `reach` wielder: it provokes (06.6.2 d). Wren is asked;
  the player says yes. Opportunity Strike: +4 against Guard 15, needs 11 (50%); no repetition snag (a
  reaction). d20 = 14 → 18: **success**: 3 harm, Rusk 12 → **9**. Her reaction is spent. The Move
  completes: Rusk–Wren `band.engaged`; group `stair foot`.
- *Odo.* Target Wren (nearest). Move near → close; Move close → engaged. Her reaction is gone: nothing
  provoked. Odo–Wren engaged, group `stair foot`. He has no action left to Flank.
- *Pell.* Row 2: held → break free. Grapple +2 against Brack's Might defense 14: needs 12: d20 = 6,
  fails. Second action, second attack (−2): needs 14: d20 = 10, fails. Still held.

> Rusk comes at you; your point meets him as he closes and scores his ribs, and then he is inside it,
> at blade's reach. Odo is at your other shoulder. Both of them stand at the foot of the loft stair.

State: Wren 13/13, engaged with Rusk (9/12) and Odo (5/5); not flanked (no Flank action yet). Brack
8/8 holding Pell (2/5).

**Round 2, Wren.** The player: "Flour in Rusk's face, then I back up the stair."
1. **Setup** (1), T-06-9 row 1: the flour bin is established at the stair's foot. Condition knob →
   `cond.blinded`. Agility +3, floor +1: +4 against Rusk's Guard 15: needs 11 (50%). It hinders a
   creature: it is this turn's first attack. Control check (06.7.4): Rusk's counter is 0 → full
   duration. d20 = 12 → 16: **success**. `cond.blinded` on Rusk until the end of his next turn
   (counter → 1). Visible: named.
2. **Withdraw** (1): engaged → close from Rusk and from Odo (one group). No Opportunity Strike.
3. **Move** (1) onto `feat.loft_stair`: unopposed. `flag.elevated` (a height, with a named stair, so
   reaching her costs no extra action) and `flag.in_chokepoint` (two abreast at most; she cannot be
   flanked there). Her bands: Rusk close, Odo close.

> A double handful of flour bursts in Rusk's face and he reels back, pawing at his eyes: blinded. You
> give ground up the stair, spear levelled. You are above them now, holding the stair; both are a lunge
> below.

**Round 2, the reavers.**
- *Rusk* (blinded). Row 5: Move close → engaged up the stair. It provokes her `reach` (her reaction
  refreshed at her turn's start): Strike +4; engine-cited levers: `cond.blinded` on the target
  (Precision) and `flag.elevated` (Precision): +4, the cap; total **+8** against his Guard 15 − 2
  (blinded, status) = 13: needs 5 (80%). d20 = 9 → 17: **success**, 3 harm: Rusk 9 → **6**, `bloodied`.
  Morale +1 → **2/6**, *stirring*: "their shouting has gone quiet". Rusk's second action: Strike Wren:
  +5 − 4 (blinded: status on sight-reliant checks) = +1, with the *from below* snag (−2): −1 against
  Guard 14: needs 15. d20 = 12: **miss**. His turn ends, and `cond.blinded` with it (ENT).
- *Odo.* Move close → engaged (the stair's capacity is two). Strike: +2, *from below* −2: +0 against
  14: needs 14. d20 = 16: **hit**. S2, 3 harm, no armor: Wren 13 → **10**.
- *Pell.* Break free: d20 = 7 and 9: both fail.

**Round 3, Wren.** The player: "The hoist rope is right here at the post. I cut it and drop the sacks
on them." 06.5.10: the intended change is harm to creatures through an object → **Strike** with two
knobs: `targets` (the rope; the fall is a `burst` on the group under it) and `harm_severity` (rung
*heavy* → **S3**, `harm.physical.crush`). IN PLACE: Rusk and Odo are both recorded in group `stair
foot`: true for both. Wren stands on the stair above the group: not selected (the OFFER lists the two
names and no ally). DC: the higher of the rope (taut, a blade in reach: Moderate, 15, stored on
`feat.grain_hoist`) and each Guard: 15 for Rusk (15), 15 for Odo (12). Agility +3, floor +1: +4; no
lever applies to a rope. Needs 11 (50%). Safe: failure is a rope half cut.

> `[OFFER] Cut the hoist rope: the sacks fall on Rusk and Odo — Strike (06.5.10; T-06-9 row 5)`
> `Roll: Agility +3 · competence +1 = +4 · Against: 15 (the rope, Moderate) · Need 11+ · 50%`
> `Stakes: Safe · Reach: Standard — each one under it takes Heavy crushing harm (5)`
> `Costs: 1 action · loud`

d20 = 13 → 17: **success** against both. Rusk: 5 harm, 6 → **1**. Odo: 5 harm, 5 → **0**: defeated
(`on_defeat`, frame id recorded; chapter 07 decides his state). The hoist is now a fact: fallen, and
the stair's foot is `difficult_ground`. Loud (a method consequence): no clock listens here.
Morale: a member defeated +1 → 3/6; the side's strength is Rusk 1 + Pell 2 = 3 of 22: at or below
half, +2 → 5/6; at or below a quarter, +2 → **complete**. The reavers **break** (06.11.5): each gains
`cond.broken`.
2. **Command** (1): "Brack, hold." A standing order (*hold him*): the hound keeps his grip with no
   further command.
3. **Talk** (1): "Throw it down, Rusk!" A demand for surrender: Presence 0, floor +1, and the engine
   cites `cond.broken` (Precision): +3 against his Resolve defense 12: needs 9 (60%). d20 = 5: **failure**
   (margin −4, no near miss). Safe: no cost. He will not yield while he can run.

**Round 3, the reavers.** *Rusk*, broken, not cornered, not held, as fast as she is: **flees**
(06.11.5). He is engaged with her: Withdraw (engaged → close), then Move close → near toward
`feat.race_door`. He ends the round across the room. *Pell*: broken, held, a thinking creature:
**yields**.

> The rope parts with a bang. Three sacks come down on the stair's foot in a roar of chaff: Odo goes
> under them and does not get up, and Rusk is flung against the post, grey-faced, one arm hanging. The
> one in Brack's jaws has stopped fighting; he is holding his free hand up, empty. "Throw it down,
> Rusk!" Rusk looks at the sacks, at the dog, at you, and runs for the race door. He is across the room
> and going.

**The chase (06.12.6).** The player: "After him." Wren is engaged with no one; the quarry flees.
Clocks: `clk.quarry_away` "Rusk gets clear" (danger, 6, 0) races `clk.run_down` "Running him down"
(progress, 8; he is at `near`: starts **1**). Ordinary turns stop; each chase round is one beat a side.
Brack stays on Pell (his order).

| Chase round | Ground drawn (`tbl.chase_ground`) | Wren's beat | Result | Rusk (fortune check, +5) | Clocks |
|---|---|---|---|---|---|
| 1 | established on his route: `feat.race_door`, the wet plank over the millrace, **Moderate** (06.12.3: a recorded feature in the way is the round's ground) | Exert (balance): Agility +3, floor +1 = +4; needs 11 | d20 = 16 → 20: success, 2 ticks | needs 10: d20 = 7: fails | run down **3/8** · away 0/6 |
| 2 | drawn, wild 1: open ground, the bank, **Easy** | Move (run; Exert may not repeat): +4; needs 6 | d20 = 11 → 15: success, 2 | needs 5: d20 = 12: success, 2 | **5/8** · 2/6 |
| 3 | drawn, wild 3: a stream to cross, the ford, **Moderate** | Exert (leap the stones; allowed again): +4; needs 11 | d20 = 19 → 23: success (margin +8), 2 | needs 10: d20 = 15: success, 2 | **7/8** · 4/6 |
| 4 | drawn, wild 1: open ground, the hill path, **Easy** | Move: +4; needs 6 | d20 = 8 → 12: success, 2: **complete** | (the acting side's ticks land first: his roll is not made) | **8/8** · voided |

`clk.run_down` completes: Wren is at `band.engaged` with Rusk and he gains `flag.cornered`. He is
broken, cannot get away, and is a thinking creature: he **yields** (06.11.5).

> He makes the hill path with you four strides behind and then two, and there his legs go. He turns
> with his back against the bank, the sword already falling out of his hand. "Enough. Enough."

**End (PR-06-10).** `conflict_end`: no hostile participant is able and willing to act. Dispositions:
Odo `defeated` (frame f.r3.1), Pell `yielded`, Rusk `yielded` after a chase. Wren 10/13, Focus 4/4,
reaction and stances cleared; bands and links cleared. Evidence is chapter 03's to compute from the
frames (spear deeds against a band-2 foe, an athletics chase, a companion-grounded deed); what she now
does with two prisoners is chapter 03's `conduct.mercy` and chapter 15's talk. Next steps on the table (P16): the
miller, the strongbox, two men who know who sent them.

*What this example exercised:* tempo (one roll, three DCs); six band changes, a Withdraw, two flags
gained by a Move; an Opportunity Strike from `reach`; a condition from a Setup with the control
counter; two commands and a standing order; a commanded Grapple; the attention rule; an environment
anchor with two knobs; engine-cited levers at the cap; a morale clock from 0 to broken with its
omens; a refused surrender; a rout, a chase with the varied-approach rule, a cornering and a yield.

### WE-06-2 "I fire ten arrows." (boundary pair)

Wren, `band.near` from a T2 reaver (Guard 15), unengaged. **Inside:** the declaration is a repeated
Strike ×10. The throttle (06.1.6; 01.14.3): three actions, three shots. Archery: Agility +3,
competence +2 = +5. The DC is his Guard for every shot.

> `[OFFER] Three shots this turn (ten will not fit in six seconds): need 10 (55%), then 12 (45%), then 14 (35%) — at least one hit 84%. Each hit: Moderate harm (3).`
> `Or: Aim, then two shots at 10 and 10 (55%, 55% — at least one 80%, and a better chance of two). Or: two shots and a step back to the trees.`

**Outside:** next turn she is engaged with him. Each shot now carries the *crowded* snag: 12, 14, 16.
The alternative the OFFER names: Withdraw (1), then two shots at 10 and 12. **Non-example:** "one roll,
harder, for all ten" → never: the DC is how hard one shot is (01.14.3; the probe's own ruling was
sixteen times too harsh).

### WE-06-3 The ogre's leg (size; a tempting non-example)

An ogre *(reference: T3, large; Might defense 19, Agility defense 13)* has wound up its maul. The
player: "I grab its leg and heave it over." **GATE:** Grapple or Force, both basic. **Size (06.3.10):**
the ogre is one step larger. Toppling the whole creature is a Force at reach −1: Standard → Limited:
delivered reach 1 on a success is `cond.off_balance`, not prone. The DM says so before any roll and
names the alternatives the rules hold:
- *Seize the leg* (T-06-9 row 21): Grapple with `targets` → a limb: no size snag, against its higher
  defense, 19. Might +1, floor +1 = +2: needs 17 (20%). On a success the ogre is `cond.slowed` while
  she holds on.
- *Trip it with the spear shaft between its ankles as it steps* (row 23): Force, `condition` → prone;
  one size step: reach Limited → `cond.off_balance` only, unless a lever restores the rung. She cites
  the windup: "it is mid-swing, weight forward" (the recorded fact `windup.ogre.maul`): an Amplifying
  lever → Standard: prone on a success. Against 19, +2: needs 17. A prone ogre's windup is spoiled
  (06.9.5).
- *Climb onto its back* (row 22).
She takes the trip. d20 = 18 → 20: success: the ogre is `cond.prone` and the maul's windup is gone.
**Non-example:** "I'm strong and it's off-balance from swinging, so it just falls" → strength is the
modifier and the windup was one lever; nothing falls without the roll, and nothing more than the ladder
gives.

### WE-06-4 The chandelier, twice (which anchor?)

*(a) "I swing across on it."* The intended change is her own position: **Exert** (T-06-9 row 4),
knobs `dc` (re-derived tier: Hard, precedent r.0412) and `stakes` (the 12-ft drop: Risky). No one is
harmed whatever she rolls. *(b) "I cut its rope so it lands on the captain."* The intended change is
harm through an object: **Strike** (row 5), knobs `targets` and `harm_severity` (heavy: S3). One roll
against the higher of the rope's tier and his Guard; IN PLACE must be true. *(c) Boundary:* "I swing
across and kick him off the gallery as I land" is (a) then a Force, two beats, the second framed after
the first resolves (01.14.1), with `plunging` as its lever only if the swing succeeded.

### WE-06-5 A mob (numbers, carry-over, a shaped effect)

Six marsh goblins *(T1: +2, S2, Guard 12, Vitality 5 each)* as one mob: pool 30, `members_now` 6,
numbers step +2: its attacks deal **S4**. It is engaged with Wren (capacity four; two wait). Advisory
(P1, a mob of six of her band): fair, 95 / 27. On its turn it Strikes twice: +2 and +0 against Guard
14: d20 = 13 → hit: S4, 8 harm: Wren 13 → 5. Second: d20 = 9: miss.
Wren's turn. *Single-target:* spear, d20 = 17 → 21, success: 3 harm: pool 27 → `members_now`
= ceil(27 ÷ 5) = 6: nobody falls yet. Second Strike (−2): d20 = 16 → 18: success: pool 24 → 5 members
(one falls: morale +1; the step drops to +1: S3). *Shaped:* her third beat is a thrown flask of lamp oil with the lantern after it *(an 08 item:
thrown, shape `burst`, S1 `harm.fire`, one stack of burning)*: Agility +3, floor +1, third attack −4:
+0 against Guard 12: needs 12: d20 = 14: a hit. Against a mob the burst would have selected up to its
cap of six, limited to `members_now` 5: the harm applies **five times**: 5 → pool 19 → 4 members
(another falls: +1; strength 19 of 30, above half). Burning is applied to the mob as a whole
(the shape selected at least half its members). At the mob's turn end: 1 fire harm, pool 18.
*Boundary:* the same lantern at a single ogre is 1 harm and one stack of burning.

### WE-06-6 The unseen shot (which defense; whose evidence)

Night; a sentry *(T2, Guard 15, Wits defense 12)* on the toll bridge; alertness `unaware`. Earlier
beat: Wren Sneaks into the alders (Agility +3, floor +1 against notice 12): success at reach 3:
`flag.hidden`. Now: "I shoot him." The frame rolls against **Guard 15** (06.4.2). Modifier: +3, archery
+2, and one engine-cited Precision lever: he gains `cond.surprised` at `conflict_start`, which is cited
first; her `flag.hidden` is the same opening and is not cited again. +7: needs 8 (65%). He has no
reaction. Primary deed tag `deed.martial.archery.bow`; secondary `deed.guile.ambush.sniping`, grounded
by position (03.1.7). d20 = 6 → 13: a miss; the arrow clatters; `flag.hidden` is lost (her beat was
visible), and he acts last in round 1 with one action. *Boundary:* with `ab.throat_of_night` the roll
would be against his **Wits** defense and ambush-primary, by the ability's own text.

### WE-06-7 Control diminishes

Round 2: flour blinds the reeve (counter 0 → full: until the end of his next turn; counter 1). Round
3: he is free of control conditions all round: counter 1 → 0 at the round's end. Round 4: a second
handful: full duration again. *Boundary:* had she thrown again in round 3 while the counter stood at 1,
the OFFER would have read "half duration, at least one turn"; a third control attempt in a row, with
the counter at 2, would be refused its condition ("he has the measure of it"), though a Strike riding
with it would still land.

### WE-06-8 The heavy blow

An ogre, engaged with Wren, spends its first action on a **Windup** (06.9.5): `windup.ogre.maul`
(S4). Its second action is an ordinary Strike. The narration shows the tell; her status line reads
"winding up: the maul". Her turn, with the blow due no earlier than its next: she may Withdraw and
Move (out of its reach of `close`: two actions, and it must close again); Defend (−2) and keep Fend
(−2 more); spoil it (WE-06-3's trip; a Strike that deals S3 or more in one hit; a blinding Setup); or
gamble on finishing it. *Arithmetic of standing still:* +7 against Guard 14 hits on 7 (70%; 50% with
Defend and Fend); S4 is 8 of her 13 Vitality; a critical success (total ≥ 24: d20 ≥ 17 without the
snags, 20%) is S5, 12: from full it leaves her 1, and from anything less it Staggers her, never worse from one blow. The player cannot say they were not told.

### WE-06-9 Wren runs (the chase as fleer, with a near miss)

Staggering odds: two T2 riders dismounting at a ford, Wren at 4 Vitality, `band.near`, not engaged.
"I run for the reed beds." Chapter 07's Retreat would price a certain escape; she prefers to try a
clean one. Clocks: `clk.escape` (6) 0; `clk.pursuit` (8) starts 1 (near). Round 1, ground: a steep
bank, Moderate. Exert (a climb by strength: Might +1, floor +1 = +2): needs 13. d20 = 14 → 16:
success: escape 2/6. Riders (remounted: pace higher → reach Great, 3 ticks): +5
against 15: d20 = 12: success: pursuit 4/8. Round 2, ground: thick reed, Moderate; Sneak (the reeds are
a `veil`; pursuit is at half, so 06.12.5's instant escape is not available, but an ordinary Sneak beat
is): Agility +3, floor +1 = +4 against the ground, 15: d20 = 9 → 13: **near miss**. Success at a cost:
2 ticks (escape 4/6) and `cost.time` S2: pursuit +1 → 5/8. Riders: d20 = 4: fail. Round 3, ground:
a stream, Moderate; Exert again (not consecutive with itself): d20 = 15 → 17: success: escape **6/6**.
She is at `band.distant`; the pursuit clock is voided at 5/8. *Had* the riders' round-2 roll succeeded
(8/8), she would have been caught at the reeds: engaged, `flag.cornered`, and chapter 07's Yield and
last-chance rules the only exits left.

---

## Edge cases & adaptation anchors

### Reaching for an anchor in a fight

When a declared action matches no rule, the DM does this, in this order (06.5.10; 01.5; INV-19):
1. `find_rulings` for the intent verb and tags: a precedent is reused unless a stated fact differs.
2. T-06-9: forty ready rulings.
3. The **intended change** picks the card: my position → Move or Exert; its position or footing →
   Force; a hold → Grapple; a lever or a short condition → Setup; harm → Strike; an object's state →
   Handle or Force; its will → Talk; not being hit → Defend or Evade.
4. Turn at most two knobs (T-00-20). A third needed change means the action is two beats.
5. Log the ruling with its signature.

**Anchor: yes rules of this chapter** (the anchor index compiles these; knobs with defaults → allowed
deltas):

| Rule | Intent verbs | Knobs |
|---|---|---|
| 06.1.5 Defend | guard, fight defensively, keep the shield up | `action_cost` 1 → 2 (Full defense); `targets` self → self and one engaged ally |
| 06.4.3 Strike (conflict) | hit, cut, shoot, throw at | `harm_severity`, `harm_tags`, `dc`, `targets`, `condition` (a call), `stakes`, `action_cost` (heavy only) |
| 06.4.10 Called shot | aim for the (part), go for the gap | `condition` (one listed call); a second snag for the head |
| 06.5.2 Grapple | grab, hold, pin, choke, climb onto | `condition`, `attribute`, `targets` (a limb), `dc`, `duration` |
| 06.5.3 Shove, trip, throw | push, trip, knock down, hurl | `condition`, `reach_unit` (into a feature), `targets` |
| 06.5.4 Disarm | knock away, snatch, wrench | by route (Grapple, called Strike) |
| 06.5.5 Feint, distract, blind | feint, distract, blind, bait | `condition`, `duration`, `dc`, `targets` |
| 06.5.6 Getting past | slip past, tumble through, break out | `dc` (opposed), `attribute` |
| 06.5.9 Aim | aim, steady | `duration`, `targets` |
| 06.5.10 Environment use | swing from, drop on, kick over, pull down | per T-06-9 |
| 06.6.6 Ready | wait for, cover, when X then Y | `duration` |
| 06.12.3 Flight beat | run, lose them, bar the way | `dc`, `reach_unit`, `time_cost`, `stakes` |
| 06.14.2 Command | order, send, have (an ally) do | `action_cost`, `targets` |

### Edge cases

- **Two beats in one sentence.** "I vault the table and stab him": a Move or Exert, then a Strike; two
  actions (01.2.2's conflict clause: a move ch.06 prices with its own roll stays its own beat; outside a conflict
  the walk or vault is the goal's method) [revision: R2-J; DL-01-37]; the second is framed after the first resolves (01.14.1). If the first fails the player may
  abandon the second at no cost.
- **A beat that would cost more actions than remain.** It is not begun: the DM says what fits ("a
  heavy swing needs two; you have one: Defend, step, or a one-handed blow with the haft, hand rung").
  Actions never carry over, and nothing is "half done" across turns except a clock.
- **An action longer than a turn** (a ritual, picking a lock, bandaging the fallen): a progress clock
  ticked once per turn by one action of the actor (01.14.6); `trait.action.concentrate` applies; harm
  forces the concentration check (01.17).
- **Attacking an object** (the lantern, the door, the bridge rope): a Force (to break it) or a Strike
  with `dc` → object tier; it is an attack-trait beat only if a creature is to be harmed by it.
- **Friendly fire.** A shaped effect lists allies in its OFFER (06.8.2); shooting into a melee
  threatens the ally only on a critical failure (06.4.7).
- **Harm reduced to zero.** The attack still hit: hooks fire and riders apply (06.4.6). A foe immune
  to the PC's attacks through reduction is a fact the OFFER reveals after the first such hit ("it
  lands and does nothing through the plate"), with what would work (a gap, a hammer, a heavier blow).
- **A flag and a condition both give a lever of the same kind.** Each is its own fact: both are cited,
  to the limit of two and the cap of ±4. A third is logged as not counted.
- **Both sides hidden, or fighting in the dark.** Everyone who relies on sight treats everyone beyond
  `band.engaged` as `flag.obscured`; an attacker with no light and no night-sight is `cond.blinded`
  for the attack. Sound still gives position: an Observe by hearing (one action) removes `flag.hidden`
  for that observer only.
- **Invisible or bodiless foes.** `flag.hidden` held by an effect, re-established at the start of each
  of the creature's turns unless a fact marks it (flour, rain, a thrown cloak: Setup). A bodiless
  creature's template says which verbs can touch it; a Grapple on a ghost is G4 with that redirect.
- **Flying foes.** `flag.aloft`: the redirects are a ranged attack, a height, a net (`entangling`), a
  Ready for the moment it stoops, or bringing it down (prone ends flight: a fall).
- **Underwater, on a rope, on horseback at a gallop.** Each is a feature fact (`difficult_ground`, a
  `hazard`) plus, where a license covers the skill, the license's fallback for those without it.
- **Three sides.** Each side has its own objective and morale clock; attention (06.9.3) treats every
  other side as enemies unless a recorded fact says two are allied. The PC may try to set them on each
  other with Talk (T-06-9 row 28). An independent side allied to the PC is resolved as a **held line**
  (16.7.12), not given turns [integration: IR ch.16 to 06 (d)].
- **A bystander in the way.** Not a participant: a feature of kind `cover` that can be harmed. A shaped
  effect's OFFER names them. Chapter 03 records what the PC chose.
- **The PC wants to be captured, or to lose convincingly.** Yield (free). To *feign* defeat is a
  Sneak or a Talk-deceive against the foe's Wits defense.
- **A duel.** `situation.conflict.duel`: two participants, an agreed end condition recorded as both
  sides' objective (first blood: the first `bloodied`; to yield; to the death, which needs chapter
  07's lethal warning on record). Tempo, actions and reactions as usual; interference by anyone else
  is a new `conflict_start`.
- **A fight the PC only watches** (two NPC groups). Not a conflict in this chapter's sense: chapter
  11's faction procedures or one fortune check per side decides it (01.6.7); if the PC then acts, a
  conflict starts with the positions the narration established.
- **A battle** (hundreds). Chapter 11 resolves the battle; the PC's part is played as a conflict
  against the mobs and leaders in reach, with the battle's tide as a clock whose ticks are the PC's
  objectives.
- **An adversary's power that this chapter does not describe.** It is data (09) built from effects;
  shaped powers and S4+ blows need a windup (06.9.5) whatever the template says.
- **A companion is the one in danger.** Commands to Withdraw or Defend cost the PC's action like any
  other; *stay back* is the standing order that keeps a weak companion out of reach without them.
- **Stunned, with the fight still on.** A stunned PC loses one turn: the player is told what happens,
  may Yield (free) and decides Fend-type questions only if the condition allows (it does not).
  Because control diminishes (06.7.4), the next such effect within the round lasts half, and a third
  fails.
- **The player asks "who can I reach?"** A G0 question answered from state: every participant, its
  band in words, its flags, its visible conditions; costs nothing.
- **Tempting non-example: "I attack and also defend and also keep an eye on the door."** Three things
  are three actions; a sentence is not a budget. The DM restates what three actions buy and asks which.
- **Tempting non-example: "My hireling handles the archers while I duel the captain."** A companion
  has no turn (06.14.1). A standing order (*harry that one*) keeps the hireling engaged with one archer
  and gives it an Opportunity Strike; anything more is a command each round.

---

## State touched

**Reads.** Attributes, competence, edge sources, licenses and grades (02, 04, 05, 08); Vitality, harm
state, reduction (07, 08); adversary stat blocks, sizes, nerve, behaviors, `defeat_disposition`,
`lethal_context`, tells (09, sealed); companion templates and loyalty (16); alertness (15); features,
light, hazards (10); abilities' effects and limits (05).

**Writes (this chapter owns).**
- **Relationship-state in conflict** (00.6.3): range bands, engagement links, groups, positional flags;
  via `set_position` only. Visibility: shown.
- **Conditions**: instances of every `cond.*` in `data/conditions.yaml`; via `apply_condition` /
  `remove_condition`. PC's: shown; others': shown if `visible`.
- **Conflict facts**: sides, objectives, the tempo order and the PC's tempo total, `defending.*`,
  `fend.*`, `aimed.*`, `charged.*`, `plunging.*`, `windup.*`, `tempo.seized`, `<weapon>.loaded`,
  `engaged.*`, `mob.*.member_out`, standing orders, the control counter per target, the attention score
  per adversary (background), features' states.
- **Clocks created** (00.8; templates in `data/conflict.yaml#clock_templates`): `clk.morale.<side>`
  (tug, sensed, 4/6/8); `clk.escape` (progress, public, 6) racing `clk.pursuit` (danger, public, 8);
  `clk.quarry_away` (danger, public, 6) racing `clk.run_down` (progress, public, 8).
- **Adversary Vitality** descriptors `bloodied` and `down` (shown; numbers background, 00.6.3).

**Tools used** (00.14.2): `frame_check`, `roll_check`, `read_result`, `apply_costs`, `set_position`,
`apply_condition` / `remove_condition`, `apply_harm`, `apply_effect`, `use_ability`, `update_quantity`
(ammunition), `set_fact`, `create_clock` / `tick_clock`, `roll_table` (`tbl.chase_ground`),
`mark_boundary` (`conflict_start`, `turn_start`, `turn_end`, `conflict_end`), `advance_time` (rounds),
`get_active_triggers`, `record_evidence`, `log_ruling` / `find_rulings`, `oracle`.

**Hooks fired by this chapter** (00.10.2): `on_check_against`, `on_attack_hit`, `on_attack_miss`,
`on_hit_taken`, `on_harm_dealt`, `on_harm_taken`, `on_vitality_threshold`, `on_defeat` (with the frame
id), `on_move`, `on_condition_applied`, `on_condition_removed`, `on_turn_start`, `on_turn_end`,
`on_clock_tick` / `on_clock_complete` (morale, chase). **Subscribed:** none of its own; the basic
reactions are core rules, not subscribers.

**Boundary handlers** (`data/boundaries.yaml owner-block 06`): the five 00 reserved, defined here —
`h.06.tempo_setup` (06.2.2), `h.06.turn_effects` (06.1.8), `h.06.ongoing_harm` (06.2.3),
`h.06.diminishing_window` (06.7.4), `h.06.clear_conflict_state` (06.13.4) — and two added:
`h.06.chase_round` (`round`, phase 5; 06.12.4) and `h.06.objective_check` (`round`, phase 9; 06.13.1).

**Effects added** (`data/effects.yaml owner-block 06`; DL-06-24): `eff.06.fewer_actions`, `eff.06.pace`,
`eff.06.grant_snag`, `eff.06.internal_harm`.

**Runtime capabilities assumed:** RC-RNG (every roll, the chase ground draw), RC-STORE (bands, links,
flags, counters with clamps), RC-EVAL (the pass, hooks, depth, stacking), RC-SCHED (turn and round
boundaries), RC-SEAL (adversary blocks; the narrator sees tells), RC-DATA (conditions, conflict
tables), RC-RETRIEVE (`situation.conflict.*` cards; active conditions and windups as triggers), RC-AUDIT
(claim class `position`), RC-LOG.

---

## Interface requests

**Requests addressed to this chapter, and how each was met.**

| From | Request | Where |
|---|---|---|
| 01 | `cond.grabbed` severity variable (S1/S2) | T-06-10; `conditions.yaml` |
| 01 | define the reserved conditions the cost menu and cards use | 06.7; `conditions.yaml` (all 23 reserved ids) |
| 01 | adopt or tune the repetition shape 0 / −2 / −4, window = the turn | 06.1.6: adopted unchanged (DL-06-03) |
| 01 | define each creature's "Guard" | 06.4.1; T-06-5 for every other `against` |
| 01 | the in-conflict stakes clause | 06.4.3: Safe by default; Risky by the trade |
| 01 | Ready and reactions | 06.6.6 |
| 01 | the companion command action for Help | 06.14.2 |
| 03 | which defense a Strike on an unaware target rolls against | 06.4.2: Guard; weapon tag primary (DL-06-08) |
| 03 | keep `flag.hidden` and `flag.mounted` current | T-06-4 set/clear lists; 06.13.4 |
| 03 | `on_defeat` carries the defeating frame id | 06.13.3 |
| 03 | a mob is one entity | 06.10.2 |
| 04, 05 | a "bloodied" expression | 06.7.6 |
| 05 | `cond.exposed` gives attackers a Precision lever | T-06-10 |
| 05 | action cost per verb; reactions per round; is `eff.reaction_grant` allowed | T-06-1; 06.1.1; 06.1.2 (yes: stances, calling capabilities, Exception-form abilities; never above two) |
| 05 | engagement links and `flag.lined_up` | 06.3.5; T-06-4 |
| 05 | adopt the five spread tags and caps | T-06-15 (order and caps unchanged; `cone` added for adversaries and objects) |
| 05 | stances end at `conflict_end` | 06.7.5; 06.13.4 |
| 05 | the command action for summoned servants, raised dead, automatons | 06.14.1 |
| 05 | size steps | 06.3.10 |
| 12 | reload state as a fact | 06.4.9 |
| 12 | T-12-11's band and flag wording | adopted; three flags added with words (T-06-4): "half-seen", "holding the gap", "in the air above" |

**To 00 (proposed amendments; this chapter works within 00 as written).**
1. **`economy` may reduce actions.** `substrate.yaml` gives `economy` the parameter `reactions_delta`
   only. `cond.dazed`, `cond.stunned` and `cond.surprised` need to *remove* actions. Proposed:
   `economy` params `[reactions_delta, actions_delta]` with `actions_delta ≤ 0` always; INV-11 already
   forbids only additions. `eff.06.fewer_actions` is written on that reading.
2. **A snag grant.** `eff.grant_lever` creates lever facts; cover, Defend, Fend and prone-at-range need
   the mirror. `eff.06.grant_snag` uses operation `lever` with a `sign: snag` parameter. Proposed: note
   in 00.10.3 that `lever` covers both.
3. **Reserved ids added:** flags `flag.obscured`, `flag.in_chokepoint`, `flag.aloft`; conditions
   `cond.surprised`, `cond.silenced`, `cond.broken`, `cond.heartened`
   (`substrate.yaml#reserved_ids`); T-00-15 and T-12-11 gain the rows.
4. **T-00-9:** handlers `h.06.chase_round`, `h.06.objective_check`.
5. **Condition schema (00.9.1):** optional field `diminishing.group` (a shared counter across a named
   group), and `decay` with `per_round_free: -1` semantics (06.7.4). PR-00-5 step 2 then counts by
   group.
6. **Glossary additions:** Guard (already used by 00), tempo, tempo DC, engagement link, group,
   feature, weight (of a weapon), mastery rung, harm mode, shape (of an effect), mob, swarm, nerve,
   morale clock, break, windup, heavy blow, attention, Defend, Fend, Withdraw, Flank, Aim, Command,
   standing order, chase round, ground, objective, pace, size step, called shot.
7. **00.3.7's coherence paragraph** was computed with one attack a round each; with this chapter's
   economy the same pairings read: P1 against one T2, 98.7% (was "even but favorable"); against one
   T3, 8% (was "a mismatch": unchanged in kind). The band words in `scales.yaml#bands.advisory_by_difference`
   should give way to T-06-13's matrix, which counts foes.

**To 01.** The Strike card's `against` "(06; default Agility defense)" resolves to Guard (06.4.1). The
engine snags of this chapter (Defend, Fend, called, nonlethal) join repetition snags under 00.3.9 (g):
outside the two-cited count, inside ±4. `cost.footing` S1's "lose one favorable flag" and S3's
`flag.cornered` are consistent with T-06-4.

**To 02.** Starting kits should give a martial origin light armor and a one-handed weapon or bow; this
chapter's P1 line assumes Vitality 12 and reduction 1. If Vitality does not grow with tier, the
top-band rows fall (simulation F: P4 against one T4 from 87% to 68%; P5 against one T5 from 80% to
57%): this chapter recommends **+2 maximum Vitality per power band above 1** (12 → 20 at P5, inside
the cap of 24), from 02/04/07 as they see fit.

**To 03.** Evidence grounding kinds this chapter supplies as state: `position` (`flag.hidden`,
`unaware(x, y)`), `mount` (`flag.mounted`), `companion` (a commanded beat's actor), `setup_beat`
(the lever fact's id). A mob's defeat is one event at the mob's band. Morale breaks produce `drive_off`
and `yielded` manners on `on_defeat` (06.11.5).

**To 05.** (a) Map `eff.05.spell_delivery` forms to shapes: `line` → `pierce`, `burst` → `burst`,
`cone` → `cone` (the sixth shape here; cap 4), `chain` → `chain`, `zone` → `linger`. (b) One zero-cost
attack working per magic branch (Moderate harm, `band.near`, at will) so a Spent caster keeps a
baseline (06.10.6). **Met** by 05.7.11 (revision I-009); an aimed working is not a "shot", so 06.4.7's
crowded snag does not apply to it. (c) `ab.shield_block` and similar claim `slot.defense_reaction` at rank 10+ and so
replace Fend (06.6.4): their texts should say "in place of Fend". (d) `ab.finishing_stroke` and
`ab.throat_of_night` deal S5: as PC abilities they need no windup; if an **adversary** holds them
(09), 06.9.5 applies. (e) Mastery (06.4.5) reads the training license grade; riders that add "one rung
heavier" are effect steps and stack with it inside the ±2 cap. (f) `ab.long_guard` ("Strikes reach
band.close") is the `reach` property by stance; `ab.commanding_ground` ticks `clk.morale.<side>`.

**To 07.** (a) `apply_harm` takes `mode` (lethal | nonlethal) and applies 06.4.8's results at 0
Vitality; NPC depth decides dead or Dying. (b) Retreat's certain outcome and price, and when it is
"uncertain" and becomes 06.12's chase. (c) Whether a foe accepts the PC's Yield is 06.11.7's lookup;
everything after is 07's. (d) The lethal warning must be on record before an adversary's attack frame
may be lethal; a Windup (06.9.5) is a perceivable sign 07 may count as the warning for that blow.
(e) Reduction: this chapter assumes worn armor 1 / 2 / 3 and a total cap of 4; `eff.06.internal_harm`
(bleeding, choking) needs `no_reduction: true`. (f) What "two further hits while Staggered" really
does (the script's Dying proxy). (g) Falls: 10 ft S2, 20 ft S3, 40 ft S4, 80 ft S5 assumed (with 10).

**To 08.** Build weapons on T-06-6 (weight fixes severity, cost, hands, bands) and T-06-7 (at most two
properties each); shields give +1 edge to Guard and no reduction; armor reduces by 1 / 2 / 3 and
carries its costs in other pillars; thrown-oil and similar items carry a shape and a severity; quality
adds harm edge inside the +2 cap; `loading` weapons carry the `loaded` fact; ammunition is a quantity;
natural armor is marked `no_gaps` where a called shot cannot bypass it.

**To 09.** Per adversary: all seven defenses and Guard; `tempo` (DC); `size`; `reaction` and reaction
abilities; attacks with weight-equivalent severity and bands, and `windup: true` on S4+ or shaped ones
(06.9.5 enforces it regardless); `morale` (nerve: skittish | steady | resolute | fearless) and
`morale_break.then` (flee | yield | cower | frenzy | fighting_withdrawal); `role` (melee | ranged |
beast | mob) for default behaviors; `objective` defaults from `defeat_disposition`; `weak_spot`
facts; `swarm: true`; `members` for mobs; `pace`. **Two actions for every template** (06.1.2).
`threat_advisory` from T-06-13 (re-run `06-conflict-sim.py` with the final templates). Reference lines
T-06-12 are this chapter's recommendation inside 00.3.7's envelope: note that T4 and T5 at the
envelope's middle are "lethal" in pairs to a PC of their own band.

**To 10.** Hazard entries as features (`feature_kind: hazard`) with severity and cadence;
`scene.light`; fall severities; tracking a fled quarry or fleeing PC after `band.distant`;
`tbl.chase_ground` may be replaced by regional tables (a region's seed, 12.16).

**To 12.** The enemy-turn step (12.2.9 item 1) is PR-06-6; the claim class `position` checks T-06-4's
words; the status line shows windups and the morale clock's existence; T-12-3's transitions are
06.2.1 and 06.13.1.

**To 13 (now the region's seed, 12.16; ch.13 is one optional pre-made seed).** Regional chase-ground
tables (the world seed uses the generic ones); feature-rich fight locations in the starting region (12.16.9);
nerve and objectives for the region's bestiary (09's build, 12.16.12). T-12-16 `ws.req.06_*` [revision: I-028].

**To 14.** Codex views: the turn summary (T-06-2); positions in words; conditions with remaining
durations; standing answers for reactions; the morale clock as "sensed"; chase clocks as public.

**To 15.** Alertness values consumed by 06.2.4; standing composed into Resolve defense for taunts,
demands and parley; prisoners.

**To 16.** Companion templates need: Guard, defenses, Vitality, attacks with weight, licenses,
`hears: voice | signs`, loyalty rules that can refuse a command, and which standing orders each kind
may take (a hound: all five; a hireling: all five; an automaton: per its maker's text).

---

## Open empirical questions

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-06-1 | Is three PC actions against two adversary actions the right asymmetry with the real bestiary? (Answered for bands 1–3 by ch.09: equal-band duels stay ≥ 99% on the final templates, T-09-3; bands 4–5 remain open) [integration: IR ch.09 to 06] | 3 / 2 (06.1.1) | **T-06-ECON**: re-run `06-conflict-sim.py` with ch.09's final templates; targets of 06.10.6 must hold at bands 1–3 within 10 points; if equal-band duels fall below 80% at P1–P3, lower template Vitality before touching the economy |
| OEQ-06-2 | Does 0 / −2 / −4 make "three Strikes" the only sensible turn in live play? | 01's shape | **T-06-VARIETY**: 30 logged PC turns per playtest session; share of turns that are three attack-trait beats; target ≤ 50%; if higher, try 0 / −4 / −4 (the simulation shows it costs about 5% of turn harm) |
| OEQ-06-3 | Do players and the DM keep bands and flags straight in text? | fixed words on every change (06.3.1) | **T-06-POS**: 5 fights of 4+ rounds; `position` claim mismatches per narration; target ≤ 1 per fight; and a player quiz after each fight ("who is engaged with you?") ≥ 90% correct |
| OEQ-06-4 | Is a deterministic morale clock too predictable, or usefully legible? | clock with listed sources (06.11) | **T-06-MORALE**: 10 group fights; share ended by a break (target 50–80%); share in which the player deliberately worked the clock (target ≥ 30%); a "felt arbitrary" rating ≤ 2 of 5 |
| OEQ-06-5 | Does the windup rule make solo adversaries too readable? | every S4+ or shaped blow announced (06.9.5) | **T-06-WINDUP**: 10 fights against T3+ solos; share of announced blows that still landed (target 30–60%); share of PC Staggers that followed an announced blow the player chose to stand under (any share is acceptable: it is the player's choice) |
| OEQ-06-6 | Do mobs feel like crowds or like one large monster? | pooled Vitality, numbers step (06.10) | **T-06-MOB**: 5 mob fights; narrated member-falls per round match `members_now` deltas (100% by claim check); a player rating of "felt like many" ≥ 4 of 5 |
| OEQ-06-7 | Are chase clocks of 6 and 8 right? | escape 6, pursuit 8 (06.12.2) | **T-06-CHASE**: 10 chases; escape rate 55–80% at band-equal pursuers; mean 3–5 chase rounds; the simulation's section I is the baseline (70%, 3.4) |
| OEQ-06-8 | Does the DM pick the right anchor for wild actions? | 06.5.10 decision 1 and T-06-9 | **T-06-ANCHOR**: 40 scripted creative declarations × 3 independent DM runs; target ≥ 85% agreement on the anchor verb and ≥ 80% on the knob set; disagreements become new T-06-9 rows |
| OEQ-06-9 | Is mastery keyed to the right thing? | training grade (06.4.5) | **T-06-MASTERY**: with 02's and 07's real Vitality and armor, the specialist-to-broad gap at P3–P4 should stay within 15 points of win rate; if larger, give broad callings the rung at tier 3 |
| OEQ-06-10 | Is control diminishing too protective of bosses? | shared counter, 1 → half, 2 → fails, −1 per free round | **T-06-CONTROL**: a control-focused PC build against T3–T4 solos over 10 fights; rounds in which the foe was controlled ÷ rounds fought; target 20–40% |
