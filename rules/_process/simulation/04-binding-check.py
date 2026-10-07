#!/usr/bin/env python3
"""04-binding-check.py -- revision I-089: which requirement of 04.3.2/04.3.4 is met LAST when the focused archer
(04-recog04.py's R1 style, conflicts on the advisory offsets of DL-00-05) enters each tier. Per tier, the
requirement whose first satisfied reflection (since the last crystallization) is latest is the binding one (ties go
to the first listed: W, C, quality events, scenes, great deeds, crises, contexts). Run on 04's ladder before
I-089 (narrow W 80/200/440/800/1300) and on the current one. Deterministic: 04-recog04.py's seeds 1-200.
Python 3, standard library only."""
import importlib.util, os
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('r4', os.path.join(HERE, '04-recog04.py'))
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
KEY = 'deed.martial.archery'
CURRENT = {k: list(v) for k, v in R.W.items()}
OLD = [80, 200, 440, 800, 1300]

def components(eng, key, tier, since, kind):
    c = {'W': eng.weighted[key] >= R.W[kind][tier - 1], 'C': eng.counted[key] >= R.C[kind][tier - 1]}
    if tier == 1:
        d = eng.detail(key)
        c.update(quality=d['dc_events'] >= R.Q1, scenes=d['scenes'] >= R.S1)
        return c
    d = eng.detail(key, since=since); r = R.SINCE[tier]
    c.update(quality=d['dc_events'] >= r['dc'], scenes=d['scenes'] >= r['scenes'], great=R.great(d, tier, r['great']),
             crises=d['crises'] >= r['crises'], contexts=d['contexts'] >= r['contexts'])
    return c

def measure(seeds=200):
    binding = defaultdict(Counter); first = {}; scene_now = [0]
    orig_pass, orig_elig = R.recognition_pass, R.eligible
    def elig(eng, ch, key, tier, since, kind=None):
        ok = orig_elig(eng, ch, key, tier, since, kind)
        if key == KEY:
            st = first.setdefault(tier, {})
            for k, v in components(eng, key, tier, since, kind or R.kind_of(key)).items():
                if v and k not in st: st[k] = scene_now[0]
            if ok:
                binding[tier][max(st, key=st.get)] += 1; first.pop(tier)
        return ok
    def rpass(eng, ch, session, scene, *a, **k):
        scene_now[0] = scene; return orig_pass(eng, ch, session, scene, *a, **k)
    R.eligible, R.recognition_pass = elig, rpass
    try:
        for sd in range(1, seeds + 1):
            first.clear(); R.run(R.ARCHER, sessions=60, seed=sd, keys=[KEY])
    finally:
        R.eligible, R.recognition_pass = orig_elig, orig_pass
    return binding

for label, narrow in (("before I-089 (narrow W 80/200/440/800/1300)", OLD), ("current (04-recog04.py's W)", CURRENT['narrow'])):
    R.W.update({'narrow': narrow, 'fine': [x * 3 // 4 for x in narrow], 'broad': [x * 3 // 2 for x in narrow],
                'hybrid': [x * 3 // 4 for x in narrow]})
    R.C.update({k: [v // 10 for v in vs] for k, vs in R.W.items()})
    b = measure()
    print('=== ladder:', label, '-- focused archer, 200 seeds: requirement met last, by tier entered')
    for t in sorted(b):
        print('  tier %d: %s' % (t, ', '.join('%s %d' % kv for kv in b[t].most_common())))
