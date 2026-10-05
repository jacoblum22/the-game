# gen02.py -- validates data02.py against the shipped data files, emits ch.02's data files,
# and runs the audits whose numbers the chapter reports.
import os as _os
_RULES = _os.environ.get('GAME_RULES', _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..')))
import re, json, itertools, sys, os, random
from collections import Counter, defaultdict
from fractions import Fraction
sys.path.insert(0, os.path.dirname(__file__))
from data02 import *
from creation_block import CREATION_BLOCK

ROOT = _RULES
D = os.path.join(ROOT, "data")
EMIT = "--emit" in sys.argv

def read(p):
    with open(p, encoding="utf-8") as f: return f.read()

# ---------- load shipped ids ----------
tags_txt = read(os.path.join(D, "tags.yaml"))
TAGS = set(re.findall(r"id: ([a-z_]+(?:\.[a-z_]+)*)", tags_txt))
lic_txt = read(os.path.join(D, "licenses.yaml"))
LICS = set(re.findall(r"^- id: (lic\.[a-z_.]+)", lic_txt, re.M))
ab_txt = read(os.path.join(D, "abilities.yaml"))
ABIL = {}
for m in re.finditer(r"^- id: (ab\.[a-z_]+)\n(.*?)(?=^- id: |\Z)", ab_txt, re.M | re.S):
    body = m.group(2)
    t = re.search(r"^  tags: \[([^\],]+)", body, re.M).group(1)
    mt = int(re.search(r"^  min_tier: (\d+)", body, re.M).group(1))
    sc = re.search(r"^  slot_class: (\w+)", body, re.M).group(1)
    cost = re.search(r"^  cost: (.*)$", body, re.M)
    nm = re.search(r"^  name: (.*)$", body, re.M).group(1)
    ABIL[m.group(1)] = dict(first=t, min_tier=mt, slot_class=sc, cost=cost.group(1) if cost else "null", name=nm)
EFFECTS = set(re.findall(r"id: (eff\.[a-z_0-9.]+)", read(os.path.join(D, "effects.yaml"))))
for fn in os.listdir(os.path.join(D, "..", "_process", "merged-contrib")):
    if fn.startswith("effects.") and fn != "effects.02.yaml":
        EFFECTS |= set(re.findall(r"id: (eff\.[a-z_0-9.]+)", read(os.path.join(D, "..", "_process", "merged-contrib", fn))))
EFFECTS.add("eff.02.bent")

MY_LICS = ["lic.lang.common", "lic.lang.elvish", "lic.lang.dwarvish", "lic.lang.orcish", "lic.lang.goblin",
           "lic.lang.giantish", "lic.lang.kinspeech", "lic.lang.old_tongue", "lic.lang.cant", "lic.lang.letters",
           "lic.people.starsight", "lic.people.stonesense", "lic.people.underfoot", "lic.people.iron_blood",
           "lic.people.cave_eyes", "lic.people.great_frame", "lic.people.keen_nose"]
ALL_LICS = LICS | set(MY_LICS)

errors = []
def need(cond, msg):
    if not cond: errors.append(msg)

def lic_of(tag):   # deed.martial.blade -> lic.training.martial_blade
    p = tag.split(".")
    return "lic.training.%s_%s" % (p[1], p[2])
def tag_of(lic):
    b, s = lic.replace("lic.training.", "").split("_", 1)
    return "deed.%s.%s" % (b, s)
def under(t, anc): return t == anc or t.startswith(anc + ".")

LEVEL2 = sorted(t for t in TAGS if t.startswith("deed.") and t.count(".") == 2)
need(len(LEVEL2) == 81, "expected 81 level-2 deed tags, got %d" % len(LEVEL2))
for t in LEVEL2: need(lic_of(t) in LICS, "no training license for " + t)

# ---------- validate authored tables ----------
for p in PEOPLES:
    need(p["tag"] in TAGS, "people tag " + p["tag"])
    for l, g in p["languages"]: need(l in ALL_LICS, l)
    if p["gift"]: need(p["gift"] in ALL_LICS, p["gift"])
    if p["branch"]: need(p["branch"] in TAGS, p["branch"])
    need(len(p["hooks"]) == 2, p["id"] + " hooks")
    if p["floors"]:
        need(sorted(p["floors"].values()) == [1, 2] and list(p["fixed"].values()) == [-1], p["id"] + " rule shape")
need(sorted(list(p["fixed"])[0] for p in PEOPLES if p["fixed"]) == sorted(ATTRS), "each attribute is the forced low of exactly one people")
for u in UPBRINGINGS:
    for t in u["tags"] + u["org_tags"] + u["branches"]: need(t in TAGS, u["id"] + " tag " + t)
    for l in u["licenses"] + (u["choice"]["of"] if u["choice"] else []): need(l in ALL_LICS, u["id"] + " " + l)
    for l, g in u["languages"]: need(l in ALL_LICS, l)
    units = {5: 2, 4: 1, 3: 0}[u["focus_base"]] + len(u["licenses"]) + (u["choice"]["pick"] if u["choice"] else 0) + len(u["languages"]) + u["language_picks"]
    need(units == 3, "%s budget %d != 3" % (u["id"], units))
    u["units"] = units
    need(u["kit"] in [k["id"] for k in KITS], u["kit"])
UP = {u["id"]: u for u in UPBRINGINGS}
PROF = {p["id"]: p for p in PROFILES}
for t in TRADES:
    for x in t["trainings"] + t["org_tags"] + t["branches"]: need(x in TAGS, t["id"] + " tag " + x)
    need(t["upbringing"] in UP, t["id"] + " upbringing")
    need(t["kit"] in [k["id"] for k in KITS], t["kit"])
    need(sorted(t["priority"]) == sorted(ATTRS), t["id"] + " priority")
    pr = PROF[t["profile"]]
    need(len(t["deep"]) == pr["deep"] and len(t["access"]) == pr["access"] and (t["technique"] is not None) == bool(pr["technique"]), t["id"] + " default picks do not match profile")
    schools = ["%s.%s" % (t["magic"]["branch"], s) for s in t["magic"]["schools"]] if t.get("magic") else []
    for s in schools: need(s in TAGS, s)
    allowed = t["trainings"] + schools
    for x in t["deep"] + t["access"]: need(x in allowed, "%s default pick %s not on its list" % (t["id"], x))
    for a in t["techniques"] + ([t["technique"]] if t["technique"] else []):
        need(a in ABIL, "%s ability %s missing" % (t["id"], a))
        if a in ABIL:
            need(ABIL[a]["min_tier"] == 1, "%s %s min_tier" % (t["id"], a))
            need(any(under(ABIL[a]["first"], x) for x in allowed), "%s technique %s (%s) not under a listed training" % (t["id"], a, ABIL[a]["first"]))
    if t["technique"]:
        need(under(ABIL[t["technique"]]["first"], t["deep"][0]), t["id"] + " default technique not under default deep")
    if t.get("magic"):
        for s in schools:   # every school has a min_tier-1 spell to gift
            need(any(under(a["first"], s) and a["min_tier"] == 1 for a in ABIL.values()), "no min_tier 1 ability under " + s)
    for txt, tg in t["aspirations"]:
        for x in tg: need(x in TAGS, "%s aspiration tag %s" % (t["id"], x))
    need(len(t["drives"]) == 3 and len(t["hooks"]) == 2 and len(t["bond_seeds"]) == 2, t["id"] + " seed counts")
ANCH = ("kin", "friend", "mentor", "ward"); THORN = ("rival", "creditor", "enemy", "lost")
HK = ("thread", "rumor", "npc", "place", "debt", "enemy", "question")
for x in UPBRINGINGS + TRADES:
    need(x["bond_seeds"][0].split(":")[0] in ANCH and x["bond_seeds"][1].split(":")[0] in THORN, x["id"] + " bond seeds must be anchor then thorn")
for x in PEOPLES + UPBRINGINGS + TRADES:
    for h in x["hooks"]: need(h.split(":")[0] in HK, x["id"] + " hook kind " + h[:20])
for k in KITS:
    allitems = list(k["items"]) + [i for c in k.get("choices", []) for o in c["options"] for i in o]
    for i in allitems:
        need(i["item_tag"] in TAGS, k["id"] + " " + i["item_tag"])
        need(i["quality"] in ("worn", "common", "fine"), k["id"] + " quality")
for tr in TRAITS:
    for x in tr["gate"] + tr["tags"]: need(x in TAGS, tr["id"] + " " + x)
    for e in tr["effects"]: need(e["effect_id"] in EFFECTS, tr["id"] + " " + e["effect_id"])
for s, nm, ab, txt in GIFTS:
    for x in (ab.values() if isinstance(ab, dict) else [ab]):
        need("deed.primal." + s in TAGS and x in ABIL and under(ABIL[x]["first"], "deed.primal." + s) and ABIL[x]["min_tier"] == 1, "gift " + s + " " + x)
for a, br in BENT_GATES.items():
    for b in br: need(b in TAGS, b)
# every magic branch has an origin granting a first license (04/05 interface request)
for mb in MAGIC_BRANCHES:
    need(any(t.get("magic", {}).get("branch") == mb for t in TRADES), "no trade for " + mb)
# coverage: every level-2 deed tag is reachable on some trade list or some upbringing
listed = set()
for t in TRADES:
    listed |= set(t["trainings"])
    if t.get("magic"): listed |= {"%s.%s" % (t["magic"]["branch"], s) for s in t["magic"]["schools"]}
for u in UPBRINGINGS:
    listed |= {tag_of(l) for l in u["licenses"] + (u["choice"]["of"] if u["choice"] else []) if l.startswith("lic.training.")}
unlisted = [t for t in LEVEL2 if t not in listed]

# ---------- attribute placement machinery ----------
def placements(array, floors, fixed):
    out = set()
    for perm in set(itertools.permutations(array)):
        a = dict(zip(ATTRS, perm))
        if all(a[k] == v for k, v in fixed.items()) and all(a[k] >= v for k, v in floors.items()):
            out.add(perm)
    return out
def default_placement(array, floors, fixed, priority):
    best = None
    for perm in placements(array, floors, fixed):
        a = dict(zip(ATTRS, perm))
        key = tuple(a[x] for x in priority)
        if best is None or key > best[0]: best = (key, a)
    return best[1]

# ---------- YAML emitter (JSON-compatible flow scalars) ----------
def q(s): return json.dumps(s, ensure_ascii=False)
def flow(v):
    if isinstance(v, dict): return "{" + ", ".join("%s: %s" % (k, flow(x)) for k, x in v.items()) + "}"
    if isinstance(v, (list, tuple)): return "[" + ", ".join(flow(x) for x in v) + "]"
    if v is None: return "null"
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, (int, float)): return str(v)
    s = str(v)
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.\-]*", s) and s not in ("null", "true", "false", "yes", "no", "on", "off"): return s
    return q(s)
