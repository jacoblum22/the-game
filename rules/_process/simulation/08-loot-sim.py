#!/usr/bin/env python3
"""sim08.py -- chapter 08's loot/craft simulation. Implements PR-08-1 (loot) and PR-08-5 (craft) over the
generated data files exactly as the chapter states them, then reports drop rates, rung and property-count
distributions, gated pool sizes, repeat rates, bound-power and relic shares, and item-layer budget compliance.
Seeded and deterministic. Copy kept at rules/_process/simulation/08-loot-sim.py; output at 08-loot-sim-output.txt.
"""
import random, collections, statistics, os, sys
import yaml

D = os.environ.get("GAME_RULES_DATA", os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")))
L = lambda f: yaml.safe_load(open(os.path.join(D, f), encoding="utf-8"))
BI = {b["id"]: b for b in L("base_items.yaml")["base_items"]}
IP = L("item_properties.yaml")
PROPS = IP["properties"]
DEFSIG = IP["default_signatures"]
LOOT = L("gen_loot.yaml")
IA = L("gen_item_ability.yaml")
MATS = {m["id"]: m for m in L("materials.yaml")["materials"]}

def matches(g, s):
    return s == g or s.startswith(g + ".")
def anymatch(gates, tags):
    return any(matches(g, t) for g in gates for t in tags)

SHARE = {"edge": 1, "harm_edge": 1, "reduction": 3, "carry": 4, "supply_use": -1}

# ---------------------------------------------------------------- reference archetypes (the 09 contract test set)
A = lambda id, tags, harm, band, gear=None, trophy=None, deeds=(), orgs=(), yld="trophy": dict(id=id, tags=tags, harm=harm, band=band, gear=gear, trophy=trophy, deeds=list(deeds), orgs=list(orgs), yld=yld)
ARCH = [
 A("wolf", ["creature.beast.predator.canine"], ["harm.physical.pierce"], 2),
 A("dire_bear", ["creature.beast.predator.ursine", "creature.beast.monstrous.dire"], ["harm.physical.cut"], 3),
 A("giant_spider", ["creature.beast.vermin.arachnid"], ["harm.venom.poison"], 2),
 A("great_serpent", ["creature.beast.reptile.serpent"], ["harm.venom.poison"], 2),
 A("griffon", ["creature.beast.monstrous.hybrid", "creature.beast.avian"], ["harm.physical.cut"], 3),
 A("bandit", ["creature.folk.human"], ["harm.physical.cut"], 1, gear=["bi.sword", "bi.leather", "bi.dagger", "bi.shortbow"], deeds=["deed.martial.blade", "deed.guile.ambush"], orgs=["org.outlaw.bandits"]),
 A("orc_raider", ["creature.folk.orc"], ["harm.physical.cut"], 2, gear=["bi.battle_axe", "bi.hide", "bi.round_shield", "bi.javelin"], deeds=["deed.martial.axe"]),
 A("goblin_skulk", ["creature.folk.goblin"], ["harm.physical.pierce"], 1, gear=["bi.knife", "bi.sling", "bi.padded"], deeds=["deed.guile.stealth"]),
 A("troll", ["creature.folk.giant.troll"], ["harm.physical.crush"], 3, gear=["bi.maul", "bi.hide"]),
 A("knight_errant", ["creature.folk.human"], ["harm.physical.cut"], 3, gear=["bi.sword", "bi.mail", "bi.kite_shield", "bi.lance"], deeds=["deed.martial.blade"], orgs=["org.order.knightly"]),
 A("skeleton", ["creature.undead.mindless.skeleton"], ["harm.physical.cut"], 1),
 A("ghoul", ["creature.undead.ravenous.ghoul"], ["harm.blight.disease"], 2),
 A("wraith", ["creature.undead.spectral.wraith"], ["harm.blight.necrotic"], 3),
 A("lich", ["creature.undead.sovereign.lich"], ["harm.blight.necrotic", "harm.arcane.raw"], 5, deeds=["deed.arcane.necromancy"]),
 A("dryad", ["creature.spirit.fey.wild"], ["harm.mind.psychic"], 2),
 A("barrow_shade", ["creature.spirit.ancestor"], ["harm.frost.cold"], 2),
 A("lesser_demon", ["creature.fiend.demon.lesser"], ["harm.fire.flame"], 3),
 A("tempter", ["creature.fiend.devil.tempter"], ["harm.mind.psychic"], 4),
 A("stone_golem", ["creature.construct.golem.stone"], ["harm.physical.crush"], 3),
 A("clockwork_sentinel", ["creature.construct.clockwork"], ["harm.physical.pierce"], 2),
 A("fire_elemental", ["creature.elemental.fire"], ["harm.fire.flame"], 3),
 A("rime_wyrmling", ["creature.dragon.great.wyrmling"], ["harm.frost.cold"], 4),
 A("wyvern", ["creature.dragon.wyvern"], ["harm.venom.poison"], 4),
 A("slime", ["creature.horror.ooze.slime"], ["harm.corrosion.acid"], 2),
 A("elder_dragon", ["creature.dragon.great.elder"], ["harm.fire.flame"], 5),
 A("mind_flayer", ["creature.horror.aberration"], ["harm.mind.psychic"], 4),
]
PLACES = [[], [], ["terrain.forest.woodland"], ["terrain.ruin.tomb.barrow"], ["terrain.frozen.tundra"], ["terrain.underground.cave"], ["terrain.wetland.marsh"], ["terrain.highland.mountains"]]
TROPHY = LOOT["base_selection"]["trophy_defaults"]

def base_candidates(tag):
    if tag.startswith("bi."):
        return [tag]
    return [b for b, e in BI.items() if tag in e["item_tags"] or any(t.startswith(tag + ".") for t in e["item_tags"]) if e.get("trophy_eligible", True) is not False and e["kind"] in ("weapon", "armor", "shield", "garment", "jewelry", "tool")]

def branch(tags):
    return ".".join(tags[0].split(".")[:2])

def sig_for(arch):
    for t in arch["tags"]:
        parts = t.split(".")
        for i in range(len(parts), 2, -1):
            k = ".".join(parts[:i])
            if k in DEFSIG:
                return DEFSIG[k]
    return None

def base_ok(p, base):
    return any(matches(k, t) for k in p["base_kinds"] for t in BI[base]["item_tags"])

def saturated(p, base):
    b = BI[base]
    if p.get("family") == "harm_edge" and "versatile" in b.get("weapon_properties", []):
        return True
    if p["id"] == "prop.guarding" and ("parrying" in b.get("weapon_properties", []) or b["kind"] == "shield"):
        return True
    if p.get("family") == "reduction" and p["id"] == "prop.reinforced" and b.get("armor_class") == "heavy":
        return True
    return False

def gated_pool(src_tags, place_tags, base, cap, domain="loot"):
    out = []
    for p in PROPS:
        if domain not in p["domains"]:
            continue
        tags = src_tags + (place_tags if p.get("place_gated") else [])
        if not anymatch(p["gate_tags"], tags):
            continue
        if p["excluded_tags"] and anymatch(p["excluded_tags"], src_tags):
            continue
        if not base_ok(p, base) or saturated(p, base):
            continue
        if p["min_tier"] > cap:
            continue
        out.append(p)
    return out

def contributions(p, tier):
    """what one property contributes to capped families at a tier (for the item share check)"""
    c = collections.Counter()
    rows = [r for r in p["tiers"] if r["tier"] <= tier]
    if not rows:
        return c
    row = max(rows, key=lambda r: r["tier"])
    for e in row["effects"]:
        eid, pa = e["effect_id"], e["params"]
        if eid == "eff.check_edge":
            c["edge:check:" + str(pa.get("applies_when", ""))[:60]] += pa["amount"]
        elif eid == "eff.defense_edge":
            c["edge:defense:" + pa.get("attribute", "")] += pa["amount"]
        elif eid == "eff.effect_dc_edge":
            c["edge:dc"] += pa["amount"]
        elif eid == "eff.harm_edge":
            c["harm_edge"] += pa["amount"]
        elif eid == "eff.strike_delivery":
            c["harm_edge"] += pa.get("harm_edge", 0)
        elif eid == "eff.harm_reduction":
            for h in pa["harm_tags"]:
                c["reduction:" + h] += pa["amount"]
        elif eid == "eff.08.adjust" and pa["quantity"] == "carry":
            c["carry"] += pa["amount"]
        elif eid == "eff.08.adjust" and pa["quantity"] == "supply_use":
            c["supply_use"] += pa["amount"]
        elif eid == "eff.hazard_step":
            for h in pa["harm_tags"]:
                c["step:" + h] += pa["steps"]
    return c

def base_contrib(base):
    c = collections.Counter()
    b = BI[base]
    for wp in b.get("weapon_properties", []):
        if wp in ("parrying", "shield_light", "shield_heavy"):
            c["edge:defense:agility"] += 1
        if wp == "versatile":
            c["harm_edge"] += 1
    if b.get("reduction"):
        for h in b["reduction"]["harm_tags"]:
            c["reduction:" + h] += b["reduction"]["amount"]
    return c

def violates(total):
    if any(v > 1 for k, v in total.items() if k.startswith("edge:")):
        return True
    if total["harm_edge"] > 1 or total["carry"] > 4 or total["supply_use"] < -1:
        return True
    if any(v < -1 for k, v in total.items() if k.startswith("step:")):
        return True
    return any(v > 3 for k, v in total.items() if k.startswith("reduction:"))

QR = {r["id"]: r for r in LOOT["quality_rungs"]}
QMAP = {(q["circumstance"], q["degree"]): q["quality_rung"] for q in LOOT["quality_map"]}
FILL = {f["circumstance"]: f for f in LOOT["fill_map"]}

class Gen:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.recent = collections.deque(maxlen=5)
        self.log = collections.Counter()

    def weight(self, p, bias=None):
        w = p["weight"]
        if bias and p.get("bias") == bias:
            w *= 3
        if p["id"] in self.recent:
            w = w / 2
        return w

    def draw(self, cands, bias=None):
        ws = [self.weight(p, bias) for p in cands]
        return self.rng.choices(cands, weights=ws, k=1)[0]

    def chosen(self, cands, bias=None):
        shown = []
        pool = list(cands)
        for _ in range(min(3, len(pool))):
            p = self.draw(pool, bias)
            shown.append(p); pool.remove(p)
        return self.rng.choice(shown)  # the simulated player picks among the shown three

    def item_ability(self, arch, circ, tier):
        cands = []
        src = arch["tags"] + arch["deeds"] + arch["orgs"]
        for e in IA["pool"]:
            if e["min_tier"] > tier:
                continue
            if e["source"].startswith("gen_absorb") and anymatch(e["gate_tags"], arch["tags"]):
                cands.append(e)
            elif e["source"].startswith("abilities") and anymatch(e["gate_tags"], src + self.deed_map(arch)):
                cands.append(e)
        if not cands:
            return None
        return self.rng.choices(cands, weights=[c["weight"] for c in cands], k=1)[0]

    def deed_map(self, arch):
        out = []
        m = IA["source_to_deed"]
        for t in arch["tags"]:
            best = None
            for k in m:
                if matches(k, t) and (best is None or k.count(".") > best.count(".")):
                    best = k
            if best:
                out += [d for d in m[best] if d.startswith("deed.")]
        return out

    def generate(self, arch, circ, degree, place, force_rung=None):
        cap = arch["band"]
        rung = force_rung or QMAP[(circ, degree)]
        sigs, mags = QR[rung]["signature_slots"], QR[rung]["magnitude_slots"]
        method = FILL[circ]["fill_method"]
        bias = FILL[circ].get("bias_tag")
        src = arch["tags"] + arch["harm"] + arch["deeds"] + arch["orgs"]
        # base selection (signature-honoring when the fill is signature)
        if arch["gear"]:
            bases = list(arch["gear"])
        else:
            bases = []
            for t in TROPHY[branch(arch["tags"])]:
                if t == "the source's own gear":
                    continue
                bases += base_candidates(t)
        signature = None
        if method == "signature" and sigs:
            sid = sig_for(arch)
            sp = next((p for p in PROPS if p["id"] == sid), None)
            if sp and sp["min_tier"] <= cap:
                fit = [b for b in bases if base_ok(sp, b)]
                if not fit:   # 08.3.6: the signature's own first base kind supplies the base
                    fit = [b for b in base_candidates(sp["base_kinds"][0]) if base_ok(sp, b)]
                    self.log["sig_base_override"] += 1
                if fit:
                    bases = fit
                    signature = sp
        base = self.rng.choice(bases)
        need = sigs + mags
        if len(gated_pool(src, place, base, cap)) < need and len(bases) > 1:   # 08.3.6: one redraw of the base
            self.log["base_redraws"] += 1
            base = self.rng.choice([x for x in bases if x != base])
        b = BI[base]
        if b["kind"] in ("weapon", "armor", "shield") and arch["tags"][0].startswith(("creature.folk", "creature.undead")) and "creature.folk" not in src:
            src = src + ["creature.folk"]   # 08.3.4: armaments the dead or the living carried were made by hands
        total_slots = min(sigs + mags, b["slot_cap"])
        mags = max(0, total_slots - sigs) if sigs <= total_slots else 0
        sigs = min(sigs, total_slots)
        pool = gated_pool(src, place, base, cap + (1 if degree == "critical_success" else 0))
        self.log["pool_sizes"] += 0
        greater = degree == "critical_success" and LOOT["degree_effects"]["critical_success"] == "greater"
        flawed = degree == "critical_failure"
        if flawed and mags:
            mags -= 1
        picked, groups, total = [], set(), base_contrib(base)
        out = {"arch": arch["id"], "band": cap, "circ": circ, "degree": degree, "rung": rung, "base": base, "pool": len(pool), "props": [], "bound": None, "violation_refills": 0}
        def place_prop(p, tier, slot):
            nonlocal total
            c = contributions(p, tier)
            newt = total + c
            if violates(newt):
                return False
            total = newt
            picked.append((p, tier, slot)); groups.add(p["mod_group"]); self.recent.append(p["id"])
            return True
        # signature slot
        if sigs:
            sig_tier = cap + (1 if greater else 0)
            cands = [p for p in pool if p["signature_eligible"] and p["mod_group"] not in groups]
            p = signature if (signature and signature in pool) else None
            if p is None and method == "signature":   # 08.3.6: a decisive fill never falls back to a relic
                cands = [c for c in cands if not c.get("relic")]
            if p is None and cands:
                p = self.chosen(cands, bias) if method == "chosen" else self.draw(cands, bias if method == "biased" else None)
            if p is not None:
                ok = place_prop(p, sig_tier, "signature")
                if not ok:
                    out["violation_refills"] += 1
                    cands2 = [c for c in cands if c is not p and c["mod_group"] not in groups]
                    if cands2:
                        p2 = self.draw(cands2)
                        place_prop(p2, sig_tier, "signature")
                if picked and picked[-1][0]["kind"] == "item_ability":
                    ia = self.item_ability(arch, circ, sig_tier)
                    out["bound"] = ia["id"] if ia else None
                    if ia is None:  # refill once with a non-ability signature
                        picked.pop()
                        cands3 = [c for c in cands if c["kind"] != "item_ability"]
                        if cands3:
                            place_prop(self.draw(cands3), sig_tier, "signature")
        for _ in range(mags):
            mt = max(1, cap - 1)
            cands = [p for p in pool if not p.get("signature_only") and p["mod_group"] not in groups and p["min_tier"] <= mt]
            if not cands:
                out["empty_slots"] = out.get("empty_slots", 0) + 1
                continue
            p = self.chosen(cands, bias) if method == "chosen" else self.draw(cands, bias if method == "biased" else None)
            if not place_prop(p, mt, "magnitude"):
                out["violation_refills"] += 1
                cands2 = [c for c in cands if c is not p and c["mod_group"] not in groups]
                if not (cands2 and place_prop(self.draw(cands2), mt, "magnitude")):
                    out["empty_slots"] = out.get("empty_slots", 0) + 1
        out["props"] = [(p["id"], t, s, p["kind"]) for p, t, s in picked]
        out["total"] = total
        out["relic"] = any(p.get("relic") for p, _, _ in picked)
        return out

# ---------------------------------------------------------------- the 1,000-drop run
def circumstance(rng):
    r = rng.random()
    return "decisive" if r < 0.45 else ("costly" if r < 0.65 else ("merciful" if r < 0.75 else "scavenged"))

def degree_for(rng, circ):
    if circ == "scavenged":  # a search frame: roughly a +5 searcher at Moderate
        r = rng.random()
        return "critical_success" if r < 0.05 else ("success" if r < 0.55 else ("failure" if r < 0.95 else "critical_failure"))
    return "critical_success" if rng.random() < 0.2 else "success"

out_lines = []
def P(*a):
    s = " ".join(str(x) for x in a)
    out_lines.append(s); print(s)

g = Gen(8)
rng = random.Random(808)
events = collections.Counter(); drops = collections.Counter()
items = []
YIELD = LOOT["drop_check"]["yield"]["trophy"]
while len(items) < 1000:
    arch = rng.choice(ARCH)
    events[arch["band"]] += 1
    if rng.randint(1, 100) > YIELD["T%d" % arch["band"]]:
        continue
    drops[arch["band"]] += 1
    circ = circumstance(rng)
    deg = degree_for(rng, circ)
    if circ == "merciful" and arch["tags"][0].startswith(("creature.undead.mindless", "creature.construct", "creature.horror.ooze")):
        circ = "decisive"
    items.append(g.generate(arch, circ, deg, rng.choice(PLACES)))

P("=== ch.08 loot simulation (seeded) ===")
P("drop check: events by band", dict(sorted(events.items())), "drops", dict(sorted(drops.items())),
  "rates", {b: round(100 * drops[b] / events[b], 1) for b in sorted(events)})
rc = collections.Counter(i["rung"] for i in items)
P("rungs:", dict(rc))
pc = collections.Counter(len(i["props"]) for i in items)
P("property count per item:", dict(sorted(pc.items())))
by_rung = collections.defaultdict(collections.Counter)
for i in items:
    by_rung[i["rung"]][len(i["props"])] += 1
for r, c in by_rung.items():
    P("  ", r, dict(sorted(c.items())))
kinds = collections.Counter(k for i in items for _, _, _, k in i["props"])
P("property kinds:", dict(kinds))
P("items with a bound power (relic, item-bound active):", sum(1 for i in items if i["bound"]), "=", round(100 * sum(1 for i in items if i["bound"]) / len(items), 1), "%")
P("relics (bound power or license):", sum(1 for i in items if i["relic"]), "=", round(100 * sum(1 for i in items if i["relic"]) / len(items), 1), "%")
P("empty slots (pool exhausted after mod groups):", sum(i.get("empty_slots", 0) for i in items))
P("cap violations caught and refilled:", sum(i["violation_refills"] for i in items))
P("base redraws (pool smaller than the rung's slots):", g.log["base_redraws"], "; signature-driven base overrides:", g.log["sig_base_override"])
P("post-generation item-share compliance:", sum(1 for i in items if not violates(i["total"])), "/", len(items))
ps = [i["pool"] for i in items]
P("gated pool size per item: min", min(ps), "median", statistics.median(ps), "max", max(ps))
# gated pool per archetype at its own band, for its first trophy/gear base (09 contract: >= 3)
P("--- 09 contract check: gated pool at tier_cap 1 and at the archetype's band, per archetype (smallest base) ---")
low = []
for a in ARCH:
    bases = a["gear"] or [b for t in TROPHY[branch(a["tags"])] if t != "the source's own gear" for b in base_candidates(t)]
    hands = lambda b: (["creature.folk"] if BI[b]["kind"] in ("weapon", "armor", "shield") and a["tags"][0].startswith(("creature.folk", "creature.undead")) else [])
    s1 = min(len(gated_pool(a["tags"] + a["harm"] + a["deeds"] + a["orgs"] + hands(b), [], b, 1)) for b in bases)
    sb = min(len(gated_pool(a["tags"] + a["harm"] + a["deeds"] + a["orgs"] + hands(b), [], b, a["band"])) for b in bases)
    smax = max(len(gated_pool(a["tags"] + a["harm"] + a["deeds"] + a["orgs"] + hands(b), [], b, a["band"])) for b in bases)
    P(f"  {a['id']:20s} T{a['band']} pool@1 min {s1:3d}  pool@band min {sb:3d} max {smax:3d}  signature {sig_for(a)}")
    if s1 < 3:
        low.append(a["id"])
P("archetypes below 3 at tier 1 on some base:", low or "none")
# tier distribution
td = collections.Counter(t for i in items for _, t, s, _ in i["props"] if s == "signature")
P("signature tiers:", dict(sorted(td.items())))
# repeat rates: per archetype stream of 200 decisive drops
P("--- repeat rates (200 consecutive drops per archetype, decisive success, no place) ---")
rep_mag, rep_item = [], []
for a in ARCH:
    gg = Gen(hash(a["id"]) % 10000)
    prev = None; prevm = None; same_m = same_i = 0; n = 0
    for k in range(200):
        it = gg.generate(a, "decisive", "success", [])
        mags = tuple(sorted(p for p, _, s, _ in it["props"] if s == "magnitude"))
        full = (it["base"],) + tuple(sorted(p for p, _, _, _ in it["props"]))
        if prev is not None:
            n += 1
            if mags and mags == prevm:
                same_m += 1
            if full == prev:
                same_i += 1
        prev, prevm = full, mags
    rep_mag.append(100 * same_m / n); rep_item.append(100 * same_i / n)
P("  same magnitude property as the previous drop: mean", round(statistics.mean(rep_mag), 1), "% max", round(max(rep_mag), 1), "% (target <= 15%, OEQ-00-5)")
P("  identical whole item to the previous drop: mean", round(statistics.mean(rep_item), 1), "% max", round(max(rep_item), 1), "%")
worst = sorted(zip(rep_mag, [a["id"] for a in ARCH]), reverse=True)[:5]
P("  worst magnitude repeat:", [(n, round(v, 1)) for v, n in worst])
# character-level budget: a PC attunes the 5 strongest-looking of 20 random drops at band 3
P("--- character level: 500 PCs each attune 5 of 20 random drops (bands 2-4) ---")
clamps = collections.Counter()
for k in range(500):
    pool = [i for i in rng.sample(items, 20)]
    pool.sort(key=lambda i: -len(i["props"]))
    chosen = pool[:5]
    tot = collections.Counter()
    for i in chosen:
        tot += i["total"]
    for fam in ("harm_edge", "carry"):
        if tot[fam] > SHARE[fam]:
            clamps[fam] += 1
    if any(v > 1 for kk, v in tot.items() if kk.startswith("edge:")):
        clamps["edge (same quantity and scope)"] += 1
    if tot["supply_use"] < -1:
        clamps["supply_use"] += 1
    if any(v > 3 for kk, v in tot.items() if kk.startswith("reduction:")):
        clamps["reduction"] += 1
P("  share of characters whose 5 attuned items would exceed an item share without the E4 clamp:", {k: f"{round(100*v/500,1)}%" for k, v in clamps.items()})

# ---------------------------------------------------------------- crafting: commissioned troll-hide coat, 200 runs
P("--- crafting check: a troll-hide coat (mat.hide from the troll) commissioned at masterwork, bias ward, trained crafter (tier cap 2) ---")
troll = next(a for a in ARCH if a["id"] == "troll")
cg = Gen(77)
cnt = collections.Counter()
for k in range(200):
    pool = gated_pool(["material.hide.leather", "creature.folk.giant.troll", "creature.folk"], [], "bi.hide", 2, domain="craft")
    mags = [p for p in pool if not p.get("signature_only") and p["mod_group"] != "sig_" and not p["signature_eligible"]]
    p = cg.draw([p for p in pool if not p.get("signature_only")], "ward")
    cnt[p["id"]] += 1
P("  craft pool size", len(pool), "top magnitude picks", cnt.most_common(6))

with open(os.path.join(os.path.dirname(__file__), "08-loot-sim-output.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines) + "\n")

# ---- diagnostics: bound power by circumstance
bc = collections.Counter((i["circ"], bool(i["bound"])) for i in items)
P("bound power by circumstance:", dict(bc))
sigm = collections.Counter((i["circ"], i["props"][0][0] if i["props"] and i["props"][0][2]=="signature" else None) for i in items if i["circ"]=="decisive")
P("decisive signatures (top 12):", sigm.most_common(12))
bad = collections.Counter((i["arch"], i["base"]) for i in items if i["circ"]=="decisive" and not (i["props"] and i["props"][0][2]=="signature"))
P("decisive items without a signature (arch, base):", bad.most_common(10))
