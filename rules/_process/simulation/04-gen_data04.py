"""gen_data04.py -- generates ch.04's calling data from compact tables and validates every tag id against
data/tags.yaml. Outputs: rules/data/callings.yaml, rules/data/hybrids.yaml, rules/data/contrib/composites.04.yaml.
Numbers mirror the ladders verified by recog04.py."""
import re, sys, io, os
ROOT = os.environ.get('GAME_RULES', os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))) + os.sep
TAGS = set(re.findall(r"\bid: ([a-z_]+(?:\.[a-z_]+)+)", open(ROOT + 'data/tags.yaml', encoding='utf-8').read()))
PROPOSED = {'deed.wilds.animals.falconry'}

def chk(tag):
    assert tag in TAGS or tag in PROPOSED, 'unknown tag ' + tag
    return tag

def q(v):
    if isinstance(v, bool): return 'true' if v else 'false'
    if v is None: return 'null'
    if isinstance(v, int): return str(v)
    if isinstance(v, list): return '[' + ', '.join(q(x) for x in v) + ']'
    if isinstance(v, dict): return '{' + ', '.join(f'{k}: {q(x)}' for k, x in v.items()) + '}'
    s = str(v)
    if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.\-]*', s) and s not in ('true', 'false', 'null', 'yes', 'no', 'none'): return s
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

# ------------------------------------------------------------------ ladders (canonical numbers)
W = {'narrow': [80, 200, 440, 800, 1300], 'fine': [60, 150, 330, 600, 975], 'broad': [120, 300, 660, 1200, 1950],
     'hybrid': [60, 150, 330, 600, 975]}
COMP = {'narrow': [3, 4, 5, 5, 6], 'fine': [3, 4, 5, 5, 6], 'broad': [2, 3, 4, 4, 5], 'hybrid': [2, 3, 4, 4, 5]}
BAND = {'narrow': [1, 2, 3, 4, 5], 'fine': [1, 2, 3, 4, 5], 'broad': [1, 2, 3, 4, 4], 'hybrid': [1, 2, 3, 4, 4],
        'vow': [1, 1, 1, 2, 2], 'dark': [1, 1, 1, 2, 2]}
PICKS = {'deed': [2, 3, 4, 5, 6], 'oath': [1, 1, 2, 2, 3]}
VOW_P = [16, 40, 80, 140, 220]
TIER_NAMES = ['Called', 'Proven', 'Tempered', 'Exalted', 'Paragon']
CAPS = {1: ['lic.call.mark'], 2: ['lic.call.proof'], 3: ['lic.call.sure_hand'], 4: ['lic.call.masters_eye'], 5: ['lic.call.open_art']}
GRADE = {'narrow': ['trained', 'trained', 'expert', 'expert', 'master'], 'fine': ['trained', 'trained', 'expert', 'expert', 'master'],
         'broad': ['trained', 'trained', 'trained', 'expert', 'expert'], 'hybrid': ['trained', 'trained', 'trained', 'expert', 'expert']}

FAMILY = {  # branch -> defaults
 'martial':   dict(attrs=['might', 'agility'], shadow=('The Butcher', ['conduct.mercy', 'conduct.restraint'], 'call.dark_wrath'),
                   grant=['veh.V8', 'veh.V1', 'veh.V7'], offer=['veh.V2', 'veh.V3', 'veh.V5', 'veh.V7'], tier=['veh.V5', 'veh.V2', 'veh.V9', 'veh.V7'], orgs=['org.order.knightly', 'org.company.mercenary', 'org.crown.military']),
 'guile':     dict(attrs=['agility', 'wits'], shadow=('The Faithless', ['conduct.honesty', 'conduct.loyalty'], 'call.dark_betrayal'),
                   grant=['veh.V8', 'veh.V7', 'veh.V1'], offer=['veh.V3', 'veh.V2', 'veh.V5', 'veh.V7'], tier=['veh.V5', 'veh.V2', 'veh.V3', 'veh.V7'], orgs=['org.outlaw.thieves', 'org.outlaw.smugglers', 'org.outlaw.assassins']),
 'wilds':     dict(attrs=['wits', 'endurance'], shadow=('The Feral', ['conduct.protection', 'conduct.generosity'], 'call.dark_cold'),
                   grant=['veh.V1', 'veh.V7'], offer=['veh.V7', 'veh.V11', 'veh.V2', 'veh.V5'], tier=['veh.V5', 'veh.V11', 'veh.V2', 'veh.V7'], orgs=['org.order.hunters', 'org.company.exploring', 'org.clan.tribe']),
 'lore':      dict(attrs=['intellect', 'wits'], shadow=('The Hoarder of Secrets', ['conduct.generosity', 'conduct.humility'], 'call.dark_pride'),
                   grant=['veh.V1', 'veh.V7'], offer=['veh.V3', 'veh.V2', 'veh.V9', 'veh.V7'], tier=['veh.V9', 'veh.V2', 'veh.V5', 'veh.V7'], orgs=['org.guild.scholarly', 'org.order.arcane', 'org.faith.temple']),
 'arcane':    dict(attrs=['intellect', 'resolve'], shadow=('The Overreacher', ['conduct.humility', 'conduct.restraint'], 'call.dark_pride'),
                   grant=['veh.V1', 'veh.V8', 'veh.V7'], offer=['veh.V2', 'veh.V3', 'veh.V5', 'veh.V11', 'veh.V7'], tier=['veh.V5', 'veh.V2', 'veh.V11', 'veh.V9', 'veh.V7'], orgs=['org.order.arcane', 'org.guild.scholarly']),
 'divine':    dict(attrs=['resolve', 'presence'], shadow=('The Zealot', ['conduct.mercy', 'conduct.humility'], 'call.dark_profane'),
                   grant=['veh.V1', 'veh.V7'], offer=['veh.V4', 'veh.V11', 'veh.V3', 'veh.V5'], tier=['veh.V4', 'veh.V5', 'veh.V11', 'veh.V9'], orgs=['org.faith.temple', 'org.faith.shrine', 'org.order.monastic']),
 'primal':    dict(attrs=['resolve', 'endurance'], shadow=('The Wild-Lost', ['conduct.restraint', 'conduct.protection'], 'call.dark_wrath'),
                   grant=['veh.V7', 'veh.V1'], offer=['veh.V11', 'veh.V5', 'veh.V2', 'veh.V7'], tier=['veh.V5', 'veh.V11', 'veh.V2', 'veh.V7'], orgs=['org.order.druidic', 'org.clan.tribe', 'org.faith.shrine']),
 'influence': dict(attrs=['presence', 'wits'], shadow=('The Manipulator', ['conduct.honesty', 'conduct.justice'], 'call.dark_tyranny'),
                   grant=['veh.V1', 'veh.V8', 'veh.V7'], offer=['veh.V3', 'veh.V2', 'veh.V7'], tier=['veh.V3', 'veh.V9', 'veh.V5', 'veh.V7'], orgs=['org.crown.noble', 'org.guild.merchant', 'org.crown.civic']),
 'craft':     dict(attrs=['intellect', 'agility'], shadow=('The Covetous', ['conduct.generosity', 'conduct.honesty'], 'call.dark_greed'),
                   grant=['veh.V1', 'veh.V7'], offer=['veh.V9', 'veh.V3', 'veh.V2', 'veh.V7'], tier=['veh.V9', 'veh.V2', 'veh.V5', 'veh.V7'], orgs=['org.guild.craft', 'org.guild.merchant']),
}
FOCUS = {  # family -> (trigger id, hook, when, text)
 'martial':   ('on_defeat', 'the defeated foe\'s threat band >= your power band and the defeating beat\'s deed tag is under your calling key', 'When you defeat a foe at or above your own band with a deed of your calling, regain 1 Focus.'),
 'guile':     ('on_degree', 'degree = critical_success and deed_tag under your calling key and the obstacle\'s defender was unaware or you held flag.hidden', 'When a deed of your calling critically succeeds against one who never saw it coming, regain 1 Focus.'),
 'wilds':     ('on_boundary', 'boundary = breather and your location is not under terrain.settlement', 'When you complete a breather outside any settlement, regain 1 Focus in addition to what the rest restores.'),
 'lore':      ('on_fact_set', 'pattern = clu.*.found or an unseal delivered by your frame whose deed tag is under your calling key', 'When a deed of your calling uncovers a clue or a sealed fact, regain 1 Focus.'),
 'arcane':    ('on_degree', 'degree = critical_success and the beat used an ability whose first tag is under your calling key', 'When a working of your calling critically succeeds, regain 1 Focus.'),
 'divine':    ('on_condition_removed', 'the condition ended on another being by your ability whose first tag is under your calling key, or on_stabilize by your frame', 'When your calling lifts a condition from another or brings another back from Dying, regain 1 Focus.'),
 'primal':    ('on_boundary', 'boundary = watch (dawn) and you are under open sky or in terrain.forest, terrain.highland, terrain.wetland, terrain.water', 'At dawn under open sky or in wild country, regain 1 Focus.'),
 'influence': ('on_fact_set', 'pattern = a standing step upward toward you written as the delivered result of your frame whose deed tag is under your calling key', 'When a deed of your calling moves someone\'s standing toward you upward, regain 1 Focus.'),
 'craft':     ('on_clock_complete', 'clock kind = project and the completing tick came from your frame whose deed tag is under your calling key', 'When a deed of your calling completes a project clock, regain 1 Focus.'),
}

