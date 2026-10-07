# deed.wilds -- 14 abilities.
from dsl05 import *

W = 'deed.wilds.'
FOE = 'the target of the Strike'

# ---------------- survival ----------------
ab('ab.hard_country', 'Hard Country', W + 'survival.hardship', 1, 'weathering', 'Edge', 'passive',
   'Bear what the open land does to a body.',
   'Applies to hazards of cold and of heat.',
   [rk("Hazards of cold and of heat count one severity rung lower for you.",
       [hazard(['harm.frost.cold', 'harm.fire.heat'])]),
    rk("Hazards of cold and of heat count one severity rung lower for you, and you gain +1 to Endure checks against weather and exhaustion.",
       [hazard(['harm.frost.cold', 'harm.fire.heat']), edge(1, 'verb = verb.endure and the source is weather or exertion')]),
    rk("Hazards of cold and of heat count one severity rung lower for you and for up to two companions travelling with you, and you gain +1 to Endure checks against weather and exhaustion.",
       [hazard(['harm.frost.cold', 'harm.fire.heat']), edge(1, 'verb = verb.endure and the source is weather or exertion'), tgt(2)])],
   harm_tags=['harm.frost.cold', 'harm.fire.heat'], x=[('fire and ice thrown as attacks', 'armor, cover, or a ward')])

ab('ab.shelter_anywhere', 'Shelter Anywhere', W + 'survival.shelter', 3, 'camp', 'Permission', 'beat',
   'Make a safe night out of bad ground.',
   'Applies to a camp you make, with an hour of work, in any terrain that has loose material: brush, snow, stone, turf.',
   [rk("With an hour of work, make a camp in which rests have full quality whatever the weather, and weather hazards count one severity rung lower for everyone in it.",
       [perm(4), hazard(['harm.frost.cold', 'harm.fire.heat', 'harm.storm'])]),
    rk("With an hour of work, make a camp in which rests have full quality whatever the weather, weather hazards count one severity rung lower for everyone in it, and the camp is a Protective lever against anything that comes on it in the night.",
       [perm(4), hazard(['harm.frost.cold', 'harm.fire.heat', 'harm.storm']), lev('protective', 'beats by those in the camp against a night encounter', 'scene')])],
   x=[('hiding the camp from a search', 'verb.sneak (conceal an object)')], nmi=['that nothing can find the camp'])

# ---------------- tracking ----------------
ab('ab.quarrys_mark', "Quarry's Mark", W + 'tracking.hunting', 1, 'mark', 'Reaction', 'trigger',
   'Fix your aim on one creature you have struck.',
   'Applies to one creature that your own attack has just hit; one mark at a time.',
   [rk("When your attack hits, mark the target: it is exposed until the scene ends, and you may cite the mark as a Precision lever on Observe beats that track it this scene.",
       [cond('cond.exposed', 1, 'scene', 'the creature your attack hit'), lev('precision', 'Observe beats that track the marked creature', 'scene', verbs=['verb.observe'])], f=1, per='scene_end'),
    rk("When your attack hits, mark the target: it is exposed until the scene ends, your Strikes against it deal +1 harm, and you may cite the mark as a Precision lever on Observe beats that track it this scene.",
       [cond('cond.exposed', 1, 'scene', 'the creature your attack hit'), lev('precision', 'Observe beats that track the marked creature', 'scene', verbs=['verb.observe']), hedge(1, 'a Strike against the marked creature'), fact('the marked creature', 'marked_by', 'the pc')], f=1, per='scene_end'),
    rk("When your attack hits, mark the target: it is exposed until the scene ends, your Strikes against it deal +2 harm, and you may cite the mark as a Precision lever on Observe beats that track it this scene. Twice per scene.",
       [cond('cond.exposed', 1, 'scene', 'the creature your attack hit'), lev('precision', 'Observe beats that track the marked creature', 'scene', verbs=['verb.observe']), hedge(2, 'a Strike against the marked creature'), fact('the marked creature', 'marked_by', 'the pc')], f=1, per='scene_end', uses=2)],
   hook='on_attack_hit', when='the attack was your own declared beat', ckey=True,
   x=[('knowing where the creature is when out of your senses', 'verb.observe (track); deed.arcane.divination'), ('marking a creature you have not hit', 'verb.setup')],
   nmi=['a visible sign on the creature', 'knowledge of its location'], basis=['WE-00-6 (00 names this ability; defined here)'])

