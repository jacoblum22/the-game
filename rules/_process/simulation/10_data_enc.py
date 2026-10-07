# 10_data_enc.py -- the generic encounter tables of ch.10 (T-10-16), per terrain branch and per home band.
# Read by 10-gen10_travel.py (exec'd into its namespace) and audited by 10-word-audit.py (PR-10-8).
# Revision B (I-029): the band-relative single table of the first draft failed PR-10-8's word step in 48 of 55
# terrain x home-band cases, because one row (e.g. "orcs, home band, their usual group") is a fair fight at one
# home band and a lethal one at another, and an archetype clamped to its fielded bands (troll 3-5 at home 1)
# is out of budget. Each terrain now carries one threat sub-table per home band 1-5 (threat_by_home), written
# against T-09-10's shapes, so every row is fielded at exactly its labelled band and its word is known.
#
# R(weight, offset, archetype, count, variant, ...): offset -1 / 0 / +1 = home-1 / home / home+1.
# Weights per home band: 6 faces at home-1, 11 at home, 3 at home+1 (09.8.2's 30/55/15; asserted).
# Edge rules (10.10.1): at home 1 the home-1 faces field band-1 creatures (there is no band 0), so they are
# written small; at home 5 the home+1 faces field band-5 solos (09.8.2's top ring).

def R(w, off, arch, count, variant='standard', ambush=False, complication=False, when='any', note=None, leader=False):
    d = {'w': w, 'band': {-1: 'home-1', 0: 'home', 1: 'home+1'}[off], 'ref': ['arch.' + arch], 'count': str(count),
         'variant': variant, 'leader': leader, 'ambush': ambush, 'complication': complication, 'when': when}
    if note: d['note'] = note
    return d

M = 'minion'; E = 'elite'; S = 'solo'

ENC = {}

# ------------------------------------------------------------------------------------------------ road
ENC['terrain.road'] = {1: [
    R(3, -1, 'brigand', '1-2', ambush=True, note='a pair of footpads at a narrows'),
    R(3, -1, 'wolf', '1-2', note='a hungry wolf shadowing the carts'),
    R(3, 0, 'goblin', '5-7', M, ambush=True, note='goblins rolling a log across the road'),
    R(3, 0, 'brigand', '5-7', M, complication=True, note='a mob of hungry men at a toll they invented'),
    R(3, 0, 'orc', '5-7', M, note='an orc raiding party on the road'),
    R(2, 0, 'ghost', '1', when='night', note='a hanged man at the crossroads gibbet'),
    R(2, 1, 'ogre', '1', note='an ogre demanding a toll at a ford'),
    R(1, 1, 'orc', '1', note='an orc outrider ahead of a raid'),
  ], 2: [
    R(3, -1, 'brigand', '4-6', M, ambush=True, note='a ragged gang of footpads'),
    R(3, -1, 'goblin', '4-6', M, ambush=True, note='goblins in the ditches'),
    R(3, 0, 'brigand', '2', note='highwaymen on good horses'),
    R(3, 0, 'soldier', '2', complication=True, note='corrupt toll-men with a writ'),
    R(3, 0, 'ogre', '1', E, note='an ogre sitting in the road eating a horse'),
    R(2, 0, 'tempter', '1', note='a well-dressed stranger with an offer'),
    R(2, 1, 'orc', '1', M, note='an orc scout who has seen too much'),
    R(1, 1, 'troll', '1', M, note='a young troll under a bridge'),
  ], 3: [
    R(3, -1, 'brigand', '6-8', M, ambush=True, note='a robber band at an ambush cut'),
    R(3, -1, 'orc', '6-8', M, note='orc raiders on the road'),
    R(3, 0, 'soldier', '1', E, note='a lord\'s sergeant collecting a tax that is not owed'),
    R(3, 0, 'troll', '2', M, note='two young trolls under a bridge'),
    R(3, 0, 'knight', '1', complication=True, note='a hedge knight who holds the bridge against all comers'),
    R(2, 0, 'vampire', '1', M, when='night', note='a pale coachman who offers a ride'),
    R(2, 1, 'ogre', '1', M, note='an ogre\'s whelp foraging along the verge'),
    R(1, 1, 'fey_noble', '1', M, when='night', note='a rider of the Wild Hunt, lost from it'),
  ], 4: [
    R(3, -1, 'brigand', '1', leader=True, ambush=True, note='a robber-baron\'s tax-collector, armed and mounted'),
    R(3, -1, 'troll', '1', note='a bridge troll grown fat on tolls'),
    R(3, 0, 'knight', '1', note='a champion holding the road for a pretender'),
    R(3, 0, 'tempter', '1', note='a crossroads devil with a contract'),
    R(3, 0, 'soldier', '1', M, complication=True, note='a press-gang\'s recruiter: the war needs bodies'),
    R(2, 0, 'ogre', '1', note='an ogre chieftain\'s toll-gate'),
    R(2, 1, 'vampire', '1', M, when='night', note='a coach with no driver, and a passenger who wants company'),
    R(1, 1, 'fey_noble', '1', M, when='night', note='the Wild Hunt passing: one rider turns aside'),
  ], 5: [
    R(3, -1, 'knight', '1', note='a renegade champion and his oath'),
    R(3, -1, 'troll', '1', note='an old troll who has eaten three bridge-wardens'),
    R(3, 0, 'tempter', '1', M, note='a devil\'s factor on its master\'s business'),
    R(3, 0, 'folk_mage', '1', note='an archmage on the road, in a temper'),
    R(3, 0, 'vampire', '1', M, when='night', note='a vampire\'s herald, hunting for its lord'),
    R(2, 0, 'fey_noble', '1', note='a lord of the Wild Hunt'),
    R(2, 1, 'fey_noble', '1', S, note='the Erl-King\'s ride crossing the road'),
    R(1, 1, 'vampire', '1', S, when='night', note='a vampire lord abroad in its coach'),
  ]}

