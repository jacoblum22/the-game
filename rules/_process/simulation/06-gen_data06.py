#!/usr/bin/env python3
"""06-gen_data06.py -- generator and validator for chapter 06's data files.

Writes (paths relative to rules/):
  data/conditions.yaml            27 conditions in 00.9.1's schema (23 reserved ids + 4 added)
  data/conflict.yaml              economy, bands, flags, weapons, shapes, morale, chases, command, ...
  data/contrib/effects.06.yaml    four effect definitions (owner-block 06)
  data/contrib/boundaries.06.yaml seven handlers (five reserved by 00, two added)
Then re-loads every file, checks ids against data/substrate.yaml and data/effects.yaml, and prints a
census. Run from rules/_process/simulation:  python 06-gen_data06.py
"""
import io
import os
import sys

import yaml

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
D = os.path.join(ROOT, 'data')
C = os.path.join(D, '..', '_process', 'merged-contrib')


def dump(path, header, obj):
    body = yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=118, default_flow_style=False)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(header.rstrip('\n') + '\n\n' + body)


def E(effect_id, **params):
    return {'effect_id': effect_id, 'params': params}


def status(amount, when):
    return E('eff.status_modifier', amount=amount, applies_when=when)


def dstatus(amount, when='any aimed attack against the bearer', attribute='agility'):
    return E('eff.defense_status', amount=amount, attribute=attribute, applies_when=when)


def lever_for_attackers(verbs=('verb.strike', 'verb.grapple', 'verb.force'), also='aimed workings', when=None):
    p = dict(type='precision', to='each entity making the beat against the bearer', for_verbs=list(verbs),
             for_tags=[also] if also else [], duration='while the condition lasts', engine_cited=True)
    if when:
        p['applies_when'] = when
    return E('eff.grant_lever', **p)


def restrict(**forbid):
    return E('eff.restrict', forbid=forbid, target='the bearer', duration='while the condition lasts')


BASIS = ['00.9', 'T-00-15', '06.7', 'DL-06-13']
NOT_IMPLY = ['a wound, a mark or lasting harm', 'a condition other than this one',
             'a duration longer than the instance holds']
CONTROL = {'window': 'conflict', 'group': 'control', 'halve_after': 1, 'immune_after': 2,
           'counter_decay': {'boundary': 'round', 'amount': -1, 'only_if': 'the target carried no control condition this round'}}


def cond(id_, name, category, severity, stacking, duration, modifies, *, tags=(), sev_var=False,
         max_stacks=1, escalates_to=None, decay=(), cleanse=(), group=None, rank=0, neutralizes=(),
         control=False, periodic=(), on_apply=(), on_remove=(), visible=True, not_imply=(), intent='',
         basis=(), reserved=True):
    return {
        'id': id_, 'name': name, 'tags': list(tags), 'category': category, 'severity': severity,
        'severity_variable': sev_var, 'stacking': stacking, 'max_stacks': max_stacks,
        'escalates_to': escalates_to, 'duration': duration, 'decay': list(decay), 'cleanse': list(cleanse),
        'exclusion_group': group, 'priority_rank': rank, 'neutralizes': list(neutralizes),
        'diminishing': dict(CONTROL) if control else None, 'modifies': list(modifies),
        'periodic': list(periodic), 'on_apply': list(on_apply), 'on_remove': list(on_remove),
        'visible': visible, 'narration_may_not_imply': NOT_IMPLY + list(not_imply),
        'reserved_by_00': reserved, 'intent': intent, 'lifecycle': 'provisional',
        'basis': BASIS + list(basis),
    }


ENT = 'rounds:1'   # "until the end of the bearer's next turn", counted at its turn_end
ACT = lambda what: {'means': 'one action by the bearer (verb.handle): ' + what, 'requires': None, 'check': None}