ab('ab.read_sign', 'Read Sign', W + 'tracking.sign', 2, 'trail_reading', 'Working', 'beat',
   'Take from a trail what made it.',
   'Applies to tracks, spoor or disturbed ground you can examine.',
   [rk("Study a trail (Observe, Wits, against its tier). The beat's reach is one rung higher, and among what it delivers you always learn how many made it and how long ago.",
       [reach('this beat'), rev('the number of trail-makers and the age of the trail')]),
    rk("Study a trail (Observe, Wits, against its tier). The beat's reach is one rung higher, among what it delivers you always learn how many made it and how long ago, and what you learn is a Precision lever on following it this scene.",
       [reach('this beat'), rev('the number of trail-makers and the age of the trail'), lev('precision', 'beats that follow this trail', 'scene')])],
   attr='wits', check=('aimed', 'verb.observe', "the trail's tier (10)"), x=[('a trail that does not exist', 'the Oracle decides whether anything passed')])

ab('ab.relentless_pursuit', 'Relentless Pursuit', W + 'tracking.trailing', 4, 'pursuit', 'Exception', 'passive',
   'Stay on a trail through what should end it.',
   'Applies to beats that follow a trail or run down a quarry.',
   [rk("+1 to beats that follow a trail; snags from rain, darkness and hard ground on those beats are waived; and each success ticks your pursuit clock one segment more.",
       [edge(1, 'the beat follows a trail or advances a pursuit clock'), waive('snags from weather, darkness and hard ground on tracking beats', 'you follow a trail'), tick('your pursuit clock', 1)])],
   x=[('a quarry that crossed water by boat or took to the air', 'pick the trail up again where it lands (verb.observe)')])

ab('ab.apex_hunter', 'Apex Hunter', W + 'tracking.hunting', 5, 'kill_shot', 'Working', 'rider',
   'Bring down the creature you have hunted.',
   'Applies to a Strike against a creature you have marked or have tracked to this place.',
   [rk("Your Strike against a creature you marked or tracked here deals harm two severity rungs heavier, +2, the target bleeds until the scene ends and is exposed until the end of its next turn, and the Strike holds a Precision lever.",
       [sev(2, 'this Strike'), hedge(2, 'this Strike'), cond('cond.bleeding', 1, 'scene', FOE), cond('cond.exposed', 1, 'rounds:1', FOE), lev('precision', 'this Strike')], f=2)],  # [revision: I-033]
   verbs=['verb.strike'], lim=1, traits=['trait.action.attack'],
   x=[('a creature you met by chance', "ab.quarrys_mark first, or track it")])

# ---------------- navigation ----------------
ab('ab.pathfinder', 'Pathfinder', W + 'navigation.wayfinding', 1, 'wayfinding', 'Edge', 'passive',
   'Keep a true line across unmarked country.',
   'Applies to beats that find or keep a route overland.',
   [rk("Navigation beats overland are framed one stakes rung lower.",
       [stakes('deed_tag under deed.wilds.navigation and the route is overland')]),
    rk("Navigation beats overland are framed one stakes rung lower, and you gain +1 to them.",
       [stakes('deed_tag under deed.wilds.navigation and the route is overland'), edge(1, 'deed_tag under deed.wilds.navigation and the route is overland')]),
    rk("Navigation beats overland are framed one stakes rung lower, you gain +1 to them, and each day of travel you lead ticks travel progress one segment more.",
       [stakes('deed_tag under deed.wilds.navigation and the route is overland'), edge(1, 'deed_tag under deed.wilds.navigation and the route is overland'), tick('the journey\'s travel progress', 1)])],
   x=[('routes underground or at sea', 'ab.hidden_ways; lic.training.wilds_seafaring')])

