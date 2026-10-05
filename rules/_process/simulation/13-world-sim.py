"""13-world-sim.py -- re-runs chapter 11's World Turn simulation (11-world-sim.py, its run() VERBATIM) with the
Thallen March's real factions from _process/merged-contrib/factions.13.yaml (owner-block '13' of data/factions.yaml),
and adds a starting-state projection.

What is substituted into 11's run() (nothing else changes):
  - the four illustrative factions -> the region's FULL factions at their data tier, hold, ratings, temperament,
    stage, first goal (scope, kind) and starting goal fill; relations from data (the sim's 'enemy' test is rel <= -2);
  - the three illustrative minors -> the region's PETTY factions, each a 6-segment clock at its data start
    (11's minor model: d6 a week, 4-5 +1, 6 +2);
  - the PC's side: helps the Bellwardens, opposes the Hushed Choir; thread sponsors drawn from the region's factions;
  - 11.3.7's 'steadfast' row (1 recover if weak, 2 aid_pc -> goal in the sim, 3 strike at -3 -> strike, 4-6 goal);
    11-world-sim.py carries the same row since integration (I-026), so setting it here changes nothing.
Targets (OEQ-11-2 / T-11-GOALS): 1.5-3.5 goal completions per faction per year; <= 10% of factions at tier 5 after
two years. Usage: python 13-world-sim.py [seeds] [--rule-cap]
(--rule-cap is accepted for old command lines and changes nothing: since integration, I-026, 11-world-sim.py's
gain_hold() applies 11.3.4 itself.)
"""
import importlib.util
import os
import random
import statistics
import sys
from collections import Counter

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "data"))
SEEDS = int([a for a in sys.argv[1:] if a.isdigit()][0]) if any(a.isdigit() for a in sys.argv[1:]) else 300

src = open(os.path.join(HERE, "11-world-sim.py"), encoding="utf-8").read()
src = src.split("if __name__ == '__main__':")[0]
a = src.index("    facs = [Faction('salt_guild'")
b = src.index("    seeded = []")
src = src[:a] + "    facs, minors = _build_13(rng)\n    pc_side = {'fac.thallen.bellwardens': 1, 'fac.thallen.hushed_choir': -1}\n" + src[b:]
for old, new in (("fac = rng.choice(['ash_wardens', 'margrave', None, None])", "fac = rng.choice(['fac.thallen.bellwardens', 'fac.thallen.vantry', None, None])"),
                 ("against = rng.choice(['ember_cult', 'salt_guild', None])", "against = rng.choice(['fac.thallen.hushed_choir', 'fac.thallen.pell_company', None])"),
                 ("war = (scenario == 'war' and f.id == 'ember_cult')", "war = (scenario == 'war' and f.id == 'fac.thallen.hushed_choir')"),
                 ("        # step 6 attention\n", "        _snap(week, facs)\n        # step 6 attention\n")):
    if old not in src:
        raise SystemExit("11-world-sim.py changed; substitution not found: " + old)
    src = src.replace(old, new)

RULE_CAP = "--rule-cap" in sys.argv  # a no-op since integration (I-026): 11.3.4 is native in 11-world-sim.py
if "gain_hold(f, stats, realm_grow=(scope == 'realm'))" not in src or "realm_grow and f.tier < 5" not in src:
    raise SystemExit("11-world-sim.py changed: 11.3.4's realm-grow cap not found in gain_hold() or its goal-completion call")
FAC = yaml.safe_load(open(os.path.join(DATA, "..", "_process", "merged-contrib", "factions.13.yaml"), encoding="utf-8"))["blocks"][0]["entries"]
FULL = [f for f in FAC if f["full"]]
PETTY = [f for f in FAC if not f["full"]]
SNAPS = []


def _build_13(rng):
    ns = G
    facs = []
    for f in FULL:
        x = ns["Faction"](f["id"], f["tier"], f["ratings"], f["temperament"], f["lifecycle_stage"])
        x.hold = 1 if f["hold"] == "strong" else 0
        x.goal = (f["goal"]["scope"], f["goal"]["kind"])
        x.filled = f["goal"]["clock"]["filled"]
        facs.append(x)
    ids = {x.id for x in facs}
    for x, f in zip(facs, FULL):
        for g in facs:
            if g is not x:
                x.rel[g.id] = f["relations"].get(g.id, 0)
    minors = [{"filled": f["goal"]["clock"]["filled"]} for f in PETTY]
    SNAPS.append({})
    return facs, minors


