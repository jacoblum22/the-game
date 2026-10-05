# Chapter 10 — simulations and data generators

All scripts are seeded and deterministic; outputs are saved beside them. Run from any directory with Python 3
and PyYAML; generators take `<output file> <data dir>` arguments.

## 10-sim10_travel.py — the travel time-tick die (10.9, T-10-10)
20,000 days per danger rating, four checks a day, the night watch one rung higher, the threat share of the
encounter table 25 / 60 / 75 / 85% (the shipped d12 shares are 25 / 58 / 75 / 83%), a pending threat arriving on
the next E or O face or the fourth check. Per day (no avoidance):

| Rating | Non-threat arrivals | Hostile arrivals | Omens | Event / discovery / opportunity / depletion / weather shift (each) | Lulls |
|---|---|---|---|---|---|
| settled | 0.22 | 0.16 | 0.44 | ≈ 0.33 | 1.57 |
| wild | 0.12 | 0.45 | 0.64 | ≈ 0.33 | 1.24 |
| perilous | 0.11 | 0.66 | 0.77 | ≈ 0.33 | 0.90 |
| deadly | 0.09 | 0.81 | 0.86 | ≈ 0.33 | 0.66 |

With half of omened threats avoided: hostile arrivals 0.09 / 0.27 / 0.41 / 0.52 a day (about 40% fewer).

## 10-sim10_site2.py — the site race (10.13.6–10.13.8)
One Explore onward and one other significant beat per area (the other beat succeeding 3 in 5 and, on failure,
ticking the danger clock); failures and exposure costs tick the danger clock by U(S2) = 1, critical failures 2;
haste is loud (+1 every beat); site checks at the rating's cadence with S faces ticking; each fight ticks once.
Share of delves in which the danger clock completes before the progress clock ("roused first"):

| Site (progress / danger) | Care +3 / +5 / +7 / +9 | Stealth +5 | Haste +5 |
|---|---|---|---|
| medium 8 / 8 (wild) | 46 / 25 / 12 / 4% | 21% | 36% |
| small 6 / 8 | — / 12% / — / — | | |
| large 12 / 12 | — / 26% / — / — | | |

Median beats ≈ 9–10 and intervals ≈ 13 (care), 9 (stealth), 6 (haste) for a medium site. Rating sweep at
medium (8/10 variant): settled 9%, wild 13%, perilous 19%, deadly 42% — the shipped 8/8 medium is harsher by
about 12 points across the board.

## 10-sim10_nav.py — way-finding, foraging and hunting odds (exhaustive d20)
"Off course" = a failure not taken as success-at-cost, or a critical failure.

| Navigator | Easy | Moderate | Hard | Very hard |
|---|---|---|---|---|
| unlicensed fallback (+3, DC +5) | 40% | 65% | 90% | 95% |
| trained (+4) | 10% | 35% | 60% | 85% |
| trained + map (+6) | 5% | 25% | 50% | 75% |
| trained + map + slow (+8) | 5% | 15% | 40% | 65% |

Expected supply a watch: licensed forager (+4) 2.05 / 1.35 / 0.85 / 0.30; unlicensed fallback 0.65 / 0.40 /
0.10 / 0.05; forager role on the move 1.75 / 1.15 / 0.65 / 0.10. Hunting (licensed +4, 2 × reach): 4.1 / 2.7 /
1.7 / 0.6, empty-handed 10 / 35 / 60 / 85%.

## Generators (data/*.yaml for chapter 10)
- `10-gen10_hazards.py` → `data/hazards.yaml` (47 entries; validates tags, afflictions, ≥ 2 signs each).
- `10-gen10_sites.py` → `data/sites.yaml` (8 themes, 14 domains; validates tags, archetypes, hazards; lists
  the 20 theme × domain pairs whose terrain-filtered denizen gate holds fewer than 3 archetypes, which use the
  theme gate alone).
- `10-gen10_traps.py` → `data/traps.yaml` (20 traps; validates tags and afflictions; asserts no subtle
  telltale where harm is S3+).
- `10-gen10_travel.py` → `data/travel.yaml` (validates every tag and archetype; audits all 11 generic
  encounter tables at exactly 6 / 11 / 3 of 20 = 30 / 55 / 15 by relative band; 63 archetype sign sets; 34
  activities).
- `data/weather.yaml` is hand-written; its validation (14 states, 20 regimes of 12, every link a state) is in
  the chapter author's log.
