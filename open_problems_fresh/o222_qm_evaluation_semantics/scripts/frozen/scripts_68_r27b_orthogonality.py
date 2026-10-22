#!/usr/bin/env python3
"""O222 R27/B -- the ORTHOGONALITY (independence) matrix, defined operationally: cells x perturbations.

Cells (5 exactly computable predicates, each calibrated on the frozen record):
  c1 = rank_Q(K)                       (record 6)
  c2 = fraction of balanced columns     (record 1)
  c3 = hits/(2*#cols)                   (record 1)
  c4 = pair-structure count             (record 6000/7140)
  c5 = #distinct row types              (record 12)
Perturbations: 3 family deletions + 62 single-axis deletions + 62 diagonal single-entry flips
 + 120 flips of column 0 = 247 perturbations.
Independence = rank over Q of the 5 x P response matrix (after removing the constant column).
PRE-REGISTERED: Pr-1 rank >= 3 (at least three genuinely independent judgement axes).
                Pr-2 c2 and c3 are NOT proportional (an entry flip can break balance without changing hits).
Usage: /usr/bin/python3 -u scripts/68_r27b_orthogonality.py"""
import importlib.util, io, json, os, collections
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("m12g",os.path.join(HERE,"12_b5_budget.py")); m12=importlib.util.module_from_spec(sp); sp.loader.exec_module(m12)
_mm,K,MUL,hx,idx,_t=m12.load_machine()
NR=len(K); NC=len(K[0]); lab=[str(x) for x in (idx if isinstance(idx,list) else range(NC))]
fams=collections.defaultdict(list)
for j,l in enumerate(lab): fams[l[0]].append(j)
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
def cells(M,cols):
    c1=rank_bar([[M[i][c] for c in cols] for i in range(NR)])
    c2=F(sum(1 for a in cols if sum(M[i][a] for i in range(NR))==0),len(cols))
    order=[(a,b) for a in cols for b in cols]; L=[]; s=0; h=0
    for (a,b) in order:
        for ctx in (a,b):
            if L and L[-1][0]==ctx: h+=1; continue
            L.append((ctx,M[s][ctx],s)); s=MUL_ov[s][hx[ctx]] if False else MUL[s][hx[ctx]]
        _c,_v,sa=L.pop(); s=sa
        if L and L[-1][0]==b: h+=1
        else: L.append((b,M[s][b],s)); s=MUL[s][hx[b]]
    c3=F(h,2*len(cols))
    rows=[tuple(M[i][a] for a in cols) for i in range(NR)]; cnt=0
    for i in range(NR):
        for j in range(i+1,NR):
            if rows[i]!=rows[j] and tuple(-x for x in rows[i])!=rows[j]: cnt+=1
    c4=cnt; c5=len(set(rows))
    return [c1,c2,c3,c4,c5]
base=cells(K,list(range(NC)))
print("CALIBRATION cells:",[str(x) for x in base],"(record: 6, 1, 1, 6000, 12)")
def flip(M,i,a):
    N=[row[:] for row in M]; N[i][a]=-N[i][a]; return N
perts=[]
for nm in ('V','F','E'):
    cols=[c for c in range(NC) if c not in fams[nm]]; perts.append(("del_"+nm,lambda cols=cols: cells(K,cols)))
for c in range(NC):
    cols=[x for x in range(NC) if x!=c]; perts.append(("del_%s"%lab[c],lambda cols=cols: cells(K,cols)))
for i in range(NC):
    M=flip(K,i,i); perts.append(("flipdiag_%d"%i,lambda M=M: cells(M,list(range(NC)))))
for i in range(NR):
    M=flip(K,i,0); perts.append(("flipcol0_%d"%i,lambda M=M: cells(M,list(range(NC)))))
print("perturbations:",len(perts))
rows=[[],  [],  [],  [],  []]
names=[]
for nm,f in perts:
    v=f(); names.append(nm)
    for k in range(5): rows[k].append(v[k]-base[k])
# drop the constant (all-zero) cell rows
deltas=[(k,r) for k,r in enumerate(rows) if any(x!=0 for x in r)]
print("cells that respond to at least one perturbation:",[ (k+1,len(r)) for k,r in deltas])
rk=rank_bar([r for _,r in deltas]) if deltas else 0
print("rank over Q of the response matrix (%d responsive cells x %d perturbations) = %d"%(len(deltas),len(perts),rk))
print("Pr-1 (rank >= 3): %s"%("HOLDS" if rk>=3 else "REFUTED (rank=%d)"%rk))
# Pr-2: c2 vs c3 patterns
r2,r3=rows[1],rows[2]
prop=all((r2[i]*r3[0]==r3[i]*r2[0]) for i in range(len(r2)) if r2[0]!=0) if r2[0]!=0 else None
print("Pr-2 (c2 not proportional to c3): %s"%("HOLDS (independent)" if prop is False else "REFUTED/undefined prop=%s"%prop))
resp={ (k+1):sum(1 for x in r if x!=0) for k,r in enumerate(rows)}
print("per-cell number of perturbations that move it:",resp)
json.dump({"base":[str(x) for x in base],"n_perturbations":len(perts),"rank":rk,
  "responsive_cells":[k+1 for k,r in deltas],"per_cell_moves":{str(k):v for k,v in resp.items()}},
  io.open(os.path.join(ROOT,"data","68_r27b_orthogonality.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
