"""wren04.py -- one continuous character (Wren) traced through 04's rules, for the chapter's long worked example.
Uses recog04's engine and rules; prints every recognition-relevant moment with the tally values 04 reads."""
import importlib.util, random
import os; spec = importlib.util.spec_from_file_location('r', os.path.join(os.path.dirname(os.path.abspath(__file__)), '04-recog04.py')); r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)

WREN = r.Style('Wren: archer, tracker, scout', (0.40, 0.35, 0.10, 0.15),
               [('deed.martial.archery.bow', 70), ('deed.martial.polearm.spear', 15), ('deed.martial.athletics.acrobatics', 15)],
               [('deed.wilds.tracking.trailing', 30), ('deed.wilds.tracking.hunting', 15), ('deed.guile.stealth.sneaking', 25),
                ('deed.wilds.survival.weathersense', 15), ('deed.martial.athletics.climbing', 15)],
               travel_tags=[('deed.wilds.navigation.wayfinding', 60), ('deed.wilds.foraging.food', 40)])
SEED = int(__import__('sys').argv[1]) if len(__import__('sys').argv) > 1 else 7
KEYS = ['deed.martial.archery', 'deed.wilds.tracking', 'deed.guile.stealth', 'deed.martial', 'deed.wilds']
H = ('deed.martial', 'deed.wilds')

def snap(eng, key, since=0):
    d = eng.detail(key, since)
    return (f"weighted {eng.weighted[key]}, counted {eng.counted[key]}, recent {eng.recent(key)}, "
            f"D+C events {d['dc_events']} (challenging {d['challenging']}, routine {d['routine']}), scenes {d['scenes']}, "
            f"by_band {d['by_band']}, success_by_band {d['succ_by_band']}, crises {d['crises']}, contexts {d['contexts']}")

