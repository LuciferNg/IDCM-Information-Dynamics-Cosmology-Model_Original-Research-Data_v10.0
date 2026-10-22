#!/usr/bin/env python3
"""
O70 — 30: Final Verification — 203 Extreme Rays
================================================
驗證:
  1. 203 rays 全部 ∈ K (M·r ≥ 0)
  2. 全部 extreme (minimal)
  3. K ⊆ cone(203) — 1000 random tests
  4. Rank = 32 (full-dim)
  5. 結構分析: 203 = ? (同 155/185/73/99 關係)
"""
import os, sys, numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
R = np.load(os.path.join(DATA, "29_complete_extreme_rays.npy"))
print("=" * 72)
print("O70 30: Final Verification — 203 Extreme Rays")
print("=" * 72)
print(f"Mori rays (facets): {M.shape}")
print(f"Extreme rays: {R.shape}")

checks = []
def check(name, cond, detail=""):
    checks.append(bool(cond))
    print(f"  [{'✅' if cond else '❌'}] {name} {detail}")

# 1. C ⊆ K
viol = M @ R.T
check("全部 rays ∈ Kähler cone", viol.min() > -1e-7, f"(min {viol.min():.2e})")

# 2. Extreme (minimal)
def in_cone(v, gens):
    n = gens.shape[0]
    res = linprog(np.zeros(n), A_eq=gens.T, b_eq=v, bounds=[(0, None)] * n, method='highs')
    return res.success

not_ext = []
for i in range(len(R)):
    others = np.delete(R, i, axis=0)
    if in_cone(R[i], others):
        not_ext.append(i)
check("全部 rays extreme (minimal)", len(not_ext) == 0, f"({len(not_ext)} non-extreme)")

# 3. K ⊆ C — 1000 random
rng = np.random.default_rng(123)
def boundary_point(d):
    res = linprog(d, A_ub=-M, b_ub=np.zeros(len(M)), bounds=[(-1, 1)] * 32, method='highs')
    return res.x if res.success else None

fails = 0
for i in range(1000):
    d = rng.standard_normal(32)
    t = boundary_point(d)
    if t is None:
        continue
    if not in_cone(t, R):
        fails += 1
check("K ⊆ cone(203) — 1000 random", fails == 0, f"({fails} fail)")

# 4. Rank
check("Rank = 32 (full-dim)", np.linalg.matrix_rank(R) == 32, f"(rank {np.linalg.matrix_rank(R)})")

# 5. Active constraints per ray
act = (np.abs(M @ R.T) < 1e-6).sum(axis=0)
check("每條 ray ≥32 active", act.min() >= 32, f"(min {act.min()}, median {np.median(act):.0f})")

# 6. 結構分析
print("\n─── 結構分析 ───")
n = len(R)
print(f"203 = 185 + 18")
print(f"203 − 99 = 104 (舊 session 漏咗 104 條!)")
print(f"203 vs: 185 (Mori rays), 155 (adjacency), 73 (Nd+L7), 99 (舊)")
# 分解嘗試
import itertools
for expr, val in [
    ("2×99+5", 2*99+5),
    ("185+18", 185+18),
    ("155+48", 155+48),
    ("3×73−16", 3*73-16),
    ("2×90+23", 2*90+23),
    ("178+25", 178+25),  # 178 = 2F11 total chain
    ("2F11+25", 2*89+25),
    ("4×44+27", 4*44+27),
    ("N_gen²×?", None),
]:
    if val is not None:
        print(f"  {expr} = {val} {'← 203!' if val == n else ''}")

# 7. 99 vs 203 對比
R99 = np.load(os.path.join(DATA, "15_all_rays.npy"))
from scipy.spatial.distance import cdist
D = cdist(R, R99, metric='cosine')
in99 = (D.min(axis=1) < 1e-4).sum()
print(f"\n203 入面有 {in99} 條喺舊 99, 新增 {n - in99} 條")

print("\n" + "=" * 72)
print(f"RESULT: {sum(checks)}/{len(checks)} PASS")
print("=" * 72)
