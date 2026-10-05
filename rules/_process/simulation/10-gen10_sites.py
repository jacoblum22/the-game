# Generates rules/data/sites.yaml (ch.10). Content hand-authored here; the script formats and validates
# every tag, archetype, hazard and trap reference, and checks that every theme x domain pair gates >= 3
# archetypes (the site denizen table is never empty).
import yaml, sys
OUT, DATA = sys.argv[1], sys.argv[2]
tags = {t['id'] for t in yaml.safe_load(open(f'{DATA}/tags.yaml', encoding='utf-8'))['tags']}
arch = yaml.safe_load(open(f'{DATA}/archetypes.yaml', encoding='utf-8'))['archetypes']
haz = {h['id'] for h in yaml.safe_load(open(f'{DATA}/hazards.yaml', encoding='utf-8'))['hazards']}
B = ['10.13', 'R5 P-28', 'C:P5', 'R2 #13']

def rows(items):  # list of str or dict -> d6/d12 rows
    out = []
    for i, it in enumerate(items, 1):
        r = {'range': str(i)}
        if isinstance(it, str): r['result'] = it
        else: r.update(it)
        out.append(r)
    return out

def D(kind, text, ref=None):
    r = {'kind': kind, 'result': text}
    if ref: r['ref'] = ref
    return r

themes = []
def theme(id, name, desc, danger, gates, weights, loot, dangers, disc, climax, omens, regrowth, facts):
    themes.append({'id': f'site.theme.{id}', 'name': name, 'tags': [], 'description': desc, 'danger': danger,
                   'creature_gate_tags': gates, 'creature_weights': weights, 'loot_gate_tags': loot,
                   'dangers': rows(dangers), 'discoveries': rows(disc), 'climax': rows(climax),
                   'danger_clock_omens': omens, 'regrowth': regrowth, 'place_facts': facts,
                   'lifecycle': 'provisional', 'basis': B})

theme('ancient', 'Ancient', 'Forgotten by all; old works, old wards, old guardians that still keep their charge.', 'wild',
  ['creature.construct', 'creature.spirit.ancestor', 'creature.undead.mindless', 'creature.beast.vermin', 'creature.horror.ooze'],
  {'creature.construct': 3, 'creature.spirit.ancestor': 2, 'creature.undead.mindless': 2, 'creature.beast.vermin': 2, 'creature.horror.ooze': 1},
  ['creature.construct', 'material.gem.crystal', 'org.order.arcane', 'material.stone.fine'],
  [D('gatekeeper', 'a guardian construct wakes at a threshold (a gatekeeper: +1 progress when defeated)', 'creature.construct'),
   D('trap', 'an old ward-trap still armed (a glyph or a mechanism, band-scaled)'),
   D('barrier', 'a sealed door whose mechanism is a puzzle (Understand first: a lever)'),
   D('hazard', 'the floor gives onto a lower hall (a height: fall by the drop)', 'haz.fall_20'),
   D('hazard', 'stale, dead air in a sealed room', 'haz.bad_air'),
   D('denizen', 'vermin pour from a burst wall'),
   D('dread', 'the faces carved on the walls all turn to follow you (dread S1)'),
   D('clock', 'something deep below begins to grind: the danger clock +1'),
   D('patrol', 'a construct walks its ancient round (a pending threat on the path behind)'),
   D('hazard', 'a ceiling held up by one cracked pillar', 'haz.cave_in'),
   D('barrier', 'the way on is a shaft with rusted rungs (a climb, recorded height)'),
   D('denizen', 'an ooze that has eaten everything else here')],
  ['a wall map of the whole site (progress +2, once)', 'the builders\' script: a language clue (15)', 'an intact mechanism worth salvage (08.6.8)',
   'a dead delver\'s journal (a clue toward the heart: progress +1)', 'a still-burning everlamp (a glowing light source)', 'a sealed niche of grave goods (a cache)'],
  [D('guardian', 'a great construct bound to the heart', 'arch.golem'), D('sealed_way', 'a vault door of the old makers'), D('guardian', 'the ancestor-spirit of the builders, who asks a question first', 'arch.ancestor'),
   D('place_of_power', 'the engine or altar the place was built around (resonance: arcane)'), D('hoard', 'the makers\' treasury, unguarded but trapped'), D('the_lost', 'the remains of the last expedition and what they carried')],
  {'stirring': ['a click deep in the walls, like a lock turning', 'dust falling in a thin line from a seam'],
   'building': ['a rhythmic grinding far below', 'every carved eye in the hall seems newer than it was'],
   'imminent': ['a great weight shifting somewhere ahead', 'lights kindling one after another down a hall no one entered']},
  {'range': None}, [])
theme('corrupted', 'Corrupted', 'Twisted by dark power: a fiend\'s nest, a cult\'s temple, a place where something was sacrificed.', 'perilous',
  ['creature.fiend', 'creature.undead', 'creature.horror', 'creature.folk.human'],
  {'creature.fiend': 3, 'creature.undead': 2, 'creature.horror': 2, 'creature.folk.human': 2},
  ['creature.fiend', 'deed.arcane.necromancy', 'org.cult', 'material.essence.blood'],
  [D('denizen', 'cultists at a rite (a pending threat; the rite is a countdown of 4 if not stopped)'),
   D('dread', 'a sight that should not be (dread S2)'), D('hazard', 'the ground here is desecrated', 'haz.desecrated_ground'),
   D('trap', 'a profane glyph on the threshold (magical trap)'), D('gatekeeper', 'a bound fiend chained to guard a door', 'creature.fiend'),
   D('patrol', 'the walking dead shuffle the corridors (pending threat)'), D('hazard', 'a pit of filth and bones', 'haz.foul_water'),
   D('clock', 'a voice begins to chant somewhere: the danger clock +2'), D('denizen', 'a horror feeding on what the cult leaves'),
   D('barrier', 'a door sealed with blood: it opens to blood (Handle with a cost of S1 harm) or to force'), D('hazard', 'blight seeps from the walls', 'haz.blight_zone'),
   D('denizen', 'a tempter offers a bargain instead of a fight (talk first)')],
  ['the cult\'s ledger: names of members in the town (a thread, 11)', 'a captive alive in a cell (the lost)', 'a profane implement (loot with a flaw)',
   'a map of the catacombs with the altar marked (progress +2, once)', 'a desecrated relic that could be restored (a thread)', 'a list of sacrifices still to come (a clock to race)'],
  [D('rite', 'a summoning in progress: a countdown of 4'), D('guardian', 'a greater fiend half-manifest', 'arch.greater_demon'), D('guardian', 'the cult\'s priest and their faithful (elite + mob)', 'arch.cultist'),
   D('guardian', 'a wight-lord who made the place a court', 'arch.wight'), D('the_lost', 'the one taken for the sacrifice'), D('place_of_power', 'the profane altar: break it (Force, Hard) to cleanse the site')],
  {'stirring': ['a smell of hot iron and burnt hair', 'a drum somewhere, slow'],
   'building': ['candles lit in a room you passed in the dark', 'the drum quickening; voices with it'],
   'imminent': ['the walls sweating something dark', 'every voice in the place falling silent at once']},
  {'range': '5-6', 'die': 'd6'}, ['desecrated'])
