# 13_gen_part2.py -- executed by 13-gen_region.py in its own namespace (not a standalone script).
# Places, routes and rings (10.1.2, T-10-2); people (12.11.1, 15.2.1); keepers (05.7.4); factions (11.3.1);
# the org-tie map (02.9.5) and institutions (04 V3/V9).
import heapq

PLACE_KINDS = {"region", "area", "settlement", "site", "site_area", "landmark", "building"}
DANGERS = ["safe", "settled", "wild", "perilous", "deadly"]
NAVS = {"easy", "moderate", "hard", "very_hard"}
OPEN = {"open", "broken", "closed"}
CLIMATES = {"temperate", "northern", "highland", "arid", "coastal"}
ROUTE_KINDS = {"road", "track", "river", "water", "trackless", "underway", "secret", "passage"}
SET_TIERS = {"camp", "village", "town", "city"}
SET_MAX_BAND = {"camp": 1, "village": 1, "town": 2, "city": 3}
ALERT = {"unaware", "suspicious", "alert", "alarmed"}
OBJ_KINDS = {"hoard", "guardian", "sealed_way", "rite_in_progress", "the_lost", "place_of_power", "way_through"}
FACT_KEYS = {"consecrated", "tended_by", "desecrated", "dead_ground", "haunted", "hushed", "true_bell", "true_bell_rung_at"}
RINGS = {r["ring"]: r for r in TRAVEL["rings"]}
HAZ_ALL = HAZ | {x["id"] for x in WD.HAZARDS}
ORROWAN = {WD.ORROWAN_LICENSE["id"]}

PL = {p["id"]: copy.deepcopy(p) for p in PD.PLACES}
NPCS = {n["id"]: n for n in PE.NPCS}
FACS = {f["id"]: f for f in FD.FACTIONS}
OBJS = {o["id"]: o for o in CD.OBJECTS}
STORIED = {s["id"]: s for s in TD.STORIED}
KEEP = {k["id"]: k for k in WD.KEEPERS}
ENC_IDS = {t["id"] for t in BD.ENCOUNTER_TABLES}
for coll, name in ((PD.PLACES, "place"), (PE.NPCS, "npc"), (FD.FACTIONS, "faction"), (CD.OBJECTS, "object")):
    ids = [x["id"] for x in coll]
    for d in [k for k, v in Counter(ids).items() if v > 1]:
        err("duplicate %s id %s" % (name, d))


def entity_ok(ref, where):
    if ref is None:
        return
    if ref in PL or ref in NPCS or ref in FACS or ref in OBJS or ref in STORIED or ref in ADV_ALL or ref in KEEP:
        return
    err("%s: unknown entity %s" % (where, ref))


