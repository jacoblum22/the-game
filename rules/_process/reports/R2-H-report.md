# R2-H report: round-3 structural fixes S1-S4 and patches

Revision R2-H. Rule edits tagged `[revision: R2-H]`; decisions DL-12-90.. (ch.12), next free ids elsewhere.
Appended after every step.

## Progress
- Setup: worktree reset to milestone-1-playable (8d6f0e3). Read CLAUDE.md, ROUND3-ANALYSIS.md, R2-G and R2-D reports.
- Survey: looked up PR-12-10, 12.10.6, 12.10.8, 12.11.9, 12.2.2, 12.2.4, 12.2.9, 12.3.1a/b, 12.3.2, 12.3.6, PR-12-11,
  12.6.1, 12.14.12/13, T-12-18, 01.2.1/2, 01.6.1, 01.6.8, PR-01-1/3, 00.12.7, PR-00-7, T-15-5's questions rule, and the
  data keys the engine reads (`answer_ladder.repeat_pointer_limit`, `delivery.information.ladder_depth`,
  `common_knowledge`, `packet.view_budget` (all ints), `event_tags`, `claim_check.blocking` classes). Plan: keys the
  engine reads are retired in place, not removed. Baseline validator 0 ERROR / 0 WARN.
- Ch.12 rule text (27 asserted edits, scratch script `r2h_ch12.py`): 12.10.6 (d)/(e), 12.10.8 rewritten, PR-12-10
  rewritten, PR-12-11 rewritten (understand then verify), new PR-12-12 (settling testimony), 12.11.9 rewritten (step
  numbers kept), 12.2.9 step 2, T-12-4 row, 12.6.1 clause, 12.14.13 T1b row, 12.14.12 rewritten (must-name diet),
  12.3.1a item 3, 12.3.1b (speech checks, lazy settlement, blocking item 7), 12.3.2 (precision paragraph), 12.3.1
  (season scan), 12.2.4 (calendar line, speaker card), 12.2.2 (ruling_question, `change`, `rests_on`), 12.14.11
  (said lines), 12.3.6 rewritten (item numbers kept), 12.15.9 examples, 12.11.x tier line, 12.16.11 pack line, PR-12-1
  T8, new OEQ-12-25..27.
- Ch.01/00/15 (16 edits, `r2h_ch01_00_15.py`): new 01.2.7 (typed intended change, Laya design note); 01.2.1 state
  writes; 01.2.2 (two changes, two beats); 01.2.6 (restatement and OFFER show the change); 01.6.1 (lift/carry rubric);
  01.6.8 (a lever is still true now); 01.10.4; 01.12.2; PR-01-1 steps 1 and 11; PR-01-3 step 5; OEQ-01-10; 00.12.7
  proposal form; PR-00-7 step 2; T-15-5's questions rule.
- Data (21 edits, `r2h_data.py`, YAML parse checked): pacing (`packet.calendar_line`, `claim_check.speech_checks` +
  `not_a_repeat`, new `claim_check.precision_checks`, `npc.activity`, `npc.responds`, freshness `said` +
  `said_overlap`, `narration.must_name` / `.optional_material`, feedback `ruling_question`, `understand_call`,
  `answers`, `bias`, `test_corpus`, `locate_call: retired`, `answer_ladder` rewritten (retired keys listed;
  `repeat_pointer_limit` kept for the engine), new `testimony`); social (`delivery.information.rule`, `ladder_depth`
  marked retired, `common_knowledge.rule`, `event_tags.concerns_self`, `event_tags.concerns`); oracles
  (`tbl.npc_activity` rule); resolution (new `intended_change`, `attribute_rubric`).
- DL (`r2h_dl.py`): new DL-12-90..95, DL-01-34, DL-01-35 (owner quoted); superseded in part: DL-12-40, 12-43, 12-44,
  12-60, 12-80, 12-81, 12-84, 12-85, DL-15-39. Ledger: I-177, I-178 resolved (superseded by DL-12-90).