# ------------------------------------------------------------------------------------------ settlement
ENC['terrain.settlement'] = {1: [
    R(3, -1, 'brigand', '1-2', ambush=True, when='night', note='footpads in an alley'),
    R(3, -1, 'vermin_swarm', '1', note='rats boiling out of a granary'),
    R(3, 0, 'brigand', '5-7', M, note='a gang\'s thugs collecting'),
    R(3, 0, 'cultist', '5-7', M, when='night', note='cultists at a cellar rite'),
    R(3, 0, 'zombie', '5-7', M, when='night', note='the dead walk out of the old graveyard'),
    R(2, 0, 'homunculus', '1', note='a wizard\'s escaped familiar, stealing'),
    R(2, 1, 'ghost', '1', when='night', note='a ghost in the well-house'),
    R(1, 1, 'possessor', '1', M, note='a child speaking in a stranger\'s voice'),
  ], 2: [
    R(3, -1, 'brigand', '4-6', M, ambush=True, when='night', note='a street gang'),
    R(3, -1, 'animated', '2', note='a dead alchemist\'s shop-guardians'),
    R(3, 0, 'soldier', '2', complication=True, note='the watch, bribed to make you vanish'),
    R(3, 0, 'cultist', '2', when='night', note='a cult cell\'s enforcers'),
    R(3, 0, 'ghost', '1', E, when='night', note='a murdered servant who wants a name spoken'),
    R(2, 0, 'folk_mage', '1', E, note='a hedge-wizard selling curses'),
    R(2, 1, 'vampire', '1', M, when='night', note='a vampire\'s thrall feeding in the stews'),
    R(1, 1, 'enforcer', '1', M, note='a debt-collector from below'),
  ], 3: [
    R(3, -1, 'cultist', '6-8', M, when='night', note='a mob whipped up by a preacher'),
    R(3, -1, 'soldier', '2', note='a guild\'s hired swords'),
    R(3, 0, 'possessor', '1', E, note='a respected burgher, possessed'),
    R(3, 0, 'ghost', '2', M, when='night', note='the ghosts of a fire in a counting-house'),
    R(3, 0, 'cultist', '1', E, complication=True, note='a cult\'s inquisitor, hunting heretics'),
    R(2, 0, 'animated', '1', E, note='a guildhall\'s bronze guardian woken'),
    R(2, 1, 'vampire', '1', M, when='night', note='a vampire\'s get, newly made and starving'),
    R(1, 1, 'tempter', '1', M, note='a smiling broker of souls'),
  ], 4: [
    R(3, -1, 'soldier', '2', note='a magistrate\'s bravos'),
    R(3, -1, 'cultist', '1', E, when='night', note='the high priest of a cult in the temple cellars'),
    R(3, 0, 'enforcer', '1', M, complication=True, note='an imp-bailiff come to collect on an old contract'),
    R(3, 0, 'possessor', '1', note='a councillor ridden by a demon'),
    R(3, 0, 'folk_mage', '1', note='a court sorcerer with a grudge'),
    R(2, 0, 'ghost', '1', when='night', note='a plague-pit\'s ghost'),
    R(2, 1, 'vampire', '1', M, when='night', note='the vampire\'s favoured child'),
    R(1, 1, 'tempter', '1', M, note='a devil in the guise of a banker'),
  ], 5: [
    R(3, -1, 'knight', '1', note='a lord\'s champion sent to arrest you'),
    R(3, -1, 'possessor', '1', note='a bishop who is no longer himself'),
    R(3, 0, 'folk_mage', '1', note='the city\'s archmage, displeased'),
    R(3, 0, 'tempter', '1', M, note='a devil\'s emissary with an offer for the city'),
    R(3, 0, 'enforcer', '1', M, note='an infernal bailiff serving a writ'),
    R(2, 0, 'vampire', '1', M, when='night', note='a vampire\'s herald in the masked ball'),
    R(2, 1, 'vampire', '1', S, when='night', note='the vampire who owns the city\'s nights'),
    R(1, 1, 'enforcer', '1', S, note='a duke of hell\'s magistrate'),
  ]}

