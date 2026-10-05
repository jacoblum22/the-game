#!/usr/bin/env python3
"""gen_data08.py -- generates and validates chapter 08's data files.

Writes rules/data/{base_items,item_properties,materials,economy,gen_loot,gen_craft,gen_gift,
gen_item_ability}.yaml and rules/data/contrib/{effects,licenses,boundaries,tags}.08.yaml.
Every tag, effect id, condition id, license id and ability id is validated against the repo's
canonical files before anything is written; the script exits non-zero on the first defect.
Copy kept at rules/_process/simulation/08-gen_data08.py.
"""
import sys, os, glob, json, re
import yaml

ROOT = os.environ.get("GAME_RULES", os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
D = os.path.join(ROOT, "data")
OUT = D

def load(p):
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)

# ------------------------------------------------------------------ canonical vocabularies
TAGS = {t["id"]: t for t in load(os.path.join(D, "tags.yaml"))["tags"]}
for fac in ["deed", "conduct", "creature", "harm", "material", "item", "terrain", "situation", "trait", "org"]:
    TAGS[fac] = {"id": fac, "level": 0}
EFFECTS = {e["id"] for e in load(os.path.join(D, "effects.yaml"))["core"]}
for f in glob.glob(os.path.join(D, "..", "_process", "merged-contrib", "effects.*.yaml")):
    for b in load(f).get("blocks", []):
        for e in b["entries"]:
            EFFECTS.add(e["id"])
CONDS = {c["id"] for c in load(os.path.join(D, "conditions.yaml"))["conditions"]}
LICS = set()
for f in [os.path.join(D, "licenses.yaml")] + glob.glob(os.path.join(D, "..", "_process", "merged-contrib", "licenses.*.yaml")):
    d = load(f)
    for k, v in d.items():
        if isinstance(v, list):
            for e in v:
                if isinstance(e, dict) and "id" in e:
                    LICS.add(e["id"])
                if isinstance(e, dict) and "entries" in e:
                    for x in e["entries"]:
                        LICS.add(x["id"])
ABIL = {a["id"]: a for a in load(os.path.join(D, "abilities.yaml"))["abilities"]}
ABSORB = load(os.path.join(D, "gen_absorb.yaml"))

NEW_TAGS = {}       # proposed level-3 tags (contrib/tags.08.yaml)
NEW_EFFECTS = {}    # 08 owner-block effects
DEFECTS = []

def chk_tag(t, where):
    if t not in TAGS and t not in NEW_TAGS:
        DEFECTS.append(f"unknown tag {t} in {where}")

def chk_eff(eid, where):
    if eid not in EFFECTS and eid not in NEW_EFFECTS:
        DEFECTS.append(f"unknown effect {eid} in {where}")

# ------------------------------------------------------------------ 08's own effect definitions
NEW_EFFECTS = {
    "eff.08.adjust": dict(op="modify", family="adjust", regime="additive",
        params={"quantity": "carry|supply_use|duration|speed|price|clock_ticks", "amount": "-4..4", "applies_when": "expr"},
        text="{amount} to {quantity} {applies_when}.",
        why_not_core="the core library has eff.max_modify (Vitality/Focus maxima) and eff.focus_cost_step only; carry, supply use and other adjust-family quantities of T-00-13 have no core effect"),
    "eff.08.cost_step": dict(op="step", regime="additive",
        params={"ladder": "severity", "steps": "-1..1", "applies_when": "cost.gear targets this item"},
        text="A cost.gear against this item is taken {steps} severity rung.",
        why_not_core="no core effect steps the severity of a COST (eff.harm_severity_step steps harm); sturdiness and fragility of gear must shift cost.gear forms"),
    "eff.08.bound_ability": dict(op="grant_license", regime="additive",
        params={"ability": "ab.*", "rank": "1..3", "relic_surcharge": "bool (05.6.3 decides when it applies)", "feeds_evidence": "false"},
        text="While this item is equipped and attuned, you hold {ability} at rank {rank} through the equipped partition.",
        why_not_core="eff.grant_license grants a license for a duration; an item-bound ability must also name its rank, occupy an equipped slot (05.2.8) and carry feeds_evidence: false (00.11.5)"),
}
for k, v in NEW_EFFECTS.items():
    v["lifecycle"] = "provisional"
    v["basis"] = ["08.2", "08.4", "DL-08-21"]
EFFECTS |= set(NEW_EFFECTS)

# ------------------------------------------------------------------ proposed tags (level 3)
def ptag(i, name, definition, distinguish=None):
    parent = i.rsplit(".", 1)[0]
    NEW_TAGS[i] = dict(id=i, name=name, parent=parent, level=i.count("."), lifecycle="provisional",
                       definition=definition, **({"distinguish": distinguish} if distinguish else {}))

ptag("item.weapon.bludgeon.whip", "Whip", "True only when a lash or whip whose flexible length strikes or entangles at reach. False for flails (a rigid haft with a chain) and nets (thrown).", "vs flail: does the whole weapon flex? Whip.")
ptag("item.shield.light.buckler", "Buckler", "True only when a fist-sized shield held at arm's length that cannot cover the body. False for round shields.", "vs round shield: can it cover you from arrows? No -> buckler.")
ptag("item.shield.light.round", "Round shield", "True only when a strapped round or oval shield that covers the torso. False for bucklers and kite shields.")
ptag("item.shield.heavy.kite", "Kite shield", "True only when a long shield covering shoulder to knee, usable on foot or mounted. False for tower shields.")
ptag("item.shield.heavy.tower", "Tower shield", "True only when a shield as tall as its bearer, braced on the ground. False for kite shields.")
ptag("item.goods.treasure.gem", "Gem", "True only when a loose cut or uncut gemstone valued for itself. False for jewelry worn (item.jewelry).")
ptag("item.goods.treasure.art", "Art object", "True only when a made object valued for its art: a statuette, a gilded cup, a tapestry. False for jewelry worn and for trade goods sold by weight.")
ptag("item.goods.treasure.coinage", "Coinage", "True only when minted coin, bullion or trade bars carried as wealth. False for coin already counted in the coin quantity.")
ptag("item.goods.document.text", "Teaching text", "True only when a book, scroll or pattern that carries a teaches: fact (an ability, rite, training license or recipe). False for maps, letters and ledgers.")
ptag("item.goods.document.map", "Map", "True only when a map, chart or route-book. False for teaching texts.")
ptag("item.consumable.oil.weapon", "Weapon oil", "True only when a coating applied to a weapon that changes its Strikes for a count of strikes or rounds. False for lamp oil and thrown incendiaries.")
ptag("item.consumable.oil.incendiary", "Incendiary", "True only when a flask, pot or charge thrown or set to burn or burst. False for weapon oils and lamp oil.")
ptag("item.consumable.remedy.antidote", "Antidote", "True only when a remedy that lowers a poison or disease stage (eff.07.affliction_shift). False for bandages and salves.")
ptag("item.conveyance.mount.war", "War mount", "True only when a mount trained to bear a rider in a fight (06 flag.mounted, combat-trained). False for riding and draft animals.")
ptag("item.conveyance.vehicle.cart", "Cart or wagon", "True only when a wheeled vehicle drawn by animals or people. False for sledges and vessels.")
ptag("item.conveyance.vessel.boat", "Boat", "True only when a small craft rowed, poled or sailed by its passengers. False for ships with a crew of more than six.")
ptag("item.tool.kit.prosthesis", "Prosthesis", "True only when a made replacement or support for a lost or ruined part of the body, fitted to one bearer (07.7.6). False for armor, a crutch or a walking staff anyone may lean on.", "vs armor: does it stand in for the body rather than cover it? Prosthesis.")  # [revision: I-016]
ptag("item.conveyance.vessel.ship", "Ship", "True only when a vessel needing a crew of more than six. False for boats.")

# ------------------------------------------------------------------ helpers
def eff(eid, **params):
    return {"effect_id": eid, "params": params}

def lic(x):
    if x not in LICS:
        DEFECTS.append(f"unknown license {x}")
    return x

BASIS_06 = ["T-06-6", "T-06-7", "06.4.4"]

# ================================================================== BASE ITEMS
BI = []

def bi(id, name, item_tags, kind, price, load, **kw):
    e = dict(id="bi." + id, name=name, item_tags=item_tags, material_tags=kw.pop("material_tags", []), kind=kind,
             price=price, weight=load)
    e.update(kw)
    e.setdefault("slot_cap", {"weapon": 3, "armor": 3, "shield": 3, "garment": 2, "jewelry": 3, "tool": 2,
                              "consumable": 0, "goods": 0, "conveyance": 2, "ammunition": 1}[kind])
    e["tags"] = item_tags
    e["lifecycle"] = "provisional"
    e.setdefault("basis", ["08.1", "T-08-3"])
    BI.append(e)
    return e

# ---- weapons (06 T-06-6 weights; <= 2 T-06-7 properties each)
W = {
 "light":      dict(severity="S2", strike_cost=1, hands=1, bands=["band.engaged"]),
 "one_handed": dict(severity="S2", strike_cost=1, hands=1, bands=["band.engaged"]),
 "heavy":      dict(severity="S3", strike_cost=2, hands=2, bands=["band.engaged"]),
 "bow":        dict(severity="S2", strike_cost=1, hands=2, bands=["band.close", "band.near"]),
 "crossbow_light": dict(severity="S2", strike_cost=1, hands=2, bands=["band.close", "band.near", "band.far"]),
 "crossbow_heavy": dict(severity="S3", strike_cost=1, hands=2, bands=["band.close", "band.near", "band.far"]),
}
def weapon(id, name, tag, weight, harm, props, price, load, deed, mats, make_time="days:1", craft="lic.training.craft_smithing", **kw):
    w = dict(W[weight]);
    bands = kw.pop("bands", w["bands"])
    if "reach" in props:
        bands = bands + ["band.close"]
    assert len(props) <= 2, id
    e = bi(id, name, [tag, "item.weapon"] if tag.count(".") >= 2 else [tag], "weapon", price, load,
           material_tags=mats, weapon_weight=weight,
           harm={"severity": w["severity"], "harm_tags": [harm], "band_reach": bands},
           strike_cost=w["strike_cost"], hands=kw.pop("hands", w["hands"]), weapon_properties=props,
           deed_tag=deed, training_license=lic("lic.training." + "_".join(deed.split(".")[1:3])),
           make={"license": lic(craft), "deed_tag": kw.pop("craft_tag", "deed.craft.smithing.weapons"), "time_per_tick": make_time},
           body_slot="hand", **kw)
    e["item_tags"] = [t for t in e["item_tags"]]
    return e

P, C, X = "harm.physical.pierce", "harm.physical.cut", "harm.physical.crush"
weapon("knife", "Knife", "item.weapon.blade.dagger", "light", C, ["close_quarters", "concealable"], 1, 0, "deed.martial.blade.dagger", ["material.metal.iron"], make_time="watches:1", trophy_eligible=False)
weapon("dagger", "Dagger", "item.weapon.blade.dagger", "light", P, ["finesse", "thrown"], 2, 1, "deed.martial.blade.dagger", ["material.metal.steel"], make_time="watches:2", default_for="item.weapon.blade.dagger")
weapon("short_sword", "Short sword", "item.weapon.blade.sword", "light", C, ["finesse", "parrying"], 8, 1, "deed.martial.blade.sword", ["material.metal.steel"])
weapon("sword", "Arming sword", "item.weapon.blade.sword", "one_handed", C, ["versatile", "parrying"], 10, 1, "deed.martial.blade.sword", ["material.metal.steel"], default_for="item.weapon.blade.sword")
weapon("rapier", "Rapier", "item.weapon.blade.rapier", "one_handed", P, ["finesse", "parrying"], 15, 1, "deed.martial.blade.fencing", ["material.metal.steel"], default_for="item.weapon.blade.rapier")
weapon("greatsword", "Greatsword", "item.weapon.blade.greatsword", "heavy", C, ["parrying"], 30, 2, "deed.martial.blade.greatsword", ["material.metal.steel"], make_time="days:2", default_for="item.weapon.blade.greatsword")
weapon("hand_axe", "Hand axe", "item.weapon.axe.hand", "light", C, ["thrown"], 3, 1, "deed.martial.axe.hand", ["material.metal.iron", "material.wood.timber"], default_for="item.weapon.axe.hand")
weapon("battle_axe", "Battle axe", "item.weapon.axe", "one_handed", C, ["versatile"], 8, 1, "deed.martial.axe", ["material.metal.iron", "material.wood.timber"], default_for="item.weapon.axe")
weapon("great_axe", "Great axe", "item.weapon.axe.great", "heavy", C, ["reach"], 20, 2, "deed.martial.axe.great", ["material.metal.iron", "material.wood.timber"], make_time="days:2", default_for="item.weapon.axe.great")
weapon("club", "Club", "item.weapon.bludgeon.club", "light", X, [], 1, 1, "deed.martial.bludgeon.club", ["material.wood.timber"], make_time="watches:1", craft="lic.training.craft_woodcraft", craft_tag="deed.craft.woodcraft.carving", default_for="item.weapon.bludgeon.club")
weapon("sap", "Sap", "item.weapon.bludgeon.club", "light", X, ["concealable", "close_quarters"], 1, 0, "deed.martial.bludgeon.club", ["material.hide.leather"], make_time="watches:1", craft="lic.training.craft_leathercraft", craft_tag="deed.craft.leathercraft.goods")
weapon("mace", "Mace", "item.weapon.bludgeon.mace", "one_handed", X, ["armor_breaking"], 8, 1, "deed.martial.bludgeon.mace", ["material.metal.iron"], default_for="item.weapon.bludgeon.mace")
weapon("war_hammer", "War hammer", "item.weapon.bludgeon.hammer", "one_handed", X, ["armor_breaking", "versatile"], 10, 1, "deed.martial.bludgeon.hammer", ["material.metal.iron"], default_for="item.weapon.bludgeon.hammer")
weapon("maul", "Maul", "item.weapon.bludgeon.hammer", "heavy", X, ["armor_breaking"], 15, 3, "deed.martial.bludgeon.hammer", ["material.metal.iron", "material.wood.timber"], make_time="days:2")
weapon("flail", "Flail", "item.weapon.bludgeon.flail", "one_handed", X, ["armor_breaking", "close_quarters"], 10, 1, "deed.martial.bludgeon.flail", ["material.metal.iron"], default_for="item.weapon.bludgeon.flail")
weapon("whip", "Whip", "item.weapon.bludgeon.whip", "light", C, ["reach", "entangling"], 3, 1, "deed.martial.bludgeon.flail", ["material.hide.leather"], craft="lic.training.craft_leathercraft", craft_tag="deed.craft.leathercraft.goods")
weapon("spear", "Spear", "item.weapon.polearm.spear", "one_handed", P, ["reach", "thrown"], 3, 1, "deed.martial.polearm.spear", ["material.wood.timber", "material.metal.iron"], default_for="item.weapon.polearm.spear")
weapon("pike", "Pike", "item.weapon.polearm.spear", "heavy", P, ["reach"], 8, 3, "deed.martial.polearm.spear", ["material.wood.timber", "material.metal.iron"])
weapon("halberd", "Halberd", "item.weapon.polearm.halberd", "heavy", C, ["reach", "armor_breaking"], 20, 3, "deed.martial.polearm.halberd", ["material.metal.steel", "material.wood.timber"], make_time="days:2", default_for="item.weapon.polearm.halberd")
weapon("staff", "Quarterstaff", "item.weapon.polearm.staff", "one_handed", X, ["versatile", "parrying"], 1, 1, "deed.martial.polearm.staff", ["material.wood.timber"], make_time="watches:1", craft="lic.training.craft_woodcraft", craft_tag="deed.craft.woodcraft.carving", default_for="item.weapon.polearm.staff")
weapon("lance", "Lance", "item.weapon.polearm.lance", "heavy", P, ["reach"], 12, 3, "deed.martial.mounted.charge", ["material.wood.fine", "material.metal.iron"], make_time="days:2", default_for="item.weapon.polearm.lance", note="1 action from the saddle with lic.training.martial_mounted (06)")
weapon("javelin", "Javelin", "item.weapon.thrown.javelin", "one_handed", P, ["thrown"], 1, 1, "deed.martial.thrown.javelin", ["material.wood.timber", "material.metal.iron"], make_time="watches:1", default_for="item.weapon.thrown.javelin")
weapon("darts", "Darts (5)", "item.weapon.thrown.javelin", "light", P, ["thrown", "concealable"], 1, 1, "deed.martial.thrown.javelin", ["material.metal.iron"], make_time="watches:1", quantity=5)
weapon("throwing_knives", "Throwing knives (3)", "item.weapon.thrown.knife", "light", P, ["thrown", "concealable"], 3, 1, "deed.martial.thrown.blades", ["material.metal.steel"], make_time="watches:2", quantity=3, default_for="item.weapon.thrown.knife")
weapon("net", "Net", "item.weapon.thrown.net", "light", X, ["thrown", "entangling"], 2, 1, "deed.martial.thrown.entangling", ["material.fiber.cordage"], craft="lic.training.craft_textiles", craft_tag="deed.craft.textiles.ropework", default_for="item.weapon.thrown.net", note="a Strike with it is declared as a Grapple (entangling); its harm is nil when so declared")
weapon("bolas", "Bolas", "item.weapon.thrown.net", "light", X, ["thrown", "entangling"], 2, 1, "deed.martial.thrown.entangling", ["material.fiber.cordage", "material.stone.common"], craft="lic.training.craft_textiles", craft_tag="deed.craft.textiles.ropework")
weapon("shortbow", "Shortbow", "item.weapon.bow.shortbow", "bow", P, [], 10, 1, "deed.martial.archery.bow", ["material.wood.timber", "material.fiber.cordage"], craft="lic.training.craft_woodcraft", craft_tag="deed.craft.woodcraft.bowyery", default_for="item.weapon.bow.shortbow", note="far band with the long-range snag (06.4.7); usable from the saddle")
weapon("longbow", "Longbow", "item.weapon.bow.longbow", "bow", P, [], 25, 2, "deed.martial.archery.bow", ["material.wood.fine.yew", "material.fiber.cordage"], craft="lic.training.craft_woodcraft", craft_tag="deed.craft.woodcraft.bowyery", make_time="days:2", bands=["band.close", "band.near", "band.far"], default_for="item.weapon.bow.longbow")
weapon("sling", "Sling", "item.weapon.bow.sling", "bow", X, [], 1, 0, "deed.martial.archery.sling", ["material.hide.leather", "material.fiber.cordage"], craft="lic.training.craft_leathercraft", craft_tag="deed.craft.leathercraft.goods", make_time="watches:1", hands=1, default_for="item.weapon.bow.sling")
weapon("light_crossbow", "Light crossbow", "item.weapon.crossbow.light", "crossbow_light", P, ["loading"], 25, 2, "deed.martial.archery.crossbow", ["material.wood.timber", "material.metal.steel"], craft="lic.training.craft_artifice", craft_tag="deed.craft.artifice.clockwork", make_time="days:2", reload_actions=1, default_for="item.weapon.crossbow.light")
weapon("heavy_crossbow", "Heavy crossbow", "item.weapon.crossbow.heavy", "crossbow_heavy", P, ["loading", "armor_breaking"], 50, 3, "deed.martial.archery.crossbow", ["material.wood.timber", "material.metal.steel"], craft="lic.training.craft_artifice", craft_tag="deed.craft.artifice.clockwork", make_time="days:3", reload_actions=2, default_for="item.weapon.crossbow.heavy")
# ammunition: a quantity, not an equipped weapon
for aid, nm, tag, pr, mats in [("arrows", "Arrows (20)", "item.weapon.ammunition.arrow", 2, ["material.wood.timber", "material.metal.iron"]),
                                ("bolts", "Crossbow bolts (20)", "item.weapon.ammunition.bolt", 3, ["material.wood.timber", "material.metal.iron"]),
                                ("sling_stones", "Sling bullets (20)", "item.weapon.ammunition.stone", 1, ["material.stone.common"])]:
    bi(aid, nm, [tag], "ammunition", pr, 1, material_tags=mats, quantity=20, quantity_name="ammunition",
       recovery="after a conflict half of those spent, rounded down, are recovered (06.4.9)", default_for=tag,
       make={"license": lic("lic.training.craft_woodcraft"), "deed_tag": "deed.craft.woodcraft.bowyery", "time_per_tick": "watches:1"},
       basis=["06.4.9", "08.9.6"])

