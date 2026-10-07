"""10-heart-check.py -- [revision: I-067] 10.13.10's guardian heart, fielded for every theme's climax archetype at
every site band 1-5.

Rule checked (10.13.10 as revised): the climax archetype is fielded at the site band if its `bands` include it, else
at the nearest band it has; the variant steps down PR-10-10's solo ladder (solo -> elite -> standard -> minion) until
PR-09-4's word against the reference PC of the site band (counter held, PR-10-8 step 2) is at most `hard`. The word is
the one the advisory shows before the first beat (09.6.5); `hard` raises 07's danger notice.
Prints, per theme row and site band: fielded band, variant, word (win / Staggered %), and whether the band is out of the
site's (09.6.6's tell). Fails if any guardian cannot be fielded at most hard. Deterministic (no RNG).
Output: 10-heart-check-output.txt.
"""
import os, sys, importlib.util
import yaml
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("tb10", os.path.join(HERE, "10_table_builder.py"))
TB = importlib.util.module_from_spec(_s); _argv = sys.argv; sys.argv = [sys.argv[0]]; _s.loader.exec_module(TB); sys.argv = _argv
WA, ARCH, WORDS = TB.WA, TB.ARCH, TB.WORDS
SITES = yaml.safe_load(open(os.path.join(WA.DATA, "sites.yaml"), encoding="utf-8"))

REF_BY_BAND = {}   # filled from sites.yaml rows (ref_by_band)

def shapes(arch, b):
    """10.13.10's guardian shapes at band b, most dangerous intent first: a solo; an elite leading a mob of five
    minions one band lower (the same band if the archetype has no lower one)."""
    lo, hi = ARCH[arch]["bands"]
    mb = b - 1 if b - 1 >= lo else b
    yield "solo", [WA.line(arch, b, "solo")]
    yield "elite+mob", [WA.line(arch, mb, "minion", members=5), WA.line(arch, b, "elite", leader=True)]
    for v in ("elite", "standard", "minion"):
        yield v, [WA.line(arch, b, v)]

def field_heart(arch, band):
    """The first two shapes are compared: the more dangerous one whose word is at most hard (tie: the solo);
    if neither is, step down elite -> standard -> minion."""
    best = None
    for i, (v, foes) in enumerate(shapes(arch, band)):
        wd, win, stag = WA.word(band, foes)
        ok = WORDS.index(wd) <= WORDS.index("hard")
        if i < 2:
            if ok and (best is None or WORDS.index(wd) > WORDS.index(best[1]) or (WORDS.index(wd) == WORDS.index(best[1]) and win < best[2])):
                best = (v, wd, win, stag)
            if i == 1 and best:
                return best
        elif ok:
            return (v, wd, win, stag)
    return (None, wd, win, stag)

fails = 0; tally = {}
print("theme / climax face / archetype (bands) | per site band 1-5: fielded band, variant, word win/stag")
for th in SITES["site_themes"]:
    for r in th["climax"]:
        if r.get("kind") != "guardian" or not r.get("ref"):
            continue
        a0 = r["ref"]; lo, hi = ARCH[a0]["bands"]
        cells = []
        for band in range(1, 6):
            a = a0 if lo <= band <= hi else (r.get("ref_by_band") or {}).get(band)
            if a is None or not ARCH[a]["bands"][0] <= band <= ARCH[a]["bands"][1]:
                fails += 1; cells.append("b%d NO ARCHETYPE" % band); continue
            v, wd, win, stag = field_heart(a, band)
            if v is None:
                fails += 1
            tally[(v, wd)] = tally.get((v, wd), 0) + 1
            cells.append("%s%s %s %.0f/%.0f" % ("" if a == a0 else a[5:] + " ", v or "NONE", wd, win, stag))
        print("  %-10s d6 %s %-18s (%d-%d) | %s" % (th["id"].split(".")[-1], r["range"], a0, lo, hi, " | ".join(cells)))
print()
print("a named archetype before a cell = the row's ref_by_band for that band (the climax archetype is not fielded there)")
print("variant/word tally over theme rows x 5 bands:", sorted(((k[0] or "NONE", k[1]), n) for k, n in tally.items()))
print("guardians that cannot be fielded at most hard:", fails)
sys.exit(1 if fails else 0)
