# 06 — Conflict simulation

Scripts: `rules/_process/simulation/06-conflict-sim.py` (seeded `random.Random(606)`; 20,000 fights or
chases per row; `python 06-conflict-sim.py [runs]`), full output `06-conflict-sim-output.txt`, and the
data generator and validator `06-gen_data06.py`. Reported in `06-conflict.md` at 06.10.6, T-06-12,
T-06-13, T-06-14 and 06.12.4.

## 1. What is modelled

Exactly chapter 06's rules: 3 PC actions and 2 adversary actions a turn; repetition snags 0 / −2 / −4;
one-handed weapons S2 at one action and heavy weapons S3 at two; the mastery rung (06.4.5); degrees by
margin with the natural-20 and natural-1 step; fixed harm 1 / 3 / 5 / 8 / 12 with a critical success
one rung heavier; armor as reduction; Fend on the first attack each round; Defend; the tempo check
against each foe's tempo DC; the morale clock with its listed tick sources; mobs with pooled Vitality
and the numbers step; windups before S4+ blows; the reckless trade; the Focus push; called shots at
gaps; chases as racing clocks with the varied ground tiers.

The PC's policy is deliberately plain: engage the weakest engaged foe, Strike with every action, no
abilities, no Setups, no terrain. Real play has more tools, so these are floors for a competent player.

## 2. What is assumed (owned by chapters not yet written)

| Assumption | Value | Owner |
|---|---|---|
| PC Vitality by band | 12 / 14 / 16 / 18 / 20 | 02, 07 |
| Worn-armor reduction | light 1, medium 2, heavy 3; PC kit 1 / 1 / 2 / 2 / 3 by band | 07, 08 |
| Adversary lines | T-06-12: attack +2/+5/+7/+10/+12; Guard 12/15/17/20/22; Vitality 5/12/18/26/40; harm S2/S2/S3/S3 (S4 heavy)/S4 (S5 heavy); reduction 0/0/1/2/2; nerve 4/6/6/8/8 | 09 |
| Staggered | Vitality 0 | 07 |
| "Dying" | a proxy: two further harmful hits while Staggered | 07 |

Section F of the output re-runs the equal-band rows with PC Vitality flat at 12.

## 3. Headline results (win% / Staggered% unless noted)

**One foe (baseline martial specialist, no Focus).** Equal band: P1 100/0 · P2 100/0.5 · P3 99.7/3 ·
P4 87/45 · P5 80/60. One band up: 98.7/9 · 44.5/86 · 62/72 · 3.7/100. Two bands up: 8 · 0 · 0.4.
Rounds: 1.5–3 against rabble, 3.2–6.4 from T3 up.

**Body count.** Two of the PC's band: 99.9 · 90/22 · 73/48 · 3 · 3. Three: 97.5 · 32 · 13 · 0 · 0.
Four T2 foes against P2 as individuals: 3%; as one mob: 43%. A T1 mob of six against P1: 95/27. A T2
mob of six against P3: 95/15. The full matrix is T-06-13 (section H of the output).

**Kit and tactics** (T-06-14). Against one strong foe, the reckless trade and the called shot at a gap
each add about ten points when the foe is armored; Defend in a duel costs a few points and pays only
against several attackers; armor is worth 7–23 points; Fend 1–17; heavy and one-handed weapons are
within six points of each other unaided.

**Focus (issue I-006).** A push on the first Strike each turn: P2 vs T3 44.5 → 72; P3 vs T4 62 → 84;
P4 vs T4 87 → 96; P3 vs two T3 73 → 90. A specialist with no Focus beats one foe of their own band
80–100% of the time; a broad-calling fighter 87% at P3 and 73% at P4. The chapter 05 case (a tier-3
caster out of Focus with a staff: +2, S2, Guard 12, Vitality 12) wins 0.4% against one T3 foe and 65%
against one T2 foe: the same picture as 05's 0.1%, and a property of that character, not of the system.

**Fearless foes.** Without a morale clock: two T3 against P3 68% (73% with); a T1 mob of six against
P1 74% (95% with).

**Vitality flat at 12.** P3 vs one T3 98/17; P4 vs one T4 68/76; P5 vs one T5 57/85.

**Chases** (escape 6 against pursuit 8). From `band.near` 70%, from close 60%, from far 79%; with a
cited lever every round 81%; slower pursuers 87%; mounted pursuers 51%; a character with no
competence 45%; about 3.4 chase rounds. With clocks of 4 and 4: 50% in 1.8 rounds; 6 and 6: 47%.

**Casters and the branch working (section J; revision I-009).** The script gained a caster mode: the
caster attacks with its branch working (05.7.11: one action, aimed against Guard, casting attribute +
competence, severity S2/S3/S4 by the casting school's grade), needs no Move to engage, and its non-physical
harm passes armor (09.3.6); Force Bolt's critical push makes the foe Move back; a Focus spell (Flame Lance
rank 2 with its burning) or the push can be spent on the first beat of a turn; `foe_fend` adds 09's
adversary Fend. Every earlier row reproduces byte for byte.
- New caster (+5, Guard 12, Vitality 12) vs one T2: Force Bolt 93.6, Rebuke 92.8, Wild Lash 92.8 (a staff:
  51.3; the martial P1 line 98.7). Weakest legal caster (+1, Guard 10, Vitality 11): 39.3–42.0.
