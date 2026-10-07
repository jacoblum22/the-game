# 13_data_world.py -- chapter 13's world canon for the Thallen March: canon_impossible, the Hush, the eight
# magic-canon items of 05.7.10, keepers, tongues, peoples present, names, calendar names, regional values,
# lifespans, and the regional NPC / omen / furnishing tables that replace 12's generic ones.
# Read by 13-gen_region.py, which validates every id against the canonical data and writes the files.
# All names and texts are original to this ruleset.

REGION = "loc.thallen"

# ----------------------------------------------------------------------------------------------- canon
CANON_IMPOSSIBLE = [
    # (05.7.10 item 1: magic) -- each a G4 for everyone (01.3 test 2)
    {"id": "ci.resurrection", "text": "No working, rite or power returns the truly dead to life. A soul that has crossed Weyla's ford does not come back; the Stilled are not dead and are not covered by this line.", "scope": "magic", "basis": ["05.7.10 item 1", "05.7.8"]},
    {"id": "ci.time", "text": "No one travels in time, or undoes what has happened.", "scope": "magic", "basis": ["05.7.10 item 1"]},
    {"id": "ci.soul_making", "text": "No one makes a soul. A made thing (a golem, a bell-warden, a homunculus) has none, whatever it says.", "scope": "magic", "basis": ["05.7.10 item 1"]},
    {"id": "ci.absent_mind", "text": "No one reads or speaks into a mind that is not present in the scene (a sending rite carries words, not thoughts).", "scope": "magic", "basis": ["05.7.10 item 1", "rit.sending"]},
    {"id": "ci.unmaking_keepers", "text": "No one destroys a keeper. A keeper may be forgotten, starved of worship, bound or bargained with; never slain.", "scope": "magic", "basis": ["05.7.10 item 1"]},
    {"id": "ci.transmutation", "text": "No working makes gold, silver, ringsilver or any metal from another substance, and no working conjures lasting food, coin or goods from nothing. Conjured things vanish at the scene's end.", "scope": "magic", "basis": ["08 Interface request AI-1", "08.8.9", "08.6"]},
    {"id": "ci.regrowth", "text": "No working or rite regrows a lost limb, eye or organ (07's maims stand; prosthesis is the road back).", "scope": "magic", "basis": ["07 Interface request", "07.7"]},
    # the world
    {"id": "ci.sound_in_the_hush", "text": "In hushed ground no sound is made or heard by any means, save the peal of a true bell and what is spoken within its peal (13.2.3).", "scope": "world", "basis": ["13.2.3"]},
    {"id": "ci.spirits_in_the_hush", "text": "No spirit, ghost or summoned servant can be present or called in hushed ground; the Quiet stills them. Only the Quiet itself is there.", "scope": "world", "basis": ["13.2.3", "13.3.5"]},
    {"id": "ci.waking_the_stilled", "text": "Nothing wakes one of the Stilled except true sound by the Waking rule (13.2.4: a true bell within a day of the stilling; after that, a watch of true sound or the spring ebb, at Oracle odds Remote; or the Mother Bell rung whole). No medicine, working or rite does it.", "scope": "world", "basis": ["13.2.4"]},
    {"id": "ci.harming_the_quiet", "text": "The Quiet cannot be struck, wounded or slain by weapon or working: it has no body. It can be lulled (by true sound), bound (by the Mother Bell), bargained with, or woken.", "scope": "world", "basis": ["13.2.2"]},
    {"id": "ci.unaided_flight", "text": "No one flies in their own shape without magic, wings or a mount that flies.", "scope": "world", "basis": ["01 G4 test 2 example"]},
]

CANON_FACTS = [
    # established world laws the Oracle treats as settled (00.12.7; 01.3 test 2)
    {"id": "canon.hush.cause", "value": "the Quiet, a sleeping power under the Mere of Sael, half-woke when the Mother Bell cracked on Hush-eve, year 0", "visibility": "sealed", "gate": "case: the Prior's archive (the Bell-Prior's confession) or reaching the Mother Bell"},
    {"id": "canon.hush.ebb", "value": "the Hem retreats about one ring every ten to twelve years; each spring a strip of land a few hours' walk deep wakes", "visibility": "shown"},
    {"id": "canon.hush.pools", "value": "pockets of the Hush (hush-pools) linger behind the Hem in rings 3-4 and re-form wherever a true bell that has rung over a place for years falls silent", "visibility": "shown"},
    {"id": "canon.true_bell", "value": "a bell cast with ringsilver in Orrow's old alloy (or consecrated to Saint Thallow by rit.consecrate_ground cast with the bell in the circle) rings through the Hush: its peal opens hushed ground within band.far while it is rung", "visibility": "shown"},
    {"id": "canon.stilled", "value": "the Stilled do not age, eat or breathe; they are not dead; moss and lichen grow on them; they are heavy as stone (moving one is Exert vs Hard); a Stilled wakes by the Waking rule (13.2.4) and only by it: at once to a true bell rung over them within a day of their stilling; after that day they are SET, and wake only to a full watch of true sound or the spring ebb passing them (Oracle Remote, once per Stilled per season; 13.1.5 T2 changes the odds) or to the Mother Bell rung whole", "visibility": "shown"},
    {"id": "canon.woken", "value": "a Woken remembers nothing of the stilled years; their body is as it was the night they were stilled; they age from waking", "visibility": "shown"},
    {"id": "canon.last_bell", "value": "the Last Bell of Tolling is a true bell; it has rung every hour, day and night, since Hush-eve, rung by the Bellwardens in turn", "visibility": "shown"},
    {"id": "canon.default_bargainer", "value": "keeper.weyla", "visibility": "available", "note": "07.5.5: Weyla at the Ford answers at the door of death in the March for anyone dying outside hushed ground"},
    {"id": "canon.magic_lawful", "value": "magic is lawful in the March; necromancy that raises the dead is a hanging crime in Vantry lands (fac.thallen.vantry duties); a working with trait.sense.visible inside Tolling's market or the bell-tower close is a method consequence (01.11.2) that reaches the Bellwardens", "visibility": "available"},
    {"id": "canon.no_cities", "value": "the March has no city: Tolling is its largest settlement (a town); Esterlow's cities lie beyond the region", "visibility": "shown"},
]

