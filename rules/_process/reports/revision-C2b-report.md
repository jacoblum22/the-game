# Revision C2b report

Agent C2b. Rows: I-034, I-089, I-087, I-047. Nothing committed; ch.13 untouched.

## I-089 + I-034: pacing on the advisory-offset model (resolved)
- **Decision: keep the targets, retune the thresholds.** 04's Design intent makes the targets the design (chosen
  before calibration, R2 #2) and the thresholds the calibration ("scaled to this game's event rate by simulation and
  never copied"). DL-00-05 changed the event rate, so W moves. New `04-binding-check.py` (output committed) shows
  the weighted total is the requirement met last at tiers 3–5 (145–194 of 200 runs), the quality floor at tier 2;
  the since-fields do not bind, so they stay.
- **Ladder** (tiers 2–5 only): narrow 80 / 160 / 340 / 640 / 1,200; fine and hybrid ×¾ (60 / 120 / 255 / 480 / 900);
  broad ×1½ (120 / 240 / 510 / 960 / 1,800); counted W ÷ 10. Changed in `04-recog04.py`, `04-gen_data04.py`,
  `04-callings_header.yaml` → `callings.yaml` (regenerated; only the 16 ladder rows and a comment changed),
  `03-counted-yield.py`.
- **Result** (`04-recog04-output.txt`, 200 seeds): archer 5 / 10 / 18 / 32 / 54, p10 at tier 5 = 50, 183 of 200
  within 60 (was 5 / 12 / 23 / 40 / 60, 103 of 200). Swordsman 3 / 7 / 12 / 20 / 34.
- **Parity.** With the faster ladder the smith's tier 3 in seeded worlds was 22 against the archer's 16 (+38%):
  a whole work was one opposition, so three scenes at a masterwork banked two great deeds. Fix: a work is one
  opposition **per scene** (04.3.4, 08.6.4, 03.4.3's record, `evidence.yaml`; `04-recog-parity.py`). A work's steps
  are bounded by its clocks, as a fight's by its encounter; the I-039 farming envoy still banks 0. Now: I-003 shape
  archer 15 / 47, envoy 14 / 42, smith 14 / 40, scholar 14 / 42 (within 15%); seeded worlds (T3 / T4 / T5) archer
  16 / 28 / 48, envoy 16 / 27 / 45, smith 17 / 27 / 44, scholar 16 / 27 / 45 (within 8%).
- **Text refreshed:** 04.3.4 (table, note), 04.3.3 (counted list), 04.3.5 (R1 table and reading, parity tables),
  04.2.4 (R4 acceptance), 04.4.2 (K-table rates and calibration from `04-feat04`/R7), Design intent calibration line,
  T-04-8 (all rows; seeded-parity row renumbered R13, it duplicated R12; R14 new), OEQ-04-1, WE-04-1 (rewritten from
  `04-wren04-output.txt`, seed 7, every number re-checked against the run, including that the crisis in scene 80
  is what completed Archer 3 and that Ranger 5 fails on 87 of 90 counted wilds units). Quotes elsewhere: 03.4.3,
  03.7.3, OEQ-03-4, 03's calibration note, 08.6.4 item 6, 09.12.3 and 09's interface note (historical figures kept,
  current ones added; `09-i005-check.py` now prints both ladders, first block byte-identical to the old output),
  12.7.7 and `pacing.yaml#world_time` (re-run `12-time-pacing.py`: tier 5 at 2.0 / 2.5 world years), ch.15's
  social-contest why-note, `04-recognition-sim.md`.
- **On-demand NPC band** (12.11.1, 00 NPC schema): `band` 1 at walk-on/recurring; a principal takes its home area's
  band (12.16.8), never lowered; a record that already has one keeps the higher; a faction's tier is never written
  in (03.4.3 lends it only to a binding party). DL-12-32.
- DL-04-32, DL-12-32.

## I-047: training licences (resolved)
- 05.9.3: taught competence entries capped at learning picks + highest confirmed calling tier (minimum 1); past
  the cap a licence is held as access; training an access-held licence is deepening, within the cap. 05.9.4's
  "no cap" sentence now says the cap is on the +2, not the licences. `licenses.yaml#training_competence_cap`,
  emitted by `05-gen_data05/emit05.py` (`gen_data05.py --emit` then `integration-merge.py`; only that key changed).
- 03.7.3: counted units written outside a scene settle per day (`cnt.progress`, `cnt.made`, Safe projects included).
- DL-05-37.

## I-087: thin tier-5 pools; successor tags (partial, row left open)
- (b) resolved: Train-a-Successor banks three **different** tags (11.13.10 item 4 and the activity, 02.2.7 item 4,
  03.2.8, `legacy.yaml#train_successor`). DL-11-28.
- (a) audit added: validator check 11 `POOLS` (INFO). Current data: 123 of 132 deed-keyed specialist callings have
  fewer than six own-pool abilities, 92 have no own-pool tier-5 ability; 43 of 81 level-2 deed nodes have no pool
  ability at min_tier 4+ (listed by `validate_ruleset.py -v`). The ledger's "19 vow/dark callings with no tier-5
  ability" does not reproduce: every vow/dark axis has a tier-5 oath ability on its pole.
- **Handoff (not done):** author at least one tier-4 or tier-5 pool ability per level-2 node in the INFO list, in
  `rules/_process/simulation/05-gen_data05/ab_<branch>.py`, then `gen_data05.py` (budget, grammar and lint checks)
  and `gen_data05.py --emit` + `integration-merge.py`; start with the lore, guile and martial nodes. This is about
  43 budget-checked abilities with text, outside this budget. When the INFO shows 0 nodes without tier 4+, close
  I-087.

## Close-out
- `integration-assemble-appendix.py` re-run (decision-log and traceability); `12-compile_anchors.py`: 129 anchors,
  0 errors, 0 warnings. Validator: 0 ERROR / 0 WARN (INFO: POOLS 2, REFS-EX 9, REFS-MD-EX 70).
- Sims re-run and outputs committed beside them: `04-recog04`, `04-recog-parity`, `04-wren04`, `04-feat04`
  (byte-identical), `09-i005-check`, `12-time-pacing`, `03-counted-yield`, new `04-binding-check`.
- New ledger rows: none.
