#!/usr/bin/env python3
"""
O137 — 小斜方截半二十面體 vs IDCM chiral 60-orbit: 完整驗證
=============================================================
回答: 「為什麼不以小斜方截半二十面體, 而是正二十面體?」

核心結果:
  - 小斜方截半二十面體 (RH) = 60 頂點, I-不變, 【中心對稱】(生成點落在鏡面上) → 24 模式
  - IDCM 60 節點 = RH 偏離鏡面 【2.6722°】 嘅 chiral 扭曲 → 9 模式
  - I-軌道只有 4 型: 12 (5-fold軸) / 20 (3-fold軸) / 30 (2-fold軸) / 60 (一般)
  - 12/20/30 【必然】中心對稱 (落對稱軸上, −v 必在軌道) → 24 模式
  - 只有 60-軌道可以係 chiral → 9 模式
"""
import numpy as np, math, itertools, sys
from collections import Counter

D="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/"
phi=(1+5**0.5)/2
def norm(P): return P/np.linalg.norm(P,axis=1,keepdims=True)
def rot(ax,an):
    a=np.array(ax,float); a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+math.sin(an)*K+(1-math.cos(an))*K@K
def dev(P,g):
    Q=norm(P@g.T); Dd=np.clip(Q@P.T,-1,1); return np.degrees(np.arccos(Dd.max(axis=1))).max()
def central(P):
    M=np.clip(P@(-P).T,-1,1); return np.degrees(np.arccos(M.max(axis=1))).max()
Tn=np.polynomial.chebyshev.Chebyshev.basis
def modes(P,tol=1e-3,nmax=44):
    x=P@P[0]
    return [n for n in range(1,nmax+1) if abs(float(Tn(n)(x).sum())-len(P)*(0 if n%2 else 1/(1-n*n)))<tol]

def cycles(A,L):
    """數簡單 L-圈 (每圈計一次)"""
    n=len(A); tot=0
    def dfs(s,u,depth,path):
        nonlocal tot
        if depth==L:
            if A[u,s]: tot+=1
            return
        for v in range(s+1,n):
            if A[u,v] and not (path>>v)&1:
                dfs(s,v,depth+1,path|(1<<v))
    for s in range(n): dfs(s,s,1,1<<s)
    return tot//2

G=[np.eye(3)]; fr=[np.eye(3)]
R1,R2=rot([0,1,phi],2*math.pi/5), rot([1,1,1],2*math.pi/3)
while fr:
    new=[]
    for g in fr:
        for h in (R1,R2):
            p=h@g
            if not any(np.allclose(p,q,atol=1e-9) for q in G): G.append(p); new.append(p)
    fr=new

ICO=np.load(D+"icosahedron_unit.npy") if (D+"icosahedron_unit.npy").startswith("/") and __import__("os").path.exists(D+"icosahedron_unit.npy") else None
# 重建 ICO / DOD / E2
ico=set()
for b in [(0,1,phi),(0,1,-phi),(0,-1,phi),(0,-1,-phi)]:
    for p in [(0,1,2),(1,2,0),(2,0,1)]: ico.add(tuple(round(b[i],10) for i in p))
ICO=norm(np.array(sorted(ico),float))
dod=set()
for s in itertools.product((1,-1),repeat=3): dod.add(tuple(float(x) for x in s))
for b in [(0,1/phi,phi),(0,1/phi,-phi),(0,-1/phi,phi),(0,-1/phi,-phi)]:
    for p in [(0,1,2),(1,2,0),(2,0,1)]: dod.add(tuple(round(b[i],10) for i in p))
DOD=norm(np.array(sorted(dod),float))
e2=[]
for i in range(12):
    for j in range(i+1,12):
        if abs(float(ICO[i]@ICO[j]) - 1/math.sqrt(5))<1e-9: e2.append(ICO[i]+ICO[j])
E2=norm(np.array(e2))

RH=np.load(D+"rhombicosidodecahedron_unit.npy")
raw=np.loadtxt("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt")
ra,dec=np.radians(raw[:,0]),np.radians(raw[:,1])
V=norm(np.column_stack([np.cos(dec)*np.cos(ra),np.cos(dec)*np.sin(ra),np.sin(dec)]))

PASS=[];FAIL=[]
def ck(n,got,exp,tol=1e-3):
    ok=abs(got-exp)<=tol if isinstance(exp,(int,float)) else got==exp
    (PASS if ok else FAIL).append(n); print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

print("="*84); print("§1 四型 I-軌道 + RH: 中心對稱性 / I-不變性 / 模式數"); print("="*84)
print(f"{'點集':>30} {'點數':>5} {'中心對稱':>10} {'I-不變':>11} {'模式數':>7} {'模式集':>34}")
res={}
for nm,P in [("正二十面體頂點 (5-fold 軸)",ICO),("正十二面體頂點 (3-fold 軸)",DOD),
             ("二十面體邊中點 (2-fold 軸)",E2),("小斜方截半二十面體 (RH)",RH),("IDCM 60 節點",V)]:
    cm=central(P); iv=max(dev(P,g) for g in G); m=modes(P)
    res[nm]=(cm,iv,m)
    ms=str(m) if len(m)<=12 else str(m[:6])+"..."+str(m[-3:])
    print(f"{nm:>30} {len(P):>5} {cm:>9.4f}° {iv:>10.5f}° {len(m):>7} {ms:>34}")