# 13.2.3: the Hush as a hazard (owner-block entry in data/contrib/hazards.13.yaml)
HAZARDS = [
    {"id": "haz.thallen.hush_pool", "name": "Hush-pool", "tags": [], "terrain_tags": [],
     "harm_tags": ["harm.mind.strain"], "severity": "S1",
     "resist": {"verb": "verb.endure", "attribute": "resolve", "dc_tier": "moderate", "stakes": "risky"},
     "cadence": "watch",
     "conditions": [
         {"effect_id": "eff.apply_condition", "params": {"condition": "cond.silenced", "target": "every creature inside", "duration": "while inside the hazard's area"}},
         {"effect_id": "eff.apply_condition", "params": {"condition": "cond.deafened", "target": "every creature inside", "duration": "while inside the hazard's area"}}],
     "affliction": None, "no_reduction": True, "perceived_on_sight": False,
     "detect": {"tier": "easy", "note": "felt the moment one steps in: one's own footfall makes no sound"},
     "signs": ["birdsong stops at a line in the grass", "a dropped stone lands without a sound", "moss on the shoulders of someone standing very still"],
     "omens": [], "lethal_context": False,
     "aftermath": "a creature Down inside is stilled (13.2.4) unless carried out before the next watch",
     "protections": [{"means": "a true bell rung within band.far (a fact true_bell on an item rung as one action each round, or each interval out of conflict)", "effect": "negate"},
                     {"means": "the peal of a true bell rung over the place for one full watch", "effect": "ends the hazard there (written as a world change)"}],
     "pace_steps": 0, "feature_kind": "hazard", "avoid": ["go round it (the edge is a sign)", "ring a true bell"],
     "notes": "Rules effects, not harm: inside, cond.silenced and cond.deafened hold (no speech, so no Talk, no arcane or divine working; trait.sense.loud beats make no noise, a lever on Sneak). A dread exposure at S1 each watch spent inside (07.11.2). A creature Staggered or Down inside at a watch boundary is stilled. ci.sound_in_the_hush and ci.spirits_in_the_hush apply.",
     "lifecycle": "provisional", "basis": ["13.2.3", "10.12.8", "07.11.2", "cond.silenced", "cond.deafened"]},
    {"id": "haz.thallen.deep_hush", "name": "The deep Hush", "tags": [], "terrain_tags": [],
     "harm_tags": ["harm.mind.strain"], "severity": "S2",
     "resist": {"verb": "verb.endure", "attribute": "resolve", "dc_tier": "hard", "stakes": "dire"},
     "cadence": "watch",
     "conditions": [
         {"effect_id": "eff.apply_condition", "params": {"condition": "cond.silenced", "target": "every creature inside", "duration": "while inside the hazard's area"}},
         {"effect_id": "eff.apply_condition", "params": {"condition": "cond.deafened", "target": "every creature inside", "duration": "while inside the hazard's area"}}],
     "affliction": None, "no_reduction": True, "perceived_on_sight": True,
     "signs": ["no wind moves the grass though clouds race overhead", "whole villages standing in their lanes", "the light itself seems to wait"],
     "omens": [], "lethal_context": True,
     "aftermath": "a creature Down inside is stilled at once (13.2.4)",
     "protections": [{"means": "a true bell rung within band.far", "effect": "step -1 (to a hush-pool's effects) while rung"},
                     {"means": "the Mother Bell rung", "effect": "negate across the region"}],
     "pace_steps": 0, "feature_kind": "hazard", "avoid": ["turn back", "carry a true bell and a ringer to spare"],
     "notes": "As haz.thallen.hush_pool, at S2 dread each watch, Hard; lethal_context true because a creature Down here is stilled at once with no carry-out: stilling is a defeat with a recorded lethal context (07.2), and the last-chance menu applies. Covers ring 4's Quietlands and ring 5's Mere.",
     "lifecycle": "provisional", "basis": ["13.2.3", "10.12.8", "07.2", "07.11.2"]},
]

