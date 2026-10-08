"""Shared pieces of the world seed (12.16): the data it reads, its dice, names, NPC and place records.

A port of the helpers of `_process/simulation/12-world-seed.py`; the draw order is the reference's, so a
`random.Random(seed)` stream reproduces it exactly.
"""

from __future__ import annotations

import functools
import re
from collections.abc import Sequence
from types import SimpleNamespace
from typing import Any

from engine.gen import _data
from engine.gen._rng import SeedRng
from engine.gen.threat_table import adversaries

Rec = dict[str, Any]
BRANCHES = ["martial", "guile", "influence", "lore", "craft", "wilds", "arcane", "divine", "primal"]
PLURAL = {"orig.people.human": "folk", "orig.people.elf": "elves", "orig.people.dwarf": "dwarves",
          "orig.people.halfling": "halflings", "orig.people.orc_kin": "orc-kin", "orig.people.goblin_kin": "goblin-kin",
          "orig.people.giant_kin": "giant-kin", "orig.people.beastfolk": "beastfolk"}


@functools.lru_cache(maxsize=1)
def data() -> SimpleNamespace:
    """Everything the seed reads (12.16.1 *Reads*), loaded once."""
    L = _data.load
    ws = L("world_seed.yaml")
    orig = L("origins.yaml")
    origd = {o["id"]: o for o in orig["origins"]}
    origd.update({e["id"]: e for b in orig.get("blocks") or [] for e in b.get("entries") or []})
    fac = L("factions.yaml")
    wt = L("world_turn.yaml")
    sites = L("sites.yaml")
    travel = L("travel.yaml")
    lic = L("licenses.yaml")
    inv = L("investigation.yaml")
    return SimpleNamespace(
        WS=ws, TAB={t["id"]: t for t in ws["tables"]}, QS={q["id"]: q for q in ws["questions"]}, DEF=ws["defaults"],
        ARCHD={a["id"]: a for a in L("archetypes.yaml")["archetypes"]}, ORIG=orig, ORIGD=origd,
        TAGS={t["id"] for t in L("tags.yaml")["tags"]}, FAC=fac, TPL={t["id"]: t for t in fac["templates"]},
        WT=wt, SITT={s["id"]: s for s in wt["situation_templates"]}, SITES=sites,
        THEMES={t["id"]: t for t in sites["site_themes"]}, DOMAINS={d["id"]: d for d in sites["site_domains"]},
        POOLS={(p["theme"], p["domain"]): p for p in sites["denizen_pools"]}, TRAVEL=travel,
        TERRAIN_DEF=travel["terrain_defaults"], GENERIC_ENC={t["terrain"]: t for t in travel["encounter_tables"]},
        ORAC={t["id"]: t for t in L("oracles.yaml")["tables"]},
        COMP={c["id"]: c for c in L("companions.yaml")["companions"]}, RIT=L("rituals.yaml")["rituals"],
        ABIL={a["id"]: a for a in L("abilities.yaml")["abilities"]},
        LICS={x["id"] for x in lic["licenses"]} | {e["id"] for b in lic["blocks"] for e in b["entries"]},
        CAL=L("calendar.yaml"), CLIMATES={c["id"] for c in L("weather.yaml")["climates"]},
        ATTRS=[a["id"] for a in L("attributes.yaml")["attributes"]], ADV=adversaries(),
        CLUE_IDS={pl["id"] for c in inv["cases"] for pl in c.get("placements", [])}
        | {nd["id"] for c in inv["cases"] for nd in c.get("nodes", [])},
    )


class Dice:
    """The reference's dice over one RC-RNG stream."""

    def __init__(self, rng: SeedRng):
        self.rng = rng

    def d(self, n: int) -> int:
        return self.rng.randint(1, n)

    def die(self, s: Any) -> int:
        return self.d(int(str(s).lstrip("d")))

    def pick(self, seq: Any) -> Any:
        return seq[self.rng.randrange(len(seq))]

    def sample(self, seq: Any, k: int) -> list[Any]:
        return self.rng.sample(list(seq), k)

    def weighted(self, items: Sequence[tuple[Any, float]]) -> Any:
        tot = sum(w for _, w in items)
        x = self.rng.random() * tot
        for k, w in items:
            x -= w
            if x < 0:
                return k
        return items[-1][0]


_ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
         "seventeen eighteen nineteen").split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def num_words(n: int) -> str:
    if n < 20:
        return _ONES[n]
    t, o = divmod(n, 10)
    return _TENS[t] + ("" if o == 0 else "-" + _ONES[o])


def fill_pitch(pitch: str, region: str, years: int) -> str:
    """# rule: 12.16.4 -- the pitch names the region and the wound's age in words."""
    w = num_words(years)
    return pitch.replace("{region}", region).replace("{years}", w).replace("{Years}", w[0].upper() + w[1:])


