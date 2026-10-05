# 13_gen_part3.py -- executed by 13-gen_region.py in its own namespace.
# PR-02-9 on the setting origins and the pregens; 15.9.4 on the cases; regional tables, storied items, calendar,
# canon (05.7.10) and the opening's clocks.

TAGROWS = {t["id"]: t for t in TAGD["tags"]}
LEVEL2_DEED = {t for t, r in TAGROWS.items() if t.startswith("deed.") and r.get("level") == 2}
MAGIC_BRANCHES = ("deed.arcane", "deed.divine", "deed.primal")
ORIG_ALL = dict(ORIG)
for o in OD.ORIGINS:
    ORIG_ALL[o["id"]] = o
LIC_ALL = LICS | ORROWAN
BOND_ANCHOR = {b["id"] for b in ORIGD["bond_kinds"]["anchor"]}
BOND_THORN = {b["id"] for b in ORIGD["bond_kinds"]["thorn"]}
HOOK_KINDS = {"thread", "rumor", "npc", "place", "debt", "enemy", "question"}
QUAL = ["worn", "common", "fine", "masterwork", "wondrous", "storied"]
SHAPES = ORIGD["attribute_shapes"]
PROFILES = {"focused": (2, 0, 0), "gifted": (1, 0, 1), "rounded": (1, 2, 0), "broad": (0, 5, 0)}
FOCUS_UNITS = {5: 2, 4: 1, 3: 0}


def training_lic(tag):
    parts = tag.split(".")
    return "lic.training.%s_%s" % (parts[1], parts[2])


def kit_ok(kit, w):
    for it in kit:
        if it["item_tag"] not in ITEM_TAGS:
            err(w + ": kit item tag " + it["item_tag"])
        if it["quality"] not in QUAL or QUAL.index(it["quality"]) > 2:
            err(w + ": kit quality above fine (02.8.2)")


def hook_ok(h, w):
    k = h.split(":", 1)[0]
    if k not in HOOK_KINDS:
        err(w + ": hook micro-format " + h)


# ---------------------------------------------------------------- setting origins (02.4.8)
for o in OD.ORIGINS:
    w = "origin " + o["id"]
    for t in o["tags"] + o["birth_pool"]:
        tag_ok(t, w)
    if o.get("backstory"):
        err(w + ": backstory must be empty (test 12)")
    for b in ("calling", "tier", "callings", "evidence"):
        if b in o:
            err(w + ": grants %s (02.1.3)" % b)
    kit_ok(o["kit"], w)
    seeds = o["bond_seeds"]
    if seeds[0].split(":", 1)[0] not in BOND_ANCHOR or seeds[1].split(":", 1)[0] not in BOND_THORN:
        err(w + ": bond seeds must be anchor then thorn (test 11)")
    for h in o["hooks"]:
        hook_ok(h, w)
    for l in o["licenses"]:
        lic_ok(l, w, extra=ORROWAN)
    if o["kind"] == "upbringing":
        units = FOCUS_UNITS[o["focus_base"]] + len(o["licenses"]) + len(o["languages"]) + (o.get("language_picks") or 0)
        if units != 3:
            err(w + ": upbringing spends %d units, not 3 (test 5)" % units)
        for lg in o["languages"]:
            if lg["grade"] != "accented":
                err(w + ": an upbringing tongue is held at accented")
        for pe in o.get("peoples", []):
            if pe not in ORIG:
                err(w + ": people " + pe)
    if o["kind"] == "livelihood":
        tr = o["trainings"]
        if not (5 <= len(tr) <= 8) or any(t not in LEVEL2_DEED for t in tr):
            err(w + ": 5-8 level-2 deed tags (test 6)")
        d = o["defaults"]
        need = PROFILES[d["profile"]]
        if len(d["deep"]) != need[0] or len(d["access"]) != need[1] or (1 if d["technique"] else 0) != need[2]:
            err(w + ": defaults do not match the profile")
        for t in d["deep"] + d["access"]:
            if t not in tr:
                err(w + ": default pick off the list")
        for c in o["competence"]:
            if c["value"] > 2 or c["tag"] not in LEVEL2_DEED:
                err(w + ": competence (test 8)")
        if len([c for c in o["competence"] if c["value"] > 1]) > 2:
            err(w + ": more than two tags above the floor")
        for ab in o["technique_suggestions"]:
            if ab not in ABIL or ABIL[ab].get("min_tier") != 1:
                err(w + ": technique suggestion " + ab)
        for a in o["aspiration_seeds"]:
            for t in a["tags"]:
                tag_ok(t, w)
        if d["upbringing"] not in ORIG_ALL:
            err(w + ": default upbringing")

