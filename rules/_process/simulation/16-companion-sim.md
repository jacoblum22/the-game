# 16 — Companion simulations

Scripts (seeded or exact; Python 3 + PyYAML), in `rules/_process/simulation/`:
- `16-companion-sim.py` → `16-companion-sim-output.txt` — what allies do to a fight. Imports `09_core.py` (which
  imports 06's `06-conflict-sim.py` unchanged): degrees, harm, the PC reference lines (T-06-12, Vitality by band per
  DL-00-04), the adversary standard line with Fend at T3+ (T-09-3), the morale clock. Adds 06.14's companions: no
  actions, one reaction; Command = one PC action for one companion beat; *guard me* Intercept while not bloodied;
  attention by 06.9.3; a companion's defeat ticks the opposing morale −1. Companion line = 16.4.3 (09's band tables;
  Vitality 6/12/16/18/20). 3,000 fights per row over 16 shapes spanning trivial to lethal at every band.
- `16-loyalty-sim.py` → `16-loyalty-sim-output.txt` — pacing of the regard and grievance clocks (16.5.3) for three PC
  profiles over 24 sessions (4,000 runs each).
- `16-heldline-sim.py` → `16-heldline-sim-output.txt` — the held line (16.7.12) as an exact Markov chain.
- `16-gen_data16.py` → `16-gen_data16-output.txt` — compiles and validates `data/companions.yaml` (40 templates, every
  id checked against tags, licenses, abilities, conditions, effects, wages and base items; 16.4.6's never-out-power
  check at every band).

## Results

**A. The band cap and the advisory contract (T-16-21).** One ally at the PC's own band moves the advisory word by two
in 4 of 16 shapes (mean 1.12); one ally capped at power band − 1 moves it by at most one in all 16 (mean 0.69:
lethal → hard 3/3, fair → easy 5/5, easy → trivial 1/1, hard → fair 2/7 — exactly the two hard shapes whose no-ally
win is 75 or more). Hence 16.2.4's band rule and 16.7.11's hard exception; chapter 09's "one word gentler" is true
for one capped ally. Two capped allies: mean 1.12–1.25, max 2; three: 1.62, max 3; four: 2.00, max 4; a cohort of
four: 1.69 (≈ four individuals' 2.00, so cohorts are priced one place per member). Larger retinues are
under-credited by the one-word rule — the conservative direction.

**B. Loyalty pacing (T-16-22).** Aligned PC: first standing change at a median of 3 sessions; Friendly by session 6 in
89% of runs. Indifferent: Warm by session 6 in 68%; Friendly by 12 in 57%, by 24 in 79%. Opposed: Wary or worse by
session 6 in 83%; lost in every run by 24. With regard uncapped (a first draft) the aligned companion was Devoted by
session 12 in 93% of runs — hence regard stops at Friendly (DL-16-08).

**C. The held line.** Symmetric steps (CS +2, S +1, F −1, CF −2), numbers steps on both sides, 6 segments from 3:
holders of the held foes' band win 62% (mean 7 rounds); a band or more above 75–96%; below or outnumbered 23–34%. A
first draft with success = delivered reach gave equal-band holders 83% — re-tuned (DL-16-14).

**D. Data.** 40 templates, 15 knacks, 17 loyalty sources, 0 validation errors. The validator caught (i) 09's
standard Vitality at bands 3–5 exceeding the leading PC's Vitality (fixed: 16.4.3's lower-of rule and clamp) and
(ii) a wage-band mismatch (the boatman).
