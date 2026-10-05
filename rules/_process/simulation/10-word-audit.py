"""10-word-audit.py -- issue I-027: PR-10-8's word step (step 2) run on travel.yaml's GENERIC encounter tables.

The generic tables are band-relative (rows at home-1 / home / home+1), so each table is audited at every home band
1-5 against a reference PC of that band (09_core.pc_line). Each threat row is fielded as 09.8.3 / 10.10.1 say:
  - band: home + offset, clamped 1..5, then to the archetype's fielded bands (nearest);
  - the adversary: built with chapter 09's own PR-09-1 code (09-gen_data09.py build(), executed up to its write
    step exactly as 13-gen_region.py does), variant standard, the archetype's first role;
  - count: "1"; "a-b" -> the middle face of tbl.09.group_shape (and the high face, reported separately);
    "group" -> the archetype's encounter.group (alone / alone or pair / band a-b / mob a-b / swarm), with its
    leader (an elite of the same archetype and band) when the group lists one;
  - four or more of one kind fold into one mob of minions (06.10.2; 09.8.1 rule 1); at home bands 4-5 a pair of
    home-band individuals becomes one elite (09.8.1 rule 2).
  - The word is PR-09-4 with the archetype's counter held (09.6.4 `advisory_alone`, the convention PR-10-8 now
    states, DL-INT-04); the no-counter word is reported beside it.
Checks (10.10.2 item 3): at least 2/3 of threat weight fair or easier; no lethal row; a hard row has
complication: false. Output: 10-word-audit-output.txt (this script's stdout). Deterministic (no RNG).
"""
import os, sys, math
from collections import Counter
import yaml
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "data"))
src = open(os.path.join(HERE, "09-gen_data09.py"), encoding="utf-8").read()
ns = {"__file__": os.path.join(HERE, "09-gen_data09.py"), "__name__": "gen09_for_10_audit"}
exec(compile(src[:src.index("\nADV = []")], "09-gen_data09.py", "exec"), ns)
C, ARCH, build, V = ns["C"], ns["ARCH"], ns["build"], ns["RO"].V
TRAVEL = yaml.safe_load(open(os.path.join(DATA, "travel.yaml"), encoding="utf-8"))
WORDS = ["trivial", "easy", "fair", "hard", "lethal"]

_CACHE = {}
def line(arch, band, variant="standard", members=1, swarm=False, leader=False):
    key = (arch, band, variant, members, swarm, leader)
    if key not in _CACHE:
        _CACHE[key] = _line(arch, band, variant, members, swarm, leader)
    return dict(_CACHE[key])

def _line(arch, band, variant="standard", members=1, swarm=False, leader=False):
    a = ARCH[arch]
    role = "swarm" if swarm else a["roles"][0]
    e = build(V("audit.%s.%d.%s" % (arch, band, variant), "audit", arch, band, role, variant, members=members, swarm=swarm, leader=leader))
    L = dict(e["calibration"]["line"])
    v = e["vitality"]
    L["vit"] = v["per_member"] if isinstance(v, dict) else v
    L["members"] = e.get("members", 1) or 1
    L["leader"] = leader
    L["swarm"] = swarm
    return L

def clamp_band(arch, b):
    lo, hi = ARCH[arch]["bands"]
    return max(lo, min(hi, max(1, min(5, b))))

def rng(s):
    a, _, b = str(s).partition("-")
    return int(a), int(b or a)

def mid_high(s):
    lo, hi = rng(s)
    return (lo + hi) // 2, hi

def field(arch, b, home, n, leader=False, swarm=False):
    foes = []
    if swarm:
        foes.append(line(arch, b, "minion", members=max(4, n), swarm=True))
    elif n >= 4:
        foes.append(line(arch, b, "minion", members=n))
    elif home >= 4 and n >= 2 and b == home:
        foes.append(line(arch, b, "elite"))          # 09.8.1 rule 2: never two equal individuals at P4-P5
    else:
        foes += [line(arch, b) for _ in range(n)]
    if leader:
        foes.append(line(arch, b, "elite", leader=True))
    return foes