# -------------------------------------------------------------------------------------------- forest
ENC['terrain.forest'] = {1: [
    R(3, -1, 'wolf', '1-2', note='a wolf at the edge of the firelight'),
    R(3, -1, 'giant_vermin', '1', ambush=True, note='a spider dropping from the canopy'),
    R(3, 0, 'wolf', '5-7', M, note='a wolf pack on a cold trail'),
    R(3, 0, 'goblin', '5-7', M, ambush=True, note='goblins with nets'),
    R(3, 0, 'wild_fey', '5-7', M, complication=True, note='a swarm of sprites who steal what you set down'),
    R(2, 0, 'brigand', '2', ambush=True, note='outlaws of the greenwood'),
    R(2, 1, 'bear', '1', note='a bear with cubs'),
    R(1, 1, 'monstrous_plant', '1', M, note='a strangling creeper across the path'),
  ], 2: [
    R(3, -1, 'wolf', '4-6', M, note='wolves circling'),
    R(3, -1, 'giant_vermin', '2', ambush=True, note='spiders in the canopy'),
    R(3, 0, 'bear', '1', E, note='a great bear defending a kill'),
    R(3, 0, 'brigand', '2', ambush=True, note='outlaws of the greenwood'),
    R(3, 0, 'elf_warden', '2', complication=True, note='wardens who want you gone from the wood'),
    R(2, 0, 'hag', '1', note='an old woman by a cauldron, too kind'),
    R(2, 1, 'troll', '1', M, note='a troll-kit, hungry'),
    R(1, 1, 'monstrous_beast', '1', M, note='an owlbear yearling'),
  ], 3: [
    R(3, -1, 'great_cat', '2', ambush=True, note='a pair of hunting cats'),
    R(3, -1, 'wolf', '6-8', M, note='a wolf pack in winter'),
    R(3, 0, 'monstrous_beast', '1', E, note='an owlbear'),
    R(3, 0, 'troll', '1', E, note='a troll in a deadfall den'),
    R(3, 0, 'fey_noble', '1', M, complication=True, note='a fey knight errant who wants a contest'),
    R(2, 0, 'place_spirit', '1', E, note='the wood\'s anger made flesh'),
    R(2, 1, 'hag', '1', M, note='a hag\'s apprentice'),
    R(1, 1, 'monstrous_plant', '1', M, note='a treant\'s sapling that walks'),
  ], 4: [
    R(3, -1, 'bear', '2', note='two great bears fighting over a carcass'),
    R(3, -1, 'elf_warden', '1', leader=True, note='a warden captain and her sworn'),
    R(3, 0, 'troll', '1', note='an old troll who knows the paths'),
    R(3, 0, 'hag', '1', complication=True, note='a hag who wants a bargain'),
    R(3, 0, 'monstrous_plant', '1', note='a walking tree, angry'),
    R(2, 0, 'monstrous_beast', '1', M, note='a chimera\'s brood, hunting'),
    R(2, 1, 'fey_noble', '1', M, note='a fey lord\'s huntsman'),
    R(1, 1, 'place_spirit', '1', M, note='the grove-spirit\'s outrider'),
  ], 5: [
    R(3, -1, 'hag', '1', note='a hag-grandmother'),
    R(3, -1, 'troll', '1', note='a troll king\'s gamekeeper'),
    R(3, 0, 'monstrous_plant', '1', note='a treant older than the kingdom'),
    R(3, 0, 'fey_noble', '1', M, note='a fey courtier with a wager'),
    R(3, 0, 'place_spirit', '1', M, note='the wood\'s guardian, half-awake'),
    R(2, 0, 'folk_mage', '1', note='a druid of the old circle'),
    R(2, 1, 'fey_noble', '1', S, note='the Erl-King riding'),
    R(1, 1, 'monstrous_beast', '1', S, note='the Questing Beast'),
  ]}

# ------------------------------------------------------------------------------------------ highland
ENC['terrain.highland'] = {1: [
    R(3, -1, 'wolf', '1-2', note='a wolf on a ridge'),
    R(3, -1, 'goblin', '2', ambush=True, note='goblin slingers among the rocks'),
    R(3, 0, 'orc', '5-7', M, note='an orc war-band\'s foragers'),
    R(3, 0, 'raptor', '1-2', note='great eagles that want your mule'),
    R(3, 0, 'goblin', '5-7', M, ambush=True, complication=True, note='goblins on a scree slope'),
    R(2, 0, 'brigand', '2', note='hill bandits'),
    R(2, 1, 'bear', '1', note='a cave bear woken early'),
    R(1, 1, 'ogre', '1', M, note='a young ogre throwing rocks'),
  ], 2: [
    R(3, -1, 'orc', '4-6', M, note='an orc war-band\'s stragglers'),
    R(3, -1, 'wolf', '4-6', M, note='wolves on the high pasture'),
    R(3, 0, 'ogre', '1', E, complication=True, note='an ogre in a pass'),
    R(3, 0, 'bear', '1', note='a bear in the berry-scrub'),
    R(3, 0, 'dwarf_holdguard', '2', note='holdguards who think you are thieves'),
    R(2, 0, 'drake', '1', note='a rock drake sunning itself'),
    R(2, 1, 'wyvern', '1', M, note='a young wyvern'),
    R(1, 1, 'troll', '1', M, note='a troll-kit in a cave'),
  ], 3: [
    R(3, -1, 'orc', '6-8', M, note='orc raiders'),
    R(3, -1, 'ogre', '2', note='a pair of ogre shepherds'),
    R(3, 0, 'wyvern', '1', E, note='a wyvern on the hunt'),
    R(3, 0, 'troll', '1', note='a hill troll'),
    R(3, 0, 'orc', '1', E, complication=True, note='an orc war-chief out for a name'),
    R(2, 0, 'earth_elemental', '1', E, note='a rockslide that stands up'),
    R(2, 1, 'giant', '1', M, note='a giant\'s child'),
    R(1, 1, 'drake', '1', M, note='a drake\'s brood'),
  ], 4: [
    R(3, -1, 'wyvern', '1', note='a wyvern'),
    R(3, -1, 'orc', '1', leader=True, note='an orc war-band\'s champion, scouting ahead'),
    R(3, 0, 'giant', '1', note='a hill giant'),
    R(3, 0, 'troll', '1', complication=True, note='a troll that has learned to set ambushes'),
    R(3, 0, 'air_elemental', '1', note='a storm that will not pass'),
    R(2, 0, 'drake', '1', note='a mountain drake'),
    R(2, 1, 'great_dragon', '1', M, note='a dragon\'s wyrmling'),
    R(1, 1, 'celestial', '1', M, note='a sky-herald on the peak'),
  ], 5: [
    R(3, -1, 'wyvern', '1', note='a wyvern'),
    R(3, -1, 'drake', '1', note='a war-drake'),
    R(3, 0, 'great_dragon', '1', M, note='a dragon\'s young, hunting'),
    R(3, 0, 'giant', '1', M, note='a giant jarl\'s outrider'),
    R(3, 0, 'air_elemental', '1', M, note='a gale off the peaks with a will'),
    R(2, 0, 'celestial', '1', M, note='a guardian of the high places'),
    R(2, 1, 'giant', '1', S, note='a storm giant'),
    R(1, 1, 'earth_elemental', '1', S, note='the mountain itself, awake'),
  ]}