ab('ab.hidden_ways', 'Hidden Ways', W + 'navigation.underways', 3, 'shortcut', 'Working', 'beat',
   'Find the way through that the map does not show.',
   'Applies to a journey or a site whose ground you can see or have a map of.',
   [rk("Search out a shorter or safer way (Observe or Recall, Wits, against the terrain's tier). On a success the route is recorded as discovered, travel or site progress ticks by your delivered reach, the next encounter check on that route is waived, and the party's next travel beat holds a Protective lever.",
       [tick("the journey's travel progress or the site's progress clock", 'delivered_reach'), rev('a route between two known places'), waive('the next encounter check on that route', 'you travel the discovered route'), lev('protective', "the party's next travel beat")], f=1, per='scene_end'),
    rk("Search out a shorter or safer way (Observe or Recall, Wits, against the terrain's tier). On a success the route is recorded as discovered, travel or site progress ticks by your delivered reach, the next encounter check on that route is waived, and travel beats on that route are framed one stakes rung lower.",
       [tick("the journey's travel progress or the site's progress clock", 'delivered_reach'), rev('a route between two known places'), waive('the next encounter check on that route', 'you travel the discovered route'), lev('protective', "the party's next travel beat"), stakes('travel beats on the discovered route')], f=1, per='scene_end')],
   attr='wits', check=('aimed', 'verb.observe', "the terrain's tier (10)"), x=[('a way through a sealed wall', 'verb.force; a spell of alteration')])

# ---------------- animals ----------------
ab('ab.gentle_hand', 'Gentle Hand', W + 'animals.calming', 1, 'calm_beast', 'Working', 'beat',
   'Take the fear or the anger out of an animal.',
   'Applies to one beast (creature.beast) within band.close that can see or hear you.',
   [rk("Calm a beast (Talk or Handle, Presence, against its Resolve defense). On a success it will not attack you this scene unless it is harmed, and its standing toward you is recorded one step warmer.",
       [restr({'methods': ['attacking you']}, 'the beast', 'scene'), fact('the beast', 'standing_to_pc', 'one step warmer this scene')]),
    rk("Calm a beast (Talk or Handle, Presence, against its Resolve defense). On a success it will not attack you this scene unless it is harmed, its standing toward you is recorded one step warmer, and you hold a Precision lever on Handle beats with it.",
       [restr({'methods': ['attacking you']}, 'the beast', 'scene'), fact('the beast', 'standing_to_pc', 'one step warmer this scene'), lev('precision', 'Handle beats with that beast', 'scene', verbs=['verb.handle'])]),
    rk("Calm up to three beasts (Talk or Handle, Presence, against the highest Resolve defense). On a success they will not attack you or those with you this scene unless harmed, their standing toward you is recorded one step warmer, and you hold a Precision lever on Handle beats with them.",
       [restr({'methods': ['attacking you or those with you']}, 'each beast', 'scene'), fact('each beast', 'standing_to_pc', 'one step warmer this scene'), lev('precision', 'Handle beats with those beasts', 'scene', verbs=['verb.handle']), tgt(2)])],
   attr='presence', check=('aimed', 'verb.talk', "the beast's Resolve defense"),
   x=[('a creature that is not a beast', 'verb.talk if it can understand you'), ('commanding it to fight for you', 'ch.16 companions; ab.beast_speech')])

ab('ab.beast_at_heel', 'Beast at Heel', W + 'animals.training', 2, 'handler', 'Lever', 'rider',
   'Direct a trained animal as an extension of your will.',
   'Applies to the command action (06) given to an animal companion you have trained or bonded.',
   [rk("When you command your animal, its commanded act holds a Precision lever and an Amplifying lever.",
       [lev('precision', "the animal's commanded act"), lev('amplifying', "the animal's commanded act")]),
    rk("When you command your animal, its commanded act holds a Precision lever and an Amplifying lever, and while it is within band.close of you it has +1 to its Agility defense.",
       [lev('precision', "the animal's commanded act"), lev('amplifying', "the animal's commanded act"), dedge(1, 'agility', 'your animal is within band.close of you')])],
   verbs=['the companion command action (06)'], x=[('an extra act by the animal', 'INV-11: it acts only when commanded')])

