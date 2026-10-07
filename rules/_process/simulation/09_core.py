#!/usr/bin/env python3
"""09_core.py -- chapter 09's shared arithmetic: exact d20 enumeration, the threat-band stat lines,
the Expected Harm Ratio (EHR) behind threat_advisory (09.6), and an extended Monte-Carlo fight model.

The fight model is chapter 06's `06-conflict-sim.py` (imported, not copied: its degree(), harm(), PC
lines, morale clock, mob numbers step and windups are used as-is) extended with the rules 06 states but
its script leaves out, and with chapter 09's variants:
  * adversary Fend at T3+ (06.6.5): -2 on the PC's first attack against it each round;
  * elite and solo variants (09.4): Vitality multiplier, reaction by variant, solo Shrug (ends one
    control condition once per conflict: modelled as nothing, since the baseline PC applies none) and
    the solo heavy blow (base +1 rung, wound up the turn before: 06.9.5);
  * swarms (06.10.5): unshaped attacks one rung lighter against them; they attack up to 4 targets
    (the PC alone here, so one roll) -- modelled through the template's numbers.
Seeded; deterministic. Imported by 09-adversary-sim.py and 09-gen_data09.py.
"""
import importlib.util
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("sim06", os.path.join(HERE, "06-conflict-sim.py"))
sim06 = importlib.util.module_from_spec(_spec)
_argv = sys.argv
sys.argv = [sys.argv[0]]
_spec.loader.exec_module(sim06)
sys.argv = _argv

HARM = sim06.HARM                      # {0:0, 1:1, 2:3, 3:5, 4:8, 5:12}
REP = sim06.REP                        # [0, -2, -4]
degree = sim06.degree
harm = sim06.harm
PC_REF = sim06.PC                      # T-06-12 PC reference lines, band 1..5

# ------------------------------------------------------------------ 09.3: the band tables
BAND_COMP = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}            # c_b: competence on an adversary's trained tags
RUNG = {                                               # attribute modifier by rung and band (T-09-2)
    'apex':   {1: 3, 2: 5, 3: 6, 4: 8, 5: 9},
    'high':   {1: 1, 2: 3, 3: 4, 4: 6, 5: 7},
    'mid':    {1: 0, 2: 1, 3: 2, 4: 3, 5: 4},
    'low':    {1: -1, 2: -1, 3: 0, 4: 1, 5: 1},
    'feeble': {1: -3, 2: -3, 3: -2, 4: -2, 5: -2},
    'none':   {1: -5, 2: -5, 3: -5, 4: -5, 5: -5},
}
# The standard line per band (T-09-3). Attack and Guard follow from RUNG['high'] + c_b; Vitality is the
# calibrated value (09-adversary-sim.py section A); harm, heavy blow, reduction, nerve, tempo as 06's
# T-06-12 reference lines, which this chapter adopts.
STANDARD = {
    1: dict(atk=2, guard=12, vit=5, sev=2, red=0, morale=4, tempo=10, heavy=None, fend=False),
    2: dict(atk=5, guard=15, vit=12, sev=2, red=0, morale=6, tempo=11, heavy=None, fend=False),
    3: dict(atk=7, guard=17, vit=18, sev=3, red=1, morale=6, tempo=12, heavy=None, fend=True),
    4: dict(atk=10, guard=20, vit=24, sev=3, red=2, morale=8, tempo=13, heavy=4, fend=True),
    5: dict(atk=12, guard=22, vit=36, sev=4, red=2, morale=8, tempo=14, heavy=5, fend=True),
}
ENVELOPE_VIT = {1: (2, 5), 2: (6, 12), 3: (12, 20), 4: (20, 32), 5: (32, 60)}
VARIANT_VIT = {'minion': 0.5, 'standard': 1.0, 'elite': 2.0, 'solo': 3.0}


def dist(mod, dc):
    """Exact degree distribution of d20 + mod vs dc (00.3.10; 01.8.1): returns [p_cf, p_f, p_s, p_cs]."""
    out = [0.0, 0.0, 0.0, 0.0]
    for d in range(1, 21):
        m = d + mod - dc
        g = 3 if m >= 10 else 2 if m >= 0 else 1 if m > -10 else 0
        if d == 20:
            g = min(3, g + 1)
        if d == 1:
            g = max(0, g - 1)
        out[g] += 0.05
    return out