# ---------------------------------------------------------------- pregens (02.2.5, PR-02-9 test 13)
PREGEN_OUT = []
PLACES_OF_ACC = {p["place"]: p for p in PD.PLACES_OF_ACCEPTANCE}
for g in OD.PREGENS:
    w = "pregen " + g["id"]
    peo, up, li = ORIG_ALL.get(g["people"]), ORIG_ALL.get(g["upbringing"]), ORIG_ALL.get(g["livelihood"])
    if not (peo and up and li) or peo["kind"] != "people" or up["kind"] != "upbringing" or li["kind"] != "livelihood":
        err(w + ": three origins of the three kinds (test 13)")
        continue
    if up.get("peoples") and g["people"] not in up["peoples"]:
        err(w + ": upbringing not open to this people")
    # test 2: attributes
    at = g["attributes"]
    if set(at) != {"might", "agility", "endurance", "wits", "intellect", "presence", "resolve"}:
        err(w + ": seven attributes")
    vals = sorted(at.values(), reverse=True)
    rule = g["rule"]
    shapes = SHAPES["free" if rule == "free" else "typical"]
    if g["people"] == "orig.people.human" and rule != "free":
        err(w + ": humans use the Free rule")
    if sorted(shapes[g["shape"]], reverse=True) != vals:
        err(w + ": attribute multiset is not the %s %s array" % (rule, g["shape"]))
    if rule == "typical":
        ar = peo["attribute_rules"]
        for a, v in ar["fixed"].items():
            if at[a] != v:
                err(w + ": fixed %s" % a)
        for a, v in ar["floors"].items():
            if at[a] < v:
                err(w + ": floor %s" % a)
    # profile and picks (02.5)
    need = PROFILES[g["profile"]]
    if len(g["deep"]) != need[0] or len(g["access"]) != need[1] or (1 if g["technique"] else 0) != need[2]:
        err(w + ": picks do not match the profile")
    offlist = [t for t in g["deep"] + g["access"] if t not in li["trainings"] and not (li.get("magic") and t in li["magic"]["schools"])]
    if len(offlist) > 1 or any(t.startswith(MAGIC_BRANCHES) for t in offlist):
        err(w + ": more than one off-list pick, or an off-list magic pick")
    schools = [t for t in g["deep"] + g["access"] if t.startswith(MAGIC_BRANCHES)]
    if schools and (not li.get("magic") or len(schools) > 1 or schools[0] not in li["magic"]["schools"]):
        err(w + ": magic school pick")
    if g["technique"]:
        ab = ABIL.get(g["technique"])
        if not ab or ab.get("min_tier") != 1 or not ab["tags"][0].startswith(g["deep"][0]) or ab.get("requires_conduct") or g["technique"].startswith("ab.abs_"):
            err(w + ": gifted technique (02.5.4)")
    if g["human_extra"]:
        if g["people"] != "orig.people.human" or g["human_extra"] not in LEVEL2_DEED or g["human_extra"].startswith(MAGIC_BRANCHES):
            err(w + ": human extra training")
    elif g["people"] == "orig.people.human":
        err(w + ": a human takes the extra training (02.4.3)")
    nlearn = max(0, at["intellect"])
    if len(g["learning_picks"]) != nlearn:
        err(w + ": learning picks %d != Intellect %d" % (len(g["learning_picks"]), nlearn))
    npicks = (peo.get("language_picks") or 0) + (up.get("language_picks") or 0)
    if len(g["language_picks"]) != npicks:
        err(w + ": tongue picks %d != %d" % (len(g["language_picks"]), npicks))
    # derive the creation record
    licenses = {}
    competence = [{"tag": "deed", "value": 1, "source": "floor"}]
    for t in g["deep"]:
        licenses[training_lic(t)] = {"grade": "trained", "source": g["livelihood"]}
        competence.append({"tag": t, "value": 2, "source": "origin"})
    for t in g["access"]:
        licenses.setdefault(training_lic(t), {"grade": "trained", "source": g["livelihood"]})
    if g["human_extra"]:
        licenses.setdefault(training_lic(g["human_extra"]), {"grade": "trained", "source": "02.4.3"})
    for l in up["licenses"] + ([g["upbringing_choice"]] if g["upbringing_choice"] else []):
        licenses.setdefault(l, {"grade": "trained", "source": g["upbringing"]})
    if up.get("license_choice") and g["upbringing_choice"] not in up["license_choice"]["of"]:
        err(w + ": upbringing license choice")
    tongues = {}
    for lg in peo["languages"] + up["languages"]:
        tongues[lg["license"]] = lg["grade"]
    for l in g["language_picks"]:
        tongues.setdefault(l, "accented")
    for l in g["learning_picks"]:
        if l.startswith("lic.lang.") and l != "lic.lang.letters":
            tongues.setdefault(l, "accented")
        else:
            licenses.setdefault(l, {"grade": "trained", "source": "learning pick"})
    for l in peo["licenses"]:
        licenses.setdefault(l, {"grade": None, "source": g["people"]})
    for l in list(licenses) + list(tongues):
        lic_ok(l, w, extra=ORROWAN)
    for t in [c["tag"] for c in competence if c["value"] > 1]:
        if t not in LEVEL2_DEED:
            err(w + ": competence tag")
    if len([c for c in competence if c["value"] > 1]) > 2:
        err(w + ": more than two tags above the floor (test 8)")
    facts = {}
    if li["id"] == "orig.life.acolyte":
        k = g.get("keeper")
        if not k or k["keeper"] not in KEEP or k["school"] not in KEEP[k["keeper"]]["schools"] or k["school"] != g["deep"][0]:
            err(w + ": acolyte keeper (05.7.4)")
        else:
            facts["pc.keeper.%s" % k["school"].split(".")[-1]] = k["keeper"]
    if li["id"] == "orig.life.hedge_taught":
        a = g.get("accepted")
        if not a or a["place"] not in PLACES_OF_ACC or a["school"] not in PLACES_OF_ACC[a["place"]]["schools"]:
            err(w + ": hedge-taught place of acceptance (02.5.5)")
        else:
            facts["pc.accepted.primal.%s" % a["school"].split(".")[-1]] = a["place"]
    kit = list(up["kit"]) + list(li["kit"])
    kit_ok(kit, w)
    # ties
    if g["drive"]["kind"] not in ("want", "creed") or not g["drive"]["text"]:
        err(w + ": drive (test 13)")
    if g["anchor"]["kind"] not in BOND_ANCHOR or g["anchor"]["npc"] not in NPCS:
        err(w + ": anchor bond bound to a region NPC (test 13)")
    if g["thorn"]["kind"] not in BOND_THORN or g["thorn"]["npc"] not in NPCS:
        err(w + ": thorn bond")
    if not g["aspiration"]["tags"]:
        err(w + ": aspiration with tags (test 13)")
    for t in g["aspiration"]["tags"]:
        tag_ok(t, w)
    br = [b for b in ORIGD["faction_tie_brackets"] if b["id"] == g["faction_tie"]["bracket"]]
    if not br or sorted(br[0]["ties"]) != sorted(x["value"] for x in g["faction_tie"]["ties"]):
        err(w + ": faction-tie bracket")
    ties = []
    for x in g["faction_tie"]["ties"]:
        m = [mm for mm in FD.ORG_TIE_MAP if mm["org"] == x["org"]]
        if not m or not m[0]["faction"]:
            err(w + ": tie %s maps to no faction" % x["org"])
            continue
        fac = m[0]["faction"]
        if g["upbringing"] == "orig.up.woken" and m[0].get("when_woken"):
            fac = m[0]["when_woken"]
        if g.get("keeper") and m[0].get("when_keeper") and g["keeper"]["keeper"] in m[0]["when_keeper"]:
            fac = m[0]["when_keeper"][g["keeper"]["keeper"]]
        ties.append({"org": x["org"], "faction": fac, "status": x["value"]})
    if g.get("keeper"):
        faith = KEEP[g["keeper"]["keeper"]]["faith"]
        if not any(t["faction"] == faith and t["status"] >= 1 for t in ties):
            err(w + ": an Acolyte's tie to the keeper's faith at Warm (02.5.5)")
    hooks = []
    for oid, idx in g["origin_hooks"].items():
        o = ORIG_ALL[oid]
        hooks.append({"source": oid, "text": o["hooks"][idx]})
    if g["drive"]["kind"] == "want":
        hooks.append({"source": "drive", "text": "thread: " + g["drive"]["text"]})
    hooks.append({"source": "bond." + g["anchor"]["npc"], "text": "npc: " + NPCS[g["anchor"]["npc"]]["name"]})
    hooks.append({"source": "bond." + g["thorn"]["npc"], "text": ("question: " if g["thorn"]["kind"] == "lost" else "npc: ") + NPCS[g["thorn"]["npc"]]["name"]})
    for t in ties:
        if t["status"] == -2:
            hooks.append({"source": "faction_tie", "text": "enemy: " + FACS[t["faction"]]["name"]})
    if not (5 <= len(hooks) <= 8):
        err(w + ": %d hooks (02.9.7: five to eight)" % len(hooks))
    rec = dict(g)
    rec.update({
        "kind": "pregen", "tags": [peo["tags"][0]], "lifecycle": "provisional", "basis": ["02.2.5", "PR-02-9", "13.16"],
        "derived": {"vitality": 12 + at["endurance"], "focus": up["focus_base"], "fate": 1,
                    "coin": (up.get("coin") or 0) + (li.get("coin") or 0), "competence": competence,
                    "licenses": [{"license": k, **v} for k, v in sorted(licenses.items())],
                    "tongues": [{"license": k, "grade": v} for k, v in sorted(tongues.items())],
                    "kit": kit, "facts": facts, "faction_ties": ties, "hooks": hooks,
                    "dread_threshold": max(4, 8 + at["resolve"])},
        "birth": "drawn live when chosen (02.2.5 a)", "creation_window": "open (02.2.6)"})
    PREGEN_OUT.append(rec)
