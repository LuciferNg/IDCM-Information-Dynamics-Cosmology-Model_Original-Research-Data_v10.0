#!/usr/bin/env python3
"""O222 R27/A -- RT3 minimality by DELETION (exact, zero parameters, pre-registered).

Frozen judgement set, calibrated on the record BEFORE any deletion:
  J1 rank_Q(K)                     = 6          (docs/19 C5)
  J2 fraction of balanced columns  = 1 (62/62)  (docs/19 C2)
  J3 hits/(2*#cols)                = 1          (R24: hits = 2N; normalised so it is not a tautology in size)
  J4 pair-structure count          = 6000/7140  (docs/19 C5)
  J5 DISTINGUISHING POWER          = #distinct row types separated by the remaining columns (base: 12/12)

PRE-REGISTERED PREDICTIONS (written before running):
  Pr-1 each family deletion (V/F/E) breaks J5 or J4 -> minimality holds at family level.
  Pr-2 the single-axis deletions (62) break J5 only for axes that are the unique separator of some row pair;
       hence there is a minimal separating subfamily strictly smaller than 62 -> the generator is NOT minimal
       as set (RT3 in the strong sense: FALSE), unless J5 stays 12/12 for all 62 deletions.
Usage: /usr/bin/python3 -u scripts/67_r27a_rt3_deletion.py"""
import importlib.util, io, json, os, collections
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("m12c",os.path.join(HERE,"12_b5_budget.py")); m12=importlib.util.module_from_spec(sp); sp.loader.exec_module(m12)
_mm,K,MUL,hx,idx,_t=m12.load_machine()
NR=len(K); NC=len(K[0]); COST=F(123,88); EMIN=F(123,176)
lab=[str(x) for x in (idx if isinstance(idx,list) else range(NC))]
fams=collections.defaultdict(list)
for j,l in enumerate(lab): fams[l[0] if l and l[0] in 'VFE' else '?'].append(j)
print("families:",{k:len(v) for k,v in sorted(fams.items())},"rows",NR,"cols",NC)
def rank_bar(A):
    A=[[int(x) for x in r] for r in A]; m=len(A); n=len(A[0]) if m else 0; r=0; prev=1
    for c in range(n):
        p=None
        for i in range(r,m):
            if A[i][c]: p=i; break
        if p is None: continue
        A[r],A[p]=A[p],A[r]
        for i in range(r+1,m):
            if A[i][c]:
                f=A[i][c]
                for k in range(c,n): A[i][k]=(A[i][k]*A[r][c]-f*A[r][k])//prev
        prev=A[r][c]; r+=1
        if r==m: break
    return r
def bal_frac(cols):
    b=sum(1 for a in cols if sum(K[i][a] for i in range(NR))==0); return F(b,len(cols)),b
def hits_frac(cols):
    order=[(a,b) for a in cols for b in cols]; L=[]; s=0; h=0
    for (a,b) in order:
        for ctx in (a,b):
            if L and L[-1][0]==ctx: h+=1; continue
            L.append((ctx,K[s][ctx],s)); s=MUL[s][hx[ctx]]
        _c,_v,s_at=L.pop(); s=s_at
        if L and L[-1][0]==b: h+=1
        else: L.append((b,K[s][b],s)); s=MUL[s][hx[b]]
    return F(h,2*len(cols)),h
def pairstruct(cols):
    rows=[tuple(K[i][a] for a in cols) for i in range(NR)]; c=0; t=0
    for i in range(NR):
        for j in range(i+1,NR):
            t+=1
            if rows[i]!=rows[j] and tuple(-x for x in rows[i])!=rows[j]: c+=1
    return c,t
def sep_count(cols):
    rows=[tuple(K[i][a] for a in cols) for i in range(NR)]
    types=sorted(set(rows)); return len(types),len(cols)
allc=list(range(NC))
J1=rank_bar(K); J2f,J2=bal_frac(allc); J3f,J3=hits_frac(allc); J4,t4=pairstruct(allc); J5,nt=sep_count(allc)
print("CAL J1 rank=%d (6) %s"%(J1,"OK" if J1==6 else "MISMATCH"))
print("CAL J2 frac=%s (%d/%d) (1, 62/62) %s"%(J2f,J2,NC,"OK" if J2f==1 else "MISMATCH"))
print("CAL J3 frac=%s hits=%d (1, 124) %s"%(J3f,J3,"OK" if (J3f==1 and J3==124) else "MISMATCH"))
print("CAL J4 %d/%d (6000/7140) %s"%(J4,t4,"OK" if (J4,t4)==(6000,7140) else "MISMATCH"))
print("CAL J5 distinct row types=%d/%d (record: 12 distinct rows)"%(J5,nt))
def judge(cols):
    return dict(rank=rank_bar([[K[i][c] for c in cols] for i in range(NR)]), balf=str(bal_frac(cols)[0]),
                hitsf=str(hits_frac(cols)[0]), ps=pairstruct(cols), sep=sep_count(cols))
base=judge(allc)
print("BASE full judge:",{k:(v if not isinstance(v,tuple) else list(v)) for k,v in base.items()})
famres={}
for nm in ('V','F','E'):
    cols=[c for c in allc if c not in fams[nm]]; g=judge(cols)
    br=[]
    if g['balf']!='1': br.append('J2=%s'%g['balf'])
    if g['hitsf']!='1': br.append('J3=%s'%g['hitsf'])
    if g['ps']!=(J4,t4): br.append('J4=%d/%d'%g['ps'])
    if g['sep'][0]!=J5: br.append('J5=%d'%g['sep'][0])
    famres['del_'+nm]=dict(cols=len(cols),broken=br,rank=g['rank'],sep=g['sep'][0])
    print("[FAM] del_%s cols=%2d rank=%d sep=%2d broken=%s"%(nm,len(cols),g['rank'],g['sep'][0],br or 'NONE'))
# single-axis deletions
bad=[]; sepmin=[]
for c in allc:
    cols=[x for x in allc if x!=c]; g=judge(cols)
    s=g['sep'][0]
    if s!=J5: bad.append((lab[c],s))
    sepmin.append((s,lab[c]))
print("[AXIS] single-axis deletions that break J5: %d/%d  %s"%(len(bad),NC,bad[:10]))
print("[AXIS] worst J5 after single deletion = %d ; unchanged for %d axes"%(min(s for s,_ in sepmin), NC-len(bad)))
print("PR-1 (family deletion breaks J5 or J4): %s"%( "HOLDS" if all(famres['del_'+nm]['broken'] for nm in 'VFE') else "REFUTED"))
print("PR-2 (some single-axis deletion breaks J5): %s -> %s"%( "HOLDS" if bad else "REFUTED (generator is irredundant at axis level)",
      "irredundant" if not bad else "redundant"))
json.dump({"families":{k:len(v) for k,v in fams.items()},
  "calibration":{"J1":J1,"J2":[str(J2f),J2],"J3":[str(J3f),J3],"J4":[J4,t4],"J5":[J5,nt]},
  "family_deletions":famres,"single_axis_breaks_J5":bad,"single_axis_min_sep":min(s for s,_ in sepmin)},
  io.open(os.path.join(ROOT,"data","67_r27a_rt3_deletion.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
