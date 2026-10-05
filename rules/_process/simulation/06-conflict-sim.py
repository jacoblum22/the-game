#!/usr/bin/env python3
"""06-conflict-sim.py -- Monte-Carlo of chapter 06's conflict rules on 00's scales.

Models, as written in rules/06-conflict.md:
  * 3 actions per PC turn, 2 per adversary turn, 1 reaction per round (06.1.1-06.1.3)
  * repetition snags 0/-2/-4 on attack-trait beats inside one turn (06.1.6; 01.14.3)
  * weapon weights: one-handed S2 (1 action per Strike), heavy S3 (2 actions per Strike) (T-06-6)
  * degrees: margin >= +10 critical success, >= 0 success, <= -10 critical failure; natural 20 one
    step up, natural 1 one step down (01.8.1)
  * harm: fixed by severity 1/3/5/8/12; a critical success is one severity rung heavier (reach +1);
    an Amplifying lever, the "go big" trade or the Focus push frames reach Great = one rung heavier;
    worn-armor reduction is subtracted on the receiver's side; harm never below 0
  * Fend: the basic defense reaction, a -2 snag on one attack per round (06.6.3)
  * Defend: 1 action, a -2 snag on every attack against the defender until its next turn (06.1.5)
  * tempo: one d20 + Wits + competence by the PC against each foe's tempo DC (06.2.2)
  * the morale clock (06.11): sizes 4/6/8, tick sources as in data/conflict.yaml#morale
  * mobs as one entity (06.10): pooled Vitality, a numbers step by current members
  * heavy blows (base S4+) need a windup action on the turn before (06.9.5)
  * reckless attack = 01.7.3's "go big" trade: reach +1, stakes Risky; a failure costs S2 harm (3), a
    critical failure S3 (5), reduced by armor
Assumed where the owning chapter is not yet written (listed in the chapter's Interface requests):
  * PC Vitality by band 12/14/16/18/20 (02/07); armor reduction light 1 / medium 2 / heavy 3 (07/08)
  * adversary stat lines per band as in T-06-12 (09 owns the final templates)
  * Staggered at Vitality 0; "Dying proxy" = two further harmful hits taken while Staggered (07 owns
    the real ladder)
Seeded: random.Random(606). Usage: python 06-conflict-sim.py [runs]
"""
import random
import statistics
import sys

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
HARM = {0: 0, 1: 1, 2: 3, 3: 5, 4: 8, 5: 12}
REP = [0, -2, -4]


def degree(rng, mod, dc):
    d = rng.randint(1, 20)
    m = d + mod - dc
    deg = 3 if m >= 10 else 2 if m >= 0 else 1 if m > -10 else 0   # 3 CS, 2 S, 1 F, 0 CF
    if d == 20:
        deg = min(3, deg + 1)
    if d == 1:
        deg = max(0, deg - 1)
    return deg


def harm(sev, steps, edge, red):
    s = max(1, min(5, sev + steps))
    return max(0, HARM[s] + edge - red)


# ---------------------------------------------------------------- stat lines (overridable)
PC = {  # band: attack, Guard, Vitality, Focus, tempo modifier, Strike base severity (one-handed, with
        # the mastery rung of 06.4.5 for a narrow martial calling: expert at tier 3, master at tier 5),
        # worn-armor reduction (light 1 / medium 2 / heavy 3)
    1: dict(atk=5, guard=14, vit=12, focus=5, tempo=2, sev=2, armor=1),
    2: dict(atk=7, guard=16, vit=14, focus=6, tempo=3, sev=2, armor=1),
    3: dict(atk=9, guard=18, vit=16, focus=7, tempo=4, sev=3, armor=2),
    4: dict(atk=11, guard=19, vit=18, focus=8, tempo=5, sev=3, armor=2),
    5: dict(atk=12, guard=20, vit=20, focus=9, tempo=6, sev=4, armor=3),
}
FOE = {  # band: attack, Guard, Vitality, base severity, reduction, morale clock, tempo DC, heavy blow
         # (T-06-12 reference lines; inside 00.3.7's envelope; ch.09 owns the final templates)
    1: dict(atk=2, guard=12, vit=5, sev=2, red=0, morale=4, tempo=10, heavy=None),
    2: dict(atk=5, guard=15, vit=12, sev=2, red=0, morale=6, tempo=11, heavy=None),
    3: dict(atk=7, guard=17, vit=18, sev=3, red=1, morale=6, tempo=12, heavy=None),
    4: dict(atk=10, guard=20, vit=26, sev=3, red=2, morale=8, tempo=13, heavy=4),
    5: dict(atk=12, guard=22, vit=40, sev=4, red=2, morale=8, tempo=14, heavy=5),
}


