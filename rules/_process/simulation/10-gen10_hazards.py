# Generates rules/data/hazards.yaml for ch.10 (hand-authored content; script only formats and validates).
import yaml, sys
OUT = sys.argv[1]
B = ['10.12', '07.10', 'R4 §9 10 item 1']
def H(id, name, tags, terrain, harm, sev, resist, cadence, signs, lethal, seen, no_red=True, conds=None,
      aff=None, omens=None, after=None, prot=None, pace=0, avoid=None, by_band=None, notes=None, detect=None, basis=None):
    e = {'id': id, 'name': name, 'tags': tags, 'terrain_tags': terrain, 'harm_tags': harm, 'severity': sev}
    if by_band: e['by_band'] = by_band
    e['resist'] = resist
    e['cadence'] = cadence
    e['conditions'] = conds or []
    e['affliction'] = aff
    e['no_reduction'] = no_red
    e['perceived_on_sight'] = seen
    if detect: e['detect'] = detect
    e['signs'] = signs
    e['omens'] = omens or []
    e['lethal_context'] = lethal
    e['aftermath'] = after
    e['protections'] = prot or []
    e['pace_steps'] = pace
    e['feature_kind'] = 'hazard'
    e['avoid'] = avoid or []
    if notes: e['notes'] = notes
    e['lifecycle'] = 'provisional'
    e['basis'] = basis or B
    return e
def R(verb, attr, tier, stakes=None):
    r = {'verb': verb, 'attribute': attr, 'dc_tier': tier}
    r['stakes'] = stakes or ('risky' if tier in ('easy','moderate') else 'dire')
    return r
EXH = {'effect_id': 'eff.apply_condition', 'params': {'condition': 'cond.exhausted', 'severity': 'S1', 'duration': 'until_rest:rest_long', 'target': 'self'}}
NONE = {'verb': 'none', 'attribute': None, 'dc_tier': None, 'stakes': 'dire'}
hz = []
# ---------------- weather exposure ----------------
hz.append(H('haz.cold', 'Cold', ['situation.travel'], [], ['harm.frost.cold'], 'S1', R('verb.endure','endurance','easy'), 'watch',
  ['breath smoking, fingers stiff', 'frost on the blanket at the dawn watch'], False, True,
  prot=[{'means': 'a fire in camp', 'effect': 'negate'}, {'means': 'shelter (10.11.6)', 'effect': 'negate'}, {'means': 'warm gear (a fact or item with warm: true)', 'effect': 'step -1'}],
  after='wakes at the next dawn numb, with one cond.exhausted stack', notes='frost: night watches without fire or shelter; snow: every exposed watch',
  avoid=['make camp with fire', 'shelter']))
hz.append(H('haz.bitter_cold', 'Bitter cold', ['situation.travel'], [], ['harm.frost.cold'], 'S3', R('verb.endure','endurance','hard'), 'watch',
  ['the air hurts to breathe', 'a waterskin frozen solid at the hip'], True, True, conds=[EXH],
  prot=[{'means': 'a fire', 'effect': 'negate'}, {'means': 'shelter', 'effect': 'negate'}, {'means': 'warm gear', 'effect': 'step -1'}],
  after='found or wakes at the next dawn, frostbitten: one cond.exhausted stack and a Light wound (07) to a hand or foot', avoid=['shelter', 'fire']))
hz.append(H('haz.blizzard', 'Blizzard', ['situation.travel'], [], ['harm.frost.cold'], 'S3', R('verb.endure','endurance','hard'), 'watch',
  ['the world gone white beyond arm\'s length', 'wind that shoves like a hand'], True, True, conds=[EXH],
  omens=['a yellow-grey bank of cloud low on the horizon', 'the wind dropping to nothing, then backing hard'],
  prot=[{'means': 'shelter (a building, cave, tent, snow hole)', 'effect': 'negate'}], pace=2,
  after='wakes under the snow at the next dawn with one more cond.exhausted stack', avoid=['shelter', 'snow hole (10.11.6)']))
