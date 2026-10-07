"""world11.py -- simulation of chapter 11's World Turn / Season Turn for 2 in-game years.

Rules as written in rules/11-living-world.md (11.2-11.11) and data/world_turn.yaml, data/factions.yaml:
- faction check: d20 + rating + 2*tier + stage_mod vs DC (entrenched -1 on goal and expand only, +1 to the DC of
  strike, scheme and court against it, 0 elsewhere including the weight of size [revision: I-068]); degrees by 00.3.10 (crit +-10, nat20/1 step);
  near miss = failure with margin >= -3.
- goal clock ticks (11.3.6): crit +2 / success +1 / failure 0 / crit-fail 0 + slip (trace, next action recover).
- agenda (11.3.7, exactly; revision I-032): overrides first (a) slip -> recover, (b) at war (relation -3; every faction
  here shares the region) and d6 1-3 -> strike that faction, (c) status >= +2 -> aid_pc (the opportunity bang
  eligible only on a d6 of 1 unless a ransom, holding threat or reward is due; none is modelled); else the temperament row of factions.yaml#agenda with its conditions; a failed condition reads as goal.
  Targets: strike/scheme the eligible rival with the lowest relation, then fullest goal clock, highest tier, lowest id;
  court the non-rival (relation 0..+1) with the highest relation (no allies are modelled), else goal.
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
- [revision: I-080] the rumor-planting test (scenarios `liar_old`, `liar_new`; printed after the three base scenarios,
  which are unchanged): the PC plants one false rumor a week (11.6.9), the margrave's rival the salt guild in the
  margrave's seat and the reverse in the guild's (the pair starts at relation 0); each arrival rolls
  wr.rumor_believed (acts_on_it 2 : nothing 3). `liar_old` is the rule before I-080 (-1 a belief, no floor, no
  cooldown); `liar_new` the rule after it (11.3.14: rumors move a relation no lower than -2; acts_on_it at most once
  a season per faction toward one rival). In both liar scenarios a successful strike also applies 11.3.14's
  defender row (-1, -2 on a critical success), which the base scenarios leave out, so a war can still come from a
  real blow.
"""
import random, statistics, sys
from collections import Counter

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

STAGE_MOD = {'rising': 1, 'flourishing': 0, 'entrenched': 0, 'declining': -1, 'collapsed': -9}
# [revision: I-068] 11.3.5: entrenched is -1 on `goal` and `expand` only (complacency) and +1 to its own defense (the DC
# of strike, scheme and court against it); on every other check, and on 11.3.9's weight of size, it reads 0.
def stage_mod(f, action=None):
    if f.stage == 'entrenched' and action in ('goal', 'expand'): return -1
    return STAGE_MOD[f.stage]
GOAL_SCOPE = {'local': 3, 'regional': 5, 'realm': 7}
GOAL_SIZE = {'local': 8, 'regional': 12, 'realm': 24}

class Faction:
    def __init__(s, fid, tier, ratings, temper, stage='flourishing'):
        s.id = fid; s.tier = tier; s.hold = 1; s.r = dict(ratings); s.temper = temper; s.stage = stage
        s.goal = None; s.filled = 0; s.rel = {}; s.status = 0; s.attention = 0; s.pursuit = 0
        s.lie_cool = {}   # [revision: I-080] week acts_on_it last fired toward each rival
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

def check(rng, f, rating, dc, action=None):
    d = rng.randint(1, 20)
    total = d + rating + 2 * f.tier + stage_mod(f, action)   # [revision: I-068]
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