# -------------------------------------------------------------------------------------------- plains
ENC['terrain.plains'] = {1: [
    R(3, -1, 'wolf', '1-2', note='a wolf in the long grass'),
    R(3, -1, 'gnoll', '1', note='a gnoll scavenger'),
    R(3, 0, 'gnoll', '5-7', M, note='a gnoll pack'),
    R(3, 0, 'orc', '5-7', M, note='orc horse-thieves'),
    R(3, 0, 'herd_beast', '5-7', M, complication=True, note='a stampede'),
    R(2, 0, 'raptor', '1-2', note='giant hawks'),
    R(2, 1, 'great_cat', '1', note='a lion'),
    R(1, 1, 'orc', '1', M, note='an orc rider far ahead of its band'),
  ], 2: [
    R(3, -1, 'gnoll', '4-6', M, note='gnolls on a trail'),
    R(3, -1, 'wolf', '4-6', M, note='wolves following a herd'),
    R(3, 0, 'orc', '2', complication=True, note='orc riders'),
    R(3, 0, 'great_cat', '1', note='a lioness'),
    R(3, 0, 'herd_beast', '1', E, note='a stampede led by a great bull'),
    R(2, 0, 'gnoll', '1', leader=True, note='a gnoll pack-mother'),
    R(2, 1, 'monstrous_beast', '1', M, note='a manticore\'s cub'),
    R(1, 1, 'wyvern', '1', M, note='a young wyvern'),
  ], 3: [
    R(3, -1, 'gnoll', '6-8', M, note='gnoll raiders'),
    R(3, -1, 'orc', '6-8', M, note='orc foot'),
    R(3, 0, 'knight', '1', complication=True, note='a knight on quest who mistakes you for his quarry'),
    R(3, 0, 'monstrous_beast', '1', E, note='a manticore'),
    R(3, 0, 'orc', '1', E, note='an orc war-chief riding alone'),
    R(2, 0, 'wyvern', '1', E, note='a wyvern hunting the herds'),
    R(2, 1, 'giant', '1', M, note='a giant\'s child herding aurochs'),
    R(1, 1, 'air_elemental', '1', M, note='a dust devil that follows'),
  ], 4: [
    R(3, -1, 'wyvern', '1', note='a wyvern'),
    R(3, -1, 'orc', '2', note='orc champions'),
    R(3, 0, 'giant', '1', note='a hill giant on the move'),
    R(3, 0, 'knight', '1', note='a champion and his oath'),
    R(3, 0, 'air_elemental', '1', complication=True, note='a whirlwind with a mind'),
    R(2, 0, 'place_spirit', '1', note='the spirit of a battlefield'),
    R(2, 1, 'monstrous_beast', '1', M, note='a sphinx\'s get'),
    R(1, 1, 'place_spirit', '1', M, note='the herald-wind of a storm'),
  ], 5: [
    R(3, -1, 'giant', '1', note='a giant warband\'s scout'),
    R(3, -1, 'wyvern', '1', note='a wyvern hunting the herds'),
    R(3, 0, 'knight', '1', M, note='a dread lord\'s outrider'),
    R(3, 0, 'air_elemental', '1', M, note='a storm-front with a will'),
    R(3, 0, 'monstrous_beast', '1', M, note='a sphinx\'s errand-beast'),
    R(2, 0, 'place_spirit', '1', M, note='the wind of the steppe'),
    R(2, 1, 'monstrous_beast', '1', S, note='a sphinx with a riddle and a hunger'),
    R(1, 1, 'air_elemental', '1', S, note='the great storm of the age'),
  ]}

