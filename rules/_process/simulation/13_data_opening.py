# 13_data_opening.py -- the opening of the Thallen March (13.15): the start date, place and weather, the inciting
# incident, the Harrowby situation and its clock, the region's world clocks, the first-session teaching arc, the
# always-available leads (P16), and the sandbox's starting state. Read by 13-gen_region.py.

def fx(eid, **params):
    return {"effect_id": eid, "params": params}

START = {
    "date": "Ringing Day (the spring quarter day), year 42 S.H.",
    "watch": "dawn",
    "place": "loc.tolling.bridge",
    "weather": {"fact": "weather.today", "value": "clear and cold; frost on the bridge parapets; a light north wind", "source": "data", "note": "the first day's weather is data; from the next dawn h.10.weather rolls (10.11.3) in the temperate spring regime"},
    "moon": "new (day 1 of the year: 11.10.3)",
    "festival": "fest.quarter_spring (Ringing Day: market, sitting, hiring fair)",
}

# the clocks running at the first scene, besides each faction's goal clock (13.7)
CLOCKS = [
    {"id": "clk.thallen.harrowby_stillness", "name": "Before the stillness sets in Harrowby", "kind": "countdown", "owner": "13 / sit.thallen.harrowby_quiet",
     "segments": 6, "filled": 1, "visibility": "public", "direction": "fill",
     "tick_sources": [], "auto_ticks": [{"boundary": "watch", "ticks": 1, "condition": None}], "decay": [],
     "omens": {"stirring": ["moss already greying the stilled women's hands"], "building": ["the stilled boy's eyes have dried open"], "imminent": ["frost on the Stilled that does not melt in the sun"]},
     "on_complete": {"effects": [fx("eff.write_fact", subject="npc.nell_cask", predicate="stilled", value="set"),
                                 fx("eff.write_fact", subject="npc.hester_tenney", predicate="stilled", value="set"),
                                 fx("eff.write_fact", subject="npc.miller_boy", predicate="stilled", value="set"),
                                 fx("eff.11.seed_hook", text="Harrowby's three set Stilled; the village divides over whether to give them to the ford", source="sit.thallen.harrowby_quiet", entities=["loc.harrowby", "fac.thallen.fordwardens"], delivery="person")],
                     "interrupting": False, "then": "close"},
     "races_with": None, "links": [], "public_reason": "Gammer Thrush and Abel Marrow both know the rule: a day, and then they set (canon.stilled)"},
    {"id": "clk.thallen.quiet_wakes", "name": "The Quiet stirs", "kind": "danger", "owner": "13 / the region", "segments": 12, "filled": 5, "visibility": "hidden", "direction": "fill",
     "tick_sources": [{"on": "year_turn", "ticks": 1, "condition": "not clk.thallen.quiet_wakes.skip_next_year_tick"},
                      {"on": "fact loc.tolling.belltower.last_bell = silent", "ticks": 3, "condition": None},
                      {"on": "a true bell destroyed or a great bell silenced (a fact)", "ticks": 1, "condition": None},
                      {"on": "the Mother Bell rung cracked (a fact)", "ticks": 2, "condition": None}],
     "auto_ticks": [], "decay": [{"boundary": "season", "ticks": -1, "only_if": "a great bell was hung or recast that season (a fact)"}],
     "omens": {"stirring": ["the Hem's spring ebb is a little smaller than last year's", "a hush-pool forms where none was"],
               "building": ["the Hem advances a mile in the summer, for the first time in forty years", "the Last Bell's peal sounds thin even to lowland ears"],
               "imminent": ["the Standing Folk of Copple Field all turn their heads north on the same night", "the White Wall of the Mere visible from the Brightfields"]},
     "on_complete": {"effects": [fx("eff.write_fact", subject="loc.the_hem", predicate="hushed", value=True),
                                 fx("eff.write_fact", subject="loc.standing_downs", predicate="danger", value="perilous")],
                     "interrupting": True, "then": "close"},
     "races_with": None, "links": [{"when": "complete", "action": "create:clk.thallen.quiet_rises"}],
     "note": "the long horizon (13.17.3): 5/12 at the start; +1 a Year Turn; seven years to complete untouched, four if the Last Bell falls silent (+3)"},
    {"id": "clk.thallen.quiet_rises", "name": "The Quiet rises", "kind": "danger", "owner": "13 / the region", "segments": 12, "filled": 0, "visibility": "hidden", "direction": "fill",
     "created_by": "clk.thallen.quiet_wakes completing", "tick_sources": [{"on": "season_turn", "ticks": 2, "condition": None}], "auto_ticks": [], "decay": [],
     "omens": {"stirring": ["Woken falling still again where they stand"], "building": ["the Hem at the Brightfields' edge"], "imminent": ["Harrowby's people standing in their lanes"]},
     "on_complete": {"effects": [fx("eff.write_fact", subject="loc.brightfields", predicate="hushed", value=True),
                                 fx("eff.write_fact", subject="loc.tolling", predicate="threatened_by_the_hush", value=True)],
                     "interrupting": True, "then": "close"},
     "races_with": None, "links": [], "note": "the second half of a realm-scale situation (12+12, 00.8.1 sizes); never runs unless the first completes"},
]