hz.append(H('haz.heat', 'Heat', ['situation.travel'], [terrain for terrain in []], ['harm.fire.heat'], 'S1', R('verb.endure','endurance','easy'), 'watch',
  ['heat shimmer on the track', 'sweat that will not stop'], False, True,
  prot=[{'means': 'resting in shade through the watch', 'effect': 'negate'}, {'means': 'water carried beyond the day\'s need', 'effect': 'step -1'}],
  after='wakes at dusk in the shade where companions dragged them, or where they fell', notes='morning and afternoon watches of travel or labor', avoid=['travel by night', 'rest in shade']))
hz.append(H('haz.scorching_heat', 'Scorching heat', ['situation.travel'], ['terrain.arid'], ['harm.fire.heat'], 'S3', R('verb.endure','endurance','hard'), 'watch',
  ['stones too hot to touch', 'the horizon swimming'], True, True, conds=[EXH],
  prot=[{'means': 'resting in shade through the watch', 'effect': 'negate'}, {'means': 'water beyond the day\'s need', 'effect': 'step -1'}],
  after='wakes at dusk, parched: one cond.exhausted stack; the day counts as without water if none remains', avoid=['travel by night', 'rest in shade']))
hz.append(H('haz.storm_exposure', 'Storm exposure', ['situation.travel'], [], ['harm.frost.cold'], 'S2', R('verb.endure','endurance','moderate'), 'watch',
  ['rain driving sideways', 'every stitch soaked through'], False, True,
  prot=[{'means': 'shelter', 'effect': 'negate'}, {'means': 'a waxed cloak or oilskin (fact)', 'effect': 'step -1'}],
  after='wakes soaked and shivering in the lee of whatever stopped them', notes='rest taken exposed is at best partial (07.8.4)', avoid=['shelter']))
hz.append(H('haz.lightning', 'Lightning', ['situation.travel'], ['terrain.highland', 'terrain.plains'], ['harm.storm.lightning'], 'S4', R('verb.evade','agility','very_hard'), 'watch',
  ['hair lifting on the arms', 'a strike splitting a lone tree a field away'], True, True,
  notes='only while on a height, a ridge or open ground in a thunderstorm', prot=[{'means': 'getting off the height or into a hollow (a Move)', 'effect': 'negate'}],
  after='wakes where they fell, ears ringing: cond.deafened until the next rest', avoid=['leave the height', 'lie low in a hollow']))
hz.append(H('haz.storm_at_sea', 'Storm at sea', ['situation.travel.water'], ['terrain.water.sea'], ['harm.physical.crush'], 'S3', R('verb.exert','might','hard'), 'watch',
  ['green water over the bow', 'the mast groaning'], True, True,
  prot=[{'means': 'lashed to the ship (a fact, a Handle beat)', 'effect': 'step -1'}, {'means': 'below decks', 'effect': 'negate'}],
  after='overboard: haz.open_water; or battered against the rail, Down on deck', notes='each watch the vessel also takes cost.gear S2 on its hull clock (08.10.4)', avoid=['below decks', 'lash yourself']))
hz.append(H('haz.thin_air', 'Thin air', ['situation.travel'], ['terrain.highland.mountains.peak'], ['harm.physical.asphyxia'], 'S2', R('verb.endure','endurance','moderate'), 'watch',
  ['breath that will not fill the chest', 'a pounding head'], False, False, conds=[EXH],
  detect={'tier': 'easy', 'note': 'felt after the first watch above the tree line'},
  prot=[{'means': 'a day spent acclimatizing at the tree line', 'effect': 'negate for a week'}], after='carried down by companions or wakes at the next dawn', avoid=['descend', 'acclimatize']))
# ---------------- falls & ground ----------------
for ft, sev, lc in [(10,'S2',False),(20,'S3',False),(40,'S4',True),(80,'S5',True)]:
    hz.append(H(f'haz.fall_{ft}', f'Fall of {ft} ft' + (' or more' if ft==80 else ''), [], [], ['harm.physical.crush'], sev, NONE, 'exposure',
      ['a drop with no handholds', 'the ground a long way below'], lc, True, conds=[{'effect_id': 'eff.apply_condition', 'params': {'condition': 'cond.prone', 'severity': 'S1', 'duration': 'scene', 'target': 'self'}}],
      prot=[{'means': 'a tied-off rope (Protective lever; limits the fall to its slack)', 'effect': 'fall becomes haz.fall_10'}, {'means': 'water deep enough below', 'effect': 'step -2'}],
      after='lies at the foot of the drop', notes=f'06.5.8; 07.10.3; {"a Heavy (S3) source for 01.6.9" if ft>=20 else ""}{"; a severity warning source when perceived (07.3.3)" if ft>=40 else ""}'.strip('; '),
      avoid=['rope', 'climb down', 'another way'], basis=['06.5.8', '07.10.3', '01.6.9', '10.12.5']))
