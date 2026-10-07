"""11-gen_factions.py -- generates rules/data/factions.yaml for chapter 11 (11.3, 11.8, T-11-4).

Ratings by tier are COMPUTED so that every template satisfies 11.3.4 exactly: four ratings, each 0..tier+2,
summing to 4 + 2*tier; increments follow the template's priority cycle (its character), skipping capped
ratings. Run: python 11-gen_factions.py > ../../data/factions.yaml   (validated by the asserts below)
"""
import yaml, sys, os

R = ['force', 'cunning', 'wealth', 'sway']

def ratings_by_tier(cycle):
    out = {}
    r = {k: 1 for k in R}
    out[0] = dict(r)
    i = 0
    for t in range(1, 6):
        cap = t + 2
        added = 0
        guard = 0
        while added < 2:
            k = cycle[i % len(cycle)]; i += 1; guard += 1
            if r[k] < cap:
                r[k] += 1; added += 1
            assert guard < 100
        out[t] = dict(r)
        assert sum(r.values()) == 4 + 2 * t, (cycle, t, r)
        assert all(0 <= v <= t + 2 for v in r.values())
    return {t: [out[t][k] for k in R] for t in out}

OMEN_GENERIC = {
    'stirring': ['strangers wearing its colors on the road', 'its people buying more than they need'],
    'building': ['its notices on every door', 'its men where they were not before'],
    'imminent': ['its leaders seen together, late, with the lamps lit', 'a hush in its houses; everyone waiting'],
}
ATT_OMEN = {
    'stirring': ['a stranger asks the innkeeper which room is yours', 'someone was asking after you at the market'],
    'building': ['the same two faces at the market two days running', 'your name spoken, then silence, as you enter'],
    'imminent': ["your door's latch has been tried in the night", 'a mark chalked on your door at dawn'],
}
FATES = {
    'dies': 'the faction loses hold; its stage becomes declining; the next officer is named successor; a situation of template succession',
    'captured': 'the faction loses hold; its next action is strike or court against the captor (a rescue); a ransom demand is news',
    'turned': 'the faction loses hold twice; one of its secrets passes to the turned linchpin; a rival gains hold',
    'exposed': 'the faction loses hold; its status toward the exposer -1; news in its seat; a situation of template scandal',
}

def fate_effects(kind):
    base = {'dies': [{'effect_id': 'eff.11.hold_step', 'params': {'faction': 'self', 'steps': -1}},
                     {'effect_id': 'eff.11.stage_set', 'params': {'faction': 'self', 'stage': 'declining'}},
                     {'effect_id': 'eff.11.new_situation', 'params': {'template': 'sit_t.succession', 'region': 'faction.seat.region', 'roles': {'faction': 'self'}}}],
            'captured': [{'effect_id': 'eff.11.hold_step', 'params': {'faction': 'self', 'steps': -1}},
                         {'effect_id': 'eff.write_fact', 'params': {'subject': 'self', 'predicate': 'next_action', 'value': 'strike_or_court_captor'}}],
            'turned': [{'effect_id': 'eff.11.hold_step', 'params': {'faction': 'self', 'steps': -2}},
                       {'effect_id': 'eff.reveal', 'params': {'sealed_ref': 'faction.secret[0] to the turned linchpin'}}],
            'exposed': [{'effect_id': 'eff.11.hold_step', 'params': {'faction': 'self', 'steps': -1}},
                        {'effect_id': 'eff.11.new_situation', 'params': {'template': 'sit_t.scandal', 'region': 'faction.seat.region', 'roles': {'faction': 'self'}}}]}
    return base[kind]

def T(id_, name, org, temper, cycle, values, patron, ladder, duties, fields, boon_base, boon_sig, goals, courtable=True,
      branch_default=None, entangle_flavor=''):
    return {
        'id': id_, 'name': name, 'tags': [org], 'org_tags': [org], 'branch_default_for': branch_default,
        'temperament': temper, 'rating_cycle': cycle, 'ratings_by_tier': ratings_by_tier(cycle),
        'values': [{'axis': a, 'pole': p} for a, p in values], 'patron_deeds': patron,
        'rank_ladder': ladder, 'duties': duties, 'fields': [{'archetype': a, 'role': r} for a, r in fields],
        'boon_base': boon_base, 'boon_signature': boon_sig,
        'goal_list': [{'d6': i + 1, 'kind': k, 'rating': rt, 'text': tx} for i, (k, rt, tx) in enumerate(goals)],
        'goal_omens': OMEN_GENERIC, 'attention_omens': ATT_OMEN,
        'fate_list': [{'fate': k, 'consequence': FATES[k], 'effects': fate_effects(k)} for k in ['dies', 'captured', 'turned', 'exposed']],
        'courtable': courtable, 'sittings': ['quarter days'], 'entanglement_flavor': entangle_flavor,
        'lifecycle': 'provisional', 'basis': ['11.3.18', 'R6 B-R2', 'DL-11-06'],
    }