SITUATIONS = [
    {"id": "sit.thallen.harrowby_quiet", "name": "The quiet in Harrowby", "template": None, "place": "loc.harrowby",
     "what": "Harrowby's bell fell silent before midnight on Ringing-eve when its clapper was stolen; a hush-pool crept over the north lane and the green, and three villagers caught in it stand stilled",
     "facts": [{"subject": "loc.harrowby.green", "predicate": "hazard", "value": "haz.thallen.hush_pool (the north lane and the green's edge) until Harrowby's bell or another true bell is rung there for a watch"},
               {"subject": "obj.thallen.harrowby_bellframe", "predicate": "clapper", "value": "missing"}],
     "clock": "clk.thallen.harrowby_stillness",
     "default_timeline": [{"at": "the next dawn", "event": "the three set (the clock completes)"},
                          {"at": "day 2", "event": "Merrin Cask accuses Tobin before the village; Tobin is beaten (a fact) unless someone stands between them"},
                          {"at": "day 3", "event": "the hush-hounds come to the pool's edge at night and take a dog"},
                          {"at": "week 1", "event": "half of Harrowby's lowland families move to Tolling (refugees at the Waking House); Vantry outriders arrive 'to keep order'"},
                          {"at": "week 2", "event": "the Wakeful petition to seat a steward in Harrowby's empty hall (their goal ticks +1)"}],
     "ends_when": "the pool is ended (a true bell rung there for a watch) or the default timeline runs out",
     "threads": ["case.silent_bells"], "lifecycle": "provisional"},
    {"id": "sit.thallen.harrowby_feud", "name": "Cask and Reave", "template": "sit_t.feud", "place": "loc.harrowby",
     "what": "the Casks have farmed Cask Farm for thirty years; Tobin Reave, Woken last spring, farmed it before the Hush and wants it back; Merrin Cask believes Tobin stole the bell to drive her off",
     "roles": {"side_a": "npc.merrin_cask", "side_b": "npc.tobin_reave", "stake": "loc.harrowby.cask_farm"},
     "default_timeline": [{"at": "day 2", "event": "Merrin accuses Tobin publicly"}, {"at": "week 2", "event": "the Wakeful take up Tobin's claim (Wakeful status toward the Casks -1)"},
                          {"at": "week 4", "event": "the Margravine's reeve rules for the Casks under the charter; Tobin is turned out"}],
     "lifecycle": "provisional"},
]

