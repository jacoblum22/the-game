#!/usr/bin/env python3
"""09-lingering-rider.py -- I-090 [revision C4]: what a burning or bleeding rider adds to an adversary's threat.

09.4.3 prices every rider at the same power premium (T-09-6: 0.06), and 09's estimator (PR-09-4) and its Monte-Carlo
model (09_core.fight) leave riders out. 06-conflict-sim.py's section K1 measured lingering harm (burning, bleeding: 1
Vitality per stack at the bearer's turn end, intensify to 3, ended by one action of the bearer) on foes. This script
puts the same condition on the PC: 09_core's fight, unchanged except that each landed attack of a foe with a lingering
rider adds one stack (max 3) to the PC, ticking at the PC's turn end, and the PC answers by one of three policies
(never; always: spend its first action ending it; smart: end it when stacks x 2 rounds >= 3, 06's bearer_ends test).
The PC's best answer (highest win%) is kept, as in K1.

Measured, per band, against the band's standard line (09.4.4) and the PC reference line: the harm ratio (mean
Vitality lost / Vitality, uncapped) and win%. The rider's premium is (ratio with rider / ratio without) - 1, the
quantity T-09-6's premium stands for (09.4.3: Vitality is divided by 1 + premium to keep the harm ratio at the band's).
Usage: python 09-lingering-rider.py [runs]  (default 6000 a cell; seed 909; output 09-lingering-rider-output.txt)
"""
import os, sys, random, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location("core09", os.path.join(HERE, "09_core.py"))
C = importlib.util.module_from_spec(_spec)
_argv = sys.argv; sys.argv = [sys.argv[0]]
_spec.loader.exec_module(C)
sys.argv = _argv
RUNS = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 6000
STAG = {}
REP, degree, harm, sim06 = C.REP, C.degree, C.harm, C.sim06


def fight(rng, pc, foes, rider=False, policy="never", fend=True):
    """09_core.fight with a lingering rider on every foe attack (rider=True) and the PC's answer by policy."""
    p = dict(pc)
    guard, armor, sev = p['guard'], p['armor'], p['sev']
    st = dict(vit=p['vit'], staggered=False, extra=0, lost=0, fend=True, stacks=0)
    nerves = [f.morale for f in foes if not f.fearless]
    mor = sim06.Morale(max(nerves) if nerves and len(nerves) == len(foes) else None, foes)
    t = rng.randint(1, 20) + p['tempo']
    before = [f for f in foes if f.tempo > t]
    after = [f for f in foes if f.tempo <= t]

    def hurt(h):
        was = st['vit']
        st['vit'] -= h
        st['lost'] += h
        if st['staggered'] and h > 0:
            st['extra'] += 1
        if not st['staggered'] and st['vit'] <= 0:
            st['staggered'] = True
            mor.tick(-2)
        elif not mor.pc_blood and st['vit'] * 2 <= p['vit'] < was * 2:
            mor.pc_blood = True
            mor.tick(-1)

    def pc_turn():
        acts, k = 3, 0
        if st['stacks'] and (policy == "always" or (policy == "smart" and st['stacks'] * 2 >= 3)):
            st['stacks'] = 0                         # one action ends it (staunch / beat out the flames)
            acts -= 1
        live = [f for f in foes if f.alive]
        if live:
            tgt = min(live, key=lambda f: (not f.engaged, f.vit))
            if not tgt.engaged:
                tgt.engaged = True
                acts -= 1
            while acts > 0:
                live = [f for f in foes if f.alive]
                if not live or mor.broken:
                    break
                if not tgt.alive:
                    eng = [f for f in live if f.engaged]
                    if eng:
                        tgt = min(eng, key=lambda f: f.vit)
                    else:
                        tgt = min(live, key=lambda f: f.vit)
                        tgt.engaged = True
                        acts -= 1
                        continue
                mod = p['atk'] + REP[min(k, 2)]
                if tgt.fend and not tgt.react_used:
                    mod -= 2
                    tgt.react_used = True
                deg = degree(rng, mod, tgt.guard)
                if deg >= 2:
                    h = harm(sev, (1 if deg == 3 else 0) - (1 if tgt.swarm else 0), 0, tgt.red)
                    if tgt.taken < 1.0:
                        h = int(h * tgt.taken)
                    before_m = tgt.cur_members()
                    tgt.vit -= h
                    if h >= 8:
                        mor.tick(1)
                    if tgt.members == 1 and not tgt.bloodied and tgt.vit * 2 <= tgt.maxvit:
                        tgt.bloodied = True
                        mor.tick(1)
                    fallen = before_m - tgt.cur_members()
                    if fallen > 0:
                        mor.tick(fallen + (1 if tgt.leader and not tgt.alive else 0))
                    mor.strength()
                acts -= 1
                k += 1
        if st['stacks']:
            hurt(st['stacks'])                       # turn end: 1 Vitality a stack, no reduction (06.7)

    def foe_turn(f):
        if not f.alive or mor.broken and not f.fearless:
            return
        f.react_used = False
        acts, k = 2, 0
        if not f.engaged:
            f.engaged = True
            acts -= 1
        while acts > 0:
            s = f.sev
            if f.heavy and not f.wound_up and k == 0 and acts == 2 and rng.random() < 0.5:
                f.wound_up = True
                acts -= 1
                continue
            if f.heavy and f.wound_up and k == 0:
                s = f.heavy
                f.wound_up = False
            mod = f.atk + REP[min(k, 2)]
            if fend and st['fend']:
                mod -= 2
                st['fend'] = False
            deg = degree(rng, mod, guard)
            if deg >= 2:
                hurt(harm(s, f.numbers_step() + (1 if deg == 3 else 0), 0, armor))
                if rider:
                    st['stacks'] = min(3, st['stacks'] + 1)
            acts -= 1
            k += 1

    rounds = 0
    while rounds < 40:
        rounds += 1
        st['fend'] = True
        for f in before:
            foe_turn(f)
        if st['extra'] >= 2:
            break
        pc_turn()
        if st['extra'] >= 2:
            break
        if mor.broken and all(f.fearless is False or not f.alive for f in foes):
            break
        if not any(f.alive for f in foes):
            break
        for f in after:
            foe_turn(f)
        if st['extra'] >= 2:
            break
    over = (mor.broken and not any(f.alive and f.fearless for f in foes)) or not any(f.alive for f in foes)
    return dict(won=over and st['extra'] < 2, lost=st['lost'])


