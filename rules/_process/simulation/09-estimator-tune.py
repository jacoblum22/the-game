#!/usr/bin/env python3
"""09-estimator-tune.py -- one simulation pass over the advisory battery, then a grid over the estimator's two
calibration constants (the margin past Staggered, in landed blows; and a Vitality offset on the Staggered
test), scoring exact agreement and the direction of misses. Chooses the setting that maximizes exact agreement
subject to gentler misses <= harsher misses (an advisory may err toward warning, never toward leniency: R4 §1)."""
import sys, os, importlib, random, collections, math, yaml
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
C = importlib.import_module("09_core")
RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
ADV = {a["id"]: a for a in yaml.safe_load(open(os.path.join(HERE, "..", "..", "data", "adversaries.yaml"), encoding="utf-8"))["adversaries"]}
def L(a, counter=True):
    x = dict(a["calibration"]["line"]); x["band"] = a["threat_band"]
    x["vit"] = a["vitality"] if isinstance(a["vitality"], int) else a["vitality"]["per_member"]
    x["members"] = a["members"]; x["swarm"] = a["swarm"]; x["leader"] = a["leader"]
    if counter: x["taken"], x["regen"] = 1.0, 0
    return x
rows = []
shapes = [(1, 1), (2, 1), (3, 1), (4, 1), (6, 1), (1, 4), (1, 6), (1, 8)]
for d in (-2, -1, 0, 1):
    for b in range(1, 6):
        e = b + d
        if 1 <= e <= 5:
            for n, m in shapes:
                if d >= 1 and (n > 2 or m > 1): continue
                rows.append((C.pc_line(b), [dict(C.std(e), members=m) for _ in range(n)]))
for a in ADV.values():
    for pb in (a["threat_band"] - 1, a["threat_band"], a["threat_band"] + 1):
        if 1 <= pb <= 5:
            rows.append((C.pc_line(pb), [L(a)]))
            if a.get("advisory_without_counter"): rows.append((C.pc_line(pb), [L(a, False)]))
sims = []
for pc, lines in rows:
    w, s, _, _ = C.simulate(pc, lambda: [C.Foe(x, members=x.get("members", 1), leader=x.get("leader", False)) for x in lines], runs=RUNS)
    sims.append(C.classify_sim(w, s))
W = C.WORDS
best = None
for buf in (1.0, 1.25, 1.5, 1.75, 2.0):
    for voff in (0.0, 0.5, 1.0, 1.5):
        ex = g = h = 0
        for (pc, lines), sw in zip(rows, sims):
            pc2 = dict(pc)
            ew, es, _ = C.estimate(dict(pc2, vit=pc2["vit"]), lines, buffer_hits=buf)
            # Vitality offset applied to the Staggered test only
            if voff:
                _, es2, _ = C.estimate(dict(pc2, vit=pc2["vit"] - voff), lines, buffer_hits=buf + voff / 3.0)
                es = es2
            ew_ = C.classify_sim(ew, es)
            if ew_ == sw: ex += 1
            elif W.index(ew_) < W.index(sw): g += 1
            else: h += 1
        print("buffer %.2f  stagger offset %.1f : exact %d/%d (%.1f%%)  gentler %d  harsher %d" % (buf, voff, ex, len(rows), 100.0 * ex / len(rows), g, h))
        if g <= h and (best is None or ex > best[0]): best = (ex, buf, voff, g, h)
print("chosen:", best)
