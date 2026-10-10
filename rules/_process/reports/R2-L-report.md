# R2-L report: round-8 rules wave (F-A facts not orders, T2, T4, T5, patches)

Revision R2-L. Rule edits tagged `[revision: R2-L]`. Source: ROUND8-PLAN.md (owner-approved 2026-10-10);
ROUND8-PROPOSAL.md (ceiling grid, examples); ROUND8-ANALYSIS.md §1; constitution VIII. Appended after every step.

## Progress
- Setup: worktree reset to milestone-1-playable (fdb6bee). Read ROUND8-PLAN, ROUND8-PROPOSAL, ROUND8-ANALYSIS,
  constitution VIII (lines 408-471), R2-K report. Baseline validator 0 ERROR / 0 WARN. Free ids confirmed:
  DL-12 ends at 125, DL-01 at 48, DL-15 at 42, DL-00 at 08, ledger at I-226.
- Survey: read by id 12.11.3-12.11.6, 12.11.9, 12.2.2, 12.2.4 (views, rows), 12.2.7, 12.2.9, PR-12-1, PR-12-2, PR-12-3,
  PR-12-10, PR-12-11, 12.3.1 (action row), 12.3.1a, 12.3.1b, 12.3.6, 12.5.8, 12.8.2, 12.10.5, 12.10.8, 12.14.9,
  12.14.11, 12.14.12, 12.15.2, 12.15.3, 12.16.16, T-12-12, T-12-18, 01.2.1, 01.2.2, 01.2.5, 01.4.1, 01.4.4, 01.18.7,
  00.7.3, 00.12.3, 11.5.6, 15.3.2, 15.3.4, 15.3.10, 15.7.1, 15.9.5, 15.9.16, T-15-15, PR-15-6; data tbl.npc_action,
  tbl.npc_practice, tbl.12.seed.inciting, tbl.12.seed.document, tbl.lead_injection, pacing.yaml (claim_check, npc,
  details.scene_writes.responses, narration, feedback, dm_questions, answer_ladder, lead_injection),
  resolution.yaml#take_the_time, investigation.yaml#journal, social.yaml#delivery.information. Grepped R8-D1 (46
  order kinds), R8-I1, R8-I2 §8-11, R8-I3 (P2, P5, P8). Engine readers checked so no key the engine reads is removed
  (`tbl.npc_action`, `tbl.npc_practice`, `willingness_by_row`, `scene_writes.responses` stay, marked retired).
- Two real decisions the plan leaves open (taken provisionally; see "Owner decisions needed"): whether an ask that
  rolls today still rolls under the ceiling; how a narrator-chosen NPC deed that changes state reaches the record.
- Ch.12 (scratch `e12a.py`, 23 edits; `e12b.py`, 40 edits; helper `r2l_lib.py`: unique match, exact or the same
  words with any wrapping, file written only if every edit applies). F-A: 12.11.4, 12.11.5 (rewritten), 12.11.9
  (rewritten: present and able, mood, ceiling, narrator decides, declared deeds, activity, state before reactions,
  standing; MUST only for spine facts; retires list), 12.2.9 step 2 and worst case, PR-12-1 T5 and T10, T-12-18
  (Talk row; response and practice rows retired), new **T-12-19** (the ceiling grid, with the three proposal
  examples), table index (T-12-17, T-12-18, T-12-19), T-12-4 row, 12.3.1 `action` source, WE-12-5, 12.2.2 (addressee
  and cost fields; worst case), 12.2.7 (no unconditional "(answered)"), 12.14.9 (open prompt: no mandatory closing),
  12.14.12 (learned fact; MUST only spine), 12.10.5 (reading follows the target), 12.10.8, PR-12-10 (learned clue; one
  judgment per message; mood and ceiling; pointer candidates), 12.2.4 rows (Narrator facts and setting once, Director
  casts by id, Fixer marks and digest). T5: 12.3.1b items 1 and 2.7, 12.14.11 said lines, PR-12-2 steps 2-3. T4:
  PR-12-11 steps 2, 3, 6 and retires, 12.3.6 item 4, 12.5.8. P3/P8: 12.15.2 title and fate, 12.15.3. P5: 12.8.2,
  PR-12-3. P7: 12.14.11, 12.2.4. T2: 12.16.16 (incident actor on stage; every kind). New OEQ-12-28 (measurement).