# the inciting incident (02.9.1's other half): what happens in the first scene, before the player's first word
INCITING = {
    "scene": "scn.thallen.open.bridge",
    "frame": "in medias res (12.4.3: the session's strong start)",
    "moment": "Ringing Day's dawn on the Wend Bridge: market carts queued at the toll-house, frost on the parapets, the whole town waiting for the Last Bell's great peal",
    "impetus": "the Last Bell rings the hour, and misses the third stroke; for a breath the whole town stands as still as the Stilled. Then hooves on the bridge: a farm-boy on a lathered pony (Cob Tenney) shouting that Harrowby's bell has gone quiet, and the quiet came with it, and his mother is standing in the lane and will not move",
    "pairs_with_drive": "every pregen's drive touches the incident or what it opens: Tamsin (the Wakeful and the Hem), Pip (Pell's road north), Corin (the Last Bell), Orla (true bells), Ithren (why the Hush moves), Bee (the ballad of the Mother Bell); a player-built PC's drive is bound by PR-13-3 step 6",
    "present": ["npc.cob_tenney", "npc.dace_wollin", "npc.mabry_cotter", "Bellwarden novices on the tower stair", "Vantry tithe-men at the toll-house", "pilgrims, carters, a Pell & Daughters wagon"],
    "open_prompt": "What do you do?",
}

# the first-session teaching arc (13.15.3): each beat is an OPPORTUNITY, never a gate; any order; any can be skipped
TEACHING_ARC = [
    {"beat": "T1 talk", "where": "the bridge or the Cracked Clapper", "teaches": "describing what you want in plain words; the OFFER (01.7) before a roll",
     "natural_trigger": "the PC questions Cob, calms the crowd, or asks Mother Dace or a Bellwarden what the missed stroke means",
     "oof_line": "[HOW THIS WORKS] Just say what your character does or says. When the outcome is uncertain I'll show you the odds and what's at stake before anything is rolled, and you can change your mind.",
     "anchors": ["15.4.1", "01.7"]},
    {"beat": "T2 a journey choice", "where": "leaving Tolling", "teaches": "the journey OFFER: routes in watches, danger in words, pace, the watch die (10.3.4)",
     "natural_trigger": "the PC sets out for Harrowby: the north road (2 watches, road) or straight across the Brightfields (1 watch, way-finding Easy)",
     "oof_line": "[JOURNEY] Two ways to Harrowby: the road (about a day, can't get lost) or across the fields (half that, but you have to find the way). Farm country: trouble is rare and small.",
     "anchors": ["10.3.4", "10.4.2"]},
    {"beat": "T3 explore and find a clue", "where": "Harrowby green, the bell-frame, the bell-pit stair", "teaches": "searching a place; clues as things you find, not conclusions (15.9.3)",
     "natural_trigger": "the PC looks at the bell, the lane, the stair behind the frame",
     "oof_line": "[CLUE] Clues go in your journal as what you found. Putting them together is up to you; when you think you know something, say so and I'll tell you whether what you hold supports it.",
     "anchors": ["15.9.5", "15.9.9"]},
    {"beat": "T4 a social knot", "where": "Merrin Cask and Tobin Reave on the green", "teaches": "standing, refusals and terms: a person will not talk until a condition changes (15.2.3)",
     "natural_trigger": "the PC tries to question Tobin while Merrin is accusing him",
     "oof_line": "[REFUSAL] Tobin won't talk while someone's calling him a thief. That's a wall no roll gets through, but you can change the situation.",
     "anchors": ["15.2.3", "15.3.5"]},
    {"beat": "T5 the first fight, with exits", "where": "the pool's edge at dusk", "teaches": "threat words, omens before a fight, conflict turns, retreat and morale",
     "natural_trigger": "the pending threat of the hush-hounds (dogs whining at nothing; then paw-prints ending at the silence) arrives at dusk if the PC is still in Harrowby",
     "encounter": {"ref": ["adv.thallen.hush_hound"], "count": "2", "advisory_vs_P1": "computed by the generator (13.15.4)", "exits": ["the alehouse door (shelter, band.near)", "fire: the hounds' nerve is skittish", "a true bell rung (a Protective lever and their morale clock +1)", "leaving them the sheep-pen"]},
     "oof_line": "[WARNING] Two hounds, silent. My read: easy for you. You can fight, run for the alehouse, or try something else entirely.",
     "anchors": ["06.1", "09.6", "07.3"]},
    {"beat": "T6 a deed that counts", "where": "anywhere in the first scenes", "teaches": "nothing out loud: evidence is hidden (03); the world remembers deeds under pressure",
     "natural_trigger": "any resolved beat with real stakes: the fight, carrying a child out of the pool, facing down the mob, ringing the bell in time",
     "oof_line": None, "anchors": ["03.2"]},
    {"beat": "T7 ringing true", "where": "Harrowby green (or wherever a true bell is)", "teaches": "the setting's one idea: true sound pushes back the Quiet; the clock was public, and beating it matters",
     "natural_trigger": "the PC rehangs the stolen clapper (found in the bell-pit), borrows a true handbell from the Bellwardens, or buys one on credit from Pell's yard, and rings it over the three before the next dawn",
     "oof_line": "[CLOCK] Before the stillness sets: 4 of 6. When it fills, the three in the lane are set for good, or near enough.",
     "anchors": ["13.2.4", "00.8.4"]},
]

