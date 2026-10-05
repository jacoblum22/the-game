# Generates rules/data/travel.yaml (ch.10). Content hand-authored; the script formats, validates every
# id, and audits the generic encounter tables against 10.10.2 (bands 30/55/15 among threat rows;
# non-threat share by rating).
import yaml, sys
OUT, DATA = sys.argv[1], sys.argv[2]
tags = {t['id'] for t in yaml.safe_load(open(f'{DATA}/tags.yaml', encoding='utf-8'))['tags']}
archs = {a['id']: a for a in yaml.safe_load(open(f'{DATA}/archetypes.yaml', encoding='utf-8'))['archetypes']}
haz = {h['id'] for h in yaml.safe_load(open(f'{DATA}/hazards.yaml', encoding='utf-8'))['hazards']}
B = ['10.3', '10.9', '10.10']
def rows(items):
    out = []
    for i, it in enumerate(items, 1):
        r = {'range': str(i)}
        r.update(it if isinstance(it, dict) else {'result': it})
        out.append(r)
    return out

rings = [
  {'ring': 0, 'distance': 'the haven and its fields', 'home_band': None, 'danger': 'safe', 'words': 'safe under the walls'},
  {'ring': 1, 'distance': 'up to 1 day', 'home_band': [1], 'danger': 'settled', 'words': 'farm country; trouble is rare and small'},
  {'ring': 2, 'distance': '1-3 days', 'home_band': [1, 2], 'danger': 'wild', 'words': 'the borderland: wild, but folk pass through'},
  {'ring': 3, 'distance': '3-6 days', 'home_band': [2, 3], 'danger': 'wild or perilous', 'words': 'the deep wilds: dangerous things live here'},
  {'ring': 4, 'distance': '6-10 days', 'home_band': [3, 4], 'danger': 'perilous', 'words': 'the old lands: only the strong travel here'},
  {'ring': 5, 'distance': 'beyond', 'home_band': [4, 5], 'danger': 'deadly', 'words': 'the far reaches: legends live here, and so do the things that killed them'},
]
pace = {
  'points_per_leg_watch': 6,
  'ladder': [{'id': 'crawl', 'points': 2}, {'id': 'slow', 'points': 4}, {'id': 'normal', 'points': 6}, {'id': 'fast', 'points': 8}, {'id': 'ride', 'points': 9}, {'id': 'hard_ride', 'points': 12}],
  'chosen': {'walkers': {'slow': 'slow', 'normal': 'normal', 'fast': 'fast'}, 'riders': {'slow': 'normal', 'normal': 'ride', 'fast': 'hard_ride'}},
  'base_by_travel_pace': {'walk': 'normal (max normal for walk-pace mounts and carts)', 'ride': 'ride ladder for an all-mounted party', 'river': 'vessel_pace', 'sea': 'vessel_pace'},
  'steps': [
    {'cause': 'burdened (08.9.2)', 'steps': 1}, {'cause': 'overloaded (08.9.2)', 'steps': 'no travel'},
    {'cause': 'weather off roads', 'steps': 'weather.yaml#states[].pace_steps'}, {'cause': 'snow_lying off roads', 'steps': 1},
    {'cause': 'night (evening, night watches) without road, light or clear sky', 'steps': 1}, {'cause': 'a slowing hazard on the leg', 'steps': 'hazards.yaml pace_steps'},
    {'cause': 'darkness without light or night-sight', 'steps': 'crawl'}],
  'effects': [
    {'pace': 'slow', 'march_units': 1, 'roles': [navigator, lookout, scout, forager] if False else ['navigator', 'lookout', 'scout', 'forager'], 'way_lever': True, 'stealth': 'a party Sneak may be made'},
    {'pace': 'normal', 'march_units': 1, 'roles': ['navigator', 'lookout', 'scout']},
    {'pace': 'fast', 'march_units': 2, 'roles': ['navigator'], 'way_snag': True},
    {'pace': 'ride', 'march_units': 1, 'roles': ['navigator', 'lookout', 'scout'], 'mount_units': 1},
    {'pace': 'hard_ride', 'march_units': 1, 'roles': ['navigator'], 'way_snag': True, 'mount_units': 2}],
}
vessel_pace = [
  {'vessel': 'bi.raft', 'calm': None, 'downstream': 8, 'upstream': None, 'sea': None, 'watches_per_day': 2},
  {'vessel': 'bi.rowboat', 'calm': 6, 'downstream': 8, 'upstream': 4, 'sea': 'coast only, 4 in calm weather', 'watches_per_day': 2},
  {'vessel': 'bi.keelboat', 'calm': 6, 'downstream': 9, 'upstream': 6, 'sea': None, 'watches_per_day': 3},
  {'vessel': 'bi.river_barge', 'calm': 6, 'downstream': 8, 'upstream': 4, 'sea': None, 'watches_per_day': 3},
  {'vessel': 'bi.cog', 'calm': None, 'downstream': None, 'upstream': None, 'sea': 16, 'watches_per_day': 4},
]
march = {'walker_allowance': 2, 'mount_allowance': 2, 'reset': 'day boundary (dawn)', 'unit_cost': {'slow': 1, 'normal': 1, 'fast': 2, 'ride': 1, 'hard_ride': 2},
         'mount_loaded_over_half': '+1 per watch', 'over_allowance': 'one stack of cond.exhausted per unit over, at the watch end (h.10.travel_progress); 07.8.10 push-on may defer it',
         'mount_at_three_stacks': 'cannot be ridden or loaded until a long rest'}
watch_activities = rows([
  {'id': 'travel', 'result': 'move along the journey: earn pace points (h.10.travel_progress)', 'rest': False},
  {'id': 'camp', 'result': 'make and keep camp: eat, tend gear, mounts graze; a lookout may watch; the rest site is set (07.8.2)', 'rest': 'rest_short possible inside it'},
  {'id': 'sleep', 'result': 'a long rest (07.8.1: a watch, at least 4 hours asleep, once a day)', 'rest': 'rest_long'},
  {'id': 'forage', 'result': 'act.forage (10.6.4)', 'rest': False},
  {'id': 'hunt', 'result': 'act.hunt / act.fish (10.6.5)', 'rest': False},
  {'id': 'scout', 'result': 'act.scout an adjacent area (10.15)', 'rest': False},
  {'id': 'map', 'result': 'act.map the area (a way-finding lever)', 'rest': False},
  {'id': 'rest', 'result': 'rest without sleeping (short rests, 07.8.1)', 'rest': 'rest_short'},
  {'id': 'keep_watch', 'result': 'the lookout role over a resting camp', 'rest': False},
  {'id': 'other', 'result': 'any listed activity with a duration of a watch or less, or a free-mode scene', 'rest': False}])
