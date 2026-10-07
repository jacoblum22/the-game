"""The thirteen steps of the world seed (PR-12-9, 12.16.4-12.16.16), one function per step.

A line-for-line port of `_process/simulation/12-world-seed.py#build_seed`, cut at its step boundaries. Every
step reads and writes one state dict `st` (so a step can be snapshotted, vetoed and re-run) and draws from the
main stream in the reference's order. Two departures from the data's grouping, both the reference's: the haven
site (`ws.q.haven_site`, listed under step 6) is asked in step 5 because the ring-1 terrain reads it, and the
far rings' powers (12.16.11) are drawn at the end of step 13 on their own stream.
"""

from __future__ import annotations

import itertools
import re
from collections import Counter
from typing import Any

from engine.gen import threat_table as TB
from engine.gen._seed_lib import (
    BRANCHES,
    PLURAL,
    Answers,
    Dice,
    Names,
    Rec,
    anc,
    by_range,
    data,
    fill_pitch,
    in_range,
    link,
    make_npc,
    name_tables,
    oracle_simple,
    person_name,
    place_record,
    role_license,
    slug,
    step_to,
    template_for,
)

# The questions each step asks, in the order the reference asks them (T-12-15; see the module doc).
STEP_QUESTIONS: dict[int, list[str]] = {
    1: ["ws.q.wound", "ws.q.climate"],
    2: ["ws.q.magic_level", "ws.q.magic_law", "ws.q.spirits", "ws.q.arcane_source", "ws.q.extra_impossible",
        "ws.q.regrowth", "ws.q.closed_school", "ws.q.relics_magic", "ws.q.hybrid_none"],
    3: ["ws.q.keeper_count", "ws.q.keepers", "ws.q.bargainer"],
    4: ["ws.q.presence", "ws.q.second_tongue"],
    5: ["ws.q.haven_site", "ws.q.terrain"],
    6: ["ws.q.haven_tier"],
    7: ["ws.q.rulers", "ws.q.fourth_faction"],
    8: [], 9: [], 10: [], 11: [],
    12: ["ws.q.month_names"],
    13: ["ws.q.inciting"],
}


def new_state() -> Rec:
    return {"S": {"_npc_ids": set(), "_routes": [], "_places": {}, "names": [], "npcs": [], "clocks": [],
                  "_given_used": set()},
            "ctx": {}, "names_used": set(), "log": []}


def step1_premise(st: Rec, dice: Dice, A: Answers, names: Names, era_dice: Dice) -> None:
    """# rule: 12.16.4 -- the wound, the climate, the region's name and the wound's age."""
    D, S, ctx = data(), st["S"], st["ctx"]
    wtab = D.TAB["tbl.12.seed.wound"]
    wound_opt = A.get("ws.q.wound", lambda: by_range(wtab["results"], dice.d(12))["option"])
    wound = next(r for r in wtab["results"] if r["option"] == wound_opt)
    climate = A.get("ws.q.climate", lambda: oracle_simple(dice, D.QS["ws.q.climate"]))
    region_name = names.region()
    rs = slug(region_name.replace("the ", ""))
    S["_rs"] = rs
    lo, hi = wound["era_years"]
    ctx["era_age"] = era_dice.rng.randint(lo, hi)
    ctx.update({"ws.q.wound": wound_opt, "ws.q.climate": climate})
    st.update(wound_opt=wound_opt, wound=wound, climate=climate, region_name=region_name, rs=rs)


def step2_canon(st: Rec, dice: Dice, A: Answers, names: Names) -> None:
    """# rule: 12.16.5 -- what is impossible, and how magic works."""
    D, ctx = data(), st["ctx"]
    QS = D.QS
    lvl = A.get("ws.q.magic_level", lambda: oracle_simple(dice, QS["ws.q.magic_level"]))
    ctx["ws.q.magic_level"] = lvl
    law = A.get("ws.q.magic_law", lambda: oracle_simple(dice, QS["ws.q.magic_law"], ctx))
    spirits = A.get("ws.q.spirits", lambda: oracle_simple(dice, QS["ws.q.spirits"], ctx))
    arcane_src = A.get("ws.q.arcane_source", lambda: oracle_simple(dice, QS["ws.q.arcane_source"]))

    def _extra() -> list[str]:
        r = by_range(QS["ws.q.extra_impossible"]["oracle"]["results"], dice.d(6))
        if r.get("option") == "none":
            return []
        return [x["option"] for x in dice.sample(D.TAB["tbl.12.seed.extra_impossible"]["results"], r["count"])]

    extra = A.get("ws.q.extra_impossible", _extra)
    regrowth = A.get("ws.q.regrowth", lambda: oracle_simple(dice, QS["ws.q.regrowth"]))
    closed_opt = A.get("ws.q.closed_school", lambda: oracle_simple(dice, QS["ws.q.closed_school"]))
    closed = next((o.get("school") for o in QS["ws.q.closed_school"]["options"] if o["id"] == closed_opt), None) or "none"
    relics = A.get("ws.q.relics_magic", lambda: oracle_simple(dice, QS["ws.q.relics_magic"]))
    hybrid = A.get("ws.q.hybrid_none", lambda: oracle_simple(dice, QS["ws.q.hybrid_none"]))
    ci = [{"id": "ci." + c["key"], "text": c["text"], "scope": c["scope"], "basis": c["basis"]}
          for c in D.DEF["canon_impossible"]]
    for e in extra:
        row = next(r for r in D.TAB["tbl.12.seed.extra_impossible"]["results"] if r["option"] == e)
        ci.append({"id": "ci." + e, "text": row["text"], "scope": row["scope"], "basis": ["12.16.5", "05.7.10 item 1"]})
    arc_text = {"anyone_literate": D.DEF["sources"]["arcane"],
                "order_only": "only those the region's arcane order admits; a teacher outside it is a crime and a text is "
                              "contraband",
                "gifted_only": "only those born with the gift (a birth gift or a Touched spark naming arcane)"}[arcane_src]
    spirit_odds = {"rare": "Unlikely in any given place; Likely at a place with resonance",
                   "uncommon": "Even in wild places; Likely at a place with resonance",
                   "common": "Likely anywhere wild; Certain at a place with resonance"}[spirits]
    st.update(lvl=lvl, law=law, spirits=spirits, arcane_src=arcane_src, extra=extra, regrowth=regrowth, closed=closed,
              relics=relics, hybrid=hybrid, ci=ci, arc_text=arc_text, spirit_odds=spirit_odds)


def step3_faith(st: Rec, dice: Dice, A: Answers, names: Names) -> None:
    """# rule: 12.16.6 -- the keepers, and who answers at death's door."""
    D, wound, closed = data(), st["wound"], st["closed"]
    nk = int(A.get("ws.q.keeper_count", lambda: oracle_simple(dice, D.QS["ws.q.keeper_count"])))
    forms_all = D.TAB["tbl.12.seed.keeper_form"]["results"]

    def _forms() -> list[str]:
        chosen: list[str] = []
        while len(chosen) < nk:
            items = [(f["option"], 3 if f["option"] in wound["keeper_bias"] else 1) for f in forms_all
                     if f["option"] not in chosen]
            chosen.append(dice.weighted(items))
        return chosen

    forms = A.get("ws.q.keepers", _forms)
    keepers: list[Rec] = []
    human = D.TAB["tbl.12.seed.names"]["by_people"]["orig.people.human"]["styles"][0]
    for fo in forms:
        f = next(x for x in forms_all if x["option"] == fo)
        nm = names.compose(human["given_start"], human["given_end"])
        title = dice.pick(f["title"])
        kid = f"keeper.{slug(nm)}"
        po = f.get("pole_override") or {}
        axes = [{"axis": a, "pole": po.get(a, "+")} for a in f["axes"]]
        despises = [{"axis": a, "pole": "+" if po.get(a) == "-" else "-"} for a in f["despises"]]
        keepers.append({"id": kid, "name": f"{nm}, {title}", "kind": f["kind"], "form": fo, "what": f["what"],
                        "axes": axes, "despises": despises, "sign": f["sign"],
                        "schools": [s for s in f["schools"] if s != closed], "faith": None, "faith_org": f["faith_org"],
                        "death": bool(f.get("death")), "nature": f.get("nature", "sacred"),
                        "basis": ["05.7.4", "04.9.2", "12.16.6"]})
    main_keeper = next((k for k in keepers if k["nature"] != "profane"), keepers[0])
    barg = A.get("ws.q.bargainer", lambda: oracle_simple(dice, D.QS["ws.q.bargainer"]))
    death_k = next((k for k in keepers if k["death"]), None)
    if barg == "death_keeper":
        bargainer = {"who": death_k["id"] if death_k else None,
                     "text": ("{} answers at the door of death (07.5.5)".format(death_k["name"])) if death_k
                     else "no one: the land has no keeper of death"}
    elif barg == "fey":
        bargainer = {"who": "arch.fey_noble",
                     "text": "a fey lord of the borderlands answers, for a price paid later (arch.fey_noble, can_bargain)"}
    elif barg == "fiend":
        bargainer = {"who": "arch.tempter", "text": "a tempter answers, and collects (arch.tempter, can_bargain)"}
    else:
        bargainer = {"who": None, "text": "no one answers at the door of death"}
    st.update(keepers=keepers, main_keeper_i=keepers.index(main_keeper), bargainer=bargainer)


