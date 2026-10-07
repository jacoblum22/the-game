# Simulation — 03 evidence capture, saturation and recency

Owner: chapter 03 (Tags and Evidence). Purpose: show that tally growth, saturation (anti-grind) and recency
behave as the rules intend, and give chapter 04 numbers to set thresholds against.

**Scripts.** `rules/_process/simulation/03-evidence03.py` (the engine and the play model; run it for the
scenario tables) and `rules/_process/simulation/03-reach03.py` (the sessions-to-threshold table). They are
copies of the scratchpad scripts `evidence03.py` and `reach03.py` in
`C:/Users/jacob/AppData/Local/Temp/claude/C--Users-jacob-the-game/8fb5973b-1540-44c9-830b-abd8a1aa0620/scratchpad/`.
Deterministic (seeded). Python 3, standard library only.

**What the engine implements** (the rules of `03-tags-and-evidence.md`, exactly):
- quality from base odds with circumstance excluded: routine ≥ 70%, difficult 40–65%, challenging ≤ 35% (03.4.1);
- points: quality 2/4/6; stakes 0/2/4; lethal +2; critical success +2; novelty +2; failure halved (rounded
  down); a Safe failure is not evidence; secondary tags at half (03.4.2);
- settlement per scene, at every node of the tag tree, diminishing 1, ½, ¼, 0 (03.5.2);
- the routine cap: one routine contribution per node per day (03.5.3);
- the same-target cap per (target, level-2 node) per day (03.5.4);
- recent = the newest 12 evidence-bearing scenes + half of scenes 13–24 (03.6.2);
- conduct: ±2 / ±4, diminishing per axis per sign per scene; strain += negative, −= floor(positive ÷ 2) (03.8);
- degrees by the reference ladder and 01.8 (margin bands of 10; natural 20 / 1 one-step shift); success at
  cost is taken on 60% of near misses and counted as a success.