# ---- armor (07.2.2 reduction 1/2/3 vs harm.physical; other pillars carry the cost)
def armor(id, name, tag, cls, price, load, mats, snags, don, craft, craft_tag, default=False, **kw):
    red = {"light": 1, "medium": 2, "heavy": 3}[cls]
    e = bi(id, name, [tag], "armor", price, {"light": 1, "medium": 2, "heavy": 3}[cls], material_tags=mats,
           armor_class=cls, reduction={"amount": red, "harm_tags": ["harm.physical"]},
           carried_weight={"light": 2, "medium": 4, "heavy": 6}[cls],
           snags=snags, don_time=don, sleep="long rest at most partial (07.8)" if cls != "light" else "no effect",
           make={"license": lic(craft), "deed_tag": craft_tag, "time_per_tick": {"light": "days:1", "medium": "days:2", "heavy": "days:3"}[cls]},
           body_slot="body", basis=["07.2.2", "T-06-11", "08.1.6"], **kw)
    if default:
        e["default_for"] = tag
    return e
armor("padded", "Padded jack", "item.armor.light.padded", "light", 5, None, ["material.fiber.cloth"], [], "intervals:1", "lic.training.craft_textiles", "deed.craft.textiles.tailoring", True)
armor("leather", "Leather armor", "item.armor.light.leather", "light", 10, None, ["material.hide.leather"], [], "intervals:1", "lic.training.craft_leathercraft", "deed.craft.leathercraft.goods", True)
armor("hide", "Hide coat", "item.armor.light.leather", "light", 8, None, ["material.hide.fur"], ["Swim"], "intervals:1", "lic.training.craft_leathercraft", "deed.craft.leathercraft.goods", note="the crafting base for beast hides")
armor("brigandine", "Brigandine", "item.armor.medium.brigandine", "medium", 60, None, ["material.metal.iron", "material.fiber.cloth"], ["Swim"], "intervals:1", "lic.training.craft_smithing", "deed.craft.smithing.armor", True)
armor("mail", "Mail hauberk", "item.armor.medium.mail", "medium", 50, None, ["material.metal.iron"], ["Sneak", "Swim"], "intervals:1", "lic.training.craft_smithing", "deed.craft.smithing.armor", True)
armor("scale", "Scale coat", "item.armor.medium.scale", "medium", 45, None, ["material.metal.iron", "material.hide.leather"], ["Sneak", "Swim"], "intervals:1", "lic.training.craft_smithing", "deed.craft.smithing.armor", True, note="the crafting base for scaled and chitin hides")
armor("splint", "Splint armor", "item.armor.heavy.splint", "heavy", 200, None, ["material.metal.iron", "material.hide.leather"], ["Sneak", "Swim", "Exert"], "intervals:2", "lic.training.craft_smithing", "deed.craft.smithing.armor", True)
armor("plate", "Plate armor", "item.armor.heavy.plate", "heavy", 400, None, ["material.metal.steel"], ["Sneak", "Swim"], "intervals:3", "lic.training.craft_smithing", "deed.craft.smithing.armor", True, note="donning takes 3 intervals alone, 1 with help")

# ---- shields (+1 Guard edge, no reduction: T-06-7, 07.2.2)
def shield(id, name, tags, prop, price, load, mats, extra, default=None):
    e = bi(id, name, tags, "shield", price, load, material_tags=mats, weapon_properties=[prop], guard_edge=1, reduction=None,
           shield_class=prop.split("_")[1], notes_rules=extra, body_slot="hand",
           make={"license": lic("lic.training.craft_woodcraft"), "deed_tag": "deed.craft.woodcraft.carpentry", "time_per_tick": "days:1"},
           harm={"severity": "S1", "harm_tags": [X], "band_reach": ["band.engaged"]}, deed_tag="deed.martial.shield.block",
           training_license=lic("lic.training.martial_shield"), basis=["T-06-7", "07.2.2", "08.1.7"])
    if default:
        e["default_for"] = default
    return e
shield("buckler", "Buckler", ["item.shield.light.buckler", "item.shield.light"], "shield_light", 3, 0, ["material.metal.iron"], "does not grant Full defense's cover (06.1.5); the shield hand may also hold a lit torch or a light item, not a weapon")
shield("round_shield", "Round shield", ["item.shield.light.round", "item.shield.light"], "shield_light", 5, 1, ["material.wood.timber", "material.hide.leather"], "grants Full defense's cover (06.1.5)", default="item.shield.light")
shield("kite_shield", "Kite shield", ["item.shield.heavy.kite", "item.shield.heavy"], "shield_heavy", 10, 2, ["material.wood.timber", "material.metal.iron"], "usable mounted; Exert and Sneak take a snag", default="item.shield.heavy")
shield("tower_shield", "Tower shield", ["item.shield.heavy.tower", "item.shield.heavy"], "shield_heavy", 15, 3, ["material.wood.timber", "material.metal.iron"], "not usable mounted; Exert and Sneak take a snag; while Defending and not Moving it is a cover feature for one ally engaged with you")
BI[-1]["make"]["time_per_tick"] = "days:2"

# ---- garments (body slots; intrinsic effects are part of the base, not properties)
def garment(id, name, tag, price, load, slot, mats, intrinsic=None, default=False, social=None, **kw):
    e = bi(id, name, [tag], "garment", price, load, material_tags=mats, body_slot=slot,
           intrinsic=intrinsic or [], make={"license": lic(kw.pop("craft", "lic.training.craft_textiles")),
           "deed_tag": kw.pop("craft_tag", "deed.craft.textiles.tailoring"), "time_per_tick": "days:1"}, **kw)
    if social:
        e["status"] = social
    if default:
        e["default_for"] = tag
    return e
garment("plain_clothes", "Plain clothes", "item.garment.clothing", 1, 0, "clothing", ["material.fiber.cloth"], default=True, social="plain")
garment("work_clothes", "Working clothes", "item.garment.clothing", 2, 0, "clothing", ["material.fiber.cloth", "material.hide.leather"], social="plain")
garment("fine_clothes", "Fine clothes", "item.garment.clothing", 15, 0, "clothing", ["material.fiber.cloth"], social="fine")
garment("courtly_attire", "Courtly attire", "item.garment.clothing", 60, 1, "clothing", ["material.fiber.silk"], social="noble")
garment("winter_furs", "Winter furs", "item.garment.clothing", 8, 1, "clothing", ["material.hide.fur.winter"], intrinsic=[eff("eff.hazard_step", steps=-1, harm_tags=["harm.frost.cold"], applies_when="hazard")], craft="lic.training.craft_leathercraft", craft_tag="deed.craft.leathercraft.goods")
garment("desert_robes", "Desert robes", "item.garment.clothing", 4, 0, "clothing", ["material.fiber.cloth"], intrinsic=[eff("eff.hazard_step", steps=-1, harm_tags=["harm.fire.heat"], applies_when="hazard")])
garment("cloak", "Cloak", "item.garment.cloak", 2, 0, "cloak", ["material.fiber.cloth"], default=True, carried_weight=1)
garment("oilskin_cloak", "Oilskin cloak", "item.garment.cloak", 4, 0, "cloak", ["material.fiber.cloth"], intrinsic=[eff("eff.05.waive", event_kind="the rain or wet snag on a rest or a watch check (10)", applies_when="exposed to rain")], carried_weight=1)
garment("boots", "Boots", "item.garment.footwear", 3, 0, "feet", ["material.hide.leather"], default=True, craft="lic.training.craft_leathercraft", craft_tag="deed.craft.leathercraft.goods")
garment("soft_shoes", "Soft shoes", "item.garment.footwear", 2, 0, "feet", ["material.hide.leather"], craft="lic.training.craft_leathercraft", craft_tag="deed.craft.leathercraft.goods")
garment("gloves", "Gloves", "item.garment.gloves", 1, 0, "hands_worn", ["material.hide.leather"], default=True, craft="lic.training.craft_leathercraft", craft_tag="deed.craft.leathercraft.goods")
garment("gauntlets", "Riding gauntlets", "item.garment.gloves", 3, 0, "hands_worn", ["material.hide.leather"], craft="lic.training.craft_leathercraft", craft_tag="deed.craft.leathercraft.goods")
garment("hood", "Hood", "item.garment.headwear", 1, 0, "head", ["material.fiber.cloth"], default=True)
garment("hat", "Hat", "item.garment.headwear", 2, 0, "head", ["material.fiber.cloth"])
garment("helm", "Helm", "item.garment.headwear", 6, 1, "head", ["material.metal.iron"], craft="lic.training.craft_smithing", craft_tag="deed.craft.smithing.armor", note="a helm is a garment, not armor: it carries no reduction (07.2.2); it is the base for head-slot properties of the ward bias")

# ---- jewelry
def jewel(id, name, tag, price, slot, mats, default=False, **kw):
    e = bi(id, name, [tag], "jewelry", price, 0, material_tags=mats, body_slot=slot,
           make={"license": lic("lic.training.craft_jewelcraft"), "deed_tag": "deed.craft.jewelcraft.goldwork", "time_per_tick": "days:1"}, **kw)
    if default:
        e["default_for"] = tag
    return e
jewel("ring", "Ring", "item.jewelry.ring", 5, "ring", ["material.metal.copper"], True)
jewel("signet", "Signet ring", "item.jewelry.ring", 20, "ring", ["material.metal.gold"], status="a seal that is a citable fact of house or office")
jewel("amulet", "Amulet", "item.jewelry.amulet", 8, "neck", ["material.metal.silver"], True)
jewel("torc", "Torc", "item.jewelry.amulet", 25, "neck", ["material.metal.gold"])
jewel("charm", "Charm", "item.jewelry.charm", 1, "charm", ["material.bone.fang"], True, trophy_eligible=True, note="trophies: a fang, a claw, a scale, a feather, a knucklebone on a thong")
jewel("circlet", "Circlet", "item.jewelry.circlet", 30, "head", ["material.metal.silver"], True)
for b in BI[-6:]:
    b["slot_cap"] = 3
BI[-2]["make"] = {"license": lic("lic.training.craft_woodcraft"), "deed_tag": "deed.craft.woodcraft.carving", "time_per_tick": "watches:1"}

# ---- tools
def tool(id, name, tag, price, load, mats, uses=None, default=False, lever=None, craft="lic.training.craft_artifice", craft_tag="deed.craft.artifice.clockwork", **kw):
    e = bi(id, name, [tag], "tool", price, load, material_tags=mats, body_slot=kw.pop("slot", "pack"),
           make={"license": lic(craft), "deed_tag": craft_tag, "time_per_tick": kw.pop("make_time", "days:1")}, **kw)
    if uses:
        e["uses"] = uses
    if lever:
        e["grants_lever"] = lever
    if default:
        e["default_for"] = tag
    return e
tool("thieves_tools", "Thieves' tools", "item.tool.kit.thieves", 15, 1, ["material.metal.steel"], default=True,
     lever={"type": "precision", "for": "lockwork and trap beats under lic.training.guile_thievery", "rule": "without the kit, lockwork is G3 or improvised (+5 DC) even for the licensed"})
tool("healers_kit", "Healer's kit", "item.tool.kit.healer", 5, 1, ["material.fiber.cloth", "material.botanical.herb.healing"], uses=10, default=True,
     lever={"type": "precision", "for": "Treat and first aid (07.8.8)", "rule": "one use per treatment; refilled at an apothecary for 1 coin per 2 uses"}, craft="lic.training.craft_alchemy", craft_tag="deed.craft.alchemy.potions")
tool("climbing_kit", "Climbing kit (rope, hook, pitons)", "item.tool.kit.climbing", 4, 2, ["material.fiber.cordage", "material.metal.iron"], default=True,
     lever={"type": "protective", "for": "Exert to climb once the rope is anchored", "rule": "the anchored rope is a fact; a fall on it is stopped (stakes one rung down)"}, craft="lic.training.craft_textiles", craft_tag="deed.craft.textiles.ropework")
tool("rope", "Rope (50 ft)", "item.tool.kit.climbing", 1, 1, ["material.fiber.cordage"], craft="lic.training.craft_textiles", craft_tag="deed.craft.textiles.ropework")
tool("disguise_kit", "Disguise kit", "item.tool.kit.disguise", 10, 1, ["material.fiber.cloth"], uses=5, default=True, lever={"type": "precision", "for": "Sneak or Talk beats under lic.training.guile_disguise", "rule": "one use per disguise"}, craft="lic.training.craft_textiles", craft_tag="deed.craft.textiles.tailoring")
tool("forgery_kit", "Forgery kit", "item.tool.kit.forgery", 12, 1, ["material.fiber.cloth"], uses=5, default=True, lever={"type": "precision", "for": "forging documents (deed.guile.deception or craft.scribing)", "rule": "one use per document"}, craft="lic.training.craft_scribing", craft_tag="deed.craft.scribing.copying")
for nm, iid, pr in [("Lute", "lute", 10), ("Flute", "flute", 3), ("Drum", "drum", 4), ("Horn", "horn", 5)]:
    tool(iid, nm, "item.tool.instrument", pr, 1, ["material.wood.fine"], default=(iid == "lute"), lever={"type": "precision", "for": "Talk to perform (deed.influence.performance)", "rule": "required for an instrumental performance; a voice needs none"}, craft="lic.training.craft_woodcraft", craft_tag="deed.craft.woodcraft.carving")
for iid, nm, tag, pr, mats in [("wand", "Wand", "item.tool.implement.wand", 10, ["material.wood.witchwood"]),
                                ("casting_staff", "Casting staff", "item.tool.implement.staff", 12, ["material.wood.witchwood"]),
                                ("orb", "Orb", "item.tool.implement.orb", 25, ["material.gem.crystal"]),
                                ("holy_symbol", "Holy symbol", "item.tool.implement.holy_symbol", 5, ["material.metal.silver"]),
                                ("totem", "Totem", "item.tool.implement.totem", 2, ["material.bone.bone", "material.botanical.herb"])]:
    e = tool(iid, nm, tag, pr, 1, mats, default=True, slot="hand",
             implement={"sign_of": "a keeper's sign when it bears the keeper's mark (05.7.4)", "vessel": "a reserve's vessel when kept a season or made by the holder (05.6.12)"},
             craft="lic.training.craft_enchanting" if iid in ("wand", "casting_staff", "orb") else ("lic.training.craft_jewelcraft" if iid == "holy_symbol" else "lic.training.craft_woodcraft"),
             craft_tag="deed.craft.enchanting.inscription" if iid in ("wand", "casting_staff", "orb") else ("deed.craft.jewelcraft.goldwork" if iid == "holy_symbol" else "deed.craft.woodcraft.carving"))
    e["slot_cap"] = 3
BI[-4]["weapon_alias"] = "bi.staff"  # a casting staff is also a quarterstaff (06)
TRADES = [("smith", "Smith's tools", "deed.craft.smithing", 20, 3), ("woodworker", "Woodworker's tools", "deed.craft.woodcraft", 10, 2),
          ("leatherworker", "Leatherworker's tools", "deed.craft.leathercraft", 8, 2), ("weaver", "Weaver's and tailor's tools", "deed.craft.textiles", 6, 1),
          ("alchemist", "Alchemist's kit", "deed.craft.alchemy", 25, 2), ("cook", "Cook's kit", "deed.craft.cookery", 3, 1),
          ("mason", "Mason's tools", "deed.craft.building", 8, 3), ("tinker", "Tinker's tools", "deed.craft.artifice", 15, 1),
          ("jeweler", "Jeweler's tools", "deed.craft.jewelcraft", 25, 1), ("enchanter", "Enchanter's kit", "deed.craft.enchanting", 40, 1),
          ("scribe", "Writing case", "deed.craft.scribing", 4, 1)]
for iid, nm, deed, pr, ld in TRADES:
    tool(iid + "_tools", nm, "item.tool.trade", pr, ld, ["material.metal.iron"], serves=deed,
         lever={"type": "precision", "for": f"crafting beats under {deed}", "rule": "a crafting beat (08.6) without the trade's tools is improvised: +5 DC, reach capped Limited, no rung above fine"})
tool("work_tools", "Tools of the work", "item.tool.trade", 3, 1, ["material.metal.iron"], default=True,
     serves="set at creation: the livelihood's first craft, trade or work deed tag (02 kit note)", lever={"type": "precision", "for": "beats of the served deed tag", "rule": "resolution of a kit's 'tools of the work' (08.1.12)"})
for iid, nm, pr, ld, burn, light in [("torch", "Torches (5)", 1, 1, "intervals:6 each", "bright to band.close, dim to band.near"),
                                       ("lantern", "Lantern", 5, 1, "intervals:24 per flask of oil", "bright to band.close, dim to band.near; hooded: may be shut to darkness as a free activity"),
                                       ("candles", "Candles (10)", 1, 0, "intervals:6 each", "dim to band.close"),
                                       ("tinderbox", "Tinderbox", 1, 0, "lights a fire or torch in 1 interval (rain: 1 hour)", "none")]:
    tool(iid, nm, "item.tool.light", pr, ld, ["material.metal.iron"], light_source={"burn": burn, "light": light}, default=(iid == "torch"),
         quantity=5 if iid == "torch" else (10 if iid == "candles" else None), basis=["08.9.5", "conflict.yaml#light", "10 consumes"])
