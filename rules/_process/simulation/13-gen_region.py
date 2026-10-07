"""13-gen_region.py -- chapter 13's generator and auditor for the Thallen March.

Reads the content modules 13_data_*.py, checks every id against the canonical data (tags, licenses, effects,
conditions, hazards, sites, archetypes, adversaries, properties, base items, abilities, rituals, origins,
companions, world_turn templates, faction templates and rank ladders, calendar effects, social refusal kinds),
builds the region's new adversaries with chapter 09's own PR-09-1 code (09-gen_data09.py's build()), and runs:

  - PR-10-8 on every regional encounter table (bands 6/11/3, shapes, words vs a home-band reference PC, mixture,
    ids and signs);
  - 11.3.1 conformance on every faction (tier, hold, ratings caps and sums, goal scopes and clock sizes, linchpin
    fates, temperament, stage, effect ids);
  - PR-02-9 on the setting origins and on every pregen;
  - 15.9.4 validity on every case (>= 3 placements, 2 holder kinds, 2 method kinds, 1 core, 2 places, 2 reserve;
    entry reachable; a fallback);
  - 10.1.2 completeness on every place, ring distances by shortest known path against T-10-2, route symmetry;
  - 05.7.10's eight canon items and every '13' interface request (a checklist).

Writes (only if there are no errors):
  data/region_thallen.yaml
  data/contrib/origins.13.yaml, licenses.13.yaml, factions.13.yaml, adversaries.13.yaml, hazards.13.yaml, calendar.13.yaml
and prints the audit report (13-gen_region-output.txt is this script's stdout).
"""
import copy
import importlib.util
import math
import os
import sys
from collections import Counter, defaultdict, deque

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.normpath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(RULES, "data")
CONTRIB = os.path.join(DATA, "..", "_process", "merged-contrib")