# ----------------------------------------------------------------------------------------------- keepers
KEEPERS = [
    {"id": "keeper.thallow", "name": "Saint Thallow, the Ringer", "kind": "saint",
     "what": "Orrow's first bell-founder, raised to power for ringing the Quiet to sleep; the keeper of true sound, of watchfulness and of the sleepless watch",
     "axes": [{"axis": "conduct.courage", "pole": "+"}, {"axis": "conduct.protection", "pole": "+"}],
     "despises": [{"axis": "conduct.courage", "pole": "-"}, {"axis": "conduct.piety", "pole": "-"}],
     "sign": "a bronze handbell worn at the belt or hung at the throat (item.tool.implement.holy_symbol)",
     "faith": "fac.thallen.bellwardens", "schools": ["deed.divine.warding", "deed.divine.exorcism", "deed.divine.oaths"],
     "rites_known": ["rit.consecrate_ground", "rit.great_exorcism", "rit.oath_binding", "rit.funeral"],
     "can_bargain": False, "tags": ["deed.divine", "conduct.courage", "conduct.protection"]},
    {"id": "keeper.aumbry", "name": "Aumbry of the Hearth", "kind": "god",
     "what": "the keeper of hearths, hospitality and the sick-bed; every farmhouse in the March keeps her hearth-key above the fire",
     "axes": [{"axis": "conduct.generosity", "pole": "+"}, {"axis": "conduct.mercy", "pole": "+"}],
     "despises": [{"axis": "conduct.generosity", "pole": "-"}],
     "sign": "an iron hearth-key on a cord (item.tool.implement.holy_symbol)",
     "faith": "fac.thallen.hearthkeepers", "schools": ["deed.divine.healing", "deed.divine.rites", "deed.divine.warding"],
     "rites_known": ["rit.vigil_of_healing", "rit.purification", "rit.seasonal_blessing", "rit.funeral"],
     "can_bargain": False, "tags": ["deed.divine", "conduct.generosity", "conduct.mercy"]},
    {"id": "keeper.merrow", "name": "Merrow the Weigher", "kind": "god",
     "what": "Esterlow's keeper of law, true weight and the given word; the realm's courts swear on her scales",
     "axes": [{"axis": "conduct.justice", "pole": "+"}, {"axis": "conduct.honesty", "pole": "+"}],
     "despises": [{"axis": "conduct.honesty", "pole": "-"}],
     "sign": "a brass balance-pin (item.tool.implement.holy_symbol)",
     "faith": "fac.thallen.weighhouse", "schools": ["deed.divine.revelation", "deed.divine.oaths", "deed.divine.smiting"],
     "rites_known": ["rit.oath_binding", "rit.augury"],
     "can_bargain": False, "tags": ["deed.divine", "conduct.justice", "conduct.honesty"]},
    {"id": "keeper.weyla", "name": "Weyla at the Ford", "kind": "god",
     "what": "the keeper of the dead and of their crossing; she stands at the ford between living and dead and lets each soul over in its time. She answers at the door of death in the March: the region's default bargainer (07.5.5)",
     "axes": [{"axis": "conduct.piety", "pole": "+"}, {"axis": "conduct.restraint", "pole": "+"}],
     "despises": [{"axis": "conduct.piety", "pole": "-"}],
     "sign": "a ford-stone: a river pebble worn through, on a thong (item.tool.implement.holy_symbol)",
     "faith": "fac.thallen.fordwardens", "schools": ["deed.divine.rites", "deed.divine.exorcism", "deed.divine.healing"],
     "rites_known": ["rit.funeral", "rit.great_exorcism", "rit.purification"],
     "can_bargain": True,
     "wants": ["that the dead be given to the ford (a body buried, burned or given to running water with the rite)",
               "that a restless dead be laid", "that one stilled by the Hush be woken or given to the ford",
               "that a coin be carried to the Ford-garden for one who died unburied in the Hem"],
     "bargain_asks": "the d6 of tbl.bargain_asks (07.5.5) read through her wants: 1 return a body taken from a grave; 2 bring a named restless dead to rest; 3 end a named necromancer or a thing that keeps the dead from crossing; 4 serve her one season in four for a year as a fordwarden; 5 carry her ford-stone and her message to a named grave in the Hem; 6 give up a named possession taken from the dead",
     "tags": ["deed.divine", "conduct.piety", "conduct.restraint"]},
    {"id": "keeper.wardens_vow", "name": "The Warden's Vow", "kind": "oath",
     "what": "the Bellwardens' sworn oath: 'No bell in my keeping falls silent while I breathe.' Held as an oath-keeper by those who swear it before the Last Bell",
     "axes": [{"axis": "conduct.loyalty", "pole": "+"}, {"axis": "conduct.protection", "pole": "+"}],
     "despises": [{"axis": "conduct.loyalty", "pole": "-"}],
     "sign": "the Warden's badge: a lantern over a bell, in pewter (item.tool.implement.holy_symbol)",
     "faith": "fac.thallen.bellwardens", "schools": ["deed.divine.oaths", "deed.divine.smiting", "deed.divine.warding"],
     "rites_known": ["rit.oath_binding"],
     "can_bargain": False, "tags": ["deed.divine", "conduct.loyalty", "conduct.protection"]},
    {"id": "keeper.lantern_man", "name": "The Lantern-Man of the Fen", "kind": "pact",
     "what": "once Orrow's keeper of lamps and lost travellers, sunk into the Sallow Fen when Orrow fell; he still keeps bargains, and keeps the ones who break them",
     "axes": [{"axis": "conduct.loyalty", "pole": "+"}, {"axis": "conduct.restraint", "pole": "-"}],
     "despises": [{"axis": "conduct.loyalty", "pole": "-"}],
     "sign": "a stub of corpse-candle in a little iron cage (item.tool.implement.holy_symbol)",
     "faith": "fac.thallen.lantern_bound", "schools": ["deed.divine.pact", "deed.divine.revelation"],
     "rites_known": ["rit.augury", "rit.oath_binding"],
     "can_bargain": True,
     "wants": ["a light carried into a dark place and left burning", "a promise made to him and kept", "the name of someone who broke a bargain"],
     "tags": ["deed.divine.pact", "conduct.loyalty", "conduct.restraint"]},
]