for iid, nm, pr, ld, cap in [("backpack", "Backpack", 2, 0, "holds the pack portion of the load (08.9.1)"), ("belt_pouch", "Belt pouch", 1, 0, "holds coin and small things; 0 load"),
                              ("satchel", "Satchel", 1, 0, "holds documents and small tools"), ("sack", "Sack", 1, 0, "a carry bag; drop it as a free activity"),
                              ("waterskin", "Waterskin", 1, 0, "holds a day's water; counted in supply"), ("chest", "Strongbox", 10, 3, "lockable (Moderate lock)"),
                              ("scroll_case", "Scroll case", 2, 0, "keeps documents dry"), ("bedroll", "Bedroll and cook-pot", 2, 1, "camp gear: a rest at a camp site, not rough (07.8)")]:
    tool(iid, nm, "item.tool.container", pr, ld, ["material.hide.leather"], holds=cap, default=(iid == "backpack"), craft="lic.training.craft_leathercraft", craft_tag="deed.craft.leathercraft.goods")
for iid, nm, pr, ld, use in [("crowbar", "Crowbar", 2, 1, "a Precision lever on Force to pry"), ("grappling_hook", "Grappling hook", 2, 1, "a Precision lever on Exert to climb where a hook can bite"),
                              ("shovel", "Shovel", 2, 2, "digging: a Precision lever; field works (craft.building.field_works)"), ("manacles", "Manacles", 4, 1, "applies cond.restrained to a pinned or yielded creature (Moderate lock)"),
                              ("spyglass", "Spyglass", 60, 0, "a Precision lever on Observe beyond band.far"), ("mirror", "Steel mirror", 5, 0, "see around corners; signal by sun"),
                              ("tent", "Tent", 5, 3, "a rest site of camp quality in foul weather (07.8)"), ("fishing_gear", "Fishing gear", 2, 1, "a Precision lever on foraging for food by water (10)")]:
    tool(iid, nm, "item.tool.trade", pr, ld, ["material.metal.iron"], use=use)

# ---- prostheses: 07.7.6's made offsets, one per maim that names a made thing (inj.maim.* `offset`) [revision: I-016]
# Each narrows its maim's restriction and never restores the attribute (07.7.6); fitted to one bearer (a fitting
# frame by the maker, 08.6); price band 2 (modest, 08.8.2). `offsets` names the maim and exactly what changes.
for iid, nm, pr, mats, craft, ctag, maim, narrows in [
    ("hook_hand", "Hook (for a lost hand)", 8, ["material.metal.iron", "material.hide.leather"], "lic.training.craft_smithing", "deed.craft.smithing",
     "inj.maim.lost_hand", "the hook holds a strap, a rope or a strapped shield: 'a shield with a weapon' is allowed again; methods that need two hands stay forbidden"),
    ("arm_brace", "Arm brace", 10, ["material.hide.leather", "material.metal.iron"], "lic.training.craft_leathercraft", "deed.craft.leathercraft",
     "inj.maim.ruined_arm", "the status penalty on Grapple and Might-based Force and Exert is -1 instead of -2 while it is worn"),
    ("peg_leg", "Peg or fitted boot", 6, ["material.wood.fine", "material.hide.leather"], "lic.training.craft_woodcraft", "deed.craft.woodcraft",
     "inj.maim.lost_foot", "Pace -1 applies only on difficult ground, in a run, flight or chase (06.12), or when climbing; on firm level ground the bearer moves at pace"),
    ("knee_brace", "Hinged knee brace", 12, ["material.metal.iron", "material.hide.leather"], "lic.training.craft_smithing", "deed.craft.smithing",
     "inj.maim.ruined_knee", "the status penalty on Exert to jump, run or climb is -1 instead of -2 while it is worn"),
    ("glass_eye", "Glass eye", 15, ["material.gem.crystal"], "lic.training.craft_jewelcraft", "deed.craft.jewelcraft",
     "inj.maim.lost_eye", "nothing mechanical: the Precision snag stands; the loss is no longer visible to those who have not seen the bearer without it (the maim's `visible` fact is hidden)"),
    ("ear_trumpet", "Ear trumpet", 6, ["material.metal.copper"], "lic.training.craft_artifice", "deed.craft.artifice",
     "inj.maim.deaf_ear", "out of a fight, the Precision snag does not apply to hearing a speaker at band.close; in a fight it cannot be used (both hands, 06)"),
]:
    e = tool(iid, nm, "item.tool.kit.prosthesis", pr, 0, mats, craft=craft, craft_tag=ctag, slot="fitted", make_time="days:2",
             offsets={"maim": maim, "narrows": narrows, "never": "restores the attribute (07.7.6)"}, fitted_to_bearer=True,
             trophy_eligible=False, basis=["07.7.6", "08.1", "08.6", "T-08-3"])

# ---- consumables
def cons(id, name, tag, price, load, effects, mats, craft, craft_tag, rank=None, uses=1, **kw):
    e = bi(id, name, [tag], "consumable", price, load, material_tags=mats, effects=effects, uses=uses,
           make={"license": lic(craft), "deed_tag": craft_tag, "time_per_tick": kw.pop("make_time", "watches:1")}, **kw)
    if rank:
        e["priority_rank"] = rank
    return e
ALC = ("lic.training.craft_alchemy", "deed.craft.alchemy.potions")
cons("healing_draught", "Healing draught", "item.consumable.potion.healing", 25, 0, [eff("eff.restore", quantity="vitality", units=3, target="the drinker")], ["material.botanical.herb.healing"], *ALC, default_for="item.consumable.potion.healing", note="1 action to drink in a conflict; counts toward 05's two healing effects per recipient per long rest")
cons("greater_healing_draught", "Greater healing draught", "item.consumable.potion.healing", 125, 0, [eff("eff.restore", quantity="vitality", units=6, target="the drinker")], ["material.botanical.herb.healing", "material.essence.heart"], *ALC)
cons("clarity_draught", "Clarity draught", "item.consumable.potion.elixir", 40, 0, [eff("eff.restore", quantity="focus", units=1, target="the drinker")], ["material.botanical.herb.arcane"], *ALC, note="05.6.11: at most 4 Focus between long rests from consumables; past it the draught restores nothing and the codex says so before it is drunk", default_for="item.consumable.potion.elixir")
cons("nighteye_elixir", "Nighteye elixir", "item.consumable.potion.elixir", 15, 0, [eff("eff.grant_lever", type="precision", for_verbs=["verb.observe", "verb.strike"], for_tags=[], duration="hours:6", applies_when="a fact of darkness or dim light is cited as a snag on the beat")], ["material.botanical.fungus"], *ALC)
cons("surefoot_elixir", "Surefoot elixir", "item.consumable.potion.elixir", 15, 0, [eff("eff.05.waive", event_kind="snags from slippery, steep or unstable footing", applies_when="for hours:6")], ["material.botanical.herb"], *ALC)
cons("ward_elixir", "Warding elixir", "item.consumable.potion.elixir", 30, 0, [eff("eff.harm_reduction", amount=2, harm_tags=["the elixir's named harm branch (fire, frost, storm, corrosion, venom or blight)"])], ["material.essence.gland"], *ALC, duration="hours:1", note="one variant per named harm branch; priced the same")
cons("poison_dose", "Blade venom (dose)", "item.consumable.potion.toxin", 20, 0, [eff("eff.apply_condition", condition="cond.poisoned", severity="S2", duration="scene", target="the next creature the coated weapon harms")], ["material.essence.gland.venom"], "lic.training.craft_alchemy", "deed.craft.alchemy.poisons", rank=None, default_for="item.consumable.potion.toxin", note="applied to a weapon (1 action); lasts until it harms or until scene_end; using it on the unwilling writes conduct evidence per 03")
cons("sleeping_draught", "Sleeping draught", "item.consumable.potion.toxin", 15, 0, [eff("eff.force_check", verb="endure", effect_dc_source="the maker's effect DC (stored on the item)", degree_table="failure: cond.unconscious for hours:2; critical failure: hours:6")], ["material.botanical.herb.toxic"], "lic.training.craft_alchemy", "deed.craft.alchemy.poisons")
cons("trail_rations", "Trail rations (2 supply)", "item.consumable.food", 1, 1, [eff("eff.restore", quantity="supply", units=2, target="the carrier")], ["material.botanical.herb"], "lic.training.craft_cookery", "deed.craft.cookery.provisions", default_for="item.consumable.food", quantity=2, quantity_name="supply", note="a kit's 'food xN' is N supply (02); supply is 10's quantity")
cons("feast", "A good meal for a table", "item.consumable.food", 3, 0, [eff("eff.grant_lever", type="precision", for_verbs=["verb.talk"], for_tags=[], duration="scene", applies_when="Talk with those who shared it")], ["material.botanical.herb"], "lic.training.craft_cookery", "deed.craft.cookery.feasting")
cons("ale_cask", "Small cask of ale", "item.consumable.food", 2, 2, [], ["material.botanical.herb"], "lic.training.craft_cookery", "deed.craft.cookery.brewing")
cons("scroll", "Scroll", "item.consumable.scroll", 0, 0, [eff("eff.08.bound_ability", ability="the ability the scroll was inscribed with", rank=1, relic_surcharge="per 05.6.3", feeds_evidence="false")], ["material.fiber.cloth"], "lic.training.craft_enchanting", "deed.craft.enchanting.inscription", default_for="item.consumable.scroll", price_rule="25 + 25 x the ability's min_tier", note="one use: reading it activates the inscribed ability once at rank 1 for its Focus (+1 relic surcharge without the training license); it needs no equipped slot and is consumed")
cons("lamp_oil", "Lamp oil (2 flasks)", "item.consumable.oil", 1, 1, [], ["material.botanical.resin"], *ALC, quantity=2, default_for="item.consumable.oil", note="fuel for a lantern (intervals:24 per flask)")
cons("firepot", "Firepot", "item.consumable.oil.incendiary", 10, 1, [eff("eff.deal_harm", severity="S2", harm_tags=["harm.fire.flame"], target="shape burst at a target point within band.near (06.8)"), eff("eff.apply_condition", condition="cond.burning", severity="S1", duration="until_cleansed", target="each creature the burst harms")], ["material.botanical.resin"], "lic.training.craft_alchemy", "deed.craft.alchemy.incendiaries", spread="burst", default_for="item.consumable.oil.incendiary", note="thrown: a Strike against the target point's tier (Easy) or a creature's Guard; on failure it lands short (06.4.7 'into a melee' risk applies)")
cons("smoke_pot", "Smoke pot", "item.consumable.oil.incendiary", 6, 1, [eff("eff.06.grant_snag", type="precision", sign="snag", to="anyone attacking into or out of the smoke", fact="smoke.<id>", applies_when="sight-based beats through the smoke", duration="rounds:5")], ["material.botanical.resin"], "lic.training.craft_alchemy", "deed.craft.alchemy.incendiaries", spread="linger")
for oid, nm, harm, cond, mat, pr in [("rime_oil", "Rime oil", "harm.frost.cold", "cond.chilled", "material.essence.heart.elemental", 30),
                                      ("ember_oil", "Ember oil", "harm.fire.flame", "cond.burning", "material.essence.gland.fire", 30),
                                      ("silvering_paste", "Silvering paste", "harm.radiance.light", None, "material.metal.silver.pure", 20),
                                      ("holy_water", "Holy water", "harm.radiance.holy", None, "material.metal.silver", 15)]:
    effs = [eff("eff.strike_delivery", priority_rank=20, harm_tags=[harm], harm_edge=1, duration="uses:3", cosmetic_merge=False)]
    cons(oid, nm, "item.consumable.oil.weapon", pr, 0, effs, [mat], *ALC, rank=20,
         note=("applied to a weapon (1 action): the next 3 Strikes with it" + ("; silver counts as silver for banes and creature weaknesses" if "silver" in oid else "") + ("; thrown from its flask it deals S2 radiant harm to undead and fiends only" if oid == "holy_water" else "")),
         default_for="item.consumable.oil.weapon" if oid == "rime_oil" else None)
BI[-1].pop("default_for", None); BI[-2].pop("default_for", None); BI[-3].pop("default_for", None)
cons("whetstone", "Whetstone", "item.consumable.oil.weapon", 1, 0, [eff("eff.harm_edge", amount=1, applies_when="the next 3 Strikes with the honed edged weapon")], ["material.stone.common"], "lic.training.craft_smithing", "deed.craft.smithing.tools", uses=5, note="1 interval to hone; an item-sourced harm edge (08.2.2): it adds nothing to a weapon already carrying an item harm edge")
cons("bandages", "Bandages", "item.consumable.remedy", 1, 0, [eff("eff.07.stabilize")], ["material.fiber.cloth"], "lic.training.craft_textiles", "deed.craft.textiles.weaving", uses=3, default_for="item.consumable.remedy", note="first aid: a Precision lever on Handle to stabilize (07)")
cons("antidote", "Antidote (general)", "item.consumable.remedy.antidote", 15, 0, [eff("eff.07.affliction_shift", stages=-1, kinds=["poison", "disease"])], ["material.botanical.herb.healing"], *ALC, default_for="item.consumable.remedy.antidote", note="general remedy: one stage (07.9.6)")
for rid, nm, fam in [("bitterwort", "Bitterwort", "venoms of beasts and vermin"), ("feverbark", "Feverbark", "fevers and wasting diseases"), ("wyvern_bane", "Wyvern-bane", "wyvern and drake venom"), ("grave_salt", "Grave salt", "grave rot and undead-borne disease")]:
    cons(rid, nm, "item.consumable.remedy.antidote", 30, 0, [eff("eff.07.affliction_shift", stages=-2, kinds=[fam])], ["material.botanical.herb.healing"], *ALC, note="specific remedy: two stages for its named family (07.9.6)")
cons("salve", "Healing salve", "item.consumable.remedy", 5, 0, [eff("eff.restore", quantity="vitality", units=1, target="the treated one at the end of a rest_short")], ["material.botanical.herb.healing"], *ALC, uses=3)

# ---- goods
def good(id, name, tag, price, load, **kw):
    return bi(id, name, [tag], "goods", price, load, **kw)
for gid, nm, pr, ld, unit in [("salt", "Salt", 6, 2, "a sack"), ("grain", "Grain", 2, 4, "a sack"), ("cloth_bolt", "Cloth", 10, 2, "a bolt"),
                               ("iron_ore", "Iron ore", 3, 4, "a basket"), ("timber", "Seasoned timber", 4, 6, "a load"), ("spices", "Spices", 30, 0, "a pouch"),
                               ("wine", "Wine", 8, 3, "a small cask"), ("furs", "Furs", 20, 3, "a bale"), ("dyes", "Dyes", 25, 1, "a box"),
                               ("trade_stock", "Working stock", 10, 2, "a bundle")]:
    good(gid, nm, "item.goods.trade", pr, ld, unit=unit, market="trade goods: sell at list in a market that lacks them, list minus one notch where common (08.8.5)", default_for="item.goods.trade" if gid == "trade_stock" else None)
for b in BI:
    if b.get("default_for") is None:
        b.pop("default_for", None)
for gid, nm, tag, pr in [("gem_lesser", "Semiprecious gem", "item.goods.treasure.gem", 10), ("gem", "Precious gem", "item.goods.treasure.gem", 100),
                          ("gem_great", "Great gem", "item.goods.treasure.gem", 1000), ("art_object", "Art object", "item.goods.treasure.art", 50),
                          ("art_treasure", "Treasure of art", "item.goods.treasure.art", 500), ("trade_bar", "Silver trade bar", "item.goods.treasure.coinage", 50)]:
    good(gid, nm, tag, pr, 0 if "gem" in gid else 1, market="treasure: sells at list minus one notch to a jeweler, broker or temple in a town or city (08.8.5)")
BI[-6]["default_for"] = "item.goods.treasure"
for gid, nm, tag, pr, extra in [("letter", "Letter or writ", "item.goods.document", 1, {"default_for": "item.goods.document"}),
                                 ("map", "Map", "item.goods.document.map", 10, {"default_for": "item.goods.document.map", "grants_lever": {"type": "precision", "for": "Observe/Recall to navigate the mapped region (10)"}}),
                                 ("ledger", "Ledger", "item.goods.document", 2, {}),
                                 ("book", "Book", "item.goods.document", 15, {}),
                                 ("spellbook", "Spellbook", "item.goods.document.text", 30, {"teaches_rule": "carries the fact teaches: <ab.* | rit.*>; a week of study ticks the learning clock 2 (05.8.5); reading needs lic.lang.letters and the text's language", "default_for": "item.goods.document.text"}),
                                 ("manual", "Manual", "item.goods.document.text", 25, {"teaches_rule": "teaches: <lic.training.*>; a week of study ticks clk.train 1 (05.9)"}),
                                 ("pattern_book", "Pattern book", "item.goods.document.text", 40, {"teaches_rule": "teaches: <prop.*> (a recipe, 08.6.9)"}),
                                 ("charter", "Charter or deed", "item.goods.document", 5, {"note": "title to a holding (11); the fact of ownership is in state, the document proves it"})]:
    good(gid, nm, tag, pr, 0, **extra)

# ---- conveyances (mounts are also entities: 16 owns their templates and loyalty)
def mount(id, name, tags, price, carry, pace, upkeep, band, trained, size="large", **kw):
    return bi(id, name, tags, "conveyance", price, 0, conveyance="mount", carry_capacity=carry, travel_pace=pace,
              upkeep_week=upkeep, companion_hint={"threat_band": band, "size": size, "combat_trained": trained,
              "template": "16 owns (companions.yaml)"}, body_slot=None, material_tags=[], slot_cap=2, **kw)
