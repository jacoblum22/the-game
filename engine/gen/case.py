"""The reduced case (PR-15-6 reduced profile, 15.9.4; `investigation.yaml#reduced_case`; DL-15-38, DL-12-62).

Two necessary nodes (the subject; the way on), three placements and one reserve each, the first node's core
placement held where the question arose. Built at seed time for the inciting incident (12.16.16) and on demand for a
story-role question with no case behind it (PR-12-10 step 1):

    case = reduced_case(reg, seed, option, place, lead_target)        # on a region record (the seed's pass)
    validate_case(case)                                               # [] = valid (15.9.4, reduced numbers)
    case = case_for_question(tx, "who is missing", place)            # in play: built, written to the store
    holder = pointer(case, node_id, asked=npc)                         # who to send the PC to: the core holder first

`reduced_case` is a port of `_process/simulation/12-world-seed.py#reduced_case`, draw for draw. In the store a case
is a record in meta `world.cases` (never rendered: its solution and placements stay sealed until delivered), its
walk-ons are NPC entities and its documents are things with a `text` fact.
"""

from __future__ import annotations

from collections.abc import Collection
from typing import Any

from engine.audit import text as words
from engine.gen._seed_lib import Rec
from engine.gen._seed_packs import (
    cast_pick,
    in_haven,
    keyed,
    lead_holder_place,
    make_document,
    pack_data,
    place_type,
    role_key,
    walk_on,
)
from engine.store.events import EntityRecord, Event
from engine.world.common import active_pc, fact, meta

CASES = "world.cases"  # meta {case id: case record}
MIN_LIVE = 2  # investigation.yaml#reduced_case.audit: min_live 2


# ------------------------------------------------------------------------------------------- the builder


