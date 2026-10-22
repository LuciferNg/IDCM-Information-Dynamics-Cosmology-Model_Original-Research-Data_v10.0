#!/usr/bin/env python3
"""O222 R28/C -- the CORRECT (V,D) pair: D from path-biased marginals (exact), and the vacuity theorem.
R27/C used D = memo fraction (a proxy) and the bound failed 50/3700.  The quantum partner of the visibility
is the which-path distinguishability built from PATH PROBABILITIES: D = |P_a(+) - P_b(+)|.
PRE-REGISTERED: Pr-1 every marginal is exactly 1/2, so D = 0 for all pairs and V^2 + D^2 <= 1 holds
  vacuously (V <= 1) -> complementarity in the frozen protocol is VACUOUS, not violated;
  Pr-2 therefore any future non-vacuous claim must exhibit path-biased marginals.
Usage: /usr/bin/python3 -u scripts/74_r28c_vd_pair.py"""
import importlib.util, io, json, os, collections, itertools
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("mX",os.path.join(HERE,"12_b5_budget.py")); mX=importlib.util.module_from_spec(sp); sp.loader.exec_module(mX)
_mm,K,MUL,hx,idx,_t=mX.load_machine()
NR=len(K); NC=len(K[0]); lab=[str(x) for x in (idx if isinstance(idx,list) else range(NC))]

marg={a:F(sum(1 for i in range(NR) if K[i][a]==1),NR) for a in range(NC)}
vals=collections.Counter(marg.values())
print("marginal P(+1) value set:",{str(k):v for k,v in vals.items()})
d=json.load(io.open(os.path.join(ROOT,"data","09_a2_blind_values.json"),encoding="utf-8"))
pos={l:i for i,l in enumerate(lab)}
viol=[]; n=0; Vc=collections.Counter()
for pr in d["pairs"]:
    a=pos.get(pr["a"]); b=pos.get(pr["b"])
    if a is None or b is None: continue
    V=abs(F(pr["C1_num"],pr["den"])); D=abs(marg[a]-marg[b]); n+=1; Vc[V]+=1
    if V*V+D*D>1: viol.append((pr["a"],pr["b"],str(V),str(D)))
print("pairs:",n,"| violations with D = |P_a(+1)-P_b(+1)|:",len(viol))
print("V set:",{str(k):v for k,v in sorted(Vc.items())})
print("Pr-1 (D=0 everywhere, bound vacuous): %s"%("HOLDS" if not viol and all(v==F(1,2) for v in marg.values()) else "REFUTED"))
print("Pr-2 (implication): non-vacuous (V,D) requires path-biased marginals; frozen marginals are exactly 1/2 => none exists")
json.dump({"marginal_set":{str(k):v for k,v in vals.items()},"violations":viol,"n":n,
  "V_set":{str(k):v for k,v in sorted(Vc.items())}},
 io.open(os.path.join(ROOT,"data","74_r28c_vd_pair.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
