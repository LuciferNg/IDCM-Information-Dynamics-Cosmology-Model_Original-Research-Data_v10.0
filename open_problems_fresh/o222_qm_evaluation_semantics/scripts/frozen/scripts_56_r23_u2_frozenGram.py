#!/usr/bin/env python3
"""O222 R23/U2 -- canonical V-side test with the FROZEN Gram.

Key algebra (exact):  vsign = sgn(Kc^T G Kc) with G the 12x12 Gram of the 12 class points.
The N2d closed form used the SEARCH candidate's U (arbitrary within the realisation family) -> not canonical.
Here G is the FROZEN Gram  G_ij = r_i . r_j  (exact Q(sqrt5), from the machine's own vectors), so the whole
computation is zero-parameter and frozen-data-determined.  Any two 12x3 factorisations of a rank-3 PSD G differ by
an orthogonal map, and sgn(Kc^T G Kc) is invariant under that -> the value is canonical.
Usage: /usr/bin/python3 -u scripts/56_r23_u2_frozenGram.py
"""
import importlib.util, json, os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("a2u2", os.path.join(HERE,"09_a2_rollback.py")); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
axes,Uax,ids,types,hvec=m.load_inputs(); G,idx,MUL=m.build_group()
add,mul,S=m.add,m.mul,m.sgn
dot3=lambda a,b: add(add(mul(a[0],b[0]),mul(a[1],b[1])),mul(a[2],b[2]))
R=[m.rot_ref(q,Uax[0]) for q in G]
sp2=importlib.util.spec_from_file_location("b5u2", os.path.join(HERE,"12_b5_budget.py")); m2=importlib.util.module_from_spec(sp2); sp2.loader.exec_module(m2)
_mm,K,_M,_h,_i,_t=m2.load_machine()
patt={}
for i in range(len(K)): patt.setdefault(tuple(K[i]), i)
rep=sorted(patt.values()); Kc=[[K[i][j] for j in range(len(K[0]))] for i in rep]
N=len(K[0]); n=12
Gr=[[dot3(R[rep[i]],R[rep[j]]) for j in range(n)] for i in range(n)]     # frozen Gram (exact Q(sqrt5))
Q=[[None]*N for _ in range(N)]
zero=(0,0)
for a in range(N):
    for b in range(N):
        acc=zero
        for i in range(n):
            ka=Kc[i][a]
            if ka==0: continue
            for i2 in range(n):
                kb=Kc[i2][b]
                if kb==0: continue
                if ka*kb==1: acc=add(acc,Gr[i][i2])
                else: acc=add(acc,mul(Gr[i][i2],(-1,0)))
        Q[a][b]=acc
J=json.load(open(os.path.join(ROOT,"data","40_candidates.json"),encoding="utf-8")); cand=J.get("candidates",J)
c3=[c for c in cand if len(c["U"][0])==3][0]; V=c3["V"]
vsign=[[1 if sum(V[a][k]*V[b][k] for k in range(3))>0 else (-1 if sum(V[a][k]*V[b][k] for k in range(3))<0 else 0) for b in range(N)] for a in range(N)]
qv=[[S(Q[a][b]) for b in range(N)] for a in range(N)]
bad=sum(1 for a in range(N) for b in range(N) if qv[a][b]!=vsign[a][b])
zerocnt=sum(1 for a in range(N) for b in range(N) if qv[a][b]==0)
print("FROZEN Gram (exact Q(sqrt5)) -> sgn(Kc^T G_frozen Kc) vs certified vsign : mismatches = %d/%d  (zeros %d)"%(bad,N*N,zerocnt))
# also: rank of the frozen Gram (exact, via the trace of powers being non-degenerate) -> report as integer rank over Q(sqrt5)
from fractions import Fraction as F
W=[[Gr[i][j][0] for j in range(n)] for i in range(n)]  # real part only is NOT enough in general; do full pair elimination
def pairmul(x,y): return (x[0]*y[0]+5*x[1]*y[1], x[0]*y[1]+x[1]*y[0])
rows=[[ (F(Gr[i][j][0]),F(Gr[i][j][1])) for j in range(n)] for i in range(n)]
def iszero(v): return v[0]==0 and v[1]==0
r=0
for c in range(n):
    piv=None
    for i in range(r,n):
        if not iszero(rows[i][c]): piv=i; break
    if piv is None: continue
    rows[r],rows[piv]=rows[piv],rows[r]
    inv=(rows[r][c][0], -rows[r][c][1])
    den=pairmul(rows[r][c],inv)[0]
    rows[r]=[ (pairmul(x,inv)[0]/den, pairmul(x,inv)[1]/den) for x in rows[r] ]
    for i in range(n):
        if i!=r and not iszero(rows[i][c]):
            f=rows[i][c]; rows[i]=[ (rows[i][k][0]-pairmul(f,rows[r][k])[0], rows[i][k][1]-pairmul(f,rows[r][k])[1]) for k in range(n)]
    r+=1
print("frozen Gram rank over Q(sqrt5) =",r)
out={"frozen_gram_rank":r,"vsign_mismatches":bad,"total":N*N,"zeros":zerocnt,
     "verdict":"FROZEN-DATA-DETERMINED (canonical)" if bad==0 else "mismatch -> not this construction"}
print(json.dumps(out,ensure_ascii=False,indent=1))
json.dump(out,open(os.path.join(ROOT,"data","56_r23_u2_frozenGram.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
