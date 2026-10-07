#!/usr/bin/env python3
"""07-gen_data07.py -- generator and validator for chapter 07's data files.

Writes (paths relative to rules/):
  data/harm.yaml                      ladder, keys, warning, exits, dispositions, rests, recovery, dread, templates
  data/injuries.yaml                  wounds by harm family x site x severity, the brink wound, scars, brink marks,
                                      maims, haunts
  data/afflictions.yaml               poisons, diseases, curses (staged)
  data/last_chance.yaml               the nine options of the last-chance menu
  data/contrib/conditions.07.yaml     six carrier conditions (owner-block 07 of conditions.yaml)
  data/contrib/effects.07.yaml        seven effect definitions (owner-block 07 of effects.yaml)
  data/contrib/boundaries.07.yaml     handlers (five reserved by 00, seven added)
Then re-loads every file and checks ids against data/substrate.yaml, data/effects.yaml, data/conditions.yaml and
the contrib effect files. Run from rules/_process/simulation:  python 07-gen_data07.py
"""
import io
import os

import yaml

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
D = os.path.join(ROOT, 'data')
C = os.path.join(D, '..', '_process', 'merged-contrib')
U = {'S1': 1, 'S2': 1, 'S3': 2, 'S4': 3, 'S5': 4}


def E(effect_id, **params):
    return {'effect_id': effect_id, 'params': params}