hz.append(H('haz.rockfall', 'Rockfall', ['situation.exploration'], ['terrain.highland', 'terrain.underground', 'terrain.ruin'], ['harm.physical.crush'], 'S3', R('verb.evade','agility','hard'), 'exposure',
  ['fresh scars on the cliff face', 'a fan of broken stone below'], False, True, no_red=False,
  omens=['pebbles skittering down', 'a dull crack above'], after='half-buried; Down until dug out (one Force beat, Easy)', avoid=['cross quickly', 'another way', 'wait for the slope to settle']))
hz.append(H('haz.avalanche', 'Avalanche', ['situation.travel'], ['terrain.highland.mountains', 'terrain.frozen'], ['harm.physical.crush', 'harm.frost.cold'], 'S5', R('verb.evade','agility','legendary'), 'exposure',
  ['a smooth loaded slope above the path', 'old debris piled in the gully'], True, True, no_red=False,
  omens=['a crack like a door slammed', 'a hush, then a rising roar'], after='buried: Down until dug out (a companion\'s three Force beats, Moderate, or the PC\'s own Endure each hour, Hard)',
  avoid=['cross one at a time at dawn', 'go round', 'wait a day after snow']))
hz.append(H('haz.cave_in', 'Cave-in', ['situation.exploration'], ['terrain.underground', 'terrain.ruin'], ['harm.physical.crush'], 'S4', R('verb.evade','agility','very_hard'), 'exposure',
  ['cracked lintels', 'props bowed with weight'], True, False, no_red=False, detect={'tier': 'moderate', 'note': 'deed.lore.engineering.structures lever'},
  omens=['dust sifting from the ceiling', 'timbers groaning'], after='buried: Down until dug out (as avalanche); the passage is blocked', avoid=['prop it (Handle, lore.engineering)', 'pass quickly and quietly']))
hz.append(H('haz.scree', 'Scree', ['situation.travel'], ['terrain.highland'], ['harm.physical.crush'], 'S2', R('verb.exert','agility','moderate'), 'exposure',
  ['a slope of loose grey stones', 'stones rattling away underfoot'], False, True, pace=1,
  after='slides 10 ft to the slope\'s foot', avoid=['go round', 'rope']))
hz.append(H('haz.mire', 'Mire', ['situation.travel'], ['terrain.wetland'], ['harm.physical.asphyxia'], 'S2', R('verb.exert','might','moderate'), 'interval',
  ['bright green moss over black water', 'reeds that grow in a ring'], False, False, detect={'tier': 'easy', 'note': 'probe with a pole: Handle, no roll'},
  conds=[{'effect_id': 'eff.apply_condition', 'params': {'condition': 'cond.restrained', 'severity': 'S2', 'duration': 'while:in the mire', 'target': 'self'}}],
  after='alone: sinks to the chest and holds there until found or freed (07.6.1 leave); with others: pulled out', pace=1, avoid=['probe the ground', 'a rope to a companion']))
hz.append(H('haz.quicksand', 'Quicksand', ['situation.travel'], ['terrain.wetland', 'terrain.arid', 'terrain.water.coast'], ['harm.physical.asphyxia'], 'S3', R('verb.exert','might','hard'), 'round',
  ['a smooth wet patch where nothing grows', 'a boot half-swallowed by the sand'], True, False, detect={'tier': 'moderate'},
  conds=[{'effect_id': 'eff.apply_condition', 'params': {'condition': 'cond.restrained', 'severity': 'S2', 'duration': 'while:in it', 'target': 'self'}}],
  after='drawn under: breath (07.10.4) applies; alone, Down only if a lethal context was not on record', avoid=['spread your weight (Exert lever)', 'a rope', 'a pole']))
