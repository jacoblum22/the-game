# 07 — Harm ladder simulation

Scripts: `rules/_process/simulation/07-harm-sim.py` (seeded `random.Random(707)`; 20,000 fights a row;
`python 07-harm-sim.py [runs]`), full output `07-harm-sim-output.txt`, and the data generator and
validator `07-gen_data07.py` (with `07-gen_harm07.py`). Reported in `07-harm-recovery-death.md` at T-07-18,
07.2.6, 07.2.7, 07.2.8, 07.5.10 and 07.8.7.

## 1. What is modelled

Chapter 06's fight model is imported unchanged from `06-conflict-sim.py` (3 PC actions against 2,
repetition snags, Fend, mastery, fixed harm with a critical one rung heavier, armor as reduction, the
morale clock, mobs, windups, T-06-12's reference lines). Its "Dying proxy" (two further hits while
Staggered) is replaced by chapter 07's ladder:

- Vitality above 0: harm lowers it; the blow that reaches 0 only Staggers (the excess is discarded).
- Staggered: each harm event adds U(bucket) to the wound load (1 / 1 / 2 / 3 / 4 for a final amount of
  1–2 / 3–4 / 5–7 / 8–11 / 12+) and leaves a wound; an arm wound (one in four) penalizes the PC's Strikes
  (S2 −1; S3 and heavier −2; the worst only).
- Load 3: a lethal event → Dying at `min(3, 1 + brink)`; a non-lethal event → Down.
- Dying: prone, one action a turn (a last Strike), attackers hold a lever; each lethal hit +1 step (+2
  for a Grievous or Catastrophic wound); the dying check at the PC's turn end against 10 / 15 / 20 with
  Endurance + the floor (+2 by default): critical success stabilized, success one step down, a failure
  by 3 or less holds, failure +1, critical failure +2.
- Past step 3: the Threshold (the menu is counted, not played).
- Foes that `kill` keep attacking a Dying PC; any other disposition stops when the PC is Dying or Down.
- PC Vitality by band per DL-00-04: 12 / 14 / 16 / 18 / 20. Armor 1 / 1 / 2 / 2 / 3 as in 06.

Policies: **fight on** (never backs down: the floor for a stubborn player) and **exit at Staggered**
(against foes that kill: Retreat as a chase won 60% of the time, 06.12.4's figure from `band.close`,
else cornered and fighting on; against foes that capture or rob: Yield, accepted).

## 2. Targets, set before tuning

| # | Target | Why |
|---|---|---|
| 1 | From any Vitality above 0, one harm event ends at Staggered | BRIEF §4: never one roll |
| 2 | A same-band foe needs 3–7 telling blows to Stagger a PC; never fewer than 2 harm events to Dying | fights of 4–7 rounds (OEQ-00-2) with a visible slide |
| 3 | *Fair* fights against killers, fighting to the end: the menu in at most 6 of 100; with an exit at Staggered at most 3 | a fair fight should almost never cost something permanent |
| 4 | *Hard* fights: at most 30 of 100 fighting on; at most 12 with an exit | hard should be dangerous to the stubborn and survivable to the prudent |
| 5 | *Lethal* fights reach Dying in most cases when fought to the end | the warning must be honest (R4 §6: follow-through) |
| 6 | A first fall left alone stabilizes at least 80% of the time; a third at most 15% | wounded memory must bite |
| 7 | Dying to full: a median of at most 2 days in a haven with a healer, at most 4 on the road alone | loss measured in days, not sessions |
| 8 | A non-lethal (Risky) fight never reaches Dying | INV-6 |

## 3. Results (20,000 runs a row)

**A. Hits of one severity from full Vitality, to Staggered and then to Dying** (exact).

| PC | S2 | S3 | S4 | S5 |
|---|---|---|---|---|
| P1, Vitality 12, unarmored | 4 + 3 | 3 + 2 | 2 + 1 | 1 + 1 |
| P1, light armor (1) | 6 + 3 | 3 + 3 | 2 + 2 | 2 + 1 |
| P3, Vitality 16, unarmored | 6 + 3 | 4 + 2 | 2 + 1 | 2 + 1 |
| P3, medium armor (2) | 16 + 3 | 6 + 3 | 3 + 2 | 2 + 1 |
| P5, Vitality 20, heavy armor (3) | never (0 harm) | 10 + 3 | 4 + 2 | 3 + 1 |

A Light blow (S1) is 12 + 3 against an unarmored P1 and does nothing through any armor.

**B. The dying ladder left alone** (no further harm, no help).

| Endure modifier | from Dying 1 | from Dying 2 | from Dying 3 |
|---|---|---|---|
| +0 | 74% stabilize, 1.9 rounds | 30%, 2.1 | 6%, 1.2 |
| +2 | **85%**, 1.7 | **44%**, 2.4 | **11%**, 1.5 |
| +4 | 93%, 1.4 | 63%, 2.6 | 21%, 1.8 |
| +6 | 96%, 1.2 | 76%, 2.4 | 33%, 2.0 |

With first aid from another each round (Handle +3 against the same DC): 98% / 79% / 35% at +2.

**C–D. Lethal context, per 100 fights, by chapter 09's advisory (rows pooled).**

