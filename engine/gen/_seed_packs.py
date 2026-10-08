"""Seed packs (12.16.9, 12.16.11, 12.16.16; DL-12-61): a look, furniture and exits for every place, a knowledge pack
and a stance for every cast NPC, documents with text, and the incident's reduced case (`engine.gen.case`).

A port of `_process/simulation/12-world-seed.py#seed_packs` and `#check_packs`, draw for draw. Packing runs after
step 13 on streams keyed by the seed and each entity's id (`keyed`), so it never moves a draw of the seed itself
and gives the same result whenever it runs.
"""

from __future__ import annotations

import functools
import hashlib
import random
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

from engine.gen import _data
from engine.gen._seed_lib import Dice, Rec, by_range, data, num_words, slug

Result = tuple[str, bool, str]


@functools.lru_cache(maxsize=1)
def pack_data() -> SimpleNamespace:
    """The tables the packs read (world_seed.yaml, social.yaml#common_knowledge, investigation.yaml#reduced_case)."""
    tab = data().TAB
    return SimpleNamespace(
        CK=_data.load("social.yaml")["common_knowledge"], RCASE=_data.load("investigation.yaml")["reduced_case"],
        LOOK=tab["tbl.12.seed.place_look"], FURN=tab["tbl.12.seed.furniture"], DOCT=tab["tbl.12.seed.document"],
        KPACK=tab["tbl.12.seed.knowledge_pack"])


def keyed(seed: Any, *parts: Any) -> Dice:
    """# rule: 12.16.9 -- a dice stream keyed by the seed and an entity id (a generated answer never depends on draw
    order)."""
    h = hashlib.sha256("|".join(map(str, (seed, *parts))).encode()).hexdigest()
    return Dice(random.Random(int(h[:15], 16)))


def place_type(p: Rec) -> str:
    if p["place_kind"] == "building":
        return p["id"].rsplit(".", 1)[1]
    if p["place_kind"] in ("settlement", "landmark"):
        return p["place_kind"]
    t = ((p.get("terrain") or ["x"])[0]).split(".")
    return t[1] if len(t) > 1 else "default"


def role_key(npc: Rec) -> str:  # rule: 12.10.6
    """social.yaml#common_knowledge.rule: first word of the role, else the first role_map pattern, else other."""
    ck = pack_data().CK
    txt = str(npc.get("role") or "").lower()
    w = txt.split()[0] if txt else "other"
    if w in ck["by_role"]:
        return w
    return next((m["role"] for m in ck["role_map"] if m["pattern"] in txt), "other")


def in_haven(reg: Rec, pid: str | None) -> bool:
    P = {p["id"]: p for p in reg["places"]}
    hav = reg["region"]["haven"]
    return pid == hav or (pid in P and P[pid].get("parent") == hav)


def pick_n(d: Dice, rows: list[Any], n: int) -> list[Any]:
    out: list[Any] = []
    while len(out) < n:
        i = d.d(len(rows)) - 1
        while rows[i] in out:
            i = (i + 1) % len(rows)
        out.append(rows[i])
    return out


def pack_places(reg: Rec, seed: Any) -> None:  # rule: 12.16.9
    """Every place (the region record aside): a look, 2-4 furniture items, its exits."""
    D = pack_data()
    P = {p["id"]: p for p in reg["places"]}
    regional = next((t for t in reg.get("tables") or [] if str(t.get("id", "")).endswith(".furnishings")), None)
    for p in reg["places"]:
        if p["place_kind"] == "region":
            continue
        k, d = place_type(p), keyed(seed, p["id"], "place")
        p["look"] = d.pick(D.LOOK["by_kind"].get(k) or D.LOOK["by_kind"]["default"]).replace("{name}", p["name"])
        items = pick_n(d, D.FURN["by_kind"].get(k) or D.FURN["by_kind"]["default"], d.d(3) + 1)
        if regional and p["place_kind"] == "building":
            items[-1] = by_range(regional["results"], d.die(regional["die"]))["result"]
        p["furniture"] = items
        if p["links"]:
            p["exits"] = [x["to"] for x in p["links"]]
        elif p["place_kind"] == "building":
            sib = [q for q in P if P[q].get("parent") == p["parent"] and P[q]["place_kind"] == "building" and q != p["id"]]
            p["exits"] = [p["parent"]] + sib[:2]
        else:
            p["exits"] = [p["parent"]] if p.get("parent") in P else []


