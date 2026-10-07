# 13_data_tables.py -- the March's regional tables: local events (10's V face), seasonal events and hooks (11),
# rumors with sealed truth and points_to (11.6), chase ground (06.12), site generation and generated-area terrain
# (10.1.8, 10.13.2), plus storied items (08.4.8) and the region's rare metal. Read by 13-gen_region.py.

def fx(eid, **params):
    return {"effect_id": eid, "params": params}

# 10.9.4 V face / 11's tbl.11.local_events replaced for the region
EVENTS = {"id": "tbl.thallen.events", "name": "Local events in the Thallen March", "die": "d12", "replaces": "tbl.11.local_events", "results": [
    {"range": "1", "result": "a traveller with the newest news of the region (11.6.6)"},
    {"range": "2", "result": "a faction's people pass on its business (a full faction, by list weight): Vantry outriders, a Pell crew, Bellwardens with handbells, or (sealed) Choir singers humming"},
    {"range": "3", "result": "a sign of a situation's next step (its trace, 11.6.2)"},
    {"range": "4", "result": "a rumor told around a fire (tbl.thallen.rumors)"},
    {"range": "5", "result": "an omen of a hidden clock (no tick; a repeat of its last omen)"},
    {"range": "6", "result": "the distant toll of the Last Bell carries further than it should; for an hour every Stilled in sight seems about to turn its head", "writes": []},
    {"range": "7", "result": "someone in trouble (a hook: tbl.11.hook.thallen)"},
    {"range": "8", "result": "the weather turns (10's shift table)"},
    {"range": "9", "result": "a newly Woken stumbles out of the north, forty years late (a recurring NPC; a hook of kind npc)"},
    {"range": "10", "result": "a hush-pool has moved in the night: a place the PC knows now carries haz.thallen.hush_pool for a week (a written world change)",
     "writes": [fx("eff.write_fact", subject="the nearest discovered place in ring 2 or 3", predicate="hazard", value="haz.thallen.hush_pool until a week passes or a true bell is rung there for a watch")]},
    {"range": "11", "result": "salvagers with a find they cannot carry and will share for help (an opportunity)"},
    {"range": "12", "result": "a lantern-light that walks (the Lantern-Man's, in the west; elsewhere a fen-light far from home)"}]}

SEASON_EVENTS = {
    "spring": {"id": "tbl.11.season_events.thallen.spring", "die": "d12", "replaces": "tbl.11.season_events.spring", "results": [
        {"range": "1-4", "event": "the Hem's spring ebb", "result": "the Hem retreats: one ring-3 place nearest the Hem-cairns loses its hush-pool; d6 of its Stilled: on a 1 one wakes (13.1.5 T2); the Bellwardens raise a new cairn line; Woken arrive in Tolling",
         "writes": [fx("eff.write_fact", subject="loc.the_hem", predicate="ebb_this_spring", value=True), fx("eff.11.seed_hook", text="Woken out of the Hem looking for homes the Margravine has chartered", source="season", entities=["fac.thallen.wakeful", "fac.thallen.vantry"], delivery="rumor")]},
        {"range": "5", "phenomenon": "ph.late_frost"},
        {"range": "6", "phenomenon": "ph.pilgrimage", "note": "pilgrims to the Last Bell on Ringing Day"},
        {"range": "7", "situation": "sit_t.feud", "note": "a Woken claimant and a lowland tenant over a Brightfields farm"},
        {"range": "8", "situation": "sit_t.flood_and_fire", "note": "the Wend in spate"},
        {"range": "9-12", "result": "nothing remarkable"}]},
    "summer": {"id": "tbl.11.season_events.thallen.summer", "die": "d12", "replaces": "tbl.11.season_events.summer", "results": [
        {"range": "1-2", "phenomenon": "ph.bandit_summer", "note": "the Hemrats and their imitators on the downs track"},
        {"range": "3", "phenomenon": "ph.drought"},
        {"range": "4", "situation": "sit_t.hunting_ground", "note": "hush-hounds come down to the Brightfields flocks"},
        {"range": "5", "situation": "sit_t.road_of_knives", "note": "a salvage rush to a new find in the Hem"},
        {"range": "6", "situation": "sit_t.festival_trouble", "note": "Longday Fair at Tolling"},
        {"range": "7", "phenomenon": "ph.comet_year", "note": "the Choir calls it a sign"},
        {"range": "8-12", "result": "nothing remarkable"}]},
    "autumn": {"id": "tbl.11.season_events.thallen.autumn", "die": "d12", "replaces": "tbl.11.season_events.autumn", "results": [
        {"range": "1-2", "phenomenon": "ph.good_harvest"},
        {"range": "3", "phenomenon": "ph.cattle_sickness"},
        {"range": "4", "phenomenon": "ph.war_levy", "note": "the Margravine raises her levy; Tolling's young men called to Vantry Keep"},
        {"range": "5", "situation": "sit_t.hunger", "note": "the Waking House overfull before winter"},
        {"range": "6", "situation": "sit_t.the_rite", "note": "the Choir at Copple Field"},
        {"range": "7", "situation": "sit_t.war_comes", "note": "Clan Ruvag comes down into the Eastholt for the winter grazing"},
        {"range": "8-12", "result": "nothing remarkable"}]},
    "winter": {"id": "tbl.11.season_events.thallen.winter", "die": "d12", "replaces": "tbl.11.season_events.winter", "results": [
        {"range": "1-3", "phenomenon": "ph.hard_winter"},
        {"range": "4", "situation": "sit_t.sickness"},
        {"range": "5", "situation": "sit_t.the_missing", "note": "a child walks north in the snow toward the quiet"},
        {"range": "6", "situation": "sit_t.cursed_ground", "note": "a hush-pool forms on the Lowroad for the Long Dark"},
        {"range": "7", "result": "Hush-eve: every bell rung all night; if every Bellwarden bell rang (a fact), the Quiet's clock skips its next Year Turn tick",
         "writes": [fx("eff.write_fact", subject="clk.thallen.quiet_wakes", predicate="skip_next_year_tick", value=True)]},
        {"range": "8-12", "result": "nothing remarkable"}]},
}

