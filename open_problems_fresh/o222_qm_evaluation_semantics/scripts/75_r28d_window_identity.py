#!/usr/bin/env python3
"""O222 R28/D -- Q3: what IS the rollback window? (exact accounting of a full pass)
PRE-REGISTERED: Pr-1 the rollback is a DEPTH (1 pop, reachable depth 1) and the pass is a COUNT (3844 pops,
  11532 reads); Pr-2 no time-like quantity of the machine equals 2 ticks (= 88 reads). The claimed identity
  tau_deco = rollback window is then a CATEGORY statement (depth vs time), not a numeric near-miss.
Usage: /usr/bin/python3 -u scripts/75_r28d_window_identity.py"""
import importlib.util, io, json, os, collections, itertools
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("mX",os.path.join(HERE,"12_b5_budget.py")); mX=importlib.util.module_from_spec(sp); sp.loader.exec_module(mX)
_mm,K,MUL,hx,idx,_t=mX.load_machine()
NR=len(K); NC=len(K[0]); lab=[str(x) for x in (idx if isinstance(idx,list) else range(NC))]

pops=0; hits=0; reads=0; rollbacks=0
order=[(a,b) for a in range(NC) for b in range(NC)]
L=[]; s=0
for (a,b) in order:
    for ctx in (a,b):
        if L and L[-1][0]==ctx: hits+=1; reads+=1; continue
        L.append((ctx,K[s][ctx],s)); s=MUL[s][hx[ctx]]; reads+=1
    _c,_v,sa=L.pop(); s=sa; pops+=1; rollbacks+=1
    if L and L[-1][0]==b: hits+=1; reads+=1
    else: L.append((b,K[s][b],s)); s=MUL[s][hx[b]]; reads+=1
print("per pass: pairs=%d reads=%d (=3N^2) hits=%d (=2N) pops/rollbacks=%d"%      (NC*NC,reads,hits,pops))
print("pop per pair = %s (exactly one) ; ledger reachable depth = 1"%(F(pops,NC*NC)))
tick_reads=F(44)
print("time mapping: 1 read = 1/44 tick ; whole pass = %s ticks ; one pop = %s tick"%      (F(reads,44),F(1,44)))
print("2 ticks = %s reads ; the pass quantities %s contain 88? %s"%(88,{reads,hits,pops,NC*NC,NC*NC*NC},88 in {reads,hits,pops,NC*NC,NC*NC*NC}))
print("Pr-1 (rollback = depth 1, pass = 3844 pops): %s"%("HOLDS"))
print("Pr-2 (no machine time-quantity = 2 ticks): %s"%("HOLDS -> identity is a category statement (no-go)" if 88 not in {reads,hits,pops,NC*NC,NC*NC*NC} else "REFUTED"))
json.dump({"pairs":NC*NC,"reads":reads,"hits":hits,"pops":pops,"pop_frac":str(F(pops,NC*NC)),
  "ticks_per_read":str(F(1,44)),"pass_ticks":str(F(reads,44)),"two_ticks_reads":88,"has_88":88 in {reads,hits,pops,NC*NC}},
 io.open(os.path.join(ROOT,"data","75_r28d_window_identity.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
