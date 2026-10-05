# gen_data08_part2.py -- executed by gen_data08.py after validation; writes the eight 08 files and contribs.
import os, yaml
OUTC = os.path.join(OUT, "..", "_process", "merged-contrib")

# ------------------------------------------------------------------ shared ladders (08.1.4, T-08-2)
QUALITY = [
 {"id": "worn", "index": 1, "signature_slots": 0, "magnitude_slots": 0, "price": "x1/2 of the base price (00.3.4's one halving, rounded down; minimum 1)", "intrinsic": [{"effect_id": "eff.08.cost_step", "params": {"ladder": "severity", "steps": 1, "applies_when": "cost.gear targets this item"}}], "meaning": "below standard: patched, dull, loose; a cost.gear against it is taken one rung heavier (fragile)"},
 {"id": "common", "index": 2, "signature_slots": 0, "magnitude_slots": 0, "price": "x1", "intrinsic": [], "meaning": "standard, serviceable work"},
 {"id": "fine", "index": 3, "signature_slots": 0, "magnitude_slots": 1, "price": "x3", "intrinsic": [], "meaning": "better make; one magnitude slot, which is OPEN (empty) unless a generator or a crafter fills it; a fine garment or jewel is a citable status fact"},
 {"id": "masterwork", "index": 4, "signature_slots": 1, "magnitude_slots": 1, "price": "x10", "intrinsic": [], "meaning": "a master's work or a true trophy: the identity layer opens"},
 {"id": "wondrous", "index": 5, "signature_slots": 1, "magnitude_slots": 2, "price": "x30", "intrinsic": [], "meaning": "the best that hands, hoards and powers produce"},
 {"id": "storied", "index": 6, "signature_slots": 1, "magnitude_slots": 2, "price": "authored", "intrinsic": [], "meaning": "hand-authored named items (uniques): a fixed property set chosen by the author, exempt from mod groups but never from the item share (08.2) or the slot cap; never generated"},
]
DEGREE_EFFECTS = {"critical_success": "greater", "critical_failure": "flawed"}
PROP_VALUE = {1: 20, 2: 50, 3: 125, 4: 300, 5: 750}

# ------------------------------------------------------------------ base_items.yaml
base_hdr = HDR("base_items.yaml", "every base item of every item.* branch: weapons (on 06's T-06-6/T-06-7), armor (07.2.2), shields,\n#   garments, jewelry, tools (kits, implements, trade tools, light, containers), consumables, goods, conveyances.\n#   Kits (02) and loot trophies resolve item tags to these entries (08.1.11).",
 "# Optional fields (T-08-1): weapon_weight, harm, strike_cost, hands, weapon_properties (<=2, T-06-7), deed_tag,\n#   training_license, reload_actions, armor_class, reduction, carried_weight, snags, don_time, sleep, guard_edge,\n#   shield_class, body_slot, intrinsic (base effects, not properties), status, implement, serves, grants_lever,\n#   uses, quantity, quantity_name, light_source, holds, effects, priority_rank, spread, conveyance, carry_capacity,\n#   travel_pace, upkeep_week, companion_hint, crew, hull_clock, make {license, deed_tag, time_per_tick},\n#   default_for (the tag this entry resolves), trophy_eligible, note. `weight` is LOAD in load units (08.9.1);\n#   `price` is coins at quality common (1 coin = one day's plain food and lodging, 08.8.1).\n")
dump("base_items.yaml", base_hdr, {"schema_version": 1, "lifecycle": "provisional",
     "quality_rungs_ref": "economy.yaml#quality_rungs and 08.1.4", "kit_resolution": KIT_RES, "base_items": BI})

# ------------------------------------------------------------------ item_properties.yaml
prop_hdr = HDR("item_properties.yaml", "the shared property pool of the gate->fill generator (00.11): every item property any domain\n#   (gen.loot, gen.craft, gen.gift) can place on an item, as effect references with tiers, mod groups, gate tags,\n#   excluded tags and base kinds; plus the flaws used by the Flawed degree effect.",
 "# Optional PoolEntry fields (T-08-1): kind (mundane | passive | license | item_ability), family (the modifier\n#   family or behavior class, for the item share of 08.2), item_share (what one instance contributes to a capped\n#   family), bias (ward | strike | sense | move | social | craft | arcane: the closed bias-tag list of biased\n#   fills), domains, place_gated (eligible when the scene's place tags match even if the source's do not, 08.3.4),\n#   signature_only, relic, saturated_by, per-tier trigger {hook, chance, params} and limits, value_by_tier.\n#   Gate matching is 00.5.4c: an entry gated on G matches a source tag S when G == S or G is an ancestor of S.\n")
for p in PROPS:
    p["value_by_tier"] = {t: PROP_VALUE[t] * (2 if p["kind"] == "item_ability" else 1) for t in range(p["min_tier"], 6)}
dump("item_properties.yaml", prop_hdr, {"schema_version": 1, "lifecycle": "provisional", "bias_tags": ["ward", "strike", "sense", "move", "social", "craft", "arcane"],
     "tier_rule": "a property at tier t uses its highest authored tier row <= t (00.11.3 step 8: fixed values per tier, no rolled ranges)",
     "chance_rule": "a trigger's chance is a natural d20 range rolled by the engine on the triggering roll's own die (00.10.7): tier 1 '20', 2 '19-20', 3 '18-20', 4 '17-20', 5 '16-20'",
     "default_signatures": DEFAULT_SIG, "properties": PROPS, "flaws": FLAWS})

# ------------------------------------------------------------------ materials.yaml
mat_hdr = HDR("materials.yaml", "crafting materials: market stock and harvested creature parts. A material's `gates` are the pool-gate\n#   tags of gen.craft (00.11.2: the source of a craft is the material). Harvest rules: 08.3.10.",
 "# Optional fields (T-08-1): stock (bought at market), harvest {verb, deed_tag, dc_tier, time}, weight (load units),\n#   fallback_signature (only for parts with no provenance;\n#   a harvested part carries its source archetype's signature), flaws, gated_pool_size (computed, with the creature.folk maker's-hand gate).\n#   rarity_band 0-4: 0 any market; 1 village or harvest; 2 town or harvest of a T2+ source; 3 city or T3+;\n#   4 never sold, found or harvested only. A harvested part's band is max(its listed band, the source's threat band - 1).\n")
dump("materials.yaml", mat_hdr, {"schema_version": 1, "lifecycle": "provisional", "materials": MATS})