# ------------------------------------------------------------------ rosters
BRANCH = [('warrior', 'Warrior', 'martial'), ('rogue', 'Rogue', 'guile'), ('wayfarer', 'Wayfarer', 'wilds'),
          ('scholar', 'Scholar', 'lore'), ('wizard', 'Wizard', 'arcane'), ('priest', 'Priest', 'divine'),
          ('druid', 'Druid', 'primal'), ('envoy', 'Envoy', 'influence'), ('artisan', 'Artisan', 'craft')]
L2 = {
 'martial': [('blade', 'Blade'), ('axe', 'Hewer'), ('bludgeon', 'Mauler'), ('polearm', 'Spearhand'), ('archery', 'Archer'),
             ('thrown', 'Hurler'), ('unarmed', 'Brawler'), ('shield', 'Shieldbearer'), ('armor', 'Ironclad'),
             ('tactics', 'Tactician'), ('mounted', 'Cavalier'), ('athletics', 'Athlete')],
 'guile': [('stealth', 'Shadow'), ('thievery', 'Thief'), ('deception', 'Trickster'), ('disguise', 'Masquer'),
           ('ambush', 'Ambusher'), ('poisoncraft', 'Poisoner'), ('escape', 'Escapist'), ('streetwise', 'Fixer')],
 'wilds': [('survival', 'Survivor'), ('tracking', 'Tracker'), ('navigation', 'Pathfinder'), ('animals', 'Beast-handler'),
           ('foraging', 'Forager'), ('seafaring', 'Mariner')],
 'lore': [('history', 'Antiquarian'), ('languages', 'Linguist'), ('bestiary', 'Bestiarist'), ('medicine', 'Physician'),
          ('engineering', 'Engineer'), ('law', 'Jurist'), ('arcana', 'Loremaster'), ('religion', 'Theologian'),
          ('investigation', 'Investigator')],
 'arcane': [('fire', 'Pyromancer'), ('frost', 'Frostbinder'), ('storm', 'Stormcaller'), ('earth', 'Geomancer'),
            ('illusion', 'Illusionist'), ('divination', 'Diviner'), ('warding', 'Abjurer'), ('mind', 'Mesmerist'),
            ('summoning', 'Summoner'), ('necromancy', 'Necromancer'), ('alteration', 'Transmuter')],
 'divine': [('healing', 'Healer'), ('warding', 'Sanctifier'), ('smiting', 'Templar'), ('rites', 'Celebrant'),
            ('oaths', 'Oathkeeper'), ('revelation', 'Oracle'), ('exorcism', 'Exorcist'), ('pact', 'Pactbound')],
 'primal': [('growth', 'Greenwarden'), ('beastkin', 'Beast-speaker'), ('weather', 'Weather-worker'),
            ('shapeshifting', 'Skinchanger'), ('spirits', 'Spirit-talker'), ('elements', 'Elementalist'), ('hexcraft', 'Hexer')],
 'influence': [('persuasion', 'Advocate'), ('command', 'Captain'), ('performance', 'Bard'), ('intimidation', 'Menace'),
               ('intrigue', 'Schemer'), ('trade', 'Merchant'), ('etiquette', 'Courtier'), ('insight', 'Confidant'),
               ('teaching', 'Mentor')],
 'craft': [('smithing', 'Smith'), ('woodcraft', 'Wright'), ('leathercraft', 'Tanner'), ('textiles', 'Weaver'),
           ('alchemy', 'Alchemist'), ('cookery', 'Victualler'), ('building', 'Builder'), ('artifice', 'Tinker'),
           ('jewelcraft', 'Jeweler'), ('enchanting', 'Enchanter'), ('scribing', 'Scribe')],
}
L3 = [  # (id, name, tag)
 ('duelist', 'Duelist', 'deed.martial.blade.fencing'), ('wrestler', 'Wrestler', 'deed.martial.unarmed.wrestling'),
 ('lancer', 'Lancer', 'deed.martial.mounted.charge'), ('acrobat', 'Acrobat', 'deed.martial.athletics.acrobatics'),
 ('champion', 'Champion', 'deed.martial.tactics.single_combat'), ('siegemaster', 'Siege-master', 'deed.martial.tactics.siege'),
 ('assassin', 'Assassin', 'deed.guile.ambush.assassination'), ('lockbreaker', 'Lockbreaker', 'deed.guile.thievery.lockpicking'),
 ('cutpurse', 'Cutpurse', 'deed.guile.thievery.pickpocketing'), ('trapspringer', 'Trapspringer', 'deed.guile.thievery.traps'),
 ('forger', 'Forger', 'deed.guile.disguise.forgery'), ('swindler', 'Swindler', 'deed.guile.deception.con'),
 ('smuggler', 'Smuggler', 'deed.guile.streetwise.smuggling'), ('infiltrator', 'Infiltrator', 'deed.guile.stealth.infiltration'),
 ('herbalist', 'Herbalist', 'deed.wilds.foraging.herbs'), ('falconer', 'Falconer', 'deed.wilds.animals.falconry'),
 ('rider', 'Rider', 'deed.wilds.animals.riding'), ('hunter', 'Hunter', 'deed.wilds.tracking.hunting'),
 ('delver', 'Delver', 'deed.wilds.navigation.underways'), ('pilot', 'Pilot', 'deed.wilds.seafaring.piloting'),
 ('surgeon', 'Surgeon', 'deed.lore.medicine.surgery'), ('cryptographer', 'Cryptographer', 'deed.lore.languages.ciphers'),
 ('barrow_reader', 'Barrow-reader', 'deed.lore.history.ruins'), ('spellbreaker', 'Spellbreaker', 'deed.arcane.warding.countering'),
 ('bonecaller', 'Bonecaller', 'deed.arcane.necromancy.raising'), ('gravekeeper', 'Gravekeeper', 'deed.divine.rites.funerary'),
 ('cursebreaker', 'Cursebreaker', 'deed.primal.hexcraft.unhexing'), ('minstrel', 'Minstrel', 'deed.influence.performance.music'),
 ('skald', 'Skald', 'deed.influence.performance.storytelling'), ('questioner', 'Questioner', 'deed.influence.intimidation.interrogation'),
 ('venturer', 'Venturer', 'deed.influence.trade.venture'), ('bowyer', 'Bowyer', 'deed.craft.woodcraft.bowyery'),
 ('weaponsmith', 'Weaponsmith', 'deed.craft.smithing.weapons'), ('armorer', 'Armorer', 'deed.craft.smithing.armor'),
 ('brewer', 'Brewer', 'deed.craft.cookery.brewing'), ('apothecary', 'Apothecary', 'deed.craft.alchemy.potions'),
 ('cartographer', 'Cartographer', 'deed.craft.scribing.cartography'), ('clockmaker', 'Clockmaker', 'deed.craft.artifice.clockwork'),
 ('trapwright', 'Trapwright', 'deed.craft.artifice.traps'), ('runescribe', 'Runescribe', 'deed.craft.enchanting.inscription'),
]
ATTR_OVERRIDE = {'deed.martial.armor': ['endurance', 'might'], 'deed.martial.athletics': ['might', 'endurance'],
                 'deed.martial.archery': ['agility', 'wits'], 'deed.martial.tactics': ['wits', 'intellect'],
                 'deed.martial.shield': ['might', 'endurance'], 'deed.guile.deception': ['presence', 'wits'],
                 'deed.guile.streetwise': ['wits', 'presence'], 'deed.guile.disguise': ['presence', 'agility'],
                 'deed.wilds.survival': ['endurance', 'wits'], 'deed.wilds.animals': ['presence', 'wits'],
                 'deed.lore.medicine': ['intellect', 'agility'], 'deed.lore.investigation': ['wits', 'intellect'],
                 'deed.influence.insight': ['wits', 'presence'], 'deed.influence.intrigue': ['wits', 'presence'],
                 'deed.influence.teaching': ['presence', 'intellect'], 'deed.craft.smithing': ['might', 'intellect'],
                 'deed.craft.building': ['might', 'intellect'], 'deed.divine.revelation': ['resolve', 'wits'],
                 'deed.primal.shapeshifting': ['endurance', 'resolve'], 'deed.primal.beastkin': ['presence', 'resolve']}