# ------------------------------------------------------------------------------------------- wetland
ENC['terrain.wetland'] = {1: [
    R(3, -1, 'giant_vermin', '1', note='a giant leech'),
    R(3, -1, 'reptile', '1', note='a marsh viper'),
    R(3, 0, 'lizardfolk', '5-7', M, ambush=True, note='lizardfolk hunters'),
    R(3, 0, 'zombie', '5-7', M, note='the bog-dead'),
    R(3, 0, 'vermin_swarm', '1', complication=True, note='a cloud of biting flies'),
    R(2, 0, 'wild_fey', '1-2', note='will-o\'-the-wisps that lead astray'),
    R(2, 1, 'hag', '1', M, note='a bog-hag\'s daughter'),
    R(1, 1, 'reptile', '1', note='a great crocodile'),
  ], 2: [
    R(3, -1, 'lizardfolk', '4-6', M, ambush=True, note='lizardfolk raiders'),
    R(3, -1, 'zombie', '4-6', M, note='drowned dead'),
    R(3, 0, 'hag', '1', E, complication=True, note='a hag who trades in names'),
    R(3, 0, 'reptile', '2', note='crocodiles under the causeway'),
    R(3, 0, 'water_elemental', '1', note='a pool that rises'),
    R(2, 0, 'goblin', '2', ambush=True, note='bog-goblins'),
    R(2, 1, 'troll', '1', M, note='a fen-troll\'s whelp'),
    R(1, 1, 'wraith', '1', M, note='a wraith out of a sunken barrow'),
  ], 3: [
    R(3, -1, 'lizardfolk', '6-8', M, note='a lizardfolk war-party'),
    R(3, -1, 'hag', '1', note='a hag'),
    R(3, 0, 'troll', '1', E, note='a fen-troll'),
    R(3, 0, 'wraith', '1', E, when='night', note='a wraith that rises from the sedge'),
    R(3, 0, 'wyrm', '1', M, complication=True, note='a marsh-wyrm\'s young'),
    R(2, 0, 'monstrous_plant', '1', E, note='a strangling mangrove'),
    R(2, 1, 'reptile', '1', M, note='a crocodile the size of a barge'),
    R(1, 1, 'water_elemental', '1', M, note='a flood-spirit'),
  ], 4: [
    R(3, -1, 'troll', '1', note='a fen-troll'),
    R(3, -1, 'wraith', '1', note='a barrow-wraith'),
    R(3, 0, 'hag', '1', note='a coven-mother'),
    R(3, 0, 'wyrm', '1', M, complication=True, note='a marsh-wyrm grown fat'),
    R(3, 0, 'monstrous_plant', '1', note='a bog-tree that walks'),
    R(2, 0, 'water_elemental', '1', note='the tide of the fen'),
    R(2, 1, 'wraith', '1', M, note='a drowned king\'s herald'),
    R(1, 1, 'wyrm', '1', M, note='a black wyrm\'s spawn'),
  ], 5: [
    R(3, -1, 'hag', '1', note='a hag-queen\'s daughter'),
    R(3, -1, 'reptile', '1', note='the great crocodile of the delta'),
    R(3, 0, 'monstrous_plant', '1', note='a swamp-god\'s idol of root and mire'),
    R(3, 0, 'wyrm', '1', M, note='a black wyrm hunting'),
    R(3, 0, 'wraith', '1', M, note='a drowned king\'s champion'),
    R(2, 0, 'water_elemental', '1', M, note='a flood with a will'),
    R(2, 1, 'wyrm', '1', S, note='the Black Wyrm of the fen'),
    R(1, 1, 'wraith', '1', S, note='the drowned king himself'),
  ]}

# ---------------------------------------------------------------------------------------------- arid
ENC['terrain.arid'] = {1: [
    R(3, -1, 'giant_vermin', '1', note='a giant scorpion'),
    R(3, -1, 'reptile', '1', note='a sand viper'),
    R(3, 0, 'gnoll', '5-7', M, note='gnolls following the caravan'),
    R(3, 0, 'brigand', '5-7', M, ambush=True, note='desert raiders at a well'),
    R(3, 0, 'orc', '5-7', M, complication=True, note='orc water-thieves'),
    R(2, 0, 'giant_vermin', '2', note='scorpions under the stones'),
    R(2, 1, 'hellbeast', '1', M, note='a hell-hound in the heat-shimmer'),
    R(1, 1, 'great_cat', '1', note='a desert lion'),
  ], 2: [
    R(3, -1, 'gnoll', '4-6', M, note='a gnoll pack'),
    R(3, -1, 'brigand', '4-6', M, ambush=True, note='raiders on camels'),
    R(3, 0, 'drake', '1', E, note='a dune drake'),
    R(3, 0, 'fire_elemental', '1', note='a flame that walks'),
    R(3, 0, 'great_cat', '2', complication=True, note='a lion pride\'s hunters'),
    R(2, 0, 'gnoll', '1', leader=True, note='a gnoll pack-mother'),
    R(2, 1, 'monstrous_beast', '1', M, note='a manticore\'s cub'),
    R(1, 1, 'hellbeast', '1', M, note='a hell-hound off its leash'),
  ], 3: [
    R(3, -1, 'gnoll', '6-8', M, note='a gnoll war-pack'),
    R(3, -1, 'orc', '6-8', M, note='orc raiders'),
    R(3, 0, 'hellbeast', '1', E, note='a hell-hound'),
    R(3, 0, 'drake', '1', complication=True, note='a drake at the only water'),
    R(3, 0, 'monstrous_beast', '1', E, note='a manticore'),
    R(2, 0, 'place_spirit', '1', E, note='a djinn of the dunes'),
    R(2, 1, 'fire_elemental', '1', M, note='a fire elemental\'s spark'),
    R(1, 1, 'earth_elemental', '1', M, note='a sandstorm with a shape'),
  ], 4: [
    R(3, -1, 'hellbeast', '2', note='a pair of hell-hounds'),
    R(3, -1, 'drake', '1', note='a dune drake'),
    R(3, 0, 'fire_elemental', '1', note='a fire elemental'),
    R(3, 0, 'orc', '1', complication=True, note='an orc warlord of the waste'),
    R(3, 0, 'air_elemental', '1', note='a sandstorm with a mind'),
    R(2, 0, 'monstrous_beast', '1', note='a sphinx, hungry'),
    R(2, 1, 'great_dragon', '1', M, note='a desert dragon\'s wyrmling'),
    R(1, 1, 'place_spirit', '1', M, note='a djinn\'s servant'),
  ], 5: [
    R(3, -1, 'drake', '1', note='a war-drake'),
    R(3, -1, 'hellbeast', '1', note='the hound of a burning god'),
    R(3, 0, 'great_dragon', '1', note='a desert dragon on the wing'),
    R(3, 0, 'fire_elemental', '1', M, note='an efreet\'s herald'),
    R(3, 0, 'place_spirit', '1', M, note='a djinn bound to a ruin'),
    R(2, 0, 'air_elemental', '1', M, note='the wind of the deep desert'),
    R(2, 1, 'fire_elemental', '1', S, note='an efreet lord'),
    R(1, 1, 'monstrous_beast', '1', S, note='the great sphinx'),
  ]}