**The play model** (an assumption, not a rule): 5 scenes per session. 45% are conflicts (3–6 PC beats;
opposition tier from the PC's band to band + 2; 25% Dire, of which 40% lethal; 35% open with a shot from
hiding, which by 03.1.7 rule 2 is an archery primary with a `guile.ambush.sniping` secondary). 25% are stealth
or site scenes (2–4 beats), 15% social (1 beat), 15% travel (1 beat). The PC is Wren (Agility +3; archery
competence +2, rising to +3 at session 6 and +4 at session 12 to stand in for 04's tiers). The band of
opposition rises at sessions 6 and 13.

**Scenarios.** A: a focused archer who scouts by stealth. B: a rat grinder. C: a weapon switcher (C2: the same
fights with one weapon). D: a pivot to fire sorcery at session 11. E: a lenient DM without grounding (E2: with
grounding). F: a generalist. G: a deliberate archery and fire hybrid.

**Headline results** (200 seeds unless noted; p10 / median / p90):

| Measure | Result |
|---|---|
| A `martial.archery` weighted at sessions 1 / 3 / 5 / 10 / 20 | 8/26/43 · 48/75/104 · 91/127/161 · 213/260/314 · 406/493/554 |
| A `martial` at 5 / 20 | 116/152/188 · 528/608/681 |
| A `guile` at 5 / 20 | 32/49/69 · 167/209/250 |
| A `deed` (root) at 20 | 850/900/954 |
| A recent `martial.archery` (median) at sessions 1, 2, 3, 5, 10, 15, 20 | 26, 50, 69, 88, 95, 80, 78 |
| A per-session yield at the focus node (median of the 20-session mean) | 24.3 |
| A quality mix at the focus node (median counts over 20 sessions) | routine 13, difficult 55, challenging 98 |
| A balance of other branches against `martial` at session 20 | guile 0.34, wilds 0.23, influence 0.12 |
| A mercy net at session 20 (median) | +12 |
| B rat grinder, archery at session 20 | 2,196 with no anti-grind · 910 with diminishing returns only · 340 under the full rules; 100% routine |
| Play like A but with a fight in every scene, archery at session 20 | 1,033 |
| A archery at session 20 with no anti-grind / under the full rules (50 seeds) | 958 / 486 |
| C vs C2, `martial` at session 20 | 1,106 vs 1,191 |
| D pivot: the session at which recent(fire) > recent(archery) | 12 / 12 / 13 |
| E vs E2: spurious `tactics` at session 20; mercy positive | 236 vs 74 (archery ≈481); 46 vs 22 (honest 18) |
| G hybrid: the session at which min(archery, fire) reaches 60 / 120 | 2/3/5 · 5/6/8 |
| Largest single event (possible: 16) | 16 |
| Largest single-scene contribution at the focus node | median 19, maximum 27 (cap 28) |

**Reading.**
1. Growth is steady: about 24 points per session at a focus level-2 node. Thresholds near 80, 200 and 450
   therefore fall at about sessions 4, 8 and 19.
2. Saturation works. Diminishing returns halve honest play's raw total and, with the routine cap, cut the
   grinder's by 85%. The grinder's evidence is entirely routine, which a quality floor excludes.
3. Weapon switching gains nothing at the branch.
4. Recency follows a change of style within two sessions and forgets the old style in five, while the
   cumulative weight is kept.
5. A lenient DM with no grounding rule would have built a false second identity half the size of the real
   one. Grounding cuts that to 15%, and cuts the conduct inflation from 2.6× to 1.2×.

**Limits.** The play model is invented; real event rates need T-03-YIELD (OEQ-03-3). Counted evidence (03.7)
is not simulated (OEQ-03-4).

## Raw output

```

=== Scenario A focused archer-stealth (seed 7) ===
sess |    martial.archery w/rec |            martial w/rec |              guile w/rec |      guile.stealth w/rec |               deed w/rec
   1 |           27/27    |           29/29    |            8/8     |            8/8     |           48/48    | mercy {'pos': 4, 'neg': 0, 'strain': 0}
   2 |           43/43    |           46/46    |           15/15    |           15/15    |           87/87    | mercy {'pos': 4, 'neg': 0, 'strain': 0}
   3 |           92/82    |          103/92    |           21/21    |           15/15    |          150/135   | mercy {'pos': 6, 'neg': 0, 'strain': 0}
   4 |          131/109   |          152/129   |           30/22    |           21/13    |          205/166   | mercy {'pos': 8, 'neg': 0, 'strain': 0}
   5 |          155/108   |          178/129   |           48/38    |           39/31    |          252/183   | mercy {'pos': 8, 'neg': 0, 'strain': 0}
   6 |          158/79    |          187/98    |           48/30    |           39/24    |          281/156   | mercy {'pos': 10, 'neg': 0, 'strain': 0}
   8 |          215/85    |          259/108   |           58/23    |           45/18    |          368/150   | mercy {'pos': 12, 'neg': 0, 'strain': 0}
  10 |          275/92    |          324/106   |           88/35    |           70/28    |          478/171   | mercy {'pos': 12, 'neg': 4, 'strain': 4}
  12 |          320/90    |          369/96    |          101/35    |           81/29    |          562/165   | mercy {'pos': 14, 'neg': 4, 'strain': 3}
  15 |          409/99    |          473/114   |          134/36    |          102/26    |          692/156   | mercy {'pos': 16, 'neg': 4, 'strain': 2}
  20 |          536/79    |          638/100   |          178/34    |          136/28    |          911/148   | mercy {'pos': 20, 'neg': 4, 'strain': 0}
   max single-event points: 14

=== Scenario B rat grinder ===
sess |    martial.archery w/rec |            martial w/rec |               deed w/rec
   1 |           20/20    |           20/20    |           20/20    | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   2 |           38/38    |           38/38    |           38/38    | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   3 |           52/52    |           52/52    |           52/52    | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   4 |           70/70    |           70/70    |           70/70    | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   5 |           88/78    |           88/78    |           88/78    | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   6 |          106/87    |          106/87    |          106/87    | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   8 |          140/105   |          140/105   |          140/105   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
  10 |          176/104   |          176/104   |          176/104   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
  12 |          210/105   |          210/105   |          210/105   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
  15 |          260/102   |          260/102   |          260/102   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
  20 |          344/100   |          344/100   |          344/100   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   max single-event points: 8

=== Scenario C weapon switcher ===
sess |            martial w/rec |    martial.archery w/rec |               deed w/rec
   1 |           52/52    |           22/22    |           52/52    | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   2 |          104/104   |           43/43    |          104/104   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   3 |          156/140   |           70/63    |          156/140   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   4 |          207/165   |          100/83    |          207/165   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   5 |          261/187   |          124/93    |          261/187   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   6 |          326/202   |          152/95    |          326/202   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   8 |          449/216   |          210/102   |          449/216   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
  10 |          587/237   |          258/95    |          587/237   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
  12 |          702/220   |          308/91    |          702/220   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
  15 |          833/171   |          380/87    |          833/171   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
  20 |         1066/167   |          496/86    |         1066/167   | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   max single-event points: 10

=== Scenario D pivot to fire sorcery at session 11 ===
sess |    martial.archery w/rec |        arcane.fire w/rec |            martial w/rec |             arcane w/rec
   1 |           27/27    |            0/0     |           29/29    |            0/0     | mercy {'pos': 4, 'neg': 0, 'strain': 0}
   2 |           43/43    |            0/0     |           46/46    |            0/0     | mercy {'pos': 4, 'neg': 0, 'strain': 0}
   3 |           92/82    |            0/0     |          103/92    |            0/0     | mercy {'pos': 6, 'neg': 0, 'strain': 0}
   4 |          131/109   |            0/0     |          152/129   |            0/0     | mercy {'pos': 8, 'neg': 0, 'strain': 0}
   5 |          155/108   |            0/0     |          178/129   |            0/0     | mercy {'pos': 8, 'neg': 0, 'strain': 0}
   6 |          158/79    |            0/0     |          187/98    |            0/0     | mercy {'pos': 10, 'neg': 0, 'strain': 0}
   8 |          205/75    |            0/0     |          248/97    |            0/0     | mercy {'pos': 14, 'neg': 0, 'strain': 0}
  10 |          263/85    |            0/0     |          311/99    |            0/0     | mercy {'pos': 14, 'neg': 0, 'strain': 0}
  12 |          263/39    |           43/43    |          345/78    |           43/43    | mercy {'pos': 18, 'neg': 0, 'strain': 0}
  15 |          263/0     |           96/70    |          384/52    |           96/70    | mercy {'pos': 26, 'neg': 0, 'strain': 0}
  20 |          263/0     |          246/117   |          481/72    |          246/117   | mercy {'pos': 30, 'neg': 0, 'strain': 0}
   max single-event points: 12

=== Scenario E lenient DM (secondary tactics on every beat, extra mercy) ===
sess |    martial.archery w/rec |    martial.tactics w/rec |            martial w/rec
   1 |           47/47    |           22/22    |           48/48    | mercy {'pos': 4, 'neg': 0, 'strain': 0}
   2 |           74/74    |           34/34    |           84/84    | mercy {'pos': 6, 'neg': 0, 'strain': 0}
   3 |           98/86    |           50/45    |          119/107   | mercy {'pos': 8, 'neg': 0, 'strain': 0}
   4 |          125/96    |           63/49    |          151/118   | mercy {'pos': 8, 'neg': 0, 'strain': 0}
   5 |          140/86    |           71/44    |          174/111   | mercy {'pos': 8, 'neg': 0, 'strain': 0}
   6 |          140/56    |           71/30    |          182/86    | mercy {'pos': 8, 'neg': 0, 'strain': 0}
   8 |          200/81    |           96/35    |          249/98    | mercy {'pos': 22, 'neg': 0, 'strain': 0}
  10 |          243/89    |          121/42    |          320/120   | mercy {'pos': 34, 'neg': 0, 'strain': 0}
  12 |          288/93    |          140/42    |          377/122   | mercy {'pos': 44, 'neg': 0, 'strain': 0}
  15 |          387/110   |          183/47    |          482/120   | mercy {'pos': 58, 'neg': 0, 'strain': 0}
  20 |          490/58    |          233/28    |          618/78    | mercy {'pos': 70, 'neg': 0, 'strain': 0}
   mercy {'pos': 70, 'neg': 0, 'strain': 0}
   max single-event points: 12

=== Scenario F generalist ===
sess |            martial w/rec |             arcane w/rec |          influence w/rec |    martial.archery w/rec
   1 |           11/11    |           10/10    |            4/4     |            0/0     | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   2 |           21/21    |           25/25    |           40/40    |            6/6     | mercy {'pos': 0, 'neg': 0, 'strain': 0}
   3 |           56/52    |           62/62    |           60/58    |           21/21    | mercy {'pos': 2, 'neg': 0, 'strain': 0}
   4 |           68/60    |           67/59    |           72/59    |           29/29    | mercy {'pos': 2, 'neg': 0, 'strain': 0}
   5 |           78/48    |           72/41    |           80/52    |           33/22    | mercy {'pos': 6, 'neg': 0, 'strain': 0}
   6 |           90/56    |           82/46    |          100/63    |           41/30    | mercy {'pos': 8, 'neg': 0, 'strain': 0}
   8 |          164/97    |          132/65    |          128/52    |           98/71    | mercy {'pos': 8, 'neg': 0, 'strain': 0}
  10 |          206/88    |          140/40    |          148/42    |          128/66    | mercy {'pos': 8, 'neg': 0, 'strain': 0}
  12 |          249/80    |          163/38    |          175/47    |          151/49    | mercy {'pos': 10, 'neg': 0, 'strain': 0}
  15 |          325/84    |          194/31    |          231/60    |          177/30    | mercy {'pos': 16, 'neg': 0, 'strain': 0}
  20 |          443/80    |          275/62    |          288/41    |          245/44    | mercy {'pos': 22, 'neg': 0, 'strain': 0}
   max single-event points: 14

=== Scenario G hybrid archer + fire ===
sess |    martial.archery w/rec |        arcane.fire w/rec |            martial w/rec |             arcane w/rec
   1 |           14/14    |           23/23    |           21/21    |           23/23    | mercy {'pos': 2, 'neg': 0, 'strain': 0}
   2 |           53/53    |           53/53    |           70/70    |           53/53    | mercy {'pos': 2, 'neg': 0, 'strain': 0}
   3 |           75/68    |           71/68    |           98/87    |           71/68    | mercy {'pos': 2, 'neg': 0, 'strain': 0}
   4 |           95/75    |          118/95    |          118/93    |          118/95    | mercy {'pos': 2, 'neg': 0, 'strain': 0}
   5 |          119/81    |          144/112   |          142/92    |          144/112   | mercy {'pos': 2, 'neg': 0, 'strain': 0}
   6 |          152/103   |          158/103   |          175/109   |          158/103   | mercy {'pos': 6, 'neg': 0, 'strain': 0}
   8 |          192/90    |          195/84    |          225/100   |          195/84    | mercy {'pos': 8, 'neg': 0, 'strain': 0}
  10 |          229/73    |          231/62    |          270/88    |          231/62    | mercy {'pos': 8, 'neg': 0, 'strain': 0}
  12 |          265/72    |          259/69    |          312/84    |          259/69    | mercy {'pos': 10, 'neg': 0, 'strain': 0}
  15 |          322/71    |          306/59    |          377/80    |          306/59    | mercy {'pos': 16, 'neg': 0, 'strain': 0}
  20 |          483/109   |          422/81    |          549/115   |          422/81    | mercy {'pos': 22, 'neg': 0, 'strain': 0}
   max single-event points: 14

=== Scenario A over 200 seeds: weighted at session N (p10 / median / p90) ===
deed.martial.archery     s1:8/26/43  s2:25/50/74  s3:48/75/104  s5:91/127/161  s10:213/260/314  s20:406/493/554
deed.martial             s1:14/32/51  s2:38/64/86  s3:66/96/123  s5:116/152/188  s10:264/316/374  s20:528/608/681
deed.guile               s1:2/10/21  s2:10/20/32  s3:18/30/45  s5:32/49/69  s10:75/103/133  s20:167/209/250
deed.guile.stealth       s1:0/8/19  s2:6/16/27  s3:11/24/38  s5:21/38/55  s10:51/80/109  s20:123/165/204
deed.wilds               s1:0/8/16  s2:4/16/27  s3:11/21/36  s5:19/34/52  s10:48/74/97  s20:107/139/177
deed.influence           s1:0/5/13  s2:0/10/22  s3:5/14/28  s5:9/21/37  s10:25/40/61  s20:51/71/100
deed                     s1:38/49/65  s2:77/95/115  s3:120/142/161  s5:201/227/252  s10:430/469/512  s20:850/900/954
recent (median) archery: [26, 50, 69, 88, 95, 80, 78]
recent (median) martial: [32, 64, 84, 107, 116, 102, 101]
mercy net median by session: [0, 2, 4, 4, 12]
pivot: session where recent(fire) > recent(archery): median 12.0 p10 12 p90 13
archery weighted at s20, grinder median 340.0 focused median 486.0
quality mix grinder {'routine': 501} focused {'difficult': 64, 'challenging': 71, 'routine': 9}
C weapon switcher martial s20 median 1105.5  C2 same fights one weapon 1190.5
grinder archery s20: no DR/no cap 2196.0  DR only 910.0  DR+routine cap 340.0
focused archery s20: no DR/no cap 957.5  full rules 486.0
focused but conflict every scene (same scene count as grinder): archery s20 1032.5
E tactics s20 median 236.0 archery 480.5 mercy pos 46.0
E2 tactics s20 median 74.0 archery 482.5 mercy pos 22.0
A (honest) tactics s20 median 0.0 mercy pos 18.0
archery points per session (mean over 20 sessions) median 24.3
focused archery event counts by quality (median over 50 seeds): {'routine': 13.0, 'difficult': 54.5, 'challenging': 98.0}
session at which weighted first reaches threshold (p10/median/p90; 31 = not within 30 sessions)
node                            40          60          80         120         160         200         300         450
deed.martial.archery      1/ 2/  3    2/ 3/  4    3/ 4/  5    4/ 5/  7    6/ 7/  8    7/ 8/ 10   10/12/ 15   16/19/ 22
deed.martial              1/ 2/  3    2/ 2/  3    2/ 3/  4    3/ 4/  6    5/ 6/  7    6/ 7/  8    9/10/ 12   13/15/ 18
deed.guile.stealth        4/ 6/  9    6/ 8/ 11    8/10/ 15   12/15/ 20   15/20/ 26   20/25/ 31   31/31/ 31   31/31/ 31
deed.guile                3/ 5/  7    5/ 6/  9    6/ 8/ 11   10/12/ 15   13/16/ 20   16/20/ 24   25/30/ 31   31/31/ 31
deed.wilds                4/ 6/  9    6/ 9/ 13    9/12/ 16   14/18/ 23   18/23/ 29   24/29/ 31   31/31/ 31   31/31/ 31
deed                      1/ 1/  2    1/ 2/  2    2/ 2/  3    3/ 3/  3    3/ 4/  5    4/ 5/  5    6/ 7/  8    9/10/ 11
hybrid G min(archery, fire)    2/ 2/  4    2/ 3/  5    3/ 4/  6    5/ 6/  8    7/ 8/ 11    8/10/ 13   13/16/ 20   21/24/ 30
A s20 martial vs deed.guile median ratio other/martial = 0.34 median other 205.5
A s20 martial vs deed.wilds median ratio other/martial = 0.23 median other 140.0
A s20 martial vs deed.influence median ratio other/martial = 0.12 median other 70.5
```
