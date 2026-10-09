# I4: what each model call is given, and model size versus instructions

Written 2026-10-09 on `milestone-1-playable` (b9c4a1b). No engine, rules or test file was changed. No harness flag
was needed: `evals/reader_live.py` already takes `--model`, `--set` and `--cache`.

**Evidence:**
- Part A: every `model_calls.request.packet` in `saves/playtest-20261008-*.db`, opened read-only. That is 385 calls
  over 133 turns in 8 saves; the two 214013/214033 saves are empty. Sizes are in characters; a token is about 4
  characters.
- Part B: 276 Claude CLI calls on the owner's subscription: golden 91 + held-out 37 + diagnostic 10, once each on
  Haiku and on Sonnet.

## Summary

- **Part A.** The rule text in a packet is about 70–85% of what a call carries, and most of it is not used by
  that call's output:
  - **Situation cards are padding.** In a `free` scene they are always the same eight cards, picked by the lowest
    chapter number. Examples: The Seer's Reading, The gift circumstance, creature lore, Rank and size. They go to
    the Reader, Narrator, Director and World on every call.
  - **The core is mostly Framer material.** The 10k core goes to every role, the Checker included. Half of it
    (levers, stakes, reach) only the Framer uses. The other half (gate classes) is something code now computes.
  - **The Reader carries cards for decisions it no longer makes.** It gets the gate and roll-test cards (9k) for
    fields that code now computes. It does not get the cards for the fields it does fill: change kinds (01.2.7) and
    the verb covers (T-00-11).
  - **Saving.** Moving to "the situation plus short guidance" cuts input by about 73%: roughly 35k → 9.6k tokens per
    turn.
- **Part B.** The split of goal from method comes from the instructions and the code, not from model size:
  - **Same split rate.** On the 8 lines where a physical act serves a demand, Sonnet split 7 of 8 and so did Haiku.
  - **Same accuracy.** Field accuracy is within noise: verb and gate are equal or slightly worse on Sonnet, while
    question_kind and change_kind are about 5 points better.
  - **Code splits anyway.** Even where a model folds the act into the demand, `reader.normalise` splits it back
    out, because any beat with `against_will` is always its own beat.

## Part A: context audit

### A1. How packets are assembled

- **One builder.** `engine/dm/packet.py::build_packet` serves the Reader, Framer, Narrator, Director, World and
  Checker. The order is: instructions → core (00.15.4: T-12-1, T-00-1, 00.12.3, 00.3.9, 00.3.14, 00.3.15, always
  10,242 characters) → up to 12 cards → the view → the last `pacing.yaml#packet.verbatim_exchanges` (4) exchanges →
  this message.
- **Core goes to every caller.** It is attached on every `build_packet` call, including the Checker, which is not a
  scene role.
- **Card selection.** `engine/retrieve/cards.py::load_cards_for` fills the 12-card cap in this order:
  - the role cards (`ROLE_CARDS`, keeping only cards with a `[J*]` or `[N]` mark);
  - the trigger cards;
  - `extra_ids`;
  - then *situation cards* for the scene's tags and mode.

  `free` mode maps to `situation.social` and `situation.investigation`. Situation cards are sorted by tag depth,
  then whether the tag is derived, then **rule id**. With equal depth, the lowest-numbered cards win every time,
  whatever the message says. That is why 04.6.4, 08.7.2, 09.10.2, 11.3.11, 11.5.3, 15.2.3, 15.3.2 and 15.3.5 appear
  in 72–117 calls each. `conflict` mode does the same with 04.10.2, 06.2.4, 06.4.3 and so on.
- **Testimony, Understand, Locator and Proposer** build a bare `Packet` with no core and no cards.

### A2. Packet size by section (characters, median / p90)

"Blocks" are the bracketed `[RESULT]`, `[OFFER]` and `[NEAR MISS]` record and pause blocks inside the exchanges.