theme('fortified', 'Fortified', 'Held and defended: a bandit hold, an orc fort, a goblin warren, a renegade\'s tower.', 'wild',
  ['creature.folk', 'creature.beast.predator.canine'], {'creature.folk.human': 3, 'creature.folk.orc': 2, 'creature.folk.goblin': 2, 'creature.folk.giant': 1, 'creature.beast.predator.canine': 1},
  ['creature.folk', 'org.outlaw', 'org.crown.military', 'item.weapon'],
  [D('patrol', 'a patrol on its round (a pending threat)'), D('alarm', 'an alarm line or a bell (alarm trap: 2 ticks)'), D('denizen', 'a guard post with a sentry (unaware on a 1-3)'),
   D('barrier', 'a barred door (Hard to force; a key exists somewhere: discovery)'), D('trap', 'a murder-hole or a spiked pit by the gate'), D('denizen', 'war-hounds loosed in the yard'),
   D('clock', 'a horn sounds: the danger clock +2'), D('gatekeeper', 'the sergeant of the watch (a gatekeeper)'), D('hazard', 'burning oil prepared above a stair', 'haz.fire'),
   D('denizen', 'prisoners who might be freed (non-threat; an ally or a complication)'), D('barrier', 'a portcullis down (Force Very hard; the winch is elsewhere)'), D('denizen', 'a deserter who will talk for a price (non-threat)')],
  ['the duty roster (when the guard changes: a lever)', 'a key ring', 'the strongbox (a cache)', 'a captured map of the region (11: a rumor and a route)', 'the armory (gear, 08.3.11)', 'letters from a patron (a thread)'],
  [D('guardian', 'the chieftain and the bodyguard (elite + mob)', 'arch.orc'), D('guardian', 'the bandit captain and the band', 'arch.brigand'), D('hoard', 'the warchest'),
   D('the_lost', 'the hostage the hold was built to keep'), D('guardian', 'an ogre the garrison keeps chained', 'arch.ogre'), D('sealed_way', 'the inner keep, barred')],
  {'stirring': ['a shout, then laughter, somewhere above', 'a dog barking twice and stopping'],
   'building': ['boots on the stair, unhurried', 'torches carried along the wall walk'],
   'imminent': ['someone calling a name and getting no answer', 'the horn-bearer running for the tower']},
  {'range': None, 'note': 'fortified sites re-arm one disarmed trap a week and replace fallen guards from the region\'s faction (11)'}, [])
theme('hallowed', 'Hallowed', 'Holy, or once holy: a shrine, an abbey, a saint\'s tomb, guarded by its faith or its dead.', 'settled',
  ['creature.spirit.celestial', 'creature.spirit.ancestor', 'creature.construct', 'creature.folk.human'], {'creature.spirit.celestial': 2, 'creature.spirit.ancestor': 3, 'creature.construct': 2, 'creature.folk.human': 1},
  ['org.faith', 'deed.divine', 'creature.spirit.celestial', 'material.metal.silver'],
  [D('dread', 'a voice asks why you have come (answer: Talk, or dread S1)'), D('trap', 'a warding glyph against the unworthy (magical trap)'), D('gatekeeper', 'a temple guardian that asks a sign of faith', 'creature.construct'),
   D('denizen', 'pilgrims or keepers (non-threat; standing per their faith)'), D('barrier', 'a door that opens to a prayer of the faith (Recall religion, or Force)'), D('hazard', 'the floor of a crypt gives way', 'haz.fall_10'),
   D('denizen', 'an ancestor spirit restless at the intrusion'), D('clock', 'the bells ring by themselves: the danger clock +1'), D('dread', 'the saint\'s image weeps (dread S1)'),
   D('barrier', 'a reliquary sealed in silver'), D('denizen', 'robbers already here, looting (a mixed encounter)'), D('trap', 'a falling-stone trap set by the old wardens')],
  ['a prayer book of the faith (a text, 05)', 'the saint\'s relic (the lost, or the heart)', 'an offering bowl (a cache, coin)', 'a record of miracles (lore; resonance clue)', 'a hidden stair to the crypt (a branch)', 'holy water (a consumable)'],
  [D('place_of_power', 'the shrine itself (resonance: the keeper\'s axes)'), D('guardian', 'the celestial warden', 'arch.celestial'), D('the_lost', 'the relic everyone seeks'),
   D('guardian', 'the guardian-dead of the order', 'arch.ancestor'), D('hoard', 'the treasury of offerings'), D('sealed_way', 'the sanctum, opened by a rite')],
  {'stirring': ['a bell note with no ringer', 'candles flickering toward you'],
   'building': ['a hum like many voices at prayer', 'the air growing cold and bright'],
   'imminent': ['every flame in the place standing straight up', 'a voice speaking your name, gently']},
  {'range': None}, ['consecrated'])
theme('haunted', 'Haunted', 'The dead do not rest: a barrow, a plague-house, a battlefield crypt, a drowned chapel.', 'perilous',
  ['creature.undead', 'creature.spirit.ancestor'], {'creature.undead.spectral': 3, 'creature.undead.mindless': 2, 'creature.undead.ravenous': 2, 'creature.undead.sovereign': 1, 'creature.spirit.ancestor': 1},
  ['creature.undead.spectral', 'creature.spirit.ancestor', 'terrain.ruin.tomb', 'deed.arcane.necromancy'],
  [D('dread', 'a cold hand on the neck (dread S2)'), D('denizen', 'the restless dead rise from their niches'), D('hazard', 'the place\'s haunting deepens', 'haz.haunting'),
   D('hazard', 'barrow air', 'haz.barrow_air'), D('patrol', 'a ghost walks its last route (pending threat)'), D('trap', 'a grave-trap: the lid drops, the floor tips'),
   D('clock', 'a wail rises and falls: the danger clock +2'), D('barrier', 'a door that will not open while the light burns'), D('gatekeeper', 'the barrow-guard', 'creature.undead'),
   D('dread', 'you see yourself lying among the dead (dread S1)'), D('denizen', 'a ghoul pack that came for the dead'), D('hazard', 'lights burn blue and low (light −2 intervals)')],
  ['the name of the dead (lets them be laid to rest: a thread)', 'grave goods (a cache)', 'a death mask (a clue)', 'a letter never sent', 'bones that still hold a weapon worth taking', 'a funeral inscription (lore)'],
  [D('guardian', 'the barrow-wight on its throne', 'arch.wight'), D('guardian', 'a wailing ghost bound to its bones', 'arch.ghost'), D('the_lost', 'the body someone needs buried'),
   D('hoard', 'the grave-hoard (cursed: flaw.binding possible)'), D('guardian', 'a wraith that drinks warmth', 'arch.wraith'), D('rite', 'the dead rising tonight: a countdown of 4')],
  {'stirring': ['your breath smoking in a room that was warm', 'a whisper that is almost your name'],
   'building': ['footsteps matching yours, a beat behind', 'a lantern guttering though the air is still'],
   'imminent': ['every niche empty that was full', 'a crowd of shapes at the edge of the light']},
  {'range': '6', 'die': 'd6'}, ['haunted'])
