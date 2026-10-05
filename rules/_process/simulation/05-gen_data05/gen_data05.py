# gen_data05.py -- generates and validates chapter 05's data files:
#   rules/data/abilities.yaml, rules/data/licenses.yaml, rules/data/rituals.yaml, rules/data/composites.yaml,
#   rules/data/contrib/effects.05.yaml, rules/data/contrib/boundaries.05.yaml
# from the individually authored tables in ab_*.py, lic_training.py, rites05.py and comp05.py.
# Checks performed (any failure aborts unless --report):
#   ids unique and prefixed; every tag exists in data/tags.yaml; first tag is a deed tag at level 2 or 3;
#   effect ids exist (core library or the 05 owner-block); hooks, behavioral slots, conditions, bands, flags and
#   duration forms are in data/substrate.yaml; parameter ranges of the core effects are respected;
#   the eight-form grammar (form -> regime/timing); principle and text lint (SG-15, T-00-22);
#   every license key required by 01/04 is present; ranks are within the rank rule; the power budget (05.11);
#   coverage asked by ch.04 (per level-2 tag, per branch and tier, per conduct axis).
import sys, re, os, collections, importlib, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.environ.get('GAME_RULES', r'C:\Users\jacob\the-game\rules')
DATA = os.path.join(ROOT, 'data')
REPORT_ONLY = '--report' in sys.argv

import dsl05
from dsl05 import ABILITIES, EU_TABLE

MODULES = ['ab_martial', 'ab_guile', 'ab_wilds', 'ab_lore', 'ab_arcane', 'ab_divine', 'ab_primal', 'ab_influence',
           'ab_craft', 'ab_conduct']
for m in MODULES:
    if os.path.exists(os.path.join(HERE, m + '.py')):
        importlib.import_module(m)

errors = []
warns = []


def err(msg):
    errors.append(msg)