HOOKS = {"id": "tbl.11.hook.thallen", "name": "Hooks in the Thallen March", "die": "d20", "replaces": "tbl.11.hook", "results": [
    {"range": "1", "seed": "a child of Harrowby has walked north into the Brightfields and not come home", "template": "sit_t.the_missing"},
    {"range": "2", "seed": "a bell rings under the Reedwend's water on still nights", "kind": "question"},
    {"range": "3", "seed": "Pell & Daughters pay double for an escort to the Hem-cairns", "kind": "quest"},
    {"range": "4", "seed": "smoke from the chimney of a stilled house at the Hem: someone is living among the Stilled", "kind": "question"},
    {"range": "5", "seed": "a Woken and a lowland tenant both hold a paper for the same farm", "template": "sit_t.feud"},
    {"range": "6", "seed": "a stranger in Orrowan clothes asks after the PC by name", "template": "sit_t.the_enemy"},
    {"range": "7", "seed": "sheep found lying unmarked and cold on the downs: the hush-hounds do not eat what they kill", "template": "sit_t.hunting_ground"},
    {"range": "8", "seed": "a wayside bell-post's handbell is gone and the Bellwarden who kept it is missing", "kind": "question"},
    {"range": "9", "seed": "a debtor begs help against Pell & Daughters, who never forgive a debt", "template": "sit_t.the_debt"},
    {"range": "10", "seed": "Hesper Pell will pay anyone who can bring her a true bell to the Chapel of the Ringer's porch", "kind": "quest"},
    {"range": "11", "seed": "Clan Gorrund will give a true handbell to whoever clears the Copper Delving", "kind": "quest"},
    {"range": "12", "seed": "the Lingerers have shut the Gloaming's paths and no one knows why", "kind": "question"},
    {"range": "13", "seed": "a Margravine's charter-clerk has vanished on the downs with the year's tithe-roll", "kind": "question"},
    {"range": "14", "seed": "Mother Sallow's crow has been seen in Copsey, asking for someone by name", "kind": "question"},
    {"range": "15", "seed": "the Tinkettle goblins want a go-between to sell to the Bridgemoot", "kind": "quest"},
    {"range": "16", "seed": "a Stilled knight in the Hem holds a letter in his fist addressed to someone alive in Tolling", "kind": "quest"},
    {"range": "17", "seed": "a cart of salvage arrived at Pell's yard with no crew", "kind": "question"},
    {"range": "18", "seed": "Ruvag's outriders have been seen on the Eastholt in spring, which they never do", "template": "sit_t.war_comes"},
    {"range": "19", "seed": "the Lamplit Library wants an Orrowan book from a named house in the Hem", "kind": "quest"},
    {"range": "20", "seed": "a Woken child of the Waking House talks in her sleep in the Deep Tongue", "kind": "question"}]}

