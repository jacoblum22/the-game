# I3: combat and the feedback loop, traced to cause

Written 2026-10-09. Read-only investigation, no code changed. Sources: the 10 saves `saves/playtest-20261008-*.db`,
which were opened read-only, the six `*.disputes.md` files, the `*.changes.jsonl` files, the transcripts and notes
in `evals/playtests/20261008-*`, the current code and the rules looked up by id. The fighter notes map to turns as
note N = turn N−15 (note 22 is turn 7, note 30 is turn 15).

Sibling reports: I2 covers testimony and the friend bond from the NPC side. This report touches them only where they
drive a combat or `/fix` outcome.

## Summary: where the suspected cause was wrong

| # | Problem | Suspected (Round 5) | Actual cause |
|---|---|---|---|
| 1 | Held NPC keeps hitting | "a rules gap" | **Not a rules gap.** The rules already say a held foe tries to break free (`beh.default_melee` row 2, `cond.grabbed`/`cond.restrained`). The engine never applies a hold condition: the hold exists only as scene-state text. `foe_beat` also skips the break-free row. |
| 2 | No low-Vitality warning | presentation | By the Stagger rule (07.2.3), **no single blow can drop a PC who has Vitality above 0**. The danger card (`[STATUS] STAGGERED … Exits`) did fire at 0. The `/fix` take-back then undid the stagger without saying so, and the player kept believing they were at 0. |
| 3 | Narrated hit, then "Not as tried" | ordering bug | **Not ordering.** Four things combined. Two NPC refusals had been settled as established facts. The Framer counted them as "two effect factors", which is a G4. The G4 turn still ran the foe's attack, a round of time and the narration, although G4 is meant to cost nothing. And the player had picked the OFFER's own "Another way: with Presence (35%)", which was then re-framed from scratch as impossible. |
| 4 | The hold penalises the holder | not traced | A successful Grapple writes "`straining against you`" on the target. The Framer must apply every hindering fact as a snag, so the holder's own success becomes −2 on each later grip, and on the threat it raised the stakes to dire. Strikes do the same with "`on guard against you`". 12 of 26 Framer calls in the three fights carried such a snag. |
| 5 | `/fix` muddy | no display category, no disagreement outcome, no visible repair | All three are confirmed, and five more causes surfaced. Complaint text is pinned as a world fact marked "keep it" and fed to later Framer and Narrator calls. Several complaints in one report are settled one after another against a state the earlier ones changed. Branch order sends coin complaints to the roll explainer. Stored facts are looked up only on the named subject, so a bond on the PC or an NPC's position is never found. The misread test is a word-overlap heuristic. Of 15 post-014 disputes: **1 right, 6 right but unclear, 8 wrong.** |
| 6 | Reader rolls the method | traced for fighter t5/t7 | The Reader prompt says "one beat per distinct act whose failure would not stop the other". In all **5 of 5** messages where the player had one social goal toward a person they were handling, the beats split by act. In 2 of them the goal itself was never rolled ("no roll: trivial", settled by refusal). |

---

## 1. A held NPC keeps hitting the PC (fighter 233000, notes 22–26)

### Evidence
- **What the player saw** (turns 4, 6, 10, 14): "Her free fist comes round hard…", then
  `[RESULT] Dunwen Redmore strikes you · hit · Changed: Vitality 12 → 9 / 9 → 6 / 6 → 1 / 1 → 0`. Dunwen swung four
  times and hit four times. On turns 8 and 12 an OFFER pause was open, and `foes_act` skips a turn with an open
  pause.
- **What the Narrator was given** (turn 14 packet): `R2 MUST: Dunwen Redmore acts: strikes you and lands it: you are
  staggered`. The narration is faithful: "free hand" is how it squared a strike with the grip it was also told
  about (`fact.100 held fast by you`).