hz.append(H('haz.thin_ice', 'Thin ice', ['situation.travel'], ['terrain.frozen', 'terrain.water.lake', 'terrain.water.river'], ['harm.frost.cold'], 'S2', R('verb.evade','agility','moderate'), 'exposure',
  ['dark patches under the snow', 'the ice singing underfoot'], False, False, detect={'tier': 'moderate', 'note': 'test with a pole: a Precision lever'},
  after='through the ice: haz.cold_water each interval until out (Exert, Moderate)', avoid=['test the ice', 'go one at a time', 'go round']))
hz.append(H('haz.cold_water', 'Cold water', ['situation.travel'], ['terrain.water', 'terrain.frozen'], ['harm.frost.cold'], 'S2', R('verb.endure','endurance','moderate'), 'interval',
  ['ice at the edges', 'water that takes the breath away'], False, True, conds=[EXH], after='hauled out blue and shaking; one cond.exhausted stack', avoid=['a boat', 'a ford elsewhere']))
hz.append(H('haz.swift_water', 'Swift water', ['situation.travel'], ['terrain.water.river'], ['harm.physical.crush'], 'S3', R('verb.exert','might','hard'), 'round',
  ['white water over rocks', 'a branch whipped past faster than a man runs'], True, True,
  prot=[{'means': 'a rope across or tied off', 'effect': 'step -1'}],
  after='washed ashore at the next link downstream, gear wet, one carried item lost (engine\'s draw)', avoid=['a ford', 'a bridge', 'a rope across']))
hz.append(H('haz.ford', 'Ford', ['situation.travel'], ['terrain.road.bridge', 'terrain.water.river'], ['harm.physical.crush'], 'S2', R('verb.exert','might','moderate'), 'exposure',
  ['a shallow riffle across the river', 'marker stones in the water'], False, True,
  notes='in high_water (10.11.4): S3, Hard, lethal_context true', prot=[{'means': 'a mount (the rider uses Handle, Presence)', 'effect': 'use the mount\'s Might'}, {'means': 'a rope across', 'effect': 'step -1'}],
  after='swept: as haz.swift_water', avoid=['wait for the water to fall', 'find a bridge']))
hz.append(H('haz.open_water', 'Open water', ['situation.travel.water'], ['terrain.water.sea', 'terrain.water.lake'], ['harm.physical.asphyxia'], 'S3', R('verb.exert','endurance','hard'), 'interval',
  ['swell lifting and dropping you', 'no bottom under your feet'], True, True, prot=[{'means': 'something that floats (a spar, a cask)', 'effect': 'step -1'}],
  after='found clinging to wreckage, or washed onto the nearest coast link at the next dawn', avoid=['a boat', 'a float']))
hz.append(H('haz.drowning', 'Drowning', [], ['terrain.water'], ['harm.physical.asphyxia'], 'S1', R('verb.endure','endurance','moderate'), 'round',
  ['water closing overhead', 'bubbles rising'], False, True, conds=[{'effect_id': 'eff.apply_condition', 'params': {'condition': 'cond.choking', 'severity': 'S1', 'duration': 'while:under water', 'target': 'self'}}],
  notes='07.10.4 exactly: breath 6 rounds + 2 per Endurance (min 2); then cond.choking, 1 harm per turn_end, Endure Moderate then a tier harder each round; lethal only by inheritance from a warned source', after='per 07.10.4 and 07.6.1', avoid=['surface', 'a line'], basis=['07.10.4', '10.12.6']))
hz.append(H('haz.smoke', 'Smoke', [], [], ['harm.physical.asphyxia'], 'S1', R('verb.endure','endurance','easy'), 'round',
  ['eyes streaming', 'a grey ceiling sinking lower'], False, True, conds=[{'effect_id': 'eff.apply_condition', 'params': {'condition': 'cond.choking', 'severity': 'S1', 'duration': 'while:in smoke', 'target': 'self'}}],
  prot=[{'means': 'a wet cloth over mouth and nose', 'effect': 'step -1'}, {'means': 'keeping low (a Move)', 'effect': 'step -1'}], notes='07.10.4 for breath', after='dragged out or wakes where the air was clean', avoid=['get low', 'get out']))