# ----------------------------------------------------------------------------------------------- magic canon (05.7.10)
MAGIC_CANON = {
    "item_1_canon_impossible": ["ci.resurrection", "ci.time", "ci.soul_making", "ci.absent_mind", "ci.unmaking_keepers", "ci.transmutation", "ci.regrowth", "ci.spirits_in_the_hush"],
    "item_2_sources": {
        "deed.arcane": {"words": "bell-grammar: the old Orrowan art of formula, worked by knowing the true names and measures of things as the bell-founders knew the measures of a bell", "who_can_learn": "anyone literate with a teacher or a text (05's default kept)", "regional_requires": "literacy (lic.lang.letters) and a teacher or a text; texts in Orrowan also need lic.lang.orrowan at accented"},
        "deed.divine": {"words": "the regard of a keeper: Saint Thallow, Aumbry, Merrow, Weyla, the Warden's Vow, or the Lantern-Man", "who_can_learn": "anyone a keeper accepts (05's default kept)", "regional_requires": "a keeper's acceptance: standing Neutral or better with the keeper's faith, or an oath"},
        "deed.primal": {"words": "the living voice of the land and its spirits, which the Hush stilled and which returns behind the Hem", "who_can_learn": "anyone a place or spirit accepts (05's default kept)", "regional_requires": "acceptance by a place: one of the places of acceptance (13.5.6)"},
    },
    "item_3_keepers": [k["id"] for k in KEEPERS],
    "item_4_places_of_power": "resonance on places (data: places[].resonance); consecrated / tended / desecrated / dead_ground / hushed facts on places (13.6.6)",
    "item_5_spirit_frequency": {"default": "Unlikely in any given place", "resonance": "Likely at a place with resonance", "forest_or_fen": "Even in the Rookwood, the Gloaming and the Sallow Fen (the spirits held the Hush back there)", "hushed": "Impossible on hushed ground (ci.spirits_in_the_hush)", "truth_T3": "13.1.5 options B/C change these odds"},
    "item_6_lawfulness": "canon.magic_lawful",
    "item_7_components_teachers_texts": "13.3.7 (components by price band; teachers and texts per settlement in places[].settlement.teachers and .texts)",
    "item_8_schools": {"closed": [], "opened": [], "notes": "No school is closed. deed.arcane.necromancy.raising and deed.divine.pact write conduct evidence when used on the unwilling (05's default kept). Necromancy that raises the dead is a crime in Vantry lands (canon.magic_lawful). In hushed ground every arcane and divine working is impossible (no speech); primal workings of the elements and growth work where their source is present; deed.primal.spirits workings fail there (no spirits)."},
}

COMPONENTS = [
    # 13.3.7: regional names for 05's rite components, by 08's price band
    {"band": 1, "name": "bell-dust", "what": "filings from a cracked Orrowan bell, sold by the pinch at Pell's yard", "stands_for": "silver dust or thread; chalk, salt and iron filings (warding and sealing rites)"},
    {"band": 1, "name": "Wend water from the Ford-garden", "what": "river water drawn at Weyla's ford in Tolling", "stands_for": "running or blessed water (purification, lift curse)"},
    {"band": 1, "name": "hearth-ash", "what": "ash from a hearth that has not gone out in a year", "stands_for": "the keeper's customary offering (Aumbry)"},
    {"band": 2, "name": "Thallow's oil", "what": "lamp oil blessed at the Last Bell", "stands_for": "water, salt or oil blessed at a shrine of the keeper (consecrate ground)"},
    {"band": 2, "name": "moss from a Stilled", "what": "lichen grown on one of the Stilled for forty years; the hedge-wise say it holds the Hush", "stands_for": "a thing the land would miss; a token of the cursed (hexcraft)"},
    {"band": 3, "name": "ringsilver", "what": "the pale metal of the Eastholt deeps that remembers sound; one ingot casts a handbell", "stands_for": "a material that gates a property (imbue); a gift the land would miss (call rain)"},
]

# ----------------------------------------------------------------------------------------------- tongues
TONGUES = [
    {"license": "lic.lang.common", "region_name": "Plain speech (the Common tongue)", "who": "everyone in the March; the tongue of Esterlow and of Orrow's markets", "note": "02's entry stands; the region renames it in narration only"},
    {"license": "lic.lang.orrowan", "region_name": "Orrowan, the bell-tongue", "who": "the Woken; old folk of the border villages; the Bellwardens' offices; every inscription in the vale", "note": "the region's second tongue (02.2.2 default): owner-block entry in data/contrib/licenses.13.yaml"},
    {"license": "lic.lang.old_tongue", "region_name": "the Deep Tongue", "who": "no one living; carved in the lowest vaults of Sael and the Ringsilver Deeps, older than Orrow", "note": "02's Old Tongue, renamed in narration; dead, at most accented"},
    {"license": "lic.lang.elvish", "region_name": "Elvish (the Lingerers' speech)", "who": "the elves of Hollin Hall in the Gloaming", "note": ""},
    {"license": "lic.lang.dwarvish", "region_name": "Dwarvish (Gorrund-tongue)", "who": "Clan Gorrund of the Eastholt", "note": ""},
    {"license": "lic.lang.goblin", "region_name": "Goblin (Tinkettle chatter)", "who": "the Tinkettle goblins of the Rookwood", "note": ""},
    {"license": "lic.lang.orcish", "region_name": "Orcish", "who": "Clan Ruvag of the Greyfells; orc-kin sell-swords", "note": ""},
    {"license": "lic.lang.giantish", "region_name": "Giantish", "who": "the hill giants and ogre-blooded drovers of the Greyfells", "note": ""},
    {"license": "lic.lang.kinspeech", "region_name": "Kin-speech (reed-talk)", "who": "the reedfolk of the Sallow Fen", "note": ""},
    {"license": "lic.lang.cant", "region_name": "the Cant (cellar-talk)", "who": "the Cellar Kin and the smugglers of the Wend", "note": ""},
]
SECOND_TONGUE = "lic.lang.orrowan"