roles = {g["role"].split(" ")[0] for g in OD.PREGENS}
for need_ in ("fighter", "sneak", "talker", "worker"):
    if need_ not in roles:
        err("pregens: no %s among them (02.2.5)" % need_)
if not any(g["people"] != "orig.people.human" for g in OD.PREGENS):
    err("pregens: no non-human")

# ---------------------------------------------------------------- cases (15.9.4)
def holder_place(h):
    if h in PL:
        return h
    if h in NPCS:
        return NPCS[h]["home"]
    if h in OBJS:
        return OBJS[h]["place"]
    return None


def node_dist(pl):
    while pl is not None and pl not in dist:
        pl = PL[pl]["parent"] if pl in PL else None
    return dist.get(pl, 99)


CASE_REPORT = {}
for c in CD.CASES:
    w = "case " + c["id"]
    keys = set(c["clues"])
    nodes = {n["id"]: n for n in c["nodes"]}
    rep = {}
    for p_ in c["placements"]:
        if p_["method"] not in IMETHODS:
            err(w + ": method " + p_["method"])
        if p_["content"] not in keys:
            err(w + ": placement %s content %s" % (p_["id"], p_["content"]))
        if holder_place(p_["holder"]) is None:
            err(w + ": placement %s holder %s unknown" % (p_["id"], p_["holder"]))
        for n in p_["nodes"]:
            if n not in nodes:
                err(w + ": placement node " + n)
        if p_["holder_kind"] == "person" and not p_.get("request_size") and p_["method"] != "imethod.read":
            err(w + ": person placement without request size: " + p_["id"])
    for r_ in c["reserve"]:
        if r_["method"] not in IMETHODS or r_["place"] not in PL or r_["content"] not in keys:
            err(w + ": reserve " + r_["id"])
    for nid, n in nodes.items():
        for s_ in n["deducible_from"]:
            for k in s_:
                if k not in keys:
                    err(w + ": %s deducible key %s" % (nid, k))
        if not n["necessary"]:
            continue
        pls = [p_ for p_ in c["placements"] if nid in p_["nodes"]]
        kinds = {p_["holder_kind"] for p_ in pls}
        meths = {p_["method"] for p_ in pls}
        cores = [p_ for p_ in pls if p_["access"] == "core"]
        places = {holder_place(p_["holder"]) for p_ in pls}
        res = [r_ for r_ in c["reserve"] if nid in r_["nodes"]]
        rep[nid] = {"placements": len(pls), "kinds": sorted(kinds), "methods": sorted(m.split(".")[1] for m in meths), "core": len(cores), "places": len(places), "reserve": len(res)}
        if len(pls) < 3 or len(kinds) < 2 or len(meths) < 2 or len(cores) < 1 or len(places) < 2 or len(res) < 2:
            err(w + ": %s fails 15.9.4: %s" % (nid, rep[nid]))
    if not c["fallbacks"]:
        err(w + ": no fallback")
    entry = [p_ for p_ in c["placements"] if p_["access"] == "core" and node_dist(holder_place(p_["holder"])) <= 2]
    if not entry:
        err(w + ": no core placement within reach of the case's start")
    oc = c.get("opposition_clock")
    if oc and oc["segments"] not in (4, 6, 8, 12):
        err(w + ": opposition clock size")
    CASE_REPORT[c["id"]] = rep
    c["validity_check"] = rep