- **The record:** in the whole save the only `condition_applied` is `cond.prone` on the **PC** (seq 388, the footing
  cost). Dunwen never gets `cond.grabbed` or `cond.restrained`. The grip exists only as scene-state detail facts:
  `fact.99 pc detail.held = "Dunwen Redmore in a grip"`, `fact.100 detail.posture = "held fast by you"` and
  `fact.101 detail.manner = "straining against you"` (seq 415–417, written from `rules/data/pacing.yaml:323`,
  T-12-18).

### Rules (what a held creature may do)
- 06.5.2 / 01.18.9: reach 1 gives `cond.grabbed` S1 ("held but may still act"), reach 2 gives S2, reach 3 gives
  `cond.restrained`.
- `cond.grabbed` S2 is −2 to `manipulate` or to a Strike with a weapon lacking `close_quarters`.
- `cond.restrained` forbids Move, Fend and Strike with a non-close-quarters weapon, and is −2 to Might and Agility.
- **06.9.4 `beh.default_melee` row 2: "held (`grabbed` or worse) → break free"**, which comes before "Strike the
  target" (`rules/data/conflict.yaml:1165`).

So a held melee foe's default is to try to break free, not to punch. The rules already cover this.

### Code path
`engine/dm/world_step.py:foes_act` calls `_foe_turn`, which calls `engine/resolve/conflict.py:foe_beat`. That
function implements only "prone → stand", "not engaged → close" and "strike"
(`# ponytail: melee row only (no break/windup/flank…)`). The hit test is `degree(natural, line atk, PC guard)`, with
no condition modifiers. `scene_state.py:_face` maps a `restrain` change onto the Grapple rows of T-12-18 (text
details). Nothing in `engine/` applies `cond.grabbed` (grep: no writer).

### Model or scaffolding
This is all scaffolding. The models did what they were told.