| role | calls | instructions | core rules | rule cards | view | exchanges (of which blocks) | message | total |
|---|---|---|---|---|---|---|---|---|
| reader | 85 | 4390 / 5055 | 10242 / 10242 | **39164 / 40105** | 1673 / 2838 | 3412 / 4415 (87 / 1188) | 112 / 186 | 59253 / 61887 |
| framer | 60 | 4242 / 4245 | 10242 / 10242 | **28313 / 28970** | 4536 / 5183 | 0 | 316 / 593 | 47658 / 48522 |
| narrator | 131 | 5919 / 5942 | 10242 / 10242 | **42606 / 43271** | 6233 / 7152 | 3386 / 4415 (77 / 1189) | 3495 / 4925 ¹ | 72243 / 74682 |
| director | 28 | 3971 / 3971 | 10242 / 10242 | **40554 / 40932** | 2084 / 2451 | 0 | 741 / 1115 | 58078 / 58727 |
| world | 8 | 3086 / 3086 | 10242 / 10242 | **41473 / 41691** | 7358 / 7532 | 0 | 380 / 627 | 62656 / 62929 |
| checker | 20 | 3366 / 3366 | 10242 / 10242 | 7034 / 7114 | 535 / 812 | 0 | 1210 / 2982 | 22677 / 24535 |
| testimony | 31 | 1015 | – | – | 58 / 86 | 0 | 142 / 191 | 1267 / 1327 |
| understand | 8 | 3171 | – | – | – | 0 | 9230 / 11820 ² | 12438 / 15028 |
| locator | 8 | 1382 | – | – | – | 0 | 2419 / 3136 | 3838 / 4555 |
| proposer | 6 | 1516 / 1613 | – | – | 186 / 199 | 0 | 155 / 161 | 1902 / 2002 |

¹ The Narrator's message is mostly the ADJUDICATION RECORD (median 2.1k), SCENE SETTING (1.2k, in 99 of 123
calls), FRESHNESS (0.3k) and the player's words (0.14k).
² Understand gets a TRANSCRIPT of every turn.

Rule text (core + cards) per call is about **50k of 59k for the Reader** (it was 50.3k of 59.9k on fighter turn 7),
53k of 72k for the Narrator, 51k of 58k for the Director, 52k of 63k for the World and 39k of 48k for the Framer.

### A3. How much of the conversation each role sees

| role | exchanges shown | truncation |
|---|---|---|
| reader | the last 4, verbatim: {0: 7, 1: 8, 2: 4, 3: 5, 4: 61} calls | Cut by count, not by characters. 61 of 85 calls had more history than they were shown; older turns reach it only as state (`older_context: state_only`). On fighter turn 7 the exchanges were 2.9k and untrimmed, not 0.45k. |
| narrator | the last 4, verbatim: {0: 16, 1: 12, 2: 6, 3: 9, 4: 88} | Same; 89 of 131 calls had more history. Repair calls do not see the draft they repair (Round 5, T3). |
| framer | 0 | Sees only the beat and the view. |
| director | 0 | **Its prompt says it gets RECENT EXCHANGES.** It sees only `THE PLAYER'S MESSAGE`. |
| world | 0 | **Its prompt says it gets RECENT EXCHANGES.** |
| checker | 0 (the sampled audit passes `turn.exchanges`, which is empty) | **Its prompt says it gets RECENT EXCHANGES.** |
| testimony | 0 | Sees the said words only (by design, PR-12-12). |
| understand / locator | the whole transcript, one line per turn | The only roles that see the full conversation. |

### A4. Do the included cards serve the role's output?

The test: does a field in the role's current schema (`engine/dm/schemas.py`) turn on this card, given the code now
computes the gate, the licence, necessity, the DC and the odds (DL-12-50, spec 007)?

Throughout this section, "core" means T-12-1 (the whole-DM checklist), T-00-1 (invariants), 00.12.3 (gate classes),
00.3.9 (levers and snags), 00.3.14 (stakes) and 00.3.15 (reach).

**Reader.** Its output: parts with class and question_kind, fact_questions with an odds rung, beats (intent,
method, purpose, assertion, shape, target, verb, pressure, three facets, g4_fact, change), clarifying_question,
restatement and rests_on.

| card | chars | used? |
|---|---|---|
| 12.2.2 classifying the message | 8420 | Yes, for classes and facets. The prompt's §1 already restates the decisions; most of the card is pipeline rationale. |
| 01.2.1 intent, method, assertion | 2895 | Yes. |
| 01.2.2 splitting beats | 2189 | Yes. This is where the split rule comes from (Part B). |
| 01.2.4 clarifying, 01.2.5 target | 1505 | Yes. |
| 01.3.8 G0 questions | 1179 | Yes, for fact_questions. |
| 01.15.2 choosing the odds | 3200 | Only when there is a fact question (the odds rung). |
| **01.3.1 gate classification** | 4486 | **No.** Code computes it; only the g4_fact clause is relevant. |
| **01.4.1 roll test** | 4654 | **No.** Code computes necessity. |
| **situation: 04.6.4 Seer's Reading, 08.7.2 gift, 09.10.2 creature lore** | ~11.6k | **No.** |
| **core** | 10242 | **No.** T-12-1 is the whole-DM checklist; 00.12.3 is computed; levers, stakes and reach are the Framer's. T-00-1 is marginal, and its relevant line is already in the prompt's "Never". |
| *missing:* 01.2.7 change kinds, T-00-11 verb covers | – | These are the cards for fields it *does* fill. The prompt carries one-line summaries of each. |

