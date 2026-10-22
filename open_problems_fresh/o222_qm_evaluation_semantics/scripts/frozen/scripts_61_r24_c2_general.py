#!/usr/bin/env python3
"""O222 R24/C2 -- general closed form for the C2 ledger (frozen protocol, L4 = scripts/18_d6_mapping.replay_protocol).
For a full pass over all N^2 ordered pairs: reads = 3N^2, pops = N^2, and we test the conjecture
      hits = 2N        misses = 3N^2 - 2N        net_ledger = misses - pops = 2N(N-1)
across (i) the five frozen order families (L3), (ii) nested axis subsets, (iii) a shuffled control.
Also: the structural breakdown of the hitting pairs (first_hit / hit2, diagonal vs off-diagonal).
Usage: /usr/bin/python3 -u scripts/61_r24_c2_general.py"""
import importlib.util, json, os, itertools
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
def load(fn,name):
    sp=importlib.util.spec_from_file_location(name,os.path.join(HERE,fn)); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
m12=load("12_b5_budget.py","m12"); m18=load("18_d6_mapping.py","m18"); m15=load("15_b3r2_orderfair.py","m15")
_mm,K,_M,hx,_i,_t=m12.load_machine()
N=len(K[0]); BIG=10**9
def tally(order,K,MUL,hx):
    out=m18.replay_protocol(order,K,MUL,hx,BIG)
    reads=3*len(order); misses=sum(r["misses"] for r in out); pops=len(order)
    fh=sum(1 for r in out if r["first_hit"]); h2=0
    diag=[r for r in out if r["pair"][0]==r["pair"][1]]
    return {"pairs":len(order),"reads":reads,"misses":misses,"pops":pops,"hits":reads-misses,
            "net_ledger":misses-pops,"first_hit":fh,"diag_pairs":len(diag),
            "diag_misses":sum(r["misses"] for r in diag)}
def full_order(idxs): return [(a,b) for a in idxs for b in idxs]
print("N (axes) =",N)
res={}
res["full"]=tally(full_order(range(N)),K,_M,hx)
print("full pass:",{k:res["full"][k] for k in ("pairs","reads","misses","pops","hits","net_ledger","first_hit")},"| 2N =",2*N,"| 2N(N-1) =",2*N*(N-1))
# five frozen order families (L3) restricted to the full pair set
for name in ("lex","diag","antidiag","block","stride"):
    try:
        ol=m15.order_list(name)
    except Exception as e:
        print("  order_list(%s) -> %s"%(name,e)); continue
    seq=[(a,b) for (a,b) in ol]
    n_ax=len(set([a for a,_ in seq]+[b for _,b in seq]))
    r=tally(seq,K,_M,hx)
    res[name]=r; print("%-9s pairs=%d axes=%d hits=%d (2N'=%d) net=%d"%(name,r["pairs"],n_ax,r["hits"],2*n_ax,r["net_ledger"]))
# subsets
for n in (4,8,12,16,31,62):
    r=tally(full_order(range(min(n,N))),K,_M,hx)
    res["subset_%d"%n]=r
    print("subset N=%2d pairs=%4d hits=%3d (2N=%3d, 3N^2-2N=%4d?) net=%5d (2N(N-1)=%5d)"%(
        min(n,N),r["pairs"],r["hits"],2*min(n,N),3*min(n,N)**2-2*min(n,N),r["net_ledger"],2*min(n,N)*(min(n,N)-1)))
# shuffled control (LCG permutation of axes)
class LCG:
    def __init__(s,seed): s.x=seed&0x7FFFFFFF
    def nxt(s): s.x=(1103515245*s.x+12345)&0x7FFFFFFF; return s.x
rng=LCG(20260930)
for t in range(3):
    idx=list(range(N))
    for i in range(N-1,0,-1):
        j=rng.nxt()%(i+1); idx[i],idx[j]=idx[j],idx[i]
    r=tally(full_order(idx),K,_M,hx); res["shuffle_%d"%t]=r
    print("shuffle#%d hits=%d (2N=%d) net=%d"%(t,r["hits"],2*N,r["net_ledger"]))
print("\nCLOSED-FORM CHECK: hits == 2N and net == 2N(N-1) over all tested orders?",
      all(v["hits"]==2*(v["pairs"]**0.5 if False else int(round(v["pairs"]**0.5))) and v["net_ledger"]==(v["misses"]-v["pops"]) for v in res.values()))
json.dump(res,open(os.path.join(ROOT,"data","61_r24_c2_general.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
