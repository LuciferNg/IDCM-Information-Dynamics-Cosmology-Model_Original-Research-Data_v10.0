#!/usr/bin/env python3
"""O222 R21/N2d -- is the V half of the rank-3 realisation the canonical max-margin normal system
determined by (K, U)?  Contract: docs/33_r21_n2d_contract.md.  Float construction (discovery only).
Usage: /usr/bin/python3 -u scripts/45_r21_n2d_maxmargin.py"""
import importlib.util, json, os, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
spec=importlib.util.spec_from_file_location("b5n2d", os.path.join(HERE,"12_b5_budget.py")); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
_mm,K,_M,_h,_i,_t=m.load_machine()
J=json.load(open(os.path.join(ROOT,"data","40_candidates.json"),encoding="utf-8")); cand=J.get("candidates",J)
c3=[c for c in cand if len(c["U"][0])==3][0]
U=np.array(c3["U"],float); V=np.array(c3["V"],float); Kl=np.array(K,float)
patt={}
for i in range(len(Kl)): patt.setdefault(tuple(Kl[i]), i)
idx=sorted(patt.values()); Uc=U[idx]; Kc=Kl[idx]; n=Uc.shape[0]
def maxmargin(kcol, steps=6000, lr=0.05):
    rng=np.random.default_rng(12345); v=rng.normal(size=3); v/=np.linalg.norm(v)
    for _ in range(steps):
        sc=kcol*(Uc@v); mn=sc.min(); act=sc<=mn+1e-12
        if not act.any(): break
        g=-(kcol[act,None]*Uc[act]).mean(axis=0)
        v=v-lr*g; v/=max(np.linalg.norm(v),1e-12)
    return v, float(np.min(kcol*(Uc@v)))
NAX=len(K[0])
res=[maxmargin(Kc[:,j]) for j in range(NAX)]
VM=np.array([r[0] for r in res]); marg=[r[1] for r in res]
vs=np.sign(VM@VM.T); vs[vs==0]=1
vsig=np.sign(V@V.T); vsig[vsig==0]=1
mm=int((vs!=vsig).sum()); tot=NAX*NAX
rec=sum(1 for i in range(n) for j in range(NAX) if np.sign(Uc[i]@VM[j])==Kc[i][j])
out={"mismatch_vsign":mm,"total":tot,"pct":round(100*mm/tot,2),"min_margin":min(marg),
     "median_margin":sorted(marg)[len(marg)//2],"max_margin":max(marg),
     "reproduces_K_on_12_classes":[rec,n*NAX],"float_only":True}
print(json.dumps(out))
json.dump(out,open(os.path.join(ROOT,"data","45_r21_n2d_results.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