About 19k of 50k is plausibly used. Nearly all of that 19k is already restated as the prompt's decisions.

**Framer.** Its output: anchor, deltas, attribute, deed tag, traits, obstacle, nudge, request_size, levers and
snags, stakes, lethal, reach, asks, threatened cost, form_intent, method_consequences and secret.

- **Role cards: used.** All 11 (01.5.1, 01.5.3, 01.6.1, 01.6.2, 01.6.3, 01.6.5, 01.6.8, 01.6.9, 01.6.10, 01.6.11,
  01.13.1; 28k) map one to one onto fields. The one situation slot goes to a verb card (01.18.x, about 1.5k),
  which is useful for the anchor.
- **Core: duplicated or unneeded.** Its 00.3.9, 00.3.14 and 00.3.15 (4.3k) duplicate 01.6.8–01.6.10. T-12-1,
  T-00-1 and 00.12.3 are not needed.
- **Missing.** 15.3.2 request size (talk only) and 01.4.7 secret; the prompt summarises both.
- **What is used.** About 30k of 38.5k. This is the one role whose cards match its job. Even so, each card is
  roughly half `[D]` text that code runs, so a per-field digest would carry the same judgment in about 6k.

**Narrator.** It writes sentences with refs, about, new, atmosphere and speaker, plus repairs.

- **Role cards: used.** 12.14.2 (no unestablished details), 12.14.3 (the player owns the character), 12.14.13
  (the content tiers for `new`) and 00.6.6 (write-on-mention): 10.1k.
- **Situation cards: not used.** The eight cards (32.5k) are social subsystem rules and an ability's voice. The
  Narrator decides nothing they cover: refusals, request size and terms arrive as record lines. The Seer's Reading
  matters only on a turn when that ability is used, and then it should come in as an `extra_id`.
- **Core: not used.** The relevant part of T-12-1's T10 line is already in the prompt.
- **What is used.** About 10k of 53k.

**Director.** Its output: cut_now, next_scene (mode, place, agenda, hoped answer, pillar, challenge type, cast,
new_npc), push and lead.

- **Role cards: used.** 12.4.2, 12.4.3, 12.9.1 and T-12-7: 7.8k. The prompt restates all but T-12-7's list.
- **Not used.** The eight situation cards (32.7k) and the core.
- **What is used.** About 8k of 51k. The judgment it most needs is "is the player still pursuing this?", and it
  sees **no exchanges**.

**World.** Its output: per NPC, want_engaged, refusal_engaged and table tags.

- **Role cards: used.** 12.11.5 and 12.2.9: 3.5k.
- **Situation cards: partly used.** 15.2.3 Refusals (4.4k) is relevant to refusal_engaged. 15.4.1 and 15.4.2 are
  marginal. The other six (about 28k) are not used.
- **Core: not used.**
- **What is used.** About 8k of 52k.

**Checker.** Its output: claims, undeclared, unexpressed and the screen flags.

- **12.3.1 (7.1k): used** for the claim classes. The prompt restates the class list.
- **Core (10.2k): not used.** The Checker judges no gate, stakes or reach.

**Testimony, Understand, Locator and Proposer.** They get no rule text; they already follow the target pattern.

### A5. Recommendation per role ("better context, not more rules")

The rules are the specification the code implements. A model call gets the situation, plus short guidance for the
one judgment it makes. Concretely:

1. **Stop tag-driven situation cards** (`load_cards_for` step 4) for every role. A subsystem card reaches a call
   only when code knows it applies: for example, `extra_ids` from the anchor's rule, the PC's ability in use, or a
   Talk frame's 15.3.2. Situation-by-tag is a retrieval heuristic, and today it degenerates into "the lowest-numbered
   social cards".
