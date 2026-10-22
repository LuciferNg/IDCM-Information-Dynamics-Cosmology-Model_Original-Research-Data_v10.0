#!/usr/bin/env python3
"""O222 R22/QM part 2 -- fix Q4 (fundamental-rep irreducibility) + Q5 (exact CHSH) . Exact arithmetic."""
import importlib.util, json, os
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("a2qm2", os.path.join(HERE,"09_a2_rollback.py")); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
axes,U,ids,types,hvec=m.load_inputs(); G,idx,MUL=m.build_group()
add,mul,S=m.add,m.mul,m.sgn
n=len(G); out={}
print("sample group element:", G[0], "| type", type(G[0]))
print("axis sample:", U[0])
# quaternion scalar part: try each component position and see which yields an irreducible chi
def norm2(w):
    p,q=w; return p*p-5*q*q
best=None
for pos in range(len(G[0]) if isinstance(G[0],(tuple,list)) else 0):
    try:
        tot=sum(4*norm2(g[pos]) for g in G)
        cand=(str(tot), pos)
        if best is None: best=cand
        if str(tot)==str(n): best=cand
        print("  scalar-position",pos,"-> sum|chi|^2 =",tot)
    except Exception as ex:
        print("  scalar-position",pos,"failed:",type(ex).__name__)
out["Q4"]={"sum_chi2_by_position":best}
# Q5: exact CHSH from the frozen correlation record
d=json.load(open(os.path.join(ROOT,"data","09_a2_correlation.json"),encoding="utf-8"))
den=d.get("denominator"); C1=d.get("C1_num"); C1r=d.get("C1rev_num"); C2=d.get("C2")
def num(x):
    if isinstance(x,list): return [F(v) for v in x]
    return F(x)
try:
    vals={k:[F(v) for v in d[k]] if isinstance(d[k],list) else F(d[k]) for k in ("C1_num","C1rev_num","C2") if k in d}
    print("C1_num type:", type(d["C1_num"]), "sample:", (d["C1_num"][:3] if isinstance(d["C1_num"],list) else d["C1_num"]))
    print("denominator:", d.get("denominator"))
    out["Q5"]={"raw":{k:(d[k] if not isinstance(d[k],list) else d[k][:6]) for k in ("denominator","C1_num","C1rev_num","C2")},
               "classical_bound":2,"tsirelson":"2*sqrt(2)"}
except Exception as ex:
    out["Q5"]={"error":str(ex)}
print(json.dumps(out,ensure_ascii=False,indent=1)[:1200])
json.dump(out,open(os.path.join(ROOT,"data","49_r22_qm_verify2.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