def entry(d, indent="  ", flow_keys=()):
    lines = []
    first = True
    for k, v in d.items():
        pre = indent + ("- " if first else "  ")
        first = False
        if isinstance(v, list) and v and isinstance(v[0], (dict, list)) and k not in flow_keys:
            lines.append("%s%s:" % (pre, k))
            for x in v: lines.append("%s    - %s" % (indent, flow(x)))
        elif isinstance(v, dict) and k not in flow_keys and len(flow(v)) > 100:
            lines.append("%s%s:" % (pre, k))
            for kk, vv in v.items(): lines.append("%s    %s: %s" % (indent, kk, flow(vv)))
        else:
            lines.append("%s%s: %s" % (pre, k, flow(v)))
    return "\n".join(lines)

BASIS_P = ["C:P4", "C:P1", "02.4.2", "02.3.2", "DL-02-03", "DL-02-04"]
KIT = {k["id"]: k for k in KITS}
def kit_items(kid):
    k = KIT[kid]
    items = [dict(i) for i in k["items"]]
    for c in k.get("choices", []): items += [dict(i) for i in c["options"][0]]
    for i in items: i.pop("note", None)
    return items

def build_origins():
    out = []
    for p in PEOPLES:
        typical = bool(p["floors"])
        rules = dict(sum=7 if typical else 5, fixed=p["fixed"], floors=p["floors"],
                     free_points=(7 - sum(p["fixed"].values())) if typical else 5,
                     shapes=SHAPES_TYPICAL if typical else SHAPES_FREE)
        if typical:
            rules["uncommon_of_kind"] = dict(sum=5, fixed={}, floors={}, free_points=5, shapes=SHAPES_FREE,
                                             keeps=["gift", "languages", "birth_pool", "hooks"], rule="02.3.4")
        e = dict(id=p["id"], name=p["name"], kind="people", tags=[p["tag"]], attribute_rules=rules,
                 licenses=[p["gift"]] if p["gift"] else [], competence=[],
                 languages=[dict(license=l, grade=g) for l, g in p["languages"]],
                 kit=[], hooks=p["hooks"], birth_pool=[p["tag"]] + ([p["branch"]] if p["branch"] else []),
                 tradeoff=p["tradeoff"], backstory=[])
        if p.get("extra_access_trainings"): e["extra_access_trainings"] = dict(count=1, any_of="any level-2 deed tag outside deed.arcane, deed.divine and deed.primal", rule="02.4.3")
        if p.get("language_choice"): e["language_picks"] = p["language_choice"]
        e["lifecycle"] = "provisional"; e["basis"] = BASIS_P
        out.append(e)
    for u in UPBRINGINGS:
        e = dict(id=u["id"], name=u["name"], kind="upbringing", tags=u["tags"], description=u["desc"],
                 attribute_rules=None, focus_base=u["focus_base"], licenses=u["licenses"], competence=[],
                 languages=[dict(license=l, grade=g) for l, g in u["languages"]])
        if u["choice"]: e["license_choice"] = u["choice"]
        if u["language_picks"]: e["language_picks"] = u["language_picks"]
        e.update(wealth=u["wealth"], kit_id=u["kit"], kit=kit_items(u["kit"]), coin=KIT[u["kit"]]["coin"],
                 org_tags=u["org_tags"], bond_seeds=u["bond_seeds"], hooks=u["hooks"],
                 birth_pool=u["branches"] + u["tags"], budget_units=u["units"], tradeoff=u["tradeoff"], backstory=[],
                 lifecycle="provisional", basis=["C:P4", "00.3.13", "02.4.4", "DL-02-05", "DL-02-10"])
        if u["id"] == "orig.up.bonded": e["birth_circumstance"] = "hard"
        out.append(e)
    for t in TRADES:
        m = t.get("magic")
        lic = [lic_of(x) for x in t["deep"] + t["access"]] + t.get("grants", [])
        e = dict(id=t["id"], name=t["name"], kind="livelihood", gloss=t["gloss"], tags=t["branches"], attribute_rules=None,
                 trainings=t["trainings"])
        if m:
            e["magic"] = dict(branch=m["branch"], casting_attribute=m["casting_attribute"],
                              schools=["%s.%s" % (m["branch"], s) for s in m["schools"]], requires_satisfied_by=m["requires"])
        if t.get("grants"): e["grants"] = t["grants"]
        if t.get("birth_circumstance"): e["birth_circumstance"] = t["birth_circumstance"]
        e.update(licenses=lic, competence=[dict(tag=x, value=2) for x in t["deep"]], languages=[],
                 defaults=dict(profile=t["profile"], deep=t["deep"], access=t["access"], technique=t["technique"],
                               attribute_priority=t["priority"], upbringing=t["upbringing"]),
                 technique_suggestions=t["techniques"], kit_id=t["kit"], kit=kit_items(t["kit"]), coin=KIT[t["kit"]]["coin"],
                 org_tags=t["org_tags"], bond_seeds=t["bond_seeds"], drive_seeds=t["drives"],
                 aspiration_seeds=[dict(text=a, tags=g) for a, g in t["aspirations"]], hooks=t["hooks"],
                 birth_pool=t["branches"], tradeoff="Which trainings are on your list, which kit you carry and which hooks follow you. The breadth profile (02.5.2) decides how many you take and how deep; a magic livelihood spends its deep pick on one school.",
                 backstory=[], lifecycle="provisional",
                 basis=["C:P4", "C:P5", "C:VII", "02.4.5", "02.5.2", "DL-02-06", "DL-02-07"])
        out.append(e)
    return out