roles = [
  {'id': 'navigator', 'allowed_at': ['slow', 'normal', 'fast', 'ride', 'hard_ride'], 'effect': 'makes the day\'s way-finding beat (10.4.2)', 'evidence_tag': 'deed.wilds.navigation.wayfinding'},
  {'id': 'lookout', 'allowed_at': ['slow', 'normal', 'ride', 'camp'], 'effect': 'arrivals never surprise the party; distance +1 band in open and broken country; omens carry the archetype family; sleepers woken in time', 'evidence_tag': 'deed.wilds.survival.weathersense'},
  {'id': 'scout', 'allowed_at': ['slow', 'normal', 'ride'], 'effect': 'perceives arrivals first (other side unaware unless its notice beats the scout\'s stored Sneak); may slip away; on a discovery face finds the nearest undiscovered site or landmark; starts encounters at band.far from the party', 'evidence_tag': 'deed.wilds.tracking.sign'},
  {'id': 'forager', 'allowed_at': ['slow'], 'effect': 'a forage beat at the watch end with an engine-cited Precision snag "on the move", yield delivered reach - 1', 'evidence_tag': 'deed.wilds.foraging.food'},
]
watch_check = {
  'die': 'd12', 'handler': 'h.10.watch_check', 'boundary': 'watch', 'phase': 7, 'night_watch_rung': '+1 (cap deadly)',
  'faces': {
    'settled': {'E': '1', 'O': '2', 'V': '3', 'D': '4', 'W': '5', 'F': '6', 'P': '7', 'L': '8-12'},
    'wild': {'E': '1', 'O': '2-3', 'V': '4', 'D': '5', 'W': '6', 'F': '7', 'P': '8', 'L': '9-12'},
    'perilous': {'E': '1-2', 'O': '3-4', 'V': '5', 'D': '6', 'W': '7', 'F': '8', 'P': '9', 'L': '10-12'},
    'deadly': {'E': '1-3', 'O': '4-5', 'V': '6', 'D': '7', 'W': '8', 'F': '9', 'P': '10', 'L': '11-12'}},
  'meanings': {'E': 'encounter (10.9.4)', 'O': 'omen', 'V': 'local event: tbl.<region>.events else tbl.event_focus (12.6.5 d)', 'D': 'depletion: tbl.10.depletion', 'W': 'weather shift: tbl.10.weather_shift',
               'F': 'discovery: nearest undiscovered place, else tbl.10.find', 'P': 'opportunity: tbl.10.opportunity', 'L': 'lull: +1 point if travelling; pending timer does not advance'},
  'threat_share_d12': {'settled': '1-3', 'wild': '1-7', 'perilous': '1-9', 'deadly': '1-10', 'rule': 'an E or O face with nothing pending first rolls d12 against the rating: on the range, the threat sub-table; else the non-threat sub-table'},
  'interrupting_results': ['arrival', 'omen', 'local event perceivable now', 'weather shift into an exposure for the exposed', 'a recurring hazard exposure'],
}
site_check = {
  'die': 'd12', 'handler': 'h.10.site_check', 'boundary': 'interval', 'phase': 7,
  'cadence_intervals': {'settled': 3, 'wild': 2, 'perilous': 2, 'deadly': 1, 'dark_without_light': 'one step faster', 'roused': 'every interval, rating +1'},
  'faces': {
    'settled': {'E': '1', 'O': '2', 'S': '3', 'D': '4', 'H': '5', 'F': '6', 'P': '7', 'L': '8-12'},
    'wild': {'E': '1', 'O': '2-3', 'S': '4', 'D': '5', 'H': '6', 'F': '7', 'P': '8', 'L': '9-12'},
    'perilous': {'E': '1-2', 'O': '3-4', 'S': '5-6', 'D': '7', 'H': '8', 'F': '9', 'P': '10', 'L': '11-12'},
    'deadly': {'E': '1-2', 'O': '3-5', 'S': '6-7', 'D': '8', 'H': '9', 'F': '10', 'P': '11', 'L': '12'}},
  'meanings': {'E': 'denizen encounter (site table)', 'O': 'omen', 'S': 'stir: the danger clock +1', 'D': 'depletion (site rows)', 'H': 'shift: the domain\'s shift table', 'F': 'discovery: theme/domain discoveries', 'P': 'tbl.10.site_opportunity', 'L': 'lull'},
}
pending = {'record': '{id, row, adversary_refs, count, sign_stage, checks_since, created_at, place}', 'arrives': ['the next E face', 'the next O face (second sign, then arrival)', 'the 4th check after creation (lulls do not count)'],
           'relax_opt_in': 'during 12\'s RELAX or a recovery window the 4th-check timer does not run (10.9.7)', 'one_at_a_time': True,
           'answers': ['avoid', 'investigate', 'prepare', 'seek', 'ignore']}