# 11.3.7's temperament rows, cell for cell (factions.yaml#agenda.rows) [revision: I-032]. Each cell is (action, condition);
# a condition that fails reads as 'goal'. Conditions: ('rival', n) a rival at relation <= n; ('rival_eq', -3) a rival at
# exactly -3; ('weak',) hold weak; ('status_le', n[, 'attention_half']) status toward the PC <= n (and its attention clock
# at half or more); ('status_ge', 2); ('imminent',) its attention clock on the PC imminent; None: always.
AGENDA = {
    'aggressive': {1: ('strike', ('rival', -2)), 2: ('strike', ('rival', -2)), 3: ('move_pc', ('status_le', -2, 'pc_in_region')),
                   4: ('expand', None), 5: ('goal', None), 6: ('goal', None)},
    'cautious':   {1: ('recover', ('weak',)), 2: ('scheme', ('rival', -1)), 3: ('court', None),
                   4: ('goal', None), 5: ('goal', None), 6: ('goal', None)},
    'mercantile': {1: ('expand', None), 2: ('scheme', ('rival', -1)), 3: ('court', None),
                   4: ('goal', None), 5: ('goal', None), 6: ('goal', None)},
    'zealous':    {1: ('strike', ('rival', -2)), 2: ('court', None), 3: ('move_pc', ('status_le', -2)),
                   4: ('goal', None), 5: ('goal', None), 6: ('goal', None)},
    'secretive':  {1: ('scheme', ('rival', -1)), 2: ('scheme', ('rival', -1)), 3: ('move_pc', ('status_le', -1, 'attention_half')),
                   4: ('lie_low', ('imminent',)), 5: ('goal', None), 6: ('goal', None)},
    'steadfast':  {1: ('recover', ('weak',)), 2: ('aid_pc', ('status_ge', 2)), 3: ('strike', ('rival_eq', -3)),
                   4: ('goal', None), 5: ('goal', None), 6: ('goal', None)},
}
ATTENTION_SIZE = 8   # 11.3.12; half = 4 filled; imminent = remaining <= max(1, 8 // 4) = 2, i.e. 6 filled

def rank_rivals(f, cands):
    # 11.3.7 targets: lowest relation, then the fullest goal clock, then the highest tier, then the lowest id
    return sorted(cands, key=lambda g: (f.rel.get(g.id, 0), -g.filled, -g.tier, g.id))

