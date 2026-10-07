#!/usr/bin/env python3
"""07-harm-sim.py -- Monte-Carlo and exact arithmetic for chapter 07's harm ladder.

Reuses chapter 06's fight model (06-conflict-sim.py: economy 3 vs 2, repetition snags, Fend, mastery,
morale clock, mobs, windups, T-06-12 reference lines) and replaces its "Dying proxy" with chapter 07's
real ladder:

  * Vitality > 0 (active): harm reduces Vitality; the blow that reaches 0 only Staggers (the excess is
    discarded, 07.2.3).
  * Staggered (Vitality 0): every harm event adds U(bucket) to the wound load (1/1/2/3/4 for a final
    amount of 1-2 / 3-4 / 5-7 / 8-11 / 12+) and leaves a wound of that bucket (07.2.4-07.2.5).
  * wound load >= 3: a LETHAL event moves the PC to Dying at step min(3, 1 + brink); a NON-LETHAL event
    puts the PC Down (out, alive) (07.2.6, 07.2.9). (LOAD_LIMIT=2 in the environment re-runs the rejected value.)
  * Dying 1..3: one action a turn, prone; each lethal harm event adds 1 step (2 for a bucket of S4+);
    at the PC's turn end the dying check: d20 + Endurance + competence floor against DC 10 / 15 / 20 by
    step; critical success = stabilized, success = one step down (from 1: stabilized), a failure within
    3 = holds, failure = +1, critical failure = +2 (07.2.7).
  * a step past 3 is the Threshold: the last-chance menu (07.5).
  * stabilizing adds 1 to brink (07.2.8): one `inj.the_brink` wound, which heals like a Heavy wound
    (a 4-segment recovery clock each, one after another); wound penalties: an arm wound is a status
    penalty on Strikes (S2 -1, S3+ -2; the worst only).
  * foes with defeat_disposition `kill` keep attacking a Dying PC; any other disposition stops when the PC
    is Dying or Down and carries out its disposition (07.7).

PC Vitality by band follows the binding decision DL-00-04: creation 12 + 2 x (band - 1).
Seeded: random.Random(707). Usage: python 07-harm-sim.py [runs]
"""
import importlib.util
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("sim06", os.path.join(HERE, "06-conflict-sim.py"))
sim06 = importlib.util.module_from_spec(spec)
_argv = sys.argv
sys.argv = [sys.argv[0]]
spec.loader.exec_module(sim06)
sys.argv = _argv

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
HARM = sim06.HARM
REP = sim06.REP
PC = sim06.PC
Foe = sim06.Foe
Morale = sim06.Morale
degree = sim06.degree
harm = sim06.harm

UNITS = {1: 1, 2: 1, 3: 2, 4: 3, 5: 4}
DYING_DC = {1: 10, 2: 15, 3: 20}
DYING_STEPS = 3
LOAD_LIMIT = int(os.environ.get("LOAD_LIMIT", "3"))   # 07.2.6; set the variable to 2 to see the rejected value


def bucket(amount):
    return 5 if amount >= 12 else 4 if amount >= 8 else 3 if amount >= 5 else 2 if amount >= 3 else 1


def dying_check(rng, mod, step):
    """Return the change in step: -9 = stabilized outright, -1, 0, +1, +2."""
    d = rng.randint(1, 20)
    m = d + mod - DYING_DC[step]
    deg = 3 if m >= 10 else 2 if m >= 0 else 1 if m > -10 else 0
    if d == 20:
        deg = min(3, deg + 1)
    if d == 1:
        deg = max(0, deg - 1)
    if deg == 3:
        return -9
    if deg == 2:
        return -1
    if deg == 1:
        return 0 if m >= -3 else 1
    return 2


