#!/usr/bin/env python3
"""O222 R26/G1 -- formal semantics of the ctx->s override: the override count as a function of the initial state.

Replicates verbatim the authoritative ledger_replay of scripts/30 (G1G8) and scans ALL 120 initial states.
Calibration: the frozen record says s0 = 0 -> overrides 65, and exactly 10 states give 65 (the rest 58).
Then the structural characterisation: which states give 65 (orbit / level / A5-orbit invariants of the machine).
Usage: /usr/bin/python3 -u scripts/65_r26_g1_semantics.py"""
import importlib.util, json, os, collections
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
def load(fn,name):
    sp=importlib.util.spec_from_file_location(name,os.path.join(HERE,fn)); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
m12=load("12_b5_budget.py","m12")
_mm,K,MUL,hx,idx,_t=m12.load_machine()
COST=F(123,88); EMIN=F(123,176); N=len(K[0]); BUDGET=10**9
order=[(a,b) for a in range(N) for b in range(N)]
def ledger_replay(order, s0):
    L=[]; s=s0; rem=BUDGET; out=[]; hits=0; overrides=0; overrides_first=0
    for (a,b) in order:
        spent=0
        for ctx in (a,b):
            if L and L[-1][0]==ctx:
                hits+=1
                if L[-1][1]!=K[s][ctx]:
                    overrides+=1
                    if not out or out[-1]["pair"]!=(a,b): overrides_first+=1
                continue
            if rem-COST*spent<EMIN: raise RuntimeError("terminal")
            v=K[s][ctx]; L.append((ctx,v,s)); s=MUL[s][hx[ctx]]; spent+=1
        _c,_v,s_at=L.pop(); s=s_at
        hit2=bool(L) and L[-1][0]==b
        if hit2:
            v=L[-1][1]
            if v!=K[s][b]: overrides+=1
        else:
            if rem-COST*spent<EMIN: raise RuntimeError("terminal")
            v=K[s][b]; L.append((b,v,s)); s=MUL[s][hx[b]]; spent+=1
        rem-=COST*spent
        out.append({"pair":(a,b),"misses":spent,"top":L[-1][0]})
    return hits, overrides, out
res={}; hist=collections.Counter(); ov_by_state={}
for s0 in range(len(idx)):
    try:
        h,ov,out=ledger_replay(order,s0)
    except RuntimeError:
        h,ov,out=(-1,-1,[])
    ov_by_state[s0]=ov; hist[ov]+=1
    if s0==0: print("CALIBRATION s0=0 : hits=%d overrides=%d (record: [33,32,0,65])"%(h,ov))
print("override histogram over all 120 states:",dict(hist))
g65=[s for s,ov in ov_by_state.items() if ov==max(hist)]
print("states giving max override (%d) = %d states: %s"%(max(hist),len(g65),g65))
# structural characterisation: compare those states' orbits / distances / quaternion norms
def orbit(s0, steps=200):
    x=s0; seen=[]
    for k in range(steps):
        if x in seen: return seen[:seen.index(x)], seen[seen.index(x):]
        seen.append(x); x=MUL[x][hx[k % N]]
    return seen, []
print("--- invariants of the distinguished states ---")
for s0 in g65[:12]:
    pre,cyc=orbit(s0)
    print("  s0=%3d : orbit preperiod %d, cycle len %d"%(s0,len(pre),len(cyc)))
print("--- invariants of a non-distinguished state (s0=1) ---")
pre,cyc=orbit(1); print("  s0=1 : preperiod %d cycle %d"%(len(pre),len(cyc)))
json.dump({"hist":{str(k):v for k,v in hist.items()},"distinguished":g65,"ov_by_state":{str(k):v for k,v in ov_by_state.items()}},
          open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"data","65_r26_g1_semantics.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
