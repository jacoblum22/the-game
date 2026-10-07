# Revision C5a report

Agent C5a. Rows: I-040, I-080, I-045, I-051, I-055, I-056, I-066, I-067 (ch.09, 10, 11; 15 not needed). Brief:
`_process/REVISION-AGENT-BRIEF.md`. Baseline: `10-gen10_travel.py`, `10-gen10_sites.py`, `10-word-audit.py` and
`11-world-sim.py` reproduced the committed data and outputs byte for byte before any edit.

## I-040 the audit's reference PC (done)
- The ledger's default (a second reference PC, Guard 10, Vitality 12, no armor, attack +5 at S2) is adopted
  **at home band 1**, the band of every new character and every pregen. `travel.yaml#encounter_audit_reference`
  holds it (emitted by `10-gen10_travel.py`). `10-word-audit.py` (C) fields every home-1 row against both
  reference PCs and applies every word test to both. `10_table_builder.py` (PR-10-10) applies both ceilings, so
  site and world-seed tables pass by construction.
- Why not at every band: measured first. A light reference at Guard 10 fails 51 of 55 generic tables, and at
  Guard 12 it fails 45. At bands 2 and up it is hard or lethal on most rows. The estimator is a no-Focus floor,
  and a non-martial PC above band 1 is defined by its Focus (T-06-12 J), so that test would empty the tables
  without measuring anything. Instead every band is covered **at play time**: new 10.10.4 item 4 says that a
  rolled threat whose advisory is lethal for the PC as it stands arrives with the PC aware first (no ambush,
  the lethal warning at first sight). The creatures stay as rolled (09.8.2: the world does not scale), and
  09.8.1 rule 3 and 09.8.2 cite the new item.
- Tables: all eleven home-1 generic tables failed against the light reference (10 failures). Their home-band
  crowds went from 6–8 to 5–7, and the frozen skeletons to 4–6. All 55 now pass. The light-reference word mix
  at home 1 is trivial 38.2 / easy 19.5 / fair 32.7 / hard 9.5 / lethal 0. The overall mix is now trivial
  37.6 / easy 24.3 / fair 29.9 / hard 8.2 (10.10.2 updated).
