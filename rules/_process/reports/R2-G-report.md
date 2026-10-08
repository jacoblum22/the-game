# R2-G report: owner rulings, check less, player feedback loop

Revision R2-G. Rule edits tagged `[revision: R2-G]`; decisions DL-12-80.. (ch.12), next free ids elsewhere.
Appended after every step.

## Progress
- Setup: worktree reset to milestone-1-playable (9aeb9c5). Read CLAUDE.md, OVERNIGHT-LOG, R2-B/E/F reports.
- Part 1 I-159: sim 01-difficulty_rubric_sim.py gains the one-modifier rule (variant B) and B1 (literal reading, nudge only). Re-run seed 158: compound bound **25 (pass)**; literal reading 35 (class `other` rung + extra snag). Other B figures move slightly (CF>S 72->70; S3+ untrained 6.97->6.93). Output committed.
- Part 1-3 rule text applied by scratch script (68 asserted unique edits): ch.12 (12.3.1, 12.3.1a, new 12.3.1b, 12.3.2, 12.3.3, 12.3.4, 12.3.6, 12.14.2, 12.14.13, 12.2.10, 12.10.6, 12.2.2, 12.2.9, 12.11.9, 12.4.8, 12.5.2, 12.5.8, 12.5.10, 12.15.9, 12.15.11, PR-12-1 T9, PR-12-2, PR-12-4, new PR-12-11, OEQ-12-20/23, new OEQ-12-24); ch.00 (00.6.6a, 00.6.7, INV-9 row, 00.12.3, 00.12.6); ch.01 (01.2.2, 01.6.5, 01.6.8, 01.6.10); ch.14 (14.2.5, 14.2.7); ch.15 (15.3.2, 15.3.10).
- Data: pacing.yaml claim_check (voice, speech_checks, blocking, t2_in_narrator_voice, otherwise, claim_log, certain_subject, code_scans; audit sampled, gates_delivery false; skip keys retired, skip_enabled kept for the engine), corrections.take_back + pinned, details.max_active retired-in-place (engine reads it), oof label FIX, new feedback block; social.yaml new event_tags (29 tags; every refusal kind and want object tagged; asserted).
- DL: DL-12-42 (D5 superseded in part), DL-12-51 (D6), DL-12-70 (D8; cap dropped), DL-01-32 (D7), DL-01-29 (I-159) updated; new DL-12-80..88, DL-01-33. Ledger I-159, I-160, I-171..I-174, I-176 resolved with revision and DL ids.
- Rule text D6 (12.15.2 word maps) and D7 (01.7.4) marked owner confirmed; banned-phrase WARNs fixed; OEQ appendix rebuilt (145). Assembly, anchors, validator: 0 ERROR / 0 WARN.

## Results
- **Sim (I-159)**: `01-difficulty_rubric_sim.py`, seed 158, re-run with one model-chosen modifier per beat. The
  compound-error bound is **25 points, pass** (was 35). Disclosure: read literally (only a nudge counts), it stays
  **35** (variant B1 in the output), because a class `other` rung is also the model's choice; the adopted rule
  counts that rung as the beat's modifier. Side effects on B: CF > S frames 72 -> 70; untrained S3+ per session
  6.97 -> 6.93 (no errors), 8.77 -> 9.01 (with errors). Every acceptance target passes.