2. **Drop the 00.15.4 core from every model packet.** It is the DM checklist that the code pipeline now *is*. Keep
   the one or two lines that apply (for example "never let an assertion become a fact") in the role prompts, where
   most already are.
3. **Per role:**

| role | keep | drop | add | est. chars (now → after) |
|---|---|---|---|---|
| reader | prompt, slim view, testimony list, message | core, all 12 cards | 4 → 6 exchanges (cheap, ~0.85k each, and this is where targets and "she already told me" live); ~1k for change kinds and verb covers; **the beat rule rewritten for goal and method** (Part B) | 59k → ~11k |
| framer | prompt, view, anchor menu, beat | core, the card bodies | one ~6k per-field digest generated from the cards' `[J*]` clauses: the verb's obstacle-class examples, the cost menu for the threatened source, the request-size rungs on Talk | 48k → ~15k |
| narrator | prompt, view, record, scene setting, speaker card, 4 exchanges | core, the 8 situation cards | a ~1.5k content-tier list (12.14.13) in the prompt; **the draft in repair calls** (Round 5, T3) | 72k → ~20k |
| director | prompt, view, raised items, places | core, the 8 situation cards | T-12-7's nine challenge types inline (1.2k); **the last 2 exchanges**, as its prompt promises | 58k → ~10k |
| world | prompt, view, what happened | core, the 9 situation cards | the last exchange; the refusal test from 15.2.3 as one line | 63k → ~12k |
| checker | prompt, ids, sentences | core | either the last exchange or a prompt that stops claiming one; keep or compress the 12.3.1 class list (~2k) | 23k → ~7k |
| testimony, understand, locator, proposer | as is | – | – | unchanged |

### A6. Token and cost change

Estimated on the 133 recorded turns (characters ÷ 4). Prices are the repo's table in `engine/llm/budget.py`.

| | input per turn | cost / 100 turns, Gemini 3.8 Flash ($0.75/M in) | Haiku 4.5 ($1/M) | Sonnet (repo table, $2/M) |
|---|---|---|---|---|
| now | ~140k chars ≈ **35k tokens** | $2.93 | $3.91 | $7.82 |
| after A5 | ~38k chars ≈ **9.6k tokens** (−73%) | $1.03 | $1.37 | $2.74 |

Per role, input per turn:

| role | now | after |
|---|---|---|
| narrator | 66.7k | 19.5k |
| reader | 35.0k | 6.9k |
| framer | 21.1k | 6.7k |
| director | 9.1k | 2.0k |
| world | 3.8k | 0.8k |
| checker | 2.8k | 1.0k |

Output (about 0.8k tokens per turn) is unchanged and is included in the costs above.

**Caching changes how much of this is money.** About 85% of today's input is a stable prefix (instructions, core,
role cards). With perfect prompt caching at 10% of the input price, today's effective input is about 8.2k tokens
per turn, against about 6.6k after the change: roughly **20% saved in dollars, rather than 65%**. The CLI saves
record `tokens_in = 2` and `cost_usd = 0`, so the actual caching cannot be read from these saves.

The larger gains are **latency** (60–75k characters per Narrator call) and **attention**. Today about 40k
characters of unrelated subsystem rules sit between a role's instructions and the situation it is judging.

**Validation before adopting.** Rerun `evals/reader_live.py` with an empty card list (a ~10-line packet switch in
the harness) on Haiku: 128 calls. Accept the change if verb, gate and change_kind hold within noise. I did not run
this, to stay within the call budget.

## Part B: model size versus instructions (Reader)

**Method.** The same prompt (`reader.md` at b9c4a1b), schema, packet (`reader_live.packet`: role cards plus core,
with the context as the view) and code (`normalise`, `now_beats`, `compute_gate`) were run on both models:

```
py -3.12 evals/reader_live.py --model {haiku,sonnet} --set {golden,heldout} --cache <scratch>
```

The Haiku baselines in `evals/baselines/` predate the spec 015, 017 and 018 prompt changes, so Haiku was run fresh.
There was one run per model per set.

### B1. Per-field accuracy

One line is about 1.1 points on the golden set and 2.7 points on the held-out set. With a single run each, verb and
gate differences under about 3 points are noise.

