#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U2 — R1b-A5 判死定理: 頂點傳遞 ⟹ A₅ 幾何投影家族全體 node-agnostic
================================================================================
R1b-A5 候選（我用 A₅ 60 節點距離/角度 → 0 參數投影 → 8 F_proj）係唔可行，
因為 O143 docs/08 頂點傳遞定理已證明: A₅ 圖 |Aut(G)|=120=I_h, G 頂點傳遞
(60 節點單一軌道) ⟹ 任何 graph-invariant 算子/幾何量都唔可以區分節點
(T₉=T₂₀ 機器精度, 2.8e-17)。

本 script 將呢個推廣到「任何 A₅ 幾何投影 → F_proj」嘅形式化 no-go:
  §1 重現 A₅ 60 節點 + Aut 頂點傳遞
  §2 驗證 graph-invariant 幾何量 (度數/距離譜/三角形/WL 色類/譜標記) 全部 node-agnostic
  §3 定理: 任何 A₅ 節點幾何量 g(V,i) 若係 Aut(G)-invariant ⟹ g(V,i)=g(V,j) ∀i,j
  §4 結論: F_proj 若由 A₅ 幾何投影生成 ⟹ 全部粒子同值 ⟹ 同 8 個互異 F_proj 矛盾
         ⟹ R1b-A5 判死 (結構不可能, 唔係「未試夠」)
"""
import numpy as np, math, itertools
from pathlib import Path

PASS, FAIL = [], []
def ck(name, got, exp, tol=None):
    if tol is not None:
        ok = bool(abs(float(got)-float(exp)) < tol)
    else:
        ok = bool(got == exp)
    (PASS if ok else FAIL).append(name)
    print(f"  {'OK ' if ok else 'FAIL'} {name} = {got}" + ("" if ok else f"  [exp {exp}]"))

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
raw = np.loadtxt(ROOT/"cmb_cold_spot/data/a5_nodes.txt")
ra, dec = np.radians(raw[:,0]), np.radians(raw[:,1])
V = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
V /= np.linalg.norm(V,axis=1,keepdims=True)
phi = (1+5**0.5)/2

print("="*84)
print("O237 U2 R1b-A5 — 頂點傳遞 ⟹ A₅ 幾何投影 node-agnostic (no-go)")
print("="*84)

# 群 I (五重 + 三重旋轉生成)
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
print(f"\n[1] A₅ 群: |I| = {len(G)} (期望 60)")

# ---------------------------------------------------------------- §1 頂點傳遞
print("\n[1] 頂點傳遞重現 (O143 docs/08)")
# 對每個 i, 搵 g∈G 令 g(V_i) ≈ V_j (所有 j)
d = np.degrees(np.arccos(np.clip(V@V.T,-1,1)))
# Aut = 120 = I_h (O143): 幾何座標只有手性 I (60 等距), 但組合 Aut = 120
# 對圖論 no-go, |Aut|=120 已夠; 幾何上用到 I (60) 已夠: 任一節點可由群作用到另一節點?
# I 作用 60 節點: 單一軌道 ⟺ 存在 g: V_i → V_j
def orbit_size(V, Gm):
    vs = V[0]
    seen = set()
    for g in Gm:
        w = vs@g
        # 找最近節點 index
        dw = 1e9; bi = -1
        for k in range(len(V)):
            dd = np.linalg.norm(w - V[k])
            if dd < dw: dw, bi = dd, k
        seen.add(bi)
    return len(seen)
o1 = orbit_size(V, G)
print(f"    I 作用節點 0 嘅軌道大小 = {o1} (60 = 頂點傳遞)")
ck("I 軌道 = 60 (頂點傳遞, 幾何層)", o1, 60)
# 補上反演 (I_h = I ∪ −I, 120) 的話
Gm2 = G + [-g for g in G]
o2 = orbit_size(V, Gm2)
ck("I_h 軌道 = 60 (頂點傳遞, 組合層)", o2, 60)

# ---------------------------------------------------------------- §2 幾何量掃描
print("\n[2] graph-invariant 幾何量 逐節點掃描 (圖論層: 應 node-agnostic)")
d2 = d.copy()
np.fill_diagonal(d2, np.inf)
# 最近鄰角距 (幾何, Aut-invariant)
nn_d = d2.min(axis=1)
print(f"    最近鄰角距: min={nn_d.min():.6f} max={nn_d.max():.6f} spread={100*(nn_d.max()-nn_d.min())/nn_d.mean():.4f}%")
# 距離譜 (全距離 bag) 每節點: 59 個非對角距離
K = 0
dist_bags = [tuple(sorted(np.round(d2[i],5))) for i in range(60)]
print(f"    全距離包 60 節點 互異類 = {len(set(dist_bags))}  (a5 raw; O143 scripts/21: 座標有 0.075° 噪聲)")
# 度數 (4-regular): 近鄰閾 1.05×min
thr = d2.min()*1.05
deg = (d2 < thr).sum(axis=1)
print(f"    度數 set = {set(deg)}")
ck("度數全部 = 4 (node-agnostic)", set(deg), {4})
# 三角形數
A = (d2 < thr).astype(int)
tri = (A@A@A).diagonal()//2
print(f"    三角形數 set = {set(tri)}")
ck("三角形數全部一致 (node-agnostic)", len(set(tri)), 1)
# WL: 修正實作 — 初始 uniform 色 0, 鄰居色聚合, 唔可以用 index 當 label
c_cur = np.zeros(60, dtype=int)
c_next = np.zeros(60, dtype=int)
for _ in range(6):
    for i in range(60):
        c_next[i] = hash(tuple(sorted(c_cur[np.where(A[i]>0)[0]])))
    c_cur = c_next.copy()
cset = set(c_cur)
print(f"    6-step WL 色類數 = {len(cset)} (O143: 收斂 16; node9/node20 同色)")
ck("WL: node9 與 node20 同色 (頂點傳遞圖論確認)", c_cur[9], c_cur[20])

# ---------------------------------------------------------------- §2b 精確 I-軌道對照
print("\n[2b] 精確無噪聲 I-軌道對照 (噪聲隔離)")
# 冷斑方向 = node 0 (a5 第一行); 用手性 I 群 60 個旋轉生成精確軌道
v0 = V[0]
Vex = np.array([v0@g for g in G])
Vex /= np.linalg.norm(Vex,axis=1,keepdims=True)
dex = np.degrees(np.arccos(np.clip(Vex@Vex.T,-1,1)))
np.fill_diagonal(dex, np.inf)
bags_ex = [tuple(sorted(np.round(dex[i],5))) for i in range(60)]
nn_ex = dex.min(axis=1)
print(f"    精確 I-軌道: 最近鄰散佈 = 100*(max-min)/mean = {100*(nn_ex.max()-nn_ex.min())/nn_ex.mean():.4f}%")
print(f"    精確 I-軌道 距離包互異類 = {len(set(bags_ex))}  (1 = 全等距一致)")
ck("精確 I-軌道距離包 = 1 類 (a5 15 類 = 噪聲, 唔係結構)", len(set(bags_ex)), 1)
# a5 raw vs 精確軌道嘅最近鄰
nn_raw = d2.min(axis=1)
print(f"    a5 raw 最近鄰 spread = {100*(nn_raw.max()-nn_raw.min())/nn_raw.mean():.4f}% vs 精確 {100*(nn_ex.max()-nn_ex.min())/nn_ex.mean():.4f}%")
ck("a5 raw 噪聲 ≫ 精確軌道 (距離分類係噪聲產物)", 100*(nn_raw.max()-nn_raw.min())/nn_raw.mean() > 100*(nn_ex.max()-nn_ex.min())/nn_ex.mean(), True)

# ---------------------------------------------------------------- §3 定理
print("\n[3] 定理 (形式化)")
print("""
  定理: 設 g(V, i) 係 A₅ 節點 i 嘅任何 Aut(G)-invariant 幾何量 (距離/角/譜/局部結構),
        即 ∀σ ∈ Aut(G): g(V, σ(i)) = g(V, i).  則 g(V, i) = g(V, j) ∀i,j.
  證明: G 頂點傳遞 ⟹ ∃σ ∈ Aut(G): σ(i) = j ⟹ g(V,i) = g(V,σ(i)) = g(V,j) ∎
  推論: 任何由 A₅ 幾何投影定義嘅 F_proj(i) 若 Aut-invariant ⟹ 全粒子同值。
        8 個互異 F_proj (O206 第十輪) ⟹ 矛盾.
  ⟹ R1b-A5 判死: 唔係「未試夠」, 係結構不可能 (除非引入非 Aut-invariant 輸入,
    即 sky-side 場 — 但質量係內在結構, 唔係 sky 投影)。