SHADOW_OVERRIDE = {  # key -> (name, axes, turns_to)
 'deed.arcane.necromancy': ('The Grave-Robber of Souls', ['conduct.piety', 'conduct.mercy'], 'call.dark_profane'),
 'deed.arcane.mind': ('The Puppeteer', ['conduct.honesty', 'conduct.justice'], 'call.dark_tyranny'),
 'deed.arcane.summoning': ('The Bound Binder', ['conduct.humility', 'conduct.piety'], 'call.dark_profane'),
 'deed.guile.ambush': ('The Murderer', ['conduct.mercy', 'conduct.justice'], 'call.dark_cruelty'),
 'deed.guile.poisoncraft': ('The Poison in the Well', ['conduct.mercy', 'conduct.honesty'], 'call.dark_cruelty'),
 'deed.influence.intimidation': ('The Terror', ['conduct.mercy', 'conduct.restraint'], 'call.dark_cruelty'),
 'deed.influence.command': ('The Tyrant in Waiting', ['conduct.justice', 'conduct.humility'], 'call.dark_tyranny'),
 'deed.influence.trade': ('The Profiteer', ['conduct.generosity', 'conduct.honesty'], 'call.dark_greed'),
 'deed.primal.hexcraft': ('The Ill-Wisher', ['conduct.mercy', 'conduct.restraint'], 'call.dark_cruelty'),
 'deed.lore.law': ('The Hanging Judge', ['conduct.mercy', 'conduct.justice'], 'call.dark_tyranny'),
 'deed.wilds.tracking': ('The Manhunter', ['conduct.mercy', 'conduct.restraint'], 'call.dark_cruelty'),
}
# oath-type deed callings: keeper kind, axes, forbidden acts [(id, text, axis, unatonable)]
OATH = {
 'deed.divine': dict(keeper='power_served', axes=['conduct.piety'], words='fixed',
    forbidden=[('desecrate_own', 'Desecrate a place, rite or relic sacred to the power you serve.', 'conduct.piety', False),
               ('deny_service', 'Renounce or deny the power you serve before witnesses to escape a cost.', 'conduct.loyalty', False)]),
 'deed.divine.healing': dict(keeper='power_served', axes=['conduct.mercy', 'conduct.piety'], words='fixed',
    forbidden=[('refuse_dying', 'Refuse aid to a dying being that asks it of you when giving it was plainly open.', 'conduct.mercy', False)]),
 'deed.divine.warding': dict(keeper='power_served', axes=['conduct.protection', 'conduct.piety'], words='fixed',
    forbidden=[('abandon_sanctuary', 'Abandon to harm one to whom you granted sanctuary.', 'conduct.protection', False)]),
 'deed.divine.smiting': dict(keeper='power_served', axes=['conduct.justice', 'conduct.piety'], words='fixed',
    forbidden=[('smite_innocent', 'Strike with sacred power one you know to be innocent.', 'conduct.justice', False)]),
 'deed.divine.rites': dict(keeper='power_served', axes=['conduct.piety'], words='fixed',
    forbidden=[('profane_rite', 'Perform a rite falsely for gain, knowing it void.', 'conduct.piety', False)]),
 'deed.divine.oaths': dict(keeper='the_oath_itself', axes=['conduct.loyalty', 'conduct.honesty'], words='personal',
    forbidden=[('break_witnessed_oath', 'Break an oath you witnessed or bound, or help another to break it.', 'conduct.loyalty', False)]),
 'deed.divine.revelation': dict(keeper='power_served', axes=['conduct.honesty', 'conduct.piety'], words='personal',
    forbidden=[('false_prophecy', 'Proclaim as revelation what you know you did not receive.', 'conduct.honesty', False)]),
 'deed.divine.exorcism': dict(keeper='power_served', axes=['conduct.protection', 'conduct.piety'], words='fixed',
    forbidden=[('bargain_with_bound', 'Strike a bargain for gain with a fiend or unquiet dead you were called to cast out.', 'conduct.piety', False)]),
 'deed.divine.pact': dict(keeper='patron_power', axes=['conduct.loyalty'], words='fixed',
    forbidden=[('break_pact_term', 'Break the stated term of your pact.', 'conduct.loyalty', True)]),
 'deed.divine.rites.funerary': dict(keeper='power_served', axes=['conduct.piety'], words='fixed',
    forbidden=[('rob_the_dead', 'Take grave goods from a grave you tend or raise its dead.', 'conduct.piety', False)]),
}

def shadow_for(key, fam):
    s = SHADOW_OVERRIDE.get(key) or SHADOW_OVERRIDE.get('.'.join(key.split('.')[:3])) or FAMILY[fam]['shadow']
    return {'name': s[0], 'conduct': [chk(a) for a in s[1]], 'pole': 'negative', 'shows_at': 'req.shadow', 'turns_to': s[2], 'forbidden_acts': []}

def oath_for(key):
    for k in (key, '.'.join(key.split('.')[:3]), '.'.join(key.split('.')[:2])):
        if k in OATH: return OATH[k]
    return None

def tiers(kind, comp_tags, fam, oath=False, key=None, synergy_by_tier=None, variant=None):
    out = []
    for t in range(1, 6):
        comp = [{'tag': chk(c), 'value': COMP[kind][t - 1]} for c in comp_tags]
        if kind == 'hybrid': comp = [{'tag': 'road:' + c, 'value': COMP[kind][t - 1]} for c in comp_tags]
        d = {'tier': t, 'competence': comp, 'capabilities': CAPS[t], 'synergy': (synergy_by_tier or {}).get(t, [])}
        if t == 4: d['attribute_increase'] = 'one_of_attributes'
        vs = FAMILY[fam]['offer'] if t == 1 else FAMILY[fam]['tier']
        if oath: vs = ['veh.V4'] + [v for v in vs if v != 'veh.V4']
        req = f'req.{kind}.{t}' + ('+' + variant if variant else '')
        d['crystallization'] = {'vehicles': vs, 'requirement': req}
        out.append(d)
    return out

def entry(cid, name, kind, breadth, fam, keys, attrs=None, oath=None, synergy=None, variant=None, extra=None, shadow=None, basis=None):
    key = keys[0]
    lad = breadth
    e = {'id': 'call.' + cid, 'name': name, 'kind': kind, 'breadth': breadth, 'family': fam, 'key_tags': [chk(k) for k in keys],
         'tags': [chk(k) for k in keys],
         'thresholds': {'primary': f'req.{lad}.1.primary', 'secondary': f'req.{lad}.1.secondary'},
         'confidence': 'policy.confidence',
         'max_tier': 5,
         'attributes': attrs or ATTR_OVERRIDE.get('.'.join(key.split('.')[:3])) or FAMILY[fam]['attrs'],
         'shadow': shadow or shadow_for(key, fam)}
    if oath:
        e['oath'] = {'keeper': oath['keeper'], 'axes': [chk(a) for a in oath['axes']], 'words': oath['words'],
                     'forbidden_acts': [{'id': f'forb.{cid}.{f[0]}', 'text': f[1], 'axis': chk(f[2]), 'unatonable': f[3]} for f in oath['forbidden']]}
        e['shadow']['forbidden_acts'] = [f'forb.{cid}.{f[0]}' for f in oath['forbidden']]
    if kind == 'specialist':
        e['focus_trigger'] = 'fg.' + fam
    e['vehicles_default'] = FAMILY[fam]['grant'] + [v for v in FAMILY[fam]['offer'] if v not in FAMILY[fam]['grant']]
    if oath: e['vehicles_default'] = ['veh.V4'] + [v for v in e['vehicles_default'] if v != 'veh.V4']
    if extra: e.update(extra)
    comp_tags = keys if kind != 'hybrid' else keys
    e['tiers'] = tiers(lad, comp_tags if not variant else [keys[0]], fam, bool(oath), key, synergy, variant)
    e['lifecycle'] = 'provisional'
    e['basis'] = basis or ['04.2', 'C:P5', 'DL-04-02']
    return e

CALLINGS = []
for cid, name, br in BRANCH:
    key = 'deed.' + br
    CALLINGS.append(entry(cid, name, 'specialist', 'broad', br, [key], oath=oath_for(key) if br == 'divine' else None,
                          extra={'pool_gate': {'own': [key], 'kin': []}, 'consolidates_from': {'rule': 'two_or_more_held_callings_keyed_under', 'tag': key}}))
for br, lst in L2.items():
    for seg, name in lst:
        key = f'deed.{br}.{seg}'
        cid = name.lower().replace('-', '_').replace(' ', '_')
        CALLINGS.append(entry(cid, name, 'specialist', 'narrow', br, [key], oath=oath_for(key) if br == 'divine' else None,
                              extra={'pool_gate': {'own': [key], 'kin': ['deed.' + br]}}))
