"""world11.py -- simulation of chapter 11's World Turn / Season Turn for 2 in-game years.

Rules as written in rules/11-living-world.md (11.2-11.11) and data/world_turn.yaml, data/factions.yaml:
- faction check: d20 + rating + 2*tier + stage_mod vs DC; degrees by 00.3.10 (crit +-10, nat20/1 step);
  near miss = failure with margin >= -3.
- goal clock ticks: crit 3 / success 2 / near-miss 1 / failure 0 / crit-fail 0 + slip (trace, next action recover).
- strike: DC = 10 + defender max(force, cunning) + 2*defender tier (+1 entrenched); success: defender loses hold
  (strong->weak; weak -> tier-1 and strong); crit: + one hold place seized; crit fail: attacker loses hold.
- goal completion: grow -> hold up (weak->strong; strong -> tier+1 weak), dominate -> target loses hold,
  change -> a situation seeded (hook). New goal drawn.
- minor factions: d6/week: 4-5 +1, 6 +2 on a 6-clock; completion -> a hook.
- PC: pursues threads; status moves; attention clocks per faction (8, decay 1/week w/o tick).
- threads: seeded hooks expire after 8 weeks unactivated; active register <= 12; PC pursues <= 3;
  situation threads race an opposing clock (6 segments, +1/week default timeline).
- hook supply: if PC-known open hooks (seeded+active) < 3 at the World Turn, generate one (step 8).
- season turn: stage transitions; seasonal event (d12: 1-4 a new situation hook).
"""
import random, statistics, sys

SEEDS = int(sys.argv[1]) if len(sys.argv) > 1 else 300
WEEKS = 104

def degree(d20, total, dc):
    m = total - dc
    if m >= 10: deg = 3
    elif m >= 0: deg = 2
    elif m > -10: deg = 1
    else: deg = 0
    if d20 == 20: deg = min(3, deg + 1)
    if d20 == 1: deg = max(0, deg - 1)
    near = (deg == 1 and m >= -3)
    return deg, near  # 3 crit success, 2 success, 1 failure, 0 crit failure

STAGE_MOD = {'rising': 1, 'flourishing': 0, 'entrenched': -1, 'declining': -1, 'collapsed': -9}
GOAL_SCOPE = {'local': 3, 'regional': 5, 'realm': 7}
GOAL_SIZE = {'local': 8, 'regional': 12, 'realm': 24}

class Faction:
    def __init__(s, fid, tier, ratings, temper, stage='flourishing'):
        s.id = fid; s.tier = tier; s.hold = 1; s.r = dict(ratings); s.temper = temper; s.stage = stage
        s.goal = None; s.filled = 0; s.rel = {}; s.status = 0; s.attention = 0; s.pursuit = 0
        s.completions = 0; s.tier_changes = 0; s.seasons_in_stage = 0; s.hold_losses_year = 0
        s.slip = False; s.alive = True
        s.new_goal()
    def new_goal(s, rng=None):
        rng = rng or random
        if s.tier <= 1: scope = 'local'
        elif s.tier <= 3: scope = rng.choice(['local', 'regional'])
        else: scope = rng.choice(['regional', 'realm'])
        kind = rng.choice(['grow', 'grow', 'dominate', 'change', 'change', 'change'])
        s.goal = (scope, kind); s.filled = 0
    def rating_for(s, kind):
        if kind == 'goal':
            return max(s.r.values())  # the goal's governing rating is the faction's best fit (data names it)
        return s.r[kind]

def check(rng, f, rating, dc):
    d = rng.randint(1, 20)
    total = d + rating + 2 * f.tier + STAGE_MOD[f.stage]
    total = max(-8, min(16, total - d)) + d  # modifier clamp -8..+16
    return degree(d, total, dc)

def lose_hold(f, stats):
    f.hold_losses_year += 1
    if f.hold == 1:
        f.hold = 0
    else:
        if f.tier == 0:
            f.alive = False; f.stage = 'collapsed'; stats['collapses'] += 1; return
        f.tier -= 1; f.hold = 1; f.tier_changes += 1; stats['tier_down'] += 1
        cap = f.tier + 2
        for k in f.r: f.r[k] = min(f.r[k], cap)

def gain_hold(f, stats, realm_grow=False):
    # 11.3.4: gaining hold goes weak -> strong; from strong the faction rises one tier with a weak hold, but rising
    # above tier 3 needs a completed grow goal of realm scope: any other gain at tier 3+ only makes the hold strong.
    # (Integration fix, issue I-026: the first version let expand and court raise a tier-3+ faction.)
    if f.hold == 0: f.hold = 1
    elif f.tier < 3 or (realm_grow and f.tier < 5):
        f.tier += 1; f.hold = 0; f.tier_changes += 1; stats['tier_up'] += 1