# -------------------------------------------------------------------------------------------- frozen
ENC['terrain.frozen'] = {1: [
    R(3, -1, 'wolf', '1-2', note='a white wolf'),
    R(3, -1, 'goblin', '2', ambush=True, note='snow goblins under white hides'),
    R(3, 0, 'skeleton', '4-6', M, complication=True, note='an old army under the ice'),
    R(3, 0, 'orc', '5-7', M, note='orc reavers'),
    R(3, 0, 'ghost', '1', E, when='night', note='the ghost of a frozen army\'s captain'),
    R(2, 0, 'wolf', '2', note='a pair of white wolves'),
    R(2, 1, 'bear', '1', note='an ice bear'),
    R(1, 1, 'great_cat', '1', M, note='a snow cat'),
  ], 2: [
    R(3, -1, 'wolf', '4-6', M, note='wolves'),
    R(3, -1, 'orc', '4-6', M, note='orc reavers'),
    R(3, 0, 'bear', '1', E, note='an ice bear'),
    R(3, 0, 'frost_elemental', '1', complication=True, note='a blizzard that walks'),
    R(3, 0, 'great_cat', '2', note='snow leopards'),
    R(2, 0, 'wight', '1', E, note='a barrow-wight of the ice'),
    R(2, 1, 'troll', '1', M, note='an ice-troll\'s whelp'),
    R(1, 1, 'wraith', '1', M, note='a wraith in the white-out'),
  ], 3: [
    R(3, -1, 'bear', '2', note='two ice bears'),
    R(3, -1, 'wolf', '6-8', M, note='a winter pack'),
    R(3, 0, 'troll', '1', E, note='an ice troll'),
    R(3, 0, 'frost_elemental', '1', E, note='a frost elemental'),
    R(3, 0, 'wight', '1', complication=True, note='a wight leading the frozen dead'),
    R(2, 0, 'wyrm', '1', M, note='an ice-wyrm\'s young'),
    R(2, 1, 'giant', '1', M, note='a frost giant\'s thrall'),
    R(1, 1, 'celestial', '1', M, note='a herald of the aurora'),
  ], 4: [
    R(3, -1, 'troll', '1', note='an ice troll'),
    R(3, -1, 'wight', '1', note='a barrow-king\'s wight'),
    R(3, 0, 'giant', '1', note='a frost giant'),
    R(3, 0, 'frost_elemental', '1', complication=True, note='the blizzard\'s heart'),
    R(3, 0, 'wyrm', '1', note='an ice-wyrm'),
    R(2, 0, 'golem', '1', note='an ice-golem from a drowned age'),
    R(2, 1, 'giant', '1', M, note='a frost-jarl\'s herald'),
    R(1, 1, 'wraith', '1', M, note='a wraith of the long night'),
  ], 5: [
    R(3, -1, 'troll', '1', note='an ice-troll chieftain'),
    R(3, -1, 'wyrm', '1', note='an ice-wyrm'),
    R(3, 0, 'giant', '1', M, note='a frost jarl\'s huscarl'),
    R(3, 0, 'frost_elemental', '1', M, note='the cold that walks'),
    R(3, 0, 'wraith', '1', M, note='a lord of the long night\'s herald'),
    R(2, 0, 'golem', '1', M, note='a sentinel of the old ice'),
    R(2, 1, 'giant', '1', S, note='the frost jarl'),
    R(1, 1, 'frost_elemental', '1', S, note='the white death'),
  ]}