def load_mod(name):
    s = importlib.util.spec_from_file_location(name.replace("-", "_"), os.path.join(HERE, name + ".py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def Y(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def contrib_entries(prefix):
    out = []
    for fn in sorted(os.listdir(CONTRIB)):
        if fn.startswith(prefix + ".") and fn.endswith(".yaml") and not fn.endswith(".13.yaml"):
            d = Y(os.path.join(CONTRIB, fn))
            for b in d.get("blocks", []) or []:
                out += b.get("entries", []) or []
            for k, v in d.items():
                if isinstance(v, list) and k != "blocks":
                    out += [e for e in v if isinstance(e, dict)]
    return out


errors, warns, notes = [], [], []


def err(m):
    errors.append(m)


def warn(m):
    warns.append(m)


# ====================================================================== canonical data
TAGD = Y(os.path.join(DATA, "tags.yaml"))
TAGS = {t["id"] for t in TAGD["tags"]} | {f["id"] for f in TAGD["facets"]}
for e in contrib_entries("tags"):
    TAGS.add(e["id"])
EFFECTS = {e["id"] for e in Y(os.path.join(DATA, "effects.yaml"))["core"]} | {e["id"] for e in contrib_entries("effects")}
CONDS = {c["id"] for c in Y(os.path.join(DATA, "conditions.yaml"))["conditions"]} | {c["id"] for c in contrib_entries("conditions")}
LICD = Y(os.path.join(DATA, "licenses.yaml"))
LICS = {l["id"] for l in LICD["licenses"]} | {l["id"] for l in contrib_entries("licenses")}
ABIL = {a["id"]: a for a in Y(os.path.join(DATA, "abilities.yaml"))["abilities"]}
RITS = {r["id"] for r in Y(os.path.join(DATA, "rituals.yaml"))["rituals"]}
HAZ = {h["id"] for h in Y(os.path.join(DATA, "hazards.yaml"))["hazards"]}
SITES = Y(os.path.join(DATA, "sites.yaml"))
THEMES = {t["id"] for t in SITES["site_themes"]}
DOMAINS = {t["id"] for t in SITES["site_domains"]}
SIZES = {s["id"]: s for s in SITES["sizes"]}
ARCHD = Y(os.path.join(DATA, "archetypes.yaml"))
ARCHY = {a["id"]: a for a in ARCHD["archetypes"]}
ADVY = {a["id"]: a for a in Y(os.path.join(DATA, "adversaries.yaml"))["adversaries"]}
IP = Y(os.path.join(DATA, "item_properties.yaml"))
PROPS = {p["id"]: p for p in IP["properties"]}
BASE = {b["id"]: b for b in Y(os.path.join(DATA, "base_items.yaml"))["base_items"]}
ITEM_TAGS = {t for b in BASE.values() for t in b.get("item_tags", [])} | {t for t in TAGS if t.startswith("item.")}
ORIGD = Y(os.path.join(DATA, "origins.yaml"))
ORIG = {o["id"]: o for o in ORIGD["origins"]}
COMP = {c["id"]: c for c in Y(os.path.join(DATA, "companions.yaml"))["companions"]}
WT = Y(os.path.join(DATA, "world_turn.yaml"))
SIT_T = {s["id"] for s in WT["situation_templates"]}
PHEN = {p["id"] for p in WT["phenomena"]}
FACD = Y(os.path.join(DATA, "factions.yaml"))
FTPL = {t["id"]: t for t in FACD["templates"]}
RLAD = {r["id"] for r in FACD["rank_ladders"]}
CAL = Y(os.path.join(DATA, "calendar.yaml"))
FX = {f["id"] for f in CAL["festival_effects"]}
SOC = Y(os.path.join(DATA, "social.yaml"))
REFUSALS = {r["id"] for r in SOC["refusal_kinds"]}
LIFESTYLES = {l["lifestyle"] for l in SOC["npc_lifestyle"]}
TRAVEL = Y(os.path.join(DATA, "travel.yaml"))
SIGNS = TRAVEL["archetype_signs"]
ECON = Y(os.path.join(DATA, "economy.yaml"))
KITS = Y(os.path.join(DATA, "kits.yaml"))
OR = Y(os.path.join(DATA, "oracles.yaml"))
ORT = {t["id"] for t in OR["tables"]}
INV = Y(os.path.join(DATA, "investigation.yaml"))
IMETHODS = {m["id"] for m in INV["methods"]}
LAST = Y(os.path.join(DATA, "last_chance.yaml"))


def tag_ok(t, where):
    if t not in TAGS:
        err("%s: unknown tag %s" % (where, t))


def lic_ok(l, where, extra=()):
    if l not in LICS and l not in extra:
        err("%s: unknown license %s" % (where, l))


def eff_ok(e, where):
    if not isinstance(e, dict) or e.get("effect_id") not in EFFECTS:
        err("%s: unknown effect %s" % (where, e))


# ====================================================================== content modules
WD = load_mod("13_data_world")
PD = load_mod("13_data_places")
PE = load_mod("13_data_people")
FD = load_mod("13_data_factions")
BD = load_mod("13_data_bestiary")
TD = load_mod("13_data_tables")
CD = load_mod("13_data_cases")
OD = load_mod("13_data_origins")
OP = load_mod("13_data_opening")

# ====================================================================== 09's PR-09-1, reused verbatim
src09 = open(os.path.join(HERE, "09-gen_data09.py"), encoding="utf-8").read()
cut = src09.index("\nADV = []")
ns09 = {"__file__": os.path.join(HERE, "09-gen_data09.py"), "__name__": "gen09_for_13"}
exec(compile(src09[:cut], "09-gen_data09.py", "exec"), ns09)
C09 = ns09["C"]
if ns09["errors"]:
    err("09's generator reports errors before build: %s" % ns09["errors"][:3])
# the script-side archetypes must agree with the canonical yaml (bands and nerve), or our build is not 09's
for aid, a in ns09["ARCH"].items():
    ay = ARCHY.get(aid)
    if not ay:
        err("09 script archetype %s missing from archetypes.yaml" % aid)
        continue
    if list(ay["bands"]) != list(a["bands"]):
        err("archetype %s bands differ: script %s yaml %s" % (aid, a["bands"], ay["bands"]))

NEW_ADV = []
for v in BD.ROSTER:
    n_err = len(ns09["errors"])
    e = ns09["build"](v)
    if len(ns09["errors"]) > n_err:
        for x in ns09["errors"][n_err:]:
            err("PR-09-1 build: " + x)
    if e is None:
        continue
    if v["id"] in ADVY:
        err("new adversary id collides with 09's: %s" % v["id"])
    e["region"] = WD.REGION
    e["basis"] = ["09.4 PR-09-1", "09.3 T-09-3", v["arch"], "13.10"]
    NEW_ADV.append(e)
for w in ns09["warn"]:
    if any(w.startswith(v["id"]) for v in BD.ROSTER):
        warns.append("PR-09-1 build: " + w)
ADV_ALL = dict(ADVY)
for e in NEW_ADV:
    ADV_ALL[e["id"]] = e
for a in BD.SUBSET_09:
    if a not in ADVY:
        err("bestiary subset names unknown adversary %s" % a)


def foe_line(adv):
    L = dict(adv["calibration"]["line"])
    v = adv["vitality"]
    if isinstance(v, dict):
        L["vit"] = v["per_member"]
        L["members"] = adv.get("members", 1)
    else:
        L["vit"] = v
        L["members"] = adv.get("members", 1)
    L["leader"] = bool(adv.get("leader"))
    L["swarm"] = bool(adv.get("swarm"))
    return L


def field_row(row):
    """09.8.3's fielding of a row: a list of foe lines (mobs as one entity)."""
    foes = []
    refs = row["ref"]
    cnt = str(row["count"])
    if cnt == "leader+mob":
        for r in refs:
            foes.append(foe_line(ADV_ALL[r]))
        return foes
    adv = ADV_ALL[refs[0]]
    if cnt == "group":
        if adv.get("members", 1) <= 1:
            err("row %s: count 'group' on a non-mob entry %s" % (row["range"], refs[0]))
        foes.append(foe_line(adv))
        return foes
    n = int(cnt.split("-")[-1])
    if n >= 4:
        L = foe_line(adv)
        L["members"] = n
        foes.append(L)
    else:
        foes += [foe_line(adv) for _ in range(n)]
    return foes


def faces(rng):
    a, _, b = str(rng).partition("-")
    return list(range(int(a), int(b or a) + 1))


AUDIT = {}


def audit_table(t):
    tid = t["id"]
    home = t["home_band"]
    rep = {"bands": Counter(), "words": Counter(), "rows": []}
    covered = []
    for row in t["threat"]:
        f = faces(row["range"])
        covered += f
        w = len(f)
        rep["bands"][row["band"]] += w
        for r in row["ref"]:
            if r not in ADV_ALL:
                err("%s %s: unknown adversary %s" % (tid, row["range"], r))
                return None
        bands = [ADV_ALL[r]["threat_band"] for r in row["ref"]]
        lead = bands[0]
        want = {"home-1": max(1, home - 1), "home": home, "home+1": min(5, home + 1)}[row["band"]]
        if lead != want:
            err("%s %s: %s is band %d but the row is %s (= %d at home %d)" % (tid, row["range"], row["ref"][0], lead, row["band"], want, home))
        if any(b > home + 1 for b in bands):
            err("%s %s: above home + 1 (a lair, not a wanderer)" % (tid, row["range"]))
        # shapes (T-09-10): at home 4-5 never two individuals of the home band
        if home >= 4 and str(row["count"]) not in ("1", "group", "leader+mob") and lead == home:
            err("%s %s: two individuals of the home band at band %d" % (tid, row["range"], home))
        if str(row["count"]) not in ("1", "group", "leader+mob") and int(str(row["count"]).split("-")[-1]) > 2 and int(str(row["count"]).split("-")[-1]) < 4:
            err("%s %s: three individuals (fold four or more into a mob; at most two individuals)" % (tid, row["range"]))
        foes = field_row(row)
        # 09.4.4 / PR-09-4 convention: the word is computed as if the PC holds the counter (taken 1, regen 0);
        # the word without the counter is reported, and such rows must show their counter in the adversary's lore
        win, stag, _ = C09.estimate(C09.pc_line(home), [dict(f, taken=1.0, regen=0) for f in foes])
        word = C09.classify_sim(win, stag)
        win0, stag0, _ = C09.estimate(C09.pc_line(home), foes)
        word0 = C09.classify_sim(win0, stag0)
        rep["words"][word] += w
        rep["rows"].append((row["range"], "+".join(row["ref"]), row["band"], row["count"], word, round(win, 1), round(stag, 1),
                            ("without its counter: " + word0) if word0 != word else ""))
        if word == "lethal":
            err("%s %s: lethal against a home-band reference PC" % (tid, row["range"]))
        if word == "hard" and row.get("complication"):
            err("%s %s: a hard row may not roll a complication" % (tid, row["range"]))
        for r in row["ref"]:
            arch = ADV_ALL[r]["archetype"]
            if not (row.get("signs") or SIGNS.get(arch)):
                err("%s %s: no signs for %s" % (tid, row["range"], arch))
    if sorted(covered) != list(range(1, 21)):
        err("%s: threat faces do not cover 1-20 exactly: %s" % (tid, sorted(covered)))
    b = rep["bands"]
    for k, target in (("home-1", 6), ("home", 11), ("home+1", 3)):
        if abs(b[k] - target) > 1:
            err("%s: band weight %s = %d (target %d +-1)" % (tid, k, b[k], target))
    fair_or_easier = sum(rep["words"][k] for k in ("trivial", "easy", "fair"))
    if fair_or_easier * 3 < 20 * 2:
        err("%s: only %d/20 threat faces fair or easier (need >= 2/3)" % (tid, fair_or_easier))
    nt = t.get("non_threat", [])
    ntf = []
    for r in nt:
        ntf += faces(r["range"])
        for a in r.get("ref", []) or []:
            if a not in ADV_ALL:
                err("%s non-threat %s: unknown %s" % (tid, r["range"], a))
    if t["danger"] != "deadly" and sorted(ntf) != list(range(1, 7)):
        err("%s: non-threat sub-table must be a full d6 (faces %s)" % (tid, sorted(ntf)))
    rep["non_threat_faces"] = len(ntf)
    AUDIT[tid] = rep
    return rep


for t in BD.ENCOUNTER_TABLES:
    audit_table(t)


if "--tables-only" in sys.argv:
    for tid, r in AUDIT.items():
        print(tid, dict(r["bands"]), dict(r["words"]))
        for x in r["rows"]:
            print("   ", x)
    print("errors", len(errors))
    for e in errors:
        print("  E", e)
    sys.exit(0)

# the remaining passes live in part files executed in this namespace (one file per concern)
for _part in ("13_gen_part2.py", "13_gen_part3.py", "13_gen_part4.py"):
    _path = os.path.join(HERE, _part)
    if os.path.exists(_path):
        exec(compile(open(_path, encoding="utf-8").read(), _part, "exec"), globals())
