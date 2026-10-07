# Simulation — 04 recognition, tiers, confidence, hybrids and provisional status

Owner: chapter 04 (Recognition and Growth). Purpose: calibrate the thresholds of `data/callings.yaml` by
simulation, define a confidence score that is actually calibrated, design the hybrid trigger (R3 G-1), and
check the anti-grind, breadth and provisional rules. Chapter 04 reports these numbers in 04.3.5, 04.4.2 and
T-04-8.

**Scripts** (Python 3, standard library only, deterministic, seeded). Copies of the scratchpad scripts in
`C:/Users/jacob/AppData/Local/Temp/claude/C--Users-jacob-the-game/8fb5973b-1540-44c9-830b-abd8a1aa0620/scratchpad/`:
- `04-recog04.py`: the engine and the tests R1–R10 (run it from this directory under the name `recog04.py`,
  or adjust the import in the two helper scripts). Output: `04-recog04-output.txt`.
- `04-feat04.py`: which facts about a just-eligible candidate predict later confirmation (the design aid for
  the confidence definition). Output: `04-feat04-output.txt`.
- `04-wren04.py`: one continuous character (seed 7) traced through every recognition event, for the
  chapter's long worked example WE-04-1. Output: `04-wren04-output.txt`.
- `04-gen_data04.py` with `04-callings_header.yaml`: the generator of `data/callings.yaml`,
  `data/hybrids.yaml` and `data/contrib/composites.04.yaml` from compact tables; it validates every tag
  against `data/tags.yaml`.

**What the engine implements.** Chapter 03's evidence rules exactly as its own simulation does (quality from
base odds; points 2/4/6 + stakes + lethal + critical + novelty, failures halved; settlement per scene with
diminishing returns 1, ½, ¼, 0 at every node; the routine cap; the same-target cap; recency over 12 + 12
evidence-bearing scenes), extended with what chapter 04 reads through 03.9: quality counts, distinct scenes,
challenge bands, crises, contexts, counted units with per-scene saturation, co-occurrence. On top of it,
chapter 04's rules as written: the requirement sets of 04.3, the since-last-tier requirements, the five
confirmations and the policy of 04.4, the competence ladder fed back into the character's modifiers,
`power_band` from tiers, lineage exclusion, three seats, the hybrid trigger, the provisional test.

**The play model (assumptions, not rules).** Five scenes per session. Scene mix by play style (for the
archer of 03's scenario A: 45% conflict, 25% stealth or site, 15% social, 15% travel). Conflicts: 3–6 PC
beats; opposition tier from the PC's `power_band` to band + 2 (capped at 5); 25% Dire, of which 40% lethal;
1–3 foes, each successful attack defeating one with probability ½ (0.9 on a critical). Site scenes: 2–4
beats, tier band to band + 1, 20% Dire (30% of those lethal), a progress clock in 60%. Social scenes: 1 beat
(2–4 for the envoy), 15% Dire, progress ticks on half of successes. Counted evidence: `cnt.defeat` = the
foe's band; `cnt.focus` 1 unit on 15% of fight beats before recognition and 45% after; `cnt.progress` 2 (3 on
a critical); `cnt.journey` 1 per travel scene. A reflection runs every second scene. The player accepts
every offer at once unless stated. 200 seeds unless stated. **The counted yields and the scaling of
opposition with `power_band` are the two assumptions that matter most; both are open empirical questions
(OEQ-04-1, OEQ-04-2).**

## Results (p10 / median / p90)

**R1. Sessions to each tier** (one key live; 60 sessions; 99 = not reached).

| Play style, key | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tier 5 | Reached tier 5 |
|---|---|---|---|---|---|---|
| archer who scouts, `martial.archery` | 3/4/5 | 7/9/11 | 16/19/22 | 31/34/38 | 52/56/— | 165 of 200 |
| swordsman fighting in 70% of scenes, `martial.blade` | 2/2/3 | 5/6/7 | 11/12/13 | 19/21/23 | 32/35/37 | 200 |
| burglar, `guile.thievery` | 3/4/5 | 8/10/11 | 18/21/29 | 32/35/40 | 53/59/— | 133 |
| envoy, `influence.persuasion` | 4/5/7 | 9/12/14 | 23/28/48 | 44/49/— | — | 0 |

