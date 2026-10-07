# 13_gen_part4.py -- executed by 13-gen_region.py in its own namespace.
# The '13' interface-request checklist (every request in rules/_process/INTERFACE-REQUESTS.md and each chapter's
# "To 13" block), the writers (region file + owner-block fragments), and the report.

CHECKLIST = [
    ("01", "canon_impossible list (G4 test 2)", ["region:canon_impossible"]),
    ("01", "what spirits of place understand", ["region:canon.spirits"]),
    ("01", "language licenses and their fallbacks", ["lic.lang.orrowan", "region:tongues"]),
    ("01", "Oracle Certain/Impossible depend on canon", ["region:canon.facts"]),
    ("02", "peoples present", ["region:peoples"]),
    ("02", "a name table per people", ["region:names"]),
    ("02", "second_tongue", ["region:tongues.second_tongue"]),
    ("02", "the powers an Acolyte may keep, with their faiths", ["region:keepers"]),
    ("02", "a place of acceptance for a Hedge-taught character", ["region:places_of_acceptance"]),
    ("02", "a faction for each org kind the origins name (or none)", ["region:factions.org_tie_map"]),
    ("02", "where each bond is placed", ["region:bond_placement"]),
    ("02", ">= 4 pregens passing PR-02-9", ["region:pregens"]),
    ("02", "the inciting incident that pairs with the long vow", ["region:opening.inciting"]),
    ("02", "setting origins in origins.yaml#blocks passing PR-02-9", ["orig.up.woken", "orig.life.salvager"]),
    ("03", "facts marking graves, shrines, holy places consecrated or tended", ["region:places[].facts"]),
    ("03", "NPC homes", ["region:npcs[].home"]),
    ("04", "keepers with the conduct axes each cares for", ["region:keepers[].axes"]),
    ("04", "institutions per deed branch (V3, V9)", ["region:factions.institutions"]),
    ("04", "whether the four none hybrid pairs hold", ["region:canon.hybrid_none_pairs"]),
    ("04/05/10", "place resonance", ["region:places[].resonance"]),
    ("05", "05.7.10 item 1: canon_impossible for magic", ["region:canon.magic.item_1_canon_impossible"]),
    ("05", "05.7.10 item 2: sources and who may learn", ["region:canon.magic.item_2_sources"]),
    ("05", "05.7.10 item 3: keepers, axes, signs, faiths", ["region:keepers"]),
    ("05", "05.7.10 item 4: places of power, desecrated, dead ground", ["region:places[].facts", "haz.thallen.hush_pool"]),
    ("05", "05.7.10 item 5: spirit frequency for the Oracle", ["region:canon.magic.item_5_spirit_frequency"]),
    ("05", "05.7.10 item 6: lawfulness of magic", ["region:canon.facts(canon.magic_lawful)"]),
    ("05", "05.7.10 item 7: components by price band; teachers and texts", ["region:canon.components", "region:places[].settlement.teachers/texts"]),
    ("05", "05.7.10 item 8: schools closed or opened", ["region:canon.magic.item_8_schools"]),
    ("05", "which rites are known in the region; may tighten magic requires", ["region:places[].settlement.rites_known", "region:canon.magic.item_2_sources.*.regional_requires"]),
    ("06", "regional chase-ground tables", ["tbl.thallen.chase_ground"]),
    ("06", "feature-rich fight locations", ["region:fight_locations"]),
    ("06", "nerve and objectives for the starter bestiary", ["adversaries.13 (morale, objective per PR-09-1)"]),
    ("07", "a default bargainer at the door of death", ["keeper.weyla", "region:canon.facts(canon.default_bargainer)"]),
    ("07", "consecrated or tended places (grave-chill's cure)", ["loc.tolling.ford_garden", "loc.nine_sisters", "loc.tolling.hearth_shrine"]),
    ("07", "whether any rite regrows a limb", ["ci.regrowth"]),
    ("07", "havens", ["loc.tolling"]),
    ("07", "regional afflictions (only if 00 grants an owner-block)", ["none: afflictions.yaml has no 13 owner-block; the Hush uses conditions and dread (DL-13-06)"]),
    ("08", "regional stock (scarce where), crafters by settlement, curio dealers", ["region:places[].settlement.market/crafters/curio"]),
    ("08", "canon_impossible on transmutation (AI-1)", ["ci.transmutation"]),
    ("08", "storied items and sets", ["region:storied_items"]),
    ("08", "faction boon signatures and customary gifts", ["factions.13 boon_base/boon_signature"]),
    ("08", "the region's rare metal", ["region:stock.rare_metal"]),
    ("09", "a regional subset of the bestiary", ["region:bestiary.subset"]),
    ("09", "owner-block entries built by PR-09-1", ["adversaries.13"]),
    ("09", "the default bargainer (can_bargain candidates)", ["keeper.weyla"]),
    ("10", "places with every 10.1.2 field", ["region:places"]),
    ("10", "route links with lengths in watches", ["region:places[].links"]),
    ("10", "danger rings per T-10-2", ["region:region.rings"]),
    ("10", "regional encounter tables in the two-sub-table shape, PR-10-8 audited", ["region:encounter_tables", "region:encounter_table_audit"]),
    ("10", "regional archetype signs and events", ["region:encounter_tables[].threat[].signs", "tbl.thallen.events"]),
    ("10", "site placements: theme, domain, band, size, objective", ["region:places[].site"]),
    ("10", "havens and rest sites", ["loc.tolling", "region:places[].rest_site"]),
    ("10", "climate per region; weather regimes if different", ["region:places[].climate (temperate; highland for the Greyfells and the Cinderhorn)"]),
    ("11", "factions in the owner-block conforming to 11.3.1, linchpin fates sealed", ["factions.13"]),
    ("11", "org-tie -> faction mapping", ["region:factions.org_tie_map"]),
    ("11", "month, weekday, quarter-day, festival and era names", ["calendar.13"]),
    ("11", "tbl.11.season_events.<region>, tbl.11.hook.<region>, tbl.<region>.events", ["tbl.11.season_events.thallen.spring", "tbl.11.hook.thallen", "tbl.thallen.events"]),
    ("11", "regional values for region scopes", ["region:values"]),
    ("11", "lifespans for its peoples", ["calendar.13 lifespans"]),
    ("11", "re-run 11-world-sim.py with the real factions", ["13-world-sim.py output"]),
    ("12", "region roster, role, name and furnishing tables", ["tbl.thallen.npc_role", "tbl.thallen.npc_detail", "region:names", "tbl.thallen.furnishings"]),
    ("12", "regional omen lists", ["tbl.thallen.omens"]),
    ("12", "gender/identity table override if wanted", ["none: 12's tbl.npc_gender kept (DL-13-12)"]),
    ("15", "settlement tiers", ["region:places[].settlement.tier"]),
    ("15", "teacher availability per settlement", ["region:places[].settlement.teachers"]),
    ("15", "sentries' post floors", ["region:places[].settlement.sentry_floors"]),
    ("15", "case.* templates (>= 3 placements per necessary node)", ["case.silent_bells", "case.orsolin_signet", "case.treaty_of_the_ford"]),
    ("15", "NPC lifestyles where they differ", ["region:npcs[].lifestyle", "region:places[].settlement.lifestyle_overrides"]),
    ("15", "whether relics count as magic for the magic refusal", ["region:canon.relics_and_refusal"]),
    ("16", "regional hire roles and quirks", ["region:places[].settlement.hire", "tbl.thallen.hire_quirk"]),
    ("16", "settlement tiers for the band limit", ["region:places[].settlement.tier"]),
    ("16", "named recruitable NPCs with own bands", ["region:npcs[].recruit"]),
    ("16", "beasts and mounts available", ["region:places[].settlement.hire.roles (cmp.hound, cmp.mount_*)"]),
]

