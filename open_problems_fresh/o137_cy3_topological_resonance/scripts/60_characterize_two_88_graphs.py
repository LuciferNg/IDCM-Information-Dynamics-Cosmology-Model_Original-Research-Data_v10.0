#!/usr/bin/env python3
"""
O137 — Round 13b (scripts/60)
=============================
★ 發現 (scripts/59): 存在【第二個】4-正則 Cayley 圖 of A₅, MILP 精確 MaxCut = 88,
   但 ≇ RH。⟹ 88 (甚至 + 連通 + 頂點傳遞 + 20 三角形) 都【唔】強制 RH 網。

本輪: 表徵 5 個 4-正則 Cayley 圖 of A₅, 找出【真正】之判別輸入。
"""
import numpy as np, math, itertools
from collections import Counter
import networkx as nx
from scipy.optimize import milp, LinearConstraint, Bounds

PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    if isinstance(exp,(int,float)) and not isinstance(exp,bool):
        ok=abs(float(got)-float(exp))<=tol
    else: ok=(got==exp)
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

BASE="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/"
D=BASE+"o137_cy3_topological_resonance/data/"
RH=np.load(D+"rhombicosidodecahedron_unit.npy")
def adj_from_vecs(V,th=28.0):
    C=np.clip(V@V.T,-1,1); A=(np.degrees(np.arccos(C))<th).astype(int)
    np.fill_diagonal(A,0); return A
A_RH=adj_from_vecs(RH); G_RH=nx.from_numpy_array(A_RH)

def parity(p):
    seen=[False]*5; par=1
    for i in range(5):
        if not seen[i]:
            j=i; c=0
            while not seen[j]: seen[j]=True; j=p[j]; c+=1
            if c%2==0: par=-par
    return par
A5=[p for p in itertools.permutations(range(5)) if parity(p)==1]
idx={p:i for i,p in enumerate(A5)}
def mul(p,q): return tuple(p[q[i]] for i in range(5))
def inv(p):
    r=[0]*5
    for i,v in enumerate(p): r[v]=i
    return tuple(r)
def order(p):
    e=tuple(range(5)); q=p; k=1
    while q!=e: q=mul(q,p); k+=1
    return k
def subgroup_order(gens):
    e=tuple(range(5)); seen={e}; fr=[e]
    while fr:
        new=[]
        for g in fr:
            for s in gens:
                q=mul(g,s)
                if q not in seen: seen.add(q); new.append(q)
        fr=new
    return len(seen)
noninv=[p for p in A5 if order(p)>2]
graphs={}
for i in range(len(noninv)):
    for j in range(i+1,len(noninv)):
        a,b=noninv[i],noninv[j]
        if b in (a,inv(a)): continue
        if subgroup_order([a,b])!=60: continue
        S=[a,inv(a),b,inv(b)]
        if len(set(S))<4: continue
        A=np.zeros((60,60),dtype=int)
        for k,p in enumerate(A5):
            for s in S: A[k,idx[mul(p,s)]]=1
        A=((A+A.T)>0).astype(int); np.fill_diagonal(A,0)
        if A.sum()!=240: continue
        key=tuple(np.round(np.sort(np.linalg.eigvalsh(A.astype(float))),5))
        graphs.setdefault(key,(A,a,b))
print(f"  重建 5 個非同構 4-正則 Cayley 圖 of A₅: {len(graphs)}")

def maxcut_lb(Adj,restarts=40,seed=0):
    rng=np.random.default_rng(seed); n=Adj.shape[0]; E=Adj.sum()/2; best=-1.0
    for _ in range(restarts):
        s=rng.choice([-1.0,1.0],size=n); As=Adj@s
        for _ in range(4*n):
            delta=s*As; i=int(np.argmax(delta))
            if delta[i]<=1e-12: break
            old=s[i]; s[i]=-s[i]; As=As-2*old*Adj[:,i]
        best=max(best,(E-float(s@As)/2)/2)
    return best