theme('infested', 'Infested', 'Overrun by things that breed: rats, spiders, goblins, fungus, an ooze-choked cistern.', 'wild',
  ['creature.beast.vermin', 'creature.beast.predator', 'creature.horror.ooze', 'creature.horror.fungal', 'creature.folk.goblin', 'creature.beast.monstrous'],
  {'creature.beast.vermin': 4, 'creature.horror.fungal': 2, 'creature.horror.ooze': 1, 'creature.folk.goblin': 2, 'creature.beast.predator': 1, 'creature.beast.monstrous': 1},
  ['creature.beast.vermin', 'creature.horror.fungal', 'material.botanical.fungus'],
  [D('denizen', 'a swarm boils out of a crack'), D('hazard', 'a vermin nest', 'haz.vermin_nest'), D('hazard', 'a spore-shelf', 'haz.spore_cloud'), D('denizen', 'the brood-mother\'s guards'),
   D('barrier', 'webs choking the passage (Force or fire)'), D('trap', 'a goblin snare'), D('clock', 'the scuttling grows: the danger clock +1'), D('hazard', 'foul water', 'haz.foul_water'),
   D('patrol', 'a hunting pack (pending threat)'), D('gatekeeper', 'a giant of its kind at a chokepoint'), D('denizen', 'eggs, and what guards them'), D('hazard', 'the floor is rotten', 'haz.fall_10')],
  ['the bones of the last delver and their pack (a cache)', 'the nest\'s heart: where they come from (progress +1)', 'a vein of glowing fungus (a light source)', 'web-silk worth harvesting', 'an old exit, overgrown (a way out)', 'a chewed map (progress +1)'],
  [D('guardian', 'the brood-mother', 'arch.giant_vermin'), D('guardian', 'the goblin boss and the mob', 'arch.goblin'), D('guardian', 'a great ooze', 'arch.ooze'),
   D('the_lost', 'the one dragged down here'), D('hoard', 'everything they dragged in'), D('place_of_power', 'the fungal heart (burn it to clear the site)')],
  {'stirring': ['a rustling in the walls', 'a smell of musk, faint'], 'building': ['the rustling everywhere, and close', 'droppings fresh and warm'],
   'imminent': ['the floor ahead moving', 'a sound like rain that is not rain']},
  {'range': '5-6', 'die': 'd6'}, [])
theme('ravaged', 'Ravaged', 'Broken by war, fire or disaster: a sacked town, a burned abbey, a flooded mine, a fallen tower.', 'wild',
  ['creature.beast', 'creature.folk', 'creature.undead.ravenous'], {'creature.beast.predator': 2, 'creature.beast.vermin': 2, 'creature.folk.human': 2, 'creature.folk.goblin': 1, 'creature.undead.ravenous': 1},
  ['creature.folk', 'terrain.ruin', 'item.goods.treasure'],
  [D('hazard', 'a wall that leans', 'haz.rockfall'), D('hazard', 'a floor burned through to the cellar', 'haz.fall_20'), D('denizen', 'scavengers on a carcass'), D('denizen', 'looters with a cart (a mixed encounter)'),
   D('barrier', 'the way choked with rubble (a dig clock of 4)'), D('hazard', 'smouldering timbers', 'haz.smoke'), D('clock', 'something collapses deeper in: the danger clock +1'), D('dread', 'the dead where they fell (dread S1)'),
   D('patrol', 'ghouls drawn by the dead (pending threat)'), D('hazard', 'water flooding the lower rooms', 'haz.cold_water'), D('gatekeeper', 'a beast that has made the ruin its den'), D('trap', 'a defender\'s last trap, still set')],
  ['a survivor in hiding (the lost, or an ally)', 'what the attackers missed (a cache)', 'a broken banner (whose? a thread)', 'a diary of the last days', 'the well, clean (a water source)', 'a mason\'s plan of the building (progress +2)'],
  [D('hoard', 'the strongroom the attackers never found'), D('guardian', 'the beast that took the ruin', 'arch.monstrous_beast'), D('the_lost', 'the survivor, or the remains'),
   D('guardian', 'a looter-captain and their crew', 'arch.brigand'), D('a_way_through', 'the far gate: a route beyond'), D('sealed_way', 'the vault under the collapse (a dig clock of 6)')],
  {'stirring': ['stone ticking as it settles', 'crows lifting from the roofs'], 'building': ['a slow slide of rubble somewhere close', 'the smell of fresh smoke'],
   'imminent': ['the whole ceiling groaning', 'a cloud of dust rolling down the hall toward you']},
  {'range': '6', 'die': 'd6'}, [])
theme('wild', 'Wild', 'Taken back by the living world: a fey ring, a beast\'s lair, a strangling grove, a spirit\'s pool.', 'wild',
  ['creature.beast', 'creature.spirit.fey', 'creature.spirit.place', 'creature.horror.plant'], {'creature.beast.predator': 3, 'creature.beast.reptile': 1, 'creature.spirit.fey': 2, 'creature.spirit.place': 1, 'creature.horror.plant': 2},
  ['creature.spirit.fey', 'deed.primal', 'creature.beast', 'material.wood.witchwood'],
  [D('denizen', 'the lair\'s beast is home'), D('hazard', 'a fey crossing', 'haz.fey_crossing'), D('barrier', 'thorns as thick as a wrist (Force, or fire)'), D('hazard', 'a mire', 'haz.mire'),
   D('denizen', 'a fey creature that wants a game or a gift'), D('trap', 'a hunter\'s old snare'), D('clock', 'the wood itself seems to close behind: the danger clock +1'), D('gatekeeper', 'the guardian of the grove', 'creature.spirit.place'),
   D('dread', 'eyes in every shadow (dread S1)'), D('denizen', 'a strangling vine that moves'), D('patrol', 'a hunting cat on your trail (pending threat)'), D('hazard', 'a hidden drop under the leaves', 'haz.fall_10')],
  ['a spring of clear water (water source; resonance primal)', 'a tree marked with old signs (a way-finding lever)', 'the beast\'s leavings: bones of what it ate', 'herbs worth gathering (forage Easy here)', 'a fey token (a thread)', 'a sleeping place, sheltered (a secured area)'],
  [D('guardian', 'the great beast of the place', 'arch.monstrous_beast'), D('guardian', 'the fey lord of the ring', 'arch.fey_noble'), D('place_of_power', 'the spirit\'s pool (resonance primal)'),
   D('guardian', 'the strangling heart-tree', 'arch.monstrous_plant'), D('the_lost', 'the child the wood took'), D('a_way_through', 'the hidden path through to the far side')],
  {'stirring': ['birdsong stopping all at once', 'branches moving without wind'], 'building': ['a musk on the air, strong', 'the path behind you no longer where it was'],
   'imminent': ['every living thing silent', 'something large breathing just beyond the light']},
  {'range': '6', 'die': 'd6'}, [])