ORROWAN_LICENSE = {
    "id": "lic.lang.orrowan", "name": "Orrowan, the bell-tongue", "kind": "language",
    "tags": ["deed.lore.languages"],
    "principle": "Speak and understand Orrowan, the tongue of the old kingdom of Orrow.",
    "scope": "Talk, listen and (with lic.lang.letters) read and write Orrowan, to the extent of the grade held. Spoken natively by the Woken and by the oldest folk of the border villages; sung in the Bellwardens' offices; carved and painted on every ruin of the vale.",
    "excludes": [{"what": "reading or writing it without lic.lang.letters", "needs": "lic.lang.letters"},
                 {"what": "any other tongue", "needs": "that tongue's own lic.lang.* license"},
                 {"what": "the Deep Tongue of Sael's lowest vaults", "needs": "lic.lang.old_tongue"}],
    "grades": [
        {"grade": "broken", "scope": "needs, directions, prices, warnings and other simple concrete matters; every Talk in it holds a Precision snag and its reach is capped at Limited"},
        {"grade": "accented", "scope": "everyday speech with no snag; you are plainly not of Orrow; subtle, technical or courtly matters hold a Precision snag"},
        {"grade": "native", "scope": "everything a native speaker can say or catch, including the bell-offices, old law and courtly forms"}],
    "attribute": "by_method",
    "crude_fallback": {"verb": "verb.talk", "method": "gesture, tone and the many nouns Orrowan shares with Plain speech (bell, field, kin, bread, the keepers' names)", "dc_shift": 5, "reach_cap": "limited", "consequence": None,
                       "reading": "an Orrowan inscription without the license yields numerals, seals, the bell-sign and the keepers' names only"},
    "stretch": None, "emulate": None,
    "effects": [
        {"effect_id": "eff.06.grant_snag", "params": {"type": "precision", "sign": "snag", "to": "the bearer", "fact": "speaks Orrowan brokenly", "applies_when": "a Talk beat is spoken in this tongue and the grade held is broken", "duration": "permanent"}},
        {"effect_id": "eff.reach_step", "params": {"ladder": "reach", "steps": -1, "applies_when": "a Talk beat is spoken in this tongue, the grade held is broken, and the framed reach is above Limited"}},
        {"effect_id": "eff.06.grant_snag", "params": {"type": "precision", "sign": "snag", "to": "the bearer", "fact": "speaks Orrowan as a foreigner", "applies_when": "a Talk beat is spoken in this tongue, the grade held is accented, and the matter is subtle, technical or courtly (a fact on the scene or the NPC)", "duration": "permanent"}}],
    "acquisition_paths": [
        {"type": "origin", "detail": "granted by the Woken upbringing (orig.up.woken) at accented, or bought with a learning pick (02.5.6)", "clock": None, "requires": None},
        {"type": "mentor", "detail": "clk.learn_tongue (8 segments, project, public): a week living among Woken in Tolling's Waking House or in Harrowby ticks 2; a week with a teacher (a Bellwarden, a Woken) or a text (needs lic.lang.letters) ticks 1", "clock": "clk.learn_tongue", "requires": "speakers to live among, or a teacher who holds it at accented or better"},
        {"type": "project", "detail": "a week of study from the Bellwardens' psalter or an Orrowan primer from the Lamplit Library ticks 1", "clock": "clk.learn_tongue", "requires": "lic.lang.letters and such a text"}],
    "source": "data", "lifecycle": "provisional",
    "basis": ["02.4.6", "00.12.1", "01.18 (Talk: a language not held)", "13.5.3", "DL-13-08"],
    "notes": "The region's second tongue (02.2.2's default tongue pick)."}

# ----------------------------------------------------------------------------------------------- peoples
PEOPLES = [
    {"origin": "orig.people.human", "present": "common", "who": "Lowlanders of Esterlow (settlers, the Margravine's folk, most of Tolling) and Orrowans (the Woken, and border families who were outside the vale on Hush-eve)", "where": ["loc.tolling", "loc.harrowby", "loc.vantry_keep", "loc.bellhollow"], "name_tables": ["tbl.thallen.names.lowlander", "tbl.thallen.names.orrowan"], "faiths": ["keeper.aumbry", "keeper.merrow", "keeper.thallow", "keeper.weyla"]},
    {"origin": "orig.people.halfling", "present": "common", "who": "the Wend-folk: river farmers, millers and bargees of Copsey and Tolling's water-stairs, who came up the Wend with the first settlers", "where": ["loc.copsey", "loc.tolling"], "name_tables": ["tbl.thallen.names.halfling"], "faiths": ["keeper.aumbry", "keeper.weyla"]},
    {"origin": "orig.people.dwarf", "present": "uncommon", "who": "Clan Gorrund of the Eastholt: miners and bell-founders, the only people who still cast in the old Orrowan alloy", "where": ["loc.gorrund_delve", "loc.tolling"], "name_tables": ["tbl.thallen.names.dwarf"], "faiths": ["keeper.thallow", "keeper.merrow"]},
    {"origin": "orig.people.elf", "present": "rare", "who": "the Lingerers of Hollin Hall in the Gloaming: a dwindling elf-house that remembers Orrow before the Hush; the Hush stopped at their forest's edge", "where": ["loc.hollin_hall"], "name_tables": ["tbl.thallen.names.elf"], "faiths": []},
    {"origin": "orig.people.goblin_kin", "present": "uncommon", "who": "the Tinkettle goblins, who moved into the empty Rookwood during the Hush and now trade, tinker and salvage; a few work in Tolling", "where": ["loc.tinkettle", "loc.tolling"], "name_tables": ["tbl.thallen.names.goblin"], "faiths": ["keeper.lantern_man"]},
    {"origin": "orig.people.orc_kin", "present": "uncommon", "who": "Clan Ruvag of the Greyfells, raiders and drovers; orc-kin sell-swords in the Red Lanterns", "where": ["loc.greyfells", "loc.tolling"], "name_tables": ["tbl.thallen.names.orc"], "faiths": []},
    {"origin": "orig.people.giant_kin", "present": "rare", "who": "ogre-blooded drovers of the high pastures, and the hill giants of the Greyfells", "where": ["loc.eastholt", "loc.greyfells"], "name_tables": ["tbl.thallen.names.giant"], "faiths": []},
    {"origin": "orig.people.beastfolk", "present": "rare", "who": "the reedfolk of the Sallow Fen (lizard-kin), who trade eels and reed-cloth at Reedmere and keep apart", "where": ["loc.reedmere"], "name_tables": ["tbl.thallen.names.reedfolk"], "faiths": ["keeper.lantern_man"]},
]