FIGHT_LOCATIONS = [
    {"place": "loc.tolling.bridge", "features": ["chokepoint: the bridge's single cart-width between the toll-house pillars", "height: the bridge-house roofs", "hazard: the Wend below (haz.swift_water)", "loose_object: carts, barrels, a market's worth of stalls"]},
    {"place": "loc.harrowby.green", "features": ["hazard: the hush-pool's edge (haz.thallen.hush_pool): silence, no speech, no arcane or divine working", "cover: the bell-frame's oak posts", "difficult_ground: the duck-pond's mud", "barrier: the alehouse door"]},
    {"place": "loc.harrowby_bellpit", "features": ["height: the casting-hole's lip (a fall of 10 ft)", "chokepoint: the collapsed stair", "veil: dust in the lantern-light", "darkness (10.7)"]},
    {"place": "loc.standing_folk", "features": ["cover: thirty Stilled reapers, heavy as stone", "hazard: the field is a hush-pool", "veil: the long grass"]},
    {"place": "loc.bellhollow", "features": ["barrier: the palisade gate", "height: the cracked bell-tower", "cover: heaps of salvage"]},
    {"place": "loc.chapel_of_the_ringer", "features": ["height: the bell-tower stair", "chokepoint: the porch where Jonquil Pell stands stilled", "hazard: a hush-pool in the nave, ended by ringing the tower bell"]},
    {"place": "loc.weir_stones", "features": ["hazard: the weir's fall (haz.swift_water)", "cover: the three stones", "difficult_ground: the slick weir-crest"]},
]