HEAD_ORIGINS = """# data/origins.yaml
# Purpose: every origin a new character is assembled from. An origin is one of three KINDS, and a character takes
#   exactly one of each: a PEOPLE (who you were born; sets the attribute rule, one innate gift, your tongues),
#   an UPBRINGING (where you grew; sets base Focus, letters, tongues, one or two access licenses, your purse) and
#   a LIVELIHOOD (what you did before the story; sets the list your trainings are picked from, your kit, your hooks).
#   Nothing here grants a calling, a tier, a calling-partition ability or any evidence (02.1.3, 02.11.1).
# Owner: 02-character (T-00-19). Owner-block: 13 (setting origins) under `blocks:`.
# Schema: data/SCHEMAS.md#originsyaml. Required fields are present on every entry; `attribute_rules` is null for
#   upbringings and livelihoods (only a people sets attributes). Optional fields added by ch.02 (T-02-14): kind, gloss,
#   description, focus_base, license_choice, language_picks, extra_access_trainings, wealth, kit_id, coin, org_tags,
#   bond_seeds, drive_seeds, aspiration_seeds, trainings, magic, grants, defaults, technique_suggestions,
#   birth_circumstance, budget_units, backstory, and inside attribute_rules: floors, shapes, uncommon_of_kind.
# Reading a LIVELIHOOD: `trainings` is the list picks are made from (02.5); `licenses`, `competence` and `kit` hold the
#   FAST-PATH DEFAULT (what the character gets if the player makes no pick); `defaults` names those picks.
# Reading `attribute_rules`: `shapes` are the arrays the player may choose among; `fixed` pins a value to an
#   attribute; `floors` are minimums; `free_points` = sum minus the fixed values (schema field; no pool is spent).
# `backstory` is declared and EMPTY on every entry: ordinary creation writes no evidence (02.11.1, DL-02-14).
# `hooks` use the micro-format "<kind>: <text>", kind in thread | rumor | npc | place | debt | enemy | question (02.9.7).
# Languages: {license, grade}; grades broken < accented < native (data/licenses.yaml owner-block 02).
# GENERATED and validated by scratchpad ch02/gen02.py from authored tables (ids checked against tags.yaml,
#   licenses.yaml, abilities.yaml; budgets and placements checked mechanically).
# Basis: [C:P1] [C:P2] [C:P4] [C:P11] [C:VII] [00.3.6] [00.4.3] [00.4.4] [R1 02, #14] [R2 02, #10] [R3 02.1-02.7]
#   [R4 9 02] [R5 CC-01..CC-13] [DL-02-01..DL-02-23]

schema_version: 1
lifecycle: provisional
kinds: [people, upbringing, livelihood]
take: {people: 1, upbringing: 1, livelihood: 1}
attribute_shapes:
  free: {sum: 5, peaked: [3, 2, 1, 0, 0, 0, -1], even: [2, 2, 1, 1, 0, 0, -1], broad: [2, 1, 1, 1, 1, 0, -1]}
  typical: {sum: 7, peaked: [3, 2, 2, 1, 0, 0, -1], even: [2, 2, 2, 2, 0, 0, -1], broad: [2, 2, 2, 1, 1, 0, -1]}
profiles:
"""