print("\n"+"="*84); print("§2 核心斷言"); print("="*84)
ck("RH 中心對稱 = 0°", central(RH), 0.0, 1e-6)
ck("RH I-不變 = 0°", max(dev(RH,g) for g in G), 0.0, 1e-5)
ck("RH 模式數 = 24", len(res["小斜方截半二十面體 (RH)"][2]), 24, 0)
ck("IDCM 中心對稱 = 5.3402°", central(V), 5.3402, 1e-3)
ck("IDCM 模式數 = 9", len(res["IDCM 60 節點"][2]), 9, 0)
ck("IDCM 模式集", res["IDCM 60 節點"][2], [1,2,3,4,5,7,9,11,13])
for nm in ["正二十面體頂點 (5-fold 軸)","正十二面體頂點 (3-fold 軸)","二十面體邊中點 (2-fold 軸)"]:
    ck(f"{nm} 中心對稱 = 0°", res[nm][0], 0.0, 1e-5)
    ck(f"{nm} 模式數 = 24", len(res[nm][2]), 24, 0)

print("\n"+"="*84); print("§3 IDCM 節點 = RH 嘅 2.6722° chiral 扭曲"); print("="*84)
Dm=np.degrees(np.arccos(np.clip(V@RH.T,-1,1)))
print(f"  IDCM → 最近 RH:  min={Dm.min():.6f}°  mean={Dm.mean():.6f}°  max={Dm.max():.6f}°")
print(f"  RH → 最近 IDCM:  min={Dm.min(axis=0).min():.6f}°  mean={Dm.min(axis=0).mean():.6f}°  max={Dm.min(axis=0).max():.6f}°")
ck("扭曲角 = 2.6722° (均勻)", float(Dm.min(axis=0).max()), 2.6722, 1e-3)
ck("RH→IDCM 位移完全均勻 (max=mean)", float(abs(Dm.min(axis=0).max()-Dm.min(axis=0).mean())), 0.0, 1e-3)
ck("2×2.6722 = 5.3444 ≈ 中心對稱破缺 5.3402", 2*float(Dm.min(axis=0).max()), 5.3402, 5e-3)
# RH 生成點在鏡面上?
ang2=np.degrees(np.arccos(np.clip(np.abs(E2@RH[0]),-1,1)))
ck("RH[0] 到最近 2-fold 軸 ≈ 90° (在鏡面上)", float(np.abs(ang2-90).min()), 0.0, 1e-3)
ang2v=np.degrees(np.arccos(np.clip(np.abs(E2@V[0]),-1,1)))
ck("IDCM[0] 到最接近 90° 嘅 2-fold 軸 ≈ 2.67° (扭曲含面內分量)", float(np.abs(ang2v-90).min()), 2.6722, 5e-3)

print("\n"+"="*84); print("§4 圖結構: IDCM 最近鄰圖 ≅ RH 圖?"); print("="*84)
for nm,P in [("RH",RH),("IDCM 60",V)]:
    dd=np.degrees(np.arccos(np.clip(P@P.T,-1,1))); np.fill_diagonal(dd,1e9)
    A=(dd<dd.min()*1.05).astype(int); np.fill_diagonal(A,0)
    c3,c4,c5=cycles(A,3),cycles(A,4),cycles(A,5)
    print(f"  {nm:>9}: 邊 {int(A.sum()//2)}, 度 {A.sum(1).min()}-{A.sum(1).max()}, 最近鄰 {dd.min():.4f}°, C3={c3}, C4={c4}, C5={c5}")
    if nm=="RH": rhc=(c3,c4,c5)
    else: vc=(c3,c4,c5)
ck("兩圖同構 (C3,C4,C5 相同)", vc==rhc, True)

print("\n"+"="*84); print("§5 Chirality 必要性"); print("="*84)
print(f"""
  60-點 I-軌道有兩類:
    (a) 生成點【在鏡面上】 (⊥ 某 2-fold 軸) ⟹ −v ∈ 軌道 ⟹ 中心對稱 ⟹ 24 模式
        例: 小斜方截半二十面體
    (b) 生成點【唔在鏡面上】 ⟹ −v ∉ 軌道 ⟹ chiral ⟹ 只有 h(l)=0 嘅奇 l 歸零 ⟹ 9 模式
        例: IDCM 60 節點 (偏離 2.6722°)

  而 12/20/30-軌道【必然】中心對稱 (生成點落對稱軸上 ⟹ −v 必在軌道) ⟹ 24 模式
  ⟹ 要得 9 模式, 必須用 60-軌道, 且必須破缺鏡面對稱 (chirality)
""")
ck("中心對稱集 → 24 模式 (無例外)", all(len(res[nm][2])==24 for nm in
   ["正二十面體頂點 (5-fold 軸)","正十二面體頂點 (3-fold 軸)","二十面體邊中點 (2-fold 軸)","小斜方截半二十面體 (RH)"]), True)
ck("chiral 60-軌道 → 9 模式", len(res["IDCM 60 節點"][2]), 9, 0)

print(f"\n{'='*84}\nPASS: {len(PASS)}, FAIL: {len(FAIL)}")
for f in FAIL: print(f"  ❌ {f}")
print("="*84)
sys.exit(1 if FAIL else 0)