mount("donkey", "Donkey", ["item.conveyance.mount"], 15, 20, "walk", 2, 1, False, size="medium")
mount("pony", "Pony", ["item.conveyance.mount"], 25, 20, "walk", 3, 1, False, size="medium")
mount("mule", "Mule", ["item.conveyance.mount"], 30, 30, "walk", 3, 1, False)
mount("riding_horse", "Riding horse", ["item.conveyance.mount"], 75, 25, "ride", 5, 1, False, default_for="item.conveyance.mount")
mount("draft_horse", "Draft horse", ["item.conveyance.mount"], 50, 40, "walk", 5, 2, False)
mount("courser", "Courser", ["item.conveyance.mount.war", "item.conveyance.mount"], 250, 25, "ride", 8, 2, True, default_for="item.conveyance.mount.war")
mount("destrier", "Destrier", ["item.conveyance.mount.war", "item.conveyance.mount"], 600, 30, "ride", 10, 3, True)
bi("saddle_tack", "Saddle and tack", ["item.conveyance.mount"], "conveyance", 10, 2, conveyance="tack", note="riding without a saddle: Handle (ride) beats take a Precision snag", slot_cap=1)
bi("barding_light", "Light barding", ["item.conveyance.mount"], "conveyance", 60, 0, conveyance="barding", reduction={"amount": 1, "harm_tags": ["harm.physical"]}, note="the mount's armor; its pace is one step slower in travel (10)", slot_cap=2)
bi("barding_heavy", "Heavy barding", ["item.conveyance.mount.war"], "conveyance", 300, 0, conveyance="barding", reduction={"amount": 2, "harm_tags": ["harm.physical"]}, note="war mounts only; travel pace one step slower", slot_cap=2)
for vid, nm, tag, pr, carry, crew, pace, upkeep, extra in [
        ("handcart", "Handcart", "item.conveyance.vehicle.cart", 5, 15, 1, "walk", 0, "pushed by one person"),
        ("cart", "Cart", "item.conveyance.vehicle.cart", 20, 60, 1, "walk", 1, "one draft animal"),
        ("wagon", "Wagon", "item.conveyance.vehicle.cart", 60, 150, 1, "walk (roads only)", 2, "two draft animals; off-road it is G4 in difficult terrain"),
        ("sledge", "Sledge", "item.conveyance.vehicle", 15, 40, 1, "walk (snow and ice)", 0, "one draft animal or two people"),
        ("carriage", "Carriage", "item.conveyance.vehicle", 250, 20, 1, "ride (roads only)", 4, "carries four in comfort; two horses"),
        ("raft", "Raft", "item.conveyance.vessel.boat", 5, 20, 1, "river, downstream only", 0, "poled"),
        ("rowboat", "Rowboat", "item.conveyance.vessel.boat", 25, 30, 1, "river and lake", 0, "four people"),
        ("keelboat", "Keelboat", "item.conveyance.vessel.boat", 300, 150, 6, "river (up and down)", 6, "sail and oars; a crew of six"),
        ("river_barge", "River barge", "item.conveyance.vessel.ship", 600, 300, 8, "river", 10, "a crew of eight"),
        ("cog", "Sailing cog", "item.conveyance.vessel.ship", 3000, 2000, 12, "sea", 40, "a crew of twelve; passage is usually bought, not the ship")]:
    bi(vid, nm, [tag], "conveyance", pr, 0, conveyance="vehicle" if "vehicle" in tag else "vessel", carry_capacity=carry, crew=crew,
       travel_pace=pace, upkeep_week=upkeep, note=extra, hull_clock=(None if "vehicle" in tag else {"segments": 4 if pr < 100 else (6 if pr < 1000 else 8), "rule": "cost.gear against a vessel ticks its hull clock by U(severity); full = foundering (10)"}),
       default_for=tag if vid in ("cart", "rowboat", "cog") else None)
for b in BI:
    if b.get("default_for") is None:
        b.pop("default_for", None)

# validate base items
ids = [b["id"] for b in BI]
assert len(ids) == len(set(ids)), "duplicate base item"
for b in BI:
    for t in b["item_tags"] + b.get("material_tags", []):
        chk_tag(t, b["id"])
    if b.get("deed_tag"):
        chk_tag(b["deed_tag"], b["id"])
    if b.get("make"):
        chk_tag(b["make"]["deed_tag"], b["id"])
    for e in b.get("effects", []) + b.get("intrinsic", []):
        chk_eff(e["effect_id"], b["id"])
        c = e["params"].get("condition")
        if c and c not in CONDS:
            DEFECTS.append(f"unknown condition {c} in {b['id']}")
    if b["kind"] == "weapon":
        assert len(b["weapon_properties"]) <= 2
# every level-2 and level-3 item tag used by kits resolves
KITS = load(os.path.join(D, "kits.yaml"))
def kit_tags(items, out):
    for it in items:
        if isinstance(it, dict) and "item_tag" in it:
            out.add(it["item_tag"])
kt = set()
for k in KITS["kits"]:
    kit_tags(k["items"], kt)
    for ch in k.get("choices", []) or []:
        for opt in ch["options"]:
            kit_tags(opt, kt)
def resolve(tag):
    for b in BI:
        if b.get("default_for") == tag:
            return b["id"]
    cands = [b["id"] for b in BI if tag in b["item_tags"]]
    return cands[0] if cands else None
KIT_RES = {t: resolve(t) for t in sorted(kt)}
for t, r in KIT_RES.items():
    if r is None:
        DEFECTS.append(f"kit tag {t} has no base item")

# ================================================================== ITEM PROPERTIES
PROPS = []
WEAP = ["item.weapon"]
ARM = ["item.armor", "item.shield", "item.garment"]
WORN = ["item.armor", "item.shield", "item.garment", "item.jewelry"]
JEWEL = ["item.jewelry"]
ANY = ["item.weapon", "item.armor", "item.shield", "item.garment", "item.jewelry", "item.tool"]
CHANCE = {1: "20", 2: "19-20", 3: "18-20", 4: "17-20", 5: "16-20"}

def prop(id, name, kind, family, gate, mod_group, weight, tiers, base_kinds, bias, text, min_tier=1, sig=False,
         excluded=None, place=False, domains=("loot", "craft", "gift"), share=None, **kw):
    e = dict(id="prop." + id, name=name, kind=kind, family=family, gate_tags=gate, excluded_tags=excluded or [],
             base_kinds=base_kinds, mod_group=mod_group, weight=weight, signature_eligible=sig, min_tier=min_tier,
             place_gated=place, bias=bias, domains=list(domains), tiers=tiers, text=text, tags=[],
             lifecycle="provisional", basis=kw.pop("basis", ["08.3", "08.4", "T-08-9"]))
    if share:
        e["item_share"] = share
    e.update(kw)
    PROPS.append(e)
    return e

def T(*pairs):
    return [{"tier": t, "effects": effs} for t, effs in pairs]

FOLK_MADE = ["creature.folk", "material.metal", "org"]

# ---------- mundane (kind: mundane) -- work without attunement while equipped
prop("keen", "Keen", "mundane", "harm_edge", FOLK_MADE + ["material.bone.fang", "material.stone.volcanic", "material.gem.crystal"], "harm_edge", 3,
     T((1, [eff("eff.harm_edge", amount=1, applies_when="Strikes with this weapon")])), WEAP, "strike",
     "+1 harm with this weapon's Strikes (the item share of harm edge, 08.2.2).", excluded=[], saturated_by=["versatile"], share={"harm_edge": 1})
prop("balanced", "Balanced", "mundane", "edge", FOLK_MADE + ["material.wood.fine", "creature.spirit.fey"], "strike_edge", 3,
     T((1, [eff("eff.check_edge", amount=1, applies_when="Strikes with this weapon")])), WEAP, "strike",
     "+1 to Strikes with this weapon.", share={"edge": 1})
prop("guarding", "Guarding", "mundane", "edge", FOLK_MADE + ["material.wood.fine.ironwood", "creature.construct"], "guard_edge", 2,
     T((1, [eff("eff.defense_edge", amount=1, attribute="agility", applies_when="Guard against aimed attacks")])), ["item.armor", "item.garment"], "ward",
     "+1 to Guard (the item share of edge: worthless beside a shield or a parrying weapon, which already fill it).", share={"edge": 1})
prop("sturdy", "Sturdy", "mundane", "durability", FOLK_MADE + ["material.metal.iron", "material.wood.fine.ironwood", "creature.folk.dwarf", "creature.construct"], "durability", 3,
     T((1, [eff("eff.08.cost_step", ladder="severity", steps=-1, applies_when="cost.gear targets this item")])), ANY, "ward",
     "A cost.gear against this item is taken one severity rung lighter (S3 damaged becomes S2 misplaced).")
prop("light_make", "Light make", "mundane", "carry", FOLK_MADE + ["material.wood.fine", "creature.folk.elf", "material.fiber.silk"], "load", 2,
     T((1, [eff("eff.08.adjust", quantity="carry", amount=1, applies_when="while this item is carried")])), ["item.armor", "item.weapon", "item.shield", "item.tool"], "move",
     "Carrying capacity +1 while it is carried (it weighs less than its kind).")
prop("quiet", "Quiet", "mundane", "snag_waiver", ["creature.folk.elf", "creature.folk.halfling", "material.hide", "creature.beast.predator.feline", "creature.spirit.fey"], "armor_snag", 2,
     T((1, [eff("eff.05.waive", event_kind="this armor's Sneak snag", applies_when="Sneak in this armor")])), ["item.armor"], "move",
     "This armor imposes no Sneak snag.", excluded=[])
prop("supple", "Supple", "mundane", "snag_waiver", ["creature.folk.dwarf", "material.hide.scale", "creature.beast.aquatic", "material.fiber.silk"], "armor_snag", 2,
     T((1, [eff("eff.05.waive", event_kind="this armor's Swim and Exert snags", applies_when="Swim or Exert in this armor")])), ["item.armor"], "move",
     "This armor imposes no Swim or Exert snag.")
prop("reinforced", "Reinforced", "mundane", "reduction", FOLK_MADE + ["material.hide.scale", "material.hide.chitin", "material.bone", "creature.beast.monstrous"], "armor_red", 2,
     T((1, [eff("eff.harm_reduction", amount=1, harm_tags=["harm.physical"])])), ["item.armor.light", "item.armor.medium"], "ward",
     "Reduce physical harm you take by 1 more (light and medium armor only: the item share of reduction is 3).", share={"reduction": 1})
prop("fine_cut", "Fine cut", "mundane", "lever", ["creature.folk.human", "creature.folk.elf", "org.crown", "org.guild", "material.fiber.silk", "creature.spirit.fey"], "social", 2,
     T((1, [eff("eff.grant_lever", type="precision", for_verbs=["verb.talk"], for_tags=["deed.influence.etiquette", "deed.influence.persuasion"], duration="while worn", applies_when="where station or taste matters")])), ["item.garment", "item.jewelry"], "social",
     "Citable as a Precision lever on etiquette and persuasion where station or taste matters.")
prop("deep_pockets", "Deep pockets", "mundane", "carry", FOLK_MADE + ["material.hide.leather", "creature.beast.herd"], "load", 1,
     T((1, [eff("eff.08.adjust", quantity="carry", amount=2, applies_when="while worn")])), ["item.garment.cloak", "item.garment.clothing", "item.tool.container"], "move",
     "Carrying capacity +2 while worn.")
prop("warm", "Warm", "mundane", "hazard", ["material.hide.fur", "creature.elemental.frost", "creature.beast.predator.ursine", "terrain.frozen"], "env_cold", 2,
     T((1, [eff("eff.hazard_step", steps=-1, harm_tags=["harm.frost"], applies_when="hazard")])), ["item.garment", "item.armor.light", "item.jewelry"], "ward",
     "Cold hazards count one severity rung lower for you.", place=True)
prop("cool", "Cool", "mundane", "hazard", ["material.fiber.silk", "creature.elemental.fire", "terrain.arid"], "env_heat", 2,
     T((1, [eff("eff.hazard_step", steps=-1, harm_tags=["harm.fire.heat"], applies_when="hazard")])), ["item.garment", "item.jewelry"], "ward",
     "Heat hazards count one severity rung lower for you.", place=True)
prop("weatherproof", "Weatherproof", "mundane", "snag_waiver", ["material.hide", "creature.beast.aquatic", "terrain.wetland", "terrain.water.coast"], "env_wet", 1,
     T((1, [eff("eff.05.waive", event_kind="snags from rain, sleet or a wet camp on rests and watch checks (10)", applies_when="while worn")])), ["item.garment.cloak", "item.garment.headwear", "item.tool.container"], "ward",
     "Rain, sleet and a wet camp impose no snag on your rests and watch checks.", place=True)
prop("masters_mark", "Master's mark", "mundane", "lever", ["creature.folk", "org.guild.craft"], "social", 1,
     T((1, [eff("eff.grant_lever", type="precision", for_verbs=["verb.talk"], for_tags=["deed.influence.trade"], duration="while carried", applies_when="selling or showing this item to a buyer who knows the mark")])), ANY, "social",
     "A maker's mark buyers know: a Precision lever when selling or showing it (08.8.5).", domains=("loot", "craft"))

# ---------- skill-targeted gear (edge +1 on one deed tag) -- passive, attuned
SKILLS = [
 ("stalkers", "Stalker's", "deed.guile.stealth", ["item.garment.footwear", "item.garment.cloak"], ["creature.beast.predator.feline", "creature.spirit.fey", "creature.folk.goblin", "creature.folk.halfling", "creature.undead.spectral", "terrain.forest"], "move"),
 ("deft", "Deft", "deed.guile.thievery", ["item.garment.gloves", "item.tool.kit"], ["creature.folk.goblin", "creature.construct.clockwork", "creature.folk.halfling", "org.outlaw.thieves"], "craft"),
 ("tracker", "Tracker's", "deed.wilds.tracking", ["item.garment.footwear", "item.jewelry.charm"], ["creature.beast.predator.canine", "creature.folk.beastfolk", "org.order.hunters"], "sense"),
 ("wayfinder", "Wayfinder's", "deed.wilds.navigation", ["item.jewelry", "item.tool"], ["creature.beast.avian", "creature.spirit.place", "creature.elemental.air", "terrain.water.sea"], "move"),
 ("survivor", "Survivor's", "deed.wilds.survival", ["item.garment", "item.tool.container"], ["creature.beast", "creature.spirit.place", "terrain.arid", "terrain.frozen"], "ward"),
 ("climbers", "Climber's", "deed.martial.athletics", ["item.garment.gloves", "item.garment.footwear"], ["creature.beast.vermin.arachnid", "creature.beast.reptile.lizard", "creature.folk.giant", "creature.beast.herd", "terrain.highland"], "move"),
 ("sages", "Sage's", "deed.lore.arcana", ["item.jewelry.circlet", "item.tool.implement", "item.garment.headwear"], ["creature.spirit", "creature.undead.sovereign", "material.essence", "org.order.arcane"], "arcane"),
 ("lorekeepers", "Lorekeeper's", "deed.lore.history", ["item.jewelry.circlet", "item.jewelry.amulet"], ["creature.spirit.ancestor", "creature.folk.dwarf", "creature.folk.elf", "terrain.ruin"], "sense"),
 ("beastwise", "Beastwise", "deed.lore.bestiary", ["item.jewelry.charm", "item.garment.headwear"], ["creature.beast.monstrous", "creature.dragon", "creature.horror", "org.order.hunters"], "sense"),
 ("honeyed", "Honeyed", "deed.influence.persuasion", ["item.jewelry.ring", "item.jewelry.amulet"], ["creature.spirit.fey", "creature.fiend.devil", "creature.folk.elf", "org.crown.noble"], "social"),
 ("dread", "Dread", "deed.influence.intimidation", ["item.armor", "item.garment.headwear", "item.jewelry.charm"], ["creature.folk.orc", "creature.horror.abomination", "creature.beast.predator.ursine", "creature.fiend.demon", "creature.dragon"], "social"),
 ("piercing_eye", "Piercing", "deed.influence.insight", ["item.jewelry"], ["creature.fiend.devil", "creature.fiend.possessor", "creature.spirit.celestial"], "sense"),
 ("minstrels", "Minstrel's", "deed.influence.performance", ["item.tool.instrument", "item.jewelry"], ["creature.spirit.fey", "creature.folk.elf", "creature.folk.halfling"], "social"),
 ("haggler", "Haggler's", "deed.influence.trade", ["item.jewelry.ring", "item.garment.clothing"], ["creature.folk.goblin", "creature.folk.dwarf", "org.guild.merchant", "creature.fiend.devil"], "social"),
 ("seeker", "Seeker's", "deed.lore.investigation", ["item.jewelry.circlet", "item.tool"], ["creature.construct.clockwork", "creature.undead.spectral", "creature.spirit.ancestor"], "sense"),
 ("physicks", "Physician's", "deed.lore.medicine", ["item.tool.kit.healer", "item.jewelry.amulet", "item.garment.gloves"], ["creature.spirit.celestial", "material.botanical.herb.healing", "org.faith"], "craft"),
]
for sid, nm, deed, kinds, gate, bias in SKILLS:
    chk_tag(deed, sid)
    prop(sid, nm, "passive", "edge", gate, "skill_edge", 2,
         T((1, [eff("eff.check_edge", amount=1, applies_when=f"beats whose primary deed tag is {deed} or under it")])), kinds, bias,
         f"+1 to checks whose primary deed tag is {deed} or under it.", share={"edge": 1})
CRAFTS = ["smithing", "woodcraft", "leathercraft", "textiles", "alchemy", "cookery", "building", "artifice", "jewelcraft", "enchanting", "scribing"]
CRAFT_GATE = {"smithing": ["creature.folk.dwarf", "material.metal", "creature.elemental.fire", "creature.construct.golem.iron"],
              "woodcraft": ["creature.folk.elf", "material.wood", "creature.horror.plant.treant", "creature.spirit.place"],
              "leathercraft": ["creature.beast", "material.hide"], "textiles": ["creature.beast.vermin.arachnid", "material.fiber", "creature.spirit.fey"],
              "alchemy": ["material.essence", "material.botanical", "creature.horror.fungal", "creature.horror.ooze"],
              "cookery": ["creature.folk.halfling", "material.botanical.herb", "creature.beast.herd"],
              "building": ["creature.folk.dwarf", "material.stone", "creature.construct.golem.stone", "creature.elemental.earth"],
              "artifice": ["creature.construct.clockwork", "creature.folk.goblin", "creature.folk.dwarf", "material.metal.copper"],
              "jewelcraft": ["material.gem", "material.metal.gold", "creature.dragon.great", "creature.folk.dwarf"],
              "enchanting": ["material.essence", "material.wood.witchwood", "material.gem.crystal", "creature.spirit"],
              "scribing": ["creature.spirit.ancestor", "org.order.monastic", "org.guild.scholarly", "creature.folk.elf"]}
for c in CRAFTS:
    prop("craft_" + c, f"Craftsman's ({c})", "passive", "edge", CRAFT_GATE[c], "craft_edge", 1,
         T((1, [eff("eff.check_edge", amount=1, applies_when=f"crafting beats whose primary deed tag is deed.craft.{c} or under it")])),
         ["item.tool.trade", "item.garment.gloves"], "craft", f"+1 to crafting beats of deed.craft.{c}.", share={"edge": 1})

