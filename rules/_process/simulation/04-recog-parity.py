#!/usr/bin/env python3
"""04-recog-parity.py -- issue I-003: do non-combat callings (envoy, smith, scholar) reach tiers 3 and 5 at the
pace of a combat calling?

Engine: chapter 04's `04-recog04.py`, loaded unchanged (03's evidence settlement, 04's requirement sets, policy,
competence ladder, power band), with the conflict opposition of DL-00-05 / 03.4.3 (challenge band = power band +
the advisory offset: -1 25% / 0 40% / +1 30% / +2 5%; the distribution `09-i005-check.py` adopted).

Play model (an assumption, the same for every style): five scenes a session; each style spends 55% of its scenes
in its own pillar and 15% in each of the others (the shape of 04's envoy); a pillar scene has 3-6 beats on the
style's tags; 25% of pillar scenes are framed Dire, and 40% of those carry the worst stakes the pillar has
(lethal for a fight; *ruinous* for a contest, revision I-003); 10% of Dire scenes put the actor at the brink
(Staggered in a fight; an opposing clock one segment from full in a contest). A reflection every second scene.
200 seeds, 90 sessions (so that a tier-5 median is measurable).

Two rule sets are compared for the contest pillars:
  CURRENT  -- the rules before revision A: a contest beat's challenge band is its DC's band (03.4.3 outside
              conflict) and its DC comes from the opposition the scene offers (band to band + 2 for social and
              lore, as 04's envoy model; a crafting step's DC is its target rung's tier, capped at Very hard =
              band 4, 08.6.4); crafting steps are always Risky (08.6.4); a contest is never lethal and no
              contest state makes a crisis except Dire + challenging (03.4.5).
  REVISED  -- revision I-003: the contest band (03.4.3: a principal's band for social and lore, the work's
              type-tier for craft) sets the challenge band, drawn like a fight's (power band + the same offset
              distribution); a Dire contest whose threatened cost is irreversible is *ruinous* (+2 points and a
              crisis, as lethal; 03.4.2, 03.4.5); a contest beat at the brink is a crisis (03.4.5); crafting
              steps on a work with irreplaceable material are Dire (08.6.4). (A counted analogue of cnt.defeat
              for a contest won was trialled and dropped: R9 shows the contest pillars' counted share above
              04.3.3's 0.10 without it, so it changed no pacing and only inflated counted evidence.)
Counted evidence in both: social and lore contests tick a progress clock on half of successes (cnt.progress 2,
or 3 on a critical); craft steps tick the project on every success and a finished work counts cnt.made = its
rung index (3 fine, 4 masterwork, 5 wondrous); fights count cnt.defeat and cnt.focus as 04's model.
Deterministic (04's seeds). Usage: python 04-recog-parity.py [seeds] [sessions]

Section "I-083 / I-039 / I-037" (revision C2a) replaces the drawn contest band with opposition drawn from seeded
worlds (`12-world-seed.py`, oracle seeds 1001-1020; seed s plays world 1001 + s mod 20). Every party a contest can
face is a world NPC: its band is its own band, or its faction's tier band (03.4.3: tier 0-1 -> 1 ... 5 -> 5) when
it may lend it. A contest scene draws a target band like a fight's (power band + the DL-00-05 offset) and faces a
party of the highest band at or below it that the world holds (ties at random): the player seeks opposition at
his level as a fighter does, and the world limits what he finds. Rule sets:
  W-OLD   -- the seed before revision C (no powers) and I-003's contest rules: any faction member lends its tier,
             no cap, no per-opposition limit (the I-083 playtest's world).
  W-NEW   -- revision C: the seed's powers of the far rings (12.16.11: band 4 per ring-4 area, band 5 per ring-5
             area); only a binding party (a faction's head or officer) lends the tier (I-039); contest band
             <= power band + 2 (I-039); a great deed counts at most twice toward one tier from one opposition
             (one party, case, research project or work; 04.3.4, I-083).
  W-NEW-NOPOWERS -- W-NEW's contest rules in the old seed: the powers are what lifts the stall.
In this section every style, the archer included, reads power band from CONFIRMED tiers (I-037: a tier counts
12 evidence-bearing scenes after its grant). A craft project persists for 2-4 craft scenes and is one opposition
in each scene worked on it (revision I-089: was one opposition for the whole project).
A "farming" envoy (one contest scene in three at the highest band the rules grant, at a DC of power band + 1) in a world
with an added tier-5 faction whose door-warden
(own band 1, not binding) is on offer measures the I-039 exploit under W-OLD and W-NEW.
"""
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = int(sys.argv[1]) if len(sys.argv) > 1 else 200
SESSIONS = int(sys.argv[2]) if len(sys.argv) > 2 else 90
src = open(os.path.join(HERE, "04-recog04.py"), encoding="utf-8").read()
src = src[:src.index("if __name__ == '__main__':")]
R = {"__name__": "recog04_parity"}
exec(compile(src, "04-recog04", "exec"), R)

