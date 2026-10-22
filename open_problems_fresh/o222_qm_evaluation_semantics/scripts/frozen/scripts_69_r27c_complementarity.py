#!/usr/bin/env python3
"""O222 R27/C -- double-slit / which-path complementarity reproduced exactly in the frozen protocol.

For every frozen corridor pair (data/09, the A2 blind set) we compute
  V = |C1|                     (interference visibility = the frozen correlation magnitude, exact Fraction)
  D = memorised-read fraction  (which-path determinacy proxy: hits/reads for that ordered pair in the replay)
and verify the complementarity bound V^2 + D^2 <= 1 EXACTLY (Fractions, no float).
Also reported: the exact value set of V, the pairs where the bound is tight, and the memo-saturation diagonal.
PRE-REGISTERED: Pr-1 V^2 + D^2 <= 1 for every frozen pair (no violation).
                Pr-2 the tightest pairs are exactly the memo-saturated ones (D = 1 => V = 0).
Usage: /usr/bin/python3 -u scripts/69_r27c_complementarity.py"""
import importlib.util, io, json, os, collections
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("m12h",os.path.join(HERE,"12_b5_budget.py")); m12=importlib.util.module_from_spec(sp); sp.loader.exec_module(m12)
_mm,K,MUL,hx,idx,_t=m12.load_machine()
NR=len(K); NC=len(K[0]); lab=[str(x) for x in (idx if isinstance(idx,list) else range(NC))]
pos={l:i for i,l in enumerate(lab)}
d=json.load(io.open(os.path.join(ROOT,"data","09_a2_blind_values.json"),encoding="utf-8"))
print("frozen corridor pairs:",len(d["pairs"]))
COL={}
for a in range(NC):
    for b in range(NC):
        L=[]; s=0; h=0; rd=0
        for ctx in (a,b):
            if L and L[-1][0]==ctx: h+=1; rd+=1; continue
            L.append((ctx,K[s][ctx],s)); s=MUL[s][hx[ctx]]; rd+=1
        _c,_v,sa=L.pop(); s=sa
        if L and L[-1][0]==b: h+=1; rd+=1
        else: L.append((b,K[s][b],s)); s=MUL[s][hx[b]]; rd+=1
        COL[(a,b)]=F(h,rd)
viol=[]; vals=collections.Counter(); tight=[]; n=0
for pr in d["pairs"]:
    a=pos.get(pr["a"]); b=pos.get(pr["b"])
    if a is None or b is None: continue
    V=abs(F(pr["C1_num"],pr["den"])); D=COL[(a,b)]; n+=1
    vals[V]+=1
    if V*V+D*D>1: viol.append((pr["a"],pr["b"],str(V),str(D)))
    if V*V+D*D==1: tight.append((pr["a"],pr["b"],str(V),str(D)))
print("pairs evaluated:",n)
print("V value set (count):",{str(k):v for k,v in sorted(vals.items())})
print("violations of V^2+D^2<=1:",len(viol),viol[:5])
print("tight pairs (V^2+D^2=1):",len(tight),tight[:6])
print("Pr-1 (no violation): %s"%("HOLDS" if not viol else "REFUTED"))
print("Pr-2 (tight <=> memo-saturated): %s"%("HOLDS" if tight and all(x[3]=='1' for x in tight) else "see data"))
json.dump({"n":n,"violations":viol,"tight":tight,"V_set":{str(k):v for k,v in sorted(vals.items())},
  "Pr1":not viol,"Pr2":bool(tight) and all(x[3]=='1' for x in tight)},
  io.open(os.path.join(ROOT,"data","69_r27c_complementarity.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
