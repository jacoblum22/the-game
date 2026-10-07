#!/usr/bin/env python3
"""09-adversary-sim.py -- chapter 09's simulations. Seeded, deterministic. Usage: python 09-adversary-sim.py [runs]

Sections (output: 09-adversary-sim-output.txt; summary: 09-adversary-sim.md):
  A. The standard line: T-06-12 with adversary Fend (06.6.5) and the retuned T4/T5 Vitality (09.3.3).
  B. 06's own script (06-conflict-sim.py, FOE patched to the final standard; its model has no adversary
     Fend) and the extended model (with Fend): the advisory matrix T-06-13 re-run -> T-09-9.
  C. Variants: elite and solo multipliers per band against P(b-1), P(b), P(b+1), with and without Focus.
  D. The estimator (PR-09-4) against the Monte Carlo: every T-06-13 shape, every bestiary adversary alone
     at its band and the bands either side, mixed encounters built from the bestiary, and band-1 PC lines
     of different builds (ch.02's request). Agreement, confusion matrix, direction of every miss.
  E. Chapter 07's ladder (07-harm-sim.py's fight07) on the final templates: per 100 lethal-context fights,
     how often the PC reaches the last-chance menu, pooled by the advisory word THIS chapter's estimator
     returns (targets from 07: trivial 0 / easy 1 / fair 5 / hard 26 / lethal 80).
  F. Solo encounter budgets: what each word looks like per PC band (T-09-10).
"""
import collections
import importlib.util
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 3000


def load(name, argv_clear=True):
    s = importlib.util.spec_from_file_location(name.replace("-", "_"), os.path.join(HERE, name + ".py"))
    m = importlib.util.module_from_spec(s)
    a = sys.argv
    if argv_clear:
        sys.argv = [sys.argv[0]]
    s.loader.exec_module(m)
    sys.argv = a
    return m


C = load("09_core")
sim06 = C.sim06
H07 = load("07-harm-sim")
import yaml
ADV = {a["id"]: a for a in yaml.safe_load(open(os.path.join(HERE, "..", "..", "data", "adversaries.yaml"), encoding="utf-8"))["adversaries"]}
W = C.WORDS


def line_of(a, counter=True):
    L = dict(a["calibration"]["line"])
    L["band"] = a["threat_band"]
    L["vit"] = a["vitality"] if isinstance(a["vitality"], int) else a["vitality"]["per_member"]
    L["members"] = a["members"]
    L["swarm"] = a["swarm"]
    L["leader"] = a["leader"]
    if counter:
        L["taken"], L["regen"] = 1.0, 0
    return L


def sim(pc, lines, runs=RUNS, use_focus=False):
    return C.simulate(pc, lambda: [C.Foe(x, members=x.get("members", 1), leader=x.get("leader", False)) for x in lines],
                      runs=runs, use_focus=use_focus)


def word(w, s):
    return C.classify_sim(w, s)


