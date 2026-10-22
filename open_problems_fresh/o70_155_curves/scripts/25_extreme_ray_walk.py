#!/usr/bin/env python3
"""
O70 — 25: Extreme Ray Walk — 由 random boundary 行到真正 extreme ray
==================================================================
發現: 99 rays 唔 complete (4/300 random boundary points ∉ cone(99)).

演算法 (Active-set walk):
1. 對 random direction d, LP 解 boundary point t* (min d·t s.t. Mt≥0, -1≤t≤1)
2. t* 嘅 active set A = {i : M_i·t* = 0} (≥32 條)
3. Extreme ray 必然 active ≥32 條獨立不等式
4. 用 active set 嘅 null space 搵 extreme direction:
   - active rows A (k×32, k≥32), 搵 rank-31 submatrix 嘅 null vector
   - 即係: 揀 31 條 active rows, null space 1D → 候選 extreme ray
5. 驗證候選 ray ∈ K (M·r ≥ 0) + extreme (31 active constraints)
"""
import os, sys, numpy as np
from scipy.optimize import linprog
from scipy.linalg import null_space

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

print("=" * 72)
print("O70 25: Extreme Ray Walk — 補齊 Kähler cone extreme rays")
print("=" * 72)

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
R_old = np.load(os.path.join(DATA, "15_all_rays.npy"))
print(f"Mori rays: {M.shape}, 舊 rays: {R_old.shape}")

# Normalize M rows? 不等式 M·t ≥ 0, scale 唔影響
# Mn = M / norm? 用嚟做 active 判定
tol = 1e-7

def boundary_point(d):
    """min d·t s.t. M·t ≥ 0, -1≤t≤1"""
    res = linprog(d, A_ub=-M, b_ub=np.zeros(len(M)), bounds=[(-1, 1)] * 32, method='highs')
    if not res.success:
        return None
    return res.x

def active_set(t):
    v = M @ t
    return np.where(np.abs(v) < 1e-6)[0]

def in_cone(v, gens, tol=1e-7):
    n = gens.shape[0]
    res = linprog(np.zeros(n), A_eq=gens.T, b_eq=v, bounds=[(0, None)] * n, method='highs')
    return res.success and np.allclose(gens.T @ res.x, v, atol=tol)

# 候選 rays 集合 (normalized)
rays_set = {}
def add_ray(r):
    rn = np.linalg.norm(r)
    if rn < 1e-12:
        return
    r = r / rn
    # 檢查 sign: cone ray 方向, normalize 令第一個非零 entry 係正
    for x in r:
        if abs(x) > 1e-10:
            if x < 0:
                r = -r
            break
    key = tuple(np.round(r, 6))
    rays_set[key] = r

for r in R_old:
    add_ray(r)
print(f"初始 rays: {len(rays_set)}")

# Walk: 用 active set 嘅 31-subset null space 產生 extreme candidates
rng = np.random.default_rng(7)
found_new = 0
n_trials = 2000
for trial in range(n_trials):
    d = rng.standard_normal(32)
    t = boundary_point(d)
    if t is None:
        continue
    A = active_set(t)
    if len(A) < 32:
        continue
    # 揀 31 條 active rows, 解 null space (應 1D)
    # 用 rank-revealing: 揀最 independent 嘅 31 條
    # 先試隨機 31-subset 幾次
    for _ in range(20):
        idx31 = rng.choice(A, 31, replace=False)
        M31 = M[idx31]
        if np.linalg.matrix_rank(M31) < 31:
            continue
        ns = null_space(M31)  # 32×1
        if ns.shape[1] != 1:
            continue
        r = ns[:, 0]
        # 驗證 r ∈ K
        if (M @ r).min() < -tol:
            r = -r
            if (M @ r).min() < -tol:
                continue
        # normalize + sign
        add_ray(r)
        break

print(f"Walk 後 rays: {len(rays_set)} (新增 {len(rays_set) - 99})")

# 驗證新增
R_all = np.array(list(rays_set.values()))
print(f"\n─── 驗證新集合 ───")
print(f"rays: {R_all.shape}")
# C ⊆ K
viol = M @ R_all.T
print(f"M·R 最小值: {viol.min():.2e}, 違反: {(viol < -1e-8).sum()}")
# 全部 extreme? (冇一條可以由其他生成)
def is_extreme(i):
    others = np.delete(R_all, i, axis=0)
    return not in_cone(R_all[i], others)

not_ext = [i for i in range(len(R_all)) if not is_extreme(i)]
print(f"non-extreme: {len(not_ext)}")
if not_ext:
    print(f"  移除 non-extreme...")
    mask = np.ones(len(R_all), dtype=bool)
    mask[not_ext] = False
    R_all = R_all[mask]
    print(f"  → {len(R_all)} extreme rays")

# K ⊆ C 再驗證
print(f"\n─── 再驗證 K ⊆ C (300 random) ───")
fails = 0
for i in range(300):
    d = rng.standard_normal(32)
    t = boundary_point(d)
    if t is None:
        continue
    if not in_cone(t, R_all):
        fails += 1
print(f"FAIL: {fails}/300")

# Save
np.save(os.path.join(DATA, "25_all_extreme_rays.npy"), R_all)
print(f"\nSaved {len(R_all)} rays → data/25_all_extreme_rays.npy")
print("Done.")
