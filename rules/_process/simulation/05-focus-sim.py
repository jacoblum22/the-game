# focus_sim05.py -- Focus economy across a fight, a rest and an adventuring day (rule 05.6; WE-05-5).
# Assumptions (stated in the chapter): ch.06 and ch.07 are unwritten, so the fight model is 00.3.7's coherence
# model: one PC beat per round, one foe attack per round, fixed harm by severity (1/3/5/8/12), degrees by 00.3.10
# (critical at margin >= 10; natural 20 steps up, natural 1 steps down), a critical success = +1 severity rung.
# The PC is Staggered at Vitality 0 (the fight is then counted as lost for this measure).
import random, statistics, math
HARM = {0: 0, 1: 1, 2: 3, 3: 5, 4: 8, 5: 12}
R = random.Random(505)

def degree(mod, dc):
    d = R.randint(1, 20); tot = d + mod; m = tot - dc
    deg = 3 if m >= 10 else 2 if m >= 0 else 1 if m > -10 else 0   # 3 crit success, 2 success, 1 failure, 0 crit failure
    if d == 20: deg = min(3, deg + 1)
    if d == 1: deg = max(0, deg - 1)
    return deg

def fight_wren(use_focus, focus, fmax=5, foe=dict(vit=10, atk=4, guard=13, sev=2), log=None):
    """Wren, tier-1 Archer: attack +6 (Agility 3 + competence 3), Guard 14, Vitality 12.
    Aimed Shot (rider, 1 Focus): Precision lever (+2) and +1 severity rung. Quarry's Mark (trigger, 1 Focus, once per
    scene): target exposed -> a second Precision lever (+2) on her later attacks (ch.06 owns the condition)."""
    vit, fvit, rounds, spent, marked, mark_used = 12, foe['vit'], 0, 0, False, False
    f0 = focus
    while vit > 0 and fvit > 0:
        rounds += 1
        mod, sev = 6, 2
        if marked: mod += 2
        if use_focus and focus >= 1:
            focus -= 1; spent += 1; mod += 2; sev += 1
        deg = degree(mod, foe['guard'])
        if deg >= 2:
            fvit -= HARM[min(5, sev + (1 if deg == 3 else 0))]
            if use_focus and not mark_used and focus >= 1 and fvit > 0:
                focus -= 1; spent += 1; marked = True; mark_used = True
        if fvit <= 0: break
        d2 = degree(foe['atk'], 14)
        if d2 >= 2: vit -= HARM[min(5, foe['sev'] + (1 if d2 == 3 else 0))]
    return dict(win=fvit <= 0 and vit > 0, rounds=rounds, spent=spent, focus=focus, vit=max(vit, 0), spent_state=(focus == 0 and f0 > 0))

def fight_ash(use_focus, focus, fmax=7, foe=dict(vit=16, atk=7, guard=16, sev=3)):
    """Ash, tier-3 Pyromancer: casting +8 (Intellect 3 + competence 5), Guard 12, Vitality 12.
    Flame Lance rank 2 (1 Focus): S3 fire and burning (1 harm at each of the foe's turn ends, per stack, max 3).
    Spell Ward rank 2 (reaction, 1 Focus): a hit is two severity rungs lighter. Arcane family trigger: a critical
    success restores 1 Focus, once per scene. Without Focus: a staff Strike at +2, S2."""
    vit, fvit, rounds, spent, burn, trig, gen = 12, foe['vit'], 0, 0, 0, False, 0
    while vit > 0 and fvit > 0:
        rounds += 1
        if use_focus and focus >= 1:
            focus -= 1; spent += 1
            deg = degree(8, foe['guard'])
            if deg >= 2:
                fvit -= HARM[3 + (1 if deg == 3 else 0)]; burn = min(3, burn + 1)
                if deg == 3 and not trig:
                    trig = True; focus = min(fmax, focus + 1); gen += 1
        else:
            deg = degree(2, foe['guard'])
            if deg >= 2: fvit -= HARM[2 + (1 if deg == 3 else 0)]
        if fvit <= 0: break
        d2 = degree(foe['atk'], 12)
        if d2 >= 2:
            sev = foe['sev'] + (1 if d2 == 3 else 0)
            if use_focus and focus >= 2:          # keep 1 Focus for the next lance
                focus -= 1; spent += 1; sev = max(0, sev - 2)
            vit -= HARM[sev]
        fvit -= burn
    return dict(win=fvit <= 0 and vit > 0, rounds=rounds, spent=spent, focus=focus, vit=max(vit, 0), gen=gen)