# --------------------------------------------------------------------------------------------- water
ENC['terrain.water'] = {1: [
    R(3, -1, 'reptile', '1', note='a water snake'),
    R(3, -1, 'raptor', '1', note='a fish-eagle that wants your catch'),
    R(3, 0, 'brigand', '5-7', M, ambush=True, note='river pirates'),
    R(3, 0, 'lizardfolk', '5-7', M, note='lizardfolk in dugouts'),
    R(3, 0, 'wild_fey', '5-7', M, complication=True, note='nixies who want a song'),
    R(2, 0, 'ghost', '1', when='night', note='a drowned ferryman'),
    R(2, 1, 'water_beast', '1', note='a pike as long as the boat'),
    R(1, 1, 'reptile', '1', note='a river crocodile'),
  ], 2: [
    R(3, -1, 'brigand', '4-6', M, ambush=True, note='river pirates'),
    R(3, -1, 'lizardfolk', '4-6', M, note='lizardfolk raiders'),
    R(3, 0, 'water_beast', '1', E, note='a river-shark'),
    R(3, 0, 'water_elemental', '1', complication=True, note='a current with a will'),
    R(3, 0, 'brigand', '2', note='a pirate captain and her mate'),
    R(2, 0, 'place_spirit', '1', note='the river\'s spirit, offended'),
    R(2, 1, 'wyrm', '1', M, note='a water-wyrm\'s young'),
    R(1, 1, 'reptile', '1', M, note='a crocodile grown old'),
  ], 3: [
    R(3, -1, 'lizardfolk', '2', note='lizardfolk raiders'),
    R(3, -1, 'brigand', '6-8', M, note='a pirate crew'),
    R(3, 0, 'water_beast', '1', complication=True, note='a giant octopus under the hull'),
    R(3, 0, 'water_elemental', '1', E, note='a water elemental'),
    R(3, 0, 'reptile', '1', E, note='a great crocodile'),
    R(2, 0, 'place_spirit', '1', E, note='the lake\'s lady, displeased'),
    R(2, 1, 'wyrm', '1', M, note='a sea-serpent\'s young'),
    R(1, 1, 'aberration', '1', M, note='something from the deep, testing the hull'),
  ], 4: [
    R(3, -1, 'reptile', '2', note='crocodiles in the shallows'),
    R(3, -1, 'water_elemental', '1', note='a whirlpool'),
    R(3, 0, 'wyrm', '1', note='a sea-serpent'),
    R(3, 0, 'water_beast', '1', complication=True, note='a giant octopus'),
    R(3, 0, 'place_spirit', '1', note='the river-god\'s anger'),
    R(2, 0, 'aberration', '1', M, note='a tentacled thing under the jetty'),
    R(2, 1, 'wyrm', '1', M, note='a dragon-turtle\'s get'),
    R(1, 1, 'great_dragon', '1', M, note='a sea dragon\'s young'),
  ], 5: [
    R(3, -1, 'wyrm', '1', note='a sea-serpent'),
    R(3, -1, 'water_beast', '1', note='a kraken\'s young'),
    R(3, 0, 'aberration', '1', M, note='a tendril of the thing in the abyss'),
    R(3, 0, 'water_elemental', '1', M, note='a wave with a will'),
    R(3, 0, 'place_spirit', '1', M, note='a river-god\'s messenger'),
    R(2, 0, 'great_dragon', '1', note='a sea dragon'),
    R(2, 1, 'wyrm', '1', S, note='the leviathan'),
    R(1, 1, 'water_elemental', '1', S, note='the flood of the age'),
  ]}

# --------------------------------------------------------------------------------------- underground
ENC['terrain.underground'] = {1: [
    R(3, -1, 'giant_vermin', '1', note='a cave spider'),
    R(3, -1, 'vermin_swarm', '1', note='a stream of rats'),
    R(3, 0, 'goblin', '5-7', M, ambush=True, note='goblins in the dark'),
    R(3, 0, 'skeleton', '5-7', M, note='skeletons on an old watch'),
    R(3, 0, 'ooze', '1', complication=True, note='a slime on the ceiling'),
    R(2, 0, 'fungal', '1-2', note='walking fungus'),
    R(2, 1, 'clockwork', '1', note='a dwarf-made sentry still on duty'),
    R(1, 1, 'lesser_demon', '1', M, note='an imp from a crack'),
  ], 2: [
    R(3, -1, 'goblin', '4-6', M, ambush=True, note='a goblin war-party'),
    R(3, -1, 'skeleton', '4-6', M, note='a skeleton patrol'),
    R(3, 0, 'ghoul', '2', note='ghouls'),
    R(3, 0, 'dwarf_holdguard', '2', note='holdguards defending a seam'),
    R(3, 0, 'clockwork', '1', E, complication=True, note='a clockwork guardian on a broken errand'),
    R(2, 0, 'ooze', '1', E, note='an ooze'),
    R(2, 1, 'troll', '1', M, note='a cave-troll\'s whelp'),
    R(1, 1, 'aberration', '1', M, note='a thing from the deep dark'),
  ], 3: [
    R(3, -1, 'ghoul', '6-8', M, note='a ghoul pack'),
    R(3, -1, 'cultist', '6-8', M, note='cultists of the deep'),
    R(3, 0, 'troll', '1', E, note='a cave troll'),
    R(3, 0, 'aberration', '1', M, complication=True, note='a mind-thing\'s servant'),
    R(3, 0, 'drake', '1', E, note='a cave drake'),
    R(2, 0, 'golem', '1', note='a golem guarding nothing'),
    R(2, 1, 'wraith', '1', M, note='a wraith from a sealed vault'),
    R(1, 1, 'earth_elemental', '1', M, note='a rock that moves'),
  ], 4: [
    R(3, -1, 'troll', '1', note='a cave troll'),
    R(3, -1, 'golem', '1', note='a golem'),
    R(3, 0, 'aberration', '1', note='a mind-thing'),
    R(3, 0, 'wyrm', '1', complication=True, note='a purple worm in its tunnel'),
    R(3, 0, 'earth_elemental', '1', note='an earth elemental'),
    R(2, 0, 'abomination', '1', note='an abomination loose from a lab'),
    R(2, 1, 'lich', '1', M, note='a lich\'s apprentice'),
    R(1, 1, 'greater_demon', '1', M, note='a demon prince\'s hound'),
  ], 5: [
    R(3, -1, 'aberration', '1', note='a mind-thing'),
    R(3, -1, 'wyrm', '1', note='a purple worm'),
    R(3, 0, 'lich', '1', note='a lich at its studies'),
    R(3, 0, 'greater_demon', '1', M, note='a demon prince\'s champion'),
    R(3, 0, 'golem', '1', M, note='an iron sentinel'),
    R(2, 0, 'abomination', '1', M, note='a flesh-horror'),
    R(2, 1, 'aberration', '1', S, note='the elder brain'),
    R(1, 1, 'fire_elemental', '1', S, note='the fire at the root of the world'),
  ]}