hz.append(H('haz.fire', 'Fire', [], [], ['harm.fire.flame'], 'S2', R('verb.evade','agility','moderate'), 'round', ['flames licking up the wall', 'heat on the face'], False, True,
  by_band=None, conds=[{'effect_id': 'eff.apply_condition', 'params': {'condition': 'cond.burning', 'severity': 'S1', 'duration': 'rounds:3', 'target': 'self'}}],
  notes='a burning brand or campfire S2; a burning room S3 (Hard); an inferno S4 (Very hard, lethal_context true, severity warning)', after='dragged clear, singed: cond.burning ends', avoid=['douse it', 'go round', 'wet cloak (step -1)']))
hz.append(H('haz.wildfire', 'Wildfire', ['situation.travel'], ['terrain.forest', 'terrain.plains.grassland'], ['harm.fire.flame'], 'S3', R('verb.evade','agility','hard'), 'interval',
  ['a wall of smoke across the horizon', 'ash falling like snow'], True, True, omens=['smoke on the wind', 'beasts running past toward you'],
  prot=[{'means': 'water to stand in', 'effect': 'negate'}, {'means': 'a burned firebreak', 'effect': 'negate'}], after='wakes in the ash of a burned-over clearing', avoid=['run upwind', 'into water', 'burn a break (Handle, survival)']))
hz.append(H('haz.lava', 'Molten rock', [], ['terrain.underground.cave.volcanic'], ['harm.fire.heat'], 'S5', R('verb.evade','agility','legendary'), 'exposure', ['the glow under a black crust', 'air that shimmers and stinks of sulphur'], True, True,
  after='none: a character Down in molten rock is dead only by the two keys; otherwise it is thrown clear, Down, at the edge', avoid=['do not cross']))
hz.append(H('haz.bad_air', 'Bad air', ['situation.exploration'], ['terrain.underground', 'terrain.ruin', 'terrain.wetland'], ['harm.venom.gas'], 'S2', R('verb.endure','endurance','moderate'), 'interval',
  ['a flame burning low and blue', 'a headache that comes from nowhere'], False, False, detect={'tier': 'easy', 'note': 'a lit flame shows it: a lantern carried in front is a Precision lever'},
  conds=[EXH], after='dragged out or wakes where the air moves', avoid=['carry a flame low', 'turn back', 'wait for a draught']))
hz.append(H('haz.firedamp', 'Firedamp', ['situation.exploration'], ['terrain.underground.mine', 'terrain.underground.sewer', 'terrain.wetland.swamp'], ['harm.fire.flame'], 'S4', R('verb.evade','agility','very_hard'), 'exposure',
  ['a sweetish smell of rot', 'a flame that flares bright and tall'], True, False, detect={'tier': 'moderate'},
  notes='only an open flame carried into it ignites it; a hooded lantern does not', omens=['the lantern flame leaping', 'a faint hiss in the dark'], after='thrown down the passage, burned; Down', avoid=['shutter the light', 'go dark']))
hz.append(H('haz.darkness', 'Darkness', ['situation.exploration'], ['terrain.underground'], [], 'S1', {'verb': 'none', 'attribute': None, 'dc_tier': None, 'stakes': 'risky'}, 'interval',
  ['black that the eyes cannot open', 'the sound of your own breath'], False, True, no_red=True,
  notes='not harm: 10.7.3 (cond.blinded for sight-reliant beats, crawl, site cadence one step faster, hazards unperceived); listed so retrieval finds it', avoid=['a light', 'night-sight']))
# ---------------- deprivation ----------------
hz.append(H('haz.starvation', 'Starvation', [], [], ['harm.physical'], 'S3', NONE, 'day', ['ribs showing', 'hands that shake'], True, True,
  notes='07.8.10 want: one cond.exhausted stack per day without food (h.10.supply); with three stacks the deprivation warning fires and each further stack is S3 harm, no reduction', after='found where they lay (07.6.1)', avoid=['forage', 'hunt', 'supply'], basis=['07.8.10', '10.6.2']))
hz.append(H('haz.thirst', 'Thirst', [], ['terrain.arid'], ['harm.physical'], 'S3', NONE, 'day', ['cracked lips', 'no spit to swallow'], True, True,
  notes='as starvation, counted on water: an arid day or a heat day without a water source needs +1 supply per consumer (10.6.2)', after='found where they lay', avoid=['find water', 'travel by night'], basis=['07.8.10', '10.6.2']))
