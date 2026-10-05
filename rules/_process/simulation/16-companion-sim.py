#!/usr/bin/env python3
"""16-companion-sim.py -- what a companion does to a fight, on chapters 06/07/09's own numbers.

Imports chapter 09's `09_core.py` (which imports 06's `06-conflict-sim.py` unchanged) for degree(), harm(),
the PC reference lines (T-06-12; Vitality 12/14/16/18/20 by DL-00-04), the adversary standard line
(T-09-3, with adversary Fend at T3+) and the morale clock, and adds chapter 16's companions as 06.14
defines them:
  * a companion has NO actions of its own and ONE reaction (06.1.1);
  * Command = 1 PC action buys ONE companion beat, framed with the companion's numbers; the companion keeps
    its own repetition window (06.14.2);
  * standing order `guard me`: the companion's reaction intercepts one hit meant for the PC (06.6.7),
    otherwise its reaction is Fend (-2 on one attack against it each round);
  * adversaries choose targets by 06.9.3's attention order: an enemy engaged with it that dealt it the most
    harm since its last turn; else the nearest, the PC before a companion;
  * a companion at 0 Vitality is defeated (07.12.1: Down or bleeding out; out of the fight either way) and
    ticks the opposing morale clock -1 (06.11.3);
  * companion lines are chapter 16's T-16-4: the adversary standard line of the companion's band (T-09-3)
    with chapter 16's companion Vitality (16.4.3) -- by construction weaker than the PC of the same band.

PC policies:
  none     -- no companion (the baseline; reproduces 09's section A/B numbers)
  guard    -- one companion under `guard me`; never commanded (the PC keeps all three actions)
  command  -- one companion under `guard me`; the PC spends its FIRST action each turn commanding the
              companion to Strike the PC's target, then makes two Strikes of its own (0 / -2)
  commandN -- N companions; the PC commands each once (N <= 2), then Strikes with what is left
Seeded random.Random(1616). Usage: python 16-companion-sim.py [runs]
"""
import importlib.util
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("core09", os.path.join(HERE, "09_core.py"))
C = importlib.util.module_from_spec(_spec)
_argv = sys.argv
sys.argv = [sys.argv[0]]
_spec.loader.exec_module(C)
sys.argv = _argv

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
REP = C.REP
degree = C.degree
harm = C.harm
WORDS = ['trivial', 'easy', 'fair', 'hard', 'lethal']

# chapter 16's companion Vitality (16.4.3): the lower of the band's standard adversary Vitality (T-09-3) and the
# PC reference Vitality of that band (T-06-12 / DL-00-04), with band 1 raised to 6 so a band-1 ally survives one
# heavy blow; always below the Vitality of the PC who can lead it
COMP_VIT = {1: 6, 2: 12, 3: 16, 4: 18, 5: 20}
COMP_ARMOR = {1: 1, 2: 1, 3: 2, 4: 2, 5: 2}        # a hireling's worn armor by band (16.4.3; 08 armor 1/2/3)


def comp_line(band):
    s = C.STANDARD[band]
    return dict(band=band, atk=s['atk'], guard=s['guard'], vit=COMP_VIT[band], sev=s['sev'],
                red=COMP_ARMOR[band])