| Advisory | Staggered | Dying | Menu, fighting on | Dying, with an exit | Menu, with an exit | Escaped | Menu, yielding to captors |
|---|---|---|---|---|---|---|---|
| trivial | 1.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7 | 0.0 |
| easy | 6.5 | 0.9 | 0.7 | 0.4 | 0.3 | 3.9 | 0.0 |
| fair | 31.3 | 7.1 | **5.0** | 3.3 | **2.3** | 18.4 | 0.1 |
| hard | 67.0 | 32.1 | **25.6** | 13.2 | **10.5** | 39.7 | 0.1 |
| lethal | 95.7 | 83.5 | **80.0** | 35.9 | **34.3** | 55.1 | 0.6 |

Rows: trivial — P1 v 1 T1, P2 v 1 T2, P3 v 1 T3; easy — P1 v 3 T1, P1 v 1 T2, P3 v 4 T2; fair — P1 v 4 T1,
P2 v 2 T2, P4 v 1 T4, P1 v a T1 mob of 6; hard — P1 v 2 T2, P2 v 1 T3, P3 v 2 T3, P3 v 1 T4, P5 v 1 T5;
lethal — P1 v 1 T3, P2 v 3 T2, P3 v 3 T3, P4 v 2 T4, P4 v 1 T5. Per-row figures are in the output file
(the fair rows range from 1.9 to 7.8 menus in 100; the hard rows from 14.5 to 35.7).

**E. Risky against Dire, the same foes.**

| Advisory | Risky (no lethal context): Staggered / Down / Dying | Dire, foes that capture: Dying / menu | Dire, foes that kill: Dying / menu |
|---|---|---|---|
| trivial | 1.2 / 0.0 / **0** | 0.0 / 0.0 | 0.0 / 0.0 |
| easy | 6.5 / 0.9 / **0** | 0.9 / 0.1 | 0.9 / 0.7 |
| fair | 31.4 / 7.1 / **0** | 7.1 / 1.0 | 7.1 / 5.0 |
| hard | 67.0 / 32.2 / **0** | 32.2 / 4.9 | 32.1 / 25.6 |
| lethal | 95.7 / 83.7 / **0** | 83.9 / 12.6 | 83.5 / 80.0 |

A Risky fight never reaches Dying, by rule; what would have been Dying is Down. Against foes that stop
when the PC falls, a Dying PC reaches the menu only when its own checks fail (about 15% of falls).

**F. Wounded memory** (P3 against two T3, foes that kill): entered with brink 0 / 1 / 2, the fight
reaches Dying 19.5 / 19.3 / 19.5 times in 100, and of those 74% / 90% / 98% go on to the menu.

**G. Recovery** (11,943 survivors of Dying pooled from section C). A survivor carries 2.9 wounds on
average (29% Light, 48% Moderate, 18% Heavy, 5% Grievous, none Catastrophic); the worst wound is Light 18%,
Moderate 35%, Heavy 34%, Grievous 13%. Each also carries its brink wound.

| Regime | Median days to full | 75th | 90th | Cannot fully heal without care |
|---|---|---|---|---|
| on the road, untreated | 4 | 4 | 8 | 13% |
| on the road, treated daily | 2 | 4 | 6 | 0 |
| in a haven, bed rest and treated | 2 | 3 | 3 | 0 |

By wound: Moderate 1 day; Heavy and brink 4 / 2 / 2 days; Grievous never / 6 / 3; Catastrophic never /
13 / 7 (including the day of surgery).

**I. The Gamble** (Endure against 15): at +2, 5% stand free, 35% live, 15% choose a price, 45% death;
at +0, 55% death; at +4, 35%; at +6, 25%.

## 4. What the numbers were used to decide

- **Wound load limit 3, not 2** (DL-07-04). At 2 (`LOAD_LIMIT=2 python 07-harm-sim.py 4000`): fair — Dying
  12.5, menu 9.1 (4.7 with an exit); hard — 43.9 and 35.9 (16.9). At 3: 7.1 and 5.0 (2.3); 32.1 and 25.6
  (10.5). Targets 3 and 4 are met only at 3.
- **Stabilize DCs 10 / 15 / 20** (DL-07-04): target 6 (85% / 44% / 11%). A flat DC 15 at every step
  gives 66% / 41% / 23% (exact chain, Endure +2): a first fall too likely to reach the menu and a third
  too likely to walk away, so wounded memory would matter less than it should.
- **Brink as a Heavy wound with its own 4-segment clock** (DL-07-04): with brink cleared by one night's
  rest, the median recovery was 1 day in every regime (60% of survivors carry nothing worse than a
  Moderate wound); as a clocked wound it is 2 / 2 / 4, which meets target 7 and makes a fall cost days.
- **The Gamble at Moderate** (DL-07-05): a 40% clean survival for a novice is tempting; 45% death is real.
- **Section E** is the arithmetic behind "death requires two keys and loss does not": the Staggered and
  fallen rates are identical with and without a lethal context; only the word *Dying* changes.

## 5. Limits

The PC policy is 06's plain one (three Strikes a turn, no Focus, no abilities, no Setups, no ground, no
companion), so every rate here is a floor for a competent player. Foes never flank or shoot. The exit
policy treats the chase as one 60% draw and ignores shots at the fleer. The menu's choices are not
played out. Wound sites are drawn one in four to the weapon arm; other sites' penalties (legs for Move,
head for tempo) are not modelled. Chapter 09's final templates should be run through this script as
well as 06's (OEQ-07-1).