CONDITIONS = [
    cond('cond.off_balance', 'Off-balance', 'physical', 'S1', 'refresh', ENT,
         [status(-2, 'attribute in [might, agility]')],
         cleanse=[ACT('recover footing')],
         intent='Footing lost. The bearer is worse at physical acts; others may cite it as one lever (type by use); the engine does not cite it automatically.',
         not_imply=['that the bearer fell (that is cond.prone)']),
    cond('cond.prone', 'Prone', 'positional', 'S2', 'unique', 'until_cleansed',
         [status(-2, 'verb in [verb.strike, verb.force, verb.grapple] and delivery is melee'),
          lever_for_attackers(when='the attack is melee'),
          E('eff.06.grant_snag', type='precision', to='each entity attacking the bearer', applies_when='the attack is ranged from band.near or farther', fact='prone target at range'),
          E('eff.06.pace', amount=-1, note='each band transition costs +1 action; at most one band a turn')],
         cleanse=[{'means': 'Stand: one action; provokes an Opportunity Strike (06.6.2 c)', 'requires': None, 'check': None}],
         intent='On the ground.'),
    cond('cond.grabbed', 'Grabbed', 'positional', 'S1', 'replace_stronger', 'while:the hold lasts',
         [restrict(methods=['change band away from the holder']),
          status(-2, 'severity is S2 and (trait.action.manipulate or (verb is verb.strike and weapon lacks close_quarters))')],
         sev_var=True, group='hold', rank=1,
         cleanse=[{'means': 'break free: one action', 'requires': None, 'check': {'verb': 'verb.grapple', 'dc_tier': "opposed: the holder's Might defense (or the binding object's tier)"}},
                  {'means': 'the holder releases, is moved away, or is stunned, unconscious or defeated', 'requires': None, 'check': None}],
         intent='Held; cannot move away. S1: may otherwise act. S2: hands hampered, and dragged when the holder Moves.',
         basis=['01.18.9', '06.5.2']),
    cond('cond.restrained', 'Restrained', 'positional', 'S3', 'replace_stronger', 'while:the hold or bonds last',
         [restrict(verbs=['verb.move'], methods=['Strike with a weapon lacking close_quarters', 'the Fend reaction']),
          status(-2, 'attribute in [might, agility]'), dstatus(-2), lever_for_attackers()],
         group='hold', rank=2, control=True,
         cleanse=[{'means': 'break free: one action', 'requires': None, 'check': {'verb': 'verb.grapple', 'dc_tier': "opposed: the holder's Might defense; bonds: their tier (rope Moderate, chain Very hard)"}}],
         intent='Bound or held fast; Move forbidden.'),
    cond('cond.pinned', 'Pinned', 'positional', 'S4', 'replace_stronger', 'while:the hold lasts',
         [restrict(verbs=['verb.move', 'verb.strike', 'verb.force', 'verb.exert'], methods=['any beat with trait.action.manipulate', 'Grapple other than to break free', 'the Fend reaction']),
          dstatus(-4), lever_for_attackers()],
         group='hold', rank=3, control=True,
         cleanse=[{'means': 'break free: one action', 'requires': None, 'check': {'verb': 'verb.grapple', 'dc_tier': "opposed: the holder's Might defense"}}],
         intent='Held down; most physical verbs forbidden; helpless (06.7.6).'),
    cond('cond.blinded', 'Blinded', 'sensory', 'S3', 'refresh', ENT,
         [status(-4, 'the beat relies on sight (Strike, aimed working, opposed Move)'), dstatus(-2), lever_for_attackers(),
          restrict(senses=['sight'], methods=['sight-based Observe', 'reactions against what the bearer cannot see', 'targeting beyond band.engaged except a suspected place at two snags'])],
         control=True,
         cleanse=[ACT('wipe or wash the eyes, when the source is grit, glare or a covering')],
         intent='Cannot see.'),
    cond('cond.deafened', 'Deafened', 'sensory', 'S2', 'refresh', ENT,
         [status(-2, 'the check is the tempo check or notice against an unseen mover'),
          restrict(senses=['hearing'], methods=['hearing-based Observe']),
          E('eff.condition_immunity', forbid={'effects_with_trait': ['trait.action.speech']}, target='self')],
         intent='Cannot hear; beats that work through speech do not affect the bearer.'),
    cond('cond.dazed', 'Dazed', 'mental', 'S2', 'refresh', ENT,
         [E('eff.06.fewer_actions', actions_delta=-1, minimum_actions=1, reactions_delta=-1)],
         control=True, tags=['trait.nature.mental'],
         intent='Reduced actions: one action fewer each turn (never fewer than one); no reaction.'),
    cond('cond.stunned', 'Stunned', 'mental', 'S3', 'refresh', ENT,
         [E('eff.06.fewer_actions', actions_delta=-3, minimum_actions=0, reactions_delta=-1), dstatus(-2), lever_for_attackers()],
         control=True, on_apply=[E('eff.cleanse', condition_or_category='sustained workings held by the bearer', target='the bearer')],
         intent='No actions and no reactions; sustained workings end.'),
    cond('cond.unconscious', 'Unconscious', 'physical', 'S4', 'unique', 'scene',
         [E('eff.06.fewer_actions', actions_delta=-3, minimum_actions=0, reactions_delta=-1), dstatus(-4), lever_for_attackers(),
          restrict(senses=['sight', 'hearing'], verbs=['verb.observe'])],
         on_apply=[E('eff.apply_condition', condition='cond.prone', severity='S2', duration='until_cleansed', target='the bearer')],
         cleanse=[{'means': 'woken: one action by another, or any harm (ordinary sleep only)', 'requires': 'the source is sleep', 'check': None},
                  {'means': 'the scene ends, or treatment (07)', 'requires': 'the source is a nonlethal defeat', 'check': None}],
         intent='Helpless and unaware; no actions.'),
    cond('cond.frightened', 'Frightened', 'mental', 'S1', 'replace_stronger', 'until_cleansed',
         [status(-1, 'severity is S1 and the source is perceived'), status(-2, 'severity in [S2, S3] and the source is perceived'),
          restrict(methods=['willingly Move closer to the source']),
          E('eff.restrict', forbid={'methods': ['any first action of the turn other than moving away from the source, if moving away is possible']}, target='the bearer', duration='while severity is S3')],
         sev_var=True, tags=['trait.nature.mental', 'harm.mind'], neutralizes=[],
         decay=[{'boundary': 'turn_end', 'action': 'reduce_severity'}],
         on_apply=[E('eff.tick_clock', clock="clk.morale.<the bearer's side>", ticks=1, limit='once per round per side')],
         control=False,
         intent='Fear of a recorded source; cannot willingly approach it. Decays one rung at each of the bearer\'s turn ends. At S3 it counts as a control condition (06.7.4).',
         not_imply=['that the bearer fled further than it Moved'], basis=['06.7.4']),
    cond('cond.charmed', 'Charmed', 'mental', 'S2', 'unique', 'scene',
         [restrict(methods=['attack-trait beats against the source']),
          E('eff.grant_lever', type='precision', to='the source', for_verbs=['verb.talk'], for_tags=[], duration='while the condition lasts', engine_cited=True)],
         tags=['trait.nature.mental'],
         cleanse=[{'means': 'the source or its allies harm the bearer', 'requires': None, 'check': None}],
         intent='Regards the source as a friend. Counts as a control condition (06.7.4). A charmed PC stays under the player\'s control; only the restriction and the lever apply.',
         not_imply=['that the bearer obeys commands', 'that the bearer attacks its allies']),
    cond('cond.distracted', 'Distracted', 'mental', 'S1', 'refresh', ENT,
         [status(-2, 'attribute is wits'), E('eff.defense_status', amount=-2, attribute='wits', applies_when='any')],
         intent='Attention split: worse at noticing, easier to slip past or feint.'),
    cond('cond.exposed', 'Exposed', 'physical', 'S1', 'refresh', ENT,
         [lever_for_attackers()],
         intent='Defenses opened: attackers hold a Precision lever (05.6; Quarry\'s Mark; a Setup).',
         basis=['05 Interface request (a)']),
    cond('cond.slowed', 'Slowed', 'physical', 'S2', 'refresh', ENT,
         [E('eff.06.pace', amount=-1, note='each band transition costs +1 action'),
          restrict(methods=['Withdraw and Strike in the same turn'])],
         intent='Fewer bands per move.'),
    cond('cond.weakened', 'Weakened', 'physical', 'S1', 'replace_stronger', ENT,
         [status(-2, 'attribute is might'),
          E('eff.harm_severity_step', ladder='severity', steps=-1, applies_when='harm dealt by the bearer and severity of the condition is S1'),
          E('eff.harm_severity_step', ladder='severity', steps=-2, applies_when='harm dealt by the bearer and severity of the condition is S2')],
         sev_var=True, intent='Reduced harm dealt.'),
    cond('cond.exhausted', 'Exhausted', 'physical', 'S2', 'intensify', 'until_rest:rest_long',
         [status(-1, 'any; per stack (stacks 1..3 give -1, -2, -3)'),
          E('eff.06.pace', amount=-1, applies_when='stacks is 3', note='as cond.slowed')],
         max_stacks=3, decay=[{'boundary': 'rest_long', 'action': 'reduce_stack'}],
         intent='Worn down. Three stacks at most; one stack leaves at each completed long rest (07).',
         basis=['05.6.6 (overdraw adds a stack)']),
    cond('cond.bleeding', 'Bleeding', 'physical', 'S1', 'intensify', 'scene',
         [], max_stacks=3, tags=['harm.physical.cut'],
         periodic=[{'boundary': 'turn_end', 'effect_id': 'eff.06.internal_harm', 'params': {'vitality_per_stack': 1, 'harm_tags': ['harm.physical.cut'], 'no_reduction': True}}],
         cleanse=[{'means': 'staunch it: one action', 'requires': None, 'check': {'verb': 'verb.handle', 'dc_tier': 'easy'}},
                  {'means': 'any magical healing of the bearer', 'requires': None, 'check': None}],
         intent='Loses 1 Vitality per stack at each of its turn ends.'),
    cond('cond.burning', 'Burning', 'physical', 'S1', 'intensify', 'rounds:3',
         [], max_stacks=3, tags=['harm.fire.flame'], neutralizes=['cond.chilled', 'cond.frozen'],
         periodic=[{'boundary': 'turn_end', 'effect_id': 'eff.deal_harm', 'params': {'severity': 'S1', 'harm_tags': ['harm.fire.flame'], 'target': 'the bearer', 'times': 'stacks'}}],
         cleanse=[ACT('beat out the flames'), {'means': 'water, or dropping to roll (the bearer becomes prone)', 'requires': None, 'check': None}],
         intent='Takes S1 fire harm per stack at each of its turn ends (reduction applies to each).'),
    cond('cond.chilled', 'Chilled', 'physical', 'S1', 'escalate', 'rounds:2',
         [status(-1, 'attribute is agility')], max_stacks=2, tags=['harm.frost.cold'],
         escalates_to={'condition': 'cond.frozen', 'at_stacks': 2}, neutralizes=['cond.burning'],
         cleanse=[{'means': 'a fire or warmth for one action', 'requires': None, 'check': None}],
         intent='Cold slows the hands and feet; a second stack freezes.'),
    cond('cond.frozen', 'Frozen', 'physical', 'S3', 'unique', ENT,
         [restrict(verbs=['verb.move']), status(-2, 'attribute in [might, agility]'), dstatus(-2), lever_for_attackers()],
         tags=['harm.frost.ice'], control=True,
         on_remove=[E('eff.apply_condition', condition='cond.chilled', severity='S1', duration='rounds:2', target='the bearer')],
         intent='Locked by cold; Move forbidden. Thaws to one stack of chilled.'),
    cond('cond.choking', 'Choking', 'physical', 'S2', 'refresh', 'while:the source lasts',
         [status(-2, 'any'), restrict(methods=['any beat with trait.action.speech'])],
         tags=['harm.physical.asphyxia'],
         periodic=[{'boundary': 'turn_end', 'effect_id': 'eff.06.internal_harm', 'params': {'vitality_per_stack': 1, 'harm_tags': ['harm.physical.asphyxia'], 'no_reduction': True}}],
         cleanse=[{'means': 'leave the source (the smoke, the water) or break the hold', 'requires': None, 'check': None}],
         intent='Cannot speak; loses 1 Vitality at each of its turn ends while the source lasts. Holding breath is ch.07\'s Endure.'),
    cond('cond.poisoned', 'Poisoned', 'affliction_stage', 'S1', 'replace_stronger', 'until_cleansed',
         [status(-1, 'severity is S1'), status(-2, 'severity in [S2, S3]'), status(-3, 'severity in [S4, S5]')],
         sev_var=True, tags=['harm.venom'],
         cleanse=[{'means': "the affliction's stage table (ch.07) or a remedy", 'requires': None, 'check': None}],
         intent='The generic carrier for ch.07\'s staged afflictions; periodic effects are the affliction\'s.'),
    cond('cond.surprised', 'Surprised', 'mental', 'S2', 'unique', 'while:its first turn has not ended',
         [E('eff.06.fewer_actions', actions_delta='to one action on its first turn', minimum_actions=1, reactions_delta=-1),
          lever_for_attackers(), E('eff.write_fact', subject='the bearer', predicate='acts_last_in_round', value=1)],
         intent='Caught unaware at the start of a conflict (06.2.4).', reserved=False, basis=['06.2.4', 'DL-06-12']),
    cond('cond.silenced', 'Silenced', 'sensory', 'S2', 'refresh', ENT,
         [restrict(methods=['any beat with trait.action.speech', 'workings that need the voice'])],
         intent='Cannot speak (a gag, a spell, a crushed throat).', reserved=False, basis=['01.17 trait.action.speech', 'DL-06-12']),
    cond('cond.broken', 'Broken', 'mental', 'S3', 'unique', 'conflict',
         [status(-2, 'the beat has trait.action.attack'),
          restrict(methods=['attack-trait beats unless flag.cornered or attacked while unable to flee']),
          E('eff.grant_lever', type='precision', to='each entity demanding its surrender', for_verbs=['verb.talk'], for_tags=[], duration='while the condition lasts', engine_cited=True)],
         tags=['trait.nature.mental'],
         intent="Its side's morale clock completed (06.11.5): it flees, yields or cowers.", reserved=False, basis=['06.11.5', 'DL-06-12']),
    cond('cond.heartened', 'Heartened', 'mental', 'S1', 'replace_stronger', 'scene',
         [status(1, 'severity is S1'), status(2, 'severity is S2'),
          E('eff.condition_immunity', forbid={'conditions': ['cond.frightened at S1']}, target='self')],
         sev_var=True, tags=['trait.nature.mental'],
         intent='Lifted by a rally, a blessing, a cause: the one status bonus (+1 or +2).', reserved=False, basis=['00.3.5 status best bonus +2', 'DL-06-12']),
]

