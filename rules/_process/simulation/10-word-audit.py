"""10-word-audit.py -- PR-10-8 (10.10.2) run on every encounter table: the generic tables in travel.yaml (one
threat sub-table per terrain branch and home band, T-10-16) and, through `audit_table()`, any regional table
(13's, or a world seed's, 12.16; `12-world-seed.py` imports this file).

History: written at integration for I-027 (band-relative generic tables, audited at every home band 1-5: 7 of 55
cases passed). Rewritten in revision B for I-029: the generic tables are now written per home band
(`threat_by_home`), each row carries its `variant` and `leader`, and the audit adds the checks below marked (B).

How a threat row is fielded (09.8.3, 10.10.1):
  - band = home + offset (home-1 / home / home+1). Below 1 it is 1 only for a home-1 row at home 1; above 5 it is
    5 only for a home+1 row at home 5 (09.8.2's top ring: those rows are solos). (B) Any other band outside the
    archetype's fielded bands (archetypes.yaml#bands) is a failure: the row could not be fielded as written.
    A fixed integer band (regional tables) is taken as is.
  - the adversary: an `arch.*` ref is built with chapter 09's own PR-09-1 code (09-gen_data09.py build(), executed
    up to its write step), variant from the row (default standard), the archetype's first role; an `adv.*` ref
    reads the bestiary entry's calibrated line (adversaries.yaml).
  - count: "n" or "a-b"; the middle face (tbl.09.group_shape 3-4) is the row's word; (B) the high face (5-6, a
    third of rolls) must not be lethal either (09.8.1 rule 3: rolled fights are never lethal). "group" reads the
    archetype's encounter.group as the integration audit did (only regional tables still use it).
  - four or more of one kind fold into one mob of minions (06.10.2; 09.8.1 rule 1); `leader: true` adds an elite of
    the same archetype and band.
  - (B) shape rules (10.10.2 item 2) are checked, not silently repaired: at most two individuals of the home band,
    and at home bands 4-5 never two home-band individuals.
  - the word is PR-09-4 with the archetype's counter held (09.6.4 `advisory_alone`, DL-INT-04); the no-counter
    word is printed beside it.
Checks (10.10.2): item 1 weights 6/11/3 of 20 by relative band (fixed-band regional rows are binned by
band - home); item 3 at least 2/3 of threat weight fair or easier, no lethal face, a hard row has
complication: false; item 4 the non-threat sub-table exists with six faces; every ref exists.
Output: 10-word-audit-output.txt (this script's stdout). Deterministic (no RNG).
Usage: python 10-word-audit.py [--data DIR]
"""
import os, sys, re
from collections import Counter
import yaml
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "data"))
if "--data" in sys.argv:
    DATA = os.path.abspath(sys.argv[sys.argv.index("--data") + 1])
src = open(os.path.join(HERE, "09-gen_data09.py"), encoding="utf-8").read()
ns = {"__file__": os.path.join(HERE, "09-gen_data09.py"), "__name__": "gen09_for_10_audit"}
exec(compile(src[:src.index("\nADV = []")], "09-gen_data09.py", "exec"), ns)
C, ARCH, build, V = ns["C"], ns["ARCH"], ns["build"], ns["RO"].V
_advdoc = yaml.safe_load(open(os.path.join(DATA, "adversaries.yaml"), encoding="utf-8"))
ADV = {e["id"]: e for e in _advdoc["adversaries"]}
for _b in _advdoc.get("blocks") or []:
    for e in _b.get("entries") or []:
        ADV[e["id"]] = e
WORDS = ["trivial", "easy", "fair", "hard", "lethal"]
OFF = {"home-1": -1, "home": 0, "home+1": 1}

_CACHE = {}
def line(arch, band, variant="standard", members=1, swarm=False, leader=False):
    key = (arch, band, variant, members, swarm, leader)
    if key not in _CACHE:
        a = ARCH[arch]
        role = "swarm" if swarm else a["roles"][0]
        e = build(V("audit.%s.%d.%s" % (arch, band, variant), "audit", arch, band, role, variant, members=members, swarm=swarm, leader=leader))
        L = dict(e["calibration"]["line"])
        v = e["vitality"]
        L["vit"] = v["per_member"] if isinstance(v, dict) else v
        L["members"] = e.get("members", 1) or 1
        L["leader"] = leader
        L["swarm"] = swarm
        _CACHE[key] = L
    return dict(_CACHE[key])

def adv_line(adv_id):
    e = ADV[adv_id]
    L = dict(e["calibration"]["line"])
    v = e["vitality"]
    L["vit"] = v["per_member"] if isinstance(v, dict) else v
    L["members"] = e.get("members", 1) or 1
    L["leader"] = e.get("leader", False)
    L["swarm"] = e.get("swarm", False)
    return L

def rng(s):
    a, _, b = str(s).partition("-")
    return int(a), int(b or a)