def in_range(rng_s: Any, v: int) -> bool:
    a, _, b = str(rng_s).partition("-")
    return int(a) <= v <= int(b or a)


def by_range(rows: list[Rec], v: int) -> Rec:
    for r in rows:
        if in_range(r["range"], v):
            return r
    raise KeyError(v)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower().replace("'", "")).strip("_")


def anc(t: str, g: str) -> bool:
    """00.5.4 c: t equals g or descends from it."""
    return t == g or t.startswith(g + ".")


class Answers:
    """# rule: 12.16.2 -- answers from the player (given) or the oracle; each logged with its source."""

    def __init__(self, given: dict[str, Any] | None = None, sources: dict[str, str] | None = None,
                 log: list[Rec] | None = None):
        self.given = dict(given or {})
        self.sources = dict(sources or {})
        self.log: list[Rec] = log if log is not None else []

    def get(self, qid: str, oracle_fn: Any) -> Any:
        if qid in self.given:
            v, src = self.given[qid], self.sources.get(qid, "player")
        else:
            v, src = oracle_fn(), "oracle"
        self.log.append({"question": qid, "answer": v, "source": src})
        return v


def oracle_simple(dice: Dice, q: Rec, ctx: Rec | None = None) -> Any:
    """# rule: 12.16.2 -- a question's oracle roll (T-12-15)."""
    o = q["oracle"]
    if "from" in o:
        return o["map"][(ctx or {})[o["from"]]]
    rows = o["results"]
    if isinstance(rows, dict):
        rows = rows[(ctx or {})[o["by"]]]
    return by_range(rows, dice.die(o["die"]))["option"]


class Names:
    """# rule: 12.16.7 -- place names composed from the seed's tables, never repeated in one seed."""

    def __init__(self, dice: Dice, used: set[str] | None = None):
        self.dice = dice
        self.used: set[str] = used if used is not None else set()

    def compose(self, starts: list[str], ends: list[str], sep: str = "") -> str:
        for _ in range(60):
            n = self.dice.pick(starts) + sep + self.dice.pick(ends)
            if n not in self.used:
                self.used.add(n)
                return n
        raise RuntimeError("name space exhausted")

    def place(self) -> str:
        t = data().TAB["tbl.12.seed.place_names"]
        return self.compose(t["start"], t["end"])

    def region(self) -> str:
        t = data().TAB["tbl.12.seed.place_names"]
        return "the " + self.compose(t["region_adjective"], t["region_noun"], " ")

    def area(self, terrain: str) -> str:
        t = data().TAB["tbl.12.seed.place_names"]
        branch = ".".join(terrain.split(".")[:2])
        return "the " + self.compose(t["area_adjective"], t["area_noun_by_terrain"][branch], " ")


def name_tables(dice: Dice, names: Names, rs: str, peoples: list[Rec]) -> list[Rec]:
    """# rule: 12.16.7 -- one d20 given / d12 family (or epithet) table per present people."""
    out: list[Rec] = []
    parts = data().TAB["tbl.12.seed.names"]["by_people"]
    for p in peoples:
        if p["present"] == "absent":
            continue
        spec = parts[p["origin"]]
        styles = spec.get("styles") or [dict(spec, name=None)]
        if p["origin"] == "orig.people.human" and p["present"] != "common":
            styles = styles[:1]
        tabs = []
        for st in styles:
            given: list[str] = []
            while len(given) < 20:
                n = dice.pick(st["given_start"]) + dice.pick(st["given_end"])
                if n not in given and n not in names.used:
                    given.append(n)
            names.used.update(given)
            if "family_start" in st:
                fam: list[str] = []
                while len(fam) < 12:
                    n = dice.pick(st["family_start"]) + dice.pick(st["family_end"])
                    n = n if " " in n else n.capitalize()
                    if n not in fam:
                        fam.append(n)
                famkey, famrows = "family", fam
            else:
                famkey, famrows = "epithet", dice.sample(st["epithets"], 12)
            pid = p["origin"].split(".")[-1]
            multi = bool(st.get("name")) and len(styles) > 1
            tid = "tbl.{}.names.{}{}".format(rs, pid, ("_" + slug(st["name"])) if multi else "")
            tabs.append({"id": tid, "name": "Names: {}{}".format(pid.replace("_", " "), (" (" + st["name"] + ")") if multi else ""),
                         "people": p["origin"], "die": "d20", "recency": True,
                         "given": [{"range": str(i + 1), "result": g} for i, g in enumerate(given)],
                         famkey: [{"range": str(i + 1), "result": f} for i, f in enumerate(famrows)], "family_die": "d12",
                         "basis": ["12.16.7", "12.11.1", "02.9.7"]})
        p["name_tables"] = [t["id"] for t in tabs]
        out += tabs
    return out


