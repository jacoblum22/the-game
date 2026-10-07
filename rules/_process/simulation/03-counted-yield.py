#!/usr/bin/env python3
"""03-counted-yield.py -- issue I-004: measure counted evidence against weighted evidence, from simulated play.

03.7.3's yield estimate ("6-9 counted units per session") and 04.3.3's counted requirement (counted = the
weighted threshold / 10) rested on arithmetic and on 04's play model (cnt.focus on a fixed share of beats, a
defeat on half of hits). Here the fights are chapter 06's conflict engine (`06-conflict-sim.py`, unchanged
apart from an evidence log): every PC attack beat, every defeat, every foe that flees a broken morale clock and
every point of Focus pushed comes from the rules. Chapter 03's evidence rules are then applied to that log
exactly as written:
  * judged points (03.4.2): quality from base odds (routine >= 70%, difficult 40-65%, challenging <= 35%) 2/4/6;
    stakes Risky +2 / Dire +4; lethal +2; critical success +2; novelty +2 on the first beat of a fight against a
    new kind of foe (one fight in four, an assumption); failures halved; all at the weapon's level-2 node;
  * settlement per scene and node (03.5.2): contributions sorted, 1st full, 2nd half, 3rd a quarter, rest 0;
    routine cap of one routine contribution per node per day (03.5.3);
  * counted (03.7.2-03.7.3): cnt.defeat = the foe's threat band per defeated foe (a mob once, at its band; a foe
    that flees a broken morale clock counts, 'yields or flees'); cnt.focus = Focus pushed; per counter and node
    per scene 1st full, 2nd half, 3rd a quarter, rest 0.
Encounters: chapter 09's budget for a session (T-09-10 / DL-00-05: power band + advisory offset; here the shapes
06's matrix rates fair or easy at each band), stakes Risky, or Dire in 25% of fights of which 40% are lethal
(04's play model). The non-combat pillars are measured in `04-recog-parity.py` (section R9 there), whose
contest counters follow the revised 03.7.2.
Output: counted / weighted per fight and per session at each power band, with and without Focus pushes, and the
verdict on 04.3.3's divisor. Deterministic (seeded). Usage: python 03-counted-yield.py [fights]
"""
import importlib.util
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIGHTS = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
_argv = sys.argv
sys.argv = [sys.argv[0]]
spec = importlib.util.spec_from_file_location("sim06", os.path.join(HERE, "06-conflict-sim.py"))
S6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S6)
sys.argv = _argv

QPTS = {'routine': 2, 'difficult': 4, 'challenging': 6}
SPTS = {'risky': 2, 'dire': 4}


def base_odds(mod, dc):
    """03.4.1: the chance of success or better, in steps of 5%."""
    n = 0
    for d in range(1, 21):
        m = d + mod - dc
        deg = 3 if m >= 10 else 2 if m >= 0 else 1 if m > -10 else 0
        if d == 20:
            deg = min(3, deg + 1)
        if d == 1:
            deg = max(0, deg - 1)
        n += deg >= 2
    return n * 5


def quality(bo):
    return 'routine' if bo >= 70 else 'difficult' if bo >= 40 else 'challenging'


