"""
recog04.py -- calibration simulation for ch.04 (Recognition and Growth).

Builds on ch.03's evidence model (03-evidence03.py): the same resolution, quality, points, settlement
(diminishing returns per node per scene, routine cap, same-target cap) and recency rules, extended with
what 04 reads through 03.9: detail() (by_quality, distinct scenes, crises, peaks, peak_band, contexts),
counted() (cnt.defeat, cnt.focus, cnt.progress, with per-scene saturation), cooccurrence(), share().

On top of it: ch.04's rules exactly as written in 04-recognition-and-growth.md --
  * requirement sets per tier (04.3): weighted W, counted C, quality floor Q, scenes floor S, and the
    "since last crystallization" kinds (peak band, crises, contexts);
  * confidence = number of the five confirmations C1..C5 that hold (04.4.2);
  * policy: grant / offer / abstain (04.4.3);
  * the tier ladder's competence values fed back into the character's modifiers (04.5.2);
  * power_band from tiers (04.5.6), which sets the opposition the play model generates;
  * hybrids (04.2.4), lineage exclusion and the three-seat cap (04.8).
Player policy in the simulation: accept every offer at once (to measure pacing), unless noted.
Deterministic: seeded RNG. Python 3, standard library only.
"""
import random, statistics, sys
from collections import defaultdict

# ---------------------------------------------------------------- resolution (00.3.10 / 01.8)
def degree(mod, dc, d20):
    m = d20 + mod - dc
    d = 3 if m >= 10 else 2 if m >= 0 else 1 if m > -10 else 0
    if d20 == 20: d = min(3, d + 1)
    if d20 == 1: d = max(0, d - 1)
    return d, (d == 1 and m >= -3)

def odds(mod, dc):
    return sum(1 for f in range(1, 21) if degree(mod, dc, f)[0] >= 2) * 5

def quality(bo):
    return 'routine' if bo >= 70 else 'difficult' if bo >= 40 else 'challenging'

QPTS = {'routine': 2, 'difficult': 4, 'challenging': 6}
SPTS = {'safe': 0, 'risky': 2, 'dire': 4}
DC = {1: 10, 2: 15, 3: 20, 4: 25, 5: 30}
DRV = [1, 2, 4]

def band_of_dc(dc):
    return 1 if dc <= 12 else 2 if dc <= 17 else 3 if dc <= 22 else 4 if dc <= 27 else 5

def ancestors(tag):
    p = tag.split('.')
    return ['.'.join(p[:i]) for i in range(len(p), 0, -1)]

def lvl(tag): return len(tag.split('.')) - 1
def lvl2(tag):
    p = tag.split('.'); return '.'.join(p[:3]) if len(p) >= 3 else tag
def branch(tag):
    p = tag.split('.'); return '.'.join(p[:2]) if len(p) >= 2 else tag