def person_name(dice: Dice, tables: list[Rec], people_origin: str, given_used: set[str]) -> str:
    """# rule: 12.11.1 -- a name from the people's table; no given name twice in one seed (recency)."""
    cands = [t for t in tables if t["people"] == people_origin]
    for _ in range(40):
        t = dice.pick(cands)
        g = by_range(t["given"], dice.d(20))["result"]
        if g in given_used:
            continue
        given_used.add(g)
        return _full_name(dice, t, g)
    # The table's 20 given names are spent (a long campaign's walk-ons): compose a fresh one from the people's own
    # syllables (tbl.12.seed.names), so names never run out. The seed's draws above are unchanged.
    spec = data().TAB["tbl.12.seed.names"]["by_people"].get(people_origin) or {}
    styles = spec.get("styles") or [spec]
    for _ in range(200):
        st = dice.pick(styles)
        if not st.get("given_start"):
            break
        g = dice.pick(st["given_start"]) + dice.pick(st["given_end"])
        if g not in given_used:
            given_used.add(g)
            return _full_name(dice, dice.pick(cands), g)
    g = by_range(dice.pick(cands)["given"], dice.d(20))["result"]  # ponytail: a reused given name, once all fail
    return _full_name(dice, dice.pick(cands), g)


def _full_name(dice: Dice, t: Rec, given: str) -> str:
    return "{} {}".format(given, by_range(t["family"] if "family" in t else t["epithet"], dice.d(12))["result"])


def template_for(org: str) -> Rec:
    """# rule: PR-11-8 -- the faction template whose org tag is the deepest ancestor of `org`."""
    D = data()
    best: tuple[int, Rec] | None = None
    for t in D.TPL.values():
        for o in t["org_tags"]:
            if anc(org, o) and (best is None or o.count(".") > best[0]):
                best = (o.count("."), t)
    if best:
        return best[1]
    branch = ".".join(org.split(".")[:2])
    for t in D.TPL.values():
        if t.get("branch_default_for") == branch:
            return t
    raise KeyError(org)


def roll_oracle_table(dice: Dice, tid: str, field: str = "results") -> Rec:
    t = data().ORAC[tid]
    return by_range(t[field], dice.die(t["die"]))


def step_to(rows: list[Rec], start: Rec, fits: Any) -> Rec:
    """# rule: 12.11.1 -- from the rolled row, step down the table (wrapping) to the first row that fits."""
    i = rows.index(start)
    for k in range(len(rows)):
        r = rows[(i + k) % len(rows)]
        if fits(r):
            return r
    return start


def role_license(tag: str) -> str | None:
    """05.9.3: the domain training license of a level-2 deed tag, if one exists."""
    p = tag.split(".")
    if len(p) < 3:
        return None
    lid = f"lic.training.{p[1]}_{p[2]}"
    return lid if lid in data().LICS else None


def roll_want(dice: Dice) -> str:
    """# rule: 12.11.1 -- a want: object and verb, the verb stepped to one that takes the object."""
    obj = roll_oracle_table(dice, "tbl.npc_want_object")
    verb = roll_oracle_table(dice, "tbl.npc_want_verb")
    on = int(obj["range"])
    verb = step_to(data().ORAC["tbl.npc_want_verb"]["results"], verb, lambda r: on in r.get("takes", [on]))
    return "{} {}".format(verb["result"], obj["result"])


def roll_refusal(dice: Dice, role_tags: Any) -> Rec:
    """# rule: 12.11.1 -- a refusal, stepped past rows whose not_for matches a role tag."""
    r = roll_oracle_table(dice, "tbl.npc_refusal")
    return step_to(data().ORAC["tbl.npc_refusal"]["results"], r,
                   lambda x: not any(t == n or t.startswith(n + ".") for n in x.get("not_for", []) for t in role_tags))