tables = [
  {'id': 'tbl.10.depletion', 'name': 'Depletion (face D, travel)', 'die': 'd6', 'results': rows([
     'one supply spoils or is spilled (-1); if none carried, a waterskin leaks: no water source this day in arid country',
     'one supply spoils or is spilled (-1); if none carried, a waterskin leaks: no water source this day in arid country',
     'a burning light gutters (-2 intervals); if none is lit, one stored source is found damp and loses half its remaining intervals, rounded down',
     'a strap, string or boot gives: one carried item (engine draw among non-relic, non-cost_immune gear) is damaged (08.1.9)',
     'a mount goes lame for the day (pace one step slower); if no mount, ammunition -2',
     'a hard stretch: the next travel watch earns 2 fewer points'])},
  {'id': 'tbl.10.depletion_site', 'name': 'Depletion (face D, site)', 'die': 'd6', 'results': rows([
     'a burning light gutters (-2 intervals)', 'a burning light gutters (-2 intervals)', 'one supply spoils in the damp (-1)', 'a strap or string gives: one carried item damaged',
     'a rope or pole frays (one damaged)', 'the air turns bad for a moment: a burning light -2 intervals'])},
  {'id': 'tbl.10.find', 'name': 'A find (face F with nothing undiscovered)', 'die': 'd12', 'results': rows([
     {'result': 'a spring', 'writes': 'landmark; water_source for the area'}, {'result': 'a waymark cairn', 'writes': 'landmark; a way-finding lever in this area'},
     {'result': 'an old campsite', 'writes': 'a camp rest site with a fire ring'}, {'result': 'a roadside shrine', 'writes': 'landmark; resonance per 13 or an Oracle question'},
     {'result': 'a cache', 'writes': '08.3.12 hoard at band - 1, coin and goods only'}, {'result': 'a fallen statue', 'writes': 'landmark; lore (act.study)'},
     {'result': 'a carcass worth harvesting', 'writes': 'a fresh body of a beast of the area\'s table (08.3.10)'}, {'result': 'a wreck or abandoned cart', 'writes': 'act.scavenge: 08.3.11 gear and coin by band'},
     {'result': 'a signpost', 'writes': 'a known link: a route name and direction (a known route link)'}, {'result': 'fresh sign of passage', 'writes': 'a track link; act.track Easy to follow'},
     {'result': 'a viewpoint', 'writes': 'a vantage: adjacent areas\' danger words; recognition if lost'}, {'result': 'a lone grave', 'writes': 'landmark; a name (a rumor seed for 11)'}])},
  {'id': 'tbl.10.opportunity', 'name': 'Opportunity (face P, travel)', 'die': 'd8', 'results': rows([
     'windfall: +1 supply', 'game sighted: a Precision lever for a hunt in this area today', 'a better line: +2 points to the next travel watch',
     'shelter found: the next camp in this area is camp, not rough, and keeps out S2 weather', 'a vantage: adjacent areas\' danger words, the nearest undiscovered landmark, recognition if lost',
     'others\' trail marks: a Precision lever on way-finding today', 'water: a water_source for the day', 'a quiet hour: a breather boundary at the watch end'])},
  {'id': 'tbl.10.veer', 'name': 'Veer when off course (10.4.6)', 'die': 'd6', 'results': rows([
     'the link nearest the intended bearing on its left', 'the link nearest the intended bearing on its left', 'the link nearest the intended bearing on its right',
     'the link nearest the intended bearing on its right', 'a link back the way the party came', 'circling: no link; the watch\'s points go nowhere'])},
  {'id': 'tbl.10.encounter_distance', 'name': 'Encounter distance (T-10-15)', 'die': 'd6',
   'by_openness': {'open': ['band.near', 'band.near', 'band.far', 'band.far', 'band.distant', 'band.distant'],
                   'broken': ['band.close', 'band.near', 'band.near', 'band.far', 'band.far', 'band.distant'],
                   'closed': ['band.close', 'band.close', 'band.close', 'band.near', 'band.near', 'band.far']},
   'modifiers': ['lookout: +1 band farther (open, broken)', 'scout: +1 band farther', 'fog or night without light: read as closed', 'ambush rows: the ambush ground\'s distance (usually band.close)']},
]
# ---- terrain defaults (T-10-12) ----
def TD(nav, forage, game, openness, grazing, water):
    return {'nav_tier': nav, 'forage_tier': dict(zip(['spring', 'summer', 'autumn', 'winter'], forage)), 'game_tier': game, 'openness': openness, 'grazing': grazing, 'water_source': water}
terrain_defaults = {
  'terrain.settlement': TD('easy', ['none'] * 4, 'none', 'broken', False, True),
  'terrain.road': TD('easy', ['moderate', 'easy', 'easy', 'hard'], 'moderate', 'broken', True, 'oracle_likely'),
  'terrain.forest.woodland': TD('easy', ['moderate', 'easy', 'easy', 'hard'], 'easy', 'broken', True, True),
  'terrain.forest.deepwood': TD('moderate', ['moderate', 'easy', 'easy', 'hard'], 'easy', 'closed', False, True),
  'terrain.forest.jungle': TD('hard', ['easy', 'easy', 'easy', 'moderate'], 'moderate', 'closed', False, True),
  'terrain.highland.hills': TD('easy', ['moderate', 'moderate', 'easy', 'hard'], 'moderate', 'broken', True, True),
  'terrain.highland.mountains': TD('hard', ['hard', 'hard', 'hard', 'very_hard'], 'hard', 'broken', False, True),
  'terrain.highland.cliffs': TD('moderate', ['hard', 'hard', 'hard', 'very_hard'], 'hard', 'open', False, 'oracle_even'),
  'terrain.plains.grassland': TD('easy', ['moderate', 'easy', 'easy', 'hard'], 'easy', 'open', True, 'oracle_likely'),
  'terrain.plains.farmland': TD('easy', ['easy', 'easy', 'easy', 'moderate'], 'moderate', 'broken', True, True),
  'terrain.plains.moor': TD('easy', ['moderate', 'moderate', 'moderate', 'hard'], 'moderate', 'open', True, True),
  'terrain.wetland.marsh': TD('moderate', ['moderate', 'easy', 'easy', 'hard'], 'moderate', 'open', True, True),
  'terrain.wetland.swamp': TD('hard', ['moderate', 'moderate', 'moderate', 'hard'], 'moderate', 'closed', False, True),
  'terrain.wetland.fen': TD('moderate', ['moderate', 'moderate', 'moderate', 'hard'], 'moderate', 'open', False, True),
  'terrain.arid.desert': TD('hard', ['very_hard'] * 4, 'hard', 'open', False, False),
  'terrain.arid.badlands': TD('moderate', ['hard', 'hard', 'hard', 'hard'], 'hard', 'broken', False, False),
  'terrain.frozen.tundra': TD('moderate', ['hard', 'moderate', 'hard', 'very_hard'], 'moderate', 'open', True, 'with_fire'),
  'terrain.frozen.glacier': TD('very_hard', ['none'] * 4, 'very_hard', 'open', False, 'with_fire'),
  'terrain.frozen.snowfield': TD('hard', ['very_hard'] * 4, 'hard', 'open', False, 'with_fire'),
  'terrain.water.river': TD('easy', ['easy'] * 4, 'easy', 'open', False, True),
  'terrain.water.lake': TD('easy', ['easy'] * 4, 'moderate', 'open', False, True),
  'terrain.water.coast': TD('moderate', ['easy', 'easy', 'easy', 'moderate'], 'moderate', 'open', False, False),
  'terrain.water.sea': TD('very_hard', ['none'] * 4, 'hard', 'open', False, False),
  'terrain.underground.cave': TD('hard', ['hard'] * 4, 'very_hard', 'closed', False, 'oracle_even'),
  'terrain.underground.mine': TD('moderate', ['very_hard'] * 4, 'none', 'closed', False, 'oracle_unlikely'),
  'terrain.underground.tunnel': TD('hard', ['very_hard'] * 4, 'none', 'closed', False, 'oracle_unlikely'),
  'terrain.underground.sewer': TD('moderate', ['hard'] * 4, 'none', 'closed', False, 'foul'),
  'terrain.ruin': TD('moderate', ['hard'] * 4, 'hard', 'broken', False, 'oracle_even'),
}
terrain_defaults_rule = ('a place takes the entry of its primary terrain tag, else its nearest ancestor with an entry (00.5.4b most-specific-wins). '
  'forage_tier "none" = G4 for foraging (nothing grows); game_tier "none" = G4 for hunting. water_source: true / false / foul (haz.foul_water) / with_fire (melting snow at a fire) / oracle_<rung> (ask once per area, 00.12.7). '
  'grazing applies spring to autumn only.')
# ---- generic encounter tables: threat sub-table d20 (rows by relative band) and non-threat d6 ----
def TR(r, ref, band, count, ambush=False, complication=False, when='any', note=None):
    d = {'range': r, 'kind': 'adversary', 'ref': [ref], 'band': band, 'count': count, 'threat': True, 'ambush': ambush, 'complication': complication, 'when': when}
    if note: d['note'] = note
    return d