for cid, name, key in L3:
    br = key.split('.')[1]
    parent = '.'.join(key.split('.')[:3])
    CALLINGS.append(entry(cid, name, 'specialist', 'fine', br, [key], oath=oath_for(key) if br == 'divine' else None,
                          extra={'pool_gate': {'own': [parent], 'kin': ['deed.' + br]}}))

# variants (same key as a narrow calling, an added requirement: Delve's same-primary, different-secondary family)
monk_oath = dict(keeper='order_or_ideal', axes=['conduct.restraint'], words='personal',
                 forbidden=[('strike_in_rage', 'Maim or kill in anger a being that offered you no harm.', 'conduct.restraint', False)])
CALLINGS.append(entry('monk', 'Monk', 'specialist', 'narrow', 'martial', ['deed.martial.unarmed'], attrs=['agility', 'resolve'],
                      oath=monk_oath, variant='monk',
                      extra={'variant_of': 'call.brawler', 'pool_gate': {'own': ['deed.martial.unarmed'], 'kin': ['deed.martial'], 'conduct': ['conduct.restraint']},
                             'pole': 'positive',   # revision I-007: the Monk's oath draws the positive restraint abilities (05.3.10; 04.8.4)
                             'variant_requirement': 'req.variant.monk'},
                      shadow={'name': 'The Cold Fist', 'conduct': ['conduct.restraint', 'conduct.mercy'], 'pole': 'negative', 'shows_at': 'req.shadow', 'turns_to': 'call.brawler', 'forbidden_acts': []},
                      basis=['04.2.6', 'R3 04.1 (Delve variant families)', 'DL-04-06']))
CALLINGS.append(entry('devourer', 'Devourer', 'specialist', 'narrow', 'lore', ['deed.lore.bestiary'], attrs=['endurance', 'resolve'],
                      variant='devourer',
                      extra={'variant_of': 'call.bestiarist', 'pool_gate': {'own': ['deed.lore.bestiary'], 'kin': ['deed.lore']},
                             'variant_requirement': 'req.variant.devourer', 'special_capability': 'lic.call.taking', 'generator': 'gen.absorb',
                             'vehicles_default': ['veh.V13'], 'price': {'kind': 'bane', 'ref': 'gen_absorb.yaml#banes'}},
                      shadow={'name': 'The Hunger', 'conduct': ['conduct.mercy', 'conduct.restraint'], 'pole': 'negative', 'shows_at': 'req.shadow', 'turns_to': 'call.dark_cruelty', 'forbidden_acts': []},
                      basis=['04.10', 'C:P5 (Blue Mage as a class-gated capability)', 'DL-04-19']))
for c in CALLINGS[-2:]:
    for t in c['tiers']:
        t['crystallization']['vehicles'] = (['veh.V4', 'veh.V3', 'veh.V2'] if c['id'] == 'call.monk' else ['veh.V13', 'veh.V5'])

