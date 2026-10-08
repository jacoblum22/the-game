"""The seed check (12.16.17, PR-12-9 step 4): every T-12-16 requirement run on one region record.

A port of `_process/simulation/12-world-seed.py#check_seed`. Returns `[(requirement id, ok, note)]`.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from engine.gen import threat_table as TB
from engine.gen._seed_lib import BRANCHES, Rec, data
from engine.gen._seed_packs import check_packs

Result = tuple[str, bool, str]


def secret_ids(reg: Rec) -> set[str]:
    return {sc["fact"] for n in reg["npcs"] for sc in n.get("secrets") or []}


def check_seed(reg: Rec) -> list[Result]:
    """# rule: 12.16.17 -- run every requirement of world_seed.yaml#requirements on a region record."""
    D = data()
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
    res: list[Result] = []

    def ok(rid: str, cond: Any, note: str = "") -> None:
        res.append((rid, bool(cond), note))

    ctx = (reg, ok, P, npcs, facs, clocks, keepers, sits, ids, hav, settle, present)
    for rq in D.WS["requirements"]:
        try:
            _check_one(rq, *ctx)
        except Exception as e:      # a missing or differently shaped key is a failed check, not a crash
            ok(rq["id"], False, f"error: {type(e).__name__}: {str(e)[:80]}")
    if "seed_cases" not in reg:     # an unpacked record (the reference's build_seed): the 64 rows only
        return res
    try:  # the 7 seed-pack rows (#pack_requirements, T-12-16's last rows) [revision: R2-D]
        res += check_packs(reg)
    except Exception as e:
        res += [(rq["id"], False, f"error: {type(e).__name__}: {str(e)[:80]}") for rq in D.WS["pack_requirements"]]
    return res