def emit_origins():
    s = HEAD_ORIGINS
    for p in PROFILES: s += "  - " + flow(p) + "\n"
    s += "upbringing_budget: {units: 3, focus_5: 2, focus_4: 1, focus_3: 0, license: 1, language: 1, letters: 1}\n"
    s += "wealth_coin: {destitute: 1, poor: '3-8', modest: '12-20', comfortable: 30}\n"
    s += CREATION_BLOCK
    s += "\norigins:\n"
    cur = None
    for e in build_origins():
        if e["kind"] != cur:
            cur = e["kind"]; s += "\n  # ============================ %s ============================\n" % cur.upper()
        s += entry(e, flow_keys=("tags", "trainings", "licenses", "birth_pool", "org_tags", "basis", "backstory", "technique_suggestions", "grants")) + "\n"
    s += "\nblocks: []   # chapter 13 adds setting origins here: [{owner: \"13\", entries: [...]}], each passing PR-02-9\n"
    return s

# ---------- gen_birth ----------
def knack_entries():
    out = []
    for t in LEVEL2:
        br = ".".join(t.split(".")[:2]); leaf = t.split(".")[2]
        m1 = re.search(r"id: %s,?\s+name: \"?([^,\"\n]+)" % re.escape(t), tags_txt)
        nm = m1.group(1)
        out.append(dict(id="birth.knack.%s_%s" % (t.split(".")[1], leaf), name="A knack for " + nm.strip().lower(), layer="knack",
                        tags=[t], gate_tags=[br], excluded_tags=[], mod_group="knack", weight=2, min_tier=1,
                        tiers=[dict(tier=1, effects=[dict(effect_id="eff.check_edge", params=dict(amount=1, applies_when="deed_tag at or under " + t))])],
                        text="+1 edge on checks whose primary deed tag is at or under %s." % t,
                        lifecycle="provisional", basis=["02.6.2", "DL-02-08"]))
    return out
def trait_entries():
    out = []
    for tr in TRAITS:
        out.append(dict(id=tr["id"], name=tr["name"], layer="quirk", tags=tr["tags"], gate_tags=tr["gate"], excluded_tags=[],
                        mod_group="quirk", weight=tr["weight"], min_tier=1, tiers=[dict(tier=1, effects=tr["effects"])],
                        text=tr["text"], lifecycle="provisional", basis=["02.6.2", "DL-02-08"]))
    return out
