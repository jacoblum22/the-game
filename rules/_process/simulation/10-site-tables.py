"""10-site-tables.py -- I-022 and PR-10-10: every site theme x domain pair has its own denizen pool
(sites.yaml#denizen_pools), and PR-10-10 builds a threat sub-table from it at every site band 1-5 that passes
PR-10-8 (10.10.2). Seeded and deterministic: one RNG (seed 1022) drives every draw, in a fixed order.

For each pair: the pool is sites.yaml#denizen_pools (the theme gate x the domain terrain, weighted by the theme's
creature_weights); the fallback pool is the theme gate alone (10.13.13). Reports: the pool size, for each band the
number of slots filled from the pool / the fallback / the nearest band, and the PR-10-8 result.
Output: 10-site-tables-output.txt (this script's stdout). Exit 1 on any failure.
"""
import os, sys, random, importlib.util
from collections import Counter
import yaml
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("tb10", os.path.join(HERE, "10_table_builder.py"))
TB = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(TB)
WA = TB.WA
DATA = WA.DATA
SITES = yaml.safe_load(open(os.path.join(DATA, "sites.yaml"), encoding="utf-8"))
ARCHS = {a["id"]: a for a in yaml.safe_load(open(os.path.join(DATA, "archetypes.yaml"), encoding="utf-8"))["archetypes"]}

def anc(t, g):
    return t == g or t.startswith(g + ".")

def theme_weight(th, a):
    best, depth = 1, -1
    for g, w in th["creature_weights"].items():
        for c in a["creature_tags"]:
            if anc(c, g) and g.count(".") > depth:
                best, depth = w, g.count(".")
    return best

def theme_gate(th):
    return {aid: theme_weight(th, a) for aid, a in ARCHS.items()
            if any(anc(c, g) for c in a["creature_tags"] for g in th["creature_gate_tags"])}

rng = random.Random(1022)
fails = 0
tot = Counter()
pools = {(p["theme"], p["domain"]): p for p in SITES["denizen_pools"]}
print("PR-10-10 on every site theme x domain pair at every band (seed 1022)")
print("pair | pool size | per band: slots from pool/fallback/nearest, PR-10-8 word mix, pass")
for th in SITES["site_themes"]:
    for dm in SITES["site_domains"]:
        entry = pools[(th["id"], dm["id"])]
        pool = {r["ref"]: r["weight"] for r in entry["archetypes"]}
        fb = theme_gate(th)
        cells = []
        for band in range(1, 6):
            rows, log = TB.build_threat_table(pool, band, rng, fallback_pool=fb)
            ok, summ, f, _ = WA.audit_table(rows, band)
            src = Counter(x[6] for x in log)
            tot.update(src)
            tot["tables"] += 1
            tot["pass"] += ok
            if not ok:
                fails += 1
                print("  FAIL %s x %s band %d: %s" % (th["id"], dm["id"], band, f))
            cells.append("b%d %d/%d/%d %s%s" % (band, src["pool"], src["fallback"], src["nearest band"],
                         "".join("%s%d" % (k[0], v) for k, v in sorted(summ["words"].items(), key=lambda kv: WA.WORDS.index(kv[0]))),
                         "" if ok else " FAIL"))
        print("%-26s x %-24s %2d | %s" % (th["id"].split(".")[-1], dm["id"].split(".")[-1], len(pool), " | ".join(cells)))
print()
print("tables built: %d | PR-10-8 pass: %d | slots: pool %d, fallback (theme gate) %d, nearest band %d" %
      (tot["tables"], tot["pass"], tot["pool"], tot["fallback"], tot["nearest band"]))
print("word letters: t trivial, e easy, f fair, h hard, l lethal (faces of 20)")
sys.exit(1 if fails else 0)
