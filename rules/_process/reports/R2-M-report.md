# R2-M report: spec 033 phase R (the DM states, code records; constitution VIII.9)

Revision R2-M. Rule edits tagged `[revision: R2-M]`. Source: specs/033-dm-states-code-records/ (HANDOFF.md owner
rulings D1 (a), D2 (b), D3; plan.md section 4; tasks.md T090-T097; cases.md C1, C4, C5-C7, C10); constitution 3.1.0
VIII.9 "Code never deduces the story". Single slice, last slice. Appended after every step.

## Progress
- Setup: `git reset --hard spec033-base` (19f95d6). Read HANDOFF.md, tasks R, plan sections 2 and 4, spec, cases C1-C10.
  Baseline validator 0 ERROR / 0 WARN. Free ids confirmed: DL-06-40..49, DL-01-60..69, DL-12-160..169 unused; next
  table id T-06-16. `basic_verbs.yaml` is hand-written (no `*gen*` script writes it; 01-difficulty_rubric_sim.py and
  12-compile_anchors.py only read it).
- Survey: read by id 06.9 (06.9.1-06.9.7), 06.3.9, 06.5.3, 06.4.4, 01.13.7, 01.9.3, 01.2.5, 00.12.3, 00.6.6, PR-00-7,
  02.4.6, PR-12-3, 12.8.1, 12.8.2, 12.8.4, PR-12-5, PR-12-12, 15.9.4, 11.13.1; refs of 06.9.1, 06.9.3, 06.3.9, 01.13.7
  (PR-06-1, PR-06-6, 09.7.1, WE-09-3, ch.07 design intent (c)); licenses.yaml ids and scopes for `covered_by`.
- Ch.06 (scratch `e06.py`, 14 edits; helper `r2m_lib.py`: unique match, exact or the same words with any wrapping,
  file written only if every edit applies, new text in the file's line ending): 06.9.1 rewritten (the DM picks each
  adversary's act and target after the PC's result; defaults logged; retired rationale and passivity measure kept),
  06.9.2 (target as picked), 06.9.3 (guidance; the Dying-PC limit binds the pick; narration clause), 06.9.4 (guidance
  and logged default), new **T-06-16** (acts legal now, cases C4), 06.9.7 (no secret holding back; picks open and
  logged), PR-06-6 steps 3 and 5, 06.3.9 (the DM states the start band; default near, logged), PR-06-1 step 2, 06.5.3
  (Force undeclared: push, logged).
- Other chapters (scratch `e_rest.py`, 18 edits): 01.13.7 (the form is the DM's pick after the roll among those that
  can land; default the first listed that can land, logged), 01.9.3 (reversal by cost id from `reverses_goal`, no
  words), 01.2.5 (target defaults are the Reader's; code never picks a target by words), 00.12.3 (`covered_by`;
  `approach` a stated field), 00.6.6 (elements declared, never found by scanning prose), ch.07 design intent (c),
  09.7.1 and WE-09-3 (lists are guidance and the logged default), 11.13.1 (`/retire` or `end_game`; no word test),
  12.8.2 and PR-12-3 (leads told to the DM, nothing spawned), PR-12-5 steps 1-2 and the pronoun rule (no fitting by
  description; role, name and pronouns as the DM states; `as` default they, logged), PR-12-12 step 1 (triggers by ids;
  with tools code settles no testimony), 15.9.4 (WITNESS NEEDED told once per shortfall; nothing placed by code).