# ---------- elemental families
ELEM = {  # harm branch: (gates, name, strike cond, sig names)
 "fire":      (["creature.elemental.fire", "creature.dragon", "creature.fiend.demon", "creature.fiend.hellbeast", "material.essence.gland.fire", "material.stone.volcanic", "deed.arcane.fire", "terrain.underground.cave.volcanic"], "Ember", "cond.burning"),
 "frost":     (["creature.elemental.frost", "creature.dragon.great", "material.hide.fur.winter", "deed.arcane.frost", "terrain.frozen"], "Rime", "cond.chilled"),
 "storm":     (["creature.elemental.air", "creature.dragon.serpentine", "deed.arcane.storm", "deed.primal.weather", "terrain.highland.mountains.peak"], "Thunder", "cond.dazed"),
 "corrosion": (["creature.horror.ooze", "creature.dragon.drake", "material.essence.ichor", "deed.craft.alchemy.reagents"], "Acid", "cond.weakened"),
 "venom":     (["creature.beast.reptile.serpent", "creature.beast.vermin", "creature.dragon.wyvern", "creature.horror.fungal", "material.essence.gland.venom", "material.botanical.herb.toxic", "deed.guile.poisoncraft", "terrain.wetland"], "Venom", "cond.poisoned"),
 "blight":    (["creature.undead", "creature.fiend", "material.essence.residue.grave_dust", "deed.arcane.necromancy", "terrain.ruin.tomb"], "Grave", "cond.weakened"),
 "radiance":  (["creature.spirit.celestial", "org.faith", "deed.divine", "material.metal.silver.pure"], "Dawn", "cond.blinded"),
 "mind":      (["creature.horror.aberration", "creature.fiend.possessor", "creature.spirit.fey.court", "deed.arcane.mind"], "Dream", "cond.distracted"),
 "arcane":    (["creature.construct", "creature.spirit", "material.essence", "material.gem.crystal", "deed.arcane", "org.order.arcane"], "Spell", "cond.exposed"),
}
RES_AMT = {1: 1, 2: 2, 3: 2, 4: 3, 5: 3}
for h, (gate, word, cond) in ELEM.items():
    prop(f"resist_{h}", f"{word}-warded", "passive", "reduction", gate, f"resist_{h}", 3,
         [{"tier": t, "effects": [eff("eff.harm_reduction", amount=RES_AMT[t], harm_tags=[f"harm.{h}"])]} for t in range(1, 6)],
         WORN, "ward", f"Reduce harm.{h} harm you take by 1 (tier 1), 2 (tiers 2-3) or 3 (tiers 4-5).", share={"reduction": 3})
    prop(f"strike_{h}", f"{word}-forged", "passive", "strike_delivery", gate, "strike_form", 2,
         [{"tier": t, "effects": [eff("eff.strike_delivery", priority_rank=14 + t, harm_tags=[f"harm.{h}"], harm_edge=(1 if t >= 3 else 0), duration="permanent", cosmetic_merge=False)]} for t in range(1, 6)],
         WEAP, "strike", f"Your Strikes with this weapon deal harm.{h} in place of their own harm type; +1 harm from tier 3 (the item share).",
         share={"harm_edge": 1}, saturated_by_rule="its tier-3 harm edge adds nothing beside another item harm edge (08.2.2)")
    if cond not in CONDS:
        DEFECTS.append(cond)
    prop(f"onhit_{h}", f"{word}-touched", "passive", "on_hit", gate, "on_hit", 2,
         [{"tier": t, "trigger": {"hook": "on_attack_hit", "chance": "natural " + CHANCE[t]},
           "effects": [eff("eff.apply_condition", condition=cond, severity=("S2" if t >= 4 else "S1"), duration=("rounds:2" if cond in ("cond.dazed", "cond.blinded") else "scene"), target="the creature hit")]} for t in range(1, 6)],
         WEAP, "strike", f"On a hit whose d20 shows the tier's natural range (20 at tier 1 widening to 16-20 at tier 5), apply {cond} to the creature hit.")
# hazard wards, retorts and condition wards per harm branch (pool depth for elemental and spirit sources)
HAZ = {"fire": "harm.fire.heat", "frost": "harm.frost.cold", "storm": "harm.storm.lightning", "corrosion": "harm.corrosion.acid",
       "venom": "harm.venom.gas", "blight": "harm.blight.disease", "radiance": "harm.radiance.light", "mind": "harm.mind.strain", "arcane": "harm.arcane.raw"}
CWARD = {"fire": "cond.burning", "frost": "cond.chilled", "storm": "cond.deafened", "blight": "cond.weakened", "mind": "cond.distracted", "arcane": "cond.silenced"}
for h, (gate, word, cond) in ELEM.items():
    prop(f"hazard_{h}", f"{word}-proof", "passive", "hazard", gate, {"fire": "env_heat", "frost": "env_cold"}.get(h, f"env_{h}"), 2,
         T((1, [eff("eff.hazard_step", steps=-1, harm_tags=[HAZ[h]], applies_when="hazard")])), WORN + ["item.tool.container"], "ward",
         f"Hazards of {HAZ[h]} count one severity rung lower for you.", place=True)
    prop(f"retort_{h}", f"{word}-thorned", "passive", "retort", gate, "retort", 2,
         [{"tier": t, "trigger": {"hook": "on_hit_taken", "chance": "natural " + CHANCE[t]},
           "effects": [eff("eff.deal_harm", severity=("S2" if t >= 4 else "S1"), harm_tags=[f"harm.{h}"], target="the attacker, if it struck you in melee")]} for t in range(1, 6)],
         ["item.armor", "item.shield", "item.garment.cloak", "item.jewelry.amulet"], "strike",
         f"When a melee attack hits you and its d20 shows the tier's natural range, the attacker takes S1 harm.{h} harm (S2 from tier 4).")
    if h in CWARD:
        prop(f"ward_{h}_cond", f"{word}-hardened", "passive", "ward", gate, "cond_ward_" + CWARD[h].split(".")[1], 2,
             T((3, [eff("eff.condition_immunity", forbid={"conditions": [CWARD[h]]}, target="self")])), WORN, "ward",
             f"{CWARD[h]} cannot be applied to you (tier 3+).", min_tier=3)
for pk, nm, gate in [("cut", "Cut-proof", ["creature.beast.reptile", "creature.beast.predator", "material.hide.scale", "creature.dragon", "creature.construct.golem", "creature.beast.monstrous"]),
                     ("pierce", "Pierce-proof", ["material.hide.chitin", "creature.beast.vermin", "creature.construct", "creature.beast.herd", "creature.horror.plant"]),
                     ("crush", "Crush-proof", ["creature.horror.ooze", "creature.beast.monstrous", "creature.folk.giant", "creature.elemental.earth", "material.hide.fur", "creature.beast.predator.ursine"])]:
    prop(f"resist_{pk}", nm, "passive", "reduction", gate, "resist_physical", 2,
         [{"tier": t, "effects": [eff("eff.harm_reduction", amount=RES_AMT[t], harm_tags=[f"harm.physical.{pk}"])]} for t in range(1, 6)],
         WORN, "ward", f"Reduce harm.physical.{pk} harm you take by 1-3 by tier (worn armor counts toward the item share of 3).", share={"reduction": 3})
# physical on-hit / bleed etc.
for pid, nm, gate, cond, dur in [("onhit_bleed", "Rending", ["creature.beast.predator", "material.bone.fang", "creature.undead.ravenous", "creature.beast.monstrous"], "cond.bleeding", "until_cleansed"),
                                  ("onhit_stagger", "Staggering", ["creature.folk.giant", "creature.beast.herd", "creature.construct.golem", "creature.elemental.earth"], "cond.off_balance", "rounds:1"),
                                  ("onhit_dread", "Dreadful", ["creature.undead.sovereign", "creature.fiend", "creature.horror.abomination", "creature.dragon.great"], "cond.frightened", "rounds:2"),
                                  ("onhit_hobble", "Hobbling", ["creature.horror.plant", "creature.horror.ooze", "creature.spirit.fey.wild", "creature.beast.vermin.arachnid"], "cond.slowed", "rounds:2"),
                                  ("onhit_expose", "Hunter's", ["creature.beast.predator", "creature.folk.beastfolk", "org.order.hunters"], "cond.exposed", "rounds:2")]:
    prop(pid, nm, "passive", "on_hit", gate, "on_hit", 2,
         [{"tier": t, "trigger": {"hook": "on_attack_hit", "chance": "natural " + CHANCE[t]},
           "effects": [eff("eff.apply_condition", condition=cond, severity=("S2" if t >= 4 else "S1"), duration=dur, target="the creature hit")]} for t in range(1, 6)],
         WEAP, "strike", f"On a hit whose d20 shows the tier's natural range, apply {cond} to the creature hit.")
# banes: harm edge vs a creature kind (shares the harm_edge mod group with keen)
for bid, nm, gate, vs in [("bane_undead", "Undeath-bane", ["material.metal.silver.pure", "org.faith", "creature.spirit.celestial", "deed.divine.exorcism"], "creature.undead"),
                           ("bane_fey", "Fey-bane", ["material.metal.iron.cold", "creature.folk.dwarf", "org.order.hunters"], "creature.spirit.fey"),
                           ("bane_fiend", "Fiend-bane", ["org.faith", "creature.spirit.celestial", "material.metal.silver.pure"], "creature.fiend"),
                           ("bane_dragon", "Dragon-bane", ["creature.dragon", "material.hide.scale.dragon", "creature.folk.dwarf"], "creature.dragon"),
                           ("bane_giant", "Giant-bane", ["creature.folk.dwarf", "creature.folk.giant", "creature.folk.halfling"], "creature.folk.giant"),
                           ("bane_beast", "Beast-bane", ["org.order.hunters", "creature.beast.monstrous", "creature.folk.beastfolk"], "creature.beast"),
                           ("bane_construct", "Construct-bane", ["creature.construct", "creature.elemental.air", "deed.arcane.storm"], "creature.construct"),
                           ("bane_horror", "Horror-bane", ["creature.horror", "creature.spirit.celestial", "org.order.knightly"], "creature.horror")]:
    chk_tag(vs, bid)
    prop(bid, nm, "passive", "harm_edge", gate, "harm_edge", 2,
         T((1, [eff("eff.harm_edge", amount=1, applies_when=f"the target is {vs} or under it")]),
           (3, [eff("eff.harm_edge", amount=1, applies_when=f"the target is {vs} or under it"), eff("eff.grant_lever", type="amplifying", for_verbs=["verb.strike"], for_tags=[], duration="while equipped", applies_when=f"the target is {vs} or under it")])),
         WEAP, "strike", f"+1 harm against {vs} (the item share); from tier 3 also a citable Amplifying lever on Strikes against them.", share={"harm_edge": 1})

# ---------- senses, movement, wards, sustain, light, carry, supply, implement, social, lore
prop("darksight", "Darksight", "passive", "lever", ["creature.folk.dwarf", "creature.folk.goblin", "creature.beast.predator.feline", "creature.undead", "terrain.underground", "creature.beast.vermin"], "senses", 3,
     T((1, [eff("eff.grant_lever", type="precision", for_verbs=["verb.observe", "verb.strike"], for_tags=[], duration="while equipped", applies_when="a fact of darkness or dim light is cited as a snag on the beat")])),
     ["item.jewelry", "item.garment.headwear"], "sense", "When darkness or dim light is cited as a snag on your Observe or Strike, cite this as a Precision lever on the same beat.", place=True)
prop("keen_ears", "Keen ears", "passive", "lever", ["creature.beast.predator", "creature.beast.herd.cervine", "creature.folk.elf", "creature.folk.beastfolk.gnoll"], "senses", 2,
     T((1, [eff("eff.grant_lever", type="precision", for_verbs=["verb.observe"], for_tags=[], duration="while equipped", applies_when="noticing by sound")])), WORN, "sense",
     "A Precision lever on Observe to notice by sound.")
prop("scent", "Scenting", "passive", "lever", ["creature.beast.predator.canine", "creature.folk.beastfolk", "creature.undead.ravenous.ghoul"], "senses", 2,
     T((1, [eff("eff.grant_lever", type="precision", for_verbs=["verb.observe"], for_tags=["deed.wilds.tracking"], duration="while equipped", applies_when="tracking or noticing by scent")])), WORN, "sense",
     "A Precision lever on Observe to track or notice by scent.")
prop("tremor", "Tremor-sense", "passive", "lever", ["creature.elemental.earth", "creature.beast.vermin", "creature.construct.golem.stone", "terrain.underground"], "senses", 1,
     T((2, [eff("eff.grant_lever", type="precision", for_verbs=["verb.observe"], for_tags=[], duration="while equipped", applies_when="noticing a creature moving on the same ground, including unseen ones")])), ["item.garment.footwear", "item.jewelry"], "sense",
     "A Precision lever on Observe to notice anything moving on the ground you stand on, seen or unseen.", min_tier=2, place=True)
prop("spirit_sight", "Spirit-sight", "passive", "lever", ["creature.spirit", "creature.undead.spectral", "deed.divine.revelation", "deed.primal.spirits"], "senses", 2,
     T((1, [eff("eff.grant_lever", type="precision", for_verbs=["verb.observe"], for_tags=[], duration="while equipped", applies_when="the thing sought is a spirit, an unseen being or a working with trait.nature.magical")])), ["item.jewelry", "item.tool.implement"], "sense",
     "A Precision lever on Observe for spirits, unseen beings and magical workings.")
prop("climbing", "Spider-grip", "passive", "movement", ["creature.beast.vermin.arachnid", "creature.beast.reptile.lizard", "creature.horror.plant.creeper"], "movement", 1,
     T((3, [eff("eff.movement_mode", priority_rank=15, mode="climb", duration="while equipped")])), ["item.garment.gloves", "item.garment.footwear"], "move",
     "You move by climb (tier 3+).", min_tier=3)
prop("swimming", "Seal-skin", "passive", "movement", ["creature.beast.aquatic", "creature.elemental.water", "terrain.water.sea", "terrain.water.lake"], "movement", 1,
     T((3, [eff("eff.movement_mode", priority_rank=15, mode="swim", duration="while equipped")])), ["item.garment", "item.armor.light", "item.jewelry"], "move",
     "You move by swim (tier 3+).", min_tier=3, place=True)
prop("featherfall", "Featherfall", "passive", "hazard", ["creature.beast.avian", "creature.elemental.air", "creature.spirit.fey", "terrain.highland.cliffs"], "fall", 1,
     T((2, [eff("eff.hazard_step", steps=-1, harm_tags=["harm.physical.crush"], applies_when="harm from a fall")]), (4, [eff("eff.hazard_step", steps=-1, harm_tags=["harm.physical.crush"], applies_when="harm from a fall"), eff("eff.grant_lever", type="protective", for_verbs=["verb.exert", "verb.evade"], for_tags=[], duration="while equipped", applies_when="a beat whose failure could drop you")])),
     ["item.garment.cloak", "item.jewelry", "item.garment.footwear"], "move", "Harm from a fall counts one severity rung lower; from tier 4 also a Protective lever on any beat whose failure could drop you.", min_tier=2, place=True)
prop("waterbreath", "Gill-charm", "passive", "ward", ["creature.beast.aquatic", "creature.elemental.water", "creature.dragon.serpentine", "terrain.water"], "breath", 1,
     T((2, [eff("eff.condition_immunity", forbid={"conditions": ["cond.choking"]}, target="self", applies_when="the source is water")])), ["item.jewelry", "item.garment.headwear"], "ward",
     "Water cannot apply cond.choking to you (tier 2+).", min_tier=2, place=True)
for wid, nm, gate, cnd, mt in [("ward_fear", "Steadfast", ["creature.undead.sovereign", "creature.spirit.celestial", "creature.dragon", "org.order.knightly", "deed.divine.oaths"], "cond.frightened", 3),
                                ("ward_charm", "Clear-eyed", ["creature.fiend.possessor", "creature.spirit.fey", "creature.horror.aberration", "deed.arcane.mind"], "cond.charmed", 3),
                                ("ward_poison", "Venom-proof", ["creature.horror.fungal", "creature.beast.vermin", "creature.beast.reptile.serpent", "creature.dragon.wyvern", "material.essence.gland.venom"], "cond.poisoned", 3),
                                ("ward_daze", "Iron-skulled", ["creature.construct.golem", "creature.folk.giant", "creature.folk.dwarf"], "cond.dazed", 3),
                                ("ward_blind", "Unblinking", ["creature.spirit.celestial", "creature.horror.aberration", "creature.construct.clockwork"], "cond.blinded", 4),
                                ("ward_bleed", "Clotting", ["creature.undead", "creature.construct", "creature.folk.giant.troll", "creature.horror.ooze"], "cond.bleeding", 3)]:
    prop(wid, nm, "passive", "ward", gate, "cond_ward_" + cnd.split(".")[1], 2,
         T((mt, [eff("eff.condition_immunity", forbid={"conditions": [cnd]}, target="self")])), WORN, "ward",
         f"{cnd} cannot be applied to you (tier {mt}+).", min_tier=mt)
prop("mind_guard", "Mind-guard", "passive", "edge", ["creature.horror.aberration", "creature.fiend.possessor", "creature.undead.sovereign", "deed.arcane.warding", "deed.divine.warding"], "resolve_edge", 2,
     T((1, [eff("eff.defense_edge", amount=1, attribute="resolve", applies_when="against effects carrying trait.nature.mental")])), ["item.jewelry", "item.garment.headwear"], "ward",
     "+1 to your Resolve defense against mental effects.", share={"edge": 1})
prop("knitting", "Knitting flesh", "passive", "sustain", ["creature.folk.giant.troll", "creature.undead.ravenous", "creature.horror.plant", "creature.horror.ooze"], "sustain", 1,
     [{"tier": t, "trigger": {"hook": "on_vitality_threshold", "params": {"threshold": "half"}},
       "effects": [eff("eff.restore", quantity="vitality", units=(1 if t < 3 else (2 if t < 5 else 3)), target="self")], "limits": {"per": "scene_end", "uses": 1}} for t in (2, 3, 5)],
     WORN, "ward", "Once per scene, when your Vitality falls to half or below, regain 1 (tier 2), 2 (tiers 3-4) or 3 (tier 5) Vitality. Fire harm taken this scene stops it.", min_tier=2)
prop("glowing", "Glowing", "passive", "light", ["creature.elemental.fire", "creature.spirit.celestial", "creature.undead.spectral", "material.gem.crystal", "creature.folk.elf"], "light", 2,
     T((1, [eff("eff.write_fact", subject="the bearer", predicate="emits_light", value="dim to band.close while unhooded (the bearer may cover it as a free activity)")])), ANY, "sense",
     "Sheds dim light to band.close; covered or uncovered as a free activity (10's light).")