# hybrids
HY = [  # (a, b, id, name, composite name, from(branch whose deed opens), to, trigger, lever, oath?, text)
 ('martial', 'guile', 'swashbuckler', 'Swashbuckler', 'Feint and Thrust', 'guile', 'martial', 'success', 'precision', None),
 ('martial', 'wilds', 'ranger', 'Ranger', "Hunter's Quarry", 'wilds', 'martial', 'success', 'amplifying', None),
 ('martial', 'lore', 'slayer', 'Slayer', 'Know the Beast', 'lore', 'martial', 'success', 'precision', None),
 ('martial', 'arcane', 'spellblade', 'Spellblade', 'Spellstrike', 'arcane', 'martial', 'focus', 'amplifying', None),
 ('martial', 'divine', 'paladin', 'Paladin', 'Sworn Strike', 'divine', 'martial', 'success', 'protective',
    dict(keeper='power_or_ideal', axes=['conduct.protection', 'conduct.mercy'], words='personal',
         forbidden=[('slay_yielded', 'Slay a being that has yielded to you.', 'conduct.mercy', False),
                    ('abandon_charge', 'Abandon to harm one under your sworn protection.', 'conduct.protection', False)])),
 ('martial', 'primal', 'berserker', 'Berserker', 'Red Mist', 'primal', 'martial', 'bloodied', 'amplifying', None),
 ('martial', 'influence', 'marshal', 'Marshal', 'Lead from the Front', 'martial', 'influence', 'defeat', 'precision', None),
 ('martial', 'craft', 'battlesmith', 'Battlesmith', "Maker's Edge", 'craft', 'martial', 'success', 'protective', None),
 ('guile', 'wilds', 'stalker', 'Stalker', 'Patient Hunter', 'wilds', 'guile', 'success', 'precision', None),
 ('guile', 'lore', 'spy', 'Spy', 'The Dossier', 'lore', 'guile', 'success', 'precision', None),
 ('guile', 'arcane', 'shadowmage', 'Shadowmage', 'Smoke and Glamour', 'arcane', 'guile', 'focus', 'protective', None),
 ('guile', 'divine', 'veiled_hand', 'Veiled Hand', 'Sanctioned Silence', 'divine', 'guile', 'success', 'precision',
    dict(keeper='power_served', axes=['conduct.loyalty', 'conduct.piety'], words='fixed',
         forbidden=[('betray_the_house', "Reveal your order's secrets or turn your craft on those it shelters.", 'conduct.loyalty', False)])),
 ('guile', 'primal', 'changeling', 'Changeling', 'Borrowed Face', 'primal', 'guile', 'focus', 'precision', None),
 ('guile', 'influence', 'charlatan', 'Charlatan', 'The Long Con', 'influence', 'guile', 'success', 'amplifying', None),
 ('guile', 'craft', 'saboteur', 'Saboteur', 'Rigged', 'craft', 'guile', 'success', 'amplifying', None),
 ('wilds', 'lore', 'naturalist', 'Naturalist', 'Field Notes', 'wilds', 'lore', 'success', 'precision', None),
 ('wilds', 'arcane', None, None, 'The formula is learned in a study and proved in a tower; no master of the trail keeps it as one craft. Hold the two callings side by side.', None, None, None, None, None),
 ('wilds', 'divine', 'pilgrim', 'Pilgrim', 'Road Blessing', 'divine', 'wilds', 'success', 'protective',
    dict(keeper='power_served', axes=['conduct.piety', 'conduct.humility'], words='personal',
         forbidden=[('turn_away_traveler', 'Turn away a traveler who asks shelter or water of you in the wild.', 'conduct.generosity', False)])),
 ('wilds', 'primal', 'wildwarden', 'Wildwarden', 'The Land Answers', 'wilds', 'primal', 'success', 'amplifying', None),
 ('wilds', 'influence', 'caravaneer', 'Caravaneer', 'Trail Law', 'wilds', 'influence', 'success', 'precision', None),
 ('wilds', 'craft', 'trapper', 'Trapper', 'Field-Made', 'wilds', 'craft', 'success', 'precision', None),
 ('lore', 'arcane', 'magister', 'Magister', 'Theory into Practice', 'lore', 'arcane', 'success', 'precision', None),
 ('lore', 'divine', 'inquisitor', 'Inquisitor', 'Cited Scripture', 'lore', 'divine', 'success', 'precision',
    dict(keeper='power_served', axes=['conduct.justice', 'conduct.honesty'], words='fixed',
         forbidden=[('condemn_on_falsehood', 'Condemn or punish on evidence you know to be false.', 'conduct.justice', False)])),
 ('lore', 'primal', 'cunning_folk', 'Cunning-folk', 'Old Knowing', 'lore', 'primal', 'success', 'precision', None),
 ('lore', 'influence', 'counselor', 'Counselor', 'Precedent', 'lore', 'influence', 'success', 'amplifying', None),
 ('lore', 'craft', 'inventor', 'Inventor', 'Worked Out on Paper', 'lore', 'craft', 'success', 'protective', None),
 ('arcane', 'divine', 'theurge', 'Theurge', 'Twin Invocation', 'arcane', 'divine', 'focus', 'precision',
    dict(keeper='power_served', axes=['conduct.piety', 'conduct.humility'], words='fixed',
         forbidden=[('bind_the_sacred', "Bind, compel or counterfeit by formula a servant or sign of the power you serve.", 'conduct.piety', False)])),
 ('arcane', 'primal', None, None, 'The formula commands and the living force is asked; each undoes the other in the same hand. No hybrid: a character may hold a calling in each.', None, None, None, None, None),
 ('arcane', 'influence', 'spellsinger', 'Spellsinger', 'Voice and Weave', 'influence', 'arcane', 'success', 'amplifying', None),
 ('arcane', 'craft', 'artificer', 'Artificer', 'Bound in the Making', 'craft', 'arcane', 'success', 'amplifying', None),
 ('divine', 'primal', None, None, 'A named power and the nameless living world do not share a servant in this setting; a pre-made setting may author one for a syncretic faith; the world seed never does (12.16.5).', None, None, None, None, None),
 ('divine', 'influence', 'preacher', 'Preacher', 'Word and Witness', 'influence', 'divine', 'success', 'amplifying',
    dict(keeper='power_served', axes=['conduct.honesty', 'conduct.piety'], words='personal',
         forbidden=[('preach_for_coin', 'Sell a blessing, a rite or a pardon for your own gain.', 'conduct.generosity', False)])),
 ('divine', 'craft', 'reliquarist', 'Reliquarist', 'Hallowed Work', 'craft', 'divine', 'success', 'precision',
    dict(keeper='power_served', axes=['conduct.piety', 'conduct.honesty'], words='fixed',
         forbidden=[('false_relic', 'Pass off as holy a thing you know is not.', 'conduct.honesty', False)])),
 ('primal', 'influence', None, None, 'Spirits are bargained with, not persuaded as folk are; no fused art is recorded. The Spirit-talker (deed.primal.spirits) covers the ground.', None, None, None, None, None),
 ('primal', 'craft', 'hedgewitch', 'Hedgewitch', 'Cauldron and Charm', 'craft', 'primal', 'success', 'amplifying', None),
 ('influence', 'craft', 'magnate', 'Magnate', 'Name on the Work', 'craft', 'influence', 'success', 'amplifying', None),
]
assert len(HY) == 36
TRIG = {
 'success':  ('on_degree', 'degree >= success and deed_tag under {frm}', 'a deed of {frmname} succeeds'),
 'focus':    ('on_focus_spent', 'ability first tag under {frm}', 'you spend Focus through an ability of {frmname}'),
 'defeat':   ('on_defeat', 'the defeating beat\'s deed_tag under {frm}', 'a deed of {frmname} defeats a foe'),
 'bloodied': ('on_vitality_threshold', 'threshold = half (your own Vitality)', 'your own Vitality first falls to half or below in a conflict'),
}
HYBRIDS = []; COMPOSITES = []
for a, b, cid, name, cname, frm, to, trig, lever, oath in HY:
    A, B = chk('deed.' + a), chk('deed.' + b)
    if cid is None:
        HYBRIDS.append({'id': f'hyb.{a}_{b}', 'name': f'{a} x {b}: no hybrid', 'tags': [A, B], 'branches': [A, B], 'calling': 'none', 'reason': cname,
                        'prerequisites': None, 'lifecycle': 'provisional', 'basis': ['04.2.4', 'R3 04.9', 'DL-04-05']})
        continue
    comp_id = 'comp.04.' + cname.lower().replace("'", '').replace(' ', '_').replace('-', '_')
    hook, when, human = TRIG[trig]
    F, T = 'deed.' + frm, 'deed.' + to
    when1 = when.format(frm=F); human1 = human.format(frmname=frm)
    either = when.format(frm=f'{A} or {B}') if trig in ('success', 'focus', 'defeat') else when1
    def rank(n):
        eff = [{'effect_id': 'eff.grant_lever',
                'params': {'type': lever if n < 3 else f'{lever}_or_player_choice_of_type', 'for_tags': [T] if n == 1 else ['the other branch of the pair' if trig != 'bloodied' else T],
                           'duration': 'scene'},
                'hook': hook, 'when': when1 if n == 1 else either, 'limits': {'per': 'scene_end', 'uses': n}}]
        text = (f"When {human1}, you gain a {lever} lever you may cite on one later beat of {to} this scene. Once per scene."
                if n == 1 else
                f"When a deed of either branch ({a} or {b}) {('succeeds' if trig == 'success' else 'defeats a foe' if trig == 'defeat' else 'spends Focus through an ability') if trig != 'bloodied' else ''}"
                f"{', or ' + human1 if trig == 'bloodied' else ''}, you gain a {lever} lever you may cite on one later beat of the other branch this scene. "
                f"{'Twice' if n == 2 else 'Three times'} per scene. A fused deed (primary tag under one branch with a grounded secondary under the other) gains +1 edge"
                + ('.' if n == 2 else ', and once per scene its reach is one rung higher. You may choose the lever\'s type each time.'))
        if trig == 'bloodied' and n > 1:
            text = (f"When {human1}, and whenever a deed of {frm} succeeds, you gain a {lever} lever you may cite on one later beat of {to} this scene. "
                    f"{'Twice' if n == 2 else 'Three times'} per scene. A fused deed (primary tag under one branch with a grounded secondary under the other) gains +1 edge"
                    + ('.' if n == 2 else ', and once per scene its reach is one rung higher. You may choose the lever\'s type each time.'))
        if n >= 2:
            eff.append({'effect_id': 'eff.check_edge', 'params': {'amount': 1, 'applies_when': f'(deed_tag under {A} and secondary_tags under {B}) or (deed_tag under {B} and secondary_tags under {A})'}})
        if n == 3:
            eff.append({'effect_id': 'eff.reach_step', 'params': {'ladder': 'reach', 'steps': 1, 'applies_when': 'a fused deed as above'}, 'limits': {'per': 'scene_end', 'uses': 1}})
        return {'rank': n, 'at_tier': {1: 1, 2: 3, 3: 5}[n], 'effects': eff, 'text': text}
    COMPOSITES.append({'id': comp_id, 'name': cname, 'tags': [A, B], 'keys': [A, B], 'key_kind': 'deed_branch',
                       'active_when': f'actor holds call.{cid} (not suspended by the Fraying, 04.9.3) at the rank\'s tier or higher',
                       'calling': f'call.{cid}', 'ranks': [rank(1), rank(2), rank(3)],
                       'effects': rank(1)['effects'], 'suppresses': [], 'rank_rule': 'the highest rank whose at_tier <= the calling tier replaces the lower ranks (restated, never added)',
                       'lifecycle': 'provisional', 'basis': ['04.5.4', 'C:P6', 'C:P5', 'DL-04-11']})
    syn = {1: [comp_id], 2: [comp_id], 3: [comp_id], 4: [comp_id], 5: [comp_id]}
    fam = a if not oath else 'divine'
    e = entry(cid, name, 'hybrid', 'hybrid', fam, [A, B], attrs=list(dict.fromkeys(FAMILY[a]['attrs'] + FAMILY[b]['attrs'])),
              oath=oath, synergy=syn,
              extra={'pool_gate': {'own': [A, B], 'kin': []}, 'hybrid': f'hyb.{a}_{b}', 'roads': 'the top-weighted level-2 child of each branch at recognition (04.5.2)',
                     'consolidates_from': {'rule': 'one_held_calling_keyed_under_each', 'tags': [A, B]}},
              basis=['04.2.4', 'C:P5 (curated sparse table)', 'R3 04.3, 04.9', 'DL-04-05'])
    e['vehicles_default'] = (['veh.V4'] if oath else []) + ['veh.V12', 'veh.V7']
    for t in e['tiers']:
        t['crystallization']['vehicles'] = ((['veh.V4'] if oath else []) + (['veh.V12', 'veh.V7'] if t['tier'] == 1 else ['veh.V5', 'veh.V12', 'veh.V2', 'veh.V7']))
    CALLINGS.append(e)
    HYBRIDS.append({'id': f'hyb.{a}_{b}', 'name': name, 'tags': [A, B], 'branches': [A, B], 'calling': f'call.{cid}',
                    'prerequisites': {'requirement': 'req.hybrid.1', 'requires_count': 1, 'exclusions': []},
                    'composite': comp_id, 'lifecycle': 'provisional', 'basis': ['04.2.4', 'C:P5', 'R3 04.9-04.10', 'DL-04-05']})

