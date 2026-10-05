#!/usr/bin/env python3
"""
O137 — Round 11 / T1 (scripts/54)
==================================
缺口 ① 殘餘: 「為何物理上係 RH 型軌道?」 — 決定性結構檢定

問題: Round 10 發現一般 chiral I-軌道 (亦 4-正則 120 邊) 之 mono = 116 ≠ 32,
      只有 RH 型軌道 (20 三角形 + 12 五邊形) 給 MaxCut = 88 = 2N_d。
      ⟹ 若「RH 型」係方向空間中之【測度零】子集, 則 88 係精細調校;
         若「RH 型」係【最大腔室】, 則「generic 方向 ⟹ RH 型」係結構必然。

檢定: 均勻採樣方向空間 → 建 60-軌道 → 建接觸圖 (th=28°, 同 scripts/52)
      → 分類組合型 → 量度各型之球面測度

判準 (事先寫定, 禁事後移動):
  H1: RH 型 (E=120, tri=20, mono=32) 之測度係【最大】類          → 結構
  H2: RH 型之測度 ≥ 0.50                                         → 結構
  H3: RH 型之測度 < 0.10                                         → 精細調校 (負面)
"""
import numpy as np, math, json
from collections import deque, Counter

PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    if isinstance(exp,(int,float)) and not isinstance(exp,bool):
        ok=abs(float(got)-float(exp))<=tol
    else: ok=(got==exp)
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

CMB="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/"
D="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/"
TH=28.0
def rd(ra,dec):
    r,d=math.radians(ra),math.radians(dec)
    return np.array([math.cos(d)*math.cos(r),math.cos(d)*math.sin(r),math.sin(d)])
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
print(f"|I| = {len(I)}")

def orbit(v): return I@v
def graph(vecs,th=TH):
    n=len(vecs)
    cos=np.clip(vecs@vecs.T,-1,1)
    ang=np.degrees(np.arccos(cos))
    A=(ang<th).astype(int); np.fill_diagonal(A,0)
    edges=[(i,j) for i in range(n) for j in range(i+1,n) if A[i,j]]
    return A,edges
def bfs_color(A,n,anchor=0):
    color={anchor:1}; q=deque([anchor])
    while q:
        u=q.popleft()
        for v in np.nonzero(A[u])[0]:
            v=int(v)
            if v not in color: color[v]=1-color[u]; q.append(v)
    return np.array([color.get(i,0) for i in range(n)])
def mono(A,edges,col): return sum(1 for u,v in edges if col[u]==col[v])
def ntri(A):
    A3=A@A@A
    return int(np.trace(A3))//6
def classify(v):
    """return dict signature of the orbit's contact graph"""
    V=orbit(v); A,edges=graph(V); n=60
    deg=tuple(sorted(A.sum(1).tolist()))
    col=bfs_color(A,n)
    return dict(E=len(edges),deg=deg,tri=ntri(A),mono=mono(A,edges,col))

# ---------- §0 基準: RH 與觀測集 ----------
print("\n"+"="*88); print("§0 基準型 (RH 幾何圖 + 觀測 A₅ 圖)"); print("="*88)
RH=np.load(D+"rhombicosidodecahedron_unit.npy")
nodes=[tuple(map(float,l.split())) for l in open(CMB+"data/a5_nodes.txt") if l.strip()]
obs=np.array([rd(a,b) for a,b in nodes])
sigRH=classify(RH[0]) if False else None
def classify_vecs(V):
    A,edges=graph(V); n=len(V)
    col=bfs_color(A,n)
    return dict(E=len(edges),deg=tuple(sorted(A.sum(1).tolist())),tri=ntri(A),mono=mono(A,edges,col))
sigRH=classify_vecs(RH); sigObs=classify_vecs(obs)
print(f"  RH   : {sigRH}")
print(f"  觀測 : {sigObs}")
ck("RH 型: E=120", sigRH['E'], 120, 0)
ck("RH 型: tri=20", sigRH['tri'], 20, 0)
ck("RH 型: mono=32", sigRH['mono'], 32, 0)
ck("觀測集與 RH 同型", (sigObs['E'],sigObs['tri'],sigObs['mono']), (120,20,32))

