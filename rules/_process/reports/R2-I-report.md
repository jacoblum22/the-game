# R2-I report: the round-4 fixes (R1, R2, R3, R5, setting once, patches)

Revision R2-I. Rule edits tagged `[revision: R2-I]`; decisions DL-12-96.. (ch.12), DL-01-36.. (ch.01). Owner
direction 2026-10-09: keep the group and movement fixes light, mostly removing friction instead of adding rules.
Appended after every step.

## Progress
- Setup: worktree reset to milestone-1-playable (be8192e). Read CLAUDE.md, ROUND4-ANALYSIS.md, R2-H report.
  Baseline validator 0 ERROR / 0 WARN.
- Survey: PR-12-10, 12.10.8, 01.2.5, 01.2.7, 12.2.2, 12.2.4, 12.14.11-13, 12.3.1b, 01.4.1, T-00-5, T-12-18, T-12-11,
  12.4.3, 01.18.4/5, 15.9.6, 12.16.9, PR-01-1, PR-06-4; data `resolution.yaml#intended_change`, `pacing.yaml`
  (`answer_ladder`, `narration`, `details.scene_writes`, `claim_check.speech_checks`); engine readers checked (new
  data keys are safe: no strict schema on these blocks).
- Rule text (23 asserted edits, scratch script `r2i_rules.py`): PR-12-10 step 4 and 12.10.8 (plain speech; no
  self-introduction); 12.2.2 target; 12.14.13 (description and ordinary-found notes); T-12-18 Move row; T-12-11
  engaged words; 12.4.3 (travel frames the arrival; look given once); 12.2.4 Narrator row; 12.14.11 setting once;
  12.14.12 optional material; 12.3.1b item 1 (PC words in attributions); 01.2.5; 01.2.7 (description slots, move_to
  row, before framing, partial move_to); 01.4.1 (already true, approaching); PR-01-1 steps 1 and 3; 01.18.5 (looking
  for); T-00-5 two everyday rows; 15.9.6 (a case's target).
- Data, DL and sim wording (17 edits/appends, `r2i_data_dl.py`, YAML parse checked): `resolution.yaml#intended_change`
  (`move_to.applies`, reach-1 text, new `descriptions`, `before_framing`); `pacing.yaml` (`verb.move` comment,
  `speech_checks` comment, `freshness.setting_once`, `optional_material += place_look_after_framing`,
  `answer_ladder.register`, `.self_introduction`). New DL-12-96..100 and DL-01-36 (owner quoted); DL-12-90 and DL-01-34
  superseded in part. Sim `12-answer_ladder_sim.py`: only its wording assumed hedged answers; re-run, output differs in
  that one line, numbers unchanged, PASS.
- Assembly (decision log; traceability unchanged), anchors (0 errors, 0 warnings), `engine/build/compile_cards.py` last
  (2133 cards). Validator 0 ERROR / 0 WARN (INFO unchanged: BASIS 1, POOLS 2, REFS-EX 9, REFS-MD-EX 70).
- Tests (no engine code changed; `cards.json` recompiled): `pytest -q` with the replay test deselected: 1765 passed,
  4 skipped. `tests/replay/test_recorded_games.py` diverges only through CORE RULES text, as in R2-G/R2-H: re-record at
  merge.

## Results
- **R1** (DL-12-96): PR-12-10 step 4 and 12.10.8: plain speech with ordinary confidence; a hedge is characterisation.
  R2-H's hedged-hearsay clause deleted. DL-12-90 superseded in part.
- **R2** (DL-12-97): a target / `whom` / `what` may be an unnamed description (01.2.5, 01.2.7, 12.2.2, 12.14.13); a
  change on it is a scene fact; no group entity, no spokesperson; consequential means the case or casting picks.
- **R3** (DL-12-98): approach = one beat, no roll unless obstructed, ends beside (01.4.1, T-00-5, T-12-18, T-12-11,
  01.2.7); bands step by step only in a conflict. Looking for: ordinary found as written (T1a), consequential by the
  case (01.18.5, 12.14.13, 15.9.6); no find procedure. Travel frames the arrival (12.4.3; P-098).
- **R5** (DL-01-36): already true = `trivial`, no roll, no OFFER; no valid target resolved before framing; no roll
  with nothing to deliver (01.2.7 step 1, 01.4.1, PR-01-1). No new necessity reason (so ch.03 / evidence untouched).
- **Setting once** (DL-12-99): look/furniture/exits on arrival and framing, then optional material marked described
  (12.4.3, 12.2.4, 12.14.11, 12.14.12).
- **Patches** (DL-12-100): no self-introduction unless asked (PR-12-10 step 4); PC words inside a speech attribution
  are `pc_agency` (12.3.1b item 1).
- **Simplified or deleted**: R2-H's hedge instruction; band-by-band movement outside a conflict; the move_to one-band
  partial form outside a conflict; the seeded look in every turn's view. Not added (rejected per owner): group
  entities, spokesperson rules, a `find` procedure or change kind, a new necessity reason.

## Notes for the orchestrator
- Decided here: the approach ends at `band.engaged`, worded "beside" outside a conflict (T-12-11), because a Strike or
  Grapple next needs engagement and Talk does not care; "already true" reuses reason `trivial` (it cannot fail) to
  avoid an enum change across 00.13.1, ch.03 and `evidence.yaml`.
- 12.10 needed no edit: R3's finding rule sits in 01.18.5 (Observe, "look for"), 12.14.13 (T1a) and 15.9.6.
- No issue-ledger entries: the round-4 findings are not in the ledger; the DL entries carry the evidence.

## Engine checklist: spec 018 (items 1-6)

### 1. Plain speech (R1)
Files: `engine/dm/packet.py` (speaker card header, lines ~540-542), `engine/dm/roles/narrator.py` (prompt lines ~153,
~163), `engine/dm/answer.py` (`guarded` wording, line ~49).
- **Retire** "beyond it, hearsay or a guess, hedged" and "answer from hearsay or a guess" in the speaker card; say
  "beyond it, answer plainly with ordinary confidence (`answer_ladder.register`); a hedge only if the character is
  cautious or gossipy". Same in the narrator prompt (drop "hedged as people do ('I heard...', 'probably...')").
- `guarded` keeps "a part of it, short", drop "hedged". `prompts/testimony.md` (strip hedges when stating a claim)
  stays as is.

### 2. A target can be a description (R2)
Files: `engine/dm/schemas.py` (Reader `change.what` / `whom`, beat `target`), `engine/dm/roles/reader.py`,
`engine/resolve/change.py` (lines ~115-117 refuse a slot not in `st.entities`), `engine/dm/oof.py` (OFFER/RESULT words).
- Reader: a slot is an id from scope **or** a short description string (`resolution.yaml#intended_change.descriptions`);
  keep the enum for ids, add a free `description` alternative (Laya log: record which).
- RECORD: a description slot writes a scene fact `{subject: "<description>", predicate: <kind's applies>, scope:
  scene}` instead of refusing ("the refugees are willing to talk"); `persuade_to` on a description writes that fact,
  not `npc.<id>.agreed`. The narrator voices a walk-on for it.
- Consequential: if a case placement or story role matches the description (`answer.py`'s `case_about` / `who_case`,
  casting `cast_who`), pick that individual and treat the slot as the id. **Do not** add group entities.
- Test: "persuade the refugees to show themselves" applies on success (fact written; no "no one named to persuade").

### 3. Movement and finding (R3)
Files: `engine/resolve/necessity.py`, `engine/resolve/pipeline.py` (`_BAND_WORDS`), `engine/dm/scene_state.py`,
`engine/resolve/change.py` (`move_to` is an OWN_WRITER), `engine/resolve/conflict.py` (`set_position` path),
`engine/dm/packet.py` (`scene_setting`), `engine/dm/roles/narrator.py` (`scene_open` purpose).
- **Simplify**: outside a conflict, `move_to` toward a present person or thing writes `band.engaged` in one beat
  (reach 2 for a no-roll beat; a rolled, obstructed approach at reach 1 = part of the way); render engaged as "beside"
  outside a conflict. **Retire** the one-band-per-Move step outside a conflict (spec 015's deferred limitation).
- Necessity: an approach is Move / open ground → `trivial` unless 01.4.1 decision 2 finds a hostile watcher or an
  obstacle on the way (existing flags).
- Looking for something absent: the Reader types it as Observe (`learn` or `none`), never `move_to` toward the place
  the PC is in. Ordinary → the narrator writes it as T1a (no roll unless an obstacle/danger/clock); consequential
  (matches a case target) → the case's placements and leads (`answer.py` consequential route / `deliver_node`).
  Guard: refuse a `move_to` whose place slot is the PC's current place and retype as a look.
- Travel: a `move_to` to another known place opens a scene with purpose `scene_open` at the threshold (12.4.3) and
  narrates the arrival; the bare beat line "You try to reach X. It works." (`engine/dm/handles.py` render,
  `engine/llm/offline.py` degree words) must not stand in for it (P-098).
- Tests: four "keep looking for the refugees" turns never produce "a few strides short"; approaching a present NPC is
  one no-roll beat; travel to Marlwall narrates an arrival.

### 4. Already true needs no roll (R5)
Files: `engine/resolve/change.py`, `engine/resolve/necessity.py`, `engine/dm/adjudication.py`, `engine/dm/oof.py`.
- Before FRAME: a `would_be_noop(change, state)` check (actor already holds the item; `npc.<id>.agreed` already holds
  the same act; the thing already open/closed; actor already beside) → necessity `trivial`, no roll, **no OFFER**;
  narrate as already so (`resolution.yaml#intended_change.before_framing.already_true`).
- No valid target and no description → ask "who?" (the one clarifying question, 01.2.5) before framing, never a roll.
- Test: "persuade Ivas" after her `agreed` fact for the same act → no roll, no OFFER.

### 5. Setting once
Files: `engine/dm/roles/narrator.py` (line ~508: `scene_setting(st)` added for purposes `turn`, `scene_open`,
`opening`), `engine/dm/packet.py` (`scene_setting`), `engine/dm/roles/narrator.py` `optional_material`.
- Give `scene_setting` only for `scene_open` / `opening` and the first `turn` after arrival at a place; then mark the
  place `described` (a usage mark per 12.14.11) and, on later turns, list the look and furniture under optional
  material as "already described" (`narration.freshness.setting_once`, `optional_material: place_look_after_framing`);
  show it again only when the PC looks around or asks.
- Test: five turns in one place carry the look line in the packet once.

### 6. Speech patches
Files: `engine/audit/claims.py` (speech checks), `engine/dm/narration.py`, `engine/audit/screen.py`,
`engine/dm/packet.py` / `engine/dm/roles/narrator.py` (prompt).
- Self-introduction: narrator prompt line "never open an NPC's speech with their own name or title unless asked"
  (`answer_ladder.self_introduction: never`); optionally a cheap scan: speech span whose first clause contains the
  speaker's stored name or role title with no `who is` question this turn → redraft.
- PC words: run `no_words_in_pc_mouth` over every speech span **and its attribution clause**: a quoted span attributed
  to "you" or embedded in an NPC span ("'Fair enough,' you say, and she nods") is checked against the player's message
  like narrator voice. Test: the "Fair enough" case from the 20261008 fighter run is caught.