def row_fields(row, home):
    off = {"home-1": -1, "home": 0, "home+1": 1}[row["band"]]
    out = []
    for ref in row["ref"]:
        b = clamp_band(ref, home + off)
        cnt = str(row["count"])
        g = ARCH[ref].get("group") or {}
        if cnt == "group":
            usual = g.get("usual", "alone")
            lead = g.get("leader") == "elite"
            if usual.startswith("swarm"):
                out.append(("mid", field(ref, b, home, 6, swarm=True)))
                continue
            if usual in ("alone",) or usual.startswith("alone"):
                n_mid, n_high = (1, 2) if "pair" in usual else (1, 1)
                lead = False
            else:
                n_mid, n_high = mid_high(g.get("count", "2-4"))
            out.append(("mid", field(ref, b, home, n_mid, leader=lead)))
            out.append(("high", field(ref, b, home, n_high, leader=lead)))
        else:
            n_mid, n_high = mid_high(cnt)
            out.append(("mid", field(ref, b, home, n_mid)))
            out.append(("high", field(ref, b, home, n_high)))
    return out

def word(home, foes, counter_held=True):
    fl = [dict(f, taken=1.0, regen=0) for f in foes] if counter_held else foes
    win, stag, _ = C.estimate(C.pc_line(home), fl)
    return C.classify_sim(win, stag), win, stag

fails = []
summary = []
for t in TRAVEL["encounter_tables"]:
    for home in range(1, 6):
        wsum = Counter(); hard_complication = []
        rows_out = []
        for row in t["threat"]:
            lo, hi = rng(row["range"]); w = hi - lo + 1
            res = {}
            for kind, foes in row_fields(row, home):
                wd, win, stag = word(home, foes)
                wd0, _, _ = word(home, foes, counter_held=False)
                res[kind] = (wd, round(win, 1), round(stag, 1), wd0)
            wd = res["mid"][0]
            wsum[wd] += w
            if wd == "lethal":
                fails.append("%s home %d row %s (%s): lethal" % (t["id"], home, row["range"], "+".join(row["ref"])))
            if wd == "hard" and row.get("complication"):
                hard_complication.append(row["range"])
            rows_out.append((row["range"], "+".join(row["ref"]), row["band"], row["count"], res["mid"], res.get("high")))
        fair = sum(wsum[k] for k in ("trivial", "easy", "fair"))
        ok = fair * 3 >= 20 * 2 and wsum["lethal"] == 0 and not hard_complication
        if fair * 3 < 40:
            fails.append("%s home %d: only %d/20 threat faces fair or easier" % (t["id"], home, fair))
        for r in hard_complication:
            fails.append("%s home %d row %s: hard and complication: true" % (t["id"], home, r))
        summary.append((t["id"], home, dict(wsum), fair, ok))
        print("%-22s home %d  %s  fair-or-easier %2d/20  %s" % (t["id"], home, " ".join("%s:%d" % (k, wsum[k]) for k in WORDS if wsum[k]), fair, "PASS" if ok else "FAIL"))
        for r in rows_out:
            mid, high = r[4], r[5]
            extra = ""
            if mid[3] != mid[0]: extra += " (without counter: %s)" % mid[3]
            if high and high[0] != mid[0]: extra += " [high face: %s]" % high[0]
            print("    %-6s %-24s %-7s %-6s %-7s win %5.1f stag %5.1f%s" % (r[0], r[1], r[2], r[3], mid[0], mid[1], mid[2], extra))
print()
print("tables x home bands audited:", len(summary), "| pass:", sum(1 for s in summary if s[4]), "| fail:", sum(1 for s in summary if not s[4]))
print("failures:", len(fails))
for f in fails:
    print("  F", f)