def gift_entries():
    out = []
    for s, nm, ab, txt in GIFTS:
        tag = "deed.primal." + s
        if isinstance(ab, dict):
            # revision I-015 (the spark): the element is named by the player or drawn by the engine with equal
            # weights at the gift draw (02.6.3); the gifted working is that element's min_tier-1 working.
            els = list(ab)
            out.append(dict(id="birth.gift." + s, name=nm, layer="gift", tags=[tag, "trait.nature.magical"], gate_tags=[tag], excluded_tags=[],
                            mod_group="gift", weight=1, signature_of=["orig.life.touched"], signature_eligible=True, min_tier=1,
                            element=dict(choices=els, chosen_by="the player's concept names it; otherwise the engine draws one, equal weights, in the same draw (02.6.3)"),
                            tiers=[dict(tier=1, effects=[
                                dict(effect_id="eff.grant_license", params=dict(license=lic_of(tag), grade="trained", duration="permanent")),
                                dict(effect_id="eff.write_fact", params=dict(subject="pc", predicate="accepted.primal." + s, value="innate")),
                                dict(effect_id="eff.write_fact", params=dict(subject="pc", predicate="spark.element", value="the element named or drawn: " + " | ".join(els))),
                                dict(effect_id="eff.grant_license", params=dict(license="gifted_ability_by_element[pc.spark.element]", grade="rank 1 (acquired partition, source.kind gift)", duration="permanent"))])],
                            competence=dict(tag=tag, value=2), gifted_ability="by_element", gifted_ability_by_element=dict(ab),
                            text=txt + " You hold %s as an innate training (+2) and, at rank 1, the working of your element: %s." % (lic_of(tag), ", ".join("%s (%s)" % (ABIL[ab[e]]["name"], e) for e in els)),
                            lifecycle="provisional", basis=["02.6.3", "04.2.7", "05.9.4", "DL-02-09", "I-015", "DL-02-24"]))
            continue
        out.append(dict(id="birth.gift." + s, name=nm, layer="gift", tags=[tag, "trait.nature.magical"], gate_tags=[tag], excluded_tags=[],
                        mod_group="gift", weight=1, signature_of=["orig.life.touched"], signature_eligible=True, min_tier=1,
                        tiers=[dict(tier=1, effects=[
                            dict(effect_id="eff.grant_license", params=dict(license=lic_of(tag), grade="trained", duration="permanent")),
                            dict(effect_id="eff.write_fact", params=dict(subject="pc", predicate="accepted.primal." + s, value="innate")),
                            dict(effect_id="eff.grant_license", params=dict(license=ab, grade="rank 1 (acquired partition, source.kind gift)", duration="permanent"))])],
                        competence=dict(tag=tag, value=2), gifted_ability=ab,
                        text=txt + " You hold %s as an innate training (+2) and %s at rank 1." % (lic_of(tag), ABIL[ab]["name"]),
                        lifecycle="provisional", basis=["02.6.3", "04.2.7", "05.9.4", "DL-02-09"]))
    return out
def bent_entries():
    out = []
    for a in ATTRS:
        out.append(dict(id="birth.bent." + a, name="A bent toward " + a.capitalize(), layer="bent", tags=BENT_GATES[a], gate_tags=BENT_GATES[a],
                        excluded_tags=[], excluded_when="the recipient's %s is +3 or more, or this entry was declined before" % a,
                        mod_group="bent", weight=1, min_tier=1, attribute=a,
                        tiers=[dict(tier=1, effects=[dict(effect_id="eff.02.bent", params=dict(attribute=a, amount=1))])],
                        text="%s +1, permanently (never above +3)." % a.capitalize(),
                        lifecycle="provisional", basis=["02.6.5", "00.4.3 a", "C:P1", "DL-02-11"]))
    return out