def _main_keeper(st: Rec) -> Rec:
    return st["keepers"][st["main_keeper_i"]]


def step4_peoples(st: Rec, dice: Dice, A: Answers, names: Names) -> None:
    """# rule: 12.16.7 -- which peoples live here, their name tables, and the tongues."""
    D, S, wound, keepers, rs, region_name = data(), st["S"], st["wound"], st["keepers"], st["rs"], st["region_name"]

    def _presence() -> dict[str, str]:
        out: dict[str, str] = {}
        cols = ["absent", "rare", "uncommon", "common"]
        for pid, rows in D.TAB["tbl.12.seed.presence"]["by_people"].items():
            pres = by_range(rows, dice.d(6))["present"]
            folk = [t for t in D.ORIGD[pid]["tags"] if t.startswith("creature.folk")]
            if any(anc(f, g) or anc(g, f) for f in folk for g in wound["gates"]) and pid != "orig.people.human":
                pres = cols[min(3, cols.index(pres) + 1)]
            out[pid] = pres
        if not any(v != "absent" for k, v in out.items() if k != "orig.people.human"):
            out["orig.people.halfling"] = "uncommon"
        return out

    presence = A.get("ws.q.presence", _presence)
    peoples: list[Rec] = []
    for pid, pres in presence.items():
        peoples.append({"origin": pid, "present": pres, "who": None, "where": [], "name_tables": [],
                        "faiths": [k["id"] for k in keepers if k["nature"] != "profane"]})
    threat_people = next((o["id"] for o in D.ORIG["origins"] if o["kind"] == "people" and o["id"] != "orig.people.human"
                          and any(anc(t, g) for t in o["tags"] if t.startswith("creature.folk") for g in wound["gates"])),
                         "orig.people.human")
    name_src = [dict(p) for p in peoples]
    for p in name_src:
        if p["origin"] == threat_people and p["present"] == "absent":
            p["present"] = "rare"
    S["names"] = name_tables(dice, names, rs, name_src)
    for p, q in zip(peoples, name_src, strict=True):
        p["name_tables"] = q["name_tables"] if p["present"] != "absent" else []
    present = [p for p in peoples if p["present"] != "absent"]
    order = {"common": 0, "uncommon": 1, "rare": 2}
    nonhuman = sorted([p for p in present if p["origin"] != "orig.people.human"],
                      key=lambda p: (order[p["present"]], p["origin"]))
    second = A.get("ws.q.second_tongue", lambda: oracle_simple(dice, D.QS["ws.q.second_tongue"]))

    def native(pid: str) -> str:
        return next(x["license"] for x in D.ORIGD[pid]["languages"] if x["grade"] == "native")

    if second == "people" and nonhuman and native(nonhuman[0]["origin"]) != "lic.lang.common":
        second_lic = native(nonhuman[0]["origin"])
        second_text = "the tongue of the land's {}".format(D.ORIGD[nonhuman[0]["origin"]]["name"].lower())
    else:
        second_lic = "lic.lang.old_tongue"
        second_text = "the Old Tongue, here the speech of the time before the {}".format(wound["era"].split("since the ")[-1].split("of the ")[-1])
    tongues: Rec = {"list": [{"license": "lic.lang.common", "region_name": f"{region_name.split()[-1]}-speech",
                              "who": "everyone"}], "second_tongue": second_lic}
    for p in present:
        lic = native(p["origin"])
        if lic != "lic.lang.common" and all(t["license"] != lic for t in tongues["list"]):
            tongues["list"].append({"license": lic, "region_name": None,
                                    "who": "the {} of {}".format(PLURAL[p["origin"]], region_name)})
    if all(t["license"] != second_lic for t in tongues["list"]):
        tongues["list"].append({"license": second_lic, "region_name": None, "who": second_text})
    tongues["list"].append({"license": "lic.lang.cant", "region_name": None,
                            "who": "thieves and smugglers, wherever they are"})
    st.update(peoples=peoples, threat_people=threat_people, nonhuman_origins=[p["origin"] for p in nonhuman],
              tongues=tongues)


def _present(st: Rec) -> list[Rec]:
    return [p for p in st["peoples"] if p["present"] != "absent"]


def step5_land(st: Rec, dice: Dice, A: Answers, names: Names) -> None:
    """# rule: 12.16.8 -- the region, its rings of areas, and the routes between them."""
    D, S = data(), st["S"]
    climate, wound, rs, region_name = st["climate"], st["wound"], st["rs"], st["region_name"]
    tbc = D.TAB["tbl.12.seed.terrain_by_climate"]
    rings_t = D.TRAVEL["rings"]
    terrain_by_ring: dict[int, list[str]] = {}
    hs_opt = A.get("ws.q.haven_site", lambda: by_range(D.TAB["tbl.12.seed.haven_site"]["results"], dice.d(8))["option"])
    hsite = next(r for r in D.TAB["tbl.12.seed.haven_site"]["results"] if r["option"] == hs_opt)

    def _terrain() -> dict[int, list[str]]:
        out = {1: list(tbc["ring1"][climate])}
        for ring in range(2, 6):
            out[ring] = [by_range(tbc["climates"][climate], dice.d(12))["terrain"]
                         for _ in range(D.DEF["areas_per_ring"][ring])]
        return out

    tbr = A.get("ws.q.terrain", _terrain)
    region_id = f"loc.{rs}"
    P = S["_places"]
    assert region_id not in P, region_id
    P[region_id] = place_record(region_id, region_name.title().replace("The ", "The "), "region", None, None, 2, "wild",
                                [tbr[2][0]], climate, wound["text"])
    P[region_id]["discovered"] = True
    areas_by_ring: dict[int, list[str]] = {}
    for ring in range(1, 6):
        rdef = rings_t[ring]
        areas_by_ring[ring] = []
        for i in range(D.DEF["areas_per_ring"][ring]):
            primary = tbr[ring][i % len(tbr[ring])] if ring > 1 else tbr[1][i % len(tbr[1])]
            terr = [primary]
            if ring == 1 and hsite["terrain"][0].startswith("terrain.water") and i == 0:
                terr.append(hsite["terrain"][0])
            hb = rdef["home_band"]
            band = hb[0] if len(hb) == 1 else (hb[0] if dice.d(6) <= 3 else hb[1])
            if ring == 5 and i == D.DEF["areas_per_ring"][5] - 1 and all(P[x]["band"] < 5 for x in areas_by_ring[5]):
                band = 5
            r3 = "wild" if dice.d(6) <= 3 else "perilous"     # the reference rolls this d6 for every area
            danger = {1: "settled", 2: "wild", 3: r3, 4: "perilous", 5: "deadly"}[ring]
            nm = names.area(primary)
            aid = "loc.{}_{}".format(rs, slug(nm.replace("the ", "")))
            rec = place_record(aid, nm[0].upper() + nm[1:], "area", region_id, ring, band, danger, terr, climate,
                               "{}, {}".format(nm, rdef["words"]))
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
                if not any(x["to"] == ids[j] for x in P[ids[i]]["links"]):
                    link(S, ids[i], ids[j], dice.pick(D.DEF["watches_between"]["same_ring"]),
                         "track" if ring <= 2 else "trackless", P[ids[i]]["terrain"][0])
        if ring > 1:
            for a in ids:
                b = dice.pick(areas_by_ring[ring - 1])
                link(S, a, b, dice.pick(D.DEF["watches_between"]["next_ring"]), "track" if ring <= 3 else "trackless",
                     P[a]["terrain"][0])
    st.update(hs_opt=hs_opt, hsite=hsite, region_id=region_id, areas_by_ring=areas_by_ring,
              terrain_by_ring=terrain_by_ring)