Target pacing (set before calibration): tier 1 at sessions 3–5, tier 2 near 9, tier 3 near 18, tier 4 near
32, tier 5 not before 50. The archer lands on it; a character who fights in most scenes is about 40% faster;
a negotiator is slower at tiers 3–5 because crises and high-band deeds are rarer in social play (OEQ-04-10).
With only its own key live, the focus calling's first recognition was a **grant** in 198, 200, 200 and 187
of 200 runs (confidence 4 or 5): the grant branch is what a single clear identity normally gets.

**R2. A level-3 key** (Lockbreaker, thresholds × ¾): 3/4/6 · 8/10/12 · 18/22/37 · 34/38/46 · 58/—/—.

**R3. The branch calling Warrior at tier 1** (weighted 120; three children at 30; largest child ≤ 2/3).

| Play style | Offered within 30 sessions | First at session | Largest child's share of `martial` at session 10 |
|---|---|---|---|
| mixed-weapons fighter | 200 of 200 | 3/4/5 | 0.43–0.59 |
| bow-focused archer | 46 of 200 | 7/—/— | 0.67–0.85 |
| single-track swordsman | 4 of 200 | — | 0.77–0.93 |

Mixed-weapons Warrior tiers: 3/4/5 · 7/8/10 · 13/15/16 · 23/25/27 · 43/46/49. [revision: I-108: R3, R7 and R8
re-quoted from the current `04-recog04-output.txt`, which agrees with T-04-8.] (An earlier trial with a share
cap of 3/4 and children at 20 offered Warrior to 93 of 200 archers.)

**R4. The hybrid trigger** (martial × arcane; `min` ≥ 60, `balance` ≥ 2/5, joint scenes ≥ 5, `recent_min` ≥
15, per-branch floors; 20 sessions). This is R3 G-1's acceptance test.

| Share of deeds in the two branches | Offered (of 200) | First offer at session | Balance at session 20 (median) |
|---|---|---|---|
| 100 / 0 | 0 | — | 0.00 |
| 95 / 5 | 0 | — | 0.12 |
| 90 / 10 | 9 | 4/5/9 | 0.23 |
| 80 / 20 | 173 | 3/5/11 | 0.41 |
| 70 / 30 | 200 | 2/3/5 | 0.64 |
| 60 / 40 | 200 | 2/3/4 | 0.79 |
| 50 / 50 | 200 | 2/3/4 | 0.93 |

The archer with stealth as a second pillar (25% of scenes): the martial × guile hybrid was offered in 65 of
200 runs by session 20 (the line, where an offer is the right policy). A deliberate 50/50 hybrid's tiers:
2/3/4 · 5/6/8 · 11/13/14 · 21/23/25 · 36/39/42. (An earlier trial with `balance` ≥ 1/3, joint scenes ≥ 4 and
no recency floor offered the hybrid to 87 of 200 characters playing 90/10.)