def exp_harm(mod, dc, sev, red, step=0):
    """Expected harm of one aimed attack: success = sev+step, critical = one rung heavier, minus reduction."""
    p = dist(mod, dc)
    s = max(1, min(5, sev + step))
    c = max(1, min(5, sev + step + 1))
    return p[2] * max(0, HARM[s] - red) + p[3] * max(0, HARM[c] - red)


def numbers_step(members_now):
    return 2 if members_now >= 6 else 1 if members_now >= 3 else 0


# ------------------------------------------------------------------ 09.6: threat_advisory's estimator
import math


def moments(mod, dc, sev, red, step=0, factor=1.0):
    """(mean harm, variance of harm, chance to hit) of one aimed attack (exact d20 enumeration); factor is
    a resistance multiplier applied per outcome and rounded down (00.10.4 E5, E7)."""
    p = dist(mod, dc)
    s = max(1, min(5, sev + step))
    c = max(1, min(5, sev + step + 1))
    hs = int(max(0, HARM[s] - red) * factor)
    hc = int(max(0, HARM[c] - red) * factor)
    m = p[2] * hs + p[3] * hc
    m2 = p[2] * hs * hs + p[3] * hc * hc
    return m, m2 - m * m, p[2] + p[3]


def foe_rate(f, pc, pc_fends, members_now):
    """Per-round (mean, variance) of harm one adversary deals the PC: two attack actions at 0/-2, the
    PC's Fend (-2) on the first when it is this foe's; a heavy blow on alternate turns (windup, blow:
    06.9.5); a mob's numbers step at its current members (06.10.3)."""
    step = numbers_step(members_now) if f.get('members', 1) > 1 else 0
    fe = 2 if pc_fends else 0
    a = moments(f['atk'] - fe, pc['guard'], f['sev'], pc['armor'], step)
    b = moments(f['atk'] - 2, pc['guard'], f['sev'], pc['armor'], step)
    if f.get('heavy'):
        h = moments(f['atk'] - fe, pc['guard'], f['heavy'], pc['armor'], step)
        return (a[0] + h[0] + b[0]) / 2.0, (a[1] + h[1] + b[1]) / 2.0
    return a[0] + b[0], a[1] + b[1]


def pc_rate(pc, f, lose_third=0.0):
    """Per-round (mean, variance) of harm the PC deals one adversary: three Strikes at 0/-2/-4, the
    adversary's Fend on the first if it has Fend, its reduction; a swarm takes unshaped harm one rung
    lighter (06.10.5). lose_third [revision: I-090]: the share of rounds the PC spends its third action
    ending a lingering-harm condition (its best answer, 09-lingering-rider.py)."""
    m = v = 0.0
    for k in range(3):
        mod = pc['atk'] + REP[k] - (2 if (k == 0 and f.get('fend')) else 0)
        x = moments(mod, f['guard'], pc['sev'], f['red'], -1 if f.get('swarm') else 0, f.get('taken', 1.0))
        w = (1.0 - lose_third) if k == 2 else 1.0
        m += x[0] * w
        v += x[1] * w
    if f.get('regen'):                       # regeneration offsets harm each round, never below a tenth
        m = max(m * 0.1, m - f['regen'])
    return m, v


def p_before(foe_tempo, pc_tempo_mod):
    """Chance this foe acts before the PC (06.2.2: its tempo DC exceeds the PC's total; a natural 20
    puts the PC first)."""
    return sum(1 for d in range(1, 20) if d + pc_tempo_mod < foe_tempo) / 20.0


def Phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


# [revision: I-090] the lost action is worth 0.6 of the third Strike (actions are partly spent on moving to a new target
# anyway); 0.6 matches 09-lingering-rider.py's simulated win shift (P4 -12.0 vs -12.3, P5 -13.5 vs -14.2) and its premium
LING_K = 0.6