def step6_haven(st: Rec, dice: Dice, A: Answers, names: Names) -> None:
    """# rule: 12.16.9 -- the haven, its buildings, a place of acceptance, fight locations and stock."""
    D, S, ctx = data(), st["S"], st["ctx"]
    rs, climate, hsite, region_name = st["rs"], st["climate"], st["hsite"], st["region_name"]
    areas_by_ring, main_keeper, closed = st["areas_by_ring"], _main_keeper(st), st["closed"]
    P = S["_places"]
    tier = A.get("ws.q.haven_tier", lambda: oracle_simple(dice, D.QS["ws.q.haven_tier"]))
    ctx["ws.q.haven_tier"] = tier
    hname = names.place()
    hid = f"loc.{rs}_{slug(hname)}"
    host = areas_by_ring[1][0]
    assert hid not in P, hid
    P[hid] = place_record(hid, hname, "settlement", host, 0, None, "safe", ["terrain.settlement." + tier] + hsite["terrain"],
                          climate, "a {} {}, the haven of {}".format("walled town" if tier == "town" else "village",
                                                                 hsite["text"], region_name),
                          safe=True, rest_site="haven", settlement_scope=hid, discovered=True, water_source=True,
                          grazing=False)
    P[hid]["openness"] = "broken"
    for a in areas_by_ring[1]:
        link(S, hid, a, dice.pick([1, 2]), "road", P[a]["terrain"][0])
        P[a]["settlement_scope"] = hid
    hdef = D.DEF["haven_by_tier"][tier]
    blds: dict[str, str] = {}
    kname = main_keeper["name"].split(",")[0]
    for b in hdef["buildings"]:
        # the reference names an inn (two picks) for every building, and keeps it only for the inn
        inn = "the {} {}".format(dice.pick(["Drowned", "Golden", "Old", "Blue", "Crooked", "Last", "Sleeping", "Red"]),
                             dice.pick(["Lamb", "Lantern", "Plough", "Bell", "Stag", "Barrel", "Hound", "Goose"]))
        bname = {"temple": f"the temple of {kname}", "shrine": f"the shrine of {kname}", "inn": inn,
                 "smithy": "the smithy", "hall": "the hall", "gate": hsite["feature"], "market": "the market square",
                 "healer": "the healer's house"}[b]
        bid = f"{hid}.{b}"
        assert bid not in P, bid
        P[bid] = place_record(bid, bname, "building", hid, 0, None, "safe", ["terrain.settlement." + tier], climate, bname,
                              safe=True, rest_site="haven" if b == "inn" else None, settlement_scope=hid, discovered=True)
        P[bid]["openness"] = "closed"
        blds[b] = bid
    holy = blds.get("temple") or blds["shrine"]
    P[holy]["facts"]["consecrated"] = True
    P[holy]["resonance"] = ["deed.divine"]
    gy = f"{hid}.graveyard"
    assert gy not in P, gy
    P[gy] = place_record(gy, "the graveyard", "building", hid, 0, None, "safe", ["terrain.settlement." + tier], climate,
                         f"the graveyard, tended by the faithful of {kname}", safe=True, settlement_scope=hid,
                         discovered=True)
    P[gy]["facts"].update({"consecrated": True, "tended_by": None})
    acc = by_range(D.TAB["tbl.12.seed.acceptance"]["results"], dice.d(6))
    acc_area = dice.pick(areas_by_ring[1] + areas_by_ring[2])
    acc_name = acc["name"].replace("{name}", names.place())
    acc_id = "loc.{}_{}".format(rs, slug(acc_name.replace("the ", "")))
    assert acc_id not in P, acc_id
    P[acc_id] = place_record(acc_id, acc_name, "landmark", acc_area, P[acc_area]["ring"], P[acc_area]["band"], None,
                             P[acc_area]["terrain"], climate, "{}, where {} dwells".format(acc_name, acc["spirit"]),
                             resonance=["deed.primal"])
    P[acc_id]["facts"]["spirit"] = acc["spirit"]
    P[acc_area]["landmarks"].append(acc_id)
    primal = [t for t in sorted(D.TAGS) if t.startswith("deed.primal.") and t.count(".") == 2 and t != closed]
    acceptance = [{"place": acc_id, "spirit": acc["spirit"], "schools": dice.sample(primal, 3), "asks": acc["asks"],
                   "contact": None}]
    fight = [{"place": blds["gate"], "features": hsite["fight"]},
             {"place": blds["inn"], "features": ["cover: tables and the bar",
                                                 "loose objects: stools, tankards, a hearth-poker", "hazard: the hearth fire"]},
             {"place": blds.get("market", blds["hall"]),
              "features": ["open ground", "crowd: market-goers who scatter (06.3.8)", "loose objects: stalls"]}]
    rare = dice.pick(D.DEF["rare_metals"])
    stock = {"rare_metal": dict(rare, tag="material.metal.rare", where=None), "components": D.DEF["components_by_band"]}
    st.update(tier=tier, hname=hname, hid=hid, hdef=hdef, blds=blds, holy=holy, gy=gy, acc_name=acc_name, acc_id=acc_id,
              acceptance=acceptance, fight=fight, stock=stock)


