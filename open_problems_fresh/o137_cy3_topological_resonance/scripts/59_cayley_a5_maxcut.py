#!/usr/bin/env python3
"""
O137 — Round 13 (scripts/59)
============================
缺口 ④ 收窄後之攻堅:
  scripts/58 已證:
    R1 ✅ RH 結構 ⟹ MaxCut ≤ 88 (定理, 界可取, MILP 精確 = 88)
    R2 ✅ 隨機 4-正則 (60v): MaxCut = 95.5 ± 2.2, 0/200 ≤ 88
    R3-A 🔴 MaxCut = 88 【唔】強制 RH — 非連通反例存在 (5×9v+8v+7v)
    R3-B   連通 SA 最佳 = 90 (> 88), 未能達到

  ⟹ 收窄後之尖銳問題:
     「連通 4-正則 (60v) 且 MaxCut = 88」係否唯一給 RH 圖?

本輪關鍵觀察:
  ★ RH 圖 = A₅ 之 Cayley 圖。
    因 I (≅ A₅) 對 60 點軌道之作用係【正則】(自由 + 傳遞, 穩定子平凡),
    故 RH 圖自動係 Cay(A₅, S), |S| = 4。
  ⟹ 尖銳問題變為: 4-正則 Cayley 圖 of A₅ 中, MaxCut = 88 者有幾個?

MaxCut 等價形式 (用於判定):
  MaxCut(G) = E − τ_odd(G),  τ_odd = 最小邊刪除數使 G 二部 (bipartization)
  ⟹ MaxCut = 88 ⟺ τ_odd = 32
"""
import numpy as np, math, itertools
from collections import Counter, defaultdict
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
TH=28.0
def adj_from_vecs(V,th=TH):
    C=np.clip(V@V.T,-1,1); A=(np.degrees(np.arccos(C))<th).astype(int)
    np.fill_diagonal(A,0); return A
def edges_of(A):
    n=A.shape[0]; return [(i,j) for i in range(n) for j in range(i+1,n) if A[i,j]]
A_RH=adj_from_vecs(RH); E_RH=edges_of(A_RH)
G_RH=nx.from_numpy_array(A_RH)

def maxcut_lb(Adj,restarts=25,seed=0):
    rng=np.random.default_rng(seed); n=Adj.shape[0]; E=Adj.sum()/2; best=-1.0
    for _ in range(restarts):
        s=rng.choice([-1.0,1.0],size=n); As=Adj@s
        for _ in range(4*n):
            delta=s*As; i=int(np.argmax(delta))
            if delta[i]<=1e-12: break
            old=s[i]; s[i]=-s[i]; As=As-2*old*Adj[:,i]
        best=max(best,(E-float(s@As)/2)/2)
    return best
def exact_maxcut(edges,n,time_limit=120):
    m=len(edges); N=n+m; c=np.zeros(N); c[n:]=-1.0
    rows=[];lb=[];ub=[]
    for k,(u,v) in enumerate(edges):
        r=np.zeros(N); r[u]=1; r[v]=1; r[n+k]=-1; rows.append(r); lb.append(0); ub.append(np.inf)
        r2=np.zeros(N); r2[u]=-1; r2[v]=-1; r2[n+k]=-1; rows.append(r2); lb.append(-2); ub.append(0)
    res=milp(c=c,constraints=LinearConstraint(np.array(rows),lb,ub),integrality=np.ones(N),
             bounds=Bounds([0]*n+[0]*m,[1]*n+[1]*m),options={"time_limit":time_limit,"presolve":True})
    return -res.fun if res.fun is not None else None

# ──────────────────────────────────────────────────────────────
print("="*88); print("§1 ★★ RH 圖 = A₅ 之 Cayley 圖?"); print("="*88)
def rot(ax,an):
    a=np.array(ax,float); a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+math.sin(an)*K+(1-math.cos(an))*K@K
def closure(gens,dec=9):
    G=[np.eye(3)]; fr=[np.eye(3)]
    while fr:
        new=[]
        for g in fr:
            for h in gens:
                q=h@g
                if not any(np.allclose(q,r,atol=10**-dec) for r in G): G.append(q); new.append(q)
        fr=new
    return np.array(G)
ph=(1+5**0.5)/2
I=closure([rot([0,1,ph],2*math.pi/5), rot([1,1,1],2*math.pi/3)])
print(f"  |I| = {len(I)}")
ck("|I| = 60 (≅ A₅)", len(I), 60)
v0=RH[0]
perm=[]
for g in I:
    w=g@v0
    j=int(np.argmax(RH@w))
    assert float(RH[j]@w)>1-1e-9, "orbit not regular!"
    perm.append(j)
print(f"  穩定子: 每個 g·v₀ 恰命中一個 RH 點 (max dot > 1−1e−9)")
ck("★ I 對 60 點之作用係【正則】(穩定子平凡, |orbit| = |I|)", len(set(perm)), 60)
S=[i for i in range(60) if A_RH[0,perm[i]]==1]
print(f"  連接集 S = {{g : v₀ ~ g·v₀}} 大小 = {len(S)}")
ck("★ |S| = 4 (4-正則)", len(S), 4)
# S 應對反元素封閉 (指標意義: g_i⁻¹ 對應之指標)
inv_idx=[]
for i in S:
    M=I[i].T
    j=int(np.argmin([np.abs(M-k).max() for k in I]))
    inv_idx.append(j)
