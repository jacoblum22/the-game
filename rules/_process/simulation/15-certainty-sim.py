"""I-048 / I-074: how often 15.3.10 makes a request certain (no roll, no evidence), before and after.
Seeded (seed 48). A request stream drawn from an assumed play mix (stated below); two player policies:
'honest' (terms as they come) and 'optimizer' (always brings two terms).
OLD 15.3.10: effective = size - terms (min R1); certain if (eff R1 and standing >= Neutral) or eff <= ceiling-2,
  and no covering refusal, and no cited hesitation reason (watcher, superior, fear).
NEW: (I-048) for certainty only one term counts; (I-074) a request that defeats a recorded want counts one rung
  higher (15.3.2) and the want is a hesitation reason (never certain).
Ceilings (social.yaml#standing_effects): Wary R1, Neutral R2, Warm R3, Friendly R4, Devoted R5."""
import random
CEIL = {"Wary": 1, "Neutral": 2, "Warm": 3, "Friendly": 4, "Devoted": 5}
STAND = [("Wary", .15), ("Neutral", .40), ("Warm", .25), ("Friendly", .15), ("Devoted", .05)]
SIZE = [(1, .30), (2, .35), (3, .20), (4, .10), (5, .05)]
TERMS = [(0, .40), (1, .40), (2, .20)]
P_HES, P_REF, P_WANT = .20, .10, .10
def pick(rng, tab):
    r = rng.random(); a = 0
    for v, p in tab:
        a += p
        if r < a: return v
    return tab[-1][0]
def certain(st, size, terms, hes, ref, defeats, rule):
    c = CEIL[st]
    if rule == "new" and defeats: size += 1
    t = terms if rule == "old" else min(terms, 1)
    eff = max(1, size - t)
    if ref or hes or (rule == "new" and defeats): return False, eff
    ok = (eff == 1 and st != "Wary") or eff <= c - 2
    return ok, eff
def run(rule, policy, n=200000, seed=48):
    rng = random.Random(seed)
    cnt = {"all": [0, 0], "R3+": [0, 0], "defeats": [0, 0]}
    for _ in range(n):
        st = pick(rng, STAND); size = pick(rng, SIZE)
        terms = 2 if policy == "optimizer" else pick(rng, TERMS)
        hes = rng.random() < P_HES; ref = rng.random() < P_REF; d = rng.random() < P_WANT
        ok, _ = certain(st, size, terms, hes, ref, d, rule)
        for k, cond in (("all", True), ("R3+", size >= 3), ("defeats", d)):
            if cond: cnt[k][1] += 1; cnt[k][0] += ok
    return {k: 100.0 * a / b for k, (a, b) in cnt.items()}
print(__doc__.splitlines()[0])
print("mix: standing", STAND, "size", SIZE, "terms", TERMS, "hesitation %.2f refusal %.2f defeats-want %.2f" % (P_HES, P_REF, P_WANT))
print("policy     rule | certain % of all | of R3+ requests | of want-defeating requests")
for policy in ("honest", "optimizer"):
    for rule in ("old", "new"):
        r = run(rule, policy)
        print("%-9s  %-4s | %5.1f | %5.1f | %5.1f" % (policy, rule, r["all"], r["R3+"], r["defeats"]))
print("Per cell (no hesitation/refusal), certain? old/new:")
for st in CEIL:
    row = []
    for size in range(1, 6):
        row.append("R%d:%s" % (size, "".join("Y" if certain(st, size, t, 0, 0, 0, rule)[0] else "." for rule in ("old", "new") for t in (0, 1, 2))))
    print("  %-8s" % st, " ".join(row), " (old t0 t1 t2 | new t0 t1 t2)")