class Foe:
    def __init__(s, band, members=1, leader=False, over=None):
        f = dict(FOE[band])
        if over:
            f.update(over)
        s.band = band
        s.atk = f['atk']
        s.guard = f['guard']
        s.sev = f['sev']
        s.red = f['red']
        s.members = members
        s.per = f['vit']
        s.maxvit = f['vit'] * members
        s.vit = s.maxvit
        s.heavy = f['heavy']
        s.wound_up = False
        s.leader = leader
        s.tempo = f['tempo']
        s.morale = f['morale']
        s.bloodied = False
        s.engaged = False

    @property
    def alive(s):
        return s.vit > 0

    def cur_members(s):
        if s.members == 1:
            return 1 if s.vit > 0 else 0
        return max(0, -(-s.vit // s.per))

    def numbers_step(s):
        if s.members == 1:
            return 0
        m = s.cur_members()
        return 2 if m >= 6 else 1 if m >= 3 else 0


class Morale:
    def __init__(s, size, foes):
        s.size = size
        s.fill = 0
        s.foes = foes
        s.half = s.quarter = False
        s.total = sum(f.maxvit for f in foes)
        s.pc_blood = False

    def tick(s, n):
        s.fill = max(0, s.fill + n)

    def strength(s):
        cur = sum(max(0, f.vit) for f in s.foes)
        if not s.half and cur * 2 <= s.total:
            s.half = True
            s.tick(2)
        if not s.quarter and cur * 4 <= s.total:
            s.quarter = True
            s.tick(2)

    @property
    def broken(s):
        return s.size is not None and s.fill >= s.size


def fight(rng, pband, foes, policy='steady', weapon='one', armor=None, shield=False, use_focus=False,
          fearless=False, pc_over=None, fend=True, called=False, caster=None, foe_fend=False, log=None):
    """caster (revision I-009): None for a weapon fighter, else a dict describing a caster's beats:
         sev    -- base severity of the branch working (05.7.11: rank 1/2/3 = S2/S3/S4); its aimed check
                   uses p['atk'] as casting attribute + competence; it costs 1 action like a Strike (06.1.3)
                   and needs no Move to engage (band.near or band.close)
         elemental -- True when the working's harm is not harm.physical: reduction from armor does not
                   apply (09.3.6; 07.2.2); spell burning (harm.fire) is likewise unreduced
         profane_step -- divine Rebuke: one rung heavier against a profane foe (the foe here is not)
         push_on_crit -- arcane Force Bolt: a critical success pushes the foe one band (it must Move back)
         spell  -- None, or dict(cost, sev, burning): a Focus spell cast as the first beat of a turn while
                   Focus lasts (e.g. Flame Lance rank 2: cost 1, S3, one stack of cond.burning)
         With use_focus and no spell, Focus pushes the first working of each turn (05.6.7).
       foe_fend (ch.09 09_core): adversaries of T3+ Fend the PC's first attack each round (-2).
       log (revision I-004): a list that receives ('beat', modifier, defense, degree, steps) for every PC attack
       and ('defeat', foe band, members fallen) for every foe or mob member defeated, and ('fled', band) for each
       foe still standing when its side's morale breaks -- the raw material of ch.03's evidence events."""
    p = dict(PC[pband])
    if pc_over:
        p.update(pc_over)
    guard = p['guard'] + (1 if shield else 0)
    if armor is None:
        armor = p['armor']
    st = dict(vit=p['vit'], focus=p['focus'] if use_focus else 0, staggered=False, extra=0, lost=0,
              defending=False, fend=True, focus_spent=0)
    if caster is not None:
        weapon = 'one'
        sev_w = caster['sev']
    for f in foes:
        f.burning = 0
        f.fended = False
    sev = p['sev'] + (1 if weapon == 'heavy' else 0)
    mor = Morale(None if fearless else max(f.morale for f in foes), foes)
    t = rng.randint(1, 20) + p['tempo']
    before = [f for f in foes if f.tempo > t]
    after = [f for f in foes if f.tempo <= t]

    def pc_turn():
        st['defending'] = False
        acts = 3
        k = 0
        live = [f for f in foes if f.alive]
        if not live:
            return
        tgt = min(live, key=lambda f: (not f.engaged, f.vit))
        if not tgt.engaged and caster is None:
            tgt.engaged = True
            acts -= 1                                   # Move: close -> engaged
        while acts > 0:
            live = [f for f in foes if f.alive]
            if not live or mor.broken:
                return
            if not tgt.alive:
                eng = [f for f in live if f.engaged]
                if eng:
                    tgt = min(eng, key=lambda f: f.vit)
                elif caster is not None:
                    tgt = min(live, key=lambda f: f.vit)   # a working reaches band.near: no Move
                else:
                    tgt = min(live, key=lambda f: f.vit)
                    tgt.engaged = True
                    acts -= 1
                    continue
            cost = 2 if weapon == 'heavy' else 1
            if policy == 'steady_defend' and acts == 1 and k >= 1:
                st['defending'] = True
                acts -= 1
                continue
            if cost > acts:
                st['defending'] = True                  # spare action: Defend
                acts -= 1
                continue
            steps = 0
            reckless = (policy == 'reckless' and k == 0)
            bsev = sev
            burn = 0
            if caster is not None:
                bsev = sev_w
                spell = caster.get('spell')
                if spell and k == 0 and st['focus'] >= spell['cost']:
                    st['focus'] -= spell['cost']
                    st['focus_spent'] += spell['cost']
                    bsev = spell['sev']
                    burn = spell.get('burning', 0)
                elif not spell and st['focus'] > 0 and k == 0:
                    st['focus'] -= 1
                    st['focus_spent'] += 1
                    steps = 1                           # Focus push on the working
            elif reckless:
                steps = 1
            elif st['focus'] > 0 and k == 0:
                st['focus'] -= 1
                st['focus_spent'] += 1
                steps = 1                               # Focus push: reach +1
            mod = p['atk'] + REP[min(k, 2)]
            if foe_fend and tgt.band >= 3 and not tgt.fended:
                tgt.fended = True
                mod -= 2                                # adversary Fend (06.6.5; 09_core)
            red = tgt.red
            if caster is not None and caster.get('elemental'):
                red = 0
            if called and tgt.red >= 2:
                mod -= 2                                # called shot at a gap: ignore worn armor
                red = 0
            deg = degree(rng, mod, tgt.guard)
            if log is not None:
                log.append(('beat', mod, tgt.guard, deg, steps))
            if deg >= 2:
                h = harm(bsev, steps + (1 if deg == 3 else 0), 0, red)
                if burn:
                    tgt.burning = min(3, tgt.burning + burn)
                if caster is not None and caster.get('push_on_crit') and deg == 3:
                    tgt.engaged = False                 # Force Bolt: pushed one band; it must Move back
                before_m = tgt.cur_members()
                tgt.vit -= h
                if h >= 8:
                    mor.tick(1)
                if tgt.members == 1 and not tgt.bloodied and tgt.vit * 2 <= tgt.maxvit:
                    tgt.bloodied = True
                    mor.tick(1)
                fallen = before_m - tgt.cur_members()
                if log is not None and fallen > 0:
                    log.append(('defeat', tgt.band, fallen))
                if fallen > 0:
                    mor.tick(fallen + (1 if tgt.leader and not tgt.alive else 0))
                mor.strength()
            elif reckless:
                c = max(0, (5 if deg == 0 else 3) - armor)
                st['vit'] -= c
                st['lost'] += c
                if not st['staggered'] and st['vit'] <= 0:
                    st['staggered'] = True
                    mor.tick(-2)
            acts -= cost
            k += 1

    def foe_turn(f):
        if not f.alive or mor.broken:
            return
        f.fended = False
        acts = 2
        k = 0
        if not f.engaged:
            f.engaged = True
            acts -= 1                                   # Move in
        while acts > 0:
            s = f.sev
            if f.heavy and not f.wound_up and k == 0 and acts == 2 and rng.random() < 0.5:
                f.wound_up = True                       # windup, told to the player
                acts -= 1
                continue
            if f.heavy and f.wound_up and k == 0:
                s = f.heavy
                f.wound_up = False
            mod = f.atk + REP[min(k, 2)] - (2 if st['defending'] else 0)
            if fend and st['fend']:
                mod -= 2
                st['fend'] = False                      # Fend on the first attack each round
            deg = degree(rng, mod, guard)
            if deg >= 2:
                h = harm(s, f.numbers_step() + (1 if deg == 3 else 0), 0, armor)
                was = st['vit']
                st['vit'] -= h
                st['lost'] += h
                if st['staggered'] and h > 0:
                    st['extra'] += 1
                if not st['staggered'] and st['vit'] <= 0:
                    st['staggered'] = True
                    mor.tick(-2)
                elif not mor.pc_blood and st['vit'] * 2 <= p['vit'] < was * 2:
                    mor.pc_blood = True
                    mor.tick(-1)
            acts -= 1
            k += 1
        if f.burning and f.alive:                       # cond.burning: S1 per stack at turn end, reduced
            f.vit -= max(0, HARM[1] - (0 if caster is not None and caster.get('elemental') else f.red)) * f.burning
            mor.strength()

    rounds = 0
    while rounds < 30:
        rounds += 1
        st['fend'] = True
        for f in before:
            foe_turn(f)
        if st['extra'] >= 2:
            break
        pc_turn()
        if mor.broken or not any(f.alive for f in foes):
            break
        for f in after:
            foe_turn(f)
        if st['extra'] >= 2:
            break
    over = mor.broken or not any(f.alive for f in foes)
    won = over and st['extra'] < 2
    if log is not None and won and mor.broken:
        for f in foes:
            if f.alive:
                log.append(('fled', f.band, f.cur_members()))
    return dict(won=won, clean=won and not st['staggered'], staggered=st['staggered'],
                dying=st['extra'] >= 2, rounds=rounds, lost=min(st['lost'], p['vit']),
                broke=mor.broken and any(f.alive for f in foes), focus_left=st['focus'],
                focus_spent=st['focus_spent'])


def run(label, pband, mk, **kw):
    rng = random.Random(606)
    res = [fight(rng, pband, mk(), **kw) for _ in range(RUNS)]
    n = len(res)

    def pct(k):
        return 100.0 * sum(1 for r in res if r[k]) / n
    print("| %-58s | %5.1f | %5.1f | %5.1f | %5.1f | %4.1f | %4.1f | %5.1f |" % (
        label, pct('won'), pct('clean'), pct('staggered'), pct('dying'),
        statistics.mean(r['rounds'] for r in res), statistics.mean(r['lost'] for r in res),
        pct('broke')))


HDR = "| %-58s | win%%  | clean | stag%% | dying | rnds | lost | broke |" % "Matchup"
SEP = "|" + "-" * 60 + "|-------|-------|-------|-------|------|------|-------|"


def table(title):
    print("\n### " + title + "\n")
    print(HDR)
    print(SEP)


if __name__ == '__main__':
    print("runs per row:", RUNS)
    BROAD = {3: dict(sev=2, atk=8, guard=17), 4: dict(sev=3, atk=10, guard=18)}
    table("A. Baseline martial PC, band kit, no Focus, three Strikes a turn: one foe")
    for b in (1, 2, 3, 4, 5):
        run("P%d vs 1xT%d (equal band)" % (b, b), b, lambda b=b: [Foe(b)])
    for b in (1, 2, 3, 4):
        run("P%d vs 1xT%d (one band up)" % (b, b + 1), b, lambda b=b: [Foe(b + 1)])
    for b in (1, 2, 3):
        run("P%d vs 1xT%d (two bands up)" % (b, b + 2), b, lambda b=b: [Foe(b + 2)])
    for b in (2, 3, 4, 5):
        run("P%d vs 1xT%d (one band down)" % (b, b - 1), b, lambda b=b: [Foe(b - 1)])
    table("B. Body count: the solo curve (baseline martial PC, no Focus)")
    for b in (1, 2, 3, 4, 5):
        run("P%d vs 2xT%d" % (b, b), b, lambda b=b: [Foe(b), Foe(b)])
        run("P%d vs 3xT%d" % (b, b), b, lambda b=b: [Foe(b), Foe(b), Foe(b)])
    for b in (2, 3, 4, 5):
        run("P%d vs 2xT%d" % (b, b - 1), b, lambda b=b: [Foe(b - 1), Foe(b - 1)])
        run("P%d vs 3xT%d" % (b, b - 1), b, lambda b=b: [Foe(b - 1), Foe(b - 1), Foe(b - 1)])
        run("P%d vs 4xT%d" % (b, b - 1), b, lambda b=b: [Foe(b - 1) for _ in range(4)])
    for b in (3, 4, 5):
        run("P%d vs 4xT%d" % (b, b - 2), b, lambda b=b: [Foe(b - 2) for _ in range(4)])
        run("P%d vs 6xT%d" % (b, b - 2), b, lambda b=b: [Foe(b - 2) for _ in range(6)])
    run("P1 vs 2xT2 (two foes a band up)", 1, lambda: [Foe(2), Foe(2)])
    table("B2. Mobs as single entities, and mixed groups (no Focus)")
    run("P1 vs T1 mob of 4", 1, lambda: [Foe(1, members=4)])
    run("P1 vs T1 mob of 6", 1, lambda: [Foe(1, members=6)])
    run("P2 vs T1 mob of 6", 2, lambda: [Foe(1, members=6)])
    run("P2 vs T1 mob of 8", 2, lambda: [Foe(1, members=8)])
    run("P2 vs T2 mob of 4", 2, lambda: [Foe(2, members=4)])
    run("P3 vs T2 mob of 4", 3, lambda: [Foe(2, members=4)])
    run("P3 vs T2 mob of 6", 3, lambda: [Foe(2, members=6)])
    run("P4 vs T3 mob of 4", 4, lambda: [Foe(3, members=4)])
    run("P4 vs T2 mob of 8", 4, lambda: [Foe(2, members=8)])
    run("P1 vs 1xT2 leader + 2xT1", 1, lambda: [Foe(2, leader=True), Foe(1), Foe(1)])
    run("P2 vs 1xT2 leader + T1 mob of 4", 2, lambda: [Foe(2, leader=True), Foe(1, members=4)])
    run("P2 vs 1xT3 leader + 2xT1", 2, lambda: [Foe(3, leader=True), Foe(1), Foe(1)])
    run("P3 vs 1xT3 leader + 2xT2", 3, lambda: [Foe(3, leader=True), Foe(2), Foe(2)])
    run("P3 vs 1xT4 leader + T2 mob of 4", 3, lambda: [Foe(4, leader=True), Foe(2, members=4)])
    run("P4 vs 1xT4 leader + 2xT3", 4, lambda: [Foe(4, leader=True), Foe(3), Foe(3)])
    table("C. Kit and tactics on the same fights (no Focus)")
    for b, e in ((1, 2), (2, 3), (3, 3), (3, 4), (4, 4), (4, 5)):
        mk = lambda e=e: [Foe(e)]
        run("P%d vs T%d: three Strikes" % (b, e), b, mk)
        run("P%d vs T%d: two Strikes + Defend" % (b, e), b, mk, policy='steady_defend')
        run("P%d vs T%d: shield (+1 Guard), two Strikes + Defend" % (b, e), b, mk, policy='steady_defend', shield=True)
        run("P%d vs T%d: heavy weapon (2-action Strike + Defend)" % (b, e), b, mk, weapon='heavy')
        run("P%d vs T%d: reckless first Strike (go big)" % (b, e), b, mk, policy='reckless')
        run("P%d vs T%d: called shots at gaps (-2, ignore armor)" % (b, e), b, mk, called=True)
        run("P%d vs T%d: no armor" % (b, e), b, mk, armor=0)
        run("P%d vs T%d: no Fend reaction" % (b, e), b, mk, fend=False)
    table("D. Focus (a push on the first Strike each turn while Focus lasts) -- issue I-006")
    for b in (1, 2, 3, 4, 5):
        for e in (b, b + 1):
            if e > 5:
                continue
            mk = lambda e=e: [Foe(e)]
            run("P%d vs T%d: no Focus" % (b, e), b, mk)
            run("P%d vs T%d: Focus push" % (b, e), b, mk, use_focus=True)
            run("P%d vs T%d: heavy weapon, no Focus" % (b, e), b, mk, weapon='heavy')
            run("P%d vs T%d: heavy weapon, Focus push" % (b, e), b, mk, weapon='heavy', use_focus=True)
    for b in (2, 3, 4):
        run("P%d vs 2xT%d: no Focus" % (b, b), b, lambda b=b: [Foe(b), Foe(b)])
        run("P%d vs 2xT%d: Focus push" % (b, b), b, lambda b=b: [Foe(b), Foe(b)], use_focus=True)
    table("E. Who is NOT a specialist: broad martial calling (no mastery rung until tier 4), and I-006's caster")
    for b in (3, 4):
        run("broad P%d vs T%d: no Focus" % (b, b), b, lambda b=b: [Foe(b)], pc_over=BROAD[b])
        run("broad P%d vs T%d: Focus push" % (b, b), b, lambda b=b: [Foe(b)], pc_over=BROAD[b], use_focus=True)
    ash = dict(atk=2, guard=12, vit=12, sev=2, armor=0)
    run("Ash (tier-3 caster, Spent, staff +2 S2): three Strikes", 3, lambda: [Foe(3)], pc_over=ash)
    run("Ash, Spent: two Strikes + Defend", 3, lambda: [Foe(3)], policy='steady_defend', pc_over=ash)
    run("Ash, Spent, vs one T2", 3, lambda: [Foe(2)], pc_over=ash)
    table("F. Sensitivity: PC Vitality flat at 12 in every band (if 02/07 give no growth)")
    for b in (2, 3, 4, 5):
        run("P%d (Vitality 12) vs 1xT%d" % (b, b), b, lambda b=b: [Foe(b)], pc_over=dict(vit=12))
        run("P%d (Vitality 12) vs 2xT%d" % (b, b), b, lambda b=b: [Foe(b), Foe(b)], pc_over=dict(vit=12))
    table("G. Fearless foes (no morale clock): mindless undead, constructs")
    for b in (1, 2, 3, 4):
        run("P%d vs 2xT%d fearless" % (b, b), b, lambda b=b: [Foe(b), Foe(b)], fearless=True)
        run("P%d vs T%d mob of 6 fearless" % (b, max(1, b - 1)), b, lambda b=b: [Foe(max(1, b - 1), members=6)], fearless=True)

    # ---- H. the advisory matrix (T-06-13): classify every encounter shape from the simulated outcome
    def classify(pband, mk, **kw):
        rng = random.Random(606)
        res = [fight(rng, pband, mk(), **kw) for _ in range(RUNS)]
        w = 100.0 * sum(r['won'] for r in res) / len(res)
        st_ = 100.0 * sum(r['staggered'] for r in res) / len(res)
        if w >= 99 and st_ <= 3:
            c = 'trivial'
        elif w >= 95 and st_ <= 15:
            c = 'easy'
        elif w >= 80 and st_ <= 50:
            c = 'fair'
        elif w >= 40:
            c = 'hard'
        else:
            c = 'lethal'
        return "%s %d/%d" % (c, round(w), round(st_))
    print()
    print("### H. Advisory matrix: class win%/Staggered% (baseline martial PC, no Focus)")
    print()
    shapes = [("1 foe", 1, 1), ("2 foes", 2, 1), ("3 foes", 3, 1), ("4 foes", 4, 1), ("6 foes", 6, 1),
              ("mob of 4", 1, 4), ("mob of 6", 1, 6), ("mob of 8", 1, 8)]
    for d in (-2, -1, 0, 1, 2):
        print()
        print("Foe band = PC band %+d" % d)
        print()
        print("| PC band | " + " | ".join(n for n, _, _ in shapes) + " |")
        print("|---|" + "---|" * len(shapes))
        for b in (1, 2, 3, 4, 5):
            e = b + d
            if e < 1 or e > 5:
                continue
            cells = []
            for name, n, m in shapes:
                cells.append(classify(b, lambda e=e, n=n, m=m: [Foe(e, members=m) for _ in range(n)]))
            print("| P%d (foes T%d) | " % (b, e) + " | ".join(cells) + " |")


# ---------------------------------------------------------------- I. chases (06.12): racing clocks
def chase(rng, pc_mod, foe_mod, dc_pool, start_pursuit, lever_every=0, escape_size=6, pursuit_size=8,
          foe_reach=2):
    esc = 0
    pur = start_pursuit
    rnd = 0
    while True:
        rnd += 1
        dc = rng.choice(dc_pool)
        mod = pc_mod + (2 if lever_every and rnd % lever_every == 0 else 0)
        d = rng.randint(1, 20)
        m = d + mod - dc
        deg = 3 if m >= 10 else 2 if m >= 0 else 1 if m > -10 else 0
        if d == 20:
            deg = min(3, deg + 1)
        if d == 1:
            deg = max(0, deg - 1)
        if deg == 3:
            esc += 3
        elif deg == 2:
            esc += 2
        elif deg == 1 and m >= -3:
            esc += 2
            pur += 1            # near miss: success at a cost (cost.time S2 = 1 tick of pursuit)
        elif deg == 1:
            pur += 1            # failure: cost.time S2
        else:
            pur += 2            # critical failure: S3 = 2 ticks
        if esc >= escape_size:
            return True, rnd    # the acting side's delivered reach completes first (00.8.5)
        if pur >= pursuit_size:
            return False, rnd
        fd = degree(rng, foe_mod, dc)
        pur += {3: foe_reach + 1, 2: foe_reach, 1: 0, 0: 0}[fd]
        if pur >= pursuit_size:
            return False, rnd


def chase_row(label, **kw):
    rng = random.Random(606)
    res = [chase(rng, **kw) for _ in range(RUNS)]
    print("| %-64s | %5.1f | %4.1f |" % (label, 100.0 * sum(r[0] for r in res) / len(res),
                                         statistics.mean(r[1] for r in res)))


if __name__ == '__main__':
    print()
    print("### I. Chases: the PC flees (escape clock 6 vs pursuit clock 8; obstacle tiers drawn per round)")
    print()
    print("| %-64s | esc%%  | rnds |" % "Case")
    print("|" + "-" * 66 + "|-------|------|")
    mixed = [10, 15, 15, 15, 20, 10]
    chase_row("P1 (+5) from T2 pursuers (+4), start near (pursuit 1/8)", pc_mod=5, foe_mod=4, dc_pool=mixed, start_pursuit=1)
    chase_row("  the same, start close (pursuit 2/8)", pc_mod=5, foe_mod=4, dc_pool=mixed, start_pursuit=2)
    chase_row("  the same, start far (pursuit 0/8)", pc_mod=5, foe_mod=4, dc_pool=mixed, start_pursuit=0)
    chase_row("  start near, a cited lever every round", pc_mod=5, foe_mod=4, dc_pool=mixed, start_pursuit=1, lever_every=1)
    chase_row("  start near, slower pursuers (reach Limited)", pc_mod=5, foe_mod=4, dc_pool=mixed, start_pursuit=1, foe_reach=1)
    chase_row("  start near, mounted pursuers (reach Great)", pc_mod=5, foe_mod=4, dc_pool=mixed, start_pursuit=1, foe_reach=3)
    chase_row("P1 untrained runner (+2) from T2 (+4), start near", pc_mod=2, foe_mod=4, dc_pool=mixed, start_pursuit=1)
    chase_row("P3 (+9) from T3 pursuers (+7), start near", pc_mod=9, foe_mod=7, dc_pool=mixed, start_pursuit=1)
    chase_row("P3 (+9) from T4 pursuers (+10), start near", pc_mod=9, foe_mod=10, dc_pool=mixed, start_pursuit=1)
    chase_row("P1 (+5) from T1 rabble (+2), start close", pc_mod=5, foe_mod=2, dc_pool=mixed, start_pursuit=2)
    chase_row("Sensitivity: clocks 4 and 4, P1 from T2, start near", pc_mod=5, foe_mod=4, dc_pool=mixed, start_pursuit=1, escape_size=4, pursuit_size=4)
    chase_row("Sensitivity: clocks 6 and 6, P1 from T2, start near", pc_mod=5, foe_mod=4, dc_pool=mixed, start_pursuit=1, escape_size=6, pursuit_size=6)


# ---------------------------------------------------------------- J. casters and the branch working (I-009)
# A caster line by band (05.7.11; revision I-009): casting attribute +3 (+4 from the tier-4 increase) + competence
# (no calling +2 at creation; a calling's +3/+4/+5/+5/+6 at tiers 1-5, 04.5.2); Guard 10 + Agility +1 + floor +1 = 12;
# no armor; Vitality 12 + 2 x (band - 1) (07.1.2); Focus 4 + tier (05.6.1). The working's severity follows the
# caster's grade in the casting school's license (trained S2, expert S3, master S4; narrow callings: expert at
# tier 3, master at tier 5), as a weapon's Strike follows mastery (06.4.5).
CASTER = {
    0: dict(atk=5, guard=12, vit=12, armor=0, tempo=2, focus=4),     # new character, no calling (ch.02)
    1: dict(atk=6, guard=12, vit=12, armor=0, tempo=2, focus=5),
    2: dict(atk=7, guard=12, vit=14, armor=0, tempo=2, focus=6),
    3: dict(atk=8, guard=12, vit=16, armor=0, tempo=3, focus=7),
    4: dict(atk=9, guard=12, vit=18, armor=0, tempo=3, focus=8),
    5: dict(atk=10, guard=12, vit=20, armor=0, tempo=4, focus=9),
}
WORK_SEV = {0: 2, 1: 2, 2: 2, 3: 3, 4: 3, 5: 4}
BRANCH = {   # how each branch working is modelled (05.7.11)
    'arcane Force Bolt': dict(elemental=True, push_on_crit=True),     # harm.arcane.force: armor does not reduce it
    'divine Rebuke': dict(elemental=True),                            # radiant/necrotic; the opposed-nature rung is not modelled
    'primal Wild Lash': dict(elemental=False),                        # thorn, stone, water, wind: physical; reduction applies
}

if __name__ == '__main__':
    table("J1. New casters (ch.02, no calling) using only their branch working (S2, no Focus) -- I-009 acceptance >= 75% vs one T2")
    for name, bw in BRANCH.items():
        for lab, mk in (("1xT1", lambda: [Foe(1)]), ("2xT1", lambda: [Foe(1), Foe(1)]), ("1xT2", lambda: [Foe(2)])):
            run("new caster +5 G12 V12, %s vs %s" % (name, lab), 1, mk, pc_over=CASTER[0], caster=dict(sev=2, **bw))
    for name, bw in BRANCH.items():
        run("weakest legal caster (+1, G10, V11), %s vs 1xT2" % name, 1, lambda: [Foe(2)],
            pc_over=dict(atk=1, guard=10, vit=11, armor=0, tempo=0), caster=dict(sev=2, **bw))
        run("weakest legal caster (+1, G10, V11), %s vs 1xT1" % name, 1, lambda: [Foe(1)],
            pc_over=dict(atk=1, guard=10, vit=11, armor=0, tempo=0), caster=dict(sev=2, **bw))
    run("reference: the same new caster with a staff, no working (+1 S2)", 1, lambda: [Foe(2)], pc_over=dict(CASTER[0], atk=1))
    run("reference: martial P1 line, no Focus", 1, lambda: [Foe(2)])

    table("J2. A Spent tier-3 caster (rank 2, S3) -- I-009 acceptance >= 40% vs one T3; martial baseline beside it")
    for name, bw in BRANCH.items():
        run("Spent P3 caster, %s vs 1xT3" % name, 3, lambda: [Foe(3)], pc_over=CASTER[3], caster=dict(sev=3, **bw))
        run("  the same, T3 Fends (09's final rule)" , 3, lambda: [Foe(3)], pc_over=CASTER[3], caster=dict(sev=3, **bw), foe_fend=True)
        run("  the same, Vitality 12 (WE-05 Ash's sheet)", 3, lambda: [Foe(3)], pc_over=dict(CASTER[3], vit=12), caster=dict(sev=3, **bw))
    run("Ash before I-009: Spent, staff +2 S2 (section E)", 3, lambda: [Foe(3)], pc_over=dict(atk=2, guard=12, vit=12, sev=2, armor=0))
    run("martial specialist P3, no Focus (I-006 baseline)", 3, lambda: [Foe(3)])
    run("martial specialist P3, no Focus, T3 Fends", 3, lambda: [Foe(3)], foe_fend=True)
    run("broad martial P3, no Focus", 3, lambda: [Foe(3)], pc_over=dict(sev=2, atk=8, guard=17))

    table("J3. The branch working at every band, Spent, against one foe of the caster's band; martial no-Focus baseline beside it")
    for b in (1, 2, 3, 4, 5):
        for name, bw in BRANCH.items():
            run("Spent P%d caster (S%d), %s vs 1xT%d" % (b, WORK_SEV[b], name, b), b, lambda b=b: [Foe(b)],
                pc_over=CASTER[b], caster=dict(sev=WORK_SEV[b], **bw))
        run("martial specialist P%d, no Focus" % b, b, lambda b=b: [Foe(b)])

    table("J4. Focus still pays: the same P3 caster Spent, pushing the working, or casting a 1-Focus spell first each turn")
    lance = dict(cost=1, sev=3, burning=1)        # ab.flame_lance rank 2: S3 fire and one stack of cond.burning
    for lab, mk in (("1xT3", lambda: [Foe(3)]), ("1xT4", lambda: [Foe(4)]), ("2xT3", lambda: [Foe(3), Foe(3)]),
                    ("2xT2", lambda: [Foe(2), Foe(2)])):
        bw = BRANCH['arcane Force Bolt']
        run("P3 caster vs %s: Spent (Force Bolt only)" % lab, 3, mk, pc_over=CASTER[3], caster=dict(sev=3, **bw))
        run("P3 caster vs %s: Focus 7, push the first bolt each turn" % lab, 3, mk, pc_over=CASTER[3], caster=dict(sev=3, **bw), use_focus=True)
        run("P3 caster vs %s: Focus 7, Flame Lance first each turn" % lab, 3, mk, pc_over=CASTER[3], caster=dict(sev=3, spell=lance, **bw), use_focus=True)
        run("martial specialist P3 vs %s: no Focus" % lab, 3, mk)
        run("martial specialist P3 vs %s: Focus push" % lab, 3, mk, use_focus=True)
    table("J5. Sensitivity: the working one rung lighter at tier 3 (S2), the alternative DL-05-31 rejected")
    for name, bw in BRANCH.items():
        run("Spent P3 caster, %s at S2 vs 1xT3" % name, 3, lambda: [Foe(3)], pc_over=CASTER[3], caster=dict(sev=2, **bw))