G = lambda k, r, t: (k, r, t)
templates = [
    T('ftpl.crown_noble', 'Noble house', 'org.crown.noble', 'cautious', ['sway', 'force', 'wealth', 'sway', 'cunning'],
      [('conduct.loyalty', '+'), ('conduct.courage', '+'), ('conduct.loyalty', '-')], ['deed.martial.mounted', 'deed.influence.etiquette', 'deed.martial.tactics'],
      'rl.noble', ['never yields the house\'s land without the lord\'s word', 'never hears a commoner\'s suit at table', 'never leaves a kinsman unavenged'],
      [('arch.soldier', 'rank_and_file'), ('arch.knight', 'officer'), ('arch.knight', 'champion')], 'item.jewelry.ring', 'prop.commanding',
      [G('grow', 'sway', 'win a marriage that brings a manor'), G('grow', 'wealth', 'raise the rents of the valley'), G('dominate', 'force', 'humble the rival house'),
       G('change', 'sway', 'win the lord\'s seat at the regional court'), G('change', 'force', 'clear the bandits from its roads'), G('dominate', 'cunning', 'prove the rival\'s claim false')],
      branch_default=None),
    T('ftpl.crown_civic', 'Town council and watch', 'org.crown.civic', 'steadfast', ['sway', 'wealth', 'force', 'sway', 'cunning'],
      [('conduct.justice', '+'), ('conduct.honesty', '+'), ('conduct.justice', '-')], ['deed.influence.persuasion', 'deed.lore.law', 'deed.martial.tactics'],
      'rl.civic', ['never opens the gate after curfew without the reeve\'s seal', 'never lets a prisoner go without a hearing', 'never takes coin to forget a crime'],
      [('arch.soldier', 'rank_and_file'), ('arch.soldier', 'officer'), ('arch.knight', 'champion')], 'item.garment.cloak', 'prop.ward_fear',
      [G('change', 'sway', 'pass a charter of market rights'), G('grow', 'wealth', 'build the new town wall'), G('change', 'force', 'rid the streets of the gangs'),
       G('grow', 'sway', 'win the support of the guilds'), G('dominate', 'cunning', 'break the smugglers\' hold on the docks'), G('change', 'wealth', 'lay in grain against the winter')],
      branch_default='org.crown'),
    T('ftpl.crown_military', 'Garrison or levy', 'org.crown.military', 'aggressive', ['force', 'force', 'sway', 'cunning', 'wealth'],
      [('conduct.courage', '+'), ('conduct.loyalty', '+'), ('conduct.courage', '-')], ['deed.martial', 'deed.martial.tactics'],
      'rl.military', ['never abandons a post without orders', 'never parleys with raiders under arms', 'never strikes a man who has yielded'],
      [('arch.soldier', 'rank_and_file'), ('arch.knight', 'officer'), ('arch.knight', 'champion')], 'item.weapon.blade', 'prop.onhit_expose',
      [G('change', 'force', 'hold the pass through the winter'), G('dominate', 'force', 'break the raiders\' camp'), G('grow', 'sway', 'win more levies from the villages'),
       G('grow', 'wealth', 'rebuild the old fort'), G('change', 'cunning', 'find the traitor in the ranks'), G('dominate', 'force', 'take the border tower')]),
    T('ftpl.faith_temple', 'Temple', 'org.faith.temple', 'steadfast', ['sway', 'sway', 'wealth', 'cunning', 'force'],
      [('conduct.piety', '+'), ('conduct.mercy', '+'), ('conduct.piety', '-')], ['deed.divine', 'deed.lore.religion', 'deed.lore.medicine'],
      'rl.temple', ['never refuses sanctuary to one who asks it', 'never lets the dead lie unblessed', 'never sells a sacrament'],
      [('arch.soldier', 'rank_and_file'), ('arch.folk_mage', 'officer'), ('arch.knight', 'champion')], 'item.jewelry.amulet', 'prop.resist_radiance',
      [G('grow', 'sway', 'raise a new shrine in the hill villages'), G('change', 'sway', 'end the old rites at the standing stones'), G('grow', 'wealth', 'fill the alms-house before winter'),
       G('dominate', 'sway', 'win the faithful from the heretic preacher'), G('change', 'cunning', 'recover the stolen relic'), G('change', 'sway', 'consecrate the haunted field')],
      branch_default='org.faith'),
    T('ftpl.faith_shrine', 'Wayside shrine and its keepers', 'org.faith.shrine', 'cautious', ['sway', 'cunning', 'sway', 'wealth', 'force'],
      [('conduct.piety', '+'), ('conduct.generosity', '+'), ('conduct.piety', '-')], ['deed.divine.rites', 'deed.lore.religion'],
      'rl.shrine', ['never lets the lamp go out', 'never names the god to an unbeliever', 'never turns a pilgrim away hungry'],
      [('arch.folk_mage', 'rank_and_file'), ('arch.folk_mage', 'officer'), ('arch.ancestor', 'champion')], 'item.jewelry.charm', 'prop.physicks',
      [G('grow', 'sway', 'draw pilgrims for the feast day'), G('change', 'sway', 'heal the village\'s sickness'), G('grow', 'wealth', 'repair the shrine roof'),
       G('change', 'cunning', 'learn what woke in the old barrow'), G('dominate', 'sway', 'shame the tavern keeper who mocks the rites'), G('grow', 'sway', 'win a keeper for the north shrine')],
      courtable=False),
    T('ftpl.order_knightly', 'Knightly order', 'org.order.knightly', 'zealous', ['force', 'sway', 'force', 'cunning', 'wealth'],
      [('conduct.courage', '+'), ('conduct.protection', '+'), ('conduct.courage', '-')], ['deed.martial', 'deed.divine.oaths', 'deed.martial.mounted'],
      'rl.knightly', ['never refuses a challenge to single combat', 'never leaves the weak undefended when asked', 'never breaks a sworn word'],
      [('arch.soldier', 'rank_and_file'), ('arch.knight', 'officer'), ('arch.knight', 'champion')], 'item.weapon.blade', 'prop.bane_horror',
      [G('dominate', 'force', 'destroy the monster in the fen'), G('grow', 'sway', 'raise a chapter-house in the town'), G('change', 'force', 'escort the pilgrims to the hill shrine'),
       G('dominate', 'force', 'drive the cult from the hills'), G('grow', 'wealth', 'win a lord\'s endowment'), G('change', 'sway', 'end the feud between two houses')],
      branch_default='org.order'),
    T('ftpl.order_arcane', 'Arcane circle or college', 'org.order.arcane', 'secretive', ['cunning', 'sway', 'cunning', 'wealth', 'force'],
      [('conduct.restraint', '+'), ('conduct.honesty', '+'), ('conduct.restraint', '-')], ['deed.arcane', 'deed.lore.arcana'],
      'rl.arcane', ['never teaches a forbidden working to the uninitiated', 'never leaves a book of the circle in strange hands', 'never casts in the presence of the profane on the circle\'s business'],
      [('arch.folk_mage', 'rank_and_file'), ('arch.folk_mage', 'officer'), ('arch.homunculus', 'champion')], 'item.tool.implement', 'prop.resist_arcane',
      [G('change', 'cunning', 'recover the lost grimoire'), G('grow', 'wealth', 'build a tower of study'), G('dominate', 'cunning', 'silence the hedge-sorcerers of the valley'),
       G('change', 'cunning', 'bind the spirit of the ruin'), G('grow', 'sway', 'win a seat at the lord\'s council'), G('change', 'cunning', 'learn what the comet means')]),
    T('ftpl.order_druidic', 'Druidic circle', 'org.order.druidic', 'cautious', ['sway', 'cunning', 'force', 'sway', 'wealth'],
      [('conduct.restraint', '+'), ('conduct.protection', '+'), ('conduct.restraint', '-')], ['deed.primal', 'deed.wilds'],
      'rl.druidic', ['never fells a living oak', 'never lets a beast be killed for sport in the grove', 'never speaks the circle\'s names to the town'],
      [('arch.elf_warden', 'rank_and_file'), ('arch.folk_mage', 'officer'), ('arch.place_spirit', 'champion')], 'item.jewelry.charm', 'prop.beastwise',
      [G('change', 'sway', 'stop the felling of the old wood'), G('change', 'cunning', 'heal the blighted spring'), G('dominate', 'force', 'drive the miners from the sacred hill'),
       G('grow', 'sway', 'win the hunters to the old ways'), G('change', 'sway', 'renew the boundary stones'), G('grow', 'cunning', 'find a new keeper for the grove')]),
    T('ftpl.order_hunters', "Hunters' lodge", 'org.order.hunters', 'aggressive', ['force', 'cunning', 'force', 'sway', 'wealth'],
      [('conduct.courage', '+'), ('conduct.protection', '+'), ('conduct.courage', '-')], ['deed.wilds.tracking', 'deed.lore.bestiary', 'deed.martial.archery'],
      'rl.hunters', ['never leaves a wounded beast to suffer', 'never sells a kill it did not make', 'never takes a bounty on a man'],
      [('arch.elf_warden', 'rank_and_file'), ('arch.elf_warden', 'officer'), ('arch.knight', 'champion')], 'item.weapon.bow', 'prop.bane_beast',
      [G('dominate', 'force', 'kill the beast of the high moor'), G('grow', 'sway', 'open a lodge in the next valley'), G('change', 'cunning', 'learn where the wyverns nest'),
       G('grow', 'wealth', 'win the margrave\'s bounty contract'), G('dominate', 'force', 'clear the wolves from the sheep runs'), G('change', 'force', 'burn the spider nests in the old mine')]),
    T('ftpl.guild_merchant', 'Merchant guild', 'org.guild.merchant', 'mercantile', ['wealth', 'cunning', 'wealth', 'sway', 'force'],
      [('conduct.honesty', '+'), ('conduct.generosity', '-'), ('conduct.honesty', '-')], ['deed.influence.trade'],
      'rl.merchant', ['never sells below the tally price', 'never extends credit to one who defaulted', 'never trades with the guild\'s declared enemies'],
      [('arch.soldier', 'rank_and_file'), ('arch.brigand', 'officer'), ('arch.soldier', 'champion')], 'item.jewelry.ring', 'prop.haggler',
      [G('grow', 'wealth', 'corner the salt trade'), G('dominate', 'wealth', 'ruin the rival trading house'), G('change', 'sway', 'win the toll on the bridge'),
       G('grow', 'wealth', 'open a warehouse in the next town'), G('change', 'cunning', 'buy the mill and the millrace'), G('dominate', 'cunning', 'break the smugglers\' prices')],
      branch_default='org.guild'),
    T('ftpl.guild_craft', 'Craft guild', 'org.guild.craft', 'cautious', ['wealth', 'sway', 'wealth', 'cunning', 'force'],
      [('conduct.honesty', '+'), ('conduct.generosity', '+'), ('conduct.honesty', '-')], ['deed.craft'],
      'rl.craft', ['never passes shoddy work under the guild\'s mark', 'never teaches a guild secret outside the guild', 'never works on a feast day'],
      [('arch.dwarf_holdguard', 'rank_and_file'), ('arch.soldier', 'officer'), ('arch.dwarf_holdguard', 'champion')], 'item.tool.trade', 'prop.masters_mark',
      [G('grow', 'wealth', 'win the commission for the cathedral doors'), G('change', 'sway', 'win a charter excluding outsiders'), G('grow', 'wealth', 'reopen the old forge'),
       G('dominate', 'sway', 'drive the unlicensed smiths out of town'), G('change', 'cunning', 'learn the rival guild\'s secret'), G('grow', 'sway', 'raise a guildhall')]),
    T('ftpl.guild_scholarly', 'Scholars\' guild or library', 'org.guild.scholarly', 'cautious', ['cunning', 'sway', 'wealth', 'cunning', 'force'],
      [('conduct.honesty', '+'), ('conduct.humility', '+'), ('conduct.honesty', '-')], ['deed.lore'],
      'rl.scholarly', ['never lets a book leave the library unsigned', 'never burns a book', 'never teaches what it has not proven'],
      [('arch.folk_mage', 'rank_and_file'), ('arch.folk_mage', 'officer'), ('arch.homunculus', 'champion')], 'item.tool.implement', 'prop.sages',
      [G('change', 'cunning', 'recover the lost chronicle'), G('grow', 'wealth', 'build a new reading hall'), G('change', 'sway', 'win the lord\'s patronage'),
       G('dominate', 'sway', 'disprove the rival scholars'), G('change', 'cunning', 'map the old ruins'), G('grow', 'sway', 'open a school in the town')]),
    T('ftpl.company_mercenary', 'Mercenary company', 'org.company.mercenary', 'aggressive', ['force', 'wealth', 'force', 'cunning', 'sway'],
      [('conduct.loyalty', '+'), ('conduct.courage', '+'), ('conduct.loyalty', '-')], ['deed.martial'],
      'rl.mercenary', ['never fights for two paymasters at once', 'never leaves its dead on the field', 'never breaks a contract before its term'],
      [('arch.brigand', 'rank_and_file'), ('arch.soldier', 'officer'), ('arch.knight', 'champion')], 'item.weapon.axe', 'prop.onhit_expose',
      [G('grow', 'wealth', 'win a lord\'s contract for the season'), G('dominate', 'force', 'beat the rival company in the field'), G('grow', 'force', 'recruit a second banner'),
       G('change', 'force', 'take the toll-castle for its paymaster'), G('grow', 'wealth', 'collect the arrears it is owed'), G('change', 'sway', 'win a charter as the town\'s guard')],
      branch_default='org.company'),
    T('ftpl.company_trading', 'Trading company or caravan house', 'org.company.trading', 'mercantile', ['wealth', 'cunning', 'wealth', 'force', 'sway'],
      [('conduct.honesty', '+'), ('conduct.loyalty', '+'), ('conduct.honesty', '-')], ['deed.influence.trade', 'deed.wilds.navigation'],
      'rl.trading', ['never leaves a wagon behind on the road', 'never carries cargo it has not seen', 'never shares a route with outsiders'],
      [('arch.soldier', 'rank_and_file'), ('arch.soldier', 'officer'), ('arch.knight', 'champion')], 'item.garment.cloak', 'prop.tracker',
      [G('grow', 'wealth', 'open the road to the far market'), G('change', 'force', 'clear the bandits from the caravan road'), G('dominate', 'wealth', 'undercut the guild\'s prices'),
       G('grow', 'wealth', 'build a waystation'), G('change', 'sway', 'win safe-conduct from the margrave'), G('grow', 'cunning', 'find a pass through the hills')]),
    T('ftpl.clan_family', 'Family or household', 'org.clan.family', 'cautious', ['sway', 'wealth', 'force', 'cunning', 'sway'],
      [('conduct.loyalty', '+'), ('conduct.generosity', '+'), ('conduct.loyalty', '-')], ['deed.influence', 'deed.craft'],
      'rl.household', ['never sells the family land', 'never shuts the door on kin', 'never forgives a slight to its dead'],
      [('arch.soldier', 'rank_and_file'), ('arch.soldier', 'officer'), ('arch.knight', 'champion')], 'item.jewelry.ring', 'prop.fine_cut',
      [G('grow', 'wealth', 'buy back the lost field'), G('change', 'sway', 'marry the eldest daughter well'), G('dominate', 'sway', 'settle the old feud on its own terms'),
       G('grow', 'sway', 'win a seat on the council'), G('change', 'cunning', 'find the missing heir'), G('grow', 'wealth', 'rebuild the burned hall')],
      branch_default='org.clan'),
    T('ftpl.outlaw_thieves', "Thieves' guild", 'org.outlaw.thieves', 'secretive', ['cunning', 'wealth', 'cunning', 'force', 'sway'],
      [('conduct.loyalty', '+'), ('conduct.honesty', '-'), ('conduct.loyalty', '-')], ['deed.guile'],
      'rl.thieves', ['never steals from the guild\'s own', 'never talks to the watch', 'never works another\'s ground without leave'],
      [('arch.brigand', 'rank_and_file'), ('arch.brigand', 'officer'), ('arch.brigand', 'champion')], 'item.garment.gloves', 'prop.deft',
      [G('grow', 'wealth', 'take the docks\' protection money'), G('dominate', 'cunning', 'ruin the watch-captain'), G('change', 'cunning', 'rob the merchant guild\'s strongroom'),
       G('grow', 'cunning', 'plant a man in the reeve\'s house'), G('dominate', 'force', 'drive the rival crew out of the market'), G('change', 'wealth', 'buy the magistrate')]),
    T('ftpl.outlaw_bandits', 'Bandit company', 'org.outlaw.bandits', 'aggressive', ['force', 'cunning', 'force', 'wealth', 'sway'],
      [('conduct.courage', '+'), ('conduct.loyalty', '+'), ('conduct.mercy', '+')], ['deed.guile.ambush', 'deed.martial'],
      'rl.bandits', ['never lets a witness walk who saw a face', 'never splits the take before the chief has his share', 'never camps two nights in the same place'],
      [('arch.brigand', 'rank_and_file'), ('arch.brigand', 'officer'), ('arch.ogre', 'champion')], 'item.weapon.blade', 'prop.onhit_expose',
      [G('dominate', 'force', 'own the road from the ford to the hills'), G('grow', 'force', 'take in the deserters'), G('change', 'cunning', 'rob the tax wagon'),
       G('grow', 'wealth', 'buy a fence in town'), G('dominate', 'force', 'burn the toll-house'), G('change', 'force', 'ransom the margrave\'s cousin')],
      branch_default='org.outlaw'),
    T('ftpl.cult', 'Cult', 'org.cult', 'secretive', ['cunning', 'sway', 'cunning', 'force', 'wealth'],
      [('conduct.piety', '+'), ('conduct.mercy', '-'), ('conduct.mercy', '+')], ['deed.divine.pact', 'deed.arcane.necromancy', 'deed.arcane.summoning'],
      'rl.cult', ['never names the master to the unsworn', 'never lets the rite go unfinished', 'never suffers an apostate to live'],
      [('arch.cultist', 'rank_and_file'), ('arch.cultist', 'officer'), ('arch.lesser_demon', 'champion')], 'item.jewelry.amulet', 'prop.honeyed',
      [G('change', 'cunning', 'wake the thing in the hill'), G('grow', 'sway', 'win converts in the poor quarter'), G('change', 'cunning', 'steal the relic from the temple'),
       G('dominate', 'cunning', 'kill the priest who preaches against it'), G('grow', 'wealth', 'buy the old chapel'), G('change', 'force', 'take a sacrifice at the new moon')],
      courtable=True, branch_default='org.cult'),
]
assert len(templates) == 18