# replay session by session with the acceptance script of the example
rng = random.Random(SEED); eng = r.Engine()
ch = r.Char({'deed.martial.archery': 2, 'deed.wilds.tracking': 2}, {'agility': 3, 'might': 1, 'wits': 2, 'presence': 0, 'intellect': 0})
import types
seen_first = {}; hybrid_first = None
orig_pass = r.recognition_pass
events = []
def my_pass(eng_, ch_, session, scene, keys, hybrids, accept=True, allow_broad=True):
    global hybrid_first
    out = []
    # tier-ups (accept)
    for key, cal in list(ch_.callings.items()):
        if cal['tier'] >= 5: continue
        t = cal['tier'] + 1
        ok = (r.hybrid_eligible(eng_, *key, t, cal['at_scene']) if cal['kind'] == 'hybrid' else r.eligible(eng_, ch_, key, t, cal['at_scene'], cal['kind']))
        if ok:
            what = snap(eng_, key, cal['at_scene']) if cal['kind'] != 'hybrid' else ('martial: ' + snap(eng_, key[0], cal['at_scene']) + ' || wilds: ' + snap(eng_, key[1], cal['at_scene']))
            events.append((session, scene, f"TIER {t} ready for {key}: since last -> {what}; total weighted {eng_.weighted[key] if cal['kind']!='hybrid' else (eng_.weighted[key[0]], eng_.weighted[key[1]])}"))
            cal['tier'] = t; cal['at_scene'] = scene; r.apply_comp(ch_, key, cal)
            ch_.history.append((session, key, t, 'offer', None))
    # consolidation at the season boundary after session 26 (scene 130): Archer + Tracker -> Ranger
    if scene >= 130 and H not in ch_.callings and r.hybrid_eligible(eng_, H[0], H[1], 1, 0) and not getattr(ch_, 'consolidated', False):
        a, b = H; mn = min(eng_.weighted[a], eng_.weighted[b]); top = max(c['tier'] for c in ch_.callings.values())
        t = max([i + 1 for i, w in enumerate(r.W['hybrid']) if mn >= w and i + 1 <= top] or [1])
        events.append((session, scene, f"CONSOLIDATE {dict((k, v['tier']) for k, v in ch_.callings.items())} -> Ranger tier {t}: martial {eng_.weighted[a]} wilds {eng_.weighted[b]} min {mn}; archery {eng_.weighted['deed.martial.archery']} tracking {eng_.weighted['deed.wilds.tracking']}; recent {eng_.recent(a)}/{eng_.recent(b)}; joint scenes {len(eng_.scenes[a] & eng_.scenes[b])}; comp {dict(ch_.comp)}"))
        ch_.callings.clear(); ch_.callings[H] = {'tier': t, 'kind': 'hybrid', 'at_scene': scene, 'roads': {a: 'deed.martial.archery', b: 'deed.wilds.tracking'}}
        r.apply_comp(ch_, H, ch_.callings[H]); ch_.consolidated = True
        ch_.history.append((session, H, t, 'consolidation', None))
        return out
    for key, cal in list(ch_.callings.items()):
        if cal['kind'] == 'hybrid' and cal['tier'] < 5:
            t = cal['tier'] + 1; a, b = key
            da, db = eng_.detail(a, cal['at_scene']), eng_.detail(b, cal['at_scene'])
            if session in (30, 34, 38, 42, 46, 50) and scene % 5 == 0:
                events.append((session, scene, f"  (Ranger progress to tier {t}: min {min(eng_.weighted[a], eng_.weighted[b])}; since: D+C {da['dc_events']}+{db['dc_events']}, scenes {da['scenes']}/{db['scenes']}, by_band {da['by_band']} / {db['by_band']}, crises {da['crises']}+{db['crises']}, contexts {da['contexts']}+{db['contexts']})"))
    cands = [k for k in KEYS if k not in ch_.callings and k not in seen_first and r.eligible(eng_, ch_, k, 1, 0) and not getattr(ch_, 'consolidated', False)]
    hy = r.hybrid_eligible(eng_, H[0], H[1], 1, 0)
    for key in cands:
        lineage = any(not isinstance(k, tuple) and (k.startswith(key + '.') or key.startswith(k + '.')) for k in ch_.callings)
        rivals = [k for k in cands if k != key and r.branch(k) == r.branch(key)]
        clear = not rivals and not (hy and r.branch(key) in H)
        conf, current = r.confidence(eng_, key, 1, r.kind_of(key))
        w = eng_.weighted[key]; rec = eng_.recent(key)
        ks = (2*rec >= r.W[r.kind_of(key)][0], 2*rec >= w, 5*w >= eng_.weighted['deed'],
              w >= sorted((v for n, v in eng_.weighted.items() if r.lvl(n) == r.lvl(key)), reverse=True)[2] if len([1 for n in eng_.weighted if r.lvl(n) == r.lvl(key)]) >= 3 else True,
              4*w >= 5*r.W[r.kind_of(key)][0])
        policy = 'abstain' if (conf == 0 or not current) else 'grant' if (conf >= 4 and clear and r.lvl(key) >= 2 and not lineage) else 'offer'
        events.append((session, scene, f"CANDIDATE {key}: {snap(eng_, key)}; deed root {eng_.weighted['deed']}; K1..K5 {ks} -> confidence {conf}; current {current}; clear field {clear}; lineage conflict {lineage}; policy {policy}"))
        if key == 'deed.martial.archery' and policy == 'grant':  # [revision: I-109] the pick table of WE-04-5 reads these
            tags = ['deed.martial.archery', 'deed.martial.archery.bow', 'deed.martial.athletics.acrobatics', 'deed.martial.athletics.climbing',
                    'deed.martial.athletics', 'deed.martial.tactics.reading', 'deed.martial.polearm.spear', 'deed.martial']
            events.append((session, scene, "  (weighted at tags: " + ', '.join(f"{t.replace('deed.martial.', '')} {eng_.weighted.get(t, 0)}" for t in tags) + ")"))
        if policy != 'abstain':
            seen_first[key] = session
            if not lineage and len(ch_.callings) < r.SEATS and key in ('deed.martial.archery', 'deed.wilds.tracking'):
                ch_.callings[key] = {'tier': 1, 'kind': r.kind_of(key), 'at_scene': scene}; r.apply_comp(ch_, key, ch_.callings[key])
                ch_.history.append((session, key, 1, policy, conf))
    if hy and hybrid_first is None:
        hybrid_first = session
        a, b = H; wa, wb = eng_.weighted[a], eng_.weighted[b]
        joint = len(eng_.scenes[a] & eng_.scenes[b])
        events.append((session, scene, f"HYBRID {H} eligible: weighted {wa}/{wb} min {min(wa,wb)} balance {min(wa,wb)}/{max(wa,wb)}; joint scenes {joint}; recent {eng_.recent(a)}/{eng_.recent(b)}; counted {eng_.counted[a]}/{eng_.counted[b]}"))
    return out
r.recognition_pass = my_pass
eng, ch, tr = r.run(WREN, sessions=60, seed=SEED, keys=KEYS, hybrids=[H], ch=ch)
for e in events: print(f"s{e[0]:>2} scene {e[1]:>3}: {e[2]}")
print('history', ch.history)
print('final', {k: v['tier'] for k, v in ch.callings.items()}, 'martial', eng.weighted['deed.martial'], 'wilds', eng.weighted['deed.wilds'],
      'archery', eng.weighted['deed.martial.archery'], 'tracking', eng.weighted['deed.wilds.tracking'])
for s_ in (10, 20, 30, 40):
    pass