domains = []
def domain(id, name, terr, light, tier, size, rest, features, shift, disc, hazards, traps, open_='closed'):
    domains.append({'id': f'site.domain.{id}', 'name': name, 'tags': terr[:1], 'terrain_tags': terr, 'light': light, 'explore_tier': tier,
                    'typical_size': size, 'rest_site': rest, 'openness': open_, 'features': rows(features), 'shift': rows(shift),
                    'discoveries': rows(disc), 'hazards': hazards, 'traps': traps, 'lifecycle': 'provisional', 'basis': B})
F = lambda text, kind=None, **kw: dict({'result': text}, **({'feature_kind': kind} if kind else {}), **kw)
domain('barrow', 'Barrow', ['terrain.ruin.tomb.barrow'], 'dark', 'moderate', 'small', 'rough',
  [F('a low passage of dry-stone walls', 'chokepoint'), F('a chamber of stone shelves with bones', 'cover'), F('a fallen capstone half-blocking the way', 'cover'), F('a burial pit, 10 ft deep', 'height', drop_ft=10),
   F('a corbelled chamber with a smoke-hole far above'), F('a niche with a slumped skeleton and grave goods', 'loose_object'), F('roots hanging through the ceiling', 'veil'), F('a standing stone carved with spirals'),
   F('a forecourt of fitted slabs, one loose', 'loose_object'), F('a passage half-filled with fallen earth', 'difficult_ground'), F('a sealed stone door with a carved face', 'barrier'), F('a ring of cairns inside the mound')],
  ['earth sifts down; a passage behind narrows', 'a draught snuffs unshielded flames (light: unshuttered sources −1 interval)', 'a stone slab slides shut behind (a barrier on the way out)', 'water seeps in: the floor becomes difficult ground', 'a sound carries from deeper in', 'the air turns close (haz.bad_air begins in this area)'],
  ['a carved king-list (lore)', 'a bronze torc (a cache)', 'charcoal from an old fire (others came this way)', 'a grave-offering bowl with coins', 'a runic warning (lore: the heart\'s nature)', 'a shaft of daylight (a way out)'],
  [['haz.barrow_air', 3], ['haz.bad_air', 2], ['haz.cave_in', 1], ['haz.fall_10', 2]], [['trap.falling_slab', 2], ['trap.pit', 2], ['trap.needle_lock', 1], ['trap.curse_glyph', 1]])
domain('crypt', 'Crypt or catacomb', ['terrain.ruin.tomb.crypt', 'terrain.ruin.tomb.catacomb'], 'dark', 'moderate', 'medium', 'rough',
  [F('a long gallery of niches stacked to the vault'), F('an ossuary of skulls set in patterns', 'cover'), F('a sarcophagus on a dais', 'cover'), F('a narrow stair spiralling down', 'chokepoint'),
   F('a flooded lower vault, knee-deep', 'difficult_ground'), F('a chapel with a broken altar'), F('iron gates rusted half-open', 'barrier'), F('a well shaft, 40 ft', 'height', drop_ft=40),
   F('a collapsed section with a way through the bones', 'difficult_ground'), F('a mourners\' hall with stone benches', 'cover'), F('a hanging censer on a chain', 'loose_object'), F('a crossroads of four galleries')],
  ['bones shift and fall from a niche (noise: the danger clock +1)', 'a gate swings shut behind (a barrier)', 'water rises a foot in the lower vaults', 'a draught snuffs unshielded flames', 'a slab cracks underfoot (haz.fall_10 to the vault below)', 'chanting heard far off (or imagined)'],
  ['a family\'s names and dates (lore)', 'a sealed burial with grave goods (a cache)', 'a map of the catacomb on a mason\'s slate (progress +2)', 'fresh footprints in the dust', 'a hidden door behind a sarcophagus (a branch)', 'a lamp with oil (a light source)'],
  [['haz.barrow_air', 2], ['haz.bad_air', 2], ['haz.foul_water', 1], ['haz.fall_40', 1], ['haz.cave_in', 1]], [['trap.pit', 2], ['trap.falling_slab', 2], ['trap.dart_wall', 1], ['trap.curse_glyph', 1], ['trap.collapsing_stair', 1]])
domain('cavern', 'Cavern', ['terrain.underground.cave'], 'dark', 'moderate', 'medium', 'rough',
  [F('a vaulted chamber with dripping stone teeth'), F('a squeeze between two walls of rock', 'chokepoint'), F('an underground stream crossing the floor', 'difficult_ground'), F('a ledge over a 40-ft drop', 'height', drop_ft=40),
   F('a boulder choke', 'cover'), F('a pool of black still water', 'hazard'), F('a chimney climbing up into darkness', 'height', drop_ft=20), F('a sand floor with tracks', None),
   F('a hall of crystal that throws back the light'), F('a slope of loose scree', 'hazard'), F('bats in thousands on the ceiling', 'veil'), F('a natural bridge over a chasm, 80 ft', 'height', drop_ft=80)],
  ['the stream rises: the low passage behind floods', 'a rock falls somewhere (haz.rockfall in this area if anyone lingers)', 'bats stream past (veil; the danger clock +1)', 'a draught from ahead: an exit near (progress +1)', 'the air turns bad', 'a deep boom far below'],
  ['blind white fish in a pool (food: 1 supply)', 'old torches in a niche (a light source)', 'cave paintings (lore)', 'a crystal vein worth taking (material)', 'a draught from a crack (a way out)', 'a skeleton with a rope and pick'],
  [['haz.rockfall', 2], ['haz.bad_air', 1], ['haz.cold_water', 1], ['haz.scree', 2], ['haz.fall_20', 1], ['haz.spore_cloud', 1]], [['trap.pit', 1], ['trap.snare', 1], ['trap.deadfall', 1]])