def step7_factions(st: Rec, dice: Dice, A: Answers, names: Names) -> None:
    """# rule: 12.16.10 -- four factions and the minor faiths, each with a running goal clock."""
    D, S = data(), st["S"]
    tier, wound, rs, hid, hname = st["tier"], st["wound"], st["rs"], st["hid"], st["hname"]
    main_keeper, keepers, areas_by_ring = _main_keeper(st), st["keepers"], st["areas_by_ring"]
    P, FAC = S["_places"], D.FAC
    rul = A.get("ws.q.rulers", lambda: by_range(D.TAB["tbl.12.seed.rulers"]["by"][tier], dice.d(6))["org"])
    used_orgs = {rul}

    def _fourth() -> str:
        for _ in range(20):
            r = by_range(FAC["tbl.11.faction_seed"]["results"], dice.d(12))["org"]
            r = r.split(" ")[0]
            if r not in used_orgs and r != wound["threat_org"] and r != main_keeper["faith_org"]:
                return r
        return "org.guild.craft"

    fourth = A.get("ws.q.fourth_faction", _fourth)
    specs: list[tuple[str, str, int, str | None, Rec | None]] = [
        ("rulers", rul, 2 if tier == "town" else 1, hid, None),
        ("faith", main_keeper["faith_org"], 2 if tier == "town" else 1, hid, main_keeper),
        ("threat", wound["threat_org"], 2 if dice.d(6) <= 3 else 3, None, None),
        ("fourth", fourth, by_range(FAC["tbl.11.faction_tier"]["results"], dice.d(6))["tier"], hid, None)]
    for k in keepers:
        if k is not main_keeper:
            specs.append(("faith_minor", k["faith_org"], 0, hid, k))
    factions: list[Rec] = []
    for role, org, ftier, seat, kp in specs:
        t = template_for(org)
        if kp is not None and role in ("faith", "faith_minor"):
            nm = "the faithful of {}".format(kp["name"].split(",")[0])
        else:
            fn = D.TAB["tbl.12.seed.faction_names"]["by_org"]
            key = max((o for o in fn if anc(org, o)), key=lambda o: o.count("."))
            nm = dice.pick(fn[key]).replace("{haven}", hname).replace("{keeper}", main_keeper["name"].split(",")[0])
            if "{place}" in nm:
                nm = nm.replace("{place}", names.place())
        fid = "fac.{}.{}".format(rs, role if role != "faith_minor" or kp is None else "faith_" + slug(kp["name"].split(",")[0]))
        if kp is not None:
            kp["faith"] = fid
        ratings = dict(zip(["force", "cunning", "wealth", "sway"], t["ratings_by_tier"][ftier], strict=True))
        g = by_range([dict(x, range=str(x["d6"])) for x in t["goal_list"]], dice.d(6))
        if role == "threat":
            g = dict(wound["threat_goal"])
        scope = "local" if ftier <= 1 else "regional"
        segs = FAC["goal_clocks"][scope]["segments"]
        if role == "faith_minor":
            pk = by_range(FAC["petty_goals"]["kinds"], g["d6"])
            hi = max(ratings.values())
            g = {"text": pk["text"], "kind": pk["kind"],
                 "rating": next(k for k in ("force", "cunning", "wealth", "sway") if ratings[k] == hi), "petty": True}
            segs = FAC["petty_goals"]["clock"]["segments"]
        filled = dice.d(max(1, segs // 3))
        clk = {"id": "clk.{}.{}.goal".format(rs, fid.split(".")[-1]), "name": "{}: {}".format(nm, g["text"]),
               "kind": "faction_goal", "owner": fid, "segments": segs, "filled": filled, "visibility": "hidden",
               "direction": "fill", "tick_sources": FAC["goal_clocks"]["tick_sources"], "omens": t["goal_omens"],
               "basis": ["11.3.1", "PR-11-8", "12.16.10"]}
        S["clocks"].append(clk)
        full = role in ("rulers", "faith", "threat", "fourth")
        goal: Rec = {"text": g["text"], "kind": g["kind"], "scope": scope, "rating": g["rating"], "clock": clk["id"],
                     "effects": [], "target": None}
        if g.get("petty"):
            goal["petty"] = True
        fac: Rec = {
            "id": fid, "name": nm[0].upper() + nm[1:], "role": role, "tags": [org], "template": t["id"], "org_tags": [org],
            "tier": ftier, "hold": "strong", "ratings": ratings,
            "temperament": wound["threat_temperament"] if role == "threat" else t["temperament"],
            "lifecycle_stage": "rising" if role == "threat" else "flourishing", "full": full,
            "full_reason": f"tier {ftier:d} >= 2 (11.3.2)" if ftier >= 2 else
            ("an opening lead names it: a thread (11.3.2)" if full else None),
            "goal": goal, "seat": seat, "holds": [seat] if seat else [], "linchpins": [], "officers": [],
            "duties": t["duties"], "relations": {}, "status_to_pc": 0, "attention": None, "pursuit": 0,
            "ranks": t["rank_ladder"], "sittings": t["sittings"], "fields": t["fields"], "values": t["values"],
            "patron_deeds": t["patron_deeds"], "boon_base": t["boon_base"], "boon_signature": t["boon_signature"],
            "courtable": t["courtable"], "lifecycle": "provisional", "basis": ["11.3.1", "11.3.18", "PR-11-8", "12.16.10"]}
        factions.append(fac)
    for a, b in itertools.combinations(factions, 2):
        if "threat" in (a["role"], b["role"]):
            v = -2 if {"rulers", "faith"} & {a["role"], b["role"]} else (-1 if dice.d(6) <= 4 else 0)
        else:
            v = {1: -1, 6: 1}.get(dice.d(6), 0)
        if v:
            a["relations"][b["id"]] = v
            b["relations"][a["id"]] = v
    # 11.3.16: bind the petty goals' texts and targets (no dice)
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
            txt = txt.replace("{neighbor}", nb["name"][0].lower() + nb["name"][1:] if nb["name"].startswith("The ")
                              else nb["name"])
        gl["text"], gl["target"] = txt, tgt
        clk = next(c for c in S["clocks"] if c["id"] == gl["clock"])
        clk["name"] = "{}: {}".format(clk["name"].split(": ")[0], txt)
    st.update(factions=factions)


def _F(st: Rec) -> dict[str, Rec]:
    return {f["role"]: f for f in st["factions"]}


def _local_weights(st: Rec) -> list[tuple[str, int]]:
    PW = {"common": 6, "uncommon": 3, "rare": 1}
    return [(p["origin"], PW[p["present"]]) for p in _present(st)]


def step8_cast(st: Rec, dice: Dice, A: Answers, names: Names) -> None:
    """# rule: 12.16.11 -- the cast: heads and officers, the haven's people, teachers and bond placement."""
    D, S = data(), st["S"]
    blds, holy, hid, hname, tier = st["blds"], st["holy"], st["hid"], st["hname"], st["tier"]
    threat_people, region_id, acceptance = st["threat_people"], st["region_id"], st["acceptance"]
    keepers, main_keeper, factions, F = st["keepers"], _main_keeper(st), st["factions"], _F(st)
    P = S["_places"]
    local_weights = _local_weights(st)

    def people_for(role: str | None = None) -> str:
        if role == "threat":
            return threat_people
        if role in ("rulers", "faith") and threat_people != "orig.people.human":
            return dice.weighted([(o, w) for o, w in local_weights if o != threat_people])
        return dice.weighted(local_weights)

    T22 = {0: 1, 1: 2, 2: 2, 3: 3, 4: 3, 5: 4}
    for fac in factions:
        home = {"rulers": blds["hall"], "faith": holy, "fourth": blds.get("market", blds["hall"]),
                "faith_minor": holy}.get(fac["role"], None)
        head = make_npc(dice, S, role="head of {}".format(fac["name"]), people=people_for(fac["role"]), home=home or region_id,
                        member_of=[fac["id"]], band=T22[fac["tier"]] + 1, role_tags=fac["patron_deeds"][:2],
                        duty=fac["duties"][0])
        fac["officers"].append(head["id"])
        tpl = template_for(fac["org_tags"][0])
        fates = {f["fate"]: f["effects"] for f in tpl["fate_list"]}
        cons = next(f["consequence"] for f in tpl["fate_list"] if f["fate"] == "dies")
        fac["linchpins"].append({"npc": head["id"], "consequence": cons, "fates": fates, "sealed": True})
        if fac["full"]:
            off = make_npc(dice, S, role="officer of {}".format(fac["name"]), people=people_for(fac["role"]),
                           home=home or region_id, member_of=[fac["id"]], band=T22[fac["tier"]],
                           role_tags=fac["patron_deeds"][:1], duty=fac["duties"][1 % len(fac["duties"])])
            fac["officers"].append(off["id"])
    priest = next(n for n in S["npcs"] if n["id"] == F["faith"]["officers"][0])
    smith = make_npc(dice, S, role="smith", people=people_for(), home=blds["smithy"], depth="minor", band=1,
                     role_tags=["deed.craft.smithing"])
    make_npc(dice, S, role="innkeeper", people=people_for(), home=blds["inn"], depth="minor", band=1,
             role_tags=["deed.influence"])
    captain = make_npc(dice, S, role="captain of the gate", people="orig.people.human", home=blds["gate"],
                       member_of=[F["rulers"]["id"]], depth="minor", band=2,
                       role_tags=["deed.martial.polearm", "deed.martial.shield"],
                       duty="never opens the gate after the night watch",
                       recruit={"cmp": "cmp.veteran", "band": 2, "terms": "for a share and a cause the rulers approve (16.3.4)"})
    wise = make_npc(dice, S, role="wise-woman of {}".format(st["acc_name"]), people=people_for(), home=st["acc_id"],
                    depth="minor", band=1, role_tags=["deed.primal"])
    acceptance[0]["contact"] = "{} (brings candidates to the spirit)".format(wise["id"])
    make_npc(dice, S, role="sellsword between contracts", people=people_for(), home=blds["inn"], depth="minor", band=1,
             role_tags=["deed.martial.blade"], recruit={"cmp": "cmp.soldier", "band": 1, "terms": "wages (16.3.2) and a fair share"})
    scholar = None
    if tier == "town":
        scholar = make_npc(dice, S, role="scribe and teacher of letters", people=people_for(), home=blds["hall"],
                           depth="minor", band=1, role_tags=["deed.lore", "deed.craft.scribing"])
    healer = make_npc(dice, S, role="healer" if tier == "town" else "herb-wife", people=people_for(),
                      home=blds.get("healer", holy), depth="minor", band=1,
                      role_tags=["deed.wilds.foraging", "deed.craft.alchemy"])
    P[st["gy"]]["facts"]["tended_by"] = F["faith"]["id"]
    # 05.7.4: a cast NPC's divine license must be a school of a keeper whose faith it belongs to
    kof = {k["faith"]: k for k in keepers if k.get("faith")}
    for n in S["npcs"]:
        kept = {s for m in n["member_of"] if m in kof for s in kof[m]["schools"]}
        n["licenses"] = [x for x in n["licenses"] if not x["id"].startswith("lic.training.divine_")
                         or "deed.divine.{}".format(x["id"].rsplit("_", 1)[-1]) in kept]
    teachers: list[Rec] = []
    for sch in main_keeper["schools"]:
        teachers.append({"target": "lic.training.divine_{}".format(sch.split(".")[-1]), "npc": priest["id"], "grade": "expert",
                         "requires": "{} accepts the student (05.7.4)".format(main_keeper["id"])})
    teachers += [{"target": "lic.training.martial_polearm", "npc": captain["id"], "grade": "expert"},
                 {"target": "lic.training.martial_shield", "npc": captain["id"], "grade": "trained"},
                 {"target": "lic.training.craft_smithing", "npc": smith["id"], "grade": "expert" if tier == "town" else "trained"},
                 {"target": "lic.training.wilds_foraging", "npc": healer["id"], "grade": "trained"}]
    for sch in acceptance[0]["schools"]:
        teachers.append({"target": "lic.training.primal_{}".format(sch.split(".")[-1]), "npc": wise["id"], "grade": "trained",
                         "requires": "{} accepts the student (05.9.4)".format(st["acc_id"])})
    if scholar:
        teachers.append({"target": "lic.lang.letters", "npc": scholar["id"], "grade": "trained"})
        teachers.append({"target": "lic.training.lore_history", "npc": scholar["id"], "grade": "expert"})
    arcane_at = next(o for o in D.QS["ws.q.magic_level"]["options"] if o["id"] == st["lvl"])["arcane_teacher_at"]
    if (arcane_at == "village") or (arcane_at == "town" and tier == "town"):
        mage = make_npc(dice, S, role="hedge-mage", people=people_for(), home=blds["hall"], depth="minor", band=2,
                        role_tags=["deed.arcane"])
        arc = [t for t in sorted(D.TAGS) if t.startswith("deed.arcane.") and t.count(".") == 2 and t != st["closed"]]
        for sch in dice.sample(arc, 2):
            teachers.append({"target": "lic.training.arcane_{}".format(sch.split(".")[-1]), "npc": mage["id"], "grade": "trained",
                             "requires": "letters and the teacher (05.9.4)"
                             + ("; admission to the arcane order" if st["arcane_src"] == "order_only" else "")})
    for t in teachers:
        assert t["target"] in D.LICS, t["target"]
        # 15.11.1 MENTOR: the teacher's record holds the target at expert (a tongue or letters: held)
        npc = next(n for n in S["npcs"] if n["id"] == t["npc"])
        grade = "expert" if t["target"].startswith("lic.training.") else None
        have = next((x for x in npc["licenses"] if x["id"] == t["target"]), None)
        if have:
            have["grade"] = grade
        else:
            npc["licenses"].append({"id": t["target"], "grade": grade})
    bond_placement = [
        {"slot": "anchor", "kind": "kin", "where": hid, "default_npc": None,
         "note": f"a new NPC in {hname} (02.9.8: never one already in the cast)"},
        {"slot": "anchor", "kind": "friend", "where": blds["inn"], "default_npc": None,
         "note": "a regular at {}".format(P[blds["inn"]]["name"])},
        {"slot": "anchor", "kind": "mentor", "where": holy, "default_npc": None,
         "note": "a teacher of the PC's trade, in the haven"},
        {"slot": "anchor", "kind": "ward", "where": hid, "default_npc": None},
        {"slot": "thorn", "kind": "rival", "where": F["fourth"]["seat"] or hid, "default_npc": None,
         "note": "a member of {}".format(F["fourth"]["name"])},
        {"slot": "thorn", "kind": "creditor", "where": blds.get("market", blds["hall"]), "default_npc": None,
         "note": "a member of {}".format(F["rulers"]["name"])},
        {"slot": "thorn", "kind": "enemy", "where": None, "default_npc": None,
         "note": "a member of {} (seat bound in step 9)".format(F["threat"]["name"])},
        {"slot": "thorn", "kind": "lost", "where": None, "default_npc": None,
         "note": "a hook of kind question; last seen at a ring-2 site (bound in step 9)"},
    ]
    st.update(teachers=teachers, bond_placement=bond_placement, smith_id=smith["id"])


def _instantiate(rs: str, tid: str, place: str, roles: Rec, what: str, sid: str) -> Rec:
    """# rule: 11.4.1 -- a situation, its timeline written whole and sealed now, its first step already fired."""
    t = data().SITT[tid]
    steps = t["steps"]
    tl = []
    for i, s in enumerate(steps):
        tl.append({"n": s.get("n", i + 1), "at": {"after": s["at"]} if s.get("at") else None, "trigger": s.get("trigger"),
                   "requires": [steps[i - 1].get("n", i)] if i else [], "prevented_by": s["prevented_by"],
                   "key_delta": [s["key_delta"]], "trace": s["trace"], "bang": None})
    return {"id": f"sit.{rs}.{sid}", "title": t["name"], "template": tid, "region": place,
            "actors": sorted(set(roles.values())), "roles": roles, "what": what, "premise": [], "cadence": t["cadence"],
            "timeline": tl, "fired": [tl[0]["n"]], "end_state": [t["end_state"]], "if_prevented": [t["if_prevented"]],
            "thread": None, "status": "active",
            "visibility": "sealed (the timeline; its traces are shown as they fire)", "lifecycle": "provisional",
            "basis": ["11.4.1", "11.4.2", "12.16.12"]}


def step9_sites(st: Rec, dice: Dice, A: Answers, names: Names) -> None:
    """# rule: 12.16.12 -- sites and lairs, the threat's seat, and the two opening situations."""
    D, S = data(), st["S"]
    rs, wound, climate, areas_by_ring, region_name = st["rs"], st["wound"], st["climate"], st["areas_by_ring"], st["region_name"]
    P, F, stock, bond_placement = S["_places"], _F(st), st["stock"], st["bond_placement"]
    sites: list[str] = []
    theme_ids = list(D.THEMES)
    for ring in range(1, 6):
        for a in areas_by_ring[ring]:
            if ring >= 4 and a != areas_by_ring[ring][0]:
                continue
            th = dice.weighted([(t, 3 if t in wound["themes"] else 1) for t in theme_ids])
            if ring == 3 and a == areas_by_ring[3][0]:
                th = wound["themes"][0]
            aterr = P[a]["terrain"]
            doms = [d for d in D.DOMAINS.values() if any(anc(dt, at) or anc(at, dt) for dt in d["terrain_tags"] for at in aterr)]
            if not doms:
                doms = [d for d in D.DOMAINS.values()
                        if any(anc(dt, "terrain.ruin") or anc(dt, "terrain.underground") for dt in d["terrain_tags"])]
            dom = dice.pick(sorted(doms, key=lambda d: d["id"]))
            band = P[a]["band"]
            lair = ring >= 4
            if lair:
                band = min(5, band + 1)
            else:
                r6 = dice.d(6)
                band = max(1, band - 1) if r6 == 1 else band
            size = {1: "small", 2: "small", 3: "medium", 4: "medium", 5: "large"}.get(dice.d(6)) or \
                dom.get("typical_size", "medium")
            pn = D.TAB["tbl.12.seed.place_names"]
            while True:
                pat = dice.pick(pn["site_patterns"])
                sn = pat.replace("{domain}", pn["domain_nouns"][dom["id"]]).replace("{name}", names.place()).replace(
                    "{adjective}", dice.pick(pn["area_adjective"]))
                sid = "loc.{}_{}".format(rs, slug(sn.replace("the ", "")))
                if sid not in P:
                    break
            climax = by_range(D.THEMES[th]["climax"], dice.d(6))
            sz = next(x for x in D.SITES["sizes"] if x["id"] == size)
            pool = {r["ref"]: r["weight"] for r in D.POOLS[(th, dom["id"])]["archetypes"]}
            fb = {aid: 1 for aid, ar in D.ARCHD.items()
                  if any(anc(c, g) for c in ar["creature_tags"] for g in D.THEMES[th]["creature_gate_tags"])}
            rows, _ = TB.build_threat_table(pool, band, dice.rng, fallback_pool=fb)
            rec = place_record(sid, sn[0].upper() + sn[1:], "site", a, ring, band, None, [dom["terrain_tags"][0]], climate,
                               "{}: {}, {}".format(sn, D.THEMES[th]["name"].lower(), dom["name"].lower()))
            rec["known"] = ring <= 2 or lair
            rec["encounter_table"] = None
            rec["site"] = {"theme": th, "domain": dom["id"], "band": band, "size": size,
                           "objective": {"kind": "climax", "ref": None, "text": climax["result"], "sealed": True},
                           "lair": lair, "danger": D.THEMES[th].get("danger"), "explore_tier": dom.get("explore_tier"),
                           "clock_sizes": {"progress": sz["progress"], "danger": sz["danger"]}, "denizen_table": rows,
                           "areas": [], "path": [], "secured": [], "denizens": [], "traps": [], "frontier": None,
                           "roused": False, "last_left": None}
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
    seat_site = next(s for s in sites if P[s]["parent"] == areas_by_ring[3][0])
    F["threat"]["seat"] = seat_site
    F["threat"]["holds"] = [seat_site]
    P[seat_site]["site"]["objective"] = {"kind": "faction_seat", "ref": F["threat"]["id"],
                                         "text": "the seat of {}, and its head".format(F["threat"]["name"]), "sealed": True}
    for n in S["npcs"]:
        if F["threat"]["id"] in n["member_of"]:
            n["home"] = seat_site
    bond_placement[6]["where"] = seat_site
    lost_site = next(s for s in sites if P[s]["ring"] == 2)
    bond_placement[7]["where"] = lost_site
    stock["rare_metal"]["where"] = next((s for s in sites if P[s]["site"]["domain"] in
                                         ("site.domain.mine", "site.domain.cavern", "site.domain.underkeep")), sites[-1])
    situations: list[Rec] = []
    sroles = D.SITT[wound["situation"]]["roles"]
    big_roles = {r: (F["threat"]["id"] if i == 0 else (F["rulers"]["id"] if i == 1 else F["faith"]["id"]))
                 for i, r in enumerate(sroles)}
    situations.append(_instantiate(rs, wound["situation"], dice.pick(areas_by_ring[2]), big_roles,
                                   fill_pitch(wound["pitch"], region_name, st["ctx"]["era_age"]), "wound"))
    hook = by_range(D.WT["tbl.11.hook"]["results"], dice.d(20))
    tries = 0
    while "template" not in hook and tries < 20:
        hook = by_range(D.WT["tbl.11.hook"]["results"], dice.d(20))
        tries += 1
    local_roles = {r: (F["fourth"]["id"] if i == 0 else F["rulers"]["id"])
                   for i, r in enumerate(D.SITT[hook["template"]]["roles"])}
    situations.append(_instantiate(rs, hook["template"], dice.pick(areas_by_ring[1]), local_roles, hook["seed"], "local"))
    st.update(sites=sites, lost_site=lost_site, situations=situations)


def step10_tables(st: Rec, dice: Dice, A: Answers, names: Names) -> None:
    """# rule: 12.16.13 -- one encounter table per area, built by PR-10-10 and audited by PR-10-8."""
    D, S = data(), st["S"]
    rs, wound, areas_by_ring, peoples, factions, sites = (st["rs"], st["wound"], st["areas_by_ring"], st["peoples"],
                                                          st["factions"], st["sites"])
    P = S["_places"]
    folk_absent = {"orig.people.elf": "arch.elf_warden", "orig.people.dwarf": "arch.dwarf_holdguard"}
    excluded = {folk_absent[p["origin"]] for p in peoples if p["present"] == "absent" and p["origin"] in folk_absent}
    fielded = {f["archetype"] for fac in factions for f in fac["fields"]}
    enc_tables: list[Rec] = []
    audit: Rec = {}
    for ring in range(1, 6):
        for a in areas_by_ring[ring]:
            terr = P[a]["terrain"]
            branch = ".".join(terr[0].split(".")[:2])

            def lives(ar: Rec, tags: list[str] = terr) -> bool:
                return any(anc(at, t) or anc(t, at) for at in ar["encounter"]["terrain"] for t in tags)

            pool: dict[str, float] = {}
            for aid, ar in D.ARCHD.items():
                if aid in excluded or not lives(ar):
                    continue
                w = 1
                if any(anc(c, g) for c in ar["creature_tags"] for g in wound["gates"]):
                    w *= 3
                if aid in fielded:
                    w *= 2
                pool[aid] = w
            fb: dict[str, float] = {aid: 1 for aid, ar in D.ARCHD.items() if aid not in excluded and lives(ar, [branch])}
            gen = D.GENERIC_ENC.get(branch) or D.GENERIC_ENC["terrain.plains"]
            for _attempt in range(3):          # 12.16.13: a failing build is rebuilt; the generic table after three
                rows, blog = TB.build_threat_table(pool, P[a]["band"], dice.rng, fallback_pool=fb)
                if TB.audit_table(rows, P[a]["band"], gen["non_threat"])[0]:
                    break
            else:
                rows, blog = gen["threat_by_home"][P[a]["band"]], [(0, None, None, None, None, None, "generic")]
            tid = "tbl.{}.enc.{}".format(rs, a[len(f"loc.{rs}_"):])
            tab = {"id": tid, "name": "Encounters: {}".format(P[a]["name"]), "home_band": P[a]["band"], "danger": P[a]["danger"],
                   "terrain": terr[0], "threat_die": "d20", "threat": rows, "non_threat_die": "d6",
                   "non_threat": gen["non_threat"], "built_by": "PR-10-10", "lifecycle": "provisional",
                   "basis": ["10.10.1", "PR-10-10", "PR-10-8", "12.16.13"]}
            ok, summ, fails, _ = TB.audit_table(rows, P[a]["band"], gen["non_threat"])
            audit[tid] = {"pass": ok, "bands": summ["bands"], "words": summ["words"], "fair_or_easier": summ["fair_or_easier"],
                          "failures": fails, "pool_size": len(pool), "slots_from": dict(Counter(x[6] for x in blog))}
            P[a]["encounter_table"] = tid
            for s in sites:
                if P[s]["parent"] == a:
                    P[s]["encounter_table"] = tid
            enc_tables.append(tab)
    bestiary_arch = sorted({r["ref"][0] for t in enc_tables for r in t["threat"]}
                           | {r["ref"][0] for s in sites for r in P[s]["site"]["denizen_table"]} | fielded)
    st.update(enc_tables=enc_tables, audit=audit, bestiary_arch=bestiary_arch)


def step11_rumors(st: Rec, dice: Dice, A: Answers, names: Names) -> None:
    """# rule: 12.16.14 -- the rumor table, each rumor's truth sealed."""
    D, S = data(), st["S"]
    P, factions, situations, sites, keepers = S["_places"], st["factions"], st["situations"], st["sites"], st["keepers"]
    rum: list[Rec] = []

    def truth(src: str) -> str:
        row = D.WT["tbl.11.rumor_truth"]["rows"][src]
        v = dice.d(10)
        return next(k for k, rr in row.items() if k in ("true", "partial", "false") and in_range(rr, v))

    for f in factions:
        if f["full"]:
            fname = f["name"][0].lower() + f["name"][1:] if f["name"].startswith("The ") else f["name"]
            rum.append({"text": "Word is that {} will try to {}.".format(fname, f["goal"]["text"]), "truth": "true",
                        "points_to": f["goal"]["clock"], "source": "hearsay"})
    for s in situations:
        rum.append({"text": s["timeline"][0]["trace"].capitalize() + "; folk say it is only the beginning.", "truth": "true",
                    "points_to": s["id"], "source": "eyewitness"})
    for sid in sites:
        src = "legend" if P[sid]["ring"] >= 3 else "hearsay"
        t = truth(src)
        obj = P[sid]["site"]["objective"]["text"]
        txt = {"true": "At {} lies {}.".format(P[sid]["name"], obj),
               "partial": "At {} lies {}, and no one has ever come back from it.".format(P[sid]["name"], obj),
               "false": "{} is empty now; whatever was there is long gone.".format(P[sid]["name"])}[t]
        rum.append({"text": txt, "truth": t, "points_to": sid, "source": src})
    k = keepers[0]
    rum.append({"text": "{} has been seen in a dream by three people this month.".format(k["name"].split(",")[0]),
                "truth": truth("legend"), "points_to": k["faith"], "source": "legend"})
    rum = rum[:20]
    die = "d20" if len(rum) > 12 else "d12"
    nfaces = int(die[1:])
    rows: list[Rec] = []
    for i, r in enumerate(rum):
        rows.append(dict(range=str(i + 1), **r))
    i = len(rows)
    while len(rows) < nfaces:
        base = rum[(len(rows) - i) % len(rum)]
        rows.append(dict(range=str(len(rows) + 1), text=base["text"].rstrip(".") + ", or so the drovers say.",
                         truth=base["truth"] if base["truth"] != "true" else "partial", points_to=base["points_to"],
                         source="hearsay"))
    rumor_tables = [{"id": "tbl.{}.rumors".format(st["rs"]), "name": "Rumors of {}".format(st["region_name"]), "die": die,
                     "rule": "each rumor's truth is SEALED here (11.6.1); 11.6.3's distortion applies as it spreads",
                     "results": rows}]
    st.update(rum=rum, rumor_tables=rumor_tables)


def step12_calendar(st: Rec, dice: Dice, A: Answers, names: Names) -> None:
    """# rule: 12.16.15 -- months, days, the era (its year is the wound's age) and the quarter-day festivals."""
    D, wound, main_keeper = data(), st["wound"], _main_keeper(st)
    mn = A.get("ws.q.month_names", lambda: oracle_simple(dice, D.QS["ws.q.month_names"]))
    ct = D.TAB["tbl.12.seed.calendar_names"]
    if mn == "named":
        months = []
        for season in ["spring", "summer", "autumn", "winter"]:
            words = dice.sample(ct["months_by_season"][season], 3)
            for w_ in words:
                months.append(dice.pick(ct["month_patterns"]).replace("{word}", w_))
    else:
        months = [m["name"] for m in D.CAL["months"]]
    fest = {k: v.replace("{keeper}", main_keeper["name"].split(",")[0]) for k, v in ct["festival_patterns"].items()}
    year = st["ctx"]["era_age"]
    calendar = {"months": months, "day_names": ct["weekdays"] if mn == "named" else D.CAL["day_names"],
                "era": {"name": wound["era"],
                        "year_one": "the year {}".format(re.sub(r"^years (since|of) ", "", wound["era"]).replace("the ", "of the ", 1))},
                "festivals": [{"quarter_day": q, "name": fest[q]} for q in ["spring", "summer", "autumn", "winter"]],
                "lifespans": "calendar.yaml#lifespans (generic)",
                "opening_date": "the spring quarter day, {:d} {}".format(year, wound["era"]),
                "basis": ["11.10.1", "11.10.4", "12.16.15"]}
    st.update(calendar=calendar, fest=fest)


def step13_opening(st: Rec, dice: Dice, A: Answers, names: Names, powers_dice: Dice) -> None:
    """# rule: 12.16.16 -- the inciting incident, the start, three leads, the pregens; then the far powers."""
    D, S = data(), st["S"]
    P, F, factions, situations, sites = S["_places"], _F(st), st["factions"], st["situations"], st["sites"]
    blds, holy, hid, climate, calendar, fest = st["blds"], st["holy"], st["hid"], st["climate"], st["calendar"], st["fest"]
    inc_opt = A.get("ws.q.inciting", lambda: by_range(D.TAB["tbl.12.seed.inciting"]["results"], dice.d(8))["option"])
    inc = next(r for r in D.TAB["tbl.12.seed.inciting"]["results"] if r["option"] == inc_opt)
    first_target = {"situation": situations[0]["id"], "faction_threat": F["threat"]["id"],
                    "faction_goal": F["rulers"]["goal"]["clock"],
                    "site_ring1": next(s for s in sites if P[s]["ring"] == 1), "site_ring2": st["lost_site"]}[inc["lead_to"]]
    start_place = {"gate": blds["gate"], "market": blds.get("market", blds["gate"]), "square": blds.get("market", hid),
                   "hall": blds["hall"], "temple": holy, "walls": blds["gate"], "inn": blds["inn"]}
    scene_key = next(k for k in start_place if k in inc["scene"])
    si = 0 if first_target != situations[0]["id"] else 1
    leads = [{"lead": "the incident itself: {}".format(inc["text"]), "points_to": first_target},
             {"lead": st["rum"][len([f for f in factions if f["full"]]) + si]["text"], "points_to": situations[si]["id"]},
             {"lead": "{} is hiring, and asks no questions".format(F["fourth"]["name"]), "points_to": F["fourth"]["goal"]["clock"]}]
    regime = f"{climate} spring"
    opening = {"start": {"date": calendar["opening_date"], "watch": "dawn", "place": start_place[scene_key],
                         "weather": {"fact": "weather.today",
                                     "value": f"rolled at the first dawn by h.10.weather in the {regime} regime (10.11.3)",
                                     "source": "engine"},
                         "moon": "new (day 1 of the year: 11.10.3)", "festival": "{} (market, sitting, hiring fair)".format(fest["spring"])},
               "inciting": {"option": inc_opt, "text": inc["text"], "scene": inc["scene"],
                            "frame": "in medias res (12.4.3: the session's strong start)",
                            "pairs_with": "the PC's long vow (02.9.1): the incident is the first step of the vow or a threat "
                                          "to the anchor bond"},
               "leads": leads, "starting_state": {"known_places": "ring 0-3 areas and their known sites (rumor)",
                                                  "status": "0 with every faction unless a creation tie sets it (02.9.5)"}}
    pregens = make_pregens(dice, st)
    # 12.16.11: the powers of the far rings, on their own stream so no earlier roll moves
    prow = D.TAB["tbl.12.seed.powers"]["results"]
    used: set[str] = set()
    for ring in (4, 5):
        for a in st["areas_by_ring"][ring]:
            row = step_to(prow, by_range(prow, powers_dice.d(8)), lambda r: r["range"] not in used)
            used.add(row["range"])
            people = powers_dice.weighted(_local_weights(st))
            pw = make_npc(powers_dice, S, role=row["role"], people=people, home=a, depth="principal", band=ring,
                          role_tags=row["role_tags"])
            pw["power"] = True
            pw["keeps"] = {"fact": "truth.{}".format(pw["id"].split(".", 1)[1]), "text": row["keeps"], "sealed": True,
                           "gate": "a lore contest kept by this power (15.9.20), or standing Devoted"}
            pw["sealed_fields"].append("keeps")
            pw["basis"] = ["12.11.1", "12.16.11"]
    st.update(inc_opt=inc_opt, opening=opening, pregens=pregens)


def make_pregens(dice: Dice, st: Rec) -> list[Rec]:
    """# rule: 12.16.16 -- four pregens (02.2.5): fighter, sneak, talker, worker of magic; one non-human."""
    D, S = data(), st["S"]
    main_keeper, acceptance, blds, hid = _main_keeper(st), st["acceptance"], st["blds"], st["hid"]
    nonhuman = st["nonhuman_origins"]
    roles = [("fighter", "orig.life.soldier"), ("sneak", "orig.life.thief"),
             ("talker", dice.pick(["orig.life.merchant", "orig.life.scholar", "orig.life.courtier"]))]
    magic = "orig.life.acolyte" if main_keeper["nature"] != "profane" else "orig.life.hedge_taught"
    roles.append(("magic", magic))
    nh = nonhuman[0] if nonhuman else "orig.people.halfling"
    out: list[Rec] = []
    used_anchor: set[str] = set()
    shapes = D.ORIG["attribute_shapes"]
    for i, (role, life) in enumerate(roles):
        L = D.ORIGD[life]
        people = nh if i == 1 else "orig.people.human"
        pr = D.ORIGD[people]["attribute_rules"]
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
        best: tuple[tuple[int, ...], dict[str, int]] | None = None
        for perm in set(itertools.permutations(arr)):
            a = dict(zip(D.ATTRS, perm, strict=True))
            if all(a[k] == v for k, v in fixed.items()) and all(a[k] >= v for k, v in floors.items()):
                key = tuple(a[x] for x in prio)
                if best is None or key > best[0]:
                    best = (key, a)
        assert best is not None
        attrs = best[1]
        has = any(t["people"] == people for t in S["names"])
        name = person_name(dice, S["names"], people if has else "orig.people.human", S["_given_used"])
        homes = (blds["inn"], hid, blds.get("market"), blds["smithy"], blds.get("healer"), blds["gate"])
        anchor = [n for n in S["npcs"] if n["home"] in homes and n["id"] not in used_anchor][0]
        used_anchor.add(anchor["id"])
        d = dict(L["defaults"])
        if life == "orig.life.acolyte":
            # 05.7.4: a divine license must be one of the keeper's schools
            sch = "deed.divine.healing" if "deed.divine.healing" in main_keeper["schools"] else main_keeper["schools"][0]
            d["deep"] = [sch]
            d["technique"] = next(a for a in L["technique_suggestions"] if any(t.startswith(sch) for t in D.ABIL[a]["tags"]))
        rec = {"id": "pregen.{}.{}".format(S["_rs"], slug(name)), "name": name, "pronouns": dice.pick(["she/her", "he/him"]),
               "role": role, "sentence": "{}, {} of {}.".format(name, L["name"].lower(), S["_places"][hid]["name"]),
               "good_at": ", ".join(t.split(".")[-1].replace("_", " ") for t in d["deep"]) or "many things a little",
               "people": people, "rule": rule, "shape": "peaked", "upbringing": d["upbringing"], "livelihood": life,
               "attributes": attrs, "profile": d["profile"], "deep": d["deep"], "access": d["access"],
               "technique": d["technique"], "drive": L["drive_seeds"][0], "aspiration": L["aspiration_seeds"][0],
               "anchor_bond": {"kind": "friend", "npc": anchor["id"]}, "thorn_bond": "open (02.9.8)",
               "keeper": main_keeper["id"] if life == "orig.life.acolyte" else None,
               "acceptance": acceptance[0]["place"] if life == "orig.life.hedge_taught" else None,
               "birth": "drawn live when the pregen is picked (02.2.5 a)", "lifecycle": "provisional",
               "basis": ["02.2.5", "PR-02-9", "12.16.16"]}
        out.append(rec)
    return out


def assemble(st: Rec, seed: int | None, mode: str) -> Rec:
    """# rule: 12.16.1 -- the region record (SCHEMAS.md#region_yaml) from the steps' writes."""
    D, S = data(), st["S"]
    P, F, factions, keepers, peoples = S["_places"], _F(st), st["factions"], st["keepers"], st["peoples"]
    hid, hsite, blds, holy, areas_by_ring, tier = st["hid"], st["hsite"], st["blds"], st["holy"], st["areas_by_ring"], st["tier"]
    main_keeper, acceptance, wound, region_id = _main_keeper(st), st["acceptance"], st["wound"], st["region_id"]
    places = list(P.values())
    for p in peoples:
        p["who"] = {"common": "many", "uncommon": "some", "rare": "a few", "absent": "none"}[p["present"]] + " " + \
            D.ORIGD[p["origin"]]["name"].lower() + " folk"
        p["where"] = [hid] if p["present"] in ("common", "uncommon") else []
    org_tie = []
    origin_orgs = sorted({t for o in D.ORIG["origins"] for t in (o.get("org_tags") or []) if t.startswith("org.")})
    for org in origin_orgs:
        exact = [f for f in factions if f["org_tags"][0] == org]
        branch = [f for f in factions if f["org_tags"][0].split(".")[:2] == org.split(".")[:2] and f is not F["threat"]]
        m = (exact or branch or [None])[0]
        org_tie.append({"org": org, "faction": m["id"] if m else None,
                        "note": None if m else "none in this land (02.9.5: the tie is to an absent kind; 11 writes no status)"})
    inst = []
    for b in BRANCHES:
        fs = [f["id"] for f in factions if any(anc(pd, "deed." + b) or anc("deed." + b, pd) for pd in f["patron_deeds"])]
        inst.append({"branch": "deed." + b, "factions": fs})
    mbt = D.DEF["market_by_terrain"]
    t1 = ".".join(P[areas_by_ring[1][0]]["terrain"][0].split(".")[:2])
    th = ".".join(hsite["terrain"][0].split(".")[:2])
    hdef = st["hdef"]
    rit = D.RIT
    hsettle = {
        "tier": tier, "values_faction": F["rulers"]["id"], "seat_of": [f["id"] for f in factions if f["seat"] == hid],
        "market": {"common": sorted(set(mbt.get(t1, {}).get("common", []) + mbt.get(th, {}).get("common", []))),
                   "scarce": sorted(set(mbt.get(t1, {}).get("scarce", []) + mbt["always_scarce"])),
                   "depth": hdef["market_depth"]},
        "special_stock": [], "curio": None,
        "crafters": [dict(c, npc=st["smith_id"] if c["trade"] == "deed.craft.smithing" else None) for c in hdef["crafters"]],
        "teachers": st["teachers"],
        "texts": [{"name": "a prayer-book of {}".format(main_keeper["name"].split(",")[0]), "base": "bi.book", "where": holy,
                   "teaches": next((r["id"] for r in rit if any(anc(r["tags"][0], s) for s in main_keeper["schools"])), None),
                   "price": None, "note": "lent to the faithful"}],
        "rites_known": sorted({r["id"] for r in rit if any(anc(r["tags"][0], s) for k in keepers for s in k["schools"])}
                              | {r["id"] for r in rit if any(anc(r["tags"][0], s) for s in acceptance[0]["schools"])}),
        "hire": {"roles": hdef["hire"]["roles"] + (["cmp.boatman"] if hsite["terrain"][0].startswith("terrain.water")
                                                   and tier == "town" else []),
                 "max_band": hdef["hire"]["max_band"], "quirk_table": "companions.yaml#tbl.16.hire_quirk"},
        "sentry_floors": [dict(post=P[blds[b]]["name"], **D.DEF["sentry_floors"][b]) for b in ("gate", "hall", "temple", "shrine")
                          if b in blds],
        "lifestyle_overrides": []}
    P[hid]["settlement"] = hsettle
    for f in factions:
        f.pop("role", None)
    for k in keepers:
        k.pop("faith_org", None)
    rings_t = D.TRAVEL["rings"]
    QS, ci = D.QS, st["ci"]
    canon_facts = [{"id": "canon.wound", "text": wound["text"]},
                   {"id": "canon.magic_level", "value": st["lvl"]},
                   {"id": "canon.magic_lawful", "value": st["law"],
                    "text": next(o["text"] for o in QS["ws.q.magic_law"]["options"] if o["id"] == st["law"])},
                   {"id": "canon.default_bargainer", "value": st["bargainer"]["who"], "text": st["bargainer"]["text"]},
                   {"id": "canon.regrowth", "value": st["regrowth"],
                    "text": next(o["text"] for o in QS["ws.q.regrowth"]["options"] if o["id"] == st["regrowth"])},
                   {"id": "canon.arcane_source", "value": st["arcane_src"], "text": st["arc_text"]}]
    magic = {"item_1_canon_impossible": [c["id"] for c in ci],
             "item_2_sources": {"arcane": st["arc_text"], "divine": D.DEF["sources"]["divine"],
                                "primal": D.DEF["sources"]["primal"]},
             "item_3_keepers": [k["id"] for k in keepers],
             "item_4_places_of_power": sorted(p["id"] for p in P.values() if p["resonance"] or p["facts"].get("desecrated")
                                              or p["facts"].get("consecrated")),
             "item_5_spirit_frequency": {"level": st["spirits"], "odds": st["spirit_odds"]},
             "item_6_lawfulness": st["law"],
             "item_7_components": "stock.components; texts and teachers in places[].settlement",
             "item_8_schools": {"closed": [] if st["closed"] == "none" else [st["closed"]],
                                "conduct_evidence": ["deed.arcane.necromancy.raising", "deed.divine.pact"]}}
    sites = st["sites"]
    region = {
        "schema_version": 1,
        "seed": {"procedure": "12.16", "seed": seed, "mode": mode, "answers": st["log"],
                 "generated_by": "_process/simulation/12-world-seed.py", "uses_generic": D.DEF["uses_generic"]},
        "region": {"id": region_id, "name": P[region_id]["name"], "home_band": 1, "danger": "settled",
                   "climate": st["climate"], "haven": hid, "wound": st["wound_opt"],
                   "rings": [{"ring": 0, "words": rings_t[0]["words"], "home_band": None, "areas": [], "places": [hid]}]
                   + [{"ring": r, "words": rings_t[r]["words"], "home_band": rings_t[r]["home_band"], "areas": areas_by_ring[r],
                       "places": [s for s in sites if P[s]["ring"] == r]} for r in range(1, 6)],
                   "pitch": fill_pitch(wound["pitch"], P[region_id]["name"], st["ctx"]["era_age"]),
                   "truths": wound["truths"], "lifecycle": "provisional", "basis": ["12.16.4", "12.16.8"]},
        "canon_impossible": [c["text"] for c in ci],
        "canon": {"impossible": ci, "facts": canon_facts, "magic": magic, "components": D.DEF["components_by_band"],
                  "spirits": "Spirits of place exist ({}); they understand heartfelt speech in any tongue, and anything they "
                             "are owed.".format(st["spirits"]),
                  "hybrid_none_pairs": st["hybrid"],
                  "relics_and_refusal": next(o["text"] for o in QS["ws.q.relics_magic"]["options"] if o["id"] == st["relics"])},
        "keepers": keepers,
        "tongues": st["tongues"],
        "peoples": peoples,
        "absent_origins": [p["origin"] for p in peoples if p["present"] == "absent"],
        "names": S["names"],
        "places": places,
        "places_of_acceptance": acceptance,
        "fight_locations": st["fight"],
        "objects": [],
        "npcs": S["npcs"],
        "bond_placement": st["bond_placement"],
        "factions": {"instances": factions, "ids": [f["id"] for f in factions],
                     "full_at_start": [f["id"] for f in factions if f["full"]], "org_tie_map": org_tie, "institutions": inst},
        "values": {"region": F["rulers"]["values"],
                   "text": "{} admires what {} admires.".format(P[region_id]["name"], F["rulers"]["name"]),
                   "by_settlement": {hid: F["rulers"]["id"]}},
        "clocks": S["clocks"],
        "situations": st["situations"],
        "encounter_tables": st["enc_tables"],
        "encounter_table_audit": st["audit"],
        "rumor_tables": st["rumor_tables"],
        "tables": [],
        "terrain_by_ring": {str(k): v for k, v in st["terrain_by_ring"].items()},
        "cases": [],
        "bestiary": {"archetypes": st["bestiary_arch"],
                     "adversaries": sorted(a for a, e in D.ADV.items() if e["archetype"] in st["bestiary_arch"]),
                     "note": "PR-09-1 builds any archetype x band x role x variant the bestiary does not list"},
        "storied_items": [],
        "stock": st["stock"],
        "pregens": st["pregens"],
        "opening": st["opening"],
        "calendar": st["calendar"],
    }
    return region


STEPS: dict[int, Any] = {2: step2_canon, 3: step3_faith, 4: step4_peoples, 5: step5_land, 6: step6_haven,
                         7: step7_factions, 8: step8_cast, 9: step9_sites, 10: step10_tables, 11: step11_rumors,
                         12: step12_calendar}
_ = role_license  # re-exported for npc generation
