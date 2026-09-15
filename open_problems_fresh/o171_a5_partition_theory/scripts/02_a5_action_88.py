#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/02 — A₅ 60-頂點群作用於 120 邊 / 88 中點: orbit + irrep 分解
=========================================================================
問題 (O171 核心): 「60-頂點群 ↔ 88-site Laplacian 譜子空間投射」點樣生成 420/421, 55/56?

呢個 script 做**真幾何群作用計算** (唔砌 identity):
  1. 由 O182 資料 (a5_nodes 60 點, 28° 閾值) 重建 A₅ 網絡: 120 邊, 度 4
  2. 求 60 點集嘅全對稱群 (orthogonal maps preserving the set)
  3. 驗 A₅ 類結構 (1,15,20,12,12) 同 χ_60 = 60δ_{g,e} (自由作用)
     ⇒ 60 點置換模 = **正則表示** ⇒ 60 = Σdim² 係結構必然
  4. 120 邊置換模: χ_120 → irrep 分解 (期望 2×正則表示)
  5. ★ 88 透明邊中點: 檢查 A₅ 係咪作用於 88 點集 → **負結果** (只有 2 個元素保持)
  6. 穩定子子群嘅軌道結構 (誠實記錄 88-site 同 A₅ 嘅真實關係)

容差: a5_nodes.txt 只有 4 位小數 + O1 群論閉合嘅 ~0.08° 軌道擾動
      → Gram 匹配 1e-5, 點匹配 5e-3 rad (0.29°, 遠細於 26°/16° 鄰距)
