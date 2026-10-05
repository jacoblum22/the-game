# Chapter 11 — world simulation (results)

Script: `rules/_process/simulation/11-world-sim.py` (copied from the scratchpad `world11.py`); raw output:
`11-world-sim-output.txt`. 300 seeds × 104 weeks (two in-game years: 104 World Turns, 8 Season Turns).

**Model (rules as written in 11.2–11.11):** four full factions (Salt Guild tier 2 mercantile; Ash Wardens tier 1
zealous, rising; a margrave tier 3 cautious, entrenched; Ember Cult tier 1 secretive, rising); two wars and one
feud; three petty factions on a d6; faction checks d20 + rating + 2 × tier + stage vs 10 + 2 × tier + 3/5/7 (goal)
or 10 + defender rating + 2 × defender tier (strike/scheme); goal ticks critical 2 / success 1; hold and tier per
11.3.4; growth past tier 3 only by a realm-scope grow goal; the weight of size each Season Turn for tier ≥ 3;
stages per 11.3.9; hooks seeded by goal completions, petty completions, failures, seasonal events (d12 ≤ 4) and
the supply rule (< 3 known open matters); seeded hooks expire at 8 weeks, cap 8; the PC pursues ≤ 2 threads,
active 70% of weeks, 1–3 serving beats a week at +5 vs 15; half of the taken threads race an opposing clock of 6
(+1 a week). Scenarios: an engaged PC; a PC at war with the cult (venture loudness quiet/contained/loud/wild
40/30/20/10%); no PC (a timeskip).

**Results** (p10 / median / p90 per two years): see T-11-24 in `11-living-world.md`.

**Re-run at integration (issue I-026).** `gain_hold()` now follows 11.3.4: rising above tier 3 needs a completed
realm-scope `grow` goal, and any other gain at tier 3 or more only strengthens the hold. The first version let
`expand` and `court` raise a tier-3+ faction. AGENDA now carries 11.3.7's `steadfast` row, and `run()` seeds the
module RNG (`Faction.__init__` draws a first goal from it), so `11-world-sim-output.txt` reproduces byte for byte.
Re-run headlines: goals 21 per region in two years (2.5 per faction per year); mean tier 1.75 → 2.01 (engaged),
1.99 (war), 1.98 (no PC); highest tier reached 3; tier 5 in 0% of faction-runs. Against the committed pre-integration
output file, every other measure moved by at most 1 at any quantile, except traces (rumors), which moved by up to
5 (266 → 271 at p10 with no PC; under 2%). The headlines below are the original pre-integration run, kept for the record; where
they differ, T-11-24 and the re-run govern.

Headlines (original run):
- Faction goals: 2.5 per faction per year (median 5 in two years); about one completed goal every five weeks in a
  region. Tiers drift up 0.6 on average over two years; a tier-5 power arises in 8% of faction-runs; ~1 collapse
  per two years, each replaced (vacuum).
- Hooks: ~60 seeded in two years (one every 10–11 days); ~32 taken up; 19 completed, 11 failed (the world won
  the race), ~23 expired untaken. The PC knew fewer than three open matters in 4 of 104 weeks and never more
  than 10.
- Pressure: an engaged PC drew ~1 move by a hostile faction in two years; a PC at war with one faction drew a
  median 7 entanglements + 4 moves (p90 11 + 8): about one every nine weeks; the bang queue never held more
  than two.
- Traces: ~280 in two years (≈ 2.7 a week): the world is legible.
- With no PC, the world still moves at the same rate (goals 20, situations 13); hooks simply expire.

**Tuning history.** First draft (goal ticks 3/2/1-on-near-miss, DCs not tier-relative): 53 goals per two years
per region (13 per faction), 47% of factions at tier 5 after two years — runaway. Second draft (scope terms 3/5/7
relative to tier, clocks 8/12/24, entrenched −1, weight of size): 38 goals (9 per faction), 9% tier 5. Third
(ticks 2/1/0): the shipped numbers above. Decision: DL-11-03, DL-11-06.

**Exhaustive odds used in the chapter** (d20, 00.3.10 step rule): goal check at rating 3 — local 55% success-or-
better (5% critical failure), regional 45% (10%), realm 35% (20%); equal strike 55%; steward +3 vs 15 45% (10%
critical failure), +5 55% (5%); aging Endure +1 vs Easy/Moderate/Hard/Very hard failure-or-worse 40/65/90/95%;
legacy ledger d20 + L: L 0 → 5/40/55, L 5 → 30/40/30, L 10 → 55/40/5 (strong / opportunity / trouble).
