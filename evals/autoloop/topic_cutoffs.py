"""Per-topic severity cutoffs for the checker (Jake, 2026-10-18). Topics are hand labels of every problem in
sonnet-five.json (games/read/causes/topics-hand.txt; a problem can have two). Searches every cutoff per topic, and
checks the choice with leave-one-round-out.
    python evals/autoloop/topic_cutoffs.py evals/autoloop/games/read/causes/topics-hand.txt   (needs numpy)"""
import json, glob, sys, re, itertools
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
R = Path('evals/autoloop/games/read/causes')
NAMES = dict(C="count", T="time", D="distance", P="place", A="deeds", I="items", N="identity", S="status", M="mechanics")
lab = {l.split()[0]: l.split()[1].split(',') for l in open(sys.argv[1], encoding='utf-8') if l.strip()}
five = json.load(open(R/'sonnet-five.json', encoding='utf-8'))
found = [json.loads(x) for f in glob.glob(str(R/'*.in.jsonl')) for x in open(f, encoding='utf-8')]
judged = {json.loads(x)["id"]: json.loads(x) for f in glob.glob(str(R/'*.out.jsonl')) for x in open(f, encoding='utf-8') if x.strip()}
fq = defaultdict(list)
for d in found:
    if judged[d["id"]]["valid"] != "no": fq[(d["game"], d["round"])].append(d["quote"])
w = lambda s: set(re.findall(r"[a-z']+", s.lower()))
def match(q, quotes):
    a = w(q)
    return any(len(a & w(b)) >= max(2, 0.5 * min(len(a), len(w(b)))) for b in quotes)
multi = sum(len(v) > 1 for v in lab.values())
print(f"{len(lab)} problems, {multi} with two topics")
# per topic: severity spread, and how often a problem is the readers' finding
print("\nPer topic: problems; severity 1/2/3/4; share that match a reader's finding at each severity")
rows = defaultdict(lambda: defaultdict(lambda: [0, 0]))
for i, x in enumerate(five):
    for j, p in enumerate(x["problems"]):
        hit = x["label"] == 1 and match(p["quote"], fq[(x["game"], x["round"])])
        for c in lab[f"{i}:{j}"]:
            rows[c][p["severity"]][0] += 1; rows[c][p["severity"]][1] += hit
for c in sorted(rows, key=lambda c: -sum(v[0] for v in rows[c].values())):
    r = rows[c]; n = sum(v[0] for v in r.values())
    print(f"  {NAMES[c]:9} {n:3}   " + "   ".join(f"sev{s}: {r[s][0]:3} ({r[s][1]/r[s][0]:.0%} real)" if r[s][0] else f"sev{s}:   -        " for s in (1, 2, 3, 4)))
# round masks per topic and cutoff; a problem counts for every topic it has
cats = list(NAMES); cuts = [2, 3, 4, 9]
y = np.array([x["label"] for x in five]); P, Nn = y.sum(), (1 - y).sum()
M = {c: np.zeros((len(cuts), len(five)), bool) for c in cats}
for i, x in enumerate(five):
    for j, p in enumerate(x["problems"]):
        for c in lab[f"{i}:{j}"]:
            for k, cut in enumerate(cuts): M[c][k, i] |= p["severity"] >= cut
idx = np.array(list(itertools.product(range(len(cuts)), repeat=len(cats))), dtype=np.int8)
hits = np.zeros((len(idx), len(five)), bool)
for ci, c in enumerate(cats): hits |= M[c][idx[:, ci]]
TP = hits[:, y == 1].sum(1); FP = hits[:, y == 0].sum(1)
def best(tp, fp, p, n, mask=None):
    s = tp / p - fp / n
    if mask is not None: s = np.where(mask, s, -9)
    return int(np.argmax(s))
flat = np.array([len(set(r)) == 1 for r in idx])
def show(name, k): print(f"  {name:48} caught {TP[k]}/{P}  flagged clean {FP[k]}/{Nn}  " + ("" if flat[k] else ", ".join(f"{NAMES[c]} {'never' if cuts[idx[k, ci]] == 9 else str(cuts[idx[k, ci]]) + '+'}" for ci, c in enumerate(cats))))
print("\nOn all rounds (fitted on the same rounds):")
for cut in (0, 1): show(f"flat {cuts[cut]}+", int(np.where(flat & (idx[:, 0] == cut))[0][0]))
show("best per-topic cutoffs", best(TP, FP, P, Nn))
# leave one round out: choose cutoffs on the other 164 rounds, then score the held-out round
for name, mask in (("flat cutoff", flat), ("per-topic cutoffs", None)):
    tp = fp = 0; picks = Counter()
    for i in range(len(five)):
        h = hits[:, i]
        k = best(TP - h * y[i], FP - h * (1 - y[i]), P - y[i], Nn - (1 - y[i]), mask)
        picks[tuple(idx[k])] += 1
        if h[k]: tp += y[i]; fp += 1 - y[i]
    print(f"\nLeave-one-out, {name}: caught {tp}/{P}, flagged clean {fp}/{Nn}; {len(picks)} different rules chosen across the 165 folds")
# stricter: a contradiction round counts as caught only if a kept problem is the readers' finding
rule = dict(C=2, T=4, D=3, P=2, A=3, I=2, N=3, S=2, M=2)
for name, keep in (("flat 3+", lambda cs, s: s >= 3), ("per-topic rule", lambda cs, s: any(s >= rule[c] for c in cs))):
    strict = sum(any(keep(lab[f"{i}:{j}"], p["severity"]) and match(p["quote"], fq[(x["game"], x["round"])]) for j, p in enumerate(x["problems"])) for i, x in enumerate(five) if x["label"])
    print(f"  {name}: {strict}/105 caught on the right line")
kept = [(lab[f"{i}:{j}"], p) for i, x in enumerate(five) for j, p in enumerate(x["problems"]) if any(p["severity"] >= rule[c] for c in lab[f"{i}:{j}"])]
dm = [p for cs, p in kept if set(cs) & {"T", "I", "M"}]
print(f"  kept {len(kept)} problems; {len(dm)} touch time/items/mechanics -> DM; checker itself said dm for {sum(p['fix']=='dm' for cs,p in kept)}")
