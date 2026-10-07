"""10-light-reference-check.py -- [revision: I-040] backs PR-10-8 step 2's second (light) reference PC.

Question (I-040, verification-1 playtest): the generic and world-seed encounter tables were audited only against
the band's martial reference PC (T-06-12: Guard 14, attack +5, armor 1). Three of the four ready-made characters
(healer, talker, sneak) have Guard 10-12 and no armor. How often does a home-band-1 row rated fair or easier
take such a character to 0 Vitality, before and after the I-040 fix (light reference at home band 1, home-band
crowds 6-8 -> 5-7)?

Method: the extended Monte Carlo fight of 09_core.py (fight(), seeded, 4,000 runs a row) and PR-09-4's estimator
(09_core.estimate) side by side, for
  A. the playtest's case: 7 reptile-folk minions (band 1) against the light PC and the martial reference;
  B. every home-band row of the generic tables at home band 1, with its old (6-8) and new count, at the middle
     face, counter held (PR-10-8 step 2).
Light PC (travel.yaml#encounter_audit_reference.light): attack +5 (the branch working, 05.7.11, modelled as a
weapon whose harm armor reduces: the conservative case), S2, Guard 10, Vitality 12, armor 0, tempo +2.
Output: 10-light-reference-check-output.txt. Seed 4040; deterministic.
"""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location("wa", os.path.join(HERE, "10-word-audit.py"))
WA = importlib.util.module_from_spec(_s); _argv = sys.argv; sys.argv = [sys.argv[0]]; _s.loader.exec_module(WA); sys.argv = _argv
C = WA.C
LIGHT = dict(WA.LIGHT[1], fend=True, focus=0)
REF = C.pc_line(1)
RUNS, SEED = 4000, 4040

def mc(pc, foes):
    fl = [dict(f, taken=1.0, regen=0) for f in foes]
    w, s, r, lost = C.simulate(pc, lambda: [C.Foe(x, members=x.get("members", 1), leader=x.get("leader", False)) for x in fl], runs=RUNS, seed=SEED)
    return w, s

def est(pc, foes):
    fl = [dict(f, taken=1.0, regen=0) for f in foes]
    w, s, _ = C.estimate(pc, fl)
    return w, s, C.classify_sim(w, s)

print("A. the playtest's row: reptile-folk minions, band 1, a mob (members ->  MC win / Staggered %, estimator win / Staggered % word)")
for n in (5, 6, 7):
    foes = [WA.line("arch.lizardfolk", 1, "minion", members=n)]
    for lab, pc in (("light (Guard 10)", LIGHT), ("martial reference (Guard 14)", REF)):
        w, s = mc(pc, foes); ew, es, wd = est(pc, foes)
        print("   %d members vs %-30s MC %5.1f / %5.1f   est %5.1f / %5.1f %s" % (n, lab, w, s, ew, es, wd))

print()
print("B. generic tables, home band 1, home-band crowd rows: old count 6-8 (mid 7) and new 5-7 (mid 6), light PC")
import yaml
src = open(os.path.join(HERE, "10_data_enc.py"), encoding="utf-8").read()
ns = {}; exec(src, ns)
worst_old = worst_new = 0.0
for terr, per in ns["ENC"].items():
    for r in per[1]:
        if r["band"] != "home" or r["variant"] != "minion":
            continue
        arch = r["ref"][0]
        lo, hi = map(int, r["count"].split("-"))
        new_mid = (lo + hi) // 2
        out = []
        for lab, n in (("old", 7), ("new", new_mid)):
            foes = [WA.line(arch, 1, "minion", members=n)]
            w, s = mc(LIGHT, foes); ew, es, wd = est(LIGHT, foes)
            out.append("%s %d: MC %5.1f/%5.1f est %-6s" % (lab, n, w, s, wd))
            if lab == "old": worst_old = max(worst_old, s)
            else: worst_new = max(worst_new, s)
        print("   %-20s %-20s %s" % (terr, arch, " | ".join(out)))
print()
print("worst chance a light PC is Staggered (reduced to 0 Vitality) by one home-band-1 crowd row: old %.1f%%, new %.1f%%" % (worst_old, worst_new))
