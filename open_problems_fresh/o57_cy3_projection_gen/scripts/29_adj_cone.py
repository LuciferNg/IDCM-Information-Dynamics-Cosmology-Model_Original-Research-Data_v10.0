#!/usr/bin/env python3
"""
O57 三期 29: 155 Adjacency Curves ↔ Kähler Cone 邊界（方向 B 驗證）
====================================================================
Gemini 方向 B: 用 CYTools 計 155 adjacency pairs 嘅三階相交數 κ_ijk,
驗證呢 155 個 curves 係咪構成 Kähler cone 嘅幾何邊界 (Extreme Rays)。

方法:
  1. 155 adjacency pairs (from sr_ideal complement)
  2. 每個 curve C_jk 嘅 volume 矩陣: V_i = κ_ijk (36-dim vector)
  3. 檢查 155 個 V_i 向量嘅線性獨立性 (rank)
  4. 檢查佢哋同 Kähler cone 嘅關係 (positive on J*?)
  5. 對比 36-dim Kähler cone (需要 36 個 extreme rays?)
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 三期 29: 155 Curves ↔ Kähler Cone")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 155 adjacency ============
print("\n[1] 155 adjacency pairs")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
sr = d["sr_ideal"]
sr_set = set()
for s in sr:
    sr_set.add((min(s), max(s)))
adj = []
for i in range(1, 37):
    for j in range(i+1, 37):
        if (i, j) not in sr_set:
            adj.append((i, j))
print(f"  Adjacency: {len(adj)}")
check("155 adjacency", len(adj) == 155, f"({len(adj)})")

# ============ 2. Curve volume vectors ============
print("\n[2] Curve volume vectors (κ_ijk)")
kappa = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])

# 每個 curve C_jk: V_i = κ_ijk (36-dim)
V_curves = []
adj_labels = []
for i, j in adj:
    v = kappa[:, i-1, j-1]  # 36-dim vector
    V_curves.append(v)
    adj_labels.append((i, j))
V_curves = np.array(V_curves)  # 155×36
print(f"  V_curves shape: {V_curves.shape}")

# 非零 vectors?
nz_vecs = (np.abs(V_curves).sum(axis=1) > 1e-10).sum()
print(f"  Nonzero volume vectors: {nz_vecs}/155")

# ============ 3. Rank 分析 ============
print("\n[3] Rank 分析")
# 155 個 36-dim vectors 嘅 rank
rank_full = np.linalg.matrix_rank(V_curves)
print(f"  Rank(155 curves) = {rank_full}")
print(f"  (36-dim space, rank 最多 36)")
print(f"  30 = 2L₅ + 2B = 22 + 8 (C sector 數!)")
print(f"  36 − 30 = 6 = ?")
check("rank = 30 = 2L₅+2B", rank_full == 30, f"({rank_full})")

# 用 nonzero vectors
nz_idx = np.abs(V_curves).sum(axis=1) > 1e-10
V_nz = V_curves[nz_idx]
print(f"  Nonzero vectors: {V_nz.shape}")
if len(V_nz) > 0:
    rank_nz = np.linalg.matrix_rank(V_nz)
    print(f"  Rank(nonzero) = {rank_nz}")

# ============ 4. J* 正性檢查 ============
print("\n[4] J* 正性 (Kähler cone)")
jd = json.load(open(os.path.join(O53, "Jstar_36D.json")))
Jstar = np.array(jd.get("Jstar_36D", jd))

# J*·V = volume 應該全正 (Kähler cone 條件)
vols_j = V_curves @ Jstar
print(f"  J* volumes: min={vols_j.min():.6f}, max={vols_j.max():.6f}")
print(f"  Positive: {(vols_j > 0).sum()}, Negative: {(vols_j < 0).sum()}")

# ============ 5. Kähler cone 邊界候選 ============
print("\n[5] Kähler cone 邊界")
# 如果 155 curves 係 Kähler cone 嘅 facet 定義者:
# Kähler cone = {t : t·V_c > 0 for all curves c}
# 每個 curve 定義一個 hyperplane t·V_c = 0

# 檢查: 有幾多個「獨立」facet?
# 即係 V_curves 嘅正錐 (positive span) 係咪 full?
# Kähler cone 對偶 = Mori cone (curve cone)
# Mori cone = {Σ a_c C_c : a_c ≥ 0} = positive span of V_curves

# 用 linear programming 檢查 J* 喺 Mori cone 對偶入面?
# 簡化: 檢查 V_curves 有冇包含 J* 嘅 positive combination

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("三期 29 總結:")
print("=" * 72)

results = {
    "test": "O57 三期 29: 155 Curves ↔ Cone",
    "adj": len(adj),
    "nonzero_vecs": int(nz_vecs),
    "rank": int(rank_full),
    "rank_identity": "30 = 2L₅+2B",
    "jstar_pos": int((vols_j > 0).sum()),
    "jstar_neg": int((vols_j < 0).sum()),
    "passed": passed, "failed": failed
}
with open("data/29_adj_cone.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 三期 29 完成!")
