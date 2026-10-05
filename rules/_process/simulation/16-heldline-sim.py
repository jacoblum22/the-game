#!/usr/bin/env python3
"""16-heldline-sim.py -- the held line of 16.7.12 (exact Markov chain, no sampling).

A public tug clock of N segments starts at N/2. Each round the holders make one fortune check: d20 + mod vs DC
(the held foes' highest Guard), degrees per 00.3.10 / 01.8.1 (crit bands +-10, natural 20 one step up, natural 1
one step down): critical success +2, success +1, failure -1, critical failure -2. The DC is the held foes' highest
Guard + 2 x their numbers step (06.10.3: 3-5 members +1, 6+ +2); the holders add +2 x their own numbers step.
Full = the held foes are beaten; 0 = the line breaks. Reports P(holders win) and the mean rounds to an end.
"""
from fractions import Fraction


def degree_probs(mod, dc):
    p = [0, 0, 0, 0]          # cf, f, s, cs
    for d in range(1, 21):
        m = d + mod - dc
        g = 3 if m >= 10 else 2 if m >= 0 else 1 if m > -10 else 0
        if d == 20:
            g = min(3, g + 1)
        if d == 1:
            g = max(0, g - 1)
        p[g] += 1
    return [x / 20.0 for x in p]


def held(mod, dc, n=6):
    pr = degree_probs(mod, dc)
    steps = {0: -2, 1: -1, 2: 1, 3: 2}
    # value iteration on states 1..n-1
    win = {0: 0.0, n: 1.0}
    rounds = {0: 0.0, n: 0.0}
    for s in range(1, n):
        win[s] = 0.5
        rounds[s] = 1.0
    for _ in range(2000):
        for s in range(1, n):
            w = r = 0.0
            for g, q in enumerate(pr):
                t = max(0, min(n, s + steps[g]))
                w += q * win[t]
                r += q * rounds[t]
            win[s] = w
            rounds[s] = 1 + r
    return win[n // 2], rounds[n // 2], pr


if __name__ == '__main__':
    rows = [
        ("band-3 knight (+7) vs a T1 mob of 4 (Guard 12 +2)", 7, 14),
        ("band-3 knight (+7) vs a T1 mob of 6 (Guard 12 +4)", 7, 16),
        ("band-3 knight (+7) vs one T1 (Guard 12)", 7, 12),
        ("band-2 escort (+5) vs one T2 (Guard 15)", 5, 15),
        ("band-2 escort (+5) vs two T2 (15)", 5, 15),
        ("band-2 escort (+5) vs a T2 mob of 4 (15 +2)", 5, 17),
        ("band-1 militia cohort of 4 (+2 +2) vs a T2 mob of 4 (15 +2)", 4, 17),
        ("band-1 villagers, one (+2) vs one T2 (15)", 2, 15),
        ("band-3 knight (+7) vs one T3 (Guard 17)", 7, 17),
        ("band-4 champion (+10) vs one T3 (17)", 10, 17),
    ]
    print("16-heldline-sim.py: 6-segment tug clock from 3; exact")
    for label, m, dc in rows:
        w, r, pr = held(m, dc)
        print("  %-58s P(hold and win) %5.1f%%  mean rounds %4.1f  (CF/F/S/CS %.0f/%.0f/%.0f/%.0f%%)" % (
            label, 100 * w, r, 100 * pr[0], 100 * pr[1], 100 * pr[2], 100 * pr[3]))