def NT(r, text, kind='people', ref=None):
    d = {'range': r, 'kind': kind, 'result': text, 'threat': False}
    if ref: d['ref'] = [ref]
    return d
enc = {}
enc['terrain.road'] = {'threat': [TR('1-3', 'arch.brigand', 'home-1', 'group', ambush=True, note='footpads at a narrows'), TR('4-6', 'arch.wolf', 'home-1', 'group'),
   TR('7-10', 'arch.brigand', 'home', 'group', complication=True, note='highwaymen with a captain'), TR('11-12', 'arch.soldier', 'home', '2-4', note='deserters or corrupt toll-men'),
   TR('13-14', 'arch.orc', 'home', 'group', note='raiders on the road'), TR('15-17', 'arch.goblin', 'home', 'group', ambush=True), TR('18-19', 'arch.ogre', 'home+1', '1'), TR('20', 'arch.troll', 'home+1', '1', note='under a bridge')],
  'non_threat': [NT('1', 'merchants with hired guards (12.11 reaction roll; trade)'), NT('2', 'pilgrims bound for a shrine (news; a rumor)'), NT('3', 'a patrol of the road wardens (reaction roll; questions)', 'people', 'arch.soldier'),
   NT('4', 'a messenger riding hard (news: a rumor from 11)'), NT('5', 'a tinker with a cart (trade; repair)'), NT('6', 'refugees from somewhere worse (a thread seed)')]}
enc['terrain.settlement'] = {'threat': [TR('1-4', 'arch.brigand', 'home-1', '2-4', ambush=True, note='footpads in an alley', when='night'), TR('5-6', 'arch.wolf', 'home-1', 'group', note='a stray dog pack'),
   TR('7-10', 'arch.brigand', 'home', 'group', note='a gang\'s thugs'), TR('11-13', 'arch.cultist', 'home', 'group', when='night'), TR('14-17', 'arch.ghoul', 'home', 'group', when='night', note='from the old graveyard'),
   TR('18-20', 'arch.hag', 'home+1', '1', when='night')],
  'non_threat': [NT('1', 'townsfolk at their business (a rumor)'), NT('2', 'a beggar with news for a coin'), NT('3', 'the watch on its round'), NT('4', 'a merchant with something unusual to sell'), NT('5', 'a drunk spoiling for an argument (talk, not a fight)'), NT('6', 'a funeral or a wedding procession')]}
enc['terrain.forest'] = {'threat': [TR('1-3', 'arch.wolf', 'home-1', 'group'), TR('4-6', 'arch.giant_vermin', 'home-1', 'group', ambush=True, note='spiders in the canopy'),
   TR('7-9', 'arch.brigand', 'home', 'group', ambush=True), TR('10-12', 'arch.wolf', 'home', 'group', complication=True), TR('13-14', 'arch.bear', 'home', '1'), TR('15-17', 'arch.wild_fey', 'home', 'group'),
   TR('18-19', 'arch.monstrous_beast', 'home+1', '1', note='an owlbear or worse'), TR('20', 'arch.troll', 'home+1', '1')],
  'non_threat': [NT('1', 'woodcutters at work'), NT('2', 'a hunter tracking game (news of the wood)'), NT('3', 'a herd of deer (game sighted)', 'beasts', 'arch.herd_beast'), NT('4', 'charcoal-burners and their mound'), NT('5', 'a hermit in a hollow tree'), NT('6', 'a druid or a warden of the wood (reaction roll)', 'people', 'arch.elf_warden')]}
enc['terrain.highland'] = {'threat': [TR('1-3', 'arch.wolf', 'home-1', 'group'), TR('4-6', 'arch.goblin', 'home-1', 'group', ambush=True), TR('7-9', 'arch.orc', 'home', 'group'),
   TR('10-11', 'arch.bear', 'home', '1'), TR('12-13', 'arch.raptor', 'home', '1-2'), TR('14-17', 'arch.ogre', 'home', '1', complication=True), TR('18-19', 'arch.giant', 'home+1', '1'), TR('20', 'arch.wyvern', 'home+1', '1')],
  'non_threat': [NT('1', 'shepherds and their flock'), NT('2', 'wild goats on a ledge (game sighted)', 'beasts', 'arch.herd_beast'), NT('3', 'dwarf traders with mules (reaction roll; trade)', 'people', 'arch.dwarf_holdguard'),
   NT('4', 'prospectors at a stream'), NT('5', 'an eagle circling: a sign of something dead ahead', 'sign_only'), NT('6', 'a cairn-builder or a pilgrim to the heights')]}
enc['terrain.plains'] = {'threat': [TR('1-3', 'arch.wolf', 'home-1', 'group'), TR('4-6', 'arch.brigand', 'home-1', 'group', note='mounted raiders'), TR('7-9', 'arch.gnoll', 'home', 'group'),
   TR('10-12', 'arch.orc', 'home', 'group', complication=True), TR('13-14', 'arch.herd_beast', 'home', 'group', note='a stampede or a bull aurochs'), TR('15-17', 'arch.monstrous_beast', 'home', '1'),
   TR('18-19', 'arch.great_cat', 'home+1', '1'), TR('20', 'arch.wyvern', 'home+1', '1')],
  'non_threat': [NT('1', 'drovers moving cattle'), NT('2', 'a caravan (trade; news)'), NT('3', 'wild horses (a mount to be caught: Handle, Hard)', 'beasts', 'arch.herd_beast'), NT('4', 'a hunting party of the local lord'), NT('5', 'a farmer at a boundary stone (directions)'), NT('6', 'travelers going the other way (news of the road behind them)')]}
enc['terrain.wetland'] = {'threat': [TR('1-3', 'arch.giant_vermin', 'home-1', 'group'), TR('4-6', 'arch.reptile', 'home-1', '1-2'), TR('7-9', 'arch.lizardfolk', 'home', 'group', ambush=True),
   TR('10-11', 'arch.zombie', 'home', 'group', note='bog-dead'), TR('12-13', 'arch.hag', 'home', '1'), TR('14-17', 'arch.water_beast', 'home', '1'), TR('18-19', 'arch.troll', 'home+1', '1'), TR('20', 'arch.monstrous_plant', 'home+1', '1')],
  'non_threat': [NT('1', 'eel-fishers in a punt'), NT('2', 'a punt-man who ferries for coin'), NT('3', 'herons rising: a sign of something moving in the reeds', 'sign_only'), NT('4', 'a hermit on a stilt-hut'), NT('5', 'lizardfolk traders (reaction roll)', 'people', 'arch.lizardfolk'), NT('6', 'a will-o\'-the-wisp leading off the path', 'sign_only')]}
