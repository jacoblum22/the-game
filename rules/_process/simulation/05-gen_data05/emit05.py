# emit05.py -- writes chapter 05's data files from the validated tables (called by gen_data05.py --emit).
import os, collections, yaml, re

ABS_PRINCIPLE = {
    'ab.abs_predators_nose': "Read the world by scent as a hunting beast does.",
    'ab.abs_thick_hide': "Carry a beast's hide under your own skin.",
    'ab.abs_pounce': "Close on prey in one spring.",
    'ab.abs_venom_gland': "Carry a venom in your own strike.",
    'ab.abs_night_eyes': "See in the dark as a night hunter does.",
    'ab.abs_wall_crawl': "Cling to a surface as a crawling thing does.",
    'ab.abs_gills': "Breathe water as a water-dweller does.",
    'ab.abs_grave_chill': "Carry the cold of the grave in your strike.",
    'ab.abs_deathless_calm': "Feel fear as the dead feel it.",
    'ab.abs_life_drink': "Take strength from the life you end.",
    'ab.abs_ghost_step': "Pass a body through what is solid.",
    'ab.abs_glamour_skin': "Wear a seeming over your own face.",
    'ab.abs_spirit_sight': "See the spirits a place holds.",
    'ab.abs_hellfire_blood': "Carry a fiend's fire in your blood.",
    'ab.abs_dread_gaze': "Put a fiend's terror into a look.",
    'ab.abs_stone_flesh': "Turn your flesh to stone for a time.",
    'ab.abs_tireless': "Go on without the rest a living body needs.",
    'ab.abs_ember_heart': "Carry a living fire where your heart is.",
    'ab.abs_rime_breath': "Breathe out a killing cold.",
    'ab.abs_stone_grip': "Grip with the strength of stone.",
    'ab.abs_storm_step': "Move as wind moves.",
    'ab.abs_dragon_breath': "Breathe out a dragon's element.",
    'ab.abs_scale_ward': "Wear scales under your skin.",
    'ab.abs_acid_touch': "Carry a dissolving touch.",
    'ab.abs_spore_cloud': "Loose a cloud of choking spores.",
    'ab.abs_rooted': "Hold to the ground as a rooted thing does.",
    'ab.abs_alien_mind': "Think in a shape no mind can easily grip.",
}


class Dumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def _rep_dict(d, data):
    flow = None
    if 'effect_id' in data or ('rank' in data and 'allowance' in data) or ('what' in data and 'needs' in data):
        flow = True
    return d.represent_mapping('tag:yaml.org,2002:map', data.items(), flow_style=flow)


Dumper.add_representer(collections.OrderedDict, _rep_dict)
Dumper.add_representer(dict, _rep_dict)


def dump(obj):
    return yaml.dump(obj, Dumper=Dumper, sort_keys=False, default_flow_style=None, width=100000, allow_unicode=True)


def write(path, header, body):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(header.rstrip('\n') + '\n\n' + body)
    print('wrote', path, os.path.getsize(path), 'bytes')


def mirror_absorbed(root):
    ga = yaml.safe_load(open(os.path.join(root, 'data', 'gen_absorb.yaml'), encoding='utf-8'))
    out = []
    for p in ga['pool']:
        active = p['activation'] == 'active'
        e = collections.OrderedDict()
        e['id'] = p['id']
        e['name'] = p['name']
        e['kind'] = 'ability'
        e['tags'] = ['deed.lore.bestiary.monsters'] + p['gate_tags']
        e['min_tier'] = p['min_tier']
        e['mod_group'] = 'abs_' + p['mod_group']
        e['slot_class'] = 'acquired'
        e['mirror_of'] = 'gen_absorb.yaml#pool/' + p['id']
        e['form'] = 'absorbed power (04.10): effects, tiers, cost and limits are ch.04\'s and are read from the mirrored entry'
        e['activation'] = p['activation']
        e['timing'] = 'beat' if active else 'passive'
        e['regime'] = 'see the mirrored entry\'s effects (each effect carries its own regime in effects.yaml)'
        e['principle'] = ABS_PRINCIPLE[p['id']]
        e['scope'] = p['text']
        e['limitation'] = 'Applies only while slotted in the acquired partition (05.2.7) by a holder of lic.call.taking who is not suspended (04.10.1).'
        e['weakness'] = {'text': "While any power of this creature branch is slotted, the branch's bane applies (gen_absorb.yaml#banes).", 'effect': 'gen_absorb.yaml#banes'}
        e['excludes'] = [dict(what='any use beyond the literal text', needs='a stretch (actives only), or another license')]
        e['attribute'] = 'by_method'
        e['check'] = {'mode': 'per the mirrored entry'}
        e['cost'] = p.get('cost', {'focus': 0})
        e['limits'] = p.get('limits')
        e['effects'] = 'gen_absorb.yaml#pool/%s/tiers (the tier the generator gave; a higher tier replaces the lower, INV-13)' % p['id']
        e['ranks'] = []
        e['crude_fallback'] = 'none'
        e['stretch'] = dict(dc_shift=5, cost_add=1, reach_cap='limited', within='principle') if active else None
        e['emulate'] = None
        e['acquisition_paths'] = [dict(type='recognition', detail='the Taking (04.10.2), by a Devourer holding lic.call.taking; gen.absorb', clock=None, requires='call.devourer, not suspended')]
        e['flares'] = []
        e['narration_may_not_imply'] = ["a power the generated output does not hold", "a weakness, appetite or change of nature beyond the bane's literal text", "the creature's mind or memories"]
        e['budget'] = "not budgeted here: ch.04 authors these entries; they are costed by 04.10.4's three separate costs (Focus per Taking, a slot, a bane)"
        e['source'] = 'gen.absorb'
        e['lifecycle'] = 'provisional'
        e['basis'] = ['04.10.5', '04 Interface request 8', '05.2.6', 'DL-05-05']
        out.append(dict(e))
    return out