def estimate(pc, foes, buffer_hits=1.75, stagger_margin=0.5):
    """PR-09-4: the advisory estimator. Returns (win%, Staggered%, harm ratio). Deterministic.
    pc: dict(atk, guard, vit (CURRENT), armor, sev, tempo, fend)
    foes: list of dicts with atk, guard, vit (per member), sev, red, heavy, fend, morale (None =
    fearless), tempo, members, leader, swarm."""
    n = len(foes)
    # (0) [revision: I-090] a lingering-harm rider (burning, bleeding: f['ling']) costs the PC one action in
    #     each round one of its attacks landed: the PC's best answer is to end it at once (09-lingering-rider.py)
    miss = 1.0
    for f in foes:
        if f.get('ling'):
            for k in (0, 1):
                miss *= 1.0 - moments(f['atk'] + REP[k], pc['guard'], f['sev'], pc['armor'])[2]
    lose = LING_K * (1.0 - miss)
    # (1) the PC's Fend goes to the adversary with the highest per-round harm
    raw = [foe_rate(f, pc, False, f.get('members', 1))[0] for f in foes]
    fend_i = max(range(n), key=lambda i: raw[i]) if pc.get('fend', True) else -1
    # (2) kill order and timeline: lowest total Vitality first (06's PC policy)
    order = sorted(range(n), key=lambda i: foes[i]['vit'] * foes[i].get('members', 1))
    t = 0.0
    segs = []
    events = []
    total = sum(f['vit'] * f.get('members', 1) for f in foes)
    removed = 0.0
    half = quarter = None
    var_t = 0.0
    for i in order:
        f = foes[i]
        m = f.get('members', 1)
        o, ov = pc_rate(pc, f, lose)
        per = f['vit'] / o if o > 0 else 1e9
        for j in range(m, 0, -1):
            s0 = t
            t += per
            segs.append((s0, t, i, j))
            before = removed
            removed += f['vit']
            var_t += f['vit'] * ov / o ** 3 if o > 0 else 0.0
            if m == 1:
                events.append((s0 + per / 2.0, 1))                       # first bloodied
            events.append((t, 2 if (f.get('leader') and j == 1) else 1))  # a member defeated
            # strength thresholds fall inside the segment, where the harm crosses them
            if half is None and removed * 2 >= total:
                half = s0 + per * max(0.0, (total / 2.0 - before)) / f['vit']
            if quarter is None and removed * 4 >= 3 * total:
                quarter = s0 + per * max(0.0, (total * 3 / 4.0 - before)) / f['vit']
    if half is not None:
        events.append((half, 2))
    if quarter is not None:
        events.append((quarter, 2))
    # (3) the morale clock (06.11): the side breaks when the ticks reach its nerve; fearless never
    nerves = [f['morale'] for f in foes if f.get('morale')]
    break_t = 1e9
    if nerves and len(nerves) == n:
        nerve = max(nerves)
        fill = 0
        for tm, k in sorted(events):
            fill += k
            if fill >= nerve:
                break_t = tm
                break
    end = min(t, break_t)
    # (4) harm taken: every adversary deals its rate from 0 until it falls (a mob at full numbers until
    #     its first member falls), truncated at the break; plus its tempo edge
    H = V = 0.0
    for i, f in enumerate(foes):
        mine = [(s0, e0, j) for (s0, e0, k, j) in segs if k == i]
        first = min(s0 for s0, e0, j in mine)
        for s0, e0, j in [(0.0, first, f.get('members', 1))] + mine:
            if s0 >= end:
                continue
            e2 = min(e0, end)
            d, dv = foe_rate(f, pc, i == fend_i, j)
            H += d * (e2 - s0)
            V += dv * (e2 - s0)
        pb = p_before(f['tempo'], pc['tempo'])
        d, dv = foe_rate(f, pc, i == fend_i, f.get('members', 1))
        H += d * (pb - 0.5)
        V += dv * max(0.0, pb - 0.5)
    H = max(0.0, H)
    rate = H / end if end > 0 else 0.0
    V += rate ** 2 * var_t * min(1.0, end / t if t > 0 else 1.0)
    # (5) the mean harm of one landed blow (for the margin past Staggered)
    hits = []
    for f in foes:
        mh, _, ph = moments(f['atk'], pc['guard'], f['sev'], pc['armor'])
        if ph > 0:
            hits.append(mh / ph)
    hbar = sum(hits) / len(hits) if hits else 0.0
    sd = math.sqrt(max(V, 1e-9))
    vit = pc['vit']
    # calibration constants (09-estimator-tune.py: the setting with the most exact words whose gentler
    # misses do not outnumber its harsher ones): Staggered tested at Vitality - 1 (a half-point of
    # continuity and a half-point of margin); beaten at 1.75 landed blows past Staggered
    p_stag = 1.0 - Phi((vit - 0.5 - stagger_margin - H) / sd)
    p_lose = 1.0 - Phi((vit + buffer_hits * hbar - 0.5 - H) / sd)
    return 100.0 * (1.0 - p_lose), 100.0 * p_stag, H / max(1, vit)


