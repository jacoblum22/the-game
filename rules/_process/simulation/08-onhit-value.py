"""08-onhit-value.py -- I-090 [revision C4]: the on-hit property family priced by what a proc is worth.

Chapter 08's on-hit properties (08-gen_data08.py: `onhit_<element>`, Rending, Staggering, Dreadful, Hobbling,
Hunter's) all proc on the same natural d20 range (tier 1: 20 ... tier 5: 16-20) and apply one condition. T-05-9 prices
conditions; 06-conflict-sim.py's section K1 measured that a lingering-harm stack (burning, bleeding) is worth about
0.67 EU for the scene, far below a light-group condition (1 EU, 2 beyond a round). This script:
  1. re-measures K1's lingering-harm values with 06-conflict-sim.py's own engine (imported, unchanged; same harness:
     a 1-Focus spell of the working's severity cast first each turn, plus the condition on a hit; the bearer's best
     answer of never / always / smart; EU = 2 x condition gain / one-rung gain, pooled over bands 1, 3, 5), adding
     2 and 3 stacks;
  2. prints the family's EU per proc and expected EU per hit at each tier, before and after I-090 (lingering-harm
     on-hit properties apply 2 stacks at tiers 1-3 and 3 stacks, the maximum, at tiers 4-5).
Usage: python 08-onhit-value.py [runs]   (default 6000 fights per cell; seeded; output 08-onhit-value-output.txt)
"""
import os, sys, random

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 6000
_argv = sys.argv
sys.argv = ["06-conflict-sim.py", str(RUNS)]
G = {"__file__": os.path.join(HERE, "06-conflict-sim.py"), "__name__": "conflict06"}
exec(compile(open(os.path.join(HERE, "06-conflict-sim.py"), encoding="utf-8").read(), "06-conflict-sim.py", "exec"), G)
sys.argv = _argv
fight, Foe, CASTER, BRANCH, WORK_SEV = G["fight"], G["Foe"], G["CASTER"], G["BRANCH"], G["WORK_SEV"]

lines = []
def P(*a):
    s = " ".join(str(x) for x in a); lines.append(s); print(s)

KM = {1: (("1xT3", lambda: [Foe(3)]), ("2xT2", lambda: [Foe(2), Foe(2)])),
      3: (("1xT4", lambda: [Foe(4)]), ("2xT3", lambda: [Foe(3), Foe(3)])),
      5: (("1xT5", lambda: [Foe(5)]), ("2xT4", lambda: [Foe(4), Foe(4)]))}
KC = [("%s x%d, scene" % (c, n), [("cond." + c, n, None)]) for c in ("bleeding", "burning") for n in (1, 2, 3)]

def winp(pband, mk, **kw):
    rng = random.Random(606)
    res = [fight(rng, pband, mk(), **kw) for _ in range(RUNS)]
    return 100.0 * sum(r['won'] for r in res) / len(res)

P("=== I-090: on-hit lingering harm priced (06-conflict-sim.py engine, %d fights a cell, seed 606) ===" % RUNS)
rung_gain, gain = 0.0, {n: 0.0 for n, _ in KC}
bw = BRANCH['arcane Force Bolt']
for b, ms in KM.items():
    sw = WORK_SEV[b]
    for lab, mk in ms:
        kw = dict(pc_over=CASTER[b], use_focus=True)
        base = winp(b, mk, caster=dict(sev=sw, spell=dict(cost=1, sev=sw), **bw), **kw)
        rung = winp(b, mk, caster=dict(sev=sw, spell=dict(cost=1, sev=min(5, sw + 1)), **bw), **kw)
        rung_gain += rung - base
        for n, cs in KC:
            by = [winp(b, mk, caster=dict(sev=sw, spell=dict(cost=1, sev=sw, conds=cs), **bw), bearer=pol, **kw)
                  for pol in ('never', 'always', 'smart')]
            gain[n] += min(by) - base
EU = {n: 2 * gain[n] / rung_gain for n, _ in KC}
P("pooled one-rung gain %.1f win points (= 2 EU)" % rung_gain)
for n, _ in KC:
    P("  %-20s %.2f EU" % (n, EU[n]))

# the family, priced per proc: T-05-9 units for the control conditions (light 1, +1 beyond a round; middle 2, +1),
# the measured value for lingering harm (the mean of bleeding and burning at that stack count)
ling = {k: (EU["bleeding x%d, scene" % k] + EU["burning x%d, scene" % k]) / 2 for k in (1, 2, 3)}
CHANCE = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}          # faces of the d20 (20; 19-20; ... 16-20)
FAM = [("Staggering (off_balance, 1 round)", lambda t: 1.0),
       ("Hunter's / Hobbling / Rime / Dream / Spell (light, 2 rounds or scene)", lambda t: 2.0),
       ("Dreadful / Thunder / Acid / Venom / Grave / Dawn (middle, 2 rounds or scene)", lambda t: 3.0),
       ("Rending / Ember-touched before I-090 (1 stack)", lambda t: ling[1]),
       ("Rending / Ember-touched after I-090 (2 stacks; 3 at tiers 4-5)", lambda t: ling[2] if t <= 3 else ling[3])]
P()
P("on-hit family: EU per proc; expected EU per hit at tiers 1 / 3 / 5 (proc chance 5% / 15% / 25% of hits)")
for nm, f in FAM:
    P("  %-82s %.2f / %.2f / %.2f per proc; per hit %.3f / %.3f / %.3f" % (
        nm, f(1), f(3), f(5), f(1) * CHANCE[1] / 20, f(3) * CHANCE[3] / 20, f(5) * CHANCE[5] / 20))
lo, hi = 1.0, 3.0
after = [ling[2], ling[3]]
P()
P("check: after I-090 the lingering-harm members sit inside the family's band (%.1f-%.1f EU a proc): %s" % (
    lo, hi, "PASS" if all(lo <= v <= hi for v in after) else "FAIL"))
with open(os.path.join(HERE, "08-onhit-value-output.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
