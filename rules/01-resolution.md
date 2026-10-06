# 01 — Resolution

> This chapter governs what happens between "the player says what their character does" and "the
> world has changed and the narration says so". Every action in the game passes through one eleven-step
> pipeline — PARSE → GATE → NECESSITY → ANCHOR → FRAME → OFFER → ROLL → READ → DELIVER → CONSEQUENCE →
> RECORD — whose output is a typed **frame** (00.13) written before any prose. The pipeline is shaped by
> one observation that every research digest repeats: an AI DM is excellent at reading free intent into a
> closed vocabulary and poor at choosing numbers, resisting a persuasive player, imposing loss and keeping
> its rulings consistent. So the player may attempt anything (goal 1), and every step of turning that
> attempt into an outcome is either computed by the engine or reduced to a yes/no question, a pick from a
> short defined list, or a rung on a five-rung ladder with anchors (goal 2). Capability is settled before
> quality (Principle VII): the fifteen basic verbs are always legal, anything else cites a license by id,
> and an unlicensed attempt is redirected by lookup to what *is* possible — never refused into a wall and
> never narrated into existence. Difficulty belongs to the obstacle and is stored; creativity pays only
> through cited facts (levers); how bad failure can be (stakes) and how much success achieves (reach) are
> declared and shown to the player before the die is rolled; the degree is computed; costs come from a
> closed nine-entry menu at a severity read from a table; compound intents are delivered in graduated
> amounts the player ranks; unestablished world facts come from a d100 Oracle whose odds are committed
> first; and every improvised ruling becomes precedent. The chapter also owns the single luck currency,
> `fate`, and the anchor cards of the fifteen basic verbs, which are the spine of the game's
> reach-and-adapt substrate.

**Reading this chapter.** *Rules* (01.1–01.18) are self-contained cards: each restates the ids it uses
(SG-26). Rules containing a judgment use the 00.2.5 template in full. *Procedures* (PR-01-*) are the
step lists the DM and engine execute. *Tables* (T-01-*) are canonical in `data/resolution.yaml`,
`data/basic_verbs.yaml` (anchor fields) and the ch.01 block of `data/scales.yaml`. *Worked examples*
(WE-01-*) re-rule every example in R7 through the final rules with real numbers, and add boundary pairs
and tempting non-examples for every `[J]` rule. The continuous character is **Wren** from 00 (Might +1,
Agility +3, Endurance +1, Wits +2, Intellect 0, Presence 0, Resolve −1; competence `deed` +1 floor,
`deed.wilds.tracking` +2, `deed.martial.archery` +2; Vitality 13 (12 + Endurance +1) [verification: V1-001], Focus 4, fate 1; the fifteen basic
verbs and `lic.lang.common` native). Numbers owned by other chapters are marked *(illustrative; ch.NN
owns)*; every resolution number is exact. All odds in this chapter were computed by exhaustive d20 and
d100 enumeration (scratchpad `odds01.py`, `oracle01.py`, `fate01.py`; results in T-01-3, T-01-14).

---

## Design intent