def resolve_band(row, home):
    """Returns (band, problem or None)."""
    b = row["band"]
    if isinstance(b, int):
        return b, None
    want = home + OFF[b]
    if want < 1:
        return 1, (None if (home == 1 and b == "home-1") else "band below 1")
    if want > 5:
        return 5, (None if (home == 5 and b == "home+1") else "band above 5")
    return want, None

def field(ref, b, n, variant, leader, home):
    """The participants for n of ref at band b, and any shape-rule problem."""
    problem = None
    if ref.startswith("adv."):
        L = adv_line(ref)
        if n >= 4 or (L["members"] > 1):
            return [L] if n == 1 else [dict(L)] * n, None
        foes = [dict(L) for _ in range(n)]
        return foes, None
    if n >= 4:
        if variant in ("elite", "solo"):
            problem = "four or more %s %s (a crowd is a mob of minions)" % (variant, ref)
        foes = [line(ref, b, "minion", members=n)]
    else:
        foes = [line(ref, b, variant) for _ in range(n)]
        if b == home and variant in ("standard", "elite", "solo"):
            if n > 2:
                problem = "%d individuals of the home band (at most two)" % n
            elif n == 2 and home >= 4:
                problem = "two home-band individuals at home band %d (09.8.1 rule 2)" % home
    if leader:
        foes.append(line(ref, b, "elite", leader=True))
    return foes, problem

def group_counts(ref):
    g = ARCH[ref].get("group") or {}
    usual = g.get("usual", "alone")
    if usual.startswith("swarm"):
        return "swarm", False
    if usual.startswith("alone"):
        return ("1-2" if "pair" in usual else "1"), False
    return g.get("count", "2-4"), g.get("leader") == "elite"

def word(home, foes, counter_held=True):
    fl = [dict(f, taken=1.0, regen=0) for f in foes] if counter_held else foes
    win, stag, _ = C.estimate(C.pc_line(home), fl)
    return C.classify_sim(win, stag), win, stag

def audit_row(row, home):
    """Word of one threat row at a home band: dict with mid/high words, problems."""
    out = {"problems": []}
    b, prob = resolve_band(row, home)
    if prob:
        out["problems"].append(prob)
    count, leader = str(row.get("count", "1")), bool(row.get("leader"))
    variant = row.get("variant") or "standard"
    res = {}
    for ref in row["ref"]:
        if ref.startswith("arch."):
            if ref not in ARCH:
                out["problems"].append("unknown archetype " + ref); continue
            lo, hi = ARCH[ref]["bands"]
            if not lo <= b <= hi:
                out["problems"].append("%s is not fielded at band %d (bands %d-%d)" % (ref, b, lo, hi))
                b = max(lo, min(hi, b))
        elif ref not in ADV:
            out["problems"].append("unknown adversary " + ref); continue
        c, lead = (group_counts(ref) if (count == "group" and ref.startswith("arch.")) else (count, False))
        if c == "group":            # an `adv.*` bestiary entry is fielded as written: a group entry is already its group
            c = "1"
        if c != "swarm" and not re.fullmatch(r"\d+(-\d+)?", str(c)):
            out["problems"].append("count %r is not one of 10.10.1's forms (\"n\", \"a-b\", \"group\")" % c)
            continue
        if c == "swarm":
            faces = {"mid": [line(ref, b, "minion", members=6, swarm=True)]}
            faces["high"] = faces["mid"]
            shape = None
        else:
            lo_n, hi_n = rng(c)
            mid_n = (lo_n + hi_n) // 2
            faces = {}
            shape = None
            for face, n in (("mid", mid_n), ("high", hi_n)):
                foes, p = field(ref, b, n, variant, leader or lead, home)
                faces[face] = foes
                shape = shape or p
        if shape:
            out["problems"].append(shape)
        for face, foes in faces.items():
            wd, win, stag = word(home, foes)
            wd0 = word(home, foes, counter_held=False)[0]
            prev = res.get(face)
            if prev is None or WORDS.index(wd) > WORDS.index(prev[0]):
                res[face] = (wd, round(win, 1), round(stag, 1), wd0)
    out.update(res)
    out["band"] = b
    return out