# vows and dark callings (conduct-keyed)
VOWS = [  # axis, id, name, keeper, forbidden text, boon effect per rank (effect_id, params, text)
 ('mercy', 'hospitaller', 'Hospitaller', 'Slay a being that has yielded to you or lies helpless before you.',
    [('eff.grant_lever', {'type': 'precision', 'for_verbs': ['verb.talk'], 'applies_when': 'the target is bloodied or defeated and the intent is to make it yield or stand down', 'duration': 'scene'}, 'Cite your vow as a Precision lever on Talk to make a bloodied or beaten foe yield.'),
     ('eff.grant_lever', {'type': 'precision_and_protective', 'for_verbs': ['verb.talk'], 'applies_when': 'as rank 1', 'duration': 'scene'}, 'Cite your vow as a Precision lever and a Protective lever on Talk to make a bloodied or beaten foe yield.'),
     ('eff.grant_lever', {'type': 'precision_and_protective', 'for_verbs': ['verb.talk', 'verb.handle'], 'applies_when': 'as rank 1, or first aid to any being', 'duration': 'scene'}, 'As rank 2, and also on Handle to give first aid to any being, friend or foe.')]),
 ('honesty', 'truthsworn', 'Truthsworn', 'Deceive for your own gain one who relies on your word.',
    [('eff.grant_lever', {'type': 'precision', 'for_verbs': ['verb.talk'], 'applies_when': 'you state a truth that an established fact supports (cite the fact)', 'duration': 'scene'}, 'Cite your vow as a Precision lever on Talk when what you say is supported by an established fact you cite.'),
     ('eff.grant_lever', {'type': 'precision', 'for_verbs': ['verb.talk', 'verb.observe'], 'applies_when': 'as rank 1, or Observe to read whether another is lying', 'duration': 'scene'}, 'As rank 1, and on Observe to read whether another is lying.'),
     ('eff.grant_lever', {'type': 'precision_and_amplifying', 'for_verbs': ['verb.talk', 'verb.observe'], 'applies_when': 'as rank 2', 'duration': 'scene'}, 'As rank 2, with an Amplifying lever as well.')]),
 ('courage', 'dauntless', 'Dauntless', 'Abandon a charge, companion or sworn post to danger out of fear.',
    [('eff.defense_edge', {'amount': 1, 'attribute': 'resolve', 'applies_when': 'the effect carries trait.nature.mental and would apply cond.frightened'}, '+1 to Resolve defense and Endure checks against being frightened.'),
     ('eff.condition_immunity', {'forbid': {'conditions': ['cond.frightened']}, 'target': 'self'}, 'cond.frightened cannot be applied to you.'),
     ('eff.condition_immunity', {'forbid': {'conditions': ['cond.frightened']}, 'target': 'self_and_allies_within_band.close'}, 'cond.frightened cannot be applied to you or to allies within the close band of you.')]),
 ('loyalty', 'liegesworn', 'Liegesworn', 'Betray the person, house or cause you named when you swore.',
    [('eff.check_edge', {'amount': 1, 'applies_when': 'verb = help and the helped actor is the one you are sworn to, or the beat directly serves the sworn cause (cite the commitment)'}, '+1 edge on Help given to the one you are sworn to, and on beats that directly serve the sworn cause.'),
     ('eff.check_edge', {'amount': 2, 'applies_when': 'as rank 1'}, '+2 edge on the same beats.'),
     ('eff.check_edge', {'amount': 2, 'applies_when': 'as rank 1; and once per scene such a beat has stakes one rung lower'}, '+2 edge on the same beats; once per scene one of them has its stakes one rung lower.')]),
 ('generosity', 'almsgiver', 'Almsgiver', 'Take from those in need, or withhold what you owe them, for your own gain.',
    [('eff.grant_lever', {'type': 'amplifying', 'for_verbs': ['verb.talk'], 'applies_when': 'the target has received a gift from you recorded as a generosity deed (cite the event)', 'duration': 'scene'}, 'Cite a recorded gift as an Amplifying lever on Talk with the one who received it or with their community.'),
     ('eff.grant_lever', {'type': 'amplifying_and_precision', 'for_verbs': ['verb.talk'], 'applies_when': 'as rank 1', 'duration': 'scene'}, 'As rank 1, with a Precision lever as well.'),
     ('eff.grant_lever', {'type': 'amplifying_and_precision', 'for_verbs': ['verb.talk', 'verb.help'], 'applies_when': 'as rank 1, or Help given to any being in need', 'duration': 'scene'}, 'As rank 2, and on Help given to any being in need.')]),
 ('justice', 'justiciar', 'Justiciar', 'Punish one you know to be innocent, or let the guilty escape answer for your own gain.',
    [('eff.grant_lever', {'type': 'precision', 'for_verbs': ['verb.observe', 'verb.talk'], 'applies_when': 'the beat exposes a falsehood, a theft or a broken law and you cite the evidence fact', 'duration': 'scene'}, 'Cite your vow as a Precision lever on Observe or Talk to expose a wrong, when you cite the evidence.'),
     ('eff.grant_lever', {'type': 'precision_and_amplifying', 'for_verbs': ['verb.observe', 'verb.talk'], 'applies_when': 'as rank 1', 'duration': 'scene'}, 'As rank 1, with an Amplifying lever as well.'),
     ('eff.grant_lever', {'type': 'precision_and_amplifying', 'for_verbs': ['verb.observe', 'verb.talk', 'verb.strike', 'verb.grapple'], 'applies_when': 'as rank 1, or a Strike or Grapple to seize one the evidence condemns', 'duration': 'scene'}, 'As rank 2, and on a Strike or Grapple to seize one the cited evidence condemns.')]),
 ('humility', 'penitent', 'Penitent', 'Demand deference or take credit that is another\'s.',
    [('eff.restore', {'quantity': 'focus', 'units': 1, 'target': 'self', 'hook': 'on_degree', 'when': 'your Help beat\'s helped attempt succeeds', 'limits': {'per': 'scene_end', 'uses': 1}}, 'When an attempt you Helped succeeds, regain 1 Focus. Once per scene.'),
     ('eff.restore', {'quantity': 'focus', 'units': 1, 'target': 'self', 'hook': 'on_degree', 'when': 'as rank 1', 'limits': {'per': 'scene_end', 'uses': 2}}, 'The same, twice per scene.'),
     ('eff.restore', {'quantity': 'focus', 'units': 1, 'target': 'self_and_helped', 'hook': 'on_degree', 'when': 'as rank 1', 'limits': {'per': 'scene_end', 'uses': 2}}, 'The same, twice per scene, and the one you Helped also regains 1 Focus.')]),
 ('restraint', 'ascetic', 'Ascetic', 'Give way to rage or appetite so that another is harmed or a duty is broken.',
    [('eff.defense_edge', {'amount': 1, 'attribute': 'resolve', 'applies_when': 'the effect carries trait.nature.mental'}, '+1 to Resolve defense and Endure checks against effects on the mind.'),
     ('eff.defense_edge', {'amount': 2, 'attribute': 'resolve', 'applies_when': 'as rank 1'}, '+2 to the same.'),
     ('eff.condition_immunity', {'forbid': {'conditions': ['cond.charmed']}, 'target': 'self', 'with': 'eff.defense_edge amount 2 as rank 2'}, '+2 to the same, and cond.charmed cannot be applied to you.')]),
 ('piety', 'devout', 'Devout', 'Desecrate what is sacred to the power or the dead you honor.',
    [('eff.grant_lever', {'type': 'protective', 'for_tags': ['deed.divine', 'deed.lore.religion'], 'applies_when': 'you are on ground a fact marks consecrated or tended, or the beat is a rite', 'duration': 'scene'}, 'Cite your vow as a Protective lever on rites and on any beat made on consecrated ground.'),
     ('eff.grant_lever', {'type': 'protective_and_precision', 'for_tags': ['deed.divine', 'deed.lore.religion'], 'applies_when': 'as rank 1', 'duration': 'scene'}, 'As rank 1, with a Precision lever as well.'),
     ('eff.harm_resistance', {'factor': 0.5, 'harm_tags': ['harm.blight.necrotic'], 'with': 'the levers of rank 2'}, 'As rank 2, and you halve necrotic harm.')]),
 ('protection', 'shieldsworn', 'Shieldsworn', 'Abandon to harm a helpless being you could plainly have shielded.',
    [('eff.intercept', {'new_target': 'self', 'applies_when': 'an ally or a helpless being engaged with you is hit', 'limits': {'per': 'scene_end', 'uses': 1}}, 'Once per scene, take a hit meant for an ally or a helpless being engaged with you.'),
     ('eff.intercept', {'new_target': 'self', 'applies_when': 'as rank 1', 'limits': {'per': 'scene_end', 'uses': 2}, 'with': 'eff.harm_reduction amount 1 on the intercepted hit'}, 'Twice per scene, and reduce the harm of an intercepted hit by 1.'),
     ('eff.intercept', {'new_target': 'self', 'applies_when': 'an ally or a helpless being within the close band is hit', 'limits': {'per': 'scene_end', 'uses': 3}, 'with': 'eff.harm_reduction amount 1 on the intercepted hit'}, 'Three times per scene, from the close band, reducing the harm by 1.')]),
]
DARK = [  # axis, id, name, power text, virtue that frays it, boon ranks
 ('mercy', 'cruelty', 'Pitiless',
    [('eff.harm_edge', {'amount': 1, 'applies_when': 'the target is bloodied'}, '+1 harm against a bloodied target.'),
     ('eff.harm_edge', {'amount': 1, 'applies_when': 'the target is bloodied, prone, grabbed, restrained or frightened'}, '+1 harm against a target that is bloodied, prone, grabbed, restrained or frightened.'),
     ('eff.harm_edge', {'amount': 2, 'applies_when': 'as rank 2'}, '+2 harm against the same.')]),
 ('honesty', 'deceit', 'Deceiver',
    [('eff.check_edge', {'amount': 1, 'applies_when': 'deed_tag under deed.guile.deception and the target\'s standing toward you >= 1'}, '+1 edge on deception against one who thinks well of you.'),
     ('eff.check_edge', {'amount': 2, 'applies_when': 'as rank 1'}, '+2 edge on the same.'),
     ('eff.check_edge', {'amount': 2, 'applies_when': 'deed_tag under deed.guile.deception or deed.guile.disguise, any target'}, '+2 edge on any deception or disguise.')]),
 ('loyalty', 'betrayal', 'Betrayer',
    [('eff.grant_lever', {'type': 'amplifying', 'for_tags': ['deed.guile.ambush'], 'applies_when': 'the target\'s standing toward you >= 1', 'duration': 'scene'}, 'An Amplifying lever on any ambush against one who trusts you.'),
     ('eff.grant_lever', {'type': 'amplifying_and_precision', 'for_tags': ['deed.guile.ambush'], 'applies_when': 'as rank 1', 'duration': 'scene'}, 'An Amplifying and a Precision lever on the same.'),
     ('eff.grant_lever', {'type': 'amplifying_and_precision', 'for_tags': ['deed.guile'], 'applies_when': 'as rank 1', 'duration': 'scene'}, 'The same on any deed of guile against one who trusts you.')]),
 ('generosity', 'greed', 'Grasping',
    [('eff.check_edge', {'amount': 1, 'applies_when': 'deed_tag under deed.influence.trade or deed.guile.thievery'}, '+1 edge on trade and theft.'),
     ('eff.check_edge', {'amount': 2, 'applies_when': 'as rank 1'}, '+2 edge on the same.'),
     ('eff.check_edge', {'amount': 2, 'applies_when': 'as rank 1; and once per scene such a beat has reach one rung higher'}, '+2 edge on the same; once per scene one such beat reaches one rung further.')]),
 ('justice', 'tyranny', 'Tyrant',
    [('eff.grant_lever', {'type': 'precision', 'for_tags': ['deed.influence.intimidation', 'deed.influence.command'], 'applies_when': 'the target holds lower rank or station than you, or is in your power (cite the fact)', 'duration': 'scene'}, 'A Precision lever on intimidation and command against those beneath you or in your power.'),
     ('eff.grant_lever', {'type': 'precision_and_amplifying', 'for_tags': ['deed.influence.intimidation', 'deed.influence.command'], 'applies_when': 'as rank 1', 'duration': 'scene'}, 'A Precision and an Amplifying lever on the same.'),
     ('eff.apply_condition', {'condition': 'cond.frightened', 'severity': 'S2', 'duration': 'scene', 'target': 'the target of a successful intimidation as rank 1', 'with': 'the levers of rank 2', 'limits': {'per': 'scene_end', 'uses': 1}}, 'As rank 2; once per scene a successful intimidation also frightens its target (S2) for the scene.')]),
 ('humility', 'pride', 'Vainglorious',
    [('eff.defense_edge', {'amount': 1, 'attribute': 'resolve', 'applies_when': 'the aimed action is Talk'}, '+1 to Resolve defense against being talked round.'),
     ('eff.defense_edge', {'amount': 2, 'attribute': 'resolve', 'applies_when': 'as rank 1'}, '+2 to the same.'),
     ('eff.defense_edge', {'amount': 2, 'attribute': 'resolve', 'applies_when': 'any aimed action or effect carrying trait.nature.mental'}, '+2 to Resolve defense against any effect on the mind.')]),
 ('restraint', 'wrath', 'Wrathful',
    [('eff.harm_edge', {'amount': 1, 'applies_when': 'you are bloodied'}, '+1 harm while you are bloodied.'),
     ('eff.harm_edge', {'amount': 1, 'applies_when': 'you are bloodied or took harm since your last turn'}, '+1 harm while you are bloodied or have taken harm since your last turn.'),
     ('eff.harm_edge', {'amount': 2, 'applies_when': 'as rank 2'}, '+2 harm in the same state.')]),
 ('piety', 'profane', 'Defiler',
    [('eff.harm_resistance', {'factor': 0.5, 'harm_tags': ['harm.radiance.holy']}, 'Halve holy harm you take.'),
     ('eff.grant_lever', {'type': 'precision', 'for_tags': ['deed.arcane.warding.dispelling', 'deed.guile.thievery'], 'applies_when': 'the obstacle is a consecration, sanctuary or holy ward', 'duration': 'scene', 'with': 'eff.harm_resistance as rank 1'}, 'As rank 1, and a Precision lever against consecrations, sanctuaries and holy wards.'),
     ('eff.grant_lever', {'type': 'precision_and_amplifying', 'for_tags': ['deed.arcane.warding.dispelling', 'deed.guile.thievery', 'deed.martial'], 'applies_when': 'the obstacle or target carries trait.nature.sacred', 'duration': 'scene', 'with': 'eff.harm_resistance as rank 1'}, 'As rank 2, with an Amplifying lever, against anything sacred.')]),
 ('protection', 'cold', 'Coldheart',
    [('eff.defense_edge', {'amount': 1, 'attribute': 'resolve', 'applies_when': 'the aimed action is a Talk that appeals to pity, kinship or duty'}, '+1 to Resolve defense against appeals to pity, kinship or duty.'),
     ('eff.condition_immunity', {'forbid': {'conditions': ['cond.charmed']}, 'target': 'self'}, 'cond.charmed cannot be applied to you.'),
     ('eff.condition_immunity', {'forbid': {'conditions': ['cond.charmed', 'cond.frightened']}, 'target': 'self'}, 'Neither cond.charmed nor cond.frightened can be applied to you.')]),
]
def conduct_entry(axis, cid, name, kind, forbidden, ranks):
    ax = chk('conduct.' + axis)
    e = {'id': 'call.' + cid, 'name': name, 'kind': 'specialist', 'breadth': kind, 'family': 'sacred' if kind == 'vow' else 'dark',
         'key_tags': [ax], 'tags': [ax], 'pole': 'positive' if kind == 'vow' else 'negative',
         'thresholds': {'primary': f'req.{kind}.1.primary', 'secondary': 'none (conduct evidence has no counted tally; the ground of every entry is a state write, 03.3.3)'},
         'confidence': 'policy.offer_only', 'max_tier': 5, 'attributes': ['resolve', 'presence'],
         'pool_gate': {'own': [], 'kin': [], 'conduct': [ax]}}
    if kind == 'vow':
        e['oath'] = {'keeper': 'the_one_sworn_to (a power, an order, a person or the ideal itself; named when the words are spoken)', 'axes': [ax], 'words': 'personal',
                     'forbidden_acts': [{'id': f'forb.{cid}.core', 'text': forbidden, 'axis': ax, 'unatonable': False}]}
        e['shadow'] = {'name': 'The Letter over the Spirit', 'conduct': [ax], 'pole': 'negative', 'shows_at': 'req.fraying.1', 'turns_to': 'call.dark_' + dict((d[0], d[1]) for d in DARK).get(axis, 'none') if axis != 'courage' else 'none', 'forbidden_acts': [f'forb.{cid}.core']}
        e['vehicles_default'] = ['veh.V4', 'veh.V11', 'veh.V7']
    else:
        e['oath'] = {'keeper': 'an_interested_power (named at the bargain; sealed until it speaks)', 'axes': [ax], 'words': 'fixed', 'reversed': True,
                     'forbidden_acts': []}
        e['shadow'] = {'name': 'The Thaw', 'conduct': [ax], 'pole': 'positive', 'shows_at': 'req.fraying_dark.1', 'turns_to': 'none (release; the matching vow may be offered when eligible)', 'forbidden_acts': []}
        e['vehicles_default'] = ['veh.V13', 'veh.V8']
        e['price'] = {'kind': 'bane', 'text': 'While held, the first time each scene that you record a positive deed on this axis, lose 1 Focus (the power takes its due).',
                      'effect': {'effect_id': 'eff.drain', 'params': {'quantity': 'focus', 'units': 1, 'target': 'self'}, 'hook': 'on_tag_event', 'when': f'tag = {ax} and sign = +1', 'limits': {'per': 'scene_end', 'uses': 1}}}
    e['boon'] = [{'rank': i + 1, 'at_tier': [1, 3, 5][i], 'effect_id': r[0], 'params': r[1], 'text': r[2]} for i, r in enumerate(ranks)]
    ts = []
    for t in range(1, 6):
        ts.append({'tier': t, 'competence': [], 'capabilities': CAPS[t] if t in (1, 2, 5) else [], 'synergy': [],
                   'crystallization': {'vehicles': e['vehicles_default'], 'requirement': f'req.{kind}.{t}'}})
    e['tiers'] = ts
    e['lifecycle'] = 'provisional'
    e['basis'] = ['04.2.5', 'C:P5 (specialists may key on conduct tags)', 'R6 R-A6', 'DL-04-07']
    return e