for pid, p in PL.items():
    w = "place " + pid
    if p["place_kind"] not in PLACE_KINDS:
        err(w + ": place_kind")
    if p["parent"] is not None and p["parent"] not in PL:
        err(w + ": unknown parent " + str(p["parent"]))
    for t in p.get("terrain", []):
        tag_ok(t, w)
    for t in p.get("resonance", []):
        tag_ok(t, w + " resonance")
    for h in p.get("hazards", []):
        if h["hazard_id"] not in HAZ_ALL:
            err(w + ": unknown hazard " + h["hazard_id"])
    for k in (p.get("facts") or {}):
        if k not in FACT_KEYS:
            err(w + ": fact key %s not in the readable list" % k)
    if p.get("climate") and p["climate"] not in CLIMATES:
        err(w + ": climate")
    if p.get("encounter_table") and p["encounter_table"] not in ENC_IDS:
        err(w + ": encounter table " + p["encounter_table"])
    if p["place_kind"] == "area":
        for f in ("band", "danger", "nav_tier", "openness", "encounter_table", "ring"):
            if p.get(f) is None:
                err(w + ": missing " + f)
        if p.get("nav_tier") not in NAVS:
            err(w + ": nav_tier")
        rr = RINGS[p["ring"]]
        if p["band"] not in (rr["home_band"] or []):
            err(w + ": band %s outside ring %d's %s" % (p["band"], p["ring"], rr["home_band"]))
        if p["danger"] not in rr["danger"].replace(" or ", ",").split(","):
            err(w + ": danger %s outside ring %d's '%s'" % (p["danger"], p["ring"], rr["danger"]))
        tb = [t for t in BD.ENCOUNTER_TABLES if t["id"] == p["encounter_table"]][0]
        if tb["home_band"] != p["band"] or tb["danger"] != p["danger"]:
            err(w + ": encounter table home band/danger differ from the area's")
    if p.get("openness") and p["openness"] not in OPEN:
        err(w + ": openness")
    st = p.get("settlement")
    if st:
        if st["tier"] not in SET_TIERS:
            err(w + ": settlement tier")
        if st.get("values_faction") not in FACS:
            err(w + ": values_faction " + str(st.get("values_faction")))
        for f in st.get("seat_of", []):
            if f not in FACS:
                err(w + ": seat_of " + f)
        for side in ("common", "scarce"):
            for b in st["market"][side]:
                if b not in BASE or "item.goods.trade" not in BASE[b]["item_tags"]:
                    err(w + ": market %s %s is not a trade good" % (side, b))
        for ss in st.get("special_stock", []):
            if ss["base"] not in BASE:
                err(w + ": special stock base " + ss["base"])
        for c in st.get("crafters", []):
            tag_ok(c["trade"], w + " crafter")
            entity_ok(c["npc"], w + " crafter")
        for tch in st.get("teachers", []):
            lic_ok(tch["target"], w + " teacher", extra=ORROWAN)
            entity_ok(tch["npc"], w + " teacher")
        for tx in st.get("texts", []):
            if tx["base"] not in BASE:
                err(w + ": text base " + tx["base"])
            t = tx["teaches"]
            if not (t in RITS or t in ABIL or t in LICS or t in ORROWAN):
                err(w + ": text teaches unknown " + t)
        for r_ in st.get("rites_known", []):
            if r_ not in RITS:
                err(w + ": rite " + r_)
        for role in st["hire"]["roles"]:
            if role not in COMP:
                err(w + ": hire role " + role)
        if st["hire"]["max_band"] > SET_MAX_BAND[st["tier"]]:
            err(w + ": hire max band above 16.3.2's settlement limit")
        for sf in st.get("sentry_floors", []):
            if sf["day"] not in ALERT or sf["night"] not in ALERT:
                err(w + ": sentry floor values")
    site = p.get("site")
    if site:
        if site["theme"] not in THEMES or site["domain"] not in DOMAINS:
            err(w + ": theme/domain")
        if site["size"] not in SIZES:
            err(w + ": size")
        th = [t for t in SITES["site_themes"] if t["id"] == site["theme"]][0]
        dm = [t for t in SITES["site_domains"] if t["id"] == site["domain"]][0]
        dg = th["danger"]
        if site["band"] >= 4:
            dg = DANGERS[min(4, DANGERS.index(dg) + 1)]
        site["danger"] = dg
        ladder = ["easy", "moderate", "hard", "very_hard"]
        et = dm.get("explore_tier") or "moderate"
        if site["band"] >= 4 and et in ladder:
            et = ladder[min(3, ladder.index(et) + 1)]
        site["explore_tier"] = et
        sz = SIZES[site["size"]]
        slug = pid.split(".", 1)[1]
        site["clock_sizes"] = {"progress": sz["progress"], "danger": sz["danger"]}
        site["progress_clock"] = "clk.%s.heart" % slug
        site["danger_clock"] = "clk.%s.wakes" % slug
        o = site["objective"]
        if o["kind"] not in OBJ_KINDS:
            err(w + ": objective kind " + o["kind"])
        if o.get("ref") and o["ref"].split(".")[0] in ("npc", "adv", "item", "obj", "loc"):
            entity_ok(o["ref"], w + " objective")
        for k in ("areas", "path", "side_areas", "secured", "denizens", "traps", "entrances", "state_log"):
            site.setdefault(k, [])
        site.setdefault("frontier", None)
        site.setdefault("roused", False)
        site.setdefault("last_left", None)
    # 10.1.2 defaults (every field present on every place)
    p.setdefault("kind", "place")
    p.setdefault("tags", list(p.get("terrain", []))[:1])
    for k, v in (("band", None), ("danger", None), ("safe", False), ("terrain", []), ("climate", None), ("nav_tier", None),
                 ("forage_tier", None), ("game_tier", None), ("openness", None), ("landmarks", []), ("water_source", None),
                 ("grazing", None), ("encounter_table", None), ("hazards", []), ("resonance", []), ("settlement_scope", None),
                 ("known", False), ("discovered", False), ("site", None), ("state_log", []), ("links", [])):
        p.setdefault(k, copy.deepcopy(v))
    if "rest_site" not in p:
        p["rest_site"] = "haven" if p["safe"] else {"settlement": "camp", "area": "rough"}.get(p["place_kind"])
    p.setdefault("exists", "exists")
    p.setdefault("visibility", "shown" if p["discovered"] else ("available" if p["known"] else "sealed"))
    p["lifecycle"] = "provisional"
    p["basis"] = ["10.1.2", "13.6"]