doc = {
    'schema_version': 1,
    'agenda': {
        'overrides': [
            {'order': 1, 'when': 'slip last turn', 'action': 'recover'},
            {'order': 2, 'when': 'relation -3 with a faction whose seat or a hold is in the same region, and d6 <= 3', 'action': 'strike', 'target': 'that faction'},  # [revision: I-061]
            {'order': 3, 'when': 'status toward the PC >= +2 and (a ransom due, a threat bang naming the PC holding, or a reward owed; or d6 = 1: the opportunity bang)', 'action': 'aid_pc'},
        ],
        'dice': 'each override that names a d6 rolls its own, only when its condition holds; the temperament row is a fresh d6 (11.3.7) [revision: I-061]',
        'rows': {
            'aggressive': ['strike if a rival at <= -2', 'strike if a rival at <= -2', 'move_on_pc if status <= -2 and the PC in its region', 'expand', 'goal', 'goal'],
            'cautious': ['recover if hold weak', 'scheme if a rival at <= -1', 'court', 'goal', 'goal', 'goal'],
            'mercantile': ['expand', 'scheme if a rival at <= -1', 'court', 'goal', 'goal', 'goal'],
            'zealous': ['strike if a rival at <= -2', 'court', 'move_on_pc if status <= -2', 'goal', 'goal', 'goal'],
            'secretive': ['scheme if a rival at <= -1', 'scheme if a rival at <= -1', 'move_on_pc if status <= -1 and its attention clock at half or more', 'lie_low if its attention clock on the PC is imminent', 'goal', 'goal'],
            'steadfast': ['recover if hold weak', 'aid_pc if status >= +2', 'strike if a rival at -3', 'goal', 'goal', 'goal'],
        },
        'failed_condition_reads_as': 'goal',
        'targets': {
            'strike_scheme': ['lowest relation', 'fullest goal clock', 'highest tier', 'lowest id'],
            'court': ['an ally of the PC with a tie to its org_tags at Warm or lower, if courtable and status <= 0 (never a kn.loyal ally at Neutral or warmer)',
                      'the non-rival faction with the highest relation below +2', 'else goal'],
        },
        'basis': ['11.3.7', 'R6 B-01', 'R4 W3', 'DL-11-04'],
    },
    'check': {
        'formula': 'd20 + rating + 2 x tier + stage modifier (+2 scheme lever, at most one); modifier clamped -8..+16',
        'rating': 'the one the action names (actions[].check); for goal, the goal record\'s goal.rating (11.3.5) [revision: I-061]',
        'stage_modifier': {'rising': 1, 'flourishing': 0, 'entrenched': {'goal_expand': -1, 'other': 0, 'defense': 1}, 'declining': -1},   # [revision: I-068] 'other' made explicit
        'dc': {'goal': '10 + 2 x tier + scope term', 'scope_term': {'local': 3, 'regional': 5, 'realm': 7},
               'against_faction': '10 + defender rating + 2 x defender tier (+1 entrenched, +2 at its seat)',
               'expand': '10 + 2 x tier + 5', 'recover_court': '10 + 2 x tier + 3'},
        'degrees': '00.3.10',
        'basis': ['11.3.5', 'DL-11-03'],
    },
    'actions': [
        {'id': 'goal', 'check': 'goal rating vs goal DC', 'critical_success': 'goal clock +2', 'success': 'goal clock +1', 'failure': 'no tick', 'critical_failure': 'slip: no tick; a true trace; next action recover'},
        {'id': 'strike', 'check': "force vs the defender's higher of force and cunning", 'critical_success': 'defender loses hold; d6 1-3 one hold place passes to the striker, 4-6 one non-linchpin officer killed or taken', 'success': 'defender loses hold', 'failure': 'a trace', 'critical_failure': 'striker loses hold'},
        {'id': 'scheme', 'check': "cunning vs the defender's cunning", 'critical_success': 'as success, and one sealed fact of the defender unsealed to the schemer and seeded as a true rumor', 'success': 'fact fac.<a>.inside.<b>: a +2 lever on its next check against that rival or a goal naming it', 'failure': 'nothing', 'critical_failure': "discovered: the defender's relation toward it -1; a trace"},
        {'id': 'expand', 'check': 'wealth vs 10 + 2 x tier + 5', 'critical_success': 'gain hold and a new hold place in its region', 'success': 'gain hold', 'failure': 'nothing', 'critical_failure': 'wealth -1 until its next completed goal'},
        {'id': 'recover', 'check': 'higher of wealth and sway vs 10 + 2 x tier + 3', 'critical_success': 'hold strong; slip cleared; goal clock +1', 'success': 'hold strong; slip cleared', 'failure': 'nothing', 'critical_failure': 'nothing; the slip stays'},
        {'id': 'court', 'check': 'sway vs 10 + 2 x tier + 3 (or a faction: its sway)', 'critical_success': 'as success, two targets', 'success': 'an ally of the PC is courted (courted_by, sealed, omen); or a faction relation +1', 'failure': 'nothing', 'critical_failure': 'the target learns: relation -1 or the ally\'s standing toward the faction -1'},
        {'id': 'move_on_pc', 'check': 'none', 'success': 'queue an entanglement (tbl.11.entanglement) at its pursuit column'},
        {'id': 'aid_pc', 'check': 'none', 'success': 'first eligible: pay a due ransom; send help to a threatened holding; gift_due if a reward is owed; an opportunity bang'},
        {'id': 'lie_low', 'check': 'none', 'success': 'its attention clock on the PC decays 1 extra; no trace'},
    ],
    'goal_clocks': {'local': {'segments': 8}, 'regional': {'segments': 12}, 'realm': {'segments': 12, 'linked_second': 12},
                    'visibility': 'hidden (sensed once the PC learns of the goal)',
                    'tick_sources': [{'on': 'faction_action_goal', 'ticks': 'per degree'}, {'on': 'random_event', 'ticks': 1}, {'on': 'rout', 'ticks': 'U(S3) (07.4.3; 3 from the Threshold)'}, {'on': 'pc_milestone', 'ticks': 2, 'condition': "the PC's domain only (11.9.8)"}],
                    'scopes_by_tier': {0: ['local'], 1: ['local'], 2: ['local', 'regional'], 3: ['local', 'regional'], 4: ['regional', 'realm'], 5: ['regional', 'realm']}},
    'stages': {
        'transitions': [
            {'from': 'rising', 'to': 'flourishing', 'when': 'a goal completed since entering, or 4 Season Turns rising'},
            {'from': 'flourishing', 'to': 'entrenched', 'when': 'tier >= 4, or 8 Season Turns flourishing'},
            {'from': ['flourishing', 'entrenched'], 'to': 'declining', 'when': 'lost hold twice in the last four seasons; or tier fell; or a linchpin fate names declining (at once)'},
            {'from': 'declining', 'to': 'rising', 'when': 'it completes a goal (at once)'},
            {'from': 'declining', 'to': 'collapsed', 'when': 'loses a weak hold at tier 0 (at once); or 4 Season Turns declining at tier 0'},
            {'from': 'any', 'to': 'collapsed', 'when': 'a linchpin fate names collapse (at once)'},
        ],
        'weight_of_size': {'applies': 'tier >= 3, at each Season Turn', 'check': 'd20 + highest rating + stage modifier (entrenched 0: its -1 is on goal and expand only) vs 10 + 2 x tier', 'failure': 'lose hold'},  # [revision: I-068]
        'basis': ['11.3.9', 'R6 B-05', 'DL-11-06'],
    },
    'rank_ladders': [
        {'id': f'rl.{k}', 'names': names} for k, names in [
            ('noble', ['retainer', 'household knight', 'castellan', 'seneschal', 'lord of the house']),
            ('civic', ['deputy', 'sworn watchman', 'watch-sergeant', 'watch-captain', 'reeve']),
            ('military', ['levy', 'man-at-arms', 'serjeant', 'captain', 'marshal']),
            ('temple', ['lay brother or sister', 'acolyte', 'priest', 'canon', 'high priest']),
            ('shrine', ['pilgrim-friend', 'lamp-keeper', 'shrine-warden', 'elder keeper', 'first keeper']),
            ('knightly', ['squire', 'brother-knight', 'knight-sergeant', 'commander', 'grand master']),
            ('arcane', ['initiate', 'adept', 'magister', 'archmagister', 'prime']),
            ('druidic', ['seeker', 'grove-friend', 'warden of the grove', 'elder', 'archdruid']),
            ('hunters', ['tracker', 'hunter', 'huntmaster', 'lodge-warden', 'master of the lodge']),
            ('merchant', ['factor\'s clerk', 'journeyman trader', 'factor', 'warden of the guild', 'guildmaster']),
            ('craft', ['apprentice', 'journeyman', 'master', 'warden', 'guildmaster']),
            ('scholarly', ['reader', 'scholar', 'lecturer', 'keeper of books', 'chancellor']),
            ('mercenary', ['recruit', 'blade', 'sergeant', 'lieutenant', 'captain-general']),
            ('trading', ['outrider', 'caravaneer', 'wagon-master', 'route-master', 'master of the house']),
            ('household', ['friend of the house', 'sworn of the house', 'steward', 'elder', 'head of the house']),
            ('thieves', ['cutpurse', 'made thief', 'crew boss', 'lieutenant', 'master of the guild']),
            ('bandits', ['hanger-on', 'sworn blade', 'band leader', 'chief\'s right hand', 'chief']),
            ('cult', ['listener', 'sworn', 'hierophant', 'high hierophant', 'voice of the master']),
        ]
    ],
    'rank_rungs': [
        {'rung': 1, 'seats': 'unlimited', 'requires': ['status >= +1 or an accepted V3 offer']},
        {'rung': 2, 'seats': 'unlimited', 'requires': ['status >= +1', 'a reputation entry of score >= 1 in its scope or seat on a key it honors', 'one season at rung 1 with every obligation kept']},
        {'rung': 3, 'seats': 'tier + 1', 'requires': ['status >= +2', 'such an entry of score >= 2', 'a seat free or won', 'a sitting']},
        {'rung': 4, 'seats': '1 + tier / 2 (round down)', 'requires': ['status >= +2', 'score >= 3', 'a seat free or won', 'a sitting']},
        {'rung': 5, 'seats': 1, 'requires': ['status +3', 'score >= 4', "the head's seat empty or won"]},
    ],
    'rank_gives': {'followers': {3: 2, 4: 4, 5: 6}, 'lifestyle_paid': {3: 'modest', 4: 'comfortable', 5: 'wealthy (noble for a tier-4+ crown faction)'},
                   'crown_rung2_lifestyle': 'comfortable', 'havens_from_rung': 2, 'mentors_from_rung': 1, 'training_fee_waived_from_rung': 2,
                   'request_rung_lower': 1, 'gift_on_promotion_to': [3, 4, 5], 'first_rank_status': 1},
    'tbl.11.entanglement': {
        'die': 'd6 + (status -2: +1; -3: +2), capped 8; column = pursuit (+1 if Hostile), 0-1 | 2 | 3+',
        'rows': [
            {'range': '1-2', 'pursuit_0_1': {'name': 'Questions', 'tag': 'social', 'intensity_delta': 1, 'content': 'an officer comes to ask what the PC was doing', 'ways_out': ['answer', 'lie', 'refuse and walk away', 'pay to be left alone']},
             'pursuit_2': {'name': 'Watchers', 'tag': 'social', 'intensity_delta': 1, 'content': 'two of its rank and file shadow the PC; a sensed clock (watchers, 4)', 'ways_out': ['lose them', 'confront them', 'feed them false trails']},
             'pursuit_3': {'name': 'Warrant', 'tag': 'threat', 'intensity_delta': 3, 'content': 'its writ or its price is posted in its scope; its holds closed to the PC', 'ways_out': ['buy it off', 'clear the PC\'s name (a thread)', 'leave its scope']}},
            {'range': '3-4', 'pursuit_0_1': {'name': 'Shakedown', 'tag': 'social', 'intensity_delta': 1, 'content': 'it demands a fee or a favor to forget it', 'ways_out': ['pay', 'do the favor', 'refuse (attention +2)']},
             'pursuit_2': {'name': 'Reprisal', 'tag': 'threat', 'intensity_delta': 3, 'content': 'it strikes something the PC values: a bond, a holding, an ally\'s livelihood', 'ways_out': ['stop it in time', 'make it whole', 'strike back']},
             'pursuit_3': {'name': 'Show of force', 'tag': 'threat', 'intensity_delta': 3, 'content': 'a band of its rank and file at the PC\'s lodging', 'ways_out': ['fight', 'flee', 'parley', 'call on a friendly faction']}},
            {'range': '5-6', 'pursuit_0_1': {'name': 'Snare', 'tag': 'threat', 'intensity_delta': 3, 'content': 'a false plea for help that leads to a place it holds', 'ways_out': ['see through the plea', 'go in prepared', 'send someone else', 'ignore it']},
             'pursuit_2': {'name': 'Ambush', 'tag': 'threat', 'intensity_delta': 3, 'content': 'its fielded rank and file at the next route the PC takes', 'ways_out': ['notice the omen and turn back', 'fight', 'take another road']},
             'pursuit_3': {'name': 'Champion', 'tag': 'threat', 'intensity_delta': 3, 'content': 'its champion is sent with orders', 'ways_out': ['face it', 'outrun it', 'turn it (Talk)', 'set a trap']}},
            {'range': '7-8', 'pursuit_0_1': {'name': 'Ultimatum', 'tag': 'social', 'intensity_delta': 1, 'content': 'leave its region within a season or face it', 'ways_out': ['leave', 'make peace', 'call its bluff']},
             'pursuit_2': {'name': 'Bounty', 'tag': 'threat', 'intensity_delta': 3, 'content': 'a bounty clock (hunters, 6, public)', 'ways_out': ['buy it off', 'kill or turn the hunters', 'make the faction withdraw it']},
             'pursuit_3': {'name': 'Abduction', 'tag': 'threat', 'intensity_delta': 3, 'content': 'it takes a bond or ally to force a meeting', 'ways_out': ['rescue', 'meet', 'trade']}},
        ],
        'specificity': 'faction', 'expires': '4 weeks', 'if_unmet': 'the row happens off-screen to what it names (never to the PC\'s person, carried possessions or licenses)',
        'basis': ['11.3.12', 'R6 B-02 (Blades entanglements)', 'R5 P-18'],
    },
    'attention': {'clock': {'kind': 'danger', 'segments': 8, 'visibility': 'hidden', 'then': 'reset'},
                  'created_when': 'status <= -1, or a loud deed against the faction',
                  'tick_sources': ['venture loudness 0-3 at venture_end (+1 its seat touched, +1 its members died, +1 Hostile)', 'cost.exposure S3+ against its members or in its holds: U(severity)', 'a noteworthy public_deed it despises in its scope: 1', 'random_event: 1'],
                  'decay': ['-1 per week with no tick', 'dt.lie_low: -2 in the region', 'lie_low action: -1'],
                  'on_complete': 'pursuit +1 (max 3); queue an entanglement; reset',
                  'pursuit_decay': '-1 at a Season Turn with no completion that season; 0 when status >= 0',
                  'paused_while': 'the rumor pc.dead circulates in its seat (11.6.8)'},
    'tbl.11.vacuum': {'die': 'd6', 'results': [
        {'range': '1-2', 'result': 'its strongest rival takes its seat (a gain of hold)'},
        {'range': '3-4', 'result': 'a new faction rises from its remnants: the template of its org_tags, tier 1, rising, a former officer its head'},
        {'range': '5', 'result': 'the region is lawless for a season: a situation from sit_t.road_of_knives'},
        {'range': '6', 'result': 'nobody yet: a seeded hook says so (the PC could fill it: establish, T-11-17)'}]},
    'tbl.11.faction_tier': {'die': 'd6', 'results': [{'range': '1-2', 'tier': 0}, {'range': '3-4', 'tier': 1}, {'range': '5', 'tier': 2}, {'range': '6', 'tier': 3}]},
    'tbl.11.faction_seed': {'die': 'd12', 'context': 'the region\'s largest settlement tier and its terrain', 'results': [
        {'range': '1', 'org': 'org.outlaw.bandits'}, {'range': '2', 'org': 'org.faith.shrine'}, {'range': '3', 'org': 'org.crown.civic'},
        {'range': '4', 'org': 'org.guild.merchant'}, {'range': '5', 'org': 'org.order.hunters'}, {'range': '6', 'org': 'org.clan.family'},
        {'range': '7', 'org': 'org.cult'}, {'range': '8', 'org': 'org.company.trading'}, {'range': '9', 'org': 'org.crown.noble'},
        {'range': '10', 'org': 'org.order.druidic (wild terrain) or org.guild.craft (settled)'}, {'range': '11', 'org': 'org.outlaw.thieves (town or city) or org.outlaw.bandits'},
        {'range': '12', 'org': 'org.order.arcane or org.order.knightly (d6: 1-3 / 4-6)'}]},
    # [revision: I-070] a petty faction's goal is drawn here, not from its template's goal list (PR-11-8 step 5): a d6 on
    # the kinds, scope local, the 6-segment clock, its text from the kind's pattern and its target by the kind's rule.
    'petty_goals': {'clock': {'segments': 6, 'visibility': 'hidden'}, 'die': 'd6 per World Turn: 1-3 nothing, 4-5 +1, 6 +2; +1 rising, -1 declining',
                    'draw': 'd6 on kinds by range (PR-11-8 step 5, a faction created petty); scope local; rating: its highest (ties force, cunning, wealth, sway)',
                    'kinds': [{'range': '1-2', 'kind': 'grow', 'text': 'win more of {seat} to it, and a hold of its own', 'target': None,
                               'writes': 'hold; then tier; at tier 2 it becomes full'},
                              {'range': '3', 'kind': 'take', 'text': 'take {place} for its own',
                               'target': 'the nearest place of its seat\'s region that no faction holds (ring, then id)', 'writes': 'a place passes to it'},
                              {'range': '4', 'kind': 'stir', 'text': 'stir up trouble at {seat}\'s next festival', 'target': None,
                               'writes': 'a situation of template sit_t.festival_trouble at its seat, itself the troublemaker'},
                              {'range': '5-6', 'kind': 'feud', 'text': 'settle its quarrel with {neighbor}',
                               'target': 'the faction with the lowest relation toward it (then the highest tier, then the lowest id)',
                               'writes': 'relation -2 with the target'}],
                    'becomes_full': 'it keeps its petty goal until the goal completes (worked by goal actions at the local DC), then draws from its template (11.3.2)',
                    'on_complete': 'its goal writes and one seeded hook'},
    'templates': templates,
    'factions': [],
    'blocks': [{'owner': '13', 'entries': []}],
}