for axis, cid, name, forb, ranks in VOWS:
    CALLINGS.append(conduct_entry(axis, cid, name, 'vow', forb, ranks))
for axis, cid, name, ranks in DARK:
    CALLINGS.append(conduct_entry(axis, 'dark_' + cid, name, 'dark', None, ranks))

ids = [c['id'] for c in CALLINGS]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
# every turns_to must exist
for c in CALLINGS:
    tt = c['shadow']['turns_to']
    assert tt.startswith('none') or tt in ids, (c['id'], tt)

# ------------------------------------------------------------------ write callings.yaml
def dump_calling(c):
    lines = [f"  - id: {c['id']}"]
    for k, v in c.items():
        if k in ('id', 'tiers'): continue
        lines.append(f"    {k}: {q(v)}")
    lines.append('    tiers:')
    for t in c['tiers']:
        lines.append('      - ' + q(t))
    return '\n'.join(lines)

HEADER = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '04-callings_header.yaml'), encoding='utf-8').read()
out = io.StringIO()
out.write(HEADER)
out.write('''
# ---------------------------------------------------------------------------------------------------------------
# Families (04.2.2): defaults shared by every calling of a deed branch, and the two conduct families.
# focus_trigger (specialists, from tier 2): one bounded Focus-generation trigger per family (C:P9 companion;
# R3 T-1). Units and limits are within ch.05's envelope; ch.05 may retune them (04 Interface requests).
# ---------------------------------------------------------------------------------------------------------------
families:
''')
for fam, f in FAMILY.items():
    fg = FOCUS[fam]
    out.write('  - ' + q({'id': fam, 'branch': 'deed.' + fam, 'attributes_default': f['attrs'], 'org_tags': f['orgs'],
                           'shadow_default': {'name': f['shadow'][0], 'conduct': f['shadow'][1], 'turns_to': f['shadow'][2]},
                           'vehicles': {'grant': f['grant'], 'offer': f['offer'], 'tier': f['tier'], 'abstain': ['veh.V6'], 'revocation': ['veh.V14']},
                           'focus_trigger': {'id': 'fg.' + fam, 'effect_id': 'eff.restore', 'params': {'quantity': 'focus', 'units': 1, 'target': 'self'},
                                             'hook': fg[0], 'when': fg[1],
                                             'limits_by_rank': {'rank_1': {'per': 'scene_end', 'uses': 1}, 'rank_2': {'per': 'scene_end', 'uses': 2}},
                                             'text': fg[2]}}) + '\n')