CANON_EXTRA = {
    "spirits": "Spirits of place in the March understand heartfelt speech in any tongue, and gesture and offering where there is no speech; they do not understand lies (a Deceive aimed at a spirit is G4 by canon), written words, or anything said inside hushed ground (where they cannot be). The vale's spirits were stilled by the Hush and return slowly behind the Hem; the Rookwood's and the Fen's never left (13.3.5).",
    "hybrid_none_pairs": {"holds": True, "pairs": {"wilds x arcane": "holds: Orrow's bell-grammar is learned in a study, not the field", "arcane x primal": "holds: the Unsounding is the proof (a formula that tried to command the living silence)", "divine x primal": "holds: the keepers are named powers; the land's spirits and the Quiet are nameless; no servant has both", "primal x influence": "holds: spirits are bargained with, not persuaded; the Spirit-talker covers it"}, "dl": "DL-13-09"},
    "relics_and_refusal": "a relic or storied item counts as magic for refusal.magic only when its use is a visible working (trait.sense.visible) or the NPC knows its properties (a fact); carrying one does not trigger the refusal (DL-13-13)",
    "the_waking_rule": "13.2.4",
    "the_quiet": "a sleeping power, not a keeper and not a creature: nameless (no divine servant), bodiless (ci.harming_the_quiet), and the reason hushed ground stills spirits",
}

# ---------------------------------------------------------------- verify checklist id refs that look like ids
KNOWN = set(PL) | set(NPCS) | set(FACS) | set(OBJS) | set(STORIED) | set(ADV_ALL) | set(KEEP) | {c["id"] for c in CD.CASES} | CI_IDS | \
    {"lic.lang.orrowan", "orig.up.woken", "orig.life.salvager", "haz.thallen.hush_pool", "tbl.thallen.chase_ground", "tbl.thallen.events",
     "tbl.11.hook.thallen", "tbl.11.season_events.thallen.spring", "tbl.thallen.npc_role", "tbl.thallen.npc_detail", "tbl.thallen.furnishings",
     "tbl.thallen.omens", "tbl.thallen.hire_quirk"}
for frm, req, refs in CHECKLIST:
    for r_ in refs:
        tok = r_.split(" ")[0]
        if tok.count(".") >= 1 and ":" not in tok and not tok.endswith((".13", ".py")) and tok not in KNOWN and not tok.startswith("none"):
            err("checklist (%s %s): unknown ref %s" % (frm, req, tok))
for fl in FIGHT_LOCATIONS:
    if fl["place"] not in PL:
        err("fight location " + fl["place"])

# ---------------------------------------------------------------- writers
HDR = "# %s\n# Purpose: %s\n# Owner: 13-starter-setting%s.\n# Schema: data/SCHEMAS.md#%s%s\n# GENERATED by rules/_process/simulation/13-gen_region.py from 13_data_*.py; do not hand-edit (regenerate).\n# Basis: %s\n\n"