def _check_one(rq: Rec, reg: Rec, ok: Any, P: Rec, npcs: Rec, facs: Rec, clocks: Rec, keepers: Rec, sits: Rec,
               ids: set[str], hav: Rec, settle: list[Rec], present: list[Rec]) -> None:
    D = data()
    DEF, ORIG, ORIGD, LICS, TAGS = D.DEF, D.ORIG, D.ORIGD, D.LICS, D.TAGS
    rid, c = rq["id"], rq["check"]
    if c == "canon_impossible":
        have = {x["id"] for x in (reg.get("canon") or {}).get("impossible", [])}
        ok(rid, reg["canon_impossible"] and all("ci." + d["key"] in have for d in DEF["canon_impossible"]),
           "{:d} entries".format(len(reg["canon_impossible"])))
    elif c in ("nonempty", "min_count"):
        v: Any = reg
        for k in rq["key"].split("/"):
            v = v.get(k) if isinstance(v, dict) else None
        if c == "nonempty":
            ok(rid, bool(v))
        else:
            ok(rid, v is not None and len(v) >= rq["min"], f"{len(v) if v else 0:d}")
    elif c == "tongues":
        tl = reg["tongues"]["list"]
        ok(rid, all(t["license"] in LICS for t in tl) and any(t["license"] == "lic.lang.common" for t in tl),
           f"{len(tl):d} tongues")
    elif c == "peoples":
        ok(rid, len(reg["peoples"]) == 8 and any(p["origin"] == "orig.people.human" and p["present"] in ("common", "uncommon")
                                                for p in reg["peoples"])
           and any(p["origin"] != "orig.people.human" for p in present), f"{len(present):d} present")
    elif c == "names":
        tids = {t["id"] for t in reg["names"]}
        ok(rid, all(p.get("name_tables") and set(p["name_tables"]) <= tids for p in present)
           and all(t.get("given") for t in reg["names"]), "{:d} tables".format(len(reg["names"])))
    elif c == "second_tongue":
        ok(rid, reg["tongues"]["second_tongue"] in LICS, reg["tongues"]["second_tongue"])
    elif c == "keepers":
        good = all(k["axes"] and k["schools"] and k["sign"] and k["faith"] in facs and all(a["axis"] in TAGS for a in k["axes"])
                   and k.get("nature") in ("sacred", "profane") for k in reg["keepers"])
        ok(rid, len(reg["keepers"]) >= 2 and good, "{:d} keepers".format(len(reg["keepers"])))
    elif c == "acceptance":
        a = reg["places_of_acceptance"]
        ok(rid, a and all(x["place"] in P and x.get("schools") and x.get("contact") for x in a))
    elif c == "org_tie_map":
        orgs = {t for o in ORIG["origins"] for t in (o.get("org_tags") or []) if t.startswith("org.")}
        m = {x["org"]: x for x in reg["factions"]["org_tie_map"]}
        ok(rid, orgs <= set(m) and all(x["faction"] in facs or x["note"] for x in m.values()), f"{len(m):d} kinds")
    elif c == "bond_placement":
        kinds = {b["kind"] for b in reg["bond_placement"]}
        want = {k["id"] for v in ORIG["bond_kinds"].values() for k in v}
        ok(rid, want <= kinds and all(b.get("where") for b in reg["bond_placement"]))
    elif c == "pregens":
        _check_pregens(rid, reg, ok, npcs)
    elif c == "inciting":
        inc = reg["opening"]["inciting"]
        ok(rid, (inc.get("text") or inc.get("moment")) and (inc.get("pairs_with") or inc.get("impetus")))
    elif c == "ref_place":
        ok(rid, reg["opening"]["start"]["place"] in P)
    elif c == "consecrated":
        ok(rid, any((p.get("facts") or {}).get("consecrated") for p in reg["places"]))
    elif c == "npc_homes":
        ok(rid, all(n["home"] in P for n in reg["npcs"]), f"{len(npcs):d} npcs")
    elif c == "institutions":
        inst = reg["factions"]["institutions"]
        if isinstance(inst, dict):
            inst = [{"branch": k, "factions": v} for k, v in inst.items()]
        ok(rid, {"deed." + b for b in BRANCHES} <= {i["branch"] for i in inst}
           and all(all(f in facs for f in i["factions"]) for i in inst),
           "{:d} branches with an institution".format(sum(1 for i in inst if i["factions"])))
    elif c == "resonance":
        ok(rid, any(p["resonance"] for p in reg["places"]))
    elif c == "magic_canon":
        m = reg["canon"]["magic"]
        ok(rid, len(m) == 8 and all(m.values()) or (len(m) == 8 and m["item_8_schools"] is not None))
    elif c == "rites_known":
        ok(rid, hav["settlement"]["rites_known"] and all(r in {x["id"] for x in D.RIT} for r in hav["settlement"]["rites_known"]))
    elif c == "components":
        comps = reg["stock"]["components"]
        ok(rid, comps and all("band" in x and x.get("name") for x in comps), f"{len(comps):d} bands")
    elif c == "generic_or_table":
        ok(rid, True, "generic: {}".format(rq.get("generic")))
    elif c == "fight_locations":
        ok(rid, len(reg["fight_locations"]) >= 2 and all(f["place"] in P and len(f["features"]) >= 2
                                                        for f in reg["fight_locations"]))
    elif c == "bestiary":
        b = reg["bestiary"]
        refs = (b.get("archetypes") or []) + (b.get("subset") or [])
        ok(rid, refs and all(a in D.ARCHD or a in D.ADV for a in refs), f"{len(refs):d} entries")
    elif c == "bargainer":
        f = {x["id"]: x for x in reg["canon"]["facts"]}["canon.default_bargainer"]
        ok(rid, f["value"] is None or f["value"] in keepers or f["value"] in D.ARCHD, str(f["value"]))
    elif c == "regrowth":
        ok(rid, any(x.get("id") in ("canon.regrowth", "ci.regrowth") for x in reg["canon"]["facts"] + reg["canon"]["impossible"]))
    elif c == "haven":
        ok(rid, hav["safe"] and hav["rest_site"] == "haven" and hav["place_kind"] == "settlement")
    elif c == "market":
        ok(rid, hav["settlement"].get("market", {}).get("common") and hav["settlement"].get("crafters")
           and all(isinstance(s["settlement"]["market"].get("common"), list) for s in settle if s["settlement"].get("market")))
    elif c == "transmutation":
        ok(rid, any(x["id"] == "ci.transmutation" for x in reg["canon"]["impossible"]))
    elif c == "boons":
        ok(rid, all(f["boon_base"] for f in facs.values()))
    elif c == "places":
        need = ["place_kind", "band", "danger", "safe", "rest_site", "terrain", "climate", "nav_tier", "openness", "landmarks",
                "water_source", "grazing", "encounter_table", "hazards", "resonance", "settlement_scope", "known",
                "discovered", "site", "state_log"]
        missing = [(p["id"], k) for p in reg["places"] for k in need if k not in p]
        areas_ok = all(p["band"] and p["danger"] and p["nav_tier"] and p["encounter_table"] for p in reg["places"]
                       if p["place_kind"] == "area")
        ok(rid, not missing and areas_ok, f"{len(P):d} places")
    elif c == "links":
        bad = [(p["id"], x["to"]) for p in reg["places"] for x in p["links"]
               if x["to"] not in P or not any(b["to"] == p["id"] for b in P[x["to"]]["links"])]
        seen: set[str] = set()
        todo = [reg["region"]["haven"]]
        while todo:
            x = todo.pop()
            if x in seen:
                continue
            seen.add(x)
            todo += [y["to"] for y in P[x]["links"]]
        unreach = [p["id"] for p in reg["places"] if p["place_kind"] in ("area", "site") and p["id"] not in seen]
        ok(rid, not bad and not unreach, "{:d} routes; unreachable {:d}".format(len({x["route"] for p in reg["places"] for x in p["links"]}), len(unreach)))
    elif c == "rings":
        rr = reg["region"]["rings"]
        ok(rid, [r["ring"] for r in rr] == [0, 1, 2, 3, 4, 5]
           and all(P[a]["band"] in D.TRAVEL["rings"][r["ring"]]["home_band"] for r in rr[1:] for a in r["areas"])
           and any(P[a]["band"] == 5 for a in rr[5]["areas"]))
    elif c == "encounter_tables":
        tabs = {t["id"]: t for t in reg["encounter_tables"]}
        res_t = {tid: TB.audit_table(t["threat"], t["home_band"], t.get("non_threat"), deadly_only=t.get("danger") == "deadly")[0]
                 for tid, t in tabs.items()}
        areas = [p for p in P.values() if p["place_kind"] == "area"]
        covered = all(p["encounter_table"] in tabs or str(p["encounter_table"]).startswith("tbl.10.enc.") for p in areas)
        ok(rid, tabs and covered and all(res_t.values()),
           f"{len(tabs):d} tables, {sum(res_t.values()):d} pass PR-10-8 (re-audited)")
    elif c == "sites":
        ss = [p for p in reg["places"] if p["site"]]
        okk = all(s["site"]["theme"] in D.THEMES and s["site"]["domain"] in D.DOMAINS and 1 <= s["site"]["band"] <= 5
                  and s["site"]["size"] and s["site"]["objective"] for s in ss)
        tabs_ok = [TB.audit_table(s["site"]["denizen_table"], s["site"]["band"])[0] for s in ss if s["site"].get("denizen_table")]
        ok(rid, ss and okk and all(tabs_ok), f"{len(ss)} sites, {sum(tabs_ok)} stored denizen tables pass PR-10-8 (the rest are built at entry, "
           "PR-10-6)")
    elif c == "rest_sites":
        ok(rid, any(p["rest_site"] == "haven" for p in reg["places"])
           and all(p["rest_site"] for p in reg["places"] if p["place_kind"] == "area"))
    elif c == "climate":
        ok(rid, reg["region"]["climate"] in D.CLIMATES)
    elif c == "factions":
        full = [f for f in facs.values() if f["full"]]
        fates_all = {"dies", "captured", "turned", "exposed", "deposed"}
        shape = all(sum(f["ratings"].values()) == 4 + 2 * f["tier"] and f["goal"]["clock"] in clocks and f["linchpins"]
                    and all({"dies", "captured", "turned", "exposed"} <= set(x["fates"]) <= fates_all and x["sealed"]
                            for x in f["linchpins"]) for f in facs.values())
        running = sum(1 for f in full if clocks[f["goal"]["clock"]]["filled"] > 0)
        ok(rid, len(full) >= 3 and shape and running >= 3, f"{len(facs):d} factions, {len(full):d} full, {running:d} running")
    elif c == "petty_factions":
        kinds = {k["kind"] for k in D.FAC["petty_goals"]["kinds"]}
        pet = [f for f in facs.values() if not f["full"]]
        bad = [f["id"] for f in pet if not (f["goal"]["kind"] in kinds and f["goal"]["scope"] == "local"
               and clocks[f["goal"]["clock"]]["segments"] == D.FAC["petty_goals"]["clock"]["segments"]
               and ("{" not in f["goal"]["text"]) and (f["goal"]["kind"] not in ("take", "feud") or f["goal"]["target"] in ids))]
        ok(rid, not bad, "{:d} petty{}".format(len(pet), (", bad " + ", ".join(bad)) if bad else ""))
    elif c == "calendar":
        cal = reg["calendar"]
        ok(rid, len(cal["months"]) == 12 and len(cal["day_names"]) == 7 and cal["era"]["name"] and len(cal["festivals"]) == 4)
    elif c == "values":
        ok(rid, reg["values"]["region"] and reg["values"]["by_settlement"])
    elif c == "situations":
        def sit_ok(s: Rec) -> bool:
            tl = s.get("timeline") or s.get("default_timeline")
            return bool(tl) and all(x.get("trace") for x in tl) and (s["template"] in D.SITT or s["template"] is None) \
                and (s.get("region") or s.get("place")) in P
        ok(rid, len(reg["situations"]) >= 2 and all(sit_ok(s) for s in reg["situations"]), "{:d}".format(len(reg["situations"])))
    elif c == "rumors":
        rows = [r for t in reg["rumor_tables"] for r in t["results"]]
        xids = ids | secret_ids(reg) | set(reg.get("cases") or []) | {o["id"] for o in reg.get("objects") or []} \
            | D.CLUE_IDS | set(D.ADV)
        bad = [r["points_to"] for r in rows if str(r["points_to"]).split(" ")[0] not in xids]
        ok(rid, rows and not bad and all(r["truth"] in ("true", "partial", "false") for r in rows),
           "{:d} rumors ({}){}".format(len(rows), dict(Counter(r["truth"] for r in rows)), (f"; not a record: {bad}") if bad else ""))
    elif c == "npcs":
        _check_npcs(rid, reg, ok, npcs, facs)
    elif c == "opening":
        o = reg["opening"]
        xids = ids | secret_ids(reg) | set(reg.get("cases") or []) | D.CLUE_IDS
        tg = [t for x in o["leads"] for t in (x["points_to"] if isinstance(x["points_to"], list) else [x["points_to"]])]
        tg = [str(t).split(" ")[0] for t in tg]
        ok(rid, o["start"]["place"] in P and len(o["leads"]) >= 3 and all(t in xids for t in tg) and len(set(tg)) >= 3)
    elif c == "settlement_tiers":
        ok(rid, all(s["settlement"]["tier"] in ("camp", "village", "town", "city") for s in settle))
    elif c == "teachers":
        t = hav["settlement"]["teachers"]

        def held(x: Rec) -> bool:
            if x["npc"] not in npcs:
                return False
            return any(lc["id"] == x["target"] and (lc.get("grade") == "expert" or not x["target"].startswith("lic.training."))
                       for lc in npcs[x["npc"]].get("licenses", []))
        ok(rid, t and all(x["target"] in LICS and x["npc"] in npcs and held(x) for x in t), f"{len(t):d} teachings")
    elif c == "sentries":
        ok(rid, hav["settlement"].get("sentry_floors"))
    elif c == "present":
        ok(rid, all(isinstance(s["settlement"].get("lifestyle_overrides", []), list) for s in settle))
    elif c == "hire":
        h = hav["settlement"]["hire"]
        ok(rid, h["roles"] and all(r in D.COMP for r in h["roles"]) and h["max_band"] in (1, 2, 3))
    elif c == "recruits":
        ok(rid, any(n["recruit"] for n in npcs.values()))
    elif c == "powers":
        rings = {r["ring"]: r["areas"] for r in reg["region"]["rings"]}
        pw = [n for n in npcs.values() if n.get("power")]
        want = {a: r for r in (4, 5) for a in rings.get(r, [])}
        okk = (sorted(n["home"] for n in pw) == sorted(want)
               and all(n["band"] == want[n["home"]] and (n.get("keeps") or {}).get("text") for n in pw))
        ok(rid, okk, "{:d} powers, bands {}".format(len(pw), sorted(n["band"] for n in pw)))
    else:
        ok(rid, False, "unknown check " + c)
    _ = ORIGD


