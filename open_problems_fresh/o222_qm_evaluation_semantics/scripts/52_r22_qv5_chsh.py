#!/usr/bin/env python3
"""O222 R22/QV5 (formal) -- exact, COMPLETE maximisation of |S| under the AUTHORITATIVE criterion
(scripts/09 chsh_max: modes raw / distinct / distinct_anti / all4; all4 = four settings pairwise distinct
 + antipodal veto; S = P[i] - Q[j] with P=C[a]+C[a2], Q=C[a]-C[a2]).
Difference from scripts/09: no top3/bot3 heuristic -- for each (a,a2,i) the best j is the extreme Q value with
the j==i exclusion resolved by the next extreme, i.e. an exact complete maximisation.  Exact integers /100... denominator.
Usage: /usr/bin/python3 -u scripts/52_r22_qv5_chsh.py
"""
import importlib.util, json, os
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); REPO=os.path.dirname(os.path.dirname(ROOT))
spec=importlib.util.spec_from_file_location("b5q", os.path.join(HERE,"12_b5_budget.py")); m5=importlib.util.module_from_spec(spec); spec.loader.exec_module(m5)
_mm,K,_M,_h,_i,_t=m5.load_machine()
N=len(K[0]); D=len(K)
d=json.load(open(os.path.join(ROOT,"data","09_a2_correlation.json"),encoding="utf-8"))
den=int(d["denominator"])
C1=[[int(x) for x in row] for row in d["C1_num"]]; C2=[[F(str(x)) for x in row] for row in d["C2"]]
# authentic antipodal test (replicates scripts/09 pair_antipodal): sgn(dot)<0 and dot^2 == na*nb, exact Q(sqrt5)
sp9=importlib.util.spec_from_file_location("a2anti", os.path.join(HERE,"09_a2_rollback.py")); m9=importlib.util.module_from_spec(sp9); sp9.loader.exec_module(m9)
_ax,UX,_i9,_t9,_h9=m9.load_inputs(); add,mul,S9=m9.add,m9.mul,m9.sgn
dot3=lambda p,q: add(add(mul(p[0],q[0]),mul(p[1],q[1])),mul(p[2],q[2]))
anti=set(); antiK=set()
for a in range(N):
    for b in range(N):
        if a==b: continue
        dt=dot3(UX[a],UX[b]); na=dot3(UX[a],UX[a]); nb=dot3(UX[b],UX[b])
        if S9(dt)<0 and mul(dt,dt)==mul(na,nb): anti.add((a,b))
        if all(K[s][a]==-K[s][b] for s in range(D)): antiK.add((a,b))
print("authentic antipodal ordered pairs =",len(anti),"| K-column variant =",len(antiK))
def toint(M, scale=None):
    if scale is None:
        sc=1
        for r in M:
            for v in r: sc = sc*v.denominator//__import__("math").gcd(sc,v.denominator)
        scale=sc
    return [[int(v*scale) for v in r] for r in M], scale
def complete_max(Cmat, mode, force_scale=None):
    """exact complete max |P[i]-Q[j]| with the all4/distinct veto rules (integers)."""
    if force_scale is not None:
        M, sc = Cmat, force_scale
    else:
        M, sc = toint([[F(v) if not isinstance(v,F) else v for v in r] for r in Cmat]) if not isinstance(Cmat[0][0],int) else (Cmat, 1)
    best=(0,None)
    rng=range(N)
    for a in rng:
        Na=M[a]
        for a2 in rng:
            if mode!='raw' and a2==a: continue
            Na2=M[a2]
            P=[Na[i]+Na2[i] for i in rng]
            Q=[Na[j]-Na2[j] for j in rng]
            idx=sorted(range(N), key=lambda j: Q[j])
            for i in rng:
                if mode=='all4' and (i==a or i==a2): continue
                if mode in ('distinct_anti','all4') and ((a,i) in anti or (a2,i) in anti): continue
                lo=next((j for j in idx if j!=i and not (mode in ('distinct_anti','all4') and ((a,j) in anti or (a2,j) in anti)) and not (mode=='all4' and (j==a or j==a2)) and not (mode!='all4' and False)), None)
                hi=next((j for j in reversed(idx) if j!=i and not (mode in ('distinct_anti','all4') and ((a,j) in anti or (a2,j) in anti)) and not (mode=='all4' and (j==a or j==a2))), None)
                for j in (lo,hi):
                    if j is None: continue
                    v=abs(P[i]-Q[j])
                    if v>best[0]: best=(v,(a,a2,i,j))
    return F(best[0], sc), best[1]
# C1 is a numerator matrix over den
out={"denominator":den,"antipodal_pairs_authentic":len(anti),"antipodal_pairs_Kcolumn":len(antiK),"results":{}}
for name,M,sc in (("C1",C1,den),("C2",C2,None)):
    for mode in ("raw","distinct","distinct_anti","all4"):
        if sc is None:
            Mi, scx = toint(M)
        else:
            Mi, scx = M, den
        val,arg = complete_max(Mi,mode, force_scale=scx)
        out["results"]["%s_%s"%(name,mode)]={"max_abs_S":str(val),"float":float(val),"argmax":list(arg) if arg else None}
        print("%s %-14s max|S| = %-12s = %.6f  argmax=%s"%(name,mode,val,float(val),arg))
out["bounds"]={"classical":2,"tsirelson":"2*sqrt(2)=2.828427...","trivial":4}
print("classical bound 2 ; Tsirelson 2sqrt2 = %.6f"%(2*2**0.5))
json.dump(out,open(os.path.join(ROOT,"data","52_r22_qv5_chsh.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
