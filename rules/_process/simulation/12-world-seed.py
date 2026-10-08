"""12-world-seed.py -- I-028: the world seed (12.16) run end to end from data, and checked against everything the
rules read from a region.

  python 12-world-seed.py                      # seed 1 in oracle mode, a guided run, and 200 seeds; report to stdout
  python 12-world-seed.py --emit FILE          # also write seed 1 (oracle mode) as a region file
  python 12-world-seed.py --seed N             # report on one seed only
  python 12-world-seed.py --answers FILE       # guided mode: answers {question_id: option_id} (others oracle)

Every step reads `data/world_seed.yaml` and the files it names (archetypes, origins, factions, world_turn, sites,
travel, oracles, companions, rituals, licenses, calendar, weather, tags). Randomness is one RC-RNG stream per
seed (random.Random(seed)), drawn in step order, so a seed number reproduces its world byte for byte.
The checks (12.16.17) are `world_seed.yaml#requirements`; the encounter tables are built by PR-10-10
(`10_table_builder.py`) and audited by PR-10-8 (`10-word-audit.py`), both imported, not copied.
[revision: R2-D] After build_seed, `seed_packs` adds the seed packs (12.16.9 looks, furniture and exits; 12.16.11
knowledge packs and stances; 12.16.16 documents and the incident's reduced case, PR-15-6) on streams keyed by the
seed and the entity id, so build_seed's own record is unchanged; `check_packs` runs `world_seed.yaml#pack_requirements`.
Output: 12-world-seed-output.txt (stdout); 12-world-seed-example.yaml (--emit). Exit 1 on any failed check.
"""
import os, sys, random, re, json, copy, itertools, importlib.util
from collections import Counter, OrderedDict
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.normpath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(R, "data")

def load(name):
    return yaml.safe_load(open(os.path.join(DATA, name), encoding="utf-8"))

_spec = importlib.util.spec_from_file_location("tb10", os.path.join(HERE, "10_table_builder.py"))
TB = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(TB)
WA = TB.WA

WS = load("world_seed.yaml")
TAB = {t["id"]: t for t in WS["tables"]}
QS = {q["id"]: q for q in WS["questions"]}
DEF = WS["defaults"]
ARCHD = {a["id"]: a for a in load("archetypes.yaml")["archetypes"]}
ORIG = load("origins.yaml")
ORIGD = {o["id"]: o for o in ORIG["origins"]}
ORIGD.update({e["id"]: e for b in ORIG.get("blocks") or [] for e in b.get("entries") or []})   # setting origins (02.4.8)
TAGS = {t["id"] for t in load("tags.yaml")["tags"]}
FAC = load("factions.yaml")
TPL = {t["id"]: t for t in FAC["templates"]}
WT = load("world_turn.yaml")
SITT = {s["id"]: s for s in WT["situation_templates"]}
SITES = load("sites.yaml")
THEMES = {t["id"]: t for t in SITES["site_themes"]}
DOMAINS = {d["id"]: d for d in SITES["site_domains"]}
POOLS = {(p["theme"], p["domain"]): p for p in SITES["denizen_pools"]}
TRAVEL = load("travel.yaml")
TERRAIN_DEF = TRAVEL["terrain_defaults"]
GENERIC_ENC = {t["terrain"]: t for t in TRAVEL["encounter_tables"]}
ORAC = {t["id"]: t for t in load("oracles.yaml")["tables"]}
COMP = {c["id"]: c for c in load("companions.yaml")["companions"]}
RIT = load("rituals.yaml")["rituals"]
_lic = load("licenses.yaml")
ABIL = {a["id"]: a for a in load("abilities.yaml")["abilities"]}
LICS = {l["id"] for l in _lic["licenses"]} | {e["id"] for b in _lic["blocks"] for e in b["entries"]}
CAL = load("calendar.yaml")
CLIMATES = {c["id"] for c in load("weather.yaml")["climates"]}
ATTRS = [a["id"] for a in load("attributes.yaml")["attributes"]]
BRANCHES = ["martial", "guile", "influence", "lore", "craft", "wilds", "arcane", "divine", "primal"]
CH_TEXT = {os.path.basename(p)[:2]: open(p, encoding="utf-8").read() for p in
           [os.path.join(R, f) for f in os.listdir(R) if re.match(r"\d\d-.*\.md$", f)]}


# ------------------------------------------------------------------------------------------------ dice
class Dice:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.log = []
    def d(self, n):
        return self.rng.randint(1, n)
    def die(self, s):
        return self.d(int(str(s).lstrip("d")))
    def pick(self, seq):
        return seq[self.rng.randrange(len(seq))]
    def sample(self, seq, k):
        return self.rng.sample(list(seq), k)
    def weighted(self, items):
        tot = sum(w for _, w in items)
        x = self.rng.random() * tot
        for k, w in items:
            x -= w
            if x < 0:
                return k
        return items[-1][0]

_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def num_words(n):
    # [revision: I-069] the wound's age in words for the pitch's {years}
    if n < 20:
        return _ONES[n]
    t, o = divmod(n, 10)
    return _TENS[t] + ("" if o == 0 else "-" + _ONES[o])

def fill_pitch(pitch, region, years):
    w = num_words(years)
    return pitch.replace("{region}", region).replace("{years}", w).replace("{Years}", w[0].upper() + w[1:])

def in_range(rng_s, v):
    a, _, b = str(rng_s).partition("-")
    return int(a) <= v <= int(b or a)

def by_range(rows, v):
    for r in rows:
        if in_range(r["range"], v):
            return r
    raise KeyError(v)

def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower().replace("'", "")).strip("_")

def anc(t, g):
    return t == g or t.startswith(g + ".")


# --------------------------------------------------------------------------------------------- answers
class Answers:
    """Answers come from the player (guided) or the oracle; every answer is logged with its source."""
    def __init__(self, dice, given=None):
        self.dice, self.given, self.log = dice, dict(given or {}), []
    def get(self, qid, oracle_fn):
        if qid in self.given:
            v, src = self.given[qid], "player"
        else:
            v, src = oracle_fn(), "oracle"
        self.log.append({"question": qid, "answer": v, "source": src})
        return v

def oracle_simple(dice, q, ctx=None):
    o = q["oracle"]
    if "from" in o:
        return o["map"][ctx[o["from"]]]
    rows = o["results"]
    if isinstance(rows, dict):
        rows = rows[ctx[o["by"]]]
    return by_range(rows, dice.die(o["die"]))["option"]


# -------------------------------------------------------------------------------------------- names
class Names:
    def __init__(self, dice):
        self.dice, self.used = dice, set()
    def compose(self, starts, ends, sep=""):
        for _ in range(60):
            n = self.dice.pick(starts) + sep + self.dice.pick(ends)
            if n not in self.used:
                self.used.add(n)
                return n
        raise RuntimeError("name space exhausted")
    def place(self):
        t = TAB["tbl.12.seed.place_names"]
        return self.compose(t["start"], t["end"])
    def region(self):
        t = TAB["tbl.12.seed.place_names"]
        return "the %s %s" % (self.compose(t["region_adjective"], t["region_noun"], " ").split(" ", 1)[0],
                              self.dice.pick(t["region_noun"])) if False else "the " + self.compose(t["region_adjective"], t["region_noun"], " ")
    def area(self, terrain):
        t = TAB["tbl.12.seed.place_names"]
        branch = ".".join(terrain.split(".")[:2])
        return "the " + self.compose(t["area_adjective"], t["area_noun_by_terrain"][branch], " ")


def name_tables(dice, names, rs, peoples):
    """One d20 given / d12 family (or epithet) table per present people; two styles for common humans."""
    out = []
    parts = TAB["tbl.12.seed.names"]["by_people"]
    for p in peoples:
        if p["present"] == "absent":
            continue
        spec = parts[p["origin"]]
        styles = spec.get("styles") or [dict(spec, name=None)]
        if p["origin"] == "orig.people.human" and p["present"] != "common":
            styles = styles[:1]
        tabs = []
        for st in styles:
            given = []
            while len(given) < 20:
                n = dice.pick(st["given_start"]) + dice.pick(st["given_end"])
                if n not in given and n not in names.used:
                    given.append(n)
            names.used.update(given)
            if "family_start" in st:
                fam = []
                while len(fam) < 12:
                    n = dice.pick(st["family_start"]) + dice.pick(st["family_end"]) if not st["family_start"][0].startswith("de ") else dice.pick(st["family_start"]) + dice.pick(st["family_end"])
                    n = n if " " in n else n.capitalize()
                    if n not in fam:
                        fam.append(n)
                famkey, famrows = "family", fam
            else:
                famkey, famrows = "epithet", dice.sample(st["epithets"], 12)
            pid = p["origin"].split(".")[-1]
            tid = "tbl.%s.names.%s%s" % (rs, pid, ("_" + slug(st["name"])) if st.get("name") and len(styles) > 1 else "")
            tabs.append({"id": tid, "name": "Names: %s%s" % (pid.replace("_", " "), (" (" + st["name"] + ")") if st.get("name") and len(styles) > 1 else ""),
                         "people": p["origin"], "die": "d20", "recency": True,
                         "given": [{"range": str(i + 1), "result": g} for i, g in enumerate(given)],
                         famkey: [{"range": str(i + 1), "result": f} for i, f in enumerate(famrows)], "family_die": "d12",
                         "basis": ["12.16.7", "12.11.1", "02.9.7"]})
        p["name_tables"] = [t["id"] for t in tabs]
        out += tabs
    return out

PLURAL = {"orig.people.human": "folk", "orig.people.elf": "elves", "orig.people.dwarf": "dwarves", "orig.people.halfling": "halflings",
          "orig.people.orc_kin": "orc-kin", "orig.people.goblin_kin": "goblin-kin", "orig.people.giant_kin": "giant-kin", "orig.people.beastfolk": "beastfolk"}
_GIVEN_USED = set()
def person_name(dice, tables, people_origin):
    """A name from the people's table; no given name is used twice in one seed (recency, 12.11.1)."""
    cands = [t for t in tables if t["people"] == people_origin]
    for _ in range(40):
        t = dice.pick(cands)
        g = by_range(t["given"], dice.d(20))["result"]
        if g in _GIVEN_USED:
            continue
        _GIVEN_USED.add(g)
        if "family" in t:
            return "%s %s" % (g, by_range(t["family"], dice.d(12))["result"])
        return "%s %s" % (g, by_range(t["epithet"], dice.d(12))["result"])
    raise RuntimeError("names exhausted")


# ------------------------------------------------------------------------------------------ the seed
def template_for(org):
    best = None
    for t in TPL.values():
        for o in t["org_tags"]:
            if anc(org, o) and (best is None or o.count(".") > best[0]):
                best = (o.count("."), t)
    if best:
        return best[1]
    branch = ".".join(org.split(".")[:2])
    for t in TPL.values():
        if t.get("branch_default_for") == branch:
            return t
    raise KeyError(org)

def roll_oracle_table(dice, tid, field="results"):
    t = ORAC[tid]
    return by_range(t[field], dice.die(t["die"]))

def step_to(rows, start, fits):
    """[revision: I-053] 12.11.1: from the rolled row, step down the table (wrapping) to the first row that fits."""
    i = rows.index(start)
    for k in range(len(rows)):
        r = rows[(i + k) % len(rows)]
        if fits(r):
            return r
    return start

def role_license(tag):
    """the domain training license of a level-2 deed tag (05.9.3: lic.training.<branch>_<child>), if one exists"""
    p = tag.split(".")
    if len(p) < 3:
        return None
    lid = "lic.training.%s_%s" % (p[1], p[2])
    return lid if lid in LICS else None

def roll_want(dice):
    obj = roll_oracle_table(dice, "tbl.npc_want_object")
    verb = roll_oracle_table(dice, "tbl.npc_want_verb")
    on = int(obj["range"])
    verb = step_to(ORAC["tbl.npc_want_verb"]["results"], verb, lambda r: on in r.get("takes", [on]))
    return "%s %s" % (verb["result"], obj["result"])

def roll_refusal(dice, role_tags):
    r = roll_oracle_table(dice, "tbl.npc_refusal")
    return step_to(ORAC["tbl.npc_refusal"]["results"], r,
                   lambda x: not any(t == n or t.startswith(n + ".") for n in x.get("not_for", []) for t in role_tags))

def make_npc(dice, S, *, role, people, home, member_of=(), depth="principal", band=1, role_tags=(), duty=None, recruit=None, name=None):
    g = roll_oracle_table(dice, "tbl.npc_gender")
    nm = name or person_name(dice, S["names"], people)
    nid = "npc.%s" % slug(nm)
    while nid in S["_npc_ids"]:
        nid += "_%d" % dice.d(9)
    S["_npc_ids"].add(nid)
    folk = ORIGD[people]["tags"][0] if ORIGD[people]["tags"][0].startswith("creature.folk") else [t for t in ORIGD[people]["tags"] if t.startswith("creature.folk")][0]
    want = roll_want(dice)
    sec = roll_oracle_table(dice, "tbl.npc_secret")["result"]
    native = [l["license"] for l in ORIGD[people].get("languages", []) if l["license"] != "lic.lang.common"]
    npc = OrderedDict([
        ("id", nid), ("name", nm), ("role", role), ("people", folk), ("gender", g["result"]), ("pronouns", g["pronouns"]),
        ("age", roll_oracle_table(dice, "tbl.npc_age")["result"]), ("depth", depth), ("home", home),
        ("member_of", list(member_of)),
        ("wants", [{"text": want, "tags": list(role_tags[:1]) or ["conduct.loyalty"], "rank": 1}]),
        ("fears", [{"text": roll_oracle_table(dice, "tbl.npc_fear")["result"], "tags": []}]),
        ("refusals", [{"kind": r.get("kind", "refusal.self"), "text": r["result"]} for r in [roll_refusal(dice, role_tags)]]
                     + ([{"kind": "refusal.duty", "text": duty, "strength": "absolute"}] if duty else [])),  # [verification: V2c-007] 11.3.17, 15.2.4 item 5
        ("secrets", [{"fact": "sec.%s.1" % nid.split(".", 1)[1], "text": sec, "gate": "standing Devoted, or a clue found by play (15.9)"}]),
        ("voice", {"register": roll_oracle_table(dice, "tbl.npc_voice_register")["result"], "habit": roll_oracle_table(dice, "tbl.npc_voice_habit")["result"]}),
        ("detail", roll_oracle_table(dice, "tbl.npc_detail")["result"]),
        ("demeanor", roll_oracle_table(dice, "tbl.npc_demeanor")["result"]),
        ("lifestyle", "comfortable" if depth == "principal" else "modest"),
        ("speaks", ["lic.lang.common"] + native[:1]),
        ("band", band), ("standing_to_pc", 0), ("exists", "exists"),
        ("officer_duty", duty), ("recruit", recruit), ("kind", "npc"), ("tags", [folk]), ("role_tags", list(role_tags)),
        # [revision: I-059] 12.16.11: role competence (T-09-2's c_b by band) and role licenses (trained) as data
        ("competence", [{"tag": t, "value": DEF["npc_competence"]["by_band"][band]} for t in role_tags]),
        ("licenses", [{"id": role_license(t), "grade": "trained"} for t in role_tags if role_license(t)]),
        ("visibility", "background"), ("sealed_fields", ["wants", "fears", "refusals", "secrets", "knowledge"]),
        ("mind", "sapient"), ("knowledge", []), ("lifecycle", "provisional"), ("basis", ["12.11.1", "12.16.11"]),
    ])
    S["npcs"].append(npc)
    return npc


def place_record(pid, name, kind, parent, ring, band, danger, terrain, climate, desc, **kw):
    td = terrain_default(terrain[0]) if terrain else {}
    rec = OrderedDict([
        ("id", pid), ("name", name), ("place_kind", kind), ("parent", parent), ("ring", ring), ("band", band),
        ("danger", danger), ("safe", False), ("rest_site", "rough" if kind == "area" else None), ("terrain", list(terrain)),
        ("climate", climate), ("nav_tier", td.get("nav_tier") if kind == "area" else None), ("forage_tier", None), ("game_tier", None),
        ("openness", td.get("openness", "broken")), ("landmarks", []), ("water_source", None), ("grazing", None),
        ("encounter_table", None), ("hazards", []), ("resonance", []), ("settlement_scope", None),
        ("known", True), ("discovered", False), ("site", None), ("state_log", []), ("links", []), ("facts", {}),
        ("desc", desc), ("kind", "place"), ("tags", list(terrain[:1])), ("exists", "exists"), ("visibility", "shown"),
        ("lifecycle", "provisional"), ("basis", ["10.1.2", "12.16.8"]),
    ])
    rec.update(kw)
    return rec