# ------------------------------------------------------------------ gen_loot.yaml
CIRC_LOOT = [
 {"id": "decisive", "true_only_when": "the source was defeated (06.13.3 manner: defeated) by the PC's own resolved beat (a frame id on on_defeat) in a conflict in which the PC was never Staggered or Dying and no frame against the PC was lethal", "false_for": "a foe finished by an ally, a companion or a hazard; any fight in which the PC was Staggered; a foe that yielded and was spared (merciful); the same as gen_absorb's decisive (04.10)"},
 {"id": "costly", "true_only_when": "the source was defeated by the PC's own resolved beat AND during that conflict the PC was Staggered or Dying, or a frame against the PC was lethal (gen_absorb's narrow_survival: one classification serves both domains)", "false_for": "a hard fight the PC came through above 0 Vitality with no lethal frame (decisive)"},
 {"id": "merciful", "true_only_when": "the source yielded, was subdued nonlethally or broke and was let go by the PC's own resolved beat AND a mercy fact is written (it is spared); the item is given or surrendered", "false_for": "a creature bound and then killed (decisive or nothing); a mindless creature (creature.undead.mindless, creature.construct, creature.horror.ooze), which cannot yield"},
 {"id": "scavenged", "default": True, "true_only_when": "none of the above: the source was found dead, killed by another or by a hazard, or the thing is found rather than won (a cache, a corpse, a hoard after its keeper fled); the degree is the SEARCH beat's", "false_for": "any defeat by the PC's own resolved beat"},
]
gen_loot = {
 "schema_version": 1, "lifecycle": "provisional", "domain": "gen.loot", "output_kind": "item",
 "pool_ref": "item_properties.yaml#properties where domains contains loot",
 "trigger": {"event": "on_defeat (manner defeated, yielded or drive_off with a body or a yield) or a resolved search of a found thing",
             "resolved_only": "an on_defeat carrying a frame id, or a resolved Observe/Handle search frame (00.11.2: a narrated kill that was never resolved generates nothing)",
             "per": "ONE generate() per defeated side (a mob, a pack or a band is one side: 06.10.2) with source = the side's highest-band member; harvest (08.3.10) is per body"},
 "circumstances": CIRC_LOOT,
 "fill_map": [{"circumstance": "decisive", "fill_method": "signature"}, {"circumstance": "costly", "fill_method": "biased", "bias_tag": "ward"},
              {"circumstance": "merciful", "fill_method": "chosen"}, {"circumstance": "scavenged", "fill_method": "weighted"}],
 "drop_check": {"rule": "before rung lookup, the engine rolls d100 against the source's yield; a miss means NO property item (materials, coin and the source's own gear only)",
                "yield": {"none": 0, "trophy": {"T1": 10, "T2": 20, "T3": 35, "T4": 50, "T5": 70}, "hoard": 100, "always": 100},
                "principal": "a principal NPC (12.11.1) or an archetype marked loot.yield: always drops on every defeat",
                "basis": ["Diablo II treasure classes' NoDrop weight, R3 08.1/A-1", "DL-08-08"]},
 "quality_rungs": [{"id": q["id"], "index": q["index"], "signature_slots": q["signature_slots"], "magnitude_slots": q["magnitude_slots"]} for q in QUALITY[:5]],
 "quality_map": [
   {"circumstance": "decisive", "degree": "critical_success", "quality_rung": "masterwork"}, {"circumstance": "decisive", "degree": "success", "quality_rung": "masterwork"},
   {"circumstance": "costly", "degree": "critical_success", "quality_rung": "masterwork"}, {"circumstance": "costly", "degree": "success", "quality_rung": "masterwork"},
   {"circumstance": "merciful", "degree": "critical_success", "quality_rung": "masterwork"}, {"circumstance": "merciful", "degree": "success", "quality_rung": "masterwork"},
   {"circumstance": "scavenged", "degree": "critical_success", "quality_rung": "fine"}, {"circumstance": "scavenged", "degree": "success", "quality_rung": "fine"},
   {"circumstance": "scavenged", "degree": "failure", "quality_rung": "common"}, {"circumstance": "scavenged", "degree": "critical_failure", "quality_rung": "common"}],
 "hoard_map": {"rule": "a hoard (yield: hoard, or a site's treasure with source = the place) generates by band, circumstance as classified (usually scavenged or decisive)",
               "T1": [{"rung": "fine", "count": 1}], "T2": [{"rung": "masterwork", "count": 1}], "T3": [{"rung": "masterwork", "count": 1}, {"rung": "fine", "count": 1}],
               "T4": [{"rung": "wondrous", "count": 1}, {"rung": "masterwork", "count": 1}], "T5": [{"rung": "wondrous", "count": 1}, {"rung": "masterwork", "count": 2}],
               "coin_table": "economy.yaml#hoard_coin", "goods_table": "economy.yaml#hoard_goods"},
 "degree_effects": {"critical_success": "greater", "critical_failure": "flawed"},
 "degree_effect_rules": {"greater": "one property (the signature first, else the first magnitude) gains +1 tier, which may exceed tier_cap by at most 1 (00.11.3 step 5)",
                         "flawed": "loot: the item's one magnitude slot is removed (a fine find becomes a common one) and the item is created damaged"},
 "tier_rule": {"signature": "tier_cap", "magnitude": "tier_cap - 1, minimum 1", "tier_cap": "the source's threat band (T1 -> 1 ... T5 -> 5); a place's tier_cap is its site band (10/13)"},
 "recency_window": 5, "slot_cap": "the base item's slot_cap (base_items.yaml)",
 "pool_gate": {
   "source_tags": "the archetype's creature_tags (most specific first) + its harm_tags + its evidence_tags (deed.*) + its org tags + loot.pool_gate_tags (09) + the trophy base's material_tags",
   "made_by_hands": "an armament (weapon, armor, shield) taken from a folk or undead source adds creature.folk to the source tags: the folk-made mundane properties are open to it",
   "place_tags": "the terrain tags of the place where it was won (10/13); they open ONLY entries flagged place_gated",
   "base_kinds": "an entry is kept only if one of its base_kinds is an ancestor-or-equal of the generated base item's tags",
   "excluded": "an entry is dropped if any excluded_tag matches the source",
   "signature_only": "entries marked signature_only may fill only the signature slot",
   "saturation": "an entry whose family the base item already fills to the item share (e.g. keen on a versatile weapon: harm_edge) is dropped (08.2.4)"},
 "base_selection": {"rule": "the item's base: (1) the archetype's loot.trophy_base if 09 names one (an item tag or a bi.* id); else (2) the trophy default for the source's creature branch below; (3) for folk and armed sources, one of the source's own carried items chosen by d6 from its gear list (09); a tag resolves by drawing uniformly among base items carrying it with trophy_eligible not false",
                    "trophy_defaults": {"creature.beast": ["item.jewelry.charm", "item.garment.cloak", "item.armor.light.leather"], "creature.folk": ["the source's own gear"],
                                        "creature.undead": ["item.jewelry.ring", "item.jewelry.amulet", "item.weapon"], "creature.spirit": ["item.jewelry.charm", "item.jewelry.amulet"],
                                        "creature.fiend": ["item.weapon", "item.jewelry.ring"], "creature.construct": ["item.shield", "item.jewelry.amulet", "item.armor.medium"],
                                        "creature.elemental": ["item.jewelry.charm", "item.jewelry.amulet"], "creature.dragon": ["item.armor", "item.shield", "item.jewelry.charm"],
                                        "creature.horror": ["item.jewelry.charm", "item.weapon"]},
                    "die": "d6 over the list repeated in order (1-2 first, 3-4 second, 5-6 third; a one-entry list is certain)"},
 "default_signatures": "item_properties.yaml#default_signatures (09 may name another signature_eligible entry whose gate matches)",
 "harvest": "08.3.10 / PR-08-3: materials.yaml entries whose source_tags match the body",
 "contract_09": {
   "archetype_fields_read": ["creature_tags (most specific first)", "harm_tags", "evidence_tags", "org_tags (folk)", "threat_band (tier_cap; drop chance)",
                             "loot.yield (none | trophy | hoard | always; default trophy for anything with a body, none for mindless vermin and swarms)",
                             "loot.trophy_base (item tag or bi.* id; optional)", "loot.pool_gate_tags (optional additions)", "signature_property (prop.*, optional; default from default_signatures)", "loot.flaw (flaw.*, optional: a curse in the source's nature, e.g. a lich's rings Binding; sealed until attunement or study, 08.5.4)",
                             "gear (folk: base item ids or tags carried and dropped, mundane, quality worn/common)", "purse (coin table id; folk only)", "harvest (mat.* override; optional)",
                             "signature_of on gen_absorb entries (used by gen.item_ability's decisive fill)"],
   "validation": "every archetype's tag set must leave >= 3 entries in the gated pool for its usual trophy base at tier_cap 1 (the simulation checks the 24 reference archetypes; 09 re-runs it on its own)"},
}
dump("gen_loot.yaml", HDR("gen_loot.yaml", "the loot domain of the gate->fill generator (00.11): what a defeated source or a found cache\n#   yields. Pool gate = the source's nature (and, for place_gated entries, the place); fill = the manner of winning."), gen_loot)