# ---------------------------------------------------------------- tables, names, storied items, calendar
for tid, tb in WD.NAME_TABLES.items():
    if len(tb["given"]) != 20 or len(tb["family"]) != 20:
        err("names %s: 20 given and 20 family (d20 each)" % tid)
for p_ in WD.PEOPLES:
    if p_["origin"] not in ORIG:
        err("peoples: " + p_["origin"])
    for t in p_["name_tables"]:
        if t not in WD.NAME_TABLES:
            err("peoples: name table " + t)
    for pl in p_["where"]:
        if pl not in PL:
            err("peoples: place " + pl)
    for k in p_["faiths"]:
        if k not in KEEP:
            err("peoples: keeper " + k)
for lst, n_ in ((WD.NPC_ROLE, 20), (WD.NPC_DETAIL, 20), (WD.OMENS, 12), (WD.FURNISHINGS, 12), (WD.HIRE_QUIRKS, 12)):
    if len(lst) != n_:
        err("a regional table has %d rows, not %d" % (len(lst), n_))
for r_ in TD.SEASON_EVENTS.values():
    for row in r_["results"]:
        if row.get("phenomenon") and row["phenomenon"] not in PHEN:
            err("season events: " + row["phenomenon"])
        if row.get("situation") and row["situation"] not in SIT_T:
            err("season events: " + row["situation"])
        for e in row.get("writes", []):
            eff_ok(e, "season events")