def L(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return yaml.safe_load(f)


tags_doc = L('tags.yaml')
TAGS = {t['id']: t for t in tags_doc['tags']}
sub = L('substrate.yaml')
HOOKS = {h['id'] for h in sub['hooks']}
SLOTS = {s['id'] for s in sub['behavioral_slots']}
CONDS = set(sub['reserved_ids']['conditions'])
BANDS = set(sub['reserved_ids']['range_bands'])
FLAGS = set(sub['reserved_ids']['positional_flags'])
eff_doc = L('effects.yaml')
CORE_EFF = {e['id']: e for e in eff_doc['core']}
DUR_RE = re.compile(r'^(rounds|intervals|hours|watches|days|uses):\d+$|^(scene|conflict|permanent|until_cleansed|instant|beat)$|^until_rest:(breather|rest_short|rest_long)$|^while:.+')

# ---------------------------------------------------------------------------------------------------------------
# The 05 owner-block of effects.yaml (written to contrib/effects.05.yaml). Added only where no core effect with
# parameters expresses the mechanic (PR-00-8); each uses one of the 20 closed operations.
# ---------------------------------------------------------------------------------------------------------------
EFF05 = [
    dict(id='eff.05.spell_delivery', op='claim_slot', slot='slot.spell_delivery', regime='priority_exclusive',
         params={'priority_rank': 'int', 'form': 'touch|bolt|line|burst|cone|chain|zone', 'duration': 'duration', 'cosmetic_merge': 'bool'},
         text="Your workings project as {form}.",
         basis=['05.10.4', 'T-00-14 slot.spell_delivery', 'DL-05-25'],
         why="the core library seeds claims for strike delivery, movement, stance, aura and body form but none for slot.spell_delivery"),
    dict(id='eff.05.defense_reaction', op='claim_slot', slot='slot.defense_reaction', regime='priority_exclusive', hook='on_hit_taken',
         params={'priority_rank': 'int', 'form': 'str', 'effects': '[effect_ref]'},
         text="When you are hit you answer with {form}.",
         basis=['05.10.3', 'T-00-14 slot.defense_reaction', 'DL-05-25'],
         why="no core claim exists for slot.defense_reaction; blocks, parries and wards must compete for one slot by rank"),
    dict(id='eff.05.waive', op='prevent', regime='additive',
         params={'event_kind': 'a named snag, provoked reaction, restriction or cost', 'applies_when': 'expr'},
         text="{event_kind} is not applied {applies_when}.",
         basis=['05.3.2 Exception form', 'DL-05-25'],
         why="the Exception form needs to negate one named rule consequence (a snag, a provoked reaction); eff.prevent_hit only negates hits"),
    dict(id='eff.05.refresh_use', op='resource', regime='independent_trigger', hook='per ability (refresh_on)',
         params={'ability': 'ab.*|self', 'uses': '1..2'},
         text="{ability} regains {uses} use.",
         basis=['05.4.6', '00.3.11 (uses are counted in units)', 'DL-05-25'],
         why="trigger-refreshed recharge (R3 05.8) returns a USE, which eff.restore's quantity list does not include"),
    dict(id='eff.05.counter_working', op='prevent', regime='independent_trigger', hook='on_declare',
         params={'applies_when': "another entity within band.near declares a working with trait.nature.magical", 'limits': 'limits'},
         text="Negate one working as it is cast.",
         basis=['05.7.7', 'R5 MG-08', 'DL-05-25'],
         why="eff.prevent_hit subscribes to on_hit_taken; a counter must cancel a declared working before it resolves"),
    dict(id='eff.05.end_working', op='remove_condition', regime='independent_trigger',
         params={'target': 'one effect_instance or condition with trait.nature.magical', 'condition_or_category': 'magical'},
         text="Ends {target}.",
         basis=['05.7.7', 'R5 MG-08', 'DL-05-25'],
         why="eff.cleanse removes conditions; dispelling must also end magical effect instances that are not conditions (wards, summonings, illusions)"),
]
EFF05_IDS = {e['id'] for e in EFF05}
ALL_EFF = set(CORE_EFF) | EFF05_IDS

FORMS = {
    'Edge': dict(regime='additive', timings={'passive'}),
    'Lever': dict(regime='additive', timings={'passive', 'rider'}),
    'Permission': dict(regime='additive', timings={'beat'}),
    'Working': dict(regime='independent_trigger', timings={'beat', 'rider'}),
    'Reaction': dict(regime='independent_trigger', timings={'reaction', 'trigger'}),
    'Form': dict(regime='priority_exclusive', timings={'beat', 'rider'}),
    'Exception': dict(regime='additive', timings={'passive', 'rider'}),
    'Reserve': dict(regime='independent_trigger', timings={'rider', 'reaction', 'trigger'}),
}
A_TERM = {'beat': 2, 'reaction': 1, 'rider': 0, 'trigger': 0, 'passive': 0}
R_TERM = {None: 0, 'round': 0, 'conflict_end': 1, 'scene_end': 1, 'rest_short': 2, 'rest_long': 3, 'day': 3, 'never': 4}
MAX_RANKS = {1: 3, 2: 2, 3: 2, 4: 1, 5: 1}
MAX_COST = {1: 2, 2: 2, 3: 3, 4: 3, 5: 4}
BANNED = [r'\blevel\b', r'\bclass\b', r'\bXP\b', r'hit points', r'\bHP\b', r'\bmana\b', r'\bstamina\b', r'saving throw',
          r'skill check', r'\badvantage\b', r'\bdisadvantage\b', r'\binjur', r'\bhurt\b', r'\bminor\b', r'\bmajor\b',
          r'\bsevere\b', r'the System', r'no protection', r'offers no', r'does not protect', r'can lull']
MAGIC = ('deed.arcane', 'deed.divine', 'deed.primal')
CAST_ATTR = {'deed.arcane': 'intellect', 'deed.divine': 'presence', 'deed.primal': 'resolve'}
BRANCH_TRAITS = {'deed.arcane': ['trait.nature.magical', 'trait.action.speech', 'trait.action.manipulate'],
                 'deed.divine': ['trait.nature.magical', 'trait.nature.sacred', 'trait.action.speech'],
                 'deed.primal': ['trait.nature.magical']}
LEARN_SEG = {1: 6, 2: 6, 3: 8, 4: 8, 5: 12}


def lint(text, where):
    for b in BANNED:
        if re.search(b, text, re.I if b not in (r'\bXP\b', r'\bHP\b') else 0):
            err('%s: banned or soft phrasing %r in %r' % (where, b, text[:70]))


def branch_of(tag):
    return '.'.join(tag.split('.')[:2])


def l2_of(tag):
    return '.'.join(tag.split('.')[:3])


def walk(o):
    """yield every effect-ref dict nested anywhere."""
    if isinstance(o, dict):
        if 'effect_id' in o:
            yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, (list, tuple)):
        for v in o:
            yield from walk(v)