# ------------------------------------------------------------------ gen_craft.yaml
gen_craft = {
 "schema_version": 1, "lifecycle": "provisional", "domain": "gen.craft", "output_kind": "item",
 "pool_ref": "item_properties.yaml#properties where domains contains craft",
 "source": "the material set: one primary material (mat.*, which must carry a material tag of the base item's make) plus at most one reagent (an essence, gem or special stock); gate tags = the union of their gates + creature.folk (the maker's hand: folk-made mundane properties are open to every crafted thing) + the harvested parts' provenance source tags",
 "circumstances": [
   {"id": "crafted", "true_only_when": "the PC (or a companion under the PC's command) makes it under the base item's make.license (any grade), with that trade's tools, at a workplace (a forge for metal, a bench for wood or leather, a still for alchemy)", "false_for": "work without the license, the tools or the workplace (improvised); work done by a paid crafter (commissioned)"},
   {"id": "commissioned", "true_only_when": "an NPC crafter holding the make.license is paid to make it; the player names the base, the materials, the target rung and one bias tag", "false_for": "a companion's work (crafted, under the PC's command); a gift (gen.gift)"},
   {"id": "improvised", "default": True, "true_only_when": "anything made without one of the license, the trade tools or a workplace: field work with a knife and what is at hand (the license's crude_fallback, 01)", "false_for": "licensed work at a workplace with tools"}],
 "fill_map": [{"circumstance": "crafted", "fill_method": "chosen"}, {"circumstance": "commissioned", "fill_method": "biased", "bias_tag": "the player's named bias tag"},
              {"circumstance": "improvised", "fill_method": "weighted"}],
 "recipe_override": "when the maker knows a recipe for a property (fact knows_recipe: prop.* or a held text with teaches: prop.*), that property may be named for one slot and is filled by recipe (deterministic) in place of the circumstance's method",
 "signature_rule": "the signature slot of a crafted or commissioned masterwork or wondrous item is filled by the PRIMARY material's signature: for a harvested part, the signature of the archetype it was taken from (its provenance: Monster Hunter's carve-to-craft model); for bought stock, materials.yaml fallback_signature; if neither exists, by the circumstance's fill among signature_eligible entries in the gated pool; an improvised item never has a signature slot",
 "target_rungs": [{"rung": "worn", "obstacle_tier": "easy", "clock": 4}, {"rung": "common", "obstacle_tier": "easy", "clock": 4}, {"rung": "fine", "obstacle_tier": "moderate", "clock": 6},
                  {"rung": "masterwork", "obstacle_tier": "hard", "clock": 8}, {"rung": "wondrous", "obstacle_tier": "very_hard", "clock": 12}],
 "grade_caps": {"none (improvised)": {"max_rung": "common", "note": "fine only with a critical completing beat (Greater raises the rung by one, not a tier)"}, "trained": {"max_rung": "masterwork", "tier_cap": 2}, "expert": {"max_rung": "wondrous", "tier_cap": 4}, "master": {"max_rung": "wondrous", "tier_cap": 5}},
 "quality_map_mode": "relative_to_target",
 "quality_map": [{"circumstance": "any", "degree": "progress clock completes first", "quality_rung": "the declared target"},
                 {"circumstance": "any", "degree": "spoilage clock completes first", "quality_rung": "none: the work is ruined; primary material consumed, reagent kept"}],
 "quality_rungs": [{"id": q["id"], "index": q["index"], "signature_slots": q["signature_slots"], "magnitude_slots": q["magnitude_slots"]} for q in QUALITY[:5]],
 "degree_effects": {"critical_success": "greater", "critical_failure": "flawed"},
 "degree_effect_rules": {"greater": "the completing beat is a critical success: one property +1 tier (may exceed tier_cap by 1); for an improvised item, the rung rises one (common -> fine) instead",
                         "flawed": "the spoilage clock stands at its last-but-one segment or later (3 of 4; 5 of 6) when the progress clock completes: one property slot holds a flaw from the primary material's flaws, else from item_properties.yaml#flaws (engine-drawn among those that apply)"},
 "tier_rule": {"tier_cap": "min(the grade cap's tier_cap, the highest rarity_band among the materials, 5); a band-0 stock material counts as band 1",
               "signature": "tier_cap", "magnitude": "tier_cap - 1, minimum 1"},
 "recency_window": 5, "slot_cap": "the base item's slot_cap",
 "project_clock": {"kind": "project", "visibility": "public", "segments": "by target rung (4/6/8/12)", "tick_sources": [{"on": "a resolved crafting step (the maker's frame)", "ticks": "delivered_reach"}],
                   "decay": [{"boundary": "week", "ticks": -1, "only_if": "no tick since last week"}], "time_per_tick": "the base item's make.time_per_tick",
                   "racing": {"name": "spoilage", "segments": "4 (6 for a wondrous target)", "kind": "danger", "visibility": "public", "tick_sources": [{"on": "a failed crafting step", "ticks": "U(severity of the step's cost)"}]}},
 "step_frame": {"verb": "verb.handle (crafted, improvised) -- the make license's methods", "attribute": "the make license's attribute (smithing Might, woodcraft Agility, alchemy and enchanting Intellect ...)",
                "deed_tag": "the base item's make.deed_tag", "dc": "the target rung's obstacle tier", "stakes": "risky (a failed step ticks spoilage U(S2) = 1 and takes one cost: cost.time or cost.gear on the materials; a critical failure ticks U(S3) = 2; a near miss may be taken as success at a cost with cost.time, which ticks no spoilage)",
                "levers": "the trade's tools (Precision, required for licensed work), a master's workshop (Precision), a recipe for the named property (Amplifying)"},
 "materials_consumed": {"primary": "price units: a common item consumes stock worth half its base price (rounded down, minimum 1); fine x1; masterwork x2; wondrous x4 -- in the material's own coins",
                        "reagent": "one unit, consumed on completion or ruin"},
}
dump("gen_craft.yaml", HDR("gen_craft.yaml", "the crafting domain of the gate->fill generator (00.11; constitution P5 sixth pass): the material\n#   gates the property pool (00.11.2), the manner of making picks the fill; type-tier x quality-tier per R2 #13."), gen_craft)

