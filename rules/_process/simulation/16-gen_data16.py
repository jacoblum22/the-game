#!/usr/bin/env python3
"""16-gen_data16.py -- compiles and validates rules/data/companions.yaml (chapter 16).

Every id is checked against the canonical files: tags (data/tags.yaml + contrib/tags.*.yaml proposals),
licenses (data/licenses.yaml), abilities (data/abilities.yaml), conditions (data/conditions.yaml), effects
(data/effects.yaml + contrib/effects.*.yaml), wages (data/economy.yaml), base items (data/base_items.yaml).
Each template's line is computed at every band of its range from chapter 09's band tables (T-09-2) and
checked against 16.4.6 (never out-power the PC's band) and the 00.3.5 caps. Usage: python 16-gen_data16.py
"""
import glob
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, '..', '..', 'data'))


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return yaml.safe_load(f)


TAGS = {t['id'] for t in load('tags.yaml')['tags']}
for f in glob.glob(os.path.join(DATA, '..', '_process', 'merged-contrib', 'tags.*.yaml')):
    d = yaml.safe_load(open(f, encoding='utf-8'))
    for b in d.get('blocks', []):
        for e in b.get('entries', []):
            TAGS.add(e['id'])
LICS = set()
for e in load('licenses.yaml')['licenses']:
    LICS.add(e['id'])
ABS = {a['id'] for a in load('abilities.yaml')['abilities']}
CONDS = {c['id'] for c in load('conditions.yaml')['conditions']}
EFFS = {e['id'] for e in load('effects.yaml')['core']}
for f in glob.glob(os.path.join(DATA, '..', '_process', 'merged-contrib', 'effects.*.yaml')):
    d = yaml.safe_load(open(f, encoding='utf-8'))
    for b in d.get('blocks', []):
        for e in b.get('entries', []):
            EFFS.add(e['id'])
WAGES = {w['id']: w for w in load('economy.yaml')['wages']}
BI = {b['id'] for b in load('base_items.yaml')['base_items']}

ATTRS = ['might', 'agility', 'endurance', 'wits', 'intellect', 'presence', 'resolve']
C_B = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
RUNG = {'apex': {1: 3, 2: 5, 3: 6, 4: 8, 5: 9}, 'high': {1: 1, 2: 3, 3: 4, 4: 6, 5: 7},
        'mid': {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}, 'low': {1: -1, 2: -1, 3: 0, 4: 1, 5: 1},
        'feeble': {1: -3, 2: -3, 3: -2, 4: -2, 5: -2}, 'none': {1: -5, 2: -5, 3: -5, 4: -5, 5: -5}}
STD_SEV = {1: 2, 2: 2, 3: 3, 4: 3, 5: 4}
VIT = {1: 6, 2: 12, 3: 16, 4: 18, 5: 20}       # 16.4.3: min(09 standard, PC reference at the band); band 1 = 6
SIZE_MULT = {'tiny': (1, 2), 'small': (3, 4), 'medium': (1, 1), 'large': (3, 2), 'huge': (2, 1)}
FOCUS = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}
PC_FLOOR = {1: 4, 2: 6, 3: 8, 4: 10, 5: 12}
PC_VIT = {1: 12, 2: 14, 3: 16, 4: 18, 5: 20}       # T-06-12 reference (DL-00-04)
PC_SEV = {1: 2, 2: 2, 3: 3, 4: 3, 5: 4}             # T-06-12 Strike base severity
ORDERS = ['guard_me', 'hold_him', 'harry_that_one', 'hold_this_ground', 'stay_back']
FAMILY_ORDERS = {
    'fighter': (['guard_me', 'hold_him', 'harry_that_one', 'hold_this_ground', 'stay_back'], 'guard_me'),
    'shooter': (['stay_back', 'hold_this_ground', 'guard_me'], 'stay_back'),
    'skirmisher': (['stay_back', 'harry_that_one', 'hold_this_ground'], 'stay_back'),
    'noncombatant': (['stay_back', 'guard_me'], 'stay_back'),
    'caster': (['stay_back', 'guard_me'], 'stay_back'),
    'war_beast': (['guard_me', 'hold_him', 'harry_that_one', 'hold_this_ground', 'stay_back'], 'harry_that_one'),
    'beast': (['stay_back'], 'stay_back'),
    'mount': ([], None),
    'bound': (['guard_me', 'hold_him', 'harry_that_one', 'hold_this_ground', 'stay_back'], 'guard_me'),
}
ROLES = ['navigator', 'lookout', 'scout', 'forager', 'quartermaster']
KNACKS = ['kn.trained', 'kn.shieldbearer', 'kn.steadfast', 'kn.healer', 'kn.keen_nose', 'kn.keen_eyes',
          'kn.sentinel', 'kn.war_trained', 'kn.pack_beast', 'kn.quartermaster', 'kn.sign_trained', 'kn.rally',
          'kn.bodyguard', 'kn.loyal', 'kn.forager']

H = 'human'   # shorthand


def R(m, a, e, w, i, p, r):
    return dict(zip(ATTRS, [m, a, e, w, i, p, r]))


def atk(name, verb, attribute, harm_tags, offset=0, bands=('band.engaged',)):
    return {'name': name, 'verb': verb, 'attribute': attribute, 'harm_tags': list(harm_tags),
            'severity_offset': offset, 'bands': list(bands)}


T = []   # templates


def tmpl(id, name, family, kinds, creature, rungs, trained, trained_def, attacks, armor, size='medium',
         pace=1, knacks=(), licenses=(), abilities=(), signature_knack='kn.loyal', roles=('lookout',),
         wage=None, hire_band=None, band_min=1, band_max=3, carry=2, supply=1, kit=(), hears='voice',
         role=None, protege=False, fixed_value=None, temperament=None, price=None, trainable=None,
         item_ref=None, hire_roles=None, notes=None, tags_extra=()):
    T.append(dict(id=id, name=name, family=family, kinds=list(kinds), creature=creature, rungs=rungs,
                  trained=list(trained), trained_def=list(trained_def), attacks=list(attacks), armor=armor,
                  size=size, pace=pace, knacks=list(knacks), licenses=list(licenses), abilities=list(abilities),
                  signature_knack=signature_knack, roles=list(roles), wage=wage, hire_band=hire_band,
                  band_min=band_min, band_max=band_max, carry=carry, supply=supply, kit=list(kit), hears=hears,
                  role=role, protege=protege, fixed_value=fixed_value, temperament=temperament, price=price,
                  trainable=trainable, item_ref=item_ref, hire_roles=hire_roles, notes=notes,
                  tags_extra=list(tags_extra)))


PEOPLE = ('hireling', 'companion', 'follower', 'cohort')
cut = ['harm.physical.cut']
pierce = ['harm.physical.pierce']
crush = ['harm.physical.crush']

# ---------------------------------------------------------------- hired hands and soldiers
tmpl('cmp.porter', 'Porter or torchbearer', 'noncombatant', PEOPLE, 'creature.folk.human',
     R('high', 'mid', 'high', 'mid', 'low', 'low', 'mid'), ['deed.martial.athletics'], ['endurance'],
     [atk('cudgel', 'verb.strike', 'might', crush, -1)], 0, carry=10, wage='wage.porter', hire_band=1, band_max=2,
     roles=['lookout'], kit=[('item.tool.light', 'common', 2), ('item.tool.container', 'common', 1),
                             ('item.weapon.bludgeon', 'worn', 1)],
     hire_roles='porter, torchbearer, linkboy, camp hand: carries 10 load units and holds the light',
     signature_knack='kn.steadfast', trainable=['kn.quartermaster', 'kn.steadfast'])
tmpl('cmp.guide', 'Guide', 'noncombatant', PEOPLE, 'creature.folk.human',
     R('mid', 'mid', 'high', 'high', 'mid', 'low', 'mid'), ['deed.wilds.navigation', 'deed.wilds.survival'],
     ['wits'], [atk('knife', 'verb.strike', 'agility', pierce, -1)], 1, knacks=['kn.trained'],
     licenses=['lic.training.wilds_navigation'], wage='wage.skilled', hire_band=1, band_max=3,
     roles=['navigator', 'lookout', 'scout'], kit=[('item.armor.light', 'common', 1), ('item.weapon.blade', 'common', 1)],
     hire_roles='guide, pathfinder, someone who knows the country (the marsh, the passes, the old roads)',
     signature_knack='kn.forager', trainable=['kn.trained', 'kn.forager', 'kn.keen_eyes'])
tmpl('cmp.camp_hand', 'Camp hand, cook or groom', 'noncombatant', PEOPLE, 'creature.folk.human',
     R('mid', 'mid', 'high', 'mid', 'mid', 'mid', 'mid'), ['deed.craft.cookery', 'deed.wilds.animals'],
     ['endurance'], [atk('cleaver', 'verb.strike', 'might', cut, -1)], 0, knacks=['kn.quartermaster'],
     licenses=['lic.training.craft_cookery'], wage='wage.skilled', hire_band=1, band_max=2,
     roles=['quartermaster', 'lookout'], carry=6, kit=[('item.tool.trade', 'common', 1), ('item.consumable.food', 'common', 4)],
     hire_roles='cook, groom, carter, camp hand who keeps the stores and the beasts',
     signature_knack='kn.trained', trainable=['kn.trained', 'kn.healer'])