def check_ref(ref, where):
    eid = ref['effect_id']
    if eid not in ALL_EFF:
        err('%s: unknown effect %s' % (where, eid))
    p = ref.get('params', {})
    if eid == 'eff.check_edge' and not 1 <= p['amount'] <= 2:
        err('%s: check_edge amount' % where)
    if eid == 'eff.harm_edge' and not 1 <= p['amount'] <= 2:
        err('%s: harm_edge amount' % where)
    if eid == 'eff.harm_reduction' and not 1 <= p['amount'] <= 4:
        err('%s: reduction amount' % where)
    if eid == 'eff.harm_severity_step' and not -2 <= p['steps'] <= 2:
        err('%s: severity steps' % where)
    if eid == 'eff.reposition' and not -2 <= p['band_change'] <= 2:
        err('%s: band_change' % where)
    if eid == 'eff.apply_condition':
        if p['condition'] not in CONDS:
            err('%s: condition %s not a reserved id' % (where, p['condition']))
    if eid == 'eff.condition_immunity':
        for c in p['forbid']['conditions']:
            if c not in CONDS:
                err('%s: condition %s' % (where, c))
    if 'duration' in p and not DUR_RE.match(str(p['duration'])):
        err('%s: duration form %r' % (where, p['duration']))
    for f in p.get('flags_add', []) + p.get('flags_remove', []):
        if f not in FLAGS:
            err('%s: flag %s' % (where, f))
    for m in re.findall(r'band\.[a-z]+', str(p)):
        if m not in BANDS:
            err('%s: band %s' % (where, m))
    for m in re.findall(r'cond\.[a-z_]+', str(p)):
        if m not in CONDS:
            err('%s: condition %s' % (where, m))


def text_ids(text, where):
    for m in re.findall(r'band\.[a-z]+', text):
        if m not in BANDS:
            err('%s: band %s in text' % (where, m))
    for m in re.findall(r'cond\.[a-z_]+', text):
        if m not in CONDS:
            err('%s: condition %s in text' % (where, m))
    for m in re.findall(r'flag\.[a-z_]+', text):
        if m not in FLAGS:
            err('%s: flag %s in text' % (where, m))


def budget(a, r, rank):
    f = r['f']
    Rt = max(0, R_TERM[r['per']] - (r['uses'] - 1))
    allowance = (a['mt'] + 2 * (rank - 1) + 1) + 2 * f + Rt + A_TERM[a['timing']] + a.get('lim', 0) + a.get('wk', 0) + a.get('oc', 0)
    value = sum(e[1] for e in r['effects'])
    terms = dict(tier=a['mt'] + 2 * (rank - 1) + 1, focus=2 * f, recharge=Rt, timing=A_TERM[a['timing']],
                 limitation=a.get('lim', 0), weakness=a.get('wk', 0), other_cost=a.get('oc', 0))
    return value, allowance, terms


def flares_for(a, refs):
    if a['timing'] == 'passive' or a['form'] in ('Edge', 'Exception', 'Reserve'):
        return []
    if 'fl' in a:
        return a['fl']
    out = []
    ids = [x['effect_id'] for x in walk(refs)]
    text = a['ranks'][0]['text']
    if any(i in ids for i in ('eff.deal_harm', 'eff.apply_condition', 'eff.harm_severity_step')):
        out.append('hard')
    if a['timing'] == 'beat' and re.search(r'band\.(close|near|far)', text):
        out.append('far')
    if a['form'] == 'Working' and 'spread' not in a and a['timing'] == 'beat':
        out.append('wide')
    if a['timing'] in ('beat', 'rider') and re.search(r"rounds:\d|'scene'|'conflict'|intervals:\d", str(refs)):
        out.append('lasting')
    if any(t.startswith('trait.sense') for t in a.get('traits', [])) or branch_of(a['tag']) in MAGIC:
        out.append('quiet')
    if a.get('check'):
        out.append('sure')
    return out


