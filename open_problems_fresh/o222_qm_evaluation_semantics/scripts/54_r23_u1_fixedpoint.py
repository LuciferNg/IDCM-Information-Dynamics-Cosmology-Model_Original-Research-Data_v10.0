#!/usr/bin/env python3
"""O222 R23/U1b -- the sharp criterion: does the self-dual FIXED-POINT condition
      sgn(Uc V^T) = Kc    with    V := Kc^T Uc
pin down vsign?  We perturb U by a random invertible 3x3 integer T (U' = U T, the exact GL(3) freedom),
recompute V' = Kc^T U' , and record (i) fixed-point violations vs (ii) vsign disagreement with the certified one.
Usage: /usr/bin/python3 -u scripts/54_r23_u1_fixedpoint.py
"""
import importlib.util, json, os, random
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("b5u1b", os.path.join(HERE,"12_b5_budget.py")); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
_mm,K,_M,_h,_i,_t=m.load_machine()
J=json.load(open(os.path.join(ROOT,"data","40_candidates.json"),encoding="utf-8")); cand=J.get("candidates",J)
c3=[c for c in cand if len(c["U"][0])==3][0]; U=c3["U"]; V=c3["V"]
patt={}
for i in range(len(K)): patt.setdefault(tuple(K[i]), i)
rep=sorted(patt.values()); Kc=[[K[i][j] for j in range(len(K[0]))] for i in rep]; Uc=[U[i] for i in rep]
N=len(K[0]); n=12
sg=lambda x: 1 if x>0 else (-1 if x<0 else 0)
vs_cert=[[sg(sum(V[a][k]*V[b][k] for k in range(3))) for b in range(N)] for a in range(N)]
def det3(T):
    return (T[0][0]*(T[1][1]*T[2][2]-T[1][2]*T[2][1])-T[0][1]*(T[1][0]*T[2][2]-T[1][2]*T[2][0])+T[0][2]*(T[1][0]*T[2][1]-T[1][1]*T[2][0]))
def analyze(T, label):
    Uc2=[[sum(Uc[i][k]*T[k][l] for k in range(3)) for l in range(3)] for i in range(n)]
    VM2=[[sum(Kc[i][j]*Uc2[i][k] for i in range(n)) for k in range(3)] for j in range(N)]
    fp=sum(1 for i in range(n) for j in range(N) if sg(sum(Uc2[i][k]*VM2[j][k] for k in range(3)))!=Kc[i][j])
    vs2=[[sg(sum(VM2[a][k]*VM2[b][k] for k in range(3))) for b in range(N)] for a in range(N)]
    vb=sum(1 for a in range(N) for b in range(N) if vs2[a][b]!=vs_cert[a][b])
    return fp, vb
rows=[]
for lab,T in [("identity",[[1,0,0],[0,1,0],[0,0,1]]),
              ("diag(2,1,1)",[[2,0,0],[0,1,0],[0,0,1]]),
              ("diag(3,5,7)",[[3,0,0],[0,5,0],[0,0,7]]),
              ("shear",[[1,1,0],[0,1,0],[0,0,1]]),
              ("rot-ish",[[2,-1,0],[1,2,0],[0,0,1]])]:
    if det3(T)==0: continue
    fp,vb=analyze(T,lab); rows.append((lab,fp,vb)); print("%-12s det=%4d | fixed-point violations=%4d | vsign mismatches=%4d"%(lab,det3(T),fp,vb))
random.seed(7)
for t in range(15):
    while True:
        T=[[random.randint(-3,3) for _ in range(3)] for _ in range(3)]
        if det3(T)!=0: break
    fp,vb=analyze(T,"rand#%d"%t); rows.append(("rand#%d"%t,fp,vb))
agree_fp = [(l,fp,vb) for l,fp,vb in rows if fp==0]
print("\nSUMMARY: draws with fixed point SATISFIED: %d/%d ; among those, vsign mismatches are all 0? %s"%(len(agree_fp),len(rows), all(vb==0 for _,fp,vb in agree_fp)))
print("draws with fixed point VIOLATED: %d ; their vsign mismatches: %s"%(len(rows)-len(agree_fp),[vb for _,fp,vb in rows if fp>0]))
out={"rows":[{"transform":l,"fp_violations":fp,"vsign_mismatches":vb} for l,fp,vb in rows],
     "fp_satisfied_count":len(agree_fp),"total":len(rows),
     "sharp_criterion_holds":all(vb==0 for _,fp,vb in agree_fp)}
print(json.dumps(out,ensure_ascii=False,indent=1)[:900])
json.dump(out,open(os.path.join(ROOT,"data","54_r23_u1_fixedpoint.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