def settle(values):
    v = sorted(values, reverse=True)[:3]
    return sum(x // d for x, d in zip(v, (1, 2, 4)))


# fair and easy shapes by power band (06's matrix, section H; 09's budget): (label, foes factory, mob?)
SHAPES = {
    1: [("1xT1", lambda: [S6.Foe(1)], False), ("2xT1", lambda: [S6.Foe(1), S6.Foe(1)], False), ("T1 mob of 4", lambda: [S6.Foe(1, members=4)], True)],
    2: [("1xT2", lambda: [S6.Foe(2)], False), ("2xT1", lambda: [S6.Foe(1), S6.Foe(1)], False), ("T1 mob of 6", lambda: [S6.Foe(1, members=6)], True)],
    3: [("1xT3", lambda: [S6.Foe(3)], False), ("2xT2", lambda: [S6.Foe(2), S6.Foe(2)], False), ("T2 mob of 4", lambda: [S6.Foe(2, members=4)], True)],
    4: [("1xT4", lambda: [S6.Foe(4)], False), ("2xT3", lambda: [S6.Foe(3), S6.Foe(3)], False), ("T3 mob of 4", lambda: [S6.Foe(3, members=4)], True)],
    5: [("1xT5", lambda: [S6.Foe(5)], False), ("2xT4", lambda: [S6.Foe(4), S6.Foe(4)], False), ("T3 mob of 6", lambda: [S6.Foe(3, members=6)], True)],
}


def one_fight(rng, band, mk, mob, push):
    log = []
    r = S6.fight(rng, band, mk(), use_focus=push, log=log)
    dire = rng.random() < 0.25
    lethal = dire and rng.random() < 0.4
    stakes = 'dire' if dire else 'risky'
    judged = []
    routine_used = False
    novel_first = rng.random() < 0.25
    first = True
    for e in log:
        if e[0] != 'beat':
            continue
        _, mod, dc, deg, steps = e
        q = quality(base_odds(mod, dc))
        p = QPTS[q] + SPTS[stakes] + (2 if lethal else 0) + (2 if deg == 3 else 0) + (2 if (first and novel_first) else 0)
        first = False
        if deg <= 1:
            p //= 2
        if q == 'routine':
            if routine_used:
                continue
            routine_used = True
        judged.append(p)
    weighted = settle(judged)
    defeats = []
    if mob:
        if r['won']:
            defeats.append(mk_band(log))
    else:
        for e in log:
            if e[0] == 'defeat':
                defeats += [e[1]] * e[2]
            elif e[0] == 'fled':
                defeats.append(e[1])
    counted_defeat = settle(defeats)
    counted_focus = settle([1] * r['focus_spent'])
    return weighted, counted_defeat + counted_focus, counted_defeat, counted_focus, r['won']


def mk_band(log):
    bands = [e[1] for e in log if e[0] in ('defeat', 'fled')]
    return max(bands) if bands else 1


if __name__ == '__main__':
    print('=== I-004: counted / weighted at the weapon node, measured on 06\'s conflict engine (%d fights a row) ===' % FIGHTS)
    print()
    print('| Band | Shape | Focus | weighted / fight | counted / fight (defeat + focus) | counted / weighted | won% |')
    print('|---|---|---|---|---|---|---|')
    per_band = {}
    YIELD = {}
    for band in range(1, 6):
        for push in (False, True):
            ws, cs = 0, 0
            for label, mk, mob in SHAPES[band]:
                rng = random.Random(3004 + band)
                rows = [one_fight(rng, band, mk, mob, push) for _ in range(FIGHTS)]
                w = statistics.mean(x[0] for x in rows)
                c = statistics.mean(x[1] for x in rows)
                cd = statistics.mean(x[2] for x in rows)
                cf = statistics.mean(x[3] for x in rows)
                won = 100.0 * sum(x[4] for x in rows) / len(rows)
                ws += w
                cs += c
                print('| P%d | %s | %s | %.1f | %.1f (%.1f + %.1f) | %.2f | %.1f |' % (band, label, 'push' if push else 'none', w, c, cd, cf, c / w, won))
                YIELD.setdefault((band, push), []).append((label, w, c))
            per_band[(band, push)] = cs / ws
    print()
    print('Counted / weighted over the three shapes, by band (no Focus / pushing):')
    for band in range(1, 6):
        print('  P%d: %.2f / %.2f' % (band, per_band[(band, False)], per_band[(band, True)]))
    lo = min(per_band.values())
    hi = max(per_band.values())
    print()
    print('Range %.2f-%.2f. 04.3.3 requires counted >= weighted threshold / 10 (a ratio of 0.10).' % (lo, hi))
    # The direct test: how many extra fights does the counted requirement cost, beyond what the weighted
    # threshold already needs, for a narrow calling's tier-t step fought at band t (04.3.3: 80/160/340/640/1200
    # weighted; counted = that / 10)? Worst shape, with and without Focus.
    W = {1: 80, 2: 160, 3: 340, 4: 640, 5: 1200}   # [revision: I-089] (was 80/200/440/800/1300)
    print()
    print('Extra fights the counted requirement costs for the step into tier t at band t (narrow calling; worst shape):')
    worst = 0
    for t in range(1, 6):
        dW = W[t] - (W[t - 1] if t > 1 else 0)
        dC = W[t] // 10 - ((W[t - 1] // 10) if t > 1 else 0)
        cells = []
        for push in (False, True):
            delays = []
            for label, w, c in YIELD[(t, push)]:
                fw = -(-dW // max(1e-9, w))
                fc = -(-dC // max(1e-9, c))
                delays.append((max(0, int(fc - fw)), label, int(fw)))
            d = max(delays)
            worst = max(worst, d[0])
            cells.append('%s: %d extra of %d (%s)' % ('push' if push else 'no Focus', d[0], d[2], d[1]))
        print('  tier %d: %s' % (t, '; '.join(cells)))
    print()
    print('Verdict: the divisor 10 %s (worst case %d extra fight%s, at the step named above).' % (
        'binds no measured play' if worst == 0 else 'binds only the case shown', worst, '' if worst == 1 else 's'))
