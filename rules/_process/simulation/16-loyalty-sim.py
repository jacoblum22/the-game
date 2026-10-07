#!/usr/bin/env python3
"""16-loyalty-sim.py -- pacing of chapter 16's regard and grievance clocks (16.5.3-16.5.4).

Model (assumptions stated so the numbers can be re-run when play data exists):
  * 5 scenes a session (03's simulation assumption); 3 sessions of play per in-game week (a week of
    venture is ~7 days, a session covers ~2-3 days of travel and sites); a venture ends every 3 sessions.
  * per scene, an evidence event on one of the ally's two value axes, with probabilities by PC profile:
      aligned:     value A honored 0.25, value B honored 0.15, either affronted 0.03
      indifferent: honored 0.08 / 0.05, affronted 0.06 / 0.04
      opposed:     honored 0.03 / 0.02, affronted 0.25 / 0.15
    (R1 / G1: one tick, at most once per axis per scene)
  * R3 (shared danger, a hard or lethal conflict both survive): 0.08 a scene, all profiles; it marks the
    regard cycle with a star (Devoted allowed).
  * R4 (generosity) 0.5 a week for 'aligned', 0.2 otherwise; R5 (the road together) 1 per venture.
  * grievance decays 1 at each week boundary with no grievance tick that week.
  * standing starts Neutral (0); a regard completion is +1, capped at Friendly (Devoted comes only from
    deeds of weight, 16.5.10, not modelled here); it counts against 15.1.7's +1 a week from small sources
    unless its cycle held a star (R3); a grievance completion is -1 (uncapped), clamped at -3.
Outputs: sessions to the first standing change, standing after 6 / 12 / 24 sessions, share of runs in
which the ally reaches Wary or worse (departure clock) by session 24.
Seeded random.Random(1617). Usage: python 16-loyalty-sim.py [runs]
"""
import random
import sys

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
SCENES = 5
SESS_PER_WEEK = 3
SESS_PER_VENTURE = 3
PROFILES = {
    'aligned':     dict(h=(0.25, 0.15), a=(0.015, 0.015), gift=0.5),
    'indifferent': dict(h=(0.08, 0.05), a=(0.06, 0.04), gift=0.2),
    'opposed':     dict(h=(0.03, 0.02), a=(0.25, 0.15), gift=0.2),
}
R3 = 0.08


def run(rng, prof, sessions=24):
    P = PROFILES[prof]
    regard = griev = 0
    star = False
    standing = 0
    first_change = None
    snap = {}
    small_this_week = 0
    griev_tick_week = False
    went_wary = False
    for s in range(1, sessions + 1):
        for _ in range(SCENES):
            for i in range(2):
                if rng.random() < P['h'][i]:
                    regard += 1
                if rng.random() < P['a'][i]:
                    griev += 1
                    griev_tick_week = True
            if rng.random() < R3:
                regard += 1
                star = True
            # completions
            while regard >= 6:
                regard -= 6
                cap = 2
                if star or small_this_week == 0:
                    if standing < cap:
                        standing += 1
                        first_change = first_change or s
                    if not star:
                        small_this_week += 1
                else:
                    regard = 5                      # the step waits for next week (the cap holds it)
                    break
                star = False
            while griev >= 6:
                griev -= 6
                standing = max(-3, standing - 1)
                first_change = first_change or s
                if standing <= -1:
                    went_wary = True
        if s % SESS_PER_VENTURE == 0:
            regard += 1                              # R5
        if s % SESS_PER_WEEK == 0:
            if rng.random() < P['gift']:
                regard += 1                          # R4
            if not griev_tick_week and griev > 0:
                griev -= 1                           # decay
            griev_tick_week = False
            small_this_week = 0
        if s in (6, 12, 24):
            snap[s] = standing
    return first_change, snap, went_wary


if __name__ == '__main__':
    rng = random.Random(1617)
    print("16-loyalty-sim.py runs=%d (5 scenes/session, 3 sessions/week, venture every 3 sessions)" % RUNS)
    for prof in PROFILES:
        res = [run(rng, prof) for _ in range(RUNS)]
        fc = sorted(r[0] for r in res if r[0])
        med = fc[len(fc) // 2] if fc else None
        def dist(k):
            d = {}
            for r in res:
                d[r[1][k]] = d.get(r[1][k], 0) + 1
            return ", ".join("%+d: %d%%" % (v, round(100.0 * c / RUNS)) for v, c in sorted(d.items()))
        wary = 100.0 * sum(1 for r in res if r[2]) / RUNS
        print("\n%-12s median sessions to first standing change: %s" % (prof, med))
        print("   standing after  6 sessions: %s" % dist(6))
        print("   standing after 12 sessions: %s" % dist(12))
        print("   standing after 24 sessions: %s" % dist(24))
        print("   reached Wary or worse by session 24: %.1f%%" % wary)