def reduced_case(reg: Rec, seed: Any, option: str, place: str, lead_target: str, tag: str = "incident") -> Rec:
    # rule: PR-15-6
    """PR-15-6, reduced profile: 2 necessary nodes, 3 placements each, 1 reserve each, the first core placement held
    at `place`. Returns the case record (sealed); writes it to `reg['seed_cases']` and its id to `reg['cases']`."""
    RCASE = pack_data().RCASE
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
            subj = walk_on(reg, seed, f"{tag}_subject", role, place)
        subject = {"id": subj["id"], "role": sub["role"], "words": subj["name"]}
    else:
        fac = {f["id"].rsplit(".", 1)[1]: f["name"] for f in reg["factions"]["instances"]}
        temple = next((p["name"] for p in reg["places"] if p["id"] in (hav + ".temple", hav + ".shrine")), "the shrine")
        what = {"alarm": "a war-band of {}".format(fac.get("threat", "the enemy")),
                "omen": "a sign of {}".format(reg["situations"][0]["title"].lower()),
                "theft": "the relic of {} from {}".format(reg["keepers"][0]["name"].split(",")[0], temple)}[option]
        subject = {"id": f"{tag}.{option}.subject", "role": sub["role"], "words": what}
    used = {subject["id"]}
    # 2-3. placements
    reporter = next((n for n in reg["npcs"] if n["home"] == place and n["id"] not in used and n.get("depth") != "walk_on"),
                    None) or walk_on(reg, seed, f"{tag}_reporter", "reporter", place)
    used.add(reporter["id"])
    witness = cast_pick(d, [n for n in locals_ if n["id"] not in used and n["home"] != place],
                        lambda n: 1 + (2 if n["home"] in blds else 0)) \
        or walk_on(reg, seed, f"{tag}_witness", "witness", next(b for b in blds if b != place))
    used.add(witness["id"])
    third = next(b for b in blds + [hav] if b not in (place, witness["home"]))
    issuer = next((f["name"] for f in reg["factions"]["instances"] if f["id"].endswith(".rulers")), "the rulers")
    doc = make_document(reg, seed, f"{tag}_notice", "bounty" if sub["kind"] == "person" else "warning", third, issuer,
                        (reporter["name"], P[place]["name"]), subject["words"])
    way = lead_holder_place(reg, lead_target)
    seer = cast_pick(d, [n for n in locals_ if n["id"] not in used and n["home"] != way],
                     lambda n: 3 if place_type(P[n["home"]]) in ("gate", "inn", "market") else 1) \
        or walk_on(reg, seed, f"{tag}_seer", "witness", next(b for b in blds if b != place))
    used.add(seer["id"])
    cid = f"case.{tag}.{option}"
    key = cid.split(".", 1)[1]

    def pl(node: int, i: int, holder: str, hk: str, method: str, access: str, at: str | None, content: str) -> Rec:
        return {"id": f"clu.{key}.n{node:d}.p{i:d}", "holder": holder, "holder_kind": hk, "method": method,
                "access": access, "at": at, "content": content, "status": "unfound", "sealed": True}

    n1 = "{}: {}".format(subject["role"], subject["words"])
    n2 = "the way on: toward {}".format(P[way]["name"])
    nodes = [
        {"id": f"clu.{key}.n1", "fact": n1, "necessary": True, "points_to": [f"clu.{key}.n2"],
         "placements": [pl(1, 1, reporter["id"], "person", "inquiry", "core", place, n1),
                        pl(1, 2, witness["id"], "person", "inquiry", "rolled", witness["home"], n1),
                        pl(1, 3, doc["id"], "document", "search", "rolled", third, n1)],
         "reserve": [pl(1, 9, f"reserve.{tag}.n1", "person", "inquiry", "core", None, n1)]},
        {"id": f"clu.{key}.n2", "fact": n2, "necessary": True, "points_to": [],
         "placements": [pl(2, 1, way, "place", "search", "core", way, n2),
                        pl(2, 2, seer["id"], "person", "inquiry", "rolled", seer["home"], n2),
                        pl(2, 3, f"obj.{tag}.left", "object", "search", "rolled", place if place != way else third, n2)],
         "reserve": [pl(2, 9, f"reserve.{tag}.n2", "person", "inquiry", "core", None, n2)]},
    ]
    case: Rec = {"id": cid, "profile": "reduced", "trigger": tag, "option": option, "opening_place": place,
                 "solution": {"subject": subject, "leads_to": lead_target, "sealed": True}, "nodes": nodes,
                 "fallbacks": [{"trigger": "stalled", "form": "tbl.15.fallback_form",
                                "delivers": "the core placement of an unfound necessary node"}],
                 "audit": "h.15.placement_audit", "basis": ["PR-15-6", "15.9.4", "12.16.16"]}
    reg["seed_cases"] = [c for c in reg.get("seed_cases") or [] if c["id"] != cid] + [case]  # the records
    reg["cases"] = [c for c in reg.get("cases") or [] if c != cid] + [cid]
    return case


def validate_case(case: Rec) -> list[str]:  # rule: 15.9.4
    """15.9.4 with investigation.yaml#reduced_case's numbers. Returns the failures (empty = valid)."""
    RCASE = pack_data().RCASE
    v, bad = RCASE["per_necessary_node"], []
    nec = [n for n in case["nodes"] if n["necessary"]]
    if len(nec) != RCASE["necessary_nodes"]:
        bad.append(f"nodes {len(nec):d}")
    for n in nec:
        pls = n["placements"]
        for what, val, lo in (("placements", len(pls), v["min_placements"]),
                              ("holder kinds", len({p["holder_kind"] for p in pls}), v["min_holder_kinds"]),
                              ("methods", len({p["method"] for p in pls}), v["min_method_kinds"]),
                              ("core", sum(p["access"] == "core" for p in pls), v["min_core"]),
                              ("places", len({p["at"] for p in pls}), v["min_places"]),
                              ("reserve", len(n["reserve"]), v["reserve"])):
            if val < lo:
                bad.append(f"{n['id']} {what} {val:d} < {lo:d}")
    if not any(p["access"] == "core" and p["at"] == case["opening_place"] for p in nec[0]["placements"]):
        bad.append("no core placement at the opening place")
    if len(case["fallbacks"]) < RCASE["per_case"]["min_fallbacks"]:
        bad.append("fallbacks")
    return bad