domain('flooded_cave', 'Flooded cave', ['terrain.underground.cave.flooded'], 'dark', 'hard', 'medium', 'rough',
  [F('a sump: the way on is under water for 20 ft', 'hazard'), F('a chamber half-filled with black water', 'difficult_ground'), F('a ledge just above the waterline', 'height', drop_ft=10), F('a waterfall pouring from a crack', 'veil'),
   F('a dry gallery high above the water', 'height', drop_ft=20), F('an eddy that turns in circles', 'hazard'), F('a pool with something pale moving in it'), F('stalactites reaching to the water', 'cover'),
   F('a mud bank', 'difficult_ground'), F('an air pocket in a drowned passage'), F('a rope someone left across the water'), F('a channel where the current runs fast', 'hazard')],
  ['the water rises a foot (every low area: swim)', 'the current strengthens', 'a light is soaked (unshielded torches out)', 'an air pocket fouls (haz.bad_air)', 'mud slides into the passage behind', 'the water falls, opening a dry way (progress +1)'],
  ['a drowned delver\'s pack (a cache)', 'a sealed air pocket with old supplies', 'a carving above the high-water line (lore)', 'a way up to a dry gallery (a branch)', 'fish (1 supply)', 'a float or a coracle (a vessel for the water)'],
  [['haz.cold_water', 3], ['haz.swift_water', 2], ['haz.drowning', 1], ['haz.bad_air', 1]], [['trap.snare', 1]])
domain('mine', 'Mine', ['terrain.underground.mine'], 'dark', 'moderate', 'medium', 'rough',
  [F('a gallery shored with timber', 'cover'), F('a vertical shaft with a rotten ladder, 40 ft', 'height', drop_ft=40), F('ore carts on rails', 'loose_object'), F('a flooded sump at a gallery\'s end', 'hazard'),
   F('a winding-wheel over a shaft', 'loose_object'), F('a cave-in half-blocking the drift', 'difficult_ground'), F('a miners\' rest with a cold hearth'), F('a seam of glittering ore'),
   F('a narrow crawl to a richer seam', 'chokepoint'), F('a tool store', 'cover'), F('a stope: a great hollow mined out, 20 ft deep', 'height', drop_ft=20), F('props bowed and cracking', 'hazard')],
  ['timbers groan (haz.cave_in omen in this area)', 'a cart rolls by itself down the rails (a loose object in motion)', 'firedamp gathers (haz.firedamp here)', 'water seeps: the low galleries flood', 'a distant pick, tapping', 'dust from a fall closes the way back (a dig clock of 4)'],
  ['a miners\' map (progress +2)', 'a lantern and oil (a light source)', 'a strongbox of wages (a cache)', 'ore worth hauling (goods, 08)', 'a canary\'s empty cage (bad air near)', 'the last shift\'s tally board (lore)'],
  [['haz.cave_in', 2], ['haz.firedamp', 1], ['haz.bad_air', 2], ['haz.fall_40', 1], ['haz.cold_water', 1]], [['trap.collapsing_stair', 1], ['trap.deadfall', 1], ['trap.pit', 1]])
domain('warren', 'Warren', ['terrain.ruin.dungeon.warren', 'terrain.underground.tunnel'], 'dark', 'hard', 'large', 'rough',
  [F('a low tunnel that forks three ways', 'chokepoint'), F('a midden heap', 'difficult_ground'), F('a den with bedding', 'cover'), F('a murder-hole above the tunnel', 'height', drop_ft=10),
   F('a crawl too low to stand', 'chokepoint'), F('a guardroom with a crude door', 'barrier'), F('a pit with stakes', 'hazard'), F('a fungus garden', None),
   F('a chieftain\'s hall with a throne of bones', 'cover'), F('a larder of hanging meat', 'veil'), F('a slave pen', 'barrier'), F('a dead end that is not (a hidden door)')],
  ['a gong sounds somewhere (the danger clock +1)', 'smoke drifts in (haz.smoke in this area)', 'a door slams behind and bars (a barrier)', 'tunnel collapses behind (a dig clock of 4)', 'a cry of alarm, then silence', 'young ones scatter (they will tell)'],
  ['a chieftain\'s map scratched on hide (progress +2)', 'loot from a caravan (a cache)', 'a prisoner (the lost or an ally)', 'a bolt-hole to the surface (a way out)', 'a shrine to an ugly god (lore)', 'stolen weapons (gear)'],
  [['haz.vermin_nest', 2], ['haz.smoke', 1], ['haz.foul_water', 1], ['haz.fall_10', 1]], [['trap.snare', 2], ['trap.spiked_pit', 2], ['trap.alarm_line', 2], ['trap.deadfall', 1]])
domain('underkeep', 'Underkeep', ['terrain.ruin.dungeon', 'terrain.ruin.dungeon.vault'], 'dark', 'moderate', 'large', 'rough',
  [F('a pillared hall', 'cover'), F('a long corridor of cells', 'chokepoint'), F('a guardroom with a table and benches', 'cover'), F('a stair down, 20 ft', 'height', drop_ft=20),
   F('a well chamber', 'hazard'), F('a torture room with chains', 'loose_object'), F('a vault door of iron', 'barrier'), F('a gallery above a hall, 20 ft', 'height', drop_ft=20),
   F('a flooded cistern', 'difficult_ground'), F('a collapsed corridor', 'difficult_ground'), F('a chapel to a forgotten god'), F('a library of rotten books')],
  ['a door swings shut and its bar drops (a barrier)', 'water drips faster: the cistern rises', 'a draught snuffs unshielded flames', 'dust from the ceiling (haz.cave_in omen)', 'a scream far off', 'a portcullis rattles down somewhere (the way out changes)'],
  ['a prison register (lore)', 'a key on a dead guard', 'the gaoler\'s chest (a cache)', 'a plan of the levels (progress +2)', 'a secret passage behind a shelf (a branch)', 'a lamp and oil (a light source)'],
  [['haz.bad_air', 1], ['haz.foul_water', 1], ['haz.cave_in', 1], ['haz.fall_20', 1], ['haz.vermin_nest', 1]], [['trap.pit', 2], ['trap.dart_wall', 2], ['trap.falling_portcullis', 1], ['trap.needle_lock', 1], ['trap.scything_blade', 1], ['trap.flooding_room', 1]])
domain('temple', 'Temple', ['terrain.ruin.temple'], 'dim', 'easy', 'medium', 'camp',
  [F('a nave of broken pews', 'cover'), F('an altar under a fallen roof', 'cover'), F('a bell tower, 40 ft', 'height', drop_ft=40), F('a cloister around an overgrown garth', 'veil'),
   F('a sacristy with a locked press', 'barrier'), F('a crypt stair', 'chokepoint'), F('statues of saints, one fallen', 'loose_object'), F('a scriptorium with ink-stained desks'),
   F('a font of still water'), F('stained glass scattered on the floor', 'difficult_ground'), F('a choir loft, 10 ft', 'height', drop_ft=10), F('a chapter house with stone seats')],
  ['the bell moves in the wind (noise: the danger clock +1)', 'a statue tips', 'rain pours through the roof (fire Moderate here)', 'a door to the crypt opens on its own', 'doves burst from the rafters', 'a stone falls from the arch (haz.rockfall)'],
  ['a psalter (a text, 05)', 'the poor box (a cache, coin)', 'a saint\'s bones in a reliquary', 'records of the brothers (lore)', 'holy water (a consumable)', 'a hidden stair to the treasury (a branch)'],
  [['haz.rockfall', 2], ['haz.fall_40', 1], ['haz.desecrated_ground', 1]], [['trap.falling_slab', 1], ['trap.curse_glyph', 1], ['trap.alarm_line', 1]], open_='broken')