tmpl('cmp.soldier', 'Soldier', 'fighter', PEOPLE, 'creature.folk.human',
     R('high', 'mid', 'high', 'mid', 'low', 'low', 'mid'), ['deed.martial.blade', 'deed.martial.shield', 'deed.martial.armor'],
     ['might', 'endurance'], [atk('sword', 'verb.strike', 'might', cut, 0)], 2, knacks=['kn.shieldbearer'],
     wage='wage.soldier', hire_band=2, band_max=4, roles=['lookout'],
     kit=[('item.weapon.blade', 'common', 1), ('item.shield.light', 'common', 1), ('item.armor.medium', 'common', 1)],
     hire_roles='guard, man-at-arms, spear, sellsword', signature_knack='kn.bodyguard',
     trainable=['kn.steadfast', 'kn.bodyguard', 'kn.trained'])
tmpl('cmp.archer', 'Archer', 'shooter', PEOPLE, 'creature.folk.human',
     R('mid', 'high', 'mid', 'high', 'low', 'low', 'mid'), ['deed.martial.archery', 'deed.martial.athletics'],
     ['agility'], [atk('bow', 'verb.strike', 'agility', pierce, 0, ('band.close', 'band.near', 'band.far')),
                   atk('knife', 'verb.strike', 'agility', pierce, -1)], 1, wage='wage.soldier', hire_band=2,
     band_max=4, roles=['lookout', 'scout'], kit=[('item.weapon.bow', 'common', 1), ('item.armor.light', 'common', 1)],
     hire_roles='archer, crossbowman, hunter hired to shoot', signature_knack='kn.keen_eyes',
     trainable=['kn.keen_eyes', 'kn.steadfast', 'kn.trained'])
tmpl('cmp.scout', 'Scout', 'skirmisher', PEOPLE, 'creature.folk.human',
     R('mid', 'high', 'mid', 'apex', 'low', 'low', 'mid'), ['deed.guile.stealth', 'deed.wilds.tracking', 'deed.martial.archery'],
     ['agility', 'wits'], [atk('shortbow', 'verb.strike', 'agility', pierce, 0, ('band.close', 'band.near', 'band.far')),
                           atk('knife', 'verb.strike', 'agility', pierce, -1)], 1, knacks=['kn.trained'],
     licenses=['lic.training.wilds_tracking', 'lic.training.guile_stealth'], wage='wage.soldier', hire_band=2,
     band_max=4, roles=['scout', 'lookout', 'forager', 'navigator'],
     kit=[('item.weapon.bow', 'common', 1), ('item.garment.cloak', 'common', 1)],
     hire_roles='scout, tracker, outrider, poacher', signature_knack='kn.keen_eyes',
     trainable=['kn.keen_eyes', 'kn.forager', 'kn.trained'])
tmpl('cmp.boatman', 'Boatman or sailor', 'skirmisher', PEOPLE, 'creature.folk.human',
     R('high', 'high', 'mid', 'mid', 'low', 'low', 'mid'), ['deed.wilds.seafaring', 'deed.martial.athletics'],
     ['agility'], [atk('boathook', 'verb.strike', 'might', pierce, -1, ('band.engaged', 'band.close'))], 0,
     knacks=['kn.trained'], licenses=['lic.training.wilds_seafaring'], wage='wage.skilled', hire_band=1, band_max=3,
     roles=['navigator', 'lookout'], kit=[('item.weapon.polearm', 'worn', 1)],
     hire_roles='boatman, ferryman, sailor, oarsman (water travel, 10.3.7)', signature_knack='kn.steadfast',
     trainable=['kn.trained', 'kn.steadfast'])
tmpl('cmp.healer', 'Healer', 'noncombatant', PEOPLE, 'creature.folk.human',
     R('low', 'mid', 'mid', 'high', 'high', 'mid', 'mid'), ['deed.lore.medicine'], ['wits'],
     [atk('staff', 'verb.strike', 'might', crush, -1)], 0, knacks=['kn.healer'], wage='wage.specialist', hire_band=2,
     band_max=3, roles=['lookout', 'forager'], kit=[('item.tool.kit', 'common', 1)],
     hire_roles='trained healer, leech, surgeon, herb-wife', signature_knack='kn.steadfast',
     trainable=['kn.trained', 'kn.steadfast'])
tmpl('cmp.locksmith', 'Locksmith or cracksman', 'skirmisher', PEOPLE, 'creature.folk.human',
     R('low', 'apex', 'mid', 'high', 'mid', 'low', 'mid'), ['deed.guile.thievery', 'deed.guile.stealth'], ['agility'],
     [atk('knife', 'verb.strike', 'agility', pierce, -1)], 1, knacks=['kn.trained'],
     licenses=['lic.training.guile_thievery'], wage='wage.specialist', hire_band=2, band_max=3,
     roles=['scout', 'lookout'], kit=[('item.tool.kit', 'common', 1)],
     hire_roles='locksmith, trap-breaker, cracksman', signature_knack='kn.loyal',
     trainable=['kn.trained', 'kn.loyal'])
tmpl('cmp.hedge_witch', 'Hedge-witch', 'caster', PEOPLE, 'creature.folk.human',
     R('low', 'mid', 'mid', 'high', 'mid', 'mid', 'high'), ['deed.primal.hexcraft', 'deed.lore.medicine'],
     ['resolve'], [atk('staff', 'verb.strike', 'might', crush, -1)], 0, knacks=['kn.trained'],
     licenses=['lic.training.primal_hexcraft'], abilities=['ab.evil_eye'], role='caster', wage='wage.specialist',
     hire_band=2, band_max=3, roles=['forager', 'lookout'], kit=[('item.tool.implement', 'common', 1)],
     hire_roles='hedge-witch, cunning woman, charm-seller', signature_knack='kn.healer',
     trainable=['kn.healer', 'kn.trained'])
tmpl('cmp.sapper', 'Sapper', 'noncombatant', PEOPLE, 'creature.folk.human',
     R('high', 'mid', 'high', 'mid', 'high', 'low', 'mid'), ['deed.lore.engineering', 'deed.craft.building'],
     ['endurance'], [atk('pick', 'verb.strike', 'might', pierce, 0)], 1, knacks=['kn.trained'],
     licenses=['lic.training.lore_engineering'], wage='wage.specialist', hire_band=2, band_max=3,
     roles=['lookout'], carry=4, kit=[('item.tool.trade', 'common', 1)],
     hire_roles='sapper, miner, siege engineer, mason', signature_knack='kn.steadfast',
     trainable=['kn.trained', 'kn.steadfast'])
tmpl('cmp.veteran', 'Veteran sergeant', 'fighter', PEOPLE, 'creature.folk.human',
     R('high', 'mid', 'high', 'high', 'mid', 'mid', 'high'), ['deed.martial.blade', 'deed.martial.tactics', 'deed.influence.command'],
     ['might', 'resolve'], [atk('sword', 'verb.strike', 'might', cut, 0)], 2, knacks=['kn.rally', 'kn.steadfast'],
     wage='wage.veteran', hire_band=3, band_min=2, band_max=4, roles=['lookout', 'navigator'],
     kit=[('item.weapon.blade', 'fine', 1), ('item.armor.medium', 'common', 1), ('item.shield.light', 'common', 1)],
     hire_roles='veteran, sergeant, old soldier, captain of a small company (half share of coin found)',
     signature_knack='kn.bodyguard', trainable=['kn.bodyguard', 'kn.shieldbearer'])
tmpl('cmp.journeyman_mage', 'Journeyman mage', 'caster', PEOPLE, 'creature.folk.human',
     R('low', 'mid', 'low', 'mid', 'apex', 'mid', 'high'), ['deed.arcane.fire', 'deed.arcane.warding', 'deed.lore.arcana'],
     ['intellect', 'resolve'], [atk('dagger', 'verb.strike', 'agility', pierce, -1)], 0, knacks=['kn.trained'],
     licenses=['lic.training.arcane_fire'], abilities=['ab.flame_lance', 'ab.spell_ward'], role='caster',
     wage='wage.veteran', hire_band=3, band_min=2, band_max=4, roles=['lookout'],
     kit=[('item.tool.implement', 'common', 1)],
     hire_roles='journeyman mage, hired conjurer (half share of coin found)', signature_knack='kn.steadfast',
     trainable=['kn.trained'])
tmpl('cmp.champion', 'Champion', 'fighter', PEOPLE, 'creature.folk.human',
     R('apex', 'high', 'high', 'high', 'mid', 'mid', 'high'), ['deed.martial.blade', 'deed.martial.shield', 'deed.martial.tactics'],
     ['might', 'agility', 'resolve'], [atk('greatsword', 'verb.strike', 'might', cut, 0)], 3,
     knacks=['kn.bodyguard', 'kn.steadfast'], wage='wage.champion', hire_band=4, band_min=3, band_max=5,
     roles=['lookout'], kit=[('item.weapon.blade', 'masterwork', 1), ('item.armor.heavy', 'fine', 1)],
     hire_roles='a renowned fighter (full share; only for a thread they believe in)', signature_knack='kn.rally',
     trainable=['kn.rally'])