# ------------------------------------------------------------------------------------------- reading


def cases(state: Any) -> dict[str, Rec]:
    """The reduced cases in the store (meta `world.cases`), by id."""
    return dict(state.meta.get(CASES) or {})


# A story-role question (PR-12-10 step 1) and the reduced_case subject that answers it
_OPTION_WORDS = (("missing", "missing taken kidnapped vanished disappeared lost"), ("duel", "challenger duel"),
                 ("dying_messenger", "messenger message sent rider"), ("refugees", "refugee refugees lead leads"),
                 ("offer", "offer offers work hire"))


def story_option(role_words: str) -> str | None:
    """The reduced-case subject option a "who ..." question asks about, else None (casting answers it)."""
    have = words.content(role_words)
    return next((opt for opt, ws in _OPTION_WORDS if have & words.content(ws)), None)


def case_covering(state: Any, role_words: str) -> Rec | None:  # rule: PR-12-10
    """The existing case whose subject role answers the question ("who is missing" -> the missing-person case)."""
    opt = story_option(role_words)
    for c in cases(state).values():
        sub = c["solution"]["subject"]
        if (opt and c["option"] == opt) or words.covers(str(sub["role"]), role_words):
            return c
    return None


def about_line(state: Any, case: Rec, node: Rec, placement: Rec | None = None) -> str:  # rule: PR-12-10
    # rule: 15.9.5
    """What a question must be about to reach a placement (`investigation.yaml` placement `about`; DL-15-40): its
    authored `about`, else the node's question (the words before ":"), never its answer, with the matter it belongs
    to (the incident's text, or the question that built the case). The clue judgment reads only this line."""
    if placement is not None and placement.get("about"):
        return str(placement["about"])
    q = str(node["fact"]).split(":", 1)[0].strip()
    if q == "the way on":
        q = "where the matter leads next (the way on)"
    inc = ((state.meta.get("world.opening") or {}).get("inciting") or {}) if state is not None else {}
    matter = str(inc.get("text") or "") if case.get("trigger") == "incident" else str(case.get("about") or "")
    return f"{q} (the matter: {matter})" if matter else q


def pointer(case: Rec, node_id: str | None = None, *, asked: str | None = None, state: Any = None) -> str | None:
    # rule: PR-12-10
    """Who (or where) to send the PC for a node of `case` (default: the first unfound necessary node): the holder of
    its core placement first, since it cannot fail (15.9.5; R2-D), else a live holder; never `asked` itself."""
    nodes = [n for n in case["nodes"] if n["necessary"]]
    node = next((n for n in nodes if n["id"] == node_id), None) if node_id else \
        next((n for n in nodes if not n.get("found")), nodes[0])
    if node is None:
        return None
    live = [p for p in node["placements"] if p["holder"] != asked and p.get("status") != "lost"
            and (state is None or _live(state, p))]
    core = [p for p in live if p["access"] == "core"]
    pick = core or live
    return pick[0]["holder"] if pick else None


def _live(state: Any, p: Rec) -> bool:
    """A placement still reachable (15.9.4 audit): its holder exists and is not dead, destroyed or departed."""
    from engine.gen.cast import alive

    if p.get("status") == "lost":
        return False
    if p["holder"] not in state.entities:
        return p["holder_kind"] == "object"  # a trace left at a place is a search target, not an entity
    return alive(state, p["holder"])


# ------------------------------------------------------------------------------------------- the store


