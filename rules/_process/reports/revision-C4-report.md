# Revision C4 report

Agent C4. Rows: I-041, I-036, I-079, I-086, I-090 (ch.03, 08; 09's estimator for I-090).

## I-041 (MAJOR): daily rematch farms evidence and loot. Resolved.
- 03.5.4: the same-target window is the week (last 7 days) instead of the day when the target is not an enemy
  (standing Wary or better, party / hire / company, or a spar by agreement). An enemy who comes back still counts
  daily. PR-03-2 step 3, the tempting-case table (new row), WE-03-5 (the sergeant's rematch now counts a week
  later; a returning bandit captain counts next day) and `evidence.yaml#same_target_cap.non_enemy_window` follow.
- 03.5.5: a **spar** is defined (agreed, stopped at first defeat, no lethal harm mode). Its deed may still be judged
  evidence under the week window; it calls no `gen.loot` and the loser keeps purse and gear.
- 08.3.1: **once a season per creature**: a creature that gave loot carries `loot.given_on`; for one season it is
  spent (no drop check, no purse; only its present gear and its body). A side falls back to its highest-band unspent
  member. PR-08-1 step 1, 08.3.11 and 08's edge-case list ("The same foe again") follow.
- Departure from the ledger default: a consenting spar is not reduced to downtime training. A wager bout before a
  crowd is a real deed, and WE-03-5 already ruled it so; what broke was the daily cadence and the loot, both
  closed. DL-03-30, DL-08-34.
- Refs checked: 03.5.4 (03 PR-03-2, table, 04.3 line 336 cites only), 08.3.1 (PR-08-1, 08 edge cases, 09's worked
  loot line: one generation for the side, unchanged).

## I-036: the rules' coin sinks modelled, P3 item gap closed. Resolved.
- `08-campaign-sim.py` now runs four spending profiles on the same seeds at 12.7.7's two world weeks a session:
  `baseline` (I-018's lifestyle-only upper bound), `frugal` (08.8.10's lifestyles + training half the downtime weeks
  at 15's fee), `spender` (frugal + one hireling a band below, a holding a band with upkeep and staff, a commissioned
  masterwork a band from P3, job fees), `noncombat` (I-086). It also measures the tier held *during* each band.
- Finding: the "one tier ahead at P3–P4" was the tier at each band's **end**, which a PC drifting a tier a band
  reaches as it enters the next band. During the band, frugal and spender sit on 08.8.10's tier at every band;
  even the lifestyle-only baseline is +1 only at P4. 08.8.10 now says the typical tier is the tier held during the
  band. Sinks spent as priced take about 320 of 770 coins a P4 session (holdings the largest).
- P3 items: T3 trophy chance 30 → 25 (OEQ-08-2's own "lower by 5" rule). P3 median 12 (mean 12.3; was 13), P2 6, P4 23;
  every band within 08.2.7's row (P5 21 in 14 sessions of an open-ended band, 25 near session 73). Generator
  `08-gen_data08_part2.py` changed and re-run (`gen_loot.yaml` only diff); `08-loot-sim.py` re-run (T3 rate 26.6%)
  and T-08-16's 1,000-drop rows and 08.2.5's share figures updated; 08.3.3, PR-08-1, OEQ-08-2, T-08-17 (rewritten
  with a profile table), OEQ-08-4 (answered). DL-08-35.
- Rejected: restating 08.2.7's P3 row (the drop check is the lever the table's revisit rule names).

## I-086: non-combat income curve. Resolved.
- New `economy.yaml#job_fees` (generator) and 08.8.8 bullet: a patron's job pays on completion a fee by its
  challenge band (03.4.3): 40 / 85 / 200 / 600 / 2,000 (four weeks of the band's hire wage). Half up front below
  Warm; failed job keeps the deposit; bargaining moves a notch. 08.8.9 rule 6 and AI-6 list job fees.
- 08.8.10's table gains a non-combat income column and a job-fee column; the fighting column now counts a job fee
  per ~5 sessions. Sim `noncombat` profile (no fights, half the site treasure, fees, work weeks): during-band tier
  W1 / W1–W2 / W3 / W4 / W5 (on the table, P2 at the W1/W2 line), so the scholar's W1–W2 plateau is gone. DL-08-36.
- 11's quest row ("a faction's commission ... by the job") and 15's Payment terms should cite `job_fees`: new row
  I-091 (ch.11/15 are not mine).

## I-079: materials outside market depth; crude repair on masterwork. Resolved.
- 08.8.5: trade goods and materials get a depth of their own (same figures a week), except materials sold to a
  crafter for a commission or project the PC can name, up to what that work needs; glut still applies. Generator:
  `economy.yaml#materials_depth_per_week`, AI-4 restated (regenerated; economy.yaml only).
- 08.6.7: crude repair (Handle; field-patch abilities likewise) on worn, common or fine items only; masterwork,
  wondrous and storied items need their lasting repair. Row renamed "damaged (crude repair)", "quality unchanged";
  08.1.9's mend column and PR-08-9 follow. WE-08-4 (24 coins of materials in a town) and the crude-repaired common
  sword example stay valid. DL-08-37.
- Departure: one depth pool for everything was rejected (a hide sale would crowd out a sword sale).
- 01.13.4's S3 row summarizes crude repair without the limit: in new row I-092 (01 is not mine).

## I-090: lingering harm on items and on adversaries. Resolved.
- 08: `08-gen_data08.py`: Rending (bleeding) and Ember-touched (burning) apply 2 stacks a proc at tiers 1–3 and 3 at
  tiers 4–5 (chance, slot unchanged). New `08-onhit-value.py` (06's engine imported; x1 reproduces K1's 0.67 EU):
  2 stacks 1.14–1.17 EU, 3 stacks 1.41–1.58, inside the family's 1–3 EU (was 0.67, below every member). Ember oil
  applies no burning (its tuple's condition is unused), so it needed no change. `item_properties.yaml` regenerated
  (two entries); `08-loot-sim` output byte-identical. DL-08-38.
- 09: the estimator ignored riders and every rider cost 0.06. New `09-lingering-rider.py` (09_core's fight plus
  stacks on the PC; never / always / smart answers, the PC's best kept): premium 0.09–0.19 by band, mean 0.15;
  the PC's best answer is to end it at once. T-09-6 / 09.4.3: lingering-harm rider 0.15. PR-09-4 step 2–3 and
  `09_core.estimate`: such a foe costs the PC its third Strike × 0.6 in the share of rounds it lands a hit (0.6 fitted:
  win shift −12.0 / −13.5 at P4 / P5 vs simulated −12.7 / −14.5; the simulated word at all five bands). Lines with no
  rider estimate exactly as before. `09-gen_data09.py` + `integration-merge.py` re-run: 14 adversaries' calibration,
  10 lose 1–2 Vitality; T-09-12b updated by script (vrock trivial → easy, vat titan hard → lethal). DL-09-26.
- Merge note: ch.09 is also being edited by the 09–11 agent; my 09 edits are 09.4.3, T-09-6, PR-09-4 steps 2–3,
  ten T-09-12b rows, `09_core.py` (estimate/pc_rate), `09-gen_data09.py` (PREMIUM, line `ling`), `DL-09-26`. If the
  other agent took DL-09-26, renumber. After merging, re-run `09-gen_data09.py` then `integration-merge.py`.
- ch.13's merged regional adversaries (`adversaries.13` block, built from 09's build()) keep the old premium; ch.13
  is unmaintained (not edited).

## Close-out (done)
- DL entries: DL-03-30, DL-08-34..38, DL-09-26. `appendix/decision-log.md` re-assembled with
  `integration-assemble-appendix.py` (no trace fragment changed, so `traceability.md` is unchanged).
- `12-compile_anchors.py`: 129 anchors, 0 errors, 0 warnings. `validate_ruleset.py`: 0 ERROR / 0 WARN.
- Generators re-run: `08-gen_data08.py` (economy, gen_loot, item_properties), `09-gen_data09.py` +
  `integration-merge.py` (adversaries, archetypes). Sims, seeded, outputs committed: `08-campaign-sim.py` (300 ×
  70), `08-loot-sim.py`, new `08-onhit-value.py` (seed 606) and `09-lingering-rider.py` (seed 909).
- New rows: I-091 (11/15 should cite `job_fees`), I-092 (01.13.4 and `ab.field_patch` should state the crude-repair
  quality limit; ch.13's regional adversaries keep the old rider premium). Parallel agents may also have used
  I-091/I-092 or DL-09-26: renumber on merge if so.