def dump(path, header, obj):
    txt = header + yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=170, default_flow_style=False)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    return len(txt)


def tablerows(lst):
    return [{"range": str(i + 1), "result": x} for i, x in enumerate(lst)]


def name_table(tid, tb):
    return {"id": tid, "name": "Names: " + tid.split(".")[-1], "die": "d20", "recency": True, "context_filters": [],
            "given": tablerows(tb["given"]), "family": tablerows(tb["family"]), "rule": "02.9.6 / 12.11.1: the engine rolls given and family and offers three",
            "lifecycle": "provisional", "basis": ["12.11.1", "02.9.6", "13.5.5"]}


REGION = {
    "schema_version": 1,
    "region": {"id": WD.REGION, "name": "The Thallen March", "home_band": 2, "danger": "wild", "climate": "temperate", "haven": PD.HAVEN,
               "rings": [{"ring": r["ring"], "words": r["words"], "areas": [p["id"] for p in PD.PLACES if p["place_kind"] == "area" and p.get("ring") == r["ring"]],
                          "places": sorted(x[2] for x in RING_REPORT if x[0] == r["ring"])} for r in TRAVEL["rings"]],
               "pitch": "13.1.2", "truths": "13.1.5", "lifecycle": "provisional", "basis": ["10.2.4", "T-10-2", "13.1", "13.6"]},
    "canon_impossible": [c["text"] for c in WD.CANON_IMPOSSIBLE],
    "canon": {"impossible": WD.CANON_IMPOSSIBLE, "facts": WD.CANON_FACTS, "magic": WD.MAGIC_CANON, "components": WD.COMPONENTS, **CANON_EXTRA},
    "keepers": WD.KEEPERS,
    "tongues": {"list": WD.TONGUES, "second_tongue": WD.SECOND_TONGUE},
    "peoples": WD.PEOPLES,
    "absent_origins": OD.ABSENT_ORIGINS,
    "names": [name_table(k, v) for k, v in WD.NAME_TABLES.items()],
    "places": list(PL.values()),
    "places_of_acceptance": PD.PLACES_OF_ACCEPTANCE,
    "fight_locations": FIGHT_LOCATIONS,
    "objects": [dict(o, kind="object", tags=[], lifecycle="provisional", basis=["15.9.2", "13.12"]) for o in CD.OBJECTS],
    "npcs": list(NPCS.values()),
    "bond_placement": PE.BOND_PLACEMENT,
    "factions": {"owner_block": "data/contrib/factions.13.yaml", "ids": [f["id"] for f in FAC_OUT], "full_at_start": [f["id"] for f in FAC_OUT if f["full"]],
                 "org_tie_map": FD.ORG_TIE_MAP, "institutions": FD.INSTITUTIONS},
    "values": {"region": WD.REGION_VALUES, "text": WD.REGION_VALUES_TEXT, "by_settlement": {p["id"]: p["settlement"]["values_faction"] for p in PL.values() if p.get("settlement")}},
    "clocks": OP.CLOCKS,
    "situations": OP.SITUATIONS,
    "encounter_tables": [dict(t, lifecycle="provisional", basis=["10.10.1", "PR-10-8", "13.14.1"]) for t in BD.ENCOUNTER_TABLES],
    "encounter_table_audit": {tid: {"bands": dict(r["bands"]), "words": dict(r["words"]),
                                    "rows": [{"range": x[0], "ref": x[1], "band": x[2], "count": x[3], "word": x[4], "win": x[5], "staggered": x[6], "note": x[7]} for x in r["rows"]]}
                              for tid, r in AUDIT.items()},
    "rumor_tables": [TD.RUMORS],
    "tables": [TD.EVENTS, TD.HOOKS] + list(TD.SEASON_EVENTS.values()) + [TD.CHASE_GROUND, TD.SITE_TABLE,
               {"id": "tbl.thallen.npc_role", "die": "d20", "replaces": "tbl.npc_role", "results": tablerows(WD.NPC_ROLE)},
               {"id": "tbl.thallen.npc_detail", "die": "d20", "replaces": "tbl.npc_detail (d100: the regional d20 is rolled first; 12's table on a repeat)", "results": tablerows(WD.NPC_DETAIL)},
               {"id": "tbl.thallen.npc_refusal_extra", "die": "d6", "rule": "rolled in place of tbl.npc_refusal on its rows 11-12; each row is kind refusal.place or refusal.wilds or refusal.master (15)", "results": tablerows(WD.NPC_REFUSAL_REGIONAL)},
               {"id": "tbl.thallen.omens", "die": "d12", "replaces": "the twist templates' generic omens (12)", "results": tablerows(WD.OMENS)},
               {"id": "tbl.thallen.furnishings", "die": "d12", "results": tablerows(WD.FURNISHINGS)},
               {"id": "tbl.thallen.hire_quirk", "die": "d12", "replaces": "tbl.16.hire_quirk", "results": tablerows(WD.HIRE_QUIRKS)}],
    "terrain_by_ring": TD.TERRAIN_BY_RING,
    "cases": CD.CASES,
    "bestiary": {"subset": BD.SUBSET_09, "regional": [e["id"] for e in NEW_ADV], "owner_block": "data/contrib/adversaries.13.yaml"},
    "storied_items": STORIED_OUT,
    "storied_sets": TD.STORIED_SETS,
    "stock": {"rare_metal": TD.RARE_METAL, "components": WD.COMPONENTS},
    "pregens": PREGEN_OUT,
    "opening": {"start": OP.START, "inciting": OP.INCITING, "teaching_arc": OP.TEACHING_ARC, "leads": OP.LEADS, "starting_state": OP.STARTING_STATE, "first_fight": OPENING_FIGHT},
    "interface_checklist": [{"from": a, "request": b, "satisfied_by": c} for a, b, c in CHECKLIST],
}