- **Validator**: 0 ERROR / 0 WARN after re-assembly, the OEQ appendix rebuild (145), anchors and cards.
- **Ledger closed**: I-159 (DL-01-29), I-160 (DL-01-33), I-171..I-174 (DL-12-88), I-176 (DL-12-87).
- **Owner rulings recorded**: D6 (DL-12-51), D7 (DL-01-32), D8 (DL-12-70) owner confirmed 2026-10-09, may revisit
  odds display and menus; D5 (DL-12-42) superseded in part by DL-12-80 and DL-12-82; detail cap dropped (DL-12-70,
  00.6.6a item 3, OEQ-12-20's cap half closed).

## Notes for the orchestrator
- `details.max_active` and `claim_check.audit.skip_enabled` stay in `pacing.yaml`, marked retired: the engine reads
  both (`engine/store/details.py::max_active` raises KeyError without it; `tests/engine/test_diff_audit.py` asserts
  `skip_enabled is False` and `full_extraction_every == 10`). Removing them is item 1 of spec 011 below.
- T2 in the narrator's voice: decided **cut**, not log (DL-12-80): it is declared by kind, so there is no matching
  and no false positive; it is rare; and it would bend the case graph. The pull-back comes from three places: an
  uncertain kind is now T1a, T2 in speech passes as testimony, and the audit no longer gates.
- I-159's adopted reading (a class `other` rung counts as the model's modifier) goes beyond the literal wording;
  both numbers are in the output and in DL-01-29.
- `/fix` already exists in `play/cli.py` (it routes to `game.dispute`, or submits an OOF dispute); the rules adopt it.

## engine checklist

### Spec 011: check less
1. `pacing.yaml`: remove `details.max_active` and its reader (`engine/store/details.py::max_active` and the
   `_lasting` slicing: order by salience then last use within the profile budget; a pinned correction counts as
   cited). Remove `claim_check.audit.skip_enabled` and rewrite `audit_mode` (`engine/dm/narration.py`) as
   `sampled`: 1 turn in `full_extraction_every`, by turn id (crc32 as now), **after delivery**, findings to the claim
   log only. Update `tests/engine/test_diff_audit.py::test_the_audit_skip_stays_off_until_the_gate_is_met`.
2. Narrator schema: each sentence gains `speaker` (enum: present people in scope, never the PC). Split speech from
   the narrator's voice (quoted spans plus `speaker`). Speech checks are code: the speaker is present, is not the
   PC, and no quoted PC words go beyond the player's message. Write a `said` record `{speaker, turn, words, about}`
   (not a world fact). A name heard in speech that equals the stored name writes a PC knowledge record `how: heard`.
3. Blocking list (`claim_check.blocking`): judge only narrator-voice claims with a certain subject in the classes
   outcome/capability, harm_condition, quantity, possession (mechanically relevant: weapon, armour, tool, key,
   consumable, coin, a cited lever, more than common value), position (coarse only, as in spec 010), existence
   (presence, alive), sealed, identity (names the PC does not know), plus `pc_agency`. Every other verdict is
   written by tier or logged to a claim log `{turn, sentence, class, verdict, store_value}`, never cut or redrafted.
4. Certain subject (`claim_check.certain_subject`): a verdict only for a unique proper name or alias, a declared
   `about` id that is the only in-scope entity the words fit (head-noun match count = 1), or the only candidate
   present; the PC and this turn's beats are always certain. Ambiguous: no verdict, logged, in both directions.
5. Code scans every turn (`claim_check.code_scans`): numerals against quantities in view; names and aliases
   against PC-known names and sealed strings; outcome words against the frame's degree and reach. An undeclared
   or atmosphere sentence is redrafted or cut only on a scan hit; otherwise it is delivered and logged (12.3.1a).
6. T2: cut only narrator-voice elements declared `clue`, `hazard` or `adversary`, or a person, item or document
   the T2 question clearly finds true; an uncertain kind is T1a (`engine/audit/declare.py` tier default).
   Audit-typed T2 never cuts.
7. Incidental clashes (a lasting detail against the store; a `write_detail` conflict) are logged and the store keeps
   its value, except blocking-list slots (a held weapon, a coarse position), which redraft.
8. Unsourced change: cut only for blocking classes; an incidental NPC act with no source is logged, neither cut nor
   written. The scene-end sweep (12.4.8 step 4): narrator voice and certain subjects only.
9. I-159: the frame check refuses a cited Precision snag on a beat whose tier carries a nonzero nudge or whose class
   is `other`; such snags apply as Protective (stakes +1 each, clamped). The odds audit and OFFER snapshots will move.