# ---------------- foraging ----------------
ab('ab.green_larder', 'Green Larder', W + 'foraging.food', 1, 'forage', 'Edge', 'passive',
   'Find what can be eaten where others see none.',
   'Applies to foraging beats in terrain that bears life.',
   [rk("Foraging beats have reach one rung higher.",
       [reach('deed_tag under deed.wilds.foraging')]),
    rk("Foraging beats have reach one rung higher, and you gain +1 to them.",
       [reach('deed_tag under deed.wilds.foraging'), edge(1, 'deed_tag under deed.wilds.foraging')]),
    rk("Foraging beats have reach one rung higher, and you gain +2 to them.",
       [reach('deed_tag under deed.wilds.foraging'), edge(2, 'deed_tag under deed.wilds.foraging')])],
   x=[('foraging on bare rock, ice or in a city', 'the terrain decides (10)')])

ab('ab.wild_physic', 'Wild Physic', W + 'foraging.herbs', 4, 'herb_cure', 'Working', 'beat',
   'Draw a cure from growing things.',
   'Applies to one living being you can tend for an interval, with herbs gathered in wild terrain within the day or carried as supply.',
   [rk("Tend one being for an interval with gathered herbs: it regains 5 Vitality, cond.poisoned and one other bodily condition end, and its next check against that poison or sickness is framed one stakes rung lower.",
       [heal(5, 'the tended being'), cleanse('cond.poisoned', 'the tended being'), cleanse('one condition of category physical', 'the tended being'), lev('protective', "the tended being's checks against that affliction", 'scene')], f=1, per='rest_short')],
   attr='wits', x=[('wounds and marks', 'ch.07 treatment'), ('a being already healed twice since its long rest', 'the healing cap (05.7.8)')])

# ---------------- seafaring ----------------
ab('ab.sea_legs', 'Sea Legs', W + 'seafaring.sailing', 1, 'deck_sense', 'Edge', 'passive',
   'Keep your body\'s balance on a moving deck.',
   'Applies to Exert, Move and Handle beats made aboard a vessel.',
   [rk("+1 to Exert, Move and Handle beats aboard a vessel.",
       [edge(1, 'verb in [verb.exert, verb.move, verb.handle] and you are aboard a vessel')]),
    rk("+1 to Exert, Move and Handle beats aboard a vessel, and the snag a pitching deck places on any of your beats is waived.",
       [edge(1, 'verb in [verb.exert, verb.move, verb.handle] and you are aboard a vessel'), waive('the snag from a pitching deck', 'you are aboard a vessel')]),
    rk("+2 to Exert, Move and Handle beats aboard a vessel, and the snag a pitching deck places on any of your beats is waived.",
       [edge(2, 'verb in [verb.exert, verb.move, verb.handle] and you are aboard a vessel'), waive('the snag from a pitching deck', 'you are aboard a vessel')])],
   x=[('swimming', 'verb.exert')])

ab('ab.storm_helm', 'Storm Helm', W + 'seafaring.piloting', 5, 'pilotage', 'Working', 'beat',
   'Bring a vessel through water that should take it.',
   'Applies to a vessel you steer or command, against one hazard of sea, river or weather.',
   [rk("Take the helm against a hazard (Handle, Wits, against the hazard's tier). The beat's reach is one rung higher and its stakes one rung lower; the hazard counts one severity rung lower for the vessel and up to three others aboard; the crew's beats hold a Precision lever this scene; a gear cost to the vessel from this beat is waived; and the passage clock ticks by your delivered reach.",
       [reach('this beat'), stakes('this beat'), hazard(['harm.physical.crush', 'harm.physical.asphyxia', 'harm.storm']), tgt(3), lev('precision', "the crew's beats against the hazard", 'scene'), waive('cost.gear applied to the vessel by this beat', 'this beat'), tick('the passage clock', 'delivered_reach')], f=3, per='scene_end')],
   attr='wits', check=('aimed', 'verb.handle', "the hazard's tier (10)"), x=[('a vessel already holed and sinking', 'verb.exert and ch.10')])