# ------------------------------------------------------------------ gen_gift.yaml
gen_gift = {
 "schema_version": 1, "lifecycle": "provisional", "domain": "gen.gift", "output_kind": "item | ability",
 "pool_ref": "item: item_properties.yaml#properties where domains contains gift; ability: gen_item_ability.yaml#pool (deed-gated entries) granted into the ACQUIRED partition (05.8.7)",
 "source": "the giver: a faction (its org tags + its patron deed tags, 11), an NPC (role_tags, 12), or a power (a creature.spirit/fiend/celestial entity or a keeper with deed.divine/primal tags, 13)",
 "who_decides_to_give": "never this file: a faction's or NPC's choice to give is 11's (World Turn, rewards of threads) or 15's (standing, bargains) or 04.11.3's (an authority lends an item); gen.gift only decides WHAT",
 "circumstances": [
   {"id": "earned", "true_only_when": "a thread, a commitment or a bargain fact names a reward owed to the PC by this giver and the PC has met its terms", "false_for": "a gift given out of goodwill with nothing owed (favored); a gift in exchange for a NEW obligation (bargained)"},
   {"id": "favored", "default": True, "true_only_when": "the giver's standing toward the PC is +2 Friendly or higher and the gift is given unasked or on a simple request", "false_for": "a reward owed (earned); anything with a price attached (bargained)"},
   {"id": "bargained", "true_only_when": "the PC accepts a new obligation in return, written as a commitment fact before the gift (an oath, a service owed, a pact; 11)", "false_for": "a debt already owed to the PC (earned)"}],
 "fill_map": [{"circumstance": "earned", "fill_method": "chosen"}, {"circumstance": "favored", "fill_method": "signature"}, {"circumstance": "bargained", "fill_method": "chosen"}],
 "quality_map": [{"circumstance": "earned", "degree": "none", "quality_rung": "masterwork"}, {"circumstance": "favored", "degree": "none", "quality_rung": "masterwork"},
                 {"circumstance": "bargained", "degree": "none", "quality_rung": "wondrous"}],
 "allows_degree_none": True,
 "quality_rungs": [{"id": q["id"], "index": q["index"], "signature_slots": q["signature_slots"], "magnitude_slots": q["magnitude_slots"]} for q in QUALITY[:5]],
 "degree_effects": {"critical_success": "none", "critical_failure": "none"},
 "tier_rule": {"tier_cap": "the giver's band: a faction's tier mapped 0-1 -> 1, 2 -> 2, 3 -> 3, 4 -> 4, 5+ -> 5 (11); an NPC's or power's threat band",
               "signature": "tier_cap", "magnitude": "tier_cap - 1, minimum 1"},
 "signature_rule": "the giver's boon_signature (a faction's or power's `boon_signature` prop, 11/13) is always eligible for its gifts regardless of gate tags (it IS the giver's identity), subject to base kinds and tier; favored places it (signature fill); earned and bargained show it among the chosen candidates; default boon signature: the default_signature of the giver's first creature tag, else none",
 "ability_gifts": {"who": "only a power (creature.spirit, creature.fiend, a keeper of deed.divine or deed.primal) may give an ability", "partition": "acquired, provisional (05.8.7)",
                   "pool": "gen_item_ability.yaml#pool entries whose gate matches the giver's deed tags", "rank": 1, "condition": "may carry the giver's condition as a commitment fact (05.8.7)"},
 "chosen_display": "the tool shows up to three eligible entries per slot (00.11.3 step 4), drawn by weight without replacement; the player picks one per slot",
 "recency_window": 5, "slot_cap": "the base item's slot_cap",
 "base_rule": "the giver names the base (a faction's customary gift: an order's blade, a guild's ring), or the player names an item tag the giver plausibly has (a [J:flag] on the giver's nature; uncertain -> the giver's customary gift)",
 "anti_minting": "a gift item carries provenance.domain gen.gift and the fact gifted_by: <giver>; selling it is a conduct.loyalty event with the giver if they learn of it (11), and it sells at the property-item rule (08.8.5)",
}
dump("gen_gift.yaml", HDR("gen_gift.yaml", "the gift domain of the gate->fill generator (00.11): patron, order and faction boons. The giver\n#   gates the pool; what the gift answers (a debt, goodwill, a bargain) picks the fill."), gen_gift)

# ------------------------------------------------------------------ gen_item_ability.yaml
ABS_ACTIVE = [p for p in ABSORB["pool"] if p.get("activation") == "active"]
pool_ia = []
for p in ABS_ACTIVE:
    pool_ia.append({"id": p["id"], "source": "gen_absorb.yaml (a natural power, mirrored in abilities.yaml)", "gate_tags": p["gate_tags"], "excluded_tags": p.get("excluded_tags", []),
                    "mod_group": p["mod_group"], "weight": p["weight"], "min_tier": p["min_tier"], "signature_eligible": bool(p.get("signature_eligible")),
                    "bias": {"strike": "strike", "ward": "ward", "move": "move", "sense": "sense"}.get(p.get("bias"), "arcane"), "rank_rule": "the absorbed tier row <= the item tier",
                    "lifecycle": "provisional", "basis": ["04.10.5", "08.4.3"]})
BRANCH_BIAS = {"martial": "strike", "guile": "move", "wilds": "sense", "lore": "sense", "arcane": "arcane", "divine": "ward", "primal": "arcane", "influence": "social", "craft": "craft"}
for a in ABIL.values():
    if a.get("activation") != "active" or a.get("slot_class") != "calling" or a.get("requires_conduct") or a.get("conduct_pole"):
        continue
    first = a["tags"][0]
    br = first.split(".")[1]
    pool_ia.append({"id": a["id"], "source": "abilities.yaml (a calling technique)", "gate_tags": [".".join(first.split(".")[:3])], "excluded_tags": [],
                    "mod_group": a["mod_group"], "weight": 2 if a["min_tier"] <= 2 else 1, "min_tier": a["min_tier"], "signature_eligible": False,
                    "bias": BRANCH_BIAS[br], "rank_rule": "item tier 3 -> rank 1; 4 -> rank 2; 5+ -> rank 3; never above the ability's authored ranks",
                    "lifecycle": "provisional", "basis": ["05.2.8", "08.4.3"]})
for e in pool_ia:
    for t in e["gate_tags"]:
        chk_tag(t, e["id"])