def emit(abilities, stats, EFF05, EU_TABLE, TAGS, ROOT):
    import lic_training, rites05, comp05, gen_data05 as G
    DATA = os.path.join(ROOT, 'data')
    os.makedirs(os.path.join(DATA, '..', '_process', 'merged-contrib'), exist_ok=True)
    errs = []
    # composite-key flags come from the composites table
    ids = {a['id'] for a in abilities}
    for k in comp05.COMPOSITE_KEY_ABILITIES:
        if k not in ids:
            errs.append('composite key %s is not an ability' % k)
    for a in abilities:
        if a['id'] in comp05.COMPOSITE_KEY_ABILITIES:
            a['composite_key'] = True
        elif 'composite_key' in a:
            del a['composite_key']
    absorbed = mirror_absorbed(ROOT)
    n_pool = sum(1 for a in abilities if 'requires_conduct' not in a)
    n_oath = sum(1 for a in abilities if 'requires_conduct' in a)
    total = len(abilities) + len(absorbed)

    # ------------------------------------------------ abilities.yaml ------------------------------------------------
    head = """# data/abilities.yaml
# Purpose: THE shared ability pool (constitution P5: a calling hands out no ability list of its own). Every entry
#   is a license with mechanics (00.12.1), tagged by the deed or conduct it is evidence of, carrying a minimum
#   tier. Calling tiers grant PICKS into the calling partition from this pool, gated by the calling's tags
#   (04.8.4); the same entries may be learned into the acquired partition (05.8.5). %d entries: %d in the
#   tag-gated pool (covering all 81 level-2 deed tags), %d oath-gated by conduct axis and pole, %d mirrors of
#   ch.04's absorbable powers (slot_class acquired).
# Owner: 05-abilities-focus-magic (T-00-19). Rules: 05-abilities-focus-magic.md. GENERATED and validated by
#   rules/_process/simulation/05-gen_data05/gen_data05.py from individually authored tables (ab_*.py): ids, tags, effect
#   ids, hooks, slots, conditions, bands, flags, duration forms, the eight-form grammar, text lint (SG-15,
#   T-00-22), ch.04's coverage requests and the power budget of every rank (05.11) are checked mechanically.
# Schema: data/SCHEMAS.md#abilitiesyaml (License fields + activation, regime, effects, cost, limits, slot_class,
#   limitation, weakness, cost_text, narration_may_not_imply, principle, stretch, emulate). Optional fields added
#   by ch.05 (T-05-2): min_tier, mod_group, form, timing, hook, when, slot, rides, check, ranks, refresh_on,
#   flares, spread, composite_key, dictates_choice, requires_conduct, conduct_pole, replaces, mirror_of, budget.
# Reading an entry: `scope`, `effects`, `cost` and `limits` at the top are RANK 1; `ranks` holds each rank as a
#   complete restatement (05.3.9: rank = min(highest authored, 1 + floor((calling tier - min_tier) / 2)); an
#   ability held in the acquired partition is rank 1). `emulate` is null on abilities: emulation is licensed by
#   the training license of the ability's first tag (licenses.yaml). `crude_fallback` is that license's.
# Basis: [C:P5] [C:V] [C:VI] [C:VII] [C:P6] [C:P9] [C:P10] [C:P12] [00.10] [00.12] [R1 05, M-17..M-22]
#   [R2 05, #3, #4, #8] [R3 05.1-05.16, #2, #3, #12, #13] [R4 9 05] [04.8.4] [DL-05-01..DL-05-30]""" % (total, n_pool, n_oath, len(absorbed))
    const = collections.OrderedDict()
    const['schema_version'] = 1
    const['lifecycle'] = 'provisional'
    const['slots'] = {'ceiling': 20, 'partitions': {'calling': 12, 'acquired': 4, 'equipped': 4}, 'shelf': 4,
                      'reslot_at': 'rest_long (quality full or partial)', 'bind_equipped_at': 'breather outside conflict, or the equip action',
                      'one_of_each': ['one instance per ability id', 'one held ability per mod_group across calling and acquired', 'one running effect per behavioral slot', 'one sustained working'],
                      'provisional': {'non_pick': 'permanent at the first reflection after use in 3 different scenes; shelved at the second season boundary otherwise'}}
    const['forms'] = [{'id': k.lower(), 'regime': v['regime'], 'timings': sorted(v['timings'])} for k, v in G.FORMS.items()]
    const['timings'] = {'beat': 'the activation is the declared beat', 'rider': 'attaches to the holder\'s own beat; one rider per beat', 'reaction': 'on its hook, uses the holder\'s reaction (06)', 'trigger': 'on its hook, from the holder\'s own resolved beat or a boundary; no action', 'passive': 'applies whenever its applies_when holds'}
    const['rank_rule'] = "rank = min(highest authored rank, 1 + floor((holding calling's tier - min_tier) / 2)); acquired partition: rank 1; equipped: the item's stated rank"
    const['recharge_types'] = [
        {'id': 'at_will', 'form': 'cost.focus 0, limits null'}, {'id': 'focus_only', 'form': 'cost.focus 1-4, limits null'},
        {'id': 'per_round', 'form': '{per: round}', 'handler': 'h.05.round_recharge'}, {'id': 'per_conflict', 'form': '{per: conflict_end}', 'handler': 'h.05.conflict_recharge'},
        {'id': 'per_scene', 'form': '{per: scene_end}', 'handler': 'h.05.scene_recharge'},
        {'id': 'per_rest', 'form': '{per: rest_short | rest_long | day}', 'handler': 'h.05.rest_recharge / h.05.day_recharge'},
        {'id': 'once', 'form': '{per: never}', 'handler': None}]
    const['refresh_ladder'] = ['round', 'conflict_end', 'scene_end', 'rest_short', 'rest_long']
    const['focus'] = {
        'max': {'formula': 'base + T_high + breadth, clamped to 12', 'base': 'set by ch.02 in 3..5 (reference 4)', 'T_high': "highest tier among held, unsuspended callings (0..5), counting a consolidated calling's specialties at their tier_reached (04.8.5)", 'breadth': '+1 per other held calling at tier 3+, at most 3', 'cap': 12},
        'cost_bands': [{'focus': 0, 'name': 'knack', 'min_tier': 1}, {'focus': 1, 'name': 'lesser', 'min_tier': 1}, {'focus': 2, 'name': 'greater', 'min_tier': 1}, {'focus': 3, 'name': 'grand', 'min_tier': 3}, {'focus': 4, 'name': 'pinnacle', 'min_tier': 5}],
        'cost_order': ['base (active rank)', 'x emulate.cost_mult (0 becomes 1)', '+ stretch.cost_add', '+1 per flare', '+1 relic surcharge', 'adjust effects (reductions at most -1, never below 1 if the base was above 0; increases at most +2)', 'clamp: above 6 is not payable'],
        'activation_max': 6,
        'spent': {'when': 'focus.current = 0', 'effects': ['sustained workings end', 'engine-applied Precision snag (-2) on trait.action.concentrate beats', 'no flare, no push'], 'ends': 'focus.current >= 1'},
        'overdraw': {'harm_by_shortfall': {1: 'S2', 2: 'S3', 3: 'S4'}, 'harm_tags': ['harm.mind.strain'], 'lethal': False, 'reduction_applies': False, 'adds': 'one stack of cond.exhausted until_rest:rest_long', 'max_between_long_rests': 3, 'refused_when': 'it would bring Vitality to 0 or below, or the actor is Staggered or Dying', 'not_for': ['push', 'flare', 'the Taking']},
        'push': {'license': 'lic.focus.push', 'cost': 1, 'choose': ['reach +1 rung', 'stakes -1 rung'], 'requires': 'competence above the PC floor on the beat\'s primary deed tag or an ancestor', 'per_beat': 1, 'counts_as_lever': False},
        'flares': [
            {'id': 'hard', 'cost': 1, 'effect': 'harm dealt or condition applied is one severity rung heavier'}, {'id': 'far', 'cost': 1, 'effect': 'range one band further'},
            {'id': 'wide', 'cost': 1, 'effect': 'one more target the ability\'s targeting rule allows (inside the spread cap)'},
            {'id': 'lasting', 'cost': 1, 'effect': 'duration one step longer: rounds:N -> scene; scene or conflict -> until_rest:rest_short; intervals:N -> hours:N'},
            {'id': 'quiet', 'cost': 1, 'effect': 'loses trait.sense.loud, .audible and .visible, and the flare tell'}, {'id': 'sure', 'cost': 1, 'effect': 'a Precision lever on its aimed check, or a Precision snag on each resist check'}],
        'flare_rules': {'per_activation': {'trained': 1, 'expert': 1, 'master': 2}, 'tell': 'a flared activation is trait.sense.visible and trait.sense.audible unless Quiet is taken', 'miscast': 'a flared spell that critically fails miscasts one rung heavier', 'refused': ['cost would pass 6', 'while Spent', 'on a stretch or an emulation']},
        'recovery': {
            'breather': {'full': 1, 'partial': 1, 'interrupted': 0, 'limit': 'at most 2 Focus-restoring breathers between short rests'},
            'rest_short': {'full': 'ceil(max / 2)', 'partial': 'ceil(max / 4)', 'interrupted': 1, 'limit': 'the first 2 short rests of a day; later ones restore as a breather'},
            'rest_long': {'full': 'to max', 'partial': 'to ceil(3 * max / 4), never lowering current', 'interrupted': 'as rest_short partial'},
            'resonant_place': '+1 on a breather or short rest at a place whose resonance matches a held calling key or ability first tag'},
        'generation': {'family_triggers': 'callings.yaml#families[].focus_trigger (confirmed unchanged: 1 Focus; once per scene from tier 2, twice from tier 4)', 'cap_per_scene': 3, 'counts': ['family triggers', 'composites', 'boons', 'Reserve-form abilities']},
        'consumables': {'cap_between_long_rests': 4},
        'reserve': {'license': 'lic.focus.reserve', 'vessel': 'one item tagged item.tool.implement, made by the holder or kept for a season', 'capacity': {'T_high 0-2': 2, 'T_high 3-4': 3, 'T_high 5': 4}, 'bank': 'declare n at a full rest_long; focus.max is n lower until the next completed rest_long; then n enters the reserve unless the holder was Spent in between', 'draw': 'free activity, vessel in hand or worn; 1 to 1; never above focus.max'},
        'drain': {'units': 'U(severity)', 'cap_per_scene': 4, 'emptying_powers': 'threat band 4-5 adversaries only, named in their tells (09)'},
        'healing_cap': {'per_recipient_between_long_rests': 2, 'counts': 'every ability, rite or item effect that restores Vitality'}}
    const['magic'] = {
        'branches': [
            {'branch': 'deed.arcane', 'source': 'formula', 'attribute': 'intellect', 'limitation': ['trait.action.speech', 'trait.action.manipulate'], 'weakness': 'countered and unwoven by arcane warding; audible when cast', 'miscast': 'backlash'},
            {'branch': 'deed.divine', 'source': 'a keeper', 'attribute': 'presence', 'limitation': ['trait.action.speech', "the keeper's sign (item.tool.implement) worn or in hand", "the keeper's regard (05.7.4)"], 'weakness': 'a Precision snag where a fact marks the place desecrated', 'miscast': 'silence'},
            {'branch': 'deed.primal', 'source': 'the living world', 'attribute': 'resolve', 'limitation': ['the source present in the scene (05.7.3)'], 'weakness': 'G4 on dead ground', 'miscast': 'debt'}],
        'miscast': {
            'when': ['an aimed working critically fails', 'a resisted working is critically resisted by every target (severity S1)'],
            'severity': {'safe': 'S1', 'risky': 'S3', 'dire': 'S4', 'plus_one_rung_if': ['flared', 'emulated'], 'max': 'S4'},
            'replaces': 'the critical failure\'s heavier menu cost (01.9.2)',
            'backlash': {'S1': [{'effect_id': 'eff.deal_harm', 'params': {'severity': 'S1', 'harm_tags': ['harm.arcane.raw'], 'target': 'self'}}],
                         'S2': [{'effect_id': 'eff.deal_harm', 'params': {'severity': 'S2', 'harm_tags': ['harm.arcane.raw'], 'target': 'self'}}],
                         'S3': [{'effect_id': 'eff.deal_harm', 'params': {'severity': 'S3', 'harm_tags': ['harm.arcane.raw'], 'target': 'self'}}, {'effect_id': 'eff.apply_condition', 'params': {'condition': 'cond.dazed', 'severity': 'S1', 'duration': 'rounds:1', 'target': 'self'}}],
                         'S4': [{'effect_id': 'eff.deal_harm', 'params': {'severity': 'S4', 'harm_tags': ['harm.arcane.raw'], 'target': 'self'}}, {'effect_id': 'eff.apply_condition', 'params': {'condition': 'cond.dazed', 'severity': 'S1', 'duration': 'rounds:1', 'target': 'self'}}, {'effect_id': 'eff.05.end_working', 'params': {'target': 'every arcane working the caster is sustaining', 'condition_or_category': 'magical'}}]},
            'silence': {'S1': [{'effect_id': 'eff.restrict', 'params': {'forbid': {'licenses': ['the miscast ability']}, 'target': 'self', 'duration': 'scene'}}],
                        'S2': [{'effect_id': 'eff.restrict', 'params': {'forbid': {'licenses': ['the miscast ability']}, 'target': 'self', 'duration': 'days:1'}}],
                        'S3': [{'effect_id': 'eff.restrict', 'params': {'forbid': {'licenses': ['every spell of the miscast ability\'s school']}, 'target': 'self', 'duration': 'days:1'}}],
                        'S4': [{'effect_id': 'eff.restrict', 'params': {'forbid': {'licenses': ['every divine spell the caster holds']}, 'target': 'self', 'duration': 'until_cleansed'}}],
                        'ends': {'S2': 'the next day boundary (dawn)', 'S3': 'the next day boundary (dawn)', 'S4': 'rit.purification, or the second day boundary'}},
            'debt': {'S1': [{'effect_id': 'eff.focus_cost_step', 'params': {'amount': 1, 'applies_when': "the caster's next working with a first tag under deed.primal, this scene"}}],
                     'S2': [{'effect_id': 'eff.focus_cost_step', 'params': {'amount': 1, 'applies_when': 'deed_tag under deed.primal, until scene_end'}}],
                     'S3': [{'effect_id': 'eff.focus_cost_step', 'params': {'amount': 1, 'applies_when': 'deed_tag under deed.primal, until an offering is made'}}],
                     'S4': [{'effect_id': 'eff.focus_cost_step', 'params': {'amount': 1, 'applies_when': 'deed_tag under deed.primal, until an offering is made'}}, {'effect_id': 'eff.apply_condition', 'params': {'condition': 'cond.exhausted', 'severity': 'S1', 'duration': 'until_rest:rest_long', 'target': 'self'}}],
                     'offering': 'a free activity at a breather where the source is present: 1 supply, or an item, or an hour of tending the place'}},
        'dispel': {'against': "the effect's stored effect DC", 'by_delivered_reach': {1: 'suppressed for rounds:3', 2: 'ended', 3: 'ended, and the maker\'s signature learned', 4: 'ended, with one more effect of the same maker in the scene'}},
        'sense': {'range': 'band.near', 'against': 'the stored effect DC if concealed, else moderate', 'own_branch_only': True}}
    const['learning'] = {'clock': {'kind': 'project', 'visibility': 'public', 'segments_by_min_tier': {1: 6, 2: 6, 3: 8, 4: 8, 5: 12}},
                         'tick_sources': [{'on': 'a successful emulation', 'ticks': 'delivered_reach'}, {'on': 'a training week with a mentor who holds it', 'ticks': 3}, {'on': 'a week of study from a text that teaches it', 'ticks': 2}, {'on': 'a week of practice alone after witnessing it', 'ticks': 1}],
                         'requires': "the training license of the ability's first tag at a grade whose technique cap covers its min_tier", 'grants_into': 'acquired partition (or the shelf), rank 1, provisional'}
    const['budget'] = {
        'allowance': 'tier + 2 x focus + recharge + timing + limitation + weakness + other_cost',
        'terms': {'tier': 'min_tier + 2 x (rank - 1) + 1', 'focus': '2 per Focus point of the rank\'s cost',
                  'recharge': {'none or per round': 0, 'per conflict or scene': 1, 'per rest_short': 2, 'per rest_long or day': 3, 'once ever': 4, 'note': 'minus 1 per use beyond the first in the period, minimum 0'},
                  'timing': {'beat': 2, 'reaction': 1, 'rider': 0, 'trigger': 0, 'passive': 0},
                  'limitation': '+1 per narrowing clause beyond the form\'s default, at most 2', 'weakness': '+1 (a condition or snag on the holder) or +2 (loss of senses, double harm)', 'other_cost': '+1 per component, interval or S1 of Vitality paid; +2 for S2'},
        'rule': 'allowance - 2 <= value <= allowance for every rank of every ability; never over',
        'passive_limits': ['no eff.prevent_hit', 'no hard-control condition', 'no harm of S3 or more'],
        'effect_units': [{'effect': a, 'units': b, 'ids': c} for a, b, c in EU_TABLE]}
    by_branch = collections.Counter()
    for a in abilities:
        by_branch['oath (%s)' % a['conduct_pole'] if 'requires_conduct' in a else '.'.join(a['tags'][0].split('.')[:2])] += 1
    by_branch['absorbed (mirrors)'] = len(absorbed)
    const['census'] = {'total': total, 'by_group': dict(sorted(by_branch.items())), 'ranks_authored': stats['ranks'],
                       'by_form': {k[5:].lower(): v for k, v in sorted(stats.items()) if k.startswith('form.')},
                       'by_timing': {k[7:]: v for k, v in sorted(stats.items()) if k.startswith('timing.')},
                       'by_min_tier': {int(k[3:]): v for k, v in sorted(stats.items()) if k.startswith('mt.')},
                       'budget_slack': {'on_allowance': stats['under0'], 'one_under': stats['under1'], 'two_under': stats['under2']}}
    body = dump(dict(const)) + '\nabilities:\n' + '\n'.join(indent_list_item(dump([a])) for a in abilities + absorbed)
    write(os.path.join(DATA, 'abilities.yaml'), head, body)

    # ------------------------------------------------ licenses.yaml ------------------------------------------------
    lic = lic_training.build(TAGS)
    push = dict(lic_training.FOCUS_LICENSES[0]); push['kind'] = 'fact'; push['universal'] = True
    extra = [push, lic_training.FOCUS_LICENSES[1]]
    for e in lic + extra:
        for k in ('principle', 'stretch', 'emulate', 'crude_fallback', 'scope', 'excludes', 'acquisition_paths'):
            if k not in e:
                errs.append('license %s lacks %s' % (e['id'], k))
        for ref in G.walk(e):
            G.check_ref(ref, e['id'])
    head = """# data/licenses.yaml
# Purpose: every license that is not an ability, a rite, a basic verb or a language: the 81 TRAINING licenses
#   (one per level-2 deed tag: the domain license of that trade or art, with grades trained < expert < master)
#   and the two Focus licenses. A training license licenses the methods of its tag that the basic verbs exclude,
#   and is what makes emulation (05.5.4), stretch grades (05.5.2), learning (05.8.5) and flares available for
#   abilities under its tag. Callings set the grade by tier (04.5.1); every other path grants `trained`.
# Owner: 05-abilities-focus-magic (T-00-19). Owner-blocks: 02 (origin licenses), 08 (item licenses), 13 (languages,
#   setting licenses), and 04 (the six lic.call.* capability licenses, data/contrib/licenses.04.yaml, approved).
# Schema: data/SCHEMAS.md#licensesyaml (License, 00.12.1). EVERY entry carries explicit principle, scope, excludes,
#   crude_fallback, stretch, emulate and acquisition_paths (01 Interface request; a missing field would be read
#   as null and logged as a rule_conflict). Generated by rules/_process/simulation/05-gen_data05/gen_data05.py.
# Basis: [C:VII] [00.12.1] [00.12.4] [01.3.5] [04.5.1, 04.5.3] [R7 4.4] [DL-05-06] [DL-05-08]"""
    doc = collections.OrderedDict(schema_version=1, lifecycle='provisional',
                                  grades=[{'grade': 'trained', 'obstacle_tier_cap': 'hard', 'technique_cap_min_tier': 2, 'stretch': {'dc_shift': 5, 'cost_add': 1, 'reach_cap': 'limited'}, 'flares': 1, 'reached_by': 'origin, mentor, text, or a calling\'s Mark at tier 1-2'},
                                          {'grade': 'expert', 'obstacle_tier_cap': 'very_hard', 'technique_cap_min_tier': 4, 'stretch': {'dc_shift': 5, 'cost_add': 1, 'reach_cap': 'standard'}, 'flares': 1, 'reached_by': 'a calling\'s tier only (04.5.1)'},
                                          {'grade': 'master', 'obstacle_tier_cap': 'legendary', 'technique_cap_min_tier': 5, 'stretch': {'dc_shift': 0, 'cost_add': 1, 'reach_cap': 'standard'}, 'flares': 2, 'reached_by': 'a calling\'s tier only (04.5.1)'}],
                                  training_clock={'name': 'training in <trade>', 'kind': 'project', 'segments': 8, 'visibility': 'public', 'direction': 'fill', 'tick_sources': [{'on': 'a downtime training week with a mentor (ch.15)', 'ticks': 2}, {'on': 'a downtime week of study from a manual', 'ticks': 1}], 'on_complete': {'effects': [{'effect_id': 'eff.grant_license', 'params': {'license': 'the training license', 'grade': 'trained', 'duration': 'permanent'}}], 'interrupting': False, 'then': 'close'}},
                                  emulate_defaults={'dc_shift': 5, 'cost_mult': 2, 'reach_cap': 'limited'})
    body = dump(dict(doc)) + '\nlicenses:\n' + '\n'.join(indent_list_item(dump([e])) for e in lic + extra) + '\nblocks: []   # owner-blocks 02, 04, 08, 13 are merged here from data/contrib/licenses.NN.yaml\n'
    write(os.path.join(DATA, 'licenses.yaml'), head, body)

    # ------------------------------------------------ rituals.yaml ------------------------------------------------
    rites = []
    BR = {'deed.arcane': ('intellect', 'backlash'), 'deed.divine': ('presence', 'silence'), 'deed.primal': ('resolve', 'debt'), 'deed.craft': ('intellect', "the miscast of the seated property's branch")}
    for (rid, name, tag, scale, grade, tpt, comps, parts, place, principle, scope, excl, effects, fcosts, canon, note) in rites05.RITES:
        if tag not in TAGS:
            errs.append('rite %s tag %s' % (rid, tag))
        sc = rites05.SCALES[scale]
        br = '.'.join(tag.split('.')[:2])
        for ref in effects:
            G.check_ref(ref, rid)
        for cst in fcosts:
            if cst not in G.sub['reserved_ids']['cost_menu']:
                errs.append('rite %s cost %s' % (rid, cst))
        if not G.DUR_RE.match(tpt):
            errs.append('rite %s time %s' % (rid, tpt))
        G.lint(scope, rid)
        e = collections.OrderedDict()
        e['id'] = rid
        e['name'] = name
        e['kind'] = 'spell'
        e['tags'] = [tag, 'trait.nature.magical', 'trait.action.concentrate', 'trait.duration.lasting']
        e['principle'] = principle
        e['scope'] = scope
        e['excludes'] = [dict(what=a, needs=b) for a, b in excl]
        e['scale'] = scale
        e['grade'] = grade or sc['grade']
        e['attribute'] = BR[br][0]
        e['requires'] = {'license': 'lic.training.' + '_'.join(tag.split('.')[1:3]), 'knowledge': 'the rite\'s text (an item with the fact teaches: %s) or a teacher; learned on a 6-segment project clock (05.8.7)' % rid, 'participants': parts, 'place': place}
        e['cost'] = {'focus': sc['focus']}
        e['components'] = ['%s (price band %d, ch.08)' % c for c in comps]
        e['time_per_tick'] = tpt
        e['dc_tier'] = sc['dc_tier']
        e['clock'] = {'name': name, 'kind': 'progress', 'owner': '05', 'segments': sc['segments'], 'visibility': 'public', 'direction': 'fill',
                      'tick_sources': [{'on': 'a resolved step of the rite (the leader\'s frame)', 'ticks': 'delivered_reach', 'condition': None}],
                      'auto_ticks': [], 'decay': [{'boundary': 'watch', 'ticks': -1, 'only_if': 'no tick since last watch'}],
                      'on_complete': {'effects': effects, 'interrupting': False, 'then': 'close'}, 'races_with': 'the rite\'s strain clock',
                      'links': [{'when': 'reaches:0', 'action': 'void:the rite\'s strain clock'}]}
        e['strain_clock'] = {'name': '%s: the working frays' % name, 'kind': 'danger', 'owner': '05', 'segments': 4, 'visibility': 'public', 'direction': 'fill',
                             'tick_sources': [{'on': 'a failed step of the rite', 'ticks': 'U(severity)', 'condition': None}], 'auto_ticks': [], 'decay': [],
                             'on_complete': {'effects': [{'effect_id': 'eff.write_fact', 'params': {'subject': 'the rite', 'predicate': 'failed', 'value': 'components consumed; the leader suffers the %s miscast at S3 (05.7.5)' % BR[br][1]}}], 'interrupting': False, 'then': 'close'},
                             'races_with': 'the rite\'s progress clock', 'links': []}
        e['failure_costs'] = fcosts
        e['effects'] = effects
        e['miscast'] = BR[br][1]
        e['crude_fallback'] = 'none'
        e['stretch'] = None
        e['emulate'] = None
        e['acquisition_paths'] = [dict(type='mentor', detail='taught by one who knows it: 3 ticks per training week', clock='clk.learn_rite (6 segments, project, public)', requires='the training license at the rite\'s grade'),
                                  dict(type='project', detail='studied from its text: 2 ticks per week', clock='clk.learn_rite (6 segments, project, public)', requires='the training license at the rite\'s grade; the text'),
                                  dict(type='discovery', detail='found as a text, an inscription or a spirit\'s teaching (ch.10, ch.13)', clock=None, requires=None)]
        e['canon_check'] = canon
        e['narration_may_not_imply'] = ['that the rite succeeded before its progress clock is full', 'an effect beyond the listed effects', 'a component not consumed']
        if note:
            e['notes'] = note
        e['lifecycle'] = 'provisional'
        e['basis'] = ['05.8.1', '05.8.2', 'R5 MG-04', 'DL-05-24']
        rites.append(dict(e))
    head = """# data/rituals.yaml
# Purpose: the rites (rituals): magic too large for one beat, run as clocked extended tasks (01.14.6; 00.8).
#   A rite is KNOWN, not held: it takes no ability slot (05.2.3). 24 authored rites, and the tables by which a
#   new rite is designed in play (05.8.4): four scales, eight conditions.
# Owner: 05-abilities-focus-magic (T-00-19). Rules: 05.8. Schema: data/SCHEMAS.md#ritualsyaml (License fields +
#   clock, components, time_per_tick, failure_costs, effects). Optional fields added by ch.05: scale, grade,
#   requires, dc_tier, strain_clock, miscast, canon_check. Each rite creates TWO racing clocks: `clock`
#   (progress, ticked by delivered reach) and `strain_clock` (danger, 4 segments, ticked by U(severity) of a
#   failed step); the first to fill decides the rite (00.8.5).
# Generated by rules/_process/simulation/05-gen_data05/gen_data05.py; every effect is validated against effects.yaml.
# Basis: [00.17.1 Q7, Q20] [R5 MG-04] [R: https://www.dungeonworldsrd.com/classes/wizard/]
#   [R: https://earthdawn.fandom.com/wiki/Spellcasting] [DL-05-24]"""
    doc = collections.OrderedDict(schema_version=1, lifecycle='provisional',
                                  procedure='PR-05-5 (perform), PR-05-6 (design)',
                                  scales=[dict(id=k, **v) for k, v in rites05.SCALES.items()],
                                  design_conditions={'table': 'tbl.05.rite_conditions', 'die': 'd8', 'draw': 'the scale\'s number of conditions, without repeats (roll_table)', 'results': [dict(range=n, id=i, text=t) for n, i, t in rites05.CONDITIONS]},
                                  custom_rites={'id_form': 'rit.custom.<n>', 'lifecycle': 'provisional; permanent when completed twice; retired at the second season boundary if never completed', 'effects': 'one to three effect references with parameters inside their declared ranges, or an existing ability\'s effects at larger scale'},
                                  learn_clock={'name': 'learning <rite>', 'kind': 'project', 'segments': 6, 'visibility': 'public', 'tick_sources': [{'on': 'a training week with one who knows it', 'ticks': 3}, {'on': 'a week of study from its text', 'ticks': 2}]})
    body = dump(dict(doc)) + '\nrituals:\n' + '\n'.join(indent_list_item(dump([e])) for e in rites)
    write(os.path.join(DATA, 'rituals.yaml'), head, body)

    # ------------------------------------------------ composites.yaml ------------------------------------------------
    comps = []
    for c in comp05.COMPOSITES:
        for k in c['keys']:
            if c['key_kind'] == 'composite_key_license':
                if k not in ids:
                    errs.append('composite %s key %s' % (c['id'], k))
            elif k not in TAGS:
                errs.append('composite %s key %s' % (c['id'], k))
        for ref in G.walk(c['effects']):
            G.check_ref(ref, c['id'])
        if c['eu'] > 4:
            errs.append('composite %s exceeds 4 effect units' % c['id'])
        G.lint(c['text'], c['id'])
        e = collections.OrderedDict(id=c['id'], name=c['name'], tags=[k for k in c['keys'] if k in TAGS], keys=c['keys'], key_kind=c['key_kind'],
                                    active_when=c['active_when'] + '; neither key suppressed (00.10.7)', effects=c['effects'], suppresses=c['suppresses'], text=c['text'])
        if 'limits' in c:
            e['limits'] = c['limits']
        e['budget'] = {'value': c['eu'], 'cap': 4}
        e['lifecycle'] = 'provisional'
        e['basis'] = ['05.10.6', 'C:P6', 'DL-05-17']
        comps.append(dict(e))
    head = """# data/composites.yaml
# Purpose: named composites (constitution P6): hand-authored combinations keyed to EXACTLY TWO low-cardinality
#   keys, and the companion mechanism for everything else: the priority-rank bands of the behavioral slots and
#   the ordered spread tags. Chapter 05 authors three key kinds: harm_branch (8), conduct_axis (5) and
#   composite_key_license (9: pairs of abilities flagged composite_key in abilities.yaml). The 32 deed_branch
#   composites (one per named hybrid calling) are ch.04's owner-block, data/contrib/composites.04.yaml.
# Owner: 05-abilities-focus-magic (T-00-19; owner-block 04). Rules: 05.10. Schema: data/SCHEMAS.md#compositesyaml.
#   Optional fields added by ch.05: name, text, limits, budget. Every composite is at most 4 effect units
#   (05.11.4) and is built from effects of effects.yaml or the 05 owner-block.
# Basis: [C:P6] [C:P5] [00.10.7] [R3 05.4, 05.5, B-1, B-5, E-3] [R2 4c Three Lashings, Compounding] [DL-05-17]"""
    doc = collections.OrderedDict(schema_version=1, lifecycle='provisional',
                                  presence_rules={'harm_branch': 'a depth-0 harm event of one key\'s branch lands on a target carrying a condition tagged with the other key\'s branch (cascade applies)',
                                                  'conduct_axis': 'the actor holds, unsuspended, at least one oath-gated ability on each axis at the positive pole',
                                                  'composite_key_license': 'the actor holds both abilities and the entry\'s stated circumstance holds',
                                                  'deed_branch': 'ch.04: the actor holds the named hybrid calling (data/contrib/composites.04.yaml)',
                                                  'suppressed': 'a suppressed priority-exclusive claimant never counts as present (WE-00-6)'},
                                  priority_rank_bands=comp05.PRIORITY_BANDS,
                                  priority_rules=['the highest rank owns the slot; lower claimants are fully suppressed unless cosmetic_merge', 'ties go to the earlier-acquired effect', 'the holder may drop a running claim of their own as a free activity', 'a suppressed claim keeps counting down its duration and resumes if the owner ends first'],
                                  spread_tags=comp05.SPREAD_TAGS, spread_total_cap=comp05.SPREAD_TOTAL_CAP,
                                  spread_rule='a working carries at most one spread tag natively; when flares, items or composites add others they resolve in `order`, each applied to the targets the previous produced, never above spread_total_cap in total')
    body = dump(dict(doc)) + '\ncomposites:\n' + '\n'.join(indent_list_item(dump([e])) for e in comps) + '\nblocks: []   # owner-block 04 (32 deed_branch composites) is merged here from data/contrib/composites.04.yaml\n'
    write(os.path.join(DATA, 'composites.yaml'), head, body)

    # ------------------------------------------------ contrib fragments ------------------------------------------------
    head = """# data/contrib/effects.05.yaml
# Purpose: ch.05's owner-block for data/effects.yaml. Six definitions, each added because no core effect with
#   parameters expresses the mechanic (PR-00-8), each using one of the 20 closed operations and one of the four
#   regimes. Everything else in abilities.yaml, rituals.yaml and composites.yaml references the core library.
# Owner: 05-abilities-focus-magic. Schema: data/SCHEMAS.md#effectsyaml. Decision: DL-05-25."""
    ents = []
    for e in EFF05:
        d = collections.OrderedDict(id=e['id'], op=e['op'])
        if e.get('slot'):
            d['slot'] = e['slot']
        d['regime'] = e['regime']
        if e.get('hook'):
            d['hook'] = e['hook']
        d['params'] = e['params']
        d['text'] = e['text']
        d['why_not_core'] = e['why']
        d['lifecycle'] = 'provisional'
        d['basis'] = e['basis']
        ents.append(dict(d))
    write(os.path.join(DATA, '..', '_process', 'merged-contrib', 'effects.05.yaml'), head, dump({'schema_version': 1, 'blocks': [{'owner': '05', 'entries': ents}]}))

    head = """# data/contrib/boundaries.05.yaml
# Purpose: ch.05's owner-block for data/boundaries.yaml. The five handlers 00 reserved for ch.05 are DEFINED in
#   05 (rule ids below) and restated here with their rule ids; four handlers are added.
# Owner: 05-abilities-focus-magic. Schema: data/SCHEMAS.md#boundariesyaml. Phase 3 = recover (00.7.5)."""
    hs = [
        dict(id='h.05.round_recharge', boundary='round', phase=3, interrupting=False, effect='refresh uses with per: round', rule_id='05.4.6', status='reserved by 00; defined'),
        dict(id='h.05.conflict_recharge', boundary='conflict_end', phase=3, interrupting=False, effect='refresh uses with per: conflict_end and below on the refresh ladder', rule_id='05.4.6', status='reserved by 00; defined'),
        dict(id='h.05.scene_recharge', boundary='scene_end', phase=3, interrupting=False, effect='refresh uses with per: scene_end and below; reset focus.generated_this_scene; end scene-duration ability effects not already expired', rule_id='05.4.6; 05.6.10', status='reserved by 00; defined'),
        dict(id='h.05.day_recharge', boundary='day', phase=3, interrupting=False, effect='refresh uses with per: day; reset focus.short_rests_today', rule_id='05.4.6; 05.6.9', status='reserved by 00; defined'),
        dict(id='h.05.focus_recover', boundary=['breather', 'rest_short', 'rest_long'], phase=3, interrupting=False, effect='restore Focus by rest type and quality (T-05-5); apply the resonant-place +1; runs after h.07.rest_recovery', rule_id='05.6.9', status='reserved by 00; defined'),
        dict(id='h.05.rest_recharge', boundary=['rest_short', 'rest_long'], phase=3, interrupting=False, effect='refresh uses with per: rest_short (both rests) and per: rest_long (long rest only) and everything below on the refresh ladder; on rest_long reset healings_since_long_rest, overdraws_since_long_rest, restored_by_consumables_since_long_rest; on rest_short reset breathers_since_short_rest', rule_id='05.4.6; 05.6.6; 05.6.11; 05.7.8', status='added'),
        dict(id='h.05.reslot', boundary='rest_long', phase=3, interrupting=False, effect='offer the exchange between acquired slots and the shelf or library (quality full or partial only)', rule_id='05.2.7', status='added'),
        dict(id='h.05.reserve', boundary='rest_long', phase=3, interrupting=False, effect='resolve reserve charging: bank the charged points if the holder was never Spent since declaring them, else lose the charge; restore focus.max; accept a new declaration', rule_id='05.6.12', status='added'),
        dict(id='h.05.provisional_abilities', boundary=['reflection', 'season'], phase=8, interrupting=False, effect='confirm non-pick abilities used in 3 different scenes; at the second season boundary shelve the unconfirmed, with a warning one season earlier', rule_id='05.2.10', status='added'),
    ]
    write(os.path.join(DATA, '..', '_process', 'merged-contrib', 'boundaries.05.yaml'), head, dump({'schema_version': 1, 'blocks': [{'owner': '05', 'handlers': hs}]}))

    if errs or G.errors:
        print('EMIT ERRORS:')
        for e in errs + G.errors:
            print('  ', e)
        raise SystemExit(1)
    print('census:', total, 'abilities =', n_pool, 'pool +', n_oath, 'oath +', len(absorbed), 'absorbed;', len(lic) + 2, 'licenses;', len(rites), 'rites;', len(comps), 'composites')


def indent_list_item(s):
    return s.rstrip('\n')