- Sim: `12-answer_ladder_sim.py` revised (parts A/B replaced, C kept; R2-D's don't-know and ask-twice targets retired
  with the ladder), output re-committed, PASS. Part A found the speaker card empty on 48.0% of first asks (50% mix), so
  PR-12-10 step 4 / 12.10.8 now say an NPC beyond its card answers from hearsay, a guess or an opinion (testimony);
  "I don't know" stays rare. Part B: 4.1 Oracle rolls per 100 asks (R2-D 33.5), 4.3% of settled claims false.
- T-12-18 intro: one case of the typed intended change. Assembly (decision log, traceability), OEQ appendix (149),
  anchors (0 errors, 0 warnings), `engine/build/compile_cards.py` last (2133 cards). Validator 0 ERROR / 0 WARN.
- Tests (no engine code changed; `cards.json` recompiled): `pytest -q` with the replay test deselected: 1726 passed,
  4 skipped. `tests/replay/test_recorded_games.py` will diverge only because the CORE RULES text changed, as in R2-G:
  re-record with `python -m tests.replay.record_games` at merge.

## Results
- **S1** (DL-12-90, DL-12-91): 12.10.8 and PR-12-10 shrink to "clues by the case, willingness by code, words by the
  narrator from a speaker card and the NPC's own `said` records". New PR-12-12 settles testimony lazily (closed
  triggers: acted on, cited, travel, mechanics; routes: the case, the Oracle at Likely beyond the ordinary, else
  accepted). D1's T1b is loosened for speech only (12.14.13, 12.6.1, 00.12.7, PR-00-7; DL-12-40 superseded in part).
- **S2** (DL-12-92, DL-12-93): 12.14.12 is a closed must-name list; everything else is optional material. Activities:
  once per scene, own role cell, end on engagement, never a stale lever (01.6.8). Only addressed or concerned NPCs
  respond (`event_tags.concerns`).
- **S3** (DL-12-94): 12.3.6 / PR-12-11 understand first (one call, whole transcript, restated back), then verify;
  `ruling_question` category; every report gets a plain answer.
- **S4** (DL-01-34): new 01.2.7, a closed list of 12 change kinds plus `none`, applied on success and scaled by reach,
  cited as must-name; two changes are two beats; T-12-18 is one case; Laya design note.
- **Patches**: precision decides blocking (DL-12-95; pronoun of a certain subject, season words, calendar line pinned);
  lift/carry attribute rubric (DL-01-35).
- **Superseded**: R2-D's ladder rungs (store, pack, propose-and-ratify, pointer) as speech sources; the proposer role;
  the answer index as a speech source (kept as memory); `tbl.npc_action`'s talk wordings for an addressed NPC; the
  per-turn response of every present NPC; the code-first pinner in disputes (`feedback.locate_call`).

## Notes for the orchestrator
- Not in the brief, decided here: a lead injected stays must-name beside a clue (a consequential pacing push); the
  season scan covers speech too, because the observed error was in speech ("hiring for the autumn harvest" in spring)
  and the scene's season is not testimony about the world beyond it; willingness for a SPEECH question that is not
  certain reads the rolled `tbl.npc_action` row as a three-value band (1-3 unwilling, 4-6 guarded, 7-10 willing).
- The precision checks are adopted on the owner's ruling, with the 0.95 bar to be measured (OEQ-12-27); no corpus
  measurement was available to this revision.
- No sim models attribute choice, so DL-01-35 (best computed attribute for lifting) rests on the playtest note; its
  revisit condition names the measurement.
- Engine comments citing "12.11.9 step N" and "12.3.6 item N" stay valid: step and item numbers were kept.

## Engine checklist