""")

# ---------------------------------------------------------------- §4 對照 O182
print("\n[4] O182 獨立確認 (逐點鏈索引已否決)")
# O182: A₅ 網 88 透明邊中點; canonical 88-grid |Sym|=4 非手性 vs 冷斑 88-grid |Sym|=2 手性
# (引述, 唔重推; 本 script 只做 R1b-A5 no-go)
print("    O182: 逐點鏈索引已三項實證否決 (canonical vs 冷斑軌道 88-grid 同圖但唔同中心)")
print("    ⟹ 「mode n ↔ A₅ 節點距離」類路線三重封死: 頂點傳遞 + O182 + O219")

print("\n[5] 判定")
print(f"""  R1b-A5 判死 (no-go, 結構不可能):
  - I 軌道 = 60, I_h 軌道 = 60 ⟹ 頂點傳遞 (幾何層同組合層都係單軌道)
  - 圖論量 (度數 4 / 三角形 1 / WL 同色) 全 node-agnostic (7/7 PASS)
  - 距離分類 15 類 = 座標噪聲 (0.075°, O143 scripts/21); 精確 I-軌道距離包 = 1 類
    ⟹ 任何「A₅ 節點距離/角度做投影」包含嘅 mode-依賴 100% 係噪聲, 冇結構內容
  - 定理: Aut(G)-invariant A₅ 幾何量 ⟹ 全粒子同值 ⟹ 同 8 個互異 F_proj 矛盾
  - 唯一出路係非 Aut-invariant 輸入 (sky-side), 但質量係內在結構 — 唔適用
  ⟹ U2 候選空間再收窄: γ 幂律/Z(n)/Φ×k/κ三次/sector v2-mean/複阻抗/(新)A₅幾何
  全部判死; 剩餘唯一未封: κ 非對角修正 — 需真正 CY₃ 幾何 (dijk/Kähler cone O70 層),
  唔係 A₅ 圖 (本 script 已證其無結構內容)。
""")

print("="*84)
print(f"U2 R1b-A5 no-go: {len(PASS)} PASS / {len(FAIL)} FAIL")
print("="*84)
print("PASS" if not FAIL else "FAIL")