# inheritance: climate from the nearest ancestor; sites and landmarks use their area's encounter table
for pid, p in PL.items():
    q = p
    while q is not None and not q.get("climate"):
        q = PL.get(q["parent"]) if q.get("parent") else None
    p["climate"] = (q or {}).get("climate") or "temperate"
    if p["place_kind"] in ("site", "landmark") and not p.get("encounter_table"):
        p["encounter_table"] = PL[p["parent"]].get("encounter_table")
    if p["place_kind"] == "area":
        p["landmarks"] = [x for x, y in PL.items() if y["place_kind"] == "landmark" and y["parent"] == pid]

for r in PD.ROUTES:
    for e in (r["a"], r["b"]):
        if e not in PL:
            err("route %s: unknown place %s" % (r["route"], e))
    if r["route_kind"] not in ROUTE_KINDS:
        err("route %s: kind" % r["route"])
    for t in r["terrain"]:
        tag_ok(t, "route " + r["route"])
    for h in r.get("hazards", []):
        if h["hazard_id"] not in HAZ_ALL:
            err("route %s: hazard %s" % (r["route"], h["hazard_id"]))
    for v in r.get("vehicle_ok", []):
        if v not in BASE:
            err("route %s: vehicle %s" % (r["route"], v))
    if r["a"] in PL and r["b"] in PL:
        for frm, to in ((r["a"], r["b"]), (r["b"], r["a"])):
            cur = r.get("current")
            if cur and frm == r["b"]:
                cur = {"downstream": "upstream", "upstream": "downstream"}.get(cur, cur)
            PL[frm]["links"].append({"to": to, "route": r["route"], "route_kind": r["route_kind"], "travel_watches": r["travel_watches"],
                                     "terrain": r["terrain"], "current": cur, "known": r["known"], "danger": r.get("danger"),
                                     "hazards": r.get("hazards", []), "vehicle_ok": r.get("vehicle_ok", []), "note": r.get("note")})

# ring distance by shortest KNOWN path from the haven, in watches (1 day = 2 march units, 10.3.5)
dist = {PD.HAVEN: 0}
pq = [(0, PD.HAVEN)]
while pq:
    d, u = heapq.heappop(pq)
    if d > dist.get(u, 1e9):
        continue
    for l in PL[u]["links"]:
        if not l["known"]:
            continue
        nd = d + l["travel_watches"]
        if nd < dist.get(l["to"], 1e9):
            dist[l["to"]] = nd
            heapq.heappush(pq, (nd, l["to"]))