# ----------------------------------------------------------------------------------------------- names (d20 each)
NAME_TABLES = {
    "tbl.thallen.names.lowlander": {
        "given": ["Abel", "Bertram", "Cob", "Dunstan", "Edda", "Fenna", "Gilly", "Hester", "Ivo", "Joss", "Kit", "Lettice", "Mabry", "Ned", "Oswin", "Prue", "Rafe", "Sibbe", "Tamsin", "Wat"],
        "family": ["Cask", "Tenney", "Marlow", "Hask", "Brede", "Cotter", "Wollin", "Tenpenny", "Rush", "Hollis", "Fairweather", "Stane", "Underby", "Cropper", "Mallin", "Ashby", "Thurrock", "Pell", "Wainwright", "Copley"]},
    "tbl.thallen.names.orrowan": {
        "given": ["Aude", "Belis", "Caddow", "Danae", "Eluned", "Faro", "Gwennor", "Hollin", "Isse", "Jory", "Kessa", "Lioren", "Merrin", "Orsolin", "Pellam", "Rhosyn", "Saelan", "Tobin", "Ysmay", "Wenna"],
        "family": ["Tollard", "Vey", "Chime", "Ringwood", "of the Mere", "Peal", "Canter", "Reave", "Halloway", "Bellweather", "of Caddow", "Strickhallow", "Mereling", "Fell", "Clapperton", "Ashpeal", "Quillon", "of Harrowby", "Lamplight", "Rook"]},
    "tbl.thallen.names.halfling": {
        "given": ["Dabble", "Tib", "Dosie", "Hobb", "Nettie", "Pipkin", "Rue", "Sorrel", "Bramwell", "Clover", "Dace", "Elm", "Fidge", "Gossam", "Holly", "Lark", "Mopsy", "Perrin", "Quill", "Tansy"],
        "family": ["Wollin", "Thistledown", "Brookbottom", "Mudlark", "Eelpie", "Kettlesby", "Underhay", "Ferryweather", "Reedmouth", "Applegate", "Barleycorn", "Coppins", "Dimble", "Furrow", "Gudgeon", "Mossbank", "Puddifoot", "Rushlight", "Sallowby", "Weirfield"]},
    "tbl.thallen.names.dwarf": {
        "given": ["Brekka", "Durn", "Haldra", "Orla", "Torvik", "Brunn", "Gessa", "Hrolla", "Ketil", "Marta", "Ondur", "Rask", "Sigra", "Thane", "Ulfa", "Vorn", "Ysolt", "Ama", "Dagny", "Grim"],
        "family": ["Gorrund", "Ironwick", "Bellmaw", "Coppergrip", "Deepsong", "Anvilheart", "Tinsmelt", "Hammerfall", "Orefinder", "Stonepeal", "Brazenhand", "Cindermoor", "Delvebright", "Forgeborn", "Graniteson", "Knellwright", "Moltmark", "Ringforge", "Slagbrow", "Tuyere"]},
    "tbl.thallen.names.elf": {
        "given": ["Ithren", "Lisanne", "Orveth", "Caelar", "Ymmeline", "Aelis", "Corrin", "Elowyn", "Faen", "Ilvar", "Lethe", "Mireth", "Neris", "Olwe", "Persil", "Rhiel", "Sennet", "Thessaly", "Ulmar", "Vireth"],
        "family": ["of Hollin Hall", "Gloamwalker", "Leafsinger", "the Lingering", "Mossfall", "Stillbrook", "Thornward", "Duskmantle", "Greenwell", "Hollinsong", "Nightbloom", "Oakshade", "Rainmere", "Silverfern", "Starwater", "Twilleaf", "Underbough", "Wildwhisper", "Yewheart", "Ashveil"]},
    "tbl.thallen.names.goblin": {
        "given": ["Nackle", "Grizzle", "Spurt", "Tinbelly", "Gobbet", "Rattle", "Snib", "Pudge", "Wicket", "Fizzwick", "Kettle", "Bodge", "Clink", "Dross", "Gimlet", "Hob", "Jiggle", "Nub", "Scrimp", "Twitch"],
        "family": ["Tinkettle", "Rustpot", "Copperspout", "Nailbiter", "Ragbag", "Lidrattle", "Soldersnout", "Grubwhistle", "Hinge", "Spannerkin", "Junkjoy", "Burrfoot", "Clatterby", "Dentpan", "Flintlick", "Gearnose", "Knobble", "Pottlecrack", "Scrapwhit", "Tackhammer"]},
    "tbl.thallen.names.orc": {
        "given": ["Ruvag", "Ghessa", "Durkha", "Mog", "Arza", "Brul", "Grasha", "Hruk", "Izgra", "Krom", "Lugdra", "Morza", "Nargul", "Oshra", "Shagra", "Torg", "Urzha", "Vrass", "Yagga", "Zurn"],
        "family": ["of Clan Ruvag", "Greyfell", "Ironjaw", "Stonehide", "Two-Axe", "Bloodbrow", "Cliffborn", "Cragmaw", "Dusktusk", "Fellhand", "Goremane", "Hillbreaker", "Longstride", "Redbelt", "Scarback", "Skullbearer", "Thunderhoof", "Warcry", "Windeater", "Wolfbane"]},
    "tbl.thallen.names.giant": {
        "given": ["Grummel", "Tarrow", "Big Moss", "Hobbe", "Old Ma Clodd", "Bulder", "Crag", "Dunmoor", "Eldra", "Fennig", "Gorp", "Hulda", "Ivar", "Jotta", "Krann", "Lumm", "Murk", "Oddo", "Rimm", "Stumpa"],
        "family": ["the Drover", "of the High Fold", "Stonecarrier", "Fellstride", "Barrowback", "Cloudhead", "Deepboots", "Elmbreaker", "Fogbeard", "Gravelgut", "Hillsit", "Knucklebone", "Longreach", "Mossback", "Oakshoulder", "Peatfoot", "Rockjaw", "Shepherd", "Thunderbelly", "Wallhand"]},
    "tbl.thallen.names.reedfolk": {
        "given": ["Ssessa", "Thrask", "Kessik", "Oolu", "Reshh", "Tzissa", "Ikkar", "Mossol", "Ulath", "Vresh", "Hasska", "Isslo", "Korr", "Lisska", "Nesh", "Phith", "Sarrak", "Tolu", "Whisk", "Yeshil"],
        "family": ["Reed-in-Water", "Two-Tides", "Eel-Taker", "Green-Back", "Still-Pool", "Old-Scale", "Mud-Sleeper", "Fen-Watcher", "Long-Tail", "Bright-Eye", "Sun-Basker", "Rain-Caller", "Frog-Catcher", "Mist-Walker", "Root-Finder", "Silt-Treader", "Cold-Blood", "Low-Song", "Deep-Ford", "Grey-Mere"]},
}

