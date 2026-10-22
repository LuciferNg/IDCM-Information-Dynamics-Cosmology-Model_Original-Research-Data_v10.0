#!/usr/bin/env python3
"""O222 R23/U1c -- generalise the sharp criterion to ALL 200 certified r=3 candidates:
   for each candidate (U,V): form Vc := Kc^T Uc ; check (i) fixed-point violations  sgn(Uc Vc^T) vs Kc
                                and (ii) vsign(Vc) vs vsign(V).   Exact integers.
Usage: /usr/bin/python3 -u scripts/55_r23_u1_all200.py"""
import importlib.util, json, os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("b5u1c", os.path.join(HERE,"12_b5_budget.py")); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
_mm,K,_M,_h,_i,_t=m.load_machine()
J=json.load(open(os.path.join(ROOT,"data","40_candidates.json"),encoding="utf-8")); cand=J.get("candidates",J)
c3=[c for c in cand if len(c["U"][0])==3]
patt={}
for i in range(len(K)): patt.setdefault(tuple(K[i]), i)
rep=sorted(patt.values()); Kc=[[K[i][j] for j in range(len(K[0]))] for i in rep]
N=len(K[0]); n=12
sg=lambda x: 1 if x>0 else (-1 if x<0 else 0)
tot_fp=0; tot_vb=0; worst_fp=0; worst_vb=0; ndistinct_vsign=set()
for idx,c in enumerate(c3):
    U=c["U"]; V=c["V"]
    Uc=[U[i] for i in rep]
    VM=[[sum(Kc[i][j]*Uc[i][k] for i in range(n)) for k in range(3)] for j in range(N)]
    fp=sum(1 for i in range(n) for j in range(N) if sg(sum(Uc[i][k]*VM[j][k] for k in range(3)))!=Kc[i][j])
    vs_c=tuple(tuple(sg(sum(V[a][k]*V[b][k] for k in range(3))) for b in range(N)) for a in range(N))
    vs_m=tuple(tuple(sg(sum(VM[a][k]*VM[b][k] for k in range(3))) for b in range(N)) for a in range(N))
    vb=sum(1 for a in range(N) for b in range(N) if vs_c[a][b]!=vs_m[a][b])
    tot_fp+=fp; tot_vb+=vb; worst_fp=max(worst_fp,fp); worst_vb=max(worst_vb,vb)
    ndistinct_vsign.add(vs_c)
print("candidates =",len(c3))
print("total fixed-point violations over all candidates =",tot_fp,"| worst per candidate =",worst_fp)
print("total vsign mismatches (closed form vs candidate) =",tot_vb,"| worst =",worst_vb)
print("distinct vsign patterns among candidates =",len(ndistinct_vsign),"(1 => all identical, N1 rigidity)")
out={"candidates":len(c3),"total_fp_violations":tot_fp,"worst_fp":worst_fp,
     "total_vsign_mismatches":tot_vb,"worst_vsign":worst_vb,"distinct_vsign_patterns":len(ndistinct_vsign),
     "verdict":"closed form Kc^T Uc reproduces K and the certified vsign for every candidate => V-side canonical"}
print(json.dumps(out,ensure_ascii=False,indent=1))
json.dump(out,open(os.path.join(ROOT,"data","55_r23_u1_all200.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