out.write('  - ' + q({'id': 'sacred', 'branch': 'conduct (positive poles)', 'attributes_default': ['resolve', 'presence'], 'org_tags': ['org.faith', 'org.order'],
                       'vehicles': {'grant': [], 'offer': ['veh.V4', 'veh.V11', 'veh.V7'], 'tier': ['veh.V4', 'veh.V11', 'veh.V7'], 'abstain': ['veh.V6'], 'revocation': ['veh.V14']}}) + '\n')
out.write('  - ' + q({'id': 'dark', 'branch': 'conduct (negative poles)', 'attributes_default': ['resolve', 'presence'], 'org_tags': ['org.cult'],
                       'vehicles': {'grant': [], 'offer': ['veh.V13', 'veh.V8'], 'tier': ['veh.V13', 'veh.V8'], 'abstain': ['veh.V6'], 'revocation': ['veh.V14']}}) + '\n')
out.write('\ncallings:\n')
def section(title): out.write(f'\n  # ============================ {title} ============================\n')
groups = [('BRANCH CALLINGS (broad; key at level 1)', [c for c in CALLINGS if c.get('breadth') == 'broad']),
          ('LEVEL-2 CALLINGS (narrow; key at level 2)', [c for c in CALLINGS if c.get('breadth') == 'narrow' and 'variant_of' not in c]),
          ('LEVEL-3 CALLINGS (fine; key at level 3)', [c for c in CALLINGS if c.get('breadth') == 'fine']),
          ('VARIANT CALLINGS (same key as a narrow calling, plus an added requirement)', [c for c in CALLINGS if 'variant_of' in c]),
          ('HYBRID CALLINGS (key: two deed branches; table in hybrids.yaml)', [c for c in CALLINGS if c['kind'] == 'hybrid']),
          ('VOWS (conduct-keyed, positive pole; the oath seat)', [c for c in CALLINGS if c.get('breadth') == 'vow']),
          ('DARK CALLINGS (conduct-keyed, negative pole; the oath seat)', [c for c in CALLINGS if c.get('breadth') == 'dark'])]
n = 0
for title, lst in groups:
    section(f'{title}: {len(lst)}')
    for c in lst:
        out.write(dump_calling(c) + '\n'); n += 1
assert n == len(CALLINGS)
open(ROOT + 'data/callings.yaml', 'w', encoding='utf-8', newline='\n').write(out.getvalue())

# ------------------------------------------------------------------ hybrids.yaml
h = io.StringIO()
h.write("""# data/hybrids.yaml
# Purpose: the curated sparse table of hybrid callings. One row for every one of the C(9,2) = 36 pairs of
#   distinct deed branches: a named hybrid calling, or an explicit `calling: none` with its reason.
#   "Sparse" means the table is keyed ONLY to branch pairs, never to deeper tags or to abilities (C:P5;
#   R3 04.9, T-5). A hybrid is offered beside the single-track candidates, never instead of them (04.7.6).
# Owner: 04-recognition-and-growth (T-00-19). Schema: data/SCHEMAS.md#hybridsyaml. Optional fields added by
#   ch.04 (documented in 04 Tables, T-04-3): name, reason (for none rows), composite, prerequisites.exclusions,
#   prerequisites.requires_count.
# The numeric trigger (min, balance, joint scenes, recent floor) is req.hybrid.* in callings.yaml#requirements;
#   it was calibrated by simulation (rules/_process/simulation/04-recognition-sim.md, R4).
# Basis: [C:P5 curated sparse table] [R3 04.3, 04.4, 04.9, 04.10, G-1] [R6 V12] [DL-04-05]

schema_version: 1
lifecycle: provisional
pairs_total: 36
named: %d
none: %d

hybrids:
""" % (sum(1 for x in HYBRIDS if x['calling'] != 'none'), sum(1 for x in HYBRIDS if x['calling'] == 'none')))
for x in HYBRIDS:
    h.write('  - ' + q(x) + '\n')
open(ROOT + 'data/hybrids.yaml', 'w', encoding='utf-8', newline='\n').write(h.getvalue())

# ------------------------------------------------------------------ contrib/composites.04.yaml
c = io.StringIO()
c.write("""# data/contrib/composites.04.yaml
# Purpose: ch.04's owner-block for data/composites.yaml (owner 05; owner-block 04 per T-00-19): the named
#   synergy composite of every hybrid calling (constitution P6 as used by P5: "a hybrid-only technique requiring
#   both ... to trigger"). One composite per named hybrid: %d entries. Specialists, vows and dark callings carry
#   no composite (their tier rewards are in callings.yaml: focus_generation and boon).
# Owner: 04-recognition-and-growth. Schema: data/SCHEMAS.md#compositesyaml (keys: exactly two; key_kind
#   deed_branch). Optional fields added by ch.04: name, calling, ranks [{rank, at_tier, effects, text}], rank_rule.
#   `effects` (the required field) holds rank 1; a higher rank REPLACES the lower one (04.5.5: restated, never
#   appended).
# Every effect is a core effect of data/effects.yaml with parameters; none is new. The expression key
#   `secondary_tags` is requested of 00 (04 Interface requests); until it exists the edge applies when the frame
#   records a grounded secondary (03.1.6) under the other branch.
# Bounds (audit): a lever counts toward the two-lever limit and the +/-4 circumstance cap (00.3.9); edge is capped
#   at +2 in total (00.3.5); a reach step is capped by the step family (00.10.6). No composite adds an action.
# Basis: [C:P6] [C:P5] [R2 4c Twinborn / Three Lashings; bounded] [R3 04.19] [DL-04-11]

schema_version: 1
blocks:
  - owner: "04"
    entries:
""" % len(COMPOSITES))
for x in COMPOSITES:
    c.write(f"      - id: {x['id']}\n")
    for k, v in x.items():
        if k in ('id', 'ranks'): continue
        c.write(f"        {k}: {q(v)}\n")
    c.write('        ranks:\n')
    for r in x['ranks']:
        c.write('          - ' + q(r) + '\n')
open(ROOT + '_process/merged-contrib/composites.04.yaml', 'w', encoding='utf-8', newline='\n').write(c.getvalue())

from collections import Counter
print('callings', len(CALLINGS), Counter((c['kind'], c['breadth']) for c in CALLINGS))
print('hybrids rows', len(HYBRIDS), 'composites', len(COMPOSITES))