domain('stronghold', 'Stronghold', ['terrain.ruin.fortress'], 'dim', 'easy', 'large', 'camp',
  [F('a gatehouse with a jammed portcullis', 'barrier'), F('a courtyard with a well', 'hazard'), F('a curtain wall walk, 30 ft', 'height', drop_ft=30), F('a great hall with a broken table', 'cover'),
   F('a kitchen with a hearth big enough to stand in', 'cover'), F('a barracks of rotten bunks', 'cover'), F('an armory, looted', None), F('a tower stair', 'chokepoint'),
   F('stables', 'veil'), F('a chapel', None), F('the lord\'s solar', 'barrier'), F('a postern gate to a ditch, 20 ft', 'height', drop_ft=20)],
  ['a stone falls from the battlements (haz.rockfall)', 'crows rise and wheel (noise carries: the danger clock +1)', 'a door bangs in the wind', 'smoke from a fire somewhere', 'a horn far off', 'the well\'s rope breaks'],
  ['the steward\'s accounts (lore; a thread)', 'a hidden strongroom behind the hearth (a branch)', 'weapons in a forgotten rack (gear)', 'the lord\'s seal (a key to doors and to people)', 'a plan of the castle (progress +2)', 'a postern key'],
  [['haz.rockfall', 2], ['haz.fall_20', 1], ['haz.fall_40', 1], ['haz.fire', 1]], [['trap.murder_hole', 2], ['trap.falling_portcullis', 1], ['trap.alarm_line', 2], ['trap.spiked_pit', 1]], open_='broken')
domain('tower', 'Tower', ['terrain.ruin.fortress'], 'dim', 'moderate', 'small', 'camp',
  [F('a spiral stair, broken in places', 'chokepoint'), F('a study crammed with books', 'cover'), F('a floor with a hole to the room below, 10 ft', 'height', drop_ft=10), F('a laboratory of glass and stains', 'loose_object'),
   F('a balcony over a 60-ft drop', 'height', drop_ft=60), F('a bedchamber with a canopied bed', 'cover'), F('a summoning circle chalked on the floor'), F('a storeroom of crates', 'cover'),
   F('a roof with a telescope', 'height', drop_ft=80), F('a cellar with barrels', 'cover'), F('a locked door with no handle', 'barrier'), F('a room of mirrors', 'veil')],
  ['the stair groans and a step falls', 'a glass shatters by itself', 'a draught snuffs unshielded flames', 'the circle flares for a moment (the danger clock +1)', 'books fall from a shelf', 'the wind howls through the top'],
  ['a spellbook or its pages (a text, 05)', 'reagents (components, 08)', 'a journal (lore; the heart\'s nature)', 'a wand-blank or implement (an item)', 'a key to the locked door', 'a scrying glass (a clue)'],
  [['haz.fall_10', 1], ['haz.fall_40', 1], ['haz.wild_magic', 1], ['haz.fire', 1]], [['trap.curse_glyph', 2], ['trap.needle_lock', 1], ['trap.collapsing_stair', 1], ['trap.flame_jet', 1]])
domain('sewer', 'Sewer', ['terrain.underground.sewer'], 'dark', 'moderate', 'medium', 'rough',
  [F('a brick channel with a walkway', 'chokepoint'), F('a junction of four tunnels'), F('a cistern, 20 ft to the water', 'height', drop_ft=20), F('a grate to the street above'),
   F('a smugglers\' cache room', 'cover'), F('an overflow weir', 'hazard'), F('a collapsed section to older tunnels', 'difficult_ground'), F('a vaulted chamber where the gangs meet', 'cover'),
   F('a ladder up a shaft', 'height', drop_ft=20), F('a rubbish choke', 'difficult_ground'), F('an iron door with a bar', 'barrier'), F('a dead body in the water', 'loose_object')],
  ['the water rises (the walkways flood)', 'voices come down a grate from the street', 'rats in a river (haz.vermin_nest)', 'a grate slams', 'firedamp gathers', 'a sluice opens far off: a surge comes'],
  ['a smuggler\'s ledger (a thread, 11)', 'a key to a merchant\'s cellar (a branch)', 'a lost purse (a cache, coin)', 'a map of the old tunnels (progress +2)', 'chalk marks of the thieves\' guild (lore)', 'a body with a message'],
  [['haz.foul_water', 3], ['haz.vermin_nest', 2], ['haz.firedamp', 1], ['haz.swift_water', 1], ['haz.bad_air', 1]], [['trap.alarm_line', 2], ['trap.snare', 1], ['trap.flooding_room', 1]])
domain('tanglewood', 'Tanglewood', ['terrain.forest.deepwood.tangle'], 'dim', 'hard', 'medium', 'rough',
  [F('a wall of thorn', 'barrier'), F('a hollow under great roots', 'cover'), F('a fallen giant tree to climb over', 'height', drop_ft=10), F('a stream in a gully', 'difficult_ground'),
   F('a clearing ringed with mushrooms', None), F('a bog under moss', 'hazard'), F('hanging creepers', 'veil'), F('a game trail', None),
   F('an ancient oak with a hollow heart', 'cover'), F('a ravine, 40 ft', 'height', drop_ft=40), F('a dead grove, grey and silent', None), F('a hunter\'s hide in a tree', 'height', drop_ft=20)],
  ['the trail behind closes over', 'a branch falls', 'mist rises from the ground (veil)', 'every bird stops singing (the danger clock +1)', 'rain begins under the canopy', 'the light goes green and dim'],
  ['a hunter\'s blaze on a tree (a way-finding lever)', 'herbs (forage Easy here)', 'an old camp with a cache', 'a fey token hung in a branch', 'a skull with something in its mouth', 'a spring (water source)'],
  [['haz.mire', 2], ['haz.fall_10', 1], ['haz.fey_crossing', 1], ['haz.spore_cloud', 1]], [['trap.snare', 2], ['trap.deadfall', 1], ['trap.spiked_pit', 1]], open_='closed')
domain('fen', 'Fen', ['terrain.wetland.fen', 'terrain.wetland.marsh'], 'bright', 'hard', 'medium', 'rough',
  [F('a causeway of sunken logs', 'chokepoint'), F('a reed bed taller than a man', 'veil'), F('an island with a dead tree', None), F('a pool of black water', 'hazard'),
   F('a stilt-hut, abandoned', 'cover'), F('a quaking bog', 'hazard'), F('a drowned chapel\'s tower', 'height', drop_ft=30), F('a channel to wade', 'difficult_ground'),
   F('a heron colony', None), F('a sunken boat', 'loose_object'), F('mist banks', 'veil'), F('a standing stone half in water', None)],
  ['the mist thickens (fog for the scene)', 'water rises a hand', 'midges in clouds (haz.marsh_miasma)', 'a bittern booms (the danger clock +1)', 'a will-o\'-the-wisp lights ahead', 'the causeway behind sinks'],
  ['a punt and pole (a vessel)', 'eel traps (2 supply)', 'a bog body with a torc (a cache)', 'a waymark post (a way-finding lever)', 'a fisher\'s hut with supplies', 'a drowned shrine (lore)'],
  [['haz.mire', 3], ['haz.quicksand', 1], ['haz.marsh_miasma', 2], ['haz.cold_water', 1], ['haz.foul_water', 1]], [['trap.snare', 1]], open_='open')