OFFSET = [-1] * 5 + [0] * 8 + [1] * 6 + [2] * 1          # DL-00-05: easy 25 / fair 40 / hard 30 / lethal 5
DC, degree, odds, quality, band_of_dc, Engine, Char = (R[k] for k in ("DC", "degree", "odds", "quality", "band_of_dc", "Engine", "Char"))
ATTR = dict(R["ATTR"])


def points_with_ruin(self, e):
    """03.4.2 as revised: lethal OR ruinous adds +2."""
    p = R["QPTS"][e['quality']] + R["SPTS"][e['stakes']]
    if e.get('lethal') or e.get('ruinous'):
        p += 2
    if e['degree'] == 3:
        p += 2
    if e.get('novel'):
        p += 2
    if e['degree'] <= 1:
        p = 0 if e['stakes'] == 'safe' else p // 2
    return p


Engine.points = points_with_ruin       # identical to 04's when no event is ruinous (the CURRENT rule set)

# ---- revision C2a switches (all off in the I-003 sections, so their output is unchanged)
MODE = {'cap_opp': False, 'confirmed': False}
_orig_detail, _orig_great, _orig_pb = Engine.detail, R["great"], Char.power_band


def detail_rows(self, node, since=0):
    d = _orig_detail(self, node, since)
    d['rows'] = [r for r in self.log[node] if r[0] > since]
    return d


def great_capped(d, tier, n):
    """04.3.4 as revised (I-083): a great deed counts at most twice toward one tier from one opposition."""
    if not MODE['cap_opp']:
        return _orig_great(d, tier, n)
    per, won = {}, set()
    for i, r in enumerate(d['rows']):
        if r[1] < tier:
            continue
        k = r[7] if r[7] is not None else ('u', i)
        per[k] = per.get(k, 0) + 1
        if r[2]:
            won.add(k)                    # the two that count from an opposition may include its success
    return sum(min(2, v) for v in per.values()) >= n and bool(won)


def power_band_confirmed(self):
    """04.5.6 as revised (I-037): each calling at its confirmed tier (12 evidence-bearing scenes after the grant)."""
    if not MODE['confirmed'] or not hasattr(self, '_eng'):
        return _orig_pb(self)
    b = 1
    for k, c in self.callings.items():
        t = c['tier'] if self._eng.ev_since(c.get('at_scene', 0)) >= 12 else c['tier'] - 1
        if t >= 1:
            b = max(b, R["BAND"][c['kind']][t - 1])
    return b


Engine.detail = detail_rows
R["great"] = great_capped
Char.power_band = power_band_confirmed


def beat(rng, eng, ch, tag, dc, stakes, lethal, target, ctx, scene, cband=None, ruinous=False, brink=False, staggered=False, opp=None):
    attr = ATTR[R["branch"](tag)]
    m = ch.mod(tag, attr)
    q = quality(odds(m, dc))
    d20 = rng.randint(1, 20)
    d, near = degree(m, dc, d20)
    if d == 1 and near and stakes != 'safe' and rng.random() < 0.6:
        d = 2
    b = max(band_of_dc(dc), cband or 0)
    crisis = lethal or staggered or ruinous or brink or (stakes == 'dire' and q == 'challenging')
    peak = d >= 2 and b >= ch.power_band() + 1
    e = {'tag': tag, 'secondary': [], 'quality': q, 'stakes': stakes, 'lethal': lethal, 'ruinous': ruinous, 'degree': d,
         'target': target, 'ctx': ctx, 'band': b, 'crisis': crisis, 'peak': peak, 'opp': opp}
    eng.record(e, scene)
    return e