- Ch.00, 01, 11, 15, 16 (scratch `e01.py`, 22 edits): 01.18.7 (talk with menace stays Talk), 01.2.2 example, 01.2.5
  (the addressee is the Reader's), 01.4.4 (P2: minutes in free play), 01.4.1 (P4: mechanical cost sources only);
  00 working stance item 1 (facts, not orders), 00.12.3 (facets never re-verb), 00.7.3 free row; 11.5.6 (terms for
  every lead and incident kind, enumerated); 15.3.10 (certainty needs a *will help* ceiling, provisional), 15.7.1
  (the ceiling's price; a payment is the paying beat's consequence), 15.9.5 (learned fact), T-15-5 questions rule
  (one clue judgment first), 15.9.16 and T-15-15 (what you were told; lookup), PR-15-6 step 7, 15.2.x want/fear lines
  that cited `tbl.npc_action`; 16 ally item 6.
- Data (scratch `edata.py`, 23 edits; all five files parse): `oracles.yaml` new `tbl.npc_mood`, `tbl.npc_ceiling`;
  `tbl.npc_action`, `tbl.npc_practice` `lifecycle: retired` + `superseded_by` (kept for their readers);
  `pacing.yaml` `npc.reaction_layer` (facts, narrator decides, mood, ceiling, cost map, declared deeds, must lines,
  retired list, measure with the 5% fallback), `npc.responds` and `scene_writes.responses` marked retired,
  `activity.empty_rows_shown`, narration (`closing_line`, `answered_mark`, `reading`, freshness `said_repeat`,
  `same_place_scene_cut`), claim_check (`unmeasured: log_only`, pronoun `precision: 0.0`, `not_a_repeat` to
  `speech_logged`), dm_questions, answer_ladder (mood, clue judgment per message, pointer candidates, sources),
  lead_injection (Director first), feedback (reread, digest, marks, undo); `resolution.yaml#take_the_time`
  (minutes, `free_unlisted_minutes: 5`, `cost_source`); `investigation.yaml#journal` (told, lookup);
  `social.yaml#delivery.information` (clue judgment first). One slip fixed by hand: the journal `lookup` key had
  landed inside the sections list.
- Decisions and ledger (scratch `edl.py`): DL-12-126..142 (DL-12.md), DL-01-49..53 (DL-01.md), DL-15-43..47 (DL-15.md),
  DL-00-09..10 (decision-log.md's DL-00 head, after DL-00-08). Owner quotes only from ROUND8-PLAN §Owner rulings, dated
  2026-10-10; T2, T4, T5 and patch entries say there is no direct quote. Every entry has a checkable "Revisit if".
  Revisit notes (ROUND8-ANALYSIS §1) acted on, each with a `Revisited` line: DL-01-39, -40, -44; DL-12-99, -103, -109,
  -110, -114, -116, -117, -119 (condition widened to "any code cap"), -122, -123; DL-15-42; DL-00-08. `Amended` lines
  on DL-12-43, -87, -93, -118 (not fired; carried by the mood) and DL-15-39. Summary in DL-12-142. Ledger I-227..I-243
  (I-243 resolved; the rest open: rules done, engine specs pending; I-228 and I-230 provisional).
- First validator run: 3 errors (12.11.9 and 12.14.9 now carry `[J]` and needed Worst case lines; a data reference
  `tbl.npc_mood_once_per_scene`). Fixed (scratch `efix1.py`). Rebuilt the OEQ appendix (`build-oeq-appendix.py`,
  150 questions). Older text that still named the willingness band or T-12-18's response rows revised (scratch
  `efix2.py`: 01.9.3, 01.15.1, 12.6.1, T-12-4 row, PR-12-12; `efix3.py`: 00.6.6a item 4). Owner decision R2-L-3
  named where its default lives (`efix4.py`: 01.4.4, DL-01-50, `resolution.yaml`).
- Close: re-assembled the appendix (`integration-assemble-appendix.py`), rebuilt the OEQ appendix (150), compiled
  anchors (129; 0 errors, 0 warnings), compiled cards last (2134 cards, core 6; `--check` ok). Validator: **0 ERROR /
  0 WARN** (INFO only: BASIS 1, POOLS 2, REFS-EX 9, REFS-MD-EX 70). Engine tests: 1938 passed, 4 skipped, 4 failed, all
  intended effects of this wave and outside its lane (tests/ untouched): three pronoun-check tests
  (`test_check_less.py::test_a_pronoun_clash_on_a_certain_subject_now_redrafts`,
  `test_precision_checks.py::test_pronoun_hit_on_the_only_person_named`,
  `::test_a_check_measured_below_min_precision_is_log_only`) expect the pronoun check to block, which T5 demotes
  (`precision: 0.0`; spec 030 updates them); `tests/replay/test_recorded_games.py::...[offline_seed11]` diverges
  because the guidance digests carry revised card text (re-record with spec 028).

## Ids touched
- Rules: 00 working stance item 1, 00.6.6a item 4, 00.7.3, 00.12.3; 01.2.2, 01.2.5, 01.4.1, 01.4.4, 01.9.3, 01.15.1,
  01.18.7; 11.5.6; 12.2.2, 12.2.4 (Narrator, Director, Fixer rows), 12.2.7, 12.2.9, 12.3.1, 12.3.1b, 12.3.6, 12.5.8,
  12.6.1, T-12-4, 12.8.2, 12.10.5, 12.10.8, 12.11.4, 12.11.5, 12.11.9, 12.14.9, 12.14.11, 12.14.12, 12.15.2, 12.15.3,
  12.16.16, PR-12-1 (T5, T10), PR-12-2, PR-12-3, PR-12-10, PR-12-11, PR-12-12, T-12-18, **T-12-19 (new)**, the ch.12
  table index, WE-12-5, **OEQ-12-28 (new)**; 15.2.x want and fear lines, 15.3.10, 15.7.1, 15.9.5, 15.9.16, T-15-5
  (questions rule), T-15-15, PR-15-6; 16 ally item 6. Ch.13 untouched.
- Data: `oracles.yaml` (`tbl.npc_mood`, `tbl.npc_ceiling` new; `tbl.npc_action`, `tbl.npc_practice` retired),
  `pacing.yaml`, `resolution.yaml`, `investigation.yaml`, `social.yaml`; `anchors.yaml`, `engine/build/cards.json` and
  `appendix/open-empirical-questions.md` regenerated.
- Decisions: DL-00-09..10; DL-01-49..53; DL-12-126..142; DL-15-43..47. Revisited/Amended lines as listed above.
  Ledger I-227..I-243.
- Unused from the allotted ranges: DL-12-143..145, DL-01-54..55, I-244..245.

## What each change retires (each rule says it)
- F-A: `tbl.npc_action` (rows as deeds, as willingness, as compliance) and `tbl.npc_practice` with its clamp; "X acts:
  …" MUST lines; code-written refusals and their example gesture lists; T-12-18's response-row scene writes; the
  `addressed`/`concerned` gate, word-overlap and "last spoke with" addressees; "quote exactly"; the mandatory closing
  line; empty activity lines; the unconditional "(answered)"; the Talk → Grapple rewrite; the reading line's guess;
  casting by description; payment as a step of the reaction.
- T2: one-sentence leads and reporter-only incidents; a second invented incident actor; per-part clue calls and
  first-question-wins routing; the journal's name-only lookup.
- T4: the odds-only rebuild; undo with no scene; internal turn numbers in replies.
- T5: blocking by any check with no measured precision; the pronoun and repeat blocks.
- Patches: the 20-minute interval in free play (P2); narrated details as cost sources (P4); place-or-verb persuade
  titles (P3); the ladder overriding the Director's pick and re-pushing known hooks (P5); re-describing on a
  same-place cut (P7); "evidence as a no-roll success" and "no reroll" (P8).

## Engine checklist per spec
Each spec labels every case **made-up** or **edge** (DL-00-08) and enumerates its breadth cases from the data's own
kinds (DL-00-10), then adds its own; it is accepted on them plus a held-out set.

**Spec 028 (F-A, with T1, T3 and the forced texture; the agreeableness measures, baseline and 3-arm A/B)**: lane
`npc_layer.py`, `roles/narrator.py`, `narration.py`, `handles.py`, `packet.py`, the Reader, `gate.covering_verb`,
`world/social.py`, `scene_state.py`, an eval script.
- Cite: 12.11.9 (steps 1-8), 12.11.4, 12.11.5, 12.2.9 step 2, PR-12-1 T5 and T10, T-12-19, T-12-18 (response rows
  retired), T-12-4, 12.3.1 (`action` source), 00.6.6a item 4; 12.2.2 (addressee, cost), 01.2.5, 01.18.7, 01.2.2,
  00.12.3; 12.2.7, 12.14.9, 12.14.12, 12.10.5; 12.10.8 item 2, PR-12-10 steps 2-4; 12.2.4 (Narrator, Director rows);
  15.3.10, 15.7.1 items 1 and 3; 16 ally item 6; OEQ-12-28. DL-00-09, DL-12-126..134, DL-01-49, DL-01-53, DL-15-47.
  Data: `oracles.yaml#tbl.npc_mood`, `#tbl.npc_ceiling`; `pacing.yaml#npc.reaction_layer` (all keys),
  `#npc.activity.empty_rows_shown`, `#narration` (`closing_line`, `answered_mark`, `reading`), `#answer_ladder`
  (`mood`, `mood_source`, `ceiling_source`, `refusal_pointer`), `#dm_questions`.
- Build:
  - facts channel: per present and able NPC, place, band and mood; per ask, the ceiling cell (or the frame's
    outcome) and pointer candidates; clue deliveries as `learned` lines; MUST only on roll and reach, state changes,
    learned clues and pauses;
  - `tbl.npc_mood` rolled lazily once per scene per NPC, held, moved one step by payment, won persuasion (up),
    threat, insult (down); the old band read through the one-to-one map;
  - Reader: `addressee` per speech or question part, `cost` per ask; the ceiling lookup with the 15.3.2 map and the
    defeats-a-want step; 15.3.10 certainty also needs a *will help* cell (provisional R2-L-1);
  - the narrator's typed deed declarations (hand_over, take, leave, summon, attack) applied by code only when present,
    able and within the ceiling, else `unsourced_change` (provisional R2-L-2);
  - payments applied as the paying beat's consequence before any reaction (gifts from the Reader's quantity);
  - Director casting returns an id or `new {group, role}`;
  - reading from the beat's target; no "quote exactly"; ordinary words for a thing with no text;
  - no closing instruction; no gesture lists; no "(answered)"; activity rows that name no visible act left out;
  - the eval: OEQ-12-28's seven measures with a hand-checked judge; baseline on the round-8 saves; the same seeded
    scenes three ways (current code, dial and ceiling, judgment only); the 5% fallback switch.