# ----------------------------------------------------------------------------------------------- regional NPC tables (replace 12's generic ones)
NPC_ROLE = ["farmer of the Brightfields", "Woken, newly out of the Hem", "salvager (a Hemrunner)", "bargee or boatman on the Wend",
            "Bellwarden novice", "Pell & Daughters crew-hand", "Vantry outrider or tithe-man", "drover", "charcoal-burner of the Rookwood",
            "goblin tinker", "dwarf founder or miner", "halfling miller or eel-catcher", "hedge-wise woman or man", "fordwarden (grave-keeper)",
            "pilgrim come to hear the Last Bell", "peddler", "innkeeper or alewife", "smith", "child", "elder who remembers the year the bells stopped"]
NPC_DETAIL = ["moss stains on old-fashioned clothes (Woken)", "a handbell on the belt", "wool stuffed in the ears 'against the quiet'",
              "a Pell & Daughters badge of a lantern and a pick", "an Orrowan coin pierced and worn on a thong", "hands green with bell-bronze",
              "a Vantry tithe-tally on a cord", "a ford-stone at the throat", "an iron hearth-key on a cord", "goblin-made spectacles",
              "a burn scar from the foundry", "speaks a little too loudly, always", "a dog that never leaves their side",
              "forty years out of fashion, and knows it", "a sprig of Rookwood holly in the hat", "salvage-scarred knuckles",
              "a lowlander's accent, softened by years here", "an old Bellwarden's lantern, unlit", "keeps glancing north", "hums under their breath, constantly"]
NPC_REFUSAL_REGIONAL = ["will not go past the Hem-cairns", "will not stay where they cannot hear a bell", "will not deal with the Woken",
                        "will not cross the Margravine", "will not sell anything taken from a grave", "will not let a bell be touched by strangers"]
OMENS = ["a bell somewhere misses a stroke", "birds fall silent mid-song", "a ring of quiet around a standing stone",
         "frost in the shape of a bell on a window", "a dog that will not bark", "a Stilled in a far field has turned its head",
         "the river runs without a sound for a breath", "every candle in the room bends north", "a child humming an Orrowan lullaby no one taught it",
         "a lantern-light in the fen where no one walks", "moss on a fresh-cut stone", "the Last Bell sounds thin, as if from far away"]
FURNISHINGS = ["a cracked Orrowan bell used as a planter", "a Hem-cairn stone set in the hearth for luck", "a hearth-key over the fire",
               "a salvaged bronze lamp, polished bright", "a Pell & Daughters price-board", "a shelf of moss-grown crockery from the Hem",
               "a handbell by the door 'in case'", "an Orrowan tapestry, half rotted", "a Vantry charter-notice nailed up", "goblin-made clockwork that does nothing useful",
               "wool and wax for the ears in a bowl by the door", "a ford-stone hung over the cradle"]