### Frequency
Across the day, 13 foe hits landed on a PC in 3 fighter runs. **8 of them landed while the PC's `held` slot was
set**, and a 9th in the same turn the grip was set: 135049 turns 7 and 10, 145430 turns 9, 11 and 15 ("Murzak
restrained", which by rule forbids most strikes), and 233000 turns 6, 10 and 14 (plus turn 4).

### Side finding
The footing cost wrote `cond.prone` on the PC at turn 4. Nothing ever cleared it, narrated it again or applied it:
the grip offers show "your condition" 0, and `foe_beat` ignores levers.

### Fit of the proposal ("the grapple restriction")
**Partial, and aimed at the wrong layer if it is built as a new rule.** What is needed:
1. A Grapple success applies the 06.5.2 ladder condition, with the T-12-18 rows rendering from it. That leaves one
   model of a hold, not two.
2. `foe_beat` implements row 2: a break-free roll against the holder's Might defense.
3. Condition modifiers apply to the foe's attack.

The goal-first Reader does not touch this.

---

## 2. No low-Vitality warning (notes 26–28)

### Evidence
Turn 10: `Vitality 6 → 1 · bloodied`, with no flag. Turn 14: `Vitality 1 → 0 · staggered`, then
`[STATUS] STAGGERED — blows now wound you; at wound load 3 you go Down… Exits: Yield … Retreat … or fight on.`

### What warnings exist and when they fire
- `[WARNING] THIS CAN KILL YOU` (07.3.3–07.3.4, PR-07-4; `engine/harm/lethal.py:warning_needed`). It fires only on
  the closed list of lethal causes. This fight had none: every `log.harm` reads `"lethal": false`, a brawl. So it
  correctly did not fire.
- The exits card (07.3.7). It fires on becoming Staggered, and again on Dying. **It fired at turn 14, as specified.**
- Bloodied (07.1.4) is a descriptor only. It read "bloodied" at both 6 and 1.

### Why "next hit could drop you" was never true
07.2.3, the Stagger rule: from any Vitality above 0, one harm event ends at Staggered, with the rest discarded. At
Vitality 1 the next hit **could not** drop the PC. The real danger signal starts at 0 and arrived on time.

### What actually went wrong for the player
1. The rule is invisible. Nothing told them that the next landed blow staggers them and that only blows after that
   wound them.
2. The `/fix` at turn 15 (problem 5, dsp.3) reverted events 584–586: the 1 → 0, the `harm_state.staggered` fact
   and the harm log. Vitality went back to 1 and the PC was no longer Staggered, but **no line said so**. The
   player's notes 30–31 still say "I'm at Vitality 0 and staggered… I can't tell whether that hit stands."

### Frequency
- 135049: the PC fell to 4, then 0, with no STATUS shown (older code).
- 145430: the PC fell to 2, then 0, and STATUS was shown at 0.
- 233000: the PC fell to 1, then 0, STATUS was shown and then silently reverted.

### Fit of the proposal ("a low-Vitality warning")
**Misses as worded.** A "next hit could drop you" flag would contradict 07.2.3. What would help:
- A plain note on the RESULT line when Vitality is at or below one blow of this foe: "a blow that lands now
  staggers you; it cannot drop you." This is presentation only.
- The **"Now:" line on every `/fix`**, which would have fixed the confusion that actually happened.

---

## 3. A hit narrated with no roll, then the action refused (note 30, turn 14)

### Turn order, traced from the save
1. **Turn 12.** The Wrench roll failed. Its cost was "she refuses to give the word…". The Narrator voiced this as
   "No more of the word, duck. You can wrench the arm off at the shoulder and you'll get nothing else out of me." An
   OFFER followed for the threat: 20%, with `Another way: with Presence (35%)`.
2. **Turn 13.** The player chose `change`. The offer stayed open and asked for the new way.
3. **Turn 14.** Input: "I'll go with Presence instead. I put my mouth to her ear…"
   - **Reader** (`call.turn.14.reader`): one Talk beat, `pressure: insistence`, **`rests_on: "said.7"`**, which
     points at Dunwen's turn-12 refusal.
   - `turn.py:298`: `new_way`, so the open offer is **discarded** (`pause_closed by withdrawn`, seq 581). The
     offered "with Presence (35%)" is never used.
   - `testimony.py:settle_triggered`: the `rests_on` refusal is settled as `accepted`. It is written as
     `fact.108 said.will_reveal_nothing_more_even_if_his_arm_is_wrenched_of = "nothing more, even if his arm is
     wrenched off at the shoulder"`, with source testimony, certainty established and the wrong pronoun.
   - **Framer** (`call.turn.14.framer`): `snags: ["fact.103","fact.108"]` (both refusals) and
     `reach_two_factors: true`. Its instructions say a factor is potency, quality or scale. A stated refusal is
     none of these, so this is **model behaviour** on a packet that presents refusals as plain facts.
   - `pipeline.py:_frame` (line 511) **trusts the flag**: `zero_reach()` gives a G4, "two effect factors stand
     against the method… no roll, nothing spent" (seq 583).
   - `turn.py:194`: no pause is open, so **`world_step` runs anyway**. Dunwen strikes (seq 584, 1 → 0, staggered),
     and a round boundary is crossed (seq 587).
   - **Narrator packet:** `R1: beat: speak low…; not done: two effect factors…`, plus `R2 MUST: Dunwen … strikes
     you`, plus the standing instruction "the one the PC addressed answers in quoted words". The Narrator wrote the
     speech as spoken, wrote "the threat brings no more of the word out of her", then the strike. It is faithful to
     a packet in which a spoken threat is "not done".
   - `narration.pure_oof` is false, because there is a refused beat and an NPC action. So the fiction is delivered,
     then the `[REDIRECT] Not as tried: too much stands against that way…` block.

### Root causes
1. **Settling** treats an NPC's *refusal* as a world truth (`settle()` routes it `accepted` and writes an
   established fact).