COND_HEADER = """# data/conditions.yaml
# Purpose: every condition in the game, in 00.9.1's schema. 27 entries: the 23 ids reserved by 00 (T-00-15) and
#   four added by ch.06 (cond.surprised, cond.silenced, cond.broken, cond.heartened; DL-06-12). Chapter 07 adds
#   affliction stages and wound carriers in its owner-block under `blocks:`.
# Owner: 06-conflict (06.7). Schema: data/SCHEMAS.md#conditionsyaml (Condition, 00.9.1).
# Conventions used here (06.7.2, the three voices; DL-06-13):
#   - status effects (eff.status_modifier, eff.defense_status) act on the BEARER's own checks and defenses;
#   - eff.grant_lever / eff.06.grant_snag with `to:` give an ENGINE-CITED lever or snag to those acting against
#     the bearer; they count toward the two-per-roll limit and the +-4 cap (00.3.9);
#   - eff.restrict forbids verbs, methods and senses (a union across conditions; forbidden = G4 for the beat);
#   - "rounds:1" is "until the end of the bearer's next turn" (counted at its turn_end, 06.1.8);
#   - `diminishing` on control conditions shares ONE counter per target across the group `control` (06.7.4);
#     cond.charmed and cond.frightened at S3 join that group by rule (06.7.4), not by this field.
# Optional fields added by ch.06 (documented in 06 Tables): reserved_by_00, intent, diminishing.group,
#   diminishing.counter_decay.
# Generated and validated by rules/_process/simulation/06-gen_data06.py.
# Basis: [00.9] [T-00-15] [R2 #3] [R3 06.7] [06.7] [DL-06-12..14]"""