WORDS = ['trivial', 'easy', 'fair', 'hard', 'lethal']


def classify_sim(win, stag):
    """06's T-06-13 word thresholds on simulated outcomes."""
    if win >= 99 and stag <= 3:
        return 'trivial'
    if win >= 95 and stag <= 15:
        return 'easy'
    if win >= 80 and stag <= 50:
        return 'fair'
    if win >= 40:
        return 'hard'
    return 'lethal'


# ------------------------------------------------------------------ the extended fight (Monte Carlo)
class Foe(sim06.Foe):
    def __init__(s, line, members=1, leader=False):
        band = line.get('band', 1)
        over = dict(line)
        sim06.Foe.__init__(s, band, members=members, leader=leader,
                           over={k: over[k] for k in ('atk', 'guard', 'vit', 'sev', 'red', 'morale', 'tempo', 'heavy')})
        s.fend = bool(line.get('fend'))
        s.swarm = bool(line.get('swarm'))
        s.fearless = line.get('morale') is None
        s.react_used = False
        s.taken = line.get('taken', 1.0)
        s.regen = line.get('regen', 0)


def fight(rng, pc, foes, use_focus=False, fend=True):
    """06's fight() with adversary Fend, swarm harm and fearless members; PC policy unchanged."""
    p = dict(pc)
    guard = p['guard']
    armor = p['armor']
    st = dict(vit=p['vit'], focus=p.get('focus', 0) if use_focus else 0, staggered=False, extra=0, lost=0,
              fend=True)
    sev = p['sev']
    nerves = [f.morale for f in foes if not f.fearless]
    mor = sim06.Morale(max(nerves) if nerves and len(nerves) == len(foes) else None, foes)
    t = rng.randint(1, 20) + p['tempo']
    before = [f for f in foes if f.tempo > t]
    after = [f for f in foes if f.tempo <= t]

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
            mod = p['atk'] + REP[min(k, 2)]
            if tgt.fend and not tgt.react_used:
                mod -= 2
                tgt.react_used = True
            deg = degree(rng, mod, tgt.guard)
            if deg >= 2:
                h = harm(sev, steps + (1 if deg == 3 else 0) - (1 if tgt.swarm else 0), 0, tgt.red)
                if tgt.taken < 1.0:
                    h = int(h * tgt.taken)              # resistance: x1/2 rounded down (00.10.4 E5/E7)
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

    def foe_turn(f):
        if not f.alive or mor.broken and not f.fearless:
            return
        f.react_used = False
        if f.regen and f.alive:
            f.vit = min(f.maxvit, f.vit + f.regen)      # pow.regenerate at its turn start
        acts = 2
        k = 0
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
                h = harm(s, f.numbers_step() + (1 if deg == 3 else 0), 0, armor)
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
        if mor.broken and all(f.fearless is False or not f.alive for f in foes):
            break
        if not any(f.alive for f in foes):
            break
        for f in after:
            foe_turn(f)
        if st['extra'] >= 2:
            break
    over = (mor.broken and not any(f.alive and f.fearless for f in foes)) or not any(f.alive for f in foes)
    won = over and st['extra'] < 2
    return dict(won=won, staggered=st['staggered'], dying=st['extra'] >= 2, rounds=rounds,
                lost=min(st['lost'], p['vit']))


def simulate(pc, mk, runs=4000, seed=909, **kw):
    rng = random.Random(seed)
    res = [fight(rng, pc, mk(), **kw) for _ in range(runs)]
    n = float(len(res))
    win = 100.0 * sum(r['won'] for r in res) / n
    stag = 100.0 * sum(r['staggered'] for r in res) / n
    rnd = sum(r['rounds'] for r in res) / n
    lost = sum(r['lost'] for r in res) / n
    return win, stag, rnd, lost


def pc_line(band, **over):
    p = dict(PC_REF[band])
    p.update(over)
    return p


def std(band, **over):
    d = dict(STANDARD[band])
    d['band'] = band
    d.update(over)
    return d