if errors:
    print("NOT WRITTEN: %d errors" % len(errors))
else:
    sizes = {}
    sizes["region_thallen.yaml"] = dump(os.path.join(DATA, "region_thallen.yaml"),
        HDR % ("data/region_thallen.yaml", "the starter region, the Thallen March, as data: region and rings, canon, keepers, tongues, peoples, names, places with links and sites, places of acceptance, objects, the cast, bond placement, the org-tie map and institutions, values, clocks, situations, encounter tables and their PR-10-8 audit, rumors, regional tables, cases, bestiary subset, storied items, stock, pregens, the opening, and the '13' interface checklist",
               "", "region_yaml (required keys places, npcs, factions, clocks, encounter_tables, rumor_tables, names, canon_impossible; optional keys documented in 13's Tables, T-13-1)", "",
               "[13] [10.1-10.2, 10.10, 10.13] [11.3, 11.5-11.7, 11.10] [12.11] [15.2, 15.9] [02.2.5, 02.9] [05.7.10] [08.4.8, 08.8] [16.3] [DL-13-01..]"), REGION)
    def block(fn, schema, purpose, key, entries, basis, extra=None):
        obj = {"schema_version": 1, "blocks": [{"owner": "13", "entries": entries}]}
        if extra:
            obj.update(extra)
        sizes[fn] = dump(os.path.join(CONTRIB, fn), HDR % ("data/contrib/" + fn, purpose, " (owner-block '13' of %s)" % schema, schema.replace(".", "") if False else schema, "", basis), obj)
    block("origins.13.yaml", "origins.yaml", "setting origins of the Thallen March (02.4.8)", "origins", OD.ORIGINS, "[02.4.4] [02.4.5] [02.4.8] [PR-02-9] [13.5.4]")
    block("kits.13.yaml", "kits.yaml", "the packs of the setting origins (02.8)", "kits",
          [{"id": o["kit_id"], "name": o["name"] + " pack" if o["kind"] == "upbringing" else o["name"] + " kit", "tags": [], "items": o["kit"], "coin": o["coin"],
            "lifecycle": "provisional", "basis": ["02.8.1", "02.8.2", "13.5.4"]} for o in OD.ORIGINS], "[02.8] [13.5.4]")
    block("licenses.13.yaml", "licenses.yaml", "the region's second tongue, Orrowan (02.4.6)", "licenses", [WD.ORROWAN_LICENSE], "[02.4.6] [00.12.1] [13.5.3]")
    block("factions.13.yaml", "factions.yaml", "the factions of the Thallen March (11.3.1; 11.3.18)", "factions", FAC_OUT, "[11.3] [13.7] [DL-13-03]")
    block("adversaries.13.yaml", "adversaries.yaml", "the March's regional adversaries, built by PR-09-1 (09-gen_data09.py build())", "adversaries", NEW_ADV, "[09.4 PR-09-1] [13.10]")
    block("hazards.13.yaml", "hazards.yaml", "the Hush as hazards (10.12.8)", "hazards", WD.HAZARDS, "[10.12.8] [13.2.3]")
    block("calendar.13.yaml", "calendar.yaml", "the March's names for the calendar engine (00.17.1 Q19; 11.10)", "calendar",
          [{"id": "cal.thallen", "name": "The reckoning of the March", "tags": [], "seasons": WD.CALENDAR["seasons"], "quarter_days": WD.CALENDAR["quarter_days"],
            "months": WD.CALENDAR["months"], "day_names": WD.CALENDAR["day_names"], "era": WD.CALENDAR["era"],
            "festivals": [dict(f, lifecycle="provisional", basis=["11.10.4", "13.9"]) for f in WD.CALENDAR["festivals"]],
            "lifespans": WD.LIFESPANS, "lifecycle": "provisional", "basis": ["11.10", "13.9"]}], "[11.10] [13.9]")
    print("written:", sizes)