enc['terrain.arid'] = {'threat': [TR('1-3', 'arch.giant_vermin', 'home-1', 'group', note='scorpions'), TR('4-6', 'arch.reptile', 'home-1', '1-2'), TR('7-9', 'arch.gnoll', 'home', 'group'),
   TR('10-12', 'arch.brigand', 'home', 'group', ambush=True, note='desert raiders'), TR('13-14', 'arch.fire_elemental', 'home', '1'), TR('15-17', 'arch.great_cat', 'home', '1'), TR('18-19', 'arch.drake', 'home+1', '1'), TR('20', 'arch.earth_elemental', 'home+1', '1')],
  'non_threat': [NT('1', 'a caravan of camels (water for coin)'), NT('2', 'nomads at a well (reaction roll)'), NT('3', 'a well-keeper'), NT('4', 'a mirage of water: a sign only', 'sign_only'), NT('5', 'pilgrims to a desert shrine'), NT('6', 'a lone wanderer, half-dead of thirst (a rescue)')]}
enc['terrain.frozen'] = {'threat': [TR('1-3', 'arch.wolf', 'home-1', 'group'), TR('4-6', 'arch.bear', 'home-1', '1'), TR('7-10', 'arch.wolf', 'home', 'group', complication=True),
   TR('11-13', 'arch.giant', 'home', '1'), TR('14-17', 'arch.frost_elemental', 'home', '1'), TR('18-19', 'arch.troll', 'home+1', '1'), TR('20', 'arch.giant', 'home+1', '1')],
  'non_threat': [NT('1', 'trappers with a sled'), NT('2', 'a reindeer herd (game sighted)', 'beasts', 'arch.herd_beast'), NT('3', 'a sled party of traders'), NT('4', 'an ice-fisher at a hole'), NT('5', 'a cairn with a message', 'sign_only'), NT('6', 'an abandoned camp, recently left', 'sign_only')]}
enc['terrain.water'] = {'threat': [TR('1-3', 'arch.water_beast', 'home-1', '1-2'), TR('4-6', 'arch.brigand', 'home-1', 'group', note='river pirates'), TR('7-10', 'arch.brigand', 'home', 'group', complication=True),
   TR('11-13', 'arch.water_elemental', 'home', '1'), TR('14-17', 'arch.lizardfolk', 'home', 'group'), TR('18-19', 'arch.water_beast', 'home+1', '1'), TR('20', 'arch.wyrm', 'home+1', '1', note='a serpent of the deep water')],
  'non_threat': [NT('1', 'fisherfolk'), NT('2', 'a ferry'), NT('3', 'a barge going downstream (passage)'), NT('4', 'merchants under sail'), NT('5', 'a drowned body: a sign', 'sign_only'), NT('6', 'seals or otters at play', 'beasts', 'arch.water_beast')]}
enc['terrain.underground'] = {'threat': [TR('1-3', 'arch.giant_vermin', 'home-1', 'group'), TR('4-6', 'arch.goblin', 'home-1', 'group', ambush=True), TR('7-9', 'arch.ooze', 'home', '1'),
   TR('10-12', 'arch.fungal', 'home', 'group'), TR('13-14', 'arch.orc', 'home', 'group'), TR('15-17', 'arch.skeleton', 'home', 'group'), TR('18-19', 'arch.aberration', 'home+1', '1'), TR('20', 'arch.drake', 'home+1', '1')],
  'non_threat': [NT('1', 'dwarf miners (reaction roll)', 'people', 'arch.dwarf_holdguard'), NT('2', 'a lost delver'), NT('3', 'blind cave fish in a pool (1 supply)', 'sign_only'), NT('4', 'myconid traders (reaction roll)', 'people', 'arch.fungal'), NT('5', 'old tool marks: a sign of a way on', 'sign_only'), NT('6', 'bats streaming toward an exit', 'sign_only')]}
enc['terrain.ruin'] = {'threat': [TR('1-3', 'arch.giant_vermin', 'home-1', 'group'), TR('4-6', 'arch.skeleton', 'home-1', 'group'), TR('7-9', 'arch.ghoul', 'home', 'group'),
   TR('10-12', 'arch.brigand', 'home', 'group', note='looters'), TR('13-14', 'arch.cultist', 'home', 'group'), TR('15-17', 'arch.ghost', 'home', '1'), TR('18-19', 'arch.wight', 'home+1', '1'), TR('20', 'arch.golem', 'home+1', '1')],
  'non_threat': [NT('1', 'scavengers picking over the stones'), NT('2', 'a scholar copying inscriptions'), NT('3', 'a pilgrim to an old altar'), NT('4', 'crows on a fresh kill: a sign', 'sign_only'), NT('5', 'a lone dog that follows'), NT('6', 'treasure-hunters with a map (rivals)')]}
encounter_tables = []
for t, d in enc.items():
    encounter_tables.append({'id': 'tbl.10.enc.' + t.split('.')[-1], 'terrain': t, 'threat_die': 'd20', 'threat': d['threat'], 'non_threat_die': 'd6', 'non_threat': d['non_threat'],
                             'lifecycle': 'provisional', 'basis': ['10.10.1', '09.8.2', 'T-09-10']})