AGENDA = {  # d6 -> action (first row whose condition holds; else 'goal')
    'aggressive': {1: 'strike', 2: 'strike', 3: 'move_pc', 4: 'goal', 5: 'goal', 6: 'goal'},
    'cautious':   {1: 'recover', 2: 'scheme', 3: 'goal', 4: 'goal', 5: 'goal', 6: 'goal'},
    'mercantile': {1: 'expand', 2: 'scheme', 3: 'goal', 4: 'goal', 5: 'goal', 6: 'goal'},
    'zealous':    {1: 'strike', 2: 'court', 3: 'goal', 4: 'goal', 5: 'goal', 6: 'goal'},
    'secretive':  {1: 'scheme', 2: 'scheme', 3: 'move_pc', 4: 'goal', 5: 'goal', 6: 'goal'},
    # 11.3.7's steadfast row (integration, I-026): 1 recover if weak; 2 aid_pc (modelled as goal); 3 strike (a rival at -3); 4-6 goal
    'steadfast':  {1: 'recover', 2: 'goal', 3: 'strike', 4: 'goal', 5: 'goal', 6: 'goal'},
}

def run(seed, scenario='engaged'):
    rng = random.Random(seed)
    stats = dict(collapses=0, tier_up=0, tier_down=0, goal_done=0, strikes=0, strike_hits=0,
                 entanglements=0, moves_on_pc=0, hooks_seeded=0, hooks_expired=0, threads_completed=0,
                 threads_failed=0, threads_activated=0, threads_retired=0, rumors=0, strain_losses=0, max_known_hooks=0,
                 weeks_known_lt3=0, bangs_max=0, situations=0, new_factions=0, slips=0)
    facs = [Faction('salt_guild', 2, {'force': 2, 'cunning': 3, 'wealth': 4, 'sway': 2}, 'mercantile'),
            Faction('ash_wardens', 1, {'force': 3, 'cunning': 2, 'wealth': 1, 'sway': 2}, 'zealous', 'rising'),
            Faction('margrave', 3, {'force': 4, 'cunning': 3, 'wealth': 3, 'sway': 4}, 'cautious', 'entrenched'),
            Faction('ember_cult', 1, {'force': 2, 'cunning': 3, 'wealth': 1, 'sway': 1}, 'secretive', 'rising')]
    for f in facs:
        for g in facs:
            if f is not g: f.rel[g.id] = 0
    def setrel(a, b, v):
        for f in facs:
            if f.id == a: f.rel[b] = v
            if f.id == b: f.rel[a] = v
    setrel('salt_guild', 'ash_wardens', -2); setrel('margrave', 'ember_cult', -2); setrel('ash_wardens', 'ember_cult', -3)
    minors = [{'filled': 0} for _ in range(3)]
    # PC: helps the wardens, opposes the cult
    pc_side = {'ash_wardens': 1, 'ember_cult': -1}
    seeded = []   # [age_weeks]
    active = []   # dicts: size, filled, opp (opposing clock or None), opp_filled
    bangs = 0
    for week in range(1, WEEKS + 1):
        # --- PC play this week (between turns) ---
        pc_active = (rng.random() < 0.7) and scenario != 'absent'
        if pc_active and active:
            t = active[0]  # pursue highest weight
            beats = rng.choice([1, 2, 2, 3])
            for _ in range(beats):
                d = rng.randint(1, 20); dg, near = degree(d, d + 5, 15)
                t['filled'] += {3: 3, 2: 2, 1: (1 if near else 0), 0: 0}[dg]
            if t['filled'] >= t['size']:
                active.remove(t); stats['threads_completed'] += 1
                if t.get('fac') in [f.id for f in facs]:
                    for f in facs:
                        if f.id == t['fac']: f.status = min(3, f.status + 1)
                if t.get('against'):
                    for f in facs:
                        if f.id == t['against']:
                            f.status = max(-3, f.status - 1); f.attention = min(8, f.attention + 2)
        # activate hooks: the PC takes up a seeded hook when pursuing < 2 threads
        while len(active) < 2 and seeded and scenario != 'absent':
            seeded.pop(0); stats['threads_activated'] += 1
            size = rng.choice([4, 6, 6, 8, 8, 12])
            opp = rng.random() < 0.5
            fac = rng.choice(['ash_wardens', 'margrave', None, None])
            against = rng.choice(['ember_cult', 'salt_guild', None])
            active.append({'size': size, 'filled': 0, 'opp': opp, 'opp_filled': 0, 'fac': fac, 'against': against})
        # --- WORLD TURN ---
        # step 2 maintain: nothing numeric here (upkeep is holdings)
        # step 3 timelines: opposing clocks of situation threads
        for t in list(active):
            if t['opp']:
                t['opp_filled'] += 1
                if t['opp_filled'] >= 6 and t in active:
                    active.remove(t); stats['threads_failed'] += 1; seeded.append(0); stats['hooks_seeded'] += 1  # failure opens a new situation
        # step 4 faction actions
        for f in facs:
            if not f.alive: continue
            roll = rng.randint(1, 6)
            act = AGENDA[f.temper][roll]
            enemies = [g for g in facs if g.alive and g is not f and f.rel.get(g.id, 0) <= -2]
            if f.slip: act = 'recover'; f.slip = False
            if act == 'strike' and not enemies: act = 'goal'
            if act == 'move_pc' and not (f.status <= -2 and f.attention >= 4): act = 'goal'
            if act == 'recover' and f.hold == 1: act = 'goal'
            if act == 'court': act = 'goal' if rng.random() < 0.5 else 'court'
            if act == 'goal':
                scope, kind = f.goal
                dg, near = check(rng, f, f.rating_for('goal'), 10 + 2 * f.tier + GOAL_SCOPE[scope])
                ticks = {3: 2, 2: 1, 1: 0, 0: 0}[dg]
                if dg == 0: f.slip = True; stats['slips'] += 1; stats['rumors'] += 1
                f.filled += ticks
                if ticks: stats['rumors'] += 1  # omen/trace
                if f.filled >= GOAL_SIZE[scope]:
                    f.completions += 1; stats['goal_done'] += 1; stats['rumors'] += 1
                    if kind == 'grow' and not (f.hold == 1 and f.tier >= 3 and scope != 'realm'): gain_hold(f, stats, realm_grow=(scope == 'realm'))
                    elif kind == 'grow': f.hold = 1
                    elif kind == 'dominate' and enemies:
                        lose_hold(rng.choice(enemies), stats)
                    else:
                        seeded.append(0); stats['hooks_seeded'] += 1; stats['situations'] += 1
                    if f.stage in ('declining',): f.stage = 'rising'; f.seasons_in_stage = 0
                    f.new_goal(rng)
            elif act == 'strike':
                tgt = rng.choice(enemies); stats['strikes'] += 1
                dc = 10 + max(tgt.r['force'], tgt.r['cunning']) + 2 * tgt.tier + (1 if tgt.stage == 'entrenched' else 0)
                dg, near = check(rng, f, f.r['force'], dc)
                if dg >= 2:
                    stats['strike_hits'] += 1; lose_hold(tgt, stats); stats['rumors'] += 1
                elif dg == 0:
                    lose_hold(f, stats); stats['rumors'] += 1
            elif act == 'expand':
                dg, near = check(rng, f, f.r['wealth'], 15 + 2 * f.tier)
                if dg >= 2: gain_hold(f, stats); stats['rumors'] += 1
            elif act == 'recover':
                dg, near = check(rng, f, max(f.r['wealth'], f.r['sway']), 15)
                if dg >= 2: f.hold = 1
            elif act == 'scheme':
                if enemies:
                    tgt = rng.choice(enemies)
                    dg, near = check(rng, f, f.r['cunning'], 10 + tgt.r['cunning'] + 2 * tgt.tier)
                    if dg >= 2: f.filled += 1; stats['rumors'] += 1
                else:
                    f.filled += 1
            elif act == 'move_pc':
                stats['moves_on_pc'] += 1; bangs += 1
            elif act == 'court':
                stats['rumors'] += 1
        # minors
        for m in minors:
            r = rng.randint(1, 6)
            m['filled'] += 2 if r == 6 else (1 if r >= 4 else 0)
            if m['filled'] >= 6:
                m['filled'] = 0; seeded.append(0); stats['hooks_seeded'] += 1; stats['rumors'] += 1
        # step 6 attention
        for f in facs:
            if not f.alive: continue
            war = (scenario == 'war' and f.id == 'ember_cult')
            if pc_active and war:
                loud = rng.choices([0, 1, 2, 3], [40, 30, 20, 10])[0]
                tick = loud + (1 if (loud and f.status <= -3) else 0)
                if loud >= 2: f.status = max(-3, f.status - 1)
                if tick: f.attention = min(8, f.attention + tick)
                elif f.attention > 0: f.attention -= 1
            elif pc_active and f.id in pc_side and pc_side[f.id] < 0 and rng.random() < 0.4:
                f.attention = min(8, f.attention + rng.choice([1, 1, 2]))
                f.status = max(-3, f.status - (1 if rng.random() < 0.15 else 0))
            elif f.attention > 0:
                f.attention -= 1
            if f.attention >= 8:
                f.attention = 0; f.pursuit = min(3, f.pursuit + 1); stats['entanglements'] += 1; bangs += 1
        # step 8 queue: bangs expire after 4 weeks (approximation: half fire each week)
        bangs = min(6, bangs)
        stats['bangs_max'] = max(stats['bangs_max'], bangs)
        bangs = bangs // 2
        # thread register upkeep: seeded hooks age and expire at 8 weeks
        seeded = [a + 1 for a in seeded]
        exp = [a for a in seeded if a > 8]
        stats['hooks_expired'] += len(exp)
        seeded = [a for a in seeded if a <= 8]
        # cap: seeded <= 12
        while len(seeded) > 8:
            seeded.pop(0); stats['hooks_expired'] += 1
        # hook supply rule
        known = len(seeded) + len(active)
        if known < 3:
            stats['weeks_known_lt3'] += 1
            seeded.append(0); stats['hooks_seeded'] += 1
        stats['max_known_hooks'] = max(stats['max_known_hooks'], len(seeded) + len(active))
        # --- SEASON TURN ---
        if week % 13 == 0:
            for f in facs:
                if not f.alive: continue
                f.seasons_in_stage += 1
                if f.tier >= 3:
                    d = rng.randint(1, 20)
                    if d + max(f.r.values()) + STAGE_MOD[f.stage] < 10 + 2 * f.tier: lose_hold(f, stats); stats['strain_losses'] = stats.get('strain_losses', 0) + 1
                if not f.alive: continue
                if f.stage == 'rising' and (f.completions >= 1 or f.seasons_in_stage >= 4):
                    f.stage = 'flourishing'; f.seasons_in_stage = 0
                elif f.stage == 'flourishing' and (f.tier >= 4 or f.seasons_in_stage >= 8):
                    f.stage = 'entrenched'; f.seasons_in_stage = 0
                elif f.stage in ('entrenched', 'flourishing') and f.hold_losses_year >= 2:
                    f.stage = 'declining'; f.seasons_in_stage = 0
                if week % 52 == 0: f.hold_losses_year = 0
                # pursuit decays if no entanglement this season (approx: 50%)
                if f.pursuit and rng.random() < 0.5: f.pursuit -= 1
            # seasonal event: d12 1-4 a new situation
            if rng.randint(1, 12) <= 4:
                seeded.append(0); stats['hooks_seeded'] += 1; stats['situations'] += 1
            # vacuum: a collapsed faction seeds a rising one
            for i, f in enumerate(facs):
                if not f.alive:
                    stats['new_factions'] += 1
                    nf = Faction('new%d' % week, 1, {'force': 2, 'cunning': 2, 'wealth': 2, 'sway': 2},
                                 rng.choice(list(AGENDA)), 'rising')
                    nf.rel = {g.id: 0 for g in facs if g is not f}
                    facs[i] = nf
    stats['final_tiers'] = [f.tier for f in facs]
    stats['completions_by_fac'] = [f.completions for f in facs]
    stats['open_active_end'] = len(active); stats['open_seeded_end'] = len(seeded)
    return stats

