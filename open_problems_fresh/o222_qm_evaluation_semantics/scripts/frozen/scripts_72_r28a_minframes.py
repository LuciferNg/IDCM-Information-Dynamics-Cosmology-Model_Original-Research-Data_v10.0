#!/usr/bin/env python3
"""O222 R28/A -- structure of the MINIMUM separating frames (exhaustive over all 4-subsets) + a rank-6 basis.
PRE-REGISTERED: Pr-1 the number of 4-element separating frames is small (< 5000); Pr-2 no minimum frame
lies inside a single axis family; Pr-3 the minimum size for rank_Q = 6 equals 6 (a matroid basis).
Usage: /usr/bin/python3 -u scripts/72_r28a_minframes.py"""
import importlib.util, io, json, os, collections, itertools
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("mX",os.path.join(HERE,"12_b5_budget.py")); mX=importlib.util.module_from_spec(sp); sp.loader.exec_module(mX)
_mm,K,MUL,hx,idx,_t=mX.load_machine()
NR=len(K); NC=len(K[0]); lab=[str(x) for x in (idx if isinstance(idx,list) else range(NC))]

rows=[tuple(K[i][a] for a in range(NC)) for i in range(NR)]
reps=[]; seen=set()
for i in range(NR):
    if rows[i] not in seen: seen.add(rows[i]); reps.append(i)
pairs=[(u,v) for x,u in enumerate(reps) for v in reps[x+1:]]
cover={a:frozenset(i for i,(u,v) in enumerate(pairs) if K[u][a]!=K[v][a]) for a in range(NC)}
ALL=frozenset(range(len(pairs)))
def sep(cols): 
    s=frozenset()
    for c in cols: s|=cover[c]
    return s==ALL
cnt4=0; mixes=collections.Counter(); ex=[]
for combo in itertools.combinations(range(NC),4):
    if sep(combo):
        cnt4+=1; mixes[''.join(sorted(lab[c][0] for c in combo))]+=1
        if len(ex)<5: ex.append([lab[c] for c in combo])
print("4-element separating frames: %d  (witnesses %s)"%(cnt4,ex))
print("family mixtures:",dict(mixes))
def rank_bar(A):
    A=[[F(x) for x in r] for r in A]; m=len(A); n=len(A[0]); r=0
    for c in range(n):
        p=next((i for i in range(r,m) if A[i][c]!=0),None)
        if p is None: continue
        A[r],A[p]=A[p],A[r]
        for i in range(r+1,m):
            if A[i][c]!=0:
                f=A[i][c]/A[r][c]
                for k in range(c,n): A[i][k]=A[i][k]-f*A[r][k]
        r+=1
        if r==m: break
    return r
# minimal size for rank_Q = 6: PROVED 0 at k=5 (5 vectors span <= 5 dimensions), so we only need one 6-basis
rk=lambda cols: rank_bar([[K[i][c] for c in cols] for i in range(NR)])
c5=0
print("5-subsets with rank 6: %d  -- proved by the dimension argument (5 vectors span <= 5)"%c5)
w6=None
for combo in itertools.combinations(range(NC),6):
    if rk(combo)==6: w6=[lab[x] for x in combo]; break
print("first 6-subset with rank 6: %s"%(w6,))
w6idx=[lab.index(x) for x in w6]; print("  -> does it also separate? %s"%sep(w6idx))
# pre-registered checks
print("Pr-1 (count < 5000): %s"%("HOLDS" if cnt4<5000 else "REFUTED (%d)"%cnt4))
print("Pr-2 (no single-family min frame): %s"%("HOLDS" if all(len(set(m))>1 for m in mixes) else "REFUTED"))
print("Pr-3 (min size for rank 6 = 6): %s"%("HOLDS" if c5==0 else "REFUTED"))
json.dump({"n_min_frames_4":cnt4,"mixtures":dict(mixes),"examples":ex,"rank6_at_5":c5,"rank6_basis":w6},
 io.open(os.path.join(ROOT,"data","72_r28a_minframes.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