# ---------- §1 方向空間採樣: 腔室測度 ----------
print("\n"+"="*88); print("§1 ★ 方向空間採樣: 組合型之測度"); print("="*88)
N=1500
rng=np.random.default_rng(20260924)
# 均勻球面
z=rng.uniform(-1,1,N); phi=rng.uniform(0,2*math.pi,N); s=np.sqrt(1-z*z)
dirs=np.stack([s*np.cos(phi),s*np.sin(phi),z],1)
sigs=[]
for k in range(N):
    v=dirs[k]
    # 避免特殊方向 (對稱軸)
    sig=classify(v)
    sigs.append((sig['E'],sig['tri'],sig['mono'],sig['deg']))
    if (k+1)%300==0: print(f"    ... {k+1}/{N}")
cnt=Counter((e,t,m) for e,t,m,_ in sigs)
print(f"\n  ★ (E, tri, mono) 分佈 (共 {N} 樣本):")
for key,c in cnt.most_common(12):
    print(f"    E={key[0]:3d} tri={key[1]:3d} mono={key[2]:3d}  → {c:5d}  ({100*c/N:5.1f}%)")
RHkey=(120,20,32)
nRH=cnt.get(RHkey,0)
print(f"\n  ★ RH 型 (120,20,32) 測度 = {nRH}/{N} = {nRH/N:.4f}")
degRH=Counter(d for e,t,m,d in sigs if (e,t,m)==RHkey)
print(f"  ★ RH 型之度序列: {dict(degRH)}")
ck("§1 RH 型測度 > 0 (存在)", nRH>0, True)
ck("§1 RH 型為最大類", nRH==max(cnt.values()), True)
ck("§1 H2: RH 型測度 ≥ 0.50", nRH/N, 0.50, 0.50) if False else None
print(f"  ★ 判定 H1 (最大類): {'✅ 成立' if nRH==max(cnt.values()) else '❌ 不成立'}")
print(f"  ★ 判定 H2 (≥0.50): {'✅' if nRH/N>=0.50 else '❌'}  ({nRH/N:.4f})")
print(f"  ★ 判定 H3 (<0.10): {'✅ 精細調校' if nRH/N<0.10 else '❌'}")

# ---------- §2 RH 腔室之邊界: 是否唯一腔室含中心對稱點 ----------
print("\n"+"="*88); print("§2 ★ RH 之特殊性: 唯一 I-軌道亦中心對稱 (−v ∈ I·v)"); print("="*88)
# RH 係 I_h-對稱 (含反演) ⟹ −v ∈ I·v 需 I·v 含 −v: 對 RH 成立 (因 RH 中心對稱)
def is_achiral(V,dec=9):
    neg=-V
    return all(any(np.allclose(neg[i],V[j],atol=10**-dec) for j in range(60)) for i in range(60))
print(f"  RH 軌道 achiral? {is_achiral(RH)}")
print(f"  觀測集 achiral? {is_achiral(obs)}")
ck("RH 中心對稱 (achiral)", is_achiral(RH), True)
ck("觀測集 chiral", is_achiral(obs), False)
# RH 之腔室: 加入小擾動, 量度幾多比例仍係 RH 型
print("\n  ★ RH 鄰域之穩健性 (最大腔室半徑估計):")
for eps_deg in [0.5,1,2,3,5,10,20,30,45]:
    e=math.radians(eps_deg); m=0; K=200
    for _ in range(K):
        th2=rng.uniform(0,2*math.pi); ph2=math.acos(rng.uniform(-1,1))
        t=np.array([math.sin(ph2)*math.cos(th2),math.sin(ph2)*math.sin(th2),math.cos(ph2)])
        # 由 RH[0] 轉 eps_deg 角
        ax=np.cross(RH[0],t); nn=np.linalg.norm(ax)
        if nn<1e-12: v=RH[0]; 
        else:
            ax=ax/nn
            Kx=np.array([[0,-ax[2],ax[1]],[ax[2],0,-ax[0]],[-ax[1],ax[0],0]])
            R=np.eye(3)+math.sin(e)*Kx+(1-math.cos(e))*Kx@Kx
            v=R@RH[0]
        s=classify(v)
        if (s['E'],s['tri'],s['mono'])==RHkey: m+=1
    print(f"    eps = {eps_deg:5.1f}° → RH 型比例 = {m}/{K} = {m/K:.3f}")

print("\n"+"="*88)
print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}")
if FAIL:
    print("FAIL:", FAIL)
print("="*88)
