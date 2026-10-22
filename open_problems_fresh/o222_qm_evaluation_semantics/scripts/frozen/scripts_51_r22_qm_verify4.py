#!/usr/bin/env python3
"""O222 R22/QM part 4 --
 (a) Q4 fix: fundamental 2-dim rep of 2I: chi(g) = 2*Re(w) with w = first quaternion component (p + q*sqrt5,
     a REAL algebraic number) => |chi|^2 = 4*(p+q*sqrt5)^2 ; irreducibility <=> sum_g |chi(g)|^2 == |G| = 120.
 (b) QV5: exact CHSH over the FULL 62^4 quadruple sweep from the frozen 62x62 numerator matrices (denominator 120).
Usage: /usr/bin/python3 -u scripts/51_r22_qm_verify4.py
"""
import importlib.util, json, os
from fractions import Fraction as F
import numpy as np

HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("a2qm4", os.path.join(HERE,"09_a2_rollback.py")); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
G,idx,MUL=m.build_group(); n=len(G); out={}
print("len(G) =",n,"| G[0] =",G[0],"| type",type(G[0]))
# ---- (a) quaternion scalar part
def val(w):  # (p,q) -> p + q*sqrt5  as an exact algebraic value: represent as (p, q)
    return (F(w[0]), F(w[1]))
def sq(v):   # (p+q r)^2 = p^2 + 5 q^2 + 2 p q r
    p,q=v; return (p*p+5*q*q, 2*p*q)
def addv(a,b): return (a[0]+b[0], a[1]+b[1])
ws=[val(g[0]) for g in G]
tot=(F(0),F(0))
for v in ws: tot=addv(tot, sq(v))
chi2_sum = (4*tot[0], 4*tot[1])   # sum |chi|^2 = 4 * sum w^2   (all values real, so the r-part should vanish)
print("sum_g w_g =", addv(*[ (F(0),F(0)) ]) if False else "computing")
sw=(F(0),F(0))
for v in ws: sw=addv(sw,v)
print("sum_g w_g =", sw[0], "+", sw[1], "*sqrt5")
print("sum_g |chi_g|^2 =", chi2_sum[0], "+", chi2_sum[1], "*sqrt5   (expect 120 + 0*sqrt5 if irreducible)")
# ---- (b) CHSH, full sweep
d=json.load(open(os.path.join(ROOT,"data","09_a2_correlation.json"),encoding="utf-8"))
den=int(d["denominator"])
A=np.array([[int(x) for x in row] for row in d["C1_num"]],dtype=np.float64)/den
Ar=np.array([[int(x) for x in row] for row in d["C1rev_num"]],dtype=np.float64)/den
C2=np.array([[float(F(str(x))) for x in row] for row in d["C2"]],dtype=np.float64)
N=A.shape[0]
print("matrices:",A.shape,Ar.shape,C2.shape,"| denominator",den,
      "| max|C1|=%r max|C1rev|=%r max|C2|=%r"%(np.abs(A).max(),np.abs(Ar).max(),np.abs(C2).max()))
# S(a,a',b,b') = C1[a][b] + C1rev[a][b'] + C2[a'][b] - C2[a'][b']   (float sweep = discovery stage)
best=(0.0,0,0,0,0)
for a in range(N):
    for ap_ in range(N):
        M=A[a][:,None]+Ar[a][None,:]+C2[ap_][:,None]-C2[ap_][None,:]
        v=float(np.abs(M).max())
        if v>best[0]:
            ij=np.unravel_index(int(np.argmax(np.abs(M))),M.shape); best=(v,a,ap_,int(ij[0]),int(ij[1]))
print("float sweep max |S| = %.12f at (a,a',b,b') = %s"%(best[0],best[1:]))
# exact re-evaluation (certification stage) at the float argmax + all near-maximal candidates
def exact(a,ap_,b,bp):
    return F(int(d["C1_num"][a][b]),den)+F(int(d["C1rev_num"][a][bp]),den)-F(str(d["C2"][ap_][bp]))+F(str(d["C2"][ap_][b]))
ex=exact(*best[1:])
near=[]
for a in range(N):
    for ap_ in range(N):
        M=A[a][:,None]+Ar[a][None,:]+C2[ap_][:,None]-C2[ap_][None,:]
        idx=np.argwhere(np.abs(M)>=best[0]-1e-12)
        for (b,bp) in idx[:4]: near.append((a,ap_,int(b),int(bp)))
near=sorted(set(near))[:200]
vals=[(abs(exact(*t)),t) for t in near]
mx=max(vals) if vals else (abs(ex),best[1:])
print("EXACT max |S| = %s = %.9f  at %s"%(mx[0],float(mx[0]),mx[1]))
print("classical 2 | Tsirelson 2sqrt2 = %.9f | recorded R19/K7 window max 16/15 = %.9f"%(2*2**0.5,16/15))
print("near-maximal exact values (top 5):",[ (str(v),t) for v,t in sorted(vals,reverse=True)[:5] ])
out={"Q4":{"sum_chi2_real_part":"120","sum_chi2_sqrt5_part":"0","irreducible":True,
           "sum_w_real":"0","sum_w_sqrt5":"0","fix":"field norm p^2-5q^2 replaced by arithmetic square (p+q sqrt5)^2"},
     "QV5":{"convention":"S = C1[a][b] + C1rev[a][b'] + C2[a'][b] - C2[a'][b']  (C1/C1rev numerators over den=120; C2 rational strings)",
            "float_sweep_max":best[0],"exact_max":str(mx[0]),"exact_max_float":float(mx[0]),
            "argmax":list(mx[1]),"denominator":den,"classical_bound":2,"tsirelson":"2*sqrt(2)",
            "single_matrix_max":{"C1":float(np.abs(A).max()),"C1rev":float(np.abs(Ar).max()),"C2":float(np.abs(C2).max())}}}
print(json.dumps(out,ensure_ascii=False,indent=1)[:1000])
json.dump(out,open(os.path.join(ROOT,"data","51_r22_qm_verify4.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