- Data (scratch `e_data.py`): `basic_verbs.yaml` `target_kinds` per verb (C1 table) and `covered_by` per `excludes`
  entry (every id checked present in licenses.yaml; empty where no license covers it: move's flight, talk's unheld
  tongue, ready's reactions; move adds `covered_by_effect: [eff.movement_mode]`); `resolution.yaml#reverses_goal`
  (persuade_to, learn: cost.closed_door); SCHEMAS.md for both. Trap hit: the working copy is CRLF and the first pass
  wrote LF lines into CRLF files; every edited file normalised to CRLF, and the helper now keeps the file's ending.
- Decisions (scratch `e_dl.py`): DL-06-40 (foe acts), DL-06-41 (start band, Force default), DL-01-60 (footing form),
  DL-01-61 (`reverses_goal`), DL-01-62 (`covered_by`, `target_kinds`, `approach`), DL-12-160 (leads and witnesses
  told), DL-12-161 (no deduction from words: targets, people, elements, testimony), DL-12-162 (retire). Each quotes
  VIII.9 and the owner's words; D1, D2, D3 quoted where they apply.
- Assemble, anchors, validator: `integration-assemble-appendix.py` (errors 0, warnings 0); `12-compile_anchors.py`
  (129 anchors; 8 hashes changed in anchors.yaml). First validator run: 1 ERROR (JRULES: 06.9.1 now `[J:enum]` without a
  Worst case line); added one (class i). Validator **0 ERROR / 0 WARN**. `engine/build/compile_cards.py` run last
  (2135 cards).
- Tests (full suite, 7 min): 2421 passed, 2 failed: `tests/replay/test_recorded_games.py` offline_seed11 and
  offline_seed11_dmtools diverge at turn 1 (narrator GUIDANCE 25190 -> 25390 chars: the changed rule cards). Expected for
  any rule-text change; not re-recorded here (rules lane; P1 runs in parallel; HANDOFF trap 5). The orchestrator
  re-records after merge.

## Rule text that told code to infer story state from words (grep and refs; T092 "retire")
Grepped chapters 00-12, 14-16 (not 13) for word overlap, keyword, regex, head noun, mention, from the narration,
spawn, first reachable, infer; checked `--refs` of 06.9.1, 06.9.3, 06.3.9, 01.13.7.
- Retired (edited): 06.9.1, 06.9.3, 06.9.4, 06.9.2, 06.9.7, PR-06-6, 09.7.1, WE-09-3, ch.07 intent (c) (code's
  choice for foes); 06.3.9, PR-06-1 (band from the scene); 01.13.7 (form); 01.9.3 (reversing phrases); 00.12.3
  (exclusion and licence from words); 01.2.5 (target by mention or recency); 00.6.6 (elements found in prose);
  PR-12-5 and the pronoun rule (fitting an existing NPC by description; role from the narration); PR-12-12 step 1
  (testimony triggers by words); 12.8.2, PR-12-3 (lead spawn); 15.9.4 (reserve placed in the world); 11.13.1 (retire).
- Already retired by earlier waves (no edit): 12.2.2 addressee by word overlap (DL-01-53), 01.4.1 already-true by word
  overlap (DL-01-45), 12.2.7 answered-question check (DL-12-101), 15.3 regex price (round 7).
- Checked, compliant, not edited: PR-00-7 (the narrator declares `new` lists: a model states); 06.5.3's into-a-feature
  `[J:flag]` (a model flag); 09's unmatched-creature rule (09 line 195: a judgment); 02.4.6 (reading is a stated
  method; the tools path states it with `reads`); 12.8.4 live-lead audit (state-based, not words; but its stalled-thread
  fallback bang fires from code: see the P5 checklist).

## Engine checklist (spec 033 phases)
- **P1 contract (now):** the plan's contract table still says REFUSED for `force` and `change fight` without `to`, and
  re-ask then nothing for `cost_form`; the rules now say default and log (D3): `force` push (`not_chosen:force`),
  `to` near (`not_chosen:fight.to`), `cost_form` the first listed option that can land (`not_chosen:cost_form`), `as`
  they for a person slot (`not_chosen:as`).