prop("pack_mule", "Pack-bearer", "passive", "carry", ["creature.beast.herd", "creature.beast.predator.ursine", "creature.folk.giant", "creature.construct.golem"], "load", 2,
     T((1, [eff("eff.08.adjust", quantity="carry", amount=2, applies_when="while worn")]), (3, [eff("eff.08.adjust", quantity="carry", amount=4, applies_when="while worn")])),
     ["item.armor", "item.garment", "item.jewelry", "item.tool.container"], "move", "Carrying capacity +2 (+4 from tier 3; the item share of carry is +4).", share={"carry": 4})
prop("waybread", "Waybread", "passive", "supply", ["creature.spirit.fey", "creature.spirit.place", "creature.folk.halfling", "material.botanical"], "supply", 1,
     T((3, [eff("eff.08.adjust", quantity="supply_use", amount=-1, applies_when="the day's supply consumption, at most once per day")])), ["item.tool.container", "item.jewelry.charm"], "move",
     "Your daily supply use is 1 lower (tier 3+; never below 0; the item share of supply use is -1).", min_tier=3, share={"supply_use": -1})
prop("swift", "Swift", "passive", "lever", ["creature.beast.herd", "creature.elemental.air", "creature.spirit.fey.wild", "creature.beast.avian"], "pace", 1,
     T((2, [eff("eff.grant_lever", type="precision", for_verbs=["verb.move", "verb.exert"], for_tags=["deed.martial.athletics.running"], duration="while equipped", applies_when="running, fleeing or chasing (06.12)")])),
     ["item.garment.footwear", "item.jewelry.charm"], "move", "A Precision lever on Move and Exert to run, flee or chase.", min_tier=2)
prop("commanding", "Commanding", "passive", "lever", ["org.crown.military", "org.crown.noble", "creature.folk.orc", "creature.fiend.devil.enforcer", "creature.dragon.great"], "social", 1,
     T((1, [eff("eff.grant_lever", type="precision", for_verbs=["verb.talk"], for_tags=["deed.influence.command"], duration="while equipped", applies_when="giving orders to those who follow you or should")])),
     ["item.jewelry", "item.armor", "item.garment.headwear"], "social", "A Precision lever on Talk to command.")
prop("lore_whispers", "Whispering", "passive", "lever", ["creature.spirit.ancestor", "creature.undead.spectral", "terrain.ruin", "creature.undead.sovereign.lich"], "lore", 1,
     T((1, [eff("eff.grant_lever", type="precision", for_verbs=["verb.recall"], for_tags=["deed.lore.history", "deed.lore.religion"], duration="while equipped", applies_when="recalling the past of a place or a dead one")])),
     ["item.jewelry", "item.goods"], "sense", "A Precision lever on Recall about the past of a place or of the dead.", place=True)
# implements (arcane bias): one per magic branch family
for imp, nm, gate, branch in [("conduit_arcane", "Conduit", ["deed.arcane", "material.wood.witchwood", "material.gem.crystal", "creature.spirit", "org.order.arcane"], "deed.arcane"),
                               ("conduit_divine", "Blessed", ["deed.divine", "org.faith", "creature.spirit.celestial", "material.metal.silver"], "deed.divine"),
                               ("conduit_primal", "Wild-bound", ["deed.primal", "creature.spirit.place", "creature.spirit.fey.wild", "material.botanical", "org.order.druidic"], "deed.primal")]:
    prop(imp, nm, "passive", "edge", gate, "effect_dc_edge", 2,
         T((1, [eff("eff.effect_dc_edge", amount=1, applies_when=f"workings whose first tag is under {branch}")])), ["item.tool.implement"], "arcane",
         f"+1 to the DC of your workings under {branch} (the item share of edge).", share={"edge": 1})
    prop(imp + "_thrift", nm + " (thrift)", "passive", "focus_cost", gate, "focus_thrift", 1,
         T((3, [eff("eff.focus_cost_step", amount=-1, applies_when=f"the first working under {branch} you activate each scene (never below 1 for a cost that began above 0, 05.6.3)")])),
         ["item.tool.implement"], "arcane", f"Once per scene, your first working under {branch} costs 1 less Focus (tier 3+; within 05.6.3's -1 cap).", min_tier=3, sig=True)

# ---------- relic licenses: off-identity capability, no competence, feeds_evidence false
RELIC_LIC = [
 ("lic_stonesense", "Stone-sense", "lic.people.stonesense", ["creature.folk.dwarf", "creature.elemental.earth", "creature.construct.golem.stone", "terrain.underground"]),
 ("lic_starsight", "Starsight", "lic.people.starsight", ["creature.folk.elf", "creature.spirit.celestial", "creature.beast.avian"]),
 ("lic_cave_eyes", "Cave-eyes", "lic.people.cave_eyes", ["creature.folk.goblin", "creature.beast.vermin", "terrain.underground.cave"]),
 ("lic_keen_nose", "Hound's nose", "lic.people.keen_nose", ["creature.beast.predator.canine", "creature.folk.beastfolk"]),
 ("lic_tongue_elvish", "Elvish tongue", "lic.lang.elvish", ["creature.folk.elf", "creature.spirit.fey"]),
 ("lic_tongue_dwarvish", "Dwarvish tongue", "lic.lang.dwarvish", ["creature.folk.dwarf"]),
 ("lic_tongue_orcish", "Orcish tongue", "lic.lang.orcish", ["creature.folk.orc"]),
 ("lic_tongue_goblin", "Goblin tongue", "lic.lang.goblin", ["creature.folk.goblin"]),
 ("lic_tongue_giantish", "Giantish tongue", "lic.lang.giantish", ["creature.folk.giant"]),
 ("lic_tongue_kinspeech", "Kinspeech", "lic.lang.kinspeech", ["creature.folk.beastfolk", "creature.beast.monstrous.magical"]),
 ("lic_tongue_old", "The old tongue", "lic.lang.old_tongue", ["creature.spirit.ancestor", "creature.undead.sovereign", "creature.dragon.great", "terrain.ruin"]),
 ("lic_lockwork", "Lock-whisper", "lic.training.guile_thievery", ["creature.construct.clockwork", "creature.folk.goblin", "org.outlaw.thieves"]),
 ("lic_beast_handling", "Beast-friend", "lic.training.wilds_animals", ["creature.beast.herd", "creature.beast.predator", "creature.spirit.place", "creature.folk.beastfolk"]),
 ("lic_seafaring", "Sea-legs", "lic.training.wilds_seafaring", ["creature.beast.aquatic", "creature.elemental.water", "terrain.water.sea"]),
 ("lic_spirit_speech", "Spirit-speech", "lic.training.primal_spirits", ["creature.spirit.place", "creature.spirit.ancestor", "creature.spirit.fey.wild"]),
 ("lic_warding", "Ward-mark", "lic.training.arcane_warding", ["creature.construct", "creature.spirit.celestial.guardian", "org.order.arcane"]),
 ("lic_command", "Captain's token", "lic.training.influence_command", ["org.crown.military", "creature.folk.orc", "creature.fiend.devil.enforcer"]),
 ("lic_medicine", "Leech's gift", "lic.training.lore_medicine", ["creature.spirit.celestial", "org.faith", "material.botanical.herb.healing"]),
]
for rid, nm, licid, gate in RELIC_LIC:
    lic(licid)
    grade = "broken" if licid.startswith("lic.lang") else ("trained" if licid.startswith("lic.training") else "held")
    prop(rid, nm, "license", "license", gate, "relic_license", 1,
         T((2, [eff("eff.grant_license", license=licid, grade=grade, duration="while equipped and attuned", competence="none", feeds_evidence="false")])),
         ["item.jewelry", "item.garment.headwear", "item.tool"], "sense" if "lic.people" in licid else ("social" if "lang" in licid or "command" in licid else "craft"),
         f"While equipped and attuned you hold {licid} at grade {grade}: you may attempt what it licenses, with no competence from it (00.3.6) and no evidence from what you do under it (00.11.5).",
         min_tier=2, sig=True, relic=True, signature_only=True)

# ---------- the bound power: the signature slot holds an item-bound active ability
prop("bound_power", "Bound power", "item_ability", "item_ability", ["creature", "deed", "org", "material.essence"], "item_ability", 1,
     T((3, [eff("eff.08.bound_ability", ability="drawn by generate(gen.item_ability) with this item's source and circumstance", rank="by tier: 3 -> 1, 4 -> 2, 5+ -> 3", relic_surcharge="per 05.6.3", feeds_evidence="false")])),
     ANY, "arcane", "This item holds one active ability (generated by gen.item_ability), usable through an equipped slot while equipped and attuned; a relic (tier 3+).",
     min_tier=3, sig=True, signature_only=True, relic=True, excluded=["creature.beast.vermin", "creature.undead.mindless", "creature.horror.ooze"])

# ---------- creature signatures (signature_eligible; one or more per level-2 creature tag)
SIG = []
def sig(id, name, gate, kinds, bias, tiers, text, **kw):
    e = prop(id, name, kw.pop("kind", "passive"), kw.pop("family", "signature"), gate, kw.pop("mod_group", id), kw.pop("weight", 3), tiers, kinds, bias, text, sig=True, **kw)
    SIG.append(e)
    return e
L = lambda t, verbs, tags, when, ty="precision": eff("eff.grant_lever", type=ty, for_verbs=verbs, for_tags=tags, duration="while equipped", applies_when=when)
sig("sig_hunters_sense", "Hunter's sense", ["creature.beast.predator"], ["item.jewelry.charm", "item.garment"], "sense",
    T((1, [L(1, ["verb.observe"], ["deed.wilds.tracking"], "tracking a creature by sign or scent")]), (3, [L(3, ["verb.observe"], ["deed.wilds.tracking"], "tracking a creature by sign or scent", "amplifying"), L(3, ["verb.observe"], ["deed.wilds.tracking"], "tracking a creature by sign or scent")])),
    "A Precision lever on Observe to track (from tier 3 also an Amplifying lever on the same beat).")
sig("sig_long_stride", "Long stride", ["creature.beast.herd"], ["item.garment.footwear", "item.jewelry.charm"], "move",
    T((1, [L(1, ["verb.exert", "verb.move"], ["deed.martial.athletics.running"], "running far or keeping a pace on foot (10)")])), "A Precision lever on Exert and Move to run far or keep a hard pace.")
sig("sig_plague_proof", "Plague-proof", ["creature.beast.vermin"], WORN, "ward",
    [{"tier": t, "effects": [eff("eff.harm_reduction", amount=RES_AMT[t], harm_tags=["harm.blight.disease"])]} for t in range(1, 6)], "Reduce disease harm you take by 1-3 by tier.")
sig("sig_shed_skin", "Shed skin", ["creature.beast.reptile"], WORN, "move",
    [{"tier": t, "trigger": {"hook": "on_condition_applied", "params": {"to_or_by": "to"}}, "effects": [eff("eff.cleanse", condition_or_category="cond.grabbed", target="self")], "limits": {"per": ("scene_end" if t >= 3 else "rest_short"), "uses": 1}} for t in (1, 3)],
    "Once per short rest (per scene from tier 3), when you are grabbed you slip free at once.")
sig("sig_keen_eye", "Keen eye", ["creature.beast.avian"], ["item.jewelry", "item.garment.headwear"], "sense",
    T((1, [L(1, ["verb.observe"], [], "spotting by sight at band.far or beyond")]), (3, [L(3, ["verb.observe", "verb.strike"], [], "spotting or shooting by sight at band.far or beyond")])), "A Precision lever on Observe by sight at far range (from tier 3 also on shots there).")
sig("sig_tide_skin", "Tide-skin", ["creature.beast.aquatic"], ["item.garment", "item.armor.light", "item.jewelry"], "move",
    T((1, [L(1, ["verb.exert"], ["deed.martial.athletics.swimming"], "swimming")]), (3, [eff("eff.movement_mode", priority_rank=16, mode="swim", duration="while equipped")])), "A Precision lever on Exert to swim; from tier 3 you move by swim.")
sig("sig_monster_hide", "Monster's hide", ["creature.beast.monstrous"], ["item.armor", "item.garment.cloak"], "ward",
    T((1, [eff("eff.harm_reduction", amount=1, harm_tags=["harm.physical"])])), "Reduce physical harm you take by 1 (counts in the item share of 3).", share={"reduction": 1})
sig("sig_well_made", "Well-made", ["creature.folk.human"], ANY, "strike",
    T((1, [eff("eff.check_edge", amount=1, applies_when="beats that use this item as their tool or weapon")])), "+1 to beats that use this item as their tool or weapon.", share={"edge": 1}, mod_group="strike_edge")
sig("sig_starlight", "Starlight craft", ["creature.folk.elf"], ANY, "sense",
    T((1, [eff("eff.write_fact", subject="the bearer", predicate="emits_light", value="dim to band.close at will"), eff("eff.08.adjust", quantity="carry", amount=1, applies_when="while carried")])), "Sheds dim light at will and weighs almost nothing (carry +1).")
sig("sig_deep_forged", "Deep-forged", ["creature.folk.dwarf"], ANY, "ward",
    T((1, [eff("eff.08.cost_step", ladder="severity", steps=-1, applies_when="cost.gear targets this item")]), (3, [eff("eff.08.cost_step", ladder="severity", steps=-2, applies_when="cost.gear targets this item")])), "A cost.gear against it is taken one rung lighter (two from tier 3): dwarf-work does not break.")
sig("sig_lucky_stitch", "Lucky stitch", ["creature.folk.halfling"], ["item.garment", "item.jewelry"], "move",
    T((1, [L(1, ["verb.evade"], [], "getting clear of a hazard, a fall or an area effect", "protective")])), "A Protective lever on Evade to get clear of a hazard, a fall or an area effect.")
sig("sig_war_cry", "War-cry", ["creature.folk.orc"], WEAP + ["item.armor"], "strike",
    [{"tier": t, "trigger": {"hook": "on_defeat"}, "effects": [eff("eff.apply_condition", condition="cond.frightened", severity="S1", duration="rounds:2", target="one enemy engaged with you that saw it")], "limits": {"per": "scene_end", "uses": 1 if t < 4 else 2}} for t in (1, 4)],
    "Once per scene (twice from tier 4), when you defeat a foe, one enemy engaged with you that saw it is frightened for 2 rounds.")
sig("sig_dirty_trick", "Dirty trick", ["creature.folk.goblin"], WEAP + ["item.garment.gloves"], "strike",
    T((1, [L(1, ["verb.setup"], [], "a feint, a thrown handful, a trip", "precision")])), "A Precision lever on Setup beats.")
sig("sig_giants_grip", "Giant's grip", ["creature.folk.giant"], ["item.garment.gloves", "item.jewelry", "item.armor"], "strike",
    T((1, [L(1, ["verb.grapple", "verb.force"], [], "seizing, shoving or breaking by strength")])), "A Precision lever on Grapple and Force.")
sig("sig_pack_sense", "Pack sense", ["creature.folk.beastfolk"], ["item.jewelry", "item.garment.headwear"], "sense",
    T((1, [eff("eff.05.waive", event_kind="attackers' Precision lever from flag.flanked against you", applies_when="while equipped")])), "Attackers gain no lever from flanking you.")
sig("sig_bone_ward", "Bone-ward", ["creature.undead.mindless"], WORN, "ward",
    [{"tier": t, "effects": [eff("eff.harm_reduction", amount=RES_AMT[t], harm_tags=["harm.physical.pierce"])]} for t in range(1, 6)], "Reduce piercing harm you take by 1-3 by tier (within the item share).")
sig("sig_hungers_edge", "Hunger's edge", ["creature.undead.ravenous"], WEAP, "strike",
    [{"tier": t, "trigger": {"hook": "on_harm_dealt"}, "effects": [eff("eff.restore", quantity="vitality", units=(1 if t < 4 else 2), target="self")], "limits": {"per": "scene_end", "uses": 1}, "when": "the harm was dealt by this weapon to a living being"} for t in (2, 4)],
    "Once per scene, when this weapon harms a living being, regain 1 Vitality (2 from tier 4).", min_tier=2)
sig("sig_grave_sight", "Grave-sight", ["creature.undead.spectral"], ["item.jewelry", "item.garment.headwear"], "sense",
    T((1, [L(1, ["verb.observe"], [], "the thing sought is a spirit, an unseen being or the trace of a death")])), "A Precision lever on Observe for spirits, unseen beings and the traces of death.")
sig("sig_crown_of_dread", "Crown of dread", ["creature.undead.sovereign"], ["item.jewelry", "item.garment.headwear", "item.armor"], "ward",
    T((1, [eff("eff.defense_edge", amount=1, attribute="resolve", applies_when="against fear")]), (4, [eff("eff.condition_immunity", forbid={"conditions": ["cond.frightened"]}, target="self")])), "+1 Resolve defense against fear; from tier 4 you cannot be frightened.", share={"edge": 1})
sig("sig_glamour", "Glamour", ["creature.spirit.fey"], ["item.jewelry", "item.garment"], "social",
    T((1, [L(1, ["verb.talk", "verb.sneak"], ["deed.guile.deception", "deed.guile.disguise"], "deceiving or passing as another")])), "A Precision lever on deception and disguise.")
sig("sig_wayfinder", "Wayfinder", ["creature.spirit.place"], ["item.jewelry", "item.tool"], "move",
    T((1, [L(1, ["verb.observe", "verb.recall"], ["deed.wilds.navigation"], "finding the way in the region where the item was taken (a fact on the item)")])), "A Precision lever on navigation in the region where it was taken.")
sig("sig_ancestral_counsel", "Ancestral counsel", ["creature.spirit.ancestor"], ["item.jewelry", "item.goods"], "sense",
    [{"tier": t, "effects": [eff("eff.grant_lever", type="amplifying", for_verbs=["verb.recall"], for_tags=["deed.lore.history"], duration="the next Recall beat", applies_when="you consulted the item at a breather")], "limits": {"per": "rest_long", "uses": 1}} for t in (1,)],
    "Once per long rest, consulted at a breather: an Amplifying lever on your next Recall of history.")
sig("sig_halo", "Halo", ["creature.spirit.celestial"], WORN, "ward",
    T((1, [eff("eff.defense_edge", amount=1, attribute="agility", applies_when="Guard against undead and fiends"), eff("eff.write_fact", subject="the bearer", predicate="emits_light", value="dim to band.close at will")])),
    "+1 Guard against undead and fiends; sheds dim light at will.", share={"edge": 1})