def terrain_default(t):
    while t:
        if t in TERRAIN_DEF:
            return TERRAIN_DEF[t]
        t = t.rsplit(".", 1)[0] if "." in t else None
    return {}

def link(S, a, b, watches, kind, terrain):
    rid = "rt.%s.%d" % (S["_rs"], len(S["_routes"]) + 1)
    S["_routes"].append(rid)
    P = S["_places"]
    for x, y in ((a, b), (b, a)):
        P[x]["links"].append({"to": y, "route": rid, "route_kind": kind, "travel_watches": watches, "terrain": [terrain],
                              "current": None, "known": P[y]["known"] and P[x]["known"], "danger": None, "hazards": [], "vehicle_ok": ["bi.cart"] if kind == "road" else []})


def build_seed(seed, given=None):
    _GIVEN_USED.clear()
    dice = Dice(seed)
    A = Answers(dice, given)
    names = Names(dice)
    S = {"_npc_ids": set(), "_routes": [], "_places": OrderedDict(), "names": [], "npcs": [], "clocks": []}
    ctx = {}

    # ---------------------------------------------------------------- 1. premise (12.16.4)
    wtab = TAB["tbl.12.seed.wound"]
    wound_opt = A.get("ws.q.wound", lambda: by_range(wtab["results"], dice.d(12))["option"])
    wound = next(r for r in wtab["results"] if r["option"] == wound_opt)
    climate = A.get("ws.q.climate", lambda: oracle_simple(dice, QS["ws.q.climate"]))
    region_name = names.region()
    rs = slug(region_name.replace("the ", ""))
    S["_rs"] = rs
    # [revision: I-069] 12.16.4: the wound's age (its row's era_years) is the opening year of the era (12.16.15), and the
    # pitch says it. Drawn on its own seed-derived stream, like I-083's powers, so no other roll of the seed moves.
    lo, hi = wound["era_years"]
    era_age = Dice(seed * 1013 + 69).rng.randint(lo, hi)
    ctx["era_age"] = era_age
    ctx.update({"ws.q.wound": wound_opt, "ws.q.climate": climate})

    # ---------------------------------------------------------------- 2. canon (12.16.5)
    lvl = A.get("ws.q.magic_level", lambda: oracle_simple(dice, QS["ws.q.magic_level"])); ctx["ws.q.magic_level"] = lvl
    law = A.get("ws.q.magic_law", lambda: oracle_simple(dice, QS["ws.q.magic_law"], ctx))
    spirits = A.get("ws.q.spirits", lambda: oracle_simple(dice, QS["ws.q.spirits"], ctx))
    arcane_src = A.get("ws.q.arcane_source", lambda: oracle_simple(dice, QS["ws.q.arcane_source"]))
    def _extra():
        r = by_range(QS["ws.q.extra_impossible"]["oracle"]["results"], dice.d(6))
        if r.get("option") == "none":
            return []
        return [x["option"] for x in dice.sample(TAB["tbl.12.seed.extra_impossible"]["results"], r["count"])]
    extra = A.get("ws.q.extra_impossible", _extra)
    regrowth = A.get("ws.q.regrowth", lambda: oracle_simple(dice, QS["ws.q.regrowth"]))
    closed_opt = A.get("ws.q.closed_school", lambda: oracle_simple(dice, QS["ws.q.closed_school"]))
    closed = next((o.get("school") for o in QS["ws.q.closed_school"]["options"] if o["id"] == closed_opt), None) or "none"
    relics = A.get("ws.q.relics_magic", lambda: oracle_simple(dice, QS["ws.q.relics_magic"]))
    hybrid = A.get("ws.q.hybrid_none", lambda: oracle_simple(dice, QS["ws.q.hybrid_none"]))
    ci = [{"id": "ci." + c["key"], "text": c["text"], "scope": c["scope"], "basis": c["basis"]} for c in DEF["canon_impossible"]]
    for e in extra:
        row = next(r for r in TAB["tbl.12.seed.extra_impossible"]["results"] if r["option"] == e)
        ci.append({"id": "ci." + e, "text": row["text"], "scope": row["scope"], "basis": ["12.16.5", "05.7.10 item 1"]})
    arc_text = {"anyone_literate": DEF["sources"]["arcane"],
                "order_only": "only those the region's arcane order admits; a teacher outside it is a crime and a text is contraband",
                "gifted_only": "only those born with the gift (a birth gift or a Touched spark naming arcane)"}[arcane_src]
    spirit_odds = {"rare": "Unlikely in any given place; Likely at a place with resonance",
                   "uncommon": "Even in wild places; Likely at a place with resonance",
                   "common": "Likely anywhere wild; Certain at a place with resonance"}[spirits]

    # ---------------------------------------------------------------- 3. faith (12.16.6)
    nk = int(A.get("ws.q.keeper_count", lambda: oracle_simple(dice, QS["ws.q.keeper_count"])))
    forms_all = TAB["tbl.12.seed.keeper_form"]["results"]
    def _forms():
        chosen = []
        while len(chosen) < nk:
            items = [(f["option"], 3 if f["option"] in wound["keeper_bias"] else 1) for f in forms_all if f["option"] not in chosen]
            chosen.append(dice.weighted(items))
        return chosen
    forms = A.get("ws.q.keepers", _forms)
    keepers = []
    for fo in forms:
        f = next(x for x in forms_all if x["option"] == fo)
        nm = names.compose(TAB["tbl.12.seed.names"]["by_people"]["orig.people.human"]["styles"][0]["given_start"],
                           TAB["tbl.12.seed.names"]["by_people"]["orig.people.human"]["styles"][0]["given_end"])
        title = dice.pick(f["title"])
        kid = "keeper.%s" % slug(nm)
        axes = [{"axis": a, "pole": (f.get("pole_override") or {}).get(a, "+")} for a in f["axes"]]
        despises = [{"axis": a, "pole": "+" if (f.get("pole_override") or {}).get(a) == "-" else "-"} for a in f["despises"]]
        keepers.append(OrderedDict([("id", kid), ("name", "%s, %s" % (nm, title)), ("kind", f["kind"]), ("form", fo), ("what", f["what"]),
                                    ("axes", axes), ("despises", despises), ("sign", f["sign"]),
                                    ("schools", [s for s in f["schools"] if s != closed]), ("faith", None), ("faith_org", f["faith_org"]),
                                    ("death", bool(f.get("death"))), ("nature", f.get("nature", "sacred")),  # [revision: I-052] 12.16.6
                                    ("basis", ["05.7.4", "04.9.2", "12.16.6"])]))
    main_keeper = next((k for k in keepers if k["nature"] != "profane"), keepers[0])
    barg = A.get("ws.q.bargainer", lambda: oracle_simple(dice, QS["ws.q.bargainer"]))
    death_k = next((k for k in keepers if k["death"]), None)
    if barg == "death_keeper":
        bargainer = {"who": death_k["id"] if death_k else None, "text": ("%s answers at the door of death (07.5.5)" % death_k["name"]) if death_k else "no one: the land has no keeper of death"}
    elif barg == "fey":
        bargainer = {"who": "arch.fey_noble", "text": "a fey lord of the borderlands answers, for a price paid later (arch.fey_noble, can_bargain)"}
    elif barg == "fiend":
        bargainer = {"who": "arch.tempter", "text": "a tempter answers, and collects (arch.tempter, can_bargain)"}
    else:
        bargainer = {"who": None, "text": "no one answers at the door of death"}

    # ---------------------------------------------------------------- 4. peoples and tongues (12.16.7)
    def _presence():
        out = {}
        cols = ["absent", "rare", "uncommon", "common"]
        for pid, rows in TAB["tbl.12.seed.presence"]["by_people"].items():
            pres = by_range(rows, dice.d(6))["present"]
            folk = [t for t in ORIGD[pid]["tags"] if t.startswith("creature.folk")]
            if any(anc(f, g) or anc(g, f) for f in folk for g in wound["gates"]) and pid != "orig.people.human":
                pres = cols[min(3, cols.index(pres) + 1)]
            out[pid] = pres
        if not any(v != "absent" for k, v in out.items() if k != "orig.people.human"):
            out["orig.people.halfling"] = "uncommon"
        return out
    presence = A.get("ws.q.presence", _presence)
    peoples = []
    for pid, pres in presence.items():
        peoples.append(OrderedDict([("origin", pid), ("present", pres), ("who", None), ("where", []), ("name_tables", []), ("faiths", [k["id"] for k in keepers if k["nature"] != "profane"])]))
    threat_people = next((o["id"] for o in ORIG["origins"] if o["kind"] == "people" and o["id"] != "orig.people.human"
                          and any(anc(t, g) for t in o["tags"] if t.startswith("creature.folk") for g in wound["gates"])), "orig.people.human")
    name_src = [dict(p) for p in peoples]
    for p in name_src:
        if p["origin"] == threat_people and p["present"] == "absent":
            p["present"] = "rare"
    S["names"] = name_tables(dice, names, rs, name_src)
    for p, q in zip(peoples, name_src):
        p["name_tables"] = q["name_tables"] if p["present"] != "absent" else []
    present = [p for p in peoples if p["present"] != "absent"]
    order = {"common": 0, "uncommon": 1, "rare": 2}
    nonhuman = sorted([p for p in present if p["origin"] != "orig.people.human"], key=lambda p: (order[p["present"]], p["origin"]))
    second = A.get("ws.q.second_tongue", lambda: oracle_simple(dice, QS["ws.q.second_tongue"]))
    native = lambda pid: next(l["license"] for l in ORIGD[pid]["languages"] if l["grade"] == "native")
    if second == "people" and nonhuman and native(nonhuman[0]["origin"]) != "lic.lang.common":
        second_lic = native(nonhuman[0]["origin"])
        second_text = "the tongue of the land's %s" % ORIGD[nonhuman[0]["origin"]]["name"].lower()
    else:
        second_lic = "lic.lang.old_tongue"
        second_text = "the Old Tongue, here the speech of the time before the %s" % wound["era"].split("since the ")[-1].split("of the ")[-1]
    tongues = {"list": [{"license": "lic.lang.common", "region_name": "%s-speech" % region_name.split()[-1], "who": "everyone"}],
               "second_tongue": second_lic}
    for p in present:
        lic = native(p["origin"])
        if lic != "lic.lang.common" and all(t["license"] != lic for t in tongues["list"]):
            tongues["list"].append({"license": lic, "region_name": None, "who": "the %s of %s" % (PLURAL[p["origin"]], region_name)})
    if all(t["license"] != second_lic for t in tongues["list"]):
        tongues["list"].append({"license": second_lic, "region_name": None, "who": second_text})
    tongues["list"].append({"license": "lic.lang.cant", "region_name": None, "who": "thieves and smugglers, wherever they are"})

    # ---------------------------------------------------------------- 5. the land (12.16.8)
    tbc = TAB["tbl.12.seed.terrain_by_climate"]
    rings_t = TRAVEL["rings"]
    terrain_by_ring = {}
    hs_opt = A.get("ws.q.haven_site", lambda: by_range(TAB["tbl.12.seed.haven_site"]["results"], dice.d(8))["option"])
    hsite = next(r for r in TAB["tbl.12.seed.haven_site"]["results"] if r["option"] == hs_opt)
    def _terrain():
        out = {1: list(tbc["ring1"][climate])}
        for ring in range(2, 6):
            out[ring] = [by_range(tbc["climates"][climate], dice.d(12))["terrain"] for _ in range(DEF["areas_per_ring"][ring])]
        return out
    tbr = A.get("ws.q.terrain", _terrain)
    region_id = "loc.%s" % rs
    P = S["_places"]
    assert region_id not in P, region_id
    P[region_id] = place_record(region_id, region_name.title().replace("The ", "The "), "region", None, None, 2, "wild",
                                [tbr[2][0]], climate, wound["text"])
    P[region_id]["discovered"] = True
    areas_by_ring = {}
    for ring in range(1, 6):
        rdef = rings_t[ring]
        areas_by_ring[ring] = []
        for i in range(DEF["areas_per_ring"][ring]):
            primary = tbr[ring][i % len(tbr[ring])] if ring > 1 else tbr[1][i % len(tbr[1])]
            terr = [primary]
            if ring == 1 and hsite["terrain"][0].startswith("terrain.water") and i == 0:
                terr.append(hsite["terrain"][0])
            band = rdef["home_band"][0] if len(rdef["home_band"]) == 1 else (rdef["home_band"][0] if dice.d(6) <= 3 else rdef["home_band"][1])
            if ring == 5 and i == DEF["areas_per_ring"][5] - 1 and all(P[x]["band"] < 5 for x in areas_by_ring[5]):
                band = 5      # [revision: I-084] 12.16.8: at least one ring-5 area is home band 5 (a home-5 table exists)
            danger = {1: "settled", 2: "wild", 3: ("wild" if dice.d(6) <= 3 else "perilous"), 4: "perilous", 5: "deadly"}[ring]
            nm = names.area(primary)
            aid = "loc.%s_%s" % (rs, slug(nm.replace("the ", "")))
            rec = place_record(aid, nm[0].upper() + nm[1:], "area", region_id, ring, band, danger, terr, climate,
                               "%s, %s" % (nm, rdef["words"]))
            rec["known"] = ring <= 3
            rec["discovered"] = ring == 1
            rec["water_source"] = any(t.startswith("terrain.water") for t in terr) or None
            assert aid not in P, aid
            P[aid] = rec
            areas_by_ring[ring].append(aid)
        terrain_by_ring[ring] = sorted(set(P[a]["terrain"][0] for a in areas_by_ring[ring]))
    for ring in range(1, 6):
        ids = areas_by_ring[ring]
        for i in range(len(ids)):
            if len(ids) > 1 and (i < len(ids) - 1 or len(ids) > 2):
                j = (i + 1) % len(ids)
                if not any(l["to"] == ids[j] for l in P[ids[i]]["links"]):
                    link(S, ids[i], ids[j], dice.pick(DEF["watches_between"]["same_ring"]), "track" if ring <= 2 else "trackless", P[ids[i]]["terrain"][0])
        if ring > 1:
            for a in ids:
                b = dice.pick(areas_by_ring[ring - 1])
                link(S, a, b, dice.pick(DEF["watches_between"]["next_ring"]), "track" if ring <= 3 else "trackless", P[a]["terrain"][0])

    # ---------------------------------------------------------------- 6. the haven (12.16.9)
    tier = A.get("ws.q.haven_tier", lambda: oracle_simple(dice, QS["ws.q.haven_tier"])); ctx["ws.q.haven_tier"] = tier
    hname = names.place()
    hid = "loc.%s_%s" % (rs, slug(hname))
    host = areas_by_ring[1][0]
    assert hid not in P, hid
    P[hid] = place_record(hid, hname, "settlement", host, 0, None, "safe", ["terrain.settlement." + tier] + hsite["terrain"], climate,
                          "a %s %s, the haven of %s" % ("walled town" if tier == "town" else "village", hsite["text"], region_name),
                          safe=True, rest_site="haven", settlement_scope=hid, discovered=True, water_source=True, grazing=False)
    P[hid]["openness"] = "broken"
    for a in areas_by_ring[1]:
        link(S, hid, a, dice.pick([1, 2]), "road", P[a]["terrain"][0])
        P[a]["settlement_scope"] = hid
    hdef = DEF["haven_by_tier"][tier]
    blds = OrderedDict()
    for b in hdef["buildings"]:
        bname = {"temple": "the temple of %s" % main_keeper["name"].split(",")[0], "shrine": "the shrine of %s" % main_keeper["name"].split(",")[0],
                 "inn": "the %s %s" % (dice.pick(["Drowned", "Golden", "Old", "Blue", "Crooked", "Last", "Sleeping", "Red"]), dice.pick(["Lamb", "Lantern", "Plough", "Bell", "Stag", "Barrel", "Hound", "Goose"])),
                 "smithy": "the smithy", "hall": "the hall", "gate": hsite["feature"], "market": "the market square", "healer": "the healer's house"}[b]
        bid = "%s.%s" % (hid, b)
        assert bid not in P, bid
        P[bid] = place_record(bid, bname, "building", hid, 0, None, "safe", ["terrain.settlement." + tier], climate, bname, safe=True, rest_site="haven" if b == "inn" else None, settlement_scope=hid, discovered=True)
        P[bid]["openness"] = "closed"
        blds[b] = bid
    holy = blds.get("temple") or blds.get("shrine")
    P[holy]["facts"]["consecrated"] = True
    P[holy]["resonance"] = ["deed.divine"]
    gy = "%s.graveyard" % hid
    assert gy not in P, gy
    P[gy] = place_record(gy, "the graveyard", "building", hid, 0, None, "safe", ["terrain.settlement." + tier], climate, "the graveyard, tended by the faithful of %s" % main_keeper["name"].split(",")[0], safe=True, settlement_scope=hid, discovered=True)
    P[gy]["facts"].update({"consecrated": True, "tended_by": None})
    # a place of acceptance for primal workers (02.5.5)
    acc = by_range(TAB["tbl.12.seed.acceptance"]["results"], dice.d(6))
    acc_area = dice.pick(areas_by_ring[1] + areas_by_ring[2])
    acc_name = acc["name"].replace("{name}", names.place())
    acc_id = "loc.%s_%s" % (rs, slug(acc_name.replace("the ", "")))
    assert acc_id not in P, acc_id
    P[acc_id] = place_record(acc_id, acc_name, "landmark", acc_area, P[acc_area]["ring"], P[acc_area]["band"], None, P[acc_area]["terrain"], climate,
                             "%s, where %s dwells" % (acc_name, acc["spirit"]), resonance=["deed.primal"])
    P[acc_id]["facts"]["spirit"] = acc["spirit"]
    P[acc_area]["landmarks"].append(acc_id)
    primal = [t for t in sorted(TAGS) if t.startswith("deed.primal.") and t.count(".") == 2 and t != closed]
    acceptance = [{"place": acc_id, "spirit": acc["spirit"], "schools": dice.sample(primal, 3), "asks": acc["asks"], "contact": None}]
    fight = [{"place": blds["gate"], "features": hsite["fight"]},
             {"place": blds["inn"], "features": ["cover: tables and the bar", "loose objects: stools, tankards, a hearth-poker", "hazard: the hearth fire"]},
             {"place": blds.get("market", blds["hall"]), "features": ["open ground", "crowd: market-goers who scatter (06.3.8)", "loose objects: stalls"]}]
    rare = dice.pick(DEF["rare_metals"])
    stock = {"rare_metal": dict(rare, tag="material.metal.rare", where=None), "components": DEF["components_by_band"]}

    # ---------------------------------------------------------------- 7. factions (12.16.10)
    rul = A.get("ws.q.rulers", lambda: by_range(TAB["tbl.12.seed.rulers"]["by"][tier], dice.d(6))["org"])
    used_orgs = {rul}
    def _fourth():
        for _ in range(20):
            r = by_range(FAC["tbl.11.faction_seed"]["results"], dice.d(12))["org"]
            r = r.split(" ")[0]
            if r not in used_orgs and r != wound["threat_org"] and r != main_keeper["faith_org"]:
                return r
        return "org.guild.craft"
    fourth = A.get("ws.q.fourth_faction", _fourth)
    specs = [("rulers", rul, 2 if tier == "town" else 1, hid, None),
             ("faith", main_keeper["faith_org"], 2 if tier == "town" else 1, hid, main_keeper),
             ("threat", wound["threat_org"], 2 if dice.d(6) <= 3 else 3, None, None),
             ("fourth", fourth, by_range(FAC["tbl.11.faction_tier"]["results"], dice.d(6))["tier"], hid, None)]
    for k in keepers:
        if k is not main_keeper:
            specs.append(("faith_minor", k["faith_org"], 0, hid, k))
    factions = []
    for role, org, ftier, seat, kp in specs:
        t = template_for(org)
        if role in ("faith", "faith_minor"):
            nm = "the faithful of %s" % kp["name"].split(",")[0]
        else:
            fn = TAB["tbl.12.seed.faction_names"]["by_org"]
            key = max((o for o in fn if anc(org, o)), key=lambda o: o.count("."))
            nm = dice.pick(fn[key]).replace("{haven}", hname).replace("{keeper}", main_keeper["name"].split(",")[0])
            if "{place}" in nm:
                nm = nm.replace("{place}", names.place())
        fid = "fac.%s.%s" % (rs, role if role != "faith_minor" else "faith_" + slug(kp["name"].split(",")[0]))
        if kp is not None:
            kp["faith"] = fid
        ratings = dict(zip(["force", "cunning", "wealth", "sway"], t["ratings_by_tier"][ftier]))
        g = by_range([dict(x, range=str(x["d6"])) for x in t["goal_list"]], dice.d(6))
        if role == "threat":
            g = dict(wound["threat_goal"])
        scope = "local" if ftier <= 1 else "regional"
        segs = FAC["goal_clocks"][scope]["segments"]
        if role == "faith_minor":
            # [revision: I-070] a petty faction (11.3.16): its goal is a petty_goals kind (the same d6), local, on the
            # 6-segment clock; text and target are bound after relations (below); rating its highest
            pk = by_range(FAC["petty_goals"]["kinds"], g["d6"])
            hi = max(ratings.values())
            g = {"text": pk["text"], "kind": pk["kind"], "rating": next(k for k in ("force", "cunning", "wealth", "sway") if ratings[k] == hi),
                 "petty": True}
            segs = FAC["petty_goals"]["clock"]["segments"]
        filled = dice.d(max(1, segs // 3))
        clk = {"id": "clk.%s.%s.goal" % (rs, fid.split(".")[-1]), "name": "%s: %s" % (nm, g["text"]), "kind": "faction_goal", "owner": fid,
               "segments": segs, "filled": filled, "visibility": "hidden", "direction": "fill",
               "tick_sources": FAC["goal_clocks"]["tick_sources"], "omens": t["goal_omens"], "basis": ["11.3.1", "PR-11-8", "12.16.10"]}
        S["clocks"].append(clk)
        fac = OrderedDict([("id", fid), ("name", nm[0].upper() + nm[1:]), ("role", role), ("tags", [org]), ("template", t["id"]), ("org_tags", [org]),
                           ("tier", ftier), ("hold", "strong"), ("ratings", ratings), ("temperament", wound["threat_temperament"] if role == "threat" else t["temperament"]),
                           ("lifecycle_stage", "rising" if role == "threat" else "flourishing"), ("full", role in ("rulers", "faith", "threat", "fourth")),
                           ("full_reason", "tier %d >= 2 (11.3.2)" % ftier if ftier >= 2 else ("an opening lead names it: a thread (11.3.2)" if role in ("rulers", "faith", "threat", "fourth") else None)),
                           ("goal", OrderedDict([("text", g["text"]), ("kind", g["kind"]), ("scope", scope), ("rating", g["rating"]), ("clock", clk["id"]), ("effects", []), ("target", None)]
                                             + ([("petty", True)] if g.get("petty") else []))),
                           ("seat", seat), ("holds", [seat] if seat else []), ("linchpins", []), ("officers", []), ("duties", t["duties"]),
                           ("relations", {}), ("status_to_pc", 0), ("attention", None), ("pursuit", 0), ("ranks", t["rank_ladder"]),
                           ("sittings", t["sittings"]), ("fields", t["fields"]), ("values", t["values"]), ("patron_deeds", t["patron_deeds"]),
                           ("boon_base", t["boon_base"]), ("boon_signature", t["boon_signature"]), ("courtable", t["courtable"]),
                           ("lifecycle", "provisional"), ("basis", ["11.3.1", "11.3.18", "PR-11-8", "12.16.10"])])
        factions.append(fac)
    F = {f["role"]: f for f in factions}
    for a, b in itertools.combinations(factions, 2):
        if "threat" in (a["role"], b["role"]):
            v = -2 if {"rulers", "faith"} & {a["role"], b["role"]} else (-1 if dice.d(6) <= 4 else 0)
        else:
            v = {1: -1, 6: 1}.get(dice.d(6), 0)
        if v:
            a["relations"][b["id"]] = v; b["relations"][a["id"]] = v
    # [revision: I-070] bind the petty goals' texts and targets (factions.yaml#petty_goals), no dice
    held = {h for f in factions for h in f["holds"]}
    for f in factions:
        gl = f["goal"]
        if not gl.get("petty"):
            continue
        tgt, txt = None, gl["text"].replace("{seat}", hname)
        if gl["kind"] == "take":
            tgt = next(a for r in (1, 2, 3, 4, 5) for a in sorted(areas_by_ring[r]) if a not in held)
            held.add(tgt)
            txt = txt.replace("{place}", P[tgt]["name"])
        elif gl["kind"] == "feud":
            others = [o for o in factions if o is not f]
            nb = min(others, key=lambda o: (f["relations"].get(o["id"], 0), -o["tier"], o["id"]))
            tgt = nb["id"]
            txt = txt.replace("{neighbor}", nb["name"][0].lower() + nb["name"][1:] if nb["name"].startswith("The ") else nb["name"])
        gl["text"], gl["target"] = txt, tgt
        clk = next(c for c in S["clocks"] if c["id"] == gl["clock"])
        clk["name"] = "%s: %s" % (clk["name"].split(": ")[0], txt)

    # ---------------------------------------------------------------- 8. the cast (12.16.11)
    PW = {"common": 6, "uncommon": 3, "rare": 1}
    local_weights = [(p["origin"], PW[p["present"]]) for p in present]
    def people_for(i, role=None):
        if role == "threat":
            return threat_people
        if role in ("rulers", "faith") and threat_people != "orig.people.human":
            # the haven's own powers are not of the people behind the wound (12.16.11)
            return dice.weighted([(o, w) for o, w in local_weights if o != threat_people])
        return dice.weighted(local_weights)
    npc_i = itertools.count()
    T22 = {0: 1, 1: 2, 2: 2, 3: 3, 4: 3, 5: 4}
    for fac in factions:
        home = {"rulers": blds["hall"], "faith": holy, "fourth": blds.get("market", blds["hall"]), "faith_minor": holy}.get(fac["role"], None)
        head = make_npc(dice, S, role="head of %s" % fac["name"], people=people_for(next(npc_i), fac["role"]), home=home or region_id, member_of=[fac["id"]],
                        band=T22[fac["tier"]] + 1, role_tags=fac["patron_deeds"][:2], duty=fac["duties"][0])
        fac["officers"].append(head["id"])
        fates = {f["fate"]: f["effects"] for f in template_for(fac["org_tags"][0])["fate_list"]}
        cons = next(f["consequence"] for f in template_for(fac["org_tags"][0])["fate_list"] if f["fate"] == "dies")
        fac["linchpins"].append({"npc": head["id"], "consequence": cons, "fates": fates, "sealed": True})
        if fac["full"]:
            off = make_npc(dice, S, role="officer of %s" % fac["name"], people=people_for(next(npc_i), fac["role"]), home=home or region_id, member_of=[fac["id"]],
                           band=T22[fac["tier"]], role_tags=fac["patron_deeds"][:1], duty=fac["duties"][1 % len(fac["duties"])])
            fac["officers"].append(off["id"])
    priest = next(n for n in S["npcs"] if n["id"] == F["faith"]["officers"][0])
    smith = make_npc(dice, S, role="smith", people=people_for(next(npc_i)), home=blds["smithy"], depth="minor", band=1, role_tags=["deed.craft.smithing"])
    keeper_inn = make_npc(dice, S, role="innkeeper", people=people_for(next(npc_i)), home=blds["inn"], depth="minor", band=1, role_tags=["deed.influence"])
    captain = make_npc(dice, S, role="captain of the gate", people="orig.people.human", home=blds["gate"], member_of=[F["rulers"]["id"]], depth="minor", band=2,
                       role_tags=["deed.martial.polearm", "deed.martial.shield"], duty="never opens the gate after the night watch",
                       recruit={"cmp": "cmp.veteran", "band": 2, "terms": "for a share and a cause the rulers approve (16.3.4)"})
    wise = make_npc(dice, S, role="wise-woman of %s" % acc_name, people=people_for(next(npc_i)), home=acc_id, depth="minor", band=1, role_tags=["deed.primal"])
    acceptance[0]["contact"] = "%s (brings candidates to the spirit)" % wise["id"]
    sword = make_npc(dice, S, role="sellsword between contracts", people=people_for(next(npc_i)), home=blds["inn"], depth="minor", band=1,
                     role_tags=["deed.martial.blade"], recruit={"cmp": "cmp.soldier", "band": 1, "terms": "wages (16.3.2) and a fair share"})
    scholar = None
    if tier == "town":
        scholar = make_npc(dice, S, role="scribe and teacher of letters", people=people_for(next(npc_i)), home=blds["hall"], depth="minor", band=1, role_tags=["deed.lore", "deed.craft.scribing"])
    healer = make_npc(dice, S, role="healer" if tier == "town" else "herb-wife", people=people_for(next(npc_i)), home=blds.get("healer", holy), depth="minor", band=1, role_tags=["deed.wilds.foraging", "deed.craft.alchemy"])
    P[gy]["facts"]["tended_by"] = F["faith"]["id"]
    # [revision: I-052] 05.7.4: a cast NPC's divine license must be a school of a keeper whose faith it belongs to
    kof = {k["faith"]: k for k in keepers if k.get("faith")}
    for n in S["npcs"]:
        kept = {s for m in n["member_of"] if m in kof for s in kof[m]["schools"]}
        n["licenses"] = [l for l in n["licenses"] if not l["id"].startswith("lic.training.divine_")
                         or "deed.divine.%s" % l["id"].rsplit("_", 1)[-1] in kept]
    # teachers (15.13; downtime.yaml#teacher_odds), from the cast
    teachers = []
    for sch in main_keeper["schools"]:
        teachers.append({"target": "lic.training.divine_%s" % sch.split(".")[-1], "npc": priest["id"], "grade": "expert", "requires": "%s accepts the student (05.7.4)" % main_keeper["id"]})
    teachers += [{"target": "lic.training.martial_polearm", "npc": captain["id"], "grade": "expert"},
                 {"target": "lic.training.martial_shield", "npc": captain["id"], "grade": "trained"},
                 {"target": "lic.training.craft_smithing", "npc": smith["id"], "grade": "expert" if tier == "town" else "trained"},
                 {"target": "lic.training.wilds_foraging", "npc": healer["id"], "grade": "trained"}]
    for sch in acceptance[0]["schools"]:
        teachers.append({"target": "lic.training.primal_%s" % sch.split(".")[-1], "npc": wise["id"], "grade": "trained", "requires": "%s accepts the student (05.9.4)" % acc_id})
    if scholar:
        teachers.append({"target": "lic.lang.letters", "npc": scholar["id"], "grade": "trained"})
        teachers.append({"target": "lic.training.lore_history", "npc": scholar["id"], "grade": "expert"})
    arcane_at = next(o for o in QS["ws.q.magic_level"]["options"] if o["id"] == lvl)["arcane_teacher_at"]
    mage = None
    if (arcane_at == "village") or (arcane_at == "town" and tier == "town"):
        mage = make_npc(dice, S, role="hedge-mage", people=people_for(next(npc_i)), home=blds["hall"], depth="minor", band=2, role_tags=["deed.arcane"])
        for sch in dice.sample([t for t in sorted(TAGS) if t.startswith("deed.arcane.") and t.count(".") == 2 and t != closed], 2):
            teachers.append({"target": "lic.training.arcane_%s" % sch.split(".")[-1], "npc": mage["id"], "grade": "trained",
                             "requires": "letters and the teacher (05.9.4)" + ("; admission to the arcane order" if arcane_src == "order_only" else "")})
    for t in teachers:
        assert t["target"] in LICS, t["target"]
        # [revision: I-059] 15.11.1 MENTOR: the teacher's record holds the target at expert (a tongue or letters: held)
        npc = next(n for n in S["npcs"] if n["id"] == t["npc"])
        grade = "expert" if t["target"].startswith("lic.training.") else None
        have = next((l for l in npc["licenses"] if l["id"] == t["target"]), None)
        if have:
            have["grade"] = grade
        else:
            npc["licenses"].append({"id": t["target"], "grade": grade})
    bond_placement = [
        {"slot": "anchor", "kind": "kin", "where": hid, "default_npc": None, "note": "a new NPC in %s (02.9.8: never one already in the cast)" % hname},
        {"slot": "anchor", "kind": "friend", "where": blds["inn"], "default_npc": None, "note": "a regular at %s" % P[blds["inn"]]["name"]},
        {"slot": "anchor", "kind": "mentor", "where": holy, "default_npc": None, "note": "a teacher of the PC's trade, in the haven"},
        {"slot": "anchor", "kind": "ward", "where": hid, "default_npc": None},
        {"slot": "thorn", "kind": "rival", "where": F["fourth"]["seat"] or hid, "default_npc": None, "note": "a member of %s" % F["fourth"]["name"]},
        {"slot": "thorn", "kind": "creditor", "where": blds.get("market", blds["hall"]), "default_npc": None, "note": "a member of %s" % F["rulers"]["name"]},
        {"slot": "thorn", "kind": "enemy", "where": None, "default_npc": None, "note": "a member of %s (seat bound in step 9)" % F["threat"]["name"]},
        {"slot": "thorn", "kind": "lost", "where": None, "default_npc": None, "note": "a hook of kind question; last seen at a ring-2 site (bound in step 9)"},
    ]

    # ---------------------------------------------------------------- 9. sites, lairs and threats (12.16.12)
    sites = []
    theme_ids = list(THEMES)
    for ring in range(1, 6):
        for a in areas_by_ring[ring]:
            if ring >= 4 and a != areas_by_ring[ring][0]:
                continue
            th = dice.weighted([(t, 3 if t in wound["themes"] else 1) for t in theme_ids])
            if ring == 3 and a == areas_by_ring[3][0]:
                th = wound["themes"][0]        # the threat faction's seat (12.16.12): the wound's first theme
            aterr = P[a]["terrain"]
            doms = [d for d in DOMAINS.values() if any(anc(dt, at) or anc(at, dt) for dt in d["terrain_tags"] for at in aterr)]
            if not doms:
                doms = [d for d in DOMAINS.values() if any(anc(dt, "terrain.ruin") or anc(dt, "terrain.underground") for dt in d["terrain_tags"])]
            dom = dice.pick(sorted(doms, key=lambda d: d["id"]))
            band = P[a]["band"]
            lair = ring >= 4
            if lair:
                band = min(5, band + 1)
            else:
                r6 = dice.d(6)
                band = max(1, band - 1) if r6 == 1 else band
            size = {1: "small", 2: "small", 3: "medium", 4: "medium", 5: "large", 6: dom.get("typical_size", "medium")}[dice.d(6)]
            while True:
                pat = dice.pick(TAB["tbl.12.seed.place_names"]["site_patterns"])
                sn = pat.replace("{domain}", TAB["tbl.12.seed.place_names"]["domain_nouns"][dom["id"]]).replace("{name}", names.place()).replace(
                    "{adjective}", dice.pick(TAB["tbl.12.seed.place_names"]["area_adjective"]))
                sid = "loc.%s_%s" % (rs, slug(sn.replace("the ", "")))
                if sid not in P:
                    break
            climax = by_range(THEMES[th]["climax"], dice.d(6))
            sz = next(x for x in SITES["sizes"] if x["id"] == size)
            pool = {r["ref"]: r["weight"] for r in POOLS[(th, dom["id"])]["archetypes"]}
            fb = {aid: 1 for aid, ar in ARCHD.items() if any(anc(c, g) for c in ar["creature_tags"] for g in THEMES[th]["creature_gate_tags"])}
            rows, blog = TB.build_threat_table(pool, band, dice.rng, fallback_pool=fb)
            rec = place_record(sid, sn[0].upper() + sn[1:], "site", a, ring, band, None, [dom["terrain_tags"][0]], climate,
                               "%s: %s, %s" % (sn, THEMES[th]["name"].lower(), dom["name"].lower()))
            rec["known"] = ring <= 2 or lair
            rec["encounter_table"] = None
            rec["site"] = OrderedDict([("theme", th), ("domain", dom["id"]), ("band", band), ("size", size),
                                       ("objective", {"kind": "climax", "ref": None, "text": climax["result"], "sealed": True}),
                                       ("lair", lair), ("danger", THEMES[th].get("danger")), ("explore_tier", dom.get("explore_tier")),
                                       ("clock_sizes", {"progress": sz["progress"], "danger": sz["danger"]}),
                                       ("denizen_table", rows), ("areas", []), ("path", []), ("secured", []), ("denizens", []), ("traps", []),
                                       ("frontier", None), ("roused", False), ("last_left", None)])
            if th == "site.theme.hallowed":
                rec["facts"]["consecrated"] = True
            if th == "site.theme.corrupted":
                rec["facts"]["desecrated"] = True
            if th == "site.theme.haunted":
                rec["facts"]["haunted"] = True
            if th in ("site.theme.ancient",):
                rec["resonance"] = ["deed.arcane"]
            assert sid not in P, sid
            P[sid] = rec
            link(S, a, sid, 1 if ring <= 2 else 2, "track" if ring <= 2 else "trackless", aterr[0])
            sites.append(sid)
    # the threat's seat: a ring-3 site (else the deepest ring-2 site)
    seat_site = next(s for s in sites if P[s]["parent"] == areas_by_ring[3][0])
    F["threat"]["seat"] = seat_site; F["threat"]["holds"] = [seat_site]
    P[seat_site]["site"]["objective"] = {"kind": "faction_seat", "ref": F["threat"]["id"], "text": "the seat of %s, and its head" % F["threat"]["name"], "sealed": True}
    for n in S["npcs"]:
        if F["threat"]["id"] in n["member_of"]:
            n["home"] = seat_site
    bond_placement[6]["where"] = seat_site
    lost_site = next(s for s in sites if P[s]["ring"] == 2)
    bond_placement[7]["where"] = lost_site
    stock["rare_metal"]["where"] = next((s for s in sites if P[s]["site"]["domain"] in ("site.domain.mine", "site.domain.cavern", "site.domain.underkeep")), sites[-1])
    # situations: the wound's, and one local hook (11.4.1, 11.4.3)
    situations = []
    def instantiate(tid, place, roles, what, sid):
        """A situation in 11.4.1's shape, its timeline written whole and sealed now, its first step already fired."""
        t = SITT[tid]
        steps = t["steps"]
        tl = []
        for i, st in enumerate(steps):
            tl.append(OrderedDict([("n", st.get("n", i + 1)), ("at", {"after": st["at"]} if st.get("at") else None), ("trigger", st.get("trigger")),
                                   ("requires", [steps[i - 1].get("n", i)] if i else []), ("prevented_by", st["prevented_by"]),
                                   ("key_delta", [st["key_delta"]]), ("trace", st["trace"]), ("bang", None)]))
        return OrderedDict([("id", "sit.%s.%s" % (rs, sid)), ("title", t["name"]), ("template", tid), ("region", place),
                            ("actors", sorted(set(roles.values()))), ("roles", roles), ("what", what),
                            ("premise", []), ("cadence", t["cadence"]), ("timeline", tl), ("fired", [tl[0]["n"]]),
                            ("end_state", [t["end_state"]]), ("if_prevented", [t["if_prevented"]]), ("thread", None), ("status", "active"),
                            ("visibility", "sealed (the timeline; its traces are shown as they fire)"),
                            ("lifecycle", "provisional"), ("basis", ["11.4.1", "11.4.2", "12.16.12"])])
    big_roles = {r: (F["threat"]["id"] if i == 0 else (F["rulers"]["id"] if i == 1 else F["faith"]["id"])) for i, r in enumerate(SITT[wound["situation"]]["roles"])}
    situations.append(instantiate(wound["situation"], dice.pick(areas_by_ring[2]), big_roles, fill_pitch(wound["pitch"], region_name, ctx["era_age"]), "wound"))
    hook = by_range(WT["tbl.11.hook"]["results"], dice.d(20))
    tries = 0
    while "template" not in hook and tries < 20:
        hook = by_range(WT["tbl.11.hook"]["results"], dice.d(20)); tries += 1
    local_roles = {r: (F["fourth"]["id"] if i == 0 else F["rulers"]["id"]) for i, r in enumerate(SITT[hook["template"]]["roles"])}
    situations.append(instantiate(hook["template"], dice.pick(areas_by_ring[1]), local_roles, hook["seed"], "local"))

    # ---------------------------------------------------------------- 10. encounter tables (12.16.13)
    folk_absent = {"orig.people.elf": "arch.elf_warden", "orig.people.dwarf": "arch.dwarf_holdguard"}
    excluded = {folk_absent[p["origin"]] for p in peoples if p["present"] == "absent" and p["origin"] in folk_absent}
    fielded = {f["archetype"] for fac in factions for f in fac["fields"]}
    enc_tables, audit = [], {}
    for ring in range(1, 6):
        for a in areas_by_ring[ring]:
            terr = P[a]["terrain"]
            branch = ".".join(terr[0].split(".")[:2])
            def lives(ar, tags=terr):
                return any(anc(at, t) or anc(t, at) for at in ar["encounter"]["terrain"] for t in tags)
            pool = {}
            for aid, ar in ARCHD.items():
                if aid in excluded or not lives(ar):
                    continue
                w = 1
                if any(anc(c, g) for c in ar["creature_tags"] for g in wound["gates"]):
                    w *= 3
                if aid in fielded:
                    w *= 2
                pool[aid] = w
            fb = {aid: 1 for aid, ar in ARCHD.items() if aid not in excluded and lives(ar, [branch])}
            gen = GENERIC_ENC.get(branch) or GENERIC_ENC["terrain.plains"]
            for attempt in range(3):          # 12.16.13: a failing build is rebuilt; the generic table after three
                rows, blog = TB.build_threat_table(pool, P[a]["band"], dice.rng, fallback_pool=fb)
                if WA.audit_table(rows, P[a]["band"], gen["non_threat"])[0]:
                    break
            else:
                rows, blog = gen["threat_by_home"][P[a]["band"]], [(0, None, None, None, None, None, "generic")]
            tid = "tbl.%s.enc.%s" % (rs, a[len("loc.%s_" % rs):])
            tab = OrderedDict([("id", tid), ("name", "Encounters: %s" % P[a]["name"]), ("home_band", P[a]["band"]), ("danger", P[a]["danger"]),
                               ("terrain", terr[0]), ("threat_die", "d20"), ("threat", rows), ("non_threat_die", "d6"), ("non_threat", gen["non_threat"]),
                               ("built_by", "PR-10-10"), ("lifecycle", "provisional"), ("basis", ["10.10.1", "PR-10-10", "PR-10-8", "12.16.13"])])
            ok, summ, fails, _ = WA.audit_table(rows, P[a]["band"], gen["non_threat"])
            audit[tid] = {"pass": ok, "bands": summ["bands"], "words": summ["words"], "fair_or_easier": summ["fair_or_easier"], "failures": fails,
                          "pool_size": len(pool), "slots_from": dict(Counter(x[6] for x in blog))}
            P[a]["encounter_table"] = tid
            for s in sites:
                if P[s]["parent"] == a:
                    P[s]["encounter_table"] = tid
            enc_tables.append(tab)
    bestiary_arch = sorted({r["ref"][0] for t in enc_tables for r in t["threat"]} |
                           {r["ref"][0] for s in sites for r in P[s]["site"]["denizen_table"]} | fielded)

    # ---------------------------------------------------------------- 11. rumors (12.16.14)
    rum = []
    def truth(src):
        row = WT["tbl.11.rumor_truth"]["rows"][src]
        v = dice.d(10)
        return next(k for k, rr in row.items() if k in ("true", "partial", "false") and in_range(rr, v))
    for f in factions:
        if f["full"]:
            rum.append({"text": "Word is that %s will try to %s." % (f["name"][0].lower() + f["name"][1:] if f["name"].startswith("The ") else f["name"], f["goal"]["text"]), "truth": "true", "points_to": f["goal"]["clock"], "source": "hearsay"})
    for s in situations:
        rum.append({"text": s["timeline"][0]["trace"].capitalize() + "; folk say it is only the beginning.", "truth": "true", "points_to": s["id"], "source": "eyewitness"})
    for sid in sites:
        src = "legend" if P[sid]["ring"] >= 3 else "hearsay"
        t = truth(src)
        obj = P[sid]["site"]["objective"]["text"]
        txt = {"true": "At %s lies %s." % (P[sid]["name"], obj),
               "partial": "At %s lies %s, and no one has ever come back from it." % (P[sid]["name"], obj),
               "false": "%s is empty now; whatever was there is long gone." % P[sid]["name"]}[t]
        rum.append({"text": txt, "truth": t, "points_to": sid, "source": src})
    k = keepers[0]
    rum.append({"text": "%s has been seen in a dream by three people this month." % k["name"].split(",")[0], "truth": truth("legend"), "points_to": k["faith"], "source": "legend"})
    rum = rum[:20]
    die = "d20" if len(rum) > 12 else "d12"
    nfaces = int(die[1:])
    rows = []
    for i, r in enumerate(rum):
        rows.append(dict(range=str(i + 1), **r))
    i = len(rows)
    while len(rows) < nfaces:
        base = rum[(len(rows) - i) % len(rum)]
        rows.append(dict(range=str(len(rows) + 1), text=base["text"].rstrip(".") + ", or so the drovers say.", truth=base["truth"] if base["truth"] != "true" else "partial", points_to=base["points_to"], source="hearsay"))
    rumor_tables = [{"id": "tbl.%s.rumors" % rs, "name": "Rumors of %s" % region_name, "die": die, "rule": "each rumor's truth is SEALED here (11.6.1); 11.6.3's distortion applies as it spreads", "results": rows}]

    # ---------------------------------------------------------------- 12. calendar (12.16.15)
    mn = A.get("ws.q.month_names", lambda: oracle_simple(dice, QS["ws.q.month_names"]))
    ct = TAB["tbl.12.seed.calendar_names"]
    if mn == "named":
        months = []
        for season in ["spring", "summer", "autumn", "winter"]:
            words = dice.sample(ct["months_by_season"][season], 3)
            for w_ in words:
                months.append(dice.pick(ct["month_patterns"]).replace("{word}", w_))
    else:
        months = [m["name"] for m in CAL["months"]]
    fest = {k: v.replace("{keeper}", main_keeper["name"].split(",")[0]) for k, v in ct["festival_patterns"].items()}
    year = ctx["era_age"]          # [revision: I-069] the wound's age, rolled at step 1 (12.16.4), not a free d20
    calendar = {"months": months, "day_names": ct["weekdays"] if mn == "named" else CAL["day_names"],
                "era": {"name": wound["era"], "year_one": "the year %s" % re.sub(r"^years (since|of) ", "", wound["era"]).replace("the ", "of the ", 1)},
                "festivals": [{"quarter_day": q, "name": fest[q]} for q in ["spring", "summer", "autumn", "winter"]],
                "lifespans": "calendar.yaml#lifespans (generic)", "opening_date": "the spring quarter day, %d %s" % (year, wound["era"]),
                "basis": ["11.10.1", "11.10.4", "12.16.15"]}

    # ---------------------------------------------------------------- 13. opening and pregens (12.16.16)
    inc_opt = A.get("ws.q.inciting", lambda: by_range(TAB["tbl.12.seed.inciting"]["results"], dice.d(8))["option"])
    inc = next(r for r in TAB["tbl.12.seed.inciting"]["results"] if r["option"] == inc_opt)
    first_target = {"situation": situations[0]["id"], "faction_threat": F["threat"]["id"], "faction_goal": F["rulers"]["goal"]["clock"],
                    "site_ring1": next(s for s in sites if P[s]["ring"] == 1), "site_ring2": lost_site}[inc["lead_to"]]
    start_place = {"gate": blds["gate"], "market": blds.get("market", blds["gate"]), "square": blds.get("market", hid), "hall": blds["hall"],
                   "temple": holy, "walls": blds["gate"], "inn": blds["inn"]}
    scene_key = next(k for k in start_place if k in inc["scene"])
    _si = 0 if first_target != situations[0]["id"] else 1
    leads = [{"lead": "the incident itself: %s" % inc["text"], "points_to": first_target},
             # [revision: I-069 sweep] the lead's words are the first-trace rumor of the situation it points to (12.16.14 order:
             # the full factions' goals, then each situation's first trace); before, it always quoted the wound's
             {"lead": rum[len([f for f in factions if f['full']]) + _si]["text"], "points_to": situations[_si]["id"]},
             {"lead": "%s is hiring, and asks no questions" % F["fourth"]["name"], "points_to": F["fourth"]["goal"]["clock"]}]
    regime = "%s spring" % climate
    opening = {"start": {"date": calendar["opening_date"], "watch": "dawn", "place": start_place[scene_key],
                         "weather": {"fact": "weather.today", "value": "rolled at the first dawn by h.10.weather in the %s regime (10.11.3)" % regime, "source": "engine"},
                         "moon": "new (day 1 of the year: 11.10.3)", "festival": "%s (market, sitting, hiring fair)" % fest["spring"]},
               "inciting": {"option": inc_opt, "text": inc["text"], "scene": inc["scene"], "frame": "in medias res (12.4.3: the session's strong start)",
                            "pairs_with": "the PC's long vow (02.9.1): the incident is the first step of the vow or a threat to the anchor bond"},
               "leads": leads, "starting_state": {"known_places": "ring 0-3 areas and their known sites (rumor)", "status": "0 with every faction unless a creation tie sets it (02.9.5)"}}
    pregens = make_pregens(dice, S, peoples, nonhuman, keepers, main_keeper, acceptance, blds, hid, arcane_src, lvl, tier)

    # ---------------------------------------------------------------- assemble the region record
    places = list(P.values())
    for p in peoples:
        p["who"] = {"common": "many", "uncommon": "some", "rare": "a few", "absent": "none"}[p["present"]] + " " + ORIGD[p["origin"]]["name"].lower() + " folk"
        p["where"] = [hid] if p["present"] in ("common", "uncommon") else []
    org_tie = []
    origin_orgs = sorted({t for o in ORIG["origins"] for t in (o.get("org_tags") or []) if t.startswith("org.")})
    for org in origin_orgs:
        exact = [f for f in factions if f["org_tags"][0] == org]
        branch = [f for f in factions if f["org_tags"][0].split(".")[:2] == org.split(".")[:2] and f is not F["threat"]]
        m = (exact or branch or [None])[0]
        org_tie.append({"org": org, "faction": m["id"] if m else None, "note": None if m else "none in this land (02.9.5: the tie is to an absent kind; 11 writes no status)"})
    inst = []
    for b in BRANCHES:
        fs = [f["id"] for f in factions if any(anc(pd, "deed." + b) or anc("deed." + b, pd) for pd in f["patron_deeds"])]
        inst.append({"branch": "deed." + b, "factions": fs})
    hsettle = OrderedDict([("tier", tier), ("values_faction", F["rulers"]["id"]), ("seat_of", [f["id"] for f in factions if f["seat"] == hid]),
                           ("market", {"common": sorted(set(DEF["market_by_terrain"].get(".".join(P[areas_by_ring[1][0]]["terrain"][0].split(".")[:2]), {}).get("common", []) + DEF["market_by_terrain"].get(".".join(hsite["terrain"][0].split(".")[:2]), {}).get("common", []))),
                                       "scarce": sorted(set(DEF["market_by_terrain"].get(".".join(P[areas_by_ring[1][0]]["terrain"][0].split(".")[:2]), {}).get("scarce", []) + DEF["market_by_terrain"]["always_scarce"])),
                                       "depth": hdef["market_depth"]}),
                           ("special_stock", []), ("curio", None),
                           ("crafters", [dict(c, npc=smith["id"] if c["trade"] == "deed.craft.smithing" else None) for c in hdef["crafters"]]),
                           ("teachers", teachers),
                           ("texts", [{"name": "a prayer-book of %s" % main_keeper["name"].split(",")[0], "base": "bi.book", "where": holy,
                                       "teaches": next((r["id"] for r in RIT if any(anc(r["tags"][0], s) for s in main_keeper["schools"])), None), "price": None, "note": "lent to the faithful"}]),
                           ("rites_known", sorted({r["id"] for r in RIT if any(anc(r["tags"][0], s) for k in keepers for s in k["schools"])} |
                                                  {r["id"] for r in RIT if any(anc(r["tags"][0], s) for s in acceptance[0]["schools"])})),
                           ("hire", {"roles": hdef["hire"]["roles"] + (["cmp.boatman"] if hsite["terrain"][0].startswith("terrain.water") and tier == "town" else []),
                                     "max_band": hdef["hire"]["max_band"], "quirk_table": "companions.yaml#tbl.16.hire_quirk"}),
                           ("sentry_floors", [dict(post=P[blds[b]]["name"], **DEF["sentry_floors"][b]) for b in ("gate", "hall", "temple", "shrine") if b in blds]),
                           ("lifestyle_overrides", [])])
    P[hid]["settlement"] = hsettle
    # [revision: I-083] 12.16.11: the powers of the far rings -- one principal per ring-4 area (band 4) and per
    # ring-5 area (band 5), each keeping a sealed truth. Drawn on its own stream (seed-derived) so that every
    # earlier roll of the seed, and the committed example, is unchanged.
    pdice = Dice(seed * 1009 + 83)
    prow = TAB["tbl.12.seed.powers"]["results"]
    used = set()
    for ring in (4, 5):
        for a in areas_by_ring[ring]:
            row = step_to(prow, by_range(prow, pdice.d(8)), lambda r: r["range"] not in used)
            used.add(row["range"])
            people = pdice.weighted(local_weights)
            pw = make_npc(pdice, S, role=row["role"], people=people, home=a, depth="principal",
                          band=ring, role_tags=row["role_tags"])
            pw["power"] = True
            pw["keeps"] = {"fact": "truth.%s" % pw["id"].split(".", 1)[1], "text": row["keeps"], "sealed": True,
                           "gate": "a lore contest kept by this power (15.9.20), or standing Devoted"}
            pw["sealed_fields"].append("keeps")
            pw["basis"] = ["12.11.1", "12.16.11"]
    for f in factions:
        f.pop("role", None)
    for k in keepers:
        k.pop("faith_org", None)
    region = OrderedDict([
        ("schema_version", 1),
        ("seed", {"procedure": "12.16", "seed": seed, "mode": "guided" if given else "oracle", "answers": A.log,
                  "generated_by": "_process/simulation/12-world-seed.py", "uses_generic": DEF["uses_generic"]}),
        ("region", OrderedDict([("id", region_id), ("name", P[region_id]["name"]), ("home_band", 1), ("danger", "settled"), ("climate", climate),
                                ("haven", hid), ("wound", wound_opt),
                                ("rings", [{"ring": 0, "words": rings_t[0]["words"], "home_band": None, "areas": [], "places": [hid]}] +
                                          [{"ring": r, "words": rings_t[r]["words"], "home_band": rings_t[r]["home_band"], "areas": areas_by_ring[r],
                                            "places": [s for s in sites if P[s]["ring"] == r]} for r in range(1, 6)]),
                                ("pitch", fill_pitch(wound["pitch"], P[region_id]["name"], ctx["era_age"])),
                                ("truths", wound["truths"]), ("lifecycle", "provisional"), ("basis", ["12.16.4", "12.16.8"])])),
        ("canon_impossible", [c["text"] for c in ci]),
        ("canon", OrderedDict([
            ("impossible", ci),
            ("facts", [{"id": "canon.wound", "text": wound["text"]},
                       {"id": "canon.magic_level", "value": lvl},
                       {"id": "canon.magic_lawful", "value": law, "text": next(o["text"] for o in QS["ws.q.magic_law"]["options"] if o["id"] == law)},
                       {"id": "canon.default_bargainer", "value": bargainer["who"], "text": bargainer["text"]},
                       {"id": "canon.regrowth", "value": regrowth, "text": next(o["text"] for o in QS["ws.q.regrowth"]["options"] if o["id"] == regrowth)},
                       {"id": "canon.arcane_source", "value": arcane_src, "text": arc_text}]),
            ("magic", OrderedDict([("item_1_canon_impossible", [c["id"] for c in ci]),
                                   ("item_2_sources", {"arcane": arc_text, "divine": DEF["sources"]["divine"], "primal": DEF["sources"]["primal"]}),
                                   ("item_3_keepers", [k["id"] for k in keepers]),
                                   ("item_4_places_of_power", sorted(p["id"] for p in P.values() if p["resonance"] or p["facts"].get("desecrated") or p["facts"].get("consecrated"))),
                                   ("item_5_spirit_frequency", {"level": spirits, "odds": spirit_odds}),
                                   ("item_6_lawfulness", law),
                                   ("item_7_components", "stock.components; texts and teachers in places[].settlement"),
                                   ("item_8_schools", {"closed": [] if closed == "none" else [closed],
                                                       "conduct_evidence": ["deed.arcane.necromancy.raising", "deed.divine.pact"]})])),
            ("components", DEF["components_by_band"]),
            ("spirits", "Spirits of place exist (%s); they understand heartfelt speech in any tongue, and anything they are owed." % spirits),
            ("hybrid_none_pairs", hybrid),
            ("relics_and_refusal", next(o["text"] for o in QS["ws.q.relics_magic"]["options"] if o["id"] == relics)),
        ])),
        ("keepers", keepers),
        ("tongues", tongues),
        ("peoples", peoples),
        ("absent_origins", [p["origin"] for p in peoples if p["present"] == "absent"]),
        ("names", S["names"]),
        ("places", places),
        ("places_of_acceptance", acceptance),
        ("fight_locations", fight),
        ("objects", []),
        ("npcs", S["npcs"]),
        ("bond_placement", bond_placement),
        ("factions", OrderedDict([("instances", factions), ("ids", [f["id"] for f in factions]), ("full_at_start", [f["id"] for f in factions if f["full"]]),
                                  ("org_tie_map", org_tie), ("institutions", inst)])),
        ("values", {"region": F["rulers"]["values"], "text": "%s admires what %s admires." % (P[region_id]["name"], F["rulers"]["name"]),
                    "by_settlement": {hid: F["rulers"]["id"]}}),
        ("clocks", S["clocks"]),
        ("situations", situations),
        ("encounter_tables", enc_tables),
        ("encounter_table_audit", audit),
        ("rumor_tables", rumor_tables),
        ("tables", []),
        ("terrain_by_ring", {str(k): v for k, v in terrain_by_ring.items()}),
        ("cases", []),
        ("bestiary", {"archetypes": bestiary_arch, "adversaries": sorted(a for a, e in WA.ADV.items() if e["archetype"] in bestiary_arch),
                      "note": "PR-09-1 builds any archetype x band x role x variant the bestiary does not list"}),
        ("storied_items", []),
        ("stock", stock),
        ("pregens", pregens),
        ("opening", opening),
        ("calendar", calendar),
    ])
    return region


def make_pregens(dice, S, peoples, nonhuman, keepers, main_keeper, acceptance, blds, hid, arcane_src, lvl, tier):
    """Four pregens (02.2.5): fighter, sneak, talker or scholar, worker of magic; one non-human. Attributes by 02.3.5's
    default placement (the livelihood's priority, Peaked shape; Typical rule unless 02.3.5's exception applies)."""
    roles = [("fighter", "orig.life.soldier"), ("sneak", "orig.life.thief"), ("talker", dice.pick(["orig.life.merchant", "orig.life.scholar", "orig.life.courtier"]))]
    magic = "orig.life.acolyte" if main_keeper["nature"] != "profane" else "orig.life.hedge_taught"
    roles.append(("magic", magic))
    nh = nonhuman[0]["origin"] if nonhuman else "orig.people.halfling"
    out = []
    used_anchor = set()
    shapes = ORIG["attribute_shapes"]
    for i, (role, life) in enumerate(roles):
        L = ORIGD[life]
        people = nh if i == 1 else "orig.people.human"
        pr = ORIGD[people]["attribute_rules"]
        typical = bool(pr.get("floors")) or bool(pr.get("fixed"))
        casting = {"orig.life.acolyte": "presence", "orig.life.hedge_taught": "wits", "orig.life.apprentice": "intellect"}.get(life)
        rule = "typical" if typical else "free"
        if typical and casting and pr.get("fixed", {}).get(casting) == -1:
            rule = "free"
        if rule == "typical":
            arr, floors, fixed = pr["shapes"]["peaked"], pr.get("floors", {}), pr.get("fixed", {})
        else:
            arr, floors, fixed = shapes["free"]["peaked"], {}, {}
        prio = L["defaults"]["attribute_priority"]
        best = None
        for perm in set(itertools.permutations(arr)):
            a = dict(zip(ATTRS, perm))
            if all(a[k] == v for k, v in fixed.items()) and all(a[k] >= v for k, v in floors.items()):
                key = tuple(a[x] for x in prio)
                if best is None or key > best[0]:
                    best = (key, a)
        attrs = best[1]
        name = person_name(dice, S["names"], people) if any(t["people"] == people for t in S["names"]) else person_name(dice, S["names"], "orig.people.human")
        anchor = [n for n in S["npcs"] if n["home"] in (blds["inn"], hid, blds.get("market"), blds["smithy"], blds.get("healer"), blds["gate"]) and n["id"] not in used_anchor][0]
        used_anchor.add(anchor["id"])
        d = dict(L["defaults"])
        if life == "orig.life.acolyte":
            # [revision: I-052] 05.7.4: a divine license must be one of the keeper's schools; healing when it keeps
            # healing, else its first school, with the livelihood's suggested technique of that school
            sch = "deed.divine.healing" if "deed.divine.healing" in main_keeper["schools"] else main_keeper["schools"][0]
            d["deep"] = [sch]
            d["technique"] = next(a for a in L["technique_suggestions"] if any(t.startswith(sch) for t in ABIL[a]["tags"]))
        rec = OrderedDict([("id", "pregen.%s.%s" % (S["_rs"], slug(name))), ("name", name), ("pronouns", dice.pick(["she/her", "he/him"])), ("role", role),
                           ("sentence", "%s, %s of %s." % (name, L["name"].lower(), S["_places"][hid]["name"])),
                           ("good_at", ", ".join(t.split(".")[-1].replace("_", " ") for t in d["deep"]) or "many things a little"),
                           ("people", people), ("rule", rule), ("shape", "peaked"), ("upbringing", d["upbringing"]), ("livelihood", life),
                           ("attributes", attrs), ("profile", d["profile"]), ("deep", d["deep"]), ("access", d["access"]), ("technique", d["technique"]),
                           ("drive", L["drive_seeds"][0]), ("aspiration", L["aspiration_seeds"][0]),
                           ("anchor_bond", {"kind": "friend", "npc": anchor["id"]}), ("thorn_bond", "open (02.9.8)"),
                           ("keeper", main_keeper["id"] if life == "orig.life.acolyte" else None),
                           ("acceptance", acceptance[0]["place"] if life == "orig.life.hedge_taught" else None),
                           ("birth", "drawn live when the pregen is picked (02.2.5 a)"), ("lifecycle", "provisional"), ("basis", ["02.2.5", "PR-02-9", "12.16.16"])])
        out.append(rec)
    return out


# ------------------------------------------------------------------------------------------- checks
def rule_refs_ok():
    bad = []
    for r in WS["requirements"]:
        for ref in r["rules"]:
            m = re.match(r"(PR-\d\d-\d+|T-\d\d-\d+|\d\d\.\d+(\.\d+)?)", ref)
            if not m:
                continue
            rid = m.group(1)
            ch = rid.split("-")[1] if rid.startswith(("PR-", "T-")) else rid[:2]
            if ch not in CH_TEXT or rid not in CH_TEXT[ch]:
                bad.append((r["id"], rid))
    return bad

CLUE_IDS = {pl["id"] for c in load("investigation.yaml")["cases"] for pl in c.get("placements", [])} | \
           {nd["id"] for c in load("investigation.yaml")["cases"] for nd in c.get("nodes", [])}

def secret_ids(reg):
    return {sc["fact"] for n in reg["npcs"] for sc in n.get("secrets") or []}

def check_seed(reg):
    """12.16.17: every requirement's check on one region record. Returns [(req_id, ok, note)]."""
    P = {p["id"]: p for p in reg["places"]}
    npcs = {n["id"]: n for n in reg["npcs"]}
    facs = {f["id"]: f for f in reg["factions"]["instances"]}
    clocks = {c["id"]: c for c in reg["clocks"]}
    keepers = {k["id"]: k for k in reg["keepers"]}
    sits = {s["id"]: s for s in reg["situations"]}
    ids = set(P) | set(npcs) | set(facs) | set(clocks) | set(keepers) | set(sits)
    hav = P[reg["region"]["haven"]]
    settle = [p for p in reg["places"] if p.get("settlement")]
    present = [p for p in reg["peoples"] if p["present"] != "absent"]
    res = []
    def ok(rid, cond, note=""):
        res.append((rid, bool(cond), note))
    for rq in WS["requirements"]:
        try:
            _check_one(rq, reg, ok, P, npcs, facs, clocks, keepers, sits, ids, hav, settle, present)
        except Exception as e:      # a missing or differently shaped key is a failed check, not a crash
            ok(rq["id"], False, "error: %s: %s" % (type(e).__name__, str(e)[:80]))
    return res

def _check_one(rq, reg, ok, P, npcs, facs, clocks, keepers, sits, ids, hav, settle, present):
        rid, c = rq["id"], rq["check"]
        if c == "canon_impossible":
            have = {c["id"] for c in (reg.get("canon") or {}).get("impossible", [])}
            ok(rid, reg["canon_impossible"] and all("ci." + d["key"] in have for d in DEF["canon_impossible"]), "%d entries" % len(reg["canon_impossible"]))
        elif c == "nonempty":
            v = reg
            for k in rq["key"].split("/"):
                v = v.get(k) if isinstance(v, dict) else None
            ok(rid, bool(v))
        elif c == "min_count":
            v = reg
            for k in rq["key"].split("/"):
                v = v.get(k) if isinstance(v, dict) else None
            ok(rid, v is not None and len(v) >= rq["min"], "%d" % (len(v) if v else 0))
        elif c == "tongues":
            ok(rid, all(t["license"] in LICS for t in reg["tongues"]["list"]) and any(t["license"] == "lic.lang.common" for t in reg["tongues"]["list"]), "%d tongues" % len(reg["tongues"]["list"]))
        elif c == "peoples":
            ok(rid, len(reg["peoples"]) == 8 and any(p["origin"] == "orig.people.human" and p["present"] in ("common", "uncommon") for p in reg["peoples"])
               and any(p["origin"] != "orig.people.human" for p in present), "%d present" % len(present))
        elif c == "names":
            tids = {t["id"] for t in reg["names"]}
            ok(rid, all(p.get("name_tables") and set(p["name_tables"]) <= tids for p in present) and all(t.get("given") for t in reg["names"]),
               "%d tables" % len(reg["names"]))
        elif c == "second_tongue":
            ok(rid, reg["tongues"]["second_tongue"] in LICS, reg["tongues"]["second_tongue"])
        elif c == "keepers":
            good = all(k["axes"] and k["schools"] and k["sign"] and k["faith"] in facs and all(a["axis"] in TAGS for a in k["axes"])
                       and k.get("nature") in ("sacred", "profane") for k in reg["keepers"])  # [revision: I-052] nature
            ok(rid, len(reg["keepers"]) >= 2 and good, "%d keepers" % len(reg["keepers"]))
        elif c == "acceptance":
            a = reg["places_of_acceptance"]
            ok(rid, a and all(x["place"] in P and x.get("schools") and x.get("contact") for x in a))
        elif c == "org_tie_map":
            orgs = {t for o in ORIG["origins"] for t in (o.get("org_tags") or []) if t.startswith("org.")}
            m = {x["org"]: x for x in reg["factions"]["org_tie_map"]}
            ok(rid, orgs <= set(m) and all(x["faction"] in facs or x["note"] for x in m.values()), "%d kinds" % len(m))
        elif c == "bond_placement":
            kinds = {b["kind"] for b in reg["bond_placement"]}
            want = {k["id"] for v in ORIG["bond_kinds"].values() for k in v}
            ok(rid, want <= kinds and all(b.get("where") for b in reg["bond_placement"]))
        elif c == "pregens":
            pg = reg["pregens"]
            rl = " | ".join(p["role"] for p in pg)
            roles = {k for k, ws in (("fighter", ["fighter"]), ("sneak", ["sneak"]), ("talker", ["talker", "scholar"]), ("magic", ["magic"])) if any(w in rl for w in ws)}
            nh = any(p["people"] != "orig.people.human" for p in pg)
            legal = True
            for p in pg:
                arr = sorted(p["attributes"].values(), reverse=True)
                shapes = [sorted(v, reverse=True) for s in ORIG["attribute_shapes"].values() for k, v in s.items() if k != "sum"]
                pr = ORIGD[p["people"]]["attribute_rules"]
                if p["rule"] == "typical":
                    legal &= all(p["attributes"][k] == v for k, v in pr.get("fixed", {}).items()) and all(p["attributes"][k] >= v for k, v in pr.get("floors", {}).items())
                legal &= arr in shapes and all(-1 <= v <= 3 for v in p["attributes"].values())
                anchor = p.get("anchor_bond") or p.get("anchor") or {}
                legal &= bool(p["drive"]) and bool(p["aspiration"]) and anchor.get("npc") in npcs and p["profile"] in {x["id"] for x in ORIG["profiles"]}
                legal &= p["upbringing"] in ORIGD and p["livelihood"] in ORIGD and p["people"] in ORIGD
                if p.get("keeper"):  # [revision: I-052] 05.7.4: every divine school the pregen holds is one its keeper keeps
                    kid = p["keeper"] if isinstance(p["keeper"], str) else (p["keeper"].get("id") or p["keeper"].get("keeper"))
                    kp = next((k for k in reg["keepers"] if k["id"] == kid), None)
                    legal &= kp is not None and all(t in kp["schools"] for t in p["deep"] + p["access"] if t.startswith("deed.divine"))
            ok(rid, len(pg) >= 4 and {"fighter", "sneak", "talker", "magic"} <= roles and nh and legal, "%d pregens" % len(pg))
        elif c == "inciting":
            inc = reg["opening"]["inciting"]
            ok(rid, (inc.get("text") or inc.get("moment")) and (inc.get("pairs_with") or inc.get("impetus")))
        elif c == "ref_place":
            ok(rid, reg["opening"]["start"]["place"] in P)
        elif c == "consecrated":
            ok(rid, any((p.get("facts") or {}).get("consecrated") for p in reg["places"]))
        elif c == "npc_homes":
            ok(rid, all(n["home"] in P for n in reg["npcs"]), "%d npcs" % len(npcs))
        elif c == "institutions":
            inst = reg["factions"]["institutions"]
            if isinstance(inst, dict):
                inst = [{"branch": k, "factions": v} for k, v in inst.items()]
            ok(rid, {"deed." + b for b in BRANCHES} <= {i["branch"] for i in inst}
               and all(all(f in facs for f in i["factions"]) for i in inst),
               "%d branches with an institution" % sum(1 for i in inst if i["factions"]))
        elif c == "resonance":
            ok(rid, any(p["resonance"] for p in reg["places"]))
        elif c == "magic_canon":
            m = reg["canon"]["magic"]
            ok(rid, len(m) == 8 and all(m.values()) or (len(m) == 8 and m["item_8_schools"] is not None))
        elif c == "rites_known":
            ok(rid, hav["settlement"]["rites_known"] and all(r in {x["id"] for x in RIT} for r in hav["settlement"]["rites_known"]))
        elif c == "components":
            comps = reg["stock"]["components"]
            ok(rid, comps and all("band" in c and c.get("name") for c in comps), "%d bands" % len(comps))
        elif c == "generic_or_table":
            ok(rid, True, "generic: %s" % rq.get("generic"))
        elif c == "fight_locations":
            ok(rid, len(reg["fight_locations"]) >= 2 and all(f["place"] in P and len(f["features"]) >= 2 for f in reg["fight_locations"]))
        elif c == "bestiary":
            b = reg["bestiary"]
            refs = (b.get("archetypes") or []) + (b.get("subset") or [])
            ok(rid, refs and all(a in ARCHD or a in WA.ADV for a in refs), "%d entries" % len(refs))
        elif c == "bargainer":
            f = {x["id"]: x for x in reg["canon"]["facts"]}["canon.default_bargainer"]
            ok(rid, f["value"] is None or f["value"] in keepers or f["value"] in ARCHD, str(f["value"]))
        elif c == "regrowth":
            ok(rid, any(x.get("id") in ("canon.regrowth", "ci.regrowth") for x in reg["canon"]["facts"] + reg["canon"]["impossible"]))
        elif c == "haven":
            ok(rid, hav["safe"] and hav["rest_site"] == "haven" and hav["place_kind"] == "settlement")
        elif c == "market":
            ok(rid, hav["settlement"].get("market", {}).get("common") and hav["settlement"].get("crafters")
               and all(isinstance(s["settlement"]["market"].get("common"), list) for s in settle if s["settlement"].get("market")))
        elif c == "transmutation":
            ok(rid, any(c_["id"] == "ci.transmutation" for c_ in reg["canon"]["impossible"]))
        elif c == "boons":
            ok(rid, all(f["boon_base"] for f in facs.values()))
        elif c == "places":
            need = ["place_kind", "band", "danger", "safe", "rest_site", "terrain", "climate", "nav_tier", "openness", "landmarks", "water_source",
                    "grazing", "encounter_table", "hazards", "resonance", "settlement_scope", "known", "discovered", "site", "state_log"]
            missing = [(p["id"], k) for p in reg["places"] for k in need if k not in p]
            areas_ok = all(p["band"] and p["danger"] and p["nav_tier"] and p["encounter_table"] for p in reg["places"] if p["place_kind"] == "area")
            ok(rid, not missing and areas_ok, "%d places" % len(P))
        elif c == "links":
            bad = [(p["id"], l["to"]) for p in reg["places"] for l in p["links"] if l["to"] not in P or not any(b["to"] == p["id"] for b in P[l["to"]]["links"])]
            # every area reachable from the haven
            seen, todo = set(), [reg["region"]["haven"]]
            while todo:
                x = todo.pop()
                if x in seen: continue
                seen.add(x); todo += [l["to"] for l in P[x]["links"]]
            unreach = [p["id"] for p in reg["places"] if p["place_kind"] in ("area", "site") and p["id"] not in seen]
            ok(rid, not bad and not unreach, "%d routes; unreachable %d" % (len({l["route"] for p in reg["places"] for l in p["links"]}), len(unreach)))
        elif c == "rings":
            rr = reg["region"]["rings"]
            ok(rid, [r["ring"] for r in rr] == [0, 1, 2, 3, 4, 5] and all(P[a]["band"] in TRAVEL["rings"][r["ring"]]["home_band"] for r in rr[1:] for a in r["areas"])
               and any(P[a]["band"] == 5 for a in rr[5]["areas"]))   # [revision: I-084] 12.16.8: a home-5 area in ring 5
        elif c == "encounter_tables":
            au = reg["encounter_table_audit"]
            # re-audit every regional table here (PR-10-8), whatever audit the region stored
            tabs = {t["id"]: t for t in reg["encounter_tables"]}
            res_t = {tid: WA.audit_table(t["threat"], t["home_band"], t.get("non_threat"), deadly_only=t.get("danger") == "deadly")[0] for tid, t in tabs.items()}
            areas = [p for p in P.values() if p["place_kind"] == "area"]
            covered = all(p["encounter_table"] in tabs or str(p["encounter_table"]).startswith("tbl.10.enc.") for p in areas)
            ok(rid, tabs and covered and all(res_t.values()), "%d tables, %d pass PR-10-8 (re-audited)" % (len(tabs), sum(res_t.values())))
        elif c == "sites":
            ss = [p for p in reg["places"] if p["site"]]
            okk = all(s["site"]["theme"] in THEMES and s["site"]["domain"] in DOMAINS and 1 <= s["site"]["band"] <= 5 and s["site"]["size"] and s["site"]["objective"] for s in ss)
            tabs = [WA.audit_table(s["site"]["denizen_table"], s["site"]["band"])[0] for s in ss if s["site"].get("denizen_table")]
            ok(rid, ss and okk and all(tabs), "%d sites, %d stored denizen tables pass PR-10-8 (the rest are built at entry, PR-10-6)" % (len(ss), sum(tabs)))
        elif c == "rest_sites":
            ok(rid, any(p["rest_site"] == "haven" for p in reg["places"]) and all(p["rest_site"] for p in reg["places"] if p["place_kind"] == "area"))
        elif c == "climate":
            ok(rid, reg["region"]["climate"] in CLIMATES)
        elif c == "factions":
            full = [f for f in facs.values() if f["full"]]
            shape = all(sum(f["ratings"].values()) == 4 + 2 * f["tier"] and f["goal"]["clock"] in clocks and f["linchpins"]
                        and all({"dies", "captured", "turned", "exposed"} <= set(l["fates"]) <= {"dies", "captured", "turned", "exposed", "deposed"} and l["sealed"] for l in f["linchpins"]) for f in facs.values())   # [revision: I-081] deposed optional
            running = sum(1 for f in full if clocks[f["goal"]["clock"]]["filled"] > 0)
            ok(rid, len(full) >= 3 and shape and running >= 3, "%d factions, %d full, %d running" % (len(facs), len(full), running))
        elif c == "petty_factions":
            # [revision: I-070] 11.3.16: a petty faction's goal is a petty_goals kind, local, on the 6-segment clock
            kinds = {k["kind"] for k in FAC["petty_goals"]["kinds"]}
            pet = [f for f in facs.values() if not f["full"]]
            bad = [f["id"] for f in pet if not (f["goal"]["kind"] in kinds and f["goal"]["scope"] == "local"
                   and clocks[f["goal"]["clock"]]["segments"] == FAC["petty_goals"]["clock"]["segments"]
                   and ("{" not in f["goal"]["text"]) and (f["goal"]["kind"] not in ("take", "feud") or f["goal"]["target"] in ids))]
            ok(rid, not bad, "%d petty%s" % (len(pet), (", bad " + ", ".join(bad)) if bad else ""))
        elif c == "calendar":
            cal = reg["calendar"]
            ok(rid, len(cal["months"]) == 12 and len(cal["day_names"]) == 7 and cal["era"]["name"] and len(cal["festivals"]) == 4)
        elif c == "values":
            ok(rid, reg["values"]["region"] and reg["values"]["by_settlement"])
        elif c == "situations":
            def sit_ok(s):
                tl = s.get("timeline") or s.get("default_timeline")
                return bool(tl) and all(x.get("trace") for x in tl) and (s["template"] in SITT or s["template"] is None) \
                    and (s.get("region") or s.get("place")) in P
            ok(rid, len(reg["situations"]) >= 2 and all(sit_ok(s) for s in reg["situations"]),
               "%d" % len(reg["situations"]))
        elif c == "rumors":
            rows = [r for t in reg["rumor_tables"] for r in t["results"]]
            xids = ids | secret_ids(reg) | set(reg.get("cases") or []) | {o["id"] for o in reg.get("objects") or []} | CLUE_IDS | set(WA.ADV)
            bad = [r["points_to"] for r in rows if str(r["points_to"]).split(" ")[0] not in xids]
            ok(rid, rows and not bad and all(r["truth"] in ("true", "partial", "false") for r in rows),
               "%d rumors (%s)%s" % (len(rows), dict(Counter(r["truth"] for r in rows)), ("; not a record: %s" % bad) if bad else ""))
        elif c == "npcs":
            # [revision: I-053] every want's verb takes its object; no refusal row whose not_for matches a role tag
            # [revision: I-059] every NPC carries competence and licenses as data, licenses real ids
            VR = {r["result"]: r for r in ORAC["tbl.npc_want_verb"]["results"]}
            OR = {r["result"]: int(r["range"]) for r in ORAC["tbl.npc_want_object"]["results"]}
            RR = {r.get("kind"): r for r in ORAC["tbl.npc_refusal"]["results"]}
            def want_ok(w):
                v, _, o = w["text"].partition(" ")
                return v not in VR or o not in OR or OR[o] in VR[v].get("takes", [OR[o]])
            def ref_ok(n):
                return all(not any(t == x or t.startswith(x + ".") for x in RR.get(r["kind"], {}).get("not_for", []) for t in n.get("role_tags", []))
                           for r in n.get("refusals", []))
            KOF = {k.get("faith"): k for k in reg["keepers"]}
            div_ok = all("deed.divine.%s" % l["id"].rsplit("_", 1)[-1] in {s for m in n["member_of"] if m in KOF for s in KOF[m]["schools"]}
                         for n in npcs.values() for l in n.get("licenses", []) if l["id"].startswith("lic.training.divine_"))  # I-052
            data_ok = div_ok and all(isinstance(n.get("competence"), list) and isinstance(n.get("licenses"), list) and all(l["id"] in LICS for l in n["licenses"])
                          for n in npcs.values())
            bad = [n["id"] for n in npcs.values() if not (all(want_ok(w) for w in n.get("wants", [])) and ref_ok(n))]
            ok(rid, len(npcs) >= 8 and all(all(m in facs for m in n["member_of"]) for n in npcs.values()) and data_ok and not bad,
               "%d npcs%s" % (len(npcs), ("; misfit wants/refusals: %s" % bad[:3]) if bad else ("" if data_ok else "; competence/licenses missing")))
        elif c == "opening":
            o = reg["opening"]
            xids = ids | secret_ids(reg) | set(reg.get("cases") or []) | CLUE_IDS
            tg = [t for l in o["leads"] for t in (l["points_to"] if isinstance(l["points_to"], list) else [l["points_to"]])]
            tg = [str(t).split(" ")[0] for t in tg]
            ok(rid, o["start"]["place"] in P and len(o["leads"]) >= 3 and all(t in xids for t in tg) and len(set(tg)) >= 3)
        elif c == "settlement_tiers":
            ok(rid, all(s["settlement"]["tier"] in ("camp", "village", "town", "city") for s in settle))
        elif c == "teachers":
            t = hav["settlement"]["teachers"]
            # [revision: I-059] 15.11.1 MENTOR: the teacher's record holds the target (training licenses at expert)
            held = lambda x: any(l["id"] == x["target"] and (l.get("grade") == "expert" or not x["target"].startswith("lic.training."))
                                 for l in npcs[x["npc"]].get("licenses", [])) if x["npc"] in npcs else False
            ok(rid, t and all(x["target"] in LICS and x["npc"] in npcs and held(x) for x in t), "%d teachings" % len(t))
        elif c == "sentries":
            ok(rid, hav["settlement"].get("sentry_floors"))
        elif c == "present":
            ok(rid, all(isinstance(s["settlement"].get("lifestyle_overrides", []), list) for s in settle))
        elif c == "hire":
            h = hav["settlement"]["hire"]
            ok(rid, h["roles"] and all(r in COMP for r in h["roles"]) and h["max_band"] in (1, 2, 3))
        elif c == "recruits":
            ok(rid, any(n["recruit"] for n in npcs.values()))
        elif c == "powers":
            # [revision: I-083] one power per ring-4 area at band 4 and per ring-5 area at band 5, each keeping a truth
            rings = {r["ring"]: r["areas"] for r in reg["region"]["rings"]}
            pw = [n for n in npcs.values() if n.get("power")]
            want = {a: r for r in (4, 5) for a in rings.get(r, [])}
            okk = (sorted(n["home"] for n in pw) == sorted(want) and all(n["band"] == want[n["home"]] and (n.get("keeps") or {}).get("text") for n in pw))
            ok(rid, okk, "%d powers, bands %s" % (len(pw), sorted(n["band"] for n in pw)))
        else:
            ok(rid, False, "unknown check " + c)


# ------------------------------------------------------------------------------- a pre-made seed (12.16.18)
def load_premade(path):
    """A pre-made region file (e.g. data/region_thallen.yaml) as the seed check sees it: its owner-block content
    (factions, calendar names) gathered from the shared files under the owner named in the region file."""
    reg = yaml.safe_load(open(path, encoding="utf-8"))
    reg = copy.deepcopy(reg)
    owner = "13"
    inst = [e for b in FAC["blocks"] if str(b["owner"]) == owner for e in b["entries"]]
    reg["factions"] = dict(reg["factions"], instances=inst)
    clocks = list(reg.get("clocks") or [])
    for f in inst:
        c = f["goal"].get("clock")
        if isinstance(c, dict):
            cid = c.get("id") or "clk.%s.goal" % f["id"]
            clocks.append(dict(c, id=cid))
            f["goal"] = dict(f["goal"], clock=cid)
    reg["clocks"] = clocks
    calb = [e for b in CAL.get("blocks") or [] if str(b["owner"]) == owner for e in b["entries"]]
    if calb:
        e = calb[0]
        reg["calendar"] = {"months": [m["name"] if isinstance(m, dict) else m for m in (e.get("months") or CAL["months"])],
                           "day_names": e.get("day_names") or CAL["day_names"], "era": e.get("era") or CAL["era"],
                           "festivals": [f for f in (e.get("festivals") or CAL["festivals"]) if str(f.get("id", "")).startswith("fest.quarter")] or e.get("festivals")}
    return reg

# ------------------------------------------------------------------- seed packs [revision: R2-D] [DL-12-61; DL-15-38]
# 12.16.9 looks, furniture and exits; 12.16.11 knowledge packs and stances; 12.16.16 documents and the reduced
# case (PR-15-6, 15.9.4 reduced profile). A pass after build_seed on streams keyed by the seed and the entity id,
# so packing never moves a draw of the seed itself (the engine port's parity holds) and a pre-made seed can be
# packed too. Checks: world_seed.yaml#pack_requirements (check_packs).
import hashlib
SOCD, INVD = load("social.yaml"), load("investigation.yaml")
CK, RCASE = SOCD["common_knowledge"], INVD["reduced_case"]
LOOK, FURN, DOCT, KPACK = (TAB[t] for t in ("tbl.12.seed.place_look", "tbl.12.seed.furniture", "tbl.12.seed.document", "tbl.12.seed.knowledge_pack"))

def keyed(seed, *parts):
    """A dice stream keyed by the seed and an entity id (C 2.2: a generated answer never depends on draw order)."""
    return Dice(int(hashlib.sha256("|".join(map(str, (seed,) + parts)).encode()).hexdigest()[:15], 16))

def place_type(p):
    if p["place_kind"] == "building":
        return p["id"].rsplit(".", 1)[1]
    if p["place_kind"] in ("settlement", "landmark"):
        return p["place_kind"]
    t = ((p.get("terrain") or ["x"])[0]).split(".")
    return t[1] if len(t) > 1 else "default"

def role_key(npc):
    """social.yaml#common_knowledge.rule: first word of the role, else the first role_map pattern, else other."""
    txt = (npc.get("role") or "").lower()
    w = txt.split()[0] if txt else "other"
    if w in CK["by_role"]:
        return w
    return next((m["role"] for m in CK["role_map"] if m["pattern"] in txt), "other")

def in_haven(reg, pid):
    P = {p["id"]: p for p in reg["places"]}
    hav = reg["region"]["haven"]
    return pid == hav or (pid in P and P[pid].get("parent") == hav)

def pick_n(d, rows, n):
    out = []
    while len(out) < n:
        i = d.d(len(rows)) - 1
        while rows[i] in out:
            i = (i + 1) % len(rows)
        out.append(rows[i])
    return out

def pack_places(reg, seed):
    P = {p["id"]: p for p in reg["places"]}
    regional = next((t for t in reg.get("tables") or [] if str(t.get("id", "")).endswith(".furnishings")), None)
    for p in reg["places"]:
        if p["place_kind"] == "region":
            continue
        k, d = place_type(p), keyed(seed, p["id"], "place")
        p["look"] = d.pick(LOOK["by_kind"].get(k) or LOOK["by_kind"]["default"]).replace("{name}", p["name"])
        items = pick_n(d, FURN["by_kind"].get(k) or FURN["by_kind"]["default"], d.d(3) + 1)
        if regional and p["place_kind"] == "building":
            items[-1] = by_range(regional["results"], d.die(regional["die"]))["result"]
        p["furniture"] = items
        if p["links"]:
            p["exits"] = [l["to"] for l in p["links"]]
        elif p["place_kind"] == "building":
            sib = [q for q in P if P[q].get("parent") == p["parent"] and P[q]["place_kind"] == "building" and q != p["id"]]
            p["exits"] = [p["parent"]] + sib[:2]
        else:
            p["exits"] = [p["parent"]] if p.get("parent") in P else []

def walk_on(reg, seed, tag, role, home):
    """12.11.1 walk-on, minimal (role, name from the seed's own tables, home); written to the store's npcs."""
    d = keyed(seed, "walk_on", tag)
    t = d.pick(reg["names"])
    nm = "%s %s" % (by_range(t["given"], d.d(20))["result"], by_range(t.get("family") or t["epithet"], d.d(12))["result"])
    n = OrderedDict([("id", "npc.%s" % slug(nm + " " + tag)), ("name", nm), ("role", role), ("depth", "walk_on"), ("home", home),
                     ("member_of", []), ("kind", "npc"), ("exists", "exists"), ("knowledge", []), ("basis", ["12.11.1", "PR-15-6"])])
    reg.setdefault("walk_ons", []).append(n)      # entities of the store; kept apart from the seed cast (12.16.11)
    return n

def lead_holder_place(reg, target):
    """Where a lead target is found: a place itself; a situation's region; a clock's faction seat (its head's home)."""
    P = {p["id"]: p for p in reg["places"]}
    if target in P:
        return target
    sit = next((s for s in reg["situations"] if s["id"] == target), None)
    if sit and sit.get("region") in P:
        return sit["region"]
    for f in reg["factions"]["instances"]:
        if target in (f["id"], f["goal"].get("clock")):
            head = next((n for n in reg["npcs"] if f["id"] in (n.get("member_of") or []) and n["role"].startswith("head of")), None)
            if head:
                return head["home"]
    return reg["region"]["haven"]

def fill_doc(row, **kw):
    t = row["text"]
    for k, v in kw.items():
        t = t.replace("{%s}" % k, str(v))
    return t

def make_document(reg, seed, tag, option, at, issuer, contact, target_words):
    d = keyed(seed, "doc", tag)
    P = {p["id"]: p for p in reg["places"]}
    row = next(r for r in DOCT["results"] if r["option"] == option)
    flds = {k: d.pick(v) for k, v in DOCT["fields"].items()}
    text = fill_doc(row, issuer=issuer, haven=P[reg["region"]["haven"]]["name"], year=reg["calendar"]["opening_date"].split(",")[-1].strip(),
                    contact=contact[0], contact_place=contact[1], target=target_words, **flds)
    doc = OrderedDict([("id", "doc.%s" % tag), ("kind", "document"), ("option", option), ("at", at), ("text", text), ("table", DOCT["id"])])
    reg.setdefault("documents", []).append(doc)
    return doc

def cast_pick(d, pool, weight):
    """social.yaml#cast fill: weighted by fit over the gated pool; None when the pool is empty."""
    pool = [(n, weight(n)) for n in pool]
    pool = [(n, w) for n, w in pool if w > 0]
    return d.weighted(pool) if pool else None

def reduced_case(reg, seed, option, place, lead_target, tag="incident"):
    """PR-15-6, reduced profile (investigation.yaml#reduced_case): 2 necessary nodes, 3 placements each, 1 reserve
    each, the first core placement held at `place`. Returns the case record (sealed)."""
    d = keyed(seed, "case", tag, option)
    P = {p["id"]: p for p in reg["places"]}
    hav = reg["region"]["haven"]
    sub = RCASE["subjects"][option]
    blds = [p["id"] for p in reg["places"] if p.get("parent") == hav and p["place_kind"] == "building"]
    locals_ = [n for n in reg["npcs"] if in_haven(reg, n["home"]) and n.get("depth") != "walk_on"]
    # 1. solution: the subject (a story role), cast first, else generated (12.11.1); never chosen
    if sub["kind"] == "person":
        roles = sub.get("cast") or []
        subj = cast_pick(d, locals_, lambda n: 3 if role_key(n) in roles else 0) if roles else None
        if subj is None:
            role = {"missing": lambda: ["child", "child", "child", "elder", "elder", "priest"][d.d(6) - 1],
                    "refugees": lambda: "traveler"}.get(option, lambda: "traveler")()
            subj = walk_on(reg, seed, "%s_subject" % tag, role, place if option != "refugees" else place)
        subject = {"id": subj["id"], "role": sub["role"], "words": subj["name"]}
    else:
        fac = {f["id"].rsplit(".", 1)[1]: f["name"] for f in reg["factions"]["instances"]}
        temple = next((p["name"] for p in reg["places"] if p["id"] in (hav + ".temple", hav + ".shrine")), "the shrine")
        words = {"alarm": "a war-band of %s" % fac.get("threat", "the enemy"), "omen": "a sign of %s" % reg["situations"][0]["title"].lower(),
                 "theft": "the relic of %s from %s" % (reg["keepers"][0]["name"].split(",")[0], temple)}[option]
        subject = {"id": "%s.%s.subject" % (tag, option), "role": sub["role"], "words": words}
    used = {subject["id"]}
    # 2-3. placements
    reporter = next((n for n in reg["npcs"] if n["home"] == place and n["id"] not in used and n.get("depth") != "walk_on"), None) \
        or walk_on(reg, seed, "%s_reporter" % tag, "reporter", place)
    used.add(reporter["id"])
    witness = cast_pick(d, [n for n in locals_ if n["id"] not in used and n["home"] != place], lambda n: 1 + (2 if n["home"] in blds else 0)) \
        or walk_on(reg, seed, "%s_witness" % tag, "witness", next(b for b in blds if b != place))
    used.add(witness["id"])
    third = next(b for b in blds + [hav] if b not in (place, witness["home"]))
    issuer = next((f["name"] for f in reg["factions"]["instances"] if f["id"].endswith(".rulers")), "the rulers")
    doc = make_document(reg, seed, "%s_notice" % tag, "bounty" if sub["kind"] == "person" else "warning", third, issuer,
                        (reporter["name"], P[place]["name"]), subject["words"])
    way = lead_holder_place(reg, lead_target)
    seer = cast_pick(d, [n for n in locals_ if n["id"] not in used and n["home"] != way], lambda n: 3 if place_type(P[n["home"]]) in ("gate", "inn", "market") else 1) \
        or walk_on(reg, seed, "%s_seer" % tag, "witness", next(b for b in blds if b != place))
    used.add(seer["id"])
    cid = "case.%s.%s" % (tag, option)
    def pl(node, i, holder, hk, method, access, at, content):
        return {"id": "clu.%s.n%d.p%d" % (cid.split(".", 1)[1], node, i), "holder": holder, "holder_kind": hk, "method": method,
                "access": access, "at": at, "content": content, "status": "unfound", "sealed": True}
    n1 = "%s: %s" % (subject["role"], subject["words"])
    n2 = "the way on: toward %s" % P[way]["name"]
    nodes = [
        {"id": "clu.%s.n1" % cid.split(".", 1)[1], "fact": n1, "necessary": True, "points_to": ["clu.%s.n2" % cid.split(".", 1)[1]],
         "placements": [pl(1, 1, reporter["id"], "person", "inquiry", "core", place, n1),
                        pl(1, 2, witness["id"], "person", "inquiry", "rolled", witness["home"], n1),
                        pl(1, 3, doc["id"], "document", "search", "rolled", third, n1)],
         "reserve": [pl(1, 9, "reserve.%s.n1" % tag, "person", "inquiry", "core", None, n1)]},
        {"id": "clu.%s.n2" % cid.split(".", 1)[1], "fact": n2, "necessary": True, "points_to": [],
         "placements": [pl(2, 1, way, "place", "search", "core", way, n2),
                        pl(2, 2, seer["id"], "person", "inquiry", "rolled", seer["home"], n2),
                        pl(2, 3, "obj.%s.left" % tag, "object", "search", "rolled", place if place != way else third, n2)],
         "reserve": [pl(2, 9, "reserve.%s.n2" % tag, "person", "inquiry", "core", None, n2)]},
    ]
    case = OrderedDict([("id", cid), ("profile", "reduced"), ("trigger", tag), ("option", option), ("opening_place", place),
                        ("solution", {"subject": subject, "leads_to": lead_target, "sealed": True}), ("nodes", nodes),
                        ("fallbacks", [{"trigger": "stalled", "form": "tbl.15.fallback_form", "delivers": "the core placement of an unfound necessary node"}]),
                        ("audit", "h.15.placement_audit"), ("basis", ["PR-15-6", "15.9.4", "12.16.16"])])
    reg["seed_cases"] = [c for c in reg.get("seed_cases") or [] if c["id"] != cid] + [case]   # the records; reg["cases"] lists ids
    reg["cases"] = [c for c in reg.get("cases") or [] if c != cid] + [cid]
    return case

def validate_case(case):
    """15.9.4 with investigation.yaml#reduced_case's numbers. Returns the failures (empty = valid)."""
    v, bad = RCASE["per_necessary_node"], []
    nec = [n for n in case["nodes"] if n["necessary"]]
    if len(nec) != RCASE["necessary_nodes"]:
        bad.append("nodes %d" % len(nec))
    for n in nec:
        pls = n["placements"]
        for what, val, lo in (("placements", len(pls), v["min_placements"]), ("holder kinds", len({p["holder_kind"] for p in pls}), v["min_holder_kinds"]),
                              ("methods", len({p["method"] for p in pls}), v["min_method_kinds"]), ("core", sum(p["access"] == "core" for p in pls), v["min_core"]),
                              ("places", len({p["at"] for p in pls}), v["min_places"]), ("reserve", len(n["reserve"]), v["reserve"])):
            if val < lo:
                bad.append("%s %s %d < %d" % (n["id"], what, val, lo))
    if not any(p["access"] == "core" and p["at"] == case["opening_place"] for p in nec[0]["placements"]):
        bad.append("no core placement at the opening place")
    if len(case["fallbacks"]) < RCASE["per_case"]["min_fallbacks"]:
        bad.append("fallbacks")
    return bad

def pack_npcs(reg, seed):
    P = {p["id"]: p for p in reg["places"]}
    hav = reg["region"]["haven"]
    case = next((c for c in reg.get("seed_cases") or [] if c["trigger"] == "incident"), None)
    secret = {case["solution"]["subject"]["id"]} if case else set()
    holders = {p["holder"] for n in case["nodes"] for p in n["placements"]} if case else set()
    near = [p for p in reg["places"] if p["place_kind"] in ("area", "site", "landmark") and p.get("ring") in (1, 2)]
    routes = P[hav]["links"]
    facs = [f for f in reg["factions"]["instances"] if not f["id"].endswith(".threat")]
    keeper = reg["keepers"][0]["name"].split(",")[0]
    rumors = [(t["id"], r["range"]) for t in reg["rumor_tables"] for r in t["results"]]
    cast = [n for n in reg["npcs"] if n.get("depth") != "walk_on"]
    named = [n for n in cast if n["id"] not in secret]          # a pack fact never names the case's solution
    for n in cast:
        d = keyed(seed, n["id"], "pack")
        ring = P[n["home"]]["ring"] if n["home"] in P else 0
        others = [m for m in named if m is not n and (P[m["home"]]["ring"] if m["home"] in P else 0) == ring] or [m for m in named if m is not n]
        def fill(row):
            rt = d.pick(routes) if routes else None
            return (row.replace("{place}", (P[rt["to"]]["name"] if rt and "{watches}" in row else d.pick(near)["name"]) if near else P[hav]["name"])
                       .replace("{watches}", num_words(rt["travel_watches"]) if rt else "a few").replace("{route_kind}", rt["route_kind"] if rt else "track")
                       .replace("{other}", d.pick(others)["name"]).replace("{faction}", d.pick(facs)["name"]).replace("{keeper}", keeper)
                       .replace("{haven}", P[hav]["name"]))
        own = []
        for slot, topic in (("trade", d.pick(CK["by_role"][role_key(n)])), ("local", d.pick(["local_news", "folk"]))):
            own.append({"fact": "kn.%s.%s" % (n["id"].split(".", 1)[1], slot), "slot": slot, "topic": topic,
                        "text": fill(d.pick(KPACK["by_topic"][topic])), "how": "seed", "tier": "T1"})
        other = d.pick(others)
        own.append({"fact": "kn.%s.tie" % n["id"].split(".", 1)[1], "slot": "tie", "topic": "folk", "about": other["id"],
                    "text": d.pick(KPACK["ties"]).replace("{other}", other["name"]).replace("{haven}", P[hav]["name"]), "how": "seed", "tier": "T1"})
        if d.d(6) >= 4 and rumors:
            rid, rng = d.pick(rumors)
            own.append({"fact": "kn.%s.rumor" % n["id"].split(".", 1)[1], "slot": "rumor", "topic": "local_news", "rumor": {"table": rid, "range": rng},
                        "truth": "sealed", "how": "seed"})
        n["knowledge"] = own
        st = KPACK["stance"]
        if n["id"] in holders:
            n["stance"] = {"toward": "incident", "stance": "helps", "why": "holds a placement of the incident's case"}
        elif any(m.endswith(".threat") for m in n.get("member_of") or []):
            n["stance"] = {"toward": "incident", "stance": "hinders", "why": "of the threat faction"}
        else:
            r = by_range(st["results"], d.die(st["die"]))
            n["stance"] = {"toward": "incident", "stance": r["stance"], "why": r["gist"]}

def seed_packs(reg, seed):
    """The seed-pack pass: places, the incident's reduced case (12.16.16), documents, then NPC packs."""
    pack_places(reg, seed)
    o = reg["opening"]
    case = reduced_case(reg, seed, o["inciting"]["option"], o["start"]["place"], o["leads"][0]["points_to"])
    o["case"] = case["id"]
    # the hire lead (12.16.16's third lead) points to a hire notice whose text names who to see and where
    P = {p["id"]: p for p in reg["places"]}
    hav = reg["region"]["haven"]
    for i, ld in enumerate(o["leads"]):
        fac = next((f for f in reg["factions"]["instances"] if ld["points_to"] == f["goal"].get("clock")), None)
        if fac and "hiring" in ld["lead"]:
            head = next(n for n in reg["npcs"] if fac["id"] in (n.get("member_of") or []) and n["role"].startswith("head of"))
            post = next((p for p in (hav + ".gate", hav + ".market", hav + ".inn") if p in P), hav)
            doc = make_document(reg, seed, "lead_%d" % (i + 1), "hire", post, fac["name"], (head["name"], P[head["home"]]["name"] if head["home"] in P else P[hav]["name"]), "")
            ld["document"], ld["names"] = doc["id"], head["name"]
    d = keyed(seed, "documents")
    opt = by_range(DOCT["results"], d.d(3) + 1)["option"]          # one more: warning, charter or bounty
    rul = next(f for f in reg["factions"]["instances"] if f["id"].endswith(".rulers"))
    capt = next((n for n in reg["npcs"] if n["home"] == hav + ".gate" and n.get("depth") != "walk_on"), None)
    site = next(p for p in reg["places"] if p["place_kind"] == "site" and p.get("ring") == 1)
    post = next((p for p in DOCT["results"] if p["option"] == opt))["posted_at"]
    at = next((hav + "." + k for k in post if hav + "." + k in P), hav)
    make_document(reg, seed, "notice", opt, at, rul["name"], (capt["name"] if capt else "the watch", P[hav + ".gate"]["name"] if hav + ".gate" in P else P[hav]["name"]), site["name"])
    pack_npcs(reg, seed)
    return reg

def check_packs(reg):
    """world_seed.yaml#pack_requirements on a packed region. Returns [(id, ok, note)]."""
    places = [p for p in reg["places"] if p["place_kind"] != "region"]
    cast = [n for n in reg["npcs"] if n.get("depth") != "walk_on" and n.get("knowledge") is not None and "stance" in n]
    cast_all = [n for n in reg["npcs"] if n.get("depth") != "walk_on"]
    case = next((c for c in reg.get("seed_cases") or [] if c["trigger"] == "incident"), None)
    docs = reg.get("documents") or []
    lead_docs = [(ld, next((x for x in docs if x["id"] == ld["document"]), None)) for ld in reg["opening"]["leads"] if ld.get("document")]
    out = []
    for rq in WS["pack_requirements"]:
        c = rq["check"]
        if c == "looks":
            bad = [p["id"] for p in places if not p.get("look")]
        elif c == "furniture":
            bad = [p["id"] for p in places if not 2 <= len(p.get("furniture") or []) <= 4]
        elif c == "exits":
            bad = [p["id"] for p in places if not p.get("exits")]
        elif c == "knowledge":
            bad = [n["id"] for n in cast_all if not (2 <= len([k for k in n.get("knowledge") or [] if k["slot"] in ("trade", "local", "tie", "rumor")]) <= 4
                                                    and {"trade", "local", "tie"} <= {k["slot"] for k in n.get("knowledge") or []})]
            sub = case["solution"]["subject"]["id"] if case else None
            bad += [n["id"] + " names the subject" for n in cast_all for k in n.get("knowledge") or [] if sub and k.get("about") == sub]
        elif c == "stance":
            bad = [n["id"] for n in cast_all if not (n.get("stance") or {}).get("stance")]
        elif c == "documents":
            bad = [x["id"] for x in docs if not x.get("text") or "{" in x["text"]] + \
                  [ld["lead"][:30] for ld, x in lead_docs if not x or ld["names"] not in x["text"]]
        elif c == "reduced_case":
            bad = ["no incident case"] if not case else validate_case(case)
        else:
            bad = ["unknown check " + c]
        out.append((rq["id"], not bad, "%d places, %d cast, %d documents%s" % (len(places), len(cast_all), len(docs), ("; " + ", ".join(bad[:3])) if bad else "")))
    return out

# --------------------------------------------------------------------------------------------- main
def dump(reg):
    def conv(x):
        if isinstance(x, OrderedDict) or isinstance(x, dict):
            return {k: conv(v) for k, v in x.items()}
        if isinstance(x, list):
            return [conv(v) for v in x]
        return x
    head = ("# _process/simulation/12-world-seed-example.yaml -- a world seed (12.16) generated by 12-world-seed.py, seed %d, oracle\n"
            "# mode: every question answered by the engine. A region record of the shape of data/region_*.yaml (SCHEMAS.md#region_yaml).\n"
            "# Verification's playtests use this world (FINISH-PLAN.md). Regenerate: python 12-world-seed.py --emit 12-world-seed-example.yaml\n"
            "# [revision: I-028]\n\n" % reg["seed"]["seed"])
    return head + yaml.safe_dump(conv(reg), sort_keys=False, allow_unicode=True, width=130, default_flow_style=None)

def report(reg, verbose=True):
    res = check_seed(reg) + (check_packs(reg) if "documents" in reg else [])   # [revision: R2-D] pack checks
    fails = [r for r in res if not r[1]]
    if verbose:
        R_ = reg["region"]
        print("seed %s (%s mode): %s, haven %s; wound %s; climate %s" % (reg["seed"]["seed"], reg["seed"]["mode"], R_["name"],
              next(p["name"] for p in reg["places"] if p["id"] == R_["haven"]), R_["wound"], R_["climate"]))
        print("  keepers: %s" % "; ".join(k["name"] for k in reg["keepers"]))
        print("  peoples: %s" % ", ".join("%s %s" % (p["origin"].split(".")[-1], p["present"]) for p in reg["peoples"]))
        print("  factions: %s" % "; ".join("%s (tier %d%s, goal %d/%d)" % (f["name"], f["tier"], ", full" if f["full"] else "",
              next(c["filled"] for c in reg["clocks"] if c["id"] == f["goal"]["clock"]), next(c["segments"] for c in reg["clocks"] if c["id"] == f["goal"]["clock"]))
              for f in reg["factions"]["instances"]))
        print("  places %d (areas %d, sites %d), npcs %d, encounter tables %d, rumors %d, pregens %d" % (
            len(reg["places"]), sum(1 for p in reg["places"] if p["place_kind"] == "area"), sum(1 for p in reg["places"] if p["site"]),
            len(reg["npcs"]), len(reg["encounter_tables"]), sum(len(t["results"]) for t in reg["rumor_tables"]), len(reg["pregens"])))
        print("  encounter tables (PR-10-8, built by PR-10-10):")
        for tid, a in reg["encounter_table_audit"].items():
            print("    %-46s home %d  %-40s fair-or-easier %2d/20  %s  pool %d" % (tid, next(t["home_band"] for t in reg["encounter_tables"] if t["id"] == tid),
                  " ".join("%s:%d" % (k, a["words"][k]) for k in WA.WORDS if a["words"].get(k)), a["fair_or_easier"], "PASS" if a["pass"] else "FAIL", a["pool_size"]))
        print("  requirements (T-12-16): %d checked, %d pass" % (len(res), len(res) - len(fails)))
        for rid, okk, note in res:
            print("    %-4s %-32s %s" % ("ok" if okk else "FAIL", rid, note))
    return fails

def render_tables():
    """T-12-15 and T-12-16 for chapter 12, rendered from world_seed.yaml (python 12-world-seed.py --tables)."""
    out = ["**T-12-15 The world seed's steps and questions** (`world_seed.yaml#steps`, `#questions`; 12.16.3).", "",
           "| Step | Rule | Questions (player or oracle) | Writes |", "|---|---|---|---|"]
    for st in WS["steps"]:
        qs = []
        for q in st["questions"]:
            qq = QS[q]
            orc = qq.get("oracle", {})
            how = orc.get("die") or ("from " + orc["from"] if "from" in orc else "")
            qs.append("`%s` (%s)" % (q, how))
        out.append("| %d. %s | %s | %s | %s |" % (st["n"], st["name"], st["rule"], "; ".join(qs) or "none: engine only",
                                                 ", ".join("`%s`" % w for w in st["writes"])))
    out += ["", "**T-12-16 What the rules read from a region, and the seed check** (`world_seed.yaml#requirements`; 12.16.17;",
            "`12-world-seed.py` runs every check). *Generic* names the default table or rule used when the seed leaves the",
            "key to it.", "", "| Id | From | What is read | Rules | Seed key | Check |", "|---|---|---|---|---|---|"]
    for r in WS["requirements"]:
        out.append("| `%s` | %s | %s | %s | `%s` | %s |" % (r["id"], r["from"], r["need"], ", ".join(r["rules"]), r["key"],
                                                          r["check"] + ((": " + r["generic"]) if r.get("generic") else "")))
    for r in WS["pack_requirements"]:   # [revision: R2-D] the seed-pack checks (12.16.17; I-130)
        out.append("| `%s` | %s | %s | %s | `%s` | %s |" % (r["id"], r["from"], r["need"], ", ".join(r["rules"]), r["key"], r["check"]))
    return "\n".join(out)

def main():
    args = sys.argv[1:]
    if "--tables" in args:
        print(render_tables())
        return
    given = None
    if "--answers" in args:
        given = yaml.safe_load(open(args[args.index("--answers") + 1], encoding="utf-8"))
    bad_refs = rule_refs_ok()
    print("12-world-seed.py -- the world seed (12.16) from data/world_seed.yaml; checks = world_seed.yaml#requirements")
    print("rule references in the requirements list: %d, unresolved %d %s" % (sum(len(r["rules"]) for r in WS["requirements"]), len(bad_refs), bad_refs or ""))
    allfails = list(bad_refs)
    if "--seed" in args:
        seeds = [int(args[args.index("--seed") + 1])]
    else:
        seeds = [1]
    print()
    reg = seed_packs(build_seed(seeds[0], given), seeds[0])
    allfails += report(reg)
    if "--emit" in args:
        open(args[args.index("--emit") + 1], "w", encoding="utf-8", newline="\n").write(dump(reg))
    if "--seed" not in args:
        # player-guided: a fixed set of answers (the rest oracle) must give a seed that passes every check
        guided = {"ws.q.wound": "long_winter", "ws.q.climate": "northern", "ws.q.magic_level": "rare", "ws.q.keeper_count": "2",
                  "ws.q.keepers": ["kf.hearth", "kf.death"], "ws.q.bargainer": "death_keeper", "ws.q.haven_tier": "village",
                  "ws.q.haven_site": "hill", "ws.q.rulers": "org.clan.family", "ws.q.inciting": "refugees", "ws.q.month_names": "named",
                  "ws.q.extra_impossible": ["no_teleport"], "ws.q.second_tongue": "old_tongue",
                  # a custom answer ("magic is something only the old families do") classified by 12.16.2:
                  "ws.q.arcane_source": "order_only"}
        print()
        print("guided run (%d answers from the player, the rest by the oracle):" % len(guided))
        g = seed_packs(build_seed(2, guided), 2)
        gf = report(g, verbose=False)
        print("  %s; %d requirements fail%s" % (g["region"]["name"], len(gf), (": " + ", ".join(f[0] for f in gf)) if gf else ""))
        allfails += gf
        print()
        n = 200
        tally, words, tables = Counter(), Counter(), 0
        for s in range(1, n + 1):
            rg = seed_packs(build_seed(1000 + s), 1000 + s)
            fl = report(rg, verbose=False)
            for f in fl:
                tally[f[0]] += 1
            for a in rg["encounter_table_audit"].values():
                tables += 1
                for k, v in a["words"].items():
                    words[k] += v
            allfails += [("seed %d" % (1000 + s),) + f for f in fl]
        tot = sum(words.values())
        print("robustness: %d oracle seeds (1001-%d): seeds with any failed check %d; failures by requirement %s" % (n, 1000 + n, len({f[0] for f in allfails if isinstance(f[0], str) and f[0].startswith("seed")}), dict(tally) or "none"))
        print("  %d regional encounter tables built and audited; word mix over their threat faces: %s" % (tables, " ".join("%s %.1f%%" % (k, 100.0 * words[k] / tot) for k in WA.WORDS)))
    if "--seed" not in args:
        # a pre-made seed is checked by the same list (12.16.17, 12.16.18); informational: chapter 13 is optional
        # and unmaintained (FINISH-PLAN), so its gaps are reported, not counted against the procedure
        print()
        pm = load_premade(os.path.join(DATA, "region_thallen.yaml"))
        pres = check_seed(pm)
        pf = [r for r in pres if not r[1]]
        print("pre-made seed: data/region_thallen.yaml (chapter 13, optional, unmaintained): %d of %d requirements hold" % (len(pres) - len(pf), len(pres)))
        for rid, okk, note in pf:
            print("    gap  %-32s %s" % (rid, note))
    print()
    print("RESULT:", "PASS" if not allfails else "FAIL (%d)" % len(allfails))
    sys.exit(1 if allfails else 0)

if __name__ == "__main__":
    main()
