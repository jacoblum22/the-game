#!/usr/bin/env python3
"""09-i005-check.py -- issue I-005: chapter 04's pacing simulation assumed conflicts drawn from the PC's band to
band+2 (tiers [b, b+1, b+1, b+2], mean +1). Chapter 09's encounter budget (09.8.1, T-09-10) fields fights mostly at
or below the PC's band: Delta -1 / 0 / +1 / +2 = 30 / 55 / 15 / 0 percent (a band+2 foe is lethal and telegraphed,
09.6.6, so it is avoided or parleyed, not fought). This re-runs 04's R1 pacing rows with that distribution and
with 04's original one, side by side. Deterministic (04's seeds)."""
import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "04-recog04.py"), encoding="utf-8").read()
src = src[:src.index("if __name__ == '__main__':")]
old = "tier = conflict_tier(rng, band)\n                stakes"   # 04-recog04.py's default since revision I-034
assert old in src
new = ("tier = max(1, min(5, rng.choice(DIST) if DIST else rng.choice([band, band + 1, band + 1, band + 2]) - 0))\n"
       "                if DIST: tier = max(1, min(5, band + rng.choice(DIST)))\n                stakes")
src = src.replace(old, new)
ns = {"__name__": "recog04_i005"}
# [revision: I-089] each model is run on two ladders: the one 09.12.3 measured (narrow W 80/200/440/800/1300, x3/4
# fine, x3/2 broad) and 04's current ladder (tiers 2-5 retuned to the advisory-offset model, DL-04-32).
OLD_W = [80, 200, 440, 800, 1300]
for ladder in ("before I-089 (narrow W 80/200/440/800/1300; the numbers 09.12.3 quotes)", "current (04-recog04.py's W)"):
  print("##### ladder:", ladder)
  for label, dist in (("04 original: conflicts at b, b+1, b+1, b+2", None),
                    ("09 budget, challenge = the foe's threat band: b-1 30% / b 55% / b+1 15%", [-1] * 6 + [0] * 11 + [1] * 3),
                    ("09 proposal, challenge = power band + advisory offset (easy -1 25% / fair 0 40% / hard +1 30% / lethal +2 5%)",
                     [-1] * 5 + [0] * 8 + [1] * 6 + [2] * 1)):
    ns = {"__name__": "recog04_i005", "DIST": dist}
    exec(compile(src, "04-recog04", "exec"), ns)
    if ladder.startswith("before"):
        ns["W"].update({"narrow": OLD_W, "fine": [x * 3 // 4 for x in OLD_W], "broad": [x * 3 // 2 for x in OLD_W],
                        "hybrid": [x * 3 // 4 for x in OLD_W]})
        ns["C"].update({k: [v // 10 for v in vs] for k, vs in ns["W"].items()})
    print("===", label)
    for style, key, mk in [(ns["ARCHER"], "deed.martial.archery", None), (ns["PURE"], "deed.martial.blade", ns["CH_SWORD"])]:
        res, pol, confs = ns["tiers_of"](style, [key], mk=mk, seeds=100)
        print("  %-52s %s | T4 / T5 within 60: %d / %d of 100" % (style.name, ns["line"](res),
              sum(1 for x in res[4] if x < 99), sum(1 for x in res[5] if x < 99)))
