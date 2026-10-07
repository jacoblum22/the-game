# draws02.py -- performs the gen.birth draws used in the chapter's worked examples, from the SHIPPED gen_birth.yaml
import os as _os
_RULES = _os.environ.get('GAME_RULES', _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..')))
import yaml, random
B = yaml.safe_load(open(_os.path.join(_RULES, 'data', 'gen_birth.yaml'), encoding="utf-8"))
POOL = B["pool"]
def matches(gate, src):  # 00.5.4c: G equals S or G is an ancestor of S
    return any(s == g or s.startswith(g + ".") for g in gate for s in src)
def carries(entry, bias): return any(t == bias or t.startswith(bias + ".") for t in entry["tags"])
def draw(layer, src, bias, rng, exclude=()):
    cands = [e for e in POOL if e["layer"] == layer and matches(e["gate_tags"], src) and e["id"] not in exclude]
    w = [e["weight"] * (3 if bias and carries(e, bias) else 1) for e in cands]
    tot = sum(w); r = rng.randint(1, tot); acc = 0
    for e, x in zip(cands, w):
        acc += x
        if r <= acc: return e, len(cands), tot, r, (acc - x + 1, acc)
def creation(name, src, circ, seed):
    rng = random.Random(seed)
    bias = {f["circumstance"]: f.get("bias_tag") for f in B["fill_map"]}[circ]
    print("\n%s | source tags %s | circumstance %s (bias %s)" % (name, src, circ, bias))
    for layer in (["gift"] if circ == "gifted" else []) + ["knack", "quirk"]:
        e, n, tot, r, band = draw(layer, src, bias, rng)
        print("  %-5s pool %2d entries, total weight %3d, roll %3d in band %s -> %s (%s)" % (layer, n, tot, r, band, e["id"], e["text"]))
creation("Wren", ["creature.folk.human", "deed.wilds", "deed.martial", "terrain.forest", "terrain.highland"], "unremarked", 2001)
creation("Bram", ["creature.folk.human", "deed.wilds", "deed.influence", "terrain.road", "terrain.settlement.camp", "deed.martial"], "unremarked", 2002)
creation("Thessaly", ["creature.folk.goblin", "deed.guile", "deed.lore", "deed.craft", "terrain.settlement.hold", "terrain.ruin.temple", "deed.divine"], "hard", 2003)
creation("Odo (boundary: same choices as Wren)", ["creature.folk.human", "deed.wilds", "deed.martial", "terrain.forest", "terrain.highland"], "unremarked", 2004)
creation("A Touched child, school named (elements)", ["creature.folk.human", "deed.craft", "deed.wilds", "deed.primal", "deed.guile", "deed.primal.elements"], "gifted", 2005)
creation("A Touched child, school left to birth", ["creature.folk.human", "deed.craft", "deed.wilds", "deed.primal", "deed.guile"] + ["deed.primal." + s for s in ("growth","beastkin","weather","shapeshifting","spirits","elements","hexcraft")], "gifted", 2006)
# Bent draws for Wren: branches with >= 3 resolved frames: martial, wilds; Agility is +3 (excluded)
rng = random.Random(3001)
print("\nWren's Bent, source tags [deed.martial, deed.wilds], Agility +3 excluded")
excl = {"birth.bent.agility"}
for n in range(3):
    e, cnt, tot, r, band = draw("bent", ["deed.martial", "deed.wilds"], None, rng, excl)
    print("  draw %d: pool %d (%s), roll %d of %d -> %s" % (n + 1, cnt, ", ".join(x["attribute"] for x in POOL if x["layer"]=="bent" and matches(x["gate_tags"], ["deed.martial","deed.wilds"]) and x["id"] not in excl), r, tot, e["attribute"]))
    excl.add(e["id"])
