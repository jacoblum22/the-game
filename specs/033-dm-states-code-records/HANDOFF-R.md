# HANDOFF 033 phase R (rules lane only; engine/ untouched except the compiled cards.json)
Done (T090-T097), revision R2-M; full report and engine checklist: `rules/_process/reports/R2-M-report.md`.
- DL-06-40 foe acts: the DM picks act, target and nonlethal per able foe AFTER the PC's result (D2), from new T-06-16
  (legal acts by state, cases C4); omitted or outside the list = first legal behavior-list row, target the PC, logged
  `not_chosen:foes.<id>`. 06.9.1 rewritten (old rationale kept as a watch; passivity measure), 06.9.2-06.9.4, 06.9.7,
  PR-06-6, 09.7.1, WE-09-3, ch.07 intent (c).
- DL-06-41: 06.3.9 the DM states the start band, default near logged `not_chosen:fight.to`; 06.5.3 Force default push
  logged `not_chosen:force`. DL-01-60: 01.13.7 the form is the DM's pick after the roll among options that can land;
  default the first listed that can land, logged `not_chosen:cost_form`.
- DL-01-61: `resolution.yaml#reverses_goal` (persuade_to, learn -> cost.closed_door); 01.9.3 reads ids, not words.
- DL-01-62: `basic_verbs.yaml` `target_kinds` per verb and `covered_by` (licence ids) per `excludes` entry; move's flight
  `covered_by_effect: [eff.movement_mode]`; 00.12.3 `approach` is a stated field.
- DL-12-160 leads (12.8.2, PR-12-3) and witnesses (15.9.4) are told, never spawned; DL-12-161 no deduction from words
  (01.2.5, 00.6.6, PR-12-5, pronoun rule, PR-12-12); DL-12-162 retire by `/retire` or `end_game` (11.13.1).
Gates: validator 0 ERROR / 0 WARN; appendix assembled; anchors recompiled; cards compiled last. Full pytest: 2421 passed,
2 failed (replay offline_seed11 and offline_seed11_dmtools: narrator GUIDANCE grew with the changed rule cards).
Traps: (1) re-record those two recordings once, after merge, from one phase only. (2) The plan's contract-table cells
REFUSED for `force` and fight `to`, and the re-ask for `cost_form`, are superseded by D3 in the rules (P1 to align).
(3) Behavior-list defaults hold non-melee rows (Windup, Flank, Reload): P3 skips rows outside T-06-16, else `wait`.
(4) 12.8.4's stalled-thread fallback bang is code-fired: P5 checks the tools path never reaches it.