def summarize(name, runs):
    n = len(runs)
    w = sum(r['win'] for r in runs)
    print("%-44s win %5.1f%%  rounds %.2f  Focus spent %.2f  Focus left %.2f  ends Spent %5.1f%%  Vitality left (wins) %.1f" % (
        name, 100 * w / n, statistics.mean(r['rounds'] for r in runs), statistics.mean(r['spent'] for r in runs),
        statistics.mean(r['focus'] for r in runs), 100 * sum(r['focus'] == 0 for r in runs) / n,
        statistics.mean([r['vit'] for r in runs if r['win']] or [0])))

N = 20000
print("== One fight ==")
summarize("Wren (tier 1, Focus 5) vs T2, no Focus", [fight_wren(False, 5) for _ in range(N)])
summarize("Wren (tier 1, Focus 5) vs T2, spending", [fight_wren(True, 5) for _ in range(N)])
summarize("Wren (tier 1, Focus 2 at start) vs T2", [fight_wren(True, 2) for _ in range(N)])
summarize("Ash (tier 3, Focus 7) vs T3, no Focus", [fight_ash(False, 7) for _ in range(N)])
summarize("Ash (tier 3, Focus 7) vs T3, spending", [fight_ash(True, 7) for _ in range(N)])
summarize("Ash (tier 3, Focus 3 at start) vs T3", [fight_ash(True, 3) for _ in range(N)])

print("== Rests (05.6.9) ==")
for fmax in (4, 5, 7, 9, 12):
    print("max %2d: breather +1 | short rest +%d (partial +%d) | long rest to %d (partial to %d)" % (fmax, math.ceil(fmax / 2), math.ceil(fmax / 4), fmax, math.ceil(3 * fmax / 4)))

def day_wren(fights=5, short_after=(2, 4)):
    """A venture day: fights against T2 foes; a breather after every fight (only 2 restore Focus between short rests);
    a short rest after the fights listed. Vitality is restored between fights (ch.07 owns it) so that the measure
    isolates Focus. Returns the Focus at the start of each fight and the Focus spent in each."""
    fmax, focus, breathers, shorts = 5, 5, 0, 0
    starts, spends = [], []
    for i in range(1, fights + 1):
        starts.append(focus)
        r = fight_wren(True, focus)
        spends.append(r['spent']); focus = r['focus']
        if i in short_after and shorts < 2:
            focus = min(fmax, focus + math.ceil(fmax / 2)); shorts += 1; breathers = 0
        elif breathers < 2:
            focus = min(fmax, focus + 1); breathers += 1
    return starts, spends

runs = [day_wren() for _ in range(N)]
print("== A venture day, Wren, 5 fights vs T2: breather after each fight, short rest after fights 2 and 4 ==")
for i in range(5):
    st = [r[0][i] for r in runs]; sp = [r[1][i] for r in runs]
    print("fight %d: Focus at start mean %.2f (starts at 0: %4.1f%%, at 1: %4.1f%%)  spent mean %.2f" % (i + 1, statistics.mean(st), 100 * sum(x == 0 for x in st) / N, 100 * sum(x == 1 for x in st) / N, statistics.mean(sp)))
print("mean Focus spent over the day: %.2f; restored by rests: breathers <= 3, short rests <= 6" % statistics.mean(sum(r[1]) for r in runs))
runs = [day_wren(short_after=()) for _ in range(N)]
print("== The same day with breathers only (no short rest) ==")
for i in range(5):
    st = [r[0][i] for r in runs]
    print("fight %d: Focus at start mean %.2f (starts at 0: %4.1f%%)" % (i + 1, statistics.mean(st), 100 * sum(x == 0 for x in st) / N))