HEAD_BIRTH = """# data/gen_birth.yaml
# Purpose: the configuration of generator domain gen.birth (00.11): constitution P1's layered variance. One domain,
#   four layers (knack, quirk, gift, bent), two moments:
#     AT CREATION (applied; P1 "mandatory at character creation"): one KNACK (+1 edge on one level-2 deed tag) and
#       one QUIRK (a small permanent trace), and, for the Touched livelihood only, one GIFT (an innate primal license with
#       its first working) in the signature slot.
#     AFTER CREATION (never auto-applied; P1 "the player MAY defer it and gamble on a later reroll"): the BENT, a
#       +1 to one attribute, drawn at a reflection from the attributes the character's own resolved deeds have
#       exercised; the player accepts it, or defers and gambles on a later draw (02.6.5-02.6.7).
# Owner: 02-character (T-00-19). Schema: data/SCHEMAS.md#gen_birthyaml (domain keys + PoolEntry).
# SOURCE (pool-gating circumstance): the character. At creation its tags are the union of its three origins'
#   `birth_pool` lists (a people tag, deed branches, terrain tags), plus the school tag(s) named for a Touched
#   character. For a Bent draw its tags are the deed branches with at least 3 resolved frames since creation (02.6.5).
# CIRCUMSTANCE (fill-quality circumstance): how the character came through childhood (creation), or which Bent
#   draw this is (after creation).
# Optional fields added by ch.02 (T-02-14): on quality_rungs `magnitude_layers`; on PoolEntry `layer`, `text`,
#   `competence`, `gifted_ability`, `attribute`, `excluded_when`. `mod_group` equals `layer`, so 00.11.3 step 6
#   (remove the picked entry's mod_group) yields exactly one entry per layer.
# Degree is always `none`: no birth draw follows a resolved frame (00.11.2 allows `none` where the domain says so).
# All entries are tier 1 (a new character is band 1: tier_cap 1). Magnitudes are fixed (00.11.3 step 8).
# GENERATED by scratchpad ch02/gen02.py; knack entries are one per level-2 deed tag of tags.yaml (81).
# Basis: [C:P1] [C:P5 pool gate / fill quality] [00.11] [00.4.3 a] [R2 02 (The Land affinity; HWFWM awakening
#   stones; racial gifts)] [R3 02.2, 02.7] [R4 9 02 #2] [DL-02-08] [DL-02-09] [DL-02-11]

schema_version: 1
lifecycle: provisional
domain: gen.birth
output_kind: property          # layers knack, quirk, gift are properties (effect refs); layer bent is attribute_variance
allows_degree_none: true
circumstances:
  - {id: unremarked, default: true, true_only_when: "nothing unusual is recorded of the character's birth or childhood, or the player gave no account", false_for: "any account that names want, war, plague, servitude, exile, or a sign"}
  - {id: hard, true_only_when: "the upbringing is orig.up.bonded, or the player's account establishes want, war, plague, servitude or exile in childhood", false_for: "ordinary poverty or a strict household"}
  - {id: omened, true_only_when: "the player's account establishes a sign at the birth or in the cradle: a storm, a comet, an eclipse, a caul, a death in the house the same night, a seer's word", false_for: "a sign that came later in life (that is a hook, 02.9.7)"}
  - {id: gifted, true_only_when: "the character's livelihood is orig.life.touched", false_for: "every other livelihood, whatever the account says"}
  - {id: bent_first, true_only_when: "this is the character's first Bent draw (02.6.5)", false_for: "creation draws"}
  - {id: bent_again, true_only_when: "this is a Bent draw after a deferral (02.6.6)", false_for: "creation draws"}
fill_map:
  - {circumstance: unremarked, fill_method: weighted}
  - {circumstance: hard, fill_method: biased, bias_tag: deed.wilds.survival}
  - {circumstance: omened, fill_method: biased, bias_tag: trait.nature.magical}
  - {circumstance: gifted, fill_method: signature}      # signature slot: the gated gift entry; several gated in -> weighted among them
  - {circumstance: bent_first, fill_method: weighted}
  - {circumstance: bent_again, fill_method: weighted}
quality_map:
  - {circumstance: unremarked, degree: none, quality_rung: plain}
  - {circumstance: hard, degree: none, quality_rung: plain}
  - {circumstance: omened, degree: none, quality_rung: plain}
  - {circumstance: gifted, degree: none, quality_rung: marked}
  - {circumstance: bent_first, degree: none, quality_rung: latent}
  - {circumstance: bent_again, degree: none, quality_rung: latent}
quality_rungs:
  - {id: plain, signature_slots: 0, magnitude_slots: 2, magnitude_layers: [knack, quirk]}
  - {id: marked, signature_slots: 1, magnitude_slots: 2, signature_layer: gift, magnitude_layers: [knack, quirk]}
  - {id: latent, signature_slots: 0, magnitude_slots: 1, magnitude_layers: [bent]}
degree_effects: {critical_success: none, critical_failure: none}
tier_rule: {signature: 1, magnitude: 1}
recency_window: 5              # matters for successors: a successor's draws halve the predecessor's results
slot_cap: 4                    # gift + knack + quirk + bent
bias_rule: "an entry carries the bias tag when one of its `tags` equals the bias tag or descends from it; its weight is x3"
bent:
  eligible_after: "the creation window has closed (02.2.6) and at least one deed branch has 3 resolved frames with the PC as actor since creation"
  source_tags: "every deed branch with >= 3 such frames"
  offered_at: reflection
  answers: [accept, defer]
  deferrals_max: 2             # the third draw is accept-or-forgo
  declined_entries_excluded: true
  never_auto_applied: true
  cap: 3

pool:
"""
def emit_birth():
    s = HEAD_BIRTH
    for title, ents in (("GIFTS (signature layer; Touched only)", gift_entries()), ("QUIRKS (magnitude layer)", trait_entries()),
                        ("BENT (latent layer; after creation; attribute_variance)", bent_entries()), ("KNACKS (magnitude layer; one per level-2 deed tag)", knack_entries())):
        s += "  # ---- %s ----\n" % title
        for e in ents:
            if e["layer"] == "knack": s += "  - " + flow(e) + "\n"
            else: s += entry(e, flow_keys=("tags", "gate_tags", "excluded_tags", "basis", "signature_of", "competence")) + "\n"
    return s

HEAD_KITS = """# data/kits.yaml
# Purpose: starting kits. A new character receives TWO kits: the pack of its upbringing (clothes, sundries, coin)
#   and the kit of its livelihood (tools, arms). Items are named by `item.*` TAG, never by base-item id: chapter 08
#   resolves each tag to a base item of that tag (00.17.1 Q17), so this file needs none of 08's ids.
# Owner: 02-character (T-00-19). Schema: data/SCHEMAS.md#kitsyaml (id, name, items [{item_tag, quality, quantity}], coin).
# Optional fields added by ch.02: `note` on an item (narration seed for the resolved item; never mechanics);
#   `choices` [{pick, options [[items]]}] (the player picks one option; the fast path takes the first).
# Quality: `worn` | `common` | `fine` are ch.02's ASSUMED names for 08's lowest serviceable rung, its standard rung
#   and the rung above it (Interface request to 08: map or rename; the order is what matters).
# Coin: an integer in 08's base unit. ASSUMED scale: 1 coin = one day's plain food and lodging (Interface request to
#   08: confirm, or multiply every `coin` here by one constant).
# Every kit obeys 02.8.2: no item above `fine`; no magical property; at most light armor; weapons of weight light,
#   one-handed or bow only (T-06-6); at most one mount, quality worn.
# GENERATED by scratchpad ch02/gen02.py (item tags checked against tags.yaml).
# Basis: [00.17.1 Q17] [R1 02 "gear must not outclass innate abilities"] [R3 02.6] [R4 9 02 #5] [06 Interface request
#   to 02] [T-06-6] [DL-02-13]

schema_version: 1
lifecycle: provisional
quality_assumed: [worn, common, fine]
coin_unit_assumed: "1 coin = one day's plain food and lodging"

kits:
"""
def emit_kits():
    s = HEAD_KITS
    for k in KITS:
        e = dict(id=k["id"], name=k["name"], tags=sorted({".".join(i["item_tag"].split(".")[:2]) for i in k["items"]}), items=k["items"])
        if k.get("choices"): e["choices"] = [dict(pick=c["pick"], options=c["options"]) for c in k["choices"]]
        e.update(coin=k["coin"], lifecycle="provisional", basis=["02.8.1", "02.8.2", "DL-02-13"])
        s += entry(e, flow_keys=("tags", "basis")) + "\n"
    return s