# ----------------------------------------------------------------------------------------------- calendar (owner-block "13")
CALENDAR = {
    "seasons": [{"id": "spring", "name": "Thawing"}, {"id": "summer", "name": "High Summer"}, {"id": "autumn", "name": "Tithing"}, {"id": "winter", "name": "the Long Dark"}],
    "quarter_days": [
        {"id": "quarter.spring", "name": "Ringing Day", "note": "the year's first day; the Last Bell's great peal at dawn; market, sitting and hiring fair"},
        {"id": "quarter.summer", "name": "Longday Fair", "note": "market, sitting, the Longday truce"},
        {"id": "quarter.autumn", "name": "Tithe Day", "note": "market, sitting, hiring fair; the Margravine's tithe falls due"},
        {"id": "quarter.winter", "name": "Hush-eve", "note": "the anniversary of the Hush; every bell in the March is rung all night (the Long Peal)"}],
    "months": [
        {"id": "month.1", "name": "Rimewane"}, {"id": "month.2", "name": "Furrowtide"}, {"id": "month.3", "name": "Blossomfall"},
        {"id": "month.4", "name": "Haysel"}, {"id": "month.5", "name": "Highsun"}, {"id": "month.6", "name": "Reaping"},
        {"id": "month.7", "name": "Gleaning"}, {"id": "month.8", "name": "Russet"}, {"id": "month.9", "name": "Emberfall"},
        {"id": "month.10", "name": "Deepcold"}, {"id": "month.11", "name": "Wolfmonth"}, {"id": "month.12", "name": "Thawhope"}],
    "day_names": ["Dawnday", "Hearthday", "Weighday", "Fordsday", "Toilday", "Marketday", "Bellday"],
    "era": {"name": "since the Hush (S.H.)", "year_one": "the spring quarter day after Hush-eve", "opening_date": "Ringing Day (spring quarter day), year 42 S.H., dawn watch"},
    "festivals": [
        {"id": "fest.quarter_spring", "name": "Ringing Day", "season": "spring", "week": 1, "day": 1, "effects": ["fx.market", "fx.sitting", "fx.hiring_fair"]},
        {"id": "fest.quarter_summer", "name": "Longday Fair", "season": "summer", "week": 1, "day": 1, "effects": ["fx.market", "fx.sitting", "fx.truce"]},
        {"id": "fest.quarter_autumn", "name": "Tithe Day", "season": "autumn", "week": 1, "day": 1, "effects": ["fx.market", "fx.sitting", "fx.hiring_fair"]},
        {"id": "fest.quarter_winter", "name": "Hush-eve (the Long Peal)", "season": "winter", "week": 1, "day": 1, "effects": ["fx.market", "fx.sitting", "fx.rumor_surge", "fx.rite_day"], "rite_school": "deed.divine.warding"},
        {"id": "fest.thallen.waking_day", "name": "Waking Day", "season": "spring", "week": 6, "day": 7, "effects": ["fx.rumor_surge"], "note": "the Wakeful's feast for the year's Woken, at the Waking House"},
        {"id": "fest.thallen.fordwake", "name": "Fordwake", "season": "autumn", "week": 13, "day": 4, "effects": ["fx.rite_day"], "rite_school": "deed.divine.rites", "note": "Weyla's night: lamps floated down the Wend for the year's dead and for the Stilled"},
        {"id": "fest.thallen.founders_pour", "name": "Founders' Pour", "season": "summer", "week": 9, "day": 6, "effects": ["fx.market"], "note": "Clan Gorrund pours its year's bells at the Delve; the one day outsiders are welcome in the foundry"}],
}

LIFESPANS = [
    {"tag": "creature.folk.human", "aging_from": 50, "note": "a Woken's age counts only waking years (canon.woken)"},
    {"tag": "creature.folk.halfling", "aging_from": 50, "note": ""},
    {"tag": "creature.folk.dwarf", "aging_from": 120, "note": ""},
    {"tag": "creature.folk.elf", "aging_from": 300, "note": "the Lingerers say the Hush aged them; no rule follows"},
    {"tag": "creature.folk.goblin", "aging_from": 35, "note": ""},
    {"tag": "creature.folk.orc", "aging_from": 35, "note": ""},
    {"tag": "creature.folk.giant", "aging_from": 80, "note": ""},
    {"tag": "creature.folk.beastfolk", "aging_from": 50, "note": "reedfolk"},
]

# 11.7.6: the region scope's values (valence for region-scope reputation); settlements name their own
REGION_VALUES = [{"axis": "conduct.courage", "pole": "+"}, {"axis": "conduct.protection", "pole": "+"},
                 {"axis": "conduct.generosity", "pole": "+"}, {"axis": "conduct.piety", "pole": "-", "despised": True}]
REGION_VALUES_TEXT = ("The March admires those who walk toward the silence for someone else's sake, who share what they bring back, "
                      "and who keep their bells; it despises grave-robbers of the tended dead, bell-breakers and those who leave a neighbor "
                      "standing in the Hush.")

HIRE_QUIRKS = [  # d12, regional replacement for tbl.16.hire_quirk
    "Woken: forty years out of date and wants to see everything",
    "has walked the Hem and come back, and will not say what they saw",
    "carries a handbell and rings it at every crossroads",
    "afraid of quiet: talks to fill every silence",
    "wants a claim of their own past the Brightfields",
    "a Vantry deserter: someone will come asking",
    "knows the country: one route link known (a lever on way-finding there)",
    "devout to Weyla: will not leave the dead unburied",
    "owes Pell & Daughters money",
    "a goblin of the Tinkettle clan: sharp with tools, sharper with prices",
    "kin stilled in the Hem: will go anywhere that might wake them",
    "a drinker: steady until there is drink"]