def make_npc(dice: Dice, S: Rec, *, role: str, people: str, home: str, member_of: Any = (), depth: str = "principal",
             band: int = 1, role_tags: Any = (), duty: str | None = None, recruit: Rec | None = None,
             name: str | None = None) -> Rec:
    """# rule: 12.16.11 -- a cast NPC at principal depth (12.11.1's fields), written into S['npcs']."""
    D = data()
    g = roll_oracle_table(dice, "tbl.npc_gender")
    nm = name or person_name(dice, S["names"], people, S["_given_used"])
    nid = f"npc.{slug(nm)}"
    while nid in S["_npc_ids"]:
        nid += f"_{dice.d(9):d}"
    S["_npc_ids"].add(nid)
    tags = D.ORIGD[people]["tags"]
    folk = tags[0] if tags[0].startswith("creature.folk") else [t for t in tags if t.startswith("creature.folk")][0]
    want = roll_want(dice)
    sec = roll_oracle_table(dice, "tbl.npc_secret")["result"]
    native = [x["license"] for x in D.ORIGD[people].get("languages", []) if x["license"] != "lic.lang.common"]
    role_tags = list(role_tags)
    npc: Rec = {"id": nid, "name": nm, "role": role, "people": folk, "gender": g["result"], "pronouns": g["pronouns"]}
    npc["age"] = roll_oracle_table(dice, "tbl.npc_age")["result"]
    npc.update({"depth": depth, "home": home, "member_of": list(member_of),
                "wants": [{"text": want, "tags": list(role_tags[:1]) or ["conduct.loyalty"], "rank": 1}]})
    npc["fears"] = [{"text": roll_oracle_table(dice, "tbl.npc_fear")["result"], "tags": []}]
    npc["refusals"] = ([{"kind": r.get("kind", "refusal.self"), "text": r["result"]} for r in [roll_refusal(dice, role_tags)]]
                       + ([{"kind": "refusal.duty", "text": duty, "strength": "absolute"}] if duty else []))
    npc["secrets"] = [{"fact": "sec.{}.1".format(nid.split(".", 1)[1]), "text": sec,
                       "gate": "standing Devoted, or a clue found by play (15.9)"}]
    reg = roll_oracle_table(dice, "tbl.npc_voice_register")["result"]
    npc["voice"] = {"register": reg, "habit": roll_oracle_table(dice, "tbl.npc_voice_habit")["result"]}
    npc["detail"] = roll_oracle_table(dice, "tbl.npc_detail")["result"]
    npc["demeanor"] = roll_oracle_table(dice, "tbl.npc_demeanor")["result"]
    npc.update({
        "lifestyle": "comfortable" if depth == "principal" else "modest", "speaks": ["lic.lang.common"] + native[:1],
        "band": band, "standing_to_pc": 0, "exists": "exists", "officer_duty": duty, "recruit": recruit, "kind": "npc",
        "tags": [folk], "role_tags": list(role_tags),
        "competence": [{"tag": t, "value": D.DEF["npc_competence"]["by_band"][band]} for t in role_tags],
        "licenses": [{"id": role_license(t), "grade": "trained"} for t in role_tags if role_license(t)],
        "visibility": "background", "sealed_fields": ["wants", "fears", "refusals", "secrets", "knowledge"],
        "mind": "sapient", "knowledge": [], "lifecycle": "provisional", "basis": ["12.11.1", "12.16.11"],
    })
    S["npcs"].append(npc)
    return npc


def terrain_default(t: str | None) -> Rec:
    td = data().TERRAIN_DEF
    while t:
        if t in td:
            return td[t]
        t = t.rsplit(".", 1)[0] if "." in t else None
    return {}


def place_record(pid: str, name: str, kind: str, parent: str | None, ring: int | None, band: int | None,
                 danger: str | None, terrain: list[str], climate: str, desc: str, **kw: Any) -> Rec:
    """# rule: 10.1.2 -- a place record with every field 10.1.2 names (12.16.8 writes them)."""
    td = terrain_default(terrain[0]) if terrain else {}
    rec: Rec = {
        "id": pid, "name": name, "place_kind": kind, "parent": parent, "ring": ring, "band": band, "danger": danger,
        "safe": False, "rest_site": "rough" if kind == "area" else None, "terrain": list(terrain), "climate": climate,
        "nav_tier": td.get("nav_tier") if kind == "area" else None, "forage_tier": None, "game_tier": None,
        "openness": td.get("openness", "broken"), "landmarks": [], "water_source": None, "grazing": None,
        "encounter_table": None, "hazards": [], "resonance": [], "settlement_scope": None, "known": True,
        "discovered": False, "site": None, "state_log": [], "links": [], "facts": {}, "desc": desc, "kind": "place",
        "tags": list(terrain[:1]), "exists": "exists", "visibility": "shown", "lifecycle": "provisional",
        "basis": ["10.1.2", "12.16.8"],
    }
    rec.update(kw)
    return rec


def link(S: Rec, a: str, b: str, watches: int, kind: str, terrain: str) -> None:
    """# rule: 10.1.3 -- a two-way route link between places a and b, `watches` long."""
    rid = "rt.{}.{:d}".format(S["_rs"], len(S["_routes"]) + 1)
    S["_routes"].append(rid)
    P = S["_places"]
    for x, y in ((a, b), (b, a)):
        P[x]["links"].append({"to": y, "route": rid, "route_kind": kind, "travel_watches": watches, "terrain": [terrain],
                              "current": None, "known": P[y]["known"] and P[x]["known"], "danger": None, "hazards": [],
                              "vehicle_ok": ["bi.cart"] if kind == "road" else []})