def _snap(week, facs):
    d = SNAPS[-1]
    for f in facs:
        d.setdefault(f.id, []).append((f.filled, f.completions, f.tier))


G = {"__name__": "world11_for_13", "_build_13": _build_13, "_snap": _snap}
sys.argv = [sys.argv[0]] + [a for a in sys.argv[1:] if a.isdigit()]  # 11's module code reads argv[1] as its seed count
exec(compile(src, "11-world-sim.py (run verbatim, factions substituted)", "exec"), G)
G["AGENDA"]["steadfast"] = {1: "recover", 2: "goal", 3: "strike", 4: "goal", 5: "goal", 6: "goal"}
run, q = G["run"], G["q"]

print("rule cap (11.3.4): native in 11-world-sim.py (integration, I-026)%s" % ("; --rule-cap given (no-op)" if RULE_CAP else ""))
print("Thallen March factions in the sim: full %s; petty %d" % ([f["id"].split(".")[-1] for f in FULL], len(PETTY)))
for scenario in ("engaged", "war", "absent"):
    SNAPS.clear()
    runs = [run(s, scenario) for s in range(SEEDS)]
    print("=== scenario: %s (%d seeds x 104 weeks) ===" % (scenario, SEEDS))
    for k in ("goal_done", "tier_up", "tier_down", "collapses", "strikes", "strike_hits", "slips", "hooks_seeded", "threads_completed",
              "threads_failed", "situations", "max_known_hooks", "weeks_known_lt3", "entanglements"):
        print("  %-18s p10/med/p90 %s" % (k, q([r[k] for r in runs])))
    comp = [c for r in runs for c in r["completions_by_fac"]]
    per_year = [c / 2.0 for c in comp]
    print("  goal completions per faction per YEAR: p10/med/p90 %s mean %.2f (target 1.5-3.5)" % (q(per_year), statistics.mean(per_year)))
    for i, f in enumerate(FULL):
        cs = [r["completions_by_fac"][i] / 2.0 for r in runs]
        print("     %-32s per year mean %.2f median %.1f" % (f["id"], statistics.mean(cs), statistics.median(cs)))
    tiers = [t for r in runs for t in r["final_tiers"]]
    c = Counter(tiers)
    print("  final tiers after 2 years: %s; at tier 5: %.1f%% (target <= 10%%)" % (sorted(c.items()), 100.0 * c[5] / len(tiers)))
    # the starting-state projection: the Choir's goal clock (the Last Bell's countdown) with no PC interference
    ch = [s.get("fac.thallen.hushed_choir", []) for s in SNAPS]
    def first_done(series):
        for wk, (filled, done, tier) in enumerate(series, 1):
            if done >= 1:
                return wk
        return 999
    wk_done = [first_done(s) for s in ch]
    print("  Choir (Last Bell silent): week of first completion p10/med/p90 %s; done by week 4: %.0f%%, by week 13: %.0f%%, by week 26: %.0f%%" % (
        q(wk_done), 100.0 * sum(w <= 4 for w in wk_done) / len(wk_done), 100.0 * sum(w <= 13 for w in wk_done) / len(wk_done), 100.0 * sum(w <= 26 for w in wk_done) / len(wk_done)))
    for fid in ("fac.thallen.vantry", "fac.thallen.bellwardens", "fac.thallen.pell_company", "fac.thallen.hushed_choir"):
        at4 = [s[fid][3][0] + 0 for s in SNAPS if fid in s and len(s[fid]) > 3]
        done4 = [s[fid][3][1] for s in SNAPS if fid in s and len(s[fid]) > 3]
        print("     week 4: %-28s goal fill median %s (p10 %s, p90 %s); completed by then %.0f%%" % (
            fid, statistics.median(at4), q(at4)[0], q(at4)[2], 100.0 * sum(1 for d in done4 if d) / len(done4)))
