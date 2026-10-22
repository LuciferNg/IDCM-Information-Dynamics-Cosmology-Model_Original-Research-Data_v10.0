#!/usr/bin/env python3
"""
O70 — 28: 由 FAIL point 提取新 extreme rays
============================================
FAIL point t* (唔喺 cone(99) 入面) 有 74-109 active constraints。
真正嘅 extreme ray 係 active set 入面某 31 條 independent rows 嘅 null space。

策略: 對每個 FAIL point,
  1. Active set A (74-109 rows)
  2. 對 A 做 rank-revealing: 逐步揀 independent rows 到 31 條
  3. 用 rank-revealing QR 攞「最 independent」嘅 31 條
  4. null space → candidate extreme ray
  5. 驗證 ∈ K + extreme (≥32 active 但其中 31 條 independent)
"""
import os, sys, numpy as np
from scipy.optimize import linprog
from scipy.linalg import null_space, qr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
R = np.load(os.path.join(DATA, "15_all_rays.npy"))

def boundary_point(d):
    res = linprog(d, A_ub=-M, b_ub=np.zeros(len(M)), bounds=[(-1, 1)] * 32, method='highs')
    return res.x if res.success else None

def in_cone(v, gens):
    n = gens.shape[0]
    res = linprog(np.zeros(n), A_eq=gens.T, b_eq=v, bounds=[(0, None)] * n, method='highs')
    return res.success

rng = np.random.default_rng(42)
rays = {}
for r in R:
    rn = r / np.linalg.norm(r)
    key = tuple(np.round(rn, 6))
    rays[key] = rn
print(f"初始: {len(rays)} rays")

n_test = 300
found = 0
for i in range(n_test):
    d = rng.standard_normal(32)
    t = boundary_point(d)
    if t is None:
        continue
    if in_cone(t, R):
        continue  # 喺 cone(99) 入面 — 冇問題
    
    # FAIL point — active set
    v = M @ t
    active = np.where(np.abs(v) < 1e-6)[0]
    
    # rank-revealing QR 揀 31 條最 independent active rows
    A_rows = M[active]  # k×32
    # 用 QR with pivoting: 前 31 個 pivot 就係最 independent
    Qq, Rr, piv = qr(A_rows.T, pivoting=True)  # 32×k
    # 揀 pivot 嘅前 31 條 (對應 A_rows 嘅邊啲 row?)
    # piv 係 column permutation of A_rows.T = row selection of A_rows
    best31 = active[piv[:31]]
    M31 = M[best31]
    if np.linalg.matrix_rank(M31) < 31:
        continue
    ns = null_space(M31)
    if ns.shape[1] != 1:
        continue
    r = ns[:, 0]
    # 方向: 確保 ∈ K
    if (M @ r).min() < -1e-8:
        r = -r
        if (M @ r).min() < -1e-8:
            continue
    rn = r / np.linalg.norm(r)
    # sign convention
    for x in rn:
        if abs(x) > 1e-10:
            if x < 0:
                rn = -rn
            break
    key = tuple(np.round(rn, 6))
    if key not in rays:
        rays[key] = rn
        found += 1
        print(f"  新 ray #{found}: active={len(active)}")

print(f"\nWalk 完: {len(rays)} rays, 新增 {found}")
if found:
    R_all = np.array(list(rays.values()))
    np.save(os.path.join(DATA, "28_extended_rays.npy"), R_all)
    print(f"Saved → data/28_extended_rays.npy ({R_all.shape})")
    
    # 再驗證 K ⊆ C
    print(f"\n─── 再驗證 K ⊆ C ───")
    fails2 = 0
    for i2 in range(500):
        d2 = rng.standard_normal(32)
        t2 = boundary_point(d2)
        if t2 is None:
            continue
        if not in_cone(t2, R_all):
            fails2 += 1
    print(f"FAIL: {fails2}/500")
    print(f"{'✅ complete!' if fails2 == 0 else '⚠️ 仲有漏'}")
else:
    print("冇搵到新 rays — 需要其他方法")