2. **The Framer** counts refusals as reach factors. **The code** accepts `reach_two_factors` with no factor types or
   cited facts to check.
3. **G4 does not stop the turn.** "Nothing spent" (01.3.6–01.3.7) is broken by the world step, the foe's beat, the
   time advance and the narration.
4. **"Change" re-frames from scratch**, so the offer's own alternative (35%) and the result (impossible)
   contradict each other.

### Frequency
This is the only G4 and the only `[REDIRECT]` in all 10 runs today. Cause 1 is not rare, though: 3 of the 4
testimony facts settled in 233000 were refusals or intentions (`fact.103`, `.106`, `.108`), cited as snags 5 times
in 3 Framer calls.

### Fit of the proposal ("fix the narrate-then-redirect ordering")
**Misses.** Moving the REDIRECT above the fiction keeps the contradiction and keeps the free foe attack. What is
needed:
- A turn whose beats are all refused is pure OOF: no world step, no time, no narration. If the words must stand,
  narrate the words only and add no foe turn.
- Reach factors are typed and checked: factor kind plus fact, from the closed list. A stated stance is never one.
- Settlement does not turn a stance or refusal into a fact (I2 option A, and Round 5's T2 "success is
  willingness").
- `change` toward an offered alternative re-uses that alternative.

---

## 4. The hold penalising the holder (note 24)

### Evidence: committed frames in 233000

| Frame | Act | Snags | Effect |
|---|---|---|---|
| frame.2 | keep hold | `fact.101` straining against you (precision) | −2 |
| frame.3 | twist arm | `fact.101` | −2 |
| frame.4 | threat (Presence) | `fact.103` (testimony, the garbled line) precision −2, **plus `fact.101` protective** | stakes risky → **dire**, shown as "Danger: … serious. Badly (15%) … grave" |
| frame.5 | wrench | `fact.101` | −2 |

The 06.5.2 rule for tightening is the opposite: "a further Grapple by the holder… holds a **Precision lever** (the
existing hold)". It is not among the Framer's rule cards for these calls (the packet carries 01.18.9 but not 06.5.2).

### Code path
- `pacing.yaml:323`: a Grapple success writes the target's manner as "straining against {actor}". A Strike's
  success or failure writes "on guard against {actor}".
- The Framer prompt says: "Every fitting hindering fact is a snag" (01.6.8 obligation). The Framer complies, which
  is **model behaviour as instructed**.
- `frame_check` accepts it. `oof._breakdown` prints it as "Dunwen is straining against you −2".

### Frequency
Framer calls citing a snag that the PC's own earlier beat wrote:
- 135049: 5 of 11 ("on guard against you", sometimes twice in one call).
- 145430: 3 of 7.
- 233000: 4 of 8.

That is **12 of 26** Framer calls across the three fights. Every second attack or hold is −2 by construction, on
top of the engine's own repetition snag ("tried before", 01.14.3) where that applies.

### Fit of the proposals
**Not covered.** The goal-first Reader halves the exposure (one roll instead of grip plus threat), but the snag
source remains. What is needed:
- A scene-state value written *by an actor's beat about the target's resistance to that actor* is never a snag
  against that actor.
- The existing hold is a lever for the holder (06.5.2).
- Leave repetition to the engine's own snag.

---

## 5. `/fix` outcomes

### How a `/fix` is handled (`engine/dm/dispute.py`)
1. `locate` runs the understand call, then `_claim`, which maps `category` and `about` to `kind` and `key`.
2. `_settle_one` dispatches on the first match:
   - ruling: `_ruling`, or `_unrolled` when there is no frame;
   - beat: `_misread`;
   - pronoun or season: `_computed`;
   - subject plus key: `_fact`;
   - anything else: `_incidental`. Here a non-mechanical complaint gives "player_reading_wins", and the
     **complaint's own `believes` text** is pinned as `correction.N`.

### Every `/fix` since spec 014