"""
import numpy as np
from pathlib import Path
from itertools import combinations

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"
GRAM_TOL = 1e-5
PT_TOL = 5e-3

ok = 0; tot = 0
def chk(name, cond, note=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
    return cond

print("="*78)
print("O171 scripts/02 — A₅ 群作用於 60 節點 / 120 邊 / 88 中點")
print("="*78)

# ---------- 1. 資料 + 網絡 ----------
nodes = np.loadtxt(DATA / "a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
V = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
col = {}
for line in (DATA / "anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split(); col[int(p[0])] = int(p[3])
color = np.array([col[i] for i in range(60)])
G_gram = V @ V.T
dist = np.arccos(np.clip(G_gram, -1, 1))
edges = [(i,j) for i in range(60) for j in range(i+1,60) if dist[i,j] < np.radians(28.0)]
transp = [(i,j) for (i,j) in edges if color[i] != color[j]]
frust  = [(i,j) for (i,j) in edges if color[i] == color[j]]
print(f"\n網絡: {len(edges)} 邊 (透明 {len(transp)} / 阻挫 {len(frust)}), 著色 {int(color.sum())}/{60-int(color.sum())}")
chk("C1 120 邊, 透明 88 / 阻挫 32", len(edges)==120 and len(transp)==88 and len(frust)==32)

# ---------- 2. 全對稱群 ----------
print("\n=== C2: 60 點集嘅對稱群 ===")
ref = [0,1,2]
Gr = np.array([[G_gram[a,b] for b in ref] for a in ref])
cand = []
for a,b,c in combinations(range(60), 3):
    for p in [(a,b,c),(a,c,b),(b,a,c),(b,c,a),(c,a,b),(c,b,a)]:
        if (abs(G_gram[p[0],p[1]]-Gr[0,1])<GRAM_TOL and abs(G_gram[p[0],p[2]]-Gr[0,2])<GRAM_TOL
            and abs(G_gram[p[1],p[2]]-Gr[1,2])<GRAM_TOL):
            cand.append(p)
A_ref_inv = np.linalg.inv(V[ref].T)
group = []; seen_keys = set()
for p in cand:
    M = V[list(p)].T @ A_ref_inv
    if not np.allclose(M @ M.T, np.eye(3), atol=1e-3): continue
    W = V @ M.T
    D = np.arccos(np.clip(W @ V.T, -1, 1))
    perm = np.argmin(D, axis=1)
    if D[np.arange(60), perm].max() > PT_TOL or len(set(perm.tolist())) != 60: continue
    key = tuple(np.round(M.ravel(), 5))
    if key in seen_keys: continue
    seen_keys.add(key); group.append((M, perm, float(np.linalg.det(M))))
print(f"  Gram 候選 = {len(cand)};  對稱群階 |Sym(60 nodes)| = {len(group)}")
rots = [(M,p,d) for (M,p,d) in group if d > 0.5]
chk("C2 對稱群階 = 60 = |A₅| (只有旋轉, 冇非正常對稱)", len(group) == 60)
chk("C2b 全部 det = +1 (A₅ 旋轉群, 冇反演)", len(rots) == 60)

# ---------- 3. A₅ 類結構 + 正則表示 ----------
print("\n=== C3: A₅ 類結構 (由 trace 分類) ===")
phi = (1+np.sqrt(5))/2; psi = (1-np.sqrt(5))/2
TRACES = [3.0, -1.0, 0.0, float(phi), float(psi)]      # 1A,2A,3A,5A,5B
def cls(M):
    t = float(np.trace(M))
    ds = [abs(t-v) for v in TRACES]
    c = int(np.argmin(ds))
    return c if ds[c] < 1e-3 else -1                      # 近似矩陣 → 1e-3 容差
class_of = [cls(M) for (M,p,d) in rots]
cls_sizes = [class_of.count(c) for c in range(5)]
print(f"  類大小 (1A,2A,3A,5A,5B) = {cls_sizes}  (Σ = {sum(cls_sizes)})")
chk("C3 A₅ 類結構 = [1,15,20,12,12]", cls_sizes == [1,15,20,12,12])
chi60 = [0]*5
for (M,p,d), c in zip(rots, class_of):
    chi60[c] += int((p == np.arange(60)).sum())
chi60 = [chi60[c]/cls_sizes[c] for c in range(5)]
print(f"  χ_60 (每類平均不動點) = {[round(x,6) for x in chi60]}")
chk("C3b χ_60 = (60,0,0,0,0) ⇒ 60 點作用自由", all(abs(chi60[c] - (60 if c==0 else 0)) < 1e-9 for c in range(5)))
print("  ⇒ 60 點置換模 ≅ 正則表示 ⊕ dim_i·ρ_i ⇒ 60 = Σ dim_i²  ★結構必然")

CHI = {1: [1,1,1,1,1], 3: [3,-1,0,phi,psi], 3.1: [3,-1,0,psi,phi],
       4: [4,0,1,-1,-1], 5: [5,1,-1,0,0]}
def mult(chi_by_class, dim, chi):
    return sum(cls_sizes[c]*chi_by_class[c]*chi[c] for c in range(5))/60.0
print("\n  正則表示分解 (期望 m_i = dim_i):")
reg_ok = True
for key, chi in CHI.items():
    m = mult(chi60, key, chi)
    print(f"    irrep dim {key}: m = {m:.6f}")
    reg_ok &= abs(m - (1 if key==1 else key)) < 1e-9 if key != 3.1 else abs(m-3) < 1e-9
chk("C3c m_i = dim_i ∀i (正則表示)", reg_ok)

# ---------- 4. 120 邊置換模 ----------
print("\n=== C4: 120 邊置換模 ===")
chi120 = [0]*5
for (M, perm60, d), c in zip(rots, class_of):
    nfix = sum(1 for (i,j) in edges if tuple(sorted((int(perm60[i]), int(perm60[j])))) == (i,j))
    chi120[c] += nfix
chi120 = [chi120[c]/cls_sizes[c] for c in range(5)]
print(f"  χ_120 (每類平均不動邊) = {[round(x,6) for x in chi120]}")
chk("C4 χ_120 = (120,0,0,0,0) ⇒ 120 邊作用自由", all(abs(chi120[c] - (120 if c==0 else 0)) < 1e-9 for c in range(5)))
tot_dim = 0
print("  irrep 分解 (期望 2×正則表示 ⇒ m = 2·dim_i):")
for key, chi in CHI.items():
    m = mult(chi120, key, chi)
    tot_dim += m * (1 if key==1 else (3 if key in (3,3.1) else key))
    print(f"    irrep dim {key}: m = {m:.6f}")
chk("C4b Σ m_i·dim_i = 120", abs(tot_dim-120) < 1e-6, f"(= {tot_dim:.6f})")
chk("C4c m_i = 2·dim_i (2×正則表示)", all(abs(mult(chi120, k, c) - 2*(1 if k==1 else (3 if k in (3,3.1) else k))) < 1e-9 for k,c in CHI.items()))

# ---------- 5. ★ 88 中點: A₅ 唔作用 (負結果) ----------
print("\n=== C5: ★ 88 透明邊中點 — A₅ 係咪作用? ===")
mid = np.array([V[i]+V[j] for (i,j) in transp]); mid /= np.linalg.norm(mid, axis=1, keepdims=True)
def perm_of(M, pts, target):
    W = pts @ M.T
    D = np.arccos(np.clip(W @ target.T, -1, 1))
    idx = np.argmin(D, axis=1)
    if D[np.arange(len(pts)), idx].max() > PT_TOL or len(set(idx.tolist())) != len(pts): return None
    return idx
keep = []
for (M, perm60, d) in rots:
    p = perm_of(M, mid, mid)
    if p is not None: keep.append((M, p, d))
print(f"  保持 88 點集嘅 A₅ 元素: {len(keep)}/60")
chk("C5 ★ A₅ **唔**作用於 88 點集 (只有 ≤2 元素)", len(keep) <= 2, f"(實算 {len(keep)})")
chk("C5b 恆等 + 1 個元素 (穩定子階 2)", len(keep) == 2)
sub = keep
# A₅ 元素階由 trace 精確決定: 3→1, −1→2, 0→3, φ/ψ→5
def order_from_trace(M):
    return {0:1, 1:2, 2:3, 3:5, 4:5}[cls(M)]
ords = [order_from_trace(M) for (M,_,_) in sub]
print(f"  穩定子元素階 = {ords}  (tr = {[round(float(np.trace(M)),6) for M,_,_ in sub]})")
# 軌道閉包 (正確做法)
perm_map = {i: sub[i][1] for i in range(len(sub))}
seen = np.zeros(88, dtype=bool); orbits = []
for i in range(88):
    if seen[i]: continue
    orb = {i}; frontier = [i]
    while frontier:
        x = frontier.pop()
        for j in range(len(sub)):
            y = int(sub[j][1][x])
            if y not in orb: orb.add(y); frontier.append(y)
    for y in orb: seen[y] = True
    orbits.append(sorted(orb))
from collections import Counter
print(f"  88 點 orbit 分解 (穩定子階 {len(sub)}): {len(orbits)} 條, 大小分佈 {dict(Counter(len(o) for o in orbits))}")
chk("C5c orbit 大小整除穩定子階", all(len(sub) % len(o) == 0 or len(o) == 1 for o in orbits))

# ---------- 6. 結論 ----------
print("\n=== C6: 結構結論 ===")
print("  ✓ A₅ 自由作用於 60 頂點 (正則表示) ⇒ 真空方向唯一 (m_triv = 1)")
print("  ✓ A₅ 自由作用於 120 邊 (2×正則表示) ⇒ 每份真空方向唯一")
print("  ✗ A₅ **唔**作用於 88 透明邊中點 (穩定子階 2) — 著色唔係 A₅ 不變")
print("  ⇒ 「60-頂點群 ↔ 88-site」**唔係**群作用關係; 真實聯繫係:")
print("     (i) 計數恆等式: 88 = 120 − 32 = 2(|A₅| − B²) = 2N_d")
print("     (ii) 譜恆等式: 45 = N_d+1 (相異能階) / 44 = #{γ ≤ μ²}")
print("     (iii) 群階: 420 = L₄|A₅|, 421 = L₄|A₅|+1 (A₅ 進入 sector 計數, 唔係作用)")

print()
print(f"RESULT: {ok}/{tot} PASS")
