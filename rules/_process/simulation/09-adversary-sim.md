# 09 — Adversary simulations

Scripts (all seeded, deterministic; Python 3 + PyYAML), in `rules/_process/simulation/`:
- `09_core.py` — shared arithmetic: band tables (T-09-2/3), exact d20 enumeration, **the advisory estimator**
  (`estimate`, PR-09-4), and an extended fight model that imports chapter 06's `06-conflict-sim.py` unchanged and
  adds adversary Fend at T3+ (06.6.5), resistance (×½ floored per outcome), regeneration, fearless members and
  swarm harm.
- `09_data_powers.py`, `09_data_arch.py`, `09_data_arch2.py`, `09_data_beh.py`, `09_data_enc.py`, `09_data_adv.py` —
  the authored content (powers and degree tables; 63 archetypes; 40 behavior lists and vocabularies; encounter
  tables; the 123-entry roster).
- `09-gen_data09.py` → `09-gen_data09-output.txt` — compiles and validates `data/archetypes.yaml`,
  `data/adversaries.yaml`, `data/behaviors.yaml` (every tag, effect, condition, ability, affliction, base item,
  flaw and absorbable id checked against the canonical files); runs PR-09-1 for every entry (Vitality solve,
  severity compensation, variants); runs chapter 08's loot pool check (contract_09) with 08's own code.
- `09-adversary-sim.py` → `09-adversary-sim-output.txt` — sections A–F below (3,000 fights per row).
- `09-estimator-tune.py` → `09-estimator-tune-output.txt` — one simulation pass over 512 encounters, then a grid
  over the estimator's two constants.
- `09-i005-check.py` → `09-i005-check-output.txt` — chapter 04's R1 pacing re-run under 09's encounter budget.

## Assumptions

| Assumption | Value | Owner |
|---|---|---|
| PC reference lines | T-06-12 (attack +5/+7/+9/+11/+12; Guard 14/16/18/19/20; Vitality 12/14/16/18/20; armor 1/1/2/2/3; Strike S2/S2/S3/S3/S4) | 06 (DL-00-04 Vitality by band) |
| Economy | PC 3 actions + Fend; adversary 2 actions; repetition 0/−2/−4 | 06 |
| Adversary Fend | T3+ standard; elite as one band higher; solo always | 06.6.5, 09.3.9 |
| Morale | 06's tick sources; nerve 4/6/8/fearless | 06 |
| Dying ladder (section E) | 07's `fight07` (wound load 3, Dying 3 steps, checks) | 07 |
| No Focus, no abilities, no terrain, no levers | the advisory is a floor | 09.6.7 |

## Results

**A. The standard line.** With adversary Fend, T4/T5 Vitality 24/36 keep one equal-band foe beaten ≥ 80% without
Focus: P1–P5 100 / 99.9 / 99.4 / 87.8 / 80.2 % (Staggered 0.1 / 0.7 / 4.7 / 42.8 / 58.2 %). With T-06-12's 26/40
and Fend: P4 81.6/53.5 (hard), P5 73.6/65.4.

**B. The advisory matrix** re-run with the final templates: 06's script as written (no adversary Fend) reproduces
T-06-13; the extended model (09's contract matrix, T-09-9) differs from T-06-13 in five cells, all harsher.

**C. Variants.** Elite ×2 (T1–T3) / ×1.25 (T4–T5); solo ×4 / ×3 / ×3 / ×1.75 / ×1.5. Against P(b), no Focus:
elite trivial / fair 97-15 / fair 90-36 / hard 74-63 / hard 63-75; solo easy 99-9 / fair 86-46 / hard 68-68 /
hard 43-86 / hard 46-86. With a Focus push each turn, solos are won 100 / 93 / 83 / 70 / 66 %.

**D. The estimator against the Monte Carlo** (586 encounters: every T-06-13 shape, every bestiary adversary at three
PC bands, every resistant adversary without its counter, 38 mixed encounters, five band-1 PC builds): **90.4%
exact, 100% within one word**; misses 26 gentler, 30 harsher. Mixed groups 78.9% exact.

**E. Chapter 07's menu rates by the estimator's word** (481 encounters, lethal context, fought to the end): trivial
0.0, easy 0.4, fair 2.3, hard 18.4, lethal 77.7 per 100, against 07's targets 0 / 1 / 5 / 26 / 80. Every word at or
below target.

**F. Solo encounter budget** (T-09-10): two equal-band foes are hard or lethal from P2 up; three are lethal; T4/T5
pairs are lethal; mobs make crowds fightable (P2 vs a T1 mob of 12: fair).

**Estimator tuning.** Grid over the landed-blow margin (1.0–2.0) and a Staggered margin (0–1.5): chosen 1.75 and
0.5 (466/512 exact on the tuning pass; gentler 21 ≤ harsher 25).

**I-005.** 04's archer under 09's budget with challenge = foe band: tiers at median sessions 7 / 20 / 31 / 46 / never
(T5 in 21 of 100 runs); with the proposed advisory-offset challenge band: 5 / 11 / 22 / 39 / 60 (T5 in 59 of 100);
04's own assumption: 4 / 9 / 19 / 34 / 56 (82 of 100).

## What the numbers decided

- T4/T5 standard Vitality 24/36 (DL-09-04).
- The variant multipliers (DL-09-08).
- The estimator's constants (DL-09-09).
- Eleven severity compensations in the bestiary (DL-09-20).
- The I-005 proposal to 03 (DL-09-22).

## Limits

The fight model has no powers beyond Fend, resistance and regeneration: riders, shaped powers, auras and
summonings enter only through the power premium (OEQ-09-3). The PC policy is three Strikes at the weakest engaged
foe; real play has more tools, so every number is a floor for a competent player.