- **P2a** (positions, contact, fight start, costs): 06.3.9 and PR-06-1 step 2 (start band as stated; default near,
  logged); 06.5.3 (Force push default, logged); 01.13.7 (offer only the options that can land at the read severity;
  write exactly the pick; default as above); 01.9.3: `frame.reverses` reads `rules.resolution["reverses_goal"]`
  (persuade_to, learn -> cost.closed_door on the beat's target) and never `_UNDO`/`_REFUSE`/`_REVERSES` on the tools
  path.
- **P2b** (gate, necessity, frame, anchors): 00.12.3: `approach` resolves against every verb's `excludes[].what`; G2
  when the actor holds an id in `covered_by` or has an active effect in `covered_by_effect` (move's flight:
  `eff.movement_mode`); empty `covered_by` -> G3 redirect naming `needs` and the crude fallback; never
  `excluded_by`/`would_be_license`. 01.2.5: the target is an id, `"pc"` or an exact recorded name.
- **P3** (foes, answer turn): 06.9.1: the foe call runs after the exchange settles (D2); the FIGHT block lists T-06-16's
  legal acts per able foe (down, dead, fled: not listed). A missing foe, or a pick outside its list: the first row of
  its behavior list (09, else `conflict.yaml#default_behaviors` by role) whose act maps to a legal T-06-16 act, else
  `wait`; target the PC; logged `not_chosen:foes.<id>`. 06.9.3: a Dying PC is a legal target only for a `kill` side.
  Restrained foe's strike: close-quarters weapon (C4's ponytail: any weapon, logged). 06.9.2: the foe beat's target
  is the pick. An IDLE exchange runs no foe call. `conflict.foe_beat` stays pipeline-only.
- **P4** (people, testimony): `target_kinds` read from `basic_verbs.yaml` (replaces the `_PERSON_KIND`/`_THING_KIND`
  regex in `dm_tools.target_kinds`); PR-12-5: no `find_existing`, `new_npc` never reuses anyone, role and name as
  stated, `as` default they (logged), creature -> `mind: animal`; 00.6.6: no `write_mentions`; PR-12-12: no settlement
  on the tools path (`said` kept as given; the DM records facts).
- **P5** (leads, witnesses, retire): 12.8.2 and PR-12-3: a LEAD DUE fact (thread, source id, form) and the counter
  reset on telling; told after a pending roll resolves; "no open thread is on record" when none; never `inject_lead`.
  15.9.4: WITNESS NEEDED once per node per shortfall (a meta flag), never `audit_cases` placing; `new_npc`/`new_item`
  `knows: <node id>` takes the reserve. 11.13.1: `/retire` exact or `end_game`; no `is_retire` regex. Check that the
  tools path never reaches 12.8.4's stalled-thread fallback bang (a code-fired event).

## R2-M2: the attack roll starts the fight (owner ruling 2026-10-11, "Field on attacks")
- Cause: live-check-1 (0 fights in 4 games; only `change fight` started one; 6 strikes refused "no position recorded").
- Edited, tagged `[revision: R2-M2]`: 06.2.1 (new paragraph: the start-the-fight field on Strike, Grapple and Force; blank
  with no fight on = starts, logged `not_chosen:fight.starts`; default band engaged for Grapple, Force, melee Strike,
  the weapon's first band for a ranged Strike; `change fight` still starts one any time), 06.3.9 (default band),
  06.4.3 decision 1 (only a RECORDED band out of reach refuses; no band on record takes engaged, logged), 06.5.2,
  06.5.3, PR-06-1 (step 0 triggers; step 2 default). DL-06-42 added (DL-06-43/44 unused).
- Appendix re-assembled, anchors recompiled, cards compiled last. Validator 0 ERROR / 0 WARN. Replays not re-recorded.
- Engine (P8) to do: the field on attack tools; log `not_chosen:fight.starts`/`fight.to`; unrecorded band -> engaged
  for melee; refuse only a recorded band out of reach. GUIDANCE grew again: re-record replays once after merge.

## Handoff
- Done: R2-M (T090-T097; DL-06-40, -41, DL-01-60..62, DL-12-160..162) and R2-M2 (DL-06-42: attack roll states
  whether it starts the fight; unrecorded band = engaged, logged; only a recorded band out of reach refuses).
  Cards: 06.2.1, 06.3.9, 06.4.3, 06.5.2, 06.5.3, PR-06-1. Appendix, anchors, cards compiled; validator 0 ERROR / 0 WARN.
- Next: engine P8 (field on attack tools, defaults, logs); orchestrator re-records the two replays once after merge.
- Traps: working copy is CRLF; the plan's REFUSED cells for `force`, fight `to`, `cost_form` are superseded by D3;
  behavior-list defaults include non-melee rows (P3 skips rows outside T-06-16).