# ------------------------------------------------------------------------------------------- conflict.yaml
CONFLICT = {
    'schema_version': 1,
    'lifecycle': 'provisional',
    'economy': {
        'actions_per_turn': {'pc': 3, 'adversary': 2, 'mob': 2, 'companion': 0},
        'reactions_per_round': {'pc': 1, 'adversary_by_band': {'T1': 0, 'T2': 1, 'T3': 1, 'T4': 1, 'T5': 1}, 'mob': 0, 'companion': 1},
        'reaction_cap_with_grants': 2,
        'reaction_grant_allowed_from': ['a stance (slot.stance)', 'a calling capability', 'an ability of the Exception form'],
        'adds_actions': 'never (INV-11; 06.1.2)',
        'one_free_handling_per_turn': True,
        'action_costs': [
            {'what': 'move: engaged<->close; close<->near', 'cost': 1, 'verb': 'verb.move'},
            {'what': 'move: near<->far (dash)', 'cost': 2, 'verb': 'verb.move'},
            {'what': 'move: far<->distant', 'cost': 3, 'verb': 'verb.move'},
            {'what': 'withdraw: engaged->close, provoking nothing', 'cost': 1, 'verb': 'verb.move'},
            {'what': 'stand from prone; mount; dismount', 'cost': 1, 'verb': 'verb.move'},
            {'what': 'flank; screen an ally; turn to clear flag.flanked', 'cost': 1, 'verb': 'verb.move', 'roll': False},
            {'what': 'strike: unarmed, light, one-handed, bow, sling, crossbow', 'cost': 1, 'verb': 'verb.strike'},
            {'what': 'strike: heavy weapon', 'cost': 2, 'verb': 'verb.strike', 'counts_as_attacks': 1},
            {'what': 'reload: light crossbow', 'cost': 1, 'verb': 'verb.handle'},
            {'what': 'reload: heavy crossbow', 'cost': 2, 'verb': 'verb.handle'},
            {'what': 'grapple; break free', 'cost': 1, 'verb': 'verb.grapple'},
            {'what': 'force: shove, trip, throw, break', 'cost': 1, 'verb': 'verb.force'},
            {'what': 'exert: climb, leap, swing', 'cost': 1, 'verb': 'verb.exert'},
            {'what': 'evade: take cover', 'cost': 1, 'verb': 'verb.evade'},
            {'what': 'defend', 'cost': 1, 'verb': 'verb.evade', 'roll': False},
            {'what': 'full defense', 'cost': 2, 'verb': 'verb.evade', 'roll': False},
            {'what': 'sneak: hide', 'cost': 1, 'verb': 'verb.sneak'},
            {'what': 'handle: use, light, tie, bandage; recover footing; beat out flames; staunch a wound', 'cost': 1, 'verb': 'verb.handle'},
            {'what': 'observe: search, study a foe', 'cost': 1, 'verb': 'verb.observe'},
            {'what': 'recall', 'cost': 1, 'verb': 'verb.recall'},
            {'what': 'talk as a beat: intimidate, taunt, demand surrender, parley', 'cost': 1, 'verb': 'verb.talk'},
            {'what': 'setup: feint, distract, blind', 'cost': 1, 'verb': 'verb.setup'},
            {'what': 'aim', 'cost': 1, 'verb': 'verb.setup', 'roll': False},
            {'what': 'help', 'cost': 1, 'verb': 'verb.help'},
            {'what': 'ready (plus the reaction when it fires; the readied beat must cost 1)', 'cost': 1, 'verb': 'verb.ready'},
            {'what': 'command a companion (2 for a companion beat that costs 2)', 'cost': 1, 'verb': 'verb.talk'},
            {'what': 'an ability with timing beat', 'cost': 'the cost of its check.verb in this table', 'verb': 'by ability'},
            {'what': 'a rider, a flare, a push, an OFFER trade', 'cost': 0, 'verb': None},
            {'what': 'a resisted check (Endure, Evade vs an effect DC)', 'cost': 0, 'verb': None},
        ],
        'free_activities': ['speak a sentence', 'drop what is held', 'release a hold', 'end a stance, aura or sustained working',
                            'one draw, stow, pick-up or pass per turn', 'look around (passive notice)',
                            'ask an out-of-fiction question', 'yield (at any moment)'],
    },
    'repeated_attack': {'penalties': [0, -2, -4], 'window': "the actor's turn", 'counts': 'every beat with trait.action.attack, any target',
                        'heavy_strike_counts_as': 1, 'reactions_in_window': False, 'companions': 'each keeps its own window per PC turn',
                        'family': 'engine-applied Precision snags, outside the two-cited count, inside the +-4 cap (00.3.9 g)',
                        'basis': ['01.14.3', 'DL-01-08', 'DL-06-03']},
    'engine_snags': [
        {'id': 'repeat', 'amount': [0, -2, -4], 'rule': '06.1.6'},
        {'id': 'defending', 'amount': -2, 'applies_to': 'every aimed attack against an actor with defending.<actor>', 'rule': '06.1.5'},
        {'id': 'fend', 'amount': -2, 'applies_to': 'the one attack the reaction answered', 'rule': '06.6.3'},
        {'id': 'called', 'amount': -2, 'applies_to': 'a called shot (-4 for the head or eyes)', 'rule': '06.4.10'},
        {'id': 'nonlethal_edged', 'amount': -2, 'applies_to': 'a nonlethal Strike with an edged, pointed or shot weapon', 'rule': '06.4.8'},
    ],
    'cited_snags': [
        {'id': 'long_range', 'when': 'thrown at band.near; shortbow or sling at band.far'},
        {'id': 'crowded', 'when': 'a shot or thrown Strike while the attacker is engaged with any enemy'},
        {'id': 'into_a_melee', 'when': "a shot or thrown Strike at a target engaged with the attacker's ally", 'critical_failure': 'cost.harm to that ally, one rung lighter'},
        {'id': 'cover', 'when': 'the target holds flag.in_cover and the attack is ranged'},
        {'id': 'unseen', 'when': 'the target holds flag.obscured and the attacker relies on sight'},
        {'id': 'from_below', 'when': 'a melee Strike without reach at a target holding flag.elevated'},
        {'id': 'prone_at_range', 'when': 'a ranged Strike from band.near or farther at a prone target'},
    ],
    'tempo': {
        'pc_check': 'd20 + wits + competence(deed.martial.tactics.reading or ancestor) + edge + status',
        'adversary_dc': '10 + wits + competence(deed.martial.tactics.reading or ancestor) + edge + status',
        'reference_dc_by_band': {'T1': 10, 'T2': 11, 'T3': 12, 'T4': 13, 'T5': 14},
        'order': ["adversaries whose tempo DC > the PC's total, highest first", 'the PC', 'remaining adversaries, highest first'],
        'natural_20': 'the PC acts first; fact tempo.seized (a Precision lever on its first beat)',
        'natural_1': 'the PC acts last',
        'delay': 'the PC may move its turn later, permanently',
        'surprise': 'cond.surprised: acts last in round 1, one action, no reaction until its first turn ends',
        'rule': '06.2.2', 'handler': 'h.06.tempo_setup'},
    'range_bands': [
        {'id': 'band.engaged', 'words': "at blade's reach; locked together", 'meaning': 'an engagement link joins the two', 'move_cost': {'to': 'band.close', 'actions': 1}, 'allows': ['melee Strike', 'Grapple', 'Force', 'touch']},
        {'id': 'band.close', 'words': 'a few strides off; a lunge away', 'meaning': 'one Move step from engaged', 'move_cost': {'to': 'band.near', 'actions': 1}, 'allows': ['reach weapons', 'thrown (no snag)', 'any ranged Strike']},
        {'id': 'band.near', 'words': "across the room; a stone's throw", 'meaning': 'two Move steps from engaged', 'move_cost': {'to': 'band.far', 'actions': 2}, 'allows': ['thrown (snag)', 'bows, slings, crossbows', 'speech']},
        {'id': 'band.far', 'words': 'a long bowshot; across the field', 'meaning': 'a dash beyond near', 'move_cost': {'to': 'band.distant', 'actions': 3}, 'allows': ['longbow, crossbow', 'shortbow and sling (snag)', 'shouting']},
        {'id': 'band.distant', 'words': 'at the edge of sight; far beyond reach', 'meaning': 'beyond far; out of the fight if distant from every enemy', 'move_cost': None, 'allows': ['sight and signals only']},
    ],
    'pace': {'default': 1, 'pace_2_costs': [1, 1, 1, 2], 'slowed_prone_difficult': '+1 action per transition',
             'quantity': 'speed (T-00-13)'},
    'band_between_non_pc': ['an engagement link -> band.engaged', 'the same group -> band.close',
                            'else the farther of their two bands to the PC, never nearer than band.near'],
    'engagement': {'capacity_same_size': 4, 'capacity_in_chokepoint': 2, 'per_size_step_target_larger': 2,
                   'screening': 'one action; an enemy moving to engage the screened ally must pass the screener (opposed Move) or stop engaged with the screener and take its Opportunity Strike'},
    'positional_flags': [
        {'id': 'flag.flanked', 'words': 'caught between them', 'reserved_by_00': True,
         'set_by': ['Flank: an enemy engaged with the target, with an ally also engaged with it, spends 1 action'],
         'cleared_by': ['the carrier ends a turn engaged with fewer than two enemies', 'the carrier spends 1 action to turn', 'the carrier gains flag.in_chokepoint'],
         'effect_refs': [E('eff.grant_lever', type='precision', to='enemies making melee attacks against the carrier', engine_cited=True)]},
        {'id': 'flag.cornered', 'words': 'your back to the wall', 'reserved_by_00': True,
         'set_by': ['a completed pursuit or run-down clock', 'cost.footing S3', "a foe's Force or Move that delivers it", 'a feature fact at framing'],
         'cleared_by': ['a Move through an enemy', 'a Force that moves an enemy', 'a new exit established'],
         'effect_refs': [E('eff.restrict', forbid={'methods': ['Withdraw', 'Retreat', 'increase band to an engaged enemy', 'start a chase']}, target='the carrier'),
                         E('eff.grant_lever', type='precision', to='an entity demanding its surrender', for_verbs=['verb.talk'], engine_cited=True)]},
        {'id': 'flag.in_cover', 'words': 'behind (the cover named)', 'reserved_by_00': True,
         'set_by': ['Evade take cover (reach 2+)', 'Move (reach 3+)', 'Full defense with a shield', 'a stance or ability'],
         'cleared_by': ['the carrier Moves other than along the cover', 'the carrier makes a melee Strike', 'the feature is destroyed', 'ignored by an enemy at band.engaged'],
         'effect_refs': [E('eff.06.grant_snag', type='precision', to='ranged attacks against the carrier', fact='cover'),
                         E('eff.grant_lever', type='protective', to='the carrier', for_verbs=['verb.evade'], applies_when='an area effect from the far side of the cover')]},
        {'id': 'flag.elevated', 'words': 'above them (the height named)', 'reserved_by_00': True,
         'set_by': ['Move or Exert onto a height feature'], 'cleared_by': ['leaving it', 'being shoved off (Force reach 2+)'],
         'effect_refs': [E('eff.grant_lever', type='precision', to='the carrier', applies_when='attacks against lower enemies', engine_cited=True),
                         E('eff.06.grant_snag', type='precision', to='melee attacks from below without reach', fact='from below')],
         'reach_cost': 'enemies spend 1 extra action (Exert) to engage unless a stair or ramp is named'},
        {'id': 'flag.hidden', 'words': 'unseen', 'reserved_by_00': True,
         'set_by': ['Sneak reach 3+ when cover, flag.obscured, darkness or a distraction allows', 'scene framing'],
         'cleared_by': ["any beat of the carrier with trait.sense.visible or .loud other than a Sneak", 'cost.exposure S3+', "an enemy's Observe beating the stored Sneak total"],
         'effect_refs': [E('eff.restrict', forbid={'methods': ['aimed beats targeting the carrier (search by Observe, or attack a suspected place at two snags)']}, target='enemies of the carrier'),
                         E('eff.grant_lever', type='precision', to='the carrier', applies_when='its first attack from hiding; the target has no reaction to it', engine_cited=True)]},
        {'id': 'flag.mounted', 'words': 'in the saddle', 'reserved_by_00': True,
         'set_by': ['the Mount action', 'Grapple reach 2+ on a creature one or more size steps larger'],
         'cleared_by': ['Dismount', 'being unhorsed (Force or Grapple reach 2+)', 'the mount defeated'],
         'effect_refs': [E('eff.06.pace', amount="the mount's pace"), E('eff.reposition', target='the carrier', flags_add=['flag.elevated'], applies_when='against enemies on foot of the mount size or smaller')],
         'rule': '06.15'},
        {'id': 'flag.lined_up', 'words': 'strung out in a line', 'reserved_by_00': True,
         'set_by': ['a corridor, bridge, stair or ford feature at framing', 'a column of march', 'a Setup or Move that draws enemies into a line (reach 2+)'],
         'cleared_by': ['the carrier leaves the feature', 'any carrier spends 1 action to break the file'],
         'effect_refs': [], 'rule_effects': ['the pierce shape selects carriers, nearest first', "at most one carrier of a line may be engaged with a target at the line's head"]},
        {'id': 'flag.obscured', 'words': 'half-seen (the smoke, the dark, the mist named)', 'reserved_by_00': False,
         'set_by': ['a veil feature', 'scene.light dim or dark', 'a Handle or Force raising smoke or dust', 'an effect'],
         'cleared_by': ['leaving the veil', 'the veil ending', 'a light brought to bear'],
         'effect_refs': [E('eff.06.grant_snag', type='precision', to='aimed attacks against the carrier that rely on sight', fact='unseen')],
         'rule_effects': ['the carrier may Sneak to hide', 'concealment never helps an Evade']},
        {'id': 'flag.in_chokepoint', 'words': 'holding the gap (the door, the bridge named)', 'reserved_by_00': False,
         'set_by': ['Move to a chokepoint feature'], 'cleared_by': ['leaving it', 'being pushed out (Force reach 2+)', 'the feature destroyed'],
         'effect_refs': [E('eff.condition_immunity', forbid={'flags': ['flag.flanked']}, target='self')],
         'rule_effects': ['engagement capacity 2', 'enemies queuing to reach it gain flag.lined_up']},
        {'id': 'flag.aloft', 'words': 'in the air above', 'reserved_by_00': False,
         'set_by': ['a slot.movement_mode claim of mode fly', "a creature's template"],
         'cleared_by': ['landing', 'cond.prone, restrained, stunned or unconscious (it falls)'],
         'effect_refs': [E('eff.restrict', forbid={'methods': ['melee Strikes, Grapple and Force against the carrier from the ground']}, target='enemies on the ground')],
         'rule_effects': ['it may engage by descending (a Move)', 'it ignores ground features']},
    ],
    'feature_kinds': ['cover', 'height', 'chokepoint', 'hazard', 'difficult_ground', 'veil', 'loose_object', 'barrier'],
    'light': {'values': ['bright', 'dim', 'dark'], 'dim': 'beyond band.close everyone is flag.obscured to observers without night-sight',
              'dark': 'everyone not in a light is flag.obscured; an observer with no light and no night-sight is cond.blinded for sight-reliant beats'},
    'sizes': {'ladder': ['tiny', 'small', 'medium', 'large', 'huge', 'colossal'], 'pc': 'medium',
              'grapple_force_vs_larger': {'1': 'reach -1 rung (engine-cited Amplifying snag: scale)', '2': 'reach -2 rungs (Zero unless levers offset: G4 for the whole creature)', '3+': 'G4 for the whole creature'},
              'vs_smaller': 'one Amplifying lever', 'melee_reach': {'large': 'band.close', 'huge': 'band.near', 'colossal': 'band.near'},
              'engagement_capacity_per_step': 2, 'mount_min_steps_larger': 1, 'cover_min_steps_larger': 2},
    'defenses': {
        'guard': {'formula': '10 + agility + competence(guard tag) + edge + status',
                  'guard_tag': "the deed tag of the defender's readied melee weapon or shield (the higher), else deed.martial.unarmed; ancestors count; a shooting weapon gives none"},
        'against': [
            {'method': 'Strike; an aimed working that must hit a body', 'defense': 'guard'},
            {'method': 'Grapple; Force', 'defense': 'the higher of might or agility defense'},
            {'method': 'break a hold', 'defense': "the holder's might defense"},
            {'method': 'Move through or past a blocker', 'defense': 'the higher of might or agility defense'},
            {'method': 'Setup by feint or trick', 'defense': 'wits defense'},
            {'method': 'Setup by a blinding or tripping throw', 'defense': 'guard'},
            {'method': 'Sneak, hide, lift', 'defense': 'the highest notice (wits defense) among observers'},
            {'method': 'Talk to frighten, taunt, demand surrender, parley', 'defense': 'resolve defense (15 composes standing)'},
            {'method': 'a resisted effect', 'defense': 'the target rolls Endure or Evade against the effect DC; no action'},
        ],
        'unaware_target': 'a Strike still rolls against guard; the weapon tag is primary (06.4.2; DL-06-08)'},
    'weapon_weights': [
        {'id': 'unarmed', 'base_severity': 'S1', 'strike_cost': 1, 'hands': 0, 'bands': ['band.engaged'], 'deed_tags': ['deed.martial.unarmed'], 'license': 'lic.training.martial_unarmed'},
        {'id': 'light', 'base_severity': 'S2', 'strike_cost': 1, 'hands': 1, 'bands': ['band.engaged'], 'thrown_bands': ['band.close', 'band.near (snag)'],
         'examples': ['dagger', 'knife', 'hand axe', 'club', 'sap', 'short sword', 'sickle', 'dart'], 'item_tags': ['item.weapon.blade.dagger', 'item.weapon.axe.hand', 'item.weapon.bludgeon.club', 'item.weapon.thrown.knife']},
        {'id': 'one_handed', 'base_severity': 'S2', 'strike_cost': 1, 'hands': 1, 'bands': ['band.engaged'],
         'examples': ['sword', 'axe', 'mace', 'hammer', 'flail', 'spear', 'javelin', 'staff'], 'item_tags': ['item.weapon.blade.sword', 'item.weapon.bludgeon.mace', 'item.weapon.bludgeon.flail', 'item.weapon.polearm.spear', 'item.weapon.polearm.staff', 'item.weapon.thrown.javelin']},
        {'id': 'heavy', 'base_severity': 'S3', 'strike_cost': 2, 'hands': 2, 'bands': ['band.engaged'],
         'examples': ['greatsword', 'great axe', 'maul', 'halberd', 'pike', 'lance (1 action from the saddle with lic.training.martial_mounted)'], 'item_tags': ['item.weapon.blade.greatsword', 'item.weapon.axe.great', 'item.weapon.bludgeon.hammer', 'item.weapon.polearm.halberd', 'item.weapon.polearm.lance']},
        {'id': 'bow', 'base_severity': 'S2', 'strike_cost': 1, 'hands': 2, 'bands': ['band.close', 'band.near', 'band.far (shortbow, sling: snag; longbow: none)'],
         'examples': ['shortbow', 'longbow', 'sling (1 hand)'], 'item_tags': ['item.weapon.bow.shortbow', 'item.weapon.bow.longbow', 'item.weapon.bow.sling']},
        {'id': 'crossbow_light', 'base_severity': 'S2', 'strike_cost': 1, 'hands': 2, 'bands': ['band.close', 'band.near', 'band.far'], 'reload_actions': 1, 'item_tags': ['item.weapon.crossbow.light']},
        {'id': 'crossbow_heavy', 'base_severity': 'S3', 'strike_cost': 1, 'hands': 2, 'bands': ['band.close', 'band.near', 'band.far'], 'reload_actions': 2, 'item_tags': ['item.weapon.crossbow.heavy']},
    ],
    'weapon_properties': [
        {'id': 'finesse', 'effect': 'Agility is allowed for melee Strikes'},
        {'id': 'reach', 'effect': "Strikes at band.close; an enemy Moving from close to engaged with the wielder provokes its Opportunity Strike"},
        {'id': 'thrown', 'effect': "may be thrown: close no snag, near one Precision snag; the weapon ends at the target's position"},
        {'id': 'versatile', 'effect': 'in two hands: harm edge +1', 'effect_refs': [E('eff.harm_edge', amount=1, applies_when='wielded in two hands')]},
        {'id': 'parrying', 'effect': '+1 edge to Guard against melee attacks while the other hand holds no shield', 'effect_refs': [E('eff.defense_edge', amount=1, attribute='agility', applies_when='melee attacks; no shield held')]},
        {'id': 'armor_breaking', 'effect': "ignores 1 point of the target's worn-armor reduction"},
        {'id': 'close_quarters', 'effect': 'usable while grabbed or restrained with no status penalty from the hold'},
        {'id': 'entangling', 'effect': 'a Strike with it may be declared as a Grapple at its band, capped at cond.grabbed S2'},
        {'id': 'loading', 'effect': 'must be reloaded; carries the fact <weapon>.loaded'},
        {'id': 'concealable', 'effect': 'a Sneak to hide it holds a Precision lever'},
        {'id': 'shield_light', 'effect': '+1 edge to Guard; enables shield abilities', 'effect_refs': [E('eff.defense_edge', amount=1, attribute='agility', applies_when='any aimed attack')]},
        {'id': 'shield_heavy', 'effect': '+1 edge to Guard; while Defending, flag.in_cover against ranged attacks; Exert and Sneak take a snag', 'effect_refs': [E('eff.defense_edge', amount=1, attribute='agility', applies_when='any aimed attack')]},
    ],
    'weapon_properties_max_per_item': 2,
    'mastery': {'rule': '06.4.5', 'reads': 'the grade of the lic.training.martial_* license covering the weapon deed tag',
                'base_severity_rungs': {'none': 0, 'trained': 0, 'expert': 1, 'master': 2},
                'stage': 'E1 base (not an effect step; outside the +-2 effect-step cap); clamps at S5',
                'applies_to': ['Strikes with weapons', 'unarmed Strikes'], 'not_to': ['workings', 'adversaries (their severities are listed in templates)']},
    'armor_reference': {'owner': '07/08 (reference used by this chapter and its simulation)', 'reduction_vs_harm_physical': {'light': 1, 'medium': 2, 'heavy': 3},
                        'shield_reduction': 0, 'total_cap_assumed': 4},
    'harm_modes': [{'id': 'lethal', 'at_zero': 'defeated; ch.07 decides dead or Dying (Dying by default for recurring and principal NPCs)'},
                   {'id': 'nonlethal', 'at_zero': 'defeated; cond.unconscious for the scene; alive', 'snag': 'one Precision snag with edged, pointed or shot weapons'},
                   {'id': 'restraint', 'at_zero': None, 'note': 'not a Strike: Grapple'}],
    'called_shots': [
        {'id': 'gap', 'snag': -2, 'needs': 'worn armor (not no_gaps)', 'on_success': 'ignore worn-armor reduction'},
        {'id': 'leg', 'snag': -2, 'on_success': 'harm one rung lighter; cond.slowed until the end of its next turn'},
        {'id': 'arm', 'snag': -2, 'on_success': 'harm one rung lighter; cond.weakened S1 until the end of its next turn; critical success: it also drops what that hand holds'},
        {'id': 'head', 'snag': -4, 'on_success': 'full harm; cond.dazed until the end of its next turn (control)'},
        {'id': 'weak_spot', 'snag': -2, 'needs': 'a recorded weak-spot fact', 'on_success': 'an Amplifying lever in addition to any other two'},
        {'id': 'held_object', 'snag': -2, 'on_success': 'no harm to the creature; the object takes a Force against its tier, or falls from the hand at reach 2+'},
    ],
    'improvised': [
        {'rung': 'hand', 'anchor': 'one hand lifts and throws it', 'held_or_thrown': 'S1 (or S2 when it resembles a light weapon)', 'dropped_or_toppled': 'S1', 'selects_at_most': 1},
        {'rung': 'body', 'anchor': "about a person's weight or bulk", 'held_or_thrown': 'S3, two actions, one Precision snag', 'dropped_or_toppled': 'S2', 'selects_at_most': 2},
        {'rung': 'heavy', 'anchor': 'several people or a mechanism move it', 'held_or_thrown': None, 'dropped_or_toppled': 'S3', 'selects_at_most': 3},
        {'rung': 'massive', 'anchor': 'part of the building or the land', 'held_or_thrown': None, 'dropped_or_toppled': 'S4', 'selects_at_most': 4},
    ],
    'improvised_footprint': 'a dropped, toppled, swung or rolled object selects at most selects_at_most creatures inside its shape cap; against a mob each share is at most one member Vitality; once fallen it is not dropped again (T-06-8; revision I-075)',
    'falls_reference': {'owner': '10', '10_ft': 'S2', '20_ft': 'S3', '40_ft': 'S4', '80_ft': 'S5', 'harm_tags': ['harm.physical.crush'], 'lands': 'cond.prone'},
    'reactions': {
        'basic': [
            {'id': 'opportunity_strike', 'triggers': ['an engaged enemy leaves band.engaged by a plain Move', 'an engaged enemy makes a manipulate-trait beat other than with a weapon in hand', 'an engaged enemy stands from prone', 'with a reach weapon: an enemy Moves from close to engaged with you'],
             'effect': 'one melee Strike at that enemy; no repetition snag', 'avoided_by': ['Withdraw', 'Move-through at reach 2+', 'abilities that say so']},
            {'id': 'fend', 'trigger': 'an aimed attack is declared against you by an attacker you perceive', 'effect': 'a -2 engine snag on that attack', 'slot': 'slot.defense_reaction', 'priority_rank': 0,
             'forbidden_while': ['cond.surprised', 'cond.blinded (vs the unseen)', 'cond.restrained', 'cond.pinned', 'cond.stunned', 'cond.unconscious']},
            {'id': 'readied_beat', 'trigger': 'the observable trigger stated when Readying', 'effect': 'the readied one-action beat resolves; depth 0'},
        ],
        'depth': 'a reaction is depth 1 (fires no subscribers); a readied beat is depth 0',
        'adversary_defaults': {'T1': [], 'T2': ['opportunity_strike'], 'T3+': ['opportunity_strike', 'fend']},
        'companion_default': 'fend (or the reaction of its standing order)'},
    'multi_target': [
        {'shape': 'pierce', 'order': 1, 'selection_rule': 'the primary target, then each participant carrying flag.lined_up in the same line, nearest the source first', 'cap': 4, 'harm': 'full'},
        {'shape': 'burst', 'order': 2, 'selection_rule': 'the primary target or point, then each participant engaged with it, then each in its group; friend and foe', 'cap': 6, 'harm': 'full'},
        {'shape': 'cone', 'order': 3, 'selection_rule': "each participant at band.engaged with the source, then each at band.close in the primary target's group; friend and foe", 'cap': 4, 'harm': 'full', 'added_by': '06 (DL-06-15)'},
        {'shape': 'fork', 'order': 4, 'selection_rule': 'the primary target and one more eligible participant within band.close of it per extra target granted', 'cap': 5, 'harm': 'full'},
        {'shape': 'chain', 'order': 5, 'selection_rule': 'after the primary resolves, the nearest other participant within band.close of the last target; friend or foe', 'cap': 3, 'harm': 'one rung lighter at each leap'},
        {'shape': 'linger', 'order': 6, 'selection_rule': 'any participant that enters the named group or feature or ends its turn there, for the duration', 'cap': 5, 'harm': 'as the effect states'},
    ],
    'multi_target_total_cap': 6,
    'multi_target_ties': ['nearer the source by band', 'lower current Vitality', 'id'],
    'multi_target_rolls': {'aimed': 'one roll compared to each defense', 'resisted': 'each target rolls; a mob rolls once'},
    'mobs': {'min_members': 3, 'vitality': 'members x template Vitality, pooled; members_now = ceil(pool / member Vitality)',
             'actions': 2, 'reactions': 0, 'numbers_step': [{'members_now': '1-2', 'severity_steps': 0}, {'members_now': '3-5', 'severity_steps': 1}, {'members_now': '6+', 'severity_steps': 2}],
             'flanking': 'a mob never Flanks and never grants flag.flanked', 'shaped_effects': 'harm applies k times, k = members the shape would select (to its cap and members_now)',
             'conditions': 'whole mob only if a shape selected at least half of members_now; else one member is out (mob.<id>.member_out)',
             'swarm': {'flag': 'swarm: true', 'size': 'tiny', 'targets': 'everyone in one group, to four; one roll compared to each Guard',
                       'unshaped_harm_to_it': 'one rung lighter', 'shaped_harm_to_it': 'one rung heavier', 'immune_to': ['grapple', 'shove', 'flag.flanked', 'cond.prone']}},
    'morale': {
        'clock': {'id_pattern': 'clk.morale.<side>', 'kind': 'tug', 'visibility': 'sensed', 'owner': '06'},
        'thresholds': {'skittish': 4, 'steady': 6, 'resolute': 8, 'fearless': None},
        'read_from': "the side's leader, else its most numerous template (09: morale)",
        'tick_sources': [
            {'on': 'a member of the side is defeated', 'ticks': 1}, {'on': "the side's leader is defeated", 'ticks': 2},
            {'on': 'side strength first at or below half', 'ticks': 2, 'once': True}, {'on': 'side strength first at or below a quarter', 'ticks': 2, 'once': True},
            {'on': 'an individual member (not a mob) is first bloodied', 'ticks': 1},
            {'on': 'one blow deals 8 or more harm to a member', 'ticks': 1},
            {'on': 'cond.frightened applied to a member', 'ticks': 1, 'limit': 'once per round'},
            {'on': "the PC's Talk aimed at their will succeeds against the leader's Resolve defense", 'ticks': 'delivered_reach'},
            {'on': 'an effect ticking clk.morale.*', 'ticks': 'as stated'},
            {'on': 'the PC is first bloodied', 'ticks': -1}, {'on': 'the PC is Staggered', 'ticks': -2},
            {'on': 'a companion of the PC is defeated', 'ticks': -1}, {'on': 'reinforcements for the side arrive', 'ticks': -2},
            {'on': "the side's leader rallies (1 action; fortune check vs Moderate)", 'ticks': '-delivered_reach'},
        ],
        'omens': {'stirring': ['one of them glances back at the door', 'their shouting has gone quiet'],
                  'building': ['they give ground a step at a time', 'the big one looks to the others and none of them meet his eye'],
                  'imminent': ['one has already lowered his blade', 'they are calling to each other, and it is not orders']},
        'on_complete': {'effects': [E('eff.apply_condition', condition='cond.broken', severity='S3', duration='conflict', target='each member of the side that is not fearless')], 'interrupting': False, 'then': 'close'},
        'break_rows': [{'state': 'can get away', 'does': 'flee'}, {'state': 'cannot get away; thinking creature', 'does': 'yield'},
                       {'state': 'cannot get away; beast', 'does': 'cower'}, {'state': 'fearless', 'does': 'unaffected'}],
        'pc_yield_accepted_by_disposition': {'capture': True, 'rob': True, 'ransom': True, 'drive_off': True, 'leave': True, 'kill': False, 'drag_to_lair': False},
    },
    'objectives': ['defeat', 'kill', 'capture', 'rob', 'drive_off', 'escape', 'hold', 'reach', 'protect', 'delay'],
    'chase': {
        'fleeing_pc': {'escape': {'id': 'clk.escape', 'name': 'The way clear', 'kind': 'progress', 'visibility': 'public', 'segments': 6, 'start': 0},
                       'pursuit': {'id': 'clk.pursuit', 'name': 'They close in', 'kind': 'danger', 'visibility': 'public', 'segments': 8, 'start_by_band': {'band.close': 2, 'band.near': 1, 'band.far': 0}}},
        'pursuing_pc': {'quarry': {'id': 'clk.quarry_away', 'name': 'The quarry gets clear', 'kind': 'danger', 'visibility': 'public', 'segments': 6, 'start': 0},
                        'run_down': {'id': 'clk.run_down', 'name': 'Running it down', 'kind': 'progress', 'visibility': 'public', 'segments': 8, 'start_by_band': {'band.close': 2, 'band.near': 1, 'band.far': 0}}},
        'beats_per_chase_round': 1, 'requires_varied_approach': True, 'flight_stakes': 'risky', 'pursuing_stakes': 'safe unless the ground is dangerous',
        'threatened_cost': 'cost.time (ticks the opposing clock by U(severity))', 'alternate_cost': 'cost.footing',
        'other_side': {'check': 'fortune check: best of might or agility modifier + competence, against the round ground', 'reach': {'equal_pace': 'standard', 'slower': 'limited', 'faster': 'great'}},
        'band_implied_by_clock': {'under_half': 'band.far', 'half_or_more': 'band.near', 'one_from_full': 'band.close'},
        'caught': 'lead pursuer at band.engaged; the fleer gains flag.cornered; ordinary rounds resume',
        'hide': 'at a cover or veil feature with pursuit under half: Sneak reach 3+ completes the escape clock',
        'ground_tables': {
            'id': 'tbl.chase_ground', 'die': 'd6', 'no_immediate_repeat': True,
            'settlement': [{'range': 1, 'result': 'an open street', 'tier': 'easy'}, {'range': 2, 'result': 'a crowded lane', 'tier': 'moderate'},
                           {'range': 3, 'result': 'carts and stalls across the way', 'tier': 'moderate'}, {'range': 4, 'result': 'a wall or fence to get over', 'tier': 'moderate'},
                           {'range': 5, 'result': 'rooftops or a canal to leap', 'tier': 'hard'}, {'range': 6, 'result': 'a dead end (only Exert, Sneak or Force)', 'tier': 'hard'}],
            'wild': [{'range': 1, 'result': 'open ground', 'tier': 'easy'}, {'range': 2, 'result': 'thick brush', 'tier': 'moderate'},
                     {'range': 3, 'result': 'a stream or ditch to cross', 'tier': 'moderate'}, {'range': 4, 'result': 'a steep bank', 'tier': 'moderate'},
                     {'range': 5, 'result': 'a ravine, deadfall or bog', 'tier': 'hard'}, {'range': 6, 'result': 'broken ground in poor light', 'tier': 'hard'}],
            'indoors': [{'range': 1, 'result': 'a straight passage', 'tier': 'easy'}, {'range': 2, 'result': 'a stair, up or down', 'tier': 'moderate'},
                        {'range': 3, 'result': 'a door to get through and shut', 'tier': 'moderate'}, {'range': 4, 'result': 'a junction where the way must be chosen (Wits or Intellect allowed)', 'tier': 'moderate'},
                        {'range': 5, 'result': 'a gap, a pit, a collapsed stretch', 'tier': 'hard'}, {'range': 6, 'result': 'darkness without a light', 'tier': 'hard'}]},
    },
    'companion_command': {
        'cost': 1, 'cost_for_two_action_beat': 2, 'verb': 'verb.talk (named use: Command)', 'range': 'band.near; the companion must perceive the command',
        'rules': ['a companion has no actions of its own and one reaction', 'one commanded beat per Command, framed with the companion numbers',
                  'each companion keeps its own repetition window per PC turn', 'a commanded Help gives one Precision lever (01.14.8)',
                  'group command: one identical simple beat (Move, Defend, a standing order), never an attack-trait beat',
                  'uncommanded: it keeps its place, its hold and its standing order, and defends itself'],
        'standing_orders': [
            {'id': 'guard_me', 'keeps': "stays in the PC's group; moves with the PC", 'reaction': 'Intercept: takes one hit meant for the PC (eff.intercept)'},
            {'id': 'hold_him', 'keeps': 'a hold it has', 'reaction': 'a -2 engine snag on the first attempt to break free each round'},
            {'id': 'harry_that_one', 'keeps': 'engagement with the named enemy, following one band a round', 'reaction': 'Opportunity Strike against that enemy'},
            {'id': 'hold_this_ground', 'keeps': 'its place; flag.in_chokepoint if in one; screens whoever is behind it', 'reaction': 'Opportunity Strike against anyone passing'},
            {'id': 'stay_back', 'keeps': 'band.near from every enemy it can see, moving one band a round', 'reaction': 'Fend'},
        ]},
    'heavy_blows': {'definition': 'an adversary attack with base severity S4 or more, or any adversary attack with a shape', 'windup_actions': 1,
                    'when': 'on a turn before the turn of the blow', 'fact': 'windup.<adversary>.<attack>',
                    'spoiled_by': ['moved against its will', 'cond.prone', 'cond.dazed', 'cond.stunned', 'cond.blinded', 'harm of S3 or more from one hit'],
                    'narration': "the template's tell, in the turn of the windup; status line: winding up"},
    'attention': ['the participant its objective names', 'an enemy engaged with it (most harm dealt to it since its last turn first)',
                  'the enemy that dealt it the most harm since its last turn', 'the nearest enemy by band (the PC before a companion)', 'an engine roll among the tied'],
    'taunt': 'a successful Talk taunt adds harm-equivalent equal to twice the delivered reach to the attention score',
    'default_behaviors': [
        {'id': 'beh.default_melee', 'priority_list': [
            {'when': 'cond.broken', 'do': 'break row (06.11.5)'}, {'when': 'held (cond.grabbed or worse)', 'do': 'break free'},
            {'when': 'cond.prone', 'do': 'stand'}, {'when': 'a heavy blow is listed and no windup is held', 'do': 'windup'},
            {'when': 'not engaged with its target', 'do': 'move toward it (withdraw first if engaged elsewhere)'},
            {'when': 'engaged; an ally also engaged with the target; target not flanked', 'do': 'flank (once)'},
            {'when': 'always', 'do': 'strike the target'}]},
        {'id': 'beh.default_ranged', 'priority_list': [
            {'when': 'cond.broken', 'do': 'break row'}, {'when': 'an enemy is engaged with it', 'do': 'withdraw, then shoot'},
            {'when': 'no line to any enemy', 'do': 'move toward the nearest cover with a line'}, {'when': 'not loaded', 'do': 'reload'},
            {'when': 'target in cover and a second action remains', 'do': 'aim'}, {'when': 'a target is in reach', 'do': 'shoot the target'},
            {'when': 'always', 'do': 'defend'}]},
        {'id': 'beh.default_beast', 'priority_list': [
            {'when': 'cond.broken', 'do': 'break row'}, {'when': 'held', 'do': 'break free'},
            {'when': 'bloodied and not cornered and nerve is skittish', 'do': 'withdraw and flee'},
            {'when': 'not engaged', 'do': 'move to engage the target'}, {'when': 'target is prone or grabbed by it', 'do': 'strike'},
            {'when': 'it has a grab attack and the target is not held', 'do': 'grapple'}, {'when': 'always', 'do': 'strike the target'}]},
        {'id': 'beh.default_mob', 'priority_list': [
            {'when': 'cond.broken', 'do': 'break row'}, {'when': 'not engaged with its target', 'do': 'move to engage'},
            {'when': 'always', 'do': 'strike (numbers apply)'}]},
    ],
    'expressions': [
        {'id': 'bloodied', 'true_when': '0 < vitality.current and vitality.current * 2 <= vitality.max (a mob: its pool)'},
        {'id': 'helpless', 'true_when': 'cond.unconscious or cond.pinned, or cond.restrained with duration until_cleansed'},
        {'id': 'unaware', 'true_when': 'alertness toward y is unaware, or y holds flag.hidden toward x, or x carries cond.surprised or cond.unconscious'},
        {'id': 'engaged', 'true_when': 'an engagement link joins x and y'},
        {'id': 'outnumbered', 'true_when': 'enemies engaged with x number two or more'},
        {'id': 'defeated', 'true_when': "ch.07's disposition flag: out of the fight"},
        {'id': 'alone', 'true_when': 'no ally of x is a participant within band.near of it'},
        {'id': 'size_steps', 'value': "y's size rung minus x's"},
    ],
    'on_defeat_payload': ['defeated', 'frame_id', 'ability_id', 'harm_mode', 'manner (defeated | drive_off | yielded)'],
    'environment_anchors_ref': 'T-06-9 in 06-conflict.md (40 rows); compiled into anchors.yaml by ch.12',
    'reference_lines': {
        'note': 'used by 06-conflict-sim.py; PC Vitality and armor assumed (02/07/08 own); adversary lines inside 00.3.7 (09 owns)',
        'pc': [{'band': 1, 'attack': 5, 'guard': 14, 'vitality': 12, 'strike_base': 'S2', 'armor': 1}, {'band': 2, 'attack': 7, 'guard': 16, 'vitality': 14, 'strike_base': 'S2', 'armor': 1},
               {'band': 3, 'attack': 9, 'guard': 18, 'vitality': 16, 'strike_base': 'S3', 'armor': 2}, {'band': 4, 'attack': 11, 'guard': 19, 'vitality': 18, 'strike_base': 'S3', 'armor': 2},
               {'band': 5, 'attack': 12, 'guard': 20, 'vitality': 20, 'strike_base': 'S4', 'armor': 3}],
        'adversary': [{'band': 1, 'attack': 2, 'guard': 12, 'vitality': 5, 'harm': 'S2', 'reduction': 0, 'nerve': 'skittish', 'tempo_dc': 10},
                      {'band': 2, 'attack': 5, 'guard': 15, 'vitality': 12, 'harm': 'S2', 'reduction': 0, 'nerve': 'steady', 'tempo_dc': 11},
                      {'band': 3, 'attack': 7, 'guard': 17, 'vitality': 18, 'harm': 'S3', 'reduction': 1, 'nerve': 'steady', 'tempo_dc': 12},
                      {'band': 4, 'attack': 10, 'guard': 20, 'vitality': 26, 'harm': 'S3', 'heavy_blow': 'S4', 'reduction': 2, 'nerve': 'resolute', 'tempo_dc': 13},
                      {'band': 5, 'attack': 12, 'guard': 22, 'vitality': 40, 'harm': 'S4', 'heavy_blow': 'S5', 'reduction': 2, 'nerve': 'resolute', 'tempo_dc': 14}]},
    'basis': ['06.1-06.15', 'C:P9', 'C:P14', 'INV-11', 'R1 #7', 'R3 #7', 'DL-06-01..26'],
}