# ---------------------------------------------------------------------------------------------- ruin
ENC['terrain.ruin'] = {1: [
    R(3, -1, 'giant_vermin', '1', note='a giant centipede'),
    R(3, -1, 'skeleton', '1-2', note='skeletons'),
    R(3, 0, 'ghoul', '5-7', M, note='a ghoul pack'),
    R(3, 0, 'brigand', '5-7', M, complication=True, note='looters who were here first'),
    R(3, 0, 'cultist', '5-7', M, note='cultists at an old altar'),
    R(2, 0, 'animated', '2', note='armour that stands up'),
    R(2, 1, 'ghost', '1', note='a ghost'),
    R(1, 1, 'wight', '1', M, note='a wight\'s sworn'),
  ], 2: [
    R(3, -1, 'skeleton', '4-6', M, note='skeletons'),
    R(3, -1, 'zombie', '4-6', M, note='the dead of the ruin'),
    R(3, 0, 'ghoul', '2', note='a ghoul pair'),
    R(3, 0, 'wight', '1', E, complication=True, note='a wight lord of a fallen hall'),
    R(3, 0, 'cultist', '2', note='a cult\'s priests'),
    R(2, 0, 'golem', '1', note='a stone guardian'),
    R(2, 1, 'vampire', '1', M, note='a vampire spawn'),
    R(1, 1, 'wraith', '1', M, note='a wraith'),
  ], 3: [
    R(3, -1, 'ghoul', '6-8', M, note='a ghoul pack'),
    R(3, -1, 'wight', '2', note='a pair of wights'),
    R(3, 0, 'wraith', '1', E, note='a wraith'),
    R(3, 0, 'vampire', '1', M, complication=True, note='a vampire\'s get'),
    R(3, 0, 'golem', '1', E, note='a golem'),
    R(2, 0, 'enforcer', '1', M, note='a devil\'s debt-collector'),
    R(2, 1, 'lich', '1', M, note='a lich\'s apprentice'),
    R(1, 1, 'deathlord', '1', M, note='a deathlord\'s herald'),
  ], 4: [
    R(3, -1, 'wraith', '1', note='a wraith'),
    R(3, -1, 'golem', '1', note='a golem'),
    R(3, 0, 'vampire', '1', note='a vampire'),
    R(3, 0, 'lich', '1', M, complication=True, note='a lich\'s apprentice'),
    R(3, 0, 'deathlord', '1', M, note='a deathlord\'s champion'),
    R(2, 0, 'celestial', '1', M, note='a fallen guardian'),
    R(2, 1, 'great_dragon', '1', M, note='a dragon\'s wyrmling'),
    R(1, 1, 'greater_demon', '1', M, note='a demon\'s herald'),
  ], 5: [
    R(3, -1, 'vampire', '1', note='a vampire'),
    R(3, -1, 'wraith', '1', note='a wraith-lord'),
    R(3, 0, 'lich', '1', note='a lich'),
    R(3, 0, 'deathlord', '1', M, note='a deathlord\'s champion'),
    R(3, 0, 'greater_demon', '1', M, note='a demon\'s herald'),
    R(2, 0, 'great_dragon', '1', note='a dragon on its hoard'),
    R(2, 1, 'deathlord', '1', S, note='the deathlord'),
    R(1, 1, 'lich', '1', S, note='the lich-king'),
  ]}


def render_t16():
    """T-10-16 for the chapter: one line per terrain and home band (python 10_data_enc.py)."""
    short = {'minion': 'minion', 'elite': 'elite', 'solo': 'solo'}
    out = ['| Terrain | Home | Threat rows (d20: faces 1-6 home - 1 · 7-17 home · 18-20 home + 1) |', '|---|---|---|']
    for t, per in ENC.items():
        for h in range(1, 6):
            cells = []
            for d in per[h]:
                shape = d['count'] + ('' if d['variant'] == 'standard' else ' ' + short[d['variant']])
                flags = (' (ambush)' if d['ambush'] else '') + (' (complication)' if d['complication'] else '') + (' (night)' if d['when'] == 'night' else '')
                lab = {'home-1': '−1', 'home': '', 'home+1': '+1'}[d['band']]
                cells.append('%s%s: %s × %s%s' % (d['ref'][0][5:].replace('_', ' '), (' [' + lab + ']') if lab else '', d.get('note', ''), shape, flags))
            out.append('| %s | %d | %s |' % (t.split('.')[-1] if h == 1 else '', h, ' · '.join(cells)))
    return '\n'.join(out)


if __name__ == '__main__':
    print(render_t16())
