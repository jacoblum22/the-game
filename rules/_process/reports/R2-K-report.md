# R2-K report: round-7 rules wave (T1-T7, D2 A, D3 A, P2, P3)

Revision R2-K. Rule edits tagged `[revision: R2-K]`. Source: ROUND7-PLAN.md (owner-approved 2026-10-09);
ROUND7-ANALYSIS.md §2, §6; constitution VIII. Appended after every step.

## Progress
- Setup: worktree reset to milestone-1-playable (9fb9375). Read ROUND7-PLAN in full, ROUND7-ANALYSIS §2 and §6,
  constitution VIII (lines 408-471), R2-J report. DL-00-07 exists (decision-log.md's DL-00 head). Baseline
  validator 0 ERROR / 0 WARN.
- Survey: read by id 01.2.7, 01.3.1, 01.3.5, 01.3.8, 01.4.1, 01.4.4, 01.4.5, 01.4.7, 01.6.8, 01.6.9, 01.6.10,
  01.7.4, 01.8.2, 01.9.3, 01.15.1, 01.15.8, 02.4.6, 08.8.8, 11.5.6, PR-11-5, 12.2.4 (role table, profiles),
  12.2.6, 12.3.6, 12.5.8, 12.6.1, 12.6.2, T-12-4, 12.10.6, 12.10.8, 12.11.1, 12.11.3, 12.11.4, 12.11.5, 12.11.9,
  12.14.11, 12.14.12, 12.15.2, 12.15.4, 12.16.16, PR-12-1, PR-12-2, PR-12-10, PR-12-11, PR-12-12, 15.3.10, 15.9.5,
  PR-15-6; DL-01-32, DL-01-36; `pacing.yaml` (npc, narration.freshness, feedback, answer_ladder, testimony),
  `resolution.yaml` (take_the_time, auto_commit, intended_change), `oracles.yaml#tbl.npc_voice_habit`. Traces
  grepped: I3 §1-4, H1 (habit exemption, usage marks fired 0 times), H2 T6 (the 7 OFFERs, Morga's subset ask,
  0c15da2), I1 symptom 1. "Explain only at an open OFFER" and the incident line exist only in the engine; the rule
  side is PR-12-11 and 12.16.16.
- Ch.01 and ch.02 (scratch `e01.py`, 17 asserted edits): 01.2.7 step 1 (every rolled beat has a typed goal, T5;
  "already agreed" includes a larger act on record, T6); 01.3.1 (embedded facts about the target never go to the
  Oracle, T1; gates key on the goal and its method, T5); 01.3.5 (a fallback framed on its own scope); 01.4.1
  (COSTLY computed on the typed frame with the stakes-vs-costs check; already true judged on the typed goal);
  01.4.4 (take the time decided by code, every verb, time charged; fallbacks provisional); 01.4.7 (secret frames
  keyed on the goal; nothing at stake takes the time); 01.6.8 (an Oracle answer is never a snag); 01.6.10 (Limited
  only with a cited factor, P2); 01.7.4 (auto-commit only for Safe frames that stay costly); 01.9.3 (no price
  reverses the goal; the effective degree, T4); 01.15.1 (one owner per question); 01.15.8 (never a snag, plain
  label); 02.4.6 (Letters on any reading, whatever the verb).
- Ch.12, 11, 15 (scratch `e12.py`, 46 asserted edits; `e12b.py`, 1 fix): T1 in 12.6.1, T-12-4 (two new rows; the
  Oracle row narrowed), PR-12-1 T4; OFFER 12.15.2 (plain-word labels, no "+0" or generic "practised", title always
  from a typed goal, Limited names its factor, Safe frames say what failing badly costs, fallback on its own scope)
  and 12.15.3 (take the time shows its time; "hidden check made" only after a roll); T2 in 11.5.6, PR-11-5 (terms
  written at making), 12.16.16 (data, not sentences), PR-12-12 (guards; no yes/no for what/where/how much), 12.2.4
  Director row (cast a description); D2 in 12.10.8 item 1, PR-12-10 step 1, 15.9.5, PR-15-6 step 3 (`about` line);
  D3 + P3 in PR-12-10 steps 2-3, 12.10.8, 12.11.4, 12.11.9 steps 3-4; T3 in 12.11.3, 12.11.9 step 4, 12.14.11
  (rewritten: no usage marks, no quote-back, the scan logged only), 12.2.4 (profiles, narrator row), PR-12-1 T12,
  12.11.1 (real pronouns in code text); T4 in 12.2.6, 12.14.12, PR-12-2; T7 in 12.2.4 Fixer row, 12.3.6 item 4,
  PR-12-11 steps 2-6 and retires, 12.5.8 item 1; 15.3.10 (certain talk keyed on the goal); 15.7.1 (typed deal price).
- Ch.00 (scratch `e00.py`, 5 edits): 00.6.6a items 3 and 5 (usage marks retired; view order by salience then newest);
  12.14.11 "said record is a usage mark" reworded; the World row's "usage marks" dropped.
- Data (scratch `edata.py`, 11 edits; YAML parses): `pacing.yaml` npc (`habit_max_per_scene` marked retired, kept
  until spec 024; `habit_phrasing: occasional`), narration.freshness (`usage_marks`, `quote_back` retired;
  `repetition_scan: log_only`), dm_questions (two rows; the Oracle row's `never_about`/`never_for`), answer_ladder
  (`clue_judgment`, `willingness_holds`, `willingness_changes_on`, `refusal_pointer`, `willingness_line_never_on`),
  testimony.guards, feedback.investigate (`rerender_display` marked retired; `proposals_added`, `dry_run`,
  `check_screen`, `sees`, `mechanics_digest`, `open_offer`, `code_guards`, `scored_on`); `resolution.yaml`
  take_the_time (computed test, stakes check, time charged, fallback provisional), auto_commit (`only_when_costly`),
  intended_change.before_framing (`already_true_judged_on: typed_goal`, `rolled_beat_needs_goal`);
  `investigation.yaml` placement `about`; `oracles.yaml#tbl.npc_voice_habit` 20 rows worded "now and then", plus a
  `rule` line. No key the engine reads was removed.
- Decisions and ledger (scratch `edl.py`, `edl2.py`): DL-01-41..48 (DL-01.md), DL-12-108..121 (DL-12.md), DL-15-40..42
  (DL-15.md), DL-00-08 (decision-log.md's DL-00 head, after DL-00-07). Owner quotes only from ROUND7-PLAN §Owner
  rulings; T5, T6, P2 and P3 carry no quote (approval recorded, no direct words). Each entry has a checkable
  "Revisit if". Revisit notes re-checked (owner process ruling): `Revisited`/`Amended` lines on DL-01-32,
  DL-01-36, DL-12-90, DL-12-99, DL-12-105 (summary in DL-12-111). Ledger I-205..I-219 (I-219 resolved; the rest
  open: rules done, engine specs pending; I-214 provisional).
- Close: re-assembled the appendix (`integration-assemble-appendix.py`), compiled anchors (129; 0 errors, 0
  warnings), compiled cards last (2133 cards, core 6). Validator: **0 ERROR / 0 WARN** (INFO only: BASIS 1, POOLS 2,
  REFS-EX 9, REFS-MD-EX 70). Engine tests: 1803 passed, 4 skipped, 1 failed:
  `tests/replay/test_recorded_games.py::...[offline_seed11]` diverges because the Framer's GUIDANCE digest carries
  revised card text (39032 -> 39259 chars). That is the intended effect of a rules wave; re-recording
  (`python -m tests.replay.record_games`) is outside this lane (tests/ untouched) and belongs with spec 023.
- Not committed: the operator instructions and CLAUDE.md say "never commit; the orchestrator commits", which
  overrides the wave brief's commit step. The work is uncommitted in the worktree.

## Ids touched
- Rules: 00.6.6a (items 3, 5); 01.2.7, 01.3.1, 01.3.5, 01.4.1, 01.4.4, 01.4.7, 01.6.8, 01.6.10, 01.7.4, 01.9.3,
  01.15.1, 01.15.8; 02.4.6; 11.5.6, PR-11-5; 12.2.4 (profiles; Narrator, World, Director, Fixer rows), 12.2.6,
  12.3.6, 12.5.8, 12.6.1, T-12-4, 12.10.8, 12.11.1, 12.11.3, 12.11.4, 12.11.9, 12.14.11, 12.14.12, 12.15.2, 12.15.3,
  12.16.16, PR-12-1 (T4, T12), PR-12-2, PR-12-10, PR-12-11, PR-12-12; 15.3.10, 15.7.1, 15.9.5, PR-15-6. Ch.13 untouched.
- Data: `pacing.yaml`, `resolution.yaml`, `oracles.yaml` (tbl.npc_voice_habit), `investigation.yaml`;
  `anchors.yaml` and `engine/build/cards.json` regenerated.
- Decisions: DL-00-08; DL-01-41..48; DL-12-108..121; DL-15-40..42. Revisit lines on DL-01-32, DL-01-36, DL-12-90,
  DL-12-99, DL-12-105. Ledger: I-205..I-219.
- Unused from the allotted ranges: DL-12-122..125, DL-15-43..44, DL-00-09..10, I-220.

## What each change retires (each rule says it)
- T1: pre-frame Oracle questions about the target, `_KNOWS_Q`, Oracle booleans for content, d100 snags, slug labels.
- T2: hooks with no terms; yes/no answers to what/where/how much; random walk-ons for a stated purpose; the regex
  price; word-overlap case routing (D2).
- T3: the habit as forced callback and in refusal lines; the once-per-scene cap; `last_used` marks and the ten-turn
  gate; the quote-back; `incident_line`; verbatim faction labels; pronoun-neutral templates.
- T4: degree-only checks; "a near miss" before the choice.
- T5: rolled `change: none`; verb-only gate keys; the hold-only success guard; description-first titles; double-counted
  fallback difficulty.
- T6: rolling every gated beat; "hidden check made" with nothing at stake; the 60% overlap; the forced fallback roll
  (provisional); auto-commit for Safe frames that take the time.
- T7: `rerender`; "explain only" at an open OFFER; the entity tool without licences; tuning-set scoring.
- D3: per-topic willingness re-rolls; redirect loops. P2: "+0", generic "practised", "a smaller part of it",
  Limited by default. P3: the willingness line on a greeting.

## Engine checklist per spec
Each spec labels every case below **made-up** or **edge** (owner rule, DL-00-08), adds its own, and is accepted on
them plus a held-out set.

**Spec 023 (T1 + T5 + T6 + P2)**: `engine/resolve/` (gate, necessity, frame, pipeline, change), `turn.py`'s fiction
questions, `oof.py`, Reader and Framer prompts.
- Cite: 01.15.1, 01.15.8, 01.3.1, 01.6.8, 12.6.1, T-12-4, PR-12-1 T4; 01.2.7, 01.3.5, 01.4.7, 01.9.3, 02.4.6,
  15.3.10, 12.15.2; 01.4.1, 01.4.4, 01.7.4, 12.15.3; 01.6.10. DL-01-41..47, DL-12-108, DL-12-121, DL-15-41.
  `resolution.yaml#take_the_time`, `#auto_commit.only_when_costly`, `#intended_change.before_framing`
  (`already_true_judged_on`, `rolled_beat_needs_goal`); `pacing.yaml#dm_questions`.
- Build:
  - drop any fact question whose subject is the beat's target or a person present; will goes to willingness,
    ability to the record (licences, role), noticing to the roll;
  - an Oracle fact is stored positive and whole with a plain label; `frame_check` refuses it as a snag;
  - every rolled beat has a typed goal (Help carries the helped goal; a look is `learn`);
  - gates on the goal plus every method it relies on: Letters on any reading of writing; certain talk on
    `persuade_to`; secret frames on a `learn` goal;
  - the 01.9.3 check rejects any price that reverses the typed goal against the same target;
  - an accepted fallback is framed on its own scope, its shift counted once;
  - `necessity()` computes COSTLY from the typed frame (stakes source, sourced cost, listening clock, conflict,
    tier, retry), with the stakes-vs-costs check; take the time charges `advance_time` and prints its RESULT line;
  - `agreed` records carry person, act, size; a same-or-smaller ask is already true; a roll never shrinks one;
  - auto-commit only for Safe frames that stay costly;
  - OFFER: no 0 terms, no generic "practised", Safe frames state failing badly's cost and chance, Limited names its
    factor.
- Retire: `_KNOWS_Q`; `turn.py:421`'s `[:60]` slug; `oof.py:234`'s negation; Oracle facts as snags; verb-only keys
  (`gate.reads_writing` on `verb.observe`, `certain_talk` on `verb.talk`, verb-keyed secret frames); rolled
  `change: none`; description-first titles; the 60% overlap `already_true`; 0c15da2's forced fallback roll
  (provisional, DL-01-46); "a smaller part of it (…)". Re-record the `tests/replay` games.
- Cases:
  - made-up: the blacksmith asked to mend a sword: no "can he work iron?" coin flip; no "can't work iron -2".
  - made-up: an old friend saved last week asked for help: willingness from standing, never an Oracle "willing?".
  - made-up: "I sweet-talk the clerk and sneak a look at the ledger" by a PC without Letters: the reading is gated.
  - made-up: "I shoulder past the guard to reach the door": typed `move_to`; success moves the PC.
  - made-up: searching your own empty room for a ring; practising on a dummy; reading your own book at leisure: no
    OFFER, no roll, time charged.
  - edge: the Framer says `stakes.source: none` but threatens `closed_door` sourced to an NPC fact: costly, rolls,
    logged.
  - edge: a take-the-time candidate at Very hard, and a fallback whose +10 shift lands at Very hard: both roll.
  - edge: Morga agreed to "hear the refugees"; "sit and listen" is already true; a larger ask rolls, and its limited
    success leaves the first agreement standing.
  - edge: the player's own "is there a rope in the loft?": Oracle allowed; a lever next beat, never a snag.
  - edge: a lock-pick near miss priced "the guard hears you": legal; "the lock jams shut again": refused, re-priced.

**Spec 024 (T3 + T4 + P1, P4-P6)**: `packet.py`, `narrator.py`, `narration.py`, `npc_layer.py` voicing,
`answer.py` degree, `scene_state.py`, `incident.py`, NPC template tables.
- Cite: 12.11.3, 12.11.9 step 4, 12.14.11, 12.2.4 (profiles, Narrator row), 00.6.6a items 3 and 5, PR-12-1 T12,
  12.16.16, 12.11.1; 01.9.3, 12.2.6, 12.14.12, PR-12-2. DL-12-113, DL-12-114, DL-12-115, DL-01-48.
  `pacing.yaml#npc.habit_phrasing`, `#narration.freshness` (`usage_marks`, `quote_back` retired; `repetition_scan:
  log_only`); `oracles.yaml#tbl.npc_voice_habit`.
- Build: one `effective_degree()` read by `npc_layer.py:570`, `answer.py:271`, `scene_state.py:160` and the
  willingness and refusal voicing; a paused beat carries no degree in the narrator record; looks and habits as
  background data (not on every `present:` line after framing); habit rows "now and then"; refusal lines without the
  habit (`npc_layer.py:491`); the incident and factions as data; templates with stored pronouns; the repetition scan
  (images, openings, closings) logged only. P1: `narration._text` keeps paragraphs. P4: `_withheld`'s suffix only on
  refusals. P5: "the any posted notice", the notice separator, pronoun-check precision in tags, `READING` precision.
  P6: demote offline narration metrics.
- Retire: `incident_line`; the raw `voice`/`detail` push; the habit in `voiced_refusal`; `used_details` and
  `last_used` marks; the freshness quote-back (`narrator.py:379-400`); pronoun-neutral strings; "result: failure, a
  near miss" before the choice; degree-only checks. Then delete `habit_max_per_scene` and the retired freshness keys.
- Cases:
  - made-up: an innkeeper who "wipes the bar with a rag" over ten turns, including while the inn burns: nothing
    pushes the image; the logged scan measures it.
  - made-up: "The Order of the Grey Hand": the narrator gets name and role as data, never "the officer of ...".
  - made-up: a lock barely missed, "succeed, but the guard hears you": the door is open and the guard reacts to it.
  - edge: an unnamed he/him walk-on: every code template says he/his, never "call them".
  - edge: a near-miss pause, then the player declares something new: the default failure is narrated only once it
    applies.
  - edge: "what did the notice say again?": honoured, not treated as repetition.
  - edge: the narrator uses a habit twice in one scene knowingly: nothing gates or redrafts it.

**Spec 025 (T2 + D2 + D3 + P3)**: `engine/gen/` (hooks, `case.py`), `answer.py` routing, `npc_layer.py`
willingness, `world/social.py`, `director.py`, testimony guards.
- Cite: 11.5.6, PR-11-5, 12.16.16, PR-12-12, T-12-4, 12.2.4 (Director row), 15.7.1; 12.10.8, PR-12-10 steps 1-3,
  15.9.5, PR-15-6; 12.11.4, 12.11.9 steps 3-4. DL-12-109, DL-12-110, DL-12-112, DL-12-118, DL-12-119, DL-12-120,
  DL-15-40, DL-15-42. `pacing.yaml#answer_ladder` (`clue_judgment`, `willingness_holds`, `willingness_changes_on`,
  `refusal_pointer`, `willingness_line_never_on`), `#testimony.guards`; `investigation.yaml` placement `about`;
  `economy.yaml#job_fees`, `#price_bands`.
- Build: hook terms at creation (pay by band, destination, issuer, people) as unsealed knowledge on the cards of those
  who'd know; the speaker card shows others' `said` on the topic; price settlement from the band; a heard place
  becomes a site on travel; the Director casts a description; a deal's price record; the D2 call (question,
  exchange, placement `about`; uncertain yes; code hands the clue over); willingness set at talk start and held,
  moved only by payment, threat, insult or a won persuasion; the refusal pointer; no willingness line on a greeting
  or thanks.
- Retire: `case_about` word overlap; random walk-ons for a stated purpose; the regex price from Framer prose; yes/no
  Oracle answers to what/where/how much; per-topic willingness re-rolls.
- Cases:
  - made-up: "Reward for the missing ferryman": the ferry-keeper asked how much, who posted it, where he was last
    seen: pay, issuer and place are written; other details improvised and consistent across speakers.
  - made-up: the widow asked "Did he have enemies?" holds "he owed the toll-keeper money": judged yes, delivered,
    with no shared word needed.
  - made-up: a lead says "refugees came in": the Director casts "the refugees" in the temple scene.
  - edge: the widow asked about the weather at the ferry: judged no; nothing leaks; answered in words.
  - edge: everyone who would know has already refused: the pointer casts someone new or gives the stuck answer
    (12.8.5), never a loop.
  - edge: a merchant says "ten silver for the map", far outside the band, and the PC pays: settled from the band.
  - edge: Guarded, then the PC pays a coin: the band moves; a new topic does not re-roll; a recorded refusal on "his
    son" still refuses that topic only.
  - edge: "Thanks, friend": no willingness line, no refusal voicing.
  - edge: a Guarded holder of a core clue with no refusal covering telling: the clue is delivered.

**Spec 026 (T7)**: `fixer.py`, `dispute.py`, fixer tools and prompt, `evals/feedback_corpus.py`.
- Cite: PR-12-11 steps 2-6 and retires, 12.3.6 item 4, 12.2.4 (Fixer row), 12.5.8 item 1, OEQ-12-26. DL-12-116,
  DL-12-117, DL-12-111. `pacing.yaml#feedback.investigate` (`proposals_added`, `dry_run`, `check_screen`, `sees`,
  `mechanics_digest`, `open_offer`, `code_guards`, `scored_on`).
- Build: one shared people card for every role and the Fixer; plain-word facts; the turn's model inputs and outputs
  as a tool; dry-run on a snapshot copy; `reframe` for an OFFER on screen; take back an unrolled pending turn; check
  the repaired screen and iterate within `max_steps`; the mechanics digest; code validates only the spine; scoring on
  fresh held-out complaints including open OFFERs, by a scorer that checks the repaired screen.
- Retire: `rerender` (then delete `rerender_display`); explain-only at an open OFFER (spec 014); the entity tool that
  hides licences; outcome-class scoring on the tuning set.
- Cases:
  - playtest: "Belie can't read, but you want me to persuade her to read", at the open OFFER: re-framed with her
    Letters; the new screen no longer asks it.
  - made-up: "the guard should know me, I'm a captain of the watch": the Fixer sees the rank and acts on evidence.
  - made-up: "I paid for the round, why did he refuse?": a dry-run with the effective degree shows acceptance; the
    repair is applied and the screen checked.
  - edge: "I should have 50 more gold" with no ledger evidence: refused by the spine guard, explained plainly.
  - edge: a re-frame that still shows the complaint: iterates within budget, then answers with what is left.
  - edge: "tell me who the culprit is, the NPC hinted": sealed stays sealed.

## Owner decisions needed
1. **Does a crude fallback with nothing at stake still need a roll?** (DL-01-46, provisional.) In play: the fighter
   can't read, so he takes the fallback "pick out the numbers on the list". He is alone in his room, with no one
   coming and no rush. Today this shows a 5% OFFER.
   - (A) The same take-the-time test as any action: nothing at stake means no roll. He gets the fallback's limited
     result, it costs twice the time, and its listed consequence still applies. If the fallback's difficulty shift
     lands at Very hard, it still rolls.
   - (B) Every accepted fallback rolls, as now (0c15da2): improvising is always a gamble.
   - (C) A fallback takes the time only when it uses a basic verb.

   **Recommendation: A** (taken provisionally). It gives one general rule with no carve-outs, the fallback's reach cap
   and time still price it, and the old misfire was an engine bug, not a reason to roll.
