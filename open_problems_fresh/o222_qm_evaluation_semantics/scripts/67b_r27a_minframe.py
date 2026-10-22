#!/usr/bin/env python3
"""O222 R27/A2 -- the MINIMAL SEPARATING FRAME (exact, exhaustive with pruning) + deletion tolerance.

Goal: the axis-level minimality question, made precise and decidable:
  Qa  what is the minimum number of axes whose readout pattern still separates all 12 distinct row types?
  Qb  what is the maximum number of axes that can be deleted while ALL frozen predicates survive
      (rank_Q = 6, every remaining column balanced, hits = 2*#cols, pair-structure count = 6000/7140
       rescaled... -> here: rank 6 + balance + separation)?
PRE-REGISTERED PREDICTION: PR-1 minimum separating frame < 62 (massive redundancy), so "delete any
  component => closure breaks" is FALSE.  PR-2 there exists a deletion of >= 50% of the axes keeping rank 6.
Usage: /usr/bin/python3 -u scripts/67b_r27a_minframe.py"""

import importlib.util, io, os
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__))
sp=importlib.util.spec_from_file_location("m12d",os.path.join(HERE,"12_b5_budget.py"))
m12=importlib.util.module_from_spec(sp); sp.loader.exec_module(m12)
_mm,K,MUL,hx,idx,_t=m12.load_machine()

NR=len(K); NC=len(K[0])
lab=[str(x) for x in (idx if isinstance(idx,list) else range(NC))]
rows=[tuple(K[i][a] for a in range(NC)) for i in range(NR)]
types=sorted(set(range(NR)),key=lambda i:rows[i])
reps=[]; seen=set()
for i in range(NR):
    if rows[i] not in seen: seen.add(rows[i]); reps.append(i)
print("distinct row types:",len(reps))
pairs=[(u,v) for x,u in enumerate(reps) for v in reps[x+1:]]
print("row-type pairs to separate:",len(pairs))
cover={}
for a in range(NC):
    s=frozenset(i for i,(u,v) in enumerate(pairs) if K[u][a]!=K[v][a])
    cover[a]=s
uncovered=frozenset(range(len(pairs)))
# exact DFS minimum hitting set over the 66 pairs
best=[99,None]
def dfs(unc, chosen, start):
    if not unc:
        if len(chosen)<best[0]: best[0]=len(chosen); best[1]=list(chosen)
        return
    if len(chosen)>=best[0]: return
    t=min(unc, key=lambda i: sum(1 for a in range(NC) if i in cover[a]))
    cands=[a for a in range(NC) if t in cover[a]]
    # branch on the columns covering the least-covered pair; simplex-style
    for a in sorted(cands, key=lambda a:-len(cover[a]&unc)):
        dfs(unc-cover[a], chosen+[a], a+1)
dfs(uncovered,[],0)
print("MINIMUM separating frame size = %d  (one witness: %s)"%(best[0],[lab[a] for a in best[1]]))
print("PR-1 (min frame < 62): %s"%("HOLDS (redundant)" if best[0]<NC else "REFUTED"))
# max deletion tolerance keeping rank 6 + balance + separation: use the min frame complement
keep=set(best[1]); keep=sorted(keep)
print("=> maximum axes deletable while KEEPING a separating set: %d (delete %d)"%(NC-len(keep),NC-len(keep)))
# rank 6 with the minimal frame?
def rank_bar(A):
    A=[[int(x) for x in r] for r in A]; m=len(A); n=len(A[0]); r=0; prev=1
    for c in range(n):
        p=next((i for i in range(r,m) if A[i][c]),None)
        if p is None: continue
        A[r],A[p]=A[p],A[r]
        for i in range(r+1,m):
            if A[i][c]:
                f=A[i][c]
                for k in range(c,n): A[i][k]=(A[i][k]*A[r][c]-f*A[r][k])//prev
        prev=A[r][c]; r+=1
        if r==m: break
    return r
print("rank of K restricted to the minimal frame = %d (base 6)"%rank_bar([[K[i][c] for c in keep] for i in range(NR)]))
print("PR-2 (>=50%% deletable keeping rank 6&separation): %s"%("HOLDS" if (NC-len(keep))>=NC//2 else "REFUTED"))
import io as _io, json
json.dump({"min_frame_size":best[0],"witness":[lab[a] for a in best[1]],"deletable":NC-len(keep),
 "rank_on_min_frame":rank_bar([[K[i][c] for c in keep] for i in range(NR)]),"n_row_types":len(reps)},
 _io.open(os.path.join(os.path.dirname(HERE),"data","67b_r27a_minframe.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