SOURCE_TO_DEED = {
 "creature.beast": ["deed.wilds", "deed.martial.unarmed"], "creature.folk": ["the archetype's evidence_tags (09)"],
 "creature.undead": ["deed.arcane.necromancy", "deed.divine.exorcism"], "creature.spirit": ["deed.primal.spirits", "deed.divine.revelation"],
 "creature.spirit.fey": ["deed.arcane.illusion", "deed.guile.deception", "deed.primal.growth"], "creature.spirit.celestial": ["deed.divine.healing", "deed.divine.warding", "deed.divine.smiting"],
 "creature.fiend": ["deed.arcane.fire", "deed.divine.pact", "deed.influence.intimidation"], "creature.construct": ["deed.arcane.warding", "deed.craft.artifice"],
 "creature.elemental.fire": ["deed.arcane.fire", "deed.primal.elements"], "creature.elemental.frost": ["deed.arcane.frost", "deed.primal.elements"],
 "creature.elemental.air": ["deed.arcane.storm", "deed.primal.weather"], "creature.elemental.earth": ["deed.arcane.earth", "deed.primal.elements"],
 "creature.elemental.water": ["deed.primal.elements", "deed.primal.weather"], "creature.dragon": ["deed.arcane.fire", "deed.influence.intimidation", "deed.martial.unarmed"],
 "creature.horror": ["deed.arcane.mind", "deed.arcane.alteration"],
 "org.faith": ["deed.divine"], "org.order.knightly": ["deed.martial", "deed.divine.oaths"], "org.order.arcane": ["deed.arcane"], "org.order.druidic": ["deed.primal"],
 "org.order.hunters": ["deed.wilds", "deed.martial.archery"], "org.order.monastic": ["deed.lore", "deed.martial.unarmed"], "org.guild": ["deed.craft", "deed.influence.trade"],
 "org.crown.military": ["deed.martial.tactics", "deed.influence.command"], "org.outlaw": ["deed.guile"], "org.cult": ["deed.divine.pact", "deed.arcane.necromancy"],
 "material.essence": ["deed.arcane"], "material.wood.witchwood": ["deed.arcane", "deed.primal"]}
for k, v in SOURCE_TO_DEED.items():
    chk_tag(k, "source_to_deed")
    for d in v:
        if d.startswith("deed."):
            chk_tag(d, "source_to_deed")
gen_ia = {
 "schema_version": 1, "lifecycle": "provisional", "domain": "gen.item_ability", "output_kind": "ability",
 "called_by": "generate(gen.loot | gen.craft | gen.gift) when prop.bound_power fills a signature slot; the parent's source, circumstance and degree pass through",
 "pool_gate": {"natural": "entries sourced from gen_absorb.yaml gate on creature tags directly (a beast's trophy holds a beast's power)",
               "technique": "entries sourced from abilities.yaml gate on deed tags; a source with no deed tags of its own uses source_to_deed (most specific matching key)",
               "never": ["oath-gated or conduct-gated abilities (requires_conduct)", "adversary_only entries", "passive abilities (an item passive is a property, not an ability)", "an ability the bearer already holds (05.2.9: it stays dormant)"]},
 "source_to_deed": SOURCE_TO_DEED,
 "circumstances": "inherited from the parent call (loot: decisive/costly/merciful/scavenged; craft: crafted/commissioned/improvised; gift: earned/favored/bargained)",
 "fill_map": [{"circumstance": "decisive", "fill_method": "signature", "note": "the archetype's signature_of absorbed power if one passes the gate, else weighted"},
              {"circumstance": "costly", "fill_method": "biased", "bias_tag": "ward"}, {"circumstance": "merciful", "fill_method": "chosen"}, {"circumstance": "scavenged", "fill_method": "weighted"},
              {"circumstance": "crafted", "fill_method": "chosen"}, {"circumstance": "commissioned", "fill_method": "biased", "bias_tag": "the named bias"}, {"circumstance": "improvised", "fill_method": "weighted"},
              {"circumstance": "earned", "fill_method": "chosen"}, {"circumstance": "favored", "fill_method": "signature"}, {"circumstance": "bargained", "fill_method": "chosen"}],
 "quality_rungs": [{"id": "bound", "signature_slots": 1, "magnitude_slots": 0}],
 "quality_map": [{"circumstance": "any", "degree": "any", "quality_rung": "bound"}],
 "degree_effects": {"critical_success": "none (the parent's Greater already raised the tier)", "critical_failure": "none"},
 "tier_rule": {"signature": "the parent property's tier (prop.bound_power's tier)", "rank": "tier 3 -> rank 1; 4 -> rank 2; 5+ -> rank 3; capped at the ability's authored ranks; an absorbed power uses its highest authored tier row <= the item tier"},
 "recency_window": 5, "slot_cap": 1,
 "binding": {"partition": "equipped (05.2.8): one slot while the item is equipped and attuned", "rank": "the item's stated rank, never a calling's",
             "cost": "the ability's Focus at that rank + 1 relic surcharge when the holder has no training license at or above its first tag (05.6.3)",
             "evidence": "feeds_evidence: false (00.11.5; 04 request 11): deeds done through it write no deed evidence", "uses": "its own limits, counted by the engine (00.10.9)"},
 "pool": pool_ia,
}
dump("gen_item_ability.yaml", HDR("gen_item_ability.yaml", "the item-ability domain of the gate->fill generator (00.11): which active ability an item holds.\n#   Pool = ch.04's absorbed natural powers (creature-gated) and ch.05's calling techniques (deed-gated); never authored anew."), gen_ia)