10. I-160(a): the Framer's reach factors (two unoffset, or a total potency) route the beat to G4 before the OFFER,
    with 01.3.7's redirect and nothing spent. (b) `extended` is already a Reader value: no change.
11. I-176: tag events from the verb, facets, target, topic, terms, pressure mark and one Framer `asks` enum (a new
    Talk frame field, closed list `social.yaml#event_tags.asks`); match refusals and wants through
    `event_tags.refusals` and `.wants`; rows: served 9 (a request) or 8, defeated 2 (1 at Hostile), engaged 6, then
    the practice clamp. The World call runs only when no tag matches and two motives point to opposite rows. Crowd
    response: a scene fact `crowd_response` on the scene's place, with a record line (`engine/dm/npc_layer.py`).
12. Live-run metrics: cut turns, first-draft pass, calls per turn, claim-log entries per 100 turns by class, and
    sampled blocking-list misses per 100 turns (OEQ-12-23).

### Spec 012: the feedback loop
1. `/fix <text>` is a DISPUTE by code (already routed in `play/cli.py`); the Reader classifies natural disputes
   (12.2.2's examples). When the Reader is unsure whether a fiction part is a dispute, append the hint line
   (`pacing.yaml#feedback.hint`) to the response. The hint is the SITUATION block's last line at session start.
2. Locate (`engine/dm/dispute.py`): extend `default_identify` to pin turn ids, quoted phrases, names, numbers and
   frame ids against the **whole transcript** (every turn, not `_turns(limit=50)`). When the report is unpinned,
   one model call returns `{turn, quote, category}` from the report and the candidate turns (this scene first,
   then search hits). Categories: remembered_wrong, rule_wrong, contradiction, misread, other.
3. Evidence: fact provenance (source event seq, source kind, turn) for every fact touched; the frame with its cited
   facts, rule ids and inputs; the claim log for those turns.
4. Rule disputes: recompute the frame from the rules data and the facts valid at its commit seq (gate, DC, nudge,
   levers and snags, cost, odds); a difference or an omitted fact is a ruling error (the existing `_ruling`, with
   reliance true).
5. Outcomes follow PR-12-11's table. A correction is a `fact_set` with `source: correction`, `supersedes` and
   `pinned: true` (a new field: never archived, always in the subject's profile in `view_for`). The player's reading
   wins only when the subject is T0 or T1a (detail slots, incidental facts) and the evidence is uncertain; never for
   quantities, harm, conditions, relevant possessions, coarse position, clues, sealed facts or rulings (INV-9).
6. Take-back: widen `_rewind` past the scene start when the evidence is code-confirmed and nothing in
   `corrections.take_back.blocked_by` happened since (death or Dying, unsealed content, a completed clock, a session
   boundary), at most `max_turns_back` (10) turns. A misread beat (no OFFER shown, or auto-committed) can be taken
   back whenever it is reported, not only on the very next message (12.5.8 item 2).
7. Labels: answers use `[CORRECTION]` and the new `[FIX]` (replace `NOTE` in `dispute.py`; `FIX` is in the OOF
   label list).
8. Review log: a dispute record in the corrections ledger `{id, time, turn, words, category, passage, evidence,
   outcome, writes, reverted}`, and an appended markdown block in `saves/<campaign>.disputes.md`.
9. Metric: disputes per 100 narrated turns (all, upheld, by category) in the live-run report and in
   `evals/longhorizon.py` (OEQ-12-24). Tests: one per outcome row of PR-12-11, plus a cross-scene take-back and a
   refused one (a death in between).

## Close-out
- `engine/build/compile_cards.py` run last; validator 0 ERROR / 0 WARN.
- Suite: 1654 passed, 4 skipped with `tests/replay/test_recorded_games.py` deselected. The 3 replay tests diverge only because the rule text in the CORE RULES section changed (20430 -> 20663 chars): re-record with `python -m tests.replay.record_games` at merge, as earlier rules waves did (not done here: tests/ fixtures are shared).