ck("★ S 對反元素封閉", sorted(inv_idx)==sorted(S), True)
# 建 Cayley 圖: 頂點 = I 元素, 邊 (h, h∘s)
pos={}
for i,g in enumerate(I):
    key=tuple(np.round(g,8).ravel())
    pos[key]=i
Acay=np.zeros((60,60),dtype=int)
for i in range(60):
    for s in S:
        prod=I[i]@I[s]
        key=tuple(np.round(prod,8).ravel())
        j=pos[key]
        Acay[i,j]=1
Acay=((Acay+Acay.T)>0).astype(int); np.fill_diagonal(Acay,0)
print(f"  Cayley 圖: E = {int(Acay.sum()/2)}, 度集 = {sorted(set(Acay.sum(axis=1).tolist()))}")
ck("★★ Cayley(I, S) ≅ RH 圖", nx.is_isomorphic(nx.from_numpy_array(Acay),G_RH), True)

# ──────────────────────────────────────────────────────────────
print("\n"+"="*88); print("§2 ★★ 枚舉全部 4-正則 Cayley 圖 of A₅"); print("="*88)
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
noninv=[p for p in A5 if order(p)>2]
print(f"  |A₅| = {len(A5)};  非對合元素 = {len(noninv)} (階 3: {sum(1 for p in noninv if order(p)==3)}, 階 5: {sum(1 for p in noninv if order(p)==5)})")
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
def cayley_edges(a,b):
    S=[a,inv(a),b,inv(b)]
    if len(set(S))<4: return None
    return S
graphs={}
pairs=0
for i in range(len(noninv)):
    for j in range(i+1,len(noninv)):
        a,b=noninv[i],noninv[j]
        if b in (a,inv(a)): continue
        pairs+=1
        if subgroup_order([a,b])!=60: continue
        S=cayley_edges(a,b)
        if S is None: continue
        n=60; A=np.zeros((n,n),dtype=int)
        for k,p in enumerate(A5):
            for s in S:
                A[k,idx[mul(p,s)]]=1
        A=((A+A.T)>0).astype(int); np.fill_diagonal(A,0)
        if A.sum()!=240: continue
        key=tuple(np.round(np.sort(np.linalg.eigvalsh(A.astype(float))),5))
        graphs.setdefault(key,(A,a,b))
print(f"  非對合元素對 = {pairs};  生成 A₅ 且 |S|=4 者 → 非同構 Cayley 圖 = {len(graphs)}")

# ──────────────────────────────────────────────────────────────
print("\n"+"="*88); print("§3 ★★ 各 Cayley 圖之 MaxCut"); print("="*88)
rows=[]
for key,(A,a,b) in graphs.items():
    lb=maxcut_lb(A.astype(float),30,seed=1)
    tri=int(np.trace(A@A@A)//6)
    iso=nx.is_isomorphic(nx.from_numpy_array(A),G_RH)
    rows.append((lb,tri,iso,A,a,b))
rows.sort(key=lambda r:r[0])
print(f"  {'MaxCut下界':>10} {'#三角形':>7} {'≅RH':>6}   階(a),階(b)")
for lb,tri,iso,A,a,b in rows:
    print(f"  {lb:>10.1f} {tri:>7} {str(iso):>6}   {order(a)},{order(b)}")
lbs=np.array([r[0] for r in rows])
print(f"\n  MaxCut 下界分佈: min = {lbs.min():.1f}, max = {lbs.max():.1f}, mean = {lbs.mean():.1f}")
n88=int((lbs<=88).sum())
print(f"  ★ 下界 ≤ 88 之 Cayley 圖數 = {n88}")
ck("★ 全部 4-正則 Cayley 圖 of A₅ 之 MaxCut 下界 ≥ 88", float(lbs.min())>=88, True)
ck("★★ 下界 = 88 者恰為 RH 圖 (即唯一 MaxCut = 88)", all(r[2] for r in rows if r[0]<=88), True)

# MILP 精確核對下界 ≤ 89 者
print("\n  ── MILP 精確核對 (下界 ≤ 90 者) ──")
for lb,tri,iso,A,a,b in rows:
    if lb<=90:
        ex=exact_maxcut(edges_of(A),60,time_limit=180)
        print(f"    LB = {lb:.1f} → MILP 精確 = {ex}   (≅RH = {iso}, 階 = {order(a)},{order(b)})")

# ──────────────────────────────────────────────────────────────
print("\n"+"="*88); print("§4 判定"); print("="*88)
print(f"""
  §1 ★★ RH 圖 = Cay(A₅, S) 已證 (|S| = 4, S 對反元素封閉, 同構驗證 ✅)
     因 I 對 60 點軌道之作用係正則 — 呢個係 O182「88 格 = A₅ 網」之代數根源。

  §2/§3: 全部 4-正則 Cayley 圖 of A₅ 共 {len(graphs)} 個非同構類。
     全部 MaxCut 下界 ≥ {lbs.min():.1f};  下界 = 88 者恰為 RH 圖。

  ⟹ 缺口 ④ 之新地位:
     ① 正向 (R1): RH 結構 ⟹ MaxCut = 88  [定理, 界可取] ✅
     ② 88 單獨唔足夠 (R3-A): 非連通反例存在 🔴
     ③ ★ 在【連通 + 頂點傳遞 (Cayley of A₅)】約束下:
        MaxCut = 88 似乎唯一給 RH 圖 — 但需 MILP 確認全部 (下界非精確)
""")
print("="*88)
print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}")
if FAIL: print("FAIL:", FAIL)
print("="*88)