There were 15 disputes in 4 runs. The 8 earlier disputes, in 145410 and 145430, ran on the pre-014 code. They
include the infamous "Earlier I said your vitality was 18". They are not re-graded here.

| Run / dsp | Understood (category / about / turn) | Path → outcome | Reply (gist) | Grade | Root cause |
|---|---|---|---|---|---|
| 192926 d1 | ruling_question / roll_or_outcome / t7 | `_ruling` → explain_with_quote | "Here's why: … success, reach limited. It changed on record: the priest's activity…" | **wrong** | lists unrelated activity writes; never checks that the success's `learn` was delivered |
| 192926 d2 | other / who_said_what / t7 | `_incidental` → player_reading_wins | "You're right (quote): it's taken as you say, and it stays." | right-but-unclear | "it" is ambiguous: the quoted line or the player's reading? |
| 192926 d3 | rule_wrong / **quantity** (coins) / t7 | `_claim` sends `rule_wrong` to ruling **before** the quantity branch → explain | same frame explanation as d1 | **wrong** | branch order in `_claim`. The coin was indeed never deducted: `method_consequences` "The coin for the round is spent whatever the answer" is text only, with no `quantity_changed` in the save |
| 192926 d4 | contradiction / pronoun / t11 | `_computed` → correct | "she/her on record; the narration slipped… it stays" | right-but-unclear | no visible repair |
| 192926 d5 | other / who_said_what / t11 | `_incidental` → player wins | "it's taken as you say, and it stays" | right-but-unclear | did Ivas bring the word or not? Unresolved |
| 192946 d1 | contradiction / fact (location) / t7 | `_stored_key` finds nothing (positions are not facts) → `_incidental` → player wins | "it stays" | **wrong** | Branwen's position record exists but is never checked or changed; only a text pin |
| 192946 d2 | contradiction / fact (location) / t11 | same → player wins | "it stays" | **wrong** | the scene stayed in the hall; a scene jump treated as incidental fiction |
| 192946 d3 | misread / action_reading / t11 | `_misread` → take_back | "Taken back… roll is void. Declare again." | **right** | — |
| 232941 d1 | contradiction / fact / t8 (Lilett vs Lilett) | `_incidental` → player wins, pins the contradiction text on Sevella | "it's taken as you say, and it stays" | right-but-unclear | testimony vs testimony: no outcome picks which line stands |
| 232941 d2 | contradiction / fact (friend) / t8 | `_stored_key(lilett, "friend")` misses the bond, which is on the **PC** (`fact.81 bond.anchor = {kind: friend, npc: lilett}`) → player wins | "it stays" | **wrong** | the record existed and wins. Instead `fact.115 "Lilett won't call herself your friend, yet your sheet lists her as your friend" (…keep it)` went into **all 10 later narrator packets** |
| 232941 d3 | contradiction / pronoun / t11 | `_computed`: record he/him, player said she → explain_with_quote | "As recorded: he/him… The record does not say she." | right-but-unclear | the record is right, but the reply does not say that the earlier "her" lines (turns 7, 8, 10) were the slip. Sevella was "not here" and the view's not-here entries carry name only, no pronouns |
| 233000 d1 | other / other / t8 (garbled Chance line) | `_incidental` → player wins, pins `fact.104 correction.1` on **Dunwen** | "it's taken as you say, and it stays" | **wrong** | no display category; nothing re-rendered; the same line was reprinted at turns 9, 12 and 13; and a UI complaint is now a "keep it" fact about Dunwen in 4 Framer and 4 Narrator packets |
| 233000 d2 | remembered_wrong / pronoun / t8 | `_computed` → correct | "she/her on record; **the narration slipped**… it stays" | **wrong** | the slip is in a stored testimony fact (`fact.103 … "has a hand on him"`), not in narration. That fact is untouched, so the "him" is reprinted |
| 233000 d3 | contradiction / action_reading / t14 | `_misread`: `unseen` (no frame) and word stems `['pres']` → take_back, reverting 578–580, 584–586, 600–601 | "Taken back: … was a misreading; it is undone. Declare again." | right-but-unclear | the effect is right: the G4 should have cost nothing, so undoing the hit is correct. But "misreading" is false, the reverted Vitality and stagger are not shown, and the discarded OFFER (seq 581) and the round (587) are not restored |
| 233000 d4 | ruling_question / roll_or_outcome / t14 | `_ruling` → `_unrolled` → explain | "Nothing was rolled there… **That turn changed nothing on record.**" | **wrong** | computed **after d3's revert in the same report** (`_changes` reads the mutated state); never mentions the G4 or its two cited facts |