# ------------------------------------------------------------------ economy.yaml
economy = {
 "schema_version": 1, "lifecycle": "provisional",
 "currency": {"units": [{"id": "coin", "definition": "one day's plain food and a bed in a common room (02's assumed unit, confirmed)", "integer": True}],
              "lots": "anything cheaper than 1 coin is sold by the LOT at 1 coin (5 torches, 2 days' trail rations, 10 candles, 20 sling bullets); no sub-coin exists (SG-23)",
              "weight": "100 coins = 1 load unit; fewer weigh nothing", "quantity": "coin is a quantity on the character (update_quantity; every change is a tool write, R1 08)"},
 "price_bands": [{"band": 0, "name": "trifle", "min": 1, "max": 1, "notch": 1}, {"band": 1, "name": "cheap", "min": 2, "max": 5, "notch": 1},
                 {"band": 2, "name": "modest", "min": 6, "max": 25, "notch": 2}, {"band": 3, "name": "costly", "min": 26, "max": 125, "notch": 10},
                 {"band": 4, "name": "precious", "min": 126, "max": 625, "notch": 50}, {"band": 5, "name": "treasure", "min": 626, "max": 3125, "notch": 250},
                 {"band": 6, "name": "fortune", "min": 3126, "max": None, "notch": 1000}],
 "valuable_band": 3,
 "quality_rungs": QUALITY,
 "property_value_by_tier": PROP_VALUE, "item_ability_value": "x2 the tier value", "relic_license_value": "the tier value",
 "list_price": "base price x quality multiplier (worn: x1/2) + the sum of property values (00.10.6 adjust family for price; integers only)",
 "buying": {"asking": "list + 1 notch of the list's band", "availability": [
    {"settlement": "camp or waystation", "max_band": 1, "rungs": ["worn", "common"], "special_stock": False},
    {"settlement": "village", "max_band": 2, "rungs": ["worn", "common", "fine (weekly 1-in-6)"], "special_stock": False},
    {"settlement": "town", "max_band": 3, "rungs": ["worn", "common", "fine"], "special_stock": "rarity_band <= 2", "masterwork": "by commission only"},
    {"settlement": "city", "max_band": 5, "rungs": ["worn", "common", "fine", "masterwork (commission or a curio dealer)"], "special_stock": "rarity_band <= 3", "property_items": "a curio dealer's stock: d4 property items each week, generated as scavenged at the region's band, sold at list + 2 notches"}],
    "oracle": "an item not listed for a settlement is not there; asking whether a specific trader has it is an Oracle question at Unlikely (one band above the settlement's max) or Remote (two)"},
 "selling": {"mundane": "half of list (x1/2), rounded down, minimum 1", "trade_goods": "list where the goods are scarce; list minus one notch where common",
             "treasure": "list minus one notch to a jeweler, broker or temple in a town or city; half of list elsewhere",
             "property_items": "half of list, and ONLY through clk.find_buyer (6 segments, project, public; ticks per week: town 1, city 2, plus delivered reach of one Talk (trade) beat per week); a village or camp never buys them",
             "own_make": "an item the seller made sells for at most its materials' price + the maker's craft wage for the days worked (the labor cap, 08.8.9)",
             "market_depth_per_week": {"camp": 10, "village": 30, "town": 150, "city": 750, "rule": "the most coin a settlement pays the PC per week for non-trade goods; past it, buyers are gone until next week"},
             "glut": "each sale of the same base item or trade good in one settlement in one week lowers that good's sale price there by one notch, recovering one notch per week (h.08.markets)"},
 "haggling": {"anchor": "verb.talk with primary tag deed.influence.trade.haggling against the trader's Wits or Presence defense (15 composes it with standing)",
              "buying": {"delivered_reach_0": "the asking price stands", "1": "list", "2": "list - 1 notch", "3": "list - 2 notches", "4": "list - 3 notches"},
              "selling": {"delivered_reach_0": "the offer stands (half of list)", "1": "half + 1 notch", "2": "half + 2 notches", "3": "half + 3 notches", "4": "list - 1 notch"},
              "floor": "a price never falls below the materials floor: half of list for a seller's own stock", "repeat": "one haggle per item per trader per day (01's repetition rule)",
              "critical_failure": "cost.closed_door: the trader will not deal with the PC this week (15)"},
 "lifestyles": [
   {"id": "destitute", "weekly_cost": 0, "unit": 1, "rest_site": "rough", "social": "a Precision snag on Talk where appearance matters (shabby)", "effects": [{"effect_id": "eff.07.rest_cap", "params": {"cap": "partial", "applies_when": "rest_long in town on this lifestyle"}}]},
   {"id": "poor", "weekly_cost": 4, "unit": 4, "rest_site": "camp", "social": "none among common folk; a snag at court"},
   {"id": "modest", "weekly_cost": 7, "unit": 7, "rest_site": "haven", "social": "none"},
   {"id": "comfortable", "weekly_cost": 14, "unit": 14, "rest_site": "haven", "social": "a citable fact of means (a lever where credit matters)"},
   {"id": "wealthy", "weekly_cost": 35, "unit": 35, "rest_site": "haven", "social": "a Precision lever on Talk with merchants and officials where means matter", "includes": "one servant"},
   {"id": "noble", "weekly_cost": 100, "unit": 100, "rest_site": "haven", "social": "a Precision lever on Talk at court; expected of rank 2+ in a crown faction (11)", "includes": "a household of four"}],
 "lifestyle_rules": {"paid_by": "h.08.upkeep at each week boundary (phase 4) for every week the PC spent any day in a settlement; a venture week costs supply instead (10)",
                     "shortfall": "unable to pay: the lifestyle drops one rung for that week and the PC takes the lower rung's effects; debt is 11's",
                     "unit_rule": "a Unit of wealth for this character = the weekly cost of the current lifestyle (minimum 1); U(severity) Units is a cost of that severity in coin (S1 1 Unit ... S5 4 Units). 03's generosity ground floor = 1 Unit"},
 "wealth_tiers": [{"tier": "W1", "name": "scraping", "coin_and_liquid": "0-50", "typical_band": "P1"}, {"tier": "W2", "name": "solvent", "coin_and_liquid": "51-300", "typical_band": "P1-P2"},
                  {"tier": "W3", "name": "prosperous", "coin_and_liquid": "301-1500", "typical_band": "P2-P3"}, {"tier": "W4", "name": "rich", "coin_and_liquid": "1501-8000", "typical_band": "P3-P4"},
                  {"tier": "W5", "name": "magnate", "coin_and_liquid": "8001+", "typical_band": "P4-P5"}],
 "purses": [{"band": 1, "die": "d4", "coin": "1d4 - 1"}, {"band": 2, "die": "2d6", "coin": "2d6"}, {"band": 3, "die": "4d6", "coin": "4d6 + 5"},
            {"band": 4, "die": "6d10", "coin": "6d10 + 20"}, {"band": 5, "die": "10d10", "coin": "10d10 + 80"}],
 "purse_rule": "folk and other carriers of coin only (09 marks purse: none for beasts); one purse per defeated or robbed creature, rolled by roll_table",
 "hoard_coin": [{"band": 1, "coin": "3d6 x 3"}, {"band": 2, "coin": "4d10 x 5"}, {"band": 3, "coin": "6d10 x 15"}, {"band": 4, "coin": "8d10 x 50"}, {"band": 5, "coin": "10d10 x 150"}],
 "hoard_goods": [{"band": 1, "goods": "d4 trade goods or a semiprecious gem"}, {"band": 2, "goods": "d4 semiprecious gems and an art object"}, {"band": 3, "goods": "d4 precious gems and d2 art objects"},
                 {"band": 4, "goods": "d6 precious gems, d4 art objects, a treasure of art"}, {"band": 5, "goods": "a great gem, d6 precious gems, d4 treasures of art"}],
 "services": [
   {"id": "svc.lodging_common", "price": 1, "per": "day", "what": "a bed in a common room and a plain meal (the coin's definition)"},
   {"id": "svc.lodging_private", "price": 3, "per": "day", "what": "a private room and good meals"}, {"id": "svc.stabling", "price": 1, "per": "day per mount", "what": "stall, fodder, grooming"},
   {"id": "svc.bath_laundry", "price": 1, "per": "visit", "what": "clears a 'filthy' or 'shabby' fact"}, {"id": "svc.messenger", "price": 1, "per": "travel day of the route", "what": "a letter carried by a runner or rider"},
   {"id": "svc.scribe", "price": 1, "per": "letter; 2 per page copied", "what": "writing and fair copies"}, {"id": "svc.sage", "price": 10, "per": "question", "what": "a Recall by a sage (lore, band 2) on one question; the answer is the sage's frame (12)"},
   {"id": "svc.identify", "price": 10, "per": "item", "what": "a sage or enchanter unseals every property of one item (08.5.3); town or city"},
   {"id": "svc.healer", "price": 2, "per": "day of care", "what": "Treat by a trained healer (07.8.8), with kit"}, {"id": "svc.surgeon", "price": 10, "per": "operation", "what": "surgery (deed.lore.medicine.surgery) for a wound (07)"},
   {"id": "svc.cure", "price": "band 3 (by severity: S1 26, S2 40, S3 60, S4 90, S5 125)", "per": "affliction", "what": "a temple's or cunning-folk's cleansing of a poison, disease or curse (05 rites; 07.9.6)"},
   {"id": "svc.rite_for_hire", "price": "personal 10, local 50, site 250, regional 1250 + components", "per": "rite", "what": "a rite performed by a ritualist who knows it (05.8; scale 05.8.3)"},
   {"id": "svc.repair", "price": "damaged: 1 notch of the item's list band; broken: 2 notches", "per": "item", "what": "repair by a licensed crafter (08.6.7); masterwork needs trained, wondrous expert"},
   {"id": "svc.commission", "price": "materials + the crafter's weekly wage x weeks (round up) + 1 notch", "per": "item", "what": "08.6.5"},
   {"id": "svc.training", "price": "trained mentor 7, expert 25, master 100", "per": "week", "what": "a training week (15; 05.8.5, 05.9)"},
   {"id": "svc.passage_road", "price": 2, "per": "day", "what": "a seat on a coach or carter's wagon with food"}, {"id": "svc.passage_river", "price": 1, "per": "day", "what": "deck passage on a barge"},
   {"id": "svc.passage_sea", "price": 3, "per": "day", "what": "passage on a cog with food; a cabin x2"}, {"id": "svc.ferry", "price": 1, "per": "crossing", "what": "river ferry"},
   {"id": "svc.toll", "price": 1, "per": "bridge or gate", "what": "a common toll (11's factions may double it)"}],
 "wages": [
   {"id": "wage.porter", "band": 1, "weekly": 7, "daily": 1, "role": "porter, torchbearer, linkboy, camp hand (carries 10 load)"},
   {"id": "wage.skilled", "band": 1, "weekly": 10, "daily": 2, "role": "guide, cook, groom, scribe, carter"},
   {"id": "wage.soldier", "band": 2, "weekly": 14, "daily": 2, "role": "guard, archer, scout, sailor"},
   {"id": "wage.specialist", "band": 2, "weekly": 21, "daily": 3, "role": "trained healer, locksmith, sapper, hedge-witch"},
   {"id": "wage.veteran", "band": 3, "weekly": 50, "daily": 8, "role": "sergeant, veteran mercenary, journeyman mage", "share": "plus a half share of coin found"},
   {"id": "wage.champion", "band": 4, "weekly": 150, "daily": 25, "role": "a renowned fighter or master of an art", "share": "plus a full share; hires only for a thread they believe in (16)"},
   {"id": "wage.legend", "band": 5, "weekly": None, "daily": None, "role": "never for coin: only for a cause, a debt or a bond (16)"}],
 "craft_wages": {"trained": 10, "expert": 25, "master": 60, "unit": "coins per week of work; the labor cap of 08.8.9 and the commission price of 08.6.5"},
 "holdings": [
   {"id": "hold.cottage", "buy": 150, "build_weeks": 6, "upkeep_week": 1, "staff": 0, "yield_week": 0, "what": "a home: a haven rest site; modest lifestyle at 4 coins/week while living there"},
   {"id": "hold.townhouse", "buy": 600, "build_weeks": 12, "upkeep_week": 3, "staff": 1, "yield_week": 0, "what": "a town home; comfortable lifestyle at 9/week while living there"},
   {"id": "hold.workshop", "buy": 400, "build_weeks": 8, "upkeep_week": 2, "staff": 1, "yield_week": "the worker's craft wage minus wages (labor value only)", "what": "a workplace for one craft (a forge, a still)"},
   {"id": "hold.shop", "buy": 800, "build_weeks": 10, "upkeep_week": 3, "staff": 2, "yield_week": "d6 x 5 gross in a town, x10 in a city, before wages (11 runs it)", "what": "a shop selling made or bought goods"},
   {"id": "hold.tavern", "buy": 1500, "build_weeks": 16, "upkeep_week": 8, "staff": 3, "yield_week": "d6 x 10 gross before wages", "what": "an inn; rumors (11) and lodging at cost"},
   {"id": "hold.farmstead", "buy": 1000, "build_weeks": 12, "upkeep_week": 4, "staff": 4, "yield_week": "supply 20/week in season; nothing in winter", "what": "food and a haven in the country"},
   {"id": "hold.watchtower", "buy": 3000, "build_weeks": 26, "upkeep_week": 10, "staff": 4, "yield_week": 0, "what": "a defensible haven; a faction's notice (11)"},
   {"id": "hold.manor", "buy": 8000, "build_weeks": 52, "upkeep_week": 30, "staff": 10, "yield_week": "rents: d6 x 20 if the land is held (11)", "what": "a seat; noble lifestyle included"},
   {"id": "hold.keep", "buy": 25000, "build_weeks": 104, "upkeep_week": 80, "staff": 30, "yield_week": "rents and tolls: 11", "what": "a stronghold; a faction in its own right at tier 1 (11)"}],
 "holding_rules": "11 owns holdings as play (improvements, staff, threats, yields as clocks); these are the prices. Building is a craft.building project (08.6) on a 12-segment clock per 13 weeks of build_weeks or part, with workers at wage.porter/skilled; buying needs a charter (bi.charter).",
 "carry": {"formula": "capacity = 10 + 2 x Might (Might -1 -> 8 ... +4 -> 18); lic.people.great_frame counts Might +1 for this only (02)",
           "states": [{"id": "unburdened", "when": "load <= capacity"}, {"id": "burdened", "when": "capacity < load <= 2 x capacity", "effects": "engine-cited Precision snag 'burdened' on Evade, Sneak and Exert; Move pace one step slower (06); travel pace one step slower (10)"},
                      {"id": "overloaded", "when": "load > 2 x capacity", "effects": "cannot Move or travel while holding it all; drop or drag (one band per round, nothing else)"}],
           "item_share": "+4 capacity from items at most (08.2.2)"},
 "supply": {"unit": "1 supply = one person's food and water for one day (10 owns use and want)", "price": "trail rations: 2 supply per coin (a lot); market food 1 coin per supply in a camp",
            "load": "every 2 supply, or part of 2, = 1 load unit", "kit_food": "a kit's food xN is N supply (02)", "item_share": "items lower daily use by at most 1 (08.2.2)"},
 "light": {"torch": "lot of 5 for 1 coin; each burns intervals:6; bright to band.close, dim to band.near", "lantern": "5 coins; a flask of oil burns intervals:24; oil 2 flasks per coin", "candle": "lot of 10 for 1 coin; each burns intervals:6; dim to band.close", "owner": "10 runs h.10.light; these are the goods"},
 "ammunition": {"arrows": "20 for 2 coins (1 load)", "bolts": "20 for 3 coins (1 load)", "sling_bullets": "20 for 1 coin (1 load)", "recovery": "half of those spent, rounded down, after a conflict (06.4.9)"},
 "mount_upkeep": "base_items.yaml upkeep_week per mount stabled; grazing in grassland or farmland in spring-autumn costs nothing; on a venture a mount eats 1 supply per day unless grazing (10)",
 "anti_inflation": [
   {"id": "AI-1", "rule": "Magic never mints coin: anything conjured, summoned or transmuted carries conjured: true, has price 0 and cannot be sold; turning base matter into precious matter is G4 unless 13's canon allows it, and then the result is conjured"},
   {"id": "AI-2", "rule": "The labor cap: an item the seller made sells for at most its materials' price + the maker's craft wage for the days worked"},
   {"id": "AI-3", "rule": "Property items sell for half of list and only through clk.find_buyer; villages and camps never buy them"},
   {"id": "AI-4", "rule": "Market depth per settlement per week caps coin paid to the PC for non-trade goods"},
   {"id": "AI-5", "rule": "Glut: repeated sales of the same good in one place lower its price one notch per sale per week"},
   {"id": "AI-6", "rule": "Coin enters only from purses, hoards, wages, rewards (11), sales and holdings' yields, each from a table here or in 11 -- never from a DM's choice (INV-3)"},
   {"id": "AI-7", "rule": "Supply-saving and carry-raising items are capped by the item share (08.2.2): -1 supply/day, +4 capacity"},
   {"id": "AI-8", "rule": "Holdings yield at most the labor of their staff and their land's rents; a yield table is 11's and is rolled, never chosen"}],
}
dump("economy.yaml", HDR("economy.yaml", "money, prices, selling, haggling, lifestyles, wealth tiers, services, wages, holdings' prices,\n#   carrying capacity, supply, light, ammunition and the anti-inflation rules (08.8-08.9)."), economy)

