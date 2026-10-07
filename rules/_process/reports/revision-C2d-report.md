# Revision C2d report

Agent C2d. Rows: I-033, I-043, I-044, I-058 (ch.00, 03, 04, 05). Brief: `_process/REVISION-AGENT-BRIEF.md`.
Baseline: `gen_data05.py` reproduced the committed data before any edit (`--emit` alone drops the merged owner
blocks of `composites.yaml`/`licenses.yaml`; `integration-merge.py` restores them, as C2b/C2c recorded).

## I-058 a healer may heal herself (done)
- Ledger default adopted, made general instead of Mend Flesh only: 05.7.8 now says a healing that applies to a
  being the caster touches, or to a being within a band, may target the caster herself unless the ability says
  otherwise; she is the recipient and counts against her own 2-healing cap. *Mend Flesh*, *Purge* and *Renewal*
  (every "one living being you touch" healing) say "yourself included" in their limitation, edited in
  `05-gen_data05/ab_divine.py` and `ab_primal.py` and emitted. *Drain Life* already heals "self".
- Why general: the same silence sat in every touch healing; fixing one name would leave the AI DM to infer
  the other two by analogy.
- Refs checked: 05.7.8's refs (DL-05-23, the ab.* exclusions naming "the healing cap (05.7.8)"), 16's acolyte
  (`ab.mend_flesh` id only), `gen_item_ability.yaml` (carries no limitation text: unchanged). DL-05-39.

## I-043 promotion criteria at content scale (done)
- Ledger default adopted with the owner made exact. 00.16.3 gains a `[D]` promotion test: applied in 20
  evidence-bearing scenes over 2+ sessions, no overturned ruling citing it (12.12.4's classes: correction,
  upheld dispute, ruling-error correction), not named in an open review-list candidate; an overturn restarts
  the count. `pacing.yaml#review.promotion` holds the numbers.
- Who promotes: `h.12.session_close` lists candidates in the review list (12.12.4). The ledger's "PR-00-8" is
  the authoring procedure, not a list; the review list is 12.12.4's. Campaign-written entries (world seed,
  improvised content, adopted rule candidates) are promoted by the engine when listed; shipped entries only by
  the maintainers' verification wave, with play's review lists as evidence (05.12.3 now cites the test). A
  permanent entry is never demoted (a fault means retirement and a successor).
- 20 is not a balance number: it is placed between 04.8.2's 12-scene confirm and 24-scene lapse windows, and
  argued in the rule. No sim.
- Refs checked (`--refs 00.16.3`, 27): the data-file header comments ("Every entry lifecycle: provisional
  (00.16.3)") stay true; 12.16's world seed (its entities start provisional), 12.12.6 (rule candidates enter
  provisional), 11's "no faction is deleted", 05.12.3 (edited), 00.17 Q12 (content vs character scale:
  unchanged). DL-00A-31 (in `decision-log.md`'s hand-kept 00 head; 00 has no fragment).

## I-044 oversized level-2 deed sets (done)
- Ledger default adopted (keep the tree, add the test), widened: `data/tags.yaml` has five level-2 sets over 8,
  not three: martial 12, arcane 11, craft 11, **lore 9, influence 9**.
- 00.2.2 names them as an admitted exception: 03.1.5 classifies level by level, and its worst case bounds a wrong
  child to a sibling under the right branch, shown in the OFFER; regrouping would rename seeded level-2 tags,
  which 00.5.5 forbids. No further level-2 child joins them (PR-03-6 step 6; 03.1.3 notes its two additions
  sit inside the exception). Level-3 sets all hold 8 or fewer (checked).
- OEQ-00-1 gains a level-2 stratum: 12 actions per oversized branch (60), 3 runs, ≥ 70% child agreement within
  each branch (not pooled, so one weak branch cannot hide in the average), no sibling pair confused in over 10%
  of its branch's actions; a miss rewrites the pair's tests and retests, a second miss makes that branch's CHILD
  step stop at the branch until a 00 amendment regroups it.
- Refs checked: PR-03-6's refs (03 tag reconciliation, 04's retired-tag carry: unchanged), 00.2.2's DL citations.
  DL-00A-32.

## I-033 lingering conditions re-priced with a condition-aware fight model (done)
- **Model.** `06-conflict-sim.py` now gives foes condition instances: burning and bleeding with stacks
  (intensify, max 3, a new stack refreshes the duration, 00.9.2), the applying effect's duration (one round
  or the scene), 1 Vitality a stack at the bearer's turn end (unreduced by worn armor), and the **bearer's
  action to end it** (one of its two; burning no check, bleeding Handle vs DC 10) under a policy parameter
  `never` / `always` / `smart`. Each K row is played under all three and keeps the least: the bearer's best
  answer. The old model let burning burn for ever, with no bearer action. Spells gained a harm edge. Every
  earlier row reproduces except J4's Flame Lance rows (now `never`; 2xT3 26.8 → 27.3 and 2xT2 91.8 → 92.0,
  because a foe dropped or bloodied by burning now ticks morale like any other).