def fight07(rng, pband, foes, lethal=True, kill=True, exit_policy='fight_on', brink0=0, end_mod=2,
            p_escape=0.6, pc_over=None, use_focus=False):
    p = dict(PC[pband])
    if pc_over:
        p.update(pc_over)
    guard = p['guard']
    armor = p['armor']
    st = dict(vit=p['vit'], focus=p['focus'] if use_focus else 0, staggered=False, load=0, dying=0,
              brink=brink0, wounds=[], threshold=False, down=False, entered_dying=False, stabilized=0,
              escaped=False, tried_exit=False, fend=True, arm_pen=0, lost=0, ended=None,
              rounds_dying=0)
    sev = p['sev']
    mor = Morale(max(f.morale for f in foes), foes)
    t = rng.randint(1, 20) + p['tempo']
    before = [f for f in foes if f.tempo > t]
    after = [f for f in foes if f.tempo <= t]

    def take(h):
        """One harm event on the PC with final amount h > 0."""
        st['lost'] += h
        if st['vit'] > 0:
            was = st['vit']
            st['vit'] = max(0, st['vit'] - h)
            if st['vit'] == 0:
                st['staggered'] = True
                mor.tick(-2)
            elif not mor.pc_blood and st['vit'] * 2 <= p['vit'] < was * 2:
                mor.pc_blood = True
                mor.tick(-1)
            return
        b = bucket(h)
        st['wounds'].append(b)
        if rng.random() < 0.25:                         # wound site: the weapon arm, one in four
            st['arm_pen'] = max(st['arm_pen'], 1 if b <= 2 else 2)
        if st['dying'] == 0:
            st['load'] += UNITS[b]
            if st['load'] >= LOAD_LIMIT:
                if lethal:
                    st['dying'] = min(DYING_STEPS, 1 + st['brink'])
                    st['entered_dying'] = True
                else:
                    st['down'] = True
        elif lethal:
            st['dying'] += 2 if b >= 4 else 1
            if st['dying'] > DYING_STEPS:
                st['threshold'] = True

    def pc_strike(tgt, k, steps=0):
        mod = p['atk'] + REP[min(k, 2)] - st['arm_pen'] - (2 if st['dying'] else 0)
        deg = degree(rng, mod, tgt.guard)
        if deg >= 2:
            h = harm(sev, steps + (1 if deg == 3 else 0), 0, tgt.red)
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

    def pc_turn():
        live = [f for f in foes if f.alive]
        if not live:
            return
        if st['dying']:
            st['rounds_dying'] += 1
            eng = [f for f in live if f.engaged]
            if eng:
                pc_strike(min(eng, key=lambda f: f.vit), 0)      # the one action: a last blow
            if not (mor.broken or not any(f.alive for f in foes)):
                pass
            ch = dying_check(rng, end_mod, st['dying'])
            if ch == -9:
                st['dying'] = 0
            else:
                st['dying'] += ch
            if st['dying'] <= 0:
                st['dying'] = 0
                st['stabilized'] += 1
                st['brink'] += 1
            elif st['dying'] > DYING_STEPS:
                st['threshold'] = True
            return
        if st['staggered'] and exit_policy == 'exit_at_staggered' and not st['tried_exit']:
            st['tried_exit'] = True
            if not kill:
                st['ended'] = 'yielded'
                return
            if rng.random() < p_escape:
                st['ended'] = 'escaped'
                return
        acts = 3
        k = 0
        tgt = min(live, key=lambda f: (not f.engaged, f.vit))
        if not tgt.engaged:
            tgt.engaged = True
            acts -= 1
        while acts > 0:
            live = [f for f in foes if f.alive]
            if not live or mor.broken:
                return
            if not tgt.alive:
                eng = [f for f in live if f.engaged]
                if eng:
                    tgt = min(eng, key=lambda f: f.vit)
                else:
                    tgt = min(live, key=lambda f: f.vit)
                    tgt.engaged = True
                    acts -= 1
                    continue
            steps = 0
            if st['focus'] > 0 and k == 0:
                st['focus'] -= 1
                steps = 1
            pc_strike(tgt, k, steps)
            acts -= 1
            k += 1

    def foe_turn(f):
        if not f.alive or mor.broken:
            return
        if (st['dying'] or st['down']) and not kill:
            return
        acts = 2
        k = 0
        if not f.engaged:
            f.engaged = True
            acts -= 1
        while acts > 0 and not st['threshold'] and not st['down']:
            if st['dying'] and not kill:
                return
            s = f.sev
            if f.heavy and not f.wound_up and k == 0 and acts == 2 and rng.random() < 0.5:
                f.wound_up = True
                acts -= 1
                continue
            if f.heavy and f.wound_up and k == 0:
                s = f.heavy
                f.wound_up = False
            mod = f.atk + REP[min(k, 2)] + (2 if st['dying'] else 0)     # a prone target: a lever
            if st['fend'] and not st['dying']:
                mod -= 2
                st['fend'] = False
            deg = degree(rng, mod, guard)
            if deg >= 2:
                h = harm(s, f.numbers_step() + (1 if deg == 3 else 0), 0, armor)
                if h > 0:
                    take(h)
            acts -= 1
            k += 1

    def over():
        return (st['threshold'] or st['down'] or st['ended'] or mor.broken or not any(f.alive for f in foes)
                or ((st['dying']) and not kill))

    rounds = 0
    while rounds < 40:
        rounds += 1
        st['fend'] = True
        for f in before:
            foe_turn(f)
        if over():
            break
        pc_turn()
        if over():
            break
        for f in after:
            foe_turn(f)
        if over():
            break
    won = (mor.broken or not any(f.alive for f in foes)) and not st['threshold'] and not st['down']
    # a PC left Dying after the fight (won, or the non-kill victors have stopped): run the dying checks out
    while st['dying'] and not st['threshold']:
        st['rounds_dying'] += 1
        ch = dying_check(rng, end_mod, st['dying'])
        st['dying'] = 0 if ch == -9 else st['dying'] + ch
        if st['dying'] <= 0:
            st['dying'] = 0
            st['stabilized'] += 1
            st['brink'] += 1
        elif st['dying'] > DYING_STEPS:
            st['threshold'] = True
    return dict(won=won, staggered=st['staggered'], dying=st['entered_dying'], threshold=st['threshold'],
                down=st['down'], rounds=rounds, wounds=list(st['wounds']), stabilized=st['stabilized'],
                brink=st['brink'], ended=st['ended'], lost=min(st['lost'], p['vit']),
                rounds_dying=st['rounds_dying'])


