# Generates rules/data/traps.yaml (ch.10, 10.14). Content hand-authored; the script formats and validates.
import yaml, sys
OUT, DATA = sys.argv[1], sys.argv[2]
tags = {t['id'] for t in yaml.safe_load(open(f'{DATA}/tags.yaml', encoding='utf-8'))['tags']}
aff = {a['id'] for a in yaml.safe_load(open(f'{DATA}/afflictions.yaml', encoding='utf-8'))['afflictions']}
B = ['10.14', '07.3.3', '07.10', 'R5 AV-08']
TIERS = ['easy', 'moderate', 'hard', 'very_hard', 'legendary']
def tiers(start, step_every=1):
    i = TIERS.index(start); out = []
    for b in range(5):
        out.append(TIERS[min(4, i + b // step_every)])
    return out
def sev(*s): return list(s)
COND = lambda c, s='S1', d='rounds:3': {'effect_id': 'eff.apply_condition', 'params': {'condition': c, 'severity': s, 'duration': d, 'target': 'victim'}}
traps = []
def T(id, name, kind, tags_, trigger, telltale, subtle, detect, disarm_lic, disarm, resist, harm_sev, harm_tags, effects, alarm, reset, bypass, lethal, after, aff_=None, notes=None):
    e = {'id': id, 'name': name, 'kind': kind, 'tags': tags_, 'trigger': trigger, 'telltale': telltale, 'telltale_kind_by_band': ['subtle' if (subtle and int(s[1]) <= 2) else 'plain' for s in harm_sev],
         'detect': {'verb': 'verb.observe', 'attribute': 'wits', 'dc_tier_by_band': detect},
         'disarm': {'license': disarm_lic, 'verb': 'verb.handle', 'dc_tier_by_band': disarm},
         'resist': resist, 'harm': {'severity_by_band': harm_sev, 'harm_tags': harm_tags}, 'effects': effects,
         'affliction': aff_, 'alarm_ticks': alarm, 'reset': reset, 'bypass': bypass, 'lethal_context': lethal,
         'aftermath': after, 'lifecycle': 'provisional', 'basis': B}
    if notes: e['notes'] = notes
    traps.append(e)
THIEF = 'lic.training.guile_thievery'
WARD = 'lic.training.arcane_warding'
T('trap.pit', 'Covered pit', 'mechanical', ['deed.guile.thievery.traps'], 'weight on the false floor',
  'a stretch of floor cleaner than the dust around it, and a faint seam', True, tiers('easy'), THIEF, tiers('moderate'),
  {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S2', 'S2', 'S3', 'S3', 'S4'), ['harm.physical.crush'], [COND('cond.prone', 'S1', 'scene')], 0, 'manual',
  [{'method': 'jump the seam', 'verb': 'verb.exert', 'tier': 'by width: 5 ft easy, 10 ft moderate'}, {'method': 'spike the lid shut', 'verb': 'verb.handle', 'tier_delta': -1}, {'method': 'walk the edge', 'verb': 'verb.exert', 'tier': 'moderate'}],
  False, 'at the bottom of the pit (10 ft at band 1-2, 20 ft at 3-4, 40 ft at 5); climbing out is act.climb')
T('trap.spiked_pit', 'Spiked pit', 'mechanical', ['deed.guile.thievery.traps'], 'weight on the false floor',
  'bones at the bottom of a hole someone left uncovered nearby, and a matching seam here', False, tiers('moderate'), THIEF, tiers('moderate'),
  {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S2', 'S3', 'S3', 'S4', 'S4'), ['harm.physical.pierce'], [COND('cond.bleeding', 'S1', 'scene')], 0, 'manual',
  [{'method': 'jump it', 'verb': 'verb.exert', 'tier': 'moderate'}, {'method': 'bridge it with a plank or door', 'verb': 'verb.handle', 'tier': 'easy'}], True,
  'impaled at the bottom; Down until hauled out', aff_='aff.wound_rot')
T('trap.snare', 'Snare', 'natural_snare', ['deed.wilds.survival'], 'a foot in the noose', 'a bent sapling and a loop of cord half-hidden in the leaves', True,
  tiers('easy'), 'lic.training.wilds_survival', tiers('easy'), {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S1', 'S1', 'S1', 'S2', 'S2'), ['harm.physical.crush'],
  [COND('cond.restrained', 'S1', 'while:until cut free (a Handle beat, no roll with a blade)')], 0, 'manual', [{'method': 'cut it from beside', 'verb': 'verb.handle', 'tier': 'easy'}], False,
  'hanging by one ankle until cut down', notes='hunters\' and goblins\' snares; cutting free with a blade is Trivial')
T('trap.deadfall', 'Deadfall', 'natural_snare', ['deed.wilds.survival'], 'a tripline across the path', 'a heavy log or stone propped above the path on a stick', False,
  tiers('easy'), 'lic.training.wilds_survival', tiers('easy'), {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S2', 'S2', 'S3', 'S3', 'S3'), ['harm.physical.crush'],
  [COND('cond.pinned', 'S2', 'while:until lifted (Force, Moderate)')], 0, 'manual', [{'method': 'spring it with a pole', 'verb': 'verb.handle', 'tier': 'easy'}, {'method': 'step over the line', 'verb': 'verb.exert', 'tier': 'easy'}], False,
  'pinned under the weight until lifted')
T('trap.needle_lock', 'Needle lock', 'mechanical', ['deed.guile.thievery.lockpicking'], 'picking or forcing the lock without the key', 'a tiny hole beside the keyhole, rimmed with dark crust', True,
  tiers('moderate'), THIEF, tiers('moderate'), {'verb': 'verb.endure', 'attribute': 'endurance'}, sev('S1', 'S1', 'S1', 'S1', 'S1'), ['harm.venom.poison'],
  [], 0, 'automatic', [{'method': 'wear thick gloves', 'verb': 'verb.handle', 'tier_delta': -1}, {'method': 'use the key', 'verb': 'verb.handle', 'tier': 'trivial'}], False,
  'the poison runs its stages (07.9)', aff_='aff.widow_venom', notes='harm is Light; what matters is the affliction (07.10.2 non-example). band 4-5 use aff.wyvern_venom')
T('trap.dart_wall', 'Dart wall', 'mechanical', ['deed.guile.thievery.traps'], 'a pressure plate in the corridor', 'rows of small holes in both walls at waist height', False,
  tiers('moderate'), THIEF, tiers('moderate'), {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S1', 'S2', 'S2', 'S3', 'S3'), ['harm.physical.pierce'], [], 0, 'automatic',
  [{'method': 'crawl below the holes', 'verb': 'verb.exert', 'tier': 'easy'}, {'method': 'plug the holes', 'verb': 'verb.handle', 'tier': 'moderate'}, {'method': 'trigger it with a thrown weight', 'verb': 'verb.handle', 'tier': 'easy'}], False,
  'lies stuck with darts in the corridor', aff_='aff.adder_venom', notes='affliction only at band 3+ (poisoned darts)')
T('trap.falling_slab', 'Falling slab', 'mechanical', ['deed.guile.thievery.traps'], 'lifting a lid, crossing a threshold', 'a seam in the ceiling and a crushed skeleton under it', False,
  tiers('moderate'), THIEF, tiers('hard'), {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S2', 'S3', 'S3', 'S4', 'S5'), ['harm.physical.crush'], [COND('cond.pinned', 'S2', 'while:until lifted (Force, Hard)')], 0, 'once',
  [{'method': 'wedge the slab', 'verb': 'verb.handle', 'tier_delta': -1}, {'method': 'trip it from outside its fall', 'verb': 'verb.handle', 'tier': 'easy'}], True,
  'pinned under the slab; Down until lifted by others or a Force beat (Hard)')
T('trap.collapsing_stair', 'Collapsing stair', 'mechanical', ['deed.lore.engineering.structures'], 'weight on the middle steps', 'steps worn hollow and cracked, with fresh grit below', True,
  tiers('easy'), 'lic.training.lore_engineering', tiers('moderate'), {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S2', 'S2', 'S3', 'S3', 'S4'), ['harm.physical.crush'],
  [COND('cond.prone', 'S1', 'scene')], 0, 'once', [{'method': 'climb the outside', 'verb': 'verb.exert', 'tier': 'moderate'}, {'method': 'cross one at a time, light', 'verb': 'verb.evade', 'tier_delta': -1}], False,
  'falls with the stair to the floor below (the height recorded)')
T('trap.scything_blade', 'Scything blade', 'mechanical', ['deed.guile.thievery.traps'], 'a tripwire at shin height', 'a curved groove cut in both walls and a dark stain on the floor', False,
  tiers('moderate'), THIEF, tiers('hard'), {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S2', 'S3', 'S3', 'S4', 'S4'), ['harm.physical.cut'], [COND('cond.bleeding', 'S1', 'scene')], 0, 'automatic',
  [{'method': 'step over the wire', 'verb': 'verb.exert', 'tier': 'easy'}, {'method': 'jam the blade in its groove', 'verb': 'verb.force', 'tier_delta': -1}], True, 'lies bleeding in the corridor')
T('trap.falling_portcullis', 'Falling portcullis', 'mechanical', ['deed.lore.engineering.mechanisms'], 'passing the gate\'s plate', 'grooves in the door jambs and spikes in the arch above', False,
  tiers('easy'), THIEF, tiers('hard'), {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S3', 'S3', 'S4', 'S4', 'S4'), ['harm.physical.pierce'], [], 2, 'manual',
  [{'method': 'wedge the grooves', 'verb': 'verb.handle', 'tier_delta': -1}, {'method': 'dash through', 'verb': 'verb.move', 'tier': 'moderate'}], True,
  'on the far side of the bars or beneath them; the way is barred (a barrier, Force Very hard; the winch elsewhere)', notes='splits a party; alarm 2')
T('trap.murder_hole', 'Murder hole', 'mechanical', ['deed.martial.tactics'], 'defenders above see intruders below', 'holes in the vault above a gate passage, blackened', False,
  tiers('easy'), 'none (it is manned: deal with the defenders)', tiers('easy'), {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S2', 'S2', 'S3', 'S3', 'S4'), ['harm.fire.heat'], [COND('cond.burning', 'S1', 'rounds:2')], 2, 'automatic',
  [{'method': 'shields overhead', 'verb': 'verb.evade', 'tier_delta': -1}, {'method': 'climb to the room above', 'verb': 'verb.exert', 'tier': 'hard'}], False, 'scalded in the passage', notes='fires only while a defender is above; each defender beat is one firing')
T('trap.alarm_line', 'Alarm line', 'alarm', ['deed.guile.stealth'], 'a cord across the way', 'a thin line at ankle height running to a cluster of bells or pans', True,
  tiers('easy'), THIEF, tiers('easy'), {'verb': 'none', 'attribute': None}, sev('S1', 'S1', 'S1', 'S1', 'S1'), [], [], 2, 'manual',
  [{'method': 'step over it', 'verb': 'verb.exert', 'tier': 'easy'}, {'method': 'muffle the bells', 'verb': 'verb.handle', 'tier': 'easy'}], False, None, notes='harms no one: the danger clock +2; in a fortified site the next E face is an arrival')
T('trap.alarm_ward', 'Alarm ward', 'magical', ['deed.arcane.warding'], 'a living thing crossing the line', 'a faint chalk or salt line across the threshold', True,
  tiers('moderate'), WARD, tiers('moderate'), {'verb': 'none', 'attribute': None}, sev('S1', 'S1', 'S1', 'S1', 'S1'), [], [], 3, 'automatic',
  [{'method': 'unweave it', 'verb': 'verb.handle', 'tier': 'by license (05.7.7)'}, {'method': 'cross without touching the ground (climb, jump the line)', 'verb': 'verb.exert', 'tier': 'moderate'}], False, None,
  notes='harms no one: the danger clock +3; the warder knows')
T('trap.curse_glyph', 'Curse glyph', 'magical', ['deed.arcane.warding'], 'reading it, touching it, or crossing it', 'a rune in the floor or on a lid, half-hidden under soot', True,
  tiers('moderate'), WARD, tiers('hard'), {'verb': 'verb.endure', 'attribute': 'resolve'}, sev('S1', 'S2', 'S2', 'S3', 'S3'), ['harm.arcane.force'], [], 1, 'automatic',
  [{'method': 'do not read it aloud; cover it', 'verb': 'verb.handle', 'tier': 'easy'}, {'method': 'deface it', 'verb': 'verb.force', 'tier_delta': 0}], False,
  'the curse runs its course (07.9.7)', aff_='aff.evil_eye')
T('trap.flame_jet', 'Flame jet', 'magical', ['deed.arcane.fire'], 'a pressure plate or a word', 'scorch marks fanning across floor and ceiling', False,
  tiers('moderate'), WARD, tiers('hard'), {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S2', 'S3', 'S3', 'S4', 'S5'), ['harm.fire.flame'], [COND('cond.burning', 'S1', 'rounds:3')], 1, 'automatic',
  [{'method': 'soak cloaks and run it', 'verb': 'verb.move', 'tier_delta': -1}, {'method': 'trigger it from afar', 'verb': 'verb.handle', 'tier': 'easy'}], True, 'lies burned in the passage')
T('trap.flooding_room', 'Flooding room', 'mechanical', ['deed.lore.engineering.waterworks'], 'the door closing behind, or a lever pulled', 'a high-water stain on all four walls and a grate in the ceiling', False,
  tiers('moderate'), 'lic.training.lore_engineering', tiers('hard'), {'verb': 'verb.exert', 'attribute': 'might'}, sev('S2', 'S2', 'S3', 'S3', 'S4'), ['harm.physical.asphyxia'], [], 1, 'manual',
  [{'method': 'wedge the door open', 'verb': 'verb.handle', 'tier': 'easy'}, {'method': 'swim up to the grate', 'verb': 'verb.exert', 'tier': 'hard'}], True,
  'the water fills over 3 rounds; then breath (07.10.4); a progress clock of 4 to force the door from inside')
T('trap.gas_vent', 'Gas vent', 'mechanical', ['deed.guile.poisoncraft'], 'opening a chest or a door', 'a greenish crust around small vents near the hinges', True,
  tiers('moderate'), THIEF, tiers('moderate'), {'verb': 'verb.endure', 'attribute': 'endurance'}, sev('S1', 'S1', 'S2', 'S2', 'S3'), ['harm.venom.gas'], [COND('cond.choking', 'S1', 'rounds:2')], 0, 'once',
  [{'method': 'hold your breath and open it from arm\'s length', 'verb': 'verb.endure', 'tier_delta': -1}, {'method': 'block the vents', 'verb': 'verb.handle', 'tier': 'easy'}], False,
  'wakes groggy where they fell', aff_='aff.drowse')
T('trap.net', 'Weighted net', 'mechanical', ['deed.guile.ambush'], 'a tripline, often with watchers', 'a bulge in the ceiling cloth or branches, and a line to it', True,
  tiers('easy'), THIEF, tiers('easy'), {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S1', 'S1', 'S1', 'S1', 'S1'), [], [COND('cond.restrained', 'S2', 'while:until cut free (Handle, Easy with a blade)')], 1, 'manual',
  [{'method': 'cut the line', 'verb': 'verb.handle', 'tier': 'easy'}], False, 'netted until cut free or until the setters come', notes='often a capture trap: its setters are a pending threat (an ambush row)')
T('trap.rolling_stone', 'Rolling stone', 'mechanical', ['deed.lore.engineering.mechanisms'], 'taking the thing from the altar', 'a sloped corridor with a groove worn down its center', False,
  tiers('hard'), THIEF, tiers('very_hard'), {'verb': 'verb.evade', 'attribute': 'agility'}, sev('S3', 'S3', 'S4', 'S4', 'S5'), ['harm.physical.crush'], [COND('cond.prone', 'S1', 'scene')], 2, 'once',
  [{'method': 'replace the weight (a sack of sand)', 'verb': 'verb.handle', 'tier': 'hard'}, {'method': 'run for the side passage', 'verb': 'verb.move', 'tier': 'moderate'}], True,
  'crushed against the far wall; Down', notes='a chase: the stone is a pursuit clock of 4 that the fleer races to a side passage')
T('trap.crushing_ceiling', 'Crushing ceiling', 'mechanical', ['deed.lore.engineering.mechanisms'], 'the door closing and a plate in the center', 'a ceiling of one great block, and walls scored by its edges', False,
  tiers('hard'), THIEF, tiers('very_hard'), {'verb': 'verb.exert', 'attribute': 'might'}, sev('S3', 'S4', 'S4', 'S5', 'S5'), ['harm.physical.crush'], [], 2, 'automatic',
  [{'method': 'brace it with a beam or the iron bar', 'verb': 'verb.force', 'tier_delta': -1}, {'method': 'force the door', 'verb': 'verb.force', 'tier': 'hard'}], True,
  'a progress clock of 4 (getting out) races the ceiling\'s countdown of 4; caught: Down in the gap, pinned', notes='band 5 entry is the 10.14.6 reference (S5, Legendary disarm)')

doc = {'schema_version': 1, 'traps': traps,
  'ways': [
    {'id': 'disarm', 'verb': 'verb.handle', 'license': 'the trap\'s disarm.license', 'dc': 'disarm tier', 'success': 'disarmed; salvage possible (08.6.8)', 'failure': 'cost (time or footing); critical failure: it fires on the disarmer'},
    {'id': 'jam', 'verb': 'verb.handle | verb.force', 'license': None, 'dc': 'disarm tier - 1 rung (min easy)', 'success': 'jammed for the scene', 'failure': 'as disarm; a forced jam is trait.sense.loud'},
    {'id': 'spring_from_afar', 'verb': 'verb.handle | verb.strike', 'license': None, 'dc': 'easy (moderate for a plate needing heavy weight)', 'success': 'fires harmlessly; spent or reset per entry', 'failure': 'does not fire'},
    {'id': 'bypass', 'verb': 'verb.exert | verb.sneak', 'license': None, 'dc': 'the obstacle\'s own tier (the entry\'s bypass rows)', 'success': 'passed; the trap remains', 'failure': 'fires on the bypasser with a Protective lever (stakes -1)'},
    {'id': 'break', 'verb': 'verb.force', 'license': None, 'dc': 'disarm tier', 'success': 'destroyed (trait.sense.loud)', 'failure': 'loud; critical failure: it fires'},
    {'id': 'understand', 'verb': 'verb.observe (Intellect) | verb.recall', 'license': None, 'dc': 'detect tier', 'success': 'trigger, effect and reset known: a Precision lever on any other way', 'failure': 'nothing learned'},
    {'id': 'use', 'verb': 'verb.setup', 'license': None, 'dc': 'the setup\'s own tier', 'success': 'a lever or fact for a later beat', 'failure': 'as setup'},
    {'id': 'avoid', 'verb': None, 'license': None, 'dc': None, 'success': 'another route, or wait for its reset', 'failure': None}],
  'springing': {'effect_dc': 'the trap\'s detect tier for its band, one rung up (cap legendary)', 'read': '01.18.3 resisted-effect table', 'alarm': 'alarm_ticks tick the site danger clock whatever the result'},
  'telltale_rule': 'every trap\'s telltale is narrated as a feature of its area when the area is first perceived; S3+ traps have plain telltales; an unperceived trap\'s harm is never lethal (07.3.5); a perceived S4+ trap raises the severity warning (07.3.3)',
  'pc_made': {'detect_tier_by_reach': {1: 'easy', 2: 'moderate', 3: 'hard', 4: 'very_hard'}, 'time': {'snare_or_alarm': 'intervals:1', 'deadfall_or_pit': 'hours:1'}, 'license': 'crude: basic verb.handle; refined: lic.training.guile_thievery or lic.training.wilds_survival (snares, deadfalls)'},
  'blocks': []}
# validation
bad = []
for t in traps:
    for g in t['tags'] + t['harm']['harm_tags']:
        if g not in tags: bad.append((t['id'], g))
    if t['affliction'] and t['affliction'] not in aff: bad.append((t['id'], t['affliction']))
    assert len(t['harm']['severity_by_band']) == 5 and len(t['detect']['dc_tier_by_band']) == 5
    top = max(int(s[1]) for s in t['harm']['severity_by_band'])
    for k, s in zip(t['telltale_kind_by_band'], t['harm']['severity_by_band']):
        assert not (int(s[1]) >= 3 and k == 'subtle'), t['id']
print('bad', bad)
hdr = """# data/traps.yaml
# Purpose: traps (10.14): trigger, telltale (the no-gotcha rule, 10.14.3), detection and disarm tiers by
#   site band, the victim's resisted check, harm by band, effects and afflictions, alarm ticks on the site's
#   danger clock, reset, ways round (bypass rows), lethal context, aftermath; plus the eight ways of dealing
#   with a perceived trap (T-10-19), the springing rule, and PC-made traps.
# Owner: 10-exploration-travel-sites (owner-block 13 for regional traps).
# Schema: data/SCHEMAS.md#trapsyaml (id, detect {verb, dc_tier}, disarm {license, dc_tier}, trigger, harm
#   {severity, harm_tags}, effects) with ch.10's band-indexed forms dc_tier_by_band and severity_by_band
#   (index 0 = band 1) and optional keys kind, telltale, telltale_kind_by_band (subtle only where the band's harm is S1-S2), resist, affliction, alarm_ticks,
#   reset, bypass, lethal_context, aftermath, notes; top-level ways, springing, telltale_rule, pc_made.
# Basis: [10.14] [07.3.3, 07.10] [R5 AV-08] [R1 §07 traps that always counter the players] [DL-10-17]
"""
txt = hdr + "\n" + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120, default_flow_style=None)
open(OUT, 'w', encoding='utf-8').write(txt)
yaml.safe_load(open(OUT, encoding='utf-8'))
print(len(traps), 'traps')