for row in TD.HOOKS["results"]:
    if row.get("template") and row["template"] not in SIT_T:
        err("hooks: " + row["template"])
for row in TD.EVENTS["results"]:
    for e in row.get("writes", []):
        eff_ok(e, "events")
for ring, lst in TD.SITE_TABLE["by_ring"].items():
    for th, dm in lst:
        if th not in THEMES or dm not in DOMAINS:
            err("site table %s: %s %s" % (ring, th, dm))
for ring, lst in TD.TERRAIN_BY_RING.items():
    for t in lst:
        tag_ok(t, "terrain by ring " + ring)
tag_ok(TD.RARE_METAL["tag"], "rare metal")
STORIED_OUT = []
for it in TD.STORIED:
    w = "storied " + it["id"]
    b = BASE.get(it["base"])
    if not b:
        err(w + ": base")
        continue
    props = [it["signature"]] + it["properties"]
    if len(it["properties"]) > 2:
        err(w + ": more than two magnitude properties (08.4.8)")
    for pr in props:
        P_ = PROPS.get(pr["prop_id"])
        if not P_:
            err(w + ": property " + pr["prop_id"])
            continue
        if not (1 <= pr["tier"] <= len(P_.get("tiers") or [1])):
            err(w + ": %s tier %d beyond its %d tiers" % (pr["prop_id"], pr["tier"], len(P_.get("tiers") or [1])))
        bk = P_.get("base_kinds")
        if bk and not any(t == k or t.startswith(k + ".") for t in b["item_tags"] for k in bk):
            err(w + ": %s base kinds %s vs base %s (%s)" % (pr["prop_id"], bk, it["base"], b.get("kind")))
    rec = {"id": it["id"], "name": it["name"], "kind": "item", "tags": b["item_tags"][:1], "base": it["base"], "quality": "storied",
           "signature": [it["signature"]], "properties": it["properties"], "sealed_properties": [], "facts": it["facts"],
           "price": it["price"], "where": it["where"], "story": it["story"], "lifecycle": "provisional", "basis": ["08.4.8", "13.11.2"]}
    STORIED_OUT.append(rec)
CALM = {m["id"] for m in CAL["months"]}
CALQ = {q["id"] for q in CAL["quarter_days"]}
for m in WD.CALENDAR["months"]:
    if m["id"] not in CALM:
        err("calendar: month " + m["id"])