def audit_table(threat_rows, home, non_threat=None, deadly_only=False):
    """PR-10-8 on one threat sub-table at one home band. Returns (ok, summary dict, fails list, row results)."""
    fails = []
    wsum = Counter(); bands = Counter(); rows_out = []
    for row in threat_rows:
        lo, hi = rng(row["range"]); w = hi - lo + 1
        r = audit_row(row, home)
        if "mid" not in r:
            fails.append("row %s: cannot be fielded (%s)" % (row["range"], "; ".join(r["problems"]))); continue
        rel = row["band"] if not isinstance(row["band"], int) else {-1: "home-1", 0: "home", 1: "home+1"}.get(row["band"] - home, "out of band %+d" % (row["band"] - home))
        bands[rel] += w
        wd = r["mid"][0]
        wsum[wd] += w
        for p in r["problems"]:
            fails.append("row %s (%s): %s" % (row["range"], "+".join(row["ref"]), p))
        if wd == "lethal" or r["high"][0] == "lethal":
            fails.append("row %s (%s): lethal%s" % (row["range"], "+".join(row["ref"]), "" if wd == "lethal" else " at the high face"))
        if wd == "hard" and row.get("complication"):
            fails.append("row %s (%s): hard and complication: true" % (row["range"], "+".join(row["ref"])))
        rows_out.append((row, r))
    total = sum(wsum.values())
    fair = sum(wsum[k] for k in ("trivial", "easy", "fair"))
    if fair * 3 < total * 2:
        fails.append("only %d/%d threat faces fair or easier" % (fair, total))
    for k, want in (("home-1", 6), ("home", 11), ("home+1", 3)):
        if abs(bands.get(k, 0) - want) > 1:
            fails.append("band weights %s (want 6/11/3 +-1)" % dict(bands)); break
    if any(k.startswith("out of band") for k in bands):
        fails.append("rows outside home-1..home+1: %s" % dict(bands))
    if non_threat is not None and not deadly_only:
        faces = sum(rng(r["range"])[1] - rng(r["range"])[0] + 1 for r in non_threat)
        if faces != 6:
            fails.append("non-threat sub-table has %d faces (want 6)" % faces)
    return (not fails), {"words": dict(wsum), "fair_or_easier": fair, "total": total, "bands": dict(bands)}, fails, rows_out

def print_table(tid, home, ok, summ, rows_out):
    print("%-22s home %d  %s  fair-or-easier %2d/%d  %s" % (tid, home, " ".join("%s:%d" % (k, summ["words"].get(k, 0)) for k in WORDS if summ["words"].get(k)), summ["fair_or_easier"], summ["total"], "PASS" if ok else "FAIL"))
    for row, r in rows_out:
        mid, high = r["mid"], r["high"]
        extra = ""
        if mid[3] != mid[0]: extra += " (without counter: %s)" % mid[3]
        if high[0] != mid[0]: extra += " [high face: %s]" % high[0]
        cnt = str(row.get("count", "1")) + ("" if (row.get("variant") or "standard") == "standard" else " " + row["variant"]) + (" +leader" if row.get("leader") else "")
        print("    %-6s %-24s %-7s b%d %-14s %-7s win %5.1f stag %5.1f%s" % (row["range"], "+".join(row["ref"]), row["band"], r["band"], cnt, mid[0], mid[1], mid[2], extra))

if __name__ == "__main__":
    TRAVEL = yaml.safe_load(open(os.path.join(DATA, "travel.yaml"), encoding="utf-8"))
    fails_all = []; summary = []; allw = Counter(); variety = []; repeat = []
    for t in TRAVEL["encounter_tables"]:
        per_home = t["threat_by_home"]
        archs_all = set()
        for home in range(1, 6):
            rows = per_home[home]
            ok, summ, fails, rows_out = audit_table(rows, home, t["non_threat"])
            summary.append((t["id"], home, ok, summ))
            for k, v in summ["words"].items(): allw[k] += v
            archs_all |= {x for r in rows for x in r["ref"]}
            print_table(t["id"], home, ok, summ, rows_out)
            fails_all += ["%s home %d %s" % (t["id"], home, f) for f in fails]
            reps = Counter()
            for r in rows:
                lo, hi = rng(r["range"]); reps[r["ref"][0]] += hi - lo + 1
            repeat.append(sum((v / 20.0) ** 2 for v in reps.values()))
        variety.append((t["id"], len(archs_all), sum(len(per_home[h]) for h in per_home)))
    print()
    print("tables x home bands audited:", len(summary), "| pass:", sum(1 for s in summary if s[2]), "| fail:", sum(1 for s in summary if not s[2]))
    tot = sum(allw.values())
    print("word mix over all threat faces (mid face, counter held): " + " ".join("%s %.1f%%" % (k, 100.0 * allw[k] / tot) for k in WORDS))
    print("variety: distinct archetypes per terrain table (over its five home bands) / threat rows:")
    for tid, n, rows in variety:
        print("    %-24s %2d archetypes, %2d rows" % (tid, n, rows))
    print("repeat: chance that two threat faces in a row field the same archetype (per table and home band): mean %.3f, max %.3f (target: max <= 0.20; the first draft's single tables: mean 0.176, max 0.255)" % (sum(repeat) / len(repeat), max(repeat)))
    if max(repeat) > 0.20:
        fails_all.append("repeat chance above 0.20 in at least one table")
    print("failures:", len(fails_all))
    for f in fails_all:
        print("  F", f)
    sys.exit(1 if fails_all else 0)