def _check_pregens(rid: str, reg: Rec, ok: Any, npcs: Rec) -> None:
    D = data()
    ORIG, ORIGD = D.ORIG, D.ORIGD
    pg = reg["pregens"]
    rl = " | ".join(p["role"] for p in pg)
    roles = {k for k, ws in (("fighter", ["fighter"]), ("sneak", ["sneak"]), ("talker", ["talker", "scholar"]),
                             ("magic", ["magic"])) if any(w in rl for w in ws)}
    nh = any(p["people"] != "orig.people.human" for p in pg)
    legal = True
    for p in pg:
        arr = sorted(p["attributes"].values(), reverse=True)
        shapes = [sorted(v, reverse=True) for s in ORIG["attribute_shapes"].values() for k, v in s.items() if k != "sum"]
        pr = ORIGD[p["people"]]["attribute_rules"]
        if p["rule"] == "typical":
            legal &= all(p["attributes"][k] == v for k, v in pr.get("fixed", {}).items()) and \
                all(p["attributes"][k] >= v for k, v in pr.get("floors", {}).items())
        legal &= arr in shapes and all(-1 <= v <= 3 for v in p["attributes"].values())
        anchor = p.get("anchor_bond") or p.get("anchor") or {}
        legal &= bool(p["drive"]) and bool(p["aspiration"]) and anchor.get("npc") in npcs \
            and p["profile"] in {x["id"] for x in ORIG["profiles"]}
        legal &= p["upbringing"] in ORIGD and p["livelihood"] in ORIGD and p["people"] in ORIGD
        if p.get("keeper"):
            kid = p["keeper"] if isinstance(p["keeper"], str) else (p["keeper"].get("id") or p["keeper"].get("keeper"))
            kp = next((k for k in reg["keepers"] if k["id"] == kid), None)
            legal &= kp is not None and all(t in kp["schools"] for t in p["deep"] + p["access"] if t.startswith("deed.divine"))
    ok(rid, len(pg) >= 4 and {"fighter", "sneak", "talker", "magic"} <= roles and nh and legal, f"{len(pg):d} pregens")