class Style:
    def __init__(self, name, pillar, tags, ctxs, attr, beats=(3, 6), dire=0.25):
        self.name, self.pillar, self.tags, self.ctxs, self.attr = name, pillar, tags, ctxs, attr
        self.beats, self.dire = beats, dire


PILLAR_SHARE = 0.55
OTHER = [('fight', 0.15), ('site', 0.15), ('social', 0.15), ('travel', 0.15)]


def scene_kind(rng, style):
    r = rng.random()
    if r < PILLAR_SHARE:
        return style.pillar
    others = [(k, w) for k, w in OTHER if k != style.pillar][:3]
    r = (r - PILLAR_SHARE) / (1 - PILLAR_SHARE) * sum(w for _, w in others)
    for k, w in others:
        r -= w
        if r <= 0:
            return k
    return others[-1][0]


SIDE = {'fight': [('deed.martial.blade.dagger', 1)], 'site': [('deed.guile.stealth.sneaking', 1)],
        'social': [('deed.influence.insight.motives', 1)], 'craft': [('deed.craft.building.field_works', 1)],
        'lore': [('deed.lore.investigation.search', 1)], 'travel': [('deed.wilds.navigation.wayfinding', 1)]}


def run(style, rules, seed, sessions, eng_out=None):
    rng = random.Random(seed)
    eng = Engine()
    if eng_out is not None:
        eng_out['eng'] = eng
    ch = style.mk()
    ch._eng = eng
    world = WORLDS[seed % len(WORLDS)] if rules.startswith('w-') else None
    project = None
    scene = day = tid = 0
    pick = R["pick"]
    for s in range(1, sessions + 1):
        for sc in range(5):
            scene += 1
            if sc % 2 == 0:
                day += 1
            band = ch.power_band()
            kind = scene_kind(rng, style)
            own = kind == style.pillar
            tags = style.tags if own else SIDE[kind]
            if kind == 'travel':
                tid += 1
                beat(rng, eng, ch, pick(rng, tags), DC[min(5, band + 1)], 'risky', False, 'route%d' % tid,
                     'situation.travel.overland', scene)
                eng.count('cnt.journey', pick(rng, tags), 1, scene)
            elif kind == 'site':
                tier = min(5, rng.choice([band, band + 1, band + 1]))
                for i in range(rng.randint(2, 4)):
                    tid += 1
                    t = pick(rng, tags)
                    e = beat(rng, eng, ch, t, DC[tier], 'risky', False, 'obs%d' % tid, 'situation.exploration.ruin', scene)
                    if e['degree'] >= 2:
                        eng.count('cnt.progress', t, 2, scene)
            else:
                dire = rng.random() < (style.dire if own else 0.15)
                worst = dire and rng.random() < 0.4
                brink = dire and rng.random() < 0.10
                stakes = 'dire' if dire else 'risky'
                n = rng.randint(*style.beats) if own else rng.randint(1, 3)
                ctx = rng.choice(style.ctxs if own else ['situation.social.parley', 'creature.folk.human'])
                if kind == 'fight':
                    tier = max(1, min(5, band + rng.choice(OFFSET)))
                    foes = rng.randint(1, 3)
                    for i in range(n):
                        tid += 1 if i % 2 == 0 else 0
                        t = pick(rng, tags)
                        e = beat(rng, eng, ch, t, DC[tier], stakes, worst, 'foe%d' % tid, ctx, scene, staggered=brink)
                        if e['degree'] >= 2 and foes > 0 and rng.random() < (0.9 if e['degree'] == 3 else 0.5):
                            foes -= 1
                            eng.count('cnt.defeat', t, tier, scene)
                        held = any(not isinstance(k, tuple) and t.startswith(k) for k in ch.callings)
                        if rng.random() < (0.45 if held else 0.15):
                            eng.count('cnt.focus', t, 1, scene)
                    eng.settle(scene, day)
                    reflect(eng, ch, s, scene, style, sc)
                    continue
                # a contest scene: social, craft or lore
                if rules == 'current':
                    if kind == 'craft':
                        cband = None
                        dc = DC[min(4, rng.choice([band, band + 1]))]   # target rung: capped at wondrous = Very hard
                        stakes, worst, brink = 'risky', False, False  # 08.6.4: a step is always Risky
                    else:
                        cband = None
                        dc = DC[min(5, rng.choice([band, band + 1, band + 1, band + 2]))]
                        worst = brink = False                          # no ruinous, no brink crisis
                elif rules == 'revised':
                    cband = max(1, min(5, band + rng.choice(OFFSET)))
                    dc = DC[min(4, cband)] if kind == 'craft' else DC[cband]
                else:   # a world rule set (revision C2a)
                    tb = max(1, min(5, band + rng.choice(OFFSET)))
                    if kind == 'craft':
                        if project is None or project[1] <= 0:
                            tid += 1
                            project = ['work%d' % tid, rng.randint(2, 4), tb]
                        project[1] -= 1
                        # [revision: I-089] a work is one opposition per scene worked on it (04.3.4, 08.6.4): its
                        # clocks bound its steps as an encounter bounds a fight's; was one opposition for the whole project
                        opp, cband = '%s@%d' % (project[0], scene), project[2]
                    else:
                        tb_cap[0] = band + 2
                        opp, cband, dcband = face(rng, world, rules, tb, style)
                    if rules != 'w-old':
                        cband = min(cband, band + 2)                  # I-039: never above power band + 2
                    dc = DC[min(4, cband)] if kind == 'craft' else DC[min(5, max(1, dcband if kind != 'craft' else cband))]
                won = 0
                for i in range(n):
                    tid += 1
                    t = pick(rng, tags)
                    if rules.startswith('w-'):
                        tgt = opp if kind != 'craft' else 'step%d' % tid
                        e = beat(rng, eng, ch, t, dc, stakes, False, tgt, ctx, scene, cband=cband, ruinous=worst, brink=brink,
                                 opp=opp if MODE['cap_opp'] else None)
                    else:
                        e = beat(rng, eng, ch, t, dc, stakes, False, ('npc%d' if kind != 'craft' else 'work%d') % tid,
                                 ctx, scene, cband=cband, ruinous=worst, brink=brink)
                    if e['degree'] >= 2:
                        won += 1
                        if kind == 'craft':
                            eng.count('cnt.progress', t, 3 if e['degree'] == 3 else 2, scene)
                        elif rng.random() < 0.5:
                            eng.count('cnt.progress', t, 3 if e['degree'] == 3 else 2, scene)
                if own and won * 2 >= n:
                    if kind == 'craft':
                        eng.count('cnt.made', t, min(5, 2 + (cband or band_of_dc(dc)) // 2 + 1), scene)
            eng.settle(scene, day)
            reflect(eng, ch, s, scene, style, sc)
    return ch


# ---- seeded worlds (revision C2a; 12-world-seed.py, oracle seeds 1001-1020)
WORLDS = []
tb_cap = [5]


def tier_band(t):
    return max(1, min(5, t))            # 03.4.3: faction tier 0-1 -> 1, 2 -> 2 ... 5 -> 5


def build_worlds(n=20):
    import importlib.util
    spec = importlib.util.spec_from_file_location('ws12', os.path.join(HERE, '12-world-seed.py'))
    ws = importlib.util.module_from_spec(spec)
    argv, sys.argv = sys.argv, ['12-world-seed.py']
    spec.loader.exec_module(ws)
    sys.argv = argv
    out = []
    for s in range(1001, 1001 + n):
        reg = ws.build_seed(s)
        facs = reg['factions']['instances']
        out.append({'npcs': [(x['id'], x['band'], list(x['member_of']), bool(x.get('power'))) for x in reg['npcs']],
                    'facs': {f['id']: (f['tier'], set(f['officers'])) for f in facs}})
    return out


def parties(w, binder_only, powers, extra_t5=False):
    out = []                             # (id, contest band, own band)
    for nid, own, mem, pw in w['npcs']:
        if pw and not powers:
            continue
        b = own
        for f in mem:
            tier, officers = w['facs'][f]
            if not binder_only or nid in officers:
                b = max(b, tier_band(tier))
        out.append((nid, b, own))
    if extra_t5:                         # an added tier-5 faction: its head (band 5, binding) and a door-warden (band 1)
        out.append(('npc.t5_head', 5, 5))
        out.append(('npc.t5_warden', 1 if binder_only else 5, 1))
    return out


def face(rng, world, rules, tb, style):
    key = (rules, getattr(style, 'greedy', False))
    if key not in world['_cache']:
        world['_cache'][key] = parties(world, rules != 'w-old', rules == 'w-new', getattr(style, 'greedy', False))
    ps = world['_cache'][key]
    if getattr(style, 'greedy', False) and rng.random() < 1 / 3:
        # the exploit: the highest band the rules will grant, then the lowest own band among those parties; the
        # frame's DC is sized to the PC (a large request of a door-warden), not to the party's band
        cap = (lambda b: b) if rules == 'w-old' else (lambda b: min(b, tb_cap[0]))
        top = max(cap(p[1]) for p in ps)
        cand = [p for p in ps if cap(p[1]) == top]
        low = min(p[2] for p in cand)
        nid, b, own = [p for p in cand if p[2] == low][0]
        return nid, b, min(5, tb_cap[0] - 1)   # the request is sized to be hard for him: DC of power band + 1
    below = [p for p in ps if p[1] <= tb]
    top = max(p[1] for p in below)
    pick_ = [p for p in below if p[1] == top]
    nid, b, own = pick_[rng.randrange(len(pick_))]
    return nid, b, b


def reflect(eng, ch, s, scene, style, sc):
    if sc % 2 == 1 or sc == 4:
        R["recognition_pass"](eng, ch, s, scene, [style.key], (), True, False)


def tiers(style, rules):
    res = {t: [] for t in range(1, 6)}
    for sd in range(1, SEEDS + 1):
        ch = run(style, rules, sd, SESSIONS)
        got = {t: 99 for t in range(1, 6)}
        for (s_, k, t, p_, c) in ch.history:
            if k == style.key and got[t] == 99:
                got[t] = s_
        for t in range(1, 6):
            res[t].append(got[t])
    return res


def med(v):
    return int(statistics.median(v))


ARCHER = Style('archer (combat calling, 03 scenario A tags)', 'fight',
               [('deed.martial.archery.bow', 75), ('deed.martial.blade.dagger', 15), ('deed.martial.athletics.acrobatics', 10)],
               ['creature.beast.predator', 'creature.folk.human', 'creature.folk.goblin', 'creature.undead.mindless',
                'creature.beast.monstrous', 'creature.undead.ravenous', 'creature.folk.giant'], 'agility')
ARCHER.key = 'deed.martial.archery'
ARCHER.mk = lambda: Char({'deed.martial.archery': 2, 'deed.wilds.tracking': 2},
                         {'agility': 3, 'might': 1, 'wits': 2, 'presence': 0, 'intellect': 0})
ENVOY = Style('envoy (social contests)', 'social',
              [('deed.influence.persuasion.argument', 50), ('deed.influence.persuasion.appeal', 25), ('deed.influence.persuasion.rapport', 25)],
              ['situation.social.parley', 'situation.social.court', 'situation.social.bargaining',
               'situation.social.interrogation', 'situation.social.performance', 'creature.folk.elf', 'creature.folk.dwarf'], 'presence')
ENVOY.key = 'deed.influence.persuasion'
ENVOY.mk = R["CH_TALK"]
SMITH = Style('smith (craft contests: works)', 'craft',
              [('deed.craft.smithing.weapons', 50), ('deed.craft.smithing.armor', 30), ('deed.craft.smithing.tools', 20)],
              ['item.weapon.blade', 'item.weapon.axe', 'item.armor.body', 'item.armor.shield', 'item.tool.implement',
               'item.weapon.polearm', 'item.tool.kit'], 'intellect')
SMITH.key = 'deed.craft.smithing'
SMITH.mk = lambda: Char({'deed.craft.smithing': 2, 'deed.craft.building': 2},
                        {'agility': 1, 'might': 3, 'wits': 1, 'presence': 0, 'intellect': 2})
SCHOLAR = Style('scholar (lore contests: sealed truths)', 'lore',
                [('deed.lore.history.legends', 40), ('deed.lore.history.ruins', 35), ('deed.lore.history.heraldry', 25)],
                ['situation.investigation.archive', 'situation.investigation.search', 'situation.exploration.ruin',
                 'situation.social.court', 'situation.investigation.interview', 'item.tool.container', 'creature.folk.elf'], 'intellect')
SCHOLAR.key = 'deed.lore.history'
SCHOLAR.mk = lambda: Char({'deed.lore.history': 2, 'deed.lore.investigation': 2},
                          {'agility': 1, 'might': 0, 'wits': 2, 'presence': 1, 'intellect': 3})
ENVOY_THIN = Style("envoy, 04's original social shape (2-4 beats, 15% Dire)", 'social', ENVOY.tags, ENVOY.ctxs, 'presence',
                   beats=(2, 4), dire=0.15)
ENVOY_THIN.key, ENVOY_THIN.mk = ENVOY.key, ENVOY.mk
ATTR['deed.craft'] = 'might'        # smithing is a Might method (08.6.4; licenses.yaml)

if __name__ == '__main__':
    print('=== I-003 parity: session at which the focus calling reaches each tier (p10/median/p90; 99 = not within %d sessions; %d seeds) ===' % (SESSIONS, SEEDS))
    rows = {}
    for style in (ARCHER, ENVOY, SMITH, SCHOLAR, ENVOY_THIN):
        for rules in (('current',) if style is ARCHER else ('current', 'revised')):
            res = tiers(style, rules)
            rows[(style.name, rules)] = res
            print('%-44s %-8s %s | T5 within %d: %d of %d' % (style.name, rules, R["line"](res), SESSIONS,
                                                             sum(1 for x in res[5] if x < 99), SEEDS))
    a3, a5 = med(rows[(ARCHER.name, 'current')][3]), med(rows[(ARCHER.name, 'current')][5])
    print()
    print('| Calling | rules | median T3 | vs archer | median T5 | vs archer | within +-20%% at both |')
    print('|---|---|---|---|---|---|---|')
    print('| %s | (combat) | %d | - | %d | - | - |' % (ARCHER.name, a3, a5))
    for style in (ENVOY, SMITH, SCHOLAR, ENVOY_THIN):
        for rules in ('current', 'revised'):
            r3, r5 = med(rows[(style.name, rules)][3]), med(rows[(style.name, rules)][5])
            ok = abs(r3 - a3) <= 0.2 * a3 and abs(r5 - a5) <= 0.2 * a5
            print('| %s | %s | %d | %+.0f%% | %s | %s | %s |' % (style.name, rules, r3, 100.0 * (r3 - a3) / a3,
                  r5 if r5 < 99 else 'never', ('%+.0f%%' % (100.0 * (r5 - a5) / a5)) if r5 < 99 else '-', 'yes' if ok else 'no'))
    # ---- revision C2a: I-083 / I-039 / I-037 in seeded worlds
    print()
    WORLDS.extend(build_worlds())
    for w in WORLDS:
        w['_cache'] = {}
    mx_old = max(b for w in WORLDS for _, b, _o in parties(w, False, False))
    mx_new = max(b for w in WORLDS for _, b, _o in parties(w, True, True))
    n5 = statistics.median([sum(1 for _, b, _o in parties(w, True, True) if b == 5) for w in WORLDS])
    n4 = statistics.median([sum(1 for _, b, _o in parties(w, True, True) if b == 4) for w in WORLDS])
    print('=== I-083 / I-039 / I-037 (revision C2a): contest opposition from %d seeded worlds; power band from confirmed tiers ===' % len(WORLDS))
    print('  highest party band in any world: old seed %d; revised seed %d (median per world: %s at band 4, %s at band 5)' % (mx_old, mx_new, n4, n5))
    MODE['confirmed'] = True
    wrows = {}
    for style in (ARCHER, ENVOY, SMITH, SCHOLAR):
        for rules in (('w-new',) if style is ARCHER else ('w-old', 'w-new-nopowers', 'w-new')):
            MODE['cap_opp'] = rules != 'w-old'
            res = tiers(style, rules)
            wrows[(style.name, rules)] = res
            print('%-44s %-15s %s | T5 within %d: %d of %d' % (style.name, rules, R["line"](res), SESSIONS,
                                                                sum(1 for x in res[5] if x < 99), SEEDS))
    a3, a5 = med(wrows[(ARCHER.name, 'w-new')][3]), med(wrows[(ARCHER.name, 'w-new')][5])
    print()
    print('| Calling | rules | median T3 | vs archer | median T4 | median T5 | vs archer | within +-20%% at both |')
    print('|---|---|---|---|---|---|---|---|')
    print('| %s | (combat, confirmed band) | %d | - | %d | %d | - | - |' % (ARCHER.name, a3, med(wrows[(ARCHER.name, 'w-new')][4]), a5))
    for style in (ENVOY, SMITH, SCHOLAR):
        for rules in ('w-old', 'w-new-nopowers', 'w-new'):
            r = wrows[(style.name, rules)]
            r3, r4, r5 = med(r[3]), med(r[4]), med(r[5])
            ok = abs(r3 - a3) <= 0.2 * a3 and r5 < 99 and abs(r5 - a5) <= 0.2 * a5
            print('| %s | %s | %s | %s | %s | %s | %s | %s |' % (style.name, rules, r3 if r3 < 99 else 'never', ('%+.0f%%' % (100.0 * (r3 - a3) / a3)) if r3 < 99 else '-',
                  r4 if r4 < 99 else 'never', r5 if r5 < 99 else 'never', ('%+.0f%%' % (100.0 * (r5 - a5) / a5)) if r5 < 99 else '-', 'yes' if ok else 'no'))
    print()
    print('I-039 exploit: a farming envoy (the envoy above, but one contest scene in three goes to the highest band the rules grant, at')
    print('a DC of power band + 1) in worlds with an added tier-5 faction (head band 5, binding; door-warden band 1, not binding)')
    GREEDY = Style('farming envoy (tier-5 door-warden on offer)', 'social', ENVOY.tags, ENVOY.ctxs, 'presence')
    GREEDY.key, GREEDY.mk, GREEDY.greedy = ENVOY.key, ENVOY.mk, True
    for rules in ('w-old', 'w-new'):
        MODE['cap_opp'] = rules != 'w-old'
        res = tiers(GREEDY, rules)
        early = []
        for sd in range(1, SEEDS + 1):          # band-4/5 deeds banked in sessions 1-10 (power band 1-2 throughout)
            h = {}
            run(GREEDY, rules, sd, 10, eng_out=h)
            early.append(sum(1 for r in h['eng'].log[GREEDY.key] if r[1] >= 4))
        print('  %-15s %s | T5 within %d: %d of %d | band-4/5 deeds in sessions 1-10: median %d' % (
            rules, R["line"](res), SESSIONS, sum(1 for x in res[5] if x < 99), SEEDS, statistics.median(early)))
    MODE['confirmed'] = MODE['cap_opp'] = False
    # ---- R9 (issue I-004): counted / weighted at the key after 10 sessions, by pillar and rule set
    print()
    print('=== R9 (I-004): counted / weighted at the focus key after 10 sessions (p10/median/p90 of the ratio; %d seeds) ===' % SEEDS)
    for style in (ARCHER, ENVOY, SMITH, SCHOLAR):
        for rules in (('current',) if style is ARCHER else ('current', 'revised')):
            ratios = []
            for sd in range(1, SEEDS + 1):
                eng_holder = {}
                run(style, rules, sd, 10, eng_out=eng_holder)
                e = eng_holder['eng']
                ratios.append(round(e.counted[style.key] / max(1, e.weighted[style.key]), 3))
            v = sorted(ratios)
            print('  %-44s %-8s %.2f / %.2f / %.2f' % (style.name, rules, v[len(v) // 10], statistics.median(v), v[9 * len(v) // 10]))