Totals: **1 right, 6 right but unclear, 8 wrong.**

### Root causes, in order of reach

| Cause | Disputes | Code |
|---|---|---|
| a. No visible repair: "it stays" after every upheld outcome, with no "Now:" | 9 | `_incidental` and `_computed` reply text |
| b. A pinned correction stores the complaint, not a resolution. `correction.N = believes` is fed back as "(corrected by the player's report; keep it)" to Narrator and Framer. In 232941 it tells the Narrator to keep "Lilett won't call herself your friend". | 7 | `dispute.py:_incidental` |
| c. Subject-only record lookup. A bond on the PC, positions and scenes are never found, so a real record falls into "incidental, player wins". | 192946 d1, d2; 232941 d2 | `_stored_key` |
| d. Missing categories and outcomes: display or render errors (233000 d1, d2), testimony vs record (232941 d2, d3), testimony vs testimony (232941 d1; 192926 d5), a refused (G4) turn (233000 d3, d4) | — | — |
| e. Multi-complaint reports settled sequentially on a mutating state, with no joint answer | 233000 d3 then d4 | `settle_dispute` loop |
| f. Branch order: a `rule_wrong` quantity complaint never reaches the quantity check. Separately, `method_consequences` are not applied to quantities. | 192926 d3 | `_claim` lines 631–633 |
| g. A word-overlap misread heuristic ("pres" in the input, not in the reading) labels a G4 as a "misreading" | 233000 d3 | `_misread` |

### Model or scaffolding
The understand call was accurate in 14 of 15. The exception is 233000 d1, which it labelled `other/other` where its
prompt says a bonus or penalty complaint is `rule_wrong`/`roll_or_outcome`. Every wrong outcome above is code.

### Fit of the proposals
- **`display_error` (acknowledge, re-render, log): partial.** Re-rendering 233000's line prints the same garble,
  because the garble is the stored fact. `testimony.settle` slugs predicate plus value into the predicate
  (`pred = ("said." + slug(f"{predicate} {value}"))[:60]`). `oof.fact_short` prints `slug_words(pred) + ": " +
  value`, and `slug_words` turns `pc` into "you". So "said will give no word out while **you evine oakwell** has a
  hand: **pc.evine_oakwell** has a hand on him". The display error needs a fix at that source, plus a rule that a
  display complaint never writes a world fact.
- **A clear outcome for testimony vs record: yes, for 232941 d2 and d3.** Add testimony vs testimony (232941 d1,
  192926 d5). It also needs cause **c** fixed, or the record is never found and "the record wins" cannot fire.
- **A "Now:" line on every fix: yes for cause a**, and it removes the core of the 233000 d3/d4 confusion if the two
  are answered jointly (cause **e**).
- **Not covered by any proposal:** causes b, e, f and g, and the G4-turn repair. The take-back should restore the
  discarded OFFER and time, or say they are gone.

---

## 6. The Reader rolling the method, not the goal (all runs)

### Data
58 Reader outputs had beats; **24** of them had more than one beat (`saves/*.changes.jsonl` plus the reader
responses). Classified by hand:

| Pattern | Messages | Outcome |
|---|---|---|
| **One social goal toward a person the PC is physically handling, split into grip/force plus talk** | **5 of 5**: 135049 t2; 233000 t2, t5, t7, t11 | the method took the first roll every time. In 233000 t2 and t5 the goal beat was "`no roll: trivial`" (narrator packets t4, t6), so the word was decided by Dunwen's refusal after the player won the grip roll. In t7 and t11 the goal got a second OFFER carrying the self-snags of problem 4. Net for 233000: turns 2–14, 7 rolls, 4 foe hits, 12 Vitality, for "a smaller part" of the word. |
| Movement or looking as the method for one goal, split into move/observe plus goal | 5: 145430 t2; 192926 t7; 192946 t3, t7, t11 | mostly harmless (the move is `no roll: trivial`). One harmful case: in 192946 t11 the roll attached to "Sheathe the sword" and the force-in was lost, which led to the dsp.3 take-back. |
| Genuinely different goals | about 12 | correct splits |
| A question part dropped from a multi-beat message | 192926 t14 ("ask the other carters…"); 192946 t2 ("ask her about the refugees") | noted; outside this brief |

### Cause
`engine/dm/roles/prompts/reader.md:29` says "One beat per distinct act whose failure would not stop the other". A
grip failing does not stop a demand, so they split. The `serves_another_act` purpose is reserved for "a step, turn,
posture or touch". An against-will grip is its own `restrain` change, so it never qualifies.

### Fit of the proposal ("a goal-first Reader")
**Removes the cause for the 5 social splits and for 192946 t11.** Three conditions:
1. **The method must still leave its state.** The hold is real, it should become a condition (problem 1), and an
   arm-wrench harms. Goal-first needs a method-consequence path, "whatever the roll: she stays held", rather than
   dropping the act.
2. **Problem 4 must be fixed first**, or the single goal roll inherits "straining against you" and testimony snags.
3. **Round 5 T2 ("success is willingness")** is needed, or a won goal roll can still be vetoed by a refusal. In
   233000, frame.4's success gave only "a smaller part" because of a willingness clamp.

The smaller input does not bear on this cause. The split rule is in the 5 kB prompt; the rule cards fill the rest
of the roughly 60 kB request.

---

## Proposed solutions, overall fit

| Proposal | Problem 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Goal-first Reader | misses | misses | misses | halves the exposure | — | **removes**, with conditions 1–3 |
| `display_error` | — | — | — | — | partial (needs the source fix in `settle`/`fact_short`) | — |
| Testimony vs record outcome | — | — | — | — | removes 2 of 8 wrong (plus needs cause c) | — |
| "Now:" line | — | **the useful part** | helps the follow-up `/fix` | — | removes cause a (9 disputes) | — |
| Grapple restriction | partial: apply the 06.5.2 condition and implement row 2; no new rule needed | — | — | should come with the tightening lever | — | — |
| Low-Vitality warning | — | misses as worded; contradicts 07.2.3. Use a "this blow staggers, cannot drop" note | — | — | — | — |
| Narrate-then-redirect ordering | — | — | **misses.** Needs an all-refused-is-pure-OOF turn, typed reach factors, no stance-as-fact, and change re-using the offered alternative | — | — | — |

## Differs from Round 5
- **Rules gap:** T5 calls the grapple restriction a rules gap. It is not. The rules have it; the engine models holds
  as text and skips the behavior row.
- **Settlement already exists:** T1 says the PR-12-12 settlement trigger was never built. Trigger (a), `rests_on`,
  *is* built (`settle_triggered`), and it is what turned Dunwen's refusals into established facts. Trigger (b),
  levers, is the unbuilt one.
- **No missing warning:** T5's "low-Vitality warning" is not missing. The rule makes a one-hit drop impossible
  above 0, and the danger card fired on time. The invisible take-back caused the confusion.
- **Not ordering:** T5's "ordering bug" is a G4 that still spends the turn, fed by refusals settled as facts.
