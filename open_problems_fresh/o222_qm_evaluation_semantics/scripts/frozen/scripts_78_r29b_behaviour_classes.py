#!/usr/bin/env python3
"""O222 R29/B2 -- how many DISTINCT behaviours do the 120 initial states produce? (exact, full)
Randomness-source quantification for the redundancy boundary.
PRE-REGISTERED: Pr-1 the number of distinct read sequences is strictly less than 120 (collisions exist).
Usage: /usr/bin/python3 -u scripts/78_r29b_behaviour_classes.py"""
import importlib.util, io, json, os, collections
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("mZ",os.path.join(HERE,"12_b5_budget.py")); mZ=importlib.util.module_from_spec(sp); sp.loader.exec_module(mZ)
_mm,K,MUL,hx,idx,_t=mZ.load_machine()
NR=len(K); NC=len(K[0])
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
    return tuple(seq)
seqs={s0:run(s0) for s0 in range(NR)}
classes=collections.defaultdict(list)
for s0,q in seqs.items(): classes[q].append(s0)
sizes=sorted(len(v) for v in classes.values())
print("initial states: %d ; distinct read behaviours: %d ; class sizes %s"%(NR,len(classes),sizes))
print("Pr-1 (distinct < 120): %s"%("HOLDS" if len(classes)<NR else "REFUTED"))
print("log2(#behaviours) = %.4f bits (the protocol's effective randomness source)"%(__import__("math").log2(len(classes))))
json.dump({"distinct":len(classes),"class_sizes":sizes,"log2_bits":__import__("math").log2(len(classes))},
 io.open(os.path.join(ROOT,"data","78_r29b_behaviour_classes.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