# ---- archetype signs (omen text, stage 1 then stage 2) ----
S = {
 'arch.wolf': ['wolf scat full of hair on the trail', 'a howl answered from two directions'], 'arch.great_cat': ['claw-scores high on a tree', 'a deer carcass dragged up into a fork'],
 'arch.bear': ['a stump torn open for grubs', 'a smell of musk and the crack of a branch'], 'arch.herd_beast': ['hoofprints by the hundred', 'a rumble felt through the ground'],
 'arch.giant_vermin': ['webs across the path, thick as rope', 'husks of things sucked dry'], 'arch.vermin_swarm': ['droppings everywhere, fresh', 'a squeaking in the walls that keeps pace'],
 'arch.reptile': ['a smooth wide track through mud', 'a hiss from the reeds'], 'arch.raptor': ['a shadow crossing the sun twice', 'a carcass picked clean on a high rock'],
 'arch.water_beast': ['something large rolling under the surface', 'the water birds all lifting at once'], 'arch.monstrous_beast': ['tracks of no animal you know', 'a scream like a woman\'s, then silence'],
 'arch.brigand': ['a cold fire with too many bootprints', 'a glint from the ridge where no one should be'], 'arch.soldier': ['the tramp of marching feet', 'a discarded ration tin with a regiment\'s mark'],
 'arch.knight': ['hoofprints of a heavy horse, shod', 'a pennon seen over a rise'], 'arch.cultist': ['a symbol daubed in blood on a stone', 'chanting carried on the wind at dusk'],
 'arch.folk_mage': ['a ring of scorched grass', 'lights moving where there is no fire'], 'arch.elf_warden': ['an arrow in a tree, a warning', 'birdcalls that are not birds'],
 'arch.dwarf_holdguard': ['a stone marker in an old script', 'the sound of iron-shod boots in a gully'], 'arch.orc': ['a stake with a skull on it', 'drums at dusk, then smoke'],
 'arch.goblin': ['crude snares by the dozen', 'giggling in the dark that stops when you stop'], 'arch.gnoll': ['bones cracked for marrow', 'a hyena laugh, many voices'],
 'arch.lizardfolk': ['a fish-trap of woven reed, newly set', 'eyes at water level watching'], 'arch.ogre': ['a footprint as long as your arm', 'a tree pulled up by its roots for a club'],
 'arch.troll': ['a stench of rot from under the bridge', 'gnawed bones of a cow, and a man'], 'arch.giant': ['a boulder thrown into a field', 'the ground shaking in a slow rhythm'],
 'arch.skeleton': ['old bones scattered and then gathered', 'a clatter in the dark, rhythmic'], 'arch.zombie': ['a smell of the grave on the wind', 'a figure standing very still in a field'],
 'arch.ghoul': ['graves dug up from beneath', 'a smell of old meat and wet earth'], 'arch.wight': ['frost on the grass in summer', 'a barrow door standing open'],
 'arch.vampire': ['livestock found bloodless', 'a pale figure watching from a window that should be empty'], 'arch.ghost': ['a cold spot that moves', 'a voice calling a name over and over'],
 'arch.wraith': ['the warmth going out of the air', 'shadows that move against the light'], 'arch.lich': ['a land of grey, dead things', 'the dead walking in ordered ranks'],
 'arch.deathlord': ['a banner of bone on the horizon', 'every bird in the sky flying away'], 'arch.fey_noble': ['music from under a hill', 'a feast laid in a glade with no one there'],
 'arch.wild_fey': ['knots in your gear you did not tie', 'laughter in the leaves'], 'arch.hag': ['charms of bone and hair hung from branches', 'a cottage that was not there yesterday'],
 'arch.place_spirit': ['the land holding its breath', 'stones arranged where no hand placed them'], 'arch.ancestor': ['a grave-gift left fresh on an old mound', 'a voice in an old tongue'],
 'arch.celestial': ['a light with no source', 'a feeling of being judged'], 'arch.lesser_demon': ['a smell of sulphur', 'scorched hoofprints that end in the air'],
 'arch.greater_demon': ['the sky darkening at noon', 'animals fleeing in a flood'], 'arch.tempter': ['a stranger who knows your name', 'a gift on the path that you wanted'],
 'arch.enforcer': ['chains dragged over stone', 'a seal burned into a door'], 'arch.possessor': ['a villager acting wrong', 'eyes that are not the person\'s own'],
 'arch.hellbeast': ['paw-prints burned into the ground', 'a baying with a crackle of fire in it'], 'arch.golem': ['heavy, perfectly regular footprints', 'a grinding of stone on stone'],
 'arch.animated': ['things not quite where you left them', 'a rattle of armor in an empty hall'], 'arch.clockwork': ['a ticking in the walls', 'a brass gear dropped on the path'],
 'arch.homunculus': ['tiny footprints in the dust', 'something small watching from a shelf'], 'arch.fire_elemental': ['grass burning in a line with no fire behind it', 'heat-shimmer moving against the wind'],
 'arch.earth_elemental': ['the ground cracking in a line', 'rocks rolling uphill'], 'arch.water_elemental': ['a wave on a still pool', 'water standing in a shape'],
 'arch.air_elemental': ['a whirlwind with no weather', 'a howl in a still sky'], 'arch.frost_elemental': ['frost spreading in a line', 'ice forming on running water'],
 'arch.great_dragon': ['a shadow the size of a field', 'a burned village on the skyline'], 'arch.drake': ['scorched stones and a reek of brimstone', 'a roar from a crag'],
 'arch.wyvern': ['a sheep carried off whole', 'a shriek from above'], 'arch.wyrm': ['a furrow through the land as wide as a road', 'a hiss like a forge'],
 'arch.aberration': ['tracks that do not make sense', 'a headache that comes with a smell of copper'], 'arch.ooze': ['a slick trail that has eaten the stone', 'bones polished clean'],
 'arch.fungal': ['puffballs bursting as you pass', 'a soft grey carpet where there was rock'], 'arch.monstrous_plant': ['vines across the path that were not there', 'a sweet smell and a drowsiness'],
 'arch.abomination': ['things stitched together and left to rot', 'a lowing that is almost words'],
}
missing = [a for a in archs if a not in S]
# ---- activities (T-10-20) as data ----
A = lambda id, verbs, verb, lic, attr, tag, tier, site, free, travel, reach, knobs: {'id': id, 'intent_verbs': verbs, 'verb': verb, 'license': lic, 'attribute': attr, 'primary_tag': tag, 'tier': tier,
   'duration': {'site': site, 'free': free, 'travel': travel}, 'reach': reach, 'knobs': knobs, 'anchor': True, 'lifecycle': 'provisional', 'basis': ['10.15']}
