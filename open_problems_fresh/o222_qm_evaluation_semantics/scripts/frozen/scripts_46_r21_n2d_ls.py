#!/usr/bin/env python3
"""O222 R21/N2d(closure) -- V half of the rank-3 realisation via the CLOSED-FORM normals
    v_j := sum_{i in 12 classes} K[i][j] * u_i          (zero parameters, no search, no optimiser)
Contract: docs/33_r21_n2d_contract.md.  Float discovery stage (exact certification is the next step).
Usage: /usr/bin/python3 -u scripts/46_r21_n2d_ls.py"""
import importlib.util, json, os, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
spec=importlib.util.spec_from_file_location("b5n2d2", os.path.join(HERE,"12_b5_budget.py")); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
_mm,K,_M,_h,_i,_t=m.load_machine()
J=json.load(open(os.path.join(ROOT,"data","40_candidates.json"),encoding="utf-8")); cand=J.get("candidates",J)
c3=[c for c in cand if len(c["U"][0])==3][0]
U=np.array(c3["U"],float); V=np.array(c3["V"],float); Kl=np.array(K,float)
patt={}
for i in range(len(Kl)): patt.setdefault(tuple(Kl[i]), i)
idx=sorted(patt.values()); Uc=U[idx]; Kc=Kl[idx]; NAX=Kl.shape[1]
VM=(Kc.T @ Uc)                       # <-- the closed form
vm=np.sign(VM@VM.T); vm[vm==0]=1
vs=np.sign(V@V.T); vs[vs==0]=1
mm=int((vm!=vs).sum()); tot=NAX*NAX
rec=sum(1 for i in range(len(Uc)) for j in range(NAX) if np.sign(Uc[i]@VM[j])==Kc[i][j])
out={"construction":"v_j = sum_i K[i][j]*u_i (closed form, zero parameters)",
     "mismatch_vsign":mm,"total":tot,"pct":round(100*mm/tot,4),
     "reproduces_K_on_12_classes":[rec,len(Uc)*NAX],"float_only":True,
     "note":"U taken from the certified r=3 candidate (rigid, N1)"}
print(json.dumps(out,ensure_ascii=False))
json.dump(out,open(os.path.join(ROOT,"data","46_r21_n2d_ls.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