def write_walk_ons(tx: Any, walk_ons: list[Rec], *, source: str = "seed", unplaced: Collection[str] = ()) -> None:
    # rule: 12.11.1
    """The walk-ons a case or a hook's terms made, as unintroduced NPC entities at their homes (`unplaced`: a missing
    person is not placed anywhere; a dead one lies where it fell)."""
    st = tx.state
    for n in walk_ons:
        if n["id"] in st.entities:
            continue
        data = {k: v for k, v in n.items() if k not in ("id", "name", "exists", "kind")}
        data["name_known"] = False  # 12.10.2
        tx.add(Event.of("entity_created", source=source, rule_id="12.11.1", entity=EntityRecord(
            id=n["id"], kind="npc", name=n["name"], visibility="background", exists=n.get("exists") or "exists",
            data=data)))
        if n.get("home") in st.entities and n["id"] not in unplaced:
            tx.add(Event.of("position_set", source=source, rule_id="12.11.1", entity=n["id"], location=n["home"]))


def write_documents(tx: Any, docs: list[Rec], *, source: str = "seed") -> None:  # rule: 12.16.16
    """A document is an object entity with a `text` fact, written when it is made, so reading it delivers its words
    (a notice, or a gate log, a muster notice, a letter that a hook's terms made: spec 029)."""
    st = tx.state
    for doc in docs:
        if doc["id"] in st.entities:
            continue
        data = {"document": doc["option"], "table": doc["table"]}
        if doc.get("aliases"):
            data["aliases"] = list(doc["aliases"])
        tx.add(Event.of("entity_created", source=source, rule_id="12.16.16", entity=EntityRecord(
            id=doc["id"], kind="object", name=doc.get("name") or "{} notice".format(doc["option"]),
            visibility="available", data=data)))
        tx.add(fact(tx, doc["id"], "text", doc["text"], rule_id="12.16.16", source="data", visibility="available",
                    event_source=source))
        if doc.get("at") in st.entities:
            tx.add(Event.of("position_set", source=source, rule_id="12.16.16", entity=doc["id"], location=doc["at"]))


def write_seeded(tx: Any, rec: Rec, *, source: str = "seed") -> None:  # rule: 12.16.16
    """Write a packed record's case walk-ons, documents and case records into the store (seed time, or the new
    parts of an on-demand case). A missing person is not placed anywhere: they are missing."""
    st = tx.state
    missing = {c["solution"]["subject"]["id"] for c in rec.get("seed_cases") or [] if c["option"] == "missing"}
    write_walk_ons(tx, rec.get("walk_ons") or [], source=source, unplaced=missing)
    write_documents(tx, rec.get("documents") or [], source=source)
    if rec.get("seed_cases"):
        merged = cases(st) | {c["id"]: c for c in rec["seed_cases"]}
        tx.add(meta(CASES, merged, "PR-15-6", source))
    from engine.gen.hooks import write_terms

    write_terms(tx, rec, source=source)  # PR-11-5 step 1: the hooks' terms, as their knowers' knowledge (DL-12-109)


def world_rec(state: Any) -> Rec:
    """A region-record view of the store, as much as `reduced_case` reads (places, cast, factions, names)."""
    from engine.gen.cast import base_pool, home_of

    places = [{"id": i, "name": e.name, **{k: e.data.get(k) for k in ("place_kind", "parent", "ring")}, "links": []}
              for i, e in state.entities.items() if e.kind == "place" and e.exists == "exists"]
    npcs = [{"id": i, "name": state.entities[i].name, "role": str(state.entities[i].data.get("role") or ""),
             "home": home_of(state, i), "member_of": list(state.entities[i].data.get("member_of") or []),
             "depth": state.entities[i].data.get("depth")} for i in base_pool(state, active_pc(state))]
    facs = [{"id": i, "name": e.name, "goal": {}} for i, e in state.entities.items() if e.kind == "faction"]
    sits = [{"id": e.data.get("seed_id"), "region": e.data.get("points_to"), "title": e.data.get("text") or e.name}
            for e in state.entities.values() if e.kind == "thread" and e.data.get("thread_kind") == "situation"]
    op = state.meta.get("world.opening") or {}
    keepers = state.meta.get("world.keepers") or [{"name": "the keeper"}]
    region = state.meta.get("world.region") or {}
    return {"region": {"haven": region.get("haven")}, "places": places, "npcs": npcs,
            "factions": {"instances": facs}, "situations": sits or [{"id": "", "region": None, "title": "the wound"}],
            "keepers": keepers, "names": state.meta.get("world.names") or [],
            "calendar": {"opening_date": str((op.get("start") or {}).get("date") or "")},
            "seed_cases": [], "cases": [], "walk_ons": [], "documents": []}