def build_abilities(train_fallback):
    out = []
    seen = set()
    groups = collections.Counter()
    stats = collections.Counter()
    for a in ABILITIES:
        w = a['id']
        if not a['id'].startswith('ab.') or not re.match(r'^ab\.[a-z0-9_]+$', a['id']):
            err('%s: id form' % w)
        if a['id'] in seen:
            err('%s: duplicate id' % w)
        seen.add(a['id'])
        tag = a['tag']
        if tag not in TAGS:
            err('%s: unknown tag %s' % (w, tag))
            continue
        if not tag.startswith('deed.') or TAGS[tag]['level'] not in (2, 3):
            err('%s: first tag must be a deed tag at level 2 or 3 (%s)' % (w, tag))
        br = branch_of(tag)
        magic = br in MAGIC
        form = a['form']
        if form not in FORMS:
            err('%s: form %s' % (w, form))
            continue
        if a['timing'] not in FORMS[form]['timings']:
            err('%s: timing %s not allowed for form %s' % (w, a['timing'], form))
        regime = 'priority_exclusive' if a.get('slot') else FORMS[form]['regime']
        if a.get('slot') and a['slot'] not in SLOTS:
            err('%s: slot %s' % (w, a['slot']))
        if form == 'Form' and not a.get('slot'):
            err('%s: a Form needs a behavioral slot' % w)
        hook = a.get('hook')
        if a['timing'] in ('reaction', 'trigger') and not hook:
            err('%s: reaction/trigger needs a hook' % w)
        if hook and hook not in HOOKS:
            err('%s: hook %s' % (w, hook))
        if regime == 'independent_trigger' and not hook:
            hook = 'on_declare' if a['timing'] == 'beat' else 'on_degree'
        pr = a['principle']
        if len(pr.split()) > 20 or re.search(r'\d', pr) or not pr.endswith('.'):
            err('%s: principle form: %r' % (w, pr))
        lint(pr, w)
        lint(a['limitation'], w)
        if not a['limitation'].startswith('Applies'):
            err('%s: limitation must be written as a positive scope boundary ("Applies ...")' % w)
        if not 1 <= a['mt'] <= 5:
            err('%s: min_tier' % w)
        if len(a['ranks']) > MAX_RANKS[a['mt']]:
            err('%s: too many ranks for min_tier %d' % (w, a['mt']))
        conduct = a.get('conduct')
        tags = [tag]
        if conduct:
            if conduct[0] not in TAGS:
                err('%s: conduct tag' % w)
            tags.append(conduct[0])
        traits = list(a.get('traits', []))
        if magic and a['timing'] != 'passive':
            for t in BRANCH_TRAITS[br]:
                if t == 'trait.nature.sacred' and 'trait.nature.profane' in traits:
                    continue
                if t not in traits:
                    traits.append(t)
        elif magic and 'trait.nature.magical' not in traits:
            traits.append('trait.nature.magical')
        for t in traits + a.get('harm_tags', []):
            if t not in TAGS:
                err('%s: unknown tag %s' % (w, t))
        tags += a.get('harm_tags', []) + traits
        ranks_out = []
        budgets = []
        for i, r in enumerate(a['ranks'], 1):
            lint(r['text'], '%s r%d' % (w, i))
            text_ids(r['text'], '%s r%d' % (w, i))
            refs = [e[0] for e in r['effects'] if e[0] is not None]
            for ref in walk(refs):
                check_ref(ref, '%s r%d' % (w, i))
            if a['timing'] == 'passive' and (r['f'] or r['per']):
                err('%s: a passive has no cost and no limits' % w)
            if r['f'] > MAX_COST[a['mt']] or r['f'] > 4:
                err('%s r%d: Focus cost %d above the band cap for min_tier %d' % (w, i, r['f'], a['mt']))
            if a['timing'] == 'passive':
                ids = [x['effect_id'] for x in walk(refs)]
                if 'eff.prevent_hit' in ids:
                    err('%s: a passive may not prevent' % w)
                for x in walk(refs):
                    if x['effect_id'] == 'eff.apply_condition' and x['params']['condition'] in dsl05.COND_HARD:
                        err('%s: a passive may not apply hard control' % w)
                    if x['effect_id'] == 'eff.deal_harm' and x['params']['severity'] in ('S3', 'S4', 'S5'):
                        err('%s: a passive may not deal S3+ harm' % w)
            v, al, terms = budget(a, r, i)
            if not al - 2 <= v <= al:
                err('BUDGET %s r%d: value %d, allowance %d (terms %s)' % (w, i, v, al, terms))
            stats['under%d' % (al - v)] += 1
            budgets.append(dict(rank=i, value=v, allowance=al, terms=terms))
            ro = dict(rank=i, at_tier=a['mt'] + 2 * (i - 1), text=r['text'], effects=refs, cost={'focus': r['f']},
                      limits=({'per': r['per'], 'uses': r['uses']} if r['per'] else None))
            ranks_out.append(ro)
        r1 = a['ranks'][0]
        refs1 = [e[0] for e in r1['effects'] if e[0] is not None]
        chk = a.get('check')
        if chk:
            if chk[0] == 'aimed':
                check = dict(mode='aimed', verb=chk[1], against=chk[2])
            else:
                check = dict(mode='resisted', resist_verb='verb.' + chk[1], resist_attribute=chk[2], dc='your effect DC (10 + attribute + competence at the first tag + edge)', degree_table=(chk[3] if len(chk) > 3 else '01.18.3'))
        else:
            check = dict(mode='none')
        attr = a.get('attr') or (CAST_ATTR[br] if magic else 'by_method')
        active = a['timing'] != 'passive'
        stretchable = active and form in ('Working', 'Permission', 'Form', 'Reaction') and not conduct
        l2 = l2_of(tag)
        fb = 'none' if magic else train_fallback.get(l2, 'none')
        if conduct:
            paths = [dict(type='recognition', detail="a pick through a calling whose pool gate lists %s at the %s pole, at tier %d or higher (04.8.4; 05.3.10)" % (conduct[0], conduct[1], a['mt']), clock=None, requires='the calling is not suspended by the Fraying')]
        else:
            paths = [dict(type='recognition', detail="a pick through a calling whose pool gate covers %s, at tier %d or higher (04.8.4)" % (tag, a['mt']), clock=None, requires=None),
                     dict(type='mentor', detail="taught into the acquired partition at rank 1: 3 ticks per training week (05.8.5)", clock='clk.learn (%d segments)' % LEARN_SEG[a['mt']], requires="lic.training.%s at a grade whose technique cap covers min_tier %d" % (l2[5:].replace('.', '_'), a['mt'])),
                     dict(type='project', detail="learned by emulation (delivered reach per success), from a text (2 per week) or by practice after witnessing it (1 per week) (05.8.5)", clock='clk.learn (%d segments)' % LEARN_SEG[a['mt']], requires="lic.training.%s at a grade whose technique cap covers min_tier %d" % (l2[5:].replace('.', '_'), a['mt']))]
        nmi = ["a harm type, target, band or duration other than the text's", "a weakness this record does not hold", "an effect on anything outside the stated targets"] + a.get('nmi', [])
        e = collections.OrderedDict()
        e['id'] = a['id']
        e['name'] = a['name']
        e['kind'] = 'spell' if magic else 'ability'
        e['tags'] = tags
        e['min_tier'] = a['mt']
        e['mod_group'] = a['grp']
        e['slot_class'] = 'calling'
        e['form'] = form.lower()
        e['activation'] = 'active' if active else 'passive'
        e['timing'] = a['timing']
        e['regime'] = regime
        if hook:
            e['hook'] = hook
        if a.get('when'):
            e['when'] = a['when']
        if a.get('slot'):
            e['slot'] = a['slot']
        if a.get('verbs'):
            e['rides'] = a['verbs']
        e['principle'] = pr
        e['scope'] = r1['text']
        e['limitation'] = a['limitation']
        if a.get('weak'):
            e['weakness'] = {'text': a['weak'][0], 'effect': a['weak'][1][0]}
            lint(a['weak'][0], w)
            for ref in walk(a['weak'][1][0]):
                check_ref(ref, w)
        if a.get('cost_text'):
            e['cost_text'] = a['cost_text']
        e['excludes'] = [dict(what=x[0], needs=x[1]) for x in a.get('x', [])]
        if not e['excludes']:
            err('%s: at least one exclusion is required' % w)
        e['attribute'] = attr
        e['check'] = check
        e['cost'] = {'focus': r1['f']}
        e['limits'] = ({'per': r1['per'], 'uses': r1['uses']} if r1['per'] else None)
        if a.get('refresh_on'):
            e['refresh_on'] = a['refresh_on']
        e['effects'] = refs1
        e['ranks'] = ranks_out
        e['crude_fallback'] = fb
        e['stretch'] = dict(dc_shift=5, cost_add=1, reach_cap='limited', within='principle') if stretchable else None
        e['emulate'] = None
        e['acquisition_paths'] = paths
        e['flares'] = flares_for(a, refs1) if not conduct else [f for f in flares_for(a, refs1) if f != 'quiet']
        if a.get('spread'):
            e['spread'] = a['spread']
        if a.get('ckey'):
            e['composite_key'] = True
        if a.get('dictates'):
            e['dictates_choice'] = True
        if conduct:
            e['requires_conduct'] = [conduct[0]]
            e['conduct_pole'] = conduct[1]
        if a.get('replaces'):
            e['replaces'] = a['replaces']
        e['narration_may_not_imply'] = nmi
        e['budget'] = budgets
        e['source'] = 'the shared pool (05.1.1)'
        e['lifecycle'] = 'provisional'
        e['basis'] = ['05.3', '05.11'] + a.get('basis', [])
        out.append(dict(e))
        groups[(br if not conduct else conduct[0] + conduct[1], a['grp'])] += 1
        stats['form.' + form] += 1
        stats['timing.' + a['timing']] += 1
        stats['mt.%d' % a['mt']] += 1
        stats['ranks'] += len(a['ranks'])
    return out, stats