print("runs per row:", RUNS)
# ============================================================================ A
print("\n### A. The standard line (T-09-3): one foe of the PC's band, extended model (adversary Fend at T3+)\n")
print("| Band | atk | Guard | Vit | harm | heavy | red | nerve | tempo | Fend | win% / Stag% / rounds / Vitality lost | word |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for b in range(1, 6):
    s = C.std(b)
    w = sim(C.pc_line(b), [s], runs=max(RUNS, 8000))
    print("| %d | %+d | %d | %d | S%d | %s | %d | %d | %d | %s | %.1f / %.1f / %.1f / %.1f | %s |" % (
        b, s["atk"], s["guard"], s["vit"], s["sev"], "S%d" % s["heavy"] if s["heavy"] else "-", s["red"], s["morale"],
        s["tempo"], "yes" if s["fend"] else "no", w[0], w[1], w[2], w[3], word(w[0], w[1])))
print("\nT-06-12's Vitality 26/40 with Fend (the values replaced):")
for b, v in ((4, 26), (5, 40)):
    w = sim(C.pc_line(b), [C.std(b, vit=v)], runs=max(RUNS, 8000))
    print("  P%d vs T%d Vitality %d: %.1f / %.1f (%s)" % (b, b, v, w[0], w[1], word(w[0], w[1])))

# ============================================================================ B
shapes = [("1 foe", 1, 1), ("2", 2, 1), ("3", 3, 1), ("4", 4, 1), ("6", 6, 1), ("mob of 4", 1, 4), ("mob of 6", 1, 6), ("mob of 8", 1, 8)]
MATRIX = {}
for label, use06 in (("06's script as written (no adversary Fend), FOE = T-09-3", True), ("extended model with adversary Fend (09's contract matrix, T-09-9)", False)):
    print("\n### B. Advisory matrix: %s\n" % label)
    if use06:
        for b in range(1, 6):
            for k in ("atk", "guard", "vit", "sev", "red", "morale", "tempo", "heavy"):
                sim06.FOE[b][k] = C.STANDARD[b][k]
    for d in (-2, -1, 0, 1, 2):
        print("Foe band = PC band %+d\n" % d)
        print("| PC | " + " | ".join(n for n, _, _ in shapes) + " |")
        print("|---|" + "---|" * len(shapes))
        for b in range(1, 6):
            e = b + d
            if e < 1 or e > 5:
                continue
            cells = []
            for name, n, m in shapes:
                if d >= 1 and (n > 2 or m > 1):
                    if n == 3 and m == 1:
                        cells.append("lethal (as T-06-13)")
                    else:
                        cells.append("-")
                    continue
                if use06:
                    rng = random.Random(606)
                    res = [sim06.fight(rng, b, [sim06.Foe(e, members=m) for _ in range(n)]) for _ in range(RUNS)]
                    w = 100.0 * sum(r["won"] for r in res) / len(res)
                    s = 100.0 * sum(r["staggered"] for r in res) / len(res)
                else:
                    w, s, _, _ = sim(C.pc_line(b), [dict(C.std(e), members=m) for _ in range(n)])
                    MATRIX[(b, d, name)] = word(w, s)
                cells.append("%s %d/%d" % (word(w, s), round(w), round(s)))
            print("| P%d (T%d) | " % (b, e) + " | ".join(cells) + " |")
        print()

# ============================================================================ C
print("\n### C. Variants (09.4.6): Vitality multiplier on the solved standard; elite and solo gain Fend; solo a heavy blow\n")
print("| Variant | Band | multiplier | vs P(b-1) | vs P(b) | vs P(b+1) | vs P(b) with a Focus push |")
print("|---|---|---|---|---|---|---|")
NERVE_UP = {4: 6, 6: 8, 8: 8}
for var, mult in (("elite", {1: 2, 2: 2, 3: 2, 4: 1.25, 5: 1.25}), ("solo", {1: 4, 2: 3, 3: 3, 4: 1.75, 5: 1.5})):
    for b in range(1, 6):
        s = C.std(b)
        f = dict(s, fend=True, vit=int(round(s["vit"] * mult[b])), morale=NERVE_UP[s["morale"]])
        if var == "solo":
            f["heavy"] = s["heavy"] or s["sev"] + 1
        cells = []
        for pb in (b - 1, b, b + 1):
            if pb < 1 or pb > 5:
                cells.append("-")
                continue
            w, st, _, _ = sim(C.pc_line(pb), [f])
            cells.append("%s %d/%d" % (word(w, st), round(w), round(st)))
        wf, sf, _, _ = sim(C.pc_line(b), [f], use_focus=True)
        print("| %s | T%d | x%s (Vit %d) | %s | %s | %s | %d/%d |" % (var, b, mult[b], f["vit"], cells[0], cells[1], cells[2], round(wf), round(sf)))

# ============================================================================ D
print("\n### D. The estimator (PR-09-4) against the Monte Carlo\n")
rows = []   # (label, pc, lines, group)
for d in (-2, -1, 0, 1, 2):
    for b in range(1, 6):
        e = b + d
        if e < 1 or e > 5:
            continue
        for name, n, m in shapes:
            if d >= 1 and (n > 2 or m > 1):
                continue
            rows.append(("P%d vs %s T%d" % (b, name, e), C.pc_line(b), [dict(C.std(e), members=m) for _ in range(n)], "matrix"))
for a in ADV.values():
    b = a["threat_band"]
    for pb in (b - 1, b, b + 1):
        if 1 <= pb <= 5:
            rows.append(("P%d vs %s" % (pb, a["id"]), C.pc_line(pb), [line_of(a)], "bestiary"))
            if a.get("advisory_without_counter"):
                rows.append(("P%d vs %s (no counter)" % (pb, a["id"]), C.pc_line(pb), [line_of(a, counter=False)], "no_counter"))
MIX = [
    (1, ["adv.bandit_captain", "adv.brigand_band"]), (1, ["adv.goblin_boss", "adv.goblin_mob"]), (1, ["adv.footpad", "adv.footpad", "adv.brigand_archer"]),
    (1, ["adv.wolf", "adv.wolf", "adv.wolf"]), (1, ["adv.skeleton_warrior", "adv.skeleton_rabble"]), (1, ["adv.cult_initiate", "adv.cult_fanatic"]),
    (2, ["adv.highwayman", "adv.brigand_archer", "adv.brigand_archer"]), (2, ["adv.orc_raider", "adv.orc_raider"]), (2, ["adv.goblin_boss", "adv.goblin_mob"]),
    (2, ["adv.dire_wolf", "adv.wolf_pack"]), (2, ["adv.man_at_arms", "adv.crossbowman", "adv.town_watch"]), (2, ["adv.ghoul", "adv.ghoul"]),
    (2, ["adv.hedge_witch", "adv.brigand_band"]), (2, ["adv.gnoll_reaver", "adv.gnoll_pack"]), (2, ["adv.giant_spider", "adv.giant_centipede"]),
    (3, ["adv.orc_warchief", "adv.orc_warband"]), (3, ["adv.sergeant", "adv.man_at_arms", "adv.crossbowman"]), (3, ["adv.barrow_wight", "adv.skeleton_rabble"]),
    (3, ["adv.cult_priest", "adv.cult_initiate", "adv.cult_fanatic"]), (3, ["adv.ogre", "adv.goblin_mob"]), (3, ["adv.warg_alpha", "adv.wolf_pack"]),
    (3, ["adv.sorcerer", "adv.highwayman", "adv.highwayman"]), (3, ["adv.wyvern", "adv.wyvern"]), (3, ["adv.knight_errant", "adv.man_at_arms"]),
    (4, ["adv.troll", "adv.ogre"]), (4, ["adv.wight_lord", "adv.barrow_wight"]), (4, ["adv.court_magus", "adv.sergeant"]),
    (4, ["adv.chain_devil", "adv.cult_priest"]), (4, ["adv.young_dragon"]), (4, ["adv.hill_giant", "adv.ogre", "adv.ogre"]),
    (4, ["adv.brain_eater", "adv.cult_fanatic", "adv.cult_fanatic"]), (5, ["adv.lich", "adv.skeleton_rabble"]), (5, ["adv.vampire_count", "adv.vampire_spawn"]),
    (5, ["adv.elder_dragon"]), (5, ["adv.death_king", "adv.wight_lord"]), (5, ["adv.frost_giant_jarl", "adv.hill_giant"]),
    (5, ["adv.fey_queen", "adv.sidhe_knight", "adv.sidhe_knight"]), (5, ["adv.pit_lord", "adv.vrock", "adv.vrock"]),
]
for pb, ids in MIX:
    rows.append(("P%d vs %s" % (pb, " + ".join(i[4:] for i in ids)), C.pc_line(pb), [line_of(ADV[i]) for i in ids], "mixed"))
# ch.02's request: the advisory reads the PC's ACTUAL line at band 1
PCS = {"martial (+5 S2, Guard 14, armor 1)": C.pc_line(1),
       "caster in melee (+2 staff S2, Guard 12, armor 0)": C.pc_line(1, atk=2, guard=12, armor=0),
       "caster with a zero-cost working (+5 S2, Guard 12, armor 0)": C.pc_line(1, atk=5, guard=12, armor=0),
       "weakest legal (+1 S2, Guard 10, armor 0, Vitality 11)": C.pc_line(1, atk=1, guard=10, armor=0, vit=11),
       "heavy-armored (+4 S2, Guard 15, armor 3)": C.pc_line(1, atk=4, guard=15, armor=3)}
for pn, pc in PCS.items():
    for ids in (["adv.highwayman"], ["adv.man_at_arms"], ["adv.footpad", "adv.footpad"], ["adv.goblin_mob"], ["adv.orc_raider", "adv.orc_raider"], ["adv.wolf", "adv.wolf", "adv.wolf"]):
        rows.append(("%s vs %s" % (pn, " + ".join(i[4:] for i in ids)), pc, [line_of(ADV[i]) for i in ids], "pc_lines"))

conf = collections.Counter()
by_group = collections.defaultdict(lambda: [0, 0, 0])
misses = []
results = []
for label, pc, lines, grp in rows:
    w, s, rnd, lost = sim(pc, lines)
    ew, es, ratio = C.estimate(pc, lines)
    a_sim, a_est = word(w, s), word(ew, es)
    conf[(a_sim, a_est)] += 1
    g = by_group[grp]
    g[0] += 1
    g[1] += a_sim == a_est
    g[2] += abs(W.index(a_sim) - W.index(a_est)) <= 1
    results.append((label, pc, lines, grp, a_sim, a_est, w, s))
    if a_sim != a_est:
        misses.append("%-70s sim %-7s %5.1f/%5.1f | est %-7s %5.1f/%5.1f  (%s)" % (label[:70], a_sim, w, s, a_est, ew, es, "est gentler" if W.index(a_est) < W.index(a_sim) else "est harsher"))
tot = sum(v[0] for v in by_group.values())
ex = sum(v[1] for v in by_group.values())
nr = sum(v[2] for v in by_group.values())
print("rows: %d   exact: %d (%.1f%%)   within one word: %d (%.1f%%)" % (tot, ex, 100.0 * ex / tot, nr, 100.0 * nr / tot))
for gk, v in by_group.items():
    print("  %-11s %3d rows  exact %5.1f%%  within one %5.1f%%" % (gk, v[0], 100.0 * v[1] / v[0], 100.0 * v[2] / v[0]))
print("\nConfusion (rows = simulated word, columns = estimated word):\n")
print("| sim \\ est | " + " | ".join(W) + " |")
print("|---|" + "---|" * 5)
for a in W:
    print("| %s | " % a + " | ".join(str(conf[(a, b)]) for b in W) + " |")
gentle = sum(1 for m in misses if m.endswith("(est gentler)"))
print("\nmisses: %d (estimator gentler %d, harsher %d)" % (len(misses), gentle, len(misses) - gentle))
for m in misses:
    print("  " + m)
print("\nBand-1 PC lines (ch.02's request): advisory read from the actual line")
for label, pc, lines, grp, a_sim, a_est, w, s in results:
    if grp == "pc_lines":
        print("  %-95s sim %-7s %5.1f/%5.1f  est %s" % (label, a_sim, w, s, a_est))

# ============================================================================ E
print("\n### E. Chapter 07's ladder on the final templates: lethal-context fights fought to the end, pooled by the estimator's word\n")
pool = collections.defaultdict(list)
Foe06 = sim06.Foe


def to06(L):
    return Foe06(L["band"], members=L.get("members", 1), leader=L.get("leader", False),
                 over={k: L[k] for k in ("atk", "guard", "vit", "sev", "red", "morale", "tempo", "heavy")})


for label, pc, lines, grp, a_sim, a_est, w, s in results:
    if grp not in ("matrix", "bestiary", "mixed"):
        continue
    pb = int(label[1]) if label.startswith("P") else 1
    if any(L.get("morale") is None for L in lines):
        lines2 = [dict(L, morale=99) for L in lines]   # 07's model needs a clock size; 99 = never breaks
    else:
        lines2 = lines
    rng = random.Random(707)
    res = [H07.fight07(rng, pb, [to06(L) for L in lines2], lethal=True, kill=True) for _ in range(max(400, RUNS // 4))]
    pool[a_est].extend(res)
TARGET = {"trivial": 0, "easy": 1, "fair": 5, "hard": 26, "lethal": 80}
print("| advisory (estimator) | fights | Staggered | Dying | menu (per 100) | 07's target |")
print("|---|---|---|---|---|---|")
for a in W:
    r = pool.get(a, [])
    if not r:
        continue
    n = float(len(r))
    print("| %s | %d | %.1f | %.1f | %.1f | %d |" % (a, len(r), 100 * sum(x["staggered"] for x in r) / n, 100 * sum(x["dying"] for x in r) / n,
                                                  100 * sum(x["threshold"] for x in r) / n, TARGET[a]))

# ============================================================================ F
print("\n### F. Solo encounter budgets (standard templates; extended model): the largest group of each shape that stays at each word\n")
for b in range(1, 6):
    pc = C.pc_line(b)
    print("P%d:" % b)
    for e in (b - 2, b - 1, b, b + 1):
        if e < 1 or e > 5:
            continue
        out = []
        for n in range(1, 9):
            w_, s_, _, _ = sim(pc, [C.std(e) for _ in range(n)], runs=max(1000, RUNS // 3))
            out.append("%d:%s" % (n, word(w_, s_)[:4]))
            if word(w_, s_) == "lethal":
                break
        mob = []
        for m in (3, 4, 6, 8, 10, 12):
            w_, s_, _, _ = sim(pc, [dict(C.std(e), members=m)], runs=max(1000, RUNS // 3))
            mob.append("%d:%s" % (m, word(w_, s_)[:4]))
            if word(w_, s_) == "lethal":
                break
        print("  T%d individuals %s | as one mob %s" % (e, " ".join(out), " ".join(mob)))