RUMORS = {"id": "tbl.thallen.rumors", "name": "Rumors of the March", "die": "d20", "rule": "each rumor's truth is SEALED here at authoring (11.6.1); 11.6.3's distortion applies as it spreads", "results": [
    {"range": "1", "text": "The Last Bell is cracked, and the Prior knows it.", "truth": "true", "points_to": "sec.brede.crack"},
    {"range": "2", "text": "The Margravine has a letter from the crown: if the vale is not settled in three years, she loses it.", "truth": "true", "points_to": "sec.vantry.term"},
    {"range": "3", "text": "Mother Pell has found a road to Sael under the water.", "truth": "true", "points_to": "sec.pell.causeway (gate: Pell's trust at Friendly, her linchpin fate, or following her boats from Bellhollow: surveillance)"},
    {"range": "4", "text": "Lady Orsolin is no lady at all.", "truth": "true", "points_to": "case.orsolin_signet"},
    {"range": "5", "text": "The Woken are not people any more; something else woke up in them.", "truth": "false", "points_to": "the Waking House (Abel Marrow can show otherwise)"},
    {"range": "6", "text": "Ringsilver is just silver the dwarves lie about.", "truth": "false", "points_to": "loc.gorrund_delve"},
    {"range": "7", "text": "There's a hag in the fen who'll give you anything for a promise.", "truth": "partial", "points_to": "loc.sallow_hollow (she gives a great deal, and takes more)"},
    {"range": "8", "text": "Ashgorge sleeps on the tribute of a hundred years of Orrow.", "truth": "true", "points_to": "loc.ashgorge_lair"},
    {"range": "9", "text": "The Kingsbarrows have opened from the inside.", "truth": "true", "points_to": "loc.kingsbarrows"},
    {"range": "10", "text": "Someone in Tolling is buying bell-wright's files.", "truth": "true", "points_to": "clu.silent_bells.n2.p3 (Lark Mossbank)"},
    {"range": "11", "text": "A true bell rung at the Mere would wake the whole of Sael.", "truth": "partial", "points_to": "obj.mother_bell (only the Mother Bell, whole)"},
    {"range": "12", "text": "The goblins of the Rookwood steal children.", "truth": "false", "points_to": "loc.tinkettle"},
    {"range": "13", "text": "There was a treaty that gave the Woken their land, and the Margravine burned it.", "truth": "partial", "points_to": "case.treaty_of_the_ford (removed, not burned)"},
    {"range": "14", "text": "The Lingerers in the Gloaming were never stilled because they made a bargain with the Quiet.", "truth": "false", "points_to": "loc.hollin_hall (the Heart-tree held it back)"},
    {"range": "15", "text": "The Bell-Prior of Sael rang the silence on purpose.", "truth": "true", "points_to": "sec.brede.confession / sec.aude.why"},
    {"range": "16", "text": "The hush-hounds are led by a she-wolf as big as a pony.", "truth": "true", "points_to": "adv.thallen.hush_hound_alpha (the Standing Downs)"},
    {"range": "17", "text": "Clan Ruvag means to take the Eastholt this autumn.", "truth": "partial", "points_to": "fac.thallen.ruvag goal (the grazing, not the hold)"},
    {"range": "18", "text": "Bellhollow's tower bell is borrowed, and the Bellwardens want it back.", "truth": "true", "points_to": "loc.bellhollow"},
    {"range": "19", "text": "A bell-mage of Sael is still awake out there, ringing.", "truth": "true", "points_to": "adv.thallen.sael_bellmage"},
    {"range": "20", "text": "The Reeve takes a tenth of every smuggled cart.", "truth": "true", "points_to": "sec.hask.bribes"}]}