# ------------------------------------------------------------------ contrib fragments
eff_frag = {"schema_version": 1, "blocks": [{"owner": "08", "entries": [dict(id=k, **v) for k, v in NEW_EFFECTS.items()]}]}
dump("../_process/merged-contrib/effects.08.yaml", "# data/contrib/effects.08.yaml\n# Purpose: ch.08's owner-block for data/effects.yaml: three definitions no core effect with parameters expresses (PR-00-8).\n# Owner: 08-items-loot-crafting. Schema: data/SCHEMAS.md#effectsyaml. Decision: DL-08-21.", eff_frag)
lic_frag = {"schema_version": 1, "blocks": [{"owner": "08", "entries": [
  {"id": "lic.08.relic_grant", "name": "A relic's granted license (the item-property license kind)", "kind": "item_property", "tags": [],
   "principle": "An item lets its bearer attempt what a named license permits, as a borrowed capability.",
   "scope": "While the item is equipped and attuned, the bearer holds the license its property names (prop.lic_* or prop.bound_power) at the grade the property names, with these fixed differences from holding it by training: grants_competence is empty (00.3.6: items never grant competence); feeds_evidence: false (00.11.5); abilities used through it cost +1 Focus when the bearer has no training license at or above their first tag (05.6.3).",
   "excludes": [{"what": "competence on the license's tag", "needs": "the license by an origin, mentor, text or calling (05.9)"},
                {"what": "evidence toward a calling from deeds done under it", "needs": "deeds done under one's own licenses"}],
   "attribute": "by_method", "crude_fallback": "none", "stretch": None, "emulate": None,
   "acquisition_paths": [{"type": "item", "detail": "loot, craft or gift with prop.lic_* or prop.bound_power (08.4)", "clock": None, "requires": None}],
   "feeds_evidence": False, "source": "the item's id", "lifecycle": "provisional", "basis": ["00.11.5", "R2 #9 (Honorblades)", "04 Interface request 11", "DL-08-11"]},
  {"id": "lic.08.attunement", "name": "Attunement", "kind": "universal", "tags": [],
   "principle": "Bind a magical item to yourself so its passive properties and powers answer you.",
   "scope": "At a breather outside a conflict, attune one equipped item that carries a passive, license or item-ability property; at most five attuned items at a time. Attuning unseals the item's properties to you (08.5.2). Ending attunement is a free activity unless a flaw forbids it.",
   "excludes": [{"what": "a sixth attuned item", "needs": "end another attunement first"}],
   "attribute": "none", "crude_fallback": "none", "stretch": None, "emulate": None,
   "acquisition_paths": [{"type": "origin", "detail": "every character holds it", "clock": None, "requires": None}],
   "lifecycle": "provisional", "basis": ["08.5.1", "R2 08 Iron Man Principle", "DL-08-14"]}]}]}