def case_for_question(tx: Any, role_words: str, place: str | None, *, lead_target: str | None = None) -> Rec | None:
    # rule: PR-15-6
    """A story-role question with no case behind it (PR-12-10 step 1): build the reduced case now, with its entry
    core placement at `place` (where it was asked, else the haven), and write it. None when the question names no
    reduced-case subject or the store has no seeded haven to build in. An existing case is returned as is."""
    st = tx.state
    found = case_covering(st, role_words)
    if found is not None:
        return found
    opt = story_option(role_words)
    reg = world_rec(st)
    hav = reg["region"]["haven"]
    P = {p["id"]: p for p in reg["places"]}
    blds = [p for p in P if P[p].get("parent") == hav and P[p].get("place_kind") == "building"]
    if opt is None or hav not in P or len(blds) < 3 or not reg["names"]:
        return None
    place = str(place if place in P and in_haven(reg, place) else hav)
    target = lead_target or next((p["id"] for p in reg["places"] if p.get("place_kind") == "site" and p.get("ring") == 1),
                                 hav)
    seed = (st.meta.get("world.seed") or {}).get("seed")
    tag = f"q{len(cases(st)) + 1:d}"
    case = reduced_case(reg, seed, opt, place, target, tag=tag)
    case["about"] = role_words  # the matter its about lines name (`about_line`)
    write_seeded(tx, reg, source="engine")
    return case


def mark_found(tx: Any, case_id: str, node_id: str, placement_id: str | None = None, *,
               fact_id: str | None = None) -> None:  # rule: 15.9.5
    """A node's answer was delivered: the node is found (with the fact that told it, and the placement that
    delivered it, if named)."""
    allc = cases(tx.state)
    c = allc.get(case_id)
    if c is None:
        return
    c = _copy(c)
    for n in c["nodes"]:
        if n["id"] == node_id:
            n["found"] = True
            if fact_id:
                n["fact_id"] = fact_id
            for p in n["placements"]:
                if p["id"] == placement_id:
                    p["status"] = "found"
    allc[case_id] = c
    tx.add(meta(CASES, allc, "15.9.5"))