CHASE_GROUND = {"id": "tbl.thallen.chase_ground", "name": "Chase ground in the March", "die": "d6", "no_immediate_repeat": True, "replaces": "tbl.chase_ground",
    "tolling": [
        {"range": 1, "result": "the Wend Bridge, crowded with carts", "tier": "moderate"},
        {"range": 2, "result": "Saltgate Square's stalls and pens", "tier": "moderate"},
        {"range": 3, "result": "the bridge-house roofs over the river", "tier": "hard"},
        {"range": 4, "result": "the water-stairs down to the Wend", "tier": "moderate"},
        {"range": 5, "result": "an open lane by the Ford-garden wall", "tier": "easy"},
        {"range": 6, "result": "a dead end against the bell-tower close (only Exert, Sneak or Force)", "tier": "hard"}],
    "brightfields_downs": [
        {"range": 1, "result": "open plough or open down", "tier": "easy"},
        {"range": 2, "result": "a hedge to break through", "tier": "moderate"},
        {"range": 3, "result": "a ditch or a stream", "tier": "moderate"},
        {"range": 4, "result": "a field of the Stilled to weave through", "tier": "moderate"},
        {"range": 5, "result": "the edge of a hush-pool: through it in silence, or round it", "tier": "hard"},
        {"range": 6, "result": "a chalk scarp in poor light", "tier": "hard"}],
    "fen_reedwend": [
        {"range": 1, "result": "a stake-path", "tier": "easy"},
        {"range": 2, "result": "reeds over your head", "tier": "moderate"},
        {"range": 3, "result": "a channel to wade or leap", "tier": "moderate"},
        {"range": 4, "result": "a mire (haz.mire)", "tier": "hard"},
        {"range": 5, "result": "a punt to seize and pole", "tier": "moderate"},
        {"range": 6, "result": "black water and fen-lights", "tier": "hard"}]}

SITE_TABLE = {"id": "tbl.thallen.sites", "name": "Sites generated in the March", "die": "d12", "replaces": "sites.yaml#site_generation", "by_ring": {
    "1": [["site.theme.infested", "site.domain.crypt"], ["site.theme.ravaged", "site.domain.underkeep"], ["site.theme.ancient", "site.domain.barrow"]],
    "2": [["site.theme.ancient", "site.domain.barrow"], ["site.theme.ravaged", "site.domain.underkeep"], ["site.theme.infested", "site.domain.mine"], ["site.theme.haunted", "site.domain.crypt"], ["site.theme.fortified", "site.domain.warren"], ["site.theme.wild", "site.domain.tanglewood"]],
    "3": [["site.theme.haunted", "site.domain.stronghold"], ["site.theme.hallowed", "site.domain.temple"], ["site.theme.ancient", "site.domain.tower"], ["site.theme.corrupted", "site.domain.fen"], ["site.theme.wild", "site.domain.tanglewood"], ["site.theme.haunted", "site.domain.crypt"]],
    "4": [["site.theme.haunted", "site.domain.crypt"], ["site.theme.ancient", "site.domain.underkeep"], ["site.theme.ancient", "site.domain.tower"], ["site.theme.wild", "site.domain.cavern"], ["site.theme.haunted", "site.domain.stronghold"]],
    "5": [["site.theme.ancient", "site.domain.underkeep"], ["site.theme.ancient", "site.domain.flooded_cave"], ["site.theme.ravaged", "site.domain.cavern"]]},
    "rule": "roll d12 and take the row (d12 - 1) mod the ring's list length + 1; size by 10.13.3's table (ring 1-2 small or medium, 3 medium or large, 4-5 large or vast: d6 1-3 the smaller); band = the area's home band; every site at ring 3+ in the vale proper (the Hem, the Quietlands, the Mere) also carries haz.thallen.hush_pool in d3 of its areas (ring 3) or haz.thallen.deep_hush throughout (rings 4-5)"}

TERRAIN_BY_RING = {"1": ["terrain.plains.farmland", "terrain.forest.woodland", "terrain.water.river"],
                   "2": ["terrain.plains.moor", "terrain.plains.grassland", "terrain.forest.woodland", "terrain.highland.hills", "terrain.wetland.marsh"],
                   "3": ["terrain.plains.moor", "terrain.forest.deepwood", "terrain.wetland.fen", "terrain.ruin"],
                   "4": ["terrain.plains.grassland", "terrain.ruin", "terrain.highland.mountains"],
                   "5": ["terrain.water.lake", "terrain.highland.mountains.peak", "terrain.ruin"]}