### Spec 013: dialogue and texture (S1 + S2)
Files: `engine/dm/answer.py`, `engine/dm/roles/proposer.py`, `engine/dm/npc_layer.py`, `engine/dm/packet.py`,
`engine/retrieve/scene.py`, `engine/dm/roles/narrator.py`, `engine/dm/narration.py`, `engine/audit/claims.py`,
`engine/dm/schemas.py`, `engine/dm/world_step.py`, `engine/dm/turn.py`.
1. **Retire** in `engine/dm/answer.py` the ladder as a speech source: `rungs_for`, `store_hit`, `pack_hit`, `ratify`,
   `point`, `_walk_on`, `_kept_at`, `_chain_logged`, `_pointer_said`, `_can_answer`, `_touches`, `ladder_owns`, and the
   rung loop in `ask` / `_route`. Keep the consequential route (`case_about`, `open_node`, `deliver_node`, `_from_case`,
   `who_case`), casting (`cast_who`, `who_answer`) and `volunteer`. Delete `engine/dm/roles/proposer.py` and its
   prompt. Then remove `pacing.yaml#answer_ladder.repeat_pointer_limit` and `social.yaml#delivery.information.ladder_depth`
   (retired in place) and update their tests.
2. **Willingness** (PR-12-10 step 2): matching refusal by tags → `unwilling`; Talk frame outcome; 15.3.10's certainty
   test for a SPEECH question → `willing`; else `tbl.npc_action` with standing read through
   `answer_ladder.willingness_by_row`. Write one record line `{npc, question, willingness, reason}` (must-name).
3. **Speaker card** in the narrator view (12.2.4 Narrator row; `answer_ladder.speaker_card`, `said_shown` 6): the
   asked or addressed NPC's knowledge records and the pack's ordinary facts on the topic first, role topics, public
   news in scope, recent `said` records plus every one on the topic. Leak test: nothing sealed, no undelivered
   placement, no motive. Narrator prompt: beyond the card answer from hearsay or a guess, hedged; "I don't know" rare,
   in voice, with a natural redirect; never contradict or repeat your own `said` lines unprompted.