domain('icereach', 'Icereach', ['terrain.frozen.glacier'], 'bright', 'hard', 'medium', 'rough',
  [F('a crevasse bridged by snow', 'hazard'), F('an ice cave glowing blue', 'cover'), F('a serac leaning over the path', 'hazard'), F('a frozen waterfall to climb, 40 ft', 'height', drop_ft=40),
   F('a wind-scoured shelf', None), F('a snow field with hidden holes', 'hazard'), F('a meltwater channel', 'difficult_ground'), F('a cairn of an old expedition', None),
   F('an ice wall with something frozen in it', None), F('a moraine of loose stone', 'hazard'), F('a cornice over a 80-ft drop', 'height', drop_ft=80), F('a cave of icicles', 'veil')],
  ['the wind rises (bitter cold for the scene)', 'a crack runs through the ice underfoot', 'a serac falls (haz.avalanche omen)', 'snow begins', 'the light blinds (sight snag in bright snow)', 'a deep groan from the glacier (the danger clock +1)'],
  ['an expedition\'s cache (supply and rope)', 'a creature frozen in the ice (harvest when thawed)', 'a rope fixed by others (a lever on climbs)', 'a sheltered ice cave (a secured area)', 'old crampons (a lever on ice)', 'a frozen journal (lore)'],
  [['haz.thin_ice', 1], ['haz.fall_40', 1], ['haz.fall_80', 1], ['haz.avalanche', 1], ['haz.bitter_cold', 2], ['haz.cold_water', 1]], [['trap.snare', 1]], open_='open')

traps_used = {t for d in domains for t, w in d['traps']}
# reshape weighted lists
for d in domains:
    d['hazards'] = [{'id': h, 'weight': w} for h, w in d['hazards']]
    d['traps'] = [{'id': t, 'weight': w} for t, w in d['traps']]

sizes = [
  {'id': 'small', 'progress': 6, 'danger': 8, 'note': 'a barrow, a tower, a lair'},
  {'id': 'medium', 'progress': 8, 'danger': 8, 'note': 'a crypt, a cave system, a temple'},
  {'id': 'large', 'progress': 12, 'danger': 12, 'note': 'an underkeep, a warren, a stronghold'},
  {'id': 'vast', 'progress': [12, 12], 'danger': 12, 'note': 'two progress clocks in sequence (the halls, then the deep)'},
]
clock_templates = [
  {'id': 'clk.10.site_progress', 'name': 'The heart of <site>', 'kind': 'progress', 'segments': 'by size', 'visibility': 'public', 'direction': 'fill',
   'tick_sources': [{'on': 'frame:act.explore_onward', 'ticks': 'delivered_reach', 'condition': None},
                    {'on': 'table:tbl.10.site_opportunity rows 2 and 5', 'ticks': 1, 'condition': None},
                    {'on': 'fact:site map acquired (once)', 'ticks': 2, 'condition': 'once per site'},
                    {'on': 'on_defeat:gatekeeper', 'ticks': 1, 'condition': 'a denizen placed by a theme danger row of kind gatekeeper'}],
   'auto_ticks': [], 'decay': [], 'omens': None,
   'on_complete': {'effects': [{'effect_id': 'eff.write_fact', 'params': {'subject': 'site', 'predicate': 'next_area_is_heart', 'value': True}}], 'interrupting': False, 'then': 'close'},
   'races_with': None, 'lifecycle': 'provisional'},
  {'id': 'clk.10.site_danger', 'name': '<site> wakes', 'kind': 'danger', 'segments': 'by size', 'visibility': 'sensed', 'direction': 'fill',
   'tick_sources': [{'on': 'trait.sense.loud', 'ticks': 1, 'condition': 'a beat inside the site'}, {'on': 'cost.exposure', 'ticks': 'U(severity)', 'condition': None},
                    {'on': 'cost.time', 'ticks': 'U(severity)', 'condition': None}, {'on': 'face:S (site check)', 'ticks': 1, 'condition': None},
                    {'on': 'boundary:conflict_start', 'ticks': 1, 'condition': 'the conflict is inside the site'}, {'on': 'trap.alarm_ticks', 'ticks': 'the trap\'s listed ticks', 'condition': None},
                    {'on': 'table:theme dangers kind clock', 'ticks': 'the row\'s listed ticks', 'condition': None}],
   'auto_ticks': [], 'decay': [{'boundary': 'day', 'ticks': -2, 'only_if': 'no tick since last day'}],
   'omens': 'the theme\'s danger_clock_omens',
   'links': [{'when': 'reaches:half', 'action': 'roll the theme dangers table once (a written danger)'}],
   'on_complete': {'effects': [{'effect_id': 'eff.write_fact', 'params': {'subject': 'site', 'predicate': 'roused', 'value': True}}], 'interrupting': True, 'then': 'reset'},
   'races_with': None, 'lifecycle': 'provisional'},
]
tables = [
  {'id': 'tbl.10.area_contents', 'name': 'What is in a new area (10.13.7)', 'die': 'd12', 'results': rows([
     'nothing more than the feature', 'nothing more than the feature', 'nothing more than the feature', 'a discovery (theme or domain discoveries, engine picks the card by d6: 1-3 domain, 4-6 theme)',
     'denizens (site denizen table; omen-first: a pending threat arrives here, else a threat row becomes pending and its sign is here)', 'denizens (as 5)',
     'a trap (the domain trap list, theme-weighted)', 'a hazard (the domain hazard list)', 'an obstacle on the way on (a barrier, a rubble choke, or a gap with a recorded drop; tier = explore tier)',
     'a branch: a side passage to a side area (side areas do not advance progress; their contents roll +2, max 12)', 'a cache (08.3.12 hoard at site band - 1, coin and goods; or one gen.loot item if found by a Search beat)', 'a theme danger (roll the theme dangers)'])},
  {'id': 'tbl.10.site_opportunity', 'name': 'Site opportunity (face P, critical success on Explore onward)', 'die': 'd8', 'results': rows([
     'a secure corner: this area becomes rest_site camp (secured)', 'a clue toward the heart: progress clock +1', 'a forgotten cache: 08.3.12 hoard at site band - 1, coin and goods only',
     'an unguarded moment: the next denizen met is unaware', 'a short way: progress clock +1', 'old marks of earlier delvers: a Precision lever on Explore onward in this site (fact)',
     'a light source: a lantern with 12 intervals of oil, or three torches', 'a way out: a new exit link from this area to the surface or a known area'])},
  {'id': 'tbl.10.site_generation', 'name': 'A site generated in play (no regional table)', 'die': 'd8', 'results': rows([
     {'result': 'theme by d8', 'values': ['ancient', 'corrupted', 'fortified', 'hallowed', 'haunted', 'infested', 'ravaged', 'wild']}]),
   'rule': 'theme: d8 over the eight themes (13 weights regionally); domain: d12 over the domains whose terrain_tags match the area\'s terrain or terrain.ruin / terrain.underground (re-roll non-matching up to twice, then take the nearest); band: the area\'s home band (d6: 1 = home - 1, 6 = home + 1 as a known lair); size: d6 1-2 small, 3-4 medium, 5 large, 6 the domain\'s typical size'},
]

