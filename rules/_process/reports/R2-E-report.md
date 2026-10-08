# R2-E report: memory (established details, spotlight, scene cards, role views)

Revision R2-E (rules half of spec 009). Rule edits tagged `[revision: R2-E]`; decisions DL-12-70.. .
Appended after every step.

## Progress
- Setup: worktree reset to milestone-1-playable (91fc837). Read the synthesis (1, 3, 4, 5 Phases 3-4, 7), all of
  lane A, lane B P2 and P6, the R2-A and R2-B reports.
- Step 1 (plan): DLs in fragment DL-12 (DL-12-70..76; ch.00's DL-00A lives in the hand-written head of decision-log.md, so the ch.00 decision is recorded as DL-12-70 like R2-B's DL-12-40). OEQs numbered OEQ-12-20.. to stay clear of R2-D. P-rows live in evals/playtests/ISSUES.md (out of scope), so the playtest evidence is cited in a new ledger row I-170 (numbered clear of parallel waves).
- Step 2 (rules): ch.00: 00.6.2 Fact shape (`certainty` gains `narrated`; `persistence` for details), 00.6.6
  (existing elements diffed), new 00.6.6a (established details), PR-00-7 step 2 (profile diff for existing
  entities), OEQ-00-6 annotated. ch.12: 12.2.4 item 3 (profiles, spotlight, scene cards; scene-detail salience,
  spotlight relevance; per-role projection) and a per-role view table after item 5; 12.3.1 (identity and position
  rows check `detail.*`; diff audit with the 1-in-10 full extraction and the < 0.3 skip gate; `narrated`
  certainty); 12.4.8 (step 4 sweep includes declared sentences; new step 8 scene-detail expiry, step 9 scene card;
  the record close is now step 10); 12.5.3 (recap from cards and chronicle); 12.6.6 (one line); 12.14.2 (one line);
  12.14.11 (usage marks); 12.14.13 (one line); PR-12-1 T8 and T12; OEQ-12-1 annotated; OEQ-12-20..23 added.
  Edits by a scratch script with asserted unique matches.
- Step 3 (data): `pacing.yaml` (hand-written): `packet.spotlight_k` 4, `packet.max_scene_cards` 2,
  `view_budget.spotlight` 400 and `scene_cards` 300, `claim_check.audit` (diff, 1 in 10, skip gate 0.3,
  `skip_enabled: false`), a new `details` block (max_active 8; 15 slots with their persistence; salience),
  `narration.freshness` keyed on `last_used`. Parsed and asserted.
- Step 4 (DL, ledger): DL-12-70 (established details; D1; D8 assumed, owner to confirm), DL-12-71 (diff audit,
  skip gate < 0.3), DL-12-72 (scene-state details by code, expiry), DL-12-73 (scene cards; recap from cards),
  DL-12-74 (spotlight K = 4), DL-12-75 (per-role views), DL-12-76 (freshness on `last_used`). Ledger row I-170
  (resolved for the rules half; cites P-063, P-073, P-127, P-085, P-037, P-030, P-094 as evidence; the P rows in
  `evals/playtests/ISSUES.md` were not touched, evals/ being out of scope).
- Step 5 (close-out): appendix re-assembled, OEQ appendix rebuilt (144 questions), anchors 129 / 0 errors /
  0 warnings, the per-role table moved after 12.2.4's *Why four.* paragraph, validator 0 ERROR / 0 WARN.
  `engine/build/compile_cards.py` run last.

## Notes for the orchestrator
- 12.6.6 needed only a cross-reference line: 12.2.4 item 3 (R2-A) already orders threads and the known cast by
  12.6.6 weight, and the engine does it.
- With one value per slot a person has exactly 8 `lasting` slots, so D8's cap of 8 binds only if the list widens
  or a slot carries several values. Recorded in DL-12-70 and OEQ-12-20 for the owner.
- Numbering kept clear of R2-D: OEQ-12-20..23, ledger I-170. Renumber at merge if preferred.
- T-12-1 (the always-loaded checklist) was left unchanged, as R2-B did, to keep the cached prefix stable.

## For the engine spec (009)
- Store: `certainty` gains `narrated` (`engine/store/events.py` Literal); details are facts `detail.<slot>` with
  `persistence` (lasting | scene | beat). A projection index `details[eid]`: slot -> fact id, `last_used` turn.
  Slots and persistence come from `pacing.yaml#details.slots`; cap `details.max_active` (8), ranked by salience
  (2 seeded, generated or cited, else 1) then `last_used`; archived details stay in the contradiction scope.
- Write-back (`mentions.py::_one` on reuse): diff each stated property against the profile: empty slot -> write
  (`narrated`), same -> no-op, different -> `identity` (lasting) or `position` (scene) failure unless this turn's
  record holds an explaining event (then supersede). Never write a `scene` slot from prose; a subject with no id
  is not written. Existing `detail`/`appearance` facts map to a slot on first read.
- Code writes scene slots (held, manner, posture, activity) from resolved beats and 12.11.9; a small per-verb
  outcome table (posture, hold) is still owed (owner: rules, not written here). Scene end: supersede all scene
  details and activities (12.4.8 step 8), then build the scene card (step 9) from the log; record close is step 10.
- View (`packet.py`): compact profiles with `(used last turn)` marks; spotlight in the order of 12.2.4 within
  `view_budget.spotlight` (400), as the PC knows it, added to `checker_ids`; at most 2 scene cards
  (`view_budget.scene_cards` 300) from outside the verbatim window; scene detail salience 2; spotlight counts
  for relevance (+2). `view_for(role)` per the 12.2.4 table; leak test on every Narrator packet.
- Checker: diff mode per `claim_check.audit`; full extraction 1 turn in 10 (RC-RNG); `skip_enabled` stays false
  until `evals/longhorizon.py` shows < 0.3 undeclared assertions per turn and recall >= 0.8 (OEQ-12-23). The
  scene-end sweep includes declared sentences' claims.
- Freshness: set `last_used` at RECORD (T12) for details, written words and speech openers; retire the image
  regex, keep the opening-clause and speech-opener scan. Recap (12.5.3) reads cards and chronicle; every
  sentence cites a card field or chronicle entry.
- Harness: OEQ-12-20..23 and the extended OEQ-00-6 / OEQ-12-1 name `evals/longhorizon.py` as their test.
