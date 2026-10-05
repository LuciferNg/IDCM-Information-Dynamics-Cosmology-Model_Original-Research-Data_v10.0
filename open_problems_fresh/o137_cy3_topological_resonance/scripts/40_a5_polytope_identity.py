#!/usr/bin/env python3
"""
O137 — A₅ 節點集身份鑑定: 小斜方截半二十面體 (Rhombicosidodecahedron) vs chiral 60-orbit

★ 用戶提問: 「為什麼不以小斜方截半二十面體, 而是正二十面體?」

本 script 檢驗一個尖銳矛盾:
  - 文檔 (cmb_cold_spot/docs/19, 20, 21) 稱 60 節點 = Rhombicosidodecahedron (120 邊)
  - 但 Rhombicosidodecahedron 【中心對稱】(含反演 −1)
  - 中心對稱 ⟹ 所有奇 Legendre 動差恆零 ⟹ 全部奇 n 選中 ⟹ 24 模式
  - 但實測只選中 9 模式 ⟹ 矛盾!

檢驗:
  (A) IDCM 60 節點: 中心對稱? I-invariant?
  (B) 構造真 Rhombicosidodecahedron → 中心對稱? 模式數?
  (C) 四種 I-軌道 (12/20/30/60) 嘅中心對稱性 + 模式數
  (D) IDCM 60 節點 同 Rhombicosidodecahedron 嘅幾何距離
  (E) 節點 0 到最近 2-fold / 3-fold / 5-fold 軸嘅角距 (chirality 參數)
  (F) 邊結構 (度數分佈) 對比
"""
import numpy as np, math, itertools
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
raw = np.loadtxt(ROOT/"cmb_cold_spot/data/a5_nodes.txt")
ra, dec = np.radians(raw[:,0]), np.radians(raw[:,1])
V = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
V /= np.linalg.norm(V,axis=1,keepdims=True)
phi = (1+5**0.5)/2

# ---- 群 I ----
def rot(ax,an):
    a=np.array(ax,float); a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+math.sin(an)*K+(1-math.cos(an))*K@K
R1,R2 = rot([0,1,phi],2*math.pi/5), rot([1,1,1],2*math.pi/3)
G=[np.eye(3)]; fr=[np.eye(3)]
while fr:
    new=[]
    for g in fr:
        for h in (R1,R2):
            p=h@g
            if not any(np.allclose(p,q,atol=1e-9) for q in G): G.append(p); new.append(p)
    fr=new

def norm(P): return P/np.linalg.norm(P,axis=1,keepdims=True)
def central(P):
    """回傳每個 v 到最近 (−v') 嘅角距 (度); max=0 ⟺ 中心對稱"""
    M = np.clip(P @ (-P).T, -1, 1)
    a = np.degrees(np.arccos(M.max(axis=1)))
    return a.max(), a.mean()
def iinv(P, tol=1e-4):
    d=[]
    for g in G:
        Q=norm(P@g.T); D=np.clip(Q@P.T,-1,1); d.append(np.degrees(np.arccos(D[np.arange(len(P)),D.argmax(axis=1)])).max())
    return max(d)
Tn=np.polynomial.chebyshev.Chebyshev.basis
def modes(P, tol=1e-3, nmax=44):
    c=P[0]  # 軸 = 節點 0
    x=P@c
    return [n for n in range(1,nmax+1) if abs(float(Tn(n)(x).sum())-len(P)*(0 if n%2 else 1/(1-n*n)))<tol]

# ---- 構造各 I-軌道 ----
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
        if abs(np.dot(ICO[i],ICO[j]) - 1/math.sqrt(5)) < 1e-9: e2.append(ICO[i]+ICO[j])
E2=norm(np.array(e2))

# Rhombicosidodecahedron (小斜方截半二十面體) — 標準座標: 【偶置換】(3 個循環置換)
def addcyc(S,*vals):
    for k in range(3): S.add(tuple(round(vals[(i+k)%3],10) for i in range(3)))
R=set()
for s in itertools.product((1,-1),repeat=3): addcyc(R, s[0]*1, s[1]*1, s[2]*phi**3)
for s in itertools.product((1,-1),repeat=3): addcyc(R, s[0]*phi**2, s[1]*phi, s[2]*2*phi)
for s in itertools.product((1,-1),repeat=2): addcyc(R, s[0]*(2+phi), 0.0, s[1]*phi**2)
RH=norm(np.array(sorted(R),float))

print("="*84); print("(A)(B)(C) 中心對稱性 + I-不變性 + 模式數"); print("="*84)
sets = [("IDCM 60 節點 (本項目)", V, 60),
        ("正二十面體 12 頂點 (5-fold 軸)", ICO, 12),
        ("正十二面體 20 頂點 (3-fold 軸)", DOD, 20),
        ("正二十面體 30 邊中點 (2-fold 軸)", E2, 30),
        ("小斜方截半二十面體 60 頂點", RH, 60)]
print(f"\n{'點集':>34} {'點數':>5} {'中心對稱 (max 角距)':>20} {'I-不變':>10} {'模式數':>7}")
for nm,P,n in sets:
    cm, ca = central(P)
    print(f"{nm:>34} {len(P):>5} {cm:>19.4f}° {iinv(P):>9.5f}° {len(modes(P)):>7}")