def audit_cases(tx: Any, emit: Any = None) -> list[str]:  # rule: 15.9.4
    """h.15.placement_audit for reduced cases: every unfound necessary node keeps `MIN_LIVE` live placements; below
    that the reserve is placed (a new witness in the haven), then a PR-15-7 generic placement. `emit` stages events
    (a handler's `ctx.emit`); default `tx.add`. Returns what was placed, in words."""
    add = emit or (lambda *evs: [tx.add(e) for e in evs])
    st = tx.state
    allc = cases(st)
    placed: list[str] = []
    reg: Rec | None = None
    for cid, c0 in allc.items():
        c = _copy(c0)
        changed = False
        for n in c["nodes"]:
            if not n.get("necessary") or n.get("found"):
                continue
            live = [p for p in n["placements"] if _live(st, p)]
            while len(live) < MIN_LIVE:
                reg = reg if reg is not None else world_rec(st)
                hav = reg["region"]["haven"]
                if hav is None or not reg["names"]:
                    break
                k = len(n.get("audit_log") or []) + 1
                spare = next((r for r in n["reserve"] if r.get("status") != "placed"), None)
                tag = "{}_{}_a{:d}".format(cid.split(".", 1)[1].replace(".", "_"), n["id"].rsplit(".", 1)[1], k)
                home = next((p["id"] for p in reg["places"] if p.get("parent") == hav and p.get("place_kind") == "building"
                             and p["id"] not in {q["at"] for q in n["placements"]}), hav)
                w = walk_on(reg, (st.meta.get("world.seed") or {}).get("seed"), tag, "witness", home)
                if spare is not None:
                    spare["status"] = "placed"
                    p = dict(spare, id=spare["id"] + f".{k:d}", holder=w["id"], at=home, status="unfound")
                    how = "reserve"
                else:  # PR-15-7: a generic placement once the reserve is spent
                    p = {"id": "{}.g{:d}".format(n["id"], k), "holder": w["id"], "holder_kind": "person",
                         "method": "inquiry", "access": "core", "at": home, "content": n["fact"], "status": "unfound",
                         "sealed": True}
                    how = "PR-15-7"
                n["placements"].append(p)
                n.setdefault("audit_log", []).append({"placed": p["id"], "how": how})
                live.append(p)
                placed.append(f"{n['id']}: {how} witness {w['name']} at {home}")
                changed = True
        if changed:
            allc[cid] = c
    if reg is not None and reg.get("walk_ons"):
        for n in reg["walk_ons"]:
            data = {k: v for k, v in n.items() if k not in ("id", "name", "exists", "kind")} | {"name_known": False}
            add(Event.of("entity_created", source="engine", rule_id="15.9.4", entity=EntityRecord(
                id=n["id"], kind="npc", name=n["name"], visibility="background", data=data)))
            add(Event.of("position_set", source="engine", rule_id="15.9.4", entity=n["id"], location=n["home"]))
    if placed:
        add(meta(CASES, allc, "15.9.4"))
    return placed


def place_on(tx: Any, node_id: str, holder: str, *, at: str | None = None) -> str | None:  # rule: 15.9.4
    """[spec 033 R4] The DM's own person or item holds necessary node `node_id`: the node's unplaced reserve entry
    (else a PR-15-7 generic placement) is placed on `holder`, at `at` (default the holder's place). Nothing is
    created and nothing is guessed. Returns the placement id, or None when no case holds that node."""
    allc = cases(tx.state)
    for cid, c0 in allc.items():
        c = _copy(c0)
        node = next((n for n in c["nodes"] if n["id"] == node_id), None)
        if node is None:
            continue
        pos = tx.state.positions.get(holder)
        where = at or (pos.location if pos is not None else None)
        person = tx.state.entities[holder].kind in ("npc", "companion", "adversary")
        k = len(node.get("audit_log") or []) + 1
        spare = next((r for r in node["reserve"] if r.get("status") != "placed"), None)
        if spare is not None:
            spare["status"] = "placed"
            p = dict(spare, id=spare["id"] + f".{k:d}", holder=holder, holder_kind="person" if person else "object",
                     at=where, status="unfound")
            how = "reserve"
        else:
            p = {"id": f"{node_id}.g{k:d}", "holder": holder, "holder_kind": "person" if person else "object",
                 "method": "inquiry" if person else "search", "access": "core", "at": where, "content": node["fact"],
                 "status": "unfound", "sealed": True}
            how = "PR-15-7"
        node["placements"].append(p)
        node.setdefault("audit_log", []).append({"placed": p["id"], "how": how, "by": "dm"})
        allc[cid] = c
        tx.add(meta(CASES, allc, "15.9.4"))
        return str(p["id"])
    return None


def _copy(c: Rec) -> Rec:
    import copy

    return copy.deepcopy(c)


__all__ = ["CASES", "MIN_LIVE", "about_line", "audit_cases", "case_covering", "case_for_question", "cases", "mark_found", "pointer",
           "reduced_case", "story_option", "validate_case", "world_rec", "write_seeded"]