sig("sig_hellfire", "Hellfire", ["creature.fiend.demon"], WEAP, "strike",
    [{"tier": t, "effects": [eff("eff.strike_delivery", priority_rank=14 + t, harm_tags=["harm.fire.flame"], harm_edge=(1 if t >= 3 else 0), duration="permanent", cosmetic_merge=False)]} for t in range(1, 6)],
    "Your Strikes with it deal fire harm (+1 harm from tier 3).", share={"harm_edge": 1})
sig("sig_silver_tongue", "Silver tongue", ["creature.fiend.devil"], ["item.jewelry", "item.garment"], "social",
    T((1, [L(1, ["verb.talk"], ["deed.influence.persuasion", "deed.influence.intrigue"], "bargaining for terms or a promise")])), "A Precision lever on Talk to bargain for terms or a promise.")
sig("sig_iron_will", "Iron will", ["creature.fiend.possessor"], WORN, "ward",
    T((1, [eff("eff.defense_edge", amount=1, attribute="resolve", applies_when="against charm and domination")]), (4, [eff("eff.condition_immunity", forbid={"conditions": ["cond.charmed"]}, target="self")])), "+1 Resolve defense against charm and domination; from tier 4 you cannot be charmed.", share={"edge": 1})
sig("sig_brimstone_hide", "Brimstone hide", ["creature.fiend.hellbeast"], ["item.armor", "item.garment", "item.shield"], "ward",
    [{"tier": t, "effects": [eff("eff.harm_reduction", amount=RES_AMT[t], harm_tags=["harm.fire"])] if t < 4 else [eff("eff.harm_resistance", factor=0.5, harm_tags=["harm.fire"])]} for t in range(1, 6)],
    "Reduce fire harm by 1-2 (tiers 1-3); from tier 4 halve fire harm you take.")
sig("sig_unyielding", "Unyielding", ["creature.construct.golem"], ["item.armor", "item.shield", "item.garment.footwear"], "ward",
    T((1, [eff("eff.defense_edge", amount=1, attribute="might", applies_when="against Grapple and Force")]), (4, [eff("eff.condition_immunity", forbid={"conditions": ["cond.prone", "cond.off_balance"]}, target="self")])), "+1 Might defense against Grapple and Force; from tier 4 you cannot be knocked prone or off balance.", share={"edge": 1})
sig("sig_guardian_weave", "Guardian weave", ["creature.construct.animated"], ["item.armor", "item.shield"], "ward",
    [{"tier": t, "trigger": {"hook": "on_hit_taken"}, "effects": [eff("eff.prevent_hit", limits={"per": "rest_long", "uses": 1}, applies_when="you are Defending (06.1.5)")]} for t in (3,)],
    "Once per long rest, while you are Defending, negate one hit (tier 3+).", min_tier=3)
sig("sig_precise", "Precise mechanism", ["creature.construct.clockwork"], ["item.tool", "item.garment.gloves", "item.weapon.crossbow"], "craft",
    T((1, [eff("eff.check_edge", amount=1, applies_when="beats under deed.guile.thievery, deed.craft.artifice or deed.martial.archery.crossbow")])), "+1 to lockwork, artifice and crossbow beats.", share={"edge": 1})
sig("sig_familiars_eye", "Familiar's eye", ["creature.construct.homunculus"], ["item.jewelry"], "sense",
    [{"tier": t, "effects": [eff("eff.write_fact", subject="the bearer", predicate="may_perceive_through", value="the item, placed and left within band.distant, as an Observe beat (1 action), once per scene")], "limits": {"per": "scene_end", "uses": 1}} for t in (2,)],
    "Once per scene you may Observe as if from where the item lies, if it is within band.distant.", min_tier=2)
for el, nm, h, opp in [("fire", "Ember heart", "harm.fire", None), ("frost", "Rime heart", "harm.frost", None)]:
    sig("sig_" + el + "_heart", nm, ["creature.elemental." + el], WORN, "ward",
        [{"tier": t, "effects": [eff("eff.harm_reduction", amount=RES_AMT[t], harm_tags=[h])] if t < 4 else [eff("eff.harm_resistance", factor=0.5, harm_tags=[h])]} for t in range(1, 6)],
        f"Reduce {h} harm by 1-2 (tiers 1-3); from tier 4 halve it.")
sig("sig_stonefoot", "Stonefoot", ["creature.elemental.earth"], ["item.garment.footwear", "item.armor", "item.jewelry"], "ward",
    T((1, [L(1, ["verb.evade", "verb.exert"], [], "keeping your feet against a shove, a quake or a slide", "protective")]), (3, [eff("eff.condition_immunity", forbid={"conditions": ["cond.off_balance"]}, target="self")])), "A Protective lever to keep your feet; from tier 3 you cannot be put off balance.")
sig("sig_tidewalker", "Tidewalker", ["creature.elemental.water"], ["item.garment", "item.jewelry"], "move",
    T((1, [eff("eff.condition_immunity", forbid={"conditions": ["cond.choking"]}, target="self", applies_when="the source is water")]), (3, [eff("eff.movement_mode", priority_rank=16, mode="swim", duration="while equipped"), eff("eff.condition_immunity", forbid={"conditions": ["cond.choking"]}, target="self", applies_when="the source is water")])), "Water cannot choke you; from tier 3 you move by swim.")
sig("sig_windborne", "Windborne", ["creature.elemental.air"], ["item.garment.cloak", "item.jewelry", "item.garment.footwear"], "move",
    T((1, [eff("eff.hazard_step", steps=-1, harm_tags=["harm.physical.crush"], applies_when="harm from a fall")]), (5, [eff("eff.movement_mode", priority_rank=17, mode="fly", duration="rounds:10 per rest_long")])), "Falls count one rung lower; at tier 5, fly for 10 rounds once per long rest.")
sig("sig_dragonscale", "Dragonscale", ["creature.dragon.great"], ["item.armor", "item.shield"], "ward",
    [{"tier": t, "effects": ([eff("eff.harm_reduction", amount=RES_AMT[t], harm_tags=["the dragon's own harm branch (provenance)"])] if t < 4 else [eff("eff.harm_resistance", factor=0.5, harm_tags=["the dragon's own harm branch (provenance)"])]) + ([eff("eff.condition_immunity", forbid={"conditions": ["cond.frightened"]}, target="self")] if t >= 4 else [])} for t in range(2, 6)],
    "Reduce harm of the dragon's own branch by 2 (tiers 2-3); from tier 4 halve it and you cannot be frightened.", min_tier=2, bound_default=True)
sig("sig_drakefire", "Drake-fire", ["creature.dragon.drake"], WEAP, "strike",
    [{"tier": t, "effects": [eff("eff.strike_delivery", priority_rank=14 + t, harm_tags=["the drake's own harm branch (provenance)"], harm_edge=(1 if t >= 3 else 0), duration="permanent", cosmetic_merge=False)]} for t in range(1, 6)],
    "Your Strikes with it deal the drake's own harm type (+1 harm from tier 3).", share={"harm_edge": 1})
sig("sig_wyvern_sting", "Wyvern sting", ["creature.dragon.wyvern"], WEAP, "strike",
    [{"tier": t, "trigger": {"hook": "on_attack_hit", "chance": "natural " + CHANCE[min(5, t + 1)]}, "effects": [eff("eff.apply_condition", condition="cond.poisoned", severity=("S2" if t >= 3 else "S1"), duration="scene", target="the creature hit")]} for t in range(1, 6)],
    "On a hit whose d20 shows the natural range one wider than the tier's, apply cond.poisoned.")
sig("sig_coils", "Coils", ["creature.dragon.serpentine"], ["item.garment.gloves", "item.jewelry", "item.weapon.thrown.net"], "strike",
    T((1, [L(1, ["verb.grapple"], [], "seizing or holding", "amplifying")])), "An Amplifying lever on Grapple.")
sig("sig_alien_ward", "Alien ward", ["creature.horror.aberration"], WORN, "ward",
    [{"tier": t, "effects": [eff("eff.harm_reduction", amount=RES_AMT[t], harm_tags=["harm.mind"])]} for t in range(1, 6)], "Reduce mind harm you take by 1-3 by tier.")
sig("sig_acid_bite", "Acid bite", ["creature.horror.ooze"], WEAP, "strike",
    [{"tier": t, "effects": [eff("eff.strike_delivery", priority_rank=14 + t, harm_tags=["harm.corrosion.acid"], harm_edge=(1 if t >= 3 else 0), duration="permanent", cosmetic_merge=False)]} for t in range(1, 6)],
    "Your Strikes with it deal acid harm (+1 harm from tier 3).", share={"harm_edge": 1})
sig("sig_spore_ward", "Spore ward", ["creature.horror.fungal"], WORN, "ward",
    [{"tier": t, "effects": [eff("eff.harm_reduction", amount=RES_AMT[t], harm_tags=["harm.venom"])] + ([eff("eff.condition_immunity", forbid={"conditions": ["cond.poisoned"]}, target="self")] if t >= 4 else [])} for t in range(1, 6)],
    "Reduce venom harm by 1-3 by tier; from tier 4 you cannot be poisoned.")
sig("sig_thornward", "Thornward", ["creature.horror.plant"], ["item.armor", "item.shield", "item.garment"], "ward",
    [{"tier": t, "trigger": {"hook": "on_hit_taken", "chance": "natural " + CHANCE[t]}, "effects": [eff("eff.deal_harm", severity="S1", harm_tags=["harm.physical.pierce"], target="the attacker, if it struck in melee")]} for t in range(1, 6)],
    "When a melee attack hits you and its d20 shows the tier's natural range, the attacker takes S1 piercing harm.")
sig("sig_dread_aspect", "Dread aspect", ["creature.horror.abomination"], ["item.armor", "item.garment.headwear", "item.jewelry"], "social",
    T((1, [L(1, ["verb.talk"], ["deed.influence.intimidation"], "intimidating by appearance")]), (3, [L(3, ["verb.talk"], ["deed.influence.intimidation"], "intimidating by appearance", "amplifying"), L(3, ["verb.talk"], ["deed.influence.intimidation"], "intimidating by appearance")])), "A Precision lever on Talk to intimidate (from tier 3 also Amplifying).")

# ---------- place signatures (a site's treasure: source = the place)
for pid, nm, gate, kinds, bias, tiers, text in [
    ("sig_tomb_ward", "Tomb-ward", ["terrain.ruin.tomb", "terrain.ruin.temple"], WORN, "ward",
     [{"tier": t, "effects": [eff("eff.harm_reduction", amount=RES_AMT[t], harm_tags=["harm.blight"])]} for t in range(1, 6)], "Reduce blight harm by 1-3 by tier."),
    ("sig_snowshod", "Snowshod", ["terrain.frozen", "creature.elemental.frost"], ["item.garment.footwear"], "move",
     T((1, [eff("eff.05.waive", event_kind="snow, ice and drift snags on Move, Exert and travel pace (10)", applies_when="while worn")])), "Snow and ice impose no snag on your Move, Exert or travel."),
    ("sig_marsh_strider", "Marsh-strider", ["terrain.wetland"], ["item.garment.footwear"], "move",
     T((1, [eff("eff.05.waive", event_kind="bog, mud and shallow-water snags on Move, Exert and travel pace (10)", applies_when="while worn")])), "Bog and mud impose no snag on your Move, Exert or travel."),
    ("sig_sand_veil", "Sand-veil", ["terrain.arid"], ["item.garment.cloak", "item.garment.headwear"], "ward",
     T((1, [eff("eff.hazard_step", steps=-1, harm_tags=["harm.fire.heat", "harm.physical.asphyxia"], applies_when="hazard")])), "Heat and sandstorm hazards count one rung lower."),
    ("sig_forest_hush", "Forest-hush", ["terrain.forest"], ["item.garment.cloak", "item.garment.footwear"], "move",
     T((1, [L(1, ["verb.sneak"], [], "in woodland or undergrowth")])), "A Precision lever on Sneak in woodland."),
    ("sig_deep_sight", "Deep-sight", ["terrain.underground"], ["item.jewelry", "item.garment.headwear"], "sense",
     T((1, [L(1, ["verb.observe"], ["deed.wilds.navigation"], "finding the way or the danger underground")])), "A Precision lever on Observe underground to find the way or the danger."),
    ("sig_tidecaller", "Tidecaller", ["terrain.water.sea", "terrain.water.coast"], ["item.jewelry", "item.tool"], "move",
     T((1, [L(1, ["verb.observe", "verb.recall"], ["deed.wilds.seafaring"], "reading weather, tide and current at sea")])), "A Precision lever on seafaring reads of weather, tide and current."),
    ("sig_ruin_lore", "Ruin-lore", ["terrain.ruin"], ["item.jewelry", "item.goods"], "sense",
     T((1, [L(1, ["verb.observe", "verb.recall"], ["deed.lore.history", "deed.lore.engineering"], "inside a ruin: finding its ways, its traps and its story")])), "A Precision lever on Observe and Recall inside ruins."),
    ("sig_road_luck", "Road-luck", ["terrain.road", "terrain.settlement"], ["item.jewelry", "item.garment.footwear"], "move",
     T((1, [L(1, ["verb.talk"], ["deed.influence.trade"], "bargaining for passage, lodging or a ride on the road")])), "A Precision lever on Talk to bargain for passage or lodging."),
]:
    sig(pid, nm, gate, kinds, bias, tiers, text, place=True)

# ---------- flaws (Flawed degree effect for crafting; cursed loot)
FLAWS = [
 dict(id="flaw.heavy", name="Heavy", effects=[eff("eff.08.adjust", quantity="carry", amount=-1, applies_when="while carried")], text="Carrying capacity -1 while carried.", applies_to=ANY),
 dict(id="flaw.loud", name="Loud", effects=[eff("eff.06.grant_snag", type="precision", sign="snag", to="the bearer", fact="loud_gear.<item>", applies_when="Sneak while it is carried", duration="while carried")], text="A Precision snag on Sneak while carried.", applies_to=ANY),
 dict(id="flaw.brittle", name="Brittle", effects=[eff("eff.08.cost_step", ladder="severity", steps=1, applies_when="cost.gear targets this item")], text="A cost.gear against it is taken one rung heavier.", applies_to=ANY),
 dict(id="flaw.marked", name="Marked", effects=[eff("eff.write_fact", subject="the item", predicate="recognizable_as", value="its source's or former owner's (a fact others may cite)")], text="It is recognizable as what it was or whose it was; others may cite that fact.", applies_to=ANY),
 dict(id="flaw.thirsty", name="Thirsty", effects=[eff("eff.08.adjust", quantity="supply_use", amount=1, applies_when="each day it is attuned")], text="While attuned, your daily supply use is 1 higher.", applies_to=ANY, magical_only=True),
 dict(id="flaw.cold_to_kin", name="Unwelcome", effects=[eff("eff.06.grant_snag", type="precision", sign="snag", to="the bearer", fact="unwelcome.<item>", applies_when="Talk with the item's source kind (its creature tag) while it is seen", duration="while equipped")], text="A Precision snag on Talk with the source's kind while it is seen.", applies_to=ANY),
 dict(id="flaw.binding", name="Binding", effects=[eff("eff.write_fact", subject="the item", predicate="cannot_unattune", value="until cleansed (eff.05.end_working or a rite that removes curses)")], text="Once attuned it cannot be unattuned until cleansed.", applies_to=ANY, magical_only=True, sources=["creature.fiend", "creature.undead", "creature.horror"]),
 dict(id="flaw.restless", name="Restless", effects=[eff("eff.07.rest_cap", cap="partial", applies_when="a rest_long while it is attuned")], text="While attuned, your long rests are at best partial.", applies_to=ANY, magical_only=True, sources=["creature.spirit", "creature.undead.spectral"]),
]
for fl in FLAWS:
    fl["lifecycle"] = "provisional"; fl["basis"] = ["00.11.3 step 5", "08.6.6", "T-08-12"]
    for e in fl["effects"]:
        chk_eff(e["effect_id"], fl["id"])

# ---------- I-019: a water-gated tier-1 property (the water elemental's tier-1 pool had 2 entries) [revision: I-019]
prop("tidesense", "Tide-sense", "passive", "lever", ["creature.elemental.water", "creature.beast.aquatic", "terrain.water"], "tides", 2,
     T((1, [eff("eff.grant_lever", type="precision", for_verbs=["verb.observe", "verb.move"], for_tags=[], duration="while equipped", applies_when="in, on or under water: reading a current, a depth, or what moves beneath")])),
     ["item.jewelry", "item.garment.footwear"], "sense",
     "A Precision lever on Observe and Move in, on or under water: currents, depths, and what moves beneath.", place=True)