- Retire: `npc_layer.addressed` (`described_in`, `_looks`, `_TURNS_TO`, `_ADDRESS`, `spoken_with`/`present[0]`, role
  head noun); the practice clamp and `tbl.npc_action` row use in `respond()`; `voiced_refusal` and `_withheld`'s
  gesture suffix; "X acts:" MUST items; `scene_state.response_values` writes; `_speech_line`'s "nobody else speaks";
  the SCENE SETTING "people here act only as the record says"; `narrator.md`'s "never their deeds or whether they
  agree"; `record_text`'s end-handback; `turn.py`'s "(answered)"; `_reading_lines` (`_POSTED`, `_READ_VERB`,
  `_SAYS`, the lone-notice fallback); `gate.covering_verb`'s Talk → Grapple; `cast_described` and `_GROUP`. Then
  delete `tbl.npc_action`, `tbl.npc_practice`, `npc.responds`, `scene_writes.responses`, `willingness_by_row`,
  `willingness_source`.
- Cases (enumerated from the data):
  - every mood × cost cell, made-up: open × none "which way to the ferry?" (will help); open × small "lend me your
    lantern for the night" (will help); open × real "lie to the watch for me" (helps for a price); open × big "hide me
    from the watch tonight" (partial or refuses); guarded × none "is this the ferry?" (will help); guarded × small
    "does Hob drink here?" (helps for a price, WE-12-5); guarded × real "watch my cart overnight" (partial or
    refuses); guarded × big "testify against the reeve" (refuses); closed × none "what time is it?" (partial); closed
    × small "let me sit by your fire" (refuses); closed × real "let me into the archive after dark" (refuses); closed
    × big "betray your lord" (refuses, may escalate);
  - edge: a won Talk frame above its cell (the frame's outcome stands; the mood moves up); a failed frame on an open ×
    none ask (refuses); a recorded refusal covering an open × none ask (refuses); an ask that defeats a recorded want
    (one cost step higher); a closed holder of a core clue (the clue is still delivered); a narrator reaction above
    its cell (logged as a violation, deed not applied);
  - every mood event: payment, won persuasion (up), threat, insult (down); edge: open plus payment stays open; closed
    plus threat stays closed and may escalate; a new topic, a repeated ask, the narrator's own words (no change);
  - every "not listed" kind: dead (the youth just killed: no reaction), unconscious, departed, gagged (not able to
    speak; may still nod);
  - every declared deed kind: hand_over at will help (applied), at helps for a price before payment (cut), after
    payment (applied); take; leave (always applied); summon from closed after an insult (applied) and from guarded
    (cut); attack at refuses, may escalate (applied, conflict starts) and from open (cut);
  - addressee: an id; none ("I call out to the room"); move-then-ask ("I step to the sellsword and ask"); a name the
    word matcher would miss ("Wait, friend!" to the woman); two people named in one message; the Reader's none with
    one person present (the narrator answers with them);
  - talk with menace: shove to intimidate (Talk, Might); raised fist (Talk); grip on the collar while demanding (Talk);
    hand over a mouth to silence (restrain goal: Grapple);
  - reading: the gate log with no text (ordinary words, nothing hidden); the letter in the PC's own pocket with a
    notice on the wall; two notices in view; a re-read when asked (honoured);
  - forced texture: ten turns with no closing line forced; eight refusals with no shared gesture; an activity row
    "is on an errand" (not shown); a SPEECH part with no answer (no "(answered)").
  - payment: "I buy the table a round and ask about the road" (coin moves, then reactions); a gift with an amount; a
    deal price paid in the same message as a question.

**Spec 029 (T2 + P9)**: lane `engine/gen/`, `answer.py` (clue routing, `learned` delivery), the journal,
`world_seed.yaml`.
- Cite: 11.5.6 (every kind), 12.16.16 (the incident's actor on stage; every kind), PR-15-6 step 7, 15.9.5, PR-12-10
  step 1 (learned fact; one judgment per message), T-15-5 questions rule, 12.10.8 item 1, 12.14.12 item 3, 15.9.16,
  T-15-15. DL-12-135, DL-15-43, DL-15-44, DL-15-45, DL-15-46; DL-15-39 amended; DL-12-103, DL-12-109, DL-12-119
  revisited. Data: `investigation.yaml#journal` (`journal.told`, `lookup`), `social.yaml#delivery.information.
  clue_judgment_first`, `pacing.yaml#answer_ladder.clue_judgment`.
- Build: `terms_for` for every kind below (who by id, what as data, where bound or created, words as a `text` fact
  where a message, notice or log exists, pay where one is offered), written as unsealed knowledge on the knowers'
  cards and documents; the incident's subject cast into the opening by id in its role, identity sealed; one clue
  judgment over all question parts before `deliver_count`; a delivered clue as a `learned` item with its knowers
  present; the journal's "what you were told" section and its lookup over thread text, said records and knowledge.
- Retire: one-sentence leads; reporter-only incidents; per-part clue calls; `deliver_count` slicing parts before
  routing; the journal's name-only short-circuit and thread-name matching.
- Cases (enumerated from the data):
  - every incident kind (`tbl.12.seed.inciting`), made-up: alarm (what is at the gate, who saw it, where); dying
    messenger (the message's words, who it was for, where they are); missing (who, since when, last seen where, the
    reward); offer (the work, the pay, the warning, who offers: the person on stage); theft (what, from where, who
    found it gone); omen (what was seen, where, who reads omens); refugees (from where, their story's words, who leads
    them); duel (the challenge's words, the challenger on stage = the case subject);
  - every opening lead: the incident's target, the situation or wound lead ("a closed cart came in"), the fourth
    faction's hire lead;
  - every document kind (`tbl.12.seed.document`): hire, bounty, warning, charter; edge: a log or ledger the player
    reads that no generator made (ordinary words, no clue, no stall, no false "answered");
  - every lead-injection form (`tbl.lead_injection`, d12): someone brings it; overheard; a found object; the
    opposition's mistake; a sign in the land; an old contact; an offer; someone seeks you out; a detail overlooked;
    pressure shows itself; a plea for help; common talk;
  - a rumor's `points_to`; every creation-hook kind (02.9.7): thread, rumor, npc, place, debt, enemy, question;
  - P9 edge: "What are the dangers, and who signed the order?" with the clue in the second part (delivered); three
    questions at Limited reach with the clue third (delivered outside the count); a clue the PC already has (not
    re-delivered); the holder absent (pointer, no delivery);
  - journal: "what do I know about the miller's daughter?" finds the baker's "left with a tinker"; "X and Y" split;
    two speakers who contradicted each other (both shown, attributed, truth unknown).

**Spec 030 (T4 + T5 + P1-P5, P7, P8, P10)**: lane `fixer.py`, `dispute.py`, `audit/` checks, `oof.py`, `necessity.py`,
the time code, `evals/playtest.py`.
- Cite: PR-12-11 steps 2, 3, 6 and retires, 12.3.6 item 4, 12.5.8, 12.2.4 Fixer row; 12.3.1b items 1 and 2.7, 12.14.11
  (said lines; setting once), PR-12-2 steps 2-3; 01.4.4, 00.7.3, 01.4.1; 12.15.2 (title, fate), 12.15.3; 12.8.2,
  PR-12-3; 12.2.4 Narrator row. DL-12-136..141, DL-01-50..52; DL-12-116, -117, -123, -99, -122, DL-01-39, -44
  revisited. Data: `pacing.yaml#feedback.investigate` (`reread_with_note`, digest, `marks_code_forced`,
  `undo_reshows_scene`), `#claim_check` (`unmeasured: log_only`, pronoun `precision: 0.0`, `speech_logged`),
  `#narration.freshness` (`said_repeat`, `same_place_scene_cut`), `#lead_injection` (`director_pick_first`,
  `never_known_thread`, `note_as`); `resolution.yaml#take_the_time` (`free_unit`, `free_unlisted_minutes`,
  `cost_source`).
- Build: `reread` (the Reader again with the note, then gate, necessity, frame); undo re-shows the scene and names
  the turn by what happened; code-forced marks on the narrator input lines the Fixer sees; the digest's three glosses;
  a check blocks only with a recorded precision at or above the minimum (code-enforced); the pronoun and repeat checks
  log; take the time in minutes in free play; mechanical-only cost sources; persuade titles from person and act;
  the Director's lead pick first, never a known thread, the note as data; setting once keyed to a change of place;
  RESULT and fate lines in plain words. P1 (engine only): `oof.changed_line` checks `name_known`. P10 (engine only):
  the harness persona sees only new output.
- Retire: the odds-only rebuild; "took back turn N"; the pronoun and repeat blocks; `pipeline._no_roll`'s interval
  default; "· evidence as a no-roll success"; "no reroll"; `inject_lead`'s ladder on a turn the Director chose; the
  "toward X, through X" template; scene-id-keyed setting.
- Cases (enumerated from the data):
  - every `/fix` category (12.3.6): remembered_wrong, rule_wrong, contradiction, misread ("I asked the captain, not the
    clerk": re-read), ruling_question, other; edge: a note that states odds (not passed, the reply says why); a
    re-read that still shows the complaint (iterate within the budget); an undo past a scene start (scene re-shown);
  - every gate class (G0-G4) after a re-read: a question re-read as a declaration; G1 Talk re-read from "Persuade" to
    intimidation with menace; G2 and G3 licence glosses in the digest ("Push: spend Focus for reach"); G4 unchanged;
  - every necessity reason for the RESULT line: uncertain_and_costly (die shown), riding, trivial ("no evidence"),
    good_idea, impossible, take_the_time ("you take the time (10 minutes) · success"), certain_with_cost; edge: a
    secret frame (no fate line; "hidden check made" only after a roll);
  - every time mode for take the time: conflict (never), site (2 intervals), free (minutes; an unlisted beat 10
    minutes; edge: three in a row stay under an hour and cut no scene), travel (2 watches), downtime (twice the days);
  - every cost source kind for P4: a clock, a person's record or stance, a hazard, a quantity or possession, a
    condition (costly); a narrated detail ("scuffed binding") (not costly; turning a page takes the time);
  - every precision check: pronoun_certain_subject (logs), season_words (0.5: logs), outcome_words (0.1: logs),
    not_a_repeat (logs); edge: a new check with no `precision` field (logs, never blocks);
  - lead injection: the Director picks the thread the player chases (that thread's lead); the Director picks none
    (ladder rungs 1-7); the ladder's first pick is a known hook (skipped);
  - setting once: arrival at a new place (look given); a scene cut at the same place (no look); leaving and returning
    (look again); a new person entering at the same place (their look only);
  - P1 edge: a death of someone whose name the PC never learned ("the freckled youth" in RESULT, never the true name);
    P3: persuade titles for a person, a group and a document holder.

## Owner decisions needed
1. **R2-L-1: does an ask that rolls today still roll, or does the ceiling answer it?** In play: you ask a wary
   dockhand to watch your cart overnight. Today that is a persuasion roll (a real cost to him), and a good roll gets a
   yes. The new grid says a wary person asked a real favour gives part of it at most, or refuses.
   - (A) Rolls stay where they are. The grid caps every ask no roll decides (questions, plain asks, reactions), and a
     free "certain" yes also needs the grid to say *will help*; otherwise the ask is rolled as usual. A won roll is
     the "won persuasion" that lifts the mood.
   - (B) Ask first, roll on pressing. A plain ask gets the grid's answer with no roll; a roll happens only when you
     press (argue, offer, threaten), and a won roll then stands and lifts the mood.
   - (C) Grid only. Requests never roll; only payment, threats, insults and won arguments move the mood.

   **Recommendation: A** (taken provisionally: DL-12-128, 15.3.10). It is the smallest change to chapter 15, keeps
   the odds the player sees in OFFERs, and the grid still covers what round 8 got wrong. Revisit after the OEQ-12-28
   baseline: if players find rolled yeses from wary people too easy, B is the next step.
2. **R2-L-2: how does an NPC deed the narrator chooses reach the record?** In play: the guard you just paid decides
   to walk off his post; the merchant hands over the map; the bouncer calls his friends.
   - (A) The narrator declares the deed as a typed change (hand over, take, leave, summon, attack); code applies it
     when the NPC is present and able and it is within the ceiling (a summons or an attack only from a closed mood
     after a threat, harm or insult, or at *refuses, may escalate*); otherwise the sentence is cut, as today.
   - (B) Words and gestures only: any deed that changes something needs code's decision (this brings back code
     ordering reactions).
   - (C) Deeds are written as narrated (the spine would follow prose).

   **Recommendation: A** (taken provisionally: DL-12-130, 12.11.9 step 5). It keeps judgment with the narrator and
   the spine exact, with the check code already runs (`unsourced_change`).
3. **R2-L-3 (small): how long does taking the time take in free play when the activity has no listed time?** In
   play: you take your time looking through a stall's wares. Today the rules say "twice the listed time", and an
   unlisted beat takes no time, so twice nothing is nothing.
   - (A) Twice 5 minutes (10 minutes).
   - (B) Twice 1 minute.
   - (C) No time at all.

   **Recommendation: A** (taken provisionally: `resolution.yaml#take_the_time.free_unlisted_minutes: 5`, DL-01-50).
   Patience should cost a little, and three such beats stay well under the hour that cut round 8's scene.