- **K1 (price).** A 1-Focus spell at the working's severity, plus one rung (= the push) or plus a condition,
  at P1/P3/P5 against one foe a band up and two foes at band. Pooled rung gain is 98.3 points (= 2 EU). One stack
  for the scene is worth **0.67 EU**, for one round **0.40**, and two stacks **1.14**. Burning and bleeding come
  out identical. The bearer's best answer is to ignore it (`never`): beating out 1 Vitality a turn costs half an
  attack.
- **Rule.** T-05-9: burning and bleeding leave the middle group (2 +1 beyond a round, so 3 for the scene) for a
  **lingering harm** row at 1 EU a stack, whatever the duration (rounded up; 1 is the table's smallest unit).
  Choking stays in the middle group because it also carries −2 on all checks and no speech. The price lives in
  `05-gen_data05/dsl05.py` (`COND_DOT`, EU_TABLE) and is emitted to `abilities.yaml#budget.effect_units`.
  T-05-9 has a note citing K1.
- **Re-budget (generator).** 18 abilities carry burning or bleeding. Ten (12 ranks) fell more than 2 EU under
  their allowance and were re-budgeted inside their themes:
  - *Flame Lance* r1 S3 +1, r2 S4 +2, r3 S4 +2 and exposed for a round. S5 was rejected because a base of S5
    clamps away every reach step, flare and critical.
  - *Firestorm* and *Dawnbreak* +2 harm edge, *Wall of Flame* +1, *Red Harvest* +2.
  - *Rain of Knives* one rung heavier and distracted for the scene.
  - *Through the Gap* two rungs.
  - *Apex Hunter* adds exposed for a round.
  - *Cinder Stride* r2 +2, r3 one rung heavier against a burning target.

  Five of the ten are in C2c's `ab_deep.py`. Pipeline: `gen_data05.py --emit` (ERRORS 0), then
  `integration-merge.py` (owner blocks verified). A second emit and merge reproduces the data byte for byte.
  Census: 185 ranks on their allowance, 222 one under, 242 two under, none over.
- **Acceptance (K2, P3 caster, Focus 7; win% vs one T3 / one T4 / two T3):**

  | Case | vs one T3 | vs one T4 | vs two T3 |
  |---|---|---|---|
  | Spent (free working only) | 91.0 | 33.6 | 26.4 |
  | Free working + push | 95.9 | 54.9 | 47.4 |
  | Old Flame Lance r2 (S3 + burning) | 92.1 | 44.3 | 27.3 |
  | **New Flame Lance r2 (S4 +2 + burning, 8 EU = allowance)** | **97.3** | **65.9** | **54.6** |

  Against the push the new spell is **+1.4 / +11.0 / +7.2** (the old one was −3.8 / −10.6 / −20.1). One T3 is
  saturated (both above 95%). In the two open matchups the margin is 11 and 7 points, under the bearer's best
  answer; when the bearer beats the flames out, the spell does better still (67.8, 59.9).
- **Text and examples updated:** T-05-9 rows and note; 05.11.5's worked-budget table (Flame Lance r1/r3,
  Firestorm) and census sentence (it was stale: 239 abilities / 526 ranks, now 362 / 649); 05.7.11's "Focus still
  pays" paragraph (K2 sentence); WE-05 crypt stair (now a T3 ghast, Vitality 18; S4 +2 + Hard flare = 14; the
  critical is clamped at S5, now said); the thermal-shock composite example (14); the emulation example (Limited
  S3 +2 = 7). `05-focus-sim.py` re-run for WE-05-5's Ash rows: spends freely 81.3 → 93.1%, starting at 3 40.7 →
  65.9%, Focus spent 5.64 → 4.31 ("four fifths" → "three fifths" in the text). One venture-day cell moved
  6.3 → 6.2% from the shared RNG. Chapter table and `05-focus-sim.md` updated.
- **Re-checked, unchanged:**
  - `tables05.py --check` (T-05-12/14 same).
  - `05-ladder-check.py` (byte-identical, 183 callings, 0 failures).
  - `12-world-seed.py` (byte-identical).
  - `gen_item_ability.yaml`: `08-gen_data08.py` in a scratch copy changed no data file; the pool carries ids,
    tags and mod_group only.
  - 09 and 16 read ability ids only.
  - Composites keyed on Flame Lance (gust pierce) are unaffected.
- **New row I-090** (08/09): 08's on-hit and oil properties price bleeding/burning like control conditions in
  their own scheme, and 09's estimator was not checked.
- DL-05-40.

## Close-out (done)
- DL entries: DL-00A-31, DL-00A-32 (hand-kept 00 head of `decision-log.md`), DL-05-39, DL-05-40 (fragment).
  `decision-log.md` and `traceability.md` re-assembled with `integration-assemble-appendix.py`.
- `12-compile_anchors.py`: 129 anchors, 0 errors, 0 warnings.
- Validator: 0 ERROR / 0 WARN (INFO: POOLS 2, REFS-EX 9, REFS-MD-EX 70).
- Sims: `06-conflict-sim.py` (seed 606, 20,000 a row; output committed, about 25 minutes), `05-focus-sim.py`
  (seed 505; results in `05-focus-sim.md` and ch.05's table).
- Ledger: I-033, I-043, I-044, I-058 resolved with evidence; new I-090 open. Nothing committed; ch.13 untouched.