def walk_on(reg: Rec, seed: Any, tag: str, role: str, home: str | None) -> Rec:  # rule: 12.11.1
    """A minimal 12.11.1 walk-on (role, a name from the seed's tables, home), kept in `reg['walk_ons']`."""
    d = keyed(seed, "walk_on", tag)
    t = d.pick(reg["names"])
    nm = "{} {}".format(by_range(t["given"], d.d(20))["result"], by_range(t.get("family") or t["epithet"], d.d(12))["result"])
    n: Rec = {"id": "npc.{}".format(slug(nm + " " + tag)), "name": nm, "role": role, "depth": "walk_on", "home": home,
              "member_of": [], "kind": "npc", "exists": "exists", "knowledge": [], "basis": ["12.11.1", "PR-15-6"]}
    reg.setdefault("walk_ons", []).append(n)  # entities of the store; kept apart from the seed cast (12.16.11)
    return n


def lead_holder_place(reg: Rec, target: str) -> str:
    """Where a lead target is found: a place itself; a situation's region; a clock's faction seat (its head's home)."""
    P = {p["id"]: p for p in reg["places"]}
    if target in P:
        return target
    sit = next((s for s in reg.get("situations") or [] if s["id"] == target), None)
    if sit and sit.get("region") in P:
        return sit["region"]
    for f in reg["factions"]["instances"]:
        if target in (f["id"], (f.get("goal") or {}).get("clock")):
            head = next((n for n in reg["npcs"] if f["id"] in (n.get("member_of") or [])
                         and str(n["role"]).startswith("head of")), None)
            if head:
                return head["home"]
    return reg["region"]["haven"]


def fill_doc(row: Rec, **kw: Any) -> str:
    t = str(row["text"])
    for k, v in kw.items():
        t = t.replace("{" + k + "}", str(v))
    return t


def make_document(reg: Rec, seed: Any, tag: str, option: str, at: str, issuer: str, contact: tuple[str, str],
                  target_words: str) -> Rec:  # rule: 12.16.16
    """A notice from tbl.12.seed.document, its text filled; kept in `reg['documents']`."""
    DOCT = pack_data().DOCT
    d = keyed(seed, "doc", tag)
    P = {p["id"]: p for p in reg["places"]}
    row = next(r for r in DOCT["results"] if r["option"] == option)
    flds = {k: d.pick(v) for k, v in DOCT["fields"].items()}
    text = fill_doc(row, issuer=issuer, haven=P[reg["region"]["haven"]]["name"],
                    year=str(reg["calendar"]["opening_date"]).split(",")[-1].strip(),
                    contact=contact[0], contact_place=contact[1], target=target_words, **flds)
    doc: Rec = {"id": f"doc.{tag}", "kind": "document", "option": option, "at": at, "text": text, "table": DOCT["id"]}
    reg.setdefault("documents", []).append(doc)
    return doc


def cast_pick(d: Dice, pool: list[Rec], weight: Callable[[Rec], float]) -> Rec | None:  # rule: 00.11.1
    """social.yaml#cast fill: weighted by fit over the gated pool; None when the pool is empty."""
    rows = [(n, w) for n, w in ((n, weight(n)) for n in pool) if w > 0]
    return d.weighted(rows) if rows else None


def pack_npcs(reg: Rec, seed: Any) -> None:  # rule: 12.16.11
    """Every cast NPC: a trade fact, a local or public one, a tie, a d6 4-6 rumor; a stance toward the incident."""
    D = pack_data()
    CK, KPACK = D.CK, D.KPACK
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
    named = [n for n in cast if n["id"] not in secret]  # a pack fact never names the case's solution

    def ring_of(n: Rec) -> int:
        return P[n["home"]]["ring"] if n["home"] in P else 0

    for n in cast:
        d = keyed(seed, n["id"], "pack")
        ring = ring_of(n)
        others = [m for m in named if m is not n and ring_of(m) == ring] or [m for m in named if m is not n]

        def fill(row: str, d: Dice = d, others: list[Rec] = others) -> str:
            rt = d.pick(routes) if routes else None
            place = (P[rt["to"]]["name"] if rt and "{watches}" in row else d.pick(near)["name"]) if near else P[hav]["name"]
            return (row.replace("{place}", place)
                    .replace("{watches}", num_words(rt["travel_watches"]) if rt else "a few")
                    .replace("{route_kind}", rt["route_kind"] if rt else "track")
                    .replace("{other}", d.pick(others)["name"]).replace("{faction}", d.pick(facs)["name"])
                    .replace("{keeper}", keeper).replace("{haven}", P[hav]["name"]))

        own: list[Rec] = []
        tail = n["id"].split(".", 1)[1]
        for slot, topic in (("trade", d.pick(CK["by_role"][role_key(n)])), ("local", d.pick(["local_news", "folk"]))):
            own.append({"fact": f"kn.{tail}.{slot}", "slot": slot, "topic": topic,
                        "text": fill(d.pick(KPACK["by_topic"][topic])), "how": "seed", "tier": "T1"})
        other = d.pick(others)
        own.append({"fact": f"kn.{tail}.tie", "slot": "tie", "topic": "folk", "about": other["id"],
                    "text": d.pick(KPACK["ties"]).replace("{other}", other["name"]).replace("{haven}", P[hav]["name"]),
                    "how": "seed", "tier": "T1"})
        if d.d(6) >= 4 and rumors:
            rid, rng = d.pick(rumors)
            own.append({"fact": f"kn.{tail}.rumor", "slot": "rumor", "topic": "local_news",
                        "rumor": {"table": rid, "range": rng}, "truth": "sealed", "how": "seed"})
        n["knowledge"] = own
        st = KPACK["stance"]
        if n["id"] in holders:
            n["stance"] = {"toward": "incident", "stance": "helps", "why": "holds a placement of the incident's case"}
        elif any(m.endswith(".threat") for m in n.get("member_of") or []):
            n["stance"] = {"toward": "incident", "stance": "hinders", "why": "of the threat faction"}
        else:
            r = by_range(st["results"], d.die(st["die"]))
            n["stance"] = {"toward": "incident", "stance": r["stance"], "why": r["gist"]}