# generic factions (instantiated by 13 or by generation; role slots bound at instantiation)
def F(id_, name, tpl, tier, temper=None, stage='flourishing', goal_i=0, extra_tags=None):
    t = next(x for x in templates if x['id'] == tpl)
    r = t['ratings_by_tier'][tier]
    g = t['goal_list'][goal_i]
    scope = 'local' if tier <= 1 else 'regional'
    return {
        'id': id_, 'name': name, 'tags': t['org_tags'] + (extra_tags or []), 'generic': True, 'template': tpl,
        'org_tags': t['org_tags'], 'tier': tier, 'hold': 'strong',
        'ratings': dict(zip(R, r)), 'temperament': temper or t['temperament'],
        'goal': {'text': g['text'], 'kind': g['kind'], 'scope': scope, 'rating': g['rating'],
                 'clock': {'kind': 'faction_goal', 'segments': 8 if scope == 'local' else 12, 'visibility': 'hidden',
                           'tick_sources': [{'on': 'faction_action_goal', 'ticks': 'per degree'}, {'on': 'random_event', 'ticks': 1}, {'on': 'rout', 'ticks': 'U(S3)'}],
                           'omens': t['goal_omens']}},
        'lifecycle_stage': stage,
        'linchpins': [{'npc': 'role:head', 'consequence': FATES['dies'], 'fates': {k: fate_effects(k) for k in ['dies', 'captured', 'turned', 'exposed']}}],
        'status_to_pc': 0, 'values': t['values'], 'patron_deeds': t['patron_deeds'], 'ranks': t['rank_ladder'],
        'duties': t['duties'], 'fields': t['fields'], 'boon_base': t['boon_base'], 'boon_signature': t['boon_signature'],
        'courtable': t['courtable'], 'sittings': ['quarter days'], 'seat': 'bound at instantiation', 'holds': [],
        'relations': {}, 'lifecycle': 'provisional', 'basis': ['11.3.18', 'DL-11-06'],
    }