# ---------------------------------------------------------------- report
print("=" * 80)
print("13-gen_region.py report")
print("places: %d (%s)" % (len(PL), dict(Counter(p["place_kind"] for p in PL.values()))))
print("routes: %d links (both directions)" % sum(len(p["links"]) for p in PL.values()))
print("rings (ring, watches from Tolling, place):")
for x in sorted(RING_REPORT):
    print("   ", x)
print("npcs: %d (%s)" % (len(NPCS), dict(Counter(n["depth"] for n in NPCS.values()))))
print("factions: %d (full %d, petty %d)" % (len(FAC_OUT), sum(f["full"] for f in FAC_OUT), sum(not f["full"] for f in FAC_OUT)))
for f in FAC_OUT:
    print("    %-34s tier %d %-6s %s %-10s %-11s goal %s/%s %s" % (f["id"], f["tier"], f["hold"], f["ratings"], f["temperament"], f["lifecycle_stage"],
          f["goal"]["clock"]["filled"], f["goal"]["clock"]["segments"], f["goal"]["scope"]))
print("new adversaries (PR-09-1): %d" % len(NEW_ADV))
for e in NEW_ADV:
    print("    %-34s %-22s T%d %-8s vit %-24s adv %s" % (e["id"], e["archetype"], e["threat_band"], e["variant"], e["vitality"], e["advisory_alone"]))
print("encounter tables (PR-10-8):")
for tid, r in AUDIT.items():
    print("    %-32s bands %s words %s non-threat d6 rows %d" % (tid, dict(r["bands"]), dict(r["words"]), r["non_threat_faces"]))
print("cases (15.9.4):")
for k, v in CASE_REPORT.items():
    print("   ", k)
    for n, x in v.items():
        print("       ", n, x)
print("pregens (PR-02-9 passed):")
for p in PREGEN_OUT:
    d = p["derived"]
    print("    %-34s %s %s/%s/%s V%d F%d coin %d ties %s hooks %d" % (p["id"], p["role"], p["people"].split(".")[-1], p["upbringing"].split(".")[-1], p["livelihood"].split(".")[-1],
          d["vitality"], d["focus"], d["coin"], [(t["faction"].split(".")[-1], t["status"]) for t in d["faction_ties"]], len(d["hooks"])))
print("opening fight (2 hush-hounds) vs reference P1:", OPENING_FIGHT)
print("opening fight options vs reference P1:", OPENING_OPTIONS)
print("interface checklist rows:", len(CHECKLIST))
print("errors:", len(errors))
for e in errors:
    print("  E", e)
print("warnings:", len(warns))
for w in warns:
    print("  W", w)
