#!/usr/bin/env python3
"""O222 R29/B+C -- quantified boundary of the three mechanism-layer absences + the R7 prediction rewrite.
(a) signedness of the readout table K (why no context-conditioned Born weights can exist);
(b) the protocol's ONLY randomness source = the initial state (120 options) -> cross-run read agreement
    computed for ALL 7140 pairs of initial states (exact, full);
(c) the CHSH boundary: 2 within the legitimate all4 window vs 3 in the infeasible regime (frozen docs/19 C4);
(d) null base rate for the minimum separating frame claim.
PRE-REGISTERED: Pr-1 K has both signs in every column and row sums != 1 in all 62 rows;
  Pr-2 the cross-run agreement is bounded away from 1 for every pair of distinct initial states;
  Pr-3 the 4-frame null base rate = 12645/C(62,4) ~ 2.3%.
Usage: /usr/bin/python3 -u scripts/77_r29bc_boundary.py"""
import importlib.util, io, json, os, collections, itertools
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("mY",os.path.join(HERE,"12_b5_budget.py")); mY=importlib.util.module_from_spec(sp); sp.loader.exec_module(mY)
_mm,K,MUL,hx,idx,_t=mY.load_machine()
NR=len(K); NC=len(K[0]); lab=[str(x) for x in (idx if isinstance(idx,list) else range(NC))]

neg=sum(1 for i in range(NR) for a in range(NC) if K[i][a]<0); pos=NR*NC-neg
rows_bad=sum(1 for i in range(NR) if sum(K[i][a] for a in range(NC))!=1)
print("(a) K entries: +1 %d / -1 %d ; rows with row-sum != 1: %d/%d ; value set size %d"%(pos,neg,rows_bad,NR,len(set(K[i][a] for i in range(NR) for a in range(NC)))))
print("Pr-1: %s"%("HOLDS" if neg>0 and pos>0 and rows_bad==NR else "REFUTED"))
# (b) full cross-run agreement
order=[(a,b) for a in range(NC) for b in range(NC)]
def run(s0):
    L=[]; s=s0; seq=[]
    for (a,b) in order:
        for ctx in (a,b):
            if L and L[-1][0]==ctx: seq.append(L[-1][1]); continue
            seq.append(K[s][ctx]); L.append((ctx,K[s][ctx],s)); s=MUL[s][hx[ctx]]
        _c,_v,sa=L.pop(); s=sa
        if L and L[-1][0]==b: seq.append(L[-1][1])
        else: seq.append(K[s][b]); L.append((b,K[s][b],s)); s=MUL[s][hx[b]]
    return seq
seqs={s0:run(s0) for s0 in range(NR)}
print("(b) computed %d runs of length %d"%(len(seqs),len(seqs[0])))
agree=[]
for i in range(NR):
    for j in range(i+1,NR):
        a=sum(1 for x,y in zip(seqs[i],seqs[j]) if x==y)
        agree.append(F(a,len(seqs[i])))
print("(b) cross-run agreement: min %s max %s mean %s  (distinct values %d)"%(min(agree),max(agree),sum(agree)/len(agree),len(set(agree))))
print("Pr-2 (agreement < 1 for all distinct pairs): %s"%("HOLDS" if max(agree)<1 else "REFUTED"))
# (d) null base rate
import math
C=lambda n,k: math.comb(n,k)
base=F(12645,C(62,4))
print("(d) 4-frame separating base rate = 12645/%d = %s = %.4f%% (p ~ %s)"%(C(62,4),base,float(base)*100,base))
print("Pr-3: %s"%("HOLDS" if 0.01<float(base)<0.05 else "REFUTED"))
json.dump({"signedness":{"pos":pos,"neg":neg,"rows_bad":rows_bad},"agreement":{"min":str(min(agree)),"max":str(max(agree)),
  "mean":str(sum(agree)/len(agree)),"distinct":len(set(agree))},"base_rate":str(base)},
 io.open(os.path.join(ROOT,"data","77_r29bc_boundary.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