def batch(pband, mk, **kw):
    rng = random.Random(707)
    return [fight07(rng, pband, mk(), **kw) for _ in range(RUNS)]


def pct(res, key):
    return 100.0 * sum(1 for r in res if r[key]) / len(res)


# ------------------------------------------------------------------ recovery arithmetic (07.9)
CLOCK = {3: 4, 4: 6, 5: 12}
REGIMES = {
    # ticks per day on a wound's recovery clock: (long rest, treated, bed rest in a haven)
    'road, untreated': dict(rest=1, treated=0, bed=0),
    'road, treated': dict(rest=1, treated=1, bed=0),
    'haven, bed rest + treated': dict(rest=1, treated=1, bed=1),
}


def wound_days(sev, regime):
    r = REGIMES[regime]
    if sev <= 1:
        return 0
    if sev == 2:
        return 1
    per_day = r['treated'] + r['bed'] + (r['rest'] if sev == 3 else 0)
    if per_day == 0:
        return None                                     # does not heal without care
    days = -(-CLOCK[sev] // per_day)
    if sev == 5:
        days += 1                                       # the day of surgery
    return days


def recovery_days(wounds, brink, regime):
    """Days until: Vitality at maximum, every wound healed, brink 0."""
    r = REGIMES[regime]
    d = 1                                               # one long rest returns Vitality to its (lowered) maximum
    if brink:                                           # each point of brink is a 4-segment clock, healed in turn
        d = max(d, -(-(4 * brink) // (r['rest'] + r['treated'] + r['bed'])))
    for w in wounds:
        wd = wound_days(w, regime)
        if wd is None:
            return None
        d = max(d, wd)
    return d


def q(xs, f):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(f * len(xs)))]


if __name__ == '__main__':
    print("runs per row:", RUNS)

    # ---- A. exact arithmetic: hits to Staggered and to Dying
    print("\n### A. Hits of one severity from full Vitality (exact; success, no critical)\n")
    print("| PC | Vitality | armor | severity | harm after armor | hits to Staggered | further hits to Dying (lethal) | total |")
    print("|---|---|---|---|---|---|---|---|")
    for band, armor in ((1, 0), (1, 1), (3, 0), (3, 2), (5, 3)):
        vit = 12 + 2 * (band - 1)
        for s in (1, 2, 3, 4, 5):
            h = max(0, HARM[s] - armor)
            if h == 0:
                print("| P%d | %d | %d | S%d | 0 | never | - | never |" % (band, vit, armor, s))
                continue
            to_stag = -(-vit // h)
            more = -(-LOAD_LIMIT // UNITS[bucket(h)])
            print("| P%d | %d | %d | S%d | %d | %d | %d | %d |" % (band, vit, armor, s, h, to_stag, more, to_stag + more))

    # ---- B. the dying ladder left alone
    print("\n### B. The dying ladder with no further harm and no help (exact chain, by Endure modifier)\n")
    print("| Endure modifier | enter at | stabilize % | Threshold % | mean rounds |")
    print("|---|---|---|---|---|")
    rng = random.Random(707)
    for mod in (0, 2, 4, 6):
        for start in (1, 2, 3):
            stab = thr = 0
            rs = []
            for _ in range(RUNS * 2):
                step, n = start, 0
                while 0 < step <= DYING_STEPS:
                    n += 1
                    ch = dying_check(rng, mod, step)
                    step = 0 if ch == -9 else step + ch
                if step <= 0:
                    stab += 1
                else:
                    thr += 1
                rs.append(n)
            tot = stab + thr
            print("| %+d | Dying %d | %.0f | %.0f | %.1f |" % (mod, start, 100.0 * stab / tot, 100.0 * thr / tot, statistics.mean(rs)))
    print("\nWith first aid from another each round (Handle +3 against the same DC, success = stabilized):\n")
    print("| Endure modifier | enter at | stabilize % | Threshold % | mean rounds |")
    print("|---|---|---|---|---|")
    for mod in (2,):
        for start in (1, 2, 3):
            stab = thr = 0
            rs = []
            for _ in range(RUNS * 2):
                step, n = start, 0
                while 0 < step <= DYING_STEPS:
                    n += 1
                    if degree(rng, 3, DYING_DC[step]) >= 2:
                        step = 0
                        break
                    ch = dying_check(rng, mod, step)
                    step = 0 if ch == -9 else step + ch
                if step <= 0:
                    stab += 1
                else:
                    thr += 1
                rs.append(n)
            tot = stab + thr
            print("| %+d | Dying %d | %.0f | %.0f | %.1f |" % (mod, start, 100.0 * stab / tot, 100.0 * thr / tot, statistics.mean(rs)))

    # ---- C. fights by advisory level (T-06-13), lethal context, foes that kill
    ADV = [
        ("trivial", [("P1 vs 1 T1", 1, lambda: [Foe(1)]), ("P2 vs 1 T2", 2, lambda: [Foe(2)]),
                     ("P3 vs 1 T3", 3, lambda: [Foe(3)])]),
        ("easy", [("P1 vs 3 T1", 1, lambda: [Foe(1) for _ in range(3)]), ("P1 vs 1 T2", 1, lambda: [Foe(2)]),
                  ("P3 vs 4 T2", 3, lambda: [Foe(2) for _ in range(4)])]),
        ("fair", [("P1 vs 4 T1", 1, lambda: [Foe(1) for _ in range(4)]), ("P2 vs 2 T2", 2, lambda: [Foe(2), Foe(2)]),
                  ("P4 vs 1 T4", 4, lambda: [Foe(4)]), ("P1 vs T1 mob of 6", 1, lambda: [Foe(1, members=6)])]),
        ("hard", [("P1 vs 2 T2", 1, lambda: [Foe(2), Foe(2)]), ("P2 vs 1 T3", 2, lambda: [Foe(3)]),
                  ("P3 vs 2 T3", 3, lambda: [Foe(3), Foe(3)]), ("P3 vs 1 T4", 3, lambda: [Foe(4)]),
                  ("P5 vs 1 T5", 5, lambda: [Foe(5)])]),
        ("lethal", [("P1 vs 1 T3", 1, lambda: [Foe(3)]), ("P2 vs 3 T2", 2, lambda: [Foe(2) for _ in range(3)]),
                    ("P3 vs 3 T3", 3, lambda: [Foe(3) for _ in range(3)]), ("P4 vs 2 T4", 4, lambda: [Foe(4), Foe(4)]),
                    ("P4 vs 1 T5", 4, lambda: [Foe(5)])]),
    ]
    print("\n### C. Lethal context, foes that kill, the PC fights to the end (per 100 fights)\n")
    print("| advisory | fight | win | Staggered | Dying | menu (Threshold) | stabilized in the fight | rounds |")
    print("|---|---|---|---|---|---|---|---|")
    summary = {}
    pool_wounds = []
    for adv, rows in ADV:
        agg = []
        for label, b, mk in rows:
            res = batch(b, mk, lethal=True, kill=True)
            agg.extend(res)
            pool_wounds.extend(r for r in res if r['dying'] and not r['threshold'])
            print("| %s | %s | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f |" % (
                adv, label, pct(res, 'won'), pct(res, 'staggered'), pct(res, 'dying'), pct(res, 'threshold'),
                100.0 * sum(1 for r in res if r['stabilized']) / len(res), statistics.mean(r['rounds'] for r in res)))
        summary[adv] = (pct(agg, 'staggered'), pct(agg, 'dying'), pct(agg, 'threshold'))
    print("\n| advisory (rows pooled) | Staggered | Dying | menu |")
    print("|---|---|---|---|")
    for adv, _ in ADV:
        print("| %s | %.1f | %.1f | %.1f |" % ((adv,) + summary[adv]))

    print("\n### D. The same fights when the player takes an exit on becoming Staggered\n")
    print("(foes that kill: Retreat, resolved as a chase won 60% of the time, else cornered and fighting on;"
          " foes that capture or rob: Yield, accepted)\n")
    print("| advisory | Dying, fight on | menu, fight on | Dying, exit (kill foes) | menu, exit (kill foes) | escaped | Dying, yield (non-kill foes) | menu, yield |")
    print("|---|---|---|---|---|---|---|---|")
    for adv, rows in ADV:
        a0, a1, a2 = [], [], []
        for label, b, mk in rows:
            a0.extend(batch(b, mk, lethal=True, kill=True))
            a1.extend(batch(b, mk, lethal=True, kill=True, exit_policy='exit_at_staggered'))
            a2.extend(batch(b, mk, lethal=True, kill=False, exit_policy='exit_at_staggered'))
        print("| %s | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f |" % (
            adv, pct(a0, 'dying'), pct(a0, 'threshold'), pct(a1, 'dying'), pct(a1, 'threshold'),
            100.0 * sum(1 for r in a1 if r['ended'] == 'escaped') / len(a1), pct(a2, 'dying'), pct(a2, 'threshold')))

    print("\n### E. Risky fights (no lethal context) against Dire fights (lethal context): the same foes\n")
    print("| advisory | Risky: Staggered | Risky: Down | Risky: Dying | Dire, foes capture: Dying | Dire, foes capture: menu | Dire, foes kill: Dying | Dire, foes kill: menu |")
    print("|---|---|---|---|---|---|---|---|")
    for adv, rows in ADV:
        r0, r1, r2 = [], [], []
        for label, b, mk in rows:
            r0.extend(batch(b, mk, lethal=False, kill=False))
            r1.extend(batch(b, mk, lethal=True, kill=False))
            r2.extend(batch(b, mk, lethal=True, kill=True))
        print("| %s | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f |" % (
            adv, pct(r0, 'staggered'), pct(r0, 'down'), pct(r0, 'dying'), pct(r1, 'dying'), pct(r1, 'threshold'),
            pct(r2, 'dying'), pct(r2, 'threshold')))

    print("\n### F. Wounded memory: the same fight entered with brink 0, 1, 2 (P3 vs 2 T3, foes that kill)\n")
    print("| brink at the start | Dying | menu | menu given Dying |")
    print("|---|---|---|---|")
    for bk in (0, 1, 2):
        res = batch(3, lambda: [Foe(3), Foe(3)], lethal=True, kill=True, brink0=bk)
        dy = pct(res, 'dying')
        th = pct(res, 'threshold')
        print("| %d | %.1f | %.1f | %.0f |" % (bk, dy, th, 100.0 * th / dy if dy else 0))

    print("\n### G. Recovery: days from Dying to full (Vitality at maximum, wounds healed, brink 0)\n")
    surv = pool_wounds
    print("survivors of Dying pooled from section C: %d" % len(surv))
    sevs = [w for r in surv for w in r['wounds']]
    print("wounds carried by a survivor: mean %.1f; share by severity: " % (len(sevs) / max(1, len(surv)))
          + ", ".join("S%d %.0f%%" % (s, 100.0 * sevs.count(s) / max(1, len(sevs))) for s in (1, 2, 3, 4, 5)))
    print("worst wound of a survivor: " + ", ".join(
        "S%d %.0f%%" % (s, 100.0 * sum(1 for r in surv if r['wounds'] and max(r['wounds']) == s) / max(1, len(surv)))
        for s in (1, 2, 3, 4, 5)))
    print()
    print("| regime | median days | 75th pct | 90th pct | share that cannot fully heal without care |")
    print("|---|---|---|---|---|")
    for regime in REGIMES:
        ds = [recovery_days(r['wounds'], r['brink'], regime) for r in surv]
        ok = [d for d in ds if d is not None]
        print("| %s | %d | %d | %d | %.0f%% |" % (regime, q(ok, 0.5), q(ok, 0.75), q(ok, 0.9),
                                                  100.0 * (len(ds) - len(ok)) / max(1, len(ds))))
    print("\n| wound | clock | road, untreated | road, treated | haven, bed rest + treated |")
    print("|---|---|---|---|---|")
    for s in (2, 3, 4, 5):
        print("| S%d | %s | %s | %s | %s |" % (s, CLOCK.get(s, '-'), wound_days(s, 'road, untreated'),
                                             wound_days(s, 'road, treated'), wound_days(s, 'haven, bed rest + treated')))

    print("\n### H. Vitality back by rest (07.8): rests needed from 0 to maximum, no wounds\n")
    print("| max Vitality | breather +2 | short rest +half | long rest |")
    print("|---|---|---|---|")
    for mx in (12, 16, 20, 24):
        print("| %d | %d breathers (2 count between short rests) | %d short rests (2 a day at this rate) | 1 (full quality) |" % (
            mx, -(-mx // 2), 2))

    print("\n### I. The Gamble (07.5.9): Endure against Moderate (DC 15)\n")
    print("| Endure modifier | stand, no cost (critical success) | live, no further cost (success) | choose a price (within 3) | death |")
    print("|---|---|---|---|---|")
    for mod in (-1, 0, 1, 2, 3, 4, 5, 6):
        cs = s_ = nm = dead = 0
        for d in range(1, 21):
            m = d + mod - 15
            deg = 3 if m >= 10 else 2 if m >= 0 else 1 if m > -10 else 0
            if d == 20:
                deg = min(3, deg + 1)
            if d == 1:
                deg = max(0, deg - 1)
            if deg == 3:
                cs += 5
            elif deg == 2:
                s_ += 5
            elif deg == 1 and m >= -3:
                nm += 5
            else:
                dead += 5
        print("| %+d | %d%% | %d%% | %d%% | %d%% |" % (mod, cs, s_, nm, dead))