- Spent P3 caster (+8, Guard 12, Vitality 16) vs one T3: 91.0 / 90.3 / 80.7; with T3 Fend 86.8 / 86.2 /
  74.5; at Vitality 12 (Ash's sheet) 84.6 / 83.6 / 70.6. Before I-009: 0.4.
- Spent caster vs one equal-band foe, P1–P5 (best branch): 100 / 99.0 / 91.0 / 48.4 / 30.1, against the
  no-Focus specialist's 100 / 100 / 99.7 / 87.3 / 79.6; Wild Lash (physical, armor reduces it) 100 /
  98.6 / 80.7 / 11.0 / 6.7.
- Focus at P3 (Focus 7): pushing the first bolt each turn, vs one T3 91.0→95.9, vs one T4 33.6→54.9, vs
  two T3 26.4→47.4, vs two T2 91.4→96.5 (the fighter's push: 99.7→99.9, 62.3→84.0, 73.0→89.6, 100→100);
  casting Flame Lance first each turn instead (rank 2 as it stood before I-033): 92.1 / 44.3 / 27.3 / 92.0.

**Lingering harm (sections K1, K2; revision I-033).** Foes now carry condition instances: burning and bleeding
(1 Vitality a stack at the bearer's turn end, unreduced by worn armor), stacking `intensify` (max 3, a new
stack refreshes the duration), lasting the applying effect's duration (one round, or the scene), and ended by
one of the bearer's two actions (burning: no check; bleeding: Handle against DC 10). The bearer's policy is a
parameter (`never` / `always` / `smart`); every row of K is played under all three and keeps the least, the
bearer's best answer. Before I-033 burning never ended and no bearer action existed; only J4's Flame Lance rows
moved (now `never`; two cells by 0.2–0.5 because a foe dropped or bloodied by burning now ticks morale).
- K1: a 1-Focus spell at the working's severity, plus one rung (= the push) or plus a condition, P1/P3/P5
  against one foe a band up and two foes at band (P1: one T3, two T2). Pooled rung gain 98.3 points. One stack
  of burning or bleeding for the scene: 0.67 EU; for one round: 0.40 EU; two stacks: 1.14 EU. The bearer's best
  answer is almost always `never`: an action spent beating out 1 Vitality a turn costs it half an attack.
- K2 (acceptance): P3 caster, Focus 7, against 1xT3 / 1xT4 / 2xT3. Spent 91.0 / 33.6 / 26.4; push 95.9 / 54.9 /
  47.4; old Flame Lance r2 (S3 + burning) 92.1 / 44.3 / 27.3; new Flame Lance r2 (S4 +2 + burning, priced 8 =
  its allowance) 97.3 / 65.9 / 54.6, i.e. +1.4 / +11.0 / +7.2 over the push where the old one was −3.8 /
  −10.6 / −20.1.

## 4. What the numbers were used to decide
- **Lingering harm** (DL-05-40; revision I-033): T-05-9 prices burning and bleeding at 1 EU a stack whatever
  the duration (K1: 0.67 / 0.40), out of the middle group's 2–3; the ten abilities that fell below their
  allowance were re-budgeted, Flame Lance r2 to S4 +2, which K2 shows beats the push by 11.0 and 7.2 points
  in the two matchups not already above 95%.

- **3 actions against 2** (DL-06-01): gives a lone PC the edge against one foe and makes the second
  foe the real threat, which is the solo curve the encounter advice needs.
- **Mastery** (DL-06-09): the first pass, with every weapon at S2 for life, gave a tier-4 fighter 2.8%
  against one T4 foe without Focus. One rung at expert and two at master restore a baseline that needs
  no Focus.
- **Adversary lines** (DL-06-25): T1 and T2 were moved to the top of 00.3.7's ranges after the first
  pass showed a lone T2 falling to a novice in two rounds with no harm done.
- **Morale sizes 4 / 6 / 8** (DL-06-18): most group fights end by a break after roughly half the foes
  are down.
- **Chase clocks 6 and 8** (DL-06-21): chosen over 4/4 and 6/6 so that flight succeeds more often than
  not and lasts three or four beats.
- **The advisory matrix** (T-06-13): chapter 09's `threat_advisory` should be this table re-run on
  its final templates, not a formula.
- **Branch workings** (DL-05-31; revision I-009): severity by grade (S2/S3/S4) meets both acceptance
  lines (a new caster ≥ 75% against one T2; a Spent tier-3 caster ≥ 40% against one T3) while staying
  under the specialist at every band; one rung lighter (section J5) passes for Force Bolt (66.0) and Rebuke
  (60.6) but fails for Wild Lash (27.9), so one shared rule needs the mastery steps.

## 5. Limits

The policy never retreats, never uses a Setup, a feature, an ability, a companion or a mixed weapon
loadout, and adversaries never flank or use ranged attacks. Each of those favors the PC except
flanking. The Dying proxy overstates deaths: under chapter 07 a Staggered PC has Yield, Retreat and a
last-chance menu.