**R5. The grinder** (03's scenario B; rats in every scene, 20 sessions): recognized in **0 of 200** runs.
Archery weighted 340, counted 100, difficult-or-better events 0, routine 60. The quality floor is the gate.

**R6. A whole character** (every level-2 key, every branch key, three curated level-3 keys and two hybrids
live; three seats; accepts everything; 100 seeds).

| Play style | First recognition at session | Callings held at sessions 5 / 10 / 20 / 40 | Highest tier at 10 / 20 / 40 / 60 | First calling |
|---|---|---|---|---|
| archer who scouts | 3/4/5 | 1 / 3 / 3 / 3 | 2 / 3 / 4 / 5 | Archer 91, Warrior 4, martial × guile 3, Shadow 2 |
| swordsman | 2/2/3 | 1 / 2 / 2 / 3 | 2 / 3 / 5 / 5 | Blade 100 |
| burglar | 3/4/5 | 2 / 3 / 3 / 3 | 2 / 2 / 4 / 4 | Lockbreaker 51, Thief 43, Shadow 4 |
| three-branch generalist | 3/5/7 | 1 / 3 / 3 / 3 | 1 / 2 / 3 / 4 | martial × arcane 36, Blade 24, Templar 22, Pyromancer 13 |

**R7. Calibration of confidence.** Six play styles × 60 seeds, 20 sessions, nothing accepted; each level-2
candidate is scored at the pass where it first becomes eligible (1,711 candidates). "Would confirm" = its
`recent` is at least 24 after 24 further evidence-bearing scenes (the candidate is still being lived).
"Designed pillar" = the key holds at least 15% of the character's settled deeds at session 20.

| Confidence | Candidates | Would confirm | Designed pillar |
|---|---|---|---|
| 0 | 411 | 38 in 100 | 23 in 100 |
| 1 | 200 | 46 | 45 |
| 2 | 255 | 65 | 83 |
| 3 | 107 | 68 | 89 |
| 4 | 677 | 90 | 98 |
| 5 | 61 | 91 | 98 |
| policy **grant** | 496 | 90 | 98 |
| policy **offer** | 756 | 70 | 81 |
| policy **abstain** | 459 | 38 | 25 |

How the five confirmations were chosen (`04-feat04.py`, 1,383 candidates over seven play styles, 40 seeds;
share that would confirm when the fact is true / false): recent ≥ 40: 85 / 51 · recent ≥ half of weighted:
89 / 55 · key ≥ 1/5 of the root: 87 / 47 · among the top three level-2 nodes: 84 / 47 · weighted ≥ 100
(margin): 80 / 67 · recent ≥ 20 (the currency floor): 73 / 34. Tested and rejected as confirmations because
they predict nothing beyond their floors: counted ≥ 10 (70 / 67), counted ≥ 16 (69 / 70), challenging ≥
routine with 12 quality events (70 / 70). A first definition built from margin, counted margin, quality,
currency and clear field was not monotone (62, 74, 65, 72, 96 in 100 for scores 1–5) and was replaced.

**R8. Provisional grants** (04.8.2: confirm when the evidence at the key since the grant reaches 24 within
24 evidence-bearing scenes). A tier-2 grant, after which the archer turns to fire sorcery:

| After the grant she… | Confirmed | Lapsed |
|---|---|---|
| stops shooting at once | 7 | 172 |
| keeps shooting for one more session | 112 | 67 |
| for two more sessions | 170 | 9 |
| never stops | 179 | 0 |

(179 runs reach the tier-2 grant.) The new calling (Pyromancer) is first recognized 2 / 4 / 5 sessions after the turn. (An earlier rule that
tested `recent ≥ 24` confirmed abandoned tiers, because the recency window still held pre-grant evidence.)

**R9. Counted against weighted** at the focus node, session 10: archery 50 against 237 (0.21); thievery 42
against 220 (0.19); persuasion 27 against 176 (0.15). The counted requirement is one tenth of the weighted
threshold, so it binds only play that yields less than about half of this.

**R10. Vows.** Sessions for one conduct axis to reach 16 / 40 / 80 / 140 / 220 positive points, when the
costly choice is taken in 60% of fights: 4/5/8 · 9/12/16 · 19/24/29 · 35/42/49 · 57/65/75; in 30%: 6/10/16 ·
17/24/33 · 38/47/59 · 71/83/— · —; in 15% (03's honest baseline): 11/18/31 · 32/48/68 · 73/—/— · — · —.

**Wren (seed 7, current ladder; `04-wren04-output.txt`) [revision: I-109].** Archer granted at session 2,
scene 10 (weighted 84, counted 12, recent 84, quality events 11, scenes 8; K1–K4; confidence 4; at the tags:
bow 84, acrobatics 37, spear 20). Archer tier 2 at scene 42 (weighted 181). Tracker eligible at scene 70
(weighted 84, recent 30, confidence 0: abstain at scenes 70, 72, 74 and 75), offered at scene 77 (weighted
101, recent 41, confidence 2). Archer tier 3 in the crisis of scene 80 (weighted 384). Wayfarer at scene 89
(weighted 203, confidence 3, a broaden fork). Shadow first eligible at scene 95 (weighted 115, recent 31,
confidence 1: offered and declined). Ranger eligible at scene 97 (martial 565, wilds 227). Tracker tier 2 at
scene 112 (weighted 162). Consolidation at the season boundary after session 26: martial 695, wilds 336 →
Ranger tier 3. Ranger tier 4 at scene 170 (martial 894, wilds 486). Wilds 933 at session 60: no
tier 5. (The earlier trace in this place was the pre-I-089 run; WE-04-2 and WE-04-3 had quoted it.)

## Reading

1. The ladder W = 80 / 200 / 440 / 800 / 1,300 (narrow) gives the intended slowing curve with no separate
   character number: the session count roughly doubles from each tier to the next (4, 9, 19, 34, 56).
   [revision: I-089] With conflicts at power band + the advisory offset (DL-00-05) the same ladder gave
   5 / 12 / 23 / 40 / 60, the weighted total binding tiers 2–5; tiers 2–5 were retuned to 160 / 340 / 640 /
   1,200 (fine and hybrid ×¾, broad ×1½), giving 5 / 10 / 18 / 32 / 54 (`04-recog04-output.txt`; DL-04-32).
   The Wren trace above is the current one (`04-wren04-output.txt`) [revision: I-109].
2. The since-last-tier requirements rarely bind a focused adventurer (the weighted total binds); they bind
   play that avoids danger, which is their purpose. For social play they slow tiers 3–5.
3. Confidence as defined is monotone in two independent measures of "was this recognition right", which is
   the operational meaning of calibrated. Grants are confirmed nine times in ten and are reversible anyway.
4. The hybrid trigger rejects incidental mixing (≤ 10% of deeds), admits deliberate mixing (≥ 30%) and puts
   second-pillar characters on the line.
5. Every number here depends on 03's point scale and on the play model. If live play yields differ
   (OEQ-03-3, OEQ-04-1), the weighted thresholds scale by one common factor; the structure does not change.

## Revision A (2026-10-05): non-combat parity (I-003) and counted yield (I-004)

**`04-recog-parity.py`** (output `04-recog-parity-output.txt`) loads `04-recog04.py` unchanged and runs one
play shape for every pillar (55% of scenes in the calling's own pillar, 3–6 beats, a quarter Dire and 40% of
those carrying the pillar's worst stakes, 10% of Dire scenes at the brink; conflicts at DL-00-05's advisory
offsets; 200 seeds, 90 sessions). It compares the rules before revision A (contest beats banded by DC; craft
steps always Risky and capped at band 4; no ruinous or brink crisis) with the revised rules (03.4.3 contest
band; 03.4.5 ruinous and brink; 15.3.11; 15.9.20; 08.6.4 item 6).

| Calling | Rules | Tier 3 median | vs archer | Tier 5 median | vs archer |
|---|---|---|---|---|---|
| archer (combat) | — | 19 | — | 51 | — |
| envoy | earlier / revised | 15 / 18 | −21% / −5% | 44 / 46 | −14% / −10% |
| smith | earlier / revised | never / 18 | — / −5% | never / 45 | — / −12% |
| scholar | earlier / revised | 15 / 17 | −21% / −11% | 44 / 46 | −14% / −10% |
| envoy, 04's thin shape (2–4 beats, 15% Dire) | earlier / revised | 18 / 20 | −5% / +5% | 53 / 54 | +4% / +6% |

Acceptance (I-003): tier-3 and tier-5 medians within ±20% of the combat calling: met by all three under the
revised rules. Under the earlier rules the smith never passed tier 2 (no crisis, no band-5 work), which was
the structural defect; the envoy's original lag (28 / never) came from its thinner scene shape and the
pre-DL-00-05 fight model, and is gone in a like-for-like comparison. A counted analogue of `cnt.defeat` for a
contest won was trialled and dropped (it changed no median).

**R9 in the same script and `03-counted-yield.py`** (I-004): counted / weighted at the key after 10 sessions,
medians: archer 0.23; envoy 0.19 → 0.31; smith 0.75 → 0.76; scholar 0.18 → 0.31 (earlier → revised).
Measured on 06's conflict engine: fighter bands 1–5 0.11 / 0.15 / 0.22 / 0.23 / 0.33 without Focus,
0.26–0.44 pushing; the ÷ 10 counted rule costs one extra fight in eight to a band-1, mob-only, no-Focus
fighter and nothing elsewhere, so it stands (DL-04-27).