doc['factions'] = [
    F('fac.generic.road_wolves', 'The Road Wolves (a bandit company)', 'ftpl.outlaw_bandits', 1),
    F('fac.generic.wayside_keepers', 'The Wayside Keepers (a shrine)', 'ftpl.faith_shrine', 0),
    F('fac.generic.caravan_house', 'A caravan house', 'ftpl.company_trading', 2),
    F('fac.generic.hunters_lodge', "A hunters' lodge", 'ftpl.order_hunters', 1, stage='rising', goal_i=4),
    F('fac.generic.town_council', 'A town council and its watch', 'ftpl.crown_civic', 2),
    F('fac.generic.hill_cult', 'A cult in the hills', 'ftpl.cult', 1, stage='rising'),
    F('fac.generic.free_blades', 'A free company', 'ftpl.company_mercenary', 1),
    F('fac.generic.country_house', 'A country house', 'ftpl.crown_noble', 2),
]
for f in doc['factions']:
    assert sum(f['ratings'].values()) == 4 + 2 * f['tier'] and all(v <= f['tier'] + 2 for v in f['ratings'].values())

header = """# data/factions.yaml
# Purpose: faction templates, generic factions, and the faction engine's tables: the agenda by temperament,
#   the faction check and actions, goal clocks, stages and the weight of size, rank ladders and rungs, the
#   entanglement table, attention, vacuums, seeding and petty factions (11.3, 11.8; T-11-2, T-11-4).
# Owner: 11-living-world (T-00-19); owner-block "13" for the starter region's factions.
# Schema: data/SCHEMAS.md#factions.yaml (required: id, name, tags, org_tags, tier, hold, ratings, goal {text,
#   clock}, lifecycle_stage, linchpins [{npc, consequence}], status_to_pc, lifecycle, basis) plus T-11-1's optional
#   keys. Ratings are force, cunning, wealth, sway; each 0..tier+2; sum 4 + 2 x tier (11.3.4).
# GENERATED by rules/_process/simulation/11-gen_factions.py (asserts the rating envelope). Edit the script.
# Generic factions (`generic: true`) carry role slots (role:head) bound when a region's seed (12.16.10, PR-11-8) instantiates them.
# Every entry lifecycle: provisional (00.16.3).
# Basis: [R6 B-01, B-02, B-05, B-08, B-R2] [R5 P-22, P-23, P-25] [DL-11-03..06, DL-11-13, DL-11-18]
"""
yaml.SafeDumper.ignore_aliases = lambda *a: True
out = header + '\n' + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=120)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'factions.yaml')
open(path, 'w', encoding='utf-8').write(out)
print('wrote', path, len(out.split()), 'words')