def seed_packs(reg: Rec, seed: Any) -> Rec:  # rule: 12.16.16
    """The seed-pack pass: places, the incident's reduced case (12.16.16), documents, then NPC packs."""
    from engine.gen.case import reduced_case

    DOCT = pack_data().DOCT
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
            doc = make_document(reg, seed, f"lead_{i + 1:d}", "hire", post, fac["name"],
                                (head["name"], P[head["home"]]["name"] if head["home"] in P else P[hav]["name"]), "")
            ld["document"], ld["names"] = doc["id"], head["name"]
    d = keyed(seed, "documents")
    opt = by_range(DOCT["results"], d.d(3) + 1)["option"]  # one more: warning, charter or bounty
    rul = next(f for f in reg["factions"]["instances"] if f["id"].endswith(".rulers"))
    capt = next((n for n in reg["npcs"] if n["home"] == hav + ".gate" and n.get("depth") != "walk_on"), None)
    site = next(p for p in reg["places"] if p["place_kind"] == "site" and p.get("ring") == 1)
    post = next(p for p in DOCT["results"] if p["option"] == opt)["posted_at"]
    at = next((hav + "." + k for k in post if hav + "." + k in P), hav)
    make_document(reg, seed, "notice", opt, at, rul["name"],
                  (capt["name"] if capt else "the watch", P[hav + ".gate"]["name"] if hav + ".gate" in P else P[hav]["name"]),
                  site["name"])
    pack_npcs(reg, seed)
    return reg


def check_packs(reg: Rec) -> list[Result]:  # rule: 12.16.17
    """world_seed.yaml#pack_requirements on a packed region. Returns [(id, ok, note)]."""
    from engine.gen.case import validate_case

    places = [p for p in reg["places"] if p["place_kind"] != "region"]
    cast_all = [n for n in reg["npcs"] if n.get("depth") != "walk_on"]
    case = next((c for c in reg.get("seed_cases") or [] if c["trigger"] == "incident"), None)
    docs = reg.get("documents") or []
    lead_docs = [(ld, next((x for x in docs if x["id"] == ld["document"]), None))
                 for ld in reg["opening"]["leads"] if ld.get("document")]
    out: list[Result] = []
    for rq in data().WS["pack_requirements"]:
        c = rq["check"]
        if c == "looks":
            bad = [p["id"] for p in places if not p.get("look")]
        elif c == "furniture":
            bad = [p["id"] for p in places if not 2 <= len(p.get("furniture") or []) <= 4]
        elif c == "exits":
            bad = [p["id"] for p in places if not p.get("exits")]
        elif c == "knowledge":
            bad = [n["id"] for n in cast_all
                   if not (2 <= len([k for k in n.get("knowledge") or [] if k["slot"] in ("trade", "local", "tie", "rumor")]) <= 4
                           and {"trade", "local", "tie"} <= {k["slot"] for k in n.get("knowledge") or []})]
            sub = case["solution"]["subject"]["id"] if case else None
            bad += [n["id"] + " names the subject" for n in cast_all for k in n.get("knowledge") or []
                    if sub and k.get("about") == sub]
        elif c == "stance":
            bad = [n["id"] for n in cast_all if not (n.get("stance") or {}).get("stance")]
        elif c == "documents":
            bad = [x["id"] for x in docs if not x.get("text") or "{" in x["text"]] + \
                  [ld["lead"][:30] for ld, x in lead_docs if not x or ld["names"] not in x["text"]]
        elif c == "reduced_case":
            bad = ["no incident case"] if not case else validate_case(case)
        else:
            bad = ["unknown check " + c]
        out.append((rq["id"], not bad, "{:d} places, {:d} cast, {:d} documents{}".format(
            len(places), len(cast_all), len(docs), ("; " + ", ".join(bad[:3])) if bad else "")))
    return out
