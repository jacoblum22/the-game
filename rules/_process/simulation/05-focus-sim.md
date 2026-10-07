# 05 — Focus economy simulation and data-generation checks

Scripts: `rules/_process/simulation/05-focus-sim.py` (seeded, `random.Random(505)`, 20,000 runs per
case) and `rules/_process/simulation/05-gen_data05/gen_data05.py` (generator and validator for
`data/abilities.yaml`, `licenses.yaml`, `rituals.yaml`, `composites.yaml` and the two contrib fragments).
Reported in `05-abilities-focus-magic.md` at WE-05-5, 05.11.5 and T-05-12.

## 1. What the Focus simulation models

Chapters 06, 07 and 09 were not yet written, so the fight model is 00.3.7's coherence model, stated here
so the numbers can be re-run when those chapters land:

- one PC beat per round and one foe attack per round;
- fixed harm by severity (1 / 3 / 5 / 8 / 12, 00.3.11); degrees by 00.3.10 (critical at margin ≥ 10; a
  natural 20 steps up, a natural 1 steps down); a critical success is one severity rung heavier;
- a PC at Vitality 0 has lost the fight for this measure (Staggered);
- **Wren**, tier-1 Archer: attack +6, Guard 14, Vitality 12, Focus 5. Aimed Shot (rider, 1 Focus):
  Precision lever (+2) and one severity rung. Quarry's Mark (trigger, 1 Focus, once per scene): the
  target is exposed, modelled as a second Precision lever (+2) on her later attacks (ch.06 owns the
  condition's exact effect). Foe: T2, Vitality 10, Guard 13, attack +4, S2 harm;
- **Ash**, tier-3 Pyromancer: casting +8, Guard 12, Vitality 12, Focus 7. Flame Lance rank 2 (1 Focus):
  S4 fire +2 and one stack of burning (1 harm per stack at each of the foe's turn ends, at most 3; re-priced
  and re-run in revision I-033, which also moved one venture-day cell, 6.3% to 6.2%). Spell
  Ward rank 2 (reaction, 1 Focus): a hit two severity rungs lighter; used while he would keep 1 Focus
  for the next lance. The arcane family trigger: +1 Focus on a critical success, once per scene.
  Without Focus he fights with a staff: +2, S2. Foe: T3, Vitality 16, Guard 16, attack +7, S3 harm.

## 2. Results

### One fight

| Case | Wins | Rounds | Focus spent | Focus left | Ends at 0 Focus | Vitality left (wins) |
|---|---|---|---|---|---|---|
| Wren (tier 1, Focus 5) vs T2, spends none | 87.0% | 4.44 | 0.00 | 5.00 | 0.0% | 6.7 |
| Wren (tier 1, Focus 5) vs T2, spends freely | 99.6% | 2.36 | 3.34 | 1.66 | 6.2% | 9.7 |
| Wren (tier 1, Focus 2 at start) vs T2 | 96.9% | 3.04 | 2.00 | 0.00 | 100.0% | 8.6 |
| Ash (tier 3, Focus 7) vs T3, spends none | 0.1% | 3.00 | 0.00 | 7.00 | 0.0% | 3.4 |
| Ash (tier 3, Focus 7) vs T3, spends freely | 93.1% | 2.87 | 4.31 | 3.09 | 13.7% | 9.4 |
| Ash (tier 3, Focus 3 at start) vs T3 | 65.9% | 2.79 | 2.97 | 0.32 | 71.2% | 8.7 |

### Rests (05.6.9)

| focus.max | breather | short rest (full / partial) | long rest (full / partial) |
|---|---|---|---|
| 4 | +1 | +2 / +1 | to 4 / to 3 |
| 5 | +1 | +3 / +2 | to 5 / to 4 |
| 7 | +1 | +4 / +2 | to 7 / to 6 |
| 9 | +1 | +5 / +3 | to 9 / to 7 |
| 12 | +1 | +6 / +3 | to 12 / to 9 |

### A venture day (Wren, five fights against T2; Vitality restored between fights to isolate Focus)

A breather after every fight (only two between short rests restore Focus); a short rest after fights 2
and 4.

| | Fight 1 | Fight 2 | Fight 3 | Fight 4 | Fight 5 |
|---|---|---|---|---|---|
| Focus at start (mean) | 5.00 | 2.66 | 3.00 | 1.00 | 3.00 |
| starts at 0 Focus | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| starts at 1 Focus | 0.0% | 6.2% | 0.0% | 100.0% | 0.0% |
| Focus spent (mean) | 3.34 | 2.66 | 3.00 | 1.00 | 3.00 |

Mean Focus spent over the day: 13.00 (pool 5; rests restored 8).

Breathers only, no short rest:

| | Fight 1 | Fight 2 | Fight 3 | Fight 4 | Fight 5 |
|---|---|---|---|---|---|
| Focus at start (mean) | 5.00 | 2.66 | 1.00 | 0.00 | 0.00 |
| starts at 0 Focus | 0.0% | 0.0% | 0.0% | 100.0% | 100.0% |

## 3. What the numbers were used to decide

- **A fight at one band costs about two thirds of a tier-1 pool and four fifths of a tier-3 caster's.**
  The pool growth of 05.6.1 (+1 per tier) keeps that fraction roughly constant as costs rise with
  ranks; a per-tier discount was rejected (DL-05-09).
- **A breather is worth exactly one activation; a short rest is worth half the pool.** With two short
  rests a day a character sustains five fights and never starts empty; with breathers only they are
  empty from the fourth fight. This is the designed price of Focus: an hour of exposure to ch.10's
  checks and ch.11's clocks (DL-05-14).
- **A caster without Focus is nearly helpless against an equal foe (0.1%)**, and at 3 of 7 Focus wins
  41%. This is the case for overdraw (05.6.6), for the push being available to everyone (05.6.7), and
  for the codex showing the pool at all times.
- **Spending freely leaves a tier-1 character Spent in 6% of fights and a tier-3 caster in 31%.** Spent
  therefore has to be a real but survivable state: sustained workings end and concentration is snagged,
  nothing else (05.6.5).

## 4. Open after ch.06, 07 and 09 are written

Re-run with the real action economy (riders and reactions per round), real foe blocks, and the real
effect of `cond.exposed` and `cond.burning`. The tests named in the chapter are T-05-BUDGET, T-05-DAY,
T-05-MISCAST and T-05-HEAL (Open empirical questions).

## 5. Data generation: checks the generator enforces

Run `python gen_data05.py --cov --emit` in `05-gen_data05/`. It aborts on any failure. Last run:

- 251 abilities = 176 tag-gated + 48 oath-gated + 27 mirrored absorbed powers; 499 authored ranks;
  83 licenses (81 training + 2 Focus); 24 rites; 22 composites; 6 effect definitions; 9 handlers.
- Ids unique and prefixed; every tag exists in `data/tags.yaml`; every ability's first tag is a deed tag
  at level 2 or 3; every effect id exists in `effects.yaml` or the 05 owner-block; hooks, behavioral
  slots, conditions, bands, flags and duration forms are in `substrate.yaml`; core-effect parameter
  ranges respected; form → regime and timing; passives carry no cost, no limits, no prevent, no hard
  control, no S3+ harm; Focus cost inside the band for the `min_tier`; rank counts inside the rank rule.
- Text lint on principles, limitations and rank texts: T-00-22 banned words and SG-15 soft phrasing
  ("no protection", "offers no", "does not protect", "can lull").
- Power budget, every rank: `allowance − 2 ≤ value ≤ allowance`. Slack over 499 ranks: 173 on
  allowance, 173 one under, 153 two under, 0 over.
- Coverage (ch.04's requests): 81 of 81 level-2 deed tags with at least 2 abilities and one at
  `min_tier` 1; every branch ≥ 14 with ≥ 2 at each `min_tier` 1–5; every conduct axis with positive-pole
  abilities at `min_tier` 1, 3 and 5.

| Branch | Total | min_tier 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| deed.martial | 26 | 12 | 6 | 4 | 2 | 2 |
| deed.guile | 17 | 8 | 3 | 2 | 2 | 2 |
| deed.wilds | 14 | 6 | 2 | 2 | 2 | 2 |
| deed.lore | 18 | 9 | 3 | 2 | 2 | 2 |
| deed.arcane | 26 | 11 | 5 | 4 | 3 | 3 |
| deed.divine | 17 | 8 | 2 | 3 | 2 | 2 |
| deed.primal | 17 | 7 | 3 | 3 | 2 | 2 |
| deed.influence | 18 | 9 | 3 | 2 | 2 | 2 |
| deed.craft | 23 | 11 | 4 | 3 | 3 | 2 |
