# 02 — Character: data generation, audits and simulations

Scripts: `rules/_process/simulation/02-gen_data02/` (copies of the scratchpad `ch02/` scripts).
Run from that folder with Python 3.12 (`gen02.py` needs no third-party module; `tables02.py`,
`draws02.py` and `sim02.py` need PyYAML).

| Script | What it does | Output |
|---|---|---|
| `data02.py` + `creation_block.py` | the authored tables: 8 peoples, 9 upbringings, 21 livelihoods, 4 profiles, 30 kits, 22 quirks, 7 gifts, the Bent gates, creation defaults and random tables | — |
| `gen02.py --emit` | validates every id against `tags.yaml`, `licenses.yaml`, `abilities.yaml` and the effect files; checks upbringing budgets, profile/default agreement, technique eligibility, magic coverage, bond-seed order, hook kinds, the 81-tag coverage; emits `data/origins.yaml`, `gen_birth.yaml`, `kits.yaml`; prints audits A1–A7 | `gen02-output.txt` |
| `gen_contrib02.py` | emits `data/contrib/licenses.02.yaml`, `effects.02.yaml`, `boundaries.02.yaml` | — |
| `tables02.py` | renders chapter 02's data-derived tables (T-02-2…T-02-10, T-02-13) from the shipped data | `part6.md` (pasted into the chapter) |
| `draws02.py` | performs the `gen.birth` draws of the worked examples from the shipped `gen_birth.yaml` with fixed seeds | `draws02-output.txt` |
| `sim02.py` | runs chapter 06's `06-conflict-sim.py` with the stat lines of new characters (band 1, no Focus) | `sim02-output.txt` |

## Results used in the chapter

- **A1 Placements.** Free rule: 1,680 legal placements (840 / 630 / 210 for Peaked / Even / Broad);
  each people's Typical rule: 84 (54 / 6 / 24). (02.3.3)
- **A3 Quantity against freedom** (T-02-3). Mean premium of a people's Typical rule (+7, three
  placements decided) over the Free rule (+5) across 16 concepts: Elf +0.9, Dwarf −0.2, Halfling +1.9,
  Orc-kin +0.9, Goblin-kin +1.2, Giant-kin −2.9, Beastfolk +0.9; each people better than Free for 4–11
  concepts and worse for 5–12. An earlier draft with Typical at +6 was worse than Free for 8–13 of 16
  concepts for every people (mean −2.0 to −6.6): that is why the Typical sum is +7 (DL-02-04).
- **A4 Knack pools** (T-02-9). 15 to 52 eligible knacks over all 1,512 origin combinations (median 35);
  chance the knack lands on a default deep training: 0% (Wanderer) to 12% (Charlatan). Quirk weights:
  uncanny 10.0% → 25.0% when omened; hardy 27.5% → 53.2% when hard.
- **A5 The Bent** (T-02-11). With n attributes eligible, wanting one: first draw 1/n; deferring until
  it comes (two deferrals, struck entries) min(1, 3/n).
- **A6 Starting odds** (T-02-15): untrained +1: 60/35/10/5% at DC 10/15/20/25; specialist +5:
  80/55/30/5%; with a knack +6: 85/60/35/10%.
- **sim02 (OEQ-02-10)**, 20,000 fights per row, chapter 06's reference foes, no Focus spent:

| Line | vs 1×T1 win | vs 2×T1 win | vs 1×T2 win |
|---|---|---|---|
| 06's reference P1 (+5, Guard 14, Vit 12, armor 1) | 100.0 | 99.9 | 98.7 |
| Wren, Free hunter (+5, 14, 12, 1) | 100.0 | 99.9 | 98.7 |
| Bram, Free soldier with shield (+5, 14, 14, 1) | 100.0 | 99.9 | 99.4 |
| Dwarf Typical soldier (+5, 12, 14, 1) | 100.0 | 99.8 | 98.2 |
| Orc-kin Typical soldier with a blade knack (+6, 15, 14, 1) | 100.0 | 100.0 | 99.8 |
| Thessaly, Free acolyte with mace, no Focus (+0, 11, 12, 0) | 98.6 | 80.5 | 30.9 |
| Elf Typical apprentice with staff, no Focus (+1, 13, 11, 0) | 99.5 | 90.9 | 54.9 |
| Weakest legal line (+0, Guard 10, Vit 11, no armor) | 97.2 | 72.7 | 21.0 |

Reading: every legal martial start is robust; a new caster who must melee a trained foe without Focus
loses more often than not. This is the case for issue I-009 (05's zero-cost workings) and for 09's
advisory reading the PC's actual line at band 1 (02 Interface requests to 05 and 09).

- **sim02, revision I-009**: the same harness, new casters using their **branch working** (05.7.11: rank 1,
  Moderate harm, one action, no Focus, no slot). Casting modifier = casting attribute + the school's +2;
  Vitality 12 + Endurance; Guard 10 + Agility + 1. Since I-009, 02.3.5 defaults a magic livelihood to the
  Free rule where its Typical rule would fix the casting attribute at −1.

| Line | vs 1×T1 win | vs 2×T1 win | vs 1×T2 win |
|---|---|---|---|
| Thessaly, Free acolyte, Rebuke (+5, 11, 12) | 100.0 | 98.4 | 90.5 |
| Elf Typical apprentice, Force Bolt (+5, 13, 11) | 100.0 | 99.1 | 94.4 |
| Human Free hedge-taught (default), Wild Lash (+5, 11, 13) | 100.0 | 99.0 | 92.1 |
| Human Free Touched (default), Wild Lash (+5, 13, 12) | 100.0 | 99.3 | 94.8 |
| Orc-kin apprentice (default since I-009, Free rule), Force Bolt (+5, 11, 12) | 100.0 | 98.6 | 91.6 |
| Goblin-kin acolyte keeping the Typical rule (Presence −1), Rebuke (+1, 12, 14) | 99.8 | 94.5 | 64.3 |
| Orc-kin apprentice keeping the Typical rule (Intellect −1), Force Bolt (+1, 12, 12) | 99.8 | 92.7 | 62.0 |
| Beastfolk hedge-taught keeping the Typical rule (Resolve −1), Wild Lash (+1, 13, 14) | 99.9 | 96.2 | 72.8 |
| Weakest legal caster (+1, Guard 10, Vit 11), Wild Lash | 98.9 | 83.5 | 39.3 |

Reading: every default-path new caster beats one trained foe 90.5–94.8% on the working alone (I-009's
acceptance: ≥ 75%). The casters below 75% have chosen a Typical rule that fixes their casting attribute at
−1, against 02.3.5's default; the DM states those odds before the player confirms, and 09's advisory reads
the real line. Rows read from `02-gen_data02/sim02-output.txt` (the earlier rows are unchanged).
