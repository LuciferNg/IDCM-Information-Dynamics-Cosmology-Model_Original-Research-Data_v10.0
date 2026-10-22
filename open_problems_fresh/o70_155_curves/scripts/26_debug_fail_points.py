#!/usr/bin/env python3
"""
O70 — 26: Debug FAIL points — 睇 active set 結構
================================================
搵出 4/300 fail 嘅 boundary point 嘅 active set,
理解 99 rays 缺咗乜。
"""
import os, sys, numpy as np
from scipy.optimize import linprog
from scipy.linalg import null_space

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
R = np.load(os.path.join(DATA, "15_all_rays.npy"))
tol = 1e-7

def boundary_point(d):
    res = linprog(d, A_ub=-M, b_ub=np.zeros(len(M)), bounds=[(-1, 1)] * 32, method='highs')
    if not res.success:
        return None
    return res.x

def in_cone(v, gens, tol=1e-7):
    n = gens.shape[0]
    res = linprog(np.zeros(n), A_eq=gens.T, b_eq=v, bounds=[(0, None)] * n, method='highs')
    return res.success and np.allclose(gens.T @ res.x, v, atol=tol)

rng = np.random.default_rng(42)
n_test = 300
fails = 0
for i in range(n_test):
    d = rng.standard_normal(32)
    t = boundary_point(d)
    if t is None:
        continue
    if not in_cone(t, R):
        fails += 1
        v = M @ t
        active = np.where(np.abs(v) < 1e-6)[0]
        inactive = np.where(np.abs(v) >= 1e-6)[0]
        print(f"\n--- FAIL point #{i} ---")
        print(f"  active constraints: {len(active)}")
        # active 嘅 99-rays 對應?
        # 每條 99-ray 對應邊啲 active constraints?
        Mr = M @ R.T  # 185×99
        ray_active = (np.abs(Mr) < 1e-6)
        # fail point 嘅 active set 有冇邊條係所有 99 rays 都冇嘅?
        # 對每條 active constraint, 睇 99 rays 有幾多條都 active 喺嗰條
        print(f"  active constraint → 99 rays 中 active 數:")
        for a in active:
            cnt = ray_active[a].sum()
            if cnt == 0:
                print(f"    constraint {a}: NO ray active (新 facet combo!)")
        # 有冇 active constraint 係 99 rays 完全冇碰嘅?
        total_ray_active = ray_active.sum(axis=1)  # 每條 constraint 有幾多 ray active
        orphan = [a for a in active if total_ray_active[a] == 0]
        print(f"  orphan constraints (99 rays 從未 active): {len(orphan)}")
        if len(orphan) > 3:
            print(f"  前幾個: {orphan[:10]}")
        if fails >= 3:
            break

print(f"\nTotal fails shown: {min(fails, 3)}")
