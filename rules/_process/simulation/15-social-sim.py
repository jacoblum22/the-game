import random, itertools
def degree(mod, dc, d):
    tot=d+mod; m=tot-dc
    if m>=10: g=3
    elif m>=0: g=2
    elif m<=-10: g=0
    else: g=1
    if d==20: g=min(3,g+1)
    if d==1: g=max(0,g-1)
    nm = (g==1 and m>=-3)
    return g, nm
def odds(mod,dc):
    c={0:0,1:0,2:0,3:0}; nm=0
    for d in range(1,21):
        g,n=degree(mod,dc,d); c[g]+=1; nm+=n
    return {k:v*5 for k,v in c.items()}, nm*5
STAND={-3:5,-2:3,-1:1,0:0,1:-1,2:-3,3:-5}
CEIL={-3:0,-2:1,-1:1,0:2,1:3,2:4,3:5}
REQ={1:0,2:2,3:5,4:8,5:10}
names={-3:'Hostile',-2:'Unfriendly',-1:'Wary',0:'Neutral',1:'Warm',2:'Friendly',3:'Devoted'}
print("T-15 grid: DC for defense 10 (commoner) at each standing x request (ceiling marked), success-or-better % at +1/+5/+9")
for s in range(-3,4):
    row=[]
    for r in range(1,6):
        dc=10+STAND[s]+REQ[r]
        tag='' if r<=CEIL[s] else '*'
        o=[sum(v for k,v in odds(m,dc)[0].items() if k>=2) for m in (1,5,9)]
        row.append(f"R{r}{tag}:{dc}({o[0]}/{o[1]}/{o[2]})")
    print(f"{names[s]:10s}", "  ".join(row))
# effective request after terms; ceiling at Neutral R2: R4 with 2 terms -> R2
# persuasion campaign: clock size by effective rung R3:4,R4:6,R5:8 ; each beat DC = def+stand+REQ[2]; ticks=delivered reach (Standard=2, crit 3, success-at-cost 2 w/ cost)
# patience clock size by standing: Wary4 Neutral6 Warm6 Friendly8 Devoted8 ; failures tick U(S2)=1 (risky) ; crit fail 2 ; each beat also +0
def campaign(mod, defense, s, size, patience, trials=200000, reach=2):
    rnd=random.Random(7); win=0; comp=0; beats=0
    for _ in range(trials):
        p=0;c=0;n=0
        while True:
            n+=1
            d=rnd.randint(1,20)
            dc=defense+STAND[s]+REQ[2]
            g,nm=degree(mod,dc,d)
            if g==3: c+=reach+1
            elif g==2: c+=reach
            elif nm: c+=reach; p+=1   # take success at cost: cost lands on patience (closed_door S2 -> 1)
            elif g==1: p+=1
            else: p+=2
            if c>=size: win+=1; comp+= (p>=patience/2); beats+=n; break
            if p>=patience: beats+=n; break
    return win/trials, comp/max(1,win), beats/trials
print()
print("Persuasion campaign (defense 10/13/16), win% / compromise share / mean beats")
for s,pat in ((-1,4),(0,6),(1,6),(2,8)):
  for size in (4,6,8):
    out=[]
    for de in (10,13,16):
      for m in (1,5,9):
        w,cpt,b=campaign(m,de,s,size,pat,40000)
        out.append(f"d{de}+{m}:{w*100:.0f}/{cpt*100:.0f}/{b:.1f}")
    print(names[s],pat,"clk",size," ".join(out))
print()
print("Campaign v2: beat DC = defense + standing + REQ[ceiling]; clock by target rung (R2 4, R3 4, R4 6, R5 8); patience Wary4 Neutral6 Warm6 Friendly8")
def campaign2(mod, defense, s, size, patience, trials=40000, reach=2):
    rnd=random.Random(11); win=0; comp=0; beats=0
    dc=defense+STAND[s]+REQ[CEIL[s]]
    for _ in range(trials):
        p=0;c=0;n=0
        while True:
            n+=1; d=rnd.randint(1,20); g,nm=degree(mod,dc,d)
            if g==3: c+=reach+1
            elif g==2: c+=reach
            elif nm: c+=reach; p+=1
            elif g==1: p+=1
            else: p+=2
            if c>=size: win+=1; comp+=(p>=patience/2); beats+=n; break
            if p>=patience: beats+=n; break
    return win/trials, comp/max(1,win), beats/trials, dc
for s,pat,size in ((-1,4,4),(0,6,4),(1,6,6),(2,8,8)):
    out=[]
    for de in (10,13,16):
      for m in (1,5,9):
        w,cpt,b,dc=campaign2(m,de,s,size,pat)
        out.append(f"d{de}(DC{dc})+{m}:{w*100:.0f}/{cpt*100:.0f}/{b:.1f}")
    print(names[s],"->R%d"%(CEIL[s]+1)," ".join(out))
