#!/usr/bin/env python3
"""O222 R23/U2 seal -- two independent seals of the frozen-Gram canonical construction:
 (b) reproduction in Gram form:  sgn( G_frozen . Kc^T )  ==  Kc      (zero-parameter; exact Q(sqrt5))
 (c) representative-independence: use ALL 120 rows (full Gram G120 over the 120 frozen readout vectors) and compare
     sgn(K^T G120 K) with the certified vsign (62x62).
Usage: /usr/bin/python3 -u scripts/57_r23_u2_seal.py
"""
import importlib.util, json, os
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
sp=importlib.util.spec_from_file_location("a2u2s", os.path.join(HERE,"09_a2_rollback.py")); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
axes,Uax,ids,types,hvec=m.load_inputs(); G,idx,MUL=m.build_group()
add,mul,S=m.add,m.mul,m.sgn
dot3=lambda a,b: add(add(mul(a[0],b[0]),mul(a[1],b[1])),mul(a[2],b[2]))
R=[m.rot_ref(q,Uax[0]) for q in G]
sp2=importlib.util.spec_from_file_location("b5u2s", os.path.join(HERE,"12_b5_budget.py")); m2=importlib.util.module_from_spec(sp2); sp2.loader.exec_module(m2)
_mm,K,_M,_h,_i,_t=m2.load_machine()
patt={}
for i in range(len(K)): patt.setdefault(tuple(K[i]), i)
rep=sorted(patt.values()); n=12; N=len(K[0]); zero=(0,0)
Gr=[[dot3(R[rep[i]],R[rep[j]]) for j in range(n)] for i in range(n)]
Kc=[[K[i][j] for j in range(len(K[0]))] for i in rep]
def qform(Km, Gm, nrows):
    """sgn of the quadratic form  Km^T G Km  (N x N)  in exact Q(sqrt5)."""
    out=[[None]*N for _ in range(N)]
    for a in range(N):
        for b in range(N):
            acc=zero
            for i in range(nrows):
                ka=Km[i][a]
                if ka==0: continue
                for i2 in range(nrows):
                    kb=Km[i2][b]
                    if kb==0: continue
                    acc=add(acc,Gm[i][i2]) if ka*kb==1 else add(acc,mul(Gm[i][i2],(-1,0)))
            out[a][b]=S(acc)
    return out
# (b) reproduction: sgn(G . Kc^T)[i][j] vs Kc[i][j]
repro=0
for i in range(n):
    for j in range(N):
        acc=zero
        for i2 in range(n):
            kk=Kc[i2][j]
            if kk==0: continue
            acc=add(acc,Gr[i][i2]) if kk==1 else add(acc,mul(Gr[i][i2],(-1,0)))
        if S(acc)!=Kc[i][j]: repro+=1
print("(b) reproduction  sgn(G_frozen . Kc^T) == Kc : mismatches %d/%d"%(repro,n*N))
# (c) all-120 version
G120=[[dot3(R[i],R[j]) for j in range(len(R))] for i in range(len(R))]
Qn=qform(K,G120,len(R))
J=json.load(open(os.path.join(ROOT,"data","40_candidates.json"),encoding="utf-8")); cand=J.get("candidates",J)
c3=[c for c in cand if len(c["U"][0])==3][0]; V=c3["V"]
sg=lambda x: 1 if x>0 else (-1 if x<0 else 0)
vsign=[[sg(sum(V[a][k]*V[b][k] for k in range(3))) for b in range(N)] for a in range(N)]
bad120=sum(1 for a in range(N) for b in range(N) if Qn[a][b]!=vsign[a][b])
print("(c) all-120 rows: sgn(K^T G120 K) vs certified vsign : mismatches %d/%d"%(bad120,N*N))
out={"reproduction_mismatches":repro,"reproduction_total":n*N,"all120_mismatches":bad120,"all120_total":N*N,
     "verdict": ("canonical construction confirmed (frozen Gram): V-side determined; rank-3 = rank of the frozen Gram"
                 if (repro==0 and bad120==0) else "partial")}
print(json.dumps(out,ensure_ascii=False,indent=1))
json.dump(out,open(os.path.join(ROOT,"data","57_r23_u2_seal.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
