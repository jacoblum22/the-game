#!/usr/bin/env python3
"""09-gen_data09.py -- compiles and validates chapter 09's data files.

Reads the authored modules 09_data_powers.py, 09_data_arch.py (+2), 09_data_beh.py, 09_data_adv.py and
writes rules/data/archetypes.yaml, adversaries.yaml, behaviors.yaml, plus the contrib fragments
data/contrib/effects.09.yaml and tags.09.yaml. Every adversary's numbers come from PR-09-1 (archetype +
band + role + variant -> stat block), including the Vitality solve against the band's standard line
(09.4.4) using 09_core.estimate. Validates every id against the canonical data files; runs chapter 08's
loot pool check (gen_loot contract_09: pool >= 3 at tier cap 1 for every base) on the result.
Deterministic. Usage: python 09-gen_data09.py   (prints a report; writes the files)
"""
import importlib.util
import math
import os
import sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "data"))
sys.path.insert(0, HERE)


def load_mod(name):
    s = importlib.util.spec_from_file_location(name.replace("-", "_"), os.path.join(HERE, name + ".py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


C = load_mod("09_core")
PW = load_mod("09_data_powers")
A1 = load_mod("09_data_arch")
A2 = load_mod("09_data_arch2")
BH = load_mod("09_data_beh")
RO = load_mod("09_data_adv")
Y = lambda f: yaml.safe_load(open(os.path.join(DATA, f), encoding="utf-8"))

# ------------------------------------------------------------------ canonical id sets
TAGS = {t["id"] for t in Y("tags.yaml")["tags"]} | {f["id"] for f in Y("tags.yaml")["facets"]}
for f in os.listdir(os.path.join(DATA, "..", "_process", "merged-contrib")):
    if f.startswith("tags."):
        d = yaml.safe_load(open(os.path.join(DATA, "..", "_process", "merged-contrib", f), encoding="utf-8")) or {}
        for blk in d.get("blocks", []) or []:
            for e in blk.get("entries", []):
                TAGS.add(e["id"])
        for e in d.get("tags", []) or []:
            TAGS.add(e["id"])
EFFECTS = {e["id"] for e in Y("effects.yaml")["core"]}
for f in os.listdir(os.path.join(DATA, "..", "_process", "merged-contrib")):
    if f.startswith("effects."):
        d = yaml.safe_load(open(os.path.join(DATA, "..", "_process", "merged-contrib", f), encoding="utf-8")) or {}
        for blk in d.get("blocks", []) or []:
            for e in blk.get("entries", []):
                EFFECTS.add(e["id"])
CONDS = {c["id"] for c in Y("conditions.yaml")["conditions"]}
for blk in (yaml.safe_load(open(os.path.join(DATA, "..", "_process", "merged-contrib", "conditions.07.yaml"), encoding="utf-8")) or {}).get("blocks", []):
    for e in blk.get("entries", []):
        CONDS.add(e["id"])
ABIL = {a["id"] for a in Y("abilities.yaml")["abilities"]}
AFF = {a["id"] for a in Y("afflictions.yaml")["afflictions"]}
BASE = {b["id"]: b for b in Y("base_items.yaml")["base_items"]}
IP = Y("item_properties.yaml")
FLAWS = {f["id"] for f in IP["flaws"]}
ABSORB = Y("gen_absorb.yaml")
ABS_POOL = {p["id"]: p for p in ABSORB["pool"]}
MATS = Y("materials.yaml")["materials"]
DISPOSITIONS = ["capture", "ransom", "rob", "drive_off", "drag_to_lair", "leave", "kill"]
CAPTIVE = ["trial", "sale", "sacrifice", "interrogation", "ransom", "labor", "the larder"]
NERVES = {"skittish": 4, "steady": 6, "resolute": 8, "fearless": None}
BREAKS = ["flee", "yield", "cower", "frenzy", "fighting_withdrawal"]
SIZES = ["tiny", "small", "medium", "large", "huge", "colossal"]
ROLES = ["soldier", "brute", "skirmisher", "archer", "caster", "controller", "leader", "lurker", "swarm", "solo"]
VARIANTS = ["minion", "standard", "elite", "solo"]
MINDS = ["mindless", "animal", "cunning", "sapient", "alien"]
LETTER = {"A": "apex", "H": "high", "M": "mid", "L": "low", "F": "feeble", "N": "none"}
ATTRS = ["might", "agility", "endurance", "wits", "intellect", "presence", "resolve"]
ALET = dict(zip("MAEWIPR", ATTRS))
STD_SEV = {1: 2, 2: 2, 3: 3, 4: 3, 5: 4}
HEAVY_SEV = {1: 3, 2: 3, 3: 4, 4: 4, 5: 5}
ARMOR = {("natural", "none"): [0] * 5, ("natural", "hide"): [0, 1, 1, 2, 2], ("natural", "plate"): [1, 2, 2, 3, 3],
         ("worn", "none"): [0] * 5, ("worn", "light"): [1] * 5, ("worn", "medium"): [2] * 5, ("worn", "heavy"): [3] * 5}
ELITE_MULT = {1: 2.0, 2: 2.0, 3: 2.0, 4: 1.25, 5: 1.25}
SOLO_MULT = {1: 4.0, 2: 3.0, 3: 3.0, 4: 1.75, 5: 1.5}
FOCUS_BASE = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}
LORE_BASE = {1: "easy", 2: "easy", 3: "moderate", 4: "hard", 5: "very_hard"}
TIER_LADDER = ["easy", "moderate", "hard", "very_hard", "legendary"]
RARITY_SHIFT = {"common": 0, "uncommon": 1, "rare": 2, "legendary": 3}
PREMIUM = {"rider": 0.06, "action": 0.06, "aura": 0.06, "lesser": 0.03, "summon": 0.10, "ability": 0.04}
LESSER = {"pow.frenzy", "pow.shield_wall", "pow.pack_tactics", "pow.ambush_strike", "pow.mend_kin", "pow.blink",
         "pow.glamour", "pow.spell_turning", "pow.rally_cry", "pow.call_kin", "pow.drag_off", "pow.second_wind", "pow.shrug"}
FREE = {"pow.flight", "pow.swimmer", "pow.climber", "pow.burrower", "pow.night_eyes", "pow.keen_scent", "pow.tremorsense",
        "pow.mindless", "pow.deathless", "pow.unliving", "pow.amorphous", "pow.incorporeal", "pow.regenerate"}

errors = []
warn = []


def err(msg):
    errors.append(msg)


def tag_ok(t, where):
    if t not in TAGS:
        err("%s: unknown tag %s" % (where, t))


def matches(g, s):
    return s == g or s.startswith(g + ".")


# ------------------------------------------------------------------ powers and degree tables
POWERS = {p["id"]: p for p in PW.POWERS}
DTABLES = {d["id"]: d for d in PW.DEGREE_TABLES}


def check_effect(e, where):
    if e["effect_id"] not in EFFECTS:
        err("%s: unknown effect %s" % (where, e["effect_id"]))
    pr = e.get("params", {})
    c = pr.get("condition")
    if c and c not in CONDS:
        err("%s: unknown condition %s" % (where, c))
    for c2 in (pr.get("forbid", {}) or {}).get("conditions", []) if isinstance(pr.get("forbid"), dict) else []:
        if c2 not in CONDS:
            err("%s: unknown condition %s" % (where, c2))
    dt = pr.get("degree_table")
    if dt and dt not in DTABLES and dt not in AFF:
        err("%s: unknown degree table %s" % (where, dt))
    for t in pr.get("harm_tags", []) if isinstance(pr.get("harm_tags"), list) else []:
        if t.startswith("harm."):
            tag_ok(t, where)
    for sub in pr.get("effects", []) if isinstance(pr.get("effects"), list) else []:
        check_effect(sub, where)


for p in PW.POWERS:
    for e in p["effects"]:
        check_effect(e, p["id"])
for d in PW.DEGREE_TABLES:
    for k in ("critical_success", "success", "failure", "critical_failure"):
        for e in d[k]:
            check_effect(e, d["id"])

# ------------------------------------------------------------------ behaviors
BEH = {b["id"]: b for b in BH.BEHAVIORS}
for b in BH.BEHAVIORS:
    for r in b["rows"]:
        for part in r["when"].replace("|", "&").split("&"):
            pr = part.strip()
            if pr not in BH.PREDICATES:
                err("%s: unknown predicate %s" % (b["id"], pr))
        if r["do"] not in BH.MACROS:
            err("%s: unknown macro %s" % (b["id"], r["do"]))
        if r["do"] == "use" and r["arg"] and r["arg"].startswith("pow.") and r["arg"] not in POWERS:
            err("%s: unknown power %s" % (b["id"], r["arg"]))

# ------------------------------------------------------------------ archetypes
ARCH = {}
for a in A1.ARCHETYPES + A2.ARCHETYPES:
    if a["id"] in ARCH:
        err("duplicate archetype " + a["id"])
    ARCH[a["id"]] = a
    w = a["id"]
    for t in a["creature_tags"] + a["harm_tags"] + a["evidence_tags"] + a["org_tags"]:
        tag_ok(t, w)
    for t in a["terrain"]:
        tag_ok(t, w)
    if len(a["attrs"]) != 7 or any(ch not in LETTER for ch in a["attrs"]):
        err(w + ": bad attrs " + a["attrs"])
    if any(ch not in ALET for ch in a["trained"]):
        err(w + ": bad trained " + a["trained"])
    for p in a["powers"]:
        if p not in POWERS:
            err("%s: unknown power %s" % (w, p))
    for k in a["attacks"]:
        for r in k["riders"]:
            if r not in POWERS:
                err("%s: unknown rider %s" % (w, r))
        for t in k["harm"]:
            tag_ok(t, w)
    for e in a["traits"]:
        check_effect(e, w)
    for b in a["behaviors"]:
        if b not in BEH:
            err("%s: unknown behavior %s" % (w, b))
    if a["disposition"] not in DISPOSITIONS:
        err("%s: disposition %s" % (w, a["disposition"]))
    if a["captive_fate"] and a["captive_fate"] not in CAPTIVE:
        err("%s: captive_fate %s" % (w, a["captive_fate"]))
    if a["nerve"] not in NERVES:
        err("%s: nerve %s" % (w, a["nerve"]))
    if a["mind"] not in MINDS:
        err("%s: mind %s" % (w, a["mind"]))
    if a["size"] not in SIZES:
        err("%s: size %s" % (w, a["size"]))
    for g in a["gear"]:
        if g not in BASE:
            err("%s: unknown gear %s" % (w, g))
    fl = a["loot"].get("flaw")
    if fl and fl not in FLAWS:
        err("%s: unknown flaw %s" % (w, fl))
    sig = a["absorb"].get("signature")
    if sig:
        if sig not in ABS_POOL:
            err("%s: unknown absorb signature %s" % (w, sig))
        elif not any(matches(g, t) for g in ABS_POOL[sig]["gate_tags"] for t in a["creature_tags"]):
            err("%s: absorb signature %s gate %s does not match %s" % (w, sig, ABS_POOL[sig]["gate_tags"], a["creature_tags"]))
    for x in a["absorb"].get("cannot_absorb", []):
        if x not in ABS_POOL:
            err("%s: unknown cannot_absorb %s" % (w, x))
    if a["lore"][0] not in TAGS:
        err("%s: lore tag %s" % (w, a["lore"][0]))


def brk_of(a):
    if a["nerve"] == "fearless":
        return None
    b = {"fight": None, "leave": "flee"}.get(a["brk"], a["brk"])
    if b is not None and b not in BREAKS:
        err("%s: break %s" % (a["id"], b))
    return b


NO_POOL = ABSORB["no_pool"]   # revision I-020: read from gen_absorb.yaml (the human-like folk), never hard-coded


def absorbable(a):
    ct = a["creature_tags"]
    natural_folk = any(t.startswith(("creature.folk.giant", "creature.folk.beastfolk")) for t in ct)
    if ct and all(any(matches(n, t) for n in NO_POOL) for t in ct):
        return {"pool": "none", "reason": "gen_absorb no_pool: the human-like folk (learned arts, not natural powers)"}
    pool = [p for p, e in ABS_POOL.items()
            if any(matches(g, t) for g in e["gate_tags"] for t in ct)
            and not any(matches(x, t) for x in (e.get("excluded_tags") or []) for t in ct)]
    out = {"pool_gate_tags": ct, "eligible": sorted(pool), "cannot_absorb": a["absorb"].get("cannot_absorb", [])}
    if a["absorb"].get("signature"):
        out["signature"] = a["absorb"]["signature"]
    if natural_folk:
        out["natural_folk"] = "giant-kin and beastfolk carry natural powers: gen_absorb's no_pool covers only the human-like folk (I-020)"
    return out


# ------------------------------------------------------------------ PR-09-1: the stat block
def rung(letter, band):
    return C.RUNG[LETTER[letter]][band]


def lore_tier(a, band):
    i = TIER_LADDER.index(LORE_BASE[band]) + RARITY_SHIFT[a["lore"][1]]
    return TIER_LADDER[min(i, len(TIER_LADDER) - 1)]


def power_premium(powers, riders, abilities):
    p = 0.0
    for x in set(powers) | set(riders):
        if x in FREE:
            continue
        if x in riders:
            p += PREMIUM["rider"]
        elif x in LESSER:
            p += PREMIUM["lesser"]
        elif x == "pow.summon_dead":
            p += PREMIUM["summon"]
        elif POWERS[x]["kind"] == "trigger" and x in ("pow.heat_aura", "pow.cold_aura", "pow.unholy_aura"):
            p += PREMIUM["aura"]
        else:
            p += PREMIUM["action"]
    p += PREMIUM["ability"] * len(abilities)
    return min(0.4, p)


def build(v):
    a = ARCH[v["arch"]]
    b = v["band"]
    w = v["id"]
    if not (a["bands"][0] <= b <= a["bands"][1]):
        err("%s: band %d outside %s's range %s" % (w, b, a["id"], a["bands"]))
    if v["role"] not in ROLES:
        err("%s: role %s" % (w, v["role"]))
    if v["variant"] not in VARIANTS:
        err("%s: variant %s" % (w, v["variant"]))
    c = C.BAND_COMP[b]
    attrs = v["attrs"] or a["attrs"]
    at = {ATTRS[i]: rung(attrs[i], b) for i in range(7)}
    trained = set(ALET[ch] for ch in a["trained"])
    gear = v["gear"] if v["gear"] is not None else a["gear"]
    shield = 1 if any("shield" in g for g in gear) else 0
    defenses = {"guard": 10 + at["agility"] + c + shield}
    for x in ATTRS:
        defenses[x] = 10 + at[x] + (c if x in trained else 0)
    tempo = 10 + at["wits"]
    # attacks
    names = v["attacks"] or [k["id"] for k in a["attacks"]]
    atks = []
    for k in a["attacks"]:
        if k["id"] not in names:
            continue
        heavy = bool(k["heavy"])
        sev = (HEAVY_SEV[b] if heavy else STD_SEV[b]) + k["off"]
        sev = max(1, min(5, sev))
        if sev >= 4 or k["shape"]:
            heavy = True
        atks.append(dict(id=k["id"], name=k["name"], verb=k["verb"], attribute=k["attr"],
                         modifier=at[k["attr"]] + c, harm={"severity": "S%d" % sev, "harm_tags": k["harm"]},
                         bands=k["bands"], weight=k["weight"], action_cost=1, shape=k["shape"], windup=heavy,
                         site=k["site"], riders=k["riders"], primary=bool(k.get("primary"))))
    if not atks:
        err(w + ": no attacks")
        return None
    # the primary attack by role
    ranged = [x for x in atks if x["weight"] in ("bow", "crossbow")]
    working = [x for x in atks if x["weight"] == "working"]
    if v["role"] == "archer" and ranged:
        prim = ranged[0]
    elif v["role"] in ("caster",) and working:
        prim = working[0]
    else:
        prims = [x for x in atks if x["primary"] and not x["windup"]] or [x for x in atks if not x["windup"]] or atks
        prim = prims[0]
    for x in atks:
        x["primary"] = x is prim
    variant = v["variant"]
    if variant == "solo" and not any(x["windup"] for x in atks):
        hv = dict(prim)
        hv.update(id=prim["id"] + "_full", name=prim["name"] + " (full force)", windup=True, primary=False,
                  harm={"severity": "S%d" % HEAVY_SEV[b], "harm_tags": prim["harm"]["harm_tags"]})
        atks.append(hv)
    heavy_sev = max([int(x["harm"]["severity"][1]) for x in atks if x["windup"] and not x["shape"]] or [0]) or None
    # armor and resistances
    arm = v["armor"] or a["armor"]
    red = ARMOR[tuple(arm)][b - 1]
    if arm[0] == "worn":
        names_g = " ".join(gear)
        red = 3 if "plate" in names_g else 2 if ("mail" in names_g or "scale" in names_g or "brigandine" in names_g) else 1 if any(x in names_g for x in ("leather", "hide", "padded")) else red
    powers = [p for p in a["powers"] + v["powers"] if p not in v["drop_powers"]]
    powers = list(dict.fromkeys(powers))
    if variant == "solo":
        powers += ["pow.shrug", "pow.second_wind"]
    for p in powers:
        mb = POWERS[p].get("min_band")
        if mb and b < mb:
            err("%s: power %s needs band %d" % (w, p, mb))
    riders = sorted({r for x in atks for r in x["riders"]})
    taken = 1.0
    for e in a["traits"]:
        if e["effect_id"] == "eff.harm_resistance":
            ht = e["params"]["harm_tags"]
            if "harm.physical" in ht:
                taken = min(taken, 0.5)
            elif any(t.startswith("harm.physical.") for t in ht):
                taken = min(taken, 0.75)
    if "pow.incorporeal" in powers:
        taken = min(taken, 0.5)
    regen = 3 if "pow.regenerate" in powers else 0
    # nerve and reactions
    nerve = a["nerve"]
    if variant == "minion" and nerve in ("steady", "resolute"):
        nerve = {"steady": "skittish", "resolute": "steady"}[nerve]
    if variant in ("elite", "solo") and nerve in ("skittish", "steady"):
        nerve = {"skittish": "steady", "steady": "resolute"}[nerve]
    eff_band = b + (1 if variant == "elite" else 0)
    if variant == "minion" or v["members"] > 1:
        reaction = []
    elif variant == "solo":
        reaction = ["opportunity_strike", "fend"]
    else:
        reaction = [] if eff_band <= 1 else ["opportunity_strike"] if eff_band == 2 else ["opportunity_strike", "fend"]
    if a["reaction"] is False:
        reaction = []
    fend = "fend" in reaction
    # Vitality: solve against the band's standard (09.4.4), then the variant multiplier
    std = C.std(b)
    pc = C.pc_line(b)
    r_std = C.estimate(pc, [std])[2]
    prem = power_premium(powers, riders, v["abilities"])
    target = r_std / (1.0 + prem)
    line = dict(atk=prim["modifier"], guard=defenses["guard"], sev=int(prim["harm"]["severity"][1]),
                heavy=heavy_sev, red=red, fend=fend, morale=NERVES[nerve], tempo=tempo, taken=taken, regen=regen,
                swarm=v["swarm"])
    lo, hi = C.ENVELOPE_VIT[b]
    tol = (0.5, 2.0) if b == 1 else (0.67, 1.5)
    solve_line = dict(line, taken=1.0, regen=0)       # 09.4.4: solved as if the PC holds the counter

    def solve():
        best = None
        for vit in range(lo, hi + 1):
            solve_line["vit"] = vit
            r = C.estimate(pc, [solve_line])[2]
            d = abs(math.log(max(r, 1e-6)) - math.log(max(target, 1e-6)))
            if best is None or d < best[0]:
                best = (d, vit, r)
        return best[1], (best[2] / target if target > 0 else 1.0)
    base_vit, fidelity = solve()
    comp = 0
    last_step = 0
    while (fidelity > tol[1] and base_vit == lo or fidelity < tol[0] and base_vit == hi) and abs(comp) < 2:
        step = -1 if fidelity > tol[1] else 1                # 09.4.5: one severity rung on the primary
        if step == -last_step:                               # integration fix: an oscillating compensation never ends
            break
        last_step = step
        if not (1 <= solve_line["sev"] + step <= 5):
            break
        comp += step
        solve_line["sev"] += step
        if solve_line.get("heavy"):
            solve_line["heavy"] = max(1, min(5, solve_line["heavy"] + step))
        base_vit, fidelity = solve()
    if comp:
        for x in atks:
            s0 = int(x["harm"]["severity"][1])
            if x["primary"] or (x["windup"] and not x["shape"]):
                x["harm"]["severity"] = "S%d" % max(1, min(5, s0 + comp))
        line["sev"] = solve_line["sev"]
        line["heavy"] = solve_line.get("heavy")
        for x in atks:
            if int(x["harm"]["severity"][1]) >= 4 or x["shape"]:
                x["windup"] = True
    if fidelity < tol[0] or fidelity > tol[1]:
        warn.append("%s: band fidelity %.2f after %+d severity rung(s) (Vitality %d at the envelope %s)" % (w, fidelity, comp, base_vit, (lo, hi)))
    mult = {"minion": 0.5, "standard": 1.0, "elite": ELITE_MULT[b], "solo": SOLO_MULT[b]}[variant]
    vit = max(1, int(round(base_vit * mult)))
    line["vit"] = vit
    focus = FOCUS_BASE[b] + (1 if variant == "elite" else 2 if variant == "solo" else 0) + (1 if v["role"] == "caster" else 0)
    if variant == "minion":
        focus = 0
    # effect DCs for the attributes its powers use
    dc_attrs = set()
    for p in powers + riders:
        for e in POWERS[p]["effects"]:
            src = e["params"].get("effect_dc_source")
            if src:
                dc_attrs.add(src.split(".")[1])
    effect_dc = {x: 10 + at[x] + c for x in sorted(dc_attrs)}
    # advisory of this adversary alone vs each power band (members as built)
    adv_alone = {}
    adv_nocounter = {}
    for pb in range(1, 6):
        foe = dict(line, members=v["members"], leader=v["leader"])
        wv, sv, _ = C.estimate(C.pc_line(pb), [dict(foe, taken=1.0, regen=0)])
        adv_alone["P%d" % pb] = C.classify_sim(wv, sv)
        if taken < 1.0 or regen:
            wv, sv, _ = C.estimate(C.pc_line(pb), [foe])
            adv_nocounter["P%d" % pb] = C.classify_sim(wv, sv)
    disp = v["disposition"] or a["disposition"]
    lethal = v["lethal"] if v["lethal"] is not None else (a["lethal"] or disp == "kill")
    s4 = any(int(x["harm"]["severity"][1]) >= 4 for x in atks)
    ctags = v["ctags"] or a["creature_tags"]
    for t in ctags:
        tag_ok(t, w)
    competence = [{"tag": t, "value": c} for t in a["evidence_tags"]]
    competence.append({"tag": "deed.martial.unarmed", "value": c})
    size = v["size"] or a["size"]
    beh = list(a["behaviors"])
    if v["members"] > 1:
        beh = ["beh.09.swarm" if v["swarm"] else "beh.09.mob"]
    if variant == "solo":
        beh = ["beh.09.solo_overlay"] + beh
    tells = dict(a["tells"])
    if v["presence"]:
        tells["presence"] = v["presence"]
    entry = {
        "id": w, "name": v["name"], "archetype": a["id"], "threat_band": b, "variant": variant, "role": v["role"],
        "default_behavior_role": "mob" if v["members"] > 1 else (a["beh_role"] or "melee"),
        "tags": list(dict.fromkeys(ctags + a["harm_tags"])), "creature_tags": ctags, "size": size,
        "members": v["members"], "swarm": v["swarm"], "leader": v["leader"], "npc_depth": v["depth"],
        "attributes": at, "competence": competence, "defenses": defenses, "tempo": tempo,
        "vitality": vit if v["members"] == 1 else {"per_member": vit, "pool": vit * v["members"]},
        "reduction": {"amount": red, "harm_tags": ["harm.physical"], "kind": arm[0], "no_gaps": a["no_gaps"] if arm[0] == "natural" else False},
        "resistances": a["traits"], "attacks": atks, "abilities": v["abilities"], "powers": powers, "focus": focus,
        "effect_dc": effect_dc, "reaction": {"count": 1 if reaction else 0, "kinds": reaction},
        "behaviors": beh, "morale": {"nerve": nerve, "segments": NERVES[nerve], "break_then": None if nerve == "fearless" else brk_of(a)},
        "pace": v["pace"] if v["pace"] is not None else a["pace"],
        "tells": tells, "weak_spot": a["weak"], "lethal_context": bool(lethal), "lethal_causes": sorted(set((["archetype"] if lethal else []) + (["severity"] if s4 else []))),
        "defeat_disposition": disp, "kill_when": a["kill_when"], "captive_fate": a["captive_fate"],
        "can_bargain": a["can_bargain"], "dread": a["dread"], "speaks": a["speaks"], "mind": a["mind"],
        "reaction_roll": a["reaction_roll"], "objective": a["objective"] or {"kill": "kill", "capture": "capture", "rob": "rob", "ransom": "capture", "drive_off": "drive_off", "drag_to_lair": "capture", "leave": "defeat"}[disp],
        "lore": {"deed_tag": a["lore"][0], "rarity": a["lore"][1], "dc_tier": lore_tier(a, b)},
        "loot": {"yield": "none" if v["members"] > 1 and a["loot"].get("yield") == "none" else ("always" if v["depth"] == "principal" else a["loot"].get("yield", "trophy")),
                 "tier_cap": b, "trophy_base": a["loot"].get("trophy_base"), "flaw": a["loot"].get("flaw"),
                 "gear": gear, "purse": a["purse"]},
        "advisory_alone": adv_alone,
        "advisory_without_counter": adv_nocounter or None,
        "counter": ("the harm or weapon its resistance does not cover (" + ", ".join(sorted({t for e in a["traits"] if e["effect_id"] == "eff.harm_resistance" for t in e["params"]["harm_tags"]})) + ")" if taken < 1.0 else None) if not regen else "fire or acid (stops regeneration)",
        "calibration": {"premium": round(prem, 2), "solved_vitality": base_vit, "fidelity": round(fidelity, 2), "severity_compensation": comp,
                        "line": {k: line[k] for k in ("atk", "guard", "sev", "heavy", "red", "fend", "morale", "tempo", "taken", "regen")}},
        "lifecycle": "provisional",
        "basis": ["09.4 PR-09-1", "09.3 T-09-3", a["id"]],
    }
    if v["note"]:
        entry["notes"] = v["note"]
    return entry


ADV = []
seen = set()
for v in RO.ROSTER:
    if v["id"] in seen:
        err("duplicate adversary " + v["id"])
    seen.add(v["id"])
    e = build(v)
    if e:
        ADV.append(e)

# ------------------------------------------------------------------ loot pool check (08.3.4 contract_09)
spec08 = importlib.util.spec_from_file_location("loot08", os.path.join(HERE, "08-loot-sim.py"))
L08 = None
try:
    src = open(os.path.join(HERE, "08-loot-sim.py"), encoding="utf-8").read()
    cut = src.index("# ---------------------------------------------------------------- reference archetypes")
    tail = src.index("def base_candidates")
    head = src[:cut] + src[tail:src.index("def contributions")]
    ns = {"__file__": os.path.join(HERE, "08-loot-sim.py")}
    exec(compile(head, "08-loot-sim-head", "exec"), ns)
    L08 = ns
except Exception as ex:  # pragma: no cover
    err("could not load 08's pool check: %r" % ex)

pool_report = []
if L08:
    TROPHY = L08["LOOT"]["base_selection"]["trophy_defaults"]
    for aid, a in ARCH.items():
        branch = ".".join(a["creature_tags"][0].split(".")[:2])
        tb = a["loot"].get("trophy_base")
        if a["loot"].get("yield") == "none":
            pool_report.append((aid, None, None, "yield none (materials only)"))
            continue
        if tb:
            bases = L08["base_candidates"](tb)
        elif a["gear"]:
            bases = a["gear"]
        else:
            bases = [x for t in TROPHY[branch] if t != "the source's own gear" for x in L08["base_candidates"](t)]
        src_tags = a["creature_tags"] + a["harm_tags"] + a["evidence_tags"] + a["org_tags"]
        sizes = []
        for bb in bases:
            hands = ["creature.folk"] if L08["BI"][bb]["kind"] in ("weapon", "armor", "shield") and a["creature_tags"][0].startswith(("creature.folk", "creature.undead")) else []
            sizes.append((len(L08["gated_pool"](src_tags + hands + L08["BI"][bb].get("material_tags", []), [], bb, 1)), bb))
        if not sizes:
            err("%s: trophy base %s resolves to no base item" % (aid, tb))
            continue
        lo = min(sizes)
        pool_report.append((aid, lo[0], lo[1], "ok" if lo[0] >= 3 else "BELOW 3"))

# ------------------------------------------------------------------ write
HDR = "# data/%s -- %s\n# Owner: 09-adversaries (T-00-19). Schema: data/SCHEMAS.md#%s plus chapter 09's optional fields (T-09-14).\n# GENERATED by rules/_process/simulation/09-gen_data09.py from 09_data_*.py (validated against tags, effects + contrib,\n#   conditions + contrib, abilities, afflictions, base_items, item_properties flaws, gen_absorb). Edit the script, not this file.\n# Every entry lifecycle: provisional (00.16.3). Basis: chapter 09 rules cited per entry.\n\n"


def dump(fname, purpose, obj):
    with open(os.path.join(DATA, fname), "w", encoding="utf-8") as fh:
        fh.write(HDR % (fname, purpose, fname.replace(".", "")))
        yaml.safe_dump(obj, fh, sort_keys=False, allow_unicode=True, width=130, default_flow_style=None)


def arch_entry(a):
    return {
        "id": a["id"], "name": a["name"], "tags": list(dict.fromkeys(a["creature_tags"] + a["harm_tags"])),
        "summary": a["summary"], "creature_tags": a["creature_tags"], "harm_tags": a["harm_tags"],
        "evidence_tags": a["evidence_tags"], "org_tags": a["org_tags"], "mind": a["mind"], "speaks": a["speaks"],
        "tongue": a["tongue"], "size": a["size"], "bands": a["bands"], "roles": a["roles"],
        "attribute_rungs": {ATTRS[i]: LETTER[a["attrs"][i]] for i in range(7)},
        "trained_defenses": [ALET[ch] for ch in a["trained"]],
        "armor": {"kind": a["armor"][0], "rung": a["armor"][1], "no_gaps": a["no_gaps"]},
        "attacks": [{k: x[k] for k in ("id", "name", "verb", "attr", "off", "harm", "bands", "weight", "heavy", "shape", "site", "riders", "primary")} for x in a["attacks"]],
        "powers": a["powers"], "traits": a["traits"], "cannot": a["cannot"], "behaviors": a["behaviors"],
        "default_behavior_role": a["beh_role"] or "melee",
        "morale": {"nerve": a["nerve"], "segments": NERVES[a["nerve"]], "break_then": brk_of(a)},
        "reaction": a["reaction"] if a["reaction"] is not None else "by_band",
        "reaction_roll": a["reaction_roll"], "pace": a["pace"],
        "lethal_context": bool(a["lethal"] or a["disposition"] == "kill"), "defeat_disposition": a["disposition"],
        "kill_when": a["kill_when"], "captive_fate": a["captive_fate"], "can_bargain": a["can_bargain"], "dread": a["dread"],
        "tells": a["tells"], "weak_spot": a["weak"],
        "loot": {"yield": a["loot"].get("yield", "trophy"), "trophy_base": a["loot"].get("trophy_base"),
                 "pool_gate_tags": a["loot"].get("pool_gate_tags", []), "flaw": a["loot"].get("flaw"),
                 "signature_property": a["loot"].get("signature_property", "default (item_properties.yaml#default_signatures)")},
        "gear": a["gear"], "purse": a["purse"], "harvest": a["harvest"] or "default (materials.yaml source_tags)",
        "absorbable": absorbable(a),
        "lore": {"deed_tag": a["lore"][0], "rarity": a["lore"][1]},
        "encounter": {"terrain": a["terrain"], "group": a["group"], "objective_default": a["objective"]},
        "lifecycle": "provisional",
        "basis": ["09.2", "R3 §6 #14", "R6 C-R5"],
    }


# revision I-020: gen_absorb.yaml records `signature_of` on each entry an archetype names as its signature;
# the two must agree, so a future archetype edit cannot leave the record stale.
_sig = {}
for _a in ARCH.values():
    _v = absorbable(_a).get("signature")
    if _v:
        _sig.setdefault(_v, set()).add(_a["id"])
for _pid, _p in ABS_POOL.items():
    if set(_p.get("signature_of") or []) != _sig.get(_pid, set()):
        err("gen_absorb %s: signature_of %s, but archetypes name it for %s" % (_pid, sorted(_p.get("signature_of") or []), sorted(_sig.get(_pid, set()))))


if not errors:
    dump("archetypes.yaml", "adversary archetypes as manufacturers: one tag set drives evidence, loot gate, absorbable pool, behavior (09.2)",
         {"schema_version": 1, "band_tables": {"competence": C.BAND_COMP, "rungs": C.RUNG, "standard": C.STANDARD,
                                               "standard_severity": STD_SEV, "heavy_severity": HEAVY_SEV,
                                               "armor": {"%s.%s" % k: v for k, v in ARMOR.items()},
                                               "variant_vitality": {"minion": 0.5, "standard": 1.0, "elite": ELITE_MULT, "solo": SOLO_MULT},
                                               "focus_base": FOCUS_BASE, "lore_base_tier": LORE_BASE, "power_premium": PREMIUM},
          "archetypes": [arch_entry(a) for a in ARCH.values()],
          "powers": PW.POWERS, "degree_tables": PW.DEGREE_TABLES})
    dump("adversaries.yaml", "the bestiary: fully statted adversaries, T1-T5, every creature branch (09.10)",
         {"schema_version": 1, "adversaries": ADV, "blocks": [{"owner": "13", "entries": []}]})
    dump("behaviors.yaml", "behavior priority lists, the closed predicate and macro vocabularies, encounter shaping tables (09.7, 09.8)",
         {"schema_version": 1, "predicates": BH.PREDICATES, "macros": BH.MACROS,
          "behaviors": [dict(id=b["id"], name=b["name"], tags=[], instinct=b["instinct"],
                             priority_list=[{k: r[k] for k in ("when", "do", "arg", "note") if r[k] is not None} for r in b["rows"]],
                             parley_when=b["parley_when"], yield_when=b["yield_when"], retreat_when=b["retreat_when"],
                             morale_break={"threshold": "the side's nerve (06.11.2)", "then": "the adversary's morale.break_then (06.11.5)"},
                             lifecycle="provisional", basis=["09.7", "06.9.1"]) for b in BH.BEHAVIORS],
          **load_mod("09_data_enc").ENCOUNTER})

# ------------------------------------------------------------------ report
print("archetypes:", len(ARCH), " adversaries:", len(ADV), " powers:", len(POWERS), " behaviors:", len(BEH),
      " degree tables:", len(DTABLES))
br = {}
for e in ADV:
    k = e["creature_tags"][0].split(".")[1]
    br.setdefault(k, []).append(e["threat_band"])
print("by branch (bands):", {k: sorted(v) for k, v in br.items()})
bc = {}
for e in ADV:
    bc[e["threat_band"]] = bc.get(e["threat_band"], 0) + 1
print("by band:", dict(sorted(bc.items())))
vc = {}
for e in ADV:
    vc[e["variant"]] = vc.get(e["variant"], 0) + 1
print("by variant:", vc)
print("errors:", len(errors))
for x in errors:
    print("  ERROR", x)
print("warnings:", len(warn))
for x in warn:
    print("  warn", x)
print("loot pools (min over bases, tier cap 1):")
for r in pool_report:
    print("  %-24s %s %s %s" % r)
print("adversary lines:")
for e in ADV:
    vit = e["vitality"] if isinstance(e["vitality"], int) else "%dx%d" % (e["members"], e["vitality"]["per_member"])
    p = [x for x in e["attacks"] if x["primary"]][0]
    print("  %-22s T%d %-8s %-10s atk %+3d %-3s Guard %2d red %d vit %-6s focus %d prem %.2f fid %.2f | %s" % (
        e["id"], e["threat_band"], e["variant"], e["role"], p["modifier"], p["harm"]["severity"], e["defenses"]["guard"],
        e["reduction"]["amount"], vit, e["focus"], e["calibration"]["premium"], e["calibration"]["fidelity"],
        " ".join("%s:%s" % (k, v[:4]) for k, v in e["advisory_alone"].items())))
sys.exit(1 if errors else 0)