def cell(band, rider, policy):
    rng = random.Random(909)
    pc = C.pc_line(band)
    res = [fight(rng, pc, [C.Foe(C.std(band))], rider=rider, policy=policy) for _ in range(RUNS)]
    win = 100.0 * sum(r['won'] for r in res) / RUNS
    ratio = statistics.mean(r['lost'] for r in res) / pc['vit']
    STAG[(band, rider, policy)] = sum(r['lost'] >= pc['vit'] for r in res) / RUNS
    return win, ratio


if __name__ == "__main__":
    out = []
    P = lambda s="": (out.append(s), print(s))
    P("=== I-090: a lingering-harm rider on the band's standard adversary (09_core fight + rider; %d fights a cell, seed 909) ===" % RUNS)
    P("band | no rider: win%, harm ratio | rider, PC never / always / smart: win%, ratio | PC's best answer | premium | PR-09-4 win% no rider -> rider (word)")
    prem = []
    for b in range(1, 6):
        w0, r0 = cell(b, False, "never")
        stag0 = STAG[(b, False, "never")]
        cells = {pol: cell(b, True, pol) for pol in ("never", "always", "smart")}
        stag_r = {pol: STAG[(b, True, pol)] for pol in cells}
        best = max(cells, key=lambda k: (cells[k][0], -cells[k][1]))
        pr = cells[best][1] / r0 - 1.0
        prem.append(pr)
        e0 = C.estimate(C.pc_line(b), [C.std(b)])
        e1 = C.estimate(C.pc_line(b), [C.std(b, ling=True)])
        P("P%d vs standard T%d | %.1f, %.3f | %s | %s | %.3f | %.1f -> %.1f (%s -> %s; simulated %s -> %s)" % (
            b, b, w0, r0, " / ".join("%.1f, %.3f" % cells[k] for k in ("never", "always", "smart")), best, pr,
            e0[0], e1[0], C.classify_sim(*e0[:2]), C.classify_sim(*e1[:2]),
            C.classify_sim(w0, 100.0 * stag0), C.classify_sim(cells[best][0], 100.0 * stag_r[best])))
    m = statistics.mean(prem)
    P()
    P("mean premium of a lingering rider over bands 1-5: %.3f (T-09-6 rider premium 0.06)" % m)
    P("rounded to T-09-6's grain (0.01): %.2f" % round(m, 2))
    with open(os.path.join(HERE, "09-lingering-rider-output.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