RING_BOUNDS = {0: (0, 0), 1: (0, 2), 2: (2, 6), 3: (6, 12), 4: (12, 20), 5: (20, 999)}
RING_REPORT = []
for pid, p in PL.items():
    if p["place_kind"] in ("settlement", "site", "landmark") and "ring" in p:
        if pid not in dist:
            err("place %s unreachable from the haven by known routes" % pid)
            continue
        lo, hi = RING_BOUNDS[p["ring"]]
        d = dist[pid]
        if not (lo <= d <= hi):
            err("place %s: declared ring %d but %d watches from Tolling (bounds %s)" % (pid, p["ring"], d, (lo, hi)))
        p["watches_from_haven"] = d
        RING_REPORT.append((p["ring"], d, pid))
        par = PL.get(p["parent"])
        if par and par["place_kind"] == "area" and abs(par["ring"] - p["ring"]) > 1:
            err("place %s: ring %d inside area %s of ring %d" % (pid, p["ring"], par["id"], par["ring"]))

# ====================================================================== people
DEPTHS = {"walk-on", "recurring", "principal"}
REGISTERS = {"formal", "plain", "rough", "flowery", "terse", "nervous", "jovial", "cold"}
for nid, n in NPCS.items():
    w = "npc " + nid
    tag_ok(n["people"], w)
    if n["depth"] not in DEPTHS:
        err(w + ": depth")
    if n["home"] not in PL:
        err(w + ": home " + n["home"])
    for f in n["member_of"]:
        if f not in FACS:
            err(w + ": member_of " + f)
    for r_ in n["refusals"]:
        if r_["kind"] not in REFUSALS:
            err(w + ": refusal kind " + r_["kind"])
    if n["lifestyle"] not in LIFESTYLES:
        err(w + ": lifestyle " + n["lifestyle"])
    for l in n["speaks"]:
        lic_ok(l, w + " speaks", extra=ORROWAN)
    for wnt in n["wants"]:
        for t in wnt["tags"]:
            tag_ok(t, w + " want")
    for t in n["fears"][0]["tags"]:
        tag_ok(t, w + " fear")
    if n["voice"]["register"] not in REGISTERS:
        err(w + ": voice register")
    if n.get("recruit") and n["recruit"].get("template") and n["recruit"]["template"] not in COMP:
        err(w + ": recruit template")
    n["kind"] = "npc"
    n["tags"] = [n["people"]]
    n["role_tags"] = sorted({t for wnt in n["wants"] for t in wnt["tags"] if t.startswith("deed")})[:3]
    n["visibility"] = "background"
    n["sealed_fields"] = ["wants", "fears", "refusals", "secrets", "knowledge"]
    n["mind"] = "sapient"
    n["patience"] = None
    n["lifecycle"] = "provisional"
    n["basis"] = ["12.11.1", "15.2.1", "13.8"]

for k in WD.KEEPERS:
    w = "keeper " + k["id"]
    for a in k["axes"] + k["despises"]:
        tag_ok(a["axis"], w)
    if k["faith"] not in FACS:
        err(w + ": faith " + k["faith"])
    for s_ in k["schools"]:
        tag_ok(s_, w)
    for r_ in k["rites_known"]:
        if r_ not in RITS:
            err(w + ": rite " + r_)
    for t in k["tags"]:
        tag_ok(t, w)