# ---------- run ----------
if errors:
    print("VALIDATION ERRORS:"); [print("  -", e) for e in errors]; sys.exit(1)
print("validation ok: %d peoples, %d upbringings, %d trades, %d kits, %d traits, %d knacks" % (len(PEOPLES), len(UPBRINGINGS), len(TRADES), len(KITS), len(TRAITS), len(LEVEL2)))
print("level-2 deed tags on no trade list and no upbringing (reachable only by the off-list pick or in play):", len(unlisted), unlisted)

if EMIT:
    for fn, txt in (("origins.yaml", emit_origins()), ("gen_birth.yaml", emit_birth()), ("kits.yaml", emit_kits())):
        with open(os.path.join(D, fn), "w", encoding="utf-8", newline="\n") as f: f.write(txt)
        print("wrote", fn, len(txt.split()), "words")

def default_rule_typical(p, t):
    """02.3.5 (revision I-009): a non-human defaults to its Typical rule, except that a magic livelihood whose
    casting attribute (05.7.2) the Typical rule fixes at -1 defaults to the Free rule (02.3.4)."""
    if not p["floors"]:
        return False
    ca = (t.get("magic") or {}).get("casting_attribute")
    return not (ca and p["fixed"].get(ca, 0) < 0)

# ================= AUDITS =================
print("\n== A1. legal attribute placements ==")
for p in PEOPLES:
    typical = bool(p["floors"])
    shapes = SHAPES_TYPICAL if typical else SHAPES_FREE
    n = {k: len(placements(v, p["floors"], p["fixed"])) for k, v in shapes.items()}
    print("%-11s %s total %d" % (p["name"], n, sum(n.values())))
print("free rule (anyone, uncommon of kind):", {k: len(placements(v, {}, {})) for k, v in SHAPES_FREE.items()})
# envelope check
for shapes, sm in ((SHAPES_FREE, 5), (SHAPES_TYPICAL, 7)):
    for k, v in shapes.items():
        assert sum(v) == sm and max(v) <= 3 and min(v) >= -1 and v.count(-1) == 1, (k, v)

print("\n== A2. default placements (peaked shape) for each trade x people ==")
for t in TRADES:
    row = []
    for p in PEOPLES:
        typical = default_rule_typical(p, t)
        a = default_placement((SHAPES_TYPICAL if typical else SHAPES_FREE)["peaked"], p["floors"] if typical else {}, p["fixed"] if typical else {}, t["priority"])
        row.append("".join("%+d" % a[x] for x in ATTRS))
    print("%-13s %s" % (t["name"], "  ".join(row)))
print("order of attributes:", ATTRS, "| peoples:", [p["name"] for p in PEOPLES])

print("\n== A3. concept fit: best attainable weighted score, free (5) vs each typical people (6) ==")
# weights: primary 4, secondary 3, tertiary 2; every character also values Agility (Guard) 1, Endurance (Vitality) 1, Wits (tempo) 1, Resolve (dread) 1
CONCEPTS = {
 "warrior": ("might", "endurance", "agility"), "archer": ("agility", "wits", "endurance"), "rogue": ("agility", "wits", "presence"),
 "scholar": ("intellect", "wits", "presence"), "wizard": ("intellect", "wits", "resolve"), "priest": ("presence", "resolve", "wits"),
 "druid": ("resolve", "wits", "endurance"), "bard": ("presence", "agility", "wits"), "envoy": ("presence", "wits", "intellect"),
 "smith": ("might", "intellect", "endurance"), "scout": ("wits", "agility", "endurance"), "brawler": ("might", "endurance", "resolve"),
 "knight": ("might", "presence", "endurance"), "shaman": ("resolve", "presence", "wits"), "thief": ("agility", "wits", "intellect"),
 "captain": ("presence", "might", "wits"),
}
def score(a, c):
    w = dict.fromkeys(ATTRS, 1)      # a solo character meets every kind of check: every attribute is worth 1
    for k in ("agility", "endurance", "wits", "resolve"): w[k] += 1   # Guard, Vitality, tempo and notice, dread
    for k, x in zip(c, (4, 3, 2)): w[k] += x
    return sum(w[k] * a[k] for k in ATTRS)
def best(shapes, floors, fixed, c):
    return max(score(dict(zip(ATTRS, perm)), c) for v in shapes.values() for perm in placements(v, floors, fixed))
hdr = "%-9s free " % "concept" + " ".join("%-5s" % p["name"][:5] for p in PEOPLES if p["floors"])
print(hdr)
wins = Counter(); below = Counter(); diffs = defaultdict(list)
for cn, c in CONCEPTS.items():
    f = best(SHAPES_FREE, {}, {}, c)
    row = []
    for p in PEOPLES:
        if not p["floors"]: continue
        b = best(SHAPES_TYPICAL, p["floors"], p["fixed"], c)
        row.append(b)
        if b < f: below[p["name"]] += 1
        diffs[p["name"]].append(b - f)
    mx = max(row)
    for p, b in zip([p for p in PEOPLES if p["floors"]], row):
        if b == mx: wins[p["name"]] += 1
    print("%-9s %3d  " % (cn, f) + " ".join("%-5d" % b for b in row))