def q(xs):
    xs = sorted(xs); n = len(xs)
    return (xs[n // 10], statistics.median(xs), xs[(9 * n) // 10])

if __name__ == '__main__':
  for scenario in ['engaged', 'war', 'absent']:
    runs = [run(s, scenario) for s in range(SEEDS)]
    print('=== scenario: %s ===' % scenario)
    keys = ['goal_done', 'tier_up', 'tier_down', 'collapses', 'new_factions', 'strikes', 'strike_hits', 'slips',
            'entanglements', 'moves_on_pc', 'hooks_seeded', 'threads_activated', 'threads_completed', 'threads_failed',
            'hooks_expired', 'rumors', 'situations', 'max_known_hooks', 'weeks_known_lt3', 'bangs_max',
            'open_active_end', 'open_seeded_end', 'strain_losses']
    print('World simulation, %d seeds x %d weeks (2 years); p10 / median / p90 per 2 years' % (SEEDS, WEEKS))
    for k in keys:
        print('%-20s %s' % (k, q([r[k] for r in runs])))
    comp = [c for r in runs for c in r['completions_by_fac']]
    print('goal completions per faction per 2y: p10/med/p90', q(comp))
    tiers = [t for r in runs for t in r['final_tiers']]
    from collections import Counter
    print('final tier distribution (start 2,1,3,1):', sorted(Counter(tiers).items()))
    print('max tier reached anywhere: ', max(tiers))
