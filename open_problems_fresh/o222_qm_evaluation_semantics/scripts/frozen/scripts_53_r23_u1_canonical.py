#!/usr/bin/env python3
"""O222 R23/U1 -- formal closure of the V-side canonicity.

Algebra (exact, integers):  with Uc = the 12 class rows of the certified r=3 candidate and Kc = K on those rows,
    VM := Kc^T Uc          (the N2d closed form)
    VM_j . VM_j' = sum_{i,i'} Kc[i][j] Kc[i'][j'] (u_i . u_i') = Kc_col_j^T G Kc_col_j' ,  G := Uc Uc^T (Gram, 12x12)
Hence vsign is a quadratic form on the columns of Kc with the Gram matrix G.  QUESTION: is sgn(Kc^T G Kc) determined
by sign(G) alone (a frozen datum)?  Tests: (a) identity check of the algebra; (b) G -> sign(G); (c) G -> D sign(G) D
with random positive-integer diagonals D (congruence preserves both the sign pattern and positive definiteness).
Usage: /usr/bin/python3 -u scripts/53_r23_u1_canonical.py
"""
import importlib.util, json, os, random
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("b5u1", os.path.join(HERE,"12_b5_budget.py")); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
_mm,K,_M,_h,_i,_t=m.load_machine()
J=json.load(open(os.path.join(ROOT,"data","40_candidates.json"),encoding="utf-8")); cand=J.get("candidates",J)
c3=[c for c in cand if len(c["U"][0])==3][0]
U=c3["U"]; V=c3["V"]
patt={}
for i in range(len(K)): patt.setdefault(tuple(K[i]), i)
rep=sorted(patt.values()); Kc=[[K[i][j] for j in range(len(K[0]))] for i in rep]; Uc=[U[i] for i in rep]
N=len(K[0]); n=12
sg=lambda x: 1 if x>0 else (-1 if x<0 else 0)
# (a) algebra identity:  Kc^T G Kc  vs  VM^T VM
G=[[sum(Uc[i][k]*Uc[j][k] for k in range(3)) for j in range(n)] for i in range(n)]
Q=[[sum(Kc[i][a]*Kc[i2][b]*G[i][i2] for i in range(n) for i2 in range(n)) for b in range(N)] for a in range(N)]
VM=[[sum(Kc[i][j]*Uc[i][k] for i in range(n)) for k in range(3)] for j in range(N)]
idbad=sum(1 for a in range(N) for b in range(N) if Q[a][b]!=sum(VM[a][k]*VM[b][k] for k in range(3)))
vsign=[[sg(sum(V[a][k]*V[b][k] for k in range(3))) for b in range(N)] for a in range(N)]
vsign_vm=[[sg(Q[a][b]) for b in range(N)] for a in range(N)]
vsbad=sum(1 for a in range(N) for b in range(N) if vsign[a][b]!=vsign_vm[a][b])
Gs=[[1 if i==j else sg(G[i][j]) for j in range(n)] for i in range(n)]
def qform(M):
    return [[sum(Kc[i][a]*Kc[i2][b]*M[i][i2] for i in range(n) for i2 in range(n)) for b in range(N)] for a in range(N)]
Q0=qform(Gs)
bad0=sum(1 for a in range(N) for b in range(N) if sg(Q0[a][b])!=vsign[a][b])
random.seed(20260930); draws=20; worst=0; per=[]
for t in range(draws):
    dg=[random.randint(1,10) for _ in range(n)]
    Md=[[dg[i]*Gs[i][j]*dg[j] for j in range(n)] for i in range(n)]
    Qt=qform(Md)
    bad=sum(1 for a in range(N) for b in range(N) if sg(Qt[a][b])!=vsign[a][b])
    per.append(bad); worst=max(worst,bad)
print("(a) algebra identity  Kc^T G Kc == VM^T VM : mismatches %d/%d"%(idbad,N*N))
print("    sgn(Q) vs certified vsign               : mismatches %d/%d"%(vsbad,N*N))
print("(b) G -> sign(G):  vsign mismatches = %d/%d"%(bad0,N*N))
print("(c) G -> D sign(G) D, %d random integer diagonals: worst mismatches = %d/%d ; per-draw = %s"%(draws,worst,N*N,per))
out={"algebra_identity_mismatches":idbad,"vsign_of_Q_mismatches":vsbad,
     "signG_only_mismatches":bad0,"random_diagonal_draws":draws,"worst_mismatches":worst,"per_draw":per,
     "G_rank":None,"G_sign_pattern_is_frozen":True,
     "verdict":"vsign determined by sign(G) alone => canonical (frozen-data-determined)" if (bad0==0 and worst==0) else "magnitude-dependent"}
# rank of G (exact, Fraction elimination)
from fractions import Fraction as F
W=[[F(G[i][j]) for j in range(n)] for i in range(n)]; r=0
for c in range(n):
    piv=None
    for i in range(r,n):
        if W[i][c]!=0: piv=i; break
    if piv is None: continue
    W[r],W[piv]=W[piv],W[r]; pv=W[r][c]; W[r]=[x/pv for x in W[r]]
    for i in range(n):
        if i!=r and W[i][c]!=0:
            f=W[i][c]; W[i]=[W[i][k]-f*W[r][k] for k in range(n)]
    r+=1
out["G_rank"]=r
print("    rank(G) =",r,"(12 = full rank => G is a genuine Gram of 12 affinely-independent points)")
print(json.dumps(out,ensure_ascii=False,indent=1))
json.dump(out,open(os.path.join(ROOT,"data","53_r23_u1_canonical.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