# ---------------- disease vectors ----------------
hz.append(H('haz.marsh_miasma', 'Marsh miasma', ['situation.travel'], ['terrain.wetland'], ['harm.blight.disease'], 'S2', R('verb.endure','endurance','moderate'), 'day',
  ['clouds of whining midges', 'a sweet rotten smell at dusk'], False, True, aff='aff.marsh_fever',
  notes='spring and summer only; an exposure to aff.marsh_fever at its virulence tier (07.9.2)', prot=[{'means': 'smoky fires and nets at camp', 'effect': 'negate'}, {'means': 'a remedy taken (08 consumable)', 'effect': 'negate'}], avoid=['camp out of the reeds', 'smoke']))
hz.append(H('haz.foul_water', 'Foul water', [], ['terrain.wetland', 'terrain.underground.sewer'], ['harm.blight.disease'], 'S2', R('verb.endure','endurance','moderate'), 'exposure',
  ['green scum and a sour smell', 'dead fish at the margin'], False, False, aff='aff.red_flux', detect={'tier': 'easy'}, prot=[{'means': 'boiled first (an interval at a fire)', 'effect': 'negate'}], avoid=['boil it', 'find other water']))
hz.append(H('haz.barrow_air', 'Barrow air', ['situation.exploration'], ['terrain.ruin.tomb'], ['harm.blight.necrotic'], 'S2', R('verb.endure','endurance','moderate'), 'day',
  ['a cold that lingers in the stones', 'a smell of old earth and iron'], False, True, aff='aff.grave_chill', notes='a night spent inside a barrow, crypt or tomb', prot=[{'means': 'sleeping outside', 'effect': 'negate'}], avoid=['sleep outside']))
hz.append(H('haz.vermin_nest', 'Vermin nest', [], ['terrain.underground.sewer', 'terrain.ruin', 'terrain.settlement.city.slum'], ['harm.blight.disease'], 'S2', R('verb.endure','endurance','moderate'), 'day',
  ['droppings everywhere', 'squeaking in the walls'], False, True, aff='aff.rat_plague', notes='a night spent among vermin', prot=[{'means': 'a camp off the floor, fire', 'effect': 'negate'}], avoid=['sleep elsewhere']))
hz.append(H('haz.spore_cloud', 'Spore cloud', ['situation.exploration'], ['terrain.underground.cave'], ['harm.venom.gas'], 'S2', R('verb.endure','endurance','moderate'), 'exposure',
  ['pale fungus in shelves on the walls', 'a fine dust that glitters in the light'], False, True, aff='aff.grey_spore',
  prot=[{'means': 'a cloth over mouth and nose', 'effect': 'step -1'}, {'means': 'not touching the growth', 'effect': 'negate'}], avoid=['go round', 'burn it from a distance']))
# ---------------- magical zones ----------------
hz.append(H('haz.desecrated_ground', 'Desecrated ground', [], [], ['harm.mind.strain'], 'S1', R('verb.endure','resolve','easy'), 'day',
  ['grass grey in a ring', 'a shrine defaced with filth'], False, False, detect={'tier': 'easy', 'note': 'deed.lore.religion lever'},
  notes='a dread exposure (07.11.2) at S1 per day spent there; divine workings take 05\'s Precision snag; the place carries the fact desecrated', avoid=['leave', 'consecrate (rit.consecrate_ground, 05)'], basis=['05.7.2', '07.11.2', '10.12.8']))
hz.append(H('haz.dead_ground', 'Dead ground', [], [], [], 'S1', {'verb': 'none', 'attribute': None, 'dc_tier': None, 'stakes': 'safe'}, 'interval',
  ['no insect, no bird, no wind', 'iron-grey earth where nothing grows'], False, False, detect={'tier': 'moderate', 'note': 'a primal caster feels it at once'},
  notes='no harm: the fact dead_ground makes primal workings G4 here (05.7.2); a breather restores no Focus here', avoid=['leave'], basis=['05.7.2', '10.12.8']))
hz.append(H('haz.wild_magic', 'Wild magic', [], [], ['harm.arcane.raw'], 'S3', R('verb.endure','resolve','hard'), 'exposure',
  ['colours slightly wrong', 'a hum in the teeth'], False, False, detect={'tier': 'moderate', 'note': 'deed.lore.arcana lever'},
  notes='each arcane or primal working cast here: the engine rolls d20; on 1-3, the caster suffers haz.arcane_surge', avoid=['do not cast', 'leave']))