| field | golden Haiku | golden Sonnet | held-out Haiku | held-out Sonnet |
|---|---|---|---|---|
| verb | **91.2%** (83/91) | 90.1% (82/91) | 94.6% (35/37) | 94.6% (35/37) |
| gate | **97.8%** (89/91) | 94.5% (86/91) | 94.6% | 94.6% |
| against_will | 92.5% (62/67) | **95.5%** (63/66) | 100% | 100% |
| uses_power | 100% | 100% | 100% | 100% |
| speech | 95.5% | 95.5% | 100% | 100% |
| question_kind | 87.9% (80/91) | **93.4%** (85/91) | 86.5% (32/37) | **91.9%** (34/37) |
| change_kind | 88.1% (59/67) | **93.9%** (62/66) | 100% (22/22) | 100% (22/22) |
| negation pairs, verb | 90.9% | **100%** | 100% | 100% |

- **Where Sonnet loses.** Most of its verb and gate misses are SPEECH read as Talk. In g026 and g033 it reads
  pressure into plain questions, which the policy (C1) labels SPEECH. Those are judgment calls against a policy
  line, not capability errors.
- **Where Haiku loses.** Its misses are capability-shaped: g071 "I don't pick the lock. I knock" became Strike, and
  g080 "pour the draught when he looks away" became Handle, not Sneak.