# ====================================================================== factions (11.3.1)
GOAL_SEG = {"local": 8, "regional": 12, "realm": 12}
SCOPES = FACD["goal_clocks"]["scopes_by_tier"]
TEMPERS = {"aggressive", "cautious", "mercantile", "zealous", "secretive", "steadfast"}
STAGES = {"rising", "flourishing", "entrenched", "declining", "collapsed"}
FULL_KINDS = {"grow", "dominate", "change"}
PETTY_KINDS = {"grow", "take", "stir", "feud"}
FAC_OUT = []
n_full = 0
for f in FD.FACTIONS:
    w = "faction " + f["id"]
    t = f["tier"]
    if not (0 <= t <= 5) or f["hold"] not in ("weak", "strong"):
        err(w + ": tier/hold")
    r = f["ratings"]
    if set(r) != {"force", "cunning", "wealth", "sway"}:
        err(w + ": ratings keys")
    if any(v < 0 or v > t + 2 for v in r.values()):
        err(w + ": a rating outside 0..tier+2")
    if sum(r.values()) != 4 + 2 * t:
        err(w + ": ratings sum %d != %d" % (sum(r.values()), 4 + 2 * t))
    if f["temperament"] not in TEMPERS or f["lifecycle_stage"] not in STAGES:
        err(w + ": temperament/stage")
    full = f["full"]
    # 11.3.2: full iff tier >= 2, status != 0, a thread/situation names it, or the PC met an officer. The Choir is named
    # by the opening case (a thread at the first scene), so it is full; nothing else below tier 2 is.
    should = t >= 2 or f["status_to_pc"] != 0 or f["id"] == "fac.thallen.hushed_choir"
    if full != should:
        err(w + ": 'full' disagrees with 11.3.2 at the start")
    n_full += 1 if full else 0
    g = f["goal"]
    if full:
        if g["kind"] not in FULL_KINDS:
            err(w + ": full goal kind " + g["kind"])
        if g["scope"] not in SCOPES[t]:
            err(w + ": goal scope %s not allowed at tier %d" % (g["scope"], t))
        segs = GOAL_SEG[g["scope"]]
    else:
        if g["kind"] not in PETTY_KINDS or g["scope"] != "local":
            err(w + ": petty goal kind/scope")
        segs = 6
    if not (0 <= g["start"] < segs):
        err(w + ": goal start")
    if g["rating"] not in r:
        err(w + ": goal rating")
    if g.get("target") and g["target"] not in FACS:
        err(w + ": goal target")
    tpl = FTPL.get(f["template"])
    if not tpl:
        err(w + ": template " + f["template"])
        continue
    for o in f["org_tags"]:
        tag_ok(o, w)
    for v in f["values"]:
        tag_ok(v["axis"], w)
    for d in f["patron_deeds"]:
        tag_ok(d, w)
    if f["ranks"] and f["ranks"] not in RLAD:
        err(w + ": rank ladder " + f["ranks"])
    for fl in f["fields"]:
        if fl["archetype"] not in ARCHY:
            err(w + ": field archetype " + fl["archetype"])
    if f["boon_base"] not in ITEM_TAGS:
        err(w + ": boon base " + f["boon_base"])
    if f["boon_signature"] and f["boon_signature"] not in PROPS:
        err(w + ": boon signature " + f["boon_signature"])
    for pl in [f["seat"]] + f["holds"]:
        if pl not in PL:
            err(w + ": place " + pl)
    for o in f.get("officers", []):
        if o not in NPCS:
            err(w + ": officer " + o)
        elif f["id"] not in NPCS[o]["member_of"]:
            err(w + ": officer %s is not a member" % o)
    for k_ in f["relations"]:
        if k_ not in FACS:
            err(w + ": relation " + k_)
    if not (1 <= len(f["linchpins"]) <= 3):
        err(w + ": 1-3 linchpins")
    for lp in f["linchpins"]:
        if lp["npc"] not in NPCS:
            err(w + ": linchpin " + lp["npc"])
        if set(lp["fates"]) != {"dies", "captured", "turned", "exposed"}:
            err(w + ": linchpin fates must be dies/captured/turned/exposed")
        for fate, effs in lp["fates"].items():
            if not effs:
                err(w + ": empty fate " + fate)
            for e in effs:
                eff_ok(e, w + " fate " + fate)
                pr = e.get("params", {})
                for key in ("faction", "toward"):
                    if key in pr and pr[key] not in FACS:
                        err(w + ": fate %s names unknown faction %s" % (fate, pr[key]))
                if e["effect_id"] == "eff.11.new_situation" and pr["template"] not in SIT_T:
                    err(w + ": situation template " + pr["template"])
    for e in g.get("on_complete", []):
        eff_ok(e, w + " goal on_complete")
    omens = g.get("omens") or tpl["goal_omens"]
    for stg in ("stirring", "building", "imminent"):
        if not omens.get(stg):
            err(w + ": omens stage " + stg)
    clock = {"id": g["clock_id"], "name": g["text"], "kind": "faction_goal", "owner": f["id"],
             "segments": 12 if g["scope"] == "realm" else segs, "linked_second": 12 if g["scope"] == "realm" else None,
             "filled": g["start"], "visibility": "hidden", "direction": "fill",
             "tick_sources": FACD["goal_clocks"]["tick_sources"] if full else [{"on": "world_turn_petty_roll", "ticks": "d6: 1-3 none, 4-5 +1, 6 +2 (+1 rising, -1 declining)"}],
             "omens": omens, "on_complete": {"effects": g.get("on_complete", []), "interrupting": False, "then": "reset"}}
    rec = {
        "id": f["id"], "name": f["name"], "kind": "faction", "tags": list(f["org_tags"]), "template": f["template"], "org_tags": f["org_tags"],
        "patron_deeds": f["patron_deeds"], "values": f["values"], "tier": t, "hold": f["hold"], "ratings": r, "temperament": f["temperament"],
        "lifecycle_stage": f["lifecycle_stage"], "full": full,
        "goal": {"text": g["text"], "kind": g["kind"], "scope": g["scope"], "clock": clock, "rating": g["rating"], "effects": g.get("on_complete", []), "target": g.get("target")},
        "seat": f["seat"], "holds": f["holds"],
        "linchpins": [{"npc": lp["npc"], "consequence": lp["consequence"], "fates": lp["fates"], "sealed": True} for lp in f["linchpins"]],
        "officers": f.get("officers", []), "duties": f["duties"], "relations": f["relations"], "status_to_pc": f["status_to_pc"],
        "attention": None, "attention_omens": tpl["attention_omens"], "pursuit": 0, "ranks": f["ranks"], "sittings": f["sittings"],
        "fields": f["fields"], "boon_base": f["boon_base"], "boon_signature": f["boon_signature"], "courtable": f["courtable"],
        "region": WD.REGION, "visibility": "sealed" if f["id"] == "fac.thallen.hushed_choir" else "available",
        "notes": f.get("notes", ""), "lifecycle": "provisional", "basis": ["11.3.1", "11.3.18", f["template"], "13.7"]}
    FAC_OUT.append(rec)
