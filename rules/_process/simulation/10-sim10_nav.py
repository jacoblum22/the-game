# ch.10 navigation & forage odds by exhaustive d20 enumeration (00.3.10 degree rule, near miss margin -1..-3)
def dist(mod, dc):
    out = {'cs':0,'s':0,'nm':0,'f':0,'cf':0}
    for d in range(1,21):
        m = d+mod-dc
        g = 3 if m>=10 else 2 if m>=0 else 0 if m<=-10 else 1
        if d==20: g=min(3,g+1)
        if d==1: g=max(0,g-1)
        if g==3: out['cs']+=5
        elif g==2: out['s']+=5
        elif g==1:
            out['nm' if m>=-3 else 'f']+=5
        else: out['cf']+=5
    return out
TIERS={'easy':10,'moderate':15,'hard':20,'very_hard':25}
print('NAVIGATION: P(lost) = failure (not near miss) + crit fail; near miss assumed success-at-cost')
for label,mod,shift in [('unlicensed fallback Wits+2 floor+1',3,5),('trained navigator Wits+2 comp+2',4,0),('navigator + map lever',6,0),('navigator + map + slow',8,0),('expert P2 +7',7,0),('unlicensed + map',5,5)]:
    row=[]
    for t,dc in TIERS.items():
        o=dist(mod,dc+shift); lost=o['f']+o['cf']; reach3=o['cs']
        row.append(f"{t}: lost {lost}% / great+ {reach3}%")
    print(label, '|', ' ; '.join(row))
print()
print('FORAGE: expected supply per watch = E[delivered reach] (Standard framed reach 2; licensed) / fallback Limited 1')
for label,mod,shift,reach in [('licensed forager Wits+2 comp+2',4,0,2),('unlicensed fallback',3,5,1),('licensed + slow-pace role snag -2',2,0,2)]:
    row=[]
    for t,dc in TIERS.items():
        o=dist(mod,dc+shift)
        ev=(o['cs']*(reach+1)+(o['s']+o['nm'])*reach)/100
        row.append(f"{t}: {ev:.2f}")
    print(label,'|',' ; '.join(row))
print()
print('HUNT: yield 2 x delivered reach; licensed tracker Wits+2 comp+2 (Wren)')
for t,dc in TIERS.items():
    o=dist(4,dc); ev=2*(o['cs']*3+(o['s']+o['nm'])*2)/100
    print(t, f"{ev:.2f} supply; fail {o['f']+o['cf']}%")