def choose_action(rng, f, facs, pc_in_region=True):
    """11.3.7 exactly: (action, target). Overrides (a)-(c) first, then the d6 on the temperament row."""
    others = [g for g in facs if g.alive and g is not f]
    if f.slip:                                                     # (a)
        return 'recover', None
    war = [g for g in others if f.rel.get(g.id, 0) <= -3]
    if war:                                                        # (b): the d6 is rolled only when a war exists
        if rng.randint(1, 6) <= 3:
            return 'strike', rank_rivals(f, war)[0]
    if f.status >= 2 and rng.randint(1, 6) == 1:                    # (c): no ransom, holding or reward is modelled,
        return 'aid_pc', None                                      #      so only the d6 = 1 opportunity bang fires
    act, cond = AGENDA[f.temper][rng.randint(1, 6)]
    tgt = None
    ok = True
    if cond:
        c = cond[0]
        if c == 'rival':
            el = [g for g in others if f.rel.get(g.id, 0) <= cond[1]]
            ok = bool(el); tgt = rank_rivals(f, el)[0] if el else None
        elif c == 'rival_eq':
            el = [g for g in others if f.rel.get(g.id, 0) == cond[1]]
            ok = bool(el); tgt = rank_rivals(f, el)[0] if el else None
        elif c == 'weak':
            ok = f.hold == 0
        elif c == 'status_le':
            ok = f.status <= cond[1]
            if ok and len(cond) > 2 and cond[2] == 'attention_half': ok = f.attention >= ATTENTION_SIZE // 2
            if ok and len(cond) > 2 and cond[2] == 'pc_in_region': ok = pc_in_region
        elif c == 'status_ge':
            ok = f.status >= cond[1]
        elif c == 'imminent':
            ok = ATTENTION_SIZE - f.attention <= max(1, ATTENTION_SIZE // 4)
    if ok and act == 'court':                                      # court target (ii); (i) allies are not modelled
        el = [g for g in others if 0 <= f.rel.get(g.id, 0) < 2]
        if el:
            tgt = sorted(el, key=lambda g: (-f.rel.get(g.id, 0), -g.tier, g.id))[0]
        else:
            ok = False                                             # (iii) else goal
    if not ok:
        return 'goal', None
    return act, tgt

def run(seed, scenario='engaged'):
    rng = random.Random(seed)
    random.seed(seed)  # Faction.__init__ draws its first goal from the module RNG; seeding it makes every run reproducible (integration, I-026)
    stats = dict(collapses=0, tier_up=0, tier_down=0, goal_done=0, strikes=0, strike_hits=0,
                 entanglements=0, moves_on_pc=0, hooks_seeded=0, hooks_expired=0, threads_completed=0,
                 threads_failed=0, threads_activated=0, threads_retired=0, rumors=0, strain_losses=0, max_known_hooks=0,
                 weeks_known_lt3=0, bangs_max=0, situations=0, new_factions=0, slips=0,
                 acts={k: 0 for k in ('goal', 'strike', 'scheme', 'expand', 'recover', 'court', 'move_pc', 'aid_pc', 'lie_low')},
                 courts_won=0, cult_weeks=WEEKS, wardens_weeks=WEEKS,
                 lie_war_week=WEEKS + 1, lie_moves=0, lie_strikes_before_war=0, lie_min_rel=0)
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
        # --- the PC's planted rumors [revision: I-080] ---
        if scenario.startswith('liar'):
            for a, b in (('margrave', 'salt_guild'), ('salt_guild', 'margrave')):
                fa = [f for f in facs if f.id == a and f.alive]
                if not fa or not any(g.id == b and g.alive for g in facs):
                    continue
                fa = fa[0]
                if rng.random() < 2.0 / 5.0:                         # acts_on_it 2 : nothing 3
                    if scenario == 'liar_old':
                        fa.rel[b] = max(-3, fa.rel.get(b, 0) - 1); stats['lie_moves'] += 1
                    elif week - fa.lie_cool.get(b, -99) >= 13 and fa.rel.get(b, 0) > -2:
                        fa.rel[b] = max(-2, fa.rel.get(b, 0) - 1); fa.lie_cool[b] = week; stats['lie_moves'] += 1
            for f in facs:
                if f.id == 'margrave' and f.alive:
                    stats['lie_min_rel'] = min(stats['lie_min_rel'], f.rel.get('salt_guild', 0))
                    if f.rel.get('salt_guild', 0) <= -3 and stats['lie_war_week'] > WEEKS:
                        stats['lie_war_week'] = week
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
            enemies = [g for g in facs if g.alive and g is not f and f.rel.get(g.id, 0) <= -2]  # dominate goals' targets
            act, tgt = choose_action(rng, f, facs)       # 11.3.7 [revision: I-032]
            stats['acts'][act] += 1
            if act == 'goal':
                scope, kind = f.goal
                dg, near = check(rng, f, f.rating_for('goal'), 10 + 2 * f.tier + GOAL_SCOPE[scope], 'goal')
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
                stats['strikes'] += 1
                dc = 10 + max(tgt.r['force'], tgt.r['cunning']) + 2 * tgt.tier + (1 if tgt.stage == 'entrenched' else 0)
                dg, near = check(rng, f, f.r['force'], dc)
                if dg >= 2:
                    stats['strike_hits'] += 1; lose_hold(tgt, stats); stats['rumors'] += 1
                    if scenario.startswith('liar'):              # 11.3.14's defender row [revision: I-080]
                        tgt.rel[f.id] = max(-3, tgt.rel.get(f.id, 0) - (2 if dg == 3 else 1))
                        if {f.id, tgt.id} == {'margrave', 'salt_guild'} and stats['lie_war_week'] > WEEKS:
                            stats['lie_strikes_before_war'] += 1
                elif dg == 0:
                    lose_hold(f, stats); stats['rumors'] += 1
            elif act == 'expand':
                dg, near = check(rng, f, f.r['wealth'], 15 + 2 * f.tier, 'expand')
                if dg >= 2: gain_hold(f, stats); stats['rumors'] += 1
            elif act == 'recover':                        # 11.3.6: DC 10 + 2 x tier + 3; success clears the slip
                dg, near = check(rng, f, max(f.r['wealth'], f.r['sway']), 13 + 2 * f.tier)
                if dg >= 2: f.hold = 1; f.slip = False
                if dg == 3: f.filled += 1
            elif act == 'scheme':
                dg, near = check(rng, f, f.r['cunning'], 10 + tgt.r['cunning'] + 2 * tgt.tier + (1 if tgt.stage == 'entrenched' else 0))   # [revision: I-068] 11.3.5's +1
                if dg >= 2: f.filled += 1; stats['rumors'] += 1   # the inside lever, spent toward its goal
                elif dg == 0: tgt.rel[f.id] = max(-3, tgt.rel.get(f.id, 0) - 1)   # discovered
            elif act == 'move_pc':
                stats['moves_on_pc'] += 1; bangs += 1
            elif act == 'court':                          # 11.3.6: sway vs 10 + the target's sway + 2 x its tier
                dg, near = check(rng, f, f.r['sway'], 10 + tgt.r['sway'] + 2 * tgt.tier + (1 if tgt.stage == 'entrenched' else 0))
                if dg >= 2:
                    tgt.rel[f.id] = min(3, tgt.rel.get(f.id, 0) + 1); f.rel[tgt.id] = min(3, f.rel.get(tgt.id, 0) + 1)
                    stats['courts_won'] += 1; stats['rumors'] += 1
                elif dg == 0:
                    tgt.rel[f.id] = max(-3, tgt.rel.get(f.id, 0) - 1)
            elif act == 'aid_pc':                         # an opportunity bang (11.3.6)
                bangs += 1
            elif act == 'lie_low':                        # its attention clock decays 1 extra (11.3.6)
                f.attention = max(0, f.attention - 1)
        for fid, key in (('ember_cult', 'cult_weeks'), ('ash_wardens', 'wardens_weeks')):   # the war's length [revision: I-032]
            if stats[key] == WEEKS and not any(g.id == fid and g.alive for g in facs): stats[key] = week
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
                    if d + max(f.r.values()) + stage_mod(f) < 10 + 2 * f.tier:   # [revision: I-068] entrenched reads 0
                        lose_hold(f, stats); stats['strain_losses'] = stats.get('strain_losses', 0) + 1
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
  for scenario in ['engaged', 'war', 'absent', 'liar_old', 'liar_new']:
    if scenario.startswith('liar'):                                 # [revision: I-080]
        runs = [run(s, scenario) for s in range(SEEDS)]
        ww = [r['lie_war_week'] for r in runs]
        print('=== scenario: %s (one planted rumor a week about the margrave / salt guild pair, relation 0 at start) ===' % scenario)
        print('runs at war (-3, margrave toward the guild) within 1 season / 1 year / 2 years: %d / %d / %d of %d' % (
            sum(1 for w in ww if w <= 13), sum(1 for w in ww if w <= 52), sum(1 for w in ww if w <= WEEKS), SEEDS))
        warw = [w for w in ww if w <= WEEKS]
        print('week war began, among runs that reached it: p10/med/p90 %s' % (str(q(warw)) if warw else '-'))
        print('relation moves by belief per 2y p10/med/p90 %s; lowest relation reached: %s' % (
            str(q([r['lie_moves'] for r in runs])), sorted(Counter(r['lie_min_rel'] for r in runs).items())))
        print('runs whose war followed at least one successful strike between the pair: %d of %d' % (
            sum(1 for r in runs if r['lie_war_week'] <= WEEKS and r['lie_strikes_before_war'] > 0), len(warw)))
        continue
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
    tot = Counter(); [tot.update(r['acts']) for r in runs]; n = sum(tot.values())
    print('faction actions (11.3.7 agenda), share of all turns: ' + ', '.join('%s %.1f%%' % (k, 100.0 * tot[k] / n) for k in
          ('goal', 'strike', 'scheme', 'expand', 'recover', 'court', 'move_pc', 'aid_pc', 'lie_low')))
    print('courts won per 2y p10/med/p90', q([r['courts_won'] for r in runs]))
    print('the Wardens-Cult war (relation -3): week the Cult collapsed p10/med/p90 %s (104 = stood); the Wardens %s' % (
          q([r['cult_weeks'] for r in runs]), q([r['wardens_weeks'] for r in runs])))