# P16: the opening's always-available leads, by where the PC may be (12.8; 15.9.12)
LEADS = [
    {"where": "Tolling, any time", "lead": "Mother Dace at the Cracked Clapper: 'Tobin Reave saw something that night, but he'll not speak to Merrin's lot; and Gammer Thrush says the stilled set by the next dawn'", "points_to": ["clu.silent_bells.n1.p3", "clk.thallen.harrowby_stillness"]},
    {"where": "Tolling, the bell-tower", "lead": "Prior Brede, at Neutral or better, asks the PC privately to find out who has been in his tower: an offer (a thread; reward earned per 08.7.2)", "points_to": ["clu.silent_bells.n4.p2", "clu.silent_bells.n5.p2"]},
    {"where": "the road or the fields", "lead": "Cob Tenney rides with the PC if asked, and talks: the bell went quiet before midnight; Tobin was out late", "points_to": ["clu.silent_bells.n1.p3"]},
    {"where": "Harrowby", "lead": "Jessamy Cask humming an Orrowan lullaby, alone by the duck-pond, if her mother is elsewhere", "points_to": ["clu.silent_bells.n1.p4"]},
    {"where": "Harrowby green", "lead": "the bell-frame itself and the stair behind it (core clues: no roll to find)", "points_to": ["clu.silent_bells.n1.p1", "clu.silent_bells.n2.p1"]},
    {"where": "anywhere, stalled", "lead": "the case's fallbacks (15.9.12) and 12.8.2's lead injection", "points_to": ["case.silent_bells fallbacks"]},
]

# 13.17: the starting state of every running clock (faction goals are in factions.13.yaml; listed here for the codex of the DM)
STARTING_STATE = {
    "faction_goal_clocks": {"clk.thallen.vantry_goal": "3/12", "clk.thallen.bellwardens_goal": "2/8", "clk.thallen.pell_goal": "4/12", "clk.thallen.choir_goal": "1/8"},
    "petty_goal_clocks": "each petty faction's goal on a 6-segment clock at its start value (factions.13.yaml)",
    "region_clocks": {"clk.thallen.quiet_wakes": "5/12 (hidden)", "clk.thallen.harrowby_stillness": "1/6 (public)", "clk.thallen.vantry_digs": "0/8 (hidden; +1 a fortnight)", "clk.thallen.treaty_burned": "0/6 (dormant until vantry.alerted_treaty)"},
    "situations": ["sit.thallen.harrowby_quiet", "sit.thallen.harrowby_feud"],
    "seeded_hooks": ["the PC's creation hooks bound by PR-13-3", "one row of tbl.11.hook.thallen at the first World Turn if fewer than three hooks are known (11.5.10)"],
    "relations": "factions.13.yaml relations",
}