print("concepts (of 16) where the typical rule is best-or-tied among peoples:", dict(wins))
print("concepts (of 16) where the typical rule scores WORSE than the free rule:", dict(below))
print("mean (typical - free), min, max per people:", {k: ("%.1f" % (sum(v) / len(v)), min(v), max(v)) for k, v in diffs.items()})

print("\n== A4. knack pool by origin (size; chance the knack lands on a default deep training) ==")
knacks = knack_entries()
def knack_pool(branches):
    return [k for k in knacks if any(k["gate_tags"][0] == b for b in branches)]
sizes = []
for t in TRADES:
    u = UP[t["upbringing"]]
    br = set(t["branches"]) | set(u["branches"])
    pool = knack_pool(br)
    hit = sum(1 for k in pool if k["tags"][0] in t["deep"])
    sizes.append(len(pool))
    print("%-13s + %-22s branches %d pool %2d  P(on a deep training) %s" % (t["name"], u["name"], len(br), len(pool), "%d/%d = %.0f%%" % (hit, len(pool), 100.0 * hit / len(pool))))
allsizes = []
for t in TRADES:
    for u in UPBRINGINGS:
        for p in PEOPLES:
            br = set(t["branches"]) | set(u["branches"]) | ({p["branch"]} if p["branch"] else set())
            allsizes.append(len(knack_pool(br)))
print("over all %d people x upbringing x trade combinations: knack pool min %d, median %d, max %d" % (len(allsizes), min(allsizes), sorted(allsizes)[len(allsizes) // 2], max(allsizes)))
tw = sum(t["weight"] for t in TRAITS)
print("trait pool: %d entries, total weight %d (universal gate); uncanny weight %d -> unremarked %.1f%%, omened (x3) %.1f%%" % (
    len(TRAITS), tw, sum(t["weight"] for t in TRAITS if "trait.nature.magical" in t["tags"]),
    100.0 * sum(t["weight"] for t in TRAITS if "trait.nature.magical" in t["tags"]) / tw,
    100.0 * 3 * sum(t["weight"] for t in TRAITS if "trait.nature.magical" in t["tags"]) / (tw + 2 * sum(t["weight"] for t in TRAITS if "trait.nature.magical" in t["tags"]))))
hard_w = sum(t["weight"] for t in TRAITS if any(under(x, "deed.wilds.survival") for x in t["tags"]))
print("hardy traits (carry deed.wilds.survival): unremarked %.1f%%, hard (x3) %.1f%%" % (100.0 * hard_w / tw, 100.0 * 3 * hard_w / (tw + 2 * hard_w)))

print("\n== A5. the Bent: chance of ending with the attribute you want (n eligible, uniform, declined entries struck) ==")
def bent_strategy(n, k_good):
    """accept only if the draw is one of k_good wanted attributes; up to 3 draws (2 deferrals); returns P(get a wanted one)."""
    p = Fraction(0); miss = Fraction(1); pool = n
    for draw in range(3):
        if pool <= 0: break
        hit = Fraction(min(k_good, pool), pool)
        p += miss * hit
        miss *= (1 - hit)
        pool -= 1
    return p
for n in (2, 3, 4, 5, 6):
    print("n=%d  want 1 specific: accept-first %5.1f%%  defer-until-it-comes %5.1f%% (else forgo %5.1f%%) | want either of 2: %5.1f%%" % (
        n, 100.0 / n, 100 * float(bent_strategy(n, 1)), 100 * float(1 - bent_strategy(n, 1)), 100 * float(bent_strategy(n, 2))))
# which attributes become eligible for sample play styles
for style, brs in (("pure martial", ["deed.martial"]), ("martial + wilds", ["deed.martial", "deed.wilds"]), ("guile + influence", ["deed.guile", "deed.influence"]),
                   ("arcane + lore", ["deed.arcane", "deed.lore"]), ("divine + influence", ["deed.divine", "deed.influence"]), ("craft only", ["deed.craft"])):
    el = [a for a in ATTRS if any(b in BENT_GATES[a] for b in brs)]
    print("  %-18s eligible: %s" % (style, ", ".join(el)))

print("\n== A6. starting numbers: ranges ==")
print("Vitality base = 12 + Endurance: creation range", 12 - 1, "to", 12 + 3, "| lifetime (-2..+4):", 10, "to", 16)
print("Focus base by upbringing:", {u["name"]: u["focus_base"] for u in UPBRINGINGS})
print("dread threshold 8 + Resolve: creation", 7, "to", 11)
# check odds table for the specialist/untrained lines (exhaustive d20, step rule)
def odds(mod, dc):
    cs = s = f = cf = 0
    for d in range(1, 21):
        tot = d + mod; m = tot - dc
        deg = 3 if m >= 10 else 2 if m >= 0 else 1 if m > -10 else 0
        if d == 20: deg = min(3, deg + 1)
        if d == 1: deg = max(0, deg - 1)
        cs += deg == 3; s += deg == 2; f += deg == 1; cf += deg == 0
    return (cs + s) * 5, cs * 5, cf * 5
for label, mod in (("untrained, attribute 0 (floor)", 1), ("access training, attribute +2", 3), ("deep training, attribute +2", 4), ("deep, attribute +3 (P1 specialist)", 5), ("deep, +3, knack on the tag", 6), ("forced low -1 (floor)", 0)):
    print("%-36s mod %+d: " % (label, mod) + "  ".join("DC%d %3d%%" % (dc, odds(mod, dc)[0]) for dc in (10, 15, 20, 25)))

print("\n== A7. totals a character can hold at creation ==")
print("training licenses: min", 2 + 1, "(focused + cloister... ) see chapter; max = broad 5 + upbringing 2 + human 1 + Intellect 3 =", 5 + 2 + 1 + 3)