if n_full > 6:
    err("more than six full factions at the start (11.3.2)")
ORG_NAMED = set()
for o in list(ORIG.values()) + OD.ORIGINS:
    ORG_NAMED |= set(o.get("org_tags") or [])
mapped = {m["org"] for m in FD.ORG_TIE_MAP}
for o in sorted(ORG_NAMED):
    if o not in mapped:
        err("org-tie map lacks %s (named by an origin)" % o)
for m in FD.ORG_TIE_MAP:
    tag_ok(m["org"], "org-tie map")
    if m["faction"] and m["faction"] not in FACS:
        err("org-tie map: unknown faction %s" % m["faction"])
    if m.get("when_woken") and m["when_woken"] not in FACS:
        err("org-tie map: %s" % m["when_woken"])
    for dd in ("when_people", "when_keeper"):
        for a, b in (m.get(dd) or {}).items():
            if b not in FACS:
                err("org-tie map %s: %s" % (dd, b))
for br in ("deed.martial", "deed.guile", "deed.wilds", "deed.lore", "deed.arcane", "deed.divine", "deed.primal", "deed.influence", "deed.craft"):
    if not FD.INSTITUTIONS.get(br):
        err("no institution for " + br)
    for f in FD.INSTITUTIONS.get(br, []):
        if f not in FACS:
            err("institutions %s: %s" % (br, f))