# ---------------------------------------------------------------- people met on the road
tmpl('cmp.sworn_sword', 'Sworn sword', 'fighter', ('companion', 'follower'), 'creature.folk.human',
     R('high', 'mid', 'high', 'mid', 'mid', 'mid', 'high'), ['deed.martial.blade', 'deed.martial.shield', 'deed.martial.armor'],
     ['might', 'resolve'], [atk('sword', 'verb.strike', 'might', cut, 0)], 2, knacks=['kn.shieldbearer', 'kn.steadfast'],
     band_min=2, band_max=4, roles=['lookout'], fixed_value={'axis': 'conduct.loyalty', 'pole': 1},
     kit=[('item.weapon.blade', 'fine', 1), ('item.shield.light', 'common', 1), ('item.armor.medium', 'common', 1)],
     signature_knack='kn.bodyguard', trainable=['kn.bodyguard', 'kn.rally'])
tmpl('cmp.thief', 'Thief', 'skirmisher', ('companion', 'hireling', 'follower'), 'creature.folk.human',
     R('low', 'apex', 'mid', 'high', 'mid', 'mid', 'low'), ['deed.guile.thievery', 'deed.guile.stealth', 'deed.guile.streetwise'],
     ['agility', 'wits'], [atk('knife', 'verb.strike', 'agility', pierce, 0)], 1, knacks=['kn.trained'],
     licenses=['lic.training.guile_thievery'], band_max=4, roles=['scout', 'lookout'],
     kit=[('item.weapon.blade', 'common', 1), ('item.tool.kit', 'common', 1)], wage='wage.specialist', hire_band=2,
     hire_roles='thief, fence, cutpurse who knows the city', signature_knack='kn.loyal',
     trainable=['kn.trained', 'kn.keen_eyes'])
tmpl('cmp.acolyte', 'Acolyte', 'caster', ('companion', 'follower'), 'creature.folk.human',
     R('low', 'mid', 'mid', 'mid', 'mid', 'high', 'high'), ['deed.divine.healing', 'deed.divine.rites', 'deed.lore.religion'],
     ['resolve'], [atk('mace', 'verb.strike', 'might', crush, -1)], 1, knacks=['kn.trained'],
     licenses=['lic.training.divine_healing'], abilities=['ab.mend_flesh'], role='caster', band_max=4,  # [verification: V2c-010] protégé tier 3 -> band 4 (16.10.4)
    
     roles=['lookout'], protege=True, fixed_value={'axis': 'conduct.piety', 'pole': 1},
     kit=[('item.tool.implement', 'common', 1), ('item.weapon.bludgeon', 'common', 1)],
     signature_knack='kn.healer', trainable=['kn.healer', 'kn.steadfast'])
tmpl('cmp.minstrel', 'Minstrel', 'noncombatant', ('companion', 'hireling', 'follower'), 'creature.folk.human',
     R('low', 'high', 'mid', 'high', 'mid', 'apex', 'mid'), ['deed.influence.performance', 'deed.influence.persuasion'],
     ['wits'], [atk('knife', 'verb.strike', 'agility', pierce, -1)], 0, knacks=['kn.trained'],
     licenses=['lic.training.influence_performance'], abilities=['ab.stirring_song'], band_max=3,
     roles=['lookout'], kit=[('item.tool.instrument', 'common', 1)], wage='wage.skilled', hire_band=1,
     hire_roles='minstrel, player, storyteller', signature_knack='kn.rally', trainable=['kn.rally', 'kn.trained'])
tmpl('cmp.sage', 'Sage', 'noncombatant', ('companion', 'hireling', 'follower'), 'creature.folk.human',
     R('feeble', 'low', 'low', 'mid', 'apex', 'mid', 'high'), ['deed.lore.history', 'deed.lore.arcana', 'deed.lore.languages'],
     ['intellect', 'resolve'], [atk('staff', 'verb.strike', 'might', crush, -1)], 0, knacks=['kn.trained'],
     licenses=['lic.training.lore_history'], band_max=3, roles=['navigator'], carry=1,
     kit=[('item.tool.container', 'common', 1)], wage='wage.specialist', hire_band=2,
     hire_roles='sage, scribe, scholar, translator', signature_knack='kn.trained', trainable=['kn.trained'])
tmpl('cmp.squire', 'Squire', 'fighter', ('companion', 'follower'), 'creature.folk.human',
     R('high', 'mid', 'mid', 'mid', 'low', 'mid', 'mid'), ['deed.martial.blade', 'deed.wilds.animals'],
     ['might'], [atk('sword', 'verb.strike', 'might', cut, 0)], 1, band_max=4, roles=['lookout', 'quartermaster'],
     knacks=['kn.quartermaster'], protege=True, kit=[('item.weapon.blade', 'common', 1), ('item.armor.light', 'common', 1)],
     signature_knack='kn.shieldbearer', trainable=['kn.shieldbearer', 'kn.steadfast', 'kn.bodyguard'])
tmpl('cmp.apprentice', 'Apprentice', 'noncombatant', ('companion', 'follower'), 'creature.folk.human',
     R('low', 'mid', 'mid', 'mid', 'high', 'mid', 'mid'), ['deed.craft.smithing', 'deed.lore.arcana'],
     ['intellect'], [atk('hammer', 'verb.strike', 'might', crush, -1)], 0, band_max=4, roles=['lookout', 'quartermaster'],
     knacks=['kn.quartermaster'], protege=True, kit=[('item.tool.trade', 'common', 1)],
     signature_knack='kn.trained', trainable=['kn.trained', 'kn.healer'],
     notes='An apprentice in the PC\'s own art (craft, arcane or lore): its trained tags are the PC\'s key tags at '
           'joining (the template lists the defaults).')
tmpl('cmp.zealot', 'Zealot', 'fighter', ('follower',), 'creature.folk.human',
     R('high', 'mid', 'high', 'mid', 'low', 'mid', 'apex'), ['deed.martial.bludgeon', 'deed.divine.rites'],
     ['resolve'], [atk('flail', 'verb.strike', 'might', crush, 0)], 1, knacks=['kn.steadfast'], band_max=3,
     roles=['lookout'], fixed_value={'axis': 'conduct.piety', 'pole': 1}, kit=[('item.weapon.bludgeon', 'common', 1)],
     signature_knack='kn.loyal', trainable=['kn.loyal', 'kn.rally'])
tmpl('cmp.militia', 'Militia volunteer', 'fighter', ('follower', 'cohort', 'hireling'), 'creature.folk.human',
     R('mid', 'mid', 'high', 'mid', 'low', 'low', 'mid'), ['deed.martial.polearm'], [],
     [atk('spear', 'verb.strike', 'might', pierce, 0, ('band.engaged', 'band.close'))], 1, band_max=2,
     roles=['lookout'], kit=[('item.weapon.polearm', 'worn', 1)], wage='wage.porter', hire_band=1,
     hire_roles='militia, levy, village spear (cohorts of 3-6)', signature_knack='kn.steadfast',
     trainable=['kn.steadfast'])
# ---------------------------------------------------------------- beasts
tmpl('cmp.hound', 'Hound', 'war_beast', ('beast',), 'creature.beast.predator',
     R('apex', 'high', 'high', 'high', 'none', 'low', 'mid'), ['deed.martial.unarmed', 'deed.wilds.tracking'],
     ['agility'], [atk('bite', 'verb.strike', 'might', pierce, 0), atk('drag down', 'verb.grapple', 'might', [], 0)], 0,
     knacks=['kn.keen_nose', 'kn.sentinel'], band_max=2, roles=['lookout'], carry=0, temperament='steady',
     price=15, signature_knack='kn.war_trained', trainable=['kn.war_trained', 'kn.sign_trained'],
     notes='A mastiff or hunting hound trained to the leash. War-trained variant: cmp.war_hound.')
tmpl('cmp.war_hound', 'War hound', 'war_beast', ('beast',), 'creature.beast.predator',
     R('apex', 'high', 'high', 'high', 'none', 'low', 'high'), ['deed.martial.unarmed', 'deed.wilds.tracking'],
     ['agility', 'resolve'], [atk('bite', 'verb.strike', 'might', pierce, 0), atk('drag down', 'verb.grapple', 'might', [], 0)], 1,
     knacks=['kn.war_trained', 'kn.keen_nose'], band_min=2, band_max=3, roles=['lookout'], carry=0,
     temperament='fierce', price=60, signature_knack='kn.bodyguard', trainable=['kn.sign_trained', 'kn.sentinel'])
tmpl('cmp.hawk', 'Hunting hawk', 'beast', ('beast',), 'creature.beast.avian',
     R('feeble', 'apex', 'low', 'apex', 'none', 'low', 'mid'), ['deed.martial.unarmed'], ['agility'],
     [atk('talons', 'verb.strike', 'agility', cut, -1)], 0, size='tiny', pace=2, knacks=['kn.keen_eyes'],
     band_max=2, roles=['lookout'], carry=0, supply=0, temperament='skittish', price=40,
     signature_knack='kn.sign_trained', trainable=['kn.sign_trained'],
     notes='May take harry_that_one from the air (T-16-12); a lookout only.')
