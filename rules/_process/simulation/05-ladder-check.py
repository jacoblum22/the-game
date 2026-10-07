#!/usr/bin/env python3
"""05-ladder-check.py -- verifies that every calling's pick ladder is complete (revision I-007).

For every calling in data/callings.yaml, every pool axis it draws on, and every tier 1-5, it applies ch.04's pool
gate (04.8.4) to data/abilities.yaml exactly as written:
  * eligible: slot_class calling; not retired and not adversary_only; min_tier <= T; first tag at or under a
    pool_gate.own or pool_gate.kin tag, or a conduct axis in pool_gate.conduct; an oath-gated ability (one with a
    conduct_pole) only through a calling whose `pole` equals it (05.3.10);
  * allowance: cumulative picks 2, 3, 4, 5, 6 for a deed-keyed calling; 1, 1, 2, 2, 3 for a vow or dark calling
    (callings.yaml#tier_ladder picks_total).
Checks, per calling:
  (1) LADDER  at every tier T the eligible pool is at least picks_total[T] (no pick is ever "kept" for want of an
      ability, PR-04-5 step 2);
  (2) STEP    at every tier where the allowance rises, at least one ability with min_tier == T exists in the
      calling's pool when T is 1, 3 or 5 for a conduct-keyed calling (so the new pick has a candidate of its own
      tier, the vow/dark ladder of 1/3/5);
  (3) AXIS    per conduct axis the calling draws on (pool_gate.conduct), the count by min_tier at the calling's pole,
      compared with the opposite pole on the same axis (the light/dark parity check);
  (4) GATE    a calling that lists pool_gate.conduct but whose pole admits no oath-gated ability on it is reported
      (the gate would be dead data).
Prints a table per calling kind and exits 1 on any LADDER, STEP or GATE failure. Deterministic; no randomness.
Usage: python 05-ladder-check.py
"""
import collections
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.environ.get('GAME_RULES', os.path.normpath(os.path.join(HERE, '..', '..')))
D = os.path.join(R, 'data')
cal = yaml.safe_load(open(os.path.join(D, 'callings.yaml'), encoding='utf-8'))
abl = yaml.safe_load(open(os.path.join(D, 'abilities.yaml'), encoding='utf-8'))['abilities']

PT = cal['tier_ladder']['picks_total']      # {deed: [...], oath: [...]}


def picks_total(c, t):
    return PT['oath' if c['breadth'] in ('vow', 'dark') else 'deed'][t - 1]


def under(tag, root):
    return tag == root or tag.startswith(root + '.')


def eligible(c, a, t):
    if a.get('slot_class') != 'calling' or a.get('lifecycle') == 'retired' or a.get('adversary_only'):
        return None
    if a['min_tier'] > t:
        return None
    g = c.get('pool_gate') or {}
    first = a['tags'][0]
    if a.get('conduct_pole'):
        ax = a['requires_conduct'][0]
        if ax in (g.get('conduct') or []) and c.get('pole') == a['conduct_pole']:
            return 'conduct:' + ax
        return None
    if any(under(first, x) for x in g.get('own') or []):
        return 'own'
    if any(under(first, x) for x in g.get('kin') or []):
        return 'kin'
    return None


fails = []
rows = collections.defaultdict(list)
axis_rows = []
for c in cal['callings']:
    pool = {t: [a for a in abl if eligible(c, a, t)] for t in range(1, 6)}
    line = []
    for t in range(1, 1 + int(c.get('max_tier', 5))):
        need = picks_total(c, t)
        have = len(pool[t])
        line.append('%d/%d' % (have, need))
        if have < need:
            fails.append('LADDER %s tier %d: %d eligible < %d picks' % (c['id'], t, have, need))
        if c['breadth'] in ('vow', 'dark') and t in (1, 3, 5) and t <= int(c.get('max_tier', 5)):
            if not any(a['min_tier'] == t for a in pool[t]):
                fails.append('STEP %s tier %d: no ability of min_tier %d for the new pick' % (c['id'], t, t))
    rows[c['breadth']].append((c['id'], c.get('pole'), line))
    for ax in (c.get('pool_gate') or {}).get('conduct') or []:
        mine = collections.Counter(a['min_tier'] for a in abl if a.get('requires_conduct') == [ax] and a.get('conduct_pole') == c.get('pole'))
        other_pole = {'positive': 'negative', 'negative': 'positive'}.get(c.get('pole'))
        theirs = collections.Counter(a['min_tier'] for a in abl if a.get('requires_conduct') == [ax] and a.get('conduct_pole') == other_pole)
        axis_rows.append((c['id'], ax, c.get('pole'), [mine[t] for t in range(1, 6)], [theirs[t] for t in range(1, 6)]))
        if not sum(mine.values()):
            fails.append('GATE %s: pool_gate.conduct lists %s but pole %r admits no oath-gated ability on it' % (c['id'], ax, c.get('pole')))

print('# Pick-ladder check (05-ladder-check.py; revision I-007)')
print()
print('Each cell is eligible abilities / cumulative picks at that tier (04.8.4 pool gate applied to abilities.yaml).')
for kind in ('vow', 'dark', 'fine', 'narrow', 'broad', 'hybrid'):
    if kind not in rows:
        continue
    print()
    print('## %s callings (%d)' % (kind, len(rows[kind])))
    print()
    print('| Calling | pole | T1 | T2 | T3 | T4 | T5 |')
    print('|---|---|---|---|---|---|---|')
    for cid, pole, line in rows[kind]:
        print('| %s | %s | %s |' % (cid, pole or '-', ' | '.join(line + [''] * (5 - len(line)))))
print()
print('## Conduct axes: abilities by min_tier 1..5 at the calling\'s pole, and at the opposite pole')
print()
print('| Calling | axis | pole | this pole (T1..T5) | opposite pole (T1..T5) |')
print('|---|---|---|---|---|')
for cid, ax, pole, mine, theirs in axis_rows:
    print('| %s | %s | %s | %s | %s |' % (cid, ax, pole, mine, theirs))
print()
checked = sum(len(v) for v in rows.values())
print('callings checked: %d; conduct calling x axis rows: %d; failures: %d' % (checked, len(axis_rows), len(fails)))
for f in fails:
    print('FAIL', f)
sys.exit(1 if fails else 0)
