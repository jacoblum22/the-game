"""
evidence03.py -- simulation of ch.03 evidence capture, weighting, saturation and recency.

Implements the rules of 03-tags-and-evidence.md exactly as written:
  * quality rung from base odds (circumstance excluded): Routine >= 70, Difficult 40..65, Challenging <= 35
  * points: quality 2/4/6; stakes safe 0 / risky 2 / dire 4; lethal +2; critical success +2;
    novelty +2; failure -> half (round down), Safe failure -> 0; secondary tags -> half (round down)
  * settlement at scene_end, per node (cascade to every ancestor), diminishing 1, 1/2, 1/4, 0 (sorted desc)
  * same target + same level-2 node already settled earlier the same day -> 0
  * recent = newest 12 evidence-bearing scenes full + scenes 13..24 halved (round down)
  * conduct: +-2 / +-4, DR per axis per sign per scene; strain += neg, -= floor(pos/2), floor 0
Scenarios A..H; prints tables used in the chapter (WE-03-S*, T-03-SIM).
Deterministic: seeded RNG.
"""
import random
from collections import defaultdict

# ---------- resolution (00.3.10 / 01.8, reference ladder) ----------
def degree(mod, dc, d20):
    total = d20 + mod
    m = total - dc
    if m >= 10: d = 3
    elif m >= 0: d = 2
    elif m > -10: d = 1
    else: d = 0
    if d20 == 20: d = min(3, d + 1)
    if d20 == 1: d = max(0, d - 1)
    near = (d == 1 and m >= -3)
    return d, near  # 3 cs, 2 s, 1 f, 0 cf

def odds(mod, dc):
    return sum(1 for f in range(1, 21) if degree(mod, dc, f)[0] >= 2) * 5

def quality(base_odds):
    if base_odds >= 70: return 'routine'
    if base_odds >= 40: return 'difficult'
    return 'challenging'

QPTS = {'routine': 2, 'difficult': 4, 'challenging': 6}
SPTS = {'safe': 0, 'risky': 2, 'dire': 4}
DC = {1: 10, 2: 15, 3: 20, 4: 25, 5: 30}

def ancestors(tag):
    parts = tag.split('.')
    return ['.'.join(parts[:i]) for i in range(len(parts), 0, -1)]

def lvl2(tag):
    p = tag.split('.')
    return '.'.join(p[:3]) if len(p) >= 3 else tag

DR = [1, 2, 4]  # divisors for 1st, 2nd, 3rd; 4th+ -> 0