activities = [
 A('act.explore_onward', ['delve', 'press on', 'go deeper'], 'verb.observe | verb.sneak | verb.move', None, 'wits | agility', 'deed.lore.investigation.search', 'site explore_tier', 'intervals:1 (care 2)', None, None, 'progress ticks', ['dc', 'attribute', 'time_cost', 'reach_unit', 'stakes']),
 A('act.search', ['search', 'look for', 'examine', 'check'], 'verb.observe', None, 'wits', 'deed.lore.investigation.search', 'the hidden thing\'s detect tier', 'intervals:1 per area', '10 min per room; hours:1 per building', None, 'items found (P17)', ['dc', 'time_cost', 'targets']),
 A('act.listen', ['listen', 'eavesdrop', 'hear'], 'verb.observe', None, 'wits', 'deed.lore.investigation.search', 'easy; moderate through a thick door', 'intervals:0-1', '1 min', None, 'items heard', ['dc', 'targets']),
 A('act.map', ['map', 'chart', 'sketch the way'], 'verb.handle', 'lic.training.wilds_navigation (charts); a sketch is G1', 'intellect', 'deed.wilds.navigation.mapping', 'easy (site); area nav tier (travel)', '+1 per area', 'hours:1', 'watches:1', 'a map fact', ['time_cost', 'dc']),
 A('act.scout', ['scout', 'range ahead', 'reconnoiter'], 'verb.sneak | verb.observe', None, 'agility | wits', 'deed.wilds.tracking.sign', 'denizens\' notice / area nav tier', 'intervals:1', 'hours:1', 'watches:1', 'what lies ahead', ['dc', 'time_cost', 'targets']),
 A('act.track', ['track', 'trail', 'follow sign'], 'verb.observe', 'lic.training.wilds_tracking (old or hard trails); fallback +5 for fresh plain tracks', 'wits', 'deed.wilds.tracking.trailing', 'trail tier: fresh soft easy; a day old or hard ground moderate; rain or rock hard; covered very_hard', 'intervals:1', 'hours:1', 'per watch at slow pace', 'run-down ticks or still on it', ['dc', 'time_cost', 'reach_unit']),
 A('act.cover_tracks', ['cover tracks', 'lose them', 'hide the trail'], 'verb.sneak', None, 'wits', 'deed.guile.stealth', 'pursuers\' best Wits defense', 'intervals:1', 'hours:1', 'watches:1 at slow pace', 'trail tier +1 rung per reach', ['dc', 'time_cost']),
 A('act.climb', ['climb', 'scale', 'descend'], 'verb.exert', None, 'might | agility', 'deed.martial.athletics.climbing', 'rough wall easy; cliff moderate; sheer or wet hard; overhang very_hard', 'intervals:1 per 60 ft', '10 min per 60 ft', None, '1 halfway, 2 the top, 3 time saved, 4 + lever', ['dc', 'time_cost', 'stakes']),
 A('act.swim', ['swim', 'cross the water', 'dive'], 'verb.exert', None, 'might | endurance', 'deed.martial.athletics.swimming', 'calm easy; current moderate; spate or swell hard; whirlpool very_hard', 'intervals:1 per crossing', '10 min', None, '1 partway, 2 across', ['dc', 'stakes', 'attribute']),
 A('act.jump', ['leap', 'vault', 'jump across'], 'verb.exert', None, 'might | agility', 'deed.martial.athletics.jumping', '5 ft easy; 10 ft moderate; 12 ft hard (running); 15 ft very_hard; 30 ft beyond', 'intervals:0-1', None, None, 'across', ['dc', 'stakes']),
 A('act.squeeze', ['crawl through', 'squeeze', 'wriggle'], 'verb.exert', None, 'agility', 'deed.martial.athletics.acrobatics', 'crawl easy; tight moderate; medium armor +1 rung; heavy armor G4', 'intervals:1', '10 min', None, 'through', ['dc', 'attribute']),
 A('act.force_way', ['break down', 'force open', 'clear'], 'verb.force', None, 'might', 'deed.martial.athletics.lifting', 'the barrier\'s tier', 'intervals:1', '1 min', None, 'open', ['dc', 'targets']),
 A('act.pick_lock', ['pick', 'open the lock'], 'verb.handle', 'lic.training.guile_thievery (fallback: force)', 'agility', 'deed.guile.thievery.lockpicking', 'the lock\'s tier', 'intervals:1', '10 min', None, 'open', ['dc']),
 A('act.disarm', ['disarm', 'jam', 'spring the trap'], 'traps.yaml#ways', 'per way', 'by way', 'deed.guile.thievery.traps', 'the trap\'s tiers', 'intervals:1', '10 min', None, 'per way', ['dc', 'verb']),
 A('act.dig', ['dig', 'clear rubble', 'tunnel'], 'verb.force | verb.exert', None, 'might | endurance', 'deed.martial.athletics.lifting', 'a progress clock: rubble 4, collapse 6, tunnel 8+', 'intervals:1 per roll', 'hours:1 per roll', None, 'clock ticks', ['dc', 'time_cost', 'reach_unit']),
 A('act.secure', ['barricade', 'bar the door', 'make safe'], 'verb.handle | verb.force', None, 'might', 'deed.craft.building', 'site explore tier', 'intervals:1', '10 min', None, 'secured area (rest site camp)', ['dc']),
 A('act.light_fire', ['make fire', 'light a torch', 'kindle'], 'verb.handle', 'lic.training.wilds_survival in hard conditions (fallback +5)', 'agility', 'deed.wilds.survival.firecraft', 'weather fire tier', 'intervals:1', '10 min', 'part of camp', 'fire; reach 2: no smoke', ['dc', 'time_cost']),
 A('act.make_camp', ['make camp', 'pitch', 'settle'], 'free activity; verb.handle for shelter', 'lic.training.wilds_survival for lasting shelter (fallback: a crude lean-to)', 'agility', 'deed.wilds.survival.shelter', 'trivial fair; storm moderate; snow hole moderate', None, 'hours:1', 'part of the camp watch', 'camp rest site; shelter and fire facts', ['time_cost']),
 A('act.keep_watch', ['keep watch', 'stand guard'], 'free (lookout role)', None, None, 'deed.wilds.survival.weathersense', None, 'while resting', 'per hour', 'per watch', 'the camp is aware', ['duration']),
 A('act.forage', ['forage', 'gather', 'scrounge'], 'verb.observe', 'lic.training.wilds_foraging (fallback +5, Limited)', 'wits', 'deed.wilds.foraging.food', 'forage tier', None, 'hours:1 (reach - 1)', 'watches:1', 'supply', ['dc', 'time_cost', 'reach_unit']),
 A('act.hunt', ['hunt', 'stalk game'], 'verb.observe', 'lic.training.wilds_tracking (fallback +5, Limited)', 'wits', 'deed.wilds.tracking.hunting', 'game tier', None, None, 'watches:1', 'supply = 2 x reach; a carcass', ['dc', 'reach_unit']),
 A('act.fish', ['fish', 'net', 'spear fish'], 'verb.handle', None, 'wits', 'deed.wilds.foraging.food', 'river or lake easy; coast moderate', None, None, 'watches:1', 'supply = reach (Limited without tackle)', ['dc', 'reach_unit']),
 A('act.snare', ['set snares'], 'verb.handle', None, 'agility', 'deed.wilds.tracking.hunting', 'd6 at dawn vs game tier (easy 3+, moderate 4+, hard 5+, very_hard 6; license +1)', None, None, 'during camp', '1 supply', ['dc']),
 A('act.find_water', ['find water'], 'verb.observe', 'lic.training.wilds_foraging (fallback +5)', 'wits', 'deed.wilds.foraging.water', 'forage tier (+1 rung arid)', None, 'hours:1', 'watches:1', 'water source; reach 2 also tomorrow', ['dc']),
 A('act.read_weather', ['read the sky', 'forecast'], 'verb.observe', 'lic.training.wilds_survival', 'wits', 'deed.wilds.survival.weathersense', 'easy', None, 'intervals:1', None, 'forecast', ['dc', 'targets']),
 A('act.find_way', ['navigate', 'reorient', 'find the way'], 'verb.observe', 'lic.training.wilds_navigation (fallback +5, Limited, landmark needed)', 'wits | intellect', 'deed.wilds.navigation.wayfinding', 'nav tier', None, None, 'per day', 'course', ['dc', 'attribute', 'time_cost', 'reach_unit']),
 A('act.ford', ['ford', 'wade across'], 'verb.exert', None, 'might', 'deed.martial.athletics.swimming', 'haz.ford tier', 'intervals:1', '10 min', 'part of the watch', 'across', ['dc', 'stakes']),
 A('act.rope', ['rig a rope', 'lower', 'belay'], 'verb.handle', None, 'agility', 'deed.martial.athletics.climbing', 'easy with an anchor point; moderate improvised', 'intervals:1', '10 min', None, 'a rope fact (Protective lever)', ['dc']),
 A('act.harvest', ['skin', 'butcher', 'carve', 'harvest'], '08.3.10', 'per 08.3.10', 'wits', 'deed.wilds.foraging.harvest', 'by the rarest part', 'intervals:1', 'hours:1 (a large body)', None, 'parts', ['dc', 'time_cost', 'reach_unit']),
 A('act.scavenge', ['loot the room', 'strip the dead'], 'verb.observe', None, 'wits', 'deed.lore.investigation.search', 'easy', 'intervals:1', '10 min', None, 'gear and coin (08.3.11)', ['time_cost']),
 A('act.study', ['read the inscription', 'study the mural'], 'verb.observe', 'a language license for scripts', 'intellect', 'deed.lore.history', 'the text\'s tier', 'intervals:1', 'hours:1', None, 'items (P17)', ['dc', 'attribute']),
 A('act.signal', ['signal', 'call out', 'light a beacon'], 'verb.handle | verb.talk', None, 'presence', 'deed.influence.command', 'easy', 'intervals:1', '1 min', None, 'heard by whom it reaches (loud)', ['targets']),
 A('act.haul', ['drag', 'carry out', 'haul up'], 'verb.exert', None, 'might | endurance', 'deed.martial.athletics.lifting', 'within capacity easy; burdened moderate; overloaded G4', 'per area walked', 'per hour', 'at crawl', 'moved', ['dc', 'time_cost']),
 A('act.rest', ['breather', 'short rest', 'long rest'], '07.8', None, None, None, None, 'breather 1; short 6; long a watch', 'breather 10 min; short hours:1', 'rest / sleep watch', '07 recovery', []),
]
# ---- validation ----
bad = []
for t in list(terrain_defaults) + [e['terrain'] for e in encounter_tables]:
    if t not in tags: bad.append(t)