def exact_maxcut(edges,n,time_limit=200):
    m=len(edges); N=n+m; c=np.zeros(N); c[n:]=-1.0
    rows=[];lb=[];ub=[]
    for k,(u,v) in enumerate(edges):
        r=np.zeros(N); r[u]=1; r[v]=1; r[n+k]=-1; rows.append(r); lb.append(0); ub.append(np.inf)
        r2=np.zeros(N); r2[u]=-1; r2[v]=-1; r2[n+k]=-1; rows.append(r2); lb.append(-2); ub.append(0)
    res=milp(c=c,constraints=LinearConstraint(np.array(rows),lb,ub),integrality=np.ones(N),
             bounds=Bounds([0]*n+[0]*m,[1]*n+[1]*m),options={"time_limit":time_limit,"presolve":True})
    return -res.fun if res.fun is not None else None
def edges_of(A):
    n=A.shape[0]; return [(i,j) for i in range(n) for j in range(i+1,n) if A[i,j]]

def tri_list(A):
    n=A.shape[0]; T=[]
    for i in range(n):
        for j in range(i+1,n):
            if A[i,j]:
                for k in range(j+1,n):
                    if A[i,k] and A[j,k]: T.append((i,j,k))
    return T
def cycles5_list(A):
    n=A.shape[0]; nb=[np.nonzero(A[i])[0].tolist() for i in range(n)]
    out=set()
    for v0 in range(n):
        for v1 in nb[v0]:
            for v2 in nb[v1]:
                if v2 in (v0,v1): continue
                for v3 in nb[v2]:
                    if v3 in (v0,v1,v2): continue
                    for v4 in nb[v3]:
                        if v4 in (v0,v1,v2,v3): continue
                        if A[v4,v0]: out.add(frozenset((v0,v1,v2,v3,v4)))
    return [sorted(c) for c in out]
def greedy_pack(cycles,used):
    out=[]
    for c in sorted(cycles,key=len):
        es=[tuple(sorted((c[k],c[(k+1)%len(c)]))) for k in range(len(c))]
        if any(e in used for e in es): continue
        for e in es: used.add(e)
        out.append(tuple(c))
    return out

print("\n"+"="*88); print("§1 ★ 5 個 4-正則 Cayley 圖 of A₅ 之完整表徵"); print("="*88)
recs=[]
for key,(A,a,b) in graphs.items():
    G=nx.from_numpy_array(A)
    lb=maxcut_lb(A.astype(float),40,seed=1)
    ex=exact_maxcut(edges_of(A),60,time_limit=200) if lb<=92 else None
    mc=ex if ex is not None else lb
    T=tri_list(A); used=set(); packT=greedy_pack(T,used)
    C5=cycles5_list(A); packP=greedy_pack(C5,used)
    is_p,emb=nx.check_planarity(G)
    faces=None
    if is_p:
        fs=set()
        for u,v in G.edges():
            fs.add(frozenset(emb.traverse_face(u,v))); fs.add(frozenset(emb.traverse_face(v,u)))
        faces=dict(sorted(Counter(len(f) for f in fs).items()))
    iso=nx.is_isomorphic(G,G_RH)
    aut=0
    for _ in nx.algorithms.isomorphism.GraphMatcher(G,G).isomorphisms_iter():
        aut+=1
        if aut>5000: break
    recs.append(dict(A=A,orders=(order(a),order(b)),mc=mc,lb=lb,ntri=len(T),
                     packT=len(packT),nc5=len(C5),packP=len(packP),
                     planar=is_p,faces=faces,iso=iso,aut=aut,
                     cov=len(used),E=int(A.sum()/2)))
recs.sort(key=lambda r:r['mc'])
print(f"  {'#':>2} {'階(a,b)':>8} {'MaxCut':>7} {'#△':>4} {'△裝填':>6} {'#C₅':>5} {'C₅裝填':>7} {'覆蓋':>5} {'平面':>5} {'Aut':>6}  ≅RH")
for i,r in enumerate(recs):
    print(f"  {i:>2} {str(r['orders']):>8} {r['mc']:>7.1f} {r['ntri']:>4} {r['packT']:>6} "
          f"{r['nc5']:>5} {r['packP']:>7} {r['cov']:>5} {str(r['planar']):>5} {r['aut']:>6}  {r['iso']}")