CONFLICT_HEADER = """# data/conflict.yaml
# Purpose: every table of chapter 06 as data: the action economy, repetition, tempo, range bands, positional
#   flags, defenses, weapon weights and properties, mastery, called shots, improvised objects, reactions, shapes
#   for multi-target effects, mobs, the morale clock, objectives, chase clocks and ground tables, the companion
#   command, heavy blows, the attention rule, default behavior lists, state expressions, and the reference lines
#   the simulation used.
# Owner: 06-conflict. Schema: data/SCHEMAS.md#conflictyaml (required keys: economy, range_bands, positional_flags,
#   repeated_attack, multi_target, morale {thresholds}, companion_command); every other key is an optional field
#   added by ch.06 and documented in 06's Tables section.
# This file is one record, not a list of entries; ids inside it (band.*, flag.*, clk.*, beh.*, tbl.*) are globally
#   unique. lifecycle: provisional for the whole file.
# Generated and validated by rules/_process/simulation/06-gen_data06.py.
# Basis: [06] [C:P9] [C:P14] [INV-11] [R1 #7] [R3 #7, 06.2-06.10] [R7 5 Ex.7] [DL-06-01..26]"""

EFFECTS = {'schema_version': 1, 'blocks': [{'owner': '06', 'entries': [
    {'id': 'eff.06.fewer_actions', 'op': 'economy', 'regime': 'additive',
     'params': {'actions_delta': '-3..-1 (never positive)', 'minimum_actions': '0..1', 'reactions_delta': '-1..0'},
     'text': '{actions_delta} actions each turn (never fewer than {minimum_actions}); {reactions_delta} reactions.',
     'why_not_core': 'no core effect removes actions; eff.reaction_grant only adds a reaction. INV-11 forbids adding actions, not removing them; substrate.yaml lists economy with reactions_delta only (Interface request to 00, item 1)',
     'lifecycle': 'provisional', 'basis': ['06.1.2', 'INV-11', 'T-00-15 (cond.dazed, cond.stunned)', 'DL-06-24']},
    {'id': 'eff.06.pace', 'op': 'modify', 'quantity': 'speed', 'family': 'adjust', 'regime': 'additive',
     'params': {'amount': "-1..1, or a mount's pace", 'applies_when': 'expr'},
     'text': 'Pace {amount}: each band transition costs one action more (negative) or the costs of pace 2 apply (positive).',
     'why_not_core': 'the core library has no modify on the quantity speed (T-00-13 names it as ch.06 bands per move action)',
     'lifecycle': 'provisional', 'basis': ['06.3.3', 'T-00-13', 'DL-06-24']},
    {'id': 'eff.06.grant_snag', 'op': 'lever', 'regime': 'additive',
     'params': {'type': 'precision|protective|amplifying', 'sign': 'snag', 'to': 'who suffers it (those acting against the bearer, or the bearer)', 'fact': 'str', 'applies_when': 'expr', 'duration': 'duration'},
     'text': 'Counts as an established {type} snag, citing {fact}, {applies_when}.',
     'why_not_core': 'eff.grant_lever creates lever facts only; cover, concealment, Defend, Fend and a prone target at range need the mirror',
     'lifecycle': 'provisional', 'basis': ['00.3.9', '06.3.6', '06.4.7', 'DL-06-24']},
    {'id': 'eff.06.internal_harm', 'op': 'harm', 'regime': 'independent_trigger', 'hook': 'on_turn_end',
     'params': {'vitality_per_stack': '1', 'harm_tags': '[tag]', 'no_reduction': True},
     'text': 'At the end of its turn the bearer loses {vitality_per_stack} Vitality per stack ({harm_tags}); no reduction applies.',
     'why_not_core': "eff.deal_harm passes through the receiver's reduction; bleeding and choking are inside the armor",
     'lifecycle': 'provisional', 'basis': ['06.7 (cond.bleeding, cond.choking)', '05 uses apply_harm(no_reduction: true) for strain', 'DL-06-24']},
]}]}