RARE_METAL = {"name": "ringsilver", "tag": "material.metal.rare", "what": "a pale, faintly singing metal found only in the Ringsilver Deeps below the Eastholt; alloyed one part in nine into bell-bronze it makes a true bell (canon.true_bell)",
              "price": {"ingot": 120, "band": 3}, "where": ["loc.ringsilver_deeps (the last open lode)", "loc.gorrund_delve (one ingot a season, if any)", "salvage: Orrowan true bells, recast"],
              "crafting": "a true handbell is a crafting project (08.6) of band 3 by a smith who holds lic.training.craft_smithing at expert and knows the old alloy (Clan Gorrund teaches it at Friendly); a great bell is a great project (11.9.7)"}

# 08.4.8: storied items (rung 6), authored as fixed property sets with tiers
STORIED = [
    {"id": "item.thallows_handbell", "name": "Thallow's Handbell (the Ringer's Own)", "base": "bi.holy_symbol", "quality": "storied",
     "signature": {"prop_id": "prop.conduit_divine", "tier": 1}, "properties": [{"prop_id": "prop.conduit_divine_thrift", "tier": 1}, {"prop_id": "prop.glowing", "tier": 1}],
     "facts": {"true_bell": True, "peal": "opens hushed ground within band.distant while rung (one ring further than any other true bell)", "keeper_sign": "keeper.thallow"},
     "where": "loc.chapel_of_the_ringer (objective)", "price": 4000,
     "story": "the handbell Saint Thallow rang over the first sleep of the Quiet; Orrow's Bell-Priors carried it at the great offices; left on the chapel altar the night the Hem came"},
    {"id": "item.clapperfall", "name": "Clapperfall", "base": "bi.war_hammer", "quality": "storied",
     "signature": {"prop_id": "prop.bane_undead", "tier": 2}, "properties": [{"prop_id": "prop.onhit_stagger", "tier": 2}],
     "facts": {"true_bell": True, "peal": "each hit rings true: hushed ground within band.close opens for the round", "made_from": "the iron of the Mother Bell's broken clapper"},
     "where": "loc.kingsbarrows (held by adv.thallen.barrow_king)", "price": 5000,
     "story": "forged by Orrow's last war-king from the clapper that broke when the Mother Bell cracked; he was buried with it, and rose with it"},
    {"id": "item.signet_of_orrow", "name": "The Signet of Orrow (the Vey ring)", "base": "bi.signet", "quality": "storied",
     "signature": {"prop_id": "prop.commanding", "tier": 1}, "properties": [{"prop_id": "prop.fine_cut", "tier": 1}],
     "facts": {"heraldry": "the bell-and-crown of Orrow's royal cousins", "claim": "carried by the Wakeful's leader as proof of blood"},
     "where": "on npc.orsolin_vey's thumb", "price": 3500,
     "story": "the seal of Orrow's royal cousins; its proper wearer stands stilled in Orsolin Manor"},
    {"id": "item.first_wardens_lantern", "name": "The First Warden's Lantern", "base": "bi.lantern", "quality": "storied",
     "signature": {"prop_id": "prop.glowing", "tier": 1}, "properties": [{"prop_id": "prop.wayfinder", "tier": 1}],
     "facts": {"burns": "without oil while its bearer keeps the Warden's Vow", "wayfinder": "its bearer always finds the way back to a lit hearth", "custody": "the Bellwardens; given to a warden who reaches rank 3 or saves the Last Bell"},
     "where": "loc.tolling.belltower (the chapter-house)", "price": 3200,
     "story": "carried by the first Bellwarden who walked the Hem on the night after Hush-eve"},
    {"id": "item.mother_bell_shard", "name": "A shard of the Mother Bell", "base": "bi.charm", "quality": "storied",
     "signature": {"prop_id": "prop.resist_mind", "tier": 2}, "properties": [],
     "facts": {"true_bell": True, "peal": "struck, it opens hushed ground within band.close for a round", "story_hook": "fitted back into the Mother Bell, it is one of the pieces a recasting needs"},
     "where": "loc.sael (the cathedral nave)", "price": 3200,
     "story": "a palm-sized fragment of the Mother Bell, blown out of its lip when it cracked"},
]
STORIED_SETS = []   # 08.4.8 sets need a named composite in composites.yaml (05's file): none in the starter region (DL-13-15)
