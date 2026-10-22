#!/usr/bin/env python3
"""O222 R28/B -- RT1 (state side): how many minimal words reach each state? (exact DP over the frozen machine)
The state of the ledger machine after a read word is determined by the word; RT1's state-side uniqueness asks
whether the SHORTEST generating word is unique.  Count, for every state, the number of distinct shortest words.
PRE-REGISTERED: Pr-1 some states have >1 shortest word (so a canonical rule is required);
                Pr-2 the lexicographically-first shortest word is a well-defined canonical form for all 120.
Usage: /usr/bin/python3 -u scripts/73_r28b_rt1_words.py"""
import importlib.util, io, json, os, collections, itertools
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("mX",os.path.join(HERE,"12_b5_budget.py")); mX=importlib.util.module_from_spec(sp); sp.loader.exec_module(mX)
_mm,K,MUL,hx,idx,_t=mX.load_machine()
NR=len(K); NC=len(K[0]); lab=[str(x) for x in (idx if isinstance(idx,list) else range(NC))]

dist={0:0}; cnt={0:1}; canon={0:()}
cur=[0]; d=0
frontier=[0]
while frontier:
    nf=[]
    for s in frontier:
        for c in range(NC):
            t=MUL[s][hx[c]]
            if t in dist: continue
            nf.append(t); dist[t]=d+1; canon[t]=canon[s]+(c,)
    # multiplicity DP at depth d+1
    for s in nf: cnt[s]=0
    for s in frontier:
        for c in range(NC):
            t=MUL[s][hx[c]]
            if dist.get(t)==d+1: cnt[t]=cnt.get(t,0)+cnt[s]
    frontier=nf; d+=1
print("depth reached:",max(dist.values()),"| states:",len(dist))
multi=[(s,dist[s],cnt[s]) for s in sorted(dist,key=lambda s:(dist[s],-cnt[s])) if cnt[s]>1]
print("states with >1 shortest word: %d  (max multiplicity %d)"%(len(multi),max((c for _,_,c in multi),default=1)))
print("first few:",[(s,dist[s],c) for s,dist[s],c in multi[:6]])
deep=[(dist[s],cnt[s]) for s in dist]
print("multiplicity by depth:",sorted(collections.Counter({d:max([c for ss,c in deep if True],default=1) for d in set(x for x,_ in deep)}).items())[:8])
print("Pr-1 (>1 somewhere): %s"%("HOLDS" if multi else "REFUTED"))
print("Pr-2 (canonical lex-first exists for all): %s"%("HOLDS" if len(canon)==NR else "REFUTED"))
json.dump({"states":len(dist),"max_depth":max(dist.values()),"n_multi":len(multi),
  "max_mult":max((c for _,_,c in multi),default=1),"examples":multi[:10]},
 io.open(os.path.join(ROOT,"data","73_r28b_rt1_words.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
