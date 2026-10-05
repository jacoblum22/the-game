# craft08.py -- crafting project race: progress (4/6/8/12, delivered reach) vs spoilage (4, U(S2)=1 on failure, U(S3)=2 on crit fail)
# degree rule per 00.3.10 (crit bands +-10, nat20 up, nat1 down); near miss (margin -1..-3) is taken as success-at-cost (reach Standard, cost.time: no spoilage)
import random, statistics
def degree(mod, dc, d):
    t = d + mod; m = t - dc
    if m >= 10: g = 3
    elif m >= 0: g = 2
    elif m > -10: g = 1
    else: g = 0
    if d == 20: g = min(3, g + 1)
    if d == 1: g = max(0, g - 1)
    near = (g == 1 and m >= -3)
    return g, near
def run(mod, dc, seg, reach=2, n=20000, seed=1, sp=4):
    rng = random.Random(seed); wins = 0; steps = []; flawed = 0; greater = 0
    for _ in range(n):
        p = s = 0; k = 0; crit_fail = False; last = None
        while p < seg and s < sp:
            k += 1; d = rng.randint(1, 20); g, near = degree(mod, dc, d)
            if g == 3: p += reach + 1; last = 3
            elif g == 2: p += reach; last = 2
            elif near: p += reach; last = 2
            elif g == 1: s += 1
            else: s += 2; crit_fail = True
        if p >= seg:
            wins += 1; steps.append(k)
            if s >= sp - 1: flawed += 1
            if last == 3: greater += 1
    return wins / n, statistics.mean(steps) if steps else None, flawed / max(1, wins), greater / max(1, wins)
print("spoilage clock: 4 (6 for wondrous); Flawed = completes with spoilage at its last-but-one segment or later")
print("target   seg DC  mod  complete%  mean_steps  flawed%_of_made  greater%_of_made")
for name, seg, dc in [("common", 4, 10), ("fine", 6, 15), ("masterwork", 8, 20), ("wondrous", 12, 25)]:
    for mod in [3, 5, 7, 9, 11, 13, 15]:
        w, st, fl, gr = run(mod, dc, seg, sp=(6 if seg == 12 else 4))
        print(f"{name:10s} {seg:3d} {dc:3d} {mod:+4d}   {100*w:6.1f}    {st if st is None else round(st,1):>6}     {100*fl:6.1f}      {100*gr:6.1f}")

print("with a recipe (Amplifying lever: framed reach Great = 3 ticks per success):")
for name, seg, dc in [("masterwork", 8, 20), ("wondrous", 12, 25)]:
    for mod in [7, 9, 11, 13]:
        w, st, fl, gr = run(mod, dc, seg, reach=3, sp=(6 if seg == 12 else 4))
        print(f"{name:10s} {seg:3d} {dc:3d} {mod:+4d}   {100*w:6.1f}    {round(st,1):>6}     {100*fl:6.1f}      {100*gr:6.1f}")
