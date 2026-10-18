"""Scores a checker run made with `quote` (haiku_check.py): drops problems whose earlier line is not really in the
context, then flat and per-topic cutoffs (the checker's own topics), with leave-one-round-out.
    python evals/autoloop/quote_cutoffs.py sonnet-quote.json   (needs numpy)"""
import json, glob, sys, re, itertools
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
R = Path('evals/autoloop/games/read/causes')
res = json.load(open(R/sys.argv[1], encoding='utf-8'))
found = [json.loads(x) for f in glob.glob(str(R/'*.in.jsonl')) for x in open(f, encoding='utf-8')]
judged = {json.loads(x)["id"]: json.loads(x) for f in glob.glob(str(R/'*.out.jsonl')) for x in open(f, encoding='utf-8') if x.strip()}
fq = defaultdict(list)
for d in found:
    if judged[d["id"]]["valid"] != "no": fq[(d["game"], d["round"])].append(d["quote"])
w = lambda s: set(re.findall(r"[a-z']+", s.lower()))
match = lambda q, qs: any(len(w(q) & w(b)) >= max(2, 0.5 * min(len(w(q)), len(w(b)))) for b in qs)
P_ = [p for x in res for p in x["problems"]]
print(f"{len(P_)} problems; earlier line really there: {sum(p['found'] for p in P_)}; by score:",
      {s: f"{sum(p['found'] for p in P_ if p['severity']==s)}/{sum(p['severity']==s for p in P_)}" for s in range(1, 6)})
print("real (matches a reader finding) among found vs not found, at 2+:",
      [f"{sum(1 for x in res for p in x['problems'] if p['found']==f and p['severity']>=2 and x['label'] and match(p['quote'], fq[(x['game'],x['round'])]))}/{sum(1 for x in res for p in x['problems'] if p['found']==f and p['severity']>=2)}" for f in (True, False)])
y = np.array([x["label"] for x in res]); P, N = y.sum(), (1 - y).sum()
def rnd(keep):
    h = np.array([any(keep(p) for p in x["problems"]) for x in res]); return h[y==1].sum(), h[y==0].sum()
for name, keep in (("2+", lambda p: p["severity"] >= 2), ("3+", lambda p: p["severity"] >= 3),
                   ("2+, line found", lambda p: p["found"] and p["severity"] >= 2), ("3+, line found", lambda p: p["found"] and p["severity"] >= 3)):
    print(f"  {name:20} caught {rnd(keep)[0]}/{P}  flagged clean {rnd(keep)[1]}/{N}")
cats = ["count", "time", "distance", "place", "deeds", "items", "identity", "status", "mechanics"]; cuts = [2, 3, 4, 9]
print("per topic (its own topics), found only: score 1/2/3/4 and share real")
for c in cats:
    ps = [(x, p) for x in res for p in x["problems"] if p["found"] and c in p["topics"]]
    print(f"  {c:9} {len(ps):3}  " + "  ".join(f"s{s}: {sum(p['severity']==s for _,p in ps):2} ({sum(p['severity']==s and x['label'] and match(p['quote'], fq[(x['game'],x['round'])]) for x,p in ps)} real)" for s in (1,2,3,4)))
M = {c: np.zeros((len(cuts), len(res)), bool) for c in cats}
for i, x in enumerate(res):
    for p in x["problems"]:
        if not p["found"]: continue
        for c in p["topics"]:
            for k, cut in enumerate(cuts): M[c][k, i] |= p["severity"] >= cut
idx = np.array(list(itertools.product(range(len(cuts)), repeat=len(cats))), dtype=np.int8)
hits = np.zeros((len(idx), len(res)), bool)
for ci, c in enumerate(cats): hits |= M[c][idx[:, ci]]
TP = hits[:, y == 1].sum(1); FP = hits[:, y == 0].sum(1)
flat = np.array([len(set(r)) == 1 for r in idx])
best = lambda tp, fp, p, n, m=None: int(np.argmax(np.where(m, tp/p - fp/n, -9) if m is not None else tp/p - fp/n))
k = best(TP, FP, P, N); print("fitted per-topic:", TP[k], FP[k], {c: cuts[idx[k, ci]] for ci, c in enumerate(cats)})
for name, mask in (("flat", flat), ("per-topic", None)):
    tp = fp = 0
    for i in range(len(res)):
        h = hits[:, i]; k = best(TP - h*y[i], FP - h*(1-y[i]), P - y[i], N - (1-y[i]), mask)
        if h[k]: tp += y[i]; fp += 1 - y[i]
    print(f"  leave-one-out {name}, line found: caught {tp}/{P}, flagged clean {fp}/{N}")