class Comp:
    def __init__(s, line, members=1):
        s.atk = line['atk']
        s.guard = line['guard']
        s.per = line['vit']
        s.members = members
        s.maxvit = line['vit'] * members          # a cohort (16.2.6) pools Vitality like a mob (06.10.2)
        s.vit = s.maxvit
        s.sev = line['sev']
        s.red = line['red']
        s.react = True
        s.engaged_with = set()

    @property
    def up(s):
        return s.vit > 0

    def step(s):                                   # 06.10.3's numbers step for a cohort's attacks
        if s.members == 1:
            return 0
        m = max(0, -(-s.vit // s.per))
        return 2 if m >= 6 else 1 if m >= 3 else 0


def fight(rng, pc, foes, comps, policy):
    p = dict(pc)
    st = dict(vit=p['vit'], staggered=False, extra=0, fend=True)
    nerves = [f.morale for f in foes if not f.fearless]
    mor = C.sim06.Morale(max(nerves) if nerves and len(nerves) == len(foes) else None, foes)
    t = rng.randint(1, 20) + p['tempo']
    before = [f for f in foes if f.tempo > t]
    after = [f for f in foes if f.tempo <= t]
    # per-foe harm since its last turn: {'pc': n, i: n}
    for f in foes:
        f.dealt = {}
    downed = [False] * len(comps)

    def hit_foe(f, h, who):
        before_m = f.cur_members()
        f.vit -= h
        f.dealt[who] = f.dealt.get(who, 0) + h
        if h >= 8:
            mor.tick(1)
        if f.members == 1 and not f.bloodied and f.vit * 2 <= f.maxvit:
            f.bloodied = True
            mor.tick(1)
        fallen = before_m - f.cur_members()
        if fallen > 0:
            mor.tick(fallen + (1 if f.leader and not f.alive else 0))
        mor.strength()

    def strike(atk, k, sev, tgt, who, extra=0):
        mod = atk + REP[min(k, 2)]
        if tgt.fend and not tgt.react_used:
            mod -= 2
            tgt.react_used = True
        deg = degree(rng, mod, tgt.guard)
        if deg >= 2:
            h = harm(sev, extra + (1 if deg == 3 else 0) - (1 if tgt.swarm else 0), 0, tgt.red)
            hit_foe(tgt, h, who)

    def pc_turn():
        acts = 3
        k = 0
        live = [f for f in foes if f.alive]
        if not live:
            return
        tgt = min(live, key=lambda f: (not f.engaged, f.vit))
        if not tgt.engaged:
            tgt.engaged = True
            acts -= 1
        n_cmd = 0
        if policy.startswith('command'):
            n_cmd = 1 if policy == 'command' else int(policy[7:])
        for ci, c in enumerate(comps):
            if n_cmd <= 0 or acts <= 0:
                break
            if not c.up:
                continue
            live = [f for f in foes if f.alive]
            if not live or mor.broken:
                return
            if not tgt.alive:
                tgt = min(live, key=lambda f: f.vit)
            c.engaged_with.add(id(tgt))
            strike(c.atk, 0, c.sev, tgt, ci, c.step())       # its own repetition window: first attack at 0
            acts -= 1
            n_cmd -= 1
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
            strike(p['atk'], k, p['sev'], tgt, 'pc')
            acts -= 1
            k += 1

    def harm_pc(h):
        st['vit'] -= h
        if st['staggered'] and h > 0:
            st['extra'] += 1
        if not st['staggered'] and st['vit'] <= 0:
            st['staggered'] = True
            mor.tick(-2)
        elif not mor.pc_blood and st['vit'] * 2 <= p['vit'] < (st['vit'] + h) * 2:
            mor.pc_blood = True
            mor.tick(-1)

    def harm_comp(ci, h):
        c = comps[ci]
        c.vit -= h
        if c.vit <= 0 and not downed[ci]:
            downed[ci] = True
            mor.tick(-1)                           # 06.11.3: a companion of the PC is defeated

    def choose_target(f):
        # 06.9.3: an enemy engaged with it, the one that dealt it the most harm since its last turn
        cands = [('pc', f.dealt.get('pc', 0))]
        for ci, c in enumerate(comps):
            if c.up and id(f) in c.engaged_with:
                cands.append((ci, f.dealt.get(ci, 0)))
        best = max(cands, key=lambda x: (x[1], x[0] == 'pc'))   # ties: the PC first (nearest rule)
        return best[0]

    def foe_turn(f):
        if not f.alive or mor.broken and not f.fearless:
            return
        f.react_used = False
        if f.regen and f.alive:
            f.vit = min(f.maxvit, f.vit + f.regen)
        acts = 2
        k = 0
        if not f.engaged:
            f.engaged = True
            acts -= 1
        who = choose_target(f)
        f.dealt = {}
        while acts > 0:
            s = f.sev
            if f.heavy and not f.wound_up and k == 0 and acts == 2 and rng.random() < 0.5:
                f.wound_up = True
                acts -= 1
                continue
            if f.heavy and f.wound_up and k == 0:
                s = f.heavy
                f.wound_up = False
            if who != 'pc' and not comps[who].up:
                who = 'pc'
            mod = f.atk + REP[min(k, 2)]
            if who == 'pc':
                if st['fend']:
                    mod -= 2
                    st['fend'] = False
                deg = degree(rng, mod, p['guard'])
                if deg >= 2:
                    steps = f.numbers_step() + (1 if deg == 3 else 0)
                    # guard me: the companion's reaction takes one hit meant for the PC (06.6.7), while it
                    # is not bloodied (the player protects a hurt companion: 16.6.4's default)
                    g = next((ci for ci, c in enumerate(comps)
                              if c.up and c.react and c.vit * 2 > c.maxvit), None)
                    if g is not None and policy != 'none':
                        comps[g].react = False
                        harm_comp(g, harm(s, steps, 0, comps[g].red))
                    else:
                        harm_pc(harm(s, steps, 0, p['armor']))
            else:
                c = comps[who]
                if c.react:
                    mod -= 2                        # the companion's Fend
                    c.react = False
                deg = degree(rng, mod, c.guard)
                if deg >= 2:
                    harm_comp(who, harm(s, f.numbers_step() + (1 if deg == 3 else 0), 0, c.red))
            acts -= 1
            k += 1

    rounds = 0
    while rounds < 40:
        rounds += 1
        st['fend'] = True
        for c in comps:
            c.react = True
        for f in before:
            foe_turn(f)
        if st['extra'] >= 2:
            break
        pc_turn()
        if not any(f.alive for f in foes) or mor.broken and all(not f.fearless or not f.alive for f in foes):
            break
        for f in after:
            foe_turn(f)
        if st['extra'] >= 2:
            break
    over = (mor.broken and not any(f.alive and f.fearless for f in foes)) or not any(f.alive for f in foes)
    won = over and st['extra'] < 2
    return dict(won=won, staggered=st['staggered'], comp_down=sum(downed), rounds=rounds)


def run(pc_band, foe_lines, comp_bands, policy, runs=RUNS, seed=1616):
    rng = random.Random(seed)
    pc = C.pc_line(pc_band)
    res = []
    for _ in range(runs):
        foes = [C.Foe(x, members=x.get('members', 1), leader=x.get('leader', False)) for x in foe_lines]
        comps = [Comp(comp_line(b[0]), b[1]) if isinstance(b, tuple) else Comp(comp_line(b)) for b in comp_bands]
        res.append(fight(rng, pc, foes, comps, policy if comp_bands else 'none'))
    n = float(runs)
    win = 100.0 * sum(r['won'] for r in res) / n
    stag = 100.0 * sum(r['staggered'] for r in res) / n
    cd = 100.0 * sum(1 for r in res if r['comp_down']) / n
    return win, stag, cd


def shape(pb, fb, n, members=1):
    if members > 1:
        L = C.std(fb, members=members)
        return [L]
    return [C.std(fb) for _ in range(n)]


SHAPES = [
    # (label, pc band, foe band, count, mob members)
    ("P1 vs 4 T1", 1, 1, 4, 1), ("P1 vs 6 T1", 1, 1, 6, 1), ("P1 vs 2 T2", 1, 2, 2, 1),
    ("P1 vs T1 mob of 8", 1, 1, 1, 8),
    ("P2 vs 2 T2", 2, 2, 2, 1), ("P2 vs 3 T2", 2, 2, 3, 1), ("P2 vs T3", 2, 3, 1, 1),
    ("P2 vs T2 mob of 4", 2, 2, 1, 4),
    ("P3 vs 2 T3", 3, 3, 2, 1), ("P3 vs T4", 3, 4, 1, 1), ("P3 vs 4 T2", 3, 2, 4, 1),
    ("P4 vs T4", 4, 4, 1, 1), ("P4 vs 2 T3", 4, 3, 2, 1), ("P4 vs 3 T3", 4, 3, 3, 1),
    ("P5 vs T5", 5, 5, 1, 1), ("P5 vs 2 T4", 5, 4, 2, 1),
]

CONFIGS = [
    ("none", [], 'none'),
    ("1 equal, command", ['eq'], 'command'),
    ("1 capped, guard", ['lo'], 'guard'),
    ("1 capped, command", ['lo'], 'command'),
    ("2 capped, command x1", ['lo', 'lo'], 'command'),
    ("2 capped, command x2", ['lo', 'lo'], 'command2'),
    ("3 capped, command x2", ['lo', 'lo', 'lo'], 'command2'),
    ("4 capped, command x2", ['lo', 'lo', 'lo', 'lo'], 'command2'),
    ("cohort of 4 capped, cmd", ['co4'], 'command'),
    ("cohort of 4 at band-2, cmd", ['c24'], 'command'),
    ("cohort of 6 at band-2, cmd", ['c26'], 'command'),
]

if __name__ == '__main__':
    print("16-companion-sim.py  runs/row=%d  seed 1616" % RUNS)
    print("Companion lines (T-16-4):", {b: comp_line(b) for b in range(1, 6)})
    print()
    shifts = {c[0]: [] for c in CONFIGS[1:]}
    for label, pb, fb, n, mem in SHAPES:
        lines = shape(pb, fb, n, mem)
        base = None
        row = [label]
        for cname, spec, pol in CONFIGS:
            bands = [pb if s == 'eq' else (max(1, pb - 1), 4) if s == 'co4' else (max(1, pb - 2), 4) if s == 'c24'
                     else (max(1, pb - 2), 6) if s == 'c26' else max(1, pb - 1) for s in spec]
            w, s, cd = run(pb, lines, bands, pol)
            word = C.classify_sim(w, s)
            if base is None:
                base = word
            else:
                shifts[cname].append(WORDS.index(base) - WORDS.index(word))
            row.append("%-24s %-7s win %5.1f stag %5.1f compdown %5.1f" % (cname, word, w, s, cd))
        print(row[0])
        for r in row[1:]:
            print("   " + r)
    print()
    print("Word shift vs no companion (positive = gentler), per configuration:")
    for k, v in shifts.items():
        hist = {d: v.count(d) for d in sorted(set(v))}
        print("  %-24s %s   (mean %.2f)" % (k, hist, sum(v) / float(len(v)) if v else 0))