def _check_npcs(rid: str, reg: Rec, ok: Any, npcs: Rec, facs: Rec) -> None:
    D = data()
    ORAC = D.ORAC
    VR = {r["result"]: r for r in ORAC["tbl.npc_want_verb"]["results"]}
    OR = {r["result"]: int(r["range"]) for r in ORAC["tbl.npc_want_object"]["results"]}
    RR = {r.get("kind"): r for r in ORAC["tbl.npc_refusal"]["results"]}

    def want_ok(w: Rec) -> bool:
        v, _, o = w["text"].partition(" ")
        return v not in VR or o not in OR or OR[o] in VR[v].get("takes", [OR[o]])

    def ref_ok(n: Rec) -> bool:
        return all(not any(t == x or t.startswith(x + ".") for x in RR.get(r["kind"], {}).get("not_for", [])
                           for t in n.get("role_tags", [])) for r in n.get("refusals", []))

    KOF = {k.get("faith"): k for k in reg["keepers"]}
    div_ok = all("deed.divine.{}".format(lc["id"].rsplit("_", 1)[-1]) in {s for m in n["member_of"] if m in KOF for s in KOF[m]["schools"]}
                 for n in npcs.values() for lc in n.get("licenses", []) if lc["id"].startswith("lic.training.divine_"))
    data_ok = div_ok and all(isinstance(n.get("competence"), list) and isinstance(n.get("licenses"), list)
                             and all(lc["id"] in D.LICS for lc in n["licenses"]) for n in npcs.values())
    bad = [n["id"] for n in npcs.values() if not (all(want_ok(w) for w in n.get("wants", [])) and ref_ok(n))]
    ok(rid, len(npcs) >= 8 and all(all(m in facs for m in n["member_of"]) for n in npcs.values()) and data_ok and not bad,
       "{:d} npcs{}".format(len(npcs), (f"; misfit wants/refusals: {bad[:3]}") if bad else ("" if data_ok else
                                                                                        "; competence/licenses missing")))