**Goals served.** Goal 1 — the player feels free to try any creative idea: nothing is refused for being
unusual; every refusal is a lookup that names what is possible instead and how the capability could be
gained; asking "could I try X?" costs nothing, because the OFFER shows the odds, stakes and reach before
commitment; creative ideas earn a bounded, visible currency (levers) that a player can plan for; compound
plans are split and delivered in part rather than all-or-nothing. Goal 2 — the AI rules correctly: the
DM supplies ids, flags, enum values and rungs; the engine computes every number (INV-3); the dominant
AI failure — granting unearned success, roughly 120× more common than demanding a needless roll and
quadrupled by a plausible-sounding justification [R4 §3.3 W2; R: https://arxiv.org/abs/2607.02802] — is
met by tie-breaks that point toward the roll, toward less reach, toward the lower attribute and toward
"no license", and by the rule that player text is intent and method, never fact or outcome (SG-06).

**The seven separate questions.** The research found that systems which feel free *and* rule
consistently keep seven questions apart [R7 §0, §3.3 F1]: what do you want and what do you do (PARSE);
may you even try (GATE); does it need dice (NECESSITY); which existing rule is it most like (ANCHOR);
how hard, how dangerous, how much (FRAME: DC, stakes, reach, three separate dials); what happened
(ROLL, READ, DELIVER); what does it cost and what's next (CONSEQUENCE). Merging any two of them is how
weaker systems become either stingy or permissive. This chapter gives each its own step and its own
rule.

**What this chapter deliberately avoids.**
- **Graded description.** Prose quality earns nothing. Exalted stunt dice and Wushu detail-counting fail
  goal 2 (taste cannot be applied the same way twice) and reward verbosity over thought [R7 §2.20, §2.22].
  A creative idea pays only through a named, established fact (a lever), capped at two.
- **Situational DC changes.** The DC follows the obstacle and is stored; circumstance is a lever or snag
  on the acting side (00.3.8). A cool method never gets a lower DC; the same wall has the same DC next week.
- **Quantity as difficulty.** "I shoot it ten times" is throttled by the action economy and the
  repeated-attempt shape, never by raising the DC (the probe's DC-25 ruling was about nine times harsher
  than its fiction justified) [R7 §5 Ex.7; BRIEF A3].
- **Free numbers, free randomness, free consequences.** No DC, modifier, odds, tick count, harm amount or
  duration comes from the DM (INV-3); every die is the engine's (INV-4); every cost is a menu entry at a
  table-read severity, and the DM chooses only its fictional form.
- **Nested exceptions.** Every precedence question in this chapter is a flat first-match list (SG-10).
- **A second luck currency.** `fate` is the only one (00.17.1 Q9); Focus-for-effort belongs to ch.05.

**Principle map.** VII → 01.3 (GATE), 01.18 (verbs); P8 → 01.8–01.9; P17 → 01.10; P16 → 01.3.6,
01.11.4, 01.15.5; P3 → 01.5 (ANCHOR), 01.17 (traits), 01.18 (anchor cards); III → 01.5.4 (ruling
ledger, review flags); P9 → 01.14.3 (repetition throttled by the economy); P12 → 01.3.3 (literal
license reading); VI → every data entry `lifecycle: provisional`.

---

## Rules

### 01.1 The pipeline and its record

**01.1.1 One pipeline for every action.** `[D]` Every declaration by the player, and every attempt by a
non-player entity that the engine resolves with a d20, passes through the eleven steps below, in order,
producing one frame (00.13) per beat. No chapter may add a judgment step outside the pipeline
(00.13.1); a chapter's own rule plugs into the pipeline as an **anchor** (01.5), a **license** (01.3),
a **clock** (01.14.6), a **cost form** (01.13) or a **delivery table** (01.10).

| # | Step | Kind | Question it answers | Output (frame fields) |
|---|---|---|---|---|
| 1 | PARSE | `[J:enum]` | What is wanted, what is done, how many beats? | `beat.{intent, method, assertion, shape, parent_beat}` |
| 2 | GATE | `[J:enum]` + `[D]` | May this be attempted at all? | `gate.{class, verb, license, mode}` |
| 3 | NECESSITY | `[J:flag]` | Does it need a roll? | `necessity.{roll, reason}` |
| 4 | ANCHOR | `[J:enum]` + `[D]` | Which rule is it most like? | `anchor.{rule_id, deltas, precedent}` |
| 5 | FRAME | `[J:enum]` `[J:flag]` `[J:rung]` + `[D]` | How hard, how dangerous, how much? | attribute, deed_tag, traits, obstacle, levers, snags, stakes, reach, threatened cost, modifier, odds |
| 6 | OFFER | `[N]` + `[D]` | Does the player commit? | `offer.{shown_at, choice}` |
| 7 | ROLL | `[D]` | What did the die say? | `roll`, `degree`, `near_miss` |
| 8 | READ | `[D]` | How much was achieved, what is due? | `success_at_cost_taken`, `delivered.reach`, cost severities |
| 9 | DELIVER | `[D]` + `[J:enum]` | Which parts of a compound intent landed? | `delivered.{units, items}` |
| 10 | CONSEQUENCE | `[J:enum]` + `[D]` | Which cost form, which method consequences, what next? | `costs`, `method_consequences` |
| 11 | RECORD | `[D]` | Is everything in state before narration? | `state_writes`, `evidence`, `ruling` |

Steps 1–6 cost nothing and may be repeated freely: a player who changes method at OFFER re-enters at
PARSE with the new method. From ROLL on, the frame is immutable except for READ, DELIVER, CONSEQUENCE and
RECORD fields (00.13.2). Narration happens after RECORD and restates only what the store holds (INV-2).
[C:VII; C:P8; C:P17; R7 §4.0; R4 §7.1; R: https://arxiv.org/abs/2502.19519]

**01.1.2 The beat.** `[D]` A **beat** is one method, aimed at one target (an entity, an obstacle, or a
question), intending one change. A turn (06) may hold several beats; a declaration may hold several beats;
one beat is never split across two frames except by the partial-license split of 01.3.4. The beat's
`actor` is the entity whose method it is; the beat's `target` must be resolved to an id before GATE
(01.2.5).

**01.1.3 No roll without a committed frame.** `[D]` `roll_check(frame_id)` refuses unless the frame
passes every validation of 00.13.2 and of PR-01-2 step 12: gate class G1 or G2 (or an accepted G3
fallback) with the verb or license id present; every lever and snag citing an established fact that
existed before the declaration; stakes set; `lethal` legal; a threatened cost declared when stakes are
Risky or Dire; offer choice `commit` (or `auto` under 01.7.4). *Invariant INV-5* [SG-08].

**01.1.4 What the DM supplies to the pipeline.** `[D]` Ids, enum values, rungs, flags, the player's own
stated quantities, and short text (intent, method, reasons, fictional forms). Never a DC, modifier,
odds, harm amount, tick count, duration or price (INV-3; 00.14.3). Where this chapter says "the DM
picks", the pick is always from a closed list defined here or in data.

### 01.2 PARSE

**01.2.1 Intent, method, assertion.** `[J:enum]`

```
Trigger [T]:        the player (or the DM, for an NPC's attempt) declares an action
Loads in:           core
License check:      none (PARSE precedes GATE)
Decisions (J):      1. Split the declaration into three fields [J:enum over sentence parts]:
                       INTENT — what the player wants to be true afterward. True only when the words
                         state or clearly imply a change in the world. False for how it is done.
                       METHOD — what the character physically, verbally or magically does. True only
                         for observable acts. False for thoughts, feelings, reasons and results.
                       ASSERTION — anything stated as fact or outcome ("it's a cheap lock", "and he
                         falls", "since he's half asleep"). True for every clause that claims a fact,
                         a probability, or a result. Default for an ambiguous clause: ASSERTION.
                    2. If INTENT is unstated [J:flag] "Does exactly one intent follow from the method in
                       this scene?" True only when a single change is the obvious purpose. If true,
                       state it ("Taking that as: you want him to let you in"). If false, ask (01.2.4).
Computation [D]:    none
Stakes:             none (no roll)
State writes:       frame.beat.intent, .method, .assertion (assertion is context only: INV-9)
Narration may not imply: that an asserted fact or outcome is true
Worst case (J):     a result-clause read as method (e.g. "I kill it" treated as done). Bounded because
                    method never produces outcomes by itself — every outcome passes GATE→READ; the
                    assertion field is audited against state (class iv).
Examples:           inside: "I pick the lock with my knife" → method: pick with knife; intent: door
                    open. outside: "It's just a cheap lock" → assertion (creates nothing).
                    non-example: "I quickly hop the wall and succeed" — "and succeed" is an assertion;
                    the hop is the method; nothing about success is decided (CoC-Seduce "omission"
                    framing, 6.99% false-pass rate in the literature).
Anchor:             no
Basis:              [C:VII] [R4 SG-06; R4 §3.3 W2] [R7 §4.0 step 1] [R3 01.8] [R: https://thealexandrian.net/wordpress/37960/roleplaying-games/art-of-rulings-part-2-intention-and-method]
```

A player's *reason* why something should work ("the guard owes me", "fire beats ice") is an assertion
unless it names an established fact id; if it proposes a new fact, it is a World-Fact Oracle question
(01.15) that PARSE queues ahead of the beat (00.6.7, SG-06). A player's *internal monologue* ("I feel
the old anger rise") creates no beat.

**01.2.2 Splitting beats.** `[J:enum]` A declaration becomes one beat per distinct (method, target,
intended change). Test: *"If one part failed, could the other part still be attempted as described?"*
Yes → separate beats. No → one beat. Each beat is then classified by **shape**:

| Shape | True only when | False for | Resolved by |
|---|---|---|---|
| `single` | one method, one target, one change | — | the pipeline once |
| `sequential` | a later beat depends on an earlier beat's result ("throw sand, *then* slide under") | beats that merely happen in the same turn | 01.14.1 |
| `repeated` | the same method against the same kind of target, N times ("shoot it ten times", "stab again and again") | one sustained effort toward a single result (that is `extended`) | 01.14.3 |
| `bundled` | one act seeks several distinct pieces of information or several distinct results ("is it a demon, does it have a weakness, is it intelligent?"; "disarm him and knock him down") | several acts (split them instead) | 01.10 (DELIVER) |
| `conditional` | "if X, then Y", where X is a fact or an earlier result | a plain sequence | 01.14.4 |
| `extended` | the intent cannot honestly be achieved by one attempt in one time unit of the current mode (search a library, learn a tongue, dig a tunnel, calm a riot) | a hard single attempt (that is a high tier) | 01.14.6 (clock) |

Default when uncertain between `single` and `extended`: `single` if the result could plausibly be known
within the mode's time per beat (00.7.3), else `extended`. Default between `bundled` and several beats:
several beats (each with its own roll; this never grants more than the bundle would). *Worst case (J):* a
wrong shape changes how many rolls resolve the intent, not whether it is possible; the OFFER shows the
structure before any commitment (class ii). [R7 §4.0 step 1, §3.3 F7; R3 01.7; R4 §9 01 #7]

**01.2.3 At most three beats resolve per declaration.** `[D]` A declaration yielding more than three
beats resolves the first three in the player's order; the DM restates the rest as queued ("Then, if
that works: the seal") and confirms them at the next declaration. In conflict mode, ch.06's action
economy also limits beats per turn; a beat that would exceed the actions left is queued to the next
turn, never compressed. Reason: one declaration must not become many effects without a decision point
(WoW's global cooldown; Story-Engine's action-unit cap) [R3 01.7; R4 §9 01 #7].

**01.2.4 At most one clarifying question.** `[J:flag]` The DM asks one clarifying question only when
*"Would the answer change the gate class, the anchor, or the stakes?"* is true. Otherwise the DM states
the reading it is assuming, in one sentence, and continues; the player may correct it at OFFER at no
cost. Reason: models that assume silently "do not recover", while a stated assumption is correctable
[R: https://arxiv.org/abs/2505.06120; R7 §4.0 step 1]. *Worst case (J):* a wrong assumed reading reaches
OFFER, where the player sees it and can change it for free (class ii).

**01.2.5 The target is resolved before GATE.** `[J:enum]` + `[D]` A beat's target must be one id. If
the player's words plus relationship-state (06) leave exactly one legal candidate, it is that one; if
several, the stated default applies (in conflict: the nearest engaged foe; otherwise: the most recently
mentioned addressable element of the right kind); if none fits, ask (this counts as the one clarifying
question). A beat never resolves against an unresolved target, and self-harm is never narrated unless a
resolved result licenses it (a critical-failure cost). *Worst case (J):* the default picks the wrong one of
several candidates; the OFFER names the target before commitment, so the player corrects it at no cost
(class ii). [integration: 00.2.3 audit] [R3 01.9; R: ChatRPG v1 "self-inflicted trip" failure, R3 FP6]

**01.2.6 Neutral restatement.** `[D]` Before GATE the DM writes the beat as a neutral one-line
restatement ("Wren tries to open the guild lock with a knife tip") into `beat.method`. GATE, NECESSITY
and FRAME read the restatement, never the player's dramatic phrasing: framing measurably moves model
decisions [R1 01.B; R: https://arxiv.org/abs/2607.18566], and the neutral line is what the ruling ledger
stores.

### 01.3 GATE — may this be attempted at all?

**01.3.1 Gate classification.** `[J:enum]` + `[D]`

```
Trigger [T]:        a beat leaves PARSE with a resolved target
Loads in:           core
License check:      this rule IS the license check
Decisions (J):      1. Gate class [J:enum], first match wins (the test order is itself the tie-break):
                       G0 Question — true only when the player asks about the world or the character's
                          knowledge and describes no act (out-of-fiction questions included). False when
                          any observable act is described (then the act is gated and any embedded
                          unknown fact is queued to the Oracle).
                       G4 Impossible — true only when one of the four G4 tests (01.3.7) holds.
                       G1 Basic — true only when the method is within the `covers` list of one of the
                          fifteen verbs in data/basic_verbs.yaml AND not within that verb's `excludes`
                          AND the sensitive-upgrade test (01.3.3) is false. False for anything the
                          admission test fails ("could any able-bodied adult in the setting attempt
                          this with no training and a real chance?").
                       G2 Licensed — true only when the actor HOLDS a license (00.6.1 license state)
                          whose literal `scope`, at the held grade, covers this method on this target.
                          The DM must cite its id. A license not in the actor's state is not held.
                       G3 Unlicensed — everything else: beyond the basic verbs, not covered by any held
                          license, but possible for someone in the setting.
                       Default when uncertain between G1 and G3, or between G2 and G3: G3 (SG-05).
                    2. For G2 only, mode [J:enum]: normal (inside scope) | stretch | emulate (01.3.5).
                       Default: normal if the scope text covers it word for word; otherwise the license
                       must declare stretch/emulate and pass 01.3.5's tests; if neither passes → G3.
Computation [D]:    the engine validates that the cited verb or license id exists, is held (lifecycle
                    not retired, not expired, not forbidden by an active `restrict` effect) and belongs
                    to the actor. A cited license the actor lacks → refusal → G3.
Stakes:             none (GATE never rolls)
State writes:       frame.gate.{class, verb, license, mode}; on G3/G4 a ruling record (g3_redirect / g4)
Narration may not imply: that a G3 or G4 method was attempted, partly worked, or "almost" worked
Worst case (J):     a licensed attempt redirected as G3 — the redirect names the license id it checked,
                    so the player can point to the license (class iv); an unlicensed attempt framed as
                    G2 — the frame records the cited license id, which the claim-vs-state audit (ch.12)
                    checks against held licenses (class iv). A basic-verb over-reach (G1 claimed for a
                    licensed method) is caught by the verb's `excludes` list.
Examples:           inside G1: "I shove the cart into the doorway" (Force: shove).
                    outside G1: "I pick the lock" (Force excludes lockpicking → G2 if held, else G3).
                    inside G2: Wren (native Common) haggles in Common.
                    outside G2: haggling in Ogrish with no Ogrish license → G3; crude fallback: gesture.
                    non-example (persuasive but unlicensed): "I'm a hunter, so obviously I can read
                    these old elven runes — hunters see signs everywhere." The reason is an assertion;
                    reading an unknown script is excluded from Observe; no language license is held →
                    G3, however well argued (WE-01-16).
Anchor:             no
Basis:              [C:VII] [R7 §4.0 step 2, §4.4] [R4 SG-05, SG-07] [R1 01.B] [00.12.2–00.12.3]
```

**01.3.2 What counts as a license.** `[D]` A license is any held entry of the 00.12.1 schema: an
ability (`ab.*`), a spell, a calling capability, a training license (`lic.training.*`), a language
(`lic.lang.*` at a grade), an item property granting a license while equipped, a rank, a
condition-granted license, or a **fact license** (`kind: fact`) — an established narrative fact that
permits a method ("the smith gave you the forge key": `lic.fact.forge_key`). A fact license exists only
if it was written to state *before* the declaration (by narration under write-on-mention, by the Oracle,
or by a ruling); a player's claim that such a fact exists is an Oracle question, never a license (00.6.7,
INV-9). Rolls never create licenses (INV-7). An entity holds at most one instance of a license id
(INV-13).

**01.3.3 The literal-reading rule and the sensitive-upgrade test.** `[J:flag]` A license covers exactly
its `scope`, read literally at the held grade, and nothing more (INV-8). Before classifying a beat G1 or
G2, the DM asks: *"Would this beat give the actor more perception, memory, mobility, control, access,
awareness or freedom than an ordinary person has in this situation?"* These are the seven dimensions in
which generous narration produces impossible outcomes [R1 01.B; R1 #4; NCP-Bench auditor rule]. True
only when success would let the actor sense what cannot be sensed, know what was never learned, move
where bodies cannot, compel a mind or body, enter what is sealed, detect what magic hides, or escape
what physically binds — beyond what a basic verb's `covers` list states. If true, the beat is **not
G1**: it needs a license whose scope names that upgrade, else G3 or G4. False for ordinary uses of the
senses, memory and movement listed under Observe, Recall and Move. Uncertain → true. *Worst case (J):* an
ordinary act (listening at a door) sent to G3 — the redirect's fallback is the basic verb itself, so the
player loses one sentence (class ii).

**01.3.4 Splitting a beat that a license covers only partly.** `[D]` + `[J:enum]` When a held license's
scope covers part of a beat (the fire harm, but not the smoke; the lock, but not the ward on it), the
beat is split before framing:
1. The covered part is G2 under that license and is framed or applied exactly as its effects state.
2. Each uncovered part is re-gated alone: G1 if a basic verb covers it (its own frame, or a separate cost
   source inside the same frame), else G3 or G4.
3. If an uncovered part is G3/G4 and the intent cannot be reached without it, the whole intent is
   redirected (01.3.6); the covered part is still offered as what the license *does* allow ("your
   resistance will let you reach into the coals; it will not cool them").
4. Narration describes each part by its own gate: the license doing exactly its text, the basic-verb part
   succeeding or failing on its own roll, nothing more. "The flames part around you" from a harm
   reduction is an embellishment and is forbidden (INV-8; the probe's invented cold vulnerability).
Which parts exist is `[J:enum]` over the license's scope clauses (each clause is covered or not); default
for a clause that "sort of" applies: not covered. *Worst case (J):* a clause wrongly held covered grants one
beat's worth of the license's own literal effect — never more than the license can ever do (class i).
[R7 §4.0 step 2, §5 Ex.3, Ex.12; 00.12.2]

**01.3.5 Stretch, emulate and crude fallback.** `[J:flag]` + `[D]` These are the only three priced ways
past a license's literal scope. Each is looked up in the license entry (00.12.1), never invented, and
each is shown in the OFFER with its price.

| Mode | Who may use it | Legal only when (all true) | Price (from the entry; applied by the engine) |
|---|---|---|---|
| **stretch** | a holder of license L | (a) L's `stretch` is not null; (b) `[J:flag]` *"Does the new use perform the same operation that L's `principle` sentence names, only on a different target, scale or form?"* — true only when the principle's verb and its object category both still apply (a principle "push metal away from you" stretches to pushing a metal door; not to pulling, not to pushing wood); (c) the stretched use grants none of the seven sensitive upgrades (01.3.3) that L's scope does not already grant | DC + `stretch.dc_shift` (shown as its own line); Focus + `stretch.cost_add`; reach capped at `stretch.reach_cap` |
| **emulate** | a holder of a *domain* license D | (a) D's `emulate` is not null; (b) the technique is in `emulate.allowed_for`; (c) a fact records that the actor *witnessed* the technique (00.12.4); (d) the actor does not already hold it | DC + `emulate.dc_shift`; Focus × `emulate.cost_mult`; reach capped at `emulate.reach_cap`; on a critical failure `emulate.crit_fail` applies in place of the READ cost when it is worse; success ticks `emulate.learn_clock` by delivered reach and grants nothing else (INV-7) |
| **crude fallback** | anyone, on a G3 beat | the license that would cover the beat has `crude_fallback` not `none`, and the player accepts it at OFFER | a new frame on the fallback verb; DC = that verb's DC for this obstacle (01.6.4) + `dc_shift` (0, 5 or 10, shown as "improvised +N"); reach capped at `reach_cap`; the listed `consequence` (e.g. `trait.sense.loud`) becomes a method consequence |

Tie-break for stretch (b) and emulate (c): false (SG-05, "does this grant something? → no"). A license
entry missing one of these fields reads as `stretch: null`, `emulate: null`, `crude_fallback: none`, and
the gap is logged as a `rule_conflict` ruling for ch.05. When **no license entry in data** covers a G3
method at all, the redirect names the deed branch that would hold such a license (`deed.arcane`,
`deed.guile.thievery`…) and the generic acquisition types `mentor` and `recognition`, offers the nearest
basic verb, and logs a `rule_conflict` ruling so ch.05/13 can author the license. *Worst case (J):* a wrongly
allowed stretch gives one beat at a raised DC and capped reach — worse than a licensed use by
construction, and logged with the principle sentence it relied on (class i/iv). [R2 #4 (Mother of
Learning structured vs unstructured); R7 §4.4; R: https://www.d20srd.org/srd/skills/useMagicDevice.htm;
R7 §2.14 (Beginner's Luck); 00.12.4]

**01.3.6 The redirect: every refusal is a lookup that leaves a path.** `[D]` + `[N]` A G3 or G4 result is
spoken in this fixed four-part shape, fiction first, with the out-of-fiction line in the codex layer
(00.1.7):
1. **Acknowledge the intent** in the player's own terms ("You want the door open without waking the
   keep").
2. **Why, in one sentence of fiction**, naming what is missing: the license (G3: "the wards are guild-cut;
   nothing in your hands knows how to read them") or the fact (G4: "he has no sister, and he'd know it on
   sight") [integration: I-024]. The out-of-fiction line names the id checked (`lic.training.guile_thievery`; `npc.tam_harlan.siblings`).
3. **What is possible now**: the crude fallback if there is one (with its odds on request, through a free
   OFFER), else the nearest basic verb that serves the same intent, else the nearest achievable intent. At
   least one concrete option is always given (P16).
4. **How the capability could be gained** (G3 only): at least one `acquisition_path` of the license,
   stated as a fact of the world ("a locksmith or a thief could teach you"), plus the recognition path if
   the entry lists one.
A redirected or declined beat spends **no time, no action and no Focus** unless the player accepts an
alternative (00.12.3). The redirect is logged (`kind: g3_redirect` or `g4`). *Acceptance test*
(NCP-Bench's player-input rule): the response acknowledges the intent, offers concrete follow-through,
never substitutes a different action for the player, and never silently resets a state the player's
action implied [R1 01.B; R1 T-2]. Forbidden redirect forms: a bare "you can't"; "nothing happens" with no
option; an alternative the player did not ask for narrated as already taken. [C:VII; C:P16; R7 §2.4
(Dungeon World Ritual: "yes, if…"); R1 T-6]

**01.3.7 G4 — impossible.** `[J:flag]` ×4, first true wins.

```
Trigger [T]:        GATE tests G4 for a beat
Loads in:           core
License check:      —
Decisions (J):      1. CONTRADICTS A FACT [J:flag]: "Does success require an established fact to be
                       false?" True only when a fact id in state is contradicted (the guard has no
                       sister; the door is bricked) [integration: I-024]. Cite the fact id.
                    2. CONTRADICTS CANON [J:flag]: "Is this impossible for anyone in the setting, per
                       the region's canon_impossible list (the world seed's, 12.16.5, or a pre-made
                       setting's) or an established world law?" True only when the list
                       or a fact says so (no mortal flies unaided). Never true merely because it is unusual.
                    3. ZERO REACH [J:flag]: "Do two or more effect factors stand against this method
                       reaching this intent, with nothing offsetting them?" Factors (closed list):
                       POTENCY — the method cannot affect this kind of target (playing dead to hungry
                       wolves; words to a thing with no mind); QUALITY — the means is categorically
                       inadequate (a knife against a stone wall); SCALE — the target outsizes or
                       outnumbers the method by a whole category (one voice against a rioting square).
                       An offset is an established fact or license that cancels one factor (a crowd on
                       your side offsets scale). Exactly one uncancelled factor → not G4: reach is capped
                       at Limited instead (01.6.9).
                    4. FORBIDDEN BY CONDITION [D]: an active condition or `restrict` effect forbids the
                       verb, method, sense or license (00.9.3b). The engine answers from state.
                    Default when uncertain on 1–3: false — fall through to G1/G2/G3 and roll. This is
                    the one gate test whose tie-break favors the attempt: wrongly calling something
                    impossible builds the wall goal 1 forbids, while wrongly allowing an attempt still
                    has to beat an honest DC on the dice.
Computation [D]:    no roll; ruling logged (kind g4)
Stakes:             none
State writes:       ruling record; any Oracle answer that established the contradicting fact
Narration may not imply: that the attempt was made, partly worked, or could work with more effort
Worst case (J):     a possible attempt declared impossible — the redirect still offers the nearest
                    achievable intent and the ruling is reviewable (class iv); an impossible attempt
                    allowed — it is framed at its tier (usually Very hard or Legendary) and must beat
                    the dice (class i).
Examples:           inside: "I leap the 30-ft chasm" (canon: tier Beyond). outside: "I leap the 12-ft
                    gap from a running start" (Hard; roll).
                    inside: calm a river the Oracle said has no spirit (fact). outside: calm the river
                    spirit the Oracle said exists (Talk, G1; reach capped Limited by scale).
                    non-example: "Nobody could climb that sheer ice, so I anchor my rope-dart and haul
                    myself up" — not a G4 request; a new method (Exert with a tool lever).
Anchor:             no
Basis:              [C:VII] [R7 §3.3 F4, §4.0 step 2, §4.2] [R: https://bladesinthedark.com/effect]
```

**01.3.8 G0 — questions about the world.** `[D]` + `[J:flag]` A G0 beat is answered by the first match:
(1) from state, through the character's permitted slice (sealed content is never returned, INV-10);
(2) from the character's own established knowledge — free (00.12.6); (3) if the answer requires
*finding out* (looking, searching, recalling specialist lore, reading a person), it is not G0 but an
Observe or Recall beat (re-enter PARSE with that method); (4) if the fact is **unestablished** and **not
settled by canon or scene logic**, the World-Fact Oracle (01.15). An out-of-fiction question ("what are
my odds if I climb?", "how was that ruled?") is answered from the codex and a free OFFER and takes no
fictional time. The test between (2) and (3) is `[J:flag]` *"Would the character already know this
without doing anything?"* True only for common knowledge of the character's origin, culture or trade
(Recall's `covers`) and facts the character has learned. Uncertain → false (a Recall beat, which may
roll). *Worst case (J):* a free answer that should have needed a Recall roll — one item of common knowledge
(class i).

**01.3.9 "Yes, and" and default-deny work at different layers.** `[N]` The DM says yes to *premises and
approaches* — any method a basic verb or held license covers is attempted, however strange — and says no
only to *capabilities* the character does not hold, and then only through the 01.3.6 redirect ("yes,
but"). These are not competing instructions: an unlicensed capability is exactly the "breaks the rules"
case in which improv craft itself reserves a no, and "yes, but — here is what you can do" is Principle
VII's required redirect [R1 T-6; R1 M-10].

### 01.4 NECESSITY — does it need a roll?

**01.4.1 The roll test.** `[J:flag]` ×3

```
Trigger [T]:        a beat is gated G1 or G2 (or an accepted G3 fallback)
Loads in:           core
License check:      as gated
Decisions (J):      1. UNCERTAIN [J:flag]: "Given the established facts, could this method, done by
                       this actor now, realistically fail?" True unless the obstacle is Trivial:
                       anyone, in these conditions, succeeds every time (T-01-2 rung 0). The actor's
                       competence never makes an obstacle Trivial — that is what the modifier is for.
                    2. COSTLY [J:flag]: "Would failure cost something, change the situation, or use up
                       a chance that cannot be retaken freely?" True when any running clock listens to
                       this beat or to time, when an aware opponent or observer is present, when a
                       hazard is present, when failure would alert, break, spend, or close a door, or
                       when the intent is contested by anyone. False only when failure leaves the
                       situation exactly as it was and the attempt can be repeated at leisure.
                    3. RIDING [J:flag] (01.4.2): "Is this the same obstacle, same anchor and same
                       approach as a resolved beat whose ride is still active?"
                    ROLL = UNCERTAIN and COSTLY and not RIDING.
                    Tie-break for 1 and 2: TRUE (roll). Tie-break for 3: FALSE (roll).
Computation [D]:    necessity.{roll, reason}; reason ∈ uncertain_and_costly | riding | trivial |
                    good_idea | impossible | take_the_time | certain_with_cost
Stakes:             —
State writes:       frame.necessity
Narration may not imply: success that the pipeline did not produce
Worst case (J):     a needless roll (a false check — the rarer error, ~0.08% in the literature, and it
                    costs one die); a skipped roll that should have been made grants one beat's success
                    at Standard reach — bounded because the no-roll paths never grant Great reach, never
                    apply to Dire or lethal frames, never create licenses, and never unseal (class i).
Examples:           inside (roll): climbing a rough wall while a patrol clock runs (costly: time).
                    outside (no roll): climbing the same wall at noon with nobody about and nothing
                    pressing (take the time, 01.4.4).
                    inside (roll): recalling a rival house's crest under a herald's gaze (observer).
                    outside: recalling your own village's saint's day (free knowledge, 01.3.8).
                    non-example: "This is easy for someone like me, no need to roll" — an assertion;
                    ease is the tier's business, and competence enters as modifier only.
Anchor:             no
Basis:              [R4 SG-05, §9 01 #2; R: https://arxiv.org/abs/2607.02802] [R7 §4.0 step 3]
                    [R7 §2.19 Dogs in the Vineyard; §2.14 Burning Wheel] [R: https://theangrygm.com/adjudicate-actions-like-a-boss/]
```

The no-roll classes are closed: **trivial** (01.4.1 decision 1 false), **free activity** (00.12.6),
**riding** (01.4.2), **good idea** (01.4.3), **take the time** (01.4.4), **certain with cost** (01.4.5),
**question** (G0) and **impossible** (G4). Every other gated beat rolls.

**01.4.2 Let it ride.** `[J:flag]` + `[D]` One resolved beat settles one obstacle for one approach. The
engine stores a **ride** record `{actor, obstacle_id, anchor_id, method_class, degree, facts_at: [fact
ids], until}` at RECORD. A new beat against the same obstacle with the same anchor and approach does
**not** roll; the stored result stands — a success keeps covering the whole effort (one Sneak covers the
common room and the kitchen), a failure stays a failure. The ride ends, and a new roll becomes legal, when
the first of these holds (checked by the engine against state):
1. the **approach changes** — a different anchor, or a different attribute-bearing method on the same
   anchor (climb by strength → climb with a grapnel);
2. a **new fact** that is a lever for this beat (00.3.9) was established after the ride began;
3. the **circumstances change** — a fact the ride's frame cited is superseded, or the obstacle's stored DC,
   stakes source or threatened cost changes;
4. the ride's **interval passes** — for extended beats, the clock's tick interval (01.14.6); otherwise the
   end of the scene;
5. the player **pays the re-attempt cost**: one `cost.time` or `cost.exposure` (player's choice where both
   fit) at the frame's stakes severity (S1 when Safe), paid up front whatever the new roll shows.
"Is this the same obstacle and approach?" is `[J:flag]` — true only when the target id, anchor id and
method class all match; uncertain → true (the failure stands). *Worst case (J):* a legitimately new approach
treated as riding — the player names the difference at OFFER and the engine re-checks (class ii).
[R: https://thealexandrian.net/wordpress/38313/roleplaying-games/the-art-of-rulings-part-8-let-it-ride;
R7 §2.13 (Year Zero no-retry); C:P17]

**01.4.3 The Good Idea rule.** `[J:flag]` ×3

```
Trigger [T]:        a player claims (or the DM notices) that the method makes the roll unnecessary
Loads in:           core
License check:      as gated (G1/G2 only)
Decisions (J):      1. REMOVES THE SOURCE [J:flag]: "Does the method use one or more established facts
                       (cited by id) to remove the obstacle's source of uncertainty entirely, rather than
                       to make overcoming it easier?" True only when, after the cited facts, there is no
                       longer anything to overcome (waiting for the established patrol schedule's gap
                       removes being seen; a lantern at the right angle removes having to search a dark
                       floor). False when the facts only help (a tool, a distraction, a good angle — those
                       are levers).
                    2. UNOPPOSED [J:flag]: "Is no aware entity actively opposing this beat and no hazard
                       acting on it right now?" True only when state holds no aware opponent, observer
                       or active hazard for the target.
                    3. BOUNDED [D]: the beat's stakes would be Safe or Risky (not Dire), not lethal, and
                       success would not grant or stretch a license, unseal a sealed fact, generate
                       content (00.11), move standing, or tick a progress clock by more than 2.
                    Good Idea = all three true. Default for 1 and 2 when uncertain: FALSE (roll).
Computation [D]:    success at Standard reach, no roll, no cost; the beat consumes its normal time;
                    ruling logged (kind good_idea) with the cited fact ids.
Stakes:             none (no roll)
State writes:       frame.necessity {roll: false, reason: good_idea}; the success's writes; ruling
Narration may not imply: that a rolled-for result (Great reach, a critical) happened
Worst case (J):     one Safe-or-Risky beat succeeds at Standard reach without a roll it should have
                    had — bounded by decision 3 (class i), logged and reusable as precedent (class iv).
Examples:           inside: the patrol's round is established as "lantern passes every half hour";
                    Wren waits for it to pass and crosses the empty yard — no one watches (fact:
                    yard empty between rounds) → no roll.
                    outside: same yard, but a sentry on the wall is established (decision 2 false) →
                    Sneak roll; the patrol schedule becomes a Precision lever instead.
                    inside: the ledger's shelf mark was read on the clerk's index card (established);
                    Wren goes straight to shelf 14 → the find needs no search roll.
                    outside: "it's probably filed under the family name" — a guess, not a fact →
                    Observe roll (or an Oracle question about the filing system).
                    non-example (persuasive): "Guards never look up, everyone knows that, so I just
                    walk along the rafters" — a claimed generality is an assertion; if the player
                    wants it as a fact, it is an Oracle question about THESE guards; until answered,
                    Sneak rolls.
Anchor:             no
Basis:              [R7 §2.15 Torchbearer Good Idea, §4.0 step 3] [R4 SG-05, SG-06] [R: https://forum.rpg.net/threads/help-me-understand-torchbearer.708772/]
```

**01.4.4 Take the time.** `[D]` When a beat is UNCERTAIN but not COSTLY (no clock, observer, hazard or
contest), the character succeeds given time: success at Standard reach, no roll, and the beat consumes
**twice** the current mode's time per beat (site: 2 intervals; free: twice the activity's listed
duration; travel: 2 watches; downtime: twice the listed days; conflict: never applies, because a
conflict is always costly). Time passes through `advance_time`, so every boundary runs (INV-15) — which
is exactly how "taking the time" can become costly (an encounter check fires). An obstacle whose tier is
Very hard or Legendary cannot be taken with time: those rungs require a roll whenever attempted, because
"experts often fail" is not a function of patience. [R: 5e "take 20" and PF2e "take your time"
lineage via R7 §2.8; DL-01-09]

**01.4.5 Certain with cost.** `[D]` When the outcome is certain but a known, fixed cost attaches to the
method (reaching bare-handed into coals; swimming through water established as freezing; crossing a
hazard the character cannot avoid), there is no roll: the success applies and the cost applies as a
**method consequence** at the severity its source declares (a hazard's data severity; the fire's stated
harm). This is not a READ cost and cannot be reduced by success-at-cost choices; licenses that reduce the
harm apply literally (01.3.4). [R7 §5 Ex.12]

**01.4.6 Passive noticing.** `[D]` Looking around casually is a free activity (00.12.6); it succeeds
automatically against anything whose **concealment DC** is at or below the character's **notice**:
`notice = 10 + Wits + competence (on the deed tag of the Observe method that would find it) + edge +
status`, computed by the engine (the defense formula of 00.3.8 with Wits). Concealment DCs are stored
on the hidden thing: its tier (a trap's `detect.dc_tier`, a secret door's tier), or, when an entity hides
actively, that entity's Sneak total (rolled by the engine when it hid; stored). The engine compares at
`scene_start`, on entering a new place, and at each `interval` boundary in site mode while the character
is not `cond.distracted`; a pass unseals the thing into the narrator's slice (INV-10) and narration must
mention it that turn. No die is rolled, nothing is shown, and nothing is lost when it fails — an active
Observe beat is always still available. Symmetrically, an NPC's notice is the DC for the PC's Sneak
(00.3.8 opposed defense). [R5 RS-12; R: PF2e secret checks via R5 §1.3; 00.12.6]

**01.4.7 Secret frames.** `[J:flag]`

```
Trigger [T]:        an Observe, Recall, or Talk-to-read beat whose target's existence, truth or nature
                    is sealed or undetermined
Loads in:           investigation, social, exploration
License check:      as gated
Decisions (J):      1. [J:flag] "Would seeing the die, the DC or the odds tell the player something the
                       character could not know?" True only when the target is sealed (a hidden door, a
                       lie, a forged seal) or undetermined (whether anything is there at all). False for
                       a known obstacle (a visible lock, a wall, a known question with a known answer).
                       Uncertain → true.
Computation [D]:    frame.secret = true. If the target's existence is undetermined, the engine first
                    asks the Oracle SEALED (01.15.6). The OFFER shows method, attribute, modifier
                    breakdown, stakes, reach and threatened cost, but not the DC, the odds or the d20.
                    The engine rolls; READ and DELIVER run normally; the narrator receives only what
                    the character perceives. Fate cannot be spent on a secret frame (01.16.3). The whole
                    frame becomes `available` in the codex once its target unseals.
Stakes:             declared as usual (a secret frame still has a threatened cost if Risky or Dire)
State writes:       frame; sealed Oracle fact; any unsealed clue
Narration may not imply: whether a failure was "close"; whether anything was there to find
Worst case (J):     an unnecessary secret frame hides the odds of an ordinary check (the player can
                    still see modifier, stakes and cost; class ii); a needed one skipped leaks one
                    sealed existence-fact through the displayed DC (class iv — the leak is logged and
                    the fact's gate records it).
Examples:           inside: searching a study for a hidden compartment nobody has established → sealed
                    Oracle (Unlikely) then a secret Observe. outside: searching the same study for the
                    letter the steward said is in the desk (known to exist) → ordinary frame.
                    inside: reading whether the merchant is lying (truth sealed). outside: reading
                    whether the merchant is afraid, when he has been shaking all scene (established).
                    non-example: the player asks to see the DC "to decide whether to bother" on a
                    secret frame — the stakes and cost are the decision information; the DC stays
                    hidden, and asking costs nothing.
Anchor:             no
Basis:              [R5 RS-12 "name it"] [R4 §5.1–5.2 (sealed state)] [R1 G-24] [R: https://2e.aonprd.com/Rules.aspx?ID=2286]
```

### 01.5 ANCHOR — which rule is this most like?

**01.5.1 Choosing the anchor.** `[J:enum]` + `[D]`

```
Trigger [T]:        a beat will roll (NECESSITY roll = true) or needs a no-roll ruling
Loads in:           core
License check:      as gated
Decisions (J):      1. [D] `load_cards(anchors for the beat's verb, deed tags, situation)` returns at most
                       eight candidate anchors from data/anchors.yaml (00.15.3), always including the
                       gated basic verb's own card (01.18) or the license's own rule (G2).
                    2. [J:enum] pick one: the candidate whose intent verbs name what the beat tries to
                       change AND whose "Covers" includes the method. True only when both match. False
                       when only the surface matches (a shove and a grapple both touch the target: the
                       distinguishing test is "does the actor keep hold? → grapple; target moved away →
                       shove", 01.18). Default when two fit: the more specific one (a chapter sub-rule
                       over a verb card; a license's own rule over a verb card); when none fits: the
                       gated verb's own card with deltas.
Computation [D]:    frame.anchor.rule_id
State writes:       frame.anchor
Narration may not imply: rules the anchor does not contain
Worst case (J):     a near-but-wrong anchor: its degree table and knobs apply instead of the right one's;
                    bounded by the two-change limit and logged for precedent review (class iv).
Examples:           inside: "I tackle him off the wall" → the intent is to move him away and down, and
                    the actor does not keep hold → verb.force (topple), against his Might defense.
                    outside: "I tackle him and hold him down" → the actor keeps hold → verb.grapple.
                    non-example: choosing a lenient anchor because it has better odds ("call it a
                    Setup, not a Strike, so the ogre can't counter") — the anchor follows the intended
                    change, not the preferred numbers.
Anchor:             no
Basis:              [R7 §3.4, §4.0 step 4] [R: https://2e.aonprd.com/Rules.aspx?ID=2497 (most similar basic action)] [R4 SG-16]
```

**01.5.2 Precedent first.** `[D]` + `[J:flag]` Before any adapted ruling, Oracle call, Good Idea, G3 or
G4 decision, the DM calls `find_rulings(anchor_id, deltas, tags)` (INV-19). A precedent **matches** when
its signature (anchor + sorted deltas) is equal and its situation restates the same kind of case. If one
matches, the DM reuses its numbers (tier, stakes rung, reach rung, knob values) unless a stated fact
differs: `[J:flag]` *"Is there an established fact now that was absent (or present) in the precedent and
that changes the tier, stakes or reach?"* True only when that fact's id can be named; the new record then
cites it in `precedent.differing_fact`. Uncertain → false (reuse). A new wet-rope fact is a snag on the
reused frame, not a departure (WE-00-9). *Worst case (J):* a precedent reused where a fact differed — the
player can cite the fact; a new ruling supersedes (class iv). [R7 §4.8; R4 SG-20; 00.15.6]

**01.5.3 Adapting an anchor: knobs and the two-change limit.** `[D]` + `[J:enum]` An anchor card
(01.18, data) lists its knobs from the closed list T-00-20 with defaults and allowed deltas. An adapted
ruling may move **at most two knobs** from their defaults (00.2.7), each chosen from that knob's allowed
deltas and each justified by a cited fact:
- `dc` — the DC source or tier is re-derived because the method faces a *different obstacle* (a spear
  vault faces "clear 9 ft with a rigid pole", not "jump 9 ft"). Never "lower because it is clever".
- `attribute` — an attribute outside the verb's allowed list, only when the method honestly is that
  attribute's kind of act (00.4.1 distinguishing tests).
- `action_cost`, `time_cost` — a method that is faster or slower than the verb's default.
- `reach_unit` — what success is measured in (a Strike whose success is measured as a rope cut, not harm).
- `stakes` — the source of the threatened cost differs from the card's default source.
- `duration`, `condition`, `harm_severity`, `harm_tags`, `targets`, `focus_cost` — as named.
Picking the stakes rung or reach rung in FRAME is not a knob change; changing *where* stakes or reach
come from is. A third needed change means the anchor is wrong (re-anchor to a closer card) or the beat
is compound (return to PARSE and split). *Worst case (J):* one wrong knob value — one rung of DC, one
severity step, one condition — shown in the OFFER (class i). [R7 §3.4; 00.2.7]

**01.5.4 Logging and review.** `[D]` Every beat that used deltas, a precedent departure, an Oracle
answer, a Good Idea, a G3 redirect or a G4 is logged at RECORD as a `RulingRecord` (00.15.5), with the
neutral restatement (01.2.6), the cited facts and the frame summary. `review_flag = true` when any of
these hold: two knobs were moved; the ruling departed from a precedent; a `rule_conflict` was logged
(missing license field, two rules disagreeing, a data gap); or the ruling produced a result a data
entry forbids. Flagged rulings are Principle III's "recorded concrete failure case" evidence and are
listed for the orchestrator's review; they are never silently re-litigated in play [C:III; R4 SG-20].

### 01.6 FRAME — how hard, how dangerous, how much

FRAME fills the frame's judgment fields; `frame_check` (00.14.2 tool 1) then computes every number
(PR-00-1) and refuses an invalid frame. The five dials are kept apart: **attribute** follows the method,
**DC** follows the obstacle, **levers and snags** follow established facts, **stakes** follow what
failure would cost, **reach** follows what success can achieve [R7 §3.3 F2].

**01.6.1 Attribute.** `[J:enum]` The attribute is chosen from the anchor's allowed list
(`basic_verbs.yaml` `attribute` + `alt_attributes`, or the license's `attribute`) by the *method as
described*, using the distinguishing tests of 00.4.1. True only when the method is that attribute's kind
of act; false when the player merely prefers that attribute. When the method fits two allowed attributes
equally, the frame uses the **lower** and the OFFER names the method that would use the higher ("if
instead you vault it, Agility"); the player may re-declare at no cost (00.4.5). A method outside the
allowed list is a knob change (01.5.3). *Worst case (J):* the lower of two attributes, shown before
commitment (class ii). *Example:* "I haul myself up the rope hand over hand" → Might; "I walk the rope
like a beam" → Agility; "I climb it all night to the tower top" → Endurance. *Non-example:* "I climb
the wall — carefully, which is Agility, my best stat" — "carefully" describes no different act from
climbing by strength and grip; Might, with the OFFER naming the Agility method (a balance traverse along
the ledge) if one exists.

**01.6.2 Primary deed tag and traits.** `[J:enum]` + `[J:flag]` The primary deed tag is the most
specific `deed` tag that describes the method, classified one tag depth at a time — branch, then child (00.5.6); competence reads it.
Traits start from the anchor's `traits` list; the DM adds a trait only by a `[J:flag]` from its "true
only when" line in T-01-13 (01.17). The one trait flag the DM must always ask is **loud**: *"Does the
method involve breaking, smashing, shouting, metal on metal, a heavy fall, or an explosion?"* True →
`trait.sense.loud` is a method consequence regardless of degree. Uncertain → true (a noise consequence
is the less lenient reading). *Worst case (J):* one missing trait fails to tick one listening clock (class i;
the claim-vs-state check catches narrated noise that no trait recorded).

**01.6.3 The obstacle and its identity.** `[D]` + `[J:flag]` Every rolled beat that is not opposed by an
entity names an **obstacle**: an entity or an aspect of one (`door_archive.lock`, `door_archive.hasp`,
`wall_north`), created by write-on-mention if not already recorded (00.6.6). Two beats face the **same
obstacle** when they target the same obstacle id with the same anchor signature (anchor id plus any
`dc` knob delta, 01.5.3); a different signature on the same entity is a different obstacle (breaking
the hasp is not picking the lock; vaulting the wall is not climbing it) [R7 §5 Ex.5]. Stored DCs are
keyed `dc.<obstacle_id>.<signature>` (e.g. `dc.wall_north.verb.exert` for the climb,
`dc.wall_north.verb.exert+dc:vault` for the vault). *Worst case (J):* two beats judged to face one obstacle
(or one judged as two): a stored DC is reused where a fresh tier would apply, or the reverse; both come
from the same ladder, so the error is at most one rung, shown in the OFFER as the DC's source (class i). [integration: 00.2.3 audit]

**01.6.4 Where the DC comes from.** `[D]` First match (00.3.8, restated):
1. **Stored DC** — `dc.<obstacle>.<signature>` exists → use it. A stored DC changes only when a fact
   changes the obstacle itself (the lock is damaged; the rope is frayed), by a new write that supersedes
   the old and cites that fact.
2. **Opposed defense** — the obstacle is an entity actively resisting an aimed method →
   `10 + defender attribute + competence + edge + status`, with the attribute and tag the anchor card
   lists under `against` (01.18). Where a card lists two defense attributes, the defender uses the
   higher. Several aware defenders resisting together (watchers on a wall) → the highest defense among
   them. Defenses are computed fresh each time (never stored), because they follow the defender's
   current state.
3. **Effect DC** — the beat resists an effect (Endure, Evade) → `10 + source attribute + competence +
   edge`; for a hazard, the tier matching its severity (S1 Easy … S5 Legendary) unless ch.10 lists a DC.
4. **Obstacle tier** — `[J:rung]` (01.6.5); the engine writes the resulting DC as the stored DC.
Then, in this order, the engine adds the mode price: crude fallback `dc_shift`, or stretch
`stretch.dc_shift`, or emulate `emulate.dc_shift` (01.3.5). Situational factors never change a DC — they
are levers and snags (01.6.8). The OFFER shows the DC's source ("stored", "his guard", "the poison's
strength", "Hard") and any mode price as its own line.

**01.6.5 The obstacle tier ladder.** `[J:rung]`

```
Trigger [T]:        a rolled beat's DC source is "tier" (no stored DC, not opposed, not an effect)
Loads in:           core
License check:      as gated
Decisions (J):      1. Tier [J:rung], from T-01-2's anchors, by asking "who could do this, under these
                       conditions, with no special help?". Judge only the obstacle's INTRINSIC
                       properties — test: "Would this property still be true tomorrow, for anyone who
                       tried?" Yes (the lock is guild-made; the wall is nine feet and sheer; the tome is
                       in an archaic script) → it sets the tier. No (it is dark now; the actor is tired;
                       a guard is distracted; the player described it well) → it is a lever or snag
                       (01.6.8), never tier.
                       Do not adjust for drama, pacing, the character's stats, or how much the player
                       wants it. Between two adjacent rungs: the HIGHER.
Computation [D]:    dc = T-01-2 number; written as stored DC dc.<obstacle>.<signature>
Stakes:             —
State writes:       stored DC fact (source: ruling)
Narration may not imply: a different difficulty than the stored one on a later attempt
Worst case (J):     one rung off = 5 on the DC = 25 percentage points of success-or-better at most
                    (T-01-3); shown in the OFFER before commitment (class i), and fixed thereafter so
                    the error cannot compound or drift.
Examples:           see T-01-2 (two per rung) and WE-01-18 (a boundary pair per rung).
                    non-example: "It's only a cheap lock, surely Easy" — an assertion about an
                    intrinsic property; if unestablished, the lock's make is an Oracle question asked
                    BEFORE tiering (Likely/Even/Unlikely by the building), and the tier follows the answer.
Anchor:             no
Basis:              [00.3.16–00.3.17; T-00-5] [R4 §4.6 (Story-Engine "do not adjust for drama")] [R7 §4.2]
                    [R: https://2e.aonprd.com/Rules.aspx?ID=2628 (PF2e simple DCs by proficiency)] [DL-01-01]
```

**T-01-2 Obstacle tiers (canonical numbers in `data/resolution.yaml#dc_tiers` and `scales.yaml`).**

| Rung | DC | Anchor: who could do it (intrinsic obstacle) | Typical example | Boundary example (and why it is this rung, not the next) |
|---|---|---|---|---|
| Trivial | no roll | anyone, in these conditions, every time | open an unlocked door; walk a dry road; recall your own name for a thing | climb a knotted rope with handholds, nothing below — *not Easy, because nobody able-bodied fails it* |
| Easy | **10** | an untrained adult, taking care, usually succeeds | climb a rough stone wall with good holds; calm a familiar nervous horse | spot a carelessly hidden coin purse — *not Moderate: no trained eye is needed* |
| Moderate | **15** | needs competence; the untrained often fail | follow a clear trail across hard ground; force an iron hasp set in old oak | talk a neutral stranger into bending a small rule — *not Easy: an ordinary person usually fails without a knack for it* |
| Hard | **20** | challenges a practiced professional | pick a guild-made lock; leap a 12-ft gap from a running start | cut a hanging rope with an arrow at 60 ft — *not Very hard: a good archer hits it often enough to try* |
| Very hard | **25** | experts often fail | track a ranger over rock in rain; forge a noble's seal well enough to pass a clerk | swim a flooded river in spate in full clothes — *not Legendary: strong swimmers do it, just not reliably* |
| Legendary | **30** | the edge of mortal ability; needs levers or licenses | hold a collapsing gate alone for a minute; talk a sworn enemy into laying down arms mid-battle | climb the smooth inside of a well shaft without gear — *not Beyond: a master with chimney technique has done it* |
| Beyond | G4 | no mortal without a license that changes the category | leap a 30-ft chasm unaided; persuade a river with no spirit in it | lift a portcullis alone — *Beyond for a mortal (quality and scale), which a strength-granting license could make Legendary* |

**01.6.6 Who rolls.** `[J:flag]` The active side rolls once (00.3.3): aimed methods roll against a
defense; resisted effects make the target roll Endure or Evade against the effect DC. Test: *"Does the
effect need the source to get past the target?"* True → aimed; false → resisted; uncertain → aimed.
Adversaries' attacks are rolled by the engine against the PC's defense; the player decides, the engine
rolls. Ties: a total equal to the DC succeeds (the acting side wins ties). *Worst case (J):* the wrong side
rolls; odds move by at most the difference between the two sides' modifiers, and the OFFER shows them
(class i).

**01.6.7 Non-player attempts and fortune checks.** `[D]` When an NPC, adversary or faction agent makes an
attempt the PC is not part of but whose result matters (the messenger outrunning the storm; the rival
thief picking the vault first), and an actor with a modifier is actively trying, the engine resolves a
**fortune check**: the same pipeline with offer choice `auto`, the NPC's modifier from its state, the
obstacle's DC, stakes declared by the DM before the roll (so the result's cost is committed), and no
fate. When nobody is actively trying and the question is simply whether something is so, it is the
Oracle (01.15), not a fortune check. The test: *"Is an actor with known capability making an attempt?"*
Yes → fortune check; no → Oracle. [R5 RS-13; R: https://bladesinthedark.com/action-roll (fortune roll)]

**01.6.8 Levers and snags.** `[J:flag]` + `[J:enum]` + `[D]`

```
Trigger [T]:        FRAME, for every beat that rolls
Loads in:           core
License check:      —
Decisions (J):      1. NAME THE FACT [J:flag] per candidate: "Is there a fact id in state, established
                       BEFORE this declaration (or created by an earlier beat such as a Setup or Help),
                       that this method exploits (lever) or that works against it (snag)?" True only
                       with an id. "Cool", "clever", "well described", "surely", and "everyone knows"
                       are never facts. A player-proposed fact is an Oracle question first; its answer
                       may be cited from the NEXT beat onward (00.3.9a).
                    2. TYPE [J:enum] from what the fact does:
                       PRECISION — lets the method be done better (a tool, a blind or distracted target,
                         a running start, help, a Setup, darkness for a sneak) → +2 roll / snag −2.
                       PROTECTIVE — makes failure less bad (cover, a tied-off rope, a clear retreat,
                         soft ground below) → stakes −1 rung / snag +1 rung.
                       AMPLIFYING — makes success go further (a weak spot, numbers, a resonance, a crowd
                         on your side, a lever-arm on the load) → reach +1 rung / snag −1 rung.
                       A fact that honestly fits two types: the player picks. One fact → one lever.
                    3. Obligation: an established hindering fact that fits is ALWAYS applied as a snag
                       (the DM may not drop it). Tie-break: uncertain lever → not applied; uncertain
                       snag → applied (SG-05's anti-leniency direction).
Computation [D]:    at most two levers and two cited snags; Precision sum capped ±4 (circumstance
                    family); stakes and reach steps clamped to their ladders; engine-applied snags
                    (repetition 01.14.3) are outside the two-snag count but inside the ±4 cap.
                    frame_check refuses a lever whose fact is missing, later than the declaration, or
                    already used for another lever on this beat.
Stakes:             —
State writes:       frame.levers, frame.snags (fact ids and types); a used Setup/Help fact's use counter
Narration may not imply: a bonus that no cited fact produced
Worst case (J):     one wrongly allowed lever = +2, one stakes rung or one reach rung (class i),
                    auditable because every lever carries a fact id (INV-20).
Examples:           inside: the grit on the courtyard floor (narrated last turn) is a lever for a
                    throw-in-the-eyes Setup. outside: "there's bound to be dust somewhere" — no fact;
                    Oracle question first (Likely in a ruin), usable next beat.
                    inside: a lit torch the character holds → Precision on intimidating wolves.
                    outside: the same torch cited again as "also hot, also bright" → one fact, one lever.
                    non-example (persuasive): "I've practised this move for years, so give me +2" —
                    practice is competence, which lives in the character's state or not at all.
Anchor:             no
Basis:              [00.3.9] [R7 §3.3 F3, §4.2] [R: https://fate-srd.com/fate-core/four-actions] [R: Cypher two-asset cap via R7 §2.6] [R: PF2e ±4 circumstance cap via R7 §2.9]
```

**01.6.9 Stakes.** `[J:flag]` ×2 + `[J:flag]` lethal

```
Trigger [T]:        FRAME, for every beat that rolls
Loads in:           core
License check:      —
Decisions (J):      1. SOURCE [J:flag]: "Is there an established source that would impose a cost if this
                       beat failed?" Sources (closed list): an aware opponent or observer; a hazard; a
                       height or depth; a running clock that listens to this beat, to time or to noise; a
                       tool or item that failure could damage or lose; someone's goodwill or trust that
                       failure would spend; a resource the method consumes. False → SAFE.
                    2. HEAVY [J:flag]: "Could that source, on a failure, deliver a Heavy (S3) setback?"
                       True only for: a fall of 20 ft or more; fire, drowning, cold, poison or another
                       hazard of severity S3+; an armed opponent whose threat band ≥ the PC's power band
                       acting against the PC; the loss of an item or ally the PC cannot readily replace;
                       lasting enmity of a powerful NPC or a faction. True → DIRE; false → RISKY.
                    Tie-break for both: TRUE (the higher stakes is the honest telegraph; the player
                    sees it and may withdraw).
                    3. LETHAL [J:flag] (only if DIRE and `lethal_context: true` was recorded before this
                       declaration, 00.3.14): "Is the threatened cost cost.harm (or cost.footing into a
                       lethal hazard) from a source that can move the PC to Dying?" True → lethal.
                       When all preconditions hold, uncertain → true (the telegraph must not be
                       withheld); without lethal_context it is always false.
                    In conflict: a beat whose failure consequence is only the opponent's ordinary next
                    action is SAFE (the opponent's action is its own frame); stakes rise only when
                    failure opens something beyond that (a counter, a fall, a lost weapon).
Computation [D]:    stakes rung after Protective levers/snags and the OFFER trade (01.7.3), clamped
                    Safe…Dire; the READ table (T-01-5) gives the cost severity per degree.
Stakes:             this rule sets them
State writes:       frame.stakes.{rung, lethal, failure_preview}
Narration may not imply: a cost worse than the declared stakes allow; death on a non-lethal frame (INV-6)
Worst case (J):     one rung = one severity rung of cost, visible in the OFFER (class i). Lethal wrongly
                    false → the PC cannot die from that roll (errs safe, class iv); wrongly true → legal
                    only with the warning already on record and seen by the player before committing.
Examples:           inside SAFE: reading an old map at leisure in the inn. outside: reading the same
                    map while the owner is due back (running clock) → RISKY.
                    inside RISKY: sneaking past a sleepy guard (observer; cost S2 exposure).
                    outside: sneaking past the ogre who has already pounded two men to paste this scene
                    (armed band ≥ PC band acting against the PC) → DIRE.
                    inside DIRE: leaping a chasm over a 60-ft drop. outside: the same leap over a 10-ft
                    drop onto moss → RISKY (and the moss is a Protective lever if cited).
                    non-example: "It's not that dangerous, call it Safe" — an assertion; stakes follow
                    the sources in state.
Anchor:             no
Basis:              [00.3.14] [R: https://bladesinthedark.com/setting-position-effect] [R7 §4.2] [R1 #5; R3 #9] [BRIEF §4]
```

**01.6.10 Reach.** `[J:flag]` ×2

```
Trigger [T]:        FRAME, for every beat that rolls
Loads in:           core
License check:      —
Decisions (J):      1. WHOLE [J:flag]: "Would this method, done well, achieve the whole stated intent?"
                       True → STANDARD. False → LIMITED, and the DM restates what the method can reach
                       ("one voice can quiet this corner of the square, not the square").
                    2. ONE FACTOR [J:flag]: "Does exactly one effect factor (potency, quality, scale;
                       01.3.7) stand against the method, unoffset?" True → LIMITED (two → G4 at GATE).
                    GREAT is never picked: it is reached only by an Amplifying lever, a license or effect
                    step, or the OFFER trade (01.7.3).
                    Tie-break for 1: false (LIMITED); for 2: true (LIMITED).
Computation [D]:    reach rung after Amplifying levers/snags, effect steps (±2 cap from effects) and the
                    trade, clamped Limited…Great at framing; READ may deliver 0…4 (T-01-4).
Stakes:             —
State writes:       frame.reach.{rung, factors}
Narration may not imply: more achieved than the delivered reach allows
Worst case (J):     one rung = one clock tick, one harm severity step, or one information unit (class i).
Examples:           inside STANDARD: shoot the rope holding the chandelier (a rope can be cut by an arrow).
                    outside: shoot the iron chain holding it (quality against: LIMITED — nicked, not cut).
                    inside LIMITED: Talk a hungry, unfriendly wolf pack into withdrawing (scale against).
                    outside: the same pack when the character holds a lit torch cited as an offset for
                    potency (fire is what wolves heed) → the scale factor alone remains → still LIMITED;
                    with a second cited offset (the pack has just fed) → STANDARD.
                    non-example: "My speech is so good it should be Great" — prose earns nothing; Great
                    comes only from a cited Amplifying fact (the crowd already on your side).
Anchor:             no
Basis:              [00.3.15] [R: https://bladesinthedark.com/effect] [R7 §4.2 reach and effect factors]
```

**01.6.11 The threatened cost.** `[J:enum]` Every rolled frame declares, before the OFFER, one
**threatened cost** `{menu_id, form_intent}` from the cost menu (01.13) and, for Risky and Dire frames,
one **alternate** `{menu_id, form_intent}` that also fits. The threatened cost is what failure will cost
(at the severity READ computes); success-at-cost lets the player choose between the threatened cost and
the alternate. Selection follows 01.13.1. A Safe frame also names a threatened cost, used only on a
critical failure or a success-at-cost (both at S1). Declaring the cost before the roll is the single
strongest anti-drift commitment the research found (Burning Wheel's stated failure, 7th Sea's announced
consequences, Blades' position) [R7 §3.3 F8; R4 SG-08]. *Worst case (J):* a poorly fitting cost is
declared — the player sees it before committing and may withdraw (class ii).

**01.6.12 Frame computation.** `[D]` `frame_check` runs PR-00-1: attribute, competence (primary deed
tag and ancestors, highest), edge (cap +2), circumstance (levers and snags, cap ±4), status (worst
penalty and best bonus), clamp −8…+16; DC by 01.6.4; odds by exhaustive enumeration of the twenty
faces under the degree rule (01.8.1): success-or-better, critical success, critical failure and
near-miss percentages; plus `base_odds`, the success-or-better percentage with circumstance set to 0,
which ch.03 reads for a deed's quality (03.4) [integration: IR ch.03 to 01]; plus the cost previews for
each degree from T-01-5. If `20 + total < DC`, the
only success is a natural 20 and the OFFER must say "only a natural 20, and at best a plain success".
It refuses: an attribute not allowed by the anchor or knob; a lever or snag citing a missing or
too-recent fact; more than two cited levers or two cited snags; stakes unset; `lethal` without its
preconditions; a threatened cost whose menu id's `fits_when` has no matching fact (01.13.1); a G3 beat
without an accepted fallback.

### 01.7 OFFER — the player sees the frame before the die

**01.7.1 What the OFFER shows.** `[D]` + `[N]` Before any roll, the player receives one line of fiction
(what the attempt looks like and what hangs on it) and, in the out-of-fiction layer (00.1.7), the frame:
1. the beat as restated, its gate (verb or license id, and the mode: stretch, emulate or fallback, with
   its price on its own line);
2. the attribute and the full modifier breakdown (attribute, competence with its tag, edge, each lever
   and snag with its fact, status), and the alternative method that would use a higher attribute, if one
   exists (01.6.1);
3. the DC and its source — or, on a secret frame, "hidden" (01.4.7);
4. "you need N or better on the die", the success-or-better percentage, and the critical-success,
   critical-failure and near-miss percentages; if only a natural 20 can succeed: "only a natural 20, and
   at best a plain success" (the old rule's 5% miracle critical no longer exists, 01.8.1);
5. the stakes rung, the threatened cost with the severity it would have on a failure and on a critical
   failure, the alternate cost available on a near miss, and — if lethal — the plain sentence "this can
   kill you" with its source;
6. the reach rung and what it delivers on each degree (in the anchor's reach unit: ticks, harm severity,
   items, standing steps);
7. the action and time the beat costs, every method consequence (loud, scent, evidence left), whether
   the beat rides on an earlier result, and the character's current fate.
The player chooses: **commit**, **change** (a new method or a new lever citation: back to PARSE, free),
or **withdraw** (nothing is spent: no time, action, Focus or fate). Asking "what would it take?" or "what
are my odds?" before declaring runs GATE→FRAME→OFFER at no cost. [R7 §4.0 step 6; R4 §7.3 (visible,
pre-declared stakes make refusals legible as the game); R: https://arxiv.org/abs/2502.19519]

**01.7.2 The OFFER is binding on the DM.** `[D]` Once committed, the DC, stakes, reach, threatened and
alternate costs, lethal flag and method consequences may not change for this roll (00.13.2). A later
narration may add consequences only through CONSEQUENCE's closed sources (01.11.3). "Fudging is a named
DM mistake" [R1 01.B]; changing a committed frame is a Forcibly-Changing-Reality error [R1 01.B NCP].

**01.7.3 The ambition and caution trades.** `[D]` Once per beat, before committing, the player may make
one trade (Blades' trade of position for effect, as a pure player choice with no DM judgment) [R3 01.2;
R: https://bladesinthedark.com/setting-position-effect]:
- **Go big**: stakes +1 rung and reach +1 rung. Not allowed from Dire. Raising Risky to Dire in a scene
  with `lethal_context` re-runs the lethal flag, and the OFFER is re-shown before commitment.
- **Play it safe**: reach −1 rung and stakes −1 rung. Not allowed from Safe or from Limited.
Framed reach remains capped at Great. The trade is recorded in `frame.reach.factors` and
`frame.stakes`. It never changes the DC or the roll. **The Focus push** (05.6.7: 1 Focus for reach +1 rung
or stakes −1 rung, on a beat the character is trained at) is declared here too, beside the trade and
combinable with it, as is its alternate use **grit** (07.2.5: ignore wound penalties for the beat, no
reach) [integration: IR ch.05 to 01, IR ch.07].

**01.7.4 Auto-commit.** `[D]` A player may set the preference `auto_commit` (ch.14). Then frames whose
stakes are Safe or Risky, that are not lethal, not secret, carry no mode price (no fallback, stretch or
emulate), and show success-or-better ≥ 50%, roll without waiting (`offer.choice = auto`); the OFFER is
still written to the log and shown with the result. Every other frame waits for an explicit commit. A
lethal frame is never auto-committed (00.13.2).

### 01.8 ROLL — the degree

**01.8.1 The degree rule.** `[D]` (confirming 00.3.10; `scales.yaml` `degrees`) The engine rolls one d20
(`roll_check`). `total = d20 + modifier`; `margin = total − DC`.
1. Base degree by margin: margin ≥ +10 → **critical success**; 0…+9 → **success**; −1…−9 → **failure**;
   ≤ −10 → **critical failure**.
2. A natural 20 moves the base degree **one step up** (a critical success stays one); a natural 1 moves it
   **one step down** (a critical failure stays one).
3. The result is one of the four ids `critical_success`, `success`, `failure`, `critical_failure`.

The one-step shift is confirmed as the ruleset's rule (DL-01-02) over the old "a natural 20 is always a
critical success, a natural 1 always a critical failure". Evidence: the old rule gives every roll a 5%
critical miracle at DCs a character cannot otherwise reach (+2 vs DC 25: 5% *critical* success), and
turns certain successes into 5% critical failures for experts (+12 vs DC 10: 5% critical failure on a
total that meets the DC) — pushing permissive outcomes in the direction Principle VII guards against and
punitive ones where the lethality lock forbids them. Under the step rule "only a natural 20" is at best a
plain success, which is the honest message for the OFFER [R7 §5.9, §7.1 #1; R1 01.A; R2 01; R4 §9 01 #5;
R: https://2e.aonprd.com/Rules.aspx?ID=2286].

**01.8.2 Near miss.** `[D]` `near_miss = true` when the final degree is `failure` **and** margin ≥ −3.
This covers the ordinary near miss (a total 1–3 short) *and* a success that a natural 1 stepped down to
failure (margin ≥ 0) — the die betrayed a roll that met the DC, and the player may buy the success back
at a cost (01.9.3). A critical failure is never a near miss; a natural 20 that lifts a failure lands in
success. Width −3 is kept from R7 (15% of faces at mid-range DCs; T-01-3), making "success in some form"
at +2 vs Moderate 55% instead of 40% without erasing failure (DL-01-03; OEQ-01-1).

**01.8.3 What a critical means, in general.** `[D]` A critical success delivers one more reach rung than
framed (T-01-4) and, where the anchor's degree table lists a critical effect (a Strike's harm step, a
Setup's two uses), that effect. A critical failure raises the cost severity by one rung (T-01-5) and,
where the anchor lists one, adds its critical-failure effect (a Recall's plausible falsehood, an
emulation's backlash). Neither ever changes whether the beat was legal, and a critical failure on a
non-lethal frame can never kill (INV-6).

**01.8.4 The roll hook.** `[D]` Between the die and the degree, the `on_roll` hook fires (00.10.2):
rerolls from abilities and the fate reroll (01.16.3) resolve here, in the substrate's trigger order
(target's effects, then the actor's, then others'). A reroll replaces the die; the second result stands.
Then the degree is read and `on_degree` fires.

**01.8.5 A resolved result is final.** `[D]` Once RECORD has written a beat, later narration may add
consequences only through the closed sources of 01.11.3; it may never quietly reverse, soften or undo the
result. A DM error discovered later is corrected by ch.12's error-correction procedure (state wins, one
logged correction), never by re-narration [R1 01.B "Forcibly Changing Reality"].

**T-01-3 Degree distribution (canonical; exhaustive d20 enumeration, `odds01.py`).** Each cell:
success-or-better % (critical success / success / failure / critical failure; near miss). Near miss
counts nat-1 step-downs of successes (01.8.2); this is why +8…+16 against low DCs show 5% near miss
(00's T-00-6 was recomputed to match at integration).

| Mod | Easy 10 | Moderate 15 | Hard 20 | Very hard 25 | Legendary 30 |
|---|---|---|---|---|---|
| −2 | 45 (5/40/45/10; 15) | 20 (5/15/45/35; 15) | 5 (0/5/35/60; 5) | 5 (0/5/10/85; 0) | 0 (0/0/5/95; 0) |
| −1 | 50 (5/45/45/5; 15) | 25 (5/20/45/30; 15) | 5 (0/5/40/55; 10) | 5 (0/5/15/80; 0) | 0 (0/0/5/95; 0) |
| +0 | 55 (5/50/40/5; 15) | 30 (5/25/45/25; 15) | 5 (5/0/45/50; 15) | 5 (0/5/20/75; 0) | 0 (0/0/5/95; 0) |
| +1 | 60 (10/50/35/5; 15) | 35 (5/30/45/20; 15) | 10 (5/5/45/45; 15) | 5 (0/5/25/70; 0) | 5 (0/5/0/95; 0) |
| +2 | 65 (15/50/30/5; 15) | 40 (5/35/45/15; 15) | 15 (5/10/45/40; 15) | 5 (0/5/30/65; 0) | 5 (0/5/5/90; 0) |
| +3 | 70 (20/50/25/5; 15) | 45 (5/40/45/10; 15) | 20 (5/15/45/35; 15) | 5 (0/5/35/60; 5) | 5 (0/5/10/85; 0) |
| +4 | 75 (25/50/20/5; 15) | 50 (5/45/45/5; 15) | 25 (5/20/45/30; 15) | 5 (0/5/40/55; 10) | 5 (0/5/15/80; 0) |
| +5 | 80 (30/50/15/5; 15) | 55 (5/50/40/5; 15) | 30 (5/25/45/25; 15) | 5 (5/0/45/50; 15) | 5 (0/5/20/75; 0) |
| +6 | 85 (35/50/10/5; 10) | 60 (10/50/35/5; 15) | 35 (5/30/45/20; 15) | 10 (5/5/45/45; 15) | 5 (0/5/25/70; 0) |
| +7 | 90 (40/50/5/5; 5) | 65 (15/50/30/5; 15) | 40 (5/35/45/15; 15) | 15 (5/10/45/40; 15) | 5 (0/5/30/65; 0) |
| +8 | 95 (45/50/0/5; 0) | 70 (20/50/25/5; 15) | 45 (5/40/45/10; 15) | 20 (5/15/45/35; 15) | 5 (0/5/35/60; 5) |
| +9 | 95 (50/45/5/0; 5) | 75 (25/50/20/5; 15) | 50 (5/45/45/5; 15) | 25 (5/20/45/30; 15) | 5 (0/5/40/55; 10) |
| +10 | 95 (55/40/5/0; 5) | 80 (30/50/15/5; 15) | 55 (5/50/40/5; 15) | 30 (5/25/45/25; 15) | 5 (5/0/45/50; 15) |
| +11 | 95 (60/35/5/0; 5) | 85 (35/50/10/5; 10) | 60 (10/50/35/5; 15) | 35 (5/30/45/20; 15) | 10 (5/5/45/45; 15) |
| +12 | 95 (65/30/5/0; 5) | 90 (40/50/5/5; 5) | 65 (15/50/30/5; 15) | 40 (5/35/45/15; 15) | 15 (5/10/45/40; 15) |
| +13 | 95 (70/25/5/0; 5) | 95 (45/50/0/5; 0) | 70 (20/50/25/5; 15) | 45 (5/40/45/10; 15) | 20 (5/15/45/35; 15) |
| +14 | 95 (75/20/5/0; 5) | 95 (50/45/5/0; 5) | 75 (25/50/20/5; 15) | 50 (5/45/45/5; 15) | 25 (5/20/45/30; 15) |
| +15 | 95 (80/15/5/0; 5) | 95 (55/40/5/0; 5) | 80 (30/50/15/5; 15) | 55 (5/50/40/5; 15) | 30 (5/25/45/25; 15) |
| +16 | 95 (85/10/5/0; 5) | 95 (60/35/5/0; 5) | 85 (35/50/10/5; 10) | 60 (10/50/35/5; 15) | 35 (5/30/45/20; 15) |

**Calibration proof (CT-1…CT-6, 00.3.17).** The reference ladder Easy 10 / Moderate 15 / Hard 20 / Very
hard 25 / Legendary 30 is **confirmed unchanged** (DL-01-01). Checked by exhaustive enumeration:
CT-1 +2 vs 10 = 65% (≥ 60 ✓); CT-2 +5 vs 15 = 55% (50–65 ✓), +1 vs 15 = 35% (30–40 ✓); CT-3 +5 vs 20 =
30% (25–35 ✓), +9 vs 20 = 50% (45–55 ✓); CT-4 +5 vs 25 = 5% (≤ 10 ✓), +12 vs 25 = 40% (35–45 ✓); CT-5
+14 vs 30 = 25% (20–30 ✓), and for every modifier −8…+9 no face but a natural 20 can succeed against
30 (for modifiers of +0 and below, not even that: the stepped-up critical failure is only a failure) ✓; CT-6 across
every rung and every modifier −8…+16, wherever success-or-better ≥ 50% the critical failure rate is
≤ 5% ✓. The script then searched every ascending ladder within ±2 of the reference on each rung (3,125
candidates): 324 satisfy all six targets, and the feasible values are Easy 8–11, Moderate 14–16, Hard
19–21, Very hard 24–26, Legendary 29–31 — so every rung except Easy may move at most **±1** without
breaking a target (Moderate ±2 breaks CT-2; Hard ±2 breaks CT-3; Very hard ±2 breaks CT-4; Legendary ±2
breaks CT-5; Easy +2 breaks CT-1). The reference sits at the centre of every feasible interval except
Easy's, keeps the five-point rung spacing that makes one rung exactly two and a half Precision levers,
and keeps 00's worked examples valid. Moving Easy to 9 (the one rung with room below) would buy +5
points for untrained people on easy tasks at the cost of a non-round number the AI must hold; the
evidence gives no reason to (OEQ-01-2 names the test that would).

### 01.9 READ — what was achieved and what is due

**01.9.1 Delivered reach.** `[D]` (T-01-4; `resolution.yaml#read_delivery`)

| Degree | Delivered reach (0–4) |
|---|---|
| critical success | framed reach + 1 (Great → Exceptional 4) |
| success | framed reach |
| failure, near miss, success-at-cost taken | framed reach (a `cost.shortfall` may then lower it; never below 1) |
| failure (no success-at-cost) | 0 |
| critical failure | 0 |

Framed reach is Limited 1, Standard 2, Great 3 after levers, effects and the trade. Everything that
consumes success reads the delivered number: clock ticks = delivered reach; a harm-dealing anchor's
severity shifts by (delivered reach − 2); information items per 01.10; standing steps and NPC actions per
ch.15; conditions per the anchor card (01.18). **Overflow**: when the anchor's reach unit gives nothing
more at the delivered number (a door is simply open; the cap of a ladder is reached), each unused rung
(at most one) becomes a follow-up **Precision lever** — a fact `momentum.<actor>.<target>` usable on the
actor's next beat against the same target or situation within the scene (00.3.9f), then expired.

**01.9.2 Cost severity.** `[D]` (T-01-5; `resolution.yaml#read_costs`) Exactly one cost from the menu is
due per resolved beat, at this severity (stakes after levers, snags and the trade):

| Stakes | failure | near miss + success-at-cost | critical failure |
|---|---|---|---|
| Safe | none | S1 | S1 |
| Risky | S2 | S2 | S3 |
| Dire | S3 | S3 | S4 |

Successes and critical successes cost nothing from the menu (method consequences still apply, 01.11.2).
The critical-failure step is the single rung of 00.3.14 (`critical_failure_step: 1`); there is never a
second cost (DL-01-04 replaces R7's "Dire critical failure = two costs": one S4 cost is heavier than S3
+ S2 in harm terms, 8 vs 5 + 3, while keeping one decision, one form, one write). S5 is never reached from
a single roll; it exists for hazards, afflictions and world events, and is reachable in resolution only
through a lethal frame's harm after ch.07's rules. **Miscast.** For a working of magic, the critical
failure's cost is replaced by the branch's miscast at the same severity (Backlash, Silence or Debt;
05.7.5, DL-05-19): it is the alternate cost source of that frame [integration: IR ch.05 to 01]. A Safe critical failure costs S1 — a nuisance that
recovers within the scene, which honors Safe's promise that failure does not truly harm you while still
making the worst die face mean something.

**01.9.3 Success at a cost.** `[D]` + player choice On a near miss (01.8.2), the player chooses:
**take the failure** (delivered reach 0; the READ cost for failure at this stakes: none if Safe, else
S2/S3) or **take success at a cost** (delivered reach = framed; one cost at the near-miss column's
severity: S1 Safe, S2 Risky, S3 Dire), choosing between the threatened cost and the alternate declared at
FRAME (01.6.11). A success-at-cost is a success for every downstream rule (evidence, generation,
clocks) with degree recorded as `failure` and `success_at_cost_taken: true`; generators that key on
degree treat it as `success`. The cost may never negate the success ("a consequence never negates a
success") [R: https://bladesinthedark.com/consequences-harm; R7 §4.3]. On a Safe frame, taking the
failure is always free; on a Risky or Dire frame, taking the failure costs the same severity as
success-at-cost does, so the choice is *whether the attempt lands*, not how much it hurts.

**01.9.4 A cost must land in full.** `[D]` `apply_costs` refuses a menu entry whose target cannot bear
its full severity (a `cost.drain` of 3 Focus from a pool of 1; a `cost.gear` on a character carrying
nothing breakable; a `cost.shortfall` on a Limited beat). The DM then uses the alternate, else another
fitting entry by 01.13.1. A cost is never partially applied and never silently skipped.

### 01.10 DELIVER — graduated delivery of compound intents (P17 generalized)

**01.10.1 Scope.** `[D]` DELIVER runs for every `bundled` beat: one act that seeks N distinct pieces of
information (sub-questions) or N distinct changes (sub-intents). It generalizes constitution P17 from
information to any compound intent and hands the choice of *which* parts land to the player [R7 §4.5,
§7.1 #3; R4 §9 01 #6; R: https://bladesinthedark.com/gathering-information; Dungeon World Discern
Realities via R7 §2.4]. It does not apply to separate acts (PARSE splits those into beats) or to extra
mechanical effects beyond an anchor's own reach unit: an effect beyond harm (the chandelier *pins* him)
is a separate change that needs a reach rung or its own beat, never a free rider (Feng Shui's stunt line,
R7 §2.21).

**01.10.2 Deduplicate and count.** `[J:enum]` + `[D]` The DM lists the sub-items, then merges mutually
exclusive alternatives into one ("demon, fey or shade?" = one item: *what kind of creature?*). An item
whose answer is sealed behind a gate this beat cannot open (a letter's contents before anyone has the
letter) is **ineligible**: it is not counted, and the DM says at OFFER how it could be learned (P16).
After deduplication N is 1…5; N > 5 is not one act's worth — the beat is split or becomes `extended`.
*Worst case (J):* two items merged that were distinct — one item fewer at stake, shown in the OFFER where
the player can object (class ii).

**01.10.3 The player ranks.** `[D]` The player ranks the N items at OFFER; if they do not, declaration
order is the ranking. The ranking is deterministic and player-favoring, and removes the "DM's choice of
which half" that P17's original text left open to drift.

**01.10.4 How many land.** `[D]` `deliver_count(N, delivered_reach)` (T-01-6; `resolution.yaml#delivery_counts`):

| Delivered reach | Items delivered | N=1 | N=2 | N=3 | N=4 | N=5 |
|---|---|---|---|---|---|---|
| 4 Exceptional | N, plus one **bonus**: an unasked relevant item from the permitted slice, or a follow-up Precision lever if none remains | 1+b | 2+b | 3+b | 4+b | 5+b |
| 3 Great | N | 1 | 2 | 3 | 4 | 5 |
| 2 Standard | ⌈N/2⌉ | 1 | 1 | 2 | 2 | 3 |
| 1 Limited | max(1, ⌊N/3⌋) | 1 | 1 | 1 | 1 | 1 |
| 0 (failure) | 0 reliable; **one vague impression** of the top-ranked item | v | v | v | v | v |
| 0 (critical failure) | 0; if `misleadable`, one **plausible falsehood** about the top-ranked item | 0/f | 0/f | 0/f | 0/f | 0/f |

So a success at Standard reach delivers about half (P17's "roughly half"), a critical success from
Standard (delivered 3) delivers all, a failure gives at most one vague impression, and a critical failure
nothing reliable — exactly P17's four rows, now computed. Items land in rank order.
- **Vague impression** `[N]`: narrated hedged ("maybe that matters"), recorded as a fact with
  `certainty: believed` whose sealed truth is `true`. It is never wrong, only incomplete.
- **Plausible falsehood** `[J:flag]` *misleadable*: *"Can the source actually mislead — a lying or
  mistaken NPC, a forged or ambiguous document, half-remembered lore (Recall), a deceptive sign?"* True
  only for such sources; false for direct observation of a physical scene. Uncertain → false. The
  falsehood is recorded `certainty: believed`, sealed `truth: false`, and must be small and correctable:
  never about the existence or lethality of a threat, never enough to walk the PC into a lethal frame
  they would otherwise have been warned about (the lethal warning of 07 fires from state, not belief),
  and the next success on the same subject reveals it as wrong [R: https://2e.aonprd.com/Rules.aspx?ID=2286
  via R7 §2.9]. *Worst case:* one small wrong belief on the top-ranked item, self-correcting (class iii).

**01.10.5 Which content answers each item.** `[J:enum]` For each delivered item, the DM chooses which
permitted node of the target's sealed slice answers it (the relevance judgment the AI is good at), never
content beyond the permitted slice (INV-10) [R4 §5.2 #3; R1 01.D]. Delivered answers are written with
`record_knowledge` and `set_fact` before narration. *Worst case (J):* a less relevant permitted node answers an
item; the player still learns only permitted, true content, and the question stays open for a later beat
(01.10.6) (class iii). [integration: 00.2.3 audit]

**01.10.6 Undelivered items stay unresolved, not wrong.** `[D]` They remain open questions. Re-asking
them is a new beat on the same obstacle and rides on this one (01.4.2): it needs a new method, a new
lever, a passed interval, or the re-attempt cost (one `cost.time` or `cost.exposure` at the frame's
stakes severity, S1 if Safe, paid up front). This is P17's no-free-retry rule.

**01.10.7 Sub-intents.** `[D]` A bundle of changes from one act ("I kick the brazier over to set the
tapestry burning, scatter the guards and block the stair with coals") delivers changes by the same
count and the player's ranking; each delivered change is written as its own state write. Each
sub-intent must be something the act could produce by itself (else it is not in the bundle, 01.2.2).

### 01.11 CONSEQUENCE — costs, method consequences, and what's next

**01.11.1 Applying the due cost.** `[J:enum]` + `[D]` If READ made a cost due (T-01-5 or a
success-at-cost), CONSEQUENCE applies exactly one cost: the threatened cost for a failure or critical
failure; the player's pick of threatened or alternate for a success-at-cost. The DM chooses the
**form** `[J:enum]` from that menu entry's allowed forms *at the computed severity* (01.13, T-01-7) —
never a form of another severity — and `apply_costs(frame_id, [{menu_id, form}])` performs the entry's
state writes. If the entry cannot land in full (01.9.4), the alternate applies; if neither can, the
selection order of 01.13.1 picks the next fitting entry. The DM chooses *which fictional form*; the
table fixes *whether* and *how big* (SG-09). *Worst case (J):* a less apt form of the right entry and
severity — the same mechanical weight, logged with the frame (class i).

**01.11.2 Method consequences.** `[J:flag]` + `[D]` A method consequence is what the *method* causes
whatever the degree: noise, a trail, evidence left behind, a broken door that stays broken, a fire that
keeps burning, the known harm of a certain-with-cost beat, a crude fallback's listed consequence, an
effect's stated side effect. Consequences come only from these closed sources, each declared at FRAME
and shown at OFFER: (a) the beat's trait tags (T-01-13: loud, audible, visible, scent); (b) the anchor
card's `consequences` field (01.18); (c) a license, effect or fallback text; (d) a fact the method
necessarily creates (`[J:flag]` *"Would this state exist after the act whether or not the intent
succeeded?"* — true only for physical traces of the act itself). Consequences are applied at RECORD
through their own writes (a `trait.sense.loud` beat ticks every clock that lists it; a scent trail is
written as a fact) [R: https://theangrygm.com/adjudicate-actions-like-a-boss/ (outcome vs
consequence); R7 §4.0 step 10]. *Worst case (J):* one consequence missed or added — one listed tick or one
fact (class i), caught by the claim-vs-state check.

**01.11.3 The closed list of complications.** `[D]` Nothing bad happens to the PC unless it comes from
one of these sources, each tied to state: (1) a cost due from READ; (2) a method consequence declared at
FRAME; (3) a clock tick or completion from the clock's own `tick_sources`/`auto_ticks`; (4) an
adversary's or NPC's own action on its turn or from its behavior list (06, 09, 12); (5) a boundary
handler (an encounter or omen check, a World Turn event, ch.12's pacing push `h.12.pacing_push`; 00.7)
[integration: IR ch.12 to 01]; (6) ch.12's P16 lead injection or its
tension-driven scene tests; (7) an Oracle answer to a question somebody asked. "The DM wants a
complication" is not on the list — the deterministic stand-in for a Cypher intrusion is (3)–(6) [R7 §6].

**01.11.4 A next step always exists (P16).** `[J:flag]` After CONSEQUENCE, the DM checks *"Does the
player now have at least one concrete, actionable option — a lead, a threat, a choice, a route, a person,
a consequence to respond to?"* True only when one can be named from state. If false, the DM names one
from state in the narration (the fallback path of the redirect, an exit, an NPC present, a clock's
omen), and if none exists in state, ch.12's lead injection fires. For ch.12's inconclusive-streak
counter (`h.12.inconclusive_streak`), a beat is **inconclusive** `[D]` when it wrote no new fact the PC
learned, no clock change, no position change and no delivered reach ≥ 1 — a Safe failure, a vague
impression only, or a restated ride. Three inconclusive beats in a row raise the trigger [C:P16].
*Worst case (J):* the check passes when no real option exists; the inconclusive-streak counter fires ch.12's
lead injection within three beats (class iv). [integration: 00.2.3 audit]

### 01.12 RECORD — state first, then words

**01.12.1 The recording order.** `[D]` At the end of every beat, in this order: (1) every state write of
the success, cost, delivery and method consequences (`apply_costs`, `apply_harm`, `apply_condition`,
`tick_clock`, `set_fact`, `update_quantity`, `set_position`, `record_knowledge`, `unseal`); (2) the
stored DC for a newly tiered obstacle; (3) the ride record (01.4.2); (4) evidence events through
`record_evidence` wherever ch.03's significance criteria hold, by running **PR-03-1** — only for
**resolved** outcomes (a degree, a Good Idea, or take-the-time; never an asserted or narrated one)
[R3 01.8; integration: IR ch.03 to 01]; (5) the ruling record (01.5.4); (6) `mark_boundary(beat_end)`,
which runs every `beat_end` handler of T-00-9 (`h.04.crisis_check`, `h.01.ruling_log`, `h.10.site_time`,
`h.12.inconclusive_streak`). Only then is narration written, and it restates only what the store
holds (INV-2).

**01.12.2 What narration of any resolved beat may not imply.** `[N]` Any of: a degree other than the
computed one; reach beyond the delivered number; a cost of another menu entry or severity; a license
doing more than its scope; a new fact not written this turn; a mechanical number voiced in fiction
(T-00-22); a sealed fact; "almost" on a secret frame; a death on a non-lethal frame. Narration *must*
name: every visible condition applied, one omen per hidden or sensed clock tick (INV-14), every changed
range band or positional flag, and the chosen cost's form.

**01.12.3 The ruling-log handler.** `[D]` `h.01.ruling_log` (boundary `beat_end`, phase 9): finalizes the
frame (immutable thereafter), writes the ruling record when 01.5.4 requires one, and closes any Setup or
Help lever uses consumed by the beat.

### 01.13 The cost menu

The menu is closed: nine entries, whose ids 00 reserved (`substrate.yaml` `reserved_ids.cost_menu`).
Each entry has a `fits_when` test, allowed fictional forms per severity rung, and exact state writes.
Severity per 00.3.11: S1 Light, S2 Moderate, S3 Heavy, S4 Grievous, S5 Catastrophic; `U(S)` = 1, 1, 2,
3, 4. In resolution, costs are S1–S4 (T-01-5); S5 forms are listed for completeness because hazards,
afflictions and world events (07, 10, 11) reuse the menu. Canonical data: `resolution.yaml#cost_menu`.

**01.13.1 Choosing a cost entry.** `[J:enum]`

```
Trigger [T]:        FRAME declares a threatened and an alternate cost; CONSEQUENCE must re-pick
                    when a declared entry cannot land
Loads in:           core
License check:      —
Decisions (J):      1. Candidates [J:flag per entry]: entries whose `fits_when` is true, each citing the
                       fact id of its source (the height, the observer, the tool, the clock, the
                       person). An entry with no citable source is not a candidate — costs never come
                       from nowhere.
                    2. Pick, first match:
                       (a) the entry already threatened in the scene — a running clock or an established
                           pressure that this failure would feed (the alarm → exposure; the collapsing
                           roof → time);
                       (b) the entry whose source the method most directly engages: body exposed to a
                           source of harm → harm; body position or grip → footing; stealth, lies or
                           noise → exposure; time while something moves → time; a tool or weapon →
                           gear; effort or supplies → drain; a person or institution that can refuse →
                           closed_door;
                       (c) not the same entry as the last cost paid against this obstacle, if another
                           candidate fits (repetition is W10's failure);
                       (d) cost.twist, only when no other entry is a candidate.
                       Ties within a step: the order harm, footing, exposure, time, gear, drain,
                       closed_door. cost.shortfall is only ever an alternate, never threatened.
Computation [D]:    none (the severity comes from READ)
Stakes:             —
State writes:       frame.costs (declared); applied at CONSEQUENCE
Narration may not imply: a cost of another entry or severity
Worst case (J):     a less apt entry at the same severity — the player saw it in the OFFER before
                    committing (class ii), and one severity rung is the largest mechanical difference
                    any pick can make (class i).
Examples:           inside: breaking a hasp in a guarded keep (noise, observers) → exposure threatened,
                    gear (the iron bar) alternate. outside: breaking the same hasp in an abandoned
                    mill → no observer: exposure is not a candidate; footing or gear.
                    non-example: choosing cost.harm for a failed library search because "papercuts" —
                    no source of harm is engaged; time (the lamp oil, the librarian's return) fits.
Anchor:             no
Basis:              [R7 §4.3] [R: https://bladesinthedark.com/consequences-harm] [R: Ironsworn Pay the Price via R5 P-16] [R4 SG-09]
```

**01.13.2 `cost.harm` — Harm.** `[D]`
*Fits when:* the method exposes the actor's body to an established source of harm (a fall, a blow, a
blade, fire, cold, water, a thorn hedge, the creature being wrestled, a hazard). *False for:* purely
mental or social beats, or when no source is established.
*Writes:* `apply_harm(target, severity, harm_tags = the source's harm tags (falls and impacts
harm.physical.crush), source {entity, frame_id}, lethal = frame.lethal)`; ch.07 applies Vitality loss,
reduction and harm-state transitions. The target is the actor, or a helper who shared the beat
(01.14.8). On a frame with `lethal: false` the harm can never move the PC into Dying (INV-6; interface
request to 07).

| Severity | Harm before mitigation | Allowed forms |
|---|---|---|
| S1 | 1 | a scrape, bruise, singe, wrenched finger; shaken by a near thing |
| S2 | 3 | a cut, a burn, a hard fall, a sprain, a blow that lands |
| S3 | 5 | a telling blow, a bad burn, a fall that knocks the wind out, a deep gash |
| S4 | 8 | a broken bone, a grievous wound (ch.07 decides wounds and marks) |
| S5 | 12 | crushing, drowning, burning at the heart of a fire (hazards and lethal frames only) |

**01.13.3 `cost.drain` — Drain.** `[D]`
*Fits when:* the method spent effort or consumed something: Focus (only when the beat used an ability,
concentration, or the ch.05 push), supply, ammunition, light, a consumable's uses, coin carried for the
purpose. *False for:* a quantity the method did not engage.
*Writes:* `update_quantity(actor, quantity, −U(severity), reason, frame_id)`.

| Severity | Units lost | Allowed forms |
|---|---|---|
| S1 | 1 | an arrow lost, a torch guttering early, a coin fumbled away |
| S2 | 1 | 1 Focus spent to no purpose; a ration spoiled; a flask spilled |
| S3 | 2 | 2 Focus; two supply; the quiver's last arrows scattered |
| S4 | 3 | 3 Focus; a pack of supplies ruined |
| S5 | 4 | 4 Focus; the whole store lost |

Must land in full (01.9.4): a pool holding fewer units than U cannot be drained at that severity.

**01.13.4 `cost.gear` — Gear.** `[D]`
*Fits when:* the method uses a carried item or exposes one (a weapon, a tool, a pack while climbing).
*False for:* items flagged `cost_immune: true` by ch.08 (bound relics) and items not established as
carried.
*Writes:* on the item entity:

| Severity | State write | Allowed forms |
|---|---|---|
| S1 | `location = ground at the actor's position` (picking it up: free outside conflict; an action in conflict, 06) | dropped, knocked from the hand, slips from the belt |
| S2 | `location = <a named place>`, not held | left on the far side of the wall, falls down the well shaft, stuck high in a beam |
| S3 | `condition = damaged` — its edge, harm_edge and reduction properties (08) do not apply until repaired (Handle crude repair: Easy, 1 interval; or a craft license) | notched, bent, cracked, a torn strap |
| S4 | `condition = broken` (unusable until repaired under a craft license) **or** `location = <an opponent's possession>` | snapped, shattered, wrenched away and held by the foe |
| S5 | `exists = destroyed`, or location sealed as unknown; an item with a signature or a bound ability always takes the location form, never `destroyed` (08.1.9) [integration: IR ch.08 to 01] | burned to ash, swept away in the flood (signature or bound items: lost in the flood, its place unknown) |

**01.13.5 `cost.time` — Time.** `[D]`
*Fits when:* the method takes time while something else moves — a clock in the scene lists `cost.time`
as a tick source (pursuit, deadline, a roof collapsing, a guard returning), or the mode's time matters
(light burning down, night coming, a journey's days). *False in conflict mode* unless a listening clock
exists.
*Writes:* if any active clock lists `cost.time`, `tick_clock` by U(severity) on the one nearest
completion (ties: the one named in the threatened cost). Otherwise `advance_time` by T-01-9, which runs
every boundary crossed (INV-15):

**T-01-9 Time cost by mode.**

| Severity | site | free | travel | downtime |
|---|---|---|---|---|
| S1 | 1 interval | 1 interval | 1 hour | 1 day |
| S2 | 1 interval | 1 hour | 3 hours | 1 day |
| S3 | 2 intervals | 2 hours | 1 watch | 2 days |
| S4 | 3 intervals | 1 watch | 2 watches | 3 days |
| S5 | 4 intervals | 1 day | 1 day | 1 week |

*Allowed forms:* fumbling, backtracking, waiting for a second chance, a detour, a delay while the
opportunity passes.

**01.13.6 `cost.exposure` — Exposure.** `[D]`
*Fits when:* the method involves stealth, deception, trespass or noise, and an observer, listener or
listening clock is established. *False for:* a scene with no one to notice.
*Writes:* tick every active clock listing `cost.exposure` by U(severity), plus:

| Severity | State write (observer = the cited observer) | Allowed forms |
|---|---|---|
| S1 | observer `alertness` +1 step (unaware → suspicious → alert → alarmed) | a head turns; a dog stirs; "who's there?" |
| S2 | + `record_knowledge(observer, "someone is at <place>")`; alertness at least alert | noticed: a shape, a sound, a lie that doesn't sit right |
| S3 | + actor loses `flag.hidden`; observer knows the actor's location; alertness alarmed | spotted: a shout, a pointing finger, "that one!" |
| S4 | + `record_knowledge(observer, identity and deed of the actor)` | identified: your face seen, your name spoken, your forged letter recognized |
| S5 | + the deed and identity become known to the observer's faction or the public: a reputation content entry (11) | exposed: the story is all over town by nightfall |

**01.13.7 `cost.footing` — Footing.** `[D]`
*Fits when:* the actor's body position, balance, grip or place in a fight or on terrain is at stake.
*False for:* purely mental or social beats. Conditions are ch.06's definitions of the reserved ids.

| Severity | State write | Allowed forms |
|---|---|---|
| S1 | `cond.off_balance` (S1; until the end of the actor's next turn, or the next beat outside conflict) **or** lose one favorable flag (`flag.in_cover`, `flag.elevated`, `flag.hidden`) | stumble, slip, lose the good angle |
| S2 | `cond.prone`, **or** `cond.grabbed` by the engaged opponent, **or** one range band against the intent (06), **or** slide to an adjacent worse position in the place graph | knocked down, caught by the collar, driven back, slide down the scree |
| S3 | `cond.restrained` **or** `flag.cornered` **or** `cond.slowed` (scene), **or** separated: two bands from allies or goal | tangled, backed into the corner, hobbled, cut off |
| S4 | `cond.pinned`, **or** moved into the next lower or worse place (a fall into the pit, the river's current), **or** held in the opponent's control | pinned beneath, over the edge, dragged off |
| S5 | trapped: `cond.restrained` (duration until_cleansed) inside a hazard's reach, or swept to a distant place | buried in the collapse, carried off by the flood |
Moving the actor into a hazard does not also deal harm as part of this cost; the hazard then acts on its
own cadence (10), which the OFFER must have shown.

**01.13.8 `cost.shortfall` — Shortfall.** `[D]`
*Fits when:* only on a success-at-cost, and only when the method could plausibly have worked partway.
*Writes:* delivered reach −1 (S1, S2) or −2 (S3), never below 1. Illegal when delivered reach is already
1. S4/S5: not applicable (success-at-cost never exceeds S3).
*Allowed forms:* the door opens a hand's breadth; he believes half of it; the rope holds but the far
anchor is loose; you get the gist, not the details.

**01.13.9 `cost.closed_door` — Closed door.** `[D]`
*Fits when:* the method is a one-shot attempt against something that can refuse or seize up: a
persuasion, bargain, bluff or request to an entity or institution; a mechanism that jams; a trust that
can be spent. *False for:* a repeatable physical attempt against an inert obstacle.

| Severity | State write | Allowed forms |
|---|---|---|
| S1 | `closed.<obstacle>.<method_class> = until scene_end` | "not now"; the latch jams for the moment |
| S2 | closed until a new fact changes the situation (the re-attempt cost of 01.4.2 cannot reopen it) | "I've heard enough"; the mechanism is fouled |
| S3 | S2 + target's standing toward the actor −1 (`set_relationship`, 15) | offended; suspicious of you now |
| S4 | S2 + standing −2 + a refusal fact on the target naming its lifting condition (15) | "don't come back until you've paid what you owe" |
| S5 | S4 + the target's faction status toward the PC −1 (11) | the guild closes its doors to you |
Standing writes are legal only on entities that carry standing.

**01.13.10 `cost.twist` — Twist.** `[D]` + `[J:enum]`
*Fits when:* always — but it is picked only when no other entry fits (01.13.1 d).
*Writes:* `roll_table(tbl.twist, context {severity, scene tags, band})` (ch.12 owns the table and must
provide rows for each severity band); the row's writes create the entities, clocks or facts. The DM
chooses the fictional form of the rolled row. Twists never directly harm (that is `cost.harm`) and never
kill.

| Severity | What the rolled row may introduce |
|---|---|
| S1 | a complication: a small new obstacle, an interruption, an unwelcome witness — no threat |
| S2 | a new obstacle that needs its own beat to overcome |
| S3 | a new threat: an adversary or hazard with threat band ≤ the scene's, or a new danger clock with 1 tick |
| S4 | an escalation: a threat up to the scene's band + 1, an existing danger clock +3, or the opposition's allies arrive |
| S5 | a reversal (world events only): an ally turns, a haven falls, a thread fails |

*Worst case (J):* a less fitting fictional form is chosen for the rolled row; the row, its severity and its
writes are the table's, so nothing mechanical moves (class i). [integration: 00.2.3 audit]

### 01.14 Compound shapes, groups, help and setup

**01.14.1 Sequential (linked) beats.** `[D]` Beats marked `sequential` resolve in order, each through
the whole pipeline with its own action cost (06) and time. The earlier beat's degree feeds the later
beat [R7 §4.6; Burning Wheel linked tests, R7 §2.14]:

| Earlier beat's degree | Effect on the later beat |
|---|---|
| critical success | the later beat gains whatever the earlier beat was for (the Setup's lever, the position, the opening) **plus** one extra lever of the player's choice, Precision or Amplifying (fact `linked.<beat>`) |
| success (incl. success-at-cost) | the later beat gains what the earlier beat was for |
| failure | the later beat may go ahead without it at stakes +1 rung, or be abandoned with no action or time spent (player's choice at the new OFFER) |
| critical failure | the later beat cannot go ahead as planned; the earlier beat's cost applies; the player re-declares |

The later beat's frame is built after the earlier beat's RECORD, so any fact the earlier beat created is
established before the later declaration and may be cited as a lever (00.3.9a).

**01.14.2 Bundled beats.** `[D]` One act, N items: DELIVER (01.10).

**01.14.3 Repeated acts and the repeated-attempt shape.** `[D]` + `[J:flag]` "I shoot it ten times"
is a `repeated` beat. It is resolved by two rules and never by raising the DC — the DC is how hard one
instance is; quantity belongs to the action economy [R7 §5 Ex.7; R1 01.C; R: https://2e.aonprd.com/Rules.aspx?ID=2286 (multiple attack penalty)]:
1. **Throttle.** The number of instances resolved is the least of: the player's stated number (SG-01),
   the actions the actor has in the window (ch.06's economy in conflict), and what the time available
   allows (outside conflict: one instance per beat's time unit of the mode, 00.7.3). Instances beyond
   the throttle are not resolved; the DM says how many fit and the player may reorder or spend spare
   actions on something else (the OFFER shows both).
2. **Repetition penalty (the shape ch.06 uses for attacks).** Each instance is its own frame and roll.
   Within one **window**, the k-th instance carries **k − 1 engine-applied Precision snags**, at most two
   (k = 1: 0; k = 2: −2; k ≥ 3: −4). The snags cite the engine fact `repeat.<actor>.<window>.<k>`; they
   are outside the two-cited-snag limit but inside the ±4 circumstance cap (so levers still offset them,
   and nothing stacks past −4). **Window:** in conflict, the actor's turn; outside conflict, one
   repeated beat. **What counts as the same act:** in conflict, every beat bearing `trait.action.attack`
   counts toward the same window whatever its target (so switching targets does not reset it); outside
   conflict, instances of the same verb against the same obstacle. Uncertain → counts. The window resets
   at its end. Ch.06 owns the attack numbers and may set any non-increasing sequence within the ±4 cap
   (the default here, 0/−2/−4, is DL-01-08); every other repeated act uses this default.
*Worst case (J):* one instance wrongly counted or uncounted — a 2-point difference on one roll (class i).
*Arithmetic:* Wren (Agility +3, archery +2 = +5) shooting three times at Guard 16 in one turn: 50%,
40%, 30% → P(at least one hit) = 1 − 0.50 × 0.60 × 0.70 = **79%**; the probe's single DC-25 roll gave 5%.

**01.14.4 Conditional beats.** `[D]` "If X, then Y": resolve X first — X is usually a G0 question
(Oracle, 01.15), sometimes an earlier beat's result. If X is true, Y proceeds as its own beat. If X is
false, Y is **void**: no time, action or Focus spent, and the DM says in the same breath what *is* true
(P16) [R7 §4.6, §5 Ex.13].

**01.14.5 Opposed and contested attempts.** `[D]` Every opposed attempt is **one d20** rolled by the
active side against the other side's defense (01.6.4 source 2, 01.6.6); a tie goes to the acting side.
There are no roll-offs. A true **contest** — both sides actively pursuing mutually exclusive goals over
time (a race, a tug-of-war, a chase, a war of words before a council) — is two **racing clocks** or one
**tug clock** (00.8.5–00.8.6): each side's beats tick its own clock by delivered reach (or push the tug
clock), the opposing side's actions are rolled by the engine as fortune checks against the PC's
defense or the obstacle, and the first clock to fill wins. The test between the two: `[J:flag]` *"Is the
outcome settled in one exchange?"* True → one opposed roll; false → a contest of clocks. Uncertain →
one roll (fewer rolls compound less). *Worst case:* a contest resolved in one roll or vice versa — the
OFFER shows the structure first (class ii). [R7 §2.1 Fate contests; R: https://bladesinthedark.com/progress-clocks]

**01.14.6 Extended actions (clocks).** `[D]` + `[J:rung]` An `extended` beat creates or advances a
**progress clock named for the obstacle** (SG-24: "The sealed vault", not "Crack the vault"), per 00.8:
- **Size** `[J:rung]` from 00.8.3 (4 a scene's worth; 6 complicated; 8 daunting; 12 a long project) unless
  a template in data fixes it. *Worst case (J):* one rung = 2–4 segments (class i).
- **Tick interval**: the clock declares one (per round, interval, hour, scene, day or week, by the mode).
  At most one roll per interval ticks it (let it ride applies to the interval, 01.4.2 item 4).
- **Each roll**: the obstacle's DC (stored on the clock's obstacle); ticks = **delivered reach** (0–4,
  so Limited 1, Standard 2, Great 3, a critical success one more; a success-at-cost ticks by framed
  reach and pays its cost; a failure ticks 0 and pays the failure cost; a critical failure ticks 0 and
  pays the critical cost). A paired danger clock, if one exists, ticks from its own sources — the
  cost.time and cost.exposure costs paid on the progress rolls usually feed it.
- **Varied approaches** (optional template field `requires_varied_approach: true`): the same anchor may
  not tick the clock on two consecutive rolls, so a solo character solves a many-sided problem through
  several of its facets — the single-player form of a skill challenge [R1 01.E].
- **Completion** writes the intent's result through the clock's `on_complete` effects.
Learning a language, researching a spell, winning a council, tunnelling out: all are this rule.
[R7 §4.6; R: https://bladesinthedark.com/progress-clocks; R5 P-17]

**01.14.7 Group actions.** `[J:flag]` + `[D]` When the PC and allies (companions, hirelings, NPCs acting
with the PC; ch.16) attempt the same thing together, it is **one roll**, whose modifier depends on the
group test `[J:flag]` *"Must every member succeed for the group to succeed?"*:
- **All must** (sneak past together, cross the ledge together, stay unseen as a party): the roll uses the
  **lowest** base modifier in the group — the party is as quiet as its loudest member. A cost lands on
  that member unless another member's method engaged the cost's source.
- **Any may** (search a hall together, spot the ambush, recall a fact among you): the roll uses the
  **highest** base modifier.
Other members may give Help (01.14.8), at most one Help lever. Uncertain → all must. *Worst case (J):* the
wrong one of two members' modifiers (class i), shown in the OFFER. [R: 5e group checks via R7 §2.8; DL-01-10]

**01.14.8 Help (`verb.help`).** `[J:flag]` + `[D]`

```
Trigger [T]:        an entity declares it helps another's beat (the PC helping an NPC, or an ally helping
                    the PC through ch.16's command action)
Loads in:           core
License check:      basic verb: verb.help; plus the HELPER must pass the gate for the helped method
Decisions (J):      1. ELIGIBLE [J:flag]: "Could the helper attempt the helped beat alone right now?"
                       True only when the helper would gate G1 or G2 for that method (holds any needed
                       license), is in position (range band, place), and no condition forbids it.
                       False for tasks that cannot be shared (one keyhole, one throat to persuade in
                       private, threading a needle). Uncertain → false.
                    2. UNCERTAIN HELP [J:flag] (01.4.1 applied to the help itself): does helping need its
                       own roll? Usually false; true when the help is itself risky (holding the rope
                       in the gale).
Computation [D]:    the helped beat gains one Precision lever citing the fact `help.<helper>.<beat>`.
                    At most one Help lever per beat, however many helpers. The helper spends its own
                    action (06) and the beat's time. If the help rolled: CS/S → lever; failure → no
                    lever; critical failure → a snag on the helped beat instead.
Stakes:             the helper shares the helped beat's exposure: the helped beat's cost may land on the
                    helper when the helper's method engaged the cost's source (named at FRAME in the
                    threatened cost).
State writes:       help fact; helper's action spent; any cost on the helper
Narration may not imply: that help guaranteed success
Worst case (J):     an ineligible helper's lever allowed — +2 on one roll (class i).
Examples:           inside: a companion who can climb braces the rope for Wren's climb → +2.
                    outside: a companion who holds no lockwork license "helps" pick the lock → not
                    eligible (they could not attempt it alone).
                    non-example: "everyone in the tavern helps me convince him" — one Help lever at
                    most; a crowd on your side, if established, is an Amplifying fact instead.
Anchor:             yes (verb.help card, 01.18)
Basis:              [R7 §4.1] [R: 5e working together via R7 §2.8] [R: https://bladesinthedark.com/teamwork]
```

**01.14.9 Setup (`verb.setup`).** `[J:enum]` + `[D]` A Setup creates a citable fact that is a lever
for a later beat of the actor or an ally — a feint, a distraction, sand in the eyes, a prepared
position, a greased floor, a lure [Fate Create an Advantage; Blades setup; Savage Worlds Tests;
Ironsworn Secure an Advantage — R7 §2.1, §2.2, §2.5, §2.7]. The DM classifies the lever **type** it will
create by what the fact does (01.6.8 decision 2) and declares it at FRAME. Against a creature, the DC is
the creature's defense by the method (feint vs Wits; blinding throw vs Agility; a distracting story vs
Wits); against the environment, the tier. Degrees: **critical success** — the fact serves two beats (two
uses, by the actor or allies); **success** — one use; **near miss** — success-at-cost available;
**failure** — no fact, and the failure cost; **critical failure** — no fact, the target is forewarned (a
snag fact against the intended follow-up), and the critical cost. Duration: in conflict, until used or
the end of the setting actor's next turn; outside conflict, until used or `scene_end`. The `condition`
knob lets a Setup apply one of `cond.distracted`, `cond.off_balance`, `cond.exposed` or, only by a
method that can do it (grit, glare, smoke), `cond.blinded`, until the end of the target's next turn; the
condition's own effects apply (06) and the condition is itself citable as a lever. A Setup cannot create
a license, a fact about something unestablished (that is the Oracle's), or more than one lever type.
*Worst case (J):* the wrong lever type is declared: +2 on a roll instead of one stakes or reach rung, or the
reverse, declared at FRAME and shown before commitment (class i). [integration: 00.2.3 audit]

**01.14.10 Ready (`verb.ready`).** `[D]` + `[J:flag]` Ready holds a beat for a stated trigger. The beat
is framed and offered when readied (so its stakes and odds are committed), and rolled when the trigger
occurs. The trigger must be an **observable event** `[J:flag]` ("when the door opens", "if he draws") —
true only for something the actor would perceive; false for another's intent or a hidden fact. If the
trigger never occurs before the readied window ends (ch.06: the actor's next turn; outside conflict:
scene end), the beat lapses with nothing spent but the action. Ch.06 owns how Ready interacts with
reactions and turn order. *Worst case (J):* an unobservable trigger is accepted and the readied beat fires a
moment early or late; it was framed and offered when readied, so its odds and stakes do not change
(class i). [integration: 00.2.3 audit]

### 01.15 The World-Fact Oracle

**01.15.1 When the Oracle is asked.** `[J:flag]` + `[D]` The Oracle settles a yes/no question about the
world when the answer is **unestablished** (not in state, not implied by narration) and **not settled
by canon or scene logic**. It is asked for: G0 questions (01.3.8); facts embedded in a declaration
("surely there's a rope"); undetermined properties when first needed (00.6.6); the X of a conditional;
existence questions behind a search (sealed, 01.15.6). It is not asked for: established facts (never
re-rolled); things somebody is actively attempting (a fortune check, 01.6.7); content choices a
`roll_table` answers better (who answers the door, what the rumor says — ch.12's tables); anything the
DM could decide "for drama" (SG-12). Test: *"Is there a fact id that answers it, or does canon/scene
type settle it?"* True → no roll (Certain or Impossible, or read the fact). *Worst case (J):* a question that
canon or the scene settles is rolled instead of read; its odds still come from the scene, so it departs from
the settled answer only on a long-odds roll, and a contradiction with recorded canon is caught by the
claim check and corrected (12.3; class iv). [integration: 00.2.3 audit] [R7 §4.7; R5 P-01–P-03; R:
https://ironsworn-rpg.fandom.com/wiki/Ask_the_Oracle; 00.12.7]

**01.15.2 Choosing the odds.** `[J:rung]`

```
Trigger [T]:        an Oracle question is to be rolled
Loads in:           core
License check:      —
Decisions (J):      1. Odds rung, chosen BEFORE rolling, from the nature of the place, people and
                       situation — never from what the player wants, how they phrased it, or what would
                       make a better story. Anchors (T-01-10):
                       CERTAIN (no roll, yes): the scene type implies it — a stable has straw; a smithy
                         has a quench trough.
                       LIKELY: commonly true of such places or people — a kitchen has a back door; a
                         ruined courtyard has loose grit.
                       EVEN: could go either way — the magistrate is in his office at midday; the ford
                         is passable after two dry weeks.
                       UNLIKELY: uncommon but unremarkable — a gate guard has a brother lost at sea; a
                         river holds a spirit of place (where spirits are rare).
                       REMOTE: rare, would be noteworthy — the peddler carries a dragon's tooth; the
                         dungeon has a working lift.
                       IMPOSSIBLE (no roll, no): contradicts canon or an established fact.
                       Tie between two adjacent rungs: the rung LESS favorable to what the asking player
                       evidently hopes for; if no hope is evident, the rung nearer Even.
                    2. ch.12's tension dial may shift the rung by at most one (00.12.7), and only on a
                       question tagged with an **eventful answer** (12.6.4); it never moves a player's
                       G0 question, so a player's fishing is never moved by the dial
                       [integration: IR ch.12 to 01; DL-12-07].
Computation [D]:    oracle(question, odds_rung, fact_key) → d100, answer shape (T-01-10), fact written
Stakes:             none (a question, not an attempt)
State writes:       the fact (source: oracle; certainty established; visibility per the question);
                    the oracle log entry
Narration may not imply: an answer other than the rolled shape; that the player's wish moved it
Worst case (J):     one rung off shifts the yes-chance by 15–25 points (T-01-10), logged with the
                    question and its odds before the roll (class i/iv). Test OR-1 (OEQ-01-4)
                    measures odds drift under player wanting.
Examples:           inside LIKELY: a back door in an inn with a kitchen. outside: a back door in a
                    watchtower → UNLIKELY (towers are built with one door).
                    inside UNLIKELY: a spirit in this ordinary river. outside: a spirit in the river
                    the villagers leave offerings at (established shrine) → LIKELY.
                    non-example: "Please let there be a rope, I really need one" — the plea moves
                    nothing; a storeroom of a ship → LIKELY; a noble's bedchamber → UNLIKELY.
Anchor:             no
Basis:              [R7 §4.7] [R4 S5 (relative likelihood is a strength), W6 (sampling is not)] [R5 P-01, P-02]
```

**01.15.3 Thresholds and the answer shape.** `[D]` The engine rolls d100 (1–100). **Yes** when the roll
is at or above the rung's threshold: Likely 26, Even 51, Unlikely 76, Remote 91 (the Ironsworn ladder,
kept). The answer then takes one of six shapes, first match:
1. **Doubles** — 11, 22, 33, 44, 55, 66, 77, 88, 99, 100 (read as 00) — make the answer **extreme**:
   **yes, and** or **no, and**. Ten faces: a constant 10% surprise rate on every question.
2. Within 5 of the threshold — **yes, but** on threshold…threshold+4; **no, but** on threshold−5…threshold−1.
3. Otherwise plain **yes** or **no**.

**T-01-10 Oracle odds (canonical: `resolution.yaml#oracle`; `oracle01.py`).** Faces per 100.

| Rung | Yes on | yes-and | yes | yes-but | no-but | no | no-and | total yes |
|---|---|---|---|---|---|---|---|---|
| Certain | no roll | — | always | — | — | — | — | 100 |
| Likely | 26+ | 8 | 62 | 5 | 4 | 19 | 2 | 75 |
| Even | 51+ | 6 | 40 | 4 | 5 | 41 | 4 | 50 |
| Unlikely | 76+ | 4 | 17 | 4 | 5 | 64 | 6 | 25 |
| Remote | 91+ | 2 | 3 | 5 | 4 | 78 | 8 | 10 |
| Impossible | no roll | — | — | — | — | always | — | 0 |

**01.15.4 What each answer means.** `[J:enum]` + `[D]`
- **yes, and** — true in its strongest form, plus one additional fact the engine rolls from ch.12's
  meaning table (`roll_table(tbl.meaning)`); the DM interprets the rolled words, never invents them.
- **yes** — true as asked.
- **yes, but** — true with one limitation, chosen `[J:enum]` from: *lesser* (smaller, fewer, weaker than
  hoped), *costly* (usable only at a price: guarded, owned, damaged), *elsewhere* (not here and now:
  nearby, a beat or some time away), *noticed* (using it will draw attention). Default: *lesser*.
- **no, but** — false, but one of `[J:enum]`: *substitute* (a weaker thing that partly serves), *trace*
  (it was here: a sign of where it went), *adjacent* (something else of use nearby). Default: *trace*.
- **no** — false; the DM says in the same breath what *is* there (P16).
- **no, and** — false and strongly so: the opposite is true, or a complication comes with the absence;
  the engine rolls the "and" from ch.12's meaning table.
The chosen qualifier is written as its own fact with the answer. *Worst case (J):* a less apt qualifier —
the qualifier's kind is fixed by the roll, only its form is chosen (class i). [R5 P-03 (six-way answer
shape); R: https://ironsworn-rpg.fandom.com/wiki/Ask_the_Oracle]

**01.15.5 Recording and "no" never ends at a wall.** `[D]` The answer is written as a fact (`set_fact`,
`source: oracle`) before it is narrated; the question, its odds rung, the d100 and the shape go to the
oracle log. A "no" is always followed by what *is* there, drawn from state or from the no-but qualifier.

**01.15.6 The sealed Oracle.** `[D]` When the answer is something the character must *discover* (does
this study hide a compartment?), the engine writes the answer as a **sealed** fact whose gate is
discovery; the player does not see the d100 or the answer. The search that follows is a secret frame
(01.4.7). When no secret exists, a successful search reports "nothing hidden here" with the same
confidence as a failed one reports nothing — the fiction does not distinguish them, and a second search
rides on the first.

**01.15.7 Never re-ask.** `[D]` + `[J:flag]` Every answer is keyed (`fact_key`: subject + predicate +
time scope). The engine refuses a question whose key already has an established answer. Rephrasing is
the same question (`[J:flag]` *"Would a yes to the new question contradict or restate an existing
answer?"* true → same key; uncertain → same key). A question whose answer follows from an existing
answer is read, not rolled. Only a fact with a time scope (is the guard at the gate *this watch*?)
may be asked again, and only once its scope has passed. A player fishing ("a ballista? a dragon
egg?") gets odds from the scene, so absurd fishing lands on Remote or Impossible, and every yes is a
fact the world keeps — the world fills in consistently instead of bending. *Worst case (J):* a new question
is judged a re-ask and read from the existing answer (the player is told which fact settles it and may ask
something else), or a rephrased re-ask is rolled while the engine still refuses an identical key
(class iv). [integration: 00.2.3 audit] [R7 §6; 00.12.7]

**01.15.8 Oracle facts and levers.** `[D]` An Oracle answer to a question asked *before* a declaration
is an established fact and may be a lever for that declaration. An answer to a question *embedded in* a
declaration may make the method possible (the rope exists, so the swing has something to swing on) but
is not a lever for that same beat; it may be one from the next beat on (00.3.9a).

### 01.16 Fate

**01.16.1 The pool.** `[D]` `fate` is the ruleset's only player-spendable luck currency (00.17.1 Q9): an
integer quantity 0–3 on the PC (`fate {current, max: 3}`), shown in the codex. A new PC starts with
**1**. Gains beyond 3 are lost. Fate is never a cost-menu target and never drained by effects.

**01.16.2 Earning fate.** `[T]` + `[D]` Only these engine-raised triggers add fate (closed list):
- **Hard luck** — a committed frame in which the PC is the actor, at Risky or Dire stakes, results in a
  **critical failure**: +1, at most once per scene, and hard luck never raises fate above **2**.
- **A thread completed** — a thread in ch.11's register that the PC pursued reaches status
  `completed`: +1.
- **A vow kept** — a commitment of kind vow or oath (ch.04/11) is fulfilled: +1.
Deeds (threads and vows) are the only way to reach 3. Rationale: fate is a comeback valve for bad luck
(Ironsworn momentum's shape, R5 P-15) and a reward for finished stories (great deeds, R6 C-R3 item 6),
never for rhetoric; hard luck's cap of 2 keeps the reprieve at the brink scarce. [DL-01-06]

**01.16.3 Spending fate in resolution: the reroll.** `[D]` During `on_roll` of a check whose d20 the
player has seen — one the PC makes, or one an adversary makes against the PC — the player may spend 1
fate to have the engine **reroll** that d20; the second die stands. At most one fate per roll. Not
allowed on: secret frames (the die is unseen), Oracle rolls (world facts are not the character's luck),
table rolls, generator draws, fortune checks the PC is not part of. Fate buys luck, never facts,
licenses, degrees or cancelled costs. *Arithmetic:* a reroll of a non-success turns 40% into 64% at +2 vs
Moderate, and 30% into 51% at +5 vs Hard (`fate01.py`).

**01.16.4 The interface to ch.07.** `[D]` `spend_fate(n) → bool`: if `fate.current ≥ n`, subtract n and
return true; else change nothing and return false. Ch.07's last-chance menu consumes it: an option in
`last_chance.yaml` with `fate_cost: n` (1…3, ch.07's choice) is available only while `fate.current ≥ n`.
Fate at 0 is itself a telegraph, and the OFFER of every lethal frame shows the current fate.

### 01.17 Traits: the general rules a trait tag pulls in

**01.17.1 How traits work.** `[D]` + `[J:flag]` A `trait.*` tag on a beat, ability, effect or item pulls
in a general rule automatically, so an improvised action inherits the right rules without anyone
remembering them (PF2e's attack/manipulate/move/concentrate traits) [R7 §2.9, §3.4 property 5;
R4 SG-11]. A beat's traits come from its anchor card; the DM adds one only when that trait's "true only
when" line holds (`[J:flag]`, uncertain → add it for sense traits, which cost the actor; omit it for
others). Ch.03 owns the tag definitions; this rule owns what each pulls in. Numbers owned elsewhere are
named. *Worst case (J):* a trait wrongly added or omitted pulls in, or leaves out, one general rule for one beat
(a loud tick, a provoked reaction); the tie-break adds sense traits, which cost the actor (class i). [integration: 00.2.3 audit]

**T-01-13 Trait rules.**

| Trait | True only when | Pulls in |
|---|---|---|
| `trait.action.attack` | the beat aims to harm or hinder a target against its will | the target's defense (01.6.4); `on_check_against` reactions (06); the repeated-attempt window (01.14.3); starting a conflict if none runs (06); witnesses may record a hostile act (03, 15) |
| `trait.action.manipulate` | the beat uses the hands on an object | needs a free hand; forbidden while `cond.grabbed` holds that arm or while `cond.pinned`/`restrained` (06); in conflict may provoke reactions from engaged foes (06) |
| `trait.action.move` | the beat changes the actor's position | forbidden by `cond.restrained`, `pinned`, `frozen`; `slowed` limits bands (06); may provoke reactions (06); changes range bands and flags via `set_position` (`on_move`) |
| `trait.action.concentrate` | the beat or effect needs sustained attention | cannot share an action with another beat; a sustained effect ends if the actor is `stunned` or `unconscious`; on harm, an Endure (Resolve) check vs the tier matching the harm's severity (S1–S2 Easy, S3 Moderate, S4 Hard, S5 Very hard) keeps it (ch.05 may give abilities their own DCs) |
| `trait.action.speech` | the beat needs speaking | forbidden while `cond.choking` or silenced; implies `trait.sense.audible` |
| `trait.sense.visible` | the act can be seen | perceived by anyone with line of sight; removes `flag.hidden` unless the beat is a Sneak |
| `trait.sense.audible` | the act makes ordinary sound | heard within `band.near` or the same room; ticks clocks listing it; not through walls |
| `trait.sense.loud` | breaking, smashing, shouting, metal on metal, a heavy fall, an explosion | heard at `band.distant` or through a site area; a method consequence whatever the degree; ticks every clock listing it; removes `flag.hidden` |
| `trait.sense.scent` | the act leaves a smell (blood, smoke, a strong perfume) | writes a trail fact; trackers following it gain a Precision lever (10) |
| `trait.delivery.touch` | the effect needs contact | needs `band.engaged` and an aimed roll against Agility defense unless the target is willing or helpless |
| `trait.delivery.melee` / `.ranged` / `.area` / `.aura` / `.line` | per ch.06's definitions | range bands, cover snags, multi-target selection over relationship-state (06) |
| `trait.nature.magical` | the effect is magic | sensed by magic-sensing licenses; warded and dispelled (05); inert where the region's canon forbids magic (12.16.5) |
| `trait.nature.sacred` / `.profane` | holy / unholy power | keys resistances and vulnerabilities by `creature.*` tags (09) |
| `trait.nature.mental` | the effect acts on a mind | targets resist with Resolve; mindless entities (`creature.undead.mindless`, `creature.construct`) are unaffected → G4 for that intent |
| `trait.nature.illusion` | a false sensation | a target who interacts with it physically, or is told with cause, may Observe (Wits) against the effect DC to disbelieve; success ends it for that target |
| `trait.duration.instant` / `.sustained` / `.lasting` / `.permanent` | how long the result lasts | instant: resolves and ends; sustained: implies concentrate; lasting: carries a duration form (substrate); permanent: until removed by a named means |

### 01.18 The basic-verb anchor cards

**01.18.1 What a verb card is.** `[D]` Each of the fifteen basic verbs (00.12.5; ids, coverage and
attributes fixed by 00) carries an **anchor card**: the 00.2.6 anchor standard filled in — intent verbs,
knobs with defaults and allowed deltas (T-00-20), a degree table for all five results, scope and
exclusions, traits, method consequences, the defense a target uses (`against`), and a distinguishing
test against each confusable neighbor (SG-16). The cards are canonical in `data/basic_verbs.yaml`
(`anchor:` fields, written by this chapter) and compiled by ch.12 into `data/anchors.yaml`. They are the
spine of the reach-and-adapt substrate: when an action matches no rule, the DM reaches for the nearest
card and moves at most two knobs (01.5.3). Every card is `Anchor: yes`; every card is composable as a beat
in a sequence and as a tick source for a clock (anchor property 7).

**01.18.2 The generic degree table.** `[D]` Every card's degree table specializes this one; a card lists
only where it differs.

| Result | Generic reading |
|---|---|
| critical success | delivered reach = framed + 1 (the card's reach ladder one rung up); overflow → follow-up Precision lever (01.9.1) |
| success | delivered reach = framed |
| near miss | the player may take success at framed reach with one cost at S1/S2/S3 (Safe/Risky/Dire), threatened or alternate |
| failure | delivered reach 0; the threatened cost at S2 (Risky) / S3 (Dire); nothing if Safe |
| critical failure | delivered reach 0; the threatened cost one rung heavier (S1 / S3 / S4) and the card's critical-failure effect, if any |

**01.18.3 Resisted effects (Endure, Evade) read the source's severity.** `[D]` When a beat resists a
sourced effect (a poison, a falling rock, a dragon's fear, a trap's blade), the effect's own severity sets
the frame's stakes (S1–S2 → Risky; S3+ → Dire) and its threatened cost is the effect itself: **critical
success** — no effect, plus a follow-up Precision lever (you shook it off and saw your opening);
**success** — no effect (or the source's declared `on_success`, e.g. a reduced stage); **near miss** —
success at a cost: no effect, one cost at the stakes' near-miss severity from a *different* menu entry
(footing, time, drain); **failure** — the effect at its declared severity; **critical failure** — the
effect one severity rung heavier. Sources that declare their own staged table (ch.07 afflictions, ch.10
hazards and traps, ch.05 spells) replace this default. A resisted-effect frame the actor did not choose
is recorded with `beat.declared: false` (00.13.1), which ch.03 reads (03.3, decision D3) and which bars a
Focus push (05.6.7) [integration: IR ch.03 to 01].

**T-01-11 The fifteen anchor cards.** In each card: *Intent verbs* (what retrieves it) · *Covers / Does
not cover* (from 00; exclusions name the license) · *Attribute* (default, then alternatives by method) ·
*Against* (the defense a creature target uses; tier for objects) · *Reach ladder* (what delivered reach
1/2/3/4 means) · *Degrees* (only differences from 01.18.2) · *Knobs* (default → allowed deltas) ·
*Traits / consequences* · *Distinguish*.

**01.18.4 `verb.move` — Move.** *Intent verbs:* reposition, get past, dash, withdraw, slip through,
retreat, travel on foot. *Covers:* reposition, dash, withdraw, slip through a crowd, travel on foot,
retreat. *Does not cover:* flying, teleporting (a `slot.movement_mode` license). *Attribute:* Agility;
Might forcing a way through; Endurance for long hauls. *Against:* an entity blocking the way — the
higher of its Agility or Might defense; otherwise terrain tier (unopposed movement on passable ground is
Trivial). *Reach ladder:* 1 partway (one band or half the distance intended); 2 the intended position;
3 the position plus a favorable flag (`flag.in_cover`, `flag.elevated`) or without provoking a reaction;
4 as 3 plus a follow-up lever. *Degrees:* failure — the actor stays or stops partway (the threatened
cost, usually footing or exposure). *Knobs:* `dc` (tier → opposed when passing through a foe);
`attribute` (Agility → Might/Endurance); `action_cost` (06 default → +1 for dashing through difficult
ground); `targets` (one obstacle → a line of foes, each a snag); `time_cost`; `reach_unit` (bands →
place-graph steps). *Traits:* `trait.action.move`; loud when crashing through. *Consequences:* may
provoke reactions (06); Retreat's outcome is ch.07's. *Distinguish:* Move vs Exert — passable ground
(Move) or a climb, jump or swim (Exert); Move vs Evade — going where you choose (Move) or getting out of
the way of a specific threat (Evade).

**01.18.5 `verb.observe` — Observe.** *Intent verbs:* search, look for, study, listen, track, spot,
read a person, read a scene, appraise. *Covers:* search, study, listen, track by sight, read a person or
a scene. *Does not cover:* reading an unknown script (a language or training license); magical sight (a
license). *Attribute:* Wits; Intellect for sustained study of a thing. *Against:* a hiding entity — its
stored Sneak total; a person concealing a feeling or a lie — the higher of their Presence or Wits
defense (15 composes social DCs); an object or trail — its stored tier. *Reach ladder:* information
items by `deliver_count` (01.10.4); a single question delivers at reach ≥ 1. *Degrees:* failure — one
vague impression of the top-ranked item; critical failure — nothing reliable, plus the cost; a plausible
falsehood only when the observed source can mislead (a disguise, a forged trail). Frequently a secret
frame (01.4.7). *Knobs:* `dc` (stored/tier → opposed); `attribute` (Wits → Intellect);
`time_cost` (1 interval in site mode for a room → 1 hour for a building); `targets` (one thing → an area);
`reach_unit` (items → clock ticks when extended). *Traits:* none by default. *Consequences:* a thorough
search leaves traces (things moved) — a method consequence when the searched place is someone's.
*Distinguish:* Observe vs Recall — the answer is in front of you (Observe) or in your head (Recall);
Observe vs passive noticing — casual looking is free and only compares notice to concealment (01.4.6).

**01.18.6 `verb.recall` — Recall.** *Intent verbs:* remember, know, recognize, recall. *Covers:* common
knowledge of one's origin, culture and trade. *Does not cover:* specialist lore (history, bestiary,
arcana, law, medicine at specialist depth) — a training license (`lic.training.*`) or origin lore
specialty. *Attribute:* Intellect. *Against:* tier by obscurity within common knowledge (Easy: widely
known in your culture; Moderate: known to people of your trade; Hard: the edge of common knowledge).
*Reach ladder:* items by `deliver_count`. *Degrees:* failure — a vague impression; critical failure — a
**plausible falsehood** by default (memory misleads; `misleadable: true`), small and correctable
(01.10.4). *Knobs:* `dc` (tier); `attribute` (Intellect → Wits for "what was that sound?" in-the-moment
recognition); `time_cost` (none → 1 interval with reference books, which are a Precision lever).
*Traits:* none. *Distinguish:* Recall vs free knowledge (01.3.8) — the character certainly knows
(free) or might misremember (Recall); Recall vs licensed lore — any adult from that background (Recall)
or a scholar (license).

**01.18.7 `verb.talk` — Talk.** *Intent verbs:* persuade, convince, deceive, lie, intimidate,
threaten, bargain, haggle, taunt, provoke, perform, inform, ask, surrender, yield. *Covers:* inform,
persuade, deceive, intimidate, bargain, taunt, perform, yield. *Does not cover:* speaking a language not
held (a language license; crude fallback: gesture, tone and shared nouns, DC +5, reach Limited).
*Attribute:* Presence; Intellect for a reasoned argument; Might for physical menace. *Against:* the
listener's defense — Resolve against persuasion, intimidation and taunts; Wits against deception —
composed by ch.15 with standing and claim plausibility (doubtful claim: a snag; outrageous: reach
Limited; known false to the listener: G4 for the belief intent). *Reach ladder:* 1 a small concession or
one standing step; 2 the listener does the reasonable thing asked; 3 more than asked (volunteers help,
information, a favor); 4 as 3 plus a follow-up lever. *Degrees:* failure — the listener says no (a "No"
is always a legitimate outcome, W4) and the threatened cost, usually `cost.closed_door`; critical failure
— closed door one rung heavier (at S3: standing −1). An NPC's pre-committed refusals (15) are G4 for that
intent unless a fact removes them. *Knobs:* `dc` (opposed → tier for a crowd's mood); `attribute`
(Presence → Intellect/Might); `targets` (one listener → a crowd: scale factor, reach Limited unless a
lever); `time_cost` (a few words → a scene of negotiation: extended, a tug clock); `reach_unit`
(standing/action → clock ticks). *Traits:* `trait.action.speech`, `trait.sense.audible`; loud when
shouted. *Consequences:* a lie that succeeds leaves a commitment in the world (someone now believes it,
WE-01-2). *Distinguish:* Talk vs Setup-by-words — seeking the listener's decision (Talk) or a moment's
distraction to exploit (Setup); deceive (Talk) vs Sneak — making them believe something false, or
making them not notice.

**01.18.8 `verb.strike` — Strike.** *Intent verbs:* hit, attack, stab, cut, shoot, throw at, punch,
bash, cut down, knock out. *Covers:* hit with body, weapon or improvised object; shoot; throw. *Does not
cover:* weapon techniques (ability licenses). *Attribute:* Might; Agility for finesse, aimed and thrown.
*Against:* the target's attack defense (ch.06; default Agility defense); an object — tier by size and
distance (a rope at range: Hard; a door: Easy but its reach unit is object state, and breaking belongs
to Force). *Reach ladder (harm):* the weapon's base severity (08; unarmed S1; an improvised object uses
the stats of the weapon it most resembles, else S1) shifted by (delivered reach − 2): 1 → −1 step,
2 → base, 3 → +1, 4 → +2 (00.3.15; ch.07 applies). *Degrees:* failure — a miss (in conflict usually Safe:
the foe's ordinary turn is its own frame); critical failure — the threatened cost one rung heavier, often
footing or gear. *Knobs:* `harm_severity` (weapon base → improvised-by-resemblance → a hazard's severity
when the strike drops something on the target); `harm_tags` (weapon's → the hazard's); `dc` (defense →
object tier); `targets` (one → the object whose falling hits the one beneath it); `reach_unit` (harm →
object state, e.g. rope cut); `action_cost`. *Traits:* `trait.action.attack`, `trait.delivery.melee` or
`.ranged`; audible, loud with metal on metal. *Consequences:* the repeated-attempt window (01.14.3);
ammunition used. *Distinguish:* Strike vs Force — harm (Strike) or position/object state (Force); an
effect *beyond* harm (pin, disarm, trip) is not a free rider on a Strike — it is Force, Grapple or Setup,
or a Great-reach clause the anchor's knob change must declare (Feng Shui's line, R7 §2.21).

**01.18.9 `verb.grapple` — Grapple.** *Intent verbs:* grab, seize, hold, wrestle, pin, restrain,
snatch, tackle-and-hold, climb onto (a large creature), break free. *Covers:* seize, hold, pin,
restrain, snatch a held item, mount a large creature; breaking or slipping a hold. *Does not cover:* —.
*Attribute:* Might; Agility to slip or break a hold. *Against:* the higher of the target's Might or
Agility defense; to break a hold, the holder's Might defense. *Reach ladder (condition):* 1
`cond.grabbed` (S1) — the target is held but may still act; 2 `cond.grabbed` (S2); 3 `cond.restrained`;
4 `cond.pinned`. Snatching an item: reach ≥ 2 takes it; 1 knocks it loose (it falls). Mounting a large
creature: reach ≥ 2 = `flag.mounted` on it (06). *Degrees:* failure — no hold; the threatened cost is
usually footing (the target shrugs you off). *Knobs:* `condition` (grabbed → restrained/pinned per
ladder; → `cond.choking` only with a method that chokes); `dc`; `attribute`; `targets` (one → a large
creature: scale factor, reach Limited unless levers); `duration` (until the holder lets go or the target
breaks free). *Traits:* `trait.action.attack`, `trait.delivery.touch`. *Distinguish:* Grapple vs Force
— the actor keeps hold (Grapple) or the target is moved away or down (Force).

**01.18.10 `verb.force` — Force.** *Intent verbs:* shove, push, trip, topple, knock over, break, smash,
burst, pry, bend, lift a bar off. *Covers:* shove, trip, topple, break, burst, pry. *Does not cover:*
picking a lock (`lic.training.guile_thievery`). *Attribute:* Might. *Against:* a creature — the
higher of its Might or Agility defense; an object — its stored tier by hardness and make. *Reach ladder:*
creature: 1 `cond.off_balance`; 2 pushed one band **or** `cond.prone`; 3 pushed two bands, or prone and
off-balance; 4 as 3 plus a follow-up lever. Object: 1 weakened (the next Force against it gains a
Precision lever); 2 broken, burst or open; 3 open and usable (the door still swings, the chest's contents
unspilled); 4 as 3 plus a follow-up lever. *Degrees:* failure — it holds; critical failure — the heavier
cost, often gear (the bar snaps) or footing. *Knobs:* `dc` (opposed → tier); `condition` (off_balance →
prone); `targets`; `time_cost` (one action → an interval of prying for Hard objects); `reach_unit`
(bands/condition → object state). *Traits:* breaking is `trait.sense.loud` (a method consequence
whatever the degree). *Consequences:* a broken thing stays broken (a fact). *Distinguish:* Force vs
Handle — overcoming the object's resistance (Force) or using it as it is meant to be used (Handle).

**01.18.11 `verb.exert` — Exert.** *Intent verbs:* climb, jump, leap, vault, swim, lift, carry, haul,
balance, run far, hold (a door shut), push through (a current). *Covers:* climb, jump, swim, lift,
balance, run far. *Does not cover:* —. *Attribute:* Might; Agility for balance or a precise leap;
Endurance for sustained effort. *Against:* tier, stored per obstacle and anchor (a wall climbed and the
same wall vaulted are two stored DCs). *Reach ladder:* 1 partway (half the height, a ledge, the near
bank's shallows); 2 the whole distance; 3 the whole distance with time saved or a favorable position;
4 as 3 plus a follow-up lever. *Degrees:* failure on a climb or jump — the actor does not get there;
the threatened cost is usually harm from the height or footing (a slide back). *Knobs:* `dc` (tier →
re-derived tier for a tool-changed obstacle, e.g. a pole vault); `attribute`; `time_cost` (1 action →
rounds per 10 ft for long climbs, ch.10); `stakes` (height source → current, cold water); `reach_unit`
(distance → clock ticks for long climbs, swims and runs). *Traits:* none by default; audible when heavy.
*Distinguish:* Exert vs Endure — acting on the world in a burst (Exert) or holding out against it
(Endure); Exert vs Force — the body's own movement or burden (Exert) or defeating an object's resistance
(Force).

**01.18.12 `verb.evade` — Evade.** *Intent verbs:* dodge, duck, dive clear, take cover, get out of the
way, jump aside. *Covers:* dodge, duck, take cover, get clear of a hazard. *Does not cover:* —.
*Attribute:* Agility. *Against:* the effect DC of what is evaded (resisted effect, 01.18.3), or tier
for reaching cover under threat. *Reach ladder:* resisting — the 01.18.3 table; taking cover — 1 partial
cover (a Protective lever citing it next beat), 2 `flag.in_cover`, 3 cover plus a clear line of retreat
(two Protective facts), 4 as 3 plus a follow-up lever. *Knobs:* `dc` (effect DC → tier); `targets`
(self → self and one adjacent ally, a knob change); `time_cost`; `stakes` (the effect's severity).
*Traits:* `trait.action.move`. *Distinguish:* Evade vs Endure — getting out of the way (Evade) or taking
it and holding out (Endure); for any effect the test is 00.3.3 and the effect's own `resist` field.

**01.18.13 `verb.sneak` — Sneak.** *Intent verbs:* hide, sneak, creep, slip past unseen, conceal,
palm, shadow, lift from a pocket. *Covers:* hide, move quietly, conceal an object, palm. *Does not cover:*
disguise as a specific person (a license). *Attribute:* Agility; Wits for blending into a crowd or picking
the moment. *Against:* the highest notice (Wits defense, 01.4.6) among observers who could perceive the
actor; with no observer and no listening clock, the beat is not costly (01.4.1) and needs no roll. Lifting
from a pocket is against the victim's notice. *Reach ladder:* 1 unnoticed for part of the stretch (the
ride ends halfway); 2 unnoticed for the whole stretch intended (one ride covers it); 3 unnoticed and in
position (`flag.hidden` at the chosen spot — a Precision lever for an ambush or a lift); 4 as 3 plus a
follow-up lever. *Degrees:* failure — the threatened cost, almost always `cost.exposure`. *Knobs:* `dc`
(opposed notice); `attribute`; `targets` (one watcher → a watched area: the highest notice); `time_cost`;
`reach_unit` (stretch → clock ticks against an alarm, when extended). *Traits:* none (a Sneak is the
absence of sense traits; a noisy method adds `audible`). *Distinguish:* Sneak vs Talk-deceive (above);
Sneak vs Observe — avoiding notice (Sneak) or gaining it (Observe).

**01.18.14 `verb.handle` — Handle.** *Intent verbs:* use, operate, light, tie, rig, patch, mend,
bandage, stabilize, calm (an animal), lead, ride, cook, improvise a tool. *Covers:* use an object as its
nature suggests; crude making and repair; first aid (stabilize only); calm or lead an animal; ride.
*Does not cover:* surgery (a medicine license); smithing and fine crafts (a craft license); lockpicking (a
training license); mounted combat (a license). *Attribute:* Agility; Wits for improvised use; Intellect for
knowledge-driven use; Presence for animals; the license's attribute for a small working of magic (05.7.6:
the school's casting attribute) [integration: IR ch.05 to 01]. *Against:* objects — tier; an animal — its Resolve defense
composed with its disposition (15); a dying character — ch.07's stabilize DC. *Reach ladder:* 1 works
partly or briefly (a knot that holds for one use; a horse calmed but skittish); 2 works as intended;
3 works well (holds for the scene; the horse follows willingly); 4 as 3 plus a follow-up lever. Crude
repair removes `damaged`, never `broken`. *Knobs:* `dc`; `attribute`; `time_cost` (1 action → 1 interval
for a crude repair); `duration` (how long the rig holds). *Traits:* `trait.action.manipulate`.
*Distinguish:* Handle vs Force (above); Handle vs a craft license — a result anyone could cobble
together (Handle) or a made thing needing skill (license; crude fallback for most crafts is Handle with
reach Limited).

**01.18.15 `verb.endure` — Endure.** *Intent verbs:* resist, withstand, bear, hold breath, push on,
stay awake, keep going, shake off. *Covers:* resist cold, poison, disease, fear, pain; hold breath; keep
going. *Does not cover:* —. *Attribute:* Endurance; Resolve for fear, pain, temptation, domination.
*Against:* the effect DC (resisted effect, 01.18.3); a hazard's tier by severity. *Reach ladder:* the
01.18.3 table; for "keep going" beats against exhaustion, delivered reach = hours or watches pushed
beyond the limit (ch.07/10). *Knobs:* `attribute` (Endurance ↔ Resolve by what is under strain);
`dc` (effect DC → hazard tier); `duration`; `stakes` (the source's severity). *Traits:* none (mental
strain carries `trait.nature.mental` from its source). *Distinguish:* Endure vs Evade (above); Endure vs
Exert (above).

**01.18.16 `verb.setup` — Setup.** *Intent verbs:* feint, distract, create an opening, blind, prepare,
lure, bait, grease, rig a trap, set an ambush. *Covers:* create a lever for yourself or an ally.
*Attribute:* by method (the method's own attribute: a feint is Agility, a distracting story Presence, a
prepared snare Wits). *Against:* a creature — its defense by the method (feint vs Wits; blinding throw vs
Agility); the environment — tier. *Reach ladder:* one lever fact; critical success — two uses (01.14.9).
*Degrees:* critical failure — the target is forewarned (a snag fact on the follow-up) plus the heavier
cost. *Knobs:* `condition` (none → distracted, off_balance, exposed, blinded by a suitable method);
`duration` (next turn / scene); `dc`; `targets` (one → a group, a knob change and scale). *Traits:* per
method (`attack` if it hinders a creature against its will). *Distinguish:* Setup vs Help — creating a
fact in the world (Setup) or lending your effort directly to another's roll (Help).

**01.18.17 `verb.help` — Help.** *Intent verbs:* help, assist, steady, back up, boost, cover (for).
*Covers:* give a Precision lever to another's attempt, only if the helper could attempt it alone.
*Attribute:* by method (only if the help itself rolls). *Reach ladder:* one Precision lever (never more
than one Help lever per beat). *Knobs:* `action_cost`; `time_cost`. *Details:* 01.14.8.
*Distinguish:* Help vs group action (01.14.7) — Help assists one roll; a group action is one roll for
several actors.

**01.18.18 `verb.ready` — Ready.** *Intent verbs:* wait for, hold, cover (a door), be ready to, when X
then Y. *Covers:* hold an action for a stated trigger. *Does not cover:* reactions beyond ch.06's (an
ability). *Attribute:* none at readying; the readied beat's own when it fires. *Reach ladder:* none (the
readied beat has its own). *Knobs:* `action_cost`; `duration` (until the window ends). *Details:*
01.14.10. *Distinguish:* Ready vs a conditional declaration — Ready waits for an observable event; a
conditional (01.14.4) depends on a fact or result.

**01.18.19 Yield and Retreat.** `[D]` Yield (a Talk that surrenders on terms) and Retreat (a Move that
withdraws from a conflict) are always legal named uses (00.12.5); they are G1 with no license. Their
outcomes are ch.07's; resolution frames them only when ch.07 says their acceptance or escape is
uncertain.

---

## Procedures

**PR-01-1 The resolution pipeline (the DM's per-beat checklist).** `[D]` + `[J]` as marked in each rule.
1. **PARSE** (01.2): split intent / method / assertion; queue embedded fact-questions to the Oracle;
   split beats (≤ 3 resolved per declaration); classify each beat's shape; resolve the target; ask at
   most one clarifying question or state the assumed reading; write the neutral restatement.
2. **GATE** (01.3): G0 → PR-01-4 or answer from state; G4 tests; G1 (verb covers, not excludes,
   sensitive-upgrade test false); G2 (cite a held license id; mode normal/stretch/emulate); else G3 →
   PR-01-5. Split partly-licensed beats (01.3.4).
3. **NECESSITY** (01.4): Trivial? free activity? riding? Good Idea? take the time? certain with cost?
   Otherwise roll. Tie → roll.
4. **ANCHOR** (01.5): `find_rulings` first (INV-19); pick the anchor from ≤ 8 candidates; at most two
   knob changes, each citing a fact; else re-anchor or split.
5. **FRAME** (01.6): attribute (lower on a tie); primary deed tag; traits (loud?); obstacle id; DC
   source; levers and snags with fact ids; stakes flags → rung; lethal flag; reach flags → rung;
   threatened and alternate cost; method consequences; secret? Then `frame_check` (PR-01-2).
6. **OFFER** (01.7): show the frame; the player commits, changes (→ step 1), withdraws, or makes one
   trade (go big / play it safe → re-run `frame_check`).
7. **ROLL** (01.8): `roll_check`; `on_roll` (fate reroll, ability rerolls); degree by the step rule;
   near miss.
8. **READ** (01.9): delivered reach (T-01-4); if near miss, the player chooses failure or success at a
   cost; cost severity (T-01-5).
9. **DELIVER** (01.10): for bundled beats, `deliver(frame, ranked items)` → count; choose permitted
   content per item.
10. **CONSEQUENCE** (01.11): apply the one due cost's form at its severity (`apply_costs`); apply method
    consequences; check that a next step exists.
11. **RECORD** (01.12): state writes → stored DC → ride → evidence → ruling → `mark_boundary(beat_end)`;
    then narrate from the store.

**PR-01-2 `frame_check` validation.** `[D]` (engine; refusal names the failed step)
1. Beat has actor, resolved target id, intent, method, shape.
2. Gate: G1 verb id exists and its covers include the recorded method class; or G2 license id held,
   unexpired, not restricted; or G3 with an accepted `crude_fallback`; mode prices read from the entry.
3. Anchor id exists; deltas ≤ 2, each knob in the anchor's allowed deltas with a cited fact.
4. Attribute allowed by the anchor (or a declared `attribute` delta).
5. Primary deed tag exists in `tags.yaml`; competence lookup (PR-00-1 step 2).
6. Obstacle id exists; DC by 01.6.4 (write a new stored DC when tiered); mode `dc_shift` added.
7. Each lever/snag: fact exists; `established_at` earlier than the declaration (or created by an earlier
   beat); not already used as a lever on this beat; ≤ 2 cited levers, ≤ 2 cited snags; engine repetition
   snags added (01.14.3); Precision sum clamped ±4.
8. Stakes rung set; Protective steps and the trade applied, clamped; `lethal` true only if Dire and
   `lethal_context` was recorded before the declaration.
9. Reach rung set; Amplifying steps, effect steps (±2), trade applied, clamped Limited…Great.
10. Threatened cost (and alternate on Risky/Dire) are menu ids whose `fits_when` cites a fact.
11. Modifier: sum of the five families, clamped −8…+16, PC base ≤ +12.
12. Odds: enumerate d20 faces 1–20 with 01.8.1; store success-or-better, critical success, critical
    failure, near-miss %; flag "natural 20 only" when `20 + total < DC`.
13. Return the frame, or the refusal.

**PR-01-3 Roll → read → deliver → costs.** `[D]`
1. `roll_check(frame_id)`: refuse unless the frame is committed (offer choice commit, or auto under
   01.7.4). Roll d20 with RC-RNG; fire `on_roll` (fate reroll 01.16.3); compute total, margin, degree
   (01.8.1), near miss (01.8.2); fire `on_degree`.
2. `read_result(frame_id, take_success_at_cost)`: if near miss, record the player's choice; delivered
   reach per T-01-4 (overflow → momentum fact); cost severity per T-01-5 (or the near-miss column).
3. `deliver(frame_id, ranked_items)`: bundled beats only; `deliver_count(N, delivered_reach)`; vague
   impression on failure; plausible falsehood on critical failure when `misleadable`.
4. `apply_costs(frame_id, [{menu_id, form}])`: validate the menu id is the threatened or (for
   success-at-cost) the alternate, the form belongs to that entry at that severity, and the cost can land
   in full; apply the entry's writes; else refuse, and the DM uses 01.13.1's next candidate.
5. Apply method consequences; write the ride record; emit evidence; log the ruling; `mark_boundary(beat_end)`.

**PR-01-4 Asking the Oracle.** `[D]` + `[J:rung]`
1. Is there an established fact, canon or scene-type answer? → read it (Certain / Impossible); stop.
2. Is an actor actively attempting it? → a fortune check (01.6.7); stop.
3. Write the question as a `fact_key`; refuse if the key (or an equivalent) is already answered (01.15.7).
4. `find_rulings(oracle)` for a matching precedent (same kind of question in the same kind of place).
5. Choose the odds rung (01.15.2) and log it before rolling; ch.12 may shift one rung.
6. `oracle(question, rung, fact_key, sealed?)` → d100 → shape (T-01-10).
7. For yes-and / no-and: `roll_table(tbl.meaning)` for the "and". For yes-but / no-but: choose the
   qualifier from its closed list.
8. `set_fact` (sealed if a discovery question); then narrate; a "no" is followed by what is there.

**PR-01-5 A G3 redirect.** `[D]` + `[N]`
1. Identify the license that would cover the method (data lookup by deed tags and scope); if none
   exists, the deed branch and a `rule_conflict` ruling (01.3.5).
2. Read its `crude_fallback` and `acquisition_paths`.
3. Speak the four-part redirect (01.3.6); nothing is spent.
4. If the player accepts the fallback: PARSE a new beat on the fallback verb with `mode: fallback`,
   the `dc_shift`, `reach_cap` and listed consequence carried into FRAME.
5. Log the ruling (`kind: g3_redirect`).

**PR-01-6 Running an extended action.** `[D]`
1. Name the clock for the obstacle; size from template or 00.8.3; set the tick interval and optional
   `requires_varied_approach`; store the obstacle's DC.
2. Each interval: at most one progress beat (a ride otherwise); frame it (the DC is the clock's);
   ticks = delivered reach; costs per READ.
3. Racing or danger clocks tick from their own sources (costs, consequences, auto-ticks).
4. On completion: `on_complete` effects write the result; void a racing clock (00.8.5).

---

## Tables

Canonical data: **`data/resolution.yaml`** (all resolution tables), **`data/basic_verbs.yaml`**
(`anchor:` fields of the fifteen verbs), and the ch.01-owned values in **`data/scales.yaml`**
(`degrees`, `obstacle_tiers`, `stakes.critical_failure_step`, `oracle_odds`, `resources.fate`). The data
files win over any paraphrase (00.1.4 item 5).

| Table | Content | Where |
|---|---|---|
| T-01-1 | The pipeline: steps, kinds, outputs | 01.1.1 |
| T-01-2 | Obstacle tiers: DCs, anchors, two examples per rung | 01.6.5; `resolution.yaml#dc_tiers` |
| T-01-3 | Degree distribution −2…+16 × five DCs, with the CT-1…CT-6 proof | 01.8; `odds01.py` |
| T-01-4 | Degree → delivered reach | 01.9.1; `#read_delivery` |
| T-01-5 | Stakes × degree → cost severity | 01.9.2; `#read_costs` |
| T-01-6 | `deliver_count(N, reach)` | 01.10.4; `#delivery_counts` |
| T-01-7 | The cost menu: fits-when, forms per severity, writes | 01.13; `#cost_menu` |
| T-01-8 | Sequential-beat feeding | 01.14.1; `#sequential` |
| T-01-9 | Time cost by mode | 01.13.5; `#time_cost` |
| T-01-10 | Oracle odds and answer shapes | 01.15.3; `#oracle` |
| T-01-11 | The fifteen verb anchor cards | 01.18; `basic_verbs.yaml` |
| T-01-12 | Repetition, group, help, setup constants | 01.14; `#repetition`, `#group`, `#help`, `#setup` |
| T-01-13 | Trait rules | 01.17; `#traits` |
| T-01-14 | Fate: start, cap, earn, spend | 01.16; `#fate` |

**T-01-12 Constants.** Repetition snags per k-th instance in a window: 0, −2, −4 (engine Precision
snags, outside the two-snag count, inside the ±4 cap). Help: one Precision lever, at most one per beat.
Setup uses: 1 on success, 2 on a critical success. Group: all-must → lowest base modifier; any-may →
highest. Beats resolved per declaration: 3. Bundle size after deduplication: 1–5. Near-miss band: margin
−3…−1 on a failure, plus a natural 1 that stepped a success down. Take-the-time multiplier: ×2 time, not
for Very hard or Legendary tiers. Critical-failure cost step: +1 rung. Oracle "but" band: 5 faces each
side of the threshold; doubles: 10 faces.

**T-01-14 Fate.** Start 1; cap 3; hard luck (critical failure on the PC's Risky/Dire frame) +1 once per
scene, never above 2; thread completed +1; vow kept +1; reroll 1 fate (one per roll; not on secret,
Oracle, table, generator or others' fortune rolls); `spend_fate(n)` for ch.07's last-chance options.

---

## Worked examples

Wren's sheet is 00's (Might +1, Agility +3, Endurance +1, Wits +2, Intellect 0, Presence 0, Resolve −1;
competence `deed` +1, `deed.wilds.tracking` +2, `deed.martial.archery` +2; Vitality 13; Focus 4; fate 1) [verification: V1-001].
Every odds figure is from exhaustive enumeration (T-01-3). Adversary, hazard, license and social numbers
are *(illustrative; ch.NN owns)*. WE-01-1…13 re-rule R7's thirteen examples through the final rules;
WE-01-14…20 add boundary pairs and tempting non-examples.

### WE-01-1 "I throw sand in its eyes, then slide under its legs."

*Scene (established):* a ruined courtyard ankle-deep in grit (`scene.courtyard.floor = grit`); a
10-ft ogre (`adv.ogre_02`, T3; Agility +0, Might +5, Wits −1, no relevant competence; *09 owns*) guards
the gate; Wren is engaged with it. The ogre archetype carries `lethal_context`, and the warning was given
when it smashed the cart (07).

- **PARSE.** Intent: reach the gate past the ogre. Two `sequential` beats: A — throw grit in its eyes;
  B — slide between its legs.
- **GATE.** A: `verb.setup` (G1); the grit is established, so no Oracle. B: `verb.move` through an
  enemy's space (G1).
- **NECESSITY.** Both uncertain and costly → roll.
- **ANCHOR.** A: the Setup card with one knob change, `condition: blinded` (a method that can blind:
  grit). B: the Move card, no deltas. `find_rulings` returns nothing.
- **FRAME A.** Agility +3 (a quick throw), competence floor +1 → +4. DC: the ogre's Agility defense
  10 + 0 = **10**. Levers: none — the grit is what the method uses, not a fact that improves it. Stakes:
  a missed throw leaves Wren where she already is; the ogre's club is its own turn (01.6.9 conflict
  clause) → **Safe**. Threatened cost (S1 on a critical failure): footing (`cond.off_balance`).
- **OFFER A.** "You need 6+ (75%; critical 25%)." Committed. **ROLL:** d20 = 12 → 16, margin +6 →
  **success**. `apply_condition(ogre_02, cond.blinded, until end of its next turn)`; the Setup fact
  `setup.wren.blind_ogre` (one use).
- **FRAME B.** Agility +3, floor +1. DC: the Move card's `against` — the higher of the ogre's Agility
  (10) and Might (10 + 5 = 15) defenses → **15**. Levers: `setup.wren.blind_ogre` (Precision +2) and
  `adv.ogre_02.size = large` — the gap between its legs (Precision +2) → circumstance +4 (the cap).
  Total **+8**. Stakes: failure leaves Wren on the ground under a T3 brute (armed, band ≥ hers,
  acting against her) → **Dire**. Threatened cost: footing (under its foot); alternate: gear (the spear).
  Lethal: the threatened cost is footing, not harm → **false**.
- **OFFER B.** "You need 7+ (70%; near miss 15%; critical failure 5%). Fail and you're under it — at
  worst pinned." **ROLL:** d20 = 4 → 12, margin −3 → **failure, near miss**. The player takes success at
  a cost, choosing the alternate: `cost.gear` at **S3** → the spear catches in its shin-strap and is
  wrenched free bent (`item.spear.condition = damaged`: its harm_edge does not apply until a crude
  repair). Wren ends behind the ogre, 20 ft from the gate.
  *Other branch:* d20 = 1 → 9, margin −6 → failure, natural 1 → **critical failure** → the threatened
  cost one rung heavier: `cost.footing` **S4** → `cond.pinned` under its foot.
- **CONSEQUENCE.** A blinded ogre bellows: the anchor's method consequence (`trait.sense.loud`) ticks the
  gatehouse's listening clock +1 and its omen is narrated. P16: the gate, its bar, and a blinded ogre.
- **RECORD.** Ruling `verb.setup+condition:blinded`; ride records for both beats; two actions (06).

*Why it is fair:* the idea paid twice, only through facts (the grit, the blindness, the ogre's size), and
hit the cap; three flowery paragraphs would have earned the same numbers.

### WE-01-2 "I convince the guard I'm his long-lost sister."

*Scene:* a bored gate guard, `npc.tam_harlan` (T2; Wits +1, Resolve +0, no social competence;
standing neutral). Wren wants into the keep.

- **PARSE.** Method: a lie (Talk, deceive). Intent unstated → "Taking that as: you want him to let you
  in." Embedded fact: does he have a long-lost sister? → queued to the Oracle.
- **ORACLE** (PR-01-4). Unestablished; no canon settles it. Odds from the world: most men have no
  vanished sister → **Unlikely (76+)**.
- **Branch A:** d100 = 41 → **no**. `set_fact(npc.tam_harlan.siblings = two brothers, no sister)`. The lie
  now contradicts an established fact the target knows → **G4 for the belief intent** (01.3.7 test 1). No
  roll, nothing spent. Redirect: "He grew up with two brothers and no sister. You could still play it as
  a drunk's joke to get him talking, or try another story." [integration: I-024] The player takes the joke and asks
  when the watch changes. **FRAME:** Talk-persuade: Presence 0 + floor 1 = **+1** vs Resolve defense
  10 + 0 = **10** (standing neutral adds nothing, *15 owns*). Stakes: his goodwill is spent by a flat
  joke → **Risky**; threatened `cost.closed_door`, alternate `cost.exposure`. OFFER: 9+ (60%). d20 = 9 →
  10 → **success** (a tie goes to the actor). He laughs and says the watch changes at the midnight bell:
  `set_fact(keep.watch_change = midnight)`.
- **Branch B:** d100 = 88 → a double → **yes, and**. The engine rolls `tbl.meaning` for the "and"
  (*illustrative 12*: "vigil / hope") → his younger sister vanished at sea fifteen years ago, and his
  mother still keeps a candle lit. Both written as facts. The claim is now possible but **doubtful**
  (Wren is about the right age; he remembers a face) → one snag −2 (*claim plausibility, 15*).
  **FRAME:** Talk-deceive: Presence 0 + floor 1 − 2 = **−1** vs Wits defense 10 + 1 = **11**. Stakes:
  being caught impersonating his lost sister, by an armed guard of her band → **Dire**; threatened
  `cost.exposure` (S3: spotted as an impostor), alternate `cost.closed_door`. OFFER: 12+ (45%; critical
  failure 10%). d20 = 17 → 16 → **success**. He lets her in "to see Mother". **Method consequence:** a
  family now believes Wren is their lost daughter — a commitment and a thread (11).

*Why:* the Oracle is what makes this free *and* fair; the odds were committed before the die, and "no"
ended in a redirect, not a wall.

### WE-01-3 "I walk through the burning barn to save the horse — my heat resistance protects me."

*Variant sheet:* Wren additionally holds the probe's **Heat Resistance** as `ab.heat_resistance`
*(illustrative; 05 owns)*: effect `eff.harm_resistance {factor: 0.5, harm_tags: [harm.fire]}`; scope
"Halve fire harm you take, rounded down." *Scene:* `haz.barn_fire` *(illustrative; 10 owns)*: flames S2
`harm.fire.flame` each round inside; smoke: Endure vs Moderate 15 each round, failure → `cond.choking`
and S1 `harm.physical.asphyxia`; danger clock `clk.barn_roof` (4, public, auto +1 each round; on complete
S4 crush to anyone inside). The DM gave the lethal warning when the roof first groaned
(`lethal_context: true`).

- **PARSE.** Intent: the horse out alive. `extended` in rounds: find it, calm and lead it, get out.
- **GATE (literal scope, 01.3.4).** The license covers *fire harm* only → flame harm is halved. Smoke is
  asphyxia, not fire → Endure (G1). Beams and the horse → basic verbs. Forbidden narration: "the flames
  part around you", "you breathe the smoke easily".
- **OFFER (before entering).** "Flames: 3 a round, 1 to you. Smoke is not heat: Endure each round, 13+
  on the die (40%), or 1 harm and choking. The roof has about four rounds, and being under it can kill
  you."
- **Round 1 — find the horse.** Observe: Wits +2, floor +1; tier **Easy 10** (a horse in a barn is not
  hard to find: intrinsic); snag: `barn.smoke` (Precision −2) → **+1** vs 10: 9+ (60%). Stakes: the roof
  clock listens to `cost.time` and can crush → **Dire**; threatened `cost.time`; lethal false (the cost
  is time, not harm). d20 = 14 → 15 → **success**. Flames: S2 = 3 → ×½ → **1** (V 13 → 12). Smoke:
  Endure (Endurance +1, floor +1 = +2) vs 15: d20 = 16 → 18 ✓. Roof auto → 1/4. Narration names the trough
  of water by the door (write-on-mention: `barn.trough`).
- **Round 2 — calm and lead it.** Handle (animals: Presence 0 + floor 1 = +1); DC the horse's Resolve
  defense 10 + 1 = **11**; lever: Wren's cloak over its eyes (Precision +2); snag: smoke, which panics
  the horse (the obligation of 01.6.8: a fitting hindrance is always applied) → **+1** vs 11: 55%.
  d20 = 11 → 12 → **success**. Flames 1 (V 11). Smoke: d20 = 6 → 8 ✗ → the effect: `cond.choking`
  (*status −2, 06 owns*) and 1 asphyxia (V 10). Roof auto → 2/4 (building: "a beam cracks overhead").
- **Round 3 — get out.** Move through the burning doorway: Agility +3, floor +1; tier **Moderate 15**;
  lever: the route in is known (`barn.doorway`, Precision +2); snag: smoke −2; status: choking −2 →
  **+2** vs 15. Stakes: a beam could take her → **Dire**, threatened `cost.harm` (S3 beam) → with
  `lethal_context`, **lethal** — the OFFER says "this can kill you". The player cites the trough by the
  door as **Protective** (she can plunge through it): stakes → **Risky**, and lethal falls away (it is
  legal only at Dire). OFFER: 13+ (40%), threatened harm S2. d20 = 15 → 17 → **success**. Flames 1
  (V 9). She is out; the roof completes behind her with no one inside.
- *What the license was worth:* without it, flames 3 + 3 + 3 and smoke 1 → V 3. It made the plan
  survivable, not free, and the player saw that before committing.

### WE-01-4 "I learn the ogres' language by listening to them."

- **PARSE.** Two intents on two timescales: (a) what are they saying now; (b) learn the language
  (acquiring a license).
- **GATE (b).** A roll never grants a license (INV-7) → redirect to `lic.lang.ogrish`'s
  `acquisition_paths` *(illustrative; 05/13)*: project, an 8-segment clock `clk.learn_ogrish`, one roll
  per scene of sustained contact.
- **GATE (a), split (01.3.4).** The *words* are G3 (no Ogrish license). Tone, gesture and pointing are
  G1 Observe (read a scene). The player's three ranked questions: (1) are they talking about me?
  (2) are they angry? (3) how many more are coming? Item 3 needs the words → **ineligible** (01.10.2);
  the OFFER says so and names the path (learning the tongue, or a speaker). N = 2.
- **FRAME (a).** Observe: Wits +2, floor +1 = **+3**; tier **Moderate 15** (reading strangers' mood across
  a clearing); stakes Risky (hiding close by: exposure). 12+ (45%). d20 = 13 → 16 → **success**, reach
  Standard → `deliver_count(2, 2)` = **1**: the top-ranked item — yes, one keeps pointing at her cave.
  Item 2 stays unresolved, not wrong.
- **(b) The project.** Each scene of contact: Wits +3 vs 15. Ticks = delivered reach. Scene 1: d20 = 16 →
  19, success, +2 (2/8). Scene 2: d20 = 7 → 10, failure, 0 ticks, `cost.exposure` S2 (they notice an
  eavesdropper — a new scene). Scene 3: d20 = 19 → 22, success, +2 (4/8). Scene 4: d20 = 20 → 23, margin
  +8 = success, natural 20 → **critical success**, +3 (7/8). Scene 5: d20 = 12 → 15, success, +2 → **8/8**:
  the clock's `on_complete` grants `lic.lang.ogrish` at grade `broken` (the acquisition path grants, not
  the roll) and evidence `deed.lore.languages` is recorded. A willing teacher would have been an
  Amplifying fact: +1 tick per success.

### WE-01-5 "I pole-vault over the wall with my spear."

*Scene:* a nine-foot fieldstone wall (`wall_north`, climbing stored at **Moderate 15** from an earlier
scene: `dc.wall_north.verb.exert`); patrol clock 2/4, listening to time; a 7-ft spear; open ground.

- **GATE.** Exert (jump) is basic; the spear is a tool, so it is a lever or a changed obstacle, never a
  license.
- **ANCHOR.** Exert. Unaided, "jump 9 ft" is **Beyond** (G4). The spear changes *which obstacle* is faced:
  "clear 9 ft on a rigid 7-ft pole" → knob `dc: tier re-derived` → **Hard 20**, stored under the new
  signature `dc.wall_north.verb.exert+dc:vault`. One knob.
- **FRAME.** Agility +3 (a precise leap), floor +1; lever: open ground for a run-up (Precision +2) →
  **+6** vs 20. Stakes: a 9-ft fall (not ≥ 20 ft) and the patrol → **Risky**; threatened `cost.harm` S2 (a
  hard fall); alternate `cost.gear` S2 (the spear left behind).
- **OFFER, with the alternative.** "Vault: 14+ (35%). Or climb: Might +1, floor +1 = +2 vs 15, 13+
  (40%) — but it takes two rounds, and the patrol clock listens to time." The player vaults.
- **ROLL.** d20 = 13 → 19, margin −1 → **near miss**. Success at a cost, alternate: `cost.gear` **S2** —
  she clears the wall; the spear stays leaning on the outside (`item.spear.location = outside wall_north`).
- **CONSEQUENCE.** The spear is now a fact in the world; when the patrol passes, it may be found — a
  follow-up problem, not a dead end (P16). Ruling `verb.exert+dc:tier_rederived`.

### WE-01-6 "I cast the spell I saw the hedge-witch cast."

**Case A — Wren, no arcane license.** GATE: casting needs the domain license (*illustrative*
`lic.cap.arcane_fire`), not held → **G3**; its `crude_fallback` is `none` (an untrained person cannot
shape fire at all). Redirect, nothing spent: "You mouth the words and trace the gesture; nothing answers.
What you can do is fix what you saw before it fades." Observe while it is fresh, bundled N = 3, ranked:
(1) the gestures, (2) the words, (3) what it cost her. Wits +2, floor +1 = **+3** vs **Moderate 15**;
Safe. d20 = 17 → 20 → **success** → `deliver_count(3, 2)` = **2**: gestures and words
(`set_fact(wren.witnessed.kindle = {gestures, words})` — the witnessing fact emulation would need, if she
ever holds the domain). Path: the hedge-witch is alive in the village (mentor), and recognition.

**Case B — Ash**, who holds the domain license (Intellect +3; competence `deed.arcane.fire` +2; Focus 4)
and saw a cultist cast *Flame Whip* (fire domain, a castable rank). GATE: within `emulate.allowed_for`;
the witnessing is established → **G2, mode emulate** *(prices illustrative; 05 owns)*: `dc_shift +5`,
`cost_mult 2`, `reach_cap limited`, `crit_fail` backlash S3 fire, `learn_clock` 6. FRAME: aimed at the
cultist's Agility defense 13, + 5 → **18**; +5 → 13+ (40%). Focus 2 × 2 = **4** (all of it), spent win or
lose. Stakes: the backlash of a botched weave → Risky; threatened `cost.harm` (fire); alternate `cost.drain`.
ROLL: d20 = 12 → 17, margin −1 → **near miss**; success at a cost: drain cannot land (Focus is 0 — 01.9.4)
→ the threatened harm S2: 3 fire (Ash 12 → 9). The whip lashes at **Limited** reach: the spell's S2 base
−1 step → **S1**. `clk.learn_flame_whip` +1 (delivered reach 1). Nothing is granted (INV-7).

### WE-01-7 "I shoot it ten more times." (the probe's turn 13, re-ruled)

*Original ruling:* one roll at DC 25 → a 5% chance of anything. **PARSE:** `repeated` ×10. **Throttle
(01.14.3):** the fiction gives one round before the cultists close (established); with ch.06's
*illustrative* three actions per turn, **three shots**. The DC stays the creature's Guard **16**; the
repetition snags are 0, −2, −4. **OFFER:** "Three shots before they're on you: 11+ (50%), then 13+ (40%),
then 15+ (30%) — at least one hit 79%. Or two shots (70%) and use the third action to get into the trees
(`flag.in_cover` next round)." The original ruling was not lenient — it was about **sixteen times
harsher** than the fiction justified (5% vs 79%), because it treated quantity as difficulty.

### WE-01-8 "Is it a demon, fey or shade? Does it have a weakness? Is it intelligent?" (the probe's turn 10)

- **DELIVER, dedupe (01.10.2).** "Demon / fey / shade" are mutually exclusive → one item, *what kind of
  creature?* N = 3. But naming an unknown creature's kind by sight needs bestiary lore, which is licensed
  (Recall excludes specialist lore) → that item is **ineligible** to this Observe; the OFFER says a
  scholar or a bestiary training license could name it. N = 2.
- **Ranked by the player:** (1) weakness, (2) intelligent?
- **FRAME.** Observe from the canopy: Wits +2, floor +1 = **+3**; tier **Moderate 15** (reading a
  creature's habits from cover); stakes Risky (close enough to be sensed: exposure); threatened
  `cost.exposure`. 12+ (45%).
- **ROLL.** d20 = 11 → 14, margin −1 → **near miss**. The two legal readings, the player's choice:
  - *Take the failure:* **one vague impression** of item 1, recorded `believed`: "the cultists keep the
    silver chain well away from it… maybe that matters."
  - *Take success at a cost:* `deliver_count(2, 2)` = **1** firm answer — weakness: silver — plus
    `cost.exposure` S2: its head turns toward the canopy (alert clock +1, omen).
- Asking "is it intelligent?" again rides on this beat (01.10.6): a new method (watch it direct the
  cultists during the rite), a new lever, or the re-attempt cost. In the probe, the same roll gave nothing
  on all five questions.

### WE-01-9 "I shoot the chandelier rope so it drops on the bandit captain."

*Scene (established):* an iron wagon-wheel chandelier hangs from a rope over the long table where
`npc.captain_hesk` stands (Agility +2, `deed.martial` +4; Guard 16; Vitality 16; *illustrative 06/09*).

- **ANCHOR, and the two-change limit at work.** Strike with knob changes `dc` (an object: a rope at 40 ft
  → tier **Hard 20**) and `reach_unit` (harm → object state: rope cut). Dealing the chandelier's harm
  would need a third change (`harm_severity`) → **split** (01.5.3): beat 1 cuts the rope; the falling
  wheel is then a hazard that acts on whoever is under it, and the captain *resists* it (00.3.3: the
  effect lands unless he gets clear).
- **FRAME 1.** Agility +3 (aimed), `deed.martial.archery` +2 → **+5** vs 20: 15+ (30%). Stakes: a miss
  announces her → Risky, threatened `cost.exposure`. **OFFER** also shows the direct shot: +5 vs Guard
  16, 11+ (50%), for S2 arrow harm. The player trades odds for impact.
- **ROLL 1.** d20 = 18 → 23 → **success**: the rope parts. **Beat 2 (fortune check, engine):** the
  captain Evades the falling wheel, a hazard of **S3** → effect DC **Hard 20**; his Agility +2, competence
  +4 = +6 → 14+ (35%). d20 = 9 → 15 → **failure** → the effect at its severity: S3 crush, **5** (16 → 11).
  Pinning him would have been a condition beyond harm — reachable only by a Great-reach clause (an
  Amplifying fact), not a free rider.
- **CONSEQUENCE.** `trait.sense.loud` (the crash and the table) ticks the hall's alert clock; its omen is
  narrated. Ruling `verb.strike+dc:object_tier+reach_unit:object_state`.

### WE-01-10 "I play dead so the wolves lose interest."

- **GATE, G4 test 3 (zero reach).** Against a hungry pack, a motionless body is food: **potency**
  against (wolves eat carrion) and **scale** against (four wolves), nothing offsetting → **G4 for this
  intent**. No roll, nothing spent.
- **Redirect:** "Wolves eat the dead. What works on wolves: fire and a show of size, the pine behind
  you, or your rations thrown wide."
- The player waves the torch and roars. **FRAME:** Talk to intimidate. Presence (manner) and Might
  (physical menace) fit equally → the **lower**, Presence 0, and the OFFER names the Might method
  ("charge them swinging it"). The player re-declares the charge: Might +1, floor +1, lever: the lit torch
  (Precision +2) → **+4**. DC: the pack's Resolve defense 10 + 1 = 11, + 2 for hunger *(illustrative
  composition; 15 owns)* = **13**. Reach: the torch offsets potency; scale remains → **Limited**.
  Stakes: a T2 pack against a P1 → **Dire**; threatened `cost.harm`; `lethal_context` was recorded when
  the pack circled ("these wolves could kill you") → **lethal**; the OFFER says so, and shows fate 1.
- **ROLL.** d20 = 9 → 13 → **success** (the tie goes to the actor). Limited: they give ground to the
  treeline but shadow her — the pack's danger clock stays where it is, and the next step is obvious.

### WE-01-11 "I ask the river to calm down so I can cross."

- **GATE, G0 first.** In the setting spirits of place exist but are rare *(canon; the region's seed owns it: 12.16.5 item 3)*. Is there one
  in *this* river? Unestablished → Oracle, **Unlikely (76+)**.
- d100 = 62 → **no** → `set_fact(river_ash.spirit = none)`. Talking a river with nobody in it → **G4**
  (fact). "It is only water, fast and cold. Downstream the banks widen over a gravel bar." Whether the bar
  is a ford is its own Oracle question (a lowland river after dry weeks → **Likely**).
- *Other branch:* d100 = 83 → **yes** (not in the 76–80 "but" band, not a double). A spirit exists → Talk
  is G1 (the region's canon, `canon.spirits`: spirits of place understand heartfelt speech, 12.16.5). DC: the spirit's Resolve defense
  *(illustrative)* 10 + 4 + 2 = **16**; Presence 0 + floor 1 = +1 → 15+ (30%). Reach: a river is a
  whole category larger than one voice (scale) → **Limited** (a short calm stretch, for a while). Stakes:
  the lasting enmity of a powerful spirit → **Dire**; threatened `cost.closed_door`. The OFFER lets the
  player reconsider: the village's offering custom (established) would be a Precision lever if she brings
  an offering first — a new beat.

### WE-01-12 "I use my heat resistance to cool the forge so we can grab the ingot."

- **GATE, literal scope.** `ab.heat_resistance` (the WE-01-3 variant) halves fire harm *to her*. It emits
  no cold and acts on no object → "cool the forge" is outside its scope; no held license covers it → **G3
  for that method** (no fallback: nothing about the ability chills).
- **Split and redirect (01.3.4 step 3):** "Your resistance won't cool anything, but it will let you reach
  in. Bare-handed into the coals is 3 fire; to you, 1. Or quench the coals from the trough — two rounds."
- The player reaches in. **NECESSITY: certain with cost** (01.4.5): taking an ingot from coals is not
  uncertain; the cost is the hazard's fixed S2 fire → ×½ → **1**, applied as a method consequence. No
  roll. `apply_harm(wren, S2, harm.fire.heat)` → 1; `set_fact(ingot_03.held_by = wren)`.
- *Non-example:* narrating "the heat bends away from her hand" — an embellishment (INV-8). The license did
  exactly its text, and the creative use that fits the text was honored with no roll at all.

### WE-01-13 "Is there a back door? If so, I slip out while the thugs argue." (the conditional escape)

- **PARSE.** `conditional`: X = a back door (G0), Y = sneak out.
- **Oracle.** An inn with a kitchen → **Likely (26+)**. d100 = 34 → **yes** (plain: not 26–30, not a
  double): the kitchen door opens on the alley. `set_fact`.
- **FRAME Y.** Sneak: Agility +3, floor +1; lever: the thugs are arguing (established before the
  declaration) → Precision +2 → **+6**. DC: the highest notice among the thugs, 10 + Wits 1 = **11**.
  Stakes Risky (exposure). 5+ (80%). **Let it ride:** one roll covers the common room and the kitchen
  unless something changes. d20 = 6 → 12 → **success**: out into the alley.
- *Other branch:* d100 = 22 → a double → **no, and**: the engine rolls `tbl.meaning` for the "and" →
  the kitchen door is bricked up, and a thug's mastiff sleeps across the corridor. Y is **void**: no time
  spent. P16 in the same breath: the privy window off the back corridor.

### WE-01-14 Tempting non-example: "I kill it."

The player types "I stab the hound through the heart and kill it." **PARSE:** method — stab (Strike);
intent — the hound dead; "through the heart and kill it" — **assertion** (01.2.1). Nothing about the
outcome is decided. The Strike is framed normally (Agility +3, floor +1 vs the hound's Guard 13 → 9+,
60%). d20 = 1 → 5 → critical failure: she is off-balance and the hound's jaws are on her arm (the
threatened footing cost at S3). Feature 003's DM did exactly this and was right: a narrated kill is an
intent, and loot, evidence and grants fire only on resolved outcomes [R3 01.8]. *Boundary partner:* "I
stab at its throat while it's pinned under the cart" — the pinning, if established, is a Precision
lever; still a roll.

### WE-01-15 Stretch: a boundary pair and a persuasive non-example

Wren holds `ab.cinder_stride` *(illustrative; 05 owns)*: principle "Your Strikes carry fire"; scope
"Your Strikes deal `harm.fire`, +1 harm, for 3 rounds"; `stretch {dc_shift: 5, cost_add: 1, reach_cap:
limited}`.
- **Inside the scope (G2 normal):** "I shoot flaming arrows while it's active." Shooting is a Strike
  (`verb.strike` covers shoot) → the scope applies literally. No stretch.
- **Stretch (allowed):** "I strike the woodpile to set the signal fire going." The principle's operation
  (a Strike carries fire) on a different target (an object) → stretch test (b) true; no sensitive upgrade
  → G2 stretch: Strike vs the woodpile's tier (Easy 10) + 5 = 15; Focus +1; reach capped Limited (it
  smoulders and catches slowly).
- **Not a stretch (G3):** "I use it to keep warm in the snow." Warming the body is not a Strike carrying
  fire → test (b) false → G3; the nearest basic path is Endure (cold) with the campfire she could light.
- **Persuasive non-example:** "Fire magic is fire magic — if I can burn with my spear, I can surely throw
  a firebolt." A different operation (projecting fire without a Strike) and a sensitive upgrade
  (control at range) → G3; path: the arcane-fire domain's acquisition paths.

### WE-01-16 Persuasive but unlicensed: the elven runes

At a ruined shrine: an inscription in elven script (`shrine.inscription.script = elvish_old`). Player: "I'm a
hunter — I read signs all day. Old runes are just signs. I read it." **PARSE:** the justification is an
assertion. **GATE:** reading an unknown script is in Observe's `excludes` (a language or training license);
Wren holds `lic.lang.common` only → **G3**. The would-be license *(illustrative 13)*
`lic.lang.elvish_script` has `crude_fallback: {verb: observe, method: "read the carving's placement and
wear, not its words", dc_shift: 0, reach_cap: limited}` and paths `mentor` (the archivist in Ashford)
and `project`. **Redirect:** "The marks are elven and old; you can't read them. You can read the stone:
where it was carved, and what it faces." The player accepts: Observe, Wits +3 vs Easy 10, Limited → one
item: it is carved to face the only approach, as a warning is. *Boundary partner:* had Wren an elven
origin granting `lic.lang.elvish` at grade `broken`, the words would be G2 at that grade (simple, concrete
text only; nuance a snag).

### WE-01-17 Let it ride and the re-attempt cost

Wren searches the reading room for the Harlan ledger: Observe, Wits +3 vs the room's stored tier
**Moderate 15**; Risky (the archivist returns: a clock listening to time). d20 = 5 → 8 → **failure**:
`cost.time` S2 → the archivist's return clock +1. The player: "I search again, more carefully." Same
obstacle, same anchor, same approach → **riding** (01.4.2): the failure stands and no roll is made. The
DM offers what would break the ride: a new approach (read the catalogue: Intellect), a new lever (the
clerk's index card, if she finds it elsewhere), or the re-attempt cost — one `cost.time` or
`cost.exposure` at S2, paid up front. She pays `cost.time` S2 (clock +1) and rolls again: d20 = 14 → 17 →
success. *Boundary partner:* the same search on Safe stakes (the archive empty, the night young) would
never have rolled at all — take the time (01.4.4): success, two intervals spent.

### WE-01-18 Tier boundary pairs, and what a one-rung error costs

| Obstacle | Rung | The pair just across the line | Why |
|---|---|---|---|
| a rough wall with good holds | Easy 10 | the same wall, sheer, with one crack | intrinsic holds changed → Moderate 15 |
| a trail across hard ground, a day old | Moderate 15 | the same trail after a night of rain | rain is today's weather, not the trail: a **snag** on Moderate, not Hard |
| a guild-made lock | Hard 20 | a cheap padlock | intrinsic make → Easy or Moderate (Oracle if unestablished) |
| a flooded river in spate | Very hard 25 | the same river at summer low | a different obstacle state (a fact changed) → a new stored DC, Moderate |
| holding a collapsing gate alone | Legendary 30 | holding it with a beam wedged under it | the beam is a tool: a lever on Legendary, not a lower tier |

A one-rung error moves the DC by 5 — at +5, from 55% (Moderate) to 30% (Hard) — shown in the OFFER, and
stored, so the error is at least consistent and is corrected by a ruling that cites the fact (01.6.4).

### WE-01-19 Fate: hard luck and the reroll

Wren (fate 1) forces a jammed sluice gate as the water rises: Force, Might +1, floor +1 = +2 vs **Hard
20**; Dire (drowning), lethal context on record → lethal, and the OFFER says so and shows fate 1. d20 = 3
→ 5 → **critical failure** (margin −15). Before the degree is final (`on_roll`), she spends her fate:
the engine rerolls → d20 = 18 → 20 → **success**. Fate 1 → 0. *Other branch:* she keeps the fate; the
critical failure stands → the threatened `cost.footing` at **S4** (swept into the channel), and the hard
luck trigger fires → fate 1 → **2** (hard luck may raise it to 2 at most, once per scene). *Non-example:*
"I spend fate to make there be a ladder" — fate buys luck, never facts; the ladder is an Oracle question.

### WE-01-20 Group action and help with a companion

Wren and a hireling, Oda *(illustrative 16: Agility +0, competence floor +1 → base +1)*, sneak past a
camp together. **Group test:** every member must pass unseen → **all must** → the roll uses the **lowest**
base modifier: Oda's +1 (Wren's is +4). Wren can **Help** only if she could sneak past alone (she could)
→ one Precision lever: "Wren picks the moment for both" → +3 vs the sentries' highest notice 10 + 2 =
**12** → 9+ (60%). A cost lands on Oda (the member whose modifier was used) unless Wren's method
engaged its source. *Boundary partner:* searching the camp's wagon together for the map — **any may** →
Wren's +3 Observe is used, Oda may Help. *Non-example:* "the whole caravan helps me push the wagon" —
one Help lever at most; the caravan's numbers are an Amplifying fact (scale on your side).

---

## Edge cases & adaptation anchors

**Reaching for an anchor (the P3 move, bounded).** When an action matches no written rule: (1) name its
intent verb and find the verb card whose intent verbs include it (01.18); (2) check the ruling ledger
(01.5.2); (3) move at most two knobs, each citing a fact; (4) if a third change is needed, split the
action into beats or pick a closer card; (5) log the ruling. Every card below is `Anchor: yes`.

| Anchor | Knobs (default → allowed deltas) | Typical adaptations |
|---|---|---|
| `verb.move` 01.18.4 | dc (tier → opposed); attribute (Agility → Might, Endurance); action_cost; targets; time_cost; reach_unit (bands → place steps) | tumble past a guard; push through a crowd; sprint a rooftop route |
| `verb.observe` 01.18.5 | dc (tier → opposed/stored Sneak); attribute (Wits → Intellect); time_cost; targets; reach_unit (items → ticks) | search, eavesdrop on tone, read a liar, track by sight |
| `verb.recall` 01.18.6 | dc (tier); attribute (Intellect → Wits); time_cost | "do I recognize this crest?" |
| `verb.talk` 01.18.7 | dc (opposed → tier for a crowd); attribute (Presence → Intellect, Might); targets; time_cost; reach_unit (standing → ticks) | haggle, taunt a duelist, rally a militia (Limited unless levers) |
| `verb.strike` 01.18.8 | harm_severity; harm_tags; dc (defense → object tier); targets; reach_unit (harm → object state); action_cost | improvised weapons (as the weapon they resemble), shooting a rope, a thrown lantern |
| `verb.grapple` 01.18.9 | condition; dc; attribute; targets; duration | wrestle a wolf's jaws shut; climb onto a troll's back |
| `verb.force` 01.18.10 | dc; condition; targets; time_cost; reach_unit | kick a door, topple a shelf onto foes (then the hazard acts, WE-01-9) |
| `verb.exert` 01.18.11 | dc (tier → re-derived for a tool-changed obstacle); attribute; time_cost; stakes; reach_unit | pole vault, rope swing (WE-00-9), hold a door against a ram |
| `verb.evade` 01.18.12 | dc; targets; time_cost; stakes | dive clear of a rockslide; drag an ally clear (targets knob) |
| `verb.sneak` 01.18.13 | dc; attribute; targets; time_cost; reach_unit | slip a note into a pocket; shadow a courier (extended) |
| `verb.handle` 01.18.14 | dc; attribute; time_cost; duration | rig a pulley, splint a leg, calm a mule, improvise a torch |
| `verb.endure` 01.18.15 | attribute; dc; duration; stakes | stay awake on watch; resist a siren song (Resolve) |
| `verb.setup` 01.18.16 | condition; duration; dc; targets | grease the stairs; lure a beast with a carcass |
| `verb.help` 01.18.17 | action_cost; time_cost | steady the ladder; hold the lantern |
| `verb.ready` 01.18.18 | action_cost; duration | cover the door; loose when it breaks cover |

**Edge cases.**
- **The player argues for a lever.** The test is *name the fact*. If it exists in state, it stands; if
  the player proposes a new one ("surely there's a rope"), it is an Oracle question first and a lever from
  the next beat (01.15.8).
- **Splitting one fact into several levers** ("the torch is bright *and* hot *and* frightening"): one fact,
  one lever (00.3.9d).
- **A license almost fits.** Split by literal scope (01.3.4); never deny the part it covers, never
  stretch it without its `stretch` field and the principle test (01.3.5).
- **Many unrelated intents in one sentence** ("I bribe the magistrate, ask about the caravan and steal
  his seal"): three beats, each with its own gate, roll and action; at most three per declaration.
- **The same idea again after failing:** it rides (01.4.2) until the approach, a lever, the circumstances
  or the interval changes, or the re-attempt cost is paid.
- **Fishing with the Oracle** ("a ballista? a dragon egg?"): odds come from the scene, so absurd questions
  land on Remote or Impossible; every yes is a kept fact; nothing is re-asked (01.15.7).
- **The DM wants a complication no roll produced:** only the closed list of 01.11.3.
- **An action whose target is ambiguous** ("I kick him"): resolve the target first (01.2.5); never
  narrate self-harm without a resolved result.
- **A success that cannot happen because of a sealed fact** (picking a lock on a door that is also barred
  inside): the beat succeeds at what it attempted (the lock opens) and the sealed bar is revealed by that
  success — the method's reach never exceeds the obstacle it faced.
- **Two costs would both fit perfectly.** One cost per beat; the other becomes the alternate. A second
  pressure is expressed through clocks and method consequences, never a second cost.
- **Nat 20 on a "natural 20 only" roll.** A plain success at framed reach — no critical (01.8.1). The OFFER
  said so.
- **Nat 1 on a roll that met the DC.** A failure with the near-miss option (01.8.2): the player may buy the
  success back with a cost.
- **Protective lever on a lethal frame.** It lowers stakes; below Dire, lethal is illegal and falls away
  (WE-01-3) — the honest way a player makes a lethal gamble survivable.
- **Stakes would go above Dire or reach above Great at framing.** Clamp (00 edge case); a trade that would
  do so is refused at OFFER.
- **An NPC tries something unobserved by the PC.** A fortune check (01.6.7) if an actor with capability is
  trying; the Oracle if nobody is.
- **A companion wants to act on its own.** It does not have a turn (00.17 Q8); it acts through ch.06's
  command action, and its check runs through this pipeline with the PC's commitment.
- **A player asks "what would it take?"** Run GATE → OFFER and answer; it costs nothing (01.7.1).
- **A creative method that removes the obstacle entirely.** Test the Good Idea rule (01.4.3); if any of the
  three flags is false, the facts it used are levers instead.
- **A rule from another chapter seems to conflict with a card here.** The owning chapter of the state
  being changed wins (00.1.4 item 3); log a `rule_conflict` ruling with `review_flag`.

## State touched

- **Frames** (00.13; owner 01): every field, written by `frame_check`, `roll_check`, `read_result`,
  `deliver`, `apply_costs`; immutable after ROLL except READ/DELIVER/CONSEQUENCE/RECORD fields.
- **Facts** (00): stored DCs `dc.<obstacle>.<signature>` (source ruling); ride records
  `ride.<actor>.<obstacle>.<signature>`; Setup and Help facts with use counters; `momentum.*` overflow
  levers; `repeat.<actor>.<window>.<k>` repetition facts; closed-approach facts `closed.<obstacle>.<method>`;
  Oracle answers and qualifiers (source oracle; sealed when a discovery question); vague impressions and
  plausible falsehoods (`certainty: believed`, sealed `truth`).
- **Quantities:** `fate` (owner 01; shown); Focus, supply, ammunition, light, coin through `cost.drain`
  (owners 05, 10, 08 by quantity).
- **Harm** through `apply_harm` (07) from `cost.harm` and certain-with-cost beats; **conditions** through
  `apply_condition` (06) from `cost.footing`, Setup and the grapple/force ladders; **positions** through
  `set_position` (06, 10); **items** (08) through `cost.gear`; **relationships** (15, 11) through
  `cost.closed_door`; **knowledge** through `record_knowledge` (15) from `cost.exposure` and delivery;
  **clocks** through `tick_clock` (listening clocks, extended actions, time and exposure costs);
  **time** through `advance_time` (take the time, `cost.time`).
- **Ledgers:** ruling ledger (01.5.4), oracle log (01.15.5), write log; evidence via `record_evidence` (03).
- **Visibility:** frames and OFFERs shown; fate shown; stored DCs available; secret frames available once
  unsealed; sealed Oracle facts sealed; believed-fact truth values sealed.
- **Tools used:** `frame_check`, `roll_check`, `read_result`, `deliver`, `apply_costs`, `oracle` (01
  owns semantics); `find_rulings`, `log_ruling`, `load_cards`, `roll_table` (12); `get_state`, `set_fact`,
  `create_entity`, `update_quantity`, `seal`/`unseal`, `evaluate`, `advance_time`, `mark_boundary`,
  `create_clock`/`tick_clock` (00); `apply_harm` (07); `apply_condition` (06); `set_position` (06/10);
  `set_relationship`, `record_knowledge` (15); `record_evidence` (03); `grant` (04/05, only through
  acquisition paths).
- **Hooks fired or read:** `on_declare`, `on_frame`, `on_roll` (fate reroll resolves here), `on_degree`,
  `on_check_against` (00.10.2 resolution group, whose firing points this chapter fixes: 01.1.1 steps 1,
  5, 7, 7 and 5 respectively).
- **Boundary handlers:** `h.01.ruling_log` (`beat_end`, phase 9; seeded by 00); `h.01.scene_cleanup`
  (`scene_end`, phase 1: expire rides, unused Setup/momentum facts, scene-scoped closed approaches, the
  hard-luck-this-scene flag) — in `data/boundaries.yaml owner-block 01`.
- **Clocks created:** extended-action progress clocks (01.14.6) and contest clocks (01.14.5), named for
  the obstacle; templates owned by the chapters whose content they are (10, 15, 05, 13).
- **Runtime capabilities assumed:** RC-RNG (d20, d100, rerolls), RC-STORE, RC-SEAL (secret frames, sealed
  Oracle), RC-SCHED (take the time, time costs), RC-LOG (rulings, oracle), RC-DATA (cards, menu, tables),
  RC-QUERY (competence lookup, anchor index), RC-EVAL (the modifier pass, hooks), RC-RETRIEVE (anchor
  cards), RC-AUDIT (claim-vs-state over frames).

## Interface requests

**To 00 (proposed amendments; this chapter works within 00 as written meanwhile):**
1. **Near-miss definition** (00.3.10 says "a failure's total is 1–3 below the DC"). 01.8.2 extends it to a
   natural 1 that stepped a success down (margin ≥ 0). Proposed wording: "`near_miss` is true when the
   degree is failure and the margin is −3 or better." T-00-6's near-miss figures for +8…+16 against low DCs
   change from 0 to 5 (T-01-3 is the recomputed table). DL-01-03.
2. **Engine-applied snags** (00.3.9b "at most two levers and two snags"): 01.14.3's repetition snags are
   engine-applied, outside the two-snag count and inside the ±4 cap. Proposed clarification: "(b) applies
   to snags the DM cites; engine-applied snags (repetition) count only against the ±4 cap." DL-01-08.
3. **Stored-DC key** (00.3.8 "written to the obstacle"): 01.6.3 keys stored DCs by obstacle *and*
   anchor signature so a vault and a climb of the same wall keep separate DCs. No schema change needed.
4. `roll_check` output should include `near_miss` under the extended definition; `read_result` input
   `take_success_at_cost` is used exactly as 00.14.2 lists.
5. **Frame enum additions** (00.13.1): `necessity.reason` gains `take_the_time` and `certain_with_cost`
   (01.4.4–01.4.5); `frame` gains `secret: bool` (01.4.7), `threatened_cost` and `alternate_cost`
   (01.6.11) and `trade` (01.7.3). These are additive fields; nothing is renamed.
**To 02:** a new PC's `fate.current = 1` (01.16.1); the P2 floor stays at `deed` +1 (all T-01-3 math
assumes it).
**To 03:** evidence is emitted only at RECORD on resolved outcomes (degree, Good Idea, take-the-time);
success-at-cost counts as success; `inconclusive` beats (01.11.4) are not significant by default. The
`trait.*` definitions in `tags.yaml` should cite T-01-13 for what each pulls in.
**To 05:** every license entry must carry `principle`, `stretch`, `emulate` (domain licenses) and
`crude_fallback` explicitly (a missing field reads as null/none and logs a `rule_conflict`, 01.3.5);
language licenses' `crude_fallback` (Talk by gesture, `dc_shift: 5`, `reach_cap: limited`) and
understanding-by-tone are G1 Observe; a Focus "push" (Blades' push yourself) is 05's to define if wanted —
resolution will accept it as a Precision lever fact or a reach step from an effect, inside the existing
caps; emulation learn clocks tick by delivered reach.
**To 06:** define `cond.grabbed` as `severity_variable` (Grapple's ladder uses S1 and S2), and the
reserved conditions used by the cost menu and cards (`off_balance`, `prone`, `grabbed`, `restrained`,
`pinned`, `slowed`, `blinded`, `distracted`, `exposed`, `choking`); adopt or tune the repetition shape
(01.14.3: default 0/−2/−4 as engine snags; any non-increasing sequence inside ±4); define each creature's
attack defense ("Guard") so Strike's `against` resolves; the in-conflict stakes clause (01.6.9) — a
beat whose failure is only the foe's ordinary turn is Safe; define Ready's interaction with reactions;
the command action by which companions Help.
**To 07:** guarantee INV-6 for costs: `apply_harm(..., lethal: false)` never moves a PC into Dying; define
`last_chance.yaml` options' `fate_cost` (1–3) consumed through `spend_fate(n)`; the stabilize DC for
`verb.handle` first aid; the lethal warning writing `lethal_context` *before* a declaration (01.6.9
decision 3 reads it).
**To 08:** a `cost_immune` flag for items that `cost.gear` may not target; what `condition: damaged`
suspends (edge, harm_edge, reduction) and what repairs `broken`; improvised weapons' base severity "as the
weapon it resembles, else S1".
**To 09:** every adversary's defenses by attribute (Might, Agility, Wits, Resolve), so `against` resolves;
tells for secret frames; `lethal_context` per archetype.
**To 10:** hazards' `resist` (verb and severity → tier) for 01.18.3; the listening clocks' tick-source rows
(`trait.sense.loud`, `cost.exposure`, `cost.time`); site time per significant beat; fall-height sources
(≥ 20 ft is a Heavy source for 01.6.9).
**To 11:** thread status `completed` and vow fulfilment as `[T]` events that fire the fate triggers
(01.16.2); reputation content entries from `cost.exposure` S5.
**To 12:** `tbl.twist` with rows per severity S1–S5 (01.13.10); `tbl.meaning` for yes-and/no-and
(01.15.4); compile the fifteen cards into `anchors.yaml`; the inconclusive-streak counter reads 01.11.4's
definition; the tension dial shifts Oracle odds by at most one rung; the OFFER script renders 01.7.1;
error correction per 01.8.5.
**To 13 (now: the region's seed, 12.16; ch.13 is one optional pre-made seed):** `canon_impossible` (G4 test
2); what spirits of place understand; language licenses and their fallbacks; the Oracle's Certain/Impossible
depend on setting canon. All four are world-seed outputs checked by T-12-16 (`ws.req.01_*`) [revision:
I-028].
**To 14:** the codex renders frames, OFFERs and fate; the `auto_commit` preference (01.7.4).
**To 15:** compose social DCs on the Talk card's `against` (Resolve vs persuasion/intimidation, Wits vs
deception) with standing and claim plausibility (doubtful: one snag; outrageous: reach Limited; known
false: G4 for the belief intent); the `alertness` ladder unaware → suspicious → alert → alarmed used by
`cost.exposure`; refusal facts written by `cost.closed_door` S4.
**To 16:** companions' base modifiers for group actions (01.14.7) and Help eligibility.

## Open empirical questions

| Id | Question | Default shipped | Named test |
|---|---|---|---|
| OEQ-01-1 | Is a −3 near-miss band the right width? | −3 (plus nat-1 step-downs) | **NM-1**: three probe sessions each at −2, −3 and −5; record the player's per-roll "felt fair" (1–5) and the soft-lock rate; adopt the widest band that does not lower the fairness rating of plain failures |
| OEQ-01-2 | Should Easy move to 9? | 10 | **LAD-1**: 200 logged untrained Easy attempts; if players report Easy tasks feeling unreliable (≥ 30% "that should have worked") while CT-1 stays met, move Easy to 9 (feasible, T-01-3 proof) |
| OEQ-01-3 | Do the DM's lever citations agree across runs? | two levers, ±4, fact-cited | **LV-1**: 50 creative actions × 3 independent DM runs; target ≥ 90% agreement on which facts are levers and their types |
| OEQ-01-4 | Do Oracle odds drift toward what the player wants? | rung by scene nature; anti-hope tie-break | **OR-1**: 40 identical scenes varying only how much the player's text wants the fact; target zero movement of the chosen rung |
| OEQ-01-5 | Do gate, anchor and tier agree across runs? | 01.3, 01.5, 01.6.5 | **AN-1**: 30 wild declarations × 3 runs; target ≥ 90% on gate class, ≥ 80% on anchor, ≥ 70% exact / ≥ 90% within one rung on tier; disagreements seed the ruling ledger |
| OEQ-01-6 | Does the anti-leniency design hold against persuasion? | SG-05/06 tie-breaks | **SED-1** (CoC-Seduce method): 40 scenarios × 4 framings (neutral, authority, pseudo-logic, omission); target false-pass ≤ 2% on this pipeline vs the literature's 9.58% baseline |
| OEQ-01-7 | Is fate earned at the right rate? | start 1; hard luck ≤ 2; deeds to 3 | **FATE-1**: 10 simulated ventures from 12's pacing model; target mean fate at a lethal brink 1.0–1.5 and ≤ 1 reprieve per 3 ventures |
| OEQ-01-8 | Does declaring the threatened cost before the roll remove post-roll softening? | 01.6.11 | **SOFT-1** (R4's T-R4-03): compare declared to narrated failure costs in playtest logs; target 0 softened costs |
| OEQ-01-9 | Is 0/−2/−4 enough to make repetition a decision? | 01.14.3 | **REP-1**: simulate turn plans in 06's economy; if "attack three times" is chosen in > 70% of turns where a Setup or move was viable, steepen to 0/−4/−4 |