# --- validation ---
bad = []
def tagok(t):
    if t not in tags: bad.append(t)
for th in themes:
    for t in th['creature_gate_tags'] + list(th['creature_weights']) + th['loot_gate_tags']: tagok(t)
    for r in th['dangers']:
        if r.get('ref', '').startswith('haz.') and r['ref'] not in haz: bad.append(r['ref'])
for d in domains:
    for t in d['terrain_tags']: tagok(t)
    for h in d['hazards']:
        if h['id'] not in haz: bad.append(h['id'])
archids = {a['id'] for a in arch}
for th in themes:
    for r in th['climax']:
        if r.get('ref') and r['ref'] not in archids: bad.append(r['ref'])
print('bad refs:', bad)
def anc(t, g): return t == g or t.startswith(g + '.')
def pair_archetypes(th, dm):
    out = []
    for a in arch:
        ct = a.get('creature_tags') or []
        if not any(anc(c, g) for c in ct for g in th['creature_gate_tags']): continue
        terr = (a.get('encounter') or {}).get('terrain') or []
        if not any(anc(dt, at) or anc(at, dt) for dt in dm['terrain_tags'] for at in terr) and not any(at in ('terrain.ruin', 'terrain.underground') and any(anc(dt, at) for dt in dm['terrain_tags']) for at in terr):
            continue
        out.append(a['id'])
    return out
thin = []
pairs = {}
for th in themes:
    for dm in domains:
        lst = pair_archetypes(th, dm)
        pairs[(th['id'], dm['id'])] = lst
        if len(lst) < 3: thin.append((th['id'].split('.')[-1], dm['id'].split('.')[-1], len(lst)))
print('pairs with < 3 archetypes by terrain:', len(thin), thin[:40])
# Revision B (I-022): archetype terrain lists were widened in 09_data_arch*.py so that every theme x domain pair
# gates at least 3 archetypes; the pair pools are listed below and PR-10-10 builds the per-band table from them.
assert not thin, ('I-022: every theme x domain pair must gate at least 3 archetypes', thin)
def _weight(th, a):
    best, depth = 1, -1
    for g, w in th['creature_weights'].items():
        for c in a['creature_tags']:
            if (c == g or c.startswith(g + '.')) and g.count('.') > depth:
                best, depth = w, g.count('.')
    return best
_archd = {a['id']: a for a in arch}
denizen_pools = []
for th in themes:
    for dm in domains:
        lst = pairs[(th['id'], dm['id'])]
        bands = {b: sum(1 for x in lst if _archd[x]['bands'][0] <= b <= _archd[x]['bands'][1]) for b in range(1, 6)}
        denizen_pools.append({'theme': th['id'], 'domain': dm['id'],
                              'archetypes': [{'ref': x, 'weight': _weight(th, _archd[x])} for x in lst],
                              'fielded_by_band': bands})
fallback_rule = ('PR-10-10 builds the table from the pair pool (denizen_pools). A slot no pool archetype can fill at its '
                 'band draws from the theme gate alone (the creatures came from elsewhere to this place); only if that '
                 'also fails does it take the nearest band a pool archetype has.')
doc = {'schema_version': 1, 'site_themes': themes, 'site_domains': domains, 'sizes': sizes, 'clock_templates': clock_templates,
       'tables': tables, 'denizen_table_rule': {'gate': 'archetype creature_tags match a theme creature_gate_tag (ancestor match, 00.5.4c) AND archetype encounter.terrain matches a domain terrain tag (either direction of ancestry)',
                                                 'weights': 'theme creature_weights by the deepest matching tag (default 1)', 'bands': 'home band = site band; 30/55/15 across band-1/band/band+1 (10.10.2)',
                                                 'build': 'PR-10-10 (10_table_builder.py): eight slots, start shapes T-10-25, stepped down until each row is at most fair (home+1: hard); passes PR-10-8 by construction (10-site-tables.py: all 560 pair x band tables)',
                                                 'fallback': fallback_rule},
       'denizen_pools': denizen_pools,
       'blocks': []}
hdr = """# data/sites.yaml
# Purpose: the Delve-style site cards (10.13): eight themes (what happened to the place) and fourteen
#   domains (what kind of place it is). The theme x domain pair gates the denizens, the dangers, the
#   discoveries, the features, the hazards and traps met inside, and the place axis of the loot pool gate
#   (08.3.4 item 4; 08.3.12 hoards). Also: site sizes and their clocks, the two clock templates, the
#   area-contents and site-opportunity tables, and the rule for generating a site in play.
# Owner: 10-exploration-travel-sites (owner-block 13 for regional cards and authored sites).
# Schema: data/SCHEMAS.md#sitesyaml (site_themes, site_domains: id, terrain_tags, creature_gate_tags,
#   loot_gate_tags, features, dangers, clock_templates) plus ch.10's optional keys (documented in 10.13.2):
#   description, danger, creature_weights, discoveries, climax, danger_clock_omens, regrowth, place_facts,
#   light, explore_tier, typical_size, rest_site, openness, shift, hazards, traps; top-level sizes, tables,
#   denizen_table_rule, denizen_pools (one per theme x domain pair: its gated archetypes with weights and the
#   number fielded at each band; PR-10-10 builds the per-band table from it) [revision: I-022].
# Rows: every die table is a list of {range, result, kind?, ref?} rows; features carry 06.3.8 feature_kind
#   and, for heights, drop_ft (10.12.5: 20 ft+ is a Heavy source).
# Validation: gen10_sites.py checks every tag, archetype, hazard and trap id, and fails if any theme x domain
#   pair's terrain-filtered denizen gate holds fewer than 3 archetypes (none does since revision B, I-022).
# Basis: [R5 P-28 (Ironsworn: Delve themes x domains)] [C:P5] [R2 #13] [DL-10-13..16]
"""
txt = hdr + "\n" + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120, default_flow_style=None)
open(OUT, 'w', encoding='utf-8').write(txt)
yaml.safe_load(open(OUT, encoding='utf-8'))
print('traps referenced:', sorted(traps_used))
print('themes', len(themes), 'domains', len(domains))