EFFECTS_HEADER = """# data/contrib/effects.06.yaml
# Purpose: ch.06's owner-block for data/effects.yaml. Four definitions, each added because no core effect with
#   parameters expresses the mechanic (PR-00-8), each using one of the 20 closed operations and one regime.
#   Everything else in conditions.yaml and conflict.yaml references the core library.
# Owner: 06-conflict. Schema: data/SCHEMAS.md#effectsyaml. Decision: DL-06-24."""

BOUNDARIES = {'schema_version': 1, 'blocks': [{'owner': '06', 'handlers': [
    {'id': 'h.06.tempo_setup', 'boundary': 'conflict_start', 'phase': 9, 'interrupting': False,
     'effect': "list participants, sides and objectives; set bands, groups and flags; apply cond.surprised; create the morale clock; roll the PC's tempo check and fix the order", 'rule_id': '06.2.1; 06.2.2; PR-06-1', 'status': 'reserved by 00; defined'},
    {'id': 'h.06.turn_effects', 'boundary': ['turn_start', 'turn_end'], 'phase': 2, 'interrupting': False,
     'effect': "turn_start: refresh the owner's reaction, lapse an unfired readied beat, expire defending and fend facts, apply turn_start periodics; turn_end: apply turn_end periodics (bleeding, burning, choking), count down durations in the owner's turns, decay cond.frightened one rung", 'rule_id': '06.1.8', 'status': 'reserved by 00; defined'},
    {'id': 'h.06.ongoing_harm', 'boundary': 'round', 'phase': 2, 'interrupting': False,
     'effect': 'apply periodic effects of the place (hazard features: a burning room, rising water) to those in them', 'rule_id': '06.2.3', 'status': 'reserved by 00; defined'},
    {'id': 'h.06.chase_round', 'boundary': 'round', 'phase': 5, 'interrupting': False,
     'effect': "while a chase runs: the other side's fortune check against the round's ground; tick its clock; completion effects", 'rule_id': '06.12.4; PR-06-8', 'status': 'added'},
    {'id': 'h.06.diminishing_window', 'boundary': 'round', 'phase': 9, 'interrupting': False,
     'effect': "lower each target's control counter by one if it carried no control condition this round", 'rule_id': '06.7.4', 'status': 'reserved by 00; defined'},
    {'id': 'h.06.objective_check', 'boundary': 'round', 'phase': 9, 'interrupting': False,
     'effect': 'test the end conditions of 06.13.1 (also run after any defeat, break, yield, truce or clock completion); mark conflict_end when one holds', 'rule_id': '06.13.1', 'status': 'added'},
    {'id': 'h.06.clear_conflict_state', 'boundary': 'conflict_end', 'phase': 1, 'interrupting': False,
     'effect': 'clear bands, links, groups and conflict-only flags; end conflict-duration conditions and effects; end stances; end defending, fend, aim, windup, tempo and momentum facts; reset control counters; close morale and chase clocks', 'rule_id': '06.13.4; PR-06-10', 'status': 'reserved by 00; defined'},
]}]}