- **Both fail h016 and h019 the same way.** They treat a casual look ("without making a show of it", "as I sit
  down") as an Observe beat.
- **Net.** Sonnet is a little better on reading questions and changes (+5 to +6 points), and no better on verb and
  gate.

### B2. Multi-beat cases: does Sonnet also split goal from method?

The golden and held-out sets have 14 lines where either model returned two or more beats. Of those, 6 are "a
physical act serving a demand" (g014, g015, g049, g050, g054, plus g055, which keeps an existing grip). I added 10
diagnostic lines from these playtest transcripts:
- 20261008-233000 (the Dunwen arm twist),
- 20261008-135049 (Eliia),
- 20261008-192946 (refugees, cell door),
- 20261008-145430 (Murzak's purse),
- 20261008-192926 (coin on the table),
- 20261008-145410 (Ysrion).

Each line was labelled by intent **before any answer was run** (Appendix). The diagnostic file lives in scratch,
not in the golden set.

**Lines where a physical act serves a demand** (the goal is the words' demand; the act is the method). Beats are
the engine's now-beats after `normalise`:

| id | line (short) | Haiku | Sonnet |
|---|---|---|---|
| g014 | grab the token, stare him down, "who gave…" | 2 (take; learn) | 2 (take; learn) |
| g015 | grab his collar, "don't lie to me…" | 2 (restrain; learn) | 2 (restrain; learn) |
| g049 | shove her against the gatepost, "who's hiring…" | **1** (Talk with against_will → Grapple; learn) | 2 (restrain; learn) |
| g050 | clamp her mouth, drag her behind the stack, "Quiet…" | 3 | 2 |
| g054 | grab his boot, "hear me out" | 2 | 2 |
| d01 | **twist her arm up behind her back: "The word, Dunwen."** | 2 (restrain; persuade_to) | 2 (restrain; learn) |
| d02 | grab Eliia's sleeve and demand to know who the rider was | 2 | **1** (Talk with against_will; learn) |
| d03 | wrench the arm higher: "all of it, or I break it" | 2 ³ | 2 (harm; learn) |
| **kept as one goal** | | **1 of 8** | **1 of 8** |

³ Haiku marked the wrench `serves_another_act`, a merge. `normalise` overruled it, because a beat with
`against_will` "is always its own beat". So Haiku's *model* merged 2 of 8, and Sonnet's merged 1 of 8.

**Other diagnostic categories** (intent beat count correct):

| category | lines | Haiku | Sonnet |
|---|---|---|---|
| object as method (sword point, a coin slid across) | d04, d09 | 2/2 | 2/2 |
| movement serves the act (slip through the crowd to lift a purse; step close to talk) | d06, d10 | 2/2 | 2/2 |
| two real goals (purse and punch; shove away then strike; kick the door, then demand) | d05, d07, d08 | 2/3: d05 got 3 beats, splitting off "shove in" as a Move | 2/3: d05 made the demand *conditional* on the door, so 1 now-beat (a defensible reading) |
| **all 10 diagnostic lines** | | **6/10** | **7/10** |

**What the two models do the same:**
- **The simple cases are fine.** Both keep the method with the goal when the method is an object (a sword, a coin)
  or a step.
- **Both split a bodily act from the words it serves,** in almost the same proportion.

**What Sonnet does differently:**
- **Its intents are phrased more consistently.** It writes "make Dunwen tell the word", while Haiku writes "Dunwen
  tells…" or "persuade_to".
- **It is better at sequencing.** In d05 it made the demand conditional on the door.

### B3. Conclusion: instructions or model size?

**Mostly instructions and code; model size barely matters.** Three layers each tell the Reader to split, and the
models comply:

1. **The prompt says so twice.** "One beat per distinct act whose failure would not stop the other" and "Two
   changes are two beats". A twisted arm can fail while the demand is still spoken, so the test says split. `restrain`
   and `learn` are two changes, so they are two beats.
2. **The code says so.** `reader.normalise` never folds a beat with `against_will` or `uses_power` into the act it
   serves. A model that merges (Haiku on d03) is split back out.
3. **The labelling policy says so.** `evals/reader_golden_POLICY.md` B5 says "touching a person … against their
   will is its own beat … even when words follow". So the golden set *rewards* the split, and a prompt tuned on it
   learns to split.

Sonnet, under the same three layers, splits 7 of 8, exactly like Haiku. Its gains (question_kind and change_kind,
about +5 points) are real but small, and they do not touch this behaviour. I estimate **about 90% instructions and
code, about 10% model**. The model share is the occasional merge, which code then undoes anyway.

**If the owner wants "twist her arm: the word!" read as one goal with a coercive method**, change all three layers
together:
- **Prompt.** Replace the failure test with a goal test, for example: "One beat per thing the player wants to end
  up true. An act done only to make someone comply (a twist, a grip, a blade at the throat) is the method of that
  demand, not a beat of its own, unless the player wants it as an end in itself (to hold them, to take, to hurt)."
- **Code.** Let `normalise` fold an `against_will` beat marked `serves_another_act` into the Talk beat it serves,
  and keep `against_will` on the merged beat. The covering verb then becomes Grapple or Force through
  `covering_verb`, which already maps Talk + against_will.
- **Policy.** Revise B5 and relabel the golden lines it governs (g014, g015, g049, g050, g054) blind, before
  rescoring.

Haiku already produces the merged form unprompted on g049, g055 and d03. The capability is there; the
instructions point the other way.

Running Sonnet as the Reader would cost about twice as much per input token in the repo's table, plus latency, for
a gain of about 5 points on two fields. That is not worth it for this question. Revisit if change_kind accuracy
becomes the bottleneck.

## Appendix: diagnostic lines (labelled before the run)

Context strings are abbreviated; the full lines are in the scratch file `i4_diag.jsonl` (session scratchpad).

"Literal" is the beat count the prompt text implies when read literally.

| id | category | line | intent beats | literal | goal kind |
|---|---|---|---|---|---|
| d01 | act serves demand | I twist her arm up behind her back and hiss, "One more swing and I'll break it. The word, Dunwen." | 1 | 2 | learn |
| d02 | act serves demand | I grab Eliia Terence by the sleeve and demand to know who the rider was, and who the message was for. | 1 | 2 | learn |
| d03 | act serves demand | I wrench the arm higher. "The rest of it, Dunwen. All of it, or I break it." | 1 | 2 | learn |
| d04 | object as method | I point my sword at the nearest refugee and say: "Tell me your story…" | 1 | 1 | learn |
| d05 | two goals | I kick the cell door open and shove in, sword drawn, demanding the prisoner tell me what he knows. | 2 | 2 | open, learn |
| d06 | move serves act | I slip through the crowd toward Murzak Red-Hand and try to lift his coin purse… | 1 | 1 | take |
| d07 | two goals | I grab the purse with my free hand and punch her again. | 2 | 2 | take, harm |
| d08 | two goals | I let go of her arm and shove her hard away, then draw steel. "Fine…" I go for her with a strike. | 2 | 2 | move_to, harm |
| d09 | object as method | I slide a coin across the table and ask if she'd tell me where the barrels are loaded. | 1 | 1 | learn |
| d10 | move serves act | I step close and lower my voice. "Then let's go somewhere quieter, Ysrion… What if I pay for your time?" | 1 | 1 | persuade_to |

**Raw answers.** The session scratchpad holds `golden_{haiku,sonnet}.jsonl`, `heldout_{haiku,sonnet}.jsonl` and
`i4_diag_{haiku,sonnet}.jsonl`. To score cached answers without new calls, run
`py -3.12 evals/reader_live.py --cached --cache <file>`. The audit script is `audit.py` in the same scratchpad.
