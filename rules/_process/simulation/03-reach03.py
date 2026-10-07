import statistics
import importlib.util, os
_spec = importlib.util.spec_from_file_location("evidence03", os.path.join(os.path.dirname(os.path.abspath(__file__)), "03-evidence03.py"))
_m = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m); run = _m.run
TH = [40, 60, 80, 120, 160, 200, 300, 450]
nodes = ['deed.martial.archery', 'deed.martial', 'deed.guile.stealth', 'deed.guile', 'deed.wilds', 'deed']
res = {n: {t: [] for t in TH} for n in nodes}
for sd in range(1, 201):
    eng, log = run('A', seed=sd, sessions=30)
    for n in nodes:
        for t in TH:
            s = next((s for s, d, m in log if d[n][0] >= t), 31)
            res[n][t].append(s)
def pct(v, p):
    v = sorted(v); return v[min(len(v)-1, int(p*len(v)))]
print('session at which weighted first reaches threshold (p10/median/p90; 31 = not within 30 sessions)')
print('node'.ljust(22), ' '.join(f'{t:>11}' for t in TH))
for n in nodes:
    print(n.ljust(22), ' '.join(f'{pct(res[n][t],.1):>3}/{int(statistics.median(res[n][t])):>2}/{pct(res[n][t],.9):>3}'.rjust(11) for t in TH))
# hybrid G: min(archery, fire) and joint
g = {t: [] for t in TH}
for sd in range(1, 101):
    eng, log = run('G', seed=sd, sessions=30)
    for t in TH:
        s = next((s for s, d, m in log if min(d['deed.martial.archery'][0], d['deed.arcane.fire'][0]) >= t), 31)
        g[t].append(s)
print('hybrid G min(archery, fire)'.ljust(22), ' '.join(f'{pct(g[t],.1):>3}/{int(statistics.median(g[t])):>2}/{pct(g[t],.9):>3}'.rjust(11) for t in TH))
# focused A: off-branch incidental min(martial, guile) and min(martial, wilds)
for other in ('deed.guile', 'deed.wilds', 'deed.influence'):
    v = []
    for sd in range(1, 101):
        eng, log = run('A', seed=sd, sessions=20)
        v.append((eng.weighted['deed.martial'], eng.weighted[other]))
    print('A s20 martial vs', other, 'median ratio other/martial =', round(statistics.median(o/m for m, o in v), 2),
          'median other', statistics.median(o for m, o in v))