# ---------------------------------------------------------------- 03 engine, extended with detail()/counted()
class Engine:
    def __init__(self):
        self.routine_day = defaultdict(set)
        self.pending = []; self.pending_counted = []
        self.node_scene_pts = defaultdict(lambda: defaultdict(int))
        self.weighted = defaultdict(int); self.raw = defaultdict(int)
        self.ev_scenes = []
        self.targets_day = defaultdict(set)
        self.contexts = defaultdict(list)
        self.q = defaultdict(lambda: defaultdict(int))          # node -> quality -> count (settled > 0)
        self.scenes = defaultdict(set)                           # node -> {scene}
        self.log = defaultdict(list)                             # node -> [(scene, band, success, crisis, peak, ctx, quality)]
        self.counted = defaultdict(int)                          # node -> units
        self.counted_scene = defaultdict(lambda: defaultdict(int))

    def points(self, e):
        p = QPTS[e['quality']] + SPTS[e['stakes']]
        if e.get('lethal'): p += 2
        if e['degree'] == 3: p += 2
        if e.get('novel'): p += 2
        if e['degree'] <= 1: p = 0 if e['stakes'] == 'safe' else p // 2
        return p

    def record(self, e, scene):
        node2 = lvl2(e['tag'])
        window = set(self.ev_scenes[-24:])
        seen = {c for (s, c) in self.contexts[node2] if s in window}
        e['novel'] = e['ctx'] not in seen
        e['pts'] = self.points(e); e['scene'] = scene
        self.pending.append(e)

    def count(self, counter, tag, units, scene):
        self.pending_counted.append((counter, tag, units))

    def settle(self, scene, day):
        contrib = defaultdict(list); had = False
        for e in self.pending:
            key = (e.get('target'), lvl2(e['tag']))
            if e.get('target') and key in self.targets_day[day]: e['pts'] = 0
            tags = [(e['tag'], e['pts'])] + [(t, e['pts'] // 2) for t in e.get('secondary', [])]
            seen = set()
            for t, p in tags:
                if p <= 0: continue
                for a in ancestors(t):
                    if a in seen: continue
                    seen.add(a); contrib[a].append((p, e))
        for e in self.pending:
            if e.get('target'): self.targets_day[day].add((e['target'], lvl2(e['tag'])))
        for node, lst in contrib.items():
            lst.sort(key=lambda x: -x[0])
            kept, used = [], node in self.routine_day[day]
            for p, e in lst:
                if e['quality'] == 'routine':
                    if used: continue
                    used = True; self.routine_day[day].add(node)
                kept.append((p, e))
            tot = 0
            for i, (p, e) in enumerate(kept[:3]):
                v = p // DRV[i]
                if v > 0:
                    tot += v; self.raw[node] += 1
                    self.q[node][e['quality']] += 1
                    self.log[node].append((scene, e['band'], e['degree'] >= 2, e['crisis'], e['peak'], e['ctx'], e['quality']))
            if tot > 0:
                had = True
                self.weighted[node] += tot; self.node_scene_pts[node][scene] += tot
                self.scenes[node].add(scene)
        for e in self.pending:
            if e['pts'] > 0: self.contexts[lvl2(e['tag'])].append((scene, e['ctx']))
        # counted: per counter per node, 1, 1/2, 1/4, 0
        cn = defaultdict(list)
        for counter, tag, units in self.pending_counted:
            for a in ancestors(tag): cn[(counter, a)].append(units)
        for (counter, node), us in cn.items():
            us.sort(reverse=True)
            tot = sum(u // DRV[i] for i, u in enumerate(us[:3]))
            self.counted[node] += tot; self.counted_scene[node][scene] += tot
        if had: self.ev_scenes.append(scene)
        self.pending = []; self.pending_counted = []

    def recent(self, node):
        new, old = self.ev_scenes[-12:], self.ev_scenes[-24:-12]
        return sum(self.node_scene_pts[node].get(s, 0) for s in new) + \
               sum(self.node_scene_pts[node].get(s, 0) for s in old) // 2

    def ev_since(self, scene):   # evidence-bearing scenes after a scene index
        return sum(1 for s in self.ev_scenes if s > scene)

    def detail(self, node, since=0):
        rows = [r for r in self.log[node] if r[0] > since]
        succ = [r for r in rows if r[2]]
        return {'dc_events': sum(1 for r in rows if r[6] != 'routine'),
                'challenging': sum(1 for r in rows if r[6] == 'challenging'),
                'routine': sum(1 for r in rows if r[6] == 'routine'),
                'raw': len(rows),
                'scenes': len({r[0] for r in rows}),
                'crises': sum(1 for r in rows if r[3]),
                'peaks': sum(1 for r in rows if r[4]),
                'peak_band': max([r[1] for r in succ], default=0),
                'by_band': [sum(1 for r in rows if r[1] == b) for b in range(1, 6)],
                'succ_by_band': [sum(1 for r in succ if r[1] == b) for b in range(1, 6)],
                'contexts': len({r[5] for r in rows})}

# ---------------------------------------------------------------- ch.04 data (mirrors data/callings.yaml#ladders)
W   = {'narrow': [80, 200, 440, 800, 1300], 'fine': [60, 150, 330, 600, 975],
       'broad': [120, 300, 660, 1200, 1950], 'hybrid': [60, 150, 330, 600, 975]}   # hybrid: min of the two branches
C   = {k: [v // 10 for v in vs] for k, vs in W.items()}
COMP = {'narrow': [3, 4, 5, 5, 6], 'fine': [3, 4, 5, 5, 6], 'broad': [2, 3, 4, 4, 5], 'hybrid': [2, 3, 4, 4, 5]}
BAND = {'narrow': [1, 2, 3, 4, 5], 'fine': [1, 2, 3, 4, 5], 'broad': [1, 2, 3, 4, 4], 'hybrid': [1, 2, 3, 4, 4]}
Q1, S1 = 6, 5                                 # tier 1: difficult-or-better events, distinct scenes
# since the last crystallization: difficult-or-better events, distinct scenes, GREAT DEEDS (settled deeds at
# challenge band >= the tier being entered, at least one of them a success), crises, distinct contexts
SINCE = {2: dict(dc=10, scenes=8, great=5, crises=0, contexts=0),
         3: dict(dc=14, scenes=10, great=6, crises=2, contexts=0),
         4: dict(dc=18, scenes=12, great=6, crises=3, contexts=5),
         5: dict(dc=22, scenes=14, great=4, crises=4, contexts=5)}
HYBRID_BALANCE = (2, 5); HYBRID_JOINT = 5; HYBRID_RECENT_MIN = 15
BROAD_SHARE_CAP = (2, 3); BROAD_CHILD_MIN = 30; BROAD_CHILDREN = 3
R_CONFIRM = 24
FINE_KEYS = {'deed.guile.thievery.lockpicking', 'deed.martial.blade.fencing', 'deed.wilds.foraging.herbs'}
SEATS = 3

def kind_of(key):
    return 'broad' if lvl(key) == 1 else 'narrow' if lvl(key) == 2 else 'fine'

class Char:
    def __init__(self, comp, attr):
        self.comp = dict(comp); self.attr = dict(attr)
        self.callings = {}        # key -> dict(tier, kind, at_scene, policy)
        self.declined = set()
        self.history = []         # (session, key, tier, policy, confidence)
        self.attr_bumped = False
    def mod(self, tag, attr):
        best = 1
        for a in ancestors(tag): best = max(best, self.comp.get(a, 0))
        return self.attr[attr] + best
    def power_band(self):
        b = 1
        for k, c in self.callings.items(): b = max(b, BAND[c['kind']][c['tier'] - 1])
        return b

def children_l2(eng, br):
    return {n: w for n, w in eng.weighted.items() if lvl(n) == 2 and n.startswith(br + '.')}

def eligible(eng, ch, key, tier, since_scene, kind=None):
    kind = kind or kind_of(key)
    if eng.weighted[key] < W[kind][tier - 1]: return False
    if eng.counted[key] < C[kind][tier - 1]: return False
    if tier == 1:
        d = eng.detail(key)
        if d['dc_events'] < Q1 or d['scenes'] < S1: return False
        if kind == 'broad':
            kids = children_l2(eng, key)
            if sum(1 for w in kids.values() if w >= BROAD_CHILD_MIN) < BROAD_CHILDREN: return False
            top = max(kids.values(), default=0)
            if BROAD_SHARE_CAP[1] * top > BROAD_SHARE_CAP[0] * eng.weighted[key]: return False
        return True
    d = eng.detail(key, since=since_scene); r = SINCE[tier]
    return (d['dc_events'] >= r['dc'] and d['scenes'] >= r['scenes'] and great(d, tier, r['great'])
            and d['crises'] >= r['crises'] and d['contexts'] >= r['contexts'])

def great(d, tier, n):
    return sum(d['by_band'][tier - 1:]) >= n and sum(d['succ_by_band'][tier - 1:]) >= 1

def hybrid_eligible(eng, a, b, tier, since_scene):
    wa, wb = eng.weighted[a], eng.weighted[b]; mn, mx = min(wa, wb), max(wa, wb)
    if mn < W['hybrid'][tier - 1]: return False
    if HYBRID_BALANCE[1] * mn < HYBRID_BALANCE[0] * mx: return False
    if min(eng.counted[a], eng.counted[b]) < C['hybrid'][tier - 1]: return False
    joint = len(eng.scenes[a] & eng.scenes[b])
    if joint < HYBRID_JOINT: return False
    if tier == 1 and min(eng.recent(a), eng.recent(b)) < HYBRID_RECENT_MIN: return False
    if tier == 1:
        return all(eng.detail(x)['dc_events'] >= 4 and eng.detail(x)['scenes'] >= 4 for x in (a, b))
    r = SINCE[tier]
    da, db = eng.detail(a, since_scene), eng.detail(b, since_scene)
    both = {k: [x + y for x, y in zip(da[k], db[k])] for k in ('by_band', 'succ_by_band')}
    return (da['dc_events'] + db['dc_events'] >= r['dc'] and min(da['scenes'], db['scenes']) >= r['scenes'] // 2
            and great(both, tier, r['great']) and min(sum(da['by_band'][tier - 1:]), sum(db['by_band'][tier - 1:])) >= 1
            and da['crises'] + db['crises'] >= r['crises'] and da['contexts'] + db['contexts'] >= r['contexts'])

def confidence(eng, key, tier, kind):
    """04.4.2: the number of the five confirmations K1..K5 that hold (0..5), and the currency floor."""
    w = eng.weighted[key]; rec = eng.recent(key); w1 = W[kind][0]
    k1 = 2 * rec >= w1                                   # Current: recent >= half the tier-1 weight
    k2 = 2 * rec >= w                                    # Rising: at least half of all the evidence is recent
    k3 = 5 * w >= eng.weighted['deed']                   # Central: the key holds >= 1/5 of the character's deed weight
    peers = sorted((v for n, v in eng.weighted.items() if lvl(n) == lvl(key)), reverse=True)
    k4 = len(peers) < 3 or w >= peers[2]                 # Leading: among the top three nodes at its level
    k5 = 4 * w >= 5 * W[kind][tier - 1]                  # Margin: a quarter past the line
    current = 4 * rec >= w1                              # the currency floor (stale candidates abstain)
    return sum((k1, k2, k3, k4, k5)), current

def recognition_pass(eng, ch, session, scene, keys, hybrids, accept=True, allow_broad=True):
    """one reflection: evaluate candidates keyed on the listed nodes; returns list of events"""
    out = []
    # tier-ups first
    for key, cal in list(ch.callings.items()):
        if cal['tier'] >= 5: continue
        t = cal['tier'] + 1
        ok = (hybrid_eligible(eng, *key, t, cal['at_scene']) if cal['kind'] == 'hybrid'
              else eligible(eng, ch, key, t, cal['at_scene'], cal['kind']))
        if ok and accept:
            cal['tier'] = t; cal['at_scene'] = scene
            apply_comp(ch, key, cal)
            ch.history.append((session, key, t, 'offer', None)); out.append((key, t, 'offer'))
    # new candidates
    cands = []
    for key in keys:
        if key in ch.callings or key in ch.declined: continue
        if not allow_broad and lvl(key) == 1: continue
        if any(not isinstance(k, tuple) and (k.startswith(key + '.') or key.startswith(k + '.')) for k in ch.callings):
            continue   # lineage: an ancestor or descendant key is held -> a fork, not a new seat (04.8.3)
        if eligible(eng, ch, key, 1, 0): cands.append(key)
    hcands = []
    for (a, b) in hybrids:
        if (a, b) in ch.callings or (a, b) in ch.declined: continue
        if hybrid_eligible(eng, a, b, 1, 0): hcands.append((a, b))
    for key in cands:
        # C5 clear field: no eligible sibling, ancestor/descendant, or hybrid touching its branch this pass
        rivals = [k for k in cands if k != key and (branch(k) == branch(key))]
        hyb = [h for h in hcands if branch(key) in h]
        clear = not rivals and not hyb
        conf, current = confidence(eng, key, 1, kind_of(key))
        policy = 'abstain' if (conf == 0 or not current) else 'grant' if (conf >= 4 and clear and lvl(key) >= 2) else 'offer'
        if len(ch.callings) >= SEATS and policy != 'abstain': policy = 'offer_replace'
        out.append((key, 1, policy, conf))
        if policy in ('grant', 'offer') and accept and len(ch.callings) < SEATS:
            ch.callings[key] = {'tier': 1, 'kind': kind_of(key), 'at_scene': scene}
            apply_comp(ch, key, ch.callings[key])
            ch.history.append((session, key, 1, policy, conf))
    for h in hcands:
        out.append((h, 1, 'offer', None))
        if accept and len(ch.callings) < SEATS:
            ch.callings[h] = {'tier': 1, 'kind': 'hybrid', 'at_scene': scene}
            apply_comp(ch, h, ch.callings[h])
            ch.history.append((session, h, 1, 'offer', None))
    return out

def apply_comp(ch, key, cal):
    v = COMP[cal['kind']][cal['tier'] - 1]
    if cal['kind'] == 'hybrid':
        for br in key:
            road = cal.setdefault('roads', {}).get(br)
            if road: ch.comp[road] = max(ch.comp.get(road, 0), v)
    else:
        ch.comp[key] = max(ch.comp.get(key, 0), v)
    if cal['tier'] >= 4 and not ch.attr_bumped:
        ch.attr_bumped = True
        a = max(ch.attr, key=lambda x: ch.attr[x]); ch.attr[a] = min(4, ch.attr[a] + 1)

# ---------------------------------------------------------------- play model
CTX_FIGHT = ['creature.beast.predator', 'creature.folk.human', 'creature.folk.goblin', 'creature.undead.mindless',
             'creature.beast.monstrous', 'creature.undead.ravenous', 'creature.folk.giant', 'creature.fiend.demon',
             'creature.construct.golem', 'creature.dragon.drake']
ATTR = {'deed.martial': 'agility', 'deed.guile': 'agility', 'deed.wilds': 'wits', 'deed.arcane': 'intellect',
        'deed.influence': 'presence', 'deed.lore': 'intellect', 'deed.craft': 'intellect', 'deed.divine': 'presence',
        'deed.primal': 'wits'}

def beat(rng, eng, ch, tag, tier, stakes, lethal, target, ctx, scene, secondary=(), staggered=False):
    attr = ATTR[branch(tag)]
    m = ch.mod(tag, attr); dc = DC[tier]
    q = quality(odds(m, dc)); d20 = rng.randint(1, 20)
    d, near = degree(m, dc, d20)
    if d == 1 and near and stakes != 'safe' and rng.random() < 0.6: d = 2
    b = band_of_dc(dc)
    crisis = lethal or staggered or (stakes == 'dire' and q == 'challenging')
    peak = d >= 2 and b >= ch.power_band() + 1
    e = {'tag': tag, 'secondary': list(secondary), 'quality': q, 'stakes': stakes, 'lethal': lethal, 'degree': d,
         'target': target, 'ctx': ctx, 'band': b, 'crisis': crisis, 'peak': peak}
    eng.record(e, scene)
    return e

class Style:
    """A play style: scene-type weights and, per scene type, the tags the PC uses with their weights."""
    def __init__(self, name, scene_mix, fight_tags, site_tags, social_tags=None, travel_tags=None, fused=None):
        self.name, self.scene_mix = name, scene_mix
        self.fight_tags, self.site_tags = fight_tags, site_tags
        self.social_tags = social_tags or [('deed.influence.persuasion.argument', 1)]
        self.travel_tags = travel_tags or [('deed.wilds.navigation.wayfinding', 1)]
        self.fused = fused      # (tag_a_prefix, secondary_tag, probability): grounded secondary on fights
        self.social_beats = (1, 1)

def pick(rng, wl):
    r = rng.random() * sum(w for _, w in wl); acc = 0
    for t, w in wl:
        acc += w
        if r <= acc: return t
    return wl[-1][0]

def run(style, sessions=60, seed=1, scenes_per_session=5, accept=True, keys=None, hybrids=(), ch=None,
        allow_broad=True, pivot=None, grinder=False, reflect_every=2):
    rng = random.Random(seed); eng = Engine()
    ch = ch or Char({'deed.martial.archery': 2, 'deed.wilds.tracking': 2},
                    {'agility': 3, 'might': 1, 'wits': 2, 'presence': 0, 'intellect': 0})
    scene = 0; day = 0; tid = 0; trace = []
    for s in range(1, sessions + 1):
        st = style if not (pivot and s >= pivot[0]) else pivot[1]
        for sc in range(scenes_per_session):
            scene += 1
            if sc % 2 == 0: day += 1
            band = ch.power_band()
            r = rng.random(); mix = st.scene_mix
            if grinder:
                for i in range(rng.randint(4, 6)):
                    tid += 1
                    e = beat(rng, eng, ch, 'deed.martial.archery.bow', 1, 'risky', False, f'rat{tid}', 'creature.beast.vermin', scene)
                    if e['degree'] >= 2: eng.count('cnt.defeat', e['tag'], 1, scene)
            elif r < mix[0]:        # conflict
                tier = min(5, rng.choice([band, band + 1, band + 1, band + 2]))
                stakes = 'dire' if rng.random() < 0.25 else 'risky'
                lethal = stakes == 'dire' and rng.random() < 0.4
                ctx = rng.choice(CTX_FIGHT[:5 + min(5, band + 1)])
                foes = rng.randint(1, 3); n = rng.randint(3, 6)
                for i in range(n):
                    tid += 1 if i % 2 == 0 else 0
                    tag = pick(rng, st.fight_tags); sec = []
                    if st.fused and tag.startswith(st.fused[0]) and rng.random() < st.fused[2]: sec = [st.fused[1]]
                    stag = stakes == 'dire' and rng.random() < 0.10
                    e = beat(rng, eng, ch, tag, tier, stakes, lethal, f'foe{tid}', ctx, scene, sec, stag)
                    if e['degree'] >= 2 and foes > 0 and rng.random() < (0.9 if e['degree'] == 3 else 0.5):
                        foes -= 1; eng.count('cnt.defeat', tag, tier, scene)
                    # Focus spent through an ability of the beat's tag: the origin ability before recognition,
                    # the calling's picks after it (03.7.2 cnt.focus)
                    held = any((not isinstance(k, tuple) and tag.startswith(k)) or
                               (isinstance(k, tuple) and branch(tag) in k) for k in ch.callings)
                    if rng.random() < (0.45 if held else 0.15):
                        eng.count('cnt.focus', tag, 1, scene)
            elif r < mix[0] + mix[1]:   # stealth / site / work scene
                tier = min(5, rng.choice([band, band + 1, band + 1]))
                clock = rng.random() < 0.6
                sstakes = 'dire' if rng.random() < 0.20 else 'risky'
                slethal = sstakes == 'dire' and rng.random() < 0.3
                sctx = rng.choice(['situation.exploration.ruin', 'situation.exploration.dungeon', 'situation.exploration.settlement',
                                   'situation.exploration.wilderness', 'situation.exploration.cave', 'situation.investigation.search'])
                for i in range(rng.randint(2, 4)):
                    tid += 1
                    tag = pick(rng, st.site_tags)
                    e = beat(rng, eng, ch, tag, tier, sstakes, slethal, f'obs{tid}', sctx, scene)
                    if clock and e['degree'] >= 2: eng.count('cnt.progress', tag, 3 if e['degree'] == 3 else 2, scene)
            elif r < mix[0] + mix[1] + mix[2]:   # social
                xstakes = 'dire' if rng.random() < 0.15 else 'risky'
                xctx = rng.choice(['situation.social.parley', 'situation.social.court', 'situation.social.bargaining',
                                   'situation.social.interrogation', 'situation.social.performance'])
                xtier = min(5, rng.choice([band, band + 1, band + 1, band + 2]))
                for i in range(rng.randint(*st.social_beats)):
                    tid += 1
                    tag = pick(rng, st.social_tags)
                    e = beat(rng, eng, ch, tag, xtier, xstakes, False, f'npc{tid}', xctx, scene)
                    if e['degree'] >= 2 and rng.random() < 0.5: eng.count('cnt.progress', tag, 3 if e['degree'] == 3 else 2, scene)
            else:                        # travel
                tid += 1
                tag = pick(rng, st.travel_tags)
                e = beat(rng, eng, ch, tag, min(5, band + 1), 'risky', False, f'route{tid}', 'situation.travel.overland', scene)
                eng.count('cnt.journey', tag, 1, scene)
            eng.settle(scene, day)
            if sc % reflect_every == reflect_every - 1 or sc == scenes_per_session - 1:   # a long rest -> reflection
                # hybrid roads: the top level-2 child of each branch at the time of the pass
                for h in hybrids:
                    pass
                ks = keys if keys is not None else candidate_keys(eng)
                res = recognition_pass(eng, ch, s, scene, ks, hybrids, accept, allow_broad)
                for key, cal in ch.callings.items():
                    if cal['kind'] == 'hybrid' and 'roads' not in cal:
                        cal['roads'] = {}
                        for br in key:
                            kids = children_l2(eng, br)
                            if kids: cal['roads'][br] = max(kids, key=kids.get)
                        apply_comp(ch, key, cal)
                trace.extend((s,) + tuple(x) for x in res)
    return eng, ch, trace

def candidate_keys(eng):
    return [n for n in eng.weighted if lvl(n) in (1, 2) or n in FINE_KEYS]

# ---------------------------------------------------------------- styles
ARCHER = Style('focused archer who scouts by stealth (03 scenario A)', (0.45, 0.25, 0.15, 0.15),
               [('deed.martial.archery.bow', 75), ('deed.martial.blade.dagger', 15), ('deed.martial.athletics.acrobatics', 10)],
               [('deed.guile.stealth.sneaking', 40), ('deed.guile.stealth.infiltration', 20),
                ('deed.martial.athletics.climbing', 20), ('deed.wilds.tracking.trailing', 20)])
PURE = Style('single-track swordsman (fights 70% of scenes)', (0.70, 0.10, 0.10, 0.10),
             [('deed.martial.blade.sword', 90), ('deed.martial.shield.block', 10)],
             [('deed.martial.athletics.climbing', 60), ('deed.lore.investigation.search', 40)])
MIXED_WEAPONS = Style('mixed-weapons fighter', (0.60, 0.15, 0.15, 0.10),
             [('deed.martial.blade.sword', 30), ('deed.martial.polearm.spear', 25), ('deed.martial.archery.bow', 20),
              ('deed.martial.shield.block', 10), ('deed.martial.tactics.ground', 15)],
             [('deed.martial.athletics.climbing', 60), ('deed.lore.investigation.search', 40)])
def two_branch(pa, name):
    pb = 100 - pa
    return Style(name, (0.45, 0.25, 0.15, 0.15),
                 [('deed.martial.blade.sword', pa), ('deed.arcane.fire.blast', pb)],
                 [('deed.martial.athletics.climbing', pa), ('deed.arcane.divination.detection', pb)],
                 fused=('deed.martial.blade', 'deed.arcane.fire.blast', 0.3 if pb >= 30 else 0.0))
THIEF = Style('burglar: site scenes 60%', (0.15, 0.60, 0.15, 0.10),
              [('deed.martial.blade.dagger', 100)],
              [('deed.guile.thievery.lockpicking', 40), ('deed.guile.stealth.sneaking', 35), ('deed.guile.thievery.traps', 25)])
TALKER = Style('envoy: social scenes 55%', (0.15, 0.15, 0.55, 0.15),
               [('deed.martial.blade.dagger', 100)], [('deed.lore.investigation.inquiry', 100)],
               social_tags=[('deed.influence.persuasion.argument', 50), ('deed.influence.intrigue.leverage', 25),
                            ('deed.influence.insight.motives', 25)])
TALKER.social_beats = (2, 4)
THREEWAY = Style('three-branch generalist', (0.40, 0.30, 0.20, 0.10),
               [('deed.martial.blade.sword', 34), ('deed.arcane.fire.blast', 33), ('deed.divine.smiting.radiance', 33)],
               [('deed.guile.stealth.sneaking', 34), ('deed.lore.investigation.search', 33), ('deed.wilds.tracking.trailing', 33)])
FIRE = Style('fire sorcerer (after a pivot)', (0.45, 0.25, 0.15, 0.15),
             [('deed.arcane.fire.blast', 85), ('deed.arcane.warding.shielding', 15)],
             [('deed.arcane.divination.detection', 60), ('deed.lore.arcana.identification', 40)])

def pct(v, p):
    v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]
def trip(v):
    v = [x for x in v]
    return f"{pct(v,.1)}/{int(statistics.median(v))}/{pct(v,.9)}"

def reach(style, key, seeds=200, sessions=60, **kw):
    """sessions at which the calling keyed on `key` reaches each tier (99 = never within the run)"""
    res = {t: [] for t in range(1, 6)}; pol = defaultdict(int); confs = defaultdict(int); held = []
    for sd in range(1, seeds + 1):
        eng, ch, tr = run(style, sessions=sessions, seed=sd, **kw)
        got = {t: 99 for t in range(1, 6)}
        for (s, k, t, p, c) in ch.history:
            if k == key and got[t] == 99:
                got[t] = s
                if t == 1: pol[p] += 1; confs[c] += 1
        for t in range(1, 6): res[t].append(got[t])
        held.append(len(ch.callings))
    return res, pol, confs, held

def share_stats(style, sessions, seeds=100, mk=None):
    out = []
    for sd in range(1, seeds + 1):
        eng, ch, tr = run(style, sessions=sessions, seed=sd, keys=[], ch=mk() if mk else None)
        kids = children_l2(eng, 'deed.martial'); top = max(kids.values(), default=0)
        out.append(round(top / max(1, eng.weighted['deed.martial']), 2))
    return out

def tiers_of(style, keys, hybrids=(), mk=None, sessions=60, seeds=200, want=None):
    res = {t: [] for t in range(1, 6)}; pol = defaultdict(int); confs = defaultdict(int)
    for sd in range(1, seeds + 1):
        eng, ch, tr = run(style, sessions=sessions, seed=sd, keys=keys, hybrids=hybrids, ch=mk() if mk else None)
        got = {t: 99 for t in range(1, 6)}
        for (s_, k, t, p_, c) in ch.history:
            if want is not None and k != want: continue
            if got[t] == 99:
                got[t] = s_
                if t == 1: pol[p_] += 1; confs[c] += 1
        for t in range(1, 6): res[t].append(got[t])
    return res, pol, confs

def line(res):
    return '  '.join(f'T{t}: {trip(res[t])}' for t in range(1, 6))

CH_TALK = lambda: Char({'deed.influence.persuasion': 2, 'deed.lore.law': 2}, {'agility': 1, 'might': 0, 'wits': 2, 'presence': 3, 'intellect': 1})
CH_THIEF = lambda: Char({'deed.guile.thievery': 2, 'deed.guile.stealth': 2}, {'agility': 3, 'might': 0, 'wits': 2, 'presence': 1, 'intellect': 1})
CH_SWORD = lambda: Char({'deed.martial.blade': 2, 'deed.martial.shield': 2}, {'agility': 3, 'might': 2, 'wits': 1, 'presence': 0, 'intellect': 0})
CH_H = lambda: Char({'deed.martial.blade': 2, 'deed.arcane.fire': 2}, {'agility': 3, 'might': 1, 'wits': 1, 'presence': 0, 'intellect': 2})

if __name__ == '__main__':
    N = 200
    print('=== R1. Pacing: session at which the focus calling reaches each tier (p10/median/p90; 99 = not within 60 sessions) ===')
    for style, key, mk in [(ARCHER, 'deed.martial.archery', None), (PURE, 'deed.martial.blade', CH_SWORD),
                           (THIEF, 'deed.guile.thievery', CH_THIEF), (TALKER, 'deed.influence.persuasion', CH_TALK)]:
        res, pol, confs = tiers_of(style, [key], mk=mk)
        print(f'{style.name:<52} key {key}')
        print('   ', line(res), ' | reached T4 / T5 within 60:', sum(1 for x in res[4] if x < 99), '/', sum(1 for x in res[5] if x < 99), 'of', N)
        print('    first recognition policy:', dict(pol), ' confidence then:', dict(sorted(confs.items())))
    print('\n=== R2. Fine (level-3) key: lockpicking under the burglar (W x 3/4) ===')
    res, pol, confs = tiers_of(THIEF, ['deed.guile.thievery.lockpicking'], mk=CH_THIEF)
    print('   ', line(res))
    print('\n=== R3. Broad (branch) calling: who is offered Warrior (deed.martial) at tier 1? ===')
    for style, mk in ((ARCHER, None), (PURE, CH_SWORD), (MIXED_WEAPONS, CH_SWORD)):
        got = []; never = 0
        for sd in range(1, N + 1):
            eng, ch, tr = run(style, sessions=30, seed=sd, keys=['deed.martial'], ch=mk() if mk else None)
            g = [s_ for (s_, k, t, p_, c) in ch.history if k == 'deed.martial' and t == 1]
            got.append(g[0] if g else 99); never += 0 if g else 1
        sh = share_stats(style, 10, mk=mk)
        print(f'   {style.name:<52} first at session {trip(got)}; never in 30 sessions: {never}/{N}; top child share of martial at s10 {trip(sh)}')
    res, pol, confs = tiers_of(MIXED_WEAPONS, ['deed.martial'], mk=CH_SWORD, sessions=70)
    print('   mixed-weapons Warrior tiers:', line(res))
    print('\n=== R4. Hybrid trigger (martial x arcane): offered within 20 sessions, by mix (R3 G-1 acceptance test) ===')
    H = [('deed.martial', 'deed.arcane')]
    for pa in (100, 95, 90, 80, 70, 60, 50):
        st = two_branch(pa, f'{pa}/{100-pa}')
        off = []; bal = []
        for sd in range(1, N + 1):
            eng, ch, tr = run(st, sessions=20, seed=sd, keys=[], hybrids=H, ch=CH_H())
            g = [s_ for (s_, k, t, p_, c) in ch.history if k == H[0] and t == 1]
            off.append(g[0] if g else 99)
            a, b = eng.weighted['deed.martial'], eng.weighted['deed.arcane']
            bal.append(round(min(a, b) / max(a, b, 1), 2))
        n = sum(1 for x in off if x < 99)
        print(f'   {pa:>3}/{100-pa:<3} offered in {n:>3}/{N} runs; first offer session {trip([x for x in off if x < 99]) if n else "-"}; '
              f'balance at s20 median {statistics.median(bal)}')
    off = 0
    for sd in range(1, N + 1):
        eng, ch, tr = run(ARCHER, sessions=20, seed=sd, keys=[], hybrids=[('deed.martial', 'deed.guile')])
        off += 1 if ch.history else 0
    print(f'   archer with stealth as a second pillar (25% of scenes): martial x guile hybrid offered in {off}/{N} runs by session 20')
    res, pol, confs = tiers_of(two_branch(50, '50/50'), [], hybrids=H, mk=CH_H)
    print('   deliberate 50/50 hybrid tiers:', line(res))
    print('\n=== R5. The grinder (03 scenario B): rats every scene, 20 sessions ===')
    rec = 0; wts = []; cts = []
    for sd in range(1, N + 1):
        eng, ch, tr = run(ARCHER, sessions=20, seed=sd, grinder=True)
        rec += 1 if ch.history else 0; wts.append(eng.weighted['deed.martial.archery']); cts.append(eng.counted['deed.martial.archery'])
    d = eng.detail('deed.martial.archery')
    print(f'   recognized in {rec}/{N} runs; archery weighted at s20 median {int(statistics.median(wts))}; counted median {int(statistics.median(cts))}; '
          f'difficult-or-better events {d["dc_events"]}, routine {d["routine"]}')
    print('\n=== R6. A whole character (level-2 keys + branch keys + curated level-3 keys live; 3 seats; accepts everything) ===')
    HY = [('deed.martial', 'deed.guile'), ('deed.martial', 'deed.arcane')]
    for style, mk in ((ARCHER, None), (PURE, CH_SWORD), (THIEF, CH_THIEF), (THREEWAY, CH_H)):
        n_at = {5: [], 10: [], 20: [], 40: []}; firsts = defaultdict(int); maxtier = {10: [], 20: [], 40: [], 60: []}; first_s = []
        for sd in range(1, 101):
            eng, ch, tr = run(style, sessions=60, seed=sd, hybrids=HY, ch=mk() if mk else None)
            for s_ in n_at: n_at[s_].append(len({k for (ss, k, t, p_, c) in ch.history if ss <= s_}))
            for s_ in maxtier: maxtier[s_].append(max([t for (ss, k, t, p_, c) in ch.history if ss <= s_], default=0))
            if ch.history: firsts[str(ch.history[0][1])] += 1; first_s.append(ch.history[0][0])
            else: first_s.append(99)
        print(f'   {style.name:<52} first recognition at session {trip(first_s)}; callings at s5/10/20/40 (median): '
              + '/'.join(str(int(statistics.median(n_at[k]))) for k in n_at)
              + '; highest tier at s10/20/40/60: ' + '/'.join(str(int(statistics.median(maxtier[k]))) for k in maxtier))
        print('      first calling recognized:', dict(sorted(firsts.items(), key=lambda x: -x[1])[:4]))
    print('\n=== R7. Confidence calibration: confirmation rate by confidence (level-2 candidates, nothing accepted) ===')
    tab = defaultdict(lambda: [0, 0, 0]); poltab = defaultdict(lambda: [0, 0, 0])
    for style, mk in ((ARCHER, None), (PURE, CH_SWORD), (THIEF, CH_THIEF), (TALKER, CH_TALK), (THREEWAY, CH_H),
                      (two_branch(80, '80/20'), CH_H)):
        for sd in range(1, 61):
            eng, ch, tr = run(style, sessions=20, seed=sd, accept=False, allow_broad=False, ch=mk() if mk else None)
            first = {}
            for row in tr:
                if len(row) != 5: continue
                s_, key, t, policy, conf = row
                if isinstance(key, tuple) or t != 1 or key in first: continue
                first[key] = (s_, conf, policy)
            for key, (s_, conf, policy) in first.items():
                e2, c2, t2 = run(style, sessions=min(26, s_ + 5), seed=sd, accept=False, allow_broad=False, ch=mk() if mk else None)
                confirmed = e2.recent(key) >= R_CONFIRM
                pillar = eng.raw[key] * 100 >= 15 * max(1, eng.raw['deed'])
                tab[conf][0] += 1; tab[conf][1] += confirmed; tab[conf][2] += pillar
                poltab[policy][0] += 1; poltab[policy][1] += confirmed; poltab[policy][2] += pillar
    for conf in sorted(tab):
        n, cf, pl = tab[conf]
        print(f'   confidence {conf}: {n:>4} candidates; would confirm {100*cf//n}%; a designed pillar {100*pl//n}%')
    for p_ in ('grant', 'offer', 'abstain'):
        if p_ in poltab:
            n, cf, pl = poltab[p_]
            print(f'   policy {p_:<8}: {n:>4} candidates; would confirm {100*cf//n}%; a designed pillar {100*pl//n}%')
    print('\n=== R8. Provisional grants: a tier-2 grant, then the archer turns to fire sorcery (04.8.2) ===')
    # confirm when the weighted evidence at the key SINCE THE GRANT reaches 24 within 24 evidence-bearing scenes; else lapse
    mkp = lambda: Char({'deed.martial.archery': 2, 'deed.wilds.tracking': 2, 'deed.arcane.fire': 2},
                       {'agility': 3, 'might': 1, 'wits': 2, 'presence': 0, 'intellect': 2})
    K = 'deed.martial.archery'
    res = {0: [0, 0], 1: [0, 0], 2: [0, 0], 99: [0, 0]}; fire_t1 = []
    for sd in range(1, N + 1):
        e3, c3, t3 = run(ARCHER, sessions=14, seed=sd, keys=[K], ch=mkp())
        g = [s_ for (s_, k, t, p_, c) in c3.history if t == 2]
        if not g: continue
        sg = g[0]
        e3, c3, t3 = run(ARCHER, sessions=sg, seed=sd, keys=[K], ch=mkp()); gs = c3.callings[K]['at_scene']
        for delay in (0, 1, 2, 99):
            piv = (sg + 1 + delay, FIRE) if delay != 99 else None
            e2, c2, t2 = run(ARCHER, sessions=sg + 6, seed=sd, keys=[K, 'deed.arcane.fire'], ch=mkp(), pivot=piv)
            w24 = sum(v for sc_, v in e2.node_scene_pts[K].items() if gs < sc_ <= gs + 24)
            res[delay][0] += 1; res[delay][1] += w24 >= 24
            if delay == 0:
                gf = [s_ - sg for (s_, k, t, p_, c) in c2.history if k == 'deed.arcane.fire' and t == 1]
                fire_t1.append(gf[0] if gf else 99)
    for d, lab in ((0, 'stops at once'), (1, 'keeps shooting one more session'), (2, 'two more sessions'), (99, 'never stops')):
        print(f'   archer who {lab:<32}: tier 2 confirmed {res[d][1]:>3} / lapsed {res[d][0] - res[d][1]:>3} of {res[d][0]}')
    print('   the new fire calling is first recognized', trip(fire_t1), 'sessions after the pivot (pivot the session after the grant)')
    print('\n=== R9. Yields 04 depends on (session 10): weighted / counted / recent at the focus node ===')
    for style, key, mk in ((ARCHER, 'deed.martial.archery', None), (THIEF, 'deed.guile.thievery', CH_THIEF), (TALKER, 'deed.influence.persuasion', CH_TALK)):
        ws, cs, rs = [], [], []
        for sd in range(1, N + 1):
            eng, ch, tr = run(style, sessions=10, seed=sd, keys=[key], ch=mk() if mk else None)
            ws.append(eng.weighted[key]); cs.append(eng.counted[key]); rs.append(eng.recent(key))
        print(f'   {key}: weighted {trip(ws)}   counted {trip(cs)}   recent {trip(rs)}   counted/weighted median {statistics.median([c/max(1,w) for c,w in zip(cs,ws)]):.2f}')
    print('\n=== R10. Vow (conduct-keyed) pacing: session at which positive points on one axis reach P (p10/median/p90) ===')
    P = [16, 40, 80, 140, 220]
    def vow(p_take, seeds=200, sessions=90):
        out = {x: [] for x in P}
        for sd in range(1, seeds + 1):
            rng = random.Random(sd); pos = 0; got = {x: 99 for x in P}
            for s_ in range(1, sessions + 1):
                for sc in range(5):
                    if rng.random() < 0.45 and rng.random() < p_take:      # a conflict scene with a costly choice taken
                        pos += 4 if rng.random() < 0.25 else 2             # Dire or lethal ground -> 4, else 2 (03.3.3)
                for x in P:
                    if got[x] == 99 and pos >= x: got[x] = s_
            for x in P: out[x].append(got[x])
        return out
    for name, p in (('sworn in all but name (takes the costly choice in 60% of fights)', 0.60),
                    ('often (30% of fights)', 0.30), ('now and then (03 scenario A: 15%)', 0.15)):
        o = vow(p)
        print(f'   {name:<64}', '  '.join(f'{x}: {trip(o[x])}' for x in P))
