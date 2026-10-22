#!/usr/bin/env python3
"""O222 R24/C2b -- structural decomposition of the C2 ledger hits: are ALL hits the diagonal pairs (a,a), 2 each?
Also the antidiag(123) / block(1954) anomalies: exact hit counts per pair class.
Usage: /usr/bin/python3 -u scripts/62_r24_c2_diag.py"""
import importlib.util, json, os
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
def load(fn,name):
    sp=importlib.util.spec_from_file_location(name,os.path.join(HERE,fn)); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
m12=load("12_b5_budget.py","m12"); m18=load("18_d6_mapping.py","m18"); m15=load("15_b3r2_orderfair.py","m15")
_mm,K,_M,hx,_i,_t=m12.load_machine(); N=len(K[0]); BIG=10**9
def classify(order):
    out=m18.replay_protocol(order,K,_M,hx,BIG)
    diag=off=0; offpairs=[]
    for r in out:
        m=r["misses"]; a,b=r["pair"]; hits=3-m
        if a==b: diag+=hits
        else:
            off+=hits
            if hits: offpairs.append((a,b,m))
    return len(order),diag,off,offpairs[:8]
orders={"full":[(a,b) for a in range(N) for b in range(N)]}
for name in ("lex","diag","antidiag","block","stride"):
    try: orders[name]=list(m15.order_list(name))
    except Exception as e: print("skip",name,e)
res={}
for name,o in orders.items():
    tot,diag,off,ex=classify(o)
    res[name]={"pairs":tot,"diag_hits":diag,"offdiag_hits":off,"diag_pairs":sum(1 for (a,b) in o if a==b),"examples":ex}
    print("%-9s pairs=%d  diag_hits=%d (2*#diag_pairs=%d)  offdiag_hits=%d %s"%(
        name,tot,diag,2*sum(1 for (a,b) in o if a==b),off, ("examples "+str(ex)) if off else ""))
json.dump(res,open(os.path.join(ROOT,"data","62_r24_c2_diag.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