class Engine:
    def __init__(self, dr=True, routine_cap=True):
        self.dr = dr
        self.routine_cap = routine_cap
        self.routine_day = defaultdict(set)   # day -> {node} that already counted a routine event
        self.pending = []
        self.settled = []          # (scene_idx, node, pts, event)
        self.node_scene_pts = defaultdict(lambda: defaultdict(int))  # node -> scene -> pts
        self.raw = defaultdict(int)
        self.weighted = defaultdict(int)
        self.ev_scenes = []        # ordered list of evidence-bearing scene idx
        self.targets_day = defaultdict(set)   # (day) -> {(target, lvl2)}
        self.contexts = defaultdict(list)     # lvl2 node -> [(scene_idx, ctx)]
        self.conduct = defaultdict(lambda: {'pos': 0, 'neg': 0, 'strain': 0})
        self.counted = defaultdict(int)
        self.by_quality = defaultdict(lambda: defaultdict(int))
        self.max_event = 0

    def base_points(self, e):
        if e.get('kind') == 'conduct':
            return e['pts']
        p = QPTS[e['quality']] + SPTS[e['stakes']]
        if e.get('lethal'): p += 2
        if e['degree'] == 3: p += 2
        if e.get('novel'): p += 2
        if e['degree'] <= 1:
            p = 0 if e['stakes'] == 'safe' else p // 2
        return p

    def record(self, e, scene_idx):
        e['scene'] = scene_idx
        if e.get('kind') != 'conduct':
            # novelty: ctx not seen on this lvl2 node within the recency window (24 ev-scenes)
            node2 = lvl2(e['tag'])
            window = set(self.ev_scenes[-24:])
            seen = {c for (s, c) in self.contexts[node2] if s in window}
            e['novel'] = e['ctx'] not in seen
        e['pts'] = self.base_points(e)
        self.max_event = max(self.max_event, e['pts'])
        self.pending.append(e)

    def settle_scene(self, scene_idx, day):
        contrib = defaultdict(list)  # node -> [(pts, e)]
        cond = defaultdict(list)     # (axis, sign) -> [pts]
        had_deed = False
        for e in self.pending:
            if e.get('kind') == 'conduct':
                cond[(e['axis'], e['sign'])].append(e['pts'])
                continue
            key = (e.get('target'), lvl2(e['tag']))
            if e.get('target') and key in self.targets_day[day] and not e.get('_same_scene_ok'):
                e['pts'] = 0
            tags = [(e['tag'], e['pts'])] + [(t, e['pts'] // 2) for t in e.get('secondary', [])]
            seen_nodes = set()
            for t, p in tags:
                if p <= 0: continue
                for a in ancestors(t):
                    if a in seen_nodes: continue   # one event credits a node once (best path)
                    seen_nodes.add(a)
                    contrib[a].append((p, e))
        # targets first touched this scene become day-capped for later scenes
        for e in self.pending:
            if e.get('kind') != 'conduct' and e.get('target'):
                self.targets_day[day].add((e['target'], lvl2(e['tag'])))
        for node, lst in contrib.items():
            lst.sort(key=lambda x: -x[0])
            if self.routine_cap:
                kept, used = [], node in self.routine_day[day]
                for p, e in lst:
                    if e['quality'] == 'routine':
                        if used: continue
                        used = True
                        self.routine_day[day].add(node)
                    kept.append((p, e))
                lst = kept
            tot = 0
            for i, (p, e) in enumerate(lst):
                if self.dr and i >= 3: break
                v = p // DR[i] if self.dr else p
                if v > 0:
                    tot += v
                    self.raw[node] += 1
            if tot > 0:
                had_deed = True
                self.weighted[node] += tot
                self.node_scene_pts[node][scene_idx] += tot
        for e in self.pending:
            if e.get('kind') != 'conduct' and e['pts'] > 0:
                self.contexts[lvl2(e['tag'])].append((scene_idx, e['ctx']))
                self.by_quality[lvl2(e['tag'])][e['quality']] += 1
        for (axis, sign), pts in cond.items():
            pts.sort(reverse=True)
            tot = sum(p // DR[i] for i, p in enumerate(pts[:3]))
            c = self.conduct[axis]
            if sign > 0:
                c['pos'] += tot; c['strain'] = max(0, c['strain'] - tot // 2)
            else:
                c['neg'] += tot; c['strain'] += tot
        if had_deed:
            self.ev_scenes.append(scene_idx)
        self.pending = []

    def recent(self, node):
        new = self.ev_scenes[-12:]
        old = self.ev_scenes[-24:-12]
        s_new = sum(self.node_scene_pts[node].get(s, 0) for s in new)
        s_old = sum(self.node_scene_pts[node].get(s, 0) for s in old)
        return s_new + s_old // 2

# ---------- play model ----------
class PC:
    def __init__(self, comp):
        self.comp = dict(comp)  # tag -> competence
        self.attr = {'agility': 3, 'might': 1, 'wits': 2, 'presence': 0, 'intellect': 0}
    def mod(self, tag, attr):
        best = 1
        for a in ancestors(tag):
            best = max(best, self.comp.get(a, 0))
        return self.attr[attr] + best

def make_beat(rng, pc, tag, attr, tier, stakes, lethal, target, ctx, secondary=(), lever=0, lenient=False):
    m = pc.mod(tag, attr)
    dc = DC[tier]
    bo = odds(m, dc)
    q = quality(bo)
    d20 = rng.randint(1, 20)
    d, near = degree(m + lever, dc, d20)
    if d == 1 and near and stakes != 'safe' and rng.random() < 0.6:
        d = 2   # success at cost taken counts as success (01.9.3)
    sec = list(secondary)
    return {'tag': tag, 'secondary': sec, 'quality': q, 'stakes': stakes, 'lethal': lethal,
            'degree': d, 'target': target, 'ctx': ctx}

def run(scenario, sessions=20, seed=7, scenes_per_session=5, verbose=False, dr=True, routine_cap=True, conflict_only=False):
    rng = random.Random(seed)
    eng = Engine(dr, routine_cap)
    pc = PC({'deed.martial.archery': 2, 'deed.wilds.tracking': 2})
    scene_idx = 0
    day = 0
    log = []
    tid = 0
    for s in range(1, sessions + 1):
        # competence growth assumed from 04 recognitions (illustrative): archery +3 at s6, +4 at s12
        if scenario in ('A', 'C', 'C2', 'E', 'E2', 'F'):
            if s == 6: pc.comp['deed.martial.archery'] = 3
            if s == 12: pc.comp['deed.martial.archery'] = 4
        if scenario == 'D' and s == 11:
            pc.comp['deed.arcane.fire'] = 2
        band = 1 if s <= 5 else (2 if s <= 12 else 3)
        for sc in range(scenes_per_session):
            scene_idx += 1
            if sc % 2 == 0: day += 1
            r = rng.random()
            beats = []
            if scenario == 'B':   # grinder: rats in the cellar, every scene, Risky (they bite), T1
                n = rng.randint(4, 6)
                for i in range(n):
                    tid += 1
                    beats.append(make_beat(rng, pc, 'deed.martial.archery.bow', 'agility', 1, 'risky', False,
                                           f'rat{tid}', 'creature.beast.vermin'))
            elif scenario in ('C', 'C2'):  # weapon switcher (C) vs same weapon (C2), identical fights: every attack a different weapon family
                fams = ['deed.martial.archery.bow', 'deed.martial.blade.dagger', 'deed.martial.thrown.javelin',
                        'deed.martial.bludgeon.club', 'deed.martial.polearm.spear', 'deed.martial.unarmed.striking']
                n = 6
                tier = band + 1
                for i in range(n):
                    tid += 1
                    beats.append(make_beat(rng, pc, fams[i] if scenario == 'C' else fams[0], 'agility', tier, 'risky', False, f'foe{tid}',
                                           'creature.folk.human'))
            else:
                focus = 'deed.martial.archery.bow'
                if scenario == 'D' and s > 10:
                    focus = 'deed.arcane.fire.blast'
                if conflict_only or r < 0.45:   # conflict
                    tier = rng.choice([band, band + 1, band + 1, band + 2])
                    tier = min(tier, 5)
                    stakes = 'dire' if rng.random() < 0.25 else 'risky'
                    lethal = stakes == 'dire' and rng.random() < 0.4
                    ctx = rng.choice(['creature.beast.predator', 'creature.folk.human', 'creature.folk.goblin',
                                      'creature.undead.mindless', 'creature.beast.monstrous'])
                    n = rng.randint(3, 6)
                    if rng.random() < 0.35:   # opens from hiding
                        tid += 1
                        # 03.1.7 rule 2: the shot is rolled against Guard, so the weapon (or spell) tag stays
                        # primary and guile.ambush.sniping is a secondary grounded by position
                        beats.append(make_beat(rng, pc, focus if scenario not in ('F',) else 'deed.martial.archery.bow',
                                               'agility' if 'arcane' not in focus else 'intellect', tier, stakes, lethal,
                                               f'foe{tid}', ctx, ['deed.guile.ambush.sniping']))
                    for i in range(n):
                        tid += 1 if i % 2 == 0 else 0
                        pick = rng.random()
                        if scenario == 'F':  # generalist
                            tag = rng.choice(['deed.martial.archery.bow', 'deed.martial.blade.sword',
                                              'deed.arcane.fire.blast', 'deed.divine.healing.mending',
                                              'deed.influence.intimidation.threat'])
                        elif scenario == 'G':  # hybrid archer + fire sorcery, some fused shots
                            tag = focus if pick < 0.5 else 'deed.arcane.fire.blast'
                        else:
                            tag = focus if pick < 0.75 else ('deed.martial.blade.dagger' if pick < 0.9
                                                             else 'deed.martial.athletics.acrobatics')
                        attr = 'agility' if 'arcane' not in tag else 'intellect'
                        sec = []
                        if scenario == 'G' and tag == focus and rng.random() < 0.3:
                            sec = ['deed.arcane.fire.blast']
                        if scenario == 'E':
                            sec = ['deed.martial.tactics.ground']
                        if scenario == 'E2' and rng.random() < 0.15:
                            sec = ['deed.martial.tactics.ground']   # lenient: secondary added to everything
                        beats.append(make_beat(rng, pc, tag, attr, tier, stakes, lethal, f'foe{tid}', ctx, sec))
                    # mercy: occasionally spare a yielding foe at a cost
                    if rng.random() < 0.15 or (scenario == 'E' and rng.random() < 0.3) or (scenario == 'E2' and rng.random() < 0.08):
                        beats.append({'kind': 'conduct', 'axis': 'conduct.mercy', 'sign': +1,
                                      'pts': 4 if stakes == 'dire' else 2})
                elif r < 0.70:  # stealth / exploration site
                    tier = rng.choice([band, band + 1, band + 1])
                    for i in range(rng.randint(2, 4)):
                        tid += 1
                        tag = rng.choice(['deed.guile.stealth.sneaking', 'deed.guile.stealth.sneaking',
                                          'deed.guile.stealth.infiltration', 'deed.guile.thievery.lockpicking',
                                          'deed.wilds.tracking.trailing'])
                        attr = 'agility' if 'tracking' not in tag else 'wits'
                        if tag == 'deed.guile.thievery.lockpicking' and 'deed.guile.thievery' not in pc.comp:
                            tag = 'deed.martial.athletics.climbing'
                        beats.append(make_beat(rng, pc, tag, attr, min(tier, 5), 'risky', False, f'obs{tid}',
                                               'situation.exploration.ruin'))
                elif r < 0.85:  # social
                    tid += 1
                    beats.append(make_beat(rng, pc, 'deed.influence.persuasion.argument', 'presence', band + 1,
                                           'risky', False, f'npc{tid}', 'situation.social.parley'))
                    if rng.random() < 0.2:
                        beats.append({'kind': 'conduct', 'axis': 'conduct.honesty', 'sign': +1, 'pts': 2})
                else:  # travel
                    tid += 1
                    beats.append(make_beat(rng, pc, 'deed.wilds.navigation.wayfinding', 'wits', band + 1, 'risky',
                                           False, f'route{tid}', 'situation.travel.overland'))
            if scenario == 'A' and s == 9 and sc == 2:
                beats.append({'kind': 'conduct', 'axis': 'conduct.mercy', 'sign': -1, 'pts': 4})  # killed a yielded foe
            for b in beats:
                eng.record(b, scene_idx)
            eng.settle_scene(scene_idx, day)
        log.append((s, {n: (eng.weighted[n], eng.recent(n), eng.raw[n]) for n in TRACK},
                    dict(eng.conduct['conduct.mercy'])))
    return eng, log

TRACK = ['deed', 'deed.martial', 'deed.martial.archery', 'deed.martial.archery.bow', 'deed.guile',
         'deed.guile.stealth', 'deed.wilds', 'deed.influence', 'deed.arcane', 'deed.arcane.fire',
         'deed.martial.blade', 'deed.martial.tactics']

def show(name, log, nodes, every=(1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20)):
    print(f"\n=== Scenario {name} ===")
    hdr = 'sess | ' + ' | '.join(f'{n.replace("deed.", "")[:18]:>18} w/rec' for n in nodes)
    print(hdr)
    for s, d, mercy in log:
        if s in every:
            row = ' | '.join(f'{d[n][0]:>12}/{d[n][1]:<5}' for n in nodes)
            print(f'{s:>4} | {row} | mercy {mercy}')

if __name__ == '__main__':
    import sys
    seeds = range(1, 201)
    # Scenario A, many seeds: distribution of per-session yields
    for scen in ['A','B','C','D','E','F','G']:
        eng, log = run(scen, seed=7)
        if scen == 'A':
            show('A focused archer-stealth (seed 7)', log, ['deed.martial.archery', 'deed.martial', 'deed.guile',
                                                           'deed.guile.stealth', 'deed'])
        elif scen == 'B':
            show('B rat grinder', log, ['deed.martial.archery', 'deed.martial', 'deed'])
        elif scen == 'C':
            show('C weapon switcher', log, ['deed.martial', 'deed.martial.archery', 'deed'])
        elif scen == 'D':
            show('D pivot to fire sorcery at session 11', log, ['deed.martial.archery', 'deed.arcane.fire',
                                                               'deed.martial', 'deed.arcane'])
        elif scen == 'E':
            show('E lenient DM (secondary tactics on every beat, extra mercy)', log,
                 ['deed.martial.archery', 'deed.martial.tactics', 'deed.martial'])
            print('   mercy', eng.conduct['conduct.mercy'])
        elif scen == 'F':
            show('F generalist', log, ['deed.martial', 'deed.arcane', 'deed.divine' if False else 'deed.influence',
                                       'deed.martial.archery'])
        elif scen == 'G':
            show('G hybrid archer + fire', log, ['deed.martial.archery', 'deed.arcane.fire', 'deed.martial',
                                                'deed.arcane'])
        print('   max single-event points:', eng.max_event)
    # Monte Carlo for A: per-session averages and percentiles at checkpoints
    print('\n=== Scenario A over 200 seeds: weighted at session N (p10 / median / p90) ===')
    import statistics
    res = defaultdict(lambda: defaultdict(list))
    rec = defaultdict(lambda: defaultdict(list))
    mercy = defaultdict(list)
    for sd in seeds:
        eng, log = run('A', seed=sd)
        for s, d, m in log:
            for n in TRACK:
                res[n][s].append(d[n][0]); rec[n][s].append(d[n][1])
            mercy[s].append(m['pos'] - m['neg'])
    def pct(v, p):
        v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]
    for n in ['deed.martial.archery', 'deed.martial', 'deed.guile', 'deed.guile.stealth', 'deed.wilds',
              'deed.influence', 'deed']:
        print(f'{n:<24}', '  '.join(f's{s}:{pct(res[n][s],.1)}/{int(statistics.median(res[n][s]))}/{pct(res[n][s],.9)}'
                                   for s in (1, 2, 3, 5, 10, 20)))
    print('recent (median) archery:', [int(statistics.median(rec['deed.martial.archery'][s])) for s in (1,2,3,5,10,15,20)])
    print('recent (median) martial:', [int(statistics.median(rec['deed.martial'][s])) for s in (1,2,3,5,10,15,20)])
    print('mercy net median by session:', [int(statistics.median(mercy[s])) for s in (1,3,5,10,20)])
    # Pivot Monte Carlo: when does arcane.fire recent exceed archery recent?
    cross = []
    for sd in seeds:
        eng, log = run('D', seed=sd)
        c = next((s for s, d, m in log if s > 10 and d['deed.arcane.fire'][1] > d['deed.martial.archery'][1]), None)
        cross.append(c if c else 99)
    print('pivot: session where recent(fire) > recent(archery): median', statistics.median(cross),
          'p10', pct(cross, .1), 'p90', pct(cross, .9))
    # Grinder vs focused: ratio at session 10
    g = [run('B', seed=sd)[0].weighted['deed.martial.archery'] for sd in range(1, 51)]
    a = [run('A', seed=sd)[0].weighted['deed.martial.archery'] for sd in range(1, 51)]
    print('archery weighted at s20, grinder median', statistics.median(g), 'focused median', statistics.median(a))
    gq = run('B', seed=3)[0].by_quality['deed.martial.archery']
    aq = run('A', seed=3)[0].by_quality['deed.martial.archery']
    print('quality mix grinder', dict(gq), 'focused', dict(aq))

    # --- extra measurements for the chapter ---
    def med(v): return statistics.median(v)
    sw = [run('C', seed=sd)[0].weighted['deed.martial'] for sd in range(1, 51)]
    sf = [run('C2', seed=sd)[0].weighted['deed.martial'] for sd in range(1, 51)]
    print('C weapon switcher martial s20 median', med(sw), ' C2 same fights one weapon', med(sf))
    g_nodr = [run('B', seed=sd, dr=False, routine_cap=False)[0].weighted['deed.martial.archery'] for sd in range(1, 51)]
    g_dr_only = [run('B', seed=sd, routine_cap=False)[0].weighted['deed.martial.archery'] for sd in range(1, 51)]
    a_nodr = [run('A', seed=sd, dr=False, routine_cap=False)[0].weighted['deed.martial.archery'] for sd in range(1, 51)]
    print('grinder archery s20: no DR/no cap', med(g_nodr), ' DR only', med(g_dr_only), ' DR+routine cap', med(g))
    print('focused archery s20: no DR/no cap', med(a_nodr), ' full rules', med(a))
    fc = [run('A', seed=sd, conflict_only=True)[0].weighted['deed.martial.archery'] for sd in range(1, 51)]
    print('focused but conflict every scene (same scene count as grinder): archery s20', med(fc))
    for scen in ('E', 'E2'):
        tt = [run(scen, seed=sd)[0] for sd in range(1, 51)]
        print(scen, 'tactics s20 median', med([e.weighted['deed.martial.tactics'] for e in tt]),
              'archery', med([e.weighted['deed.martial.archery'] for e in tt]),
              'mercy pos', med([e.conduct['conduct.mercy']['pos'] for e in tt]))
    base = [run('A', seed=sd)[0] for sd in range(1, 51)]
    print('A (honest) tactics s20 median', med([e.weighted['deed.martial.tactics'] for e in base]),
          'mercy pos', med([e.conduct['conduct.mercy']['pos'] for e in base]))
    # per-session yield of the focus node (s2..s20 slope)
    sl = [(run('A', seed=sd)[0].weighted['deed.martial.archery']) / 20 for sd in range(1, 51)]
    print('archery points per session (mean over 20 sessions) median', med(sl))
    # quality mix focused, median shares
    qs = defaultdict(list)
    for e in base:
        q = e.by_quality['deed.martial.archery']
        for k in ('routine', 'difficult', 'challenging'): qs[k].append(q.get(k, 0))
    print('focused archery event counts by quality (median over 50 seeds):', {k: med(v) for k, v in qs.items()})