- Sim: `10-light-reference-check.py` (seed 4040, 09_core's Monte Carlo). The playtest's seven reptile-folk
  minions take the light PC to 0 Vitality in 24% of fights and the martial PC in 8%; the playtest's own model
  gave 21% and 9%. Across terrains, a crowd of seven does so in 22–57% of fights and a crowd of six in 11–40%.
- Re-runs: `10-site-tables-output.txt` passes 560/560, and only band 1 changed. `12-world-seed-output.txt`
  passes; its 2,600 tables give trivial 35.1 / easy 25.9 / fair 35.5 / hard 3.5. `12-world-seed-example.yaml`
  was re-emitted, with 11 lines changed in three home-1 tables. Note: the playtest's Weeping Meads row 10–12
  is still there, and it is **fair** for the light PC (97.5% win, 24% to 0 Vitality). That is inside T-06-13's
  `fair`, which allows Staggered up to 50%.
- Refs checked: PR-10-8, PR-10-10, 10.10.2, 09.8.1, 09.8.2, T-10-16, and `10-exploration-sim.md`'s numbers.
  12.16's quoted mix is ch.12's, so it goes to **I-096**. Ch.13's separate audit goes to **I-097**. DL-10-28.

## I-080 planted rumors and war (done)
- Ledger default adopted. 11.3.14's closed list gains the rumor row. A rumor moves a relation −1, never
  below −2, and at most once a season per faction toward one rival (`rumor_acted.<rival>`). 11.6.9 states it,
  and `world_turn.yaml#wr.rumor_believed` gains the floor and a `cooldown`.
- Sim: `11-world-sim.py` gains the scenarios `liar_old` and `liar_new`, appended after the three base
  scenarios, whose output is byte-identical. In both, the PC plants one lie a week about a faction pair that
  starts at relation 0, and strikes apply 11.3.14's defender row. Under the old rule 276 of 300 runs reached
  war within a season; under the new rule none did. Within two years the count fell from 300 to 195, and the
  median war week moved from 7 to 55. Every war under the new rule followed a deed row. DL-11-29.

## I-045 the word mix 04 assumes (measured; text handed off)
- `09-word-mix-pacing.py` loads 04-recog04 by path, swaps only its `CONFLICT_OFFSET`, and runs 200 seeds. On
  the tables' measured mix (trivial 34 / easy 26 / fair 36 / hard 4 / lethal 0), a PC who fights only rolled
  encounters stalls: the archer reaches tier 2 at a median session 58 and never reaches tier 3. With half its
  fights chosen (fair 50 / hard 40 / lethal 10), the archer reaches its tiers at 6/13/21/34/58, against
  04.3.5's 5/10/18/32/54.
- 09.12.3 now states that DL-00-05's mix is a campaign mix: it holds only when about half of a PC's fights are
  ones the PC seeks out. The pacing text in 04.3.5, T-04-8 and 02.11.1 belongs to other chapters, so the
  refresh goes to **I-095**, together with the question for 12.7.4. DL-09-26.

## I-066 lone minions (done)
- I took the second option, which adds no new numbers. 09.4.6 gains "A lone minion": one to three minions
  fielded without a mob are a weakened single foe, using the minion line exactly. With Focus 0 they have no
  Focus-cost powers, so a lone minion lich has lost its spells, and the narration must show the weakness.
  T-09-5, 09.4.8's VARIANT and 10.10.1 cite it.
- A `lesser` variant was rejected: it is a fifth variant for a few rows, and powers bought with Focus would sit
  outside the audit's estimator. The audit was re-run. DL-09-27.

## I-067 the guardian heart (done; better than the default)
- New 10.13.10: the guardian is fielded at the site band. When the climax archetype's bands do not cover that
  band, the row's `ref_by_band` names the archetype to use. All 21 guardian rows now cover bands 1–5
  (`10-gen10_sites.py` checks this). The engine compares two shapes, a solo and an elite leading five minions,
  and fields the more dangerous one whose word is at most hard. If neither is, it steps down.
- The ledger's "nearest band" rule was rejected. A guardian two bands up is lethal by 09.6.6 whatever its
  shape: the greater demon at bands 1–2 had no shape under lethal. Below an archetype's top band, a band-5
  heart would be trivial.
- `10-heart-check.py` covers 105 cells and finds none lethal: 62 solo, 34 elite plus mob, 9 elite.
- WE-10-2 now fields a band-1 ghoul elite leading five minions: fair, 92% win / 27% to 0 Vitality. DL-10-30.

## I-055, I-056, I-051 (done)
- **I-055:** new 10.2.6. A settlement's road to its parent area is the area's first leg: the haven ends at the
  gate.
- **I-056:** depletion face 5 gains a fallback: "with neither [mount nor ammunition], one more supply spoils".
  Both the text and the generated `travel.yaml` say so.
- **I-051:** new 10.2.7, "A settlement's day":
  - hours and curfew;
  - the ruler's watch;
  - the law, kept as the ruler's 11.3.12 attention clock;
  - the haven holds.

  The optional NP-07 and LW-10 are anchored as OEQ-11-9 and OEQ-11-10, because there is no ch.14. DL-10-29.

## New rows
- **I-095** (04/02/12): the pacing text against the campaign mix.
- **I-096** (12): 12.16's stale world-seed word mix.
- **I-097** (13): ch.13's own audit lacks the light reference.

The ids skip 091–094 to avoid colliding with parallel agents; the orchestrator may renumber them.

## Close-out
- `appendix/decision-log.md` was re-assembled with `integration-assemble-appendix.py`. No trace fragment
  changed.
- `12-compile_anchors.py`: 0 errors, 0 warnings.
- `validate_ruleset.py`: 0 ERROR / 0 WARN.