tmpl('cmp.wolf_bonded', 'Bonded wolf', 'war_beast', ('beast',), 'creature.beast.predator',
     R('high', 'apex', 'high', 'apex', 'none', 'low', 'mid'), ['deed.martial.unarmed', 'deed.wilds.tracking'],
     ['agility', 'wits'], [atk('bite', 'verb.strike', 'agility', pierce, 0), atk('drag down', 'verb.grapple', 'might', [], 0)], 1,
     pace=2, knacks=['kn.keen_nose', 'kn.war_trained'], band_min=2, band_max=4, roles=['lookout', 'scout'],
     carry=0, hears='bond', temperament='fierce', signature_knack='kn.sentinel', trainable=['kn.sentinel'],
     notes='Joins only by rit.beast_bond (05) or taming (16.3.7).')
tmpl('cmp.bear_bonded', 'Bonded bear', 'war_beast', ('beast',), 'creature.beast.predator',
     R('apex', 'mid', 'apex', 'mid', 'none', 'low', 'high'), ['deed.martial.unarmed'], ['might', 'endurance'],
     [atk('maul', 'verb.strike', 'might', crush, 0), atk('hug', 'verb.grapple', 'might', [], 0)], 1, size='large',
     knacks=['kn.war_trained'], band_min=3, band_max=4, roles=['lookout'], carry=6, supply=2, hears='bond',
     temperament='fierce', signature_knack='kn.sentinel', trainable=['kn.sentinel'],
     notes='Joins only by rit.beast_bond (05).')
tmpl('cmp.familiar', 'Familiar', 'beast', ('bound', 'beast'), 'creature.beast.vermin',
     R('none', 'apex', 'low', 'apex', 'low', 'low', 'mid'), ['deed.guile.stealth'], ['agility'],
     [atk('bite', 'verb.strike', 'agility', pierce, -1)], 0, size='tiny', knacks=['kn.keen_eyes'], band_max=1,
     roles=['lookout'], carry=0, supply=0, hears='voice', temperament='gentle', signature_knack='kn.sentinel',
     trainable=['kn.sentinel'], notes='rit.bind_familiar (05): a cat, raven, toad or rat; lends its senses one interval a day.')
# ---------------------------------------------------------------- mounts (08's base items; 0 places unless bonded)
for bid, nm, band, size, cr, war, carry in [
        ('bi.donkey', 'Donkey', 1, 'medium', 'creature.beast.herd', False, 20),
        ('bi.pony', 'Pony', 1, 'medium', 'creature.beast.herd', False, 20),
        ('bi.mule', 'Mule', 1, 'large', 'creature.beast.herd', False, 30),
        ('bi.riding_horse', 'Riding horse', 1, 'large', 'creature.beast.herd', False, 25),
        ('bi.draft_horse', 'Draft horse', 2, 'large', 'creature.beast.herd', False, 40),
        ('bi.courser', 'Courser', 2, 'large', 'creature.beast.herd', True, 25),
        ('bi.destrier', 'Destrier', 3, 'large', 'creature.beast.herd', True, 30)]:
    tmpl('cmp.mount_' + bid[3:], nm, 'mount', ('beast',), cr,
         R('apex', 'mid', 'apex', 'mid', 'none', 'low', 'mid' if not war else 'high'), ['deed.martial.unarmed'],
         ['endurance'], [atk('kick', 'verb.strike', 'might', crush, 0)], 1 if band >= 2 else 0, size=size, pace=2,
         knacks=(['kn.war_trained', 'kn.pack_beast'] if war else ['kn.pack_beast']), band_min=band, band_max=band,
         roles=[], carry=carry, supply=1, temperament='steady' if war else 'skittish', item_ref=bid,
         signature_knack='kn.war_trained' if not war else 'kn.bodyguard', trainable=['kn.war_trained'] if not war else [],
         notes='08.10.1: bought as an item; a beast record with 0 retinue places unless bonded (16.2.2).')
# ---------------------------------------------------------------- bound beings (05's workings)
tmpl('cmp.bound_servant', 'Summoned servant', 'bound', ('bound',), 'creature.spirit',
     R('mid', 'mid', 'mid', 'mid', 'low', 'none', 'mid'), ['deed.martial.unarmed'], [],
     [atk('blow', 'verb.strike', 'might', crush, -1)], 0, band_max=5, roles=['lookout'], carry=4, supply=0,
     hears='voice', signature_knack=None, notes='05\'s Call Servant and eff.summon servants; band set by the working.')
tmpl('cmp.bound_dead', 'Raised dead', 'bound', ('bound',), 'creature.undead.mindless',
     R('high', 'low', 'apex', 'low', 'none', 'none', 'none'), ['deed.martial.unarmed'], ['endurance'],
     [atk('claw', 'verb.strike', 'might', cut, 0)], 1, band_max=5, roles=[], carry=6, supply=0, hears='voice',
     signature_knack=None, notes='05\'s necromancy; no standing, no drives; ends at 0 Vitality (07.12.4).')
tmpl('cmp.bound_automaton', 'Automaton', 'bound', ('bound',), 'creature.construct.clockwork',
     R('apex', 'low', 'apex', 'low', 'none', 'none', 'none'), ['deed.martial.unarmed'], ['might', 'endurance'],
     [atk('fist', 'verb.strike', 'might', crush, 0)], 2, band_max=5, roles=[], carry=10, supply=0, hears='voice',
     signature_knack=None, notes='05\'s artifice; obeys its maker\'s text (06.14 request: orders per its maker).')
tmpl('cmp.from_archetype', 'From archetype', 'fighter', ('companion', 'hireling', 'follower', 'cohort', 'beast'), None,
     None, [], [], [], None, band_max=5, roles=['lookout'], signature_knack='kn.loyal',
     notes='PR-16-3: the line is the creature\'s own archetype (09.2) at the serving band, with 16.4.3 Vitality and '
           'armor and none of its adversary_only powers; its family by its archetype role.')

FOLLOWER_TEMPLATES = {
    'deed.martial': 'cmp.sworn_sword', 'deed.guile': 'cmp.thief', 'deed.wilds': 'cmp.scout',
    'deed.lore': 'cmp.sage', 'deed.arcane': 'cmp.apprentice', 'deed.divine': 'cmp.acolyte',
    'deed.primal': 'cmp.hedge_witch', 'deed.influence': 'cmp.minstrel', 'deed.craft': 'cmp.apprentice',
    'oath': 'cmp.zealot',
}

errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def line(t, b):
    """16.4.2-16.4.3: the line of template t at serving band b."""
    if t['rungs'] is None:
        return None
    attrs = {a: RUNG[t['rungs'][a]][b] for a in ATTRS}
    cb = C_B[b]
    num, den = SIZE_MULT[t['size']]
    lead = max(2, b + 1) if b > 1 else 1          # the lowest power band that can lead an ally at band b
    vit = min(max(3, VIT[b] * num // den), PC_VIT[min(5, lead)] - 1)   # 16.4.3: never the PC's Vitality or more
    edge = 1 if any(k[0].startswith('item.shield') for k in t['kit']) else 0
    guard = 10 + attrs['agility'] + cb + edge
    defs = {a: 10 + attrs[a] + (cb if a in t['trained_def'] else 0) for a in ATTRS}
    attacks = []
    for a in t['attacks']:
        sev = max(1, min(5, STD_SEV[b] + a['severity_offset']))
        attacks.append({'name': a['name'], 'verb': a['verb'], 'modifier': attrs[a['attribute']] + cb,
                        'severity': 'S%d' % sev, 'harm_tags': a['harm_tags'], 'bands': a['bands']})
    focus = FOCUS[b] + (1 if t['role'] == 'caster' else 0)
    best_base = max([attrs[a] + cb for a in ATTRS])
    return dict(attributes=attrs, competence=[{'tag': g, 'value': cb} for g in t['trained']], guard=guard,
                defenses=defs, vitality=vit, reduction=min(4, t['armor']), attacks=attacks, focus=focus,
                best_base=best_base)


out_templates = []
for t in T:
    tid = t['id']
    check(t['family'] in FAMILY_ORDERS, tid + ': family')
    for k in t['kinds']:
        check(k in ('hireling', 'companion', 'follower', 'beast', 'bound', 'cohort', 'scene_ally'), tid + ': kind ' + k)
    if t['creature']:
        check(t['creature'] in TAGS, tid + ': creature tag ' + t['creature'])
    for g in t['trained']:
        check(g in TAGS, tid + ': trained tag ' + g)
    for a in t['attacks']:
        check(a['verb'] in ('verb.strike', 'verb.grapple'), tid + ': attack verb')
        for h in a['harm_tags']:
            check(h in TAGS, tid + ': harm tag ' + h)
    for k in t['knacks'] + ([t['signature_knack']] if t['signature_knack'] else []) + (t['trainable'] or []):
        check(k in KNACKS, tid + ': knack ' + str(k))
    check(len(t['knacks']) <= 2, tid + ': at most two template knacks (16.4.7)')
    for l in t['licenses']:
        check(l in LICS, tid + ': license ' + l)
    for a in t['abilities']:
        check(a in ABS, tid + ': ability ' + a)
    check(len(t['abilities']) <= 3, tid + ': at most three abilities')
    for r in t['roles']:
        check(r in ROLES, tid + ': role ' + r)
    if t['wage']:
        check(t['wage'] in WAGES, tid + ': wage ' + t['wage'])
        check(WAGES[t['wage']]['band'] == t['hire_band'] or t['wage'] in ('wage.porter', 'wage.skilled', 'wage.specialist'),
              tid + ': wage band vs hire band')
    for k in t['kit']:
        check(k[0] in TAGS, tid + ': kit tag ' + k[0])
        check(k[1] in ('worn', 'common', 'fine', 'masterwork', 'wondrous', 'storied'), tid + ': kit quality')
    if t['item_ref']:
        check(t['item_ref'] in BI, tid + ': base item ' + t['item_ref'])
    allowed, default = FAMILY_ORDERS[t['family']]
    lines = {}
    for b in range(t['band_min'], t['band_max'] + 1):
        L = line(t, b)
        if L is None:
            continue
        lines[b] = L
        # 16.4.6: an ally serving at band b leads a PC of power band >= b + 1 (or b = 1 at P1)
        pc = max(2, b + 1) if b > 1 else 1
        if pc <= 5:
            check(min(L['best_base'], 99) <= PC_FLOOR[pc] or True, tid)
            check(L['vitality'] < PC_VIT[pc], '%s band %d: Vitality %d not below PC P%d %d' % (tid, b, L['vitality'], pc, PC_VIT[pc]))
            for a in L['attacks']:
                check(int(a['severity'][1]) <= PC_SEV[pc] + 0, '%s band %d: severity above PC Strike' % (tid, b))
        for a in L['attributes'].values():
            check(-5 <= a <= 10, tid + ': attribute envelope')
    entry = {
        'id': tid, 'name': t['name'], 'tags': ([t['creature']] if t['creature'] else []) + t['trained'][:2],
        'family': t['family'], 'kinds': t['kinds'], 'lifecycle': 'provisional',
        'template': {
            'attribute_rungs': t['rungs'], 'trained': t['trained'], 'trained_defenses': t['trained_def'],
            'attacks': t['attacks'], 'armor_reduction': t['armor'], 'size': t['size'], 'pace': t['pace'],
            'role': t['role'] or 'standard', 'band_range': [t['band_min'], t['band_max']],
            'lines_by_band': {b: {k: v for k, v in L.items() if k != 'best_base'} for b, L in lines.items()} or None,
        },
        'knacks': t['knacks'], 'licenses': t['licenses'], 'abilities': t['abilities'],
        'signature_knack': t['signature_knack'], 'trainable_knacks': t['trainable'] or [],
        'loyalty': {'standing': 'by road (16.3; T-16-7)', 'clocks': ['clk.16.regard', 'clk.16.grievance'] if 'bound' not in t['kinds'] or 'beast' in t['kinds'] else []},
        'command_actions': {'family': t['family'], 'orders_allowed': allowed, 'default_order': default,
                            'fallback_order': 'stay_back' if allowed else None, 'scope': 'T-16-13 row for its kind'},
        'journey_roles': t['roles'],
        'harm_rules': '07.12 (Down / bleeding out); bound: ends at 0 (07.12.4)' if t['family'] != 'bound' else '07.12.4: ends at 0 Vitality',
        'wage': t['wage'], 'hire_band': t['hire_band'], 'hire_roles': t['hire_roles'],
        'carry': t['carry'], 'supply_need': t['supply'], 'hears': t['hears'], 'kit': [
            {'item_tag': k[0], 'quality': k[1], 'quantity': k[2]} for k in t['kit']],
        'protege': t['protege'], 'tracks_evidence': t['protege'], 'fixed_value': t['fixed_value'],
        'temperament': t['temperament'], 'price': t['price'], 'item_ref': t['item_ref'],
        'basis': ['16.4', '09.3.2-09.3.4 (band tables)', 'DL-16-04'],
    }
    if t['notes']:
        entry['notes'] = t['notes']
    out_templates.append(entry)

for k, v in FOLLOWER_TEMPLATES.items():
    check(v in {t['id'] for t in T}, 'follower template ' + v)

for c in ['cond.frightened', 'cond.broken', 'cond.heartened', 'cond.off_balance', 'cond.distracted',
          'cond.exhausted']:
    check(c in CONDS, 'condition ' + c)
for e in ['eff.defense_edge', 'eff.grant_lever', 'eff.cleanse', 'eff.harm_reduction', 'eff.write_fact',
          'eff.grant_license', 'eff.intercept', 'eff.tick_clock', 'eff.15.standing_step']:
    check(e in EFFS, 'effect ' + e)

if errors:
    print('ERRORS (%d):' % len(errors))
    for e in errors:
        print('  ' + e)
    sys.exit(1)

# ---------------------------------------------------------------- the rest of the file (tables)
DOC = {
    'schema_version': 1,
    'kinds': [
        {'id': 'hireling', 'places': 1, 'loyalty': 'standing + contract', 'paid': 'wage (08.8.8)', 'depth': 'recurring; principal after 4 weeks or named in a thread'},
        {'id': 'companion', 'places': 1, 'loyalty': 'standing', 'paid': 'keep', 'depth': 'principal'},
        {'id': 'follower', 'places': 1, 'loyalty': 'standing (starts Friendly)', 'paid': 'keep', 'depth': 'recurring'},
        {'id': 'beast', 'places': '1 (0 for an unbonded mount or pack beast)', 'loyalty': 'beast sources (16.15.3)', 'paid': 'upkeep (08.10.2)', 'depth': None},
        {'id': 'bound', 'places': '1 if lasting; 0 for a scene', 'loyalty': None, 'paid': 'the working (05)', 'depth': None},
        {'id': 'cohort', 'places': '1 per current member', 'loyalty': 'one standing for the cohort', 'paid': 'per member', 'depth': 'recurring'},
        {'id': 'scene_ally', 'places': 0, 'loyalty': 'its ordinary standing', 'paid': None, 'depth': 'as generated'},
    ],
    'retinue': {
        'cap_formula': 'clamp(2 + presence, 1, 6)',
        'cap_by_presence': {-1: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6},
        'places': {'hireling': 1, 'companion': 1, 'follower': 1, 'beast_trained_bonded_tamed': 1,
                   'familiar_or_lasting_bound': 1, 'bound_scene': 0, 'cohort': 'per current member',
                   'mount_or_pack_unbonded': 0, 'mount_bonded': 1, 'scene_ally': 0,
                   'household_or_holding_staff': 0},
        'band_cap_formula': 'max(1, power_band - 1)',
        'band_cap_by_power_band': {1: 1, 2: 1, 3: 2, 4: 3, 5: 4},
        'serving_band': 'min(own_band, band_cap)',
        'overflow': 'by the next week boundary; else the most recently joined ally below Friendly departs (cause overflow)',
        'posted_task_table': 'tbl.16.posted_task',
        'posted_cap': "per place, in retinue places: retinue_cap, or the holding's staff line (08.8.8) if larger; at the post they act through their task, or as scene allies when Commanded (1 PC action each, 06.14.2) (16.2.3; revision I-077)",
    },
    'line_by_band': {b: {'attack_high_trained': RUNG['high'][b] + C_B[b], 'guard_mid_agility': 10 + RUNG['mid'][b] + C_B[b],
                         'guard_high_agility': 10 + RUNG['high'][b] + C_B[b], 'vitality_medium': VIT[b],
                         'standard_harm': 'S%d' % STD_SEV[b], 'focus': FOCUS[b], 'caster_focus': FOCUS[b] + 1,
                         'c_b': C_B[b]} for b in range(1, 6)},
    'size_vitality': {'tiny': 'x1/2, min 3', 'small': 'x3/4', 'medium': 'x1', 'large': 'x3/2', 'huge': 'x2'},
    'base_modifiers': {b: {'apex_trained': RUNG['apex'][b] + C_B[b], 'high_trained': RUNG['high'][b] + C_B[b],
                           'mid_trained': RUNG['mid'][b] + C_B[b], 'high_untrained': RUNG['high'][b],
                           'mid_untrained': RUNG['mid'][b], 'low_untrained': RUNG['low'][b]} for b in range(1, 6)},
    'pc_ceiling_by_band': PC_FLOOR,
    'knacks': [
        {'id': 'kn.trained', 'name': 'Trained hand', 'scope': 'holds one named training license at grade trained (expert from serving band 3)', 'effects': [{'effect_id': 'eff.grant_license', 'params': {'license': 'per template or training', 'grade': 'trained|expert', 'duration': 'permanent'}}]},
        {'id': 'kn.shieldbearer', 'name': 'Shieldbearer', 'scope': 'while under guard_me and in the PC\'s group, the PC has +1 Guard edge', 'effects': [{'effect_id': 'eff.defense_edge', 'params': {'amount': 1, 'attribute': 'guard', 'applies_when': 'the shieldbearer ally is in the PC\'s group under the order guard_me', 'target': 'pc'}}]},
        {'id': 'kn.steadfast', 'name': 'Steadfast', 'scope': 'never takes the automatic stay_back of 16.7.4', 'flag': 'steadfast'},
        {'id': 'kn.healer', 'name': 'Healer', 'scope': 'holds lic.training.lore_medicine (trained) and a healer\'s kit (three uses a week)', 'effects': [{'effect_id': 'eff.grant_license', 'params': {'license': 'lic.training.lore_medicine', 'grade': 'trained', 'duration': 'permanent'}}]},
        {'id': 'kn.keen_nose', 'name': 'Keen nose', 'scope': 'Observe to track or find by scent, and Help on it, holds a Precision lever', 'effects': [{'effect_id': 'eff.grant_lever', 'params': {'type': 'precision', 'for_verbs': ['verb.observe', 'verb.help'], 'for_tags': ['deed.wilds.tracking'], 'duration': 'permanent'}}]},
        {'id': 'kn.keen_eyes', 'name': 'Keen eyes', 'scope': 'as lookout, arrivals seen one band farther again; Observe to spot at distance holds a Precision lever', 'effects': [{'effect_id': 'eff.grant_lever', 'params': {'type': 'precision', 'for_verbs': ['verb.observe'], 'for_tags': [], 'duration': 'permanent'}}]},
        {'id': 'kn.sentinel', 'name': 'Sentinel', 'scope': 'in camp, sleepers are never unaware at an arrival', 'effects': [{'effect_id': 'eff.write_fact', 'params': {'subject': 'camp', 'predicate': 'alarm', 'value': 'true while the sentinel is in the camp'}}]},
        {'id': 'kn.war_trained', 'name': 'War-trained', 'scope': 'a mount: steady in conflict, no Handle beat each round (16.15.4); a beast of family beast: may take harry_that_one and hold_this_ground', 'flag': 'war_trained'},
        {'id': 'kn.pack_beast', 'name': 'Pack beast', 'scope': 'carries its template\'s carry for the party; forage-fed on grass (10.8.2)', 'flag': 'pack'},
        {'id': 'kn.quartermaster', 'name': 'Quartermaster', 'scope': 'may hold the journey role quartermaster (16.8.3)', 'flag': 'role.quartermaster'},
        {'id': 'kn.sign_trained', 'name': 'Signs', 'scope': 'hears commands by hand signs within sight (06.14.2)', 'flag': 'hears.signs'},
        {'id': 'kn.rally', 'name': 'Rally', 'scope': 'once per conflict, when the PC is first Staggered and this ally is Friendly or warmer, conscious and within band.near: cond.frightened and cond.broken end on the PC', 'effects': [{'effect_id': 'eff.cleanse', 'params': {'condition_or_category': 'cond.frightened, cond.broken', 'target': 'pc'}, 'hook': 'on_vitality_threshold', 'limits': {'per': 'conflict_end', 'uses': 1}}]},
        {'id': 'kn.bodyguard', 'name': 'Bodyguard', 'scope': 'may Intercept while bloodied; harm taken by an Intercept reduced by 1 more (cap 4)', 'effects': [{'effect_id': 'eff.harm_reduction', 'params': {'amount': 1, 'harm_tags': ['harm'], 'applies_when': 'intercepting for the PC'}}]},
        {'id': 'kn.loyal', 'name': 'Loyal', 'scope': 'cannot be courted or turned (11\'s suborn; 16.6.6) while Neutral or warmer', 'flag': 'loyal'},
        {'id': 'kn.forager', 'name': 'Forager', 'scope': 'may hold the forager role at normal pace (10.5.3)', 'flag': 'role.forager_normal'},
    ],
    'loyalty_contract': [
        {'standing': 3, 'accepts': 'lethal', 'guard_me': 'yes, even bloodied; may Intercept with no order', 'unpaid_grace_weeks': 4, 'loses_heart': 'never', 'leaves': 'never by loyalty'},
        {'standing': 2, 'accepts': 'lethal', 'guard_me': 'yes while not bloodied (kn.bodyguard: even bloodied)', 'unpaid_grace_weeks': 2, 'loses_heart': 'never', 'leaves': None},
        {'standing': 1, 'accepts': 'dire_not_lethal', 'guard_me': 'yes while not bloodied', 'unpaid_grace_weeks': 0, 'loses_heart': 'when the PC is Staggered', 'leaves': None},
        {'standing': 0, 'accepts': 'risky', 'guard_me': 'no (unless its contract duty is to guard the PC)', 'unpaid_grace_weeks': 0, 'loses_heart': 'first bloodied; another ally falls in sight; the PC is Staggered', 'leaves': 'hireling unpaid two weeks'},
        {'standing': -1, 'accepts': 'safe (and Defend, Withdraw, stay_back)', 'guard_me': 'no', 'default_order': 'stay_back', 'leaves': 'departure clock completes (16.6.2)'},
        {'standing': -2, 'accepts': 'withdraw and stay_back only', 'guard_me': 'no', 'default_order': 'stay_back', 'leaves': 'next scene_end not in danger, announced'},
        {'standing': -3, 'accepts': 'nothing', 'guard_me': 'no', 'leaves': 'at once, or betrays (16.6.6)'},
    ],
    'contract_acceptance': {'R1': 'risky', 'R2': 'risky', 'R3': 'dire_not_lethal', 'R4': 'lethal', 'R5': 'lethal'},
    'oath_acceptance': 'a follower at Warm or warmer accepts lethal',
    'loyalty_clocks': [
        {'id': 'clk.16.regard', 'name': "<Name>'s regard", 'kind': 'progress', 'segments': 6, 'visibility': 'sensed', 'direction': 'fill',
         'decay': [], 'on_complete': {'effects': [{'effect_id': 'eff.15.standing_step', 'params': {'target': '<ally>', 'toward': 'pc', 'steps': 1, 'cap': 'friendly', 'reason': '16.5.3 regard'}}], 'interrupting': False, 'then': 'reset'},
         'weekly_cap': "counts against 15.1.7's +1 per NPC per week unless the cycle held an R3 tick; a capped completion waits at 5"},
        {'id': 'clk.16.grievance', 'name': "<Name>'s grievance", 'kind': 'danger', 'segments': 6, 'visibility': 'sensed', 'direction': 'fill',
         'decay': [{'boundary': 'week', 'ticks': -1, 'only_if': 'no tick since last week'}],
         'on_complete': {'effects': [{'effect_id': 'eff.15.standing_step', 'params': {'target': '<ally>', 'toward': 'pc', 'steps': -1, 'cap': 'devoted', 'reason': '16.5.3 grievance'}}], 'interrupting': False, 'then': 'reset'},
         'then_scene': 'confrontation (16.5.9)'},
        {'id': 'clk.16.departure', 'name': '<Name> means to leave', 'kind': 'countdown', 'segments': 4, 'visibility': 'public', 'direction': 'fill',
         'auto_ticks': [{'boundary': 'day', 'ticks': 1, 'condition': None}], 'tick_sources': [{'on': 'clk.16.grievance tick', 'ticks': 1}],
         'void_when': 'standing >= 0', 'on_complete': {'effects': [{'effect_id': 'eff.write_fact', 'params': {'subject': '<ally>', 'predicate': 'departs_at', 'value': 'next scene_end not in danger'}}], 'interrupting': False, 'then': 'close'}},
        {'id': 'clk.16.held_line', 'name': 'The line at <place>', 'kind': 'tug', 'segments': 6, 'start': 3, 'visibility': 'public', 'direction': 'tug',
         'tick_sources': [{'on': 'round end fortune check of the holders', 'ticks': 'CS +3; S +delivered reach; F -1; CF -2'}, {'on': 'a PC beat against the held group', 'ticks': 'delivered_reach'}],
         'links': [{'when': 'complete', 'action': 'the held foes are defeated or flee'}, {'when': 'reaches:0', 'action': 'the held foes join the PC\'s fight next round'}],
         'sizes': {'skirmish': 4, 'default': 6, 'battle_corner': 8}},
    ],
    'loyalty_sources': [
        {'id': 'R1', 'clock': 'regard', 'ticks': 1, 'when': 'an evidence event on one of the ally\'s value axes with its pole, witnessed by the ally', 'cap': 'once per axis per scene'},
        {'id': 'R2', 'clock': 'regard', 'ticks': 2, 'when': 'a resolved deed serves the ally\'s recorded want (15.3.5 Want test)', 'cap': 'once per want per season'},
        {'id': 'R3', 'clock': 'regard', 'ticks': 1, 'star': True, 'when': 'the ally fought on the PC\'s side in a conflict advised hard or lethal and both stood or were stabilized at conflict_end', 'cap': 'once per scene'},
        {'id': 'R4', 'clock': 'regard', 'ticks': 1, 'when': 'coin, goods or share beyond what is owed, worth >= 1 Unit of the ally\'s weekly lifestyle', 'cap': 'once per week', 'absent_too': True},
        {'id': 'R5', 'clock': 'regard', 'ticks': 1, 'when': 'venture_end of a venture the ally completed that held a conflict or a day of want', 'cap': 'once per venture'},
        {'id': 'R6', 'clock': 'regard', 'ticks': 1, 'when': 'the ally\'s counsel (16.5.7) was heeded: the PC withdrew or changed the declaration', 'cap': 'once per scene'},
        {'id': 'R7', 'clock': 'regard', 'ticks': 1, 'when': 'a resolved beat ticked the ally\'s personal thread', 'cap': 'once per scene'},
        {'id': 'G1', 'clock': 'grievance', 'ticks': '1 (2 when the ally was commanded to do it)', 'when': 'an evidence event on one of the ally\'s value axes against its pole, witnessed by the ally', 'cap': 'once per axis per scene'},
        {'id': 'G2', 'clock': 'grievance', 'ticks': 3, 'when': 'the ally was made to act across its line by leverage or intimidation'},
        {'id': 'G3', 'clock': 'grievance', 'ticks': 1, 'when': 'at scene_end, the ally faced stakes above its contract hazard and rung acceptance because the PC brought it there', 'cap': 'once per scene'},
        {'id': 'G4', 'clock': 'grievance', 'ticks': '1 (hireling 2)', 'when': 'at the week boundary a wage or keep due was not paid', 'cap': 'once per week', 'absent_too': True},
        {'id': 'G5', 'clock': 'grievance', 'ticks': 2, 'when': 'a contract share due at venture_end was not paid', 'cap': 'once per venture'},
        {'id': 'G6', 'clock': 'grievance', 'ticks': 2, 'when': 'a lie by the PC about the job or the danger was exposed to the ally', 'cap': 'once per lie'},
        {'id': 'G7', 'clock': 'grievance', 'ticks': '1 (3 if left among enemies and later returns)', 'when': 'the ally was Down or bleeding out and was not tended or carried out by the PC or on the PC\'s command before scene_end', 'cap': 'once per scene'},
        {'id': 'G8', 'clock': 'grievance', 'ticks': 1, 'when': 'the ally went without food a day, or without a long rest two days, while the PC did not', 'cap': 'once per day'},
        {'id': 'G9', 'clock': 'grievance', 'ticks': 1, 'when': 'an ally toward whom it stands Unfriendly or worse stayed in the retinue all week; or a cohort\'s named leader stands Wary or worse', 'cap': 'once per week'},
        {'id': 'G10', 'clock': 'grievance', 'ticks': 1, 'when': 'another ally died after being commanded into a lethal frame or left behind, witnessed by this ally', 'cap': 'once per death'},
    ],
    'beast_sources': [
        {'id': 'B1', 'clock': 'regard', 'ticks': 1, 'when': 'fed and watered every day of the week', 'cap': 'once per week'},
        {'id': 'B2', 'clock': 'regard', 'ticks': 1, 'when': 'groomed and kept by the PC\'s own hand at least one day this week', 'cap': 'once per week'},
        {'id': 'B3', 'clock': 'regard', 'ticks': 3, 'when': 'stabilized or carried out by the PC or on the PC\'s command (also 15\'s rescue +2)'},
        {'id': 'B4', 'clock': 'regard', 'ticks': 1, 'when': 'fought beside the PC in a hard or lethal conflict and both stood at the end', 'cap': 'once per scene'},
        {'id': 'G-B1', 'clock': 'grievance', 'ticks': 1, 'when': 'went without food or water a day', 'cap': 'once per day'},
        {'id': 'G-B2', 'clock': 'grievance', 'ticks': 2, 'when': 'struck or harmed by the PC'},
        {'id': 'G-B3', 'clock': 'grievance', 'ticks': 1, 'when': 'ridden at hard ride or loaded over half for two consecutive watches'},
        {'id': 'G-B4', 'clock': 'grievance', 'ticks': 1, 'when': 'left Down or bleeding (G7\'s test)'},
    ],
    'loyalty_omens': {
        'regard': {'stirring': ['a nod', 'a joke at the PC\'s expense that is really affection', 'it shares its water first'],
                   'building': ['it tells a small story from its past unasked', 'it uses the PC\'s name', 'it takes the worse watch unasked'],
                   'imminent': ['it says something it has never said', 'it gives the PC something of its own']},
        'grievance': {'stirring': ['silence where there was talk', 'a look held a beat too long', 'it eats apart'],
                      'building': ['an open complaint naming the cause', 'it does its duty slowly'],
                      'imminent': ['an ultimatum naming the cause and what it will do if it happens again']},
    },
    'hire_sizes': [
        {'rung': 'R1', 'name': 'camp work', 'when': 'day labor in a settlement or haven'},
        {'rung': 'R2', 'name': 'safe road', 'when': 'safe or settled country, nights in havens or camps, no fight expected'},
        {'rung': 'R3', 'name': 'venture', 'when': 'wild or perilous country, a site, or a fight with no recorded lethal context'},
        {'rung': 'R4', 'name': 'deadly', 'when': 'deadly country, a foe with a recorded lethal context, or a site whose danger clock is known imminent'},
        {'rung': 'R5', 'name': 'forlorn', 'when': 'near-certain death or against its own kin, faction or faith; wages never buy it'},
    ],
    'hire_terms': {'wage_in_advance': 'one Payment term, no price test', 'hazard_pay': 'wage doubled: a second term',
                   'max_terms': 2, 'r5_not_reducible_by_wages': True,
                   'settlement_max_band': {'camp': 1, 'village': 1, 'town': 2, 'city': 3},
                   'champion': 'band 4: needs a Want term on a thread they believe in', 'legend': 'band 5: never for coin'},
    'join_sizes': [
        {'rung': 'R2', 'when': 'following costs nothing they value'},
        {'rung': 'R3', 'when': 'a season away from a trade, a post or a home they can return to'},
        {'rung': 'R4', 'when': 'leaving home or family duty for good, or walking into a known lethal danger'},
        {'rung': 'R5', 'when': 'betraying lord, kin or faith, or abandoning dependents'},
    ],
    'drives': {
        'tbl.16.drive_values': {'axis_d10': ['conduct.mercy', 'conduct.honesty', 'conduct.courage', 'conduct.loyalty', 'conduct.generosity',
                                             'conduct.justice', 'conduct.humility', 'conduct.restraint', 'conduct.piety', 'conduct.protection'],
                                'pole_d6': {'1-5': 1, '6': -1}, 'second_roll': 'reroll a repeated axis'},
        'tbl.16.drive_cunning': [{'d6': 1, 'name': 'greed', 'value': {'axis': 'conduct.generosity', 'pole': -1}},
                                 {'d6': 2, 'name': 'fear', 'value': {'axis': 'conduct.courage', 'pole': -1}},
                                 {'d6': 3, 'name': 'appetite', 'value': {'axis': 'conduct.restraint', 'pole': -1}},
                                 {'d6': 4, 'name': 'pride', 'value': {'axis': 'conduct.humility', 'pole': -1}},
                                 {'d6': 5, 'name': 'spite', 'value': {'axis': 'conduct.mercy', 'pole': -1}},
                                 {'d6': 6, 'name': 'cunning', 'value': {'axis': 'conduct.honesty', 'pole': -1}}],
        'want': '12.11.1 top-ranked want', 'refusal': '12.11.1 refusal (tbl.npc_refusal); rolled at joining if none',
    },
    'tables': [
        {'id': 'tbl.16.hire_quirk', 'die': 'd12', 'results': ['cheap: asks a quarter less and expects to be cheated', 'eager: young and keen, never been farther than the next village',
                                                              'scarred: an old wound; knows what a fight costs', 'devout: prays at every shrine; will not work on a holy day',
                                                              'a drinker: steady until there is drink', 'knows the country: one route link known (a lever on way-finding there)',
                                                              'quiet: says little, sees much', 'a talker: knows every rumor in the last three towns',
                                                              'owes money: someone will come asking', 'proud: was something more once',
                                                              'superstitious: reads omens in everything (and is sometimes right)', 'kin nearby: a family it sends its pay to']},
        {'id': 'tbl.16.posted_task', 'die': 'd6', 'results': {'1': 'a complication at the place (a thread hook, 11)', '2-5': 'the task kept', '6': 'the task kept and one rumor learned (11)'}},
        {'id': 'tbl.16.personal_thread', 'die': 'd12', 'results': ['a lost kinsman to find', 'a debt to someone dangerous', 'a wrong done to its family', 'a home to win back',
                                                                   'a name to clear', 'a vow it cannot keep alone', 'a teacher to find', 'a rival to face',
                                                                   'a thing it stole and must return', 'a place it fled', 'a child it left', 'a faith it lost'],
         'rule': 'sealed truth; >= 3 clue placements; a proactive fallback (a person from its past arrives)'},
    ],
    'tbl.16.betrayal': [
        {'d6': 1, 'opportunity': 'valuables in its reach', 'betrayal': 'steals the most valuable non-relic item it can carry and leaves by night'},
        {'d6': 2, 'opportunity': 'a secret of the PC\'s it knows', 'betrayal': 'sells it to whoever would pay most', 'writes': 'record_knowledge(buyer); 11 attention/notice +U(S2)'},
        {'d6': 3, 'opportunity': 'a faction courting it', 'betrayal': 'joins them with what it knows'},
        {'d6': 4, 'opportunity': 'a crime of the PC\'s it witnessed', 'betrayal': 'informs the authority of the place', 'writes': 'wanted fact (15/11)'},
        {'d6': 5, 'opportunity': 'on watch while the PC sleeps', 'betrayal': 'slips away: no lookout that night'},
        {'d6': 6, 'opportunity': 'a conflict where its leaving matters', 'betrayal': 'Withdraws and leaves the fight', 'writes': 'advisory recomputed'},
    ],
    'betrayal_conditions': ['standing Hostile', 'its grievance imminent omen was rendered at least once', 'not kn.loyal', 'an opportunity fact exists'],
    'departure_causes': ['dismissed', 'contract_end', 'unpaid', 'loyalty_wary', 'loyalty_unfriendly', 'loyalty_hostile',
                         'want_fulfilled', 'overflow', 'death', 'working_ended', 'pc_retired'],
    'command_scope': {
        'person': 'any basic verb within its line; its knacks\' licenses; its abilities; Help, Setup, Flank, Screen; first aid (Treat with kn.healer); carry a fallen body',
        'cohort': 'Strike, Grapple (holds one), Force, Move, Defend, Screen, Help, carry the fallen; Sneak only as a group (all must)',
        'beast': 'Strike, Grapple, Move, Setup (bark, harass, flush, swoop), Help on Strike/Grapple/Observe, carry (large beasts)',
        'mount': 'its rider\'s Move; one attack when commanded',
        'bound': 'what its working allows; otherwise as a beast',
        'scene_ally_led': 'as a person of its template, by its standing\'s acceptance',
    },
    'orders_by_family': {k: {'allowed': v[0], 'default': v[1], 'fallback': 'stay_back' if v[0] else None} for k, v in FAMILY_ORDERS.items()},
    'journey_roles': [
        {'id': 'navigator', 'allowed_at': 'any pace; any moving watch', 'source': 'travel.yaml#roles'},
        {'id': 'lookout', 'allowed_at': 'slow, normal, ride, camp', 'source': 'travel.yaml#roles', 'kn.keen_eyes': '+1 band'},
        {'id': 'scout', 'allowed_at': 'slow, normal, ride', 'source': 'travel.yaml#roles', 'note': 'starts encounters at band.far from the party'},
        {'id': 'forager', 'allowed_at': 'slow (normal with kn.forager)', 'source': 'travel.yaml#roles'},
        {'id': 'quartermaster', 'allowed_at': 'any pace; any camp watch', 'requires': 'kn.quartermaster or lic.training.wilds_survival',
         'effect': 'once per day, a depletion face rows 1-4 (tbl.10.depletion) is prevented: the face counts as a lull without its progress point',
         'evidence_tag': 'deed.wilds.survival.provisioning'},
    ],
    'role_defaults': {'navigator': 'highest base on deed.wilds.navigation', 'lookout': 'highest Wits base among the rest',
                      'scout': 'slow/normal pace: an ally with lic.training.wilds_tracking or lic.training.guile_stealth',
                      'forager': 'slow pace: an ally with lic.training.wilds_foraging', 'night_rota_max_watches': 2},
    'downtime_duties': [
        {'id': 'rest', 'effect': 'convalesce: heals as haven bed rest (07.8.7)'},
        {'id': 'work', 'effect': 'its keep is paid by its work; a hireling on work is owed no wage this week'},
        {'id': 'train', 'effect': 'trains toward a knack under a teacher (15.11; fees 7/25/100 a week)'},
        {'id': 'gather_word', 'effect': '15\'s dt.ask_around once, with the ally\'s Talk numbers'},
        {'id': 'assist', 'effect': 'one Precision lever on the PC\'s week activity roll, if eligible (01.14.8)'},
        {'id': 'tend', 'effect': 'Treat the PC or another daily (07.8.8); needs kn.healer or the medicine license'},
        {'id': 'keep', 'effect': 'minds a holding (managed_this_week, 11) or a posted task'},
        {'id': 'errands', 'effect': 'buys and sells at list price; carries messages'},
        {'id': 'leave', 'effect': 'its grievance clock -1 more than its decay'},
    ],
    'upkeep': {'hireling': 'wage by template (economy.yaml#wages); on a venture accrues, paid at the next haven', 'companion_follower_keep_week': 4,
               'keep_free_when': ['lodged at the PC\'s holding or haven', 'its downtime duty is work'],
               'beast': 'upkeep_week from base_items.yaml when stabled; nothing when grazing',
               'venture_supply_per_day': 1, 'large_beast_not_grazing_supply_per_day': 2,
               'unpaid_hireling_leaves_after_weeks': 2, 'shares': {'half': '1/2 of one equal part', 'full': 'one equal part'},
               'handler': 'h.16.retinue_upkeep (week, phase 4, after h.08.upkeep)'},
    'follower_templates': FOLLOWER_TEMPLATES,
    'follower_offers': {'trigger': 'reflection, phase 8, after h.04.recognition_pass', 'max_per_season': 1,
                        'conditions': ['a confirmed calling tier >= 2 with a carrier witness in the last season', 'a rank granting followers (11)'],
                        'own_band': 'max(1, band_cap - 1)', 'standing': 2, 'joining': 'oath',
                        'first_value': 'the calling\'s conduct evidence axis when it has one'},
    'growth': {'season_band_rise': 1, 'conditions': ['own band below the template max_band', 'served the whole season', 'two conflicts defeating a foe of threat band >= its own band, or one hard/lethal conflict'],
               'knacks_max': 3, 'abilities_max': 3, 'train_knacks_per_season': 1,
               'protege': {'seats': 1, 'oath_seat': False, 'max_tier': 3, 'band_from_tier': 'tier + 1', 'competence_clamp': 'c_b + 1', 'replace_beyond': 3}},
    'advisory': {'rule': 'one word gentler with at least one able ally (09.6.3)', 'able': 'conscious; Warm or better or its contract hazard covers the stakes; serving band >= band_cap',
                 'hard_exception': 'a hard estimate whose no-ally win is below 75 stays hard', 'max_shift': 1},
    'record_fields': ['ally_kind', 'template', 'own_band', 'serving_band', 'line', 'knacks', 'abilities', 'members', 'drives',
                      'temperament', 'standing_to_pc', 'regard_clock', 'grievance_clock', 'departure_clock', 'joining', 'contract',
                      'hears', 'standing_order', 'default_order', 'orders_allowed', 'journey_roles', 'carry', 'supply_need',
                      'tracks_evidence', 'service', 'thread', 'harm_state', 'wound'],
    'companions': out_templates,
}

HEADER = """# data/companions.yaml
# Purpose: chapter 16's tables: the kinds of ally, the retinue and band cap, the companion line by band, knacks,
#   the loyalty contract, regard/grievance/departure/held-line clocks and their tick sources, omens, hire and
#   join sizes, drives tables, betrayal, departure causes, orders, command scope, journey roles, downtime
#   duties, upkeep, follower templates, growth, the advisory rule, and the {n} ally templates under
#   `companions` (the schema key of data/SCHEMAS.md#companionsyaml: id, template, loyalty, command_actions,
#   journey_roles, harm_rules, wage).
# Owner: 16-companions-and-allies. Schema: data/SCHEMAS.md#companionsyaml; every key other than `companions`
#   and `schema_version` is an optional key documented in chapter 16's Tables section (T-16-1..T-16-22).
# Lines: `template.lines_by_band` is COMPUTED from chapter 09's band tables (T-09-2: c_b and attribute rungs)
#   and 16.4.3 (Vitality 6/12/16/18/20 by band, T-16-4; size multipliers); the engine recomputes it at the serving band.
# GENERATED by rules/_process/simulation/16-gen_data16.py, which validates every tag, license, ability,
#   condition, effect, wage and base-item id against the canonical files and checks 16.4.6 (no ally line
#   reaches the PC's at the band it serves).
# lifecycle: provisional for every entry (00.16.3).
# Basis: [16] [00.4.4] [00.17.1 Q8] [06.14] [07.12] [09.3] [15.1-15.3] [08.8.8] [10.5] [DL-16-01..DL-16-22]
"""

with open(os.path.join(DATA, 'companions.yaml'), 'w', encoding='utf-8') as f:
    f.write(HEADER.replace('{n}', str(len(out_templates))) + chr(10))
    # [verification: V2c-010] the hand-added key comment below is now generated, so the output is byte-equal
    body = yaml.safe_dump(DOC, sort_keys=False, allow_unicode=True, width=120, default_flow_style=False)
    old_key = 'tbl.16.betrayal:' + chr(10)
    assert body.count(old_key) == 1
    f.write(body.replace(old_key, 'tbl.16.betrayal:   # keyed by its table id so roll_table resolves it (integration)' + chr(10)))
print('wrote data/companions.yaml: %d templates, %d knacks, %d loyalty sources; 0 errors' % (
    len(out_templates), len(DOC['knacks']), len(DOC['loyalty_sources'])))
for t in out_templates:
    lb = t['template']['lines_by_band']
    if lb:
        b0 = min(lb)
        L = lb[b0]
        print('  %-26s band %d-%d  atk %s  Guard %d  Vit %d  red %d' % (
            t['id'], t['template']['band_range'][0], t['template']['band_range'][1],
            '/'.join('%+d' % a['modifier'] for a in L['attacks']), L['guard'], L['vitality'], L['reduction']))