BOUNDARIES_HEADER = """# data/contrib/boundaries.06.yaml
# Purpose: ch.06's owner-block for data/boundaries.yaml. The five handlers 00 reserved for ch.06 are DEFINED in 06
#   (rule ids below) and restated here with their rule ids; two handlers are added.
# Owner: 06-conflict. Schema: data/SCHEMAS.md#boundariesyaml. Phases per 00.7.5."""


def main():
    os.makedirs(C, exist_ok=True)
    dump(os.path.join(D, 'conditions.yaml'), COND_HEADER, {'schema_version': 1, 'conditions': CONDITIONS, 'blocks': []})
    dump(os.path.join(D, 'conflict.yaml'), CONFLICT_HEADER, CONFLICT)
    dump(os.path.join(C, 'effects.06.yaml'), EFFECTS_HEADER, EFFECTS)
    dump(os.path.join(C, 'boundaries.06.yaml'), BOUNDARIES_HEADER, BOUNDARIES)

    # ---------------- validation
    def load(p):
        with io.open(p, encoding='utf-8') as f:
            return yaml.safe_load(f)
    sub = load(os.path.join(D, 'substrate.yaml'))
    core = {e['id'] for e in load(os.path.join(D, 'effects.yaml'))['core']}
    mine = {e['id'] for e in load(os.path.join(C, 'effects.06.yaml'))['blocks'][0]['entries']}
    conds = load(os.path.join(D, 'conditions.yaml'))['conditions']
    conf = load(os.path.join(D, 'conflict.yaml'))
    ids = [c['id'] for c in conds]
    errs = []
    for r in sub['reserved_ids']['conditions']:
        if r not in ids:
            errs.append('missing reserved condition ' + r)
    if len(ids) != len(set(ids)):
        errs.append('duplicate condition id')
    stackings = {x['id'] for x in sub['condition_stacking']}
    cats = set(sub['condition_categories'])
    req = ['id', 'name', 'tags', 'category', 'severity', 'severity_variable', 'stacking', 'max_stacks', 'escalates_to',
           'duration', 'decay', 'cleanse', 'exclusion_group', 'priority_rank', 'neutralizes', 'diminishing', 'modifies',
           'periodic', 'on_apply', 'on_remove', 'visible', 'narration_may_not_imply', 'lifecycle', 'basis']

    def refs(c):
        for k in ('modifies', 'on_apply', 'on_remove'):
            for e in c[k]:
                yield e['effect_id']
        for e in c['periodic']:
            yield e['effect_id']
    for c in conds:
        for k in req:
            if k not in c:
                errs.append('%s lacks %s' % (c['id'], k))
        if c['stacking'] not in stackings:
            errs.append('%s bad stacking' % c['id'])
        if c['category'] not in cats:
            errs.append('%s bad category' % c['id'])
        if c['severity'] not in ('S1', 'S2', 'S3', 'S4', 'S5'):
            errs.append('%s bad severity' % c['id'])
        for n in c['neutralizes']:
            if n not in ids:
                errs.append('%s neutralizes unknown %s' % (c['id'], n))
        if c['escalates_to'] and c['escalates_to']['condition'] not in ids:
            errs.append('%s escalates to unknown' % c['id'])
        for e in refs(c):
            if e not in core and e not in mine:
                errs.append('%s references unknown effect %s' % (c['id'], e))
    for b in sub['reserved_ids']['range_bands']:
        if b not in [x['id'] for x in conf['range_bands']]:
            errs.append('missing band ' + b)
    for fl in sub['reserved_ids']['positional_flags']:
        if fl not in [x['id'] for x in conf['positional_flags']]:
            errs.append('missing flag ' + fl)
    for k in ('economy', 'range_bands', 'positional_flags', 'repeated_attack', 'multi_target', 'morale', 'companion_command'):
        if k not in conf:
            errs.append('conflict.yaml lacks ' + k)
    ops = {o['id'] for o in sub['operations']}
    for e in load(os.path.join(C, 'effects.06.yaml'))['blocks'][0]['entries']:
        if e['op'] not in ops:
            errs.append('effect %s bad op' % e['id'])
    hs = load(os.path.join(C, 'boundaries.06.yaml'))['blocks'][0]['handlers']
    if sum(m['cap'] for m in conf['multi_target']) <= 0 or conf['multi_target_total_cap'] != 6:
        errs.append('multi-target caps')
    print('conditions: %d (%d reserved by 00, %d added); control group: %d' % (
        len(conds), sum(1 for c in conds if c['reserved_by_00']), sum(1 for c in conds if not c['reserved_by_00']),
        sum(1 for c in conds if c['diminishing'])))
    print('conflict.yaml keys: %d; flags: %d; bands: %d; action-cost rows: %d; shapes: %d; weapon weights: %d; properties: %d' % (
        len(conf), len(conf['positional_flags']), len(conf['range_bands']), len(conf['economy']['action_costs']),
        len(conf['multi_target']), len(conf['weapon_weights']), len(conf['weapon_properties'])))
    print('contrib effects: %d; handlers: %d' % (len(mine), len(hs)))
    if errs:
        print('ERRORS:')
        for e in errs:
            print('  ' + e)
        sys.exit(1)
    print('validation: OK')


if __name__ == '__main__':
    main()
