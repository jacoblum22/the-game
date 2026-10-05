# ch.10 travel time-tick check simulation: rates per day by danger rating.
import random
R = random.Random(10)
# faces on d12: counts of E (encounter) and O (omen); then V,D,W,F,P one each; rest L
RATINGS = {'settled':(1,1),'wild':(1,2),'perilous':(2,2),'deadly':(3,2)}
ORDER = ['settled','wild','perilous','deadly']
THREAT_SHARE = {'settled':0.25,'wild':0.60,'perilous':0.75,'deadly':0.85}
def faces(r):
    e,o = RATINGS[r]
    f = ['E']*e+['O']*o+['V','D','W','F','P']
    f += ['L']*(12-len(f))
    return f
def step(r,k):  # rating one rung higher (night)
    i = min(3, ORDER.index(r)+k); return ORDER[i]
def run(r, days=20000, night_up=True, avoid=0.0, auto_after=4):
    stats = dict(enc_nonthreat=0, threats=0, omens=0, events=0, disc=0, opp=0, depl=0, weather=0, lull=0, avoided=0)
    pending = None  # checks since omen
    for d in range(days):
        for w in range(4):
            rr = step(r,1) if (night_up and w==3) else r
            # threat share uses the region's base table
            face = R.choice(faces(rr))
            if pending is not None:
                pending += 1
            if face == 'E':
                if pending is not None:
                    stats['threats'] += 1; pending=None
                else:
                    if R.random() < THREAT_SHARE[r]:
                        stats['omens'] += 1  # converted to omen (omen-first)
                        if R.random() < avoid: stats['avoided']+=1
                        else: pending = 0
                    else:
                        stats['enc_nonthreat'] += 1
            elif face == 'O':
                if pending is not None:
                    stats['threats'] += 1; pending=None   # second sign: it arrives
                else:
                    stats['omens'] += 1
                    # omen pre-rolls next encounter: threat or not
                    if R.random() < THREAT_SHARE[r]:
                        if R.random() < avoid: stats['avoided']+=1
                        else: pending = 0
                    else:
                        pass  # non-threat omen: sign of travelers etc; arrives next E as nonthreat (counted there)
            else:
                stats[{'V':'events','D':'depl','W':'weather','F':'disc','P':'opp','L':'lull'}[face]] += 1
            if pending is not None and pending >= auto_after:
                stats['threats'] += 1; pending=None
    return {k: round(v/days,3) for k,v in stats.items()}
for r in ORDER:
    print(r, run(r))
print('--- with 50% avoidance of omened threats')
for r in ORDER:
    print(r, run(r, avoid=0.5))