print("\n"+"="*88); print("§2 ★★ 兩個 MaxCut = 88 之圖逐項對比"); print("="*88)
two=[r for r in recs if abs(r['mc']-88)<1e-9]
for r in two:
    print(f"\n  ── 階(a,b) = {r['orders']},  ≅RH = {r['iso']} ──")
    print(f"     MaxCut(MILP 精確) = {r['mc']:.1f};  E = {r['E']}")
    print(f"     #△ = {r['ntri']} (邊不相交裝填 = {r['packT']});  #C₅ = {r['nc5']} (裝填 = {r['packP']})")
    print(f"     △+C₅ 覆蓋邊數 = {r['cov']} / {r['E']}")
    print(f"     平面 = {r['planar']};  面型 = {r['faces']}")
    print(f"     Aut 群階 = {r['aut']}")
ck("★ 恰 2 個 4-正則 Cayley 圖 of A₅ with MaxCut = 88", len(two), 2)
ck("★ 其中只有 1 個 ≅ RH", sum(1 for r in two if r['iso']), 1)
rh=[r for r in recs if r['iso']][0]; nonrh=[r for r in two if not r['iso']][0]
print(f"\n  ★★ 判別輸入:")
print(f"     平面性:      RH = {rh['planar']},   非RH = {nonrh['planar']}")
print(f"     面結構:      RH = {rh['faces']}")
print(f"                  非RH = {nonrh['faces']}")
print(f"     Aut 群階:    RH = {rh['aut']},   非RH = {nonrh['aut']}")
print(f"     △+C₅ 覆蓋:   RH = {rh['cov']},   非RH = {nonrh['cov']}  (E = 120)")
ck("★★ 平面性判別: RH 平面, 非 RH 者非平面", (rh['planar'],nonrh['planar']), (True,False))
ck("★★ RH: 20 邊不相交 △ + 12 邊不相交 C₅ 覆蓋全部 120 邊",
   (rh['packT'],rh['packP'],rh['cov']), (20,12,120))

print("\n"+"="*88); print("§3 判定"); print("="*88)
print(f"""
  ★★ 決定性結果 (缺口 ④ 之「88 → 強制 A₅ 網」命題【否證】):
     MaxCut = 88 唔唯一決定 RH 網。存在第二個 4-正則 Cayley 圖 of A₅
     (連通 + 頂點傳遞 + Aut ⊇ A₅ + 20 三角形 + MaxCut = 88 精確) 但 ≇ RH。
     ⟹ 88 單獨 (甚至 + 連通 + 頂點傳遞 + 20△) 皆【唔】足夠。

  ★ 真正判別輸入 = 【平面性 / 球面等邊嵌入】:
     RH  = 平面, 面型 {rh['faces']} (Archimedean 3.4.5.4)
     非RH = 非平面 (面型 {nonrh['faces']})
     RH 之 △ + C₅ 裝填覆蓋全部 120 邊 ({rh['cov']}/120); 非 RH 覆蓋 {nonrh['cov']}/120。

  ⟹ 缺口 ④ 之正確陳述:
     「4-正則 + 20 邊不相交 △ + 12 邊不相交 ⬠ 覆蓋全部 120 邊 ⟹ MaxCut ≤ 88」
      係【單向】定理 (scripts/58 §2)。
     「MaxCut = 88 ⟹ RH/A₅ 網」係【假】 — 需要【額外】輸入「平面球面等邊嵌入」,
       而該輸入必須由 IDCM 側 (88 sites 之球面幾何) 提供, 唔可以從 88 推出。
""")
print("="*88)
print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}")
if FAIL: print("FAIL:", FAIL)
print("="*88)