class NoAlias(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def block(obj):
    return yaml.dump(obj, Dumper=NoAlias, sort_keys=False, allow_unicode=True, width=116, default_flow_style=None)


def line(obj):
    return '- ' + yaml.dump(obj, Dumper=NoAlias, sort_keys=False, allow_unicode=True, width=100000,
                            default_flow_style=True).strip()


def write(path, header, body):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(header.rstrip('\n') + '\n\n' + body)


# =====================================================================================================
# injuries.yaml
# =====================================================================================================
SITES = ['arm', 'leg', 'body', 'head']
NAMES = {  # family: site: [S2, S3, S4, S5]
    'cut': {
        'arm': ['gashed forearm', 'arm laid open to the muscle', 'severed tendons in the arm', 'arm cut to the bone and hanging'],
        'leg': ['slashed thigh', 'leg laid open', 'hamstrung leg', 'leg cut to the bone'],
        'body': ['cut across the ribs', 'deep cut in the side', 'belly wound', 'opened from hip to rib'],
        'head': ['cut scalp, blood in the eyes', 'face laid open', 'slashed across an eye', 'cut to the skull']},
    'pierce': {
        'arm': ['punctured forearm', 'arm run through', 'shoulder run through', 'arm pinned through the joint'],
        'leg': ['punctured calf', 'thigh run through', 'pierced knee', 'leg run through at the hip'],
        'body': ['shallow stab in the flank', 'stab wound in the side', 'pierced gut', 'pierced lung'],
        'head': ['torn ear', 'pierced cheek', 'punctured eye socket', 'pierced through jaw and throat']},
    'crush': {
        'arm': ['bruised and numbed arm', 'cracked forearm', 'broken arm', 'shattered arm'],
        'leg': ['wrenched knee', 'cracked shin', 'broken leg', 'shattered leg'],
        'body': ['bruised ribs', 'cracked ribs', 'broken ribs', 'crushed chest'],
        'head': ['ringing skull', 'concussion', 'cracked skull', 'caved skull']},
    'fire': {
        'arm': ['blistered hand', 'burned arm', 'charred hand', 'arm burned to the bone'],
        'leg': ['blistered shin', 'burned leg', 'charred foot', 'leg burned to the bone'],
        'body': ['scorched back', 'burned chest', 'deep burns across the torso', 'burned over half the body'],
        'head': ['singed face', 'burned face', 'seared eyes', 'burned to the skull']},
    'frost': {
        'arm': ['frost-nipped fingers', 'frostbitten hand', 'dead-white hand', 'arm frozen through'],
        'leg': ['frost-nipped toes', 'frostbitten foot', 'dead-white foot', 'leg frozen through'],
        'body': ['chilled to the bone', 'frost-burned chest', 'frozen lungs', 'frozen to the core'],
        'head': ['frost-nipped ears', 'frostbitten face', 'frost-blinded eyes', 'frozen through the skull']},
    'storm': {
        'arm': ['numb, twitching arm', 'lightning-scored arm', 'arm locked in spasm', 'arm cooked along the nerve'],
        'leg': ['numb, twitching leg', 'lightning-scored leg', 'leg locked in spasm', 'leg cooked along the nerve'],
        'body': ['thunder-struck chest', 'stuttering heart', 'burst vessels in the chest', 'heart stopped and restarted'],
        'head': ['flash-dazzled, ringing head', 'burst eardrum', 'lightning-blind eyes', 'seared behind the eyes']},
    'corrosion': {
        'arm': ['acid-pitted hand', 'acid-eaten forearm', 'hand eaten to the tendons', 'arm eaten to the bone'],
        'leg': ['acid-pitted shin', 'acid-eaten calf', 'foot eaten to the tendons', 'leg eaten to the bone'],
        'body': ['acid-splashed chest', 'acid-eaten flank', 'eaten through to the ribs', 'torso eaten open'],
        'head': ['acid-flecked face', 'acid-eaten cheek', 'acid in the eyes', 'face eaten away']},
    'blight': {
        'arm': ['grey, cold patch on the arm', 'withered forearm', 'dead flesh to the elbow', 'arm withered to the shoulder'],
        'leg': ['grey, cold patch on the leg', 'withered calf', 'dead flesh to the knee', 'leg withered to the hip'],
        'body': ['grey, cold patch over the ribs', 'withering in the side', 'rot in the gut', 'rot in the chest'],
        'head': ['grey patch on the cheek', 'withered face', 'clouded, dying eyes', 'rot behind the eyes']},
    'radiance': {
        'arm': ['light-scalded hand', 'light-seared arm', 'hand seared white', 'arm seared to white bone'],
        'leg': ['light-scalded shin', 'light-seared leg', 'foot seared white', 'leg seared to white bone'],
        'body': ['light-scalded chest', 'light-seared chest', 'seared through the breast', 'hollowed by light'],
        'head': ['dazzled, scalded face', 'light-seared face', 'light-blinded eyes', 'seared hollow behind the eyes']},
    'arcane': {
        'arm': ['force-bruised arm', 'force-cracked forearm', 'arm twisted out of true', 'arm unmade at the joint'],
        'leg': ['force-bruised leg', 'force-cracked shin', 'leg twisted out of true', 'leg unmade at the joint'],
        'body': ['force-bruised chest', 'ribs sprung by force', 'organs wrenched', 'torso wrenched out of true'],
        'head': ['rattled skull', 'force-struck skull', 'force-cracked skull', 'skull split by force']},
}
FAMILY_TAG = {'cut': 'harm.physical.cut', 'pierce': 'harm.physical.pierce', 'crush': 'harm.physical.crush',
              'fire': 'harm.fire', 'frost': 'harm.frost', 'storm': 'harm.storm', 'corrosion': 'harm.corrosion',
              'blight': 'harm.blight', 'radiance': 'harm.radiance', 'arcane': 'harm.arcane'}
LIGHT = {'cut': 'shallow cut', 'pierce': 'puncture', 'crush': 'bruise', 'fire': 'scorch', 'frost': 'frost-nip',
         'storm': 'jolt', 'corrosion': 'acid sting', 'blight': 'grey chill', 'radiance': 'light-scald',
         'arcane': 'force-bruise'}
SCAR = {'cut': 'a long pale scar', 'pierce': 'a puckered scar, entry and exit', 'crush': 'a bone that healed thick and crooked',
        'fire': 'a slick burn scar', 'frost': 'a dead-white, numb patch', 'storm': 'a fern-shaped scar, branching',
        'corrosion': 'pitted, shining skin', 'blight': 'a grey patch that never warms', 'radiance': 'a sun-white brand',
        'arcane': 'a patch of skin that hums in the cold'}
RECOVERY = {'S1': 'until_rest:breather', 'S2': 'until_rest:rest_long', 'S3': 'clock:clk.wound_heavy',
            'S4': 'clock:clk.wound_grievous', 'S5': 'surgery, then clock:clk.wound_catastrophic'}


def wound_entries():
    out = []
    for fam, tag in FAMILY_TAG.items():
        out.append({'id': 'inj.w.%s.light' % fam, 'name': LIGHT[fam].capitalize(), 'kind': 'wound', 'severity': 'S1',
                    'harm_tags': [tag], 'site': 'any', 'tags': [tag], 'effects': [], 'load': 1,
                    'recovery': RECOVERY['S1'], 'lifecycle': 'provisional', 'basis': ['07.2.4', '07.2.5']})
        for site in SITES:
            for i, sev in enumerate(['S2', 'S3', 'S4', 'S5']):
                eff = [E('eff.apply_condition', condition='cond.wound_%s' % site, severity=sev,
                         duration='until_cleansed', target='the bearer')]
                if sev != 'S2':
                    eff.append(E('eff.07.vitality_max_penalty', amount=-U[sev]))
                e = {'id': 'inj.w.%s.%s.%s' % (fam, site, sev.lower()), 'name': NAMES[fam][site][i].capitalize(),
                     'kind': 'wound', 'severity': sev, 'harm_tags': [tag], 'site': site, 'tags': [tag],
                     'effects': eff, 'load': U[sev], 'recovery': RECOVERY[sev]}
                if sev in ('S4', 'S5'):
                    e['leaves'] = 'inj.scar.%s' % fam
                if sev == 'S5':
                    e['becomes_maim_after'] = 'days:7 without surgery'
                e['lifecycle'] = 'provisional'
                e['basis'] = ['07.2.4', '07.2.5', 'T-07-4']
                out.append(e)
    out.append({'id': 'inj.the_brink', 'name': 'Back from the brink', 'kind': 'brink', 'severity': 'S3',
                'harm_tags': [], 'site': 'none', 'tags': [],
                'effects': [E('eff.07.vitality_max_penalty', amount=-2)], 'load': 0,
                'recovery': 'clock:clk.back_from_the_brink (one brink wound at a time, the oldest first)',
                'raises_dying_entry_step': 1, 'stacking': 'independent', 'lifecycle': 'provisional',
                'basis': ['07.2.8', 'R: https://2e.aonprd.com/Rules.aspx?ID=2319', 'DL-07-04']})
    for fam, tag in FAMILY_TAG.items():
        out.append({'id': 'inj.scar.%s' % fam, 'name': SCAR[fam].capitalize(), 'kind': 'scar', 'severity': 'S1',
                    'harm_tags': [tag], 'site': 'as the wound', 'tags': [tag], 'effects': [],
                    'recovery': 'permanent', 'visible': True, 'evidence_tags': ['copied from the felling frame (07.7.5)'],
                    'lifecycle': 'provisional', 'basis': ['07.7.2']})
    return out


def mark(id_, name, gate, up, down, text, **extra):
    e = {'id': 'inj.mark.%s' % id_, 'name': name, 'kind': 'mark', 'severity': 'S1', 'harm_tags': [],
         'gate_tags': gate, 'tags': [t for t in gate if t not in ('any', 'bargain')], 'effects': [x for x in (up, down) if x],
         'upside': up['params'].get('text') if up and 'text' in up['params'] else None, 'text': text,
         'recovery': 'permanent', 'weight': 2, 'evidence_tags': ['copied from the felling frame (07.7.5)']}
    e.pop('upside')
    e.update(extra)
    e['lifecycle'] = 'provisional'
    e['basis'] = ['07.7.3', 'C:P1', 'R6 C-R6']
    return e


def marks():
    S = lambda amount, when: E('eff.status_modifier', amount=amount, applies_when=when)
    VM = lambda n: E('eff.07.vitality_max_penalty', amount=-n)
    FR = lambda when: E('eff.apply_condition', condition='cond.frightened', severity='S1', duration='scene',
                        target='the bearer', applies_when=when, limits={'per': 'scene_end', 'uses': 1})
    return [
        mark('pale_streak', 'Pale streak', ['any'], None, None,
             'A plain mark of the brink: a streak of white hair, a stare, a scar. No mechanical weight. Always offered.',
             always_offered=True, weight=0),
        mark('deaths_debtor', "Death's debtor", ['bargain'], None, None,
             'The sign of the one you owe. Granted only by lc.bargain; visible to those who know such signs.',
             granted_by='lc.bargain', weight=0),
        mark('hard_to_kill', 'Hard to kill', ['any'],
             E('eff.check_edge', amount=2, applies_when='the dying check (07.2.7) and the Gamble (07.5.10)'), VM(1),
             '+2 edge on your dying checks and the Gamble. Maximum Vitality -1.'),
        mark('grave_cold', 'Grave-cold', ['creature.undead', 'harm.frost', 'harm.blight'],
             E('eff.hazard_step', ladder='severity', steps=-1, harm_tags=['harm.frost'], applies_when='hazard'),
             S(-1, 'Talk beats that comfort or befriend the living'),
             'Hazards of harm.frost count one severity rung lighter. -1 status on Talk that comforts or befriends.'),
        mark('ghost_sight', 'Ghost-sight', ['creature.undead.spectral', 'creature.spirit', 'harm.blight'],
             E('eff.grant_lever', type='precision', for_verbs=['verb.observe'],
               for_tags=['creature.undead.spectral', 'creature.spirit'], duration='permanent'), None,
             'A Precision lever on Observe to perceive spirits and the spectral dead. Dread threshold -1.',
             dread_threshold_delta=-1),
        mark('fire_kissed', 'Fire-kissed', ['harm.fire', 'creature.elemental.fire', 'creature.dragon'],
             E('eff.harm_reduction', amount=1, harm_tags=['harm.fire']), FR('cond.burning is first applied to the bearer in a scene'),
             'Reduce harm.fire you take by 1. The first time you are burning in a scene: frightened (S1).'),
        mark('storm_touched', 'Storm-touched', ['harm.storm', 'creature.elemental.air'],
             E('eff.check_edge', amount=1, applies_when='the tempo check (06.2.2)'),
             S(-1, 'beats with trait.action.manipulate'),
             '+1 edge on tempo checks. -1 status on beats with trait.action.manipulate (a tremor).'),
        mark('beast_wary', 'Beast-wary', ['creature.beast'],
             E('eff.grant_lever', type='precision', for_verbs=['verb.observe'], for_tags=['creature.beast'],
               duration='permanent'),
             S(-1, 'Handle beats to calm, lead or ride an animal'),
             'A Precision lever on Observe to notice beasts and their sign. -1 status on Handle with animals.'),
        mark('iron_gut', 'Iron gut', ['harm.venom', 'harm.corrosion'],
             E('eff.check_edge', amount=1, applies_when='exposure and stage checks of afflictions of kind poison'), VM(1),
             '+1 edge on exposure and stage checks against poisons. Maximum Vitality -1.'),
        mark('cold_nerve', 'Cold nerve', ['creature.folk', 'any'],
             E('eff.condition_immunity', forbid={'conditions': ['cond.frightened'], 'at_severity': 'S1'}, target='self'),
             S(-1, 'Talk beats that ask a stranger for trust'),
             'cond.frightened at S1 cannot be applied to you. -1 status on Talk that asks a stranger for trust.'),
        mark('drowned_once', 'Drowned once', ['harm.physical.asphyxia', 'terrain.water'], None,
             FR('the bearer first enters deep water in a scene'),
             'You hold your breath 6 rounds longer (07.10.4). The first time you enter deep water in a scene: frightened (S1).',
             breath_rounds_bonus=6),
        mark('sun_scarred', 'Sun-scarred', ['harm.radiance'],
             E('eff.harm_reduction', amount=1, harm_tags=['harm.radiance']), S(-1, 'sight-based Observe in dim light'),
             'Reduce harm.radiance you take by 1. -1 status on sight-based Observe in dim light.'),
        mark('witch_marked', 'Witch-marked', ['harm.arcane', 'harm.mind'],
             E('eff.check_edge', amount=1, applies_when='Endure with Resolve against effects with trait.nature.magical'), VM(1),
             '+1 edge on Endure with Resolve against magical effects. Maximum Vitality -1.'),
        mark('quick_clot', 'Quick to clot', ['harm.physical.cut', 'harm.physical.pierce'],
             E('eff.cleanse', condition_or_category='cond.bleeding', target='the bearer',
               applies_when="the bearer's turn_end", hook='on_turn_end'), VM(1),
             'cond.bleeding on you ends at the end of your turn without staunching. Maximum Vitality -1.'),
        mark('light_sleeper', 'Light sleeper', ['any'],
             E('eff.condition_immunity', forbid={'conditions': ['cond.surprised']}, target='self',
               applies_when='the bearer is resting'), None,
             'cond.surprised cannot be applied to you while you rest. Dread eases by rest only in a haven.',
             dread_rest_haven_only=True),
        mark('mended_crooked', 'Mended crooked', ['harm.physical.crush'],
             E('eff.defense_edge', amount=1, attribute='might', applies_when='Force and Grapple against the bearer'),
             S(-1, 'Exert beats to jump or run'),
             '+1 edge to your Might defense against Force and Grapple. -1 status on Exert to jump or run.'),
    ]


def maim(id_, name, site, attrs, restriction, text, offset):
    return {'id': 'inj.maim.%s' % id_, 'name': name, 'kind': 'maim', 'severity': 'S5', 'harm_tags': [], 'site': site,
            'tags': [], 'attribute_order': attrs,
            'effects': [E('eff.07.maim', attribute_order=attrs, amount=-1), restriction], 'text': text,
            'offset': offset, 'recovery': 'permanent', 'visible': True,
            'evidence_tags': ['copied from the felling frame (07.7.5)'], 'lifecycle': 'provisional',
            'basis': ['07.7.4', '00.4.3 c', 'R6 C-09 take']}


def maims():
    R = lambda **forbid: E('eff.restrict', forbid=forbid, target='the bearer', duration='permanent')
    SN = lambda fact, when: E('eff.06.grant_snag', type='precision', sign='snag', to='the bearer', fact=fact,
                              applies_when=when, duration='permanent')
    S = lambda amount, when: E('eff.status_modifier', amount=amount, applies_when=when)
    prosthetic = lambda what, made=False: [{'type': 'item', 'detail': '%s (%s): narrows the restriction, never restores the attribute' % (what, '08: base_items.yaml, item.tool.kit.prosthesis' if made else '08')},  # [revision: I-016]
                               {'type': 'recognition', 'detail': 'a calling that takes the loss as its ground (04, offered)'},
                               {'type': 'discovery', 'detail': 'a rite of regrowth, only if the region\'s canon allows one (12.16.5; default: none)'}]
    return [
        maim('lost_hand', 'Lost hand', 'arm', ['agility', 'might'],
             R(methods=['any method that needs two hands', 'a weapon of weight heavy or bow', 'a shield with a weapon']),
             'Agility -1 (else Might). No method that needs two hands.', prosthetic('a hook or a strapped shield', made=True)),
        maim('ruined_arm', 'Ruined arm', 'arm', ['might', 'agility'],
             S(-2, 'Grapple, and Might-based Force and Exert'),
             'Might -1 (else Agility). -2 status on Grapple and Might-based Force and Exert.', prosthetic('a brace', made=True)),
        maim('lost_foot', 'Lost foot', 'leg', ['agility', 'might'], E('eff.06.pace', amount=-1, applies_when='always'),
             'Agility -1 (else Might). Pace -1: each band transition costs one action more.', prosthetic('a peg or a fitted boot', made=True)),
        maim('ruined_knee', 'Ruined knee', 'leg', ['agility', 'endurance'], S(-2, 'Exert beats to jump, run or climb'),
             'Agility -1 (else Endurance). -2 status on Exert to jump, run or climb.', prosthetic('a hinged brace', made=True)),
        maim('broken_wind', 'Broken wind', 'body', ['endurance', 'might'],
             E('eff.status_modifier', amount=-2, applies_when='Endure to keep going or hold breath; breath is held half as long (07.10.4)'),
             'Endurance -1 (else Might). Breath is held half as long; -2 status on Endure to keep going.',
             prosthetic('nothing made: only a slower life')),
        maim('gut_scarred', 'Gut-scarred', 'body', ['endurance', 'resolve'],
             E('eff.status_modifier', amount=-2, applies_when='exposure and stage checks of afflictions that are eaten or drunk'),
             'Endurance -1 (else Resolve). -2 status on checks against anything eaten or drunk.',
             prosthetic('a careful diet (a lifestyle cost, 08)')),
        maim('lost_eye', 'Lost eye', 'head', ['wits', 'agility'],
             SN('maim.lost_eye', 'ranged attacks and sight-based Observe beyond band.near'),
             'Wits -1 (else Agility). A Precision snag on ranged attacks and sight-based Observe beyond band.near.',
             prosthetic('nothing restores the depth; a glass eye hides it', made=True)),
        maim('deaf_ear', 'Deaf ear', 'head', ['wits', 'presence'], SN('maim.deaf_ear', 'hearing-based Observe; noticing unseen movers'),
             'Wits -1 (else Presence). A Precision snag on hearing-based Observe.', prosthetic('an ear trumpet, out of a fight', made=True)),
        maim('broken_face', 'Broken face', 'head', ['presence', 'wits'],
             S(-1, 'Talk with those who have not met the bearer before; any disguise is G4 without a full mask'),
             'Presence -1 (else Wits). -1 status on Talk with strangers; no disguise without a full mask.',
             prosthetic('a mask (which is its own fact)')),
        maim('addled', 'Addled', 'head', ['intellect', 'wits'], S(-1, 'Recall, and beats with trait.action.concentrate'),
             'Intellect -1 (else Wits). -1 status on Recall and on beats with trait.action.concentrate.',
             prosthetic('written notes kept and consulted (a free activity that takes an interval)')),
        maim('hollowed', 'Hollowed', 'spirit', ['resolve', 'presence'],
             E('eff.status_modifier', amount=-1, applies_when='dread checks (07.11.2)'),
             'Resolve -1 (else Presence). -1 status on dread checks. Chosen when the worst fresh wound is of harm.blight, harm.arcane, harm.radiance or harm.mind.',
             prosthetic('a keeper, an oath or a bond that holds you (04, 15)')),
    ]


def haunt(id_, name, gate, effects, text, **extra):
    e = {'id': 'inj.haunt.%s' % id_, 'name': name, 'kind': 'haunt', 'severity': 'S3', 'harm_tags': ['harm.mind.strain'],
         'gate_tags': gate, 'tags': ['harm.mind.strain'], 'effects': effects, 'text': text, 'recovery': 'permanent',
         'weight': 2, 'evidence_tags': ['copied from the breaking event (07.7.5)']}
    e.update(extra)
    e['lifecycle'] = 'provisional'
    e['basis'] = ['07.11.4', '07.11.5', 'R6 C-R7', 'R: https://bladesinthedark.com/consequences-harm']
    return e


def haunts():
    S = lambda amount, when: E('eff.status_modifier', amount=amount, applies_when=when)
    return [
        haunt('night_terrors', 'Night terrors', ['any'],
              [E('eff.07.rest_cap', rests=['rest_long'], quality='partial', applies_when='the rest site is not a haven')],
              'Long rests outside a haven are at best partial.'),
        haunt('dread_of', 'A dread of what broke you', ['any'],
              [E('eff.apply_condition', condition='cond.frightened', severity='S1', duration='scene', target='the bearer',
                 applies_when='the bearer first perceives a creature or hazard carrying the recorded tag in a scene',
                 limits={'per': 'scene_end', 'uses': 1})],
              'Records the most specific creature or harm tag of the breaking source. Frightened (S1) at first sight of its kind each scene.',
              records='the breaking source tag'),
        haunt('the_shakes', 'The shakes', ['any'], [S(-1, 'beats with trait.action.manipulate while the bearer is shaken (07.11.3)')],
              '-1 status on beats with trait.action.manipulate while shaken.'),
        haunt('cold', 'Gone cold', ['creature.folk', 'any'],
              [E('eff.condition_immunity', forbid={'conditions': ['cond.frightened'], 'at_severity': 'S1'}, target='self'),
               S(-1, 'Talk beats that comfort or befriend')],
              'cond.frightened at S1 cannot be applied to you. -1 status on Talk that comforts or befriends.'),
        haunt('flinch', 'Flinching', ['any'], [S(-2, 'the tempo check (06.2.2)')], '-2 status on tempo checks.'),
        haunt('joyless', 'Joyless', ['any'], [], 'Solace eases 1 less dread (07.11.7). Dread threshold +1.',
              dread_threshold_delta=1, solace_delta=-1),
        haunt('the_stare', 'The stare', ['any'],
              [E('eff.check_edge', amount=1, applies_when='Talk beats that intimidate'), S(-1, 'Talk beats that persuade')],
              '+1 edge on Talk that intimidates. -1 status on Talk that persuades.'),
        haunt('obsession', 'Obsession', ['any'],
              [E('eff.07.dread', units=1, check=False, hook='on_boundary', boundary='week',
                 applies_when='the obsession thread gained no progress this week')],
              'Opens a thread toward the thing that broke you (11). Dread +1 at each week in which the thread went unpursued.',
              opens='thread'),
    ]


INJ_HEADER = """# data/injuries.yaml
# Purpose: every wound, the brink wound, scars, brink marks, maims and haunts (07.2.4-07.2.5, 07.2.8, 07.7, 07.11.5).
#   kind: wound  - taken while Staggered or Dying; keyed by harm family x site x severity (PR-07-2). Effects go through
#                  the four carrier conditions cond.wound_<site> (data/conditions.yaml owner-block 07), which hold the
#                  site's status penalty and restrictions by severity (T-07-4).
#   kind: brink  - inj.the_brink, taken each time a character is stabilized from Dying (07.2.8).
#   kind: scar   - left when a Grievous or Catastrophic wound heals (07.7.2). No modifier.
#   kind: mark   - brink marks: the player picks one of three drawn by gate_tags, or inj.mark.pale_streak (07.7.3).
#   kind: maim   - a permanent -1 to the first eligible attribute in attribute_order, plus a restriction (07.7.4).
#   kind: haunt  - taken at a dread break; at most three (07.11.4-07.11.6).
# Owner: 07-harm-recovery-death. Schema: data/SCHEMAS.md#injuriesyaml (Injury: id, severity, harm_tags, effects,
#   recovery, evidence_tags). Optional fields added by ch.07 (documented in 07 Tables): kind, site, load, leaves,
#   becomes_maim_after, gate_tags, weight, text, attribute_order, offset, dread_threshold_delta, breath_rounds_bonus,
#   dread_rest_haven_only, solace_delta, always_offered, granted_by, records, opens, visible, raises_dying_entry_step.
# Site of a wound: the called shot's site, else the attack's listed site, else tbl.wound_site (harm.yaml#tables).
# Family of a wound: the first harm tag of the event, matched with cascade to: harm.physical.cut | .pierce | .crush,
#   harm.fire, harm.frost, harm.storm, harm.corrosion, harm.blight, harm.radiance, harm.arcane. Harm with only
#   harm.venom, harm.mind or harm.physical.asphyxia tags is internal (periodic): it adds wound load and leaves no
#   record (07.2.4).
# Generated and validated by rules/_process/simulation/07-gen_data07.py.
# Basis: [07.2.4] [07.2.5] [07.7] [07.11.5] [R4 9 07 item 3] [R6 C-R6] [00.4.3 c] [DL-07-03] [DL-07-10]

schema_version: 1
injuries:"""

# =====================================================================================================
# contrib/conditions.07.yaml
# =====================================================================================================


def cond(id_, name, tags, category, modifies, intent, *, stacking='replace_stronger', max_stacks=1, duration='until_cleansed',
         cleanse=None, periodic=None, not_imply=None, basis=None, sev='S2'):
    return {'id': id_, 'name': name, 'tags': tags, 'category': category, 'severity': sev, 'severity_variable': True,
            'stacking': stacking, 'max_stacks': max_stacks, 'escalates_to': None, 'duration': duration, 'decay': [],
            'cleanse': cleanse or [], 'exclusion_group': None, 'priority_rank': 0, 'neutralizes': [], 'diminishing': None,
            'modifies': modifies, 'periodic': periodic or [], 'on_apply': [], 'on_remove': [], 'visible': True,
            'narration_may_not_imply': not_imply or ['a wound of another site or severity than the record',
                                                     'healing that the recovery clock has not delivered'],
            'intent': intent, 'lifecycle': 'provisional', 'basis': basis or ['00.9', '07.2.5', 'T-07-4', 'DL-07-10']}


def wound_conditions():
    S = lambda amount, sev, when: E('eff.status_modifier', amount=amount, applies_when='severity %s; %s' % (sev, when))
    R = lambda sev, **forbid: E('eff.restrict', forbid=forbid, target='the bearer', duration='while the condition lasts',
                                applies_when='severity %s' % sev)
    heal = [{'means': "the wound's recovery (07.8.5-07.8.7): the carrier ends when the wound record heals", 'requires': None,
             'check': None}]
    arm_when = 'attack-trait and manipulate-trait beats with that arm, Grapple, Might-based Force and Exert'
    leg_when = 'Move, Evade, and Exert or Sneak carried by the legs'
    body_when = 'Endure with Endurance, and sustained Exert'
    head_when = 'checks with Wits or Intellect (including tempo), and beats with trait.action.concentrate'
    return [
        cond('cond.wound_arm', 'Wounded arm', ['harm.physical'], 'physical',
             [S(-1, 'is S2', arm_when), S(-2, 'in [S3, S4]', arm_when), S(-3, 'is S5', arm_when),
              R('in [S3, S4, S5]', methods=['a weapon of weight heavy', 'a bow']),
              R('in [S4, S5]', methods=['anything held in that hand: a shield, a second weapon, a two-handed method']),
              R('is S5', methods=['Exert to climb or swim without help'])],
             'a wound of the arm or hand; penalty and restrictions by severity (T-07-4)', cleanse=heal),
        cond('cond.wound_leg', 'Wounded leg', ['harm.physical'], 'physical',
             [S(-1, 'is S2', leg_when), S(-2, 'in [S3, S4]', leg_when), S(-3, 'is S5', leg_when),
              E('eff.06.pace', amount=-1, applies_when='severity in [S3, S4, S5]'),
              R('in [S4, S5]', methods=['Exert to jump or run']),
              E('eff.restrict', forbid={'methods': ['standing unsupported: the bearer is cond.prone unless it leans on a staff, a wall or a companion; Move is one band a turn at most']},
                target='the bearer', duration='while the condition lasts', applies_when='severity is S5')],
             'a wound of the leg or foot; penalty and restrictions by severity (T-07-4)', cleanse=heal),
        cond('cond.wound_body', 'Wounded body', ['harm.physical'], 'physical',
             [S(-1, 'is S2', body_when), S(-2, 'in [S3, S4]', body_when), S(-3, 'is S5', body_when),
              E('eff.07.rest_cap', rests=['breather'], quality='interrupted', applies_when='severity in [S3, S4, S5]'),
              E('eff.apply_condition', condition='cond.weakened', severity='S1', duration='while the condition lasts',
                target='the bearer', applies_when='severity in [S4, S5]'),
              E('eff.06.fewer_actions', actions_delta=-1, minimum_actions=1, reactions_delta=0, applies_when='severity is S5')],
             'a wound of the trunk; penalty and restrictions by severity (T-07-4)', cleanse=heal),
        cond('cond.wound_head', 'Wounded head', ['harm.physical'], 'physical',
             [S(-1, 'is S2', head_when), S(-2, 'in [S3, S4]', head_when), S(-3, 'is S5', head_when),
              E('eff.06.grant_snag', type='precision', sign='snag', to='the bearer', fact='wound.head.blurred',
                applies_when='severity in [S3, S4, S5]; ranged attacks and sight-based Observe beyond band.near',
                duration='while the condition lasts'),
              E('eff.restrict', forbid={'senses': ['one sense, as the wound entry names: sight on one side, or hearing']},
                target='the bearer', duration='while the condition lasts', applies_when='severity in [S4, S5]'),
              E('eff.06.fewer_actions', actions_delta=-1, minimum_actions=1, reactions_delta=0, applies_when='severity is S5')],
             'a wound of the head or face; penalty and restrictions by severity (T-07-4)', cleanse=heal),
        cond('cond.diseased', 'Diseased', ['harm.blight.disease'], 'affliction_stage',
             [E('eff.status_modifier', amount=-1, applies_when='severity is S1'),
              E('eff.status_modifier', amount=-2, applies_when='severity in [S2, S3]'),
              E('eff.status_modifier', amount=-3, applies_when='severity in [S4, S5]'),
              E('eff.07.rest_cap', rests=['rest_short', 'rest_long'], quality='partial', applies_when='severity in [S2, S3, S4, S5]')],
             'the carrier for staged diseases (07.9.8); the same status numbers as cond.poisoned', sev='S1',
             cleanse=[{'means': "the affliction's stage table or a cure (07.9.6)", 'requires': None, 'check': None}],
             not_imply=['a stage other than the one held', 'a cure that no check, remedy or treatment delivered'],
             basis=['00.9.4', '07.9.1', '07.9.8', 'R5 HR-08']),
        cond('cond.cursed', 'Cursed', ['trait.nature.magical'], 'magical',
             [E('eff.status_modifier', amount=-1, applies_when='severity is S1; only the checks the curse entry names'),
              E('eff.status_modifier', amount=-2, applies_when='severity in [S2, S3]; only the checks the curse entry names'),
              E('eff.status_modifier', amount=-3, applies_when='severity in [S4, S5]; only the checks the curse entry names')],
             'the carrier for staged curses (07.9.7); one instance per curse, up to three curses', sev='S1',
             stacking='independent', max_stacks=3,
             cleanse=[{'means': "the curse's lift (07.9.7)", 'requires': 'the sealed lift fact, once learned', 'check': None},
                      {'means': 'eff.05.end_working: one stage down', 'requires': 'a working that ends magical effects',
                       'check': {'verb': 'by the working', 'dc_tier': "the curse's virulence"}}],
             not_imply=['a stage other than the one held', 'that the curse is lifted before its lift fact is written'],
             basis=['00.9.4', '07.9.7', 'R5 HR-08']),
    ]


COND_HEADER = """# data/contrib/conditions.07.yaml
# Purpose: ch.07's owner-block for data/conditions.yaml (T-00-19: "conditions: 07 (affliction carriers)"). Six
#   carriers: four wound carriers by site (the mechanical face of data/injuries.yaml wounds, T-07-4) and two
#   affliction carriers beside ch.06's cond.poisoned. Harm states (staggered, dying, dead) are NOT conditions (00.9.4).
# Confirmed, not redefined: cond.exhausted (ch.06: intensify, 3 stacks, -1 per stack, slowed at 3; 07.8.10) and
#   cond.poisoned (ch.06: -1 / -2 / -3 by severity; the carrier of every affliction of kind poison).
# Owner: 07-harm-recovery-death. Schema: data/SCHEMAS.md#conditionsyaml (Condition, 00.9.1); optional field `intent`
#   as ch.06 uses it. Generated and validated by rules/_process/simulation/07-gen_data07.py.
# Basis: [00.9] [06.7.1] [07.2.5] [07.9.1] [DL-07-10]

schema_version: 1
blocks:
- owner: '07'
  entries:"""

# =====================================================================================================
# contrib/effects.07.yaml
# =====================================================================================================
EFFECTS = [
    {'id': 'eff.07.vitality_max_penalty', 'op': 'modify', 'quantity': 'vitality_max', 'family': 'adjust', 'regime': 'additive',
     'params': {'amount': '-4..-1'},
     'text': '{amount} maximum Vitality (never below half of base plus band growth, 07.1.2).',
     'why_not_core': 'eff.max_modify takes amount 1..4 only; wounds, brink and some marks lower the maximum',
     'lifecycle': 'provisional', 'basis': ['07.1.2', '07.2.5', '07.2.8', 'DL-07-16']},
    {'id': 'eff.07.dread', 'op': 'resource', 'regime': 'independent_trigger', 'hook': 'per source (on_dying, on_boundary, on_condition_applied, or the calling rule)',
     'params': {'units': '1..4 | U(severity)', 'severity': 'S1..S5 | null', 'check': 'bool (true: a dread check at the severity, 07.11.2; false: flat)',
                'target': 'target_rule'},
     'text': '{target} gains {units} dread (after a dread check when {check}).',
     'why_not_core': "eff.drain's quantity list is focus | supply; dread is ch.07's own quantity",
     'lifecycle': 'provisional', 'basis': ['07.11.1', '07.11.2', 'DL-07-16']},
    {'id': 'eff.07.maim', 'op': 'set_fact', 'regime': 'independent_trigger',
     'params': {'attribute_order': '[attr_id, attr_id]', 'amount': '-1'},
     'text': 'Permanently lowers the first attribute in {attribute_order} not maimed before and above -2 by 1 (00.4.3 c).',
     'why_not_core': 'attributes are not quantities of the evaluation pass (T-00-13) and no effect may change them; a maim is the one write 00.4.3 c allows, expressed as a recorded fact',
     'lifecycle': 'provisional', 'basis': ['00.4.3 c', '07.7.4', 'DL-07-16']},
    {'id': 'eff.07.stabilize', 'op': 'set_fact', 'regime': 'independent_trigger',
     'params': {'target': 'one Dying being', 'brink_wound': 'bool (default true; false for lc.reprieve and a critical Gamble)'},
     'text': '{target} is stabilized: Dying ends, the harm state is Staggered, on_stabilize fires (07.2.8).',
     'why_not_core': 'harm states are not conditions (00.9.4), so eff.cleanse cannot end Dying',
     'lifecycle': 'provisional', 'basis': ['07.2.8', '05 ab.breath_of_life', 'DL-07-16']},
    {'id': 'eff.07.affliction_shift', 'op': 'remove_condition', 'regime': 'independent_trigger',
     'params': {'affliction': 'aff.* | kind | family tag', 'stages': '-2..-1', 'target': 'target_rule'},
     'text': "Lowers {affliction} on {target} by {stages} stage(s); at stage 0 it is cured and its carrier ends.",
     'why_not_core': 'eff.cleanse removes a whole condition; remedies and treatment move an affliction along its stages',
     'lifecycle': 'provisional', 'basis': ['07.9.6', 'DL-07-16']},
    {'id': 'eff.07.rest_cap', 'op': 'restrict', 'regime': 'additive',
     'params': {'rests': '[breather | rest_short | rest_long]', 'quality': 'partial | interrupted', 'applies_when': 'expr'},
     'text': 'The named rests are at best {quality} for the bearer {applies_when}.',
     'why_not_core': 'eff.restrict forbids verbs, methods, senses and licenses; rest quality is none of those',
     'lifecycle': 'provisional', 'basis': ['07.8.4', 'DL-07-16']},
    {'id': 'eff.07.block_restore', 'op': 'prevent', 'regime': 'additive',
     'params': {'event_kind': 'a Vitality-restoring effect on the bearer', 'source_filter': 'trait.nature.magical | rest | any',
                'amount': 'all | half'},
     'text': '{source_filter} restoring of Vitality to the bearer is reduced by {amount}.',
     'why_not_core': 'eff.prevent_hit negates hits only; three curses (deaths_debt, grave_bound, wasting) close a channel of recovery',
     'lifecycle': 'provisional', 'basis': ['07.9.7', 'DL-07-16']},
]
EFF_HEADER = """# data/contrib/effects.07.yaml
# Purpose: ch.07's owner-block for data/effects.yaml. Seven definitions, each added because no core effect with
#   parameters expresses the mechanic (PR-00-8), each using one of the 20 closed operations and one regime.
#   Everything else in harm.yaml, injuries.yaml, afflictions.yaml and last_chance.yaml references the core library
#   and ch.06's eff.06.* (fewer_actions, pace, grant_snag, internal_harm).
# Owner: 07-harm-recovery-death. Schema: data/SCHEMAS.md#effectsyaml. Decision: DL-07-16.

schema_version: 1
blocks:
- owner: '07'
  entries:"""

# =====================================================================================================
# contrib/boundaries.07.yaml
# =====================================================================================================
HANDLERS = [
    ('h.07.after_conflict', 'conflict_end', 3, False,
     'run the defeat disposition if the PC is Down, yielded or captured (PR-07-7); if anyone is Dying keep time in rounds until the ladder resolves; write setback facts',
     '07.6.1; PR-07-7', 'reserved by 00; defined'),
    ('h.07.affliction_onset', 'interval', 2, False,
     'end onsets that have run out (stage 1 begins); run stage checks of afflictions on the interval cadence (PR-07-9)',
     '07.9.3; PR-07-9', 'reserved by 00; defined'),
    ('h.07.fatigue', 'watch', 4, False,
     'advance watches_awake; apply cond.exhausted at 4, 6, 8; S2 harm each watch beyond 8 (lethal: false)',
     '07.8.10', 'reserved by 00; defined'),
    ('h.07.natural_recovery', 'day', 3, False,
     'tick every recovery clock from rested_today / treated_today / bed_rest_today (T-07-15); heal completed wounds; write scars; turn an unoperated Catastrophic wound into a maim at day 7; clear the three flags',
     '07.8.7; PR-07-10', 'reserved by 00; defined'),
    ('h.07.rest_recovery', ['breather', 'rest_short', 'rest_long'], 3, False,
     'restore Vitality by rest type and quality (T-07-14); clear wound load; heal Light and Moderate wounds; remove exhausted stacks; ease dread; set rested_today. Reads quality from the boundary payload; requested to run before h.05.focus_recover and h.05.rest_recharge',
     '07.8.5; PR-07-8', 'reserved by 00; defined'),
    ('h.07.dying_check', ['turn_end', 'round'], 2, False,
     "turn_end: the dying check of a Dying character whose turn it is (07.2.7); round: the same for a Dying character outside a conflict, and +1 on every clk.bleeding_out",
     '07.2.7; 07.12.1; PR-07-3', 'added'),
    ('h.07.lethal_scan', ['scene_start', 'conflict_start'], 7, False,
     'evaluate the lethal-warning rows (07.3.3) and the danger notice (07.3.8) against the framed scene; raise trg.lethal_warning / trg.danger_notice. The same rows are also evaluated whenever their state changes',
     '07.3.3; 07.3.8; PR-07-4', 'added'),
    ('h.07.load_clear', 'scene_end', 1, False,
     'clear wound_load; end lethal contexts whose `ends` is scene_end; heal Light wounds',
     '07.2.6; 07.3.5', 'added'),
    ('h.07.affliction_day', 'day', 2, False,
     'stage checks of afflictions on the day cadence; stage harm; contagion exposures; the 7-day wound_rot exposure of an unticked Grievous wound',
     '07.9.3; 07.9.8; PR-07-9', 'added'),
    ('h.07.curse_cycle', 'week', 2, False,
     'stage checks of curses on the week cadence; haunt effects keyed to the week; the weekly captivity dread check',
     '07.9.7; 07.11.2', 'added'),
    ('h.07.vitality_max', ['reflection', 'season'], 9, False,
     'recompute maximum Vitality from base, power_band, effects and wound penalties (07.1.2); raise current by the same amount when power_band rose',
     '07.1.2; DL-00-04', 'added'),
    ('h.07.career_end', 'scene_end', 8, False,
     "if career_end is written (the fourth break, 07.11.6) hand the character to ch.11's retirement procedure",
     '07.11.6', 'added'),
]
BND_HEADER = """# data/contrib/boundaries.07.yaml
# Purpose: ch.07's owner-block for data/boundaries.yaml. The five handlers 00 reserved for ch.07 are DEFINED in 07
#   (rule ids below) and restated here with their rule ids; seven handlers are added.
# Ordering note: 00.7.5 orders handlers within a phase by owner chapter number, which would run ch.05's rest handlers
#   before h.07.rest_recovery. Rest QUALITY is computed when ch.07 marks the rest boundary and travels in the boundary
#   payload (07.8.1), so no handler depends on the order; ch.05 asked that h.07.rest_recovery run first, which is
#   recorded as `before` below and filed as an Interface request to 00 (a within-phase `before` key).
# Owner: 07-harm-recovery-death. Schema: data/SCHEMAS.md#boundariesyaml. Phases per 00.7.5.

schema_version: 1
blocks:
- owner: '07'
  handlers:"""

# =====================================================================================================
# afflictions.yaml
# =====================================================================================================


def stage(n, condition, sev, effects=(), harm=None, text=''):
    s = {'stage': n, 'condition': condition, 'severity': sev, 'duration': None, 'check': None,
         'on_fail': 'rise one stage (critical failure: two)', 'on_success': 'fall one stage (critical success: two)'}
    if harm:
        s['harm'] = {'severity': harm, 'no_reduction': True, 'periodic': True, 'at': 'each stage check'}
    s['effects'] = list(effects)
    s['text'] = text
    return s


def aff(id_, name, kind, harm_tags, delivery, virulence, onset, cadence, stages, cure, *, attribute='endurance',
        max_checks=None, lethal=False, warn_stage=None, terminal=None, contagious=False, lift=None, notes=None, basis=None,
        checks=True):
    for s in stages:
        s['duration'] = cadence
        s['check'] = {'verb': 'verb.endure', 'attribute': attribute, 'dc_tier': virulence} if checks else None
        if not checks:
            s['on_fail'] = s['on_success'] = 'no check: moves only by its trigger'
    e = {'id': id_, 'name': name, 'kind': kind, 'tags': harm_tags, 'harm_tags': harm_tags, 'delivery': delivery,
         'virulence': virulence, 'onset': onset, 'cadence': cadence, 'max_checks': max_checks, 'lethal': lethal,
         'warn_stage': warn_stage, 'contagious': contagious, 'stages': stages,
         'terminal': terminal, 'cure': cure, 'lift': lift}
    if notes:
        e['notes'] = notes
    e['lifecycle'] = 'provisional'
    e['basis'] = basis or ['07.9', 'R5 HR-08', 'R: https://2e.aonprd.com/Rules.aspx?ID=2319']
    return e


def afflictions():
    AC = lambda c, sev='S2', dur='while the stage lasts': E('eff.apply_condition', condition=c, severity=sev, duration=dur, target='the bearer')
    VM = lambda n: E('eff.07.vitality_max_penalty', amount=-n)
    P, DIS, CUR = 'cond.poisoned', 'cond.diseased', 'cond.cursed'
    antidote = ['a general antidote (item.consumable.remedy): one stage down', 'Treat (07.8.8)', 'eff.cleanse naming cond.poisoned (07.9.6)']
    return [
        aff('aff.adder_venom', 'Adder venom', 'poison', ['harm.venom.poison'], ['wound'], 'moderate', 'rounds:1', 'rounds:1',
            [stage(1, P, 'S1', harm='S1', text='A burning ache spreads from the bite.'),
             stage(2, P, 'S2', harm='S2', text='The limb swells; the head swims.'),
             stage(3, P, 'S3', [AC('cond.weakened', 'S1')], harm='S2', text='Strength drains out of the grip.')],
            antidote + ['runs its course after 4 checks'], max_checks=4,
            terminal='holds at stage 3'),
        aff('aff.widow_venom', "Weaver's venom", 'poison', ['harm.venom.poison'], ['wound'], 'hard', 'intervals:1', 'intervals:1',
            [stage(1, P, 'S1', [AC('cond.slowed')], text='The legs grow heavy.'),
             stage(2, P, 'S2', [AC('cond.slowed'), AC('cond.weakened', 'S2')], text='The hands will not close.'),
             stage(3, P, 'S3', [AC('cond.restrained', 'S3'), E('eff.06.fewer_actions', actions_delta=-2, minimum_actions=1, reactions_delta=-1)],
                   text='Awake and unable to move: what great spiders want of their prey.')],
            antidote + ['runs its course after 6 checks'], max_checks=6, terminal='holds at stage 3',
            notes='The venom of creatures whose disposition is drag_to_lair.'),
        aff('aff.nightshade', 'Nightshade', 'poison', ['harm.venom.poison'], ['ingested'], 'hard', 'intervals:1', 'intervals:1',
            [stage(1, P, 'S2', [AC('cond.distracted', 'S1')], text='Dry mouth, wide pupils, a racing heart.'),
             stage(2, P, 'S3', harm='S2', text='Visions; the heart stumbles.'),
             stage(3, P, 'S4', harm='S3', text='Convulsions.')],
            ['a specific remedy (charcoal and mustard-water, taken within the first two stages): two stages down'] + antidote
            + ['runs its course after 8 checks'], max_checks=8, lethal=True, warn_stage=2,
            terminal='S3 harm at each check while stage 3 holds'),
        aff('aff.drowse', 'Drowse', 'poison', ['harm.venom.poison'], ['ingested', 'inhaled'], 'moderate', 'intervals:1', 'intervals:1',
            [stage(1, P, 'S1', [AC('cond.distracted', 'S1')], text='Eyelids like lead.'),
             stage(2, P, 'S2', [AC('cond.unconscious', 'S4', 'until woken by harm or by one action of another, then stage 1')],
                   text='Asleep.')],
            ['being woken (stage 2 to stage 1)', 'runs its course after 3 checks'] + antidote, max_checks=3,
            terminal='holds at stage 2', notes="The carrier for ab.slow_draught and any sleeping draught (05's request)."),
        aff('aff.wyvern_venom', 'Wyvern venom', 'poison', ['harm.venom.poison'], ['wound'], 'very_hard', 'rounds:1', 'rounds:1',
            [stage(1, P, 'S2', harm='S2', text='Fire in the blood.'),
             stage(2, P, 'S3', harm='S3', text='The heart labors.'),
             stage(3, P, 'S4', [AC('cond.slowed')], harm='S3', text='The limbs stiffen.')],
            ['a specific remedy (wyvern-bane, 08): two stages down'] + antidote + ['runs its course after 6 checks'],
            max_checks=6, lethal=True, warn_stage=1, terminal='S3 harm at each check while stage 3 holds',
            notes='A round-cadence killer: the warning fires at stage 1, and its bearer is a T4 foe whose severity row has usually fired already.'),
        aff('aff.ghoul_ichor', 'Ghoul ichor', 'poison', ['harm.venom.poison', 'harm.blight.necrotic'], ['wound'], 'moderate',
            'rounds:1', 'rounds:1',
            [stage(1, P, 'S1', [AC('cond.slowed')], text='Cold stiffness in the wound.'),
             stage(2, P, 'S2', [AC('cond.restrained', 'S3', 'rounds:1')], text='Rigid for a breath (a control condition: 06.7.4 applies).')],
            antidote + ['runs its course after 3 checks'], max_checks=3, terminal='holds at stage 2'),
        aff('aff.blackroot', 'Blackroot', 'poison', ['harm.venom.poison'], ['wound', 'ingested'], 'hard', 'intervals:1', 'intervals:1',
            [stage(1, P, 'S2', text='A numb line creeping from the cut.'),
             stage(2, P, 'S3', harm='S2', text='Black veins; cold sweat.'),
             stage(3, P, 'S4', harm='S3', text='The breath comes short.')],
            ['a specific remedy (bitterwort draught, 08): two stages down'] + antidote + ['runs its course after 6 checks'],
            max_checks=6, lethal=True, warn_stage=2, terminal='S3 harm at each check while stage 3 holds',
            notes="An assassin's blade venom."),
        aff('aff.grey_spore', 'Grey spore', 'poison', ['harm.venom.gas'], ['inhaled'], 'moderate', 'rounds:2', 'intervals:1',
            [stage(1, P, 'S1', [AC('cond.distracted', 'S1')], text='A cough that will not clear.'),
             stage(2, P, 'S2', [AC('cond.exhausted', 'S2', 'until_rest:rest_long')], text='Lungs like wet wool.')],
            ['clean air for an interval: one stage down'] + antidote + ['runs its course after 4 checks'], max_checks=4,
            terminal='holds at stage 2'),
        aff('aff.marsh_fever', 'Marsh fever', 'disease', ['harm.blight.disease'], ['a wetland hazard (10)', 'insect bites'], 'moderate',
            'days:2', 'days:1',
            [stage(1, DIS, 'S1', text='Chills at dusk.'),
             stage(2, DIS, 'S2', [AC('cond.exhausted', 'S2', 'while the stage lasts (this stack cannot be removed)')], text='Fever and shaking.'),
             stage(3, DIS, 'S3', [AC('cond.exhausted', 'S2', 'while the stage lasts')], harm='S2', text='Burning up; the mind wanders.'),
             stage(4, DIS, 'S4', [AC('cond.exhausted', 'S2', 'while the stage lasts')], harm='S3', text='Delirium.')],
            ['a specific remedy (feverbark tea, 08): two stages down', 'Treat (07.8.8)', 'a week of convalescence: one stage down (07.8.11)'],
            lethal=True, warn_stage=3, terminal='S3 harm at each check while stage 4 holds'),
        aff('aff.wound_rot', 'Wound rot', 'disease', ['harm.blight.disease'], ['a Grievous wound untended for 7 days', 'a wound taken in filth'],
            'hard', 'days:2', 'days:1',
            [stage(1, DIS, 'S2', text='Heat and a smell. The wound it sits in stops healing: its recovery clock does not tick.'),
             stage(2, DIS, 'S3', harm='S2', text='Red lines running from the wound.'),
             stage(3, DIS, 'S4', harm='S3', text='Black at the edges.')],
            ['Treat at Hard, reach 2 or more (cutting it clean): two stages down', 'a general remedy (a poultice): one stage down',
             'a week of convalescence with treatment: one stage down'],
            lethal=True, warn_stage=2,
            terminal='S3 harm at each check while stage 3 holds, and the wound it sits in becomes one severity rung heavier (to S5 at most)'),
        aff('aff.red_flux', 'Red flux', 'disease', ['harm.blight.disease'], ['bad water', 'spoiled food'], 'moderate', 'days:1', 'days:1',
            [stage(1, DIS, 'S1', [E('eff.status_modifier', amount=0, applies_when='supply use of water is doubled (10)')], text='Cramps.'),
             stage(2, DIS, 'S2', [AC('cond.exhausted', 'S2', 'while the stage lasts')], text='Cannot keep water down.'),
             stage(3, DIS, 'S3', [AC('cond.exhausted', 'S2', 'while the stage lasts'), AC('cond.weakened', 'S1')], text='Wrung out.')],
            ['clean water and rest: a full-quality long rest lowers it one stage', 'a general remedy: one stage down',
             'runs its course after 7 checks'], max_checks=7, contagious=True, terminal='holds at stage 3'),
        aff('aff.grave_chill', 'Grave-chill', 'disease', ['harm.blight.necrotic'], ['the touch of the walking dead', 'a night in a barrow'],
            'hard', 'watches:1', 'days:1',
            [stage(1, DIS, 'S1', text='A cold that fire does not reach.'),
             stage(2, DIS, 'S2', [VM(2)], text='Grey at the lips.'),
             stage(3, DIS, 'S3', [VM(4), E('eff.07.dread', units=1, check=False, hook='on_boundary', boundary='day')],
                   text='The dead feel nearer than the living.')],
            ['a long rest at a consecrated or tended place (the region\'s seed, 12.16.9): one stage down', 'a working of deed.divine.healing that names it',
             'medicine does not touch it'], terminal='holds at stage 3'),
        aff('aff.rat_plague', 'Rat plague', 'disease', ['harm.blight.disease'], ['vermin bites', 'close contact with a bearer'], 'hard',
            'days:3', 'days:1',
            [stage(1, DIS, 'S1', text='Headache; swollen glands.'),
             stage(2, DIS, 'S2', [AC('cond.exhausted', 'S2', 'while the stage lasts')], text='Fever; black swellings.'),
             stage(3, DIS, 'S3', [AC('cond.exhausted', 'S2', 'while the stage lasts')], harm='S2', text='The swellings burst.'),
             stage(4, DIS, 'S4', [AC('cond.exhausted', 'S2', 'while the stage lasts')], harm='S3', text='Bleeding under the skin.')],
            ['Treat (07.8.8)', 'a week of convalescence with treatment: one stage down', 'a specific remedy, if the region\'s seed or setting has one'],
            lethal=True, warn_stage=3, contagious=True, terminal='S3 harm at each check while stage 4 holds'),
        aff('aff.lockjaw', 'Lockjaw', 'disease', ['harm.blight.disease'], ['a deep puncture from rusted or fouled metal'], 'hard',
            'days:4', 'days:1',
            [stage(1, DIS, 'S1', [E('eff.status_modifier', amount=-1, applies_when='beats with trait.action.speech')], text='A stiff jaw.'),
             stage(2, DIS, 'S2', [AC('cond.silenced'), AC('cond.slowed')], text='The jaw locks; the neck arches.'),
             stage(3, DIS, 'S3', [AC('cond.silenced'), AC('cond.restrained', 'S3')], harm='S2', text='Spasms that bend the spine.')],
            ['Treat at Hard (cleaning the wound deep) within the onset: prevents it', 'Treat (07.8.8)', 'a working that names it'],
            lethal=True, warn_stage=2, terminal='S3 harm at each check while stage 3 holds'),
        aff('aff.deaths_debt', "Death's debt", 'curse', ['trait.nature.magical'], ['lc.bargain (07.5.5)'], 'legendary', 'rounds:0', 'trigger',
            [stage(1, CUR, 'S1', [E('eff.07.rest_cap', rests=['rest_long'], quality='partial', applies_when='for easing dread only: rests ease no dread')],
                   text="The debtor's sign shows. While the debt is honored it stays here."),
             stage(2, CUR, 'S2', [E('eff.07.block_restore', event_kind='a Vitality-restoring effect on the bearer', source_filter='trait.nature.magical', amount='all')],
                   text='Healing magic slides off you.'),
             stage(3, CUR, 'S3', [VM(4), E('eff.07.rest_cap', rests=['rest_long'], quality='partial', applies_when='always')],
                   text='You are being called in.'),
             stage(4, CUR, 'S4', text='Forfeit: at the next scene_start you stand at the Threshold again, without the bargain (07.5.5).')],
            ['the lift only'], attribute='resolve', lethal=True, warn_stage=3, checks=False,
            terminal='stage 4 is the forfeit', lift='the vow the bargainer asked is fulfilled (11)',
            notes='Advances one stage each time clk.deaths_debt completes unpaid; no stage checks. eff.05.end_working does not touch it.',
            basis=['07.5.5', '07.9.7', 'R6 C-14']),
        aff('aff.evil_eye', 'The evil eye', 'curse', ['trait.nature.magical'], ['a hex (rit.lay_curse, a hedge-witch, a dying breath)'], 'moderate',
            'days:1', 'days:1',
            [stage(1, CUR, 'S1', [E('eff.06.grant_snag', type='precision', sign='snag', to='the bearer', fact='curse.evil_eye',
                                    applies_when="the bearer's first rolled beat of each scene (engine-cited)", duration='while the stage lasts')],
                   text='Small things go wrong first.'),
             stage(2, CUR, 'S2', [E('eff.06.grant_snag', type='precision', sign='snag', to='the bearer', fact='curse.evil_eye',
                                    applies_when="the bearer's first two rolled beats of each scene (engine-cited)", duration='while the stage lasts')],
                   text='Then larger ones.'),
             stage(3, CUR, 'S3', [E('eff.06.grant_snag', type='precision', sign='snag', to='the bearer', fact='curse.evil_eye',
                                    applies_when="the bearer's first two rolled beats of each scene (engine-cited)", duration='while the stage lasts'),
                                  E('eff.stakes_step', ladder='stakes', steps=1, applies_when="the bearer's first Risky frame of each scene")],
                   text='And what goes wrong goes badly.')],
            ['the lift', 'eff.05.end_working against Moderate: one stage down', 'runs its course after 7 checks'], attribute='resolve',
            max_checks=7, terminal='holds at stage 3', lift='the one who laid it forgives the bearer, or receives a gift freely given'),
        aff('aff.wasting', 'The wasting', 'curse', ['trait.nature.magical'], ['rit.lay_curse (05)', 'a power wronged'], 'hard', 'days:1', 'days:7',
            [stage(1, CUR, 'S2', [VM(2)], text='Thinner each week.'),
             stage(2, CUR, 'S3', [VM(4), AC('cond.exhausted', 'S2', 'while the stage lasts (this stack cannot be removed)')], text='Grey and slow.'),
             stage(3, CUR, 'S4', [VM(4), AC('cond.exhausted', 'S2', 'while the stage lasts'),
                                  E('eff.07.rest_cap', rests=['rest_long'], quality='partial', applies_when='always')], text='A shadow of yourself.')],
            ['the lift', 'eff.05.end_working against Hard: one stage down'], attribute='resolve', terminal='holds at stage 3',
            lift='written when the curse is laid (the wrong righted, the thing returned); sealed until learned, with three clue placements (15)'),
        aff('aff.grave_bound', 'Grave-bound', 'curse', ['trait.nature.magical', 'harm.blight.necrotic'], ['taking from the dead', 'a barrow-king\'s word'],
            'hard', 'days:1', 'days:7',
            [stage(1, CUR, 'S2', [E('eff.07.block_restore', event_kind='a Vitality-restoring effect on the bearer', source_filter='rest', amount='half')],
                   text='No fire warms you: rests restore half the Vitality they would.'),
             stage(2, CUR, 'S3', [E('eff.07.block_restore', event_kind='a Vitality-restoring effect on the bearer', source_filter='rest', amount='half'),
                                  E('eff.07.block_restore', event_kind='a Vitality-restoring effect on the bearer', source_filter='trait.nature.magical', amount='all')],
                   text='Nor does any healing hand.'),
             stage(3, CUR, 'S4', [E('eff.07.block_restore', event_kind='a Vitality-restoring effect on the bearer', source_filter='any', amount='all')],
                   text='Nothing restores you.')],
            ['the lift', 'eff.05.end_working against Hard: one stage down'], attribute='resolve', terminal='holds at stage 3',
            lift='what was taken from the dead is returned to them, or the dead are laid to rest (a rite, 05)',
            basis=['07.9.7', 'R6 C.3 worked example ("no warmth heals you")']),
    ]


AFF_HEADER = """# data/afflictions.yaml
# Purpose: staged afflictions: poisons, diseases and curses (07.9). An affliction is an exposure check, an onset, then
#   a stage check at each cadence boundary: critical success two stages down, success one down, failure by 3 or less
#   holds, failure one up, critical failure two up (07.9.3). Stage 0 is cured. Each stage applies one carrier
#   condition (cond.poisoned, ch.06; cond.diseased, cond.cursed, data/conditions.yaml owner-block 07) at the stage's severity,
#   optional stage harm at each check (no reduction, periodic, lethal only after the warn_stage warning is effective,
#   07.9.5), and listed effects.
# Owner: 07-harm-recovery-death. Schema: data/SCHEMAS.md#afflictionsyaml (Affliction: id, harm_tags, stages [{stage,
#   condition, severity, duration, check {verb, dc_tier}, on_fail, on_success}], onset, cure). Optional fields added by
#   ch.07 (documented in 07 Tables): kind, delivery, virulence, cadence, max_checks, lethal, warn_stage, contagious,
#   terminal, lift, stage.harm, stage.effects, stage.text, check.attribute.
# Cadence handlers: rounds -> the carrier's periodic at the bearer's turn_end (06.1.8); intervals -> h.07.affliction_onset;
#   days:1 -> h.07.affliction_day; days:7 -> h.07.curse_cycle; trigger -> the named event.
# Generated and validated by rules/_process/simulation/07-gen_data07.py.
# Basis: [07.9] [R5 HR-08, G-8] [R: https://2e.aonprd.com/Rules.aspx?ID=2319] [DL-07-17]

schema_version: 1
afflictions:
"""

# =====================================================================================================
# last_chance.yaml
# =====================================================================================================


def option(n, id_, name, requires, struck_when, outcome, world_writes, text, **extra):
    e = {'id': id_, 'name': name, 'order': n, 'tags': [], 'requires': requires, 'struck_when': struck_when,
         'outcome': outcome, 'world_writes': world_writes, 'text': text}
    e.update(extra)
    e['lifecycle'] = 'provisional'
    e['basis'] = ['07.5.2', 'T-07-10', 'R6 C.3 C-R3', 'DL-07-05']
    return e


def options():
    STAB = E('eff.07.stabilize', target='the PC', brink_wound=True)
    V1 = E('eff.restore', quantity='vitality', units='to 1', target='the PC')
    VQ = E('eff.restore', quantity='vitality', units='to ceil(vitality.max / 4)', target='the PC')
    return [
        option(1, 'lc.captured', 'Captured',
               "a victor is present AND (victor.defeat_disposition in [capture, ransom, rob, drag_to_lair] OR victor.objective == capture(pc))",
               ["the victor's disposition changed to kill this scene (a recorded behavior change, 09)",
                'quarter was offered and refused this scene (fact quarter_refused), unless capture is the victor\'s own objective'],
               [STAB, E('eff.write_fact', subject='pc', predicate='defeated.manner', value='captured')],
               ['run disposition capture, defeated column (T-07-11; PR-07-7)', 'setback.threshold', 'setback.captured',
                'a brink mark (07.7.3)', 'chronicle line'],
               'You live, in their hands: taken, stripped, held somewhere with a clock and three ways out.',
               always_available=False, death=False, stays_in_scene=False, brink_wound=True, mark='chosen: one of three'),
        option(2, 'lc.maimed', 'Maimed',
               'NOT chosen this scene AND some attribute has no maim and is above -2',
               [],
               [E('eff.07.stabilize', target='the PC', brink_wound=True), VQ,
                E('eff.07.maim', attribute_order="the drawn maim entry's", amount=-1),
                E('eff.write_fact', subject='pc', predicate='wound_load', value=0)],
               ['a maim entry drawn by the site of the worst fresh wound (07.7.4; injuries.yaml kind: maim)', 'setback.threshold',
                'chronicle line'],
               'The blow that should have killed takes something else, for life. You stand, with a quarter of your Vitality.',
               always_available=True, once_per='scene', death=False, stays_in_scene=True, brink_wound=True, mark='the maim'),
        option(3, 'lc.bargain', "Death's Bargain",
               'a bargainer exists (07.5.2 decision 2) AND the PC carries no aff.deaths_debt',
               ['the bargainer is the foe at the Threshold and holds a recorded refusal (15): the PC\'s death is its sworn duty'],
               [STAB, V1, E('eff.force_check', verb='none', effect_dc_source='none', degree_table='afflictions.yaml#aff.deaths_debt at stage 1, no exposure check')],
               ['vow thread for the ask (11) with clk.deaths_debt (harm.yaml#clock_templates)', 'the mark inj.mark.deaths_debtor',
                'setback.threshold', 'the bargainer ends the danger in its own way (a fact naming how)', 'chronicle line'],
               'A power spares you for a price it names. You carry its curse until the debt is paid; forfeit, and you stand here again.',
               always_available=False, death=False, stays_in_scene=False, brink_wound=True, mark='inj.mark.deaths_debtor'),
        option(4, 'lc.left_for_dead', 'Left for Dead',
               "(a victor is present AND victor.defeat_disposition NOT in [kill, drag_to_lair]) OR (no victor AND the source is a hazard or affliction)",
               ['the hazard is one nothing is left in: a flow of molten rock, a sealed and flooding vault (a recorded fact of the place)'],
               [STAB, V1],
               ['advance_time one watch (every boundary runs)', 'objective_lost', 'a folk victor takes all carried coin and the most valuable carried item to a cache (07.6.4)',
                'what was in hand lies where the PC fell', "the belief pc.dead on the victor (truth: false)", 'setback.threshold',
                'setback.defeated', 'a brink mark (07.7.3)', 'chronicle line',
                'position: where the PC fell, or the nearest place downstream or below when the source was water or a fall'],
               'They take you for dead and go. You wake a watch later with what they did not want.',
               always_available=False, death=False, stays_in_scene=False, brink_wound=True, mark='chosen: one of three'),
        option(5, 'lc.rout', 'Rout',
               '(a route exists (07.4.3 decision 1) AND the PC is not cornered, restrained or pinned) OR an able companion can carry the PC',
               ['every recorded route is held (facts naming who holds each)'],
               [STAB, V1, E('eff.tick_clock', clock='the clock chosen by 07.4.3', ticks='U(S4)')],
               ['position: the nearest safe place the route reaches', 'fallen companions carried along', 'objective_lost',
                'setback.threshold', 'setback.retreated {severity: S4}', 'a brink mark (07.7.3)', 'chronicle line'],
               'You are carried or drag yourself clear, and the world pays: three ticks on the clock this fight was about.',
               always_available=False, death=False, stays_in_scene=False, brink_wound=True, mark='chosen: one of three'),
        option(6, 'lc.reprieve', 'Reprieve',
               'fate.current >= fate_cost',
               [],
               [E('eff.07.stabilize', target='the PC', brink_wound=False), VQ,
                E('eff.write_fact', subject='pc', predicate='wound_load', value=0)],
               ['spend_fate(fate_cost) (01.16.4)', 'the event that passed the Threshold is undone (its harm and step are not applied)',
                'reprieves_taken + 1', 'setback.threshold', 'chronicle line'],
               'Luck, spent. The blow goes wide. You stand with a quarter of your Vitality and owe nothing.',
               fate_cost='min(3, 1 + reprieves_taken)', fate_cost_range=[1, 3], always_available=False, death=False,
               stays_in_scene=True, brink_wound=False, mark='none'),
        option(7, 'lc.last_stand', 'Last Stand',
               'none',
               [],
               [E('eff.write_fact', subject='pc', predicate='last_stand', value='one turn of three actions; every rolled beat is a critical success at its framed reach; abilities cost no Focus (07.5.9)'),
                E('eff.write_fact', subject='pc', predicate='harm_state', value='dead (at the end of that turn; Key 1 on record, Key 2 a)')],
               ['a legend line in the chronicle with its witnesses (11)', "ch.11's legacy procedure begins"],
               'One last turn in which nothing you attempt fails. Then you die.',
               always_available=True, death=True, stays_in_scene=True, brink_wound=False, mark='none'),
        option(8, 'lc.gamble', 'Gamble',
               'none',
               [],
               [E('eff.force_check', verb='endure', effect_dc_source='tier: moderate',
                  degree_table='last_chance.yaml#lc.gamble.degrees')],
               ['a lethal frame with its own OFFER (exact odds shown; auto_commit never applies)', 'setback.threshold', 'chronicle line'],
               'One roll, odds shown. You may walk away having paid nothing. You may die.',
               always_available=True, death='on failure and critical failure', stays_in_scene='by result', brink_wound='by result', mark='by result',
               degrees={'critical_success': 'as lc.reprieve at no cost (no fate spent, no brink wound)',
                        'success': 'stabilized where the PC lies and overlooked: as lc.left_for_dead with nothing taken and no mark; a brink wound',
                        'failure_within_3': 'the player chooses one still-available option of lc.captured, lc.maimed, lc.bargain, lc.left_for_dead, lc.rout and pays it in full',
                        'failure': 'harm_state.dead (Key 2 b)', 'critical_failure': 'harm_state.dead (Key 2 b)'},
               check={'verb': 'verb.endure', 'attribute': 'endurance', 'dc_tier': 'moderate', 'levers': 'none', 'status': 'none',
                      'fate_reroll': True}),
        option(9, 'lc.road_ends', 'The Road Ends',
               'none',
               [],
               [STAB, V1],
               ["ch.11's retirement procedure runs at once, ending: retire to a life; the character becomes an NPC",
                'carried from the scene by whoever the fiction provides (a fact naming who)', 'setback.threshold', 'chronicle line'],
               'You live, and never take the road again. Your story passes to those who come after.',
               always_available=True, death=False, stays_in_scene=False, brink_wound=True, mark='none', ends_career=True),
    ]


LC_HEADER = """# data/last_chance.yaml
# Purpose: the nine options of the last-chance menu, offered at the Threshold in place of any death roll (07.5).
#   The engine evaluates `requires` against state, the DM may strike an option only for a reason on its closed
#   `struck_when` list (citing a fact id), and the engine validates that at least three options remain and at least one
#   is not death (always true: lc.maimed or lc.road_ends, lc.last_stand, lc.gamble). There is no default choice.
#   Death is written only by lc.last_stand, or by lc.gamble on a failure (the Two-Key rule, 07.3.1).
# Owner: 07-harm-recovery-death. Schema: data/SCHEMAS.md#last_chanceyaml (Option: id, name, requires, outcome,
#   world_writes, fate_cost?, always_available?). Optional fields added by ch.07 (documented in 07 Tables): order,
#   struck_when, text, death, stays_in_scene, brink_wound, mark, once_per, fate_cost_range, degrees, check, ends_career.
# fate_cost: ch.01's spend_fate(n) (01.16.4); n = min(3, 1 + reprieves already taken in this character's life).
# Generated and validated by rules/_process/simulation/07-gen_data07.py.
# Basis: [07.5] [R6 C.3 C-R3] [R4 9 07 item 5] [INV-6] [01.16.4] [DL-07-05] [DL-07-06] [DL-07-07]

schema_version: 1
validation: {min_options: 3, min_not_death: 1, default_choice: none, pause_point: true}
options:
"""

exec(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '07-gen_harm07.py'), encoding='utf-8').read())