for e in encounter_tables:
    for r in e['threat'] + e['non_threat']:
        for ref in r.get('ref', []):
            if ref not in archs: bad.append(ref)
for a in activities:
    if a['primary_tag'] and a['primary_tag'] not in tags: bad.append(a['primary_tag'])
for r in roles:
    if r['evidence_tag'] not in tags: bad.append(r['evidence_tag'])
print('bad', bad, 'missing signs', missing)
# audit: bands among threat rows by d20 weight
audit = {}
for e in encounter_tables:
    w = {'home-1': 0, 'home': 0, 'home+1': 0}
    for r in e['threat']:
        a, b = (r['range'].split('-') + [r['range']])[:2]
        w[r['band']] += int(b) - int(a) + 1
    audit[e['id']] = w
    assert w == {'home-1': 6, 'home': 11, 'home+1': 3}, (e['id'], w)
print('band audit ok: every generic table is 6/11/3 of 20 = 30/55/15')
doc = {'schema_version': 1, 'rings': rings, 'pace': pace, 'vessel_pace': vessel_pace, 'march': march, 'activities_by_watch': watch_activities, 'roles': roles,
       'watch_check': watch_check, 'site_check': site_check, 'pending_threat': pending, 'tables': tables,
       'terrain_defaults': terrain_defaults, 'terrain_defaults_rule': terrain_defaults_rule,
       'encounter_tables': encounter_tables, 'encounter_table_audit': {k: v for k, v in audit.items()}, 'archetype_signs': S,
       'activities': activities,
       'navigation': {'beat': 'act.find_way (10.4.2)', 'tiers': ['easy', 'moderate', 'hard', 'very_hard'], 'reach': {0: 'off course: sealed nav.lost, veer by tbl.10.veer', 1: 'on course, the day\'s pace one step slower', 2: 'on course', 3: 'on course, +2 points per travel watch of the leg today', 4: 'as 3, and one undiscovered place in the area discovered'},
                      'levers': ['map of the area', 'area mapped by the PC', 'slow pace', 'stars at night', 'a guide\'s Help'], 'snags': ['night without stars', 'fog, storm, snow, blizzard', 'fast pace'],
                      'take_the_time': 'easy, moderate, hard: no roll, reach standard, each travel watch of the day earns half points', 'lost_reveal': ['expected arrival + 1 travel watch', 'a way-finding beat while lost', 'recognition', 'a license or ability (stonesense: Certain underground)']},
       'supply': {'unit': '1 supply = one person-day of food and water (08.9.4)', 'load': '2 supply per load unit', 'need': '1 per consumer per day; +1 in heat, scorching or arid without water_source', 'half_rations': 'half need, rounded up per two consumers; long rest at best partial; a second consecutive day counts as without food',
                  'want': 'one cond.exhausted stack per unfed consumer per day; 07.8.10 deprivation warning at three stacks; then S3 harm, no reduction', 'order': ['pc', 'companions', 'hirelings', 'mounts']},
       'blocks': []}
hdr = """# data/travel.yaml
# Purpose: travel and exploration data for ch.10: danger rings, the pace ladder and its steps, vessel
#   paces, the march allowance, watch activities, journey roles, the overloaded time-tick check for travel
#   (watch_check) and sites (site_check), the pending-threat record, the face result tables (depletion,
#   find, opportunity, veer, encounter distance), terrain defaults (nav, forage, game, openness, grazing,
#   water), the generic encounter tables by terrain branch (used where 13 provides none), archetype omen
#   signs, the exploration activity catalog (T-10-20), navigation and supply summaries.
# Owner: 10-exploration-travel-sites (owner-block 13 for regional encounter tables, events and signs).
# Schema: data/SCHEMAS.md#travelyaml (pace, activities, watch_check {die, results}, navigation, supply,
#   exploration_activities) plus ch.10's optional keys listed above (the exploration activity catalog is
#   the key `activities`; the per-watch activity list is `activities_by_watch`).
# Encounter tables: threat sub-table d20 with relative bands (6 rows' worth home-1, 11 home, 3 home+1 =
#   30/55/15, 09.8.2, audited by gen10_travel.py), non-threat sub-table d6; the danger rating's
#   threat_share_d12 picks the sub-table (10.9.4-10.9.5).
# Basis: [10.3-10.10, 10.15] [R5 P-30..P-36] [R6 B-14, B-15, B-R5] [09.8] [DL-10-02..10]
"""
txt = hdr + "\n" + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120, default_flow_style=None)
open(OUT, 'w', encoding='utf-8').write(txt)
yaml.safe_load(open(OUT, encoding='utf-8'))
print('ok', len(encounter_tables), 'tables', len(S), 'signs', len(activities), 'activities')