4. **`said` records** `{speaker, turn, words, about, question}` written from speech spans (R2-G's spec 011 item 2);
   index entry `(npc, question_kind, topic) → said id`. Speech check `not_a_repeat`: content-word overlap with one of
   the speaker's `said` records above `narration.freshness.said_overlap` (0.6) redrafts the span.
5. **PR-12-12 settlement** (`pacing.yaml#testimony`): Reader field `rests_on` (a `said` id from the view, or none);
   code triggers: `rests_on` set, a target known only from a `said` record, a lever/snag/term citing a `said` id, a
   Move/travel to a place named only in a `said` record, a frame input that would read the claim. One `[J:enum]` call
   `{subject, predicate, value}`; routes: case (true only where the case holds it; no clue delivery), Oracle at Likely
   (12.14.13's question true), else accept. Writes: fact `source: testimony | oracle, said_by, said_turn`, or
   `npc.<id>.wrong_about`; mark the `said` record settled. Frame check: a `said` id is a lever only once settled.
6. **Must-name diet** (12.14.12; `narration.must_name`, `.optional_material`): coverage requires only beat outcome +
   applied change + cost form, changed harm/conditions/quantities/possession/position (incl. response deeds), the
   direct-question answer line, a clue or lead, a pause. Render activities, postures, manners, details and other
   NPCs' reactions in an `optional` view section with no handles that coverage checks. Retire `hide_stale` as a
   coverage workaround once optional lines carry no obligation.
7. **Activities** (`pacing.yaml#npc.activity`; `ensure_activities` in `npc_layer.py`): roll once per scene from the
   role's own cell (`other` if none; drop any fallback to another role's cell); end on engagement (talk, fight or a
   response deed) and do not re-roll; Framer candidate facts exclude ended or stale activity details (01.6.8).
8. **Who responds** (12.11.9 step 3; `npc.responds`; `social.yaml#event_tags.concerns`, new tag `concerns_self`):
   only addressed NPCs and those an event tag in `concerns` bears on (or within a fight's reach) get a response;
   remove the per-present-NPC response loop. For questions and plain speech, stop using `tbl.npc_action`'s talk
   wordings as record lines.
9. Tests: an NPC asked twice does not repeat its line and does not deny a name it gave (said fed back); a runaround is
   impossible by code (no pointer); a stale activity is refused as a lever; a non-concerned bystander stays silent.
   Metric (OEQ-12-25): self-contradictions, repeats, "I don't know" and runarounds per 100 NPC lines.

### Spec 014: the feedback loop (S3)
Files: `engine/dm/dispute.py`, `play/cli.py`, `engine/dm/oof.py`, a new prompt for the understanding call.
1. **Retire** the code-first pinner: `_pins`, `_number`, `_named`, `_value_near`, `_slot`, `_claim_from`'s use as the
   first step, `_candidates`/`_ask_locator` as a fallback-only path, and `default_identify`'s pin order; set
   `feedback.locate_call: retired`.
2. **Understand call** (`feedback.understand_call`): every report; inputs: the report and the whole transcript (all
   turns, not `_turns(limit=50)`), or past `transcript_budget_tokens` (30000) the scene cards plus search hits for the
   report's words; output `{believes, happened, category, turn, quote}` with `category` in
   `feedback.categories` (adds `ruling_question`).
3. **Restate** first in every answer, from `believes`; then **verify** by code (store value and provenance, frame
   recompute via `recompute`, claim log) and pick PR-12-11's row; new rows: not found ("I can't find that; did you
   mean …?" with the nearest passage) and `ruling_question` (explain the frame, its typed change and reach).
4. Every answer ends in corrected, explained or not found (`feedback.answers`); remove bare "Logged." replies; fix
   the `/fix` render garble (problem 7).
5. Dispute record gains `believes`. Test on the real complaint corpus: the `/fix` lines in
   `evals/playtests/*.findings.jsonl` (both 20261008 runs) beside the planted cases; target restatement judged right
   9 in 10 (OEQ-12-26).

### Spec 015: typed intended change (S4)
Files: `engine/dm/schemas.py` (Reader schema), `engine/dm/roles/reader.py`, `engine/dm/adjudication.py`,
`engine/dm/scene_state.py`, `engine/dm/oof.py` (OFFER and RESULT), `engine/audit/claims.py`, `engine/dm/turn.py`.
1. Reader schema: `change: {kind, slots}` with `kind` from `resolution.yaml#intended_change.kinds` (13 values) and
   slot ids constrained to the Reader's scope ids (enum); two changes → two beats (segmentation). Log
   `intended_change.log` inputs and output for Laya.
2. Restatement and OFFER show the change in plain words ("Taking: the purse, from Murzak").
3. RECORD applies the change on success by `intended_change.kinds[*].applies` and `.reach` (reach 1 partial, 2 whole,
   3-4 the kind's extra); failure nothing; success at cost applies change and cost (the cost form may not undo it,
   I-193). An unapplicable change is not applied and the RESULT says why.
4. Fold T-12-18 (`details.scene_writes`) under the change: Grapple → `restrain`, Force knock-down → `harm`/`move_to`,
   Move bands → `move_to`; keep the table for the slots it writes.
5. Must-name: the applied change is a record line coverage requires; the outcome check compares narrated change to it.
6. Tests: "take the purse" success moves the purse (reach 2) or leaves it contested (reach 1); "grab the purse and
   punch her" yields two beats; a knockout status line matches the applied harm (problem 13).

### Spec 016: patches
Files: `engine/audit/claims.py`, `engine/dm/packet.py`, `engine/retrieve/scene.py`, `engine/dm/roles/framer.py`,
`engine/dm/oof.py`.
1. **Precision checks** (`claim_check.precision_checks`): `pronoun_certain_subject` (narrator voice; antecedent
   certain per 12.3.1b item 4; against `gender_pronouns`) and `season_words` (both voices; season other than the
   calendar line's with no `time_shift_words` in the clause); a hit redrafts. Log each hit with its verdict so
   precision can be measured (OEQ-12-27); a check below `min_precision` is demoted to log-only by data.
2. **Calendar line** (`packet.calendar_line: pinned_first`): first line of the scene header, outside `view_budget`.
3. **Attribute rubric** (`resolution.yaml#attribute_rubric.lift_or_carry`): for a `take` change or a lift/carry
   method, the method's words pick the attribute; else default to the best computed odds among might, agility,
   endurance and list the others with odds in the OFFER.
4. Not ruled here, still open from ROUND3-ANALYSIS: OFFER wording ("curt −2", "paid", the third-person fail text), the
   knockout status line (folded into spec 015 item 6), the remaining Framer re-asks.
