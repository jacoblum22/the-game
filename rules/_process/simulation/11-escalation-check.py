"""11-escalation-check.py -- [revision: I-084] how long an outgrown faction's 'win a power' goal takes (11.3.3).

An outgrown faction (its champion band below the PC's power_band while it is set against the PC) takes, as its next
goal, `change`, scope regional, rating its highest: win the band-5 power of the far rings to its cause. This script
measures the weeks that goal clock needs, using 11-world-sim.py's own check() and choose_action() (11.3.5-11.3.7,
loaded by path, nothing re-implemented): a tier-3 aggressive faction (the seed's usual threat, 12.16.10) with two
rivals at -2 (the rulers and the faith), one World Turn a week, slips -> recover, strikes resolved against tier-2
rivals (hold losses are counted, not applied, so the clock is measured at tier 3). Regional clock: 12 segments.
Usage: python 11-escalation-check.py [seeds]   (default 2000; seeded, deterministic)
"""
import importlib.util, os, random, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ws11", os.path.join(HERE, "11-world-sim.py"))
ws = importlib.util.module_from_spec(spec)
sys.argv, _argv = [sys.argv[0]], sys.argv          # 11-world-sim reads argv[1] as its seed count at import
spec.loader.exec_module(ws)
sys.argv = _argv
SEEDS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000

def q(xs):
    xs = sorted(xs)
    return xs[len(xs) // 10], statistics.median(xs), xs[(len(xs) * 9) // 10]

def run(seed, ratings, stage):
    rng = random.Random(seed)
    random.seed(seed)
    f = ws.Faction('threat', 3, ratings, 'aggressive', stage)
    rul = ws.Faction('rulers', 2, {'force': 2, 'cunning': 2, 'wealth': 2, 'sway': 2}, 'cautious')
    fai = ws.Faction('faith', 2, {'force': 1, 'cunning': 2, 'wealth': 2, 'sway': 3}, 'steadfast')
    for g in (rul, fai):
        f.rel[g.id] = -2; g.rel[f.id] = -2
    filled, week, losses = 0, 0, 0
    while filled < 12 and week < 520:
        week += 1
        act, tgt = ws.choose_action(rng, f, [f, rul, fai])
        if act == 'goal':
            dg, _ = ws.check(rng, f, max(f.r.values()), 10 + 2 * f.tier + ws.GOAL_SCOPE['regional'], 'goal')
            filled += {3: 2, 2: 1, 1: 0, 0: 0}[dg]
            if dg == 0: f.slip = True
        elif act == 'recover':
            dg, _ = ws.check(rng, f, max(f.r['wealth'], f.r['sway']), 13 + 2 * f.tier)
            if dg >= 2: f.slip = False
            if dg == 3: filled += 1
        elif act == 'strike':
            dc = 10 + max(tgt.r['force'], tgt.r['cunning']) + 2 * tgt.tier
            dg, _ = ws.check(rng, f, f.r['force'], dc)
            if dg == 0: losses += 1
        elif act == 'expand':
            ws.check(rng, f, f.r['wealth'], 15 + 2 * f.tier, 'expand')
    return week, losses

print("11-escalation-check.py: weeks for an outgrown tier-3 faction's regional 'win a power' clock (12 segments)")
for label, ratings, stage in [
        ("highest rating 5 (force 5, cunning 2, wealth 1, sway 2), rising", {'force': 5, 'cunning': 2, 'wealth': 1, 'sway': 2}, 'rising'),
        ("highest rating 4 (force 4, cunning 3, wealth 1, sway 2), flourishing", {'force': 4, 'cunning': 3, 'wealth': 1, 'sway': 2}, 'flourishing'),
        ("highest rating 4, entrenched (-1 on goal)", {'force': 4, 'cunning': 3, 'wealth': 1, 'sway': 2}, 'entrenched')]:
    res = [run(s, ratings, stage) for s in range(1, SEEDS + 1)]
    w = [r[0] for r in res]
    print("  %-70s weeks p10/median/p90 %s; seasons (13 weeks) at the median %.1f" % (label, q(w), statistics.median(w) / 13))