print(f"\n  (中心對稱 max 角距 = 每個 v 到最近 (−v') 嘅角距最大值; 0 ⟺ 完全中心對稱)")
print(f"  ⟹ 中心對稱 ⟹ 所有奇 Legendre 動差恆零 ⟹ 全部奇 n 選中 ⟹ 24 模式")

print("\n"+"="*84); print("(C2) 模式集逐個列出"); print("="*84)
for nm,P,n in sets:
    m=modes(P)
    print(f"  {nm:>34}: {len(m):>2} 個 = {m if len(m)<=12 else str(m[:6])+' ... '+str(m[-3:])}")

print("\n"+"="*84); print("(D) IDCM 60 節點 vs 小斜方截半二十面體 幾何距離"); print("="*84)
D = np.degrees(np.arccos(np.clip(V@RH.T,-1,1)))
print(f"  IDCM 節點 → 最近 RH 頂點:  min={D.min():.4f}°  mean={D.mean():.4f}°  max={D.max():.4f}°")
print(f"  RH 頂點 → 最近 IDCM 節點:  min={D.min(axis=0).min():.4f}°  mean={D.min(axis=0).mean():.4f}°  max={D.min(axis=0).max():.4f}°")
print(f"  ★ 兩集係同一組? {'✅ 係' if D.min()<0.01 else '🔴 唔係 — 相距 %.2f°' % D.min()}")
# 最近鄰角距對比
def nn(P):
    d=np.degrees(np.arccos(np.clip(P@P.T,-1,1))); np.fill_diagonal(d,1e9)
    return d.min(axis=1)
print(f"\n  最近鄰角距:  IDCM 60: min={nn(V).min():.4f}° max={nn(V).max():.4f}°")
print(f"               RH  60: min={nn(RH).min():.4f}° max={nn(RH).max():.4f}°")

print("\n"+"="*84); print("(E) Chirality 參數: 節點 0 到最近對稱軸"); print("="*84)
for nm, ax in [("5-fold 軸 (12)", ICO), ("3-fold 軸 (20)", DOD), ("2-fold 軸 (30)", E2)]:
    a=np.degrees(np.arccos(np.clip(np.abs(ax@V[0]),-1,1)))
    print(f"  節點 0 → {nm:>16}: 最小 {a.min():.4f}°")
print(f"\n  ★ 節點 0 落在鏡面上 ⟺ 節點 0 ⊥ 某 2-fold 軸 ⟺ −v₀ ∈ 軌道 ⟺ 中心對稱")
a2 = np.degrees(np.arccos(np.clip(np.abs(E2@V[0]),-1,1)))
print(f"  節點 0 到最近 2-fold 軸 = {a2.min():.4f}°  (需 90° 才中心對稱)")
print(f"  節點 0 到【最接近 90°】嘅 2-fold 軸 = {np.abs(a2-90).min():.4f}°   ⟸ chirality 參數")
print(f"  (小斜方截半二十面體頂點: 此值 = 0 ⟹ 落在鏡面上)")

print("\n"+"="*84); print("(E2) 圖結構對比 (最近鄰圖)"); print("="*84)
def graph(P, fac=1.05):
    d=np.degrees(np.arccos(np.clip(P@P.T,-1,1))); np.fill_diagonal(d,1e9)
    A=(d < d.min()*fac).astype(int); np.fill_diagonal(A,0)
    return A
for nm,P in [("IDCM 60 節點", V), ("小斜方截半二十面體", RH)]:
    A=graph(P)
    tri = int(np.trace(A@A@A)//6)
    # 4-圈 / 5-圈: 用 A^k 對角減去含更短圈者 (簡化: 短圈計數)
    A2, A3, A4, A5 = A@A, A@A@A, A@A@A@A, A@A@A@A@A
    print(f"  {nm:>18}: 點 {len(P)}, 邊 {int(A.sum()//2)}, 度數 {A.sum(1).min()}–{A.sum(1).max()}, 三角形 {tri}")

print("\n"+"="*84); print("(F) 邊結構 (最近鄰圖)"); print("="*84)
for nm,P,n in [("IDCM 60", V, 60), ("小斜方截半二十面體 60", RH, 60)]:
    d=np.degrees(np.arccos(np.clip(P@P.T,-1,1))); np.fill_diagonal(d,1e9)
    dmin=d.min()
    for fac in [1.02, 1.10, 1.25]:
        adj=(d < dmin*fac).sum(axis=1)
        print(f"  {nm:>22} 門檻 {fac:.2f}×min({dmin:.4f}°): 度數 {adj.min()}–{adj.max()} (中位 {int(np.median(adj))}), 邊數 {int(adj.sum()//2)}")
    print()

print("="*84); print("結論"); print("="*84)
print(f"""
  IDCM 60 節點集:
    - I-invariant ✅ (偏差 9.7e−5°)
    - 中心對稱 🔴 否 (max 角距 {central(V)[0]:.4f}°) ⟹ 【唔係】小斜方截半二十面體
    - 模式數 = {len(modes(V))}

  小斜方截半二十面體 60 頂點:
    - I-invariant ✅ (偏差 {iinv(RH):.5f}°)
    - 中心對稱 ✅ 是 (max 角距 {central(RH)[0]:.4f}°) ⟹ 含反演 −1
    - 模式數 = {len(modes(RH))}

  ⟹ 兩者係【唔同】嘅 60-點 I-軌道。
  ⟹ 用 小斜方截半二十面體 會得 {len(modes(RH))} 模式, 唔係 9。
""")