hz.append(H('haz.arcane_surge', 'Arcane surge', [], [], ['harm.arcane.raw'], 'S3', R('verb.endure','resolve','hard'), 'exposure',
  ['the working twists in the hand', 'light pouring from the wrong place'], False, True, notes='triggered by haz.wild_magic', after='wakes where they fell; the working is lost'))
hz.append(H('haz.fey_crossing', 'Fey crossing', [], ['terrain.forest.deepwood.ancient'], ['harm.mind.psychic'], 'S2', R('verb.endure','resolve','moderate'), 'day',
  ['a ring of pale mushrooms', 'music just out of hearing'], False, False, detect={'tier': 'moderate'},
  notes='way-finding here is Very hard; a night asleep inside: on failure wake a day later (advance_time 1 day; every boundary runs)', avoid=['do not sleep inside the ring', 'iron (a fact) as a Protective lever']))
hz.append(H('haz.haunting', 'Haunting', [], ['terrain.ruin'], ['harm.mind.strain'], 'S2', R('verb.endure','resolve','moderate'), 'watch',
  ['footsteps where no one walks', 'cold spots and a smell of candles'], False, False, notes='a dread exposure (07.11.2) at S2 at each night watch spent there; the place carries the fact haunted', avoid=['leave before dark', 'lay the spirit (05, 15)']))
hz.append(H('haz.blight_zone', 'Blight', [], [], ['harm.blight.decay'], 'S2', R('verb.endure','endurance','moderate'), 'day',
  ['trees black and weeping', 'meat that rots overnight'], False, True, notes='supply carried spoils 1 a day; S2 harm per day exposed', avoid=['cross fast', 'leave']))
hz.append(H('haz.ward_line', 'Ward line', [], [], ['harm.arcane.force'], 'S3', R('verb.endure','resolve','hard'), 'exposure',
  ['a faint line of chalk or salt', 'the air tight as a drumskin'], False, False, detect={'tier': 'moderate', 'note': 'arcane or divine warding license lever'},
  notes='a standing ward from a rite (05): its harm and tier are the rite\'s; this entry is the default', avoid=['unweave it (05.7.7)', 'go round']))

doc = {'schema_version': 1, 'hazards': hz, 'blocks': []}
hdr = """# data/hazards.yaml
# Purpose: every environmental, deprivation, disease-vector and magical-zone hazard (10.12): severity on
#   the S1-S5 scale, harm tags, resist (verb, attribute, tier, stakes: 01's request), exposure cadence,
#   conditions or affliction, signs and omens, lethal context, whether it is perceived on sight, aftermath
#   when it puts a PC Down (07's requests), protections, pace steps, feature kind (06), ways round.
# Owner: 10-exploration-travel-sites (owner-block 13 for regional hazards, 00.17.1 Q18). Ch.07 owns what
#   harm does (07.10); the effect DC is the tier matching the severity unless dc_tier is given (00.3.8).
# Schema: data/SCHEMAS.md#hazardsyaml (id, terrain_tags, harm_tags, severity, resist, cadence, conditions,
#   omens, lethal_context) plus ch.10's optional keys: name, tags, by_band, affliction, no_reduction,
#   perceived_on_sight, detect, signs, aftermath, protections, pace_steps, feature_kind, avoid, notes.
# Cadence: exposure (once on entry/contact) | round | interval | watch | day (handlers h.10.watch_exposure,
#   h.10.site_exposure, 06's h.06.ongoing_harm in a conflict).
# Basis: [10.12] [07.10] [R4 §9 10 item 1] [R5 EX-05] [DL-10-11]
"""
yaml.safe_dump  # noqa
txt = hdr + "\n" + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120, default_flow_style=None)
open(OUT, 'w', encoding='utf-8').write(txt)
# validate
d = yaml.safe_load(open(OUT, encoding='utf-8'))
ids = [x['id'] for x in d['hazards']]
assert len(ids) == len(set(ids)), 'dup'
for x in d['hazards']:
    assert x['severity'] in ('S1','S2','S3','S4','S5'), x['id']
    assert len(x['signs']) >= 2, x['id']
print(len(ids), 'hazards ok')
