# 09_data_enc.py -- chapter 09's encounter-shaping data (09.8, 09.9, 09.11): written into
# data/behaviors.yaml beside the behavior lists. Tables are rolled by roll_table (00.14 #7), never chosen.

E = lambda eid, **p: {"effect_id": eid, "params": p}

ENCOUNTER = {
    "challenge_axes": [
        {"id": "axis.numbers", "name": "Numbers", "true_only_when": "the opposition fields three or more participants or a mob", "tests": "area effects, Defend, ground that funnels"},
        {"id": "axis.toughness", "name": "One tough foe", "true_only_when": "a single elite or solo, or one foe a band above the PC", "tests": "sustained offense, Focus pacing, called shots"},
        {"id": "axis.reach", "name": "Out of reach", "true_only_when": "the opposition fights from range, from aloft, from water or from cover", "tests": "closing distance, cover, ranged answers"},
        {"id": "axis.control", "name": "Control", "true_only_when": "the opposition's powers apply control conditions, grabs or afflictions", "tests": "Endure and Evade, break free, cleansing, the exits"},
        {"id": "axis.ground", "name": "Ground", "true_only_when": "a complication of kind terrain is in play (a hazard, a height, water, darkness, a chokepoint)", "tests": "the environment anchors (T-06-9), movement, Exert"},
        {"id": "axis.objective", "name": "Objective", "true_only_when": "either side's objective is not defeat (hold, reach, protect, escape, delay, capture)", "tests": "acting under a clock rather than winning the exchange"},
        {"id": "axis.clock", "name": "Time pressure", "true_only_when": "a public or sensed clock completes during the conflict unless the PC acts", "tests": "choosing between fighting and doing"},
        {"id": "axis.talk", "name": "Talk", "true_only_when": "the opposition will parley, yield, bargain or be turned (its behavior list has a parley row)", "tests": "influence, insight, the mercy axis"},
    ],
    "rotation_rule": "At framing, every encounter records the axes it presents (each [J:flag] against the definitions above). When an encounter table offers a choice of complication, or 12's push needs one, the engine prefers the axis least recently presented (the stalest axis first; ties by roll). 12.9.2 owns the rotation ledger; this list is its vocabulary for fights.",
    "complications": {
        "id": "tbl.09.complication", "die": "d12", "recency": True,
        "results": [
            {"range": "1", "axis": "axis.ground", "result": "Footing: the ground is wet, iced, scree or a slope; a feature `slick` (06.3.8) covers the PC's group.", "effects": [E("eff.write_fact", subject="scene", predicate="feature", value="slick ground (difficult; Exert Moderate to keep footing when hit by a Force)")]},
            {"range": "2", "axis": "axis.ground", "result": "Height: a ledge, stair, gallery or bank gives one side flag.elevated if it reaches it.", "effects": [E("eff.write_fact", subject="scene", predicate="feature", value="height (flag.elevated to whoever holds it)")]},
            {"range": "3", "axis": "axis.ground", "result": "Dark: the light is dim or failing; beyond band.close everyone is flag.obscured to those without night eyes (06 light).", "effects": [E("eff.write_fact", subject="scene", predicate="light", value="dim")]},
            {"range": "4", "axis": "axis.ground", "result": "Hazard: fire, a drop, deep water or a collapsing roof is part of the ground (10's hazard at the band's severity).", "effects": [E("eff.write_fact", subject="scene", predicate="feature", value="hazard of the place's kind (10)")]},
            {"range": "5", "axis": "axis.ground", "result": "Chokepoint: a door, bridge or narrow way lets one side hold flag.in_chokepoint.", "effects": [E("eff.write_fact", subject="scene", predicate="feature", value="chokepoint")]},
            {"range": "6", "axis": "axis.objective", "result": "Something else they want: the opposition's objective becomes rob, capture or reach (a person, a thing, a door), not the PC's defeat.", "effects": [E("eff.write_fact", subject="the opposing side", predicate="objective", value="rolled on its disposition: rob/capture/reach")]},
            {"range": "7", "axis": "axis.objective", "result": "Someone to protect: a bystander, a beast, a captive is in the fight; the PC's natural objective becomes protect.", "effects": [E("eff.summon", template="a bystander NPC (12 generation)", location="band.near", duration="scene")]},
            {"range": "8", "axis": "axis.clock", "result": "The clock runs: something completes in 4 rounds unless stopped (a fuse, a rising tide, a ritual, a bell).", "effects": [E("eff.tick_clock", clock="clk.09.complication (public, 4, +1 at each round)", ticks=0)]},
            {"range": "9", "axis": "axis.clock", "result": "Reinforcements: the opposition has more coming (clk.09.reinforcements, sensed, 4; +1 each round; omens mandatory).", "effects": [E("eff.tick_clock", clock="clk.09.reinforcements", ticks=0)]},
            {"range": "10", "axis": "axis.talk", "result": "They would rather talk: the opposition's leader opens with a demand or an offer (a parley row fires on its first action).", "effects": [E("eff.write_fact", subject="the opposing leader", predicate="opens_with", value="talk")]},
            {"range": "11", "axis": "axis.reach", "result": "Split: one of the opposition holds range or cover from the start (archer, caster, or a beast aloft).", "effects": [E("eff.write_fact", subject="one opposing participant", predicate="starts_at", value="band.far, in cover if a feature allows")]},
            {"range": "12", "axis": "axis.numbers", "result": "Mixed: roll again on the place's encounter table and combine by tbl.09.mixing.", "effects": []},
        ],
    },
    "mixing": {
        "id": "tbl.09.mixing", "die": "d8",
        "results": [
            {"range": "1-2", "result": "At each other's throats: the two groups are fighting when the PC arrives; each is a side; the PC may join, wait or slip past.", "sides": "three"},
            {"range": "3", "result": "The aftermath: the second group has just beaten the first: its survivors are bloodied (each member at half Vitality), the losers' bodies lie there (harvest, 08.3.10).", "sides": "one"},
            {"range": "4", "result": "Hunter and quarry: the first is hunting the second, which flees toward the PC.", "sides": "two"},
            {"range": "5-6", "result": "Allies: the two travel or work together (one side; the advisory is computed for both).", "sides": "one"},
            {"range": "7", "result": "A deal in progress: they are trading or bargaining; a parley with either is open.", "sides": "two"},
            {"range": "8", "result": "Captor and captive: one holds the other prisoner (a rescue, a ransom, or a witness).", "sides": "two"},
        ],
    },
    "reinforcement_clock": {"id": "clk.09.reinforcements", "kind": "countdown", "segments": 4, "visibility": "sensed",
                            "auto_ticks": [{"boundary": "round", "ticks": 1, "condition": "the conflict continues"}],
                            "tick_sources": [{"on": "pow.call_kin", "ticks": 2}],
                            "omens": {"stirring": ["a horn answers, far off", "shouts beyond the wall"], "building": ["running feet, closer", "torches on the ridge"], "imminent": ["they are at the door", "the first of them comes over the rise"]},
                            "on_complete": {"effects": "the template's reinforcements enter at band.far (06.2.5); morale -2 for their side (06.11.3)", "interrupting": False, "then": "close"}},
    "band_tells": {
        "1": {"name": "rabble", "tells": ["poorly armed, or armed with whatever came to hand", "nervous: looks to the others before acting", "thin, hungry, or young", "moves like it has never really had to fight"]},
        "2": {"name": "trained", "tells": ["kept gear, used well", "moves with purpose and keeps its footing", "watches your hands, not your face", "the scars of a few fights"]},
        "3": {"name": "elite", "tells": ["unhurried: it has done this many times", "the others give it room", "fine or terrible arms, kept with care", "it reads your stance before you move"]},
        "4": {"name": "champion", "tells": ["the ground seems smaller around it", "veterans would turn back here", "its presence is a pressure you feel", "a reputation runs ahead of it: songs, warnings, bones"]},
        "5": {"name": "legend", "tells": ["the world bends near it: weather, light, animals", "stories name it, and the stories are not exaggerated", "a whole region arranges itself around avoiding it", "standing near it, you feel how small a life is"]},
    },
    "out_of_band": {
        "rule": "09.6.6: an adversary perceived with threat band >= power_band + 1 is shown with one band tell of its band beyond the PC's, at first perception; at >= power_band + 2 the advisory is lethal for any count (T-06-13) and 07's lethal warning fires.",
        "first_perception_tell": "the band tell row of its band, chosen by the engine (no repeats in the scene)",
    },
    "beast_mood": {
        "id": "tbl.09.beast_mood", "die": "2d6", "applies_to": "adversaries met outside a conflict whose archetype has reaction_roll false (animals, the mindless excluded: the mindless follow their behavior list)",
        "results": [
            {"range": "2-4", "result": "hunting: it attacks when it reaches band.close (or springs its ambush)", "conflict": True},
            {"range": "5-6", "result": "territorial: it threatens; it attacks if the PC comes nearer than band.near or does not withdraw within 2 rounds", "conflict": "conditional"},
            {"range": "7-9", "result": "wary: it watches and keeps its distance; it attacks only if cornered or harmed", "conflict": False},
            {"range": "10-11", "result": "indifferent: feeding, resting or passing; it ignores the PC unless disturbed", "conflict": False},
            {"range": "12", "result": "curious: it approaches but does not attack; food or calm handling may win it over (Handle with Presence)", "conflict": False},
        ],
        "modifiers": ["-2 if it is starving (a fact) or the PC smells of blood", "-2 if the PC is in its lair or near its young", "+2 if the PC offers food", "+1 if the PC is downwind and quiet"],
    },
    "nemesis": {
        "id": "tbl.09.nemesis", "die": "d8", "trigger": "09.9.3: an adversary of depth recurring or principal, or any adversary that defeats the PC (victory_over_pc) or escapes a conflict with the PC alive, is promoted to recurring and rolls once here (no repeats for the same adversary)",
        "results": [
            {"range": "1", "id": "nem.scar", "result": "Scarred: it carries the wound the PC gave it. A new weak spot fact: the old wound (called shots at it work as at a weak spot).", "effects": [E("eff.write_fact", subject="self", predicate="weak_spot", value="the wound the PC gave it")]},
            {"range": "2", "id": "nem.fear", "result": "Afraid of the PC's weapon: frightened (S1) at first sight of the harm type or tag the PC defeated it with, each scene.", "effects": [E("eff.write_fact", subject="self", predicate="fears", value="the harm tag or method of its last defeat")]},
            {"range": "3", "id": "nem.learned", "result": "Learned the PC: +1 to its defenses against the PC's primary deed tag of the beat that last harmed it most (eff.defense_edge).", "effects": [E("eff.defense_edge", amount=1, attribute="agility", applies_when="against the PC's recorded signature deed tag")]},
            {"range": "4", "id": "nem.grudge", "result": "Grudge: its defeat_disposition toward the PC becomes kill (07.3.3's `disposition` warning fires when it is next perceived).", "effects": [E("eff.write_fact", subject="self", predicate="defeat_disposition_toward_pc", value="kill")]},
            {"range": "5", "id": "nem.promoted", "result": "Promoted among its kind: standard -> elite (once in its life; an elite rolls again).", "effects": [E("eff.write_fact", subject="self", predicate="variant", value="elite")]},
            {"range": "6", "id": "nem.retinue", "result": "Gathered followers: it now travels with a mob of minions of its own kind (members 3) or of its faction.", "effects": [E("eff.write_fact", subject="self", predicate="escort", value="a minion mob of 3")]},
            {"range": "7", "id": "nem.boast", "result": "Boasts of it: a rumor (11) naming the PC and the encounter, true or embellished, spreads in its region.", "effects": [E("eff.write_fact", subject="region", predicate="rumor", value="the adversary's account of the PC")]},
            {"range": "8", "id": "nem.hunts", "result": "Hunts the PC: a hidden clock (11: danger, 6, +1 a week; omens mandatory) ends in it arriving where the PC is.", "effects": [E("eff.tick_clock", clock="clk.09.nemesis_hunt (hidden, 6)", ticks=0)]},
        ],
    },
    "encounter_shapes": {
        "id": "tbl.09.group_shape", "die": "d6",
        "rule": "When an archetype's encounter.group names a range (e.g. '3-8') the count is rolled: 1-2 low end, 3-4 middle, 5-6 high end; four or more of one template become one mob (06.10.2) unless the template is named; a group with a leader fields its elite as a separate participant.",
    },
}