def coverage(abilities):
    """ch.04's coverage requests."""
    l2tags = [t for t in TAGS if t.startswith('deed.') and TAGS[t]['level'] == 2]
    per_l2 = collections.defaultdict(list)
    per_branch = collections.defaultdict(lambda: collections.Counter())
    cond_pos = collections.defaultdict(list)
    cond_neg = collections.defaultdict(list)
    for a in abilities:
        if a.get('requires_conduct'):
            (cond_pos if a['conduct_pole'] == 'positive' else cond_neg)[a['requires_conduct'][0]].append(a['min_tier'])
            continue
        t = a['tags'][0]
        per_l2[l2_of(t)].append(a['min_tier'])
        per_branch[branch_of(t)][a['min_tier']] += 1
    rep = []
    for t in l2tags:
        ms = per_l2.get(t, [])
        if len(ms) < 2 or 1 not in ms:
            err('COVERAGE %s: %s' % (t, ms))
    for b in sorted(per_branch):
        c = per_branch[b]
        tot = sum(c.values())
        rep.append((b, tot, [c[i] for i in range(1, 6)]))
        if tot < 12 or any(c[i] < 2 for i in range(1, 6)):
            err('COVERAGE branch %s: total %d by tier %s' % (b, tot, [c[i] for i in range(1, 6)]))
    axes = [t for t in TAGS if t.startswith('conduct.')]
    for ax in axes:
        ms = cond_pos.get(ax, [])
        if len(ms) < 2 or 1 not in ms or 3 not in ms:
            err('COVERAGE conduct+ %s: %s' % (ax, ms))
    return rep, {k: sorted(v) for k, v in cond_pos.items()}, {k: sorted(v) for k, v in cond_neg.items()}


if __name__ == '__main__':
    try:
        import lic_training
        fallback = lic_training.fallback_map()
    except ImportError:
        fallback = {}
    abilities, stats = build_abilities(fallback)
    rep = cp = cn = None
    if not REPORT_ONLY or '--cov' in sys.argv:
        rep, cp, cn = coverage(abilities)
    print('abilities authored:', len(abilities))
    for k in sorted(stats):
        print('  ', k, stats[k])
    if rep:
        for b, tot, c in rep:
            print('  ', b, tot, c)
        print('   conduct+', cp)
        print('   conduct-', cn)
    print('ERRORS: %d' % len(errors))
    for e in errors:
        print('  ', e)
    if errors and not REPORT_ONLY:
        sys.exit(1)
    if '--emit' in sys.argv and not errors:
        import emit05
        emit05.emit(abilities, stats, EFF05, EU_TABLE, TAGS, ROOT)
