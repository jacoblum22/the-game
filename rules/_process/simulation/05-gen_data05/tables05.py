# tables05.py -- renders chapter 05's data-derived tables T-05-12 (the pool by group and minimum tier) and T-05-14
# (index of the pool) from data/abilities.yaml, and rewrites them in 05-abilities-focus-magic.md in place.
# Added in revision A (I-007, I-009, I-015) so the chapter's tables are quoted from the data, never typed.
# Row order of T-05-14 is the chapter's existing order; a key the chapter does not yet list is appended before the
# conduct rows (deed tags) or after them (branch workings). Usage: python tables05.py [--check]
import collections
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('GAME_RULES', os.path.normpath(os.path.join(HERE, '..', '..', '..')))
CH = os.path.join(ROOT, '05-abilities-focus-magic.md')
AB = yaml.safe_load(open(os.path.join(ROOT, 'data', 'abilities.yaml'), encoding='utf-8'))['abilities']
PER = {'round': '%d/round', 'conflict_end': '/conflict', 'scene_end': '/scene', 'rest_short': '/short rest',
       'rest_long': '/long rest', 'day': '/day', 'never': '%d ever'}


def cell(a):
    if a['timing'] == 'passive':
        return '*%s* (%d · — · passive)' % (a['name'], a['min_tier'])
    s = '*%s* (%d · %dF · %s' % (a['name'], a['min_tier'], a['cost']['focus'], a['timing'])
    lim = a.get('limits')
    if lim:
        f = PER[lim['per']]
        s += ', ' + (f % lim['uses'] if '%d' in f else f)
    return s + ')'


def key(a):
    if a.get('slot_class') == 'license':
        return 'branch working (`%s`)' % a['tags'][0]
    if a.get('requires_conduct'):
        return '`%s` (%s)' % (a['requires_conduct'][0], a['conduct_pole'])
    return '`%s`' % '.'.join(a['tags'][0].split('.')[1:3])


rows = collections.OrderedDict()
for a in AB:
    if a.get('slot_class') == 'acquired' and a.get('mirror_of'):
        continue
    rows.setdefault(key(a), []).append(a)
for k in rows:
    rows[k].sort(key=lambda a: a['min_tier'])

text = open(CH, encoding='utf-8').read()
m = re.search(r"(\*\*T-05-14 Index of the pool\.\*\*.*?\n\n\| Tag \| Abilities \|\n\|---\|---\|\n)((?:\|[^\n]*\|\n)+)", text, re.S)
head, body = m.group(1), m.group(2)
old_keys = [ln.split(' | ')[0][2:] for ln in body.strip('\n').split('\n')]
deed_new = [k for k in rows if k not in old_keys and k.startswith('`deed') is False and not k.startswith('`conduct') and not k.startswith('branch')]
order = []
for k in old_keys:
    if k.startswith('`conduct') and deed_new:
        order += deed_new
        deed_new = []
    order.append(k)
order += [k for k in rows if k not in order]
missing = [k for k in old_keys if k not in rows]
assert not missing, missing
new_body = ''.join('| %s | %s |\n' % (k, '; '.join(cell(a) for a in rows[k])) for k in order)

# T-05-12
grp = collections.OrderedDict()
for b in ('martial', 'guile', 'wilds', 'lore', 'arcane', 'divine', 'primal', 'influence', 'craft'):
    grp['`deed.%s`' % b] = [a for a in AB if not a.get('requires_conduct') and a.get('slot_class') == 'calling' and a['tags'][0].startswith('deed.%s.' % b)]
grp['branch workings (05.7.11; held through training, no slot)'] = [a for a in AB if a.get('slot_class') == 'license']
grp['oath-gated, positive pole'] = [a for a in AB if a.get('conduct_pole') == 'positive']
grp['oath-gated, negative pole'] = [a for a in AB if a.get('conduct_pole') == 'negative']
grp['absorbed powers (ch.04)'] = [a for a in AB if a.get('mirror_of')]
L2 = collections.defaultdict(set)
tags = yaml.safe_load(open(os.path.join(ROOT, 'data', 'tags.yaml'), encoding='utf-8'))['tags']
l2all = collections.defaultdict(set)
for t in tags:
    if t['id'].startswith('deed.') and t['level'] == 2:
        l2all[t['id'].split('.')[1]].add(t['id'])
t12 = ['| Group | Total | min_tier 1 | 2 | 3 | 4 | 5 | Level-2 tags covered (each with at least 2, one at tier 1) |',
       '|---|---|---|---|---|---|---|---|']
tot = collections.Counter()
for g, xs in grp.items():
    if not xs:
        continue
    c = collections.Counter(a['min_tier'] for a in xs)
    tot.update(c)
    if g.startswith('`deed.'):
        b = g[6:-1]
        per = collections.defaultdict(list)
        for a in xs:
            per['.'.join(a['tags'][0].split('.')[:3])].append(a['min_tier'])
        ok = sum(1 for t in l2all[b] if len(per[t]) >= 2 and 1 in per[t])
        cov = '%d of %d' % (ok, len(l2all[b]))
    elif 'oath' in g:
        axes = len({a['requires_conduct'][0] for a in xs})
        cov = '%d axes x %d' % (axes, len(xs) // axes)
    elif g.startswith('branch'):
        cov = 'one per magic branch'
    else:
        cov = 'gated by creature tags'
    t12.append('| %s | %d | %s |' % (g, len(xs), ' | '.join(str(c[i]) for i in range(1, 6)) + ' | ' + cov))
allcov = sum(int(r.split(' | ')[-1].split(' of ')[0]) for r in t12[2:11])
t12.append('| **all** | **%d** | %s | %d of 81 |' % (len(AB), ' | '.join(str(tot[i]) for i in range(1, 6)), allcov))
m12 = re.search(r"(\*\*T-05-12 The pool by branch and minimum tier\.\*\*.*?\n\n)((?:\|[^\n]*\|\n)+)", text, re.S)
new12 = '\n'.join(t12) + '\n'

if '--check' in sys.argv:
    print('T-05-12 same:', m12.group(2) == new12, '| T-05-14 same:', body == new_body)
    sys.exit(0 if (m12.group(2) == new12 and body == new_body) else 1)
text = text[:m12.start(2)] + new12 + text[m12.end(2):]
m = re.search(r"(\*\*T-05-14 Index of the pool\.\*\*.*?\n\n\| Tag \| Abilities \|\n\|---\|---\|\n)((?:\|[^\n]*\|\n)+)", text, re.S)
text = text[:m.start(2)] + new_body + text[m.end(2):]
open(CH, 'w', encoding='utf-8', newline='\n').write(text)
print('wrote T-05-12 (%d rows) and T-05-14 (%d rows)' % (len(t12) - 2, len(order)))