dump("../_process/merged-contrib/licenses.08.yaml", "# data/contrib/licenses.08.yaml\n# Purpose: ch.08's owner-block for data/licenses.yaml (T-00-19 allows owner-block 08).\n# Owner: 08-items-loot-crafting. Schema: data/SCHEMAS.md#licensesyaml (License, 00.12.1).", lic_frag)
bnd_frag = {"schema_version": 1, "blocks": [{"owner": "08", "handlers": [
  {"id": "h.08.upkeep", "boundary": "week", "phase": 4, "interrupting": False, "effect": "charge the lifestyle (if any day of the week was spent in a settlement), mount stabling, holdings' upkeep and hirelings' coin wages not paid by 16's handler; shortfall drops the lifestyle one rung (08.8.6)", "rule_id": "08.8.6"},
  {"id": "h.08.markets", "boundary": "week", "phase": 6, "interrupting": False, "effect": "recover one notch of glut per good per settlement; reset market depth; restock curio dealers (d4 property items in cities); tick each clk.find_buyer by its settlement's weekly ticks", "rule_id": "08.8.5"},
  {"id": "h.08.durations", "boundary": "*", "phase": 1, "interrupting": False, "effect": "expire item effect instances with uses: or duration forms (oils, elixirs, imbued properties at season), mark spent light sources", "rule_id": "08.1.9"},
  {"id": "h.08.craft_decay", "boundary": "week", "phase": 5, "interrupting": False, "effect": "covered by h.00.clock_auto (crafting project clocks carry decay rows); listed for traceability only", "rule_id": "08.6.4"}]}]}
dump("../_process/merged-contrib/boundaries.08.yaml", "# data/contrib/boundaries.08.yaml\n# Purpose: ch.08's owner-block for data/boundaries.yaml (h.08.upkeep is reserved in T-00-9; the rest are added).\n# Owner: 08-items-loot-crafting. Schema: data/SCHEMAS.md#boundariesyaml.", bnd_frag)
tag_frag = {"schema_version": 1, "proposed_by": "08", "tags": list(NEW_TAGS.values())}
dump("../_process/merged-contrib/tags.08.yaml", "# data/contrib/tags.08.yaml\n# Purpose: level-3 item tags proposed by ch.08 (steward of `item` and `material`), per 00.5.5 and PR-03-6.\n# Owner: proposed by 08 to 03. Schema: data/SCHEMAS.md#tagsyaml. Sibling budget (8 per parent) respected.", tag_frag)

print("properties", len(PROPS), "signature-eligible", sum(p["signature_eligible"] for p in PROPS), "base items", len(BI), "materials", len(MATS), "item-ability pool", len(pool_ia))
print("default signatures", len(DEFAULT_SIG))
