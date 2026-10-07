"""feat04.py -- which confirmations predict that a provisional grant would be confirmed? (design aid for 04.4.2)"""
import importlib.util, statistics
from collections import defaultdict
import os; spec = importlib.util.spec_from_file_location('r', os.path.join(os.path.dirname(os.path.abspath(__file__)), '04-recog04.py')); r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)

rows = []
styles = ((r.ARCHER, None), (r.PURE, r.CH_SWORD), (r.THIEF, r.CH_THIEF), (r.TALKER, r.CH_TALK), (r.THREEWAY, r.CH_H),
          (r.two_branch(80, '80/20'), r.CH_H), (r.MIXED_WEAPONS, r.CH_SWORD))
for style, mk in styles:
    for sd in range(1, 41):
        # replay scene by scene: capture features at first eligibility for each level-2 key
        rng_first = {}
        for upto in range(1, 21):
            eng, ch, tr = r.run(style, sessions=upto, seed=sd, accept=False, allow_broad=False, keys=[], ch=mk() if mk else None)
            for key in [n for n in eng.weighted if r.lvl(n) == 2]:
                if key in rng_first: continue
                if r.eligible(eng, ch, key, 1, 0):
                    w, c = eng.weighted[key], eng.counted[key]; d = eng.detail(key); rec = eng.recent(key)
                    root = eng.weighted['deed']; br = eng.weighted[r.branch(key)]
                    sibs = [v for k, v in eng.weighted.items() if r.lvl(k) == 2 and k != key]
                    rng_first[key] = dict(session=upto, w=w, c=c, rec=rec, share_root=w / root, lead=w >= max(sibs, default=0),
                                          top3=sum(1 for v in sibs if v > w) < 3, ch_ge_r=d['challenging'] >= d['routine'],
                                          dc=d['dc_events'], raw=d['raw'], scenes=d['scenes'])
        for key, f in rng_first.items():
            e2, c2, t2 = r.run(style, sessions=min(26, f['session'] + 5), seed=sd, accept=False, allow_broad=False, keys=[], ch=mk() if mk else None)
            f['confirm'] = e2.recent(key) >= r.R_CONFIRM
            f['key'] = key; rows.append(f)

def rate(pred, name):
    a = [x for x in rows if pred(x)]; b = [x for x in rows if not pred(x)]
    ra = sum(x['confirm'] for x in a) / max(1, len(a)); rb = sum(x['confirm'] for x in b) / max(1, len(b))
    print(f'{name:<44} true: n={len(a):>4} confirm {ra:.0%} | false: n={len(b):>4} confirm {rb:.0%}')

print('candidates', len(rows), 'overall confirm', f"{sum(x['confirm'] for x in rows)/len(rows):.0%}")
rate(lambda x: 4 * x['w'] >= 5 * 80, 'margin: weighted >= 100')
rate(lambda x: 4 * x['c'] >= 5 * 8, 'counted margin: counted >= 10')
rate(lambda x: x['c'] >= 16, 'counted >= 2C')
rate(lambda x: x['ch_ge_r'] and x['dc'] >= 12, 'quality: challenging >= routine and dc >= 12')
for R in (20, 30, 40, 50, 60):
    rate(lambda x, R=R: x['rec'] >= R, f'recent >= {R}')
for p in (0.10, 0.15, 0.20, 0.25, 0.33):
    rate(lambda x, p=p: x['share_root'] >= p, f'share of root >= {p}')
rate(lambda x: x['lead'], 'leading level-2 node of the character')
rate(lambda x: x['top3'], 'among the top three level-2 nodes')
for s in (4, 6, 8, 10):
    rate(lambda x, s=s: x['session'] <= s, f'became eligible by session {s}')
rate(lambda x: x['rec'] * 2 >= x['w'], 'recent >= half of weighted (fast riser)')
rate(lambda x: x['rec'] * 4 >= x['w'] * 3, 'recent >= 3/4 of weighted')
# candidate confidence definitions
def conf_a(x):
    return sum([x['rec'] >= 40, x['share_root'] >= 0.2, x['top3'], 4 * x['c'] >= 5 * 8, x['ch_ge_r'] and x['dc'] >= 12])
tab = defaultdict(lambda: [0, 0])
for x in rows:
    k = conf_a(x); tab[k][0] += 1; tab[k][1] += x['confirm']
print('conf_a = [recent>=40, share_root>=1/5, top3, counted margin, quality]')
for k in sorted(tab): print('  ', k, tab[k][0], f'{tab[k][1]/tab[k][0]:.0%}')
def conf_b(x):
    return sum([x['rec'] >= 40, x['rec'] * 2 >= x['w'], x['share_root'] >= 0.2, 4 * x['c'] >= 5 * 8, x['ch_ge_r'] and x['dc'] >= 12])
tab = defaultdict(lambda: [0, 0])
for x in rows:
    k = conf_b(x); tab[k][0] += 1; tab[k][1] += x['confirm']
print('conf_b = [recent>=40, recent>=w/2, share_root>=1/5, counted margin, quality]')
for k in sorted(tab): print('  ', k, tab[k][0], f'{tab[k][1]/tab[k][0]:.0%}')