# ---------- I-017: wider gates, so that no source that yields loot repeats its magnitude property in more than 15% of
# consecutive decisive drops (08-loot-sim.py, every archetype of data/archetypes.yaml at every band). Each addition is a
# kind of creature the property's own fiction already fits (a wolf-pelt cloak is warm; acid eats the armor it strikes).
# [revision: I-017]
EXTRA_GATES = {
 "warm":          ["creature.beast.predator.canine", "creature.beast.predator.feline", "creature.beast.aquatic", "creature.beast.herd", "creature.beast.monstrous", "creature.elemental.fire"],
 "cool":          ["creature.elemental.water", "creature.elemental.air"],
 "sturdy":        ["creature.elemental.earth", "creature.elemental.frost", "creature.fiend", "creature.dragon", "creature.beast.herd", "creature.undead.mindless"],
 "keen":          ["creature.fiend.demon", "creature.dragon", "creature.horror.ooze"],
 "light_make":    ["creature.construct.clockwork"],
 "masters_mark":  ["creature.construct.clockwork"],
 "guarding":      ["creature.beast.monstrous", "creature.beast.herd"],
 "reinforced":    ["creature.beast.reptile", "creature.beast.herd"],
 "supple":        ["creature.beast.reptile"],
 "quiet":         ["creature.beast.reptile"],
 "wayfinder":     ["creature.elemental.water", "creature.construct.clockwork"],
 "minstrels":     ["creature.construct.clockwork"],
 "stalkers":      ["creature.beast.aquatic.shark", "creature.beast.predator.canine", "creature.beast.monstrous"],
 "tracker":       ["creature.beast.monstrous"],
 "survivor":      ["creature.horror.plant"],
 "climbers":      ["creature.horror.plant"],
 "craft_alchemy": ["creature.horror.plant"],
 "craft_textiles": ["creature.horror.plant"],
 "physicks":      ["creature.horror.plant"],
 "lorekeepers":   ["creature.elemental.earth", "creature.elemental.frost"],
 "piercing_eye":  ["creature.beast.avian.raptor"],
 "commanding":    ["creature.beast.avian.raptor"],
 "dread":         ["creature.beast.monstrous", "creature.elemental.fire", "creature.folk.beastfolk.gnoll", "creature.folk.giant.troll", "creature.fiend.hellbeast", "org.order.knightly"],
 "darksight":     ["creature.beast.avian", "creature.elemental.earth", "creature.horror.fungal", "creature.horror.abomination", "creature.construct.homunculus", "creature.folk.beastfolk.gnoll", "creature.folk.giant.troll"],
 "keen_ears":     ["creature.beast.avian", "creature.beast.herd", "creature.beast.monstrous", "creature.elemental.air", "creature.folk.beastfolk.lizardfolk"],
 "scent":         ["creature.beast.aquatic.shark", "creature.folk.giant", "creature.fiend.hellbeast"],
 "spirit_sight":  ["creature.elemental", "creature.construct.homunculus"],
 "mind_guard":    ["creature.horror.abomination", "creature.undead.mindless"],
 "tremor":        ["creature.horror.fungal"],
 "featherfall":   ["creature.beast.predator.feline"],
 "glowing":       ["creature.elemental.frost", "creature.construct.clockwork"],
 "pack_mule":     ["creature.elemental.earth"],
 "waybread":      ["creature.horror.fungal"],
 "knitting":      ["creature.horror.abomination"],
 "resist_cut":    ["creature.beast.aquatic", "creature.elemental.earth", "creature.horror.abomination", "creature.folk.beastfolk.lizardfolk", "org.order.knightly"],
 "resist_pierce": ["creature.elemental.earth", "creature.undead.mindless"],
 "resist_crush":  ["creature.elemental.water", "creature.horror.plant", "creature.horror.abomination", "creature.beast.herd", "creature.folk.dwarf"],
 "resist_fire":   ["creature.elemental.water"],
 "hazard_frost":  ["creature.elemental.water", "creature.beast.aquatic"],
 "resist_storm":  ["creature.beast.avian"],
 "hazard_storm":  ["creature.beast.avian"],
 "resist_venom":  ["creature.construct.homunculus", "creature.folk.beastfolk.lizardfolk"],
 "hazard_venom":  ["creature.construct.homunculus", "creature.folk.beastfolk.lizardfolk"],
 "resist_blight": ["creature.horror.fungal", "creature.horror.abomination"],
 "hazard_blight": ["creature.horror.fungal", "creature.horror.abomination"],
 "resist_arcane": ["creature.beast.monstrous.magical"],
 "hazard_arcane": ["creature.beast.monstrous.magical"],
 "onhit_bleed":   ["creature.fiend.demon", "creature.dragon"],
 "onhit_dread":   ["creature.dragon"],
 "onhit_stagger": ["creature.fiend.demon", "org.order.knightly"],
 "hazard_mind":   ["creature.horror.fungal"],
 "fine_cut":      ["creature.beast.predator.feline"],
 "onhit_expose":  ["creature.horror.ooze", "deed.guile.ambush"],
 "bane_construct": ["creature.horror.ooze"],
 "lore_whispers": ["creature.undead.mindless"],
 "onhit_venom":   ["creature.folk.beastfolk.lizardfolk"],
 "strike_venom":  ["creature.folk.beastfolk.lizardfolk"],
 "bane_undead":   ["org.order.knightly"],
}
_byid = {p["id"]: p for p in PROPS}
for k, tags in EXTRA_GATES.items():
    pp = _byid["prop." + k]
    for t in tags:
        chk_tag(t, "EXTRA_GATES " + k)
        if t in pp["gate_tags"]:
            DEFECTS.append("EXTRA_GATES %s: %s already gated" % (k, t))
        pp["gate_tags"] = pp["gate_tags"] + [t]   # a new list: family members share their gate list objects

SIG_GROUPS = {'sig_wyvern_sting': 'on_hit', 'sig_thornward': 'retort', 'sig_hellfire': 'strike_form', 'sig_drakefire': 'strike_form', 'sig_acid_bite': 'strike_form', 'sig_fire_heart': 'resist_fire', 'sig_frost_heart': 'resist_frost', 'sig_brimstone_hide': 'resist_fire', 'sig_bone_ward': 'resist_physical', 'sig_alien_ward': 'resist_mind', 'sig_spore_ward': 'resist_venom', 'sig_plague_proof': 'resist_blight', 'sig_monster_hide': 'armor_red'}
for p in PROPS:
    k = p['id'].split('.',1)[1]
    if k in SIG_GROUPS:
        p['mod_group'] = SIG_GROUPS[k]
for p in PROPS:
    if p['id'] in ('prop.sig_fire_heart','prop.sig_frost_heart'):
        p['mod_group'] = 'resist_' + p['id'].split('_')[1]
# ---------- validate properties
pid = [p["id"] for p in PROPS]
assert len(pid) == len(set(pid)), "duplicate prop id"
for p in PROPS:
    for t in p["gate_tags"] + p["excluded_tags"] + p["base_kinds"]:
        chk_tag(t, p["id"])
    for tr in p["tiers"]:
        for e in tr["effects"]:
            chk_eff(e["effect_id"], p["id"])
            c = e["params"].get("condition")
            if c and c not in CONDS:
                DEFECTS.append(f"unknown condition {c} in {p['id']}")
            for c in (e["params"].get("forbid") or {}).get("conditions", []):
                if c not in CONDS:
                    DEFECTS.append(f"unknown condition {c} in {p['id']}")
    if min(t["tier"] for t in p["tiers"]) != p["min_tier"]:
        DEFECTS.append(f"{p['id']}: min_tier {p['min_tier']} != lowest authored tier")
# coverage: every level-2 creature tag has at least one signature_eligible entry whose gate matches it
def matches(gate, src):
    return src == gate or src.startswith(gate + ".")
CRE2 = [t for t, v in TAGS.items() if t.startswith("creature.") and v.get("level") == 2]
DEFAULT_SIG = {}
for c in sorted(CRE2):
    cands = [p for p in PROPS if p["signature_eligible"] and not p.get("place_gated") and p["kind"] != "item_ability" and any(matches(g, c) for g in p["gate_tags"])]
    if not cands:
        DEFECTS.append(f"no signature for {c}")
        continue
    # most specific gate wins; then authored order
    pref = [p for p in cands if p["id"].startswith("prop.sig_")] or [p for p in cands if not p.get("relic") and p["family"] != "focus_cost"] or cands
    best = max(pref, key=lambda p: (max(g.count(".") for g in p["gate_tags"] if matches(g, c)), -PROPS.index(p)))
    DEFAULT_SIG[c] = best["id"]

# ================================================================== MATERIALS
MATS = []
def mat(id, name, mtags, src, gates, price, band, harvest_dc=None, load=1, sig=None, flaws=None, **kw):
    e = dict(id="mat." + id, name=name, tags=mtags, material_tags=mtags, source_tags=src, gates=gates, price=price,
             rarity_band=band, harvest={"verb": "verb.handle", "deed_tag": "deed.wilds.foraging.harvest", "dc_tier": harvest_dc or ["easy", "easy", "moderate", "hard", "very_hard", "legendary"][band],
                                         "time": "intervals:1" if load <= 1 else "hours:1"} if src else None,
             weight=load, lifecycle="provisional", basis=kw.pop("basis", ["08.6.2", "T-08-13"]))
    if sig:
        e["signature_property"] = sig
    if flaws:
        e["flaws"] = flaws
    e.update(kw)
    MATS.append(e)
    return e
# mundane stock (bought; rarity band 0 = common market goods)
for mid, nm, t, pr in [("iron", "Iron stock", "material.metal.iron", 2), ("steel", "Steel stock", "material.metal.steel", 5), ("copper", "Copper and bronze", "material.metal.copper", 3),
                        ("silver", "Silver", "material.metal.silver", 20), ("gold", "Gold", "material.metal.gold", 100), ("timber", "Timber", "material.wood.timber", 1),
                        ("fine_wood", "Fine wood", "material.wood.fine", 4), ("yew", "Yew stave", "material.wood.fine.yew", 6), ("common_stone", "Building stone", "material.stone.common", 1),
                        ("fine_stone", "Marble", "material.stone.fine", 10), ("leather", "Tanned leather", "material.hide.leather", 2), ("cloth", "Cloth", "material.fiber.cloth", 1),
                        ("silk", "Silk", "material.fiber.silk", 15), ("cordage", "Cordage", "material.fiber.cordage", 1), ("herbs", "Common herbs", "material.botanical.herb", 1),
                        ("resin", "Resin and pitch", "material.botanical.resin", 1), ("bone", "Bone", "material.bone.bone", 1), ("semiprecious", "Semiprecious stones", "material.gem.semiprecious", 10)]:
    mat(mid, nm, [t], [], [t], pr, 0, sig=None, stock=True)
MATS[-1]["rarity_band"] = 1
# special stock (rarity band 1-3, bought only in towns/cities or found)
for mid, nm, t, pr, band, extra in [("cold_iron", "Cold iron", "material.metal.iron.cold", 25, 2, ["material.metal.iron.cold"]),
                                     ("pure_silver", "Pure silver", "material.metal.silver.pure", 60, 2, ["material.metal.silver.pure"]),
                                     ("ironwood", "Ironwood", "material.wood.fine.ironwood", 30, 2, ["material.wood.fine.ironwood"]),
                                     ("witchwood", "Witchwood", "material.wood.witchwood", 40, 2, ["material.wood.witchwood", "deed.arcane"]),
                                     ("volcanic_glass", "Volcanic glass", "material.stone.volcanic", 8, 1, ["material.stone.volcanic", "harm.fire"]),
                                     ("crystal", "Spell-crystal", "material.gem.crystal", 50, 3, ["material.gem.crystal", "harm.arcane"]),
                                     ("precious_gem", "Precious gem (for setting)", "material.gem.precious", 100, 3, ["material.gem.precious"]),
                                     ("rare_metal", "Rare metal (the setting names it)", "material.metal.rare", 200, 4, ["material.metal.rare"]),
                                     ("healing_herbs", "Healing herbs", "material.botanical.herb.healing", 3, 1, ["material.botanical.herb.healing"]),
                                     ("toxic_herbs", "Toxic herbs", "material.botanical.herb.toxic", 4, 1, ["material.botanical.herb.toxic", "harm.venom"]),
                                     ("arcane_herbs", "Reagent herbs", "material.botanical.herb.arcane", 6, 1, ["material.botanical.herb.arcane", "deed.arcane"]),
                                     ("fungus", "Cave fungus", "material.botanical.fungus", 2, 1, ["material.botanical.fungus", "terrain.underground"])]:
    mat(mid, nm, [t], [], extra, pr, band, stock=True)
# creature parts (harvested): gates = the source's tags; rarity band follows the source band at harvest
PARTS = [
 ("pelt", "Pelt", "material.hide.fur", ["creature.beast.predator", "creature.beast.herd", "creature.beast.monstrous"], 2, 1, 2),
 ("winter_pelt", "Winter pelt", "material.hide.fur.winter", ["creature.beast.predator.ursine", "creature.elemental.frost"], 6, 1, 2),
 ("hide", "Hide", "material.hide.leather", ["creature.beast.herd", "creature.beast.reptile.crocodilian", "creature.folk.giant.troll"], 2, 1, 2),
 ("scales", "Scales", "material.hide.scale", ["creature.beast.reptile", "creature.dragon", "creature.folk.beastfolk.lizardfolk"], 4, 1, 2),
 ("dragon_scale", "Dragon scale", "material.hide.scale.dragon", ["creature.dragon"], 120, 3, 2),
 ("chitin", "Chitin plates", "material.hide.chitin", ["creature.beast.vermin.insect", "creature.beast.vermin.arachnid", "creature.horror.aberration"], 4, 1, 2),
 ("fangs", "Fangs and claws", "material.bone.fang", ["creature.beast.predator", "creature.beast.monstrous", "creature.dragon", "creature.undead.ravenous", "creature.fiend.hellbeast"], 2, 1, 0),
 ("horn", "Horn and antler", "material.bone.horn", ["creature.beast.herd", "creature.fiend.demon", "creature.beast.monstrous"], 3, 1, 1),
 ("ivory", "Tusk ivory", "material.bone.ivory", ["creature.beast.herd.swine", "creature.folk.giant", "creature.beast.monstrous.dire"], 15, 2, 1),
 ("bones", "Bones", "material.bone.bone", ["creature.beast", "creature.undead.mindless", "creature.folk"], 1, 1, 1),
 ("silk_gland", "Spinner's silk", "material.fiber.silk", ["creature.beast.vermin.arachnid"], 15, 2, 0),
 ("sinew", "Sinew", "material.fiber.cordage", ["creature.beast", "creature.dragon"], 1, 1, 0),
 ("venom_sac", "Venom sac", "material.essence.gland.venom", ["creature.beast.reptile.serpent", "creature.beast.vermin", "creature.dragon.wyvern", "creature.horror.fungal"], 10, 2, 0),
 ("fire_gland", "Fire gland", "material.essence.gland.fire", ["creature.elemental.fire", "creature.dragon", "creature.fiend.hellbeast"], 25, 2, 0),
 ("gland", "Strange gland", "material.essence.gland", ["creature.horror", "creature.beast.monstrous.magical"], 15, 2, 0),
 ("beast_heart", "Beast heart", "material.essence.heart.beast", ["creature.beast.monstrous", "creature.beast.predator", "creature.folk.giant"], 20, 2, 1),
 ("elemental_core", "Elemental core", "material.essence.heart.elemental", ["creature.elemental", "creature.construct.golem"], 60, 3, 1),
 ("heart", "Heart of power", "material.essence.heart", ["creature.dragon", "creature.fiend", "creature.spirit.celestial", "creature.undead.sovereign"], 150, 3, 1),
 ("blood", "Potent blood", "material.essence.blood", ["creature.dragon", "creature.fiend", "creature.undead.ravenous.vampire", "creature.beast.monstrous.magical"], 30, 2, 0),
 ("ichor", "Ichor", "material.essence.ichor", ["creature.horror", "creature.fiend.demon"], 20, 2, 0),
 ("ectoplasm", "Ectoplasm", "material.essence.residue.ectoplasm", ["creature.undead.spectral", "creature.spirit"], 25, 2, 0),
 ("grave_dust", "Grave dust", "material.essence.residue.grave_dust", ["creature.undead.mindless", "creature.undead.ravenous", "creature.undead.sovereign"], 10, 1, 0),
 ("residue", "Spirit residue", "material.essence.residue", ["creature.spirit.fey", "creature.spirit.place", "creature.spirit.ancestor"], 20, 2, 0),
 ("golem_clay", "Animate clay or stone", "material.stone.common", ["creature.construct.golem.clay", "creature.construct.golem.stone", "creature.elemental.earth"], 5, 1, 3),
 ("clockwork", "Clockwork parts", "material.metal.copper", ["creature.construct.clockwork", "creature.construct.animated"], 15, 2, 1),
 ("living_wood", "Living wood", "material.wood.witchwood", ["creature.horror.plant.treant", "creature.spirit.place"], 40, 2, 3),
 ("spore_cap", "Spore cap", "material.botanical.fungus", ["creature.horror.fungal"], 8, 1, 0),
 ("feathers", "Feathers", "material.fiber.cordage", ["creature.beast.avian"], 2, 1, 0),
]
for mid, nm, mt, src, pr, band, ld in PARTS:
    mat(mid, nm, [mt], src, sorted(set(src + [mt])), pr, band, load=ld)
mat("residuum", "Residuum (salvaged essence)", ["material.essence.residue"], [], ["material.essence.residue"], 0, 1, stock=False,
    instance_rule="salvage (08.6.8) writes the instance's gates = the salvaged signature property's gate_tags and its rarity band = that signature's tier - 1 (minimum 1); price = the signature's tier value / 2 (00.3.4's halving)",
    basis=["08.6.8", "R3 A-10 (Diablo IV Codex of Power)"])
MATS[-1]["harvest"] = None
for m in MATS:
    for t in m["tags"] + m["source_tags"] + m["gates"]:
        chk_tag(t, m["id"])
    # default signature for a crafted item: the deepest-matching signature_eligible property of its gates
    if not m.get("stock"):
        cands = [p for p in PROPS if p["signature_eligible"] and p["kind"] != "item_ability" and not p.get("place_gated") and any(matches(g, s) for g in p["gate_tags"] for s in m["gates"])]
        cands = [p for p in cands if p["id"].startswith("prop.sig_")] or [p for p in cands if not p.get("relic") and p["family"] != "focus_cost"] or cands
        if cands:
            best = max(cands, key=lambda p: (max(g.count(".") for g in p["gate_tags"] for s in m["gates"] if matches(g, s)), -PROPS.index(p)))
            m["fallback_signature"] = best["id"]
    m["gated_pool_size"] = sum(1 for p in PROPS if "craft" in p["domains"] and any(matches(g, s) for g in p["gate_tags"] for s in m["gates"] + ["creature.folk"]))
    if m["gated_pool_size"] < 2 and not m.get("stock") and m["id"] != "mat.residuum":
        DEFECTS.append(f"{m['id']} gates only {m['gated_pool_size']} properties")

# ================================================================== write
if DEFECTS:
    print("DEFECTS:"); [print(" ", d) for d in DEFECTS]; sys.exit(1)

def dump(name, header, data):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(header.strip() + "\n\n")
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=200, default_flow_style=None)
    print("wrote", name, os.path.getsize(os.path.join(OUT, name)))

HDR = lambda fname, purpose, extra="": f"""# data/{fname}
# Purpose: {purpose}
# Owner: 08-items-loot-crafting (T-00-19). Schema: data/SCHEMAS.md#{fname.replace('.', '')} plus the optional fields
#   documented in chapter 08's Tables section (T-08-1).
{extra}# GENERATED by rules/_process/simulation/08-gen_data08.py (validated against tags.yaml, effects.yaml + contrib,
#   conditions.yaml, licenses.yaml + contrib, abilities.yaml and gen_absorb.yaml). Edit the script, not this file.
# Every entry lifecycle: provisional (00.16.3)."""

import builtins
builtins.BI, builtins.PROPS, builtins.MATS, builtins.FLAWS, builtins.DEFAULT_SIG, builtins.KIT_RES = BI, PROPS, MATS, FLAWS, DEFAULT_SIG, KIT_RES
builtins.NEW_TAGS, builtins.NEW_EFFECTS, builtins.TAGS, builtins.ABIL, builtins.ABSORB, builtins.CONDS = NEW_TAGS, NEW_EFFECTS, TAGS, ABIL, ABSORB, CONDS
builtins.dump, builtins.HDR, builtins.eff, builtins.chk_tag, builtins.matches = dump, HDR, eff, chk_tag, matches

if __name__ == "__main__":
    exec(open(os.path.join(os.path.dirname(__file__), "08-gen_data08_part2.py"), encoding="utf-8").read())
