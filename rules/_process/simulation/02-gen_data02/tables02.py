# tables02.py -- renders the data-derived tables of chapter 02 as markdown (so no number is transcribed by hand)
import os as _os
_RULES = _os.environ.get('GAME_RULES', _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..')))
import sys, os, re, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from data02 import *
import yaml
D = _os.path.join(_RULES, 'data')
LIC = yaml.safe_load(open(os.path.join(D, "..", "_process", "merged-contrib", "licenses.02.yaml"), encoding="utf-8"))["blocks"][0]["entries"]
LN = {l["id"]: l["name"] for l in LIC}
AB = {}
for a in yaml.safe_load(open(os.path.join(D, "abilities.yaml"), encoding="utf-8"))["abilities"]:
    AB[a["id"]] = a
KIT = {k["id"]: k for k in KITS}
UPD = {u["id"]: u for u in UPBRINGINGS}
MINUS = "\u2212"
def plain(tag): return tag.split(".")[-1].replace("_", " ")
def tname(l):
    if l.startswith("lic.training."):
        return l.replace("lic.training.", "").split("_", 1)[1].replace("_", " ")
    return LN.get(l, l)
def sgn(v): return ("+%d" % v) if v > 0 else ((MINUS + "%d" % -v) if v < 0 else "0")
def placements(array, floors, fixed):
    out = set()
    for perm in set(itertools.permutations(array)):
        a = dict(zip(ATTRS, perm))
        if all(a[k] == v for k, v in fixed.items()) and all(a[k] >= v for k, v in floors.items()): out.add(perm)
    return out
def default_placement(array, floors, fixed, priority):
    best = None
    for perm in placements(array, floors, fixed):
        a = dict(zip(ATTRS, perm)); key = tuple(a[x] for x in priority)
        if best is None or key > best[0]: best = (key, a)
    return best[1]
out = {}
# ---- T-02-2 peoples
r = ["| People | Rule | Must hold | Fixed | Gift (license; literal effect) | Tongues | Birth-pool branch |", "|---|---|---|---|---|---|---|"]
GT = {"lic.people.starsight": "**Starsight**: dim light is no hindrance to your sight (night-sight for 06.3.7's dim rule)",
      "lic.people.stonesense": "**Stonesense**: underground you always know down, depth and the way back; Precision lever on Observe and Recall about worked stone, mines, tunnels, caves",
      "lic.people.underfoot": "**Underfoot**: Precision lever on Sneak while a crowd or a larger creature is between you and the watcher",
      "lic.people.iron_blood": "**Iron blood**: hazards of venom and disease count one severity rung lighter",
      "lic.people.cave_eyes": "**Cave-eyes**: in darkness you see to `band.close` as others see in dim light",
      "lic.people.great_frame": "**Great frame**: +1 edge on Force and Grapple",
      "lic.people.keen_nose": "**Keen nose**: Precision lever on Observe by scent"}
def lname(l): return LN[l].replace("the ", "")
for p in PEOPLES:
    typ = bool(p["floors"])
    must = ", ".join("%s \u2265 %s" % (k.capitalize(), sgn(v)) for k, v in sorted(p["floors"].items(), key=lambda kv: -kv[1])) if typ else "\u2014"
    fx = ", ".join("%s %s" % (k.capitalize(), sgn(v)) for k, v in p["fixed"].items()) if typ else "\u2014"
    gift = GT[p["gift"]] if p["gift"] else "**Adaptable**: one extra training held as access (02.4.3)"
    tg = ", ".join("%s (%s)" % (lname(l), g) for l, g in p["languages"]) + ("; one more of choice (accented)" if p.get("language_choice") else "")
    r.append("| **%s** | %s | %s | %s | %s | %s | %s |" % (p["name"], "Typical +7, or Free +5" if typ else "Free +5", must, fx, gift, tg, ("`%s`" % p["branch"]) if p["branch"] else "\u2014"))
out["T-02-2"] = "\n".join(r)
# ---- T-02-4 upbringings
r = ["| Upbringing | Raised in | Focus | Licenses (held as access) | Letters | Tongues | Purse | Birth-pool branches | Organization kinds |", "|---|---|---|---|---|---|---|---|---|"]
for u in UPBRINGINGS:
    lic = [tname(l) for l in u["licenses"] if l != "lic.lang.letters"]
    if u["choice"]: lic.append("one of " + " / ".join(tname(l) for l in u["choice"]["of"]))
    tg = [("%s (%s)" % (lname(l), g)) for l, g in u["languages"]] + (["one of choice (accented)"] if u["language_picks"] else [])
    r.append("| **%s** | %s | **%d** | %s | %s | %s | %s, %d coin | %s | %s |" % (u["name"], u["desc"], u["focus_base"], "; ".join(lic) or "\u2014", "yes" if u["letters"] else "no", "; ".join(tg) or "\u2014", u["wealth"], KIT[u["kit"]]["coin"], ", ".join(b.split(".")[1] for b in u["branches"]), ", ".join(o.replace("org.", "") for o in u["org_tags"])))
out["T-02-4"] = "\n".join(r)
# ---- T-02-5 livelihoods
r = ["| Livelihood | Training list (level-2 deed tags) | Default profile and picks | Default upbringing | Kit (first option); coin |", "|---|---|---|---|---|"]
ITEM = {"item.shield.light": "round shield", "item.armor.light.leather": "leather armor", "item.armor.light.padded": "padded armor",
        "item.tool.light": "light", "item.tool.trade": "tools of the work", "item.tool.kit.thieves": "thieves' tools", "item.tool.kit.healer": "healer's kit",
        "item.tool.kit.climbing": "rope and hook", "item.tool.kit.disguise": "disguise kit", "item.weapon.axe.hand": "hand axe",
        "item.goods.trade": "trade goods", "item.goods.document": "document", "item.tool.container": "pack", "item.consumable.food": "food",
        "item.weapon.ammunition.arrow": "arrows", "item.weapon.ammunition.stone": "sling stones", "item.conveyance.mount": "riding horse",
        "item.tool.implement.holy_symbol": "holy symbol", "item.consumable.remedy": "remedies", "item.consumable.oil": "oil",
        "item.weapon.blade.dagger": "dagger", "item.garment.clothing": "clothing"}
def iname(tag): return ITEM.get(tag, plain(tag))
def kitline(kid):
    k = KIT[kid]; items = list(k["items"]) + [i for c in k.get("choices", []) for i in c["options"][0]]
    names = []
    for i in items:
        names.append(iname(i["item_tag"]) + (" \u00d7%d" % i["quantity"] if i["quantity"] > 1 else "") + (" (%s)" % i["quality"] if i["quality"] != "common" else ""))
    alt = ""
    if k.get("choices"):
        alt = "; in place of the %s: %s" % (iname(k["choices"][0]["options"][0][0]["item_tag"]), " / ".join(" and ".join(iname(i["item_tag"]) for i in o) for o in k["choices"][0]["options"][1:]))
    return ", ".join(names) + alt + "; %d coin" % k["coin"]
for t in TRADES:
    lst = ", ".join("%s.%s" % (x.split(".")[1], x.split(".")[2]) for x in t["trainings"])
    if t.get("magic"): lst = "**one school of %s** (%s); " % (t["magic"]["branch"].split(".")[1], ", ".join(t["magic"]["schools"])) + lst
    if t.get("grants"): lst += "; grants Letters"
    d = "**%s**: deep %s" % (t["profile"].capitalize(), " + ".join(plain(x) for x in t["deep"]) or "\u2014")
    if t["access"]: d += "; access " + ", ".join(plain(x) for x in t["access"])
    if t["technique"]: d += "; technique *%s*" % AB[t["technique"]]["name"]
    r.append("| **%s** (%s) | %s | %s | %s | %s |" % (t["name"], t["gloss"], lst, d, UPD[t["upbringing"]]["name"], kitline(t["kit"])))
out["T-02-5"] = "\n".join(r)
# ---- T-02-6 default placements
def code(a): return " ".join(sgn(a[x]) for x in ATTRS)
r = ["| Livelihood (priority) | " + " | ".join(p["name"] for p in PEOPLES) + " |", "|---|" + "---|" * len(PEOPLES)]
for t in TRADES:
    cells = []
    for p in PEOPLES:
        ca = (t.get("magic") or {}).get("casting_attribute")
        typ = bool(p["floors"]) and not (ca and p["fixed"].get(ca, 0) < 0)   # 02.3.5 caster exception (I-009)
        cell = code(default_placement((SHAPES_TYPICAL if typ else SHAPES_FREE)["peaked"], p["floors"] if typ else {}, p["fixed"] if typ else {}, t["priority"]))
        cells.append(cell + ("†" if bool(p["floors"]) and not typ else ""))
    r.append("| %s (%s) | %s |" % (t["name"], " ".join(x[:3].capitalize() for x in t["priority"]), " | ".join(cells)))
out["T-02-6"] = "\n".join(r)
# ---- T-02-7 gifts
r = ["| Gift | School (innate license, competence +2) | First working (rank 1, acquired partition) | Its literal text | Focus |", "|---|---|---|---|---|"]
for s, nm, ab, txt in GIFTS:
    if isinstance(ab, dict):   # the spark: one working per element (revision I-015)
        for el, x in ab.items():
            a = AB[x]
            r.append("| **%s** (%s) | `deed.primal.%s` | *%s* (`%s`) | %s | %s |" % (nm, el, s, a["name"], x, a["scope"], a["cost"]["focus"] if a.get("cost") else 0))
        continue
    a = AB[ab]
    r.append("| **%s** | `deed.primal.%s` | *%s* (`%s`) | %s | %s |" % (nm, s, a["name"], ab, a["scope"], a["cost"]["focus"] if a.get("cost") else 0))
out["T-02-7"] = "\n".join(r)
# ---- T-02-8 traits
r = ["| Quirk | What the player is told | Effect reference | Weight | Tripled by manner |", "|---|---|---|---|---|"]
for t in TRAITS:
    e = t["effects"][0]
    if e["effect_id"] == "eff.grant_lever": ref = "`eff.grant_lever` %s; verbs %s; when %s" % (e["params"]["type"], ", ".join(v.replace("verb.", "") for v in e["params"]["for_verbs"]), e["params"]["applies_when"])
    elif e["effect_id"] == "eff.hazard_step": ref = "`eff.hazard_step` %s1 rung; %s; when %s" % (MINUS, ", ".join(e["params"]["harm_tags"]), e["params"]["applies_when"])
    else: ref = "`%s` %s" % (e["effect_id"], e["params"]["sealed_ref"])
    carries = "hard" if any(x == "deed.wilds.survival" or x.startswith("deed.wilds.survival.") for x in t["tags"]) else ""
    if "trait.nature.magical" in t["tags"]: carries = (carries + ", " if carries else "") + "omened"
    gate = "" if t["gate"] == ["creature.folk"] else " *(only if the pool holds %s)*" % " or ".join(g.split(".", 1)[1] if g.startswith("terrain") else g.split(".")[1] for g in t["gate"])
    r.append("| **%s**%s | %s | %s | %d | %s |" % (t["name"], gate, t["text"], ref, t["weight"], carries or "\u2014"))
out["T-02-8"] = "\n".join(r)
# ---- T-02-9 knack pools
tags_txt = open(os.path.join(D, "tags.yaml"), encoding="utf-8").read()
L2 = sorted(set(re.findall(r"id: (deed\.[a-z_]+\.[a-z_]+)[,\n]", tags_txt)))
assert len(L2) == 81, len(L2)
def pool(brs): return [t for t in L2 if ".".join(t.split(".")[:2]) in brs]
r = ["| Livelihood + its default upbringing (human) | Branches in the pool | Knacks eligible | Chance the knack lands on a default deep training |", "|---|---|---|---|"]
for t in TRADES:
    u = UPD[t["upbringing"]]; brs = sorted(set(t["branches"]) | set(u["branches"]))
    pl = pool(brs); hit = sum(1 for k in pl if k in t["deep"])
    r.append("| %s + %s | %s | %d | %d in %d (%.0f%%) |" % (t["name"], u["name"], ", ".join(b.split(".")[1] for b in brs), len(pl), hit, len(pl), 100.0 * hit / len(pl)))
out["T-02-9"] = "\n".join(r)
bc = {}
for t in L2: bc[t.split(".")[1]] = bc.get(t.split(".")[1], 0) + 1
out["branch_counts"] = ", ".join("%s %d" % (k, v) for k, v in bc.items())
# ---- T-02-10 bent gates
r = ["| Attribute (`birth.bent.*`) | In the pool when the character has 3 or more resolved frames in any of |", "|---|---|"]
for a in ATTRS: r.append("| %s | %s |" % (a.capitalize(), ", ".join("`%s`" % b for b in BENT_GATES[a])))
out["T-02-10"] = "\n".join(r)
r2 = ["| If the character has worked only in | The Bent pool holds |", "|---|---|"]
for b in ["martial", "guile", "wilds", "lore", "arcane", "divine", "primal", "influence", "craft"]:
    r2.append("| %s | %s |" % (b, ", ".join(a.capitalize() for a in ATTRS if "deed." + b in BENT_GATES[a])))
out["T-02-10b"] = "\n".join(r2)
# ---- T-02-13 fate's hand
O = yaml.safe_load(open(os.path.join(D, "origins.yaml"), encoding="utf-8"))
NM = {e["id"]: e["name"] for e in O["origins"]}
r = []
for t in O["tables"]:
    r.append("- `%s` (d100): " % t["id"] + " \u00b7 ".join("%s %s" % (("%d\u2013%d" % tuple(x["range"])) if x["range"][0] != x["range"][1] else str(x["range"][0]), NM[x["result"]]) for x in t["results"]))
out["T-02-13"] = "\n".join(r)
# ---- T-02-3 the P4 audit
CONCEPTS = {
 "warrior": ("might", "endurance", "agility"), "archer": ("agility", "wits", "endurance"), "rogue": ("agility", "wits", "presence"),
 "scholar": ("intellect", "wits", "presence"), "wizard": ("intellect", "wits", "resolve"), "priest": ("presence", "resolve", "wits"),
 "druid": ("resolve", "wits", "endurance"), "bard": ("presence", "agility", "wits"), "envoy": ("presence", "wits", "intellect"),
 "smith": ("might", "intellect", "endurance"), "scout": ("wits", "agility", "endurance"), "brawler": ("might", "endurance", "resolve"),
 "knight": ("might", "presence", "endurance"), "shaman": ("resolve", "presence", "wits"), "thief": ("agility", "wits", "intellect"),
 "captain": ("presence", "might", "wits"),
}
def score(a, c):
    w = dict.fromkeys(ATTRS, 1)
    for k in ("agility", "endurance", "wits", "resolve"): w[k] += 1
    for k, x in zip(c, (4, 3, 2)): w[k] += x
    return sum(w[k] * a[k] for k in ATTRS)
def best(shapes, floors, fixed, c):
    return max(score(dict(zip(ATTRS, perm)), c) for v in shapes.values() for perm in placements(v, floors, fixed))
TP = [p for p in PEOPLES if p["floors"]]
r = ["| Concept (first, second, third attribute) | Free (+5) | " + " | ".join(p["name"] for p in TP) + " |", "|---|---|" + "---|" * len(TP)]
diffs = {p["name"]: [] for p in TP}
for cn, c in CONCEPTS.items():
    f = best(SHAPES_FREE, {}, {}, c); cells = []
    for p in TP:
        b = best(SHAPES_TYPICAL, p["floors"], p["fixed"], c); diffs[p["name"]].append(b - f)
        cells.append(("**%d**" % b) if b > f else ("%d" % b if b == f else "*%d*" % b))
    r.append("| %s (%s) | %d | %s |" % (cn, ", ".join(x[:3].capitalize() for x in c), f, " | ".join(cells)))
r.append("| **mean difference from Free** | | " + " | ".join(("%+.1f" % (sum(v) / len(v))).replace("-", MINUS) for v in diffs.values()) + " |")
r.append("| **best / worst difference** | | " + " | ".join(("%+d / %+d" % (max(v), min(v))).replace("-", MINUS) for v in diffs.values()) + " |")
r.append("| **concepts better / equal / worse than Free** | | " + " | ".join("%d / %d / %d" % (sum(1 for x in v if x > 0), sum(1 for x in v if x == 0), sum(1 for x in v if x < 0)) for v in diffs.values()) + " |")
out["T-02-3"] = "\n".join(r)
tpl = open(os.path.join(HERE, "part6_template.md"), encoding="utf-8").read()
for k, v in out.items(): tpl = tpl.replace("{{%s}}" % k, v)
assert "{{" not in tpl, re.findall(r"\{\{[^}]+\}\}", tpl)
open(os.path.join(HERE, "part6.md"), "w", encoding="utf-8", newline="\n").write(tpl)
print("part6.md written", len(tpl.split()), "words"); print(out["branch_counts"])
