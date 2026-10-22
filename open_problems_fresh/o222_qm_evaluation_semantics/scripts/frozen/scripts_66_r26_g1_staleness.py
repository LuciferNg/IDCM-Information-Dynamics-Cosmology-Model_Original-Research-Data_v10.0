#!/usr/bin/env python3
"""O222 R26/G1b -- the formal semantics of the ctx->s override: STALENESS under state evolution.
Claim: in the frozen protocol, every ledger hit compares the stored K[state_at_storage][ctx] with K[current_state][ctx];
       an override occurs exactly when the machine's state has moved on since the value was stored.
Test over all 120 initial states: overrides(s0) == #{ hits where state_now != state_at_store }  (by construction)
       and the structural reduction: overrides(s0) = hits - #{hits whose (state,ctx) pair is a repeat with equal value}.
We also record, per s0: hits, #distinct states visited, #distinct (state,ctx) pairs, #distinct ctx.
Usage: /usr/bin/python3 -u scripts/66_r26_g1_staleness.py"""
import importlib.util, json, os, collections
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("m12b",os.path.join(HERE,"12_b5_budget.py")); m12=importlib.util.module_from_spec(sp); sp.loader.exec_module(m12)
_mm,K,MUL,hx,idx,_t=m12.load_machine()
N=len(K[0]); BUDGET=10**9; COST=F(123,88); EMIN=F(123,176)
order=[(a,b) for a in range(N) for b in range(N)]
def run(s0):
    L=[]; s=s0; rem=BUDGET
    hits=0; ov=0; stale=0; agree_rep=0
    visited=set(); pairs=collections.Counter(); ctxs=set()
    for (a,b) in order:
        spent=0
        for ctx in (a,b):
            visited.add(s); ctxs.add(ctx)
            if L and L[-1][0]==ctx:
                hits+=1
                stored_s=L[-1][2]; stored_v=L[-1][1]
                now=K[s][ctx]
                if s!=stored_s: stale+=1
                if stored_v!=now:
                    ov+=1
                elif s==stored_s:
                    agree_rep+=1
                continue
            v=K[s][ctx]; L.append((ctx,v,s)); s=MUL[s][hx[ctx]]; spent+=1
            visited.add(s); pairs[(s,ctx)]+=1
        _c,_v,s_at=L.pop(); s=s_at
        if L and L[-1][0]==b:
            hits+=1
            stored_s=L[-1][2]; stored_v=L[-1][1]
            if s!=stored_s: stale+=1
            if stored_v!=K[s][b]: ov+=1
            elif s==stored_s: agree_rep+=1
        else:
            v=K[s][b]; L.append((b,v,s)); s=MUL[s][hx[b]]; spent+=1
        rem-=COST*spent
    return hits,ov,stale,agree_rep,len(visited),len(pairs),len(ctxs)
rows=[]
for s0 in range(len(idx)):
    h,ov,st,ag,nv,np_,nc=run(s0)
    rows.append((s0,h,ov,st,ag,nv,np_,nc))
print("s0 : hits overrides stale agree #visited #(s,ctx) #ctx")
for r in rows[:6]: print("  %3d : %4d %4d %4d %4d %4d %4d %3d"%r)
print("...")
print("IDENTITY CHECK  overrides == stale ? ", all(r[2]==r[3] for r in rows))
print("SECOND IDENTITY overrides == hits - agree ? ", all(r[2]==r[1]-r[4] for r in rows))
hs=sorted(set(r[1] for r in rows)); ovs=sorted(set(r[2] for r in rows)); sts=sorted(set(r[3] for r in rows))
print("distinct hits:",hs,"| distinct overrides:",ovs[:6],"..",ovs[-3:],"| distinct stale:",sts[:4],"..",sts[-2:])
print("s0=0 row:",[r for r in rows if r[0]==0])
json.dump({"rows":[list(r) for r in rows],
           "identity_overrides_eq_stale": all(r[2]==r[3] for r in rows),
           "identity_overrides_eq_hits_minus_agree": all(r[2]==r[1]-r[4] for r in rows),
           "override_range":[min(ovs),max(ovs)],"hits_range":[min(hs),max(hs)]},
          open(os.path.join(ROOT,"data","66_r26_g1_staleness.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
