# ch.10 site delve v2: explore beat + one other significant beat per area; listening danger clock.
import random, sys
R = random.Random(2020)
def degree(mod, dc):
    d = R.randint(1,20); t = d+mod; m = t-dc
    g = 3 if m>=10 else 2 if m>=0 else 0 if m<=-10 else 1
    if d==20: g=min(3,g+1)
    if d==1: g=max(0,g-1)
    return g, (g==1 and m>=-3)
SF = {'settled':dict(E=1,O=1,S=1), 'wild':dict(E=1,O=2,S=1), 'perilous':dict(E=2,O=2,S=2), 'deadly':dict(E=2,O=3,S=2)}
CAD = {'settled':3,'wild':2,'perilous':2,'deadly':1}
def delve(mod=5, dc=15, prog=8, danger=8, rating='wild', approach='care', other=1, other_succ=0.6, threat_share=0.6):
    p=d=0; since=0; pend=None; fights=0; beats=0; ints=0
    f=SF[rating]; faces=['E']*f['E']+['O']*f['O']+['S']*f['S']+['D','H','F','P']; faces+=['L']*(12-len(faces))
    def tick_time(n):
        nonlocal since, pend, d, fights, ints
        for _ in range(n):
            ints+=1; since+=1
            if since>=CAD[rating]:
                since=0; fc=R.choice(faces)
                if pend is not None: pend+=1
                if fc=='S': d+=1
                elif fc in 'EO':
                    if pend is not None: fights+=1; pend=None; d+=1
                    elif fc=='E' and R.random()>threat_share: pass  # non-threat meeting
                    else: pend=0
                if pend is not None and pend>=4: fights+=1; pend=None; d+=1
    while p<prog and d<danger and beats<300:
        beats+=1
        r = 2 + (1 if approach=='haste' else 0)
        g,near = degree(mod, dc)
        if g==3: p+=r+1
        elif g==2: p+=r
        elif g==1:
            if near: p+=r; d+=1
            else: d+=1
        else: d+=2
        if approach=='haste': d+=1
        if p>=prog: break
        tick_time(2 if approach=='care' else 1)
        if approach=='stealth' and g<=1 and not near: pass
        for _ in range(other):
            beats+=1
            if R.random()>other_succ: d+=1
            tick_time(1)
    return p>=prog, beats, ints, fights
def stats(n=20000, **kw):
    w=b=i=fg=0
    for _ in range(n):
        ok,bb,ii,ff=delve(**kw); w+=ok; b+=bb; i+=ii; fg+=ff
    return dict(objective=round(w/n,3), roused=round(1-w/n,3), beats=round(b/n,1), intervals=round(i/n,1), fights=round(fg/n,2))
print('medium prog8 vs danger sizes, care, wild, mod5')
for dz in [6,8,10,12]: print(dz, stats(danger=dz))
print('approach x mod, prog8 danger8? and 10')
for dz in [8,10]:
  for ap in ['care','stealth','haste']:
    for mod in [3,5,7,9]:
      print(dz, ap, mod, stats(danger=dz, approach=ap, mod=mod))
print('sizes small6/8, medium8/10, large12/12, vast12/12 at mod5 care wild')
for pz,dz in [(6,8),(8,10),(12,12),(12,10)]: print(pz,dz, stats(prog=pz,danger=dz))
print('ratings at 8/10')
for r in SF: print(r, stats(rating=r, danger=10))