if len(WD.CALENDAR["months"]) != 12 or len(WD.CALENDAR["day_names"]) != 7 or len(WD.CALENDAR["quarter_days"]) != 4:
    err("calendar: 12 months, 7 days, 4 quarter days")
for q in WD.CALENDAR["quarter_days"]:
    if q["id"] not in CALQ:
        err("calendar: quarter " + q["id"])
for fe in WD.CALENDAR["festivals"]:
    for e in fe["effects"]:
        if e not in FX:
            err("calendar: festival effect " + e)
    if not (1 <= fe["week"] <= 13 and 1 <= fe["day"] <= 7):
        err("calendar: festival date")
    if fe.get("rite_school"):
        tag_ok(fe["rite_school"], "festival")
for l in WD.LIFESPANS:
    tag_ok(l["tag"], "lifespans")
for v in WD.REGION_VALUES:
    tag_ok(v["axis"], "region values")

# ---------------------------------------------------------------- canon (05.7.10) and hazards
for k in ("item_1_canon_impossible", "item_2_sources", "item_3_keepers", "item_4_places_of_power", "item_5_spirit_frequency",
          "item_6_lawfulness", "item_7_components_teachers_texts", "item_8_schools"):
    if not WD.MAGIC_CANON.get(k):
        err("magic canon: missing " + k)
CI_IDS = {c["id"] for c in WD.CANON_IMPOSSIBLE}
for c in WD.MAGIC_CANON["item_1_canon_impossible"]:
    if c not in CI_IDS:
        err("magic canon: " + c)
for br in WD.MAGIC_CANON["item_2_sources"]:
    tag_ok(br, "magic canon sources")
for h in WD.HAZARDS:
    for e in h["conditions"]:
        eff_ok(e, h["id"])
        if e["params"]["condition"] not in CONDS:
            err(h["id"] + ": condition " + e["params"]["condition"])
    for t in h["harm_tags"]:
        tag_ok(t, h["id"])
lic_ok("lic.lang.letters", "canon")
for e in WD.ORROWAN_LICENSE["effects"]:
    eff_ok(e, "lic.lang.orrowan")
for c in WD.COMPONENTS:
    if not (0 <= c["band"] <= 6):
        err("components band")

# ---------------------------------------------------------------- opening
for ck in OP.CLOCKS:
    if ck["segments"] not in (4, 6, 8, 12):
        err("opening clock %s: size" % ck["id"])
    if ck["visibility"] != "public":
        for stg in ("stirring", "building", "imminent"):
            if not ck["omens"].get(stg):
                err("opening clock %s: omens" % ck["id"])
    for e in ck["on_complete"]["effects"]:
        eff_ok(e, ck["id"])
for s_ in OP.SITUATIONS:
    if s_.get("template") and s_["template"] not in SIT_T:
        err("situation template " + s_["template"])
    if s_["place"] not in PL:
        err("situation place")
for b in OP.TEACHING_ARC:
    for r_ in b.get("encounter", {}).get("ref", []):
        if r_ not in ADV_ALL:
            err("teaching arc: " + r_)
if OP.START["place"] not in PL:
    err("opening place")
for nm in OP.INCITING["present"]:
    pass
# the first fight's word against each band-1 reference and against each pregen's actual line (PR-09-4 reads the PC's own numbers)
_hh = foe_line(ADV_ALL["adv.thallen.hush_hound"])
_w, _s, _ = C09.estimate(C09.pc_line(1), [dict(_hh), dict(_hh)])
OPENING_FIGHT = {"vs_reference_P1": C09.classify_sim(_w, _s), "win": round(_w, 1), "staggered": round(_s, 1)}
OPENING_OPTIONS = {}
for label, foes in (("2 hush-hounds", [_hh, _hh]), ("hush-hound pack (mob of 5)", [foe_line(ADV_ALL["adv.thallen.hush_pack"])]),
                    ("grey bitch alone", [foe_line(ADV_ALL["adv.thallen.hush_hound_alpha"])]),
                    ("grey bitch + 2 hush-hounds", [foe_line(ADV_ALL["adv.thallen.hush_hound_alpha"]), _hh, _hh])):
    _w, _s, _ = C09.estimate(C09.pc_line(1), [dict(f) for f in foes])
    OPENING_OPTIONS[label] = (C09.classify_sim(_w, _s), round(_w, 1), round(_s, 1))
