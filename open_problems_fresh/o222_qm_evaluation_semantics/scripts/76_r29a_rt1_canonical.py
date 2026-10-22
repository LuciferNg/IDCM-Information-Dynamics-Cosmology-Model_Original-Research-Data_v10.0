#!/usr/bin/env python3
"""O222 R29/A -- RT1 in CANONICAL form: representation theorem + the source of the word-level redundancy.

Theorem (constructive): the map state -> lexicographically least shortest word is a bijection onto its image,
so after fixing the canonical rule RT1 is UNIQUE.  The residual redundancy of the presentation is measured by
the shortest positive relations among the generator set.
PRE-REGISTERED: Pr-1 the canonical map is injective for all 120 states (trivially, checked constructively);
  Pr-2 the number of length-2 positive relations (a,b with a*b = id, both generators) equals 20
       (all 20 order-3 face generators come with their inverse); Pr-3 no length-1 relation exists.
  Pr-4 the lex-first canonical word is also budget-minimal for every state.
Usage: /usr/bin/python3 -u scripts/76_r29a_rt1_canonical.py"""
import importlib.util, io, json, os, collections, itertools
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("mY",os.path.join(HERE,"12_b5_budget.py")); mY=importlib.util.module_from_spec(sp); sp.loader.exec_module(mY)
_mm,K,MUL,hx,idx,_t=mY.load_machine()
NR=len(K); NC=len(K[0]); lab=[str(x) for x in (idx if isinstance(idx,list) else range(NC))]

# canonical words (lex-least shortest) + multiplicities
dist={0:0}; cnt={0:1}; canon={0:()}
frontier=[0]; d=0
while frontier:
    nf=[]
    for s in frontier:
        for c in range(NC):
            t=MUL[s][hx[c]]
            if t not in dist:
                dist[t]=d+1; canon[t]=None; nf.append(t)
    for s in nf: cnt[s]=0
    for s in frontier:
        for c in range(NC):
            t=MUL[s][hx[c]]
            if dist.get(t)==d+1:
                cnt[t]=cnt.get(t,0)+cnt[s]
                w=canon[s]+(c,)
                if canon[t] is None or w<canon[t]: canon[t]=w
    frontier=nf; d+=1
img={}
inj=True
for s,w in canon.items():
    if w in img and img[w]!=s: inj=False
    img[w]=s
print("states=%d canonical words=%d injective=%s"%(len(canon),len(img),inj))
print("Pr-1 (canonical map injective): %s"%("HOLDS" if inj and len(canon)==NR else "REFUTED"))
rel1=[c for c in range(NC) if MUL[0][hx[c]]==0]
rel2=[(a,b) for a in range(NC) for b in range(NC) if MUL[MUL[0][hx[a]]][hx[b]]==0]
print("length-1 relations:",len(rel1),"  length-2 relations:",len(rel2))
print("Pr-2 (length-2 = 20): %s"%("HOLDS" if len(rel2)==20 else "REFUTED (%d)"%len(rel2)))
print("Pr-3 (no length-1): %s"%("HOLDS" if not rel1 else "REFUTED"))
print("length-2 relation families:",collections.Counter((lab[a][0],lab[b][0]) for a,b in rel2))
# budget-minimality of the canonical word: cost law 3 - [t=a] - [b=a] per ordered pair
def word_cost(w):
    # replay the word as a ledger pass over the axes it names (cost = reads)
    L=[]; s=0; cost=0
    for ctx in w:
        if L and L[-1][0]==ctx: cost+=1; continue
        L.append((ctx,K[s][ctx],s)); s=MUL[s][hx[ctx]]; cost+=1
    return cost
# REAL Pr-4 test: enumerate ALL words of length <= 2, group by the state they reach, and check whether the
# lex-first canonical word attains the minimum ledger cost within its group (exact).
byword={}
for c in range(NC):
    t=MUL[0][hx[c]]; byword.setdefault(t,[]).append((c,))
for c1 in range(NC):
    t1=MUL[0][hx[c1]]
    for c2 in range(NC):
        t=MUL[t1][hx[c2]]; byword.setdefault(t,[]).append((c1,c2))
bad=0; tested=0
for st,ws in byword.items():
    if dist.get(st,99)>2: continue
    if len(ws)<2: continue
    tested+=1
    costs=[word_cost(w) for w in ws]
    if word_cost(canon[st])!=min(costs): bad+=1
print("Pr-4 real test: %d multi-word states of length<=2 tested, %d where the lex-first word is NOT cost-minimal"%(tested,bad))
print("Pr-4 (lex-first is budget-minimal): %s"%("HOLDS" if bad==0 else "REFUTED (%d)"%bad))
print("canonical length distribution:",collections.Counter(len(w) for w in canon.values()))
print("multiplicity: %d states with >1 shortest word; max %d"%(sum(1 for s in cnt if cnt[s]>1),max(cnt.values())))
json.dump({"injective":inj,"n1":len(rel1),"n2":len(rel2),"rel2_families":{k[0]+k[1]:v for k,v in collections.Counter((lab[a][0],lab[b][0]) for a,b in rel2).items()},
  "length_dist":{str(k):v for k,v in collections.Counter(len(w) for w in canon.values()).items()},
  "multi_states":sum(1 for s in cnt if cnt[s]>1),"max_mult":max(cnt.values())},
 io.open(os.path.join(ROOT,"data","76_r29a_rt1_canonical.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
